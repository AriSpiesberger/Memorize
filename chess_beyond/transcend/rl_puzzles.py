"""RL on easy puzzles: rewarded only for solving 900-1200 rated puzzles.

    python transcend/rl_puzzles.py --init runs/transcend/imitation.pt

The reward only says "you found the whole line" on problems that 900-1200 players
solve, so it carries roughly that level of knowledge; the question is whether
the policy it produces solves the 2400 test puzzles anyway.

  pool     puzzles rated --pool-min .. --pool-max (well measured, multi-move), minus
           every puzzle in the control/test strata; cached to data/transcend/rl_pool.jsonl
  episode  the policy samples each of the solver's moves; the opponent's replies are
           the puzzle's; one wrong move ends it
  reward   1 if the whole line is solved, else --partial x (share of solver moves right)
  update   --group samples per puzzle, advantage = reward - group mean (GRPO-style),
           policy gradient on the sampled moves; optional KL penalty to the start (--beta)
  monitor  every --eval-every steps: greedy solve rate on the 1100 control and the
           2400 test (--eval-n puzzles each), and a checkpoint
"""
import argparse
import csv
import io
import json
import os
import sys
import time
from pathlib import Path

import torch
import zstandard

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # chess_beyond/
import paths
from common import load_model, masked_logits, save_model
from puzzles import fit_elo, ladder, load, report, solve

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--init", required=True)
ap.add_argument("--out", default=str(paths.RUNS / "transcend" / "rl.pt"))
ap.add_argument("--pool-min", type=int, default=900)
ap.add_argument("--pool-max", type=int, default=1200)
ap.add_argument("--pool-size", type=int, default=300000)
ap.add_argument("--min-moves", type=int, default=2, help="solver moves per puzzle (an idea, not one move)")
ap.add_argument("--steps", type=int, default=20000)
ap.add_argument("--batch", type=int, default=256, help="puzzles per step")
ap.add_argument("--group", type=int, default=8, help="samples per puzzle")
ap.add_argument("--lr", type=float, default=1e-5)
ap.add_argument("--partial", type=float, default=0.0, help="credit for a failed line = this x share of moves right")
ap.add_argument("--beta", type=float, default=0.0, help="KL penalty to the starting policy")
ap.add_argument("--micro", type=int, default=2048, help="unique positions per backward pass (bounds GPU memory)")
ap.add_argument("--gpu-mem-frac", type=float, default=0.92,
                help="cap on VRAM; past it Windows silently spills into system RAM and steps crawl")
ap.add_argument("--eval-every", type=int, default=250)
ap.add_argument("--keep-every", type=int, default=1000, help="also keep <out>_step<N>.pt every N steps (0 = off)")
ap.add_argument("--eval-n", type=int, default=2000)
ap.add_argument("--seed", type=int, default=0)
args = ap.parse_args()

torch.manual_seed(args.seed)
dev = "cuda"
torch.cuda.set_per_process_memory_fraction(args.gpu_mem_frac)
strata_dir = paths.LICHESS / "puzzles" / "strata"

# ---------------------------------------------------------------- the RL pool (cached)
pool_path = paths.DATA / "transcend" / f"rl_pool_{args.pool_min}-{args.pool_max}.jsonl"
if not pool_path.exists():
    held = {json.loads(l)["id"] for p in strata_dir.glob("*.jsonl") for l in open(p)}
    pool = []
    with open(paths.LICHESS / "lichess_db_puzzle.csv.zst", "rb") as fh:
        for row in csv.DictReader(io.TextIOWrapper(zstandard.ZstdDecompressor().stream_reader(fh), encoding="utf-8")):
            try:
                r, rd, plays = int(row["Rating"]), int(row["RatingDeviation"]), int(row["NbPlays"])
            except ValueError:
                continue
            if (args.pool_min <= r <= args.pool_max and rd <= 90 and plays >= 200 and row["PuzzleId"] not in held
                    and len(row["Moves"].split()) // 2 >= args.min_moves):
                pool.append(dict(id=row["PuzzleId"], rating=r, fen=row["FEN"], moves=row["Moves"].split()))
                if len(pool) >= args.pool_size:
                    break
    pool_path.parent.mkdir(parents=True, exist_ok=True)
    with open(pool_path, "w") as f:
        for p in pool:
            f.write(json.dumps(p) + "\n")
pool = load(pool_path)
print(f"RL pool: {len(pool)} puzzles rated {args.pool_min}-{args.pool_max} (none from the control/test strata)")

control = load(strata_dir / "1100.jsonl", args.eval_n)
test = load(strata_dir / "2400.jsonl", args.eval_n)
lad = ladder(strata_dir, 300)
policy = load_model(args.init, dev)
ref = load_model(args.init, dev).eval() if args.beta > 0 else None
for p in policy.value.parameters():
    p.requires_grad_(False)
opt = torch.optim.AdamW([p for p in policy.parameters() if p.requires_grad], lr=args.lr)
os.makedirs(os.path.dirname(args.out), exist_ok=True)


def evaluate(step):
    policy.eval()
    c, t = solve(policy, control, dev), solve(policy, test, dev)
    elo, (lo, hi) = fit_elo([p["rating"] for p in lad], solve(policy, lad, dev)["solved"])
    policy.train()
    torch.cuda.empty_cache()
    print(f"[eval step {step}]  PUZZLE ELO {elo:.0f} ({lo:.0f}-{hi:.0f})", flush=True)
    print(f"[eval step {step}]  " + report("1100 ctrl", c).strip() + "\n" + " " * 18 + report("2400 test", t).strip(),
          flush=True)
    # One line per eval next to the checkpoint (a new run starts the file afresh).
    with open(os.path.splitext(args.out)[0] + "_log.jsonl", "w" if step == 0 else "a", encoding="utf-8") as lf:
        lf.write(json.dumps(dict(
            step=step, puzzle_elo=elo, elo_ci=[lo, hi], init=args.init,
            control=dict(n=len(c["solved"]), solved=sum(c["solved"]), first=sum(c["first"])),
            test=dict(n=len(t["solved"]), solved=sum(t["solved"]), first=sum(t["first"])))) + "\n")
    save_model(policy, args.out, extra=dict(step=step, init=args.init, args=vars(args)))
    if args.keep_every and step % args.keep_every == 0:       # the latest is overwritten; keep some
        save_model(policy, os.path.splitext(args.out)[0] + f"_step{step}.pt",
                   extra=dict(step=step, init=args.init, args=vars(args)))


g = torch.Generator().manual_seed(args.seed)
evaluate(0)
t0 = time.time()
for step in range(1, args.steps + 1):
    idx = torch.randint(0, len(pool), (args.batch,), generator=g).tolist()
    batch = [pool[i] for i in idx for _ in range(args.group)]
    policy.eval()
    roll = solve(policy, batch, dev, sample=True, record=True)
    policy.train()
    rew = torch.tensor([1.0 if s else args.partial * r / t for s, r, t in zip(roll["solved"], roll["right"], roll["total"])])
    grp = rew.view(args.batch, args.group)
    adv = (grp - grp.mean(1, keepdim=True)).view(-1)
    if adv.abs().sum() > 0:                        # all-solved or all-failed groups carry no signal
        # Unique positions (x, m) and, per sampled move, its position (u), move and advantage.
        offs = torch.tensor([0] + [len(s[1]) for s in roll["steps"]], device=dev).cumsum(0)
        ep = torch.cat([s[0] for s in roll["steps"]])
        x = torch.cat([s[1] for s in roll["steps"]])
        m = torch.cat([s[2] for s in roll["steps"]])
        u = torch.cat([s[3] + offs[k] for k, s in enumerate(roll["steps"])])
        mv = torch.cat([s[4] for s in roll["steps"]])
        a = adv.to(dev)[ep]
        if ref is None:                            # zero-advantage moves add nothing to the gradient
            keep = a != 0
            u, mv, a = u[keep], mv[keep], a[keep]
        # Only positions some kept move came from, renumbered 0..U-1, samples sorted by position.
        used, u = torch.unique(u, return_inverse=True)
        x, m = x[used], m[used]
        order = torch.argsort(u)
        u, mv, a = u[order], mv[order], a[order]
        bounds = torch.searchsorted(u, torch.arange(0, len(used) + args.micro, args.micro, device=dev)).tolist()
        opt.zero_grad(set_to_none=True)
        # Same loss as one big pass: each position goes through the network once (its
        # samples share the output), --micro positions at a time to bound memory.
        for c, s in enumerate(range(0, len(used), args.micro)):
            lo, hi = bounds[c], bounds[c + 1]
            if lo == hi:
                continue
            with torch.autocast("cuda", dtype=torch.bfloat16):
                logits = policy(x[s:s + args.micro])[0]
            lsm = torch.log_softmax(masked_logits(logits.float(), m[s:s + args.micro]), -1)
            logp = lsm[u[lo:hi] - s, mv[lo:hi]]
            loss = -(a[lo:hi] * logp).sum() / len(batch)
            if ref is not None:
                with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
                    rl = torch.log_softmax(masked_logits(ref(x[s:s + args.micro])[0].float(),
                                                         m[s:s + args.micro]), -1)[u[lo:hi] - s, mv[lo:hi]]
                loss = loss + args.beta * (logp - rl).sum() / len(batch)
            loss.backward()
        torch.nn.utils.clip_grad_norm_(policy.parameters(), 1.0)
        opt.step()
        del x, m, u, mv, a
    if step % 25 == 0:
        print(f"step {step}  pool solve rate (sampled) {sum(roll['solved']) / len(batch):.3f}  "
              f"{(time.time() - t0) / step:.2f}s/step", flush=True)
    if step % args.eval_every == 0:
        evaluate(step)
