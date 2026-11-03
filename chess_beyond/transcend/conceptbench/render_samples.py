"""20 random positives and 20 negatives per concept, as boards, for a human spot-check.

    python transcend/conceptbench/render_samples.py --concepts isolated_queens_pawn,carlsbad          # text boards
    python transcend/conceptbench/render_samples.py --family structures --html results/transcend/conceptbench/spotcheck.html

Text goes to stdout; --html writes one page with each concept's definition and boards. Each board shows its game's ply
and side to move. Negatives are unmatched draws from all labelled negatives (matching is build_dataset.py's job).
"""

import argparse
import html
import json
import sys
from pathlib import Path

import chess
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bench import COUNTS, LABELS, POSITIONS

GLYPH = dict(zip("PNBRQKpnbrqk", "♙♘♗♖♕♔♟♞♝♜♛♚"))
CSS = """
:root { --bg: #fff; --fg: #1a1a1a; --mut: #666; --light: #eeeed2; --dark: #9db67c; --line: #ddd; color-scheme: light dark; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg: #161616; --fg: #eee; --mut: #aaa; --line: #333; } }
:root[data-theme="dark"] { --bg: #161616; --fg: #eee; --mut: #aaa; --line: #333; }
body { background: var(--bg); color: var(--fg); font: 15px/1.5 system-ui, sans-serif; margin: 0 auto; max-width: 1180px; padding: 16px; }
h2 { margin: 36px 0 4px; font-size: 20px; border-top: 1px solid var(--line); padding-top: 20px; }
h3 { font-size: 14px; margin: 14px 0 6px; color: var(--mut); font-weight: 600; }
p.def { margin: 0 0 8px; }
nav a { margin-right: 12px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, 136px); gap: 10px; }
.bd { display: grid; grid-template-columns: repeat(8, 17px); grid-auto-rows: 17px; width: 136px; }
.bd span { display: block; text-align: center; font-size: 15px; line-height: 17px; color: #111; font-family: "Segoe UI Symbol", "DejaVu Sans", sans-serif; }
.l { background: var(--light); } .d { background: var(--dark); }
.cap { font-size: 11px; color: var(--mut); margin-top: 2px; }
"""


def board_html(fen):
    b = chess.Board(fen)
    cells = []
    for r in range(7, -1, -1):
        for f in range(8):
            p = b.piece_at(chess.square(f, r))
            cells.append(f'<span class="{"l" if (r + f) % 2 else "d"}">{GLYPH[p.symbol()] if p else ""}</span>')
    return f'<div class="bd">{"".join(cells)}</div>'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--concepts", default="", help="comma-separated")
    ap.add_argument("--family", default="")
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--html")
    a = ap.parse_args()
    import pandas as pd
    info = json.loads(COUNTS.read_text(encoding="utf-8"))["concepts"]
    names = [c for c in a.concepts.split(",") if c] + [k for k, c in info.items() if a.family and c["family"] == a.family]
    pos = pd.read_parquet(POSITIONS, columns=["fen", "ply", "side", "phase"])
    lab = pd.read_parquet(LABELS, columns=names)
    rng = np.random.default_rng(a.seed)
    sections = []
    for k in names:
        y = lab[k].to_numpy()
        section = [f'<h2 id="{k}">{html.escape(k)}</h2><p class="def">{html.escape(info[k]["definition"])}</p>',
                   f'<p class="cap">{info[k]["fit_pos"] + info[k]["test_pos"]} positives, {info[k]["fit_neg"] + info[k]["test_neg"]} negatives</p>']
        print(f"\n===== {k}: {info[k]['definition']}")
        for val, title in ((1, "positives"), (0, "negatives")):
            idx = np.flatnonzero(y == val)
            idx = rng.choice(idx, min(a.n, len(idx)), replace=False)
            cards = []
            print(f"\n--- {title}")
            for i in idx:
                r = pos.iloc[int(i)]
                print(f"\n{r['fen']}   ply {r['ply']}, {r['side']} to move, {r['phase']}\n{chess.Board(r['fen'])}")
                cards.append(f'<div>{board_html(r["fen"])}<div class="cap">ply {r["ply"]}, {r["side"][0]} to move, {r["phase"]}</div></div>')
            section.append(f'<h3>{title}</h3><div class="grid">{"".join(cards)}</div>')
        sections.append("".join(section))
    if a.html:
        nav = "".join(f'<a href="#{k}">{k}</a>' for k in names)
        Path(a.html).write_text(f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                                f'<title>Concept Spot-check</title><style>{CSS}</style><h1>Concept spot-check</h1>'
                                f'<p>{a.n} random positives and {a.n} random negatives per concept, seed {a.seed}. White at the bottom.</p>'
                                f'<nav>{nav}</nav>{"".join(sections)}</html>', encoding="utf-8")
        print(f"\nwrote {a.html}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
