"""A look at chosen divergence.py concepts: where each holds across its window and where it does not, and how often it
fires in S's rollouts against W's at the same positions. CPU, on a divergence run's cached codes.

    python transcend/dynamic/conceptlook.py --tag p16-r1024-T0.4-s0-L11-4k --concepts 4:1193,262 6:1752,603

concept    k:latents, a family of --model's report.json at that k with exactly those latents (its weights from there).
with       the model's branch pairs at that k (its lp pairs, both halves) where the concept holds: v . (z^chosen_tau -
           z^subpar_tau) >= 0.5 at every tau = t..t+k (divergence.py's test). Up to --show, from different positions
           first, the heavier subpar branch first.
without    for each shown position, its pair at the same k where the concept does not hold, nearest in split ply.
           Each pair: the board at the split (after the shared moves), the chosen move against the subpar one with their
           shares there, both lines in SAN with [brackets] on the plies where v . z >= 0.5 in that line, Lichess links.
fires      per position and model (S's rollouts and W's, the model both colours, from the same 50 positions): the share of
           plies (lines weighted by how often they were sampled) where v . z >= 0.5. Binarised two ways: each run's own
           mu (as divergence.py does) and one threshold for both (S's mu), and continuous: the mean of sum_j v_j z_j / mu_j
           (S's mu). Per concept: the mean over positions for each model, S - W with a 95% bootstrap interval over
           positions, and how many positions have S above W.

-> results/transcend/divergence/<tag>/concepts-look.md"""

import argparse
import json
import sys
from pathlib import Path

import chess
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # chess_beyond/
import paths  # noqa: E402  also puts transcend/'s folders on sys.path
import divergence as dv
import oneposition as op
import recurring as rc
import shared as gd


def load_mu(tag, model):
    return np.array(json.loads((dv.RUNS / tag / model / "mu.json").read_text(encoding="utf-8"))["mu"])


def family(tag, model, k, lat):
    F = json.loads((dv.RESULTS / tag / "report.json").read_text(encoding="utf-8"))[model]["families"]
    hit = [f for f in F if f["k"] == k and sorted(f["latents"]) == sorted(lat)]
    if not hit:
        sys.exit(f"no {model} family at k = {k} with latents {lat} in {tag}")
    return max(hit, key=lambda f: f["recurrence"])


def holds(Q, p, v, k, plies):
    rc_, rs_ = p["c"] * (plies + 1), p["s"] * (plies + 1)
    d = (Q[rc_ + p["t"]:rc_ + p["t"] + k + 1].astype(np.float32) - Q[rs_ + p["t"]:rs_ + p["t"] + k + 1].astype(np.float32)) @ v
    return bool((np.asarray(d.todense()).ravel() >= 0.5 - 1e-9).all())


def split_board(root, sans, t):
    b = chess.Board(root["fen"])
    for m in sans[:t - 1]:
        b.push_san(m)
    return b


def marks(Q, q, lat, n, plies):
    """Per ply of line q: which of the concept's latents are on, as letters (a = the first latent, b = the second ...)."""
    Z = Q[q * (plies + 1):(q + 1) * (plies + 1)][:, lat].toarray() > 0
    return {t: "".join(chr(97 + i) for i in np.flatnonzero(Z[t])) for t in range(1, n + 1) if Z[t].any()}


def san_marked(sans, m, root):
    """SAN with move numbers; a ply where a latent is on is [bracketed] with the letters of the latents on."""
    b = chess.Board(root["fen"])
    n, white = b.fullmove_number, b.turn == chess.WHITE
    out = []
    for i, x in enumerate(sans):
        w = white if i % 2 == 0 else not white
        num = n + (i + (0 if white else 1)) // 2
        s_ = (f"{num}." if w else (f"{num}..." if i == 0 else "")) + x
        out.append(f"[{s_}]{m[i + 1]}" if (i + 1) in m else s_)
    return " ".join(out)


def pair_block(label, root, D, Q, p, v, plies):
    b = split_board(root, D[p["c"]]["sans"], p["t"])
    lat = list(v.indices)
    mc = marks(Q, p["c"], lat, len(D[p["c"]]["sans"]), plies)
    ms = marks(Q, p["s"], lat, len(D[p["s"]]["sans"]), plies)
    side = "White" if b.turn == chess.WHITE else "Black"
    return [f"**{label}**: split at ply {p['t']}, {side} to move: chosen **{p['chosen']}** ({p['wc']:.0%} there) vs "
            f"subpar **{p['subpar']}** ({p['ws']:.0%}). `{b.fen()}`", "", "```", str(b), "```", "",
            "| chosen | subpar |", "|---|---|",
            f"| {san_marked(D[p['c']]['sans'], mc, root)} | {san_marked(D[p['s']]['sans'], ms, root)} |",
            f"| [Lichess]({gd.lichess_line(root, D[p['c']]['sans'])}) | [Lichess]({gd.lichess_line(root, D[p['s']]['sans'])}) |", ""]


def fire_rates(tag, model, roots, v, mu_own, mu_s, plies):
    """Per position: (own-mu binary rate, S-mu binary rate, continuous mean), plies weighted by line counts."""
    run = dv.RUNS / tag / model
    out = np.full((len(roots), 3), np.nan)
    scaled = v.toarray().ravel() / np.maximum(mu_s, 1e-12)
    for k in range(len(roots)):
        if not (run / f"pos-{k}.npz").exists():
            continue
        D, P, _, _ = rc.load_pos(run, k)
        lens = np.array([len(d["sans"]) for d in D])
        n = np.array([d["n"] for d in D], float)
        valid = np.concatenate([(np.arange(plies + 1) >= 1) & (np.arange(plies + 1) <= L) for L in lens])
        wrow = np.repeat(n, plies + 1) * valid
        vals = []
        for mu in (mu_own, mu_s):
            z = np.asarray((rc.on_matrix(P, mu, 0.5).astype(np.float32) @ v).todense()).ravel() >= 0.5 - 1e-9
            vals.append((z * wrow).sum() / wrow.sum())
        vals.append((np.asarray(P @ scaled).ravel() * wrow).sum() / wrow.sum())
        out[k] = vals
    return out


PIECES = "PNBRQKpnbrqk"


def boards(tag, model, roots, plies):
    """Every ply's board in the model's rollouts (lines replayed from the root) -> per position: (rows of its code
    matrix, one-hot boards (rows, 12 * 64), side to move after the move (rows,), line weights per row)."""
    run = dv.RUNS / tag / model
    out = {}
    for k in range(len(roots)):
        if not (run / f"pos-{k}.npz").exists():
            continue
        D = json.loads(str(np.load(run / f"pos-{k}.npz")["D"]))
        rows, X, stm, w = [], [], [], []
        for q, d in enumerate(D):
            b = chess.Board(roots[k]["fen"])
            for t, m in enumerate(d["sans"], 1):
                b.push_san(m)
                x = np.zeros(12 * 64, bool)
                for sq, pc in b.piece_map().items():
                    x[PIECES.index(pc.symbol()) * 64 + sq] = True
                rows.append(q * (plies + 1) + t)
                X.append(x)
                stm.append(b.turn == chess.WHITE)
                w.append(d["n"])
        out[k] = (np.array(rows), np.array(X), np.array(stm), np.array(w, float))
    return out


def scan(B, tag, model, mu, lat, plies, top):
    """Weighted phi correlation of each latent (and of 'either on') with each piece-on-square and with White to move,
    over every rollout ply -> lines of text."""
    run = dv.RUNS / tag / model
    Z, X, S, W = [], [], [], []
    for k, (rows, Xk, stm, w) in B.items():
        D, P, _, _ = rc.load_pos(run, k)
        Q = rc.on_matrix(P, mu, 0.5)
        Z.append(Q[rows][:, lat].toarray() > 0)
        X.append(Xk), S.append(stm), W.append(w)
    Z, X, S, W = np.concatenate(Z), np.concatenate(X), np.concatenate(S), np.concatenate(W)
    W = W / W.sum()

    def phi(z, F):
        F = F.astype(np.float64)
        mz, mf = (W * z).sum(), W @ F
        cov = (W * z) @ F - mz * mf
        return cov / np.sqrt(mz * (1 - mz) * mf * (1 - mf) + 1e-12)

    sqname = lambda i: f"{'White' if i // 64 < 6 else 'Black'} {'PNBRQK'[i // 64 % 6]} on {chess.square_name(i % 64)}"
    out = []
    for name, z in [(chr(97 + i), Z[:, i]) for i in range(len(lat))] + [("either", Z.any(1))]:
        f = phi(z, X)
        o = np.argsort(-f)[:top]
        st = phi(z, S[:, None])[0]
        out.append(f"- {name}: on at {(W * z).sum():.1%} of plies; phi with White to move {st:+.2f}; top: "
                   + ", ".join(f"{sqname(i)} {f[i]:+.2f} (on {(W * z * X[:, i]).sum() / max((W * X[:, i]).sum(), 1e-12):.0%} "
                               f"of plies with it, {(W * z * ~X[:, i]).sum() / max((W * ~X[:, i]).sum(), 1e-12):.0%} without)"
                               for i in o))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--concepts", nargs="+", required=True, help="k:latent,latent ...")
    ap.add_argument("--model", default="S", help="whose families and pairs")
    ap.add_argument("--source", default=str(dv.SOURCE))
    ap.add_argument("--plies", type=int, default=16)
    ap.add_argument("--on", type=float, default=0.5)
    ap.add_argument("--show", type=int, default=6)
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--scan-top", type=int, default=4, help="board predicates listed per latent")
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    roots = json.loads((Path(a.source) / "positions.json").read_text(encoding="utf-8"))
    mu = {m: load_mu(a.tag, m) for m in ("S", "W")}
    run = dv.RUNS / a.tag / a.model
    cache = {}
    B = boards(a.tag, a.model, roots, a.plies)

    def pos(k):
        if k not in cache:
            cache[k] = dv.load_on(run, k, mu[a.model], a.on)
        return cache[k]

    out = ["# The candidate concepts: with, without, and S against W", "",
           f"Run {a.tag}, {a.model}'s pairs. With: pairs where v . (z^chosen - z^subpar) >= 0.5 on every ply of the window "
           "t..t+k. Without: a pair at the same position and k where it does not hold, nearest in split ply. [move]ab: the "
           "concept's latents on after that move (a: its first latent, b: its second, as listed in the heading); ply 1 is the "
           "line's first move. With weights 0.5 / 0.5, v . z >= 0.5 when either is on, so 'fires' below counts either.", ""]
    summary = ["## S against W: how often each concept fires", "",
               "Per position, the share of rollout plies where v . z >= 0.5 (lines weighted by how often they were sampled), "
               "each model's own rollouts from the same 50 positions; mean over positions. S - W: 95% bootstrap interval over "
               "positions.", "",
               "| concept | with / pairs | S own mu | W own mu | S - W (own mu), 95% | positions S > W | S, S's mu | W, S's mu "
               "| S - W (S's mu), 95% | continuous S / W | S - W continuous, 95% |",
               "|---|---|---|---|---|---|---|---|---|---|---|"]
    for spec in a.concepts:
        kc, lat = spec.split(":")
        kc, lat = int(kc), [int(x) for x in lat.split(",")]
        f = family(a.tag, a.model, kc, lat)
        v = dv.vec(f["latents"], f["weights"], len(mu[a.model]))
        withs, alls = [], {}
        for k in range(len(roots)):
            lpf = run / f"lp-{k}.json"
            if not lpf.exists():
                continue
            recs = json.loads(lpf.read_text(encoding="utf-8"))["ks"][str(kc)]
            _, _, Q = pos(k)
            for p in recs:
                p["position"], p["holds"] = k, holds(Q, p, v, kc, a.plies)
            alls[k] = recs
            withs += [p for p in recs if p["holds"]]
        npairs = sum(len(r) for r in alls.values())
        name = f"k = {kc}: {' + '.join(f'{chr(97 + i)} = {j} ({x:.2f})' for i, (j, x) in enumerate(zip(v.indices, v.data)))}"
        out += [f"## {name}", "",
                f"Holds at {len(withs)} of {npairs} pairs ({len(withs) / max(npairs, 1):.1%}), at {len({p['position'] for p in withs})} "
                f"positions; recurrence in the report {f['recurrence']:.1%} (null 95th {f['null95']:.1%}).", ""]
        out += ["Board scan (every ply of the rollouts, lines weighted by count): each latent's phi correlation with each piece "
                "on a square and with White to move after the move; 'on X% of plies with it' is the latent's rate given the "
                "piece is there.", ""] + scan(B, a.tag, a.model, mu[a.model], list(v.indices), a.plies, a.scan_top) + [""]
        seen, shown = set(), []
        for p in sorted(withs, key=lambda p: -p["ws"]):
            if p["position"] not in seen:
                seen.add(p["position"])
                shown.append(p)
        shown = shown[:a.show]
        for i, p in enumerate(shown):
            k = p["position"]
            root = roots[k]
            D, _, Q = pos(k)
            out += [f"### {name}: position {k}, pair {i + 1}", ""]
            out += pair_block("with", root, D, Q, p, v, a.plies)
            alt = [q for q in alls[k] if not q["holds"]]
            if alt:
                q = min(alt, key=lambda q: (abs(q["t"] - p["t"]), -q["ws"]))
                out += pair_block("without", root, D, Q, q, v, a.plies)
            else:
                out += ["(every pair at this position holds it)", ""]
        R = {m: fire_rates(a.tag, m, roots, v, mu[m], mu["S"], a.plies) for m in ("S", "W")}
        ok = ~np.isnan(R["S"][:, 0]) & ~np.isnan(R["W"][:, 0])
        cells = []
        for c in range(3):
            dS, dW = R["S"][ok, c], R["W"][ok, c]
            diff = dS - dW
            bs = [diff[rng.integers(0, len(diff), len(diff))].mean() for _ in range(a.boot)]
            lo, hi = np.quantile(bs, [.025, .975])
            fmt = (lambda x: f"{x:.3f}") if c == 2 else (lambda x: f"{x:.2%}")
            cells.append((fmt(dS.mean()), fmt(dW.mean()), f"{fmt(diff.mean())} [{fmt(lo)}, {fmt(hi)}]", int((diff > 0).sum())))
        summary.append(f"| {name} | {len(withs)} / {npairs} | {cells[0][0]} | {cells[0][1]} | {cells[0][2]} | {cells[0][3]} of "
                       f"{ok.sum()} | {cells[1][0]} | {cells[1][1]} | {cells[1][2]} | {cells[2][0]} / {cells[2][1]} | {cells[2][2]} |")
    res = dv.RESULTS / a.tag
    (res / "concepts-look.md").write_text("\n".join(summary + [""] + out) + "\n", encoding="utf-8")
    print("\n".join(summary))
    print(f"wrote {res / 'concepts-look.md'}")


if __name__ == "__main__":
    main()
