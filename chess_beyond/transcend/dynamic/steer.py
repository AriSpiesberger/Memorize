"""Steering a mined concept: its direction in a model's layer-11 state, the push, and what the push does.

A concept (concept_mine.py) is a unit vector v over crosscoder latents, in units of each latent's mean firing mu_j. Its
direction in model m's residual stream is  u_m = sum_j v_j mu_j W_dec[j, m] / scale_m  (the crosscoder's decoder for that
model, the input scaling undone), so adding c u_m raises the concept's activity v . z by c. overnight_confirm.py pushes
h -> h + r ||h|| u_hat at the prompt end (where the model is about to write its move) and reads the change in its moves.

The pilot and its follow-ups that led to that test (steer_concepts, steer_after, steer_hist, steer_match: strength in the
concept's own gap, then by the state's norm, after the split, over the last 6 plies, against the natural change) are in
git history before this file; none passed its self-check.
"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]                      # chess_beyond/
sys.path.insert(0, str(ROOT))
import paths  # noqa: E402,F401  also puts transcend/'s folders on sys.path


def advance(p, b, san):
    import chess
    mv = b.parse_san(san)
    p += san + (" " if b.turn == chess.WHITE else f" {b.fullmove_number + 1}.")
    b.push(mv)
    return p


def prompt_at(root, sans, n):
    """The prompt and board after the first n moves of a line from root (shared.positions' format)."""
    import chess
    b = chess.Board(root["fen"]); p = root["prompt"]
    for s in sans[:n]: p = advance(p, b, s)
    return p, b.fen()


def setup(a):
    import eval as ev
    import shared as gd
    dev = ev.device(a.device)
    cc = gd.load_cc(ROOT / a.cc_run, a.cc, a.strong, dev)
    models = {m: ev.load(cc.info["models"][m], dev)[0] for m in (0, 1)}
    return dev, gd, cc, models, {"S": cc.s, "W": cc.w}


def direction(cc, lat, w, mu, col, dev):
    import torch
    Wd = cc.coder.W_dec.detach().float()
    d = (torch.tensor(w, device=dev)[:, None] * torch.tensor(mu, device=dev)[:, None] * Wd[lat, col]).sum(0)
    return d / cc.scales[col]


def states(gd, cc, models, mi, mo, pts, a, dev):
    """Target model mi's boards, legal moves, base log-probabilities and L11 states at the points; the other model's states."""
    import chess
    boards = [chess.Board(p["fen"]) for p in pts]; prompts = [p["prompt"] for p in pts]
    legal, base, st = gd.policy(models[mi], boards, dev, prompts, grab=(str(cc.layer[mi]),), batch=a.batch)
    _, _, st2 = gd.policy(models[mo], boards, dev, prompts, grab=(str(cc.layer[mo]),), batch=a.batch)
    return boards, prompts, legal, base, st[str(cc.layer[mi])].to(dev), st2[str(cc.layer[mo])].to(dev)


def readback(gd, cc, mi, mo, h, oh, push, jb, dev):
    """Rise in the concept's activity sum_j w_j z_j / mu_j per point after h -> h + push."""
    import torch
    with torch.no_grad():
        f0, _ = gd.encode_states(cc, {mi: h, mo: oh}); f1, _ = gd.encode_states(cc, {mi: h + push, mo: oh})
        wv = torch.tensor(jb["w"], device=dev) / torch.tensor(jb["mu"], device=dev)
        return ((f1[:, jb["lat"]] - f0[:, jb["lat"]]).float() * wv).sum(1).cpu().numpy()


def fits(models, pts):
    from pgn_model import MAX_MOVE_CHARS, encode
    ctx = min(m.ctx for m in models.values())
    return [p for p in pts if len(encode(p["prompt"])) + MAX_MOVE_CHARS + 1 <= ctx]


def feats(fen, moves):
    """Per legal move: piece moved (6), from (64), to (64), capture, check, castles."""
    import chess
    b = chess.Board(fen); X = np.zeros((len(moves), 6 + 128 + 3))
    for i, u in enumerate(moves):
        mv = chess.Move.from_uci(u); p = b.piece_at(mv.from_square)
        X[i, p.piece_type - 1] = 1; X[i, 6 + mv.from_square] = 1; X[i, 70 + mv.to_square] = 1
        X[i, 134] = b.is_capture(mv); X[i, 135] = b.gives_check(mv); X[i, 136] = b.is_castling(mv)
    return X
