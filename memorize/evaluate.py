"""Score a model on multiple-choice benchmarks (right or wrong per question).

    python -m memorize.evaluate --name baseline --bench mmlu_pro mmlu_redux --n 300

Each benchmark is scored on a fixed, seeded sample of questions, so runs with
the same --n and --split-seed are comparable. Results go to
results/<name>/<benchmark>.jsonl and can be resumed.
"""

import argparse
import json
import math
import time
from pathlib import Path

import mlx.core as mx
from mlx_lm import load

from memorize import benchmarks
from memorize import engine

RESULTS_DIR = Path(__file__).parent.parent / "results"


def evaluate(model, tokenizer, items, out_path, args):
    done = {}
    if out_path.exists():
        with open(out_path, encoding="utf-8") as f:
            done = {r["id"]: r for r in map(json.loads, f)}
    todo = [item for item in items if item["id"] not in done]
    prompts = [
        tokenizer.apply_chat_template(
            [{"role": "user", "content": benchmarks.format_prompt(item)}],
            add_generation_prompt=True,
            enable_thinking=not args.no_think,
        )
        for item in todo
    ]

    start, n_tokens = time.time(), 0
    with open(out_path, "a", encoding="utf-8") as f:

        def on_done(i, rollout):
            nonlocal n_tokens
            item = todo[i]
            answer = rollout.answer(tokenizer)
            pred = benchmarks.extract_answer(answer)
            record = {
                "id": item["id"],
                "subject": item["subject"],
                "gold": item["answer"],
                "pred": pred,
                "correct": pred == item["answer"],
                "reasoning_tokens": rollout.reasoning_tokens,
                "total_tokens": len(rollout.tokens),
                "forced": rollout.forced,
                "text": tokenizer.decode(rollout.tokens),
            }
            done[item["id"]] = record
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            f.flush()
            n_tokens += len(rollout.tokens)
            if len(done) % 10 == 0 or len(done) == len(items):
                acc = sum(r["correct"] for r in done.values()) / len(done)
                print(
                    f"  {len(done)}/{len(items)}  acc {acc:.1%}  "
                    f"{n_tokens / (time.time() - start):.0f} tok/s  "
                    f"peak {mx.get_peak_memory() / 1e9:.1f} GB",
                    flush=True,
                )

        engine.generate(
            model,
            tokenizer,
            prompts,
            thinking=not args.no_think,
            budget=args.budget,
            batch_size=args.batch_size,
            on_done=on_done,
        )
    return [done[item["id"]] for item in items]


def summarize(records):
    n = len(records)
    acc = sum(r["correct"] for r in records) / n
    return {
        "n": n,
        "accuracy": acc,
        "stderr": math.sqrt(acc * (1 - acc) / n),
        "no_answer": sum(r["pred"] is None for r in records) / n,
        "forced_close": sum(r["forced"] for r in records) / n,
        "mean_reasoning_tokens": sum(r["reasoning_tokens"] for r in records) / n,
        "mean_total_tokens": sum(r["total_tokens"] for r in records) / n,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="results/<name>/")
    parser.add_argument("--bench", nargs="+", default=list(benchmarks.BENCHMARKS))
    parser.add_argument("--n", type=int, default=300, help="questions per benchmark")
    parser.add_argument("--split-seed", type=int, default=0)
    parser.add_argument("--model", default=engine.MODEL)
    parser.add_argument("--adapter-path")
    parser.add_argument("--no-think", action="store_true")
    parser.add_argument(
        "--budget", type=int, default=2048, help="reasoning tokens per question"
    )
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    mx.random.seed(args.seed)
    model, tokenizer = load(args.model, adapter_path=args.adapter_path)
    out_dir = RESULTS_DIR / args.name
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = {}
    for bench in args.bench:
        items, _ = benchmarks.split(bench, args.n, args.split_seed)
        print(f"{bench}: {len(items)} questions", flush=True)
        records = evaluate(model, tokenizer, items, out_dir / f"{bench}.jsonl", args)
        summary[bench] = summarize(records)
        s = summary[bench]
        print(f"{bench}: {s['accuracy']:.1%} ± {s['stderr']:.1%}  (n={s['n']})", flush=True)
        with open(out_dir / "summary.json", "w", encoding="utf-8") as f:
            json.dump({"args": vars(args), "results": summary}, f, indent=2)


if __name__ == "__main__":
    main()
