"""What every conceptbench script shares: where things live, game phase, material, the split, a prompt <-> board. No
torch here: the labelling workers import this."""

import sys
import zlib
from pathlib import Path

import chess

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # chess_beyond/
import paths  # noqa: E402  also puts transcend/'s folders on sys.path

DATA = paths.DATA / "transcend" / "conceptbench"
RUNS = paths.RUNS / "transcend" / "conceptbench"
RESULTS = paths.ROOT / "results" / "transcend" / "conceptbench"
POSITIONS = DATA / "positions.parquet"
LABELS = DATA / "labels.parquet"
COUNTS = DATA / "label_counts.json"
CONCEPTS = DATA / "concepts"
MANIFEST = CONCEPTS / "manifest.json"

VALUES = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}
OPENING_LAST_MOVE = 10      # opening: up to this move number, unless already an endgame
ENDGAME_MAX_PIECES = 6      # endgame: at most this many queens, rooks, bishops and knights in all (shared.middlegame's line)
PHASES = ("opening", "middlegame", "endgame")
TEST_SHARE = 2              # of 10 hash buckets: 20% of games are test


def material(board, color):
    """Pawn units of one side, kings aside."""
    return sum(VALUES[t] * len(board.pieces(t, color)) for t in VALUES)


def phase_of(board):
    pieces = sum(len(board.pieces(t, c)) for t in VALUES if t != chess.PAWN for c in chess.COLORS)
    if pieces <= ENDGAME_MAX_PIECES:
        return "endgame"
    return "opening" if board.fullmove_number <= OPENING_LAST_MOVE else "middlegame"


def split_of(game_id):
    """fit / test by game."""
    return "test" if zlib.crc32(game_id.encode()) % 10 < TEST_SHARE else "fit"


def prompt_of(sans):
    """pgn_model.prompt without replaying the game: the moves so far, ready for the side to move."""
    parts = [f"{i // 2 + 1}.{s}" if i % 2 == 0 else s for i, s in enumerate(sans)]
    text = ";" + " ".join(parts)
    n = len(sans)
    if n == 0:
        return text + "1."
    return text + (f" {n // 2 + 1}." if n % 2 == 0 else " ")


def sans_of(prompt):
    """The SAN moves of a prompt (or of any ';1.e4 e5 2.Nf3 ' movetext)."""
    sans = []
    for t in prompt.lstrip(";").split():
        s = t.split(".", 1)[1] if "." in t else t
        if s:
            sans.append(s)
    return sans


def board_of(prompt):
    """The board after a prompt, with its move stack."""
    b = chess.Board()
    for s in sans_of(prompt):
        b.push_san(s)
    return b
