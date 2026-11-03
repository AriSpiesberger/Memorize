# Crosscoder at L8, 4096 latents

k = 64, 20000 steps of 4096; human and rollout positions about half each. Held out: human by game, rollouts by root.

| held out | FVU chess-pgn-1000-1300 | FVU chess-pgn-2400plus | L0 |
|---|---|---|---|
| human | 0.0325 | 0.0392 | 65.9 |
| rollouts | 0.0336 | 0.0369 | 62.7 |

Splice KL (nats): each model's move distribution against the one with its state at this layer replaced by the reconstruction; S-W KL: S's distribution against W's at the same positions.

| held out | chess-pgn-1000-1300 | chess-pgn-2400plus | S-W KL |
|---|---|---|---|
| human | 0.0040 | 0.0089 | 0.4162 |
| rollouts | 0.0050 | 0.0079 | 0.5055 |

Dead latents (never firing on the held-out positions): 0.8%; resampled during training: 0. Antipodal decoder pairs (cosine < -0.9): chess-pgn-1000-1300 28, chess-pgn-2400plus 31.
