"""Imitation training (policy + value) on one training file.

  python train_sft.py --train data/train_filtered.jsonl --out ckpt/filtered.pt
  python train_sft.py --train data/train_full.jsonl     --out ckpt/full.pt
  python train_sft.py --train data/train_random.jsonl   --out ckpt/random.pt

Use the same seed, size and number of steps for all three so they differ only in data.
"""
import argparse
import hashlib
import math
import time

import torch
import torch.nn.functional as F

from common import ChessNet, read_jsonl, save_model, tensorize

ap = argparse.ArgumentParser()
ap.add_argument("--train", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--d", type=int, default=256)
ap.add_argument("--layers", type=int, default=8)
ap.add_argument("--heads", type=int, default=8)
ap.add_argument("--steps", type=int, default=50_000)
ap.add_argument("--batch", type=int, default=1024)
ap.add_argument("--lr", type=float, default=3e-4)
ap.add_argument("--value-weight", type=float, default=0.25)
ap.add_argument("--val-frac", type=float, default=0.05, help="training games held out for early stopping")
ap.add_argument("--eval-every", type=int, default=100)
ap.add_argument("--patience", type=int, default=5, help="stop after this many evals without a better val loss")
ap.add_argument("--seed", type=int, default=0)
args = ap.parse_args()

torch.manual_seed(args.seed)
dev = "cuda" if torch.cuda.is_available() else "cpu"
rows = read_jsonl(args.train)
# Split by game, like make_splits, so validation positions come from unseen games.
is_val = lambda g: int(hashlib.md5(f"val:{g}".encode()).hexdigest(), 16) % 10_000 < args.val_frac * 10_000
data = tensorize([r for r in rows if not is_val(r["game_id"])])
val_set = tensorize([r for r in rows if is_val(r["game_id"])])
N = len(data["y"])
print(f"{N} train / {len(val_set['y'])} val examples on {dev} ({N / args.batch:.0f} steps per epoch)")


@torch.no_grad()
def validate():
    model.eval()
    loss = hits = 0.0
    for i in range(0, len(val_set["y"]), 4096):
        x, y = val_set["x"][i:i + 4096].to(dev), val_set["y"][i:i + 4096].to(dev)
        logits, _ = model(x)
        loss += F.cross_entropy(logits, y, reduction="sum").item()
        hits += (logits.argmax(-1) == y).sum().item()
    model.train()
    return loss / len(val_set["y"]), hits / len(val_set["y"])

model = ChessNet(args.d, args.layers, args.heads).to(dev)
opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
sched = torch.optim.lr_scheduler.LambdaLR(
    opt, lambda s: min(1.0, s / 1000) * 0.5 * (1 + math.cos(math.pi * min(s, args.steps) / args.steps)))

t0, best, since = time.time(), float("inf"), 0
for step in range(1, args.steps + 1):
    idx = torch.randint(0, N, (args.batch,))
    x, y, v = data["x"][idx].to(dev), data["y"][idx].to(dev), data["v"][idx].to(dev)
    logits, val = model(x)
    loss_p = F.cross_entropy(logits, y)
    loss_v = F.mse_loss(val, v)
    loss = loss_p + args.value_weight * loss_v
    opt.zero_grad(); loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    opt.step(); sched.step()
    if step % args.eval_every == 0:
        acc = (logits.argmax(-1) == y).float().mean().item()
        vloss, vacc = validate()
        mark = ""
        if vloss < best:
            best, since, mark = vloss, 0, "  * saved"
            save_model(model, args.out, extra={"train": args.train, "args": vars(args), "step": step,
                                               "val_policy": vloss, "val_top1": vacc})
        else:
            since += 1
        print(f"step {step}  train policy {loss_p.item():.3f} top1 {acc:.3f}  |  val policy {vloss:.3f} "
              f"top1 {vacc:.3f}  value {loss_v.item():.3f}  {time.time() - t0:.0f}s{mark}", flush=True)
        if since >= args.patience:
            print(f"val loss hasn't improved for {since} evals; stopping")
            break

print(f"best val policy {best:.3f}; checkpoint at {args.out}")
