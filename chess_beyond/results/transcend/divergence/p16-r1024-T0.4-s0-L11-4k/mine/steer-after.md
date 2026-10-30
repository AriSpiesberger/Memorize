# Steering mined concepts after the split, strength by norm

h -> h + r ||h|| u_hat at the prompt end, r = 0.1, 0.25, 0.5; every condition (+v, -v, 20 random v's of matching firing rate) pushes equally hard. Points: the chosen line at the plies of each branch pair's window where the concept is on; target the line's next move. Decision rule as steer_concepts.py: self-check at r = 0.25 (+v above every random v, -v below zero, Benjamini-Hochberg q < 0.05); transfer at any r (Bonferroni over 3), above the random 95th.

Self-check passes: 1 of 10. Positive control (shared, cos >= 0.7, self-check passed): 0 of 0 transfer (nan%; the rule needs >= 70%).

Verdicts: fails self-check 9, shared but no transfer 1

| concept | theme | shared cos | points (positions) | verdict | self +v / -v / random median / max (q), r = 0.25 | +v over r | -v over r | readback of +v over r (g) | KL +v / -v / random | transfer: other +v / random 95th @r (q) | held-out points: +v self / other |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S141 | repeats a move | 0.128 | 25 (3) | shared but no transfer | +0.05 / -0.15 / -0.02 / +0.03 (0.05) | +0.03 +0.05 +0.01 | -0.04 -0.15 -0.35 | +0.38 +0.97 +1.99 (0.67) | 0.04 / 0.06 / 0.11 | W -0.02 / +0.02 @0.1 (1.00) | 33: +0.05 / -0.06 |
| S8 | two or more rook moves | 0.963 | 61 (9) | fails self-check | -0.03 / -0.17 / -0.03 / +0.00 (0.61) | -0.01 -0.03 -0.13 | -0.02 -0.17 -0.53 | +1.16 +2.90 +5.79 (1.06) | 0.02 / 0.09 / 0.02 | W -0.10 / -0.06 @0.5 (1.00) | 17: -0.05 / -0.01 |
| W29 | two or more rook moves | 0.963 | 53 (5) | fails self-check | +0.01 / -0.05 / -0.04 / +0.00 (0.24) | -0.01 +0.01 -0.02 | -0.00 -0.05 -0.11 | +1.01 +2.54 +5.09 (1.34) | 0.03 / 0.06 / 0.03 | S -0.11 / -0.03 @0.5 (1.00) | 14: -0.05 / -0.05 |
| S14 | two or more captures | 0.915 | 61 (8) | fails self-check | -0.39 / -0.00 / -0.08 / +0.00 (1.00) | -0.11 -0.39 -0.74 | +0.01 -0.00 -0.06 | +1.05 +2.66 +5.36 (1.24) | 0.22 / 0.03 / 0.10 | W -0.07 / -0.01 @0.25 (1.00) | 27: -0.48 / -0.07 |
| W25 | king move | 0.915 | 41 (10) | fails self-check | -0.06 / -0.02 / +0.02 / +0.06 (1.00) | +0.04 -0.06 -0.40 | +0.04 -0.02 -0.15 | +0.80 +2.08 +4.18 (1.48) | 0.09 / 0.04 / 0.03 | S -0.04 / +0.01 @0.1 (1.00) | 33: -0.19 / -0.55 |
| S29 | two or more pawn moves | 0.895 | 64 (4) | fails self-check | -0.05 / -0.17 / -0.07 / -0.01 (0.61) | -0.01 -0.05 -0.18 | -0.03 -0.17 -0.82 | +0.09 +0.22 +0.45 (1.10) | 0.07 / 0.14 / 0.02 | W -0.11 / -0.04 @0.5 (1.00) | 34: -0.05 / +0.02 |
| W138 | no capture or check | 0.895 | 21 (3) | fails self-check | -0.01 / -0.09 / -0.05 / +0.02 (0.61) | -0.00 -0.01 -0.02 | -0.02 -0.09 -0.30 | +0.12 +0.31 +0.62 (1.35) | 0.02 / 0.08 / 0.03 | S -0.22 / +0.06 @0.5 (1.00) | 14: +0.06 / +0.08 |
| W197 | two or more pawn moves | 0.665 | 12 (3) | fails self-check | -0.04 / -0.09 / -0.04 / -0.00 (0.61) | +0.00 -0.04 -0.19 | -0.02 -0.09 -0.31 | +1.08 +2.71 +5.43 (1.44) | 0.02 / 0.02 / 0.03 | S -0.36 / -0.06 @0.5 (1.00) | 17: -0.07 / -0.02 |
| W30 | two or more pawn moves | 0.074 | 25 (3) | fails self-check | -0.07 / -0.01 / -0.06 / -0.02 (0.65) | -0.02 -0.07 -0.21 | +0.01 -0.01 -0.18 | +0.46 +1.14 +2.29 (0.42) | 0.02 / 0.07 / 0.02 | S -0.05 / -0.00 @0.5 (1.00) | 28: -0.07 / -0.09 |
| S58 |  | 0.049 | 23 (4) | fails self-check | -0.08 / -0.16 / -0.06 / -0.00 (0.67) | -0.02 -0.08 -0.34 | -0.02 -0.16 -0.70 | +0.14 +0.34 +0.69 (1.45) | 0.07 / 0.16 / 0.05 | W -0.12 / -0.04 @0.5 (1.00) | 17: -0.44 / -0.13 |

By ply of the window (own model, +v at r = 0.25; step 0 = the state after the split move):

| concept | step 0 | step 1 | step 2 | step 3 | step 4 | step 5 | step 6 | step 7 | step 8 |
|---|---|---|---|---|---|---|---|---|---|
| S8 | -0.07 | +0.01 | -0.00 | -0.13 | -0.03 | +0.03 | -0.05 | -0.11 | +0.04 |
| S14 | -0.96 | -0.15 | -0.22 | -0.14 | -0.49 | -0.47 | -0.55 | -0.00 | -0.31 |
| S29 | +0.09 | +0.06 | -0.37 | -0.08 | -0.03 | -0.10 | +0.02 | -0.00 | -0.06 |
| S58 | -0.56 | -0.02 | +0.09 | +0.02 | +0.05 | -0.06 | +0.08 | – | – |
| S141 | -0.12 | +0.14 | -0.02 | +0.06 | +0.19 | +0.10 | +0.04 | +0.07 | +0.00 |
| W25 | -0.11 | +0.12 | -0.19 | -0.20 | -0.08 | +0.01 | +0.16 | – | – |
| W29 | -0.04 | +0.11 | +0.03 | -0.09 | +0.03 | -0.03 | -0.02 | +0.01 | +0.03 |
| W30 | -0.06 | -0.15 | +0.02 | -0.09 | -0.12 | -0.05 | -0.07 | -0.05 | -0.05 |
| W138 | -0.11 | +0.10 | +0.05 | +0.05 | +0.01 | -0.05 | -0.10 | -0.00 | -0.09 |
| W197 | -0.01 | -0.04 | -0.01 | -0.06 | -0.11 | – | – | – | – |

Readback: the concept's activity (sum_j w_j z_j / mu_j) after the push, median over points, beside its natural chosen-minus-subpar gap g. KL over all legal moves at the primary strength.

