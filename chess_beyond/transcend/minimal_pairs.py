"""Minimal pairs: same board, two moves S played from it; one switches the latent on, the other leaves it off."""
import json, sys, random
from pathlib import Path
import numpy as np, chess, chess.svg
from scipy import sparse
ROOT=Path(sys.argv[1]); run=ROOT/"runs/transcend/divergence/p16-r1024-T0.4-s0-L11-4k/S"
roots=json.loads((ROOT/"runs/transcend/manypositions/p16-r1024-T0.4-s0/positions.json").read_text())
mu=np.array(json.loads((run/"mu.json").read_text())["mu"]); PL=16
LAT=[570,19,323,47,3477]
found={j:[] for j in LAT}
for pos in range(50):
  z=np.load(run/f"pos-{pos}.npz"); D=json.loads(str(z["D"]))
  M=sparse.csr_matrix((z["data"].astype(np.float32),z["indices"],z["indptr"]),shape=tuple(z["shape"])).tocsc()[:,LAT].toarray()/mu[LAT]
  for t in range(1,PL+1):
    nodes={}
    for q,d in enumerate(D):
      if len(d["sans"])>=t: nodes.setdefault(tuple(d["sans"][:t-1]),{}).setdefault(d["sans"][t-1],[]).append(q)
    for pre,ch in nodes.items():
      if len(ch)<2: continue
      w={m:sum(D[q]["n"] for q in qs) for m,qs in ch.items()}
      if sum(w.values())<20: continue
      for i,j in enumerate(LAT):
        q0=next(iter(ch.values()))[0]
        if M[q0*(PL+1)+t-1,i]>0.5: continue   # must be off before the move
        st={m:M[qs[0]*(PL+1)+t,i] for m,qs in ch.items()}
        onm=[m for m in ch if st[m]>0.5]; offm=[m for m in ch if st[m]<0.2]
        if onm and offm:
          a=max(onm,key=lambda m:w[m]); b=max(offm,key=lambda m:w[m])
          found[j].append(dict(pos=pos,t=t,pre=list(pre),on=a,off=b,won=w[a],woff=w[b],act=float(st[a]),tot=sum(w.values()),q_on=ch[a][0],q_off=ch[b][0]))
out=[]
random.seed(0)
for j in LAT:
  F=sorted(found[j],key=lambda r:-min(r["won"],r["woff"]))
  seen=set(); sel=[]
  for r in F:
    if r["pos"] in seen: continue
    seen.add(r["pos"]); sel.append(r)
    if len(sel)==8: break
  for r in sel:
    root=roots[r["pos"]]; b=chess.Board(root["fen"])
    for m in r["pre"]: b.push_san(m)
    ma,mb=b.parse_san(r["on"]),b.parse_san(r["off"])
    r["side"]="White" if b.turn else "Black"; r["fen"]=b.fen()
    r["svg"]=chess.svg.board(b,size=240,orientation=b.turn,arrows=[chess.svg.Arrow(ma.from_square,ma.to_square,color="#2e8b57dd"),chess.svg.Arrow(mb.from_square,mb.to_square,color="#8a8f80cc")])
  out.append(dict(latent=j,count=len(F),positions=len({r['pos'] for r in F}),pairs=sel))
  print(j,"minimal pairs",len(F),"positions",len({r['pos'] for r in F}),[(r["on"],r["off"]) for r in sel])
Path(sys.argv[2]).write_text(json.dumps(out))
