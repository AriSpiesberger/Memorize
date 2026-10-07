"""Train and evaluate everything after the splits, in one go.

    python run_experiment.py                      # uses data/, writes ckpt/ and logs/
    python run_experiment.py --sft-steps 3000     # fewer imitation steps
    python run_experiment.py --redo               # retrain even if checkpoints exist

Order: imitation (full, filtered, random) -> RL from filtered (deep, shallow,
random) -> evaluate.py. A step whose checkpoint already exists is skipped, so an
interrupted run picks up where it stopped. Each step's output goes to the
console and to logs/<step>.log.
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--data", default="data")
ap.add_argument("--ckpt", default="ckpt")
ap.add_argument("--sft-steps", type=int, default=3000, help="max imitation steps; train_sft stops early on val loss")
ap.add_argument("--rl-steps", type=int, default=5000)
ap.add_argument("--search-sims", type=int, default=400, help="PUCT simulations for the search arms (0 = skip search)")
ap.add_argument("--redo", action="store_true", help="rerun steps whose checkpoint already exists")
args = ap.parse_args()

data, ckpt, logs = HERE / args.data, HERE / args.ckpt, HERE / "logs"
ckpt.mkdir(exist_ok=True)
logs.mkdir(exist_ok=True)


def step(name, script, *cli, out=None):
    if out is not None and out.exists() and not args.redo:
        print(f"== {name}: {out.name} exists, skipping", flush=True)
        return
    print(f"\n== {name}", flush=True)
    t0 = time.time()
    with open(logs / f"{name}.log", "w", encoding="utf-8") as log:
        proc = subprocess.Popen([sys.executable, "-u", str(HERE / script), *map(str, cli)], cwd=HERE,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
        for line in proc.stdout:
            print("   " + line, end="", flush=True)
            log.write(line)
    if proc.wait() != 0:
        sys.exit(f"{name} failed (exit {proc.returncode}); see logs/{name}.log")
    print(f"== {name} done in {(time.time() - t0) / 60:.1f} min", flush=True)


for arm in ("full", "filtered", "random"):
    step(f"sft_{arm}", "train_sft.py", "--train", data / f"train_{arm}.jsonl", "--out", ckpt / f"{arm}.pt",
         "--steps", args.sft_steps, out=ckpt / f"{arm}.pt")

for reward in ("deep", "shallow", "random"):
    step(f"rl_{reward}", "rl_finetune.py", "--init", ckpt / "filtered.pt", "--positions", data / "rl_positions.jsonl",
         "--reward", reward, "--out", ckpt / f"rl_{reward}.pt", "--monitor", data / "test_hard.jsonl",
         "--steps", args.rl_steps, out=ckpt / f"rl_{reward}.pt")

models = {"full": "full", "filtered": "filtered", "random_ctrl": "random",
          "rl_deep": "rl_deep", "rl_shallow": "rl_shallow", "rl_random": "rl_random"}
search = ["--search", f"filtered={args.search_sims}", f"rl_deep={args.search_sims}"] if args.search_sims else []
step("evaluate", "evaluate.py", "--data", data, "--full-ref", ckpt / "full.pt",
     "--models", *[f"{k}={ckpt / f'{v}.pt'}" for k, v in models.items()], *search, "--out", HERE / "results.json")
print("\nresults.json and best_rate_by_depth.png are in", HERE)
