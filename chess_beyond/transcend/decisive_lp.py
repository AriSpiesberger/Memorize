"""Decisive branch points (chosen share >= WC at a node with >= NODE rollouts), LP on binary and on continuous latents;
concepts grouped by exact latent support, each checked against the best single piece-on-square fact."""
import json, sys, time
from pathlib import Path
import numpy as np, chess
from scipy import sparse
from scipy.optimize import linprog
ROOT = Path(sys.argv[1]); OUT = Path(sys.argv[2]); WC, NODE = 0.75, 30
run = ROOT / "runs/transcend/divergence/p16-r1024-T0.4-s0-L11-4k/S"
roots = json.loads((ROOT / "runs/transcend/manypositions/p16-r1024-T0.4-s0/positions.json").read_text())
mu = np.array(json.loads((run / "mu.json").read_text())["mu"]); PL = 16; KS = (0, 2, 4, 6); C = 2.0

def load(k):
    z = np.load(run / f"pos-{k}.npz"); D = json.loads(str(z["D"]))
    P = sparse.csr_matrix((z["data"].astype(np.float32), z["indices"], z["indptr"]), shape=tuple(z["shape"]))
    B = P.copy(); B.data = (B.data > 0.5 * mu[B.indices]).astype(np.float32); B.eliminate_zeros()
    Z = P.copy(); Z.data = Z.data / np.maximum(mu[Z.indices], 1e-6); Z.data = np.minimum(Z.data, 3.0)   # in units of mean firing, capped
    return D, B.tocsr(), Z.tocsr()

def pairs_of(D):
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
            if tot < NODE or wt[best] / tot < WC: continue
            for m, qs in ch.items():
                if m != best and wt[m] / tot >= 0.02:
                    out.append(dict(t=t, c=ch[best][0], s=qs[0], chosen=best, subpar=m, wc=wt[best] / tot, ws=wt[m] / tot, node=tot))
    return out

def solve(dc, ds):
    act = np.flatnonzero((dc != 0).any(0) | (ds != 0).any(0))
    if not len(act): return [], []
    d = dc[:, act] - ds[:, act]; n = len(act)
    r = linprog(np.r_[np.ones(n), C], A_ub=np.hstack([-d, -np.ones((len(d), 1))]), b_ub=-np.ones(len(d)),
                bounds=[(0, None)] * (n + 1), method="highs-ds")
    if r.status != 0: return [], []
    v = r.x[:n]; nz = v > 1e-6
    return act[nz].tolist(), v[nz].tolist()

t0 = time.time(); recs = []
for pos in range(50):
    D, B, Z = load(pos)
    lens = [len(d["sans"]) for d in D]
    for p in pairs_of(D):
        for k in KS:
            if min(lens[p["c"]], lens[p["s"]]) < p["t"] + k: continue
            for mode, M in (("binary", B), ("continuous", Z)):
                a, b = p["c"] * (PL + 1) + p["t"], p["s"] * (PL + 1) + p["t"]
                lat, w = solve(M[a:a + k + 1].toarray(), M[b:b + k + 1].toarray())
                recs.append(dict(p, pos=pos, k=k, mode=mode, latents=lat, weights=w))
    print(f"pos {pos}: {len(recs)} records ({time.time()-t0:.0f}s)", flush=True)
OUT.write_text(json.dumps(recs))
