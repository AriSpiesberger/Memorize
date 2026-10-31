# transcend/board

**Imitate 1100-level players, then RL on easy puzzles only. Does the model solve 2400-rated puzzles its teachers
can't?** A policy/value network on encoded boards.

| model | puzzle Elo (95% CI) | game Elo vs Maia-2 (95% CI) | 1100 puzzles solved | 2400 puzzles solved |
| --- | --- | --- | --: | --: |
| imitation, all games | 1159 (1135-1184) | 1198 (1171-1224) | 37.7% | 6.91% |
| imitation, filtered games | 1140 (1116-1164) | 1163 (1137-1189) | 37.3% | 6.58% |
| + RL on 900-1200 puzzles | 1434 (1410-1459) | **765 (723-805)** | 72.2% | 6.1% |

RL on easy puzzles nearly doubles the easy solve rate, barely moves the 2400 rate (an 1100 human solves ~0.07%, random
legal moves ~0.23%), and costs about 400 Elo in real games. Details:
[results/transcend/summary.md](../../results/transcend/summary.md).

## Run

```bash
# games: 400k games with both players rated 1000-1300, 3+ minutes, cleaned (../clean)
python rating_bands/download_month.py --month 2025-06
python rating_bands/collect_games.py --month 2025-06 --pgn data/lichess/2025-06.pgn.zst \
    --bands 1000,1300 --min-base 180 --per-band 400000 --tag train
python transcend/clean/maia_filter.py --pgn data/lichess/bands/2025-06-train/1000-1300.pgn
# test puzzles (and the RL pool, never overlapping them)
python rating_bands/puzzle_strata.py --centers 1100,2400,2600,2800 --width 100 --max-deviation 90 --min-plays 200
# imitation, RL, evaluation
python transcend/board/make_data.py --pgn data/lichess/bands/2025-06-train/1000-1300.maia-clean.pgn
python transcend/board/train.py
python transcend/board/rl_puzzles.py --init runs/transcend/imitation.pt
python transcend/board/eval_puzzles.py --ckpt runs/transcend/rl.pt --strata all --n 2000 --elo
python transcend/board/play_elo.py --ckpt runs/transcend/imitation.pt runs/transcend/rl.pt
python transcend/board/pass_at_k.py --ckpt runs/transcend/imitation.pt runs/transcend/rl.pt
python transcend/board/plot_results.py           # -> results/transcend/summary.md and figures
```

| script | what it does |
| --- | --- |
| `make_data.py` | every position as (board, move played, result); positions from test puzzles removed |
| `train.py` | imitation; held-out loss, top-1 and puzzle Elo at every eval; early stopping |
| `rl_puzzles.py` | RL rewarded only for solving 900-1200 puzzles (GRPO-style) |
| `eval_puzzles.py` | solve rates per stratum with 95% intervals; `--elo` fits a puzzle rating |
| `play_elo.py` | games against Maia-2 at fixed ratings, fitted to a game Elo (also plays PGN models) |
| `pass_at_k.py` | pass@k per stratum: does RL teach new solutions or sharpen old ones? |
| `plot_results.py` | figures and `results/transcend/summary.md` from every run's log (no options: it just runs) |
| `puzzles.py` | puzzle strata and solving, shared with `../pgn/eval.py` |

Test sets (`data/lichess/puzzles/strata/`): 20,000 puzzles each at 1100 (control), 2400 and 2600, and 7,156 at 2800,
each with a multi-move solution and a rating from hundreds of attempts. None of their source games is in the training
data.

**Activation probe.** At every eval, `train.py` and `rl_puzzles.py` snapshot the vector the network decides from for a
fixed set of positions ([../../probe.py](../../probe.py)): an SVD plot coloured by complexity, sharpness and source,
and a cross-validated probe R^2 for each. `python probe.py build --pgn <band pgn>` makes the set; runs skip this until
it exists.
