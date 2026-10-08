"""A stratified puzzle set: narrow, well-measured rating strata 400 points apart.

    python rating_bands/puzzle_strata.py          # -> data/lichess/puzzles/strata/<rating>.jsonl

A Lichess puzzle rating behaves like a player rating: a solver rated the same as
the puzzle solves it about half the time, and every 400 points of gap cuts the
odds by 10x (P = 1 / (1 + 10^((puzzle - solver) / 400))). So strata whose centres
are 400 apart, each only +/- --width wide and with ratings measured tightly (low
RatingDeviation, many plays), can be told apart: a solver at one stratum solves
about half of it, ~9% of the next one up and ~1% of the one after.

Writes one file per stratum (solution line, themes, rating, deviation, plays,
link) and strata_summary.json with the counts and the expected solve-rate matrix.
"""
import argparse
import csv
import hashlib
import io
import json
import sys
from pathlib import Path

import zstandard

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # chess_beyond/: paths.py
import paths

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--csv", default=str(paths.LICHESS / "lichess_db_puzzle.csv.zst"))
ap.add_argument("--centers", default="1000,1400,1800,2200,2600")
ap.add_argument("--width", type=int, default=50, help="each stratum is centre +/- width")
ap.add_argument("--max-deviation", type=int, default=75, help="only puzzles whose rating is this certain")
ap.add_argument("--min-plays", type=int, default=300)
ap.add_argument("--min-moves", type=int, default=2, help="solver moves in the solution (an idea, not one move)")
ap.add_argument("--per-stratum", type=int, default=5000)
ap.add_argument("--seed", type=int, default=0)
args = ap.parse_args()

centers = [int(c) for c in args.centers.split(",")]
found = {c: [] for c in centers}
with open(args.csv, "rb") as fh:
    for row in csv.DictReader(io.TextIOWrapper(zstandard.ZstdDecompressor().stream_reader(fh), encoding="utf-8")):
        try:
            rating, rd, plays = int(row["Rating"]), int(row["RatingDeviation"]), int(row["NbPlays"])
        except ValueError:
            continue
        if rd > args.max_deviation or plays < args.min_plays or len(row["Moves"].split()) // 2 < args.min_moves:
            continue
        for c in centers:
            if abs(rating - c) <= args.width:
                h = int.from_bytes(hashlib.md5(f"{args.seed}:{row['PuzzleId']}".encode()).digest()[:4], "big")
                found[c].append((h, row))

out = paths.LICHESS / "puzzles" / "strata"
out.mkdir(parents=True, exist_ok=True)
expected = lambda solver, puzzle: 1 / (1 + 10 ** ((puzzle - solver) / 400))
summary = dict(args=vars(args), strata={})
print(f"strata: centre +/- {args.width}, rating deviation <= {args.max_deviation}, plays >= {args.min_plays}, "
      f">= {args.min_moves} solver moves\n")
for c in centers:
    rows = [r for _, r in sorted(found[c], key=lambda t: t[0])[:args.per_stratum]]
    with open(out / f"{c}.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(dict(id=r["PuzzleId"], rating=int(r["Rating"]), deviation=int(r["RatingDeviation"]),
                                    plays=int(r["NbPlays"]), fen=r["FEN"], moves=r["Moves"].split(),
                                    themes=r["Themes"].split(), link=f"https://lichess.org/training/{r['PuzzleId']}",
                                    game=r["GameUrl"])) + "\n")
    summary["strata"][c] = dict(available=len(found[c]), kept=len(rows))
    print(f"  stratum {c}: {len(found[c]):7d} qualify, kept {len(rows)}")

print("\nExpected solve rate (rows: solver rating, columns: stratum)")
print(f"{'':>8}" + "".join(f"{c:>8}" for c in centers))
summary["expected_solve"] = {}
for s in centers:
    summary["expected_solve"][s] = {c: round(expected(s, c), 4) for c in centers}
    print(f"{s:>8}" + "".join(f"{expected(s, c):8.1%}" for c in centers))
json.dump(summary, open(out / "strata_summary.json", "w"), indent=1)
print("\nwrote", out)
