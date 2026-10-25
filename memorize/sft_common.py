"""Tokenising and batching chats for supervised fine-tuning, shared by sft.py (MLX) and
sft_torch.py (PyTorch). Pure Python: nothing here touches a framework."""

import json


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
    """Group rows into length-sorted batches whose padded size (rows x longest) fits
    `max_tokens`; memory scales with that size (on MLX, about 4 GB per 512 tokens)."""
    batches, current = [], []
    for row in sorted(rows, key=lambda r: len(r[0])):
        if current and (len(current) + 1) * len(row[0]) > max_tokens:
            batches.append(current)
            current = []
        current.append(row)
    if current:
        batches.append(current)
    return batches
