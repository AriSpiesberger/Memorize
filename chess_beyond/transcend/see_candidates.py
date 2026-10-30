import json, sys
from pathlib import Path
from urllib.parse import quote
import numpy as np, chess, chess.svg
from scipy import sparse

ROOT = Path(sys.argv[1]); TAG = "p16-r1024-T0.4-s0-L11-4k"; PL = 16; ON = 0.5
run = ROOT / "runs/transcend/divergence" / TAG / "S"
roots = json.loads((ROOT / "runs/transcend/manypositions/p16-r1024-T0.4-s0/positions.json").read_text())
mu = np.array(json.loads((run / "mu.json").read_text())["mu"])
C = [(4, [1193, 262], [3680, 121]), (4, [1230, 1109], [710, 185]), (6, [1752, 603], [3287, 634]),
     (6, [1122, 923], [2156, 772]), (6, [3874, 2247], [1359, 691]), (6, [1455, 416], [1787, 558])]

def load(k):
    z = np.load(run / f"pos-{k}.npz"); D = json.loads(str(z["D"]))
    P = sparse.csr_matrix((z["data"].astype(np.float32), z["indices"], z["indptr"]), shape=tuple(z["shape"]))
    P.data = (P.data > ON * mu[P.indices]).astype(np.float32); P.eliminate_zeros()
    return D, P.tocsr()

def movetext(root, sans):
    b = chess.Board(root["fen"]); out = []
    for i, m in enumerate(sans):
        w = b.turn == chess.WHITE; n = b.fullmove_number
        out.append((f"{n}." if w else (f"{n}..." if i == 0 else "")) + m); b.push_san(m)
    return out

def link(root, sans, t):
    pre = root["prompt"].lstrip(";").split()
    full = " ".join(pre) + " " + " ".join(movetext(root, sans)).replace("...", ". ..").replace(". ..", "...")
    npre = sum(1 for x in pre for _ in [0]) if False else None
    b = chess.Board(); plies = 0
    # count prompt plies by replaying the prompt
    for tok in pre:
        mv = tok.split(".")[-1]
        if mv: b.push_san(mv); plies += 1
    pgn = " ".join(x for x in (" ".join(pre) + " " + " ".join(sans_with_nums(b, sans))).split())
    return f"https://lichess.org/analysis/pgn/{quote(pgn)}#{plies + t - 1}"

def sans_with_nums(b, sans):
    b = b.copy(); out = []
    for i, m in enumerate(sans):
        w = b.turn == chess.WHITE; n = b.fullmove_number
        out.append((f"{n}." if w else (f"{n}..." if i == 0 else "")) + m); b.push_san(m)
    return out

def onplies(Q, q, j):
    col = Q[q * (PL + 1):(q + 1) * (PL + 1)][:, j].toarray().ravel()
    return [t for t in range(1, PL + 1) if col[t] > 0]

cache = {}
out = []
for k, lat, match in C:
    v = np.zeros(len(mu)); v[lat] = 0.5
    withs, withouts, npairs = [], [], 0
    for pos in range(50):
        L = json.loads((run / f"lp-{pos}.json").read_text())
        if pos not in cache: cache[pos] = load(pos)
        D, Q = cache[pos]
        for p in L["ks"][str(k)]:
            npairs += 1
            a, b_ = p["c"] * (PL + 1), p["s"] * (PL + 1)
            d = (Q[a + p["t"]:a + p["t"] + k + 1] - Q[b_ + p["t"]:b_ + p["t"] + k + 1]) @ v
            holds = bool(np.all(np.asarray(d).ravel() >= 0.5 - 1e-9))
            rec = dict(pos=pos, t=p["t"], chosen=p["chosen"], subpar=p["subpar"], wc=p["wc"], ws=p["ws"], c=p["c"], s=p["s"],
                       found=sorted(p["latents"]) == sorted(lat) or bool(set(p["latents"]) & set(lat)), holds=holds,
                       margin=[round(float(x), 2) for x in np.asarray(d).ravel()])
            (withs if holds else withouts).append(rec)
    def render(r):
        root = roots[r["pos"]]; D, Q = cache[r["pos"]]
        sc, ss = D[r["c"]]["sans"], D[r["s"]]["sans"]
        b = chess.Board(root["fen"])
        for m in sc[:r["t"] - 1]: b.push_san(m)
        mc, ms = b.parse_san(r["chosen"]), b.parse_san(r["subpar"])
        svg = chess.svg.board(b, size=300, orientation=b.turn, arrows=[chess.svg.Arrow(mc.from_square, mc.to_square, color="#2e8b57cc"),
                              chess.svg.Arrow(ms.from_square, ms.to_square, color="#c0392bcc")], lastmove=None)
        pre = chess.Board(); 
        for tok in root["prompt"].lstrip(";").split():
            mv = tok.split(".")[-1]
            if mv: pre.push_san(mv)
        line = lambda sans, q: dict(sans=sans_with_nums(chess.Board(root["fen"]), sans),
                                    on={str(j): onplies(Q, q, j) for j in lat},
                                    link="https://lichess.org/analysis/pgn/" + quote(" ".join(root["prompt"].lstrip(";").split() + sans_with_nums(pre, sans))) + f"#{len(pre.move_stack) + r['t'] - 1}")
        return dict(r, fen=root["fen"], game=root["game"], band=root["band"], board_fen=b.fen(), side="White" if b.turn else "Black",
                    svg=svg, chosen_line=line(sc, r["c"]), subpar_line=line(ss, r["s"]))
    seen, show = set(), []
    for r in sorted(withs, key=lambda r: (not r["found"], -r["ws"])):
        if r["pos"] in seen: continue
        seen.add(r["pos"])
        same = [x for x in withouts if x["pos"] == r["pos"]]
        same.sort(key=lambda x: abs(x["t"] - r["t"]))
        show.append(dict(with_=render(r), without=render(same[0]) if same else None))
        if len(show) == 4: break
    out.append(dict(k=k, latents=lat, match=match, pairs=npairs, holds=len(withs), positions=len({r["pos"] for r in withs}),
                    found_by_lp=sum(r["found"] for r in withs), examples=show))
    print(k, lat, "pairs", npairs, "holds", len(withs), "positions", len({r['pos'] for r in withs}), flush=True)
Path(sys.argv[2]).write_text(json.dumps(out))
