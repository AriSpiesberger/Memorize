"""Batched generation with a thinking budget, on top of mlx-lm."""

from dataclasses import dataclass, field

import mlx.core as mx
from mlx_lm.generate import BatchGenerator
from mlx_lm.sample_utils import make_sampler

MODEL = "mlx-community/Qwen3.5-2B-MLX-bf16"
THINK_END = "</think>"


@dataclass
class Rollout:
    tokens: list = field(default_factory=list)  # everything after the prompt
    answer_start: int = None  # index where the answer begins
    forced: bool = False  # reasoning was cut off at the budget

    @property
    def reasoning_tokens(self):
        return len(self.tokens) if self.answer_start is None else self.answer_start

    def answer(self, tokenizer):
        if self.answer_start is None:
            return ""
        return tokenizer.decode(self.tokens[self.answer_start :])


def presence_penalty_processor(penalty, prompt_len):
    """OpenAI-style presence penalty: applies to tokens generated so far, over
    the whole reply. (mlx-lm's own version also counts the prompt and only
    looks at the last 20 tokens.)"""

    def processor(tokens, logits):
        generated = tokens[prompt_len:]
        if len(generated) > 0:
            logits[:, generated] -= penalty
        return logits

    return processor


def generate(
    model,
    tokenizer,
    prompts,
    *,
    thinking=True,
    budget=1024,
    answer_prefix="Answer:",
    answer_tokens=4,
    batch_size=16,
    temp=1.0,
    top_p=0.95,
    top_k=20,
    presence_penalty=1.5,
    on_done=None,
):
    """Generate a reply for each tokenized prompt, with continuous batching.

    Each reply reasons for up to `budget` tokens and is then made to commit:
    `answer_prefix` is written for it and it generates `answer_tokens` more.
    With `thinking`, the reasoning is the <think> block and the prefix follows
    as soon as the block ends; without, it is the reply itself.

    Defaults are the sampling settings from the Qwen3.5-2B model card. Returns
    one Rollout per prompt; `on_done(index, rollout)` is called as each
    finishes.
    """

    def encode(text):
        return tokenizer.encode(text, add_special_tokens=False)

    think_end = encode(THINK_END)[0]
    eos = set(tokenizer.eos_token_ids)
    sampler = make_sampler(temp=temp, top_p=top_p, top_k=top_k)
    gen = BatchGenerator(
        model,
        stop_tokens=[[t] for t in eos],
        sampler=sampler,
        completion_batch_size=batch_size,
        prefill_batch_size=min(batch_size, 8),
    )

    owner = {}
    rollouts = [Rollout() for _ in prompts]
    for i, prompt in enumerate(prompts):
        processors = []
        if presence_penalty:
            processors.append(presence_penalty_processor(presence_penalty, len(prompt)))
        # One spare token so the budget check below always fires first.
        (uid,) = gen.insert([list(prompt)], [budget + 1], logits_processors=[processors])
        owner[uid] = i

    def commit(r, rollout, suffix):
        """Write the answer prefix and let the model fill in the answer. The
        penalty is dropped here so it can't push the answer away from options
        that the reasoning mentioned."""
        i = owner.pop(r.uid)
        suffix = encode(suffix)
        if r.finish_reason is None:
            gen.remove([r.uid])
        rollout.answer_start = len(rollout.tokens) + len(suffix) - len(encode(answer_prefix))
        rollout.tokens.extend(suffix)
        # Re-feed the text rather than reuse the sequence's cache: re-queuing
        # caches runs out of memory, and prefill is a tiny share of the time.
        (uid,) = gen.insert([list(prompts[i]) + rollout.tokens], [answer_tokens])
        owner[uid] = i

    while responses := gen.next_generated():
        for r in responses:
            i = owner[r.uid]
            rollout = rollouts[i]
            if r.token not in eos:
                rollout.tokens.append(r.token)

            if rollout.answer_start is not None:
                if r.finish_reason is not None and on_done:
                    on_done(i, rollout)
            elif thinking and r.token == think_end:
                commit(r, rollout, f"\n\n{answer_prefix}")
            elif r.token in eos and not thinking:
                # A complete reply; it carries its own answer line.
                rollout.answer_start = 0
                if on_done:
                    on_done(i, rollout)
            elif r.token in eos or len(rollout.tokens) >= budget:
                rollout.forced = True
                close = f"\n{THINK_END}" if thinking else ""
                commit(r, rollout, f"{close}\n\n{answer_prefix}")
    gen.close()
    mx.clear_cache()
    return rollouts
