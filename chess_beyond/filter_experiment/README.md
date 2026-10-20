# filter_experiment

**Remove the excellent moves humans found in hard positions from the training data. Can
imitation, RL or search still find them?**

Commands and details are in the
[chess_beyond README](../README.md#experiment-filter_experiment). Status: runs end to end; needs
far more data.

| step | script |
| --- | --- |
| Stockfish-labelled positions from 1100-1600 games | `build_dataset.py` |
| easy / buffer / hard bands; `full`, `filtered` and `random` training sets | `make_splits.py` |
| imitation (one arm) | `train_sft.py` |
| RL from `filtered` (deep engine, shallow engine, or coin-flip reward) | `rl_finetune.py` |
| best-move rate on held-out hard and easy positions | `evaluate.py` |
| all of the above after the splits, resumable | `run_experiment.py` |

The RL reward comes from Stockfish, so it measures whether the model can *learn* the moves when
told, not whether it *discovers* them.
