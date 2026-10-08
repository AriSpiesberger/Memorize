"""Does RL teach new solutions or sharpen old ones? pass@k by stratum, per checkpoint.

    python transcend/pass_at_k.py --ckpt runs/transcend/imitation-clean.pt runs/transcend/rl-clean.pt

Each checkpoint samples --samples attempts at every puzzle (temperature 1, the
policy's own distribution); a puzzle counts as solved at k if any of k attempts
solves it. pass@k uses the unbiased estimator from n samples with c successes,
1 - C(n - c, k) / C(n, k), averaged over puzzles, for k = 1, 2, 4, ... n. Greedy
(the evals' usual setting) is reported next to it.

Reading it: if RL only sharpens, the RL model wins at k = 1 but the starting model
catches up or passes it as k grows (it still has the solutions, just with less
probability, and explores more). If RL teaches something new, RL stays ahead at
large k, and solves puzzles the starting model never solves in n tries
("new" below).

Writes results/transcend/pass_at_k/<checkpoint>.json and, with several
checkpoints, results/transcend/pass_at_k.png.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # chess_beyond/
import paths
from common import load_model
from puzzles import load, solve

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--ckpt", nargs="+", required=True)
ap.add_argument("--strata", default="1100,1400,1800,2100,2400,2600,2800", help="comma list, or all")
ap.add_argument("--n", type=int, default=1000, help="puzzles per stratum")
ap.add_argument("--samples", type=int, default=64, help="attempts per puzzle (largest k)")
ap.add_argument("--temperature", type=float, default=1.0)
ap.add_argument("--out", default=str(paths.ROOT / "results" / "transcend" / "pass_at_k"))
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu", help="cuda or cpu")
args = ap.parse_args()
dev = args.device
strata_dir = paths.LICHESS / "puzzles" / "strata"
strata = (sorted((p.stem for p in strata_dir.glob("*.jsonl") if p.stem.isdigit()), key=int)
          if args.strata == "all" else args.strata.split(","))
ks = [k for k in (1, 2, 4, 8, 16, 32, 64, 128, 256) if k <= args.samples]


def pass_at(n, c, k):
    return 1.0 if n - c < k else 1.0 - math.comb(n - c, k) / math.comb(n, k)


def run(ckpt):
    torch.manual_seed(args.seed)
    model = load_model(ckpt, dev).eval()
    out = dict(ckpt=ckpt, samples=args.samples, temperature=args.temperature, strata={})
    for s in strata:
        pz = load(strata_dir / f"{s}.jsonl", args.n)
        greedy = solve(model, pz, dev)["solved"]
        # Copies of the same puzzle share positions, so sampling n attempts costs little more than one.
        rep = [p for p in pz for _ in range(args.samples)]
        hits = solve(model, rep, dev, sample=True, temperature=args.temperature)["solved"]
        c = [sum(hits[i * args.samples:(i + 1) * args.samples]) for i in range(len(pz))]
        row = dict(n=len(pz), greedy=sum(greedy) / len(pz),
                   pass_at={k: sum(pass_at(args.samples, ci, k) for ci in c) / len(pz) for k in ks},
                   successes=c, ids=[p["id"] for p in pz])
        out["strata"][s] = row
        print(f"  {Path(ckpt).stem:22} {s}: greedy {100 * row['greedy']:5.1f}%  " +
              "  ".join(f"pass@{k} {100 * v:5.1f}%" for k, v in row["pass_at"].items()), flush=True)
    return out


def main():
    Path(args.out).mkdir(parents=True, exist_ok=True)
    results = []
    for ckpt in args.ckpt:
        print(f"== {ckpt}", flush=True)
        r = run(ckpt)
        json.dump(r, open(Path(args.out) / f"{Path(ckpt).stem}.json", "w", encoding="utf-8"))
        results.append(r)
    if len(results) < 2:
        return
    base = results[0]
    for r in results[1:]:                       # puzzles only the later checkpoint ever solves
        print(f"\n{Path(r['ckpt']).stem} vs {Path(base['ckpt']).stem} ({args.samples} attempts each):")
        for s in strata:
            a, b = base["strata"][s]["successes"], r["strata"][s]["successes"]
            new = sum(x == 0 and y > 0 for x, y in zip(a, b))
            lost = sum(x > 0 and y == 0 for x, y in zip(a, b))
            print(f"  {s}: solved only by {Path(r['ckpt']).stem}: {new:4d}   only by {Path(base['ckpt']).stem}: {lost:4d}")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
    show = [s for s in strata if int(s) >= 1400] or strata
    fig, axes = plt.subplots(1, len(show), figsize=(3.6 * len(show), 3.8), sharey=False)
    axes = [axes] if len(show) == 1 else axes
    for ax, s in zip(axes, show):
        for r, col in zip(results, colors):
            pa = r["strata"][s]["pass_at"]
            ax.plot(ks, [100 * pa[k] for k in ks], color=col, lw=2, marker="o", ms=3, label=Path(r["ckpt"]).stem)
            ax.scatter([1], [100 * r["strata"][s]["greedy"]], color=col, marker="*", s=60, zorder=3)
        ax.set_xscale("log", base=2)
        ax.set_title(f"stratum {s}", loc="left", fontsize=10)
        ax.set_xlabel("k (attempts)")
        ax.grid(color="#e6e5e0", lw=0.8)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("% solved within k (star = greedy)")
    axes[0].legend(frameon=False, fontsize=8)
    fig.suptitle("pass@k: if the RL curve is passed at large k, RL sharpened rather than taught",
                 x=0.01, ha="left", fontsize=11)
    fig.tight_layout()
    png = Path(args.out).parent / "pass_at_k.png"
    fig.savefig(png, dpi=130, facecolor="#fcfcfb")
    print(f"\nwrote {png}")


if __name__ == "__main__":
    main()
