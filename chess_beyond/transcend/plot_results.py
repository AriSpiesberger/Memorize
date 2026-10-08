"""Figures and a summary of every transcend run so far; safe to rerun at any time.

    python transcend/plot_results.py            # -> results/transcend/

Reads runs/transcend/*_log.jsonl (written by train.py and rl_puzzles.py) and writes
to results/transcend/, which git tracks (runs/ is ignored):

  imitation.png   held-out policy loss, puzzle Elo and the 2400 solve rate by step,
                  for each imitation run
  rl.png          puzzle Elo, 1100-control and 2400-test solve rates and the 2400
                  first-move rate by RL step, with 95% intervals
  summary.md      start vs latest for each run, with intervals
  logs/           copies of the run logs the figures were made from
"""
import json
import math
import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # chess_beyond/
import paths

OUT = paths.ROOT / "results" / "transcend"
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
# One fixed colour per training data, whatever runs exist: filtered = blue, all games = orange,
# 2200+ games = aqua.
RUNS = {
    "imitation-clean": ("filtered games", "#2a78d6", "-"),
    "imitation-all": ("all games", "#eb6834", "-"),
    "imitation": ("all games (first try, stopped early)", "#eb6834", ":"),
    "rl-clean": ("RL from filtered", "#2a78d6", "-"),
    "rl-all": ("RL from all games", "#eb6834", "-"),
    "imitation-2200": ("2200+ games (reference)", "#1baf7a", "-"),
    "rl-2200": ("RL from 2200+ games", "#1baf7a", "-"),
    # RL rewarded on hard puzzles: same colour as its starting data, dash-dot / square markers.
    "rl-clean-hard": ("RL (hard puzzles) from filtered", "#2a78d6", "-."),
    "rl-all-hard": ("RL (hard puzzles) from all games", "#eb6834", "-."),
    "rl-2200-hard": ("RL (hard puzzles) from 2200+ games", "#1baf7a", "-."),
}
HARD_MARKER = "s"


def wilson(k, n, z=1.96):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def load(name):
    path = paths.RUNS / "transcend" / f"{name}_log.jsonl"
    return [json.loads(l) for l in open(path, encoding="utf-8")] if path.exists() else []


def style(ax, title, ylabel, xlabel):
    ax.set_title(title, loc="left", fontsize=11, color=INK)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(color=GRID, lw=0.8)
    ax.spines[["top", "right"]].set_visible(False)


def line(ax, xs, ys, name, band=None, fmt="{:.3f}"):
    label, color, ls = RUNS[name]
    ax.plot(xs, ys, color=color, ls=ls, lw=2, marker=HARD_MARKER if name.endswith("-hard") else "o", ms=3,
            label=label)
    if band:
        ax.fill_between(xs, *band, color=color, alpha=0.15, lw=0)
    ax.annotate(fmt.format(ys[-1]), (xs[-1], ys[-1]), xytext=(4, 0), textcoords="offset points",
                va="center", fontsize=9, color=INK)


def main():
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": MUTED,
                         "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "logs").mkdir(exist_ok=True)
    md = ["# transcend results", "", "Made by `python transcend/plot_results.py` from `runs/transcend/*_log.jsonl`.", ""]

    # ---------------------------------------------------------------- imitation
    imit = {n: load(n) for n in ("imitation-clean", "imitation-all", "imitation-2200", "imitation")}
    imit = {n: r for n, r in imit.items() if r}
    if imit:
        fig, axes = plt.subplots(1, 3, figsize=(16, 4.4))
        for name, rows in imit.items():
            st = [r["step"] for r in rows]
            line(axes[0], st, [r["val_policy"] for r in rows], name)
            line(axes[1], st, [r["puzzle_elo"] for r in rows], name,
                 band=([r["elo_ci"][0] for r in rows], [r["elo_ci"][1] for r in rows]), fmt="{:.0f}")
            line(axes[2], st, [100 * r["solve_2400"] for r in rows], name, fmt="{:.1f}%")
        style(axes[0], "Held-out policy loss (lower is better)", "cross-entropy", "training step")
        style(axes[1], "Puzzle Elo (95% CI)", "puzzle rating", "training step")
        style(axes[2], "2400 puzzles solved (ladder, ~300)", "% solved", "training step")
        axes[0].legend(frameon=False, fontsize=9)
        fig.suptitle("Imitation of 1000-1300 rated games", x=0.01, ha="left", fontsize=12, color=INK)
        fig.tight_layout()
        fig.savefig(OUT / "imitation.png", dpi=130, facecolor=SURFACE)
        plt.close(fig)
        md += ["## imitation", "", "| run | last step | held-out loss | puzzle Elo (95% CI) | 1100 solved | 2400 solved |",
               "| --- | --: | --: | --- | --: | --: |"]
        for name, rows in imit.items():
            r = rows[-1]
            md.append(f"| {RUNS[name][0]} (`{name}`) | {r['step']} | {r['val_policy']:.3f} | "
                      f"{r['puzzle_elo']:.0f} ({r['elo_ci'][0]:.0f}-{r['elo_ci'][1]:.0f}) | "
                      f"{100 * r['solve_1100']:.1f}% | {100 * r['solve_2400']:.2f}% |")
        md.append("")

    # ---------------------------------------------------------------- RL
    rl = {n: load(n) for n in ("rl-clean", "rl-all", "rl-2200", "rl-clean-hard", "rl-all-hard", "rl-2200-hard")}
    rl = {n: r for n, r in rl.items() if r}
    if rl:
        fig, axes = plt.subplots(1, 4, figsize=(20, 4.4))
        for name, rows in rl.items():
            st = [r["step"] for r in rows]
            line(axes[0], st, [r["puzzle_elo"] for r in rows], name,
                 band=([r["elo_ci"][0] for r in rows], [r["elo_ci"][1] for r in rows]), fmt="{:.0f}")
            for ax, key, field in ((axes[1], "control", "solved"), (axes[2], "test", "solved"), (axes[3], "test", "first")):
                k = [r[key][field] for r in rows]
                n = [r[key]["n"] for r in rows]
                ci = [wilson(a, b) for a, b in zip(k, n)]
                line(ax, st, [100 * a / b for a, b in zip(k, n)], name,
                     band=([100 * c[0] for c in ci], [100 * c[1] for c in ci]), fmt="{:.1f}%")
        style(axes[0], "Puzzle Elo (95% CI)", "puzzle rating", "RL step")
        style(axes[1], "1100 control: solved", "% solved", "RL step")
        style(axes[2], "2400 test: solved", "% solved", "RL step")
        style(axes[3], "2400 test: first move right", "% right", "RL step")
        axes[0].legend(frameon=False, fontsize=9)
        fig.suptitle("RL on puzzles (900-1200 unless marked hard): 1100 control and 2400 test, 2000 puzzles each",
                     x=0.01, ha="left", fontsize=12, color=INK)
        fig.tight_layout()
        fig.savefig(OUT / "rl.png", dpi=130, facecolor=SURFACE)
        plt.close(fig)
        md += ["## RL on 900-1200 puzzles", "",
               "| run | metric | step 0 | latest | change | 95% CI at latest |", "| --- | --- | --: | --: | --: | --- |"]
        for name, rows in rl.items():
            a, b = rows[0], rows[-1]
            md.append(f"| {RUNS[name][0]} | puzzle Elo | {a['puzzle_elo']:.0f} | {b['puzzle_elo']:.0f} (step {b['step']}) "
                      f"| {b['puzzle_elo'] - a['puzzle_elo']:+.0f} | {b['elo_ci'][0]:.0f}-{b['elo_ci'][1]:.0f} |")
            for key, field, label in (("control", "solved", "1100 solved"), ("test", "solved", "2400 solved"),
                                      ("test", "first", "2400 first move")):
                pa, pb = a[key][field] / a[key]["n"], b[key][field] / b[key]["n"]
                lo, hi = wilson(b[key][field], b[key]["n"])
                md.append(f"| {RUNS[name][0]} | {label} | {100 * pa:.1f}% | {100 * pb:.1f}% | "
                          f"{100 * (pb - pa):+.1f} pts | {100 * lo:.1f}-{100 * hi:.1f}% |")
        md += ["", "The rl-clean log up to step 2250 was rebuilt from the console output; its first-move counts "
               "come from the printed percentages (to 0.1%).", ""]

    # ---------------------------------------------------------------- RL by stratum
    strat = {n: r for n, r in rl.items() if "strata" in r[0]}
    if strat:
        fig, axes = plt.subplots(1, 2, figsize=(15, 4.8))
        for name, rows in strat.items():
            _, color, _ = RUNS[name]
            for row, ls, when in ((rows[0], "--", "step 0"), (rows[-1], "-", f"step {rows[-1]['step']}")):
                levels = sorted(row["strata"], key=int)
                xs = [int(s) for s in levels]
                for ax, field in ((axes[0], "solved"), (axes[1], "first")):
                    k = [row["strata"][s][field] for s in levels]
                    n = [row["strata"][s]["n"] for s in levels]
                    ci = [wilson(a, b) for a, b in zip(k, n)]
                    ax.plot(xs, [100 * a / b for a, b in zip(k, n)], color=color, ls=ls, lw=2,
                            marker=HARD_MARKER if name.endswith("-hard") else "o", ms=4,
                            label=f"{RUNS[name][0]}, {when}")
                    ax.fill_between(xs, [100 * c[0] for c in ci], [100 * c[1] for c in ci], color=color, alpha=0.12, lw=0)
        xs = sorted(int(s) for s in next(iter(strat.values()))[0]["strata"])
        axes[0].plot(xs, [100 / (1 + 10 ** ((x - 1100) / 400)) for x in xs], color=MUTED, ls=":", lw=1.5,
                     label="1100 player (Elo formula)")
        axes[0].set_yscale("log")                   # solve rates span 70% to 0.1%
        pools = sorted({tuple(r[0].get("pool", [900, 1200])) for r in strat.values()})
        for ax in axes:
            for lo_, hi_ in pools:                  # each reward range used by a plotted run
                ax.axvspan(lo_, hi_, color=GRID, alpha=0.6, lw=0)
                ax.annotate(f"reward {lo_}-{hi_}", ((lo_ + hi_) / 2, 0.98), xycoords=("data", "axes fraction"),
                            ha="center", va="top", fontsize=8, color=MUTED)
        style(axes[0], "Solved, by puzzle rating (log scale)", "% solved", "puzzle rating (stratum)")
        style(axes[1], "First move right, by puzzle rating", "% right", "puzzle rating (stratum)")
        axes[0].legend(frameon=False, fontsize=8)
        fig.suptitle("Where RL's gains land: every stratum, before (dashed) and after (solid), 95% CI",
                     x=0.01, ha="left", fontsize=12, color=INK)
        fig.tight_layout()
        fig.savefig(OUT / "rl_strata.png", dpi=130, facecolor=SURFACE)
        plt.close(fig)
        md += ["## RL by stratum", "", "| run | stratum | solved, step 0 | solved, latest | first move, step 0 | first move, latest |",
               "| --- | --: | --: | --: | --: | --: |"]
        for name, rows in strat.items():
            a, b = rows[0]["strata"], rows[-1]["strata"]
            for s in sorted(a, key=int):
                f = lambda d, k: f"{100 * d[s][k] / d[s]['n']:.1f}%"
                md.append(f"| {RUNS[name][0]} | {s} | {f(a, 'solved')} | {f(b, 'solved')} | {f(a, 'first')} | {f(b, 'first')} |")
        md += ["", "![rl by stratum](rl_strata.png)", ""]

    for p in (paths.RUNS / "transcend").glob("*_log.jsonl"):
        shutil.copy(p, OUT / "logs" / p.name)
    md += ["## figures", "", "![imitation](imitation.png)", "", "![rl](rl.png)", ""]
    (OUT / "summary.md").write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {OUT}: " + ", ".join(sorted(p.name for p in OUT.iterdir())))


if __name__ == "__main__":
    main()
