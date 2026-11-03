"""Imbalances, one concept per side (white_<name>, black_<name>). Thresholds below; each rule is in DEFS and goes in the
manifest. Where the good-or-bad reading is unclear the label is None, so the middle of the range is neither."""

import chess

from bench import VALUES

VERSION = 1

BAD_BISHOP_SHARE = 0.6      # bad bishop: at least this share of own pawns on its colour
GOOD_BISHOP_SHARE = 0.4     # good bishop: at most this share
BISHOP_MIN_PAWNS = 4        # with fewer own pawns the share means little
SPACE_FILES = "cdef"        # files counted for space
SPACE_MARGIN = 3            # space advantage: this many squares more than the opponent
SPACE_MIN_PAWNS = 4         # both sides
OUTPOST_RANKS = (3, 4, 5)   # ranks 4 to 6 from the knight's side, counted from 0
WEAK_KING_SQUARES = 2       # weak squares in front of the king: at least this many
DEVELOPMENT_LEAD = 2        # development lead: at least this many more points
DEVELOPMENT_LAST_MOVE = 15  # development is not a question after this move
KING_UNSAFE = 5             # king danger at least this: unsafe
KING_SAFE = 2               # king danger at most this: safe

MINOR_HOME = {chess.WHITE: ((chess.KNIGHT, chess.B1), (chess.KNIGHT, chess.G1), (chess.BISHOP, chess.C1), (chess.BISHOP, chess.F1)),
              chess.BLACK: ((chess.KNIGHT, chess.B8), (chess.KNIGHT, chess.G8), (chess.BISHOP, chess.C8), (chess.BISHOP, chess.F8))}
CASTLED = {chess.WHITE: (chess.G1, chess.C1), chess.BLACK: (chess.G8, chess.C8)}

RULES = {
    "bishop_vs_knight": "this side has bishops and no knights, the other knights and no bishops, as many minor pieces each",
    "bad_bishop": f"one bishop and at least {BISHOP_MIN_PAWNS} own pawns; positive: at least {BAD_BISHOP_SHARE:.0%} of them on "
                  f"its colour; negative: at most {GOOD_BISHOP_SHARE:.0%} (a good bishop); between: no label",
    "space_advantage": f"space = over files {SPACE_FILES}, the relative rank of the most advanced own pawn (no pawn counts as the "
                       f"second rank); this side's is at least {SPACE_MARGIN} more; both sides at least {SPACE_MIN_PAWNS} pawns",
    "rook_open_file": "a rook on a file with no pawns",
    "rook_half_open_file": "a rook on a file with no own pawn and an enemy pawn",
    "queen_open_or_half_open_file": "a queen on a file with no own pawn",
    "knight_outpost": "a knight on its 4th to 6th rank, defended by an own pawn, on a square no enemy pawn can ever attack",
    "weak_king_squares": f"king on its first two ranks, enemy queen on: at least {WEAK_KING_SQUARES} of the squares on the two "
                         "ranks in front of it, on its file and the next, from the third rank up, hold no own pawn and can "
                         "never be defended by one",
    "queenside_majority": "more pawns than the opponent on files a-d",
    "kingside_majority": "more pawns than the opponent on files e-h",
    "passed_pawn": "a pawn with no enemy pawn ahead of it on its file or the next",
    "development_lead": f"up to move {DEVELOPMENT_LAST_MOVE}; development = minor pieces off their home squares, plus one if "
                        f"the king is on a castled square; this side's is at least {DEVELOPMENT_LEAD} more",
    "king_unsafe": "enemy queen on; king danger = missing shield pawns (of 3, on the two ranks in front, its file and the next) "
                   "+ files next to and on the king with no own pawn + enemy queens, rooks, bishops and knights attacking a "
                   f"square next to the king. Positive: danger at least {KING_UNSAFE}; negative: at most {KING_SAFE}; between: no label",
}
DEFS = {f"{s}_{k}": v for s in ("white", "black") for k, v in RULES.items()}


def rel_rank(sq, color):
    r = chess.square_rank(sq)
    return r if color == chess.WHITE else 7 - r


def pawns(board, color):
    return board.pieces(chess.PAWN, color)


def file_pawns(board, f, color):
    return int(board.pieces_mask(chess.PAWN, color) & chess.BB_FILES[f])


def bishop_vs_knight(board, c):
    me, you = (len(board.pieces(chess.BISHOP, c)), len(board.pieces(chess.KNIGHT, c))), \
              (len(board.pieces(chess.BISHOP, not c)), len(board.pieces(chess.KNIGHT, not c)))
    return me[0] > 0 and me[1] == 0 and you[0] == 0 and you[1] == me[0]


def bad_bishop(board, c):
    bs, ps = board.pieces(chess.BISHOP, c), pawns(board, c)
    if len(bs) != 1 or len(ps) < BISHOP_MIN_PAWNS:
        return None
    colour = chess.BB_LIGHT_SQUARES if chess.BB_SQUARES[next(iter(bs))] & chess.BB_LIGHT_SQUARES else chess.BB_DARK_SQUARES
    share = bin(int(ps) & colour).count("1") / len(ps)
    return True if share >= BAD_BISHOP_SHARE else False if share <= GOOD_BISHOP_SHARE else None


def space(board, c):
    total = 0
    for f in SPACE_FILES:
        fi = "abcdefgh".index(f)
        rs = [rel_rank(s, c) for s in pawns(board, c) if chess.square_file(s) == fi]
        total += max(rs) if rs else 1
    return total


def space_advantage(board, c):
    if min(len(pawns(board, chess.WHITE)), len(pawns(board, chess.BLACK))) < SPACE_MIN_PAWNS:
        return None
    return space(board, c) - space(board, not c) >= SPACE_MARGIN


def heavy_on_file(board, c, piece, half):
    """A piece of this side on a file with no own pawn; half: with an enemy pawn on it; not half: with no pawn at all."""
    for s in board.pieces(piece, c):
        f = chess.square_file(s)
        if not file_pawns(board, f, c) and bool(file_pawns(board, f, not c)) == half:
            return True
    return False


def adjacent(f):
    return [x for x in (f - 1, f + 1) if 0 <= x <= 7]


def knight_outpost(board, c):
    for s in board.pieces(chess.KNIGHT, c):
        rr, f = rel_rank(s, c), chess.square_file(s)
        if rr not in OUTPOST_RANKS or not board.attackers_mask(c, s) & board.pieces_mask(chess.PAWN, c):
            continue
        if not any(chess.square_file(p) in adjacent(f) and rel_rank(p, c) > rr for p in pawns(board, not c)):
            return True
    return False


def front_squares(board, c):
    """The squares on the two ranks in front of this side's king, on its file and the next."""
    k = board.king(c)
    f, rr = chess.square_file(k), rel_rank(k, c)
    out = []
    for r in (rr + 1, rr + 2):
        for x in [f] + adjacent(f):
            if r <= 7:
                out.append(chess.square(x, r if c == chess.WHITE else 7 - r))
    return out


def weak_king_squares(board, c):
    if rel_rank(board.king(c), c) > 1 or not board.pieces(chess.QUEEN, not c):
        return None
    own = pawns(board, c)
    n = 0
    for s in front_squares(board, c):
        f, rr = chess.square_file(s), rel_rank(s, c)
        if s in own or rr < 2:      # on the second rank every empty square qualifies: pawns do not go back
            continue
        if not any(chess.square_file(p) in adjacent(f) and rel_rank(p, c) < rr for p in own):
            n += 1
    return n >= WEAK_KING_SQUARES


def majority(board, c, files):
    mask = 0
    for f in files:
        mask |= chess.BB_FILES[f]
    return bin(int(board.pieces_mask(chess.PAWN, c)) & mask).count("1") > bin(int(board.pieces_mask(chess.PAWN, not c)) & mask).count("1")


def passed_pawn(board, c):
    enemy = pawns(board, not c)
    for s in pawns(board, c):
        f, rr = chess.square_file(s), rel_rank(s, c)
        if not any(abs(chess.square_file(e) - f) <= 1 and rel_rank(e, c) > rr for e in enemy):
            return True
    return False


def development(board, c):
    home = sum(board.piece_type_at(s) == t and board.color_at(s) == c for t, s in MINOR_HOME[c])
    return 4 - home + (board.king(c) in CASTLED[c])


def development_lead(board, c):
    if board.fullmove_number > DEVELOPMENT_LAST_MOVE:
        return None
    return development(board, c) - development(board, not c) >= DEVELOPMENT_LEAD


def king_danger(board, c):
    k = board.king(c)
    f = chess.square_file(k)
    fronts = front_squares(board, c)
    shield = sum(s in pawns(board, c) for s in fronts)
    bare = sum(not file_pawns(board, x, c) for x in [f] + adjacent(f))
    ring = chess.SquareSet(chess.BB_KING_ATTACKS[k])
    attackers = 0
    for t in VALUES:
        if t == chess.PAWN:
            continue
        for s in board.pieces(t, not c):
            if board.attacks_mask(s) & int(ring):
                attackers += 1
    return max(0, 3 - shield) + bare + attackers


def king_unsafe(board, c):
    if not board.pieces(chess.QUEEN, not c):
        return None
    d = king_danger(board, c)
    return True if d >= KING_UNSAFE else False if d <= KING_SAFE else None


def labels(board, game=None):
    out = {}
    for c, s in ((chess.WHITE, "white"), (chess.BLACK, "black")):
        out[f"{s}_bishop_vs_knight"] = bishop_vs_knight(board, c)
        out[f"{s}_bad_bishop"] = bad_bishop(board, c)
        out[f"{s}_space_advantage"] = space_advantage(board, c)
        out[f"{s}_rook_open_file"] = heavy_on_file(board, c, chess.ROOK, False)
        out[f"{s}_rook_half_open_file"] = heavy_on_file(board, c, chess.ROOK, True)
        out[f"{s}_queen_open_or_half_open_file"] = (heavy_on_file(board, c, chess.QUEEN, False)
                                                    or heavy_on_file(board, c, chess.QUEEN, True))
        out[f"{s}_knight_outpost"] = knight_outpost(board, c)
        out[f"{s}_weak_king_squares"] = weak_king_squares(board, c)
        out[f"{s}_queenside_majority"] = majority(board, c, range(4))
        out[f"{s}_kingside_majority"] = majority(board, c, range(4, 8))
        out[f"{s}_passed_pawn"] = passed_pawn(board, c)
        out[f"{s}_development_lead"] = development_lead(board, c)
        out[f"{s}_king_unsafe"] = king_unsafe(board, c)
    return out
