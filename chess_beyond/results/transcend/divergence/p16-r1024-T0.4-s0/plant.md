# Planted check (S)

At each of the first 20 positions: one random pair with 4 plies left after the split; 3 latents (off in both lines at plies t..t+4, on at 1-30% of the position's plies) switched on in the chosen line only at plies t..t+4; steps 1-2 rerun (C = 2.0). 'in v': v holds a planted latent; 'only': v is planted latents only; 'ties': all 3 are among the latents that alone separate the window; 'leak': other pairs at that position whose v holds a planted latent.

| position | ply | chosen / subpar | planted | k=4: in v, only, ties | k=4 v | k=0: in v, only, ties | k=0 v | leak k=4 / k=0 |
|---|---|---|---|---|---|---|---|---|
| 0 | 11 | Rxb2+ / cxb2 | 5148, 9096, 10830 | yes, yes, yes (3 ties) | 5148:1.00 | no, no, yes (49 ties) | 52:1.00 | 0 / 0 |
| 1 | 4 | Nf6 / Nde5 | 237, 2846, 13596 | yes, yes, yes (3 ties) | 237:1.00 | no, no, yes (26 ties) | 52:1.00 | 0 / 0 |
| 2 | 9 | d5 / f5 | 9854, 11733, 15844 | yes, yes, yes (3 ties) | 9854:1.00 | no, no, yes (31 ties) | 72:1.00 | 0 / 0 |
| 3 | 8 | Ne3 / b4 | 4494, 13252, 14983 | yes, yes, yes (4 ties) | 4494:1.00 | no, no, yes (27 ties) | 873:1.00 | 0 / 0 |
| 4 | 8 | Bg7 / Bf5 | 493, 9170, 14229 | yes, yes, yes (3 ties) | 493:1.00 | yes, yes, yes (25 ties) | 493:1.00 | 0 / 0 |
| 5 | 11 | Qh5 / e4 | 1558, 3184, 14040 | yes, yes, yes (3 ties) | 1558:1.00 | no, no, yes (35 ties) | 52:1.00 | 0 / 0 |
| 6 | 4 | Ne3 / g3 | 4357, 6442, 7283 | yes, yes, yes (3 ties) | 4357:1.00 | no, no, yes (28 ties) | 2095:1.00 | 0 / 0 |
| 7 | 2 | Kh8 / Kh7 | 168, 2476, 10692 | yes, yes, yes (3 ties) | 168:1.00 | yes, yes, yes (12 ties) | 168:1.00 | 2 / 4 |
| 8 | 5 | Nxd2 / Qxd2 | 6678, 10226, 12538 | yes, yes, yes (3 ties) | 6678:1.00 | no, no, yes (15 ties) | 2842:1.00 | 1 / 0 |
| 9 | 11 | Ra1 / Nd4 | 6435, 11482, 15746 | yes, yes, yes (3 ties) | 6435:1.00 | no, no, yes (38 ties) | 123:1.00 | 0 / 0 |
| 10 | 12 | b6 / Be8 | 6819, 12119, 12309 | yes, yes, yes (3 ties) | 6819:1.00 | no, no, yes (43 ties) | 52:1.00 | 0 / 0 |
| 11 | 8 | Rac8 / Rxg5 | 9409, 12204, 14176 | yes, yes, yes (3 ties) | 9409:1.00 | no, no, yes (59 ties) | 714:1.00 | 0 / 0 |
| 12 | 8 | Bf4 / Re1 | 8501, 12298, 14850 | yes, yes, yes (3 ties) | 8501:1.00 | no, no, yes (35 ties) | 1167:1.00 | 0 / 0 |
| 13 | 10 | a3 / Bd4 | 6210, 9769, 11268 | yes, yes, yes (3 ties) | 6210:1.00 | no, no, yes (26 ties) | 123:1.00 | 0 / 0 |
| 14 | 10 | Qb5 / Qc7 | 5483, 7947, 9516 | yes, yes, yes (3 ties) | 5483:1.00 | no, no, yes (27 ties) | 801:1.00 | 0 / 0 |
| 15 | 7 | Rd8 / Qxc6 | 3439, 4202, 14473 | yes, yes, yes (3 ties) | 3439:1.00 | no, no, yes (36 ties) | 294:1.00 | 1 / 0 |
| 16 | 3 | Rfe8+ / Nxh1 | 1425, 6567, 13864 | yes, yes, yes (3 ties) | 1425:1.00 | no, no, yes (35 ties) | 689:1.00 | 0 / 0 |
| 17 | 7 | Re1 / Bf4 | 4322, 12734, 14315 | yes, yes, yes (3 ties) | 4322:1.00 | no, no, yes (18 ties) | 997:1.00 | 0 / 0 |
| 18 | 9 | Rad1 / Bxc5 | 2342, 5615, 9487 | yes, yes, yes (3 ties) | 2342:1.00 | no, no, yes (39 ties) | 33:1.00 | 0 / 0 |
| 19 | 12 | b6 / cxb4 | 3667, 12253, 13516 | yes, yes, yes (3 ties) | 3667:1.00 | no, no, yes (28 ties) | 455:1.00 | 0 / 0 |

- k = 4: planted latent in v at 100% of 20 positions, v planted latents only at 100%, all 3 among the ties at 100%
- k = 0: planted latent in v at 10% of 20 positions, v planted latents only at 10%, all 3 among the ties at 100%

Recovered at k = 4 (planted latent in v at >= 80% of positions): yes

