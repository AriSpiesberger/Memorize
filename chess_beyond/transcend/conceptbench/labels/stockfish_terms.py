"""Optional, off by default (label_positions.py --stockfish-terms <binary>): Stockfish's classical evaluation terms, per
side, labelled as the top against the bottom 30% of positions.

Needs a Stockfish 8-11 binary: its `eval` command prints the classical table per term and side, and later versions do
not. The score for a term is the mean of its middlegame and endgame numbers. The cut points come from the fit split, so
this family is not a function of one board alone: values(), then labels_from_values().
"""

import subprocess

import numpy as np

VERSION = 1
TOP_SHARE = 0.3
TERMS = ("Mobility", "King safety", "Threats", "Passed", "Space", "Knights", "Bishops", "Rooks", "Queens", "Pawns")
DEFS = {f"sf_{s}_{t.lower().replace(' ', '_')}": f"Stockfish 8-11 eval term {t} for {s}: top {TOP_SHARE:.0%} of positions "
        f"against bottom {TOP_SHARE:.0%}; cut points from the fit split"
        for s in ("white", "black") for t in TERMS}


def parse_eval(text):
    """A Stockfish 8-11 `eval` table -> {term: (white, black)}, each the mean of its MG and EG. Terms with no per-side
    numbers (Material, Imbalance: '---') are left out."""
    out = {}
    for line in text.splitlines():
        cells = line.split("|")
        if len(cells) != 4:
            continue
        term = cells[0].strip()
        try:
            wm, we = (float(x) for x in cells[1].split())
            bm, be = (float(x) for x in cells[2].split())
        except ValueError:
            continue
        out[term.replace("Passed pawns", "Passed")] = ((wm + we) / 2, (bm + be) / 2)
    return out


class Engine:
    def __init__(self, path):
        self.p = subprocess.Popen([path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)

    def values(self, fen):
        self.p.stdin.write(f"position fen {fen}\neval\nisready\n")
        self.p.stdin.flush()
        lines = []
        for line in self.p.stdout:
            if line.startswith("readyok"):
                break
            lines.append(line)
        return parse_eval("".join(lines))

    def close(self):
        self.p.kill()


def labels_from_values(values, is_fit):
    """values: {concept: per-position numbers}; is_fit: the fit rows -> {concept: int8 labels, 1 / 0 / -1}."""
    out = {}
    for k, v in values.items():
        lo, hi = np.nanquantile(v[is_fit], [TOP_SHARE, 1 - TOP_SHARE])
        y = np.full(len(v), -1, dtype=np.int8)
        y[v <= lo], y[v >= hi] = 0, 1
        out[k] = y
    return out
