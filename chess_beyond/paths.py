"""Where everything lives, so scripts work from any working directory.

    chess_beyond/
    ├── data/     downloads and datasets      (gitignored)
    ├── runs/     checkpoints, logs, results  (gitignored)
    ├── models/   third-party weights, Maia-2 (gitignored)
    └── tools/    Stockfish binary            (gitignored)
"""
import glob
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RUNS = ROOT / "runs"
MODELS = ROOT / "models"
TOOLS = ROOT / "tools"

LICHESS = DATA / "lichess"          # monthly .pgn.zst files and bands/<month>/
FILTER_DATA = DATA / "filter"       # positions*.jsonl and splits/ for the filter experiment
FILTER_RUNS = RUNS / "filter"       # ckpt/, logs/, results.json
MAIA2 = MODELS / "maia2"            # pass as save_root to maia2.model.from_pretrained


def stockfish():
    """The Stockfish binary under tools/stockfish (any build), or $STOCKFISH."""
    if os.environ.get("STOCKFISH"):
        return os.environ["STOCKFISH"]
    found = [f for f in sorted(glob.glob(str(TOOLS / "stockfish" / "stockfish*")))
             if os.path.isfile(f) and (f.endswith(".exe") or os.access(f, os.X_OK))]
    if not found:
        raise SystemExit("no Stockfish found: put a build in chess_beyond/tools/stockfish/ or set $STOCKFISH "
                         "(https://stockfishchess.org/download/)")
    return found[0]
