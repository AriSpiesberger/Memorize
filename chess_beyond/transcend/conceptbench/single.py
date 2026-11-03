"""The static bench with one unit instead of a concept vector: if the crosscoder's latents are sparse and clean, a single
latent should carry a known concept, and the LP's v (hundreds of latents) should not be needed.

    python transcend/conceptbench/single.py                  # -> results/transcend/conceptbench/single.md, single.json

Per concept and readout, on the same matched pairs as score.py: the one unit (and sign) whose value orders the most fit
pairs correctly (positive above its negative; a tie counts half, so a latent off on both sides scores 0.5), then its pair
accuracy on the test pairs, with a 95% bootstrap interval over test games. Readouts: each model alone through the
layer's crosscoder (cc4096-Wview / -Sview), W and S raw (one neuron), the board (one piece-on-square). Beside it, the
LP's accuracy from score.py for the same readout, so the cost of dropping v can be read off.
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bench import CONCEPTS, MANIFEST, POSITIONS, RESULTS, RUNS

ACTS = RUNS / "acts"
LAYERS = ("4", "8", "11", "15", "final")
READOUTS = ("cc4096-Wview", "cc4096-Sview", "W", "S")
BOOT = 1000


def acc(d):
    return (d > 0).mean(0) + 0.5 * (d == 0).mean(0)


def main():
    import pandas as pd
    import pyarrow.parquet as pq
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    games = pd.factorize(pd.read_parquet(POSITIONS, columns=["game_id"])["game_id"])[0]
    pairs = {}
    for k in man["concepts"]:
        t = pq.read_table(CONCEPTS / f"{k}.parquet").to_pydict()
        pairs[k] = (np.array(t["split"]), np.array(t["pos"]), np.array(t["neg"]))
    rng = np.random.default_rng(0)
    out = {}
    targets = [("board", "board")] + [(r, L) for L in LAYERS for r in READOUTS]
    for r, L in targets:
        X = np.load(ACTS / r / f"L{L}.npy", mmap_mode="r")
        lp = json.loads((RESULTS / r / f"{'board' if r == 'board' else 'L' + L}.json").read_text(encoding="utf-8"))
        rows = {}
        for k, (split, pos, neg) in pairs.items():
            fit, te = split == "fit", split == "test"
            d_fit = np.asarray(X[pos[fit]], np.float32) - np.asarray(X[neg[fit]], np.float32)
            a = acc(d_fit)
            u, sign = (int(np.argmax(a)), 1) if a.max() >= 1 - a.min() else (int(np.argmin(a)), -1)
            col_p, col_n = np.asarray(X[pos[te], u], np.float32), np.asarray(X[neg[te], u], np.float32)
            hit = (sign * (col_p - col_n) > 0) + 0.5 * (col_p == col_n)
            g, gi = np.unique(np.r_[games[pos[te]], games[neg[te]]], return_inverse=True)
            gp, gn = gi[:te.sum()], gi[te.sum():]
            boots = []
            for _ in range(BOOT):
                w = rng.multinomial(len(g), np.full(len(g), 1 / len(g))).astype(float)
                pw = w[gp] * w[gn]
                boots.append((pw * hit).sum() / max(pw.sum(), 1e-12))
            rows[k] = dict(unit=u, sign=sign, fit=float(a[u] if sign > 0 else 1 - a[u]), test=float(hit.mean()),
                           test_ci=np.quantile(boots, [.025, .975]).tolist(), lp=lp.get(k, {}).get("accuracy"),
                           ties=float((col_p == col_n).mean()))
        out[f"{r}|{L}"] = rows
        print(f"  {r} L{L}: single {np.mean([v['test'] for v in rows.values()]):.3f}, LP "
              f"{np.mean([v['lp'] for v in rows.values() if v['lp'] is not None]):.3f}", flush=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "single.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    write(out, man)


def write(out, man):
    fams = ["pieces", "openings", "structures", "imbalances", "plans"]
    fam = {k: c["family"] for k, c in man["concepts"].items()}
    names = {"cc4096-Wview": "W through cc", "cc4096-Sview": "S through cc", "W": "W raw", "S": "S raw", "board": "board"}
    md = ["# One unit against the concept vector", "",
          "Test pair accuracy of the single best unit (picked on fit pairs) / the LP's concept vector v, family means. A latent "
          "is one crosscoder latent, a neuron one raw dimension, the board one piece-on-square. Ties count half, so a latent "
          "that is off on both sides of a pair scores 0.5 there.", "",
          "| readout | layer | " + " | ".join(fams) + " |", "|---|---|" + "---|" * len(fams)]
    for key, rows in out.items():
        r, L = key.split("|")
        cells = []
        for f in fams:
            ks = [k for k in rows if fam[k] == f]
            cells.append(f"{np.mean([rows[k]['test'] for k in ks]):.3f} / {np.mean([rows[k]['lp'] for k in ks if rows[k]['lp'] is not None]):.3f}")
        md.append(f"| {names[r]} | {L} | " + " | ".join(cells) + " |")
    md += ["", "## Per concept, layer 11", "", "| concept | W cc: latent, single [95%] / LP | S cc: latent, single [95%] / LP | W raw single / LP | S raw single / LP | board single / LP |",
           "|---|---|---|---|---|---|"]
    for k in sorted(fam, key=lambda x: (fams.index(fam[x]), x)):
        c = []
        for key in ("cc4096-Wview|11", "cc4096-Sview|11", "W|11", "S|11", "board|board"):
            v = out[key][k]
            c.append((f"{v['unit']}: " if key.startswith("cc") else "") + f"{v['test']:.2f} [{v['test_ci'][0]:.2f}, {v['test_ci'][1]:.2f}] / {v['lp']:.2f}")
        md.append(f"| {k} | " + " | ".join(c) + " |")
    (RESULTS / "single.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"wrote {RESULTS / 'single.md'}")


if __name__ == "__main__":
    main()
