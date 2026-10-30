# PGN model evaluations

Evaluations of the two character-level PGN models (the Transcendence paper's setup, trained on Modal): [Arisp/chess-pgn-1000-1300](https://huggingface.co/Arisp/chess-pgn-1000-1300) and [Arisp/chess-pgn-2400plus](https://huggingface.co/Arisp/chess-pgn-2400plus). The same tables are in their model cards (copies in [model_cards/](model_cards/)). Raw results are the `*.json` files here; `level_ratings.json` is the Stockfish-level calibration.

```bash
export STOCKFISH=tools/fairy-stockfish-largeboard_x86-64.exe   # Lichess levels 1-3 need negative skill levels
python transcend/pgn/calibrate_levels.py                            # rate the levels against Maia-2
python transcend/pgn/eval.py games   --model Arisp/chess-pgn-2400plus --level-ratings results/transcend/eval/level_ratings.json
python transcend/pgn/eval.py rerate  --model Arisp/chess-pgn-1000-1300 --level-ratings results/transcend/eval/level_ratings.json
python transcend/pgn/eval.py puzzles --model Arisp/chess-pgn-2400plus --strata-dir strata-pgn
```

## chess-pgn-1000-1300

All evaluations sample moves at temperature T, as in Transcendence: every legal move is scored by the product of its characters' tempered probabilities and one is drawn, renormalised over the legal moves (so illegal moves are never played; "illegal mass" is how much probability the model put on strings that are not a legal move). Code: `chess_beyond/transcend/pgn/eval.py` in [AriSpiesberger/Memorize](https://github.com/AriSpiesberger/Memorize).

#### Games against Stockfish

The model played Lichess's AI levels (Lichess's skill, depth and move time per level, on Fairy-Stockfish 14 LB) from 50 openings taken from held-out games, each with both colours: 100 games per level and temperature. Score = (wins + draws / 2) / games.

**Ratings.** Transcendence rated its Stockfish levels at 1552 / 1842 / 2142, but those numbers are for a different Stockfish setup and do not fit these levels. Each level was therefore rated here against Maia-2 (rapid) set to 1100, 1300, 1500, 1700, 1900, 2100 (50 openings x 2 colours per pair; `transcend/pgn/calibrate_levels.py`):

| level | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| rating vs Maia-2 (95% CI) | 614 (481-721) | 634 (509-737) | 1279 (1240-1319) | 1808 (1770-1846) | 2050 (2007-2093) | >= 2523 |

The model's rating is a Glicko-2 fit over the calibrated levels it played (1, 3 and 5), on Maia-2's scale, which follows Lichess rapid ratings of the humans it imitates (95%: R +/- 2 RD). Levels 7 and 8 are stronger than any Maia-2 setting and are reported as scores only. The "paper scale" column uses Transcendence's 1552 / 1842 / 2142 instead, for comparison with the paper only.

| T | L1 | L3 | L5 | L7 | L8 | **rating** | paper scale | illegal mass |
|---|---|---|---|---|---|---|---|---|
| 0.001 | 0.95 | 0.72 | 0.11 | 0.02 | 0.00 | **1477 +/- 74** | 2056 +/- 57 | 1.5% |
| 1 | 0.93 | 0.36 | 0.05 | 0.01 | 0.00 | **1120 +/- 74** | 1849 +/- 57 | 3.8% |

Caveat: the calibrated levels do not agree perfectly (for one model the L3 and L5 scores alone imply ratings a few hundred points apart), most likely because Maia-2's strongest settings are closer in strength than their labels; comparisons across temperatures and between the two models are solid, the absolute numbers less so.

#### Puzzles

The first 2000 puzzles of each set: a pool rated 900-1200 (the 1050 column) and three strata rated 2400, 2600 and 2800 (within 100 points); all with rating deviation <= 90, >= 200 plays and >= 2 solver moves, and with every puzzle whose source game is in either model's training data excluded. The model is given the game that led to each puzzle (fetched from Lichess), must play every solver move (opponent replies given; a different mating move also counts), and gets a puzzle rating from the Lichess puzzle formula.

| T | 1050 solved | 2400 solved | 2600 solved | 2800 solved | puzzle rating |
|---|---|---|---|---|---|
| 0.001 | 52.8% (50.7-55.0) | 7.7% (6.6-9.0) | 4.7% (3.8-5.7) | 2.8% (2.2-3.6) | 1210 (1194-1227) |
| 0.005 | 52.9% (50.8-55.1) | 7.8% (6.7-9.0) | 4.8% (3.9-5.8) | 2.9% (2.2-3.7) | 1213 (1196-1229) |
| 0.01 | 52.9% (50.7-55.1) | 7.6% (6.6-8.9) | 4.8% (3.9-5.8) | 2.7% (2.1-3.5) | 1210 (1194-1227) |
| 0.05 | 52.9% (50.8-55.1) | 7.5% (6.4-8.7) | 5.1% (4.2-6.2) | 2.6% (2.0-3.4) | 1212 (1195-1229) |
| 0.1 | 52.1% (49.9-54.3) | 7.9% (6.8-9.2) | 5.1% (4.2-6.2) | 2.8% (2.1-3.6) | 1209 (1193-1226) |
| 0.25 | 50.9% (48.8-53.1) | 7.6% (6.6-8.9) | 5.0% (4.1-6.0) | 2.5% (1.9-3.2) | 1194 (1177-1210) |
| 0.5 | 46.2% (44.0-48.4) | 7.5% (6.5-8.8) | 4.6% (3.8-5.6) | 2.8% (2.1-3.6) | 1155 (1139-1171) |
| 1 | 31.4% (29.5-33.5) | 4.5% (3.7-5.5) | 2.9% (2.3-3.7) | 1.5% (1.1-2.1) | 1001 (985-1017) |
| 1.5 | 20.8% (19.1-22.6) | 3.9% (3.1-4.8) | 2.5% (1.9-3.3) | 1.2% (0.8-1.8) | 903 (885-920) |

The puzzle rating is fitted over all four sets together and is driven mostly by the ~1050 pool, where most solves are; read the per-set rates for the hard strata. Puzzle ratings are on Lichess's puzzle scale, not its game scale.



## chess-pgn-2400plus

All evaluations sample moves at temperature T, as in Transcendence: every legal move is scored by the product of its characters' tempered probabilities and one is drawn, renormalised over the legal moves (so illegal moves are never played; "illegal mass" is how much probability the model put on strings that are not a legal move). Code: `chess_beyond/transcend/pgn/eval.py` in [AriSpiesberger/Memorize](https://github.com/AriSpiesberger/Memorize).

#### Games against Stockfish

The model played Lichess's AI levels (Lichess's skill, depth and move time per level, on Fairy-Stockfish 14 LB) from 50 openings taken from held-out games, each with both colours: 100 games per level and temperature. Score = (wins + draws / 2) / games.

**Ratings.** Transcendence rated its Stockfish levels at 1552 / 1842 / 2142, but those numbers are for a different Stockfish setup and do not fit these levels. Each level was therefore rated here against Maia-2 (rapid) set to 1100, 1300, 1500, 1700, 1900, 2100 (50 openings x 2 colours per pair; `transcend/pgn/calibrate_levels.py`):

| level | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| rating vs Maia-2 (95% CI) | 614 (481-721) | 634 (509-737) | 1279 (1240-1319) | 1808 (1770-1846) | 2050 (2007-2093) | >= 2523 |

The model's rating is a Glicko-2 fit over the calibrated levels it played (1, 3 and 5), on Maia-2's scale, which follows Lichess rapid ratings of the humans it imitates (95%: R +/- 2 RD). Levels 7 and 8 are stronger than any Maia-2 setting and are reported as scores only. The "paper scale" column uses Transcendence's 1552 / 1842 / 2142 instead, for comparison with the paper only.

| T | L1 | L3 | L5 | L7 | L8 | **rating** | paper scale | illegal mass |
|---|---|---|---|---|---|---|---|---|
| 0.001 | 0.97 | 0.81 | 0.47 | 0.05 | 0.01 | **1850 +/- 74** | 2272 +/- 57 | 2.1% |
| 0.005 | 0.96 | 0.74 | 0.36 | 0.04 | 0.01 | **1695 +/- 74** | 2182 +/- 57 | 1.8% |
| 0.01 | 0.99 | 0.78 | 0.38 | 0.03 | 0.00 | **1766 +/- 74** | 2223 +/- 57 | 2.0% |
| 0.05 | 0.97 | 0.80 | 0.47 | 0.04 | 0.02 | **1842 +/- 74** | 2267 +/- 57 | 2.3% |
| 0.1 | 0.97 | 0.83 | 0.46 | 0.03 | 0.01 | **1858 +/- 74** | 2276 +/- 57 | 2.1% |
| 0.25 | 0.96 | 0.84 | 0.45 | 0.03 | 0.01 | **1846 +/- 74** | 2269 +/- 57 | 2.2% |
| 0.5 | 0.98 | 0.79 | 0.39 | 0.04 | 0.00 | **1770 +/- 74** | 2226 +/- 57 | 2.5% |
| 1 | 0.98 | 0.45 | 0.07 | 0.01 | 0.00 | **1250 +/- 74** | 1925 +/- 57 | 4.6% |
| 1.5 | 0.89 | 0.14 | 0.03 | 0.01 | 0.01 | **902 +/- 74** | 1723 +/- 57 | 8.4% |

Caveat: the calibrated levels do not agree perfectly (for one model the L3 and L5 scores alone imply ratings a few hundred points apart), most likely because Maia-2's strongest settings are closer in strength than their labels; comparisons across temperatures and between the two models are solid, the absolute numbers less so.

#### Puzzles

The first 2000 puzzles of each set: a pool rated 900-1200 (the 1050 column) and three strata rated 2400, 2600 and 2800 (within 100 points); all with rating deviation <= 90, >= 200 plays and >= 2 solver moves, and with every puzzle whose source game is in either model's training data excluded. The model is given the game that led to each puzzle (fetched from Lichess), must play every solver move (opponent replies given; a different mating move also counts), and gets a puzzle rating from the Lichess puzzle formula.

| T | 1050 solved | 2400 solved | 2600 solved | 2800 solved | puzzle rating |
|---|---|---|---|---|---|
| 0.001 | 43.4% (41.2-45.5) | 10.5% (9.3-12.0) | 8.0% (6.9-9.3) | 3.9% (3.1-4.8) | 1192 (1176-1209) |
| 0.005 | 43.4% (41.2-45.5) | 10.4% (9.1-11.8) | 8.0% (6.9-9.3) | 3.9% (3.1-4.8) | 1191 (1174-1207) |
| 0.01 | 43.2% (41.0-45.4) | 10.4% (9.2-11.9) | 7.8% (6.8-9.1) | 3.9% (3.1-4.8) | 1189 (1173-1205) |
| 0.05 | 43.3% (41.1-45.5) | 10.8% (9.5-12.2) | 8.0% (6.8-9.2) | 4.0% (3.3-5.0) | 1195 (1178-1211) |
| 0.1 | 42.8% (40.6-45.0) | 9.8% (8.6-11.2) | 7.8% (6.8-9.1) | 3.6% (2.9-4.6) | 1179 (1163-1195) |
| 0.25 | 40.8% (38.7-43.0) | 10.9% (9.6-12.3) | 7.7% (6.6-9.0) | 3.6% (2.9-4.5) | 1170 (1154-1186) |
| 0.5 | 37.5% (35.4-39.6) | 9.5% (8.3-10.9) | 6.2% (5.2-7.3) | 3.5% (2.8-4.5) | 1122 (1107-1138) |
| 1 | 27.4% (25.5-29.4) | 6.4% (5.4-7.6) | 5.0% (4.1-6.0) | 3.5% (2.7-4.3) | 1015 (999-1031) |
| 1.5 | 17.6% (16.0-19.4) | 4.0% (3.2-4.9) | 3.2% (2.5-4.1) | 1.5% (1.0-2.1) | 883 (866-901) |

The puzzle rating is fitted over all four sets together and is driven mostly by the ~1050 pool, where most solves are; read the per-set rates for the hard strata. Puzzle ratings are on Lichess's puzzle scale, not its game scale.


