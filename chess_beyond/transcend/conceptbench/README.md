# transcend/conceptbench

**Does a model represent known chess concepts?** A reusable evaluation after Schut et al.'s static-concept validation:
label positions from games no model trained on, pair each positive with a matched negative, fit a sparse concept vector
per concept on one split of games, and score it on the other. Any model that reads the PGN format can be scored.

## Run

```bash
python transcend/conceptbench/build_positions.py --fresh data/lichess/2026-09.head.pgn.zst   # positions.parquet
python -m unittest discover -s transcend/conceptbench/tests                                  # the labellers on hand-chosen FENs
python transcend/conceptbench/label_positions.py                                             # labels, counts table
python transcend/conceptbench/render_samples.py --family structures --html results/transcend/conceptbench/spotcheck.html
python transcend/conceptbench/build_dataset.py                                               # concepts/<name>.parquet, manifest.json
python transcend/conceptbench/score.py --family pieces,openings                              # the check first
python transcend/conceptbench/score.py --family structures,imbalances,plans
python transcend/conceptbench/score.py --models MyModel=runs/my.pt --layers 11,final         # any other model
python transcend/conceptbench/score.py --models cc4096,cc4096-s1 --layers 11                 # over crosscoder latents
python transcend/conceptbench/score.py --models cc4096-Wview,cc4096-Sview --layers 4,8,11,15,final   # each model alone in its space
python transcend/conceptbench/traj.py build && python transcend/conceptbench/traj.py acts     # the dynamic bench: every ply
python transcend/conceptbench/traj.py score && python transcend/conceptbench/traj.py report && python transcend/conceptbench/traj.py paired
```

Over a crosscoder, a position's features are its latents: W's and S's cached states at the crosscoder's layer, scaled as in
training and encoded together at the inference threshold (one score for the pair, needs both models' activations cached).
The LP and everything after it is unchanged: it fits a sparse direction over all the latents, not one latent.

The fresh month is the first 1.5 GB of the file (4.5M games): `curl --range 0-1484746751 -o data/lichess/2026-09.head.pgn.zst
https://database.lichess.org/standard/lichess_db_standard_rated_2026-09.pgn.zst`. The openings list goes in
`data/transcend/conceptbench/openings/{a,b,c,d,e}.tsv`, from github.com/lichess-org/chess-openings.

| script | what it does |
| --- | --- |
| `bench.py` | paths, game phase, material, the split, prompts and boards (no torch: the labelling workers import it) |
| `build_positions.py` | held-out games plus a fresh month, at most 10 positions per game, split 80 / 20 by game |
| `labels/` | one module per concept family: `pieces`, `openings`, `structures`, `imbalances`, `plans`, and `stockfish_terms` (off by default) |
| `tests/` | each labeller on hand-chosen positions, present and absent |
| `label_positions.py` | every labeller over every position; the counts table; drops concepts under 300 positives in fit |
| `render_samples.py` | 20 random positives and negatives per concept, as text or an HTML page, for a human spot-check |
| `build_dataset.py` | positives paired with nearest negatives; `manifest.json` |
| `score.py` | activations (cached), the LP, the test scores, the controls, `report.md` |
| `labels/plan_book.py` | 45 book plans over whole games (a structure and the moves that carry it out), as episodes, for the dynamic bench |
| `traj.py` | the dynamic bench: every ply of the bench's games labelled as episodes; per concept and readout the one unit (raw neuron, crosscoder latent, board feature) that tracks it best, scored on test games against labels shifted round each game; `paired`: S against W on the same games. [report](../../results/transcend/conceptbench/traj/report.md), [paired](../../results/transcend/conceptbench/traj/paired.md) |

The book plans whose latent comes on before the plan are drawn on the concept map as good examples: `transcend/interp/known_plans.py`.

## Choices the brief left open

- **Where positions come from.** `data/pgn_probe/population.jsonl` (held-out games of both bands, the 1000-1300s and the
  2400+s) and 2026-09, after every model's training months. In the fresh month: rated, both players 1800+, base time at
  least 10 minutes. A game reaching a rare structure (`structures.RARE`) gives its positions from plies in one; other
  games give 2 at random. Selection never looks at what the game does next, so plans are not selected on their outcome.
- **Structures, either colour or book colour.** Generic ones hold for either colour; the named defences (King's Indian,
  French Advance, Caro-Kann/Slav, Benoni) only in their book colours. Each rule's docstring is its definition.
- **"Small centre"** is a term with more than one use. Here: e4 against d6, with no White d-pawn and no Black e-pawn.
- **Plans are marked by their first move**, which can be read off a game without judging intent: b4 of the minority
  attack, d4-d5, ...f5 or ...g5, ...b5 or ...d5.
- **Matching also fixes side to move**, and ply breaks ties, beyond the phase and material asked for: the prompt ends
  differently per side.
- **Counts are labelled both ways.** "Exactly k" is what the brief's list suggests, but a middle value isn't monotone in the
  count, so one direction can't express it. `pieces.py` adds "at least k", which can be. They were added after the first
  run with `build_dataset.py --only`, so every other concept kept its pairs and scores.
- **The board control runs for every concept**, not only plans: it says how much of a static label a linear read of the
  board already gets.
- **`SLACK` = 100 and 2000 pairs.** Picked on a partial position set (5 concepts, W and random-init), then frozen: at a
  price of 1 the LP returns v = 0, at 10 it underfits, and from 100 test accuracy is flat. This looked at test pairs of the
  partial set for one hyperparameter, a small leak. 4000 pairs scores up to 0.02-0.03 better on hard concepts but took
  ~600 s a job here (with 5 shuffles, on a shared machine), ~22 hours for the first run: use `--pairs 4000` for a final one.
- **Shuffled labels** run once per cell, for time (`SHUFFLES`). For a strong concept one random direction can land far from
  0.5 either way, since test pairs share a large mean difference: read the mean over a family, which should be 0.5.

`stockfish_terms.py` needs a Stockfish 8-11 binary, which is not in `tools/`: its table parser is unit-tested on a sample
written by hand, not on a real engine's output.
