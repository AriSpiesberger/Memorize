"""Concept-graph diff: what separates the 2400+ model's (S) rollouts from the 1000-1300 model's (W), from the
same root positions, on the crosscoder's latents alone (no engine in the analysis). Two levels: plan
templates, a sparse combination of latents per ply fitted by a max-min LP to separate S's rollouts from
W's and kept only if that margin holds on new games (plans), and the latents and the chains between them,
G_S against G_W (nodes, graph).

    python transcend/graphdiff.py health --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal
    python transcend/graphdiff.py recall --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal
    python transcend/graphdiff.py lines  --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal
    python transcend/graphdiff.py plans  --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal
    python transcend/graphdiff.py nodes  --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal
    python transcend/graphdiff.py graph  --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal
    python transcend/graphdiff.py all    --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal
    modal run --detach modal/modal_graphdiff.py::main            # the same on Modal, the slow parts spread out

lines is five stages, which Modal runs separately and in parallel (--part/--parts):
roots (candidates, policies), play (the rollouts), gather (-> lines.json), judge (board facts), encode (codes).

health  Gate 1, on the crosscoder's held-out games (crosscoder.py train's validation positions):
        - reconstruction: fraction of variance unexplained (FVU) per model;
        - spliced policy: each model's distribution over the legal moves with its state at the
          crosscoder's layer (at the prompt's last character, where the crosscoder reads it) replaced
          by the reconstruction: KL(real || spliced) and top-1 agreement; next to the same with the
          state replaced by its mean over the positions (the scale: "KL recovered" = 1 - KL spliced /
          KL mean) and with the real state put back (a check of the splice itself: KL ~ 0);
        - density: L0, dead latents (never fire), dense ones (fire on > 10% / > 50% of positions);
        - exclusivity: relative decoder norm r = |d_S| / (|d_S| + |d_W|) tags each latent S-only
          (r > 0.9), W-only (r < 0.1), shared (0.3-0.7) or leaning. Two checks of the tag:
            predictability  the same ridge regression from each model's own states to the latent's
                            activation, fitted on half the games, R^2 on the other half. An S-only
                            latent is confirmed when S's own R^2 >= --r2-floor and W's is at most half
                            of it; with S's R^2 below the floor it is "unconfirmed" (neither model
                            predicts it well), not S-only. The reverse for W-only. The encoder reads
                            S's states directly, so for a latent that leans on S's encoder weights S's
                            R^2 is high almost by construction: read the ratio with that in mind.
            latent scaling  within each model's own decoder space (after Minder et al. 2025): beta_m
                            is the scale along latent j's unit decoder direction in model m that best
                            fits m's activation minus the other latents' reconstruction, where j fires;
                            nu = beta_W / beta_S (S-only) or beta_S / beta_W (W-only): small = exclusive.
        -> results/transcend/graphdiff/<run>/health.json; <run>/exclusivity.npz
recall  Gate 2, known-concept recall (naming only: it labels latents, it filters nothing). Labels:
          on explain.py's 100k stored positions (run explain.py first): board facts (predicates.py) and
          skill facts (Stockfish and Maia-2, skill.py) from facts.npz; square facts (which piece stands
          where) from squares.npz; with --classic (a Stockfish 8-11 binary, whose `eval` prints the
          classical evaluation by term: material, imbalance, pawns, knights, bishops, rooks, queens,
          mobility, king safety, threats, passed pawns, space, ...), per term "clearly favours the
          side to move" (>= its 80th percentile and 0.1 pawns) and "favours the opponent";
          on --puzzles Lichess puzzles, rebuilt from their source game's moves (eval.histories; the
          ~8k cached from the pass@k runs, --fetch-puzzles fetches more from Lichess) at the position
          the solver moves from, read by both models: the puzzle themes (fork, pin, mateIn2, ...).
        STS is left out: its positions come without the moves that lead to them, and these models
        read nothing but move text (the Leela trick of repeating the position has no move-text analogue).
        Per label, on one half of the games: the --cands latents whose mean activation differs most
        with and without it (in standard deviations), the best of them by AUC, and except for square
        labels the best combination of up to 3 (logistic regression, added greedily); AUC on the other
        half. Recall = the fraction of labels at held-out AUC >= --auc. Control: each label shuffled
        across positions (recall should be ~0).
        -> results/transcend/graphdiff/<run>/recall.json
lines   Roots: held-out positions of both bands (data/pgn_probe/population.jsonl, the validation games
        of each model's dataset), in the middlegame (after move 10, more than 6 pieces besides kings
        and pawns); --roots of them, half from each band,
        at most --per-game per game, split by game (--held % held out) before anything else.
        Policies are over the legal moves: a move's probability is the product of its characters'
        (each prompt's cache shared by all its legal moves); a move is drawn from p^(1/--temperature),
        renormalised (--temperature 1: each model's own imitation distribution; 0: greedy). No filter on whether
        S and W would play differently: the rollouts diverge on their own. From each root, --rollouts of each,
        --plies plies:
            "S"   S writes every move, both colours
            "W"   W writes every move, both colours
            "S2"  S again (--control): the S-vs-S control, which takes S's sampling noise through the same pipeline
        (both models are pure imitation learners: a rollout is one model imitating the game from the root, with no
        player and no opponent)
        Every position is read by both models and encoded with the crosscoder (and its FVU there: the
        crosscoder never saw rollouts); board facts (predicates.py, position facts) for the anchor nodes.
        --depth > 0 adds Stockfish's evaluation of every position (only for the report's line-end
        evaluations and, with graph --engine-split, a positional/tactical split; nothing is filtered by it).
        -> <run>/roots.json, play-*.json, lines.json, judge-*.npz, codes.npz, evals.npy, facts.npy, meta.json
plans   Concepts, as in Schut et al. (AlphaZero concept discovery), in the crosscoder's latent space: the
        crosscoder gives both models one standardised dictionary, so S's and W's rollouts are compared on the
        same features (never on the models' own activations, which live in different spaces). A concept is a
        non-negative vector v over the latents (activations scaled by each latent's mean where it fires,
        latents firing on --min-rate..--max-rate), applied to every ply of a rollout and averaged over its plies
        (--sum-plies all; own/split are options; averaged, not summed, so a rollout that ends early isn't
        smaller), so it can occur at any ply. Per root, d = the mean over S's rollouts minus over W's (plies after
        the root, which they all share). One departure from Schut, who requires v . z+_t >= v . z-_t at every
        step: here the rollout's total has to separate, so a concept may sit in a few plies. Roots are split by
        game three ways: fit (not held out), selection and replication (the held-out games, halved).
          1. fit       the max-min LP, once per side (S's concepts on d, W's on -d):
                         max m  s.t.  v . d_i >= m for the roots i,  sum v <= 1,  v >= 0
                       per cluster of --cluster-size roots whose rollouts diverge alike (cosine k-means on the
                       fit roots' d); soft margin: a share --nu of the roots may fall inside it. Dual simplex
                       (scipy's HiGHS): a vertex, so sparse.
          2. merge     concepts matching at cosine >= --dedupe join one group (the members' mean).
          3. margin    the filter: on the selection roots, the concept's soft margin (the share --nu quantile
                       of v . d, what the LP maximised) must be > 0 and above the 95th percentile of
                       --null-templates random concepts with its weights and latents of the same firing-rate
                       decile (never its own); then the same on the replication roots. --local (default): a
                       concept is scored on the held-out roots of its own clusters (each held-out root joins its
                       nearest cluster centroid by d), the random concepts on the same roots; a concept real for
                       one kind of divergence is not asked to hold everywhere. At least --min-concept-roots of them.
          control      with S2 rollouts: each concept's margin on S - S2 on the same roots (a concept that also
                       separates S from S is noise, and dropped), and the whole of 1-3 run on S - S2 (how many
                       concepts sampling noise alone produces).
          4. graph     concepts as nodes, on the replication roots: active at a ply when v . (that ply's latents)
                       reaches halfway between its mean on S's and on W's selection rollouts. Follows: lift at lags
                       2, 4, 6, G_S vs G_W, bootstrap + BH (as for latents); competes: active together less than
                       chance (lag-0 lift with its interval below 1); replaces: S's rollout carries out B where
                       W's carries out A (a rollout carries a concept out when its summed score reaches the halfway
                       mark), lift over chance.
        -> results/transcend/graphdiff/<run>/plans.md; <run>/plans.json, plans.html (the concept graph and a
           card per concept: its latents, and roots where its side's rollout carries it out)
nodes   Latents, from the rollouts alone. Per root and latent, d = its activation averaged over S's
        rollouts minus over W's (plies after the root); a root counts for a latent when d != 0. Exact sign test on
        >= --min-pairs fit roots (BH at --fdr-nodes over the latents firing on --min-rate..--max-rate),
        confirmed one-sided on >= --min-pairs-held held-out roots; null: S and W swapped on random roots,
        --null times; control: the same tests on S against S2. The graph's nodes (at most --max-nodes): the latents of the plan templates that
        passed the margin filter, then the latents S and W differ on, then the most common; board facts
        true on 1-99% of positions are anchor nodes. -> <run>/nodes.json
graph   G_S from the "S" rollouts, G_W from the "W" rollouts, same nodes, same roots (--split fit; held for
        the replication). A node is active at a ply when its activation is above its 90th percentile
        over all line positions (for a latent firing on < 10% of them: when it fires). Edges from every ply
        (the models write both colours' moves, so no ply is special) at lags 1, 2, 3, 4, 6. Over (root, ply)
        pairs, n of them, n_A with A at t, n_B with B at t + k:
            lift_k(A -> B) = (n_AB + a) / (n_A n_B / n + a)        (P(B | A) / P(B), shrunk to 1 by a = --prior)
        delta = log lift_S - log lift_W; roots resampled (--boot Poisson bootstraps, one draw for both
        graphs), z = delta / its bootstrap sd, two-sided normal p, Benjamini-Hochberg at --fdr over
        every edge with n_AB >= --min-count in either graph (no self edges). S-only: significant, S's
        lift >= --lift with its 95% interval above 1, W's interval covering 1; W-only the reverse;
        reweighted: the other significant ones.
        Motifs: chains A -> B -> C (-> D) of lag-2 edges that pass (lift >= --lift, interval above
        1) in either graph. Per root, completions (A at t, B at t + 2, C at t + 4, ...) in its S rollout
        and its W rollout; the effect is the log ratio of the totals (+1 each), the test an exact paired
        one on roots (McNemar: roots where it completes in S's rollout and not W's against the reverse),
        BH at --fdr over chains with >= --min-discordant such roots; split by the root's band too
        (positions from 1000-1300 games are ones S rarely saw in training). Next to it the rate the
        chain completes once A fires, which separates "W doesn't reach A" from "W reaches A and goes
        elsewhere". S-only latent nodes: their strongest lag-2 neighbours among shared nodes in G_S,
        and whether W's rollouts reach them.
        -> results/transcend/graphdiff/<run>/report.md (gates, nodes, diff, motifs),
           edges-<set>-<split>.csv (the significant edges), motifs-<set>-<split>.csv; <run>/motifs-<split>.html (the top --show
           motifs, each with roots where it completes in the S rollout and not the W rollout).

All thresholds are starting values: set them once from the nulls, then freeze them before reading the diff.
"""
import argparse
import csv
import html
import json
import math
import os
import re
import subprocess
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
MATE_PAWNS = 15.0
ANCHORS = [n for n in predicates.NAMES if not n.startswith("move_")]   # position facts: the anchor nodes
PLAN, RESPONSE = (2, 4, 6), (1, 3)
EXCL = {0: "not scored", 1: "confirmed", 2: "not confirmed", 3: "unconfirmed"}


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
        c = np.full((len(idx) * R, n + 1), SPACE, dtype=np.int64)
        clen = np.ones(len(idx) * R, dtype=np.int64)
        for j, i in enumerate(idx):
            for r, mv in enumerate(legal[i]):
                t = encode(boards[i].san(mv) + " ")
                c[j * R + r, :len(t)] = t
                clen[j * R + r] = len(t)
        c, clen = torch.from_numpy(c).to(dev), torch.from_numpy(clen).to(dev)
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
    dirs = [cc.coder.W_dec[:, cc.col[m]] / cc.coder.W_dec[:, cc.col[m]].norm(dim=-1, keepdim=True).clamp_min(1e-8)
            for m in (cc.s, cc.w)]                           # (latents, d) unit decoder directions, S then W
    num = torch.zeros((2, L), dtype=torch.float64, device=dev)
    den = torch.zeros(L, dtype=torch.float64, device=dev)
    for i in range(0, len(tr), 4096):
        x = stack(arrs, tr[i:i + 4096], cc.scales, dev)
        f = cc.coder.encode(x)[0]
        e = x - cc.coder.decode(f)
        for j, m in enumerate((cc.s, cc.w)):
            num[j] += (f * (e[:, cc.col[m]] @ dirs[j].T)).sum(0).double()
        f = f.double()
        den += (f ** 2).sum(0)
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
    norms = cc.coder.norms()
    beta = [(norms[:, cc.col[m]].double() + num[j] / den.clamp_min(1e-12)).cpu().numpy() for j, m in enumerate((cc.s, cc.w))]
    ok = (nf[0] >= 50).cpu().numpy() & (nf[1] >= 50).cpu().numpy()
    status = np.zeros(L, dtype=np.int8)                        # 0 not scored, 1 confirmed, 2 not confirmed, 3 unconfirmed
    nu = np.full(L, np.nan)
    excl = {}
    for t in ("S-only", "W-only", "shared"):
        m = ok & (tags == t)
        own, other = (r2S, r2W) if t != "W-only" else (r2W, r2S)
        b_own, b_other = (beta[0], beta[1]) if t != "W-only" else (beta[1], beta[0])
        nu[m] = b_other[m] / np.maximum(np.abs(b_own[m]), 1e-9)
        floor = own >= a.r2_floor
        if t != "shared":
            status[m & floor & (other <= 0.5 * own)] = 1
            status[m & floor & (other > 0.5 * own)] = 2
            status[m & ~floor] = 3
        med = lambda v: float(np.median(v[m])) if m.any() else None
        excl[t] = dict(latents=int(m.sum()), r2_S=med(r2S), r2_W=med(r2W), nu=med(nu),
                       nu_q=[float(v) for v in np.quantile(nu[m], [0.1, 0.9])] if m.any() else None,
                       **({k: int((status[m] == c).sum()) for k, c in (("confirmed", 1), ("not_confirmed", 2), ("unconfirmed", 3))}
                          if t != "shared" else {}))
    rec["exclusivity"] = excl
    rec["r2_floor"] = a.r2_floor
    cc.out.mkdir(parents=True, exist_ok=True)
    np.savez(cc.out / "exclusivity.npz", r=cc.r, r2_S=r2S, r2_W=r2W, beta_S=beta[0], beta_W=beta[1], nu=nu,
             scored=ok, status=status, rate=rate)

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
            f"Exclusivity checks (own-model R^2 floor {rec['r2_floor']}): confirmed = own R^2 above the floor and the other "
            "model's at most half of it; unconfirmed = own R^2 below the floor. nu = the other model's latent scaling over the "
            "own model's (10th-90th percentile): small = exclusive. The encoder reads both models' states, so a latent leaning "
            "on S's encoder weights is predictable from S's states almost by construction.", "",
            "| tag | latents scored | median R^2 from S's states | from W's | confirmed | not confirmed | unconfirmed | median nu (10-90%) |",
            "|---|---|---|---|---|---|---|---|"]
    for t, e in rec["exclusivity"].items():
        f = lambda v: "-" if v is None else f"{v:.2f}"
        q = e.get("nu_q")
        out.append(f"| {t} | {e['latents']} | {f(e['r2_S'])} | {f(e['r2_W'])} | {e.get('confirmed', '-')} | "
                   f"{e.get('not_confirmed', '-')} | {e.get('unconfirmed', '-')} | {f(e.get('nu'))}"
                   + (f" ({q[0]:.2f}-{q[1]:.2f})" if q else "") + " |")
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


class Classic:
    """An old Stockfish (8 to 11, before the classical evaluation was removed) whose `eval` command prints
    the classical evaluation term by term. terms(fen) -> {term: pawns for White, middlegame and endgame
    averaged}; {} when it prints no table (in check)."""

    def __init__(self, path):
        self.p = subprocess.Popen([path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
        self.send("uci")
        self.until(lambda l: l.startswith("uciok"))

    def send(self, cmd):
        self.p.stdin.write(cmd + "\n")
        self.p.stdin.flush()

    def until(self, stop, most=400):
        lines = []
        for _ in range(most):
            line = self.p.stdout.readline()
            if not line:
                raise RuntimeError("the classical Stockfish stopped")
            lines.append(line.rstrip())
            if stop(lines[-1]):
                return lines
        raise RuntimeError("no end of the eval trace: is this Stockfish 8-11?")

    def terms(self, fen):
        self.send(f"position fen {fen}")
        self.send("eval")
        out = {}
        for line in self.until(lambda l: re.match(r"\s*(total|final) evaluation", l, re.I) is not None):
            parts = [x.strip() for x in line.split("|")]
            if len(parts) < 3 or not parts[0] or parts[0] in ("Term", "Total") or parts[0].startswith("-"):
                continue
            nums = re.findall(r"-?\d+\.\d+", parts[-1])
            if len(nums) >= 2:
                out[parts[0]] = (float(nums[0]) + float(nums[1])) / 2
        return out

    def close(self):
        try:
            self.send("quit")
            self.p.wait(timeout=5)
        except Exception:
            self.p.kill()


_classic = _corpus = None


def _classic_init(path, folders):
    global _classic, _corpus
    _classic, _corpus = Classic(path), Corpus(folders)


def _classic_terms(rows):
    """Classical terms for a chunk of stored positions, from the side to move's point of view."""
    out = []
    for row in rows:
        b = position(_corpus, row)[0]
        t = _classic.terms(b.fen())
        out.append({k: v if b.turn == chess.WHITE else -v for k, v in t.items()})
    return out


def classic_labels(path, rows, idx, folders, cache, workers):
    """Per classical term, two labels over the stored positions: it clearly favours the side to move
    (>= its 80th percentile and >= 0.1 pawns) or the opponent (<= its 20th percentile and <= -0.1);
    with a mask of the positions the trace exists for (none in check). Cached."""
    if cache.exists() and np.array_equal(np.load(cache)["idx"], idx):
        z = np.load(cache)
        names, V = [str(n) for n in z["names"]], z["V"]
    else:
        print(f"  classical evaluation terms ({path}), {workers} workers", flush=True)
        with Pool(workers, initializer=_classic_init, initargs=(path, folders)) as pool:
            ts = [t for part in pool.imap(_classic_terms, np.array_split(rows[idx], max(1, len(idx) // 200))) for t in part]
        names = sorted({k for t in ts for k in t})
        V = np.array([[t.get(k, np.nan) for k in names] for t in ts], dtype=np.float32)
        np.savez(cache, idx=idx, names=np.array(names), V=V)
    has = ~np.isnan(V).all(1) if len(names) else np.zeros(len(idx), bool)
    print(f"  classical trace for {has.mean():.0%} of positions ({len(names)} terms: {', '.join(names)}); none means in "
          "check, or an output format this parser doesn't know", flush=True)
    Y, M, out = [], [], []
    for k, n in enumerate(names):
        v, ok = V[:, k], ~np.isnan(V[:, k])
        if ok.sum() < 100:
            continue
        hi, lo = max(np.quantile(v[ok], 0.8), 0.1), min(np.quantile(v[ok], 0.2), -0.1)
        for side, lab in (("us", ok & (v >= hi)), ("them", ok & (v <= lo))):
            Y.append(lab)
            M.append(ok)
            out.append(f"classic: {n} favours {side}")
    return (np.stack(Y, 1), np.stack(M, 1), out) if out else (None, None, [])


def puzzle_set(a, ctx):
    """Lichess puzzles with their source game's moves (eval.histories: cached in data/lichess/puzzles;
    --fetch-puzzles fetches the missing ones): the position the solver moves from, its themes, its game."""
    from lichess_ids import game_id
    hist = paths.LICHESS / "puzzles" / "histories.jsonl"
    cached = {d["game"] for d in map(json.loads, open(hist)) if d["moves"]} if hist.exists() else set()
    files = sorted((paths.LICHESS / "puzzles" / "strata").glob("*.jsonl")) + [paths.LICHESS / "puzzles" / "pool" / "1050.jsonl"]
    seen, ps = set(), []
    for f in files:
        if not f.exists():
            continue
        for line in open(f, encoding="utf-8"):
            p = json.loads(line)
            if p["id"] not in seen and (a.fetch_puzzles or game_id(p["game"]) in cached):
                seen.add(p["id"])
                ps.append(p)
    rng = np.random.default_rng(a.seed)
    ps = [ps[i] for i in rng.permutation(len(ps))[:a.puzzles]]
    out = []
    for p, b in zip(ps, ev.histories(ps) if ps else []):
        if b is None:
            continue
        b = b.copy()
        b.push_uci(p["moves"][0])                                      # the opponent's move that sets the puzzle up
        if len(prompt(b)) + 1 <= ctx:
            out.append((b, set(p["themes"]), game_id(p["game"])))
    return out


def score_labels(Fs, Y, M, fit, test, names, group, a, rng):
    """Per label: the best of its --cands candidate latents by fit-half AUC, its held-out AUC, the best
    combination of up to 3 (not for square labels), and the same with the label shuffled (null).
    Fs (n, latents) on the device; Y, M (n, labels) bools: the label, and where it is defined."""
    dev = Fs.device
    nul = [k for k, g in enumerate(group) if g != "square"]
    Yn, Mn = Y[:, nul].copy(), M[:, nul]
    for hh in (fit, test):                                            # shuffled within each half
        w = np.flatnonzero(hh)
        Yn[w] = Yn[rng.permutation(w)]
    Yt = torch.from_numpy(np.concatenate([Y, Yn], 1)).to(dev)
    Mt = torch.from_numpy(np.concatenate([M, Mn], 1)).to(dev)
    K = Yt.shape[1]
    fit_t, test_t = torch.from_numpy(fit).to(dev), torch.from_numpy(test).to(dev)
    # candidates: standardised difference of mean activation with and without the label, fit half
    S1, S0 = torch.zeros((K, Fs.shape[1]), device=dev), torch.zeros((K, Fs.shape[1]), device=dev)
    sall, ss = torch.zeros(Fs.shape[1], device=dev), torch.zeros(Fs.shape[1], device=dev)
    fr = torch.nonzero(fit_t)[:, 0]
    for i in range(0, len(fr), 8192):
        r = fr[i:i + 8192]
        f = Fs[r].float()
        S1 += (Yt[r] & Mt[r]).float().T @ f
        S0 += (~Yt[r] & Mt[r]).float().T @ f
        sall += f.sum(0)
        ss += (f ** 2).sum(0)
    n1 = (Yt & Mt)[fit_t].float().sum(0)[:, None]
    n0 = (~Yt & Mt)[fit_t].float().sum(0)[:, None]
    nfit = float(fit_t.sum())
    sd = (ss / nfit - (sall / nfit) ** 2).clamp_min(1e-8).sqrt()
    diff = (S1 / n1.clamp_min(1) - S0 / n0.clamp_min(1)) / sd[None]
    cands = diff.abs().topk(min(a.cands, Fs.shape[1]), 1).indices
    out, t0 = [], time.time()
    for k in range(K):
        y, m = Yt[:, k], Mt[:, k]
        mf, mt = fit_t & m, test_t & m
        yf, yt = y[mf], y[mt]
        best = None
        for j in cands[k].tolist():
            sgn = 1.0 if diff[k, j] >= 0 else -1.0
            au = auc_t(Fs[mf, j].float() * sgn, yf)
            if best is None or au > best[1]:
                best = (j, au, sgn)
        j, au_fit, sgn = best
        r = dict(fit_auc=au_fit, test_auc=auc_t(Fs[mt, j].float() * sgn, yt), latent=j, sign=int(sgn))
        if k < len(names):
            r.update(label=names[k], group=group[k], rate=float(yf.float().mean()))
            if group[k] != "square":                                  # up to 3 latents, added greedily
                chosen, cur = [j], au_fit
                for _ in range(2):
                    trial = []
                    for c in cands[k].tolist():
                        if c not in chosen:
                            Xc = Fs[:, chosen + [c]].float()
                            sf, _ = logistic(Xc[mf], yf, Xc[mt])
                            trial.append((auc_t(sf, yf), c))
                    if not trial or max(trial)[0] < cur + 0.005:
                        break
                    cur, c = max(trial)
                    chosen.append(c)
                if len(chosen) > 1:
                    Xc = Fs[:, chosen].float()
                    _, st_ = logistic(Xc[mf], yf, Xc[mt])
                    r.update(combo=chosen, combo_test_auc=auc_t(st_, yt))
            out.append(r)
        else:
            out[nul[k - len(names)]]["null_test_auc"] = r["test_auc"]
        if (k + 1) % 50 == 0:
            print(f"\r  {k + 1}/{K} labels, {time.time() - t0:.0f}s", end="", flush=True)
    print()
    return out


def enough(Y, M, fit, test, n=30):
    """Labels with >= n positives and negatives in each half."""
    return [k for k in range(Y.shape[1])
            if min(min((Y[h, k] & M[h, k]).sum(), (~Y[h, k] & M[h, k]).sum()) for h in (fit, test)) >= n]


@torch.no_grad()
def recall(a):
    dev = ev.device(a.device)
    cc = load_cc(a.cc_run, a.cc, a.strong, dev)
    rng = np.random.default_rng(a.seed)
    rows = np.load(cc.run / "rows.npy")
    fpath = next((p for p in [cc.dir / "facts.npz", *sorted(cc.run.glob("cc-*/facts.npz"))] if p.exists()), None)
    if fpath is None:
        sys.exit(f"no facts.npz under {cc.run}: run explain.py on this crosscoder run first")
    # the stored positions: board and skill facts, square facts, classical evaluation terms
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
    M = np.ones_like(Y)
    if a.classic:
        Yc, Mc, nc = classic_labels(a.classic, rows, idx, cc.info["folders"], cc.run / "classic.npz", a.workers)
        if nc:
            Y, M, names, group = np.concatenate([Y, Yc], 1), np.concatenate([M, Mc], 1), names + nc, group + ["classic"] * len(nc)
    halves = (rows[idx, 0].astype(np.int64) * 1_000_003 + rows[idx, 1]) * 2654435761 % 2 ** 32 % 2
    fit, test = halves == 0, halves == 1
    ok = enough(Y, M, fit, test)
    Y, M, names, group = Y[:, ok], M[:, ok], [names[k] for k in ok], [group[k] for k in ok]
    print(f"gate 2, stored positions: {len(names)} labels ({', '.join(f'{g} {group.count(g)}' for g in dict.fromkeys(group))}) "
          f"on {len(idx)} positions ({fpath})", flush=True)
    arrs = load_sources(cc.run, cc.sources)
    Fs = torch.empty((len(idx), cc.ck["latents"]), dtype=torch.float16, device=dev)
    for i in range(0, len(idx), 4096):
        Fs[i:i + 4096] = cc.coder.encode(stack(arrs, idx[i:i + 4096], cc.scales, dev))[0].half()
    out = score_labels(Fs, Y, M, fit, test, names, group, a, rng)
    sets = dict(stored=len(idx))
    del Fs
    # Lichess puzzle themes, on puzzle positions read by both models
    if a.puzzles:
        models = {m: ev.load(cc.info["models"][m], dev)[0] for m in (0, 1)}
        ps = puzzle_set(a, min(m.ctx for m in models.values()))
        themes = sorted({t for _, ts, _ in ps for t in ts})
        Yp = np.array([[t in ts for t in themes] for _, ts, _ in ps], dtype=bool).reshape(len(ps), len(themes))
        hp = np.array([zlib.crc32(g.encode()) % 2 for _, _, g in ps])
        okp = enough(Yp, np.ones_like(Yp), hp == 0, hp == 1)
        print(f"gate 2, puzzles: {len(ps)} puzzle positions with their game's moves, {len(okp)} themes with enough of each",
              flush=True)
        if okp:
            seqs = [encode(prompt(b)) for b, _, _ in ps]
            st = {m: line_states(models[m], seqs, [[len(s) - 1] for s in seqs], cc.layer[m], dev, a.max_tokens) for m in (0, 1)}
            Fp = torch.empty((len(ps), cc.ck["latents"]), dtype=torch.float16, device=dev)
            for i in range(0, len(ps), 4096):
                Fp[i:i + 4096] = encode_states(cc, {m: st[m][i:i + 4096].to(dev) for m in (0, 1)})[0].half()
            Yp = Yp[:, okp]
            out += score_labels(Fp, Yp, np.ones_like(Yp), hp == 0, hp == 1, [f"puzzle: {themes[k]}" for k in okp],
                                ["puzzle"] * len(okp), a, rng)
            sets["puzzles"] = len(ps)
    best = lambda r: max(r["test_auc"], r.get("combo_test_auc", 0))
    summ = {}
    for g in [*dict.fromkeys(r["group"] for r in out), "all"]:
        rs = [r for r in out if g in ("all", r["group"])]
        summ[g] = dict(labels=len(rs), **{f"recall_{t}": float(np.mean([best(r) >= t for r in rs])) for t in (a.auc, 0.8)},
                       **{f"recall_single_{t}": float(np.mean([r["test_auc"] >= t for r in rs])) for t in (a.auc, 0.8)})
        nr = [r["null_test_auc"] for r in rs if "null_test_auc" in r]
        if nr:
            summ[g][f"null_recall_{a.auc}"] = float(np.mean(np.array(nr) >= a.auc))
            summ[g]["null_median_auc"] = float(np.median(nr))
    rec = dict(facts=str(fpath), positions=sets, auc=a.auc, cands=a.cands, classic=a.classic, summary=summ, labels=out)
    cc.res.mkdir(parents=True, exist_ok=True)
    (cc.res / "recall.json").write_text(json.dumps(rec, indent=1))
    print(recall_text(rec))
    print(f"wrote {cc.res / 'recall.json'}")


def recall_text(rec):
    t = rec["auc"]
    pos = rec["positions"] if isinstance(rec["positions"], dict) else dict(stored=rec["positions"])
    out = [f"## Gate 2: known-concept recall ({', '.join(f'{n} {k} positions' for k, n in pos.items())}; held-out half of the games)",
           "", f"| labels | n | recall at AUC >= {t} (best of 1-3 latents) | single latent | at AUC >= 0.8 | shuffled labels: recall | "
               "shuffled: median AUC |", "|---|---|---|---|---|---|---|"]
    for g, s in rec["summary"].items():
        nr = s.get(f"null_recall_{t}")
        out.append(f"| {g} | {s['labels']} | {s[f'recall_{t}']:.0%} | {s[f'recall_single_{t}']:.0%} | {s['recall_0.8']:.0%} | "
                   f"{'-' if nr is None else f'{nr:.0%}'} | {s.get('null_median_auc', float('nan')):.2f} |")
    worst = sorted((r for r in rec["labels"] if r["group"] != "square"),
                   key=lambda r: max(r["test_auc"], r.get("combo_test_auc", 0)))[:15]
    out += ["", "Labels (not squares) the dictionary recovers worst: " + "; ".join(
        f"{r['label']} {max(r['test_auc'], r.get('combo_test_auc', 0)):.2f}" for r in worst)]
    if not rec.get("classic"):
        out += ["", "Not in the library: Stockfish's classical evaluation terms (pass --classic with a Stockfish 8-11 binary) "
                    "and STS (positions without the moves that lead to them)."]
    return "\n".join(out)


# ---------------------------------------------------------------- the lines

_eng = _depth = None


def _eval_init(depth):
    global _eng, _depth
    _eng, _depth = (skill.Annotator(depth=depth) if depth else None), depth


def _eval(job):
    """Stockfish's evaluation for the side to move (centipawns, mates as +/- skill.MATE) and the
    anchor facts, for one position given as the position before it and the move to it."""
    key, prev, uci = job
    b = chess.Board(prev)
    b.push(chess.Move.from_uci(uci))
    v = predicates.features(b)
    facts = [v[predicates.NAMES.index(n)] for n in ANCHORS]
    if not _depth:
        return key, None, facts
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
    if T <= 0:                                                          # greedy
        return int(np.argmax(logp))
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


def dirs(a):
    """This crosscoder's run folder (runs/transcend/graphdiff/<run>) and results folder."""
    name = f"{Path(a.cc_run).name}-{a.cc.removeprefix('cc-')}"
    return RUNS / name, RESULTS / name


def roots_stage(a):
    """The roots and both models' policies there -> <run>/roots.json."""
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
        if taken[r["band"]] >= a.roots // len(bands):                 # no disagreement filter: rollouts diverge on their own
            continue
        taken[r["band"]] += 1
        held = zlib.crc32(f"{r['band']}/{r['game']}".encode()) % 100 < a.held
        roots.append(dict(band=r["band"], game=r["game"], ply=r["ply"], fen=b.fen(), prompt=r["prompt"], held=bool(held),
                          s_top=b.san(legal[k][lpS[k].argmax()]), w_top=b.san(legal[k][lpW[k].argmax()]),
                          s_p=float(np.exp(lpS[k].max())), w_p=float(np.exp(lpW[k].max())),
                          legal=[m.uci() for m in legal[k]], lpS=lpS[k].round(5).tolist(), lpW=lpW[k].round(5).tolist()))
    print(f"{len(roots)} roots ({sum(r['held'] for r in roots)} held out by game); S's and W's most likely first moves "
          f"differ at {sum(lpS[k].argmax() != lpW[k].argmax() for k in range(len(cand))) / len(cand):.0%} of them", flush=True)
    settings = {k: getattr(a, k) for k in ("plies", "temperature", "seed", "held", "depth", "rollouts", "control")}
    (cc.out / "roots.json").write_text(json.dumps(dict(roots=roots, bands=bands, settings=settings)), encoding="utf-8")
    print(f"wrote {cc.out / 'roots.json'}")


def play_stage(a):
    """S's and W's rollouts from the roots with index % --parts == --part -> <run>/play-<part>-of-<parts>.json.
    --rollouts of each per root: "S": S writes every move (both colours), "W": W writes every move: each model
    imitating the game from the root; with --control, "S2": another --rollouts of S, for the S-vs-S control."""
    dev = ev.device(a.device)
    out, _ = dirs(a)
    R = json.loads((out / "roots.json").read_text(encoding="utf-8"))
    cc = load_cc(a.cc_run, a.cc, a.strong, "cpu")
    models = {m: ev.load(cc.info["models"][m], dev)[0] for m in (0, 1)}
    Sm, Wm = models[cc.s], models[cc.w]
    rng = np.random.default_rng([a.seed, a.part])
    L = []
    for ri, r in enumerate(R["roots"]):
        if ri % a.parts != a.part:
            continue
        b = ev.board_of(parse_movetext(r["prompt"])[0])
        legal = [chess.Move.from_uci(u) for u in r["legal"]]
        kinds = [("S", np.array(r["lpS"])), ("W", np.array(r["lpW"]))] + ([("S2", np.array(r["lpS"]))] if a.control else [])
        for kind, lp in kinds:
            for k in range(a.rollouts):
                line = dict(root=ri, kind=kind, r=k, board=b.copy(), moves=[], sans=[], prompt=r["prompt"])
                advance(line, legal[sample(lp, a.temperature, rng)])
                L.append(line)
    t0 = time.time()
    for ply in range(1, a.plies):
        live = [l for l in L if len(l["moves"]) == ply and not l["board"].is_game_over()]
        for m, model in ((cc.s, Sm), (cc.w, Wm)):
            group = [l for l in live if (cc.w if l["kind"] == "W" else cc.s) == m]          # S2: S again (the control)
            if group:
                lg, lp, _ = policy(model, [l["board"] for l in group], dev, [l["prompt"] for l in group], batch=a.batch)
                for l, mv, p in zip(group, lg, lp):
                    advance(l, mv[sample(p, a.temperature, rng)])
        print(f"\r  part {a.part + 1}/{a.parts}: {len(L)} lines, ply {ply + 1}/{a.plies}, {time.time() - t0:.0f}s", end="", flush=True)
    print()
    for l in L:
        del l["board"], l["prompt"]
    path = out / f"play-{a.part}-of-{a.parts}.json"
    path.write_text(json.dumps(L), encoding="utf-8")
    print(f"wrote {path}")


def gather(a):
    """The play parts -> <run>/lines.json (roots in order, then the kinds in play order)."""
    out, _ = dirs(a)
    R = json.loads((out / "roots.json").read_text(encoding="utf-8"))
    parts = [out / f"play-{p}-of-{a.parts}.json" for p in range(a.parts)]
    missing = [p.name for p in parts if not p.exists()]
    if missing:
        sys.exit(f"play parts missing: {', '.join(missing)}")
    L = [l for p in parts for l in json.loads(p.read_text(encoding="utf-8"))]
    rank = {k: i for i, k in enumerate(dict.fromkeys(l["kind"] for l in L))}
    L.sort(key=lambda l: (l["root"], rank[l["kind"]], l.get("r", 0)))
    roots = [{k: v for k, v in r.items() if k not in ("legal", "lpS", "lpW")} for r in R["roots"]]
    (out / "lines.json").write_text(json.dumps(dict(roots=roots, lines=L, bands=R["bands"], settings=R["settings"])),
                                    encoding="utf-8")
    print(f"wrote {out / 'lines.json'}: {len(L)} lines from {len(roots)} roots")


def positions(Ld):
    """Every position of every line, in order: its prompt end (character index) per line, a key (FEN and
    the move to it), whether Stockfish is needed there (every position of the contrast-A lines, the last
    of the others) and the Stockfish jobs (key, position before, move)."""
    roots = Ld["roots"]
    prev = []
    for r in roots:
        b = ev.board_of(parse_movetext(r["prompt"])[0])
        mv = b.pop()
        prev.append((b.fen(), mv.uci()))
    seqs, ends, keys, need, jobs, line_start = [], [], [], [], {}, [0]
    for l in Ld["lines"]:
        r = roots[l["root"]]
        b = chess.Board(r["fen"])
        p, pv, uci = r["prompt"], *prev[l["root"]]
        e, ks, js = [len(p) - 1], [r["fen"] + " " + uci], [(pv, uci)]
        for u in l["moves"]:
            mv = chess.Move.from_uci(u)
            san = b.san(mv)
            p += san + (" " if b.turn == chess.WHITE else f" {b.fullmove_number + 1}.")
            js.append((b.fen(), u))
            b.push(mv)
            e.append(len(p) - 1)
            ks.append(b.fen() + " " + u)
        nd = [True] * len(ks)
        for k, j, n in zip(ks, js, nd):
            if n:
                jobs.setdefault(k, (k, *j))
        seqs.append(encode(p))
        ends.append(e)
        keys += ks
        need += nd
        line_start.append(line_start[-1] + len(e))
    return seqs, ends, keys, np.array(need), jobs, line_start


def judge(a):
    """Stockfish (--depth) and the board facts on part --part of --parts of the positions that need them
    -> <run>/judge-<part>-of-<parts>.npz. A finished part is kept (a rerun skips it)."""
    out, _ = dirs(a)
    path = out / f"judge-{a.part}-of-{a.parts}.npz"
    if path.exists():
        print(f"{path} exists; skipping")
        return
    Ld = json.loads((out / "lines.json").read_text(encoding="utf-8"))
    jobs = positions(Ld)[4]
    todo = [jobs[k] for k in sorted(jobs)][a.part::a.parts]
    print(f"part {a.part + 1}/{a.parts}: {len(todo)} of {len(jobs)} positions, Stockfish depth {a.depth} and board facts, "
          f"{a.workers} workers", flush=True)
    res, t0 = {}, time.time()
    with Pool(a.workers, initializer=_eval_init, initargs=(a.depth,)) as pool:
        for d_, (key, cp, facts) in enumerate(pool.imap_unordered(_eval, todo, chunksize=16), 1):
            res[key] = (cp, facts)
            if d_ % 500 == 0 or d_ == len(todo):
                rate = d_ / (time.time() - t0)
                print(f"\r  {d_}/{len(todo)}, {rate:.0f}/s, {(len(todo) - d_) / max(rate, 1e-9) / 60:.0f} min left   ",
                      end="", flush=True)
    print()
    ks = sorted(res)
    np.savez(str(path) + ".tmp.npz", keys=np.array(ks), cp=np.array([np.nan if res[k][0] is None else res[k][0] for k in ks]),
             facts=np.array([res[k][1] for k in ks], dtype=bool).reshape(len(ks), len(ANCHORS)))
    os.replace(str(path) + ".tmp.npz", path)
    print(f"wrote {path}")


def judged(out, needed):
    """Stockfish results from the judge parts, {key: (cp, facts)}: the first complete set of parts."""
    found = {}
    for p in out.glob("judge-*-of-*.npz"):
        k, n = map(int, re.match(r"judge-(\d+)-of-(\d+)\.npz", p.name).groups())
        found.setdefault(n, {})[k] = p
    for n, ps in sorted(found.items()):
        if len(ps) == n:
            res = {}
            for p in ps.values():
                z = np.load(p)
                res.update({k: (None if np.isnan(c) else c, f) for k, c, f in zip(z["keys"].tolist(), z["cp"], z["facts"])})
            if needed <= set(res):
                return res
    sys.exit(f"no complete set of judge parts in {out} covers the positions: run judge")


def encode_stage(a):
    """Both models' states at every position, the crosscoder codes, the Stockfish results merged
    -> <run>/codes.npz, evals.npy, facts.npy, meta.json."""
    dev = ev.device(a.device)
    cc = load_cc(a.cc_run, a.cc, a.strong, dev)
    Ld = json.loads((cc.out / "lines.json").read_text(encoding="utf-8"))
    roots, L, bands = Ld["roots"], Ld["lines"], Ld["bands"]
    seqs, ends, keys, need, jobs, line_start = positions(Ld)
    res = judged(cc.out, set(jobs))
    npos = line_start[-1]
    pos_line = np.repeat(np.arange(len(L)), np.diff(line_start))
    pos_t = np.concatenate([np.arange(n) for n in np.diff(line_start)]).astype(np.int16)
    evals = np.full(npos, np.nan, dtype=np.float32)
    facts = np.zeros((npos, len(ANCHORS)), dtype=bool)
    for q in np.flatnonzero(need):
        cp, fa = res[keys[q]]
        facts[q] = fa
        if cp is not None:
            sign = 1 if pos_t[q] % 2 == 0 else -1                  # even plies: the root's side to move
            evals[q] = float(np.clip(sign * cp / 100, -MATE_PAWNS, MATE_PAWNS))
    models = {m: ev.load(cc.info["models"][m], dev)[0] for m in (0, 1)}
    print(f"states of both models at {npos} positions of {len(L)} lines, and the crosscoder", flush=True)
    st = {m: line_states(models[m], seqs, ends, cc.layer[m], dev, a.max_tokens) for m in (0, 1)}
    indptr, lat, val = [0], [], []
    # reconstruction error and L0 per (line kind, root band): off-distribution lines would reconstruct worse
    kinds = list(dict.fromkeys(l["kind"] for l in L))
    kind_of = np.array([kinds.index(L[q]["kind"]) for q in pos_line])
    band_of = np.array([bands.index(roots[L[q]["root"]]["band"]) for q in pos_line])
    grp = torch.from_numpy(kind_of * len(bands) + band_of).to(dev)
    G, S_ = len(kinds) * len(bands), len(cc.sources)
    err, sxx = torch.zeros((G, S_), device=dev), torch.zeros((G, S_), device=dev)
    sx = torch.zeros((G, S_, cc.ck["d"]), device=dev)
    cnt, l0 = torch.zeros(G, device=dev), torch.zeros(G, device=dev)
    with torch.no_grad():
        for i in range(0, npos, 4096):
            f, x = encode_states(cc, {m: st[m][i:i + 4096].to(dev) for m in (0, 1)})
            g = grp[i:i + 4096]
            err.index_add_(0, g, (cc.coder.decode(f) - x).pow(2).sum(2))
            sx.index_add_(0, g, x)
            sxx.index_add_(0, g, x.pow(2).sum(2))
            cnt.index_add_(0, g, torch.ones(len(g), device=dev))
            l0.index_add_(0, g, (f > 0).sum(1).float())
            nz = (f > 0).nonzero()                                   # row-major: rows in order
            indptr += (np.cumsum(np.bincount(nz[:, 0].cpu().numpy(), minlength=len(f))) + indptr[-1]).tolist()
            lat.append(nz[:, 1].int().cpu().numpy())
            val.append(f[nz[:, 0], nz[:, 1]].half().cpu().numpy())
    var = (sxx.sum(0) - sx.sum(0).pow(2).sum(1) / npos) / npos      # per source, pooled over every line position
    fvu = (err.sum(0) / npos / var).tolist()
    rel = (err / cnt[:, None].clamp_min(1) / var).cpu().numpy()     # each group's error over the pooled variance
    l0g = (l0 / cnt.clamp_min(1)).cpu().numpy()
    by = {}
    for gi in range(G):
        if cnt[gi] > 0:
            kind, band = kinds[gi // len(bands)], bands[gi % len(bands)]
            by.setdefault(kind, {})[band] = dict(positions=int(cnt[gi]), l0=float(l0g[gi]),
                                                 **{cc.info["names"][m]: float(rel[gi, k]) for k, (m, _) in enumerate(cc.sources)})
    np.savez(cc.out / "codes.npz", indptr=np.array(indptr, dtype=np.int64), lat=np.concatenate(lat), val=np.concatenate(val),
             line_start=np.array(line_start, dtype=np.int64), pos_line=pos_line, pos_t=pos_t)
    np.save(cc.out / "evals.npy", evals)
    np.save(cc.out / "facts.npy", facts)
    end = {kind: [evals[line_start[q + 1] - 1] for q, l in enumerate(L) if l["kind"] == kind] for kind in kinds}
    s = Ld["settings"]
    meta = dict(cc_run=str(cc.run), cc=cc.dir.name, S=cc.info["names"][cc.s], W=cc.info["names"][cc.w],
                plies=s["plies"], temperature=s["temperature"], depth=s["depth"],
                roots=len(roots), lines=len(L), positions=npos, held=s["held"], seed=s["seed"], latents=cc.ck["latents"],
                anchors=ANCHORS, fvu_lines={cc.info["names"][m]: fvu[k] for k, (m, _) in enumerate(cc.sources)}, fvu_by=by,
                bands=bands, mean_end_eval={kind: float(np.nanmean(v)) if v and not np.isnan(v).all() else None
                                            for kind, v in end.items()},
                stockfish_missing=int(np.isnan(evals[need]).sum()))
    (cc.out / "meta.json").write_text(json.dumps(meta, indent=1))
    print(lines_text(meta))
    print(f"wrote {cc.out}: codes.npz, evals.npy, facts.npy, meta.json")


def lines(a):
    """roots, play, gather, judge and encode in one process (on Modal they run as separate, sharded stages)."""
    roots_stage(a)
    a.part, a.parts = 0, 1
    play_stage(a)
    gather(a)
    judge(a)
    encode_stage(a)


def lines_text(meta):
    names = list(meta["fvu_lines"])
    out = ["## Lines", "", "Crosscoder FVU on the line positions (rollouts, which it never saw): "
           + ", ".join(f"{n} {v:.3f}" for n, v in meta["fvu_lines"].items()) + "."]
    ends = {k: v for k, v in meta["mean_end_eval"].items() if v is not None}
    if ends:
        out.append("Mean Stockfish evaluation at each line's end, pawns for the root's side to move (--depth > 0; S lines "
                   "should end better than W lines): " + ", ".join(f"{k} {v:+.2f}" for k, v in ends.items()) + ".")
    by = meta.get("fvu_by")
    if by:
        out += ["", "Reconstruction error by line and root band (squared error over the pooled variance, so the rows compare "
                    "directly; the crosscoder under-fires where it is high) and mean active latents:", "",
                "| line | root band | positions | " + " | ".join(f"error {n}" for n in names) + " | L0 |",
                "|---|---|---|" + "---|" * len(names) + "---|"]
        for kind, bs in by.items():
            for band, r in bs.items():
                out.append(f"| {kind} | {band} | {r['positions']} | " + " | ".join(f"{r[n]:.3f}" for n in names) + f" | {r['l0']:.1f} |")
        gap = [(band, n, by["S"][band][n] / max(by["W"][band][n], 1e-9)) for band in by.get("S", {}) if band in by.get("W", {})
               for n in names]
        bad = [f"{band} roots, {n}: S lines {g:.2f}x W lines' error" for band, n, g in gap if not 0.8 <= g <= 1.25]
        out += ["", "S vs W lines (flag outside 0.8-1.25x): " + ("; ".join(bad) + ": consider retraining the crosscoder with rollouts"
                                                              if bad else "within range")]
    return "\n".join(out)


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


def binom_tail(k, n):
    """P(X >= k) for X ~ Binomial(n, 1/2), elementwise (exact)."""
    k, n = np.asarray(k, dtype=np.int64), np.asarray(n, dtype=np.int64)
    out = np.ones(len(k))
    for m in np.unique(n):
        if m <= 0:
            continue
        j = torch.arange(m + 1, dtype=torch.float64)
        logpmf = torch.lgamma(torch.tensor(m + 1.0, dtype=torch.float64)) - torch.lgamma(j + 1) - torch.lgamma(m - j + 1) - m * math.log(2)
        tail = torch.flip(torch.cumsum(torch.flip(logpmf.exp(), [0]), 0), [0]).clamp(max=1).numpy()
        sel = n == m
        out[sel] = tail[np.clip(k[sel], 0, m)]
    return out


def sign_tests(lat, d, flip, fit_pair, active, a, nlat):
    """Filters 2 and 3 for every latent from the per-(pair, latent) differences (flip: +-1 per pair, the null;
    a flip keeps which pairs differ, so the null has the same conditioning on d != 0).
      2: exact two-sided sign test on the informative fit pairs (>= --min-pairs), BH at --fdr-nodes over
         the active latents tested
      3: one-sided sign test in filter 2's direction on the informative held-out pairs (>= --min-pairs-held),
         BH at --fdr-nodes over filter 2's survivors"""
    s = np.sign(d) * flip
    cnt = {}
    for nm, m in (("fit", fit_pair), ("held", ~fit_pair)):
        cnt[nm] = (np.bincount(lat[m & (s > 0)], minlength=nlat), np.bincount(lat[m & (s < 0)], minlength=nlat))
    (pf, ngf), (ph, ngh) = cnt["fit"], cnt["held"]
    nf, nh = pf + ngf, ph + ngh
    sf = np.where(pf >= ngf, 1, -1)
    kf, kh = np.maximum(pf, ngf), np.where(sf > 0, ph, ngh)
    p2, p3 = np.ones(nlat), np.ones(nlat)
    q2, q3 = np.ones(nlat), np.ones(nlat)
    t2 = np.flatnonzero(active & (nf >= a.min_pairs))
    p2[t2] = np.minimum(1, 2 * binom_tail(kf[t2], nf[t2]))
    q2[t2], ok2 = bh(p2[t2], a.fdr_nodes)
    f2 = np.zeros(nlat, bool)
    f2[t2[ok2]] = True
    t3 = np.flatnonzero(f2 & (nh >= a.min_pairs_held))
    p3[t3] = binom_tail(kh[t3], nh[t3])
    q3[t3], ok3 = bh(p3[t3], a.fdr_nodes)
    f3 = np.zeros(nlat, bool)
    f3[t3[ok3]] = True
    return f2, f3, dict(nf=nf, sf=sf, af=kf / np.maximum(nf, 1), p2=p2, q2=q2, nh=nh, ah=kh / np.maximum(nh, 1), p3=p3, q3=q3)


def latent_tests(D, fit_r, active, a, nlat, rng):
    """Filters 2 and 3 on D (roots x latents, sparse), and the null: each root's two sides swapped at random."""
    Dc = D.tocoo()
    rows, lat, d = Dc.row, Dc.col, Dc.data
    keep = np.abs(d) > 1e-9
    rows, lat, d = rows[keep], lat[keep], d[keep]
    f2, f3, st = sign_tests(lat, d, np.ones(len(d)), fit_r[rows], active, a, nlat)
    null = []
    for _ in range(a.null):
        n2, n3, _ = sign_tests(lat, d, rng.choice([-1.0, 1.0], D.shape[0])[rows], fit_r[rows], active, a, nlat)
        null.append((int(n2.sum()), int(n3.sum())))
    return f2, f3, st, (np.array(null) if null else np.zeros((1, 2)))


def nodes(a):
    """Latent nodes, from the rollouts alone. (1) Each latent's own S-vs-W difference: per root, d = its scaled
    activation averaged over S's rollouts minus over W's (plies after the root, --sum-plies); exact sign test on
    the fit roots (BH at --fdr-nodes over the active latents), confirmed one-sided on the held-out roots; null:
    each root's two sides swapped at random; control: the same on S against a second set of S rollouts. (2) The
    graph's nodes: the latents of the concepts that passed the margin filter (plans.json, when plans has run),
    then the latents S and W differ on, then the most common active ones, up to --max-nodes."""
    out, _ = dirs(a)
    meta, Ld, z, evals, facts = load_run(out)
    roots, L, T, nlat = Ld["roots"], Ld["lines"], meta["plies"], meta["latents"]
    by = rollouts_by(L)
    control = all((ri, "S2") in by for ri in range(len(roots)) if (ri, "S") in by)
    rr = np.array([ri for ri in range(len(roots)) if (ri, "S") in by and (ri, "W") in by and (not control or (ri, "S2") in by)])
    fit_root = np.array([not r["held"] for r in roots])
    fit_r = fit_root[rr]
    pos_root = np.array([L[q]["root"] for q in z["pos_line"]])
    fit_pos = fit_root[pos_root]
    rate = np.bincount(z["lat"][fit_pos[z["row"]]], minlength=nlat) / max(fit_pos.sum(), 1)
    active = (rate >= a.min_rate) & (rate <= a.max_rate)
    X, _, _ = rollout_sums(z, np.ones(nlat, bool), scales_of(z, nlat), T, nlat, "all" if a.sum_plies == "split" else a.sum_plies)
    mean = {}
    for kind in ("S", "W") + (("S2",) if control else ()):
        rows = [(q, g) for g, ri in enumerate(rr) for q in by[(ri, kind)]]
        mean[kind] = per_root(X[[q for q, _ in rows]], [g for _, g in rows], len(rr))
    rng = np.random.default_rng(a.seed)
    f2, f3, st, null = latent_tests((mean["S"] - mean["W"]).tocsr(), fit_r, active, a, nlat, rng)
    ctrl = None
    if control:
        c2, c3, _, _ = latent_tests((mean["S"] - mean["S2"]).tocsr(), fit_r, active, a, nlat, rng)
        ctrl = dict(decision=int(c2.sum()), held_out=int(c3.sum()), both=int((f3 & c3).sum()))
    in_plans = {}
    pj = out / "plans.json"
    if pj.exists():
        for p in json.loads(pj.read_text(encoding="utf-8"))["plans"]:
            if p["replicated"] and not p.get("control"):
                for f in p["features"]:
                    in_plans[f["latent"]] = in_plans.get(f["latent"], 0) + 1
    diffl = np.flatnonzero(f3)
    diffl = diffl[np.argsort(st["q3"][diffl])]
    common = np.flatnonzero(active)
    common = common[np.argsort(-rate[common])]
    order = list(dict.fromkeys([j for j, _ in sorted(in_plans.items(), key=lambda x: -x[1])] + diffl.tolist() + common.tolist()))
    order = order[:a.max_nodes]
    excl = out / "exclusivity.npz"
    if excl.exists():
        r, status = np.load(excl)["r"], np.load(excl)["status"]
    else:
        r, status = load_cc(a.cc_run, a.cc, a.strong, "cpu").r, np.zeros(nlat, np.int8)
    ex = explanations(meta)
    n_fit = max(int(fit_r.sum()), 1)
    lat_nodes = []
    for j in order:
        n = dict(kind="latent", id=int(j), r=float(r[j]), tag=tag(r[j]), exclusive=EXCL[int(status[j])], rate=float(rate[j]),
                 plans=int(in_plans.get(j, 0)), coverage=float(st["nf"][j] / n_fit), more_in="S" if st["sf"][j] > 0 else "W",
                 sep_fit=float(st["af"][j]), n_fit=int(st["nf"][j]), q_fit=float(st["q2"][j]),
                 sep_held=float(st["ah"][j]), n_held=int(st["nh"][j]), q_held=float(st["q3"][j]), differs=bool(f3[j]))
        n["label"] = label(n, ex)
        lat_nodes.append(n)
    frate = facts[fit_pos].mean(0)
    anchors = [dict(kind="fact", id=k, name=n, rate=float(frate[k])) for k, n in enumerate(ANCHORS) if 0.01 <= frate[k] <= 0.99]
    for n in anchors:
        n["label"] = label(n, ex)
    funnel = dict(latents=nlat, active=int(active.sum()), decision=int(f2.sum()), held_out=int(f3.sum()), kept=len(order),
                  from_plans=sum(1 for j in order if j in in_plans), null_decision_mean=float(null[:, 0].mean()),
                  null_held_out_mean=float(null[:, 1].mean()), null_held_out_max=int(null[:, 1].max()), null_runs=a.null,
                  control=ctrl)
    rec = dict(funnel=funnel, roots=dict(all=len(rr), fit=int(fit_r.sum()), held=int((~fit_r).sum())),
               settings={k: getattr(a, k) for k in ("min_rate", "max_rate", "min_pairs", "min_pairs_held", "fdr_nodes",
                                                    "max_nodes", "null", "seed", "sum_plies")},
               tags={t: sum(n["tag"] == t for n in lat_nodes) for t in ("S-only", "W-only", "shared", "leaning S", "leaning W")},
               latents=lat_nodes, anchors=anchors)
    (out / "nodes.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
    print(nodes_text(rec))
    print(f"wrote {out / 'nodes.json'}")


def nodes_text(rec):
    f, s = rec["funnel"], rec["settings"]
    out = ["## Latents: S's rollouts against W's", "",
           f"{rec['roots']['all']} roots ({rec['roots']['fit']} fit, {rec['roots']['held']} held out). Per root and latent, "
           f"d = its activation averaged over S's rollouts minus over W's (plies: {s['sum_plies']}); a root counts for a "
           "latent when d != 0.", "",
           "| filter | latents | with S and W swapped at random (mean of %d) |" % f["null_runs"]
           + (" control: S against S |" if f.get("control") else ""), "|---|---|---|" + ("---|" if f.get("control") else ""),
           f"| all | {f['latents']} | |" + (" |" if f.get("control") else ""),
           f"| active on {s['min_rate']:.0%}-{s['max_rate']:.0%} of positions | {f['active']} | {f['active']} |"
           + (f" {f['active']} |" if f.get("control") else ""),
           f"| S and W differ: sign test on >= {s['min_pairs']} fit roots, BH at {s['fdr_nodes']} | {f['decision']} | "
           f"{f['null_decision_mean']:.1f} |" + (f" {f['control']['decision']} |" if f.get("control") else ""),
           f"| ... confirmed on >= {s['min_pairs_held']} held-out roots, BH at {s['fdr_nodes']} | {f['held_out']} | "
           f"{f['null_held_out_mean']:.1f} (max {f['null_held_out_max']}) |" + (f" {f['control']['held_out']} |" if f.get("control") else ""), ""]
    if f.get("control"):
        out += [f"Control: {f['control']['held_out']} latents separate S's rollouts from a second set of S's (sampling noise the "
                f"test lets through); {f['control']['both']} of the {f['held_out']} S-vs-W latents are among them.", ""]
    out += [f"Graph nodes: {f['kept']} latents ({f['from_plans']} from concepts that passed the margin filter, then the latents "
            "S and W differ on, then the most common), by tag: " + ", ".join(f"{t} {n}" for t, n in rec["tags"].items())
            + f"; {len(rec['anchors'])} board facts as anchors."]
    if f["held_out"] and f["null_held_out_mean"] > 0.2 * f["held_out"]:
        out += ["", f"**Warning**: the null passes {f['null_held_out_mean']:.0f} latents against {f['held_out']} real: thresholds too loose."]
    rows = sorted((n for n in rec["latents"] if n["differs"]), key=lambda n: n["q_held"])[:40]
    if rows:
        out += ["", "Latents S's and W's rollouts differ on most reliably:", "",
                "| latent | tag (exclusivity check) | more in | coverage | fit roots agreeing (q) | held-out (q) | in concepts | rate | explanation |",
                "|---|---|---|---|---|---|---|---|---|"]
        for n in rows:
            out.append(f"| {n['id']} | {n['tag']}{'' if n['tag'] == 'shared' else ' (' + n['exclusive'] + ')'} | {n['more_in']} | "
                       f"{n['coverage']:.0%} | {n['sep_fit']:.0%} of {n['n_fit']} ({n['q_fit']:.2g}) | "
                       f"{n['sep_held']:.0%} of {n['n_held']} ({n['q_held']:.2g}) | {n['plans']} | {n['rate']:.1%} | "
                       f"{n['label'].split(': ', 1)[-1]} |")
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
    (root, t), t + k <= T (every ply: the models write both colours' moves) -> n (B,), n_A (B, N), n_B (B, N),
    n_AB (B, N, N)."""
    T = A.shape[1] - 1
    n = nA = nB = nAB = 0
    for t in range(0, T - k + 1):
        m = A[:, t + k, -1]                                          # the last column: the position exists
        X, Y = A[:, t] * m[:, None], A[:, t + k]
        n = n + w @ m
        nA, nB = nA + w @ X, nB + w @ Y
        nAB = nAB + torch.einsum("br,rn,rm->bnm", w, X, Y)
    return n, nA, nB, nAB


def loglift(n, nA, nB, nAB, prior):
    return torch.log((nAB + prior) / (nA[:, :, None] * nB[:, None, :] / n[:, None, None].clamp_min(1) + prior))


def moments(acc, x):
    acc[0] += x.sum(0)
    acc[1] += (x * x).sum(0)


def sd_of(acc, B):
    return ((acc[1] / B - (acc[0] / B) ** 2).clamp_min(0) * B / max(B - 1, 1)).sqrt()


def diff_edges(AS, AW, lags, a, dev, groups=None):
    """Edge statistics for both graphs at each lag, point estimates and Poisson-bootstrap sds. groups: each row's
    root (rows are rollout pairs), so the bootstrap resamples roots."""
    R = AS.shape[0]
    G = R if groups is None else int(groups.max()) + 1
    gi = None if groups is None else torch.from_numpy(np.asarray(groups)).to(dev)
    g = torch.Generator(device="cpu").manual_seed(a.seed)
    one = torch.ones((1, R), device=dev)
    out = {}
    for k in lags:
        cS, cW = lag_counts(AS, k, one), lag_counts(AW, k, one)
        e = dict(lS=loglift(*cS, a.prior)[0], lW=loglift(*cW, a.prior)[0], nS=cS[3][0], nW=cW[3][0], aS=cS[1][0], aW=cW[1][0])
        acc = {x: [0, 0] for x in ("lS", "lW", "D")}
        for b0 in range(0, a.boot, a.boot_chunk):
            w = torch.poisson(torch.ones((min(a.boot_chunk, a.boot - b0), G)), generator=g).to(dev)
            if gi is not None:
                w = w[:, gi]
            lS, lW = loglift(*lag_counts(AS, k, w), a.prior), loglift(*lag_counts(AW, k, w), a.prior)
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
            rows.append(dict(lag=int(k), family="even" if k % 2 == 0 else "odd", src=int(i), dst=int(j),
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
    """(R, M) completions per root (the chain's nodes active at t, t + 2, ..., any t) and (R, M) starts
    (its first node active at a t with room for the rest)."""
    T = A.shape[1] - 1
    K = torch.zeros((A.shape[0], len(motifs)), device=dev)
    St = torch.zeros_like(K)
    for c0 in range(0, len(motifs), chunk):
        part = motifs[c0:c0 + chunk]
        for n in sorted({len(c) for c in part}):
            cols = [c0 + q for q, c in enumerate(part) if len(c) == n]
            ids = torch.tensor([motifs[q] for q in cols], device=dev)
            for t in range(0, T - 2 * (n - 1) + 1):
                prod = A[:, t, ids[:, 0]]
                St[:, cols] += prod
                for j in range(1, n):
                    prod = prod * A[:, t + 2 * j, ids[:, j]]
                K[:, cols] += prod
    return K, St


def motif_stats(KS, KW, StS, StW, band, a):
    """Per motif: completions in the S and W lines, and an exact paired test on the roots (McNemar): b = roots
    where it completes in the S line and not the W line, c the reverse, two-sided sign test of b against
    b + c, BH at --fdr over the motifs with b + c >= --min-discordant (fewer can't reach significance).
    Roots, not completions, are the unit: a root's completions are not independent. b and c per root band."""
    cS, cW = (KS > 0).cpu().numpy(), (KW > 0).cpu().numpy()
    b, c = (cS & ~cW).sum(0), (~cS & cW).sum(0)
    p = np.minimum(1, 2 * binom_tail(np.maximum(b, c), b + c))
    tested = b + c >= a.min_discordant
    q, sig = np.ones(len(p)), np.zeros(len(p), bool)
    q[tested], sig[tested] = bh(p[tested], a.fdr)
    tS, tW = KS.sum(0).cpu().numpy(), KW.sum(0).cpu().numpy()
    bands = {n: ((cS & ~cW)[band == n].sum(0), (~cS & cW)[band == n].sum(0)) for n in sorted(set(band))}
    return dict(tS=tS, tW=tW, lr=np.log((tS + 1) / (tW + 1)), b=b, c=c, p=p, q=q, sig=sig, tested=tested,
                startS=StS.sum(0).cpu().numpy(), startW=StW.sum(0).cpu().numpy(), bands=bands)


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
    by = rollouts_by(L)
    use = [ri for ri, r in enumerate(roots) if r["held"] == (a.split == "held") and (ri, "S") in by and (ri, "W") in by]
    rp = [(by[(ri, "S")][k], by[(ri, "W")][k], u) for u, ri in enumerate(use)
          for k in range(min(len(by[(ri, "S")]), len(by[(ri, "W")])))]                 # rollout pairs: S's k-th, W's k-th
    S_ids, W_ids, grp = [x[0] for x in rp], [x[1] for x in rp], np.array([x[2] for x in rp])
    AS = activity(z, facts, nodes, S_ids, T, meta["latents"])
    AW = activity(z, facts, nodes, W_ids, T, meta["latents"])
    # the W line's worst move by W (even plies: W to move), by Stockfish
    drop = np.full(len(W_ids), np.nan)
    for r, q in enumerate(W_ids):
        e = evals[z["line_start"][q]:z["line_start"][q + 1]]
        d = [e[t] - e[t + 1] for t in range(0, len(e) - 1, 2) if not (np.isnan(e[t]) or np.isnan(e[t + 1]))]
        drop[r] = max(d) if d else np.nan
    if not a.engine_split or np.isnan(drop).all():              # one set of roots, unless asked to split by the engine
        sets = dict(all=np.arange(len(W_ids)))
    else:
        sets = dict(positional=np.flatnonzero(drop <= a.blunder), tactical=np.flatnonzero(drop > a.blunder))
    print(f"{len(use)} {a.split} roots, {len(W_ids)} rollout pairs ({', '.join(f'{k} {len(v)}' for k, v in sets.items())}); "
          f"{len(nodes)} nodes", flush=True)
    res.mkdir(parents=True, exist_ok=True)
    report, cards = [], {}
    for sname, ix in sets.items():
        if len(ix) < a.min_roots:
            report.append(f"## {sname} roots: only {len(ix)}, skipped (--min-roots {a.min_roots})")
            continue
        print(f"{sname}: edges at lags {PLAN + RESPONSE}, {a.boot} bootstraps", flush=True)
        tS, tW = torch.from_numpy(AS[ix]).to(dev), torch.from_numpy(AW[ix]).to(dev)
        uniq, inv = np.unique(grp[ix], return_inverse=True)                      # rows -> roots
        E = diff_edges(tS, tW, sorted(k for k in PLAN + RESPONSE if k <= T), a, dev, groups=inv)
        for e in E.values():                                     # drop the "position exists" column
            for k_ in e:
                e[k_] = e[k_][:len(nodes)] if e[k_].ndim == 1 else e[k_][:len(nodes), :len(nodes)]
        rows = categorise(E, nodes, a)
        with open(res / f"edges-{sname}-{a.split}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["lag", "family", "category", "src", "dst", "lift_S", "lift_W", "delta", "z", "p", "q", "n_S", "n_W",
                        "src_label", "dst_label"])
            for r in sorted((r for r in rows if r["category"] != "shared"), key=lambda r: r["p"]):   # significant only
                w.writerow([r["lag"], r["family"], r["category"], r["src"], r["dst"], f"{r['lift_S']:.3f}", f"{r['lift_W']:.3f}",
                            f"{r['delta']:.3f}", f"{r['z']:.2f}", f"{r['p']:.3g}", f"{r['q']:.3g}", r["n_S"], r["n_W"],
                            nodes[r["src"]]["label"], nodes[r["dst"]]["label"]])
        motifs = chains(E[2], a)
        print(f"  {len(rows)} edges tested; {len(motifs)} motif candidates", flush=True)
        gt = torch.from_numpy(inv).to(dev)
        by_root = lambda K: torch.zeros((len(uniq), K.shape[1]), device=dev).index_add_(0, gt, K)   # a root's rollouts summed
        KS, StS = (by_root(x) for x in completions(tS, motifs, dev))
        KW, StW = (by_root(x) for x in completions(tW, motifs, dev))
        root_ids = [use[u] for u in uniq]
        ms = motif_stats(KS, KW, StS, StW, np.array([roots[ri]["band"] for ri in root_ids]), a)
        with open(res / f"motifs-{sname}-{a.split}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            bn = list(ms["bands"])
            w.writerow(["motif", "log_ratio", "p", "q", "completions_S", "completions_W", "roots_S_not_W", "roots_W_not_S",
                        *[f"{x}_{n}" for n in bn for x in ("S_not_W", "W_not_S")], "follow_S", "follow_W", "labels"])
            for m in np.argsort(ms["p"]):
                w.writerow([" > ".join(map(str, motifs[m])), f"{ms['lr'][m]:.3f}", f"{ms['p'][m]:.3g}", f"{ms['q'][m]:.3g}",
                            int(ms["tS"][m]), int(ms["tW"][m]), int(ms["b"][m]), int(ms["c"][m]),
                            *[int(ms["bands"][n][x][m]) for n in bn for x in (0, 1)],
                            f"{ms['tS'][m] / max(ms['startS'][m], 1):.3f}", f"{ms['tW'][m] / max(ms['startW'][m], 1):.3f}",
                            " > ".join(nodes[x]["label"] for x in motifs[m])])
        nb = {n: int(v) for n, v in zip(*np.unique([roots[ri]["band"] for ri in root_ids], return_counts=True))}
        report.append(graph_text(sname, a, f"{len(root_ids)}, {len(ix)} rollout pairs: "
                                 + ", ".join(f"{v} from {n} games" for n, v in nb.items()),
                                 rows, motifs, ms, nodes, attach(E[2], nodes, tS, tW, a)))
        cards[sname] = prototypes(motifs, ms, KS, KW, root_ids, Ld, by, evals, z, nodes, a)
    health_p, recall_p = res / "health.json", res / "recall.json"
    head = [f"# Concept-graph diff, pilot first pass: {name} ({a.split} roots)", "",
            f"S = {meta['S']}, W = {meta['W']}; crosscoder {meta['cc']} of {Path(meta['cc_run']).name}; {meta['roots']} roots, "
            f"{meta['plies']} plies per line at temperature {meta['temperature']}, Stockfish depth {meta['depth']}.", ""]
    head.append(health_text(json.loads(health_p.read_text())) if health_p.exists() else "## Gate 1: not run (graphdiff.py health)")
    head += ["", recall_text(json.loads(recall_p.read_text())) if recall_p.exists() else "## Gate 2: not run (graphdiff.py recall)", ""]
    head += [lines_text(meta), ""]
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
           "", "| lags | | S-only | W-only | reweighted | not significant |", "|---|---|---|---|---|---|"]
    for fam, lags in (("even", PLAN), ("odd", RESPONSE)):
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
            f"{len(motifs)} candidate chains of lag-2 edges, {int(ms['tested'].sum())} with >= {a.min_discordant} roots "
            f"where they complete in one line and not the other (tested, exact paired test); {len(sig)} differ at FDR {a.fdr} "
            f"({int((ms['lr'][sig] > 0).sum())} more in S's lines, {int((ms['lr'][sig] < 0).sum())} more in W's). "
            "follow = completions per time the first node fires with room for the chain."]
    for title, order in (("more in S's lines", sig[np.argsort(-ms["lr"][sig])]), ("more in W's lines", sig[np.argsort(ms["lr"][sig])])):
        order = [m for m in order if (ms["lr"][m] > 0) == (title.endswith("S's lines"))][:a.show]
        if not order:
            continue
        bn = list(ms["bands"])
        out += ["", f"Top {len(order)} {title}:", "",
                "| # | chain | completions S / W | roots: S not W / W not S | " + " | ".join(f"{n} roots" for n in bn)
                + " | follow S / W | log ratio | q |", "|---|---|---|---|" + "---|" * len(bn) + "---|---|---|"]
        for rank, m in enumerate(order, 1):
            out.append(f"| {rank} | {' &rarr; '.join(lab(x) for x in motifs[m])} | {int(ms['tS'][m])} / {int(ms['tW'][m])} | "
                       f"{int(ms['b'][m])} / {int(ms['c'][m])} | "
                       + " | ".join(f"{int(ms['bands'][n][0][m])} / {int(ms['bands'][n][1][m])}" for n in bn)
                       + f" | {ms['tS'][m] / max(ms['startS'][m], 1):.2f} / {ms['tW'][m] / max(ms['startW'][m], 1):.2f} | "
                       f"{ms['lr'][m]:+.2f} | {ms['q'][m]:.2g} |")
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
                q = by[(ri, kind)][0]                                   # its first rollout pair
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


# ---------------------------------------------------------------- plan templates

def scales_of(z, nlat):
    """Each latent's mean activation where it fires, over every line position: templates weigh latents on one scale."""
    cnt = np.bincount(z["lat"], minlength=nlat)
    tot = np.bincount(z["lat"], weights=z["val"].astype(np.float64), minlength=nlat)
    return (tot / np.maximum(cnt, 1)).clip(min=1e-6)


def line_matrix(z, keep, scale, T, nlat):
    """(lines, (T + 1) * latents) sparse: each line's normalised activations, column t * latents + j."""
    from scipy import sparse
    rows = z["row"]
    m = keep[z["lat"]]
    cols = z["pos_t"][rows][m].astype(np.int64) * nlat + z["lat"][m]
    vals = z["val"][m].astype(np.float64) / scale[z["lat"][m]]
    return sparse.csr_matrix((vals, (z["pos_line"][rows][m], cols)), shape=(len(z["line_start"]) - 1, (T + 1) * nlat))


def maxmin(job):
    """Schut et al.'s max-min LP, w >= 0 (or signed, w = w+ - w-, with signed=True):
        max m - C sum(xi)   s.t.   D w + xi >= m,   sum(w) <= 1,   w, xi >= 0
    nu = 0: the hard margin (xi = 0); nu > 0: C = 1 / (nu n), at most a share nu of the rows inside the
    margin. Dual simplex, so the answer is a vertex: sparse. -> key, (columns, weights, m, share separated)."""
    from scipy import sparse
    from scipy.optimize import linprog
    key, D, cols, nu, signed = job
    n, k = D.shape
    kk = 2 * k if signed else k
    ns = n if nu > 0 else 0
    c = np.zeros(kk + 1 + ns)
    c[kk] = -1.0
    if ns:
        c[kk + 1:] = 1.0 / (nu * n)
    top = ([-D, D] if signed else [-D]) + [sparse.csr_matrix(np.ones((n, 1)))] + ([-sparse.identity(n, format="csr")] if ns else [])
    bot = sparse.hstack([sparse.csr_matrix(np.ones((1, kk))), sparse.csr_matrix((1, 1 + ns))])
    A = sparse.vstack([sparse.hstack(top), bot]).tocsr()
    b = np.zeros(n + 1)
    b[-1] = 1.0
    r = linprog(c, A_ub=A, b_ub=b, bounds=[(0, None)] * kk + [(None, None)] + [(0, None)] * ns, method="highs-ds")
    if r.status != 0:
        return key, None
    w = r.x[:k] - r.x[k:2 * k] if signed else r.x[:k]
    nz = np.abs(w) > 1e-9
    return key, (cols[nz], w[nz], float(r.x[kk]), float(np.mean(D @ w > 0)))


def kmeans(X, K, seed, iters=25):
    """Cosine k-means on the rows of X (dense torch) -> cluster of each row, and the unit centroids."""
    X = X / X.norm(dim=1, keepdim=True).clamp_min(1e-9)
    g = torch.Generator(device="cpu").manual_seed(seed)
    cent = X[torch.randperm(len(X), generator=g)[:K].to(X.device)].clone()
    for _ in range(iters):
        lab = (X @ cent.T).argmax(1)
        for k in range(K):
            m = lab == k
            if m.any():
                c = X[m].sum(0)
                cent[k] = c / c.norm().clamp_min(1e-9)
    return lab.cpu().numpy(), cent


def template_vector(cols, w, ncols):
    from scipy import sparse
    return sparse.csr_matrix((w / np.abs(w).sum(), (np.zeros(len(cols), dtype=np.int64), cols)), shape=(1, ncols))


def dedupe(temps, ncols, tau, prune=0.05):
    """Greedy grouping (best templates first): a template joins the first group whose first member it matches
    at cosine >= tau. A group's template is its members' mean, weights below `prune` x the largest dropped,
    L1 = 1. -> [(columns, weights, member indices)]."""
    from scipy import sparse
    if not temps:
        return []
    M = sparse.vstack([template_vector(t["cols"], t["w"], ncols) for t in temps]).tocsr()
    U = sparse.diags(1 / np.sqrt(np.asarray(M.multiply(M).sum(1)).ravel().clip(min=1e-18))) @ M
    sim = (U @ U.T).tocsr()
    order = sorted(range(len(temps)), key=lambda i: (-temps[i]["sep"], -temps[i]["m"]))
    reps, groups = [], []
    for i in order:
        row = sim.getrow(i).toarray().ravel()[reps] if reps else np.zeros(0)
        if len(row) and row.max() >= tau:
            groups[int(row.argmax())].append(i)
        else:
            reps.append(i)
            groups.append([i])
    out = []
    for g in groups:
        v = np.asarray(M[g].mean(0)).ravel()
        keep = np.abs(v) >= prune * np.abs(v).max()
        cols = np.flatnonzero(keep)
        out.append((cols, v[cols] / np.abs(v[cols]).sum(), g))
    return out


def weights_matrix(templates, ncols, shift=0, nlat=1):
    """(columns, templates) sparse signed weights, each template's plies shifted by `shift` (dropped if outside)."""
    from scipy import sparse
    r, c, v = [], [], []
    for g, (cols, w) in enumerate(templates):
        cs = cols + shift * nlat
        ok = (cs >= 0) & (cs < ncols)
        if ok.all():
            r.append(cs)
            c.append(np.full(len(cs), g))
            v.append(w)
    if not r:
        return sparse.csr_matrix((ncols, len(templates)))
    return sparse.csr_matrix((np.concatenate(v), (np.concatenate(r), np.concatenate(c))), shape=(ncols, len(templates)))


def sign_counts(D, Wm, chunk=4096):
    """For each template column: pairs where D w > 0 and where D w < 0."""
    from scipy import sparse
    pos, neg = [], []
    for i in range(0, Wm.shape[1], chunk):
        s = D @ Wm[:, i:i + chunk]
        s = s.toarray() if sparse.issparse(s) else np.asarray(s)
        pos.append((s > 1e-9).sum(0))
        neg.append((s < -1e-9).sum(0))
    return np.concatenate(pos), np.concatenate(neg)


def null_templates(templates, rate_bin, bins, rng, n, nlat):
    """For each template, n random templates with its plies, signs and weights, each latent replaced by a
    random other candidate latent with a similar firing rate (the same rate decile; never the template's own)."""
    out = []
    for cols, w in templates:
        t, j = cols // nlat, cols % nlat
        own = set(j.tolist())
        pool = {x: [y for y in bins[rate_bin[x]] if y not in own] or list(bins[rate_bin[x]]) for x in set(j.tolist())}
        for _ in range(n):
            jj = np.array([pool[x][rng.integers(len(pool[x]))] for x in j])
            cc_ = t * nlat + jj
            u, first = np.unique(cc_, return_index=True)
            out.append((u, w[first]))
    return out


def mcnemar(xS, xW):
    """Paired exact test over roots: b = executed in the S line and not the W line, c the reverse. -> b, c, p."""
    b, c = (xS & ~xW).sum(0), (~xS & xW).sum(0)
    return b, c, np.minimum(1, 2 * binom_tail(np.maximum(b, c), b + c))


def describe_plan(cols, w, nlat, ex, most=16):
    """A template in words: its heaviest features, ply by ply (even plies: the root's side to move)."""
    items = sorted(sorted(zip(cols // nlat, cols % nlat, w), key=lambda x: -abs(x[2]))[:most], key=lambda x: x[0])
    parts = []
    for t, j, v in items:
        e = ex.get(int(j))
        what = e["explanation"] if e and e.get("status") in ("explained", "weak") else f"latent {j}"
        parts.append(dict(ply=int(t), latent=int(j), weight=float(v), text=what,
                          role="pursued" if v > 0 else "avoided"))
    return parts


def rollouts_by(L):
    """{(root, kind): [line ids]}, the rollouts in order."""
    by = {}
    for q, l in enumerate(L):
        by.setdefault((l["root"], l["kind"]), []).append(q)
    return by


def per_root(X, groups, n):
    """The mean of X's rows (sparse) per group: groups[i] in 0..n-1 is row i's root."""
    from scipy import sparse
    groups = np.asarray(groups)
    cnt = np.bincount(groups, minlength=n).clip(min=1)
    M = sparse.csr_matrix((1.0 / cnt[groups], (groups, np.arange(len(groups)))), shape=(n, len(groups)))
    return (M @ X).tocsr()


def rollout_sums(z, keep, scale, T, nlat, plies):
    """(lines, F) sparse: each rollout's scaled latents averaged over the plies it counts (after the root, which both
    models share; --sum-plies all, own or split), so a rollout that ends early isn't smaller; and C, the same per ply."""
    from scipy import sparse
    C = line_matrix(z, keep, scale, T, nlat)
    nf = 2 if plies == "split" else 1
    t_, j_ = np.repeat(np.arange(T + 1), nlat), np.tile(np.arange(nlat), T + 1)
    on = (t_ >= 1) & ((t_ % 2 == 0) if plies == "own" else True)
    Pm = sparse.csr_matrix((np.ones(on.sum()), (np.flatnonzero(on), (t_[on] % 2) * nlat * (nf - 1) + j_[on])),
                           shape=(C.shape[1], nf * nlat))
    n = np.diff(z["line_start"]) - 1                                    # plies after the root
    n = n // 2 if plies == "own" else n
    X = sparse.diags(1.0 / np.maximum(n, 1)) @ (C @ Pm)
    return X.tocsr(), C, nf


def local_margins(D, Wm, sign, masks, nu, chunk=2048):
    """Per template column c: the share-nu quantile of sign_c * (D w_c) over the rows masks[c] picks (its own
    clusters' roots), -inf when it has none; and the share of those rows above 0."""
    from scipy import sparse
    m, share = np.full(Wm.shape[1], -np.inf), np.zeros(Wm.shape[1])
    for i in range(0, Wm.shape[1], chunk):
        s = D @ Wm[:, i:i + chunk]
        s = (s.toarray() if sparse.issparse(s) else np.asarray(s)) * sign[i:i + chunk][None, :]
        for k in range(s.shape[1]):
            rows = masks[i + k]
            if rows.any():
                m[i + k] = np.quantile(s[rows, k], nu)
                share[i + k] = (s[rows, k] > 1e-9).mean()
    return m, share


def discover(D, psplit, keep, rate, nlat, F, a, dev, tag_=""):
    """Fit, merge and filter concepts on D (roots x features): the max-min LP per cluster of roots whose
    differences look alike, once per side (v >= 0 on D and on -D); concepts matching at cosine >= --dedupe
    merged; then the margin filter on the selection and the replication roots, each concept scored on the roots
    of its own clusters (held-out roots join their nearest cluster centroid), against rate-matched random
    concepts scored on the same roots."""
    fit_rows = np.flatnonzero(psplit == 0)
    Xd = torch.from_numpy(D.toarray()).float().to(dev)
    lab, cent = kmeans(Xd[torch.from_numpy(fit_rows).to(dev)], max(1, round(len(fit_rows) / a.cluster_size)), a.seed)
    assign = (Xd / Xd.norm(dim=1, keepdim=True).clamp_min(1e-9) @ cent.T).argmax(1).cpu().numpy()
    assign[fit_rows] = lab
    del Xd
    jobs = []
    for sign_ in (1, -1):
        for k in range(len(cent)):
            rows = fit_rows[lab == k]
            if len(rows) < 2:
                continue
            Dr = D[rows] * sign_
            cols = np.unique(Dr.indices)
            if len(cols):
                jobs.append((("cluster", k, sign_), Dr[:, cols].tocsc().tocsr(), cols, a.nu, False))
    print(f"  {tag_}fitting {len(jobs)} LPs ({len(cent)} clusters x S's and W's concepts), {a.workers} workers", flush=True)
    temps, t0 = [], time.time()
    with Pool(a.workers) as pool:
        for d_, (key, r) in enumerate(pool.imap_unordered(maxmin, jobs, chunksize=4), 1):
            if r is not None and r[2] > 1e-9 and len(r[0]):
                temps.append(dict(key=key, sign=key[2], cols=r[0], w=r[1], m=r[2], sep=r[3]))
            if d_ % 50 == 0 or d_ == len(jobs):
                print(f"\r  {d_}/{len(jobs)} LPs, {len(temps)} concepts with a positive margin, {time.time() - t0:.0f}s",
                      end="", flush=True)
    print()
    templates, sign, groups = [], [], []
    for s_ in (1, -1):
        mine = [t for t in temps if t["sign"] == s_]
        for cols, w, members in dedupe(mine, F, a.dedupe):
            templates.append((cols, w))
            sign.append(s_)
            groups.append([mine[i] for i in members])
    sign = np.array(sign, dtype=np.int64)
    out = dict(templates=templates, sign=sign, groups=groups, temps=temps, lps=len(jobs), assign=assign, clusters=len(cent))
    if not templates:
        out.update(stats={}, selected=np.zeros(0, bool), replicated=np.zeros(0, bool), nulls=[], masks={})
        return out
    own = [np.array(sorted({t["key"][1] for t in g})) for g in groups]   # each concept's clusters
    Wm = weights_matrix(templates, F)
    cand = np.flatnonzero(keep)
    rb = np.zeros(nlat, dtype=np.int64)
    rb[cand] = np.searchsorted(np.quantile(rate[cand], np.linspace(0, 1, 11)[1:-1]), rate[cand])
    bins = {b: cand[rb[cand] == b] for b in np.unique(rb[cand])}
    nulls = null_templates(templates, rb, bins, np.random.default_rng(a.seed), a.null_templates, nlat)
    Wn = weights_matrix(nulls, F)
    nsign = np.repeat(sign, a.null_templates)
    stats, masks = {}, {}
    for nm, s_ in (("select", 1), ("replicate", 2)):
        rows = np.flatnonzero(psplit == s_)
        mk = [np.isin(assign[rows], o) if a.local else np.ones(len(rows), bool) for o in own]
        m, share = local_margins(D[rows], Wm, sign, mk, a.nu)
        mn, _ = local_margins(D[rows], Wn, nsign, [x for x in mk for _ in range(a.null_templates)], a.nu)
        mn = mn.reshape(len(templates), a.null_templates)
        n95 = np.quantile(mn, 0.95, axis=1)
        used = np.array([x.sum() for x in mk])
        stats[nm] = dict(roots=len(rows), margin=m, share=share, null95=n95, used=used,
                         passed=(m > 0) & (m > n95) & (used >= a.min_concept_roots), null_pos=float((mn > 0).mean()))
        masks[nm] = (rows, mk)
    out.update(stats=stats, selected=stats["select"]["passed"], nulls=nulls, masks=masks,
               replicated=stats["select"]["passed"] & stats["replicate"]["passed"])
    return out


def plans(a):
    from scipy import sparse
    dev = ev.device(a.device)
    out, res = dirs(a)
    meta, Ld, z, evals, facts = load_run(out)
    roots, L, T, nlat = Ld["roots"], Ld["lines"], meta["plies"], meta["latents"]
    ex = explanations(meta)
    # three splits by game: fit the concepts, select them, replicate them
    split = np.array([0 if not r["held"] else 1 + zlib.crc32(f"{r['band']}/{r['game']}/select".encode()) % 2 for r in roots])
    pos_root = np.array([L[q]["root"] for q in z["pos_line"]])
    fit_pos = split[pos_root] == 0
    rate = np.bincount(z["lat"][fit_pos[z["row"]]], minlength=nlat) / max(fit_pos.sum(), 1)
    keep = (rate >= a.min_rate) & (rate <= a.max_rate)
    X, C, nf = rollout_sums(z, keep, scales_of(z, nlat), T, nlat, a.sum_plies)
    F = nf * nlat
    by = rollouts_by(L)
    control = all((ri, "S2") in by for ri in range(len(roots)) if (ri, "S") in by)
    rr = np.array([ri for ri in range(len(roots)) if (ri, "S") in by and (ri, "W") in by and (not control or (ri, "S2") in by)])
    mean = {}
    for kind in ("S", "W") + (("S2",) if control else ()):
        rows = [(q, g) for g, ri in enumerate(rr) for q in by[(ri, kind)]]
        mean[kind] = per_root(X[[q for q, _ in rows]], [g for _, g in rows], len(rr))
    D = (mean["S"] - mean["W"]).tocsr()                                # per root: S's rollouts minus W's
    psplit = split[rr]
    zero = np.asarray(abs(D).sum(1)).ravel() == 0                      # identical rollouts (greedy): nothing to separate
    if zero.any():
        psplit = np.where(zero, -1, psplit)
    k_ = len(by[(rr[0], "S")]) if len(rr) else 0
    print(f"concepts: {len(rr)} roots, {k_} rollouts per model each ({', '.join(f'{n} {(psplit == i).sum()}' for i, n in enumerate(('fit', 'select', 'replicate')))}"
          f"{f', {zero.sum()} with identical rollouts left out' if zero.any() else ''}); {keep.sum()} candidate latents "
          f"(firing on {a.min_rate:.0%}-{a.max_rate:.0%} of positions); plies: {a.sum_plies}"
          f"{'; control: S against a second set of S rollouts' if control else ''}", flush=True)

    found = discover(D, psplit, keep, rate, nlat, F, a, dev)
    templates, sign, groups, stats = found["templates"], found["sign"], found["groups"], found["stats"]
    if not templates:
        sys.exit("no concept has a positive margin: larger clusters (--cluster-size) or a larger --nu")
    selected, replicated = found["selected"], found["replicated"]
    print(f"  {len(found['temps'])} concepts -> {len(templates)} after merging ({(sign > 0).sum()} S's, {(sign < 0).sum()} W's); "
          f"margin filter{' on each concept own clusters roots' if a.local else ''}: {selected.sum()} on the selection roots "
          f"(random concepts' margin > 0: {stats['select']['null_pos']:.1%}), {replicated.sum()} again on the replication roots "
          f"({(sign[replicated] > 0).sum()} S's, {(sign[replicated] < 0).sum()} W's)", flush=True)
    # the S-vs-S control: (1) each concept on S's rollouts against S's second set, on the same roots; (2) the whole
    # discovery run on S - S' (concepts found there are noise the filters let through)
    ctrl = {}
    Wm = weights_matrix(templates, F)
    if control:
        Dc = (mean["S"] - mean["S2"]).tocsr()
        Wn = weights_matrix(found["nulls"], F)
        nsign = np.repeat(sign, a.null_templates)
        for nm in ("select", "replicate"):
            rows, mk = found["masks"][nm]
            m, _ = local_margins(Dc[rows], Wm, sign, mk, a.nu)
            mn, _ = local_margins(Dc[rows], Wn, nsign, [x for x in mk for _ in range(a.null_templates)], a.nu)
            mn = mn.reshape(len(templates), a.null_templates)
            ctrl[nm] = dict(margin=m, null95=np.quantile(mn, 0.95, axis=1), passed=(m > 0) & (m > np.quantile(mn, 0.95, axis=1)))
        ctrl_both = ctrl["select"]["passed"] & ctrl["replicate"]["passed"]
        print("  control, S against S:", flush=True)
        cf = discover(Dc, psplit, keep, rate, nlat, F, a, dev, tag_="control: ")
        ctrl_run = dict(templates=len(cf["templates"]), selected=int(cf["selected"].sum()), replicated=int(cf["replicated"].sum()))
        print(f"  control: {ctrl_run['replicated']} S-vs-S concepts pass both margin filters (noise let through); "
              f"{int((replicated & ctrl_both).sum())} of the {replicated.sum()} S-vs-W concepts also separate S from S", flush=True)
    else:
        ctrl_both, ctrl_run = np.zeros(len(templates), bool), None

    # a root carries a concept out when its rollouts' mean score reaches halfway between the mean on S's and on W's
    # selection roots; per ply, a rollout has it active where that ply's score reaches the per-ply halfway mark
    sel_rows, rep_rows = np.flatnonzero(psplit == 1), np.flatnonzero(psplit == 2)
    tau = (np.asarray((mean["S"][sel_rows] @ Wm).mean(0)).ravel() + np.asarray((mean["W"][sel_rows] @ Wm).mean(0)).ravel()) / 2
    droots = rr[rep_rows]
    band = np.array([roots[ri]["band"] for ri in droots])
    xS = np.asarray((mean["S"][rep_rows] @ Wm).todense()) >= tau
    xW = np.asarray((mean["W"][rep_rows] @ Wm).todense()) >= tau
    b, c, _ = mcnemar(xS, xW)

    # the concept graph on the replication roots: concepts as nodes, active at a ply (above); follows (lags 2, 4, 6),
    # competes (rarely active together, lag 0), replaces (S's rollouts carry out B where W's carry out A); rollouts
    # in pairs (S's k-th with W's k-th), bootstrapped by root
    keep_g = replicated & ~ctrl_both
    gi = np.flatnonzero(keep_g)
    order = gi[np.argsort(-stats["replicate"]["margin"][gi])][:a.max_plans]
    P = [templates[g] for g in order]
    Wp = weights_matrix(P, F)
    counted = [t for t in range(1, T + 1) if not (a.sum_plies == "own" and t % 2)]

    def ply_scores(lines):
        s_ = np.zeros((len(lines), T + 1, len(P)), np.float32)
        Cl = C[lines]
        for t in counted:
            half = (t % 2) * nlat * (nf - 1)
            s_[:, t] = np.asarray((Cl[:, t * nlat:(t + 1) * nlat] @ Wp[half:half + nlat]).todense())
        return s_

    pr = [(by[(ri, "S")][k], by[(ri, "W")][k], g) for g, ri in enumerate(droots)
          for k in range(min(len(by[(ri, "S")]), len(by[(ri, "W")])))]
    sel_lines = [q for ri in rr[sel_rows] for kind in ("S", "W") for q in by[(ri, kind)]]
    plan_rows, competes, replaces = [], [], []
    if len(P) >= 2 and len(droots) >= a.min_roots:
        sp = ply_scores(sel_lines)[:, counted]
        tau_ply = sp.reshape(-1, len(P)).mean(0)
        AS, AW = np.zeros((len(pr), T + 1, len(P) + 1), np.float32), np.zeros((len(pr), T + 1, len(P) + 1), np.float32)
        for A_, ls in ((AS, [p[0] for p in pr]), (AW, [p[1] for p in pr])):
            for r, q in enumerate(ls):
                A_[r, :z["line_start"][q + 1] - z["line_start"][q], -1] = 1
            A_[:, counted, :-1] = (ply_scores(ls)[:, counted] >= tau_ply[None, None]) * A_[:, counted, -1:]
        tS, tW = torch.from_numpy(AS).to(dev), torch.from_numpy(AW).to(dev)
        E = diff_edges(tS, tW, [k for k in (0, 2, 4, 6) if k <= T], a, dev, groups=np.array([p[2] for p in pr]))
        for e in E.values():
            for k_ in e:
                e[k_] = e[k_][:len(P)] if e[k_].ndim == 1 else e[k_][:len(P), :len(P)]
        pnodes = [dict(kind="plan", id=int(g), label=f"concept {int(g)}") for g in order]
        plan_rows = categorise({k: v for k, v in E.items() if k > 0}, pnodes, a)
        e0 = E[0]
        for i in range(len(P)):
            for j in range(i + 1, len(P)):
                for who, l_, sd_, n_ in (("S", e0["lS"], e0["sd_lS"], e0["aS"]), ("W", e0["lW"], e0["sd_lW"], e0["aW"])):
                    if min(n_[i], n_[j]) >= a.min_count and l_[i, j] + 1.96 * sd_[i, j] < 0:
                        competes.append(dict(a=int(order[i]), b=int(order[j]), lines=who, lift=float(np.exp(l_[i, j]))))
        onlyW = (xW[:, order] & ~xS[:, order]).astype(np.float64)
        onlyS = (xS[:, order] & ~xW[:, order]).astype(np.float64)
        nAB = onlyW.T @ onlyS
        lift = (nAB + a.prior) / (np.outer(onlyW.sum(0), onlyS.sum(0)) / max(len(droots), 1) + a.prior)
        for i, j in zip(*np.nonzero((nAB >= a.min_count) & ~np.eye(len(P), dtype=bool))):
            replaces.append(dict(w_plan=int(order[i]), s_plan=int(order[j]), roots=int(nAB[i, j]), lift=float(lift[i, j])))
        replaces.sort(key=lambda r: -r["lift"])
        competes.sort(key=lambda r: r["lift"])

    recs = []
    for g, (cols, w) in enumerate(templates):
        members = groups[g]
        r = dict(id=g, side="S" if sign[g] > 0 else "W", features=describe_concept(cols, w, nlat, a.sum_plies, ex),
                 n_features=int(len(cols)), fits=len(members), fit_margin=float(np.mean([t["m"] for t in members])),
                 fit_share=float(np.mean([t["sep"] for t in members])),
                 **{f"{nm}_{k}": float(st[k][g]) for nm, st in stats.items() for k in ("margin", "share", "null95", "used")},
                 selected=bool(selected[g]), replicated=bool(replicated[g]), control=bool(ctrl_both[g]), tau=float(tau[g]),
                 **({f"control_{nm}_{k}": float(st[k][g]) for nm, st in ctrl.items() for k in ("margin", "null95")} if ctrl else {}),
                 executed=dict(S_not_W=int(b[g]), W_not_S=int(c[g]),
                               bands={n: [int((xS[band == n, g] & ~xW[band == n, g]).sum()), int((~xS[band == n, g] & xW[band == n, g]).sum())]
                                      for n in sorted(set(band))}))
        if keep_g[g]:
            want = (xS[:, g] & ~xW[:, g]) if sign[g] > 0 else (xW[:, g] & ~xS[:, g])
            r["examples"] = [example(Ld, by, evals, z, int(ri)) for ri in droots[want][:3]]
        recs.append(r)
    rec = dict(settings={k: getattr(a, k) for k in ("cluster_size", "nu", "dedupe", "min_rate", "max_rate", "sum_plies", "local",
                                                    "null_templates", "max_plans")},
               funnel=dict(roots=len(rr), rollouts=k_, identical=int(zero.sum()), fit_roots=int((psplit == 0).sum()),
                           select_roots=stats["select"]["roots"], replicate_roots=stats["replicate"]["roots"],
                           lps=found["lps"], clusters=found["clusters"], templates=len(found["temps"]), merged=len(templates),
                           selected=int(selected.sum()), replicated=int(replicated.sum()),
                           replicated_S=int((sign[replicated] > 0).sum()), replicated_W=int((sign[replicated] < 0).sum()),
                           null_select=stats["select"]["null_pos"], null_replicate=stats["replicate"]["null_pos"],
                           control=ctrl_run, also_control=int((replicated & ctrl_both).sum()), kept=int(keep_g.sum())),
               plans=recs, graph=dict(nodes=[int(g) for g in order], follows=[dict(r, src=int(order[r["src"]]), dst=int(order[r["dst"]]))
                                                                             for r in plan_rows if r["category"] != "shared"],
                                     competes=competes[:200], replaces=replaces[:200]))
    (out / "plans.json").write_text(json.dumps(rec, default=float), encoding="utf-8")
    res.mkdir(parents=True, exist_ok=True)
    (res / "plans.md").write_text(plans_text(rec, a) + "\n", encoding="utf-8")
    plans_page(out / "plans.html", out.name, rec)
    print(plans_text(rec, a))
    print(f"wrote {res / 'plans.md'}, {out / 'plans.json'} and {out / 'plans.html'}")


def describe_concept(cols, w, nlat, plies, ex, most=16):
    """A concept in words: its heaviest latents, and on whose move they count."""
    out = []
    for h, j, v in sorted(zip(cols // nlat, cols % nlat, w), key=lambda x: -abs(x[2]))[:most]:
        e = ex.get(int(j))
        when = {"own": "own move", "all": "any ply"}.get(plies) or ("own move" if h == 0 else "opponent's move")
        out.append(dict(latent=int(j), weight=float(v), when=when,
                        text=e["explanation"] if e and e.get("status") in ("explained", "weak") else f"latent {j}"))
    return out


def example(Ld, by, evals, z, ri):
    root = Ld["roots"][ri]
    item = dict(fen=root["fen"], band=root["band"], s_top=root["s_top"], w_top=root["w_top"], lines={})
    for kind in ("S", "W"):
        q = by[(ri, kind)][0]                                           # its first rollout
        l = Ld["lines"][q]
        item["lines"][kind] = dict(sans=l["sans"], first=l["moves"][0])
    return item


def plan_words(r, most=6):
    top = sorted(r["features"], key=lambda f: -abs(f["weight"]))[:most]
    return "; ".join(f"{f['text']} ({f['weight']:.2f})" for f in top)


def plans_text(rec, a):
    f = rec["funnel"]
    ctl = f.get("control")
    out = ["# Concepts: S's rollouts against W's", "",
           f"{f['roots']} roots, {f['rollouts']} rollouts per model each (a root uses their mean): {f['fit_roots']} to fit, "
           f"{f['select_roots']} to select, {f['replicate_roots']} to replicate (different games)"
           + (f"; {f['identical']} with identical S and W rollouts left out" if f.get("identical") else "") + ". "
           "Concepts are fitted, filtered and compared on the crosscoder's latents alone, each scored "
           + ("on the held-out roots of its own clusters (nearest centroid)." if a.local else "on all held-out roots."), "",
           "| step | S against W | control: S against S |", "|---|---|---|",
           f"| LPs fitted ({f['clusters']} clusters of ~{a.cluster_size} roots, S's and W's concepts) | {f['lps']} | |",
           f"| concepts with a positive margin | {f['templates']} | |",
           f"| after merging similar ones | {f['merged']} | {ctl['templates'] if ctl else '-'} |",
           f"| soft margin (share {a.nu} quantile) > 0 on selection roots, and above 95% of random concepts | {f['selected']} | "
           f"{ctl['selected'] if ctl else '-'} |",
           f"| ... and again on replication roots | {f['replicated']} ({f['replicated_S']} S's, {f['replicated_W']} W's) | "
           f"{ctl['replicated'] if ctl else '-'} |",
           f"| S-vs-W concepts that also separate S from S (dropped) | {f.get('also_control', 0)} | |",
           f"| random concepts with a margin > 0 (selection / replication) | {f['null_select']:.1%} / {f['null_replicate']:.1%} | |", ""]
    if ctl and ctl["replicated"] and f["replicated"] and ctl["replicated"] > 0.2 * f["replicated"]:
        out += [f"**Warning**: S against S yields {ctl['replicated']} concepts against {f['replicated']} for S against W: much of "
                "the S-vs-W list may be sampling noise.", ""]
    rep = [r for r in rec["plans"] if r["replicated"] and not r.get("control")]
    for side, title in (("S", "S's rollouts carry out and W's don't"), ("W", "W's rollouts carry out and S's don't")):
        rs = sorted((r for r in rep if r["side"] == side), key=lambda r: -r["replicate_margin"])[:a.show]
        if not rs:
            continue
        bn = list(rs[0]["executed"]["bands"])
        out += [f"## Plans {title}", "",
                "| plan | template (heaviest features, by ply) | margin: fit / selection / replication (random 95%) | "
                "replication roots where it beats the other side | executed S not W / W not S | "
                + " | ".join(f"{n} roots" for n in bn) + " | fits merged |", "|---|---|---|---|---|" + "---|" * len(bn) + "---|"]
        for r in rs:
            e = r["executed"]
            out.append(f"| {r['id']} | {plan_words(r)} | {r['fit_margin']:.3f} / {r['select_margin']:.3f} / {r['replicate_margin']:.3f} "
                       f"({r['replicate_null95']:.3f}) | {r['replicate_share']:.0%} | {e['S_not_W']} / {e['W_not_S']} | "
                       + " | ".join(f"{v[0]} / {v[1]}" for v in e["bands"].values()) + f" | {r['fits']} |")
        out.append("")
    g = rec["graph"]
    lab = {r["id"]: r for r in rec["plans"]}
    if g["follows"]:
        out += ["## Plan graph: which plans follow which (S-only and W-only edges)", "", "| lag | from | to | lift S | lift W | category |",
                "|---|---|---|---|---|---|"]
        for r in sorted(g["follows"], key=lambda r: -abs(r["delta"]))[:a.show]:
            out.append(f"| {r['lag']} | {r['src']}: {plan_words(lab[r['src']], 2)} | {r['dst']}: {plan_words(lab[r['dst']], 2)} | "
                       f"{r['lift_S']:.2f} | {r['lift_W']:.2f} | {r['category']} |")
        out.append("")
    if g["replaces"]:
        out += ["## Replacements: S executes the second plan where W executes the first (same root)", "",
                "| W's plan | S's plan | roots | lift |", "|---|---|---|---|"]
        out += [f"| {r['w_plan']}: {plan_words(lab[r['w_plan']], 2)} | {r['s_plan']}: {plan_words(lab[r['s_plan']], 2)} | {r['roots']} | "
                f"{r['lift']:.2f} |" for r in g["replaces"][:a.show]]
        out.append("")
    if g["competes"]:
        out += ["## Competing plans (rarely executed in the same line)", "", "| plan | plan | lines | lift |", "|---|---|---|---|"]
        out += [f"| {r['a']}: {plan_words(lab[r['a']], 2)} | {r['b']}: {plan_words(lab[r['b']], 2)} | {r['lines']} | {r['lift']:.2f} |"
                for r in g["competes"][:a.show]]
    return "\n".join(out)


def plans_page(path, name, rec):
    """plans.html: the plan graph (vis-network) and a card per plan in it, with roots where S executes it and W doesn't."""
    keep = set(rec["graph"]["nodes"])
    data = dict(plans={r["id"]: r for r in rec["plans"] if r["id"] in keep}, graph=rec["graph"])
    js = json.dumps(data, default=float).replace("</", "<\\/")
    path.write_text(f"""<!doctype html><html><head><meta charset="utf-8"><title>Plans: {html.escape(name)}</title>
<script src="https://unpkg.com/vis-network@9.1.9/standalone/umd/vis-network.min.js"></script>
<style>body{{font-family:system-ui,sans-serif;margin:0;display:flex;height:100vh}}#net{{flex:1;border-right:1px solid #ccc}}
#card{{width:560px;overflow:auto;padding:12px}}.ln{{font-family:monospace;font-size:12px}}.f{{margin:2px 0}}{BOARD_CSS}</style></head>
<body>{BOARD_DEFS}{MOVE_HEAD}<div id="net"></div><div id="card"><h3>Plans: {html.escape(name)}</h3>
<p>Nodes: plans that passed the margin filter on two sets of new games (green: S's rollouts carry them out, orange: W's). Arrows: one plan follows another
(green S-only, orange W-only); dashed blue: S executes the arrow's head where W executes its tail; red: rarely in the same line.
Click a plan.</p></div>
<script>{BOARD_JS}
const D = {js};
const col = p => p.side === "S" ? "#2e8b57" : "#e08a1e";
const nodes = new vis.DataSet(Object.values(D.plans).map(p => ({{id: p.id, label: String(p.id), color: col(p), shape: "dot",
  size: 8 + 2 * Math.sqrt(p.fits)}})));
const E = [];
for (const e of D.graph.follows) if (e.src in D.plans && e.dst in D.plans)
  E.push({{from: e.src, to: e.dst, arrows: "to", color: e.category === "S-only" ? "#2e8b57" : e.category === "W-only" ? "#e08a1e" : "#999"}});
for (const e of D.graph.replaces.slice(0, 60)) if (e.w_plan in D.plans && e.s_plan in D.plans)
  E.push({{from: e.w_plan, to: e.s_plan, arrows: "to", dashes: true, color: "#4a6fd6"}});
for (const e of D.graph.competes.slice(0, 60)) if (e.a in D.plans && e.b in D.plans) E.push({{from: e.a, to: e.b, color: "#d64a4a"}});
const net = new vis.Network(document.getElementById("net"), {{nodes, edges: new vis.DataSet(E)}}, {{physics: {{stabilization: true}}}});
net.on("click", ev => {{
  if (!ev.nodes.length) return;
  const p = D.plans[ev.nodes[0]], e = p.executed;
  let h = `<h3>plan ${{p.id}} (${{p.side}}'s)</h3><div>merged from ${{p.fits}} fits; soft margin: fit ${{p.fit_margin.toFixed(3)}},
    selection ${{p.select_margin.toFixed(3)}}, replication ${{p.replicate_margin.toFixed(3)}} (random templates' 95th percentile
    ${{p.replicate_null95.toFixed(3)}}); ${{(100 * p.replicate_share).toFixed(0)}}% of replication roots favour ${{p.side}}</div>
    <div>executed by S's rollout and not W's on ${{e.S_not_W}} roots, the reverse on ${{e.W_not_S}}</div>`;
  h += "<h4>concept: latents, summed over the rollout</h4>" + p.features.map(f => `<div class="f">${{f.text}}
    (${{f.when}}, weight ${{f.weight.toFixed(2)}})</div>`).join("");
  for (const x of (p.examples || [])) h += `<h4>${{x.band}} root: ${{p.side}}'s rollout carries it out, the other doesn't</h4>
    ${{board(x.fen, x.lines[p.side].first)}}<div class="ln">S would play ${{x.s_top}}, W ${{x.w_top}}<br>
    <b>S's rollout</b>: ${{x.lines.S.sans.join(" ")}}<br><b>W's rollout</b>: ${{x.lines.W.sans.join(" ")}}</div>`;
  document.getElementById("card").innerHTML = h;
}});
</script></body></html>""", encoding="utf-8")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["health", "recall", "lines", "roots", "play", "gather", "judge", "encode", "nodes",
                                        "graph", "plans", "all"])
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
    g.add_argument("--r2-floor", type=float, default=0.5, help="own-model R^2 needed before an exclusive tag can be confirmed")
    g = ap.add_argument_group("recall")
    g.add_argument("--cands", type=int, default=10, help="candidate latents per label")
    g.add_argument("--auc", type=float, default=0.9, help="held-out AUC at which a label counts as recovered")
    g.add_argument("--classic", default=None, help="a Stockfish 8-11 binary, for the classical evaluation terms")
    g.add_argument("--puzzles", type=int, default=8000, help="Lichess puzzles for the theme labels (0: none)")
    g.add_argument("--fetch-puzzles", action="store_true",
                   help="also use puzzles whose source game isn't cached yet, fetching them from Lichess")
    g = ap.add_argument_group("lines")
    g.add_argument("--population", default=str(PROBE / "population.jsonl"), help="held-out positions with their band")
    g.add_argument("--roots", type=int, default=4000, help="roots, half from each band")
    g.add_argument("--oversample", type=int, default=3, help="candidates per root wanted (before the disagreement filter)")
    g.add_argument("--per-game", type=int, default=2, help="roots per game at most")
    g.add_argument("--held", type=int, default=30, help="percent of games held out")
    g.add_argument("--plies", type=int, default=8, help="plies per line")
    g.add_argument("--temperature", type=float, default=1.0,
                   help="sampling temperature over the legal moves (1: each model's own imitation distribution; 0: greedy)")
    g.add_argument("--rollouts", type=int, default=4, help="rollouts per model per root (a root uses their mean)")
    g.add_argument("--control", action=argparse.BooleanOptionalAction, default=True,
                   help="also roll out S a second time (S2) for the S-vs-S control")
    g.add_argument("--part", type=int, default=0, help="play and judge: this part of the roots / positions ...")
    g.add_argument("--parts", type=int, default=1, help="... of this many (Modal runs the parts in parallel)")
    g.add_argument("--depth", type=int, default=0, help="Stockfish depth (0: no engine, the default; only the report's "
                   "line-end evaluations and graph's positional/tactical split use it)")
    g.add_argument("--workers", type=int, default=max(1, min(16, (os.cpu_count() or 2) - 2)), help="Stockfish processes")
    g.add_argument("--max-tokens", type=int, default=300_000, help="characters per forward pass when reading the lines")
    g = ap.add_argument_group("nodes")
    g.add_argument("--min-rate", type=float, default=0.01, help="latents firing on at least this share of positions ...")
    g.add_argument("--max-rate", type=float, default=0.5, help="... and at most this share")
    g.add_argument("--min-pairs", type=int, default=20, help="fit roots where S and W differ on a latent, needed to test it")
    g.add_argument("--min-pairs-held", type=int, default=10, help="held-out roots needed to confirm it")
    g.add_argument("--fdr-nodes", type=float, default=0.05, help="filters 2 and 3: Benjamini-Hochberg false discovery rate")
    g.add_argument("--max-nodes", type=int, default=300, help="latent nodes in the graph at most")
    g.add_argument("--null", type=int, default=50, help="random label flips for the null")
    g = ap.add_argument_group("graph")
    g.add_argument("--split", choices=["fit", "held"], default="fit", help="roots the graphs are built on")
    g.add_argument("--engine-split", action="store_true",
                   help="split the roots into positional and tactical by Stockfish (needs --depth > 0 in lines)")
    g.add_argument("--blunder", type=float, default=1.5, help="with --engine-split: a W move losing more pawns makes the root tactical")
    g.add_argument("--min-roots", type=int, default=50, help="roots a set needs to be analysed")
    g.add_argument("--lift", type=float, default=1.5, help="lift for a strong edge")
    g.add_argument("--min-count", type=int, default=10, help="co-occurrences an edge needs in either graph to be tested")
    g.add_argument("--fdr", type=float, default=0.05, help="Benjamini-Hochberg false discovery rate")
    g.add_argument("--prior", type=float, default=5.0, help="pseudocount shrinking each lift toward 1")
    g.add_argument("--min-discordant", type=int, default=8, help="roots completing a motif in one line only, needed to test it")
    g.add_argument("--boot", type=int, default=1000, help="bootstrap resamples of the roots")
    g.add_argument("--boot-chunk", type=int, default=25, help="bootstrap resamples at once (GPU memory)")
    g.add_argument("--max-motifs", type=int, default=20_000, help="motif candidates at most")
    g.add_argument("--show", type=int, default=20, help="motifs (and plans) listed per direction")
    g = ap.add_argument_group("plans")
    g.add_argument("--sum-plies", choices=["all", "own", "split"], default="all",
                   help="plies summed per rollout: all (default: the models write both colours' moves, so every ply is "
                        "the model's), own (only the root's side to move) or split (the two as separate latents)")
    g.add_argument("--cluster-size", type=int, default=100, help="roots per cluster (k-means on the roots' S - W differences)")
    g.add_argument("--min-concept-roots", type=int, default=15,
                   help="held-out roots a concept must be scored on (its clusters' roots with --local) to pass")
    g.add_argument("--local", action=argparse.BooleanOptionalAction, default=True,
                   help="score each concept on its own clusters' held-out roots (nearest centroid), not all of them")
    g.add_argument("--nu", type=float, default=0.2, help="soft margin: the share of roots allowed inside it (fit and filter)")
    g.add_argument("--dedupe", type=float, default=0.5, help="cosine at which templates merge")
    g.add_argument("--null-templates", type=int, default=50, help="rate-matched random templates per template")
    g.add_argument("--max-plans", type=int, default=300, help="plans in the plan graph at most")
    a = ap.parse_args()
    steps = dict(health=health, recall=recall, lines=lines, roots=roots_stage, play=play_stage, gather=gather, judge=judge,
                 encode=encode_stage, nodes=nodes, graph=graph, plans=plans)
    for name in (["health", "recall", "lines", "plans", "nodes", "graph"] if a.command == "all" else [a.command]):
        print(f"\n=== {name}", flush=True)
        steps[name](a)


if __name__ == "__main__":
    main()
