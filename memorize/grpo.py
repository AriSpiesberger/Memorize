"""GRPO or Dr. GRPO on multiple-choice questions, as a LoRA on mlx-lm.

    python -m mlx_lm fuse --model Qwen/Qwen3.5-2B-Base --adapter-path adapters/sft-run2 \\
        --save-path models/sft-fused
    python -m memorize.grpo --model models/sft-fused --out adapters/grpo-run1

Each step samples `--questions` training questions and `--group` replies per
question (temperature 1). A reply earns 1 if its last line is the benchmark's
required answer line with the right letter, `--format-reward` if the line is
well formed but wrong, and 0 otherwise, including replies that run out of
room. The loss is the policy gradient plus `--beta` times the k3 estimate of
KL to the starting model, which is the same model with the LoRA switched off,
so no second copy of the weights is needed. One gradient update per batch of
fresh replies (mu = 1), so the PPO ratio is 1 and its clipping never binds.

--algo grpo     (DeepSeekMath) advantage = (r - group mean) / group std; each
                reply's loss is averaged over its own tokens, then over replies.
--algo dr_grpo  (Liu et al. 2025) advantage = r - group mean; token losses are
                summed and divided by a constant, replies x --max-new. Removes
                GRPO's bias toward long wrong replies and toward questions the
                model almost always gets right or wrong.

Groups where every reply scored the same have zero advantage and are skipped
(their only gradient would be the KL term); the normaliser still counts every
reply, so the gradient scale matches the full objective's.

What it prints:
  every step     reward, accuracy, format rate, out-of-room rate, reply length,
                 KL, gradient norm, timing
  every N steps  the best and worst reply to one question
  every M steps  a greedy check on fixed held-out questions from the training
                 benchmark and from every benchmark it does not train on
                 (`--track-bench`): strict format, accuracy, out-of-room, one
                 line per benchmark. These are the numbers to watch.

Training questions are a fixed, seeded set of `--train-n` per benchmark from
outside the held-out split (`benchmarks.split`), so held-out checks and later
evaluation stay clean. They are worked through in shuffled passes, each
question once per pass; their ids are saved to <out>/train_ids.json.
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
from mlx.utils import tree_flatten, tree_map
from mlx_lm import load
from mlx_lm.generate import BatchGenerator
from mlx_lm.sample_utils import make_sampler
from mlx_lm.tuner.lora import LoRALinear
from mlx_lm.tuner.trainer import grad_checkpoint
from mlx_lm.tuner.utils import linear_to_lora_layers

from memorize import benchmarks, prompts
from memorize.stats import describe, mcnemar


def chat_prompt(tokenizer, item):
    return tokenizer.apply_chat_template(
        [{"role": "user", "content": prompts.user_prompt(item)}],
        add_generation_prompt=True,
        enable_thinking=False,
    )


def reward(text, item, format_reward):
    pred = prompts.strict_answer(text, item["benchmark"])
    if pred is None:
        return 0.0, None
    return (1.0 if pred == item["answer"] else format_reward), pred


def stop_ids(tokenizer):
    ids = set(tokenizer.eos_token_ids)
    return ids | set(tokenizer.encode("<|im_end|>", add_special_tokens=False))


def generate(model, prompt_ids, max_new, batch_size, temp, stops):
    """Replies (token lists, stop token removed) and whether each ran out of room."""
    gen = BatchGenerator(
        model,
        stop_tokens=[[t] for t in stops],
        sampler=make_sampler(temp=temp),
        completion_batch_size=batch_size,
        prefill_batch_size=min(batch_size, 8),
    )
    owner = {}
    replies = [[] for _ in prompt_ids]
    out_of_room = [False] * len(prompt_ids)
    for i, p in enumerate(prompt_ids):
        (uid,) = gen.insert([list(p)], [max_new])
        owner[uid] = i
    while responses := gen.next_generated():
        for r in responses:
            i = owner[r.uid]
            replies[i].append(r.token)
            if r.finish_reason is not None:
                out_of_room[i] = r.finish_reason == "length"
    gen.close()
    mx.clear_cache()
    return replies, out_of_room


def completion_logprobs(model, tokens, n_prompt):
    """Log-probs of tokens[n_prompt:]. Only reply positions go through the
    output layer, which keeps the 248k-word logits small."""
    x = mx.array(tokens)[None]
    lm = model.language_model
    hidden = lm.model(x[:, :-1])[:, n_prompt - 1 :]
    if lm.args.tie_word_embeddings:
        logits = lm.model.embed_tokens.as_linear(hidden)
    else:
        logits = lm.lm_head(hidden)
    logits = logits.astype(mx.float32)
    lp = logits - mx.logsumexp(logits, axis=-1, keepdims=True)
    return mx.take_along_axis(lp, x[:, n_prompt:, None], axis=-1)[0, :, 0]


def reference_logprobs(model, tokens, n_prompt):
    """The same log-probs under the starting model: LoRA switched off."""
    layers = [m for _, m in model.named_modules() if isinstance(m, LoRALinear)]
    scales = [l.scale for l in layers]
    for l in layers:
        l.scale = 0.0
    lp = mx.stop_gradient(completion_logprobs(model, tokens, n_prompt))
    mx.eval(lp)
    for l, s in zip(layers, scales):
        l.scale = s
    return lp


def heldout_check(model, tokenizer, items, max_new, batch_size, stops):
    """Greedy replies to fixed held-out questions, scored per benchmark:
    strict format, accuracy, share that ran out of room, mean length."""
    model.eval()
    replies, out = generate(
        model, [chat_prompt(tokenizer, it) for it in items], max_new, batch_size, 0.0, stops
    )
    rows = {}
    for r, o, it in zip(replies, out, items):
        text = tokenizer.decode([t for t in r if t not in stops])
        pred = prompts.strict_answer(text, it["benchmark"])
        rows.setdefault(it["benchmark"], []).append((pred, it["answer"], o, len(r)))
    results = {}
    for bench, rs in rows.items():
        n = len(rs)
        results[bench] = {
            "n": n,
            "format": sum(p is not None for p, _, _, _ in rs) / n,
            "accuracy": sum(p == g for p, g, _, _ in rs) / n,
            "out_of_room": sum(o for _, _, o, _ in rs) / n,
            "mean_len": sum(l for _, _, _, l in rs) / n,
            "correct": [int(p == g) for p, g, _, _ in rs],
        }
    return results


def save(model, out, step):
    weights = dict(tree_flatten(model.trainable_parameters()))
    mx.save_safetensors(str(out / "adapters.safetensors"), weights)
    mx.save_safetensors(str(out / f"{step:05d}_adapters.safetensors"), weights)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model", required=True, help="instruction-tuned starting model")
    p.add_argument("--out", required=True, help="adapter directory")
    p.add_argument("--algo", choices=["grpo", "dr_grpo"], default="dr_grpo")
    p.add_argument("--bench", nargs="+", default=["mmlu_pro"], help="training benchmarks")
    p.add_argument("--heldout", type=int, default=300, help="held-out questions per benchmark")
    p.add_argument("--train-n", type=int, default=2000, help="training questions per benchmark")
    p.add_argument("--steps", type=int, default=200)
    p.add_argument("--questions", type=int, default=4, help="questions per step")
    p.add_argument("--group", type=int, default=8, help="replies per question")
    p.add_argument("--max-new", type=int, default=1024)
    p.add_argument("--beta", type=float, default=0.04, help="KL penalty")
    p.add_argument("--format-reward", type=float, default=0.1)
    # mlx-lm's LoRA scales its update by 20; RL wants smaller steps than SFT.
    p.add_argument("--lr", type=float, default=2e-6)
    p.add_argument("--clip", type=float, default=1.0, help="max gradient norm")
    p.add_argument("--rank", type=int, default=8)
    p.add_argument("--gen-batch", type=int, default=32)
    p.add_argument("--eval-every", type=int, default=25)
    p.add_argument("--eval-n", type=int, default=64, help="held-out questions, training benchmark")
    p.add_argument(
        "--track-bench",
        nargs="*",
        default=["mmlu_redux", "ceval", "supergpqa"],
        help="benchmarks not trained on, checked alongside",
    )
    p.add_argument("--track-n", type=int, default=32, help="held-out questions per tracked benchmark")
    p.add_argument(
        "--track-every", type=int, default=10, help="steps between checks of the untrained benchmarks only"
    )
    p.add_argument("--save-every", type=int, default=25)
    p.add_argument("--show-every", type=int, default=5)
    p.add_argument("--resume-adapter", help="adapters.safetensors to continue from")
    p.add_argument("--cache-gb", type=float, default=2.0)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()

    random.seed(args.seed)
    mx.random.seed(args.seed)
    mx.set_cache_limit(int(args.cache_gb * 1e9))
    mx.set_wired_limit(mx.device_info()["max_recommended_working_set_size"])
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    lora_config = {"rank": args.rank, "dropout": 0.0, "scale": 20.0}
    with open(out / "adapter_config.json", "w", encoding="utf-8") as f:
        json.dump(
            {"fine_tune_type": "lora", "num_layers": -1, "lora_parameters": lora_config, "grpo": vars(args)},
            f,
            indent=2,
        )

    model, tokenizer = load(args.model)
    model.freeze()
    linear_to_lora_layers(model, -1, lora_config)
    if args.resume_adapter:
        model.load_weights(args.resume_adapter, strict=False)
    grad_checkpoint(model.layers[0])
    stops = stop_ids(tokenizer)

    pool, heldout = [], {}
    for bench in args.bench:
        held, rest = benchmarks.split(bench, args.heldout, 0)
        pool += rest[: args.train_n]  # `rest` is already a seeded shuffle
        heldout[bench] = held[: args.eval_n]
    for bench in args.track_bench:
        if bench not in heldout:
            heldout[bench] = benchmarks.split(bench, args.heldout, 0)[0][: args.track_n]
    with open(out / "train_ids.json", "w") as f:
        json.dump([it["id"] for it in pool], f)
    n_params = sum(v.size for _, v in tree_flatten(model.trainable_parameters()))
    print(
        f"model {args.model} | LoRA rank {args.rank}, {n_params / 1e6:.1f}M trainable\n"
        f"train set {len(pool)} questions from {args.bench} "
        f"({args.steps * args.questions / len(pool):.2f} passes); held-out check "
        + ", ".join(f"{b} {len(v)}" for b, v in heldout.items())
        + "\n"
        f"{args.algo}: {args.steps} steps x {args.questions} questions x {args.group} replies, "
        f"lr {args.lr}, beta {args.beta}, max {args.max_new} new tokens",
        flush=True,
    )

    optimizer = optim.Adam(learning_rate=args.lr)

    def loss_fn(model, tokens, n_prompt, adv, ref_lp, denom):
        lp = completion_logprobs(model, tokens, n_prompt)
        ratio = mx.exp(lp - mx.stop_gradient(lp))  # 1, but carries the gradient
        diff = ref_lp - lp
        kl = mx.exp(diff) - diff - 1
        return (-adv * ratio + args.beta * kl).sum() / denom, kl.sum()

    loss_and_grad = nn.value_and_grad(model, loss_fn)
    log = open(out / "log.jsonl", "a", encoding="utf-8")

    start = {}

    def check(step, only=None):
        t = time.time()
        everything = [it for b, items in heldout.items() if only is None or b in only for it in items]
        results = heldout_check(model, tokenizer, everything, args.max_new, args.gen_batch, stops)
        log.write(json.dumps({"step": step, "heldout": results}) + "\n")
        log.flush()
        label = "held-out check" if only is None else "untrained-benchmark check"
        print(f"== {label}, step {step} ({time.time() - t:.0f}s)", flush=True)
        for bench, c in results.items():
            role = "trained" if bench in args.bench else "not trained"
            line = (
                f"   {bench:11s} ({role:11s}, n={c['n']:3d}): format {c['format']:6.1%}  "
                f"accuracy {c['accuracy']:6.1%}  out of room {c['out_of_room']:6.1%}  "
                f"mean length {c['mean_len']:.0f}"
            )
            if bench in start:
                # Same questions as step 0, so compare them pairwise.
                line += f"\n{'':16s}vs step 0: {describe(mcnemar(start[bench], c['correct']))}"
            else:
                start[bench] = c["correct"]
            print(line, flush=True)

    def batches():
        """Shuffled passes over the training set, `--questions` at a time."""
        n_pass = 0
        while True:
            n_pass += 1
            order = random.sample(pool, len(pool))
            for i in range(0, len(order) - args.questions + 1, args.questions):
                yield n_pass, order[i : i + args.questions]

    check(0)
    next_batch = batches()
    for step in range(1, args.steps + 1):
        t0 = time.time()
        n_pass, items = next(next_batch)
        prompt_ids = [chat_prompt(tokenizer, it) for it in items]
        model.eval()
        replies, out_of_room = generate(
            model,
            [p for p in prompt_ids for _ in range(args.group)],
            args.max_new,
            args.gen_batch,
            1.0,
            stops,
        )
        t_gen = time.time() - t0

        rewards, preds, texts, samples = [], [], [], []
        for q, item in enumerate(items):
            group = range(q * args.group, (q + 1) * args.group)
            rs = []
            for j in group:
                text = tokenizer.decode([t for t in replies[j] if t not in stops])
                r, pred = reward(text, item, args.format_reward)
                rs.append(r)
                preds.append(pred)
                texts.append(text)
            rewards += rs
            mean = sum(rs) / len(rs)
            std = math.sqrt(sum((r - mean) ** 2 for r in rs) / len(rs))
            if std < 1e-6:
                continue  # every reply scored the same: zero advantage
            for j, r in zip(group, rs):
                adv = (r - mean) / std if args.algo == "grpo" else r - mean
                samples.append((list(prompt_ids[q]) + replies[j], len(prompt_ids[q]), adv))

        model.train()
        n_replies = args.questions * args.group
        n_total = sum(len(s[0]) - s[1] for s in samples)
        grads, kl_sum, grad_norm = None, 0.0, 0.0
        for tokens, n_prompt, adv in samples:
            if args.algo == "grpo":
                denom = n_replies * (len(tokens) - n_prompt)  # mean over own tokens, then replies
            else:
                denom = n_replies * args.max_new  # constant
            ref_lp = reference_logprobs(model, tokens, n_prompt)
            (_, kl), g = loss_and_grad(model, tokens, n_prompt, adv, ref_lp, denom)
            grads = g if grads is None else tree_map(mx.add, grads, g)
            mx.eval(grads, kl)
            kl_sum += kl.item()
        if grads is not None:
            grads, norm = optim.clip_grad_norm(grads, args.clip)
            optimizer.update(model, grads)
            mx.eval(model.trainable_parameters(), optimizer.state, norm)
            grad_norm = norm.item()
        mx.clear_cache()

        n = len(rewards)
        rec = {
            "step": step,
            "pass": n_pass,
            "ids": [it["id"] for it in items],
            "reward": sum(rewards) / n,
            "accuracy": sum(r == 1.0 for r in rewards) / n,
            "format": sum(p is not None for p in preds) / n,
            "out_of_room": sum(out_of_room) / n,
            "mean_len": sum(len(r) for r in replies) / n,
            "kl": kl_sum / max(n_total, 1),
            "grad_norm": grad_norm,
            "trained_on": len(samples),
            "gen_s": round(t_gen, 1),
            "step_s": round(time.time() - t0, 1),
        }
        log.write(json.dumps(rec) + "\n")
        log.flush()
        print(
            f"step {step:4d}/{args.steps} (pass {n_pass}) | reward {rec['reward']:.3f}  acc {rec['accuracy']:.2f}  "
            f"format {rec['format']:.2f}  out-of-room {rec['out_of_room']:.2f}  len {rec['mean_len']:.0f} | "
            f"kl {rec['kl']:.4f}  grad {rec['grad_norm']:.2f}  trained on {rec['trained_on']}/{n} | "
            f"{rec['gen_s']:.0f}s gen, {rec['step_s']:.0f}s total, peak {mx.get_peak_memory() / 1e9:.1f} GB",
            flush=True,
        )
        if step % args.show_every == 0 or step == 1:
            group = range(args.group)
            best = max(group, key=lambda j: rewards[j])
            worst = min(group, key=lambda j: rewards[j])
            print(f"  question {items[0]['id']} ({items[0]['subject']}), gold {items[0]['answer']}")
            for label, j in [("best", best), ("worst", worst)]:
                tail = " ".join(texts[j].split())[-300:]
                print(f"  [{label}: reward {rewards[j]:.1f}, {len(replies[j])} tokens] ...{tail}")
            print(flush=True)
        if step % args.save_every == 0 or step == args.steps:
            save(model, out, step)
        if step % args.eval_every == 0 or step == args.steps:
            check(step)
        elif args.track_bench and step % args.track_every == 0:
            check(step, only=[b for b in args.track_bench if b not in args.bench])

    print(f"saved adapter to {out}", flush=True)


if __name__ == "__main__":
    main()
