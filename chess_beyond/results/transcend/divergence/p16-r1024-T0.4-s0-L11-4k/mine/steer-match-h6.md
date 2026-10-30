# Pushing a concept against having it

Matched plies of each branch pair's chosen (concept high) and subpar (low) lines. Natural: the chosen state's move distribution minus the subpar state's. Injected: the subpar state's after h -> h + r ||h|| u_hat (r = 0.1, 0.25, 0.5), minus its own; +v, -v and 20 random v's of matching firing rate, all pushing equally hard. Alignment: the injected change projected on the unit natural change, mean over pairs (beside it the mean cosine). Self-check at r = 0.25: +v above every random v, -v below zero, Benjamini-Hochberg q < 0.05; transfer at any r (Bonferroni), above the random 95th. Pushed at the last 6 plies' prompt ends, each by its own norm.

## common: probability over the moves legal in both states

Self-check passes: 0 of 10; transfer: 0 of those.

| concept | theme | shared cos | pairs (positions) | natural size | +v / -v / random median / max (q), r = 0.25 | cosine +v / -v / random median / max | +v over r | -v over r | self-check | transfer: other +v / random 95th @r (q) |
|---|---|---|---|---|---|---|---|---|---|---|
| S8 | two or more rook moves | 0.963 | 83 (9) | 0.602 | +0.002 / +0.049 / +0.016 / +0.047 (0.90) | +0.05 / +0.19 / +0.09 / +0.27 | -0.002 +0.002 +0.023 | +0.009 +0.049 +0.081 | fails | W -0.001 / +0.006 @0.1 (1.00) |
| W29 | two or more rook moves | 0.963 | 50 (5) | 0.643 | +0.026 / -0.007 / +0.014 / +0.052 (0.42) | +0.22 / -0.07 / +0.09 / +0.33 | +0.011 +0.026 +0.052 | -0.008 -0.007 +0.014 | fails | S +0.051 / +0.129 @0.5 (1.00) |
| S14 | two or more captures | 0.915 | 72 (8) | 0.714 | +0.051 / +0.001 / +0.013 / +0.046 (0.03) | +0.20 / +0.00 / +0.08 / +0.31 | +0.002 +0.051 +0.100 | -0.001 +0.001 +0.013 | fails | W +0.095 / +0.075 @0.5 (0.23) |
| W25 | king move | 0.915 | 45 (10) | 0.622 | +0.017 / +0.012 / +0.009 / +0.029 (0.42) | +0.19 / +0.08 / +0.10 / +0.28 | +0.000 +0.017 +0.061 | +0.003 +0.012 +0.026 | fails | S +0.062 / +0.029 @0.25 (0.00) |
| S29 | two or more pawn moves | 0.895 | 82 (4) | 0.549 | +0.023 / +0.017 / +0.015 / +0.043 (0.42) | +0.14 / +0.12 / +0.12 / +0.30 | +0.012 +0.023 +0.041 | -0.002 +0.017 +0.081 | fails | W +0.004 / +0.012 @0.1 (1.00) |
| W138 | no capture or check | 0.895 | 20 (3) | 0.548 | +0.027 / -0.005 / +0.016 / +0.043 (0.42) | +0.19 / +0.04 / +0.12 / +0.39 | +0.015 +0.027 +0.041 | -0.005 -0.005 +0.015 | fails | S +0.006 / +0.008 @0.1 (1.00) |
| W197 | two or more pawn moves | 0.665 | 15 (3) | 0.599 | +0.019 / +0.004 / +0.019 / +0.038 (0.48) | +0.23 / +0.10 / +0.16 / +0.41 | +0.006 +0.019 +0.050 | +0.001 +0.004 +0.045 | fails | S +0.010 / +0.010 @0.1 (0.85) |
| S141 | repeats a move | 0.128 | 18 (3) | 0.463 | +0.023 / -0.001 / +0.000 / +0.029 (0.11) | +0.11 / -0.02 / -0.02 / +0.16 | +0.005 +0.023 +0.052 | -0.003 -0.001 +0.009 | fails | W +0.009 / +0.017 @0.1 (1.00) |
| W30 | two or more pawn moves | 0.074 | 52 (3) | 0.513 | +0.021 / +0.005 / +0.006 / +0.027 (0.26) | +0.17 / +0.01 / +0.08 / +0.19 | +0.007 +0.021 +0.050 | +0.002 +0.005 +0.053 | fails | S +0.011 / +0.011 @0.1 (0.85) |
| S58 |  | 0.049 | 47 (4) | 0.620 | +0.024 / +0.031 / +0.016 / +0.050 (0.42) | +0.11 / +0.09 / +0.08 / +0.25 | +0.010 +0.024 +0.046 | +0.002 +0.031 +0.068 | fails | W -0.001 / +0.011 @0.1 (1.00) |

## features: expected move features

Self-check passes: 0 of 10; transfer: 0 of those.

| concept | theme | shared cos | pairs (positions) | natural size | +v / -v / random median / max (q), r = 0.25 | cosine +v / -v / random median / max | +v over r | -v over r | self-check | transfer: other +v / random 95th @r (q) |
|---|---|---|---|---|---|---|---|---|---|---|
| S8 | two or more rook moves | 0.963 | 95 (9) | 1.587 | +0.009 / +0.087 / +0.025 / +0.043 (0.96) | +0.01 / +0.22 / +0.10 / +0.25 | -0.001 +0.009 +0.041 | +0.014 +0.087 +0.169 | fails | W +0.004 / +0.006 @0.1 (1.00) |
| W29 | two or more rook moves | 0.963 | 59 (5) | 1.482 | -0.011 / +0.046 / +0.008 / +0.043 (0.96) | -0.10 / +0.14 / +0.05 / +0.18 | -0.009 -0.011 -0.013 | +0.017 +0.046 +0.092 | fails | S +0.018 / +0.172 @0.5 (1.00) |
| S14 | two or more captures | 0.915 | 93 (8) | 1.747 | +0.112 / +0.023 / +0.027 / +0.058 (0.00) | +0.20 / +0.06 / +0.12 / +0.21 | +0.014 +0.112 +0.168 | +0.010 +0.023 +0.050 | fails | W +0.133 / +0.101 @0.5 (0.04) |
| W25 | king move | 0.915 | 57 (10) | 1.734 | +0.001 / +0.024 / +0.014 / +0.039 (0.96) | +0.02 / +0.14 / +0.09 / +0.19 | -0.003 +0.001 +0.027 | +0.008 +0.024 +0.062 | fails | S +0.098 / +0.101 @0.5 (0.68) |
| S29 | two or more pawn moves | 0.895 | 83 (4) | 1.286 | +0.019 / +0.052 / +0.020 / +0.062 (0.96) | +0.05 / +0.17 / +0.10 / +0.24 | +0.000 +0.019 +0.063 | +0.014 +0.052 +0.156 | fails | W +0.013 / +0.028 @0.25 (1.00) |
| W138 | no capture or check | 0.895 | 21 (3) | 1.249 | +0.000 / +0.019 / +0.021 / +0.062 (0.96) | -0.02 / +0.11 / +0.15 / +0.33 | -0.003 +0.000 +0.011 | +0.004 +0.019 +0.055 | fails | S +0.047 / +0.204 @0.5 (1.00) |
| W197 | two or more pawn moves | 0.665 | 15 (3) | 1.298 | +0.000 / +0.054 / +0.021 / +0.124 (0.96) | +0.05 / +0.30 / +0.10 / +0.26 | -0.002 +0.000 +0.051 | +0.019 +0.054 +0.123 | fails | S +0.029 / +0.028 @0.1 (0.62) |
| S141 | repeats a move | 0.128 | 24 (3) | 1.434 | +0.050 / +0.016 / +0.011 / +0.026 (0.00) | +0.20 / -0.16 / +0.04 / +0.17 | +0.010 +0.050 +0.088 | +0.007 +0.016 +0.024 | fails | W +0.047 / +0.031 @0.25 (0.34) |
| W30 | two or more pawn moves | 0.074 | 53 (3) | 1.457 | +0.036 / +0.026 / +0.005 / +0.052 (0.27) | +0.04 / +0.21 / +0.08 / +0.28 | +0.011 +0.036 +0.066 | -0.005 +0.026 +0.133 | fails | S +0.011 / +0.009 @0.1 (0.73) |
| S58 |  | 0.049 | 47 (4) | 1.298 | +0.032 / +0.096 / +0.018 / +0.049 (0.44) | +0.10 / +0.17 / +0.11 / +0.23 | +0.007 +0.032 +0.090 | +0.018 +0.096 +0.259 | fails | W +0.004 / +0.012 @0.1 (1.00) |

Natural size: the mean length of the natural change (the same units as the alignment); an alignment equal to it would mean the push reproduces the whole difference between having the concept and not.

