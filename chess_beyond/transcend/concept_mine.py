"""Mine dynamic concepts at scale and sort them by how clean they are, for both models.

A concept is a family of LP solutions v: at a decisive branch point (a node reached by >= --node rollouts where the model
plays the chosen move >= --wc of the time), v separates the chosen line from a subpar one on every ply of the window
t..t+k (Schut's LP, continuous activations in units of each latent's mean firing, capped at 3). Solutions from different
branch points join one family when their v's point the same way (cosine >= --sim).

The rollouts are the same in both crosscoder seeds, so each concept is checked against seed 1 at its own branch points:
  agreement  mean pairwise cosine of the seed-1 solutions at those branch points (null: random seed-1 solutions)
  replication correlation, over every ply of every rollout, between the concept's activity (v . z, seed 0) and that of
             its seed-1 counterpart (the mean of those seed-1 solutions) (null: seed-1 means of random solutions)
  board      mean ridge-probe AUC (board one-hot + the move just played -> latent on) of the concept's latents
Tiers:
  replication_own   the same correlation on the concept's own positions only, against the strict null: seed-1 means of
             solutions from OTHER branch points at those positions and k (same positions, different decisions)
  best    replication >= max(--best-r, null95 + 0.3), agreement >= max(--best-a, null95 + 0.2), >= 3 positions, board < 0.85,
          replication_own >= its strict null95 + 0.1
  clean   replication >= null95 + 0.15, agreement >= null95 + 0.1, >= 2 positions, board < 0.85, replication_own >= strict null95
  board   would be best or clean, but its latents are mostly board (mean AUC >= 0.85)
  weak    the rest
  readable  best, and its activating windows (both seeds) share one move theme well above the model's base rate
            (repeats a move, checks, captures, king moves, castling, repeated queen/rook/pawn/knight/bishop moves, quiet)

Stages (each caches its output, so they can run one at a time):
  python transcend/concept_mine.py lp --model S --seed 0      # and --seed 1, and for W
  python transcend/concept_mine.py plant --model S            # planted check of the LP and the families (and W)
  python transcend/concept_mine.py screen --model S           # board probe per latent (and W)
  python transcend/concept_mine.py families --model S
  python transcend/concept_mine.py score --model S
  python transcend/concept_mine.py examples --model S
  python transcend/concept_mine.py report                      # both models: concepts.json, concepts.md
  python transcend/concept_mine.py all                         # everything above, both models

Inputs: runs/transcend/divergence/<tag>/<S|W>/pos-*.npz and mu.json (from divergence.py play), for --tag and --tag1.
Outputs: runs/transcend/divergence/<tag>/mine/ (caches), results/transcend/divergence/<tag>/mine/ (concepts.json, .md).
More positions played with divergence.py play (both tags) give more concepts with no change here."""
import argparse, json, sys, time
from pathlib import Path
from collections import Counter
import numpy as np
from scipy import sparse

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs" / "transcend" / "divergence"
RESULTS = ROOT / "results" / "transcend" / "divergence"
PL = 16


def cache(a):
    d = RUNS / a.tag / "mine"; d.mkdir(parents=True, exist_ok=True); return d


def out_dir(a):
    d = RESULTS / a.tag / "mine"; d.mkdir(parents=True, exist_ok=True); return d


def roots_of(a):
    return json.loads((Path(a.source) / "positions.json").read_text(encoding="utf-8"))


def n_positions(a):
    run = RUNS / a.tag / "S"
    return sum(1 for _ in run.glob("pos-*.npz"))


def load_pos(run, k, mu):
    z = np.load(run / f"pos-{k}.npz"); D = json.loads(str(z["D"]))
    Z = sparse.csr_matrix((z["data"].astype(np.float32), z["indices"], z["indptr"]), shape=tuple(z["shape"]))
    Z.data = np.minimum(Z.data / np.maximum(mu[Z.indices], 1e-6), 3.0)
    return D, Z.tocsr()


def mu_of(run):
    return np.array(json.loads((run / "mu.json").read_text(encoding="utf-8"))["mu"])


def keyof(r):
    return f'{r["pos"]}/{r["t"]}/{r["c"]}/{r["s"]}/{r["k"]}'


# ------------------------------------------------------------------ lp
def pairs_of(D, a):
    out = []
    for t in range(1, PL + 1):
        nodes = {}
        for q, d in enumerate(D):
            if len(d["sans"]) >= t:
                nodes.setdefault(tuple(d["sans"][:t - 1]), {}).setdefault(d["sans"][t - 1], []).append(q)
        for ch in nodes.values():
            if len(ch) < 2: continue
            wt = {m: sum(D[q]["n"] for q in qs) for m, qs in ch.items()}; tot = sum(wt.values())
            best = max(ch, key=lambda m: (wt[m], -ch[m][0]))
            if tot < a.node or wt[best] / tot < a.wc: continue
            for m, qs in ch.items():
                if m != best and wt[m] / tot >= a.min_share:
                    out.append(dict(t=t, c=ch[best][0], s=qs[0], chosen=best, subpar=m, wc=wt[best] / tot, ws=wt[m] / tot, node=tot))
    return out


def solve(dc, ds, C):
    from scipy.optimize import linprog
    act = np.flatnonzero((dc != 0).any(0) | (ds != 0).any(0))
    if not len(act): return [], []
    d = dc[:, act] - ds[:, act]; n = len(act)
    r = linprog(np.r_[np.ones(n), C], A_ub=np.hstack([-d, -np.ones((len(d), 1))]), b_ub=-np.ones(len(d)),
                bounds=[(0, None)] * (n + 1), method="highs-ds")
    if r.status != 0: return [], []
    v = r.x[:n]; nz = v > 1e-6
    return act[nz].tolist(), v[nz].tolist()


def lp(a, model, seed):
    tag = a.tag if seed == 0 else a.tag1
    run = RUNS / tag / model; mu = mu_of(run); ks = [int(x) for x in a.ks.split(",")]
    f = cache(a) / f"lp-{model}-s{seed}.json"
    recs = json.loads(f.read_text()) if f.exists() else []
    done = {r["pos"] for r in recs}; t0 = time.time()
    for pos in range(n_positions(a)):
        if pos in done: continue
        D, Z = load_pos(run, pos, mu); lens = [len(d["sans"]) for d in D]
        for p in pairs_of(D, a):
            for k in ks:
                if min(lens[p["c"]], lens[p["s"]]) < p["t"] + k: continue
                ra, rb = p["c"] * (PL + 1) + p["t"], p["s"] * (PL + 1) + p["t"]
                lat, w = solve(Z[ra:ra + k + 1].toarray(), Z[rb:rb + k + 1].toarray(), a.C)
                recs.append(dict(p, pos=pos, k=k, latents=lat, weights=w))
        if time.time() - t0 > a.budget:          # stop and save; rerunning resumes
            f.write_text(json.dumps(recs)); print(f"lp {model} s{seed}: paused after position {pos} ({len(recs)} records); rerun to resume", flush=True); return False
    f.write_text(json.dumps(recs))
    print(f"lp {model} s{seed}: {len(recs)} records, {sum(1 for r in recs if r['latents'])} nonzero ({time.time() - t0:.0f}s)", flush=True)
    return True


# ------------------------------------------------------------------ screen (board probe)
def screen(a, model):
    import chess
    f = cache(a) / f"screen-{model}.json"
    if f.exists(): print(f"screen {model}: cached", flush=True); return
    roots = roots_of(a); run = RUNS / a.tag / model; mu = mu_of(run)
    X, rows, P = [], [], []
    for pos in range(n_positions(a)):
        z = np.load(run / f"pos-{pos}.npz"); D = json.loads(str(z["D"]))
        M = sparse.csr_matrix((z["data"].astype(np.float32), z["indices"], z["indptr"]), shape=tuple(z["shape"]))
        M.data = (M.data > 0.5 * mu[M.indices]).astype(np.float32); M.eliminate_zeros(); M = M.tocsr()
        for q, d in enumerate(D[:a.screen_lines]):
            b = chess.Board(roots[pos]["fen"])
            for t, m in enumerate(d["sans"], 1):
                mv = b.parse_san(m); pt = b.piece_type_at(mv.from_square)
                x = np.zeros(910, np.float32)
                x[768 + pt - 1] = 1; x[774] = b.is_capture(mv); x[775] = b.is_castling(mv); x[776] = mv.promotion is not None
                x[778 + mv.to_square] = 1; x[842 + mv.from_square] = 1; x[906] = b.turn
                b.push(mv); x[777] = b.is_check()
                for sq, pc in b.piece_map().items(): x[(pc.piece_type - 1 + 6 * (not pc.color)) * 64 + sq] = 1
                x[909] = 1; X.append(x); rows.append(M[q * (PL + 1) + t]); P.append(pos)
    X = np.array(X); P = np.array(P); Y = sparse.vstack(rows).tocsc()
    tr = P < int(0.7 * n_positions(a)); te = ~tr
    G = X[tr].T @ X[tr]; INV = [np.linalg.inv(G + l * np.eye(X.shape[1])) for l in (1, 30, 300, 3000)]
    def auc(s, y):
        o = np.argsort(s); r = np.empty(len(o)); r[o] = np.arange(1, len(o) + 1); n1 = y.sum(); n0 = len(y) - n1
        return float((r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)) if n1 and n0 else None
    out = []
    for j0 in range(0, Y.shape[1], 512):
        Yc = Y[:, j0:j0 + 512].toarray(); XY = X[tr].T @ Yc[tr]; preds = [X[te] @ (Ai @ XY) for Ai in INV]
        for k in range(Yc.shape[1]):
            y = Yc[te, k] > 0
            out.append(max((auc(p[:, k], y) or 0) for p in preds) if y.sum() >= 10 and (~y).sum() >= 10 else None)
    f.write_text(json.dumps(dict(auc=out, rate=np.asarray(Y.mean(0)).ravel().tolist())))
    print(f"screen {model}: {sum(v is not None and v < 0.85 for v in out)} of {sum(v is not None for v in out)} measurable latents below AUC 0.85", flush=True)


# ------------------------------------------------------------------ plant (sanity check of lp + families)
def plant(a, model="S"):
    """At --plant-positions positions, one decisive pair each (k = 4): the same 3 latents switched on (1.5 x their mean)
    at plies t..t+4 of the chosen line only, latents off in both lines there and firing on 1-30% of plies. Then the LP on
    each planted pair, and the families pass over the real solutions with the planted ones swapped in.
    Pass: the LP's v holds only planted latents, and one family forms whose centroid is >= 80% planted latents."""
    rng = np.random.default_rng(a.seed_rng); run = RUNS / a.tag / model; mu = mu_of(run); k = 4
    R = json.loads((cache(a) / f"lp-{model}-s0.json").read_text())
    rate = np.zeros(4096); rows = 0
    for p in range(n_positions(a)):
        z = np.load(run / f"pos-{p}.npz"); rate += z["vcnt"]; rows += int(z["shape"][0])
    rate /= max(rows, 1); pool = np.flatnonzero((rate > 0.01) & (rate < 0.3))
    ps = rng.permutation(n_positions(a))[:a.plant_positions]; chosen = None; planted = []
    for p in ps:
        D, Z = load_pos(run, p, mu); lens = [len(d["sans"]) for d in D]
        prs = [q for q in pairs_of(D, a) if min(lens[q["c"]], lens[q["s"]]) >= q["t"] + k]
        if not prs: continue
        q = prs[rng.integers(len(prs))]; ra, rb = q["c"] * (PL + 1) + q["t"], q["s"] * (PL + 1) + q["t"]
        zc, zs = Z[ra:ra + k + 1].toarray(), Z[rb:rb + k + 1].toarray()
        off = pool[(zc[:, pool] == 0).all(0) & (zs[:, pool] == 0).all(0)]
        if chosen is None:
            if len(off) < 3: continue
            chosen = [int(x) for x in rng.choice(off, 3, replace=False)]
        if not all(j in off for j in chosen): continue
        zc[:, chosen] = 1.5
        lat, w = solve(zc, zs, a.C)
        planted.append(dict(q, pos=int(p), k=k, latents=lat, weights=w))
    hits = [set(r["latents"]) <= set(chosen) and len(r["latents"]) > 0 for r in planted]
    # families with the planted solutions in place of the real ones at the same keys
    keys = {keyof(r) for r in planted}
    allr = [r for r in R if r["latents"] and keyof(r) not in keys] + [r for r in planted if r["latents"]]
    V = np.array([unit(r) for r in allr]); order = np.argsort([-len(r["latents"]) for r in allr], kind="stable")
    cents, mem = [], []
    for i in order:
        if cents:
            s_ = np.array(cents) @ V[i]; j = int(s_.argmax())
            if s_[j] >= a.sim:
                mem[j].append(int(i)); c = V[mem[j]].mean(0); cents[j] = c / np.linalg.norm(c); continue
        cents.append(V[i].copy()); mem.append([int(i)])
    pl_idx = set(range(len(allr) - sum(1 for r in planted if r["latents"]), len(allr)))
    best = max(range(len(mem)), key=lambda j: len(pl_idx & set(mem[j])))
    c = cents[best]; share = float((c[chosen] ** 2).sum() / (c ** 2).sum())
    res = dict(planted_latents=chosen, pairs=len(planted), lp_only_planted=int(sum(hits)),
               family_members=len(mem[best]), planted_in_family=len(pl_idx & set(mem[best])), family_planted_share=round(share, 3))
    (out_dir(a) / f"plant-{model}.json").write_text(json.dumps(res))
    print(f"plant {model}: {res}; pass = {sum(hits) >= 0.8 * len(planted) and share >= 0.8 and res['planted_in_family'] >= 0.8 * len(planted)}", flush=True)


# ------------------------------------------------------------------ families
def unit(r):
    x = np.zeros(4096, np.float32); x[r["latents"]] = r["weights"]; n = np.linalg.norm(x); return x / n if n else x


def families(a, model):
    R = [r for r in json.loads((cache(a) / f"lp-{model}-s0.json").read_text()) if r["latents"]]
    V = np.array([unit(r) for r in R])
    order = np.argsort([-len(r["latents"]) for r in R], kind="stable")
    cents, mem = [], []
    for i in order:
        if cents:
            s = np.array(cents) @ V[i]; j = int(s.argmax())
            if s[j] >= a.sim:
                mem[j].append(int(i)); c = V[mem[j]].mean(0); cents[j] = c / np.linalg.norm(c); continue
        cents.append(V[i].copy()); mem.append([int(i)])
    # one reassignment pass: every solution to its nearest centroid
    C = np.array(cents); S = V @ C.T; best = S.argmax(1); ok = S[np.arange(len(V)), best] >= a.sim
    mem = [[] for _ in cents]
    for i in np.flatnonzero(ok): mem[best[i]].append(int(i))
    F = []
    for m in mem:
        if len(m) < a.min_members: continue
        pos = {R[i]["pos"] for i in m}
        if len(pos) < a.min_positions: continue
        c = V[m].mean(0); c /= np.linalg.norm(c)
        F.append(dict(members=[keyof(R[i]) for i in m], n=len(m), positions=len(pos), ks=dict(Counter(str(R[i]["k"]) for i in m)),
                      tight=round(float((V[m] @ c).mean()), 3), centroid={int(j): round(float(c[j]), 4) for j in np.flatnonzero(c > 1e-3)}))
    F.sort(key=lambda f: -f["n"])
    (cache(a) / f"families-{model}.json").write_text(json.dumps(F))
    print(f"families {model}: {len(R)} solutions -> {len(F)} families with >= {a.min_members} members at >= {a.min_positions} positions", flush=True)


# ------------------------------------------------------------------ score
def dense(cent):
    x = np.zeros(4096, np.float32)
    for j, w in cent.items(): x[int(j)] = w
    return x


def score(a, model):
    rng = np.random.default_rng(a.seed)
    F = json.loads((cache(a) / f"families-{model}.json").read_text())
    R1 = {keyof(r): r for r in json.loads((cache(a) / f"lp-{model}-s1.json").read_text())}
    pool = [unit(r) for r in R1.values() if r["latents"]]; Pm = np.array(pool)
    scr = json.loads((cache(a) / f"screen-{model}.json").read_text())["auc"]
    C0 = np.array([dense(f["centroid"]) for f in F]).T                     # 4096 x F
    C1 = np.zeros_like(C0); agree = np.full(len(F), np.nan); agree_null = {}
    def coh(W):
        if len(W) < 2: return np.nan
        S = W @ W.T; n = len(W); return float((S.sum() - n) / (n * (n - 1)))
    for i, f in enumerate(F):
        W1 = np.array([unit(R1[k]) for k in f["members"] if k in R1 and R1[k]["latents"]])
        f["in_seed1"] = int(len(W1))
        if len(W1):
            c = W1.mean(0); C1[:, i] = c / max(np.linalg.norm(c), 1e-9); agree[i] = coh(W1)
            m = min(len(W1), 40)
            if m not in agree_null:
                agree_null[m] = float(np.nanpercentile([coh(Pm[rng.choice(len(Pm), m, replace=False)]) for _ in range(200)], 95))
            f["agreement_null95"] = round(agree_null[m], 3)
        f["agreement"] = None if np.isnan(agree[i]) else round(float(agree[i]), 3)
        lat = [int(j) for j in f["centroid"]]; w = np.array([f["centroid"][str(j)] if str(j) in f["centroid"] else f["centroid"][j] for j in f["centroid"]])
        au = np.array([scr[j] if scr[j] is not None else np.nan for j in lat]); ok = ~np.isnan(au)
        f["board"] = round(float((au[ok] * w[ok]).sum() / w[ok].sum()), 3) if ok.any() else None
    NP = np.array([Pm[rng.choice(len(Pm), 5, replace=False)].mean(0) for _ in range(a.null)]).T   # 4096 x null
    run0, run1 = RUNS / a.tag / model, RUNS / a.tag1 / model; mu0, mu1 = mu_of(run0), mu_of(run1)
    n = 0; s0 = np.zeros(len(F)); s00 = np.zeros(len(F)); s1 = np.zeros(len(F)); s11 = np.zeros(len(F)); s01 = np.zeros(len(F))
    sn = np.zeros(a.null); snn = np.zeros(a.null); s0n = np.zeros((len(F), a.null))
    for pos in range(n_positions(a)):
        _, Z0 = load_pos(run0, pos, mu0); _, Z1 = load_pos(run1, pos, mu1)
        T0 = np.asarray(Z0 @ C0); T1 = np.asarray(Z1 @ C1); TN = np.asarray(Z1 @ NP)
        n += len(T0); s0 += T0.sum(0); s00 += (T0 ** 2).sum(0); s1 += T1.sum(0); s11 += (T1 ** 2).sum(0); s01 += (T0 * T1).sum(0)
        sn += TN.sum(0); snn += (TN ** 2).sum(0); s0n += T0.T @ TN
    def corr(sx, sxx, sy, syy, sxy):
        cov = sxy / n - (sx / n) * (sy / n); vx = sxx / n - (sx / n) ** 2; vy = syy / n - (sy / n) ** 2
        return cov / np.sqrt(np.maximum(vx * vy, 1e-12))
    r = corr(s0, s00, s1, s11, s01)
    rn = corr(s0[:, None], s00[:, None], sn[None, :], snn[None, :], s0n)
    # the strict test, on the concept's own positions only: its seed-1 counterpart against seed-1 means of solutions from
    # OTHER branch points at the same positions and k (same positions, different decisions)
    byk = {}
    for kk, rr_ in R1.items():
        if rr_["latents"]: byk.setdefault((rr_["pos"], rr_["k"]), []).append(kk)
    NV = []
    for i, f in enumerate(F):
        mem = set(f["members"]); ps = {int(k_.split("/")[0]) for k_ in mem}; ks_ = {int(k_.split("/")[4]) for k_ in mem}
        cand = [k_ for p_ in ps for kk in ks_ for k_ in byk.get((p_, kk), []) if k_ not in mem]
        m = max(2, min(f["in_seed1"], 10)); draws = []
        for _ in range(a.strict_null):
            if len(cand) < m: break
            c = np.array([unit(R1[cand[j]]) for j in rng.choice(len(cand), m, replace=False)]).mean(0); draws.append(c / max(np.linalg.norm(c), 1e-9))
        NV.append(np.array(draws).T if draws else np.zeros((4096, 0), np.float32)); f["_ps"] = sorted(ps)
    acc = [dict(n=0, s=np.zeros(3 + 2 * NV[i].shape[1])) for i in range(len(F))]
    S0 = [dict() for _ in F]
    for pos in range(n_positions(a)):
        fi = [i for i, f in enumerate(F) if pos in f["_ps"]]
        if not fi: continue
        _, Z0 = load_pos(run0, pos, mu0); _, Z1 = load_pos(run1, pos, mu1)
        for i in fi:
            x = np.asarray(Z0 @ C0[:, i]).ravel(); y = np.asarray(Z1 @ C1[:, i]).ravel(); Y = np.asarray(Z1 @ NV[i]) if NV[i].shape[1] else np.zeros((len(x), 0))
            d = S0[i]
            for nm, val in (("n", len(x)), ("x", x.sum()), ("xx", (x * x).sum()), ("y", y.sum()), ("yy", (y * y).sum()), ("xy", (x * y).sum()),
                            ("Y", Y.sum(0)), ("YY", (Y * Y).sum(0)), ("xY", x @ Y)):
                d[nm] = d.get(nm, 0) + val
    for i, f in enumerate(F):
        d = S0[i]; nn = d["n"]
        def cc(sx, sxx, sy, syy, sxy):
            cov = sxy / nn - (sx / nn) * (sy / nn); vx = sxx / nn - (sx / nn) ** 2; vy = syy / nn - (sy / nn) ** 2
            return cov / np.sqrt(np.maximum(vx * vy, 1e-12))
        f["replication_own"] = round(float(cc(d["x"], d["xx"], d["y"], d["yy"], d["xy"])), 3)
        rs = cc(d["x"], d["xx"], d["Y"], d["YY"], d["xY"]) if np.size(d["Y"]) else np.array([1.0])
        f["replication_own_null95"] = round(float(np.percentile(rs, 95)), 3); f["strict_null_draws"] = int(np.size(d["Y"]))
        del f["_ps"]
    for i, f in enumerate(F):
        f["replication"] = round(float(r[i]), 3); f["replication_null95"] = round(float(np.percentile(rn[i], 95)), 3)
        f["seed1_counterpart"] = {int(j): round(float(C1[j, i]), 4) for j in np.argsort(-C1[:, i])[:8] if C1[j, i] > 1e-3}
        an = f.get("agreement_null95", 1.0); ag = f["agreement"] if f["agreement"] is not None else -1; rr = f["replication"]; rnull = f["replication_null95"]
        nb = f["board"] is None or f["board"] < a.board_max
        ro, rs = f["replication_own"], f["replication_own_null95"]; strict = f["strict_null_draws"] >= 10
        best = rr >= max(a.best_r, rnull + 0.3) and ag >= max(a.best_a, an + 0.2) and f["positions"] >= 3 and strict and ro >= rs + 0.1
        clean = rr >= rnull + 0.15 and ag >= an + 0.1 and f["positions"] >= 2 and strict and ro >= rs
        f["tier"] = ("best" if best else "clean") if (best or clean) and nb else ("board" if best or clean else "weak")
        f["cleanliness"] = round(float((rr - rnull) + (ag - an) + (ro - rs) + 0.05 * min(f["positions"], 10)), 3)
    (cache(a) / f"scored-{model}.json").write_text(json.dumps(F))
    print(f"score {model}: " + ", ".join(f"{t} {c}" for t, c in Counter(f["tier"] for f in F).most_common()), flush=True)


# ------------------------------------------------------------------ examples
def examples(a, model):
    import chess
    roots = roots_of(a); F = json.loads((cache(a) / f"scored-{model}.json").read_text())
    R0 = {keyof(r): r for r in json.loads((cache(a) / f"lp-{model}-s0.json").read_text())}
    run0, run1 = RUNS / a.tag / model, RUNS / a.tag1 / model; mu0, mu1 = mu_of(run0), mu_of(run1)
    keep = [i for i, f in enumerate(F) if f["tier"] in ("best", "clean", "board")] + \
           [i for i, f in enumerate(F) if f["tier"] == "weak"][:a.weak_examples]
    def nums(fen, sans):
        b = chess.Board(fen); o = []
        for i, m in enumerate(sans):
            w = b.turn; nn = b.fullmove_number; o.append((f"{nn}." if w else (f"{nn}..." if i == 0 else "")) + m); b.push_san(m)
        return o
    def sq(m): return [chess.square_name(m.from_square), chess.square_name(m.to_square)]
    C0 = np.array([dense(F[i]["centroid"]) for i in keep]).T
    C1 = np.array([dense(F[i]["seed1_counterpart"]) for i in keep]).T
    K = [int(max(F[i]["ks"], key=lambda x: F[i]["ks"][x])) for i in keep]
    best0 = [dict() for _ in keep]; best1 = [dict() for _ in keep]; L = {}
    for pos in range(n_positions(a)):
        D, Z0 = load_pos(run0, pos, mu0); _, Z1 = load_pos(run1, pos, mu1); L[pos] = D
        lens = np.array([len(d["sans"]) for d in D])
        for (Zs, C, store) in ((Z0, C0, best0), (Z1, C1, best1)):
            A = np.asarray(Zs @ C).reshape(len(D), PL + 1, len(keep))
            for k in sorted(set(K)):
                idx = [j for j, kk in enumerate(K) if kk == k]
                Wm = np.stack([A[:, t:t + k + 1][:, :, idx].min(1) for t in range(1, PL - k + 1)], 1)
                valid = np.stack([lens >= t + k for t in range(1, PL - k + 1)], 1); Wm[~valid] = -1
                flat = Wm.reshape(-1, len(idx)); arg = flat.argmax(0)
                for c, j in enumerate(idx):
                    q, t = divmod(int(arg[c]), PL - k)
                    store[j][pos] = (float(flat[arg[c], c]), int(q), int(t) + 1)
    def window(pos, q, t, k, sc):
        D = L[pos]; root = roots[pos]; sans = D[q]["sans"]; b = chess.Board(root["fen"])
        for m in sans[:t - 1]: b.push_san(m)
        return dict(pos=pos, score=round(sc, 2), t=t, k=k, line=nums(root["fen"], sans), fen=b.fen(), side="White" if b.turn else "Black",
                    arrow=sq(b.parse_san(sans[t - 1])), games=D[q]["n"], band=root["band"], game=root["game"])
    for j, i in enumerate(keep):
        f = F[i]; k = K[j]
        f["activating"] = [window(p, q, t, k, sc) for p, (sc, q, t) in sorted(best0[j].items(), key=lambda kv: -kv[1][0])[:a.n_examples] if sc > 0]
        f["activating_seed1"] = [window(p, q, t, k, sc) for p, (sc, q, t) in sorted(best1[j].items(), key=lambda kv: -kv[1][0])[:3] if sc > 0]
        v = dense(f["centroid"]); bps, seen = [], set()
        for key in sorted(f["members"], key=lambda k_: -R0[k_]["node"]):
            r = R0[key]
            if r["pos"] in seen: continue
            seen.add(r["pos"]); D = L[r["pos"]]; root = roots[r["pos"]]; b = chess.Board(root["fen"])
            for m in D[r["c"]]["sans"][:r["t"] - 1]: b.push_san(m)
            _, Z0 = load_pos(run0, r["pos"], mu0)
            act = lambda q, nn: [round(float(x), 2) for x in np.asarray(Z0[q * (PL + 1):(q + 1) * (PL + 1)] @ v).ravel()[1:nn + 1]]
            bps.append(dict(pos=r["pos"], t=r["t"], k=r["k"], chosen=r["chosen"], subpar=r["subpar"], wc=round(r["wc"], 3), ws=round(r["ws"], 3), node=r["node"],
                            fen=b.fen(), side="White" if b.turn else "Black", arrows=[sq(b.parse_san(r["chosen"])), sq(b.parse_san(r["subpar"]))],
                            cline=nums(root["fen"], D[r["c"]]["sans"]), sline=nums(root["fen"], D[r["s"]]["sans"]),
                            cact=act(r["c"], len(D[r["c"]]["sans"])), sact=act(r["s"], len(D[r["s"]]["sans"]))))
            if len(bps) == a.n_branch: break
        f["branch_points"] = bps
    (cache(a) / f"examples-{model}.json").write_text(json.dumps(F, default=int))
    print(f"examples {model}: {len(keep)} concepts with examples", flush=True)


# ------------------------------------------------------------------ themes
THEMES = ["repeats a move", "check", "two or more checks", "capture", "two or more captures", "king move", "castles",
          "two or more queen moves", "two or more rook moves", "two or more pawn moves", "two or more knight moves",
          "two or more bishop moves", "no capture or check"]


def window_themes(moves):
    """Themes of a window from its SAN alone (move numbers stripped)."""
    sans = [m.split(".")[-1] for m in moves]
    piece = lambda m: "K" if m.startswith("O-O") else (m[0] if m[0] in "KQRBN" else "P")
    cnt = Counter(piece(m) for m in sans)
    # a side repeating one of its own moves, or shuffling back (Kg8 ... Kh8 ... Kg8)
    own = [sans[i::2] for i in (0, 1)]
    rep = any(len(set(x)) < len(x) for x in own)
    caps = sum("x" in m for m in sans); chks = sum("+" in m or "#" in m for m in sans)
    return [rep, chks >= 1, chks >= 2, caps >= 1, caps >= 2, cnt["K"] > 0 and not any(m.startswith("O-O") for m in sans),
            any(m.startswith("O-O") for m in sans), cnt["Q"] >= 2, cnt["R"] >= 2, cnt["P"] >= 2, cnt["N"] >= 2, cnt["B"] >= 2,
            caps == 0 and chks == 0]


def add_themes(F):
    """Per concept: the theme its activating windows (both seeds) share most, against the model's base rate."""
    allw = [window_themes(x["line"][x["t"] - 1:x["t"] + x["k"]]) for f in F for x in f.get("activating", []) + f.get("activating_seed1", [])]
    base = np.array(allw, float).mean(0) if allw else np.zeros(len(THEMES))
    for f in F:
        W = [window_themes(x["line"][x["t"] - 1:x["t"] + x["k"]]) for x in f.get("activating", []) + f.get("activating_seed1", [])]
        if len(W) < 4: f["theme"] = None; f["coherence"] = None; continue
        share = np.array(W, float).mean(0); lift = share / np.maximum(base, 1e-6)
        score_ = (share - base) * (share >= 0.6)
        j = int(score_.argmax())
        f["coherence"] = round(float(share[j] - base[j]), 3)
        f["theme"] = dict(name=THEMES[j], share=round(float(share[j]), 2), base=round(float(base[j]), 2), lift=round(float(lift[j]), 2)) if score_[j] > 0.15 and lift[j] >= 1.5 else None


# ------------------------------------------------------------------ report
def report(a):
    out = {}; md = ["# Mined dynamic concepts", "",
                    f"Tag {a.tag}, checked against {a.tag1}. Decisive branch points: >= {a.node} rollouts, chosen move >= {a.wc:.0%}. "
                    f"k in {a.ks}. Families: cosine >= {a.sim}, >= {a.min_members} solutions at >= {a.min_positions} positions.", ""]
    cents = {}
    for model in ("S", "W"):
        f_ = cache(a) / f"examples-{model}.json"
        if not f_.exists(): md += [f"## {model}", "", "not mined yet", ""]; continue
        F = json.loads(f_.read_text())
        for i, f in enumerate(F): f["id"] = f"{model}{i}"
        add_themes(F)
        for f in F: f["readable"] = bool(f["tier"] == "best" and f["theme"] is not None)
        cents[model] = np.array([dense(f["centroid"]) for f in F])
        tiers = Counter(f["tier"] for f in F)
        md += [f"## {model}", "", ", ".join(f"{t}: {tiers.get(t, 0)}" for t in ("best", "clean", "board", "weak")) +
               f"; best with a clear theme in its examples: {sum(f['readable'] for f in F)}", "",
               "### Best, with a theme", "", "| concept | theme (share of windows / base rate) | branch points | positions | replication | agreement | chosen > subpar at branch points | activating windows |", "|---|---|---|---|---|---|---|---|"]
        for f in sorted([f for f in F if f["readable"]], key=lambda f: -f["coherence"]):
            bp = "; ".join(f'{b["chosen"]} > {b["subpar"]}' for b in f.get("branch_points", [])[:4])
            win = " / ".join(" ".join(x["line"][x["t"] - 1:x["t"] + x["k"]]) for x in f.get("activating", [])[:3])
            md.append(f"| {f['id']} | {f['theme']['name']} ({f['theme']['share']:.0%} / {f['theme']['base']:.0%}) | {f['n']} | {f['positions']} | {f['replication']} | {f['agreement']} | {bp} | {win} |")
        md += ["", "### Best and clean, by cleanliness", "",
               "| concept | tier | branch points | positions | k | replication (null 95th) | agreement (null 95th) | board | top activating windows |",
               "|---|---|---|---|---|---|---|---|---|"]
        for f in sorted([f for f in F if f["tier"] in ("best", "clean")], key=lambda f: -f["cleanliness"])[:a.md_rows]:
            win = " / ".join(" ".join(x["line"][x["t"] - 1:x["t"] + x["k"]]) for x in f.get("activating", [])[:3])
            md.append(f"| {f['id']} | {f['tier']} | {f['n']} | {f['positions']} | {','.join(sorted(f['ks']))} | {f['replication']} ({f['replication_null95']}) | "
                      f"{f['agreement']} ({f.get('agreement_null95')}) | {f['board']} | {win} |")
        md.append("")
        out[model] = F
    if "S" in cents and "W" in cents:
        S = cents["S"] @ cents["W"].T
        for i, f in enumerate(out["S"]): j = int(S[i].argmax()); f["match"] = dict(id=f"W{j}", cos=round(float(S[i, j]), 3))
        for j, f in enumerate(out["W"]): i = int(S[:, j].argmax()); f["match"] = dict(id=f"S{i}", cos=round(float(S[i, j]), 3))
    for model, F in out.items():
        C = cents[model]; SS = C @ C.T
        out[model] = dict(concepts=F, edges=[dict(a=i, b=j, cos=round(float(SS[i, j]), 3)) for i in range(len(F)) for j in range(i + 1, len(F)) if SS[i, j] >= a.edge])
    od = out_dir(a)
    (od / "concepts.json").write_text(json.dumps(dict(settings=vars(a), **out), default=int))
    (od / "concepts.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"wrote {od / 'concepts.json'} and concepts.md", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["lp", "plant", "screen", "families", "score", "examples", "report", "all"])
    ap.add_argument("--model", choices=["S", "W"], default="S")
    ap.add_argument("--seed", type=int, choices=[0, 1], default=0, help="lp: which crosscoder seed's codes")
    ap.add_argument("--tag", default="p16-r1024-T0.4-s0-L11-4k")
    ap.add_argument("--tag1", default="p16-r1024-T0.4-s0-L11-4k-s1")
    ap.add_argument("--source", default=str(ROOT / "runs/transcend/manypositions/p16-r1024-T0.4-s0"))
    ap.add_argument("--node", type=int, default=30, help="rollouts that must reach a branch point")
    ap.add_argument("--wc", type=float, default=0.75, help="the chosen move's share there")
    ap.add_argument("--min-share", type=float, default=0.02)
    ap.add_argument("--ks", default="2,3,4,5,6,8")
    ap.add_argument("--C", type=float, default=2.0)
    ap.add_argument("--sim", type=float, default=0.5)
    ap.add_argument("--min-members", type=int, default=3)
    ap.add_argument("--min-positions", type=int, default=2)
    ap.add_argument("--screen-lines", type=int, default=25)
    ap.add_argument("--plant-positions", type=int, default=20)
    ap.add_argument("--null", type=int, default=300)
    ap.add_argument("--strict-null", type=int, default=40, help="score: draws for the same-positions null")
    ap.add_argument("--best-r", type=float, default=0.6)
    ap.add_argument("--best-a", type=float, default=0.25)
    ap.add_argument("--board-max", type=float, default=0.85)
    ap.add_argument("--weak-examples", type=int, default=40, help="also give examples to the largest weak concepts")
    ap.add_argument("--n-examples", type=int, default=6)
    ap.add_argument("--n-branch", type=int, default=5)
    ap.add_argument("--edge", type=float, default=0.25)
    ap.add_argument("--md-rows", type=int, default=60)
    ap.add_argument("--budget", type=float, default=1e9, help="lp: seconds before pausing (rerun resumes)")
    ap.add_argument("--seed-rng", dest="seed_rng", type=int, default=0)
    a = ap.parse_args(); a.seed_ = a.seed; a.seed = a.seed_rng if a.command != "lp" else a.seed
    if a.command == "lp": lp(a, a.model, a.seed_)
    elif a.command == "plant": plant(a, a.model)
    elif a.command == "screen": screen(a, a.model)
    elif a.command == "families": families(a, a.model)
    elif a.command == "score": a.seed = a.seed_rng; score(a, a.model)
    elif a.command == "examples": examples(a, a.model)
    elif a.command == "report": report(a)
    else:
        for m in ("S", "W"):
            lp(a, m, 0); lp(a, m, 1); plant(a, m); screen(a, m); families(a, m); a.seed = a.seed_rng; score(a, m); examples(a, m)
        report(a)


if __name__ == "__main__":
    main()
