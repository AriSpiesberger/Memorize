"""Share the trained LoRA adapters through one Hugging Face model repo.

Adapter weights are not in git. Each adapter in adapters/models.json lives in
its own folder of the hub repo (`<repo>/<name>/`), next to a README that lists
them all. Runs on the Mac and on Windows; needs `hf auth login` (write token)
to push, nothing to pull from a public repo.

    python -m memorize.hub list                       # registry, local and hub status
    python -m memorize.hub push sft-run2-torch        # upload adapters/sft-run2-torch
    python -m memorize.hub push --all                 # every adapter present locally
    python -m memorize.hub pull sft-run2              # download into adapters/sft-run2
    python -m memorize.hub pull --all

The first push without `--repo` creates `<your hf user>/memorize-adapters` and
records it in adapters/models.json, so commit that file afterwards.

Loading one directly:
    PeftModel.from_pretrained(model, "<repo>", subfolder="sft-run2-torch")   # peft
    mlx_lm.load("Qwen/Qwen3.5-2B-Base", adapter_path="adapters/sft-run2")    # mlx, after pull
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADAPTERS = ROOT / "adapters"
REGISTRY = ADAPTERS / "models.json"

# What a pushed adapter folder holds: the weights the loaders need plus the
# training record. Intermediate checkpoints stay local.
FILES = {
    "mlx": ["adapter_config.json", "adapters.safetensors"],
    "peft": ["adapter_config.json", "adapter_model.safetensors", "sft_torch.json", "train.log"],
}


def registry():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def save_registry(reg):
    REGISTRY.write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")


def weights_file(fmt):
    return FILES[fmt][1]


def is_local(name, info):
    return (ADAPTERS / name / weights_file(info["format"])).exists()


def resolve_repo(reg, repo, create=False):
    repo = repo or reg.get("hub_repo")
    if repo:
        return repo
    if not create:
        sys.exit("no hub repo yet: adapters/models.json has no hub_repo; push first or pass --repo")
    from huggingface_hub import whoami

    try:
        user = whoami()["name"]
    except Exception:
        sys.exit("not logged in to Hugging Face: run `hf auth login` with a write token first")
    return f"{user}/memorize-adapters"


def model_card(reg, repo):
    rows = "\n".join(
        f"| `{name}` | {info['format']} | {info['base_model']} | {info['summary']} |"
        for name, info in reg["models"].items()
    )
    return f"""---
license: mit
base_model: Qwen/Qwen3.5-2B-Base
library_name: peft
tags: [lora, qwen3.5, mmlu-pro, memorization]
---

# memorize adapters

LoRA adapters from [Memorize](https://github.com/AriSpiesberger/Memorize), a small
lab for poking at Qwen3.5-2B. Every adapter sits on `Qwen/Qwen3.5-2B-Base`, in its
own folder of this repo. `mlx` adapters load with mlx-lm on Apple Silicon (and convert
to PyTorch with `python -m memorize.mlx_to_peft`); `peft` adapters load with PEFT.

| adapter | format | base | what it is |
| --- | --- | --- | --- |
{rows}

```python
from huggingface_hub import snapshot_download
snapshot_download("{repo}", allow_patterns=["sft-run2-torch/*"], local_dir="adapters")

# or, for a peft adapter, straight from the hub:
from peft import PeftModel
model = PeftModel.from_pretrained(base_model, "{repo}", subfolder="sft-run2-torch")
```

In the Memorize repo: `python -m memorize.hub pull <name>` (or `--all`).
"""


def push(names, repo, private):
    from huggingface_hub import HfApi

    reg = registry()
    repo = resolve_repo(reg, repo, create=True)
    api = HfApi()
    api.create_repo(repo, repo_type="model", private=private, exist_ok=True)
    for name in names:
        info = reg["models"][name]
        folder = ADAPTERS / name
        files = [f for f in FILES[info["format"]] if (folder / f).exists()]
        if weights_file(info["format"]) not in files:
            print(f"skip {name}: no {weights_file(info['format'])} here (trained on {info['trained_on']})")
            continue
        print(f"push {name} -> {repo}/{name}: {', '.join(files)}", flush=True)
        api.upload_folder(
            repo_id=repo,
            folder_path=str(folder),
            path_in_repo=name,
            allow_patterns=files,
            commit_message=f"Upload {name}",
        )
    api.upload_file(
        repo_id=repo,
        path_or_fileobj=model_card(reg, repo).encode("utf-8"),
        path_in_repo="README.md",
        commit_message="Update model card",
    )
    if reg.get("hub_repo") != repo:
        reg["hub_repo"] = repo
        save_registry(reg)
        print(f"recorded hub_repo = {repo} in adapters/models.json; commit it")
    print(f"https://huggingface.co/{repo}")


def pull(names, repo, tries=6):
    import time

    from huggingface_hub import snapshot_download

    reg = registry()
    repo = resolve_repo(reg, repo)
    for name in names:
        patterns = [f"{name}/{f}" for f in FILES[reg["models"][name]["format"]]]
        for attempt in range(1, tries + 1):
            try:
                snapshot_download(repo, allow_patterns=patterns, local_dir=str(ADAPTERS))
                break
            except Exception as e:  # HF downloads drop often; retry
                if attempt == tries:
                    raise
                print(f"   {name}: attempt {attempt} failed ({type(e).__name__}), retrying", flush=True)
                time.sleep(10)
        ok = is_local(name, reg["models"][name])
        print(f"pull {name}: {'ok' if ok else 'not on the hub yet'}", flush=True)


def show(repo):
    reg = registry()
    repo = repo or reg.get("hub_repo")
    remote = set()
    if repo:
        try:
            from huggingface_hub import list_repo_files

            remote = {f.split("/")[0] for f in list_repo_files(repo)}
        except Exception as e:
            print(f"(couldn't list {repo}: {type(e).__name__})")
    print(f"hub repo: {repo or '(none yet)'}\n")
    print(f"{'adapter':18} {'format':6} {'local':6} {'hub':4}  summary")
    for name, info in reg["models"].items():
        print(
            f"{name:18} {info['format']:6} {'yes' if is_local(name, info) else '-':6} "
            f"{'yes' if name in remote else '-':4}  {info['summary'][:70]}"
        )


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("action", choices=["list", "push", "pull"])
    p.add_argument("names", nargs="*", help="adapter names from adapters/models.json")
    p.add_argument("--all", action="store_true", help="every adapter in the registry")
    p.add_argument("--repo", help="hub repo id (default: hub_repo in adapters/models.json)")
    p.add_argument("--private", action="store_true", help="create the hub repo as private")
    args = p.parse_args()

    known = registry()["models"]
    names = list(known) if args.all else args.names
    unknown = [n for n in names if n not in known]
    if unknown:
        sys.exit(f"not in adapters/models.json: {', '.join(unknown)}")
    if args.action == "list":
        show(args.repo)
    elif not names:
        sys.exit("name one or more adapters, or pass --all")
    elif args.action == "push":
        push(names, args.repo, args.private)
    else:
        pull(names, args.repo)


if __name__ == "__main__":
    main()
