"""At one position, a concept (a set of latents firing together) that some of S's rollouts carry out and others don't.
S only: S plays every move of every rollout (W's activations are read too, because the crosscoder encodes the pair).

    python transcend/dynamic/oneposition.py --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal

1. position   one middlegame position from a held-out game with at least two reasonable moves: the first candidate (in a
              seeded random order) where S gives >= 2 moves >= --reasonable and none more than --max-top.
2. temperature --rollouts rollouts of --plies plies at each of --temps; per T the number of distinct lines and the share of
              the most common one, and the median ply at which a line leaves it; the lowest T with >= --min-distinct distinct lines and no line above --max-line is used.
3. encode     every distinct line through the crosscoder; a line is, per latent, the share of its plies where it fires;
              each line weighted by how often it was sampled (a repeated line is not independent evidence); candidate
              latents: those whose fraction varies across the lines (weighted sd >= --min-sd).
4. concepts   weighted correlations of every pair of latents over the distinct lines; null: each latent's values
              shuffled across the distinct lines independently (the weights stay with the lines), --shuffles times, the
              largest correlation each time, the threshold the 95th percentile of those maxima (family-wise); average
              linkage (distance 1 - r) cut there; every group of >= 3 latents a candidate concept. A line carries a
              concept when at least half the group's latents are above their own weighted median fraction in it.
5. board      splits read off the board (the first move; which piece goes to which square; castling, by side; pawn
              breaks, pawn captures and pushes to the fifth rank or beyond; trades, a capture recaptured on the same
              square, and the queens coming off): per concept, the share of carrying and of other rollouts in each split,
              and the best-matching splits (weighted phi).
   branch     with --branch-plies k (default 4), steps 4's groups are found after the branch effect is removed: each
              latent's fraction minus its weighted mean over the lines sharing the first k moves, so a group co-fires for
              reasons other than a shared prefix. Routes: per concept the distinct move sequences carrying it, cut before
              its latents start firing (half of them at one ply), and the distinct boards at that point, each against
              --null-sets random line sets of the same size and onset plies: below the 5th percentile, a branch.
6. replicate  a second, independent --rollouts at the same T, steps 3-4 again; concepts matched by shared latents (Jaccard).
7. read       per replicated concept: its latents, the share of rollouts carrying it, its best split, and 3 distinct lines
              carrying it and 3 not, in SAN, the plies where its latents fire in [brackets].

-> results/transcend/oneposition/<tag>/report.md, report.json; rollouts and codes cached in runs/transcend/oneposition/<tag>
   (a rerun with the same --tag reuses them)."""

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

import chess
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # chess_beyond/
import paths  # noqa: E402  also puts transcend/'s folders on sys.path
import eval as ev
import shared as gd
from concepts import room
from pgn_model import MAX_MOVE_CHARS, prompt
from pgn_probe import parse_movetext

RUNS = paths.RUNS / "transcend" / "oneposition"
RESULTS = paths.ROOT / "results" / "transcend" / "oneposition"


# ---------------------------------------------------------------- data
def pick_position(a, Sm, dev):
    """The first candidate (seeded random order) where S's policy gives >= 2 moves >= --reasonable, none above --max-top."""
    rng = np.random.default_rng(a.seed)
    pop = [json.loads(l) for l in open(a.population, encoding="utf-8")]
    cand = []
    for i in rng.permutation(len(pop)):
        r = pop[i]
        if len(r["prompt"]) + room(a.plies) + MAX_MOVE_CHARS + 1 > Sm.ctx:
            continue
        b = ev.board_of(parse_movetext(r["prompt"])[0])
        if prompt(b) != r["prompt"] or b.is_game_over() or not gd.middlegame(b):
            continue
        cand.append((r, b))
        if len(cand) >= a.candidates:
            break
    legal, lp, _ = gd.policy(Sm, [b for _, b in cand], dev, [r["prompt"] for r, _ in cand], batch=a.batch)
    for (r, b), mv, l in zip(cand, legal, lp):
        p = np.exp(l - np.logaddexp.reduce(l))
        if p.max() <= a.max_top and (p >= a.reasonable).sum() >= 2:
            top = sorted(zip(p, mv), key=lambda x: -x[0])[:5]
            root = dict(prompt=r["prompt"], fen=b.fen(), band=r["band"], game=r["game"],
                        top=[(b.san(m), float(q)) for q, m in top])
            print(f"position: {b.fen()} ({r['band']} game {r['game']}); S's top moves "
                  + ", ".join(f"{s} {q:.0%}" for s, q in root["top"]), flush=True)
            return root, mv, l
    sys.exit("no candidate with two reasonable moves: raise --candidates")


def rollouts(a, root, legal, lp, Sm, dev, T, seed):
    """--rollouts lines of S from the root at temperature T, S writing every move -> [tuple of SANs], [tuple of UCIs]."""
    rng = np.random.default_rng(seed)
    b0 = ev.board_of(parse_movetext(root["prompt"])[0])
    L = []
    for k in range(a.rollouts):
        line = dict(board=b0.copy(), moves=[], sans=[], prompt=root["prompt"])
        gd.advance(line, legal[gd.sample(lp, T, rng)])
        L.append(line)
    for ply in range(1, a.plies):
        live = [l for l in L if len(l["moves"]) == ply and not l["board"].is_game_over()]
        if live:
            lg, lps, _ = gd.policy(Sm, [l["board"] for l in live], dev, [l["prompt"] for l in live], batch=a.batch)
            for l, mv, p in zip(live, lg, lps):
                gd.advance(l, mv[gd.sample(p, T, rng)])
    return [tuple(l["sans"]) for l in L], [tuple(l["moves"]) for l in L]


def split_ply(D):
    """The ply (1-based) at which each distinct line first leaves the most common one -> list (one per other line)."""
    top = D[0]["sans"]
    out = []
    for d in D[1:]:
        s_ = d["sans"]
        i = next((i for i, (x, y) in enumerate(zip(s_, top)) if x != y), min(len(s_), len(top)))
        out.append(i + 1)
    return out


def distinct(sans, ucis):
    """The distinct lines, most common first -> [dict(sans, moves, n)]."""
    cnt = Counter(zip(sans, ucis))
    return [dict(sans=list(s), moves=list(u), n=n) for (s, u), n in cnt.most_common()]


def encode(a, cc, models, root, D, dev):
    """Per distinct line and latent: the share of its plies (after the root) where the latent fires -> (lines, latents)
    float32; and which latents fire at which ply, sparse (lines * (plies + 1), latents)."""
    from scipy import sparse
    Ld = dict(roots=[dict(prompt=root["prompt"], fen=root["fen"])], lines=[dict(root=0, moves=d["moves"]) for d in D])
    seqs, ends, _, _, _, line_start = gd.positions(Ld)
    st = {m: gd.line_states(models[m], seqs, ends, cc.layer[m], dev, a.max_tokens) for m in (0, 1)}
    rows, cols = [], []
    with torch.no_grad():
        for i in range(0, len(st[0]), 4096):
            f, _ = gd.encode_states(cc, {m: st[m][i:i + 4096].to(dev) for m in (0, 1)})
            nz = (f > 0).nonzero().cpu().numpy()
            rows.append(nz[:, 0] + i)
            cols.append(nz[:, 1])
    rows, cols = np.concatenate(rows), np.concatenate(cols)
    nlat = cc.ck["latents"]
    pos_line = np.repeat(np.arange(len(D)), np.diff(line_start))
    pos_t = np.concatenate([np.arange(n) for n in np.diff(line_start)])
    after = pos_t[rows] >= 1                                            # the root itself is shared by every line
    r_, c_ = rows[after], cols[after]
    P = sparse.csr_matrix((np.ones(len(r_), np.float32), (pos_line[r_] * (a.plies + 1) + pos_t[r_], c_)),
                          shape=(len(D) * (a.plies + 1), nlat))
    n = np.maximum(np.diff(line_start) - 1, 1)
    X = np.zeros((len(D), nlat), np.float32)
    np.add.at(X, (pos_line[r_], c_), 1.0)
    return X / n[:, None], P


# ---------------------------------------------------------------- analysis
def wcorr(X, w):
    """Correlations of X's columns over its rows, row weights w (summing to 1)."""
    mu = w @ X
    Z = (X - mu) * np.sqrt(w)[:, None]
    sd = np.sqrt((Z ** 2).sum(0))
    return (Z.T @ Z) / np.maximum(np.outer(sd, sd), 1e-12)


def shuffle_threshold(X, w, n, rng, q=0.95):
    """Family-wise: each column's values shuffled across the lines independently (weights stay with the lines), n times,
    each time the largest off-diagonal correlation; the q-quantile of those maxima."""
    iu = np.triu_indices(X.shape[1], 1)
    mx = []
    for _ in range(n):
        Y = np.take_along_axis(X, rng.random(X.shape).argsort(0), 0)
        mx.append(float(wcorr(Y, w)[iu].max()))
    return float(np.quantile(mx, q))


def groups_of(R, thr):
    """Average linkage on 1 - r, cut at 1 - thr -> [arrays of column indices], >= 3 each."""
    from scipy.cluster.hierarchy import fcluster, linkage
    from scipy.spatial.distance import squareform
    Dm = np.clip(1 - R, 0, 2)
    np.fill_diagonal(Dm, 0)
    lab = fcluster(linkage(squareform(Dm, checks=False), "average"), t=1 - thr, criterion="distance")
    return [np.flatnonzero(lab == c) for c in np.unique(lab) if (lab == c).sum() >= 3]


def wmedian(X, w):
    """Each column's weighted median over the rows."""
    o = np.argsort(X, 0)
    cw = np.cumsum(w[o], 0)
    k = (cw < 0.5).sum(0)
    return np.take_along_axis(X, o, 0)[np.minimum(k, len(X) - 1), np.arange(X.shape[1])]


def above(X, g, med):
    """Per line, the share of the group's latents above their own weighted median fraction."""
    return (X[:, g] > med[g][None, :]).mean(1)


def carrying(X, g, med):
    """A line carries a concept when at least half the group's latents are above their own weighted median fraction
    (with 16 plies nearly every latent fires somewhere in nearly every line, so "fires at all" has no contrast)."""
    return above(X, g, med) >= 0.5


def branch_of(D, k):
    """Each distinct line's branch: its first k moves -> labels 0..B-1."""
    keys = {}
    return np.array([keys.setdefault(tuple(d["sans"][:k]), len(keys)) for d in D])


def residual(X, w, lab):
    """X minus what the branch explains: each latent's weighted mean over its branch's lines subtracted."""
    Z = X.astype(np.float64).copy()
    for b in np.unique(lab):
        m = lab == b
        Z[m] -= (w[m] @ X[m]) / w[m].sum()
    return Z


def concepts(X, w, a, rng, tag, lab=None):
    """Steps 3-4 on one batch's distinct lines -> kept latents, threshold, [dict(latents, share, r)], the matrix the
    groups were found on (X, or with lab its residual after the branch effect), and its medians. Candidate latents:
    those whose fraction of plies varies across the lines (weighted sd >= --min-sd), and with lab still varies within
    branches (residual weighted sd >= --min-sd / 2)."""
    t0 = time.time()
    mu = w @ X
    sd = np.sqrt(w @ (X - mu) ** 2)
    keep = sd >= a.min_sd
    X = residual(X, w, lab) if lab is not None else X
    if lab is not None:
        keep &= np.sqrt(w @ X ** 2) >= a.min_sd / 2
    kk = np.flatnonzero(keep)
    Xk = X[:, kk]
    med = wmedian(X, w)
    thr = shuffle_threshold(Xk, w, a.shuffles, rng)
    R = wcorr(Xk, w)
    out = []
    for g in groups_of(R, thr):
        out.append(dict(latents=kk[g].tolist(), share=float(w @ carrying(X, kk[g], med)),
                        r=float(R[np.ix_(g, g)][np.triu_indices(len(g), 1)].mean())))
    out.sort(key=lambda c: -c["r"])
    print(f"  {tag}: {len(kk)} latents whose fraction of plies varies{' (also within branches)' if lab is not None else ''}; "
          f"threshold r > {thr:.3f} (family-wise); {len(out)} concepts of >= 3 latents ({time.time() - t0:.0f}s)", flush=True)
    return kk, thr, out, X, med


def onset(P, q, g, plies):
    """The first ply (1-based) at which at least half the group's latents fire in line q, or None."""
    pl = P[q * (plies + 1):(q + 1) * (plies + 1)][:, g].toarray() > 0
    t = next((t for t in range(1, plies + 1) if pl[t].mean() >= 0.5), None)
    return t


def boards_of(D, root, plies):
    """Per distinct line, the board (pieces and side to move) after each ply 0..len -> [[str]]."""
    out = []
    for d in D:
        b = chess.Board(root["fen"])
        fs = [b.board_fen() + (" w" if b.turn else " b")]
        for u in d["moves"]:
            b.push(chess.Move.from_uci(u))
            fs.append(b.board_fen() + (" w" if b.turn else " b"))
        out.append(fs)
    return out


def effective(keys, ws):
    """The effective number of distinct keys: 1 / sum of squared weight shares."""
    tot = {}
    for k, x in zip(keys, ws):
        tot[k] = tot.get(k, 0.0) + x
    v = np.array(list(tot.values()))
    v /= v.sum()
    return float(1 / (v ** 2).sum()), len(tot)


def spread(D, w, fire, P, g, plies, fens, rng, n_null):
    """How varied the lines carrying a concept are, where its latents start firing (onset: the first ply with half of
    them firing): the move sequences before the onset (routes) and the boards at it (transpositions count once), each
    as an effective number, against a null of n_null random line sets of the same size (drawn by sampling weight)
    given the carrying lines' onset plies. Below the null's 5th percentile: a branch."""
    q_, t_ = [], []
    for q in np.flatnonzero(fire):
        t = onset(P, q, g, plies)
        if t is not None and t <= len(D[q]["sans"]):
            q_.append(q)
            t_.append(t)
    if len(q_) < 2:
        return dict(routes=len(q_), effective=float(len(q_)), boards=len(q_), boards_eff=float(len(q_)), onset=t_[0] if t_ else None,
                    null5=float("nan"), null5_boards=float("nan"), branch=True, branch_boards=True)
    route = lambda q, t: tuple(D[q]["sans"][:t - 1])
    board = lambda q, t: fens[q][t]
    er, nr = effective([route(q, t) for q, t in zip(q_, t_)], w[q_])
    eb, nb_ = effective([board(q, t) for q, t in zip(q_, t_)], w[q_])
    ok = np.flatnonzero(np.array([len(d["sans"]) for d in D]) >= max(t_))
    pool = ok if len(ok) >= len(q_) else np.arange(len(D))
    pw = w[pool] / w[pool].sum()
    nr_, nb2 = [], []
    for _ in range(n_null):
        qs = rng.choice(pool, len(q_), replace=False, p=pw)
        ts = rng.permutation(t_)
        ts = [min(t, len(D[q]["sans"])) for q, t in zip(qs, ts)]
        nr_.append(effective([route(q, t) for q, t in zip(qs, ts)], w[qs])[0])
        nb2.append(effective([board(q, t) for q, t in zip(qs, ts)], w[qs])[0])
    n5, nb5 = float(np.quantile(nr_, 0.05)), float(np.quantile(nb2, 0.05))
    o = sorted(zip(t_, w[q_]))
    cw = np.cumsum([x[1] for x in o])
    return dict(routes=nr, effective=er, boards=nb_, boards_eff=eb, onset=int(o[int(np.searchsorted(cw, cw[-1] / 2))][0]),
                null5=n5, null5_boards=nb5, branch=er < n5, branch_boards=eb < nb5)


def board_splits(D, root):
    """Splits read off the board -> {name: bool per distinct line}: the first move; which piece goes to which square;
    castling, by side; pawn breaks (pawn captures, pawn pushes to the fifth rank or beyond); trades (a capture
    recaptured on the same square, by piece type; the queens coming off)."""
    n = len(D)
    out = {}
    feat = {}
    b0 = chess.Board(root["fen"])
    both_q = bool(b0.pieces(chess.QUEEN, chess.WHITE)) and bool(b0.pieces(chess.QUEEN, chess.BLACK))
    for i, d in enumerate(D):
        b = b0.copy()
        f = set()
        if d["sans"]:
            f.add(f"first move {d['sans'][0]}")
        last_cap = None
        for u in d["moves"]:
            mv = chess.Move.from_uci(u)
            side = "White" if b.turn == chess.WHITE else "Black"
            pt = b.piece_type_at(mv.from_square)
            name = chess.piece_name(pt).capitalize() if pt else "?"
            f.add(f"{side} {name} to {chess.square_name(mv.to_square)}")
            if b.is_castling(mv):
                f.add(f"{side} castles")
            cap = b.piece_at(mv.to_square) if b.is_capture(mv) else None
            if pt == chess.PAWN:
                rank = chess.square_rank(mv.to_square) + 1
                rel = rank if b.turn == chess.WHITE else 9 - rank
                if b.is_capture(mv):
                    f.add(f"{side} pawn break: pawn takes on {chess.square_name(mv.to_square)}")
                elif rel >= 5:
                    f.add(f"{side} pawn push to {chess.square_name(mv.to_square)}")
            if b.is_capture(mv) and last_cap == mv.to_square:
                f.add(f"trade on {chess.square_name(mv.to_square)}")
                if cap is not None:
                    f.add(f"trade of a {chess.piece_name(cap.piece_type)}")
            last_cap = mv.to_square if b.is_capture(mv) else None
            b.push(mv)
        if both_q and not b.pieces(chess.QUEEN, chess.WHITE) and not b.pieces(chess.QUEEN, chess.BLACK):
            f.add("queens off")
        for x in f:
            feat.setdefault(x, np.zeros(n, bool))[i] = True
    w = np.array([d["n"] for d in D], float)
    w /= w.sum()
    for k, v in feat.items():
        if 0.05 <= w @ v <= 0.95:
            out[k] = v
    return out


def wphi(x, y, w):
    x, y = x.astype(float), y.astype(float)
    mx, my = w @ x, w @ y
    vx, vy = w @ (x - mx) ** 2, w @ (y - my) ** 2
    return 0.0 if vx <= 0 or vy <= 0 else float(w @ ((x - mx) * (y - my)) / np.sqrt(vx * vy))


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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cc-run", default="runs/transcend/crosscoder/everything-3m")
    ap.add_argument("--cc", default="Lfinal")
    ap.add_argument("--strong", default="2400", help="a part of S's name")
    ap.add_argument("--population", default=str(gd.PROBE / "population.jsonl"), help="held-out positions")
    ap.add_argument("--candidates", type=int, default=400, help="held-out middlegame positions to choose the root from")
    ap.add_argument("--reasonable", type=float, default=0.2, help="a reasonable move has at least this share of S's policy")
    ap.add_argument("--max-top", type=float, default=0.6, help="... and no move more than this")
    ap.add_argument("--rollouts", type=int, default=1024, help="rollouts per temperature and per batch")
    ap.add_argument("--plies", type=int, default=16)
    ap.add_argument("--temps", default="0.2,0.4,0.6", help="temperatures to choose from, lowest first")
    ap.add_argument("--min-distinct", type=int, default=20, help="distinct lines the chosen temperature needs ...")
    ap.add_argument("--max-line", type=float, default=0.5, help="... with no single line above this share")
    ap.add_argument("--min-sd", type=float, default=0.05, help="candidate latents: weighted sd of their fraction of plies "
                    "across the lines at least this")
    ap.add_argument("--shuffles", type=int, default=100)
    ap.add_argument("--jaccard", type=float, default=0.3, help="latent overlap at which a concept counts as found again")
    ap.add_argument("--branch-plies", type=int, default=4, help="the branch effect: a line's first this many moves (0: no "
                    "correction)")
    ap.add_argument("--null-sets", type=int, default=1000, help="random line sets for the routes and boards null")
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--max-tokens", type=int, default=300_000)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    from scipy import sparse
    tag = a.tag or f"p{a.plies}-r{a.rollouts}-s{a.seed}-T{a.temps.replace(',', '_')}"
    run, res = RUNS / tag, RESULTS / tag
    run.mkdir(parents=True, exist_ok=True)
    res.mkdir(parents=True, exist_ok=True)
    cache = run / "data.json"
    if cache.exists():
        C = json.loads(cache.read_text(encoding="utf-8"))
        z = np.load(run / "codes.npz")
        Xs = [z["X1"], z["X2"]]
        Ps = [sparse.csr_matrix((z[f"P{k}_data"], z[f"P{k}_indices"], z[f"P{k}_indptr"]), shape=tuple(z[f"P{k}_shape"])) for k in (1, 2)]
        print(f"reusing {run}", flush=True)
    else:
        dev = ev.device(a.device)
        cc = gd.load_cc(a.cc_run, a.cc, a.strong, dev)
        models = {m: ev.load(cc.info["models"][m], dev)[0] for m in (0, 1)}
        Sm = models[cc.s]
        root, legal, lp0 = pick_position(a, Sm, dev)
        temps, chosen = [], None                                       # step 2
        for T in [float(x) for x in a.temps.split(",")]:
            t0 = time.time()
            sans, ucis = rollouts(a, root, legal, lp0, Sm, dev, T, [a.seed, int(T * 1000), 1])
            D = distinct(sans, ucis)
            ok = len(D) >= a.min_distinct and D[0]["n"] / a.rollouts <= a.max_line
            sp = split_ply(D)
            temps.append(dict(T=T, distinct=len(D), top=D[0]["n"] / a.rollouts, ok=ok,
                              split=float(np.median(sp)) if sp else float("nan")))
            print(f"T {T}: {len(D)} distinct lines of {a.rollouts}, the most common {D[0]['n'] / a.rollouts:.0%}, "
                  f"median ply at which a line leaves it {temps[-1]['split']:.0f} ({time.time() - t0:.0f}s)", flush=True)
            if ok and chosen is None:
                chosen = (T, D)
        if chosen is None:
            sys.exit("no temperature gives enough distinct lines: add a higher one to --temps")
        T, D1 = chosen
        sans, ucis = rollouts(a, root, legal, lp0, Sm, dev, T, [a.seed, int(T * 1000), 2])   # step 6's batch
        D2 = distinct(sans, ucis)
        print(f"T {T} chosen; second batch: {len(D2)} distinct lines", flush=True)
        Xs, Ps = [], []
        for D in (D1, D2):
            X, P = encode(a, cc, models, root, D, dev)
            Xs.append(X), Ps.append(P)
        C = dict(root=root, temps=temps, T=T, batches=[D1, D2])
        cache.write_text(json.dumps(C), encoding="utf-8")
        np.savez_compressed(run / "codes.npz", X1=Xs[0], X2=Xs[1],
                            **{f"P{k + 1}_{f}": getattr(Ps[k], f) for k in (0, 1) for f in ("data", "indices", "indptr")},
                            **{f"P{k + 1}_shape": np.array(Ps[k].shape) for k in (0, 1)})
    root, T = C["root"], C["T"]
    rng = np.random.default_rng(a.seed)
    out = ["# A concept inside S's rollouts from one position", "",
           f"Position `{root['fen']}` ({root['band']} game {root['game']}); S's top moves "
           + ", ".join(f"{s} {q:.0%}" for s, q in root["top"]) + f". {a.rollouts} rollouts of S, {a.plies} plies, S plays both "
           "colours; a line is, per latent, the share of its plies where the latent fires; distinct lines weighted by how often "
           "each was sampled.", "", "## Temperature", "",
           "| T | distinct lines | most common line | median ply where a line leaves the most common one | used |", "|---|---|---|---|---|"]
    out += [f"| {t['T']} | {t['distinct']} | {t['top']:.0%} | {t.get('split', float('nan')):.0f} | {'yes' if t['T'] == T else ''} |"
            for t in C["temps"]]
    out += ["", f"T = {T}: the lowest with >= {a.min_distinct} distinct lines and no line above {a.max_line:.0%}.", ""]
    found = []
    for k, (D, X) in enumerate(zip(C["batches"], Xs), 1):
        w = np.array([d["n"] for d in D], float)
        w /= w.sum()
        lab = branch_of(D, a.branch_plies) if a.branch_plies > 0 else None
        kk, thr, cs, Z, med = concepts(X, w, a, rng, f"batch {k}", lab)
        found.append((D, Z, w, kk, thr, cs, med, lab))
    (D1, X1, w1, kk1, thr1, c1, med1, lab1), (D2, X2, w2, kk2, thr2, c2, _, lab2) = found
    for i, c in enumerate(c1):                                         # step 6: in the second batch?
        c["name"] = str(i + 1)
        s1 = set(c["latents"])
        jac, d = max(((len(s1 & set(x["latents"])) / len(s1 | set(x["latents"])), x) for x in c2), key=lambda x: x[0], default=(0.0, None))
        c["match"] = dict(jaccard=jac, shared=len(s1 & set(d["latents"])) if d else 0, size=len(d["latents"]) if d else 0)
        c["replicated"] = jac >= a.jaccard
    splits = board_splits(D1, root)                                    # step 5
    fens1 = boards_of(D1, root, a.plies)
    for c in c1:
        fire = carrying(X1, np.array(c["latents"]), med1)
        c["spread"] = spread(D1, w1, fire, Ps[0], np.array(c["latents"]), a.plies, fens1, rng, a.null_sets)
        c["early"] = (c["spread"]["onset"] or 0) <= 1                  # firing from the first ply: no route to compare
        c["plan"] = not c["early"] and not c["spread"]["branch"] and not c["spread"]["branch_boards"]
        c["verdict"] = "from ply 1 (untestable)" if c["early"] else "candidate" if c["plan"] else "branch"
        ph = sorted(((wphi(fire, m, w1), nm) for nm, m in splits.items()), key=lambda x: -abs(x[0]))
        c["splits"] = [dict(split=nm, phi=v, carrying=float(w1[fire] @ splits[nm][fire] / max(w1[fire].sum(), 1e-12)),
                            other=float(w1[~fire] @ splits[nm][~fire] / max(w1[~fire].sum(), 1e-12))) for v, nm in ph[:3]]
    rk = [c for c in c1 if c["replicated"]]
    nb = len(np.unique(lab1)) if lab1 is not None else 0
    out += [f"## Concepts (batch 1: {len(D1)} distinct lines, {len(kk1)} latents, threshold r > {thr1:.3f}; batch 2: {len(D2)} "
            f"distinct lines, {len(kk2)} latents, threshold r > {thr2:.3f}, {len(c2)} concepts)", "",
            (f"The branch effect removed first: each latent's fraction minus its weighted mean over the lines of the same branch "
             f"(the first {a.branch_plies} moves; {nb} branches in batch 1), so a group co-fires for reasons other than a shared "
             "prefix; a line carries a concept when half its latents are above their own weighted median of that residual. "
             if lab1 is not None else "No branch correction (--branch-plies 0). ")
            + f"{len(c1)} concepts in batch 1, {len(rk)} found again in batch 2 (Jaccard of latents >= {a.jaccard}). Onset: the "
            "first ply where half a concept's latents fire. Routes: the move sequences before the onset; boards: the positions "
            "at it (transpositions count once); each an effective number (weighted by how often a line was sampled), against "
            f"{a.null_sets} random line sets of the same size given the same onset plies: below the null's 5th percentile on "
            "routes or on boards, a branch; otherwise a candidate (the same latents on genuinely different lines and boards).", "",
            "| concept | latents | mean r | carrying | in batch 2 (Jaccard, shared) | onset ply | routes: effective (null 5%) | boards: effective (null 5%) | | best board split (phi): carrying / other |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for c in c1:
        bs = c["splits"][0] if c["splits"] else None
        sp = c["spread"]
        out.append(f"| {c['name']} | {', '.join(map(str, c['latents']))} | {c['r']:.2f} | {c['share']:.0%} | "
                   f"{'yes' if c['replicated'] else 'no'} ({c['match']['jaccard']:.2f}, {c['match']['shared']}) | "
                   f"{sp['onset'] if sp['onset'] else '-'} | {sp['effective']:.1f} ({sp['null5']:.1f}) | "
                   f"{sp['boards_eff']:.1f} ({sp['null5_boards']:.1f}) | {c['verdict']} | "
                   + (f"{bs['split']} ({bs['phi']:+.2f}): {bs['carrying']:.0%} / {bs['other']:.0%}" if bs else "-") + " |")
    out += ["", f"{len(splits)} board splits tested (each in 5-95% of the rollouts).", ""]
    for c in sorted(rk, key=lambda c: not c["plan"]):                 # step 7, candidate plans first
        g = np.array(c["latents"])
        fire = carrying(X1, g, med1)
        dens = above(X1, g, med1)
        yes = [i for i in np.argsort(-dens) if fire[i]][:3]
        no = [i for i in np.argsort(dens) if not fire[i]][:3]
        sp = c["spread"]
        out += [f"### Concept {c['name']} ({c['verdict']}): latents {', '.join(map(str, c['latents']))}; "
                f"carried by {c['share']:.0%} of the rollouts, its latents starting at ply {sp['onset']}: {sp['effective']:.1f} "
                f"effective routes (random lines: {sp['null5']:.1f} at the 5th percentile), {sp['boards_eff']:.1f} effective boards "
                f"({sp['null5_boards']:.1f})", ""]
        out += [f"- {s['split']}: {s['carrying']:.0%} of carrying rollouts, {s['other']:.0%} of the others (phi {s['phi']:+.2f})"
                for s in c["splits"]]
        out.append("")
        for nm, ids in (("carrying it", yes), ("not carrying it", no)):
            out += [f"{nm}:", ""]
            for q in ids:
                pl = Ps[0][q * (a.plies + 1):(q + 1) * (a.plies + 1)][:, g].toarray() > 0
                plies = {t for t in range(1, a.plies + 1) if pl[t].mean() >= 0.5}     # half the group's latents at that ply
                out.append(f"- {mark(D1[q]['sans'], plies, root)}  (sampled {D1[q]['n']}x; "
                           f"[Lichess]({gd.lichess_line(root, D1[q]['sans'])}))")
            out.append("")
    rep = dict(root=root, temps=C["temps"], T=T, settings=vars(a), concepts=c1, batch2=c2,
               thresholds=[thr1, thr2], latents=[len(kk1), len(kk2)], distinct=[len(D1), len(D2)])
    (res / "report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    (res / "report.json").write_text(json.dumps(rep, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o), indent=1))
    print(f"{len(c1)} concepts, {len(rk)} found again in batch 2; wrote {res / 'report.md'}")


if __name__ == "__main__":
    main()
