"""Pure RL from random init on several algorithmic tasks, with an optional scratchpad.

Same recipe as rl_addition.py (tiny transformer, no pretraining, no supervised loss,
REINFORCE with a group baseline), extended in two ways:

  workspace  --scratch K : before answering, the model emits K free characters drawn from
             digits, letters and space (the same tokens the task itself uses). Nothing constrains them and no reward looks
             at them; they get only the credit of the answer that follows. Whatever they
             mean, RL has to invent it. K=0 is the no-workspace baseline.
  tasks      several domains, one model or one model per task (see TASKS below).

Sequence:  [task] input... '='  |  scratch x K  |  answer digits
Eval:      greedy accuracy on TRAIN problems and on HELD-OUT problems never trained on.
"""
import argparse, json, os, random, time
import torch, torch.nn as nn

PLUS, EQ, TIMES, LP, RP = 10, 11, 12, 13, 14
TASK0, LET0, SPACE, V = 15, 24, 50, 51       # task tokens 15..23, letters a-z 24..49, space 50
SCR_IDS = list(range(10)) + list(range(LET0, V))   # workspace alphabet: digits, letters, space (37 chars)
S = len(SCR_IDS)
def decode(t): return "".join(str(i) if i < 10 else " " if i == SPACE else chr(97 + i - LET0) for i in t)

def digits(x, n): return [int(c) for c in str(x).zfill(n)]

# Each task: rng -> (input tokens, target digits). Fixed lengths per task.
def t_add(rng, n=2):                         # a+b, answer least significant digit first
    a, b = rng.randrange(10**n), rng.randrange(10**n)
    return digits(a, n) + [PLUS] + digits(b, n), digits(a + b, n + 1)[::-1]
def t_add_msb(rng, n=2):                     # same, but most significant first: needs carry lookahead
    x, y = t_add(rng, n); return x, y[::-1]
def t_mul(rng, n=2):                         # a*b, least significant first
    a, b = rng.randrange(10**n), rng.randrange(10**n)
    return digits(a, n) + [TIMES] + digits(b, n), digits(a * b, 2 * n)[::-1]
def t_sort(rng, L=5):
    l = [rng.randrange(10) for _ in range(L)]; return l, sorted(l)
def t_reverse(rng, L=6):
    l = [rng.randrange(10) for _ in range(L)]; return l, l[::-1]
def t_parity(rng, L=8):                      # xor of bits
    l = [rng.randrange(2) for _ in range(L)]; return l, [sum(l) % 2]
def t_summod(rng, L=6):                      # sum of digits mod 10
    l = [rng.randrange(10) for _ in range(L)]; return l, [sum(l) % 10]
def t_count(rng, L=8):                       # how often does the last digit occur in the list
    l = [rng.randrange(4) for _ in range(L)]; q = rng.randrange(4); return l + [q], [l.count(q)]
def t_dyck(rng, L=8):                        # are the parentheses balanced
    s, depth = [], 0
    for i in range(L):                       # random balanced string
        close = depth > 0 and (L - i == depth or rng.random() < 0.5)
        s.append(RP if close else LP); depth += -1 if close else 1
    if rng.random() < 0.5:                   # half the time, corrupt it
        i = rng.randrange(L); s[i] = LP if s[i] == RP else RP
    d, ok = 0, True
    for c in s:
        d += 1 if c == LP else -1; ok &= d >= 0
    return s, [int(ok and d == 0)]

def t_modadd(rng, p=97):                     # (a+b) mod p, two digits each
    a, b = rng.randrange(p), rng.randrange(p); return digits(a, 2) + [PLUS] + digits(b, 2), digits((a + b) % p, 2)
_LUT = random.Random(12345); LUT = [_LUT.randrange(10) for _ in range(1000)]
def t_lookup(rng):                           # random key -> random value: pure memorisation, held-out must be chance
    k = rng.randrange(1000); return digits(k, 3), [LUT[k]]

TASKS = dict(modadd=t_modadd, lookup=t_lookup, add=t_add, add_msb=t_add_msb, mul=t_mul, sort=t_sort, reverse=t_reverse,
             parity=t_parity, summod=t_summod, count=t_count, dyck=t_dyck)

ap = argparse.ArgumentParser()
ap.add_argument("--tasks", default="add_msb,sort,reverse,parity,summod,count,dyck",
                help="comma list from: " + ",".join(TASKS))
ap.add_argument("--joint", action="store_true", help="one model on all tasks (default: one model per task)")
ap.add_argument("--scratch", type=int, default=0, help="K workspace tokens before the answer (0 = none)")
ap.add_argument("--reward", choices=["sparse", "dense"], default="dense")
ap.add_argument("--steps", type=int, default=3000)
ap.add_argument("--batch", type=int, default=64)
ap.add_argument("--group", type=int, default=8)
ap.add_argument("--lr", type=float, default=1e-3)
ap.add_argument("--ent", type=float, default=0.0, help="entropy bonus on scratch tokens")
ap.add_argument("--d", type=int, default=128)
ap.add_argument("--layers", type=int, default=3)
ap.add_argument("--pool", type=int, default=20000, help="max distinct train problems per task")
ap.add_argument("--held", type=int, default=1000, help="held-out problems per task")
ap.add_argument("--eval-every", type=int, default=250)
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--threads", type=int, default=2)
ap.add_argument("--out", default=None)
args = ap.parse_args()

torch.set_num_threads(args.threads)
K = args.scratch
names = args.tasks.split(",")

def make_data(name, tid):
    """Distinct train / held-out problems, as (input-with-task-token, target) tensors."""
    rng = random.Random(1000 * tid + 7); seen, probs = set(), []
    want, tries = args.pool + args.held, 0
    while len(probs) < want and tries < 20 * want:
        x, y = TASKS[name](rng); tries += 1
        if tuple(x) not in seen: seen.add(tuple(x)); probs.append(([TASK0 + tid] + x + [EQ], y))
    rng.shuffle(probs); h = min(args.held, len(probs) // 5)
    return probs[h:], probs[:h]

class TinyLM(nn.Module):
    def __init__(s, maxlen, d, layers):
        super().__init__()
        s.tok = nn.Embedding(V, d); s.pos = nn.Embedding(maxlen, d)
        layer = nn.TransformerEncoderLayer(d, 4, 4 * d, dropout=0.0, batch_first=True, norm_first=True)
        s.tr = nn.TransformerEncoder(layer, layers); s.head = nn.Linear(d, V)
    def forward(s, seq):
        T = seq.shape[1]
        mask = torch.triu(torch.full((T, T), float("-inf")), 1)
        return s.head(s.tr(s.tok(seq) + s.pos(torch.arange(T)), mask=mask))

SCR_T = torch.tensor(SCR_IDS)

def rollout(model, x, lo, greedy=False):
    """Sample K scratch tokens then lo answer digits. Returns scratch, answer, and their log-probs / entropies."""
    seq, lps, ents = x, [], []
    for i in range(K + lo):
        logits = model(seq)[:, -1]
        logits = logits[:, SCR_IDS] if i < K else logits[:, :10]
        dist = torch.distributions.Categorical(logits=logits)
        a = logits.argmax(-1) if greedy else dist.sample()
        lps.append(dist.log_prob(a)); ents.append(dist.entropy())
        seq = torch.cat([seq, (SCR_T[a] if i < K else a)[:, None]], 1)
    return seq[:, x.shape[1]:x.shape[1] + K], seq[:, x.shape[1] + K:], torch.stack(lps, 1), torch.stack(ents, 1)

def tensors(ps):
    return torch.tensor([p[0] for p in ps]), torch.tensor([p[1] for p in ps])

@torch.no_grad()
def accuracy(model, ps, m=1000):
    x, y = tensors(ps[:m]); _, d, _, _ = rollout(model, x, y.shape[1], greedy=True)
    return (d == y).all(1).float().mean().item(), (d == y).float().mean().item()

def train(group_names, tag):
    """Train one model on the given tasks (sampled uniformly per step); return its log and samples."""
    torch.manual_seed(args.seed); rnd = random.Random(args.seed)
    data = {n: make_data(n, names.index(n)) for n in group_names}
    maxlen = max(len(tr[0][0]) + K + len(tr[0][1]) for tr, _ in data.values())
    model = TinyLM(maxlen, args.d, args.layers); opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    log, t0 = [], time.time()
    for step in range(args.steps + 1):
        if step % args.eval_every == 0:
            row = dict(step=step)
            for n, (tr, he) in data.items():
                (a, ad), (b, bd) = accuracy(model, tr), accuracy(model, he)
                row[n] = dict(train=a, held=b, train_digit=ad, held_digit=bd)
            log.append(row)
            print(f"[{tag}] step {step:5d} {time.time()-t0:4.0f}s  " +
                  "  ".join(f"{n} {row[n]['train']:.2f}/{row[n]['held']:.2f}" for n in data), flush=True)
        n = rnd.choice(group_names); tr, _ = data[n]
        x, y = tensors(rnd.sample(tr, args.batch)); lo = y.shape[1]
        x = x.repeat_interleave(args.group, 0); y = y.repeat_interleave(args.group, 0)
        _, d, lp, ent = rollout(model, x, lo)
        correct = (d == y).float()
        if args.reward == "sparse": correct = correct.all(1, keepdim=True).float().expand(-1, lo)
        adv = (correct.view(-1, args.group, lo) - correct.view(-1, args.group, lo).mean(1, keepdim=True)).view(-1, lo)
        loss = -(adv * lp[:, K:]).sum(1).mean()
        if K:   # scratch tokens share the credit of the whole answer
            seq_adv = adv.mean(1, keepdim=True)
            loss = loss - (seq_adv * lp[:, :K]).sum(1).mean() - args.ent * ent[:, :K].sum(1).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    samples = {}
    for n, (_, he) in data.items():
        x, y = tensors(he[:5]); s, d, _, _ = rollout(model, x, y.shape[1], greedy=True)
        samples[n] = [dict(input=x[i].tolist(), scratch=decode(s[i].tolist()), answer=d[i].tolist(), target=y[i].tolist())
                      for i in range(len(x))]
    return log, samples

runs = {"joint": names} if args.joint else {n: [n] for n in names}
result = dict(args=vars(args), runs={})
for tag, group in runs.items():
    log, samples = train(group, tag)
    result["runs"][tag] = dict(log=log, samples=samples)
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        json.dump(result, open(args.out, "w"))
