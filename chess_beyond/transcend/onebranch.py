"""One position where the model splits between a few moves: what in its L11 state separates the lines that take one
first move from the lines that take another, ply by ply, read through the crosscoder's latents and through the raw
activations, each against the board.

    python transcend/onebranch.py states  --position 2    # GPU: raw L11 states of both models along the cached lines
    python transcend/onebranch.py analyse --position 2    # CPU

data       divergence.py's cached rollouts at --position (one of the 50 positions; --div-tag's codes, 1,024 rollouts of
           16 plies at T = 0.4, the model both colours), for S's rollouts and W's. states: every ply's state after block
           L11 of both models along each distinct line (the crosscoder's hook), and a check that the crosscoder encodes
           them to the cached codes. -> runs/transcend/onebranch/<div-tag>-p<position>/<S|W>-states.npy.
paths      the root moves the model plays in >= --min-path of its rollouts; the most played is 'chosen'; every other path
           is compared with it, and every two non-chosen paths with each other.
split      the distinct lines of each path halved at random (seeded), train and test; lines weighted by how often they
           were sampled.
reps       at each ply tau (1 = after the first move), each row of a line alive at tau:
             board         one-hot board (12 x 64) and side to move: the reference; it separates the paths whenever their
                           boards differ, which is almost always, so it is the bar, not the null.
             latents on    the crosscoder's codes, binarised as divergence.py does (z > 0.5 mu_j).
             latents       the codes' values.
             raw           the playing model's own L11 state (S's for S's rollouts).
             raw - board   raw minus its ridge prediction from the board (fit on the train rows of every path and ply):
                           what the state carries beyond a linear read of the board.
             latents - board  the same for the latents' values.
probe      weighted L2 logistic regression (inputs standardised on the train rows; --l2 chosen per probe on half of
           the train lines from a grid), two ways: refit at every tau, and fixed (fit at tau = --fix-at and --fix-at + 1,
           each applied at every tau of its parity, since the codes differ by side to move: a direction that persists).
           Metric: weighted AUC on the test lines.
same board test rows from the two paths that reach the same board (pieces and side to move) at the same tau: their AUC
           under each representation except the board, each row scored by its tau's refit probe (the board cannot tell them apart; anything above 0.5 is the
           route, carried in the state).
LP         divergence.py's LP on the two paths' most frequent lines, at k in --ks: v, and the share of test line pairs (one
           from each path) where v holds over the window (within-position recurrence).
latents    per comparison, the --top latents by |coefficient| in the refit latents probe at tau = 1 and at tau = --fix-at
           + 4, each with its best board predicate at this position (weighted phi over every row) and its firing rate
           in each path.

-> results/transcend/onebranch/<div-tag>-p<position>/report.md, report.json"""

import argparse
import json
import sys
import zlib
from pathlib import Path

import chess
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paths
import eval as ev
import divergence as dv
import recurring as rc
import shared as gd

RUNS = paths.RUNS / "transcend" / "onebranch"
RESULTS = paths.ROOT / "results" / "transcend" / "onebranch"
PIECES = "PNBRQKpnbrqk"


def dirs(a):
    name = f"{a.div_tag}-p{a.position}"
    run, res = RUNS / name, RESULTS / name
    run.mkdir(parents=True, exist_ok=True)
    res.mkdir(parents=True, exist_ok=True)
    return run, res


def root_of(a):
    return json.loads((Path(a.source) / "positions.json").read_text(encoding="utf-8"))[a.position]


# ---------------------------------------------------------------- states (GPU)
def states(a):
    run, _ = dirs(a)
    dev = ev.device(a.device)
    cc = gd.load_cc(a.cc_run, a.cc, a.strong, dev)
    models = {m: ev.load(cc.info["models"][m], dev)[0] for m in (0, 1)}
    root = root_of(a)
    for M in ("S", "W"):
        f = run / f"{M}-states.npy"
        if f.exists():
            print(f"{f} exists")
            continue
        D, P, _, _ = rc.load_pos(dv.RUNS / a.div_tag / M, a.position)
        Ld = dict(roots=[dict(prompt=root["prompt"], fen=root["fen"])], lines=[dict(root=0, moves=d["moves"]) for d in D])
        seqs, ends, _, _, _, line_start = gd.positions(Ld)
        st = {m: gd.line_states(models[m], seqs, ends, cc.layer[m], dev, a.max_tokens) for m in (0, 1)}
        pos_line = np.repeat(np.arange(len(D)), np.diff(line_start))
        pos_t = np.concatenate([np.arange(n) for n in np.diff(line_start)])
        X = np.zeros((len(D) * (a.plies + 1), 2, st[0].shape[1]), np.float16)
        X[pos_line * (a.plies + 1) + pos_t] = torch.stack([st[cc.s], st[cc.w]], 1).numpy()    # [:, 0] S's, [:, 1] W's
        with torch.no_grad():                                          # the hook check: the cached codes again
            fs = []
            for i in range(0, len(st[0]), 4096):
                fs.append(gd.encode_states(cc, {m: st[m][i:i + 4096].to(dev) for m in (0, 1)})[0].cpu().numpy())
        F = np.concatenate(fs)
        keep = pos_t >= 1
        Pc = P[pos_line[keep] * (a.plies + 1) + pos_t[keep]].toarray()
        agree = ((F[keep] > 0) == (Pc > 0)).all(1).mean()
        print(f"{M}: {len(D)} lines, {keep.sum()} states; rows whose re-encoded codes match the cached ones exactly: {agree:.1%}",
              flush=True)
        if agree < 0.9:
            sys.exit("the states do not reproduce divergence.py's codes: wrong crosscoder, layer or position")
        np.save(f, X)
        print(f"wrote {f}")


# ---------------------------------------------------------------- analysis (CPU)
def board_rows(root, D, plies):
    """One-hot board + side to move per row (lines * (plies + 1), 769) bool, and a key per row (board, side)."""
    B = np.zeros((len(D) * (plies + 1), 769), bool)
    keys = np.empty(len(D) * (plies + 1), object)
    for q, d in enumerate(D):
        b = chess.Board(root["fen"])
        for t, m in enumerate(d["sans"], 1):
            b.push_san(m)
            r = q * (plies + 1) + t
            for sq, pc in b.piece_map().items():
                B[r, PIECES.index(pc.symbol()) * 64 + sq] = True
            B[r, 768] = b.turn == chess.WHITE
            keys[r] = b.board_fen() + (" w" if b.turn else " b")
    return B, keys


def ridge_residual(Y, B, tr, alpha=10.0):
    """Y minus its ridge prediction from B, fit on rows tr."""
    Bt, Yt = B[tr].astype(np.float64), Y[tr].astype(np.float64)
    bm, ym = Bt.mean(0), Yt.mean(0)
    W = np.linalg.solve((Bt - bm).T @ (Bt - bm) + alpha * np.eye(B.shape[1]), (Bt - bm).T @ (Yt - ym))
    return (Y - ym - (B - bm) @ W).astype(np.float32)


def wauc(s, y, w):
    """Weighted AUC of scores s for labels y (bool)."""
    o = np.argsort(s, kind="stable")
    s, y, w = s[o], y[o], w[o]
    pos, neg = w * y, w * ~y
    # ties: average rank via grouping equal scores
    _, start = np.unique(s, return_index=True)
    grp = np.repeat(np.arange(len(start)), np.diff(np.r_[start, len(s)]))
    gneg, gpos = np.bincount(grp, neg), np.bincount(grp, pos)
    below = np.cumsum(gneg) - gneg
    return float(((below + gneg / 2) * gpos).sum() / max(pos.sum() * neg.sum(), 1e-12))


def logreg(X, y, w, l2, iters=200):
    """Weighted L2 logistic regression, full-batch L-BFGS -> (coef, bias)."""
    X, y, w = torch.from_numpy(X).double(), torch.from_numpy(y.astype(np.float64)), torch.from_numpy(w / w.sum())
    W = torch.zeros(X.shape[1], dtype=torch.float64, requires_grad=True)
    b = torch.zeros(1, dtype=torch.float64, requires_grad=True)
    opt = torch.optim.LBFGS([W, b], max_iter=iters, line_search_fn="strong_wolfe")

    def closure():
        opt.zero_grad()
        z = X @ W + b
        loss = (w * torch.nn.functional.binary_cross_entropy_with_logits(z, y, reduction="none")).sum() + l2 * (W @ W)
        loss.backward()
        return loss

    opt.step(closure)
    return W.detach().numpy(), float(b.detach())


class Probe:
    """Standardise on the train rows, choose l2 on half the train lines, refit on all the train lines."""

    def __init__(self, X, y, w, line, grid):
        self.m, sd = X.mean(0), X.std(0)
        self.inv = np.where(sd > 1e-6, 1 / np.maximum(sd, 1e-6), 0)
        Z = (X - self.m) * self.inv
        half = np.array([zlib.crc32(str(q).encode()) % 2 == 0 for q in line])
        if half.all() or (~half).all() or len(set(y[half])) < 2 or len(set(y[~half])) < 2:
            self.l2 = grid[len(grid) // 2]
        else:
            sc = [wauc(Z[~half] @ logreg(Z[half], y[half], w[half], l2)[0], y[~half], w[~half]) for l2 in grid]
            self.l2 = grid[int(np.argmax(sc))]
        self.coef, self.b = logreg(Z, y, w, self.l2)

    def score(self, X):
        return ((X - self.m) * self.inv) @ self.coef + self.b


def wphi(x, F, w):
    w = w / w.sum()
    F = F.astype(np.float64)
    mx, mf = (w * x).sum(), w @ F
    cov = (w * x) @ F - mx * mf
    return cov / np.sqrt(mx * (1 - mx) * mf * (1 - mf) + 1e-12)


def sqname(i):
    if i == 768:
        return "White to move"
    return f"{'White' if i // 64 < 6 else 'Black'} {'PNBRQK'[i // 64 % 6]} on {chess.square_name(i % 64)}"


def analyse_model(a, M, root, rng):
    run, _ = dirs(a)
    D, P, _, _ = rc.load_pos(dv.RUNS / a.div_tag / M, a.position)
    mu = np.array(json.loads((dv.RUNS / a.div_tag / M / "mu.json").read_text(encoding="utf-8"))["mu"])
    Xraw = np.load(run / f"{M}-states.npy")[:, 0 if M == "S" else 1].astype(np.float32)
    Lv = P.toarray().astype(np.float32)
    Lon = (rc.on_matrix(P, mu, a.on).toarray() > 0).astype(np.float32)
    B, keys = board_rows(root, D, a.plies)
    nrow = a.plies + 1
    lens = np.array([len(d["sans"]) for d in D])
    n = np.array([d["n"] for d in D], float)
    first = np.array([d["sans"][0] for d in D])
    tot = n.sum()
    share = {m: n[first == m].sum() / tot for m in set(first)}
    pathm = [m for m, s in sorted(share.items(), key=lambda x: -x[1]) if s >= a.min_path]
    test_line = np.zeros(len(D), bool)
    for m in pathm:                                                    # half of each path's distinct lines are test
        idx = np.flatnonzero(first == m)
        test_line[rng.permutation(idx)[:len(idx) // 2]] = True
    rows_line = np.repeat(np.arange(len(D)), nrow)
    rows_t = np.tile(np.arange(nrow), len(D))
    alive = (rows_t >= 1) & (rows_t <= lens[rows_line])
    in_path = np.isin(first[rows_line], pathm)
    trrow = alive & in_path & ~test_line[rows_line]
    live_lat = np.flatnonzero(Lon[alive].any(0))                       # only latents that fire somewhere here
    Lon, Lv = Lon[:, live_lat], Lv[:, live_lat]
    reps = {"board": B.astype(np.float32), "latents on": Lon, "latents": Lv, "raw": Xraw,
            "raw - board": ridge_residual(Xraw, B.astype(np.float32), trrow),
            "latents - board": ridge_residual(Lv, B.astype(np.float32), trrow)}
    grid = [1e-4, 1e-3, 1e-2, 1e-1, 1.0]
    comps = [(pathm[0], m) for m in pathm[1:]] + [(x, y) for i, x in enumerate(pathm[1:]) for y in pathm[i + 2:]]
    out = dict(model=M, lines=len(D), share={m: share[m] for m in pathm}, comparisons=[])
    for c, s in comps:
        sel = np.isin(first[rows_line], [c, s]) & alive
        R = dict(chosen=c, subpar=s, refit={}, fixed={}, same_board={}, n_test={}, n_same={})
        y_all = first[rows_line] == c
        w_all = n[rows_line]
        fixed, refit = {}, {}                                          # fixed: one probe per parity of tau (side to move)
        for name, X in reps.items():
            R["refit"][name], R["fixed"][name] = [], []
            for t in range(1, a.plies + 1):
                tr = sel & (rows_t == t) & ~test_line[rows_line]
                te = sel & (rows_t == t) & test_line[rows_line]
                ok = len(set(y_all[tr])) == 2 and len(set(y_all[te])) == 2
                if not ok:
                    R["refit"][name].append(float("nan"))
                    continue
                refit[name, t] = Probe(X[tr], y_all[tr], w_all[tr], rows_line[tr], grid)
                if t in (a.fix_at, a.fix_at + 1):
                    fixed[name, t % 2] = refit[name, t]
                R["refit"][name].append(wauc(refit[name, t].score(X[te]), y_all[te], w_all[te]))
                if name == "board":
                    R["n_test"][t] = int(te.sum())
            for t in range(1, a.plies + 1):
                te = sel & (rows_t == t) & test_line[rows_line]
                ok = (name, t % 2) in fixed and len(set(y_all[te])) == 2
                R["fixed"][name].append(wauc(fixed[name, t % 2].score(X[te]), y_all[te], w_all[te]) if ok else float("nan"))
            R["n_test"] = {t: R["n_test"].get(t, 0) for t in range(1, a.plies + 1)}
        # same board: test rows of the two paths sharing a board at the same tau
        # same board: test rows of the two paths sharing a board at the same tau, scored by that tau's refit probe
        same = np.zeros(len(keys), bool)
        for t in range(1, a.plies + 1):
            te = np.flatnonzero(sel & (rows_t == t) & test_line[rows_line])
            both = {keys[i] for i in te if y_all[i]} & {keys[i] for i in te if not y_all[i]}
            same[[i for i in te if keys[i] in both]] = True
        R["n_same"] = int(same.sum())
        R["same_taus"] = sorted({int(t) for t in rows_t[same]})
        if same.sum() and len(set(y_all[same])) == 2:
            for name, X in reps.items():
                if name == "board":
                    continue
                sc = np.full(len(keys), np.nan)
                for t in R["same_taus"]:
                    m = same & (rows_t == t)
                    if (name, t) in refit:
                        sc[m] = refit[name, t].score(X[m])
                ok = same & ~np.isnan(sc)
                if len(set(y_all[ok])) == 2:
                    R["same_board"][name] = wauc(sc[ok], y_all[ok], w_all[ok])
        # the LP on the two most frequent lines, and its recurrence over test line pairs
        qc, qs = (int(np.flatnonzero((first == m) & ~test_line)[0]) for m in (c, s))
        Q = rc.on_matrix(P, mu, a.on).tocsr()
        R["lp"] = []
        tc, ts = np.flatnonzero((first == c) & test_line), np.flatnonzero((first == s) & test_line)
        for k in [int(x) for x in a.ks.split(",")]:
            if min(lens[qc], lens[qs]) < 1 + k:
                continue
            v = dv.solve(dv.window(Q, qc, 1, k, a.plies), dv.window(Q, qs, 1, k, a.plies), a.C)
            rec = float("nan")
            if v["latents"]:
                vv = dv.vec(v["latents"], v["weights"], Q.shape[1])
                pairs = [(i, j) for i, j in zip(rng.choice(tc, 300), rng.choice(ts, 300)) if min(lens[i], lens[j]) >= 1 + k]
                hold = [((Q[i * nrow + 1:i * nrow + 2 + k].astype(np.float32) - Q[j * nrow + 1:j * nrow + 2 + k].astype(np.float32))
                         @ vv).toarray().ravel().min() >= 0.5 - 1e-9 for i, j in pairs]
                rec = float(np.mean(hold)) if hold else float("nan")
            R["lp"].append(dict(k=k, latents=v["latents"], weights=v["weights"], recurrence=rec))
        # the latents behind the refit latents probe, early and late
        R["top"] = {}
        for t in sorted({1, min(a.fix_at + 4, a.plies)}):
            tr = sel & (rows_t == t) & ~test_line[rows_line]
            if len(set(y_all[tr])) < 2:
                continue
            pr = Probe(reps["latents"][tr], y_all[tr], w_all[tr], rows_line[tr], grid)
            o = np.argsort(-np.abs(pr.coef))[:a.top]
            lst = []
            rw = alive & in_path
            for i in o:
                j = int(live_lat[i])
                z = Lon[rw, i] > 0
                ph = wphi(z, B[rw], n[rows_line[rw]])
                bi = int(np.argmax(ph))
                rate = {m: float((Lon[alive & (first[rows_line] == m), i] * n[rows_line[alive & (first[rows_line] == m)]]).sum()
                                 / n[rows_line[alive & (first[rows_line] == m)]].sum()) for m in (c, s)}
                lst.append(dict(latent=j, coef=float(pr.coef[i]), predicate=sqname(bi), phi=float(ph[bi]), rate=rate))
            R["top"][t] = lst
        out["comparisons"].append(R)
        print(f"{M}: {c} vs {s} done", flush=True)
    return out


def analyse(a):
    run, res = dirs(a)
    root = root_of(a)
    rng = np.random.default_rng(a.seed)
    names = ["board", "latents on", "latents", "raw", "raw - board", "latents - board"]
    b = chess.Board(root["fen"])
    rep, out = {}, [f"# One position, a few paths: {a.div_tag}, position {a.position}", "",
                    f"`{root['fen']}` ({root['band']} game {root['game']}), {'White' if b.turn else 'Black'} to move. S's policy: "
                    + ", ".join(f"{s} {q:.0%}" for s, q in root["top"]) + ".", "",
                    f"Paths: root moves in >= {a.min_path:.0%} of the model's rollouts (1,024 at T = 0.4); distinct lines halved "
                    "per path into train and test; AUC on test lines, weighted by sample count, at each ply tau after the first "
                    f"move. Refit: a probe per tau. Fixed: the probes fit at tau = {a.fix_at} and {a.fix_at + 1}, each applied at every tau of "
                    "its parity (the codes differ by side to move). board: one-hot "
                    "board + side to move (the bar: different first moves give different boards). raw - board, latents - board: "
                    "minus a ridge read of the board. Same board: test rows of the two paths at the same tau with the same "
                    "board, scored by the fixed probes (the board cannot separate them).", ""]
    for M in ("S", "W"):
        if not (run / f"{M}-states.npy").exists():
            out += [f"## {M}", "", f"no states: run `onebranch.py states --position {a.position}` first", ""]
            continue
        R = analyse_model(a, M, root, rng)
        rep[M] = R
        out += [f"## {M}'s rollouts", "", f"{R['lines']} distinct lines; paths: "
                + ", ".join(f"{m} {s:.0%}" for m, s in R["share"].items()) + ".", ""]
        for C in R["comparisons"]:
            out += [f"### {M}: {C['chosen']} against {C['subpar']}", "",
                    "| tau | test rows | " + " | ".join(names) + " | " + " | ".join(f"fixed: {x}" for x in names) + " |",
                    "|---|---|" + "---|" * (2 * len(names))]
            for t in range(1, a.plies + 1):
                out.append(f"| {t} | {C['n_test'][t]} | " + " | ".join(f"{C['refit'][x][t - 1]:.2f}" for x in names) + " | "
                           + " | ".join(f"{C['fixed'][x][t - 1]:.2f}" for x in names) + " |")
            out += ["", f"Same board at the same tau: {C['n_same']} test rows (tau {', '.join(map(str, C['same_taus']))}), each "
                    "scored by its tau's refit probe"
                    + (": " + ", ".join(f"{x} {v:.2f}" for x, v in C["same_board"].items()) if C["same_board"] else "") + ".", ""]
            out += ["LP on the two most frequent lines (divergence.py's, window from the first move): "
                    + "; ".join(f"k = {r['k']}: " + (", ".join(f"{j} ({x:.2f})" for j, x in zip(r["latents"], r["weights"])) or "v = 0")
                                + (f", holds on {r['recurrence']:.0%} of test line pairs" if r["latents"] else "") for r in C["lp"]) + ".", ""]
            for t, lst in C["top"].items():
                out += [f"Top latents of the refit latents probe at tau = {t} (+: toward {C['chosen']}):", "",
                        f"| latent | coefficient | best board predicate (phi) | on in {C['chosen']} | on in {C['subpar']} |",
                        "|---|---|---|---|---|"]
                out += [f"| {r['latent']} | {r['coef']:+.2f} | {r['predicate']} ({r['phi']:+.2f}) | {r['rate'][C['chosen']]:.0%} | "
                        f"{r['rate'][C['subpar']]:.0%} |" for r in lst]
                out.append("")
    (res / "report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    (res / "report.json").write_text(json.dumps(dict(settings=vars(a), **rep), default=float), encoding="utf-8")
    print("\n".join(out))
    print(f"wrote {res / 'report.md'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["states", "analyse"])
    ap.add_argument("--position", type=int, default=2)
    ap.add_argument("--div-tag", default="p16-r1024-T0.4-s0-L11-4k")
    ap.add_argument("--source", default=str(dv.SOURCE))
    ap.add_argument("--cc-run", default="runs/transcend/crosscoder/mixed-L11")
    ap.add_argument("--cc", default="L11-4096")
    ap.add_argument("--strong", default="2400")
    ap.add_argument("--plies", type=int, default=16)
    ap.add_argument("--on", type=float, default=0.5)
    ap.add_argument("--min-path", type=float, default=0.1)
    ap.add_argument("--fix-at", type=int, default=2, help="the fixed probe's ply")
    ap.add_argument("--ks", default="0,2,4,6")
    ap.add_argument("--C", type=float, default=2.0)
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--max-tokens", type=int, default=40_000)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    {"states": states, "analyse": analyse}[a.command](a)


if __name__ == "__main__":
    main()
