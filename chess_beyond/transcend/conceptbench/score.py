"""Score models on the concept dataset: Schut et al.'s static-concept validation.

    python transcend/conceptbench/score.py --family pieces,openings                       # the check first
    python transcend/conceptbench/score.py --family structures,imbalances,plans           # then the rest
    python transcend/conceptbench/score.py --models W=Arisp/chess-pgn-1000-1300 --layers 11,final   # any model, by name=spec
    python transcend/conceptbench/score.py --stage report

1. acts    the residual stream after a block (a number, 0-15), or after the final norm (final), at the token where the
           model writes its move: a position's prompt end. Attention is causal, so each game goes through once and is read
           at its positions. float16, cached in runs/transcend/conceptbench/acts/<model>/L<layer>.npy.
2. fit     per concept, per model and layer, the LP on the fit split, features standardised on the fit positions:
           min ||v||_1 + SLACK * mean(xi), subject to v . z+ >= v . z- + 1 - xi and xi >= 0, on up to --pairs sampled pairs.
3. score   on the test split: pair accuracy, the share of matched pairs with v . z+ > v . z- (a tie counts half), and AUC,
           over all the concept's test positives against its test negatives; 95% bootstrap intervals, resampling
           games (a pair weighs its two games' counts).
4. controls, run automatically
           shuffled   the same LP with each fit pair's order flipped at random (labels shuffled within pairs), scored on the
                      real test pairs, SHUFFLES times per cell: the mean over a family should be 0.5. One cell's can be far from it
                      for a strong concept: a random direction lands either way, since test pairs share a large mean difference
           random     a randomly initialised model of the same architecture, as a model of its own (--random-seed)
           crosscoder --models cc4096 --layers 11: features are a crosscoder's latents, W's and S's states encoded together
                      (one score for the pair); the same LP over all the latents, not one latent. Its comparison is W+S,
                      the two models' raw states side by side (1024 features): the same information, not re-encoded
           board      the same LP on a one-hot board (12 x 64, side to move, castling rights). The brief asks for it for
                      plans; it runs for every concept, since it says how much of a static label a linear read of the board gets.

-> results/transcend/conceptbench/<model>/L<layer>.json, board/board.json and report.md: concept x model x layer.
"""

import argparse
import json
import multiprocessing as mp
import os
import sys
import time
import zlib
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):       # one thread per LP worker
    os.environ.setdefault(_v, "1")

import chess
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bench import CONCEPTS, MANIFEST, POSITIONS, RESULTS, RUNS, paths

SLACK = 100.0               # the LP's price on mean slack, against ||v||_1 (README: how it was chosen)
CHECK_POSITIONS = 200       # positions per model read alone, to check the reads from whole games
SHUFFLES = 1                # shuffled-label LPs per concept, model and layer: one draw can land far from 0.5, the family mean should not
ACTS = RUNS / "acts"
LP_CACHE = RUNS / "lp"
RANDOM = "random-init"
BOARD = "board"
FAMILY_ORDER = ("pieces", "openings", "structures", "imbalances", "plans", "stockfish_terms")
MODELS = {"W": "Arisp/chess-pgn-1000-1300", "S": "Arisp/chess-pgn-2400plus",
          "W-rl": "runs/transcend/rl-pgn-1000-1300-all.pt", "W-rl-b0.01": "runs/transcend/rl-pgn-1000-1300-all-b0.01.pt",
          "S-rl": "runs/transcend/rl-pgn-2400+-all.pt", "S-rl-b0.01": "runs/transcend/rl-pgn-2400+-all-b0.01.pt",
          RANDOM: RANDOM,
          "cc4096": "cc:runs/transcend/crosscoder/mixed-L{layer}/cc-L{layer}-4096/cc.pt",          # crossmix.py, one per layer
          "cc4096-s1": "cc:runs/transcend/crosscoder/mixed-L{layer}/cc-L{layer}-4096-s1/cc.pt",
          "cc4096-Wview": "ccW:runs/transcend/crosscoder/mixed-L{layer}/cc-L{layer}-4096/cc.pt",       # W's state alone
          "cc4096-Sview": "ccS:runs/transcend/crosscoder/mixed-L{layer}/cc-L{layer}-4096/cc.pt",
          "W+S": "concat:W,S"}             # both models' raw states side by side: what a crosscoder of the two reads


# ---------------------------------------------------------------- activations
def game_sequences(df, ctx):
    """Each game once, as far as its last position -> token sequences, per game the prompt ends, per game the pos_ids."""
    from pgn_model import MAX_MOVE_CHARS, encode
    seqs, ends, ids = [], [], []
    for _, g in df.groupby("game_id", sort=False):
        g = g.sort_values("ply")
        last = g["prompt"].iloc[-1]
        for p in g["prompt"]:
            if not last.startswith(p):
                sys.exit(f"game {g['game_id'].iloc[0]}: a prompt is not a prefix of the game's last one")
        if len(last) + MAX_MOVE_CHARS + 1 > ctx:
            sys.exit("a prompt does not fit the context")
        seqs.append(encode(last))
        ends.append([len(p) - 1 for p in g["prompt"]])
        ids.append(g["pos_id"].to_numpy())
    return seqs, ends, ids


def load_model(name, spec, dev, seed):
    import torch
    import eval as ev
    from pgn_model import PGNTransformer
    if spec == RANDOM:
        torch.manual_seed(seed)
        return PGNTransformer().to(dev).eval()         # the paper's architecture, the same as every other model here
    if spec.endswith(".pt") and not Path(spec).is_absolute():
        spec = str(paths.ROOT / spec)
    return ev.load(spec, dev)[0]


def encode_cc(name, spec, layers, df):
    """A crosscoder's latents as a model's features: W's and S's cached states at its layer, scaled as in training, encoded
    together at the inference threshold -> one (positions, latents) array for the pair. spec: cc:<path to cc.pt>, with
    {layer} for one crosscoder per layer. Stats over every fit position, not a sample: a rare latent missed by a sample
    would get sd at the floor and be scaled 1000x.
    ccW:/ccS: one model's view: that model's state, the other's held at its mean over the fit positions, so the same
    dictionary gives each model its own score."""
    kind, _, path = spec.partition(":")
    view = {"cc": None, "ccW": 0, "ccS": 1}[kind]
    for L in layers:
        encode_cc_layer(name, path.format(layer=L), L, df, view)


def encode_cc_layer(name, path, L, df, view=None):
    import torch
    import crosscoder as cx
    out = ACTS / name / f"L{L}.npy"
    if out.exists():
        return
    ck = torch.load(paths.ROOT / path, map_location="cpu", weights_only=False)
    srcs = [tuple(s) for s in ck["sources"]]
    if srcs != [(0, L), (1, L)]:
        sys.exit(f"{name}: {path} has sources {srcs}, not W and S at L{L}")
    out.parent.mkdir(parents=True, exist_ok=True)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    cc = cx.CrossCoder(2, ck["d"], ck["latents"], ck["k"]).to(dev)
    cc.load_state_dict(ck["state"])
    scales = ck["scales"].to(dev)
    src = [np.load(ACTS / m / f"L{L}.npy", mmap_mode="r") for m in ("W", "S")]            # sources: 0 = W, 1 = S
    F_ = np.lib.format.open_memmap(out.with_suffix(".tmp.npy"), mode="w+", dtype=np.float16, shape=(len(df), ck["latents"]))
    err, tot, l0, fired = np.zeros(2), np.zeros(2), 0.0, np.zeros(ck["latents"], bool)
    mean = np.stack([s.mean(0, dtype=np.float64) for s in src])
    fit_mean = [torch.from_numpy(np.load(ACTS / m / f"L{L}.stats.npz")["mean"]).float().to(dev) for m in ("W", "S")]
    with torch.no_grad():
        for i in range(0, len(df), 8192):
            x = torch.from_numpy(np.stack([np.asarray(s[i:i + 8192], np.float32) for s in src], 1)).to(dev) * scales[None, :, None]
            if view is not None:
                x[:, 1 - view] = fit_mean[1 - view] * scales[1 - view]
            f, _, _ = cc.encode(x)
            xh = cc.decode(f)
            err += (xh - x).pow(2).sum((0, 2)).cpu().numpy()
            tot += (x - torch.from_numpy(mean).float().to(dev)[None] * scales[None, :, None]).pow(2).sum((0, 2)).cpu().numpy()
            l0 += float((f > 0).sum())
            fired |= (f > 0).any(0).cpu().numpy()
            F_[i:i + len(x)] = f.cpu().numpy().astype(np.float16)
    F_.flush()
    del F_
    os.replace(out.with_suffix(".tmp.npy"), out)
    fvu = err / tot
    print(f"  {name}: FVU W {fvu[0]:.3f} S {fvu[1]:.3f} on these positions (training held-out: {ck['val_fvu']}); "
          f"L0 {l0 / len(df):.1f}; latents firing {fired.sum()} of {len(fired)}", flush=True)
    if view is None and fvu.max() > 0.2:
        sys.exit(f"{name}: FVU {fvu} here, far above training's: the states are not what it was trained on")
    X = np.load(out, mmap_mode="r")
    is_fit = pd_split_is_fit()
    S = np.asarray(X[np.flatnonzero(is_fit)], np.float64)
    np.savez(ACTS / name / f"L{L}.stats.npz", mean=S.mean(0), sd=np.maximum(S.std(0), 1e-3))


def pd_split_is_fit():
    import pandas as pd
    return pd.read_parquet(POSITIONS, columns=["split"])["split"].to_numpy() == "fit"


def extract(name, spec, layers, df, a):
    """The states at every position for the layers not cached yet."""
    if spec.startswith(("cc:", "ccW:", "ccS:")):
        return encode_cc(name, spec, layers, df)
    if spec.startswith("concat:"):
        for L in layers:
            out = ACTS / name / f"L{L}.npy"
            if not out.exists():
                out.parent.mkdir(parents=True, exist_ok=True)
                np.save(out, np.concatenate([np.load(ACTS / m / f"L{L}.npy") for m in spec[7:].split(",")], 1))
        return
    import torch
    from pgn_model import SPACE, encode
    out = ACTS / name
    todo = [L for L in layers if not (out / f"L{L}.npy").exists()]
    if not todo:
        return
    out.mkdir(parents=True, exist_ok=True)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    t0 = time.time()
    model = load_model(name, spec, dev, a.random_seed)
    if len(model.blocks) != 16:
        sys.exit(f"{name}: {len(model.blocks)} blocks")
    seqs, ends, ids = game_sequences(df, model.ctx)
    grabbed = {}
    hooks = [model.blocks[int(L)].register_forward_hook(lambda m, i, o, L=L: grabbed.__setitem__(L, o)) for L in todo if L != "final"]
    X = {L: np.zeros((len(df), model.ln.normalized_shape[0]), np.float16) for L in todo}
    order = sorted(range(len(seqs)), key=lambda i: len(seqs[i]))
    s = 0
    with torch.inference_mode():
        while s < len(order):
            j = s + 1
            while j < len(order) and (j + 1 - s) * len(seqs[order[j]]) <= a.max_tokens:
                j += 1
            batch, s = order[s:j], j
            x = torch.full((len(batch), len(seqs[batch[-1]])), SPACE, dtype=torch.long)
            bi, ci, oi = [], [], []
            for r, i in enumerate(batch):
                x[r, :len(seqs[i])] = torch.tensor(seqs[i])
                bi += [r] * len(ends[i])
                ci += ends[i]
                oi.append(ids[i])
            oi = np.concatenate(oi)
            with torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev == "cuda"):
                feats = model.features(x.to(dev))
            bt, ct = torch.tensor(bi, device=dev), torch.tensor(ci, device=dev)
            for L in todo:
                h = feats if L == "final" else grabbed[L]
                X[L][oi] = h[bt, ct].float().cpu().numpy().astype(np.float16)
    # the shortcut's check: a position read from its prompt alone, against the read from its whole game
    rng = np.random.default_rng(0)
    rel = {L: [] for L in todo}
    with torch.inference_mode(), torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev == "cuda"):
        for i in rng.choice(len(df), CHECK_POSITIONS, replace=False):
            feats = model.features(torch.tensor([encode(df["prompt"].iloc[int(i)])], device=dev))
            for L in todo:
                alone = (feats if L == "final" else grabbed[L])[0, -1].float().cpu().numpy()
                rel[L].append(np.linalg.norm(alone - X[L][int(i)].astype(np.float32)) / np.linalg.norm(alone))
    for h in hooks:
        h.remove()
    for L in todo:
        if not np.isfinite(X[L]).all():
            sys.exit(f"{name} L{L}: non-finite activations")
        print(f"  {name} L{L}: read alone against read from the game, relative difference: median {np.median(rel[L]):.4f}, "
              f"max {np.max(rel[L]):.4f}", flush=True)
        if np.median(rel[L]) > 0.05:
            sys.exit(f"{name} L{L}: the two reads disagree, stopping")
        np.save(out / f"L{L}.npy", X[L])
    del model
    torch.cuda.empty_cache()
    print(f"  {name}: L{', L'.join(todo)} ({(time.time() - t0) / 60:.1f} min)", flush=True)


def board_features(df):
    """One-hot pieces, side to move, castling rights: 773 columns, cached."""
    path = ACTS / BOARD / "Lboard.npy"
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    X = np.zeros((len(df), 773), np.float16)
    for i, fen in enumerate(df["fen"]):
        b = chess.Board(fen)
        for sq, p in b.piece_map().items():
            X[i, (p.piece_type - 1 + 6 * (p.color == chess.BLACK)) * 64 + sq] = 1
        X[i, 768] = b.turn == chess.WHITE
        X[i, 769:773] = [b.has_kingside_castling_rights(chess.WHITE), b.has_queenside_castling_rights(chess.WHITE),
                         b.has_kingside_castling_rights(chess.BLACK), b.has_queenside_castling_rights(chess.BLACK)]
    np.save(path, X)


def feature_stats(name, L, is_fit):
    """Mean and standard deviation over the fit positions, cached next to the activations."""
    path = ACTS / name / f"L{L}.stats.npz"
    if not path.exists():
        X = np.load(ACTS / name / f"L{L}.npy", mmap_mode="r")
        idx = np.flatnonzero(is_fit)
        S = np.asarray(X[idx[:: max(1, len(idx) // 50_000)]], np.float64)
        np.savez(path, mean=S.mean(0), sd=np.maximum(S.std(0), 1e-3))


# ---------------------------------------------------------------- the LP and its scores
def solve_lp(d, slack):
    """min ||v||_1 + slack * mean(xi) subject to d v + xi >= 1, xi >= 0; d: (pairs, features) -> v."""
    from scipy import sparse
    from scipy.optimize import linprog
    n, m = d.shape[1], d.shape[0]
    A = sparse.hstack([sparse.csr_matrix(-d), sparse.csr_matrix(d), -sparse.identity(m, format="csr")], format="csr")
    c = np.r_[np.ones(2 * n), np.full(m, slack / m)]
    r = linprog(c, A_ub=A, b_ub=-np.ones(m), bounds=(0, None), method="highs-ipm")
    if r.status != 0:
        raise RuntimeError(f"the LP failed: {r.message}")
    return r.x[:n] - r.x[n:2 * n]


def order_hits(s_pos, s_neg):
    return (s_pos > s_neg) + 0.5 * (s_pos == s_neg)


def auc_of(scores, is_pos, w):
    """Weighted Mann-Whitney, ties half: scores sorted once by the caller."""
    wp, wn = w * is_pos, w * ~is_pos
    groups = np.r_[0, np.cumsum(scores[1:] != scores[:-1])]
    gn = np.bincount(groups, wn)
    gbelow = np.cumsum(gn) - gn
    u = (wp * (gbelow[groups] + 0.5 * gn[groups])).sum()
    return u / max(wp.sum() * wn.sum(), 1e-12)


def intervals(hit, g_pos, g_neg, scores, is_pos, g_all, n_games, rng, n):
    """Pair accuracy and AUC with 95% bootstrap intervals over games."""
    order = np.argsort(scores)
    s, ip, ga = scores[order], is_pos[order], g_all[order]
    acc, auc = [], []
    for _ in range(n):
        w = rng.multinomial(n_games, np.full(n_games, 1 / n_games)).astype(np.float64)
        pw = w[g_pos] * w[g_neg]
        acc.append((pw * hit).sum() / max(pw.sum(), 1e-12))
        auc.append(auc_of(s, ip, w[ga]))
    return np.quantile(acc, [.025, .975]).tolist(), np.quantile(auc, [.025, .975]).tolist()


_mem = {}
game_of = None


def init_worker(games):
    global game_of
    game_of = games


def get_x(name, L):
    if (name, L) not in _mem:
        _mem[(name, L)] = (np.load(ACTS / name / f"L{L}.npy", mmap_mode="r"), np.load(ACTS / name / f"L{L}.stats.npz"))
    return _mem[(name, L)]


def score_job(job):
    """One concept, one model and layer: the LP, its shuffled control, the test scores -> the result row."""
    name, L, concept, pairs_max, slack, boot, seed = job
    t0 = time.time()
    path = LP_CACHE / name / f"L{L}" / f"{concept}-p{pairs_max}-c{slack:g}-b{boot}-s{SHUFFLES}.json"
    if path.exists():
        return name, L, concept, json.loads(path.read_text(encoding="utf-8"))
    import pyarrow.parquet as pq
    t = pq.read_table(CONCEPTS / f"{concept}.parquet").to_pydict()
    split, pos, neg = np.array(t["split"]), np.array(t["pos"]), np.array(t["neg"])
    X, st = get_x(name, L)
    mean, sd = st["mean"], st["sd"]
    Z = lambda idx: (np.asarray(X[idx], np.float64) - mean) / sd
    rng = np.random.default_rng(zlib.crc32(f"{name}/{L}/{concept}/{seed}".encode()))
    fit = np.flatnonzero(split == "fit")
    fit = rng.choice(fit, min(pairs_max, len(fit)), replace=False)
    d = Z(pos[fit]) - Z(neg[fit])
    v = solve_lp(d, slack)
    v_shuf = [solve_lp(d * rng.choice([-1.0, 1.0], len(d))[:, None], slack) for _ in range(SHUFFLES)]
    te = split == "test"
    tp, tn = pos[te], neg[te]
    zp, zn = Z(tp), Z(tn)
    hit = order_hits(zp @ v, zn @ v)
    shuf = [float(order_hits(zp @ u, zn @ u).mean()) for u in v_shuf]
    # AUC over the concept's test positions (each once), bootstrap over their games
    up, un = np.unique(tp), np.unique(tn)
    upos = np.intersect1d(up, un)
    if len(upos):
        raise RuntimeError(f"{concept}: positions both positive and negative")
    all_ids = np.r_[up, un]
    is_pos = np.r_[np.ones(len(up), bool), np.zeros(len(un), bool)]
    score_all = Z(all_ids) @ v
    games, g_inv = np.unique(game_of[np.r_[all_ids, tp, tn]], return_inverse=True)
    ga, gp, gn = g_inv[:len(all_ids)], g_inv[len(all_ids):len(all_ids) + len(tp)], g_inv[len(all_ids) + len(tp):]
    acc_ci, auc_ci = intervals(hit, gp, gn, score_all, is_pos, ga, len(games), rng, boot)
    s_all = np.argsort(score_all)
    auc = auc_of(score_all[s_all], is_pos[s_all], np.ones(len(all_ids)))
    res = dict(accuracy=float(hit.mean()), accuracy_ci=acc_ci, auc=float(auc), auc_ci=auc_ci,
               shuffled_accuracy=float(np.mean(shuf)), shuffled_min=min(shuf), shuffled_max=max(shuf), fit_accuracy=float((d @ v > 0).mean()),
               nonzero=int((np.abs(v) > 1e-6).sum()), norm1=float(np.abs(v).sum()), fit_pairs=len(fit), test_pairs=int(te.sum()),
               test_games=len(games), seconds=time.time() - t0)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(res), encoding="utf-8")
    return name, L, concept, res


# ---------------------------------------------------------------- report
def layer_name(L):
    return "board" if L == BOARD else f"L{L}"


def report(man, models, layers):
    fam = {k: c["family"] for k, c in man["concepts"].items()}
    R = {}
    for m in list(models) + [BOARD]:
        for L in ([BOARD] if m == BOARD else layers):
            p = RESULTS / m / f"{layer_name(L)}.json"
            if p.exists():
                R[m, L] = json.loads(p.read_text(encoding="utf-8"))
    out = ["# Known-concept scores", "",
           "Each cell: test pair accuracy (share of matched pairs ordered correctly by the concept vector) [95% bootstrap "
           "interval over games], and after `s` the shuffled-label control: one shuffled LP, so one cell can sit far from 0.50 for a "
           "strong concept, in either direction; read its family mean in the table under each family. `board` is the LP on a one-hot board: "
           "the same fit, no model. `random-init` is an untrained model of the same architecture. Chance is 0.50.", "",
           f"{len(man['concepts'])} concepts; {len(man['dropped'])} listed concepts dropped for too few positives, "
           f"{man['openings_below_threshold']} openings likewise.", ""]
    shown = [m for m in models if any((m, L) in R for L in layers)]
    for f in FAMILY_ORDER:
        names = [k for k in man["concepts"] if fam[k] == f]
        if not names or not any(k in R.get(key, {}) for k in names for key in R):
            continue
        for L in layers:
            if not any(k in R.get((m, L), {}) for m in shown for k in names):
                continue
            out += [f"## {f}, {layer_name(L)}", "", "| concept | fit + / test pairs | " + " | ".join(shown) + " | board |",
                    "|---|--:|" + "---|" * (len(shown) + 1)]
            for k in sorted(names):
                c = man["concepts"][k]
                cells = []
                for m in shown + [BOARD]:
                    r = R.get((m, BOARD if m == BOARD else L), {}).get(k)
                    cells.append("" if r is None else f"{r['accuracy']:.3f} [{r['accuracy_ci'][0]:.3f}, {r['accuracy_ci'][1]:.3f}] s{r['shuffled_accuracy']:.2f}")
                out.append(f"| {k} | {c['fit_pos']} / {c['test_pairs']} | " + " | ".join(cells) + " |")
            out.append("")
        out += [f"### {f}: mean pair accuracy and AUC over the family's concepts", "",
                "| model | layer | mean accuracy | mean AUC | mean shuffled | mean nonzero weights | mean fit accuracy |", "|---|---|--:|--:|--:|--:|--:|"]
        for (m, L), r in R.items():
            rows = [r[k] for k in names if k in r]
            if rows:
                out.append(f"| {m} | {layer_name(L)} | {np.mean([x['accuracy'] for x in rows]):.3f} | {np.mean([x['auc'] for x in rows]):.3f} | "
                           f"{np.mean([x['shuffled_accuracy'] for x in rows]):.3f} | {np.mean([x['nonzero'] for x in rows]):.0f} | {np.mean([x['fit_accuracy'] for x in rows]):.3f} |")
        out.append("")
    if man["dropped"]:
        out += ["## Dropped: too few positives in fit", "", ", ".join(f"{k} ({c['fit_pos']})" for k, c in sorted(man["dropped"].items())), ""]
    (RESULTS / "report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {RESULTS / 'report.md'}", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=("all", "acts", "lp", "report"), default="all")
    ap.add_argument("--models", default=",".join(MODELS), help="names from MODELS, or name=spec (HF repo or .pt checkpoint)")
    ap.add_argument("--layers", default="11,final")
    ap.add_argument("--family", default="", help="comma-separated; empty: every family")
    ap.add_argument("--concepts", default="", help="comma-separated; instead of --family")
    ap.add_argument("--pairs", type=int, default=2000, help="LP pairs per concept")
    ap.add_argument("--slack", type=float, default=SLACK)
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--max-tokens", type=int, default=40_000, help="characters per forward pass (VRAM)")
    ap.add_argument("--random-seed", type=int, default=0)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    import pandas as pd
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    specs = {}
    for part in a.models.split(","):
        k, _, v = part.partition("=")
        specs[k] = v or MODELS[k]
    layers = a.layers.split(",")
    if a.stage in ("all", "acts"):
        df = pd.read_parquet(POSITIONS, columns=["pos_id", "game_id", "ply", "prompt", "fen"])
        for name, spec in specs.items():
            extract(name, spec, layers, df, a)
        board_features(df)
    if a.stage in ("all", "lp"):
        df = pd.read_parquet(POSITIONS, columns=["split", "game_id"])
        is_fit = df["split"].to_numpy() == "fit"
        games = pd.factorize(df["game_id"])[0]
        targets = [(n, L) for n in specs for L in layers] + [(BOARD, BOARD)]
        for n, L in targets:
            feature_stats(n, L if n != BOARD else BOARD, is_fit)
        fams = a.family.split(",") if a.family else FAMILY_ORDER
        concepts = [c for c in a.concepts.split(",") if c] or \
            [k for f in fams for k, c in man["concepts"].items() if c["family"] == f]
        jobs = [(n, L, c, a.pairs, a.slack, a.boot, a.seed) for n, L in targets for c in concepts]
        print(f"{len(jobs)} LP jobs ({len(concepts)} concepts x {len(targets)} model-layers), {1 + SHUFFLES} LPs each", flush=True)
        t0 = time.time()
        R = {}
        for n, L in targets:                                            # results already written stay
            p = RESULTS / n / f"{layer_name(L)}.json"
            R[n, L] = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
        with mp.Pool(a.workers, init_worker, (games,)) as pool:
            for i, (n, L, c, res) in enumerate(pool.imap_unordered(score_job, jobs)):
                R[n, L][c] = res
                if i % 50 == 0 or i == len(jobs) - 1:
                    print(f"  {i + 1} of {len(jobs)}, {(time.time() - t0) / 60:.1f} min; {n} {layer_name(L)} {c}: "
                          f"{res['accuracy']:.3f} (shuffled {res['shuffled_accuracy']:.3f}; {res['seconds']:.0f}s)", flush=True)
                    write_results(R)
        write_results(R)
    if a.stage != "acts":
        report(man, list(specs), layers)


def write_results(R):
    for (n, L), r in R.items():
        p = RESULTS / n / f"{layer_name(L)}.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(r, indent=1, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
