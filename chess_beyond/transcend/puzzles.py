"""Puzzle helpers shared by evaluation and RL: load strata, play solutions with the network.

A Lichess puzzle is a FEN plus a move list: moves[0] is the opponent's move that
sets the puzzle up, then the solver and the opponent alternate. The solver must
play every one of their moves; the opponent's replies are given. As on Lichess, a
different move that mates on the spot also counts.
"""
import json
import math
from pathlib import Path

import chess
import torch

from common import MOVE_TO_ID, MOVES, encode_board, legal_mask, masked_logits, model_move_to_real


def load(path, n=0):
    rows = [json.loads(l) for l in open(path)]
    return rows[:n] if n else rows


def start(pz):
    """Board after the opponent's setup move, and the remaining line."""
    b = chess.Board(pz["fen"])
    b.push_uci(pz["moves"][0])
    return b, pz["moves"][1:]


def ladder(strata_dir, per_stratum=300):
    """A fixed rating ladder: the first per_stratum puzzles of every stratum file (1000 ... 2800)."""
    out = []
    for p in sorted(Path(strata_dir).glob("*.jsonl")):
        out += load(p, per_stratum)
    return out


def fit_elo(ratings, solved):
    """Puzzle rating R maximising the likelihood of the outcomes under
    P(solve) = 1 / (1 + 10^((puzzle - R) / 400)), with a 95% interval from the Fisher information."""
    def ll(R):
        return sum(-math.log1p(10 ** ((r - R) / 400)) if s else -math.log1p(10 ** ((R - r) / 400))
                   for r, s in zip(ratings, solved))
    lo, hi = -500.0, 4000.0
    while hi - lo > 1:                                  # the log-likelihood is concave in R
        m1, m2 = lo + (hi - lo) / 3, hi - (hi - lo) / 3
        lo, hi = (m1, hi) if ll(m1) < ll(m2) else (lo, m2)
    R = (lo + hi) / 2
    k = math.log(10) / 400
    info = sum(k * k * q * (1 - q) for q in (1 / (1 + 10 ** ((r - R) / 400)) for r in ratings))
    se = 1 / math.sqrt(info)
    return R, (R - 1.96 * se, R + 1.96 * se)


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


@torch.no_grad()
def solve(model, puzzles, dev, sample=False, temperature=1.0, record=False, batch=4096):
    """Play every puzzle's solution with the network (greedy, or sampled for RL).

    Returns per puzzle: solved (bool), first move right (bool), solver moves right
    before the first mistake, total solver moves. With record=True also returns
    the steps taken, as (puzzle index, board tokens, legal mask, chosen move id),
    so RL can recompute log-probs with gradients."""
    n = len(puzzles)
    boards, lines = zip(*(start(p) for p in puzzles)) if n else ((), ())
    boards, lines = [b.copy() for b in boards], list(lines)
    pos = [0] * n                                   # index into the line of the next solver move
    alive = list(range(n))
    solved, first, right = [False] * n, [False] * n, [0] * n
    total = [(len(l) + 1) // 2 for l in lines]
    steps = []
    while alive:
        nxt = []
        for s in range(0, len(alive), batch):
            idx = alive[s:s + batch]
            x = torch.tensor([encode_board(boards[i]) for i in idx], device=dev)
            m = torch.stack([legal_mask(boards[i]) for i in idx]).to(dev)
            logits = masked_logits(model(x)[0].float(), m)
            if sample:
                choice = torch.multinomial(torch.softmax(logits / temperature, -1), 1).squeeze(1)
            else:
                choice = logits.argmax(-1)
            for j, i in enumerate(idx):
                b = boards[i]
                mv = model_move_to_real(MOVES[int(choice[j])], b.turn)
                want = chess.Move.from_uci(lines[i][pos[i]])
                if record:
                    steps.append((i, x[j].cpu(), m[j].cpu(), int(choice[j])))
                ok = mv == want
                if not ok and pos[i] == len(lines[i]) - 1:        # last move: any mate counts
                    b2 = b.copy(stack=False); b2.push(mv); ok = b2.is_checkmate()
                if pos[i] == 0:
                    first[i] = ok
                if not ok:
                    continue
                right[i] += 1
                b.push(want if mv == want else mv)
                if pos[i] + 1 < len(lines[i]):
                    b.push_uci(lines[i][pos[i] + 1])               # the opponent's reply
                pos[i] += 2
                if pos[i] >= len(lines[i]):
                    solved[i] = True
                else:
                    nxt.append(i)
        alive = nxt
    out = dict(solved=solved, first=first, right=right, total=total)
    if record:
        out["steps"] = steps
    return out


def report(name, res, expected=None):
    n = len(res["solved"])
    k, f = sum(res["solved"]), sum(res["first"])
    lo, hi = wilson(k, n)
    exp = f"   (an 1100 human: ~{expected:.2%})" if expected is not None else ""
    return (f"{name:>10}: solved {k:5d}/{n:<5d} = {k / max(n, 1):6.2%}  [95% CI {lo:.2%}-{hi:.2%}]   "
            f"first move {f / max(n, 1):6.1%}{exp}")
