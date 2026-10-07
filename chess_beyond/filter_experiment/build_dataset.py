"""Annotate positions from mid-rated Lichess games with Stockfish.

  python filter_experiment/build_dataset.py --pgn data/lichess/2015-01.pgn.zst \
      --out data/filter/positions.jsonl \
      --min-elo 1100 --max-elo 1600 --games 200000 --workers 32

For each sampled position it records:
  fen, played (real UCI), m_played (model-frame UCI), result (for the mover:
  1 win, 0 draw, -1 loss), game_id, mover_elo,
  deep_scores   {model-frame uci: centipawns}  for the top moves (deep search;
                every legal move with --multipv 0)
  best_set      model-frame moves within --margin of the deep best
  shallow_best_set  same, from a search at --shallow-depth (the weak judge)
  depth_to_find shallowest depth at which the engine's top move is already in
                best_set (max_find_depth + 1 if never found)
  label_depth   depth of the search behind best_set: --easy-depth if the position
                is clearly easy (see annotate), else --deep-depth

Order matters: each search starts with a cleared hash (ucinewgame), and the
shallow and depth-to-find passes run BEFORE the deep pass, so deep results
cannot leak into the shallow ones.
"""
import argparse
import io
import json
import multiprocessing as mp
import random
import sys

import chess
import chess.engine
import chess.pgn

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # chess_beyond/: common.py, paths.py, search.py
import paths
from common import move_to_model_frame

ap = argparse.ArgumentParser()
ap.add_argument("--pgn", required=True, help=".pgn or .pgn.zst")
ap.add_argument("--stockfish", default=None, help="default: tools/stockfish/")
ap.add_argument("--out", required=True)
ap.add_argument("--min-elo", type=int, default=1100)
ap.add_argument("--max-elo", type=int, default=1600)
ap.add_argument("--min-base-seconds", type=int, default=180, help="skip bullet games")
ap.add_argument("--games", type=int, default=50000, help="games to use")
ap.add_argument("--positions-per-game", type=int, default=4)
ap.add_argument("--skip-plies", type=int, default=10, help="skip the opening")
ap.add_argument("--deep-depth", type=int, default=16)
ap.add_argument("--shallow-depth", type=int, default=4)
ap.add_argument("--max-find-depth", type=int, default=14)
ap.add_argument("--multipv", type=int, default=8,
                help="deep search scores this many top moves, doubling while all of them are within --margin "
                "(0 = every legal move, the original, ~6x slower)")
ap.add_argument("--settle-depth", type=int, default=4,
                help="positions whose deep top move already appears by this depth are easy and get best-set "
                "labels from a cheaper --easy-depth search (0 = full deep search for every position)")
ap.add_argument("--easy-depth", type=int, default=12, help="label depth for settled (easy) positions")
ap.add_argument("--margin", type=int, default=50, help="centipawns")
ap.add_argument("--workers", type=int, default=8)
ap.add_argument("--hash-mb", type=int, default=64)
ap.add_argument("--seed", type=int, default=0)
args = ap.parse_args()
args.stockfish = args.stockfish or paths.stockfish()

MATE = 100_000


def score_cp(info, turn):
    return info["score"].pov(turn).score(mate_score=MATE)


# ----------------------------------------------------------------- worker
ENGINE = None


def init_worker(path, hash_mb):
    global ENGINE
    ENGINE = chess.engine.SimpleEngine.popen_uci(path)
    ENGINE.configure({"Threads": 1, "Hash": hash_mb})


def all_move_scores(board, depth, k=0):
    """Scores at a fixed depth, model-frame keys: every legal move, or (k > 0)
    the top k, doubling k until the weakest line falls outside --margin, so the
    best set is complete."""
    n = board.legal_moves.count()
    k = n if k <= 0 else min(k, n)
    while True:
        infos = ENGINE.analyse(board, chess.engine.Limit(depth=depth), multipv=k, game=object())
        out = {}
        for info in infos:
            if "pv" in info and info["pv"]:
                out[move_to_model_frame(info["pv"][0], board.turn)] = score_cp(info, board.turn)
        if k >= n or min(out.values()) < max(out.values()) - args.margin:
            return out
        k = min(2 * k, n)


def within_margin(scores, margin):
    best = max(scores.values())
    return sorted(m for m, s in scores.items() if s >= best - margin)


def top_move_by_depth(board, max_depth):
    """The engine's top move at each completed depth of ONE search
    (Stockfish deepens iteratively, so this is what a depth-d search picks)."""
    top = {}
    with ENGINE.analysis(board, chess.engine.Limit(depth=max_depth), game=object()) as an:
        for info in an:
            if info.get("pv") and "depth" in info and info.get("multipv", 1) == 1:
                top[info["depth"]] = move_to_model_frame(info["pv"][0], board.turn)
    return top


def annotate(task):
    """Tiered: one single-line search to --deep-depth gives the top move at every
    depth. If its final move already appears by --settle-depth the position is
    easy, and its best set (the alternatives) comes from a cheaper --easy-depth
    search; otherwise from the full --deep-depth search."""
    try:
        board = chess.Board(task["fen"])
        shallow = all_move_scores(board, args.shallow_depth)
        top = top_move_by_depth(board, max(args.deep_depth, args.max_find_depth))
        final = top[max(top)]
        # The deep search's own top move is in the best set, so finding it by
        # --settle-depth makes the position easy without any further search.
        early = min(d for d in top if top[d] == final)
        easy = 0 < early <= args.settle_depth
        label_depth = args.easy_depth if easy else args.deep_depth
        deep = all_move_scores(board, label_depth, args.multipv)
        if not deep:
            return None
        best_set = within_margin(deep, args.margin)
        d_find = args.max_find_depth + 1
        for d in sorted(top):
            if d <= args.max_find_depth and top[d] in best_set:
                d_find = d
                break
        if easy:
            d_find = min(d_find, early)
        task.update(deep_scores=deep, best_set=best_set,
                    shallow_best_set=within_margin(shallow, args.margin),
                    depth_to_find=d_find, label_depth=label_depth,
                    played_in_best=task["m_played"] in best_set)
        return task
    except Exception as e:                       # keep long runs alive
        print("annotate error:", e, file=sys.stderr)
        return None


# ----------------------------------------------------------------- reading games
def open_pgn(path):
    if path.endswith(".zst"):
        import zstandard
        fh = open(path, "rb")
        return io.TextIOWrapper(zstandard.ZstdDecompressor().stream_reader(fh), encoding="utf-8")
    return open(path, encoding="utf-8")


def base_seconds(tc):
    try:
        return int(tc.split("+")[0])
    except Exception:
        return 0


def tasks_from_games():
    rng = random.Random(args.seed)
    pgn = open_pgn(args.pgn)
    used = 0
    while used < args.games:
        game = chess.pgn.read_game(pgn)
        if game is None:
            break
        h = game.headers
        try:
            we, be = int(h.get("WhiteElo", 0)), int(h.get("BlackElo", 0))
        except ValueError:
            continue
        if not (args.min_elo <= we <= args.max_elo and args.min_elo <= be <= args.max_elo):
            continue
        if base_seconds(h.get("TimeControl", "-")) < args.min_base_seconds:
            continue
        res = {"1-0": 1, "0-1": -1, "1/2-1/2": 0}.get(h.get("Result"))
        if res is None:
            continue
        moves = list(game.mainline_moves())
        plies = list(range(args.skip_plies, len(moves)))
        if not plies:
            continue
        used += 1
        gid = h.get("Site", f"game{used}")
        chosen = set(rng.sample(plies, min(args.positions_per_game, len(plies))))
        board = game.board()
        for i, mv in enumerate(moves):
            if i in chosen and board.legal_moves.count() > 1:
                yield {"game_id": gid, "ply": i, "fen": board.fen(),
                       "played": mv.uci(), "m_played": move_to_model_frame(mv, board.turn),
                       "result": res if board.turn == chess.WHITE else -res,
                       "mover_elo": we if board.turn == chess.WHITE else be}
            board.push(mv)


if __name__ == "__main__":
    import time
    expected = args.games * args.positions_per_game     # upper bound: short games give fewer
    t0, n_out = time.time(), 0
    with mp.Pool(args.workers, initializer=init_worker, initargs=(args.stockfish, args.hash_mb)) as pool, \
            open(args.out, "w") as f:
        for r in pool.imap_unordered(annotate, tasks_from_games(), chunksize=4):
            if r is not None:
                f.write(json.dumps(r) + "\n")
                n_out += 1
                if n_out % 50 == 0:
                    f.flush()                   # a stopped run keeps what it has
                    rate = n_out / (time.time() - t0)
                    eta = (expected - n_out) / rate / 60
                    print(f"\r{n_out}/{expected} positions  {rate:.1f}/s  ~{eta:.0f} min left   ",
                          end="", flush=True)
    print()
    print("wrote", n_out, "positions to", args.out)
