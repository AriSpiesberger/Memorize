"""Seed check for chosen concepts. The rollouts are identical in both seeds, only the crosscoder differs.
(1) Same branch points: the seed-1 LP's v's at the concept's own branch points. Do they agree with each other (mean
pairwise cosine), against random sets of seed-1 v's of the same size and k?
(2) Same activity: the seed-0 concept's v . z over every ply of every rollout, against the seed-1 concept (mean of those
seed-1 v's) on the same plies. Correlation, against seed-1 concepts built from random branch points.
(3) What the seed-1 concept does: its top activating windows."""
import json, sys
from pathlib import Path
import numpy as np, chess
from scipy import sparse
ROOT=Path(sys.argv[1]); PL=16; BASE=ROOT/"runs/transcend/divergence"
G=json.load(open("vgraph_act.json"))
WANT=[("S",259),("S",12),("W",216),("W",70)]
rng=np.random.default_rng(0)
def vec(r):
    x=np.zeros(4096); x[r["latents"]]=r["weights"]; n=np.linalg.norm(x); return x/n if n else x
def key(r): return (r["pos"],r["t"],r["c"],r["s"],r["k"])
def load(tag,M):
    run=BASE/tag/M; mu=np.array(json.loads((run/"mu.json").read_text())["mu"]); Z=[]
    for p in range(50):
        z=np.load(run/f"pos-{p}.npz")
        A=sparse.csr_matrix((z["data"].astype(np.float32),z["indices"],z["indptr"]),shape=tuple(z["shape"]))
        A.data=np.minimum(A.data/np.maximum(mu[A.indices],1e-6),3.0); Z.append(A.tocsr())
    return Z
roots=json.loads((ROOT/"runs/transcend/manypositions/p16-r1024-T0.4-s0/positions.json").read_text())
def nums(fen,sans):
    b=chess.Board(fen); o=[]
    for i,m in enumerate(sans):
        w=b.turn; n=b.fullmove_number; o.append((f"{n}." if w else (f"{n}..." if i==0 else ""))+m); b.push_san(m)
    return o
out=[]
for M in "SW":
    R0=[r for r in json.load(open(f"all-{M}.json")) if r["mode"]=="continuous" and r["k"]>=2 and r["latents"]]
    R1={key(r):r for r in json.load(open(f"s1-{M}.json")) if r["mode"]=="continuous" and r["k"]>=2}
    V0=np.array([vec(r) for r in R0])
    Z0=load("p16-r1024-T0.4-s0-L11-4k",M); Z1=load("p16-r1024-T0.4-s0-L11-4k-s1",M)
    lines=[json.loads(str(np.load(BASE/"p16-r1024-T0.4-s0-L11-4k"/M/f"pos-{p}.npz")["D"])) for p in range(50)]
    pool=[r for r in R1.values() if r["latents"]]
    def trace(Z,v): return np.concatenate([np.asarray(Z[p]@v).ravel() for p in range(50)])
    for (MM,ci) in WANT:
        if MM!=M: continue
        f=G[M]["families"][ci]; c=np.zeros(4096); c[f["latents"]]=f["weights"]; c/=np.linalg.norm(c)
        mem=[r for r,v in zip(R0,V0) if v@c>=0.5]                       # the concept's branch points (cosine >= 0.5 to its mean v)
        s1=[R1.get(key(r)) for r in mem]; s1=[r for r in s1 if r and r["latents"]]
        W1=np.array([vec(r) for r in s1]) if s1 else np.zeros((0,4096))
        def coh(W):
            if len(W)<2: return float("nan")
            S=W@W.T; n=len(W); return float((S.sum()-n)/(n*(n-1)))
        co=coh(W1)
        nulls=[]
        for _ in range(300):
            idx=rng.choice(len(pool),size=len(W1),replace=False); nulls.append(coh(np.array([vec(pool[i]) for i in idx])))
        c1=W1.mean(0) if len(W1) else np.zeros(4096)
        t0=trace(Z0,c); t1=trace(Z1,c1) if len(W1) else np.zeros_like(t0)
        r=float(np.corrcoef(t0,t1)[0,1]) if t1.std()>0 else float("nan")
        rn=[]
        for _ in range(100):
            idx=rng.choice(len(pool),size=max(len(W1),1),replace=False); cn=np.array([vec(pool[i]) for i in idx]).mean(0)
            tn=trace(Z1,cn); rn.append(np.corrcoef(t0,tn)[0,1] if tn.std()>0 else 0)
        # top windows of the seed-1 concept (k = the concept's main k)
        k=int(max(f["ks"],key=lambda x:f["ks"][x])); best=[]
        for p in range(50):
            D=lines[p]; A=np.asarray(Z1[p]@c1).reshape(len(D),PL+1); lens=np.array([len(d["sans"]) for d in D])
            Wm=np.stack([A[:,t:t+k+1].min(1) for t in range(1,PL-k+1)],1); valid=np.stack([lens>=t+k for t in range(1,PL-k+1)],1); Wm[~valid]=-1
            q,t=np.unravel_index(int(Wm.argmax()),Wm.shape); best.append((float(Wm[q,t]),p,int(q),int(t)+1))
        best.sort(reverse=True); acts=[]
        for sc,p,q,t in best[:4]:
            line=nums(roots[p]["fen"],lines[p][q]["sans"]); acts.append(dict(pos=p,score=round(sc,2),window=" ".join(line[t-1:t+k])))
        top1=np.argsort(-c1)[:6]
        res=dict(concept=f"{M}{ci}",branch_points=len(mem),in_seed1=len(W1),seed1_agreement=round(co,3),agreement_null95=round(float(np.nanpercentile(nulls,95)),3),
                 trace_corr=round(r,3),trace_null95=round(float(np.percentile(rn,95)),3),seed1_latents=[(int(j),round(float(c1[j]/c1[top1].sum()),2)) for j in top1],
                 seed1_top_windows=acts)
        out.append(res); print(json.dumps(res),flush=True)
Path(sys.argv[2]).write_text(json.dumps(out))
