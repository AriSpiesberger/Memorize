"""Build the general-chat replay set: everyday instruction data with no math or science.

    python -m memorize.general_data            # writes data/general/{train,valid}.jsonl

label_split mixes this in while it trains on multiple-choice letters, so general
instruction following has something to hold onto, and scores the held-out part
every eval to show whether it drifts. Sources are the ones memorize.sft_data uses:

  databricks/databricks-dolly-15k                     creative writing, brainstorming,
                                                      summarization, classification
  allenai/tulu-3-sft-personas-instruction-following  prompts with explicit output constraints

Chats that touch math, science, or multiple-choice format are dropped, as is
anything already in data/sft (the instruct model has seen it). Each row is
{"messages": [...]}.
"""

import argparse
import json
import random
import re
from pathlib import Path

from datasets import load_dataset
from transformers import AutoTokenizer

from memorize.sft_data import constraint_chats, keep

OUT_DIR = Path(__file__).parent.parent / "data" / "general"
SFT_DIR = OUT_DIR.parent / "sft"
DOLLY_CATEGORIES = {"creative_writing", "brainstorming", "summarization", "classification"}

# Deliberately broad: a false positive just costs one chat out of tens of thousands.
STEM = re.compile(
    r"\b(math\w*|algebra\w*|calculus|geometr\w*|trigonometr\w*|theorem|equation\w*|integral|derivative"
    r"|probabilit\w*|statistic\w*|arithmetic|fraction\w*|polynomial|logarithm\w*|calculat\w*|formula\w*"
    r"|physic\w*|chemi\w*|biolog\w*|molecul\w*|atom\w*|quantum|relativity|gravit\w*|electr\w*|magnet\w*"
    r"|neutron|proton|enzyme\w*|dna|rna|genes?|genetic\w*|protein\w*|cells?|bacteri\w*|virus\w*|species"
    r"|evolution\w*|ecosystem\w*|photosynthesis|climate|geolog\w*|astronom\w*|planets?|galax\w*|cosmos|cosmic"
    r"|scien\w*|experiment\w*|hypothes\w*|laborator\w*|engineer\w*|algorithm\w*|computer science"
    r"|machine learning|neural|medic\w*|clinical|anatom\w*|physiolog\w*|neuro\w*|pharma\w*|disease\w*"
    r"|periodic table|thermodynamic\w*|kinetic|velocity|momentum|voltage|circuit\w*|solve|proof)\b",
    re.IGNORECASE,
)


def dolly_chats():
    for r in load_dataset("databricks/databricks-dolly-15k", split="train"):
        if r["category"] not in DOLLY_CATEGORIES or len(r["response"].strip()) < 3:
            continue
        instruction, context = r["instruction"].strip(), r["context"].strip()
        user = instruction if not context else f"{instruction}\n\n{context}"
        yield [{"role": "user", "content": user}, {"role": "assistant", "content": r["response"].strip()}]


def seen_prompts():
    seen = set()
    for split in ("train", "valid"):
        path = SFT_DIR / f"{split}.jsonl"
        if path.exists():
            for line in open(path, encoding="utf-8"):
                seen.add(json.loads(line)["messages"][0]["content"])
    return seen


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tokenizer", default="Qwen/Qwen3.5-2B-Base")
    p.add_argument("--n-train", type=int, default=2000)
    p.add_argument("--n-valid", type=int, default=200)
    p.add_argument("--max-tokens", type=int, default=384, help="whole chat, so replies stay short")
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer)
    seen = seen_prompts()
    rows, dropped = [], {"stem": 0, "seen": 0, "format/length": 0}
    for name, chats in [("dolly", dolly_chats()), ("constraint", constraint_chats())]:
        n0 = len(rows)
        for messages in chats:
            if STEM.search(" ".join(m["content"] for m in messages)):
                dropped["stem"] += 1
            elif messages[0]["content"] in seen:
                dropped["seen"] += 1
            elif not keep(tokenizer, messages, args.max_tokens):
                dropped["format/length"] += 1
            else:
                rows.append(messages)
        print(f"{name}: {len(rows) - n0} usable chats")
    print("dropped:", dropped)

    random.Random(args.seed).shuffle(rows)
    need = args.n_train + args.n_valid
    if len(rows) < need:
        raise SystemExit(f"only {len(rows)} usable chats, need {need}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for split, part in [("valid", rows[: args.n_valid]), ("train", rows[args.n_valid : need])]:
        with open(OUT_DIR / f"{split}.jsonl", "w", encoding="utf-8") as f:
            for messages in part:
                f.write(json.dumps({"messages": messages}, ensure_ascii=False) + "\n")
        print(f"{split}: {len(part)} -> {OUT_DIR / f'{split}.jsonl'}")


if __name__ == "__main__":
    main()
