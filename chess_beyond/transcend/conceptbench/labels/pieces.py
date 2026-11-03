"""What each side has on the board. Every value of a count is its own yes-or-no concept, since the LP is binary.

"Exactly k" of a middle value is not monotone in the count, so one linear direction can't express it even if the model holds
the count linearly. "At least k" can be: it is the fair test of a count. (At least the top value is that value's own concept.)
"""

import chess

VERSION = 2
MAX_ROOKS = 2       # the last value means "this many or more"
MAX_MINORS = 4

DEFS = {}
for _s in ("white", "black"):
    DEFS[f"{_s}_has_queen"] = f"{_s} has at least one queen"
    DEFS[f"{_s}_bishop_pair"] = f"{_s} has two or more bishops"
    for _n in range(MAX_ROOKS + 1):
        DEFS[f"{_s}_rooks_{_n}"] = f"{_s} has {_n}{'+' if _n == MAX_ROOKS else ''} rooks"
    for _n in range(MAX_MINORS + 1):
        DEFS[f"{_s}_minors_{_n}"] = f"{_s} has {_n}{'+' if _n == MAX_MINORS else ''} bishops and knights"
    for _n in range(1, MAX_ROOKS):
        DEFS[f"{_s}_rooks_atleast_{_n}"] = f"{_s} has at least {_n} rooks"
    for _n in range(1, MAX_MINORS):
        DEFS[f"{_s}_minors_atleast_{_n}"] = f"{_s} has at least {_n} bishops and knights"


def labels(board, game=None):
    out = {}
    for c, s in ((chess.WHITE, "white"), (chess.BLACK, "black")):
        bishops, knights, rooks = (len(board.pieces(t, c)) for t in (chess.BISHOP, chess.KNIGHT, chess.ROOK))
        out[f"{s}_has_queen"] = bool(board.pieces(chess.QUEEN, c))
        out[f"{s}_bishop_pair"] = bishops >= 2
        for n in range(MAX_ROOKS + 1):
            out[f"{s}_rooks_{n}"] = min(rooks, MAX_ROOKS) == n
        for n in range(MAX_MINORS + 1):
            out[f"{s}_minors_{n}"] = min(bishops + knights, MAX_MINORS) == n
        for n in range(1, MAX_ROOKS):
            out[f"{s}_rooks_atleast_{n}"] = rooks >= n
        for n in range(1, MAX_MINORS):
            out[f"{s}_minors_atleast_{n}"] = bishops + knights >= n
    return out
