# Crosscoder at L11, 16384 latents

k = 64, 20000 steps of 4096; human and rollout positions about half each. Held out: human by game, rollouts by root.

| held out | FVU chess-pgn-1000-1300 | FVU chess-pgn-2400plus | L0 |
|---|---|---|---|
| human | 0.0750 | 0.0901 | 66.4 |
| rollouts | 0.0841 | 0.0932 | 65.7 |

Splice KL (nats): each model's move distribution against the one with its state at this layer replaced by the reconstruction; S-W KL: S's distribution against W's at the same positions.

| held out | chess-pgn-1000-1300 | chess-pgn-2400plus | S-W KL |
|---|---|---|---|
| human | 0.0278 | 0.0459 | 0.4162 |
| rollouts | 0.0314 | 0.0508 | 0.5055 |

Dead latents (never firing on the held-out positions): 3.6%; resampled during training: 0. Antipodal decoder pairs (cosine < -0.9): chess-pgn-1000-1300 31, chess-pgn-2400plus 27.
