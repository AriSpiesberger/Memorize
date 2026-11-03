"""Named pawn structures, each an explicit rule on pawn squares. The rules look only at pawns.

A rule is written with us / them for a structure either colour can have (the concept is True if it holds for White as
written, or for Black on the mirrored board), and with white / black for a defence that belongs to one colour. Each
docstring is the definition; it goes in the manifest.
"""

import chess

VERSION = 1
MIN_PAWNS = 4       # isolated queen's pawn and hanging pawns: at least this many pawns on that side, so not a bare endgame


def sq(*names):
    m = 0
    for n in names:
        m |= chess.BB_SQUARES[chess.parse_square(n)]
    return m


def has(pawns, *names):
    """All these squares hold a pawn."""
    m = sq(*names)
    return pawns & m == m


def on_file(pawns, f):
    return pawns & chess.BB_FILES["abcdefgh".index(f)]


def count(mask):
    return bin(mask).count("1")


def isolated_queens_pawn(us, them):
    """Us: a single d-pawn, on d4, no pawn on the c- or e-file, at least MIN_PAWNS pawns. Them: no d-pawn."""
    return (has(us, "d4") and count(on_file(us, "d")) == 1 and not on_file(us, "c") and not on_file(us, "e")
            and not on_file(them, "d") and count(us) >= MIN_PAWNS)


def hanging_pawns(us, them):
    """Us: pawns on c4 and d4, the only ones on those files, none on the b- or e-file, at least MIN_PAWNS pawns. Them:
    no c-pawn, no d-pawn."""
    return (has(us, "c4", "d4") and count(on_file(us, "c")) == 1 and count(on_file(us, "d")) == 1
            and not on_file(us, "b") and not on_file(us, "e") and not on_file(them, "c") and not on_file(them, "d")
            and count(us) >= MIN_PAWNS)


def carlsbad(us, them):
    """The QGD Exchange structure; us: the side that can play the minority attack. Us: d4, an e-pawn on e2 or e3, a
    b-pawn, no c-pawn. Them: d5, a c-pawn on c6 or c7, a b-pawn, no e-pawn. (Colours reversed it is the Caro-Kann
    Exchange.)"""
    return (has(us, "d4") and bool(us & sq("e2", "e3")) and bool(on_file(us, "b")) and not on_file(us, "c")
            and has(them, "d5") and bool(them & sq("c6", "c7")) and bool(on_file(them, "b")) and not on_file(them, "e"))


def maroczy_bind(us, them):
    """Us: c4 and e4, no d-pawn. Them: a d-pawn on d6 or d7, an e-pawn on e6 or e7, no c-pawn."""
    return (has(us, "c4", "e4") and not on_file(us, "d") and bool(them & sq("d6", "d7")) and bool(them & sq("e6", "e7"))
            and not on_file(them, "c"))


def hedgehog(us, them):
    """Us: c4 and e4, no d-pawn. Them: a6, b6, d6 and e6, no c-pawn. (A kind of Maroczy bind: both labels hold.)"""
    return has(us, "c4", "e4") and not on_file(us, "d") and has(them, "a6", "b6", "d6", "e6") and not on_file(them, "c")


def stonewall(us, them):
    """Us: d4, e3 and f4. (Black's is the Dutch Stonewall: d5, e6, f5.)"""
    return has(us, "d4", "e3", "f4")


def small_centre(us, them):
    """Us: e4, no d-pawn. Them: d6, no e-pawn. (The Philidor / Old Indian exchange on d4 or e5: e-pawn against d-pawn.)"""
    return has(us, "e4") and not on_file(us, "d") and has(them, "d6") and not on_file(them, "e")


def kings_indian(white, black):
    """Closed King's Indian, Black as the King's Indian side. White: d5, e4, and a c-pawn on c4 or c5. Black: d6, e5, and
    no pawn on c5 (with c5 it is a Czech Benoni)."""
    return (has(white, "d5", "e4") and bool(white & sq("c4", "c5")) and has(black, "d6", "e5")
            and not black & sq("c5"))


def french_advance(white, black):
    """White: d4 and e5. Black: d5 and e6. (Also the Caro-Kann Advance once Black has played ...e6: both labels hold.)"""
    return has(white, "d4", "e5") and has(black, "d5", "e6")


def caro_slav(white, black):
    """Either of two formations with White on d4 and Black's c-pawn on c6 and e-pawn on e6 or e7. The chain (Slav, Caro
    Advance): Black also has d5. The Caro-Kann main line: Black has no d-pawn and White no e-pawn."""
    if not (has(white, "d4") and has(black, "c6") and black & sq("e6", "e7")):
        return False
    return has(black, "d5") or (not on_file(black, "d") and not on_file(white, "e"))


def benoni(white, black):
    """Modern Benoni. White: d5, an e-pawn, no c-pawn. Black: c5 and d6, no e-pawn."""
    return (has(white, "d5") and bool(on_file(white, "e")) and not on_file(white, "c")
            and has(black, "c5", "d6") and not on_file(black, "e"))


EITHER = (isolated_queens_pawn, hanging_pawns, carlsbad, maroczy_bind, hedgehog, stonewall, small_centre)
BOOK = (kings_indian, french_advance, caro_slav, benoni)
RARE = (isolated_queens_pawn, hanging_pawns, carlsbad, maroczy_bind, hedgehog, kings_indian, benoni)
DEFS = {f.__name__: " ".join(f.__doc__.split()) + (" Either colour." if f in EITHER else " Book colours only.")
        for f in EITHER + BOOK}


def masks(board):
    return board.pieces_mask(chess.PAWN, chess.WHITE), board.pieces_mask(chess.PAWN, chess.BLACK)


def who(rule, board):
    """The colours for which an EITHER rule holds, as written for White."""
    w, b = masks(board)
    out = []
    if rule(w, b):
        out.append(chess.WHITE)
    if rule(chess.flip_vertical(b), chess.flip_vertical(w)):
        out.append(chess.BLACK)
    return out


def labels(board, game=None):
    w, b = masks(board)
    fw, fb = chess.flip_vertical(b), chess.flip_vertical(w)     # Black's pawns as if White's, and White's as if Black's
    out = {f.__name__: bool(f(w, b) or f(fw, fb)) for f in EITHER}
    out.update({f.__name__: bool(f(w, b)) for f in BOOK})
    return out


def rare_structure(board):
    """Whether a structure too rare for plain sampling holds: build_positions.py looks for these in the fresh month."""
    w, b = masks(board)
    fw, fb = chess.flip_vertical(b), chess.flip_vertical(w)
    return any(f(w, b) or (f in EITHER and f(fw, fb)) for f in RARE)
