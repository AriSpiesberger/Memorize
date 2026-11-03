# Crosscoder at L13, 4096 latents

k = 64, 20000 steps of 4096; human and rollout positions about half each. Held out: human by game, rollouts by root.

| held out | FVU chess-pgn-1000-1300 | FVU chess-pgn-2400plus | L0 |
|---|---|---|---|
| human | 0.1397 | 0.1581 | 63.9 |
| rollouts | 0.1509 | 0.1591 | 65.3 |

Splice KL (nats): each model's move distribution against the one with its state at this layer replaced by the reconstruction; S-W KL: S's distribution against W's at the same positions.

| held out | chess-pgn-1000-1300 | chess-pgn-2400plus | S-W KL |
|---|---|---|---|
| human | 0.0300 | 0.0509 | 0.4162 |
| rollouts | 0.0399 | 0.0614 | 0.5055 |

Dead latents (never firing on the held-out positions): 0.0%; resampled during training: 0. Antipodal decoder pairs (cosine < -0.9): chess-pgn-1000-1300 4, chess-pgn-2400plus 6.
