"""Which latents are NOT explained by the board plus the move just played: ridge probe from (board one-hot, move features)
to each latent's on/off, fit on 35 positions, AUC on the other 15. Per model (S, W)."""
import json, sys
from pathlib import Path
import numpy as np, chess
from scipy import sparse
ROOT=Path(sys.argv[1]); TAG="p16-r1024-T0.4-s0-L11-4k"; PL=16
roots=json.loads((ROOT/"runs/transcend/manypositions/p16-r1024-T0.4-s0/positions.json").read_text())
def auc(score, y):
    o=np.argsort(score); r=np.empty(len(o)); r[o]=np.arange(1,len(o)+1); n1=y.sum(); n0=len(y)-n1
    return (r[y].sum()-n1*(n1+1)/2)/(n1*n0) if n1 and n0 else np.nan
res={}
for model in ("S","W"):
    run=ROOT/"runs/transcend/divergence"/TAG/model; mu=np.array(json.loads((run/"mu.json").read_text())["mu"])
    X=[];Y=[];P=[]
    for pos in range(50):
        z=np.load(run/f"pos-{pos}.npz"); D=json.loads(str(z["D"]))
        M=sparse.csr_matrix((z["data"].astype(np.float32),z["indices"],z["indptr"]),shape=tuple(z["shape"]))
        M.data=(M.data>0.5*mu[M.indices]).astype(np.float32); M.eliminate_zeros()
        for q,d in enumerate(D[:25]):
            b=chess.Board(roots[pos]["fen"])
            for t,m in enumerate(d["sans"],1):
                mv=b.parse_san(m); pt=b.piece_type_at(mv.from_square); cap=b.is_capture(mv); cas=b.is_castling(mv); col=b.turn
                f=np.zeros(907,np.float32); f[768+pt-1]=1; f[774]=cap; f[775]=cas; f[776]=mv.promotion is not None; f[777+mv.to_square]=1; f[841+mv.from_square]=1; f[905]=col
                b.push(mv); f[778-1]=b.is_check()   # index 777 overwritten below is fine: to-square block starts at 777
                for sq,pc in b.piece_map().items(): f[(pc.piece_type-1+6*(not pc.color))*64+sq]=1
                f[906]=1; X.append(f); P.append(pos); Y.append(q*(PL+1)+t)
        # rows for this position
        idx=np.array(Y[-sum(1 for p in P if p==pos):]); Y[-len(idx):]=[M[i] for i in idx]
    X=np.array(X); P=np.array(P); Ym=sparse.vstack(Y).tocsc()
    tr=P<35; te=~tr
    G=X[tr].T@X[tr]; INV=[np.linalg.inv(G+l*np.eye(X.shape[1])) for l in (1,30,300,3000)]   # best of 4 ridge strengths: generous to the board
    rate=np.asarray(Ym.mean(0)).ravel(); out=[]
    for j0 in range(0,Ym.shape[1],512):
        Yc=Ym[:,j0:j0+512].toarray()
        XY=X[tr].T@Yc[tr]; preds=[X[te]@(Ai@XY) for Ai in INV]
        for k in range(Yc.shape[1]):
            y=Yc[te,k]>0
            out.append(max(auc(p[:,k],y) for p in preds) if y.sum()>=10 else np.nan)
    res[model]=dict(rate=rate.tolist(),auc=[None if np.isnan(a) else float(a) for a in out])
    a=np.array([np.nan if v is None else v for v in res[model]["auc"]]); ok=~np.isnan(a)&(rate>=0.005)
    print(model,"latents firing >=0.5%:",int(ok.sum()),"| board+move AUC quartiles",np.nanpercentile(a[ok],[10,25,50,75,90]).round(3).tolist(),
          "| AUC<0.85:",int((a[ok]<0.85).sum()),"| AUC<0.75:",int((a[ok]<0.75).sum()), flush=True)
    for j in (19,570,323,47,3477,0,49,116):
        print("   latent",j,"rate %.3f"%rate[j],"AUC",res[model]["auc"][j])
Path(sys.argv[2]).write_text(json.dumps(res))
