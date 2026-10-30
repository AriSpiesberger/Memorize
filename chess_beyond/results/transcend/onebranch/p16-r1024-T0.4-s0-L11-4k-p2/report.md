# One position, a few paths: p16-r1024-T0.4-s0-L11-4k, position 2

`r1bqk2r/p2pbp2/2p1p3/3nP1pp/4N3/P7/1PP2PPP/R1BQKB1R b KQkq - 1 11` (2400+ game 1202), Black to move. S's policy: Qc7 28%, f5 26%, g4 23%, f6 4%, c5 4%.

Paths: root moves in >= 10% of the model's rollouts (1,024 at T = 0.4); distinct lines halved per path into train and test; AUC on test lines, weighted by sample count, at each ply tau after the first move. Refit: a probe per tau. Fixed: the probes fit at tau = 2 and 3, each applied at every tau of its parity (the codes differ by side to move). board: one-hot board + side to move (the bar: different first moves give different boards). raw - board, latents - board: minus a ridge read of the board. Same board: test rows of the two paths at the same tau with the same board, each scored by its tau's refit probe (the board cannot separate them).

## S's rollouts

669 distinct lines; paths: Qc7 47%, f5 30%, g4 22%.

### S: Qc7 against f5

| tau | test rows | board | latents on | latents | raw | raw - board | latents - board | fixed: board | fixed: latents on | fixed: latents | fixed: raw | fixed: raw - board | fixed: latents - board |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 236 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 | 1.00 |
| 2 | 236 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 3 | 236 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 4 | 236 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.12 | 1.00 | 1.00 | 0.21 |
| 5 | 236 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.95 | 1.00 | 1.00 | 0.25 |
| 6 | 236 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.95 | 0.88 | 0.64 | 0.94 | 0.85 | 0.83 |
| 7 | 236 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.98 | 0.91 | 0.69 | 0.93 | 0.93 | 0.73 |
| 8 | 236 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.95 | 0.90 | 0.53 | 0.89 | 0.61 | 0.46 |
| 9 | 236 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.98 | 0.86 | 0.40 | 0.88 | 0.78 | 0.51 |
| 10 | 236 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.99 | 0.93 | 0.72 | 0.24 | 0.58 | 0.24 | 0.09 |
| 11 | 236 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.98 | 0.98 | 0.92 | 0.26 | 0.79 | 0.63 | 0.79 |
| 12 | 236 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.99 | 0.92 | 0.49 | 0.32 | 0.36 | 0.47 | 0.40 |
| 13 | 236 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.99 | 0.97 | 0.86 | 0.35 | 0.70 | 0.58 | 0.83 |
| 14 | 236 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.89 | 0.84 | 0.46 | 0.32 | 0.40 | 0.69 | 0.69 |
| 15 | 236 | 1.00 | 1.00 | 0.99 | 1.00 | 1.00 | 0.96 | 0.97 | 0.91 | 0.39 | 0.56 | 0.55 | 0.82 |
| 16 | 236 | 1.00 | 1.00 | 0.99 | 1.00 | 0.99 | 0.95 | 0.84 | 0.56 | 0.35 | 0.27 | 0.60 | 0.50 |

Same board at the same tau: 0 test rows (tau ), each scored by its tau's refit probe.

LP on the two most frequent lines (divergence.py's, window from the first move): k = 0: 286 (1.00), holds on 100% of test line pairs; k = 2: v = 0; k = 4: v = 0; k = 6: v = 0.

Top latents of the refit latents probe at tau = 1 (+: toward Qc7):

| latent | coefficient | best board predicate (phi) | on in Qc7 | on in f5 |
|---|---|---|---|---|
| 895 | +0.10 | White Q on d1 (+0.64) | 29% | 75% |
| 2058 | +0.10 | White P on e5 (+0.63) | 9% | 8% |
| 3783 | -0.10 | Black N on d5 (+0.68) | 13% | 6% |
| 623 | +0.10 | White N on e4 (+0.44) | 14% | 12% |
| 3842 | -0.10 | White to move (+0.78) | 58% | 56% |
| 1204 | +0.10 | Black N on d5 (+0.39) | 7% | 6% |
| 3145 | -0.10 | White to move (+0.50) | 29% | 34% |
| 3097 | -0.10 | White to move (+0.93) | 47% | 48% |

Top latents of the refit latents probe at tau = 6 (+: toward Qc7):

| latent | coefficient | best board predicate (phi) | on in Qc7 | on in f5 |
|---|---|---|---|---|
| 2509 | -0.21 | White P on c2 (+0.47) | 6% | 49% |
| 376 | +0.19 | Black Q on e5 (+0.49) | 38% | 3% |
| 895 | -0.19 | White Q on d1 (+0.64) | 29% | 75% |
| 3450 | -0.19 | White P on c2 (+0.54) | 0% | 43% |
| 1678 | -0.19 | White P on f6 (+0.39) | 4% | 23% |
| 1497 | +0.18 | Black P on g5 (+0.58) | 37% | 8% |
| 1254 | -0.18 | Black N on f6 (+0.36) | 14% | 42% |
| 1520 | -0.17 | Black N on f6 (+0.61) | 0% | 36% |

### S: Qc7 against g4

| tau | test rows | board | latents on | latents | raw | raw - board | latents - board | fixed: board | fixed: latents on | fixed: latents | fixed: raw | fixed: raw - board | fixed: latents - board |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 261 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 2 | 261 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 3 | 261 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 4 | 261 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.87 | 0.64 |
| 5 | 261 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.99 | 1.00 | 1.00 | 0.62 | 1.00 | 1.00 | 0.43 |
| 6 | 261 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.95 | 0.85 | 0.98 | 0.94 | 0.29 |
| 7 | 261 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.60 | 0.99 | 0.95 | 0.51 |
| 8 | 261 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.99 | 0.97 | 0.95 | 0.27 | 0.97 | 0.68 | 0.66 |
| 9 | 261 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.99 | 0.99 | 0.48 | 0.97 | 0.95 | 0.67 |
| 10 | 261 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.88 | 0.79 | 0.48 | 0.91 | 0.69 | 0.59 |
| 11 | 261 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.96 | 0.93 | 0.43 | 0.94 | 0.86 | 0.73 |
| 12 | 261 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.98 | 0.89 | 0.82 | 0.25 | 0.89 | 0.81 | 0.59 |
| 13 | 261 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.99 | 0.94 | 0.90 | 0.38 | 0.92 | 0.81 | 0.73 |
| 14 | 261 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.95 | 0.87 | 0.82 | 0.40 | 0.87 | 0.76 | 0.52 |
| 15 | 261 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.97 | 0.92 | 0.87 | 0.37 | 0.76 | 0.78 | 0.64 |
| 16 | 261 | 1.00 | 1.00 | 1.00 | 1.00 | 0.99 | 0.94 | 0.87 | 0.84 | 0.37 | 0.82 | 0.66 | 0.67 |

Same board at the same tau: 0 test rows (tau ), each scored by its tau's refit probe.

LP on the two most frequent lines (divergence.py's, window from the first move): k = 0: 609 (1.00), holds on 100% of test line pairs; k = 2: v = 0; k = 4: v = 0; k = 6: v = 0.

Top latents of the refit latents probe at tau = 1 (+: toward Qc7):

| latent | coefficient | best board predicate (phi) | on in Qc7 | on in g4 |
|---|---|---|---|---|
| 1272 | +0.14 | Black Q on c7 (+0.36) | 7% | 10% |
| 2024 | +0.14 | Black Q on c7 (+0.41) | 7% | 6% |
| 286 | -0.14 | White to move (+0.37) | 14% | 31% |
| 3842 | -0.14 | White to move (+0.78) | 58% | 51% |
| 1752 | +0.14 | Black P on h4 (+0.33) | 3% | 7% |
| 3285 | +0.14 | Black Q on c7 (+0.34) | 17% | 9% |
| 72 | +0.14 | White to move (+0.73) | 37% | 49% |
| 2147 | +0.14 | White B on c1 (+0.67) | 68% | 63% |

Top latents of the refit latents probe at tau = 6 (+: toward Qc7):

| latent | coefficient | best board predicate (phi) | on in Qc7 | on in g4 |
|---|---|---|---|---|
| 559 | -0.21 | White P on e5 (+0.56) | 9% | 41% |
| 1497 | +0.21 | Black P on g5 (+0.58) | 37% | 1% |
| 3351 | -0.20 | Black P on g4 (+0.64) | 2% | 44% |
| 705 | -0.19 | White P on f6 (+0.26) | 19% | 31% |
| 895 | -0.19 | White Q on d1 (+0.64) | 29% | 57% |
| 3904 | -0.19 | Black N on b6 (+0.40) | 0% | 23% |
| 1599 | -0.18 | White P on e5 (+0.57) | 6% | 35% |
| 376 | +0.18 | Black Q on e5 (+0.49) | 38% | 10% |

### S: f5 against g4

| tau | test rows | board | latents on | latents | raw | raw - board | latents - board | fixed: board | fixed: latents on | fixed: latents | fixed: raw | fixed: raw - board | fixed: latents - board |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 157 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 2 | 157 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 3 | 157 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 4 | 157 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.99 | 1.00 | 0.49 | 0.51 | 1.00 | 1.00 | 0.54 |
| 5 | 157 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.89 | 0.99 | 0.99 | 0.27 |
| 6 | 157 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.92 | 0.28 | 0.90 | 0.97 | 0.85 |
| 7 | 157 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.98 | 0.88 | 0.99 | 0.99 | 0.64 |
| 8 | 157 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.99 | 1.00 | 0.94 | 0.27 | 0.78 | 0.91 | 0.73 |
| 9 | 157 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.98 | 0.62 | 0.98 | 0.99 | 0.83 |
| 10 | 157 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.99 | 1.00 | 0.87 | 0.14 | 0.85 | 0.87 | 0.73 |
| 11 | 157 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.99 | 1.00 | 0.95 | 0.18 | 0.91 | 0.95 | 0.63 |
| 12 | 157 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.96 | 1.00 | 0.85 | 0.14 | 0.90 | 0.84 | 0.79 |
| 13 | 157 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.97 | 1.00 | 0.95 | 0.16 | 0.96 | 0.99 | 0.76 |
| 14 | 157 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.94 | 0.99 | 0.87 | 0.15 | 0.89 | 0.85 | 0.80 |
| 15 | 157 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.98 | 1.00 | 0.96 | 0.26 | 0.95 | 0.94 | 0.77 |
| 16 | 157 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.97 | 0.98 | 0.87 | 0.17 | 0.89 | 0.79 | 0.56 |

Same board at the same tau: 0 test rows (tau ), each scored by its tau's refit probe.

LP on the two most frequent lines (divergence.py's, window from the first move): k = 0: 19 (1.00), holds on 100% of test line pairs; k = 2: v = 0; k = 4: 1382 (1.00), 2589 (1.00), holds on 56% of test line pairs; k = 6: v = 0.

Top latents of the refit latents probe at tau = 1 (+: toward f5):

| latent | coefficient | best board predicate (phi) | on in f5 | on in g4 |
|---|---|---|---|---|
| 72 | -0.12 | White to move (+0.73) | 22% | 49% |
| 480 | -0.12 | White N on e4 (+0.65) | 12% | 23% |
| 3378 | -0.12 | Black N on d5 (+0.54) | 6% | 13% |
| 2009 | +0.12 | White N on e4 (+0.33) | 13% | 4% |
| 3744 | +0.12 | Black Q on d8 (+0.32) | 27% | 4% |
| 3124 | -0.12 | White P on e5 (+0.52) | 0% | 27% |
| 4003 | +0.12 | White to move (+0.50) | 23% | 12% |
| 1697 | +0.12 | White N on g5 (+0.42) | 19% | 2% |

Top latents of the refit latents probe at tau = 6 (+: toward f5):

| latent | coefficient | best board predicate (phi) | on in f5 | on in g4 |
|---|---|---|---|---|
| 2509 | +0.23 | White P on c2 (+0.47) | 49% | 1% |
| 3351 | -0.22 | Black P on g4 (+0.64) | 0% | 44% |
| 559 | -0.21 | White P on e5 (+0.56) | 1% | 41% |
| 1678 | +0.20 | White P on f6 (+0.39) | 23% | 8% |
| 3450 | +0.20 | White P on c2 (+0.54) | 43% | 1% |
| 2284 | +0.19 | Black P on g5 (+0.44) | 7% | 0% |
| 3904 | -0.18 | Black N on b6 (+0.40) | 0% | 23% |
| 1599 | -0.18 | White P on e5 (+0.57) | 0% | 35% |

## W's rollouts

914 distinct lines; paths: g4 73%, Bb7 12%.

### W: g4 against Bb7

| tau | test rows | board | latents on | latents | raw | raw - board | latents - board | fixed: board | fixed: latents on | fixed: latents | fixed: raw | fixed: raw - board | fixed: latents - board |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 385 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 2 | 385 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 3 | 385 | 1.00 | 1.00 | 0.99 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.99 | 1.00 | 1.00 | 1.00 |
| 4 | 385 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.98 | 0.92 | 0.98 | 0.98 | 0.77 |
| 5 | 385 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.99 | 0.94 | 0.87 | 0.95 | 0.99 | 0.93 |
| 6 | 385 | 0.99 | 1.00 | 1.00 | 1.00 | 1.00 | 0.99 | 0.98 | 0.95 | 0.90 | 0.96 | 0.95 | 0.81 |
| 7 | 385 | 0.99 | 0.95 | 0.94 | 0.98 | 0.99 | 0.84 | 0.99 | 0.90 | 0.82 | 0.93 | 0.99 | 0.83 |
| 8 | 385 | 0.98 | 0.96 | 0.96 | 0.98 | 0.97 | 0.96 | 0.97 | 0.89 | 0.79 | 0.93 | 0.91 | 0.65 |
| 9 | 385 | 0.99 | 0.96 | 0.95 | 0.98 | 0.98 | 0.94 | 0.97 | 0.86 | 0.78 | 0.92 | 0.97 | 0.78 |
| 10 | 385 | 0.99 | 0.98 | 0.97 | 0.99 | 0.98 | 0.97 | 0.96 | 0.91 | 0.77 | 0.93 | 0.89 | 0.59 |
| 11 | 385 | 0.99 | 0.96 | 0.94 | 0.96 | 0.97 | 0.93 | 0.97 | 0.86 | 0.76 | 0.90 | 0.94 | 0.63 |
| 12 | 385 | 0.97 | 0.96 | 0.94 | 0.97 | 0.95 | 0.92 | 0.94 | 0.89 | 0.76 | 0.91 | 0.87 | 0.70 |
| 13 | 384 | 0.97 | 0.92 | 0.90 | 0.97 | 0.96 | 0.91 | 0.95 | 0.86 | 0.68 | 0.89 | 0.93 | 0.63 |
| 14 | 384 | 0.95 | 0.93 | 0.90 | 0.97 | 0.95 | 0.91 | 0.93 | 0.92 | 0.75 | 0.91 | 0.89 | 0.57 |
| 15 | 384 | 0.94 | 0.87 | 0.86 | 0.93 | 0.93 | 0.89 | 0.94 | 0.78 | 0.64 | 0.83 | 0.89 | 0.60 |
| 16 | 384 | 0.92 | 0.88 | 0.86 | 0.96 | 0.88 | 0.83 | 0.91 | 0.87 | 0.68 | 0.89 | 0.82 | 0.53 |

Same board at the same tau: 195 test rows (tau 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16), each scored by its tau's refit probe: latents on 0.74, latents 0.83, raw 0.85, raw - board 0.77, latents - board 0.81.

LP on the two most frequent lines (divergence.py's, window from the first move): k = 0: 157 (1.00), holds on 100% of test line pairs; k = 2: v = 0; k = 4: v = 0; k = 6: v = 0.

Top latents of the refit latents probe at tau = 1 (+: toward g4):

| latent | coefficient | best board predicate (phi) | on in g4 | on in Bb7 |
|---|---|---|---|---|
| 3378 | -0.11 | Black N on d5 (+0.47) | 18% | 13% |
| 3515 | +0.11 | White to move (+0.97) | 49% | 50% |
| 72 | +0.11 | White to move (+0.90) | 45% | 42% |
| 3784 | +0.11 | Black Q on d8 (+0.45) | 20% | 20% |
| 2593 | +0.11 | White to move (+0.51) | 22% | 13% |
| 2058 | -0.11 | White to move (+0.78) | 39% | 30% |
| 4003 | -0.11 | White to move (+0.49) | 20% | 18% |
| 1752 | +0.11 | White Q on g4 (+0.36) | 10% | 3% |

Top latents of the refit latents probe at tau = 6 (+: toward g4):

| latent | coefficient | best board predicate (phi) | on in g4 | on in Bb7 |
|---|---|---|---|---|
| 357 | -0.93 | White K on h2 (+0.12) | 1% | 1% |
| 1497 | -0.69 | Black P on g5 (+0.66) | 0% | 27% |
| 3109 | -0.61 | Black P on g5 (+0.52) | 1% | 22% |
| 2284 | -0.55 | Black P on g5 (+0.52) | 0% | 18% |
| 3351 | +0.49 | Black P on g4 (+0.45) | 41% | 5% |
| 4011 | -0.40 | White to move (+0.43) | 27% | 28% |
| 2058 | -0.39 | White to move (+0.78) | 39% | 30% |
| 2585 | -0.33 | Black P on g5 (+0.07) | 0% | 0% |

