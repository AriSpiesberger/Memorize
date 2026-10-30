"""Offline RL for a PGN model on database games, rewarded only by who won: +1 for the winner's
moves, and (optionally) a penalty for the loser's.

    python transcend/rl_pgn_games.py --init Arisp/chess-pgn-1000-1300 --data data/transcend/pgn-1000-1300 \
        --out runs/transcend/rl-pgn-1000-1300.pt --games 500000

--init is a Hugging Face repo or a local .pt (eval.load); it is also the frozen KL reference.

Games. A seeded random --games of the training games in --data (make_pgn_data.py output, the games
the model was imitating; the held-out ones are never trained on), one pass, --batch games per step,
each read from its first ';' and cut at --ctx characters (a move cut by the window is dropped). Kept
only if (by default):
  decisive            draws carry no reward (--keep-draws keeps them: KL only)
  normal termination  not lost on time, abandoned or by rules infraction, where the result says
                      little about the moves (--keep-unnormal keeps them)
  |WhiteElo - BlackElo| <= --max-elo-diff (50)
                      otherwise the winner is mostly the higher-rated player, and "play like the
                      winner" is partly "play like the stronger player": imitation again
The ratings and terminations come from <data>/info.npz (make_pgn_data.py --info-only).

The model is one player per game, and only that player's moves get a loss: each move's SAN and
closing space (what the model writes when it plays); move numbers, the result and the opponent's
moves are context only. --loser picks the player and the loss on a move with probability p (the
product of its characters' probabilities):
  skip     (default) the model is the winner: -log p. Reward-weighted fine-tuning on won games.
  bounded  a random side (seeded): -log p if it won, +p if it lost. The push on a losing move is
           p * grad log p: never more than REINFORCE's, and it fades as p falls, so p cannot be
           driven to 0. (-log(1 - p) also fades, but its push is p / (1 - p): ~100 on the near-
           forced moves a loser plays at p ~ 0.99, recaptures and king moves out of check.)
  logp     a random side: -log p if it won, +log p if it lost (plain REINFORCE, r = -1). The
           push on a losing move never fades; the KL below cannot hold it (its pull on a
           character vanishes with that character's probability).
Each move is weighted by --gamma ** (plies left after it; default 1 = every move counts fully),
and the first --skip-plies plies get no loss (default 0). Plus, at the same characters,
--beta * KL(pi || ref) over the full 33-character distribution. Everything is averaged over the
batch's trained characters.

Every --eval-every steps, on the first --val-n held-out games that pass the same filters (the
same games every time), over both players' moves:
  ce          mean -log pi per move character (imitation fit; rises as the policy leaves the data)
  win, lose   mean log p per move of the winner's and the loser's moves
  gap         win - lose (what the reward pushes up; not playing strength: use eval.py games)
  kl          KL(pi || ref) per move character
Lines go to <out>_log.jsonl, the weights to <out>_step<N>.pt (train_pgn.py's format, which eval.py
loads), and the last weights to <out>.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # chess_beyond/
from eval import load
from pgn_model import VOCAB, save_pgn_model

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--init", required=True, help="Hugging Face repo or local .pt to start from (also the KL reference)")
ap.add_argument("--data", required=True, help="make_pgn_data.py output folder, with info.npz")
ap.add_argument("--out", required=True)
ap.add_argument("--games", type=int, default=500_000, help="training games, sampled from the ones that pass the filters")
ap.add_argument("--loser", choices=["skip", "bounded", "logp"], default="skip")
ap.add_argument("--max-elo-diff", type=int, default=50, help="keep games with |WhiteElo - BlackElo| <= this (-1 = off)")
ap.add_argument("--keep-draws", action="store_true")
ap.add_argument("--keep-unnormal", action="store_true", help="keep time forfeits, abandoned games, rules infractions")
ap.add_argument("--gamma", type=float, default=1.0, help="weight a move by gamma ** (plies left after it)")
ap.add_argument("--skip-plies", type=int, default=0, help="no loss on the first N plies")
ap.add_argument("--batch", type=int, default=256, help="games per optimizer step")
ap.add_argument("--micro", type=int, default=128, help="games per forward pass (memory)")
ap.add_argument("--ctx", type=int, default=1024)
ap.add_argument("--lr", type=float, default=1e-5)
ap.add_argument("--warmup", type=int, default=50)
ap.add_argument("--weight-decay", type=float, default=0.0)
ap.add_argument("--beta", type=float, default=0.1, help="KL(pi || ref) weight")
ap.add_argument("--eval-every", type=int, default=100)
ap.add_argument("--val-n", type=int, default=2000, help="held-out games for the evals")
ap.add_argument("--log-every", type=int, default=10)
ap.add_argument("--compile", action="store_true")
ap.add_argument("--gpu-mem-frac", type=float, default=0.92)
ap.add_argument("--device", default="cuda")
ap.add_argument("--seed", type=int, default=0)
args = ap.parse_args()

torch.manual_seed(args.seed)
dev = args.device
cuda = dev == "cuda"
if cuda:
    torch.cuda.set_per_process_memory_fraction(args.gpu_mem_frac)
    torch.backends.cuda.matmul.allow_tf32 = True


def autocast():
    return torch.autocast("cuda", dtype=torch.bfloat16) if cuda else torch.autocast("cpu", enabled=False)


# ---------------------------------------------------------------- games and filters

data = Path(args.data)
meta = json.loads((data / "meta.json").read_text())
tokens = np.fromfile(data / "tokens.bin", dtype=np.uint8)
starts = np.load(data / "starts.npy")
ends = np.append(starts[1:], len(tokens))
nv = meta["val_games"]
if not (data / "info.npz").exists():
    sys.exit(f"no {data}/info.npz (ratings and terminations): run make_pgn_data.py --info-only with the flags "
             f"{data} was built with (Modal: modal_train.py::pgn_info)")
info = np.load(data / "info.npz")
if len(info["chars"]) != len(starts) or not np.array_equal(info["chars"], np.diff(np.append(starts, len(tokens)))):
    sys.exit(f"{data}/info.npz does not line up with starts.npy")
WHITE_OUTCOME = np.zeros(len(VOCAB), dtype=np.int8)              # by a game's last character: 1-0, 0-1, 1/2-1/2
WHITE_OUTCOME[VOCAB.index("0")], WHITE_OUTCOME[VOCAB.index("1")] = 1, -1
outcome = WHITE_OUTCOME[tokens[ends - 1]]
keep = np.ones(len(starts), dtype=bool)
counts = {}
for label, ok in [("decisive", outcome != 0 if not args.keep_draws else None),
                  ("normal termination", info["normal"] if not args.keep_unnormal else None),
                  (f"|elo diff| <= {args.max_elo_diff}",
                   (info["white_elo"] >= 0) & (info["black_elo"] >= 0)
                   & (np.abs(info["white_elo"].astype(int) - info["black_elo"]) <= args.max_elo_diff)
                   if args.max_elo_diff >= 0 else None)]:
    if ok is not None:
        keep &= ok
        counts[label] = f"{ok[nv:].mean():.1%}"
train_pool = np.flatnonzero(keep[nv:]) + nv
val_ids = np.flatnonzero(keep[:nv])[:args.val_n]
print(f"filters (share of training games passing each): {counts}; {len(train_pool):,} of {len(starts) - nv:,} "
      f"pass all; {len(val_ids)} held-out games for the evals", flush=True)
if args.games > len(train_pool):
    sys.exit(f"only {len(train_pool):,} training games pass the filters, fewer than --games {args.games:,}")
train_ids = np.random.default_rng(args.seed).choice(train_pool, args.games, replace=False)
# the side the model plays in each game: the winner (--loser skip), else a random side; +1 = White
SIDE = np.where(outcome != 0, outcome, 1) if args.loser == "skip" else \
    np.random.default_rng(args.seed + 1).choice(np.array([1, -1], dtype=np.int8), len(starts))


def plies(text):
    """Per character of a game: the ply its move belongs to (the SAN and its closing space), -1 for
    ';', move numbers and the result."""
    cut = text.rfind(" ")
    ply = np.full(len(text), -1, dtype=np.int32)
    i, n = 1, 0                                          # past ';'
    while i < cut:
        j = text.find(" ", i)
        dot = text.find(".", i, j)                       # "<n>.<white move>" or "<black move>"
        ply[(dot + 1 if dot >= 0 else i):j + 1] = n
        n, i = n + 1, j + 1
    return ply, n


def rows(ids, train):
    """x, y (next characters), and per target: reward of the move's side (+1 won, -1 lost, 0 draw),
    its weight, whether it gets a loss, and its ply (-1 for none); (n, ctx) each. train=False: every
    move of both players, unweighted (the evals)."""
    n, T = len(ids), args.ctx + 1
    w = np.zeros((n, T), dtype=np.int64)
    r, wt, m = (np.zeros((n, T), dtype=np.float32) for _ in range(3))
    pl = np.full((n, T), -1, dtype=np.int64)
    for k, g in enumerate(ids):
        chars = tokens[starts[g]:ends[g]]
        ply, total = plies("".join(VOCAB[c] for c in chars))
        L = min(len(chars), T)
        if L < len(chars) and ply[L] >= 0:
            ply[ply == ply[L]] = -1                      # the move the window cuts
        ply = ply[:L]
        mover = np.where(ply % 2 == 0, 1, -1)
        on = ply >= 0
        if train:
            on &= (mover == SIDE[g]) & (ply >= args.skip_plies)
        w[k, :L] = chars[:L]
        r[k, :L] = mover * outcome[g] * on
        wt[k, :L] = np.where(on, args.gamma ** (total - 1 - ply), 0) if train else on
        m[k, :L] = on
        pl[k, :L] = np.where(on, ply, -1)
    t = lambda a: torch.from_numpy(a[:, 1:]).to(dev, non_blocking=True)
    return torch.from_numpy(w[:, :-1]).to(dev, non_blocking=True), t(w), t(r), t(wt), t(m), t(pl)


# ---------------------------------------------------------------- model and loss

model, name = load(args.init, dev)
ref, _ = load(args.init, dev)
for p in ref.parameters():
    p.requires_grad_(False)
model.train()
fwd = torch.compile(model) if args.compile else model
reff = torch.compile(ref) if args.compile else ref
decay = [p for p in model.parameters() if p.dim() >= 2]
no_decay = [p for p in model.parameters() if p.dim() < 2]
opt = torch.optim.AdamW([dict(params=decay, weight_decay=args.weight_decay), dict(params=no_decay, weight_decay=0.0)],
                        lr=args.lr, betas=(0.9, 0.95), fused=cuda)
steps = len(train_ids) // args.batch
print(f"{name}: {len(train_ids):,} games, {args.batch} per step -> {steps:,} steps; loser {args.loser}, "
      f"beta {args.beta}, lr {args.lr}, gamma {args.gamma}, skip plies {args.skip_plies}", flush=True)


def forward(x, y, pl):
    """Per target: log pi(y), KL(pi || ref); and per (row, ply) the move's log p (sum over its characters)."""
    with autocast():
        logits = fwd(x)
    with torch.no_grad(), autocast():
        ref_logits = reff(x)
    lp = F.log_softmax(logits.float(), -1)
    lp_y = lp.gather(-1, y.unsqueeze(-1)).squeeze(-1)
    kl = (lp.exp() * (lp - F.log_softmax(ref_logits.float(), -1))).sum(-1)
    slot = torch.where(pl >= 0, pl, args.ctx)                       # ctx = a slot no move uses
    move_lp = torch.zeros(len(x), args.ctx + 1, device=dev).scatter_add(1, slot, lp_y * (pl >= 0))
    return lp_y, kl, move_lp, slot


def loss_sums(x, y, r, wt, m, pl):
    """Sums over the trained characters: the policy loss and the KL."""
    lp_y, kl, move_lp, slot = forward(x, y, pl)
    pg = -(wt * lp_y * (r > 0)).sum()                               # winner: -log p, character by character
    lose = (r < 0) & (m > 0)
    if args.loser == "logp":
        pg = pg + (wt * lp_y * lose).sum()
    elif args.loser == "bounded":                                   # + p per losing move
        move_wt = torch.zeros_like(move_lp).scatter_reduce(1, slot, wt * lose, "amax")[:, :args.ctx]
        pg = pg + (move_wt * move_lp[:, :args.ctx].exp()).sum()
    return pg, (kl * m).sum()


@torch.no_grad()
def evaluate():
    model.eval()
    tot = dict(chars=0.0, ce=0.0, kl=0.0, win=0.0, nwin=0.0, lose=0.0, nlose=0.0)
    for s in range(0, len(val_ids), args.micro):
        x, y, r, _, m, pl = rows(val_ids[s:s + args.micro], train=False)
        lp_y, kl, move_lp, slot = forward(x, y, pl)
        sign = torch.zeros_like(move_lp).scatter_reduce(1, slot, r, "amax") \
            + torch.zeros_like(move_lp).scatter_reduce(1, slot, r, "amin")   # the move's reward, 0 if no move
        sign[:, args.ctx] = 0
        tot["chars"] += m.sum().item()
        tot["ce"] += -(lp_y * m).sum().item()
        tot["kl"] += (kl * m).sum().item()
        tot["win"] += (move_lp * (sign > 0)).sum().item()
        tot["nwin"] += (sign > 0).sum().item()
        tot["lose"] += (move_lp * (sign < 0)).sum().item()
        tot["nlose"] += (sign < 0).sum().item()
    model.train()
    out = dict(ce=tot["ce"] / tot["chars"], kl=tot["kl"] / tot["chars"], win=tot["win"] / max(tot["nwin"], 1),
               lose=tot["lose"] / max(tot["nlose"], 1))
    out["gap"] = out["win"] - out["lose"]
    return out


# ---------------------------------------------------------------- training

os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
stem = os.path.splitext(args.out)[0]
log_path = stem + "_log.jsonl"
if os.path.exists(log_path):
    sys.exit(f"{log_path} exists: use another --out")


def log_eval(step, extra=None):
    ev = evaluate()
    print(f"step {step}  held-out ce {ev['ce']:.4f}  kl {ev['kl']:.4f}  win {ev['win']:.3f}  lose {ev['lose']:.3f}"
          f"  gap {ev['gap']:.3f}", flush=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(dict(step=step, games=step * args.batch, **ev, **(extra or {}))) + "\n")
    save_pgn_model(model, f"{stem}_step{step}.pt", extra=dict(step=step, init=args.init, args=vars(args), **ev))


log_eval(0)
t0, last = time.time(), time.time()
for step in range(1, steps + 1):
    for g in opt.param_groups:
        g["lr"] = args.lr * min(1.0, step / args.warmup)
    ids = train_ids[(step - 1) * args.batch:step * args.batch]
    parts = [rows(ids[s:s + args.micro], train=True) for s in range(0, len(ids), args.micro)]
    n = sum(p[4].sum() for p in parts).clamp(min=1)                 # trained characters in the whole batch
    pg_tot, kl_tot = torch.zeros((), device=dev), torch.zeros((), device=dev)
    for part in parts:
        pg, kl = loss_sums(*part)
        ((pg + args.beta * kl) / n).backward()
        pg_tot += pg.detach() / n
        kl_tot += kl.detach() / n
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    opt.step()
    opt.zero_grad(set_to_none=True)
    if step % args.log_every == 0:
        now = time.time()
        rate = args.log_every / (now - last)
        last = now
        print(f"  step {step}/{steps}  pg {pg_tot.item():+.4f}  kl {kl_tot.item():.4f}  {rate * args.batch:.0f} games/s  "
              f"~{(steps - step) / max(rate, 1e-9) / 60:.0f} min left", flush=True)
    if step % args.eval_every == 0 or step == steps:
        log_eval(step, dict(train_pg=pg_tot.item(), train_kl=kl_tot.item(), hours=(time.time() - t0) / 3600))
        last = time.time()
save_pgn_model(model, args.out, extra=dict(step=steps, init=args.init, args=vars(args)))
print(f"done: {steps} steps, {steps * args.batch:,} games -> {args.out}")
