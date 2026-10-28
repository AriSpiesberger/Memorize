"""Concepts inside one model's rollouts from a single position: S only, no W, no position clustering, no deflation,
no merging. A concept is a pattern: a set of latents that fire together across rollouts.

    python transcend/oneposition.py --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal

1. data       one middlegame position from a held-out game with several plausible moves for S (the highest-entropy
              candidate among --candidates whose top move is <= 50% and with >= 3 moves >= 10%), --rollouts rollouts
              of S from it (--plies plies, temperature --temperature, S plays both colours), every position through the
              crosscoder; a rollout is, per latent, the share of its plies where the latent fires, and a latent fires
              in a rollout when it fires at one of its plies at least. Latents firing in 5-95% of the rollouts are
              kept. Two halves: A (fit) and B (check).
2. planted    on a copy of half A, patterns planted without changing any latent's values: each chosen latent's values
              reordered across the rollouts so its highest land in a chosen set (its rate unchanged, only the alignment
              between latents changes); latents not already correlated (|r| < 0.1 with each other). Concept 1: 5
              latents aligned in a random 30% of the rollouts; concept 2: 5 latents sharing one with concept 1, in a
              different 20% (the shared latent's highest values in both sets). Steps 3-4 blind. Pass, fixed in
              advance: each planted concept matched by a found group containing >= 3 of its 5 latents, at least half of
              the group planted latents. If it fails: report and stop.
3. groups     correlations of every pair of latents over half A's rollouts (one position: no position confound);
              null: every column shuffled independently (keeps every latent, destroys any pattern), --shuffles times,
              each time the largest correlation over all pairs; the threshold is the 95th percentile of those maxima
              (family-wise). Average-linkage clustering (distance 1 - r) cut at the threshold; every group of >= 3
              latents a candidate concept.
4. weights    a rollout carries a group when at least half its latents fire in it; Schut's soft-margin LP on carrying
              against non-carrying rollouts (their pairs), w >= 0, sum(w) <= 1, restricted to the group's latents ->
              weights only (its margin is no evidence: carrying is defined by the same latents).
5. replicate  on half B: the group's mean pairwise correlation above B's own shuffle threshold.
6. moves      natural ground truth, all of batch 1: splits read off the board (the first move; castling, by side; each
              move, pawn pushes marked, played in 10-90% of the rollouts; a queen trade): per replicated group, the
              share of carrying and of other rollouts in each split, and the best-matching split (phi).
7. stability  a second, independent batch from the same position, steps 3-5 again; groups matched by their latents.
8. read       per replicated group: its latents, the share of rollouts carrying it, its best move split, and 5 rollouts
              carrying it and 5 not, in SAN, with the plies where its latents fire marked.

-> results/transcend/oneposition/<tag>/report.md, report.json (rollouts and codes cached in runs/transcend/oneposition/<tag>;
   a rerun with the same --tag reuses them)."""

import argparse
import json
import sys
import time
from pathlib import Path

import chess
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paths
import eval as ev
import graphdiff as gd
from concepts import room
from pgn_model import MAX_MOVE_CHARS, prompt
from pgn_probe import parse_movetext

RUNS = paths.RUNS / "transcend" / "oneposition"
RESULTS = paths.ROOT / "results" / "transcend" / "oneposition"


# ---------------------------------------------------------------- data
def pick_position(a, Sm, dev):
    """The highest-entropy candidate (S's policy) among --candidates held-out middlegame positions with several
    plausible moves: top move <= 50%, >= 3 moves >= 10%."""
    rng = np.random.default_rng(a.seed)
    pop = [json.loads(l) for l in open(a.population, encoding="utf-8")]
    cand = []
    for i in rng.permutation(len(pop)):
        r = pop[i]
        if len(r["prompt"]) + room(a.plies) + MAX_MOVE_CHARS + 1 > Sm.ctx:
            continue
        b = ev.board_of(parse_movetext(r["prompt"])[0])
        if prompt(b) != r["prompt"] or b.is_game_over() or not gd.middlegame(b):
            continue
        cand.append((r, b))
        if len(cand) >= a.candidates:
            break
    legal, lp, _ = gd.policy(Sm, [b for _, b in cand], dev, [r["prompt"] for r, _ in cand], batch=a.batch)
    best = None
    for (r, b), mv, l in zip(cand, legal, lp):
        p = np.exp(l - np.logaddexp.reduce(l))
        if p.max() > 0.5 or (p >= 0.1).sum() < 3:
            continue
        H = float(-(p * np.log(np.maximum(p, 1e-300))).sum())
        if best is None or H > best[0]:
            best = (H, r, b, mv, l)
    if best is None:
        sys.exit("no candidate with several plausible moves: raise --candidates")
    H, r, b, mv, l = best
    p = np.exp(l - np.logaddexp.reduce(l))
    top = sorted(zip(p, mv), key=lambda x: -x[0])[:5]
    print(f"position: {b.fen()} ({r['band']} game {r['game']}); S's entropy {H:.2f}; top moves "
          + ", ".join(f"{b.san(m)} {q:.0%}" for q, m in top), flush=True)
    return dict(prompt=r["prompt"], fen=b.fen(), band=r["band"], game=r["game"], entropy=H,
                top=[(b.san(m), float(q)) for q, m in top]), mv, l


def rollouts(a, root, legal, lp, Sm, dev, seed):
    """--rollouts lines of S from the root, S writing every move."""
    rng = np.random.default_rng(seed)
    b0 = ev.board_of(parse_movetext(root["prompt"])[0])
    L = []
    for k in range(a.rollouts):
        line = dict(root=0, kind="S", r=k, board=b0.copy(), moves=[], sans=[], prompt=root["prompt"])
        gd.advance(line, legal[gd.sample(lp, a.temperature, rng)])
        L.append(line)
    for ply in range(1, a.plies):
        live = [l for l in L if len(l["moves"]) == ply and not l["board"].is_game_over()]
        if live:
            lg, lps, _ = gd.policy(Sm, [l["board"] for l in live], dev, [l["prompt"] for l in live], batch=a.batch)
            for l, mv, p in zip(live, lg, lps):
                gd.advance(l, mv[gd.sample(p, a.temperature, rng)])
    for l in L:
        del l["board"], l["prompt"]
    return L


def encode(a, cc, models, root, L, dev):
    """Per rollout and latent: the share of its plies (after the root) where the latent fires -> (rollouts, latents)
    float32; and which latents fire at which ply, sparse (rollouts * (plies + 1), latents)."""
    from scipy import sparse
    Ld = dict(roots=[dict(prompt=root["prompt"], fen=root["fen"])], lines=L)
    seqs, ends, _, _, _, line_start = gd.positions(Ld)
    st = {m: gd.line_states(models[m], seqs, ends, cc.layer[m], dev, a.max_tokens) for m in (0, 1)}
    rows, cols = [], []
    with torch.no_grad():
        for i in range(0, len(st[0]), 4096):
            f, _ = gd.encode_states(cc, {m: st[m][i:i + 4096].to(dev) for m in (0, 1)})
            nz = (f > 0).nonzero().cpu().numpy()
            rows.append(nz[:, 0] + i)
            cols.append(nz[:, 1])
    rows, cols = np.concatenate(rows), np.concatenate(cols)
    nlat = cc.ck["latents"]
    pos_line = np.repeat(np.arange(len(L)), np.diff(line_start))
    pos_t = np.concatenate([np.arange(n) for n in np.diff(line_start)])
    after = pos_t[rows] >= 1                                            # the root itself is shared by every rollout
    r_, c_ = rows[after], cols[after]
    P = sparse.csr_matrix((np.ones(len(r_), np.float32), (pos_line[r_] * (a.plies + 1) + pos_t[r_], c_)),
                          shape=(len(L) * (a.plies + 1), nlat))
    n = np.maximum(np.diff(line_start) - 1, 1)
    X = np.zeros((len(L), nlat), np.float32)
    np.add.at(X, (pos_line[r_], c_), 1.0)
    return X / n[:, None], P


# ---------------------------------------------------------------- analysis
def corr(X):
    Z = X - X.mean(0)
    sd = np.sqrt((Z ** 2).sum(0))
    return (Z.T @ Z) / np.maximum(np.outer(sd, sd), 1e-12)


def shuffle_threshold(X, n, rng, q=0.95):
    """Family-wise: every column shuffled independently, n times, each time the largest off-diagonal correlation;
    the q-quantile of those maxima."""
    iu = np.triu_indices(X.shape[1], 1)
    mx = []
    for _ in range(n):
        Y = np.take_along_axis(X, rng.random(X.shape).argsort(0), 0)
        mx.append(float(corr(Y)[iu].max()))
    return float(np.quantile(mx, q))


def groups_of(X, thr):
    """Average-linkage clustering of the columns on 1 - r, cut at 1 - thr -> [arrays of column indices], >= 3 each."""
    from scipy.cluster.hierarchy import fcluster, linkage
    from scipy.spatial.distance import squareform
    Dm = np.clip(1 - corr(X), 0, 2)
    np.fill_diagonal(Dm, 0)
    lab = fcluster(linkage(squareform(Dm, checks=False), "average"), t=1 - thr, criterion="distance")
    return [np.flatnonzero(lab == c) for c in np.unique(lab) if (lab == c).sum() >= 3]


def carrying(X, g):
    """A rollout carries a group when at least half its latents fire in it."""
    return (X[:, g] > 0).mean(1) >= 0.5


def mean_r(R, g):
    return float(R[np.ix_(g, g)][np.triu_indices(len(g), 1)].mean())


def weights(X, g, rng, a):
    """Schut's soft-margin LP on carrying-minus-non-carrying pairs, restricted to g -> (columns, weights), or
    uniform weights when the LP has nothing to separate."""
    from scipy import sparse
    fire = carrying(X, g)
    P, N = np.flatnonzero(fire), np.flatnonzero(~fire)
    if len(P) and len(N):
        ii = np.stack(np.meshgrid(P, N, indexing="ij"), -1).reshape(-1, 2)
        if len(ii) > a.max_pairs:
            ii = ii[rng.choice(len(ii), a.max_pairs, replace=False)]
        _, r = gd.maxmin(("g", sparse.csr_matrix(X[ii[:, 0]][:, g] - X[ii[:, 1]][:, g]), np.asarray(g), a.nu, False))
        if r is not None and len(r[0]):
            return np.asarray(r[0]), np.asarray(r[1])
    return np.asarray(g), np.full(len(g), 1 / len(g))


def find(X, a, rng, tag):
    """Steps 3-4 on X (rollouts x kept latents) -> threshold, [dict(group, cols, w, share, r_A)]."""
    t0 = time.time()
    thr = shuffle_threshold(X, a.shuffles, rng)
    R = corr(X)
    out = []
    for g in groups_of(X, thr):
        cols, w = weights(X, g, rng, a)
        out.append(dict(group=g, cols=cols, w=w, share=float(carrying(X, g).mean()), r_A=mean_r(R, g)))
    print(f"  {tag}: shuffle threshold r > {thr:.3f} (family-wise); {len(out)} groups of >= 3 latents "
          f"({time.time() - t0:.0f}s)", flush=True)
    return thr, out


def check(X, cs, a, rng):
    """Step 5 on X: each group's mean pairwise correlation above X's own shuffle threshold."""
    thr = shuffle_threshold(X, a.shuffles, rng)
    R = corr(X)
    for c in cs:
        c["r_check"] = mean_r(R, c["group"])
        c["share_check"] = float(carrying(X, c["group"]).mean())
        c["replicated"] = bool(c["r_check"] > thr)
    return thr


def plant(X, rng):
    """Two planted patterns in a copy of X, no value changed: 9 latents not already correlated (|r| < 0.1 pairwise,
    picked greedily in random order); concept 1 = 5 of them aligned in a random 30% of the rollouts, concept 2 = the
    first of those plus the other 4, aligned in a different 20%. Aligning a latent in a set R: its |R| highest values
    go to R's rollouts (in random order), the rest to the others, so its values and rate are unchanged."""
    X = X.copy()
    n = len(X)
    R0 = corr(X)
    pick = []
    for j in rng.permutation(X.shape[1]):
        if X[:, j].std() > 0 and all(abs(R0[j, k]) < 0.1 for k in pick):
            pick.append(int(j))
            if len(pick) == 9:
                break
    if len(pick) < 9:
        sys.exit("not 9 uncorrelated latents to plant")
    L1, L2 = np.array(pick[:5]), np.array([pick[0]] + pick[5:9])
    perm = rng.permutation(n)
    R1, R2 = perm[:int(0.3 * n)], perm[int(0.3 * n):int(0.5 * n)]

    def align(j, R):
        v = np.sort(X[:, j])[::-1]
        rest = np.setdiff1d(np.arange(n), R)
        X[rng.permutation(R), j] = v[:len(R)]
        X[rng.permutation(rest), j] = v[len(R):]

    for j in pick:
        align(j, np.union1d(R1, R2) if j == pick[0] else (R1 if j in L1 else R2))
    return X, [L1, L2]


def planted_test(XA, a, rng):
    Xp, Ls = plant(XA, rng)
    thr, found = find(Xp, a, rng, "planted")
    Rp = corr(Xp)
    print("  planted latents' mean pairwise r: " + ", ".join(f"concept {c + 1} {mean_r(Rp, L):.3f}" for c, L in enumerate(Ls))
          + f" (threshold {thr:.3f}); their firing rates: "
          + "; ".join(", ".join(f"{(Xp[:, j] > 0).mean():.0%}" for j in L) for L in Ls), flush=True)
    planted_all = set(np.concatenate(Ls).tolist())
    rows, ok = [], True
    for c, L in enumerate(Ls):
        Ls_ = set(L.tolist())
        best, n_good = None, 0
        for f in found:
            gset = set(f["group"].tolist())
            present = len(Ls_ & gset)
            on = len(planted_all & gset) / len(gset)                   # the share of the group that is planted latents
            good = present >= 3 and on >= 0.5
            n_good += good
            if best is None or (good, present, on) > (best["good"], best["present"], best["on"]):
                best = dict(good=good, on=on, present=present, size=len(gset))
        rows.append(dict(concept=c + 1, matched=bool(best and best["good"]), matching=int(n_good),
                         share_planted=best["on"] if best else 0.0, present=best["present"] if best else 0,
                         size=best["size"] if best else 0))
        ok &= bool(best and best["good"])
    return ok, rows, len(found)


def move_splits(L, root):
    """Splits of the rollouts read off the board -> {name: bool array}: the first move; castling, by side; each move
    (pawn pushes marked) played at some ply by 10-90% of the rollouts; a queen trade (both queens gone)."""
    n = len(L)
    out = {}
    first = [l["sans"][0] if l["sans"] else "" for l in L]
    for m in sorted(set(first)):
        v = np.array([f == m for f in first])
        if 0.05 <= v.mean() <= 0.95:
            out[f"first move {m}"] = v
    b0 = chess.Board(root["fen"])
    sides = ("White", "Black")
    cast = {s_: np.zeros(n, bool) for s_ in sides}
    queens = np.zeros(n, bool)
    both_q = len(b0.pieces(chess.QUEEN, chess.WHITE)) > 0 and len(b0.pieces(chess.QUEEN, chess.BLACK)) > 0
    played = {}
    for i, l in enumerate(L):
        b = b0.copy()
        for u, san in zip(l["moves"], l["sans"]):
            mv = chess.Move.from_uci(u)
            side = sides[0] if b.turn == chess.WHITE else sides[1]
            if b.is_castling(mv):
                cast[side][i] = True
            push = b.piece_type_at(mv.from_square) == chess.PAWN and not b.is_capture(mv)
            played.setdefault(f"{side} {san}" + (" (pawn push)" if push else ""), np.zeros(n, bool))[i] = True
            b.push(mv)
        queens[i] = both_q and not b.pieces(chess.QUEEN, chess.WHITE) and not b.pieces(chess.QUEEN, chess.BLACK)
    for s_ in sides:
        if 0.05 <= cast[s_].mean() <= 0.95:
            out[f"{s_} castles"] = cast[s_]
    if 0.05 <= queens.mean() <= 0.95:
        out["queen trade"] = queens
    for k_, v in sorted(played.items(), key=lambda x: -x[1].mean()):
        if 0.1 <= v.mean() <= 0.9:
            out[k_] = v
    return out


def phi(x, y):
    x, y = x.astype(float), y.astype(float)
    return 0.0 if x.std() == 0 or y.std() == 0 else float(np.corrcoef(x, y)[0, 1])


def mark(sans, plies, root):
    """SAN with move numbers, the plies where the group's latents fire in [brackets]."""
    b = chess.Board(root["fen"])
    n, white = b.fullmove_number, b.turn == chess.WHITE
    out = []
    for i, m in enumerate(sans):
        w = white if i % 2 == 0 else not white
        num = n + (i + (0 if white else 1)) // 2
        s = (f"{num}." if w else (f"{num}..." if i == 0 else "")) + m
        out.append(f"[{s}]" if (i + 1) in plies else s)
    return " ".join(out)


def save(res, out, rep):
    (res / "report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    (res / "report.json").write_text(json.dumps(rep, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o), indent=1))
    print(f"wrote {res / 'report.md'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cc-run", default="runs/transcend/crosscoder/everything-3m")
    ap.add_argument("--cc", default="Lfinal")
    ap.add_argument("--strong", default="2400", help="a part of S's name")
    ap.add_argument("--population", default=str(gd.PROBE / "population.jsonl"), help="held-out positions")
    ap.add_argument("--candidates", type=int, default=400, help="held-out middlegame positions to choose the root from")
    ap.add_argument("--rollouts", type=int, default=512, help="rollouts per batch (halves A and B: half each)")
    ap.add_argument("--plies", type=int, default=8)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--min-share", type=float, default=0.05, help="latents firing in at least this share of rollouts ...")
    ap.add_argument("--max-share", type=float, default=0.95, help="... and at most this share")
    ap.add_argument("--shuffles", type=int, default=100)
    ap.add_argument("--nu", type=float, default=0.2, help="soft margin: share of pairs allowed inside it")
    ap.add_argument("--max-pairs", type=int, default=20000, help="carrying/non-carrying pairs per LP at most")
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--max-tokens", type=int, default=300_000)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    from scipy import sparse
    tag = a.tag or f"r{a.rollouts}-s{a.seed}"
    run, res = RUNS / tag, RESULTS / tag
    run.mkdir(parents=True, exist_ok=True)
    res.mkdir(parents=True, exist_ok=True)
    cache = run / "data.npz"
    if cache.exists():
        z = np.load(cache, allow_pickle=True)
        root, batches, Xs = json.loads(str(z["root"])), [json.loads(str(z["L1"])), json.loads(str(z["L2"]))], [z["X1"], z["X2"]]
        Ps = [sparse.csr_matrix((z[f"P{k}_data"], z[f"P{k}_indices"], z[f"P{k}_indptr"]), shape=tuple(z[f"P{k}_shape"])) for k in (1, 2)]
        print(f"reusing {cache}", flush=True)
    else:
        dev = ev.device(a.device)
        cc = gd.load_cc(a.cc_run, a.cc, a.strong, dev)
        models = {m: ev.load(cc.info["models"][m], dev)[0] for m in (0, 1)}
        root, legal, lp0 = pick_position(a, models[cc.s], dev)
        batches, Xs, Ps = [], [], []
        for k in (1, 2):                                               # two independent batches (step 7)
            t0 = time.time()
            L = rollouts(a, root, legal, lp0, models[cc.s], dev, [a.seed, k])
            X, P = encode(a, cc, models, root, L, dev)
            batches.append(L), Xs.append(X), Ps.append(P)
            print(f"batch {k}: {len(L)} rollouts of S, encoded ({time.time() - t0:.0f}s)", flush=True)
        np.savez_compressed(cache, root=json.dumps(root), L1=json.dumps(batches[0]), L2=json.dumps(batches[1]), X1=Xs[0], X2=Xs[1],
                            **{f"P{k + 1}_{f}": getattr(Ps[k], f) for k in (0, 1) for f in ("data", "indices", "indptr")},
                            **{f"P{k + 1}_shape": np.array(Ps[k].shape) for k in (0, 1)})
    rng = np.random.default_rng(a.seed)
    rep = dict(root=root, settings=vars(a), batches=[])
    out = ["# Concepts inside S's rollouts from one position", "",
           f"Position `{root['fen']}` ({root['band']} game {root['game']}); S's entropy there {root['entropy']:.2f}; top moves "
           + ", ".join(f"{m} {p:.0%}" for m, p in root["top"]) + f". {a.rollouts} rollouts of S per batch, {a.plies} plies, "
           f"temperature {a.temperature}; a rollout = per latent, the share of its plies where it fires.", ""]
    reps = []
    for k, (L, X, P) in enumerate(zip(batches, Xs, Ps), 1):
        share = (X > 0).mean(0)
        kk = np.flatnonzero((share >= a.min_share) & (share <= a.max_share))
        perm = np.random.default_rng([a.seed, k, 7]).permutation(len(L))
        A, B = perm[:len(L) // 2], perm[len(L) // 2:]
        XA, XB = X[A][:, kk], X[B][:, kk]
        print(f"batch {k}: {len(kk)} latents firing in {a.min_share:.0%}-{a.max_share:.0%} of rollouts; halves {len(A)} / {len(B)}", flush=True)
        if k == 1:                                                     # step 2, before anything is read
            ok, prow, nf = planted_test(XA, a, rng)
            rep["planted"] = dict(passed=ok, rows=prow, found=nf)
            out += ["## Planted test (half A of batch 1)", "",
                    "No value changed, only alignment: concept 1, 5 latents (not already correlated) aligned in 30% of the "
                    "rollouts; concept 2, 5 latents (one shared with 1) in a different 20%. Pass: each matched by a found group "
                    f"with >= 3 of its 5 latents, at least half of the group planted latents. {nf} groups found on the planted data.", "",
                    "| planted | matched | found groups that match | best group: share planted | its planted latents | its size |",
                    "|---|---|---|---|---|---|"]
            out += [f"| {r['concept']} | {'yes' if r['matched'] else 'no'} | {r['matching']} | {r['share_planted']:.0%} | "
                    f"{r['present']} / 5 | {r['size']} |" for r in prow]
            out += ["", f"**Planted test {'passed' if ok else 'FAILED'}.**", ""]
            print(f"planted test {'passed' if ok else 'FAILED'}: " + "; ".join(
                f"concept {r['concept']}: best group {r['present']}/5 of its latents, {r['share_planted']:.0%} planted, size "
                f"{r['size']}" for r in prow), flush=True)
            if not ok:
                out += ["Stopped here, as fixed in advance. Next: --rollouts 2048 (1,024 per half)."]
                save(res, out, rep)
                return
        thr, cs = find(XA, a, rng, f"batch {k} half A")
        thrB = check(XB, cs, a, rng)
        for c in cs:                                                   # back to latent ids
            c["latents"], c["group_latents"] = kk[c["cols"]].tolist(), kk[c["group"]].tolist()
        cs.sort(key=lambda c: -c["r_A"])
        for i, c in enumerate(cs):
            c["name"] = f"{k}.{i + 1}"
        rk = [c for c in cs if c["replicated"]]
        reps.append(rk)
        out += [f"## Batch {k}: groups", "",
                f"{len(kk)} latents; half A: family-wise shuffle threshold r > {thr:.3f}, {len(cs)} groups of >= 3 latents; "
                f"half B (threshold r > {thrB:.3f}): {len(rk)} replicate.", "",
                "| group | latents | LP weights (top) | share carrying (A / B) | mean r A / B | replicated |",
                "|---|---|---|---|---|---|"]
        for c in cs:
            ws = sorted(zip(c["latents"], c["w"]), key=lambda x: -abs(x[1]))
            out.append(f"| {c['name']} | {', '.join(map(str, c['group_latents']))} | " + ", ".join(f"{j} ({w:.2f})" for j, w in ws[:6])
                       + f" | {c['share']:.0%} / {c['share_check']:.0%} | {c['r_A']:.2f} / {c['r_check']:.2f} | "
                       f"{'yes' if c['replicated'] else 'no'} |")
        out.append("")
        if k == 1 and rk:
            # step 6: natural ground truth, splits read off the board, over all of batch 1
            splits = move_splits(L, root)
            out += ["## Move-defined splits (batch 1, all rollouts)", "",
                    f"{len(splits)} splits: " + ", ".join(f"{nm} ({m.mean():.0%})" for nm, m in list(splits.items())[:40]), "",
                    "| group | carrying | best split (phi) | share of carrying / other rollouts in it | next best |", "|---|---|---|---|---|"]
            for c in rk:
                fire = carrying(X, np.array(c["group_latents"]))
                ph = sorted(((phi(fire, m), nm) for nm, m in splits.items()), key=lambda x: -abs(x[0]))
                c["splits"] = [(nm, v) for v, nm in ph[:5]]
                if ph:
                    v, nm = ph[0]
                    m = splits[nm]
                    c["best_split"] = (nm, v, float(m[fire].mean()), float(m[~fire].mean()))
                    out.append(f"| {c['name']} | {fire.mean():.0%} | {nm} ({v:+.2f}) | {m[fire].mean():.0%} / {m[~fire].mean():.0%} | "
                               + ", ".join(f"{n2} ({v2:+.2f})" for v2, n2 in ph[1:3]) + " |")
            out.append("")
            # step 8: read them from their rollouts
            for c in rk:
                g = np.array(c["group_latents"])
                fire = carrying(X, g)
                w_ = np.zeros(X.shape[1])
                w_[c["latents"]] = c["w"]
                score = X @ w_
                yes = np.flatnonzero(fire)[np.argsort(-score[fire])][:5]
                no = np.flatnonzero(~fire)[np.argsort(score[~fire])][:5]
                bs = c.get("best_split")
                out += [f"### Group {c['name']}: latents {', '.join(map(str, c['group_latents']))}; carried by {fire.mean():.0%} of "
                        "batch 1's rollouts" + (f"; best move split: {bs[0]} (phi {bs[1]:+.2f}; {bs[2]:.0%} of carrying rollouts, "
                                                f"{bs[3]:.0%} of the others)" if bs else ""), ""]
                for nm, ids in (("carrying it", yes), ("not carrying it", no)):
                    out += [f"{nm}:", ""]
                    for q in ids:
                        pl = P[q * (a.plies + 1):(q + 1) * (a.plies + 1)][:, g].toarray()
                        plies = {t for t in range(1, a.plies + 1) if pl[t].sum() > 0}
                        out.append(f"- {mark(L[q]['sans'], plies, root)}  ([Lichess]({gd.lichess_line(root, L[q]['sans'])}))")
                    out.append("")
        rep["batches"].append(dict(threshold_A=thr, threshold_B=thrB, latents=len(kk), groups=len(cs), replicated=len(rk),
                                   items=[{x: c.get(x) for x in ("name", "group_latents", "latents", "w", "share", "share_check",
                                                                 "r_A", "r_check", "replicated", "splits", "best_split")} for c in cs]))
    # step 7: stability, batch 1's replicated groups in batch 2
    c1, c2 = reps
    out += ["## Stability: batch 1's replicated groups in batch 2 (an independent batch from the same position)", "",
            "| batch 1 group | best batch 2 match | Jaccard of latents | shared latents |", "|---|---|---|---|"]
    hits = 0
    for c in c1:
        s1 = set(c["group_latents"])
        jac, d = max(((len(s1 & set(d["group_latents"])) / len(s1 | set(d["group_latents"])), d) for d in c2),
                     key=lambda x: x[0], default=(0.0, None))
        hits += jac >= 0.3
        out.append(f"| {c['name']} | {d['name'] if d else '-'} | {jac:.2f} | {len(s1 & set(d['group_latents'])) if d else 0} |")
    out += ["", f"{hits} of {len(c1)} reappear (Jaccard >= 0.3); batch 2 has {len(c2)} replicated groups.", ""]
    rep["stability"] = dict(reappear=int(hits), of=len(c1), batch2=len(c2))
    print(f"stability: {hits} of {len(c1)} batch-1 groups reappear in batch 2 (Jaccard >= 0.3)", flush=True)
    save(res, out, rep)


if __name__ == "__main__":
    main()
