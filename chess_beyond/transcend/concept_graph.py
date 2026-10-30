"""Concept graphs where a node is a dynamic concept: a family of LP solutions v (decisive branch points, continuous
activations, k = 2, 4, 6, all latents allowed) grouped by cosine similarity. Per model. Edges: two concepts whose mean
v's overlap (cosine >= EDGE). Cross-model: each concept's best match in the other model."""
import json, sys
from pathlib import Path
from collections import Counter
import numpy as np
SIM, EDGE, MINM = 0.5, 0.25, 3
scr = json.load(open("screen.json"))
board_auc = {m: np.array([np.nan if v is None else v for v in scr[m]["auc"]]) for m in "SW"}
def vec(r):
    x = np.zeros(4096); x[r["latents"]] = r["weights"]; return x / np.linalg.norm(x)
fams = {}
for M in "SW":
    R = [r for r in json.load(open(f"all-{M}.json")) if r["mode"] == "continuous" and r["k"] >= 2 and r["latents"]]
    V = np.array([vec(r) for r in R])
    order = np.argsort([-len(r["latents"]) for r in R])          # larger supports seed families first
    cents, members = [], []
    for i in order:
        if cents:
            C = np.array(cents); s = C @ V[i]; j = int(s.argmax())
            if s[j] >= SIM:
                members[j].append(i); c = V[members[j]].mean(0); cents[j] = c / np.linalg.norm(c); continue
        cents.append(V[i].copy()); members.append([i])
    F = []
    for c, mem in zip(cents, members):
        pos = {R[i]["pos"] for i in mem}
        if len(mem) < MINM or len(pos) < 2: continue
        top = np.argsort(-c)[:8]; top = [int(j) for j in top if c[j] > 0.05]
        w = c[top] / c[top].sum()
        auc = np.nanmean([board_auc[M][j] if not np.isnan(board_auc[M][j]) else 1.0 for j in top])
        ex = sorted((R[i] for i in mem), key=lambda r: -r["node"])
        seen, exs = set(), []
        for r in ex:
            if r["pos"] in seen: continue
            seen.add(r["pos"]); exs.append(dict(pos=r["pos"], t=r["t"], k=r["k"], c=r["c"], s=r["s"], chosen=r["chosen"], subpar=r["subpar"], wc=r["wc"], ws=r["ws"], node=r["node"]))
            if len(exs) == 4: break
        F.append(dict(model=M, n=len(mem), positions=len(pos), ks=dict(Counter(R[i]["k"] for i in mem)), latents=top,
                      weights=[round(float(x), 3) for x in w], board=round(float(auc), 3), cent=c, examples=exs))
    fams[M] = (F, len(R))
    print(M, "v's", len(R), "families", len(cents), "kept (>=3 members, >=2 positions)", len(F))
out = {}
for M, O in (("S", "W"), ("W", "S")):
    F, n = fams[M]; Fo, _ = fams[O]
    Co = np.array([f["cent"] for f in Fo]) if Fo else np.zeros((0, 4096))
    for f in F:
        s = Co @ f["cent"] if len(Co) else np.zeros(0)
        j = int(s.argmax()) if len(s) else -1
        f["match"] = dict(idx=j, cos=round(float(s[j]), 3)) if j >= 0 else None
    C = np.array([f["cent"] for f in F]); S_ = C @ C.T
    edges = [dict(a=i, b=j, cos=round(float(S_[i, j]), 3)) for i in range(len(F)) for j in range(i + 1, len(F)) if S_[i, j] >= EDGE]
    out[M] = dict(vs=n, families=[{k: v for k, v in f.items() if k != "cent"} for f in F], edges=edges)
    shared = sum(1 for f in F if f["match"] and f["match"]["cos"] >= SIM)
    print(M, "edges", len(edges), "concepts with a match in the other model (cos >= 0.5):", shared, "of", len(F),
          "| board-explained (mean AUC >= 0.85):", sum(f["board"] >= 0.85 for f in F))
Path(sys.argv[1]).write_text(json.dumps(out))
