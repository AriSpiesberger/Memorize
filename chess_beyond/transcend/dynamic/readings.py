"""Each model's own reading of the shared latents, at the same positions: where S and W pick different moves, does
S's reading differ from W's more than where they agree?

    python transcend/dynamic/readings.py --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal

1. positions  --positions held-out middlegame positions, one per game (seeded random order); S's and W's top moves
              (their policies' most likely move); a position disagrees when they differ, agrees when not.
2. readings   each model's own reading of every latent from the crosscoder encoder, before the shared nonlinearity:
              r^m = (x_m - b_dec_m) W_enc^m, its block of the pre-activation sum_m r^m + b_enc (x_m: the model's state
              at the position, scaled as the crosscoder was trained). Also the latents' activations f (after the shared
              ReLU and threshold), for which latents are active. Checked first: r^S + r^W + b_enc reproduces the
              encoder's own pre-activation (a wrong bias, block or transpose stops the run). Readings are
              pre-activations, so they can be negative; "active" always means the joint code (f > 0), never a reading's
              sign. Encoder columns differ in scale between the models, so d = r^S - r^W carries a constant offset per
              latent: only the contrast disagree vs agree counts, where the offset cancels.
3. look       per active latent (f > 0 at >= --min-active of positions), the mean of r^S - r^W over the disagree
              positions against the agree ones: the --show with the largest difference either way, its t, and its
              Spearman correlation with the policies' JS divergence; and the latent pairs whose d is exactly opposite.
4. LP         Schut's soft-margin max-min LP (v >= 0, sum(v) <= 1, active latents), fitted on half the positions (by
              game), two ways. (1) The readings: S's side on d = r^S - r^W at the fit disagree positions (W's on -d);
              it holds where v.d reaches the fitted margin; gap = held-out disagree hits minus agree hits. (2) The
              contrast: positives d at the fit disagree positions, negatives d at the fit agree ones (their pairs), so a
              constant offset between the models' readings cancels; held-out AUC of v.d, disagree against agree. Each
              against --perms permutations of the disagree / agree labels, refitted. And, threshold-free, v.d against
              the Jensen-Shannon divergence of the two policies on the held-out positions (Spearman).

-> results/transcend/readings/<tag>/report.md, report.json; runs/transcend/readings/<tag>/readings.npz."""

import argparse
import json
import sys
import time
import zlib
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # chess_beyond/
import paths  # noqa: E402  also puts transcend/'s folders on sys.path
import eval as ev
import shared as gd
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
        if "js" in z.files:                                            # caches from before the divergence are redone
            return {k: z[k] for k in z.files}
    dev = ev.device(a.device)
    cc = gd.load_cc(a.cc_run, a.cc, a.strong, dev)
    models = {m: ev.load(cc.info["models"][m], dev)[0] for m in (0, 1)}
    t0 = time.time()
    P = positions(a, min(m.ctx for m in models.values()))
    boards, prompts = [b for _, b in P], [r["prompt"] for r, _ in P]
    top, st, dist = {}, {}, {}
    for m in (0, 1):
        legal, lp, states = gd.policy(models[m], boards, dev, prompts, grab=(cc.layer[m],), batch=a.batch)
        top[m] = [mv[int(np.argmax(l))].uci() for mv, l in zip(legal, lp)]
        dist[m] = [np.exp(l - np.logaddexp.reduce(l)) for l in lp]     # legal moves in the same order for both models
        st[m] = states[cc.layer[m]].float()
    js = np.array([js_div(p, q) for p, q in zip(dist[cc.s], dist[cc.w])])
    print(f"{len(P)} positions, both policies ({time.time() - t0:.0f}s)", flush=True)
    with torch.no_grad():
        x = torch.stack([st[m].to(dev) for m, _ in cc.sources], 1) * cc.scales[None, :, None]
        d = x.shape[-1]
        W, bd = cc.coder.W_enc, cc.coder.b_dec
        r = {m: ((x[:, i] - bd[i]) @ W[i * d:(i + 1) * d]).cpu().numpy() for i, (m, _) in enumerate(cc.sources)}
        f_, pre, _ = cc.coder.encode(x)
        f = f_.cpu().numpy()
        # the readings must add up to the crosscoder's own pre-activation: a wrong bias, block or transpose shows here
        recon = r[0] + r[1] + cc.coder.b_enc.cpu().numpy()
        err = np.abs(recon - pre.cpu().numpy())
        scale = np.abs(pre.cpu().numpy()).mean()
        print(f"sanity: r^S + r^W + b_enc against the encoder's pre-activation: max |error| {err.max():.2e}, mean "
              f"{err.mean():.2e} (mean |pre-activation| {scale:.3f})", flush=True)
        if err.max() > 1e-3 * max(scale, 1e-6) * 100:
            sys.exit("the readings don't reproduce the pre-activation: stopping")
    out = dict(rS=r[cc.s].astype(np.float32), rW=r[cc.w].astype(np.float32), f=f.astype(np.float32),
               topS=np.array(top[cc.s]), topW=np.array(top[cc.w]), js=js.astype(np.float32), fen=np.array([b.fen() for b in boards]),
               band=np.array([r_["band"] for r_, _ in P]), game=np.array([str(r_["game"]) for r_, _ in P]))
    np.savez_compressed(cache, **out)
    return out


def js_div(p, q):
    """Jensen-Shannon divergence (bits) between two distributions over the same moves."""
    m = (p + q) / 2
    kl = lambda x, y: float(np.sum(x[x > 0] * np.log2(x[x > 0] / y[x > 0])))
    return (kl(p, m) + kl(q, m)) / 2


def auc(score, label):
    pos, neg = score[label], score[~label]
    if not len(pos) or not len(neg):
        return float("nan")
    r = np.argsort(np.argsort(np.r_[pos, neg])) + 1.0
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def spearman(x, y):
    rx, ry = np.argsort(np.argsort(x)), np.argsort(np.argsort(y))
    return float(np.corrcoef(rx, ry)[0, 1])


def pairs_lp(d, pos, neg, cols, nu, rng, most):
    """Schut's LP on the pairs (a positive position minus a negative one) of d restricted to cols -> (v, margin) or None."""
    from scipy import sparse
    P, N = np.flatnonzero(pos), np.flatnonzero(neg)
    ii = np.stack(np.meshgrid(P, N, indexing="ij"), -1).reshape(-1, 2)
    if len(ii) > most:
        ii = ii[rng.choice(len(ii), most, replace=False)]
    _, r = gd.maxmin(("lp", sparse.csr_matrix(d[ii[:, 0]][:, cols] - d[ii[:, 1]][:, cols]), cols, nu, False))
    if r is None or not len(r[0]):
        return None
    v = np.zeros(d.shape[1])
    v[r[0]] = r[1]
    return v, r[2]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cc-run", default="runs/transcend/crosscoder/everything-3m")
    ap.add_argument("--cc", default="Lfinal")
    ap.add_argument("--strong", default="2400")
    ap.add_argument("--population", default=str(gd.PROBE / "population.jsonl"))
    ap.add_argument("--positions", type=int, default=1000)
    ap.add_argument("--show", type=int, default=20)
    ap.add_argument("--nu", type=float, default=0.2, help="soft margin: the share of fit rows allowed inside it")
    ap.add_argument("--nu-contrast", type=float, default=0.5, help="the contrast LP's soft margin: the share of disagree-agree "
                    "pairs allowed inside it (0.5: the median pair separated; 0.2 asks 80% of pairs, which no v >= 0 may reach)")
    ap.add_argument("--min-active", type=float, default=0.05, help="latents active at >= this share of positions (lists, LPs)")
    ap.add_argument("--max-pairs", type=int, default=5000, help="disagree-agree pairs per contrast LP at most")
    ap.add_argument("--perms", type=int, default=100, help="label permutations for the significance of each gap")
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
    rS, rW, f, js = z["rS"], z["rW"], z["f"], z["js"]
    dis = z["topS"] != z["topW"]
    d = rS - rW
    n_d, n_a = int(dis.sum()), int((~dis).sum())
    act = (f > 0).mean(0)
    live = np.flatnonzero(act >= a.min_active)
    fit = np.array([zlib.crc32(f"{b}/{g}".encode()) % 2 for b, g in zip(z["band"], z["game"])]) == 0   # by game
    held = ~fit
    rng = np.random.default_rng(a.seed)
    out = [f"# Each model's reading of the shared latents: where S and W disagree vs agree", "",
           f"{len(dis)} held-out middlegame positions (one per game): S and W pick different top moves at {n_d} "
           f"({n_d / len(dis):.0%}), the same at {n_a}; their policies' Jensen-Shannon divergence: median {np.median(js):.3f} bits "
           f"(disagree {np.median(js[dis]):.3f}, agree {np.median(js[~dis]):.3f}). r^m = (x_m - b_dec_m) W_enc^m, each model's "
           f"block of the pre-activation; d = r^S - r^W. Fit / held-out halves by game: {int((fit & dis).sum())} / "
           f"{int((held & dis).sum())} disagree, {int((fit & ~dis).sum())} / {int((held & ~dis).sum())} agree. Only latents active "
           f"(joint code f > 0) at >= {a.min_active:.0%} of positions: {len(live)}.", ""]

    # 3: look, active latents only
    md, ma = d[dis].mean(0), d[~dis].mean(0)
    t = (md - ma) / np.sqrt(d[dis].var(0, ddof=1) / n_d + d[~dis].var(0, ddof=1) / n_a + 1e-12)
    rho = np.array([spearman(d[:, j], js) for j in live])
    for nm, order in (("larger at disagree positions (S reads it more than W there)", live[np.argsort(-(md - ma)[live])]),
                      ("smaller at disagree positions (W reads it more than S there)", live[np.argsort((md - ma)[live])])):
        out += [f"## The {a.show} active latents with the mean of d most {nm}", "",
                "| latent | mean d, disagree | mean d, agree | difference | t | Spearman with JS | active |", "|---|---|---|---|---|---|---|"]
        out += [f"| {j} | {md[j]:+.3f} | {ma[j]:+.3f} | {md[j] - ma[j]:+.3f} | {t[j]:+.1f} | {rho[np.searchsorted(live, j)]:+.2f} | "
                f"{act[j]:.0%} |" for j in order[:a.show]]
        out.append("")
    C = np.corrcoef(d[:, live].T)
    mirror = [(int(live[i]), int(live[j])) for i, j in zip(*np.where(np.triu(C, 1) < -0.99))]
    out += [f"Pairs of active latents whose d is exactly opposite (correlation < -0.99: one quantity, two latents): {len(mirror)}"
            + (": " + ", ".join(f"{i}/{j}" for i, j in mirror[:20]) if mirror else "") + ".", ""]

    # the LPs. (1) as before: S's reading over W's on the disagree positions; (2) the contrast: d at disagree positions
    # against d at agree ones, where a constant offset can't help
    def lp_readings(lab, sgn):
        cols = live[(f[fit & lab][:, live] > 0).mean(0) >= a.min_active] if (fit & lab).any() else live
        _, r = gd.maxmin(("lp", sparse.csr_matrix(sgn * d[fit & lab][:, cols]), cols, a.nu, False))
        if r is None or not len(r[0]):
            return None
        v = np.zeros(d.shape[1])
        v[r[0]] = r[1]
        s = sgn * d @ v
        return v, r[2], float((s[held & lab] >= r[2]).mean()) - float((s[held & ~lab] >= r[2]).mean()), s

    def lp_contrast(lab, sgn):
        got = pairs_lp(sgn * d, fit & lab, fit & ~lab, live, a.nu_contrast, rng, a.max_pairs)
        if got is None:
            return None
        v, m = got
        s = sgn * d @ v
        return v, m, auc(s[held], lab[held]), s

    def perm(fn, sgn, stat, none):
        vals = []
        for _ in range(a.perms):
            lab = np.zeros(len(dis), bool)
            for half in (fit, held):                                  # shuffle within each half, keeping the counts
                idx = np.flatnonzero(half)
                lab[rng.choice(idx, int(dis[half].sum()), replace=False)] = True
            got = fn(lab, sgn)
            vals.append(none if got is None else got[2])     # no solution: v = 0, a constant score
            print(f"\r    permutations {_ + 1}/{a.perms}", end="", flush=True)
        print()
        vals = np.array(vals)
        return float(((vals >= stat).sum() + 1) / (len(vals) + 1)), vals

    rep = dict(n=len(dis), disagree=n_d, agree=n_a, live=len(live), mirror=mirror, lps={})
    out += ["## Schut's LP, two ways", "",
            "(1) As before: S's reading over W's (or W's over S's) on the fit disagree positions; it holds at a position when "
            "v.d reaches the fitted margin. Gap = held-out disagree hits minus held-out agree hits. (2) The contrast: positives d "
            "at the fit disagree positions, negatives d at the fit agree ones (their pairs), so the offset between the models' "
            "readings cancels and the LP has to find what is specific to disagreement; scored by the held-out AUC of v.d for "
            "disagree against agree (S's side: v.d larger where they disagree; W's side: smaller). Both against "
            f"{a.perms} permutations of the disagree / agree labels (within each half), refitted; and v.d against the policies' "
            "Jensen-Shannon divergence on all held-out positions (Spearman), threshold-free.", "",
            "| LP | side | held-out disagree / agree | statistic | permutation p (null median, 95%) | Spearman v.d with JS (held out) | v (latent: weight) |",
            "|---|---|---|---|---|---|---|"]
    for kind, fn in (("(1) readings", lp_readings), ("(2) contrast", lp_contrast)):
        for side, sgn in (("S", 1), ("W", -1)):
            print(f"  {kind}, {side}'s side: fitting, then {a.perms} permutations", flush=True)
            got = fn(dis, sgn)
            if got is None:
                out.append(f"| {kind} | {side} | no solution | | | | |")
                continue
            v, m, stat, s = got
            p, nul = perm(fn, sgn, stat, 0.0 if kind == "(1) readings" else 0.5)
            if kind == "(1) readings":
                hd, ha = float((s[held & dis] >= m).mean()), float((s[held & ~dis] >= m).mean())
                cell, st = f"{hd:.0%} / {ha:.0%}", f"gap {stat:+.0%}"
                nl = f"{np.median(nul):+.0%}, {np.quantile(nul, 0.95):+.0%}"
            else:
                cell, st = f"{int((held & dis).sum())} / {int((held & ~dis).sum())}", f"AUC {stat:.2f}"
                nl = f"{np.median(nul):.2f}, {np.quantile(nul, 0.95):.2f}"
            rj = spearman(s[held], js[held])
            vs = sorted(((j, x) for j, x in enumerate(v) if x > 0), key=lambda x: -x[1])
            out.append(f"| {kind} | {side} | {cell} | {st} | {p:.3f} ({nl}) | {rj:+.2f} | "
                       + ", ".join(f"{j}: {x:.2f}" for j, x in vs[:12]) + (" ..." if len(vs) > 12 else "") + " |")
            rep["lps"][f"{kind} {side}"] = dict(stat=stat, p=p, null=nul.tolist(), spearman_js=rj, v={int(j): float(x) for j, x in vs})
    out += ["", "A concept specific to disagreement: the contrast LP's held-out AUC clearly above its permutation null, and v.d "
            "rising with the policies' divergence on held-out positions.", ""]
    (res / "report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    (res / "report.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print("\n".join(out[-(len(rep['lps']) + 4):]))
    print(f"wrote {res / 'report.md'}")


if __name__ == "__main__":
    main()
