"""Co-pick graphs over non-board latents: S (2400+) and W (1000-1300), continuous LP at decisive branch points, k = 2, 4, 6.
Node: latent; weight per model = share of that model's decisive pairs whose v uses it. Edge: two latents in the same v.
Each node gets a profile: lift of simple move/position features when it is on, and its most common moves."""
import json, sys
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations
import numpy as np, chess
from scipy import sparse
ROOT=Path(sys.argv[1]); PL=16; TAG="p16-r1024-T0.4-s0-L11-4k"
roots=json.loads((ROOT/"runs/transcend/manypositions/p16-r1024-T0.4-s0/positions.json").read_text())
G={}; npairs={}
for M in "SW":
    R=[r for r in json.load(open(f"nb-{M}.json")) if r["mode"]=="continuous" and r["k"]>=2]
    npairs[M]=len(R); node=Counter(); edge=Counter(); npos=defaultdict(set)
    for r in R:
        L=sorted(r["latents"])
        for j in L: node[j]+=1; npos[j].add(r["pos"])
        for a,b in combinations(L,2): edge[(a,b)]+=1
    G[M]=dict(node=node,edge=edge,npos=npos)
# nodes: used in >= 8 pairs by either model
nodes=sorted({j for M in "SW" for j,c in G[M]["node"].items() if c>=8})
VAL={1:1,2:3,3:3,4:5,5:9,6:100}
def threats(b,c):
    n=0
    for s,p in b.piece_map().items():
        if p.color==c or p.piece_type==6: continue
        att=[VAL[b.piece_type_at(a)] for a in b.attackers(c,s)]
        if att and (not b.is_attacked_by(not c,s) or min(att)<VAL[p.piece_type]): n+=1
    return n
FN=["check","capture","pawn move","piece move","king move","castles","creates a threat","retreat","advance into enemy half","queens off","an own piece left hanging","quiet (no capture, check or threat)"]
feats=[]; acts=[]; mv_names=[]
for M in "SW":
    run=ROOT/"runs/transcend/divergence"/TAG/M; mu=np.array(json.loads((run/"mu.json").read_text())["mu"])
    for pos in range(0,50,2):
        z=np.load(run/f"pos-{pos}.npz"); D=json.loads(str(z["D"]))
        A=sparse.csr_matrix((z["data"].astype(np.float32),z["indices"],z["indptr"]),shape=tuple(z["shape"])).tocsc()[:,nodes].toarray()/mu[nodes]
        for q,d in enumerate(D[:15]):
            b=chess.Board(roots[pos]["fen"])
            for t,m in enumerate(d["sans"],1):
                mv=b.parse_san(m); c=b.turn; pt=b.piece_type_at(mv.from_square); cap=b.is_capture(mv); cas=b.is_castling(mv)
                t0=threats(b,c); fr,to=chess.square_rank(mv.from_square),chess.square_rank(mv.to_square); fwd=(to-fr) if c else (fr-to)
                b.push(mv); thr=threats(b,c)>t0; chk=b.is_check()
                hang=any(p.color==c and p.piece_type!=6 and b.is_attacked_by(not c,s) and not b.is_attacked_by(c,s) for s,p in b.piece_map().items())
                feats.append([chk,cap,pt==1,pt in (2,3,4,5),pt==6 and not cas,cas,thr,fwd<0,(to>=4) if c else (to<=3),not b.pieces(5,True) and not b.pieces(5,False),hang,not(cap or chk or thr)])
                acts.append(A[q*(PL+1)+t]>0.5); mv_names.append(m)
F=np.array(feats,float); A=np.array(acts); base=F.mean(0); mv_names=np.array(mv_names)
out=[]
for i,j in enumerate(nodes):
    on=A[:,i]
    if on.sum()<20: prof=[]; tops=[]
    else:
        lift=F[on].mean(0)/np.maximum(base,1e-6)
        prof=[dict(f=FN[k],lift=round(float(lift[k]),2),p=round(float(F[on,k].mean()),2)) for k in np.argsort(-lift)[:3]]
        tops=[m for m,_ in Counter(mv_names[on]).most_common(6)]
    out.append(dict(id=int(j),rate=round(float(on.mean()),4),profile=prof,moves=tops,
                    S=G["S"]["node"].get(j,0),W=G["W"]["node"].get(j,0),posS=len(G["S"]["npos"].get(j,())),posW=len(G["W"]["npos"].get(j,()))))
edges=[]
for (a,b) in {e for M in "SW" for e in G[M]["edge"]}:
    if a in nodes and b in nodes:
        s,w=G["S"]["edge"].get((a,b),0),G["W"]["edge"].get((a,b),0)
        if max(s,w)>=3: edges.append(dict(a=int(a),b=int(b),S=s,W=w))
Path(sys.argv[2]).write_text(json.dumps(dict(pairs=npairs,nodes=out,edges=edges)))
print("pairs",npairs,"nodes",len(out),"edges",len(edges))
print("top S:",sorted(out,key=lambda o:-o["S"])[:8] and [(o["id"],o["S"],o["W"],o["profile"][:1]) for o in sorted(out,key=lambda o:-o["S"])[:8]])
print("top W:",[(o["id"],o["S"],o["W"],o["profile"][:1]) for o in sorted(out,key=lambda o:-o["W"])[:8]])
