# Latent explanations

100000 positions, split by game into a fit half (choose each latent's explanation) and a test half (score it). An explanation is a board fact (predicates.py) or skill fact (skill.py), or two joined by "and"; its score is the F1 of predicting when the latent fires, on the test half. **explained**: F1 >= 0.5; **weak**: >= 0.3. Latents firing fewer than 20 times in either half are too rare to score.

- 16384 latents, 10598 scored: 50 explained (0%), 120 weak, 10428 unexplained; 5786 too rare.

## By which model uses the latent

relative decoder norm r: ~0 the first model only, ~0.5 both, ~1 the second model only.

**uses a skill fact**: of the explained and weak latents, how many explanations include a skill fact (only move, deep move, sacrifice, threat, blunder, Maia-2 rarity, ...) rather than board facts alone.

| r | scored | explained | weak | median F1 | uses a skill fact |
| --- | --- | --- | --- | --- | --- |
| < 0.4 | 878 | 0% | 2% | 0.04 | 5% |
| 0.4-0.6 | 7480 | 1% | 1% | 0.02 | 38% |
| >= 0.6 | 2240 | 0% | 1% | 0.02 | 24% |

## Most common explanations (explained latents)

- 15 latents: the best move is quiet (no capture, check or promotion)
- 5 latents: the move is the engine's best (or within 2 win-% points of it)
- 3 latents: the middlegame
- 2 latents: an endgame (6 or fewer pieces besides kings and pawns)
- 2 latents: White is to move
- 1 latents: the move is a rook move and the move is a capture
- 1 latents: one of their pieces is attacked by a cheaper piece of ours and the move is a pawn move
- 1 latents: an endgame (6 or fewer pieces besides kings and pawns) and the side to move is up material (2+ pawns' worth)
- 1 latents: the queens are off and their last move gave check
- 1 latents: the queens are off and we still have castling rights
- 1 latents: we still have castling rights and their king is boxed in on the back rank and we have a rook or queen
- 1 latents: the move is a queen move and the move takes an attacked piece of ours to safety
- 1 latents: the queens are off
- 1 latents: the move is a king move and the move is a capture
- 1 latents: the side to move is winning (win chance 75%+)
- 1 latents: the move is a bishop move and the move takes an attacked piece of ours to safety
- 1 latents: the move is a rook move and the move takes an attacked piece of ours to safety
- 1 latents: we still have castling rights
- 1 latents: we have a checking move
- 1 latents: the side to move is in check and 3+ squares around our king are attacked by them

## The 40 best-explained latents

| latent | r | explanation | precision | recall | F1 | null F1 |
| --- | --- | --- | --- | --- | --- | --- |
| 11273 | 0.49 | White is to move | 0.71 | 0.87 | 0.79 | 0.46 |
| 10386 | 0.49 | we still have castling rights | 0.85 | 0.63 | 0.73 | 0.35 |
| 3406 | 0.72 | the side to move is winning (win chance 75%+) | 0.84 | 0.63 | 0.72 | 0.27 |
| 1469 | 0.49 | the move is a queen move and the move takes an attacked piece of ours to safety | 0.93 | 0.58 | 0.71 | 0.05 |
| 1260 | 0.57 | the queens are off and we still have castling rights | 0.61 | 0.78 | 0.68 | 0.01 |
| 2327 | 0.51 | the queens are off | 1.00 | 0.49 | 0.65 | 0.27 |
| 5626 | 0.40 | the move is a bishop move and the move takes an attacked piece of ours to safety | 0.74 | 0.57 | 0.65 | 0.03 |
| 14723 | 0.74 | the side to move is losing (win chance 25% or less) | 0.97 | 0.49 | 0.65 | 0.24 |
| 14293 | 0.48 | the middlegame and they still have castling rights | 0.67 | 0.61 | 0.64 | 0.10 |
| 16125 | 0.53 | the side to move is in check and we have a passed pawn on the 6th or 7th rank | 0.61 | 0.66 | 0.63 | 0.00 |
| 10419 | 0.50 | White is to move | 0.62 | 0.64 | 0.63 | 0.50 |
| 12506 | 0.39 | the move is a knight move and the move takes an attacked piece of ours to safety | 0.78 | 0.51 | 0.62 | 0.03 |
| 12371 | 0.51 | the middlegame | 0.59 | 0.64 | 0.62 | 0.49 |
| 14244 | 0.51 | the middlegame | 0.58 | 0.63 | 0.61 | 0.49 |
| 13121 | 0.50 | the best move is quiet (no capture, check or promotion) | 0.52 | 0.73 | 0.61 | 0.57 |
| 435 | 0.68 | an endgame (6 or fewer pieces besides kings and pawns) and the side to move is up material (2+ pawns' worth) | 0.52 | 0.72 | 0.61 | 0.06 |
| 1428 | 0.49 | we still have castling rights and their king is boxed in on the back rank and we have a rook or queen | 0.59 | 0.60 | 0.60 | 0.07 |
| 16305 | 0.51 | the best move is quiet (no capture, check or promotion) | 0.52 | 0.70 | 0.60 | 0.58 |
| 14567 | 0.50 | the best move is quiet (no capture, check or promotion) | 0.49 | 0.72 | 0.58 | 0.55 |
| 10712 | 0.53 | the best move is quiet (no capture, check or promotion) | 0.48 | 0.72 | 0.57 | 0.54 |
| 7157 | 0.50 | an endgame (6 or fewer pieces besides kings and pawns) | 0.82 | 0.43 | 0.57 | 0.30 |
| 10926 | 0.52 | we have a checking move | 0.57 | 0.56 | 0.57 | 0.48 |
| 13278 | 0.51 | the best move is quiet (no capture, check or promotion) | 0.46 | 0.73 | 0.57 | 0.53 |
| 326 | 0.43 | one of their pieces is attacked by a cheaper piece of ours and the move is a pawn move | 0.45 | 0.77 | 0.57 | 0.02 |
| 12343 | 0.51 | the best move is quiet (no capture, check or promotion) | 0.46 | 0.72 | 0.56 | 0.53 |
| 6691 | 0.50 | the best move is quiet (no capture, check or promotion) | 0.47 | 0.68 | 0.56 | 0.56 |
| 16185 | 0.52 | the move is a queen move and the move recaptures on the square they just captured on | 0.81 | 0.42 | 0.55 | 0.02 |
| 820 | 0.49 | the queens are off and their last move gave check | 0.54 | 0.57 | 0.55 | 0.02 |
| 4449 | 0.50 | the move is the engine's best (or within 2 win-% points of it) | 0.47 | 0.66 | 0.55 | 0.51 |
| 11697 | 0.50 | the move is the engine's best (or within 2 win-% points of it) | 0.46 | 0.68 | 0.55 | 0.49 |
| 9212 | 0.51 | the best move is quiet (no capture, check or promotion) | 0.45 | 0.69 | 0.55 | 0.54 |
| 16019 | 0.51 | the best move is quiet (no capture, check or promotion) | 0.46 | 0.66 | 0.54 | 0.56 |
| 7474 | 0.53 | the best move is quiet (no capture, check or promotion) | 0.44 | 0.72 | 0.54 | 0.52 |
| 2095 | 0.52 | the best move is quiet (no capture, check or promotion) | 0.44 | 0.70 | 0.54 | 0.53 |
| 16057 | 0.49 | the best move is quiet (no capture, check or promotion) | 0.46 | 0.65 | 0.54 | 0.56 |
| 13061 | 0.50 | the best move is quiet (no capture, check or promotion) | 0.45 | 0.68 | 0.54 | 0.54 |
| 12744 | 0.53 | the move is the engine's best (or within 2 win-% points of it) | 0.47 | 0.64 | 0.54 | 0.51 |
| 11364 | 0.57 | the side to move is in check and 3+ squares around our king are attacked by them | 0.45 | 0.66 | 0.53 | 0.02 |
| 15759 | 0.53 | the move is the engine's best (or within 2 win-% points of it) | 0.46 | 0.62 | 0.53 | 0.52 |
| 12838 | 0.50 | the best move is quiet (no capture, check or promotion) | 0.43 | 0.68 | 0.53 | 0.52 |
