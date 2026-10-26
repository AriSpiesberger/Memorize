"""Rate the Stockfish levels eval.py plays, against Maia-2 at known human ratings.

    python transcend/calibrate_levels.py                       # -> results/transcend/eval/level_ratings.json
    python transcend/eval.py rerate --model Arisp/chess-pgn-1000-1300 --level-ratings results/transcend/eval/level_ratings.json

eval.py's `games` plays Lichess's AI levels (Fairy-Stockfish with Lichess's skill,
depth and move time, eval.LEVELS) but rated them with Transcendence's numbers for a
different Stockfish setup (1552 / 1842 / 2142), and the results showed those numbers
don't fit these opponents. This script measures them instead, the way the paper did
with Maia bots: every level plays Maia-2 (rapid model, sampling its moves like a
human at that rating) set to each --anchors rating, from eval.py's held-out openings
with both colours, and each level's rating is the R that best explains its results,
P(score) = 1 / (1 + 10^((anchor - R) / 400)), draws as half points, with a
likelihood-ratio 95% interval.

The scale is Maia-2's, which follows Lichess rapid ratings of the humans it imitates
and is the scale play_elo.py rates the board models on, so PGN and board models end
up comparable. Its limits: Maia-2's top bucket is everyone 2000+ (the 2100 anchor
plays as that bucket) and its bottom is everyone under 1100, so a level that wins
almost every game against the 2100 anchor only gets a lower bound; those are flagged.

Needs Fairy-Stockfish ($STOCKFISH) for the negative skill levels of Lichess levels 1-3.
"""
import argparse
import json
import queue
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import chess
import chess.engine
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))          # transcend/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))      # chess_beyond/
import paths
import eval as ev                                                 # transcend/eval.py: LEVELS, openings
from maia import elo_cat, encode, mirror_move

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--levels", type=int, nargs="+", default=[1, 2, 3, 4, 5, 6], choices=sorted(ev.LEVELS))
ap.add_argument("--anchors", type=int, nargs="+", default=[1100, 1300, 1500, 1700, 1900, 2100],
                help="Maia-2 ratings; 2100 plays as Maia's 2000+ bucket, anything under 1100 as its <1100 bucket")
ap.add_argument("--openings", type=int, default=50, help="openings, each with both colours, per level and anchor")
ap.add_argument("--opening-plies", type=int, default=8)
ap.add_argument("--max-plies", type=int, default=300)
ap.add_argument("--maia-type", choices=["rapid", "blitz"], default="rapid")
ap.add_argument("--workers", type=int, default=8, help="Stockfish processes (one core each)")
ap.add_argument("--out", default=str(paths.ROOT / "results" / "transcend" / "eval" / "level_ratings.json"))
ap.add_argument("--seed", type=int, default=0)
args = ap.parse_args()
dev = "cuda" if torch.cuda.is_available() else "cpu"
torch.manual_seed(args.seed)


@torch.inference_mode()
def maia_moves(maia, moves_dict, moves_list, boards, ratings):
    """Maia-2's sampled move for each board, each at its own rating."""
    frames = [b if b.turn == chess.WHITE else b.mirror() for b in boards]
    x = torch.from_numpy(np.stack([encode(f) for f in frames])).to(dev).float()
    mask = torch.zeros((len(frames), len(moves_list)), dtype=torch.bool, device=dev)
    for i, f in enumerate(frames):
        mask[i, [moves_dict[mv.uci()] for mv in f.legal_moves]] = True
    cat = torch.tensor([elo_cat(r) for r in ratings], device=dev)
    logits = maia(x, cat, cat)[0].float().masked_fill(~mask, -1e9)
    pick = torch.multinomial(torch.softmax(logits, -1), 1).squeeze(1).tolist()
    out = []
    for p, b in zip(pick, boards):
        mv = chess.Move.from_uci(moves_list[p])
        out.append(mv if b.turn == chess.WHITE else mirror_move(mv))
    return out


def fit(scores):
    """Max-likelihood rating from (anchor, score) pairs, with a likelihood-ratio 95% interval."""
    grid = np.arange(-500, 4000, 1.0)
    a = np.array([s[0] for s in scores], dtype=float)[:, None]
    y = np.array([s[1] for s in scores], dtype=float)[:, None]
    p = 1 / (1 + 10 ** ((a - grid[None]) / 400))
    ll = (y * np.log(p + 1e-12) + (1 - y) * np.log(1 - p + 1e-12)).sum(0)
    best = int(ll.argmax())
    inside = grid[ll >= ll[best] - 1.92]
    return float(grid[best]), (float(inside.min()), float(inside.max()))


def main():
    from maia2 import inference as I2
    from maia2 import model as M2

    maia = M2.from_pretrained(type=args.maia_type, device="gpu" if dev == "cuda" else "cpu",
                              save_root=str(paths.MAIA2)).eval()
    moves_dict, _, rev = I2.prepare()
    moves_list = [rev[i] for i in range(len(rev))]
    starts = ev.openings(args.openings, args.opening_plies)

    engines = queue.Queue()
    for _ in range(args.workers):
        e = chess.engine.SimpleEngine.popen_uci(paths.stockfish())
        e.configure({"Threads": 1, "Hash": 16})
        engines.put(e)
    first = engines.queue[0]
    lo, hi = first.options["Skill Level"].min, first.options["Skill Level"].max
    bad = [lv for lv in args.levels if not lo <= ev.LEVELS[lv][0] <= hi]
    if bad:
        sys.exit(f"this engine's Skill Level is {lo}..{hi}, so levels {bad} can't be played as Lichess does; "
                 "point $STOCKFISH at Fairy-Stockfish")
    engine_name = first.id.get("name", "?")

    G = []
    for lv in args.levels:
        for r in args.anchors:
            for sans in starts:
                for colour in (chess.WHITE, chess.BLACK):        # colour = the engine's side
                    b = chess.Board()
                    for s in sans:
                        b.push_san(s)
                    G.append(dict(level=lv, anchor=r, colour=colour, board=b, start=len(sans), result=None))
    print(f"{engine_name}: {len(args.levels)} levels x {len(args.anchors)} Maia-2 ratings x {len(starts)} openings "
          f"x 2 colours = {len(G)} games", flush=True)

    def engine_move(g):
        skill, depth, secs = ev.LEVELS[g["level"]]
        e = engines.get()
        try:
            e.configure({"Skill Level": skill})
            return e.play(g["board"], chess.engine.Limit(time=secs, depth=depth)).move
        finally:
            engines.put(e)

    t0, live = time.time(), list(G)
    with ThreadPoolExecutor(args.workers) as pool:
        while live:
            humans = [g for g in live if g["board"].turn != g["colour"]]
            engine = [g for g in live if g["board"].turn == g["colour"]]
            for s in range(0, len(humans), 512):
                chunk = humans[s:s + 512]
                for g, mv in zip(chunk, maia_moves(maia, moves_dict, moves_list, [g["board"] for g in chunk],
                                                   [g["anchor"] for g in chunk])):
                    g["board"].push(mv)
            for g, mv in zip(engine, pool.map(engine_move, engine)):
                g["board"].push(mv)
            for g in live:
                b = g["board"]
                if b.is_game_over(claim_draw=True) or len(b.move_stack) - g["start"] >= args.max_plies:
                    out = b.outcome(claim_draw=True)
                    g["result"] = 0.5 if out is None or out.winner is None else float(out.winner == g["colour"])
            live = [g for g in live if g["result"] is None]
            print(f"\r{len(G) - len(live)}/{len(G)} games finished, {time.time() - t0:.0f}s", end="", flush=True)
    while not engines.empty():
        engines.get().quit()

    top = max(args.anchors)
    record = dict(engine=engine_name, maia_type=args.maia_type, anchors=args.anchors, openings=len(starts),
                  opening_plies=args.opening_plies, max_plies=args.max_plies, seed=args.seed, levels={})
    print(f"\n\nLichess AI levels on {engine_name}, rated against Maia-2 ({args.maia_type}); score = the level's")
    print(f"{'level':>6} " + "".join(f"{'vs ' + str(r):>9}" for r in args.anchors) + f"{'rating':>10}  95% interval")
    for lv in args.levels:
        mine = [g for g in G if g["level"] == lv]
        per = {}
        for r in args.anchors:
            res = [g["result"] for g in mine if g["anchor"] == r]
            per[r] = dict(games=len(res), wins=res.count(1.0), draws=res.count(0.5), losses=res.count(0.0),
                          score=sum(res) / len(res))
        R, (lo_, hi_) = fit([(g["anchor"], g["result"]) for g in mine])
        bound = per[top]["score"] > 0.95                     # beats Maia's top bucket nearly always
        record["levels"][lv] = dict(rating=R, ci95=[lo_, hi_], lower_bound_only=bound, anchors=per,
                                    skill_depth_secs=ev.LEVELS[lv])
        print(f"{lv:>6} " + "".join(f"{per[r]['score']:>9.2f}" for r in args.anchors)
              + f"{R:>10.0f}  {lo_:.0f}-{hi_:.0f}" + ("   (lower bound: beats Maia's top bucket)" if bound else ""))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(record, indent=1))
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
