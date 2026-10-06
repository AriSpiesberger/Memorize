"""Build the instruction-tuning set: constraint-following chats plus general ones.

    python -m memorize.sft_data                # writes data/sft/{train,valid}.jsonl

Sources:
  allenai/tulu-3-sft-personas-instruction-following  prompts with explicit output
      constraints (format, length, keywords, case, ...)
  databricks/databricks-dolly-15k                     general human-written tasks

Multiple-choice items and step-by-step reasoning are dropped, so the benchmark
format and reasoning are left for RL to teach. Each row is {"messages": [...]}.
"""

import argparse
import json
import random
import re
from pathlib import Path

from datasets import load_dataset
from transformers import AutoTokenizer

OUT_DIR = Path(__file__).parent.parent / "data" / "sft"
EXCLUDE = re.compile(
    r"multiple[- ]choice|step by step|step-by-step|let's think|answer\s*:"
    r"|(^|\n)\s*\(?[A-D][\)\.]\s",
    re.IGNORECASE,
)


def n_tokens(tokenizer, messages):
    text = tokenizer.apply_chat_template(messages, tokenize=False)
    return len(tokenizer.encode(text, add_special_tokens=False))


def keep(tokenizer, messages, max_tokens):
    if any(EXCLUDE.search(m["content"]) for m in messages):
        return False
    return n_tokens(tokenizer, messages) <= max_tokens


def constraint_chats():
    for r in load_dataset("allenai/tulu-3-sft-personas-instruction-following", split="train"):
        messages = [m for m in r["messages"] if m["role"] in ("user", "assistant")]
        if [m["role"] for m in messages] == ["user", "assistant"]:
            yield messages


def general_chats():
    for r in load_dataset("databricks/databricks-dolly-15k", split="train"):
        instruction, context = r["instruction"].strip(), r["context"].strip()
        response = r["response"].strip()
        if len(response) < 3:
            continue
        user = instruction if not context else f"{instruction}\n\n{context}"
        yield [{"role": "user", "content": user}, {"role": "assistant", "content": response}]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tokenizer", default="Qwen/Qwen3.5-2B-Base")
    p.add_argument("--n-constraint", type=int, default=1800)
    p.add_argument("--n-general", type=int, default=600)
    p.add_argument("--n-valid", type=int, default=200)
    p.add_argument("--max-tokens", type=int, default=512)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer)
    rng = random.Random(args.seed)
    sources = {}
    for name, chats in [("constraint", constraint_chats()), ("general", general_chats())]:
        rows = [m for m in chats if keep(tokenizer, m, args.max_tokens)]
        rng.shuffle(rows)
        sources[name] = rows
        print(f"{name}: {len(rows)} usable chats")

    # Validation mirrors the training mix.
    frac = args.n_constraint / (args.n_constraint + args.n_general)
    n_valid_c = round(args.n_valid * frac)
    train = sources["constraint"][: args.n_constraint] + sources["general"][: args.n_general]
    valid = (
        sources["constraint"][args.n_constraint : args.n_constraint + n_valid_c]
        + sources["general"][args.n_general : args.n_general + args.n_valid - n_valid_c]
    )
    rng.shuffle(train)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for split, rows in [("train", train), ("valid", valid)]:
        with open(OUT_DIR / f"{split}.jsonl", "w", encoding="utf-8") as f:
            for messages in rows:
                f.write(json.dumps({"messages": messages}, ensure_ascii=False) + "\n")
        print(f"{split}: {len(rows)} -> {OUT_DIR / f'{split}.jsonl'}")


if __name__ == "__main__":
    main()
