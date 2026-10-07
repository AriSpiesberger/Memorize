"""Label positions from rating-band games: did the player find a best move, and
what makes that move hard to find?

    python label_bands.py --bands ../../data/lichess/bands/2025-06 --per-band 20000 --workers 30

For each band PGN (from collect_games.py) it samples --per-game positions per
game and runs two engine searches per position:
  * one 2-line search to --depth: the best move, the runner-up's score (is it an
    "only move"?) and the engine's top move at every depth (depth_to_find)
  * if the player chose something else, one search of just the played move, to
    see whether it was also within --margin of the best
Output: <bands>/labels/<band>.jsonl, one row per position:
  band, elo (mover), opp_elo, clock (mover's seconds left), fen, played,
  best, best_cp, second_cp, gap_cp, played_cp, found (played within margin),
  depth_to_find, and features of the best move: capture, check, quiet,
  retreat, piece, promotion, gives_material, n_legal, material (phase).
"""
import argparse
import glob
import json
import multiprocessing as mp
import os
import random
import re
import sys
import time

import chess
import chess.engine
import chess.pgn

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--bands", required=True, help="folder of <band>.pgn files from collect_games.py")
ap.add_argument("--stockfish", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools",
                                                    "stockfish", "stockfish-windows-x86-64-universal.exe"))
ap.add_argument("--per-band", type=int, default=20000, help="positions per band")
ap.add_argument("--per-game", type=int, default=4)
ap.add_argument("--skip-plies", type=int, default=10, help="skip the opening")
ap.add_argument("--min-clock", type=int, default=30, help="skip moves made with less than this many seconds left")
ap.add_argument("--depth", type=int, default=16)
ap.add_argument("--margin", type=int, default=50, help="centipawns: 'found' means within this of the best")
ap.add_argument("--workers", type=int, default=30)
ap.add_argument("--seed", type=int, default=0)
args = ap.parse_args()

MATE = 100_000
VALUE = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
CLK = re.compile(r"\[%clk (\d+):(\d+):(\d+)\]")
ENGINE = None


def init_worker():
    global ENGINE
    ENGINE = chess.engine.SimpleEngine.popen_uci(args.stockfish)
    ENGINE.configure({"Threads": 1, "Hash": 64})


def cp(info, turn):
    return info["score"].pov(turn).score(mate_score=MATE)


def move_features(board, mv):
    """What kind of move is it? Humans miss quiet moves, retreats and sacrifices
    far more often than captures and checks."""
    piece = board.piece_at(mv.from_square)
    capture = board.is_capture(mv)
    check = board.gives_check(mv)
    forward = 1 if board.turn == chess.WHITE else -1
    dr = (chess.square_rank(mv.to_square) - chess.square_rank(mv.from_square)) * forward
    # Material it puts en prise: the moved piece lands where a cheaper enemy piece attacks it,
    # minus what it captured. A rough sacrifice flag, not a full exchange evaluation.
    after = board.copy(stack=False)
    after.push(mv)
    attackers = [after.piece_at(s) for s in after.attackers(not board.turn, mv.to_square)]
    taken = VALUE[board.piece_at(mv.to_square).piece_type] if capture and board.piece_at(mv.to_square) else 0
    moved = VALUE[mv.promotion or piece.piece_type]
    cheapest = min((VALUE[a.piece_type] for a in attackers if a), default=None)
    defended = bool(after.attackers(board.turn, mv.to_square))
    loss = 0
    if cheapest is not None and (cheapest < moved or not defended):
        loss = max(0, moved - taken - (cheapest if defended else 0))
    return {"capture": capture, "check": check, "quiet": not (capture or check or mv.promotion),
            "retreat": dr < 0, "piece": chess.piece_symbol(piece.piece_type), "promotion": bool(mv.promotion),
            "gives_material": loss}


def label(task):
    try:
        board = chess.Board(task["fen"])
        turn = board.turn
        top, lines = {}, {}
        with ENGINE.analysis(board, chess.engine.Limit(depth=args.depth), multipv=2, game=object()) as an:
            for info in an:
                if not info.get("pv") or "depth" not in info or "score" not in info:
                    continue
                if info.get("lowerbound") or info.get("upperbound"):   # partial result mid-iteration
                    continue
                k = info.get("multipv", 1)
                if k == 1:
                    top[info["depth"]] = info["pv"][0]
                if k not in lines or info["depth"] >= lines[k][0]:      # keep each line's deepest result
                    lines[k] = (info["depth"], info["pv"][0], cp(info, turn))
        best, best_cp = lines[1][1], lines[1][2]
        second_cp = lines[2][2] if 2 in lines else None
        played = chess.Move.from_uci(task["played"])
        if played == best:
            played_cp = best_cp
        else:
            info = ENGINE.analyse(board, chess.engine.Limit(depth=args.depth), root_moves=[played], game=object())
            played_cp = cp(info, turn)
        # depth_to_find: shallowest depth whose top move is the final best move
        d_find = min((d for d, m in top.items() if m == best), default=args.depth)
        material = sum(VALUE[p.piece_type] for p in board.piece_map().values())
        task.update(best=best.uci(), best_cp=best_cp, second_cp=second_cp,
                    gap_cp=None if second_cp is None else best_cp - second_cp, played_cp=played_cp,
                    found=played_cp >= best_cp - args.margin, depth_to_find=d_find,
                    n_legal=board.legal_moves.count(), material=material, **move_features(board, best))
        return task
    except Exception as e:                       # keep long runs alive
        print("label error:", e, file=sys.stderr)
        return None


def positions(path, band, rng):
    n = 0
    with open(path, encoding="utf-8") as f:
        while n < args.per_band:
            game = chess.pgn.read_game(f)
            if game is None:
                return
            h = game.headers
            try:
                we, be = int(h["WhiteElo"]), int(h["BlackElo"])
            except (KeyError, ValueError):
                continue
            nodes = list(game.mainline())
            plies = [i for i in range(args.skip_plies, len(nodes))]
            for i in sorted(rng.sample(plies, min(args.per_game, len(plies)))):
                node = nodes[i]
                board = node.parent.board()
                m = CLK.search(node.comment or "")
                clock = int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3]) if m else None
                if board.legal_moves.count() < 2 or (clock is not None and clock < args.min_clock):
                    continue
                white = board.turn == chess.WHITE
                yield {"band": band, "game_id": h.get("Site", ""), "ply": i, "fen": board.fen(),
                       "played": node.move.uci(), "elo": we if white else be, "opp_elo": be if white else we,
                       "clock": clock}
                n += 1
                if n >= args.per_band:
                    return


if __name__ == "__main__":
    out_dir = os.path.join(args.bands, "labels")
    os.makedirs(out_dir, exist_ok=True)
    for path in sorted(glob.glob(os.path.join(args.bands, "*.pgn"))):
        band = os.path.basename(path)[:-4]
        out = os.path.join(out_dir, f"{band}.jsonl")
        if os.path.exists(out):
            print(f"{band}: {out} exists, skipping")
            continue
        t0, n = time.time(), 0
        with mp.Pool(args.workers, initializer=init_worker) as pool, open(out + ".tmp", "w") as f:
            for r in pool.imap_unordered(label, positions(path, band, random.Random(args.seed)), chunksize=4):
                if r is None:
                    continue
                f.write(json.dumps(r) + "\n")
                n += 1
                if n % 50 == 0:
                    f.flush()
                    rate = n / (time.time() - t0)
                    print(f"\r{band:>10}: {n}/{args.per_band} positions  {rate:.1f}/s  "
                          f"~{(args.per_band - n) / rate / 60:.0f} min left   ", end="", flush=True)
        os.replace(out + ".tmp", out)
        print(f"\r{band:>10}: {n} positions in {(time.time() - t0) / 60:.1f} min -> {out}" + " " * 20)
