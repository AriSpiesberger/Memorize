"""Scored explanations for crosscoder latents, in plain chess terms.

    python transcend/explain.py --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal

The claim being tested: the latents (and the concept paths built from them in concepts.py) are
tangible chess ideas. An explanation is a predicate from predicates.py ("one of their pieces is
hanging", "the move gives check", ...) or two joined by "and", and it is only as good as its
score: how well it predicts, on positions it was not chosen on, when the latent fires.

  1. facts    --n positions sampled from the crosscoder's stored ones (rows.npy), every predicate
              computed on each (python-chess, all CPU cores). Cached in <cc-run>/<cc>/predicates.npz.
  2. counts   the positions are encoded with the crosscoder from the stored model states (no chess
              model is loaded); per latent, how often it fires with each predicate and each pair.
  3. score    games are split in two halves. On the "fit" half each latent's explanation is the
              predicate or pair with the best F1 (it must both cover the latent's firings and not
              fire much without it); precision, recall and F1 are then measured on the "test" half,
              next to the F1 the same predicate would get if it were unrelated to the latent
              (null). Also listed: facts nearly always true when the latent fires (recall >= 0.8)
              that are much rarer otherwise (lift >= 2).

-> results/transcend/crosscoder/<run>/<cc>/explanations.jsonl (one line per latent) and explain.md
   (how many latents are explained, by how much each model uses them, the best explanations).
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
import eval as ev                                                 # device
from crosscoder import RESULTS, Corpus, CrossCoder, load_sources, position, stack
from predicates import NAMES, TEXT, features

_corpus = None


def _init(folders):
    global _corpus
    _corpus = Corpus(folders)


def _facts(rows):
    """Predicates for a chunk of (folder, game, ply, char) rows, in a worker process."""
    out = np.zeros((len(rows), len(NAMES)), dtype=bool)
    for k, row in enumerate(rows):
        b, nxt, _ = position(_corpus, row)
        try:
            mv = b.parse_san(nxt)
        except ValueError:
            mv = None
        out[k] = features(b, mv)
    return out


def facts(rows, idx, folders, cache, workers):
    if cache.exists():
        z = np.load(cache)
        if np.array_equal(z["idx"], idx) and list(z["names"]) == NAMES:
            print(f"predicates: cached in {cache}", flush=True)
            return z["P"]
    chunks = np.array_split(rows[idx], max(1, len(idx) // 1000))
    parts, t0 = [], time.time()
    with Pool(workers, initializer=_init, initargs=(folders,)) as pool:
        for k, part in enumerate(pool.imap(_facts, chunks)):
            parts.append(part)
            done = sum(len(p) for p in parts)
            print(f"\r  predicates: {done}/{len(idx)} positions, {done / (time.time() - t0):.0f}/s   ", end="", flush=True)
    print()
    P = np.concatenate(parts)
    np.savez(cache, idx=idx, names=np.array(NAMES), P=P)
    return P


@torch.no_grad()
def counts(cc_run, ck, idx, halves, P, dev, batch):
    """Per half: latent firings, predicate (and pair) counts, and their co-occurrences."""
    sources = [tuple(s) for s in ck["sources"]]
    cc = CrossCoder(len(sources), ck["d"], ck["latents"], ck["k"]).to(dev)
    cc.load_state_dict(ck["state"])
    scales = ck["scales"].to(dev)
    arrs = load_sources(cc_run, sources)
    F = P.shape[1]
    ia, ib = torch.triu_indices(F, F, 1, device=dev)
    Q = F + len(ia)
    Lt = ck["latents"]
    tp = torch.zeros((2, Lt, Q), device=dev)
    fires = torch.zeros((2, Lt), device=dev)
    pred = torch.zeros((2, Q), device=dev)
    n = torch.zeros(2, device=dev)
    Pt = torch.from_numpy(P).to(dev)
    Ht = torch.from_numpy(halves).to(dev)
    t0 = time.time()
    for s in range(0, len(idx), batch):
        f, _, _ = cc.encode(stack(arrs, idx[s:s + batch], scales, dev))
        on = (f > 0).float()
        p = Pt[s:s + batch].float()
        q = torch.cat([p, p[:, ia] * p[:, ib]], 1)
        for h in (0, 1):
            m = (Ht[s:s + batch] == h).float()[:, None]
            tp[h] += (on * m).T @ q
            fires[h] += (on * m).sum(0)
            pred[h] += (q * m).sum(0)
            n[h] += m.sum()
        print(f"\r  encoded {min(s + batch, len(idx))}/{len(idx)} positions, {(time.time() - t0) / 60:.1f} min   ",
              end="", flush=True)
    print()
    names = NAMES + [f"{NAMES[a]}&{NAMES[b]}" for a, b in zip(ia.tolist(), ib.tolist())]
    return tp.cpu(), fires.cpu(), pred.cpu(), n.cpu(), names


def text(name):
    return " and ".join(TEXT[x] for x in name.split("&"))


def score(tp, fires, pred, n, names, a):
    """One record per latent: its explanation, held-out precision / recall / F1, the null F1, more facts."""
    fit = 2 * tp[0] / (fires[0][:, None] + pred[0][None, :]).clamp_min(1)
    fit[:, pred[0] < a.min_pred] = -1                                 # too rare to judge
    F = len(NAMES)
    fit[:, F:] -= 0.02                                                # a pair must beat one predicate clearly
    alt = fit.topk(4, dim=1)
    out = []
    for j in range(tp.shape[1]):
        r = dict(latent=j, fires_fit=int(fires[0, j]), fires_test=int(fires[1, j]))
        if fires[0, j] < a.min_fires or fires[1, j] < a.min_fires:
            r.update(status="too rare", explanation="", f1=0.0)
            out.append(r)
            continue
        c = int(alt.indices[j, 0])
        k, ft, pt = float(tp[1, j, c]), float(fires[1, j]), float(pred[1, c])
        prec, rec = k / max(pt, 1), k / max(ft, 1)
        f1 = 2 * k / max(ft + pt, 1)
        null = 2 * (ft / n[1]) * pt / max(ft + pt, 1)                 # F1 if the predicate ignored the latent
        base = pred[1, :F] / n[1]
        recall_all = tp[1, j, :F] / max(ft, 1)
        always = [(NAMES[i], float(recall_all[i]), float(base[i])) for i in range(F)
                  if recall_all[i] >= 0.8 and recall_all[i] >= 2 * base[i]]
        always.sort(key=lambda t: -t[1] / max(t[2], 1e-6))
        r.update(status="explained" if f1 >= a.good else "weak" if f1 >= a.weak else "unexplained",
                 name=names[c], explanation=text(names[c]), precision=prec, recall=rec, f1=f1, f1_null=float(null),
                 alternatives=[[names[int(i)], text(names[int(i)]), float(v)]
                               for i, v in zip(alt.indices[j, 1:], alt.values[j, 1:]) if v > 0],
                 always=[[nm, TEXT[nm], rc, bs] for nm, rc, bs in always[:4]])
        out.append(r)
    return out


def report(recs, lat, out_dir, a, n_pos):
    rel = {r["latent"]: r["rel_norm"] for r in lat}
    scored = [r for r in recs if r["status"] != "too rare"]
    cnt = lambda rs, s: sum(1 for r in rs if r["status"] == s)
    md = ["# Latent explanations", "",
          f"{n_pos} positions, split by game into a fit half (choose each latent's explanation) and a test "
          f"half (score it). An explanation is a predicate from predicates.py, or two joined by \"and\"; its "
          f"score is the F1 of predicting when the latent fires, on the test half. **explained**: F1 >= {a.good}; "
          f"**weak**: >= {a.weak}. Latents firing fewer than {a.min_fires} times in either half are too rare to score.", "",
          f"- {len(recs)} latents, {len(scored)} scored: {cnt(scored, 'explained')} explained "
          f"({100 * cnt(scored, 'explained') / max(len(scored), 1):.0f}%), {cnt(scored, 'weak')} weak, "
          f"{cnt(scored, 'unexplained')} unexplained; {len(recs) - len(scored)} too rare.", "",
          "## By which model uses the latent", "",
          "relative decoder norm r: ~0 the first model only, ~0.5 both, ~1 the second model only.", "",
          "| r | scored | explained | weak | median F1 |", "| --- | --- | --- | --- | --- |"]
    for lo, hi, lab in ((0, 0.4, "< 0.4"), (0.4, 0.6, "0.4-0.6"), (0.6, 1.01, ">= 0.6")):
        rs = [r for r in scored if lo <= rel.get(r["latent"], 0.5) < hi]
        if rs:
            md.append(f"| {lab} | {len(rs)} | {100 * cnt(rs, 'explained') / len(rs):.0f}% | "
                      f"{100 * cnt(rs, 'weak') / len(rs):.0f}% | {np.median([r['f1'] for r in rs]):.2f} |")
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
    (out_dir / "explain.md").write_text("\n".join(md) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cc-run", default="runs/transcend/crosscoder/everything-3m", help="crosscoder run folder")
    ap.add_argument("--cc", default="Lfinal", help="crosscoder in that run, e.g. Lfinal or L12")
    ap.add_argument("--n", type=int, default=300_000, help="positions to sample from the stored ones")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2), help="processes for the predicates")
    ap.add_argument("--batch", type=int, default=4096, help="positions encoded at once")
    ap.add_argument("--min-fires", type=int, default=20, help="firings needed in each half to score a latent")
    ap.add_argument("--min-pred", type=int, default=20, help="a predicate (or pair) must hold this often in the fit half")
    ap.add_argument("--good", type=float, default=0.5, help="held-out F1 for 'explained'")
    ap.add_argument("--weak", type=float, default=0.3, help="held-out F1 for 'weak'")
    ap.add_argument("--show", type=int, default=40, help="latents listed in explain.md")
    ap.add_argument("--device", default="auto", help="auto, cuda, mps or cpu")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()

    cc_run = Path(a.cc_run)
    cc_dir = cc_run / ("cc-" + a.cc.removeprefix("cc-"))
    info = json.loads((cc_run / "collect.json").read_text())
    rows = np.load(cc_run / "rows.npy")
    idx = np.sort(np.random.default_rng(a.seed).choice(len(rows), min(a.n, len(rows)), replace=False))
    print(f"{len(idx)} of {len(rows)} stored positions; {len(NAMES)} predicates, "
          f"{len(NAMES) * (len(NAMES) - 1) // 2} pairs", flush=True)
    P = facts(rows, idx, info["folders"], cc_dir / "predicates.npz", a.workers)
    # games, not positions, are split: a game's positions are alike
    halves = ((rows[idx, 0].astype(np.int64) * 1_000_003 + rows[idx, 1]) * 2654435761 % 2 ** 32 % 2).astype(np.int64)

    dev = ev.device(a.device)
    ck = torch.load(cc_dir / "cc.pt", map_location="cpu", weights_only=False)
    tp, fires, pred, n, names = counts(cc_run, ck, idx, halves, P, dev, a.batch)
    recs = score(tp, fires, pred, n, names, a)

    with open(cc_dir / "latents.jsonl", encoding="utf-8") as f:
        lat = [{k: r[k] for k in ("latent", "rel_norm", "rate")} for r in map(json.loads, f)]
    out_dir = RESULTS / cc_run.name / cc_dir.name
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "explanations.jsonl", "w", encoding="utf-8") as f:
        for r, l in zip(recs, lat):
            f.write(json.dumps(dict(r, rel_norm=l["rel_norm"])) + "\n")
    report(recs, lat, out_dir, a, len(idx))
    print((out_dir / "explain.md").read_text(encoding="utf-8").split("## By which")[0].strip())
    print(f"\nwrote {out_dir / 'explanations.jsonl'} and {out_dir / 'explain.md'}")


if __name__ == "__main__":
    main()
