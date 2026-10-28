"""Where does a recurring pattern occur? Schut-style search over every position of a manypositions run, with the
pattern's latents, on cached data only.

    python transcend/patternsearch.py --tag p16-r1024-T0.4-s0 --pattern 5

1. score       every position by its own lines (weighted by how often each was sampled): coherence, the mean pairwise
               correlation of the pattern's latents across the lines (do they fire together here?); carry rate, the
               share of lines where at least half of them are on at the same ply. A latent is measurable at a position
               when its fraction of plies varies across the lines (weighted sd >= --min-sd, the rule the groups were
               found by); a position is scored when >= --min-latents of the group's latents are, coherence over those;
               the rest listed as not measurable. (Requiring every latent leaves random groups measurable nowhere.)
2. rank        the positions by coherence, the ones where the pattern was found by grouping marked.
3. agreement   the AUC of coherence for picking out those positions (among the measurable), against --null-groups
               random latent groups of the same size, each latent swapped for one in the same overall-firing decile
               among the latents measurable at >= --min-positions positions, scored the same way.
4. family      the spread of coherence across the measurable positions: high nearly everywhere, a fixed family of
               latents; high at some and low at others, situational.
5. read        the top-ranked positions the grouping missed, with how sharp they are (plies with a bare king, <= 1
               shield pawn on either side, and with check) against all positions.

-> results/transcend/manypositions/<tag>/search-<pattern>.md, .json"""

import argparse
import json
import sys
from pathlib import Path

import chess
import numpy as np
from scipy import sparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import graphdiff as gd
import manypositions as mp
import oneposition as op


def shield(b, color):
    """Own pawns on the three files around the king, in the two ranks in front of it."""
    k = b.king(color)
    f, r = chess.square_file(k), chess.square_rank(k)
    d = 1 if color == chess.WHITE else -1
    n = 0
    for ff in (f - 1, f, f + 1):
        for rr in (r + d, r + 2 * d):
            if 0 <= ff < 8 and 0 <= rr < 8:
                p = b.piece_at(chess.square(ff, rr))
                n += bool(p and p.piece_type == chess.PAWN and p.color == color)
    return n


def sharpness(D, w, fen):
    """Weighted shares of plies with a bare king (either side) and with check."""
    s = np.zeros(3)
    for q, d in enumerate(D):
        b = chess.Board(fen)
        for u in d["moves"]:
            b.push(chess.Move.from_uci(u))
            s += w[q] * np.array([min(shield(b, chess.WHITE), shield(b, chess.BLACK)) <= 1, b.is_check(), 1])
    return s[0] / s[2], s[1] / s[2]


def auc(score, label):
    """The probability that a labelled position outranks an unlabelled one (ties half)."""
    pos, neg = score[label], score[~label]
    if not len(pos) or not len(neg):
        return float("nan")
    return float(((pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()) / (len(pos) * len(neg)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tag", default="p16-r1024-T0.4-s0", help="the manypositions run")
    ap.add_argument("--pattern", required=True, help="the pattern's name in that run's report")
    ap.add_argument("--min-sd", type=float, default=0.05, help="a latent is measurable at a position when its weighted sd is >= this")
    ap.add_argument("--null-groups", type=int, default=200)
    ap.add_argument("--min-latents", type=int, default=3, help="a position is scored when at least this many of the group's "
                    "latents are measurable there (coherence over those)")
    ap.add_argument("--min-positions", type=int, default=5, help="null latents: measurable at at least this many positions")
    ap.add_argument("--show", type=int, default=8, help="top-ranked positions the grouping missed, to read")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    run, res = mp.RUNS / a.tag, mp.RESULTS / a.tag
    rep = json.loads((res / "report.json").read_text(encoding="utf-8"))
    pat = next(p for p in rep["patterns"] if p["name"] == a.pattern)
    roots = json.loads((run / "positions.json").read_text(encoding="utf-8"))
    plies, K = rep["settings"]["plies"], len(rep["positions"])
    L = np.array(pat["latents"])
    found = np.zeros(K, bool)
    found[pat["positions"]] = True
    rng = np.random.default_rng(a.seed)

    def load(k):
        z = np.load(run / f"pos-{k}.npz")
        D = json.loads(str(z["D"]))
        P = sparse.csr_matrix((z["data"], z["indices"], z["indptr"]), shape=tuple(z["shape"]))
        w = np.array([d["n"] for d in D], float)
        return D, P, w / w.sum()

    # the overall firing deciles for the null (step 3), among latents measurable at >= --min-positions positions
    share, meas = np.zeros(0), np.zeros(0)
    for k in range(K):
        D, P, w = load(k)
        X = mp.x_of(P, D, plies, P.shape[1])
        f = w @ (X > 0)
        v = (np.sqrt(w @ (X - w @ X) ** 2) >= a.min_sd).astype(float)
        share, meas = (f, v) if not len(share) else (share + f, meas + v)
    share /= K
    live = np.flatnonzero((share > 0) & (meas >= a.min_positions))
    dec = np.searchsorted(np.quantile(share[live], np.linspace(0, 1, 11)[1:-1]), share)
    pool = {b: live[dec[live] == b] for b in np.unique(dec[live])}
    groups = [L] + [np.array([rng.choice([x for x in pool[dec[j]] if x not in L] or pool[dec[j]]) for j in L])
                    for _ in range(a.null_groups)]

    # step 1: score every position, the pattern and the null groups alike
    coh = np.full((len(groups), K), np.nan)
    carry = np.full(K, np.nan)
    sharp = np.zeros((K, 2))
    for k in range(K):
        D, P, w = load(k)
        X = mp.x_of(P, D, plies, P.shape[1])
        sd = np.sqrt(w @ (X - w @ X) ** 2)
        for gi, g in enumerate(groups):
            gm = g[sd[g] >= a.min_sd]                                  # the measurable ones here
            if len(gm) >= a.min_latents:
                R = op.wcorr(X[:, gm], w)
                coh[gi, k] = float(R[np.triu_indices(len(gm), 1)].mean())
        if np.isfinite(coh[0, k]):
            on = [((P[q * (plies + 1):(q + 1) * (plies + 1)][:, L].toarray() > 0).mean(1) >= 0.5)[1:].any() for q in range(len(D))]
            carry[k] = float(w @ np.array(on))
        sharp[k] = sharpness(D, w, roots[k]["fen"])
        print(f"\r  scored {k + 1}/{K} positions", end="", flush=True)
    print()

    # steps 2-4
    m = np.isfinite(coh[0])
    a_real = auc(coh[0, m], found[m])
    a_null = []
    for gi in range(1, len(groups)):
        mg = np.isfinite(coh[gi])
        if mg.sum() >= 5 and found[mg].any() and (~found[mg]).any():
            a_null.append(auc(coh[gi, mg], found[mg]))
    a_null = np.array(a_null)
    print(f"  pattern measurable at {m.sum()} positions ({found[m].sum()} found); random groups measurable at >= 5: "
          f"{len(a_null)} of {len(groups) - 1}; their measurable positions: median {np.median(np.isfinite(coh[1:]).sum(1)):.0f}", flush=True)
    order = [k for k in np.argsort(-np.nan_to_num(coh[0], nan=-9)) if m[k]]
    hi = np.nanmedian([coh[0, k] for k in order])
    out = [f"# Where pattern {a.pattern} occurs: a search over all {K} positions", "",
           f"Latents {', '.join(map(str, L))}; found by grouping at {found.sum()} positions ({', '.join(str(k + 1) for k in np.flatnonzero(found))}). "
           f"Scored where >= {a.min_latents} of its latents are measurable (weighted sd >= {a.min_sd}; coherence over those): {m.sum()} positions, {found[m].sum()} of the {found.sum()} among them; "
           f"not measurable: {', '.join(str(k + 1) for k in np.flatnonzero(~m)) or '-'}.", "",
           "## Agreement", "",
           f"AUC of coherence for picking out the positions where grouping found it: **{a_real:.2f}**; {len(a_null)} random latent "
           f"groups of the same size and overall firing rates: median {np.median(a_null):.2f}, 95th percentile "
           f"{np.quantile(a_null, 0.95):.2f}; the pattern beats {(a_null < a_real).mean():.0%} of them.", "",
           "## Family or situational", "",
           f"Coherence across the {m.sum()} measurable positions: median {np.nanmedian(coh[0, m]):.2f}, 10th percentile "
           f"{np.nanquantile(coh[0, m], 0.1):.2f}, 90th {np.nanquantile(coh[0, m], 0.9):.2f}; below 0.1 at "
           f"{(coh[0, m] < 0.1).sum()} positions, above 0.3 at {(coh[0, m] > 0.3).sum()}. The same random groups, median coherence "
           f"{np.nanmedian(coh[1:]):.2f}.", "",
           "## Positions by coherence", "",
           f"Sharpness for comparison: over all {K} positions, bare-king plies median {np.median(sharp[:, 0]):.0%}, checks "
           f"{sharp[:, 1].mean():.1%} on average.", "",
           "| rank | position | coherence | carry rate | found by grouping | bare-king plies | checks | S's top moves |",
           "|---|---|---|---|---|---|---|---|"]
    for i, k in enumerate(order):
        out.append(f"| {i + 1} | {k + 1} | {coh[0, k]:.2f} | {carry[k]:.0%} | {'yes' if found[k] else ''} | {sharp[k, 0]:.0%} | "
                   f"{sharp[k, 1]:.1%} | {', '.join(f'{s} {q:.0%}' for s, q in roots[k]['top'][:3])} |")
    missed = [k for k in order if not found[k]][:a.show]
    out += ["", f"## The top-ranked positions grouping missed", "",
            f"Their bare-king plies: mean {np.mean(sharp[missed, 0]):.0%} (all positions {sharp[:, 0].mean():.0%}, the {found.sum()} found "
            f"{sharp[found, 0].mean():.0%}); checks {np.mean(sharp[missed, 1]):.1%} (all {sharp[:, 1].mean():.1%}, found "
            f"{sharp[found, 1].mean():.1%}).", ""]
    for k in missed:
        r = roots[k]
        out.append(f"- position {k + 1}, coherence {coh[0, k]:.2f}: `{r['fen']}` ({r['band']} game {r['game']}); bare king "
                   f"{sharp[k, 0]:.0%}, checks {sharp[k, 1]:.1%}; [the position on Lichess]({gd.lichess_line(r, [])})")
    (res / f"search-{a.pattern}.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    (res / f"search-{a.pattern}.json").write_text(json.dumps(dict(
        pattern=a.pattern, latents=L.tolist(), found=np.flatnonzero(found).tolist(), coherence=coh[0].tolist(),
        carry=carry.tolist(), auc=a_real, auc_null=a_null.tolist(), sharpness=sharp.tolist()), default=float, indent=1))
    print(f"AUC {a_real:.2f} (random groups: median {np.median(a_null):.2f}, 95th percentile {np.quantile(a_null, 0.95):.2f}); "
          f"measurable at {m.sum()} positions; wrote {res / f'search-{a.pattern}.md'}")


if __name__ == "__main__":
    main()
