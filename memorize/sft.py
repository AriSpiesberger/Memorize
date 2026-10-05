"""Instruction-tune a base model with a LoRA, watching it learn as it goes.

    python -m memorize.sft_data                                  # build data/sft/
    python -m memorize.sft --out adapters/sft-run2

Prints training loss as it runs, validation loss at regular intervals, and
after every epoch (and once before training) answers a fixed set of probes:
short instructions with checkable output constraints, plus a few held-out
MMLU-Pro questions in the RL prompt format. Each probe is marked pass or fail.

Loss is on the assistant reply only. The adapter is saved after every epoch
in mlx-lm's format, so `mlx_lm.load(model, adapter_path=out)` reads it.
"""

import argparse
import json
import math
import random
import time
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np
from mlx.utils import tree_flatten, tree_map
from mlx_lm import load
from mlx_lm.generate import BatchGenerator
from mlx_lm.sample_utils import make_sampler
from mlx_lm.tuner.trainer import grad_checkpoint
from mlx_lm.tuner.utils import linear_to_lora_layers

from memorize import benchmarks, grpo

DATA_DIR = Path(__file__).parent.parent / "data" / "sft"


def _json_capital(text):
    try:
        return "tokyo" in str(json.loads(text.strip().strip("`").removeprefix("json"))["capital"]).lower()
    except Exception:
        return False


# (prompt, check) pairs: each check looks only at the reply text.
INSTRUCTION_PROBES = [
    (
        "Name three fruits. Write your entire answer in capital letters.",
        lambda t: any(c.isalpha() for c in t) and t == t.upper(),
    ),
    (
        'What is the capital of Japan? Reply with JSON containing a single key "capital" and nothing else.',
        _json_capital,
    ),
    (
        "Is the Pacific the largest ocean on Earth? Answer with exactly one word: yes or no.",
        lambda t: t.strip().strip(".!").lower() in ("yes", "no"),
    ),
    (
        'Write one sentence about the moon that ends with the word "tonight".',
        lambda t: t.strip().rstrip(".!\"'").lower().endswith("tonight"),
    ),
    (
        "List two primary colors as a bulleted list where every line starts with '- ', and write nothing else.",
        lambda t: len(_lines(t)) == 2 and all(l.startswith("- ") for l in _lines(t)),
    ),
    (
        "What is 7 plus 5? Reply with only the number.",
        lambda t: t.strip().rstrip(".") == "12",
    ),
    (
        "Write the word hello in all lowercase letters and nothing else.",
        lambda t: t.strip().strip(".!\"'") == "hello",
    ),
    (
        "Describe a cat in fewer than 15 words.",
        lambda t: 0 < len(t.split()) < 15,
    ),
    (
        "Give exactly three words that describe the ocean, separated by commas, and nothing else.",
        lambda t: len(parts := [w.strip() for w in t.strip().rstrip(".").split(",")]) == 3
        and all(len(w.split()) == 1 for w in parts),
    ),
    (
        "Name three planets as a numbered list in the form '1. ...', '2. ...', '3. ...', and write nothing else.",
        lambda t: [l[:3] for l in _lines(t)] == ["1. ", "2. ", "3. "],
    ),
    (
        "Why is the sky blue? Answer in exactly two sentences.",
        lambda t: _sentences(t) == 2,
    ),
    (
        "Translate 'good morning' into French. Reply with the translation only.",
        lambda t: "bonjour" in t.lower() and len(t.split()) <= 3,
    ),
    (
        "Write one sentence that uses both the word 'river' and the word 'lantern'.",
        lambda t: "river" in t.lower() and "lantern" in t.lower() and _sentences(t) == 1,
    ),
    (
        "Start your reply with the word 'Certainly' and then name one color.",
        lambda t: t.strip().startswith("Certainly"),
    ),
    (
        "What is the largest planet in the solar system? Wrap your entire answer in double quotation marks.",
        lambda t: len(t.strip()) > 2 and t.strip()[0] in "\"“" and t.strip()[-1] in "\"”",
    ),
    (
        "Describe a sunset in two sentences without using any commas.",
        lambda t: "," not in t and _sentences(t) == 2,
    ),
    (
        "Give a title for a story about a lost dog, wrapped in double angle brackets like <<title>>, and nothing else.",
        lambda t: t.strip().startswith("<<") and t.strip().endswith(">>"),
    ),
    (
        "请只用一个词回答：晴天时天空通常是什么颜色？",
        lambda t: "蓝" in t and len(t.strip().strip("。.")) <= 4,
    ),
    (
        "用中文列出三种水果，每行一种，不要写其他内容。",
        lambda t: len(_lines(t)) == 3 and not any(c.isascii() and c.isalpha() for c in t),
    ),
]


def _lines(text):
    return [l.strip() for l in text.strip().splitlines() if l.strip()]


def _sentences(text):
    """Sentence count by terminal punctuation (., !, ? and their CJK forms)."""
    import re

    return len(re.findall(r"[.!?。！？]+(?=\s|$)", text.strip()))


def load_split(path, tokenizer, max_seq):
    """Token ids and prompt length per chat; the loss covers what follows the prompt."""
    rows, skipped = [], 0
    for line in open(path):
        messages = json.loads(line)["messages"]
        full = tokenizer.apply_chat_template(messages, tokenize=False)
        prompt = tokenizer.apply_chat_template(
            messages[:-1], tokenize=False, add_generation_prompt=True, enable_thinking=False
        )
        ids = tokenizer.encode(full, add_special_tokens=False)[:max_seq]
        n_prompt = len(tokenizer.encode(prompt, add_special_tokens=False))
        if not full.startswith(prompt) or n_prompt >= len(ids):
            skipped += 1
            continue
        rows.append((ids, n_prompt))
    return rows, skipped


def to_batch(rows):
    length = max(len(ids) for ids, _ in rows)
    tokens = np.zeros((len(rows), length), dtype=np.int32)
    mask = np.zeros((len(rows), length - 1), dtype=np.float32)
    for i, (ids, n_prompt) in enumerate(rows):
        tokens[i, : len(ids)] = ids
        mask[i, n_prompt - 1 : len(ids) - 1] = 1.0  # targets that are reply tokens
    tokens = mx.array(tokens)
    return tokens[:, :-1], tokens[:, 1:], mx.array(mask)


def pack(rows, max_tokens):
    """Group rows into batches whose padded size (rows x longest) fits
    `max_tokens`; memory scales with that size, about 4 GB per 512 tokens."""
    batches, current = [], []
    for row in sorted(rows, key=lambda r: len(r[0])):
        if current and (len(current) + 1) * len(row[0]) > max_tokens:
            batches.append(current)
            current = []
        current.append(row)
    if current:
        batches.append(current)
    return batches


def loss_fn(model, inputs, targets, mask):
    logits = model(inputs).astype(mx.float32)
    ce = nn.losses.cross_entropy(logits, targets) * mask
    n = mask.sum()
    return ce.sum() / n, n


def evaluate(model, rows, max_tokens):
    total, n_tokens = 0.0, 0.0
    for batch in pack(rows, max_tokens):
        loss, n = loss_fn(model, *to_batch(batch))
        mx.eval(loss, n)
        total += loss.item() * n.item()
        n_tokens += n.item()
    return total / n_tokens


def run_probes(model, tokenizer, mmlu_items, label):
    stop_ids = set(tokenizer.eos_token_ids)
    stop_ids |= set(tokenizer.encode("<|im_end|>", add_special_tokens=False))
    prompts, limits = [], []
    for text, _ in INSTRUCTION_PROBES:
        prompts.append(
            tokenizer.apply_chat_template(
                [{"role": "user", "content": text}], add_generation_prompt=True, enable_thinking=False
            )
        )
        limits.append(200)
    for item in mmlu_items:
        prompts.append(grpo.build_prompt(tokenizer, item))
        limits.append(768)

    model.eval()
    gen = BatchGenerator(
        model,
        stop_tokens=[[t] for t in stop_ids],
        sampler=make_sampler(temp=0.0),
        completion_batch_size=len(prompts),
        prefill_batch_size=8,
    )
    owner, out = {}, [[] for _ in prompts]
    for i, (p, limit) in enumerate(zip(prompts, limits)):
        (uid,) = gen.insert([list(p)], [limit])
        owner[uid] = i
    while responses := gen.next_generated():
        for r in responses:
            if r.token not in stop_ids:
                out[owner[r.uid]].append(r.token)
    gen.close()
    mx.clear_cache()
    replies = [tokenizer.decode(t) for t in out]

    def show(text, width=220):
        text = " ".join(text.split())
        return text if len(text) <= width else text[: width - 3] + "..."

    print(f"\n----- probes: {label} -----", flush=True)
    passed = 0
    for (prompt, check), reply in zip(INSTRUCTION_PROBES, replies):
        ok = bool(check(reply))
        passed += ok
        print(f"[{'PASS' if ok else 'FAIL'}] {show(prompt, 90)}\n       -> {show(reply)}")
    formatted = correct = 0
    for item, reply in zip(mmlu_items, replies[len(INSTRUCTION_PROBES) :]):
        _, pred = grpo.reward(reply, item["answer"], 0.0)
        formatted += pred is not None
        correct += pred == item["answer"]
        mark = "PASS" if pred == item["answer"] else ("WRONG" if pred else "NO FORMAT")
        print(
            f"[{mark}] mmlu {item['id']} ({item['subject']}) gold {item['answer']}, "
            f"pred {pred}, {len(reply.split())} words\n       -> ...{show(reply[-200:], 200)}"
        )
    print(
        f"----- instructions {passed}/{len(INSTRUCTION_PROBES)}, mmlu format "
        f"{formatted}/{len(mmlu_items)}, mmlu correct {correct}/{len(mmlu_items)} -----\n",
        flush=True,
    )


def save(model, out, name):
    weights = dict(tree_flatten(model.trainable_parameters()))
    mx.save_safetensors(str(out / name), weights)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", default="Qwen/Qwen3.5-2B-Base")
    p.add_argument("--data", default=str(DATA_DIR), help="dir with train.jsonl, valid.jsonl")
    p.add_argument("--out", required=True, help="adapter directory")
    p.add_argument("--epochs", type=int, default=1)
    p.add_argument("--batch-size", type=int, default=8, help="chats per optimizer step")
    p.add_argument(
        "--max-batch-tokens",
        type=int,
        default=1536,
        help="padded tokens per forward pass; ~16 GB peak at 1536 (3 x 512)",
    )
    # mlx-lm's LoRA multiplies its update by `scale` (20), so learning rates
    # that suit other LoRA setups are ~10x too high here.
    p.add_argument("--lr", type=float, default=1e-5)
    p.add_argument("--clip", type=float, default=20.0, help="max gradient norm")
    p.add_argument("--warmup", type=int, default=20, help="optimizer steps")
    p.add_argument("--rank", type=int, default=8)
    p.add_argument("--max-seq", type=int, default=512)
    p.add_argument("--resume-adapter", help="adapters.safetensors to start from")
    p.add_argument("--report-every", type=int, default=25, help="optimizer steps")
    p.add_argument("--eval-every", type=int, default=100, help="optimizer steps")
    p.add_argument(
        "--cache-gb",
        type=float,
        default=2.0,
        help="cap on MLX's cache of freed buffers; uncapped it grows until macOS swaps",
    )
    p.add_argument("--n-mmlu-probes", type=int, default=0)
    p.add_argument("--no-grad-checkpoint", action="store_true")
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()

    random.seed(args.seed)
    mx.random.seed(args.seed)
    # Packed batches vary in shape, so freed buffers rarely get reused; cap the
    # cache and keep the weights resident instead of letting them page out.
    mx.set_cache_limit(int(args.cache_gb * 1e9))
    mx.set_wired_limit(mx.device_info()["max_recommended_working_set_size"])
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    lora_config = {"rank": args.rank, "dropout": 0.0, "scale": 20.0}
    with open(out / "adapter_config.json", "w") as f:
        json.dump(
            {"fine_tune_type": "lora", "num_layers": -1, "lora_parameters": lora_config, "sft": vars(args)},
            f,
            indent=2,
        )

    model, tokenizer = load(args.model)
    model.freeze()
    linear_to_lora_layers(model, -1, lora_config)
    if args.resume_adapter:
        model.load_weights(args.resume_adapter, strict=False)
    if not args.no_grad_checkpoint:
        grad_checkpoint(model.layers[0])
    n_params = sum(v.size for _, v in tree_flatten(model.trainable_parameters()))

    train, skipped_t = load_split(Path(args.data) / "train.jsonl", tokenizer, args.max_seq)
    valid, skipped_v = load_split(Path(args.data) / "valid.jsonl", tokenizer, args.max_seq)
    mmlu_items = benchmarks.split("mmlu_pro", 300, 0)[0][: args.n_mmlu_probes]
    per_step = args.batch_size
    steps_per_epoch = math.ceil(len(train) / per_step)
    total_steps = steps_per_epoch * args.epochs
    print(
        f"model {args.model} | LoRA rank {args.rank}, {n_params / 1e6:.1f}M trainable\n"
        f"train {len(train)} chats ({skipped_t} skipped), valid {len(valid)} ({skipped_v} skipped)\n"
        f"{args.epochs} epochs x {steps_per_epoch} optimizer steps "
        f"({args.batch_size} chats each, packed into passes of <= {args.max_batch_tokens} "
        f"tokens), lr {args.lr}",
        flush=True,
    )

    warmup = min(args.warmup, total_steps)
    schedule = optim.join_schedules(
        [
            optim.linear_schedule(args.lr * 0.01, args.lr, warmup),
            optim.cosine_decay(args.lr, max(total_steps - warmup, 1), args.lr * 0.1),
        ],
        [warmup],
    )
    optimizer = optim.Adam(learning_rate=schedule)
    loss_and_grad = nn.value_and_grad(model, loss_fn)

    run_probes(model, tokenizer, mmlu_items, "before training")
    val = evaluate(model, valid, args.max_batch_tokens)
    print(f"step 0 | valid loss {val:.3f}", flush=True)
    best = val

    step = 0
    for epoch in range(1, args.epochs + 1):
        order = list(range(len(train)))
        random.shuffle(order)
        model.train()
        window_loss, window_tokens, window_norms, t0 = 0.0, 0.0, [], time.time()
        for start in range(0, len(order), per_step):
            chunk = [train[i] for i in order[start : start + per_step]]
            grads, n_chunk = None, sum(len(ids) - n for ids, n in chunk)
            for batch in pack(chunk, args.max_batch_tokens):
                (loss, n), g = loss_and_grad(model, *to_batch(batch))
                # Weight each micro-batch by its share of the reply tokens.
                g = tree_map(lambda x: x * (n / n_chunk), g)
                grads = g if grads is None else tree_map(mx.add, grads, g)
                mx.eval(grads, loss, n)
                window_loss += loss.item() * n.item()
                window_tokens += n.item()
            grads, norm = optim.clip_grad_norm(grads, args.clip)
            optimizer.update(model, grads)
            mx.eval(model.trainable_parameters(), optimizer.state, norm)
            window_norms.append(norm.item())
            step += 1

            if step % args.report_every == 0:
                elapsed = time.time() - t0
                print(
                    f"epoch {epoch} step {step}/{total_steps} | train loss "
                    f"{window_loss / window_tokens:.3f} | lr {optimizer.learning_rate.item():.2e} | "
                    f"grad norm {sum(window_norms) / len(window_norms):.2f} "
                    f"(max {max(window_norms):.2f}) | "
                    f"{window_tokens / elapsed:.0f} tok/s | peak {mx.get_peak_memory() / 1e9:.1f} GB, "
                    f"cache {mx.get_cache_memory() / 1e9:.1f} GB",
                    flush=True,
                )
                window_loss, window_tokens, window_norms, t0 = 0.0, 0.0, [], time.time()
            if step % args.eval_every == 0:
                val = evaluate(model, valid, args.max_batch_tokens)
                best = min(best, val)
                print(f"step {step} | valid loss {val:.3f} (best {best:.3f})", flush=True)
                model.train()

        val = evaluate(model, valid, args.max_batch_tokens)
        best = min(best, val)
        print(f"== end of epoch {epoch} | valid loss {val:.3f} (best {best:.3f})", flush=True)
        save(model, out, "adapters.safetensors")
        save(model, out, f"epoch{epoch}_adapters.safetensors")
        run_probes(model, tokenizer, mmlu_items, f"after epoch {epoch}")
        mx.clear_cache()

    print(f"saved adapter to {out}", flush=True)


if __name__ == "__main__":
    main()
