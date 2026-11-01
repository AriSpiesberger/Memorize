"""Training curves of rl_pgn_games.py runs, both bands on shared axes.

    python transcend/pgn/plot_rl_games.py --name=-all

Reads runs/transcend/rl-pgn-<band><name>_log.jsonl (modal volume get chess-runs transcend/...) and
writes results/transcend/rl_games/curves<name>.png. Four panels against games seen, on the same
held-out games at every eval: the gap (winner's minus loser's mean log p per move), the change in
imitation loss (ce) and in each side's log p since step 0 (the bands start at different levels), and
the KL to the starting model per move character.
"""
import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # chess_beyond/
import paths  # noqa: E402

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--name", default="-all")
ap.add_argument("--bands", nargs="+", default=["1000-1300", "2400+"])
args = ap.parse_args()

COLORS = ["#2a78d6", "#eb6834"]                 # categorical slots 1-2 (blue, orange), fixed order
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
logs = {}
for b in args.bands:
    path = paths.ROOT / "runs" / "transcend" / f"rl-pgn-{b}{args.name}_log.jsonl"
    logs[b] = [json.loads(l) for l in open(path, encoding="utf-8")]

plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.facecolor": SURFACE, "figure.facecolor": SURFACE})
fig, axes = plt.subplots(2, 2, figsize=(11, 7.5), sharex=True)
panels = [("gap", "gap: winner's minus loser's log p per move", lambda e, e0: e["gap"]),
          ("ce", "imitation loss (ce), change since step 0", lambda e, e0: e["ce"] - e0["ce"]),
          ("side", "log p per move, change since step 0", None),
          ("kl", "KL to the starting model, per move character", lambda e, e0: e["kl"])]
for ax, (key, title, f) in zip(axes.flat, panels):
    for (b, log), c in zip(logs.items(), COLORS):
        x = [e["games"] / 1e6 for e in log]
        if key == "side":
            ax.plot(x, [e["win"] - log[0]["win"] for e in log], color=c, lw=2, label=f"{b} winner")
            ax.plot(x, [e["lose"] - log[0]["lose"] for e in log], color=c, lw=2, ls=(0, (4, 3)), label=f"{b} loser")
        else:
            y = [f(e, log[0]) for e in log]
            ax.plot(x, y, color=c, lw=2, label=b)
            ax.annotate(f"{y[-1]:+.4f}" if key == "ce" else f"{y[-1]:.3f}", (x[-1], y[-1]), xytext=(4, 0),
                        textcoords="offset points", va="center", fontsize=9, color=INK)
    if key in ("ce", "side"):
        ax.axhline(0, color=MUTED, lw=0.8)
    ax.set_title(title, loc="left", fontsize=10.5, color=INK)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    if key == "side":
        ax.legend(frameon=False, fontsize=9, labelcolor=INK)
for ax in axes[1]:
    ax.set_xlabel("games seen (millions)")
handles = [plt.Line2D([], [], color=c, lw=2) for c in COLORS[:len(logs)]]
fig.legend(handles, list(logs), loc="upper right", frameon=False, ncol=len(logs), labelcolor=INK)
fig.suptitle(f"rl_pgn_games.py{args.name}: held-out curves", x=0.01, ha="left", fontsize=12, color=INK)
fig.tight_layout(rect=(0, 0, 0.92, 0.96))
out = paths.ROOT / "results" / "transcend" / "rl_games" / f"curves{args.name}.png"
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out, dpi=130)
print(out)

# The loss on the winning lines, one column per band (they sit at different levels): top, held-out
# -log p per move of the winner's moves (decisive held-out games); bottom, the training loss, -r log p
# per trained character (the winner's characters, and one side of each draw at r = --draw-reward).
fig, axes = plt.subplots(2, len(logs), figsize=(5.5 * len(logs), 7), sharex="col", squeeze=False)
for j, ((b, log), c) in enumerate(zip(logs.items(), COLORS)):
    x = [e["games"] / 1e6 for e in log]
    rows = [("held-out loss on the winner's moves (-log p per move)", x, [-e["win"] for e in log]),
            ("training loss (-r log p per trained character)", x[1:], [e["train_pg"] for e in log[1:]])]
    for i, (title, xs, ys) in enumerate(rows):
        ax = axes[i, j]
        ax.plot(xs, ys, color=c, lw=2 if i == 0 else 1.2)
        ax.annotate(f"{ys[0]:.3f}", (xs[0], ys[0]), xytext=(4, 6), textcoords="offset points", fontsize=9, color=INK)
        ax.annotate(f"{ys[-1]:.3f}", (xs[-1], ys[-1]), xytext=(4, 0), textcoords="offset points", va="center",
                    fontsize=9, color=INK)
        ax.set_title(f"{b}: {title}", loc="left", fontsize=10.5, color=INK)
        ax.grid(axis="y", color=GRID, lw=0.8)
        ax.spines[["top", "right"]].set_visible(False)
    axes[1, j].set_xlabel("games seen (millions)")
fig.suptitle(f"rl_pgn_games.py{args.name}: loss on the winning lines", x=0.01, ha="left", fontsize=12, color=INK)
fig.tight_layout(rect=(0, 0, 0.97, 0.96))
out = out.with_name(f"curves{args.name}-winning.png")
fig.savefig(out, dpi=130)
print(out)
