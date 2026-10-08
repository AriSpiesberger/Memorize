"""Imitation data from rating-band games: every position, encoded for the network.

    python transcend/make_data.py --pgn data/lichess/bands/2025-06-train/1000-1300.pgn

Each position becomes (board tokens, the move the player made, the game result
for the mover), stored as int8/int16 arrays in shards of --shard-games games:
data/transcend/imitation/shard_00000.npz ...

Positions that occur in any puzzle under data/lichess/puzzles/strata/ (the test
and control sets, every position along each solution) are dropped, so the model
can't have seen a test position during training.
"""
import argparse
import glob
import io
import json
import multiprocessing as mp
import os
import sys
import time
from pathlib import Path

import chess
import chess.pgn
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # chess_beyond/: common.py, paths.py
import paths
from common import MOVE_TO_ID, encode_board, move_to_model_frame

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--pgn", nargs="+", required=True, help="band PGN file(s) from rating_bands/collect_games.py")
ap.add_argument("--out", default=str(paths.DATA / "transcend" / "imitation"))
ap.add_argument("--skip-plies", type=int, default=0, help="drop the first N plies of each game")
ap.add_argument("--max-games", type=int, default=0, help="0 = all games in the files")
ap.add_argument("--shard-games", type=int, default=20000)
ap.add_argument("--exclude", default=str(paths.LICHESS / "puzzles" / "strata"), help="folder of puzzle strata to keep out")
ap.add_argument("--workers", type=int, default=24)
args = ap.parse_args()

RESULT = {"1-0": 1, "0-1": -1, "1/2-1/2": 0}


def key(board):
    return " ".join(board.fen().split()[:4])


def puzzle_positions(folder):
    keys = set()
    for p in glob.glob(os.path.join(folder, "*.jsonl")):
        for line in open(p):
            pz = json.loads(line)
            b = chess.Board(pz["fen"])
            for mv in pz["moves"]:
                b.push_uci(mv)
                keys.add(key(b))
    return keys


EXCLUDE = set()


def init(excl):
    global EXCLUDE
    EXCLUDE = excl


def encode_games(texts):
    xs, ys, vs, dropped = [], [], [], 0
    for t in texts:
        g = chess.pgn.read_game(io.StringIO(t))
        if g is None:
            continue
        res = RESULT.get(g.headers.get("Result"))
        if res is None:
            continue
        b = g.board()
        for i, mv in enumerate(g.mainline_moves()):
            if i >= args.skip_plies:
                if key(b) in EXCLUDE:
                    dropped += 1
                else:
                    xs.append(encode_board(b))
                    ys.append(MOVE_TO_ID[move_to_model_frame(mv, b.turn)])
                    vs.append(res if b.turn == chess.WHITE else -res)
            b.push(mv)
    return (np.array(xs, dtype=np.int8).reshape(-1, 70), np.array(ys, dtype=np.int16),
            np.array(vs, dtype=np.int8), dropped)


def game_texts():
    n = 0
    for path in args.pgn:
        buf = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("[Event ") and buf:
                    yield "".join(buf)
                    n += 1
                    buf = []
                    if args.max_games and n >= args.max_games:
                        return
                buf.append(line)
        if buf:
            yield "".join(buf)
            n += 1


def chunks(it, size):
    c = []
    for t in it:
        c.append(t)
        if len(c) == size:
            yield c
            c = []
    if c:
        yield c


if __name__ == "__main__":
    os.makedirs(args.out, exist_ok=True)
    t0 = time.time()
    excl = puzzle_positions(args.exclude) if os.path.isdir(args.exclude) else set()
    print(f"excluding {len(excl)} puzzle positions ({time.time() - t0:.0f}s)")
    shard, games, total, dropped = 0, 0, 0, 0
    with mp.Pool(args.workers, initializer=init, initargs=(excl,)) as pool:
        for block in chunks(game_texts(), args.shard_games):
            parts = pool.map(encode_games, [block[i:i + 200] for i in range(0, len(block), 200)])
            x = np.concatenate([p[0] for p in parts]); y = np.concatenate([p[1] for p in parts])
            v = np.concatenate([p[2] for p in parts]); dropped += sum(p[3] for p in parts)
            np.savez(os.path.join(args.out, f"shard_{shard:05d}.npz"), x=x, y=y, v=v)
            shard += 1; games += len(block); total += len(y)
            print(f"\r{games} games -> {total / 1e6:.2f}M positions in {shard} shards, "
                  f"{dropped} puzzle positions dropped, {time.time() - t0:.0f}s   ", end="", flush=True)
    print(f"\ndone: {args.out}")
