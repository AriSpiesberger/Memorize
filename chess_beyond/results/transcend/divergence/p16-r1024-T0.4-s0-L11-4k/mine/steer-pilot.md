# Steering mined concepts (pilot)

Strength alpha in units of each concept's own gap g. Decision rule fixed before the results (see steer_concepts.py summary): Benjamini-Hochberg at q < 0.05 over concepts, 20 random v's per concept on latents of matching firing rate.

Self-check passes: 0 of 10. Positive control (shared, cos >= 0.7, self-check passed): 0 of 0 transfer (nan%; the rule needs >= 70% before a failure to transfer counts).

Verdicts: fails self-check 10

| concept | tier | theme | shared cos | verdict | self +v / -v / max random (q) | dose +v over alpha | KL +v / -v / random | transfer: other model +v / random 95th @alpha (q) | decoder share | held-out points (other positions) | held-out +v self / other |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S8 | best | two or more rook moves | 0.963 | fails self-check | +0.01 / -0.01 / +0.08 (0.90) | +0.01 +0.01 +0.01 +0.01 | 0.00 / 0.00 / 0.00 | W +0.02 / +0.06 @0.5 (1.00) | 0.473 | 4 (4) | -0.00 / +0.11 |
| W29 | best | two or more rook moves | 0.963 | fails self-check | -0.16 / +0.07 / +0.01 (1.00) | -0.07 -0.16 -0.43 -0.76 | 0.01 / 0.01 / 0.00 | S -0.36 / +0.10 @2.0 (1.00) | 0.529 | 4 (4) | -0.06 / -0.11 |
| S14 | best | two or more captures | 0.915 | fails self-check | +0.04 / -0.10 / +0.04 (0.90) | +0.02 +0.04 +0.08 -0.20 | 0.00 / 0.01 / 0.02 | W +0.02 / +0.07 @2.0 (1.00) | 0.441 | 4 (4) | -0.03 / +0.02 |
| W25 | best | king move | 0.915 | fails self-check | +0.02 / -0.03 / +0.08 (0.90) | +0.00 +0.02 +0.02 -0.08 | 0.01 / 0.02 / 0.00 | S -0.00 / +0.05 @1.0 (1.00) | 0.57 | 4 (4) | -0.03 / -0.09 |
| S29 | best | two or more pawn moves | 0.895 | fails self-check | -0.24 / -0.01 / +0.06 (1.00) | -0.07 -0.24 -0.74 -1.22 | 0.06 / 0.02 / 0.00 | W +0.01 / +0.02 @0.5 (1.00) | 0.489 | 3 (3) | -0.05 / +0.07 |
| W138 | best | no capture or check | 0.895 | fails self-check | -0.05 / -0.09 / +0.05 (0.90) | -0.02 -0.05 -0.19 -0.43 | 0.01 / 0.02 / 0.01 | S -0.09 / +0.04 @0.5 (1.00) | 0.468 | 4 (4) | +0.02 / +0.21 |
| W197 | best | two or more pawn moves | 0.665 | fails self-check | +0.01 / -0.07 / +0.12 (0.90) | +0.01 +0.01 -0.01 -0.06 | 0.00 / 0.01 / 0.01 | S +0.05 / +0.09 @1.0 (1.00) | 0.367 | 4 (4) | +0.08 / +0.17 |
| S141 | best | repeats a move | 0.128 | fails self-check | -0.01 / +0.01 / +0.02 (0.90) | -0.01 -0.01 -0.03 -0.06 | 0.00 / 0.00 / 0.00 | W -0.01 / +0.04 @1.0 (1.00) | 0.716 | 4 (4) | +0.02 / -0.01 |
| W30 | board | two or more pawn moves | 0.074 | fails self-check | -0.01 / -0.02 / +0.02 (0.90) | +0.00 -0.01 +0.01 -0.02 | 0.00 / 0.01 / 0.00 | S -0.23 / +0.10 @2.0 (1.00) | 0.513 | 3 (3) | +0.01 / +0.02 |
| S58 | best |  | 0.049 | fails self-check | -0.07 / +0.01 / +0.08 (0.90) | -0.04 -0.07 -0.16 -0.34 | 0.01 / 0.01 / 0.01 | W +0.04 / +0.09 @2.0 (1.00) | 0.555 | 4 (4) | -0.08 / -0.05 |

Columns: self = the concept's own model at its branch points, alpha = 1. Dose: +v at alpha = 0.5, 1.0, 2.0, 4.0. KL: over all legal moves at alpha = 1, the disruption beside the gain; a large KL for -v and random as well means the effect is disruption, not the concept. Held-out points: windows where the concept switches on away from its branch points; the count in brackets is at other positions, the stronger test. Decoder share: the concept's latents' decoder norm in the other model; near zero means that model does not represent them.

