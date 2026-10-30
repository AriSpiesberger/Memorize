"""A map of the L11 4k crosscoder's latents laid out by how play combines them, with the mined concepts drawn on it.

Nodes   latents of seed 0 that match a seed-1 latent (mutual best decoder cosine, both models' decoders, > --match-cos;
        crossmix.py match's rule) and are on at >= --min-rate of rollout plies. On: z > 0.5 x mu_j, mu_j the mean of the
        two models' mu (one threshold for both, so S and W counts compare).
Layout  over every ply t >= 1 of every rollout line (weighted by how many rollouts played it) at every night1 position
        (discovery and confirmation), S and W pooled: P(i), P(i, j) = share of plies where i is on, where i and j are both
        on; PPMI = max(0, log P(i, j) / P(i) P(j)) (diagonal 0); 3D embedding = the top 3 singular vectors x sqrt(s).
Edges   per model, the mined concepts that replicate across seeds (overnight_confirm.py choose's rule 1); each a star from
        its centre (the weighted mean of its latents' places) to its latents, the concept being its centroid's top latents
        covering 95% of the squared weight (keep95), restricted to the nodes. Colour: persistence (the old reports' rule:
        plies in a row from the split with v . (z_chosen - z_subpar) >= 0.5, |v|_1 = 1, median over its branch points where
        it is on at the split). Size: discovery positions it was found at.
G_diff  concepts whose best match in the other model (report()'s centroid cosine) is below --absent-cos, plus dPMI edges:
        PMI_S - PMI_W (counts + 0.5) per pair with >= --min-pair co-occurring plies pooled, over its sd under random S/W
        swaps by position (the positions are shared, so a swap is a fair null; sd analytic, linearised, over every
        position); kept when |z| beats the 95th percentile of the largest |z| over all pairs in --perms actual swaps
        (maxT, family-wise over every pair).

    python transcend/interp/concept_graph.py build      # CPU, a few minutes: runs/transcend/overnight/<name>/graph.npz, .json
    python transcend/interp/concept_graph.py page       # results/transcend/overnight/<name>-graph.html
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


def page(a):
    g = (OV / a.name / "graph.json").read_text()
    html = (Path(__file__).with_name("concept_graph.html")).read_text(encoding="utf-8").replace("/*DATA*/", g.replace("</", "<\\/"))
    RES.mkdir(parents=True, exist_ok=True); f = RES / f"{a.name}-graph.html"; f.write_text(html, encoding="utf-8")
    print(f"wrote {f} ({len(html) / 1e6:.1f} MB)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["build", "page"])
    ap.add_argument("--name", default="night1")
    ap.add_argument("--prefix", default="ov1")
    ap.add_argument("--match-cos", type=float, default=0.9)
    ap.add_argument("--min-rate", type=float, default=1e-4)
    ap.add_argument("--min-pair", type=float, default=200, help="pooled co-occurring plies (rollout-weighted) for a dPPMI pair")
    ap.add_argument("--perms", type=int, default=40)
    ap.add_argument("--absent-cos", type=float, default=0.5, help="G_diff: best match in the other model below this")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    if a.command == "build": build(a)
    else:
        page(a)


if __name__ == "__main__":
    main()
