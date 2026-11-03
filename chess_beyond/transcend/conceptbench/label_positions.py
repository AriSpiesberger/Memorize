"""Every labeller over every position, and the counts table.

    python transcend/conceptbench/label_positions.py
    python transcend/conceptbench/label_positions.py --stockfish-terms tools/stockfish-11.exe     # optional family, slow

-> labels.parquet (pos_id, then a concept column: 1 positive, 0 negative, -1 no label), label_counts.json (per concept:
   family, its definition, positives and negatives by split and game phase, dropped or kept) and
   results/transcend/conceptbench/label_counts.md. A concept with fewer than --min-positives positives in fit is dropped and
   reported. Openings appear only if they could pass (the list has thousands of names).
"""

import argparse
import json
import multiprocessing as mp
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bench import COUNTS, LABELS, PHASES, POSITIONS, RESULTS, board_of
from labels import FAMILIES, openings, stockfish_terms


def label_chunk(rows):
    """[(pos_id, prompt, fen, future)] -> [(pos_id, {concept: bool or None}, openings applicable)]."""
    out = []
    for pos_id, prompt, fen, future in rows:
        b = board_of(prompt)
        if b.fen() != fen:
            raise ValueError(f"position {pos_id}: its prompt gives {b.fen()}, stored {fen}")
        game = dict(future=future.split(",") if future else [])
        got = {}
        for name, fam in FAMILIES.items():
            got.update(fam.labels(b, game))
        out.append((pos_id, got, openings.applicable(b)))
    return out


def sf_values(a, df):
    eng = stockfish_terms.Engine(a.stockfish_terms)
    vals = {k: np.full(len(df), np.nan) for k in stockfish_terms.DEFS}
    for i, fen in enumerate(df["fen"]):
        for term, (w, b) in eng.values(fen).items():
            for s, v in (("white", w), ("black", b)):
                k = f"sf_{s}_{term.lower().replace(' ', '_')}"
                if k in vals:
                    vals[k][i] = v
    eng.close()
    return stockfish_terms.labels_from_values(vals, df["split"].to_numpy() == "fit")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--min-positives", type=int, default=300)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--stockfish-terms", help="a Stockfish 8-11 binary: adds stockfish_terms.py's family")
    a = ap.parse_args()
    import pandas as pd
    t0 = time.time()
    df = pd.read_parquet(POSITIONS)
    n = len(df)
    if not np.array_equal(df["pos_id"].to_numpy(), np.arange(n)):
        sys.exit("positions.parquet: pos_id is not 0..n-1")
    rows = list(zip(df["pos_id"].tolist(), df["prompt"].tolist(), df["fen"].tolist(), df["future"].tolist()))
    chunks = [rows[i:i + 500] for i in range(0, n, 500)]
    Y, sparse_applicable = {}, np.zeros(n, bool)
    fam_of = {}
    with mp.Pool(a.workers) as pool:
        for c, part in enumerate(pool.imap_unordered(label_chunk, chunks)):
            for pos_id, got, app in part:
                sparse_applicable[pos_id] = app
                for k, v in got.items():
                    if k not in Y:
                        Y[k] = np.full(n, -1, dtype=np.int8)
                    if v is not None:
                        Y[k][pos_id] = int(v)
            if c % 40 == 0:
                print(f"  {(c + 1) * 500} of {n}, {time.time() - t0:.0f}s", flush=True)
    for name, fam in FAMILIES.items():
        if getattr(fam, "SPARSE", False):
            for k in Y:
                if k.startswith(("eco_", "line_")):
                    Y[k][sparse_applicable & (Y[k] < 1)] = 0
                    fam_of[k] = name
        else:
            for k in fam.DEFS:
                fam_of[k] = name
    if a.stockfish_terms:
        for k, y in sf_values(a, df).items():
            Y[k], fam_of[k] = y, "stockfish_terms"
    defs = {**{k: v for f in FAMILIES.values() for k, v in f.DEFS.items()}, **stockfish_terms.DEFS}
    is_fit = df["split"].to_numpy() == "fit"
    phase = df["phase"].to_numpy()
    counts = {}
    for k, y in Y.items():
        c = dict(family=fam_of[k], definition=defs.get(k) or openings.define(k),
                 fit_pos=int((is_fit & (y == 1)).sum()), fit_neg=int((is_fit & (y == 0)).sum()),
                 test_pos=int((~is_fit & (y == 1)).sum()), test_neg=int((~is_fit & (y == 0)).sum()), by_phase={})
        for p in PHASES:
            m = phase == p
            c["by_phase"][p] = dict(fit_pos=int((is_fit & m & (y == 1)).sum()), fit_neg=int((is_fit & m & (y == 0)).sum()),
                                    test_pos=int((~is_fit & m & (y == 1)).sum()), test_neg=int((~is_fit & m & (y == 0)).sum()))
        c["kept"] = c["fit_pos"] >= a.min_positives
        counts[k] = c
    keep = [k for k, c in counts.items() if c["kept"] or c["family"] != "openings"]
    import pyarrow as pa
    import pyarrow.parquet as pq
    pq.write_table(pa.table({"pos_id": np.arange(n), **{k: Y[k] for k in keep}}), LABELS, compression="zstd")
    shown = {k: counts[k] for k in keep}
    gone = sum(1 for c in counts.values() if c["family"] == "openings" and not c["kept"])
    COUNTS.write_text(json.dumps(dict(min_positives=a.min_positives, positions=n, openings_below_threshold=gone, concepts=shown,
                                      versions={k: f.VERSION for k, f in FAMILIES.items()}), indent=1), encoding="utf-8")
    write_table(shown, gone, a.min_positives, n, df)
    print(f"{len(keep)} concepts ({sum(c['kept'] for c in shown.values())} kept); {gone} opening concepts below the threshold "
          f"({(time.time() - t0) / 60:.1f} min)", flush=True)


def write_table(counts, gone, min_pos, n, df):
    RESULTS.mkdir(parents=True, exist_ok=True)
    src = Counter(df["source"])
    out = ["# Label counts", "",
           f"{n} positions from {df['game_id'].nunique()} games ({', '.join(f'{k}: {v}' for k, v in sorted(src.items()))}). "
           f"Fit {int((df['split'] == 'fit').sum())}, test {int((df['split'] == 'test').sum())}, by game.", "",
           f"Dropped: fewer than {min_pos} positives in fit (marked **dropped**), and {gone} opening concepts not listed at all "
           "for the same reason.", "",
           "Cells are positives / negatives. The phase columns are fit, then test after the semicolon.", "",
           "| family | concept | fit + | fit - | test + | test - | opening | middlegame | endgame | |", "|---|---|--:|--:|--:|--:|--:|--:|--:|---|"]
    for k, c in sorted(counts.items(), key=lambda kv: (list(FAMILIES).index(kv[1]["family"]) if kv[1]["family"] in FAMILIES else 9, kv[0])):
        ph = ["; ".join(f"{c['by_phase'][p][f'{s}_pos']}/{c['by_phase'][p][f'{s}_neg']}" for s in ("fit", "test")) for p in PHASES]
        out.append(f"| {c['family']} | {k} | {c['fit_pos']} | {c['fit_neg']} | {c['test_pos']} | {c['test_neg']} | "
                   + " | ".join(ph) + f" | {'' if c['kept'] else '**dropped**'} |")
    (RESULTS / "label_counts.md").write_text("\n".join(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
