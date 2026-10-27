# chess_beyond

**Can a model trained on human games find the moves those humans miss?**

Three experiments share this folder:

| | question | status |
| --- | --- | --- |
| [transcend/](transcend/) | Imitate 1100-level players, then RL on easy puzzles only. Does it solve 2400-rated puzzles its teachers can't? | imitation + RL done, [results](results/transcend/summary.md) |
| [rating_bands/](rating_bands/) | Which moves does each rating band *never* find (ability), as opposed to finding them less often (consistency)? | stratified sets built (games and puzzles) |
| [filter_experiment/](filter_experiment/) | Remove the excellent moves humans found in hard positions from the training data. Can imitation, RL or search still find them? | runs end to end; needs far more data |

## Headline so far (transcend)

| model | puzzle Elo (95% CI) | game Elo vs Maia-2 (95% CI) | 1100 puzzles solved | 2400 puzzles solved |
| --- | --- | --- | --: | --: |
| imitation of 1100-level games (all) | 1159 (1135-1184) | 1198 (1171-1224) | 37.7% | 6.91% |
| imitation of 1100-level games (filtered) | 1140 (1116-1164) | 1163 (1137-1189) | 37.3% | 6.58% |
| + RL on 900-1200 puzzles | 1434 (1410-1459) at step 2250 | **765 (723-805)** at step 4750 | 72.2% | 6.1% |

An 1100-rated human is expected to solve ~0.07% of the 2400 stratum, and random legal moves
~0.23%. RL on easy puzzles lifts easy-puzzle play a lot but barely moves the 2400 rate, and it
makes the model a much weaker player in real games (about 400 Elo down against Maia-2).
Details, intervals and figures: [results/transcend/summary.md](results/transcend/summary.md).

### The Transcendence paper's model (character-level PGN, 51M parameters)

Trained on Modal on 10M games per band, never shown the board:
[Arisp/chess-pgn-1000-1300](https://huggingface.co/Arisp/chess-pgn-1000-1300) and
[Arisp/chess-pgn-2400plus](https://huggingface.co/Arisp/chess-pgn-2400plus). Game ratings come from
games against Lichess's Stockfish AI levels, each level rated against Maia-2 (so on the same human
scale as the board models above); puzzle ratings are on Lichess's puzzle scale.

| model | game rating, T = 0.001 | game rating, T = 1 | puzzles solved T = 0.001: ~1050 / 2400 / 2800 | puzzle rating, T = 0.001 |
| --- | --: | --: | --: | --: |
| chess-pgn-1000-1300 | **1477 +/- 74** | 1120 +/- 74 | 52.8% / 7.7% / 2.8% | 1210 (1194-1227) |
| chess-pgn-2400plus | **1850 +/- 74** | 1250 +/- 74 | 43.4% / 10.5% / 3.9% | 1192 (1176-1209) |

The 1000-1300 model plays at its data's level when sampled at T = 1 and about 350 points above it
near-greedy, the paper's transcendence result (~1500 there). The 2400+ model gains as much from low
temperature but stays far below its data's level. Every temperature, level and puzzle set, with
intervals and caveats: [results/transcend/eval/](results/transcend/eval/README.md).

## Layout

```
chess_beyond/
├── paths.py              where data, runs, models and Stockfish live
├── common.py             board encoding, move vocabulary, the policy/value network
├── search.py             PUCT tree search using only the network (no engine)
├── intervals.py          Wilson confidence intervals for the rates reported (home GPU)
├── lichess_ids.py        Lichess game ids from Site headers and puzzle URLs (shared with Modal)
├── probe.py              activation snapshots: where the network puts fixed positions before it decides
├── modal/                the cloud side: Modal apps that build data and train (see modal/README.md)
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

## Where code runs

Three kinds of code share this folder. Keeping them apart keeps the labs separate:

| kind | where it lives | runs on |
| --- | --- | --- |
| **Modal only** | [modal/](modal/) | Modal containers (cloud); needs the `modal` CLI |
| **Shared** | `paths.py`, `common.py`, `probe.py`, `lichess_ids.py`, `rating_bands/collect_games.py`, `rating_bands/puzzle_strata.py`, `transcend/make_pgn_data.py`, `transcend/pgn_model.py`, `transcend/pgn_probe.py`, `transcend/train_pgn.py` | a home GPU or Modal, unchanged. Modal calls these scripts, so editing one changes both |
| **Home GPU** | everything else: `search.py`, `intervals.py`, `transcend/` (`train.py`, `rl_puzzles.py`, `eval_puzzles.py`, `play_elo.py`, `pass_at_k.py`, `maia*.py`, ...), `rating_bands/` (`discover.py`, `hard_puzzles.py`, ...), `filter_experiment/` | your own machine (CUDA); not wired to Modal |

Rule of thumb: put logic in the shared or experiment folders, and keep `modal/` to
container setup, Volumes and calls. Details and commands: [modal/README.md](modal/README.md).

## Running on Modal

Modal builds the upsampled games database and trains the PGN model in the cloud, with the
same scripts you would run at home. Run these from this folder; full details are in
[modal/README.md](modal/README.md).

```bash
export MODAL_PROFILE=arispiesberger
modal run modal/modal_app.py::smoke                   # one month, 20,000 games per band
modal run --detach modal/modal_app.py::build_games    # 40 months, newest first, then merge
modal run --detach modal/modal_train.py::prepare      # SFT data, puzzle strata, probe set
```

The merged bands land in `data/lichess/bands/upsampled/1000-1300.pgn` and `2400+.pgn` on the
`chess-data` Volume, which is mounted where `paths.py` looks (`data/`).

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
python transcend/pass_at_k.py --ckpt runs/transcend/imitation.pt runs/transcend/rl.pt
# the paper's character-level PGN model, for comparison
python transcend/make_pgn_data.py --pgn data/lichess/bands/2025-06-train/1000-1300.pgn --out data/transcend/pgn-all
python transcend/train_pgn.py --data data/transcend/pgn-all --out runs/transcend/pgn-all.pt
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
| `play_elo.py` | whole games against Maia-2 at fixed ratings, fitted to a game Elo; also plays the PGN model at any temperature |
| `pass_at_k.py` | pass@k by stratum per checkpoint: does RL teach new solutions, or only sharpen ones the starting model already had? |
| `make_pgn_data.py`, `pgn_model.py`, `train_pgn.py` | the Transcendence paper's setup: a character-level transformer (16 layers, d=512) trained on raw PGN movetext, never shown the board |
| `plot_results.py` | figures and `results/transcend/summary.md` from every run's log |
| `eval.py` | PGN models (a local `.pt` or a Hugging Face repo) at several temperatures: `games` vs Lichess's Stockfish AI levels, `positions` (top-k and win % lost on held-out positions), `puzzles` (with each puzzle's game history), `rerate` (a finished games run with other level ratings) |
| `sae.py` | a TopK sparse autoencoder on a PGN model's states just before it moves (any layer), and each latent's top-activating positions from held-out games or a game corpus (`results/transcend/sae/`, plus an HTML page with boards) |
| `crosscoder.py` | a BatchTopK crosscoder between the two PGN models (1000-1300 and 2400+) on the same random positions from games of every rating, many per game: which latents are shared and which belong to one model (relative decoder norms), each latent's top positions with both models' moves, and a layer sweep (`results/transcend/crosscoder/`) |
| `explain.py` | a scored, plain-chess explanation for every crosscoder latent: the fact from `predicates.py` (or two joined by "and") that best predicts when it fires, scored on held-out games ([below](#interpretability-concepts-and-the-paths-between-them)) |
| `concepts.py` | concept paths: each PGN model plays itself, every position is encoded with the crosscoder, and path i -> j is "latent j turns on within a few plies after latent i", beyond what sibling rollouts show; graphs of the paths only one model takes and the ones both take, example rollouts for each path, and an SVD summary ([below](#interpretability-concepts-and-the-paths-between-them)) |
| `predicates.py`, `skill.py`, `pages.py` | helpers: the facts explanations are written in, board facts (hanging pieces, pins, forks, what the move does) and skill facts from Stockfish and Maia-2 (only move, deep move, sound sacrifice, blunder, rare for 1100s); and the boards and cards of the HTML pages |
| `calibrate_levels.py` | rates each Lichess AI level against Maia-2 at known ratings, for `eval.py --level-ratings` (needs Fairy-Stockfish for levels 1-3) |

Test sets (`data/lichess/puzzles/strata/`): 20,000 puzzles each at 1100 (control), 2400 and 2600,
and 7,156 at 2800, each with a multi-move solution and a rating measured from hundreds of
attempts. None of their source games is in the training games.

## Interpretability: concepts and the paths between them

What do the two PGN models (1000-1300 and 2400+) represent, and how do their ideas follow from
one another? The thesis: the latents are tangible chess concepts, and while the models share
nearly all of them, some **paths** between concepts are taken by only one model.

```bash
# 1. a crosscoder between the two models: one dictionary of latents read from both (~3M positions)
python transcend/crosscoder.py collect --positions 3000000 --per-game 4 --layers 8 12 15 final --run runs/transcend/crosscoder/everything-3m
python transcend/crosscoder.py train   --run runs/transcend/crosscoder/everything-3m --layers final
python transcend/crosscoder.py top     --run runs/transcend/crosscoder/everything-3m --cc Lfinal
# 2. an explanation for every latent, scored on held-out games
#    (board facts + Stockfish on every CPU core, ~30-40 min for 100k positions; then Maia-2 and the crosscoder on the GPU)
python transcend/explain.py --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal
# 3. self-play rollouts: which latents turn on after which, with each model playing
python transcend/concepts.py rollout --cc-run runs/transcend/crosscoder/everything-3m --cc Lfinal
# 4. the path graphs, example rollouts for every path, then Stockfish on every move of those rollouts
#    (examples and score each redraw the graph with what they add)
python transcend/concepts.py graph    --run runs/transcend/concepts/everything-3m-Lfinal
python transcend/concepts.py examples --run runs/transcend/concepts/everything-3m-Lfinal
python transcend/concepts.py score    --run runs/transcend/concepts/everything-3m-Lfinal
# optional: the same paths summarised as SVD "flow modes"
python transcend/concepts.py modes    --run runs/transcend/concepts/everything-3m-Lfinal
```

| step | what it measures | look at |
| --- | --- | --- |
| crosscoder | which latents each model uses (relative decoder norm: 0 = only the 1000-1300 model, 1 = only 2400+) | `results/transcend/crosscoder/everything-3m/cc-Lfinal/report.md` |
| explain | each latent's explanation, one or two facts, with its held-out precision, recall and F1 next to what an unrelated fact scores (*explained* = F1 >= 0.5). Board facts (`predicates.py`): hanging pieces, pins, forks, checks, passed pawns, what the move does. Skill facts (`skill.py`, Stockfish and Maia-2): only one good move, a best move found only at depth, a sound sacrifice, meeting a threat, a blunder, a move 1100s rarely play but 2000+ players do | `.../cc-Lfinal/explain.md` (including how many explanations need a skill fact, by which model uses the latent), `explanations.jsonl` |
| rollout | per model, how often latent j turns on within 4 plies of latent i, against sibling rollouts from the same start (so the start position itself explains nothing) | `runs/.../concepts/everything-3m-Lfinal/<model>/` (counts) |
| graph | three graphs: paths taken only by the 1000-1300 model (significant with it, absent with the other), only by 2400+, and by both; every latent on them comes up with both models | `runs/.../graph.html`, `results/transcend/concepts/everything-3m-Lfinal/summary.md` |
| examples | for each path, rollouts where it happens: the position where i turns on, the one where j does, the moves between, and which facts changed | hover an arrow in `graph.html` |
| score | Stockfish on every move of those rollouts: does the path gain or lose win chances for the side that takes it, how much each side's moves lose, and what kind of move starts and ends it (only move, deep, sacrifice, rare for 1100s, ...) | edge cards in `graph.html`; the per-graph table in `summary.md` |

In `graph.html`, hover a node for its explanation and top positions (boards), hover an arrow for
the path's example rollouts; click to pin a card. `summary.md` lists the strongest paths and how
many of their latents have explanations.

## Activation probe

At every eval, `train.py` and `rl_puzzles.py` save the vector the network decides from (CLS after
the final LayerNorm) for a fixed set of positions, plot the positions on SVD components 1 and 2,
coloured by complexity (legal moves), sharpness (Stockfish win% of the best move minus the second
best) and source (puzzle stratum or game), and log a cross-validated linear-probe R^2 for each.
Build the probe set once; until it exists the runs skip this.

```bash
python probe.py build --pgn data/lichess/bands/2025-06-train/1000-1300.pgn      # -> data/probe.jsonl (~2,600 positions)
python transcend/train.py ...                                # -> runs/transcend/imitation_probe/step<N>.png/.npz, log.jsonl
python probe.py snapshot --ckpt runs/transcend/rl_step4000.pt                     # any saved checkpoint, after the fact
python probe.py series --dir runs/transcend/imitation_probe --color sharpness --basis last
```

`--basis own` gives each step its own SVD; `first`/`last` project every step onto one step's
axes, so movement between checkpoints shows as drift.

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
