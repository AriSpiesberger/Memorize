"""Chess predicates: plain yes/no facts about a position and the move played from it.

They are the vocabulary latent explanations are written in (explain.py): an explanation is one
predicate, or two joined by "and", that predicts when a latent fires. Everything is computed with
python-chess (no engine), from the point of view of the side to move: "we" move next, "they" just
moved.

    from predicates import NAMES, TEXT, features
    features(board, move)          # -> list of bools, one per NAMES entry (move may be None)
"""
import chess

VALUE = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 100}
PIECES = [(chess.PAWN, "pawn"), (chess.KNIGHT, "knight"), (chess.BISHOP, "bishop"), (chess.ROOK, "rook"),
          (chess.QUEEN, "queen"), (chess.KING, "king")]

# (name, readable text): the order features() returns them in
DEFS = [
    # the game
    ("white_to_move", "White is to move"),
    ("opening", "the opening (move 10 or earlier)"),
    ("middlegame", "the middlegame"),
    ("endgame", "an endgame (6 or fewer pieces besides kings and pawns)"),
    ("queens_off", "the queens are off"),
    # material, in pawns (1, 3, 3, 5, 9)
    ("material_up", "the side to move is up material (2+ pawns' worth)"),
    ("material_down", "the side to move is down material (2+ pawns' worth)"),
    ("material_level", "material is level"),
    # threats
    ("in_check", "the side to move is in check"),
    ("our_piece_hanging", "one of our pieces (knight or more) is attacked and undefended"),
    ("their_piece_hanging", "one of their pieces (knight or more) is attacked by us and undefended"),
    ("our_piece_attacked_by_lower", "one of our pieces is attacked by a cheaper piece"),
    ("their_piece_attacked_by_lower", "one of their pieces is attacked by a cheaper piece of ours"),
    ("we_have_mate_in_1", "we have mate in one"),
    ("they_threaten_mate", "they threaten mate in one"),
    ("we_have_a_check", "we have a checking move"),
    ("we_have_a_fork", "we have a move that attacks two of their pieces (knight or more, or the king)"),
    ("our_piece_pinned", "one of our pieces is pinned to our king"),
    ("their_piece_pinned", "one of their pieces is pinned to their king"),
    # kings
    ("we_can_castle", "we still have castling rights"),
    ("they_can_castle", "they still have castling rights"),
    ("our_king_exposed", "3+ squares around our king are attacked by them"),
    ("their_king_exposed", "3+ squares around their king are attacked by us"),
    ("our_back_rank_weak", "our king is boxed in on the back rank and they have a rook or queen"),
    ("their_back_rank_weak", "their king is boxed in on the back rank and we have a rook or queen"),
    # pawns
    ("we_have_a_passed_pawn", "we have a passed pawn"),
    ("they_have_a_passed_pawn", "they have a passed pawn"),
    ("we_have_an_advanced_passer", "we have a passed pawn on the 6th or 7th rank"),
    ("they_have_an_advanced_passer", "they have a passed pawn on their 6th or 7th rank"),
    # their last move
    ("they_just_captured", "their last move was a capture"),
    ("they_just_checked", "their last move gave check"),
] + [
    # the move played
    (f"move_{name}", f"the move is a {name} move") for _, name in PIECES
] + [
    ("move_capture", "the move is a capture"),
    ("move_recapture", "the move recaptures on the square they just captured on"),
    ("move_wins_material", "the move takes a hanging piece or a more valuable one"),
    ("move_trade", "the move captures a piece of equal value"),
    ("move_check", "the move gives check"),
    ("move_mates", "the move is checkmate"),
    ("move_castles", "the move castles"),
    ("move_promotes", "the move promotes a pawn"),
    ("move_pawn_two", "the move is a two-square pawn push"),
    ("move_develops", "the move develops a knight or bishop off the back rank"),
    ("move_retreats", "the move retreats a piece toward our side"),
    ("move_attacks_piece", "the moved piece attacks one of their pieces that is hanging or worth more"),
    ("move_hangs_piece", "the moved piece can be taken for free or by a cheaper piece"),
    ("move_escapes_attack", "the move takes an attacked piece of ours to safety"),
]
NAMES = [n for n, _ in DEFS]
TEXT = dict(DEFS)


def material(b, color):
    return sum(VALUE[p.piece_type] for p in b.piece_map().values() if p.color == color and p.piece_type != chess.KING)


def hanging(b, sq):
    """The piece on sq is attacked by the other side and not defended by its own."""
    p = b.piece_at(sq)
    return bool(b.attackers(not p.color, sq)) and not b.attackers(p.color, sq)


def attacked_by_lower(b, sq):
    p = b.piece_at(sq)
    return any(VALUE[b.piece_type_at(a)] < VALUE[p.piece_type] for a in b.attackers(not p.color, sq))


def in_danger(b, sq):
    return hanging(b, sq) or attacked_by_lower(b, sq)


def passed(b, sq):
    """A pawn with no enemy pawn ahead of it on its own or the adjacent files."""
    p = b.piece_at(sq)
    f, r = chess.square_file(sq), chess.square_rank(sq)
    ahead = range(r + 1, 8) if p.color == chess.WHITE else range(r - 1, -1, -1)
    for ff in (f - 1, f, f + 1):
        if 0 <= ff < 8 and any(b.piece_at(chess.square(ff, rr)) == chess.Piece(chess.PAWN, not p.color) for rr in ahead):
            return False
    return True


def king_exposed(b, color):
    k = b.king(color)
    return k is not None and sum(1 for s in chess.SquareSet(chess.BB_KING_ATTACKS[k]) if b.is_attacked_by(not color, s)) >= 3


def back_rank_weak(b, color):
    """King on its back rank, every square in front of it blocked by its own pieces, and the
    other side has a rook or queen."""
    k = b.king(color)
    home = 0 if color == chess.WHITE else 7
    if k is None or chess.square_rank(k) != home:
        return False
    if not (b.pieces(chess.ROOK, not color) or b.pieces(chess.QUEEN, not color)):
        return False
    f, step = chess.square_file(k), 1 if color == chess.WHITE else -1
    front = [chess.square(ff, home + step) for ff in (f - 1, f, f + 1) if 0 <= ff < 8]
    return all(b.piece_at(s) is not None and b.piece_at(s).color == color for s in front)


def side_facts(b, us):
    them = not us
    ours = [s for s, p in b.piece_map().items() if p.color == us and p.piece_type != chess.KING]
    theirs = [s for s, p in b.piece_map().items() if p.color == them and p.piece_type != chess.KING]
    big = lambda s: b.piece_type_at(s) != chess.PAWN
    passers = lambda c: [s for s in b.pieces(chess.PAWN, c) if passed(b, s)]
    adv = lambda c, s: chess.square_rank(s) >= 5 if c == chess.WHITE else chess.square_rank(s) <= 2
    return dict(
        our_piece_hanging=any(big(s) and hanging(b, s) for s in ours),
        their_piece_hanging=any(big(s) and hanging(b, s) for s in theirs),
        our_piece_attacked_by_lower=any(attacked_by_lower(b, s) for s in ours),
        their_piece_attacked_by_lower=any(attacked_by_lower(b, s) for s in theirs),
        our_piece_pinned=any(b.is_pinned(us, s) for s in ours),
        their_piece_pinned=any(b.is_pinned(them, s) for s in theirs),
        we_can_castle=b.has_castling_rights(us),
        they_can_castle=b.has_castling_rights(them),
        our_king_exposed=king_exposed(b, us),
        their_king_exposed=king_exposed(b, them),
        our_back_rank_weak=back_rank_weak(b, us),
        their_back_rank_weak=back_rank_weak(b, them),
        we_have_a_passed_pawn=bool(passers(us)),
        they_have_a_passed_pawn=bool(passers(them)),
        we_have_an_advanced_passer=any(adv(us, s) for s in passers(us)),
        they_have_an_advanced_passer=any(adv(them, s) for s in passers(them)),
    )


def legal_facts(b, us):
    """Facts that need a look at every legal move: mate in one, a check, a fork."""
    mate = check = fork = False
    for mv in b.legal_moves:
        if b.gives_check(mv):
            check = True
            b.push(mv)
            mate = mate or b.is_checkmate()
            b.pop()
        if not fork:
            b.push(mv)
            hit = [s for s in b.attacks(mv.to_square)
                   if b.piece_at(s) is not None and b.piece_at(s).color != us and b.piece_type_at(s) != chess.PAWN]
            if len(hit) >= 2 and not in_danger(b, mv.to_square):
                fork = True
            b.pop()
        if mate and fork:
            break
    return dict(we_have_mate_in_1=mate, we_have_a_check=check, we_have_a_fork=fork)


def threat_of_mate(b):
    """If they could move again now, would they have mate in one?"""
    if b.is_check():
        return False
    b.push(chess.Move.null())
    try:
        for mv in b.legal_moves:
            if b.gives_check(mv):
                b.push(mv)
                m = b.is_checkmate()
                b.pop()
                if m:
                    return True
        return False
    finally:
        b.pop()


def move_facts(b, mv, us):
    f = {f"move_{name}": False for _, name in PIECES}
    if mv is None:
        return dict(f, move_capture=False, move_recapture=False, move_wins_material=False, move_trade=False,
                    move_check=False, move_mates=False, move_castles=False, move_promotes=False, move_pawn_two=False,
                    move_develops=False, move_retreats=False, move_attacks_piece=False, move_hangs_piece=False,
                    move_escapes_attack=False)
    pt = b.piece_type_at(mv.from_square)
    f[f"move_{chess.piece_name(pt)}"] = True
    cap = b.is_capture(mv)
    victim = chess.PAWN if b.is_en_passant(mv) else b.piece_type_at(mv.to_square)
    last = b.peek() if b.move_stack else None
    prev = b.copy(stack=1)
    if last is not None:
        prev.pop()
    rank = lambda s: chess.square_rank(s) if us == chess.WHITE else 7 - chess.square_rank(s)
    was_danger = pt != chess.KING and in_danger(b, mv.from_square)
    target_hanging = cap and victim is not None and not b.attackers(not us, mv.to_square)
    f.update(
        move_capture=cap,
        move_recapture=cap and last is not None and last.to_square == mv.to_square and prev.is_capture(last),
        move_wins_material=cap and victim is not None and (target_hanging or VALUE[victim] > VALUE[pt]),
        move_trade=cap and victim is not None and VALUE[victim] == VALUE[pt],
        move_check=b.gives_check(mv),
        move_castles=b.is_castling(mv),
        move_promotes=mv.promotion is not None,
        move_pawn_two=pt == chess.PAWN and abs(chess.square_rank(mv.to_square) - chess.square_rank(mv.from_square)) == 2,
        move_develops=pt in (chess.KNIGHT, chess.BISHOP) and rank(mv.from_square) == 0 and rank(mv.to_square) > 0,
        move_retreats=pt not in (chess.PAWN, chess.KING) and rank(mv.to_square) < rank(mv.from_square),
    )
    b.push(mv)
    try:
        f["move_mates"] = b.is_checkmate()
        t = mv.to_square
        hits = [s for s in b.attacks(t) if b.piece_at(s) is not None and b.piece_at(s).color != us
                and b.piece_type_at(s) != chess.KING]
        f["move_attacks_piece"] = any(hanging(b, s) or VALUE[b.piece_type_at(s)] > VALUE[b.piece_type_at(t)] for s in hits)
        f["move_hangs_piece"] = b.piece_type_at(t) != chess.KING and in_danger(b, t)
        f["move_escapes_attack"] = was_danger and not f["move_hangs_piece"]
    finally:
        b.pop()
    return f


def features(board, move=None):
    """One bool per NAMES entry for this position (side to move = "we") and the move played from it."""
    b = board.copy(stack=2)
    us = b.turn
    minor_major = sum(1 for p in b.piece_map().values() if p.piece_type not in (chess.PAWN, chess.KING))
    d = material(b, us) - material(b, not us)
    last = b.peek() if b.move_stack else None
    prev_capture = prev_check = False
    if last is not None:
        prev_check = b.is_check()
        b.pop()
        prev_capture = b.is_capture(last)
        b.push(last)
    v = dict(
        white_to_move=us == chess.WHITE,
        opening=b.fullmove_number <= 10,
        endgame=minor_major <= 6,
        middlegame=b.fullmove_number > 10 and minor_major > 6,
        queens_off=not b.pieces(chess.QUEEN, chess.WHITE) and not b.pieces(chess.QUEEN, chess.BLACK),
        material_up=d >= 2,
        material_down=d <= -2,
        material_level=d == 0,
        in_check=b.is_check(),
        they_threaten_mate=threat_of_mate(b),
        they_just_captured=prev_capture,
        they_just_checked=prev_check,
    )
    v.update(side_facts(b, us))
    v.update(legal_facts(b, us))
    v.update(move_facts(b, move, us))
    return [bool(v[n]) for n in NAMES]
