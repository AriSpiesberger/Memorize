"""Pure RL from random init on n-digit addition. No pretraining, no supervised loss.

Input  : digits of a, '+', digits of b, '='   (most significant first)
Output : n+1 digits of a+b, LEAST significant first (fixed length)
Policy : tiny causal transformer, samples output digits at temperature 1
Rewards:
  sparse : 1 if the whole answer is right, else 0  (one reward per answer)
  dense  : per digit, 1 if that digit is right     (one reward per token)
Update : REINFORCE with a group baseline (G samples per problem, like GRPO).
Eval   : greedy accuracy on TRAIN pairs and on HELD-OUT pairs never trained on.
"""
import argparse, json, math, os, random, time
import torch, torch.nn as nn, torch.nn.functional as F

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=2)
ap.add_argument("--reward", choices=["sparse", "dense"], default="dense")
ap.add_argument("--steps", type=int, default=3000)
ap.add_argument("--batch", type=int, default=64, help="problems per step")
ap.add_argument("--group", type=int, default=8, help="samples per problem")
ap.add_argument("--lr", type=float, default=1e-3)
ap.add_argument("--holdout", type=float, default=0.2)
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--out", default=None)
args = ap.parse_args()
torch.manual_seed(args.seed); random.seed(args.seed)
torch.set_num_threads(8)

PLUS, EQ, V = 10, 11, 12
n = args.n
L_in, L_out = 2 * n + 2, n + 1

# ---- data: all pairs, split train / held-out
N = 10 ** n
pairs = [(a, b) for a in range(N) for b in range(N)]
if len(pairs) > 200_000:
    pairs = random.sample(pairs, 200_000)
random.shuffle(pairs)
k = int(len(pairs) * args.holdout)
held, train = pairs[:k], pairs[k:]

def enc(a, b):
    da = [int(c) for c in str(a).zfill(n)]; db = [int(c) for c in str(b).zfill(n)]
    return da + [PLUS] + db + [EQ]

def target(a, b):
    s = str(a + b).zfill(n + 1)[::-1]      # least significant digit first
    return [int(c) for c in s]

def batch(ps):
    x = torch.tensor([enc(a, b) for a, b in ps]); y = torch.tensor([target(a, b) for a, b in ps])
    return x, y

# ---- model
class TinyLM(nn.Module):
    def __init__(s, d=128, h=4, layers=3):
        super().__init__()
        s.tok = nn.Embedding(V, d); s.pos = nn.Embedding(L_in + L_out, d)
        layer = nn.TransformerEncoderLayer(d, h, 4 * d, dropout=0.0, batch_first=True, norm_first=True)
        s.tr = nn.TransformerEncoder(layer, layers); s.head = nn.Linear(d, 10)
    def forward(s, seq):                       # seq: (B, T) -> logits over digits (B, T, 10)
        T = seq.shape[1]
        h = s.tok(seq) + s.pos(torch.arange(T))
        mask = torch.triu(torch.full((T, T), float("-inf")), 1)
        return s.head(s.tr(h, mask=mask))

model = TinyLM()
opt = torch.optim.Adam(model.parameters(), lr=args.lr)

def rollout(x, greedy=False):
    """Sample L_out digits. Returns digits (B, L_out) and their log-probs (B, L_out)."""
    seq, lps = x, []
    for _ in range(L_out):
        logits = model(seq)[:, -1]
        dist = torch.distributions.Categorical(logits=logits)
        d = logits.argmax(-1) if greedy else dist.sample()
        lps.append(dist.log_prob(d)); seq = torch.cat([seq, d[:, None]], 1)
    return seq[:, L_in:], torch.stack(lps, 1)

@torch.no_grad()
def accuracy(ps, m=2000):
    ps = ps[:m]; x, y = batch(ps); d, _ = rollout(x, greedy=True)
    full = (d == y).all(1).float().mean().item(); dig = (d == y).float().mean().item()
    return full, dig

log, t0 = [], time.time()
for step in range(args.steps + 1):
    if step % 250 == 0:
        tr, trd = accuracy(train); he, hed = accuracy(held)
        log.append(dict(step=step, train=tr, held=he, train_digit=trd, held_digit=hed))
        print(f"step {step:5d}  train {tr:.3f}  held-out {he:.3f}  (digit acc {trd:.3f}/{hed:.3f})  {time.time()-t0:.0f}s", flush=True)
    ps = random.sample(train, args.batch)
    x, y = batch(ps)
    x = x.repeat_interleave(args.group, 0); y = y.repeat_interleave(args.group, 0)
    d, lp = rollout(x)
    correct = (d == y).float()                                   # (B*G, L_out)
    if args.reward == "sparse":
        r = correct.all(1).float()                               # (B*G,)
        rg = r.view(-1, args.group)
        adv = (rg - rg.mean(1, keepdim=True)).view(-1)           # group baseline
        loss = -(adv[:, None] * lp).sum(1).mean()
    else:
        rg = correct.view(-1, args.group, L_out)
        adv = (rg - rg.mean(1, keepdim=True)).view(-1, L_out)    # per-digit group baseline
        loss = -(adv * lp).sum(1).mean()
    opt.zero_grad(); loss.backward(); opt.step()

if args.out:
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    json.dump(dict(args=vars(args), log=log), open(args.out, "w"))
