# chess_beyond

**Can a model trained on human games find the moves those humans miss?**

| folder | question | where it stands |
| --- | --- | --- |
| [transcend/](transcend/) | Imitate 1100-level players, then RL on easy puzzles only. Does it solve 2400-rated puzzles its teachers can't? | done: RL lifts easy puzzles, barely moves 2400s, and costs ~400 game Elo |
| [transcend/pgn/](transcend/pgn/) | The Transcendence paper's character-level PGN model, one per rating band | near-greedy, the 1000-1300 model plays ~350 above its data; the 2400+ model stays far below its data |
| [transcend/interp/](transcend/interp/) | What do the two PGN models represent, and which paths between concepts does only one take? | layer-15 crosscoder, explanations and path graphs built |
| [transcend/dynamic/](transcend/dynamic/) | Within each model, which latent patterns separate the line it plays from the one it doesn't, and do they steer it? | concepts mined; steering under test |
| [rating_bands/](rating_bands/) | Which moves does each rating band *never* find, as opposed to finding less often? Builds the puzzle strata. | strata built |
| [filter_experiment/](filter_experiment/) | Remove humans' excellent moves in hard positions from training. Can imitation, RL or search recover them? | runs end to end; needs far more data |

Numbers and figures: [results/transcend/summary.md](results/transcend/summary.md) (board model),
[results/transcend/eval/](results/transcend/eval/README.md) (PGN models).

## Layout

```
chess_beyond/
├── paths.py, common.py, search.py, probe.py, intervals.py, lichess_ids.py   shared helpers
├── transcend/          board-model experiment; pgn/, interp/, dynamic/ inside it
├── rating_bands/       games by rating band, puzzle strata
├── filter_experiment/  remove excellent moves, try to recover them
├── modal/              the cloud side (Modal apps only)
├── results/            reports and figures worth keeping                 (tracked)
└── data/ runs/ models/ tools/   datasets, checkpoints, Maia-2, Stockfish    (gitignored)
```

Run every command from this folder (`chess_beyond/`) with the repo's venv.

## Setup

```bash
pip install chess zstandard matplotlib            # torch comes from the repo's requirements.txt
pip install maia2 --no-deps einops gdown pandas pyyaml "pyzstd<0.20"   # Maia-2, keeping your torch
```

Put a Stockfish build in `tools/stockfish/` ([download](https://stockfishchess.org/download/)) or
point `$STOCKFISH` at one. Maia-2 weights download into `models/maia2/` on first use.

## Where code runs

Everything runs on a home GPU. [modal/](modal/README.md) holds only the Modal apps, which call
these scripts unchanged (so editing one changes both): `paths.py`, `common.py`, `probe.py`,
`lichess_ids.py`, `intervals.py`, `rating_bands/collect_games.py`, `rating_bands/puzzle_strata.py`
and the scripts in `transcend/pgn/`. `tools/check_repo.py` (repo root) keeps the two apart.
