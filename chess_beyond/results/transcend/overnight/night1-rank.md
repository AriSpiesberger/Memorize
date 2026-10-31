# Concepts ranked (night1)

Readable: not board-tier, seen at >= 8 discovery positions, persists >= 2 plies, at least one held-out pair. Ranked by strength (summed margins over the seed-check nulls). Model-only: best match in the other model below cosine 0.5.

## All readable concepts

| concept | model | tier | theme | strength | positions | persists (median / max) | held-out (confirmation) | best match in other model |
|---|---|---|---|---|---|---|---|---|
| S21 | S | best |  | 1.827 | 10 | 11.0 / 15 | 3 (3) | W9 (0.99) |
| W242 | W | clean | two or more queen moves | 1.741 | 10 | 2.0 / 3 | 1 (1) | S630 (0.91) |
| S97 | S | best | two or more pawn moves | 1.646 | 17 | 2.0 / 5 | 3 (2) | W347 (0.96) |
| W9 | W | clean | no capture or check | 1.535 | 13 | 12.0 / 15 | 3 (3) | S21 (0.99) |
| S124 | S | clean | two or more rook moves | 1.364 | 18 | 3.0 / 4 | 3 (3) | W835 (0.20) |
| S154 | S | clean | two or more pawn moves | 1.283 | 14 | 2.5 / 3 | 3 (2) | W157 (0.91) |
| W236 | W | clean | king move | 1.154 | 9 | 3.0 / 9 | 2 (0) | S107 (0.56) |

## S only

| concept | model | tier | theme | strength | positions | persists (median / max) | held-out (confirmation) | best match in other model |
|---|---|---|---|---|---|---|---|---|
| S124 | S | clean | two or more rook moves | 1.364 | 18 | 3.0 / 4 | 3 (3) | W835 (0.20) |

## W only

| concept | model | tier | theme | strength | positions | persists (median / max) | held-out (confirmation) | best match in other model |
|---|---|---|---|---|---|---|---|---|

## Model-only concepts, counted

| model | all | not board | not board, persists >= 2 | readable |
|---|---|---|---|---|
| S | 168 | 23 | 12 | 1 |
| W | 157 | 11 | 6 | 0 |

Concepts on the map: S 680, W 644.

