"""A map of the L11 4k crosscoder's latents laid out by how play combines them, with the mined concepts drawn on it.

Nodes   latents of seed 0 that match a seed-1 latent (mutual best decoder cosine, both models' decoders, > --match-cos;
        crossmix.py match's rule) and are on at >= --min-rate of rollout plies. On: z > 0.5 x mu_j, mu_j the mean of the
        two models' mu (one threshold for both, so S and W counts compare).
Layout  over every ply t >= 1 of every rollout line (weighted by how many rollouts played it) at every night1 position
        (discovery and confirmation), S and W pooled: P(i), P(i, j) = share of plies where i is on, where i and j are both
        on; PPMI = max(0, log P(i, j) / P(i) P(j)). Placed by layout(): communities, then a stress layout within and
        between them, of one graph holding the latents (each joined to its strongest play partners by PPMI) and every
        concept of both models (joined to its latents), so every latent has one place in all three views.
Edges   per model, the mined concepts that replicate across seeds (overnight_confirm.py choose's rule 1); each a star from
        its own node to its latents, the concept being its centroid's top latents
        covering 95% of the squared weight (keep95), restricted to the nodes. Colour: persistence (the old reports' rule:
        plies in a row from the split with v . (z_chosen - z_subpar) >= 0.5, |v|_1 = 1, median over its branch points where
        it is on at the split). Size: discovery positions it was found at.
G_diff  concepts whose best match in the other model (report()'s centroid cosine) is below --absent-cos, plus dPMI edges:
        PMI_S - PMI_W (counts + 0.5) per pair with >= --min-pair co-occurring plies pooled, over its sd under random S/W
        swaps by position (the positions are shared, so a swap is a fair null; sd analytic, linearised, over every
        position); kept when |z| beats the 95th percentile of the largest |z| over all pairs in --perms actual swaps
        (maxT, family-wise over every pair).

    python transcend/interp/concept_graph.py build      # CPU, a few minutes: runs/transcend/overnight/<name>/graph.npz, .json
    python transcend/interp/concept_graph.py layout     # CPU, under a minute: places the nodes (into graph.json)
    python transcend/interp/concept_graph.py examples   # CPU, a few minutes: examples for the edges (into graph.json)
    python transcend/interp/concept_graph.py pairs      # CPU, resumable: each concept's examples as pairs from one board (into graph.json)
    python transcend/interp/concept_graph.py rank       # CPU, seconds: results/transcend/overnight/<name>-rank.md (concepts ranked for reading)
    python transcend/interp/concept_graph.py page       # results/transcend/overnight/<name>-graph.html (and -graph.json, its data)

The page is concept_graph.html with the data put in. To change the page only, edit concept_graph.html and run page: it
reads results/transcend/overnight/<name>-graph.json when runs/ is absent (build, layout and examples need runs/).
"""
import argparse, json, sys, time
from pathlib import Path
import numpy as np
from scipy import sparse

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # chess_beyond/
import paths  # noqa: E402
from concept_mine import PL, pairs_of, keyof  # noqa: E402
from overnight_confirm import keep95  # noqa: E402

DIV = paths.RUNS / "transcend" / "divergence"
OV = paths.RUNS / "transcend" / "overnight"
CC = paths.RUNS / "transcend" / "crosscoder" / "mixed-L11"
RES = paths.ROOT / "results" / "transcend" / "overnight"


def seed_match(a):
    import torch
    W = [torch.load(CC / f"cc-L11-4096{s}" / "cc.pt", map_location="cpu", weights_only=False)["state"]["W_dec"].float().flatten(1)
         for s in ("", "-s1")]
    u0, u1 = [torch.nn.functional.normalize(w, dim=1) for w in W]
    C = (u0 @ u1.T).numpy(); b1 = C.argmax(1); b0 = C.argmax(0)
    cos = C[np.arange(len(C)), b1]
    return (b0[b1] == np.arange(len(C))) & (cos > a.match_cos), cos


def raw(f):
    z = np.load(f); D = json.loads(str(z["D"]))
    return D, sparse.csr_matrix((z["data"].astype(np.float32), z["indices"], z["indptr"]), shape=tuple(z["shape"]))


def plies(D):
    """Rows t >= 1 of each line, and each row's weight (the line's rollout count)."""
    rows, w = [], []
    for q, d in enumerate(D):
        for t in range(1, len(d["sans"]) + 1): rows.append(q * (PL + 1) + t); w.append(d["n"])
    return np.array(rows), np.array(w, np.float64)


def files(a, m):
    out = []
    for split in ("disc", "conf"):
        run = DIV / f"{a.prefix}-{split}-s0" / m
        out += [run / f"pos-{k}.npz" for k in range(sum(1 for _ in run.glob("pos-*.npz")))]
    return out


def build(a):
    t0 = time.time()
    mu = {m: np.array(json.loads((DIV / f"{a.prefix}-disc-s0" / m / "mu.json").read_text())["mu"]) for m in "SW"}
    thr = 0.5 * (mu["S"] + mu["W"]) / 2
    matched, mcos = seed_match(a)
    fs = {m: files(a, m) for m in "SW"}; n_pos = len(fs["S"]); assert n_pos == len(fs["W"])
    # pass 1: firing rates of the matched latents, to fix the nodes
    on_cnt = {m: np.zeros(4096) for m in "SW"}; N = {m: 0.0 for m in "SW"}
    def onrows(f, cols=None):
        D, Z = raw(f); r, w = plies(D); X = Z[r]; X.data = (X.data > thr[X.indices]).astype(np.float32); X.eliminate_zeros()
        return (X if cols is None else X[:, cols]).tocsr(), w
    for m in "SW":
        for f in fs[m]:
            X, w = onrows(f); on_cnt[m] += X.T @ w; N[m] += w.sum()
    rate = (on_cnt["S"] + on_cnt["W"]) / (N["S"] + N["W"])
    nodes = np.flatnonzero(matched & (rate >= a.min_rate)); n = len(nodes)
    print(f"nodes: {matched.sum()} seed-matched latents, {n} of them on at >= {a.min_rate:.0e} of plies ({time.time() - t0:.0f}s)", flush=True)
    # pass 2: co-occurrence per model, and the label-swap null for the difference
    rng = np.random.default_rng(a.seed); swap = rng.random((a.perms, n_pos)) < 0.5
    Cm = {m: np.zeros((n, n)) for m in "SW"}; acc = np.zeros((a.perms, n, n), np.float32); Np = {m: np.zeros(n_pos) for m in "SW"}
    A2, Ai, Dij = np.zeros((n, n)), np.zeros((n, n)), np.zeros((n, n))
    for p in range(n_pos):
        Cp = {}
        for m in "SW":
            X, w = onrows(fs[m][p], nodes); Cp[m] = (X.T @ sparse.diags(w) @ X).tocoo(); Np[m][p] = w.sum()
            Cm[m][Cp[m].row, Cp[m].col] += Cp[m].data
        d = (Cp["S"] - Cp["W"]).tocoo()                        # what a swap at p moves from S's total to W's
        for b in np.flatnonzero(swap[:, p]): acc[b, d.row, d.col] += d.data
        dd = (Cp["S"] - Cp["W"]).toarray(); dg = np.diag(dd).copy()   # moments for the analytic swap variance
        A2 += dd * dd; Ai += dd * dg[:, None]; Dij += np.outer(dg, dg)
        if p % 100 == 0: print(f"  co-occurrence: position {p} of {n_pos} ({time.time() - t0:.0f}s)", flush=True)
    def ppmi(C, NN):
        P = C / NN; pi = np.diag(P).copy()
        with np.errstate(divide="ignore", invalid="ignore"):
            x = np.log(P / np.outer(pi, pi))
        x[~np.isfinite(x)] = 0; x = np.maximum(x, 0); np.fill_diagonal(x, 0); return x
    pool = ppmi(Cm["S"] + Cm["W"], N["S"] + N["W"])
    U, s, _ = np.linalg.svd(pool); X3 = U[:, :3] * np.sqrt(s[:3])
    # dPMI = PMI_S - PMI_W, each over its own plies, counts + 0.5 (a pair one model never combines stays finite). Its sd
    # under random S/W swaps by position, analytically: linearised, a swap at p changes dPMI by
    # g_p = -a_ij d_ij + a_ii d_ii + a_jj d_jj (d = C_S(p) - C_W(p), a = 1/C_S + 1/C_W), so var = sum_p g_p^2 / 4,
    # summed exactly over every position. The --perms actual swaps give the family-wise cut (maxT over all pairs).
    def pmi(C, NN):
        P = (C + 0.5) / NN; pi = np.diag(P).copy(); return np.log(P / np.outer(pi, pi))
    support = (Cm["S"] + Cm["W"]) >= a.min_pair; np.fill_diagonal(support, False)
    obs = pmi(Cm["S"], N["S"]) - pmi(Cm["W"], N["W"])
    up = np.triu(support, 1); ii, jj = np.nonzero(up)
    A = 1 / (Cm["S"] + 0.5) + 1 / (Cm["W"] + 0.5); ad = np.diag(A).copy(); Dii = np.diag(Dij).copy()
    aij, ai, aj = A[ii, jj], ad[ii], ad[jj]
    var = 0.25 * (aij ** 2 * A2[ii, jj] + ai ** 2 * Dii[ii] + aj ** 2 * Dii[jj] - 2 * aij * ai * Ai[ii, jj] - 2 * aij * aj * Ai[jj, ii]
                  + 2 * ai * aj * Dij[ii, jj])
    sd = np.sqrt(np.maximum(var, 1e-12)); zobs = obs[ii, jj] / sd; NB = np.zeros((a.perms, len(ii)), np.float32)
    for b in range(a.perms):
        dn = float((Np["S"] - Np["W"])[swap[b]].sum())
        NB[b] = (pmi(Cm["S"] - acc[b], N["S"] - dn) - pmi(Cm["W"] + acc[b], N["W"] + dn))[ii, jj]
    rms = np.sqrt((NB.astype(np.float64) ** 2).mean(0))
    print(f"  analytic sd / swap rms over pairs: median {np.median(sd / rms):.2f}, 5th {np.percentile(sd / rms, 5):.2f}, 95th {np.percentile(sd / rms, 95):.2f}", flush=True)
    mx = np.abs(NB / sd).max(1); cut = float(np.percentile(mx, 95)); keep = np.abs(zobs) > cut
    zfull = np.zeros_like(obs); zfull[ii, jj] = zobs; zfull = zfull + zfull.T
    iu = np.stack([ii[keep], jj[keep]], 1)
    print(f"dPMI: {len(ii)} pairs with support, null max |z| 95th = {cut:.2f}, {len(iu)} pairs beat it "
          f"(S more {int((zobs[keep] > 0).sum())}, W more {int((zobs[keep] < 0).sum())})", flush=True)
    np.savez_compressed(OV / a.name / "graph.npz", nodes=nodes, X3=X3, s=s[:10], rate=rate[nodes], mcos=mcos[nodes],
                        CS=Cm["S"], CW=Cm["W"], N=np.array([N["S"], N["W"]]), null_max=np.array(mx), dpmi=obs, z=zfull)
    dedges = [dict(i=int(i), j=int(j), d=round(float(obs[i, j]), 3), z=round(float(zfull[i, j]), 2), n=int(Cm["S"][i, j] + Cm["W"][i, j]))
              for i, j in iu]
    # concepts
    rep = json.loads((paths.ROOT / "results" / "transcend" / "divergence" / f"{a.prefix}-disc-s0" / "mine" / "concepts.json").read_text())
    where = {int(j): k for k, j in enumerate(nodes)}
    ok = lambda v, nn, dd: v is not None and nn is not None and v >= nn + dd
    concepts = []
    for m in "SW":
        C = [c for c in rep[m]["concepts"] if ok(c.get("replication"), c.get("replication_null95"), 0.15)
             and ok(c.get("agreement"), c.get("agreement_null95"), 0.1) and ok(c.get("replication_own"), c.get("replication_own_null95"), 0.0)]
        R0 = {keyof(r): r for r in json.loads((DIV / f"{a.prefix}-disc-s0" / "mine" / f"lp-{m}-s0.json").read_text())}
        byp = {}
        for c in C:
            for k in c["members"]: byp.setdefault(R0[k]["pos"], []).append((c["id"], R0[k]))
        V = {c["id"]: keep95(c["centroid"]) for c in C}
        runs = {c["id"]: [] for c in C}
        run0 = DIV / f"{a.prefix}-disc-s0" / m
        for p, lst in byp.items():
            D, Z = raw(run0 / f"pos-{p}.npz"); Z.data = np.minimum(Z.data / np.maximum(mu[m][Z.indices], 1e-6), 3.0)
            seen = set()
            for cid, r in lst:
                if (cid, r["t"], r["c"], r["s"]) in seen: continue
                seen.add((cid, r["t"], r["c"], r["s"]))
                lat, w = V[cid]; v = np.array(w) / np.abs(w).sum()
                L = min(len(D[r["c"]]["sans"]), len(D[r["s"]]["sans"]))
                dz = (Z[r["c"] * (PL + 1) + r["t"]:r["c"] * (PL + 1) + L + 1][:, lat].toarray()
                      - Z[r["s"] * (PL + 1) + r["t"]:r["s"] * (PL + 1) + L + 1][:, lat].toarray()) @ v
                if len(dz) and dz[0] >= 0.5:
                    runs[cid].append(int(np.argmin(np.r_[dz, -1] >= 0.5)))
        for c in C:
            lat, w = V[c["id"]]; w = np.array(w)
            keep = [i for i, j in enumerate(lat) if j in where]
            concepts.append(dict(id=c["id"], model=m, lat=[where[lat[i]] for i in keep], latent=[lat[i] for i in keep],
                                 w=[round(float(w[i]), 4) for i in keep], covered=round(float((w[keep] ** 2).sum()), 3), k95=len(lat),
                                 positions=c["positions"], tier=c["tier"], theme=(c.get("theme") or {}).get("name"),
                                 persistence=float(np.median(runs[c["id"]])) if runs[c["id"]] else None, on_at_split=len(runs[c["id"]]),
                                 match=c["match"]["id"], match_cos=c["match"]["cos"], absent=c["match"]["cos"] < a.absent_cos))
    out = dict(settings={k: v for k, v in vars(a).items() if k != "command"}, n_matched=int(matched.sum()), n_positions=n_pos,
               plies=dict(S=N["S"], W=N["W"]), sv=[round(float(x), 2) for x in s[:10]], dpmi_cut=round(cut, 3),
               pairs_supported=int(np.triu(support, 1).sum()),
               nodes=[dict(latent=int(j), x=[round(float(v), 4) for v in X3[k]], rate=round(float(rate[j]), 5), seed_cos=round(float(mcos[j]), 3))
                      for k, j in enumerate(nodes)], concepts=concepts, dedges=dedges)
    (OV / a.name / "graph.json").write_text(json.dumps(out))
    cov = {m: np.median([c["covered"] for c in concepts if c["model"] == m]) for m in "SW"}
    print(f"concepts: S {sum(c['model'] == 'S' for c in concepts)} (absent in W: {sum(c['absent'] for c in concepts if c['model'] == 'S')}), "
          f"W {sum(c['model'] == 'W' for c in concepts)} (absent in S: {sum(c['absent'] for c in concepts if c['model'] == 'W')}); "
          f"median share of squared weight on nodes S {cov['S']:.2f}, W {cov['W']:.2f}; wrote {OV / a.name / 'graph.json'} ({time.time() - t0:.0f}s)", flush=True)


def layout(a):
    """The map. One graph holds every latent and every drawable concept of both models. Edges: each latent to its --knn
    strongest partners in play (PPMI x log(1 + count), pooled; length 1.5 - strength / max) and each concept to its
    latents (length --concept-len x (1.5 - weight)). A concept's latents rarely fire together (median PMI ~0 within a
    concept), so co-occurrence alone scatters them; the concept edges are what keep them together. Louvain communities of
    that graph (--resolution); each community laid out on its own shortest-path distances (classical MDS, then weighted
    SMACOF, w = d^-2), as a ball of radius ~ size^(1/3); the communities placed by their mean distances to one another
    and spread until no two balls overlap (--sep). Scored against random latent sets of the same size: the mean distance
    within concepts (>= 3 latents) and between play partners, each over random."""
    from scipy.sparse import csr_matrix
    from scipy.sparse.csgraph import shortest_path
    z = np.load(OV / a.name / "graph.npz"); g = json.loads((OV / a.name / "graph.json").read_text())
    C = z["CS"] + z["CW"]; n = len(C); P = C / z["N"].sum(); pi = np.diag(P).copy()
    with np.errstate(divide="ignore", invalid="ignore"): PMI = np.log(P / np.outer(pi, pi))
    PMI[~np.isfinite(PMI)] = 0; np.fill_diagonal(PMI, 0)
    M = np.maximum(PMI, 0) * np.log1p(C); np.fill_diagonal(M, 0)
    knn = [(i, int(j), float(M[i, j])) for i in range(n) for j in np.argsort(-M[i])[:a.knn] if M[i, j] > 0]
    mx = max(w for *_, w in knn)
    cons = [k for k, c in enumerate(g["concepts"]) if c["lat"]]; m = n + len(cons)
    r, c_, L = [], [], []
    for i, j, w in knn: r.append(i); c_.append(j); L.append(1.5 - w / mx)
    for q, k in enumerate(cons):
        for kk, w in zip(g["concepts"][k]["lat"], g["concepts"][k]["w"]): r.append(n + q); c_.append(kk); L.append(a.concept_len * (1.5 - w))
    A = csr_matrix((L, (r, c_)), shape=(m, m)); A = A.maximum(A.T)
    D = shortest_path(A, directed=False); fin = np.isfinite(D); D[~fin] = D[fin].max() * 1.2
    # communities of the same graph (Louvain, weight 1 / length)
    import networkx as nx
    Gx = nx.Graph(); Gx.add_nodes_from(range(m)); Ac = A.tocoo()
    Gx.add_weighted_edges_from((int(i), int(j), 1 / w) for i, j, w in zip(Ac.row, Ac.col, Ac.data) if i < j)
    comm = np.zeros(m, int)
    for q, cs in enumerate(sorted(nx.community.louvain_communities(Gx, weight="weight", seed=a.seed, resolution=a.resolution), key=len, reverse=True)):
        comm[list(cs)] = q
    Q = nx.community.modularity(Gx, [set(np.flatnonzero(comm == q)) for q in range(comm.max() + 1)], weight="weight")
    def stress(D_):
        k_ = len(D_)
        if k_ < 4: return np.random.default_rng(a.seed).normal(size=(k_, 3)) * 0.3
        J = np.eye(k_) - 1 / k_; w_, V = np.linalg.eigh(-0.5 * J @ (D_ ** 2) @ J); X_ = V[:, -3:] * np.sqrt(np.maximum(w_[-3:], 0))
        W = 1 / np.maximum(D_, 1e-9) ** 2; np.fill_diagonal(W, 0)
        Vm = -W.copy(); np.fill_diagonal(Vm, W.sum(1)); Vp = np.linalg.pinv(Vm + 1 / k_) - 1 / k_
        for _ in range(a.iters):
            E = np.maximum(np.linalg.norm(X_[:, None] - X_[None], axis=-1), 1e-9)
            B = -W * D_ / E; np.fill_diagonal(B, 0); np.fill_diagonal(B, -B.sum(1)); X_ = Vp @ (B @ X_)
        return X_ - X_.mean(0)
    # two levels: each community laid out on its own distances, as a ball of radius ~ size^(1/3); the communities placed
    # by their mean distances to one another, spread until no two balls overlap (--sep: the gap, x the radii)
    nq = comm.max() + 1; X = np.zeros((m, 3)); rad = np.zeros(nq)
    for q in range(nq):
        idx = np.flatnonzero(comm == q); Xq = stress(D[np.ix_(idx, idx)])
        rad[q] = len(idx) ** (1 / 3); Xq *= rad[q] / max(np.percentile(np.linalg.norm(Xq, axis=1), 95), 1e-9); X[idx] = Xq
    Dc = np.array([[D[np.ix_(comm == p, comm == q)].mean() if p != q else 0 for q in range(nq)] for p in range(nq)])
    Yc = stress(Dc); dc = np.linalg.norm(Yc[:, None] - Yc[None], axis=-1); np.fill_diagonal(dc, np.inf)
    X += Yc[comm] * float(np.max((1 + a.sep) * (rad[:, None] + rad[None]) / dc))
    X = X - X[:n].mean(0); X *= 400 / np.percentile(np.linalg.norm(X[:n], axis=1), 95)
    rng = np.random.default_rng(a.seed); Dn = np.linalg.norm(X[:n, None] - X[None, :n], axis=-1); base = Dn[np.triu_indices(n, 1)].mean()
    spread = lambda L_: Dn[np.ix_(L_, L_)][np.triu_indices(len(L_), 1)].mean()
    big = [g["concepts"][k]["lat"] for k in cons if len(g["concepts"][k]["lat"]) >= 3]
    sc = float(np.median([spread(L_) / np.mean([spread(list(rng.choice(n, len(L_), replace=False))) for _ in range(5)]) for L_ in big]))
    sk = float(np.mean([Dn[i, j] for i, j, _ in knn]) / base)
    wi = [np.mean([PMI[x, y] for i, x in enumerate(L_) for y in L_[i + 1:]]) for L_ in big]
    for k, nd in enumerate(g["nodes"]): nd["p"] = [round(float(v), 2) for v in X[k]]; nd["comm"] = int(comm[k])
    rate = {m_: np.diag(z["C" + m_]) / z["N"][q] for q, m_ in enumerate("SW")}
    for k, nd in enumerate(g["nodes"]): nd["s_share"] = round(float(rate["S"][k] / max(rate["S"][k] + rate["W"][k], 1e-12)), 3)
    for q, k in enumerate(cons): g["concepts"][k]["p"] = [round(float(v), 2) for v in X[n + q]]; g["concepts"][k]["comm"] = int(comm[n + q])
    rep = json.loads((paths.ROOT / "results" / "transcend" / "divergence" / f"{a.prefix}-disc-s0" / "mine" / "concepts.json").read_text())
    src = {f["id"]: f for m_ in "SW" for f in rep[m_]["concepts"]}
    for c in g["concepts"]:
        f = src[c["id"]]
        c["windows"] = [dict(line=x["line"], t=x["t"], k=x["k"], band=x["band"]) for x in f.get("activating", [])[:3]]
        c["bps"] = [dict(chosen=b["chosen"], subpar=b["subpar"], wc=b["wc"], cline=b["cline"][:b["t"] + b["k"]], t=b["t"], k=b["k"])
                    for b in f.get("branch_points", [])[:2]]
    g["layout"] = dict(knn=a.knn, concept_len=a.concept_len, iters=a.iters, sep=a.sep, communities=int(comm.max() + 1), modularity=round(Q, 3), concept_spread=round(sc, 3), neighbour_spread=round(sk, 3),
                       pmi_within_concepts=round(float(np.median(wi)), 3), knn_edges=len(knn))
    (OV / a.name / "graph.json").write_text(json.dumps(g))
    print(f"layout: {m} nodes ({n} latents, {len(cons)} concepts), {len(knn)} play edges, {comm.max() + 1} communities (Q {Q:.2f}); concept spread {sc:.2f} of random, "
          f"play partners {sk:.2f} of random; median PMI within concepts {np.median(wi):.3f}", flush=True)


def examples(a):
    """Examples for the edges, from every rollout ply of both models (values in units of the latent's mu, pooled).
    Concept -> latent edge: the latent's top activating plies (one per position, --n-ex), each with a minimal-pair
    non-activating example: the same position and ply, the line sharing the longest prefix whose latent is off (0) there.
    Plus, at the concept's branch points (its own model's codes), the latent's mean over the window on the chosen line
    and on the subpar one. dPMI pair: plies where both are on (min of the two, top), and where one is on and the other
    off, from the model that combines them more."""
    from concept_mine import nums
    g = json.loads((OV / a.name / "graph.json").read_text()); N = g["nodes"]
    mu = {m: np.array(json.loads((DIV / f"{a.prefix}-disc-s0" / m / "mu.json").read_text())["mu"]) for m in "SW"}
    mup = (mu["S"] + mu["W"]) / 2
    roots = sum((json.loads((OV / a.name / s / "positions.json").read_text(encoding="utf-8")) for s in ("disc", "conf")), [])
    use = sorted({k for c in g["concepts"] for k in c["lat"]} | {e[x] for e in g["dedges"] for x in ("i", "j")})
    cols = np.array([N[k]["latent"] for k in use]); col_of = {k: q for q, k in enumerate(use)}
    fs = {m: files(a, m) for m in "SW"}; t0 = time.time()
    top = [[] for _ in use]                                  # (value, model, file, row)
    pairs = [dict(e=e, m="S" if e["d"] > 0 else "W", both=[], only_i=[], only_j=[]) for e in g["dedges"]]
    def keep(lst, item, n):
        lst.append(item); lst.sort(key=lambda x: -x[0]); del lst[n:]
    for m in "SW":
        for fi, f in enumerate(fs[m]):
            D, Z = raw(f); r, _ = plies(D); X = Z[r][:, cols].toarray() / mup[cols]
            am = X.argmax(0); v = X[am, np.arange(len(cols))]
            for q in np.flatnonzero(v > 0.5): keep(top[q], (float(v[q]), m, fi, int(r[am[q]])), 3 * a.n_ex)
            for p in pairs:
                if p["m"] != m: continue
                xi, xj = X[:, col_of[p["e"]["i"]]], X[:, col_of[p["e"]["j"]]]
                for key, s_ in (("both", np.minimum(xi, xj)), ("only_i", np.where(xj == 0, xi, 0)), ("only_j", np.where(xi == 0, xj, 0))):
                    b = int(s_.argmax())
                    if s_[b] > 0.5: keep(p[key], (float(s_[b]), m, fi, int(r[b]), float(xi[b]), float(xj[b])), a.n_ex)
            if fi % 200 == 0: print(f"  {m}: position {fi} of {len(fs[m])} ({time.time() - t0:.0f}s)", flush=True)
    cache = {}
    def load(m, fi):
        if (m, fi) not in cache:
            if len(cache) > 64: cache.clear()
            cache[(m, fi)] = raw(fs[m][fi])
        return cache[(m, fi)]
    def ply(m, fi, row, extra=2):
        import chess
        D, _ = load(m, fi); q, t = divmod(row, PL + 1); root = roots[fi]; sans = D[q]["sans"]
        b = chess.Board(root["fen"])
        for mv in sans[:t - 1]: b.push_san(mv)
        return dict(model=m, band=root["band"], line=nums(root["fen"], sans[:t + extra]), t=t, games=D[q]["n"],
                    fen=b.fen(), uci=b.parse_san(sans[t - 1]).uci())
    def contrast(m, fi, row, col):
        D, Z = load(m, fi); q, t = divmod(row, PL + 1); sans = D[q]["sans"]; best = None
        for q2, d in enumerate(D):
            if q2 == q or len(d["sans"]) < t: continue
            if Z[q2 * (PL + 1) + t, col] != 0: continue
            pre = next((i for i, (x, y) in enumerate(zip(d["sans"][:t], sans[:t])) if x != y), t)
            if best is None or pre > best[0]: best = (pre, q2)
        if best is None: return None
        out = ply(m, fi, best[1] * (PL + 1) + t); out["diverge"] = best[0]; out["value"] = 0.0; return out
    ex = {}
    for q, k in enumerate(use):
        seen, rows = set(), []
        for v, m, fi, row in top[q]:
            if fi in seen: continue
            seen.add(fi); e = ply(m, fi, row); e["value"] = round(v, 2)
            e["off"] = contrast(m, fi, row, int(cols[q])); rows.append(e)
            if len(rows) == a.n_ex: break
        ex[str(k)] = rows
    for p in pairs:
        p["e"]["examples"] = {key: [dict(ply(m, fi, row), value=round(v, 2), vi=round(xi, 2), vj=round(xj, 2)) for v, m, fi, row, xi, xj in p[key]]
                              for key in ("both", "only_i", "only_j")}
    # the concept's latents at its branch points, chosen line against subpar, its own model's codes
    R0 = {m: {keyof(r): r for r in json.loads((DIV / f"{a.prefix}-disc-s0" / "mine" / f"lp-{m}-s0.json").read_text())} for m in "SW"}
    rep = json.loads((paths.ROOT / "results" / "transcend" / "divergence" / f"{a.prefix}-disc-s0" / "mine" / "concepts.json").read_text())
    src = {f["id"]: f for m_ in "SW" for f in rep[m_]["concepts"]}
    for c in g["concepts"]:
        if not c["lat"]: continue
        m = c["model"]; recs, ps = [], set()
        for key in sorted(src[c["id"]]["members"], key=lambda k_: -R0[m][k_]["node"]):
            r_ = R0[m][key]
            if r_["pos"] in ps: continue
            ps.add(r_["pos"]); recs.append(r_)
            if len(recs) == 2: break
        bpv = []
        for r_ in recs:
            D, Z = raw(DIV / f"{a.prefix}-disc-s0" / m / f"pos-{r_['pos']}.npz"); t, k = r_["t"], r_["k"]
            val = lambda q: (Z[q * (PL + 1) + t:q * (PL + 1) + t + k + 1][:, c["latent"]].toarray() / np.maximum(mu[m][c["latent"]], 1e-6)).mean(0)
            vc, vs = val(r_["c"]), val(r_["s"])
            bpv.append(dict(chosen=r_["chosen"], subpar=r_["subpar"], t=t, k=k, wc=round(r_["wc"], 3),
                            vals={str(j): [round(float(x), 2), round(float(y), 2)] for j, x, y in zip(c["latent"], vc, vs)}))
        c["bpv"] = bpv
    g["examples"] = ex
    (OV / a.name / "graph.json").write_text(json.dumps(g))
    print(f"examples: {len(ex)} latents, {sum(len(v) for v in ex.values())} activating examples "
          f"({sum(1 for v in ex.values() for e in v if e['off'])} with a minimal pair), {len(pairs)} dPMI pairs ({time.time() - t0:.0f}s)", flush=True)


def lichess_pgn(root, sans, ply):
    """A Lichess analysis link that loads the game up to the root, then the line, opened at ply `ply` (plies from the
    game's start): the viewer steps forward through the moves from there."""
    import re, chess
    from urllib.parse import quote
    pre = [t for t in (re.sub(r"^\d+\.(\.\.)?", "", x) for x in root["prompt"].lstrip(";").split()) if t]
    b = chess.Board(); out = []
    for i, m in enumerate(pre + list(sans)):
        if b.turn == chess.WHITE: out.append(f"{b.fullmove_number}.{m}")
        elif i == 0: out.append(f"{b.fullmove_number}...{m}")
        else: out.append(m)
        b.push_san(m)
    return f"https://lichess.org/analysis/pgn/{quote(' '.join(out))}#{len(pre) + ply}"


def lichess_branch(root, sa, sb, d):
    """One Lichess analysis link with the whole game: the game up to the root, the rollout's shared moves sa[:d], then the
    'on' line sa[d:] as the main line and the 'off' line sb[d:] as a variation from the same move, opened at the branch
    point (the position both lines start from), so the two continuations sit side by side on one board."""
    import re, chess
    from urllib.parse import quote
    pre = [t for t in (re.sub(r"^\d+\.(\.\.)?", "", x) for x in root["prompt"].lstrip(";").split()) if t]
    def toks(b, moves):
        b = b.copy(); out = []
        for i, m in enumerate(moves):
            out.append(f"{b.fullmove_number}.{m}" if b.turn == chess.WHITE else (f"{b.fullmove_number}...{m}" if i == 0 else m))
            b.push_san(m)
        return out
    b = chess.Board(); head = toks(b, pre + list(sa[:d]))
    for m in pre + list(sa[:d]): b.push_san(m)
    main, alt = toks(b, sa[d:]), toks(b, sb[d:])
    b1 = b.copy(); b1.push_san(sa[d]); rest = toks(b1, sa[d + 1:])
    text = " ".join(head + [main[0], "(" + " ".join(alt) + ")"] + rest)
    return f"https://lichess.org/analysis/pgn/{quote(text)}#{len(pre) + d}"


def lichess_at_branch(fen, sa, sb):
    """A Lichess analysis link that starts AT the branching point: a PGN whose starting position is the branch board
    (SetUp/FEN headers), the 'on' line as the main line and the 'off' line as a variation from its first move. It opens
    on the branch board with both continuations hanging from it, whatever Lichess does with ply anchors."""
    import chess
    from urllib.parse import quote
    b = chess.Board(fen)
    def toks(b, moves):
        b = b.copy(); out = []
        for i, m in enumerate(moves):
            out.append(f"{b.fullmove_number}.{m}" if b.turn == chess.WHITE else (f"{b.fullmove_number}...{m}" if i == 0 else m))
            b.push_san(m)
        return out
    alt = toks(b, sb); b1 = b.copy(); b1.push_san(sa[0]); rest = toks(b1, sa[1:])
    text = f'[SetUp "1"]\n[FEN "{fen}"]\n\n' + " ".join([toks(b, sa[:1])[0], "(" + " ".join(alt) + ")"] + rest)
    return f"https://lichess.org/analysis/pgn/{quote(text)}"


def lichess_line_from(fen, moves):
    """A Lichess analysis link whose game starts at fen (the branch board) and plays `moves`, nothing more."""
    import chess
    from urllib.parse import quote
    b = chess.Board(fen); out = []
    for i, m in enumerate(moves):
        out.append(f"{b.fullmove_number}.{m}" if b.turn == chess.WHITE else (f"{b.fullmove_number}...{m}" if i == 0 else m))
        b.push_san(m)
    text = '[SetUp "1"]' + "\n" + '[FEN "' + fen + '"]' + "\n\n" + " ".join(out)
    return "https://lichess.org/analysis/pgn/" + quote(text)


def pairs(a):
    """Every concept's examples as pairs from one starting board: the line where the concept comes on against the line
    where it does not, both from the same branch point, the concept's activity marked ply by ply on each, and a Lichess
    link per line that opens at the split and steps forward.
      mined     its own branch points (the chosen line against the subpar one), up to --n-pairs at different positions.
      held-out  decisive branch points (node >= 30 rollouts, chosen >= 75%, as concept_mine.py) at positions it was not
                mined from, anywhere in its own model's rollouts (discovery and confirmation), where the concept stays
                higher on the chosen line by >= 0.5 at every ply of its window (its most common k); the --n-pairs largest,
                at different positions.
    Activity: v . z, v the concept's keep95 weights with |v|_1 = 1, z in units of each latent's mu (capped at 3); on at a
    ply when >= 0.5. Resumable: rerun until it says done (--budget seconds a call)."""
    import chess
    from types import SimpleNamespace
    from concept_mine import nums
    g = json.loads((OV / a.name / "graph.json").read_text())
    rep = json.loads((paths.ROOT / "results" / "transcend" / "divergence" / f"{a.prefix}-disc-s0" / "mine" / "concepts.json").read_text())
    src = {f["id"]: f for m_ in "SW" for f in rep[m_]["concepts"]}
    roots = sum((json.loads((OV / a.name / s_ / "positions.json").read_text(encoding="utf-8")) for s_ in ("disc", "conf")), [])
    n_disc = len(json.loads((OV / a.name / "disc" / "positions.json").read_text(encoding="utf-8")))
    crit = SimpleNamespace(node=30, wc=0.75, min_share=0.02); t0 = time.time()
    for m in "SW":
        st_f = OV / a.name / f"pairs-state-{m}.json"
        st = json.loads(st_f.read_text()) if st_f.exists() else dict(next=0, top={})
        if st["next"] is None: continue
        C = [c for c in g["concepts"] if c["model"] == m and c["lat"]]
        mu = np.array(json.loads((DIV / f"{a.prefix}-disc-s0" / m / "mu.json").read_text())["mu"])
        V = np.zeros((4096, len(C)), np.float32); K = []; mined_pos = []
        R0 = {keyof(r): r for r in json.loads((DIV / f"{a.prefix}-disc-s0" / "mine" / f"lp-{m}-s0.json").read_text())}
        for i, c in enumerate(C):
            lat, w = keep95(src[c["id"]]["centroid"]); w = np.array(w); V[lat, i] = w / np.abs(w).sum()
            K.append(int(max(src[c["id"]]["ks"], key=lambda x: src[c["id"]]["ks"][x])))
            mined_pos.append({R0[k_]["pos"] for k_ in src[c["id"]]["members"]})
        K = np.array(K); fs = files(a, m)
        for fi in range(st["next"], len(fs)):
            D, Z = raw(fs[fi]); Z.data = np.minimum(Z.data / np.maximum(mu[Z.indices], 1e-6), 3.0)
            A = np.asarray((Z @ V)); lens = [len(d["sans"]) for d in D]
            for p in pairs_of(D, crit):
                for k in sorted(set(K.tolist())):
                    if min(lens[p["c"]], lens[p["s"]]) < p["t"] + k: continue
                    idx = np.flatnonzero(K == k); rc, rs = p["c"] * (PL + 1) + p["t"], p["s"] * (PL + 1) + p["t"]
                    gap = (A[rc:rc + k + 1, idx] - A[rs:rs + k + 1, idx]).min(0)
                    for j in np.flatnonzero(gap >= 0.5):
                        i = int(idx[j])
                        if fi < n_disc and fi in mined_pos[i]: continue
                        lst = st["top"].setdefault(C[i]["id"], [])
                        if any(x[1] == fi for x in lst):
                            q_ = next(n_ for n_, x in enumerate(lst) if x[1] == fi)
                            if lst[q_][0] >= gap[j]: continue
                            del lst[q_]
                        lst.append([round(float(gap[j]), 3), fi, p["t"], p["c"], p["s"], k, p["chosen"], p["subpar"], p["wc"], p["ws"], p["node"]])
                        lst.sort(key=lambda x: -x[0]); del lst[a.n_pairs:]
            if time.time() - t0 > a.budget:
                st["next"] = fi + 1; st_f.write_text(json.dumps(st))
                print(f"pairs {m}: paused after position {fi + 1} of {len(fs)}; rerun to resume", flush=True); return
        st["next"] = None; st_f.write_text(json.dumps(st))
        print(f"pairs {m}: search done, held-out pairs for {len(st['top'])} of {len(C)} concepts ({time.time() - t0:.0f}s)", flush=True)
    # render both models' pairs into graph.json, one position at a time
    tasks = []                                                # (m, fi, concept index, order, args)
    VV = {}
    for m in "SW":
        st = json.loads((OV / a.name / f"pairs-state-{m}.json").read_text())
        R0 = {keyof(r): r for r in json.loads((DIV / f"{a.prefix}-disc-s0" / "mine" / f"lp-{m}-s0.json").read_text())}
        for ci, c in enumerate(g["concepts"]):
            if c["model"] != m or not c["lat"]: continue
            lat, w = keep95(src[c["id"]]["centroid"]); w = np.array(w); v = np.zeros(4096, np.float32); v[lat] = w / np.abs(w).sum(); VV[ci] = v
            ps, o = set(), 0
            for key in sorted(src[c["id"]]["members"], key=lambda k_: -R0[k_]["node"]):
                r_ = R0[key]
                if r_["pos"] in ps: continue
                ps.add(r_["pos"])
                tasks.append((m, r_["pos"], ci, o, ("mined", r_["t"], r_["c"], r_["s"], r_["k"], r_["chosen"], r_["subpar"], r_["wc"], r_["ws"], r_["node"], None))); o += 1
                if len(ps) == a.n_pairs: break
            for x in st["top"].get(c["id"], []):
                tasks.append((m, x[1], ci, o, ("held-out", x[2], x[3], x[4], x[5], x[6], x[7], x[8], x[9], x[10], x[0]))); o += 1
    mus = {m: np.array(json.loads((DIV / f"{a.prefix}-disc-s0" / m / "mu.json").read_text())["mu"]) for m in "SW"}
    fsm = {m: files(a, m) for m in "SW"}
    res = {}
    tasks.sort(key=lambda x: (x[0], x[1])); cur = None
    for m, fi, ci, o, (kind, t, c_, s_, k, chosen, subpar, wc, ws, node, gap) in tasks:
        if cur != (m, fi):
            D, Z = raw(fsm[m][fi]); Z.data = np.minimum(Z.data / np.maximum(mus[m][Z.indices], 1e-6), 3.0); Z = Z.tocsr(); cur = (m, fi)
        root = roots[fi]; sc, ss = D[c_]["sans"], D[s_]["sans"]; v = VV[ci]
        b = chess.Board(root["fen"])
        for mv in sc[:t - 1]: b.push_san(mv)
        act = lambda q, n: [round(float(x), 2) for x in np.asarray(Z[q * (PL + 1):q * (PL + 1) + n + 1] @ v).ravel()[1:]]
        r = dict(kind=kind, pos=fi, split="discovery" if fi < n_disc else "confirmation", band=root["band"], t=t, k=k,
                 chosen=chosen, subpar=subpar, wc=round(wc, 3), ws=round(ws, 3), node=node, fen=b.fen(),
                 uc=b.parse_san(chosen).uci(), us=b.parse_san(subpar).uci(),
                 cline=nums(root["fen"], sc), sline=nums(root["fen"], ss), cact=act(c_, len(sc)), sact=act(s_, len(ss)),
                 lk=lichess_at_branch(b.fen(), sc[t - 1:], ss[t - 1:]), lg=lichess_branch(root, sc, ss, t - 1))
        if gap is not None: r["gap"] = gap
        # how long the concept persists: plies in a row from the split where it stays higher on the concept line by >= 0.5
        ca, sa_ = r["cact"][t - 1:], r["sact"][t - 1:]; n = 0
        while n < min(len(ca), len(sa_)) and ca[n] - sa_[n] >= 0.5: n += 1
        n = max(n, 1); r["persist"] = n
        r["lkc"] = lichess_line_from(r["fen"], sc[t - 1:t - 1 + n]); r["lks"] = lichess_line_from(r["fen"], ss[t - 1:t - 1 + n])
        res.setdefault(ci, []).append((o, r))
    for ci, lst in res.items(): g["concepts"][ci]["pairs"] = [r for _, r in sorted(lst, key=lambda x: x[0])]
    done = len(res)
    (OV / a.name / "graph.json").write_text(json.dumps(g))
    n_h = sum(1 for c in g["concepts"] for p in c.get("pairs", []) if p["kind"] == "held-out")
    print(f"pairs: {done} concepts, {sum(len(c.get('pairs', [])) for c in g['concepts'])} pairs ({n_h} held-out) written into graph.json "
          f"({time.time() - t0:.0f}s); now run page", flush=True)


def latentpairs(a):
    """The latents' examples as pairs from one board too. Each activating ply and its minimal pair (examples()) share a
    game up to the ply where their lines part; that position is the starting board, the two moves played there are its
    arrows, and both lines run on from it, the latent's ply marked (on in the one, off in the other)."""
    import re, chess
    g = json.loads((OV / a.name / "graph.json").read_text())
    roots = sum((json.loads((OV / a.name / s_ / "positions.json").read_text(encoding="utf-8")) for s_ in ("disc", "conf")), [])
    strip = lambda x: re.sub(r"^\d+\.(\.\.)?", "", x)
    by_start = {}
    for i, r in enumerate(roots):
        b = chess.Board(r["fen"]); by_start.setdefault((b.fullmove_number, b.turn), []).append(i)
    def find_root(e):
        first = e["line"][0]; n = int(re.match(r"^(\d+)", first).group(1)); turn = "..." not in first
        sans = [strip(x) for x in e["line"]]
        for i in by_start.get((n, turn), []):
            b = chess.Board(roots[i]["fen"])
            try:
                for mv in sans[:e["t"] - 1]: b.push_san(mv)
            except Exception: continue
            if b.fen() == e["fen"]: return i, sans
        return None, sans
    ok = miss = 0
    for k, exs in g.get("examples", {}).items():
        for e in exs:
            off = e.get("off")
            if not off: continue
            i, sa = find_root(e)
            if i is None: miss += 1; continue
            sb = [strip(x) for x in off["line"]]; d = off["diverge"]
            if d >= len(sa) or d >= len(sb): miss += 1; continue
            root = roots[i]; b = chess.Board(root["fen"])
            for mv in sa[:d]: b.push_san(mv)
            e["pair"] = dict(fen=b.fen(), ua=b.parse_san(sa[d]).uci(), ub=b.parse_san(sb[d]).uci(), start=d + 1,
                             la=e["line"], lb=off["line"], lk=lichess_at_branch(b.fen(), sa[d:], sb[d:]), lg=lichess_branch(root, sa, sb, d))
            ok += 1
    (OV / a.name / "graph.json").write_text(json.dumps(g))
    print(f"latentpairs: {ok} latent examples now start from their shared board ({miss} without one)", flush=True)


def strength_of(f):
    """How strongly a concept is defined: its margins over the nulls in the seed check (concept_mine.py score), summed."""
    parts = [(f.get(x), f.get(x + "_null95")) for x in ("replication", "agreement", "replication_own")]
    return round(sum(v - n for v, n in parts), 3) if all(v is not None and n is not None for v, n in parts) else None


def rank(a):
    """The concepts ranked, for reading: results/transcend/overnight/<name>-rank.md and -rank.json.
    Readable = not board-tier, seen at >= --rank-positions discovery positions, persists >= 2 plies (median over its
    branch points), and has >= 1 held-out pair. Ranked by strength (seed-check margins). Model-only: best match in the
    other model below --absent-cos. Counts of model-only concepts per model by tier and persistence."""
    from collections import Counter
    g = json.loads((OV / a.name / "graph.json").read_text())
    rep = json.loads((paths.ROOT / "results" / "transcend" / "divergence" / f"{a.prefix}-disc-s0" / "mine" / "concepts.json").read_text())
    src = {f["id"]: f for m_ in "SW" for f in rep[m_]["concepts"]}
    rows = []
    for c in g["concepts"]:
        if not c["lat"]: continue
        P = c.get("pairs", []); held = [p for p in P if p["kind"] == "held-out"]
        rows.append(dict(id=c["id"], model=c["model"], tier=c["tier"], theme=c["theme"], strength=strength_of(src.get(c["id"], {})),
                         positions=c["positions"], persistence=c["persistence"], held_out=len(held),
                         held_out_confirmation=sum(p["split"] == "confirmation" for p in held), max_persist=max([p["persist"] for p in P] or [0]),
                         match=c["match"], match_cos=c["match_cos"], only=c["match_cos"] < a.absent_cos, latents=c["latent"]))
    readable = lambda r: r["tier"] != "board" and r["positions"] >= a.rank_positions and (r["persistence"] or 0) >= 2 and r["held_out"] >= 1 and r["strength"] is not None
    R = sorted([r for r in rows if readable(r)], key=lambda r: -r["strength"])
    def table(sel):
        out = ["| concept | model | tier | theme | strength | positions | persists (median / max) | held-out (confirmation) | best match in other model |",
               "|---|---|---|---|---|---|---|---|---|"]
        for r in sel:
            out.append(f"| {r['id']} | {r['model']} | {r['tier']} | {r['theme'] or ''} | {r['strength']} | {r['positions']} | {r['persistence']} / {r['max_persist']} | "
                       f"{r['held_out']} ({r['held_out_confirmation']}) | {r['match']} ({r['match_cos']:.2f}) |")
        return out
    md = [f"# Concepts ranked ({a.name})", "", f"Readable: not board-tier, seen at >= {a.rank_positions} discovery positions, persists >= 2 plies, at least one held-out pair. "
          f"Ranked by strength (summed margins over the seed-check nulls). Model-only: best match in the other model below cosine {a.absent_cos}.", ""]
    md += ["## All readable concepts", ""] + table(R[:a.rank_top]) + [""]
    for m in "SW":
        md += [f"## {m} only", ""] + table([r for r in R if r["model"] == m and r["only"]][:a.rank_top]) + [""]
    md += ["## Model-only concepts, counted", "", "| model | all | not board | not board, persists >= 2 | readable |", "|---|---|---|---|---|"]
    for m in "SW":
        X = [r for r in rows if r["model"] == m and r["only"]]
        md.append(f"| {m} | {len(X)} | {sum(r['tier'] != 'board' for r in X)} | {sum(r['tier'] != 'board' and (r['persistence'] or 0) >= 2 for r in X)} | {sum(readable(r) for r in X)} |")
    tot = {m: sum(r["model"] == m for r in rows) for m in "SW"}
    md += ["", f"Concepts on the map: S {tot['S']}, W {tot['W']}.", ""]
    RES.mkdir(parents=True, exist_ok=True)
    (RES / f"{a.name}-rank.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (RES / f"{a.name}-rank.json").write_text(json.dumps(dict(readable=R, all=rows)))
    print(f"rank: {len(R)} readable concepts of {len(rows)}; wrote {RES / (a.name + '-rank.md')}", flush=True)


def page(a):
    # runs/ is not in git, so the page's data is also kept beside the page in results/ (and read from there without runs/)
    src = OV / a.name / "graph.json"; keep = RES / f"{a.name}-graph.json"
    g = (src if src.exists() else keep).read_text()
    if src.exists(): RES.mkdir(parents=True, exist_ok=True); keep.write_text(g)
    from pages import BOARD_DEFS, BOARD_JS, MOVE_HEAD
    bjs = BOARD_JS.split("function explHTML")[0].replace('const q = cls === "sm" ? 16 : 32', 'const q = cls === "sm" ? 16 : cls === "md" ? 22 : 32')
    assert "function board" in bjs and '"md" ? 22' in bjs
    gd = json.loads(g)                                        # the page shows only what it needs: concept pairs, no latent examples
    gd.pop("examples", None)
    # how strongly each concept is defined: its margins over the nulls in the seed check (concept_mine.py score), summed:
    # replication across every ply, agreement of the seed-1 solutions at its branch points, replication on its own positions
    rep = json.loads((paths.ROOT / "results" / "transcend" / "divergence" / f"{a.prefix}-disc-s0" / "mine" / "concepts.json").read_text())
    src = {f["id"]: f for m_ in "SW" for f in rep[m_]["concepts"]}
    fe = Path(__file__).with_name("featured.json")             # concepts labelled by hand for people to look through
    gd["featured"] = json.loads(fe.read_text(encoding="utf-8"))["concepts"] if fe.exists() else []
    for c in gd["concepts"]:
        f = src.get(c["id"], {})
        parts = [(f.get(x), f.get(x + "_null95")) for x in ("replication", "agreement", "replication_own")]
        c["strength"] = round(sum(v - n for v, n in parts), 3) if all(v is not None and n is not None for v, n in parts) else None
    for c in gd["concepts"]:
        for q in c.get("pairs", []): q.pop("lk", None); q.pop("lg", None)
    g = json.dumps(gd)
    html = (Path(__file__).with_name("concept_graph.html")).read_text(encoding="utf-8").replace("/*DATA*/", g.replace("</", "<\\/"))
    html = html.replace("<!--BOARDS-->", BOARD_DEFS + MOVE_HEAD).replace("/*BOARD_JS*/", bjs)
    # the 3D library inside the page (vendor/), so it runs where outside scripts are blocked and offline
    tag = '<script src="https://unpkg.com/3d-force-graph@1.73.4/dist/3d-force-graph.min.js"></script>'
    lib = Path(__file__).with_name("vendor") / "3d-force-graph-1.73.4.min.js"
    if lib.exists() and tag in html:
        html = html.replace(tag, "<script>" + lib.read_text(encoding="utf-8").replace("</script", "<\\/script") + "</script>")
    RES.mkdir(parents=True, exist_ok=True); f = RES / f"{a.name}-graph.html"; f.write_text(html, encoding="utf-8")
    print(f"wrote {f} ({len(html) / 1e6:.1f} MB)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["build", "layout", "examples", "pairs", "latentpairs", "rank", "page"])
    ap.add_argument("--name", default="night1")
    ap.add_argument("--prefix", default="ov1")
    ap.add_argument("--match-cos", type=float, default=0.9)
    ap.add_argument("--min-rate", type=float, default=1e-4)
    ap.add_argument("--min-pair", type=float, default=200, help="pooled co-occurring plies (rollout-weighted) for a dPPMI pair")
    ap.add_argument("--perms", type=int, default=40)
    ap.add_argument("--absent-cos", type=float, default=0.5, help="G_diff: best match in the other model below this")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-ex", type=int, default=3, help="examples: per latent and per pair kind")
    ap.add_argument("--n-pairs", type=int, default=3, help="pairs: mined and held-out pairs per concept")
    ap.add_argument("--budget", type=float, default=150, help="pairs: seconds a call before pausing (rerun resumes)")
    ap.add_argument("--rank-positions", type=int, default=8, help="rank: discovery positions a readable concept is seen at")
    ap.add_argument("--rank-top", type=int, default=40, help="rank: rows per table")
    ap.add_argument("--knn", type=int, default=6, help="layout: play partners per latent")
    ap.add_argument("--concept-len", type=float, default=0.25, help="layout: concept-to-latent edge length, against 1 for play partners")
    ap.add_argument("--iters", type=int, default=80, help="layout: SMACOF iterations")
    ap.add_argument("--sep", type=float, default=0.6, help="layout: gap between community balls, x their radii")
    ap.add_argument("--resolution", type=float, default=0.5, help="layout: Louvain resolution")
    a = ap.parse_args()
    if a.command == "build": build(a)
    elif a.command == "layout": layout(a)
    elif a.command == "examples": examples(a)
    elif a.command == "pairs": pairs(a)
    elif a.command == "latentpairs": latentpairs(a)
    elif a.command == "rank": rank(a)
    else:
        page(a)


if __name__ == "__main__":
    main()
