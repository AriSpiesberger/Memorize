"""Put an rl_pgn_games.py model on Hugging Face, packaged like its starting model (config.json,
model.safetensors, pgn_model.py, README.md), with a model card comparing it to the starting model.

    python transcend/pgn/push_rl_hf.py --ckpt runs/transcend/rl-pgn-2400+-all-b0.01.pt --repo Arisp/chess-pgn-2400plus-rl

--ckpt is a final rl_pgn_games.py checkpoint (its args are read from it); <stem>_log.jsonl next to it gives
the games trained on. The card's tables come from eval.py's results/transcend/eval/<stem>-{games,positions,
puzzles}.json and the starting model's <name>-*.json, whichever exist. --dry-run writes the folder
(runs/transcend/hf/<repo name>/) and stops, to read the card first. Needs `hf auth login`.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # chess_beyond/
import paths  # noqa: E402

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--ckpt", required=True)
ap.add_argument("--repo", required=True, help="e.g. Arisp/chess-pgn-2400plus-rl")
ap.add_argument("--private", action="store_true")
ap.add_argument("--dry-run", action="store_true")
args = ap.parse_args()

ck = torch.load(args.ckpt, map_location="cpu")
rl = ck["extra"]["args"]
init = rl["init"]                                                   # the starting model's HF repo
from huggingface_hub import HfApi, snapshot_download  # noqa: E402
from safetensors.torch import save_file  # noqa: E402

base = Path(snapshot_download(init))
base_cfg = json.loads((base / "config.json").read_text())
stem = Path(args.ckpt).stem
log_path = Path(args.ckpt).with_name(stem + "_log.jsonl")
log = [json.loads(l) for l in open(log_path, encoding="utf-8")] if log_path.exists() else []
games = log[-1]["games"] if log else None
evdir = paths.ROOT / "results" / "transcend" / "eval"
ev = lambda name, kind: json.loads(p.read_text()) if (p := evdir / f"{name}-{kind}.json").exists() else None
base_name = init.split("/")[-1]
band = base_cfg["band"]
repo_name = args.repo.split("/")[-1]

out = paths.ROOT / "runs" / "transcend" / "hf" / repo_name
out.mkdir(parents=True, exist_ok=True)
save_file({k: v.contiguous() for k, v in ck["state"].items()}, out / "model.safetensors")
shutil.copy(Path(__file__).with_name("pgn_model.py"), out / "pgn_model.py")
cfg = dict(architecture=base_cfg["architecture"], vocab=base_cfg["vocab"], band=band, starting_model=init,
           rl=dict(method="outcome-weighted imitation (rl_pgn_games.py --loser skip)", games=games,
                   **{k: rl[k] for k in ("beta", "lr", "batch", "draw_reward", "max_elo_diff", "keep_unnormal",
                                         "gamma", "skip_plies", "seed")}),
           held_out=log[-1] if log else None)
(out / "config.json").write_text(json.dumps(cfg, indent=1))

# ---------------------------------------------------------------- model card
TEMPS = ["0.001", "0.01", "0.1", "1.0"]
rows = []
g_rl, g_base = ev(stem, "games"), ev(base_name, "games")
if g_rl and g_base:
    rows += ["## Results", "",
             "This model and the starting model, evaluated with the same code: `chess_beyond/transcend/pgn/eval.py` in",
             "[AriSpiesberger/Memorize](https://github.com/AriSpiesberger/Memorize), which also has the training script",
             "(`rl_pgn_games.py`).",
             "", "**Games** against Lichess's Stockfish levels 1, 3, 5, 7 and 8 (Fairy-Stockfish), 100 games per level from",
             "50 openings; Glicko-2 rating over the calibrated levels 1, 3 and 5 (95% interval: about +/-74 each).", "",
             f"| temperature | {base_name} | this model | change |", "|---|---|---|---|"]
    for t in TEMPS:
        a, b = g_base["by_temperature"].get(t), g_rl["by_temperature"].get(t)
        if a and b:
            rows.append(f"| {float(t):g} | {a['rating']:.0f} | **{b['rating']:.0f}** | {b['rating'] - a['rating']:+.0f} |")
    rows.append("")
p_rl, p_base = ev(stem, "puzzles"), ev(base_name, "puzzles")
if p_rl and p_base:
    rows += ["**Puzzles** (Lichess puzzles with their game history; 2,000 each at ratings 1050, 2400, 2600, 2800), puzzle rating:",
             "", f"| temperature | {base_name} | this model |", "|---|---|---|"]
    for t in TEMPS:
        a, b = p_base["by_temperature"].get(t), p_rl["by_temperature"].get(t)
        if a and b:
            rows.append(f"| {float(t):g} | {a['rating']:.0f} | **{b['rating']:.0f}** |")
    rows.append("")
q_rl, q_base = ev(stem, "positions"), ev(base_name, "positions")
if q_rl and q_base:
    rows += ["**Human-likeness**: held-out positions from games of this band, temperature 0.001; how often the model's",
             "top 1 / 3 / 5 moves contain the move the human played, and the expected score lost against Stockfish's",
             "best move (depth 12):", "", "| | top-1 | top-3 | top-5 | lost vs best |", "|---|---|---|---|---|"]
    for name, q in ((base_name, q_base), ("this model", q_rl)):
        r = q["by_temperature"]["0.001"][band]
        rows.append(f"| {name} | {r['top1']:.1%} | {r['top3']:.1%} | {r['top5']:.1%} | {r['lost_vs_best']:.2%} |")
    rows.append("")

kept = "the ones that ended normally (not on time, abandoned or by a rules infraction)"
card = f"""---
license: mit
library_name: pytorch
base_model: {init}
tags:
- chess
- pgn
- character-level
- transformer
---

# {repo_name}

[{base_name}](https://huggingface.co/{init}), a character-level PGN transformer trained only on Lichess games of
**{band}** players, fine-tuned to **play the moves that won** while staying on human lines. Same architecture,
same files, same usage as the starting model; only the weights differ.

## Method

Offline, outcome-weighted imitation on the band's own human games: no self-play, no engine, no rollouts.

- Games: the starting model's own {band} training games, {kept}{f"; {games:,} games, one pass" if games else ""}.
- In each decisive game the model is the **winner**, and only the winner's moves get a loss: the ordinary
  next-character cross-entropy on each move's characters. The loser's moves and the move numbers are context
  only. In a drawn game the model is a random side, at weight {rl['draw_reward']}.
- Plus {rl['beta']} x KL(policy || starting model) at the same characters, so it stays close to the human
  distribution it started from. AdamW, learning rate {rl['lr']}, {rl['batch']} games per step.

Every gradient step moves probability onto a move a human actually played, so the model cannot learn moves no
human would play; it shifts toward the human moves that won. The reward is the game result alone.

{chr(10).join(rows)}
## Usage

As for [{base_name}](https://huggingface.co/{init}), with this repository's id:

```python
import json, chess, torch
from huggingface_hub import snapshot_download
from safetensors.torch import load_file
import sys

path = snapshot_download("{args.repo}")
sys.path.insert(0, path)
from pgn_model import PGNTransformer, generate_moves

cfg = json.load(open(f"{{path}}/config.json"))["architecture"]
model = PGNTransformer(**cfg)
model.load_state_dict(load_file(f"{{path}}/model.safetensors"))
model.eval()

board = chess.Board()
board.push_san("e4")
move = generate_moves(model, [board], temperature=0.0, dev="cpu")[0]   # None if 5 attempts were illegal
print(board.san(move))
```

## Limitations

The starting model's: it knows the position only from the move history and occasionally writes an illegal
move; past roughly move 80-100 the game no longer fits its 1,024-character context. It plays like a strong
player of its band, blunders included; it is not an engine.
"""
(out / "README.md").write_text(card, encoding="utf-8")
print(f"wrote {out}")
if args.dry_run:
    sys.exit()
api = HfApi()
api.create_repo(args.repo, private=args.private, exist_ok=True)
api.upload_folder(repo_id=args.repo, folder_path=str(out), commit_message=f"{stem}: rl_pgn_games.py from {init}")
print(f"https://huggingface.co/{args.repo}")
