# Seed stability of the L11 crosscoders: seed 0 against seed 1

A latent of seed 0 matches when it and a latent of seed 1 are each other's best partner by decoder cosine and the cosine is above 0.9. r: the latent's decoder norm toward S over its total (seed 0); exclusive: r < 0.1 (W only) or > 0.9 (S only).

## 4096 latents

| decoder | all (4096) | shared (4096) | S only (0) | W only (0) | median best cosine |
|---|---|---|---|---|---|
| both models | 31.2% | 31.2% | - | - | 0.804 |
| both models, optimal one-to-one | 31.2% | 31.2% | - | - | |
| chess-pgn-1000-1300 | 30.2% | 30.2% | - | - | 0.796 |
| chess-pgn-2400plus | 30.6% | 30.6% | - | - | 0.796 |

## 16384 latents

| decoder | all (16384) | shared (16384) | S only (0) | W only (0) | median best cosine |
|---|---|---|---|---|---|
| both models | 23.0% | 23.0% | - | - | 0.746 |
| chess-pgn-1000-1300 | 21.9% | 21.9% | - | - | 0.745 |
| chess-pgn-2400plus | 23.3% | 23.3% | - | - | 0.747 |

