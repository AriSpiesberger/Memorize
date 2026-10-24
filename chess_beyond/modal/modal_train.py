"""Train the PGN model (the Transcendence paper's full-game model) on the upsampled games, on Modal.

    export MODAL_PROFILE=arispiesberger
    modal run --detach modal/modal_train.py::prepare                     # data for both bands + the probe set
    modal run modal/modal_train.py::smoke --band 1000-1300               # 200 steps, two evals, snapshots
    modal run --detach modal/modal_train.py::train_band --band 1000-1300 # the full run (paper: 100K steps)
    modal run --detach modal/modal_train.py::train_band --band 2400+

prepare (CPU, runs on Modal end to end), in this order so no test puzzle can leak:
  puzzle_strata.py   the puzzles for the later RL and evals, with the transcend quality bar
                     (rating deviation <= 90, >= 200 plays, >= 2 solver moves), taking only
                     puzzles whose source game is NOT in either band's SFT games:
                       data/lichess/puzzles/pool/1050.jsonl     every one rated 900-1200 (~600k);
                                                                train/test splits come later
                       data/lichess/puzzles/strata/<r>.jsonl    20,000 each at 2400 and 2600,
                                                                every one at 2800 (~7k), for evals
  make_pgn_data.py   exactly 10,000,000 training games + 5,000 held out per band, newest first:
                     data/lichess/bands/upsampled/<band>.pgn (the 10M database) followed by
                     sft-extra/<band>.pgn (the next 100,000 games in the same newest-first order,
                     from the months the merge stopped in), so the few games skipped (no moves)
                     or dropped (a test puzzle's source; expected none) and the held-out 5,000
                     are made up -> data/transcend/pgn-<band>/ (tokens.bin, starts.npy, meta.json)
  collect_games.py   20,000 games at 1600-1800 from 2025-06 -> data/lichess/bands/2025-06-probe/
  pgn_probe.py build 5,000 held-out positions per band + 10 labelled 1600-1800 positions
                     -> data/pgn_probe/
train (GPU): transcend/train_pgn.py with --compile --resume, so every eval writes
  runs/transcend/pgn-<band>.pt (best held-out loss), _log.jsonl, _state.pt and
  _pgn_probe/step<N>.png. Modal stops a function after 24 h, so after 23 h the run
  saves, hands over to a fresh container and continues from its last eval.

GPU: CHESS_GPU (default A100-80GB), e.g. CHESS_GPU=H100 modal run ...
"""
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import modal

ROOT = Path(__file__).resolve().parent.parent      # chess_beyond/ (this file lives in chess_beyond/modal/)
REMOTE = "/root/chess_beyond"
DATA, RUNS = f"{REMOTE}/data", f"{REMOTE}/runs"
BANDS = ["1000-1300", "2400+"]
TAG = {"1000-1300": "train", "2400+": "top"}         # modal_app.py's per-month folders: <month>-<tag>/
SFT_GAMES, EXTRA = 10_000_000, 100_000
PUZZLE_CSV = "https://database.lichess.org/lichess_db_puzzle.csv.zst"
QUALITY = ["--max-deviation", "90", "--min-plays", "200", "--min-moves", "2"]   # the transcend bar
PUZZLE_SETS = {                                       # folder -> stratum flags
    "pool": ["--centers", "1050", "--width", "150", "--per-stratum", "0"],                  # 900-1200, all
    "strata": ["--centers", "2400,2600,2800", "--width", "100", "--per-stratum", "20000"],  # evals
}
PROBE_MONTH = "2025-06"
GPU = os.environ.get("CHESS_GPU", "A100-80GB")
HANDOVER = 23 * 60 * 60                      # seconds before a fresh container takes over

app = modal.App("chess-beyond-train")
data = modal.Volume.from_name("chess-data", create_if_missing=True)
runs = modal.Volume.from_name("chess-runs", create_if_missing=True)
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("torch==2.11.*", "numpy", "chess", "zstandard", "matplotlib")
    .add_local_dir(ROOT, REMOTE, ignore=["data", "runs", "models", "tools", "results", "modal", "**/__pycache__", "*.pyc"])
)


def sh(cmd):
    """Run a repo script with live output; raise if it fails."""
    print("$", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=REMOTE, check=True)


@app.function(image=image, volumes={DATA: data}, cpu=2.0, memory=16 * 1024, timeout=3 * 60 * 60)
def puzzle_strata():
    """The RL pool and the eval strata, from puzzles whose source game is in neither band's SFT games."""
    csv = Path(DATA) / "lichess" / "lichess_db_puzzle.csv.zst"
    if not csv.exists():
        import urllib.request
        csv.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(PUZZLE_CSV, str(csv) + ".tmp")
        os.replace(str(csv) + ".tmp", csv)
        data.commit()
    for folder, flags in PUZZLE_SETS.items():
        out = Path(DATA) / "lichess" / "puzzles" / folder
        if (out / "strata_summary.json").exists():
            print(f"{out} already built; skipping")
            continue
        sh([sys.executable, "rating_bands/puzzle_strata.py", *flags, *QUALITY, "--out", str(out),
            "--exclude-games", *[f"data/lichess/bands/upsampled/{b}.pgn" for b in BANDS]])
        data.commit()


def months_back(month, n):
    y, m = map(int, month.split("-"))
    for _ in range(n):
        yield f"{y:04d}-{m:02d}"
        y, m = (y, m - 1) if m > 1 else (y - 1, 12)


def sft_extra(band, n=EXTRA):
    """The games that come right after the 10M database in its newest-first order: the rest of
    the month the merge stopped in, then older months, up to n games."""
    import json
    out = Path(DATA) / "lichess" / "bands" / "sft-extra" / f"{band}.pgn"
    if out.exists():
        return out
    manifest = json.loads((Path(DATA) / "lichess" / "bands" / "upsampled" / "manifest.json").read_text())
    last_month, taken = manifest["sources"][band]["from"][-1]
    out.parent.mkdir(parents=True, exist_ok=True)
    written, sources = 0, []
    with open(str(out) + ".tmp", "wb") as w:
        for i, month in enumerate(months_back(last_month, 60)):
            path = Path(DATA) / "lichess" / "bands" / f"{month}-{TAG[band]}" / f"{band}.pgn"
            if written >= n or not path.exists():
                continue
            skip, seen, mine, game = (taken if i == 0 else 0), 0, 0, []
            with open(path, "rb") as f:
                for line in f:
                    if line.startswith(b"[Event ") and game:
                        if seen >= skip:
                            w.write(b"".join(game)); written += 1; mine += 1
                        seen, game = seen + 1, []
                        if written >= n:
                            break
                    game.append(line)
                else:
                    if game and seen >= skip and written < n:
                        w.write(b"".join(game)); written += 1; mine += 1
            sources.append((month, skip, mine))
    os.replace(str(out) + ".tmp", out)
    (out.parent / f"{band}.json").write_text(json.dumps(dict(games=written, after=[last_month, taken], from_=sources)))
    print(f"{band}: {written} extra games after {last_month} game {taken}: {sources}", flush=True)
    return out


@app.function(image=image, volumes={DATA: data}, cpu=2.0, memory=24 * 1024, timeout=6 * 60 * 60)
def make_pgn(band: str):
    data.reload()
    puzzles = [Path(DATA) / "lichess" / "puzzles" / f for f in PUZZLE_SETS]
    if not all((p / "strata_summary.json").exists() for p in puzzles):
        raise RuntimeError("build the puzzles first (prepare does this), so their games can be kept out")
    out = Path(DATA) / "transcend" / f"pgn-{band}"
    if (out / "meta.json").exists():
        print(f"{out} already built; skipping")
        return
    extra = sft_extra(band)
    data.commit()
    sh([sys.executable, "transcend/make_pgn_data.py", "--pgn", f"data/lichess/bands/upsampled/{band}.pgn", str(extra),
        "--out", str(out), "--exclude-puzzles", *map(str, puzzles), "--games", str(SFT_GAMES)])
    data.commit()


@app.function(image=image, volumes={DATA: data}, cpu=1.0, memory=2048, timeout=2 * 60 * 60)
def probe_games():
    pgn = Path(DATA) / "lichess" / "bands" / f"{PROBE_MONTH}-probe" / "1600-1800.pgn"
    if pgn.exists() and pgn.stat().st_size > 0:
        print(f"{pgn} already collected; skipping")
        return
    sh([sys.executable, "rating_bands/collect_games.py", "--month", PROBE_MONTH, "--bands", "1600,1800",
        "--min-base", "180", "--per-band", "20000", "--tag", "probe"])
    data.commit()


@app.function(image=image, volumes={DATA: data}, cpu=2.0, memory=8192, timeout=2 * 60 * 60)
def build_probe():
    data.reload()
    sh([sys.executable, "transcend/pgn_probe.py", "build",
        "--data", *[f"data/transcend/pgn-{b}" for b in BANDS], "--names", *BANDS,
        "--labelled-pgn", f"data/lichess/bands/{PROBE_MONTH}-probe/1600-1800.pgn", "--labelled-name", "1600-1800"])
    data.commit()


@app.function(image=image, volumes={DATA: data}, cpu=0.125, memory=512, timeout=8 * 60 * 60)
def prepare_all():
    """Test strata (avoiding the SFT games) and the 1600-1800 games in parallel; then both
    bands' PGN data (avoiding the strata's games); then the probe set."""
    games = probe_games.spawn()
    puzzle_strata.remote()
    for c in [make_pgn.spawn(b) for b in BANDS]:
        c.get()
    games.get()
    build_probe.remote()


def commit_every(volume, seconds, stop):
    while not stop.wait(seconds):
        try:
            volume.commit()
        except Exception as e:                      # a failed background commit is retried next time
            print(f"[commit] {e}", flush=True)


@app.function(image=image, gpu=GPU, volumes={DATA: data, RUNS: runs}, cpu=8.0, memory=64 * 1024,
              timeout=24 * 60 * 60)
def train(band: str, stop_step: int = 0, eval_every: int = 1000, name: str = ""):
    out = f"runs/transcend/pgn-{band}{name}.pt"
    cmd = [sys.executable, "transcend/train_pgn.py", "--data", f"data/transcend/pgn-{band}", "--out", out,
           "--eval-every", str(eval_every), "--compile", "--resume"]
    if stop_step:
        cmd += ["--stop-step", str(stop_step)]
    print("$", " ".join(cmd), flush=True)
    stop = threading.Event()
    threading.Thread(target=commit_every, args=(runs, 600, stop), daemon=True).start()
    p = subprocess.Popen(cmd, cwd=REMOTE)
    try:
        code = p.wait(timeout=HANDOVER)
    except subprocess.TimeoutExpired:
        p.terminate()
        p.wait()
        stop.set()
        runs.commit()
        print("23 h reached: continuing in a fresh container from the last eval", flush=True)
        train.spawn(band, stop_step, eval_every, name)
        return
    stop.set()
    runs.commit()
    if code:
        raise RuntimeError(f"train_pgn.py exited with {code}")


@app.local_entrypoint()
def prepare():
    call = prepare_all.spawn()
    print(f"prepare started on Modal ({call.object_id}); with --detach it runs on after this terminal closes")


@app.local_entrypoint()
def smoke(band: str = "1000-1300"):
    """200 steps with evals at 100 and 200: checks memory, speed, checkpoints and the snapshots."""
    train.remote(band, stop_step=200, eval_every=100, name="-smoke")


@app.local_entrypoint()
def train_band(band: str = "1000-1300"):
    call = train.spawn(band)
    print(f"training {band} on Modal ({call.object_id}); with --detach it runs on after this terminal closes")
