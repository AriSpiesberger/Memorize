---
license: mit
library_name: pytorch
tags:
- chess
- pgn
- character-level
- transformer
---

# chess-pgn-2400plus

A 51M-parameter character-level transformer that plays chess by writing PGN movetext, trained only
on Lichess games where **both players were rated 2400+**. It follows the PGN model of
*Transcendence: Generative Models Can Outperform The Experts That Train Them* (Zhang et al., NeurIPS 2024):
it reads and writes games one character at a time (`;1.e4 e5 2.Nf3 ...`) and is never shown a board or the rules.

It is one of a pair trained with the same recipe on different rating bands:
[chess-pgn-1000-1300](https://huggingface.co/Arisp/chess-pgn-1000-1300) and
[chess-pgn-2400plus](https://huggingface.co/Arisp/chess-pgn-2400plus).

## Data

- Lichess standard rated games, March 2023 to June 2025 (28 months), newest first, both players rated 2400+, initial clock time of at least 180 seconds.
- **10,000,000 training games** (4.82B characters, 482 per game on average) and 5,000 held-out games (the newest).
- Draws are kept. Games that are the source of a Lichess puzzle in our evaluation sets are excluded (22 dropped).
- Format: one game per line of text, `;` + SAN movetext + result, e.g. `;1.e4 e5 2.Nf3 Nc6 ... 1-0`. Vocabulary of 33 characters.

## Model

Decoder-only transformer: 16 layers, d=512, 8 heads, ReLU MLPs, learned positions, context 1,024 characters (`config.json`).

## Training

- Next-character cross-entropy on 1,024-character windows that each start at a game's beginning; 128 windows (131,072 characters) per step.
- AdamW (betas 0.9/0.95, weight decay 0.1), learning rate 2e-4 after 2,000 warmup steps, cosine decay to 2e-5 over 200,000 steps, bf16, one NVIDIA B200.
- Held-out loss every 500 steps; early stopping after 16 evals without improvement, counted after the first epoch.
- This model: the full 200,000-step schedule (its held-out loss was still improving at the last eval), then three fine-tuning stages, each starting from the previous stage's best weights with a fresh optimizer and ended by early stopping: peak learning rate 5e-5 (best after 500 steps), 2e-5 (best after 1,000) and 1e-5 after a 20,000-step warmup (best after 18,500). **220,000 optimizer steps in all** on the path to this checkpoint (246,500 were run), about 6.0 passes over the training characters.

## Results

Held-out loss: **0.3622 bits per character** on the 5,000 held-out games.

Top move (greedy) equal to the move played, on 20,000 held-out positions (10,000 from each band's held-out games):

| | 1000-1300 games | 2400+ games |
|---|---|---|
| this model | 42.6% | 53.3% |
| mean surprise of the played move (nats) | 1.99 | 1.40 |

Illegal moves, on 3,000 held-out positions per band:

| | 1000-1300 games | 2400+ games |
|---|---|---|
| top move (greedy) | 0.87% | 0.30% |
| one sampled move, T = 1 | 2.03% | 1.03% |

## Evaluation

All evaluations sample moves at temperature T, as in Transcendence: every legal move is scored by the product of its characters' tempered probabilities and one is drawn, renormalised over the legal moves (so illegal moves are never played; "illegal mass" is how much probability the model put on strings that are not a legal move). Code: `chess_beyond/transcend/pgn/eval.py` in [AriSpiesberger/Memorize](https://github.com/AriSpiesberger/Memorize).

### Games against Stockfish

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

### Puzzles

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

See [chess-pgn-1000-1300](https://huggingface.co/Arisp/chess-pgn-1000-1300) for the other band.

## Usage

```python
import json, chess, torch
from huggingface_hub import snapshot_download
from safetensors.torch import load_file
import sys

path = snapshot_download("Arisp/chess-pgn-2400plus")
sys.path.insert(0, path)
from pgn_model import PGNTransformer, generate_moves

cfg = json.load(open(f"{path}/config.json"))["architecture"]
model = PGNTransformer(**cfg)
model.load_state_dict(load_file(f"{path}/model.safetensors"))
model.eval()

board = chess.Board()
board.push_san("e4")
move = generate_moves(model, [board], temperature=0.0, dev="cpu")[0]   # None if 5 attempts were illegal
print(board.san(move))
```

`generate_moves` writes characters until a space and parses them as SAN. At temperature 0 a retry repeats the
same characters, so for play, sample (temperature > 0) on retries.

## Limitations

- **Illegal moves.** The model only knows the position from the move history, and occasionally writes a move that is not legal.
- **Context of 1,024 characters.** Past roughly move 80-100 the start of the game no longer fits; the model then no longer
  knows the position and its move-match accuracy halves. Training never shows characters beyond a game's first 1,024.
- It imitates players of one rating band, blunders included; it is not an engine.
