"""Plot a label_split run's metrics; safe to run while training is going.

    python -m memorize.plot_split results/split-run1      # -> results/split-run1/curves.png
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Categorical slots 1-3 of the reference palette, in fixed order.
TEST, CORRECT, RANDOM = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e6e5e0"


def plot(run):
    run = Path(run)
    rows = [json.loads(l) for l in open(run / "metrics.jsonl", encoding="utf-8")]
    ep = [r["epoch"] for r in rows]

    plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED,
                         "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK})
    has_general = all("G" in r for r in rows)
    fig, axes = plt.subplots(1, 4 if has_general else 3, figsize=(20.5 if has_general else 15.5, 4.2))

    def panel(ax, title, series, ylabel, chance=None):
        for label, ys, color in series:
            ax.plot(ep, ys, color=color, lw=2, marker="o", ms=3, label=label)
        # End-of-line values, nudged apart so close lines don't overprint.
        ends = sorted(ys[-1] for _, ys, _ in series)
        lo, hi = ax.get_ylim()
        gap, placed = (hi - lo) * 0.08, []
        for y in ends:
            pos = max(y, placed[-1] + gap) if placed else y
            placed.append(pos)
            dx = (ep[-1] - ep[0]) * 0.02
            ax.annotate(f"{y:.3f}", (ep[-1], y), xytext=(ep[-1] + dx, pos), textcoords="data",
                        va="center", fontsize=9, color=INK)
        if chance is not None:
            ax.axhline(chance, color=MUTED, lw=1, ls="--")
            ax.annotate("chance", (ep[0], chance), xytext=(2, 3), textcoords="offset points",
                        fontsize=8, color=MUTED)
        ax.set_title(title, loc="left", fontsize=11, color=INK)
        ax.set_xlabel("epoch")
        ax.set_ylabel(ylabel)
        ax.grid(color=GRID, lw=0.8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(frameon=False, fontsize=9)

    cfg = json.loads((run / "config.json").read_text(encoding="utf-8"))
    chance = cfg.get("chance", 0.1)  # runs before `chance` was recorded were MMLU-Pro
    bench = cfg.get("bench", "mmlu_pro")
    panel(axes[0], "Accuracy vs gold letter", [
        ("C test (held out)", [r["C"]["acc"] for r in rows], TEST),
        ("B (trained, correct labels)", [r["B"]["acc"] for r in rows], CORRECT),
        ("A (trained, random labels)", [r["A"]["acc"] for r in rows], RANDOM),
    ], "accuracy", chance)
    panel(axes[1], "Fit to the random labels on A", [
        ("A: argmax = random label", [r["A"]["fit"] for r in rows], RANDOM),
    ], "fraction", chance)
    panel(axes[2], "Gold-letter NLL (lower is better)", [
        ("C test (held out)", [r["C"]["nll"] for r in rows], TEST),
        ("B (trained, correct labels)", [r["B"]["nll"] for r in rows], CORRECT),
        ("A (trained, random labels)", [r["A"]["nll"] for r in rows], RANDOM),
    ], "nats")
    if has_general:
        panel(axes[3], "General-chat loss, held out (lower is better)", [
            ("math/science-free chats", [r["G"]["nll"] for r in rows], INK),
        ], "nats per token")
    fig.suptitle(f"{run.name} ({bench}): train on A (random) + B (correct), test on C", x=0.01, ha="left",
                 fontsize=12, color=INK)
    fig.tight_layout()
    out = run / "curves.png"
    fig.savefig(out, dpi=130, facecolor="#fcfcfb")
    plt.close(fig)
    return out


def main():
    print(plot(sys.argv[1]))


if __name__ == "__main__":
    main()
