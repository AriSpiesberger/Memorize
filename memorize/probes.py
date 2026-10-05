"""Instruction-following probes: short prompts with output constraints that a
check function verifies from the reply text alone. Shared by the MLX and
PyTorch SFT scripts."""

import json
import re


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
    return len(re.findall(r"[.!?。！？]+(?=\s|$)", text.strip()))
