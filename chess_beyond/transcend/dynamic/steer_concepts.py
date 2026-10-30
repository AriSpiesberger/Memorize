"""Do mined concepts move the models? Inject a concept's direction into a model's layer-11 state and read off its moves.

A concept (concept_mine.py) is a unit vector v over crosscoder latents, in units of each latent's mean firing mu_j. Its
direction in model m's residual stream is  u_m = sum_j v_j mu_j W_dec[j, m] / scale_m  (the crosscoder's decoder for
that model, the input scaling undone). Adding c u_m raises the concept's activity v . z by c, so strengths are in the
concept's own units:  alpha = 1 adds its typical gap between chosen and subpar lines at its branch points (g, the mean of
v . (z_chosen - z_subpar) at the split ply); alpha = 2 twice that.

Where: only at the hook, the prompt's last character, after the crosscoder's layer: the state the crosscoder was trained
on, where the model is about to write its move. The move's characters are then scored with the steered state in the
cache (shared.policy with layer/repl), so a move's log-probability is the sum over its characters, over the legal moves.

Points (prep, from concept_mine.py's examples):
  own       the concept's branch points: before the split move; target the chosen move, alternative the subpar one.
            Then follow-ups along the chosen line inside the window: target that line's next move.
  heldout   its activating windows away from its branch points (another position where possible): before the move
            after which it switches on; target that move. The test of a general idea, not a memorised move.
Conditions: +v, -v (should push the other way), and two random v's on latents of matching firing rate (same weights).
Targets: the concept's own model (the self-check) and the other model. Order of reading (summary):
  1. self-check: +v raises the target in its own model, -v lowers it, random does neither.
  2. positive control: concepts shared by cosine (a match >= --shared in the other model), injected cross-model.
  3. only then the model-only concepts cross-model; a failure there means something once step 2 succeeds.
Each concept also carries its latents' decoder norm share in the target model (from the crosscoder): near zero means
that model has no representation of those latents, a different finding from "represented but unused".
Note: the codes are the joint crosscoder's (both models read every line), so "S's concepts" and "W's concepts" differ in
which lines each model plays; whether a concept is shared is what this test decides.

  python transcend/dynamic/steer_concepts.py prep        # CPU: runs/.../<tag>/mine/steer-jobs.json
  python transcend/dynamic/steer_concepts.py run --only S141,S8,W29,S14,W25,S29,W138,W30,S58,W197     # the pilot first
  python transcend/dynamic/steer_concepts.py summary --only S141,S8,W29,S14,W25,S29,W138,W30,S58,W197
  python transcend/dynamic/steer_concepts.py run         # GPU (or CPU, slowly): steer-results.jsonl
  python transcend/dynamic/steer_concepts.py summary     # results/.../<tag>/mine/steer.md, steer.json
  modal run --detach modal/modal_train.py::steer_concepts     # prep locally, upload, run on a GPU, download
"""
import argparse, json, sys, time
from pathlib import Path
from collections import Counter
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))  # chess_beyond/
import paths  # noqa: E402  also puts transcend/'s folders on sys.path
RUNS = ROOT / "runs" / "transcend" / "divergence"
RESULTS = ROOT / "results" / "transcend" / "divergence"
PL = 16


def mine_dir(a): return RUNS / a.tag / "mine"


def strip(m): return m.split(".")[-1]


def advance(p, b, san):
    import chess
    mv = b.parse_san(san)
    p += san + (" " if b.turn == chess.WHITE else f" {b.fullmove_number + 1}.")
    b.push(mv)
    return p


def prompt_at(root, sans, n):
    """The prompt and board after the first n moves of a line from root (shared.positions' format)."""
    import chess
    b = chess.Board(root["fen"]); p = root["prompt"]
    for s in sans[:n]: p = advance(p, b, s)
    return p, b.fen()


# ------------------------------------------------------------------ prep (CPU)
def prep(a):
    from scipy import sparse
    roots = json.loads((Path(a.source) / "positions.json").read_text(encoding="utf-8"))
    md = mine_dir(a); jobs = []; rng = np.random.default_rng(a.seed)
    F = {m: json.loads((md / f"examples-{m}.json").read_text()) for m in "SW"}
    rep = RESULTS / a.tag / "mine" / "concepts.json"
    themes = {c["id"]: (c.get("theme") or {}).get("name") for m in "SW" for c in json.loads(rep.read_text())[m]["concepts"]} if rep.exists() else {}
    for m in "SW":
        for i, f in enumerate(F[m]): f["id"] = f"{m}{i}"; f["theme"] = themes.get(f["id"])
    def vec(f):
        x = np.zeros(4096)
        for j, w in f["centroid"].items(): x[int(j)] = w
        return x / np.linalg.norm(x)
    C = {m: np.array([vec(f) for f in F[m]]) for m in "SW"}
    cos = C["S"] @ C["W"].T
    for m, o in (("S", "W"), ("W", "S")):
        run = RUNS / a.tag / m; mu = np.array(json.loads((run / "mu.json").read_text())["mu"])
        R0 = {f'{r["pos"]}/{r["t"]}/{r["c"]}/{r["s"]}/{r["k"]}': r for r in json.loads((md / f"lp-{m}-s0.json").read_text())}
        cnt = np.zeros(4096); tot_rows = 0; cache = {}
        for p in range(len(roots)):
            z = np.load(run / f"pos-{p}.npz"); cnt += z["vcnt"]; tot_rows += int(z["shape"][0])
        rate = cnt / max(tot_rows, 1); act = np.flatnonzero(rate > 0)
        dec = np.searchsorted(np.quantile(rate[act], np.linspace(0, 1, 11)[1:-1]), rate)
        def load(p):
            if p not in cache:
                z = np.load(run / f"pos-{p}.npz"); D = json.loads(str(z["D"]))
                Z = sparse.csr_matrix((z["data"].astype(np.float32), z["indices"], z["indptr"]), shape=tuple(z["shape"]))
                Z.data = np.minimum(Z.data / np.maximum(mu[Z.indices], 1e-6), 3.0); cache[p] = (D, Z.tocsr())
            return cache[p]
        for i, f in enumerate(F[m]):
            sim = cos[i] if m == "S" else cos[:, i]; j = int(sim.argmax()); shared = float(sim[j])
            pick = f["tier"] == "best" or (f["tier"] in ("clean", "board") and shared >= a.shared_control) or f["id"] in a.extra.split(",")
            if not pick: continue
            v = vec(f); order = np.argsort(-v); keep = order[:max(1, int(np.searchsorted(np.cumsum(v[order] ** 2), 0.95)) + 1)]
            lat = [int(x) for x in keep]; w = v[keep] / np.linalg.norm(v[keep])
            gaps, points, bpos = [], [], set()
            for key in sorted(f["members"], key=lambda k_: -R0[k_]["node"]):
                r = R0[key]; D, Z = load(r["pos"]); t = r["t"]
                zc = Z[r["c"] * (PL + 1) + t, lat].toarray().ravel(); zs = Z[r["s"] * (PL + 1) + t, lat].toarray().ravel()
                gaps.append(float(w @ (zc - zs)))
                if r["pos"] in bpos or len(points) >= a.own_points * (1 + a.follow): continue
                bpos.add(r["pos"]); sc = D[r["c"]]["sans"]; root = roots[r["pos"]]
                p_, fen = prompt_at(root, sc, t - 1)
                points.append(dict(kind="own", pos=r["pos"], step=0, prompt=p_, fen=fen, target=r["chosen"], alt=r["subpar"]))
                for d in range(1, a.follow + 1):
                    if t - 1 + d >= len(sc) or d > r["k"]: break
                    p_, fen = prompt_at(root, sc, t - 1 + d)
                    points.append(dict(kind="own", pos=r["pos"], step=d, prompt=p_, fen=fen, target=sc[t - 1 + d], alt=None))
            held = [x for x in f.get("activating", []) if x["pos"] not in bpos] or \
                   [x for x in f.get("activating", []) if not any(k_.startswith(f'{x["pos"]}/{x["t"]}/') for k_ in f["members"])]
            for x in held[:a.heldout_points]:
                sans = [strip(s) for s in x["line"]]; root = roots[x["pos"]]; t = x["t"]
                p_, fen = prompt_at(root, sans, t - 1)
                points.append(dict(kind="heldout", pos=x["pos"], step=0, prompt=p_, fen=fen, target=sans[t - 1], alt=None, other_position=x["pos"] not in bpos))
                for d in range(1, a.follow + 1):
                    if t - 1 + d >= len(sans) or d > x["k"]: break
                    p_, fen = prompt_at(root, sans, t - 1 + d)
                    points.append(dict(kind="heldout", pos=x["pos"], step=d, prompt=p_, fen=fen, target=sans[t - 1 + d], alt=None, other_position=x["pos"] not in bpos))
            rand = []
            for _ in range(a.n_random):
                nl = []
                for l_ in lat:
                    opts = act[dec[act] == dec[l_]]; x_ = int(rng.choice(opts))
                    while x_ in nl or x_ in lat: x_ = int(rng.choice(opts))
                    nl.append(x_)
                rand.append(dict(lat=nl, mu=[float(mu[x_]) for x_ in nl]))
            jobs.append(dict(id=f["id"], model=m, other=o, tier=f["tier"], theme=f.get("theme"),
                             shared=round(shared, 3), match=f"{o}{j}", lat=lat, w=[float(x) for x in w], mu=[float(mu[x_]) for x_ in lat],
                             gap=float(np.median(gaps)) if gaps else 1.0, random=rand, points=points))
    out = md / "steer-jobs.json"; out.write_text(json.dumps(dict(settings=vars(a), jobs=jobs)))
    c = Counter((j_["model"], j_["tier"], j_["shared"] >= a.shared_control) for j_ in jobs)
    print(f"prep: {len(jobs)} concepts, {sum(len(j_['points']) for j_ in jobs)} points -> {out}")
    for k, v in sorted(c.items()): print(f"   {k[0]} {k[1]:5s} {'shared' if k[2] else 'model-only':10s} {v}")
    print(f"   gap g (median over concepts): {np.median([j_['gap'] for j_ in jobs]):.2f}")


# ------------------------------------------------------------------ run (GPU)
def run(a):
    import torch, chess
    import eval as ev
    import shared as gd
    from pgn_model import MAX_MOVE_CHARS, encode
    dev = ev.device(a.device)
    J = json.loads((mine_dir(a) / "steer-jobs.json").read_text())["jobs"]
    if a.only: J = [j_ for j_ in J if j_["id"] in a.only.split(",")]
    print(f"run: {len(J)} concepts on {dev}", flush=True)
    cc = gd.load_cc(ROOT / a.cc_run, a.cc, a.strong, dev)
    models = {m: ev.load(cc.info["models"][m], dev)[0] for m in (0, 1)}
    idx = {"S": cc.s, "W": cc.w}
    Wd = cc.coder.W_dec.detach().float()                         # (latents, sources, d)
    nm = cc.coder.norms().detach().float().cpu().numpy()          # (latents, sources)
    alphas = [float(x) for x in a.alphas.split(",")]
    out = mine_dir(a) / a.results
    done = set()
    if out.exists():
        for l in out.read_text().splitlines():
            r = json.loads(l); done.add((r["id"], r["target_model"]))
    fh = out.open("a")
    t0 = time.time()
    for n_, jb in enumerate(J):
        for tm in (jb["model"], jb["other"]):
            if (jb["id"], tm) in done: continue
            mi = idx[tm]; col = cc.col[mi]; model = models[mi]; layer = cc.layer[mi]
            def direction(lat, w, mu):
                d = (torch.tensor(w, device=dev)[:, None] * torch.tensor(mu, device=dev)[:, None] * Wd[lat, col]).sum(0)
                return d / cc.scales[col]
            conds = {"+v": direction(jb["lat"], jb["w"], jb["mu"])}
            conds["-v"] = -conds["+v"]
            for r_i, rd in enumerate(jb["random"][:a.n_random]): conds[f"rand{r_i}"] = direction(rd["lat"], jb["w"], rd["mu"])
            share = float((np.array(jb["w"]) ** 2 * nm[jb["lat"], col] / np.maximum(nm[jb["lat"]].sum(1), 1e-8)).sum())
            pts = [p for p in jb["points"] if len(encode(p["prompt"])) + MAX_MOVE_CHARS + 1 <= model.ctx]
            if not pts: continue
            boards = [chess.Board(p["fen"]) for p in pts]; prompts = [p["prompt"] for p in pts]
            legal, base, st = gd.policy(model, boards, dev, prompts, grab=(str(layer),), batch=a.batch)
            h = st[str(layer)].to(dev)
            if n_ < a.readback:     # read the steering back through the crosscoder: +v at alpha = 1 should raise v . z by about g
                mo = idx[jb["other"] if tm == jb["model"] else jb["model"]]
                _, _, st2 = gd.policy(models[mo], boards, dev, prompts, grab=(str(cc.layer[mo]),), batch=a.batch)
                with torch.no_grad():
                    other_h = st2[str(cc.layer[mo])].to(dev)
                    f0, _ = gd.encode_states(cc, {mi: h, mo: other_h})
                    f1, _ = gd.encode_states(cc, {mi: h + jb["gap"] * conds["+v"][None], mo: other_h})
                    wv = torch.tensor(jb["w"], device=dev) / torch.tensor(jb["mu"], device=dev)
                    rise = ((f1[:, jb["lat"]] - f0[:, jb["lat"]]).float() * wv).sum(1).mean().item()
                print(f"  readback {jb['id']} into {tm}: concept activity rose by {rise:+.2f} (intended {jb['gap']:+.2f})", flush=True)
            def find(i, san):
                if san is None: return None
                try: mv = boards[i].parse_san(san)
                except Exception: return None
                return legal[i].index(mv) if mv in legal[i] else None
            ti = [find(i, p["target"]) for i, p in enumerate(pts)]; ai = [find(i, p["alt"]) for i, p in enumerate(pts)]
            rec = dict(id=jb["id"], model=jb["model"], target_model=tm, tier=jb["tier"], theme=jb["theme"], shared=jb["shared"], gap=jb["gap"],
                       decoder_share=round(share, 3), points=[dict(kind=p["kind"], pos=p["pos"], step=p["step"], target=p["target"], alt=p["alt"],
                                                                   other_position=p.get("other_position")) for p in pts],
                       base_t=[None if t_ is None else float(base[i][t_]) for i, t_ in enumerate(ti)],
                       base_a=[None if t_ is None else float(base[i][t_]) for i, t_ in enumerate(ai)], runs={})
            combos = [(cn, al) for cn in conds for al in alphas if not cn.startswith("rand") or al <= 2]   # one batched call
            repl = torch.cat([h + al * jb["gap"] * conds[cn][None] for cn, al in combos]).float().cpu()
            _, lp, _ = gd.policy(model, boards * len(combos), dev, prompts * len(combos), layer=str(layer), repl=repl, batch=a.batch)
            n = len(pts)
            for c_i, (cn, al) in enumerate(combos):
                L_ = lp[c_i * n:(c_i + 1) * n]
                kl = [float(np.sum(np.exp(base[i]) * (base[i] - L_[i]))) for i in range(n)]      # KL(base || steered), all legal moves
                rec["runs"][f"{cn}@{al}"] = dict(t=[None if t_ is None else float(L_[i][t_]) for i, t_ in enumerate(ti)],
                                                a=[None if t_ is None else float(L_[i][t_]) for i, t_ in enumerate(ai)], kl=kl)
            fh.write(json.dumps(rec) + "\n"); fh.flush()
        print(f"{n_ + 1}/{len(J)} {jb['id']} ({time.time() - t0:.0f}s)", flush=True)
    fh.close()


# ------------------------------------------------------------------ summary
def summary(a):
    """The decision rule, fixed before the results (all at the concept's own points unless named):
      self-check passes   own model, alpha = 1, decision points (own branch points, step 0): the chosen move's
                          log-probability rises by more than every random v, and -v lowers it; p from the rise's z against
                          the random v's (normal approximation), Benjamini-Hochberg over concepts.
      transfers           other model, alpha <= 2: the rise beats the random v's 95th percentile at some alpha; p as above,
                          the smallest over the alphas x their number (Bonferroni), then Benjamini-Hochberg over concepts.
      fails to transfer   passes the self-check, does not transfer, and the shared concepts (positive control) transfer at
                          >= --control-rate under the same settings; otherwise 'untested' (the control did not work).
    Beside it: KL over all moves (disruption), where held-out points come from, and the dose response over alpha."""
    from statistics import NormalDist
    R = [json.loads(l) for l in (mine_dir(a) / a.results).read_text().splitlines()]
    alphas = [float(x) for x in a.alphas.split(",")]
    nd = NormalDist()
    def mean_delta(r, cond, al, kind="own", step=0, field="t"):
        out = []
        for i, p in enumerate(r["points"]):
            if (kind and p["kind"] != kind) or (step is not None and p["step"] != step): continue
            key = f"{cond}@{al}"
            if key not in r["runs"]: return None
            if field == "kl": out.append(r["runs"][key]["kl"][i]); continue
            b = r["base_t"][i]; x = r["runs"][key]["t"][i]
            if b is not None and x is not None: out.append(x - b)
        return float(np.mean(out)) if out else None
    def test(r, al, kind="own", step=0):
        obs = mean_delta(r, "+v", al, kind, step); neg = mean_delta(r, "-v", al, kind, step)
        rnd = [x for k in range(a.n_random) if (x := mean_delta(r, f"rand{k}", al, kind, step)) is not None]
        if obs is None or len(rnd) < 3: return None
        mu_, sd = float(np.mean(rnd)), float(np.std(rnd, ddof=1)) or 1e-6
        return dict(obs=obs, neg=neg, rmax=max(rnd), r95=float(np.percentile(rnd, 95)), p=1 - nd.cdf((obs - mu_) / sd))
    def bh(ps):
        ps = np.array(ps, float); n = len(ps); o = np.argsort(ps); q = np.empty(n)
        q[o] = np.minimum.accumulate((ps[o] * n / np.arange(1, n + 1))[::-1])[::-1]
        return np.minimum(q, 1)
    rows = {}
    for r in R:
        key = r["id"]; row = rows.setdefault(key, dict(id=r["id"], model=r["model"], tier=r["tier"], theme=r["theme"], shared=r["shared"]))
        own = r["target_model"] == r["model"]
        held = [p for p in r["points"] if p["kind"] == "heldout" and p["step"] == 0]
        row["heldout_points"] = len(held); row["heldout_other_positions"] = sum(bool(p.get("other_position")) for p in held)
        dose = [mean_delta(r, "+v", al) for al in alphas]
        kls = {c: mean_delta(r, c, 1.0, step=0, field="kl") for c in ("+v", "-v", "rand0")}
        if own:
            t = test(r, 1.0)
            row.update(self=t, self_dose=dose, self_kl=kls, self_heldout=test(r, 1.0, "heldout"))
        else:
            ts = {al: test(r, al) for al in alphas if al <= 2}
            ts = {k: v for k, v in ts.items() if v}
            best = min(ts.items(), key=lambda kv: kv[1]["p"]) if ts else None
            row.update(other=r["target_model"], decoder_share=r["decoder_share"], xfer=best[1] if best else None, xfer_alpha=best[0] if best else None,
                       xfer_p=min(1, best[1]["p"] * len(ts)) if best else None, xfer_dose=dose, xfer_kl=kls, xfer_heldout=test(r, 1.0, "heldout"))
    rows = list(rows.values())
    sp = [r for r in rows if r.get("self")]; q = bh([r["self"]["p"] for r in sp])
    for r, qq in zip(sp, q): r["self_q"] = float(qq); r["self_pass"] = bool(r["self"]["obs"] > r["self"]["rmax"] and (r["self"]["neg"] or 0) < 0 and qq < a.fdr)
    xp = [r for r in rows if r.get("xfer")]; q = bh([r["xfer_p"] for r in xp])
    for r, qq in zip(xp, q): r["xfer_q"] = float(qq); r["transfers"] = bool(r["xfer"]["obs"] > r["xfer"]["r95"] and qq < a.fdr)
    ctrl = [r for r in rows if r.get("self_pass") and r["shared"] >= a.shared_control and "transfers" in r]
    rate = float(np.mean([r["transfers"] for r in ctrl])) if ctrl else float("nan")
    for r in rows:
        if r.get("self_pass") and "transfers" in r and not r["transfers"]:
            r["verdict"] = "fails to transfer" if rate >= a.control_rate and r["shared"] < a.shared_control else ("untested (control weak)" if rate < a.control_rate else "shared but no transfer")
        elif r.get("self_pass") and r.get("transfers"): r["verdict"] = "transfers"
        elif "self_pass" in r: r["verdict"] = "fails self-check"
        else: r["verdict"] = "incomplete"
        d = r.get("self_dose") or []
        r["dose_smooth"] = bool(len(d) == len(alphas) and all(x is not None for x in d) and all(d[i] <= d[i + 1] + 0.02 for i in range(len(d) - 1)) and d[-1] > d[0])
    f_ = lambda x: "–" if x is None else f"{x:+.2f}"
    g_ = lambda x: "–" if x is None else f"{x:.2f}"
    md = ["# Steering mined concepts (pilot)" if a.only else "# Steering mined concepts", "",
          f"Strength alpha in units of each concept's own gap g. Decision rule fixed before the results (see steer_concepts.py summary): "
          f"Benjamini-Hochberg at q < {a.fdr} over concepts, {a.n_random} random v's per concept on latents of matching firing rate.", "",
          f"Self-check passes: {sum(r.get('self_pass', False) for r in rows)} of {len(sp)}. "
          f"Positive control (shared, cos >= {a.shared_control}, self-check passed): {sum(r['transfers'] for r in ctrl)} of {len(ctrl)} transfer "
          f"({rate:.0%}; the rule needs >= {a.control_rate:.0%} before a failure to transfer counts).", "",
          "Verdicts: " + ", ".join(f"{k} {v}" for k, v in Counter(r["verdict"] for r in rows).most_common()), "",
          "| concept | tier | theme | shared cos | verdict | self +v / -v / max random (q) | dose +v over alpha | KL +v / -v / random | transfer: other model +v / random 95th @alpha (q) | decoder share | held-out points (other positions) | held-out +v self / other |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    order = {"transfers": 0, "fails to transfer": 1, "shared but no transfer": 2, "untested (control weak)": 3, "fails self-check": 4, "incomplete": 5}
    for r in sorted(rows, key=lambda r: (order.get(r["verdict"], 9), -(r["shared"]))):
        s_ = r.get("self") or {}; x_ = r.get("xfer") or {}
        dose = " ".join(f_(x) for x in (r.get("self_dose") or [])) + (" (smooth)" if r["dose_smooth"] else "")
        kl = r.get("self_kl") or {}
        md.append(f"| {r['id']} | {r['tier']} | {r['theme'] or ''} | {r['shared']} | {r['verdict']} | {f_(s_.get('obs'))} / {f_(s_.get('neg'))} / {f_(s_.get('rmax'))} ({g_(r.get('self_q'))}) | "
                  f"{dose} | {g_(kl.get('+v'))} / {g_(kl.get('-v'))} / {g_(kl.get('rand0'))} | {r.get('other', '')} {f_(x_.get('obs'))} / {f_(x_.get('r95'))} @{r.get('xfer_alpha', '–')} ({g_(r.get('xfer_q'))}) | "
                  f"{r.get('decoder_share', '–')} | {r.get('heldout_points', 0)} ({r.get('heldout_other_positions', 0)}) | "
                  f"{f_((r.get('self_heldout') or {}).get('obs'))} / {f_((r.get('xfer_heldout') or {}).get('obs'))} |")
    md += ["", "Columns: self = the concept's own model at its branch points, alpha = 1. Dose: +v at alpha = " + ", ".join(map(str, alphas)) +
           ". KL: over all legal moves at alpha = 1, the disruption beside the gain; a large KL for -v and random as well means the effect is "
           "disruption, not the concept. Held-out points: windows where the concept switches on away from its branch points; the count in "
           "brackets is at other positions, the stronger test. Decoder share: the concept's latents' decoder norm in the other model; near "
           "zero means that model does not represent them.", ""]
    od = RESULTS / a.tag / "mine"; od.mkdir(parents=True, exist_ok=True)
    name = "steer-pilot" if a.only else "steer"
    (od / f"{name}.md").write_text("\n".join(md) + "\n", encoding="utf-8"); (od / f"{name}.json").write_text(json.dumps(rows, default=str))
    print(f"wrote {od / (name + '.md')}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["prep", "run", "summary"])
    ap.add_argument("--tag", default="p16-r1024-T0.4-s0-L11-4k")
    ap.add_argument("--source", default=str(ROOT / "runs/transcend/manypositions/p16-r1024-T0.4-s0"))
    ap.add_argument("--cc-run", default="runs/transcend/crosscoder/mixed-L11")
    ap.add_argument("--cc", default="L11-4096")
    ap.add_argument("--strong", default="2400")
    ap.add_argument("--shared-control", type=float, default=0.7, help="cosine to the other model's nearest concept that counts as shared")
    ap.add_argument("--extra", default="", help="more concept ids to include, comma-separated (e.g. W30,W38)")
    ap.add_argument("--own-points", type=int, default=4)
    ap.add_argument("--heldout-points", type=int, default=4)
    ap.add_argument("--follow", type=int, default=2, help="follow-up moves scored along the line inside the window")
    ap.add_argument("--alphas", default="0.5,1,2,4")
    ap.add_argument("--read-alpha", type=float, default=2.0)
    ap.add_argument("--min-effect", type=float, default=0.05)
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--n-random", type=int, default=20, help="random v's per concept (run at alpha <= 2)")
    ap.add_argument("--only", default="", help="run/summary: just these concept ids, comma-separated (the pilot)")
    ap.add_argument("--results", default="", help="results file name in mine/ (default steer-results.jsonl, or steer-pilot.jsonl with --only)")
    ap.add_argument("--fdr", type=float, default=0.05)
    ap.add_argument("--readback", type=int, default=10, help="run: for the first N concepts, check through the crosscoder that +v raises the concept's activity")
    ap.add_argument("--control-rate", type=float, default=0.7, help="shared concepts that must transfer before a failure to transfer counts")
    ap.add_argument("--device", default="auto")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    a.results = a.results or ("steer-pilot.jsonl" if a.only else "steer-results.jsonl")
    {"prep": prep, "run": run, "summary": summary}[a.command](a)


if __name__ == "__main__":
    main()
