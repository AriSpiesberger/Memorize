# transcend/pgn

**The Transcendence paper's model (Zhang et al., 2024): a character-level transformer (16 layers,
d=512, 51M parameters) on raw PGN movetext, never shown the board.** One per rating band,
trained on Modal on 10M games each:
[Arisp/chess-pgn-1000-1300](https://huggingface.co/Arisp/chess-pgn-1000-1300) and
[Arisp/chess-pgn-2400plus](https://huggingface.co/Arisp/chess-pgn-2400plus).

| model | game rating, T = 0.001 | game rating, T = 1 | puzzles solved T = 0.001: ~1050 / 2400 / 2800 | puzzle rating, T = 0.001 |
| --- | --: | --: | --: | --: |
| chess-pgn-1000-1300 | **1477 +/- 74** | 1120 +/- 74 | 52.8% / 7.7% / 2.8% | 1210 (1194-1227) |
| chess-pgn-2400plus | **1850 +/- 74** | 1250 +/- 74 | 43.4% / 10.5% / 3.9% | 1192 (1176-1209) |

Game ratings come from games against Lichess's Stockfish levels, each level rated against Maia-2,
so they are on the same human scale as the board model. At T = 1 the 1000-1300 model plays at its
data's level; near-greedy it plays ~350 above, the paper's transcendence result. The 2400+ model
gains as much from low temperature but stays far below its data. Every temperature, level and
puzzle set: [results/transcend/eval/](../../results/transcend/eval/README.md).

## Run

Training runs on Modal ([modal/README.md](../../modal/README.md)); the same scripts run at home:

```bash
python transcend/pgn/make_pgn_data.py --pgn data/lichess/bands/2025-06-train/1000-1300.pgn --out data/transcend/pgn-all
python transcend/pgn/train_pgn.py --data data/transcend/pgn-all --out runs/transcend/pgn-all.pt
# evaluation (Lichess levels 1-3 need Fairy-Stockfish for negative skill levels)
export STOCKFISH=tools/fairy-stockfish-largeboard_x86-64.exe
python transcend/pgn/calibrate_levels.py                        # rate the levels against Maia-2
python transcend/pgn/eval.py games   --model Arisp/chess-pgn-2400plus --level-ratings results/transcend/eval/level_ratings.json
python transcend/pgn/eval.py puzzles --model Arisp/chess-pgn-2400plus --strata-dir strata-pgn
```

| script | what it does |
| --- | --- |
| `pgn_model.py` | the model and its character vocabulary and prompt format |
| `make_pgn_data.py` | band PGN files -> one character array (`tokens.bin`, `starts.npy`), plus `info.npz` (ratings, terminations) |
| `train_pgn.py` | the paper's recipe (AdamW, cosine schedule), resumable |
| `pgn_probe.py` | activation snapshots of a fixed position set, the PGN-model version of `../../probe.py` |
| `rl_pgn_games.py` | offline RL on database games, rewarded only by who won, with a KL penalty to the starting model (Modal: `modal_train.py::rl_games`) |
| `eval.py` | a PGN model at several temperatures: `games` vs Lichess's Stockfish levels, `positions`, `puzzles`, `rerate` |
| `calibrate_levels.py` | rates each Lichess level against Maia-2 at known ratings |

All but `eval.py` and `calibrate_levels.py` are shared with Modal: editing one changes Modal runs too.
