# Concepts inside S's rollouts from one position

Position `3r4/6kp/2bbQ1p1/8/8/2q2PN1/6PP/3R3K w - - 0 38` (2400+ game 2329); S's entropy there 2.62; top moves Nf5+ 14%, Qe2 13%, Ne4 12%, h4 10%, Rxd6 9%. 2048 rollouts of S per batch, 8 plies, temperature 1.0; a rollout = per latent, the share of its plies where it fires.

## Planted test (half A of batch 1)

No value changed, only alignment: concept 1, 5 latents (not already correlated) aligned in 30% of the rollouts; concept 2, 5 latents (one shared with 1) in a different 20%. Pass: each matched by a found group with >= 3 of its 5 latents, at least half of the group planted latents. 70 groups found on the planted data.

| planted | matched | found groups that match | best group: share planted | its planted latents | its size |
|---|---|---|---|---|---|
| 1 | no | 0 | 100% | 0 / 5 | 4 |
| 2 | yes | 1 | 100% | 4 / 5 | 4 |

**Planted test FAILED.**

Stopped here, as fixed in advance. Next: --rollouts 2048 (1,024 per half).
