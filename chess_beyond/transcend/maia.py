"""Maia-2 helpers shared by maia_filter.py and play_elo.py: its board encoding in
numpy and its rating buckets, without importing torch or maia2 (so CPU worker
processes stay light)."""
import chess
import numpy as np


def encode(board):
    """Maia-2's board_to_tensor in numpy (18 x 8 x 8, uint8), for the side to move as White."""
    t = np.zeros((18, 8, 8), dtype=np.uint8)
    for i, piece in enumerate((chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING)):
        for color, off in ((chess.WHITE, 0), (chess.BLACK, 6)):
            for sq in board.pieces(piece, color):
                t[i + off, sq // 8, sq % 8] = 1
    if board.turn == chess.WHITE:
        t[12] = 1
    for i, right in enumerate((board.has_kingside_castling_rights(chess.WHITE),
                               board.has_queenside_castling_rights(chess.WHITE),
                               board.has_kingside_castling_rights(chess.BLACK),
                               board.has_queenside_castling_rights(chess.BLACK))):
        if right:
            t[13 + i] = 1
    # Maia-2 builds its board from a FEN, which only keeps the en-passant square
    # when the capture is legal; a board that played the moves keeps it after any
    # double pawn push.
    if board.ep_square is not None and board.has_legal_en_passant():
        t[17, board.ep_square // 8, board.ep_square % 8] = 1
    return t


def elo_cat(elo):
    """maia2.utils.map_to_category: <1100 -> 0, 1100-1199 -> 1, ..., >=2000 -> 10."""
    return 0 if elo < 1100 else 10 if elo >= 2000 else 1 + (elo - 1100) // 100


def mirror_move(move):
    return chess.Move(chess.square_mirror(move.from_square), chess.square_mirror(move.to_square), move.promotion)
