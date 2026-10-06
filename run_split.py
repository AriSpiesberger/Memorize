"""Set up the environment and launch a label_split run, on Windows or Linux with an NVIDIA GPU.

    python run_split.py                                        # instruction SFT, built if missing
    python run_split.py --name mac-sft --mlx-adapter adapters/sft-run2   # the Mac's MLX SFT
    python run_split.py --name nogold --detach -- --exclude-gold --epochs 6
    python run_split.py --dry-run

Steps:
  1. create .venv if missing; reinstall requirements.txt whenever it changes
  2. check that torch sees a CUDA GPU
  3. get the starting point, an instruction-SFT LoRA on Qwen3.5-2B-Base:
       default        adapters/instruct; if it isn't there, pull it from
                      Hugging Face (Arisp/memorize-instruct, see adapters/models.json), and failing
                      that build the instruction data (memorize.sft_data) and
                      train it with memorize.sft_torch (the sft-run2 recipe)
       --mlx-adapter  an MLX LoRA (pulled from the hub if missing), converted
                      to PEFT once
  4. download the model and MMLU-Pro, retrying (HF downloads drop often)
  5. run `python -m memorize.label_split --out results/label-split/<date>_<benchmark>[_<name>]` inside .venv;
     anything after `--` is passed on to it

Output lands in results/label-split/<date>_<benchmark>[_<name>]/: train.log, metrics.jsonl, curves.png (redrawn
after every eval), splits.json, config.json, adapter/. Only the standard library
is used here, so any Python 3.10+ can start it; the work happens in .venv.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import venv
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
PY = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def step(msg):
    print(f"\033[36m==> {msg}\033[0m", flush=True)


def py(*args, **kw):
    """Run the venv's python; raise if it fails."""
    subprocess.run([str(PY), *args], cwd=ROOT, check=True, **kw)


def setup_env():
    if not PY.exists():
        step(f"creating .venv with Python {sys.version.split()[0]}")
        venv.create(VENV, with_pip=True)
    stamp = VENV / "requirements.sha256"
    digest = hashlib.sha256((ROOT / "requirements.txt").read_bytes()).hexdigest()
    if not stamp.exists() or stamp.read_text().strip().lower() != digest:
        step("installing requirements.txt")
        py("-m", "pip", "install", "-q", "--upgrade", "pip")
        py("-m", "pip", "install", "-q", "-r", "requirements.txt")
        stamp.write_text(digest)


def check_cuda():
    step("checking CUDA")
    code = (
        "import torch, sys; ok = torch.cuda.is_available(); "
        "print(torch.__version__, torch.cuda.get_device_name(0) if ok else 'NO CUDA GPU'); "
        "sys.exit(0 if ok else 1)"
    )
    try:
        py("-c", code)
    except subprocess.CalledProcessError:
        sys.exit("torch can't see a CUDA GPU; training needs one (this does not run on a Mac)")


def pull_from_hub(adapter_dir):
    """Fetch adapters/<name> from the project's HF repo if it is registered there."""
    reg = json.loads((ROOT / "adapters/models.json").read_text(encoding="utf-8"))
    name = Path(adapter_dir).name
    if name not in reg:
        return
    step(f"pulling {name} from huggingface.co/{reg[name]['hub_repo']}")
    subprocess.run([str(PY), "-m", "memorize.hub", "pull", name], cwd=ROOT)


def convert_adapter(mlx_dir, model):
    """PEFT copy of an MLX LoRA, converted once; returns (path, base model)."""
    mlx_dir = Path(mlx_dir)
    if not (ROOT / mlx_dir / "adapters.safetensors").exists():
        pull_from_hub(mlx_dir)
    if not (ROOT / mlx_dir / "adapters.safetensors").exists():
        sys.exit(
            f"{mlx_dir / 'adapters.safetensors'} is missing and not on the hub. Adapter weights are "
            f"not in git: push it from the Mac with `python -m memorize.hub push {mlx_dir.name}`, "
            f"or copy the file over."
        )
    if model is None:
        cfg = json.loads((mlx_dir / "adapter_config.json").read_text(encoding="utf-8"))
        model = cfg.get("model") or cfg["sft"]["model"]
    peft = mlx_dir.with_name(mlx_dir.name + "-peft")
    if not (peft / "adapter_model.safetensors").exists():
        step(f"converting {mlx_dir} -> {peft}")
        py("-m", "memorize.mlx_to_peft", "--mlx", str(mlx_dir), "--out", str(peft), "--base-model", model)
    return peft, model


def retry(what, args, tries=8):
    """Run the venv's python, retrying failures (network); show the last error."""
    for i in range(1, tries + 1):
        r = subprocess.run([str(PY), *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        if r.returncode == 0:
            return r.stdout
        print(f"   {what}: attempt {i} failed, retrying", flush=True)
        time.sleep(10)
    print("\n".join(r.stderr.strip().splitlines()[-5:]))
    sys.exit(f"{what} kept failing (last error above)")


def build_sft(out, model):
    """Pull the instruction SFT from the hub, or train it with the sft-run2 recipe."""
    if not (ROOT / out / "adapter_model.safetensors").exists():
        pull_from_hub(out)
    if (ROOT / out / "adapter_model.safetensors").exists():
        return
    if not (ROOT / "data/sft/train.jsonl").exists():
        step("building the instruction data (memorize.sft_data)")
        print(retry("sft data download", ["-m", "memorize.sft_data"]).strip())
    step(f"no {out} yet: training the instruction SFT (~300 steps)")
    retry("base model download", ["-c", f"from huggingface_hub import snapshot_download; snapshot_download({model!r})"])
    env = dict(os.environ, HF_HUB_OFFLINE="1", PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
    (ROOT / out).mkdir(parents=True, exist_ok=True)
    with open(ROOT / out / "train.log", "w", encoding="utf-8") as log:
        proc = subprocess.Popen(
            [str(PY), "-m", "memorize.sft_torch", "--model", model, "--out", str(out)],
            cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8",
        )
        for line in proc.stdout:
            log.write(line)
            if not line.startswith(("Loading weights", "W1", "[transformers]")):
                print("   " + line, end="", flush=True)
    if proc.wait() != 0:
        sys.exit(f"SFT training failed; see {out / 'train.log'}")


def fetch(model, bench="mmlu_pro", tries=10):
    step(f"fetching {model} and {bench}")
    code = (
        f"from huggingface_hub import snapshot_download; snapshot_download({model!r}); "
        f"from memorize import benchmarks; print(len(benchmarks.load({bench!r})), 'questions')"
    )
    for i in range(1, tries + 1):
        r = subprocess.run([str(PY), "-c", code], cwd=ROOT, capture_output=True, text=True)
        if r.returncode == 0:
            print(r.stdout.strip())
            return
        print(f"   download attempt {i} failed, retrying", flush=True)
        time.sleep(10)
    print("\n".join(r.stderr.strip().splitlines()[-5:]))
    sys.exit("downloads kept failing (last error above)")


def main():
    argv = sys.argv[1:]
    extra = argv[argv.index("--") + 1 :] if "--" in argv else []
    argv = argv[: argv.index("--")] if "--" in argv else argv
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--name", default="", help="optional tag, appended to the folder: results/label-split/<date>_<benchmark>[_<tag>]")
    p.add_argument("--model", help="base model under the adapter (default Qwen/Qwen3.5-2B-Base, "
                   "or the --mlx-adapter's own base)")
    p.add_argument(
        "--sft",
        default="adapters/instruct",
        help="PEFT instruction-SFT LoRA to start from; trained first if missing (default %(default)s)",
    )
    p.add_argument("--mlx-adapter", help="start from this MLX LoRA instead (e.g. adapters/sft-run2 from the Mac)")
    p.add_argument("--no-adapter", action="store_true", help="start from --model alone, with no LoRA")
    p.add_argument("--detach", action="store_true", help="run in the background")
    p.add_argument("--dry-run", action="store_true", help="set up and print the command, don't start")
    args = p.parse_args(argv)

    setup_env()
    check_cuda()
    model, adapter = args.model, []
    if args.no_adapter:
        if not model:
            sys.exit("--no-adapter needs --model")
    elif args.mlx_adapter:
        peft, model = convert_adapter(args.mlx_adapter, model)
        adapter = ["--adapter", str(peft)]
    else:
        model = model or "Qwen/Qwen3.5-2B-Base"
        if not args.dry_run:
            build_sft(Path(args.sft), model)
        adapter = ["--adapter", str(Path(args.sft))]
    bench = extra[extra.index("--bench") + 1] if "--bench" in extra else "mmlu_pro"
    fetch(model, bench)
    if "--replay-frac" not in extra or extra[extra.index("--replay-frac") + 1] != "0":
        if not (ROOT / "data/general/train.jsonl").exists():
            step("building the general-chat replay data (memorize.general_data)")
            print(retry("general data download", ["-m", "memorize.general_data"]).strip())

    tag = f"_{args.name}" if args.name else ""
    out = Path("results/label-split") / f"{datetime.now():%Y-%m-%d}_{bench}{tag}"
    cmd = [str(PY), "-m", "memorize.label_split", "--model", model, "--out", str(out), *adapter, *extra]
    # Everything is cached by now, so skip the flaky HF API calls.
    env = dict(os.environ, HF_HUB_OFFLINE="1", PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
    step(" ".join(["python", *cmd[1:]]))
    if args.dry_run:
        print("dry run: not starting")
        return
    if args.detach:
        (ROOT / out).mkdir(parents=True, exist_ok=True)
        err = open(ROOT / out / "stderr.log", "w", encoding="utf-8")
        kw = (
            {"creationflags": subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP}
            if os.name == "nt"
            else {"start_new_session": True}
        )
        proc = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=err, **kw)
        print(f"started in the background (pid {proc.pid}); its log is {out / 'train.log'}")
        return
    sys.exit(subprocess.run(cmd, cwd=ROOT, env=env).returncode)


if __name__ == "__main__":
    main()
