"""Score models on held-out positions: how often the top move is in the best set.

  python evaluate.py --data data/ --models full=ckpt/full.pt filtered=ckpt/filtered.pt \
      random_ctrl=ckpt/random.pt rl_deep=ckpt/rl_deep.pt rl_shallow=ckpt/rl_shallow.pt \
      rl_random=ckpt/rl_random.pt --search filtered=200 rl_deep=200 --full-ref ckpt/full.pt

Reports, per model:
  hard / easy best-move rate (argmax over legal moves)
  rate by depth_to_find (all test positions) -> best_rate_by_depth.png
  on hard positions, split by whether any best move appears as a label in
      train_filtered (a "seen elsewhere" channel) or never does
  with --full-ref: rate on hard positions the full-data model also misses
      (its best-set probability < --rare), i.e. what the humans' own model misses
--search name=sims runs PUCT search with that many simulations for that model
(slow: it uses --search-limit positions).
"""
import argparse
import json
from collections import defaultdict

import chess
import torch

from common import MOVE_TO_ID, MOVES, encode_board, legal_mask, load_model, masked_logits, model_move_to_real, read_jsonl
from search import mcts_move

ap = argparse.ArgumentParser()
ap.add_argument("--data", required=True)
ap.add_argument("--models", nargs="+", required=True, help="name=path")
ap.add_argument("--search", nargs="*", default=[], help="name=sims")
ap.add_argument("--search-limit", type=int, default=500)
ap.add_argument("--full-ref", default=None)
ap.add_argument("--rare", type=float, default=0.05)
ap.add_argument("--out", default="results.json")
args = ap.parse_args()

dev = "cuda" if torch.cuda.is_available() else "cpu"
test_all = read_jsonl(f"{args.data}/test_all.jsonl")
hard = [r for r in test_all if r["band"] == "hard"]
easy = [r for r in test_all if r["band"] == "easy"]
seen_labels = set(json.load(open(f"{args.data}/filtered_label_set.json")))
for r in hard:
    r["seen_elsewhere"] = any(m in seen_labels for m in r["best_set"])


@torch.no_grad()
def policy_probs(model, rows):
    out = []
    for i in range(0, len(rows), 512):
        chunk = rows[i:i + 512]
        boards = [chess.Board(r["fen"]) for r in chunk]
        x = torch.tensor([encode_board(b) for b in boards], device=dev)
        m = torch.stack([legal_mask(b) for b in boards]).to(dev)
        out.append(torch.softmax(masked_logits(model(x)[0], m), -1).cpu())
    return torch.cat(out) if out else torch.empty(0, len(MOVES))


def best_mass(probs, rows):
    return [sum(probs[i, MOVE_TO_ID[m]].item() for m in r["best_set"]) for i, r in enumerate(rows)]


def rate(hits):
    return round(sum(hits) / len(hits), 4) if hits else None


results = {}
rare_mask = None
if args.full_ref:
    ref = load_model(args.full_ref, dev).eval()
    rare_mask = [p < args.rare for p in best_mass(policy_probs(ref, hard), hard)]

by_depth_all = {}
for spec in args.models:
    name, path = spec.split("=", 1)
    model = load_model(path, dev).eval()
    probs = policy_probs(model, test_all)
    top = probs.argmax(-1).tolist()
    hit = {id(r): MOVES[t] in set(r["best_set"]) for t, r in zip(top, test_all)}
    depth = defaultdict(list)
    for r in test_all:
        depth[r["depth_to_find"]].append(hit[id(r)])
    by_depth_all[name] = {d: rate(v) for d, v in sorted(depth.items())}
    hard_hits = [hit[id(r)] for r in hard]
    res = {"hard": rate(hard_hits), "easy": rate([hit[id(r)] for r in easy]),
           "hard_seen_elsewhere": rate([h for h, r in zip(hard_hits, hard) if r["seen_elsewhere"]]),
           "hard_never_seen": rate([h for h, r in zip(hard_hits, hard) if not r["seen_elsewhere"]]),
           "hard_best_mass": round(sum(best_mass(probs[[i for i, r in enumerate(test_all) if r["band"] == "hard"]], hard)) / max(len(hard), 1), 4),
           "n_hard": len(hard), "n_easy": len(easy)}
    if rare_mask is not None:
        res["hard_missed_by_full_model"] = rate([h for h, k in zip(hard_hits, rare_mask) if k])
    results[name] = res
    print(name, json.dumps(res), flush=True)

for spec in args.search:
    name, sims = spec.split("=", 1)
    path = dict(s.split("=", 1) for s in args.models)[name]
    model = load_model(path, dev).eval()
    rows = hard[:args.search_limit]
    hits = []
    for r in rows:
        b = chess.Board(r["fen"])
        mv = mcts_move(model, b, sims=int(sims), device=dev)
        hits.append(mv is not None and mv in {model_move_to_real(m, b.turn) for m in r["best_set"]})
    results[f"{name}+search{sims}"] = {"hard": rate(hits), "n_hard": len(rows)}
    print(f"{name}+search{sims}", results[f"{name}+search{sims}"], flush=True)

results["by_depth"] = by_depth_all
json.dump(results, open(args.out, "w"), indent=2)

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4))
    for name, curve in by_depth_all.items():
        ds = [d for d in curve if curve[d] is not None]
        ax.plot(ds, [curve[d] for d in ds], marker="o", label=name)
    stats = json.load(open(f"{args.data}/stats.json"))["args"]
    ax.axvspan(stats["easy_max"] + 0.5, stats["hard_min"] - 0.5, color="grey", alpha=0.15, label="buffer")
    ax.set_xlabel("depth to find the best move"); ax.set_ylabel("best-move rate (top move)")
    ax.legend(fontsize=8); ax.grid(alpha=0.3); fig.tight_layout()
    fig.savefig("best_rate_by_depth.png", dpi=150)
    print("saved best_rate_by_depth.png")
except Exception as e:
    print("plot skipped:", e)
print("wrote", args.out)
