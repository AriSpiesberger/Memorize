"""Each model's own reading of the shared latents, at the same positions: where S and W pick different moves, does
S's reading differ from W's more than where they agree?

    python transcend/readings.py --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal

1. positions  --positions held-out middlegame positions, one per game (seeded random order); S's and W's top moves
              (their policies' most likely move); a position disagrees when they differ, agrees when not.
2. readings   each model's own reading of every latent from the crosscoder encoder, before the shared nonlinearity:
              r^m = (x_m - b_dec_m) W_enc^m, its block of the pre-activation sum_m r^m + b_enc (x_m: the model's state
              at the position, scaled as the crosscoder was trained). Also the latents' activations f (after the shared
              ReLU and threshold), for which latents are active.
3. look       per latent, the mean of r^S - r^W over the disagree positions against the agree ones: the --show latents
              with the largest difference (and its t statistic), either way.
4. LP         Schut's soft-margin max-min LP on half the disagree positions (split by game), v >= 0, sum(v) <= 1,
              restricted to latents active (f > 0) at >= --min-active of those positions: S's side on d = r^S - r^W,
              W's side on -d. The constraint holds at a position when v.d reaches the fitted margin (the "v.d >= 1" of
              the LP scaled by its margin). Reported: how often it holds on the held-out disagree positions and on the
              agree positions. A real concept separates the readings more where the models disagree.

-> results/transcend/readings/<tag>/report.md, report.json; runs/transcend/readings/<tag>/readings.npz."""

import argparse
import json
import sys
import time
import zlib
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paths
import eval as ev
import graphdiff as gd
from pgn_model import MAX_MOVE_CHARS, prompt
from pgn_probe import parse_movetext

RUNS = paths.RUNS / "transcend" / "readings"
RESULTS = paths.ROOT / "results" / "transcend" / "readings"


def positions(a, ctx):
    rng = np.random.default_rng(a.seed)
    pop = [json.loads(l) for l in open(a.population, encoding="utf-8")]
    out, games = [], set()
    for i in rng.permutation(len(pop)):
        r = pop[i]
        if (r["band"], r["game"]) in games or len(r["prompt"]) + MAX_MOVE_CHARS + 1 > ctx:
            continue
        b = ev.board_of(parse_movetext(r["prompt"])[0])
        if prompt(b) != r["prompt"] or b.is_game_over() or not gd.middlegame(b):
            continue
        games.add((r["band"], r["game"]))
        out.append((r, b))
        if len(out) >= a.positions:
            break
    return out


def read(a):
    """Positions, top moves, and each model's readings -> dict (cached)."""
    run = RUNS / a.tag
    run.mkdir(parents=True, exist_ok=True)
    cache = run / "readings.npz"
    if cache.exists():
        z = np.load(cache, allow_pickle=True)
        return {k: z[k] for k in z.files}
    dev = ev.device(a.device)
    cc = gd.load_cc(a.cc_run, a.cc, a.strong, dev)
    models = {m: ev.load(cc.info["models"][m], dev)[0] for m in (0, 1)}
    t0 = time.time()
    P = positions(a, min(m.ctx for m in models.values()))
    boards, prompts = [b for _, b in P], [r["prompt"] for r, _ in P]
    top, st = {}, {}
    for m in (0, 1):
        legal, lp, states = gd.policy(models[m], boards, dev, prompts, grab=(cc.layer[m],), batch=a.batch)
        top[m] = [mv[int(np.argmax(l))].uci() for mv, l in zip(legal, lp)]
        st[m] = states[cc.layer[m]].float()
    print(f"{len(P)} positions, both policies ({time.time() - t0:.0f}s)", flush=True)
    with torch.no_grad():
        x = torch.stack([st[m].to(dev) for m, _ in cc.sources], 1) * cc.scales[None, :, None]
        d = x.shape[-1]
        W, bd = cc.coder.W_enc, cc.coder.b_dec
        r = {m: ((x[:, i] - bd[i]) @ W[i * d:(i + 1) * d]).cpu().numpy() for i, (m, _) in enumerate(cc.sources)}
        f = cc.coder.encode(x)[0].cpu().numpy()
    out = dict(rS=r[cc.s].astype(np.float32), rW=r[cc.w].astype(np.float32), f=f.astype(np.float32),
               topS=np.array(top[cc.s]), topW=np.array(top[cc.w]), fen=np.array([b.fen() for b in boards]),
               band=np.array([r_["band"] for r_, _ in P]), game=np.array([str(r_["game"]) for r_, _ in P]))
    np.savez_compressed(cache, **out)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cc-run", default="runs/transcend/crosscoder/everything-3m")
    ap.add_argument("--cc", default="Lfinal")
    ap.add_argument("--strong", default="2400")
    ap.add_argument("--population", default=str(gd.PROBE / "population.jsonl"))
    ap.add_argument("--positions", type=int, default=1000)
    ap.add_argument("--show", type=int, default=20)
    ap.add_argument("--nu", type=float, default=0.2, help="soft margin: the share of fit positions allowed inside it")
    ap.add_argument("--min-active", type=float, default=0.05, help="LP latents: active at >= this share of the fit positions")
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    from scipy import sparse
    a.tag = a.tag or f"n{a.positions}-s{a.seed}"
    res = RESULTS / a.tag
    res.mkdir(parents=True, exist_ok=True)
    z = read(a)
    rS, rW, f = z["rS"], z["rW"], z["f"]
    dis = z["topS"] != z["topW"]
    d = rS - rW
    n_d, n_a = int(dis.sum()), int((~dis).sum())
    # 3: look
    md, ma = d[dis].mean(0), d[~dis].mean(0)
    vd, va = d[dis].var(0, ddof=1), d[~dis].var(0, ddof=1)
    diff = md - ma
    t = diff / np.sqrt(vd / max(n_d, 1) + va / max(n_a, 1) + 1e-12)
    act = (f > 0).mean(0)
    out = [f"# Each model's reading of the shared latents: where S and W disagree vs agree", "",
           f"{len(dis)} held-out middlegame positions (one per game): S and W pick different top moves at {n_d} "
           f"({n_d / len(dis):.0%}), the same at {n_a}. r^m = (x_m - b_dec_m) W_enc^m, each model's block of the "
           "pre-activation; d = r^S - r^W.", ""]
    for nm, order in (("larger at disagree positions (S reads it more than W there)", np.argsort(-diff)),
                      ("smaller at disagree positions (W reads it more than S there)", np.argsort(diff))):
        out += [f"## The {a.show} latents with the mean of d most {nm}", "",
                "| latent | mean d, disagree | mean d, agree | difference | t | active (any position) |", "|---|---|---|---|---|---|"]
        out += [f"| {j} | {md[j]:+.3f} | {ma[j]:+.3f} | {diff[j]:+.3f} | {t[j]:+.1f} | {act[j]:.1%} |" for j in order[:a.show]]
        out.append("")
    big_t = np.argsort(-np.abs(t))[:a.show]
    out += [f"By |t| instead (the difference against its noise): " + ", ".join(f"{j} ({t[j]:+.1f})" for j in big_t), ""]
    # 4: LP, fit on half the disagree positions by game
    fit = dis & (np.array([zlib.crc32(f"{b}/{g}".encode()) % 2 for b, g in zip(z["band"], z["game"])]) == 0)
    held = dis & ~fit
    cols = np.flatnonzero((f[fit] > 0).mean(0) >= a.min_active)
    rep = dict(n=len(dis), disagree=n_d, agree=n_a, fit=int(fit.sum()), held=int(held.sum()), lp_latents=len(cols), sides={})
    out += ["## Schut's LP", "", f"Fit on {fit.sum()} disagree positions (half, by game), on the {len(cols)} latents active at >= "
            f"{a.min_active:.0%} of them; soft margin nu = {a.nu}. Held out: {held.sum()} disagree positions; and all {n_a} agree "
            "positions (never fitted on).", "",
            "| side | fit margin | holds: fit disagree | held-out disagree | agree | v (latent: weight) |", "|---|---|---|---|---|---|"]
    for side, sgn in (("S over W (v.(r^S - r^W))", 1), ("W over S (v.(r^W - r^S))", -1)):
        Dfit = sparse.csr_matrix(sgn * d[fit][:, cols])
        _, r = gd.maxmin(("lp", Dfit, cols, a.nu, False))
        if r is None:
            out.append(f"| {side} | no solution | | | | |")
            continue
        vc, vw, m, _ = r
        v = np.zeros(d.shape[1])
        v[vc] = vw
        s = sgn * d @ v
        h = lambda mask: float((s[mask] >= m).mean()) if mask.any() else float("nan")
        out.append(f"| {side} | {m:.4f} | {h(fit):.0%} | **{h(held):.0%}** | **{h(~dis):.0%}** | "
                   + ", ".join(f"{j}: {x:.2f}" for j, x in sorted(zip(vc, vw), key=lambda x: -x[1])[:15])
                   + (" ..." if len(vc) > 15 else "") + " |")
        rep["sides"][side] = dict(margin=m, v=dict(zip(map(int, vc), map(float, vw))), fit=h(fit), held=h(held), agree=h(~dis),
                                  mean_held=float(s[held].mean()), mean_agree=float(s[~dis].mean()))
    out += ["", "A real concept: the constraint holds clearly more often on the held-out disagree positions than on the agree ones "
            "(both never fitted on).", ""]
    rep["top_diff"] = [int(j) for j in np.argsort(-np.abs(diff))[:a.show]]
    (res / "report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    (res / "report.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print("\n".join(out[-8:]))
    print(f"wrote {res / 'report.md'}")


if __name__ == "__main__":
    main()
