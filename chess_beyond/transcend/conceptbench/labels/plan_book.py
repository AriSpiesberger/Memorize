"""Book plans over whole games, for the dynamic bench (traj.py). A plan is a structure the plan's side is in, and the moves
that carry it out (Soltis, Pawn Structure Chess; Flores Rios, Chess Structures). plans.py marks a position by whether
the plan's first move comes within 10 plies; here a plan is an episode, a stretch of a game:

    start  LEAD plies before the plan's first move (not before the structure began), the first move played while the
           side is in the structure
    end    the plan's last move: each further move of the plan within GAP plies of the one before
    valid  at least MIN_MOVES of its moves, at least MIN_DISTINCT different ones, and its REQUIRED ones

Positions in an episode are positives. Positions in the structure with no episode coming are negatives (so negatives
share the structure, as in plans.py). The rest has no label: out of the structure, a chain of plan moves that is not a
valid episode, or too near the end of the known moves to tell whether the plan comes.

Every square is written for the plan's side as if it were White: Black's ...f5 is f4 here (the board mirrored by rank).
"""

from collections import namedtuple

import chess

from bench import ENDGAME_MAX_PIECES, VALUES
from . import structures as st
from .structures import sq

VERSION = 1
LEAD = 10           # plies before the first plan move that count as the plan
GAP = 10            # a plan's next move within this many plies of its previous one
MIN_RUN = 4         # an episode shorter than this is no label (as for the other concepts)

flip = chess.flip_vertical
P, N, B, R, Q, K = chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING


def rel_masks(board, c):
    """(this side's pawns, the other's), the board mirrored if c is Black."""
    us, them = board.pieces_mask(P, c), board.pieces_mask(P, not c)
    return (us, them) if c == chess.WHITE else (flip(us), flip(them))


def rel_sq(s, c):
    return s if c == chess.WHITE else chess.square_mirror(s)


def piece_at(board, c, name):
    """The piece on a square named as if c were White, as (type, ours?) or None."""
    p = board.piece_at(rel_sq(chess.parse_square(name), c))
    return None if p is None else (p.piece_type, p.color == c)


# ---------------------------------------------------------------- structures, for the plan's side c
def owner(rule):
    """The plan's side is the rule's us."""
    return lambda board, c: rule(*rel_masks(board, c))


def opponent(rule):
    """The plan's side is the rule's them: the rule holds as written for the other side."""
    return lambda board, c: rule(*rel_masks(board, not c))


def book(rule, color):
    """A one-colour defence (rule(white, black)); the plan belongs to `color`."""
    return lambda board, c: c == color and rule(board.pieces_mask(P, chess.WHITE), board.pieces_mask(P, chess.BLACK))


def both(*preds):
    return lambda board, c: all(p(board, c) for p in preds)


def pawns_on(*names):
    """The plan's side has a pawn on one of these squares."""
    return lambda board, c: bool(rel_masks(board, c)[0] & sq(*names))


def sicilian(them_extra):
    """Open Sicilian, us the side with e4: e4, no d-pawn, a c-pawn on c2 or c3. Them: d6, no c-pawn, and them_extra."""
    def rule(us, them):
        return (st.has(us, "e4") and not st.on_file(us, "d") and bool(us & sq("c2", "c3"))
                and st.has(them, "d6") and not st.on_file(them, "c") and them_extra(them))
    return rule


scheveningen = sicilian(lambda them: st.has(them, "e6"))
najdorf = sicilian(lambda them: st.has(them, "e5"))
dragon_pawns = sicilian(lambda them: st.has(them, "g6", "e7"))


def dragon(board, c):
    """Dragon, the plan's side as White: the Sicilian above with Black's g6 and e7, and Black's bishop on g7."""
    return dragon_pawns(*rel_masks(board, c)) and piece_at(board, c, "g7") == (B, False)


def dragon_them(board, c):
    return dragon_pawns(*rel_masks(board, not c)) and piece_at(board, not c, "g7") == (B, False)


def big_centre(us, them):
    """Us: d4 and e4. Them: no d-pawn, no e-pawn ahead of e7, a c-pawn on c7 or c5 (the Grunfeld centre)."""
    return st.has(us, "d4", "e4") and not st.on_file(them, "d") and not them & sq("e6", "e5") and bool(them & sq("c7", "c5"))


def king_wing(board, c):
    """'q' if c's king is on files a-c, 'k' on f-h, else None."""
    f = chess.square_file(board.king(c))
    return "q" if f <= 2 else "k" if f >= 5 else None


def opposite_castling(board, c):
    """The kings on opposite wings, each on its first two ranks."""
    wings = king_wing(board, c), king_wing(board, not c)
    home = all(chess.square_rank(rel_sq(board.king(x), x)) <= 1 for x in (c, not c))
    return None not in wings and wings[0] != wings[1] and home


def fianchetto_target(board, c):
    """The other side's king on g8 behind a fianchetto: pawn g6, bishop g7 (as if c were White)."""
    return (piece_at(board, c, "g8") == (K, False) and piece_at(board, c, "g6") == (P, False)
            and piece_at(board, c, "g7") == (B, False))


def queenside_majority(board, c):
    us, them = rel_masks(board, c)
    qs = chess.BB_FILE_A | chess.BB_FILE_B | chess.BB_FILE_C | chess.BB_FILE_D
    return st.count(us & qs) > st.count(them & qs)


def endgame(board, c):
    return sum(len(board.pieces(t, x)) for t in VALUES if t != P for x in chess.COLORS) <= ENDGAME_MAX_PIECES


def rook_middlegame(board, c):
    return bool(board.pieces(R, c)) and board.fullmove_number > 10


# ---------------------------------------------------------------- the plan's moves
def mv(piece, to, frm=None, capture=None, captured=None):
    """A move of the plan's side (squares as if White): a piece of this type to one of `to`; optionally from one of
    `frm`, a capture or not, capturing this type."""
    to_m, frm_m = sq(*to.split()), sq(*frm.split()) if frm else None

    def match(board, move, c):
        if board.piece_type_at(move.from_square) != piece:
            return False
        if not chess.BB_SQUARES[rel_sq(move.to_square, c)] & to_m:
            return False
        if frm_m is not None and not chess.BB_SQUARES[rel_sq(move.from_square, c)] & frm_m:
            return False
        if capture is not None and board.is_capture(move) != capture:
            return False
        if captured is not None and board.piece_type_at(move.to_square) != captured:
            return False
        return True
    return match


def storm_toward_king(board, move, c):
    """A pawn move on the wing of the other side's king (files f-h or a-c)."""
    if board.piece_type_at(move.from_square) != P:
        return False
    wing = king_wing(board, not c)
    f = chess.square_file(move.from_square)
    return (wing == "k" and f >= 5) or (wing == "q" and f <= 2)


def queenside_push(board, move, c):
    return board.piece_type_at(move.from_square) == P and chess.square_file(move.from_square) <= 2


def centre_distance(s):
    return max(abs(chess.square_file(s) * 2 - 7), abs(chess.square_rank(s) * 2 - 7)) // 2


def king_to_centre(board, move, c):
    return board.piece_type_at(move.from_square) == K and centre_distance(move.to_square) < centre_distance(move.from_square)


Plan = namedtuple("Plan", "structure marks min_moves min_distinct required doc")


def plan(structure, marks, doc, min_moves=1, min_distinct=1, required=()):
    return Plan(structure, marks, min_moves, min_distinct, tuple(required), doc)


W, BL = chess.WHITE, chess.BLACK
carlsbad_minority_side = both(owner(st.carlsbad), pawns_on("b2", "b3"))
kid_black = both(book(st.kings_indian, BL), pawns_on("f2", "f3"), pawns_on("g2", "g3"))

PLANS = {
    # Carlsbad: us the minority side (d4, e3, b-pawn, no c-pawn against d5, c6)
    "carlsbad_minority": plan(carlsbad_minority_side,
                              {"b4": mv(P, "b4", "b2 b3"), "b5": mv(P, "b5"), "bxc6": mv(P, "c6", "b5", capture=True)},
                              "Carlsbad, the minority side: b4, then b5 and bxc6", required=["b4"]),
    "carlsbad_central_break": plan(owner(st.carlsbad), {"f3": mv(P, "f3", "f2"), "e4": mv(P, "e4", "e3")},
                                   "Carlsbad, the minority side: f3 and the e3-e4 break", required=["e4"]),
    "carlsbad_pillsbury": plan(owner(st.carlsbad), {"Ne5": mv(N, "e5"), "f4": mv(P, "f4", "f2 f3")},
                               "Carlsbad, the minority side: the Pillsbury attack, Ne5 and f4", min_distinct=2),
    "carlsbad_kingside_counter": plan(opponent(st.carlsbad), {"Ne4": mv(N, "e5"), "f5": mv(P, "f4", "f2 f3")},
                                      "Carlsbad, the majority side: ...Ne4 and ...f5 on the kingside"),
    # isolated queen's pawn: us the side with it
    "iqp_break": plan(owner(st.isolated_queens_pawn), {"d5": mv(P, "d5", "d4")}, "IQP: the d4-d5 break", required=["d5"]),
    "iqp_kingside_attack": plan(owner(st.isolated_queens_pawn),
                                {"Ne5": mv(N, "e5"), "rook_lift": mv(R, "e3 f3"), "rook_swing": mv(R, "g3 h3"),
                                 "battery": mv(Q, "d3 c2"), "bishop_b1h7": mv(B, "c2 b1 d3")},
                                "IQP: kingside attack, two of Ne5, a rook lift to e3/f3 and over to g3/h3, Qd3/Qc2, Bc2/Bb1/Bd3",
                                min_distinct=2),
    "iqp_blockade": plan(opponent(st.isolated_queens_pawn), {"blockade": mv(N, "d4"), "blockade_b": mv(B, "d4"), "blockade_q": mv(Q, "d4")},
                         "IQP, the side against it: a piece to the blockade square in front of the pawn"),
    # hanging pawns
    "hanging_pawns_advance": plan(owner(st.hanging_pawns), {"c5": mv(P, "c5", "c4"), "d5": mv(P, "d5", "d4")},
                                  "Hanging pawns: one of them advances, c4-c5 or d4-d5"),
    "hanging_pawns_levers": plan(opponent(st.hanging_pawns), {"e5": mv(P, "e4", "e2 e3"), "b5": mv(P, "b4", "b2 b3")},
                                 "Hanging pawns, the side against them: the levers ...e5 or ...b5"),
    # King's Indian
    "kings_indian_storm": plan(kid_black, {"f5": mv(P, "f4", "f2 f3"), "f4": mv(P, "f5", "f4"), "g5": mv(P, "g4", "g2 g3"),
                                           "g4": mv(P, "g5", "g4")},
                               "Closed King's Indian, Black: the kingside storm, two of ...f5, ...f4, ...g5, ...g4", min_distinct=2),
    "kings_indian_queenside": plan(book(st.kings_indian, W), {"b4": mv(P, "b4", "b2 b3"), "c5": mv(P, "c5", "c4"),
                                                              "cxd6": mv(P, "d6", "c5", capture=True)},
                                   "Closed King's Indian, White: the queenside break c4-c5, with b4 and cxd6", required=["c5"]),
    # Benoni
    "benoni_b5": plan(book(st.benoni, BL), {"b5": mv(P, "b4", "b2 b3"), "b4": mv(P, "b5", "b4")},
                      "Modern Benoni, Black: queenside expansion ...b5 (then ...b4)", required=["b5"]),
    "benoni_e5": plan(book(st.benoni, W), {"e5": mv(P, "e5", "e4")}, "Modern Benoni, White: the e4-e5 break", required=["e5"]),
    "benoni_f4_e5": plan(book(st.benoni, W), {"f4": mv(P, "f4", "f2 f3"), "e5": mv(P, "e5", "e4")},
                         "Modern Benoni, White: f4 and then e5", min_distinct=2),
    # French Advance
    "french_c5": plan(book(st.french_advance, BL), {"c5": mv(P, "c4", "c2 c3")}, "French Advance, Black: the ...c5 break"),
    "french_f6": plan(book(st.french_advance, BL), {"f6": mv(P, "f3", "f2"), "fxe5": mv(P, "e4", "f3", capture=True)},
                      "French Advance, Black: the ...f6 break (then ...fxe5)", required=["f6"]),
    "french_d4_pressure": plan(book(st.french_advance, BL), {"Qb6": mv(Q, "b3"), "Nc6": mv(N, "c3"), "Nf5": mv(N, "f4")},
                               "French Advance, Black: pressure on d4, two of ...Qb6, ...Nc6, ...Nf5", min_distinct=2),
    "french_kingside": plan(book(st.french_advance, W), {"f4": mv(P, "f4", "f2 f3"), "f5": mv(P, "f5", "f4")},
                            "French Advance, White: kingside expansion f4-f5", min_distinct=2),
    # Caro-Kann / Slav
    "caro_slav_c5": plan(book(st.caro_slav, BL), {"c5": mv(P, "c4", "c3")}, "Caro-Kann / Slav, Black: the ...c5 break"),
    "caro_slav_e5": plan(book(st.caro_slav, BL), {"e5": mv(P, "e4", "e2 e3")}, "Caro-Kann / Slav, Black: the ...e5 break"),
    "caro_slav_space": plan(book(st.caro_slav, W), {"c5": mv(P, "c5", "c4"), "e5": mv(P, "e5", "e4")},
                            "Caro-Kann / Slav, White: space, c4-c5 or e4-e5"),
    # Maroczy bind and hedgehog: the plan's side is the one bound
    "maroczy_break": plan(both(opponent(st.maroczy_bind), pawns_on("d2", "d3"), pawns_on("b2", "b3")),
                          {"b5": mv(P, "b4", "b2 b3"), "d5": mv(P, "d4", "d2 d3")}, "Maroczy bind, the side bound: ...b5 or ...d5"),
    "maroczy_f5": plan(opponent(st.maroczy_bind), {"f5": mv(P, "f4", "f2 f3")}, "Maroczy bind, the side bound: the ...f5 break"),
    "hedgehog_break": plan(opponent(st.hedgehog), {"b5": mv(P, "b4", "b3"), "d5": mv(P, "d4", "d3")},
                           "Hedgehog: the ...b5 or ...d5 break"),
    # Stonewall: us d4 e3 f4
    "stonewall_attack": plan(owner(st.stonewall), {"Ne5": mv(N, "e5"), "g4": mv(P, "g4"), "g5": mv(P, "g5"), "Rf3": mv(R, "f3"),
                                                   "Rh3": mv(R, "h3")},
                             "Stonewall: Ne5 and a kingside attack, g4/g5 or a rook to f3/h3", min_distinct=2, required=["Ne5"]),
    "stonewall_c5_break": plan(opponent(st.stonewall), {"c5": mv(P, "c4", "c2 c3")}, "Stonewall, the side against it: ...c5"),
    # small centre: us e4 against d6
    "small_centre_f4": plan(owner(st.small_centre), {"f4": mv(P, "f4", "f2 f3")}, "Small centre, the e4 side: f4"),
    "small_centre_d5": plan(opponent(st.small_centre), {"d5": mv(P, "d4", "d3")}, "Small centre, the d6 side: the ...d5 break"),
    "small_centre_f5": plan(opponent(st.small_centre), {"f5": mv(P, "f4", "f2 f3")}, "Small centre, the d6 side: the ...f5 break"),
    # Open Sicilian
    "scheveningen_english_attack": plan(owner(scheveningen), {"g4": mv(P, "g4", "g2 g3"), "g5": mv(P, "g5"), "f4": mv(P, "f4", "f2 f3"),
                                                              "f5": mv(P, "f5"), "h4": mv(P, "h4", "h2 h3")},
                                        "Scheveningen, White: kingside pawn storm, two of g4, g5, f4, f5, h4", min_distinct=2),
    "scheveningen_b5": plan(opponent(scheveningen), {"b5": mv(P, "b4", "b2 b3")}, "Scheveningen, Black: ...b5 expansion"),
    "scheveningen_d5": plan(opponent(scheveningen), {"d5": mv(P, "d4", "d3")}, "Scheveningen, Black: the ...d5 break"),
    "najdorf_nd5": plan(owner(najdorf), {"Nd5": mv(N, "d5")}, "Najdorf / ...e5 Sicilian, White: a knight to the d5 hole"),
    "najdorf_d5": plan(opponent(najdorf), {"d5": mv(P, "d4", "d3")}, "Najdorf / ...e5 Sicilian, Black: the ...d5 break"),
    "najdorf_b5": plan(opponent(najdorf), {"b5": mv(P, "b4", "b2 b3")}, "Najdorf / ...e5 Sicilian, Black: ...b5 expansion"),
    "dragon_h_storm": plan(dragon, {"h4": mv(P, "h4", "h2 h3"), "h5": mv(P, "h5", "h4")}, "Dragon, White: h4-h5", min_distinct=2),
    "dragon_b5": plan(dragon_them, {"b5": mv(P, "b4", "b2 b3")}, "Dragon, Black: ...b5"),
    "dragon_exchange_sac": plan(dragon_them, {"Rxc3": mv(R, "c6", capture=True, captured=N)},
                                "Dragon, Black: the exchange sacrifice ...Rxc3"),
    # big centre (Grunfeld)
    "big_centre_d5": plan(owner(big_centre), {"d5": mv(P, "d5", "d4")}, "Big centre, its side: the d4-d5 advance"),
    "big_centre_c5": plan(opponent(big_centre), {"c5": mv(P, "c4", "c2 c3")}, "Big centre, the side against it: ...c5 pressure"),
    # in any structure
    "opposite_castling_storm": plan(opposite_castling, {"push": storm_toward_king},
                                    "Kings on opposite wings: at least two pawn moves on the other king's wing", min_moves=2),
    "fianchetto_h_storm": plan(fianchetto_target, {"h4": mv(P, "h4", "h2 h3"), "h5": mv(P, "h5", "h4")},
                               "Against a fianchettoed king (g8, g6, Bg7): h4-h5", min_distinct=2),
    "queenside_majority_push": plan(queenside_majority, {"push": queenside_push},
                                    "A queenside majority (files a-d): at least two pawn moves on files a-c", min_moves=2),
    "king_centralisation": plan(endgame, {"step": king_to_centre}, "Endgame: at least three king moves toward the centre",
                                min_moves=3),
    "rook_seventh": plan(rook_middlegame, {"R7": mv(R, "a7 b7 c7 d7 e7 f7 g7 h7")}, "After move 10: a rook to the seventh rank"),
}
NAMES = {    # short plain names for pages; the opening is in DEFS
    "carlsbad_minority": "Minority attack", "carlsbad_central_break": "e4 break", "carlsbad_pillsbury": "Pillsbury attack",
    "carlsbad_kingside_counter": "Kingside counterattack", "iqp_break": "d5 break", "iqp_kingside_attack": "Kingside attack",
    "iqp_blockade": "Blockade", "hanging_pawns_advance": "Push the hanging pawns", "hanging_pawns_levers": "Hit the hanging pawns",
    "kings_indian_storm": "Kingside pawn storm", "kings_indian_queenside": "Queenside break", "benoni_b5": "b5 push",
    "benoni_e5": "e5 break", "benoni_f4_e5": "f4 then e5", "french_c5": "c5 break", "french_f6": "f6 break",
    "french_d4_pressure": "Pile up on d4", "french_kingside": "f4-f5 push", "caro_slav_c5": "c5 break", "caro_slav_e5": "e5 break",
    "caro_slav_space": "Grab space", "maroczy_break": "Break free", "maroczy_f5": "f5 break", "hedgehog_break": "Break free",
    "stonewall_attack": "Stonewall attack", "stonewall_c5_break": "c5 break", "small_centre_f4": "f4 push",
    "small_centre_d5": "d5 break", "small_centre_f5": "f5 break", "scheveningen_english_attack": "Kingside pawn storm",
    "scheveningen_b5": "b5 push", "scheveningen_d5": "d5 break", "najdorf_nd5": "Knight to d5", "najdorf_d5": "d5 break",
    "najdorf_b5": "b5 push", "dragon_h_storm": "h-pawn storm", "dragon_b5": "b5 push", "dragon_exchange_sac": "Exchange sacrifice",
    "big_centre_d5": "d5 push", "big_centre_c5": "c5 break", "opposite_castling_storm": "Pawn storm",
    "fianchetto_h_storm": "h-pawn storm", "queenside_majority_push": "Push the majority", "king_centralisation": "King to the centre",
    "rook_seventh": "Rook to the 7th",
}
DEFS = {f"plan_{k}": p.doc + f". Episode: from {LEAD} plies before its first move (in the structure) to its last move, each "
        f"within {GAP} plies of the one before; in the structure with no episode coming: negative." for k, p in PLANS.items()}


def episodes(boards, moves, n_known):
    """boards: the positions of one game, boards[p] before moves[p]; n_known: plies known in all (labels need LEAD more).
    -> {concept: list of 1 / 0 / None per position}."""
    n = len(boards)
    out = {}
    for name, p in PLANS.items():
        lab = [None] * n
        for c in chess.COLORS:
            inside = [p.structure(b, c) for b in boards]
            marks = []
            for i, (b, m) in enumerate(zip(boards, moves)):
                if m is not None and b.turn == c:
                    hit = next((k for k, f in p.marks.items() if f(b, m, c)), None)
                    if hit:
                        marks.append((i, hit))
            pos, amb, j = set(), set(), 0
            while j < len(marks):
                i0, _ = marks[j]
                if not inside[i0]:
                    j += 1
                    continue
                chain = [marks[j]]
                j += 1
                while j < len(marks) and marks[j][0] - chain[-1][0] <= GAP:
                    chain.append(marks[j])
                    j += 1
                ids = {k for _, k in chain}
                start = i0
                while start > 0 and inside[start - 1] and i0 - start < LEAD:
                    start -= 1
                span = range(start, chain[-1][0] + 1)
                ok = (len(chain) >= p.min_moves and len(ids) >= p.min_distinct and set(p.required) <= ids
                      and len(span) >= MIN_RUN)
                (pos if ok else amb).update(span)
            for i in range(n):
                if i in pos:
                    lab[i] = 1
                elif i in amb or lab[i] == 1:
                    continue
                elif inside[i] and i + LEAD <= n_known and lab[i] is None:
                    lab[i] = 0
            for i in amb:
                if lab[i] == 0:
                    lab[i] = None
        out[f"plan_{name}"] = lab
    return out
