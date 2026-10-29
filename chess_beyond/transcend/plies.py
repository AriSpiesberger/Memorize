"""Does the S-W reading difference at disagree positions grow over the plies after the decision? The 1,000 positions
of readings.py, their disagree / agree labels and fit / held-out halves, and its two contrast directions v_S, v_W,
followed along lines both models play.

    python transcend/plies.py --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal               # both stages
    python transcend/plies.py --stage analyse                                                             # CPU only

1. play     from each position, --lines rollouts by S and --lines by W, --plies plies each, temperature --T, the
            model writing both colours' moves. At every position of every line (ply 0 = the root) both models'
            states, and their readings r^S, r^W of the active latents (readings.py's formula and sanity check:
            r^S + r^W + b_enc reproduces the encoder's pre-activation). In chunks of --chunk positions, each saved
            as it finishes (a rerun skips finished chunks); the first chunk's time projects the total.
2. analyse  per ply tau, three modes. A, S's line: d = S's reading of S's line minus W's reading of it; A, W's line:
            the same on W's line; B, own lines: S's reading of S's line minus W's reading of W's line (rollout k of S
            paired with rollout k of W), which splits into the representation term (A on S's line) plus the
            trajectory term (W's reading of S's line minus W's reading of W's line). Each line is an example; a line
            carries its position's label and half. Per mode and side (S's direction on d, W's on -d):
              fixed   v_S / v_W from readings.py (fitted at the roots), held-out AUC disagree vs agree
              refit   the same contrast LP refitted at tau on the fit lines, held-out AUC
              null    --perms shuffles of the positions' labels within each half (a position's lines move together):
                      the fixed direction rescored, and the LP refitted (no solution: v = 0, AUC 0.5); 95th and p
            Stops at tau = 0 if the fixed AUC doesn't reproduce readings.py's (every line starts at the root).
            report.md / report.json / auc.png rewritten after every ply, so a partial run is usable.

-> runs/transcend/plies/<tag>/chunk-<i>.npz; results/transcend/plies/<tag>/report.md, report.json, auc.png."""

import argparse
import json
import sys
import time
import zlib
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paths
import eval as ev
import readings as rd
import shared as gd
from pgn_model import MAX_MOVE_CHARS

RUNS = paths.RUNS / "transcend" / "plies"
RESULTS = paths.ROOT / "results" / "transcend" / "plies"
MODES = ("A, S's line", "A, W's line", "B, own lines")


def setup(a):
    """readings.py's positions, labels, halves, active latents and contrast directions."""
    z = dict(np.load(rd.RUNS / a.tag / "readings.npz", allow_pickle=True))
    rep = json.loads((rd.RESULTS / a.tag / "report.json").read_text(encoding="utf-8"))
    live = np.flatnonzero((z["f"] > 0).mean(0) >= a.min_active)
    if len(live) != rep["live"]:
        sys.exit(f"{len(live)} active latents here, {rep['live']} in readings.py's report: different --min-active?")
    v = {}
    for side in ("S", "W"):
        w = rep["lps"][f"(2) contrast {side}"]["v"]
        out = set(map(int, w)) - set(live.tolist())
        if out:
            sys.exit(f"{side}'s direction uses latents outside the active set: {sorted(out)}")
        v[side] = np.zeros(len(live))
        v[side][np.searchsorted(live, [int(j) for j in w])] = list(w.values())
    dis = z["topS"] != z["topW"]
    fit = np.array([zlib.crc32(f"{b}/{g}".encode()) % 2 for b, g in zip(z["band"], z["game"])]) == 0   # readings.py's halves
    return z, rep, live, v, dis, fit


def play(a, z, live):
    dev = ev.device(a.device)
    cc = gd.load_cc(a.cc_run, a.cc, a.strong, dev)
    models = {m: ev.load(cc.info["models"][m], dev)[0] for m in (0, 1)}
    ctx = min(m.ctx for m in models.values())
    P = rd.positions(argparse.Namespace(seed=a.seed, population=a.population, positions=a.positions), ctx)
    if [b.fen() for _, b in P] != list(z["fen"]):
        sys.exit("these positions aren't readings.py's (a different --population, --positions or --seed?)")
    run = RUNS / a.tag
    run.mkdir(parents=True, exist_ok=True)
    chunks = range(0, len(P), a.chunk)
    t0, done = time.time(), 0
    for c in chunks:
        path = run / f"chunk-{c // a.chunk:03d}.npz"
        if path.exists():
            continue
        t1 = time.time()
        part = P[c:c + a.chunk]
        out = {}
        for who, m in (("S", cc.s), ("W", cc.w)):
            rng = np.random.default_rng(zlib.crc32(f"{a.seed}/{who}/{c}".encode()))
            L = [dict(board=b.copy(), moves=[], sans=[], prompt=r["prompt"]) for r, b in part for _ in range(a.lines)]
            for ply in range(a.plies):
                go = [l for l in L if len(l["moves"]) == ply and not l["board"].is_game_over()
                      and len(l["prompt"]) + 2 * MAX_MOVE_CHARS + 4 <= ctx]       # room for this move and the next prompt end
                if not go:
                    break
                lg, lps, _ = gd.policy(models[m], [l["board"] for l in go], dev, [l["prompt"] for l in go], batch=a.batch)
                for l, mv, p in zip(go, lg, lps):
                    gd.advance(l, mv[gd.sample(p, a.T, rng)])
            Ld = dict(roots=[dict(prompt=r["prompt"], fen=b.fen()) for r, b in part],
                      lines=[dict(root=i // a.lines, moves=l["moves"]) for i, l in enumerate(L)])
            seqs, ends, _, _, _, start = gd.positions(Ld)
            st = {mm: gd.line_states(models[mm], seqs, ends, cc.layer[mm], dev, a.max_tokens) for mm in (0, 1)}
            R = {mm: [] for mm in (0, 1)}
            err, scale = 0.0, []
            with torch.no_grad():
                W, bd = cc.coder.W_enc, cc.coder.b_dec
                for i in range(0, len(st[0]), 4096):
                    x = torch.stack([st[mm][i:i + 4096].to(dev).float() for mm, _ in cc.sources], 1) * cc.scales[None, :, None]
                    dd = x.shape[-1]
                    r = {mm: (x[:, k] - bd[k]) @ W[k * dd:(k + 1) * dd] for k, (mm, _) in enumerate(cc.sources)}
                    _, pre, _ = cc.coder.encode(x)
                    err = max(err, float((r[0] + r[1] + cc.coder.b_enc - pre).abs().max()))
                    scale.append(float(pre.abs().mean()))
                    for mm in (0, 1):
                        R[mm].append(r[mm][:, live].cpu().numpy())
            if err > 0.1 * max(np.mean(scale), 1e-6):
                sys.exit(f"the readings don't reproduce the pre-activation (max |error| {err:.2e}): stopping")
            n = len(part)
            alive = np.zeros((n, a.lines, a.plies + 1), bool)
            arr = {mm: np.full((n, a.lines, a.plies + 1, len(live)), np.nan, np.float32) for mm in (0, 1)}
            for mm in (0, 1):
                Rm = np.concatenate(R[mm])
                for q in range(len(L)):
                    k = start[q + 1] - start[q]
                    arr[mm][q // a.lines, q % a.lines, :k] = Rm[start[q]:start[q + 1]]
                    alive[q // a.lines, q % a.lines, :k] = True
            out[f"rS_{who}"], out[f"rW_{who}"], out[f"alive_{who}"] = arr[cc.s], arr[cc.w], alive
            out[f"err_{who}"] = err
        np.savez_compressed(path, **out)
        done += 1
        left = sum(not (run / f"chunk-{cc_ // a.chunk:03d}.npz").exists() for cc_ in chunks)
        print(f"chunk {c // a.chunk + 1}/{len(chunks)}: {len(part)} positions, {time.time() - t1:.0f}s"
              + (f"; projected for the {left} left: {(time.time() - t0) / done * left / 60:.0f} min" if left else ""), flush=True)


_W = {}


def _refit(job):
    """One fit of the contrast LP on the fit lines under the labels lab (in a worker, which reads the ply's data once
    from the file the parent wrote) -> (held-out AUC, v or None)."""
    path, lab, seed, nu, most = job
    if _W.get("path") != path:
        z = np.load(path)
        _W.clear()
        _W.update(path=path, **{k: z[k] for k in z.files})
    w = _W
    got = rd.pairs_lp(w["sdd"], w["fl"] & lab[w["pp"]], w["fl"] & ~lab[w["pp"]], np.arange(w["sdd"].shape[1]), nu,
                      np.random.default_rng(seed), most)
    if got is None:
        return 0.5, None                                           # no solution: v = 0, a constant score
    return rd.auc(w["sdd"][w["hl"]] @ got[0], lab[w["pp"]][w["hl"]]), got[0]


def load(a):
    run = RUNS / a.tag
    files = sorted(run.glob("chunk-*.npz"))
    want = [run / f"chunk-{i:03d}.npz" for i in range(len(files))]
    if files != want:
        print("note: chunks missing in the middle; using the contiguous ones from the start")
    keep = []
    for f in want:
        if not f.exists():
            break
        keep.append(np.load(f))
    if not keep:
        sys.exit(f"no chunks in {run}: run --stage play first")
    return {k: np.concatenate([c[k] for c in keep]) for k in ("rS_S", "rW_S", "alive_S", "rS_W", "rW_W", "alive_W")}


def analyse(a, z, rep, live, v, dis, fit):
    D = load(a)
    N = len(D["alive_S"])
    dis, fit = dis[:N], fit[:N]
    held = ~fit
    Lc = D["alive_S"].shape[1]
    pos = np.repeat(np.arange(N), Lc)
    res = RESULTS / a.tag
    res.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(a.seed)
    shuf = []                                                     # the same shuffles for every ply, mode and side
    for _ in range(a.perms):
        lab = np.zeros(N, bool)
        for half in (fit, held):
            idx = np.flatnonzero(half)
            lab[rng.choice(idx, int(dis[half].sum()), replace=False)] = True
        shuf.append(lab)
    rows, decomp = [], []
    t_start = time.time()
    tmp = RUNS / a.tag / "fits"
    tmp.mkdir(parents=True, exist_ok=True)
    pool = Pool(a.workers)                                        # one pool for the whole run
    for tau in range(a.plies + 1):
        t1 = time.time()
        g = lambda k: D[k][:, :, tau].reshape(N * Lc, -1)
        aS, aW = D["alive_S"][:, :, tau].ravel(), D["alive_W"][:, :, tau].ravel()
        X = {MODES[0]: (g("rS_S") - g("rW_S"), aS), MODES[1]: (g("rS_W") - g("rW_W"), aW),
             MODES[2]: (g("rS_S") - g("rW_W"), aS & aW)}
        if tau == 0:
            root = (z["rS"] - z["rW"])[:N][:, live]
            e = np.nanmax(np.abs(X[MODES[0]][0][aS] - root[pos[aS]]))
            print(f"tau 0: the lines' root readings against readings.py's: max |difference| {e:.3f} "
                  f"(mean |d| {np.abs(root).mean():.3f})")
        for mode in MODES:
            d, ok = X[mode]
            dd, pp = np.nan_to_num(d[ok]), pos[ok]
            fl, hl = fit[pp], held[pp]
            for side, sgn in (("S", 1), ("W", -1)):
                s = sgn * dd @ v[side]
                fixed = rd.auc(s[hl], dis[pp][hl])
                if tau == 0 and mode == MODES[0]:
                    want = rep["lps"][f"(2) contrast {side}"]["stat"]
                    print(f"  sanity, {side}'s direction: fixed AUC at the roots {fixed:.3f}, readings.py {want:.3f}")
                    if N == rep["n"] and abs(fixed - want) > 0.02:
                        sys.exit("the roots don't reproduce readings.py's AUC: stopping")

                nf = np.array([rd.auc(s[hl], lab[pp][hl]) for lab in shuf])
                path = str(tmp / f"fit-{tau}-{MODES.index(mode)}-{side}.npz")
                np.savez(path, sdd=sgn * dd, fl=fl, hl=hl, pp=pp)
                jobs = [(path, lab, zlib.crc32(f"{a.seed}/{tau}/{mode}/{side}/{i}".encode()), a.nu_contrast, a.max_pairs)
                        for i, lab in enumerate([dis] + shuf)]
                got = []
                for r in pool.imap(_refit, jobs):
                    got.append(r)
                    print(f"\r  ply {tau}, {mode}, {side}'s side: {len(got)}/{len(jobs)} fits", end="", flush=True)
                Path(path).unlink(missing_ok=True)
                ref, vr = got[0]
                nr = np.array([g_[0] for g_ in got[1:]])
                rows.append(dict(tau=tau, mode=mode, side=side, lines=int(hl.sum()), fixed=fixed,
                                 fixed_null95=float(np.quantile(nf, .95)), fixed_p=float(((nf >= fixed).sum() + 1) / (len(nf) + 1)),
                                 refit=ref, refit_null95=float(np.quantile(nr, .95)), refit_p=float(((nr >= ref).sum() + 1) / (len(nr) + 1)),
                                 refit_v={int(live[j]): float(x) for j, x in enumerate(vr) if x > 0} if vr is not None else {}))
        print()
        # mode B's decomposition, with the fixed directions
        ok = aS & aW
        hl = held[pos] & ok
        for side, sgn in (("S", 1), ("W", -1)):
            rep_t = sgn * np.nan_to_num(g("rS_S") - g("rW_S")) @ v[side]
            trj_t = sgn * np.nan_to_num(g("rW_S") - g("rW_W")) @ v[side]
            lab = dis[pos]
            gap = lambda s: float(s[hl & lab].mean() - s[hl & ~lab].mean())
            decomp.append(dict(tau=tau, side=side, representation=gap(rep_t), trajectory=gap(trj_t), total=gap(rep_t + trj_t),
                               auc_representation=rd.auc(rep_t[hl], lab[hl]), auc_trajectory=rd.auc(trj_t[hl], lab[hl])))
        write(a, res, N, rows, decomp)
        el = time.time() - t1
        print(f"ply {tau} done ({el / 60:.1f} min)" + (f"; projected for the rest: {el * a.plies / 60:.0f} min" if tau == 0 else ""), flush=True)
    pool.close()
    print(f"wrote {res / 'report.md'} ({(time.time() - t_start) / 60:.0f} min)")


def write(a, res, N, rows, decomp):
    out = ["# The S-W reading difference over the plies after the decision", "",
           f"{N} of readings.py's positions; from each, {a.lines} lines by S and {a.lines} by W, {a.plies} plies, T = {a.T}. "
           "AUC: held-out lines, disagree vs agree (a line carries its position's label and half). Fixed: readings.py's contrast "
           "direction from the roots; refit: the contrast LP refitted at that ply. Null: "
           f"{a.perms} shuffles of the positions' labels within each half (refit: refitted, no solution = 0.5).", ""]
    for mode in MODES:
        for side in ("S", "W"):
            R = [r for r in rows if r["mode"] == mode and r["side"] == side]
            if not R:
                continue
            out += [f"## {mode}, {side}'s direction", "", "| ply | held-out lines | fixed AUC | null 95th | p | refit AUC | null 95th | p |",
                    "|---|---|---|---|---|---|---|---|"]
            out += [f"| {r['tau']} | {r['lines']} | {r['fixed']:.3f} | {r['fixed_null95']:.3f} | {r['fixed_p']:.3f} | {r['refit']:.3f} | "
                    f"{r['refit_null95']:.3f} | {r['refit_p']:.3f} |" for r in R]
            out.append("")
    out += ["## B, own lines: the decomposition (fixed directions)", "",
            "Mean of v.d on held-out disagree lines minus agree lines; representation = A on S's line (S's minus W's reading of S's "
            "line), trajectory = W's reading of S's line minus W's reading of W's line; they add up to the total.", "",
            "| ply | side | representation | trajectory | total | AUC representation | AUC trajectory |", "|---|---|---|---|---|---|---|"]
    out += [f"| {r['tau']} | {r['side']} | {r['representation']:+.3f} | {r['trajectory']:+.3f} | {r['total']:+.3f} | "
            f"{r['auc_representation']:.3f} | {r['auc_trajectory']:.3f} |" for r in decomp]
    (res / "report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    (res / "report.json").write_text(json.dumps(dict(rows=rows, decomposition=decomp), indent=1), encoding="utf-8")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 4, figsize=(17, 7), sharey="row")
    for j, mode in enumerate(MODES):
        for i, side in enumerate(("S", "W")):
            R = [r for r in rows if r["mode"] == mode and r["side"] == side]
            if not R:
                continue
            t = [r["tau"] for r in R]
            x = ax[i, j]
            x.fill_between(t, 0.5, [r["refit_null95"] for r in R], color="0.85", label="refit null 95th")
            x.plot(t, [r["fixed_null95"] for r in R], ":", color="0.4", label="fixed null 95th")
            x.plot(t, [r["fixed"] for r in R], "o-", label="fixed (roots' v)")
            x.plot(t, [r["refit"] for r in R], "s-", label="refit per ply")
            x.axhline(0.5, color="0.6", lw=0.8)
            x.set_title(f"{mode}, {side}'s direction", fontsize=10)
            x.set_xlabel("ply after the position")
            if j == 0:
                x.set_ylabel("held-out AUC")
    for i, side in enumerate(("S", "W")):
        R = [r for r in decomp if r["side"] == side]
        x = ax[i, 3]
        t = [r["tau"] for r in R]
        for k in ("representation", "trajectory", "total"):
            x.plot(t, [r[k] for r in R], "o-", label=k)
        x.axhline(0, color="0.6", lw=0.8)
        x.set_title(f"B decomposition, {side}'s direction", fontsize=10)
        x.set_xlabel("ply after the position")
        x.set_ylabel("mean v.d, disagree - agree")
        x.legend(fontsize=8)
    ax[0, 0].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(res / "auc.png", dpi=110)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=("all", "play", "analyse"), default="all")
    ap.add_argument("--cc-run", default="runs/transcend/crosscoder/everything-3m")
    ap.add_argument("--cc", default="Lfinal")
    ap.add_argument("--strong", default="2400")
    ap.add_argument("--population", default=str(gd.PROBE / "population.jsonl"))
    ap.add_argument("--positions", type=int, default=1000, help="readings.py's --positions")
    ap.add_argument("--seed", type=int, default=0, help="readings.py's --seed")
    ap.add_argument("--tag", default="", help="readings.py's tag (default n<positions>-s<seed>)")
    ap.add_argument("--lines", type=int, default=8, help="rollouts per model per position")
    ap.add_argument("--plies", type=int, default=8)
    ap.add_argument("--T", type=float, default=1.0)
    ap.add_argument("--chunk", type=int, default=50, help="positions per saved chunk (the first one is timed)")
    ap.add_argument("--min-active", type=float, default=0.05, help="readings.py's --min-active")
    ap.add_argument("--nu-contrast", type=float, default=0.5)
    ap.add_argument("--max-pairs", type=int, default=5000)
    ap.add_argument("--perms", type=int, default=100)
    ap.add_argument("--workers", type=int, default=8, help="processes for the LP fits (each ~1-2 GB)")
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--max-tokens", type=int, default=100_000, help="characters per forward pass for the lines' states")
    ap.add_argument("--device", default="auto")
    a = ap.parse_args()
    a.tag = a.tag or f"n{a.positions}-s{a.seed}"
    z, rep, live, v, dis, fit = setup(a)
    if a.stage in ("all", "play"):
        play(a, z, live)
    if a.stage in ("all", "analyse"):
        analyse(a, z, rep, live, v, dis, fit)


if __name__ == "__main__":
    main()
