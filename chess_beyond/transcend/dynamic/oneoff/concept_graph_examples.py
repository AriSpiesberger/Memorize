import json, sys
from pathlib import Path
import numpy as np, chess
from scipy import sparse
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # dynamic/: concept_mine
from concept_mine import nums
ROOT=Path(sys.argv[1]); PL=16; TAG="p16-r1024-T0.4-s0-L11-4k"
roots=json.loads((ROOT/"runs/transcend/manypositions/p16-r1024-T0.4-s0/positions.json").read_text())
G=json.load(open("vgraph.json"))
for M in "SW":
    run=ROOT/"runs/transcend/divergence"/TAG/M; mu=np.array(json.loads((run/"mu.json").read_text())["mu"]); cache={}
    for f in G[M]["families"]:
        v=np.zeros(4096); v[f["latents"]]=f["weights"]
        for e in f["examples"]:
            p=e["pos"]
            if p not in cache:
                z=np.load(run/f"pos-{p}.npz"); D=json.loads(str(z["D"]))
                Z=sparse.csr_matrix((z["data"].astype(np.float32),z["indices"],z["indptr"]),shape=tuple(z["shape"]))
                Z.data=np.minimum(Z.data/np.maximum(mu[Z.indices],1e-6),3.0); cache[p]=(D,Z.tocsr())
            D,Z=cache[p]; root=roots[p]; sc,ss=D[e["c"]]["sans"],D[e["s"]]["sans"]
            b=chess.Board(root["fen"])
            for m in sc[:e["t"]-1]: b.push_san(m)
            mc,ms=b.parse_san(e["chosen"]),b.parse_san(e["subpar"])
            act=lambda q,n:[round(float(x),2) for x in (Z[q*(PL+1):(q+1)*(PL+1)]@v)[1:n+1]]
            e.update(fen=b.fen(),side="White" if b.turn else "Black",arrows=[[chess.square_name(mc.from_square),chess.square_name(mc.to_square)],[chess.square_name(ms.from_square),chess.square_name(ms.to_square)]],
                     cline=nums(root["fen"],sc),sline=nums(root["fen"],ss),cact=act(e["c"],len(sc)),sact=act(e["s"],len(ss)),game=root["game"],band=root["band"])
Path(sys.argv[2]).write_text(json.dumps(G)); print("ok")
