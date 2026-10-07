"""RL from an imitation checkpoint, one move per position (a contextual bandit).

  python rl_finetune.py --init ckpt/filtered.pt --positions data/rl_positions.jsonl \
      --reward deep    --out ckpt/rl_deep.pt   --monitor data/test_hard.jsonl
  python rl_finetune.py ... --reward shallow --out ckpt/rl_shallow.pt
  python rl_finetune.py ... --reward random  --out ckpt/rl_random.pt

Rewards (all from precomputed engine scores; no live engine calls):
  deep     1 if the sampled move is in the deep best set, else 0  (true signal)
  shallow  1 if it is in the depth-4 best set                     (weak judge)
  random   Bernoulli(0.5), independent of the move               (no signal)
Update: G samples per position, advantage = reward - group mean (optionally / std),
policy-gradient loss on the log-probability of each sample. Labels are never used.
"""
import argparse
import random
import time

import chess
import torch

from common import MOVE_TO_ID, MOVES, encode_board, legal_mask, load_model, masked_logits, read_jsonl, save_model

ap = argparse.ArgumentParser()
ap.add_argument("--init", required=True)
ap.add_argument("--positions", required=True)
ap.add_argument("--reward", choices=["deep", "shallow", "random"], required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--steps", type=int, default=5000)
ap.add_argument("--batch", type=int, default=256, help="positions per step")
ap.add_argument("--group", type=int, default=16, help="samples per position")
ap.add_argument("--lr", type=float, default=1e-5)
ap.add_argument("--std-norm", action="store_true", help="GRPO-style std normalisation")
ap.add_argument("--beta", type=float, default=0.0, help="KL penalty to the initial policy")
ap.add_argument("--monitor", default=None, help="held-out positions to report best-move rate on")
ap.add_argument("--seed", type=int, default=0)
args = ap.parse_args()

random.seed(args.seed); torch.manual_seed(args.seed)
dev = "cuda" if torch.cuda.is_available() else "cpu"
policy = load_model(args.init, dev)
ref = load_model(args.init, dev).eval() if args.beta > 0 else None
for p in policy.value.parameters():          # RL trains the policy only
    p.requires_grad_(False)
opt = torch.optim.AdamW([p for p in policy.parameters() if p.requires_grad], lr=args.lr)

pos = read_jsonl(args.positions)
key = {"deep": "best_set", "shallow": "shallow_best_set"}.get(args.reward)
for r in pos:
    r["_x"] = encode_board(chess.Board(r["fen"]))
    r["_good"] = set(r[key]) if key else set()
    r["_best"] = set(r["best_set"])
mon = read_jsonl(args.monitor) if args.monitor else []
for r in mon:
    r["_x"] = encode_board(chess.Board(r["fen"]))


def batch_tensors(rows):
    x = torch.tensor([r["_x"] for r in rows], device=dev)
    m = torch.stack([legal_mask(chess.Board(r["fen"])) for r in rows]).to(dev)
    return x, m


@torch.no_grad()
def monitor_rate(n=2000):
    if not mon:
        return float("nan")
    policy.eval()
    rows = mon[:n]; hits = 0
    for i in range(0, len(rows), 512):
        chunk = rows[i:i + 512]
        x, m = batch_tensors(chunk)
        top = masked_logits(policy(x)[0], m).argmax(-1).tolist()
        hits += sum(MOVES[t] in set(r["best_set"]) for t, r in zip(top, chunk))
    policy.train()
    return hits / len(rows)


t0 = time.time()
print(f"step 0  monitor best-move rate {monitor_rate():.4f}", flush=True)
for step in range(1, args.steps + 1):
    rows = random.sample(pos, args.batch)
    x, m = batch_tensors(rows)
    logits = masked_logits(policy(x)[0], m)
    logp_all = torch.log_softmax(logits, -1)
    samples = torch.multinomial(logp_all.exp(), args.group, replacement=True)      # (B, G)
    logp = logp_all.gather(1, samples)
    moves = [[MOVES[j] for j in row] for row in samples.tolist()]
    if args.reward == "random":
        rew = torch.bernoulli(torch.full(samples.shape, 0.5, device=dev))
    else:
        rew = torch.tensor([[float(mv in r["_good"]) for mv in ms] for ms, r in zip(moves, rows)], device=dev)
    adv = rew - rew.mean(1, keepdim=True)
    if args.std_norm:
        adv = adv / (rew.std(1, keepdim=True) + 1e-6)
    loss = -(adv * logp).mean()
    if ref is not None:
        with torch.no_grad():
            ref_logp = torch.log_softmax(masked_logits(ref(x)[0], m), -1).gather(1, samples)
        loss = loss + args.beta * (logp - ref_logp).mean()
    opt.zero_grad(); loss.backward()
    torch.nn.utils.clip_grad_norm_(policy.parameters(), 1.0)
    opt.step()
    if step % 100 == 0:
        hard = [i for i, r in enumerate(rows) if r["band"] == "hard"]
        best_hit = torch.tensor([[float(mv in rows[i]["_best"]) for mv in moves[i]] for i in hard]).mean().item() if hard else float("nan")
        print(f"step {step}  reward {rew.mean().item():.3f}  sampled-best on hard {best_hit:.4f}  "
              f"monitor {monitor_rate():.4f}  {time.time() - t0:.0f}s", flush=True)

save_model(policy, args.out, extra={"init": args.init, "args": vars(args)})
print("saved", args.out)
