"""Character-level PGN data for pgn_model.py, from band PGN files.

    python transcend/make_pgn_data.py --pgn data/lichess/bands/2025-06-train/1000-1300.pgn --out data/transcend/pgn-all

Each game becomes ';1.e4 e5 2.Nf3 ... <result>' (pgn_model.movetext): the moves as
SAN, with clocks, evaluations, annotations and move numbers like '1...' removed.
The games are concatenated into one uint8 array of character ids:

  <out>/tokens.bin   all games, back to back (each starts with ';')
  <out>/starts.npy   offset of every game in tokens.bin
  <out>/meta.json    counts, and the first --val-games games held out for validation

The SAN comes straight from the PGN (Lichess writes standard SAN), so no game is
replayed; a game with a character outside the vocabulary is skipped.
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # chess_beyond/
from pgn_model import STOI, movetext

COMMENT = re.compile(r"\{[^}]*\}")
NUMBER = re.compile(r"\d+\.(\.\.)?")
RESULTS = {"1-0", "0-1", "1/2-1/2"}

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--pgn", nargs="+", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--val-games", type=int, default=5000)
args = ap.parse_args()


def games(path):
    """(result, movetext) per game."""
    head, moves, in_moves = {}, [], False
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("["):
                if in_moves:
                    yield head.get("Result"), " ".join(moves)
                    head, moves, in_moves = {}, [], False
                key, _, val = line[1:].partition(" ")
                head[key] = val.strip().rstrip("]").strip('"')
            elif line.strip():
                in_moves = True
                moves.append(line.strip())
    if in_moves:
        yield head.get("Result"), " ".join(moves)


def to_text(result, text):
    sans = []
    for tok in NUMBER.sub(" ", COMMENT.sub(" ", text)).split():
        tok = tok.rstrip("?!")
        if not tok or tok in RESULTS or tok == "*":
            continue
        sans.append(tok)
    if not sans or result not in RESULTS:
        return None
    return movetext(sans, result)


out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)
t0 = time.time()
buf, starts, pos, kept, skipped = bytearray(), [], 0, 0, 0
lut = np.full(256, 255, dtype=np.uint8)
for c, i in STOI.items():
    lut[ord(c)] = i
for path in args.pgn:
    for result, text in games(path):
        g = to_text(result, text)
        if g is None or any(ord(ch) > 255 or lut[ord(ch)] == 255 for ch in g):
            skipped += 1
            continue
        starts.append(pos)
        enc = lut[np.frombuffer(g.encode("ascii"), dtype=np.uint8)]
        buf += enc.tobytes()
        pos += len(enc)
        kept += 1
        if kept % 100000 == 0:
            print(f"\r{kept} games, {pos / 1e6:.0f}M characters, {time.time() - t0:.0f}s", end="", flush=True)
(out / "tokens.bin").write_bytes(bytes(buf))
np.save(out / "starts.npy", np.array(starts, dtype=np.int64))
meta = dict(games=kept, skipped=skipped, characters=pos, val_games=args.val_games, sources=args.pgn,
            mean_chars=pos / max(kept, 1))
(out / "meta.json").write_text(json.dumps(meta, indent=1))
print(f"\n{kept} games ({skipped} skipped), {pos / 1e6:.1f}M characters "
      f"(mean {pos / max(kept, 1):.0f} per game) -> {out}")
