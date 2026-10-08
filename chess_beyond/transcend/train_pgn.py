"""Train the character-level PGN transformer with the "Transcendence" recipe.

    python transcend/train_pgn.py --data data/transcend/pgn-all --out runs/transcend/pgn-all.pt

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
"""
import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # chess_beyond/
from pgn_model import PGNTransformer, save_pgn_model

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
ap.add_argument("--log-every", type=int, default=50)
ap.add_argument("--compile", action="store_true", help="torch.compile the model")
ap.add_argument("--gpu-mem-frac", type=float, default=0.92)
ap.add_argument("--seed", type=int, default=0)
args = ap.parse_args()

torch.manual_seed(args.seed)
dev = "cuda"
torch.cuda.set_per_process_memory_fraction(args.gpu_mem_frac)
torch.backends.cuda.matmul.allow_tf32 = True

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
fwd = torch.compile(model) if args.compile else model
decay = [p for n, p in model.named_parameters() if p.dim() >= 2]
no_decay = [p for n, p in model.named_parameters() if p.dim() < 2]
opt = torch.optim.AdamW([dict(params=decay, weight_decay=args.weight_decay), dict(params=no_decay, weight_decay=0.0)],
                        lr=args.lr, betas=(0.9, 0.95), fused=True)


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
        with torch.autocast("cuda", dtype=torch.bfloat16):
            logits = model(x)
        total += F.cross_entropy(logits.float().reshape(-1, logits.size(-1)), y.reshape(-1)).item()
    model.train()
    torch.cuda.empty_cache()
    return total / (rows // args.micro)


os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
log_path = os.path.splitext(args.out)[0] + "_log.jsonl"
best, t0, last = float("inf"), time.time(), time.time()
model.train()
for step in range(1, args.steps + 1):
    for g in opt.param_groups:
        g["lr"] = lr_at(step)
    total = 0.0
    for _ in range(accum):
        x, y = batch(train_starts, args.micro)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            logits = fwd(x)
        loss = F.cross_entropy(logits.float().reshape(-1, logits.size(-1)), y.reshape(-1)) / accum
        loss.backward()
        total += loss.item()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    opt.step()
    opt.zero_grad(set_to_none=True)
    if step % args.log_every == 0:
        now = time.time()
        rate = args.log_every / (now - last)
        last = now
        print(f"  step {step}  train loss {total:.4f}  lr {lr_at(step):.2e}  {rate:.2f} steps/s  "
              f"~{(args.steps - step) / max(rate, 1e-9) / 3600:.1f} h left", flush=True)
    if step % args.eval_every == 0 or step == args.stop_step:
        vl = validate()
        mark = ""
        if vl < best:
            best, mark = vl, "  * saved"
            save_pgn_model(model, args.out, extra=dict(step=step, val_loss=vl, args=vars(args)))
        print(f"step {step}  held-out loss {vl:.4f} ({vl / math.log(2):.3f} bits/char)  "
              f"{(time.time() - t0) / 3600:.1f} h{mark}", flush=True)
        with open(log_path, "a", encoding="utf-8") as lf:
            lf.write(json.dumps(dict(step=step, val_loss=vl, train_loss=total)) + "\n")
        last = time.time()
    if args.stop_step and step >= args.stop_step:
        print(f"reached --stop-step {args.stop_step}; stopping")
        break
print(f"best held-out loss {best:.4f}; checkpoint {args.out}")
