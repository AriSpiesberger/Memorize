"""Multiple-choice benchmarks in one format.

Every item is a dict: {id, benchmark, subject, question, options, answer}
where `options` is a list of strings and `answer` is the gold letter.
"""

import json
import random
import re
from pathlib import Path

LETTERS = "ABCDEFGHIJ"
CACHE_DIR = Path(__file__).parent.parent / "data"

PROMPT = """Answer the following multiple choice question. The last line of your \
response must be in the format "Answer: X", where X is the letter of the correct option.

{question}

{options}"""

ANSWER_RE = re.compile(r"(?:Answer|答案)\s*[:：]\s*[\*\(\[\s]*([A-J])\b", re.IGNORECASE)


def _mmlu_pro():
    from datasets import load_dataset

    for r in load_dataset("TIGER-Lab/MMLU-Pro", split="test"):
        yield {
            "id": str(r["question_id"]),
            "subject": r["category"],
            "question": r["question"],
            "options": r["options"],
            "answer": r["answer"],
        }


def _mmlu_redux():
    from datasets import get_dataset_config_names, load_dataset

    name = "edinburgh-dawg/mmlu-redux-2.0"
    for subject in get_dataset_config_names(name):
        for i, r in enumerate(load_dataset(name, subject, split="test")):
            # Redux flags questions whose original MMLU label is broken; keep
            # only the ones annotated as fine.
            if r["error_type"] != "ok":
                continue
            yield {
                "id": f"{subject}-{i}",
                "subject": subject,
                "question": r["question"],
                "options": r["choices"],
                "answer": LETTERS[r["answer"]],
            }


def _ceval():
    from datasets import get_dataset_config_names, load_dataset

    name = "ceval/ceval-exam"
    for subject in get_dataset_config_names(name):
        for r in load_dataset(name, subject, split="val"):
            yield {
                "id": f"{subject}-{r['id']}",
                "subject": subject,
                "question": r["question"],
                "options": [r[k] for k in "ABCD"],
                "answer": r["answer"],
            }


def _supergpqa():
    from huggingface_hub import hf_hub_download

    path = hf_hub_download("m-a-p/SuperGPQA", "SuperGPQA-all.jsonl", repo_type="dataset")
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            yield {
                "id": r["uuid"],
                "subject": r["discipline"],
                "question": r["question"],
                "options": r["options"],
                "answer": r["answer_letter"],
            }


def _gpqa():
    import csv

    from huggingface_hub import hf_hub_download

    # Gated: accept the terms at huggingface.co/datasets/Idavidrein/gpqa and
    # run `hf auth login` first.
    path = hf_hub_download("Idavidrein/gpqa", "gpqa_diamond.csv", repo_type="dataset")
    rng = random.Random(0)
    with open(path, newline="", encoding="utf-8") as f:
        for i, r in enumerate(csv.DictReader(f)):
            correct = r["Correct Answer"].strip()
            options = [correct] + [r[f"Incorrect Answer {k}"].strip() for k in (1, 2, 3)]
            rng.shuffle(options)
            yield {
                "id": str(i),
                "subject": r["High-level domain"],
                "question": r["Question"].strip(),
                "options": options,
                "answer": LETTERS[options.index(correct)],
            }


BENCHMARKS = {
    "mmlu_pro": _mmlu_pro,
    "mmlu_redux": _mmlu_redux,
    "ceval": _ceval,
    "supergpqa": _supergpqa,
    "gpqa": _gpqa,
}


def load(name):
    """All items of a benchmark, cached as jsonl under data/."""
    path = CACHE_DIR / f"{name}.jsonl"
    if not path.exists():
        items = [dict(item, benchmark=name) for item in BENCHMARKS[name]()]
        CACHE_DIR.mkdir(exist_ok=True)
        # Explicit utf-8 (Windows defaults to cp1252); write then rename so an
        # interrupted download never leaves a truncated cache behind.
        tmp = path.with_suffix(".jsonl.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            for item in items:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        tmp.replace(path)
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def split(name, n_eval, seed=0):
    """Fixed (eval, rest) split. The eval set for a given seed is a prefix of
    the same shuffle, so growing n_eval only adds questions; `rest` is the pool
    that training may draw from."""
    items = load(name)
    random.Random(seed).shuffle(items)
    return items[:n_eval], items[n_eval:]


def format_prompt(item):
    options = "\n".join(f"{LETTERS[i]}. {o}" for i, o in enumerate(item["options"]))
    return PROMPT.format(question=item["question"], options=options)


def extract_answer(text):
    """The letter the model settled on, or None if it never gave one."""
    matches = ANSWER_RE.findall(text)
    return matches[-1].upper() if matches else None
