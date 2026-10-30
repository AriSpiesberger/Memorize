# Each model's reading of the shared latents: where S and W disagree vs agree

1000 held-out middlegame positions (one per game): S and W pick different top moves at 412 (41%), the same at 588; their policies' Jensen-Shannon divergence: median 0.140 bits (disagree 0.223, agree 0.097). r^m = (x_m - b_dec_m) W_enc^m, each model's block of the pre-activation; d = r^S - r^W. Fit / held-out halves by game: 206 / 206 disagree, 295 / 293 agree. Only latents active (joint code f > 0) at >= 5% of positions: 186.

## The 20 active latents with the mean of d most larger at disagree positions (S reads it more than W there)

| latent | mean d, disagree | mean d, agree | difference | t | Spearman with JS | active |
|---|---|---|---|---|---|---|
| 11036 | +1.880 | +0.360 | +1.520 | +3.0 | +0.14 | 24% |
| 4312 | +0.518 | -0.963 | +1.481 | +4.1 | +0.24 | 30% |
| 10728 | +1.642 | +0.239 | +1.403 | +3.1 | +0.06 | 30% |
| 6341 | +1.736 | +0.482 | +1.254 | +3.3 | +0.28 | 20% |
| 15221 | -0.341 | -1.189 | +0.848 | +2.3 | +0.20 | 26% |
| 13911 | +0.912 | +0.129 | +0.782 | +1.9 | +0.15 | 30% |
| 5111 | +2.254 | +1.495 | +0.759 | +1.9 | +0.13 | 26% |
| 6935 | +0.200 | -0.497 | +0.697 | +2.0 | +0.17 | 32% |
| 12856 | +0.084 | -0.546 | +0.630 | +1.7 | +0.19 | 28% |
| 8247 | +1.764 | +1.437 | +0.328 | +0.8 | -0.00 | 32% |
| 1263 | +1.098 | +0.783 | +0.315 | +0.6 | +0.06 | 27% |
| 7474 | -0.136 | -0.363 | +0.227 | +1.9 | +0.02 | 48% |
| 2512 | -0.517 | -0.709 | +0.192 | +0.4 | +0.02 | 31% |
| 11273 | +0.494 | +0.340 | +0.154 | +1.8 | +0.12 | 40% |
| 11697 | +0.093 | -0.056 | +0.149 | +1.5 | +0.04 | 35% |
| 3872 | +0.361 | +0.221 | +0.140 | +3.1 | +0.09 | 5% |
| 6691 | +0.079 | -0.057 | +0.136 | +1.2 | +0.05 | 53% |
| 1167 | +0.036 | -0.084 | +0.120 | +2.5 | +0.13 | 7% |
| 6307 | -0.231 | -0.350 | +0.119 | +1.8 | +0.00 | 10% |
| 4449 | +0.203 | +0.087 | +0.116 | +0.9 | +0.03 | 41% |

## The 20 active latents with the mean of d most smaller at disagree positions (W reads it more than S there)

| latent | mean d, disagree | mean d, agree | difference | t | Spearman with JS | active |
|---|---|---|---|---|---|---|
| 5080 | -1.843 | -0.342 | -1.501 | -3.0 | -0.14 | 28% |
| 10560 | -0.561 | +0.904 | -1.465 | -4.1 | -0.24 | 28% |
| 3356 | -1.656 | -0.247 | -1.409 | -3.1 | -0.06 | 32% |
| 7500 | -1.721 | -0.468 | -1.253 | -3.2 | -0.28 | 19% |
| 6897 | +0.313 | +1.166 | -0.853 | -2.3 | -0.20 | 25% |
| 14520 | -0.953 | -0.178 | -0.776 | -1.9 | -0.15 | 33% |
| 9704 | -2.268 | -1.507 | -0.761 | -1.9 | -0.13 | 27% |
| 10266 | -0.209 | +0.480 | -0.689 | -1.9 | -0.17 | 33% |
| 13007 | -0.094 | +0.534 | -0.628 | -1.7 | -0.19 | 33% |
| 14795 | -1.805 | -1.483 | -0.322 | -0.7 | +0.00 | 28% |
| 3718 | -1.156 | -0.836 | -0.320 | -0.6 | -0.06 | 27% |
| 12744 | +0.068 | +0.294 | -0.226 | -1.8 | -0.01 | 38% |
| 9134 | +0.476 | +0.668 | -0.192 | -0.4 | -0.02 | 33% |
| 16305 | -0.164 | -0.006 | -0.158 | -1.5 | -0.04 | 56% |
| 16057 | -0.584 | -0.427 | -0.158 | -1.8 | -0.12 | 50% |
| 1331 | +0.321 | +0.460 | -0.139 | -3.4 | -0.11 | 9% |
| 12838 | -0.135 | +0.001 | -0.137 | -1.2 | -0.05 | 38% |
| 14472 | +0.618 | +0.754 | -0.136 | -2.2 | -0.08 | 5% |
| 11428 | -0.327 | -0.197 | -0.130 | -3.5 | -0.13 | 21% |
| 13121 | -0.262 | -0.145 | -0.117 | -1.0 | -0.03 | 50% |

Pairs of active latents whose d is exactly opposite (correlation < -0.99: one quantity, two latents): 32: 52/3714, 689/2234, 801/12775, 1263/3718, 2095/15759, 2327/10926, 2512/9134, 3356/10728, 3406/14723, 4312/10560, 4324/13061, 4449/13121, 5080/11036, 5111/9704, 5410/6954, 6341/7500, 6691/12838, 6736/14567, 6897/15221, 6935/10266.

## Schut's LP, two ways

(1) As before: S's reading over W's (or W's over S's) on the fit disagree positions; it holds at a position when v.d reaches the fitted margin. Gap = held-out disagree hits minus held-out agree hits. (2) The contrast: positives d at the fit disagree positions, negatives d at the fit agree ones (their pairs), so the offset between the models' readings cancels and the LP has to find what is specific to disagreement; scored by the held-out AUC of v.d for disagree against agree (S's side: v.d larger where they disagree; W's side: smaller). Both against 100 permutations of the disagree / agree labels (within each half), refitted; and v.d against the policies' Jensen-Shannon divergence on all held-out positions (Spearman), threshold-free.

| LP | side | held-out disagree / agree | statistic | permutation p (null median, 95%) | Spearman v.d with JS (held out) | v (latent: weight) |
|---|---|---|---|---|---|---|
| (1) readings | S | 68% / 70% | gap -2% | 0.703 (+0%, +7%) | +0.12 | 8149: 0.13, 10000: 0.10, 10226: 0.09, 16076: 0.08, 7687: 0.07, 14472: 0.07, 2842: 0.07, 11318: 0.06, 4161: 0.05, 1331: 0.05, 3872: 0.03, 2864: 0.03 ... |
| (1) readings | W | 71% / 62% | gap +9% | 0.030 (+1%, +6%) | +0.19 | 7271: 0.20, 237: 0.14, 686: 0.10, 11428: 0.09, 7960: 0.08, 14240: 0.07, 16057: 0.05, 3406: 0.04, 12744: 0.02, 275: 0.02, 5080: 0.02, 9704: 0.02 ... |
| (2) contrast | S | 206 / 293 | AUC 0.58 | 0.050 (0.51, 0.54) | +0.25 | 10926: 0.12, 2327: 0.11, 10386: 0.05, 13982: 0.05, 8149: 0.03, 9560: 0.03, 8823: 0.03, 6778: 0.03, 13705: 0.03, 7960: 0.03, 3872: 0.02, 703: 0.02 ... |
| (2) contrast | W | 206 / 293 | AUC 0.57 | 0.053 (0.49, 0.53) | +0.18 | 3356: 0.12, 10728: 0.12, 16305: 0.10, 11697: 0.10, 2234: 0.08, 689: 0.08, 9452: 0.02, 13512: 0.02, 2860: 0.02, 4291: 0.01, 6341: 0.01, 7500: 0.01 ... |

A concept specific to disagreement: the contrast LP's held-out AUC clearly above its permutation null, and v.d rising with the policies' divergence on held-out positions.

