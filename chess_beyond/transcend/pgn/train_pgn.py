"""Train the character-level PGN transformer with the "Transcendence" recipe.

    python transcend/pgn/train_pgn.py --data data/transcend/pgn-all --out runs/transcend/pgn-all.pt

Recipe from the paper (ChessFormer): AdamW, lr 3e-4, 2000 warmup steps then cosine
decay, weight decay 0.1, ~125K tokens per optimizer step, 100K steps; model 16
layers, d=512, 8 heads (pgn_model.py). The paper's context length isn't stated;
1024 characters covers almost every game.

Each training row is --ctx + 1 characters starting at a game's first ';' (so the
model always reads a game from its first move); rows that run past a game's end
continue into the next one. Loss is next-character cross-entropy on every
position. The first --val-games games (make_pgn_data.py) are held out.

Every --eval-every steps: held-out loss, and the checkpoint if it is the best so
far; <out>_log.jsonl gets a line per eval. Playing strength comes from
play_elo.py, which plays this model against Maia-2 at any --temperature.

Also at every eval (and before training), when the probe set exists
(pgn_probe.py build), an activation snapshot into <out>_pgn_probe/: the last
layer's state just before the model moves, for ~10,000 held-out game positions,
as density heatmaps on singular vectors 1-3 with 10 labelled positions marked.

Early stopping: training ends when the held-out loss hasn't improved for --patience
evals in a row, counted only after --min-epochs passes over the data (1 by default);
the checkpoint is always the best one. When the run ends (early stop or --steps),
the resume state is deleted, leaving the checkpoint, the logs and the probe folder.

Resuming: every eval also writes <out>_state.pt (model, optimizer, step, best
loss, random state). --resume continues from it, so a run longer than one
cloud container's time limit can go on in the next one.
"""
import argparse
import json
import math
import os
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # chess_beyond/
import paths  # noqa: E402  also puts transcend/'s folders on sys.path
from pgn_model import PGNTransformer, save_pgn_model
from pgn_probe import DEFAULT as PROBE_DEFAULT, snapshot

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--data", required=True, help="make_pgn_data.py output folder")
ap.add_argument("--out", required=True)
ap.add_argument("--d", type=int, default=512)
ap.add_argument("--layers", type=int, default=16)
ap.add_argument("--heads", type=int, default=8)
ap.add_argument("--ctx", type=int, default=1024)
ap.add_argument("--batch-tokens", type=int, default=125_000, help="tokens per optimizer step (paper: 125K)")
ap.add_argument("--micro", type=int, default=16, help="rows per forward pass (memory)")
ap.add_argument("--lr", type=float, default=3e-4)
ap.add_argument("--min-lr", type=float, default=3e-5, help="cosine floor")
ap.add_argument("--weight-decay", type=float, default=0.1)
ap.add_argument("--warmup", type=int, default=2000)
ap.add_argument("--steps", type=int, default=100_000, help="length of the cosine schedule (paper: 100K)")
ap.add_argument("--stop-step", type=int, default=0, help="end here without changing the schedule (0 = --steps)")
ap.add_argument("--eval-every", type=int, default=1000)
ap.add_argument("--probe-every", type=int, default=0, help="activation snapshot every N steps (0 = every eval)")
ap.add_argument("--log-every", type=int, default=50)
ap.add_argument("--compile", action="store_true", help="torch.compile the model")
ap.add_argument("--compile-mode", default="default",
                choices=["default", "max-autotune-no-cudagraphs", "max-autotune"],
                help="torch.compile mode: max-autotune tries more GPU kernels (slower to compile) and, "
                     "without -no-cudagraphs, also uses CUDA graphs. Same maths in every mode.")
ap.add_argument("--gpu-mem-frac", type=float, default=0.92)
ap.add_argument("--probe", default=str(PROBE_DEFAULT),
                help="pgn_probe.py build folder for activation snapshots at every eval; '' turns them off")
ap.add_argument("--resume", action="store_true", help="continue from <out>_state.pt if it exists")
ap.add_argument("--overwrite", action="store_true", help="start over even if <out> holds a finished run")
ap.add_argument("--init", default="", help="start from this checkpoint's weights (fresh optimizer and schedule)")
ap.add_argument("--patience", type=int, default=8,
                help="stop after this many evals without a better held-out loss (counted after --min-epochs; 0 = never)")
ap.add_argument("--min-epochs", type=float, default=1.0,
                help="early stopping can only count once this many passes over the training data are done")
ap.add_argument("--min-delta", type=float, default=0.0, help="improvement that counts as better")
ap.add_argument("--device", default="cuda", help="cuda for real runs; cpu for a quick local smell test")
ap.add_argument("--seed", type=int, default=0)
args = ap.parse_args()
if args.probe and not os.path.exists(os.path.join(args.probe, "population.jsonl")):
    sys.exit(f"no probe set at {args.probe}, so this run would make no plots: build it first "
             f"(pgn_probe.py build, or modal_train.py::prepare), or pass --probe '' to train without them")

torch.manual_seed(args.seed)
dev = args.device
cuda = dev == "cuda"
if cuda:
    torch.cuda.set_per_process_memory_fraction(args.gpu_mem_frac)
    torch.backends.cuda.matmul.allow_tf32 = True


def autocast():
    """bf16 on the GPU; plain float32 elsewhere."""
    return torch.autocast("cuda", dtype=torch.bfloat16) if cuda else torch.autocast("cpu", enabled=False)


def empty_cache():
    if cuda:
        torch.cuda.empty_cache()

data = Path(args.data)
meta = json.loads((data / "meta.json").read_text())
tokens = torch.from_numpy(np.fromfile(data / "tokens.bin", dtype=np.uint8)).to(dev)   # ~1 byte per character
starts = torch.from_numpy(np.load(data / "starts.npy")).to(dev)
nv = meta["val_games"]
val_end = int(starts[nv])
train_starts = starts[nv:]
train_starts = train_starts[train_starts < len(tokens) - args.ctx - 1]
val_starts = starts[:nv]
val_starts = val_starts[val_starts < val_end - args.ctx - 1]
offs = torch.arange(args.ctx + 1, device=dev)
accum = max(1, math.ceil(args.batch_tokens / (args.micro * args.ctx)))
print(f"{meta['games']} games, {len(tokens) / 1e6:.0f}M characters; {len(train_starts)} train starts, "
      f"{nv} games held out\n{accum} x {args.micro} rows x {args.ctx} = "
      f"{accum * args.micro * args.ctx / 1e3:.0f}K tokens per step, {args.steps} steps "
      f"(~{args.steps * accum * args.micro * args.ctx / len(tokens):.1f} passes over the data)", flush=True)

model = PGNTransformer(args.d, args.layers, args.heads, args.ctx).to(dev)
print(f"model: {sum(p.numel() for p in model.parameters()) / 1e6:.1f}M params", flush=True)
fwd = torch.compile(model, mode=args.compile_mode) if args.compile else model
decay = [p for n, p in model.named_parameters() if p.dim() >= 2]
no_decay = [p for n, p in model.named_parameters() if p.dim() < 2]
opt = torch.optim.AdamW([dict(params=decay, weight_decay=args.weight_decay), dict(params=no_decay, weight_decay=0.0)],
                        lr=args.lr, betas=(0.9, 0.95), fused=cuda)


def lr_at(step):
    if step < args.warmup:
        return args.lr * (step + 1) / args.warmup
    t = min((step - args.warmup) / max(args.steps - args.warmup, 1), 1.0)
    return args.min_lr + (args.lr - args.min_lr) * 0.5 * (1 + math.cos(math.pi * t))


def batch(pool, n, gen=None):
    s = pool[torch.randint(0, len(pool), (n,), device=dev, generator=gen)]
    w = tokens[s[:, None] + offs].long()
    return w[:, :-1], w[:, 1:]


@torch.no_grad()
def validate(rows=512):
    model.eval()
    g = torch.Generator(device=dev).manual_seed(1234)          # the same held-out rows every time
    total = 0.0
    for _ in range(rows // args.micro):
        x, y = batch(val_starts, args.micro, g)
        with autocast():
            logits = model(x)
        total += F.cross_entropy(logits.float().reshape(-1, logits.size(-1)), y.reshape(-1)).item()
    model.train()
    empty_cache()
    return total / (rows // args.micro)


os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
stem = os.path.splitext(args.out)[0]
log_path, state_path, probe_dir = stem + "_log.jsonl", stem + "_state.pt", stem + "_pgn_probe"
best, since, first = float("inf"), 0, 1
if os.path.exists(args.out) and not os.path.exists(state_path) and not args.overwrite:
    # a finished run leaves its checkpoint but no resume state: starting again would overwrite it
    sys.exit(f"{args.out} is a finished run's checkpoint and there is no resume state; "
             f"use another --out, or --overwrite to start over")
if args.resume and os.path.exists(state_path):
    st = torch.load(state_path, map_location=dev, weights_only=False)
    model.load_state_dict(st["model"])
    opt.load_state_dict(st["opt"])
    torch.set_rng_state(st["rng_cpu"].cpu())
    if cuda:
        torch.cuda.set_rng_state(st["rng_cuda"].cpu())
    best, since, first = st["best"], st.get("since", 0), st["step"] + 1
    print(f"resumed from {state_path} at step {st['step']} (best held-out loss {best:.4f}, "
          f"{since} evals without improvement)", flush=True)
else:
    if args.init:                    # weights only: the optimizer, warmup and schedule start fresh
        src = torch.load(args.init, map_location=dev, weights_only=False)
        model.load_state_dict(src["state"])
        print(f"started from the weights in {args.init} (its step {src['extra'].get('step')}, "
              f"held-out loss {src['extra'].get('val_loss', float('nan')):.4f})", flush=True)
    if args.probe:
        snapshot(model, 0, probe_dir, args.probe, title=Path(args.out).stem)    # the starting network
        empty_cache()


def save_state(step):
    tmp = state_path + ".tmp"
    torch.save(dict(model=model.state_dict(), opt=opt.state_dict(), step=step, best=best, since=since,
                    rng_cpu=torch.get_rng_state(), rng_cuda=torch.cuda.get_rng_state() if cuda else None, args=vars(args)), tmp)
    os.replace(tmp, state_path)                  # never leave a half-written state behind


tokens_per_step = accum * args.micro * args.ctx
min_steps = max(args.warmup, math.ceil(args.min_epochs * len(tokens) / tokens_per_step))
print(f"one epoch = {len(tokens) / tokens_per_step:,.0f} steps; early stopping counts from step {min_steps:,}"
      f" (patience {args.patience} evals)", flush=True)
finished = False
t0, last = time.time(), time.time()
model.train()
for step in range(first, args.steps + 1):
    for g in opt.param_groups:
        g["lr"] = lr_at(step)
    total = torch.zeros((), device=dev)          # stays on the GPU: no sync until it is printed
    for _ in range(accum):
        x, y = batch(train_starts, args.micro)
        if args.compile and args.compile_mode == "max-autotune":
            torch.compiler.cudagraph_mark_step_begin()    # each pass gets its own graph outputs
        with autocast():
            logits = fwd(x)
        loss = F.cross_entropy(logits.float().reshape(-1, logits.size(-1)), y.reshape(-1)) / accum
        loss.backward()
        total += loss.detach()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    opt.step()
    opt.zero_grad(set_to_none=True)
    if step % args.log_every == 0:
        now = time.time()
        rate = args.log_every / (now - last)
        last = now
        print(f"  step {step}  train loss {total.item():.4f}  lr {lr_at(step):.2e}  {rate:.2f} steps/s  "
              f"~{(args.steps - step) / max(rate, 1e-9) / 3600:.1f} h left", flush=True)
    if step % args.eval_every == 0 or step == args.stop_step:
        vl = validate()
        mark = ""
        if vl < best - args.min_delta:
            best, since, mark = vl, 0, "  * saved"
            save_pgn_model(model, args.out, extra=dict(step=step, val_loss=vl, args=vars(args)))
        elif step >= min_steps:
            since += 1
            mark = f"  ({since}/{args.patience} without improvement)" if args.patience else ""
        print(f"step {step}  held-out loss {vl:.4f} ({vl / math.log(2):.3f} bits/char)  lr {lr_at(step):.2e}  "
              f"{(time.time() - t0) / 3600:.1f} h{mark}", flush=True)
        with open(log_path, "a", encoding="utf-8") as lf:
            lf.write(json.dumps(dict(step=step, val_loss=vl, train_loss=total.item(), lr=lr_at(step), best=best,
                                     since=since)) + "\n")
        if args.probe and (not args.probe_every or step % args.probe_every == 0):
            snapshot(model, step, probe_dir, args.probe, title=Path(args.out).stem)
            empty_cache()
        save_state(step)
        last = time.time()
        if args.patience and since >= args.patience:
            print(f"held-out loss hasn't improved for {since} evals; stopping (best {best:.4f})", flush=True)
            finished = True
            break
    if args.stop_step and step >= args.stop_step:
        print(f"reached --stop-step {args.stop_step}; stopping")
        break
else:
    finished = not args.stop_step or args.stop_step >= args.steps
if finished and os.path.exists(args.out):
    shutil.copyfile(args.out, stem + "-final.pt")    # a second copy no relaunch writes to
    print(f"run finished; best checkpoint also copied to {stem}-final.pt", flush=True)
if finished and os.path.exists(state_path):
    os.remove(state_path)            # the run is over: the resume state (~600 MB) is no longer needed
    print(f"run finished; removed {state_path}", flush=True)
print(f"best held-out loss {best:.4f}; checkpoint {args.out}")
