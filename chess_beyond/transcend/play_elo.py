"""Playing strength in games: checkpoints vs Maia-2 at fixed ratings, fitted to an Elo.

    python transcend/play_elo.py --ckpt runs/transcend/imitation-clean.pt runs/transcend/rl-clean.pt

Puzzle Elo measures tactics on puzzles; this measures whole games. Each
checkpoint plays Maia-2 (rapid model) set to each --anchors rating. Maia samples
its moves from its predicted distribution, so it plays like a human at that rating,
blunders included; the checkpoint plays its greedy move, as in the puzzle evals.

Games start from --openings positions taken --opening-plies into real games from
--pgn (the 1000-1300 band), each played once with either colour. A game is drawn
at --max-plies or by the usual rules (threefold and fifty-move claimed).

The rating is the R that best explains every result, with the Elo model
P(score) = 1 / (1 + 10^((anchor - R) / 400)) and draws as half points; the 95%
interval is where the log-likelihood is within 1.92 of its best. It is on Maia's
scale, which follows Lichess rapid ratings of the humans it imitates. Maia-2's
lowest bucket covers everyone under 1100; that anchor is counted as 1000, so
ratings well below 1100 are an extrapolation.

Results are appended to results/transcend/play_elo.jsonl.
"""
import argparse
import io
import json
import math
import random
import sys
import time
from pathlib import Path

import chess
import chess.pgn
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # chess_beyond/
import paths
from common import MOVES, encode_board, legal_mask, load_model, masked_logits, model_move_to_real
from maia import elo_cat, encode, mirror_move
from pgn_model import generate_moves, load_pgn_model

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--ckpt", nargs="+", required=True)
ap.add_argument("--anchors", default="1000,1100,1300,1500,1700",
                help="Maia-2 ratings to play; Maia-2's lowest bucket is <1100, counted here as 1000")
ap.add_argument("--openings", type=int, default=100, help="opening positions, each played with both colours")
ap.add_argument("--opening-plies", type=int, default=8)
ap.add_argument("--pgn", default=str(paths.LICHESS / "bands" / "2025-06-train" / "1000-1300.maia-clean.pgn"))
ap.add_argument("--max-plies", type=int, default=300, help="plies after the opening before a draw is called")
ap.add_argument("--maia-type", choices=["rapid", "blitz"], default="rapid")
ap.add_argument("--out", default=str(paths.ROOT / "results" / "transcend" / "play_elo.jsonl"))
ap.add_argument("--temperature", type=float, default=0.0,
                help="the checkpoint's sampling temperature; 0 = greedy (Transcendence used 0.001, 1.0, 1.5)")
ap.add_argument("--seed", type=int, default=0)
args = ap.parse_args()
dev = "cuda" if torch.cuda.is_available() else "cpu"
random.seed(args.seed)
torch.manual_seed(args.seed)


def openings():
    """Positions --opening-plies into games picked evenly through the PGN."""
    out, seen = [], set()
    with open(args.pgn, encoding="utf-8") as f:
        while len(out) < args.openings * 20:            # read a pool, then sample from it
            g = chess.pgn.read_game(f)
            if g is None:
                break
            b = g.board()
            for ply, mv in enumerate(g.mainline_moves()):
                if ply == args.opening_plies:
                    break
                b.push(mv)
            if ply == args.opening_plies and not b.is_game_over() and b.fen() not in seen:
                seen.add(b.fen())
                out.append(b)
    return random.Random(args.seed).sample(out, min(args.openings, len(out)))


def load_any(path):
    """A board model (common.ChessNet) or a PGN model (pgn_model.PGNTransformer)."""
    kind = torch.load(path, map_location="cpu", weights_only=False)["config"].get("kind", "board")
    return (load_pgn_model(path, dev) if kind == "pgn" else load_model(path, dev)).eval(), kind


@torch.inference_mode()
def ours_move(model, kind, boards):
    """The checkpoint's move for each board; None means it failed to give a legal move."""
    if kind == "pgn":
        return generate_moves(model, boards, args.temperature, dev)
    x = torch.tensor([encode_board(b) for b in boards], device=dev)
    m = torch.stack([legal_mask(b) for b in boards]).to(dev)
    logits = masked_logits(model(x)[0].float(), m)
    if args.temperature <= 0:
        choice = logits.argmax(-1).tolist()
    else:
        choice = torch.multinomial(torch.softmax(logits / args.temperature, -1), 1).squeeze(1).tolist()
    return [model_move_to_real(MOVES[c], b.turn) for c, b in zip(choice, boards)]


@torch.inference_mode()
def maia_move(maia, moves_dict, moves_list, boards, rating):
    frames = [b if b.turn == chess.WHITE else b.mirror() for b in boards]
    x = torch.from_numpy(np.stack([encode(f) for f in frames])).to(dev).float()
    mask = torch.zeros((len(frames), len(moves_list)), dtype=torch.bool, device=dev)
    for i, f in enumerate(frames):
        mask[i, [moves_dict[mv.uci()] for mv in f.legal_moves]] = True
    cat = torch.full((len(frames),), elo_cat(rating), device=dev)
    logits = maia(x, cat, cat)[0].float().masked_fill(~mask, -1e9)
    pick = torch.multinomial(torch.softmax(logits, -1), 1).squeeze(1).tolist()
    out = []
    for p, b in zip(pick, boards):
        mv = chess.Move.from_uci(moves_list[p])
        out.append(mv if b.turn == chess.WHITE else mirror_move(mv))
    return out


def play(model, kind, maia, moves_dict, moves_list, starts, rating):
    """Score (1 / 0.5 / 0 for the checkpoint) of every opening x colour against Maia at `rating`."""
    games = [(b.copy(), colour) for b in starts for colour in (chess.WHITE, chess.BLACK)]
    plies = [0] * len(games)
    result = [None] * len(games)
    forfeits[0] = 0
    while True:
        live = [i for i, (b, _) in enumerate(games) if result[i] is None]
        if not live:
            break
        ours = [i for i in live if games[i][0].turn == games[i][1]]
        theirs = [i for i in live if games[i][0].turn != games[i][1]]
        for idx, fn in ((ours, lambda bs: ours_move(model, kind, bs)),
                        (theirs, lambda bs: maia_move(maia, moves_dict, moves_list, bs, rating))):
            if not idx:
                continue
            for i, mv in zip(idx, fn([games[i][0] for i in idx])):
                b, colour = games[i]
                if mv is None:                        # no legal move in 5 tries: the game is lost
                    result[i] = 0.0
                    forfeits[0] += 1
                    continue
                b.push(mv)
                plies[i] += 1
                if b.is_checkmate():
                    result[i] = 1.0 if b.turn != colour else 0.0
                elif b.is_game_over(claim_draw=True) or plies[i] >= args.max_plies:
                    result[i] = 0.5
    return result


forfeits = [0]          # games lost by failing to produce a legal move, per play() call


def fit(scores):
    """Max-likelihood rating from (anchor, score) pairs, with a likelihood-ratio 95% interval."""
    grid = np.arange(-500, 3500, 1.0)
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
    moves_dict, _, moves_rev = I2.prepare()
    moves_list = [moves_rev[i] for i in range(len(moves_rev))]
    anchors = [int(a) for a in args.anchors.split(",")]
    starts = openings()
    print(f"{len(starts)} openings x 2 colours x {len(anchors)} Maia-2 ratings = "
          f"{2 * len(starts) * len(anchors)} games per checkpoint")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    for ckpt in args.ckpt:
        model, kind = load_any(ckpt)
        scores, per = [], {}
        t0 = time.time()
        for r in anchors:
            res = play(model, kind, maia, moves_dict, moves_list, starts, r)
            scores += [(r, s) for s in res]
            w, d = sum(s == 1.0 for s in res), sum(s == 0.5 for s in res)
            per[r] = dict(games=len(res), wins=w, draws=d, losses=len(res) - w - d, score=sum(res) / len(res),
                          illegal_forfeits=forfeits[0])
            print(f"  {Path(ckpt).name} vs Maia-2 {r}: +{w} ={d} -{len(res) - w - d}  "
                  f"score {per[r]['score']:.1%}" + (f"  ({forfeits[0]} lost to illegal moves)" if forfeits[0] else ""),
                  flush=True)
        R, (lo, hi) = fit(scores)
        print(f"{Path(ckpt).name} (temperature {args.temperature}): game Elo {R:.0f} (95% CI {lo:.0f}-{hi:.0f}), {time.time() - t0:.0f}s\n", flush=True)
        step = torch.load(ckpt, map_location="cpu", weights_only=False).get("extra", {}).get("step")
        with open(args.out, "a", encoding="utf-8") as f:
            f.write(json.dumps(dict(ckpt=ckpt, kind=kind, temperature=args.temperature, step=step, elo=R, ci95=[lo, hi], anchors=per,
                                    openings=len(starts), maia_type=args.maia_type, seed=args.seed)) + "\n")


if __name__ == "__main__":
    main()
