# chess_beyond

**Can a model trained on human games find the moves those humans miss?**

Two experiments share this folder:

| | question | status |
| --- | --- | --- |
| [filter_experiment/](filter_experiment/) | Remove the excellent moves humans found in hard positions from the training data. Can imitation, RL or search still find them? | runs end to end; needs far more data |
| [rating_bands/](rating_bands/) | Which moves does each rating band *never* find (ability), as opposed to finding them less often (consistency)? | pipeline built; waiting on a full month of games |

## Layout

```
chess_beyond/
├── paths.py              where data, runs, models and Stockfish live
├── common.py             board encoding, move vocabulary, the policy/value network
├── search.py             PUCT tree search using only the network (no engine)
├── filter_experiment/    experiment 1
├── rating_bands/         experiment 2
├── data/      lichess/ downloads, filter/ positions and splits     (gitignored)
├── runs/      checkpoints, logs, results                           (gitignored)
├── models/    maia2/ weights (downloaded by the maia2 package)     (gitignored)
└── tools/     stockfish/ binary                                    (gitignored)
```

Run every command from this folder (`chess_beyond/`) with the repo's venv.

## Setup

```bash
pip install chess zstandard matplotlib            # torch comes from the repo's requirements.txt
```

Put a Stockfish build in `tools/stockfish/` ([download](https://stockfishchess.org/download/)),
or point `$STOCKFISH` at one. `paths.stockfish()` finds it either way.

## Experiment 1: filter_experiment

```bash
python filter_experiment/build_dataset.py --pgn data/lichess/2015-01.pgn.zst \
    --out data/filter/positions.jsonl --games 10000 --workers 30     # Stockfish labels, ~2.5 h
python filter_experiment/make_splits.py --positions data/filter/positions.jsonl --test-frac 0.3
python filter_experiment/run_experiment.py                         # imitation x3, RL x3, evaluate
```

| step | what it does |
| --- | --- |
| `build_dataset.py` | samples positions from 1100-1600 games; Stockfish finds the best moves and how deep it had to search to find them (`depth_to_find`). Easy positions get cheaper labels, so it runs ~6x faster than a full search. |
| `make_splits.py` | bands positions as easy / buffer / hard, splits by game, and builds the three training sets: `full`, `filtered` (human best moves in hard positions removed) and `random` (same number removed at random) |
| `train_sft.py` | imitation of the human move; early-stops on held-out games |
| `rl_finetune.py` | RL from `filtered`, rewarded by the deep engine, a shallow engine, or a coin flip |
| `evaluate.py` | best-move rate on held-out hard and easy positions, with and without search |
| `run_experiment.py` | runs the last three in order, resumable; writes to `runs/filter/` |

Note: the reward in `rl_finetune.py` comes from Stockfish, so it measures whether the model can
*learn* the moves when told, not whether it *discovers* them. Self-play or expert iteration
would be the honest "beyond the teachers" arm, and isn't built yet.

## Experiment 2: rating_bands

```bash
python rating_bands/download_month.py --month 2025-06              # ~30 GB, resumable, 2-3 h
python rating_bands/collect_games.py --month 2025-06 --pgn data/lichess/2025-06.pgn.zst
python rating_bands/label_bands.py --bands data/lichess/bands/2025-06   # ~4 h
python rating_bands/find_curves.py --labels data/lichess/bands/2025-06/labels
```

| step | what it does |
| --- | --- |
| `download_month.py` | fetches a Lichess month over 8 connections (Lichess throttles each one) |
| `collect_games.py` | keeps rapid/classical games where both players are in one band: <1000, 1000-1300, 1300-1700, 1700-2000, 2000-2300, 2300+ |
| `label_bands.py` | per position: the best move, whether the player found it, how deep the engine needed, whether it's an only move, and what kind of move it is (quiet, retreat, sacrifice, ...) |
| `find_curves.py` | find-rate by band against engine depth and move type, with the random-move floor, on only-move positions |

A band at the random-move floor for some kind of move simply doesn't find it; a band above
the floor finds it some of the time. Next step: a model of find-probability by rating that gives
each move a *discovery rating*, the lowest rating that finds it.

Maia-2 (a rating-conditioned human-move model, `pip install maia2 --no-deps`) only resolves
ratings 1100-2000 and gave nearly flat curves on engine-hard positions, so it's a secondary
signal here, not the definition of the strata. Load it with
`maia2.model.from_pretrained("rapid", save_root=str(paths.MAIA2))`.
