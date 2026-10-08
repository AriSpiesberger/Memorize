"""Hard Lichess puzzles, and a check that weaker players can't solve them.

    python rating_bands/hard_puzzles.py                     # uses data/lichess/lichess_db_puzzle.csv.zst

Every Lichess puzzle comes from a real game and has a full solution line (each
step checked by an engine to be the only winning move) and a rating measured from
thousands of attempts by players of every level.

For puzzles in each rating bucket, Maia-2 (a model of how humans at a given rating
actually play) plays through the WHOLE solution at ratings 1000 ... 2000+:
  P(solve at rating R) = product over the solver's moves of P_Maia(correct move | R)
One correct move can be luck; a 3-move solution needs every move, so this shrinks
multiplicatively and is a much stricter test than "found the first move".

Prints, per puzzle-rating bucket, the median P(solve) at each Maia rating and the
share of puzzles that rating essentially can't solve (P < --unsolvable). Writes the
hardest puzzles, with their per-rating solve probabilities, to
data/lichess/puzzles/hard_puzzles.jsonl.

Note: Maia-2 lumps everything from 2000 up into one bucket, so it shows who CAN'T
solve a puzzle, not how far above 2000 a solver needs to be. Puzzle ratings run on
their own scale, somewhat above game ratings.
"""
import argparse
import csv
import hashlib
import io
import json
import os
import sys
from pathlib import Path

import chess
import numpy as np
import torch
import zstandard

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # chess_beyond/: paths.py
import paths

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--csv", default=str(paths.LICHESS / "lichess_db_puzzle.csv.zst"))
ap.add_argument("--buckets", default="1000,1400,1800,2200,2600,3500", help="puzzle-rating bucket edges")
ap.add_argument("--per-bucket", type=int, default=2000, help="puzzles sampled per bucket")
ap.add_argument("--min-plays", type=int, default=1000, help="only puzzles attempted at least this often")
ap.add_argument("--max-deviation", type=int, default=80, help="only puzzles whose rating is this certain")
ap.add_argument("--min-moves", type=int, default=2, help="solver moves in the solution (2 = at least a 2-move idea)")
ap.add_argument("--unsolvable", type=float, default=0.01, help="P(solve) below this counts as 'can't solve'")
ap.add_argument("--maia-type", choices=["rapid", "blitz"], default="rapid")
ap.add_argument("--seed", type=int, default=0)
args = ap.parse_args()

ELOS = [1000, 1300, 1500, 1700, 1900, 2100]            # Maia-2 buckets: <1100, 1300s, ..., >=2000
edges = [int(x) for x in args.buckets.split(",")]
buckets = list(zip(edges, edges[1:]))
bname = lambda b: f"{b[0]}-{b[1]}" if b[1] < 3500 else f"{b[0]}+"
dev = "cuda" if torch.cuda.is_available() else "cpu"


def keep_hash(pid):          # a fixed pseudo-random sample, independent of file order
    return int.from_bytes(hashlib.md5(f"{args.seed}:{pid}".encode()).digest()[:4], "big")


# ---------------------------------------------------------------- pick puzzles
cand = {b: [] for b in buckets}
with open(args.csv, "rb") as fh:
    text = io.TextIOWrapper(zstandard.ZstdDecompressor().stream_reader(fh), encoding="utf-8")
    for row in csv.DictReader(text):
        try:
            rating, dev_r, plays = int(row["Rating"]), int(row["RatingDeviation"]), int(row["NbPlays"])
        except ValueError:
            continue
        if plays < args.min_plays or dev_r > args.max_deviation:
            continue
        moves = row["Moves"].split()
        if (len(moves) - 1 + 1) // 2 < args.min_moves:          # moves[0] is the opponent's setup move
            continue
        for b in buckets:
            if b[0] <= rating < b[1]:
                cand[b].append((keep_hash(row["PuzzleId"]), row))
                break
puzzles = {b: [r for _, r in sorted(c, key=lambda t: t[0])[:args.per_bucket]] for b, c in cand.items()}
for b in buckets:
    print(f"puzzles {bname(b):>10}: {len(cand[b]):7d} qualify, using {len(puzzles[b])}")

# ---------------------------------------------------------------- solver positions and solution moves
steps = []                                     # (puzzle index, fen, solution move uci)
flat = [(b, r) for b in buckets for r in puzzles[b]]
for pi, (_, row) in enumerate(flat):
    board = chess.Board(row["FEN"])
    moves = row["Moves"].split()
    board.push_uci(moves[0])                   # the opponent's move that sets the puzzle
    for j, mv in enumerate(moves[1:]):
        if j % 2 == 0:
            steps.append((pi, board.fen(), mv))
        board.push_uci(mv)

# ---------------------------------------------------------------- Maia-2 plays each solution move
from maia2 import inference as I2
from maia2 import model as M2
from maia2.utils import mirror_move

mdl = M2.from_pretrained(type=args.maia_type, device="gpu" if dev == "cuda" else "cpu", save_root=str(paths.MAIA2))
all_moves_dict, elo_dict, _ = I2.prepare()
logp = np.zeros((len(steps), len(ELOS)), dtype=np.float64)
with torch.no_grad():
    for s in range(0, len(steps), 1024):
        chunk = steps[s:s + 1024]
        boards, legal, idx = [], [], []
        for _, fen, mv in chunk:
            b, _, _, lg = I2.preprocessing(fen, 1500, 1500, elo_dict, all_moves_dict)
            boards.append(b); legal.append(lg)
            idx.append(all_moves_dict[mv if fen.split(" ")[1] == "w" else mirror_move(mv)])
        boards, legal, idx = torch.stack(boards).to(dev), torch.stack(legal).to(dev), torch.tensor(idx, device=dev)
        for k, e in enumerate(ELOS):
            cat = torch.full((len(chunk),), I2.map_to_category(e, elo_dict), device=dev)
            logits, _, _ = mdl(boards, cat, cat)
            lp = torch.log_softmax(logits.masked_fill(legal == 0, -1e9), -1)
            logp[s:s + len(chunk), k] = lp.gather(1, idx[:, None]).squeeze(1).double().cpu().numpy()
        print(f"\rMaia-2 on solution moves {min(s + 1024, len(steps))}/{len(steps)}", end="", flush=True)
print()

solve = np.zeros((len(flat), len(ELOS)))       # log P(solve) = sum of log P(each solution move)
first = np.full((len(flat), len(ELOS)), np.nan)
for (pi, _, _), lp in zip(steps, logp):
    if np.isnan(first[pi, 0]):
        first[pi] = np.exp(lp)
    solve[pi] += lp
solve = np.exp(solve)

# ---------------------------------------------------------------- report
print(f"\nMedian P(Maia plays the whole solution) by puzzle rating, and in brackets the share of puzzles with "
      f"P < {args.unsolvable:.0%} (can't solve)")
print(f"{'puzzle rating':>14}  {'n':>5}" + "".join(f"{'Maia ' + (str(e) if e < 2100 else '2000+'):>18}" for e in ELOS))
report = {}
for b in buckets:
    m = np.array([bb == b for bb, _ in flat])
    if not m.any():
        continue
    report[bname(b)] = {}
    line = f"{bname(b):>14}  {m.sum():5d}"
    for k, e in enumerate(ELOS):
        med, cant = float(np.median(solve[m, k])), float((solve[m, k] < args.unsolvable).mean())
        report[bname(b)][e] = dict(median_solve=med, cant_solve=cant, median_first_move=float(np.median(first[m, k])))
        line += f"{med:10.3f} ({cant:4.0%})"
    print(line)

print("\nSame, first move only (one correct move can be luck):")
for b in buckets:
    m = np.array([bb == b for bb, _ in flat])
    if m.any():
        print(f"{bname(b):>14}  {m.sum():5d}" + "".join(f"{np.median(first[m, k]):10.3f}        " for k in range(len(ELOS))))

# ---------------------------------------------------------------- the hardest puzzles, verified
out_dir = paths.LICHESS / "puzzles"
out_dir.mkdir(parents=True, exist_ok=True)
top = buckets[-1]
hard = [(i, r) for i, (b, r) in enumerate(flat) if b == top]
hard.sort(key=lambda t: solve[t[0], ELOS.index(1900)])
with open(out_dir / "hard_puzzles.jsonl", "w") as f:
    for i, r in hard:
        f.write(json.dumps(dict(id=r["PuzzleId"], rating=int(r["Rating"]), plays=int(r["NbPlays"]), fen=r["FEN"],
                                moves=r["Moves"], themes=r["Themes"].split(), game=r["GameUrl"],
                                link=f"https://lichess.org/training/{r['PuzzleId']}",
                                p_solve={str(e): round(float(solve[i, k]), 5) for k, e in enumerate(ELOS)},
                                p_first_move={str(e): round(float(first[i, k]), 4) for k, e in enumerate(ELOS)})) + "\n")
json.dump(dict(args=vars(args), elos=ELOS, report=report), open(out_dir / "puzzle_report.json", "w"), indent=1)

print(f"\nHardest {bname(top)} puzzles for Maia 1900 (P(solve) at 1000 / 1500 / 1900 / 2000+):")
for i, r in hard[:8]:
    p = solve[i]
    print(f"  {r['Rating']}  {p[0]:.4f} / {p[2]:.4f} / {p[4]:.4f} / {p[5]:.4f}   "
          f"{' '.join(r['Themes'].split()[:4]):40s} https://lichess.org/training/{r['PuzzleId']}")
print(f"\nwrote {out_dir / 'hard_puzzles.jsonl'} ({len(hard)} puzzles) and puzzle_report.json")
