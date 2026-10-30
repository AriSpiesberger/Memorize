"""Concept-level seed stability: whether divergence.py's concepts from a seed-0 crosscoder are the same directions as
those from a seed-1 crosscoder, whatever latents each seed built them from. CPU, after divergence.py report has run on
both crosscoders.

    python transcend/dynamic/conceptseed.py --tag0 p16-r1024-T0.4-s0-L11-4k --cc0 L11-4096 --tag1 p16-r1024-T0.4-s0-L11-4k-s1 --cc1 L11-4096-s1

direction  a family's v (its mean v over latents, |v|_1 = 1, from report.json) becomes a direction in both models' L11
           space through its own crosscoder's decoder: u = sum_j v_j mu_j d_j (mu_j: the divergence run's mean activation
           of latent j where it fires, the scale its binary code stands for; d_j: (2, 512), both models' decoder rows, in
           the crosscoder's scaled input space).
presence   at each of --positions held-out positions of the crosscoders' data (crossmix.py's held-out human and rollout
           states, half each), the raw L11 states of both models, scaled as the crosscoder scales them, projected onto u.
families   one row per (model, k, latent set): a support found in both halves (A and B) is one concept, its two
           members' numbers averaged (recurrence, each held out on the other half; correlations below).
match      per seed-0 family member, the seed-1 candidate whose presence correlates best with it on the selection half
           of the positions; the correlation reported is on the other half (so picking the best of many does not inflate
           it). Seed-1 candidates: its families with identical u merged (same latents and weights); among the families
           behind the chosen u, the one at the same k, then the higher recurrence, is reported. Two versions: any k (a
           concept that is one latent at k = 0 in seed 0 may be two at k = 4 in seed 1) and same k; the gap between them is
           how often a concept changes k across seeds. Beside it the cosine of the two u's, and the correlation of each
           model's part of u alone.
null       --null-sets sets of fake seed-0 families (each real one's weights on random seed-0 latents of the same
           firing-rate decile, firing on these positions), each matched to the seed-1 candidates exactly as the real ones
           (chosen on one half, scored on the other); per family the 95th percentile: whether a concept is more stable
           across seeds than random latents of its firing rate. (Fakes on the seed-1 side would not do: ~2,000
           single-latent fakes cover most of the 4,096 latents, so they nearly always contain the real counterpart.)
ceiling    the best single seed-1 latent, any (u = mu_j d_j), same selection: whether seed 1's dictionary has the direction
           at all. A family above its null but not above the ceiling is stable, but its family structure adds nothing
           over one latent.
--center   subtract the positions' mean state first. A check only: a projection of centred states differs from the
           uncentred one by a constant, which a correlation removes, so every number should be unchanged.

-> results/transcend/divergence/<tag0>/concept-seed-<tag1>.md, .json"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # chess_beyond/
import paths  # noqa: E402  also puts transcend/'s folders on sys.path
from crosscoder import CrossCoder
from crossmix import held_out_human, held_out_roll

DIV_RUNS = paths.RUNS / "transcend" / "divergence"
DIV_RES = paths.ROOT / "results" / "transcend" / "divergence"


def load_coder(run, cc):
    ck = torch.load(run / ("cc-" + cc.removeprefix("cc-")) / "cc.pt", map_location="cpu", weights_only=False)
    c = CrossCoder(len(ck["sources"]), ck["d"], ck["latents"], ck["k"]).eval()
    c.load_state_dict(ck["state"])
    return c, ck["scales"].float()


def positions(run, n, rng):
    """n held-out positions, half human, half rollout -> (n, models, d) float32, unscaled."""
    info = json.loads((run / "collect.json").read_text())
    R = json.loads((run / "rollouts" / "rows.json").read_text(encoding="utf-8"))
    hold = dict(human=held_out_human(np.load(run / "human" / "rows.npy")), rollouts=held_out_roll(R["roots"], R["rows"]))
    out = []
    for k in ("human", "rollouts"):
        idx = np.flatnonzero(hold[k])
        idx = np.sort(rng.choice(idx, min(n // 2, len(idx)), replace=False))
        if not all((run / k / "acts" / f"{nm}-L{info['layers'][0]}.npy").exists() for nm in info["names"]):
            sys.exit(f"missing activations in {run / k / 'acts'}")
        arr = [np.load(run / k / "acts" / f"{nm}-L{info['layers'][0]}.npy", mmap_mode="r") for nm in info["names"]]
        out.append(np.stack([np.asarray(x[idx], np.float32) for x in arr], 1))
    return np.concatenate(out), info


def families(tag, model):
    f = DIV_RES / tag / "report.json"
    if not f.exists():
        sys.exit(f"{f} missing: run divergence.py report --tag {tag} first")
    F = json.loads(f.read_text(encoding="utf-8")).get(model, {}).get("families", [])
    mu = np.array(json.loads((DIV_RUNS / tag / model / "mu.json").read_text(encoding="utf-8"))["mu"])
    return F, mu


def directions(F, mu, W):
    """(families, models, d): u = sum_j v_j mu_j d_j."""
    U = np.zeros((len(F),) + W.shape[1:], np.float32)
    for i, f in enumerate(F):
        lat = np.asarray(f["latents"], int)
        U[i] = np.einsum("j,jmd->md", np.asarray(f["weights"]) * mu[lat], W[lat])
    return U


def zcols(P):
    P = P - P.mean(0)
    return P / (P.std(0) + 1e-12)


def best_match(P0, P1, sel):
    """Per column of P0, the column of P1 with the highest correlation on sel -> (its index, its correlation on ~sel)."""
    a, b = zcols(P0[sel]), zcols(P1[sel])
    j = (a.T @ b / sel.sum()).argmax(1)
    a, b = zcols(P0[~sel]), zcols(P1[~sel])
    return j, (a * b[:, j]).mean(0)


def groups(F):
    """(k, latent set) -> indices of the families with that support (one per half it was found in)."""
    G = {}
    for i, f in enumerate(F):
        G.setdefault((f["k"], tuple(sorted(f["latents"]))), []).append(i)
    return G


def candidates(F):
    """Seed-1 families with identical u merged -> (one representative family per u, the families behind each)."""
    C = {}
    for i, f in enumerate(F):
        key = tuple(sorted(zip(f["latents"], np.round(f["weights"], 6))))
        C.setdefault(key, []).append(i)
    keys = list(C)
    return [F[C[key][0]] for key in keys], [C[key] for key in keys]


def pick(F1, members, k):
    """Among the seed-1 families behind one u: the same k first, then the higher recurrence."""
    return max(members, key=lambda i: (F1[i]["k"] == k, F1[i]["recurrence"]))


def match_cands(P0, k0, PC, ck, sel, same_k):
    """Per column of P0, its best candidate (any, or one with a family at the column's k) -> (candidate, correlation)."""
    if not same_k:
        return best_match(P0, PC, sel)
    j, r = np.zeros(P0.shape[1], int), np.full(P0.shape[1], np.nan)
    for k in np.unique(k0):
        i0 = np.flatnonzero(k0 == k)
        ic = np.flatnonzero([k in s_ for s_ in ck])
        if len(ic):
            jj, rr = best_match(P0[:, i0], PC[:, ic], sel)
            j[i0], r[i0] = ic[jj], rr
    return j, r


def best_latent(P0, X1, U, sel, chunk=4096):
    """Per column of P0, the best of U's rows as a direction on X1 (chosen on sel, scored on ~sel), in chunks of U."""
    a = zcols(P0[sel])
    bv, bj = np.full(P0.shape[1], -np.inf), np.zeros(P0.shape[1], int)
    for c in range(0, len(U), chunk):
        C = a.T @ zcols(X1[sel] @ U[c:c + chunk].T) / sel.sum()
        v, jj = C.max(1), C.argmax(1)
        upd = v > bv
        bv[upd], bj[upd] = v[upd], (jj + c)[upd]
    q = zcols(X1[~sel] @ U[bj].T)
    return bj, (zcols(P0[~sel]) * q).mean(0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cc-run", default="runs/transcend/crosscoder/mixed-L11")
    ap.add_argument("--tag0", required=True)
    ap.add_argument("--cc0", required=True)
    ap.add_argument("--tag1", required=True)
    ap.add_argument("--cc1", required=True)
    ap.add_argument("--models", default="S,W")
    ap.add_argument("--positions", type=int, default=20_000)
    ap.add_argument("--null-sets", type=int, default=20)
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--center", action="store_true", help="subtract the positions' mean state first (a check: no number should move)")
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    run = Path(a.cc_run)
    X, info = positions(run, a.positions, rng)
    sel = np.zeros(len(X), bool)
    sel[rng.permutation(len(X))[:len(X) // 2]] = True
    coders = [load_coder(run, cc) for cc in (a.cc0, a.cc1)]
    Xs = [torch.from_numpy(X) * sc[None, :, None] for _, sc in coders]
    W = [c.W_dec.detach().numpy() for c, _ in coders]
    with torch.no_grad():                                              # firing rates, for the null's deciles
        fire = [sum((c.encode(x[i:i + 4000])[0] > 0).sum(0) for i in range(0, len(X), 4000)).numpy() / len(X)
                for (c, _), x in zip(coders, Xs)]
    pools = []
    for fr in fire:
        act = np.flatnonzero(fr > 0)
        dec = np.searchsorted(np.quantile(fr[act], np.linspace(0, 1, 11)[1:-1]), fr)
        pools.append((dec, {b: act[dec[act] == b] for b in range(10)}))
    if a.center:
        Xs = [x - x.mean(0, keepdim=True) for x in Xs]
    Xf = [x.flatten(1).numpy() for x in Xs]
    Xs0, Xs1 = Xs[0].numpy(), Xs[1].numpy()
    si = next(i for i, n in enumerate(info["names"]) if "2400" in n)
    part = {"S": si, "W": 1 - si}

    out = [f"# Concept-level seed stability: {a.tag0} ({a.cc0}) against {a.tag1} ({a.cc1})", "",
           f"Each family's v -> u = sum_j v_j mu_j d_j through its own crosscoder; presence = the scaled raw L11 states of both "
           f"models{' (centred)' if a.center else ''} projected onto u, at {len(X)} held-out positions (half human, half rollout). "
           "One row per (k, latent set), its members in halves A and B averaged. Each seed-0 member's best seed-1 candidate "
           "(families with identical u merged; the same k, then the higher recurrence, reported) chosen on half the positions, "
           "scored on the other half; any k and same k. Null: "
           f"{a.null_sets} sets of fake seed-0 families (the real weights on random seed-0 latents of the same firing-rate decile) "
           "matched the same way, 95th percentile per family. Ceiling: the best single seed-1 latent, same selection. "
           "'At ceiling': the any-k correlation within 0.02 of the ceiling or above it.", ""]
    rep = {}
    lat = lambda f: ", ".join(f"{x} ({w:.2f})" for w, x in sorted(zip(f["weights"], f["latents"]), reverse=True)[:5])
    med = lambda x: float(np.nanmedian(x)) if len(x) else float("nan")
    for model in a.models.split(","):
        F0, mu0 = families(a.tag0, model)
        F1, mu1 = families(a.tag1, model)
        if not F0 or not F1:
            out += [f"## {model}", "", f"no families ({len(F0)} in seed 0, {len(F1)} in seed 1)", ""]
            continue
        C1, behind = candidates(F1)
        ck = [{F1[i]["k"] for i in b} for b in behind]
        U0, UC = directions(F0, mu0, W[0]), directions(C1, mu1, W[1])
        P0, PC = Xf[0] @ U0.reshape(len(F0), -1).T, Xf[1] @ UC.reshape(len(C1), -1).T
        k0 = np.array([f["k"] for f in F0])
        res_ = {v: match_cands(P0, k0, PC, ck, sel, v) for v in (False, True)}
        dec0, pool0 = pools[0]
        nul = {False: [], True: []}
        for _ in range(a.null_sets):
            fake = [dict(latents=[int(rng.choice(pool0[int(dec0[x])])) for x in f["latents"]], weights=f["weights"]) for f in F0]
            Pf = Xf[0] @ directions(fake, mu0, W[0]).reshape(len(F0), -1).T
            for v in (False, True):
                nul[v].append(match_cands(Pf, k0, PC, ck, sel, v)[1])
        n95 = {v: np.quantile(np.stack(nul[v]), 0.95, axis=0) for v in nul}
        live = np.flatnonzero(mu1 > 0)
        cj, cr = best_latent(P0, Xf[1], mu1[live, None] * W[1][live].reshape(len(live), -1), sel)
        cj = live[cj]
        j = res_[False][0]
        cos = np.array([float(U0[i].ravel() @ UC[j[i]].ravel() / (np.linalg.norm(U0[i]) * np.linalg.norm(UC[j[i]]) + 1e-12))
                        for i in range(len(F0))])
        per = {}
        for m, k in part.items():
            q0 = Xs0[:, k] @ U0[:, k].T
            q1 = Xs1[:, k] @ UC[:, k].T
            per[m] = (zcols(q0[~sel]) * zcols(q1[~sel])[:, j]).mean(0)
        rows = []
        for (k, _), idx in groups(F0).items():                         # one row per concept: its halves averaged
            i = idx[0]
            g = F1[pick(F1, behind[j[i]], k)]
            mean = lambda x: float(np.mean([x[t] for t in idx]))
            rows.append(dict(k=k, latents=F0[i]["latents"], weights=F0[i]["weights"], halves=len(idx),
                             recurrence=float(np.mean([F0[t]["recurrence"] for t in idx])),
                             div_null95=float(np.mean([F0[t]["null95"] for t in idx])),
                             match=g["latents"], match_weights=g["weights"], match_k=g["k"], match_recurrence=g["recurrence"],
                             corr=mean(res_[False][1]), corr_same_k=mean(res_[True][1]), null95=mean(n95[False]),
                             null95_same_k=mean(n95[True]), null_median=float(np.median(np.stack(nul[False])[:, idx])),
                             ceiling=mean(cr), ceiling_latent=int(cj[i]), u_cos=mean(cos), S_part=mean(per["S"]),
                             W_part=mean(per["W"])))
        for r in rows:
            r.update(stable=bool(r["corr"] > r["null95"]), stable_same_k=bool(r["corr_same_k"] > r["null95_same_k"]),
                     at_ceiling=bool(r["corr"] >= r["ceiling"] - 0.02), recurs=bool(r["recurrence"] > r["div_null95"]))
        out += [f"## {model}", "", f"{len(F0)} seed-0 family members -> {len(rows)} concepts; {len(F1)} seed-1 families -> "
                f"{len(C1)} distinct u's.", "",
                "| k | concepts | correlation, any k: median | same k: median | null median | above their null 95th: any k "
                "| same k | at ceiling | ceiling median | concepts recurring above their divergence null | of those, above "
                "the seed null (any k) | median u cosine |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for k in sorted({r["k"] for r in rows}):
            R = [r for r in rows if r["k"] == k]
            col = lambda f: np.array([r[f] for r in R], float)
            rec = [r for r in R if r["recurs"]]
            out.append(f"| {k} | {len(R)} | {med(col('corr')):.2f} | {med(col('corr_same_k')):.2f} | {med(col('null_median')):.2f} | "
                       f"{col('stable').mean():.0%} | {col('stable_same_k').mean():.0%} | {col('at_ceiling').mean():.0%} | "
                       f"{med(col('ceiling')):.2f} | {len(rec)} | "
                       f"{np.mean([r['stable'] for r in rec]) if rec else float('nan'):.0%} | {med(col('u_cos')):.2f} |")
        out.append("")
        for k in sorted({r["k"] for r in rows}):
            R = sorted([r for r in rows if r["k"] == k], key=lambda r: -r["recurrence"])[:a.top]
            out += [f"### {model}, k = {k}: the top {len(R)} by recurrence", "",
                    "| # | seed-0 latents (weight) | halves | recurrence (divergence null 95th) | matched seed-1 (k; latents) "
                    "| its recurrence | correlation, any k | same k | seed null 95th | ceiling (latent) | u cosine | S part "
                    "| W part |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
            for n, r in enumerate(R):
                out.append(f"| {n + 1} | {lat(r)} | {r['halves']} | {r['recurrence']:.1%} ({r['div_null95']:.1%}) | "
                           f"{r['match_k']}; {lat(dict(latents=r['match'], weights=r['match_weights']))} | "
                           f"{r['match_recurrence']:.1%} | {r['corr']:.2f}{' *' if r['stable'] else ''} | {r['corr_same_k']:.2f} | "
                           f"{r['null95']:.2f} | {r['ceiling']:.2f} ({r['ceiling_latent']}) | {r['u_cos']:.2f} | "
                           f"{r['S_part']:.2f} | {r['W_part']:.2f} |")
            out.append("")
        out[-1:] = ["", "*: above its seed null 95th (any k).", ""]
        rep[model] = rows
    res = DIV_RES / a.tag0
    res.mkdir(parents=True, exist_ok=True)
    (res / f"concept-seed-{a.tag1}{'-centred' if a.center else ''}.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    (res / f"concept-seed-{a.tag1}{'-centred' if a.center else ''}.json").write_text(json.dumps(dict(settings=vars(a), **rep)), encoding="utf-8")
    print("\n".join(out))
    print(f"wrote {res / f'concept-seed-{a.tag1}' }{'-centred' if a.center else ''}.md")


if __name__ == "__main__":
    main()
