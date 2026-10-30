import json, sys
from pathlib import Path
from urllib.parse import quote
import numpy as np, chess, chess.svg
from scipy import sparse
ROOT = Path(sys.argv[1]); run = ROOT / "runs/transcend/divergence/p16-r1024-T0.4-s0-L11-4k/S"
roots = json.loads((ROOT / "runs/transcend/manypositions/p16-r1024-T0.4-s0/positions.json").read_text())
mu = np.array(json.loads((run / "mu.json").read_text())["mu"]); PL = 16
R = json.load(open(sys.argv[2])); EX = {o["latents"][0] if len(o["latents"])==1 else None: o for o in json.load(open(sys.argv[3]))}
LAT = [19, 49, 116, 0, 47, 323, 3477, 570]
def pre_board(root):
    b = chess.Board()
    for tok in root["prompt"].lstrip(";").split():
        mv = tok.split(".")[-1]
        if mv: b.push_san(mv)
    return b
def nums(fen, sans):
    b = chess.Board(fen); out = []
    for i, m in enumerate(sans):
        w = b.turn; n = b.fullmove_number
        out.append((f"{n}." if w else (f"{n}..." if i == 0 else "")) + m); b.push_san(m)
    return out
cache = {}
def load(pos):
    if pos not in cache:
        z = np.load(run / f"pos-{pos}.npz"); D = json.loads(str(z["D"]))
        P = sparse.csr_matrix((z["data"].astype(np.float32), z["indices"], z["indptr"]), shape=tuple(z["shape"])).tocsc()[:, LAT].toarray()
        cache[pos] = (D, P / np.maximum(mu[LAT], 1e-6))
    return cache[pos]
out = []
for li, j in enumerate(LAT):
    # top activations, one per position
    best = []
    for pos in range(50):
        D, A = load(pos)
        a = A[:, li].copy(); a[::PL + 1] = 0
        r = int(a.argmax()); q, t = divmod(r, PL + 1)
        if t == 0 or t > len(D[q]["sans"]): continue
        best.append((float(a[r]), pos, q, t))
    best.sort(reverse=True); tops = []
    for val, pos, q, t in best[:6]:
        D, A = load(pos); root = roots[pos]; b = chess.Board(root["fen"])
        for m in D[q]["sans"][:t - 1]: b.push_san(m)
        mv = b.parse_san(D[q]["sans"][t - 1]); san = D[q]["sans"][t - 1]; mover = "White" if b.turn else "Black"; b.push(mv)
        tops.append(dict(pos=pos, act=round(val, 2), move=san, mover=mover, fen=b.fen(),
                         svg=chess.svg.board(b, size=260, lastmove=mv, orientation=chess.WHITE)))
    # decisive pairs where the LP picked exactly this latent
    picks = [r for r in R if r["mode"] == "binary" and r["latents"] == [j]]
    picks.sort(key=lambda r: (-r["k"], -r["node"]))
    seen, pairs = set(), []
    for r in picks:
        if r["pos"] in seen: continue
        seen.add(r["pos"]); D, A = load(r["pos"]); root = roots[r["pos"]]
        b = chess.Board(root["fen"]); sc, ss = D[r["c"]]["sans"], D[r["s"]]["sans"]
        for m in sc[:r["t"] - 1]: b.push_san(m)
        mc, ms = b.parse_san(r["chosen"]), b.parse_san(r["subpar"])
        svg = chess.svg.board(b, size=260, orientation=b.turn, arrows=[chess.svg.Arrow(mc.from_square, mc.to_square, color="#2e8b57cc"), chess.svg.Arrow(ms.from_square, ms.to_square, color="#c0392bcc")])
        pb = pre_board(root)
        def L(sans, q):
            on = [t for t in range(1, len(sans) + 1) if A[q * (PL + 1) + t, li] > 0.5]
            return dict(sans=nums(root["fen"], sans), on=on, link="https://lichess.org/analysis/pgn/" + quote(" ".join(root["prompt"].lstrip(";").split() + nums(pb.fen(), sans))) + f"#{len(pb.move_stack) + r['t'] - 1}")
        pairs.append(dict(pos=r["pos"], t=r["t"], k=r["k"], chosen=r["chosen"], subpar=r["subpar"], wc=r["wc"], ws=r["ws"], node=r["node"],
                          side="White" if b.turn else "Black", svg=svg, c=L(sc, r["c"]), s=L(ss, r["s"])))
        if len(pairs) == 3: break
    out.append(dict(latent=j, n_picks=len(picks), positions=len({r["pos"] for r in picks}), ks=sorted({r["k"] for r in picks}), tops=tops, pairs=pairs))
    print(j, len(picks), [ (t["move"], t["mover"], t["act"]) for t in tops], flush=True)
Path(sys.argv[4]).write_text(json.dumps(out))
