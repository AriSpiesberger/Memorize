# Dynamic concepts with a persistence window

Per model, at 50 positions (1024 rollouts of 16 plies, T = 0.4, the model both colours): a latent on at a ply when z > 0.5 x mu_j. Pairs: at each branching point the most-played move against every move with >= 2% of that point's weight, each by its most frequent line, <= 50 per position. LP: min |v|_1 + 2.0 xi s.t. v . (z^c_tau - z^s_tau) >= 1 - xi for tau = t..t+k. Families: Jaccard >= 0.5 of supports with a family's core, within one half (25 / 25 positions by game); recurrence: the share of the other half's pairs (same k) where the family's mean v (|v|_1 = 1) gives >= 0.5 on every ply of the window; null: 200 random v's per family on rate-matched latents (firing-rate deciles). Persistence: plies in a row from the split with v . d >= 0.5, median over the other half's k = 0 pairs where it is on at the split.

## S

| k | pairs | nonzero v | families | held-out recurrence: median / 90% / max | null 95th: median | null (every draw): 90% / 99% | families above their null 95th (chance: 5%) |
|---|---|---|---|---|---|---|---|
| 0 | 1247 | 100% | 437 | 0.8% / 2.8% / 8.5% | 2.1% | 2.4% / 5.8% | 27 (6%) |
| 2 | 1217 | 31% | 312 | 0.0% / 0.2% / 0.8% | 0.0% | 0.0% / 0.3% | 31 (10%) |
| 4 | 1122 | 17% | 172 | 0.0% / 0.2% / 1.2% | 0.0% | 0.0% / 0.2% | 22 (13%) |
| 6 | 995 | 13% | 113 | 0.0% / 0.2% / 0.8% | 0.0% | 0.0% / 0.2% | 16 (14%) |

### S: the top 20 families by held-out recurrence

| # | k | latents (weight) | found in | held out on | recurrence | null 95th | persistence (pairs on at split) | positions found |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 19 (1.00) | B (27 v's) | A | 8.5% | 5.3% | 1.0 (53) | 2, 4, 10, 12, 13, 21, 22, 23, 27, 30, 39, 40 ... |
| 2 | 0 | 532 (1.00) | B (4 v's) | A | 6.9% | 5.7% | 1.0 (43) | 2, 30, 39 |
| 3 | 0 | 49 (1.00) | A (25 v's) | B | 6.8% | 5.2% | 1.0 (42) | 0, 7, 18, 19, 24, 25, 26, 28, 29, 34, 35, 49 |
| 4 | 0 | 532 (1.00) | A (7 v's) | B | 6.8% | 5.2% | 1.0 (42) | 24, 37, 45, 49 |
| 5 | 0 | 705 (1.00) | A (2 v's) | B | 5.8% | 5.2% | 1.0 (36) | 18, 38 |
| 6 | 0 | 572 (1.00) | A (2 v's) | B | 5.8% | 5.7% | 1.0 (36) | 20, 34 |
| 7 | 0 | 556 (1.00) | A (1 v's) | B | 5.8% | 5.5% | 1.0 (36) | 25 |
| 8 | 0 | 570 (1.00) | A (1 v's) | B | 5.6% | 4.8% | 1.0 (35) | 7 |
| 9 | 0 | 705 (1.00) | B (1 v's) | A | 5.6% | 5.1% | 1.0 (35) | 40 |
| 10 | 0 | 49 (1.00) | B (31 v's) | A | 5.4% | 5.4% | 1.0 (34) | 8, 12, 15, 21, 22, 27, 36, 39, 40, 41, 43, 44 ... |
| 11 | 0 | 19 (1.00) | A (48 v's) | B | 5.3% | 5.2% | 1.0 (33) | 0, 3, 5, 6, 9, 16, 19, 20, 24, 25, 26, 31 ... |
| 12 | 0 | 570 (1.00) | B (2 v's) | A | 5.3% | 4.9% | 1.0 (33) | 21, 48 |
| 13 | 0 | 960 (1.00) | A (2 v's) | B | 4.7% | 5.3% | 1.0 (29) | 0, 19 |
| 14 | 0 | 282 (1.00) | A (1 v's) | B | 4.7% | 5.2% | 1.0 (29) | 5 |
| 15 | 0 | 498 (1.00) | A (1 v's) | B | 4.4% | 5.2% | 1.0 (27) | 35 |
| 16 | 0 | 1153 (1.00) | A (1 v's) | B | 4.4% | 4.7% | 1.0 (27) | 38 |
| 17 | 0 | 833 (1.00) | B (2 v's) | A | 4.1% | 5.1% | 1.0 (26) | 1, 30 |
| 18 | 0 | 206 (1.00) | B (3 v's) | A | 4.1% | 2.1% | 1.0 (26) | 4, 40, 44 |
| 19 | 0 | 619 (1.00) | B (2 v's) | A | 4.1% | 5.9% | 1.0 (26) | 17, 30 |
| 20 | 0 | 255 (1.00) | B (4 v's) | A | 4.0% | 2.2% | 1.0 (25) | 8, 15, 21 |

#### S #1 (k = 0): latents 19

position 33 (`r2qk1r1/3bbpnp/p3N1p1/2ppB1P1/1p2P2P/1P3Q2/P1P2P2/2KR1B1R b q - 0 19`), split at ply 6: d6 (78% there) vs Rxd4 (22%)

| chosen | subpar |
|---|---|
| [19...Nxe6] [20.exd5] [Nd4] 21.Bxd4 cxd4 [22.d6] Bxd6 23.Qe4+ Kf8 24.Qxd4 Be7 25.Qxd7 Qxd7 26.Rxd7 Rd8 27.Rxd8+ | [19...Nxe6] [20.exd5] [Nd4] 21.Bxd4 cxd4 22.Rxd4 Qb6 23.Re4 Kf8 24.Bc4 Bd6 25.h5 Bf5 26.Re2 [Qd4] [27.hxg6] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.Bf4%20a6%204.e3%20e6%205.g4%20Bb4%206.Ne2%20Be7%207.g5%20Nh5%208.h4%20b5%209.Bh2%20Nc6%2010.Nc1%20g6%2011.Nb3%20Ng7%2012.Qf3%20b4%2013.Na4%20Bd7%2014.O-O-O%20Nxd4%2015.Nxd4%20Bxa4%2016.Be5%20Rg8%2017.e4%20c5%2018.b3%20Bd7%2019.Nxe6%20Nxe6%2020.exd5%20Nd4%2021.Bxd4%20cxd4%2022.d6%20Bxd6%2023.Qe4%2B%20Kf8%2024.Qxd4%20Be7%2025.Qxd7%20Qxd7%2026.Rxd7%20Rd8%2027.Rxd8%2B#37) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.Bf4%20a6%204.e3%20e6%205.g4%20Bb4%206.Ne2%20Be7%207.g5%20Nh5%208.h4%20b5%209.Bh2%20Nc6%2010.Nc1%20g6%2011.Nb3%20Ng7%2012.Qf3%20b4%2013.Na4%20Bd7%2014.O-O-O%20Nxd4%2015.Nxd4%20Bxa4%2016.Be5%20Rg8%2017.e4%20c5%2018.b3%20Bd7%2019.Nxe6%20Nxe6%2020.exd5%20Nd4%2021.Bxd4%20cxd4%2022.Rxd4%20Qb6%2023.Re4%20Kf8%2024.Bc4%20Bd6%2025.h5%20Bf5%2026.Re2%20Qd4%2027.hxg6#37) |

position 31 (`5r2/5k2/p2q1p1r/1pn4p/8/P1N2Q1P/1P3PP1/3RR1K1 b - - 3 25`), split at ply 14: Ne7+ (78% there) vs Qxh5 (22%)

| chosen | subpar |
|---|---|
| 25...Qc7 26.Nd5 Qb7 27.b4 Ne6 28.Rxe6 Kxe6 29.Re1+ Kf7 [30.Re7+] Kg8 31.Rxb7 Rg6 [32.Ne7+] Kf7 33.Nxg6+ | 25...Qc7 26.Nd5 Qb7 27.b4 Ne6 28.Rxe6 Kxe6 29.Re1+ Kf7 [30.Re7+] Kg8 31.Rxb7 Rg6 32.Qxh5 Rg7 [33.Rxg7+] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.Bb5%20Qc7%204.O-O%20e6%205.Re1%20h5%206.c3%20Nf6%207.d4%20cxd4%208.cxd4%20a6%209.Bf1%20Ng4%2010.h3%20f6%2011.Nc3%20b5%2012.a3%20Bb7%2013.e5%20Nh6%2014.Bxh6%20Rxh6%2015.exf6%20gxf6%2016.d5%20Nd8%2017.Nd4%20Kf7%2018.Be2%20Qe5%2019.Bf3%20Qf4%2020.dxe6%2B%20dxe6%2021.Bxb7%20Nxb7%2022.Nxe6%20Qd6%2023.Nxf8%20Rxf8%2024.Qf3%20Nc5%2025.Rad1%20Qc7%2026.Nd5%20Qb7%2027.b4%20Ne6%2028.Rxe6%20Kxe6%2029.Re1%2B%20Kf7%2030.Re7%2B%20Kg8%2031.Rxb7%20Rg6%2032.Ne7%2B%20Kf7%2033.Nxg6%2B#49) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.Bb5%20Qc7%204.O-O%20e6%205.Re1%20h5%206.c3%20Nf6%207.d4%20cxd4%208.cxd4%20a6%209.Bf1%20Ng4%2010.h3%20f6%2011.Nc3%20b5%2012.a3%20Bb7%2013.e5%20Nh6%2014.Bxh6%20Rxh6%2015.exf6%20gxf6%2016.d5%20Nd8%2017.Nd4%20Kf7%2018.Be2%20Qe5%2019.Bf3%20Qf4%2020.dxe6%2B%20dxe6%2021.Bxb7%20Nxb7%2022.Nxe6%20Qd6%2023.Nxf8%20Rxf8%2024.Qf3%20Nc5%2025.Rad1%20Qc7%2026.Nd5%20Qb7%2027.b4%20Ne6%2028.Rxe6%20Kxe6%2029.Re1%2B%20Kf7%2030.Re7%2B%20Kg8%2031.Rxb7%20Rg6%2032.Qxh5%20Rg7%2033.Rxg7%2B#49) |

position 37 (`2r2k1r/1p1B1p1p/p5p1/2PpP3/6P1/P3q3/1P1NN1P1/n2K3Q w - - 2 26`), split at ply 6: Rb8 (78% there) vs Qxb2 (22%)

| chosen | subpar |
|---|---|
| [26.Bxc8] Qxe5 [27.Qh6+] Ke7 [28.Bxb7] [Rb8] 29.c6 Nb3 [30.c7] [Qxc7] [31.Bxd5] Nxd2 32.Kxd2 Rxb2+ 33.Ke3 Qe5+ | [26.Bxc8] Qxe5 [27.Qh6+] Ke7 [28.Bxb7] Qxb2 [29.Bxd5] [Rd8] [30.Qe3+] [Kf8] [31.Qh6+] [Ke7] [32.Qe3+] [Kf8] [33.Qh6+] [Ke7] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20e6%203.e3%20Bd6%204.Bg3%20Bxg3%205.hxg3%20Nc6%206.c4%20Nge7%207.a3%20Bd7%208.Qg4%20g6%209.Qg5%20Nf5%2010.Qf4%20Qe7%2011.g4%20Nd6%2012.c5%20Ne4%2013.Qxc7%20Bc8%2014.Qf4%20e5%2015.Qh6%20Bxg4%2016.f3%20Ng3%2017.fxg4%20Nxh1%2018.Qxh1%20Qg5%2019.Be2%20Qxe3%2020.dxe5%20Nd4%2021.Nd2%20Nc2%2B%2022.Kd1%20Nxa1%2023.Bb5%2B%20Kf8%2024.Ne2%20a6%2025.Bd7%20Rc8%2026.Bxc8%20Qxe5%2027.Qh6%2B%20Ke7%2028.Bxb7%20Rb8%2029.c6%20Nb3%2030.c7%20Qxc7%2031.Bxd5%20Nxd2%2032.Kxd2%20Rxb2%2B%2033.Ke3%20Qe5%2B#50) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20e6%203.e3%20Bd6%204.Bg3%20Bxg3%205.hxg3%20Nc6%206.c4%20Nge7%207.a3%20Bd7%208.Qg4%20g6%209.Qg5%20Nf5%2010.Qf4%20Qe7%2011.g4%20Nd6%2012.c5%20Ne4%2013.Qxc7%20Bc8%2014.Qf4%20e5%2015.Qh6%20Bxg4%2016.f3%20Ng3%2017.fxg4%20Nxh1%2018.Qxh1%20Qg5%2019.Be2%20Qxe3%2020.dxe5%20Nd4%2021.Nd2%20Nc2%2B%2022.Kd1%20Nxa1%2023.Bb5%2B%20Kf8%2024.Ne2%20a6%2025.Bd7%20Rc8%2026.Bxc8%20Qxe5%2027.Qh6%2B%20Ke7%2028.Bxb7%20Qxb2%2029.Bxd5%20Rd8%2030.Qe3%2B%20Kf8%2031.Qh6%2B%20Ke7%2032.Qe3%2B%20Kf8%2033.Qh6%2B%20Ke7#50) |

#### S #2 (k = 0): latents 532

position 37 (`2r2k1r/1p1B1p1p/p5p1/2PpP3/6P1/P3q3/1P1NN1P1/n2K3Q w - - 2 26`), split at ply 8: Rb8 (75% there) vs Qc4+ (25%)

| chosen | subpar |
|---|---|
| 26.Bxc8 [Kg7] 27.Bxb7 [Nb3] 28.Nxb3 Qxb3+ 29.Kc1 [Rb8] 30.c6 Qxb2+ 31.Kd1 Qb1+ 32.Nc1 Qe4 33.Qe1 Qxg4+ | 26.Bxc8 [Kg7] 27.Bxb7 [Nb3] 28.Nxb3 Qxb3+ 29.Kc1 Qc4+ 30.Nc3 Qxc5 31.Bxd5 Qe3+ 32.Kb1 Qxe5 33.Qf1 Rf8 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20e6%203.e3%20Bd6%204.Bg3%20Bxg3%205.hxg3%20Nc6%206.c4%20Nge7%207.a3%20Bd7%208.Qg4%20g6%209.Qg5%20Nf5%2010.Qf4%20Qe7%2011.g4%20Nd6%2012.c5%20Ne4%2013.Qxc7%20Bc8%2014.Qf4%20e5%2015.Qh6%20Bxg4%2016.f3%20Ng3%2017.fxg4%20Nxh1%2018.Qxh1%20Qg5%2019.Be2%20Qxe3%2020.dxe5%20Nd4%2021.Nd2%20Nc2%2B%2022.Kd1%20Nxa1%2023.Bb5%2B%20Kf8%2024.Ne2%20a6%2025.Bd7%20Rc8%2026.Bxc8%20Kg7%2027.Bxb7%20Nb3%2028.Nxb3%20Qxb3%2B%2029.Kc1%20Rb8%2030.c6%20Qxb2%2B%2031.Kd1%20Qb1%2B%2032.Nc1%20Qe4%2033.Qe1%20Qxg4%2B#50) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20e6%203.e3%20Bd6%204.Bg3%20Bxg3%205.hxg3%20Nc6%206.c4%20Nge7%207.a3%20Bd7%208.Qg4%20g6%209.Qg5%20Nf5%2010.Qf4%20Qe7%2011.g4%20Nd6%2012.c5%20Ne4%2013.Qxc7%20Bc8%2014.Qf4%20e5%2015.Qh6%20Bxg4%2016.f3%20Ng3%2017.fxg4%20Nxh1%2018.Qxh1%20Qg5%2019.Be2%20Qxe3%2020.dxe5%20Nd4%2021.Nd2%20Nc2%2B%2022.Kd1%20Nxa1%2023.Bb5%2B%20Kf8%2024.Ne2%20a6%2025.Bd7%20Rc8%2026.Bxc8%20Kg7%2027.Bxb7%20Nb3%2028.Nxb3%20Qxb3%2B%2029.Kc1%20Qc4%2B%2030.Nc3%20Qxc5%2031.Bxd5%20Qe3%2B%2032.Kb1%20Qxe5%2033.Qf1%20Rf8#50) |

position 24 (`3r2k1/pp4p1/2n1b2p/8/3p2q1/8/PPQB1PP1/4RRK1 w - - 2 25`), split at ply 15: f3 (76% there) vs Rc7 (24%)

| chosen | subpar |
|---|---|
| 25.Qe4 Qxe4 [26.Rxe4] Bxa2 [27.Rfe1] Bd5 28.Re8+ Rxe8 29.Rxe8+ Kf7 [30.Rc8] Ke6 [31.b4] a6 [32.f3] [Ne5] | 25.Qe4 Qxe4 [26.Rxe4] Bxa2 [27.Rfe1] Bd5 28.Re8+ Rxe8 29.Rxe8+ Kf7 [30.Rc8] Ke6 [31.b4] a6 32.Rc7 b5 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e6%202.d4%20d5%203.Nd2%20Nf6%204.e5%20Nfd7%205.Bd3%20c5%206.c3%20Nc6%207.Ne2%20cxd4%208.cxd4%20f6%209.exf6%20Qxf6%2010.Nf3%20h6%2011.O-O%20Bd6%2012.Ng3%20O-O%2013.Bd2%20e5%2014.dxe5%20Ndxe5%2015.Nxe5%20Bxe5%2016.Qc2%20Be6%2017.Rae1%20Rae8%2018.Nh5%20Bxh2%2B%2019.Kxh2%20Qh4%2B%2020.Kg1%20Qxh5%2021.Bg6%20Qg4%2022.Bxe8%20Rxe8%2023.Bc3%20d4%2024.Bd2%20Rd8%2025.Qe4%20Qxe4%2026.Rxe4%20Bxa2%2027.Rfe1%20Bd5%2028.Re8%2B%20Rxe8%2029.Rxe8%2B%20Kf7%2030.Rc8%20Ke6%2031.b4%20a6%2032.f3%20Ne5#48) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e6%202.d4%20d5%203.Nd2%20Nf6%204.e5%20Nfd7%205.Bd3%20c5%206.c3%20Nc6%207.Ne2%20cxd4%208.cxd4%20f6%209.exf6%20Qxf6%2010.Nf3%20h6%2011.O-O%20Bd6%2012.Ng3%20O-O%2013.Bd2%20e5%2014.dxe5%20Ndxe5%2015.Nxe5%20Bxe5%2016.Qc2%20Be6%2017.Rae1%20Rae8%2018.Nh5%20Bxh2%2B%2019.Kxh2%20Qh4%2B%2020.Kg1%20Qxh5%2021.Bg6%20Qg4%2022.Bxe8%20Rxe8%2023.Bc3%20d4%2024.Bd2%20Rd8%2025.Qe4%20Qxe4%2026.Rxe4%20Bxa2%2027.Rfe1%20Bd5%2028.Re8%2B%20Rxe8%2029.Rxe8%2B%20Kf7%2030.Rc8%20Ke6%2031.b4%20a6%2032.Rc7%20b5#48) |

position 26 (`r1b1r1k1/2p3bp/2p2pq1/2Np4/p5P1/P1Q1B3/1PP2P1P/1K1R2R1 w - - 3 24`), split at ply 4: f5 (76% there) vs fxg5 (24%)

| chosen | subpar |
|---|---|
| 24.h4 Rb8 25.g5 [f5] 26.Bd4 Bxd4 27.Qxd4 Qd6 [28.g6] h6 29.g7 Qe5 30.Qxe5 Rxe5 31.Rde1 Rxe1+ | 24.h4 Rb8 25.g5 fxg5 26.Rxg5 [Qf6] 27.Bd4 [Qxd4] 28.Rxd4 [Re1+] 29.Qxe1 Bf5 [30.Rxf5] [Rxb2+] 31.Kxb2 [Bxd4+] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.h4%20Rb8%2025.g5%20f5%2026.Bd4%20Bxd4%2027.Qxd4%20Qd6%2028.g6%20h6%2029.g7%20Qe5%2030.Qxe5%20Rxe5%2031.Rde1%20Rxe1%2B#46) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.h4%20Rb8%2025.g5%20fxg5%2026.Rxg5%20Qf6%2027.Bd4%20Qxd4%2028.Rxd4%20Re1%2B%2029.Qxe1%20Bf5%2030.Rxf5%20Rxb2%2B%2031.Kxb2%20Bxd4%2B#46) |

#### S #3 (k = 0): latents 49

position 48 (`r4r1k/1ppqn2p/p5p1/4pP2/2Pp2P1/3PbRNP/PP4BK/R2Q4 b - - 1 21`), split at ply 14: Rf3 (75% there) vs Qe4 (25%)

| chosen | subpar |
|---|---|
| 21...gxf5 22.gxf5 [Rxf5] 23.Nxf5 Nxf5 24.Qe2 Rg8 25.Raf1 Bf4+ 26.Kh1 Ng3+ 27.Rxg3 Rxg3 [28.Rf3] Rxf3 29.Qxf3 | 21...gxf5 22.gxf5 [Rxf5] 23.Nxf5 Nxf5 24.Qe2 Rg8 25.Raf1 Bf4+ 26.Kh1 Ng3+ 27.Rxg3 Rxg3 28.Qe4 c6 29.Rxf4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nc3%20e5%203.g3%20Bc5%204.Bg2%20a6%205.Nge2%20Nge7%206.h3%20d6%207.d3%20O-O%208.O-O%20Be6%209.Kh2%20f5%2010.f4%20Qd7%2011.exf5%20Nxf5%2012.g4%20Ne3%2013.Bxe3%20Bxe3%2014.f5%20Bf7%2015.Nd5%20Bxd5%2016.Bxd5%2B%20Kh8%2017.Bg2%20d5%2018.c3%20Ne7%2019.Rf3%20d4%2020.c4%20g6%2021.Ng3%20gxf5%2022.gxf5%20Rxf5%2023.Nxf5%20Nxf5%2024.Qe2%20Rg8%2025.Raf1%20Bf4%2B%2026.Kh1%20Ng3%2B%2027.Rxg3%20Rxg3%2028.Rf3%20Rxf3%2029.Qxf3#41) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nc3%20e5%203.g3%20Bc5%204.Bg2%20a6%205.Nge2%20Nge7%206.h3%20d6%207.d3%20O-O%208.O-O%20Be6%209.Kh2%20f5%2010.f4%20Qd7%2011.exf5%20Nxf5%2012.g4%20Ne3%2013.Bxe3%20Bxe3%2014.f5%20Bf7%2015.Nd5%20Bxd5%2016.Bxd5%2B%20Kh8%2017.Bg2%20d5%2018.c3%20Ne7%2019.Rf3%20d4%2020.c4%20g6%2021.Ng3%20gxf5%2022.gxf5%20Rxf5%2023.Nxf5%20Nxf5%2024.Qe2%20Rg8%2025.Raf1%20Bf4%2B%2026.Kh1%20Ng3%2B%2027.Rxg3%20Rxg3%2028.Qe4%20c6%2029.Rxf4#41) |

position 27 (`r3kb1r/1p2pp1p/p2p1np1/4n1Q1/3B4/PP2P3/2qPNPPP/R4RK1 b kq - 1 15`), split at ply 7: Qf5 (77% there) vs Qxb3 (23%)

| chosen | subpar |
|---|---|
| 15...Qxd2 16.Nf4 Bg7 [17.Rfd1] Qc2 [18.Rac1] [Qf5] 19.Qg3 O-O 20.Rc7 Ne4 21.Qh4 g5 [22.Qh5] gxf4 23.exf4 | 15...Qxd2 16.Nf4 Bg7 [17.Rfd1] Qc2 [18.Rac1] Qxb3 [19.Rb1] Qc2 [20.Rdc1] [Qf5] 21.Qg3 b5 22.a4 O-O 23.axb5 |
| [Lichess](https://lichess.org/analysis/pgn/1.e3%20c5%202.Qh5%20Nf6%203.Qxc5%20g6%204.Bc4%20d6%205.Qg5%20Nc6%206.a3%20Ne5%207.Bb5%2B%20Bd7%208.Ba4%20Bxa4%209.b3%20Bd7%2010.Bb2%20Qc7%2011.Nc3%20a6%2012.Nge2%20Bb5%2013.O-O%20Bxe2%2014.Nxe2%20Qxc2%2015.Bd4%20Qxd2%2016.Nf4%20Bg7%2017.Rfd1%20Qc2%2018.Rac1%20Qf5%2019.Qg3%20O-O%2020.Rc7%20Ne4%2021.Qh4%20g5%2022.Qh5%20gxf4%2023.exf4#29) | [Lichess](https://lichess.org/analysis/pgn/1.e3%20c5%202.Qh5%20Nf6%203.Qxc5%20g6%204.Bc4%20d6%205.Qg5%20Nc6%206.a3%20Ne5%207.Bb5%2B%20Bd7%208.Ba4%20Bxa4%209.b3%20Bd7%2010.Bb2%20Qc7%2011.Nc3%20a6%2012.Nge2%20Bb5%2013.O-O%20Bxe2%2014.Nxe2%20Qxc2%2015.Bd4%20Qxd2%2016.Nf4%20Bg7%2017.Rfd1%20Qc2%2018.Rac1%20Qxb3%2019.Rb1%20Qc2%2020.Rdc1%20Qf5%2021.Qg3%20b5%2022.a4%20O-O%2023.axb5#29) |

position 8 (`r2qkb1r/pp3ppp/4pn2/8/b1pP4/PnP1PN1P/R1Q2PP1/1NB1KB1R w Kkq - 6 12`), split at ply 6: Rc8 (78% there) vs O-O (19%)

| chosen | subpar |
|---|---|
| 12.Qb2 Bd6 13.Bxc4 Nxc1 14.Qxc1 [Rc8] 15.Bd3 O-O 16.O-O Qc7 17.c4 b5 18.c5 Be7 19.Nc3 a6 | 12.Qb2 Bd6 13.Bxc4 Nxc1 14.Qxc1 O-O 15.O-O [Rc8] 16.Nbd2 b5 17.Bb3 Bxb3 18.Nxb3 Nd5 19.Rc2 Nb6 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Qb2%20Bd6%2013.Bxc4%20Nxc1%2014.Qxc1%20Rc8%2015.Bd3%20O-O%2016.O-O%20Qc7%2017.c4%20b5%2018.c5%20Be7%2019.Nc3%20a6#22) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Qb2%20Bd6%2013.Bxc4%20Nxc1%2014.Qxc1%20O-O%2015.O-O%20Rc8%2016.Nbd2%20b5%2017.Bb3%20Bxb3%2018.Nxb3%20Nd5%2019.Rc2%20Nb6#22) |

#### S #4 (k = 0): latents 532

position 48 (`r4r1k/1ppqn2p/p5p1/4pP2/2Pp2P1/3PbRNP/PP4BK/R2Q4 b - - 1 21`), split at ply 14: Rf3 (75% there) vs Qe4 (25%)

| chosen | subpar |
|---|---|
| 21...gxf5 22.gxf5 Rxf5 23.Nxf5 Nxf5 24.Qe2 Rg8 25.Raf1 Bf4+ 26.Kh1 Ng3+ 27.Rxg3 Rxg3 [28.Rf3] Rxf3 29.Qxf3 | 21...gxf5 22.gxf5 Rxf5 23.Nxf5 Nxf5 24.Qe2 Rg8 25.Raf1 Bf4+ 26.Kh1 Ng3+ 27.Rxg3 Rxg3 28.Qe4 c6 [29.Rxf4] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nc3%20e5%203.g3%20Bc5%204.Bg2%20a6%205.Nge2%20Nge7%206.h3%20d6%207.d3%20O-O%208.O-O%20Be6%209.Kh2%20f5%2010.f4%20Qd7%2011.exf5%20Nxf5%2012.g4%20Ne3%2013.Bxe3%20Bxe3%2014.f5%20Bf7%2015.Nd5%20Bxd5%2016.Bxd5%2B%20Kh8%2017.Bg2%20d5%2018.c3%20Ne7%2019.Rf3%20d4%2020.c4%20g6%2021.Ng3%20gxf5%2022.gxf5%20Rxf5%2023.Nxf5%20Nxf5%2024.Qe2%20Rg8%2025.Raf1%20Bf4%2B%2026.Kh1%20Ng3%2B%2027.Rxg3%20Rxg3%2028.Rf3%20Rxf3%2029.Qxf3#41) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nc3%20e5%203.g3%20Bc5%204.Bg2%20a6%205.Nge2%20Nge7%206.h3%20d6%207.d3%20O-O%208.O-O%20Be6%209.Kh2%20f5%2010.f4%20Qd7%2011.exf5%20Nxf5%2012.g4%20Ne3%2013.Bxe3%20Bxe3%2014.f5%20Bf7%2015.Nd5%20Bxd5%2016.Bxd5%2B%20Kh8%2017.Bg2%20d5%2018.c3%20Ne7%2019.Rf3%20d4%2020.c4%20g6%2021.Ng3%20gxf5%2022.gxf5%20Rxf5%2023.Nxf5%20Nxf5%2024.Qe2%20Rg8%2025.Raf1%20Bf4%2B%2026.Kh1%20Ng3%2B%2027.Rxg3%20Rxg3%2028.Qe4%20c6%2029.Rxf4#41) |

position 2 (`r1bqk2r/p2pbp2/2p1p3/3nP1pp/4N3/P7/1PP2PPP/R1BQKB1R b KQkq - 1 11`), split at ply 12: b4 (76% there) vs Bd2 (24%)

| chosen | subpar |
|---|---|
| 11...f5 12.exf6 Nxf6 13.Nxg5 d5 14.Bd3 e5 15.Bg6+ Kf8 16.Nf7 Qa5+ [17.b4] Qc7 18.Nxh8 Kg7 19.Nf7 | 11...f5 12.exf6 Nxf6 13.Nxg5 d5 14.Bd3 e5 15.Bg6+ Kf8 16.Nf7 Qa5+ 17.Bd2 Qc7 18.Nxh8 Kg7 19.Nf7 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.a3%20Be7%207.Nxc6%20bxc6%208.e5%20Nd5%209.Qg4%20g5%2010.Ne4%20h5%2011.Qd1%20f5%2012.exf6%20Nxf6%2013.Nxg5%20d5%2014.Bd3%20e5%2015.Bg6%2B%20Kf8%2016.Nf7%20Qa5%2B%2017.b4%20Qc7%2018.Nxh8%20Kg7%2019.Nf7#21) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.a3%20Be7%207.Nxc6%20bxc6%208.e5%20Nd5%209.Qg4%20g5%2010.Ne4%20h5%2011.Qd1%20f5%2012.exf6%20Nxf6%2013.Nxg5%20d5%2014.Bd3%20e5%2015.Bg6%2B%20Kf8%2016.Nf7%20Qa5%2B%2017.Bd2%20Qc7%2018.Nxh8%20Kg7%2019.Nf7#21) |

position 4 (`r1bq1b1r/3k2pp/p1p5/1p1Bp1N1/8/3P4/PPP2PPP/RNB1K2R w KQ - 0 12`), split at ply 10: Re8+ (75% there) vs Qe6+ (23%)

| chosen | subpar |
|---|---|
| 12.Be6+ Kc7 13.Bxc8 Qxc8 14.Nf7 Rg8 15.Nxe5 [Bd6] 16.Nf3 [Re8+] 17.Be3 Bf4 18.O-O Bxe3 19.fxe3 Rxe3 | 12.Be6+ Kc7 13.Bxc8 Qxc8 14.Nf7 Rg8 15.Nxe5 [Bd6] 16.Nf3 Qe6+ 17.Be3 Bf4 18.O-O Bxe3 19.fxe3 Qxe3+ |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Bc4%20a6%203.d3%20Nf6%204.Nf3%20b5%205.Bb3%20Nc6%206.Ng5%20d5%207.exd5%20Nxd5%208.Qf3%20Nce7%209.Qxf7%2B%20Kd7%2010.Qxd5%2B%20Nxd5%2011.Bxd5%20c6%2012.Be6%2B%20Kc7%2013.Bxc8%20Qxc8%2014.Nf7%20Rg8%2015.Nxe5%20Bd6%2016.Nf3%20Re8%2B%2017.Be3%20Bf4%2018.O-O%20Bxe3%2019.fxe3%20Rxe3#22) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Bc4%20a6%203.d3%20Nf6%204.Nf3%20b5%205.Bb3%20Nc6%206.Ng5%20d5%207.exd5%20Nxd5%208.Qf3%20Nce7%209.Qxf7%2B%20Kd7%2010.Qxd5%2B%20Nxd5%2011.Bxd5%20c6%2012.Be6%2B%20Kc7%2013.Bxc8%20Qxc8%2014.Nf7%20Rg8%2015.Nxe5%20Bd6%2016.Nf3%20Qe6%2B%2017.Be3%20Bf4%2018.O-O%20Bxe3%2019.fxe3%20Qxe3%2B#22) |

#### S #5 (k = 0): latents 705

position 41 (`r1q1kn1r/p3b3/2p3p1/1p2Pp1p/3P1B1P/1QPB2N1/PP6/2KR3R b kq - 1 18`), split at ply 15: Qxd8 (75% there) vs Bxd8 (25%)

| chosen | subpar |
|---|---|
| 18...a5 19.d5 a4 20.Qc2 cxd5 21.Bxb5+ Kf7 22.Rxd5 Ne6 23.Rf1 a3 24.b3 [Rd8] 25.Rxd8 [Qxd8] 26.Bc4 | 18...a5 19.d5 a4 20.Qc2 cxd5 21.Bxb5+ Kf7 22.Rxd5 Ne6 23.Rf1 a3 24.b3 [Rd8] 25.Rxd8 Bxd8 26.Bc4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.Nc3%20dxe4%204.Nxe4%20Bf5%205.f3%20Nf6%206.Bd3%20e6%207.Ne2%20Nbd7%208.Bf4%20Be7%209.g4%20Bxe4%2010.fxe4%20Nxg4%2011.Ng3%20f6%2012.Qxg4%20g6%2013.Qxe6%20Nf8%2014.Qb3%20b5%2015.c3%20Qc8%2016.e5%20f5%2017.h4%20h5%2018.O-O-O%20a5%2019.d5%20a4%2020.Qc2%20cxd5%2021.Bxb5%2B%20Kf7%2022.Rxd5%20Ne6%2023.Rf1%20a3%2024.b3%20Rd8%2025.Rxd8%20Qxd8%2026.Bc4#35) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.Nc3%20dxe4%204.Nxe4%20Bf5%205.f3%20Nf6%206.Bd3%20e6%207.Ne2%20Nbd7%208.Bf4%20Be7%209.g4%20Bxe4%2010.fxe4%20Nxg4%2011.Ng3%20f6%2012.Qxg4%20g6%2013.Qxe6%20Nf8%2014.Qb3%20b5%2015.c3%20Qc8%2016.e5%20f5%2017.h4%20h5%2018.O-O-O%20a5%2019.d5%20a4%2020.Qc2%20cxd5%2021.Bxb5%2B%20Kf7%2022.Rxd5%20Ne6%2023.Rf1%20a3%2024.b3%20Rd8%2025.Rxd8%20Bxd8%2026.Bc4#35) |

position 21 (`r1b2rk1/pp2q1pp/3b4/5p1Q/4p3/2N5/PPP2PPP/R1BR2K1 w - - 2 17`), split at ply 13: Rd1 (76% there) vs Rf1 (24%)

| chosen | subpar |
|---|---|
| [17.Nd5] Qe5 18.Bf4 Qe6 [19.Bxd6] Qxd6 20.Nb6 Qxb6 21.Rd5 Be6 22.Re5 Qxb2 [23.Rd1] Qxe5 24.Qe2 [Rad8] | [17.Nd5] Qe5 18.Bf4 Qe6 [19.Bxd6] Qxd6 20.Nb6 Qxb6 21.Rd5 Be6 22.Re5 Qxb2 23.Rf1 [Qxe5] 24.f4 Qd4+ |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Qxd4%20Nf6%205.e5%20Nfd7%206.exd6%20Nc6%207.Qe3%20e6%208.Nc3%20Bxd6%209.Bd3%20O-O%2010.O-O%20Nde5%2011.Nxe5%20Nxe5%2012.Be4%20f5%2013.Bf3%20Nxf3%2B%2014.Qxf3%20e5%2015.Rd1%20e4%2016.Qh5%20Qe7%2017.Nd5%20Qe5%2018.Bf4%20Qe6%2019.Bxd6%20Qxd6%2020.Nb6%20Qxb6%2021.Rd5%20Be6%2022.Re5%20Qxb2%2023.Rd1%20Qxe5%2024.Qe2%20Rad8#32) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Qxd4%20Nf6%205.e5%20Nfd7%206.exd6%20Nc6%207.Qe3%20e6%208.Nc3%20Bxd6%209.Bd3%20O-O%2010.O-O%20Nde5%2011.Nxe5%20Nxe5%2012.Be4%20f5%2013.Bf3%20Nxf3%2B%2014.Qxf3%20e5%2015.Rd1%20e4%2016.Qh5%20Qe7%2017.Nd5%20Qe5%2018.Bf4%20Qe6%2019.Bxd6%20Qxd6%2020.Nb6%20Qxb6%2021.Rd5%20Be6%2022.Re5%20Qxb2%2023.Rf1%20Qxe5%2024.f4%20Qd4%2B#32) |

position 40 (`r3k3/pp1nbpp1/2p1p3/3nP1Bq/3NBP2/3P2Q1/PPP3K1/R7 b q - 0 24`), split at ply 14: Ke3 (80% there) vs Kg4 (20%)

| chosen | subpar |
|---|---|
| 24...Bxg5 25.fxg5 Nxe5 26.Rh1 Qg4 27.Qxg4 Nxg4 [28.Bxd5] cxd5 29.Kf3 Ne5+ 30.Kf4 Ng6+ [31.Ke3] Ke7 [32.Rf1] | 24...Bxg5 25.fxg5 Nxe5 26.Rh1 Qg4 27.Qxg4 Nxg4 [28.Bxd5] cxd5 29.Kf3 Ne5+ 30.Kf4 Ng6+ 31.Kg4 Ke7 32.Rf1 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.Nf3%20d5%203.d3%20Bg4%204.h3%20Bh5%205.Nc3%20e6%206.g4%20Bg6%207.h4%20h5%208.Ne5%20Ne7%209.Nxg6%20Nxg6%2010.gxh5%20Nxh4%2011.Qg4%20Ng6%2012.Bg2%20Ne5%2013.Qg3%20Ned7%2014.Bf4%20d4%2015.Ne2%20Qa5%2B%2016.Kf1%20Rxh5%2017.Rxh5%20Qxh5%2018.e5%20Nb6%2019.Nxd4%20Nd5%2020.Bg5%20Nd7%2021.Bf3%20Qg6%2022.Be4%20Qh5%2023.Kg2%20Be7%2024.f4%20Bxg5%2025.fxg5%20Nxe5%2026.Rh1%20Qg4%2027.Qxg4%20Nxg4%2028.Bxd5%20cxd5%2029.Kf3%20Ne5%2B%2030.Kf4%20Ng6%2B%2031.Ke3%20Ke7%2032.Rf1#47) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.Nf3%20d5%203.d3%20Bg4%204.h3%20Bh5%205.Nc3%20e6%206.g4%20Bg6%207.h4%20h5%208.Ne5%20Ne7%209.Nxg6%20Nxg6%2010.gxh5%20Nxh4%2011.Qg4%20Ng6%2012.Bg2%20Ne5%2013.Qg3%20Ned7%2014.Bf4%20d4%2015.Ne2%20Qa5%2B%2016.Kf1%20Rxh5%2017.Rxh5%20Qxh5%2018.e5%20Nb6%2019.Nxd4%20Nd5%2020.Bg5%20Nd7%2021.Bf3%20Qg6%2022.Be4%20Qh5%2023.Kg2%20Be7%2024.f4%20Bxg5%2025.fxg5%20Nxe5%2026.Rh1%20Qg4%2027.Qxg4%20Nxg4%2028.Bxd5%20cxd5%2029.Kf3%20Ne5%2B%2030.Kf4%20Ng6%2B%2031.Kg4%20Ke7%2032.Rf1#47) |

#### S #6 (k = 0): latents 572

position 47 (`r2qr1k1/pp3ppp/1bn5/3p4/3Nb2n/1NP2PBP/PP2B1PK/R2Q1R2 b - - 0 16`), split at ply 9: a6 (75% there) vs Be6 (25%)

| chosen | subpar |
|---|---|
| [16...Bg6] 17.Bb5 [Rc8] 18.Qd2 [Nf5] 19.Nxf5 [Bxf5] 20.Rad1 [a6] 21.Bd3 Be6 22.Bb1 Qf6 23.Rfe1 Rcd8 24.Qc2 | [16...Bg6] 17.Bb5 [Rc8] 18.Qd2 [Nf5] 19.Nxf5 [Bxf5] 20.Rad1 Be6 21.Rfe1 a6 22.Bf1 Qf6 23.Qf4 Qg6 24.Bd3 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bg6%2017.Bb5%20Rc8%2018.Qd2%20Nf5%2019.Nxf5%20Bxf5%2020.Rad1%20a6%2021.Bd3%20Be6%2022.Bb1%20Qf6%2023.Rfe1%20Rcd8%2024.Qc2#31) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bg6%2017.Bb5%20Rc8%2018.Qd2%20Nf5%2019.Nxf5%20Bxf5%2020.Rad1%20Be6%2021.Rfe1%20a6%2022.Bf1%20Qf6%2023.Qf4%20Qg6%2024.Bd3#31) |

position 15 (`r1q2rk1/2B2ppp/p1Q1p3/3p4/3Pn3/P3P3/P1P2PPP/R4RK1 b - - 4 17`), split at ply 11: Rxb1 (76% there) vs Rcb5 (24%)

| chosen | subpar |
|---|---|
| 17...Ra7 [18.Bb6] Rb7 19.Qxc8 Rxc8 20.Bc5 Nxc5 21.dxc5 Rxc5 22.Rab1 [Rxb1] 23.Rxb1 g6 24.Rb2 Rc3 25.a4 | 17...Ra7 [18.Bb6] Rb7 19.Qxc8 Rxc8 20.Bc5 Nxc5 21.dxc5 Rxc5 22.Rab1 Rcb5 23.Rxb5 Rxb5 24.Rc1 Rb2 25.Kf1 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bf4%20d6%203.e3%20Nc6%204.Bb5%20Bd7%205.Bxc6%20Bxc6%206.Nf3%20Bxf3%207.Qxf3%20e6%208.Qxb7%20d5%209.Bxc7%20Qc8%2010.Qc6%2B%20Nd7%2011.Na3%20Be7%2012.Nb5%20O-O%2013.Qc3%20a6%2014.Na3%20Bxa3%2015.bxa3%20Nf6%2016.O-O%20Ne4%2017.Qc6%20Ra7%2018.Bb6%20Rb7%2019.Qxc8%20Rxc8%2020.Bc5%20Nxc5%2021.dxc5%20Rxc5%2022.Rab1%20Rxb1%2023.Rxb1%20g6%2024.Rb2%20Rc3%2025.a4#33) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bf4%20d6%203.e3%20Nc6%204.Bb5%20Bd7%205.Bxc6%20Bxc6%206.Nf3%20Bxf3%207.Qxf3%20e6%208.Qxb7%20d5%209.Bxc7%20Qc8%2010.Qc6%2B%20Nd7%2011.Na3%20Be7%2012.Nb5%20O-O%2013.Qc3%20a6%2014.Na3%20Bxa3%2015.bxa3%20Nf6%2016.O-O%20Ne4%2017.Qc6%20Ra7%2018.Bb6%20Rb7%2019.Qxc8%20Rxc8%2020.Bc5%20Nxc5%2021.dxc5%20Rxc5%2022.Rab1%20Rcb5%2023.Rxb5%20Rxb5%2024.Rc1%20Rb2%2025.Kf1#33) |

position 27 (`r3kb1r/1p2pp1p/p2p1np1/4n1Q1/3B4/PP2P3/2qPNPPP/R4RK1 b kq - 1 15`), split at ply 7: Qf5 (77% there) vs Qxb3 (23%)

| chosen | subpar |
|---|---|
| 15...Qxd2 16.Nf4 Bg7 17.Rfd1 Qc2 18.Rac1 [Qf5] 19.Qg3 O-O 20.Rc7 Ne4 21.Qh4 g5 22.Qh5 gxf4 23.exf4 | 15...Qxd2 16.Nf4 Bg7 17.Rfd1 Qc2 18.Rac1 Qxb3 19.Rb1 Qc2 20.Rdc1 [Qf5] 21.Qg3 b5 22.a4 O-O 23.axb5 |
| [Lichess](https://lichess.org/analysis/pgn/1.e3%20c5%202.Qh5%20Nf6%203.Qxc5%20g6%204.Bc4%20d6%205.Qg5%20Nc6%206.a3%20Ne5%207.Bb5%2B%20Bd7%208.Ba4%20Bxa4%209.b3%20Bd7%2010.Bb2%20Qc7%2011.Nc3%20a6%2012.Nge2%20Bb5%2013.O-O%20Bxe2%2014.Nxe2%20Qxc2%2015.Bd4%20Qxd2%2016.Nf4%20Bg7%2017.Rfd1%20Qc2%2018.Rac1%20Qf5%2019.Qg3%20O-O%2020.Rc7%20Ne4%2021.Qh4%20g5%2022.Qh5%20gxf4%2023.exf4#29) | [Lichess](https://lichess.org/analysis/pgn/1.e3%20c5%202.Qh5%20Nf6%203.Qxc5%20g6%204.Bc4%20d6%205.Qg5%20Nc6%206.a3%20Ne5%207.Bb5%2B%20Bd7%208.Ba4%20Bxa4%209.b3%20Bd7%2010.Bb2%20Qc7%2011.Nc3%20a6%2012.Nge2%20Bb5%2013.O-O%20Bxe2%2014.Nxe2%20Qxc2%2015.Bd4%20Qxd2%2016.Nf4%20Bg7%2017.Rfd1%20Qc2%2018.Rac1%20Qxb3%2019.Rb1%20Qc2%2020.Rdc1%20Qf5%2021.Qg3%20b5%2022.a4%20O-O%2023.axb5#29) |

#### S #7 (k = 0): latents 556

position 12 (`2k4r/1pb3p1/p1n4p/5R2/4p2Q/P1PpB2P/1q4P1/R6K b - - 1 22`), split at ply 10: Qxf4 (75% there) vs Rxf4 (25%)

| chosen | subpar |
|---|---|
| 22...Qxc3 23.Rc1 [Qxa3] [24.Qxe4] [Rd8] 25.Rf7 [Qd6] 26.Bf4 [Qxf4] [27.Qxf4] [Bxf4] 28.Rxc6+ [bxc6] [29.Rxf4] [d2] [30.Rf1] | 22...Qxc3 23.Rc1 [Qxa3] [24.Qxe4] [Rd8] 25.Rf7 [Qd6] 26.Bf4 [Qxf4] 27.Rxf4 [d2] 28.Rd1 [Bxf4] [29.Qxf4] [Nd4] 30.Rxd2 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.e4%20dxe4%204.f3%20exf3%205.Nxf3%20c5%206.Bd3%20cxd4%207.Ne4%20Nxe4%208.Bxe4%20Nc6%209.O-O%20Qb6%2010.Kh1%20e5%2011.Qe1%20Bd6%2012.Ng5%20Bd7%2013.a3%20O-O-O%2014.Nxf7%20Bc7%2015.Nxh8%20Rxh8%2016.Rf7%20h6%2017.c3%20a6%2018.Bf5%20Bxf5%2019.Rxf5%20d3%2020.Be3%20Qxb2%2021.h3%20e4%2022.Qh4%20Qxc3%2023.Rc1%20Qxa3%2024.Qxe4%20Rd8%2025.Rf7%20Qd6%2026.Bf4%20Qxf4%2027.Qxf4%20Bxf4%2028.Rxc6%2B%20bxc6%2029.Rxf4%20d2%2030.Rf1#43) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.e4%20dxe4%204.f3%20exf3%205.Nxf3%20c5%206.Bd3%20cxd4%207.Ne4%20Nxe4%208.Bxe4%20Nc6%209.O-O%20Qb6%2010.Kh1%20e5%2011.Qe1%20Bd6%2012.Ng5%20Bd7%2013.a3%20O-O-O%2014.Nxf7%20Bc7%2015.Nxh8%20Rxh8%2016.Rf7%20h6%2017.c3%20a6%2018.Bf5%20Bxf5%2019.Rxf5%20d3%2020.Be3%20Qxb2%2021.h3%20e4%2022.Qh4%20Qxc3%2023.Rc1%20Qxa3%2024.Qxe4%20Rd8%2025.Rf7%20Qd6%2026.Bf4%20Qxf4%2027.Rxf4%20d2%2028.Rd1%20Bxf4%2029.Qxf4%20Nd4%2030.Rxd2#43) |

position 41 (`r1q1kn1r/p3b3/2p3p1/1p2Pp1p/3P1B1P/1QPB2N1/PP6/2KR3R b kq - 1 18`), split at ply 15: Qxd8 (75% there) vs Bxd8 (25%)

| chosen | subpar |
|---|---|
| 18...a5 [19.d5] a4 [20.Qc2] [cxd5] [21.Bxb5+] [Kf7] [22.Rxd5] Ne6 [23.Rf1] a3 [24.b3] Rd8 25.Rxd8 [Qxd8] 26.Bc4 | 18...a5 [19.d5] a4 [20.Qc2] [cxd5] [21.Bxb5+] [Kf7] [22.Rxd5] Ne6 [23.Rf1] a3 [24.b3] Rd8 25.Rxd8 Bxd8 26.Bc4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.Nc3%20dxe4%204.Nxe4%20Bf5%205.f3%20Nf6%206.Bd3%20e6%207.Ne2%20Nbd7%208.Bf4%20Be7%209.g4%20Bxe4%2010.fxe4%20Nxg4%2011.Ng3%20f6%2012.Qxg4%20g6%2013.Qxe6%20Nf8%2014.Qb3%20b5%2015.c3%20Qc8%2016.e5%20f5%2017.h4%20h5%2018.O-O-O%20a5%2019.d5%20a4%2020.Qc2%20cxd5%2021.Bxb5%2B%20Kf7%2022.Rxd5%20Ne6%2023.Rf1%20a3%2024.b3%20Rd8%2025.Rxd8%20Qxd8%2026.Bc4#35) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.Nc3%20dxe4%204.Nxe4%20Bf5%205.f3%20Nf6%206.Bd3%20e6%207.Ne2%20Nbd7%208.Bf4%20Be7%209.g4%20Bxe4%2010.fxe4%20Nxg4%2011.Ng3%20f6%2012.Qxg4%20g6%2013.Qxe6%20Nf8%2014.Qb3%20b5%2015.c3%20Qc8%2016.e5%20f5%2017.h4%20h5%2018.O-O-O%20a5%2019.d5%20a4%2020.Qc2%20cxd5%2021.Bxb5%2B%20Kf7%2022.Rxd5%20Ne6%2023.Rf1%20a3%2024.b3%20Rd8%2025.Rxd8%20Bxd8%2026.Bc4#35) |

position 42 (`rnb2rk1/5ppp/p3pn2/1p1p4/q7/B3P1P1/3NNPBP/R2Q1RK1 w - - 0 14`), split at ply 11: Rxc6 (78% there) vs Nd4 (22%)

| chosen | subpar |
|---|---|
| [14.Bxf8] [Qxa1] [15.Qxa1] [Kxf8] [16.Qa3+] [Ke8] [17.Rc1] [Bd7] [18.Qd6] [Nc6] [19.Rxc6] [Bxc6] [20.Qxc6+] [Ke7] [21.Qxa8] [Nd7] | [14.Bxf8] [Qxa1] [15.Qxa1] [Kxf8] [16.Qa3+] [Ke8] [17.Rc1] [Bd7] [18.Qd6] [Nc6] 19.Nd4 Rc8 [20.Nxc6] Rxc6 21.Rxc6 [Bxc6] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.e3%20e6%203.Ne2%20c5%204.Nd2%20a6%205.g3%20Nf6%206.Bg2%20Be7%207.O-O%20O-O%208.c3%20b5%209.a4%20Qa5%2010.dxc5%20Bxc5%2011.b4%20Bxb4%2012.cxb4%20Qxb4%2013.Ba3%20Qxa4%2014.Bxf8%20Qxa1%2015.Qxa1%20Kxf8%2016.Qa3%2B%20Ke8%2017.Rc1%20Bd7%2018.Qd6%20Nc6%2019.Rxc6%20Bxc6%2020.Qxc6%2B%20Ke7%2021.Qxa8%20Nd7#26) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.e3%20e6%203.Ne2%20c5%204.Nd2%20a6%205.g3%20Nf6%206.Bg2%20Be7%207.O-O%20O-O%208.c3%20b5%209.a4%20Qa5%2010.dxc5%20Bxc5%2011.b4%20Bxb4%2012.cxb4%20Qxb4%2013.Ba3%20Qxa4%2014.Bxf8%20Qxa1%2015.Qxa1%20Kxf8%2016.Qa3%2B%20Ke8%2017.Rc1%20Bd7%2018.Qd6%20Nc6%2019.Nd4%20Rc8%2020.Nxc6%20Rxc6%2021.Rxc6%20Bxc6#26) |

#### S #8 (k = 0): latents 570

position 48 (`r4r1k/1ppqn2p/p5p1/4pP2/2Pp2P1/3PbRNP/PP4BK/R2Q4 b - - 1 21`), split at ply 14: Rf3 (75% there) vs Qe4 (25%)

| chosen | subpar |
|---|---|
| 21...gxf5 [22.gxf5] Rxf5 [23.Nxf5] [Nxf5] [24.Qe2] Rg8 25.Raf1 Bf4+ 26.Kh1 [Ng3+] [27.Rxg3] [Rxg3] [28.Rf3] [Rxf3] 29.Qxf3 | 21...gxf5 [22.gxf5] Rxf5 [23.Nxf5] [Nxf5] [24.Qe2] Rg8 25.Raf1 Bf4+ 26.Kh1 [Ng3+] [27.Rxg3] [Rxg3] 28.Qe4 [c6] [29.Rxf4] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nc3%20e5%203.g3%20Bc5%204.Bg2%20a6%205.Nge2%20Nge7%206.h3%20d6%207.d3%20O-O%208.O-O%20Be6%209.Kh2%20f5%2010.f4%20Qd7%2011.exf5%20Nxf5%2012.g4%20Ne3%2013.Bxe3%20Bxe3%2014.f5%20Bf7%2015.Nd5%20Bxd5%2016.Bxd5%2B%20Kh8%2017.Bg2%20d5%2018.c3%20Ne7%2019.Rf3%20d4%2020.c4%20g6%2021.Ng3%20gxf5%2022.gxf5%20Rxf5%2023.Nxf5%20Nxf5%2024.Qe2%20Rg8%2025.Raf1%20Bf4%2B%2026.Kh1%20Ng3%2B%2027.Rxg3%20Rxg3%2028.Rf3%20Rxf3%2029.Qxf3#41) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nc3%20e5%203.g3%20Bc5%204.Bg2%20a6%205.Nge2%20Nge7%206.h3%20d6%207.d3%20O-O%208.O-O%20Be6%209.Kh2%20f5%2010.f4%20Qd7%2011.exf5%20Nxf5%2012.g4%20Ne3%2013.Bxe3%20Bxe3%2014.f5%20Bf7%2015.Nd5%20Bxd5%2016.Bxd5%2B%20Kh8%2017.Bg2%20d5%2018.c3%20Ne7%2019.Rf3%20d4%2020.c4%20g6%2021.Ng3%20gxf5%2022.gxf5%20Rxf5%2023.Nxf5%20Nxf5%2024.Qe2%20Rg8%2025.Raf1%20Bf4%2B%2026.Kh1%20Ng3%2B%2027.Rxg3%20Rxg3%2028.Qe4%20c6%2029.Rxf4#41) |

position 15 (`r1q2rk1/2B2ppp/p1Q1p3/3p4/3Pn3/P3P3/P1P2PPP/R4RK1 b - - 4 17`), split at ply 10: Bg3 (77% there) vs Rb7 (23%)

| chosen | subpar |
|---|---|
| [17...Nd2] [18.Rfd1] [Nc4] [19.Rdb1] [Qe8] [20.Qxe8] [Rfxe8] [21.a4] [Rec8] [22.Bg3] [Na3] [23.Rb7] [Rxc2] [24.h4] [h5] [25.Rab1] | [17...Nd2] [18.Rfd1] [Nc4] [19.Rdb1] [Qe8] [20.Qxe8] [Rfxe8] [21.a4] [Rec8] 22.Rb7 [Kf8] [23.Rab1] [Ke8] [24.Bf4] [h6] [25.h4] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bf4%20d6%203.e3%20Nc6%204.Bb5%20Bd7%205.Bxc6%20Bxc6%206.Nf3%20Bxf3%207.Qxf3%20e6%208.Qxb7%20d5%209.Bxc7%20Qc8%2010.Qc6%2B%20Nd7%2011.Na3%20Be7%2012.Nb5%20O-O%2013.Qc3%20a6%2014.Na3%20Bxa3%2015.bxa3%20Nf6%2016.O-O%20Ne4%2017.Qc6%20Nd2%2018.Rfd1%20Nc4%2019.Rdb1%20Qe8%2020.Qxe8%20Rfxe8%2021.a4%20Rec8%2022.Bg3%20Na3%2023.Rb7%20Rxc2%2024.h4%20h5%2025.Rab1#33) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bf4%20d6%203.e3%20Nc6%204.Bb5%20Bd7%205.Bxc6%20Bxc6%206.Nf3%20Bxf3%207.Qxf3%20e6%208.Qxb7%20d5%209.Bxc7%20Qc8%2010.Qc6%2B%20Nd7%2011.Na3%20Be7%2012.Nb5%20O-O%2013.Qc3%20a6%2014.Na3%20Bxa3%2015.bxa3%20Nf6%2016.O-O%20Ne4%2017.Qc6%20Nd2%2018.Rfd1%20Nc4%2019.Rdb1%20Qe8%2020.Qxe8%20Rfxe8%2021.a4%20Rec8%2022.Rb7%20Kf8%2023.Rab1%20Ke8%2024.Bf4%20h6%2025.h4#33) |

position 13 (`r2qkb1r/ppp3pp/5n2/3p4/8/2P1BB2/PP3P1P/RN1QK2R b KQkq - 2 11`), split at ply 11: Nd7 (76% there) vs b5 (18%)

| chosen | subpar |
|---|---|
| 11...c6 [12.Nd2] Bd6 13.Qe2 O-O 14.O-O-O Qa5 15.Kb1 Rae8 16.Qd3 [Nd7] 17.Rhg1 Ne5 18.Qe2 Nxf3 19.Nxf3 | 11...c6 [12.Nd2] Bd6 13.Qe2 O-O 14.O-O-O Qa5 15.Kb1 Rae8 16.Qd3 b5 17.Nb3 Qc7 18.Bc5 Bxc5 19.Nxc5 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.d4%20Bxf5%205.Bd3%20Bg4%206.c3%20e5%207.dxe5%20Nxe5%208.Be2%20Nxf3%2B%209.gxf3%20Bxf3%2010.Bxf3%20Nf6%2011.Be3%20c6%2012.Nd2%20Bd6%2013.Qe2%20O-O%2014.O-O-O%20Qa5%2015.Kb1%20Rae8%2016.Qd3%20Nd7%2017.Rhg1%20Ne5%2018.Qe2%20Nxf3%2019.Nxf3#21) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.d4%20Bxf5%205.Bd3%20Bg4%206.c3%20e5%207.dxe5%20Nxe5%208.Be2%20Nxf3%2B%209.gxf3%20Bxf3%2010.Bxf3%20Nf6%2011.Be3%20c6%2012.Nd2%20Bd6%2013.Qe2%20O-O%2014.O-O-O%20Qa5%2015.Kb1%20Rae8%2016.Qd3%20b5%2017.Nb3%20Qc7%2018.Bc5%20Bxc5%2019.Nxc5#21) |

#### S #9 (k = 0): latents 705

position 38 (`2r2rk1/2q2Ppp/p2b4/1ppQ4/8/2NP4/PP2K1PP/R1B4n b - - 0 22`), split at ply 10: Ke3 (75% there) vs Kd2 (25%)

| chosen | subpar |
|---|---|
| 22...Qxf7 23.Qxf7+ Rxf7 24.Be3 Re8 25.Ne4 [Bxh2] [26.Bxc5] Ng3+ [27.Ke3] Nxe4 [28.dxe4] Bf4+ [29.Kd3] Rd7+ 30.Kc3 | 22...Qxf7 23.Qxf7+ Rxf7 24.Be3 Re8 25.Ne4 [Bxh2] [26.Bxc5] Ng3+ 27.Kd2 Nxe4+ [28.dxe4] Bf4+ [29.Kd3] Rd7+ 30.Kc3 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Qh5%20e6%203.Nf3%20Nc6%204.Bb5%20Nb4%205.Ba4%20a6%206.c3%20Nd3%2B%207.Kd1%20Nxf2%2B%208.Ke2%20Nxh1%209.Ne5%20Qe7%2010.d3%20Nf6%2011.Qf3%20b5%2012.Bb3%20d6%2013.Nc6%20Qc7%2014.e5%20Nd5%2015.c4%20Qxc6%2016.cxd5%20Qc7%2017.dxe6%20Bb7%2018.Bd5%20Bxd5%2019.Qxd5%20Rc8%2020.exd6%20Bxd6%2021.Nc3%20O-O%2022.exf7%2B%20Qxf7%2023.Qxf7%2B%20Rxf7%2024.Be3%20Re8%2025.Ne4%20Bxh2%2026.Bxc5%20Ng3%2B%2027.Ke3%20Nxe4%2028.dxe4%20Bf4%2B%2029.Kd3%20Rd7%2B%2030.Kc3#43) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Qh5%20e6%203.Nf3%20Nc6%204.Bb5%20Nb4%205.Ba4%20a6%206.c3%20Nd3%2B%207.Kd1%20Nxf2%2B%208.Ke2%20Nxh1%209.Ne5%20Qe7%2010.d3%20Nf6%2011.Qf3%20b5%2012.Bb3%20d6%2013.Nc6%20Qc7%2014.e5%20Nd5%2015.c4%20Qxc6%2016.cxd5%20Qc7%2017.dxe6%20Bb7%2018.Bd5%20Bxd5%2019.Qxd5%20Rc8%2020.exd6%20Bxd6%2021.Nc3%20O-O%2022.exf7%2B%20Qxf7%2023.Qxf7%2B%20Rxf7%2024.Be3%20Re8%2025.Ne4%20Bxh2%2026.Bxc5%20Ng3%2B%2027.Kd2%20Nxe4%2B%2028.dxe4%20Bf4%2B%2029.Kd3%20Rd7%2B%2030.Kc3#43) |

position 37 (`2r2k1r/1p1B1p1p/p5p1/2PpP3/6P1/P3q3/1P1NN1P1/n2K3Q w - - 2 26`), split at ply 6: Rb8 (78% there) vs Qxb2 (22%)

| chosen | subpar |
|---|---|
| 26.Bxc8 [Qxe5] 27.Qh6+ [Ke7] 28.Bxb7 [Rb8] 29.c6 [Nb3] 30.c7 Qxc7 31.Bxd5 Nxd2 [32.Kxd2] Rxb2+ [33.Ke3] [Qe5+] | 26.Bxc8 [Qxe5] 27.Qh6+ [Ke7] 28.Bxb7 Qxb2 29.Bxd5 [Rd8] 30.Qe3+ [Kf8] 31.Qh6+ [Ke7] 32.Qe3+ [Kf8] 33.Qh6+ [Ke7] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20e6%203.e3%20Bd6%204.Bg3%20Bxg3%205.hxg3%20Nc6%206.c4%20Nge7%207.a3%20Bd7%208.Qg4%20g6%209.Qg5%20Nf5%2010.Qf4%20Qe7%2011.g4%20Nd6%2012.c5%20Ne4%2013.Qxc7%20Bc8%2014.Qf4%20e5%2015.Qh6%20Bxg4%2016.f3%20Ng3%2017.fxg4%20Nxh1%2018.Qxh1%20Qg5%2019.Be2%20Qxe3%2020.dxe5%20Nd4%2021.Nd2%20Nc2%2B%2022.Kd1%20Nxa1%2023.Bb5%2B%20Kf8%2024.Ne2%20a6%2025.Bd7%20Rc8%2026.Bxc8%20Qxe5%2027.Qh6%2B%20Ke7%2028.Bxb7%20Rb8%2029.c6%20Nb3%2030.c7%20Qxc7%2031.Bxd5%20Nxd2%2032.Kxd2%20Rxb2%2B%2033.Ke3%20Qe5%2B#50) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20e6%203.e3%20Bd6%204.Bg3%20Bxg3%205.hxg3%20Nc6%206.c4%20Nge7%207.a3%20Bd7%208.Qg4%20g6%209.Qg5%20Nf5%2010.Qf4%20Qe7%2011.g4%20Nd6%2012.c5%20Ne4%2013.Qxc7%20Bc8%2014.Qf4%20e5%2015.Qh6%20Bxg4%2016.f3%20Ng3%2017.fxg4%20Nxh1%2018.Qxh1%20Qg5%2019.Be2%20Qxe3%2020.dxe5%20Nd4%2021.Nd2%20Nc2%2B%2022.Kd1%20Nxa1%2023.Bb5%2B%20Kf8%2024.Ne2%20a6%2025.Bd7%20Rc8%2026.Bxc8%20Qxe5%2027.Qh6%2B%20Ke7%2028.Bxb7%20Qxb2%2029.Bxd5%20Rd8%2030.Qe3%2B%20Kf8%2031.Qh6%2B%20Ke7%2032.Qe3%2B%20Kf8%2033.Qh6%2B%20Ke7#50) |

position 25 (`1r3r2/pb4kp/1p4p1/2pnP3/4B3/2P4P/PP1N2P1/R4RK1 w - - 3 21`), split at ply 12: Rbd8 (77% there) vs c4 (20%)

| chosen | subpar |
|---|---|
| 21.Nc4 Ba6 22.Bxd5 Bxc4 23.Bxc4 b5 24.Bd5 Rfe8 25.Rf7+ Kh6 26.Re1 [Rbd8] 27.Bf3 Rd2 28.Re2 Rd1+ | 21.Nc4 Ba6 22.Bxd5 Bxc4 23.Bxc4 b5 24.Bd5 Rfe8 25.Rf7+ Kh6 26.Re1 c4 27.e6 Rb6 28.e7 [Rd6] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.Nc4%20Ba6%2022.Bxd5%20Bxc4%2023.Bxc4%20b5%2024.Bd5%20Rfe8%2025.Rf7%2B%20Kh6%2026.Re1%20Rbd8%2027.Bf3%20Rd2%2028.Re2%20Rd1%2B#40) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.Nc4%20Ba6%2022.Bxd5%20Bxc4%2023.Bxc4%20b5%2024.Bd5%20Rfe8%2025.Rf7%2B%20Kh6%2026.Re1%20c4%2027.e6%20Rb6%2028.e7%20Rd6#40) |

#### S #10 (k = 0): latents 49

position 7 (`2q2rk1/1Q3pp1/p1N1p2p/3p4/8/6P1/3r1P1P/1R3RK1 w - - 3 24`), split at ply 2: Kh7 (77% there) vs Kh8 (23%)

| chosen | subpar |
|---|---|
| 24.Ne7+ [Kh7] 25.Nxc8 Rxc8 26.Qxf7 Rc6 27.Rb7 Rcc2 28.Qxg7# | 24.Ne7+ Kh8 25.Nxc8 Rxc8 26.Qxf7 e5 27.Rb7 Rg8 28.Rfb1 e4 [29.Rb8] Rxb8 30.Rxb8+ Kh7 31.Qf5+ g6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.Qf3%20e6%203.Bc4%20Nf6%204.d4%20d5%205.exd5%20cxd5%206.Bb5%2B%20Bd7%207.Bxd7%2B%20Nbxd7%208.Bg5%20Be7%209.Nc3%20h6%2010.Bxf6%20Bxf6%2011.Nge2%20O-O%2012.O-O%20Nb6%2013.Nb5%20Nc4%2014.Qd3%20Nxb2%2015.Qc3%20Nc4%2016.Rab1%20a6%2017.Na3%20Rc8%2018.Nxc4%20Rxc4%2019.Qb3%20Bxd4%2020.Qxb7%20Rxc2%2021.Nxd4%20Rxa2%2022.g3%20Rd2%2023.Nc6%20Qc8%2024.Ne7%2B%20Kh7%2025.Nxc8%20Rxc8%2026.Qxf7%20Rc6%2027.Rb7%20Rcc2%2028.Qxg7%23#46) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.Qf3%20e6%203.Bc4%20Nf6%204.d4%20d5%205.exd5%20cxd5%206.Bb5%2B%20Bd7%207.Bxd7%2B%20Nbxd7%208.Bg5%20Be7%209.Nc3%20h6%2010.Bxf6%20Bxf6%2011.Nge2%20O-O%2012.O-O%20Nb6%2013.Nb5%20Nc4%2014.Qd3%20Nxb2%2015.Qc3%20Nc4%2016.Rab1%20a6%2017.Na3%20Rc8%2018.Nxc4%20Rxc4%2019.Qb3%20Bxd4%2020.Qxb7%20Rxc2%2021.Nxd4%20Rxa2%2022.g3%20Rd2%2023.Nc6%20Qc8%2024.Ne7%2B%20Kh8%2025.Nxc8%20Rxc8%2026.Qxf7%20e5%2027.Rb7%20Rg8%2028.Rfb1%20e4%2029.Rb8%20Rxb8%2030.Rxb8%2B%20Kh7%2031.Qf5%2B%20g6#46) |

position 0 (`2kr2r1/ppp5/2n1RbNp/2q2p1P/3p4/2PQ1P1B/PPKN3P/6R1 b - - 0 20`), split at ply 4: Rxc6 (76% there) vs bxc3 (22%)

| chosen | subpar |
|---|---|
| 20...dxc3 [21.Qxc3] Bxc3 [22.Rxc6] Rxd2+ [23.Kb1] Qxc6 24.Ne7+ Kb8 25.Nxc6+ bxc6 26.bxc3 [Rxh2] 27.Bxf5 [Rxh5] 28.Be4 | 20...dxc3 [21.Qxc3] Bxc3 22.bxc3 Nd4+ 23.Kb2 Nxe6 24.Nb3 Qf2+ 25.Ka3 [Qxh2] 26.Bxf5 Qd6+ 27.Kb2 Kb8 28.Re1 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.Qxc3%20Bxc3%2022.Rxc6%20Rxd2%2B%2023.Kb1%20Qxc6%2024.Ne7%2B%20Kb8%2025.Nxc6%2B%20bxc6%2026.bxc3%20Rxh2%2027.Bxf5%20Rxh5%2028.Be4#39) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.Qxc3%20Bxc3%2022.bxc3%20Nd4%2B%2023.Kb2%20Nxe6%2024.Nb3%20Qf2%2B%2025.Ka3%20Qxh2%2026.Bxf5%20Qd6%2B%2027.Kb2%20Kb8%2028.Re1#39) |

position 19 (`r4r1k/ppq1b1pp/2npQ3/4p3/1PP5/P1P2N2/5PPP/R1B2RK1 w - - 1 18`), split at ply 14: Qxc3 (75% there) vs h6 (21%)

| chosen | subpar |
|---|---|
| 18.Ng5 Bxg5 19.Bxg5 [Rae8] 20.Qh3 Qf7 21.Rad1 Qxc4 22.Rxd6 Rf7 23.Rfd1 Ref8 24.Be3 [Qxc3] 25.b5 Nd4 | 18.Ng5 Bxg5 19.Bxg5 [Rae8] 20.Qh3 Qf7 21.Rad1 Qxc4 22.Rxd6 Rf7 23.Rfd1 Ref8 24.Be3 h6 25.Qe6 Qxc3 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bc4%20Nf6%204.d3%20Be7%205.O-O%20O-O%206.Nc3%20d6%207.a3%20Be6%208.Qe2%20Bxc4%209.dxc4%20Nd7%2010.Nd5%20Nc5%2011.b4%20Ne6%2012.c3%20f5%2013.exf5%20Rxf5%2014.Qe4%20Rf8%2015.Qg4%20Qd7%2016.Nxc7%20Qxc7%2017.Qxe6%2B%20Kh8%2018.Ng5%20Bxg5%2019.Bxg5%20Rae8%2020.Qh3%20Qf7%2021.Rad1%20Qxc4%2022.Rxd6%20Rf7%2023.Rfd1%20Ref8%2024.Be3%20Qxc3%2025.b5%20Nd4#34) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bc4%20Nf6%204.d3%20Be7%205.O-O%20O-O%206.Nc3%20d6%207.a3%20Be6%208.Qe2%20Bxc4%209.dxc4%20Nd7%2010.Nd5%20Nc5%2011.b4%20Ne6%2012.c3%20f5%2013.exf5%20Rxf5%2014.Qe4%20Rf8%2015.Qg4%20Qd7%2016.Nxc7%20Qxc7%2017.Qxe6%2B%20Kh8%2018.Ng5%20Bxg5%2019.Bxg5%20Rae8%2020.Qh3%20Qf7%2021.Rad1%20Qxc4%2022.Rxd6%20Rf7%2023.Rfd1%20Ref8%2024.Be3%20h6%2025.Qe6%20Qxc3#34) |

## W

| k | pairs | nonzero v | families | held-out recurrence: median / 90% / max | null 95th: median | null (every draw): 90% / 99% | families above their null 95th (chance: 5%) |
|---|---|---|---|---|---|---|---|
| 0 | 1006 | 100% | 382 | 0.8% / 2.8% / 9.0% | 2.4% | 2.6% / 6.1% | 22 (6%) |
| 2 | 953 | 30% | 246 | 0.0% / 0.2% / 1.4% | 0.0% | 0.0% / 0.4% | 17 (7%) |
| 4 | 876 | 14% | 108 | 0.0% / 0.3% / 1.8% | 0.0% | 0.0% / 0.2% | 15 (14%) |
| 6 | 747 | 14% | 94 | 0.0% / 0.3% / 1.0% | 0.0% | 0.0% / 0.3% | 13 (14%) |

### W: the top 20 families by held-out recurrence

| # | k | latents (weight) | found in | held out on | recurrence | null 95th | persistence (pairs on at split) | positions found |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 19 (1.00) | B (26 v's) | A | 9.0% | 4.6% | 1.0 (45) | 2, 4, 8, 10, 12, 17, 21, 30, 42, 43, 44 |
| 2 | 0 | 619 (1.00) | A (2 v's) | B | 7.9% | 6.1% | 1.0 (40) | 16, 46 |
| 3 | 0 | 49 (1.00) | A (16 v's) | B | 6.3% | 5.1% | 1.0 (32) | 0, 7, 9, 16, 19, 24, 25, 28, 31, 33, 35, 45 |
| 4 | 0 | 19 (1.00) | A (40 v's) | B | 6.1% | 5.3% | 1.0 (31) | 0, 3, 5, 6, 9, 19, 20, 24, 26, 33, 34, 37 ... |
| 5 | 0 | 405 (1.00) | A (6 v's) | B | 5.5% | 6.1% | 1.0 (28) | 16, 19, 25, 31, 38 |
| 6 | 0 | 556 (1.00) | B (4 v's) | A | 5.2% | 5.2% | 1.0 (26) | 4, 14, 42, 48 |
| 7 | 0 | 323 (1.00) | B (2 v's) | A | 5.0% | 4.4% | 1.0 (25) | 43, 48 |
| 8 | 0 | 705 (1.00) | B (1 v's) | A | 5.0% | 5.6% | 1.0 (25) | 47 |
| 9 | 0 | 335 (1.00) | A (3 v's) | B | 4.9% | 4.8% | 1.0 (25) | 0, 25, 33 |
| 10 | 0 | 405 (1.00) | B (7 v's) | A | 4.6% | 5.4% | 1.0 (23) | 13, 17, 22, 23, 36 |
| 11 | 0 | 116 (1.00) | A (6 v's) | B | 4.5% | 5.8% | 1.0 (23) | 3, 7, 9, 34, 46 |
| 12 | 0 | 960 (1.00) | A (1 v's) | B | 4.5% | 5.3% | 1.0 (23) | 19 |
| 13 | 0 | 335 (1.00) | B (3 v's) | A | 4.4% | 5.4% | 1.0 (22) | 48 |
| 14 | 0 | 532 (1.00) | A (5 v's) | B | 4.3% | 6.5% | 1.0 (22) | 20, 29, 31, 46 |
| 15 | 0 | 49 (1.00) | B (25 v's) | A | 4.2% | 4.6% | 1.0 (21) | 8, 12, 15, 17, 21, 22, 27, 32, 36, 39, 40, 43 |
| 16 | 0 | 570 (1.00) | B (3 v's) | A | 4.0% | 5.0% | 1.0 (20) | 17, 22 |
| 17 | 0 | 917 (1.00) | B (1 v's) | A | 4.0% | 4.6% | 1.0 (20) | 30 |
| 18 | 0 | 498 (1.00) | A (3 v's) | B | 4.0% | 5.5% | 1.0 (20) | 3, 46 |
| 19 | 0 | 856 (1.00) | A (2 v's) | B | 3.8% | 5.5% | 1.0 (19) | 0, 35 |
| 20 | 0 | 33 (1.00) | A (3 v's) | B | 3.8% | 2.8% | 1.0 (19) | 28, 29, 34 |

#### W #1 (k = 0): latents 19

position 33 (`r2qk1r1/3bbpnp/p3N1p1/2ppB1P1/1p2P2P/1P3Q2/P1P2P2/2KR1B1R b q - 0 19`), split at ply 4: d6 (78% there) vs Bc4 (22%)

| chosen | subpar |
|---|---|
| [19...Bxe6] [20.exd5] [Bd7] [21.d6] [Bxd6] 22.Bxd6 [Nf5] 23.Qe4+ [Be6] 24.Bxc5 [Qa5] 25.Qxa8+ [Qd8] 26.Qxd8# | [19...Bxe6] [20.exd5] [Bd7] 21.Bc4 [Nf5] [22.d6] [Bxd6] 23.Bxd6 Nxd6 24.Rhe1+ [Be6] 25.Bxe6 [fxe6] 26.Rxe6+ [Kd7] 27.Rexd6+ |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.Bf4%20a6%204.e3%20e6%205.g4%20Bb4%206.Ne2%20Be7%207.g5%20Nh5%208.h4%20b5%209.Bh2%20Nc6%2010.Nc1%20g6%2011.Nb3%20Ng7%2012.Qf3%20b4%2013.Na4%20Bd7%2014.O-O-O%20Nxd4%2015.Nxd4%20Bxa4%2016.Be5%20Rg8%2017.e4%20c5%2018.b3%20Bd7%2019.Nxe6%20Bxe6%2020.exd5%20Bd7%2021.d6%20Bxd6%2022.Bxd6%20Nf5%2023.Qe4%2B%20Be6%2024.Bxc5%20Qa5%2025.Qxa8%2B%20Qd8%2026.Qxd8%23#37) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.Bf4%20a6%204.e3%20e6%205.g4%20Bb4%206.Ne2%20Be7%207.g5%20Nh5%208.h4%20b5%209.Bh2%20Nc6%2010.Nc1%20g6%2011.Nb3%20Ng7%2012.Qf3%20b4%2013.Na4%20Bd7%2014.O-O-O%20Nxd4%2015.Nxd4%20Bxa4%2016.Be5%20Rg8%2017.e4%20c5%2018.b3%20Bd7%2019.Nxe6%20Bxe6%2020.exd5%20Bd7%2021.Bc4%20Nf5%2022.d6%20Bxd6%2023.Bxd6%20Nxd6%2024.Rhe1%2B%20Be6%2025.Bxe6%20fxe6%2026.Rxe6%2B%20Kd7%2027.Rexd6%2B#37) |

position 37 (`2r2k1r/1p1B1p1p/p5p1/2PpP3/6P1/P3q3/1P1NN1P1/n2K3Q w - - 2 26`), split at ply 8: Rxd2+ (75% there) vs Qxd2# (22%)

| chosen | subpar |
|---|---|
| [26.Bxc8] Kg7 27.Bxb7 [Rb8] 28.Bxd5 [Rxb2] [29.Qf1] [Rxd2+] [30.Ke1] [Rxe2+] [31.Qxe2] Qxe2+ 32.Kxe2 Nc2 33.c6 Nd4+ | [26.Bxc8] Kg7 27.Bxb7 [Rb8] 28.Bxd5 [Rxb2] [29.Qf1] Qxd2# |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20e6%203.e3%20Bd6%204.Bg3%20Bxg3%205.hxg3%20Nc6%206.c4%20Nge7%207.a3%20Bd7%208.Qg4%20g6%209.Qg5%20Nf5%2010.Qf4%20Qe7%2011.g4%20Nd6%2012.c5%20Ne4%2013.Qxc7%20Bc8%2014.Qf4%20e5%2015.Qh6%20Bxg4%2016.f3%20Ng3%2017.fxg4%20Nxh1%2018.Qxh1%20Qg5%2019.Be2%20Qxe3%2020.dxe5%20Nd4%2021.Nd2%20Nc2%2B%2022.Kd1%20Nxa1%2023.Bb5%2B%20Kf8%2024.Ne2%20a6%2025.Bd7%20Rc8%2026.Bxc8%20Kg7%2027.Bxb7%20Rb8%2028.Bxd5%20Rxb2%2029.Qf1%20Rxd2%2B%2030.Ke1%20Rxe2%2B%2031.Qxe2%20Qxe2%2B%2032.Kxe2%20Nc2%2033.c6%20Nd4%2B#50) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20e6%203.e3%20Bd6%204.Bg3%20Bxg3%205.hxg3%20Nc6%206.c4%20Nge7%207.a3%20Bd7%208.Qg4%20g6%209.Qg5%20Nf5%2010.Qf4%20Qe7%2011.g4%20Nd6%2012.c5%20Ne4%2013.Qxc7%20Bc8%2014.Qf4%20e5%2015.Qh6%20Bxg4%2016.f3%20Ng3%2017.fxg4%20Nxh1%2018.Qxh1%20Qg5%2019.Be2%20Qxe3%2020.dxe5%20Nd4%2021.Nd2%20Nc2%2B%2022.Kd1%20Nxa1%2023.Bb5%2B%20Kf8%2024.Ne2%20a6%2025.Bd7%20Rc8%2026.Bxc8%20Kg7%2027.Bxb7%20Rb8%2028.Bxd5%20Rxb2%2029.Qf1%20Qxd2%23#50) |

position 5 (`r3kbnr/pbpn2pp/1p2q3/1Q2p1B1/4P3/2N2N2/PPP3PP/2KR1B1R b kq - 2 11`), split at ply 2: Qa6 (78% there) vs Qd3 (22%)

| chosen | subpar |
|---|---|
| [11...Bc6] [12.Qa6] [Ngf6] [13.Bb5] [Bxb5] 14.Nxb5 [Bd6] 15.Nxd6+ cxd6 16.Bxf6 Nxf6 17.Qb5+ Kf7 18.Ng5+ Kg6 19.Nxe6 | [11...Bc6] 12.Qd3 [h6] 13.Bh4 [g5] [14.Bg3] [O-O-O] [15.Qa6+] [Kb8] [16.Bb5] [Nc5] [17.Rxd8+] [Qc8] 18.Rxc8# |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Nf3%20d6%204.Qe2%20Qe7%205.d3%20b6%206.Nc3%20Bb7%207.fxe5%20dxe5%208.Bg5%20Qe6%209.O-O-O%20fxe4%2010.dxe4%20Nd7%2011.Qb5%20Bc6%2012.Qa6%20Ngf6%2013.Bb5%20Bxb5%2014.Nxb5%20Bd6%2015.Nxd6%2B%20cxd6%2016.Bxf6%20Nxf6%2017.Qb5%2B%20Kf7%2018.Ng5%2B%20Kg6%2019.Nxe6#21) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Nf3%20d6%204.Qe2%20Qe7%205.d3%20b6%206.Nc3%20Bb7%207.fxe5%20dxe5%208.Bg5%20Qe6%209.O-O-O%20fxe4%2010.dxe4%20Nd7%2011.Qb5%20Bc6%2012.Qd3%20h6%2013.Bh4%20g5%2014.Bg3%20O-O-O%2015.Qa6%2B%20Kb8%2016.Bb5%20Nc5%2017.Rxd8%2B%20Qc8%2018.Rxc8%23#21) |

#### W #2 (k = 0): latents 619

position 32 (`r2qk2r/ppp2ppp/2n5/7b/1b1P4/2P2N1P/PB2BPP1/R2QK2R b KQkq - 0 12`), split at ply 5: Bxe2 (75% there) vs Nxe5 (25%)

| chosen | subpar |
|---|---|
| [12...Ba5] 13.O-O [O-O] 14.Ne5 [Bxe2] [15.Qxe2] Nxe5 16.Qxe5 Re8 [17.Qxa5] b6 [18.Qb5] a6 [19.Qd3] c5 [20.d5] | [12...Ba5] 13.O-O [O-O] 14.Ne5 Nxe5 15.dxe5 Qxd1 16.Raxd1 Bxe2 [17.Rfe1] [Bxd1] 18.Rxd1 Rad8 19.Re1 Rfe8 20.c4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20d5%202.exd5%20Nf6%203.Nc3%20Nxd5%204.Bc4%20Nxc3%205.bxc3%20Nc6%206.Bb2%20e5%207.Nf3%20Bg4%208.h3%20Bh5%209.Be2%20Bc5%2010.d4%20exd4%2011.cxd4%20Bb4%2B%2012.c3%20Ba5%2013.O-O%20O-O%2014.Ne5%20Bxe2%2015.Qxe2%20Nxe5%2016.Qxe5%20Re8%2017.Qxa5%20b6%2018.Qb5%20a6%2019.Qd3%20c5%2020.d5#23) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20d5%202.exd5%20Nf6%203.Nc3%20Nxd5%204.Bc4%20Nxc3%205.bxc3%20Nc6%206.Bb2%20e5%207.Nf3%20Bg4%208.h3%20Bh5%209.Be2%20Bc5%2010.d4%20exd4%2011.cxd4%20Bb4%2B%2012.c3%20Ba5%2013.O-O%20O-O%2014.Ne5%20Nxe5%2015.dxe5%20Qxd1%2016.Raxd1%20Bxe2%2017.Rfe1%20Bxd1%2018.Rxd1%20Rad8%2019.Re1%20Rfe8%2020.c4#23) |

position 43 (`1r1qk2r/p2b2pp/1p3n2/n3Qp2/P2Pp3/4PP2/3N2PP/R1B1KB1R b KQk - 1 17`), split at ply 1: Qe7 (75% there) vs Kf7 (25%)

| chosen | subpar |
|---|---|
| [17...Qe7] 18.Qxb8+ Qd8 19.Qxd8+ Kxd8 [20.Bb5] Bxb5 [21.axb5] Nd5 22.fxe4 fxe4 23.Nxe4 Re8 [24.Nd6] Rxe3+ 25.Bxe3 | 17...Kf7 [18.Bc4+] [Kf8] 19.Ba3+ Qe7 20.Qxe7# |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20f6%203.c4%20e5%204.e3%20e4%205.Nfd2%20c6%206.Nc3%20Bb4%207.cxd5%20cxd5%208.f3%20f5%209.Qa4%2B%20Nc6%2010.a3%20Bxc3%2011.bxc3%20Bd7%2012.Qb3%20Rb8%2013.c4%20dxc4%2014.Qxc4%20Nf6%2015.a4%20Na5%2016.Qc5%20b6%2017.Qe5%2B%20Qe7%2018.Qxb8%2B%20Qd8%2019.Qxd8%2B%20Kxd8%2020.Bb5%20Bxb5%2021.axb5%20Nd5%2022.fxe4%20fxe4%2023.Nxe4%20Re8%2024.Nd6%20Rxe3%2B%2025.Bxe3#33) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20f6%203.c4%20e5%204.e3%20e4%205.Nfd2%20c6%206.Nc3%20Bb4%207.cxd5%20cxd5%208.f3%20f5%209.Qa4%2B%20Nc6%2010.a3%20Bxc3%2011.bxc3%20Bd7%2012.Qb3%20Rb8%2013.c4%20dxc4%2014.Qxc4%20Nf6%2015.a4%20Na5%2016.Qc5%20b6%2017.Qe5%2B%20Kf7%2018.Bc4%2B%20Kf8%2019.Ba3%2B%20Qe7%2020.Qxe7%23#33) |

position 10 (`2r2rk1/pp1bb1pp/1qn1pn2/3p1p2/PP1P4/2P2N1P/3NBPPB/R1Q2RK1 w - - 1 15`), split at ply 4: b6 (76% there) vs bxa6 (24%)

| chosen | subpar |
|---|---|
| 15.a5 [Qd8] 16.a6 [b6] [17.b5] [Na5] [18.Ne5] [Bd6] 19.Nxd7 Qxd7 20.Bxd6 Qxd6 21.Nf3 Ne4 [22.Qb2] Nxc3 | 15.a5 [Qd8] 16.a6 bxa6 17.Rxa6 Nxb4 [18.Rxa7] Nc6 [19.Ra1] Ne4 20.Nxe4 fxe4 [21.Ne5] Nxe5 22.Bxe5 Bf6 |
| [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nf6%202.d4%20e6%203.Bf4%20c5%204.e3%20cxd4%205.exd4%20Qb6%206.Qc1%20Nc6%207.c3%20Be7%208.Nbd2%20d5%209.h3%20Nh5%2010.Bh2%20O-O%2011.Be2%20Bd7%2012.O-O%20f5%2013.b4%20Nf6%2014.a4%20Rac8%2015.a5%20Qd8%2016.a6%20b6%2017.b5%20Na5%2018.Ne5%20Bd6%2019.Nxd7%20Qxd7%2020.Bxd6%20Qxd6%2021.Nf3%20Ne4%2022.Qb2%20Nxc3#28) | [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nf6%202.d4%20e6%203.Bf4%20c5%204.e3%20cxd4%205.exd4%20Qb6%206.Qc1%20Nc6%207.c3%20Be7%208.Nbd2%20d5%209.h3%20Nh5%2010.Bh2%20O-O%2011.Be2%20Bd7%2012.O-O%20f5%2013.b4%20Nf6%2014.a4%20Rac8%2015.a5%20Qd8%2016.a6%20bxa6%2017.Rxa6%20Nxb4%2018.Rxa7%20Nc6%2019.Ra1%20Ne4%2020.Nxe4%20fxe4%2021.Ne5%20Nxe5%2022.Bxe5%20Bf6#28) |

#### W #3 (k = 0): latents 49

position 43 (`1r1qk2r/p2b2pp/1p3n2/n3Qp2/P2Pp3/4PP2/3N2PP/R1B1KB1R b KQk - 1 17`), split at ply 1: Qe7 (75% there) vs Kf7 (25%)

| chosen | subpar |
|---|---|
| [17...Qe7] 18.Qxb8+ [Qd8] 19.Qxd8+ Kxd8 20.Bb5 Bxb5 21.axb5 Nd5 22.fxe4 fxe4 23.Nxe4 Re8 24.Nd6 Rxe3+ 25.Bxe3 | 17...Kf7 18.Bc4+ Kf8 19.Ba3+ [Qe7] 20.Qxe7# |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20f6%203.c4%20e5%204.e3%20e4%205.Nfd2%20c6%206.Nc3%20Bb4%207.cxd5%20cxd5%208.f3%20f5%209.Qa4%2B%20Nc6%2010.a3%20Bxc3%2011.bxc3%20Bd7%2012.Qb3%20Rb8%2013.c4%20dxc4%2014.Qxc4%20Nf6%2015.a4%20Na5%2016.Qc5%20b6%2017.Qe5%2B%20Qe7%2018.Qxb8%2B%20Qd8%2019.Qxd8%2B%20Kxd8%2020.Bb5%20Bxb5%2021.axb5%20Nd5%2022.fxe4%20fxe4%2023.Nxe4%20Re8%2024.Nd6%20Rxe3%2B%2025.Bxe3#33) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20f6%203.c4%20e5%204.e3%20e4%205.Nfd2%20c6%206.Nc3%20Bb4%207.cxd5%20cxd5%208.f3%20f5%209.Qa4%2B%20Nc6%2010.a3%20Bxc3%2011.bxc3%20Bd7%2012.Qb3%20Rb8%2013.c4%20dxc4%2014.Qxc4%20Nf6%2015.a4%20Na5%2016.Qc5%20b6%2017.Qe5%2B%20Kf7%2018.Bc4%2B%20Kf8%2019.Ba3%2B%20Qe7%2020.Qxe7%23#33) |

position 17 (`r3k2r/pp2qp1p/2n1bnp1/2p5/2N3P1/2bPBP2/P1PN3P/3QKB1R w Kkq - 1 14`), split at ply 5: Qe2 (81% there) vs Kf1 (19%)

| chosen | subpar |
|---|---|
| 14.Bg2 Bxc4 15.dxc4 Qxe3+ [16.Qe2] Bxd2+ 17.Kd1 Qxe2+ 18.Kxe2 Bf4 19.Re1 O-O 20.Kf1 Rfe8 21.Rd1 [Rad8] | 14.Bg2 Bxc4 15.dxc4 Qxe3+ 16.Kf1 Bxd2 17.Qb1 b6 18.Qb5 Qe1# |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.d3%20g6%203.Nf3%20Bg7%204.e5%20Nc6%205.Bf4%20d6%206.exd6%20Bxb2%207.dxe7%20Qxe7%2B%208.Be3%20Bxa1%209.Na3%20Bc3%2B%2010.Nd2%20Nf6%2011.Nc4%20Bg4%2012.f3%20Bf5%2013.g4%20Be6%2014.Bg2%20Bxc4%2015.dxc4%20Qxe3%2B%2016.Qe2%20Bxd2%2B%2017.Kd1%20Qxe2%2B%2018.Kxe2%20Bf4%2019.Re1%20O-O%2020.Kf1%20Rfe8%2021.Rd1%20Rad8#26) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.d3%20g6%203.Nf3%20Bg7%204.e5%20Nc6%205.Bf4%20d6%206.exd6%20Bxb2%207.dxe7%20Qxe7%2B%208.Be3%20Bxa1%209.Na3%20Bc3%2B%2010.Nd2%20Nf6%2011.Nc4%20Bg4%2012.f3%20Bf5%2013.g4%20Be6%2014.Bg2%20Bxc4%2015.dxc4%20Qxe3%2B%2016.Kf1%20Bxd2%2017.Qb1%20b6%2018.Qb5%20Qe1%23#26) |

position 27 (`r3kb1r/1p2pp1p/p2p1np1/4n1Q1/3B4/PP2P3/2qPNPPP/R4RK1 b kq - 1 15`), split at ply 8: Rad1 (77% there) vs Nf3 (19%)

| chosen | subpar |
|---|---|
| 15...Nd3 16.Bxf6 exf6 17.Qxf6 Rg8 18.Nd4 Qxd2 [19.Rad1] Qc3 [20.Qf3] Ne5 21.Qxb7 Rd8 22.Qxa6 Be7 23.Qb5+ | 15...Nd3 16.Bxf6 exf6 17.Qxf6 Rg8 18.Nd4 Qxd2 19.Nf3 Qc3 20.Qxc3 Ne5 21.Nxe5 dxe5 22.Qxe5+ Be7 23.Qc7 |
| [Lichess](https://lichess.org/analysis/pgn/1.e3%20c5%202.Qh5%20Nf6%203.Qxc5%20g6%204.Bc4%20d6%205.Qg5%20Nc6%206.a3%20Ne5%207.Bb5%2B%20Bd7%208.Ba4%20Bxa4%209.b3%20Bd7%2010.Bb2%20Qc7%2011.Nc3%20a6%2012.Nge2%20Bb5%2013.O-O%20Bxe2%2014.Nxe2%20Qxc2%2015.Bd4%20Nd3%2016.Bxf6%20exf6%2017.Qxf6%20Rg8%2018.Nd4%20Qxd2%2019.Rad1%20Qc3%2020.Qf3%20Ne5%2021.Qxb7%20Rd8%2022.Qxa6%20Be7%2023.Qb5%2B#29) | [Lichess](https://lichess.org/analysis/pgn/1.e3%20c5%202.Qh5%20Nf6%203.Qxc5%20g6%204.Bc4%20d6%205.Qg5%20Nc6%206.a3%20Ne5%207.Bb5%2B%20Bd7%208.Ba4%20Bxa4%209.b3%20Bd7%2010.Bb2%20Qc7%2011.Nc3%20a6%2012.Nge2%20Bb5%2013.O-O%20Bxe2%2014.Nxe2%20Qxc2%2015.Bd4%20Nd3%2016.Bxf6%20exf6%2017.Qxf6%20Rg8%2018.Nd4%20Qxd2%2019.Nf3%20Qc3%2020.Qxc3%20Ne5%2021.Nxe5%20dxe5%2022.Qxe5%2B%20Be7%2023.Qc7#29) |

#### W #4 (k = 0): latents 19

position 8 (`r2qkb1r/pp3ppp/4pn2/8/b1pP4/PnP1PN1P/R1Q2PP1/1NB1KB1R w Kkq - 6 12`), split at ply 5: Bxb3 (75% there) vs O-O (25%)

| chosen | subpar |
|---|---|
| [12.Qb2] [Ne4] [13.Bxc4] [Qa5] [14.Bxb3] [Bxb3] 15.Qxb3 [Rc8] [16.Bd2] [Bxa3] 17.Nxa3 [Nxc3] 18.Bxc3 Qxc3+ 19.Qxc3 Rxc3 | [12.Qb2] [Ne4] [13.Bxc4] [Qa5] 14.O-O [Bd6] [15.Bxb3] [Bxb3] 16.Qxb3 O-O 17.Qxb7 [Rab8] 18.Qxe4 [Rxb1] 19.Qxb1 Qxc3 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Qb2%20Ne4%2013.Bxc4%20Qa5%2014.Bxb3%20Bxb3%2015.Qxb3%20Rc8%2016.Bd2%20Bxa3%2017.Nxa3%20Nxc3%2018.Bxc3%20Qxc3%2B%2019.Qxc3%20Rxc3#22) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Qb2%20Ne4%2013.Bxc4%20Qa5%2014.O-O%20Bd6%2015.Bxb3%20Bxb3%2016.Qxb3%20O-O%2017.Qxb7%20Rab8%2018.Qxe4%20Rxb1%2019.Qxb1%20Qxc3#22) |

position 43 (`1r1qk2r/p2b2pp/1p3n2/n3Qp2/P2Pp3/4PP2/3N2PP/R1B1KB1R b KQk - 1 17`), split at ply 1: Qe7 (75% there) vs Kf7 (25%)

| chosen | subpar |
|---|---|
| [17...Qe7] [18.Qxb8+] [Qd8] [19.Qxd8+] [Kxd8] [20.Bb5] [Bxb5] 21.axb5 [Nd5] [22.fxe4] fxe4 23.Nxe4 [Re8] 24.Nd6 [Rxe3+] 25.Bxe3 | 17...Kf7 [18.Bc4+] [Kf8] [19.Ba3+] [Qe7] 20.Qxe7# |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20f6%203.c4%20e5%204.e3%20e4%205.Nfd2%20c6%206.Nc3%20Bb4%207.cxd5%20cxd5%208.f3%20f5%209.Qa4%2B%20Nc6%2010.a3%20Bxc3%2011.bxc3%20Bd7%2012.Qb3%20Rb8%2013.c4%20dxc4%2014.Qxc4%20Nf6%2015.a4%20Na5%2016.Qc5%20b6%2017.Qe5%2B%20Qe7%2018.Qxb8%2B%20Qd8%2019.Qxd8%2B%20Kxd8%2020.Bb5%20Bxb5%2021.axb5%20Nd5%2022.fxe4%20fxe4%2023.Nxe4%20Re8%2024.Nd6%20Rxe3%2B%2025.Bxe3#33) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20f6%203.c4%20e5%204.e3%20e4%205.Nfd2%20c6%206.Nc3%20Bb4%207.cxd5%20cxd5%208.f3%20f5%209.Qa4%2B%20Nc6%2010.a3%20Bxc3%2011.bxc3%20Bd7%2012.Qb3%20Rb8%2013.c4%20dxc4%2014.Qxc4%20Nf6%2015.a4%20Na5%2016.Qc5%20b6%2017.Qe5%2B%20Kf7%2018.Bc4%2B%20Kf8%2019.Ba3%2B%20Qe7%2020.Qxe7%23#33) |

position 21 (`r1b2rk1/pp2q1pp/3b4/5p1Q/4p3/2N5/PPP2PPP/R1BR2K1 w - - 2 17`), split at ply 9: Nc7 (78% there) vs Bxe7 (22%)

| chosen | subpar |
|---|---|
| 17.Bg5 Qe5 [18.Rd5] Qe6 19.Nb5 g6 20.Qh6 Be7 [21.Nc7] Qc6 [22.Nxa8] Qxd5 23.Bxe7 Re8 24.Bf6 Re7 | 17.Bg5 Qe5 [18.Rd5] Qe6 19.Nb5 g6 20.Qh6 Be7 21.Bxe7 Qxe7 22.Rad1 Be6 23.Rd6 a6 24.Nd4 Bxa2 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Qxd4%20Nf6%205.e5%20Nfd7%206.exd6%20Nc6%207.Qe3%20e6%208.Nc3%20Bxd6%209.Bd3%20O-O%2010.O-O%20Nde5%2011.Nxe5%20Nxe5%2012.Be4%20f5%2013.Bf3%20Nxf3%2B%2014.Qxf3%20e5%2015.Rd1%20e4%2016.Qh5%20Qe7%2017.Bg5%20Qe5%2018.Rd5%20Qe6%2019.Nb5%20g6%2020.Qh6%20Be7%2021.Nc7%20Qc6%2022.Nxa8%20Qxd5%2023.Bxe7%20Re8%2024.Bf6%20Re7#32) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Qxd4%20Nf6%205.e5%20Nfd7%206.exd6%20Nc6%207.Qe3%20e6%208.Nc3%20Bxd6%209.Bd3%20O-O%2010.O-O%20Nde5%2011.Nxe5%20Nxe5%2012.Be4%20f5%2013.Bf3%20Nxf3%2B%2014.Qxf3%20e5%2015.Rd1%20e4%2016.Qh5%20Qe7%2017.Bg5%20Qe5%2018.Rd5%20Qe6%2019.Nb5%20g6%2020.Qh6%20Be7%2021.Bxe7%20Qxe7%2022.Rad1%20Be6%2023.Rd6%20a6%2024.Nd4%20Bxa2#32) |

#### W #5 (k = 0): latents 405

position 44 (`6rr/ppkn3p/8/2pQ4/5Bb1/3B3P/PqP5/2R2KNR b - - 0 24`), split at ply 3: Rf8 (77% there) vs Qf6 (23%)

| chosen | subpar |
|---|---|
| 24...Kc8 25.Qc4 [Rf8] 26.hxg4 Rxf4+ 27.Qxf4 [Rf8] 28.Qxf8+ [Nxf8] 29.Bf5+ Kc7 30.Nf3 Qxc1+ 31.Kg2 Qxc2+ 32.Bxc2 | 24...Kc8 25.Qc4 Qf6 26.hxg4 Rxg4 27.Ne2 Rhg8 28.Rg1 Rxg1+ 29.Nxg1 Rxg1+ 30.Kxg1 Qg6+ 31.Kf2 Qf6 32.Ke3 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Bc4%20fxe4%204.d3%20d5%205.Bb3%20exd3%206.Qxd3%20e4%207.Qd4%20Nf6%208.Nc3%20c5%209.Qe5%2B%20Be7%2010.Nxd5%20Nxd5%2011.Bxd5%20Qa5%2B%2012.Bd2%20Qb6%2013.Qxg7%20Bf6%2014.Qf7%2B%20Kd8%2015.Bxe4%20Bg4%2016.Qd5%2B%20Nd7%2017.h3%20Bh4%2B%2018.g3%20Bxg3%2B%2019.Kf1%20Qb5%2B%2020.Bd3%20Qxb2%2021.Qg5%2B%20Kc7%2022.Rc1%20Rag8%2023.Qd5%20Bxf4%2024.Bxf4%2B%20Kc8%2025.Qc4%20Rf8%2026.hxg4%20Rxf4%2B%2027.Qxf4%20Rf8%2028.Qxf8%2B%20Nxf8%2029.Bf5%2B%20Kc7%2030.Nf3%20Qxc1%2B%2031.Kg2%20Qxc2%2B%2032.Bxc2#47) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Bc4%20fxe4%204.d3%20d5%205.Bb3%20exd3%206.Qxd3%20e4%207.Qd4%20Nf6%208.Nc3%20c5%209.Qe5%2B%20Be7%2010.Nxd5%20Nxd5%2011.Bxd5%20Qa5%2B%2012.Bd2%20Qb6%2013.Qxg7%20Bf6%2014.Qf7%2B%20Kd8%2015.Bxe4%20Bg4%2016.Qd5%2B%20Nd7%2017.h3%20Bh4%2B%2018.g3%20Bxg3%2B%2019.Kf1%20Qb5%2B%2020.Bd3%20Qxb2%2021.Qg5%2B%20Kc7%2022.Rc1%20Rag8%2023.Qd5%20Bxf4%2024.Bxf4%2B%20Kc8%2025.Qc4%20Qf6%2026.hxg4%20Rxg4%2027.Ne2%20Rhg8%2028.Rg1%20Rxg1%2B%2029.Nxg1%20Rxg1%2B%2030.Kxg1%20Qg6%2B%2031.Kf2%20Qf6%2032.Ke3#47) |

position 15 (`r1q2rk1/2B2ppp/p1Q1p3/3p4/3Pn3/P3P3/P1P2PPP/R4RK1 b - - 4 17`), split at ply 2: f3 (75% there) vs Rab1 (22%)

| chosen | subpar |
|---|---|
| 17...Ra7 [18.f3] Rxc7 [19.Qa4] Nc3 [20.Qb3] Ne2+ 21.Kf2 Rxc2 22.Ke1 Nc3 23.Rf2 Rxf2 24.Kxf2 Nb5 25.a4 | 17...Ra7 18.Rab1 Rxc7 19.Qa4 Nd2 20.Rfd1 Nxb1 21.Rxb1 Rxc2 22.h3 Rc1+ 23.Rxc1 Qxc1+ 24.Kh2 Rc8 25.Qxa6 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bf4%20d6%203.e3%20Nc6%204.Bb5%20Bd7%205.Bxc6%20Bxc6%206.Nf3%20Bxf3%207.Qxf3%20e6%208.Qxb7%20d5%209.Bxc7%20Qc8%2010.Qc6%2B%20Nd7%2011.Na3%20Be7%2012.Nb5%20O-O%2013.Qc3%20a6%2014.Na3%20Bxa3%2015.bxa3%20Nf6%2016.O-O%20Ne4%2017.Qc6%20Ra7%2018.f3%20Rxc7%2019.Qa4%20Nc3%2020.Qb3%20Ne2%2B%2021.Kf2%20Rxc2%2022.Ke1%20Nc3%2023.Rf2%20Rxf2%2024.Kxf2%20Nb5%2025.a4#33) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bf4%20d6%203.e3%20Nc6%204.Bb5%20Bd7%205.Bxc6%20Bxc6%206.Nf3%20Bxf3%207.Qxf3%20e6%208.Qxb7%20d5%209.Bxc7%20Qc8%2010.Qc6%2B%20Nd7%2011.Na3%20Be7%2012.Nb5%20O-O%2013.Qc3%20a6%2014.Na3%20Bxa3%2015.bxa3%20Nf6%2016.O-O%20Ne4%2017.Qc6%20Ra7%2018.Rab1%20Rxc7%2019.Qa4%20Nd2%2020.Rfd1%20Nxb1%2021.Rxb1%20Rxc2%2022.h3%20Rc1%2B%2023.Rxc1%20Qxc1%2B%2024.Kh2%20Rc8%2025.Qxa6#33) |

position 47 (`r2qr1k1/pp3ppp/1bn5/3p4/3Nb2n/1NP2PBP/PP2B1PK/R2Q1R2 b - - 0 16`), split at ply 8: Bd3 (78% there) vs Re1 (17%)

| chosen | subpar |
|---|---|
| 16...Bg6 [17.Nxc6] bxc6 [18.Nd4] Nf5 [19.Nxf5] Bxf5 [20.Bd3] Bxd3 [21.Qxd3] Bc7 [22.Bxc7] Qxc7+ [23.Kh1] Rab8 [24.Rab1] | 16...Bg6 [17.Nxc6] bxc6 [18.Nd4] Nf5 [19.Nxf5] Bxf5 20.Re1 Bc7 21.f4 Qf6 22.Bd3 Rxe1 23.Qxe1 Bxd3 24.Rd1 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bg6%2017.Nxc6%20bxc6%2018.Nd4%20Nf5%2019.Nxf5%20Bxf5%2020.Bd3%20Bxd3%2021.Qxd3%20Bc7%2022.Bxc7%20Qxc7%2B%2023.Kh1%20Rab8%2024.Rab1#31) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bg6%2017.Nxc6%20bxc6%2018.Nd4%20Nf5%2019.Nxf5%20Bxf5%2020.Re1%20Bc7%2021.f4%20Qf6%2022.Bd3%20Rxe1%2023.Qxe1%20Bxd3%2024.Rd1#31) |

#### W #6 (k = 0): latents 556

position 25 (`1r3r2/pb4kp/1p4p1/2pnP3/4B3/2P4P/PP1N2P1/R4RK1 w - - 3 21`), split at ply 6: Rxb7 (75% there) vs Rxf1+ (25%)

| chosen | subpar |
|---|---|
| [21.c4] [Ne3] [22.Bxb7] [Nxf1] [23.Rxf1] [Rxb7] [24.Ne4] Rxf1+ [25.Kxf1] [Re7] [26.Nd6] Rxe5 [27.Nb5] a6 28.Nc7 a5 | [21.c4] [Ne3] [22.Bxb7] [Nxf1] [23.Rxf1] Rxf1+ [24.Kxf1] [Rxb7] [25.Ne4] [Re7] [26.Ke2] Rxe5 [27.Ke3] Kf7 [28.g4] Ke6 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.c4%20Ne3%2022.Bxb7%20Nxf1%2023.Rxf1%20Rxb7%2024.Ne4%20Rxf1%2B%2025.Kxf1%20Re7%2026.Nd6%20Rxe5%2027.Nb5%20a6%2028.Nc7%20a5#40) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.c4%20Ne3%2022.Bxb7%20Nxf1%2023.Rxf1%20Rxf1%2B%2024.Kxf1%20Rxb7%2025.Ne4%20Re7%2026.Ke2%20Rxe5%2027.Ke3%20Kf7%2028.g4%20Ke6#40) |

position 5 (`r3kbnr/pbpn2pp/1p2q3/1Q2p1B1/4P3/2N2N2/PPP3PP/2KR1B1R b kq - 2 11`), split at ply 5: Bxd5 (80% there) vs O-O-O (18%)

| chosen | subpar |
|---|---|
| 11...Nf6 [12.Bxf6] [gxf6] 13.Nd5 [Bxd5] 14.exd5 Qd6 15.Qc6 Qxc6 16.dxc6 [Nc5] 17.Bb5 a6 18.Bc4 b5 19.Bd5 | 11...Nf6 [12.Bxf6] [gxf6] 13.Nd5 O-O-O [14.Bc4] [Bh6+] [15.Kb1] Nc5 16.Nxb6+ axb6 17.Bxe6+ Nxe6 18.Rxd8+ Rxd8 19.a3 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Nf3%20d6%204.Qe2%20Qe7%205.d3%20b6%206.Nc3%20Bb7%207.fxe5%20dxe5%208.Bg5%20Qe6%209.O-O-O%20fxe4%2010.dxe4%20Nd7%2011.Qb5%20Nf6%2012.Bxf6%20gxf6%2013.Nd5%20Bxd5%2014.exd5%20Qd6%2015.Qc6%20Qxc6%2016.dxc6%20Nc5%2017.Bb5%20a6%2018.Bc4%20b5%2019.Bd5#21) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Nf3%20d6%204.Qe2%20Qe7%205.d3%20b6%206.Nc3%20Bb7%207.fxe5%20dxe5%208.Bg5%20Qe6%209.O-O-O%20fxe4%2010.dxe4%20Nd7%2011.Qb5%20Nf6%2012.Bxf6%20gxf6%2013.Nd5%20O-O-O%2014.Bc4%20Bh6%2B%2015.Kb1%20Nc5%2016.Nxb6%2B%20axb6%2017.Bxe6%2B%20Nxe6%2018.Rxd8%2B%20Rxd8%2019.a3#21) |

position 20 (`r3k1nr/1p1n4/1p1bp1pp/3p1p2/3P4/2P2N2/PP1N1PPP/R1B2RK1 b kq - 1 14`), split at ply 9: h4 (83% there) vs Ngf6 (17%)

| chosen | subpar |
|---|---|
| 14...g5 15.h3 g4 16.hxg4 fxg4 17.Nh2 h5 18.g3 [h4] 19.Nxg4 hxg3 20.fxg3 [Bxg3] 21.Nf3 Ngf6 22.Nxf6+ | 14...g5 15.h3 g4 16.hxg4 fxg4 17.Nh2 h5 18.g3 Ngf6 19.Re1 e5 20.dxe5 Nxe5 21.f3 gxf3 22.Ndxf3 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20e6%202.Bf4%20c5%203.e3%20cxd4%204.exd4%20Qb6%205.Bc1%20d5%206.Nf3%20Bb4%2B%207.c3%20Bd6%208.Bd3%20g6%209.Nbd2%20f5%2010.Qb3%20h6%2011.Qxb6%20axb6%2012.Bb5%2B%20Bd7%2013.Bxd7%2B%20Nxd7%2014.O-O%20g5%2015.h3%20g4%2016.hxg4%20fxg4%2017.Nh2%20h5%2018.g3%20h4%2019.Nxg4%20hxg3%2020.fxg3%20Bxg3%2021.Nf3%20Ngf6%2022.Nxf6%2B#27) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20e6%202.Bf4%20c5%203.e3%20cxd4%204.exd4%20Qb6%205.Bc1%20d5%206.Nf3%20Bb4%2B%207.c3%20Bd6%208.Bd3%20g6%209.Nbd2%20f5%2010.Qb3%20h6%2011.Qxb6%20axb6%2012.Bb5%2B%20Bd7%2013.Bxd7%2B%20Nxd7%2014.O-O%20g5%2015.h3%20g4%2016.hxg4%20fxg4%2017.Nh2%20h5%2018.g3%20Ngf6%2019.Re1%20e5%2020.dxe5%20Nxe5%2021.f3%20gxf3%2022.Ndxf3#27) |

#### W #7 (k = 0): latents 323

position 19 (`r4r1k/ppq1b1pp/2npQ3/4p3/1PP5/P1P2N2/5PPP/R1B2RK1 w - - 1 18`), split at ply 12: Kh7 (75% there) vs Rf8 (25%)

| chosen | subpar |
|---|---|
| 18.Bg5 Bxg5 19.Nxg5 Rae8 20.Qh3 h6 21.Ne6 Rxe6 [22.Qxe6] Rf6 23.Qe8+ [Kh7] 24.b5 [Na5] 25.Qa8 Nxc4 | 18.Bg5 Bxg5 19.Nxg5 Rae8 20.Qh3 h6 21.Ne6 Rxe6 [22.Qxe6] Rf6 23.Qe8+ Rf8 24.Qxf8+ [Kh7] 25.Qf5+ Kh8 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bc4%20Nf6%204.d3%20Be7%205.O-O%20O-O%206.Nc3%20d6%207.a3%20Be6%208.Qe2%20Bxc4%209.dxc4%20Nd7%2010.Nd5%20Nc5%2011.b4%20Ne6%2012.c3%20f5%2013.exf5%20Rxf5%2014.Qe4%20Rf8%2015.Qg4%20Qd7%2016.Nxc7%20Qxc7%2017.Qxe6%2B%20Kh8%2018.Bg5%20Bxg5%2019.Nxg5%20Rae8%2020.Qh3%20h6%2021.Ne6%20Rxe6%2022.Qxe6%20Rf6%2023.Qe8%2B%20Kh7%2024.b5%20Na5%2025.Qa8%20Nxc4#34) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bc4%20Nf6%204.d3%20Be7%205.O-O%20O-O%206.Nc3%20d6%207.a3%20Be6%208.Qe2%20Bxc4%209.dxc4%20Nd7%2010.Nd5%20Nc5%2011.b4%20Ne6%2012.c3%20f5%2013.exf5%20Rxf5%2014.Qe4%20Rf8%2015.Qg4%20Qd7%2016.Nxc7%20Qxc7%2017.Qxe6%2B%20Kh8%2018.Bg5%20Bxg5%2019.Nxg5%20Rae8%2020.Qh3%20h6%2021.Ne6%20Rxe6%2022.Qxe6%20Rf6%2023.Qe8%2B%20Rf8%2024.Qxf8%2B%20Kh7%2025.Qf5%2B%20Kh8#34) |

position 35 (`3rr1k1/ppp2pp1/5b1p/8/2qP4/7P/PP3PKP/R2Q2R1 w - - 4 21`), split at ply 3: f3 (75% there) vs Kf1 (25%)

| chosen | subpar |
|---|---|
| 21.b3 Qc6+ [22.f3] Rxd4 [23.Qf1] Rd2+ [24.Kh1] Bxa1 [25.Qxa1] Qxf3+ 26.Rg2 Qxg2# | 21.b3 Qc6+ 22.Kf1 Rxd4 23.Qh5 Qa6+ 24.Kg2 Qc6+ 25.f3 Rd2+ 26.Kh1 Bxa1 27.Rxa1 Qxf3+ 28.Qxf3 Ree2 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nc3%20Nf6%203.d4%20exd4%204.Qxd4%20Nc6%205.Qd1%20d6%206.Bb5%20Be7%207.Bg5%20h6%208.Bxf6%20Bxf6%209.Qf3%20O-O%2010.Nh3%20Nd4%2011.Qd1%20Bxh3%2012.gxh3%20d5%2013.exd5%20Qd6%2014.Be2%20Rfe8%2015.Ne4%20Rxe4%2016.c3%20Rxe2%2B%2017.Kf1%20Ree8%2018.cxd4%20Qxd5%2019.Rg1%20Qc4%2B%2020.Kg2%20Rad8%2021.b3%20Qc6%2B%2022.f3%20Rxd4%2023.Qf1%20Rd2%2B%2024.Kh1%20Bxa1%2025.Qxa1%20Qxf3%2B%2026.Rg2%20Qxg2%23#40) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nc3%20Nf6%203.d4%20exd4%204.Qxd4%20Nc6%205.Qd1%20d6%206.Bb5%20Be7%207.Bg5%20h6%208.Bxf6%20Bxf6%209.Qf3%20O-O%2010.Nh3%20Nd4%2011.Qd1%20Bxh3%2012.gxh3%20d5%2013.exd5%20Qd6%2014.Be2%20Rfe8%2015.Ne4%20Rxe4%2016.c3%20Rxe2%2B%2017.Kf1%20Ree8%2018.cxd4%20Qxd5%2019.Rg1%20Qc4%2B%2020.Kg2%20Rad8%2021.b3%20Qc6%2B%2022.Kf1%20Rxd4%2023.Qh5%20Qa6%2B%2024.Kg2%20Qc6%2B%2025.f3%20Rd2%2B%2026.Kh1%20Bxa1%2027.Rxa1%20Qxf3%2B%2028.Qxf3%20Ree2#40) |

position 29 (`r1b1k1nr/p2ppp1p/6p1/8/8/q7/P1P1BPPP/R2Q1K1R w kq - 0 15`), split at ply 5: Qxe2 (77% there) vs Kxe2 (23%)

| chosen | subpar |
|---|---|
| 15.Bf3 Ba6+ [16.Be2] Bxe2+ [17.Qxe2] Nf6 18.g3 O-O 19.Kg2 Qd6 20.Rhd1 Qc6+ [21.Kg1] Rfe8 [22.Rab1] Rab8 | 15.Bf3 Ba6+ [16.Be2] Bxe2+ 17.Kxe2 Nf6 18.Re1 O-O 19.Kf1 Qa6+ 20.Kg1 e6 21.Qf3 Nd5 22.Rad1 Rac8 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20g6%205.Nc3%20Bg7%206.Be3%20Nf6%207.Nxc6%20bxc6%208.e5%20Ng8%209.Bd4%20c5%2010.Bxc5%20Qc7%2011.Ba3%20Bxe5%2012.Be2%20Bxc3%2B%2013.bxc3%20Qxc3%2B%2014.Kf1%20Qxa3%2015.Bf3%20Ba6%2B%2016.Be2%20Bxe2%2B%2017.Qxe2%20Nf6%2018.g3%20O-O%2019.Kg2%20Qd6%2020.Rhd1%20Qc6%2B%2021.Kg1%20Rfe8%2022.Rab1%20Rab8#28) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20g6%205.Nc3%20Bg7%206.Be3%20Nf6%207.Nxc6%20bxc6%208.e5%20Ng8%209.Bd4%20c5%2010.Bxc5%20Qc7%2011.Ba3%20Bxe5%2012.Be2%20Bxc3%2B%2013.bxc3%20Qxc3%2B%2014.Kf1%20Qxa3%2015.Bf3%20Ba6%2B%2016.Be2%20Bxe2%2B%2017.Kxe2%20Nf6%2018.Re1%20O-O%2019.Kf1%20Qa6%2B%2020.Kg1%20e6%2021.Qf3%20Nd5%2022.Rad1%20Rac8#28) |

#### W #8 (k = 0): latents 705

position 11 (`r3k2r/p3bp2/qn2p3/1R2Pp1p/3P3P/3Q1N2/3B1PP1/1R4K1 w kq - 3 21`), split at ply 9: Ng5 (76% there) vs Rb5 (24%)

| chosen | subpar |
|---|---|
| [21.Ba5] O-O [22.Bxb6] axb6 [23.Rxb6] Qa2 [24.R6b2] [Qd5] [25.Ng5] [Bxg5] [26.hxg5] [Kg7] 27.Qh3 Kg6 28.Qxh5+ Kxh5 | [21.Ba5] O-O [22.Bxb6] axb6 [23.Rxb6] Qa2 [24.R6b2] [Qd5] 25.Rb5 Qe4 [26.Qxe4] fxe4 27.Nd2 Bxh4 [28.Nxe4] Be7 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.e5%20Bf5%204.h4%20h5%205.Bd3%20Bxd3%206.Qxd3%20Qa5%2B%207.b4%20Qxb4%2B%208.Nd2%20Qb5%209.c4%20dxc4%2010.Nxc4%20e6%2011.Bd2%20Qa6%2012.Nf3%20Nh6%2013.O-O%20Nf5%2014.Rab1%20b5%2015.Ne3%20g6%2016.a4%20Be7%2017.Nxf5%20gxf5%2018.axb5%20cxb5%2019.Rxb5%20Nd7%2020.Rfb1%20Nb6%2021.Ba5%20O-O%2022.Bxb6%20axb6%2023.Rxb6%20Qa2%2024.R6b2%20Qd5%2025.Ng5%20Bxg5%2026.hxg5%20Kg7%2027.Qh3%20Kg6%2028.Qxh5%2B%20Kxh5#40) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.e5%20Bf5%204.h4%20h5%205.Bd3%20Bxd3%206.Qxd3%20Qa5%2B%207.b4%20Qxb4%2B%208.Nd2%20Qb5%209.c4%20dxc4%2010.Nxc4%20e6%2011.Bd2%20Qa6%2012.Nf3%20Nh6%2013.O-O%20Nf5%2014.Rab1%20b5%2015.Ne3%20g6%2016.a4%20Be7%2017.Nxf5%20gxf5%2018.axb5%20cxb5%2019.Rxb5%20Nd7%2020.Rfb1%20Nb6%2021.Ba5%20O-O%2022.Bxb6%20axb6%2023.Rxb6%20Qa2%2024.R6b2%20Qd5%2025.Rb5%20Qe4%2026.Qxe4%20fxe4%2027.Nd2%20Bxh4%2028.Nxe4%20Be7#40) |

position 9 (`1k2r3/Rpp1qp1p/3pbb2/8/5Qr1/3PBN2/1PP1BPPP/5RK1 w - - 3 19`), split at ply 9: Bxd4 (78% there) vs Rxd4 (22%)

| chosen | subpar |
|---|---|
| 19.Qa4 Rxa4 20.Rxa4 [Bxb2] [21.Ba7+] Kc8 [22.Nd4] Bxd4 [23.Bxd4] Bd7 24.Ra8# | 19.Qa4 Rxa4 20.Rxa4 [Bxb2] [21.Ba7+] Kc8 [22.Nd4] Bxd4 23.Rxd4 Kd7 24.Bh5 Ra8 25.Ra1 Bd5 [26.Rxd5] Rxa7 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Qh5%20Nf6%203.Qxe5%2B%20Be7%204.d3%20Nc6%205.Qg5%20Nxe4%206.Qxg7%20Bf6%207.Qg4%20d6%208.Qxe4%2B%20Be6%209.Nf3%20Qd7%2010.Nc3%20O-O-O%2011.Be2%20Rde8%2012.O-O%20Bxa2%2013.Qa4%20Be6%2014.Qf4%20Qe7%2015.Nb5%20Rhg8%2016.Nxa7%2B%20Nxa7%2017.Rxa7%20Kb8%2018.Be3%20Rg4%2019.Qa4%20Rxa4%2020.Rxa4%20Bxb2%2021.Ba7%2B%20Kc8%2022.Nd4%20Bxd4%2023.Bxd4%20Bd7%2024.Ra8%23#36) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Qh5%20Nf6%203.Qxe5%2B%20Be7%204.d3%20Nc6%205.Qg5%20Nxe4%206.Qxg7%20Bf6%207.Qg4%20d6%208.Qxe4%2B%20Be6%209.Nf3%20Qd7%2010.Nc3%20O-O-O%2011.Be2%20Rde8%2012.O-O%20Bxa2%2013.Qa4%20Be6%2014.Qf4%20Qe7%2015.Nb5%20Rhg8%2016.Nxa7%2B%20Nxa7%2017.Rxa7%20Kb8%2018.Be3%20Rg4%2019.Qa4%20Rxa4%2020.Rxa4%20Bxb2%2021.Ba7%2B%20Kc8%2022.Nd4%20Bxd4%2023.Rxd4%20Kd7%2024.Bh5%20Ra8%2025.Ra1%20Bd5%2026.Rxd5%20Rxa7#36) |

position 45 (`r4rk1/pp4pp/1b3q2/1P1pRp2/P7/1QP3P1/5P1P/R5K1 b - - 2 26`), split at ply 11: Rd1+ (76% there) vs Qe1+ (19%)

| chosen | subpar |
|---|---|
| [26...Qxe5] 27.Rd1 [Rad8] 28.c4 dxc4 29.Qxc4+ Kh8 30.Rxd8 [Rxd8] 31.Qh4 [Rd1+] 32.Kg2 [Qe4+] 33.Qxe4 [fxe4] 34.f3 | [26...Qxe5] 27.Rd1 [Rad8] 28.c4 dxc4 29.Qxc4+ Kh8 30.Rxd8 [Rxd8] 31.Qh4 Qe1+ 32.Kg2 Qxf2+ 33.Kh3 Qf1# |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.e5%20c5%204.dxc5%20Nc6%205.Bf4%20e6%206.Bb5%20Bd7%207.Na3%20Bxc5%208.Nf3%20Nge7%209.O-O%20Ng6%2010.Bg5%20f6%2011.Bh4%20Nxh4%2012.Nxh4%20Nxe5%2013.Bxd7%2B%20Qxd7%2014.c3%20O-O%2015.b4%20Bb6%2016.b5%20Qe7%2017.Nc2%20Ng4%2018.Nd4%20Ne5%2019.a4%20Nc4%2020.Re1%20f5%2021.Rxe6%20Qxh4%2022.g3%20Qg5%2023.Nf3%20Qd8%2024.Ne5%20Nxe5%2025.Rxe5%20Qf6%2026.Qb3%20Qxe5%2027.Rd1%20Rad8%2028.c4%20dxc4%2029.Qxc4%2B%20Kh8%2030.Rxd8%20Rxd8%2031.Qh4%20Rd1%2B%2032.Kg2%20Qe4%2B%2033.Qxe4%20fxe4%2034.f3#51) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.e5%20c5%204.dxc5%20Nc6%205.Bf4%20e6%206.Bb5%20Bd7%207.Na3%20Bxc5%208.Nf3%20Nge7%209.O-O%20Ng6%2010.Bg5%20f6%2011.Bh4%20Nxh4%2012.Nxh4%20Nxe5%2013.Bxd7%2B%20Qxd7%2014.c3%20O-O%2015.b4%20Bb6%2016.b5%20Qe7%2017.Nc2%20Ng4%2018.Nd4%20Ne5%2019.a4%20Nc4%2020.Re1%20f5%2021.Rxe6%20Qxh4%2022.g3%20Qg5%2023.Nf3%20Qd8%2024.Ne5%20Nxe5%2025.Rxe5%20Qf6%2026.Qb3%20Qxe5%2027.Rd1%20Rad8%2028.c4%20dxc4%2029.Qxc4%2B%20Kh8%2030.Rxd8%20Rxd8%2031.Qh4%20Qe1%2B%2032.Kg2%20Qxf2%2B%2033.Kh3%20Qf1%23#51) |

#### W #9 (k = 0): latents 335

position 14 (`2r1k2r/1bqpbpp1/p3p2p/1p4Pn/3nP1BP/2N1BP2/PPPQ4/2KR3R w k - 0 15`), split at ply 7: Qxg5 (79% there) vs Be3 (19%)

| chosen | subpar |
|---|---|
| 15.Bxd4 Ng3 [16.Rhg1] hxg5 [17.hxg5] Bxg5 [18.Qxg5] Ne2+ 19.Nxe2 Qxc2# | 15.Bxd4 Ng3 [16.Rhg1] hxg5 [17.hxg5] Bxg5 18.Be3 Bxe3 19.Qxe3 b4 20.Ne2 Qxc2# |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Bxd4%20Ng3%2016.Rhg1%20hxg5%2017.hxg5%20Bxg5%2018.Qxg5%20Ne2%2B%2019.Nxe2%20Qxc2%23#28) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Bxd4%20Ng3%2016.Rhg1%20hxg5%2017.hxg5%20Bxg5%2018.Be3%20Bxe3%2019.Qxe3%20b4%2020.Ne2%20Qxc2%23#28) |

position 36 (`3r1rk1/1pq1npp1/p1p1P2p/8/4Q3/5N2/PP3PPP/3R1RK1 b - - 0 20`), split at ply 13: Re8 (82% there) vs b5 (18%)

| chosen | subpar |
|---|---|
| 20...Rxd1 21.Rxd1 fxe6 22.Qxe6+ Kh8 23.Rd7 Qf4 24.Qxe7 Qc1+ 25.Qe1 Qxe1+ 26.Nxe1 [Re8] 27.Kf1 b5 28.Rd6 | 20...Rxd1 21.Rxd1 fxe6 22.Qxe6+ Kh8 23.Rd7 Qf4 24.Qxe7 Qc1+ 25.Qe1 Qxe1+ 26.Nxe1 b5 27.Ra7 Rf6 28.Rxa6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.Bb5%20e5%204.O-O%20Bd6%205.c3%20a6%206.Bxc6%20dxc6%207.d4%20cxd4%208.cxd4%20exd4%209.Qxd4%20Bf8%2010.Qc3%20Nf6%2011.Bg5%20Be7%2012.Nbd2%20O-O%2013.Rad1%20Qc7%2014.e5%20Nd5%2015.Qc2%20h6%2016.Bxe7%20Nxe7%2017.Ne4%20Bf5%2018.Qe2%20Bxe4%2019.Qxe4%20Rad8%2020.e6%20Rxd1%2021.Rxd1%20fxe6%2022.Qxe6%2B%20Kh8%2023.Rd7%20Qf4%2024.Qxe7%20Qc1%2B%2025.Qe1%20Qxe1%2B%2026.Nxe1%20Re8%2027.Kf1%20b5%2028.Rd6#39) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.Bb5%20e5%204.O-O%20Bd6%205.c3%20a6%206.Bxc6%20dxc6%207.d4%20cxd4%208.cxd4%20exd4%209.Qxd4%20Bf8%2010.Qc3%20Nf6%2011.Bg5%20Be7%2012.Nbd2%20O-O%2013.Rad1%20Qc7%2014.e5%20Nd5%2015.Qc2%20h6%2016.Bxe7%20Nxe7%2017.Ne4%20Bf5%2018.Qe2%20Bxe4%2019.Qxe4%20Rad8%2020.e6%20Rxd1%2021.Rxd1%20fxe6%2022.Qxe6%2B%20Kh8%2023.Rd7%20Qf4%2024.Qxe7%20Qc1%2B%2025.Qe1%20Qxe1%2B%2026.Nxe1%20b5%2027.Ra7%20Rf6%2028.Rxa6#39) |

position 21 (`r1b2rk1/pp2q1pp/3b4/5p1Q/4p3/2N5/PPP2PPP/R1BR2K1 w - - 2 17`), split at ply 2: Qe5 (82% there) vs Qe6 (16%)

| chosen | subpar |
|---|---|
| 17.Bg5 [Qe5] 18.g3 f4 19.Bxf4 Qxh5 20.Rxd6 Bh3 21.Nxe4 Qf3 22.Nf6+ Rxf6 23.Rxf6 Qg2# | 17.Bg5 Qe6 18.Nb5 Be7 19.Nc7 Qg6 20.Qxg6 hxg6 21.Bxe7 [Rf7] 22.Nxa8 Rxe7 23.Rd8+ Kf7 24.Rxc8 e3 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Qxd4%20Nf6%205.e5%20Nfd7%206.exd6%20Nc6%207.Qe3%20e6%208.Nc3%20Bxd6%209.Bd3%20O-O%2010.O-O%20Nde5%2011.Nxe5%20Nxe5%2012.Be4%20f5%2013.Bf3%20Nxf3%2B%2014.Qxf3%20e5%2015.Rd1%20e4%2016.Qh5%20Qe7%2017.Bg5%20Qe5%2018.g3%20f4%2019.Bxf4%20Qxh5%2020.Rxd6%20Bh3%2021.Nxe4%20Qf3%2022.Nf6%2B%20Rxf6%2023.Rxf6%20Qg2%23#32) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Qxd4%20Nf6%205.e5%20Nfd7%206.exd6%20Nc6%207.Qe3%20e6%208.Nc3%20Bxd6%209.Bd3%20O-O%2010.O-O%20Nde5%2011.Nxe5%20Nxe5%2012.Be4%20f5%2013.Bf3%20Nxf3%2B%2014.Qxf3%20e5%2015.Rd1%20e4%2016.Qh5%20Qe7%2017.Bg5%20Qe6%2018.Nb5%20Be7%2019.Nc7%20Qg6%2020.Qxg6%20hxg6%2021.Bxe7%20Rf7%2022.Nxa8%20Rxe7%2023.Rd8%2B%20Kf7%2024.Rxc8%20e3#32) |

#### W #10 (k = 0): latents 405

position 25 (`1r3r2/pb4kp/1p4p1/2pnP3/4B3/2P4P/PP1N2P1/R4RK1 w - - 3 21`), split at ply 6: Rxb7 (75% there) vs Rxf1+ (25%)

| chosen | subpar |
|---|---|
| [21.c4] [Ne3] [22.Bxb7] [Nxf1] [23.Rxf1] [Rxb7] [24.Ne4] Rxf1+ 25.Kxf1 Re7 26.Nd6 Rxe5 27.Nb5 a6 28.Nc7 a5 | [21.c4] [Ne3] [22.Bxb7] [Nxf1] [23.Rxf1] Rxf1+ 24.Kxf1 Rxb7 25.Ne4 Re7 26.Ke2 Rxe5 27.Ke3 Kf7 28.g4 Ke6 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.c4%20Ne3%2022.Bxb7%20Nxf1%2023.Rxf1%20Rxb7%2024.Ne4%20Rxf1%2B%2025.Kxf1%20Re7%2026.Nd6%20Rxe5%2027.Nb5%20a6%2028.Nc7%20a5#40) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.c4%20Ne3%2022.Bxb7%20Nxf1%2023.Rxf1%20Rxf1%2B%2024.Kxf1%20Rxb7%2025.Ne4%20Re7%2026.Ke2%20Rxe5%2027.Ke3%20Kf7%2028.g4%20Ke6#40) |

position 19 (`r4r1k/ppq1b1pp/2npQ3/4p3/1PP5/P1P2N2/5PPP/R1B2RK1 w - - 1 18`), split at ply 2: Bxg5 (80% there) vs Rf6 (19%)

| chosen | subpar |
|---|---|
| 18.Ng5 [Bxg5] 19.Bxg5 [Rae8] 20.Qg4 [Ne7] 21.Rad1 [Ng6] 22.c5 [dxc5] 23.bxc5 [Qxc5] 24.Rd7 [Qxc3] 25.Rxb7 [Qxa3] | 18.Ng5 Rf6 19.Qg4 h6 20.Ne6 Qd7 21.Qxg7# |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bc4%20Nf6%204.d3%20Be7%205.O-O%20O-O%206.Nc3%20d6%207.a3%20Be6%208.Qe2%20Bxc4%209.dxc4%20Nd7%2010.Nd5%20Nc5%2011.b4%20Ne6%2012.c3%20f5%2013.exf5%20Rxf5%2014.Qe4%20Rf8%2015.Qg4%20Qd7%2016.Nxc7%20Qxc7%2017.Qxe6%2B%20Kh8%2018.Ng5%20Bxg5%2019.Bxg5%20Rae8%2020.Qg4%20Ne7%2021.Rad1%20Ng6%2022.c5%20dxc5%2023.bxc5%20Qxc5%2024.Rd7%20Qxc3%2025.Rxb7%20Qxa3#34) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bc4%20Nf6%204.d3%20Be7%205.O-O%20O-O%206.Nc3%20d6%207.a3%20Be6%208.Qe2%20Bxc4%209.dxc4%20Nd7%2010.Nd5%20Nc5%2011.b4%20Ne6%2012.c3%20f5%2013.exf5%20Rxf5%2014.Qe4%20Rf8%2015.Qg4%20Qd7%2016.Nxc7%20Qxc7%2017.Qxe6%2B%20Kh8%2018.Ng5%20Rf6%2019.Qg4%20h6%2020.Ne6%20Qd7%2021.Qxg7%23#34) |

position 31 (`5r2/5k2/p2q1p1r/1pn4p/8/P1N2Q1P/1P3PP1/3RR1K1 b - - 3 25`), split at ply 11: Kg6 (78% there) vs Rf7 (15%)

| chosen | subpar |
|---|---|
| 25...Qc7 26.Qd5+ [Kg7] 27.b4 [Na4] 28.Nxa4 [bxa4] 29.Rc1 [Qf4] 30.Re7+ [Kg6] 31.Qd3+ [f5] 32.Rc6+ Rf6 33.Rxf6+ | 25...Qc7 26.Qd5+ [Kg7] 27.b4 [Na4] 28.Nxa4 [bxa4] 29.Rc1 [Qf4] 30.Re7+ Rf7 31.Qxf7+ Kh8 32.Qg7# |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.Bb5%20Qc7%204.O-O%20e6%205.Re1%20h5%206.c3%20Nf6%207.d4%20cxd4%208.cxd4%20a6%209.Bf1%20Ng4%2010.h3%20f6%2011.Nc3%20b5%2012.a3%20Bb7%2013.e5%20Nh6%2014.Bxh6%20Rxh6%2015.exf6%20gxf6%2016.d5%20Nd8%2017.Nd4%20Kf7%2018.Be2%20Qe5%2019.Bf3%20Qf4%2020.dxe6%2B%20dxe6%2021.Bxb7%20Nxb7%2022.Nxe6%20Qd6%2023.Nxf8%20Rxf8%2024.Qf3%20Nc5%2025.Rad1%20Qc7%2026.Qd5%2B%20Kg7%2027.b4%20Na4%2028.Nxa4%20bxa4%2029.Rc1%20Qf4%2030.Re7%2B%20Kg6%2031.Qd3%2B%20f5%2032.Rc6%2B%20Rf6%2033.Rxf6%2B#49) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.Bb5%20Qc7%204.O-O%20e6%205.Re1%20h5%206.c3%20Nf6%207.d4%20cxd4%208.cxd4%20a6%209.Bf1%20Ng4%2010.h3%20f6%2011.Nc3%20b5%2012.a3%20Bb7%2013.e5%20Nh6%2014.Bxh6%20Rxh6%2015.exf6%20gxf6%2016.d5%20Nd8%2017.Nd4%20Kf7%2018.Be2%20Qe5%2019.Bf3%20Qf4%2020.dxe6%2B%20dxe6%2021.Bxb7%20Nxb7%2022.Nxe6%20Qd6%2023.Nxf8%20Rxf8%2024.Qf3%20Nc5%2025.Rad1%20Qc7%2026.Qd5%2B%20Kg7%2027.b4%20Na4%2028.Nxa4%20bxa4%2029.Rc1%20Qf4%2030.Re7%2B%20Rf7%2031.Qxf7%2B%20Kh8%2032.Qg7%23#49) |

