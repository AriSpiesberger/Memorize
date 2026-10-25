"""What the two Modal apps (modal_app.py, modal_train.py) share: where the lab is mounted,
the data Volume, the rating bands, and the container image that carries chess_beyond/.

Only Modal code imports this; the labs never do (tools/check_repo.py checks).
"""
from pathlib import Path

import modal

ROOT = Path(__file__).resolve().parent.parent      # chess_beyond/ (this file lives in chess_beyond/modal/)
REMOTE = "/root/chess_beyond"                      # where the container sees it
DATA = f"{REMOTE}/data"                            # where paths.py looks, so the scripts need no path flags
DATA_VOLUME = "chess-data"

# Rating bands: collect_games.py's --bands edges, and the tag of the per-month folders
# (data/lichess/bands/<month>-<tag>/). collect_games.py turns consecutive edges into bands, so
# the two ranges run as separate passes; one pass over "1000,1300,2400,4000" would also keep 1300-2400.
BANDS_SPEC = {"1000-1300": ("1000,1300", "train"), "2400+": ("2400,4000", "top")}


def months_back(latest, n):
    """`latest` and the n - 1 months before it, newest first, as YYYY-MM."""
    y, m = map(int, latest.split("-"))
    out = []
    for _ in range(n):
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y, m - 1) if m > 1 else (y - 1, 12)
    return out


def lab_image(*packages):
    """Debian with Python 3.12 and the given pip packages, plus chess_beyond/ at REMOTE (code only:
    no data, runs, models, tools, results or this folder) and this module (Modal ships only the
    entry file by itself)."""
    return (
        modal.Image.debian_slim(python_version="3.12")
        .pip_install(*packages)
        .add_local_dir(ROOT, REMOTE, ignore=["data", "runs", "models", "tools", "results", "modal",
                                             "**/__pycache__", "*.pyc"])
        .add_local_python_source("modal_shared")
    )
