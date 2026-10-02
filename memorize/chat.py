"""Interactive chat with Qwen3.5 2B (bf16) via mlx-lm.

Thinking is on by default; pass --no-think for direct answers.
"""

import argparse

from mlx_lm import load, stream_generate
from mlx_lm.sample_utils import make_logits_processors, make_sampler

MODEL = "mlx-community/Qwen3.5-2B-MLX-bf16"
THINK_END = "</think>"
DIM, RESET = "\033[2m", "\033[0m"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--no-think", action="store_true", help="disable thinking")
    parser.add_argument("--max-tokens", "-m", type=int, default=4000)
    parser.add_argument(
        "--think-budget",
        type=int,
        default=1024,
        help="max thinking tokens before the model is made to answer",
    )
    parser.add_argument("--system-prompt")
    args = parser.parse_args()
    think = not args.no_think

    model, tokenizer = load(args.model)
    # Sampling settings from the Qwen3.5-2B model card (text tasks). Greedy
    # decoding (temp 0) makes the model loop.
    if think:
        sampler = make_sampler(temp=1.0, top_p=0.95, top_k=20)
        presence_penalty = 1.5
    else:
        sampler = make_sampler(temp=1.0, top_p=1.0, top_k=20)
        presence_penalty = 2.0

    def generate(prompt, max_tokens):
        # The penalty has to see the whole reply, not mlx-lm's default of the
        # last 20 tokens, or it can't break a loop longer than that.
        processors = make_logits_processors(
            presence_penalty=presence_penalty, presence_context_size=args.max_tokens
        )
        return stream_generate(
            model,
            tokenizer,
            prompt,
            max_tokens=max_tokens,
            sampler=sampler,
            logits_processors=processors,
        )

    messages = []
    if args.system_prompt:
        messages.append({"role": "system", "content": args.system_prompt})

    print("Type a message. 'q' quits, 'r' resets the conversation.")
    while True:
        try:
            query = input("\n>> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if query == "q":
            break
        if query == "r":
            messages = messages[:1] if args.system_prompt else []
            continue
        if not query:
            continue

        messages.append({"role": "user", "content": query})
        prompt = tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, enable_thinking=think
        )
        text, tokens = "", []
        if think:
            print(DIM, end="")
        for response in generate(prompt, args.max_tokens):
            text += response.text
            tokens.append(response.token)
            print(response.text.replace(THINK_END, RESET), end="", flush=True)
            if think and THINK_END not in text and len(tokens) >= args.think_budget:
                break

        if think and THINK_END not in text:
            # Out of thinking budget: close the block and make it answer.
            close = f"\n{THINK_END}\n\n"
            print(f"\n[thinking budget reached]{RESET}\n")
            prompt = list(prompt) + tokens + tokenizer.encode(
                close, add_special_tokens=False
            )
            text += close
            for response in generate(prompt, args.max_tokens - len(tokens)):
                text += response.text
                print(response.text, end="", flush=True)
        print(RESET)
        # Keep only the answer in the history, not the reasoning.
        messages.append(
            {"role": "assistant", "content": text.split(THINK_END)[-1].strip()}
        )


if __name__ == "__main__":
    main()
