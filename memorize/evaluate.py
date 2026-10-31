"""Score a model on the seeded held-out multiple-choice questions, or compare two runs. MLX (Apple Silicon).

    python -m memorize.evaluate budget   --name baseline --bench mmlu_pro mmlu_redux --n 300 --budget 2048
    python -m memorize.evaluate format   --model models/sft-fused --adapter-path memorize/adapters/grpo-run1 --name grpo-run1
    python -m memorize.evaluate mmlu_pro --mode chat_cot --adapter-path memorize/adapters/sft-run1 \\
        --out memorize/results/sft-run1-chat-cot/mmlu_pro.jsonl
    python -m memorize.evaluate compare  sft drgrpo-run1

budget    thinking on, up to --budget reasoning tokens a question (force-closed when they run out: engine.py), right
          or wrong per question.  -> results/<name>/<bench>.jsonl, summary.json
format    each benchmark's EvalScope prompt (prompts.py), greedy, thinking off. Headline: strict format, the last line
          exactly 'ANSWER: X' ('答案：X' for C-Eval); also loose format (a marker anywhere), ran out of room, accuracy, a
          few failing replies; then sft.py's 19 instruction probes (did RL cost general instruction following?).
          -> results/<name>/format_<bench>.jsonl, format_summary.json
mmlu_pro  MMLU-Pro alone, base or instruction-tuned. cot: the official protocol (TIGER-AI-Lab/MMLU-Pro
          evaluate_from_local.py: k-shot chain of thought from the validation split of the same subject, raw
          completion, greedy, 2048 new tokens, stop at "Question:", its three answer regexes, shots dropped until the
          prompt fits a 4096 context). direct: the same examples without the reasoning (not official; the
          no-reasoning reference). chat_cot / chat_direct: EvalScope's zero-shot prompts.  -> --out, <out>.summary.json
compare   two format runs question by question: the change in accuracy and in strict format, with McNemar's exact
          test (stats.py).

The same --n gives the same questions in every command, and an interrupted run resumes.
"""

import argparse
import json
import math
import re
import time
from pathlib import Path

from memorize import benchmarks, prompts

RESULTS_DIR = Path(__file__).parent / "results"
FORMAT_BENCH = ["mmlu_pro", "mmlu_redux", "ceval", "supergpqa"]
CHOICES = "ABCDEFGHIJKLMNOP"


def resume(path):
    """The records already in a results file, by question id."""
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return {r["id"]: r for r in map(json.loads, f)}


def append(f, done, rec):
    done[rec["id"]] = rec
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    f.flush()


def greedy(model, tok, prompt_ids, max_new, batch_size, on_done, chat=True, stop_text=None):
    """Greedy, batched decoding of token-id prompts; on_done(i, token ids, finish) as each one ends ("stop" or
    "length"). A chat reply also stops at <|im_end|> (the base tokenizer only stops on <|endoftext|>); stop_text
    ends a raw completion early."""
    import mlx.core as mx
    from mlx_lm.generate import BatchGenerator
    from mlx_lm.sample_utils import make_sampler

    stop_ids = set(tok.eos_token_ids)
    if chat:
        stop_ids |= set(tok.encode("<|im_end|>", add_special_tokens=False))
    gen = BatchGenerator(model, stop_tokens=[[t] for t in stop_ids], sampler=make_sampler(temp=0.0),
                         completion_batch_size=batch_size, prefill_batch_size=min(batch_size, 8))
    owner, toks = {}, {}
    for i, p in enumerate(prompt_ids):
        (uid,) = gen.insert([list(p)], [max_new])
        owner[uid], toks[uid] = i, []
    while responses := gen.next_generated():
        for r in responses:
            if r.token not in stop_ids:
                toks[r.uid].append(r.token)
            hit = stop_text is not None and stop_text in tok.decode(toks[r.uid][-8:])
            if r.finish_reason is not None:
                on_done(owner[r.uid], toks.pop(r.uid), "stop" if r.finish_reason == "stop" or hit else "length")
            elif hit:
                gen.remove([r.uid])
                on_done(owner[r.uid], toks.pop(r.uid), "stop")
    gen.close()
    mx.clear_cache()


# ------------------------------------------------------------------ budget
def budget(args):
    import mlx.core as mx
    from mlx_lm import load
    from memorize import engine

    mx.random.seed(args.seed)
    args.model = args.model or engine.MODEL
    model, tok = load(args.model, adapter_path=args.adapter_path)
    out_dir = RESULTS_DIR / args.name
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {}
    for bench in args.bench:
        items, _ = benchmarks.split(bench, args.n, args.split_seed)
        path = out_dir / f"{bench}.jsonl"
        done = resume(path)
        todo = [it for it in items if it["id"] not in done]
        print(f"{bench}: {len(items)} questions", flush=True)
        chats = [tok.apply_chat_template([{"role": "user", "content": benchmarks.format_prompt(it)}],
                                         add_generation_prompt=True, enable_thinking=not args.no_think) for it in todo]
        start, n_tokens = time.time(), 0
        with open(path, "a", encoding="utf-8") as f:

            def on_done(i, rollout):
                nonlocal n_tokens
                it, pred = todo[i], benchmarks.extract_answer(rollout.answer(tok))
                append(f, done, {"id": it["id"], "subject": it["subject"], "gold": it["answer"], "pred": pred,
                                 "correct": pred == it["answer"], "reasoning_tokens": rollout.reasoning_tokens,
                                 "total_tokens": len(rollout.tokens), "forced": rollout.forced,
                                 "text": tok.decode(rollout.tokens)})
                n_tokens += len(rollout.tokens)
                if len(done) % 10 == 0 or len(done) == len(items):
                    acc = sum(r["correct"] for r in done.values()) / len(done)
                    print(f"  {len(done)}/{len(items)}  acc {acc:.1%}  {n_tokens / (time.time() - start):.0f} tok/s  "
                          f"peak {mx.get_peak_memory() / 1e9:.1f} GB", flush=True)

            engine.generate(model, tok, chats, thinking=not args.no_think, budget=args.budget,
                            batch_size=args.batch_size, on_done=on_done)
        recs = [done[it["id"]] for it in items]
        n = len(recs)
        acc = sum(r["correct"] for r in recs) / n
        s = summary[bench] = {
            "n": n, "accuracy": acc, "stderr": math.sqrt(acc * (1 - acc) / n),
            "no_answer": sum(r["pred"] is None for r in recs) / n,
            "forced_close": sum(r["forced"] for r in recs) / n,
            "mean_reasoning_tokens": sum(r["reasoning_tokens"] for r in recs) / n,
            "mean_total_tokens": sum(r["total_tokens"] for r in recs) / n,
        }
        print(f"{bench}: {s['accuracy']:.1%} ± {s['stderr']:.1%}  (n={s['n']})", flush=True)
        with open(out_dir / "summary.json", "w", encoding="utf-8") as f:
            json.dump({"args": {k: v for k, v in vars(args).items() if k != "command"}, "results": summary}, f, indent=2)


# ------------------------------------------------------------------ format
def format_summary(recs):
    n = len(recs)
    return {
        "n": n,
        "strict_format": sum(r["strict"] is not None for r in recs) / n,
        "loose_format": sum(r["loose"] is not None for r in recs) / n,
        "ran_out_of_room": sum(r["finish"] == "length" for r in recs) / n,
        "accuracy_strict": sum(r["strict"] == r["gold"] for r in recs) / n,
        "accuracy_loose": sum(r["loose"] == r["gold"] for r in recs) / n,
        "median_tokens": sorted(r["tokens"] for r in recs)[n // 2],
    }


def format_(args):
    import mlx.core as mx
    from mlx_lm import load
    from memorize import sft

    mx.set_cache_limit(int(2e9))
    model, tok = load(args.model, adapter_path=args.adapter_path)
    out_dir = RESULTS_DIR / args.name
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {"model": args.model, "adapter": args.adapter_path, "results": {}}
    for bench in args.bench:
        items, _ = benchmarks.split(bench, args.n, 0)
        path = out_dir / f"format_{bench}.jsonl"
        done = resume(path)
        todo = [it for it in items if it["id"] not in done]
        print(f"{bench}: {len(todo)} to run, {len(done)} done", flush=True)
        chats = [tok.apply_chat_template([{"role": "user", "content": prompts.user_prompt(it)}],
                                         add_generation_prompt=True, enable_thinking=False) for it in todo]
        start = time.time()
        with open(path, "a", encoding="utf-8") as f:

            def on_done(i, t, finish):
                it, text = todo[i], tok.decode(t)
                append(f, done, {"id": it["id"], "subject": it["subject"], "gold": it["answer"],
                                 "strict": prompts.strict_answer(text, bench), "loose": prompts.loose_answer(text, bench),
                                 "tokens": len(t), "finish": finish, "text": text})
                if len(done) % 20 == 0 or len(done) == len(items):
                    s = format_summary(list(done.values()))
                    print(f"  {len(done)}/{len(items)}  strict format {s['strict_format']:.1%}  "
                          f"accuracy {s['accuracy_strict']:.1%}  {time.time() - start:.0f}s", flush=True)

            greedy(model, tok, chats, args.max_new, args.batch_size, on_done)
        recs = [done[it["id"]] for it in items]
        s = summary["results"][bench] = format_summary(recs)
        print(f"{bench}: strict format {s['strict_format']:.1%} | loose {s['loose_format']:.1%} | "
              f"ran out of room {s['ran_out_of_room']:.1%} | accuracy {s['accuracy_strict']:.1%} "
              f"(loose {s['accuracy_loose']:.1%}) | median {s['median_tokens']} tokens", flush=True)
        for r in [r for r in recs if r["strict"] is None][: args.show_failures]:
            print(f"  [no strict answer line, {r['finish']}, {r['tokens']} tokens] ...{' '.join(r['text'].split())[-200:]}")
        with open(out_dir / "format_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
    if not args.skip_probes:
        sft.run_probes(model, tok, [], "instruction following")
    print("\nbenchmark      strict  loose  out-of-room  accuracy")
    for bench, s in summary["results"].items():
        print(f"{bench:13s} {s['strict_format']:6.1%} {s['loose_format']:6.1%} "
              f"{s['ran_out_of_room']:10.1%}  {s['accuracy_strict']:8.1%}")


# ------------------------------------------------------------------ mmlu_pro
INITIAL_PROMPT = (
    "The following are multiple choice questions (with answers) about {$}. Think step by"
    ' step and then finish your answer with "the answer is (X)" where X is the correct'
    " letter choice.\n\n\n"
)
STOP = "Question:"
# Zero-shot chat prompts, verbatim from EvalScope (utils/multi_choices.py and the MMLU-Pro adapter)
CHAT_DIRECT = (
    "Answer the following multiple choice question. The entire content of your response"
    " should be of the following format: 'ANSWER: [LETTER]' (without quotes) where"
    " [LETTER] is one of {letters}.\n\nQuestion:\n{question}\nOptions:\n{choices}\n"
)
CHAT_COT = prompts.MMLU_PRO          # the same zero-shot prompt the RL and SFT scripts use
CHAT_ANSWER_RE = re.compile(r"(?i)ANSWER\s*:\s*\**\s*\(?([A-J])\b")


def format_example(example, mode, including_answer=True):
    prompt = "Question:\n" + example["question"] + "\nOptions:\n"
    for i, opt in enumerate(example["options"]):
        prompt += "{}. {}\n".format(CHOICES[i], opt)
    if mode == "cot":
        if including_answer:
            return prompt + example["cot_content"].replace("A: Let's think step by step.",
                                                           "Answer: Let's think step by step.") + "\n\n"
        return prompt + "Answer: Let's think step by step."
    if including_answer:
        return prompt + "Answer: The answer is ({}).\n\n".format(example["answer"])
    return prompt + "Answer: The answer is ("


def build_prompt(val, curr, k, mode):
    prompt = INITIAL_PROMPT.replace("{$}", curr["category"]) + "\n"
    for example in [e for e in val if e["category"] == curr["category"]][:k]:
        prompt += format_example(example, mode, True)
    return prompt + format_example(curr, mode, False)


def official_answer(text):
    """The official script's three regexes, in order."""
    m = re.search(r"answer is \(?([A-J])\)?", text)
    if m:
        return m.group(1)
    m = re.search(r".*[aA]nswer:\s*([A-J])", text)
    if m:
        return m.group(1)
    m = re.search(r"\b[A-J]\b(?!.*\b[A-J]\b)", text, re.DOTALL)
    return m.group(0) if m else None


def chat_prompt(tok, item, mode):
    n = len(item["options"])
    text = (CHAT_DIRECT if mode == "chat_direct" else CHAT_COT).format(
        letters=",".join(CHOICES[:n]), question=item["question"],
        choices="\n".join(f"{CHOICES[i]}) {o}" for i, o in enumerate(item["options"])))
    return tok.apply_chat_template([{"role": "user", "content": text}], add_generation_prompt=True,
                                   enable_thinking=False)


def last_line_ok(text):
    """What the RL reward requires: the last non-empty line is exactly 'ANSWER: X'."""
    lines = [l for l in text.strip().splitlines() if l.strip()]
    return bool(lines) and re.fullmatch(r"ANSWER:\s*[A-J]\s*", lines[-1].strip()) is not None


def mmlu_pro(args):
    import mlx.core as mx
    from datasets import load_dataset
    from mlx_lm import load

    model, tok = load(args.model, adapter_path=args.adapter_path)
    ds = load_dataset("TIGER-Lab/MMLU-Pro")
    val = [dict(r, options=[o for o in r["options"] if o != "N/A"]) for r in ds["validation"]]
    test = {str(r["question_id"]): dict(r, options=[o for o in r["options"] if o != "N/A"]) for r in ds["test"]}
    items = [test[it["id"]] for it in benchmarks.split("mmlu_pro", args.n, 0)[0]]   # the repo's seeded held-out split
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = resume(out)
    todo = [it for it in items if str(it["question_id"]) not in done]
    print(f"{args.mode}: {len(todo)} to run, {len(done)} done", flush=True)

    chat = args.mode.startswith("chat")
    max_new = {"cot": args.max_new, "chat_cot": args.max_new, "chat_direct": 32}.get(args.mode, 4)
    prompt_ids, shots = [], []
    for it in todo:
        k = 0 if chat else args.ntrain
        while not chat:
            p = tok.encode(build_prompt(val, it, k, args.mode))
            if len(p) < args.ctx - args.max_new or k == 0:
                break
            k -= 1
        prompt_ids.append(chat_prompt(tok, it, args.mode) if chat else p)
        shots.append(k)

    start, n_tok = time.time(), 0
    with open(out, "a", encoding="utf-8") as f:

        def on_done(i, t, finish):
            nonlocal n_tok
            it, text = todo[i], tok.decode(t) if chat else tok.decode(t).split(STOP)[0]
            if chat:
                m = CHAT_ANSWER_RE.findall(text)
                pred = m[-1].upper() if m else None
            elif args.mode == "direct":
                m = re.match(r"\s*([A-J])", text)
                pred = m.group(1) if m else None
            else:
                pred = official_answer(text)
            append(f, done, {"id": str(it["question_id"]), "subject": it["category"], "gold": it["answer"],
                             "pred": pred, "correct": pred == it["answer"], "n_options": len(it["options"]),
                             "shots": shots[i], "tokens": len(t), "finish": finish, "text": text})
            n_tok += len(t)
            if len(done) % 20 == 0 or len(done) == len(items):
                acc = sum(r["correct"] for r in done.values()) / len(done)
                print(f"  {len(done)}/{len(items)} acc {acc:.1%} {n_tok / (time.time() - start):.0f} tok/s "
                      f"peak {mx.get_peak_memory() / 1e9:.1f} GB", flush=True)

        greedy(model, tok, prompt_ids, max_new, args.batch_size, on_done, chat=chat, stop_text=None if chat else STOP)

    recs = [done[str(it["question_id"])] for it in items]
    n = len(recs)
    acc = sum(r["correct"] for r in recs) / n
    # The official script gives an unparsed answer a random guess; report its expected value, not one draw.
    guess = sum(1 / r["n_options"] for r in recs if r["pred"] is None) / n
    summary = {
        "model": args.model, "adapter": args.adapter_path, "mode": args.mode, "n": n,
        "accuracy_strict": acc, "accuracy_official_expected": acc + guess, "stderr": math.sqrt(acc * (1 - acc) / n),
        "no_answer": sum(r["pred"] is None for r in recs) / n,
        "hit_length": sum(r["finish"] == "length" for r in recs) / n,
        "strict_format": sum(last_line_ok(r["text"]) for r in recs) / n,
        "mean_tokens": sum(r["tokens"] for r in recs) / n,
        "shots": {str(k): sum(r["shots"] == k for r in recs) for k in range(args.ntrain + 1)},
    }
    print(json.dumps(summary, indent=1), flush=True)
    with open(out.with_suffix(".summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)


# ------------------------------------------------------------------ compare
def compare(args):
    from memorize.stats import describe, mcnemar

    print(f"{args.before} -> {args.after}\n")
    for bench in args.bench:
        a, b = (resume(RESULTS_DIR / name / f"format_{bench}.jsonl") for name in (args.before, args.after))
        ids = sorted(set(a) & set(b))
        if not ids:
            print(f"{bench:11s} no shared questions")
            continue
        for metric, value in [("accuracy", lambda r: r["strict"] == r["gold"]), ("format", lambda r: r["strict"] is not None)]:
            before, after = [value(a[i]) for i in ids], [value(b[i]) for i in ids]
            print(f"{bench:11s} {metric:8s} n={len(ids):3d}  {sum(before) / len(ids):6.1%} -> "
                  f"{sum(after) / len(ids):6.1%}  {describe(mcnemar(before, after))}")
        print()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)
    b = sub.add_parser("budget")
    b.add_argument("--name", required=True, help="memorize/results/<name>/")
    b.add_argument("--bench", nargs="+", default=list(benchmarks.BENCHMARKS))
    b.add_argument("--n", type=int, default=300, help="questions per benchmark")
    b.add_argument("--split-seed", type=int, default=0)
    b.add_argument("--model", default=None, help="default: engine.MODEL")
    b.add_argument("--adapter-path")
    b.add_argument("--no-think", action="store_true")
    b.add_argument("--budget", type=int, default=2048, help="reasoning tokens per question")
    b.add_argument("--batch-size", type=int, default=16)
    b.add_argument("--seed", type=int, default=0)
    f = sub.add_parser("format")
    f.add_argument("--model", default="Qwen/Qwen3.5-2B-Base")
    f.add_argument("--adapter-path")
    f.add_argument("--name", required=True, help="memorize/results/<name>/")
    f.add_argument("--bench", nargs="+", default=FORMAT_BENCH)
    f.add_argument("--n", type=int, default=100, help="questions per benchmark")
    f.add_argument("--max-new", type=int, default=2048)
    f.add_argument("--batch-size", type=int, default=16)
    f.add_argument("--show-failures", type=int, default=3)
    f.add_argument("--skip-probes", action="store_true")
    m = sub.add_parser("mmlu_pro")
    m.add_argument("--model", default="Qwen/Qwen3.5-2B-Base")
    m.add_argument("--adapter-path")
    m.add_argument("--mode", choices=["cot", "direct", "chat_direct", "chat_cot"], default="cot")
    m.add_argument("--n", type=int, default=300)
    m.add_argument("--ntrain", type=int, default=5)
    m.add_argument("--ctx", type=int, default=4096)
    m.add_argument("--max-new", type=int, default=2048)
    m.add_argument("--batch-size", type=int, default=16)
    m.add_argument("--out", required=True)
    c = sub.add_parser("compare")
    c.add_argument("before", help="memorize/results/<before>/")
    c.add_argument("after", help="memorize/results/<after>/")
    c.add_argument("--bench", nargs="+", default=FORMAT_BENCH)
    args = ap.parse_args()
    {"budget": budget, "format": format_, "mmlu_pro": mmlu_pro, "compare": compare}[args.command](args)


if __name__ == "__main__":
    main()
