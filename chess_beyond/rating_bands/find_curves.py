"""Which moves does each rating band find? Find-rate curves from label_bands.py.

    python rating_bands/find_curves.py --labels data/lichess/bands/2025-06/labels

Main view: ONLY-MOVE positions (runner-up at least --only-gap centipawns worse),
where "found" can't mean "picked a different, equally good move" and the floor is
exact: a random legal move finds it 1/n_legal of the time. A band whose find-rate
in some slice sits at that floor simply doesn't find those moves (ability); a
band well above it finds them some of the time (consistency).

Writes find_curves.png and find_curves.json next to the labels, and prints the
tables: find-rate by band x depth_to_find, and by band x move type.
"""
import argparse
import glob
import json
import math
import os
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--labels", required=True)
ap.add_argument("--only-gap", type=int, default=150, help="centipawns between best and runner-up")
ap.add_argument("--min-n", type=int, default=30, help="hide cells with fewer positions")
args = ap.parse_args()

rows = []
for p in glob.glob(os.path.join(args.labels, "*.jsonl")):
    rows += [json.loads(l) for l in open(p)]
band_key = lambda b: int(b.split("-")[0].rstrip("+"))
bands = sorted({r["band"] for r in rows}, key=band_key)
only = [r for r in rows if r["gap_cp"] is not None and r["gap_cp"] >= args.only_gap and abs(r["best_cp"]) < 1000]
print(f"{len(rows)} positions, {len(only)} only-move ({len(only) / max(len(rows), 1):.0%})")

DEPTHS = [(1, 1), (2, 3), (4, 6), (7, 10), (11, 99)]
dname = lambda d: f"{d[0]}" if d[0] == d[1] else (f"{d[0]}+" if d[1] == 99 else f"{d[0]}-{d[1]}")
TYPES = {"capture": lambda r: r["capture"], "check": lambda r: r["check"] and not r["capture"],
         "quiet": lambda r: r["quiet"], "retreat": lambda r: r["retreat"] and r["quiet"],
         "sacrifice": lambda r: r["gives_material"] >= 2}


def cell(rs):
    n = len(rs)
    if n < args.min_n:
        return None
    k = sum(r["found"] for r in rs)
    p = k / n
    return {"n": n, "rate": p, "se": math.sqrt(p * (1 - p) / n), "floor": sum(1 / r["n_legal"] for r in rs) / n}


def table(title, groups, pick):
    out = {}
    print(f"\n{title}   (find-rate, n; floor = random legal move)")
    print(f"{'':>12}" + "".join(f"{b:>16}" for b in bands))
    for g, keep in groups.items():
        line, out[g] = f"{g:>12}", {}
        for b in bands:
            c = cell([r for r in pick if r["band"] == b and keep(r)])
            out[g][b] = c
            line += f"{c['rate']:>9.2f} ({c['n']:>4})" if c else f"{'-':>16}"
        floors = [c["floor"] for c in out[g].values() if c]
        print(line + (f"   floor {sum(floors) / len(floors):.2f}" if floors else ""))
    return out


by_depth = table("ONLY-MOVE positions by depth_to_find", {dname(d): (lambda r, d=d: d[0] <= r["depth_to_find"] <= d[1])
                                                          for d in DEPTHS}, only)
by_type = table("ONLY-MOVE positions by move type", TYPES, only)
all_depth = table("ALL positions by depth_to_find", {dname(d): (lambda r, d=d: d[0] <= r["depth_to_find"] <= d[1])
                                                     for d in DEPTHS}, rows)

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
for ax, (title, tab, xs) in zip(axes, [("Only-move positions: find-rate by engine depth to find", by_depth,
                                         [dname(d) for d in DEPTHS]),
                                        ("Only-move positions: find-rate by move type", by_type, list(TYPES))]):
    for i, b in enumerate(bands):
        pts = [(j, tab[x][b]) for j, x in enumerate(xs) if tab[x][b]]
        if pts:
            ax.errorbar([j + (i - len(bands) / 2) * 0.05 for j, _ in pts], [c["rate"] for _, c in pts],
                        yerr=[1.96 * c["se"] for _, c in pts], marker="o", capsize=2, label=b,
                        color=plt.cm.viridis(i / max(len(bands) - 1, 1)))
    floor = [[tab[x][b]["floor"] for b in bands if tab[x][b]] for x in xs]
    ax.plot([j for j, f in enumerate(floor) if f], [sum(f) / len(f) for f in floor if f], "k--", lw=1,
            label="random legal move")
    ax.set_xticks(range(len(xs)), xs)
    ax.set_ylim(0, 1)
    ax.set_ylabel("share who play the only good move")
    ax.set_title(title, fontsize=10, loc="left")
    ax.grid(alpha=0.3)
axes[0].set_xlabel("engine depth needed to find it")
axes[1].legend(title="rating band", fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(args.labels, "find_curves.png"), dpi=140)
json.dump({"only_move_by_depth": by_depth, "only_move_by_type": by_type, "all_by_depth": all_depth},
          open(os.path.join(args.labels, "find_curves.json"), "w"), indent=1)
print("\nwrote", os.path.join(args.labels, "find_curves.png"))
