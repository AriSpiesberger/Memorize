"""Character-level PGN data for pgn_model.py, from band PGN files.

    python transcend/make_pgn_data.py --pgn data/lichess/bands/2025-06-train/1000-1300.pgn --out data/transcend/pgn-all

Each game becomes ';1.e4 e5 2.Nf3 ... <result>' (pgn_model.movetext): the moves as
SAN, with clocks, evaluations, annotations and move numbers like '1...' removed.
The games are concatenated into one uint8 array of character ids:

  <out>/tokens.bin   all games, back to back (each starts with ';')
  <out>/starts.npy   offset of every game in tokens.bin
  <out>/meta.json    counts, and the first --val-games games held out for validation

<out>/info.npz also holds, per stored game (same order as starts.npy): white_elo, black_elo (-1 if
missing), normal (Termination "Normal": not lost on time, abandoned or by rules infraction) and
chars. --info-only writes just info.npz into an existing <out>, by the same pass over the same
files and flags, and checks every game's length against starts.npy so the two stay aligned.

--max-games N keeps a random sample of N usable games (seeded, in file order), so
datasets of different sizes can be matched game for game.

The SAN comes straight from the PGN (Lichess writes standard SAN), so no game is
replayed; a game with a character outside the vocabulary is skipped.
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # chess_beyond/
from lichess_ids import game_id
from pgn_model import STOI, movetext

COMMENT = re.compile(r"\{[^}]*\}")
NUMBER = re.compile(r"\d+\.(\.\.)?")
RESULTS = {"1-0", "0-1", "1/2-1/2"}

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--pgn", nargs="+", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--val-games", type=int, default=5000)
ap.add_argument("--max-games", type=int, default=0, help="keep a random sample of this many games (0 = all)")
ap.add_argument("--games", type=int, default=0,
                help="exactly this many TRAINING games (plus --val-games held out), taken in file order; "
                     "the files must hold enough usable games (0 = all)")
ap.add_argument("--exclude-puzzles", nargs="*", default=[],
                help="folders of puzzles (*.jsonl): games that are the source of any of these puzzles are dropped")
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--info-only", action="store_true",
                help="write only info.npz into an existing --out (same files and flags as its build), checked against starts.npy")
args = ap.parse_args()


def games(path):
    """(site, result, movetext, headers) per game."""
    head, moves, in_moves = {}, [], False
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("["):
                if in_moves:
                    yield head.get("Site", ""), head.get("Result"), " ".join(moves), head
                    head, moves, in_moves = {}, [], False
                key, _, val = line[1:].partition(" ")
                head[key] = val.strip().rstrip("]").strip('"')
            elif line.strip():
                in_moves = True
                moves.append(line.strip())
    if in_moves:
        yield head.get("Site", ""), head.get("Result"), " ".join(moves), head


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


puzzle_games = set()
if args.exclude_puzzles:
    import glob
    for p in [f for d in args.exclude_puzzles for f in glob.glob(os.path.join(d, "*.jsonl"))]:
        for line in open(p, encoding="utf-8"):
            puzzle_games.add(game_id(json.loads(line)["game"]))
    print(f"{len(puzzle_games)} puzzle source games to keep out", flush=True)


def usable():
    for path in args.pgn:
        for site, result, text, _ in games(path):
            if game_id(site) in puzzle_games:
                continue
            g = to_text(result, text)
            if g is not None and all(ord(ch) < 256 and lut[ord(ch)] != 255 for ch in g):
                yield g


lut = np.full(256, 255, dtype=np.uint8)
for c, i in STOI.items():
    lut[ord(c)] = i
keep = None
if args.max_games:
    total = sum(1 for _ in usable())                 # first pass: how many usable games there are
    if total < args.max_games:
        sys.exit(f"only {total} usable games, fewer than --max-games {args.max_games}")
    rng = np.random.default_rng(args.seed)
    keep = np.zeros(total, dtype=bool)
    keep[rng.choice(total, args.max_games, replace=False)] = True
    print(f"{total} usable games; keeping a random {args.max_games}", flush=True)

out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)
t0 = time.time()
buf, starts, pos, kept, skipped, puzzle_dropped = bytearray(), [], 0, 0, 0, 0
info = dict(white_elo=[], black_elo=[], normal=[], chars=[])


def elo(head, key):
    v = head.get(key, "")
    return int(v) if v.isdigit() else -1


n_seen = 0
target = args.games + args.val_games if args.games else 0
for path in args.pgn:
    if target and kept >= target:
        break
    for site, result, text, head in games(path):
        if game_id(site) in puzzle_games:
            puzzle_dropped += 1
            continue
        g = to_text(result, text)
        if g is None or any(ord(ch) > 255 or lut[ord(ch)] == 255 for ch in g):
            skipped += 1
            continue
        n_seen += 1
        if keep is not None and not keep[n_seen - 1]:
            continue
        starts.append(pos)
        info["white_elo"].append(elo(head, "WhiteElo"))
        info["black_elo"].append(elo(head, "BlackElo"))
        info["normal"].append(head.get("Termination") == "Normal")
        info["chars"].append(len(g))
        if not args.info_only:
            buf += lut[np.frombuffer(g.encode("ascii"), dtype=np.uint8)].tobytes()
        pos += len(g)
        kept += 1
        if kept % 100000 == 0:
            print(f"\r{kept} games, {pos / 1e6:.0f}M characters, {time.time() - t0:.0f}s", end="", flush=True)
        if target and kept >= target:
            break
if target and kept < target:
    sys.exit(f"only {kept} usable games in {args.pgn}, fewer than --games {args.games} + --val-games {args.val_games}")
info = dict(white_elo=np.array(info["white_elo"], dtype=np.int16), black_elo=np.array(info["black_elo"], dtype=np.int16),
            normal=np.array(info["normal"], dtype=bool), chars=np.array(info["chars"], dtype=np.int32))
if args.info_only:
    built = np.load(out / "starts.npy")
    lengths = np.diff(np.append(built, json.loads((out / "meta.json").read_text())["characters"]))
    if len(built) != kept or not np.array_equal(lengths, info["chars"]):
        sys.exit(f"{kept} games here but {len(built)} in {out}, or their lengths differ: not the same build; "
                 f"info.npz not written")
    np.savez(out / "info.npz", **info)
    print(f"\n{kept} games checked against {out}/starts.npy; wrote info.npz "
          f"({info['normal'].mean():.1%} normal terminations)")
    sys.exit(0)
np.savez(out / "info.npz", **info)
(out / "tokens.bin").write_bytes(bytes(buf))
np.save(out / "starts.npy", np.array(starts, dtype=np.int64))
meta = dict(games=kept, train_games=kept - args.val_games, skipped=skipped, puzzle_source_games_dropped=puzzle_dropped,
            exclude_puzzles=args.exclude_puzzles, max_games=args.max_games, seed=args.seed, characters=pos, val_games=args.val_games, sources=args.pgn,
            mean_chars=pos / max(kept, 1))
(out / "meta.json").write_text(json.dumps(meta, indent=1))
print(f"\n{kept} games ({skipped} skipped, {puzzle_dropped} dropped as puzzle source games), {pos / 1e6:.1f}M characters "
      f"(mean {pos / max(kept, 1):.0f} per game) -> {out}")
