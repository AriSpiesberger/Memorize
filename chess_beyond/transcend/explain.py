"""Scored explanations for crosscoder latents, in plain chess terms, and what the layer knows.

    python transcend/explain.py --cc-run runs/transcend/crosscoder/everything-3m --cc L15

The claim being tested: the latents (and the concept paths built from them in concepts.py) are
tangible chess ideas. An explanation is a fact, or two joined by "and", and it is only as good as
its score: how well it predicts, on positions it was not chosen on, when the latent fires. Three
kinds of facts:
  board facts (predicates.py)   what is on the board: a hanging piece, a pin, a check, a passed pawn
  square facts (predicates.py)  which piece stands where, and where their last move went, seen from
                                the side to move ("our king on g1": castled short, either colour)
  skill facts (skill.py)        what it takes: only one good move, a best move found only at depth,
                                a sound sacrifice, an answer to a threat, a blunder, a move 1100s
                                rarely play but 2000+ players do (Stockfish and Maia-2)
Facts are yes/no, but a strong player's knowledge is also a matter of degree (how good is this
position?), so each latent also gets an engine link: when it fires, how much better or worse the side
to move stands by Stockfish than the pieces on the board predict (a linear fit from the board and
square facts), measured on held-out games.

  1. facts    --n positions sampled from the crosscoder's stored ones (rows.npy); board facts on
              every CPU core, each worker with its own Stockfish (--depth), then Maia-2 on the GPU.
              Cached in <cc-run>/<cc>/facts.npz with the raw engine numbers (--no-engine: board
              facts only); another crosscoder of the same run reuses it, as the positions are the
              same. Square facts are cheap and cached in <cc-run>/squares.npz.
  2. counts   the positions are encoded with the crosscoder from the stored model states (no chess
              model is loaded). Pass 1: per latent, how often it fires with each fact, and the
              engine numbers where it fires. Pass 2: each latent's --pair-from best single facts
              (on the fit half) are paired, and the pairs counted.
  3. score    games are split in two halves. On the "fit" half each latent's explanation is the
              fact or pair with the best F1 (it must both cover the latent's firings and not fire
              much without it); precision, recall and F1 are then measured on the "test" half,
              next to the F1 the same fact would get if it were unrelated to the latent (null).
              Also listed: facts nearly always true when the latent fires (recall >= 0.8) that are
              much rarer otherwise (lift >= 2), and the engine link.
  4. layer    what the layer knows as a whole: linear probes from each model's states at this layer
              to Stockfish's numbers (evaluation, threat, only-move gap), next to the board and
              square facts alone, and how much the crosscoder's engine-linked latents add, split by
              which model uses them.

-> results/transcend/crosscoder/<run>/<cc>/explanations.jsonl (one line per latent) and explain.md.
   concepts.py graph picks the explanations up for its node and path cards.
"""
import argparse
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))          # transcend/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))      # chess_beyond/
import chess
import eval as ev                                                 # device
import predicates
import skill
from crosscoder import RESULTS, Corpus, CrossCoder, load_sources, position, source_name, stack

NAMES = predicates.NAMES + skill.NAMES                             # the facts cached in facts.npz
ALL = NAMES + predicates.SQUARE_NAMES                              # every fact an explanation can use
TEXT = {**predicates.TEXT, **skill.TEXT, **predicates.SQUARE_TEXT}
NUMBERS = ["wp", "gap", "found_at", "threat", "loss", "gives"]     # engine numbers kept beside the facts
# engine targets a latent's firing is compared with: the evaluation, and the evaluation and threat
# beyond what the board and square facts predict (all in win-% points for the side to move)
TARGETS = ["eval", "eval_beyond_board", "threat_beyond_board", "gap"]
LINK, LINK_Z = 5.0, 4.0                                            # engine-linked: |shift| >= 5 points, z >= 4

_corpus = _engine = None


def _init(folders, depth):
    global _corpus, _engine
    _corpus = Corpus(folders)
    _engine = skill.Annotator(depth=depth) if depth else None


def _facts(rows):
    """Board facts, engine numbers and (fen, move, best) for a chunk of (folder, game, ply, char)
    rows, in a worker process."""
    P = np.zeros((len(rows), len(predicates.NAMES)), dtype=bool)
    eng, pos = [], []
    for k, row in enumerate(rows):
        b, nxt, _ = position(_corpus, row)
        try:
            mv = b.parse_san(nxt)
        except ValueError:
            mv = None
        P[k] = predicates.features(b, mv)
        e = _engine.annotate(b, mv) if _engine else None
        eng.append(e)
        pos.append((b.fen(), mv.uci() if mv else None, e["best"] if e else None))
    return P, eng, pos


def _squares(rows):
    return np.array([predicates.squares(position(_corpus, row)[0]) for row in rows], dtype=bool)


def cached(paths, idx, ok=lambda z: True):
    """The first of these .npz caches that was made for these positions, or None."""
    for p in paths:
        if p.exists():
            z = np.load(p)
            if np.array_equal(z["idx"], idx) and ok(z):
                print(f"  cached in {p}", flush=True)
                return z
    return None


def facts(rows, idx, folders, caches, workers, depth):
    """(positions, len(NAMES)) bools and the engine numbers, computed once and cached in caches[0]."""
    z = cached(caches, idx, lambda z: list(z["names"]) == NAMES and int(z["depth"]) == depth)
    if z is not None:
        return z["P"], z["numbers"], z["maia"]
    chunks = np.array_split(rows[idx], max(1, len(idx) // 200))
    Ps, engs, poss, t0 = [], [], [], time.time()
    with Pool(workers, initializer=_init, initargs=(folders, depth)) as pool:
        for P, eng, pos in pool.imap(_facts, chunks):
            Ps.append(P)
            engs += eng
            poss += pos
            done = len(engs)
            rate = done / (time.time() - t0)
            print(f"\r  board{' and engine' if depth else ''} facts: {done}/{len(idx)} positions, {rate:.0f}/s, "
                  f"{(len(idx) - done) / max(rate, 1e-9) / 60:.0f} min left   ", end="", flush=True)
    print()
    if depth:
        print("  Maia-2: how likely 1100 and 2000+ players are to play each move", flush=True)
        maia = skill.maia_probs([(chess.Board(f), chess.Move.from_uci(m) if m else None,
                                  chess.Move.from_uci(bm) if bm else None) for f, m, bm in poss])
        S = np.array([skill.facts(e, m) for e, m in zip(engs, maia)], dtype=bool)
        numbers = np.array([[e.get(k, np.nan) if e else np.nan for k in NUMBERS] for e in engs], dtype=np.float32)
    else:
        maia = np.full((len(idx), 3), np.nan, dtype=np.float32)
        S = np.zeros((len(idx), len(skill.NAMES)), dtype=bool)
        numbers = np.full((len(idx), len(NUMBERS)), np.nan, dtype=np.float32)
    P = np.concatenate([np.concatenate(Ps), S], 1)
    np.savez(caches[0], idx=idx, names=np.array(NAMES), depth=depth, P=P, numbers=numbers, maia=maia)
    return P, numbers, maia


def refresh(P, numbers):
    """Recompute, from the cached engine numbers, the skill facts that need nothing else, so a cache made
    before skill.py's definitions changed stays right (the undecided-position condition)."""
    n = {k: numbers[:, NUMBERS.index(k)] for k in NUMBERS}
    has_move = ~np.isnan(n["loss"])
    with np.errstate(invalid="ignore"):
        undecided = (n["wp"] >= skill.OPEN[0]) & (n["wp"] <= skill.OPEN[1])
        keep = has_move & undecided & (n["loss"] <= skill.KEEP)
        col = lambda f: len(predicates.NAMES) + skill.NAMES.index(f)
        P[:, col("move_sound_sacrifice")] = keep & (n["gives"] >= skill.SAC)
        P[:, col("move_meets_threat")] = keep & (n["threat"] >= skill.THREAT)
    return P


def square_facts(rows, idx, folders, cache, workers):
    """(positions, len(SQUARE_NAMES)) bools, cached."""
    z = cached([cache], idx)
    if z is not None:
        return z["Q"]
    with Pool(workers, initializer=_init, initargs=(folders, 0)) as pool:
        Q = np.concatenate(list(pool.imap(_squares, np.array_split(rows[idx], max(1, len(idx) // 500)))))
    np.savez_compressed(cache, idx=idx, Q=Q)
    return Q


def ridge(X, y, fit, lam=10.0):
    """Linear fit of y (one target, or several as columns) on X (standardised, ridge) on the fit rows
    -> predictions for every row."""
    X = torch.as_tensor(np.asarray(X), dtype=torch.float64)
    fit = torch.from_numpy(np.asarray(fit))
    mu, sd = X[fit].mean(0), X[fit].std(0) + 1e-3
    Z = torch.cat([(X - mu) / sd, torch.ones(len(X), 1, dtype=torch.float64)], 1)
    A, yt = Z[fit], torch.as_tensor(np.asarray(y), dtype=torch.float64)[fit]
    w = torch.linalg.solve(A.T @ A + lam * torch.eye(Z.shape[1], dtype=torch.float64), A.T @ yt)
    return (Z @ w).numpy()


def r2(pred, y):
    return float(1 - np.mean((pred - y) ** 2) / np.var(y))


def auc(score, y):
    order = np.argsort(score)
    rank = np.empty(len(score))
    rank[order] = np.arange(len(score))
    pos = y.sum()
    return float((rank[y].sum() - pos * (pos - 1) / 2) / max(pos * (len(y) - pos), 1))


def target_stats(Y, halves):
    """Per half: each engine target's total, count of positions that have it, and spread."""
    out = {}
    for k, f in (("tot", lambda y: np.nansum(y, 0)), ("cnt", lambda y: (~np.isnan(y)).sum(0)),
                 ("sd", lambda y: np.nan_to_num(np.nanstd(y, 0), nan=1.0) + 1e-6)):
        out[k] = torch.tensor(np.stack([f(Y[halves == h]) for h in (0, 1)]), dtype=torch.float32)
    return out


@torch.no_grad()
def counts(cc_run, ck, idx, halves, P, Y, rel, dev, batch, pair_from, keep, min_pred):
    """Per half (0 fit, 1 test). Pass 1: latent firings, single-fact counts and co-occurrences, and
    sums of the engine targets Y where each latent fires. Pass 2: each latent's pair_from best facts
    on the fit half, paired and counted; and, for the layer's probe, the firings of the latents most
    tied to the evaluation beyond the board: keep // 3 from each group by relative decoder norm rel
    (mostly the first model, both, mostly the second), so the groups compare at equal size."""
    sources = [tuple(s) for s in ck["sources"]]
    cc = CrossCoder(len(sources), ck["d"], ck["latents"], ck["k"]).to(dev)
    cc.load_state_dict(ck["state"])
    scales = ck["scales"].to(dev)
    arrs = load_sources(cc_run, sources)
    F, Lt = P.shape[1], ck["latents"]
    Pt, Ht = torch.from_numpy(P).to(dev), torch.from_numpy(halves).to(dev)
    V = torch.from_numpy(~np.isnan(Y)).float().to(dev)
    Yt = torch.from_numpy(np.nan_to_num(Y)).float().to(dev)
    c = dict(tp=torch.zeros((2, Lt, F), device=dev), fires=torch.zeros((2, Lt), device=dev),
             pred=torch.zeros((2, F), device=dev), gram=torch.zeros((2, F, F), device=dev),
             ysum=torch.zeros((2, Lt, Y.shape[1]), device=dev), ycnt=torch.zeros((2, Lt, Y.shape[1]), device=dev),
             n=torch.zeros(2, device=dev), **{k: v.to(dev) for k, v in target_stats(Y, halves).items()})

    def firing(s):
        f, _, _ = cc.encode(stack(arrs, idx[s:s + batch], scales, dev))
        return f > 0

    t0 = time.time()
    for s in range(0, len(idx), batch):
        on, p = firing(s).float(), Pt[s:s + batch].float()
        for h in (0, 1):
            m = (Ht[s:s + batch] == h).float()[:, None]
            om, pm = on * m, p * m
            c["tp"][h] += om.T @ p
            c["fires"][h] += om.sum(0)
            c["pred"][h] += pm.sum(0)
            c["gram"][h] += pm.T @ p
            c["ysum"][h] += om.T @ (Yt[s:s + batch] * V[s:s + batch])
            c["ycnt"][h] += om.T @ V[s:s + batch]
            c["n"][h] += m.sum()
        print(f"\r  pass 1: {min(s + batch, len(idx))}/{len(idx)} positions, {(time.time() - t0) / 60:.1f} min   ",
              end="", flush=True)
    print()

    # each latent's best single facts on the fit half, paired
    fit1 = 2 * c["tp"][0] / (c["fires"][0][:, None] + c["pred"][0][None, :]).clamp_min(1)
    fit1[:, c["pred"][0] < min_pred] = -1
    cand = fit1.topk(pair_from, dim=1).indices                        # (latents, pair_from)
    del fit1
    ia, ib = torch.triu_indices(pair_from, pair_from, 1, device=dev)
    c["A"], c["B"] = cand[:, ia], cand[:, ib]                         # (latents, pairs)
    c["tp2"] = torch.zeros((2, Lt, len(ia)), device=dev)
    # the latents most tied to the evaluation beyond the board, on the fit half (by |z|)
    link = engine_link(c, 0, TARGETS.index("eval_beyond_board"))[1].abs().nan_to_num(0)
    r = torch.as_tensor(rel, device=dev)
    c["kept"] = torch.cat([(link * g).topk(keep // 3).indices for g in (r < 0.4, (r >= 0.4) & (r <= 0.6), r > 0.6)])
    kept_on = np.zeros((len(idx), len(c["kept"])), dtype=bool)
    t0 = time.time()
    for s in range(0, len(idx), batch):
        on = firing(s)
        kept_on[s:s + batch] = on[:, c["kept"]].cpu().numpy()
        pos, lat = on.nonzero(as_tuple=True)
        pb = Pt[s:s + batch]
        hit = (pb[pos[:, None], c["A"][lat]] & pb[pos[:, None], c["B"][lat]]).float()
        h = Ht[s:s + batch][pos]
        for k in (0, 1):
            m = h == k
            c["tp2"][k].index_add_(0, lat[m], hit[m])
        print(f"\r  pass 2: {min(s + batch, len(idx))}/{len(idx)} positions, {(time.time() - t0) / 60:.1f} min   ",
              end="", flush=True)
    print()
    out = {k: v.cpu() for k, v in c.items()}
    out["kept_on"] = kept_on
    return out


def engine_link(c, h, t):
    """Per latent, on half h, target t: (mean where it fires minus where it does not, z of that)."""
    n_on = c["ycnt"][h][:, t]
    s_on = c["ysum"][h][:, t]
    S, N, SD = c["tot"][h][t], c["cnt"][h][t], c["sd"][h][t]
    on = s_on / n_on.clamp_min(1)
    off = (S - s_on) / (N - n_on).clamp_min(1)
    shift = on - off
    z = shift / (SD * (1 / n_on.clamp_min(1) + 1 / (N - n_on).clamp_min(1)).sqrt())
    return on, torch.where(n_on >= 20, z, torch.zeros_like(z)), shift


def score(c, a):
    """One record per latent: its explanation, held-out precision / recall / F1, the null F1, facts that
    nearly always hold when it fires, and its engine link."""
    F = len(ALL)
    tp, fires, pred, n, gram = c["tp"], c["fires"], c["pred"], c["n"], c["gram"]
    A, B, tp2 = c["A"], c["B"], c["tp2"]
    pred2 = torch.stack([gram[h][A, B] for h in (0, 1)])               # (2, latents, pairs)
    fit1 = 2 * tp[0] / (fires[0][:, None] + pred[0][None, :]).clamp_min(1)
    fit1[:, pred[0] < a.min_pred] = -1                                 # too rare to judge
    fit2 = 2 * tp2[0] / (fires[0][:, None] + pred2[0]).clamp_min(1) - 0.02   # a pair must beat one fact clearly
    fit2[pred2[0] < a.min_pred] = -1
    both = torch.cat([fit1, fit2], 1)
    alt = both.topk(4, dim=1)
    links = {t: engine_link(c, 1, k) for k, t in enumerate(TARGETS)}

    def name(j, c_):
        return ALL[c_] if c_ < F else f"{ALL[int(A[j, c_ - F])]}&{ALL[int(B[j, c_ - F])]}"

    out = []
    for j in range(tp.shape[1]):
        r = dict(latent=j, fires_fit=int(fires[0, j]), fires_test=int(fires[1, j]))
        if fires[0, j] < a.min_fires or fires[1, j] < a.min_fires:
            r.update(status="too rare", explanation="", f1=0.0)
            out.append(r)
            continue
        cj = int(alt.indices[j, 0])
        k, pt = (float(tp[1, j, cj]), float(pred[1, cj])) if cj < F else \
                (float(tp2[1, j, cj - F]), float(pred2[1, j, cj - F]))
        ft = float(fires[1, j])
        prec, rec = k / max(pt, 1), k / max(ft, 1)
        f1 = 2 * k / max(ft + pt, 1)
        null = 2 * (ft / n[1]) * pt / max(ft + pt, 1)                 # F1 if the fact ignored the latent
        base = pred[1] / n[1]
        recall_all = tp[1, j] / max(ft, 1)
        always = [(ALL[i], float(recall_all[i]), float(base[i])) for i in torch.nonzero(
                  (recall_all >= 0.8) & (recall_all >= 2 * base)).squeeze(1).tolist()]
        always.sort(key=lambda t: -t[1] / max(t[2], 1e-6))
        nm = name(j, cj)
        r.update(status="explained" if f1 >= a.good else "weak" if f1 >= a.weak else "unexplained",
                 name=nm, explanation=text(nm), precision=prec, recall=rec, f1=f1, f1_null=float(null),
                 alternatives=[[name(j, int(i)), text(name(j, int(i))), float(v)]
                               for i, v in zip(alt.indices[j, 1:], alt.values[j, 1:]) if v > 0],
                 always=[[x, TEXT[x], rc, bs] for x, rc, bs in always[:4]])
        eng = {t: dict(on=float(links[t][0][j]), z=float(links[t][1][j]), shift=float(links[t][2][j])) for t in TARGETS}
        e = eng["eval_beyond_board"]
        r["engine"] = eng
        r["engine_linked"] = bool(abs(e["shift"]) >= LINK and abs(e["z"]) >= LINK_Z)
        r["engine_text"] = (f"the side to move's Stockfish win chance is {eng['eval']['on']:.0f}% when it fires, "
                            f"{e['shift']:+.0f} points from what the pieces on the board predict")
        out.append(r)
    return out


def text(name):
    return " and ".join(TEXT[x] for x in name.split("&"))


def layer_probe(cc_run, ck, idx, fit, test, board_X, numbers, kept, kept_on, rel):
    """What the layer knows: probes from each model's states to Stockfish's numbers, next to the board
    and square facts alone, and what the engine-linked latents add, by which model uses them."""
    info = json.loads((cc_run / "collect.json").read_text())
    wp, gap, threat = (numbers[:, NUMBERS.index(k)] for k in ("wp", "gap", "threat"))
    ok = ~(np.isnan(wp) | np.isnan(gap) | np.isnan(threat))
    fit, test = fit & ok, test & ok
    wp, gap, threat = (np.nan_to_num(x) for x in (wp, gap, threat))
    sharp, decided = gap >= skill.SHARP, (wp < 20) | (wp > 80)

    ys = np.stack([wp, threat, gap, sharp, decided], 1).astype(np.float64)

    def row(X):                                                    # one fit for all five targets
        p = ridge(X, ys, fit)[test]
        return [r2(p[:, 0], wp[test]), r2(p[:, 1], threat[test]), r2(p[:, 2], gap[test]),
                auc(p[:, 3], sharp[test]), auc(p[:, 4], decided[test])]

    rows = [("the board and square facts alone", row(board_X))]
    for m, L in (tuple(s) for s in ck["sources"]):
        X = np.asarray(np.load(cc_run / "acts" / f"{source_name(info['names'][m], L)}.npy", mmap_mode="r")[idx],
                       dtype=np.float32)
        rows.append((f"{info['names'][m]}, layer {L} states", row(X)))
        print(f"  probed {rows[-1][0]}", flush=True)
    r_kept = np.array([rel.get(int(j), 0.5) for j in kept])
    for lab, sel in (("all of them", np.ones(len(kept), bool)), ("used mostly by the first model (r < 0.4)", r_kept < 0.4),
                     ("used by both (0.4-0.6)", (r_kept >= 0.4) & (r_kept <= 0.6)),
                     ("used mostly by the second model (r > 0.6)", r_kept > 0.6)):
        if sel.sum() >= 5:
            rows.append((f"board and square facts + the {int(sel.sum())} engine-linked latents {lab}",
                         row(np.concatenate([board_X, kept_on[:, sel]], 1))))
    return rows


def report(recs, lat, out_dir, a, n_pos, probe, names):
    rel = {r["latent"]: r["rel_norm"] for r in lat}
    scored = [r for r in recs if r["status"] != "too rare"]
    cnt = lambda rs, s: sum(1 for r in rs if r["status"] == s)
    md = ["# Latent explanations", "",
          f"{n_pos} positions, split by game into a fit half (choose each latent's explanation) and a test "
          f"half (score it). An explanation is a board fact, a square fact (predicates.py) or a skill fact "
          f"(skill.py), or two joined by \"and\"; its score is the F1 of predicting when the latent fires, on "
          f"the test half. **explained**: F1 >= {a.good}; **weak**: >= {a.weak}. Latents firing fewer than "
          f"{a.min_fires} times in either half are too rare to score. Squares are named from the side to move's "
          f"side of the board, as if it were White (rank 1 is our back rank).", "",
          f"- {len(recs)} latents, {len(scored)} scored: {cnt(scored, 'explained')} explained "
          f"({100 * cnt(scored, 'explained') / max(len(scored), 1):.0f}%), {cnt(scored, 'weak')} weak, "
          f"{cnt(scored, 'unexplained')} unexplained; {len(recs) - len(scored)} too rare.",
          f"- **engine-linked**: {sum(r.get('engine_linked', False) for r in scored)} latents fire where the side to "
          f"move stands at least {LINK:g} win-% points better or worse, by Stockfish, than the pieces on the board "
          f"predict (z >= {LINK_Z:g}, test half).", ""]
    if probe:
        md += ["## What the layer knows", "",
               "Linear probes (ridge, fit on the fit half, scored on the test half) to Stockfish's numbers for the "
               "position: its evaluation (win % for the side to move), the size of the threat against the side to "
               "move, and the only-move gap (how much worse the second-best move is); and as yes/no, AUC for "
               f"\"only one good move\" (gap >= {skill.SHARP}) and \"decided\" (win % < 20 or > 80). The first row "
               "is what the board and square facts alone allow; the model rows read the models' own states at "
               "this layer; the last rows add the firings of the latents most tied to the evaluation beyond the "
               "board (chosen on the fit half), by which model uses them.", "",
               "| read from | eval R2 | threat R2 | gap R2 | only one good move AUC | decided AUC |",
               "| --- | --- | --- | --- | --- | --- |"]
        md += [f"| {lab} | " + " | ".join(f"{v:.3f}" for v in vals) + " |" for lab, vals in probe]
        md.append("")
    md += ["## By which model uses the latent", "",
           f"relative decoder norm r: ~0 {names[0]} only, ~0.5 both, ~1 {names[1]} only.", "",
           "**uses a skill fact**: of the explained and weak latents, how many explanations include a skill fact "
           "(only move, deep move, sacrifice, threat, blunder, Maia-2 rarity, ...). **square facts**: how many use "
           "a square fact. **engine-linked**: share of scored latents tied to the evaluation beyond the board.", "",
           "| r | scored | explained | weak | median F1 | uses a skill fact | square facts | engine-linked |",
           "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    uses = lambda r, vocab: any(x in vocab for x in r.get("name", "").split("&"))
    for lo, hi, lab in ((0, 0.4, "< 0.4"), (0.4, 0.6, "0.4-0.6"), (0.6, 1.01, ">= 0.6")):
        rs = [r for r in scored if lo <= rel.get(r["latent"], 0.5) < hi]
        if rs:
            ok = [r for r in rs if r["status"] in ("explained", "weak")]
            md.append(f"| {lab} | {len(rs)} | {100 * cnt(rs, 'explained') / len(rs):.0f}% | "
                      f"{100 * cnt(rs, 'weak') / len(rs):.0f}% | {np.median([r['f1'] for r in rs]):.2f} | "
                      f"{100 * sum(uses(r, skill.TEXT) for r in ok) / max(len(ok), 1):.0f}% | "
                      f"{100 * sum(uses(r, predicates.SQUARE_TEXT) for r in ok) / max(len(ok), 1):.0f}% | "
                      f"{100 * sum(r.get('engine_linked', False) for r in rs) / len(rs):.0f}% |")
    common = {}
    for r in scored:
        if r["status"] == "explained":
            common[r["explanation"]] = common.get(r["explanation"], 0) + 1
    md += ["", "## Most common explanations (explained latents)", ""]
    md += [f"- {n} latents: {t}" for t, n in sorted(common.items(), key=lambda t: -t[1])[:20]]
    md += ["", f"## The {a.show} best-explained latents", "",
           "| latent | r | explanation | precision | recall | F1 | null F1 |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in sorted(scored, key=lambda r: -r["f1"])[:a.show]:
        md.append(f"| {r['latent']} | {rel.get(r['latent'], float('nan')):.2f} | {r['explanation']} | {r['precision']:.2f} | "
                  f"{r['recall']:.2f} | {r['f1']:.2f} | {r['f1_null']:.2f} |")
    linked = sorted((r for r in scored if r.get("engine_linked")),
                    key=lambda r: -abs(r["engine"]["eval_beyond_board"]["shift"]))
    md += ["", f"## The {min(a.show, len(linked))} most engine-linked latents", "",
           "Win chance (Stockfish) for the side to move where the latent fires, and how far that is from what the "
           "pieces on the board predict; the same for the threat against the side to move; then the latent's "
           "best fact explanation.", "",
           "| latent | r | win % when firing | beyond the board | threat beyond the board | explanation (F1) |",
           "| --- | --- | --- | --- | --- | --- |"]
    for r in linked[:a.show]:
        e = r["engine"]
        md.append(f"| {r['latent']} | {rel.get(r['latent'], float('nan')):.2f} | {e['eval']['on']:.0f} | "
                  f"{e['eval_beyond_board']['shift']:+.1f} | {e['threat_beyond_board']['shift']:+.1f} | "
                  f"{r['explanation']} ({r['f1']:.2f}) |")
    (out_dir / "explain.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cc-run", default="runs/transcend/crosscoder/everything-3m", help="crosscoder run folder")
    ap.add_argument("--cc", default="L15", help="crosscoder in that run, e.g. L15 or Lfinal")
    ap.add_argument("--n", type=int, default=100_000, help="positions to sample from the stored ones")
    ap.add_argument("--workers", type=int, default=max(1, min(16, (os.cpu_count() or 2) - 2)),
                    help="processes for the facts (each runs one single-threaded Stockfish)")
    ap.add_argument("--depth", type=int, default=14, help="Stockfish depth for the skill facts")
    ap.add_argument("--no-engine", action="store_true", help="board facts only: no Stockfish, no Maia-2")
    ap.add_argument("--batch", type=int, default=4096, help="positions encoded at once")
    ap.add_argument("--pair-from", type=int, default=16, help="each latent's best single facts that are paired")
    ap.add_argument("--keep", type=int, default=600, help="engine-linked latents in the layer's probe (a third per model group)")
    ap.add_argument("--min-fires", type=int, default=20, help="firings needed in each half to score a latent")
    ap.add_argument("--min-pred", type=int, default=20, help="a fact (or pair) must hold this often in the fit half")
    ap.add_argument("--good", type=float, default=0.5, help="held-out F1 for 'explained'")
    ap.add_argument("--weak", type=float, default=0.3, help="held-out F1 for 'weak'")
    ap.add_argument("--show", type=int, default=40, help="latents listed in each table of explain.md")
    ap.add_argument("--device", default="auto", help="auto, cuda, mps or cpu")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()

    cc_run = Path(a.cc_run)
    cc_dir = cc_run / ("cc-" + a.cc.removeprefix("cc-"))
    info = json.loads((cc_run / "collect.json").read_text())
    rows = np.load(cc_run / "rows.npy")
    idx = np.sort(np.random.default_rng(a.seed).choice(len(rows), min(a.n, len(rows)), replace=False))
    print(f"{len(idx)} of {len(rows)} stored positions; {len(ALL)} facts", flush=True)
    depth = 0 if a.no_engine else a.depth
    P, numbers, maia = facts(rows, idx, info["folders"], [cc_dir / "facts.npz", *sorted(cc_run.glob("cc-*/facts.npz"))],
                             a.workers, depth)
    if depth:
        P = refresh(P.copy(), numbers)
    Q = square_facts(rows, idx, info["folders"], cc_run / "squares.npz", a.workers)
    if depth:
        loss, gap = numbers[:, NUMBERS.index("loss")], numbers[:, NUMBERS.index("gap")]
        print(f"  engine: median loss of the move played {np.nanmedian(loss):.1f} win-% points; "
              f"{100 * np.nanmean(gap >= skill.SHARP):.0f}% of positions have only one good move", flush=True)
    # games, not positions, are split: a game's positions are alike
    halves = ((rows[idx, 0].astype(np.int64) * 1_000_003 + rows[idx, 1]) * 2654435761 % 2 ** 32 % 2).astype(np.int64)
    fit, test = halves == 0, halves == 1

    # engine targets: the evaluation as is, and the evaluation and threat beyond a linear fit (on the
    # fit half) from the board and square facts
    board_X = np.concatenate([P[:, :len(predicates.NAMES)], Q], 1).astype(np.float32)
    wp, gap, threat = (numbers[:, NUMBERS.index(k)] for k in ("wp", "gap", "threat"))
    Y = np.full((len(idx), len(TARGETS)), np.nan, dtype=np.float32)
    if depth:
        print("  fitting the evaluation and threat from the board and square facts", flush=True)
        ok = ~(np.isnan(wp) | np.isnan(threat))
        fit_ok = fit & ok
        Y[:, 0], Y[:, 3] = wp, gap
        Y[ok, 1] = (wp - ridge(board_X, np.nan_to_num(wp), fit_ok))[ok]
        Y[ok, 2] = (threat - ridge(board_X, np.nan_to_num(threat), fit_ok))[ok]

    dev = ev.device(a.device)
    ck = torch.load(cc_dir / "cc.pt", map_location="cpu", weights_only=False)
    with open(cc_dir / "latents.jsonl", encoding="utf-8") as f:
        lat = [{k: r[k] for k in ("latent", "rel_norm", "rate")} for r in map(json.loads, f)]
    rel = {r["latent"]: r["rel_norm"] for r in lat}
    rel_arr = np.array([rel.get(j, 0.5) for j in range(ck["latents"])], dtype=np.float32)
    c = counts(cc_run, ck, idx, halves, np.concatenate([P, Q], 1), Y, rel_arr, dev, a.batch, a.pair_from, a.keep,
               a.min_pred)
    recs = score(c, a)
    probe = []
    if depth:
        print("what the layer knows: probes", flush=True)
        probe = layer_probe(cc_run, ck, idx, fit, test, board_X, numbers, c["kept"].numpy(), c["kept_on"], rel)
    out_dir = RESULTS / cc_run.name / cc_dir.name
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "explanations.jsonl", "w", encoding="utf-8") as f:
        for r, l in zip(recs, lat):
            f.write(json.dumps(dict(r, rel_norm=l["rel_norm"])) + "\n")
    report(recs, lat, out_dir, a, len(idx), probe, info["names"])
    print((out_dir / "explain.md").read_text(encoding="utf-8").split("## By which")[0].strip())
    print(f"\nwrote {out_dir / 'explanations.jsonl'} and {out_dir / 'explain.md'}")


if __name__ == "__main__":
    main()
