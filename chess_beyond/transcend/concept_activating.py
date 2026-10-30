"""Top activating examples per concept: over every line of the model's rollouts at all 50 positions, the windows of k+1
consecutive plies where the concept's v . z stays highest (scored by its minimum over the window), best per position."""
import json, sys
from pathlib import Path
import numpy as np, chess
from scipy import sparse
ROOT=Path(sys.argv[1]); PL=16; TAG="p16-r1024-T0.4-s0-L11-4k"
roots=json.loads((ROOT/"runs/transcend/manypositions/p16-r1024-T0.4-s0/positions.json").read_text())
G=json.load(open(sys.argv[2]))
def nums(fen,sans):
    b=chess.Board(fen); o=[]
    for i,m in enumerate(sans):
        w=b.turn; n=b.fullmove_number; o.append((f"{n}." if w else (f"{n}..." if i==0 else ""))+m); b.push_san(m)
    return o
for M in "SW":
    run=ROOT/"runs/transcend/divergence"/TAG/M; mu=np.array(json.loads((run/"mu.json").read_text())["mu"])
    F=G[M]["families"]; nF=len(F)
    V=np.zeros((4096,nF),np.float32)
    for i,f in enumerate(F): V[f["latents"],i]=f["weights"]
    K=np.array([max(f["ks"],key=lambda k:f["ks"][k]) for f in F]).astype(int)
    best=[dict() for _ in range(nF)]   # pos -> (score, q, t0)
    for p in range(50):
        z=np.load(run/f"pos-{p}.npz"); D=json.loads(str(z["D"]))
        Z=sparse.csr_matrix((z["data"].astype(np.float32),z["indices"],z["indptr"]),shape=tuple(z["shape"]))
        Z.data=np.minimum(Z.data/np.maximum(mu[Z.indices],1e-6),3.0)
        A=np.asarray((Z@V)).reshape(len(D),PL+1,nF)        # lines, plies, concepts
        lens=np.array([len(d["sans"]) for d in D])
        for k in sorted(set(K)):
            idx=np.flatnonzero(K==k)
            Ak=A[:,:,idx]
            # min over window t..t+k, t>=1, t+k<=len
            W=np.stack([Ak[:,t:t+k+1].min(1) for t in range(1,PL-k+1)],1)    # lines, starts, concepts
            valid=np.stack([(lens>=t+k) for t in range(1,PL-k+1)],1)
            W[~valid]=-1
            flat=W.reshape(-1,len(idx)); arg=flat.argmax(0)
            for c,ci in enumerate(idx):
                sc=float(flat[arg[c],c])
                if sc>0: q,t=divmod(int(arg[c]),PL-k); best[ci][p]=(sc,q,t+1,D)
    for i,f in enumerate(F):
        top=sorted(best[i].items(),key=lambda kv:-kv[1][0])[:4]; acts=[]
        for p,(sc,q,t,D) in top:
            root=roots[p]; sans=D[q]["sans"]; b=chess.Board(root["fen"])
            for m in sans[:t-1]: b.push_san(m)
            k=int(K[i]); mv=b.parse_san(sans[t-1])
            acts.append(dict(pos=p,score=round(sc,2),t=t,k=k,line=nums(root["fen"],sans),fen=b.fen(),arrow=[chess.square_name(mv.from_square),chess.square_name(mv.to_square)],side="White" if b.turn else "Black",games=D[q]["n"]))
        f["activating"]=acts
    print(M,"done",flush=True)
Path(sys.argv[3]).write_text(json.dumps(G,default=int)); print("ok")
