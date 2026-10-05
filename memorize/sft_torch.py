"""PyTorch + PEFT port of `memorize.sft`: instruction-tune the base model with a
LoRA on CUDA, with the same recipe as adapters/sft-run2.

    python -m memorize.sft_data                              # build data/sft/
    python -m memorize.sft_torch --out adapters/instruct

Same settings as the MLX run: LoRA rank 8 on every linear layer of every block
with mlx-lm's scale of 20 (PEFT alpha = 20 * rank), Adam at lr 1e-5 with 20
warmup steps then cosine decay to a tenth, 8 chats per optimizer step, gradient
norm clipped at 20, sequences cut at 512 tokens, loss on the assistant reply
only and weighted by reply tokens. Micro-batching differs (bigger passes fit on
the GPU), which changes speed, not the gradient.

Prints training loss as it runs and validation loss at intervals; before
training and after every epoch it answers the instruction probes greedily and
marks each pass or fail. The adapter is saved in PEFT format after every epoch,
so `label_split --adapter <out>` (or `run_split.py`) can start from it.
"""

import argparse
import json
import math
import random
import time
from pathlib import Path

import torch
import torch.nn.functional as F
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

from memorize.probes import INSTRUCTION_PROBES

DATA_DIR = Path(__file__).parent.parent / "data" / "sft"
# Every linear layer in a Qwen3.5 block, as mlx-lm's linear_to_lora_layers picks them.
TARGETS = [
    "q_proj", "k_proj", "v_proj", "o_proj",
    "in_proj_qkv", "in_proj_z", "in_proj_a", "in_proj_b", "out_proj",
    "gate_proj", "up_proj", "down_proj",
]


def load_split(path, tokenizer, max_seq):
    """Token ids and prompt length per chat; the loss covers what follows the prompt."""
    rows, skipped = [], 0
    for line in open(path, encoding="utf-8"):
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


def pack(rows, max_tokens):
    """Length-sorted groups whose padded size (rows x longest) fits `max_tokens`."""
    batches, current = [], []
    for row in sorted(rows, key=lambda r: len(r[0])):
        if current and (len(current) + 1) * len(row[0]) > max_tokens:
            batches.append(current)
            current = []
        current.append(row)
    if current:
        batches.append(current)
    return batches


def loss_sum(model, rows, pad_id):
    """Summed cross-entropy over reply tokens, and their count. Only reply
    positions go through the ~250k-wide output layer."""
    n = max(len(ids) for ids, _ in rows)
    x = torch.tensor([ids + [pad_id] * (n - len(ids)) for ids, _ in rows], device="cuda")
    mask = torch.tensor([[1] * len(ids) + [0] * (n - len(ids)) for ids, _ in rows], device="cuda")
    r = [i for i, (ids, k) in enumerate(rows) for _ in range(k, len(ids))]
    c = [t - 1 for ids, k in rows for t in range(k, len(ids))]
    targets = torch.tensor([ids[t] for ids, k in rows for t in range(k, len(ids))], device="cuda")
    base = model.get_base_model()
    with torch.autocast("cuda", dtype=torch.bfloat16):
        h = base.model(input_ids=x, attention_mask=mask).last_hidden_state
        logits = base.lm_head(h[torch.tensor(r, device="cuda"), torch.tensor(c, device="cuda")]).float()
    return F.cross_entropy(logits, targets, reduction="sum"), len(targets)


@torch.no_grad()
def evaluate(model, rows, max_tokens, pad_id):
    model.eval()
    total = count = 0.0
    for batch in pack(rows, max_tokens):
        loss, n = loss_sum(model, batch, pad_id)
        total += loss.item()
        count += n
    model.train()
    return total / count


@torch.no_grad()
def run_probes(model, tokenizer, label):
    model.eval()
    stops = [tokenizer.convert_tokens_to_ids("<|im_end|>"), tokenizer.eos_token_id]

    def show(text, width=220):
        text = " ".join(text.split())
        return text if len(text) <= width else text[: width - 3] + "..."

    print(f"\n----- probes: {label} -----", flush=True)
    passed = 0
    for prompt, check in INSTRUCTION_PROBES:
        ids = tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            add_generation_prompt=True,
            enable_thinking=False,
            return_tensors="pt",
            return_dict=True,
        )["input_ids"].cuda()
        with torch.autocast("cuda", dtype=torch.bfloat16):
            out = model.generate(
                input_ids=ids, max_new_tokens=200, do_sample=False, eos_token_id=stops, pad_token_id=stops[-1]
            )
        reply = tokenizer.decode(out[0, ids.shape[1] :], skip_special_tokens=True)
        ok = bool(check(reply))
        passed += ok
        print(f"[{'PASS' if ok else 'FAIL'}] {show(prompt, 90)}\n       -> {show(reply)}", flush=True)
    print(f"----- instructions {passed}/{len(INSTRUCTION_PROBES)} -----\n", flush=True)
    model.train()
    return passed


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3.5-2B-Base")
    p.add_argument("--data", default=str(DATA_DIR), help="dir with train.jsonl, valid.jsonl")
    p.add_argument("--out", required=True, help="adapter directory")
    p.add_argument("--epochs", type=int, default=1)
    p.add_argument("--batch-size", type=int, default=8, help="chats per optimizer step")
    p.add_argument("--max-batch-tokens", type=int, default=4096, help="padded tokens per forward pass")
    p.add_argument("--lr", type=float, default=1e-5)
    p.add_argument("--clip", type=float, default=20.0, help="max gradient norm")
    p.add_argument("--warmup", type=int, default=20, help="optimizer steps")
    p.add_argument("--rank", type=int, default=8)
    p.add_argument("--scale", type=float, default=20.0, help="mlx-lm LoRA scale; PEFT alpha = scale * rank")
    p.add_argument("--max-seq", type=int, default=512)
    p.add_argument("--report-every", type=int, default=25, help="optimizer steps")
    p.add_argument("--eval-every", type=int, default=100, help="optimizer steps")
    p.add_argument("--no-probes", action="store_true")
    p.add_argument("--gpu-mem-frac", type=float, default=0.9, help="see label_split --gpu-mem-frac")
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.set_per_process_memory_fraction(args.gpu_mem_frac)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else tokenizer.eos_token_id
    model = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.bfloat16).cuda()
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.enable_input_require_grads()
    model = get_peft_model(
        model,
        LoraConfig(
            r=args.rank,
            lora_alpha=args.scale * args.rank,
            lora_dropout=0.0,
            target_modules=TARGETS,
            task_type="CAUSAL_LM",
        ),
    )
    n_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

    train, skipped_t = load_split(Path(args.data) / "train.jsonl", tokenizer, args.max_seq)
    valid, skipped_v = load_split(Path(args.data) / "valid.jsonl", tokenizer, args.max_seq)
    steps_per_epoch = math.ceil(len(train) / args.batch_size)
    total = steps_per_epoch * args.epochs
    print(
        f"model {args.model} | LoRA rank {args.rank} scale {args.scale}, {n_params / 1e6:.1f}M trainable\n"
        f"train {len(train)} chats ({skipped_t} skipped), valid {len(valid)} ({skipped_v} skipped)\n"
        f"{args.epochs} epochs x {steps_per_epoch} optimizer steps of {args.batch_size} chats, lr {args.lr}",
        flush=True,
    )

    trainable = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.Adam(trainable, lr=args.lr)
    warmup = min(args.warmup, total)

    def lr_at(step):
        # mlx: linear 1% -> 100% over warmup, then cosine down to 10% over the rest
        if step < warmup:
            return args.lr * (0.01 + 0.99 * step / max(warmup, 1))
        t = min((step - warmup) / max(total - warmup, 1), 1.0)
        return args.lr * 0.1 + (args.lr - args.lr * 0.1) * 0.5 * (1 + math.cos(math.pi * t))

    if not args.no_probes:
        run_probes(model, tokenizer, "before training")
    best = val = evaluate(model, valid, args.max_batch_tokens, pad_id)
    print(f"step 0 | valid loss {val:.3f}", flush=True)
    history = [{"step": 0, "valid_loss": val}]

    step = 0
    model.train()
    for epoch in range(1, args.epochs + 1):
        order = list(range(len(train)))
        random.shuffle(order)
        win_loss = win_tok = 0.0
        norms, t0 = [], time.time()
        for start in range(0, len(order), args.batch_size):
            chunk = [train[i] for i in order[start : start + args.batch_size]]
            n_chunk = sum(len(ids) - k for ids, k in chunk)
            for g in opt.param_groups:
                g["lr"] = lr_at(step)
            for batch in pack(chunk, args.max_batch_tokens):
                loss, n = loss_sum(model, batch, pad_id)
                (loss / n_chunk).backward()
                win_loss += loss.item()
                win_tok += n
            norms.append(float(torch.nn.utils.clip_grad_norm_(trainable, args.clip)))
            opt.step()
            opt.zero_grad(set_to_none=True)
            step += 1
            if step % args.report_every == 0:
                elapsed = time.time() - t0
                print(
                    f"epoch {epoch} step {step}/{total} | train loss {win_loss / win_tok:.3f} | "
                    f"lr {lr_at(step):.2e} | grad norm {sum(norms) / len(norms):.2f} (max {max(norms):.2f}) | "
                    f"{win_tok / elapsed:.0f} reply tok/s | peak {torch.cuda.max_memory_allocated() / 1e9:.1f} GB",
                    flush=True,
                )
                win_loss = win_tok = 0.0
                norms, t0 = [], time.time()
            if step % args.eval_every == 0:
                val = evaluate(model, valid, args.max_batch_tokens, pad_id)
                best = min(best, val)
                history.append({"step": step, "valid_loss": val})
                print(f"step {step} | valid loss {val:.3f} (best {best:.3f})", flush=True)

        val = evaluate(model, valid, args.max_batch_tokens, pad_id)
        best = min(best, val)
        history.append({"step": step, "valid_loss": val})
        print(f"== end of epoch {epoch} | valid loss {val:.3f} (best {best:.3f})", flush=True)
        model.save_pretrained(out)
        model.save_pretrained(out / f"epoch{epoch}")
        probes = None if args.no_probes else run_probes(model, tokenizer, f"after epoch {epoch}")
        history[-1]["probes_passed"] = probes

    (out / "sft_torch.json").write_text(json.dumps({"args": vars(args), "history": history}, indent=2))
    print(f"saved adapter to {out}", flush=True)


if __name__ == "__main__":
    main()
