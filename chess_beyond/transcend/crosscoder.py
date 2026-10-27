"""A crosscoder between the two PGN models: one dictionary of latents, read from and written to both
models' states on the same positions, so each latent is either shared or belongs to one model.

    python transcend/crosscoder.py collect                       # both HF models, layers 4 8 12 15 final
    python transcend/crosscoder.py train --run runs/transcend/crosscoder/chess-pgn-1000-1300__chess-pgn-2400plus --layers 12
    python transcend/crosscoder.py top   --run runs/transcend/crosscoder/chess-pgn-1000-1300__chess-pgn-2400plus --cc L12
    python transcend/crosscoder.py all                           # collect, then train + top for each layer (a sweep)
    python transcend/crosscoder.py sweep --run runs/transcend/crosscoder/chess-pgn-1000-1300__chess-pgn-2400plus

collect  Samples random games from make_pgn_data.py folders (default pgn-everything: Lichess games
         of every rating) and, per game, --per-game random plies from
         --min-ply on. One forward pass per game gives every ply's state, so a million positions
         take ~60k games. At each ply the state is the one at the prompt's last character, just
         before the model writes its move (as in sae.py), from both models, at every --layers entry
         (a block index 0-15, the residual stream after that block, or 'final', after the last
         LayerNorm). -> <run>/acts/<model>-L<layer>.npy (float16, one row per position),
         <run>/rows.npy (folder, game, ply, character index) and <run>/collect.json.

train    A BatchTopK crosscoder (Lindsey et al. 2024, "Sparse Crosscoders for Cross-Layer Features
         and Model Diffing"; BatchTopK as in Bussmann et al. 2024 and, for model diffing, Minder et
         al. 2025, which found L1 crosscoders invent model-exclusive latents). The sources are
         (model, layer) pairs, each scaled to mean norm sqrt(d):
             f = BatchTopK(ReLU(sum_s W_enc[s] (x_s - b_dec[s]) + b_enc)),   x_hat_s = W_dec[:, s] f + b_dec[s]
         Each latent's decoder norms sum to 1 over the sources (free split between the models), and
         latents are ranked by activation x that sum, k per position on average over the batch; at inference a latent fires above a threshold learned during
         training. A latent can still write to one model only. With several
         --layers it is one crosscoder over all of them (acausal, across layers and models).
         AuxK keeps latents from dying. -> <run>/cc-<layers>/cc.pt and train_log.jsonl.

top      Per latent, relative decoder norm r = |d_B| / (|d_A| + |d_B|): ~0 only model A (the first
         --models entry) uses it, ~1 only model B, ~0.5 shared; for shared latents, the cosine of
         the two models' decoder directions. Encodes every position and keeps each latent's top
         --examples. Writes results/transcend/crosscoder/<run>/<cc>/: report.md (FVU per model,
         the r histogram, then the --report strongest latents exclusive to A, exclusive to B,
         and shared with dissimilar decoders, each with firing rates per folder and top positions:
         the move played and each model's own top move and probability), relative_norms.png and
         summary.json; <run>/<cc>/latents.jsonl (every latent) and features.html (boards).

Which layer: both models must track the board from the move text, so middle layers likely hold
mostly shared, board-state latents; the move choice, where the two rating bands differ, is
nearest the head, so late layers (12-15, final) are where model-exclusive latents should show.
`all` trains one crosscoder per collected layer and writes sweep.md to compare them.
"""
import argparse
import html
import json
import math
import sys
import time
from pathlib import Path

import chess
import chess.svg
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parent))          # transcend/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))      # chess_beyond/
import paths
import eval as ev                                                 # load, board_of, score, device
from pgn_model import SPACE, VOCAB, prompt
from pgn_probe import parse_movetext
from sae import last_moves, lichess

RUNS = paths.RUNS / "transcend" / "crosscoder"
RESULTS = paths.ROOT / "results" / "transcend" / "crosscoder"
MODELS = ["Arisp/chess-pgn-1000-1300", "Arisp/chess-pgn-2400plus"]
FOLDERS = ["data/transcend/pgn-everything"]
CHARS = np.array(list(VOCAB))


# ---------------------------------------------------------------- positions

class Corpus:
    """make_pgn_data.py folders: game text by (folder, game)."""

    def __init__(self, folders):
        self.folders = [Path(f) if Path(f).is_absolute() else paths.ROOT / f for f in folders]
        self.tokens = [np.memmap(f / "tokens.bin", dtype=np.uint8, mode="r") for f in self.folders]
        self.starts = [np.load(f / "starts.npy") for f in self.folders]
        self.names = [f.name for f in self.folders]

    def span(self, f, g):
        s = self.starts[f]
        return int(s[g]), int(s[g + 1]) if g + 1 < len(s) else len(self.tokens[f])

    def text(self, f, g):
        s, e = self.span(f, g)
        return "".join(CHARS[self.tokens[f][s:e]])

    def ids(self, f, g, n):
        s, _ = self.span(f, g)
        return torch.from_numpy(self.tokens[f][s:s + n].astype(np.int64))


def ply_ends(text, ctx, min_ply):
    """(ply, character index) for each ply from min_ply on that has a next move: the index of the
    prompt's last character in the game text ('<n>.' before a White move, the space before a Black
    one), kept while it fits in the context."""
    sans, _ = parse_movetext(text)
    out, o = [], 1                                            # o: where move token p starts (after ';')
    for p, tok in enumerate(text[1:].split(" ")[:len(sans)]):
        if p % 2 == 0:
            num = str(p // 2 + 1)
            if not tok.startswith(num + "."):
                return []                                     # not the expected movetext
            end = o + len(num)
        else:
            end = o - 1
        if end >= ctx:
            break
        if p >= min_ply:
            out.append((p, end))
        o += len(tok) + 1
    return out


def pick_positions(corpus, n, per_game, min_ply, ctx, seed):
    """(n, 4) int64 rows (folder, game, ply, character index), n // folders from each folder."""
    rng = np.random.default_rng(seed)
    rows = []
    for f, name in enumerate(corpus.names):
        want, got, games = n // len(corpus.names), 0, 0
        for g in rng.permutation(len(corpus.starts[f])):
            if got >= want:
                break
            ends = ply_ends(corpus.text(f, int(g)), ctx, min_ply)
            if not ends:
                continue
            take = rng.choice(len(ends), min(per_game, len(ends), want - got), replace=False)
            rows += [(f, int(g), *ends[j]) for j in sorted(take)]
            got += len(take)
            games += 1
        print(f"  {name}: {got} positions from {games} games", flush=True)
    return np.array(rows, dtype=np.int64)


def source_name(model_name, layer):
    return f"{model_name}-L{layer}"


@torch.no_grad()
def collect(a):
    dev = ev.device(a.device)
    models = [ev.load(m, dev) for m in a.models]
    names = [n for _, n in models]
    run = Path(a.run) if a.run else RUNS / "__".join(names)
    corpus = Corpus(a.pgn_data)
    ctx = min(m.ctx for m, _ in models)
    print(f"picking {a.positions} positions, {a.per_game} per game", flush=True)
    rows = pick_positions(corpus, a.positions, a.per_game, a.min_ply, ctx, a.seed)
    d = models[0][0].ln.normalized_shape[0]
    (run / "acts").mkdir(parents=True, exist_ok=True)
    np.save(run / "rows.npy", rows)
    out = {(i, L): np.lib.format.open_memmap(run / "acts" / f"{source_name(n, L)}.npy", mode="w+",
                                             dtype=np.float16, shape=(len(rows), d))
           for i, n in enumerate(names) for L in a.layers}

    games = {}                                                # (folder, game) -> [(row, char index)]
    for r, (f, g, _, e) in enumerate(rows):
        games.setdefault((int(f), int(g)), []).append((r, int(e)))
    order = sorted(games, key=lambda k: games[k][-1][1])     # a game's rows are in ply order: last = longest
    grabbed = {}
    hooks = [m.blocks[int(L)].register_forward_hook(lambda mod, i, o, L=L: grabbed.__setitem__(L, o))
             for m, _ in models for L in a.layers if L != "final"]
    t0, done, s = time.time(), 0, 0
    try:
        while s < len(order):
            j = s + 1                                         # games are sorted by length: grow while it fits
            while j < len(order) and (j + 1 - s) * (games[order[j]][-1][1] + 1) <= a.max_tokens:
                j += 1
            batch, s = order[s:j], j
            T = games[batch[-1]][-1][1] + 1
            x = torch.full((len(batch), T), SPACE, dtype=torch.long)
            bi, ci, ri = [], [], []
            for b, k in enumerate(batch):
                ids = corpus.ids(*k, T)
                x[b, :len(ids)] = ids
                for r, e in games[k]:
                    bi.append(b), ci.append(e), ri.append(r)
            x = x.to(dev)
            bi, ci, ri = torch.tensor(bi, device=dev), torch.tensor(ci, device=dev), np.array(ri)
            perm = np.argsort(ri)                             # memmap writes in row order
            for i, (m, _) in enumerate(models):
                with torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev == "cuda"):
                    feats = m.features(x)
                for L in a.layers:
                    h = feats if L == "final" else grabbed[L]
                    out[i, L][ri[perm]] = h[bi, ci].float().cpu().numpy()[perm]
            done += len(ri)
            print(f"\r  {done}/{len(rows)} positions  {time.time() - t0:.0f}s", end="", flush=True)
    finally:
        for h in hooks:
            h.remove()
    print()
    for arr in out.values():
        arr.flush()
    (run / "collect.json").write_text(json.dumps(dict(
        models=a.models, names=names, layers=a.layers, folders=a.pgn_data, folder_names=corpus.names,
        positions=len(rows), games=len(games), per_game=a.per_game, min_ply=a.min_ply, d=d), indent=1))
    print(f"wrote {run / 'acts'}: {len(out)} arrays of {len(rows)} x {d}")
    return run


# ---------------------------------------------------------------- the crosscoder

class CrossCoder(nn.Module):
    def __init__(self, S, d, latents, k):
        super().__init__()
        dec = torch.randn(latents, S, d)
        dec = dec / dec.norm(dim=-1, keepdim=True) / S                    # norms sum to 1 over sources
        self.W_dec = nn.Parameter(dec)                                     # (latents, sources, d)
        self.W_enc = nn.Parameter(dec.reshape(latents, S * d).T.clone())   # (sources * d, latents)
        self.b_enc = nn.Parameter(torch.zeros(latents))
        self.b_dec = nn.Parameter(torch.zeros(S, d))
        self.register_buffer("theta", torch.tensor(-1.0))                  # inference threshold
        self.k = k

    def norms(self):
        return self.W_dec.norm(dim=-1)                                     # (latents, sources)

    @torch.no_grad()
    def normalise(self):
        """Each latent's decoder norms sum to 1 over the sources; how they split between models stays free.
        Without it, AuxK shrinks dead latents' decoders (the residual they fit is small), which lowers
        their selection score (activation x norm), so they never come back."""
        self.W_dec /= self.norms().sum(1).clamp_min(1e-8)[:, None, None]

    def encode(self, x, batch_topk=False):
        """x (b, sources, d) -> (f, pre-activations, smallest selected score)."""
        p = (x - self.b_dec).flatten(1) @ self.W_enc + self.b_enc
        a = F.relu(p)
        score = a * self.norms().sum(1)
        if batch_topk:
            top = score.flatten().topk(self.k * len(x))
            keep = torch.zeros(score.numel(), dtype=torch.bool, device=x.device)
            keep[top.indices] = True
            return a * keep.view_as(a), p, top.values[-1].detach()
        return a * (score > self.theta), p, None

    def decode(self, f):
        return (f @ self.W_dec.flatten(1)).view(len(f), *self.b_dec.shape) + self.b_dec


def load_sources(run, sources):
    """Memmaps of the (model, layer) activation files, in source order."""
    info = json.loads((run / "collect.json").read_text())
    return [np.load(run / "acts" / f"{source_name(info['names'][m], L)}.npy", mmap_mode="r") for m, L in sources]


def stack(arrs, idx, scales, dev):
    """(len(idx), sources, d) float32 on dev, scaled."""
    x = torch.from_numpy(np.stack([np.asarray(arr[idx]) for arr in arrs], 1).astype(np.float32)).to(dev)
    return x * scales[None, :, None]


def train(a, layers):
    run = Path(a.run)
    info = json.loads((run / "collect.json").read_text())
    missing = [L for L in layers if L not in info["layers"]]
    if missing:
        sys.exit(f"layers {missing} were not collected (have {info['layers']})")
    sources = [(m, L) for m in range(len(info["names"])) for L in layers]
    cc_dir = run / ("cc-L" + "+".join(layers))
    cc_dir.mkdir(exist_ok=True)
    arrs = load_sources(run, sources)
    rows = np.load(run / "rows.npy")
    dev = ev.device(a.device)
    torch.manual_seed(a.seed)
    torch.backends.cuda.matmul.allow_tf32 = True
    held = (rows[:, 0] * 1_000_003 + rows[:, 1]) % 50 == 0                 # held out by game, ~2%
    val_idx, tr_idx = np.flatnonzero(held)[:20_000], np.flatnonzero(~held)
    S, d = len(sources), info["d"]
    print(f"loading {len(rows)} x {S} sources ({', '.join(source_name(info['names'][m], L) for m, L in sources)})",
          flush=True)
    X = torch.empty((len(rows), S, d), dtype=torch.float16)
    for s, arr in enumerate(arrs):
        for i in range(0, len(rows), 200_000):
            X[i:i + 200_000, s] = torch.from_numpy(np.array(arr[i:i + 200_000]))
    sample = X[torch.from_numpy(tr_idx[:100_000])].float()
    scales = (math.sqrt(d) / sample.norm(dim=-1).mean(0)).to(dev)          # each source at mean norm sqrt(d)
    data_dev = "cpu" if a.data_on_cpu else dev
    X = X.to(data_dev)
    tr = torch.from_numpy(tr_idx).to(data_dev)
    val = X[torch.from_numpy(val_idx).to(data_dev)].to(dev).float() * scales[None, :, None]
    cc = CrossCoder(S, d, a.latents, a.k).to(dev)
    with torch.no_grad():
        cc.b_dec.copy_((sample.to(dev) * scales[None, :, None]).mean(0))
        var = ((sample.to(dev) * scales[None, :, None]) - cc.b_dec).pow(2).sum((1, 2)).mean()
    del sample
    opt = torch.optim.Adam(cc.parameters(), lr=a.lr, betas=(0.9, 0.999))
    last_fired = torch.zeros(a.latents, dtype=torch.long, device=dev)
    log = open(cc_dir / "train_log.jsonl", "w", encoding="utf-8")
    t0 = time.time()
    print(f"{len(tr_idx)} training positions, {len(val_idx)} held out (by game); {a.latents} latents, "
          f"k = {a.k}, {a.steps} steps of {a.batch}", flush=True)
    for step in range(1, a.steps + 1):
        lr = a.lr * min(1.0, step / 200) * min(1.0, 5 * (a.steps - step) / a.steps)
        for g in opt.param_groups:
            g["lr"] = lr
        x = X[tr[torch.randint(0, len(tr), (a.batch,), device=data_dev)]].to(dev, non_blocking=True).float()
        x = x * scales[None, :, None]
        f, p, smallest = cc.encode(x, batch_topk=True)
        x_hat = cc.decode(f)
        mse = (x_hat - x).pow(2).sum((1, 2)).mean() / var
        with torch.no_grad():
            cc.theta.copy_(smallest if cc.theta < 0 else 0.99 * cc.theta + 0.01 * smallest)
        last_fired[(f > 0).any(0)] = step
        dead = (step - last_fired) > a.dead_steps
        loss, aux = mse, torch.zeros((), device=dev)
        if dead.any():                                                     # AuxK: dead latents model the residual
            top = p.masked_fill(~dead[None, :], -float("inf")).topk(min(a.k_aux, int(dead.sum())), dim=-1)
            z = torch.zeros_like(p).scatter_(-1, top.indices, F.relu(top.values))
            e = (x - x_hat).detach()
            aux = ((z @ cc.W_dec.flatten(1)).view_as(e) - e).pow(2).sum((1, 2)).mean() / e.pow(2).sum((1, 2)).mean().clamp_min(1e-8)
            loss = loss + a.aux_coef * aux
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        cc.normalise()
        if step % a.eval_every == 0 or step == a.steps:
            fvu, l0 = evaluate(cc, val)
            row = dict(step=step, train_nmse=float(mse.detach()), aux=float(aux.detach()), val_fvu={source_name(info["names"][m], L): v
                       for (m, L), v in zip(sources, fvu)}, val_l0=l0, dead_frac=float(dead.float().mean()),
                       theta=float(cc.theta), lr=lr)
            log.write(json.dumps(row) + "\n")
            log.flush()
            print(f"  step {step}  train nmse {row['train_nmse']:.4f}  held-out FVU "
                  + " ".join(f"{k} {v:.3f}" for k, v in row["val_fvu"].items())
                  + f"  L0 {l0:.1f}  dead {100 * row['dead_frac']:.1f}%  {time.time() - t0:.0f}s", flush=True)
    torch.save(dict(state=cc.state_dict(), sources=sources, d=d, latents=a.latents, k=a.k, scales=scales.cpu(),
                    val_fvu=row["val_fvu"], val_l0=l0, dead_frac=row["dead_frac"], args=vars(a)), cc_dir / "cc.pt")
    print(f"wrote {cc_dir / 'cc.pt'}")
    return cc_dir


@torch.no_grad()
def evaluate(cc, val):
    """Fraction of variance unexplained per source, and mean active latents, at the inference threshold."""
    err = torch.zeros(val.shape[1], device=val.device)
    l0 = 0.0
    for i in range(0, len(val), 4096):
        x = val[i:i + 4096]
        f, _, _ = cc.encode(x)
        err += (cc.decode(f) - x).pow(2).sum((0, 2))
        l0 += float((f > 0).sum())
    tot = (val - val.mean(0)).pow(2).sum((0, 2))
    return (err / tot).tolist(), l0 / len(val)


# ---------------------------------------------------------------- latents and their positions

def position(corpus, row):
    f, g, ply, _ = (int(v) for v in row)
    sans, _ = parse_movetext(corpus.text(f, g))
    b = ev.board_of(sans[:ply])
    return b, sans[ply], corpus.names[f]


def model_moves(models, boards, dev):
    """Per model, per board: (top move SAN, its probability, probability of each legal move by SAN)."""
    out = []
    for m, _ in models:
        moves, lp = ev.score(m, boards, [1.0], dev)
        per = []
        for b, mv, l in zip(boards, moves, lp[0]):
            p = np.exp(l - l.max())
            p /= p.sum()
            sans = [b.san(x) for x in mv]
            j = int(p.argmax())
            per.append((sans[j], float(p[j]), dict(zip(sans, p.tolist()))))
        out.append(per)
    return out


@torch.no_grad()
def top(a, cc_dir):
    cc_dir = Path(cc_dir)
    run = cc_dir.parent
    info = json.loads((run / "collect.json").read_text())
    ck = torch.load(cc_dir / "cc.pt", map_location="cpu", weights_only=False)
    sources = [tuple(s) for s in ck["sources"]]
    dev = ev.device(a.device)
    cc = CrossCoder(len(sources), ck["d"], ck["latents"], ck["k"]).to(dev)
    cc.load_state_dict(ck["state"])
    scales = ck["scales"].to(dev)
    names = info["names"]
    A, B = names

    dn = cc.norms()                                                        # (latents, sources)
    nm = torch.stack([dn[:, [s for s, (m, _) in enumerate(sources) if m == i]].pow(2).sum(1).sqrt()
                      for i in range(2)], 1)
    r = (nm[:, 1] / nm.sum(1).clamp_min(1e-12)).cpu().numpy()
    layers = sorted({L for _, L in sources}, key=str)
    cos = torch.stack([F.cosine_similarity(cc.W_dec[:, sources.index((0, L))], cc.W_dec[:, sources.index((1, L))], dim=-1)
                       for L in layers], 1).mean(1).cpu().numpy()

    arrs = load_sources(run, sources)
    rows = np.load(run / "rows.npy")
    folder_of = rows[:, 0]
    nf = len(info["folder_names"])
    Lt, E = ck["latents"], a.examples
    best_v = torch.full((Lt, E), -1.0, device=dev)
    best_i = torch.zeros((Lt, E), dtype=torch.long, device=dev)
    count = torch.zeros((nf, Lt), device=dev)
    for s in range(0, len(rows), 4096):
        idx = np.arange(s, min(s + 4096, len(rows)))
        f, _, _ = cc.encode(stack(arrs, idx, scales, dev))
        fo = torch.from_numpy(folder_of[idx]).to(dev)
        for j in range(nf):
            count[j] += (f[fo == j] > 0).sum(0)
        v = torch.cat([best_v, f.T], 1)
        i = torch.cat([best_i, torch.from_numpy(idx).to(dev).expand(Lt, -1)], 1)
        keep = v.topk(E, dim=1)
        best_v, best_i = keep.values, i.gather(1, keep.indices)
        print(f"\r  encoded {idx[-1] + 1}/{len(rows)}", end="", flush=True)
    print()
    n_f = torch.tensor([(folder_of == j).sum() for j in range(nf)], device=dev, dtype=torch.float)
    rate, rate_f = (count.sum(0) / len(rows)).cpu().numpy(), (count / n_f[:, None]).cpu().numpy()
    best_v, best_i = best_v.cpu().numpy(), best_i.cpu().numpy()
    alive = rate > 0

    with open(cc_dir / "latents.jsonl", "w", encoding="utf-8") as f:
        for j in range(Lt):
            f.write(json.dumps(dict(latent=j, rel_norm=float(r[j]), cos=float(cos[j]), rate=float(rate[j]),
                                    rate_by_folder={n: float(rate_f[k, j]) for k, n in enumerate(info["folder_names"])},
                                    top=[(int(i), float(v)) for i, v in zip(best_i[j], best_v[j]) if v > 0])) + "\n")

    x_ = a.exclusive
    groups = {"A": alive & (r < x_), "B": alive & (r > 1 - x_), "shared": alive & (np.abs(r - 0.5) < 0.2)}
    ok = (rate >= a.min_rate) & (rate <= a.max_rate)
    picks = {g: sorted(np.flatnonzero(m & ok), key=lambda j: -best_v[j, 0])[:a.report] for g, m in groups.items()}
    picks["shared, dissimilar decoders"] = sorted(np.flatnonzero(groups["shared"] & ok & (cos < 0.5)),
                                                  key=lambda j: -best_v[j, 0])[:a.report]
    picks["shared"] = picks["shared"][:max(10, a.report // 3)]

    shown = sorted({int(i) for js in picks.values() for j in js for i, v in zip(best_i[j], best_v[j]) if v > 0})
    corpus = Corpus(info["folders"])
    pos = {i: position(corpus, rows[i]) for i in shown}
    moves = {}
    if not a.no_model_moves and shown:
        print(f"  each model's move on {len(shown)} example positions", flush=True)
        models = [ev.load(m, dev) for m in info["models"]]
        mm = model_moves(models, [pos[i][0] for i in shown], dev)
        moves = {i: (mm[0][n], mm[1][n]) for n, i in enumerate(shown)}

    out = RESULTS / run.name / cc_dir.name
    out.mkdir(parents=True, exist_ok=True)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.hist(r[alive], bins=50, range=(0, 1), color="#4a6fa5")
    ax.set_yscale("log")
    ax.set_xlabel(f"relative decoder norm  |d_{B}| / (|d_{A}| + |d_{B}|)")
    ax.set_ylabel("latents")
    ax.set_title(f"crosscoder {cc_dir.name}: 0 = only {A}, 1 = only {B}")
    fig.tight_layout()
    fig.savefig(out / "relative_norms.png", dpi=120)
    plt.close(fig)

    hist, _ = np.histogram(r[alive], bins=10, range=(0, 1))
    summary = dict(cc=cc_dir.name, sources=[source_name(names[m], L) for m, L in sources], latents=Lt, k=ck["k"],
                   val_fvu=ck["val_fvu"], val_l0=ck["val_l0"], dead_frac=ck["dead_frac"], alive=int(alive.sum()),
                   only_A=int(groups["A"].sum()), only_B=int(groups["B"].sum()), shared=int(groups["shared"].sum()),
                   shared_cos_median=float(np.median(cos[groups["shared"]])) if groups["shared"].any() else None,
                   rel_norm_hist=hist.tolist(), A=A, B=B)
    (out / "summary.json").write_text(json.dumps(summary, indent=1))

    titles = {"A": f"Only in {A} (r < {x_})", "B": f"Only in {B} (r > {1 - x_:.1f})",
              "shared, dissimilar decoders": "Shared (0.3 < r < 0.7), but the two decoders point different ways (cosine < 0.5)",
              "shared": "Shared (0.3 < r < 0.7), the strongest"}
    md = [f"# Crosscoder {A} vs {B}, {cc_dir.name}", "",
          f"BatchTopK crosscoder, {Lt} latents, k = {ck['k']} (held-out L0 {ck['val_l0']:.1f}), on {info['positions']} "
          f"positions from {info['games']} games ({', '.join(info['folder_names'])}).", "",
          "| source | held-out FVU |", "| --- | --- |",
          *[f"| {k} | {v:.3f} |" for k, v in ck["val_fvu"].items()], "",
          f"Latents firing at least once: {alive.sum()} ({100 * alive.mean():.1f}%). "
          f"Only {A}: **{summary['only_A']}**, only {B}: **{summary['only_B']}**, shared: **{summary['shared']}** "
          f"(median decoder cosine {summary['shared_cos_median'] or float('nan'):.2f}).", "",
          "Relative decoder norm, 10 bins from 0 (only " + A + ") to 1 (only " + B + "): " + " ".join(map(str, hist)), "",
          "![relative decoder norms](relative_norms.png)", "",
          "Each example: activation, folder, move and side to move, the last moves, **the move played**, then each "
          f"model's top move at T = 1 ({A} / {B}).", ""]
    page = [f"<!doctype html><meta charset='utf-8'><title>{html.escape(cc_dir.name)}</title>",
            "<style>body{font:14px system-ui,sans-serif;margin:24px;max-width:1300px}"
            ".ex{display:inline-block;width:230px;margin:6px;vertical-align:top;font-size:12px}"
            "h2{margin-top:40px}h3{margin-top:28px}code{font-size:12px}</style>",
            f"<h1>{html.escape(md[0][2:])}</h1><p>{html.escape(md[2])}</p>"]

    def said(i):
        if i not in moves:
            return ""
        (sa, pa, _), (sb, pb, _) = moves[i]
        return f"{sa} {100 * pa:.0f}% / {sb} {100 * pb:.0f}%"

    for g, js in picks.items():
        md += [f"## {titles[g]}", ""]
        page.append(f"<h2>{html.escape(titles[g])}</h2>")
        for j in js:
            rf = ", ".join(f"{n} {100 * rate_f[k, j]:.2f}%" for k, n in enumerate(info["folder_names"]))
            head = f"latent {j}: r = {r[j]:.2f}, cosine {cos[j]:.2f}, fires on {100 * rate[j]:.2f}% ({rf})"
            md += [f"### {head}", ""]
            page.append(f"<h3>{html.escape(head)}</h3>")
            for i, v in zip(best_i[j], best_v[j]):
                if v <= 0:
                    continue
                b, nxt, folder = pos[int(i)]
                side = "white" if b.turn == chess.WHITE else "black"
                text = last_moves(prompt(b))
                md.append(f"- {v:.2f} | {folder} | move {b.fullmove_number}, {side} | `{text}` -> **{nxt}** | "
                          f"{said(int(i))} | [board]({lichess(b.fen())})")
                mv = b.parse_san(nxt)
                svg = chess.svg.board(b, size=220, arrows=[chess.svg.Arrow(mv.from_square, mv.to_square)],
                                      flipped=b.turn == chess.BLACK)
                page.append(f"<div class='ex'>{svg}<br>{v:.2f} &middot; {html.escape(folder)} &middot; move "
                            f"{b.fullmove_number} ({side})<br><code>{html.escape(last_moves(prompt(b), 6))}</code> "
                            f"&rarr; <b>{html.escape(nxt)}</b><br>{html.escape(said(int(i)))} &middot; "
                            f"<a href='{lichess(b.fen())}'>lichess</a></div>")
            md.append("")
    (out / "report.md").write_text("\n".join(md), encoding="utf-8")
    (cc_dir / "features.html").write_text("\n".join(page), encoding="utf-8")
    print(f"wrote {out / 'report.md'}, {out / 'relative_norms.png'}, {cc_dir / 'latents.jsonl'} and {cc_dir / 'features.html'}")
    return summary


def sweep(run, summaries):
    """results/.../<run>/sweep.md: one line per crosscoder."""
    A, B = summaries[0]["A"], summaries[0]["B"]
    md = [f"# Crosscoder layer sweep, {A} vs {B}", "",
          f"| crosscoder | FVU {A} | FVU {B} | L0 | alive | only {A} | only {B} | shared | shared cosine (median) |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for s in summaries:
        fa = np.mean([v for k, v in s["val_fvu"].items() if k.startswith(A + "-")])
        fb = np.mean([v for k, v in s["val_fvu"].items() if k.startswith(B + "-")])
        md.append(f"| [{s['cc']}]({s['cc']}/report.md) | {fa:.3f} | {fb:.3f} | {s['val_l0']:.1f} | {s['alive']} | "
                  f"{s['only_A']} | {s['only_B']} | {s['shared']} | {s['shared_cos_median'] or float('nan'):.2f} |")
    out = RESULTS / Path(run).name / "sweep.md"
    out.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[2:]))
    print(f"wrote {out}")


# ---------------------------------------------------------------- command line

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for cmd in ("collect", "train", "top", "all", "sweep"):
        p = sub.add_parser(cmd)
        p.add_argument("--device", default="auto", help="auto, cuda, mps or cpu")
        p.add_argument("--seed", type=int, default=0)
        p.add_argument("--run", default=None, help="run folder (default runs/transcend/crosscoder/<A>__<B>)")
        if cmd in ("collect", "all"):
            p.add_argument("--models", nargs=2, default=MODELS, help="model A and model B (HF repo ids or .pt)")
            p.add_argument("--pgn-data", nargs="+", default=FOLDERS, help="make_pgn_data.py folders to sample games from")
            p.add_argument("--positions", type=int, default=1_000_000)
            p.add_argument("--per-game", type=int, default=16, help="random plies per game")
            p.add_argument("--min-ply", type=int, default=10)
            p.add_argument("--max-tokens", type=int, default=64 * 1024, help="characters per forward batch")
        if cmd in ("collect", "train", "all"):
            p.add_argument("--layers", nargs="+", required=cmd == "train",
                           default=None if cmd == "train" else ["4", "8", "12", "15", "final"],
                           help="block indices 0-15 or 'final'; train: several = one crosscoder across those layers")
        if cmd in ("train", "all"):
            p.add_argument("--latents", type=int, default=16384)
            p.add_argument("--k", type=int, default=64, help="active latents per position, on average over a batch")
            p.add_argument("--steps", type=int, default=30_000)
            p.add_argument("--batch", type=int, default=4096)
            p.add_argument("--lr", type=float, default=2e-4)
            p.add_argument("--k-aux", type=int, default=512, help="AuxK: dead latents used to model the residual")
            p.add_argument("--aux-coef", type=float, default=1 / 32)
            p.add_argument("--dead-steps", type=int, default=500, help="steps without firing before a latent counts as dead")
            p.add_argument("--eval-every", type=int, default=1000)
            p.add_argument("--data-on-cpu", action="store_true", help="keep the activations in RAM, not VRAM")
        if cmd == "top":
            p.add_argument("--cc", required=True, help="crosscoder folder name in the run, e.g. L12 or L8+12+15")
        if cmd in ("top", "all"):
            p.add_argument("--examples", type=int, default=12, help="top positions kept per latent")
            p.add_argument("--report", type=int, default=30, help="latents shown per group")
            p.add_argument("--exclusive", type=float, default=0.1, help="r below this: only A; above 1 - this: only B")
            p.add_argument("--min-rate", type=float, default=0.0005, help="report only latents firing at least this often")
            p.add_argument("--max-rate", type=float, default=0.2, help="... and at most this often")
            p.add_argument("--no-model-moves", action="store_true", help="skip each model's top move on the examples")
    a = ap.parse_args()
    if a.cmd in ("collect", "all"):
        a.run = str(collect(a))
    if not a.run:
        sys.exit("--run is required")
    if a.cmd == "train":
        train(a, a.layers)
    if a.cmd == "top":
        cc = a.cc if a.cc.startswith("cc-") else "cc-" + a.cc
        top(a, Path(a.run) / cc)
    if a.cmd == "all":
        summaries = [top(a, train(a, [L])) for L in a.layers]
        sweep(a.run, summaries)
    if a.cmd == "sweep":                                     # sweep.md from the crosscoders already through `top`
        found = sorted((RESULTS / Path(a.run).name).glob("cc-*/summary.json"), key=lambda f: f.stat().st_mtime)
        sweep(a.run, [json.loads(f.read_text()) for f in found])


if __name__ == "__main__":
    main()
