"""Does any pattern of latents recur, persistently, across many positions? S only: S plays every move of every rollout
(W's activations are read too, because the crosscoder encodes the pair).

    python transcend/manypositions.py --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal --positions 1   # time one
    python transcend/manypositions.py --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal --positions 50

1. positions   --positions held-out middlegame positions from as many different games, by oneposition's rule (>= 2
               moves S plays >= --reasonable, none above --max-top), in a seeded random order.
2. rollouts    at each: --rollouts rollouts of --plies plies at temperature --temperature, S playing both colours,
               encoded (distinct lines, weighted by how often each was sampled). Cached per position, so a run with a
               larger --positions reuses the ones already played; the first position's time gives the projected total.
3. groups      per position, as oneposition (no branch correction, no route or board nulls): weighted correlations of
               the latents whose fraction of plies varies, the family-wise shuffle threshold, average linkage, groups of
               >= 3 latents, every group kept.
4. persistence per group and carrying line (half the group's latents above their weighted median), the longest run of
               consecutive plies where at least half the group's latents are on; each group's weighted median run.
5. matching    two groups from different positions match at Jaccard >= --jaccard of their latents; matching groups
               joined into recurring patterns (connected components); recurrence = the distinct positions in one.
6. chance      each latent's share of all lines (every position) where it fires; a pattern is flagged when most of its
               latents fire in > --common of all lines (side to move, material: they would recur trivially). Null:
               every group's latents swapped for random candidate latents of its position with a similar overall
               firing rate (the same decile), step 5 rerun, --null-runs times: recurrence counts by chance.
7. report      recurring patterns by recurrence (latents, positions, the null's count at that recurrence, median
               persistence, flag); for the top --show, example lines from 3 positions, the plies where the pattern is
               on in [brackets]; the recurrence histogram next to the null's.

-> results/transcend/manypositions/<tag>/report.md, report.json; rollouts and codes in runs/transcend/manypositions/<tag>."""

import argparse
import json
import sys
import time
from pathlib import Path

import chess
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paths
import eval as ev
import graphdiff as gd
import oneposition as op
from concepts import room
from pgn_model import MAX_MOVE_CHARS, prompt
from pgn_probe import parse_movetext

RUNS = paths.RUNS / "transcend" / "manypositions"
RESULTS = paths.ROOT / "results" / "transcend" / "manypositions"


def pick_positions(a, Sm, dev):
    """Up to --positions positions from different games, each with >= 2 moves >= --reasonable and none above --max-top
    (S's policy), in a seeded random order -> [(root, legal moves, log-probabilities)]."""
    rng = np.random.default_rng(a.seed)
    pop = [json.loads(l) for l in open(a.population, encoding="utf-8")]
    out, games = [], set()
    order = rng.permutation(len(pop))
    for s in range(0, len(order), a.scan):
        cand = []
        for i in order[s:s + a.scan]:
            r = pop[i]
            if (r["band"], r["game"]) in games or len(r["prompt"]) + room(a.plies) + MAX_MOVE_CHARS + 1 > Sm.ctx:
                continue
            b = ev.board_of(parse_movetext(r["prompt"])[0])
            if prompt(b) != r["prompt"] or b.is_game_over() or not gd.middlegame(b):
                continue
            cand.append((r, b))
        if not cand:
            continue
        legal, lp, _ = gd.policy(Sm, [b for _, b in cand], dev, [r["prompt"] for r, _ in cand], batch=a.batch)
        for (r, b), mv, l in zip(cand, legal, lp):
            if (r["band"], r["game"]) in games:
                continue
            p = np.exp(l - np.logaddexp.reduce(l))
            if p.max() <= a.max_top and (p >= a.reasonable).sum() >= 2:
                games.add((r["band"], r["game"]))
                top = sorted(zip(p, mv), key=lambda x: -x[0])[:5]
                out.append((dict(prompt=r["prompt"], fen=b.fen(), band=r["band"], game=r["game"],
                                 top=[(b.san(m), float(q)) for q, m in top]), mv, l))
                if len(out) >= a.positions:
                    return out
    return out


def x_of(P, D, plies, nlat):
    """Per distinct line, the share of its plies where each latent fires, from the per-ply matrix."""
    from scipy import sparse
    n = np.array([max(len(d["sans"]), 1) for d in D], float)
    rows = np.repeat(np.arange(len(D)), plies + 1)
    S = sparse.csr_matrix((np.ones(len(rows)), (rows, np.arange(len(rows)))), shape=(len(D), len(rows)))
    return np.asarray((S @ (P > 0).astype(np.float32)).todense(), np.float32) / n[:, None]


def runs_of(P, q, g, plies):
    """The longest run of consecutive plies in line q where at least half of g's latents are on, and those plies."""
    on = (P[q * (plies + 1):(q + 1) * (plies + 1)][:, g].toarray() > 0).mean(1) >= 0.5
    best, cur, plies_on = 0, 0, set()
    for t in range(1, plies + 1):
        cur = cur + 1 if on[t] else 0
        best = max(best, cur)
        if on[t]:
            plies_on.add(t)
    return best, plies_on


def wmed(v, w):
    o = np.argsort(v)
    cw = np.cumsum(w[o])
    return float(v[o][min(int(np.searchsorted(cw, cw[-1] / 2)), len(v) - 1)])


def components(groups, jac):
    """Connected components of groups (position, set of latents) joined at Jaccard >= jac across different positions."""
    par = list(range(len(groups)))

    def find(i):
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i

    by = {}
    for i, (_, s) in enumerate(groups):
        for j in s:
            by.setdefault(j, []).append(i)
    for i, (pi, si) in enumerate(groups):
        seen = set()
        for j in si:
            for k in by[j]:
                if k <= i or k in seen:
                    continue
                seen.add(k)
                pk, sk = groups[k]
                if pk != pi and len(si & sk) / len(si | sk) >= jac:
                    par[find(i)] = find(k)
    comp = {}
    for i in range(len(groups)):
        comp.setdefault(find(i), []).append(i)
    return list(comp.values())


def recurrence_hist(groups, comps):
    h = {}
    for c in comps:
        r = len({groups[i][0] for i in c})
        h[r] = h.get(r, 0) + 1
    return h


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cc-run", default="runs/transcend/crosscoder/everything-3m")
    ap.add_argument("--cc", default="Lfinal")
    ap.add_argument("--strong", default="2400", help="a part of S's name")
    ap.add_argument("--population", default=str(gd.PROBE / "population.jsonl"), help="held-out positions")
    ap.add_argument("--positions", type=int, default=50)
    ap.add_argument("--scan", type=int, default=400, help="candidate positions per policy pass while choosing")
    ap.add_argument("--reasonable", type=float, default=0.2)
    ap.add_argument("--max-top", type=float, default=0.6)
    ap.add_argument("--rollouts", type=int, default=1024)
    ap.add_argument("--plies", type=int, default=16)
    ap.add_argument("--temperature", type=float, default=0.4)
    ap.add_argument("--min-sd", type=float, default=0.05, help="candidate latents: weighted sd of their fraction of plies")
    ap.add_argument("--shuffles", type=int, default=100)
    ap.add_argument("--jaccard", type=float, default=0.5, help="latent overlap at which groups of two positions match")
    ap.add_argument("--common", type=float, default=0.8, help="a latent firing in more than this share of all lines is common")
    ap.add_argument("--null-runs", type=int, default=20)
    ap.add_argument("--show", type=int, default=10)
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--max-tokens", type=int, default=300_000)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    from scipy import sparse
    tag = a.tag or f"p{a.plies}-r{a.rollouts}-T{a.temperature}-s{a.seed}"
    run, res = RUNS / tag, RESULTS / tag
    run.mkdir(parents=True, exist_ok=True)
    res.mkdir(parents=True, exist_ok=True)

    # 1-2: positions and rollouts, cached per position
    plist = run / "positions.json"
    have = json.loads(plist.read_text(encoding="utf-8")) if plist.exists() else []
    need = [k for k in range(a.positions) if not (run / f"pos-{k}.npz").exists()]
    if need:
        dev = ev.device(a.device)
        cc = gd.load_cc(a.cc_run, a.cc, a.strong, dev)
        models = {m: ev.load(cc.info["models"][m], dev)[0] for m in (0, 1)}
        Sm = models[cc.s]
        t0 = time.time()
        picked = pick_positions(a, Sm, dev)
        print(f"{len(picked)} positions from {len(picked)} games ({time.time() - t0:.0f}s)", flush=True)
        if len(picked) < a.positions:
            print(f"  only {len(picked)} positions meet the rule", flush=True)
        roots = [p[0] for p in picked]
        m_ = min(len(have), len(roots))
        if [r["fen"] for r in have[:m_]] != [r["fen"] for r in roots[:m_]]:
            sys.exit(f"{plist} holds other positions: use another --tag")
        plist.write_text(json.dumps(roots), encoding="utf-8")
        times = []
        for k in need:
            if k >= len(picked):
                break
            t0 = time.time()
            root, legal, lp = picked[k]
            sans, ucis = op.rollouts(a, root, legal, lp, Sm, dev, a.temperature, [a.seed, k])
            D = op.distinct(sans, ucis)
            _, P = op.encode(a, cc, models, root, D, dev)
            np.savez_compressed(run / f"pos-{k}.npz", D=json.dumps(D), data=P.data, indices=P.indices, indptr=P.indptr,
                                shape=np.array(P.shape))
            times.append(time.time() - t0)
            left = len([j for j in need if j > k and j < len(picked)])
            print(f"position {k + 1}/{a.positions}: {len(D)} distinct lines ({times[-1]:.0f}s); projected: {left} left in "
                  f"{np.mean(times) * left / 60:.0f} min, 50 positions in {np.mean(times) * 50 / 60:.0f} min", flush=True)
    else:
        roots = have
    K = min(a.positions, len(roots))
    if K < 2:
        print(f"{K} position played: rerun with --positions 50 for the rest (the played ones are reused)")
        return

    # 3-4: groups and persistence per position
    rng = np.random.default_rng(a.seed)
    nlat = None
    pos = []
    share_sum = None
    t0 = time.time()
    for k in range(K):
        z = np.load(run / f"pos-{k}.npz")
        D = json.loads(str(z["D"]))
        P = sparse.csr_matrix((z["data"], z["indices"], z["indptr"]), shape=tuple(z["shape"]))
        nlat = P.shape[1]
        X = x_of(P, D, a.plies, nlat)
        w = np.array([d["n"] for d in D], float)
        w /= w.sum()
        fires = w @ (X > 0)
        share_sum = fires if share_sum is None else share_sum + fires
        kk, thr, cs, _, med = op.concepts(X, w, a, rng, f"position {k + 1}")
        for c in cs:
            g = np.array(c["latents"])
            fire = op.carrying(X, g, med)
            rl = np.array([runs_of(P, q, g, a.plies)[0] for q in np.flatnonzero(fire)])
            c["persistence"] = wmed(rl.astype(float), w[fire]) if len(rl) else 0.0
        pos.append(dict(D=D, P=P, w=w, kk=kk, thr=thr, groups=cs, med=med))
    share = share_sum / K
    print(f"groups at {K} positions ({time.time() - t0:.0f}s): {sum(len(p['groups']) for p in pos)} in all", flush=True)

    # 5: recurring patterns
    G = [(k, set(c["latents"])) for k, p in enumerate(pos) for c in p["groups"]]
    ref = [(k, i) for k, p in enumerate(pos) for i in range(len(p["groups"]))]
    comps = components(G, a.jaccard)
    hist = recurrence_hist(G, comps)

    # 6: chance
    nb = np.zeros(nlat, np.int64)
    qs = np.quantile(share, np.linspace(0, 1, 11)[1:-1])
    nb[:] = np.searchsorted(qs, share)
    null_hists, null_max = [], []
    for _ in range(a.null_runs):
        Gn = []
        for k, p in enumerate(pos):
            pool = {}
            for j in p["kk"]:
                pool.setdefault(int(nb[j]), []).append(int(j))
            for c in p["groups"]:
                new = set()
                for j in c["latents"]:
                    opts = [x for x in pool.get(int(nb[j]), []) if x not in new]
                    new.add(int(rng.choice(opts)) if opts else j)
                Gn.append((k, new))
        cn = components(Gn, a.jaccard)
        h = recurrence_hist(Gn, cn)
        null_hists.append(h)
        null_max.append(max(h))
    rmax = max(max(hist), max(null_max))
    null_mean = {r: float(np.mean([h.get(r, 0) for h in null_hists])) for r in range(1, rmax + 1)}
    null_atleast = {r: float(np.mean([sum(v for k_, v in h.items() if k_ >= r) for h in null_hists])) for r in range(1, rmax + 1)}

    pats = []
    for c in comps:
        P_ = sorted({ref[i][0] for i in c})
        if len(P_) < 2:
            continue
        lat = sorted(set().union(*[G[i][1] for i in c]))
        core = sorted(set.intersection(*[G[i][1] for i in c])) if len(c) > 1 else lat
        common = float(np.mean(share[lat] > a.common))
        per = [pos[ref[i][0]]["groups"][ref[i][1]]["persistence"] for i in c]
        pats.append(dict(members=c, positions=P_, recurrence=len(P_), latents=lat, core=core, common=common,
                         flag=common > 0.5, persistence=float(np.median(per)), null_atleast=null_atleast.get(len(P_), 0.0)))
    pats.sort(key=lambda p: (-p["recurrence"], -p["persistence"]))

    # 7: report
    out = ["# Recurring latent patterns across positions", "",
           f"{K} positions from {K} games; at each {a.rollouts} rollouts of S, {a.plies} plies, T = {a.temperature}; groups per "
           f"position as oneposition (no branch correction), {sum(len(p['groups']) for p in pos)} in all. Two groups of different "
           f"positions match at Jaccard >= {a.jaccard}; a pattern is a connected component, its recurrence the positions in it. "
           f"Null: each group's latents swapped for random candidate latents of its position in the same overall-firing decile, "
           f"{a.null_runs} runs. Flag: most of a pattern's latents fire in > {a.common:.0%} of all lines.", "",
           "## Recurrence", "", "| positions | patterns | null (mean) |", "|---|---|---|"]
    out += [f"| {r} | {hist.get(r, 0)} | {null_mean.get(r, 0):.1f} |" for r in range(1, rmax + 1)]
    out += ["", f"The null's largest recurrence over its {a.null_runs} runs: median {np.median(null_max):.0f}, max {max(null_max)}.", "",
            "## Patterns recurring at >= 2 positions", "",
            "| pattern | positions | null: patterns this recurrent (mean) | latents (core: in every member) | median persistence (plies) | common latents | flag |",
            "|---|---|---|---|---|---|---|"]
    for i, p in enumerate(pats):
        p["name"] = str(i + 1)
        out.append(f"| {p['name']} | {p['recurrence']} | {p['null_atleast']:.1f} | {', '.join(map(str, p['latents'][:12]))}"
                   f"{' ...' if len(p['latents']) > 12 else ''} (core: {', '.join(map(str, p['core'])) or '-'}) | "
                   f"{p['persistence']:.1f} | {p['common']:.0%} | {'mostly common latents' if p['flag'] else ''} |")
    out.append("")
    for p in pats[:a.show]:
        out += [f"### Pattern {p['name']}: {p['recurrence']} positions, latents {', '.join(map(str, p['latents']))}", ""]
        seen = []
        for i in p["members"]:
            k, gi = ref[i]
            if k in seen:
                continue
            seen.append(k)
            q_ = pos[k]
            g = np.array(q_["groups"][gi]["latents"])
            X = x_of(q_["P"], q_["D"], a.plies, nlat)
            fire = op.carrying(X, g, q_["med"])
            cand = [(runs_of(q_["P"], q, g, a.plies), q) for q in np.flatnonzero(fire)]
            if not cand:
                continue
            (rl, plies_on), q = max(cand, key=lambda x: (x[0][0], q_["w"][x[1]]))
            r = roots[k]
            out.append(f"- position {k + 1} (`{r['fen']}`), group latents {', '.join(map(str, g))}, on for {rl} plies in a row: "
                       f"{op.mark(q_['D'][q]['sans'], plies_on, r)}  ([Lichess]({gd.lichess_line(r, q_['D'][q]['sans'])}))")
            if len(seen) == 3:
                break
        out.append("")
    common_lat = np.flatnonzero(share > a.common)
    out += ["## Latents by share of all lines", "", f"{len(common_lat)} latents fire in > {a.common:.0%} of all lines: "
            + ", ".join(f"{j} ({share[j]:.0%})" for j in common_lat[np.argsort(-share[common_lat])][:40]), ""]
    rep = dict(settings=vars(a), positions=roots[:K], hist=hist, null_mean=null_mean, null_max=null_max,
               patterns=[{x: p[x] for x in ("name", "positions", "recurrence", "latents", "core", "common", "flag", "persistence",
                                            "null_atleast")} for p in pats],
               groups=[[{x: c[x] for x in ("latents", "share", "r", "persistence")} for c in p["groups"]] for p in pos],
               share={int(j): float(share[j]) for j in np.flatnonzero(share > 0)})
    (res / "report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    (res / "report.json").write_text(json.dumps(rep, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o), indent=1))
    print(f"{len(pats)} patterns recur at >= 2 positions (max {max(hist)}; the null's max: median {np.median(null_max):.0f}); "
          f"wrote {res / 'report.md'}")


if __name__ == "__main__":
    main()
