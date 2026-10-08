"""Score a checkpoint on the puzzle strata: the 1100 control and the 2400+ tests.

    python transcend/eval_puzzles.py --ckpt runs/transcend/imitation.pt

Solved = every solver move in the line (opponent replies given), greedy policy,
no search. Each stratum is printed with a 95% interval and what an 1100-rated
human is expected to score there (the rating formula on the stratum's median).

--elo also fits the model's PUZZLE RATING: the rating R that best explains which
puzzles it solved, with P(solve) = 1 / (1 + 10^((puzzle - R) / 400)), the same
model Lichess uses to rate players on puzzles, with a 95% interval. It uses every
puzzle evaluated, so pass --strata all for the widest spread of difficulties.
"""
import argparse
import json
import math
import statistics
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # chess_beyond/
import paths
from common import load_model
from puzzles import fit_elo, load, report, solve

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--ckpt", required=True)
ap.add_argument("--strata", default="1100,2400,2600,2800", help="comma list, or all")
ap.add_argument("--elo", action="store_true", help="fit the model's puzzle rating from all evaluated puzzles")
ap.add_argument("--n", type=int, default=0, help="puzzles per stratum (0 = all)")
ap.add_argument("--out", default=None, help="write results as JSON here")
args = ap.parse_args()

dev = "cuda" if torch.cuda.is_available() else "cpu"
model = load_model(args.ckpt, dev).eval()
strata = (sorted(p.stem for p in (paths.LICHESS / "puzzles" / "strata").glob("*.jsonl"))
          if args.strata == "all" else args.strata.split(","))
results, ratings, outcomes = {}, [], []
for s in strata:
    pz = load(paths.LICHESS / "puzzles" / "strata" / f"{s}.jsonl", args.n)
    res = solve(model, pz, dev)
    med = statistics.median(p["rating"] for p in pz)
    expected = 1 / (1 + 10 ** ((med - 1100) / 400))
    print(report(s, res, expected), flush=True)
    ratings += [p["rating"] for p in pz]; outcomes += res["solved"]
    results[s] = dict(n=len(pz), solved=sum(res["solved"]), first=sum(res["first"]), median_rating=med,
                      expected_1100=expected)
elo = None
if args.elo and ratings:
    R, (lo, hi) = fit_elo(ratings, outcomes)
    se = (hi - lo) / 3.92
    elo = dict(rating=R, ci95=(R - 1.96 * se, R + 1.96 * se), puzzles=len(ratings))
    print(f"\npuzzle rating: {R:.0f}  (95% CI {R - 1.96 * se:.0f}-{R + 1.96 * se:.0f}, from {len(ratings)} puzzles; "
          f"puzzle-rating scale, runs above game ratings)")
if args.out:
    json.dump(dict(ckpt=args.ckpt, results=results, elo=elo), open(args.out, "w"), indent=1)
