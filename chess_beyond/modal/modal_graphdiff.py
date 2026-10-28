"""The concept-graph diff (transcend/graphdiff.py) on Modal, with its slow parts spread out: the rollouts over
several GPU containers, the board facts over CPU containers.

    export MODAL_PROFILE=arispiesberger
    modal run modal/modal_graphdiff.py::upload                 # once: the crosscoder and data from this machine
    modal run --detach modal/modal_graphdiff.py::main          # every stage
    modal run --detach modal/modal_graphdiff.py::main --stages plans --extra "--fit cluster --cluster-size 40"
    modal volume get chess-results transcend/graphdiff ./results/transcend   # report.md, plans.md, CSVs
    modal volume get chess-runs transcend/graphdiff ./runs/transcend         # lines, codes, motifs/plans pages

Stages (graphdiff.py's commands; --stages takes a comma-separated list, "lines" = roots, play, gather,
judge, encode):
  health, recall   one GPU container each
  roots            one GPU container: candidates and both models' policies at them
  play             --play-parts GPU containers, each running CHESS_PLAY_PROCS play processes side by side (playing
                   is bound by python-chess on the CPU, so one process leaves the GPU mostly idle), each process
                   the lines of its share of the roots
  gather           the play parts -> lines.json (CPU)
  judge            --judge-parts CPU containers of CHESS_JUDGE_CPU cores: the board facts (the anchor nodes) on
                   their share of the positions; no engine unless --extra "--depth 12" (the part files survive
                   a rerun, so a failed part is redone alone)
  encode           one GPU container: both models' states, the crosscoder codes
  plans, nodes     CPU (plans fits its LPs on CHESS_PLANS_CPU cores); nodes takes the latents of the plans that
                   passed the margin filter, so it comes after plans
  graph            one GPU container (the bootstraps)
--extra passes more flags to every stage (e.g. "--roots 8000 --plies 10"); --cc / --cc-run pick the crosscoder.

What upload puts on the Volumes (graphdiff.py reads them at the same paths as at home):
  chess-runs     transcend/crosscoder/<run>/: collect.json, rows.npy, squares.npz, acts/*-L<layer>.npy for the
                 crosscoder's layer, cc-L<layer>/ (cc.pt, latents.jsonl, facts.npz)
  chess-results  transcend/crosscoder/<run>/cc-L<layer>/explanations.jsonl (latent names, from explain.py)
  chess-data     graphdiff/population.jsonl (this machine's data/pgn_probe/population.jsonl: the roots), and if the
                 Volume lacks them: transcend/pgn-everything/ (the stored positions' games),
                 lichess/puzzles/histories.jsonl, strata/, pool/ (puzzle themes for recall)
The image carries Stockfish (Debian's, for the judge) and Stockfish 11 built from source (for recall's
classical evaluation terms; recall runs without them if that build failed). Models come from Hugging Face
and are cached on chess-runs (hf/); CHESS_HF_SECRET names a Modal secret with HF_TOKEN if the repos are private.
"""
import os
import subprocess
import sys
from pathlib import Path, PurePosixPath

import modal

from modal_shared import DATA, DATA_VOLUME, REMOTE, ROOT, lab_image

RUNS, RESULTS = f"{REMOTE}/runs", f"{REMOTE}/results"
GPU = os.environ.get("CHESS_GPU", "L40S")             # small models, Python-bound decoding: a big GPU buys little
JUDGE_CPU = int(os.environ.get("CHESS_JUDGE_CPU", "8"))
PLANS_CPU = int(os.environ.get("CHESS_PLANS_CPU", "32"))
PLAY_PROCS = int(os.environ.get("CHESS_PLAY_PROCS", "4"))   # play processes per GPU container
SF11 = "/usr/local/bin/stockfish11"
CC_RUN, CC = "runs/transcend/crosscoder/everything-3m", "Lfinal"
POPULATION = f"{DATA}/graphdiff/population.jsonl"     # the roots' held-out positions, as uploaded from this machine

app = modal.App("chess-beyond-graphdiff")
data = modal.Volume.from_name(DATA_VOLUME, create_if_missing=True)
runs = modal.Volume.from_name("chess-runs", create_if_missing=True)
results = modal.Volume.from_name("chess-results", create_if_missing=True)
VOLUMES = {DATA: data, RUNS: runs, RESULTS: results}
SECRETS = [modal.Secret.from_name(os.environ["CHESS_HF_SECRET"])] if os.environ.get("CHESS_HF_SECRET") else []
image = lab_image(
    "torch==2.11.*", "numpy", "scipy", "chess", "huggingface_hub", "safetensors",
    apt=["stockfish", "git", "make", "g++"],
    commands=["git clone --depth 1 --branch sf_11 https://github.com/official-stockfish/Stockfish /tmp/sf11 "
              f"&& make -C /tmp/sf11/src build ARCH=x86-64-modern -j8 && cp /tmp/sf11/src/stockfish {SF11} "
              "|| echo 'Stockfish 11 build failed: recall runs without the classical terms'"],
    env={"STOCKFISH": "/usr/games/stockfish", "HF_HOME": f"{RUNS}/hf", "PYTHONUNBUFFERED": "1"})


def run(stage, args, workers, device):
    """One graphdiff.py stage in this container, on the latest Volume contents; commit what it wrote."""
    for v in (data, runs, results):
        v.reload()
    if stage == "recall" and os.path.exists(SF11) and "--classic" not in args:
        args = [*args, "--classic", SF11]
    cmd = [sys.executable, "transcend/graphdiff.py", stage, *args, "--device", device, "--workers", str(workers)]
    print("$", " ".join(cmd), flush=True)
    try:
        subprocess.run(cmd, cwd=REMOTE, check=True)
    finally:
        runs.commit()
        results.commit()


@app.function(image=image, gpu=GPU, cpu=16.0, memory=64 * 1024, volumes=VOLUMES, secrets=SECRETS, timeout=8 * 60 * 60)
def gpu_stage(stage, args):
    run(stage, args, 16, "cuda")


@app.function(image=image, gpu=GPU, cpu=16.0, memory=64 * 1024, volumes=VOLUMES, secrets=SECRETS, timeout=8 * 60 * 60)
def play_group(arglists):
    """Several play parts side by side on one GPU, each with its share of the CPU threads."""
    for v in (data, runs, results):
        v.reload()
    threads = str(max(1, 16 // len(arglists)))
    env = dict(os.environ, OMP_NUM_THREADS=threads, MKL_NUM_THREADS=threads)
    procs = [subprocess.Popen([sys.executable, "transcend/graphdiff.py", "play", *args, "--device", "cuda"], cwd=REMOTE, env=env)
             for args in arglists]
    codes = [p.wait() for p in procs]
    runs.commit()
    if any(codes):
        raise RuntimeError(f"play parts exited with {codes}")


@app.function(image=image, cpu=float(JUDGE_CPU), memory=8 * 1024, volumes=VOLUMES, timeout=4 * 60 * 60)
def judge_stage(args):
    run("judge", args, JUDGE_CPU, "cpu")


@app.function(image=image, cpu=float(PLANS_CPU), memory=64 * 1024, volumes=VOLUMES, timeout=8 * 60 * 60)
def cpu_stage(stage, args):
    run(stage, args, PLANS_CPU, "cpu")


@app.local_entrypoint()
def main(stages: str = "health,recall,lines,plans,nodes,graph", play_parts: int = 8, judge_parts: int = 8,
         cc_run: str = CC_RUN, cc: str = CC, extra: str = ""):
    base = ["--cc-run", cc_run, "--cc", cc, "--population", POPULATION, *extra.split()]
    order = [s for x in stages.split(",") for s in (["roots", "play", "gather", "judge", "encode"] if x == "lines" else [x])]
    parts = play_parts * PLAY_PROCS
    for stage in order:
        print(f"=== {stage}", flush=True)
        if stage == "play":
            groups = [[[*base, "--part", str(p), "--parts", str(parts)] for p in range(g * PLAY_PROCS, (g + 1) * PLAY_PROCS)]
                      for g in range(play_parts)]
            list(play_group.map(groups))
        elif stage == "gather":
            cpu_stage.remote("gather", [*base, "--parts", str(parts)])
        elif stage == "judge":
            list(judge_stage.map([[*base, "--part", str(p), "--parts", str(judge_parts)] for p in range(judge_parts)]))
        elif stage in ("nodes", "plans"):
            cpu_stage.remote(stage, base)
        else:
            gpu_stage.remote(stage, base)


@app.local_entrypoint()
def upload(cc_run: str = CC_RUN, cc: str = CC):
    """Copy the crosscoder run (only the chosen layer's activations) and the data graphdiff.py reads onto the Volumes."""
    run_dir, layer = ROOT / cc_run, "L" + cc.removeprefix("cc-").removeprefix("L")
    rel = PurePosixPath(Path(cc_run).as_posix()).relative_to("runs")    # Volume paths use /, also from Windows
    with runs.batch_upload(force=True) as b:
        for f in ("collect.json", "rows.npy", "squares.npz"):
            if (run_dir / f).exists():
                b.put_file(run_dir / f, f"{rel}/{f}")
        for f in sorted((run_dir / "acts").glob(f"*-{layer}.npy")):
            b.put_file(f, f"{rel}/acts/{f.name}")
        b.put_directory(run_dir / f"cc-{layer}", f"{rel}/cc-{layer}")
    expl = ROOT / "results" / "transcend" / "crosscoder" / rel.name / f"cc-{layer}" / "explanations.jsonl"
    if expl.exists():
        with results.batch_upload(force=True) as b:
            b.put_file(expl, f"transcend/crosscoder/{rel.name}/cc-{layer}/explanations.jsonl")
    # data: only what the Volume lacks (the probe set and puzzle strata built on Modal stay as they are);
    # the roots' positions go to their own path, so this machine's copy never replaces Modal's
    d = ROOT / "data"
    with data.batch_upload(force=True) as b:
        b.put_file(d / "pgn_probe" / "population.jsonl", POPULATION.removeprefix(DATA + "/"))
        for local, remote in ((d / "transcend" / "pgn-everything", "transcend/pgn-everything"),
                              (d / "lichess" / "puzzles" / "histories.jsonl", "lichess/puzzles/histories.jsonl"),
                              (d / "lichess" / "puzzles" / "strata", "lichess/puzzles/strata"),
                              (d / "lichess" / "puzzles" / "pool", "lichess/puzzles/pool")):
            if not local.exists() or present(data, remote):
                print(f"  {remote}: {'already on chess-data' if local.exists() else 'not on this machine'}; skipped")
            elif local.is_dir():
                b.put_directory(local, remote)
            else:
                b.put_file(local, remote)
    print("uploaded")


def present(vol, path):
    parent, name = path.rsplit("/", 1)
    try:
        return any(e.path.rstrip("/").split("/")[-1] == name for e in vol.listdir(parent))
    except Exception:
        return False
