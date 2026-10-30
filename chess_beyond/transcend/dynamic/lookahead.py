"""Look-ahead at L11: does a concept's expression BEFORE a split predict how likely the model is to play the move the
concept follows, beyond what the board predicts?

Per concept (steer_concepts.py's jobs: its latents lat, weights w) and per rollout set (the concept's own model's
rollouts, and the other model's), from divergence.py's cached codes (concept_mine.load_pos: units of mu, capped at 3):
  nodes     every branching point with >= --node rollouts through it and >= 2 moves played from it
  e_pre     the concept's expression w . z at the node (the state before the move)
  target    the move the concept follows: the child after which the expression is highest; a node counts when the
            children's expressions spread by >= --spread (the move matters for the concept)
  y         logit of the target's share of the node's rollouts, (n + 0.5) / (N + 1)
  board     the one-hot board at the node (12 x 64, side to move)
Fit (5 folds, grouped by position, out-of-fold): ridge board -> y, and board + e_pre (e_pre unpenalised); the ridge
strength picked per model from a grid by the same folds. Gain = R^2(board + e_pre) - R^2(board), with a bootstrap over
positions (the out-of-fold predictions held fixed). Null: the same, end to end (its own targets and nodes), for each of
the job's random directions (random latents of matching firing rate, the same weights): their median and 95th.

    python transcend/dynamic/lookahead.py --only S141,S8,W29,S14,W25,S29,W138,W30,S58,W197
-> results/transcend/divergence/<tag>/mine/lookahead.md, .json"""
import argparse, json, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # chess_beyond/
import paths  # noqa: E402  also puts transcend/'s folders on sys.path
from concept_mine import load_pos, mu_of, RUNS, RESULTS, PL


def board_x(b):
    import chess
    x = np.zeros(12 * 64 + 1, np.float32)
    for sq, p in b.piece_map().items(): x[(p.piece_type - 1 + 6 * (not p.color)) * 64 + sq] = 1
    x[-1] = b.turn == chess.WHITE
    return x


def nodes_of(D, root, min_node):
    """Branching points of one position's lines -> (t, a line through it, {move: (a line through it, rollouts)}), boards."""
    import chess
    out, B = [], []
    for t in range(1, PL + 1):
        nd = {}
        for q, d in enumerate(D):
            if len(d["sans"]) >= t:
                c = nd.setdefault(tuple(d["sans"][:t - 1]), {}).setdefault(d["sans"][t - 1], [q, 0]); c[1] += d["n"]
        for pre, ch in nd.items():
            if len(ch) < 2 or sum(n for _, n in ch.values()) < min_node: continue
            b = chess.Board(root["fen"])
            for s in pre: b.push_san(s)
            out.append((t, next(iter(ch.values()))[0], ch)); B.append(board_x(b))
    return out, B


def ridge_oof(X, y, g, alphas, free):
    """Out-of-fold ridge predictions per strength in alphas (each fold's Gram matrix computed once); columns in `free`
    (and the intercept) unpenalised -> {alpha: predictions}."""
    X1 = np.hstack([X, np.ones((len(X), 1), X.dtype)]).astype(np.float64)
    oof = {al: np.zeros(len(y)) for al in alphas}
    for f in np.unique(g):
        tr = g != f; G = X1[tr].T @ X1[tr]; b = X1[tr].T @ y[tr]
        for al in alphas:
            P = np.full(X1.shape[1], al); P[free] = 1e-6; P[-1] = 1e-6       # tiny: a constant column stays solvable
            oof[al][~tr] = X1[~tr] @ np.linalg.solve(G + np.diag(P), b)
    return oof


def r2(y, p): return 1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum()


def test(dirs, E, Ech, Y, Xb, pos, a, rng, boot):
    """One direction (lat, w) over the cached nodes -> gain, its bootstrap, the node count."""
    lat, w = dirs
    rows = []
    for i, (ep, ch) in enumerate(zip(E, Ech)):
        e = float(ep[lat] @ w); post = {m: float(v[lat] @ w) for m, (v, n, N) in ch.items()}
        vals = sorted(post.values())
        if vals[-1] - vals[0] < a.spread or vals[-1] == vals[-2]: continue
        m = max(post, key=post.get); _, n, N = ch[m]
        rows.append((i, e, np.log((n + 0.5) / (N - n + 0.5))))
    if len(rows) < a.min_nodes: return None
    idx = np.array([r[0] for r in rows]); e = np.array([r[1] for r in rows]); y = np.array([r[2] for r in rows])
    X = Xb[idx]; g_ = pos[idx]; folds = np.unique(g_); fmap = {p: k % a.folds for k, p in enumerate(rng.permutation(folds))}
    g = np.array([fmap[p] for p in g_])
    P0 = ridge_oof(X, y, g, a.alphas, []); best = max(a.alphas, key=lambda al: r2(y, P0[al]))
    p0 = P0[best]; p1 = ridge_oof(np.hstack([X, e[:, None]]), y, g, [best], [X.shape[1]])[best]
    gain = r2(y, p1) - r2(y, p0)
    bs = []
    if boot:
        up = np.unique(g_)
        for _ in range(a.boot):
            pick = rng.choice(up, len(up)); ii = np.concatenate([np.flatnonzero(g_ == p) for p in pick])
            bs.append(r2(y[ii], p1[ii]) - r2(y[ii], p0[ii]))
    er = e - ridge_oof(X, e, g, [best], [])[best]                                   # e_pre with the board read out
    yr = y - p0
    return dict(gain=float(gain), lo=float(np.percentile(bs, 2.5)) if bs else None, hi=float(np.percentile(bs, 97.5)) if bs else None,
                r2_board=float(r2(y, p0)), corr=float(np.corrcoef(e, y)[0, 1]) if e.std() > 0 else 0.0, partial=float(np.corrcoef(er, yr)[0, 1]) if er.std() > 0 else 0.0,
                nodes=len(rows), positions=len(np.unique(g_)), alpha=best)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tag", default="p16-r1024-T0.4-s0-L11-4k")
    ap.add_argument("--source", default=str(Path(__file__).resolve().parents[2] / "runs/transcend/manypositions/p16-r1024-T0.4-s0"))
    ap.add_argument("--only", default="")
    ap.add_argument("--node", type=int, default=20, help="rollouts through a node")
    ap.add_argument("--spread", type=float, default=0.5, help="children's expressions must spread by this much (units of mu)")
    ap.add_argument("--min-nodes", type=int, default=30)
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--alphas", default="1,10,100,1000")
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--n-random", type=int, default=20)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(); a.alphas = [float(x) for x in a.alphas.split(",")]
    md_dir = RUNS / a.tag / "mine"
    roots = json.loads((Path(a.source) / "positions.json").read_text(encoding="utf-8"))
    J = json.loads((md_dir / "steer-jobs.json").read_text())["jobs"]
    if a.only: J = [j for j in J if j["id"] in a.only.split(",")]
    need = sorted({x for j in J for x in j["lat"] + [l for r in j["random"][:a.n_random] for l in r["lat"]]})
    col = {x: i for i, x in enumerate(need)}
    data = {}
    for m in "SW":                                                          # nodes of m's rollouts, dense on the needed latents
        run = RUNS / a.tag / m; mu = mu_of(run); E, Ech, Xb, pos = [], [], [], []
        for p in range(len(roots)):
            D, Z = load_pos(run, p, mu); Z = Z[:, need].toarray()
            nodes, B = nodes_of(D, roots[p], a.node)
            for (t, q0, ch), bx in zip(nodes, B):
                N = sum(n for _, n in ch.values())
                E.append(Z[q0 * (PL + 1) + t - 1]); Ech.append({mv: (Z[q * (PL + 1) + t], n, N) for mv, (q, n) in ch.items()})
                Xb.append(bx); pos.append(p)
        data[m] = (E, Ech, np.array(Xb), np.array(pos))
        print(f"{m}: {len(E)} nodes over {len(roots)} positions", flush=True)
    part = md_dir / "lookahead-rows.jsonl"                                  # one row per concept as it finishes; rerun resumes
    res = [json.loads(l) for l in part.read_text().splitlines()] if part.exists() else []
    have = {r["id"] for r in res}
    for j in J:
        if j["id"] in have: continue
        rng = np.random.default_rng([a.seed, int(j["id"][1:]), ord(j["id"][0])])
        w = np.array(j["w"]); row = dict(id=j["id"], model=j["model"], theme=j.get("theme"), shared=j["shared"])
        for which, m in (("own", j["model"]), ("other", j["other"])):
            E, Ech, Xb, pos = data[m]
            row[which] = test(([col[x] for x in j["lat"]], w), E, Ech, None, Xb, pos, a, rng, True)
            nul = [test(([col[x] for x in r["lat"]], w), E, Ech, None, Xb, pos, a, rng, False) for r in j["random"][:a.n_random]]
            g = [x["gain"] for x in nul if x]; pc = [x["partial"] for x in nul if x]
            row[which + "_null"] = dict(n=len(g), median=float(np.median(g)) if g else None, p95=float(np.percentile(g, 95)) if g else None,
                                        partial_median=float(np.median(pc)) if pc else None, partial_p95=float(np.percentile(pc, 95)) if pc else None)
        res.append(row)
        with part.open("a") as fh: fh.write(json.dumps(row) + "\n")
        print(j["id"], {k: (round(row[k]["gain"], 4) if row[k] else None) for k in ("own", "other")}, flush=True)
    f_ = lambda x, d=3: "–" if x is None else f"{x:+.{d}f}"
    md = ["# Look-ahead at L11", "",
          f"Per concept, its expression at a branching point (before the move) against the logit of the share of rollouts playing "
          f"the move after which the concept is highest (nodes with >= {a.node} rollouts, >= 2 moves, the children's expressions "
          f"spreading by >= {a.spread}). Gain: out-of-fold R^2 of board + expression minus board alone ({a.folds} folds by position), "
          f"95% bootstrap over positions. Null: {a.n_random} random directions of matching firing rate, each run end to end. "
          "Partial: the correlation of the expression and the share once the board is read out of both.", "",
          "| concept | theme | rollouts | nodes (positions) | R^2 board | gain [95% CI] | null median / 95th | partial r | null partial median / 95th | above null 95th |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    res = [r for r in res if not a.only or r["id"] in a.only.split(",")]
    for r in res:
        for which in ("own", "other"):
            x, n = r[which], r[which + "_null"]
            if not x:
                md.append(f"| {r['id']} | {r['theme'] or ''} | {which} ({r['model'] if which == 'own' else ('W' if r['model'] == 'S' else 'S')}) | too few nodes | | | | | | |"); continue
            above = n["p95"] is not None and x["gain"] > n["p95"] and x["lo"] > 0
            md.append(f"| {r['id']} | {r['theme'] or ''} | {which} ({r['model'] if which == 'own' else ('W' if r['model'] == 'S' else 'S')}) | "
                      f"{x['nodes']} ({x['positions']}) | {x['r2_board']:.3f} | {f_(x['gain'], 4)} [{f_(x['lo'], 4)}, {f_(x['hi'], 4)}] | "
                      f"{f_(n['median'], 4)} / {f_(n['p95'], 4)} | {f_(x['partial'], 2)} | {f_(n['partial_median'], 2)} / {f_(n['partial_p95'], 2)} | "
                      f"{'yes' if above else 'no'} |")
    od = RESULTS / a.tag / "mine"; od.mkdir(parents=True, exist_ok=True)
    (od / "lookahead.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (od / "lookahead.json").write_text(json.dumps(dict(settings={k: v for k, v in vars(a).items()}, rows=res)))
    print(f"wrote {od / 'lookahead.md'}")


if __name__ == "__main__":
    main()
