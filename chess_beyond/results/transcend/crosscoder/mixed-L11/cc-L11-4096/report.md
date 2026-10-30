# Crosscoder at L11, 4096 latents

k = 64, 20000 steps of 4096; human and rollout positions about half each. Held out: human by game, rollouts by root.

| held out | FVU chess-pgn-1000-1300 | FVU chess-pgn-2400plus | L0 |
|---|---|---|---|
| human | 0.0819 | 0.0983 | 64.4 |
| rollouts | 0.0882 | 0.0967 | 64.5 |

Splice KL (nats): each model's move distribution against the one with its state at this layer replaced by the reconstruction; S-W KL: S's distribution against W's at the same positions.

| held out | chess-pgn-1000-1300 | chess-pgn-2400plus | S-W KL |
|---|---|---|---|
| human | 0.0278 | 0.0463 | 0.4162 |
| rollouts | 0.0331 | 0.0451 | 0.5055 |

Dead latents (never firing on the held-out positions): 0.8%; resampled during training: 0. Antipodal decoder pairs (cosine < -0.9): chess-pgn-1000-1300 25, chess-pgn-2400plus 23.
