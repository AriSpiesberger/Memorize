# transcend

**Imitate 1100-level players, then RL on easy puzzles only. Does the model solve 2400-rated
puzzles its teachers can't?**

Commands, the full script table and setup are in the
[chess_beyond README](../README.md#experiment-transcend); headline numbers, intervals and figures
are in [results/transcend/summary.md](../results/transcend/summary.md).

| step | script |
| --- | --- |
| clean the training games | `filter_cheaters.py`, `maia_filter.py` |
| build imitation data | `make_data.py` |
| imitation | `train.py` |
| RL on 900-1200 puzzles | `rl_puzzles.py` |
| evaluate | `eval_puzzles.py` (puzzles), `play_elo.py` (games vs Maia-2), `pass_at_k.py` |
| the Transcendence paper's character-level PGN model | `make_pgn_data.py`, `pgn_model.py`, `train_pgn.py` |
| sparse autoencoder on the PGN model, with max-activating positions | `sae.py` (`collect`, `train`, `top`, or `all`) |
| crosscoder between the two PGN models (shared vs model-only latents), layer sweep | `crosscoder.py` (`collect`, `train`, `top`, or `all`) |
| a scored chess explanation for every crosscoder latent | `explain.py` (board facts from `predicates.py`, skill facts from `skill.py`: Stockfish and Maia-2) |
| concept paths from self-play rollouts: which latents turn on after which, the paths only one model takes, example rollouts per path, Stockfish on those rollouts | `concepts.py` (`rollout`, `graph`, `examples`, `score`, `modes`); page helpers in `pages.py` |
| evaluate the PGN models (games, positions, puzzles, by temperature) | `eval.py`, with level ratings from `calibrate_levels.py`; results in [../results/transcend/eval/](../results/transcend/eval/README.md) |
| figures and summary | `plot_results.py` |

The interpretability pipeline (crosscoder, explanations, concept paths), its commands and what
each step writes: [chess_beyond README](../README.md#interpretability-concepts-and-the-paths-between-them).

`puzzles.py` and `maia.py` are shared helpers. `train.py` and `rl_puzzles.py` also save
activation snapshots at every eval ([../probe.py](../probe.py)).
