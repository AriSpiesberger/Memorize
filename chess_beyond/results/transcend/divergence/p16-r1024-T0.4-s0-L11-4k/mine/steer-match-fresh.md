# Pushing a concept against having it

Matched plies of each branch pair's chosen (concept high) and subpar (low) lines. Natural: the chosen state's move distribution minus the subpar state's. Injected: the subpar state's after h -> h + r ||h|| u_hat (r = 0.1, 0.25, 0.5), minus its own; +v, -v and 20 random v's of matching firing rate, all pushing equally hard. Alignment: the injected change projected on the unit natural change, mean over pairs (beside it the mean cosine). Self-check at r = 0.25: +v above every random v, -v no better than the random median, Benjamini-Hochberg q < 0.05; transfer at any r (Bonferroni), above the random 95th. Fresh branch pairs: positions the concept was not mined from.

## Pre-specified

Each concept in its named space only; Benjamini-Hochberg over these 3 tests.

| concept | space | pairs (positions) | +v | -v | random median | random max | +v / natural size | q | verdict |
|---|---|---|---|---|---|---|---|---|---|
| S14 | features | 150 (34) | +0.165 | +0.028 | +0.020 | +0.067 | 10.5% | 0.000 | fails |
| S141 | features | 150 (22) | +0.029 | +0.010 | +0.015 | +0.028 | 1.8% | 0.067 | fails |
| W25 | common | 123 (29) | +0.011 | +0.013 | +0.012 | +0.038 | 1.8% | 0.671 | fails |

## common: probability over the moves legal in both states

Self-check passes: 1 of 3; transfer: 0 of those.

| concept | theme | shared cos | pairs (positions) | natural size | +v / -v / random median / max (q), r = 0.25 | cosine +v / -v / random median / max | +v over r | -v over r | self-check | transfer: other +v / random 95th @r (q) |
|---|---|---|---|---|---|---|---|---|---|---|
| S14 | two or more captures | 0.915 | 142 (34) | 0.626 | +0.068 / +0.005 / +0.014 / +0.059 (0.00) | +0.20 / +0.04 / +0.10 / +0.20 | +0.012 +0.068 +0.118 | +0.000 +0.005 +0.023 | passes | W +0.020 / +0.019 @0.25 (0.08) |
| W25 | king move | 0.915 | 123 (29) | 0.597 | +0.011 / +0.013 / +0.012 / +0.038 (0.67) | +0.11 / +0.17 / +0.10 / +0.20 | -0.003 +0.011 +0.035 | +0.003 +0.013 +0.036 | fails | S +0.059 / +0.034 @0.25 (0.00) |
| S141 | repeats a move | 0.128 | 126 (22) | 0.588 | +0.011 / +0.009 / +0.008 / +0.035 (0.61) | +0.07 / +0.05 / +0.09 / +0.23 | -0.001 +0.011 +0.048 | +0.003 +0.009 +0.028 | fails | W +0.042 / +0.038 @0.5 (0.08) |

## features: expected move features

Self-check passes: 0 of 3; transfer: 0 of those.

| concept | theme | shared cos | pairs (positions) | natural size | +v / -v / random median / max (q), r = 0.25 | cosine +v / -v / random median / max | +v over r | -v over r | self-check | transfer: other +v / random 95th @r (q) |
|---|---|---|---|---|---|---|---|---|---|---|
| S14 | two or more captures | 0.915 | 150 (34) | 1.567 | +0.165 / +0.028 / +0.020 / +0.067 (0.00) | +0.22 / +0.08 / +0.09 / +0.15 | +0.017 +0.165 +0.265 | +0.007 +0.028 +0.058 | fails | W +0.048 / +0.025 @0.25 (0.00) |
| W25 | king move | 0.915 | 150 (29) | 1.584 | +0.024 / +0.011 / +0.016 / +0.057 (0.40) | +0.09 / +0.08 / +0.11 / +0.18 | +0.004 +0.024 +0.073 | +0.003 +0.011 +0.034 | fails | S +0.112 / +0.042 @0.25 (0.00) |
| S141 | repeats a move | 0.128 | 150 (22) | 1.588 | +0.029 / +0.010 / +0.015 / +0.028 (0.07) | +0.12 / -0.02 / +0.06 / +0.12 | +0.004 +0.029 +0.107 | +0.002 +0.010 +0.034 | fails | W +0.067 / +0.060 @0.5 (0.11) |

Natural size: the mean length of the natural change (the same units as the alignment); an alignment equal to it would mean the push reproduces the whole difference between having the concept and not.

