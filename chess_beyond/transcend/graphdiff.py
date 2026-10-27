"""Concept-graph diff, the pilot's first pass: chains of crosscoder concepts the 2400+ model (S) follows
and the 1000-1300 model (W) doesn't, from the same root positions, kept only if they survive pruning.

    python transcend/graphdiff.py health --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal
    python transcend/graphdiff.py recall --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal
    python transcend/graphdiff.py lines  --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal
    python transcend/graphdiff.py nodes  --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal
    python transcend/graphdiff.py graph  --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal
    python transcend/graphdiff.py all    --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal

health  Gate 1, on the crosscoder's held-out games (crosscoder.py train's validation positions):
        - reconstruction: fraction of variance unexplained (FVU) per model;
        - spliced policy: each model's distribution over the legal moves with its state at the
          crosscoder's layer (at the prompt's last character, where the crosscoder reads it) replaced
          by the reconstruction: KL(real || spliced) and top-1 agreement; next to the same with the
          state replaced by its mean over the positions (the scale: "KL recovered" = 1 - KL spliced /
          KL mean) and with the real state put back (a check of the splice itself: KL ~ 0);
        - density: L0, dead latents (never fire), dense ones (fire on > 10% / > 50% of positions);
        - exclusivity: relative decoder norm r = |d_S| / (|d_S| + |d_W|) tags each latent S-only
          (r > 0.9), W-only (r < 0.1), shared (0.3-0.7) or leaning. The two models share no basis, so
          latent scaling (Minder et al. 2025) doesn't carry over; instead, a linear map (ridge) from
          each model's own states to the latent's activation, fitted on half the games, R^2 on the
          other half. An S-only latent is confirmed when W's states predict it at most half as well
          as S's (R^2_W <= 0.5 R^2_S), and the reverse for W-only.
        -> results/transcend/graphdiff/<run>/health.json; <run>/exclusivity.npz
recall  Gate 2, known-concept recall. Labels: explain.py's facts on its 100k stored positions (board
        facts, predicates.py; skill facts from Stockfish and Maia-2, skill.py; in facts.npz) and square
        facts (which piece stands where, squares.npz): run explain.py first. Per label, on one half of
        the games: the --cands latents whose mean activation differs most with and without it (in
        standard deviations), the best of them by AUC, and for board and skill labels the best
        combination of up to 3 of them (logistic regression, added greedily); AUC on the other half.
        Recall = the fraction of labels at held-out AUC >= --auc. Control: each label shuffled across
        positions (recall should be ~0). Lichess puzzle themes and STS aren't in the library: their
        positions come without a game history, which these models need.
        -> results/transcend/graphdiff/<run>/recall.json
lines   Roots: held-out positions of both bands (data/pgn_probe/population.jsonl, the validation games
        of each model's dataset), in the middlegame (after move 10, more than 6 pieces besides kings
        and pawns), where S's and W's most likely moves differ; --roots of them, half from each band,
        at most --per-game per game, split by game (--held % held out) before anything else.
        Policies are over the legal moves: a move's probability is the product of its characters'
        (each prompt's cache shared by all its legal moves); a move is drawn from p^(1/--temperature),
        renormalised. From each root, --plies plies:
            contrast A   "S": S plays both sides;  "W": W plays the root's side to move, S replies
            contrast B   "chosen": S's most likely move, "alt1".."alt4": its 2nd-5th; then S both sides
        Stockfish (--depth, the same for every line) on every position: the evaluation in pawns for
        the root's side to move (mates as +/- 15). Every position is read by both models and encoded
        with the crosscoder (and its FVU there: the crosscoder never saw rollouts); board facts
        (predicates.py, position facts) for the anchor nodes.
        -> <run>/lines.json, codes.npz, evals.npy, facts.npy, meta.json
nodes   Node filters on the fit roots, confirmed on the held-out ones. A contrast-B pair is (chosen,
        altK) where Stockfish prefers chosen's last position by >= --margin pawns; per pair and latent,
        d = sum over plies 1.. of (activation in chosen - in altK). A pair is informative for a latent
        when d != 0.
            1. active     fires on >= --min-rate of the line positions
            2. decision   >= --min-pairs informative fit pairs, one sign of d on >= --sep of them
                          (+ pursued, - avoided)
            3. held-out   >= --min-pairs-held informative held-out pairs, the same sign on >= --sep-held
        Null: the same filters with each pair's chosen/rejected labels flipped at random, --null times.
        Survivors (at most --max-nodes, by held-out sign agreement) are the latent nodes; board facts
        true on 1-99% of positions are anchor nodes. -> <run>/nodes.json
graph   G_S from the "S" lines, G_W from the "W" lines, same nodes, same roots (--split fit; held for
        the replication). A node is active at a ply when its activation is above its 90th percentile
        over all line positions (for a latent firing on < 10% of them: when it fires). Edges start only
        at plies where the studied player is to move (0, 2, 4, ...): plan edges at lags 2, 4, 6, response
        edges at lags 1, 3. Over (root, ply) pairs, n of them, n_A with A at t, n_B with B at t + k:
            lift_k(A -> B) = (n_AB + 1) / (n_A n_B / n + 1)        (P(B | A) / P(B), smoothed)
        delta = log lift_S - log lift_W; roots resampled (--boot Poisson bootstraps, one draw for both
        graphs), z = delta / its bootstrap sd, two-sided normal p, Benjamini-Hochberg at --fdr over
        every edge with n_AB >= --min-count in either graph (no self edges). S-only: significant, S's
        lift >= --lift with its 95% interval above 1, W's interval covering 1; W-only the reverse;
        reweighted: the other significant ones.
        Motifs: chains A -> B -> C (-> D) of lag-2 plan edges that pass (lift >= --lift, interval above
        1) in either graph. Per root, completions (A at t, B at t + 2, C at t + 4, ...) in its S line
        and its W line; log ratio of the totals (+1 each), the same bootstrap and FDR, over the chains
        with >= --min-count completions in either graph. Next to it the
        rate the chain completes once A fires, which separates "W doesn't reach A" from "W reaches A
        and goes elsewhere". The positional roots (W never loses more than --blunder pawns on one move
        of its line, by Stockfish) and the tactical ones are analysed separately. S-only latent nodes:
        their strongest lag-2 neighbours among shared nodes in G_S, and whether W's lines reach them.
        -> results/transcend/graphdiff/<run>/report.md (gates, funnel, diff, motifs),
           edges-<set>-<split>.csv, motifs-<set>-<split>.csv; <run>/motifs-<split>.html (the top --show
           motifs, each with prototype roots where it completes in the S line and not the W line).

All thresholds are starting values: set them once from the nulls, then freeze them before reading the diff.
"""
import argparse
import csv
import html
import json
import math
import os
import sys
import time
import zlib
from multiprocessing import Pool
from pathlib import Path
from types import SimpleNamespace

import chess
import chess.engine
import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parent))          # transcend/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))      # chess_beyond/
import paths
import eval as ev                                                 # load, board_of, device
import predicates
import skill
from concepts import Cache, extend, pad, room
from crosscoder import RESULTS as CC_RESULTS
from crosscoder import Corpus, CrossCoder, evaluate, load_sources, position, stack
from explain import NAMES as EXPLAIN_NAMES
from explain import refresh
from pages import BOARD_CSS, BOARD_DEFS, BOARD_JS, MOVE_HEAD
from pgn_model import MAX_MOVE_CHARS, SPACE, encode, prompt
from pgn_probe import DEFAULT as PROBE
from pgn_probe import parse_movetext

RUNS = paths.RUNS / "transcend" / "graphdiff"
RESULTS = paths.ROOT / "results" / "transcend" / "graphdiff"
KINDS = ["S", "W", "chosen", "alt1", "alt2", "alt3", "alt4"]
MATE_PAWNS = 15.0
ANCHORS = [n for n in predicates.NAMES if not n.startswith("move_")]   # position facts: the anchor nodes
PLAN, RESPONSE = (2, 4, 6), (1, 3)


# ---------------------------------------------------------------- the crosscoder and the policies

def load_cc(cc_run, cc, strong, dev):
    """The crosscoder, its (model, layer) sources and scales, which model is S (its name contains
    `strong`) and which W, and each latent's relative decoder norm toward S."""
    cc_run = Path(cc_run)
    cc_dir = cc_run / ("cc-" + cc.removeprefix("cc-"))
    info = json.loads((cc_run / "collect.json").read_text())
    ck = torch.load(cc_dir / "cc.pt", map_location="cpu", weights_only=False)
    sources = [tuple(s) for s in ck["sources"]]
    if sorted(m for m, _ in sources) != [0, 1]:
        sys.exit(f"graphdiff.py needs a crosscoder with one layer per model (this one has {sources})")
    coder = CrossCoder(len(sources), ck["d"], ck["latents"], ck["k"]).to(dev).eval()
    coder.load_state_dict(ck["state"])
    s = [i for i, n in enumerate(info["names"]) if strong in n]
    if len(s) != 1:
        sys.exit(f"--strong {strong!r} should match exactly one of {info['names']}")
    s = s[0]
    col = {m: k for k, (m, _) in enumerate(sources)}
    with torch.no_grad():
        nm = coder.norms()
        r = (nm[:, col[s]] / nm.sum(1).clamp_min(1e-8)).cpu().numpy()
    name = f"{cc_run.name}-{cc_dir.name.removeprefix('cc-')}"
    return SimpleNamespace(run=cc_run, dir=cc_dir, info=info, ck=ck, sources=sources, coder=coder,
                           scales=ck["scales"].to(dev), s=s, w=1 - s, col=col, layer=dict(sources), r=r,
                           out=RUNS / name, res=RESULTS / name)


def tag(r):
    if r > 0.9:
        return "S-only"
    if r < 0.1:
        return "W-only"
    if 0.3 <= r <= 0.7:
        return "shared"
    return "leaning S" if r > 0.5 else "leaning W"


def encode_states(cc, st):
    """{model: (n, d)} states at the crosscoder's layer -> latent activations (n, latents), scaled input."""
    x = torch.stack([st[m].float() for m, _ in cc.sources], 1) * cc.scales[None, :, None]
    return cc.coder.encode(x)[0], x


def prefill_at(model, x, plen, cache, grab=(), layer=None, repl=None):
    """concepts.prefill, with the prompt-end state after `layer` (a block index or 'final') replaced by
    repl (S, d) when given, so the move's characters and the later layers read it. -> first-character
    logits (S, vocab), {layer: (S, d)} real prompt-end states for the layers in grab."""
    S, T = x.shape
    d = model.ln.normalized_shape[0]
    rows = torch.arange(S, device=x.device)
    cache.plen, cache.plen_rep = plen, plen.repeat_interleave(cache.R)
    cache.pmask = torch.arange(cache.pk[0].shape[2], device=x.device)[None, :] < plen[:, None]
    h = model.tok(x) + model.pos(torch.arange(T, device=x.device))
    out = {}
    for l, blk in enumerate(model.blocks):
        q, k, v = (z.view(S, T, blk.heads, d // blk.heads).transpose(1, 2) for z in blk.qkv(blk.ln1(h)).split(d, dim=2))
        cache.pk[l][:, :, :T], cache.pv[l][:, :, :T] = k, v
        y = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        h = h + blk.proj(y.transpose(1, 2).reshape(S, T, d))
        h = h + blk.mlp(blk.ln2(h))
        if str(l) in grab:
            out[str(l)] = h[rows, plen - 1].float()
        if layer == str(l):
            h[rows, plen - 1] = repl.to(h.dtype)
    f = model.ln(h[rows, plen - 1])
    if "final" in grab:
        out["final"] = f.float()
    if layer == "final":
        f = repl.to(f.dtype)
    return model.head(f).float(), out


@torch.no_grad()
def policy(model, boards, dev, prompts=None, grab=(), layer=None, repl=None, batch=48):
    """Each board's legal moves and their log-probabilities (sum over the move's characters, renormalised
    over the legal moves), and {layer: (len(boards), d)} prompt-end states for grab. prompts: the boards'
    prompt strings when already known. With layer and repl (len(boards), d), the prompt-end state at that
    layer is replaced first (see prefill_at)."""
    if not boards:
        return [], [], {}
    legal = [list(b.legal_moves) for b in boards]
    ids = [encode(p) for p in (prompts or [prompt(b) for b in boards])]
    if max(len(p) for p in ids) + MAX_MOVE_CHARS + 1 > model.ctx:
        raise ValueError("a prompt does not fit in the model's context")
    n = MAX_MOVE_CHARS
    logp, states = [None] * len(boards), {}
    order = sorted(range(len(boards)), key=lambda i: (len(legal[i]), len(ids[i])))
    for s in range(0, len(order), batch):
        idx = order[s:s + batch]
        R = max(1, max(len(legal[i]) for i in idx))
        x, plen = pad([ids[i] for i in idx], dev)
        cache = Cache(model, len(idx), R, x.shape[1], n, dev)
        c = torch.full((len(idx) * R, n + 1), SPACE, dtype=torch.long)
        clen = torch.ones(len(idx) * R, dtype=torch.long)
        for j, i in enumerate(idx):
            for r, mv in enumerate(legal[i]):
                t = encode(boards[i].san(mv) + " ")
                c[j * R + r, :len(t)] = torch.tensor(t)
                clen[j * R + r] = len(t)
        c, clen = c.to(dev), clen.to(dev)
        with torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev == "cuda"):
            first, st = prefill_at(model, x, plen, cache, grab, layer, None if repl is None else repl[idx].to(dev))
            _, out = extend(model, c[:, :n], torch.arange(n, device=dev).expand(len(c), n), cache, ("final",), Ls=n)
            rest = model.head(out["final"]).float()
        lp = torch.log_softmax(first.repeat_interleave(R, 0), -1).gather(1, c[:, :1])[:, 0]
        more = torch.log_softmax(rest, -1).gather(2, c[:, 1:, None])[..., 0]
        lp = lp + (more * (torch.arange(1, n + 1, device=dev)[None] < clen[:, None])).sum(1)
        lp = lp.view(len(idx), R).double().cpu().numpy()
        for j, i in enumerate(idx):
            v = lp[j, :len(legal[i])]
            logp[i] = v - np.logaddexp.reduce(v)
        for L, v in st.items():
            states.setdefault(L, torch.zeros((len(boards), v.shape[1])))[idx] = v.cpu()
    return legal, logp, states


def kl_top1(ref, other):
    """Mean KL(ref || other) over positions and how often their most likely moves agree."""
    kl = [float(np.sum(np.exp(p) * (p - q))) for p, q in zip(ref, other)]
    return float(np.mean(kl)), float(np.mean([int(p.argmax() == q.argmax()) for p, q in zip(ref, other)]))


# ---------------------------------------------------------------- gate 1: health

@torch.no_grad()
def health(a):
    dev = ev.device(a.device)
    cc = load_cc(a.cc_run, a.cc, a.strong, dev)
    names, L, d = cc.info["names"], cc.ck["latents"], cc.ck["d"]
    arrs = load_sources(cc.run, cc.sources)
    rows = np.load(cc.run / "rows.npy")
    held = (rows[:, 0] * 1_000_003 + rows[:, 1]) % 50 == 0          # crosscoder.py train's validation games
    val = np.flatnonzero(held)[:20_000]
    print(f"gate 1 on {len(val)} held-out positions of {cc.run.name}/{cc.dir.name}", flush=True)
    X = stack(arrs, val, cc.scales, dev)
    fvu, l0 = evaluate(cc.coder, X)
    fires = torch.zeros(L, device=dev)
    for i in range(0, len(X), 4096):
        fires += (cc.coder.encode(X[i:i + 4096])[0] > 0).sum(0)
    rate = (fires / len(X)).cpu().numpy()
    del X
    tags = np.array([tag(r) for r in cc.r])
    rec = dict(cc=str(cc.dir), positions=len(val), S=names[cc.s], W=names[cc.w],
               fvu={names[m]: fvu[k] for k, (m, _) in enumerate(cc.sources)}, l0=l0,
               dead=int((rate == 0).sum()), dense10=int((rate > 0.1).sum()), dense50=int((rate > 0.5).sum()),
               tags={t: int((tags == t).sum()) for t in ("S-only", "W-only", "shared", "leaning S", "leaning W")})

    # exclusivity: ridge from each model's own states to every latent's activation, R^2 on the other half
    rng = np.random.default_rng(a.seed)
    tr = np.flatnonzero(~held)
    tr = np.sort(rng.choice(tr, min(a.probe_n, len(tr)), replace=False))
    half = (rows[tr, 0].astype(np.int64) * 1_000_003 + rows[tr, 1]) * 2654435761 % 2 ** 32 % 2
    print(f"exclusivity: ridge from each model's states to the latents, {len(tr)} positions", flush=True)
    G = torch.zeros((2, 2, d + 1, d + 1), dtype=torch.float64, device=dev)    # [S/W, half]
    B = torch.zeros((2, 2, d + 1, L), dtype=torch.float64, device=dev)
    yy = torch.zeros((2, L), dtype=torch.float64, device=dev)
    ys, nf = torch.zeros_like(yy), torch.zeros_like(yy)
    nh = [0, 0]
    for i in range(0, len(tr), 4096):
        x = stack(arrs, tr[i:i + 4096], cc.scales, dev)
        f = cc.coder.encode(x)[0].double()
        h = torch.from_numpy(half[i:i + 4096]).to(dev)
        for hh in (0, 1):
            sel = h == hh
            fh = f[sel]
            yy[hh] += (fh ** 2).sum(0)
            ys[hh] += fh.sum(0)
            nf[hh] += (fh > 0).sum(0)
            nh[hh] += int(sel.sum())
            for j, m in enumerate((cc.s, cc.w)):
                z = torch.cat([x[sel, cc.col[m]].double(), torch.ones((len(fh), 1), dtype=torch.float64, device=dev)], 1)
                G[j, hh] += z.T @ z
                B[j, hh] += z.T @ fh
    reg = a.ridge * torch.eye(d + 1, dtype=torch.float64, device=dev)
    reg[d, d] = 0
    r2 = []
    for j in (0, 1):
        w = torch.linalg.solve(G[j, 0] + reg, B[j, 0])
        sse = yy[1] - 2 * (w * B[j, 1]).sum(0) + (w * (G[j, 1] @ w)).sum(0)
        sst = yy[1] - ys[1] ** 2 / max(nh[1], 1)
        r2.append((1 - sse / sst.clamp_min(1e-9)).cpu().numpy())
    r2S, r2W = r2
    ok = (nf[0] >= 50).cpu().numpy() & (nf[1] >= 50).cpu().numpy()
    cc.out.mkdir(parents=True, exist_ok=True)
    np.savez(cc.out / "exclusivity.npz", r=cc.r, r2_S=r2S, r2_W=r2W, scored=ok, rate=rate)
    excl = {}
    for t in ("S-only", "W-only", "shared"):
        m = ok & (tags == t)
        own, other = (r2S, r2W) if t != "W-only" else (r2W, r2S)
        excl[t] = dict(latents=int(m.sum()), r2_S=float(np.median(r2S[m])) if m.any() else None,
                       r2_W=float(np.median(r2W[m])) if m.any() else None,
                       confirmed=float(np.mean(other[m] <= 0.5 * own[m])) if m.any() and t != "shared" else None)
    rec["exclusivity"] = excl

    # spliced policy
    corpus = Corpus(cc.info["folders"])
    models = {m: ev.load(cc.info["models"][m], dev)[0] for m in (0, 1)}
    ctx = min(m.ctx for m in models.values())
    boards = [position(corpus, rows[i])[0] for i in val[:a.policy_n] if rows[i, 3] + MAX_MOVE_CHARS + 2 <= ctx]
    print(f"spliced policy on {len(boards)} positions", flush=True)
    real, st = {}, {}
    for m, model in models.items():
        _, real[m], s_ = policy(model, boards, dev, grab=(cc.layer[m],), batch=a.batch)
        st[m] = s_[cc.layer[m]].to(dev)
    f, _ = encode_states(cc, st)
    xh = cc.coder.decode(f)
    rec["policy"] = {}
    for m, model in models.items():
        k = cc.col[m]
        reps = dict(real=st[m], spliced=xh[:, k] / cc.scales[k], mean=st[m].mean(0, keepdim=True).expand_as(st[m]))
        row = {}
        for nm, rep in reps.items():
            _, lp, _ = policy(model, boards, dev, layer=cc.layer[m], repl=rep.cpu(), batch=a.batch)
            row[f"kl_{nm}"], row[f"top1_{nm}"] = kl_top1(real[m], lp)
        row["kl_recovered"] = 1 - row["kl_spliced"] / max(row["kl_mean"], 1e-9)
        rec["policy"][names[m]] = row
    cc.res.mkdir(parents=True, exist_ok=True)
    (cc.res / "health.json").write_text(json.dumps(rec, indent=1))
    print(health_text(rec))
    print(f"wrote {cc.res / 'health.json'} and {cc.out / 'exclusivity.npz'}")


def health_text(rec):
    out = [f"## Gate 1: health ({rec['positions']} held-out positions)", "",
           "| model | FVU | KL spliced | KL mean-ablated | KL recovered | top-1 spliced | top-1 mean-ablated | splice check (KL real) |",
           "|---|---|---|---|---|---|---|---|"]
    for n, p in rec["policy"].items():
        out.append(f"| {n} | {rec['fvu'][n]:.3f} | {p['kl_spliced']:.3f} | {p['kl_mean']:.3f} | {p['kl_recovered']:.1%} | "
                   f"{p['top1_spliced']:.1%} | {p['top1_mean']:.1%} | {p['kl_real']:.4f} |")
    out += ["", f"L0 {rec['l0']:.1f}; dead {rec['dead']}; firing on > 10% of positions {rec['dense10']}, "
                f"on > 50% {rec['dense50']}", "",
            "Tags by relative decoder norm toward S: " + ", ".join(f"{t} {n}" for t, n in rec["tags"].items()), "",
            "| tag | latents scored | median R^2 from S's states | from W's | exclusive confirmed |", "|---|---|---|---|---|"]
    for t, e in rec["exclusivity"].items():
        f = lambda v, p=False: "-" if v is None else (f"{v:.0%}" if p else f"{v:.2f}")
        out.append(f"| {t} | {e['latents']} | {f(e['r2_S'])} | {f(e['r2_W'])} | {f(e['confirmed'], True)} |")
    flags = [f"FVU {v:.2f} for {n}" for n, v in rec["fvu"].items() if v > 0.2]
    flags += [f"{n}: only {p['kl_recovered']:.0%} of the KL recovered" for n, p in rec["policy"].items() if p["kl_recovered"] < 0.8]
    flags += [f"{n}: the splice check is off (KL {p['kl_real']:.3f} with the real state put back)"
              for n, p in rec["policy"].items() if p["kl_real"] > 0.01]
    if rec["dense10"] > 0.01 * sum(rec["tags"].values()):
        flags.append(f"{rec['dense10']} dense latents")
    out += ["", "Red flags (FVU > 0.2, KL recovered < 80%, splice check KL > 0.01, > 1% of latents dense): "
            + ("; ".join(flags) if flags else "none")]
    return "\n".join(out)


# ---------------------------------------------------------------- gate 2: known-concept recall

def auc_t(s, y):
    """P(a positive scores above a negative), ties counted half."""
    neg, pos = torch.sort(s[~y].float()).values, s[y].float()
    lo, hi = torch.searchsorted(neg, pos, right=False), torch.searchsorted(neg, pos, right=True)
    return float((lo + hi).double().sum() / 2 / max(len(pos) * len(neg), 1))


def logistic(Xf, yf, Xt):
    """Logistic regression on standardised features (fit rows) -> scores for the fit and test rows."""
    mu, sd = Xf.mean(0), Xf.std(0) + 1e-6
    Zf, Zt = (Xf - mu) / sd, (Xt - mu) / sd
    w = torch.zeros(Zf.shape[1] + 1, device=Zf.device, requires_grad=True)
    opt = torch.optim.LBFGS([w], max_iter=60, line_search_fn="strong_wolfe")
    y = yf.float()

    def closure():
        opt.zero_grad()
        loss = F.binary_cross_entropy_with_logits(Zf @ w[:-1] + w[-1], y) + 1e-4 * (w[:-1] ** 2).sum()
        loss.backward()
        return loss

    with torch.enable_grad():
        opt.step(closure)
    w = w.detach()
    return Zf @ w[:-1], Zt @ w[:-1]


@torch.no_grad()
def recall(a):
    dev = ev.device(a.device)
    cc = load_cc(a.cc_run, a.cc, a.strong, dev)
    rows = np.load(cc.run / "rows.npy")
    fpath = next((p for p in [cc.dir / "facts.npz", *sorted(cc.run.glob("cc-*/facts.npz"))] if p.exists()), None)
    if fpath is None:
        sys.exit(f"no facts.npz under {cc.run}: run explain.py on this crosscoder run first")
    z = np.load(fpath)
    idx, names, depth = z["idx"], [str(n) for n in z["names"]], int(z["depth"])
    P = refresh(z["P"].copy(), z["numbers"]) if depth and names == EXPLAIN_NAMES else z["P"]
    group = ["skill" if n in skill.NAMES else "board" for n in names]
    keep = [k for k, g in enumerate(group) if depth or g == "board"]
    Y, names, group = P[:, keep], [names[k] for k in keep], [group[k] for k in keep]
    sq = cc.run / "squares.npz"
    if sq.exists() and np.array_equal(np.load(sq)["idx"], idx):
        Y = np.concatenate([Y, np.load(sq)["Q"]], 1)
        names, group = names + predicates.SQUARE_NAMES, group + ["square"] * len(predicates.SQUARE_NAMES)
    halves = (rows[idx, 0].astype(np.int64) * 1_000_003 + rows[idx, 1]) * 2654435761 % 2 ** 32 % 2
    fit, test = halves == 0, halves == 1
    ok = [k for k in range(Y.shape[1]) if min(Y[fit, k].sum(), (~Y[fit, k]).sum(), Y[test, k].sum(), (~Y[test, k]).sum()) >= 30]
    Y, names, group = Y[:, ok], [names[k] for k in ok], [group[k] for k in ok]
    # control: board and skill labels shuffled across positions within each half
    rng = np.random.default_rng(a.seed)
    nul = [k for k, g in enumerate(group) if g != "square"]
    Yn = Y[:, nul].copy()
    for hh in (fit, test):
        w = np.flatnonzero(hh)
        Yn[w] = Yn[rng.permutation(w)]
    Yall = np.concatenate([Y, Yn], 1)
    K = Yall.shape[1]
    print(f"gate 2: {len(names)} labels ({', '.join(f'{g} {group.count(g)}' for g in ('board', 'skill', 'square'))}) "
          f"on {len(idx)} positions ({fpath})", flush=True)
    arrs = load_sources(cc.run, cc.sources)
    Fs = torch.empty((len(idx), cc.ck["latents"]), dtype=torch.float16, device=dev)
    for i in range(0, len(idx), 4096):
        Fs[i:i + 4096] = cc.coder.encode(stack(arrs, idx[i:i + 4096], cc.scales, dev))[0].half()
    fit_t, test_t = torch.from_numpy(fit).to(dev), torch.from_numpy(test).to(dev)
    Yt = torch.from_numpy(Yall).to(dev)
    # candidates: standardised difference of mean activation, fit half
    S1 = torch.zeros((K, Fs.shape[1]), device=dev)
    sall, ss = torch.zeros(Fs.shape[1], device=dev), torch.zeros(Fs.shape[1], device=dev)
    fr = torch.nonzero(fit_t)[:, 0]
    for i in range(0, len(fr), 8192):
        f = Fs[fr[i:i + 8192]].float()
        S1 += Yt[fr[i:i + 8192]].float().T @ f
        sall += f.sum(0)
        ss += (f ** 2).sum(0)
    n1 = Yt[fit_t].float().sum(0)[:, None]
    nfit = float(fit_t.sum())
    mu1, mu0 = S1 / n1, (sall[None] - S1) / (nfit - n1)
    sd = (ss / nfit - (sall / nfit) ** 2).clamp_min(1e-8).sqrt()
    diff = (mu1 - mu0) / sd[None]
    cands = diff.abs().topk(a.cands, 1).indices
    out = []
    t0 = time.time()
    for k in range(K):
        y = Yt[:, k]
        yf, yt = y[fit_t], y[test_t]
        best = None
        for j in cands[k].tolist():
            sgn = 1.0 if diff[k, j] >= 0 else -1.0
            s = Fs[:, j].float() * sgn
            au = auc_t(s[fit_t], yf)
            if best is None or au > best[1]:
                best = (j, au, sgn)
        j, au_fit, sgn = best
        au_test = auc_t(Fs[test_t, j].float() * sgn, yt)
        r = dict(fit_auc=au_fit, test_auc=au_test, latent=j, sign=int(sgn))
        if k < len(names):
            r.update(label=names[k], group=group[k], rate=float(y.float().mean()))
            if group[k] != "square":                         # up to 3 latents, added greedily
                chosen, cur = [j], au_fit
                for _ in range(2):
                    trial = []
                    for c in cands[k].tolist():
                        if c in chosen:
                            continue
                        cols = chosen + [c]
                        Xc = Fs[:, cols].float()
                        sf, _ = logistic(Xc[fit_t], yf, Xc[test_t])
                        trial.append((auc_t(sf, yf), c))
                    if not trial or max(trial)[0] < cur + 0.005:
                        break
                    cur, c = max(trial)
                    chosen.append(c)
                if len(chosen) > 1:
                    Xc = Fs[:, chosen].float()
                    _, st_ = logistic(Xc[fit_t], yf, Xc[test_t])
                    r.update(combo=chosen, combo_test_auc=auc_t(st_, yt))
            out.append(r)
        else:
            out[nul[k - len(names)]]["null_test_auc"] = au_test
        if (k + 1) % 50 == 0:
            print(f"\r  {k + 1}/{K} labels, {time.time() - t0:.0f}s", end="", flush=True)
    print()
    best = lambda r: max(r["test_auc"], r.get("combo_test_auc", 0))
    summ = {}
    for g in ("board", "skill", "square", "all"):
        rs = [r for r in out if g in ("all", r["group"])]
        if not rs:
            continue
        summ[g] = dict(labels=len(rs), **{f"recall_{t}": float(np.mean([best(r) >= t for r in rs])) for t in (a.auc, 0.8)},
                       **{f"recall_single_{t}": float(np.mean([r["test_auc"] >= t for r in rs])) for t in (a.auc, 0.8)})
        nr = [r["null_test_auc"] for r in rs if "null_test_auc" in r]
        if nr:
            summ[g][f"null_recall_{a.auc}"] = float(np.mean(np.array(nr) >= a.auc))
            summ[g]["null_median_auc"] = float(np.median(nr))
    rec = dict(facts=str(fpath), positions=len(idx), auc=a.auc, cands=a.cands, summary=summ, labels=out)
    cc.res.mkdir(parents=True, exist_ok=True)
    (cc.res / "recall.json").write_text(json.dumps(rec, indent=1))
    print(recall_text(rec))
    print(f"wrote {cc.res / 'recall.json'}")


def recall_text(rec):
    t = rec["auc"]
    out = [f"## Gate 2: known-concept recall ({rec['positions']} positions, held-out half of the games)", "",
           f"| labels | n | recall at AUC >= {t} (best of 1-3 latents) | single latent | at AUC >= 0.8 | shuffled labels: recall | shuffled: median AUC |",
           "|---|---|---|---|---|---|---|"]
    for g, s in rec["summary"].items():
        nr = s.get(f"null_recall_{t}")
        out.append(f"| {g} | {s['labels']} | {s[f'recall_{t}']:.0%} | {s[f'recall_single_{t}']:.0%} | {s['recall_0.8']:.0%} | "
                   f"{'-' if nr is None else f'{nr:.0%}'} | {s.get('null_median_auc', float('nan')):.2f} |")
    worst = sorted((r for r in rec["labels"] if r["group"] != "square"),
                   key=lambda r: max(r["test_auc"], r.get("combo_test_auc", 0)))[:12]
    out += ["", "Board and skill labels the dictionary recovers worst: " + "; ".join(
        f"{r['label']} {max(r['test_auc'], r.get('combo_test_auc', 0)):.2f}" for r in worst)]
    return "\n".join(out)


# ---------------------------------------------------------------- the lines

_eng = _depth = None


def _eval_init(depth):
    global _eng, _depth
    _eng, _depth = skill.Annotator(depth=depth), depth


def _eval(job):
    """Stockfish's evaluation for the side to move (centipawns, mates as +/- skill.MATE) and the
    anchor facts, for one position given as the position before it and the move to it."""
    key, prev, uci = job
    b = chess.Board(prev)
    b.push(chess.Move.from_uci(uci))
    v = predicates.features(b)
    facts = [v[predicates.NAMES.index(n)] for n in ANCHORS]
    if not any(b.generate_legal_moves()):
        return key, (-skill.MATE if b.is_check() else 0), facts
    if b.is_insufficient_material():
        return key, 0, facts
    for _ in range(2):
        try:
            info = _eng.engine.analyse(b, chess.engine.Limit(depth=_depth), game=object())
            return key, info["score"].pov(b.turn).score(mate_score=skill.MATE), facts
        except (chess.engine.EngineError, chess.engine.EngineTerminatedError):
            try:
                _eng.engine.quit()
            except Exception:
                pass
            _eng.start()
    return key, None, facts


def middlegame(b):
    return b.fullmove_number > 10 and sum(1 for p in b.piece_map().values() if p.piece_type not in (chess.PAWN, chess.KING)) > 6


def sample(logp, T, rng):
    p = np.exp((logp - logp.max()) / T)
    return int(rng.choice(len(p), p=p / p.sum()))


def advance(line, mv):
    """Play mv in a line: its board, moves, SANs and prompt string (pgn_model.prompt, kept incrementally)."""
    b = line["board"]
    san = b.san(mv)
    line["prompt"] += san + (" " if b.turn == chess.WHITE else f" {b.fullmove_number + 1}.")
    b.push(mv)
    line["moves"].append(mv.uci())
    line["sans"].append(san)


@torch.no_grad()
def line_states(model, seqs, ends, layer, dev, max_tokens):
    """The state after `layer` at the given characters of each sequence -> (total ends, d) float16, in order."""
    grabbed = {}
    hook = None if layer == "final" else model.blocks[int(layer)].register_forward_hook(
        lambda mod, i, o: grabbed.__setitem__("h", o))
    offs = np.cumsum([0] + [len(e) for e in ends])
    out = torch.zeros((int(offs[-1]), model.ln.normalized_shape[0]), dtype=torch.float16)
    order = sorted(range(len(seqs)), key=lambda i: len(seqs[i]))
    s = 0
    try:
        while s < len(order):
            j = s + 1
            while j < len(order) and (j + 1 - s) * len(seqs[order[j]]) <= max_tokens:
                j += 1
            batch, s = order[s:j], j
            x = torch.full((len(batch), len(seqs[batch[-1]])), SPACE, dtype=torch.long)
            bi, ci, oi = [], [], []
            for r, i in enumerate(batch):
                x[r, :len(seqs[i])] = torch.tensor(seqs[i])
                bi += [r] * len(ends[i])
                ci += ends[i]
                oi += range(offs[i], offs[i + 1])
            with torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev == "cuda"):
                feats = model.features(x.to(dev))
            h = feats if layer == "final" else grabbed["h"]
            out[oi] = h[torch.tensor(bi, device=dev), torch.tensor(ci, device=dev)].to(torch.float16).cpu()
    finally:
        if hook is not None:
            hook.remove()
    return out


def lines(a):
    dev = ev.device(a.device)
    cc = load_cc(a.cc_run, a.cc, a.strong, dev)
    cc.out.mkdir(parents=True, exist_ok=True)
    models = {m: ev.load(cc.info["models"][m], dev)[0] for m in (0, 1)}
    Sm, Wm = models[cc.s], models[cc.w]
    ctx = min(m.ctx for m in models.values())
    rng = np.random.default_rng(a.seed)
    pop = [json.loads(l) for l in open(a.population, encoding="utf-8")]
    by_band = {}
    for i in rng.permutation(len(pop)):
        if len(pop[i]["prompt"]) + room(a.plies) + MAX_MOVE_CHARS + 1 <= ctx:
            by_band.setdefault(pop[i]["band"], []).append(int(i))
    bands = sorted(by_band)
    cand, per_game = [], {}
    for band in bands:
        got = 0
        for i in by_band[band]:
            if got >= a.roots * a.oversample // len(bands):
                break
            r = pop[i]
            if per_game.get((band, r["game"]), 0) >= a.per_game:
                continue
            b = ev.board_of(parse_movetext(r["prompt"])[0])
            if prompt(b) != r["prompt"] or b.is_game_over() or not middlegame(b):
                continue
            cand.append((i, b))
            per_game[(band, r["game"])] = per_game.get((band, r["game"]), 0) + 1
            got += 1
    print(f"{len(cand)} middlegame candidates from {', '.join(bands)}; S = {cc.info['names'][cc.s]}, "
          f"W = {cc.info['names'][cc.w]}; root policies", flush=True)
    boards = [b for _, b in cand]
    legal, lpS, _ = policy(Sm, boards, dev, [pop[i]["prompt"] for i, _ in cand], batch=a.batch)
    _, lpW, _ = policy(Wm, boards, dev, [pop[i]["prompt"] for i, _ in cand], batch=a.batch)
    roots, taken = [], {band: 0 for band in bands}
    for k, (i, b) in enumerate(cand):
        r = pop[i]
        if lpS[k].argmax() == lpW[k].argmax() or taken[r["band"]] >= a.roots // len(bands):
            continue
        taken[r["band"]] += 1
        held = zlib.crc32(f"{r['band']}/{r['game']}".encode()) % 100 < a.held
        roots.append(dict(k=k, band=r["band"], game=r["game"], ply=r["ply"], fen=b.fen(), prompt=r["prompt"], held=bool(held),
                          s_top=b.san(legal[k][lpS[k].argmax()]), w_top=b.san(legal[k][lpW[k].argmax()]),
                          s_p=float(np.exp(lpS[k].max())), w_p=float(np.exp(lpW[k].max()))))
    print(f"{len(roots)} roots where S and W disagree ({sum(r['held'] for r in roots)} held out by game; "
          f"{sum(lpS[k].argmax() != lpW[k].argmax() for k in range(len(cand))) / len(cand):.0%} of candidates disagree)", flush=True)

    L = []
    for ri, r in enumerate(roots):
        k, b = r["k"], boards[r["k"]]
        order = np.argsort(-lpS[k])
        first = {"S": sample(lpS[k], a.temperature, rng), "W": sample(lpW[k], a.temperature, rng), "chosen": int(order[0])}
        for j in range(1, min(5, len(order))):
            first[f"alt{j}"] = int(order[j])
        for kind, j in first.items():
            line = dict(root=ri, kind=kind, board=b.copy(), moves=[], sans=[], prompt=r["prompt"])
            advance(line, legal[k][j])
            L.append(line)
    t0 = time.time()
    for ply in range(1, a.plies):
        live = [l for l in L if len(l["moves"]) == ply and not l["board"].is_game_over()]
        for m, model in ((cc.s, Sm), (cc.w, Wm)):
            group = [l for l in live if (cc.w if l["kind"] == "W" and ply % 2 == 0 else cc.s) == m]
            if group:
                lg, lp, _ = policy(model, [l["board"] for l in group], dev, [l["prompt"] for l in group], batch=a.batch)
                for l, mv, p in zip(group, lg, lp):
                    advance(l, mv[sample(p, a.temperature, rng)])
        print(f"\r  {len(L)} lines, ply {ply + 1}/{a.plies}, {time.time() - t0:.0f}s", end="", flush=True)
    print()

    # every position of every line: its prompt end, the position before it and the move to it
    root_prev = []
    for r in roots:
        b = boards[r["k"]].copy()
        mv = b.pop()
        root_prev.append((b.fen(), mv.uci()))
    seqs, ends, jobs, pos_key = [], [], {}, []
    line_start = [0]
    for l in L:
        b = chess.Board(roots[l["root"]]["fen"])
        prev, uci = root_prev[l["root"]]
        p = roots[l["root"]]["prompt"]
        e = [len(p) - 1]
        keys = [roots[l["root"]]["fen"] + " " + uci]
        jobs.setdefault(keys[0], (keys[0], prev, uci))
        for u in l["moves"]:
            mv = chess.Move.from_uci(u)
            san = b.san(mv)
            p += san + (" " if b.turn == chess.WHITE else f" {b.fullmove_number + 1}.")
            prev = b.fen()
            b.push(mv)
            e.append(len(p) - 1)
            keys.append(b.fen() + " " + u)
            jobs.setdefault(keys[-1], (keys[-1], prev, u))
        assert p == l["prompt"]
        seqs.append(encode(p))
        ends.append(e)
        pos_key += keys
        line_start.append(line_start[-1] + len(e))
    npos = line_start[-1]
    print(f"{npos} positions ({len(jobs)} distinct): Stockfish depth {a.depth} and board facts, {a.workers} workers", flush=True)
    res, t0 = {}, time.time()
    with Pool(a.workers, initializer=_eval_init, initargs=(a.depth,)) as pool:
        for d_, (key, cp, facts) in enumerate(pool.imap_unordered(_eval, list(jobs.values()), chunksize=16), 1):
            res[key] = (cp, facts)
            if d_ % 500 == 0 or d_ == len(jobs):
                rate = d_ / (time.time() - t0)
                print(f"\r  {d_}/{len(jobs)}, {rate:.0f}/s, {(len(jobs) - d_) / max(rate, 1e-9) / 60:.0f} min left   ",
                      end="", flush=True)
    print()
    pos_line = np.repeat(np.arange(len(L)), np.diff(line_start))
    pos_t = np.concatenate([np.arange(n) for n in np.diff(line_start)]).astype(np.int16)
    evals = np.full(npos, np.nan, dtype=np.float32)
    facts = np.zeros((npos, len(ANCHORS)), dtype=bool)
    for q, key in enumerate(pos_key):
        cp, fa = res[key]
        facts[q] = fa
        if cp is not None:
            sign = 1 if pos_t[q] % 2 == 0 else -1                  # even plies: the root's side to move
            evals[q] = float(np.clip(sign * cp / 100, -MATE_PAWNS, MATE_PAWNS))

    print("states of both models at every position, and the crosscoder", flush=True)
    st = {m: line_states(models[m], seqs, ends, cc.layer[m], dev, a.max_tokens) for m in (0, 1)}
    indptr, lat, val = [0], [], []
    err = torch.zeros(len(cc.sources), device=dev)
    sx = torch.zeros((len(cc.sources), cc.ck["d"]), device=dev)
    sxx = torch.zeros(len(cc.sources), device=dev)
    with torch.no_grad():
        for i in range(0, npos, 4096):
            f, x = encode_states(cc, {m: st[m][i:i + 4096].to(dev) for m in (0, 1)})
            err += (cc.coder.decode(f) - x).pow(2).sum((0, 2))
            sx += x.sum(0)
            sxx += x.pow(2).sum((0, 2))
            nz = (f > 0).nonzero()                                   # row-major: rows in order
            indptr += (np.cumsum(np.bincount(nz[:, 0].cpu().numpy(), minlength=len(f))) + indptr[-1]).tolist()
            lat.append(nz[:, 1].int().cpu().numpy())
            val.append(f[nz[:, 0], nz[:, 1]].half().cpu().numpy())
    fvu = (err / (sxx - sx.pow(2).sum(1) / npos)).tolist()
    np.savez(cc.out / "codes.npz", indptr=np.array(indptr, dtype=np.int64), lat=np.concatenate(lat), val=np.concatenate(val),
             line_start=np.array(line_start, dtype=np.int64), pos_line=pos_line, pos_t=pos_t)
    np.save(cc.out / "evals.npy", evals)
    np.save(cc.out / "facts.npy", facts)
    for l in L:
        del l["board"], l["prompt"]
    for r in roots:
        del r["k"]
    (cc.out / "lines.json").write_text(json.dumps(dict(roots=roots, lines=L)), encoding="utf-8")
    end = {kind: [evals[line_start[q + 1] - 1] for q, l in enumerate(L) if l["kind"] == kind] for kind in KINDS}
    meta = dict(cc_run=str(cc.run), cc=cc.dir.name, S=cc.info["names"][cc.s], W=cc.info["names"][cc.w],
                plies=a.plies, temperature=a.temperature, depth=a.depth, roots=len(roots), lines=len(L), positions=npos,
                held=a.held, seed=a.seed, latents=cc.ck["latents"], anchors=ANCHORS,
                fvu_lines={cc.info["names"][m]: fvu[k] for k, (m, _) in enumerate(cc.sources)},
                mean_end_eval={kind: float(np.nanmean(v)) if v else None for kind, v in end.items()},
                stockfish_missing=int(np.isnan(evals).sum()))
    (cc.out / "meta.json").write_text(json.dumps(meta, indent=1))
    print(f"FVU on the line positions: {', '.join(f'{n} {v:.3f}' for n, v in meta['fvu_lines'].items())}")
    print("mean evaluation at the line's end, pawns for the root's side to move: "
          + ", ".join(f"{k} {v:+.2f}" for k, v in meta["mean_end_eval"].items() if v is not None))
    print(f"wrote {cc.out}: lines.json, codes.npz, evals.npy, facts.npy, meta.json")


# ---------------------------------------------------------------- node filters

def load_run(out):
    if not (out / "meta.json").exists():
        sys.exit(f"{out / 'meta.json'} is missing: run lines first")
    meta = json.loads((out / "meta.json").read_text())
    L = json.loads((out / "lines.json").read_text(encoding="utf-8"))
    z = dict(np.load(out / "codes.npz"))
    z["row"] = np.repeat(np.arange(len(z["indptr"]) - 1), np.diff(z["indptr"]))
    return meta, L, z, np.load(out / "evals.npy"), np.load(out / "facts.npy")


def explanations(meta):
    p = CC_RESULTS / Path(meta["cc_run"]).name / meta["cc"] / "explanations.jsonl"
    if not p.exists():
        return {}
    return {r["latent"]: r for r in map(json.loads, open(p, encoding="utf-8"))}


def label(n, ex):
    if n["kind"] == "fact":
        return predicates.TEXT[n["name"]]
    e = ex.get(n["id"])
    if not e or e.get("status") == "too rare":
        return f"latent {n['id']}"
    return f"latent {n['id']}: {e['explanation']} ({e['status']}, F1 {e['f1']:.2f})"


def end_eval(evals, z, q):
    return evals[z["line_start"][q + 1] - 1]


def pair_signs(z, pairs, nlat):
    """Per (pair, latent) with a nonzero difference: pair, latent, d = sum over plies >= 1 of chosen's
    activation minus the rejected line's."""
    ls, ip = z["line_start"], z["indptr"]
    P, J, V = [], [], []
    for p, (c, k) in enumerate(pairs):
        for q, sgn in ((c, 1.0), (k, -1.0)):
            e0, e1 = ip[ls[q] + 1], ip[ls[q + 1]]                     # plies 1.. (the root is shared)
            P.append(np.full(e1 - e0, p))
            J.append(z["lat"][e0:e1])
            V.append(sgn * z["val"][e0:e1].astype(np.float32))
    key = np.concatenate(P).astype(np.int64) * nlat + np.concatenate(J)
    u, inv = np.unique(key, return_inverse=True)
    d = np.bincount(inv, weights=np.concatenate(V))
    nzm = np.abs(d) > 1e-6
    return (u // nlat)[nzm], (u % nlat)[nzm], d[nzm]


def filters(lat, d, flip, fit_pair, active, a, nlat):
    """Filters 2 and 3 for every latent given the per-(pair, latent) signs (flip: +-1 per pair, for the null)."""
    s = np.sign(d) * flip
    out = {}
    for nm, m in (("fit", fit_pair), ("held", ~fit_pair)):
        pos = np.bincount(lat[m & (s > 0)], minlength=nlat)
        neg = np.bincount(lat[m & (s < 0)], minlength=nlat)
        n = pos + neg
        out[nm] = (n, np.where(pos >= neg, 1, -1), np.maximum(pos, neg) / np.maximum(n, 1))
    (nf, sf, af), (nh, sh, ah) = out["fit"], out["held"]
    f2 = active & (nf >= a.min_pairs) & (af >= a.sep)
    f3 = f2 & (nh >= a.min_pairs_held) & (sh == sf) & (ah >= a.sep_held)
    return f2, f3, out


def nodes(a):
    cc_run = Path(a.cc_run)
    out = RUNS / f"{cc_run.name}-{a.cc.removeprefix('cc-')}"
    meta, Ld, z, evals, facts = load_run(out)
    roots, L = Ld["roots"], Ld["lines"]
    nlat = meta["latents"]
    by = {(l["root"], l["kind"]): q for q, l in enumerate(L)}
    fit_root = np.array([not r["held"] for r in roots])
    pairs, pair_root = [], []
    tried = 0
    for ri in range(len(roots)):
        c = by.get((ri, "chosen"))
        for j in range(1, 5):
            k = by.get((ri, f"alt{j}"))
            if c is None or k is None:
                continue
            tried += 1
            if end_eval(evals, z, c) - end_eval(evals, z, k) >= a.margin:
                pairs.append((c, k))
                pair_root.append(ri)
    if not pairs:
        sys.exit("no contrast-B pair passes --margin: lower it, or check the Stockfish evaluations")
    fit_pair_r = fit_root[np.array(pair_root, dtype=np.int64)]
    print(f"contrast B: {len(pairs)} of {tried} (chosen, rejected) pairs where Stockfish prefers chosen by >= {a.margin} pawns "
          f"({fit_pair_r.sum()} fit, {(~fit_pair_r).sum()} held out)", flush=True)
    pos_root = np.array([L[q]["root"] for q in z["pos_line"]])
    fit_pos = fit_root[pos_root]
    fires = np.bincount(z["lat"][fit_pos[z["row"]]], minlength=nlat)
    rate = fires / max(fit_pos.sum(), 1)
    active = rate >= a.min_rate
    pp, lat, d = pair_signs(z, pairs, nlat)
    fit_pair = fit_pair_r[pp]
    f2, f3, st = filters(lat, d, np.ones(len(d)), fit_pair, active, a, nlat)
    rng = np.random.default_rng(a.seed)
    null = []
    for _ in range(a.null):
        flip = rng.choice([-1.0, 1.0], len(pairs))[pp]
        n2, n3, _ = filters(lat, d, flip, fit_pair, active, a, nlat)
        null.append((int(n2.sum()), int(n3.sum())))
    null = np.array(null) if null else np.zeros((1, 2))
    surv = np.flatnonzero(f3)
    (nf, sf, af), (nh, sh, ah) = st["fit"], st["held"]
    surv = surv[np.lexsort((-nh[surv], -ah[surv]))][:a.max_nodes]
    excl = out / "exclusivity.npz"
    r = np.load(excl)["r"] if excl.exists() else None
    if r is None:
        cc = load_cc(a.cc_run, a.cc, a.strong, "cpu")
        r = cc.r
    ex = explanations(meta)
    lat_nodes = [dict(kind="latent", id=int(j), r=float(r[j]), tag=tag(r[j]), sign="pursued" if sf[j] > 0 else "avoided",
                      sep_fit=float(af[j]), n_fit=int(nf[j]), sep_held=float(ah[j]), n_held=int(nh[j]), rate=float(rate[j]))
                 for j in surv]
    frate = facts[fit_pos].mean(0)
    anchors = [dict(kind="fact", id=k, name=n, rate=float(frate[k])) for k, n in enumerate(ANCHORS) if 0.01 <= frate[k] <= 0.99]
    for n in lat_nodes + anchors:
        n["label"] = label(n, ex)
    funnel = dict(latents=nlat, active=int(active.sum()), decision=int(f2.sum()), held_out=int(f3.sum()), kept=len(surv),
                  null_decision_mean=float(null[:, 0].mean()), null_held_out_mean=float(null[:, 1].mean()),
                  null_held_out_max=int(null[:, 1].max()), null_runs=a.null)
    rec = dict(funnel=funnel, pairs=dict(tried=tried, kept=len(pairs), fit=int(fit_pair_r.sum()), held=int((~fit_pair_r).sum())),
               settings={k: getattr(a, k) for k in ("margin", "min_rate", "min_pairs", "sep", "min_pairs_held", "sep_held",
                                                    "max_nodes", "null", "seed")},
               tags={t: sum(n["tag"] == t for n in lat_nodes) for t in ("S-only", "W-only", "shared", "leaning S", "leaning W")},
               latents=lat_nodes, anchors=anchors)
    (out / "nodes.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print(nodes_text(rec))
    print(f"wrote {out / 'nodes.json'}")


def nodes_text(rec):
    f, s = rec["funnel"], rec["settings"]
    out = ["## Nodes", "",
           f"Contrast B: {rec['pairs']['kept']} of {rec['pairs']['tried']} (chosen, rejected) pairs kept (Stockfish prefers "
           f"chosen's end by >= {s['margin']} pawns): {rec['pairs']['fit']} fit, {rec['pairs']['held']} held out.", "",
           "| filter | latents | with labels flipped at random (mean of %d) |" % f["null_runs"], "|---|---|---|",
           f"| all | {f['latents']} | |",
           f"| 1. active on >= {s['min_rate']:.0%} of line positions | {f['active']} | {f['active']} |",
           f"| 2. one sign on >= {s['sep']:.0%} of >= {s['min_pairs']} informative fit pairs | {f['decision']} | {f['null_decision_mean']:.1f} |",
           f"| 3. same sign on >= {s['sep_held']:.0%} of >= {s['min_pairs_held']} held-out pairs | {f['held_out']} | "
           f"{f['null_held_out_mean']:.1f} (max {f['null_held_out_max']}) |",
           f"| kept (at most {s['max_nodes']}) | {f['kept']} | |", "",
           "Kept latents by tag: " + ", ".join(f"{t} {n}" for t, n in rec["tags"].items())
           + f"; {len(rec['anchors'])} board facts as anchors."]
    if f["held_out"] and f["null_held_out_mean"] > 0.2 * f["held_out"]:
        out += ["", f"**Warning**: the null passes {f['null_held_out_mean']:.0f} latents against {f['held_out']} real: thresholds too loose."]
    out += ["", "| latent | tag | r | sign | fit pairs agreeing | held-out | rate | explanation |", "|---|---|---|---|---|---|---|---|"]
    for n in rec["latents"][:40]:
        out.append(f"| {n['id']} | {n['tag']} | {n['r']:.2f} | {n['sign']} | {n['sep_fit']:.0%} of {n['n_fit']} | "
                   f"{n['sep_held']:.0%} of {n['n_held']} | {n['rate']:.1%} | {n['label'].split(': ', 1)[-1]} |")
    return "\n".join(out)


# ---------------------------------------------------------------- the graphs and the diff

def bh(p, q):
    """Benjamini-Hochberg: adjusted p-values, and which pass at FDR q."""
    m = len(p)
    if not m:
        return np.zeros(0), np.zeros(0, bool)
    order = np.argsort(p)
    adj = np.minimum.accumulate((p[order] * m / np.arange(1, m + 1))[::-1])[::-1].clip(max=1)
    out = np.empty(m)
    out[order] = adj
    return out, out <= q


def lag_counts(A, k, w):
    """A (R, T+1, N) activity (0 where a line has ended), w (B, R) root weights: weighted counts over
    (root, t), t even, t + k <= T -> n (B,), n_A (B, N), n_B (B, N), n_AB (B, N, N)."""
    T = A.shape[1] - 1
    n = nA = nB = nAB = 0
    for t in range(0, T - k + 1, 2):
        m = A[:, t + k, -1]                                          # the last column: the position exists
        X, Y = A[:, t] * m[:, None], A[:, t + k]
        n = n + w @ m
        nA, nB = nA + w @ X, nB + w @ Y
        nAB = nAB + torch.einsum("br,rn,rm->bnm", w, X, Y)
    return n, nA, nB, nAB


def loglift(n, nA, nB, nAB):
    return torch.log((nAB + 1) / (nA[:, :, None] * nB[:, None, :] / n[:, None, None].clamp_min(1) + 1))


def moments(acc, x):
    acc[0] += x.sum(0)
    acc[1] += (x * x).sum(0)


def sd_of(acc, B):
    return ((acc[1] / B - (acc[0] / B) ** 2).clamp_min(0) * B / max(B - 1, 1)).sqrt()


def diff_edges(AS, AW, lags, a, dev):
    """Edge statistics for both graphs at each lag, point estimates and Poisson-bootstrap sds."""
    R = AS.shape[0]
    g = torch.Generator(device="cpu").manual_seed(a.seed)
    one = torch.ones((1, R), device=dev)
    out = {}
    for k in lags:
        cS, cW = lag_counts(AS, k, one), lag_counts(AW, k, one)
        e = dict(lS=loglift(*cS)[0], lW=loglift(*cW)[0], nS=cS[3][0], nW=cW[3][0], aS=cS[1][0], aW=cW[1][0])
        acc = {x: [0, 0] for x in ("lS", "lW", "D")}
        for b0 in range(0, a.boot, a.boot_chunk):
            w = torch.poisson(torch.ones((min(a.boot_chunk, a.boot - b0), R)), generator=g).to(dev)
            lS, lW = loglift(*lag_counts(AS, k, w)), loglift(*lag_counts(AW, k, w))
            moments(acc["lS"], lS)
            moments(acc["lW"], lW)
            moments(acc["D"], lS - lW)
        e.update({f"sd_{x}": sd_of(v, a.boot) for x, v in acc.items()})
        out[k] = {x: v.cpu().numpy() for x, v in e.items()}
    return out


def categorise(E, nodes, a):
    """Every testable edge with its diff, p, BH-adjusted p and category."""
    N, rows = len(nodes), []
    for k, e in E.items():
        test = (np.maximum(e["nS"], e["nW"]) >= a.min_count) & ~np.eye(N, dtype=bool)
        for i, j in zip(*np.nonzero(test)):
            D, sd = e["lS"][i, j] - e["lW"][i, j], e["sd_D"][i, j]
            rows.append(dict(lag=int(k), family="plan" if k % 2 == 0 else "response", src=int(i), dst=int(j),
                             n_S=float(e["nS"][i, j]), n_W=float(e["nW"][i, j]),
                             lift_S=float(np.exp(e["lS"][i, j])), lift_W=float(np.exp(e["lW"][i, j])),
                             lS=float(e["lS"][i, j]), lW=float(e["lW"][i, j]), sd_S=float(e["sd_lS"][i, j]),
                             sd_W=float(e["sd_lW"][i, j]), delta=float(D), z=float(D / max(sd, 1e-9))))
    p = np.array([math.erfc(abs(r["z"]) / math.sqrt(2)) for r in rows])
    q, sig = bh(p, a.fdr)
    ll = math.log(a.lift)
    for r, pv, qv, s in zip(rows, p, q, sig):
        strong = lambda l, sd: (l >= ll and l - 1.96 * sd > 0) or (l <= -ll and l + 1.96 * sd < 0)
        near1 = lambda l, sd: l - 1.96 * sd <= 0 <= l + 1.96 * sd
        r.update(p=float(pv), q=float(qv))
        if not s:
            r["category"] = "shared"
        elif strong(r["lS"], r["sd_S"]) and near1(r["lW"], r["sd_W"]):
            r["category"] = "S-only"
        elif strong(r["lW"], r["sd_W"]) and near1(r["lS"], r["sd_S"]):
            r["category"] = "W-only"
        else:
            r["category"] = "reweighted"
    return rows


def chains(E2, a):
    """Motif candidates: chains of 2 and 3 lag-2 edges that pass in either graph, strongest first."""
    ll = math.log(a.lift)
    ok = lambda l, sd, n: (l >= ll) & (l - 1.96 * sd > 0) & (n >= a.min_count)
    cand = ok(E2["lS"], E2["sd_lS"], E2["nS"]) | ok(E2["lW"], E2["sd_lW"], E2["nW"])
    np.fill_diagonal(cand, False)
    strength = np.maximum(E2["lS"], E2["lW"])
    two = [(min(strength[i, j], strength[j, k]), (i, j, k)) for j in range(len(cand))
           for i in np.flatnonzero(cand[:, j]) for k in np.flatnonzero(cand[j]) if i != k]
    two.sort(reverse=True)
    two = two[:a.max_motifs]
    three = [(min(s, strength[c[2], m]), (*c, m)) for s, c in two[:a.max_motifs // 2]
             for m in np.flatnonzero(cand[c[2]]) if m not in c]
    three.sort(reverse=True)
    out = [c for _, c in two[:a.max_motifs - min(len(three), a.max_motifs // 2)]] + [c for _, c in three[:a.max_motifs // 2]]
    return out


def completions(A, motifs, dev, chunk=4096):
    """(R, M) completions per root (the chain's nodes active at t, t + 2, ..., t even) and (R, M) starts
    (its first node active at a t with room for the rest)."""
    T = A.shape[1] - 1
    K = torch.zeros((A.shape[0], len(motifs)), device=dev)
    St = torch.zeros_like(K)
    for c0 in range(0, len(motifs), chunk):
        part = motifs[c0:c0 + chunk]
        for n in sorted({len(c) for c in part}):
            cols = [c0 + q for q, c in enumerate(part) if len(c) == n]
            ids = torch.tensor([motifs[q] for q in cols], device=dev)
            for t in range(0, T - 2 * (n - 1) + 1, 2):
                prod = A[:, t, ids[:, 0]]
                St[:, cols] += prod
                for j in range(1, n):
                    prod = prod * A[:, t + 2 * j, ids[:, j]]
                K[:, cols] += prod
    return K, St


def motif_stats(KS, KW, StS, StW, a, dev):
    R = KS.shape[0]
    g = torch.Generator(device="cpu").manual_seed(a.seed + 1)
    acc = [0, 0]
    for b0 in range(0, a.boot, a.boot_chunk):
        w = torch.poisson(torch.ones((min(a.boot_chunk, a.boot - b0), R)), generator=g).to(dev)
        moments(acc, torch.log((w @ KS + 1) / (w @ KW + 1)))
    sd = sd_of(acc, a.boot).cpu().numpy()
    tS, tW = KS.sum(0).cpu().numpy(), KW.sum(0).cpu().numpy()
    lr = np.log((tS + 1) / (tW + 1))
    z = lr / np.maximum(sd, 1e-9)
    p = np.array([math.erfc(abs(v) / math.sqrt(2)) for v in z])
    tested = np.maximum(tS, tW) >= a.min_count                  # small counts: the bootstrap sd is unreliable
    q, sig = np.ones(len(p)), np.zeros(len(p), bool)
    q[tested], sig[tested] = bh(p[tested], a.fdr)
    sS, sW = StS.sum(0).cpu().numpy(), StW.sum(0).cpu().numpy()
    return dict(tS=tS, tW=tW, lr=lr, sd=sd, z=z, p=p, q=q, sig=sig, tested=tested, startS=sS, startW=sW,
                rootsS=(KS > 0).sum(0).cpu().numpy(), rootsW=(KW > 0).sum(0).cpu().numpy())


def activity(z, facts, nodes, line_ids, T, nlat):
    """(R, T+1, N+1) activity of the nodes along the given lines (one per root); the last column marks
    positions that exist."""
    R, N = len(line_ids), len(nodes)
    A = np.zeros((R, T + 1, N + 1), dtype=np.float32)
    col = np.full(nlat, -1)
    thr = np.zeros(N, dtype=np.float32)
    for c, n in enumerate(nodes):
        if n["kind"] == "latent":
            col[n["id"]] = c
            thr[c] = n.get("thr", 0.0)
    ls, ip = z["line_start"], z["indptr"]
    for r, q in enumerate(line_ids):
        if q is None:
            continue
        p0, p1 = ls[q], ls[q + 1]
        t = np.arange(p1 - p0)
        A[r, t, -1] = 1
        for c, n in enumerate(nodes):
            if n["kind"] == "fact":
                A[r, t, c] = facts[p0:p1, n["id"]]
        e0, e1 = ip[p0], ip[p1]
        cs = col[z["lat"][e0:e1]]
        keep = cs >= 0
        cs = cs[keep]
        tt = z["row"][e0:e1][keep] - p0
        on = z["val"][e0:e1][keep].astype(np.float32) > thr[cs]
        A[r, tt[on], cs[on]] = 1
    return A


def thresholds(z, nodes):
    """Each latent node's activity threshold: its 90th percentile over all line positions (0 if it fires
    on fewer than 10% of them: then active = fires)."""
    npos = len(z["indptr"]) - 1
    for n in nodes:
        if n["kind"] != "latent":
            continue
        v = z["val"][z["lat"] == n["id"]].astype(np.float32)
        rate = len(v) / npos
        n["thr"] = float(np.quantile(v, 1 - 0.1 / rate)) if rate > 0.1 else 0.0


def graph(a):
    dev = ev.device(a.device)
    cc_run = Path(a.cc_run)
    name = f"{cc_run.name}-{a.cc.removeprefix('cc-')}"
    out, res = RUNS / name, RESULTS / name
    meta, Ld, z, evals, facts = load_run(out)
    if not (out / "nodes.json").exists():
        sys.exit(f"{out / 'nodes.json'} is missing: run nodes first")
    nd = json.loads((out / "nodes.json").read_text(encoding="utf-8"))
    nodes = nd["latents"] + nd["anchors"]
    thresholds(z, nodes)
    roots, L, T = Ld["roots"], Ld["lines"], meta["plies"]
    by = {(l["root"], l["kind"]): q for q, l in enumerate(L)}
    use = [ri for ri, r in enumerate(roots) if r["held"] == (a.split == "held")]
    S_ids, W_ids = [by.get((ri, "S")) for ri in use], [by.get((ri, "W")) for ri in use]
    AS = activity(z, facts, nodes, S_ids, T, meta["latents"])
    AW = activity(z, facts, nodes, W_ids, T, meta["latents"])
    # the W line's worst move by W (even plies: W to move), by Stockfish
    drop = np.full(len(use), np.nan)
    for r, q in enumerate(W_ids):
        e = evals[z["line_start"][q]:z["line_start"][q + 1]]
        d = [e[t] - e[t + 1] for t in range(0, len(e) - 1, 2) if not (np.isnan(e[t]) or np.isnan(e[t + 1]))]
        drop[r] = max(d) if d else np.nan
    sets = dict(positional=np.flatnonzero(drop <= a.blunder), tactical=np.flatnonzero(drop > a.blunder))
    print(f"{len(use)} {a.split} roots: {len(sets['positional'])} positional (W never loses more than {a.blunder} pawns "
          f"on a move), {len(sets['tactical'])} tactical; {len(nodes)} nodes", flush=True)
    res.mkdir(parents=True, exist_ok=True)
    report, cards = [], {}
    for sname, ix in sets.items():
        if len(ix) < a.min_roots:
            report.append(f"## {sname} roots: only {len(ix)}, skipped (--min-roots {a.min_roots})")
            continue
        print(f"{sname}: edges at lags {PLAN + RESPONSE}, {a.boot} bootstraps", flush=True)
        tS, tW = torch.from_numpy(AS[ix]).to(dev), torch.from_numpy(AW[ix]).to(dev)
        E = diff_edges(tS, tW, sorted(k for k in PLAN + RESPONSE if k <= T), a, dev)
        for e in E.values():                                     # drop the "position exists" column
            for k_ in e:
                e[k_] = e[k_][:len(nodes)] if e[k_].ndim == 1 else e[k_][:len(nodes), :len(nodes)]
        rows = categorise(E, nodes, a)
        with open(res / f"edges-{sname}-{a.split}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["lag", "family", "category", "src", "dst", "lift_S", "lift_W", "delta", "z", "p", "q", "n_S", "n_W",
                        "src_label", "dst_label"])
            for r in sorted(rows, key=lambda r: r["p"]):
                w.writerow([r["lag"], r["family"], r["category"], r["src"], r["dst"], f"{r['lift_S']:.3f}", f"{r['lift_W']:.3f}",
                            f"{r['delta']:.3f}", f"{r['z']:.2f}", f"{r['p']:.3g}", f"{r['q']:.3g}", r["n_S"], r["n_W"],
                            nodes[r["src"]]["label"], nodes[r["dst"]]["label"]])
        motifs = chains(E[2], a)
        print(f"  {len(rows)} edges tested; {len(motifs)} motif candidates", flush=True)
        KS, StS = completions(tS, motifs, dev)
        KW, StW = completions(tW, motifs, dev)
        ms = motif_stats(KS, KW, StS, StW, a, dev)
        with open(res / f"motifs-{sname}-{a.split}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["motif", "log_ratio", "z", "p", "q", "completions_S", "completions_W", "roots_S", "roots_W",
                        "follow_S", "follow_W", "labels"])
            for m in np.argsort(ms["p"]):
                w.writerow([" > ".join(map(str, motifs[m])), f"{ms['lr'][m]:.3f}", f"{ms['z'][m]:.2f}", f"{ms['p'][m]:.3g}",
                            f"{ms['q'][m]:.3g}", int(ms["tS"][m]), int(ms["tW"][m]), int(ms["rootsS"][m]), int(ms["rootsW"][m]),
                            f"{ms['tS'][m] / max(ms['startS'][m], 1):.3f}", f"{ms['tW'][m] / max(ms['startW'][m], 1):.3f}",
                            " > ".join(nodes[x]["label"] for x in motifs[m])])
        report.append(graph_text(sname, a, len(ix), rows, motifs, ms, nodes, attach(E[2], nodes, tS, tW, a)))
        cards[sname] = prototypes(motifs, ms, KS, KW, [use[i] for i in ix], Ld, by, evals, z, nodes, a)
    health_p, recall_p = res / "health.json", res / "recall.json"
    head = [f"# Concept-graph diff, pilot first pass: {name} ({a.split} roots)", "",
            f"S = {meta['S']}, W = {meta['W']}; crosscoder {meta['cc']} of {Path(meta['cc_run']).name}; {meta['roots']} roots, "
            f"{meta['plies']} plies per line at temperature {meta['temperature']}, Stockfish depth {meta['depth']}.", ""]
    head.append(health_text(json.loads(health_p.read_text())) if health_p.exists() else "## Gate 1: not run (graphdiff.py health)")
    head += ["", recall_text(json.loads(recall_p.read_text())) if recall_p.exists() else "## Gate 2: not run (graphdiff.py recall)", ""]
    head += ["## Lines", "", "Crosscoder FVU on the line positions (rollouts, which it never saw): "
             + ", ".join(f"{n} {v:.3f}" for n, v in meta["fvu_lines"].items()) + ".",
             "Mean Stockfish evaluation at each line's end, pawns for the root's side to move (S lines should end better "
             "than W lines, and chosen better than the alternatives): "
             + ", ".join(f"{k} {v:+.2f}" for k, v in meta["mean_end_eval"].items() if v is not None) + ".", ""]
    head += [nodes_text(nd), ""]
    (res / "report.md").write_text("\n".join(head + report) + "\n", encoding="utf-8")
    page(out / f"motifs-{a.split}.html", name, cards)
    print("\n".join(report))
    print(f"wrote {res / 'report.md'}, edges-*-{a.split}.csv, motifs-*-{a.split}.csv and {out / f'motifs-{a.split}.html'}")


def attach(E2, nodes, tS, tW, a):
    """S-only latent nodes: lag-2 predecessors and successors among shared nodes in G_S, and their rates."""
    out = []
    rate = lambda A, c: float(A[:, :, c].sum() / A[:, :, -1].sum().clamp_min(1))
    shared = [c for c, n in enumerate(nodes) if n.get("tag") == "shared"]
    for c, n in enumerate(nodes):
        if n.get("tag") != "S-only":
            continue
        rS, rW = rate(tS, c), rate(tW, c)
        pick = lambda vals: sorted(((float(E2["lS"][i, j]), float(E2["lW"][i, j]), x) for x, i, j in vals
                                    if E2["nS"][i, j] >= a.min_count), reverse=True)[:3]
        pre = pick([(x, x, c) for x in shared])
        suc = pick([(x, c, x) for x in shared])
        out.append(dict(node=c, rate_S=rS, rate_W=rW, absent=rW < 0.25 * rS, pre=pre, suc=suc))
    return out


def graph_text(sname, a, nroots, rows, motifs, ms, nodes, att):
    lab = lambda c: nodes[c]["label"]
    out = [f"## {sname.capitalize()} roots ({nroots})", "", "### Edges",
           "", f"Tested: {len(rows)} edges with >= {a.min_count} co-occurrences in either graph; significant at FDR {a.fdr}:",
           "", "| family | lags | S-only | W-only | reweighted | not significant |", "|---|---|---|---|---|---|"]
    for fam, lags in (("plan", PLAN), ("response", RESPONSE)):
        rs = [r for r in rows if r["family"] == fam]
        cnt = {c: sum(r["category"] == c for r in rs) for c in ("S-only", "W-only", "reweighted", "shared")}
        out.append(f"| {fam} | {', '.join(map(str, lags))} | {cnt['S-only']} | {cnt['W-only']} | {cnt['reweighted']} | {cnt['shared']} |")
    for cat in ("S-only", "W-only"):
        rs = sorted((r for r in rows if r["category"] == cat), key=lambda r: -abs(r["delta"]))[:15]
        if rs:
            out += ["", f"Strongest {cat} edges:", "", "| lag | from | to | lift S | lift W | q |", "|---|---|---|---|---|---|"]
            out += [f"| {r['lag']} | {lab(r['src'])} | {lab(r['dst'])} | {r['lift_S']:.2f} | {r['lift_W']:.2f} | {r['q']:.2g} |"
                    for r in rs]
    sig = np.flatnonzero(ms["sig"])
    out += ["", "### Motifs", "",
            f"{len(motifs)} candidate chains of lag-2 plan edges, {int(ms['tested'].sum())} with >= {a.min_count} completions "
            f"in either graph (tested); {len(sig)} differ at FDR {a.fdr} "
            f"({int((ms['lr'][sig] > 0).sum())} more in S's lines, {int((ms['lr'][sig] < 0).sum())} more in W's). "
            "follow = completions per time the first node fires with room for the chain."]
    for title, order in (("more in S's lines", sig[np.argsort(-ms["lr"][sig])]), ("more in W's lines", sig[np.argsort(ms["lr"][sig])])):
        order = [m for m in order if (ms["lr"][m] > 0) == (title.endswith("S's lines"))][:a.show]
        if not order:
            continue
        out += ["", f"Top {len(order)} {title}:", "", "| # | chain | completions S / W | roots S / W | follow S / W | log ratio | q |",
                "|---|---|---|---|---|---|---|"]
        for rank, m in enumerate(order, 1):
            out.append(f"| {rank} | {' &rarr; '.join(lab(x) for x in motifs[m])} | {int(ms['tS'][m])} / {int(ms['tW'][m])} | "
                       f"{int(ms['rootsS'][m])} / {int(ms['rootsW'][m])} | {ms['tS'][m] / max(ms['startS'][m], 1):.2f} / "
                       f"{ms['tW'][m] / max(ms['startW'][m], 1):.2f} | {ms['lr'][m]:+.2f} | {ms['q'][m]:.2g} |")
    if att:
        out += ["", "### S-only latents", "", "| latent | rate in S / W lines | in W play | strongest predecessors (lift S / W) | successors |",
                "|---|---|---|---|---|"]
        f = lambda xs: "; ".join(f"{lab(x)} ({math.exp(s):.2f} / {math.exp(w):.2f})" for s, w, x in xs) or "-"
        for r in att:
            out.append(f"| {lab(r['node'])} | {r['rate_S']:.1%} / {r['rate_W']:.1%} | "
                       f"{'absent' if r['absent'] else 'present, used differently'} | {f(r['pre'])} | {f(r['suc'])} |")
    return "\n".join(out)


def prototypes(motifs, ms, KS, KW, root_ids, Ld, by, evals, z, nodes, a):
    """For the top motifs more in S's lines: up to 3 roots where it completes in the S line and not in the W line."""
    sig = np.flatnonzero(ms["sig"] & (ms["lr"] > 0))
    top = sig[np.argsort(-ms["lr"][sig])][:a.show]
    KS, KW = KS.cpu().numpy(), KW.cpu().numpy()
    out = []
    for m in top:
        ex = []
        for r in np.flatnonzero((KS[:, m] > 0) & (KW[:, m] == 0))[:3]:
            ri = root_ids[r]
            root = Ld["roots"][ri]
            item = dict(fen=root["fen"], band=root["band"], s_top=root["s_top"], w_top=root["w_top"], lines={})
            for kind in ("S", "W"):
                q = by[(ri, kind)]
                l = Ld["lines"][q]
                e = evals[z["line_start"][q]:z["line_start"][q + 1]]
                item["lines"][kind] = dict(sans=l["sans"], first=l["moves"][0], end=float(e[-1]) if not np.isnan(e[-1]) else None)
            ex.append(item)
        out.append(dict(chain=[nodes[x]["label"] for x in motifs[m]], tS=int(ms["tS"][m]), tW=int(ms["tW"][m]),
                        lr=float(ms["lr"][m]), q=float(ms["q"][m]), ex=ex))
    return out


def page(path, name, cards):
    data = json.dumps(cards).replace("</", "<\\/")
    path.write_text(f"""<!doctype html><html><head><meta charset="utf-8"><title>Motifs: {html.escape(name)}</title>
<style>body{{font-family:system-ui,sans-serif;margin:16px;max-width:1100px}}.card{{border:1px solid #ccc;border-radius:6px;padding:10px;margin:14px 0}}
.ex{{display:flex;gap:18px;flex-wrap:wrap;margin-top:8px}}.ln{{font-family:monospace;font-size:12px;max-width:520px}}
.chain{{font-weight:600}}{BOARD_CSS}</style></head><body>{BOARD_DEFS}{MOVE_HEAD}
<h2>Motifs more often completed in S's lines than W's: {html.escape(name)}</h2>
<p>Each card: the chain (node at ply t, the next at t + 2, ...), its completions in S's / W's lines, then roots where it
completes in S's line and not in W's: the root with S's first move, and both lines (evaluations: pawns for the root's side to move,
at the line's end).</p><div id="out"></div>
<script>{BOARD_JS}
const C = {data};
const fmt = v => v === null ? "?" : (v > 0 ? "+" : "") + v.toFixed(2);
let h = "";
for (const [set, ms] of Object.entries(C)) {{
  h += `<h3>${{set}} roots</h3>`;
  ms.forEach((m, i) => {{
    h += `<div class="card"><div class="chain">${{i + 1}}. ${{m.chain.join(" &rarr; ")}}</div>
      <div>completions S ${{m.tS}} / W ${{m.tW}}, log ratio ${{m.lr.toFixed(2)}}, q ${{m.q.toPrecision(2)}}</div><div class="ex">`;
    for (const x of m.ex) {{
      h += `<div>${{board(x.fen, x.lines.S.first)}}<div class="ln">${{x.band}} game; S would play ${{x.s_top}}, W ${{x.w_top}}<br>
        <b>S line</b> (${{fmt(x.lines.S.end)}}): ${{x.lines.S.sans.join(" ")}}<br>
        <b>W line</b> (${{fmt(x.lines.W.end)}}): ${{x.lines.W.sans.join(" ")}}<br>
        <a target="_blank" href="https://lichess.org/analysis/${{x.fen.replace(/ /g, "_")}}">lichess</a></div></div>`;
    }}
    h += "</div></div>";
  }});
}}
document.getElementById("out").innerHTML = h;
</script></body></html>""", encoding="utf-8")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["health", "recall", "lines", "nodes", "graph", "all"])
    ap.add_argument("--cc-run", default="runs/transcend/crosscoder/everything-3m", help="crosscoder run folder")
    ap.add_argument("--cc", default="Lfinal", help="crosscoder in that run (one layer per model), e.g. Lfinal or L15")
    ap.add_argument("--strong", default="2400", help="a part of the strong model's name (S); the other is W")
    ap.add_argument("--device", default="auto", help="auto, cuda, mps or cpu")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--batch", type=int, default=48, help="boards per policy batch (all their legal moves at once)")
    g = ap.add_argument_group("health")
    g.add_argument("--policy-n", type=int, default=2000, help="held-out positions for the spliced policy")
    g.add_argument("--probe-n", type=int, default=200_000, help="positions for the exclusivity ridge")
    g.add_argument("--ridge", type=float, default=10.0, help="ridge penalty for the exclusivity fit")
    g = ap.add_argument_group("recall")
    g.add_argument("--cands", type=int, default=10, help="candidate latents per label")
    g.add_argument("--auc", type=float, default=0.9, help="held-out AUC at which a label counts as recovered")
    g = ap.add_argument_group("lines")
    g.add_argument("--population", default=str(PROBE / "population.jsonl"), help="held-out positions with their band")
    g.add_argument("--roots", type=int, default=4000, help="roots, half from each band")
    g.add_argument("--oversample", type=int, default=3, help="candidates per root wanted (before the disagreement filter)")
    g.add_argument("--per-game", type=int, default=2, help="roots per game at most")
    g.add_argument("--held", type=int, default=30, help="percent of games held out")
    g.add_argument("--plies", type=int, default=8, help="plies per line")
    g.add_argument("--temperature", type=float, default=0.25, help="every policy's temperature (over legal moves)")
    g.add_argument("--depth", type=int, default=12, help="Stockfish depth for every position")
    g.add_argument("--workers", type=int, default=max(1, min(16, (os.cpu_count() or 2) - 2)), help="Stockfish processes")
    g.add_argument("--max-tokens", type=int, default=300_000, help="characters per forward pass when reading the lines")
    g = ap.add_argument_group("nodes")
    g.add_argument("--margin", type=float, default=0.5, help="pawns by which Stockfish must prefer the chosen line's end")
    g.add_argument("--min-rate", type=float, default=0.01, help="filter 1: fires on at least this share of line positions")
    g.add_argument("--min-pairs", type=int, default=30, help="filter 2: informative fit pairs needed")
    g.add_argument("--sep", type=float, default=0.65, help="filter 2: share of informative fit pairs with the majority sign")
    g.add_argument("--min-pairs-held", type=int, default=15, help="filter 3: informative held-out pairs needed")
    g.add_argument("--sep-held", type=float, default=0.60, help="filter 3: share of held-out pairs with the fit sign")
    g.add_argument("--max-nodes", type=int, default=300, help="latent nodes kept at most")
    g.add_argument("--null", type=int, default=50, help="random label flips for the null")
    g = ap.add_argument_group("graph")
    g.add_argument("--split", choices=["fit", "held"], default="fit", help="roots the graphs are built on")
    g.add_argument("--blunder", type=float, default=1.5, help="pawns: a W move losing more makes the root tactical")
    g.add_argument("--min-roots", type=int, default=50, help="roots a set needs to be analysed")
    g.add_argument("--lift", type=float, default=1.5, help="lift for a strong edge")
    g.add_argument("--min-count", type=int, default=10, help="co-occurrences an edge needs in either graph to be tested")
    g.add_argument("--fdr", type=float, default=0.05, help="Benjamini-Hochberg false discovery rate")
    g.add_argument("--boot", type=int, default=1000, help="bootstrap resamples of the roots")
    g.add_argument("--boot-chunk", type=int, default=25, help="bootstrap resamples at once (GPU memory)")
    g.add_argument("--max-motifs", type=int, default=20_000, help="motif candidates at most")
    g.add_argument("--show", type=int, default=20, help="motifs listed (and drawn) per direction")
    a = ap.parse_args()
    steps = dict(health=health, recall=recall, lines=lines, nodes=nodes, graph=graph)
    for name in (steps if a.command == "all" else [a.command]):
        print(f"\n=== {name}", flush=True)
        steps[name](a)


if __name__ == "__main__":
    main()
