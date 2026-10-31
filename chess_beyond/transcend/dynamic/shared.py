"""Helpers for the dynamic-concept scripts: the crosscoder, both models' policies and states, rollouts and their cached
codes, the lines' positions, and Schut's max-min LP."""

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
from concepts import Cache, extend, pad
from crosscoder import CrossCoder
from pgn_model import MAX_MOVE_CHARS, SPACE, encode, prompt
from pgn_probe import DEFAULT as PROBE
from pgn_probe import parse_movetext


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


# ------------------------------------------------------------------ rollouts and their codes (from the retired
# oneposition.py, recurring.py and readings.py; divergence.py, overnight_play.py and layerprobe.py use them)


def middlegame_roots(a, ctx):
    """--positions middlegame positions from --population, one per game, in a seeded random order -> [(row, board)]."""
    rng = np.random.default_rng(a.seed)
    pop = [json.loads(l) for l in open(a.population, encoding="utf-8")]
    out, games = [], set()
    for i in rng.permutation(len(pop)):
        r = pop[i]
        if (r["band"], r["game"]) in games or len(r["prompt"]) + MAX_MOVE_CHARS + 1 > ctx:
            continue
        b = ev.board_of(parse_movetext(r["prompt"])[0])
        if prompt(b) != r["prompt"] or b.is_game_over() or not middlegame(b):
            continue
        games.add((r["band"], r["game"]))
        out.append((r, b))
        if len(out) >= a.positions:
            break
    return out


def rollouts(a, root, legal, lp, Sm, dev, T, seed):
    """--rollouts lines of S from the root at temperature T, S writing every move -> [tuple of SANs], [tuple of UCIs]."""
    rng = np.random.default_rng(seed)
    b0 = ev.board_of(parse_movetext(root["prompt"])[0])
    L = []
    for k in range(a.rollouts):
        line = dict(board=b0.copy(), moves=[], sans=[], prompt=root["prompt"])
        advance(line, legal[sample(lp, T, rng)])
        L.append(line)
    for ply in range(1, a.plies):
        live = [l for l in L if len(l["moves"]) == ply and not l["board"].is_game_over()]
        if live:
            lg, lps, _ = policy(Sm, [l["board"] for l in live], dev, [l["prompt"] for l in live], batch=a.batch)
            for l, mv, p in zip(live, lg, lps):
                advance(l, mv[sample(p, T, rng)])
    return [tuple(l["sans"]) for l in L], [tuple(l["moves"]) for l in L]


def distinct(sans, ucis):
    """The distinct lines, most common first -> [dict(sans, moves, n)]."""
    from collections import Counter
    cnt = Counter(zip(sans, ucis))
    return [dict(sans=list(s), moves=list(u), n=n) for (s, u), n in cnt.most_common()]


def mark(sans, plies, root):
    """SAN with move numbers, the plies where the concept's latents fire in [brackets]."""
    b = chess.Board(root["fen"])
    n, white = b.fullmove_number, b.turn == chess.WHITE
    out = []
    for i, m in enumerate(sans):
        w = white if i % 2 == 0 else not white
        num = n + (i + (0 if white else 1)) // 2
        s = (f"{num}." if w else (f"{num}..." if i == 0 else "")) + m
        out.append(f"[{s}]" if (i + 1) in plies else s)
    return " ".join(out)


def encode_values(a, cc, models, root, D, dev):
    """Every position's activations, values kept -> sparse (lines * (plies + 1), latents) float32 (row 0 of a line: its
    root, left empty)."""
    import torch
    from scipy import sparse
    Ld = dict(roots=[dict(prompt=root["prompt"], fen=root["fen"])], lines=[dict(root=0, moves=d["moves"]) for d in D])
    seqs, ends, _, _, _, line_start = positions(Ld)
    st = {m: line_states(models[m], seqs, ends, cc.layer[m], dev, a.max_tokens) for m in (0, 1)}
    rows, cols, vals = [], [], []
    with torch.no_grad():
        for i in range(0, len(st[0]), 4096):
            f, _ = encode_states(cc, {m: st[m][i:i + 4096].to(dev) for m in (0, 1)})
            nz = (f > 0).nonzero()
            rows.append(nz[:, 0].cpu().numpy() + i)
            cols.append(nz[:, 1].cpu().numpy())
            vals.append(f[nz[:, 0], nz[:, 1]].float().cpu().numpy())
    rows, cols, vals = np.concatenate(rows), np.concatenate(cols), np.concatenate(vals)
    pos_line = np.repeat(np.arange(len(D)), np.diff(line_start))
    pos_t = np.concatenate([np.arange(n) for n in np.diff(line_start)])
    keep = pos_t[rows] >= 1
    r_ = rows[keep]
    return sparse.csr_matrix((vals[keep], (pos_line[r_] * (a.plies + 1) + pos_t[r_], cols[keep])),
                             shape=(len(D) * (a.plies + 1), cc.ck["latents"]))


def raw_pos(run, k):
    """A position's cached codes as saved (not divided by mu) -> lines, codes, line weights, the npz."""
    from scipy import sparse
    z = np.load(run / f"pos-{k}.npz")
    D = json.loads(str(z["D"]))
    P = sparse.csr_matrix((z["data"].astype(np.float32), z["indices"], z["indptr"]), shape=tuple(z["shape"]))
    w = np.array([d["n"] for d in D], float)
    return D, P, w / w.sum(), z


def mu_counts(run, K):
    """Each latent's mean value when on, over the cached positions 0..K-1 (their vcnt, vsum)."""
    cnt, tot = 0, 0
    for k in range(K):
        if (run / f"pos-{k}.npz").exists():
            z = np.load(run / f"pos-{k}.npz")
            cnt, tot = cnt + z["vcnt"], tot + z["vsum"]
    return tot / np.maximum(cnt, 1)


def on_matrix(P, mu, frac):
    """Activations above frac x mu_j, as a boolean sparse matrix of the same shape."""
    Q = P.copy()
    Q.data = (Q.data > frac * mu[Q.indices]).astype(np.float32)
    Q.eliminate_zeros()
    return Q


def core_match(G, jac):
    """Greedy, largest groups first: a group (position, set) joins the pattern whose core it matches best at Jaccard >=
    jac, else starts one; a core is the latents in at least half of the pattern's members -> [dict(members, core)]."""
    pats, index = [], {}
    for i in sorted(range(len(G)), key=lambda i: -len(G[i][1])):
        k, s = G[i]
        cand = {p for j in s for p in index.get(j, ())}
        best, bj = None, jac
        for p in cand:
            c = pats[p]["core"]
            j_ = len(s & c) / len(s | c)
            if j_ >= bj:
                best, bj = p, j_
        if best is None:
            pats.append(dict(members=[i], counts={j: 1 for j in s}, core=set(s)))
            p = len(pats) - 1
        else:
            p = best
            P_ = pats[p]
            P_["members"].append(i)
            for j in s:
                P_["counts"][j] = P_["counts"].get(j, 0) + 1
            old = P_["core"]
            P_["core"] = {j for j, n in P_["counts"].items() if n >= len(P_["members"]) / 2}
            for j in old - P_["core"]:
                index[j].discard(p)
        for j in pats[p]["core"]:
            index.setdefault(j, set()).add(p)
    return pats
