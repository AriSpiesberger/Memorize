"""Shared pieces: move vocabulary, board encoding, model, data loading.

Convention: every position is shown to the model from the side to move.
If black is to move, the board is mirrored (colours swapped, ranks flipped),
so the model always "plays white". Moves are mirrored the same way.
Stored data keeps both the real UCI move and the model-frame ("m_") move.
"""
import json

import chess
import torch
import torch.nn as nn

# ----------------------------------------------------------------- moves
def _build_vocab():
    moves = []
    for frm in range(64):
        fr, ff = divmod(frm, 8)
        for to in range(64):
            if to == frm:
                continue
            tr, tf = divmod(to, 8)
            dr, df = tr - fr, tf - ff
            queen_like = dr == 0 or df == 0 or abs(dr) == abs(df)
            knight = (abs(dr), abs(df)) in {(1, 2), (2, 1)}
            if queen_like or knight:
                moves.append(chess.Move(frm, to).uci())
    # promotions (model frame: always white, rank 7 -> rank 8)
    for f in range(8):
        frm = chess.square(f, 6)
        for df in (-1, 0, 1):
            if 0 <= f + df < 8:
                to = chess.square(f + df, 7)
                for p in "qrbn":
                    moves.append(chess.Move(frm, to).uci() + p)
    return moves


MOVES = _build_vocab()                      # 1880 moves
MOVE_TO_ID = {m: i for i, m in enumerate(MOVES)}


def to_model_frame(board: chess.Board):
    """Board seen from the side to move."""
    return board if board.turn == chess.WHITE else board.mirror()


def move_to_model_frame(move: chess.Move, turn: bool) -> str:
    if turn == chess.WHITE:
        return move.uci()
    m = chess.Move(chess.square_mirror(move.from_square),
                   chess.square_mirror(move.to_square), move.promotion)
    return m.uci()


def model_move_to_real(uci: str, turn: bool) -> chess.Move:
    m = chess.Move.from_uci(uci)
    if turn == chess.WHITE:
        return m
    return chess.Move(chess.square_mirror(m.from_square),
                      chess.square_mirror(m.to_square), m.promotion)


# ----------------------------------------------------------------- board encoding
# tokens: 0 = empty, 1..6 = own P N B R Q K, 7..12 = opponent P N B R Q K
# extra tokens: 4 castling flags (13/14 = no/yes) and en-passant file (15 = none, 16..23)
SEQ_LEN = 1 + 64 + 4 + 1          # CLS + squares + castling + ep
VOCAB_IN = 25                     # 24 = CLS


def encode_board(board: chess.Board) -> list:
    b = to_model_frame(board)
    toks = [24]
    for sq in range(64):
        p = b.piece_at(sq)
        if p is None:
            toks.append(0)
        else:
            toks.append(p.piece_type + (0 if p.color == chess.WHITE else 6))
    for flag in (b.has_kingside_castling_rights(chess.WHITE), b.has_queenside_castling_rights(chess.WHITE),
                 b.has_kingside_castling_rights(chess.BLACK), b.has_queenside_castling_rights(chess.BLACK)):
        toks.append(14 if flag else 13)
    toks.append(15 if b.ep_square is None else 16 + chess.square_file(b.ep_square))
    return toks


def legal_mask(board: chess.Board) -> torch.Tensor:
    mask = torch.zeros(len(MOVES), dtype=torch.bool)
    for mv in board.legal_moves:
        mask[MOVE_TO_ID[move_to_model_frame(mv, board.turn)]] = True
    return mask


# ----------------------------------------------------------------- model
class ChessNet(nn.Module):
    """Transformer over the board; policy head over MOVES, value head in [-1, 1]
    (expected game result for the side to move)."""

    def __init__(self, d=256, layers=8, heads=8):
        super().__init__()
        self.tok = nn.Embedding(VOCAB_IN, d)
        self.pos = nn.Parameter(torch.zeros(SEQ_LEN, d))
        layer = nn.TransformerEncoderLayer(d, heads, 4 * d, dropout=0.0,
                                           batch_first=True, norm_first=True)
        self.body = nn.TransformerEncoder(layer, layers)
        self.norm = nn.LayerNorm(d)
        self.policy = nn.Linear(d, len(MOVES))
        self.value = nn.Sequential(nn.Linear(d, d), nn.GELU(), nn.Linear(d, 1), nn.Tanh())
        self.config = dict(d=d, layers=layers, heads=heads)

    def forward(self, x):
        h = self.norm(self.body(self.tok(x) + self.pos))[:, 0]
        return self.policy(h), self.value(h).squeeze(-1)


def save_model(model, path, extra=None):
    torch.save({"config": model.config, "state": model.state_dict(), "extra": extra or {}}, path)


def load_model(path, device="cpu"):
    ck = torch.load(path, map_location=device)
    m = ChessNet(**ck["config"]).to(device)
    m.load_state_dict(ck["state"])
    return m


def masked_logits(logits, masks):
    return logits.masked_fill(~masks, float("-inf"))


# ----------------------------------------------------------------- data
def read_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f]


def write_jsonl(rows, path):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def tensorize(rows, with_masks=False):
    """rows need 'fen' (and 'm_played', 'result' for training)."""
    xs, ys, vs, ms = [], [], [], []
    for r in rows:
        b = chess.Board(r["fen"])
        xs.append(encode_board(b))
        if "m_played" in r:
            ys.append(MOVE_TO_ID[r["m_played"]])
        vs.append(float(r.get("result", 0.0)))
        if with_masks:
            ms.append(legal_mask(b))
    out = {"x": torch.tensor(xs, dtype=torch.long), "v": torch.tensor(vs)}
    if ys:
        out["y"] = torch.tensor(ys, dtype=torch.long)
    if with_masks:
        out["mask"] = torch.stack(ms)
    return out
