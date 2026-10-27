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

examples For the graph's paths, example rollouts: replays rollouts from fresh starts (same models
         and settings) until each path has --per-edge rollouts in which it happens, then redraws
         the graph; hovering an arrow shows them (the two positions and the moves between).
         -> results/transcend/concepts/<run>/path_examples.json

score    Stockfish (skill.py) on every move of the example rollouts, from i's position to after
         j's move: the change in win chances for the side to move at i (the side that takes the
         path), each side's average loss per move, and the skill facts of the moves at i and j
         (only move, deep move, sound sacrifice, rare for 1100s via Maia-2, ...); then redraws the
         graph, whose edge cards and summary.md table show them.
         -> results/transcend/concepts/<run>/path_scores.json

graph    Edge statistics: excess = C - E, lift = (C + 1) / (E + 1), z = excess / sqrt(E + 1),
         rate = excess / N[i] (how much more likely j's onset is within the window, per onset of
         i). A path passes with a player at z >= --z, lift >= --lift, C >= --min-count. Latents are
         nearly all shared between the models, so the graphs split PATHS, not latents: "only A"
         paths pass when A plays and are absent when B plays (z < --absent, rates differ at
         z >= --z), "only B" the reverse, "both" pass with both; the --edges strongest of each.
         Only latents with >= --min-onsets onsets with each player (both models reach the
         concept) and firing in <= --max-rate of positions (no hubs) take part. Nodes carry the
         crosscoder's relative decoder norm, the latent's scored explanation (explain.py, when it
         has been run), its top positions and the facts (predicates.py) those have in common.
         -> results/transcend/concepts/<run>/edges-only-<model>.csv, edges-both.csv, summary.md;
            <run>/graph.graphml (for Gephi) and <run>/graph.html (interactive, the three views).

modes    The graph summarised: truncated SVD (--modes components) of the excess-rate matrix
         r[i, j] = (C - E) / (N[i] + --prior), per player and as the diff (second player minus
         first), over latents that fire in <= --max-rate of positions. Component k is a flow
         pattern: source latents (u_k) whose onsets lead to onsets of target latents (v_k); each
         is listed with its strongest real edges and the rates under both players.
         -> results/transcend/concepts/<run>/modes.md, modes.json; <run>/modes.html (one card per
            mode, the latents' top positions drawn as boards).

    python transcend/concepts.py modes   --run runs/transcend/concepts/everything-3m-Lfinal
    python transcend/concepts.py score   --run runs/transcend/concepts/everything-3m-Lfinal   # after examples
"""
import argparse
import html
import json
import os
import re
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import chess
import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parent))          # transcend/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))      # chess_beyond/
import paths
import eval as ev                                                 # load, board_of, device
from crosscoder import RESULTS as CC_RESULTS
from crosscoder import FOLDERS, Corpus, CrossCoder, pick_positions, position
from pgn_model import BOS, MAX_MOVE_CHARS, MAX_TRIES, SPACE, VOCAB, encode, prompt
from pgn_probe import parse_movetext
import skill
from predicates import NAMES, TEXT, features
from pages import BOARD_CSS, BOARD_DEFS, BOARD_JS, MOVE_HEAD
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


def load_coder(cc_run, cc, dev):
    """The crosscoder, the states it reads ((model, layer) sources), its scales and its two models, in order."""
    cc_run = Path(cc_run)
    cc_dir = cc_run / ("cc-" + cc.removeprefix("cc-"))
    info = json.loads((cc_run / "collect.json").read_text())
    ck = torch.load(cc_dir / "cc.pt", map_location="cpu", weights_only=False)
    sources = [tuple(s) for s in ck["sources"]]
    coder = CrossCoder(len(sources), ck["d"], ck["latents"], ck["k"]).to(dev)
    coder.load_state_dict(ck["state"])
    models = [ev.load(m, dev) for m in info["models"]]
    return cc_run, cc_dir, info, ck, sources, coder, ck["scales"].to(dev), models


def activations(models, sources, coder, scales, pi, boards, prompts, R, plies, T, dev, gen, graphs):
    """Model pi plays R rollouts from each start; every position is read by both models and encoded.
    -> continuation characters, ends (see play), (S*R, plies, latents) active, illegal attempts."""
    buf, ends, pst, fails = play(models[pi][0], boards, prompts, R, plies, T, dev, gen,
                                 [L for m, L in sources if m == pi], graphs=graphs)
    x, plen = pad(prompts, dev)
    st = [pst if m == pi else states(mm, x, plen, R, buf, ends, [L for k, L in sources if k == m], dev)
          for m, (mm, _) in enumerate(models)]
    xs = torch.stack([st[m][L] for m, L in sources], 2)          # (B, plies, sources, d)
    f, _, _ = coder.encode(xs.flatten(0, 1) * scales[None, :, None])
    return buf, ends, (f > 0).view(len(buf), plies, -1), fails


def rollout(a):
    dev = ev.device(a.device)
    torch.backends.cuda.matmul.allow_tf32 = True
    cc_run, cc_dir, info, ck, sources, cc, scales, models = load_coder(a.cc_run, a.cc, dev)
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
            buf, ends, act, fails = activations(models, sources, cc, scales, info["models"].index(player), boards,
                                                prompts, R, a.plies, a.temperature, dev, gen, not a.no_cuda_graphs)
            valid = ends >= -1
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


# ---------------------------------------------------------------- example rollouts for the graph's paths

def path_example(board, prompt_ids, cont, ends, ti, tj):
    """One rollout as the graph shows it: the position at ply ti (where i turns on) and at ply tj (j),
    each with the move played from it, and the moves from the start to tj with move numbers."""
    pre = "".join(VOCAB[c] for c in prompt_ids)
    n0 = len(parse_movetext(pre)[0])
    n = max(0, int(ends.max()) + MAX_MOVE_CHARS + 1)
    sans = parse_movetext(pre + "".join(VOCAB[c] for c in cont[:n].tolist()))[0][n0:]
    b, moves = board.copy(), []
    for s in sans:
        try:
            mv = b.parse_san(s)
        except ValueError:
            break
        moves.append(mv)
        b.push(mv)
    if tj > len(moves):
        return None
    b, line, at = board.copy(), [], {}
    for k in range(tj + 1):
        at[k] = (b.fen(), moves[k].uci() if k < len(moves) else "")
        if k == len(moves):
            break
        num = f"{b.fullmove_number}." if b.turn == chess.WHITE else (f"{b.fullmove_number}..." if k == 0 else "")
        line.append([num + b.san(moves[k]), "i" if k == ti else "j" if k == tj else ""])
        b.push(moves[k])
    return dict(start=last_moves(prompt(board), 6), fen_i=at[ti][0], uci_i=at[ti][1], fen_j=at[tj][0],
                uci_j=at[tj][1], ti=ti, tj=tj, line=line)


def examples(a):
    """Replays rollouts (fresh starts, same settings) until each of the graph's paths has --per-edge
    rollouts where it happens: i turns on at some ply and j within the window after it."""
    run = Path(a.run)
    cfg = json.loads((run / "config.json").read_text())
    dev = ev.device(a.device)
    torch.backends.cuda.matmul.allow_tf32 = True
    names = [m.split("/")[-1] for m in cfg["models"]]
    A, B = names
    res = RESULTS / run.name
    want = {n: set() for n in names}
    for v, who in ((f"only {A}", [A]), (f"only {B}", [B]), ("both", [A, B])):
        p = res / f"edges-{v.replace(' ', '-')}.csv"
        if not p.exists():
            sys.exit(f"{p} is missing: run graph first")
        for line in p.read_text(encoding="utf-8").splitlines()[1:]:
            i, j = (int(float(x)) for x in line.split(",")[:2])
            for n in who:
                want[n].add((i, j))
    _, _, info, ck, sources, coder, scales, models = load_coder(cfg["cc_run"], cfg["cc"], dev)
    R, P, w = cfg["rollouts"], cfg["plies"], cfg["window"]
    corpus = Corpus(cfg["pgn_data"])
    ctx = min(m.ctx for m, _ in models) - room(P)
    starts = pick_positions(corpus, a.ex_starts, 1, cfg["min_ply"], ctx, cfg["seed"] + 1)   # not the counted starts
    per_batch = max(1, a.batch // R)
    out_path = res / "path_examples.json"
    # saved after each player, so a stopped run keeps the players it finished; "_done" marks them
    found = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else {}
    found.setdefault("_done", {})
    for n in names:
        if found["_done"].get(n, 0) >= a.per_edge:
            print(f"  {n}: done in an earlier run ({out_path})")
            continue
        pi = names.index(n)
        pairs = sorted(want[n])
        I = torch.tensor([p[0] for p in pairs], device=dev)
        J = torch.tensor([p[1] for p in pairs], device=dev)
        U, inv = torch.unique(torch.cat([I, J]), return_inverse=True)
        Iu, Ju = inv[:len(pairs)], inv[len(pairs):]
        need = [a.per_edge] * len(pairs)
        got = found[n] = {}
        gen = torch.Generator(device=dev).manual_seed(cfg["seed"] * 1000 + 7)
        t0, last_new, filled = time.time(), 0, 0
        for s in range(0, len(starts), per_batch):
            boards, prompts = [], []
            for f, g, ply, end in (tuple(int(v) for v in r) for r in starts[s:s + per_batch]):
                boards.append(ev.board_of(parse_movetext(corpus.text(f, g))[0][:ply]))
                prompts.append(corpus.ids(f, g, end + 1).tolist())
            buf, ends, act, _ = activations(models, sources, coder, scales, pi, boards, prompts, R, P,
                                            cfg["temperature"], dev, gen, not a.no_cuda_graphs)
            act = act[:, :, U] & (ends >= -1)[..., None]
            on = act[:, 1:] & ~act[:, :-1]                    # on[:, t]: onset at ply t + 1
            win = torch.zeros_like(on)
            for d in range(1, w + 1):
                win[:, :-d] |= on[:, d:]
            hit = on[:, :, Iu] & win[:, :, Ju]                # (rollouts, plies, paths)
            open_ = torch.tensor([k > 0 for k in need], device=dev)
            for e in (hit.flatten(0, 1).any(0) & open_).nonzero().squeeze(1).tolist():
                seen = set()
                for b, t in hit[:, :, e].nonzero().tolist():
                    if need[e] == 0 or b in seen:
                        continue
                    seen.add(b)
                    d = next(d for d in range(1, w + 1) if t + d < on.shape[1] and bool(on[b, t + d, Ju[e]]))
                    ex = path_example(boards[b // R], prompts[b // R], buf[b], ends[b], t + 1, t + d + 1)
                    if ex:
                        got.setdefault(f"{pairs[e][0]}-{pairs[e][1]}", []).append(ex)
                        need[e] -= 1
            full = sum(k == 0 for k in need)
            done = min(s + per_batch, len(starts))
            print(f"\r  {n}: {done}/{len(starts)} starts, {full}/{len(pairs)} paths have {a.per_edge} examples, "
                  f"{sum(1 for k in need if k < a.per_edge)} at least one, {(time.time() - t0) / 60:.1f} min   ",
                  end="", flush=True)
            if full == len(pairs):
                break
            examples_now = sum(a.per_edge - k for k in need)
            if examples_now > filled:
                filled, last_new = examples_now, done
            elif done - last_new >= a.stall:              # the paths left are too rare to be worth the wait
                print(f"\n  {n}: no new example in the last {a.stall} starts; moving on", end="")
                break
        print()
        found["_done"][n] = a.per_edge
        out_path.write_text(json.dumps(found), encoding="utf-8")
        print(f"  saved {out_path}", flush=True)
    print(f"wrote {out_path}; redrawing the graph with them")
    graph(a)


# ---------------------------------------------------------------- engine scores for the paths' example rollouts

_annotator = None


def _score_init(depth):
    global _annotator
    _annotator = skill.Annotator(depth=depth)


def _replay(x):
    """An example's positions from i's (ply ti) to just after the move at j (ply tj): (board, move) pairs."""
    b, out = chess.Board(x["fen_i"]), []
    for tok, _ in x["line"][x["ti"]:x["tj"] + 1]:
        san = re.sub(r"^\d+\.(\.\.)?", "", tok)
        mv = b.parse_san(san)
        out.append((b.copy(stack=False), mv))
        b.push(mv)
    return out, b


def _score(job):
    """Stockfish on every move of one example: win chances for the side to move at i (the path's
    "taker") from i's position to after j's move, each move's loss, and the moves at i and j."""
    key, k, x = job
    try:
        steps, end = _replay(x)
    except ValueError:
        return key, k, None
    taker = steps[0][0].turn
    ann = [_annotator.annotate(b, mv) for b, mv in steps]
    if any(e is None for e in ann):
        return key, k, None
    pov = lambda wp, turn: wp if turn == taker else 100 - wp
    wp_i = pov(ann[0]["wp"], taker)
    last = ann[-1]
    wp_end = pov(last["wp"] - last["loss"], steps[-1][0].turn)          # after the move at j
    losses = [(b.turn == taker, e["loss"]) for (b, _), e in zip(steps, ann)]
    return key, k, dict(k=k, wp_i=wp_i, wp_end=wp_end, gain=wp_end - wp_i,
                        loss_taker=float(np.mean([l for t, l in losses if t] or [0])),
                        loss_other=float(np.mean([l for t, l in losses if not t] or [0])),
                        e_i=ann[0], e_j=last, fen_i=steps[0][0].fen(), fen_j=steps[-1][0].fen(),
                        j_mover="taker" if steps[-1][0].turn == taker else "other")


def score_paths(a):
    """Stockfish (and Maia-2) on the paths' example rollouts (concepts.py examples): for each example,
    does the path gain or lose for the side that takes it, how well is each move played, and what
    kind of moves start and end it (skill.py's facts). -> results/.../<run>/path_scores.json"""
    run = Path(a.run)
    res = RESULTS / run.name
    pe = res / "path_examples.json"
    if not pe.exists():
        sys.exit(f"{pe} is missing: run examples first")
    found = json.loads(pe.read_text(encoding="utf-8"))
    jobs = [((n, key), k, x) for n, paths in found.items() if n != "_done"
            for key, xs in paths.items() for k, x in enumerate(xs)]
    print(f"{len(jobs)} example rollouts; Stockfish depth {a.depth} on every move from i's position to j's", flush=True)
    out, t0 = {}, time.time()
    with Pool(a.workers, initializer=_score_init, initargs=(a.depth,)) as pool:
        for d, ((n, key), k, r) in enumerate(pool.imap_unordered(_score, jobs, chunksize=4), 1):
            if r is not None:
                out.setdefault(n, {}).setdefault(key, {})[k] = r
            if d % 20 == 0 or d == len(jobs):
                rate = d / (time.time() - t0)
                print(f"\r  {d}/{len(jobs)} examples, {rate:.1f}/s, {(len(jobs) - d) / max(rate, 1e-9) / 60:.0f} min left   ",
                      end="", flush=True)
    print()
    # Maia-2 on the moves at i and j: how likely 1100s and 2000+ players are to play them
    rs = [r for paths in out.values() for xs in paths.values() for r in xs.values()]
    pairs = []
    for r in rs:
        for fen, e in ((r["fen_i"], r["e_i"]), (r["fen_j"], r["e_j"])):
            pairs.append((chess.Board(fen), chess.Move.from_uci(e["move"]), chess.Move.from_uci(e["best"])))
    print("  Maia-2 on the moves at i and j", flush=True)
    maia = skill.maia_probs(pairs) if pairs else []
    for t, r in enumerate(rs):
        r["facts_i"] = [n for n, v in zip(skill.NAMES, skill.facts(r["e_i"], maia[2 * t])) if v]
        r["facts_j"] = [n for n, v in zip(skill.NAMES, skill.facts(r["e_j"], maia[2 * t + 1])) if v]
        r["maia_i"], r["maia_j"] = [float(v) for v in maia[2 * t]], [float(v) for v in maia[2 * t + 1]]
    out = {n: {key: [xs[k] for k in sorted(xs)] for key, xs in paths.items()} for n, paths in out.items()}
    (res / "path_scores.json").write_text(json.dumps(dict(depth=a.depth, scores=out)), encoding="utf-8")
    print(f"wrote {res / 'path_scores.json'}; redrawing the graph with them")
    graph(a)


# ---------------------------------------------------------------- the graph

def edge_stats(folder, R):
    """Co-onset counts C, their expectation E and onsets N, kept in RAM: the latents x latents
    matrices of two players (and the scoring's temporaries) don't fit on the card together."""
    C = torch.from_numpy(np.load(folder / "C.npy")).float()
    E = (torch.from_numpy(np.load(folder / "X.npy")).float() - C) / (R - 1)
    N = torch.from_numpy(np.load(folder / "onsets.npy")).float()
    C.fill_diagonal_(0)
    E.fill_diagonal_(0)
    return C, E, N


def chunked_top(score, L, k, dev, rows=1024):
    """Top-k flat indices of an L x L score, scored --rows rows at a time on the GPU.
    score(s, e) returns (score, passes) for rows s:e; returns (flat indices, number passing)."""
    vals, idx, passing = [], [], 0
    for s in range(0, L, rows):
        sc, ok = score(s, min(s + rows, L))
        passing += int(ok.sum())
        v, f = torch.where(ok, sc, torch.full_like(sc, -1)).flatten().topk(min(k, sc.numel()))
        vals.append(v.cpu()); idx.append(f.cpu() + s * L)
    v, o = torch.cat(vals).topk(min(k, passing))
    return torch.cat(idx)[o], passing


def path_edges(sa, sb, alive, kind, a, dev):
    """Paths i -> j by who takes them. kind "A": strong when the first player plays (z >= --z, lift,
    count) and absent when the second does (z < --absent, and the two rates differ by z >= --z, so
    "absent" is measured, not just unseen); "B" the reverse; "both": strong with both players.
    Only latents in alive (seen often enough with both players, not hubs) take part."""
    (Ca, Ea, Na), (Cb, Eb, Nb) = sa, sb
    L = Ca.shape[1]
    na, nb = Na.clamp_min(1), Nb.clamp_min(1)

    def score(s, e):
        ca, ea, cb, eb = (t[s:e].to(dev) for t in (Ca, Ea, Cb, Eb))
        ma, mb = na[s:e, None].to(dev), nb[s:e, None].to(dev)
        za, zb = (ca - ea) / (ea + 1).sqrt(), (cb - eb) / (eb + 1).sqrt()
        oka = (za >= a.z) & ((ca + 1) / (ea + 1) >= a.lift) & (ca >= a.min_count)
        okb = (zb >= a.z) & ((cb + 1) / (eb + 1) >= a.lift) & (cb >= a.min_count)
        dz = ((ca - ea) / ma - (cb - eb) / mb) / ((ca + ea + 1) / ma ** 2 + (cb + eb + 1) / mb ** 2).sqrt()
        pair = (alive[s:e, None] & alive[None, :]).to(dev)
        if kind == "A":
            return za, pair & oka & (zb < a.absent) & (dz >= a.z)
        if kind == "B":
            return zb, pair & okb & (za < a.absent) & (-dz >= a.z)
        return torch.minimum(za, zb), pair & oka & okb
    flat, passing = chunked_top(score, L, a.edges, dev)
    out = []
    for x, y in zip((flat // L).tolist(), (flat % L).tolist()):
        e = dict(i=x, j=y)
        for tag, (C, E, N) in (("A", sa), ("B", sb)):
            c, ex = float(C[x, y]), float(E[x, y])
            e.update({f"C_{tag}": c, f"E_{tag}": ex, f"rate_{tag}": (c - ex) / max(float(N[x]), 1.0),
                      f"z_{tag}": (c - ex) / (ex + 1) ** 0.5})
        e["z"] = e["z_A"] if kind == "A" else e["z_B"] if kind == "B" else min(e["z_A"], e["z_B"])
        out.append(e)
    return out, passing


def shared_facts(fact_rows):
    """What a latent's top positions have in common: predicates true in at least half of them."""
    if not fact_rows:
        return ""
    share = np.mean(fact_rows, 0)
    common = sorted(((s, n) for n, s in zip(NAMES, share) if s >= 0.5), reverse=True)
    if not common:
        return f"its top {len(fact_rows)} positions share no fact"
    return f"its top {len(fact_rows)} positions: " + "; ".join(f"{TEXT[n]} ({100 * s:.0f}%)" for s, n in common)


def explanations(cfg):
    """explain.py's scored explanations for this crosscoder, if it has been run: {latent: record}."""
    p = CC_RESULTS / Path(cfg["cc_run"]).name / cfg["cc"] / "explanations.jsonl"
    if not p.exists():
        return {}
    with open(p, encoding="utf-8") as f:
        return {r["latent"]: r for r in map(json.loads, f)}


def describe(cfg, nodes, n_examples=3):
    """Per latent: crosscoder relative norm, firing rate, its scored explanation (explain.py), its top
    positions as 'last moves -> move' (boards for the first n_examples) and the facts they share."""
    cc_run = Path(cfg["cc_run"])
    lat = {}
    with open(cc_run / cfg["cc"] / "latents.jsonl", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["latent"] in nodes:
                lat[r["latent"]] = r
    expl = explanations(cfg)
    info = json.loads((cc_run / "collect.json").read_text())
    corpus, rows = Corpus(info["folders"]), np.load(cc_run / "rows.npy", mmap_mode="r")
    out = {}
    for j in nodes:
        r = lat.get(j, dict(rel_norm=float("nan"), rate=0.0, top=[]))
        ex, boards, fr = [], [], []
        for k, (i, v) in enumerate(r["top"]):
            b, nxt, _ = position(corpus, rows[i])
            try:
                mv = b.parse_san(nxt)
            except ValueError:
                mv = None
            fr.append(features(b, mv))
            if k < n_examples:
                ex.append(f"{last_moves(prompt(b), 6)} -> {nxt}")
                boards.append([b.fen(), last_moves(prompt(b), 6), nxt, mv.uci() if mv else ""])   # drawn in the pages
        out[j] = dict(rel_norm=r["rel_norm"], rate=r["rate"], examples=ex, boards=boards, why=shared_facts(fr),
                      expl=expl.get(j))
    return out


def short(d):
    """A latent in one line, for summary.md and GraphML."""
    e = d.get("expl")
    if e and e["status"] in ("explained", "weak"):
        return f"{e['status']}: {e['explanation']} (F1 {e['f1']:.2f})"
    return d["why"]


# A path's two positions, i's and j's, can have different sides to move; these pairs swap when they do,
# so changes are always told from the side to move at i ("we").
SWAP = dict(p for a_, b_ in (("our_piece_hanging", "their_piece_hanging"),
                             ("our_piece_attacked_by_lower", "their_piece_attacked_by_lower"),
                             ("our_piece_pinned", "their_piece_pinned"), ("we_can_castle", "they_can_castle"),
                             ("our_king_exposed", "their_king_exposed"), ("our_back_rank_weak", "their_back_rank_weak"),
                             ("we_have_a_passed_pawn", "they_have_a_passed_pawn"),
                             ("we_have_an_advanced_passer", "they_have_an_advanced_passer"),
                             ("material_up", "material_down")) for p in ((a_, b_), (b_, a_)))
POSITION_FACTS = [n for n in NAMES if not n.startswith("move_") and n not in
                  ("white_to_move", "they_just_captured", "they_just_checked", "in_check", "we_have_mate_in_1",
                   "they_threaten_mate", "we_have_a_check", "we_have_a_fork")]


def transition(x):
    """What changed between a path example's two positions (concepts.py examples), and the two moves."""
    def at(fen, uci):
        b = chess.Board(fen)
        return dict(zip(NAMES, features(b, chess.Move.from_uci(uci) if uci else None))), b.turn
    fi, ti = at(x["fen_i"], x["uci_i"])
    fj, tj = at(x["fen_j"], x["uci_j"])
    same = ti == tj
    fj_ours = {n: fj[SWAP.get(n, n) if not same else n] for n in POSITION_FACTS}
    moves = lambda f: [TEXT[n].removeprefix("the move ") for n in NAMES if n.startswith("move_") and f[n]
                       and n not in ("move_" + p for p in ("pawn", "knight", "bishop", "rook", "queen", "king"))]
    return dict(appear=[TEXT[n] for n in POSITION_FACTS if fj_ours[n] and not fi[n]],
                vanish=[TEXT[n] for n in POSITION_FACTS if fi[n] and not fj_ours[n]],
                move_i=moves(fi), move_j=moves(fj), j_mover="we" if same else "they")


def slim(r):
    """The parts of a path_scores.json record the page shows."""
    if not r:
        return None
    return {k: r[k] for k in ("wp_i", "wp_end", "gain", "loss_taker", "loss_other", "facts_i", "facts_j", "j_mover")}


def path_summary(rs):
    """A path's engine scores over its example rollouts: mean win-% change for the taker, mean loss per
    move by side, and the share of examples with each skill fact at the move at i and at j."""
    if not rs:
        return None
    m = lambda k: float(np.mean([r[k] for r in rs]))
    st = dict(n=len(rs), wp_i=m("wp_i"), wp_end=m("wp_end"), gain=m("gain"), loss_taker=m("loss_taker"),
              loss_other=m("loss_other"))
    for f in skill.NAMES:
        st["i_" + f] = float(np.mean([f in r["facts_i"] for r in rs]))
        st["j_" + f] = float(np.mean([f in r["facts_j"] for r in rs]))
    return st


def graph(a):
    run = Path(a.run)
    cfg = json.loads((run / "config.json").read_text())
    dev = ev.device(a.device)
    names = [m.split("/")[-1] for m in cfg["models"]]
    players = [n for n in names if (run / n / "C.npy").exists()]
    if len(players) != 2:
        sys.exit(f"graph compares two players; found rollouts for {players}")
    A, B = players
    out = RESULTS / run.name
    out.mkdir(parents=True, exist_ok=True)
    R = cfg["rollouts"]
    st = {n: edge_stats(run / n, R) for n in players}
    meta = {n: json.loads((run / n / "meta.json").read_text()) for n in players}
    L = st[A][0].shape[0]
    rate = latent_rates(cfg)
    fire = torch.tensor([rate.get(j, 0.0) for j in range(L)])
    alive = (fire <= a.max_rate) & (st[A][2] >= a.min_onsets) & (st[B][2] >= a.min_onsets)
    print(f"{int(alive.sum())} of {L} latents take part: firing in <= {100 * a.max_rate:g}% of positions, "
          f">= {a.min_onsets} onsets with each player", flush=True)
    titles = {"A": f"only {A}", "B": f"only {B}", "both": "both"}
    views, found = {}, {}
    for kind, v in titles.items():
        views[v], found[v] = path_edges(st[A], st[B], alive, kind, a, dev)
        print(f"{v}: {found[v]} paths pass, keeping {len(views[v])}", flush=True)
    del st
    nodes = sorted({e[k] for es in views.values() for e in es for k in ("i", "j")})
    print(f"describing {len(nodes)} latents", flush=True)
    desc = describe(cfg, set(nodes))

    # Example rollouts per path (concepts.py examples), under the player(s) each view is about
    pe, ps = out / "path_examples.json", out / "path_scores.json"
    found_ex = json.loads(pe.read_text(encoding="utf-8")) if pe.exists() else {}
    scores = json.loads(ps.read_text(encoding="utf-8"))["scores"] if ps.exists() else {}
    score_of = {(n, key, r["k"]): r for n, sp in scores.items() for key, rs in sp.items() for r in rs}
    paths, path_stats = {}, {}
    for (kind, v), who in zip(titles.items(), ([A], [B], [A, B])):
        keys = {f"{e['i']}-{e['j']}" for e in views[v]}
        paths[v] = {}
        for n in who:
            for key, xs in found_ex.get(n, {}).items():
                if key in keys:
                    paths[v].setdefault(key, []).extend(
                        dict(x, player=n, change=transition(x), score=slim(score_of.get((n, key, k))))
                        for k, x in enumerate(xs))
        path_stats[v] = {key: path_summary([x["score"] for x in xs if x["score"]]) for key, xs in paths[v].items()}

    slug = lambda v: v.replace(" ", "-")
    for v, es in views.items():
        with open(out / f"edges-{slug(v)}.csv", "w", encoding="utf-8") as f:
            keys = list(es[0]) if es else ["i", "j"]
            f.write(",".join(keys) + "\n")
            for e in es:
                f.write(",".join(f"{e[k]:.6g}" if isinstance(e[k], float) else str(e[k]) for k in keys) + "\n")

    def label(j):
        d = desc[j]
        return f"latent {j} (r {d['rel_norm']:.2f}, fires {100 * d['rate']:.2f}%; {short(d)}): " + " | ".join(d["examples"][:2])

    md = [f"# Concept paths, {run.name}", "",
          f"Self-play rollouts from {cfg['starts']} start positions x {R} rollouts x up to {cfg['plies']} plies at "
          f"T = {cfg['temperature']}, encoded with crosscoder {cfg['cc']} of {Path(cfg['cc_run']).name}. "
          f"Path i -> j: an onset of i is followed by an onset of j within {cfg['window']} plies more often than in "
          f"sibling rollouts from the same start (z >= {a.z}, lift >= {a.lift}, count >= {a.min_count}). "
          f"**only X**: the path passes when X plays, and when the other model plays it is absent (z < {a.absent}) "
          f"and its rate differs (z >= {a.z}). **both**: it passes with both. Latents taking part fire in <= "
          f"{100 * a.max_rate:g}% of positions and have >= {a.min_onsets} onsets with each player, so every concept "
          "in a path comes up with both models; what differs is whether one leads to the other.", ""]
    for n in players:
        s = meta[n]["stats"]
        md.append(f"- **{n}** playing itself: {s['rollouts']} rollouts, {s['illegal'] / max(1, s['rollouts']):.3f} illegal "
                  f"attempts per rollout, {100 * s['stopped_early'] / max(1, s['rollouts']):.1f}% ended early (game over or "
                  f"5 illegal attempts).")
    for v in views:
        md.append(f"- **{v}**: {found[v]} paths pass, {len(views[v])} kept.")
    if any(d.get("expl") for d in desc.values()):
        # the thesis check: are the concepts on these paths ones explain.py could name?
        md += ["", "Latents on the kept paths with a scored explanation (explain.py: explained = held-out F1 >= 0.5):", ""]
        for v, es in views.items():
            ls = {e[k] for e in es for k in ("i", "j")}
            st = [(desc[j].get("expl") or {}).get("status", "none") for j in ls]
            md.append(f"- **{v}**: {len(ls)} latents, {sum(x == 'explained' for x in st)} explained, "
                      f"{sum(x == 'weak' for x in st)} weak, {sum(x == 'unexplained' for x in st)} unexplained, "
                      f"{sum(x in ('too rare', 'none') for x in st)} not scored")
    md.append("")
    if scores:
        md += ["## What the paths do, by Stockfish (concepts.py score)", "",
               "Per path, over its example rollouts: the change in win chances for the side to move at i (the side "
               "that takes the path), from i's position to after the move at j; the average win-% points each "
               "side's moves lost; and how often the move at i is the engine's best, the only good move, a deep "
               "move, a sound sacrifice, or one 1100-level players rarely play.", "",
               "| paths | with scores | mean gain for the taker | taker's loss per move | other side's | move at i: best / only / deep / sacrifice / rare for 1100 |",
               "| --- | --- | --- | --- | --- | --- |"]
        for v in views:
            st = [x for x in path_stats[v].values() if x]
            if st:
                m = lambda k: np.mean([x[k] for x in st])
                md.append(f"| {v} | {len(st)} | {m('gain'):+.1f} | {m('loss_taker'):.1f} | {m('loss_other'):.1f} | "
                          + " / ".join(f"{100 * m('i_' + f):.0f}%" for f in ("move_best", "move_only", "move_deep",
                                                                            "move_sound_sacrifice", "move_rare_for_1100")) + " |")
        md.append("")
    for v, es in views.items():
        md += [f"## {v}: the {min(a.show, len(es))} strongest paths", ""]
        for e in es[:a.show]:
            extra = f"+{100 * e['rate_A']:.1f}% per onset with {A} (z {e['z_A']:.1f}), +{100 * e['rate_B']:.1f}% with {B} (z {e['z_B']:.1f})"
            st = path_stats.get(v, {}).get(f"{e['i']}-{e['j']}") if scores else None
            if st:
                extra += (f"; Stockfish over {st['n']} rollouts: {st['gain']:+.1f} win-% for the taker, its moves lose "
                          f"{st['loss_taker']:.1f}, the other side's {st['loss_other']:.1f}")
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

    data = dict(nodes={j: dict(r=desc[j]["rel_norm"], rate=desc[j]["rate"], ex=desc[j]["boards"], why=desc[j]["why"],
                              expl=desc[j]["expl"]) for j in nodes}, paths=paths, path_stats=path_stats,
                skill_text=skill.SHORT, have_examples=bool(found_ex),
                views={v: [[e["i"], e["j"], round(e["z"], 2), round(e["rate_A"], 4), round(e["rate_B"], 4)]
                           for e in es[:a.html_edges]] for v, es in views.items()},
                found=found, A=A, B=B)
    # Cards (boards, explanations, rollouts, engine scores) shared by graph.html and graph3d.html
    cards_css = f""".pair{{display:flex;gap:10px}}.cap{{font-size:12px;text-align:center}}.mi{{background:#cfe0ff;padding:0 2px}}.mj{{background:#ffd5cf;padding:0 2px}}
#tip{{position:fixed;display:none;max-width:560px;max-height:90vh;overflow-y:auto;background:#fff;border:1px solid #999;
border-radius:6px;padding:8px;box-shadow:0 2px 10px rgba(0,0,0,.25);z-index:10}}#tip.pinned{{border:2px solid #258}}
{BOARD_CSS}"""
    cards_js = f"""function colour(r) {{ if (!(r >= 0)) return "#999"; const b = Math.round(255 * (1 - r)), rr = Math.round(255 * r);
  return Math.abs(r - 0.5) < 0.1 ? "#aaa" : `rgb(${{rr}},80,${{b}})`; }}
{BOARD_JS}
let net, frozen = true, pinned = false;
const pc = x => (x >= 0 ? "+" : "") + (100 * x).toFixed(1) + "%";
function edgeHTML(id) {{
  const [i, j] = id.split("-"), e = D.views[sel.value].find(e => `${{e[0]}}-${{e[1]}}` === id);
  let h = `<b>${{i}} &rarr; ${{j}}</b>: chance that ${{j}} turns on within {cfg['window']} plies of ${{i}}, above sibling
    rollouts: ${{pc(e[3])}} with ${{D.A}}, ${{pc(e[4])}} with ${{D.B}}
    <div><span class="mi">${{i}}</span></div>${{explHTML(D.nodes[i], true)}}<div><span class="mj">${{j}}</span></div>${{explHTML(D.nodes[j], true)}}`;
  const st = (D.path_stats[sel.value] || {{}})[id];
  if (st) h += `<div class="why" style="border-left:4px solid ${{st.gain >= 0 ? "#1d7a2e" : "#b3261e"}}"><b>Stockfish, over ${{st.n}}
    rollout${{st.n > 1 ? "s" : ""}}:</b> win chance for the side that takes the path ${{st.wp_i.toFixed(0)}}% &rarr; ${{st.wp_end.toFixed(0)}}%
    (<b>${{st.gain >= 0 ? "+" : ""}}${{st.gain.toFixed(1)}}</b>); its moves lose ${{st.loss_taker.toFixed(1)}} win-% points on average,
    the other side's ${{st.loss_other.toFixed(1)}}` + skillList("move at i", st, "i_") + skillList("move at j", st, "j_") + "</div>";
  const xs = D.paths[sel.value][id] || [];
  if (!xs.length) h += D.have_examples ? "<i>no rollout with this path was found</i>"
                                       : "<i>no example rollouts yet: run concepts.py examples</i>";
  for (const x of xs) {{
    h += `<hr><div class="mv"><b>${{x.player}}</b> playing, from &hellip; ${{x.start}}</div><div class="pair">
      <div>${{board(x.fen_i, x.uci_i)}}<div class="cap"><span class="mi">${{i}}</span> turns on (ply ${{x.ti}})</div></div>
      <div>${{board(x.fen_j, x.uci_j)}}<div class="cap"><span class="mj">${{j}}</span> turns on (ply ${{x.tj}})</div></div></div>
      <div class="mv">` + x.line.map(([t, k]) => k ? `<span class="m${{k}}">${{t}}</span>` : t).join(" ") + "</div>" + changeHTML(x.change)
      + scoreHTML(x.score);
  }}
  return h;
}}
// Skill facts (skill.py) shared by the path's examples at the move at i or j: "only move (2 of 3)"
function skillList(lab, st, pre) {{
  const xs = Object.keys(D.skill_text).filter(f => st[pre + f] > 0)
    .map(f => `${{D.skill_text[f]}} (${{Math.round(st[pre + f] * st.n)}} of ${{st.n}})`);
  return xs.length ? `<div><b>${{lab}}:</b> ${{xs.join("; ")}}</div>` : "";
}}
function scoreHTML(sc) {{
  if (!sc) return "";
  const f = xs => xs.map(n => D.skill_text[n]).join(", ") || "nothing notable";
  return `<div class="why">Stockfish: taker's win chance ${{sc.wp_i.toFixed(0)}}% &rarr; ${{sc.wp_end.toFixed(0)}}%
    (${{sc.gain >= 0 ? "+" : ""}}${{sc.gain.toFixed(1)}}); move at i: ${{f(sc.facts_i)}}; move at j (${{sc.j_mover === "taker" ? "taker" : "other side"}}): ${{f(sc.facts_j)}}</div>`;
}}
// What changed from i's position to j's, told from the side to move at i ("we"), and the two moves
function changeHTML(c) {{
  if (!c) return "";
  const li = (lab, xs) => xs.length ? `<div><b>${{lab}}</b> ${{xs.join("; ")}}</div>` : "";
  return `<div class="why">` + li("move at i (ours):", c.move_i) + li(`move at j (${{c.j_mover === "we" ? "ours" : "theirs"}}):`, c.move_j) +
         li("now true:", c.appear) + li("no longer true:", c.vanish) +
         (c.appear.length || c.vanish.length ? "" : "<div>no change in the position facts</div>") + "</div>";
}}
function showTip(j, ev, edge) {{
  tip.innerHTML = edge ? edgeHTML(j) : latentHTML(j); tip.style.display = "block";
  const x = ev.clientX + 16, y = ev.clientY - 20;
  tip.style.left = Math.min(x, innerWidth - tip.offsetWidth - 8) + "px";
  tip.style.top = Math.max(8, Math.min(y, innerHeight - tip.offsetHeight - 8)) + "px";
}}
"""
    page = f"""<!doctype html><meta charset="utf-8"><title>Concept paths</title>
<script src="https://unpkg.com/vis-network@9.1.9/standalone/umd/vis-network.min.js"></script>
<style>body{{margin:0;font:13px system-ui,sans-serif}}#bar{{padding:8px;border-bottom:1px solid #ccc}}
#g{{height:calc(100vh - 60px)}}
{cards_css}</style>
{BOARD_DEFS}{MOVE_HEAD}
<div id="bar"><a href="graph3d.html">3D view</a> &nbsp; paths <select id="v"></select> <span id="n"></span> &nbsp; size <select id="sz"><option value="deg">paths in this view</option>
<option value="rate">firing rate</option><option value="one">equal</option></select> &nbsp; <button id="mv">unfreeze layout</button><br>
arrow i &rarr; j: concept j turns on within {cfg['window']} plies of concept i, more than in sibling rollouts. <b>only X</b>: this path is taken when X
plays and not when the other model does (both concepts come up with both models). Node colour: decoder share, blue = {html.escape(A)},
red = {html.escape(B)}, grey = both. Hover a node to see the concept, or an arrow to see a rollout where the path happens; click to pin.</div>
<div id="g"></div><div id="tip"></div>
<script>
const D = {json.dumps(data)};
const sel = document.getElementById("v"), sz = document.getElementById("sz"), tip = document.getElementById("tip");
for (const v of Object.keys(D.views)) sel.add(new Option(v, v));
{cards_js}function draw() {{
  const es = D.views[sel.value], used = new Set(), deg = {{}};
  document.getElementById("n").textContent = `${{es.length}} shown of ${{D.found[sel.value]}} passing`;
  es.forEach(e => {{ used.add(e[0]); used.add(e[1]); deg[e[0]] = (deg[e[0]] || 0) + 1; deg[e[1]] = (deg[e[1]] || 0) + 1; }});
  const size = j => sz.value === "rate" ? Math.sqrt(D.nodes[j].rate + 1e-6) : sz.value === "deg" ? Math.sqrt(deg[j]) : 1;
  const nodes = [...used].map(j => ({{id: j, label: String(j), color: colour(D.nodes[j].r), value: size(j)}}));
  const edges = es.map(e => ({{id: `${{e[0]}}-${{e[1]}}`, from: e[0], to: e[1], value: Math.abs(e[2]), arrows: "to",
                              color: {{color: "#8899aa", opacity: 0.6, hover: "#258", highlight: "#258"}}}}));
  if (net) net.destroy();
  tip.style.display = "none"; pinned = false; tip.classList.remove("pinned");
  net = new vis.Network(document.getElementById("g"), {{nodes, edges}},
    {{physics: {{solver: "forceAtlas2Based", stabilization: {{iterations: 400}}}}, nodes: {{shape: "dot", scaling: {{min: 5, max: 26}}}},
      edges: {{scaling: {{min: 0.5, max: 4}}, smooth: false}}, interaction: {{hover: true, tooltipDelay: 100}}}});
  // the layout settles once and then stays put (the button turns the simulation back on)
  net.once("stabilizationIterationsDone", () => {{ net.setOptions({{physics: false}}); frozen = true; }});
  net.on("hoverNode", p => {{ if (!pinned) showTip(p.node, p.event); }});
  net.on("blurNode", () => {{ if (!pinned) tip.style.display = "none"; }});
  net.on("hoverEdge", p => {{ if (!pinned) showTip(p.edge, p.event, true); }});
  net.on("blurEdge", () => {{ if (!pinned) tip.style.display = "none"; }});
  net.on("click", p => {{
    if (p.nodes.length) {{ pinned = true; tip.classList.add("pinned"); showTip(p.nodes[0], p.event.srcEvent); }}
    else if (p.edges.length) {{ pinned = true; tip.classList.add("pinned"); showTip(p.edges[0], p.event.srcEvent, true); }}
    else {{ pinned = false; tip.classList.remove("pinned"); tip.style.display = "none"; }}
  }});
}}
document.getElementById("mv").onclick = e => {{
  frozen = !frozen; net.setOptions({{physics: !frozen}}); e.target.textContent = frozen ? "unfreeze layout" : "freeze layout"; }};
sel.onchange = draw; sz.onchange = draw; draw();
</script>"""
    (run / "graph.html").write_text(page, encoding="utf-8")

    # The same views in 3D (3d-force-graph on three.js). Kept light so it stays smooth with hundreds of
    # paths: links are plain lines (no tube meshes or arrowheads; particles show the direction), hover only
    # recolours (no geometry is rebuilt), neighbours come from a lookup table, the layout is mostly worked
    # out before the first frame, and the pixel ratio is capped.
    page3d = f"""<!doctype html><meta charset="utf-8"><title>Concept paths 3D</title>
<script src="https://unpkg.com/3d-force-graph@1.73.4/dist/3d-force-graph.min.js"></script>
<style>html,body{{margin:0;height:100%;overflow:hidden}}
body{{color:#e2e8f5;font:13px/1.45 system-ui,sans-serif;
background:radial-gradient(ellipse at 50% 40%,#16203a 0%,#0b1022 45%,#04060d 100%)}}
#bar{{position:fixed;top:14px;left:14px;z-index:5;padding:12px 16px;max-width:640px;border-radius:12px;
background:rgba(12,17,32,.62);backdrop-filter:blur(10px);border:1px solid rgba(148,163,209,.18);box-shadow:0 8px 30px rgba(0,0,0,.35)}}
#bar select,#bar button{{background:rgba(30,40,68,.8);color:#e2e8f5;border:1px solid rgba(148,163,209,.3);border-radius:6px;
padding:3px 9px;font:inherit;cursor:pointer}}#bar button:hover,#bar select:hover{{border-color:#a5b4fc}}
#bar a{{color:#a5b4fc;text-decoration:none}}.title{{font-size:16px;font-weight:600;letter-spacing:.03em;margin-right:12px}}
.key{{display:inline-block;width:10px;height:10px;border-radius:50%;margin:0 5px 0 12px;vertical-align:-1px;box-shadow:0 0 8px currentColor}}
#n{{color:#94a3c7}}#hint{{color:#8b97b8;margin-top:8px;font-size:12px}}
{cards_css}
#tip{{position:fixed;display:none;max-width:560px;max-height:88vh;overflow-y:auto;background:#fbfaf6;color:#1d2230;
border-radius:10px;padding:10px 12px;box-shadow:0 10px 40px rgba(0,0,0,.55);z-index:10}}#tip.pinned{{outline:2px solid #a5b4fc}}</style>
{BOARD_DEFS}{MOVE_HEAD}
<div id="bar"><span class="title">Concept paths</span><select id="v"></select> <span id="n"></span><br>
<span class="key" style="background:#38bdf8;color:#38bdf8"></span>{html.escape(A)}
<span class="key" style="background:#c4b5fd;color:#c4b5fd"></span>both
<span class="key" style="background:#fb7185;color:#fb7185"></span>{html.escape(B)}
&nbsp; <button id="rot">pause rotation</button> <button id="fit">re-centre</button> <a href="graph.html">&nbsp;2D view</a>
<div id="hint">node colour: which model uses the concept &middot; particles flow i &rarr; j; once scored, a path glows
<span style="color:#34d399">green</span> when it gains for the side taking it and <span style="color:#f43f5e">red</span> when it loses
&middot; hover for the card, click to pin and fly there, drag to orbit, scroll to zoom</div></div>
<div id="g"></div><div id="tip"></div>
<script>
const D = {json.dumps(data)};
const sel = document.getElementById("v"), tip = document.getElementById("tip");
for (const v of Object.keys(D.views)) sel.add(new Option(v, v));
let last = {{clientX: innerWidth / 2, clientY: innerHeight / 2}};
addEventListener("mousemove", e => {{ last = e; }}, {{passive: true}});
{cards_js}
// node colour by relative decoder norm: sky blue (first model) -> lilac (both) -> coral pink (second model)
const STOPS = [[56, 189, 248], [196, 181, 253], [251, 113, 133]];
function glow(r) {{
  if (!(r >= 0)) return "#7c86a2";
  const t = Math.max(0, Math.min(1, (r - 0.25) / 0.5)) * 2, k = Math.min(1, Math.floor(t)), f = t - k;
  const c = STOPS[k].map((a, i) => Math.round(a + (STOPS[k + 1][i] - a) * f));
  return `rgb(${{c[0]}},${{c[1]}},${{c[2]}})`;
}}
const TINT = {{"only {A}": "#38bdf8", "only {B}": "#fb7185", both: "#a5b4fc"}};
const GAIN = "#34d399", LOSS = "#f43f5e", DIM_NODE = "#1a2138", DIM_LINK = "rgba(60,72,110,0.12)";
let hl = new Set(), hlLinks = new Set(), focus = null, adj = new Map();
const G = ForceGraph3D({{controlType: "orbit"}})(document.getElementById("g"))
  .backgroundColor("rgba(0,0,0,0)").showNavInfo(false)
  .nodeLabel(() => "").nodeOpacity(1).nodeResolution(10).nodeRelSize(3)
  .nodeColor(n => hl.size ? (n.id === focus ? "#ffffff" : hl.has(n.id) ? n.c : DIM_NODE) : n.c)
  .linkWidth(0).linkOpacity(0.28).linkHoverPrecision(3)
  .linkColor(l => hl.size && !hlLinks.has(l) ? DIM_LINK : l.color)
  .linkDirectionalParticles(l => l.p).linkDirectionalParticleWidth(1.8).linkDirectionalParticleResolution(6)
  .linkDirectionalParticleSpeed(l => 0.0025 + 0.002 * l.w)
  .linkDirectionalParticleColor(l => hl.size && !hlLinks.has(l) ? DIM_LINK : l.color)
  .warmupTicks(120).cooldownTicks(160).d3VelocityDecay(0.35)
  .onNodeHover(n => later(() => {{ setFocus(n ? n.id : null, null); if (pinned) return;
    if (n) showTip(n.id, last); else tip.style.display = "none"; }}))
  .onLinkHover(l => later(() => {{ setFocus(null, l); if (pinned) return;
    if (l) showTip(l.id, last, true); else tip.style.display = "none"; }}))
  .onNodeClick(n => {{ setFocus(n.id, null); pinned = true; tip.classList.add("pinned"); showTip(n.id, last); fly(n); }})
  .onLinkClick(l => {{ setFocus(null, l); pinned = true; tip.classList.add("pinned"); showTip(l.id, last, true); }})
  .onBackgroundClick(() => {{ pinned = false; tip.classList.remove("pinned"); tip.style.display = "none"; setFocus(null, null, true); }});
G.renderer().setPixelRatio(Math.min(devicePixelRatio || 1, 1.5));
let pending = 0;                                             // at most one hover update per frame
function later(f) {{ cancelAnimationFrame(pending); pending = requestAnimationFrame(f); }}
function setFocus(id, link, force) {{                         // light up a node's neighbourhood, or one path
  if (pinned && !force) return;
  const key = id !== null ? "n" + id : link ? "l" + link.id : null;
  if (key === setFocus.key) return;
  setFocus.key = key;
  hl = new Set(); hlLinks = new Set(); focus = id;
  if (id !== null) {{ hl.add(id); for (const k of adj.get(id) || []) {{ hlLinks.add(k); hl.add(k.source.id ?? k.source); hl.add(k.target.id ?? k.target); }} }}
  if (link) {{ hlLinks.add(link); hl.add(link.source.id); hl.add(link.target.id); }}
  G.nodeColor(G.nodeColor()).linkColor(G.linkColor()).linkDirectionalParticleColor(G.linkDirectionalParticleColor());
}}
function fly(n) {{
  const d = 80, k = 1 + d / Math.max(1, Math.hypot(n.x, n.y, n.z));
  G.cameraPosition({{x: n.x * k, y: n.y * k, z: n.z * k}}, n, 1400);
}}
function draw() {{
  const v = sel.value, es = D.views[v], deg = {{}};
  document.getElementById("n").textContent = `${{es.length}} shown of ${{D.found[v]}} passing`;
  es.forEach(e => {{ deg[e[0]] = (deg[e[0]] || 0) + 1; deg[e[1]] = (deg[e[1]] || 0) + 1; }});
  const nodes = Object.keys(deg).map(j => ({{id: +j, val: 1 + 1.6 * Math.sqrt(deg[j]), c: glow(D.nodes[j].r)}}));
  const zmax = Math.max(...es.map(e => Math.abs(e[2])), 1);
  const links = es.map(e => {{
    const st = (D.path_stats[v] || {{}})[`${{e[0]}}-${{e[1]}}`], w = Math.abs(e[2]) / zmax;
    const color = st ? (st.gain >= 2 ? GAIN : st.gain <= -2 ? LOSS : TINT[v]) : TINT[v];
    return {{id: `${{e[0]}}-${{e[1]}}`, source: e[0], target: e[1], w, p: w > 0.5 ? 2 : 1, color}};
  }});
  adj = new Map();
  for (const l of links) for (const j of [l.source, l.target]) {{ if (!adj.has(j)) adj.set(j, []); adj.get(j).push(l); }}
  pinned = false; tip.style.display = "none"; tip.classList.remove("pinned");
  hl = new Set(); hlLinks = new Set(); focus = null; setFocus.key = null;
  G.graphData({{nodes, links}});
  setTimeout(() => G.zoomToFit(900, 60), 600);
}}
let spin = true;
G.controls().autoRotate = true; G.controls().autoRotateSpeed = 0.45;
document.getElementById("rot").onclick = e => {{ spin = !spin; G.controls().autoRotate = spin;
  e.target.textContent = spin ? "pause rotation" : "rotate"; }};
document.getElementById("fit").onclick = () => G.zoomToFit(900, 60);
addEventListener("resize", () => G.width(innerWidth).height(innerHeight));
document.addEventListener("visibilitychange", () => document.hidden ? G.pauseAnimation() : G.resumeAnimation());
sel.onchange = draw; draw();
</script>"""
    (run / "graph3d.html").write_text(page3d, encoding="utf-8")
    print(f"wrote {out / 'summary.md'}, {out}/edges-*.csv, {run / 'graph.graphml'}, {run / 'graph.html'} and {run / 'graph3d.html'}")


# ---------------------------------------------------------------- modes: SVD of the flow matrices

def latent_rates(cfg):
    with open(Path(cfg["cc_run"]) / cfg["cc"] / "latents.jsonl", encoding="utf-8") as f:
        return {r["latent"]: r["rate"] for r in map(json.loads, f)}


def modes(a):
    run = Path(a.run)
    cfg = json.loads((run / "config.json").read_text())
    dev = ev.device(a.device)
    names = [m.split("/")[-1] for m in cfg["models"]]
    players = [n for n in names if (run / n / "C.npy").exists()]
    st = {n: edge_stats(run / n, cfg["rollouts"]) for n in players}
    L = st[players[0]][0].shape[0]
    rate = latent_rates(cfg)
    fire = torch.tensor([rate.get(j, 0.0) for j in range(L)])
    keep = fire <= a.max_rate
    for n in players:
        keep &= st[n][2] >= a.min_onsets
    keep = keep.nonzero().squeeze(1)
    print(f"{len(keep)} of {L} latents kept: firing in <= {100 * a.max_rate:g}% of positions, "
          f">= {a.min_onsets} onsets with each player", flush=True)
    sub = {}
    for n in players:
        C, E, N = st[n]
        C, E, N = C[keep][:, keep], E[keep][:, keep], N[keep]
        sub[n] = (C, (C - E) / (N[:, None] + a.prior))            # excess rate per onset of i, shrunk for rare i
    del st
    zero = torch.zeros(())
    mats = {n: torch.where(sub[n][0] >= a.min_count, sub[n][1], zero) for n in players}
    if len(players) == 2:
        A, B = players
        both = (sub[A][0] >= a.min_count) | (sub[B][0] >= a.min_count)
        mats = {"diff": torch.where(both, sub[B][1] - sub[A][1], zero), **mats}

    res, used = {}, set()
    for v, M in mats.items():
        Mg = M.to(dev)
        U, S, V = torch.svd_lowrank(Mg, q=a.modes + 10, niter=6)
        total = float((Mg ** 2).sum())
        del Mg
        U, S, V = U[:, :a.modes].cpu(), S[:a.modes].cpu(), V[:, :a.modes].cpu()
        out = []
        for k in range(len(S)):
            u, w = U[:, k], V[:, k]
            if u[u.abs().argmax()] < 0:                           # sign: the strongest source is positive
                u, w = -u, -w
            t = min(a.top, len(u))
            su, sw = u.abs().topk(t).indices, w.abs().topk(t).indices
            contrib = float(S[k]) * u[su][:, None] * w[sw][None, :]
            real = M[su][:, sw]
            ok = (torch.sign(real) == torch.sign(contrib)) & (real != 0)  # edges the mode explains, and that are there
            score = torch.where(ok, contrib.abs(), torch.full_like(contrib, -1)).flatten()
            edges = []
            for f in score.topk(min(a.mode_edges, int(ok.sum()))).indices.tolist():
                x, y = int(su[f // t]), int(sw[f % t])
                e = dict(i=int(keep[x]), j=int(keep[y]), value=float(M[x, y]))
                for n in players:
                    e["rate_" + n] = float(sub[n][1][x, y])
                edges.append(e)
            m = dict(s=float(S[k]), share=float(S[k]) ** 2 / max(total, 1e-12),
                     sources=[[int(keep[x]), float(u[x])] for x in su[:a.show_latents].tolist()],
                     targets=[[int(keep[x]), float(w[x])] for x in sw[:a.show_latents].tolist()], edges=edges)
            used |= {l for l, _ in m["sources"] + m["targets"]} | {e[c] for e in edges for c in ("i", "j")}
            out.append(m)
        res[v] = out
        first = ", ".join("%.1f" % (100 * m["share"]) for m in out[:5])
        print(f"{v}: top {len(S)} modes hold {100 * sum(m['share'] for m in out):.1f}% of the matrix ({first}% ...)",
              flush=True)

    print(f"describing {len(used)} latents", flush=True)
    desc = describe(cfg, used)
    outdir = RESULTS / run.name
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "modes.json").write_text(json.dumps(dict(args={k: v for k, v in vars(a).items() if k != "func"},
                                                        players=players, modes=res)), encoding="utf-8")
    md = [f"# Flow modes, {run.name}", "",
          "Truncated SVD of the excess-rate matrix r[i, j] = (C - E) / (N_i + prior): how much more often latent j "
          f"turns on within {cfg['window']} plies of i's onset than in sibling rollouts. **diff** = r under "
          f"{players[-1]} minus r under {players[0]} (positive: stronger when {players[-1]} plays). A mode is a group "
          "of source latents (u) feeding a group of target latents (v).", ""]
    lab = lambda j: f"{j} (r {desc[j]['rel_norm']:.2f}): {desc[j]['examples'][0] if desc[j]['examples'] else ''}"
    for v, out in res.items():
        md += [f"## {v}", ""]
        for k, m in enumerate(out):
            md += [f"### {v} mode {k}: {100 * m['share']:.1f}% of the matrix", ""]
            for e in m["edges"][:a.show]:
                rates = ", ".join(f"{n} {100 * e['rate_' + n]:+.1f}%" for n in players)
                md.append(f"- **{e['i']} -> {e['j']}** ({rates})  \n  {html.escape(lab(e['i']))}  \n  -> {html.escape(lab(e['j']))}")
            md.append("")
    (outdir / "modes.md").write_text("\n".join(md), encoding="utf-8")

    data = dict(nodes={j: dict(r=desc[j]["rel_norm"], rate=desc[j]["rate"], ex=desc[j]["boards"], why=desc[j]["why"],
                              expl=desc[j]["expl"]) for j in used},
                modes=res, players=players, A=names[0], B=names[1] if len(names) > 1 else "")
    page = f"""<!doctype html><meta charset="utf-8"><title>Flow modes</title>
<style>body{{margin:0;font:13px system-ui,sans-serif}}#bar{{padding:8px;border-bottom:1px solid #ccc}}
#wrap{{display:flex;height:calc(100vh - 60px)}}#main{{flex:1;overflow-y:auto;padding:8px}}
#side{{width:300px;overflow-y:auto;padding:8px;border-left:1px solid #ccc}}
.mode{{border:1px solid #ccc;border-radius:6px;padding:8px;margin-bottom:12px}}.cols{{display:flex;gap:16px;flex-wrap:wrap}}
.lats{{display:flex;flex-wrap:wrap;gap:6px}}.lat{{cursor:pointer;text-align:center;font-size:11px}}.lat:hover{{outline:2px solid #69c}}
table{{border-collapse:collapse;margin-top:6px}}td,th{{padding:2px 8px;text-align:right;font-size:12px}}
td.l{{cursor:pointer;color:#258;text-decoration:underline}}.pos{{color:#c33}}.neg{{color:#36c}}
{BOARD_CSS}</style>
{BOARD_DEFS}{MOVE_HEAD}
<div id="bar">view <select id="v"></select> &nbsp; Each mode: <b>source</b> latents (left) turn on, then <b>target</b> latents (right)
turn on within {cfg['window']} plies, more than in sibling rollouts. In <b>diff</b>, red = stronger when {html.escape(players[-1])} plays,
blue = stronger when {html.escape(players[0])} plays. Click a latent for its top positions.</div>
<div id="wrap"><div id="main"></div><div id="side">click a latent</div></div>
<script>
const D = {json.dumps(data)};
const sel = document.getElementById("v"), main = document.getElementById("main"), side = document.getElementById("side");
for (const v of Object.keys(D.modes)) sel.add(new Option(v, v));
{BOARD_JS}
const pct = x => (x >= 0 ? "+" : "") + (100 * x).toFixed(1) + "%";
function chip(j, w) {{
  const ex = D.nodes[j].ex[0];
  return `<div class="lat" onclick="side.innerHTML = latentHTML(${{j}})">${{ex ? board(ex[0], ex[3], "sm") : ""}}
    ${{j}} <span class="${{w >= 0 ? "pos" : "neg"}}">${{w.toFixed(2)}}</span><br>r ${{(+D.nodes[j].r).toFixed(2)}}</div>`;
}}
function colour(r) {{ if (!(r >= 0)) return "#999"; const b = Math.round(255 * (1 - r)), rr = Math.round(255 * r);
  return Math.abs(r - 0.5) < 0.2 ? "#aaa" : `rgb(${{rr}},80,${{b}})`; }}
// A mode as a fixed two-column graph: sources left, targets right, arrows for its edges
// (width ~ size of the effect; in diff, red = stronger for the second player, blue = for the first).
function flow(m, diff) {{
  const left = m.sources.map(s => s[0]), right = m.targets.map(t => t[0]);
  for (const e of m.edges) {{ if (!left.includes(e.i)) left.push(e.i); if (!right.includes(e.j)) right.push(e.j); }}
  const W = 420, H = 30 * Math.max(left.length, right.length) + 20, xl = 60, xr = W - 60;
  const y = (k, n) => 20 + (k + 0.5) * (H - 30) / n;
  const pos = {{}};
  left.forEach((j, k) => pos["s" + j] = y(k, left.length)); right.forEach((j, k) => pos["t" + j] = y(k, right.length));
  const big = Math.max(...m.edges.map(e => Math.abs(e.value)), 1e-9);
  let s = `<svg width="${{W}}" height="${{H}}" style="flex:none"><defs>
    <marker id="ar" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0L10,5L0,10z" fill="#666"/></marker></defs>
    <text x="${{xl}}" y="12" text-anchor="middle" font-size="11">sources</text><text x="${{xr}}" y="12" text-anchor="middle" font-size="11">targets</text>`;
  for (const e of m.edges) {{
    const c = diff ? (e.value >= 0 ? "#c33" : "#36c") : "#778";
    s += `<line x1="${{xl + 9}}" y1="${{pos["s" + e.i]}}" x2="${{xr - 11}}" y2="${{pos["t" + e.j]}}" stroke="${{c}}" stroke-opacity="0.7"
      stroke-width="${{1 + 5 * Math.abs(e.value) / big}}" marker-end="url(#ar)"><title>${{e.i}} → ${{e.j}}: ${{pct(e.value)}}</title></line>`;
  }}
  const node = (j, x, yy, anchor, dx) => `<g style="cursor:pointer" onclick="side.innerHTML = latentHTML(${{j}})">
    <circle cx="${{x}}" cy="${{yy}}" r="8" fill="${{colour(D.nodes[j].r)}}" stroke="#333"/>
    <text x="${{x + dx}}" y="${{yy + 4}}" text-anchor="${{anchor}}" font-size="11">${{j}}</text></g>`;
  left.forEach(j => s += node(j, xl, pos["s" + j], "end", -12));
  right.forEach(j => s += node(j, xr, pos["t" + j], "start", 12));
  return s + "</svg>";
}}
function draw() {{
  const v = sel.value, diff = v === "diff";
  main.innerHTML = D.modes[v].map((m, k) => {{
    const rows = m.edges.map(e => `<tr><td class="l" onclick="side.innerHTML = latentHTML(${{e.i}})">${{e.i}}</td><td>&rarr;</td>
      <td class="l" onclick="side.innerHTML = latentHTML(${{e.j}})">${{e.j}}</td>` +
      D.players.map(n => `<td>${{pct(e["rate_" + n])}}</td>`).join("") +
      (diff ? `<td class="${{e.value >= 0 ? "pos" : "neg"}}">${{pct(e.value)}}</td>` : "") + "</tr>").join("");
    return `<div class="mode"><b>mode ${{k}}</b>: ${{(100 * m.share).toFixed(1)}}% of the matrix
      <div class="cols">${{flow(m, diff)}}<div><b>sources</b><div class="lats">${{m.sources.map(([j, w]) => chip(j, w)).join("")}}</div></div>
      <div><b>targets</b><div class="lats">${{m.targets.map(([j, w]) => chip(j, w)).join("")}}</div></div></div>
      <table><tr><th>i</th><th></th><th>j</th>${{D.players.map(n => `<th>${{n}}</th>`).join("")}}${{diff ? "<th>diff</th>" : ""}}</tr>${{rows}}</table></div>`;
  }}).join("");
}}
sel.onchange = draw; draw();
</script>"""
    (run / "modes.html").write_text(page, encoding="utf-8")
    print(f"wrote {outdir / 'modes.md'}, {outdir / 'modes.json'} and {run / 'modes.html'}")


# ---------------------------------------------------------------- command line

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for cmd in ("rollout", "graph", "examples", "score", "modes", "all"):
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
        if cmd == "examples":
            p.add_argument("--ex-starts", type=int, default=25_000,
                           help="fresh start positions to replay at most (stops once every path has its examples)")
            p.add_argument("--per-edge", type=int, default=4, help="example rollouts per path")
            p.add_argument("--stall", type=int, default=3000,
                           help="stop a player's search after this many starts without a new example")
            p.add_argument("--batch", type=int, default=1024, help="rollouts played at once")
            p.add_argument("--no-cuda-graphs", action="store_true", help="decode eagerly (slower; for debugging)")
        if cmd == "score":
            p.add_argument("--depth", type=int, default=14, help="Stockfish depth")
            p.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2),
                           help="processes, each running one single-threaded Stockfish")
        if cmd in ("graph", "examples", "score", "all"):
            p.add_argument("--z", type=float, default=6.0)
            p.add_argument("--lift", type=float, default=1.5)
            p.add_argument("--min-count", type=int, default=30)
            p.add_argument("--absent", type=float, default=1.0,
                           help="an 'only X' path has z below this when the other model plays")
            p.add_argument("--max-rate", type=float, default=0.05,
                           help="leave out latents firing in more than this share of positions (hubs)")
            p.add_argument("--min-onsets", type=int, default=200,
                           help="latents need this many onsets with EACH player, so both models reach the concept")
            p.add_argument("--edges", type=int, default=400, help="paths kept per view")
            p.add_argument("--html-edges", type=int, default=400, help="paths drawn per view in graph.html")
            p.add_argument("--show", type=int, default=40, help="edges listed per view in summary.md")
        if cmd == "modes":
            p.add_argument("--modes", type=int, default=15, help="SVD components per view")
            p.add_argument("--max-rate", type=float, default=0.05,
                           help="leave out latents firing in more than this share of positions (they swamp the matrix)")
            p.add_argument("--min-onsets", type=int, default=100, help="keep latents with at least this many onsets per player")
            p.add_argument("--prior", type=float, default=100.0,
                           help="pseudo-onsets added to N_i: shrinks the rates of rarely seen latents toward 0")
            p.add_argument("--min-count", type=int, default=20, help="cells with fewer co-onsets are set to 0")
            p.add_argument("--top", type=int, default=40, help="sources x targets searched for each mode's edges")
            p.add_argument("--mode-edges", type=int, default=12, help="edges listed per mode")
            p.add_argument("--show-latents", type=int, default=8, help="source and target latents drawn per mode")
            p.add_argument("--show", type=int, default=8, help="edges per mode in modes.md")
    a = ap.parse_args()
    if a.cmd in ("rollout", "all"):
        if a.rollouts < 2:
            sys.exit("--rollouts must be at least 2 (sibling rollouts are the control)")
        a.run = str(rollout(a))
    if a.cmd in ("graph", "all"):
        if not a.run:
            sys.exit("--run is required")
        graph(a)
    if a.cmd == "examples":
        if not a.run:
            sys.exit("--run is required")
        examples(a)
    if a.cmd == "score":
        if not a.run:
            sys.exit("--run is required")
        score_paths(a)
    if a.cmd == "modes":
        if not a.run:
            sys.exit("--run is required")
        modes(a)


if __name__ == "__main__":
    main()
