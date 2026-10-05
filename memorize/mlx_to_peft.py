"""Convert an mlx-lm LoRA adapter into a PEFT adapter that PyTorch can load.

    python -m memorize.mlx_to_peft --mlx adapters/sft-run2 --out adapters/sft-run2-peft

mlx-lm computes  y = W x + scale * (x @ lora_a) @ lora_b  with lora_a of shape
(in, r) and lora_b of shape (r, out). PEFT computes
y = W x + (alpha / r) * B(A(x)) with A.weight (r, in) and B.weight (out, r), so
A = lora_a.T, B = lora_b.T and alpha = scale * r.

Module names are matched on the part from `layers.N.` onwards, which is the
same in both libraries; the prefix in front of it differs between them.
"""

import argparse
import json
import re
from pathlib import Path

from safetensors.numpy import load_file
from safetensors.torch import save_file

LAYER_PATH = re.compile(r"(layers\.\d+\..+)\.lora_([ab])$")


def convert(mlx_dir, out_dir, base_model, prefix):
    mlx_dir, out_dir = Path(mlx_dir), Path(out_dir)
    cfg = json.loads((mlx_dir / "adapter_config.json").read_text())
    lora = cfg["lora_parameters"]
    rank, scale = lora["rank"], lora["scale"]

    import torch

    weights, modules = {}, set()
    for key, value in load_file(str(mlx_dir / "adapters.safetensors")).items():
        m = LAYER_PATH.search(key)
        if not m:
            raise ValueError(f"unexpected adapter key {key}")
        path, which = m.groups()
        modules.add(path.split(".")[-1])
        t = torch.from_numpy(value.astype("float32")).T.contiguous()
        weights[f"{prefix}{path}.lora_{which.upper()}.weight"] = t

    out_dir.mkdir(parents=True, exist_ok=True)
    save_file(weights, str(out_dir / "adapter_model.safetensors"))
    (out_dir / "adapter_config.json").write_text(
        json.dumps(
            {
                "peft_type": "LORA",
                "task_type": "CAUSAL_LM",
                "base_model_name_or_path": base_model,
                "r": rank,
                "lora_alpha": scale * rank,
                "lora_dropout": lora.get("dropout", 0.0),
                "target_modules": sorted(modules),
                "bias": "none",
                "converted_from": str(mlx_dir),
            },
            indent=2,
        )
    )
    print(f"{len(weights)} tensors, modules {sorted(modules)} -> {out_dir}")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mlx", required=True, help="mlx-lm adapter directory")
    p.add_argument("--out", required=True)
    p.add_argument("--base-model", default="Qwen/Qwen3.5-2B-Base")
    p.add_argument(
        "--prefix",
        default="base_model.model.model.",
        help="PEFT key prefix in front of `layers.N.` for the transformers model class used",
    )
    args = p.parse_args()
    convert(args.mlx, args.out, args.base_model, args.prefix)


if __name__ == "__main__":
    main()
