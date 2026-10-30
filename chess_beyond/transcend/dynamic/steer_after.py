"""steer_concepts.py's pilot, diagnosed and rerun: strength by the activation's norm, injected after the split.

diag   (GPU) the pilot as it ran: per concept, target model and alpha, at its points (steer-jobs.json), the readback
       (the concept's activity v . z through the crosscoder after adding alpha g u, intended alpha g) and the size of the
       push against the L11 state, ||alpha g u|| / ||h|| (median and range over points; beside it the random v's).
prep   (CPU) new points: every branch pair of the concept (its family's members), along the chosen line at the plies of
       its window t..t+k where the concept is on (its cached expression w . z > --min-on): the state after the split
       move and its follow-ups; target the chosen line's next move. Plus its activating windows away from its branch
       points (held out), the same way. One point per (position, prompt).
run    (GPU) at each point, h -> h + r ||h|| u_hat for r in --strengths (0.1, 0.25, 0.5: the push is that share of the
       state's norm), u_hat the unit direction of +v, -v, or a random v (matching firing rates, the same weights), so every
       condition pushes equally hard. The next move's log-probability and KL over all moves, in both models; the
       readback of +v at each r.
summary (CPU) steer_concepts.py's decision rule, unchanged, at --primary (r = 0.25) for the self-check, any r for
       transfer (Bonferroni over the strengths): self-check passes when +v raises the target more than every random v,
       -v lowers it, and Benjamini-Hochberg q < --fdr over concepts (p from the rise's z against the random v's).

    python transcend/dynamic/steer_after.py diag --only S141,S8,W29,S14,W25,S29,W138,W30,S58,W197 --device cuda
    python transcend/dynamic/steer_after.py prep --only S141,S8,W29,S14,W25,S29,W138,W30,S58,W197
    python transcend/dynamic/steer_after.py run --device cuda
    python transcend/dynamic/steer_after.py summary
-> results/transcend/divergence/<tag>/mine/steer-diag.md, steer-after.md (.json)"""
import argparse, json, sys, time
from pathlib import Path
from collections import Counter
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # chess_beyond/
import paths  # noqa: E402  also puts transcend/'s folders on sys.path
import steer_concepts as sc
from concept_mine import load_pos, mu_of, PL

RUNS, RESULTS, ROOT = sc.RUNS, sc.RESULTS, sc.ROOT


def setup(a):
    import eval as ev
    import shared as gd
    dev = ev.device(a.device)
    cc = gd.load_cc(ROOT / a.cc_run, a.cc, a.strong, dev)
    models = {m: ev.load(cc.info["models"][m], dev)[0] for m in (0, 1)}
    return dev, gd, cc, models, {"S": cc.s, "W": cc.w}


def direction(cc, lat, w, mu, col, dev):
    import torch
    Wd = cc.coder.W_dec.detach().float()
    d = (torch.tensor(w, device=dev)[:, None] * torch.tensor(mu, device=dev)[:, None] * Wd[lat, col]).sum(0)
    return d / cc.scales[col]


def states(gd, cc, models, mi, mo, pts, a, dev):
    """Target model mi's boards, legal moves, base log-probabilities and L11 states at the points; the other model's states."""
    import chess
    boards = [chess.Board(p["fen"]) for p in pts]; prompts = [p["prompt"] for p in pts]
    legal, base, st = gd.policy(models[mi], boards, dev, prompts, grab=(str(cc.layer[mi]),), batch=a.batch)
    _, _, st2 = gd.policy(models[mo], boards, dev, prompts, grab=(str(cc.layer[mo]),), batch=a.batch)
    return boards, prompts, legal, base, st[str(cc.layer[mi])].to(dev), st2[str(cc.layer[mo])].to(dev)


def readback(gd, cc, mi, mo, h, oh, push, jb, dev):
    """Rise in the concept's activity sum_j w_j z_j / mu_j per point after h -> h + push."""
    import torch
    with torch.no_grad():
        f0, _ = gd.encode_states(cc, {mi: h, mo: oh}); f1, _ = gd.encode_states(cc, {mi: h + push, mo: oh})
        wv = torch.tensor(jb["w"], device=dev) / torch.tensor(jb["mu"], device=dev)
        return ((f1[:, jb["lat"]] - f0[:, jb["lat"]]).float() * wv).sum(1).cpu().numpy()


def fits(models, pts):
    from pgn_model import MAX_MOVE_CHARS, encode
    ctx = min(m.ctx for m in models.values())
    return [p for p in pts if len(encode(p["prompt"])) + MAX_MOVE_CHARS + 1 <= ctx]


def jobs(a, name="steer-jobs.json"):
    J = json.loads((sc.mine_dir(a) / name).read_text())["jobs"]
    return [j for j in J if not a.only or j["id"] in a.only.split(",")]


q3 = lambda x: f"{np.median(x):.3f} [{np.min(x):.3f}, {np.max(x):.3f}]"


# ------------------------------------------------------------------ diag (GPU)
def diag(a):
    dev, gd, cc, models, idx = setup(a)
    alphas = [float(x) for x in a.alphas.split(",")]
    md = ["# Steering pilot: readback and push size", "",
          "The pilot as it ran (steer_concepts.py run: h -> h + alpha g u at the prompt end before the split). Readback: the "
          "concept's activity through the crosscoder after the push, against the intended alpha g (median over points). Push: "
          "||alpha g u|| / ||h|| at L11, median [min, max] over points; random: the same for the random v's (median over v's of "
          "their medians).", "",
          "| concept | g | into | ||h|| median | alpha | intended | readback rise | push / ||h|| | random push / ||h|| |",
          "|---|---|---|---|---|---|---|---|---|"]
    rows = []
    for jb in jobs(a):
        for tm in (jb["model"], jb["other"]):
            mi = idx[tm]; mo = 1 - mi; col = cc.col[mi]
            pts = fits(models, jb["points"])
            if not pts: continue
            *_, h, oh = states(gd, cc, models, mi, mo, pts, a, dev)
            u = direction(cc, jb["lat"], jb["w"], jb["mu"], col, dev); hn = h.norm(dim=1).cpu().numpy()
            ru = [direction(cc, r["lat"], jb["w"], r["mu"], col, dev).norm().item() for r in jb["random"][:a.n_random]]
            for al in alphas:
                rise = readback(gd, cc, mi, mo, h, oh, (al * jb["gap"] * u)[None], jb, dev)
                pr = al * jb["gap"] * u.norm().item() / hn
                rp = float(np.median([np.median(al * jb["gap"] * x / hn) for x in ru]))
                rows.append(dict(id=jb["id"], into=tm, gap=jb["gap"], alpha=al, intended=al * jb["gap"], rise=float(np.median(rise)),
                                 push=pr.tolist(), random_push=rp, h_norm=float(np.median(hn))))
                print(f"  readback {jb['id']} into {tm} @alpha {al}: rise {np.median(rise):+.2f} (intended {al * jb['gap']:+.2f}); "
                      f"push/||h|| {np.median(pr):.3f} (random {rp:.3f})", flush=True)
                md.append(f"| {jb['id']} | {jb['gap']:.2f} | {tm} | {np.median(hn):.1f} | {al} | {al * jb['gap']:+.2f} | {np.median(rise):+.2f} | "
                          f"{q3(pr)} | {rp:.3f} |")
    od = RESULTS / a.tag / "mine"; od.mkdir(parents=True, exist_ok=True)
    (od / "steer-diag.md").write_text("\n".join(md) + "\n", encoding="utf-8"); (od / "steer-diag.json").write_text(json.dumps(rows))
    print(f"wrote {od / 'steer-diag.md'}")


# ------------------------------------------------------------------ prep (CPU)
def prep(a):
    roots = json.loads((Path(a.source) / "positions.json").read_text(encoding="utf-8"))
    md = sc.mine_dir(a)
    F = {m: json.loads((md / f"examples-{m}.json").read_text()) for m in "SW"}
    R0 = {m: {f'{r["pos"]}/{r["t"]}/{r["c"]}/{r["s"]}/{r["k"]}': r for r in json.loads((md / f"lp-{m}-s0.json").read_text())} for m in "SW"}
    cache = {}
    def codes(m, p):
        if (m, p) not in cache:
            run = RUNS / a.tag / m; cache[(m, p)] = load_pos(run, p, mu_of(run))
        return cache[(m, p)]
    out = []
    for jb in jobs(a):
        m = jb["model"]; f = F[m][int(jb["id"][1:])]; w = np.array(jb["w"]); pts, seen, bpos = [], set(), set()
        for key in f["members"]:
            r = R0[m][key]; D, Z = codes(m, r["pos"]); sans = D[r["c"]]["sans"]; bpos.add(r["pos"])
            for d in range(r["k"] + 1):
                row = r["t"] + d
                if row >= len(sans): break
                e = float(Z[r["c"] * (PL + 1) + row, jb["lat"]].toarray().ravel() @ w)
                if e <= a.min_on: continue
                p_, fen = sc.prompt_at(roots[r["pos"]], sans, row)
                if (r["pos"], p_) in seen: continue
                seen.add((r["pos"], p_))
                pts.append(dict(kind="own", pos=r["pos"], step=d, prompt=p_, fen=fen, target=sans[row], alt=None, expr=round(e, 3)))
        for x in f.get("activating", []):
            if any(k_.startswith(f'{x["pos"]}/{x["t"]}/') for k_ in f["members"]): continue
            sans = [sc.strip(s) for s in x["line"]]
            for d in range(x["k"] + 1):
                row = x["t"] + d
                if row >= len(sans): break
                p_, fen = sc.prompt_at(roots[x["pos"]], sans, row)
                if (x["pos"], p_) in seen: continue
                seen.add((x["pos"], p_))
                pts.append(dict(kind="heldout", pos=x["pos"], step=d, prompt=p_, fen=fen, target=sans[row], alt=None, other_position=x["pos"] not in bpos))
        out.append(dict({k: v for k, v in jb.items() if k != "points"}, points=pts))
        c = Counter(p["kind"] for p in pts)
        print(f"{jb['id']}: {len(f['members'])} branch pairs -> {c['own']} own points ({len({p['pos'] for p in pts if p['kind'] == 'own'})} positions), "
              f"{c['heldout']} held out", flush=True)
    (md / "steer-after-jobs.json").write_text(json.dumps(dict(settings=vars(a), jobs=out)))
    print(f"prep: {len(out)} concepts, {sum(len(j['points']) for j in out)} points -> {md / 'steer-after-jobs.json'}")


# ------------------------------------------------------------------ run (GPU)
def run(a):
    import torch
    dev, gd, cc, models, idx = setup(a)
    J = jobs(a, "steer-after-jobs.json"); rs = [float(x) for x in a.strengths.split(",")]
    out = sc.mine_dir(a) / "steer-after.jsonl"
    done = {(r["id"], r["target_model"]) for r in map(json.loads, out.read_text().splitlines())} if out.exists() else set()
    fh = out.open("a"); t0 = time.time()
    print(f"run: {len(J)} concepts, {sum(len(j['points']) for j in J)} points, strengths {rs}, {a.n_random} random v's, on {dev}", flush=True)
    for n_, jb in enumerate(J):
        for tm in (jb["model"], jb["other"]):
            if (jb["id"], tm) in done: continue
            mi = idx[tm]; mo = 1 - mi; col = cc.col[mi]
            pts = fits(models, jb["points"])
            if not pts: continue
            boards, prompts, legal, base, h, oh = states(gd, cc, models, mi, mo, pts, a, dev)
            u = direction(cc, jb["lat"], jb["w"], jb["mu"], col, dev); u = u / u.norm()
            conds = {"+v": u, "-v": -u}
            for r_i, rd in enumerate(jb["random"][:a.n_random]):
                d = direction(cc, rd["lat"], jb["w"], rd["mu"], col, dev); conds[f"rand{r_i}"] = d / d.norm()
            hn = h.norm(dim=1, keepdim=True)
            rb = {r: readback(gd, cc, mi, mo, h, oh, r * hn * u[None], jb, dev) for r in rs}
            def find(i, san):
                try: mv = boards[i].parse_san(san)
                except Exception: return None
                return legal[i].index(mv) if mv in legal[i] else None
            ti = [find(i, p["target"]) for i, p in enumerate(pts)]
            rec = dict(id=jb["id"], model=jb["model"], target_model=tm, tier=jb["tier"], theme=jb["theme"], shared=jb["shared"], gap=jb["gap"],
                       points=[{k: p.get(k) for k in ("kind", "pos", "step", "target", "expr", "other_position")} for p in pts],
                       h_norm=hn[:, 0].cpu().tolist(), readback={str(r): v.tolist() for r, v in rb.items()},
                       base_t=[None if t_ is None else float(base[i][t_]) for i, t_ in enumerate(ti)], runs={})
            combos = [(cn, r) for cn in conds for r in rs]; n = len(pts)
            for s in range(0, len(combos), a.chunk):                       # a few conditions per call, to bound memory
                cs = combos[s:s + a.chunk]
                repl = torch.cat([h + r * hn * conds[cn][None] for cn, r in cs]).float().cpu()
                _, lp, _ = gd.policy(models[mi], boards * len(cs), dev, prompts * len(cs), layer=str(cc.layer[mi]), repl=repl, batch=a.batch)
                for c_i, (cn, r) in enumerate(cs):
                    L_ = lp[c_i * n:(c_i + 1) * n]
                    rec["runs"][f"{cn}@{r}"] = dict(t=[None if t_ is None else float(L_[i][t_]) for i, t_ in enumerate(ti)],
                                                    kl=[float(np.sum(np.exp(base[i]) * (base[i] - L_[i]))) for i in range(n)])
            fh.write(json.dumps(rec) + "\n"); fh.flush()
            print(f"  {jb['id']} into {tm}: {n} points; readback of +v at r = {rs}: "
                  + ", ".join(f"{np.median(rb[r]):+.2f}" for r in rs) + f" (natural gap g {jb['gap']:.2f})", flush=True)
        print(f"{n_ + 1}/{len(J)} {jb['id']} ({time.time() - t0:.0f}s)", flush=True)


# ------------------------------------------------------------------ summary (CPU)
def summary(a):
    from statistics import NormalDist
    nd = NormalDist(); rs = [float(x) for x in a.strengths.split(",")]
    R = [json.loads(l) for l in (sc.mine_dir(a) / "steer-after.jsonl").read_text().splitlines()]
    if a.only: R = [r for r in R if r["id"] in a.only.split(",")]
    def delta(r, cond, s, kind="own", field="t", step=None):
        key = f"{cond}@{s}"
        if key not in r["runs"]: return None
        o = []
        for i, p in enumerate(r["points"]):
            if (kind and p["kind"] != kind) or (step is not None and p["step"] != step): continue
            if field == "kl": o.append(r["runs"][key]["kl"][i]); continue
            b, x = r["base_t"][i], r["runs"][key]["t"][i]
            if b is not None and x is not None: o.append(x - b)
        return float(np.mean(o)) if o else None
    def test(r, s, kind="own"):
        obs, neg = delta(r, "+v", s, kind), delta(r, "-v", s, kind)
        rnd = [x for k in range(a.n_random) if (x := delta(r, f"rand{k}", s, kind)) is not None]
        if obs is None or len(rnd) < 3: return None
        m_, sd = float(np.mean(rnd)), float(np.std(rnd, ddof=1)) or 1e-6
        return dict(obs=obs, neg=neg, rmax=max(rnd), r95=float(np.percentile(rnd, 95)), rmed=float(np.median(rnd)), p=1 - nd.cdf((obs - m_) / sd))
    rows = {}
    for r in R:
        row = rows.setdefault(r["id"], dict(id=r["id"], model=r["model"], tier=r["tier"], theme=r["theme"], shared=r["shared"]))
        own = r["target_model"] == r["model"]
        row["points"] = sum(p["kind"] == "own" for p in r["points"]); row["positions"] = len({p["pos"] for p in r["points"] if p["kind"] == "own"})
        row["heldout_points"] = sum(p["kind"] == "heldout" for p in r["points"])
        dose = [delta(r, "+v", s) for s in rs]; kls = {c: delta(r, c, a.primary, field="kl") for c in ("+v", "-v", "rand0")}
        rb = [float(np.median(r["readback"][str(s)])) for s in rs]
        if own:
            steps = sorted({p["step"] for p in r["points"] if p["kind"] == "own"})
            row.update(self=test(r, a.primary), self_dose=dose, self_neg_dose=[delta(r, "-v", s) for s in rs], self_kl=kls, self_readback=rb,
                       self_heldout=test(r, a.primary, "heldout"), self_steps={d: delta(r, "+v", a.primary, step=d) for d in steps})
        else:
            ts = {s: v for s in rs if (v := test(r, s))}
            best = min(ts.items(), key=lambda kv: kv[1]["p"]) if ts else None
            row.update(other=r["target_model"], xfer=best[1] if best else None, xfer_r=best[0] if best else None,
                       xfer_p=min(1, best[1]["p"] * len(ts)) if best else None, xfer_dose=dose, xfer_kl=kls, xfer_readback=rb,
                       xfer_heldout=test(r, a.primary, "heldout"))
    rows = list(rows.values())
    sp = [r for r in rows if r.get("self")]; q = sc.bh([r["self"]["p"] for r in sp])
    for r, qq in zip(sp, q): r["self_q"] = float(qq); r["self_pass"] = bool(r["self"]["obs"] > r["self"]["rmax"] and (r["self"]["neg"] or 0) < 0 and qq < a.fdr)
    xp = [r for r in rows if r.get("xfer")]; q = sc.bh([r["xfer_p"] for r in xp])
    for r, qq in zip(xp, q): r["xfer_q"] = float(qq); r["transfers"] = bool(r["xfer"]["obs"] > r["xfer"]["r95"] and qq < a.fdr)
    ctrl = [r for r in rows if r.get("self_pass") and r["shared"] >= a.shared_control and "transfers" in r]
    rate = float(np.mean([r["transfers"] for r in ctrl])) if ctrl else float("nan")
    for r in rows:
        if r.get("self_pass") and "transfers" in r and not r["transfers"]:
            r["verdict"] = "fails to transfer" if rate >= a.control_rate and r["shared"] < a.shared_control else ("untested (control weak)" if rate < a.control_rate else "shared but no transfer")
        elif r.get("self_pass") and r.get("transfers"): r["verdict"] = "transfers"
        elif "self_pass" in r: r["verdict"] = "fails self-check"
        else: r["verdict"] = "incomplete"
    f_ = lambda x: "–" if x is None else f"{x:+.2f}"
    g_ = lambda x: "–" if x is None else f"{x:.2f}"
    md = ["# Steering mined concepts after the split, strength by norm", "",
          f"h -> h + r ||h|| u_hat at the prompt end, r = {', '.join(map(str, rs))}; every condition (+v, -v, {a.n_random} random v's of matching "
          f"firing rate) pushes equally hard. Points: the chosen line at the plies of each branch pair's window where the concept is on; "
          f"target the line's next move. Decision rule as steer_concepts.py: self-check at r = {a.primary} (+v above every random v, -v below "
          f"zero, Benjamini-Hochberg q < {a.fdr}); transfer at any r (Bonferroni over {len(rs)}), above the random 95th.", "",
          f"Self-check passes: {sum(r.get('self_pass', False) for r in rows)} of {len(sp)}. Positive control (shared, cos >= {a.shared_control}, "
          f"self-check passed): {sum(r['transfers'] for r in ctrl)} of {len(ctrl)} transfer ({rate:.0%}; the rule needs >= {a.control_rate:.0%}).", "",
          "Verdicts: " + ", ".join(f"{k} {v}" for k, v in Counter(r["verdict"] for r in rows).most_common()), "",
          f"| concept | theme | shared cos | points (positions) | verdict | self +v / -v / random median / max (q), r = {a.primary} | +v over r | -v over r | "
          f"readback of +v over r (g) | KL +v / -v / random | transfer: other +v / random 95th @r (q) | held-out points: +v self / other |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    order = {"transfers": 0, "fails to transfer": 1, "shared but no transfer": 2, "untested (control weak)": 3, "fails self-check": 4, "incomplete": 5}
    gap = {r["id"]: r["gap"] for r in R}
    for r in sorted(rows, key=lambda r: (order.get(r["verdict"], 9), -r["shared"])):
        s_, x_, kl = r.get("self") or {}, r.get("xfer") or {}, r.get("self_kl") or {}
        md.append(f"| {r['id']} | {r['theme'] or ''} | {r['shared']} | {r['points']} ({r['positions']}) | {r['verdict']} | "
                  f"{f_(s_.get('obs'))} / {f_(s_.get('neg'))} / {f_(s_.get('rmed'))} / {f_(s_.get('rmax'))} ({g_(r.get('self_q'))}) | "
                  f"{' '.join(f_(x) for x in r.get('self_dose') or [])} | {' '.join(f_(x) for x in r.get('self_neg_dose') or [])} | "
                  f"{' '.join(f_(x) for x in r.get('self_readback') or [])} ({gap[r['id']]:.2f}) | "
                  f"{g_(kl.get('+v'))} / {g_(kl.get('-v'))} / {g_(kl.get('rand0'))} | "
                  f"{r.get('other', '')} {f_(x_.get('obs'))} / {f_(x_.get('r95'))} @{r.get('xfer_r', '–')} ({g_(r.get('xfer_q'))}) | "
                  f"{r['heldout_points']}: {f_((r.get('self_heldout') or {}).get('obs'))} / {f_((r.get('xfer_heldout') or {}).get('obs'))} |")
    md += ["", f"By ply of the window (own model, +v at r = {a.primary}; step 0 = the state after the split move):", "",
           "| concept | " + " | ".join(f"step {d}" for d in range(9)) + " |", "|---|" + "---|" * 9]
    for r in rows:
        st = r.get("self_steps") or {}
        md.append(f"| {r['id']} | " + " | ".join(f_(st.get(d)) for d in range(9)) + " |")
    md += ["", "Readback: the concept's activity (sum_j w_j z_j / mu_j) after the push, median over points, beside its natural "
           "chosen-minus-subpar gap g. KL over all legal moves at the primary strength.", ""]
    od = RESULTS / a.tag / "mine"; od.mkdir(parents=True, exist_ok=True)
    (od / "steer-after.md").write_text("\n".join(md) + "\n", encoding="utf-8"); (od / "steer-after.json").write_text(json.dumps(rows, default=str))
    print(f"wrote {od / 'steer-after.md'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["diag", "prep", "run", "summary"])
    ap.add_argument("--tag", default="p16-r1024-T0.4-s0-L11-4k")
    ap.add_argument("--source", default=str(ROOT / "runs/transcend/manypositions/p16-r1024-T0.4-s0"))
    ap.add_argument("--cc-run", default="runs/transcend/crosscoder/mixed-L11")
    ap.add_argument("--cc", default="L11-4096")
    ap.add_argument("--strong", default="2400")
    ap.add_argument("--only", default="", help="concept ids, comma-separated (prep picks them; run and summary then use what prep wrote)")
    ap.add_argument("--alphas", default="0.5,1,2,4", help="diag: the pilot's strengths")
    ap.add_argument("--strengths", default="0.1,0.25,0.5", help="push as a share of ||h||")
    ap.add_argument("--primary", type=float, default=0.25, help="the strength the self-check is decided at")
    ap.add_argument("--min-on", type=float, default=0.0, help="prep: a window ply counts when the concept's expression is above this")
    ap.add_argument("--n-random", type=int, default=20)
    ap.add_argument("--chunk", type=int, default=6, help="run: conditions x strengths per policy call")
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--shared-control", type=float, default=0.7)
    ap.add_argument("--control-rate", type=float, default=0.7)
    ap.add_argument("--fdr", type=float, default=0.05)
    ap.add_argument("--device", default="auto")
    a = ap.parse_args()
    {"diag": diag, "prep": prep, "run": run, "summary": summary}[a.command](a)


if __name__ == "__main__":
    main()
