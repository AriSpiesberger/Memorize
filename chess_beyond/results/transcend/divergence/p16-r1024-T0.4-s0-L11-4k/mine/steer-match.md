# Pushing a concept against having it

Matched plies of each branch pair's chosen (concept high) and subpar (low) lines. Natural: the chosen state's move distribution minus the subpar state's. Injected: the subpar state's after h -> h + r ||h|| u_hat (r = 0.1, 0.25, 0.5), minus its own; +v, -v and 20 random v's of matching firing rate, all pushing equally hard. Alignment: the injected change projected on the unit natural change, mean over pairs (beside it the mean cosine). Self-check at r = 0.25: +v above every random v, -v below zero, Benjamini-Hochberg q < 0.05; transfer at any r (Bonferroni), above the random 95th.

## common: probability over the moves legal in both states

Self-check passes: 0 of 10; transfer: 0 of those.

| concept | theme | shared cos | pairs (positions) | natural size | +v / -v / random median / max (q), r = 0.25 | cosine +v / -v / random median / max | +v over r | -v over r | self-check | transfer: other +v / random 95th @r (q) |
|---|---|---|---|---|---|---|---|---|---|---|
| S8 | two or more rook moves | 0.963 | 83 (9) | 0.602 | -0.000 / +0.046 / +0.016 / +0.045 (0.94) | +0.01 / +0.17 / +0.09 / +0.24 | -0.003 -0.000 +0.018 | +0.010 +0.046 +0.076 | fails | W +0.000 / +0.008 @0.1 (1.00) |
| W29 | two or more rook moves | 0.963 | 50 (5) | 0.643 | +0.026 / -0.003 / +0.014 / +0.051 (0.30) | +0.23 / -0.03 / +0.12 / +0.32 | +0.009 +0.026 +0.056 | -0.006 -0.003 +0.014 | fails | S -0.000 / +0.012 @0.1 (1.00) |
| S14 | two or more captures | 0.915 | 72 (8) | 0.714 | +0.033 / +0.002 / +0.009 / +0.051 (0.24) | +0.20 / -0.02 / +0.11 / +0.27 | -0.000 +0.033 +0.072 | +0.000 +0.002 +0.011 | fails | W +0.084 / +0.075 @0.5 (0.77) |
| W25 | king move | 0.915 | 45 (10) | 0.622 | +0.037 / +0.011 / +0.007 / +0.030 (0.03) | +0.27 / +0.06 / +0.11 / +0.27 | +0.007 +0.037 +0.072 | +0.002 +0.011 +0.029 | fails | S +0.145 / +0.084 @0.5 (0.00) |
| S29 | two or more pawn moves | 0.895 | 82 (4) | 0.549 | +0.028 / +0.013 / +0.012 / +0.035 (0.29) | +0.17 / +0.09 / +0.10 / +0.28 | +0.013 +0.028 +0.049 | -0.005 +0.013 +0.072 | fails | W +0.004 / +0.010 @0.1 (1.00) |
| W138 | no capture or check | 0.895 | 20 (3) | 0.548 | +0.024 / -0.003 / +0.014 / +0.043 (0.34) | +0.02 / +0.14 / +0.08 / +0.33 | +0.013 +0.024 +0.033 | -0.005 -0.003 +0.015 | fails | S +0.006 / +0.009 @0.1 (1.00) |
| W197 | two or more pawn moves | 0.665 | 15 (3) | 0.599 | +0.021 / +0.000 / +0.020 / +0.043 (0.42) | +0.21 / +0.10 / +0.24 / +0.47 | +0.007 +0.021 +0.051 | -0.001 +0.000 +0.044 | fails | S +0.011 / +0.010 @0.1 (0.85) |
| S141 | repeats a move | 0.128 | 18 (3) | 0.463 | +0.022 / -0.004 / +0.005 / +0.026 (0.21) | +0.08 / +0.03 / -0.00 / +0.15 | +0.003 +0.022 +0.056 | -0.001 -0.004 -0.001 | fails | W +0.004 / +0.018 @0.1 (1.00) |
| W30 | two or more pawn moves | 0.074 | 52 (3) | 0.513 | +0.019 / +0.002 / +0.005 / +0.025 (0.26) | +0.14 / -0.01 / +0.06 / +0.20 | +0.007 +0.019 +0.048 | +0.003 +0.002 +0.044 | fails | S +0.011 / +0.010 @0.1 (0.85) |
| S58 |  | 0.049 | 47 (4) | 0.620 | +0.025 / +0.030 / +0.016 / +0.046 (0.36) | +0.09 / +0.08 / +0.10 / +0.24 | +0.011 +0.025 +0.045 | +0.002 +0.030 +0.058 | fails | W -0.001 / +0.009 @0.1 (1.00) |

## features: expected move features

Self-check passes: 0 of 10; transfer: 0 of those.

| concept | theme | shared cos | pairs (positions) | natural size | +v / -v / random median / max (q), r = 0.25 | cosine +v / -v / random median / max | +v over r | -v over r | self-check | transfer: other +v / random 95th @r (q) |
|---|---|---|---|---|---|---|---|---|---|---|
| S8 | two or more rook moves | 0.963 | 95 (9) | 1.587 | +0.008 / +0.082 / +0.025 / +0.054 (0.92) | +0.02 / +0.20 / +0.08 / +0.21 | -0.001 +0.008 +0.037 | +0.014 +0.082 +0.163 | fails | W +0.008 / +0.006 @0.1 (0.44) |
| W29 | two or more rook moves | 0.963 | 59 (5) | 1.482 | -0.007 / +0.032 / +0.008 / +0.048 (0.92) | -0.06 / +0.12 / +0.05 / +0.26 | -0.005 -0.007 -0.007 | +0.012 +0.032 +0.072 | fails | S +0.021 / +0.177 @0.5 (1.00) |
| S14 | two or more captures | 0.915 | 93 (8) | 1.747 | +0.099 / +0.015 / +0.020 / +0.051 (0.00) | +0.20 / +0.04 / +0.10 / +0.23 | +0.012 +0.099 +0.170 | +0.004 +0.015 +0.043 | fails | W +0.116 / +0.106 @0.5 (0.22) |
| W25 | king move | 0.915 | 57 (10) | 1.734 | +0.002 / +0.018 / +0.012 / +0.039 (0.92) | -0.01 / +0.14 / +0.07 / +0.19 | -0.000 +0.002 +0.025 | +0.004 +0.018 +0.055 | fails | S +0.096 / +0.088 @0.5 (0.42) |
| S29 | two or more pawn moves | 0.895 | 83 (4) | 1.286 | +0.020 / +0.040 / +0.016 / +0.054 (0.92) | +0.07 / +0.14 / +0.08 / +0.21 | +0.001 +0.020 +0.061 | +0.010 +0.040 +0.144 | fails | W +0.038 / +0.098 @0.5 (1.00) |
| W138 | no capture or check | 0.895 | 21 (3) | 1.249 | -0.001 / +0.020 / +0.020 / +0.061 (0.92) | -0.03 / +0.15 / +0.14 / +0.33 | -0.003 -0.001 +0.005 | +0.003 +0.020 +0.056 | fails | S +0.048 / +0.185 @0.5 (1.00) |
| W197 | two or more pawn moves | 0.665 | 15 (3) | 1.298 | +0.011 / +0.042 / +0.026 / +0.119 (0.92) | +0.06 / +0.29 / +0.10 / +0.26 | +0.002 +0.011 +0.071 | +0.013 +0.042 +0.117 | fails | S +0.032 / +0.022 @0.1 (0.22) |
| S141 | repeats a move | 0.128 | 24 (3) | 1.434 | +0.046 / +0.017 / +0.010 / +0.033 (0.01) | +0.17 / -0.10 / +0.04 / +0.20 | +0.006 +0.046 +0.091 | +0.008 +0.017 +0.025 | fails | W +0.114 / +0.098 @0.5 (0.22) |
| W30 | two or more pawn moves | 0.074 | 53 (3) | 1.457 | +0.034 / +0.017 / +0.006 / +0.051 (0.23) | -0.00 / +0.15 / +0.09 / +0.28 | +0.010 +0.034 +0.062 | -0.005 +0.017 +0.115 | fails | S +0.009 / +0.008 @0.1 (0.83) |
| S58 |  | 0.049 | 47 (4) | 1.298 | +0.031 / +0.092 / +0.015 / +0.047 (0.49) | +0.06 / +0.16 / +0.09 / +0.22 | +0.007 +0.031 +0.082 | +0.017 +0.092 +0.271 | fails | W +0.017 / +0.046 @0.25 (1.00) |

Natural size: the mean length of the natural change (the same units as the alignment); an alignment equal to it would mean the push reproduces the whole difference between having the concept and not.

