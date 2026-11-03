"""The opening a game is in, by the Lichess chess-openings list (github.com/lichess-org/chess-openings, a-e.tsv, in
data/transcend/conceptbench/openings/), for positions in moves FIRST_MOVE to LAST_MOVE.

Walk back along the game: the latest position that is in the list names the opening. Positions are compared, not move
orders, so transpositions count. Two concepts per position: eco_<code> (the ECO family, e.g. eco_B90) and
line_<name> (the named line: the list's name up to its first comma, e.g. "Sicilian Defense: Najdorf Variation").
Negative: any other position in the same moves, including one in no listed opening.
"""

import csv
import io
import re

import chess

from bench import DATA

VERSION = 1
FIRST_MOVE, LAST_MOVE = 8, 15
SPARSE = True
DEFS = {}                   # filled as concepts are seen: see define()
_book = None


def line_name(name):
    return name.split(",")[0].strip()


def slug(name):
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")


def define(concept):
    if concept.startswith("eco_"):
        return f"moves {FIRST_MOVE}-{LAST_MOVE}: the latest listed position of the game has ECO {concept[4:]}"
    return f"moves {FIRST_MOVE}-{LAST_MOVE}: the latest listed position of the game is in the line {concept[5:]}"


def book(folder=None):
    """{position key: (ECO, name)} from the five lists. A position listed twice keeps its first name."""
    global _book
    if _book is None:
        _book = {}
        for f in "abcde":
            text = ((folder or DATA / "openings") / f"{f}.tsv").read_text(encoding="utf-8")
            for r in csv.DictReader(io.StringIO(text), delimiter="\t"):
                b = chess.Board()
                for t in r["pgn"].split():
                    if not t[0].isdigit():
                        b.push_san(t)
                _book.setdefault(b.epd(), (r["eco"], r["name"]))
    return _book


def applicable(board):
    return FIRST_MOVE <= board.fullmove_number <= LAST_MOVE


def named(board):
    """The (ECO, name) of the latest listed position of the game, or None."""
    bk = book()
    b = board.copy(stack=True)
    while True:
        hit = bk.get(b.epd())
        if hit:
            return hit
        if not b.move_stack:
            return None
        b.pop()


def labels(board, game=None):
    if not applicable(board):
        return {}
    hit = named(board)
    if hit is None:
        return {}
    return {f"eco_{hit[0]}": True, f"line_{slug(line_name(hit[1]))}": True}
