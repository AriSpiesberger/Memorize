"""PUCT tree search (AlphaZero-style) using only the network: policy priors and
value-head leaf evaluations. No engine is used at test time.

  from search import mcts_move
  move = mcts_move(model, board, sims=200)
"""
import math

import chess
import torch

from common import MOVE_TO_ID, encode_board, move_to_model_frame


class Node:
    __slots__ = ("prior", "children", "N", "W")

    def __init__(self, prior):
        self.prior, self.children, self.N, self.W = prior, {}, 0, 0.0

    def Q(self):
        return self.W / self.N if self.N else 0.0


@torch.no_grad()
def evaluate(model, board, device):
    """Priors over legal moves and value for the side to move."""
    if board.is_checkmate():
        return {}, -1.0
    if board.is_game_over(claim_draw=True):
        return {}, 0.0
    x = torch.tensor([encode_board(board)], device=device)
    logits, v = model(x)
    legal = list(board.legal_moves)
    ids = torch.tensor([MOVE_TO_ID[move_to_model_frame(m, board.turn)] for m in legal], device=device)
    p = torch.softmax(logits[0, ids], -1).tolist()
    return dict(zip(legal, p)), float(v[0])


def mcts_move(model, board, sims=200, c_puct=1.5, device="cpu"):
    model.eval()
    root = Node(1.0)
    priors, _ = evaluate(model, board, device)
    if not priors:
        return None
    root.children = {m: Node(p) for m, p in priors.items()}
    for _ in range(sims):
        node, b, path = root, board.copy(stack=False), []
        while node.children:                                   # select
            total = math.sqrt(node.N + 1)
            mv, node = max(node.children.items(),
                           key=lambda kv: -kv[1].Q() + c_puct * kv[1].prior * total / (1 + kv[1].N))
            # child Q is from the child's mover's view, so negate for the parent
            b.push(mv); path.append(node)
        pri, value = evaluate(model, b, device)               # expand + evaluate
        node.children = {m: Node(p) for m, p in pri.items()}
        for n in reversed(path):                              # backup (value is for side to move at leaf)
            n.N += 1; n.W += value
            value = -value
        root.N += 1
    return max(root.children.items(), key=lambda kv: kv[1].N)[0]
