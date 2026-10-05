"""MMLU-Pro on the seeded held-out questions, for base or instruction-tuned models.

    python -m memorize.eval_mmlu_pro --mode chat_cot --adapter-path adapters/sft-run1 \
        --out results/sft-run1-chat-cot/mmlu_pro.jsonl

Few-shot modes port the official MMLU-Pro script for a base (completion) model:

Follows TIGER-AI-Lab/MMLU-Pro evaluate_from_local.py: k-shot chain-of-thought
prompt built from the validation split of the same subject, raw completion (no
chat template), greedy decoding, 2048 new tokens, stop at "Question:", the same
three answer regexes, and shots dropped until the prompt fits a 4096 context.

--mode cot          official protocol
--mode direct       same examples with the reasoning removed (not an official
                    protocol; the "no reasoning" reference)

Zero-shot chat modes, for an instruction-tuned model, use EvalScope's prompts:
--mode chat_cot     think step by step, last line 'ANSWER: X' (the RL prompt)
--mode chat_direct  reply with only 'ANSWER: X'

Results are appended as they finish, so an interrupted run resumes.
"""

import argparse
import json
import math
import re
import time
from pathlib import Path

import mlx.core as mx
from datasets import load_dataset
from mlx_lm import load
from mlx_lm.generate import BatchGenerator
from mlx_lm.sample_utils import make_sampler

from memorize import benchmarks

CHOICES = "ABCDEFGHIJKLMNOP"
INITIAL_PROMPT = (
    "The following are multiple choice questions (with answers) about {$}. Think step by"
    ' step and then finish your answer with "the answer is (X)" where X is the correct'
    " letter choice.\n\n\n"
)
STOP = "Question:"


def format_example(example, mode, including_answer=True):
    prompt = "Question:\n" + example["question"] + "\nOptions:\n"
    for i, opt in enumerate(example["options"]):
        prompt += "{}. {}\n".format(CHOICES[i], opt)
    if mode == "cot":
        if including_answer:
            cot = example["cot_content"].replace(
                "A: Let's think step by step.", "Answer: Let's think step by step."
            )
            prompt += cot + "\n\n"
        else:
            prompt += "Answer: Let's think step by step."
    else:
        if including_answer:
            prompt += "Answer: The answer is ({}).\n\n".format(example["answer"])
        else:
            prompt += "Answer: The answer is ("
    return prompt


def build_prompt(val, curr, k, mode):
    prompt = INITIAL_PROMPT.replace("{$}", curr["category"]) + "\n"
    for example in [e for e in val if e["category"] == curr["category"]][:k]:
        prompt += format_example(example, mode, True)
    return prompt + format_example(curr, mode, False)


def extract_answer(text):
    m = re.search(r"answer is \(?([A-J])\)?", text)
    if m:
        return m.group(1)
    m = re.search(r".*[aA]nswer:\s*([A-J])", text)
    if m:
        return m.group(1)
    m = re.search(r"\b[A-J]\b(?!.*\b[A-J]\b)", text, re.DOTALL)
    return m.group(0) if m else None


# Zero-shot chat prompts, verbatim from EvalScope (utils/multi_choices.py and
# the MMLU-Pro adapter), for a model that follows instructions.
CHAT_DIRECT = (
    "Answer the following multiple choice question. The entire content of your response"
    " should be of the following format: 'ANSWER: [LETTER]' (without quotes) where"
    " [LETTER] is one of {letters}.\n\nQuestion:\n{question}\nOptions:\n{choices}\n"
)
CHAT_COT = (
    "Answer the following multiple choice question. The last line of your response"
    " should be of the following format: 'ANSWER: [LETTER]' (without quotes) where"
    " [LETTER] is one of {letters}. Think step by step before answering.\n\n"
    "Question:\n{question}\nOptions:\n{choices}\n"
)
CHAT_ANSWER_RE = re.compile(r"(?i)ANSWER\s*:\s*\**\s*\(?([A-J])\b")


def chat_prompt(tok, item, mode):
    n = len(item["options"])
    text = (CHAT_DIRECT if mode == "chat_direct" else CHAT_COT).format(
        letters=",".join(CHOICES[:n]),
        question=item["question"],
        choices="\n".join(f"{CHOICES[i]}) {o}" for i, o in enumerate(item["options"])),
    )
    return tok.apply_chat_template(
        [{"role": "user", "content": text}],
        add_generation_prompt=True,
        enable_thinking=False,
    )


def _last_line_ok(text):
    lines = [l for l in text.strip().splitlines() if l.strip()]
    return bool(lines) and re.fullmatch(r"ANSWER:\s*[A-J]\s*", lines[-1].strip()) is not None


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", default="Qwen/Qwen3.5-2B-Base")
    p.add_argument("--adapter-path")
    p.add_argument(
        "--mode", choices=["cot", "direct", "chat_direct", "chat_cot"], default="cot"
    )
    p.add_argument("--n", type=int, default=300)
    p.add_argument("--ntrain", type=int, default=5)
    p.add_argument("--ctx", type=int, default=4096)
    p.add_argument("--max-new", type=int, default=2048)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--out", required=True)
    args = p.parse_args()

    model, tok = load(args.model, adapter_path=args.adapter_path)
    ds = load_dataset("TIGER-Lab/MMLU-Pro")
    val = [dict(r, options=[o for o in r["options"] if o != "N/A"]) for r in ds["validation"]]
    test = {
        str(r["question_id"]): dict(r, options=[o for o in r["options"] if o != "N/A"])
        for r in ds["test"]
    }
    # Same seeded held-out split the rest of the repo uses.
    ids = [it["id"] for it in benchmarks.split("mmlu_pro", args.n, 0)[0]]
    items = [test[i] for i in ids]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {}
    if out.exists():
        done = {r["id"]: r for r in map(json.loads, open(out, encoding="utf-8"))}
    todo = [it for it in items if str(it["question_id"]) not in done]
    print(f"{args.mode}: {len(todo)} to run, {len(done)} done", flush=True)

    chat = args.mode.startswith("chat")
    max_new = {"cot": args.max_new, "chat_cot": args.max_new, "chat_direct": 32}.get(
        args.mode, 4
    )
    eos = set(tok.eos_token_ids)
    if chat:
        # The base tokenizer only stops on <|endoftext|>; a chat reply ends at <|im_end|>.
        eos |= set(tok.encode("<|im_end|>", add_special_tokens=False))
    gen = BatchGenerator(
        model,
        stop_tokens=[[t] for t in eos],
        sampler=make_sampler(temp=0.0),
        completion_batch_size=args.batch_size,
        prefill_batch_size=min(args.batch_size, 8),
    )
    owner, toks, shots = {}, {}, {}
    for i, it in enumerate(todo):
        k = 0 if chat else args.ntrain
        while not chat:
            prompt = tok.encode(build_prompt(val, it, k, args.mode))
            if len(prompt) < args.ctx - args.max_new or k == 0:
                break
            k -= 1
        if chat:
            prompt = chat_prompt(tok, it, args.mode)
        (uid,) = gen.insert([prompt], [max_new])
        owner[uid], toks[uid], shots[uid] = i, [], k

    start, n_tok = time.time(), 0
    with open(out, "a", encoding="utf-8") as f:

        def finish(uid, stopped):
            it, t = todo[owner[uid]], toks.pop(uid)
            text = tok.decode(t) if chat else tok.decode(t).split(STOP)[0]
            if chat:
                m = CHAT_ANSWER_RE.findall(text)
                pred = m[-1].upper() if m else None
            elif args.mode == "direct":
                m = re.match(r"\s*([A-J])", text)
                pred = m.group(1) if m else None
            else:
                pred = extract_answer(text)
            rec = {
                "id": str(it["question_id"]),
                "subject": it["category"],
                "gold": it["answer"],
                "pred": pred,
                "correct": pred == it["answer"],
                "n_options": len(it["options"]),
                "shots": shots[uid],
                "tokens": len(t),
                "finish": "stop" if stopped else "length",
                "text": text,
            }
            done[rec["id"]] = rec
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            if len(done) % 20 == 0 or len(done) == len(items):
                acc = sum(r["correct"] for r in done.values()) / len(done)
                print(
                    f"  {len(done)}/{len(items)} acc {acc:.1%} "
                    f"{n_tok / (time.time() - start):.0f} tok/s "
                    f"peak {mx.get_peak_memory() / 1e9:.1f} GB",
                    flush=True,
                )

        while responses := gen.next_generated():
            for r in responses:
                n_tok += 1
                if r.token not in eos:
                    toks[r.uid].append(r.token)
                hit_stop = not chat and STOP in tok.decode(toks[r.uid][-8:])
                if r.finish_reason is not None:
                    finish(r.uid, r.finish_reason == "stop" or hit_stop)
                elif hit_stop:
                    gen.remove([r.uid])
                    finish(r.uid, True)
    gen.close()

    recs = [done[str(it["question_id"])] for it in items]
    n = len(recs)
    acc = sum(r["correct"] for r in recs) / n
    # The official script gives an unparsed answer a random guess; report its
    # expected value rather than one random draw.
    guess = sum(1 / r["n_options"] for r in recs if r["pred"] is None) / n
    summary = {
        "model": args.model,
        "adapter": args.adapter_path,
        "mode": args.mode,
        "n": n,
        "accuracy_strict": acc,
        "accuracy_official_expected": acc + guess,
        "stderr": math.sqrt(acc * (1 - acc) / n),
        "no_answer": sum(r["pred"] is None for r in recs) / n,
        "hit_length": sum(r["finish"] == "length" for r in recs) / n,
        # What the RL reward requires: the last non-empty line is exactly 'ANSWER: X'.
        "strict_format": sum(_last_line_ok(r["text"]) for r in recs) / n,
        "mean_tokens": sum(r["tokens"] for r in recs) / n,
        "shots": {str(k): sum(r["shots"] == k for r in recs) for k in range(args.ntrain + 1)},
    }
    print(json.dumps(summary, indent=1), flush=True)
    json.dump(summary, open(out.with_suffix(".summary.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
