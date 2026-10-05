"""Measure a chat model on every benchmark, plus general instruction following.

    python -m memorize.eval_format --model models/sft-fused --name sft
    python -m memorize.eval_format --model models/sft-fused --adapter-path adapters/grpo-run1 --name grpo-run1

For each benchmark, the model answers the first `--n` seeded held-out
questions zero-shot with that benchmark's EvalScope prompt (see
`memorize.prompts`), greedy, thinking off. The headline number is strict
format: the last line is exactly the required 'ANSWER: X' (or '答案：X' for
C-Eval). Also reported: replies with an answer marker somewhere (loose),
replies that ran out of room, and accuracy as a side readout. A few failing
replies per benchmark are printed so the failure modes are visible.

Then the 19 instruction probes from `memorize.sft` (format constraints that
have nothing to do with the benchmarks) show whether RL cost general
instruction following.

Results go to results/<name>/format_<bench>.jsonl and format_summary.json,
and an interrupted run resumes.
"""

import argparse
import json
import time
from pathlib import Path

import mlx.core as mx
from mlx_lm import load
from mlx_lm.generate import BatchGenerator
from mlx_lm.sample_utils import make_sampler

from memorize import benchmarks, prompts, sft

RESULTS_DIR = Path(__file__).parent.parent / "results"
DEFAULT_BENCH = ["mmlu_pro", "mmlu_redux", "ceval", "supergpqa"]


def generate(model, tokenizer, items, max_new, batch_size, on_done):
    stop_ids = set(tokenizer.eos_token_ids)
    stop_ids |= set(tokenizer.encode("<|im_end|>", add_special_tokens=False))
    gen = BatchGenerator(
        model,
        stop_tokens=[[t] for t in stop_ids],
        sampler=make_sampler(temp=0.0),
        completion_batch_size=batch_size,
        prefill_batch_size=min(batch_size, 8),
    )
    owner, toks = {}, {}
    for i, item in enumerate(items):
        prompt = tokenizer.apply_chat_template(
            [{"role": "user", "content": prompts.user_prompt(item)}],
            add_generation_prompt=True,
            enable_thinking=False,
        )
        (uid,) = gen.insert([list(prompt)], [max_new])
        owner[uid], toks[uid] = i, []
    while responses := gen.next_generated():
        for r in responses:
            if r.token not in stop_ids:
                toks[r.uid].append(r.token)
            if r.finish_reason is not None:
                t = toks.pop(r.uid)
                on_done(items[owner[r.uid]], tokenizer.decode(t), len(t), r.finish_reason)
    gen.close()
    mx.clear_cache()


def summarize(records):
    n = len(records)
    return {
        "n": n,
        "strict_format": sum(r["strict"] is not None for r in records) / n,
        "loose_format": sum(r["loose"] is not None for r in records) / n,
        "ran_out_of_room": sum(r["finish"] == "length" for r in records) / n,
        "accuracy_strict": sum(r["strict"] == r["gold"] for r in records) / n,
        "accuracy_loose": sum(r["loose"] == r["gold"] for r in records) / n,
        "median_tokens": sorted(r["tokens"] for r in records)[n // 2],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", default="Qwen/Qwen3.5-2B-Base")
    p.add_argument("--adapter-path")
    p.add_argument("--name", required=True, help="results/<name>/")
    p.add_argument("--bench", nargs="+", default=DEFAULT_BENCH)
    p.add_argument("--n", type=int, default=100, help="questions per benchmark")
    p.add_argument("--max-new", type=int, default=2048)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--show-failures", type=int, default=3)
    p.add_argument("--skip-probes", action="store_true")
    args = p.parse_args()

    mx.set_cache_limit(int(2e9))
    model, tokenizer = load(args.model, adapter_path=args.adapter_path)
    out_dir = RESULTS_DIR / args.name
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {"model": args.model, "adapter": args.adapter_path, "results": {}}

    for bench in args.bench:
        items, _ = benchmarks.split(bench, args.n, 0)
        path = out_dir / f"format_{bench}.jsonl"
        done = {}
        if path.exists():
            done = {r["id"]: r for r in map(json.loads, open(path))}
        todo = [it for it in items if it["id"] not in done]
        print(f"{bench}: {len(todo)} to run, {len(done)} done", flush=True)
        start = time.time()

        with open(path, "a") as f:

            def on_done(item, text, n_tokens, finish):
                rec = {
                    "id": item["id"],
                    "subject": item["subject"],
                    "gold": item["answer"],
                    "strict": prompts.strict_answer(text, bench),
                    "loose": prompts.loose_answer(text, bench),
                    "tokens": n_tokens,
                    "finish": finish,
                    "text": text,
                }
                done[rec["id"]] = rec
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                f.flush()
                if len(done) % 20 == 0 or len(done) == len(items):
                    s = summarize(list(done.values()))
                    print(
                        f"  {len(done)}/{len(items)}  strict format {s['strict_format']:.1%}  "
                        f"accuracy {s['accuracy_strict']:.1%}  {time.time() - start:.0f}s",
                        flush=True,
                    )

            generate(model, tokenizer, todo, args.max_new, args.batch_size, on_done)

        records = [done[it["id"]] for it in items]
        s = summary["results"][bench] = summarize(records)
        print(
            f"{bench}: strict format {s['strict_format']:.1%} | loose {s['loose_format']:.1%} | "
            f"ran out of room {s['ran_out_of_room']:.1%} | accuracy {s['accuracy_strict']:.1%} "
            f"(loose {s['accuracy_loose']:.1%}) | median {s['median_tokens']} tokens",
            flush=True,
        )
        for r in [r for r in records if r["strict"] is None][: args.show_failures]:
            tail = " ".join(r["text"].split())[-200:]
            print(f"  [no strict answer line, {r['finish']}, {r['tokens']} tokens] ...{tail}")
        with open(out_dir / "format_summary.json", "w") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

    if not args.skip_probes:
        sft.run_probes(model, tokenizer, [], "instruction following")

    print("\nbenchmark      strict  loose  out-of-room  accuracy")
    for bench, s in summary["results"].items():
        print(
            f"{bench:13s} {s['strict_format']:6.1%} {s['loose_format']:6.1%} "
            f"{s['ran_out_of_room']:10.1%}  {s['accuracy_strict']:8.1%}"
        )


if __name__ == "__main__":
    main()
