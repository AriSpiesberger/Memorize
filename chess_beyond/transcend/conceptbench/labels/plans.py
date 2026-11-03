"""Dynamic: for a position in a structure, did the game carry out the structure's book plan within the next HORIZON plies?
Asked only where the plan's first move has not been played yet, and only where HORIZON more plies are known (a game
that ends sooner, or a held-out game whose later moves we do not have, gets no label). The mark of a plan is its first
move, which can be read off a game without judging intent. Negatives are therefore always in the same structure.

Every rule is written for the plan's side, its pawns as if White (us), the opponent's as if Black (them), so ...f5 in a
King's Indian reads f4 here. The docstrings are the definitions.
"""

from collections import namedtuple

import chess

from .structures import carlsbad, isolated_queens_pawn, kings_indian, maroczy_bind, sq

VERSION = 1
HORIZON = 10
flip = chess.flip_vertical


def carlsbad_minority(us, them):
    """In a Carlsbad, the side with the minority, its b-pawn still on b2 or b3. Positive: the b-pawn goes to b4, the
    first step of the minority attack."""
    return carlsbad(us, them) and bool(us & sq("b2", "b3"))


def iqp_break(us, them):
    """With an isolated queen's pawn on d4 (d5 for Black). Positive: it advances, the d4-d5 break."""
    return isolated_queens_pawn(us, them)


def kings_indian_storm(us, them):
    """In a closed King's Indian, Black, the f-pawn still on f7 or f6 and the g-pawn on g7 or g6. Positive: ...f5 or
    ...g5, the first step of the kingside storm."""
    return kings_indian(flip(them), flip(us)) and bool(us & sq("f2", "f3")) and bool(us & sq("g2", "g3"))


def maroczy_break(us, them):
    """In a Maroczy bind, the side bound, its d-pawn on d6 or d7 and its b-pawn on b7 or b6. Positive: ...b5 or ...d5."""
    return maroczy_bind(flip(them), flip(us)) and bool(us & sq("d2", "d3")) and bool(us & sq("b2", "b3"))


Plan = namedtuple("Plan", "rule marks colors")      # marks: the (from squares, to square) that carry it out
PLANS = {"plan_carlsbad_minority": Plan(carlsbad_minority, [((chess.B2, chess.B3), chess.B4)], chess.COLORS),
         "plan_iqp_break": Plan(iqp_break, [((chess.D4,), chess.D5)], chess.COLORS),
         "plan_kings_indian_storm": Plan(kings_indian_storm, [((chess.F2, chess.F3), chess.F4), ((chess.G2, chess.G3), chess.G4)],
                                         (chess.BLACK,)),
         "plan_maroczy_break": Plan(maroczy_break, [((chess.B2, chess.B3), chess.B4), ((chess.D2, chess.D3), chess.D4)], chess.COLORS)}
DEFS = {k: " ".join(p.rule.__doc__.split()) + f" Within {HORIZON} plies; only where {HORIZON} more plies are known."
        for k, p in PLANS.items()}


def pawn_moves(board, future, color):
    """(from, to) of this colour's pawn moves along the future moves, as if White."""
    b = board.copy(stack=False)
    out = []
    for u in future[:HORIZON]:
        m = chess.Move.from_uci(u)
        if b.turn == color and b.piece_type_at(m.from_square) == chess.PAWN:
            out.append((m.from_square, m.to_square) if color == chess.WHITE
                       else (chess.square_mirror(m.from_square), chess.square_mirror(m.to_square)))
        b.push(m)
    return out


def labels(board, game=None):
    w = board.pieces_mask(chess.PAWN, chess.WHITE)
    b = board.pieces_mask(chess.PAWN, chess.BLACK)
    future = (game or {}).get("future") or []
    out = {}
    for name, p in PLANS.items():
        sides = [c for c in p.colors if (p.rule(w, b) if c == chess.WHITE else p.rule(flip(b), flip(w)))]
        if not sides or len(future) < HORIZON:
            out[name] = None
            continue
        moves = [mv for c in sides for mv in pawn_moves(board, future, c)]
        out[name] = any(f in src and t == to for f, t in moves for src, to in p.marks)
    return out
