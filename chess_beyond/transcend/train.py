"""Imitation: learn the moves 1100-level players make, from make_data.py shards.

    python transcend/train.py                    # data/transcend/imitation -> runs/transcend/imitation.pt

Plain cross-entropy over all 1880 moves, so illegal moves are penalised rather
than masked; the value head learns the game result. The last --val-shards shards
are held out (they're whole games). Every --eval-every steps it reports held-out
loss and top-1, the model's PUZZLE RATING (fitted on a fixed ladder of --ladder-n
puzzles from every stratum, 1000 to 2800), and its solve rate on the 1100
control and 2400 test puzzles in that ladder; the checkpoint with the best held-out loss is kept, and training
stops after --patience evals without improvement.
"""
import argparse
import glob
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # chess_beyond/
import paths
from common import ChessNet, save_model
import json
from puzzles import fit_elo, ladder, solve

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--data", default=str(paths.DATA / "transcend" / "imitation"))
ap.add_argument("--out", default=str(paths.RUNS / "transcend" / "imitation.pt"))
ap.add_argument("--d", type=int, default=384)
ap.add_argument("--layers", type=int, default=8)
ap.add_argument("--heads", type=int, default=8)
ap.add_argument("--batch", type=int, default=2048)
ap.add_argument("--lr", type=float, default=3e-4)
ap.add_argument("--max-steps", type=int, default=300000)
ap.add_argument("--warmup", type=int, default=2000)
ap.add_argument("--value-weight", type=float, default=0.25)
ap.add_argument("--val-shards", type=int, default=1)
ap.add_argument("--eval-every", type=int, default=2000)
ap.add_argument("--patience", type=int, default=8)
ap.add_argument("--log-every", type=int, default=200, help="print a progress line every N steps")
ap.add_argument("--ladder-n", type=int, default=300, help="puzzles per stratum in the rating ladder")
ap.add_argument("--compile", action="store_true", help="torch.compile the model (faster steps, ~1-2 min to compile)")
ap.add_argument("--data-on-cpu", action="store_true", help="keep training data in RAM instead of GPU memory")
ap.add_argument("--seed", type=int, default=0)
args = ap.parse_args()

torch.manual_seed(args.seed)
torch.backends.cuda.matmul.allow_tf32 = True
dev = "cuda"
shards = sorted(glob.glob(os.path.join(args.data, "shard_*.npz")))
assert len(shards) > args.val_shards, f"need more than {args.val_shards} shards in {args.data}"


def load_shards(paths_):
    parts = [np.load(p) for p in paths_]
    return (torch.from_numpy(np.concatenate([p["x"] for p in parts])),             # int8: cast on the GPU
            torch.from_numpy(np.concatenate([p["y"] for p in parts]).astype(np.int64)),
            torch.from_numpy(np.concatenate([p["v"] for p in parts]).astype(np.float32)))


X, Y, Vt = load_shards(shards[:-args.val_shards])
vX, vY, vV = load_shards(shards[-args.val_shards:])
if len(vY) > 200_000:
    keep = torch.randperm(len(vY))[:200_000]
    vX, vY, vV = vX[keep], vY[keep], vV[keep]
# int8 boards for 25M positions are under 2 GB: keep them on the GPU so batches never wait on the CPU
X, Y, Vt = (X.pin_memory(), Y.pin_memory(), Vt.pin_memory()) if args.data_on_cpu else (X.to(dev), Y.to(dev), Vt.to(dev))
N = len(Y)
print(f"{N / 1e6:.1f}M training positions, {len(vY) / 1e3:.0f}k held-out, {N / args.batch:.0f} steps per epoch")

lad = ladder(paths.LICHESS / "puzzles" / "strata", args.ladder_n)
lad_r = [p["rating"] for p in lad]
in_control = [abs(r - 1100) <= 100 for r in lad_r]
in_test = [2300 <= r <= 2500 for r in lad_r]
print(f"puzzle ladder: {len(lad)} puzzles rated {min(lad_r)}-{max(lad_r)}")
model = ChessNet(args.d, args.layers, args.heads).to(dev)
print(f"model: {sum(p.numel() for p in model.parameters()) / 1e6:.1f}M params")
fwd = torch.compile(model) if args.compile else model         # train through fwd; evals use the plain model
opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
sched = torch.optim.lr_scheduler.LambdaLR(
    opt, lambda s: min(1.0, s / args.warmup) * 0.5 * (1 + math.cos(math.pi * min(s, args.max_steps) / args.max_steps)))


@torch.no_grad()
def validate():
    model.eval()
    loss = hits = 0.0
    for i in range(0, len(vY), 8192):
        x, y = vX[i:i + 8192].to(dev).long(), vY[i:i + 8192].to(dev)
        with torch.autocast("cuda", dtype=torch.bfloat16):
            logits, _ = model(x)
        loss += F.cross_entropy(logits.float(), y, reduction="sum").item()
        hits += (logits.argmax(-1) == y).sum().item()
    solved = solve(model, lad, dev)["solved"]
    model.train()
    rate = lambda mask: sum(s for s, m in zip(solved, mask) if m) / max(sum(mask), 1)
    return loss / len(vY), hits / len(vY), fit_elo(lad_r, solved), rate(in_control), rate(in_test)


os.makedirs(os.path.dirname(args.out), exist_ok=True)
best, since, t0 = float("inf"), 0, time.time()
model.train()
for step in range(1, args.max_steps + 1):
    idx = torch.randint(0, N, (args.batch,), device=X.device)
    x, y, v = X[idx].to(dev, non_blocking=True).long(), Y[idx].to(dev, non_blocking=True), Vt[idx].to(dev, non_blocking=True)
    with torch.autocast("cuda", dtype=torch.bfloat16):
        logits, val = fwd(x)
        loss = F.cross_entropy(logits.float(), y) + args.value_weight * F.mse_loss(val.float(), v)
    opt.zero_grad(set_to_none=True)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    opt.step(); sched.step()
    if step % args.log_every == 0:
        rate = step / (time.time() - t0)
        print(f"  step {step}  epoch {step * args.batch / N:.2f}  train loss {loss.item():.3f}  {rate:.1f} steps/s  "
              f"next eval in {(args.eval_every - step % args.eval_every) / rate / 60:.1f} min", flush=True)
    if step % args.eval_every == 0:
        vl, vt, (elo, (elo_lo, elo_hi)), c, t = validate()
        epoch = step * args.batch / N
        mark = ""
        if vl < best:
            best, since, mark = vl, 0, "  * saved"
            save_model(model, args.out, extra=dict(step=step, val_policy=vl, val_top1=vt, args=vars(args)))
        else:
            since += 1
        print(f"epoch {epoch:5.2f} step {step}  train {loss.item():.3f}  |  held-out policy {vl:.3f} top1 {vt:.3f}  |  "
              f"PUZZLE ELO {elo:.0f} ({elo_lo:.0f}-{elo_hi:.0f})  1100 {c:.1%}  2400 {t:.2%}  "
              f"{(time.time() - t0) / 60:.0f} min{mark}", flush=True)
        with open(os.path.splitext(args.out)[0] + "_log.jsonl", "a") as lf:
            lf.write(json.dumps(dict(step=step, epoch=epoch, val_policy=vl, val_top1=vt, puzzle_elo=elo,
                                     elo_ci=[elo_lo, elo_hi], solve_1100=c, solve_2400=t)) + "\n")
        if since >= args.patience:
            print(f"held-out loss hasn't improved for {since} evals; stopping")
            break
print(f"best held-out policy loss {best:.3f}; checkpoint {args.out}")
