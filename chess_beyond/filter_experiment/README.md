# filter_experiment

**Remove the excellent moves humans found in hard positions from the training data. Can
imitation, RL or search still find them?** Status: runs end to end; needs far more data.

```bash
python filter_experiment/build_dataset.py --pgn data/lichess/2015-01.pgn.zst \
    --out data/filter/positions.jsonl --games 10000 --workers 30     # Stockfish labels, ~2.5 h
python filter_experiment/make_splits.py --positions data/filter/positions.jsonl --test-frac 0.3
python filter_experiment/run_experiment.py                         # imitation x3, RL x3, evaluate -> runs/filter/
```

| script | what it does |
| --- | --- |
| `build_dataset.py` | positions from 1100-1600 games; Stockfish's best moves and the depth it needed to find them (`depth_to_find`) |
| `make_splits.py` | easy / buffer / hard bands, split by game; training sets `full`, `filtered` (human best moves in hard positions removed) and `random` (as many removed at random) |
| `train_sft.py` | imitation of the human move; early-stops on held-out games |
| `rl_finetune.py` | RL from `filtered`, rewarded by a deep engine, a shallow engine, or a coin flip |
| `evaluate.py` | best-move rate on held-out hard and easy positions, with and without search |
| `run_experiment.py` | the last three in order, resumable |

The RL reward comes from Stockfish, so it measures whether the model can *learn* the moves when
told, not whether it *discovers* them.
