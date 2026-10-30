# Look-ahead at L11

Per concept, its expression at a branching point (before the move) against the logit of the share of rollouts playing the move after which the concept is highest (nodes with >= 20 rollouts, >= 2 moves, the children's expressions spreading by >= 0.5). Gain: out-of-fold R^2 of board + expression minus board alone (5 folds by position), 95% bootstrap over positions. Null: 20 random directions of matching firing rate, each run end to end. Partial: the correlation of the expression and the share once the board is read out of both.

| concept | theme | rollouts | nodes (positions) | R^2 board | gain [95% CI] | null median / 95th | partial r | null partial median / 95th | above null 95th |
|---|---|---|---|---|---|---|---|---|---|
| S8 | two or more rook moves | own (S) | 716 (46) | 0.002 | +0.0019 [-0.0063, +0.0091] | -0.0039 / +0.0052 | +0.06 | +0.01 / +0.14 | no |
| S8 | two or more rook moves | other (W) | 567 (42) | -0.000 | -0.0032 [-0.0088, +0.0001] | -0.0051 / +0.0207 | +0.02 | -0.01 / +0.19 | no |
| S14 | two or more captures | own (S) | 500 (46) | -0.005 | -0.0019 [-0.0155, +0.0088] | -0.0040 / +0.0042 | -0.04 | -0.01 / +0.16 | no |
| S14 | two or more captures | other (W) | 488 (45) | -0.007 | -0.0034 [-0.0077, +0.0008] | -0.0177 / +0.0378 | +0.02 | -0.00 / +0.17 | no |
| S29 | two or more pawn moves | own (S) | 138 (23) | -0.011 | -0.0227 [-0.0812, +0.0212] | -0.0023 / +0.0068 | -0.12 | +0.01 / +0.12 | no |
| S29 | two or more pawn moves | other (W) | 169 (21) | -0.012 | +0.0077 [-0.0374, +0.0433] | -0.0012 / +0.0257 | -0.12 | +0.01 / +0.12 | no |
| S58 |  | own (S) | 127 (26) | -0.026 | -0.0812 [-0.1156, -0.0381] | -0.0006 / +0.0086 | -0.01 | +0.00 / +0.15 | no |
| S58 |  | other (W) | 122 (23) | -0.047 | -0.0141 [-0.0620, +0.0283] | -0.0035 / +0.0180 | +0.08 | +0.01 / +0.25 | no |
| S141 | repeats a move | own (S) | 129 (30) | 0.010 | +0.0523 [-0.1526, +0.2347] | -0.0067 / +0.0258 | +0.31 | -0.00 / +0.12 | no |
| S141 | repeats a move | other (W) | 101 (32) | -0.062 | -0.0216 [-0.1470, +0.0250] | -0.0015 / +0.0398 | -0.07 | -0.01 / +0.16 | no |
| W25 | king move | own (W) | 445 (44) | -0.011 | -0.0108 [-0.0227, -0.0020] | -0.0067 / +0.0026 | -0.04 | +0.02 / +0.09 | no |
| W25 | king move | other (S) | 470 (45) | 0.000 | -0.0015 [-0.0049, +0.0013] | -0.0033 / +0.0109 | +0.02 | +0.01 / +0.09 | no |
| W29 | two or more rook moves | own (W) | 556 (42) | -0.002 | -0.0016 [-0.0061, +0.0029] | -0.0149 / +0.0078 | +0.04 | +0.02 / +0.12 | no |
| W29 | two or more rook moves | other (S) | 708 (46) | -0.004 | -0.0006 [-0.0091, +0.0068] | -0.0054 / +0.0178 | +0.06 | -0.03 / +0.26 | no |
| W30 | two or more pawn moves | own (W) | 68 (10) | -0.055 | -0.0428 [-0.1878, +0.0217] | -0.0035 / +0.0194 | -0.11 | -0.01 / +0.19 | no |
| W30 | two or more pawn moves | other (S) | 103 (11) | 0.017 | -0.0731 [-0.2868, +0.0947] | -0.0023 / +0.0182 | -0.06 | +0.03 / +0.18 | no |
| W138 | no capture or check | own (W) | 186 (27) | -0.008 | +0.0159 [-0.0251, +0.0512] | -0.0083 / +0.0136 | -0.15 | -0.02 / +0.08 | no |
| W138 | no capture or check | other (S) | 141 (29) | -0.098 | -0.0772 [-0.1446, -0.0337] | -0.0044 / +0.0121 | -0.08 | -0.01 / +0.15 | no |
| W197 | two or more pawn moves | own (W) | 283 (43) | -0.012 | +0.0096 [-0.0138, +0.0299] | -0.0054 / +0.0031 | +0.12 | +0.02 / +0.10 | no |
| W197 | two or more pawn moves | other (S) | 322 (42) | -0.020 | -0.0051 [-0.0189, +0.0071] | -0.0068 / +0.0063 | +0.04 | +0.01 / +0.10 | no |
