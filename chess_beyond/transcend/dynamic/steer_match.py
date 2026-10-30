"""Does pushing a concept change the policy the way having it does? No name needed: both effects are read off the model.

Pairs (prep, CPU): each branch pair of the concept (its family's members), at the matched plies t..t+k of its chosen
and subpar lines where the concept is higher on the chosen line (cached w . z, by more than --min-gap): the concept
naturally high (chosen) against low (subpar), at the same depth from the same branching point.
  natural   the move distribution at the chosen state minus that at the subpar state
  injected  the distribution at the subpar state after h -> h + r ||h|| u_hat, minus its own; u_hat the unit direction
            of +v, -v, or a random v (matching firing rates, the same weights): every push equally hard
Two spaces, since the two states' legal moves differ:
  common    the moves legal in both, probabilities renormalised over them (skipped when fewer than 2)
  features  the expected move features: piece moved (6), from (64), to (64), capture, check, castles
Alignment per pair: the injected change's projection on the unit natural change (how far the push moves the policy
toward having the concept, in probability or feature units), and its cosine. Decision rule as steer_concepts.py, at
--primary: +v's mean alignment above every random v's, -v's below zero, p from the z against the random v's,
Benjamini-Hochberg over concepts; in the other model at any strength (Bonferroni), above the random 95th.
--neg-rule median: -v no better than the random v's median, in place of below zero.

Fresh pairs (--pairs fresh): branch pairs the concept was not mined from: concept_mine.py's decisive branch points
(--node, --wc, --min-share, its defaults) at positions none of its members come from, over its most common window k,
at matched plies where it is higher on the chosen line by more than --min-gap; at most --max-pairs, drawn at random.
--spaces id:space,... names each concept's pre-specified space; the summary then decides it there alone, with
Benjamini-Hochberg over those tests.
--history n (run, summary): push at the prompt ends of the last n plies (steer_hist.py), each by its own norm.
--name: a suffix for this variant's files (jobs, results).

    python transcend/dynamic/steer_match.py prep --only S141,S8,W29,S14,W25,S29,W138,W30,S58,W197
    python transcend/dynamic/steer_match.py run --device cuda
    python transcend/dynamic/steer_match.py summary
-> results/transcend/divergence/<tag>/mine/steer-match.md (.json)"""
import argparse, json, sys, time
from pathlib import Path
from collections import Counter
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # chess_beyond/
import paths  # noqa: E402  also puts transcend/'s folders on sys.path
import steer_concepts as sc
import steer_after as sa
from concept_mine import load_pos, mu_of, PL

RUNS, RESULTS, ROOT = sc.RUNS, sc.RESULTS, sc.ROOT


def jobs_file(a): return f"steer-match{'-' + a.name if a.name else ''}-jobs.json"


def stem(a): return f"steer-match{'-' + a.name if a.name else ''}{f'-h{a.history}' if a.history > 1 else ''}"


# ------------------------------------------------------------------ prep (CPU)
def prep(a):
    roots = json.loads((Path(a.source) / "positions.json").read_text(encoding="utf-8"))
    md = sc.mine_dir(a)
    F = {m: json.loads((md / f"examples-{m}.json").read_text()) for m in "SW"}
    R0 = {m: {f'{r["pos"]}/{r["t"]}/{r["c"]}/{r["s"]}/{r["k"]}': r for r in json.loads((md / f"lp-{m}-s0.json").read_text())} for m in "SW"}
    cache, out, mus = {}, [], {m: mu_of(RUNS / a.tag / m) for m in "SW"}
    from types import SimpleNamespace
    from concept_mine import pairs_of
    npos = len(roots); rng = np.random.default_rng(a.seed)
    for jb in sa.jobs(a):
        m = jb["model"]; f = F[m][int(jb["id"][1:])]; w = np.array(jb["w"]); pairs, seen = [], set()
        if a.pairs == "fresh":                                             # decisive pairs at positions it was not mined from
            used = {R0[m][k_]["pos"] for k_ in f["members"]}; K = int(max(f["ks"], key=lambda x: f["ks"][x]))
            ns = SimpleNamespace(node=a.node, wc=a.wc, min_share=a.min_share); recs = []
            for pos in range(npos):
                if pos in used: continue
                if (m, pos) not in cache: cache[(m, pos)] = load_pos(RUNS / a.tag / m, pos, mus[m])
                recs += [dict(p_, pos=pos, k=K) for p_ in pairs_of(cache[(m, pos)][0], ns)]
        else:
            recs = [R0[m][key] for key in f["members"]]
        for r in recs:
            if (m, r["pos"]) not in cache: cache[(m, r["pos"])] = load_pos(RUNS / a.tag / m, r["pos"], mus[m])
            D, Z = cache[(m, r["pos"])]; sc_, ss = D[r["c"]]["sans"], D[r["s"]]["sans"]
            for d in range(r["k"] + 1):
                row = r["t"] + d
                if row > min(len(sc_), len(ss)): break
                ec = float(Z[r["c"] * (PL + 1) + row, jb["lat"]].toarray().ravel() @ w)
                es = float(Z[r["s"] * (PL + 1) + row, jb["lat"]].toarray().ravel() @ w)
                if ec - es <= a.min_gap: continue
                pc, fc = sc.prompt_at(roots[r["pos"]], sc_, row); ps, fs = sc.prompt_at(roots[r["pos"]], ss, row)
                if (pc, ps) in seen: continue
                seen.add((pc, ps))
                pairs.append(dict(pos=r["pos"], step=d, high=dict(prompt=pc, fen=fc), low=dict(prompt=ps, fen=fs), gap=round(ec - es, 3)))
        if a.max_pairs and len(pairs) > a.max_pairs: pairs = [pairs[i] for i in sorted(rng.choice(len(pairs), a.max_pairs, replace=False))]
        out.append(dict({k: v for k, v in jb.items() if k != "points"}, pairs=pairs))
        print(f"{jb['id']}: {len(recs)} {'fresh ' if a.pairs == 'fresh' else ''}branch pairs -> {len(pairs)} matched plies ({len({p['pos'] for p in pairs})} positions)", flush=True)
    (md / jobs_file(a)).write_text(json.dumps(dict(settings=vars(a), jobs=out)))
    print(f"prep: {len(out)} concepts, {sum(len(j['pairs']) for j in out)} pairs -> {md / jobs_file(a)}")


# ------------------------------------------------------------------ run (GPU)
def run(a):
    import torch, chess
    dev, gd, cc, models, idx = sa.setup(a)
    from steer_hist import policy_hist
    J = sa.jobs(a, jobs_file(a)); rs = [float(x) for x in a.strengths.split(",")]
    out = sc.mine_dir(a) / f"{stem(a)}.jsonl"
    done = {(r["id"], r["target_model"]) for r in map(json.loads, out.read_text().splitlines())} if out.exists() else set()
    fh = out.open("a"); t0 = time.time()
    print(f"run: {len(J)} concepts, {sum(len(j['pairs']) for j in J)} pairs, strengths {rs}, {a.n_random} random v's, "
          f"history {a.history} plies, on {dev}", flush=True)
    rd = lambda v: [round(float(x), 5) for x in v]
    for n_, jb in enumerate(J):
        for tm in (jb["model"], jb["other"]):
            if (jb["id"], tm) in done: continue
            mi = idx[tm]; col = cc.col[mi]; model = models[mi]; L = str(cc.layer[mi])
            P = [p for p in jb["pairs"] if sa.fits(models, [p["high"]]) and sa.fits(models, [p["low"]])]
            if not P: continue
            bh = [chess.Board(p["high"]["fen"]) for p in P]; bl = [chess.Board(p["low"]["fen"]) for p in P]
            lh, ph, _ = gd.policy(model, bh, dev, [p["high"]["prompt"] for p in P], batch=a.batch)
            ll, pl, st = gd.policy(model, bl, dev, [p["low"]["prompt"] for p in P], grab=(L,), batch=a.batch)
            h = st[L].to(dev); hn = h.norm(dim=1, keepdim=True)
            u = sa.direction(cc, jb["lat"], jb["w"], jb["mu"], col, dev); u = u / u.norm()
            conds = {"+v": u, "-v": -u}
            for r_i, rr in enumerate(jb["random"][:a.n_random]):
                d = sa.direction(cc, rr["lat"], jb["w"], rr["mu"], col, dev); conds[f"rand{r_i}"] = d / d.norm()
            rec = dict(id=jb["id"], model=jb["model"], target_model=tm, tier=jb["tier"], theme=jb["theme"], shared=jb["shared"],
                       pairs=[dict(pos=p["pos"], step=p["step"], gap=p["gap"], high=p["high"]["fen"], low=p["low"]["fen"],
                                   high_moves=[m.uci() for m in lh[i]], low_moves=[m.uci() for m in ll[i]], high_lp=rd(ph[i]), low_lp=rd(pl[i]))
                              for i, p in enumerate(P)], runs={})
            combos = [(cn, r) for cn in conds for r in rs]; n = len(P); prompts = [p["low"]["prompt"] for p in P]
            for s in range(0, len(combos), a.chunk):
                cs = combos[s:s + a.chunk]
                if a.history > 1:
                    dirs = torch.stack([conds[cn] for cn, r in cs for _ in range(n)]); rr = [r for cn, r in cs for _ in range(n)]
                    _, lp = policy_hist(model, bl * len(cs), dev, prompts * len(cs), L, a.history, dirs, rr, a.batch)
                else:
                    repl = torch.cat([h + r * hn * conds[cn][None] for cn, r in cs]).float().cpu()
                    _, lp, _ = gd.policy(model, bl * len(cs), dev, prompts * len(cs), layer=L, repl=repl, batch=a.batch)
                for c_i, (cn, r) in enumerate(cs): rec["runs"][f"{cn}@{r}"] = [rd(x) for x in lp[c_i * n:(c_i + 1) * n]]
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            print(f"  {jb['id']} into {tm}: {n} pairs", flush=True)
        print(f"{n_ + 1}/{len(J)} {jb['id']} ({time.time() - t0:.0f}s)", flush=True)


# ------------------------------------------------------------------ summary (CPU)
def feats(fen, moves):
    """Per legal move: piece moved (6), from (64), to (64), capture, check, castles."""
    import chess
    b = chess.Board(fen); X = np.zeros((len(moves), 6 + 128 + 3))
    for i, u in enumerate(moves):
        mv = chess.Move.from_uci(u); p = b.piece_at(mv.from_square)
        X[i, p.piece_type - 1] = 1; X[i, 6 + mv.from_square] = 1; X[i, 70 + mv.to_square] = 1
        X[i, 134] = b.is_capture(mv); X[i, 135] = b.gives_check(mv); X[i, 136] = b.is_castling(mv)
    return X


def deltas(p, runs, keys):
    """One pair -> {space: (natural change, {condition: injected change})}."""
    ph, pl = np.exp(np.array(p["high_lp"])), np.exp(np.array(p["low_lp"]))
    out = {}
    com = [m for m in p["low_moves"] if m in set(p["high_moves"])]
    if len(com) >= 2:
        ih = [p["high_moves"].index(m) for m in com]; il = [p["low_moves"].index(m) for m in com]
        nrm = lambda q: q / max(q.sum(), 1e-12)
        base = nrm(pl[il])
        out["common"] = (nrm(ph[ih]) - base, {k: nrm(np.exp(np.array(runs[k]))[il]) - base for k in keys})
    Xh, Xl = feats(p["high"], p["high_moves"]), feats(p["low"], p["low_moves"])
    base = pl @ Xl
    out["features"] = (ph @ Xh - base, {k: np.exp(np.array(runs[k])) @ Xl - base for k in keys})
    return out


def summary(a):
    from statistics import NormalDist
    nd = NormalDist(); rs = [float(x) for x in a.strengths.split(",")]
    R = [json.loads(l) for l in (sc.mine_dir(a) / f"{stem(a)}.jsonl").read_text().splitlines()]
    negok = (lambda t: t["neg"] <= t["rmed"]) if a.neg_rule == "median" else (lambda t: t["neg"] < 0)
    negtxt = "-v no better than the random median" if a.neg_rule == "median" else "-v below zero"
    if a.only: R = [r for r in R if r["id"] in a.only.split(",")]
    def align(r):
        """-> {space: {condition@r: (mean projection, mean cosine)}}, pairs per space, mean natural size."""
        keys = list(r["runs"]); acc = {}; nat = {}
        for i, p in enumerate(r["pairs"]):
            for sp, (dn, di) in deltas(p, {k: r["runs"][k][i] for k in keys}, keys).items():
                nn = np.linalg.norm(dn)
                if nn < 1e-9: continue
                nat.setdefault(sp, []).append(nn)
                for k, x in di.items():
                    acc.setdefault(sp, {}).setdefault(k, []).append((float(x @ dn / nn), float(x @ dn / (nn * np.linalg.norm(x) + 1e-12))))
        return {sp: {k: tuple(np.mean(v, 0)) for k, v in d.items()} for sp, d in acc.items()}, {sp: len(v) for sp, v in nat.items()}, \
               {sp: float(np.mean(v)) for sp, v in nat.items()}
    def test(A, s, f=0):
        if f"+v@{s}" not in A: return None
        obs, neg = A[f"+v@{s}"][f], A[f"-v@{s}"][f]
        rnd = [A[k][f] for k in A if k.startswith("rand") and k.endswith(f"@{s}")]
        if len(rnd) < 3: return None
        m_, sd = float(np.mean(rnd)), float(np.std(rnd, ddof=1)) or 1e-9
        return dict(obs=obs, neg=neg, rmed=float(np.median(rnd)), rmax=max(rnd), r95=float(np.percentile(rnd, 95)), p=1 - nd.cdf((obs - m_) / sd))
    def bh(ps):
        ps = np.array(ps, float); n = len(ps); o = np.argsort(ps); q = np.empty(n)
        q[o] = np.minimum.accumulate((ps[o] * n / np.arange(1, n + 1))[::-1])[::-1]
        return np.minimum(q, 1)
    rows = {}
    for r in R:
        A, npairs, nat = align(r)
        row = rows.setdefault(r["id"], dict(id=r["id"], model=r["model"], theme=r["theme"], shared=r["shared"], positions=len({p["pos"] for p in r["pairs"]})))
        own = r["target_model"] == r["model"]
        for sp in ("common", "features"):
            if sp not in A: continue
            if own:
                row[sp] = dict(pairs=npairs[sp], natural=nat[sp], self=test(A[sp], a.primary), cos=test(A[sp], a.primary, 1),
                               dose=[A[sp][f"+v@{s}"][0] for s in rs], neg_dose=[A[sp][f"-v@{s}"][0] for s in rs])
            else:
                ts = {s: v for s in rs if (v := test(A[sp], s))}
                best = min(ts.items(), key=lambda kv: kv[1]["p"]) if ts else None
                row.setdefault(sp, {}).update(other=r["target_model"], xfer=best[1] if best else None, xfer_r=best[0] if best else None,
                                               xfer_p=min(1, best[1]["p"] * len(ts)) if best else None)
    rows = list(rows.values())
    for sp in ("common", "features"):
        S = [r for r in rows if (r.get(sp) or {}).get("self")]; q = bh([r[sp]["self"]["p"] for r in S])
        for r, qq in zip(S, q):
            t = r[sp]["self"]; r[sp]["q"] = float(qq); r[sp]["pass"] = bool(t["obs"] > t["rmax"] and negok(t) and qq < a.fdr)
        X = [r for r in rows if (r.get(sp) or {}).get("xfer")]; q = bh([r[sp]["xfer_p"] for r in X])
        for r, qq in zip(X, q): r[sp]["xq"] = float(qq); r[sp]["transfers"] = bool(r[sp]["xfer"]["obs"] > r[sp]["xfer"]["r95"] and qq < a.fdr)
    f_ = lambda x, d=3: "–" if x is None else f"{x:+.{d}f}"
    md = ["# Pushing a concept against having it", "",
          f"Matched plies of each branch pair's chosen (concept high) and subpar (low) lines. Natural: the chosen state's move "
          f"distribution minus the subpar state's. Injected: the subpar state's after h -> h + r ||h|| u_hat (r = {', '.join(map(str, rs))}), "
          f"minus its own; +v, -v and {a.n_random} random v's of matching firing rate, all pushing equally hard. Alignment: the injected "
          f"change projected on the unit natural change, mean over pairs (beside it the mean cosine). Self-check at r = {a.primary}: "
          f"+v above every random v, {negtxt}, Benjamini-Hochberg q < {a.fdr}; transfer at any r (Bonferroni), above the random 95th."
          + (f" Pushed at the last {a.history} plies' prompt ends, each by its own norm." if a.history > 1 else "")
          + (" Fresh branch pairs: positions the concept was not mined from." if a.name.startswith("fresh") else ""), ""]
    if a.spaces:                                                           # the pre-specified test: one space per concept
        pre = [(r, sp) for i_, sp in (x.split(":") for x in a.spaces.split(",")) for r in rows if r["id"] == i_ and (r.get(sp) or {}).get("self")]
        q = bh([r[sp]["self"]["p"] for r, sp in pre])
        md += ["## Pre-specified", "", f"Each concept in its named space only; Benjamini-Hochberg over these {len(pre)} tests.", "",
               "| concept | space | pairs (positions) | +v | -v | random median | random max | +v / natural size | q | verdict |",
               "|---|---|---|---|---|---|---|---|---|---|"]
        for (r, sp), qq in zip(pre, q):
            t = r[sp]["self"]; ok = t["obs"] > t["rmax"] and negok(t) and qq < a.fdr
            r[sp]["pre_q"], r[sp]["pre_pass"] = float(qq), bool(ok)
            md.append(f"| {r['id']} | {sp} | {r[sp]['pairs']} ({r['positions']}) | {f_(t['obs'])} | {f_(t['neg'])} | {f_(t['rmed'])} | {f_(t['rmax'])} | "
                      f"{t['obs'] / r[sp]['natural']:.1%} | {qq:.3f} | {'passes' if ok else 'fails'} |")
        md.append("")
    for sp, unit in (("common", "probability over the moves legal in both states"), ("features", "expected move features")):
        R_ = [r for r in rows if r.get(sp)]
        md += [f"## {sp}: {unit}", "",
               f"Self-check passes: {sum(r[sp].get('pass', False) for r in R_)} of {sum(1 for r in R_ if r[sp].get('self'))}; "
               f"transfer: {sum(r[sp].get('transfers', False) for r in R_ if r[sp].get('pass'))} of those.", "",
               f"| concept | theme | shared cos | pairs (positions) | natural size | +v / -v / random median / max (q), r = {a.primary} | cosine +v / -v / random median / max | +v over r | -v over r | self-check | transfer: other +v / random 95th @r (q) |",
               "|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in sorted(R_, key=lambda r: (not r[sp].get("pass", False), -r["shared"])):
            x = r[sp]; s_, c_, t_ = x.get("self") or {}, x.get("cos") or {}, x.get("xfer") or {}
            md.append(f"| {r['id']} | {r['theme'] or ''} | {r['shared']} | {x.get('pairs', '–')} ({r['positions']}) | {x.get('natural', 0):.3f} | "
                      f"{f_(s_.get('obs'))} / {f_(s_.get('neg'))} / {f_(s_.get('rmed'))} / {f_(s_.get('rmax'))} ({x.get('q', float('nan')):.2f}) | "
                      f"{f_(c_.get('obs'), 2)} / {f_(c_.get('neg'), 2)} / {f_(c_.get('rmed'), 2)} / {f_(c_.get('rmax'), 2)} | "
                      f"{' '.join(f_(v) for v in x.get('dose', []))} | {' '.join(f_(v) for v in x.get('neg_dose', []))} | "
                      f"{'passes' if x.get('pass') else 'fails'} | {x.get('other', '')} {f_(t_.get('obs'))} / {f_(t_.get('r95'))} @{x.get('xfer_r', '–')} "
                      f"({x.get('xq', float('nan')):.2f}) |")
        md.append("")
    md += ["Natural size: the mean length of the natural change (the same units as the alignment); an alignment equal to it "
           "would mean the push reproduces the whole difference between having the concept and not.", ""]
    od = RESULTS / a.tag / "mine"; od.mkdir(parents=True, exist_ok=True)
    (od / f"{stem(a)}.md").write_text("\n".join(md) + "\n", encoding="utf-8"); (od / f"{stem(a)}.json").write_text(json.dumps(rows, default=str))
    print(f"wrote {od / (stem(a) + '.md')}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["prep", "run", "summary"])
    ap.add_argument("--tag", default="p16-r1024-T0.4-s0-L11-4k")
    ap.add_argument("--source", default=str(ROOT / "runs/transcend/manypositions/p16-r1024-T0.4-s0"))
    ap.add_argument("--cc-run", default="runs/transcend/crosscoder/mixed-L11")
    ap.add_argument("--cc", default="L11-4096")
    ap.add_argument("--strong", default="2400")
    ap.add_argument("--only", default="")
    ap.add_argument("--min-gap", type=float, default=0.0, help="prep: the concept higher on the chosen line by more than this")
    ap.add_argument("--pairs", choices=["members", "fresh"], default="members")
    ap.add_argument("--node", type=int, default=30, help="prep --pairs fresh: concept_mine.py's branch-point thresholds")
    ap.add_argument("--wc", type=float, default=0.75)
    ap.add_argument("--min-share", type=float, default=0.02)
    ap.add_argument("--max-pairs", type=int, default=0, help="prep: at most this many matched plies per concept, drawn at random")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--name", default="", help="a suffix for this variant's files")
    ap.add_argument("--history", type=int, default=1, help="run/summary: push at the last n plies' prompt ends")
    ap.add_argument("--neg-rule", choices=["zero", "median"], default="zero")
    ap.add_argument("--spaces", default="", help="summary: id:space,... the pre-specified space per concept")
    ap.add_argument("--strengths", default="0.1,0.25,0.5")
    ap.add_argument("--primary", type=float, default=0.25)
    ap.add_argument("--n-random", type=int, default=20)
    ap.add_argument("--chunk", type=int, default=6)
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--fdr", type=float, default=0.05)
    ap.add_argument("--device", default="auto")
    a = ap.parse_args()
    {"prep": prep, "run": run, "summary": summary}[a.command](a)


if __name__ == "__main__":
    main()
