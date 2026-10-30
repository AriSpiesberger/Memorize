# Latent explanations

100000 positions, split by game into a fit half (choose each latent's explanation) and a test half (score it). An explanation is a board fact, a square fact (predicates.py) or a skill fact (skill.py), or two joined by "and"; its score is the F1 of predicting when the latent fires, on the test half. **explained**: F1 >= 0.5; **weak**: >= 0.3. Latents firing fewer than 20 times in either half are too rare to score. Squares are named from the side to move's side of the board, as if it were White (rank 1 is our back rank).

- 16384 latents, 11035 scored: 1338 explained (12%), 1368 weak, 8329 unexplained; 5349 too rare.
- **engine-linked**: 470 latents fire where the side to move stands at least 5 win-% points better or worse, by Stockfish, than the pieces on the board predict (z >= 4, test half).

## What the layer knows

Linear probes (ridge, fit on the fit half, scored on the test half) to Stockfish's numbers for the position: its evaluation (win % for the side to move), the size of the threat against the side to move, and the only-move gap (how much worse the second-best move is); and as yes/no, AUC for "only one good move" (gap >= 15) and "decided" (win % < 20 or > 80). The first row is what the board and square facts alone allow; the model rows read the models' own states at this layer; the last rows add the firings of the latents most tied to the evaluation beyond the board (chosen on the fit half), by which model uses them.

| read from | eval R2 | threat R2 | gap R2 | only one good move AUC | decided AUC |
| --- | --- | --- | --- | --- | --- |
| the board and square facts alone | 0.680 | 0.397 | 0.169 | 0.797 | 0.887 |
| chess-pgn-1000-1300, layer 15 states | 0.649 | 0.425 | 0.206 | 0.802 | 0.870 |
| chess-pgn-2400plus, layer 15 states | 0.773 | 0.480 | 0.206 | 0.815 | 0.921 |
| board and square facts + the 600 engine-linked latents all of them | 0.788 | 0.462 | 0.222 | 0.807 | 0.916 |
| board and square facts + the 200 engine-linked latents used mostly by the first model (r < 0.4) | 0.692 | 0.406 | 0.182 | 0.799 | 0.892 |
| board and square facts + the 200 engine-linked latents used by both (0.4-0.6) | 0.711 | 0.427 | 0.208 | 0.801 | 0.895 |
| board and square facts + the 200 engine-linked latents used mostly by the second model (r > 0.6) | 0.777 | 0.444 | 0.200 | 0.807 | 0.911 |

## By which model uses the latent

relative decoder norm r: ~0 chess-pgn-1000-1300 only, ~0.5 both, ~1 chess-pgn-2400plus only.

**uses a skill fact**: of the explained and weak latents, how many explanations include a skill fact (only move, deep move, sacrifice, threat, blunder, Maia-2 rarity, ...). **square facts**: how many use a square fact. **engine-linked**: share of scored latents tied to the evaluation beyond the board.

| r | scored | explained | weak | median F1 | uses a skill fact | square facts | engine-linked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| < 0.4 | 758 | 4% | 11% | 0.13 | 1% | 94% | 7% |
| 0.4-0.6 | 8604 | 15% | 13% | 0.14 | 2% | 97% | 4% |
| >= 0.6 | 1673 | 1% | 10% | 0.11 | 4% | 90% | 7% |

## Most common explanations (explained latents)

- 5 latents: the move is the engine's best (or within 2 win-% points of it)
- 5 latents: the best move is quiet (no capture, check or promotion)
- 4 latents: their last move put a pawn on h6 and our bishop on g5
- 4 latents: White is to move
- 4 latents: their last move put a pawn on g5 and our bishop on h4
- 4 latents: our pawn on g2
- 3 latents: their queen on c4
- 3 latents: our pawn on e4 and their pawn on d5
- 3 latents: their last move put a queen on h4 and their last move gave check
- 3 latents: our rook on a1
- 3 latents: their last move put a queen on d1 and one of their pieces (knight or more) is attacked by us and undefended
- 3 latents: their last move put a bishop on d6 and our bishop on f4
- 2 latents: our pawn on f5
- 2 latents: our pawn on f6
- 2 latents: their last move put a pawn on d4 and our pawn on c3
- 2 latents: an endgame (6 or fewer pieces besides kings and pawns)
- 2 latents: their king on d4
- 2 latents: their last move put a knight on d2 and the move recaptures on the square they just captured on
- 2 latents: our pawn on d6
- 2 latents: their last move put a pawn on h5 and our pawn on g4

## The 40 best-explained latents

| latent | r | explanation | precision | recall | F1 | null F1 |
| --- | --- | --- | --- | --- | --- | --- |
| 6056 | 0.50 | our pawn on e2 | 1.00 | 0.95 | 0.98 | 0.06 |
| 14573 | 0.51 | our knight on b1 | 0.99 | 0.95 | 0.97 | 0.16 |
| 9421 | 0.52 | our knight on g1 | 0.99 | 0.95 | 0.97 | 0.09 |
| 15850 | 0.50 | our knight on d2 | 1.00 | 0.94 | 0.97 | 0.07 |
| 11179 | 0.50 | our pawn on c3 | 0.99 | 0.94 | 0.97 | 0.19 |
| 12942 | 0.52 | their knight on f6 | 0.97 | 0.96 | 0.97 | 0.25 |
| 14576 | 0.49 | our knight on c3 | 0.97 | 0.96 | 0.96 | 0.20 |
| 16006 | 0.49 | our knight on d4 | 1.00 | 0.93 | 0.96 | 0.02 |
| 9673 | 0.49 | our pawn on f3 | 1.00 | 0.93 | 0.96 | 0.09 |
| 5198 | 0.48 | our queen on e2 | 1.00 | 0.93 | 0.96 | 0.04 |
| 15087 | 0.53 | our pawn on d2 | 0.95 | 0.97 | 0.96 | 0.08 |
| 8557 | 0.44 | their last move put a knight on c5 | 0.96 | 0.95 | 0.96 | 0.00 |
| 13936 | 0.51 | our knight on e2 | 1.00 | 0.92 | 0.96 | 0.04 |
| 14472 | 0.49 | our pawn on d3 | 0.97 | 0.95 | 0.96 | 0.18 |
| 15740 | 0.48 | our pawn on b3 | 0.99 | 0.93 | 0.96 | 0.12 |
| 14082 | 0.52 | our bishop on d3 | 1.00 | 0.92 | 0.96 | 0.07 |
| 7884 | 0.45 | our pawn on h3 | 0.98 | 0.93 | 0.96 | 0.21 |
| 12492 | 0.51 | their last move put a pawn on h6 and our bishop on g5 | 1.00 | 0.92 | 0.96 | 0.00 |
| 4774 | 0.49 | our pawn on g3 | 0.98 | 0.94 | 0.96 | 0.17 |
| 5657 | 0.50 | our knight on e5 | 1.00 | 0.91 | 0.95 | 0.03 |
| 1216 | 0.41 | their last move put a bishop on g4 and our knight on f3 | 0.99 | 0.92 | 0.95 | 0.01 |
| 9640 | 0.51 | our knight on e4 | 1.00 | 0.91 | 0.95 | 0.02 |
| 1234 | 0.54 | their knight on c6 | 0.97 | 0.94 | 0.95 | 0.20 |
| 2528 | 0.50 | our queen on f3 | 1.00 | 0.91 | 0.95 | 0.03 |
| 2205 | 0.54 | their last move put a knight on c2 and the side to move is in check | 1.00 | 0.91 | 0.95 | 0.00 |
| 11597 | 0.48 | our queen on d2 | 1.00 | 0.91 | 0.95 | 0.04 |
| 6943 | 0.52 | our bishop on f4 | 1.00 | 0.90 | 0.95 | 0.05 |
| 10555 | 0.50 | our bishop on e3 | 1.00 | 0.90 | 0.95 | 0.06 |
| 8059 | 0.49 | their last move put a knight on b4 | 0.97 | 0.92 | 0.95 | 0.00 |
| 1733 | 0.47 | our queen on d3 | 1.00 | 0.90 | 0.95 | 0.02 |
| 12509 | 0.52 | their last move put a knight on g4 and their last move gave check | 1.00 | 0.90 | 0.95 | 0.00 |
| 15366 | 0.47 | our pawn on b4 | 0.98 | 0.91 | 0.94 | 0.09 |
| 13824 | 0.47 | our bishop on g2 and our knight on f3 | 1.00 | 0.89 | 0.94 | 0.02 |
| 8309 | 0.51 | our knight on d5 | 1.00 | 0.90 | 0.94 | 0.02 |
| 14592 | 0.50 | our bishop on d2 | 1.00 | 0.89 | 0.94 | 0.04 |
| 5904 | 0.47 | our pawn on a3 | 0.95 | 0.94 | 0.94 | 0.18 |
| 3125 | 0.49 | our knight on g5 | 1.00 | 0.89 | 0.94 | 0.02 |
| 12594 | 0.48 | our knight on b5 | 0.99 | 0.89 | 0.94 | 0.01 |
| 7413 | 0.50 | our knight on c4 | 0.99 | 0.89 | 0.94 | 0.01 |
| 9354 | 0.44 | their last move put a knight on f5 | 0.98 | 0.90 | 0.94 | 0.00 |

## The 40 most engine-linked latents

Win chance (Stockfish) for the side to move where the latent fires, and how far that is from what the pieces on the board predict; the same for the threat against the side to move; then the latent's best fact explanation.

| latent | r | win % when firing | beyond the board | threat beyond the board | explanation (F1) |
| --- | --- | --- | --- | --- | --- |
| 4796 | 0.35 | 15 | -27.1 | +0.3 | their last move put a queen on e1 (0.05) |
| 5350 | 0.51 | 16 | -27.1 | +0.1 | their last move put a rook on g4 (0.03) |
| 8468 | 0.45 | 87 | +25.4 | +25.6 | the move is checkmate and our knight on g5 (0.18) |
| 578 | 0.49 | 99 | -24.1 | -2.0 | the move promotes a pawn (0.14) |
| 1133 | 0.44 | 20 | -24.1 | +0.8 | their last move put a queen on g3 (0.02) |
| 15415 | 0.55 | 23 | -22.8 | +1.7 | our king on b3 (0.04) |
| 13744 | 0.49 | 98 | -22.6 | -4.9 | our queen on e8 (0.02) |
| 12078 | 0.60 | 13 | -22.5 | -8.3 | our king on b5 (0.00) |
| 763 | 0.47 | 72 | +22.3 | +26.1 | their last move put a king on h7 (0.01) |
| 13084 | 0.25 | 92 | +21.8 | +18.7 | we have mate in one and our knight on g5 (0.17) |
| 15762 | 0.57 | 1 | +20.7 | +7.7 | our king on h3 and the side to move is in check (0.03) |
| 9879 | 0.42 | 91 | +20.6 | +16.5 | our knight on h8 (0.00) |
| 997 | 0.52 | 45 | -20.3 | -8.4 | our knight on h6 (0.03) |
| 1003 | 0.57 | 95 | +20.1 | +14.8 | our queen on h7 (0.04) |
| 9207 | 0.53 | 77 | +19.7 | +10.5 | their last move put a pawn on f6 (0.02) |
| 9585 | 0.45 | 61 | +19.6 | +20.3 | their last move put a knight on h7 (0.04) |
| 5069 | 0.61 | 26 | -19.6 | -1.0 | their queen on h3 (0.13) |
| 5312 | 0.59 | 66 | +19.5 | +19.9 | their last move put a queen on f7 (0.00) |
| 11478 | 0.54 | 86 | +19.4 | +5.7 | our king on g6 (0.05) |
| 8062 | 0.54 | 99 | -19.2 | -4.8 | we have mate in one (0.13) |
| 3677 | 0.55 | 37 | -19.1 | -0.8 | their last move put a queen on h3 (0.09) |
| 10597 | 0.61 | 31 | -18.8 | -0.4 | their last move put a queen on h4 and they threaten mate in one (0.17) |
| 4433 | 0.54 | 97 | -18.8 | -8.5 | their last move put a king on a8 (0.09) |
| 2407 | 0.49 | 96 | -18.7 | -7.0 | our queen on a8 (0.10) |
| 14830 | 0.52 | 43 | -18.7 | -4.7 | their last move put a knight on h4 (0.05) |
| 1614 | 0.22 | 68 | +18.7 | +12.9 | their last move put a rook on g6 (0.00) |
| 13243 | 0.56 | 84 | +18.4 | +4.4 | the move is checkmate (0.03) |
| 7199 | 0.54 | 2 | +18.3 | -4.6 | their queen on b1 (0.05) |
| 12237 | 0.52 | 17 | -18.3 | -3.4 | their last move put a queen on g3 (0.43) |
| 15196 | 0.50 | 41 | +18.0 | -4.8 | their last move put a queen on f3 and the side to move is in check (0.07) |
| 3707 | 0.58 | 70 | +18.0 | +23.0 | their last move put a queen on g4 (0.03) |
| 4976 | 0.56 | 92 | +17.9 | +11.3 | their last move put a queen on g5 and one of their pieces is attacked by a cheaper piece of ours (0.10) |
| 14838 | 0.44 | 92 | +17.9 | +17.3 | we have mate in one and our queen on f3 (0.17) |
| 9540 | 0.42 | 47 | +17.9 | -7.6 | their last move put a queen on d2 and the side to move is in check (0.18) |
| 14546 | 0.47 | 95 | -17.9 | -6.1 | their last move put a king on a7 (0.00) |
| 965 | 0.55 | 43 | -17.8 | -4.6 | their last move put a rook on d8 and one of our pieces is attacked by a cheaper piece (0.09) |
| 1404 | 0.51 | 69 | +17.8 | +6.5 | their last move put a king on g6 (0.12) |
| 2364 | 0.46 | 76 | +17.7 | +6.1 | our queen on h5 and we have mate in one (0.09) |
| 9582 | 0.64 | 70 | +17.5 | +25.1 | their last move put a queen on g7 (0.00) |
| 5160 | 0.55 | 86 | +17.3 | +5.7 | their last move put a rook on c1 and the move recaptures on the square they just captured on (0.08) |
