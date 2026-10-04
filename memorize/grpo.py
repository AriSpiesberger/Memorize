"""GRPO with a KL penalty, on multiple-choice questions, with a LoRA on mlx-lm.

    python -m memorize.grpo --model models/sft-fused --out adapters/grpo-run1

Each step samples `--questions` training questions, generates `--group`
replies per question, and rewards a reply 1 if its last line is
`ANSWER: <letter>` with the right letter, `--format-reward` if the line is
well formed but wrong, and 0 otherwise. Advantages are normalised within each
group. The loss is the token-level policy gradient plus `--beta` times the k3
KL estimate against the starting policy, which is the same model with the
LoRA switched off, so no second copy of the weights is needed.

Training questions come from the part of each benchmark outside the seeded
held-out eval split (`benchmarks.split`), so evaluation stays clean.
"""

import argparse
import json
import math
import random
import re
import time
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
from mlx.utils import tree_flatten, tree_map
from mlx_lm import load
from mlx_lm.generate import BatchGenerator
from mlx_lm.sample_utils import make_sampler
from mlx_lm.tuner.lora import LoRALinear
from mlx_lm.tuner.trainer import grad_checkpoint
from mlx_lm.tuner.utils import linear_to_lora_layers

from memorize import benchmarks

LETTERS = benchmarks.LETTERS
# EvalScope's zero-shot chain-of-thought prompt (MMLU-Pro adapter), verbatim.
PROMPT = (
    "Answer the following multiple choice question. The last line of your response"
    " should be of the following format: 'ANSWER: [LETTER]' (without quotes) where"
    " [LETTER] is one of {letters}. Think step by step before answering.\n\n"
    "Question:\n{question}\nOptions:\n{choices}\n"
)
LAST_LINE_RE = re.compile(r"ANSWER:\s*([A-J])\s*")


def build_prompt(tokenizer, item):
    n = len(item["options"])
    text = PROMPT.format(
        letters=",".join(LETTERS[:n]),
        question=item["question"],
        choices="\n".join(f"{LETTERS[i]}) {o}" for i, o in enumerate(item["options"])),
    )
    return tokenizer.apply_chat_template(
        [{"role": "user", "content": text}],
        add_generation_prompt=True,
        enable_thinking=False,
    )


def reward(text, gold, format_reward):
    """1 for a correct, well-formed last line; `format_reward` for a well-formed
    wrong one; 0 when the last line is not `ANSWER: X`."""
    lines = [l for l in text.strip().splitlines() if l.strip()]
    m = LAST_LINE_RE.fullmatch(lines[-1].strip()) if lines else None
    if not m:
        return 0.0, None
    pred = m.group(1)
    return (1.0 if pred == gold else format_reward), pred


def lora_layers(model):
    return [m for _, m in model.named_modules() if isinstance(m, LoRALinear)]


def reference_logprobs(model, tokens, n_prompt):
    """Log-probs of the completion under the starting policy (LoRA off)."""
    layers = lora_layers(model)
    scales = [l.scale for l in layers]
    for l in layers:
        l.scale = 0.0
    lp = token_logprobs(model, tokens, n_prompt)
    for l, s in zip(layers, scales):
        l.scale = s
    return mx.stop_gradient(lp)


def token_logprobs(model, tokens, n_prompt):
    x = mx.array(tokens)[None]
    logits = model(x[:, :-1]).astype(mx.float32)
    lp = logits - mx.logsumexp(logits, axis=-1, keepdims=True)
    lp = mx.take_along_axis(lp, x[:, 1:, None], axis=-1)[0, :, 0]
    return lp[n_prompt - 1 :]


def generate(model, tokenizer, prompts, max_new, batch_size, stop_ids):
    gen = BatchGenerator(
        model,
        stop_tokens=[[t] for t in stop_ids],
        sampler=make_sampler(temp=1.0),
        completion_batch_size=batch_size,
        prefill_batch_size=min(batch_size, 8),
    )
    owner, out = {}, [None] * len(prompts)
    for i, p in enumerate(prompts):
        (uid,) = gen.insert([list(p)], [max_new])
        owner[uid] = i
        out[i] = []
    finished = [None] * len(prompts)
    while responses := gen.next_generated():
        for r in responses:
            i = owner[r.uid]
            out[i].append(r.token)
            if r.finish_reason is not None:
                finished[i] = r.finish_reason
    gen.close()
    mx.clear_cache()
    return out, finished


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", required=True, help="instruction-tuned starting model")
    p.add_argument("--out", required=True, help="adapter directory")
    p.add_argument("--bench", default="mmlu_pro")
    p.add_argument("--heldout", type=int, default=300, help="eval questions to skip")
    p.add_argument("--steps", type=int, default=100)
    p.add_argument("--questions", type=int, default=4, help="questions per step")
    p.add_argument("--group", type=int, default=8, help="replies per question")
    p.add_argument("--max-new", type=int, default=768)
    p.add_argument("--beta", type=float, default=0.04)
    p.add_argument("--format-reward", type=float, default=0.1)
    # mlx-lm's LoRA scales its update by 20, so keep the learning rate low.
    p.add_argument("--lr", type=float, default=1e-5)
    p.add_argument("--clip", type=float, default=1.0, help="max gradient norm")
    p.add_argument("--show-every", type=int, default=5, help="print sample replies")
    p.add_argument("--rank", type=int, default=8)
    p.add_argument("--gen-batch", type=int, default=16)
    p.add_argument("--save-every", type=int, default=10)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()

    random.seed(args.seed)
    mx.random.seed(args.seed)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    lora_config = {"rank": args.rank, "dropout": 0.0, "scale": 20.0}
    with open(out / "adapter_config.json", "w") as f:
        json.dump(
            {
                "fine_tune_type": "lora",
                "num_layers": -1,
                "lora_parameters": lora_config,
                "model": args.model,
                "grpo": vars(args),
            },
            f,
            indent=2,
        )

    model, tokenizer = load(args.model)
    model.freeze()
    linear_to_lora_layers(model, -1, lora_config)
    grad_checkpoint(model.layers[0])
    n_train = sum(v.size for _, v in tree_flatten(model.trainable_parameters()))
    print(f"trainable parameters: {n_train / 1e6:.2f}M", flush=True)

    stop_ids = set(tokenizer.eos_token_ids)
    stop_ids |= set(tokenizer.encode("<|im_end|>", add_special_tokens=False))
    _, pool = benchmarks.split(args.bench, args.heldout, 0)
    optimizer = optim.Adam(learning_rate=args.lr)

    def loss_fn(model, tokens, n_prompt, adv, ref_lp, n_total):
        lp = token_logprobs(model, tokens, n_prompt)
        ratio = mx.exp(lp - mx.stop_gradient(lp))
        pg = -(adv * ratio)
        diff = ref_lp - lp
        kl = mx.exp(diff) - diff - 1
        return (pg + args.beta * kl).sum() / n_total, kl.sum()

    loss_and_grad = nn.value_and_grad(model, loss_fn)
    log = open(out / "log.jsonl", "a")

    for step in range(1, args.steps + 1):
        t0 = time.time()
        items = random.sample(pool, args.questions)
        prompts = [build_prompt(tokenizer, it) for it in items]
        model.eval()
        completions, finished = generate(
            model,
            tokenizer,
            [pr for pr in prompts for _ in range(args.group)],
            args.max_new,
            args.gen_batch,
            stop_ids,
        )
        t_gen = time.time() - t0

        samples, rewards, preds, texts = [], [], [], []
        for q, it in enumerate(items):
            group = range(q * args.group, (q + 1) * args.group)
            rs = []
            for j in group:
                text = tokenizer.decode([t for t in completions[j] if t not in stop_ids])
                r, pred = reward(text, it["answer"], args.format_reward)
                texts.append(text)
                rs.append(r)
                preds.append(pred)
            rewards += rs
            mean = sum(rs) / len(rs)
            std = math.sqrt(sum((r - mean) ** 2 for r in rs) / len(rs))
            if std < 1e-6:
                continue  # every reply scored the same: no signal
            for j, r in zip(group, rs):
                samples.append((list(prompts[q]) + completions[j], len(prompts[q]), (r - mean) / std))

        model.train()
        n_total = sum(len(s[0]) - s[1] for s in samples)
        grads, kl_sum = None, 0.0
        for tokens, n_prompt, adv in samples:
            ref_lp = reference_logprobs(model, tokens, n_prompt)
            (_, kl), g = loss_and_grad(model, tokens, n_prompt, adv, ref_lp, n_total)
            grads = g if grads is None else tree_map(mx.add, grads, g)
            mx.eval(grads, kl)
            kl_sum += kl.item()
        grad_norm = 0.0
        if grads is not None:
            grads, norm = optim.clip_grad_norm(grads, args.clip)
            optimizer.update(model, grads)
            mx.eval(model.trainable_parameters(), optimizer.state, norm)
            grad_norm = norm.item()
        mx.clear_cache()

        n = len(rewards)
        rec = {
            "step": step,
            "reward": sum(rewards) / n,
            "accuracy": sum(r == 1.0 for r in rewards) / n,
            "format": sum(p is not None for p in preds) / n,
            "truncated": sum(f == "length" for f in finished) / n,
            "mean_len": sum(len(c) for c in completions) / n,
            "kl": kl_sum / max(n_total, 1),
            "grad_norm": grad_norm,
            "trained_on": len(samples),
            "gen_s": round(t_gen, 1),
            "step_s": round(time.time() - t0, 1),
            "peak_gb": round(mx.get_peak_memory() / 1e9, 1),
        }
        log.write(json.dumps(rec) + "\n")
        log.flush()
        print(
            f"step {step:4d}  reward {rec['reward']:.3f}  acc {rec['accuracy']:.3f}  "
            f"format {rec['format']:.2f}  len {rec['mean_len']:.0f}  kl {rec['kl']:.4f}  "
            f"grad {rec['grad_norm']:.2f}  "
            f"trained {rec['trained_on']}  {rec['step_s']:.0f}s  peak {rec['peak_gb']} GB",
            flush=True,
        )
        if step % args.show_every == 0 or step == 1:
            # The best and worst reply to the first question of the step.
            group = list(range(args.group))
            best = max(group, key=lambda j: rewards[j])
            worst = min(group, key=lambda j: rewards[j])
            print(f"  question {items[0]['id']} ({items[0]['subject']}), gold {items[0]['answer']}")
            for label, j in [("best", best), ("worst", worst)]:
                tail = " ".join(texts[j].split())[-300:]
                print(f"  [{label}: reward {rewards[j]:.1f}, {len(completions[j])} tokens] ...{tail}")
            print(flush=True)
        if step % args.save_every == 0 or step == args.steps:
            weights = dict(tree_flatten(model.trainable_parameters()))
            mx.save_safetensors(str(out / "adapters.safetensors"), weights)
            mx.save_safetensors(str(out / f"{step:05d}_adapters.safetensors"), weights)


if __name__ == "__main__":
    main()
