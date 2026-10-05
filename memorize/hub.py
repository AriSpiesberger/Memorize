"""Share trained adapters on the Hugging Face Hub, one repo per model.

Adapter weights are not in git. adapters/models.json lists each shared model,
its hub repo, how it was made (code commit, commands, data checksums,
environment) and what it scored; the model card on the hub is generated from
that entry. Pulling a public repo needs no login; pushing needs `hf auth login`.

    python -m memorize.hub list                   # registry, local and hub status
    python -m memorize.hub pull instruct          # download into adapters/instruct
    python -m memorize.hub push instruct          # upload adapters/instruct + model card

Loading straight from the hub:
    from peft import PeftModel
    model = PeftModel.from_pretrained(base_model, "Arisp/memorize-instruct")
"""

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADAPTERS = ROOT / "adapters"
REGISTRY = ADAPTERS / "models.json"
GITHUB = "https://github.com/AriSpiesberger/Memorize"

# The weights the loaders need plus the training record; checkpoints stay local.
FILES = {
    "peft": ["adapter_config.json", "adapter_model.safetensors", "sft_torch.json", "train.log"],
    "mlx": ["adapter_config.json", "adapters.safetensors"],
}


def registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def is_local(name, info):
    return (ADAPTERS / name / FILES[info["format"]][1]).exists()


def retry(fn, what, tries=6):
    """HF connections drop often; retry with a pause."""
    for attempt in range(1, tries + 1):
        try:
            return fn()
        except Exception as e:
            if attempt == tries:
                raise
            print(f"   {what}: attempt {attempt} failed ({type(e).__name__}), retrying", flush=True)
            time.sleep(8)


def model_card(name, info):
    rec, res = info["recipe"], info["results"]
    mmlu = res["mmlu_pro_direct_letter"]
    return f"""---
license: apache-2.0
base_model: {info["base_model"]}
library_name: peft
pipeline_tag: text-generation
datasets:
  - allenai/tulu-3-sft-personas-instruction-following
  - databricks/databricks-dolly-15k
tags: [lora, peft, qwen3.5, instruction-tuning]
---

# {name}

{info["summary"]}

From [Memorize]({GITHUB}), a small lab for poking at Qwen3.5-2B.

## use

```python
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

tok = AutoTokenizer.from_pretrained("{info["base_model"]}")
base = AutoModelForCausalLM.from_pretrained("{info["base_model"]}", dtype=torch.bfloat16)
model = PeftModel.from_pretrained(base, "{info["hub_repo"]}")

ids = tok.apply_chat_template(
    [{{"role": "user", "content": "Name three fruits."}}],
    add_generation_prompt=True, enable_thinking=False, return_tensors="pt", return_dict=True,
)["input_ids"]
out = model.generate(ids, max_new_tokens=100, eos_token_id=tok.convert_tokens_to_ids("<|im_end|>"))
print(tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True))
```

Use the chat template with `enable_thinking=False` (how it was trained), and stop
on `<|im_end|>`: the base model's own config only stops on `<|endoftext|>`.

## results

| | base model | this adapter |
| --- | --- | --- |
| validation loss (200 held-out chats) | {res["valid_loss"]["before"]:.3f} | {res["valid_loss"]["after"]:.3f} |
| instruction probes passed (greedy) | {res["instruction_probes"]["before"]} | {res["instruction_probes"]["after"]} |
| MMLU-Pro, direct letter, n={mmlu["n"]} | {mmlu["before"]:.1%} | {mmlu["after"]:.1%} |

Probes are short prompts with checkable output constraints
([memorize/probes.py]({GITHUB}/blob/main/memorize/probes.py)). MMLU-Pro is
scored from the letter right after `ANSWER:` with no reasoning, on {mmlu["set"]}
([memorize/label_split.py]({GITHUB}/blob/main/memorize/label_split.py)).

## how it was made

- **Data**: 1,800 constraint-following chats from tulu-3-sft-personas-instruction-following
  plus 600 Dolly-15k chats, 200 held out for validation, each at most 512 tokens;
  multiple-choice and step-by-step items dropped. Seed 0.
- **LoRA**: rank 8, alpha 160 (mlx-lm's scale of 20), no dropout, on every linear
  layer of every block (attention, linear attention, MLP); 8.4M parameters.
- **Training**: 1 epoch, 300 steps of 8 chats, Adam at lr 1e-5 (20 warmup steps
  from 1%, then cosine to 10%), gradient norm clipped at 20, bf16, loss on the
  assistant reply only. Seed 0.
- **Environment**: {rec["environment"]}.

`sft_torch.json` (in this repo) has every argument and the validation curve;
`train.log` is the full training log.

## reproduce

```bash
git clone {GITHUB} && cd Memorize
git checkout {rec["code_commit"]}        # the code that trained it
python -m venv .venv && .venv/bin/pip install -r requirements.txt   # Windows: .venv\\Scripts\\pip
{rec["data"]}           # data/sft/train.jsonl, valid.jsonl
{rec["train"]}
```

The data files should hash to sha256 `{rec["data_sha256"]["train.jsonl"]}…` (train) and
`{rec["data_sha256"]["valid.jsonl"]}…` (valid) if the upstream datasets are unchanged.
"""


def push(name, info, private):
    from huggingface_hub import HfApi

    folder = ADAPTERS / name
    files = [f for f in FILES[info["format"]] if (folder / f).exists()]
    if FILES[info["format"]][1] not in files:
        sys.exit(f"no {FILES[info['format']][1]} in {folder}")
    repo = info["hub_repo"]
    api = HfApi()
    retry(lambda: api.create_repo(repo, repo_type="model", private=private, exist_ok=True), "create repo")
    print(f"push {name} -> {repo}: {', '.join(files)}", flush=True)
    retry(
        lambda: api.upload_folder(
            repo_id=repo, folder_path=str(folder), allow_patterns=files, commit_message=f"Upload {name}"
        ),
        "upload",
    )
    retry(
        lambda: api.upload_file(
            repo_id=repo,
            path_or_fileobj=model_card(name, info).encode("utf-8"),
            path_in_repo="README.md",
            commit_message="Update model card",
        ),
        "model card",
    )
    print(f"https://huggingface.co/{repo}")


def pull(name, info):
    from huggingface_hub import snapshot_download

    retry(
        lambda: snapshot_download(
            info["hub_repo"], allow_patterns=FILES[info["format"]], local_dir=str(ADAPTERS / name)
        ),
        f"pull {name}",
    )
    print(f"pull {name}: {'ok' if is_local(name, info) else 'failed'} -> adapters/{name}", flush=True)


def show(reg):
    from huggingface_hub import list_repo_files

    print(f"{'model':12} {'local':6} {'hub':4}  hub repo")
    for name, info in reg.items():
        try:
            on_hub = FILES[info["format"]][1] in retry(lambda: list_repo_files(info["hub_repo"]), "list", 3)
        except Exception:
            on_hub = None
        hub = {True: "yes", False: "-", None: "?"}[on_hub]
        print(f"{name:12} {'yes' if is_local(name, info) else '-':6} {hub:4}  https://huggingface.co/{info['hub_repo']}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("action", choices=["list", "push", "pull"])
    p.add_argument("names", nargs="*", help="models from adapters/models.json (default: all)")
    p.add_argument("--private", action="store_true", help="create the hub repo as private")
    args = p.parse_args()

    reg = registry()
    names = args.names or list(reg)
    unknown = [n for n in names if n not in reg]
    if unknown:
        sys.exit(f"not in adapters/models.json: {', '.join(unknown)}")
    if args.action == "list":
        show({n: reg[n] for n in names})
    for name in names if args.action != "list" else []:
        (push(name, reg[name], args.private) if args.action == "push" else pull(name, reg[name]))


if __name__ == "__main__":
    main()
