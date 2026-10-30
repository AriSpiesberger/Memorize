"""Overnight confirmation: choose candidates from the discovery mining, then test them on the confirmation positions.
The rules are in results/transcend/overnight/<name>-prereg.md (fixed before any data).

choose  (GPU, short) candidates: replicate across seeds, >= --min-positions discovery positions, and the push lands
        (readback >= g at 25% of ||h||); plus S14 from the old run. Frozen in results/transcend/overnight/<name>-candidates.json
prep    (CPU) per candidate, its matched plies at confirmation positions; 50 random directions of matching firing rate
run     (GPU) towards (+v into concept-low) and away (-v into concept-high), and the randoms, at the last position, L11,
        0.25 ||h||; candidates in order of discovery positions, until --stop-by
report  (CPU) results/transcend/overnight/<name>-report.md

    python transcend/dynamic/overnight_confirm.py choose --device cuda
    python transcend/dynamic/overnight_confirm.py prep
    python transcend/dynamic/overnight_confirm.py run --device cuda --stop-by 2026-10-30T06:35
    python transcend/dynamic/overnight_confirm.py report
"""
import argparse, json, sys, time
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # chess_beyond/
import paths  # noqa: E402  also puts transcend/'s folders on sys.path
import steer_concepts as sc
from concept_mine import load_pos, mu_of, pairs_of, PL

OV = paths.RUNS / "transcend" / "overnight"
DIV = paths.RUNS / "transcend" / "divergence"
RES = paths.ROOT / "results" / "transcend" / "overnight"
OLD = "p16-r1024-T0.4-s0-L11-4k"


def disc_tag(a): return f"{a.prefix}-disc-s0"
def conf_tag(a): return f"{a.prefix}-conf-s0"


def keep95(cent):
    x = np.zeros(4096)
    for j, w in cent.items(): x[int(j)] = w
    v = x / np.linalg.norm(x); order = np.argsort(-v)
    keep = order[:max(1, int(np.searchsorted(np.cumsum(v[order] ** 2), 0.95)) + 1)]
    return [int(j) for j in keep], (v[keep] / np.linalg.norm(v[keep])).tolist()


def rates(tag, m):
    run = DIV / tag / m; cnt = np.zeros(4096); rows = 0
    for f in run.glob("pos-*.npz"):
        z = np.load(f); cnt += z["vcnt"]; rows += int(z["shape"][0])
    return cnt / max(rows, 1)


def randoms(lat, rate, mu, n, rng):
    act = np.flatnonzero(rate > 0); dec = np.searchsorted(np.quantile(rate[act], np.linspace(0, 1, 11)[1:-1]), rate); out = []
    for _ in range(n):
        nl = []
        for l_ in lat:
            opts = act[dec[act] == dec[l_]]; x_ = int(rng.choice(opts))
            while x_ in nl or x_ in lat: x_ = int(rng.choice(opts))
            nl.append(x_)
        out.append(dict(lat=nl, mu=[float(mu[x_]) for x_ in nl]))
    return out


def gap_points(tag, m, members, R0, lat, w, mu, roots, n_pts):
    """The concept's natural gap g (median w . (z_chosen - z_subpar) at the split ply) and up to n_pts readback points."""
    gaps, pts, cache = [], [], {}
    for key in sorted(members, key=lambda k_: -R0[k_]["node"]):
        r = R0[key]
        if r["pos"] not in cache: cache[r["pos"]] = load_pos(DIV / tag / m, r["pos"], mu)
        D, Z = cache[r["pos"]]
        zc = Z[r["c"] * (PL + 1) + r["t"], lat].toarray().ravel(); zs = Z[r["s"] * (PL + 1) + r["t"], lat].toarray().ravel()
        gaps.append(float(np.array(w) @ (zc - zs)))
        if len(pts) < n_pts:
            p_, fen = sc.prompt_at(roots[r["pos"]], D[r["c"]]["sans"], r["t"]); pts.append(dict(prompt=p_, fen=fen))
    return float(np.median(gaps)), pts


# ------------------------------------------------------------------ choose
def choose(a):
    import torch, chess
    import steer_after as sa
    rng = np.random.default_rng(a.seed)
    rep = json.loads((paths.ROOT / "results/transcend/divergence" / disc_tag(a) / "mine" / "concepts.json").read_text())
    roots = json.loads((OV / a.name / "disc" / "positions.json").read_text(encoding="utf-8"))
    counts = dict(mined={}, replicate={}, positions={}, landed={})
    cands = []
    for m in "SW":
        mu = mu_of(DIV / disc_tag(a) / m)
        R0 = {f'{r["pos"]}/{r["t"]}/{r["c"]}/{r["s"]}/{r["k"]}': r for r in json.loads((DIV / disc_tag(a) / "mine" / f"lp-{m}-s0.json").read_text())}
        C = rep[m]["concepts"]; counts["mined"][m] = len(C)
        ok = lambda v, n, d: v is not None and n is not None and v >= n + d
        rp = [c for c in C if ok(c.get("replication"), c.get("replication_null95"), 0.15) and ok(c.get("agreement"), c.get("agreement_null95"), 0.1)
              and ok(c.get("replication_own"), c.get("replication_own_null95"), 0.0)]
        counts["replicate"][m] = len(rp)
        rp = [c for c in rp if c["positions"] >= a.min_positions]; counts["positions"][m] = len(rp)
        for c in rp:
            lat, w = keep95(c["centroid"])
            g, pts = gap_points(disc_tag(a), m, c["members"], R0, lat, w, mu, roots, a.readback_points)
            cands.append(dict(id=f"{a.prefix}:{c['id']}", model=m, source=disc_tag(a), lat=lat, w=w, mu=[float(mu[j]) for j in lat],
                              gap=g, positions=c["positions"], members=len(c["members"]), tier=c["tier"], board=c.get("board"),
                              replication=c["replication"], agreement=c["agreement"], ks=c["ks"], theme=(c.get("theme") or {}).get("name"),
                              activating=c.get("activating", []), pts=pts))
    # S14 from the old run, by default
    old = next(j for j in json.loads((DIV / OLD / "mine" / "steer-jobs.json").read_text())["jobs"] if j["id"] == "S14")
    Fo = json.loads((DIV / OLD / "mine" / "examples-S.json").read_text())[14]
    R0o = {f'{r["pos"]}/{r["t"]}/{r["c"]}/{r["s"]}/{r["k"]}': r for r in json.loads((DIV / OLD / "mine" / "lp-S-s0.json").read_text())}
    roots_o = json.loads((paths.RUNS / "transcend/manypositions/p16-r1024-T0.4-s0/positions.json").read_text(encoding="utf-8"))
    _, pts_o = gap_points(OLD, "S", Fo["members"], R0o, old["lat"], old["w"], mu_of(DIV / OLD / "S"), roots_o, a.readback_points)
    cands.append(dict(id="S14", model="S", source=OLD, lat=old["lat"], w=old["w"], mu=old["mu"], gap=old["gap"], positions=Fo["positions"],
                      members=len(Fo["members"]), tier=Fo["tier"], board=Fo.get("board"), replication=Fo["replication"], agreement=Fo["agreement"],
                      ks=Fo["ks"], theme="two or more captures", activating=Fo.get("activating", []), pts=pts_o, default=True))
    # readback on the GPU
    dev, gd, cc, models, idx = sa.setup(a)
    for c in cands:
        mi = idx[c["model"]]; mo = 1 - mi
        pts = sa.fits(models, c["pts"])
        _, _, _, _, h, oh = sa.states(gd, cc, models, mi, mo, pts, a, dev)
        u = sa.direction(cc, c["lat"], c["w"], c["mu"], cc.col[mi], dev); u = u / u.norm()
        rise = sa.readback(gd, cc, mi, mo, h, oh, 0.25 * h.norm(dim=1, keepdim=True) * u[None], c, dev)
        c["readback"] = float(np.median(rise)); c["landed"] = bool(c["readback"] >= c["gap"])
        print(f"  {c['id']} ({c['model']}, {c['positions']} positions): readback {c['readback']:+.2f} against g {c['gap']:.2f} -> "
              f"{'lands' if c['landed'] else 'does not land'}", flush=True)
    counts["landed"] = {m: sum(c["landed"] for c in cands if c["model"] == m and not c.get("default")) for m in "SW"}
    chosen = [c for c in cands if c["landed"] or c.get("default")]
    chosen.sort(key=lambda c: -c["positions"])
    for c in chosen: c.pop("pts", None)
    RES.mkdir(parents=True, exist_ok=True)
    out = dict(frozen=datetime.now().isoformat(timespec="seconds"), counts=counts, all=[{k: v for k, v in c.items() if k not in ("pts", "activating")} for c in cands],
               candidates=chosen)
    (RES / f"{a.name}-candidates.json").write_text(json.dumps(out, indent=1))
    print(f"frozen {len(chosen)} candidates -> {RES / (a.name + '-candidates.json')}; counts {counts}", flush=True)


# ------------------------------------------------------------------ prep
def prep(a):
    rng = np.random.default_rng(a.seed)
    C = json.loads((RES / f"{a.name}-candidates.json").read_text())["candidates"]
    roots = json.loads((OV / a.name / "conf" / "positions.json").read_text(encoding="utf-8"))
    ns = SimpleNamespace(node=a.node, wc=a.wc, min_share=a.min_share); jobs = []
    for c in C:
        m = c["model"]; run = DIV / conf_tag(a) / m; mu = np.ones(4096)
        mu[c["lat"]] = c["mu"]                                           # only the concept's latents are read
        K = int(max(c["ks"], key=lambda x: c["ks"][x])); w = np.array(c["w"]); pairs, seen = [], set()
        for pos in range(len(roots)):
            if not (run / f"pos-{pos}.npz").exists(): continue
            D, Z = load_pos(run, pos, mu)
            for r in pairs_of(D, ns):
                sc_, ss = D[r["c"]]["sans"], D[r["s"]]["sans"]
                for d in range(K + 1):
                    row = r["t"] + d
                    if row > min(len(sc_), len(ss)): break
                    ec = float(Z[r["c"] * (PL + 1) + row, c["lat"]].toarray().ravel() @ w)
                    es = float(Z[r["s"] * (PL + 1) + row, c["lat"]].toarray().ravel() @ w)
                    if ec - es <= a.min_gap: continue
                    pc, fc = sc.prompt_at(roots[pos], sc_, row); ps, fs = sc.prompt_at(roots[pos], ss, row)
                    if (pc, ps) in seen: continue
                    seen.add((pc, ps)); pairs.append(dict(pos=pos, step=d, gap=round(ec - es, 3), high=dict(prompt=pc, fen=fc), low=dict(prompt=ps, fen=fs)))
        if len(pairs) > a.max_pairs: pairs = [pairs[i] for i in sorted(rng.choice(len(pairs), a.max_pairs, replace=False))]
        rate = rates(c["source"], m); mu_full = mu_of(DIV / c["source"] / m)
        jobs.append(dict(c, pairs=pairs, random=randoms(c["lat"], rate, mu_full, a.n_random, rng)))
        print(f"{c['id']} ({m}): {len(pairs)} matched plies at {len({p['pos'] for p in pairs})} confirmation positions", flush=True)
    (OV / a.name / "confirm-jobs.json").write_text(json.dumps(jobs))


# ------------------------------------------------------------------ run
def run(a):
    import torch, chess
    import steer_after as sa
    stop = datetime.fromisoformat(a.stop_by)
    dev, gd, cc, models, idx = sa.setup(a)
    J = json.loads((OV / a.name / "confirm-jobs.json").read_text())
    out = OV / a.name / "confirm.jsonl"
    done = {json.loads(l)["id"] for l in out.read_text().splitlines()} if out.exists() else set()
    rd = lambda v: [round(float(x), 5) for x in v]; t0 = time.time()
    for n_, jb in enumerate(J):
        if jb["id"] in done: continue
        if datetime.now() >= stop: print(f"stop-by reached: {len(J) - n_} candidates untested", flush=True); break
        mi = idx[jb["model"]]; col = cc.col[mi]; model = models[mi]; L = str(cc.layer[mi])
        P = [p for p in jb["pairs"] if sa.fits(models, [p["high"]]) and sa.fits(models, [p["low"]])]
        if not P: print(f"{jb['id']}: no pairs", flush=True); continue
        bh = [chess.Board(p["high"]["fen"]) for p in P]; bl = [chess.Board(p["low"]["fen"]) for p in P]
        ph_, pl_ = [p["high"]["prompt"] for p in P], [p["low"]["prompt"] for p in P]
        lh, base_h, sh = gd.policy(model, bh, dev, ph_, grab=(L,), batch=a.batch)
        ll, base_l, sl = gd.policy(model, bl, dev, pl_, grab=(L,), batch=a.batch)
        hh, hl = sh[L].to(dev), sl[L].to(dev)
        u = sa.direction(cc, jb["lat"], jb["w"], jb["mu"], col, dev); u = u / u.norm()
        dirs = {"v": u}
        for r_i, rr in enumerate(jb["random"]):
            d = sa.direction(cc, rr["lat"], jb["w"], rr["mu"], col, dev); dirs[f"rand{r_i}"] = d / d.norm()
        rec = dict(id=jb["id"], model=jb["model"], pairs=[dict(pos=p["pos"], step=p["step"], gap=p["gap"], high=p["high"]["fen"], low=p["low"]["fen"],
                   high_moves=[m.uci() for m in lh[i]], low_moves=[m.uci() for m in ll[i]], high_lp=rd(base_h[i]), low_lp=rd(base_l[i]))
                   for i, p in enumerate(P)], towards={}, away={})
        n = len(P); keys = list(dirs)
        for s in range(0, len(keys), a.chunk):                          # towards: +d into low; away: -d into high
            ks = keys[s:s + a.chunk]
            for side, hs, boards, prompts, sign in (("towards", hl, bl, pl_, 1.0), ("away", hh, bh, ph_, -1.0)):
                repl = torch.cat([hs + sign * a.r * hs.norm(dim=1, keepdim=True) * dirs[k][None] for k in ks]).float().cpu()
                _, lp, _ = gd.policy(model, boards * len(ks), dev, prompts * len(ks), layer=L, repl=repl, batch=a.batch)
                for c_i, k in enumerate(ks): rec[side][k] = [rd(x) for x in lp[c_i * n:(c_i + 1) * n]]
        with out.open("a") as fh: fh.write(json.dumps(rec) + "\n")
        print(f"{n_ + 1}/{len(J)} {jb['id']}: {n} plies ({time.time() - t0:.0f}s)", flush=True)


# ------------------------------------------------------------------ report
def js(p, q):
    m = 0.5 * (p + q); f = lambda x, y: float(np.sum(x[x > 0] * np.log(x[x > 0] / y[x > 0])))
    return 0.5 * f(p, m) + 0.5 * f(q, m)


def measures(r):
    """-> {side: {direction: (JS gap closed, features projection)}}, plies used."""
    from steer_match import feats
    nrm = lambda q: q / max(q.sum(), 1e-12)
    out = {}; used = 0
    for side in ("towards", "away"):
        num = {k: 0.0 for k in r[side]}; den = 0.0; fp = {k: [] for k in r[side]}
        for i, p in enumerate(r["pairs"]):
            ph, pl = np.exp(np.array(p["high_lp"])), np.exp(np.array(p["low_lp"]))
            com = [m for m in p["low_moves"] if m in set(p["high_moves"])]
            Xh, Xl = feats(p["high"], p["high_moves"]), feats(p["low"], p["low_moves"])
            nat = ph @ Xh - pl @ Xl; nn = np.linalg.norm(nat)
            if len(com) >= 2:
                ih = [p["high_moves"].index(m) for m in com]; il = [p["low_moves"].index(m) for m in com]
                H, Lw = nrm(ph[ih]), nrm(pl[il]); j0 = js(Lw, H); den += j0
                for k in r[side]:
                    x = nrm(np.exp(np.array(r[side][k][i]))[il] if side == "towards" else np.exp(np.array(r[side][k][i]))[ih])
                    num[k] += j0 - (js(x, H) if side == "towards" else js(x, Lw))
                if side == "towards": used += 1
            if nn > 1e-9:
                for k in r[side]:
                    q = np.exp(np.array(r[side][k][i]))
                    fp[k].append(float((q @ Xl - pl @ Xl) @ nat / nn) if side == "towards" else float((q @ Xh - ph @ Xh) @ (-nat) / nn))
        out[side] = {k: (num[k] / den if den else float("nan"), float(np.mean(fp[k])) if fp[k] else float("nan")) for k in r[side]}
    return out, used


def report(a):
    from statistics import NormalDist
    nd = NormalDist()
    cj = json.loads((RES / f"{a.name}-candidates.json").read_text()); C = {c["id"]: c for c in cj["candidates"]}
    R = [json.loads(l) for l in (OV / a.name / "confirm.jsonl").read_text().splitlines()] if (OV / a.name / "confirm.jsonl").exists() else []
    def stat(vals, obs):
        rnd = np.array(vals, float); m_, sd = rnd.mean(), rnd.std(ddof=1) or 1e-12
        return dict(obs=obs, r95=float(np.percentile(rnd, 95)), rmed=float(np.median(rnd)), p=1 - nd.cdf((obs - m_) / sd))
    rows = []
    for r in R:
        M, used = measures(r); row = dict(id=r["id"], model=r["model"], plies=len(r["pairs"]), common=used, positions=len({p["pos"] for p in r["pairs"]}))
        for side in ("towards", "away"):
            rk = [k for k in M[side] if k.startswith("rand")]
            row[side] = stat([M[side][k][0] for k in rk], M[side]["v"][0]); row[side + "_feat"] = stat([M[side][k][1] for k in rk], M[side]["v"][1])
        row["p"] = max(row["towards"]["p"], row["away"]["p"]); rows.append(row)
    if rows:
        ps = np.array([r["p"] for r in rows]); n = len(ps); o = np.argsort(ps); q = np.empty(n)
        q[o] = np.minimum.accumulate((ps[o] * n / np.arange(1, n + 1))[::-1])[::-1]
        for r, qq in zip(rows, np.minimum(q, 1)):
            r["q"] = float(qq); r["pass"] = bool(r["towards"]["obs"] > r["towards"]["r95"] and r["away"]["obs"] > r["away"]["r95"] and qq < 0.05)
    roots = {sp: json.loads((OV / a.name / sp / "positions.json").read_text(encoding="utf-8")) for sp in ("disc", "conf")}
    cnt = cj["counts"]; f_ = lambda x, d=3: "–" if x is None or x != x else f"{x:+.{d}f}"
    md = [f"# Overnight mine and confirm ({a.name})", "",
          f"Rules fixed before any data: {a.name}-prereg.md. Candidates frozen {cj['frozen']}.", "",
          "## Positions", "",
          f"{len(roots['disc']) + len(roots['conf'])} positions sampled: {len(roots['disc'])} discovery, {len(roots['conf'])} confirmation "
          f"(256 rollouts of 16 plies at T = 0.4, S and W each; the first 8 positions at 512).", "",
          "## Concepts at each step", "", "| step | S | W |", "|---|---|---|"]
    for k, lab in (("mined", "mined (families with examples)"), ("replicate", "replicate across seeds"), ("positions", f"and seen at >= {a.min_positions} discovery positions"),
                   ("landed", "and the push lands (readback >= g)")):
        md.append(f"| {lab} | {cnt[k].get('S', 0)} | {cnt[k].get('W', 0)} |")
    md.append(f"| tested (plus S14 by default) | {sum(r['model'] == 'S' for r in rows)} | {sum(r['model'] == 'W' for r in rows)} |")
    md.append(f"| passed | {sum(r.get('pass', False) and r['model'] == 'S' for r in rows)} | {sum(r.get('pass', False) and r['model'] == 'W' for r in rows)} |")
    untested = [c for c in C if c not in {r['id'] for r in rows}]
    md += ["", f"Untested (time): {', '.join(untested) if untested else 'none'}.", "",
           "## Each candidate", "",
           "Towards: +v into the concept-low state; away: -v into the concept-high state. JS: share of the Jensen-Shannon gap closed on "
           "the moves legal in both states (main measure). Features: the move-features projection. Random: 50 directions of the same "
           "size and matching firing rates. q: Benjamini-Hochberg over the candidates tested, on the larger of the two JS p's.", "",
           "| candidate | model | theme | discovery positions | plies (confirmation positions) | JS towards (random 95th) | JS away (random 95th) "
           "| features towards (random 95th) | features away (random 95th) | q | verdict |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: r["q"]):
        c = C[r["id"]]
        md.append(f"| {r['id']} | {r['model']} | {c.get('theme') or ''} | {c['positions']} | {r['plies']} ({r['positions']}) | "
                  f"{f_(r['towards']['obs'])} ({f_(r['towards']['r95'])}) | {f_(r['away']['obs'])} ({f_(r['away']['r95'])}) | "
                  f"{f_(r['towards_feat']['obs'])} ({f_(r['towards_feat']['r95'])}) | {f_(r['away_feat']['obs'])} ({f_(r['away_feat']['r95'])}) | "
                  f"{r['q']:.3f} | {'passes' if r['pass'] else 'fails'} |")
    for r in [r for r in rows if r.get("pass")]:
        c = C[r["id"]]; ex, seen = [], set()
        for x in c.get("activating", []):
            if x["pos"] in seen: continue
            seen.add(x["pos"]); ex.append(x)
            if len(ex) == 3: break
        md += ["", f"### {r['id']} passes", "", f"Latents (weight): {', '.join(f'{l} ({w:.2f})' for l, w in zip(c['lat'], c['w']))}. "
               f"Discovery positions {c['positions']}, branch pairs {c['members']}; confirmation plies {r['plies']} at {r['positions']} positions.", ""]
        for x in ex:
            t = x["t"]; line = x["line"]
            md.append(f"- position {x['pos']} ({x.get('band', '')}): " + " ".join(f"**{m}**" if t <= i + 1 <= t + x["k"] else m for i, m in enumerate(line)))
    RES.mkdir(parents=True, exist_ok=True)
    (RES / f"{a.name}-report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (RES / f"{a.name}-report.json").write_text(json.dumps(rows))
    print(f"wrote {RES / (a.name + '-report.md')}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["choose", "prep", "run", "report"])
    ap.add_argument("--name", default="night1")
    ap.add_argument("--prefix", default="ov1")
    ap.add_argument("--cc-run", default="runs/transcend/crosscoder/mixed-L11")
    ap.add_argument("--cc", default="L11-4096")
    ap.add_argument("--strong", default="2400")
    ap.add_argument("--min-positions", type=int, default=20)
    ap.add_argument("--readback-points", type=int, default=16)
    ap.add_argument("--node", type=int, default=30)
    ap.add_argument("--wc", type=float, default=0.75)
    ap.add_argument("--min-share", type=float, default=0.02)
    ap.add_argument("--min-gap", type=float, default=0.5)
    ap.add_argument("--max-pairs", type=int, default=100)
    ap.add_argument("--n-random", type=int, default=50)
    ap.add_argument("--r", type=float, default=0.25)
    ap.add_argument("--chunk", type=int, default=6)
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--stop-by", default="2026-10-30T06:35")
    ap.add_argument("--device", default="auto")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    dict(choose=choose, prep=prep, run=run, report=report)[a.command](a)


if __name__ == "__main__":
    main()
