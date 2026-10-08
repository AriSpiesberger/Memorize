# chess_beyond

**Can a model trained on human games find the moves those humans miss?**

Three experiments share this folder:

| | question | status |
| --- | --- | --- |
| [transcend/](transcend/) | Imitate 1100-level players, then RL on easy puzzles only. Does it solve 2400-rated puzzles its teachers can't? | imitation + RL done, [results](results/transcend/summary.md) |
| [rating_bands/](rating_bands/) | Which moves does each rating band *never* find (ability), as opposed to finding them less often (consistency)? | stratified sets built (games and puzzles) |
| [filter_experiment/](filter_experiment/) | Remove the excellent moves humans found in hard positions from the training data. Can imitation, RL or search still find them? | runs end to end; needs far more data |

## Headline so far (transcend)

| model | puzzle Elo (95% CI) | 1100 puzzles solved | 2400 puzzles solved |
| --- | --- | --: | --: |
| imitation of 1100-level games (filtered) | 1140 (1116-1164) | 37.3% | 6.58% |
| + RL on 900-1200 puzzles (step 2250) | 1434 (1410-1459) | 72.2% | 6.1% |

An 1100-rated human is expected to solve ~0.07% of the 2400 stratum, and random legal moves
~0.23%. RL on easy puzzles lifts easy-puzzle play a lot but barely moves the 2400 rate.
Details, intervals and figures: [results/transcend/summary.md](results/transcend/summary.md).

## Layout

```
chess_beyond/
├── paths.py              where data, runs, models and Stockfish live
├── common.py             board encoding, move vocabulary, the policy/value network
├── search.py             PUCT tree search using only the network (no engine)
├── transcend/            experiment: imitate 1100s, RL on easy puzzles, test on hard ones
├── rating_bands/         experiment: which moves each rating finds; builds the puzzle strata
├── filter_experiment/    experiment: remove excellent moves from training, try to recover them
├── results/   figures and summaries worth keeping                  (tracked)
├── data/      lichess/ downloads, bands, puzzles; transcend/ shards (gitignored)
├── runs/      checkpoints and logs                                 (gitignored)
├── models/    maia2/ weights (downloaded by the maia2 package)     (gitignored)
└── tools/     stockfish/ binary                                    (gitignored)
```

Run every command from this folder (`chess_beyond/`) with the repo's venv.

## Setup

```bash
pip install chess zstandard matplotlib            # torch comes from the repo's requirements.txt
pip install maia2 --no-deps einops gdown pandas pyyaml "pyzstd<0.20"   # Maia-2, keeping your torch
```

Put a Stockfish build in `tools/stockfish/` ([download](https://stockfishchess.org/download/)),
or point `$STOCKFISH` at one. `paths.stockfish()` finds it either way. Maia-2 weights download
into `models/maia2/` on first use.

## Experiment: transcend

```bash
# games: 400k games with both players rated 1000-1300, 3+ minutes
python rating_bands/download_month.py --month 2025-06
python rating_bands/collect_games.py --month 2025-06 --pgn data/lichess/2025-06.pgn.zst \
    --bands 1000,1300 --min-base 180 --per-band 400000 --tag train
# drop games where a player plays far above or below their rating (engine help, sandbagging);
# the account lookup is optional and only checks that the Maia filter catches marked cheaters
python transcend/filter_cheaters.py --pgn data/lichess/bands/2025-06-train/1000-1300.pgn
python transcend/maia_filter.py     --pgn data/lichess/bands/2025-06-train/1000-1300.pgn
# puzzles: test strata (and the RL pool, built automatically, never overlapping them)
python rating_bands/puzzle_strata.py --centers 1100,2400,2600,2800 --width 100 --max-deviation 90 --min-plays 200
# imitation, RL, evaluation
python transcend/make_data.py --pgn data/lichess/bands/2025-06-train/1000-1300.maia-clean.pgn
python transcend/train.py
python transcend/rl_puzzles.py --init runs/transcend/imitation.pt
python transcend/eval_puzzles.py --ckpt runs/transcend/rl.pt --strata all --n 2000 --elo
python transcend/play_elo.py --ckpt runs/transcend/imitation.pt runs/transcend/rl.pt
python transcend/plot_results.py
```

| script | what it does |
| --- | --- |
| `filter_cheaters.py` | looks every player up with Lichess's public API; can drop games with accounts marked for cheating (`<pgn>.clean.pgn`), and `maia_filter.py` uses the lookups to report how many marked cheaters it catches |
| `maia_filter.py` | scores each player's moves with Maia-2 at 2000+ and <1100 and drops games where someone plays far above or below their rating (`<pgn>.maia-clean.pgn`, the data for the filtered runs) |
| `make_data.py` | every position of every game as (board, move played, game result); positions from any test puzzle are removed |
| `train.py` | imitation of the move played; held-out loss, top-1 and a puzzle Elo at every eval; early stopping |
| `rl_puzzles.py` | RL rewarded only for solving 900-1200 rated puzzles (GRPO-style), monitoring the control and test strata |
| `eval_puzzles.py` | solve rates per stratum with 95% intervals, `--elo` for a fitted puzzle rating, `--list` for which puzzles were solved |
| `play_elo.py` | whole games against Maia-2 at fixed ratings, fitted to a game Elo |
| `plot_results.py` | figures and `results/transcend/summary.md` from every run's log |

Test sets (`data/lichess/puzzles/strata/`): 20,000 puzzles each at 1100 (control), 2400 and 2600,
and 7,156 at 2800, each with a multi-move solution and a rating measured from hundreds of
attempts. None of their source games is in the training games.

## Experiment: rating_bands

```bash
python rating_bands/collect_games.py --month 2025-06 --pgn data/lichess/2025-06.pgn.zst \
    --min-base 300 --max-base 300 --tag blitz                       # 5-minute games per band
python rating_bands/label_bands.py --bands data/lichess/bands/2025-06-blitz        # ~3 h
python rating_bands/discover.py --labels data/lichess/bands/2025-06-blitz/labels --maia-type blitz --target idea3
python rating_bands/show_sequences.py --labels data/lichess/bands/2025-06-blitz/labels
python rating_bands/puzzle_strata.py
```

| script | what it does |
| --- | --- |
| `download_month.py` | fetches a Lichess month over 8 connections (Lichess throttles each one), resumable |
| `collect_games.py` | keeps games where both players are in one band: <1000, 1000-1300, 1300-1700, 1700-2000, 2000-2300, 2300+ |
| `label_bands.py` | per position: best move, whether the player found it, engine depth needed, only-move or not, move type, and whether they followed the idea through the next two moves (`idea2`, `idea3`) |
| `find_curves.py` | find-rate by band against engine depth and move type, with the random-move floor |
| `discover.py` | a cross-fitted model of P(find) by rating gives every position a *discovery rating*; writes the stratified set `strata_<target>.jsonl` with validation tables |
| `show_sequences.py` | prints the hardest sequences strong players found, in readable moves with Lichess links |
| `hard_puzzles.py` | checks hard Lichess puzzles with Maia-2 playing the whole solution at each rating |
| `puzzle_strata.py` | narrow, well-measured puzzle-rating strata 400 points apart, with the expected solve-rate matrix |

What it found: in 5-minute games the bands separate sharply, and requiring the player to
follow the idea through (not just find the first move) removes most accidental finds; low-rated
players convert hard finds about half as often as easy ones, 2300+ players about 80% as often.
Maia-2 only resolves 1100-2000 and is nearly flat across ratings on hard positions, so the strata
come from real games and measured puzzle ratings, not from Maia.

## Experiment: filter_experiment

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
*learn* the moves when told, not whether it *discovers* them.
