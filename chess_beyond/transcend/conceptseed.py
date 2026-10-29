"""Concept-level seed stability: whether divergence.py's concepts from a seed-0 crosscoder are the same directions as
those from a seed-1 crosscoder, whatever latents each seed built them from. CPU, after divergence.py report has run on
both crosscoders.

    python transcend/conceptseed.py --tag0 p16-r1024-T0.4-s0-L11-4k --cc0 L11-4096 --tag1 p16-r1024-T0.4-s0-L11-4k-s1 --cc1 L11-4096-s1

direction  a family's v (its mean v over latents, |v|_1 = 1, from report.json) becomes a direction in both models' L11
           space through its own crosscoder's decoder: u = sum_j v_j mu_j d_j (mu_j: the divergence run's mean activation
           of latent j where it fires, the scale its binary code stands for; d_j: (2, 512), both models' decoder rows, in
           the crosscoder's scaled input space).
presence   at each of --positions held-out positions of the crosscoders' data (crossmix.py's held-out human and rollout
           states, half each), the raw L11 states of both models, scaled as the crosscoder scales them, projected onto u.
match      per seed-0 family, the seed-1 family (same model, any k) whose presence correlates best with it on the
           selection half of the positions; the correlation reported is on the other half (so picking the best of many
           does not inflate it). Beside it the cosine of the two u's, and the correlation of each model's part of u alone.
null       the same selection against --null-sets sets of fake seed-1 families: each real seed-1 family with its weights
           kept and its latents redrawn from seed-1 latents in the same firing-rate decile (firing on the same positions).
           Per seed-0 family, the 95th percentile of the fakes' held-out best correlation. Projections of random
           directions correlate with each other through the states' dominant directions, so this null is the bar, not 0.

-> results/transcend/divergence/<tag0>/concept-seed-<tag1>.md, .json"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paths
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
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    run = Path(a.cc_run)
    X, info = positions(run, a.positions, rng)
    sel = np.zeros(len(X), bool)
    sel[rng.permutation(len(X))[:len(X) // 2]] = True
    coders = [load_coder(run, cc) for cc in (a.cc0, a.cc1)]
    Xs = [torch.from_numpy(X) * sc[None, :, None] for _, sc in coders]
    W = [c.W_dec.detach().numpy() for c, _ in coders]
    with torch.no_grad():                                              # seed 1's firing rates, for the null's deciles
        c1, _ = coders[1]
        fire = sum((c1.encode(Xs[1][i:i + 4000])[0] > 0).sum(0) for i in range(0, len(X), 4000)).numpy() / len(X)
    act = np.flatnonzero(fire > 0)
    dec = np.searchsorted(np.quantile(fire[act], np.linspace(0, 1, 11)[1:-1]), fire)
    pool = {b: act[dec[act] == b] for b in range(10)}
    Xf = [x.flatten(1).numpy() for x in Xs]
    si = next(i for i, n in enumerate(info["names"]) if "2400" in n)
    part = {"S": si, "W": 1 - si}

    out = [f"# Concept-level seed stability: {a.tag0} ({a.cc0}) against {a.tag1} ({a.cc1})", "",
           f"Each family's v -> u = sum_j v_j mu_j d_j through its own crosscoder; presence = the scaled raw L11 states of both "
           f"models projected onto u, at {len(X)} held-out positions (half human, half rollout). Per seed-0 family, the seed-1 "
           f"family of the same model with the best correlation on half the positions; the correlation shown is on the other "
           f"half. Null: {a.null_sets} sets of fake seed-1 families (each real one's weights on rate-matched random latents), "
           "the same selection; its 95th percentile per family.", ""]
    rep = {}
    for model in a.models.split(","):
        F0, mu0 = families(a.tag0, model)
        F1, mu1 = families(a.tag1, model)
        if not F0 or not F1:
            out += [f"## {model}", "", f"no families ({len(F0)} in seed 0, {len(F1)} in seed 1)", ""]
            continue
        U0, U1 = directions(F0, mu0, W[0]), directions(F1, mu1, W[1])
        P0, P1 = Xf[0] @ U0.reshape(len(F0), -1).T, Xf[1] @ U1.reshape(len(F1), -1).T
        j, r = best_match(P0, P1, sel)
        nul = []
        for _ in range(a.null_sets):
            fake = [dict(latents=[int(rng.choice(pool[int(dec[x])])) for x in f["latents"]], weights=f["weights"]) for f in F1]
            Pf = Xf[1] @ directions(fake, mu1, W[1]).reshape(len(F1), -1).T
            nul.append(best_match(P0, Pf, sel)[1])
        n95 = np.quantile(np.stack(nul), 0.95, axis=0)
        cos = np.array([float(U0[i].ravel() @ U1[j[i]].ravel() / (np.linalg.norm(U0[i]) * np.linalg.norm(U1[j[i]]) + 1e-12))
                        for i in range(len(F0))])
        per = {}
        for m, k in part.items():
            q0 = Xs[0][:, k].numpy() @ U0[:, k].T
            q1 = Xs[1][:, k].numpy() @ U1[:, k].T
            per[m] = (zcols(q0[~sel]) * zcols(q1[~sel])[:, j]).mean(0)
        order = sorted(range(len(F0)), key=lambda i: (-F0[i]["recurrence"], -F0[i]["persistence"]))
        top = order[:a.top]
        above = r > n95
        out += [f"## {model}", "",
                f"{len(F0)} seed-0 families, {len(F1)} seed-1. Held-out correlation with the best seed-1 family: median "
                f"{np.median(r):.2f} (null 95th, median over families: {np.median(n95):.2f}); above their null 95th: "
                f"{above.sum()} ({above.mean():.0%}; chance 5%). The top {len(top)} by recurrence: median {np.median(r[top]):.2f}, "
                f"above the null {above[top].sum()}.", "",
                "| # | k | seed-0 latents (weight) | recurrence | matched seed-1 family (k; latents) | its recurrence | correlation "
                "| null 95th | u cosine | S part | W part |", "|---|---|---|---|---|---|---|---|---|---|---|"]
        for rank, i in enumerate(top):
            f, g = F0[i], F1[j[i]]
            lat = lambda f: ", ".join(f"{x} ({w:.2f})" for w, x in sorted(zip(f["weights"], f["latents"]), reverse=True)[:5])
            out.append(f"| {rank + 1} | {f['k']} | {lat(f)} | {f['recurrence']:.1%} | {g['k']}; {lat(g)} | {g['recurrence']:.1%} | "
                       f"{r[i]:.2f} | {n95[i]:.2f} | {cos[i]:.2f} | {per['S'][i]:.2f} | {per['W'][i]:.2f} |")
        out.append("")
        rep[model] = [dict(family=i, k=F0[i]["k"], latents=F0[i]["latents"], match=int(j[i]), corr=float(r[i]),
                           null95=float(n95[i]), u_cos=float(cos[i]), S_part=float(per["S"][i]), W_part=float(per["W"][i]))
                      for i in range(len(F0))]
    res = DIV_RES / a.tag0
    res.mkdir(parents=True, exist_ok=True)
    (res / f"concept-seed-{a.tag1}.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    (res / f"concept-seed-{a.tag1}.json").write_text(json.dumps(dict(settings=vars(a), **rep)), encoding="utf-8")
    print("\n".join(out))
    print(f"wrote {res / f'concept-seed-{a.tag1}.md'}")


if __name__ == "__main__":
    main()
