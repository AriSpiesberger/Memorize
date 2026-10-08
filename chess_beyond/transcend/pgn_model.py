"""A character-level PGN transformer, as in "Transcendence" (Zhang et al., NeurIPS 2024).

The model reads and writes games as plain PGN movetext, one character at a time,
e.g. ";1.e4 e5 2.Nf3 Nc6 3.Bb5 a6 ... 1-0", and is never shown the board or the
rules. Settings follow the paper's ChessFormer: a decoder-only transformer, 16
layers, d=512, 8 heads, ReLU MLPs, no dropout (~50M parameters).

Vocabulary: the 32 characters below, with ';' starting every game.

Playing: the prompt is the game so far in the same format, ending in "<n>." for a
White move or "<white move> " for a Black one; the model writes characters until
a space, and the result is parsed as SAN. An illegal or unparseable move is
resampled; after 5 failures the model loses the game (the paper's rule).
"""
import math

import chess
import torch
import torch.nn as nn
import torch.nn.functional as F

VOCAB = " #+-.0123456789;=BKNOQRabcdefghx"     # 32 characters; ';' starts a game
STOI = {c: i for i, c in enumerate(VOCAB)}
BOS = STOI[";"]
SPACE = STOI[" "]
MAX_TRIES = 5
MAX_MOVE_CHARS = 8                             # longest SAN, e.g. "exd8=Q+#" fits


def encode(text):
    return [STOI[c] for c in text]


def movetext(sans, result=None):
    """';1.e4 e5 2.Nf3 ...' from SAN moves; with a result, appended after a space."""
    parts = []
    for i, san in enumerate(sans):
        parts.append(f"{i // 2 + 1}.{san}" if i % 2 == 0 else san)
    text = ";" + " ".join(parts)
    return text + (" " + result if result else "")


def prompt(board):
    """The game so far, ready for the side to move: '...<n>.' or '...<white move> '."""
    root = board.root()
    sans = []
    for mv in board.move_stack:
        sans.append(root.san(mv))
        root.push(mv)
    text = movetext(sans)
    n = len(sans)
    if n == 0:
        return text + "1."
    return text + (f" {n // 2 + 1}." if n % 2 == 0 else " ")


class Block(nn.Module):
    def __init__(self, d, heads):
        super().__init__()
        self.ln1, self.ln2 = nn.LayerNorm(d), nn.LayerNorm(d)
        self.qkv, self.proj = nn.Linear(d, 3 * d), nn.Linear(d, d)
        self.mlp = nn.Sequential(nn.Linear(d, 4 * d), nn.ReLU(), nn.Linear(4 * d, d))
        self.heads = heads

    def forward(self, x):
        b, t, d = x.shape
        q, k, v = self.qkv(self.ln1(x)).split(d, dim=2)
        q, k, v = (z.view(b, t, self.heads, d // self.heads).transpose(1, 2) for z in (q, k, v))
        y = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        x = x + self.proj(y.transpose(1, 2).reshape(b, t, d))
        return x + self.mlp(self.ln2(x))


class PGNTransformer(nn.Module):
    def __init__(self, d=512, layers=16, heads=8, ctx=1024):
        super().__init__()
        self.tok = nn.Embedding(len(VOCAB), d)
        self.pos = nn.Embedding(ctx, d)
        self.blocks = nn.ModuleList(Block(d, heads) for _ in range(layers))
        self.ln = nn.LayerNorm(d)
        self.head = nn.Linear(d, len(VOCAB), bias=False)
        self.ctx = ctx
        self.config = dict(kind="pgn", d=d, layers=layers, heads=heads, ctx=ctx)
        self.apply(self._init)
        for name, p in self.named_parameters():        # GPT-2 scaled init for residual projections
            if name.endswith("proj.weight") or name.endswith("mlp.2.weight"):
                nn.init.normal_(p, 0.0, 0.02 / math.sqrt(2 * layers))

    @staticmethod
    def _init(m):
        if isinstance(m, nn.Linear):
            nn.init.normal_(m.weight, 0.0, 0.02)
            if m.bias is not None:
                nn.init.zeros_(m.bias)
        elif isinstance(m, nn.Embedding):
            nn.init.normal_(m.weight, 0.0, 0.02)

    def forward(self, idx):
        t = idx.shape[1]
        x = self.tok(idx) + self.pos(torch.arange(t, device=idx.device))
        for blk in self.blocks:
            x = blk(x)
        return self.head(self.ln(x))


def save_pgn_model(model, path, extra=None):
    torch.save({"config": model.config, "state": model.state_dict(), "extra": extra or {}}, path)


def load_pgn_model(path, device="cpu"):
    ck = torch.load(path, map_location=device)
    cfg = {k: v for k, v in ck["config"].items() if k != "kind"}
    m = PGNTransformer(**cfg).to(device)
    m.load_state_dict(ck["state"])
    return m


@torch.inference_mode()
def generate_moves(model, boards, temperature=0.0, dev="cuda", batch=256):
    """One move per board (None after MAX_TRIES illegal attempts). temperature 0 = greedy."""
    out = [None] * len(boards)
    prompts = [encode(prompt(b))[-(model.ctx - MAX_MOVE_CHARS):] for b in boards]
    todo = list(range(len(boards)))
    for _ in range(MAX_TRIES):
        if not todo:
            break
        written = {i: [] for i in todo}
        for s in range(0, len(todo), batch):
            live = todo[s:s + batch]
            while live:
                seqs = [prompts[i] + written[i] for i in live]
                n = max(len(q) for q in seqs)
                x = torch.full((len(seqs), n), SPACE, dtype=torch.long)
                for r, q in enumerate(seqs):
                    x[r, :len(q)] = torch.tensor(q)
                last = torch.tensor([len(q) - 1 for q in seqs])
                with torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev == "cuda"):
                    logits = model(x.to(dev))
                logits = logits[torch.arange(len(seqs)), last.to(dev)].float()
                logits[:, BOS] = -float("inf")                 # never start a new game mid-move
                if temperature <= 0:
                    nxt = logits.argmax(-1)
                else:
                    nxt = torch.multinomial(torch.softmax(logits / temperature, -1), 1).squeeze(1)
                still = []
                for i, c in zip(live, nxt.tolist()):
                    if c == SPACE and written[i]:
                        continue                                # move finished
                    if c != SPACE:
                        written[i].append(c)
                    if len(written[i]) < MAX_MOVE_CHARS:
                        still.append(i)
                live = still
        retry = []
        for i in todo:
            san = "".join(VOCAB[c] for c in written[i])
            try:
                out[i] = boards[i].parse_san(san)
            except ValueError:
                retry.append(i)
        todo = retry
    return out
