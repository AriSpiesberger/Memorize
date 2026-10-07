"""Build train/test splits, the best-move filter, and the controls.

  python filter_experiment/make_splits.py --positions data/filter/positions_10k.jsonl \
      --easy-max 4 --hard-min 8

Bands by depth_to_find:  easy <= easy_max < buffer < hard_min <= hard
Outputs (in --out):
  train_full.jsonl       every training example (reference)
  train_filtered.jsonl   best-set moves removed in buffer + hard positions
  train_random.jsonl     same number of examples removed, uniformly at random
  rl_positions.jsonl     training positions (labels unused) with engine scores
  test_hard.jsonl        held-out hard positions  (main test set)
  test_easy.jsonl        held-out easy positions  (sanity check)
  test_all.jsonl         held-out positions of every band (depth curves)
  filtered_label_set.json  model-frame moves that appear as labels in train_filtered
  stats.json
Splits are by game, so no game is on both sides.
"""
import argparse
import hashlib
import json
import os
import random

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # chess_beyond/: common.py, paths.py, search.py
import paths
from common import read_jsonl, write_jsonl

ap = argparse.ArgumentParser()
ap.add_argument("--positions", required=True)
ap.add_argument("--out", default=str(paths.FILTER_DATA / "splits"))
ap.add_argument("--easy-max", type=int, default=4)
ap.add_argument("--hard-min", type=int, default=8)
ap.add_argument("--test-frac", type=float, default=0.1)
ap.add_argument("--seed", type=int, default=0)
args = ap.parse_args()
assert args.easy_max < args.hard_min
os.makedirs(args.out, exist_ok=True)


def band(r):
    d = r["depth_to_find"]
    return "easy" if d <= args.easy_max else ("hard" if d >= args.hard_min else "buffer")


def is_test(game_id):
    h = int(hashlib.md5(f"{args.seed}:{game_id}".encode()).hexdigest(), 16)
    return (h % 10_000) / 10_000 < args.test_frac


rows = read_jsonl(args.positions)
for r in rows:
    r["band"] = band(r)
train = [r for r in rows if not is_test(r["game_id"])]
test = [r for r in rows if is_test(r["game_id"])]

filtered = [r for r in train if r["band"] == "easy" or not r["played_in_best"]]
n_removed = len(train) - len(filtered)
rng = random.Random(args.seed)
random_ctrl = rng.sample(train, len(filtered))

write_jsonl(train, f"{args.out}/train_full.jsonl")
write_jsonl(filtered, f"{args.out}/train_filtered.jsonl")
write_jsonl(random_ctrl, f"{args.out}/train_random.jsonl")
write_jsonl([{k: r[k] for k in ("fen", "band", "depth_to_find", "best_set", "shallow_best_set", "deep_scores")}
             for r in train], f"{args.out}/rl_positions.jsonl")
write_jsonl([r for r in test if r["band"] == "hard"], f"{args.out}/test_hard.jsonl")
write_jsonl([r for r in test if r["band"] == "easy"], f"{args.out}/test_easy.jsonl")
write_jsonl(test, f"{args.out}/test_all.jsonl")
json.dump(sorted({r["m_played"] for r in filtered}), open(f"{args.out}/filtered_label_set.json", "w"))


def summary(rs):
    out = {}
    for b in ("easy", "buffer", "hard"):
        sub = [r for r in rs if r["band"] == b]
        out[b] = {"n": len(sub),
                  "human_played_best": round(sum(r["played_in_best"] for r in sub) / max(len(sub), 1), 4)}
    return out


stats = {"args": vars(args), "positions": len(rows), "train": len(train), "test": len(test),
         "removed_by_filter": n_removed, "train_bands": summary(train), "test_bands": summary(test),
         "filtered_hard_best_labels_left": sum(r["band"] != "easy" and r["played_in_best"] for r in filtered)}
json.dump(stats, open(f"{args.out}/stats.json", "w"), indent=2)
print(json.dumps(stats, indent=2))
