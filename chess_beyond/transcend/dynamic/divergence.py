"""Schut et al.'s dynamic concepts within each model, with persistence built into the fit: at every point where a model's
rollouts branch, the sparsest set of latents that separates the line it played most often from a line it played less,
not at one ply but on every ply of a window after the split. Concepts are gathered first; how they recur across
positions is measured afterwards, on held-out positions.

    python transcend/dynamic/divergence.py play   --model S        # GPU: S's cached manypositions lines, re-encoded with values
    python transcend/dynamic/divergence.py play   --model W        # GPU: W's own rollouts at the same positions, encoded
    python transcend/dynamic/divergence.py plant                   # CPU, S: the planted check (run it before lp)
    python transcend/dynamic/divergence.py lp     --model S        # CPU: divergence pairs and the LP, every k
    python transcend/dynamic/divergence.py report                  # CPU: families, recurrence, persistence, examples (S, W)

0. data      the 50 positions of the manypositions run (--source). S: its cached lines (1,024 rollouts of 16 plies at
             T = 0.4, S both colours) re-encoded through the crosscoder with activation values kept. W: --rollouts
             rollouts of --plies plies at --temperature from the same positions, W both colours, encoded the same way.
             A latent is on at a ply when z > --on x mu_j (mu_j: its mean activation where it fires, over all of that
             model's positions). One file per position, so a partial run is usable.
1. pairs     per position, the tree of distinct lines (weighted by how often each was sampled). At each branching
             point (shared moves up to ply t-1, different moves at ply t) the chosen branch is the move played most
             often there; every other move with at least --min-share of that point's weight is a subpar branch. Each
             branch is represented by its most frequent line. Per k, pairs without k plies left after the split in
             both lines are skipped, and at most --cap pairs are kept per position, spread over the branching plies
             (round robin over t, the heavier subpar branch first).
2. LP        per pair and k in --ks:  min_{v >= 0} |v|_1 + C xi  s.t.  v . (z^chosen_tau - z^subpar_tau) >= 1 - xi,
             tau = t..t+k, one slack per pair, over the latents on in either line within the window; HiGHS dual
             simplex. Every v is saved (v = 0 is "no concept") with the position, ply, moves, k, the active latents,
             and the ties: every latent that alone separates the whole window (on in the chosen line and off in the
             subpar one at every tau), since L1 returns just one of a set of equivalent latents.
             C: with binary codes v . d <= |v|_1, so separating costs |v|_1 >= 1 while v = 0, xi = 1 costs C; at C = 1
             the LP is indifferent and v = 0 always optimal. Default --C 2: a v is returned when one with |v|_1 < 2
             separates (or partly separates at lower total cost).
3. plant     S only, at the first --plant-positions positions: one branching point each (a random pair with 4 plies
             left), 3 latents switched on at plies t..t+4 in the chosen line only (latents off in both lines in that
             window, firing on 1-30% of the position's plies); steps 1-2 at k = 4 and k = 0. Per planted pair: whether
             v holds a planted latent, whether v is planted latents only, whether all 3 are in the ties; and how many
             other pairs at that position pick up a planted latent.
4. measure   per model and k. Positions split 25 / 25 by a hash of band and game. Families: within one half, the
             nonzero v's grouped greedily (largest support first) when their support has Jaccard >= --jaccard with a
             family's core (the latents in at least half its members, as recurring.py); a family is its members'
             mean v, renormalised to |v|_1 = 1. Held-out recurrence: the share of the other half's pairs (same k) where
             v . (z^chosen_tau - z^subpar_tau) >= 0.5 at every ply of the window. Null: --null random v's per family
             with its weights on as many latents, each drawn from the latents that fire anywhere in that model's run
             in the same firing-rate decile; the family's null 95th percentile. Persistence: on the other half's k = 0
             pairs, the consecutive plies from the split where v . d_tau >= 0.5, median over the pairs where it is on
             at the split.
5. report    per model and k: pairs, share with nonzero v, families, held-out recurrence against the null; the top
             --top families by held-out recurrence; for the top --show, 3 held-out pairs from different positions where
             it holds, chosen and subpar lines side by side in SAN, plies where v . z >= 0.5 in that line in
             [brackets], Lichess links.

-> runs/transcend/divergence/<tag>/<S|W>/ (pos-k.npz codes, lp-k.json pairs and v's),
   results/transcend/divergence/<tag>/plant.md, report.md, report.json"""

import argparse
import json
import sys
import time
import zlib
from pathlib import Path

import chess
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # chess_beyond/
import paths  # noqa: E402  also puts transcend/'s folders on sys.path
import eval as ev
import shared as gd
import oneposition as op
import recurring as rc

RUNS = paths.RUNS / "transcend" / "divergence"
RESULTS = paths.ROOT / "results" / "transcend" / "divergence"
SOURCE = paths.RUNS / "transcend" / "manypositions" / "p16-r1024-T0.4-s0"


def dirs(a, model):
    run, res = RUNS / a.tag / model, RESULTS / a.tag
    run.mkdir(parents=True, exist_ok=True)
    res.mkdir(parents=True, exist_ok=True)
    return run, res


def roots_of(a):
    return json.loads((Path(a.source) / "positions.json").read_text(encoding="utf-8"))


def eta(times, left):
    return f"{np.mean(times) * left / 60:.0f} min"


# ---------------------------------------------------------------- 0: data
def play(a):
    run, _ = dirs(a, a.model)
    roots = roots_of(a)
    todo = [k for k in range(len(roots)) if not (run / f"pos-{k}.npz").exists()]
    if not todo:
        print(f"all {len(roots)} positions done in {run}")
        return
    dev = ev.device(a.device)
    cc = gd.load_cc(a.cc_run, a.cc, a.strong, dev)
    models = {m: ev.load(cc.info["models"][m], dev)[0] for m in (0, 1)}
    me = models[cc.s if a.model == "S" else cc.w]
    times = []
    for i, k in enumerate(todo):
        t0 = time.time()
        root = roots[k]
        cached = Path(a.source) / f"pos-{k}.npz"
        if a.model == "S" and cached.exists():                         # S's lines as the 50-position run sampled them
            D = json.loads(str(np.load(cached)["D"]))
        else:
            b = ev.board_of(gd.parse_movetext(root["prompt"])[0])
            legal, lp, _ = gd.policy(me, [b], dev, [root["prompt"]], batch=a.batch)
            sans, ucis = op.rollouts(a, root, legal[0], lp[0], me, dev, a.temperature, [a.seed, k, 0 if a.model == "S" else 1])
            D = op.distinct(sans, ucis)
        P = rc.encode_values(a, cc, models, root, D, dev)
        cnt = np.bincount(P.indices, minlength=P.shape[1])
        tot = np.bincount(P.indices, weights=P.data.astype(np.float64), minlength=P.shape[1])
        np.savez_compressed(run / f"pos-{k}.npz", D=json.dumps(D), data=P.data.astype(np.float16), indices=P.indices,
                            indptr=P.indptr, shape=np.array(P.shape), vcnt=cnt, vsum=tot)
        times.append(time.time() - t0)
        left = len(todo) - i - 1
        print(f"{a.model} position {k} ({i + 1}/{len(todo)}): {len(D)} distinct lines ({times[-1]:.0f}s); {left} left in "
              f"{eta(times, left)}", flush=True)
        if i + 1 == 5:
            print(f"  timed 5 positions: {np.mean(times):.0f}s each, projected total {eta(times, len(todo))}", flush=True)


def load_on(run, k, mu, on):
    """A position's lines, weights and on-matrix (lines * (plies + 1), latents) bool sparse."""
    D, P, w, _ = rc.load_pos(run, k)
    return D, w, rc.on_matrix(P, mu, on).tocsr()


def mu_for(a, run, K):
    """mu_j over all the model's positions played; saved on first use so every position is binarised alike."""
    f = run / "mu.json"
    if f.exists():
        m = json.loads(f.read_text(encoding="utf-8"))
        if m["positions"] < K:
            print(f"  mu from {m['positions']} positions (now {K} played): delete {f} to recompute", flush=True)
        return np.array(m["mu"])
    mu = rc.mu_of(run, K)
    f.write_text(json.dumps(dict(positions=sum((run / f"pos-{k}.npz").exists() for k in range(K)), mu=mu.tolist())),
                 encoding="utf-8")
    return mu


# ---------------------------------------------------------------- 1: pairs
def pairs_of(D, plies, min_share):
    """Every (chosen, subpar) pair of branches -> [dict(t, c, s, chosen, subpar, wc, ws, node)]; c, s: the branches'
    most frequent lines (D is most common first, so a branch's first line)."""
    out = []
    for t in range(1, plies + 1):
        nodes = {}
        for q, d in enumerate(D):
            if len(d["sans"]) >= t:
                nodes.setdefault(tuple(d["sans"][:t - 1]), {}).setdefault(d["sans"][t - 1], []).append(q)
        for ch in nodes.values():
            if len(ch) < 2:
                continue
            wt = {m: sum(D[q]["n"] for q in qs) for m, qs in ch.items()}
            tot = sum(wt.values())
            best = max(ch, key=lambda m: (wt[m], -ch[m][0]))
            for m, qs in ch.items():
                if m != best and wt[m] < wt[best] and wt[m] / tot >= min_share:
                    out.append(dict(t=t, c=ch[best][0], s=qs[0], chosen=best, subpar=m, wc=wt[best] / tot, ws=wt[m] / tot,
                                    node=tot))
    return out


def select(pairs, D, k, cap):
    """Pairs with k plies left after the split in both lines; at most cap, round robin over t, heavier subpar first."""
    ok = [p for p in pairs if min(len(D[p["c"]]["sans"]), len(D[p["s"]]["sans"])) >= p["t"] + k]
    by = {}
    for p in sorted(ok, key=lambda p: -p["ws"]):
        by.setdefault(p["t"], []).append(p)
    out, ts = [], sorted(by)
    while len(out) < cap and any(by[t] for t in ts):
        for t in ts:
            if by[t] and len(out) < cap:
                out.append(by[t].pop(0))
    return sorted(out, key=lambda p: (p["t"], -p["ws"]))


def window(Q, q, t, k, plies):
    r = q * (plies + 1)
    return Q[r + t:r + t + k + 1].toarray() > 0


# ---------------------------------------------------------------- 2: LP
def solve(zc, zs, C):
    """Schut's LP with a persistence window, on (k + 1, latents) bool rows -> dict(latents, weights, xi, active, ties)."""
    from scipy.optimize import linprog
    act = np.flatnonzero((zc | zs).any(0))
    d = zc[:, act].astype(float) - zs[:, act].astype(float)
    ties = act[(d == 1).all(0)].tolist()
    if not len(act):
        return dict(latents=[], weights=[], xi=1.0, active=[], ties=[])
    n = len(act)
    A = np.hstack([-d, -np.ones((len(d), 1))])
    r = linprog(np.r_[np.ones(n), C], A_ub=A, b_ub=-np.ones(len(d)), bounds=[(0, None)] * (n + 1), method="highs-ds")
    if r.status != 0:
        return dict(latents=[], weights=[], xi=float("nan"), active=act.tolist(), ties=ties, failed=r.message)
    v = r.x[:n]
    nz = v > 1e-9
    return dict(latents=act[nz].tolist(), weights=v[nz].tolist(), xi=float(r.x[n]), active=act.tolist(), ties=ties)


def lp_position(a, D, Q, ks):
    """Steps 1-2 at one position -> {k: [pair records with v]}."""
    allp = pairs_of(D, a.plies, a.min_share)
    out = {}
    for k in ks:
        recs = []
        for p in select(allp, D, k, a.cap):
            v = solve(window(Q, p["c"], p["t"], k, a.plies), window(Q, p["s"], p["t"], k, a.plies), a.C)
            recs.append(dict(**p, k=k, **v))
        out[k] = recs
    return out, len(allp)


def lp(a):
    run, _ = dirs(a, a.model)
    roots = roots_of(a)
    have = [k for k in range(len(roots)) if (run / f"pos-{k}.npz").exists()]
    if not have:
        sys.exit(f"no positions in {run}: run play --model {a.model} first")
    mu = mu_for(a, run, len(roots))
    ks = [int(x) for x in a.ks.split(",")]
    todo = [k for k in have if not (run / f"lp-{k}.json").exists()]
    times = []
    for i, k in enumerate(todo):
        t0 = time.time()
        D, w, Q = load_on(run, k, mu, a.on)
        res, n_all = lp_position(a, D, Q, ks)
        (run / f"lp-{k}.json").write_text(json.dumps(dict(position=k, pairs_all=n_all, ks={str(x): r for x, r in res.items()})),
                                          encoding="utf-8")
        times.append(time.time() - t0)
        left = len(todo) - i - 1
        print(f"{a.model} position {k}: {n_all} branch pairs; " + ", ".join(
            f"k={x}: {len(r)} pairs, {np.mean([bool(p['latents']) for p in r]) if r else 0:.0%} nonzero v" for x, r in res.items())
              + f" ({times[-1]:.1f}s; {left} left in {eta(times, left)})", flush=True)
        if i + 1 == 5:
            print(f"  timed 5 positions: {np.mean(times):.1f}s each, projected total {eta(times, len(todo))}", flush=True)
    print(f"lp done: {sum((run / f'lp-{k}.json').exists() for k in range(len(roots)))} of {len(roots)} positions in {run}")


# ---------------------------------------------------------------- 3: plant
def plant(a):
    run, res = dirs(a, "S")
    roots = roots_of(a)
    mu = mu_for(a, run, len(roots))
    rng = np.random.default_rng(a.seed)
    from scipy import sparse
    rows, out = [], ["# Planted check (S)", "",
                     f"At each of the first {a.plant_positions} positions: one random pair with 4 plies left after the split; "
                     f"3 latents (off in both lines at plies t..t+4, on at 1-30% of the position's plies) switched on in the "
                     f"chosen line only at plies t..t+4; steps 1-2 rerun (C = {a.C}). 'in v': v holds a planted latent; "
                     "'only': v is planted latents only; 'ties': all 3 are among the latents that alone separate the window; "
                     "'leak': other pairs at that position whose v holds a planted latent.", "",
                     "| position | ply | chosen / subpar | planted | k=4: in v, only, ties | k=4 v | k=0: in v, only, ties | k=0 v | leak k=4 / k=0 |",
                     "|---|---|---|---|---|---|---|---|---|"]
    for k in range(a.plant_positions):
        if not (run / f"pos-{k}.npz").exists():
            continue
        D, w, Q = load_on(run, k, mu, a.on)
        cand = select(pairs_of(D, a.plies, a.min_share), D, 4, 10 ** 9)
        if not cand:
            continue
        p = cand[int(rng.integers(len(cand)))]
        lens = np.array([len(d["sans"]) for d in D])
        valid = np.concatenate([(np.arange(a.plies + 1) >= 1) & (np.arange(a.plies + 1) <= n) for n in lens])
        rate = np.asarray(Q[valid].sum(0)).ravel() / valid.sum()
        off = ~(window(Q, p["c"], p["t"], 4, a.plies) | window(Q, p["s"], p["t"], 4, a.plies)).any(0)
        pool = np.flatnonzero(off & (rate >= 0.01) & (rate <= 0.3))
        if len(pool) < 3:
            continue
        g = set(rng.choice(pool, 3, replace=False).tolist())
        r0 = p["c"] * (a.plies + 1)
        rr = np.repeat(np.arange(r0 + p["t"], r0 + p["t"] + 5), 3)
        add = sparse.csr_matrix((np.ones(len(rr), np.float32), (rr, np.tile(sorted(g), 5))), shape=Q.shape)
        Qp = Q + add
        Qp.data = np.minimum(Qp.data, 1)
        R, _ = lp_position(a, D, Qp, [4, 0])
        cells, leak = [], []
        for kw in (4, 0):
            mine = solve(window(Qp, p["c"], p["t"], kw, a.plies), window(Qp, p["s"], p["t"], kw, a.plies), a.C)
            hit, only, ties = bool(g & set(mine["latents"])), bool(mine["latents"]) and set(mine["latents"]) <= g, g <= set(mine["ties"])
            rows.append(dict(position=k, k=kw, hit=hit, only=only, ties=ties))
            cells += [f"{'yes' if hit else 'no'}, {'yes' if only else 'no'}, {'yes' if ties else 'no'} ({len(mine['ties'])} ties)",
                      ", ".join(f"{j}:{x:.2f}" for j, x in zip(mine["latents"], mine["weights"])) or "0"]
            leak.append(sum(1 for q in R[kw] if (q["t"], q["c"], q["s"]) != (p["t"], p["c"], p["s"]) and g & set(q["latents"])))
        out.append(f"| {k} | {p['t']} | {p['chosen']} / {p['subpar']} | {', '.join(map(str, sorted(g)))} | " + " | ".join(cells)
                   + f" | {leak[0]} / {leak[1]} |")
        print(f"position {k}: planted {sorted(g)} at ply {p['t']}; k=4 {cells[0]}; k=0 {cells[2]}", flush=True)
    out.append("")
    for kw in (4, 0):
        r = [x for x in rows if x["k"] == kw]
        if r:
            out.append(f"- k = {kw}: planted latent in v at {np.mean([x['hit'] for x in r]):.0%} of {len(r)} positions, v planted "
                       f"latents only at {np.mean([x['only'] for x in r]):.0%}, all 3 among the ties at {np.mean([x['ties'] for x in r]):.0%}")
    rec = [x for x in rows if x["k"] == 4]
    ok = rec and np.mean([x["hit"] for x in rec]) >= 0.8
    out += ["", "Recovered at k = 4 (planted latent in v at >= 80% of positions): " + ("yes" if ok else "**no: stop here**"), ""]
    (res / "plant.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    (res / "plant.json").write_text(json.dumps(rows), encoding="utf-8")
    print("\n".join(out[-4:]) + f"\nwrote {res / 'plant.md'}")


# ---------------------------------------------------------------- 4: measure
def halves(roots):
    order = sorted(range(len(roots)), key=lambda i: zlib.crc32(f"{roots[i]['band']}/{roots[i]['game']}".encode()))
    return {i: ("A" if r < len(roots) // 2 else "B") for r, i in enumerate(order)}


def diff_rows(Q, recs, plies, full=False):
    """Stacked z^chosen - z^subpar rows: the window t..t+k of each pair, or (full) t..the end of the shorter line ->
    sparse (rows, latents), and each pair's (start, end) rows."""
    from scipy import sparse
    blocks, se, n = [], [], 0
    for p in recs:
        e = min(p["lc"], p["ls"]) if full else p["t"] + p["k"]
        rc_, rs_ = p["c"] * (plies + 1), p["s"] * (plies + 1)
        blocks.append(Q[rc_ + p["t"]:rc_ + e + 1] - Q[rs_ + p["t"]:rs_ + e + 1])
        se.append((n, n + e - p["t"] + 1))
        n += e - p["t"] + 1
    return (sparse.vstack(blocks).tocsr() if blocks else None), se


def held(Dw, se, V, chunk=2000):
    """Share of pairs where v . d >= 0.5 on every row of the pair, per column of V (latents, F)."""
    out = []
    starts = np.array([s for s, _ in se])
    for i in range(0, V.shape[1], chunk):
        M = (Dw @ V[:, i:i + chunk]).toarray() >= 0.5 - 1e-9
        bad = np.add.reduceat((~M).astype(np.int32), starts, axis=0)    # windows are contiguous and cover every row
        out.append((bad == 0).mean(0))
    return np.concatenate(out) if out else np.zeros(0)


def runs_from(Df, se, V):
    """Per pair and column of V, the consecutive rows from the split with v . d >= 0.5 -> (pairs, F)."""
    M = (Df @ V).toarray() >= 0.5 - 1e-9
    return np.stack([np.cumprod(M[s:e], 0).sum(0) for s, e in se]) if se else np.zeros((0, V.shape[1]))


def vec(lat, wts, nlat):
    from scipy import sparse
    return sparse.csc_matrix((np.asarray(wts, float), (np.asarray(lat, int), np.zeros(len(lat), int))), shape=(nlat, 1))


def measure(a, model, roots, side):
    """Families, held-out recurrence, its null and persistence for one model -> per k a summary and the families."""
    from scipy import sparse
    run, _ = dirs(a, model)
    have = [k for k in range(len(roots)) if (run / f"lp-{k}.json").exists()]
    if not have:
        return None
    mu = mu_for(a, run, len(roots))
    ks = [int(x) for x in a.ks.split(",")]
    rows, on_cnt, plies_n = {k: {"A": [], "B": []} for k in ks}, None, 0
    Dw, Df = {k: {"A": [], "B": []} for k in ks}, {"A": [], "B": []}
    t0 = time.time()
    for k in have:
        L = json.loads((run / f"lp-{k}.json").read_text(encoding="utf-8"))
        D, w, Q = load_on(run, k, mu, a.on)
        Qf = Q.astype(np.float32)
        lens = np.array([len(d["sans"]) for d in D])
        valid = np.concatenate([(np.arange(a.plies + 1) >= 1) & (np.arange(a.plies + 1) <= n) for n in lens])
        c = np.asarray(Q[valid].sum(0)).ravel()
        on_cnt = c if on_cnt is None else on_cnt + c
        plies_n += int(valid.sum())
        h = side[k]
        for kw in ks:
            recs = L["ks"][str(kw)]
            for p in recs:
                p.update(position=k, lc=int(lens[p["c"]]), ls=int(lens[p["s"]]))
            rows[kw][h] += recs
            if recs:
                Dw[kw][h].append(diff_rows(Qf, recs, a.plies))
            if kw == 0 and recs:
                Df[h].append(diff_rows(Qf, recs, a.plies, full=True))
    nlat = len(mu)
    rate = on_cnt / max(plies_n, 1)

    def stack(parts):
        if not parts:
            return None, []
        se, off = [], 0
        for _, s in parts:
            se += [(x + off, y + off) for x, y in s]
            off = se[-1][1]
        return sparse.vstack([m for m, _ in parts]).tocsr(), se

    Dw = {kw: {h: stack(Dw[kw][h]) for h in "AB"} for kw in ks}
    Df = {h: stack(Df[h]) for h in "AB"}
    act = np.flatnonzero(rate > 0)
    qs = np.quantile(rate[act], np.linspace(0, 1, 11)[1:-1])
    dec = np.searchsorted(qs, rate)
    pool = {b: act[dec[act] == b] for b in range(10)}
    rng = np.random.default_rng(a.seed)
    print(f"{model}: {len(have)} positions loaded ({time.time() - t0:.0f}s)", flush=True)

    summary, fams = {}, []
    for kw in ks:
        allr = rows[kw]["A"] + rows[kw]["B"]
        nz = [p for p in allr if p["latents"]]
        S = dict(pairs=len(allr), nonzero=len(nz) / max(len(allr), 1), families=0, recurrence=[], null95=[], above=0)
        for h, o in (("A", "B"), ("B", "A")):
            G = [p for p in rows[kw][h] if p["latents"]]
            if not G or Dw[kw][o][0] is None:
                continue
            pats = rc.core_match([(p["position"], set(p["latents"])) for p in G], a.jaccard)
            V, NV = [], []
            for pt in pats:
                acc = {}
                for i in pt["members"]:
                    for j, x in zip(G[i]["latents"], G[i]["weights"]):
                        acc[j] = acc.get(j, 0.0) + x / len(pt["members"])
                lat = np.array(sorted(acc), int)
                wt = np.array([acc[j] for j in lat])
                wt /= wt.sum()
                pt.update(lat=lat, wt=wt)
                V.append(vec(lat, wt, nlat))
                for _ in range(a.null):
                    nl = []
                    for j in lat:
                        opts = pool[int(dec[j])]
                        x = int(rng.choice(opts))
                        while x in nl and len(opts) > len(lat):
                            x = int(rng.choice(opts))
                        nl.append(x)
                    NV.append(vec(nl, wt, nlat))
            V, NV = sparse.hstack(V).tocsc(), sparse.hstack(NV).tocsc()
            rec = held(*Dw[kw][o], V)
            nul = held(*Dw[kw][o], NV).reshape(len(pats), a.null)
            n95 = np.quantile(nul, 0.95, axis=1)
            run_ = runs_from(*Df[o], V) if Df[o][0] is not None else np.zeros((0, len(pats)))
            for i, pt in enumerate(pats):
                on0 = run_[:, i] >= 1
                fams.append(dict(model=model, k=kw, half=h, latents=pt["lat"].tolist(), weights=pt["wt"].tolist(),
                                 core=sorted(pt["core"]), members=len(pt["members"]),
                                 positions=sorted({G[m]["position"] for m in pt["members"]}),
                                 recurrence=float(rec[i]), null95=float(n95[i]), null_mean=float(nul[i].mean()),
                                 persistence=float(np.median(run_[on0, i])) if on0.any() else 0.0, persistence_n=int(on0.sum()),
                                 heldout=o))
            S["families"] += len(pats)
            S["recurrence"] += rec.tolist()
            S["null95"] += n95.tolist()
            S["null_all"] = S.get("null_all", []) + nul.ravel().tolist()
            S["above"] += int((rec > n95).sum())
            print(f"{model} k={kw} {h}: {len(G)} nonzero v's -> {len(pats)} families, held out on {o} "
                  f"({len(Dw[kw][o][1])} pairs; {time.time() - t0:.0f}s)", flush=True)
        summary[kw] = S
    return dict(summary=summary, families=fams, rows=rows, mu=mu)


# ---------------------------------------------------------------- 5: report
def line_marks(Q, q, v, n, plies):
    """The plies (1-based) where v . z >= 0.5 in line q."""
    z = Q[q * (plies + 1):(q + 1) * (plies + 1)].astype(np.float32) @ v
    z = np.asarray(z.todense()).ravel() if hasattr(z, "todense") else np.ravel(z)
    return {t for t in range(1, n + 1) if z[t] >= 0.5 - 1e-9}


def report(a):
    roots = roots_of(a)
    side = halves(roots)
    _, res = dirs(a, "S")
    q = lambda xs, p: float(np.quantile(xs, p)) if len(xs) else float("nan")
    out = ["# Dynamic concepts with a persistence window", "",
           f"Per model, at {len(roots)} positions ({a.rollouts} rollouts of {a.plies} plies, T = {a.temperature}, the model "
           f"both colours): a latent on at a ply when z > {a.on} x mu_j. Pairs: at each branching point the most-played move "
           f"against every move with >= {a.min_share:.0%} of that point's weight, each by its most frequent line, <= {a.cap} per "
           f"position. LP: min |v|_1 + {a.C} xi s.t. v . (z^c_tau - z^s_tau) >= 1 - xi for tau = t..t+k. Families: Jaccard >= "
           f"{a.jaccard} of supports with a family's core, within one half (25 / 25 positions by game); recurrence: the share "
           f"of the other half's pairs (same k) where the family's mean v (|v|_1 = 1) gives >= 0.5 on every ply of the window; "
           f"null: {a.null} random v's per family on rate-matched latents (firing-rate deciles). Persistence: plies in a row "
           f"from the split with v . d >= 0.5, median over the other half's k = 0 pairs where it is on at the split.", ""]
    rep = {}
    for model in ("S", "W"):
        M = measure(a, model, roots, side)
        if M is None:
            out += [f"## {model}", "", "no lp results yet", ""]
            continue
        run, _ = dirs(a, model)
        out += [f"## {model}", "", "| k | pairs | nonzero v | families | held-out recurrence: median / 90% / max | null 95th: median "
                "| null (every draw): 90% / 99% | families above their null 95th (chance: 5%) |", "|---|---|---|---|---|---|---|---|"]
        for kw, S in M["summary"].items():
            r, n = S["recurrence"], S.get("null_all", [])
            out.append(f"| {kw} | {S['pairs']} | {S['nonzero']:.0%} | {S['families']} | {q(r, .5):.1%} / {q(r, .9):.1%} / "
                       f"{max(r, default=float('nan')):.1%} | {q(S['null95'], .5):.1%} | {q(n, .9):.1%} / {q(n, .99):.1%} | "
                       f"{S['above']} ({S['above'] / max(S['families'], 1):.0%}) |")
        F = sorted(M["families"], key=lambda f: (-f["recurrence"], -f["persistence"]))
        out += ["", f"### {model}: the top {a.top} families by held-out recurrence", "",
                "| # | k | latents (weight) | found in | held out on | recurrence | null 95th | persistence (pairs on at split) | positions found |",
                "|---|---|---|---|---|---|---|---|---|"]
        for i, f in enumerate(F[:a.top]):
            o = sorted(zip(f["weights"], f["latents"]), reverse=True)
            out.append(f"| {i + 1} | {f['k']} | {', '.join(f'{j} ({x:.2f})' for x, j in o[:10])}{' ...' if len(o) > 10 else ''} | "
                       f"{f['half']} ({f['members']} v's) | {f['heldout']} | {f['recurrence']:.1%} | {f['null95']:.1%} | "
                       f"{f['persistence']:.1f} ({f['persistence_n']}) | {', '.join(map(str, f['positions'][:12]))}"
                       f"{' ...' if len(f['positions']) > 12 else ''} |")
        out.append("")
        cache = {}
        for i, f in enumerate(F[:a.show]):
            v = vec(f["latents"], f["weights"], len(M["mu"]))
            cand = sorted(M["rows"][f["k"]][f["heldout"]], key=lambda p: -p["ws"])
            out += [f"#### {model} #{i + 1} (k = {f['k']}): latents {', '.join(map(str, f['latents']))}", ""]
            seen = set()
            for p in cand:
                if p["position"] in seen:
                    continue
                k = p["position"]
                if k not in cache:
                    cache[k] = load_on(run, k, M["mu"], a.on)
                D, _, Q = cache[k]
                mc = line_marks(Q, p["c"], v, p["lc"], a.plies)
                ms = line_marks(Q, p["s"], v, p["ls"], a.plies)
                d = (Q[p["c"] * (a.plies + 1):(p["c"] + 1) * (a.plies + 1)].astype(np.float32)
                     - Q[p["s"] * (a.plies + 1):(p["s"] + 1) * (a.plies + 1)].astype(np.float32)) @ v
                d = np.asarray(d.todense()).ravel()
                if not all(d[t] >= 0.5 - 1e-9 for t in range(p["t"], p["t"] + p["k"] + 1)):
                    continue
                seen.add(k)
                r = roots[k]
                out += [f"position {k} (`{r['fen']}`), split at ply {p['t']}: {p['chosen']} ({p['wc']:.0%} there) vs "
                        f"{p['subpar']} ({p['ws']:.0%})", "", "| chosen | subpar |", "|---|---|",
                        f"| {op.mark(D[p['c']]['sans'], mc, r)} | {op.mark(D[p['s']]['sans'], ms, r)} |",
                        f"| [Lichess]({gd.lichess_line(r, D[p['c']]['sans'])}) | [Lichess]({gd.lichess_line(r, D[p['s']]['sans'])}) |", ""]
                if len(seen) == 3:
                    break
            if not seen:
                out += ["(no held-out pair where it holds)", ""]
        rep[model] = dict(summary={k: {x: y for x, y in S.items() if x != "null_all"} for k, S in M["summary"].items()},
                          families=F)
    (res / "report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    (res / "report.json").write_text(json.dumps(dict(settings=vars(a), halves=side, **rep), default=float), encoding="utf-8")
    print(f"wrote {res / 'report.md'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["play", "plant", "lp", "report"])
    ap.add_argument("--model", choices=["S", "W"], default="S")
    ap.add_argument("--source", default=str(SOURCE), help="the manypositions run: its positions, and S's cached lines")
    ap.add_argument("--cc-run", default="runs/transcend/crosscoder/everything-3m")
    ap.add_argument("--cc", default="Lfinal")
    ap.add_argument("--strong", default="2400", help="a part of S's name")
    ap.add_argument("--rollouts", type=int, default=1024)
    ap.add_argument("--plies", type=int, default=16)
    ap.add_argument("--temperature", type=float, default=0.4)
    ap.add_argument("--on", type=float, default=0.5, help="a latent is on at a ply when z > this x its mean where it fires")
    ap.add_argument("--min-share", type=float, default=0.02, help="a subpar branch: at least this share of the branching point's weight")
    ap.add_argument("--cap", type=int, default=50, help="pairs per position and k")
    ap.add_argument("--ks", default="0,2,4,6")
    ap.add_argument("--C", type=float, default=2.0, help="slack cost; at 1 the LP is degenerate with binary codes (v = 0 always optimal)")
    ap.add_argument("--plant-positions", type=int, default=20)
    ap.add_argument("--jaccard", type=float, default=0.5)
    ap.add_argument("--null", type=int, default=200, help="random v's per family")
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--show", type=int, default=10)
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--max-tokens", type=int, default=300_000)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tag", default="p16-r1024-T0.4-s0")
    a = ap.parse_args()
    dict(play=play, plant=plant, lp=lp, report=report)[a.command](a)


if __name__ == "__main__":
    main()
