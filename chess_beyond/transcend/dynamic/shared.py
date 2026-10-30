"""Helpers shared by readings.py, oneposition.py and recurring.py (kept from the retired graphdiff.py and
manypositions.py): the crosscoder, both models' policies and states, rollouts, the lines' positions, and Schut's
max-min LP."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import chess
import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # chess_beyond/
import paths  # noqa: E402  also puts transcend/'s folders on sys.path
import eval as ev
from concepts import Cache, extend, pad, room
from crosscoder import CrossCoder
from pgn_model import MAX_MOVE_CHARS, SPACE, encode, prompt
from pgn_probe import DEFAULT as PROBE
from pgn_probe import parse_movetext

RUNS = paths.RUNS / "transcend" / "graphdiff"
RESULTS = paths.ROOT / "results" / "transcend" / "graphdiff"


def load_cc(cc_run, cc, strong, dev, name=None):
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
    name = name or f"{cc_run.name}-{cc_dir.name.removeprefix('cc-')}"        # --name: the same folder dirs() uses
    return SimpleNamespace(run=cc_run, dir=cc_dir, info=info, ck=ck, sources=sources, coder=coder,
                           scales=ck["scales"].to(dev), s=s, w=1 - s, col=col, layer=dict(sources), r=r,
                           out=RUNS / name, res=RESULTS / name)


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


def lichess_line(root, sans):
    """A Lichess analysis link: the game from its start, through the rollout, opened at the root."""
    from urllib.parse import quote
    from pgn_model import movetext
    pre = parse_movetext(root["prompt"])[0]
    return f"https://lichess.org/analysis/pgn/{quote(movetext(pre + list(sans))[1:])}#{len(pre)}"


def encode_states(cc, st):
    """{model: (n, d)} states at the crosscoder's layer -> latent activations (n, latents), scaled input."""
    x = torch.stack([st[m].float() for m, _ in cc.sources], 1) * cc.scales[None, :, None]
    return cc.coder.encode(x)[0], x


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


def pick_positions(a, Sm, dev):
    """Up to --positions positions from different games, each with >= 2 moves >= --reasonable and none above --max-top
    (S's policy), in a seeded random order -> [(root, legal moves, log-probabilities)]."""
    rng = np.random.default_rng(a.seed)
    pop = [json.loads(l) for l in open(a.population, encoding="utf-8")]
    out, games = [], set()
    order = rng.permutation(len(pop))
    for s in range(0, len(order), a.scan):
        cand = []
        for i in order[s:s + a.scan]:
            r = pop[i]
            if (r["band"], r["game"]) in games or len(r["prompt"]) + room(a.plies) + MAX_MOVE_CHARS + 1 > Sm.ctx:
                continue
            b = ev.board_of(parse_movetext(r["prompt"])[0])
            if prompt(b) != r["prompt"] or b.is_game_over() or not middlegame(b):
                continue
            cand.append((r, b))
        if not cand:
            continue
        legal, lp, _ = policy(Sm, [b for _, b in cand], dev, [r["prompt"] for r, _ in cand], batch=a.batch)
        for (r, b), mv, l in zip(cand, legal, lp):
            if (r["band"], r["game"]) in games:
                continue
            p = np.exp(l - np.logaddexp.reduce(l))
            if p.max() <= a.max_top and (p >= a.reasonable).sum() >= 2:
                games.add((r["band"], r["game"]))
                top = sorted(zip(p, mv), key=lambda x: -x[0])[:5]
                out.append((dict(prompt=r["prompt"], fen=b.fen(), band=r["band"], game=r["game"],
                                 top=[(b.san(m), float(q)) for q, m in top]), mv, l))
                if len(out) >= a.positions:
                    return out
    return out


def x_of(P, D, plies, nlat):
    """Per distinct line, the share of its plies where each latent fires, from the per-ply matrix."""
    from scipy import sparse
    n = np.array([max(len(d["sans"]), 1) for d in D], float)
    rows = np.repeat(np.arange(len(D)), plies + 1)
    S = sparse.csr_matrix((np.ones(len(rows)), (rows, np.arange(len(rows)))), shape=(len(D), len(rows)))
    return np.asarray((S @ (P > 0).astype(np.float32)).todense(), np.float32) / n[:, None]


def wmed(v, w):
    o = np.argsort(v)
    cw = np.cumsum(w[o])
    return float(v[o][min(int(np.searchsorted(cw, cw[-1] / 2)), len(v) - 1)])
