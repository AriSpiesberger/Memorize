# Planted check (S)

At each of the first 20 positions: one random pair with 4 plies left after the split; 3 latents (off in both lines at plies t..t+4, on at 1-30% of the position's plies) switched on in the chosen line only at plies t..t+4; steps 1-2 rerun (C = 2.0). 'in v': v holds a planted latent; 'only': v is planted latents only; 'ties': all 3 are among the latents that alone separate the window; 'leak': other pairs at that position whose v holds a planted latent.

| position | ply | chosen / subpar | planted | k=4: in v, only, ties | k=4 v | k=0: in v, only, ties | k=0 v | leak k=4 / k=0 |
|---|---|---|---|---|---|---|---|---|
| 0 | 11 | Rxb2+ / cxb2 | 919, 2015, 2639 | yes, yes, yes (3 ties) | 919:1.00 | no, no, yes (28 ties) | 206:1.00 | 0 / 0 |
| 1 | 4 | Nf6 / Nde5 | 49, 737, 3345 | yes, yes, yes (3 ties) | 49:1.00 | no, no, yes (21 ties) | 15:1.00 | 0 / 3 |
| 2 | 9 | d5 / f5 | 2390, 2930, 3946 | no, no, yes (4 ties) | 570:1.00 | no, no, yes (18 ties) | 289:1.00 | 0 / 0 |
| 3 | 8 | Ne3 / b4 | 1104, 3225, 3770 | yes, yes, yes (3 ties) | 1104:1.00 | no, no, yes (22 ties) | 218:1.00 | 0 / 0 |
| 4 | 8 | Bg7 / Bf5 | 124, 2179, 3507 | yes, yes, yes (3 ties) | 124:1.00 | no, no, yes (27 ties) | 101:1.00 | 0 / 1 |
| 5 | 11 | Qh5 / e4 | 407, 723, 3475 | yes, yes, yes (3 ties) | 407:1.00 | no, no, yes (21 ties) | 219:1.00 | 0 / 0 |
| 6 | 4 | Ne3 / g3 | 1230, 1643, 1857 | yes, yes, yes (3 ties) | 1230:1.00 | no, no, yes (21 ties) | 104:1.00 | 0 / 0 |
| 7 | 2 | Kh8 / Kh7 | 21, 455, 2819 | yes, yes, yes (3 ties) | 21:1.00 | yes, yes, yes (10 ties) | 21:1.00 | 2 / 2 |
| 8 | 5 | Nxd2 / Qxd2 | 1533, 2417, 3118 | yes, yes, yes (3 ties) | 1533:1.00 | no, no, yes (19 ties) | 33:1.00 | 1 / 0 |
| 9 | 11 | Ra1 / Nd4 | 1547, 2707, 4016 | yes, yes, yes (3 ties) | 1547:1.00 | no, no, yes (29 ties) | 18:1.00 | 0 / 0 |
| 10 | 12 | b6 / Be8 | 1547, 2735, 2821 | yes, yes, yes (3 ties) | 1547:1.00 | no, no, yes (34 ties) | 19:1.00 | 0 / 0 |
| 11 | 8 | Rac8 / Rxg5 | 2185, 3057, 3538 | yes, yes, yes (3 ties) | 2185:1.00 | no, no, yes (21 ties) | 200:1.00 | 0 / 0 |
| 12 | 8 | Bf4 / Re1 | 1842, 2840, 3637 | yes, yes, yes (3 ties) | 1842:1.00 | no, no, yes (30 ties) | 155:1.00 | 0 / 0 |
| 13 | 10 | a3 / Bd4 | 1418, 2336, 2667 | yes, yes, yes (3 ties) | 1418:1.00 | no, no, yes (16 ties) | 115:1.00 | 0 / 0 |
| 14 | 10 | Qb5 / Qc7 | 1355, 2025, 2400 | yes, yes, yes (3 ties) | 1355:1.00 | no, no, yes (31 ties) | 17:1.00 | 0 / 0 |
| 15 | 7 | Rd8 / Qxc6 | 923, 1080, 3502 | yes, yes, yes (3 ties) | 923:1.00 | no, no, yes (30 ties) | 20:1.00 | 1 / 0 |
| 16 | 3 | Rfe8+ / Nxh1 | 342, 1524, 3475 | yes, yes, yes (3 ties) | 342:1.00 | no, no, yes (33 ties) | 2:1.00 | 0 / 0 |
| 17 | 7 | Re1 / Bf4 | 918, 3202, 3484 | yes, yes, yes (3 ties) | 918:1.00 | no, no, yes (17 ties) | 204:1.00 | 0 / 0 |
| 18 | 9 | Rad1 / Bxc5 | 521, 1354, 2252 | yes, yes, yes (3 ties) | 521:1.00 | no, no, yes (31 ties) | 81:1.00 | 0 / 0 |
| 19 | 12 | b6 / cxb4 | 910, 2884, 3287 | yes, yes, yes (3 ties) | 910:1.00 | no, no, yes (17 ties) | 21:1.00 | 0 / 0 |

- k = 4: planted latent in v at 95% of 20 positions, v planted latents only at 95%, all 3 among the ties at 100%
- k = 0: planted latent in v at 5% of 20 positions, v planted latents only at 5%, all 3 among the ties at 100%

Recovered at k = 4 (planted latent in v at >= 80% of positions): yes

