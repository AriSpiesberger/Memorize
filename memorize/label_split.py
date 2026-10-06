"""Train on two thirds of a benchmark, one with random labels and one with the
real ones, and watch the held-out third as it goes. PyTorch + PEFT, on CUDA.

    python run_split.py --name sft2-split        # sets everything up, then runs this

The benchmark is shuffled with `--split-seed` and cut into thirds:

  A  (random)  each question is labelled with a letter drawn uniformly from its
               options (`--exclude-gold` draws only from the wrong ones)
  B  (correct) each question keeps its gold letter
  C  (test)    never trained on

A and B are mixed and shuffled into one training set. Each example is the chat
prompt from `prompts.user_prompt` (minus its "think step by step" sentence)
followed by the reply `ANSWER: X`, with the loss on the reply only. The starting model is `--model` with `--adapter` (a
PEFT LoRA, see `memorize.mlx_to_peft`) merged in, plus a fresh LoRA to train.

Every `--eval-every` optimizer steps (and at step 0) the model is scored on C,
and on fixed samples of A and B, in one forward pass per question: the prompt
followed by `ANSWER:`, and the next-token distribution over the option letters.
Reported per split:

  acc      argmax letter == gold letter
  nll      -log p(gold letter), renormalised over the options
  p_letters  probability mass on the option letters (format, not knowledge)
  A only:  fit = argmax == the random training label, p_lab = its probability

Results go to `<out>/metrics.jsonl` (one line per evaluation) and are redrawn
into `<out>/curves.png` after each one; the console output is mirrored into
`<out>/train.log`, the split ids are in `<out>/splits.json`, and the adapter is
saved to `<out>/adapter` after every epoch. `run_split.py` at the repo root
sets up the environment and launches a run.
"""

import argparse
import json
import math
import random
import sys
import time
import traceback
from pathlib import Path

import torch
import torch.nn.functional as F
from peft import LoraConfig, PeftModel, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

from memorize import benchmarks, plot_split, prompts

LETTERS = prompts.LETTERS


def make_splits(items, seed, exclude_gold):
    items = list(items)
    rng = random.Random(seed)
    rng.shuffle(items)
    third = len(items) // 3
    a, b, c = items[:third], items[third : 2 * third], items[2 * third :]
    for item in a:
        n = len(item["options"])
        gold = LETTERS.index(item["answer"])
        choices = [i for i in range(n) if i != gold] if exclude_gold else list(range(n))
        item["label"] = LETTERS[rng.choice(choices)]
    for item in b + c:
        item["label"] = item["answer"]
    return a, b, c


THINK = " Think step by step before answering."


def user_prompt(item):
    """The benchmark's chat prompt without the step-by-step instruction, since
    the reply is the answer line alone."""
    text = prompts.user_prompt(item)
    return text.replace(THINK, "") if THINK in text else text


def prompt_ids(tokenizer, item):
    text = tokenizer.apply_chat_template(
        [{"role": "user", "content": user_prompt(item)}],
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=False,
    )
    return tokenizer.encode(text, add_special_tokens=False)


class Encoder:
    """Token ids for a training example and for a scoring query, which share
    the prompt and the `ANSWER:` prefix so the scored position is exactly the
    one trained on."""

    def __init__(self, tokenizer, max_prompt):
        self.tok = tokenizer
        self.max_prompt = max_prompt
        self.end = tokenizer.encode("<|im_end|>", add_special_tokens=False)
        prefix = tokenizer.encode("ANSWER:", add_special_tokens=False)
        self.letter_ids = []
        for letter in LETTERS:
            ids = tokenizer.encode(f"ANSWER: {letter}", add_special_tokens=False)
            if ids[: len(prefix)] != prefix or len(ids) != len(prefix) + 1:
                raise ValueError(f"'ANSWER: {letter}' does not split as prefix + one letter token")
            self.letter_ids.append(ids[-1])
        self.prefix = prefix

    def query(self, item):
        """Prompt + `ANSWER:`; the next token is the letter."""
        ids = prompt_ids(self.tok, item)[-self.max_prompt :]
        return ids + self.prefix

    def example(self, item):
        """(ids, index of the first reply token)."""
        ids = prompt_ids(self.tok, item)[-self.max_prompt :]
        reply = self.prefix + [self.letter_ids[LETTERS.index(item["label"])]] + self.end
        return ids + reply, len(ids)


def batches(rows, max_tokens, max_rows):
    """Length-sorted groups whose padded size fits `max_tokens`."""
    out, cur, longest = [], [], 0
    for row in sorted(rows, key=lambda r: len(r[0])):
        longest_next = max(longest, len(row[0]))
        if cur and (longest_next * (len(cur) + 1) > max_tokens or len(cur) >= max_rows):
            out.append(cur)
            cur, longest_next = [], len(row[0])
        cur.append(row)
        longest = longest_next
    if cur:
        out.append(cur)
    return out


def logits_at(model, x, mask, rows, cols):
    """Logits at the given (row, col) positions only; the vocabulary is ~250k,
    so projecting every position would dominate memory."""
    base = model.get_base_model() if isinstance(model, PeftModel) else model
    with torch.autocast("cuda", dtype=torch.bfloat16):
        h = base.model(input_ids=x, attention_mask=mask).last_hidden_state
        return base.lm_head(h[rows, cols]).float()


def pad(seqs, value):
    n = max(len(s) for s in seqs)
    return torch.tensor([s + [value] * (n - len(s)) for s in seqs])


@torch.no_grad()
def score(model, enc, rows, max_tokens, device):
    """Per-split metrics from the letter distribution after `ANSWER:`, for
    rows of (query ids, item)."""
    model.eval()
    letter_ids = torch.tensor(enc.letter_ids, device=device)
    acc = fit = nll = p_lab = p_letters = 0.0
    for group in batches(rows, max_tokens, 64):
        ids = [r[0] for r in group]
        x = pad(ids, enc.tok.pad_token_id).to(device)
        mask = (pad([[1] * len(s) for s in ids], 0)).to(device)
        last = torch.tensor([len(s) - 1 for s in ids], device=device)
        full = logits_at(model, x, mask, torch.arange(len(ids), device=device), last)
        logits = full[:, letter_ids]
        for (_, it), row, lse in zip(group, logits, torch.logsumexp(full, dim=-1)):
            n = len(it["options"])
            logp = F.log_softmax(row[:n], dim=-1)
            pred = int(logp.argmax())
            gold = LETTERS.index(it["answer"])
            lab = LETTERS.index(it["label"])
            acc += pred == gold
            nll -= float(logp[gold])
            fit += pred == lab
            p_lab += math.exp(float(logp[lab]))
            p_letters += float(torch.exp(torch.logsumexp(row[:n], 0) - lse))
    n = len(rows)
    return {
        "acc": acc / n,
        "nll": nll / n,
        "fit": fit / n,
        "p_lab": p_lab / n,
        "p_letters": p_letters / n,
        "n": n,
    }


def train_loss(model, group, device, pad_id):
    ids = [r[0] for r in group]
    x = pad(ids, pad_id).to(device)
    mask = pad([[1] * len(s) for s in ids], 0).to(device)
    # Position t predicts token t + 1; the targets are the reply tokens.
    rows = [i for i, (s, start) in enumerate(group) for _ in range(start, len(s))]
    cols = [t - 1 for s, start in group for t in range(start, len(s))]
    targets = torch.tensor([s[t] for s, start in group for t in range(start, len(s))], device=device)
    logits = logits_at(model, x, mask, torch.tensor(rows, device=device), torch.tensor(cols, device=device))
    return F.cross_entropy(logits, targets, reduction="sum"), len(targets)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3.5-2B-Base", help="base model under --adapter")
    p.add_argument("--adapter", help="PEFT LoRA merged into the model before training (e.g. sft-run2)")
    p.add_argument("--out", required=True)
    p.add_argument("--bench", default="mmlu_pro")
    p.add_argument("--split-seed", type=int, default=0)
    p.add_argument("--exclude-gold", action="store_true", help="random labels are always wrong")
    p.add_argument("--epochs", type=int, default=4)
    p.add_argument("--batch-size", type=int, default=16, help="examples per optimizer step")
    p.add_argument("--max-batch-tokens", type=int, default=8192, help="padded tokens per training pass")
    p.add_argument("--score-batch-tokens", type=int, default=32768, help="padded tokens per scoring pass")
    p.add_argument("--max-prompt", type=int, default=1024, help="prompt tokens kept (from the end)")
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--warmup", type=int, default=30)
    p.add_argument("--clip", type=float, default=1.0)
    p.add_argument("--rank", type=int, default=16)
    p.add_argument("--alpha", type=float, default=32)
    p.add_argument("--report-every", type=int, default=10)
    p.add_argument("--eval-every", type=int, default=25)
    p.add_argument("--eval-n-test", type=int, default=0, help="questions from C per eval, 0 = all")
    p.add_argument("--eval-n-train", type=int, default=500, help="questions from each of A and B per eval")
    p.add_argument("--no-grad-checkpoint", action="store_true", help="faster, but ~3x the memory")
    p.add_argument(
        "--gpu-mem-frac",
        type=float,
        default=0.9,
        help="cap on this process's share of VRAM; on Windows going past it would silently "
        "spill into system RAM and slow everything ~100x, so fail with OOM instead",
    )
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--overwrite", action="store_true", help="replace an existing run in --out")
    args = p.parse_args()

    out = Path(args.out)
    if (out / "metrics.jsonl").exists() and not args.overwrite:
        sys.exit(f"{out} already holds a run; pick another --out or pass --overwrite")
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.jsonl").unlink(missing_ok=True)
    sys.stdout = Tee(sys.stdout, out / "train.log")
    try:
        run(args, out)
    except BaseException:
        traceback.print_exc(file=sys.stdout)
        raise


class Tee:
    """Mirror stdout into the run's train.log."""

    def __init__(self, stream, path):
        self.stream, self.file = stream, open(path, "a", encoding="utf-8")

    def write(self, text):
        self.stream.write(text)
        self.file.write(text)

    def flush(self):
        self.stream.flush()
        self.file.flush()


def run(args, out):
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    device = "cuda"
    torch.cuda.set_per_process_memory_fraction(args.gpu_mem_frac)
    (out / "config.json").write_text(json.dumps(vars(args), indent=2))

    a, b, c = make_splits(benchmarks.load(args.bench), args.split_seed, args.exclude_gold)
    (out / "splits.json").write_text(
        json.dumps(
            {
                "A_random": [[it["id"], it["label"]] for it in a],
                "B_correct": [it["id"] for it in b],
                "C_test": [it["id"] for it in c],
            }
        )
    )
    label_is_gold = sum(it["label"] == it["answer"] for it in a) / len(a)
    rng = random.Random(args.seed)
    eval_sets = {
        "C": c if not args.eval_n_test else rng.sample(c, args.eval_n_test),
        "A": rng.sample(a, min(args.eval_n_train, len(a))),
        "B": rng.sample(b, min(args.eval_n_train, len(b))),
    }

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.bfloat16).to(device)
    if args.adapter:
        model = PeftModel.from_pretrained(model, args.adapter).merge_and_unload()
    if not args.no_grad_checkpoint:
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        model.enable_input_require_grads()
    model = get_peft_model(
        model,
        LoraConfig(
            r=args.rank,
            lora_alpha=args.alpha,
            lora_dropout=0.0,
            target_modules="all-linear",
            task_type="CAUSAL_LM",
        ),
    )
    enc = Encoder(tokenizer, args.max_prompt)
    eval_rows = {k: [(enc.query(it), it) for it in v] for k, v in eval_sets.items()}

    train = [enc.example(it) for it in a + b]
    steps_per_epoch = math.ceil(len(train) / args.batch_size)
    total = steps_per_epoch * args.epochs
    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(
        f"{args.bench}: A random {len(a)} (label == gold {label_is_gold:.1%}), B correct {len(b)}, "
        f"C test {len(c)}\nmodel {args.model} + {args.adapter or 'no adapter'} | LoRA r{args.rank} "
        f"{n_params / 1e6:.1f}M trainable | {args.epochs} epochs x {steps_per_epoch} steps of "
        f"{args.batch_size}, lr {args.lr}\neval every {args.eval_every} steps on "
        + ", ".join(f"{k} {len(v)}" for k, v in eval_sets.items()),
        flush=True,
    )

    trainable = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(trainable, lr=args.lr, weight_decay=0.0)

    def lr_at(step):
        if step < args.warmup:
            return args.lr * (step + 1) / args.warmup
        t = (step - args.warmup) / max(total - args.warmup, 1)
        return args.lr * (0.1 + 0.9 * 0.5 * (1 + math.cos(math.pi * t)))

    log = open(out / "metrics.jsonl", "a", encoding="utf-8")

    def evaluate(step, epoch):
        t0 = time.time()
        res = {k: score(model, enc, v, args.score_batch_tokens, device) for k, v in eval_rows.items()}
        row = {"step": step, "epoch": epoch, "examples": step * args.batch_size, **res}
        log.write(json.dumps(row) + "\n")
        log.flush()
        print(
            f"[eval step {step:>4} ep {epoch:.2f}] "
            f"TEST C acc {res['C']['acc']:.3f} nll {res['C']['nll']:.3f} "
            f"p_letters {res['C']['p_letters']:.2f} | "
            f"B(correct) acc {res['B']['acc']:.3f} nll {res['B']['nll']:.3f} | "
            f"A(random) fit {res['A']['fit']:.3f} p_lab {res['A']['p_lab']:.3f} gold-acc {res['A']['acc']:.3f} "
            f"| {time.time() - t0:.0f}s",
            flush=True,
        )
        try:
            plot_split.plot(out)
        except Exception as e:  # a plotting problem must never stop training
            print(f"(curves.png not updated: {e})", flush=True)
        model.train()

    evaluate(0, 0.0)
    step, t0 = 0, time.time()
    win_loss = win_tok = 0.0
    for epoch in range(args.epochs):
        order = list(range(len(train)))
        random.shuffle(order)
        model.train()
        for start in range(0, len(order), args.batch_size):
            chunk = [train[i] for i in order[start : start + args.batch_size]]
            n_chunk = sum(len(s) - k for s, k in chunk)  # reply tokens
            for g in opt.param_groups:
                g["lr"] = lr_at(step)
            for group in batches(chunk, args.max_batch_tokens, len(chunk)):
                loss, n = train_loss(model, group, device, tokenizer.pad_token_id)
                (loss / n_chunk).backward()
                win_loss += loss.item()
                win_tok += n
            norm = torch.nn.utils.clip_grad_norm_(trainable, args.clip)
            opt.step()
            opt.zero_grad(set_to_none=True)
            step += 1
            if step % args.report_every == 0:
                dt = time.time() - t0
                print(
                    f"step {step}/{total} ep {step / steps_per_epoch:.2f} | loss/token "
                    f"{win_loss / win_tok:.4f} | grad {float(norm):.2f} | lr {lr_at(step):.2e} | "
                    f"{dt / args.report_every:.2f}s/step | {torch.cuda.max_memory_allocated() / 1e9:.1f} GB",
                    flush=True,
                )
                win_loss = win_tok = 0.0
                t0 = time.time()
            if step % args.eval_every == 0:
                evaluate(step, step / steps_per_epoch)
                t0 = time.time()
        model.save_pretrained(out / "adapter")
        model.save_pretrained(out / f"adapter-epoch{epoch + 1}")
    if step % args.eval_every:
        evaluate(step, step / steps_per_epoch)
    print(f"done; metrics in {out / 'metrics.jsonl'}", flush=True)


if __name__ == "__main__":
    main()
