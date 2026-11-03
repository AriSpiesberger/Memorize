# Crosscoder at L9, 4096 latents

k = 64, 20000 steps of 4096; human and rollout positions about half each. Held out: human by game, rollouts by root.

| held out | FVU chess-pgn-1000-1300 | FVU chess-pgn-2400plus | L0 |
|---|---|---|---|
| human | 0.0453 | 0.0557 | 65.7 |
| rollouts | 0.0477 | 0.0531 | 63.2 |

Splice KL (nats): each model's move distribution against the one with its state at this layer replaced by the reconstruction; S-W KL: S's distribution against W's at the same positions.

| held out | chess-pgn-1000-1300 | chess-pgn-2400plus | S-W KL |
|---|---|---|---|
| human | 0.0085 | 0.0146 | 0.4162 |
| rollouts | 0.0075 | 0.0141 | 0.5055 |

Dead latents (never firing on the held-out positions): 1.0%; resampled during training: 3. Antipodal decoder pairs (cosine < -0.9): chess-pgn-1000-1300 24, chess-pgn-2400plus 24.
