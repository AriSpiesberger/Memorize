"""Concept graphs from self-play rollouts: which crosscoder latents turn on after which.

    python transcend/concepts.py rollout --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal
    python transcend/concepts.py graph   --run runs/transcend/concepts/everything-3m-Lfinal

rollout  Start positions: random plies (one per game) of games from --pgn-data (default every
         rating). Each player model (default both models of the crosscoder) plays itself from each
         start, --rollouts times, for --plies plies at --temperature (characters sampled, the
         move parsed as SAN, an illegal move resampled up to 5 times as in eval.py). For speed:
         a KV cache that keeps each start's prompt once for all its rollouts, the per-character
         bookkeeping as GPU tensors (python-chess only for finished moves), the decoding step
         replayed as a CUDA graph, and the playing model's states taken while it plays.
         Games stop at checkmate, stalemate or a dead position (no repetition rules). Every position reached is then read by
         BOTH models (the crosscoder needs both) and encoded with the crosscoder; a latent's
         onset at ply t is: active at t, not at t - 1.
         Edge counts, per player model, for latents i, j (dense, every pair):
             C[i, j]  onsets of i at ply t followed by an onset of j in plies t+1 .. t+--window,
                      in the same rollout
             X[i, j]  the same, summed over every pair of rollouts from the same start
         so E = (X - C) / (rollouts - 1) is what C would be if i's onset told nothing about
         j's beyond what the start position does (sibling rollouts share the start, the side to
         move, the move number). The excess C - E is the edge. -> <run>/<model>/{C,X}.npy,
         onsets.npy (N[i]), active.npy, meta.json; saved every --save-every batches, and a
         rerun resumes from the last save. sample.txt: some rollouts as text.

graph    Edge statistics: excess = C - E, lift = (C + 1) / (E + 1), z = excess / sqrt(E + 1),
         rate = excess / N[i] (how much more likely j's onset is within the window, per onset of
         i). Edges: z >= --z, lift >= --lift, C >= --min-count, the --edges strongest by z per
         model; and a diff graph, edges whose rate differs between the two players
         (z of the difference >= --z). Nodes carry the crosscoder's relative decoder norm
         (0 = only model A, 1 = only model B) and their top positions.
         -> results/transcend/concepts/<run>/edges-<model>.csv, edges-diff.csv, summary.md;
            <run>/graph.graphml (for Gephi) and <run>/graph.html (interactive, both players and
            the diff).
"""
import argparse
import html
import json
import sys
import time
from pathlib import Path

import chess
import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parent))          # transcend/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))      # chess_beyond/
import paths
import eval as ev                                                 # load, board_of, device
from crosscoder import FOLDERS, Corpus, CrossCoder, pick_positions, position
from pgn_model import BOS, MAX_MOVE_CHARS, MAX_TRIES, SPACE, VOCAB, encode, prompt
from pgn_probe import parse_movetext
from sae import last_moves

RUNS = paths.RUNS / "transcend" / "concepts"
RESULTS = paths.ROOT / "results" / "transcend" / "concepts"


# ---------------------------------------------------------------- self-play with a KV cache

class Cache:
    """KV cache in two parts: each start's prompt once, shared by its R rollouts, and each rollout's own
    continuation. Attention reads the prompt once per start, not once per rollout: the prompt is most of
    the context, and reading the cache is what a decoding step costs."""

    def __init__(self, model, S, R, Lp, Ls, dev):
        heads, d = model.blocks[0].heads, model.ln.normalized_shape[0]
        dt = torch.bfloat16 if dev == "cuda" else torch.float32
        self.pk = [torch.zeros((S, heads, Lp, d // heads), dtype=dt, device=dev) for _ in model.blocks]
        self.pv = [torch.zeros_like(k) for k in self.pk]
        self.sk = [torch.zeros((S * R, heads, Ls, d // heads), dtype=dt, device=dev) for _ in model.blocks]
        self.sv = [torch.zeros_like(k) for k in self.sk]
        self.S, self.R, self.plen, self.plen_rep, self.pmask = S, R, None, None, None


def attend(q, cache, l, spos, Ls):
    """q (B, heads, T, dh) at continuation positions spos (B, T): attention over the start's prompt
    and the first Ls continuation positions up to spos, one softmax over both."""
    B, H, T, dh = q.shape
    S, R = cache.S, cache.R
    Lp = cache.pk[l].shape[2]
    qg = q.reshape(S, R, H, T, dh).transpose(1, 2).reshape(S, H, R * T, dh)
    sp = (qg @ cache.pk[l].transpose(-1, -2)).float() * dh ** -0.5
    sp = sp.masked_fill(~cache.pmask[:, None, None, :], -float("inf"))
    sp = sp.view(S, H, R, T, Lp).transpose(1, 2).reshape(B, H, T, Lp)
    ss = (q @ cache.sk[l][:, :, :Ls].transpose(-1, -2)).float() * dh ** -0.5
    ss = ss.masked_fill(~(torch.arange(Ls, device=q.device)[None, None, :] <= spos[:, :, None])[:, None], -float("inf"))
    w = torch.softmax(torch.cat([sp, ss], -1), -1).to(q.dtype)
    wp = w[..., :Lp].reshape(S, R, H, T, Lp).transpose(1, 2).reshape(S, H, R * T, Lp)
    yp = (wp @ cache.pv[l]).view(S, H, R, T, dh).transpose(1, 2).reshape(B, H, T, dh)
    return yp + w[..., Lp:] @ cache.sv[l][:, :, :Ls]


def prefill(model, x, plen, cache, layers=()):
    """The S prompts (right-padded) through the model, filling the prompt cache. -> next-character logits
    at each prompt's end, repeated for the R rollouts, and {layer: (S, d)} states there."""
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
        if str(l) in layers:
            out[str(l)] = h[rows, plen - 1].float()
    f = model.ln(h[rows, plen - 1])
    if "final" in layers:
        out["final"] = f.float()
    return model.head(f).float().repeat_interleave(cache.R, 0), out


def extend(model, x, spos, cache, layers=(), Ls=None):
    """Continuation characters x (B, T) at positions spos (B, T) through the model, writing their cache;
    attention covers the first Ls continuation positions (default spos.max() + 1, which syncs).
    -> logits at the last position and {layer: (B, T, d)} states."""
    B, T = x.shape
    d = model.ln.normalized_shape[0]
    Ls = Ls or int(spos.max()) + 1
    rows = torch.arange(B, device=x.device)[:, None]
    h = model.tok(x) + model.pos(cache.plen_rep[:, None] + spos)
    out = {}
    for l, blk in enumerate(model.blocks):
        q, k, v = (z.view(B, T, blk.heads, d // blk.heads).transpose(1, 2) for z in blk.qkv(blk.ln1(h)).split(d, dim=2))
        cache.sk[l][rows, :, spos] = k.transpose(1, 2).to(cache.sk[l].dtype)
        cache.sv[l][rows, :, spos] = v.transpose(1, 2).to(cache.sv[l].dtype)
        y = attend(q, cache, l, spos, Ls)
        h = h + blk.proj(y.transpose(1, 2).reshape(B, T, d))
        h = h + blk.mlp(blk.ln2(h))
        if str(l) in layers:
            out[str(l)] = h.float()
    f = model.ln(h)
    if "final" in layers:
        out["final"] = f.float()
    return model.head(f[:, -1]).float(), out


class Stepper:
    """One decoding step (one character per row) at fixed shapes, recorded as a CUDA graph and replayed,
    so a step is one launch instead of hundreds. Falls back to running eagerly if capture fails or the
    first replay disagrees with the eager step."""

    def __init__(self, model, cache, layers, dev, graphs):
        B = cache.sk[0].shape[0]
        self.model, self.cache, self.layers, self.dev = model, cache, layers, dev
        self.Ls = cache.sk[0].shape[2]
        self.tok = torch.full((B, 1), SPACE, dtype=torch.long, device=dev)
        self.spos = torch.zeros((B, 1), dtype=torch.long, device=dev)
        self.graph, self.checked = None, False
        if graphs and dev == "cuda":
            try:
                s = torch.cuda.Stream()
                s.wait_stream(torch.cuda.current_stream())
                with torch.cuda.stream(s):                  # warm-up (writes only continuation position 0,
                    for _ in range(2):                      # which the first real step overwrites)
                        self.eager()
                torch.cuda.current_stream().wait_stream(s)
                self.graph = torch.cuda.CUDAGraph()
                with torch.cuda.graph(self.graph):
                    self.out = self.eager()
            except Exception as e:
                print(f"\n  CUDA graph capture failed ({type(e).__name__}: {e}); decoding eagerly", flush=True)
                self.graph = None

    def eager(self):
        with torch.autocast("cuda", dtype=torch.bfloat16, enabled=self.dev == "cuda", cache_enabled=False):
            return extend(self.model, self.tok, self.spos, self.cache, self.layers, Ls=self.Ls)

    def __call__(self, tok, spos):
        self.tok.copy_(tok)
        self.spos.copy_(spos)
        if self.graph is None:
            return self.eager()
        if not self.checked:                                # same inputs, same cache writes: compare once
            self.checked = True
            ref = self.eager()
            ref = (ref[0].clone(), {k: v.clone() for k, v in ref[1].items()})
            self.graph.replay()
            err = (self.out[0] - ref[0]).abs().max().item()
            if not err < 1e-2:
                print(f"\n  CUDA graph replay differs from the eager step (max {err:.3g}); decoding eagerly", flush=True)
                self.graph = None
                return ref
            return self.out
        self.graph.replay()
        return self.out


def room(plies):
    """Characters a rollout of `plies` plies can add: each move, a space and every other ply ' <n>.'."""
    return plies * (MAX_MOVE_CHARS + 1) + (plies // 2 + 1) * 5 + 4


def pad(prompts, dev):
    plen = torch.tensor([len(p) for p in prompts], device=dev)
    x = torch.full((len(prompts), int(plen.max())), SPACE, dtype=torch.long, device=dev)
    for s, p in enumerate(prompts):
        x[s, :len(p)] = torch.tensor(p)
    return x, plen


def over(board):
    """Checkmate, stalemate or dead position (repetition and 50-move draws are not checked; rollouts are short)."""
    return not any(board.generate_legal_moves()) or board.is_insufficient_material()


@torch.no_grad()
def play(model, boards, prompts, R, plies, T, dev, gen, layers=(), graphs=True):
    """Self-play, R rollouts from each of the S boards (their prompts as token ids), up to `plies` plies.
    The character-level bookkeeping runs on the GPU; only rows that just finished a move go to python-chess.
    -> continuation characters (S*R, n); ends (S*R, plies): where each ply's prompt ends, -1 = the start
    prompt's last character, >= 0 = that index in the continuation, -2 = game stopped; the playing model's
    {layer: (S*R, plies, d)} states there (zeros where ends == -2); illegal attempts.
    Rows are start-major: row s*R + r."""
    x, plen = pad(prompts, dev)
    boards = [b.copy(stack=False) for b in boards for _ in range(R)]
    B, Ls, M = len(boards), room(plies), MAX_MOVE_CHARS
    cache = Cache(model, len(prompts), R, x.shape[1], Ls, dev)
    with torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev == "cuda"):
        logits, first = prefill(model, x, plen, cache, layers)
    stepper = Stepper(model, cache, layers, dev, graphs)
    rows = torch.arange(B, device=dev)
    L_ = lambda: torch.zeros(B, dtype=torch.long, device=dev)
    buf = torch.full((B, Ls), SPACE, dtype=torch.long, device=dev)
    ends = torch.full((B, plies), -2, dtype=torch.long, device=dev)
    ends[:, 0] = -1
    pst = {L: torch.zeros((B, plies, v.shape[-1]), device=dev) for L, v in first.items()}
    for L, v in first.items():
        pst[L][:, 0] = v.repeat_interleave(R, 0)
    ply_logits = logits.clone()                               # logits where each row's current move starts (retries)
    pos, ply, tries, npart, qlen, qidx = L_(), L_(), L_(), L_(), L_(), L_()
    pos_end = L_() - 1                                        # the current ply's prompt end
    done = torch.zeros(B, dtype=torch.bool, device=dev)
    part = torch.zeros((B, M), dtype=torch.long, device=dev)  # the move being written
    qbuf = torch.zeros((B, 6), dtype=torch.long, device=dev)  # forced characters ' <n>.' still to feed
    fails = 0

    def sample(lg, empty):
        lg = lg / T
        lg[:, BOS] = -float("inf")                            # never a new game mid-move
        lg[:, SPACE] = torch.where(empty, -float("inf"), lg[:, SPACE])   # a move has at least one character
        return torch.multinomial(torch.softmax(lg, -1), 1, generator=gen).squeeze(1)

    while True:
        nxt = sample(logits, npart == 0)
        live = ~done
        forced = live & (qlen > 0)
        samp = live & (qlen == 0)
        cont = samp & (nxt != SPACE) & (npart < M)
        comp = samp & ~cont                                   # a space (move written) or too long
        feed = torch.where(forced, qbuf.gather(1, qidx[:, None]).squeeze(1), torch.full_like(nxt, SPACE))
        feed = torch.where(cont, nxt, feed)
        at = npart.clamp(max=M - 1)[:, None]
        part.scatter_(1, at, torch.where(cont[:, None], nxt[:, None], part.gather(1, at)))
        npart = npart + cont.long()
        qidx, qlen = qidx + forced.long(), qlen - forced.long()
        start = forced & (qlen == 0)                          # the last forced character is the prompt's end

        ci = comp.nonzero().squeeze(1)
        if len(ci):
            info = torch.stack([nxt[ci], npart[ci], ply[ci], pos[ci], tries[ci]], 1).tolist()
            chars = part[ci].tolist()
            ok, stop, qn, qc, retry = [], [], [], [], []
            for b, (c, n, p, ps, tr), ch in zip(ci.tolist(), info, chars):
                mv = None
                if c == SPACE:
                    try:
                        mv = boards[b].parse_san("".join(VOCAB[i] for i in ch[:n]))
                    except ValueError:
                        pass
                if mv is None:
                    fails += 1
                    ok.append(False), stop.append(tr + 1 >= MAX_TRIES), qn.append(0), qc.append([0] * 6)
                    if tr + 1 < MAX_TRIES:
                        retry.append(b)
                    continue
                bd = boards[b]
                bd.push(mv)
                end = p + 1 >= plies or ps + room(1) >= Ls or over(bd)
                q = encode(f"{bd.fullmove_number}.") if not end and bd.turn == chess.WHITE else []
                ok.append(True), stop.append(end), qn.append(len(q)), qc.append(q + [0] * (6 - len(q)))
            okm = torch.zeros(B, dtype=torch.bool, device=dev)
            stm = torch.zeros(B, dtype=torch.bool, device=dev)
            qnm = L_()
            okm[ci] = torch.tensor(ok, device=dev)
            stm[ci] = torch.tensor(stop, device=dev)
            qnm[ci] = torch.tensor(qn, device=dev)
            qbuf[ci] = torch.tensor(qc, dtype=torch.long, device=dev)
            fail = comp & ~okm
            ply = ply + okm.long()
            tries = torch.where(okm, 0, tries + fail.long())
            npart = torch.where(comp, 0, npart)
            done = done | (comp & stm)
            qlen = torch.where(okm, qnm, qlen)
            qidx = torch.where(okm, 0, qidx)
            start = start | (okm & ~stm & (qnm == 0))         # Black to move: the space fed now is the prompt's end
            if retry:                                         # resample the move from where it starts
                r = torch.tensor(retry, device=dev)
                c = sample(ply_logits[r].clone(), torch.ones(len(retry), dtype=torch.bool, device=dev))
                feed[r] = c
                part[r, 0] = c
                npart[r] = 1
                pos[r] = pos_end[r] + 1
        pk = ply.clamp(max=plies - 1)[:, None]
        ends.scatter_(1, pk, torch.where(start[:, None], pos[:, None], ends.gather(1, pk)))
        pos_end = torch.where(start, pos, pos_end)
        if bool(done.all()):
            break
        p = pos.clamp(max=Ls - 1)
        buf[rows, p] = feed
        logits, out = stepper(feed[:, None], p[:, None])
        ply_logits = torch.where(start[:, None], logits, ply_logits)
        for L in pst:
            pst[L][rows, pk[:, 0]] = torch.where(start[:, None], out[L][:, 0], pst[L][rows, pk[:, 0]])
        pos = pos + live.long() * (~done).long()
    return buf, ends, pst, fails


@torch.no_grad()
def states(model, x, plen, R, buf, ends, layers, dev, chunk=32):
    """{layer: (S*R, plies, d)} states where each ply's prompt ends (zeros where ends == -2): the start
    prompts once per start, then every rollout's continuation, in chunks of `chunk` characters."""
    B = len(buf)
    n = int(ends.max()) + 1
    cache = Cache(model, len(x), R, x.shape[1], max(n, 1), dev)
    with torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev == "cuda"):
        _, first = prefill(model, x, plen, cache, layers)
        cont = {L: [] for L in layers}
        for c in range(0, n, chunk):
            m = min(n, c + chunk)
            spos = torch.arange(c, m, device=dev).expand(B, -1)
            _, st = extend(model, buf[:, c:m], spos, cache, layers, Ls=m)
            for L in layers:
                cont[L].append(st[L])
    e = ends.to(dev)
    rows = torch.arange(B, device=dev)[:, None]
    out = {}
    for L in layers:
        base = first[L].repeat_interleave(R, 0)[:, None].expand(-1, e.shape[1], -1)
        if n:
            got = torch.cat(cont[L], 1)[rows, e.clamp_min(0)]
            base = torch.where((e >= 0)[..., None], got, base)
        out[L] = base * (e >= -1)[..., None]
    return out


# ---------------------------------------------------------------- edge counts

class Counts:
    """C, X, onsets, active on the GPU (float32, exact for counts below 2^24), flushed to float64 on save."""

    def __init__(self, L, dev, folder, resume):
        self.folder, self.dev, self.L = folder, dev, L
        self.meta = json.loads((folder / "meta.json").read_text()) if resume and (folder / "meta.json").exists() else {}
        load = (lambda n, shape: np.load(folder / f"{n}.npy") if self.meta else np.zeros(shape))
        self.total = {n: load(n, s) for n, s in (("C", (L, L)), ("X", (L, L)), ("onsets", L), ("active", L))}
        self.reset()

    def reset(self):
        self.gpu = {n: torch.zeros(v.shape, device=self.dev) for n, v in self.total.items()}

    def add(self, act, valid, R, window):
        """act (B, P, L) bool, valid (B, P); rows are starts x R rollouts."""
        B, P, L = act.shape
        a = act.float() * valid[..., None]
        on = a[:, 1:] * (1 - a[:, :-1]) * valid[:, :-1, None]          # onset at plies 1 .. P-1
        win = torch.zeros_like(on)
        for d in range(1, window + 1):                                  # j's onsets in t+1 .. t+window
            win[:, :-d] = torch.maximum(win[:, :-d], on[:, d:])
        src = on[:, :-1] * valid[:, 2:, None]                           # sources need a next ply
        win = win[:, :-1]
        O, W = src.reshape(-1, L), win.reshape(-1, L)
        self.gpu["C"] += O.T @ W
        Os = src.view(B // R, R, -1, L).sum(1).reshape(-1, L)
        Ws = win.view(B // R, R, -1, L).sum(1).reshape(-1, L)
        self.gpu["X"] += Os.T @ Ws
        self.gpu["onsets"] += O.sum(0)
        self.gpu["active"] += a.sum((0, 1))

    def save(self, meta):
        for n, v in self.gpu.items():
            self.total[n] += v.double().cpu().numpy()
        self.reset()
        self.folder.mkdir(parents=True, exist_ok=True)
        for n, v in self.total.items():
            np.save(self.folder / f"{n}.npy", v)
        self.meta = meta
        (self.folder / "meta.json").write_text(json.dumps(meta, indent=1))


def rollout(a):
    dev = ev.device(a.device)
    torch.backends.cuda.matmul.allow_tf32 = True
    cc_run = Path(a.cc_run)
    cc_dir = cc_run / ("cc-" + a.cc.removeprefix("cc-"))
    info = json.loads((cc_run / "collect.json").read_text())
    ck = torch.load(cc_dir / "cc.pt", map_location="cpu", weights_only=False)
    sources = [tuple(s) for s in ck["sources"]]
    cc = CrossCoder(len(sources), ck["d"], ck["latents"], ck["k"]).to(dev)
    cc.load_state_dict(ck["state"])
    scales = ck["scales"].to(dev)
    models = [ev.load(m, dev) for m in info["models"]]                 # the crosscoder's two models, in order
    layers = sorted({L for _, L in sources}, key=str)
    run = Path(a.run) if a.run else RUNS / f"{cc_run.name}-{cc_dir.name.removeprefix('cc-')}"
    run.mkdir(parents=True, exist_ok=True)
    players = a.players or info["models"]
    R = a.rollouts
    per_batch = max(1, a.batch // R)

    corpus = Corpus(a.pgn_data)
    ctx = min(m.ctx for m, _ in models) - room(a.plies)
    print(f"picking {a.starts} start positions", flush=True)
    starts = pick_positions(corpus, a.starts, 1, a.min_ply, ctx, a.seed)
    order = np.random.default_rng(a.seed).permutation(len(starts))
    chunk = per_batch * 64                                              # within chunks, similar prompt lengths
    order = np.concatenate([o[np.argsort(starts[o, 3], kind="stable")] for o in np.array_split(order, max(1, len(order) // chunk))])
    (run / "config.json").write_text(json.dumps(dict(cc_run=str(cc_run), cc=cc_dir.name, models=info["models"],
                                                     players=players, starts=len(starts), rollouts=R, plies=a.plies,
                                                     window=a.window, temperature=a.temperature,
                                                     pgn_data=a.pgn_data, min_ply=a.min_ply, seed=a.seed), indent=1))

    for player in players:
        pm = models[info["models"].index(player)][0]
        name = models[info["models"].index(player)][1]
        counts = Counts(ck["latents"], dev, run / name, resume=True)
        done_starts = counts.meta.get("starts_done", 0)
        stats = dict(counts.meta.get("stats", dict(rollouts=0, positions=0, illegal=0, stopped_early=0)))
        if done_starts:
            print(f"{name}: resuming after {done_starts} starts", flush=True)
        gen = torch.Generator(device=dev).manual_seed(a.seed * 1000 + done_starts)
        t0, n_batches = time.time(), 0
        (run / name).mkdir(exist_ok=True)
        sample_f = open(run / name / "sample.txt", "w", encoding="utf-8") if done_starts == 0 else None
        for s in range(done_starts, len(order), per_batch):
            idx = order[s:s + per_batch]
            boards, prompts = [], []
            for i in idx:
                f, g, ply, end = (int(v) for v in starts[i])
                sans, _ = parse_movetext(corpus.text(f, g))
                boards.append(ev.board_of(sans[:ply]))
                prompts.append(corpus.ids(f, g, end + 1).tolist())
            pi = info["models"].index(player)
            mine = [L for m, L in sources if m == pi]
            buf, ends, pst, fails = play(pm, boards, prompts, R, a.plies, a.temperature, dev, gen, mine,
                                         graphs=not a.no_cuda_graphs)
            valid = ends >= -1
            x, plen = pad(prompts, dev)
            st = [pst if m == pi else states(mm, x, plen, R, buf, ends, [L for k, L in sources if k == m], dev)
                  for m, (mm, _) in enumerate(models)]
            xs = torch.stack([st[m][L] for m, L in sources], 2)          # (B, plies, sources, d)
            f, _, _ = cc.encode(xs.flatten(0, 1) * scales[None, :, None])
            act = (f > 0).view(len(buf), a.plies, -1)
            counts.add(act, valid.float(), R, a.window)
            stats["rollouts"] += len(buf)
            stats["positions"] += int(valid.sum())
            stats["illegal"] += fails
            stats["stopped_early"] += int((ends[:, -1] < -1).sum())
            if sample_f and s < done_starts + 4 * per_batch:
                for r in range(min(2 * R, len(buf))):
                    text = prompts[r // R] + buf[r, :max(0, int(ends[r].max())) + MAX_MOVE_CHARS + 1].tolist()
                    sample_f.write("".join(VOCAB[c] for c in text).rstrip() + "\n")
                sample_f.flush()
            n_batches += 1
            s_done = min(s + per_batch, len(order))
            if n_batches % a.save_every == 0 or s_done == len(order):
                counts.save(dict(player=player, starts_done=s_done, stats=stats))
            rate = (s_done - done_starts) * R / (time.time() - t0)
            print(f"\r  {name}: {s_done}/{len(order)} starts, {stats['rollouts']} rollouts, {rate:.0f} rollouts/s, "
                  f"illegal {stats['illegal'] / max(1, stats['rollouts']):.3f}/rollout, ETA {(len(order) - s_done) * R / max(rate, 1e-9) / 60:.0f} min   ",
                  end="", flush=True)
        if counts.meta.get("starts_done", 0) < len(order):
            counts.save(dict(player=player, starts_done=len(order), stats=stats))
        print(f"\n  {name}: done, {run / name}")
    return run


# ---------------------------------------------------------------- the graph

def edge_stats(folder, R, dev):
    t = {n: torch.from_numpy(np.load(folder / f"{n}.npy")).float().to(dev) for n in ("C", "X")}
    N = torch.from_numpy(np.load(folder / "onsets.npy")).float().to(dev)
    C = t["C"]
    E = (t["X"] - C) / (R - 1)
    C.fill_diagonal_(0)
    E.fill_diagonal_(0)
    return C, E, N


def top_edges(C, E, N, a):
    excess = C - E
    z = excess / (E + 1).sqrt()
    lift = (C + 1) / (E + 1)
    ok = (z >= a.z) & (lift >= a.lift) & (C >= a.min_count)
    zz = torch.where(ok, z, torch.full_like(z, -1))
    n = min(a.edges, int(ok.sum()))
    v, flat = zz.flatten().topk(n)
    i, j = flat // C.shape[1], flat % C.shape[1]
    rate = excess[i, j] / N[i].clamp_min(1)
    return [dict(i=int(a_), j=int(b_), C=float(C[a_, b_]), E=float(E[a_, b_]), lift=float(lift[a_, b_]),
                 rate=float(r_), z=float(z_)) for a_, b_, r_, z_ in zip(i.tolist(), j.tolist(), rate.tolist(), v.tolist())], int(ok.sum())


def diff_edges(sa, sb, a):
    """Edges whose excess rate (per onset of i) differs between the two players."""
    (Ca, Ea, Na), (Cb, Eb, Nb) = sa, sb
    ra, rb = (Ca - Ea) / Na.clamp_min(1)[:, None], (Cb - Eb) / Nb.clamp_min(1)[:, None]
    se = ((Ca + Ea + 1) / Na.clamp_min(1)[:, None] ** 2 + (Cb + Eb + 1) / Nb.clamp_min(1)[:, None] ** 2).sqrt()
    z = (ra - rb) / se
    ok = (z.abs() >= a.z) & ((Ca >= a.min_count) | (Cb >= a.min_count))
    zz = torch.where(ok, z.abs(), torch.full_like(z, -1))
    n = min(a.edges, int(ok.sum()))
    v, flat = zz.flatten().topk(n)
    i, j = flat // Ca.shape[1], flat % Ca.shape[1]
    return [dict(i=int(x), j=int(y), rate_A=float(ra[x, y]), rate_B=float(rb[x, y]), z=float(z[x, y]),
                 C_A=float(Ca[x, y]), C_B=float(Cb[x, y])) for x, y in zip(i.tolist(), j.tolist())], int(ok.sum())


def describe(cfg, nodes, n_examples=3):
    """Per latent: crosscoder relative norm, firing rate and its top positions as 'last moves -> move'."""
    cc_run = Path(cfg["cc_run"])
    lat = {}
    with open(cc_run / cfg["cc"] / "latents.jsonl", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["latent"] in nodes:
                lat[r["latent"]] = r
    info = json.loads((cc_run / "collect.json").read_text())
    corpus, rows = Corpus(info["folders"]), np.load(cc_run / "rows.npy", mmap_mode="r")
    out = {}
    for j in nodes:
        r = lat.get(j, dict(rel_norm=float("nan"), rate=0.0, top=[]))
        ex = []
        for i, v in r["top"][:n_examples]:
            b, nxt, _ = position(corpus, rows[i])
            ex.append(f"{last_moves(prompt(b), 6)} -> {nxt}")
        out[j] = dict(rel_norm=r["rel_norm"], rate=r["rate"], examples=ex)
    return out


def graph(a):
    run = Path(a.run)
    cfg = json.loads((run / "config.json").read_text())
    dev = ev.device(a.device)
    names = [m.split("/")[-1] for m in cfg["models"]]
    players = [n for n in names if (run / n / "C.npy").exists()]
    out = RESULTS / run.name
    out.mkdir(parents=True, exist_ok=True)
    R = cfg["rollouts"]
    views, found, meta = {}, {}, {}
    st = {}
    for n in players:
        st[n] = edge_stats(run / n, R, dev)
        views[n], found[n] = top_edges(*st[n], a)
        meta[n] = json.loads((run / n / "meta.json").read_text())
        print(f"{n}: {found[n]} edges pass, keeping {len(views[n])}", flush=True)
    if len(players) == 2:
        views["diff"], found["diff"] = diff_edges(st[players[0]], st[players[1]], a)
        print(f"diff: {found['diff']} edges pass, keeping {len(views['diff'])}", flush=True)
    del st
    nodes = sorted({e[k] for es in views.values() for e in es for k in ("i", "j")})
    print(f"describing {len(nodes)} latents", flush=True)
    desc = describe(cfg, set(nodes))

    for v, es in views.items():
        with open(out / f"edges-{v}.csv", "w", encoding="utf-8") as f:
            keys = list(es[0]) if es else ["i", "j"]
            f.write(",".join(keys) + "\n")
            for e in es:
                f.write(",".join(f"{e[k]:.6g}" if isinstance(e[k], float) else str(e[k]) for k in keys) + "\n")

    def label(j):
        d = desc[j]
        return f"latent {j} (r {d['rel_norm']:.2f}, fires {100 * d['rate']:.2f}%): " + " | ".join(d["examples"][:2])

    md = [f"# Concept graph, {run.name}", "",
          f"Self-play rollouts from {cfg['starts']} start positions x {R} rollouts x up to {cfg['plies']} plies at "
          f"T = {cfg['temperature']}, encoded with crosscoder {cfg['cc']} of {Path(cfg['cc_run']).name}. "
          f"Edge i -> j: an onset of i is followed by an onset of j within {cfg['window']} plies more often than in "
          f"sibling rollouts from the same start (z >= {a.z}, lift >= {a.lift}, count >= {a.min_count}).", ""]
    for n in players:
        s = meta[n]["stats"]
        md.append(f"- **{n}** playing itself: {s['rollouts']} rollouts, {s['illegal'] / max(1, s['rollouts']):.3f} illegal "
                  f"attempts per rollout, {100 * s['stopped_early'] / max(1, s['rollouts']):.1f}% ended early (game over or "
                  f"5 illegal attempts); {found[n]} edges pass.")
    if "diff" in views:
        md.append(f"- **diff**: {found['diff']} edges whose rate differs between the players (|z| >= {a.z}).")
    md.append("")
    for v, es in views.items():
        md += [f"## {v}: the {min(a.show, len(es))} strongest edges", ""]
        for e in es[:a.show]:
            extra = (f"rate {100 * e['rate_A']:.1f}% vs {100 * e['rate_B']:.1f}%, z {e['z']:.1f}" if v == "diff"
                     else f"lift {e['lift']:.2f}, +{100 * e['rate']:.1f}% per onset, z {e['z']:.0f}")
            md.append(f"- **{e['i']} -> {e['j']}** ({extra})  \n  {html.escape(label(e['i']))}  \n  -> {html.escape(label(e['j']))}")
        md.append("")
    (out / "summary.md").write_text("\n".join(md), encoding="utf-8")

    # GraphML: one node set, edge attributes per view
    g = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
         '<key id="rel" for="node" attr.name="rel_norm" attr.type="double"/>',
         '<key id="rate" for="node" attr.name="rate" attr.type="double"/>',
         '<key id="lab" for="node" attr.name="label" attr.type="string"/>',
         '<key id="view" for="edge" attr.name="view" attr.type="string"/>',
         '<key id="w" for="edge" attr.name="z" attr.type="double"/>',
         '<graph edgedefault="directed">']
    for j in nodes:
        g.append(f'<node id="n{j}"><data key="rel">{desc[j]["rel_norm"]:.4f}</data><data key="rate">{desc[j]["rate"]:.6f}</data>'
                 f'<data key="lab">{html.escape(label(j))}</data></node>')
    for v, es in views.items():
        for e in es:
            g.append(f'<edge source="n{e["i"]}" target="n{e["j"]}"><data key="view">{v}</data><data key="w">{e["z"]:.3f}</data></edge>')
    g += ["</graph>", "</graphml>"]
    (run / "graph.graphml").write_text("\n".join(g), encoding="utf-8")

    data = dict(nodes={j: dict(r=desc[j]["rel_norm"], rate=desc[j]["rate"], label=label(j)) for j in nodes},
                views={v: [[e["i"], e["j"], round(e["z"], 2)] for e in es[:a.html_edges]] for v, es in views.items()},
                A=names[0], B=names[1] if len(names) > 1 else "")
    page = f"""<!doctype html><meta charset="utf-8"><title>Concept graph</title>
<script src="https://unpkg.com/vis-network@9.1.9/standalone/umd/vis-network.min.js"></script>
<style>body{{margin:0;font:13px system-ui,sans-serif}}#bar{{padding:8px;border-bottom:1px solid #ccc}}#g{{height:calc(100vh - 44px)}}</style>
<div id="bar">view <select id="v"></select> &nbsp; colour: blue = only {html.escape(names[0])}, red = only {html.escape(data['B'])}, grey = shared;
arrows i &rarr; j: j turns on after i (diff view: grey = stronger when {html.escape(names[0])} plays, red = when {html.escape(data['B'])} plays). Hover a node for its top positions.</div><div id="g"></div>
<script>
const D = {json.dumps(data)};
const sel = document.getElementById("v");
for (const v of Object.keys(D.views)) sel.add(new Option(v, v));
function colour(r) {{ if (!(r >= 0)) return "#999"; const b = Math.round(255 * (1 - r)), rr = Math.round(255 * r);
  return Math.abs(r - 0.5) < 0.2 ? "#aaa" : `rgb(${{rr}},80,${{b}})`; }}
let net;
function draw() {{
  const es = D.views[sel.value], used = new Set();
  es.forEach(e => {{ used.add(e[0]); used.add(e[1]); }});
  const nodes = [...used].map(j => ({{id: j, label: String(j), title: D.nodes[j].label, color: colour(D.nodes[j].r),
                                     value: Math.sqrt(D.nodes[j].rate + 1e-6)}}));
  const edges = es.map(e => ({{from: e[0], to: e[1], value: Math.abs(e[2]), arrows: "to", title: "z " + e[2],
                              color: {{color: e[2] < 0 ? "#c33" : "#8899aa", opacity: 0.5}}}}));
  if (net) net.destroy();
  net = new vis.Network(document.getElementById("g"), {{nodes, edges}},
    {{physics: {{solver: "forceAtlas2Based", stabilization: {{iterations: 300}}}}, nodes: {{shape: "dot", scaling: {{min: 4, max: 24}}}},
      edges: {{scaling: {{min: 0.5, max: 4}}, smooth: false}}, interaction: {{hover: true}}}});
}}
sel.onchange = draw; draw();
</script>"""
    (run / "graph.html").write_text(page, encoding="utf-8")
    print(f"wrote {out / 'summary.md'}, {out}/edges-*.csv, {run / 'graph.graphml'} and {run / 'graph.html'}")


# ---------------------------------------------------------------- command line

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for cmd in ("rollout", "graph", "all"):
        p = sub.add_parser(cmd)
        p.add_argument("--device", default="auto", help="auto, cuda, mps or cpu")
        p.add_argument("--run", default=None, help="run folder (default runs/transcend/concepts/<crosscoder run>-<cc>)")
        if cmd in ("rollout", "all"):
            p.add_argument("--cc-run", default="runs/transcend/crosscoder/everything-3m", help="crosscoder run folder")
            p.add_argument("--cc", default="Lfinal", help="crosscoder in that run, e.g. Lfinal or L12")
            p.add_argument("--players", nargs="+", default=None, help="models that play (default: both crosscoder models)")
            p.add_argument("--pgn-data", nargs="+", default=FOLDERS, help="make_pgn_data.py folders for start positions")
            p.add_argument("--starts", type=int, default=125_000)
            p.add_argument("--rollouts", type=int, default=8, help="rollouts per start (>= 2: siblings are the control)")
            p.add_argument("--plies", type=int, default=16)
            p.add_argument("--window", type=int, default=4, help="plies after i's onset in which j's onset counts")
            p.add_argument("--temperature", type=float, default=1.0)
            p.add_argument("--min-ply", type=int, default=10)
            p.add_argument("--batch", type=int, default=1024, help="rollouts played at once")
            p.add_argument("--save-every", type=int, default=100, help="batches between saves (a rerun resumes)")
            p.add_argument("--no-cuda-graphs", action="store_true", help="decode eagerly (slower; for debugging)")
            p.add_argument("--seed", type=int, default=0)
        if cmd in ("graph", "all"):
            p.add_argument("--z", type=float, default=6.0)
            p.add_argument("--lift", type=float, default=1.5)
            p.add_argument("--min-count", type=int, default=30)
            p.add_argument("--edges", type=int, default=20_000, help="edges kept per view")
            p.add_argument("--html-edges", type=int, default=3000, help="edges drawn per view in graph.html")
            p.add_argument("--show", type=int, default=40, help="edges listed per view in summary.md")
    a = ap.parse_args()
    if a.cmd in ("rollout", "all"):
        if a.rollouts < 2:
            sys.exit("--rollouts must be at least 2 (sibling rollouts are the control)")
        a.run = str(rollout(a))
    if a.cmd in ("graph", "all"):
        if not a.run:
            sys.exit("--run is required")
        graph(a)


if __name__ == "__main__":
    main()
