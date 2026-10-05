"""Compare two `eval_format` runs question by question.

    python -m memorize.eval_format --model models/sft-fused --name sft --n 300
    python -m memorize.eval_format --model models/sft-fused --adapter-path adapters/drgrpo-run1 \\
        --name drgrpo-run1 --n 300
    python -m memorize.compare sft drgrpo-run1

For each benchmark both runs answered, pairs the replies by question id and
reports the change in accuracy and in strict format, with McNemar's exact
test (see `memorize.stats`).
"""

import argparse
import json
from pathlib import Path

from memorize.stats import describe, mcnemar

RESULTS_DIR = Path(__file__).parent.parent / "results"


def load(name, bench):
    path = RESULTS_DIR / name / f"format_{bench}.jsonl"
    return {r["id"]: r for r in map(json.loads, open(path))} if path.exists() else {}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("before", help="results/<before>/")
    p.add_argument("after", help="results/<after>/")
    p.add_argument("--bench", nargs="+", default=["mmlu_pro", "mmlu_redux", "ceval", "supergpqa"])
    args = p.parse_args()

    print(f"{args.before} -> {args.after}\n")
    for bench in args.bench:
        a, b = load(args.before, bench), load(args.after, bench)
        ids = sorted(set(a) & set(b))
        if not ids:
            print(f"{bench:11s} no shared questions")
            continue
        for metric, value in [
            ("accuracy", lambda r: r["strict"] == r["gold"]),
            ("format", lambda r: r["strict"] is not None),
        ]:
            before = [value(a[i]) for i in ids]
            after = [value(b[i]) for i in ids]
            print(
                f"{bench:11s} {metric:8s} n={len(ids):3d}  "
                f"{sum(before) / len(ids):6.1%} -> {sum(after) / len(ids):6.1%}  "
                f"{describe(mcnemar(before, after))}"
            )
        print()


if __name__ == "__main__":
    main()
