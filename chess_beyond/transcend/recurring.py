"""The latent patterns that recur most across many positions, found on one half of them and replicated on the other,
ranked, and described by what they measurably do on the board. S only: S plays every move of every rollout (W's
activations are read too, because the crosscoder encodes the pair). The per-position method is manypositions'.

    python transcend/recurring.py pick    --positions 1000             # GPU: the positions, split A / B by game
    python transcend/recurring.py play    --shard 0 --shards 50        # GPU: rollouts, codes, board facts per position
    python transcend/recurring.py groups  --shard 0 --shards 50        # CPU: per-position groups
    python transcend/recurring.py match                                # CPU: patterns on A, found again on B, nulls
    python transcend/recurring.py search  --shard 0 --shards 50        # CPU: coherence, carry rate, board facts
    python transcend/recurring.py report                               # the table, histograms, boards
(Shards of the same stage can run side by side, e.g. 4 play processes on one GPU: playing is bound by python-chess on
the CPU, so one process leaves the GPU mostly idle.)

1. pick      --positions held-out middlegame positions, each from a different game, by oneposition's rule (>= 2 moves
             S plays >= --reasonable, none above --max-top); split in advance into halves A and B by game (a hash of
             band and game, sorted, the first half A).
2. play      per position --rollouts rollouts of --plies plies at --temperature, S playing both colours; the distinct
             lines (weighted by how often each was sampled), every position's crosscoder activations (values kept), and
             a fixed set of board facts on every ply (FACTS). One file per position, so a partial run is usable.
3. groups    a latent is on at a ply when its activation z > --on x mu_j (mu_j: its mean activation where it fires, over
             every position); a line, per latent, the share of its plies on; groups as oneposition (weighted
             correlations of the latents whose share varies, the family-wise shuffle threshold, average linkage,
             groups of >= 3), every group kept, each with its persistence (the weighted median, over carrying lines,
             of the longest run of plies with half its latents on).
4. match     on half A: groups joined into patterns greedily (largest first) when their Jaccard with a pattern's core
             is >= --jaccard; a core is the latents present in at least half of a pattern's member groups, so patterns
             can't drift by chaining. Recurrence in A = its distinct positions. Then on half B, independently: the B
             positions with a group at Jaccard >= --jaccard with the core. Nulls: A's groups with every latent swapped
             for a random candidate latent of its position in the same overall-firing decile, matched again
             (--null-runs times); and per pattern --null-cores random cores of rate-matched latents, counted in B.
             The --top patterns by recurrence in B are kept.
5. search    per kept pattern, at every position where >= 3 of its core latents are measurable (their share varies,
             weighted sd >= --min-sd): coherence (mean pairwise correlation of those latents over the lines) and carry
             rate (lines with half of them on at one ply); the AUC of each for picking out the positions where it was
             found (A and B), next to --null-cores random cores; and the board facts on its on and off plies.
6. report    the ranked table (recurrence in A and B and their nulls, persistence, coherence median and spread, AUCs,
             the facts that differ most between on and off plies, as standardised differences), the recurrence
             histograms for A and B against the nulls, and for the top --boards patterns the board where it switches
             on at 4 different positions (report.html).

-> runs/transcend/recurring/<tag>/ (positions, per-position files), results/transcend/recurring/<tag>/report.md, .html"""

import argparse
import html
import json
import sys
import time
import zlib
from pathlib import Path

import chess
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paths
import eval as ev
import graphdiff as gd
import manypositions as mp
import oneposition as op

RUNS = paths.RUNS / "transcend" / "recurring"
RESULTS = paths.ROOT / "results" / "transcend" / "recurring"
VALUE = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
FACTS = ["gives check", "capture", "material, mover minus opponent", "material on the board", "both queens on",
         "a queen on", "mover's king shield pawns", "opponent's king shield pawns", "open files by the mover's king",
         "open files by the opponent's king", "mover's passed pawns", "opponent's passed pawns", "pawn push",
         "castling rights left", "attackers near the mover's king", "attackers near the opponent's king", "promotion",
         "castles"]


# ---------------------------------------------------------------- board facts
def shield(b, color):
    k = b.king(color)
    f, r = chess.square_file(k), chess.square_rank(k)
    d = 1 if color == chess.WHITE else -1
    return sum(1 for ff in (f - 1, f, f + 1) for rr in (r + d, r + 2 * d) if 0 <= ff < 8 and 0 <= rr < 8
               and b.piece_at(chess.square(ff, rr)) == chess.Piece(chess.PAWN, color))


def open_files(b, color):
    """Files next to and at the king with no pawn of its own side."""
    f = chess.square_file(b.king(color))
    own = {chess.square_file(s) for s in b.pieces(chess.PAWN, color)}
    return sum(1 for ff in (f - 1, f, f + 1) if 0 <= ff < 8 and ff not in own)


def passed(b, color):
    enemy = b.pieces(chess.PAWN, not color)
    n = 0
    for s in b.pieces(chess.PAWN, color):
        f, r = chess.square_file(s), chess.square_rank(s)
        ahead = range(r + 1, 8) if color == chess.WHITE else range(0, r)
        if not any(chess.square(ff, rr) in enemy for ff in (f - 1, f, f + 1) if 0 <= ff < 8 for rr in ahead):
            n += 1
    return n


def attackers_near(b, color):
    """Distinct enemy pieces attacking the king's square or one next to it."""
    k = b.king(color)
    zone = chess.SquareSet(chess.BB_KING_ATTACKS[k]) | chess.SquareSet.from_square(k)
    att = set()
    for s in zone:
        att |= set(b.attackers(not color, s))
    return len(att)


def facts_after(b, mv, before):
    """FACTS for the position after mv (b has been pushed); before is the board before it. Mover = who played mv."""
    me = not b.turn
    mat = {c: sum(VALUE[p.piece_type] for p in b.piece_map().values() if p.color == c) for c in (chess.WHITE, chess.BLACK)}
    q = {c: bool(b.pieces(chess.QUEEN, c)) for c in (chess.WHITE, chess.BLACK)}
    return [b.is_check(), before.is_capture(mv), mat[me] - mat[not me], mat[me] + mat[not me], q[True] and q[False],
            q[True] or q[False], shield(b, me), shield(b, not me), open_files(b, me), open_files(b, not me), passed(b, me),
            passed(b, not me), before.piece_type_at(mv.from_square) == chess.PAWN and not before.is_capture(mv),
            sum(bool(b.castling_rights & m) for m in (chess.BB_H1, chess.BB_A1, chess.BB_H8, chess.BB_A8)),
            attackers_near(b, me), attackers_near(b, not me), mv.promotion is not None, before.is_castling(mv)]


def line_facts(fen, moves, plies):
    """(plies + 1, FACTS) for one line: row t after its t-th move (row 0 and rows past its end: NaN)."""
    F = np.full((plies + 1, len(FACTS)), np.nan, np.float32)
    b = chess.Board(fen)
    for t, u in enumerate(moves, 1):
        mv = chess.Move.from_uci(u)
        before = b.copy(stack=False)
        b.push(mv)
        F[t] = facts_after(b, mv, before)
    return F


# ---------------------------------------------------------------- stages
def dirs(a):
    run, res = RUNS / a.tag, RESULTS / a.tag
    run.mkdir(parents=True, exist_ok=True)
    res.mkdir(parents=True, exist_ok=True)
    return run, res


def mine(a, K):
    return [k for k in range(K) if k % a.shards == a.shard]


def pick(a):
    run, _ = dirs(a)
    dev = ev.device(a.device)
    cc = gd.load_cc(a.cc_run, a.cc, a.strong, dev)
    Sm = ev.load(cc.info["models"][cc.s], dev)[0]
    t0 = time.time()
    picked = mp.pick_positions(a, Sm, dev)
    order = sorted(range(len(picked)), key=lambda i: zlib.crc32(f"{picked[i][0]['band']}/{picked[i][0]['game']}".encode()))
    half = {i: ("A" if r < len(picked) // 2 else "B") for r, i in enumerate(order)}
    out = [dict(**p[0], half=half[i], legal=[m.uci() for m in p[1]], lp=[float(x) for x in p[2]]) for i, p in enumerate(picked)]
    (run / "positions.json").write_text(json.dumps(out), encoding="utf-8")
    print(f"{len(out)} positions from {len(out)} games ({sum(p['half'] == 'A' for p in out)} A, "
          f"{sum(p['half'] == 'B' for p in out)} B; {time.time() - t0:.0f}s)", flush=True)


def encode_values(a, cc, models, root, D, dev):
    """Every position's activations, values kept -> sparse (lines * (plies + 1), latents) float32 (row 0 of a line: its
    root, left empty)."""
    import torch
    from scipy import sparse
    Ld = dict(roots=[dict(prompt=root["prompt"], fen=root["fen"])], lines=[dict(root=0, moves=d["moves"]) for d in D])
    seqs, ends, _, _, _, line_start = gd.positions(Ld)
    st = {m: gd.line_states(models[m], seqs, ends, cc.layer[m], dev, a.max_tokens) for m in (0, 1)}
    rows, cols, vals = [], [], []
    with torch.no_grad():
        for i in range(0, len(st[0]), 4096):
            f, _ = gd.encode_states(cc, {m: st[m][i:i + 4096].to(dev) for m in (0, 1)})
            nz = (f > 0).nonzero()
            rows.append(nz[:, 0].cpu().numpy() + i)
            cols.append(nz[:, 1].cpu().numpy())
            vals.append(f[nz[:, 0], nz[:, 1]].float().cpu().numpy())
    rows, cols, vals = np.concatenate(rows), np.concatenate(cols), np.concatenate(vals)
    pos_line = np.repeat(np.arange(len(D)), np.diff(line_start))
    pos_t = np.concatenate([np.arange(n) for n in np.diff(line_start)])
    keep = pos_t[rows] >= 1
    r_ = rows[keep]
    return sparse.csr_matrix((vals[keep], (pos_line[r_] * (a.plies + 1) + pos_t[r_], cols[keep])),
                             shape=(len(D) * (a.plies + 1), cc.ck["latents"]))


def play(a):
    run, _ = dirs(a)
    roots = json.loads((run / "positions.json").read_text(encoding="utf-8"))
    todo = [k for k in mine(a, len(roots)) if not (run / f"pos-{k}.npz").exists()]
    if not todo:
        print("nothing to play in this shard")
        return
    dev = ev.device(a.device)
    cc = gd.load_cc(a.cc_run, a.cc, a.strong, dev)
    models = {m: ev.load(cc.info["models"][m], dev)[0] for m in (0, 1)}
    t_all = time.time()
    for i, k in enumerate(todo):
        t0 = time.time()
        root = roots[k]
        legal = [chess.Move.from_uci(u) for u in root["legal"]]
        sans, ucis = op.rollouts(a, root, legal, np.array(root["lp"]), models[cc.s], dev, a.temperature, [a.seed, k])
        D = op.distinct(sans, ucis)
        P = encode_values(a, cc, models, root, D, dev)
        F = np.concatenate([line_facts(root["fen"], d["moves"], a.plies) for d in D])
        cnt = np.bincount(P.indices, minlength=P.shape[1])
        tot = np.bincount(P.indices, weights=P.data.astype(np.float64), minlength=P.shape[1])
        np.savez_compressed(run / f"pos-{k}.npz", D=json.dumps(D), data=P.data.astype(np.float16), indices=P.indices,
                            indptr=P.indptr, shape=np.array(P.shape), facts=F.astype(np.float16), vcnt=cnt, vsum=tot)
        per = (time.time() - t_all) / (i + 1)
        print(f"position {k} ({i + 1}/{len(todo)} of this shard): {len(D)} distinct lines ({time.time() - t0:.0f}s); "
              f"{per:.0f}s a position so far: all {len(roots)} in {per * len(roots) / 3600:.1f} h in one process", flush=True)


def load_pos(run, k):
    from scipy import sparse
    z = np.load(run / f"pos-{k}.npz")
    D = json.loads(str(z["D"]))
    P = sparse.csr_matrix((z["data"].astype(np.float32), z["indices"], z["indptr"]), shape=tuple(z["shape"]))
    w = np.array([d["n"] for d in D], float)
    return D, P, w / w.sum(), z


def mu_of(run, K):
    cnt, tot = 0, 0
    for k in range(K):
        if (run / f"pos-{k}.npz").exists():
            z = np.load(run / f"pos-{k}.npz")
            cnt, tot = cnt + z["vcnt"], tot + z["vsum"]
    return tot / np.maximum(cnt, 1)


def on_matrix(P, mu, frac):
    """Activations above frac x mu_j, as a boolean sparse matrix of the same shape."""
    Q = P.copy()
    Q.data = (Q.data > frac * mu[Q.indices]).astype(np.float32)
    Q.eliminate_zeros()
    return Q


def longest(Q, q, g, plies):
    on = (Q[q * (plies + 1):(q + 1) * (plies + 1)][:, g].toarray() > 0).mean(1) >= 0.5
    best = cur = 0
    for t in range(1, plies + 1):
        cur = cur + 1 if on[t] else 0
        best = max(best, cur)
    return best, on


def groups(a):
    run, _ = dirs(a)
    roots = json.loads((run / "positions.json").read_text(encoding="utf-8"))
    mu_f = run / "mu.npy"
    if mu_f.exists():
        mu = np.load(mu_f)
    else:                                                              # every shard gets the same; a race is harmless
        mu = mu_of(run, len(roots))
        np.save(mu_f, mu)
    rng = np.random.default_rng([a.seed, a.shard])
    for k in mine(a, len(roots)):
        out_f = run / f"groups-{k}.json"
        if out_f.exists() or not (run / f"pos-{k}.npz").exists():
            continue
        D, P, w, _ = load_pos(run, k)
        Q = on_matrix(P, mu, a.on)
        X = mp.x_of(Q, D, a.plies, Q.shape[1])
        kk, thr, cs, _, med = op.concepts(X, w, a, rng, f"position {k}")
        for c in cs:
            g = np.array(c["latents"])
            fire = op.carrying(X, g, med)
            rl = np.array([longest(Q, q, g, a.plies)[0] for q in np.flatnonzero(fire)], float)
            c["persistence"] = mp.wmed(rl, w[fire]) if len(rl) else 0.0
        out_f.write_text(json.dumps(dict(threshold=thr, kk=kk.tolist(), groups=cs, fires=(w @ (X > 0)).tolist()), default=float),
                         encoding="utf-8")


def core_match(G, jac):
    """Greedy, largest groups first: a group (position, set) joins the pattern whose core it matches best at Jaccard >=
    jac, else starts one; a core is the latents in at least half of the pattern's members -> [dict(members, core)]."""
    pats, index = [], {}
    for i in sorted(range(len(G)), key=lambda i: -len(G[i][1])):
        k, s = G[i]
        cand = {p for j in s for p in index.get(j, ())}
        best, bj = None, jac
        for p in cand:
            c = pats[p]["core"]
            j_ = len(s & c) / len(s | c)
            if j_ >= bj:
                best, bj = p, j_
        if best is None:
            pats.append(dict(members=[i], counts={j: 1 for j in s}, core=set(s)))
            p = len(pats) - 1
        else:
            p = best
            P_ = pats[p]
            P_["members"].append(i)
            for j in s:
                P_["counts"][j] = P_["counts"].get(j, 0) + 1
            old = P_["core"]
            P_["core"] = {j for j, n in P_["counts"].items() if n >= len(P_["members"]) / 2}
            for j in old - P_["core"]:
                index[j].discard(p)
        for j in pats[p]["core"]:
            index.setdefault(j, set()).add(p)
    return pats


def found_in(Gb, core, jac, index):
    """The positions of Gb (position, set) with a group at Jaccard >= jac with core (index: latent -> groups)."""
    out = set()
    for i in {i for j in core for i in index.get(j, ())}:
        k, s = Gb[i]
        if len(s & core) / len(s | core) >= jac:
            out.add(k)
    return out


def match(a):
    run, res = dirs(a)
    roots = json.loads((run / "positions.json").read_text(encoding="utf-8"))
    K = len(roots)
    have = [k for k in range(K) if (run / f"groups-{k}.json").exists()]
    Gs = {k: json.loads((run / f"groups-{k}.json").read_text(encoding="utf-8")) for k in have}
    half = {k: roots[k]["half"] for k in have}
    fires = np.mean([Gs[k]["fires"] for k in have], 0)
    meas = np.zeros(len(fires))
    for k in have:
        meas[Gs[k]["kk"]] += 1
    rng = np.random.default_rng(a.seed)
    GA = [(k, set(c["latents"])) for k in have if half[k] == "A" for c in Gs[k]["groups"]]
    GB = [(k, set(c["latents"])) for k in have if half[k] == "B" for c in Gs[k]["groups"]]
    refA = [(k, i) for k in have if half[k] == "A" for i in range(len(Gs[k]["groups"]))]
    idxB = {}
    for i, (_, s) in enumerate(GB):
        for j in s:
            idxB.setdefault(j, set()).add(i)
    t0 = time.time()
    pats = core_match(GA, a.jaccard)
    for p in pats:
        p["A"] = sorted({GA[i][0] for i in p["members"]})
        p["B"] = sorted(found_in(GB, p["core"], a.jaccard, idxB)) if len(p["core"]) >= 3 else []
    print(f"{len(GA)} groups in A, {len(GB)} in B: {len(pats)} patterns on A ({time.time() - t0:.0f}s)", flush=True)
    # nulls: A's recurrence by chance; B's count for random rate-matched cores
    live = np.flatnonzero((fires > 0) & (meas >= 5))
    dec = np.searchsorted(np.quantile(fires[live], np.linspace(0, 1, 11)[1:-1]), fires)
    pool = {b: live[dec[live] == b] for b in np.unique(dec[live])}
    nullA = []
    for _ in range(a.null_runs):
        Gn = []
        for k, s in GA:
            kk = Gs[k]["kk"]
            byd = {}
            for j in kk:
                byd.setdefault(int(dec[j]), []).append(j)
            new = set()
            for j in s:
                opts = [x for x in byd.get(int(dec[j]), []) if x not in new]
                new.add(int(rng.choice(opts)) if opts else j)
            Gn.append((k, new))
        pn = core_match(Gn, a.jaccard)
        nullA.append([len({Gn[i][0] for i in p["members"]}) for p in pn])
    keep = sorted((p for p in pats if len(p["core"]) >= 3), key=lambda p: (-len(p["B"]), -len(p["A"])))[:a.top]
    for p in keep:
        nb = []
        for _ in range(a.null_cores):
            c = {int(rng.choice(pool[dec[j]])) if dec[j] in pool else j for j in p["core"]}
            nb.append(len(found_in(GB, c, a.jaccard, idxB)))
        p["null_B"] = float(np.mean(nb))
        mem = [Gs[refA[i][0]]["groups"][refA[i][1]] for i in p["members"]]
        p["persistence"] = float(np.median([m["persistence"] for m in mem]))
    top_r = max([len(p["A"]) for p in pats] + [max(n) for n in nullA])
    out = dict(patterns=[dict(name=str(i + 1), core=sorted(p["core"]), latents=sorted(p["counts"]), A=p["A"], B=p["B"],
                              null_B=p["null_B"], persistence=p["persistence"]) for i, p in enumerate(keep)],
               histA=np.bincount([len(p["A"]) for p in pats]).tolist(),
               histA_null=np.mean([np.bincount(n, minlength=top_r + 1)[:top_r + 1] for n in nullA], 0).tolist(),
               nullA_max=[int(max(n)) for n in nullA],
               histB=np.bincount([len(p["B"]) for p in pats if len(p["core"]) >= 3]).tolist(),
               groups=dict(A=len(GA), B=len(GB)), positions=dict(A=sum(h == "A" for h in half.values()), B=sum(h == "B" for h in half.values())),
               fires=fires.tolist())
    (run / "patterns.json").write_text(json.dumps(out, default=float), encoding="utf-8")
    print(f"kept {len(keep)} patterns; top recurrence in B {len(keep[0]['B']) if keep else 0}, in A "
          f"{max((len(p['A']) for p in pats), default=0)} (null A max: median {np.median(out['nullA_max']):.0f})", flush=True)


def search(a):
    run, _ = dirs(a)
    roots = json.loads((run / "positions.json").read_text(encoding="utf-8"))
    pj = json.loads((run / "patterns.json").read_text(encoding="utf-8"))
    pats, fires = pj["patterns"], np.array(pj["fires"])
    mu = np.load(run / "mu.npy")
    rng = np.random.default_rng([a.seed, 99])                          # the same random cores in every shard
    live = np.flatnonzero(fires > 0)
    dec = np.searchsorted(np.quantile(fires[live], np.linspace(0, 1, 11)[1:-1]), fires)
    pool = {b: live[dec[live] == b] for b in np.unique(dec[live])}
    cores = [np.array(p["core"]) for p in pats]
    nulls = [[np.array([rng.choice(pool[dec[j]]) if dec[j] in pool else j for j in c]) for _ in range(a.null_cores)]
             for c in cores]
    nF = len(FACTS)
    for k in mine(a, len(roots)):
        out_f = run / f"search-{k}.npz"
        if out_f.exists() or not (run / f"pos-{k}.npz").exists():
            continue
        D, P, w, z = load_pos(run, k)
        Q = on_matrix(P, mu, a.on)
        X = mp.x_of(Q, D, a.plies, Q.shape[1])
        sd = np.sqrt(w @ (X - w @ X) ** 2)
        F = z["facts"].astype(np.float32)
        wr = np.repeat(w, a.plies + 1)
        coh = np.full((len(pats), 1 + a.null_cores), np.nan)
        carry = np.full(len(pats), np.nan)
        acc = np.zeros((len(pats), 2, 3, nF))                          # on / off x (weight, sum, sum of squares) x fact
        ex = {}
        for pi, c in enumerate(cores):
            for ni, g in enumerate([c] + nulls[pi]):
                gm = g[sd[g] >= a.min_sd]
                if len(gm) >= 3:
                    coh[pi, ni] = float(op.wcorr(X[:, gm], w)[np.triu_indices(len(gm), 1)].mean())
            if not np.isfinite(coh[pi, 0]):
                continue
            gm = c[sd[c] >= a.min_sd]
            onp = (np.asarray(Q[:, gm].sum(1)).ravel() >= len(gm) / 2)          # per (line, ply)
            onp[::a.plies + 1] = False
            carry[pi] = float(w @ onp.reshape(len(D), a.plies + 1).any(1))
            ok = np.isfinite(F).all(1)
            for si, sel in ((0, onp & ok), (1, ~onp & ok)):
                ww = wr[sel]
                acc[pi, si, 0] = ww.sum()
                acc[pi, si, 1] = ww @ F[sel]
                acc[pi, si, 2] = ww @ F[sel] ** 2
            if pi < a.boards:                                          # the switch-on board of the longest run here
                best = None
                for q in np.flatnonzero(onp.reshape(len(D), a.plies + 1).any(1)):
                    rl, on = longest(Q, q, gm, a.plies)
                    if best is None or (rl, w[q]) > (best[0], w[best[1]]):
                        best = (rl, q, on)
                if best:
                    rl, q, on = best
                    t = next(t for t in range(1, a.plies + 1) if on[t])
                    ex[pi] = dict(line=q, ply=t, run=int(rl), sans=D[q]["sans"], moves=D[q]["moves"])
        np.savez_compressed(out_f, coh=coh, carry=carry, acc=acc, ex=json.dumps(ex))
        print(f"  searched position {k}", flush=True)


def report(a):
    run, res = dirs(a)
    import chess.svg
    roots = json.loads((run / "positions.json").read_text(encoding="utf-8"))
    pj = json.loads((run / "patterns.json").read_text(encoding="utf-8"))
    pats = pj["patterns"]
    have = [k for k in range(len(roots)) if (run / f"search-{k}.npz").exists()]
    S = {k: np.load(run / f"search-{k}.npz") for k in have}
    found = {i: set(p["A"]) | set(p["B"]) for i, p in enumerate(pats)}
    rows = []
    for i, p in enumerate(pats):
        coh = np.array([S[k]["coh"][i, 0] for k in have])
        car = np.array([S[k]["carry"][i] for k in have])
        lab = np.array([k in found[i] for k in have])
        m = np.isfinite(coh)
        a_coh = mp_auc(coh[m], lab[m])
        a_car = mp_auc(car[m], lab[m])
        nul = []
        for ni in range(1, a.null_cores + 1):
            cn = np.array([S[k]["coh"][i, ni] for k in have])
            mn = np.isfinite(cn)
            if mn.sum() >= 5:
                nul.append(mp_auc(cn[mn], lab[mn]))
        acc = sum(S[k]["acc"][i] for k in have)
        mean = acc[:, 1] / np.maximum(acc[:, 0:1], 1e-12)
        var = acc[:, 2] / np.maximum(acc[:, 0:1], 1e-12) - mean ** 2
        dstd = (mean[0] - mean[1]) / np.sqrt(np.maximum((var[0] + var[1]) / 2, 1e-12))
        top = np.argsort(-np.abs(np.nan_to_num(dstd)))[:4]
        rows.append(dict(p=p, measurable=int(m.sum()), coh_med=float(np.nanmedian(coh)) if m.any() else np.nan,
                         coh_iqr=(float(np.nanquantile(coh, 0.25)), float(np.nanquantile(coh, 0.75))) if m.any() else (np.nan, np.nan),
                         auc_coh=a_coh, auc_carry=a_car, auc_null=float(np.median(nul)) if nul else np.nan,
                         facts=[(FACTS[j], float(dstd[j]), float(mean[0, j]), float(mean[1, j])) for j in top]))
    out = ["# Recurring latent patterns: found on half A, replicated on half B", "",
           f"{pj['positions']['A']} positions in A, {pj['positions']['B']} in B ({pj['groups']['A']} and {pj['groups']['B']} groups); "
           f"{a.rollouts} rollouts of S per position, {a.plies} plies, T = {a.temperature}; on: activation > {a.on} x mu_j. Patterns: "
           f"groups joined at Jaccard >= {a.jaccard} with a core (latents in at least half the members); found in B: a B group at "
           f"Jaccard >= {a.jaccard} with the core. Null A: groups' latents swapped for rate-matched candidates of the same position "
           f"({len(pj['nullA_max'])} runs); null B: random rate-matched cores ({a.null_cores} per pattern).", "",
           "## Recurrence", "", "| positions | patterns (A) | null (A, mean) | patterns found again at this many B positions |", "|---|---|---|---|"]
    hA, hN, hB = pj["histA"], pj["histA_null"], pj["histB"]
    for r in range(1, max(len(hA), len(hB))):
        out.append(f"| {r} | {hA[r] if r < len(hA) else 0} | {hN[r] if r < len(hN) else 0:.1f} | {hB[r] if r < len(hB) else 0} |")
    out += ["", f"Null A's largest recurrence: median {np.median(pj['nullA_max']):.0f}, max {max(pj['nullA_max'])}.", "",
            f"## The top {len(pats)} by recurrence in B", "",
            "| # | core latents | A | B | null B | persistence | coherence median (IQR) | measurable | AUC coherence / carry (null) | facts on vs off (standardised difference: on / off) |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows):
        p = r["p"]
        out.append(f"| {i + 1} | {', '.join(map(str, p['core']))} | {len(p['A'])} | {len(p['B'])} | {p['null_B']:.1f} | {p['persistence']:.1f} | "
                   f"{r['coh_med']:.2f} ({r['coh_iqr'][0]:.2f}-{r['coh_iqr'][1]:.2f}) | {r['measurable']} | {r['auc_coh']:.2f} / "
                   f"{r['auc_carry']:.2f} ({r['auc_null']:.2f}) | "
                   + "; ".join(f"{n} {d:+.2f} ({x:.2g} / {y:.2g})" for n, d, x, y in r["facts"]) + " |")
    (res / "report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    cards = []
    for i in range(min(a.boards, len(pats))):
        exs = [(k, json.loads(str(S[k]["ex"])).get(str(i))) for k in have if k in found[i]]
        exs = [(k, e) for k, e in exs if e][:4]
        bs = []
        for k, e in exs:
            r = roots[k]
            b = chess.Board(r["fen"])
            for u in e["moves"][:e["ply"]]:
                b.push(chess.Move.from_uci(u))
            bs.append(f"<div><div class='cap'>position {k} ({r['half']}), ply {e['ply']} after {html.escape(e['sans'][e['ply'] - 1])}, "
                      f"on {e['run']} plies</div>{chess.svg.board(b, size=230, lastmove=chess.Move.from_uci(e['moves'][e['ply'] - 1]))}"
                      f"<div class='cap'><a target='_blank' href='{gd.lichess_line(r, e['sans'])}'>Lichess</a></div></div>")
        fx = "; ".join(f"{n} {d:+.2f}" for n, d, _, _ in rows[i]["facts"])
        cards.append(f"<div class='card'><h3>#{i + 1}: core {', '.join(map(str, pats[i]['core']))} <span>A {len(pats[i]['A'])}, "
                     f"B {len(pats[i]['B'])} (null {pats[i]['null_B']:.1f}); {fx}</span></h3><div class='row'>{''.join(bs)}</div></div>")
    (res / "report.html").write_text(
        "<!doctype html><html><head><meta charset='utf-8'><title>Recurring patterns</title><style>body{font:14px system-ui;margin:24px;"
        "background:#f7f6f2}.card{background:#fff;border:1px solid #ddd;border-radius:10px;padding:10px 14px;margin:12px 0}"
        "h3{margin:0 0 6px;font-size:15px}h3 span{font-weight:400;color:#667;font-size:13px}.row{display:flex;gap:12px;flex-wrap:wrap}"
        ".cap{font-size:12px;color:#556}</style></head><body><h1>Recurring patterns: the board where each switches on</h1>"
        + "".join(cards) + "</body></html>", encoding="utf-8")
    print(f"wrote {res / 'report.md'} and {res / 'report.html'}")


def mp_auc(score, label):
    pos, neg = score[label], score[~label]
    if not len(pos) or not len(neg):
        return float("nan")
    return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()) / (len(pos) * len(neg)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["pick", "play", "groups", "match", "search", "report"])
    ap.add_argument("--cc-run", default="runs/transcend/crosscoder/everything-3m")
    ap.add_argument("--cc", default="Lfinal")
    ap.add_argument("--strong", default="2400")
    ap.add_argument("--population", default=str(gd.PROBE / "population.jsonl"))
    ap.add_argument("--positions", type=int, default=1000)
    ap.add_argument("--scan", type=int, default=400)
    ap.add_argument("--reasonable", type=float, default=0.2)
    ap.add_argument("--max-top", type=float, default=0.6)
    ap.add_argument("--rollouts", type=int, default=512)
    ap.add_argument("--plies", type=int, default=16)
    ap.add_argument("--temperature", type=float, default=0.4)
    ap.add_argument("--on", type=float, default=0.5, help="a latent is on at a ply when its activation > this x its mean where it fires")
    ap.add_argument("--min-sd", type=float, default=0.05)
    ap.add_argument("--shuffles", type=int, default=100)
    ap.add_argument("--jaccard", type=float, default=0.5)
    ap.add_argument("--null-runs", type=int, default=10)
    ap.add_argument("--null-cores", type=int, default=20)
    ap.add_argument("--top", type=int, default=100)
    ap.add_argument("--boards", type=int, default=20)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--shards", type=int, default=1)
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--max-tokens", type=int, default=300_000)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tag", default="p16-r512-T0.4")
    a = ap.parse_args()
    dict(pick=pick, play=play, groups=groups, match=match, search=search, report=report)[a.command](a)


if __name__ == "__main__":
    main()
