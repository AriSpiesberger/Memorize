"""The dataset: for each kept concept, positive positions paired with matched negatives.

    python transcend/conceptbench/build_dataset.py
    python transcend/conceptbench/build_dataset.py --only white_rooks_atleast_1,...     # adds to the dataset

A full build draws from one random stream, so it changes every concept's pairs and scores already cached no longer apply to
them. --only leaves the other concepts' pairs alone, and adds to the manifest. A positive is paired with its nearest negative, in the same split, game phase and side to move, by material: distance =
|difference in balance| + |difference in total material|, plus PLY_WEIGHT x |difference in ply|, which only breaks ties.
A negative is used once while there are unused ones near enough to consider (MATCH_K nearest), then reused. For plans, the
negatives are by construction in the same structure (plans.py labels only positions in the structure). Very common
concepts are capped at MAX_FIT and MAX_TEST positives.

Side to move is matched too, beyond the brief: the prompt ends differently for each side, and a mismatch would only add noise.

-> concepts/<name>.parquet (split, pos, neg: pos_ids into positions.parquet, distance) and concepts/manifest.json
   (definitions, thresholds, counts, the version of each labeller, matching quality).
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bench import CONCEPTS, COUNTS, LABELS, MANIFEST, POSITIONS
from labels import imbalances, plans, structures

PLY_WEIGHT = 0.01
MATCH_K = 32
MAX_FIT = 4000
MAX_TEST = 2000


def thresholds():
    """Every named constant of the labellers."""
    return {m.__name__.split(".")[-1]: {k: v for k, v in vars(m).items() if k.isupper() and isinstance(v, (int, float, str))}
            for m in (imbalances, plans, structures)}


def match(pos, neg, F, rng):
    """Each position in pos -> its matched negative from neg, in the same group already: F are the matching features."""
    tree = cKDTree(F[neg])
    k = min(MATCH_K, len(neg))
    _, near = tree.query(F[pos], k=k)
    near = near.reshape(len(pos), k)
    used = np.zeros(len(neg), bool)
    out = np.zeros(len(pos), int)
    for i in rng.permutation(len(pos)):
        free = near[i][~used[near[i]]]
        j = free[0] if len(free) else near[i, 0]
        used[j] = True
        out[i] = neg[j]
    return out


def concept_pairs(y, df_cols, rng):
    """The (split, pos, neg, distance) rows of one concept, and how many positives found no negative."""
    split, phase, side, F = df_cols
    rows, unmatched = [], 0
    for s, cap in (("fit", MAX_FIT), ("test", MAX_TEST)):
        pos_all = np.flatnonzero((y == 1) & (split == s))
        pos_all = rng.choice(pos_all, min(cap, len(pos_all)), replace=False)
        for ph in np.unique(phase[pos_all]):
            for sd in ("white", "black"):
                pos = pos_all[(phase[pos_all] == ph) & (side[pos_all] == sd)]
                neg = np.flatnonzero((y == 0) & (split == s) & (phase == ph) & (side == sd))
                if not len(pos):
                    continue
                if not len(neg):
                    unmatched += len(pos)
                    continue
                m = match(pos, neg, F, rng)
                rows.append((np.full(len(pos), s), pos, m, np.abs(F[pos] - F[m]).sum(1)))
    return rows, unmatched


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--only", default="", help="comma-separated concepts to add; the others keep their pairs")
    a = ap.parse_args()
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    t0 = time.time()
    df = pd.read_parquet(POSITIONS, columns=["split", "phase", "side", "material_balance", "material_total", "ply", "game_id"])
    info = json.loads(COUNTS.read_text(encoding="utf-8"))
    F = np.c_[df["material_balance"], df["material_total"], PLY_WEIGHT * df["ply"]].astype(np.float32)
    cols = (df["split"].to_numpy().astype(str), df["phase"].to_numpy().astype(str), df["side"].to_numpy().astype(str), F)
    kept = [k for k, c in info["concepts"].items() if c["kept"]]
    only = [k for k in a.only.split(",") if k]
    if not set(only) <= set(kept):
        sys.exit(f"--only: not kept concepts: {sorted(set(only) - set(kept))}")
    kept = only or kept
    lab = pd.read_parquet(LABELS, columns=kept)
    CONCEPTS.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(a.seed)
    man = dict(version=1, seed=a.seed, positions=len(df), thresholds=thresholds(), labeller_versions=info["versions"],
               matching=dict(ply_weight=PLY_WEIGHT, k=MATCH_K, max_fit=MAX_FIT, max_test=MAX_TEST), concepts={},
               dropped={k: dict(fit_pos=c["fit_pos"], family=c["family"]) for k, c in info["concepts"].items() if not c["kept"]},
               openings_below_threshold=info["openings_below_threshold"])
    if only:
        old = json.loads(MANIFEST.read_text(encoding="utf-8"))
        man["concepts"], man["dropped"] = old["concepts"], old["dropped"]
    for k in kept:
        rows, unmatched = concept_pairs(lab[k].to_numpy(), cols, rng)
        if not rows:
            man["dropped"][k] = dict(fit_pos=info["concepts"][k]["fit_pos"], family=info["concepts"][k]["family"], reason="no negatives")
            continue
        sp, po, ne, di = (np.concatenate(x) for x in zip(*rows))
        pq.write_table(pa.table(dict(split=sp, pos=po, neg=ne, distance=di)), CONCEPTS / f"{k}.parquet", compression="zstd")
        c = info["concepts"][k]
        man["concepts"][k] = dict(family=c["family"], definition=c["definition"], fit_pairs=int((sp == "fit").sum()),
                                  test_pairs=int((sp == "test").sum()), unmatched=unmatched, mean_distance=float(di.mean()),
                                  fit_pos=c["fit_pos"], fit_neg=c["fit_neg"], test_pos=c["test_pos"], test_neg=c["test_neg"],
                                  by_phase=c["by_phase"], neg_reused=float(1 - len(np.unique(ne)) / len(ne)))
    MANIFEST.write_text(json.dumps(man, indent=1), encoding="utf-8")
    print(f"{len(man['concepts'])} concepts -> {CONCEPTS} ({time.time() - t0:.0f}s); {len(man['dropped'])} dropped", flush=True)


if __name__ == "__main__":
    main()
