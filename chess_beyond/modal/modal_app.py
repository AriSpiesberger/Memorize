"""Build chess_beyond's data on Modal: the transcend setup, upsampled.

Same scripts, same filters, only more games: 10 million games per band where
both players are in the band and the base time is at least 3 minutes, for the
1000-1300 band (the imitation data) and 2400+.

    export MODAL_PROFILE=arispiesberger
    modal run modal/modal_app.py::smoke                 # one month, 20,000 games per band
    modal run --detach modal/modal_app.py::build_games  # every month needed, newest first, then merge
    modal run modal/modal_app.py::merge                 # re-run the merge alone

Each month runs in its own small container (half a core, 1 GiB): collect_games.py
streams the dump over HTTP and filters as it reads, so the ~30 GB file is never
stored, and only the band games are written to the `chess-data` Volume (mounted
where paths.py looks: chess_beyond/data). The work is mostly waiting on the
download, so a tiny container costs about $0.03 an hour. The merge
concatenates months newest first until each band holds exactly the target:

    data/lichess/bands/<month>-<tag>/<band>.pgn      per month
    data/lichess/bands/upsampled/<band>.pgn          10M games each, for make_data.py --pgn

Lichess's servers are shared, so at most MAX_PARALLEL months download at once.
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import modal

ROOT = Path(__file__).resolve().parent.parent      # chess_beyond/ (this file lives in chess_beyond/modal/)
REMOTE = "/root/chess_beyond"
DATA = f"{REMOTE}/data"
BANDS = f"{DATA}/lichess/bands"

# The transcend recipe (README: collect_games.py --bands 1000,1300 --min-base 180).
MIN_BASE = 180
PER_BAND = 10_000_000
# collect_games.py turns consecutive edges into bands, so the two ranges run as
# separate passes; one pass over "1000,1300,2400,4000" would also keep 1300-2400.
BANDS_SPEC = {"1000-1300": ("1000,1300", "train"), "2400+": ("2400,4000", "top")}
# Months to read, newest first. From a sample of 2025-06 and 2023-06: ~7.2M
# 1000-1300 games and ~0.3M 2400+ games per month at >= 3 minutes, so
# 1000-1300 fills in 2 months and 2400+ in ~33; 40 months leaves a margin.
LATEST = "2025-06"
N_MONTHS = {"1000-1300": 2, "2400+": 40}
# How many months stream at once, and the CPU each gets; set at launch, e.g.
# CHESS_PARALLEL=15 CHESS_CPU=1 modal run modal/modal_app.py::build_games
MAX_PARALLEL = int(os.environ.get("CHESS_PARALLEL", "6"))
COUNTS_URL = "https://database.lichess.org/standard/counts.txt"
CPU = float(os.environ.get("CHESS_CPU", "0.5"))


def git_commit():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True).stdout.strip() or "unknown"
    except OSError:
        return "unknown"


app = modal.App("chess-beyond-data")
volume = modal.Volume.from_name("chess-data", create_if_missing=True)
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("zstandard", "chess")
    .add_local_dir(
        ROOT,
        REMOTE,
        ignore=["data", "runs", "models", "tools", "results", "modal", "**/__pycache__", "*.pyc"],
    )
)


def months_back(latest, n):
    y, m = map(int, latest.split("-"))
    out = []
    for _ in range(n):
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y, m - 1) if m > 1 else (y - 1, 12)
    return out


def official_count(month):
    """Lichess's published game count for a month (database.lichess.org/standard/counts.txt)."""
    import urllib.request
    for line in urllib.request.urlopen(COUNTS_URL, timeout=60).read().decode().splitlines():
        if f"_{month}.pgn" in line:
            return int(line.split()[1])
    return None


def run(cmd, log):
    """Run one of the existing scripts, echo its output, keep it in a log, and
    return its stdout."""
    print("$", " ".join(cmd), flush=True)
    p = subprocess.run(cmd, cwd=REMOTE, capture_output=True, text=True)
    Path(log).parent.mkdir(parents=True, exist_ok=True)
    with open(log, "a") as f:
        f.write("$ " + " ".join(cmd) + "\n" + p.stdout + p.stderr[-4000:] + "\n")
    print(p.stdout[-2000:], flush=True)
    if p.returncode:
        raise RuntimeError(f"{cmd[1]} failed:\n{p.stderr[-2000:]}")
    return p.stdout


@app.function(
    image=image,
    volumes={DATA: volume},
    cpu=CPU,
    memory=1024,
    timeout=8 * 60 * 60,  # a month is ~30-55 min when Lichess is fast, ~4.5 h when throttled
    max_containers=MAX_PARALLEL,
    retries=2,  # a cut-short stream raises and is read again
)
def collect_month(month: str, bands: list[str], per_band: int = PER_BAND):
    """Keep one month's band games, streaming the dump (collect_games.py's
    default when no --pgn is given); one pass per band range."""
    volume.reload()
    counts = {}
    for band in bands:
        edges, tag = BANDS_SPEC[band]
        done = Path(BANDS) / f"{month}-{tag}" / f"{band}.done.json"
        if done.exists() and json.loads(done.read_text())["per_band"] == per_band:
            counts[band] = json.loads(done.read_text())["games"]   # finished in an earlier launch
            continue
        out = run([sys.executable, "rating_bands/collect_games.py", "--month", month, "--bands", edges,
                   "--min-base", str(MIN_BASE), "--per-band", str(per_band), "--tag", tag],
                  f"{BANDS}/logs/{month}.log")
        counts[band] = count_games(f"{BANDS}/{month}-{tag}/{band}.pgn")
        # A dropped connection looks like the end of the file to collect_games.py, so
        # check the games read against Lichess's own count unless the band filled up.
        read = int(re.search(r"read (\d+) games", out).group(1))
        expected = official_count(month)
        if counts[band] < per_band and expected and read != expected:
            Path(f"{BANDS}/{month}-{tag}/{band}.pgn").unlink(missing_ok=True)
            volume.commit()
            raise RuntimeError(f"{month}: read {read} of {expected} games (stream cut short); retrying")
        done.write_text(json.dumps({"games": counts[band], "per_band": per_band, "min_base": MIN_BASE,
                                    "games_read": read, "games_in_month": expected}))
        volume.commit()
    print(month, counts, flush=True)
    return month, counts


def count_games(path):
    n = 0
    with open(path, "rb") as f:
        for line in f:
            if line.startswith(b"[Event "):
                n += 1
    return n


@app.function(image=image, volumes={DATA: volume}, cpu=2.0, memory=4096, timeout=3 * 60 * 60)
def merge_bands(per_band: int = PER_BAND, out_name: str = "upsampled", commit: str = "unknown"):
    """Concatenate months newest first until each band has exactly `per_band`
    games. Reports how many came from each month."""
    volume.reload()
    out_dir = Path(BANDS) / out_name
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {}
    for band, (_, tag) in BANDS_SPEC.items():
        kept, sources = 0, []
        with open(out_dir / f"{band}.pgn", "wb") as out:
            for month in months_back(LATEST, N_MONTHS[band]):
                path = Path(BANDS) / f"{month}-{tag}" / f"{band}.pgn"
                if kept >= per_band or not path.exists():
                    continue
                taken, game = 0, []
                with open(path, "rb") as f:
                    for line in f:
                        if line.startswith(b"[Event ") and game:
                            out.write(b"".join(game))
                            taken, game = taken + 1, []
                            if kept + taken >= per_band:
                                break
                        game.append(line)
                    else:
                        if game and kept + taken < per_band:
                            out.write(b"".join(game))
                            taken += 1
                kept += taken
                sources.append((month, taken))
        report[band] = {"games": kept, "from": sources}
        print(f"{band}: {kept} games from {len(sources)} months", flush=True)
    manifest = {
        "built": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
        "code_commit": commit,
        "rule": "both players in the band, base time >= min_base_seconds, standard rated, no variants",
        "min_base_seconds": MIN_BASE,
        "per_band": per_band,
        "bands": {b: {"collect_games_bands": e, "tag": t} for b, (e, t) in BANDS_SPEC.items()},
        "order": "newest month first, whole months until the band is full",
        "files": {b: f"{b}.pgn" for b in BANDS_SPEC},
        "sources": report,
    }
    with open(out_dir / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    volume.commit()
    return report


@app.local_entrypoint()
def smoke():
    """One month, 20,000 games per band, into data/lichess/bands/<month>-<tag>/."""
    month, counts = collect_month.remote(LATEST, list(BANDS_SPEC), per_band=20_000)
    print("smoke:", month, counts)


@app.function(image=image, volumes={DATA: volume}, cpu=0.125, memory=512, timeout=24 * 60 * 60)
def build(commit: str = "unknown"):
    """Runs on Modal, so the laptop can close: hand out every month each band
    needs (MAX_PARALLEL at a time; finished months are skipped), then merge."""
    jobs = {}
    for band, n in N_MONTHS.items():
        for month in months_back(LATEST, n):
            jobs.setdefault(month, []).append(band)
    print(f"{len(jobs)} months: " + ", ".join(f"{m} {'+'.join(b)}" for m, b in jobs.items()))
    failed = []
    results = collect_month.starmap(jobs.items(), return_exceptions=True)
    for month, result in zip(jobs, results):
        if isinstance(result, BaseException):
            failed.append(month)
            print(f"{month} FAILED: {result}")
        else:
            print(*result)
    if failed:
        print(f"{len(failed)} months failed ({', '.join(failed)}); rerun build_games (finished months are skipped)")
        return {"failed": failed}
    report = merge_bands.remote(commit=commit)
    print(report)
    return report


@app.local_entrypoint()
def build_games():
    """Start the build on Modal and return. Needs --detach: without it Modal stops the app,
    and the build with it, as soon as this function returns."""
    call = build.spawn(commit=git_commit())
    print(f"build started on Modal (call {call.object_id}); follow it on the app page above.")
    print("It keeps running only if launched with `modal run --detach`.")


@app.local_entrypoint()
def merge():
    print(merge_bands.remote(commit=git_commit()))
