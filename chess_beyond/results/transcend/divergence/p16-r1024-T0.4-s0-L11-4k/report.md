# Dynamic concepts with a persistence window

Per model, at 50 positions (1024 rollouts of 16 plies, T = 0.4, the model both colours): a latent on at a ply when z > 0.5 x mu_j. Pairs: at each branching point the most-played move against every move with >= 2% of that point's weight, each by its most frequent line, <= 50 per position. LP: min |v|_1 + 2.0 xi s.t. v . (z^c_tau - z^s_tau) >= 1 - xi for tau = t..t+k. Families: Jaccard >= 0.5 of supports with a family's core, within one half (25 / 25 positions by game); recurrence: the share of the other half's pairs (same k) where the family's mean v (|v|_1 = 1) gives >= 0.5 on every ply of the window; null: 200 random v's per family on rate-matched latents (firing-rate deciles). Persistence: plies in a row from the split with v . d >= 0.5, median over the other half's k = 0 pairs where it is on at the split.

## S

| k | pairs | nonzero v | families | held-out recurrence: median / 90% / max | null 95th: median | null (every draw): 90% / 99% | families above their null 95th (chance: 5%) |
|---|---|---|---|---|---|---|---|
| 0 | 2500 | 100% | 657 | 0.7% / 2.6% / 8.6% | 1.6% | 2.3% / 5.8% | 45 (7%) |
| 2 | 2500 | 35% | 655 | 0.0% / 0.2% / 1.2% | 0.1% | 0.1% / 0.3% | 66 (10%) |
| 4 | 2500 | 17% | 355 | 0.0% / 0.1% / 1.0% | 0.0% | 0.0% / 0.2% | 30 (8%) |
| 6 | 2500 | 14% | 330 | 0.0% / 0.1% / 1.0% | 0.0% | 0.0% / 0.1% | 43 (13%) |

### S: the top 20 families by held-out recurrence

| # | k | latents (weight) | found in | held out on | recurrence | null 95th | persistence (pairs on at split) | positions found |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 619 (1.00) | A (3 v's) | B | 8.6% | 4.9% | 1.0 (108) | 6, 29, 31 |
| 2 | 0 | 19 (1.00) | A (75 v's) | B | 8.2% | 5.7% | 1.0 (102) | 0, 3, 5, 6, 9, 11, 16, 18, 19, 20, 24, 25 ... |
| 3 | 0 | 619 (1.00) | B (3 v's) | A | 7.9% | 5.5% | 1.0 (99) | 1, 13, 15 |
| 4 | 0 | 570 (1.00) | A (5 v's) | B | 7.4% | 4.8% | 1.0 (93) | 3, 7, 20, 28 |
| 5 | 0 | 1831 (1.00) | B (2 v's) | A | 7.4% | 5.5% | 1.0 (92) | 30 |
| 6 | 0 | 19 (1.00) | B (86 v's) | A | 6.5% | 5.8% | 1.0 (81) | 1, 2, 4, 8, 10, 12, 14, 15, 17, 23, 27, 30 ... |
| 7 | 0 | 570 (1.00) | B (9 v's) | A | 6.5% | 5.5% | 1.0 (81) | 10, 23, 27, 30, 32, 41, 44, 47 |
| 8 | 0 | 323 (1.00) | A (13 v's) | B | 6.4% | 5.0% | 1.0 (80) | 3, 11, 18, 19, 24, 31, 38, 45, 46 |
| 9 | 0 | 532 (1.00) | B (2 v's) | A | 6.4% | 5.7% | 1.0 (80) | 10, 15 |
| 10 | 0 | 532 (1.00) | A (7 v's) | B | 5.9% | 5.7% | 1.0 (74) | 7, 11, 19, 28, 29, 45 |
| 11 | 0 | 556 (1.00) | B (4 v's) | A | 5.8% | 5.2% | 1.0 (72) | 2, 36, 40, 43 |
| 12 | 0 | 1640 (1.00) | B (1 v's) | A | 5.8% | 4.6% | 1.0 (72) | 27 |
| 13 | 0 | 705 (1.00) | A (3 v's) | B | 5.7% | 4.9% | 1.0 (71) | 7, 28, 37 |
| 14 | 0 | 705 (1.00) | B (2 v's) | A | 5.7% | 4.3% | 1.0 (71) | 12, 40 |
| 15 | 0 | 49 (1.00) | A (47 v's) | B | 5.6% | 6.1% | 1.0 (70) | 0, 5, 7, 9, 11, 16, 19, 20, 24, 25, 28, 29 ... |
| 16 | 0 | 49 (1.00) | B (46 v's) | A | 5.5% | 5.4% | 1.0 (69) | 1, 2, 4, 10, 12, 17, 22, 23, 27, 30, 40, 42 ... |
| 17 | 0 | 856 (1.00) | B (1 v's) | A | 4.9% | 5.2% | 1.0 (61) | 41 |
| 18 | 0 | 556 (1.00) | A (3 v's) | B | 4.8% | 4.4% | 1.0 (60) | 20, 37 |
| 19 | 0 | 960 (1.00) | B (2 v's) | A | 4.3% | 5.4% | 1.0 (54) | 12, 15 |
| 20 | 0 | 694 (1.00) | B (2 v's) | A | 4.2% | 5.2% | 1.0 (53) | 27, 30 |

#### S #1 (k = 0): latents 619

position 43 (`1r1qk2r/p2b2pp/1p3n2/n3Qp2/P2Pp3/4PP2/3N2PP/R1B1KB1R b KQk - 1 17`), split at ply 2: Ba3 (50% there) vs fxe4 (48%)

| chosen | subpar |
|---|---|
| 17...Kf7 [18.Ba3] Re8 [19.Qf4] Kg8 [20.Bb5] Bxb5 21.axb5 exf3 22.gxf3 Nd5 [23.Qxf5] Nxe3 [24.Qd3] Qh4+ [25.Ke2] | 17...Kf7 18.fxe4 Re8 [19.Qf4] Nxe4 20.Nxe4 Rxe4 [21.Qf3] Qe7 22.Bd3 Rxd4 [23.O-O] [Rxd3] 24.Qxf5+ [Kg8] [25.Qxd3] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20f6%203.c4%20e5%204.e3%20e4%205.Nfd2%20c6%206.Nc3%20Bb4%207.cxd5%20cxd5%208.f3%20f5%209.Qa4%2B%20Nc6%2010.a3%20Bxc3%2011.bxc3%20Bd7%2012.Qb3%20Rb8%2013.c4%20dxc4%2014.Qxc4%20Nf6%2015.a4%20Na5%2016.Qc5%20b6%2017.Qe5%2B%20Kf7%2018.Ba3%20Re8%2019.Qf4%20Kg8%2020.Bb5%20Bxb5%2021.axb5%20exf3%2022.gxf3%20Nd5%2023.Qxf5%20Nxe3%2024.Qd3%20Qh4%2B%2025.Ke2#33) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20f6%203.c4%20e5%204.e3%20e4%205.Nfd2%20c6%206.Nc3%20Bb4%207.cxd5%20cxd5%208.f3%20f5%209.Qa4%2B%20Nc6%2010.a3%20Bxc3%2011.bxc3%20Bd7%2012.Qb3%20Rb8%2013.c4%20dxc4%2014.Qxc4%20Nf6%2015.a4%20Na5%2016.Qc5%20b6%2017.Qe5%2B%20Kf7%2018.fxe4%20Re8%2019.Qf4%20Nxe4%2020.Nxe4%20Rxe4%2021.Qf3%20Qe7%2022.Bd3%20Rxd4%2023.O-O%20Rxd3%2024.Qxf5%2B%20Kg8%2025.Qxd3#33) |

position 13 (`r2qkb1r/ppp3pp/5n2/3p4/8/2P1BB2/PP3P1P/RN1QK2R b KQkq - 2 11`), split at ply 9: a4 (53% there) vs Nxe4 (47%)

| chosen | subpar |
|---|---|
| 11...Bd6 12.Nd2 O-O 13.Qb3 c6 14.O-O-O a5 15.Ne4 [a4] [16.Qc2] Nxe4 17.Bxe4 h6 18.Bh7+ [Kh8] 19.Bg6 | 11...Bd6 12.Nd2 O-O 13.Qb3 c6 14.O-O-O a5 15.Ne4 Nxe4 16.Bxe4 a4 [17.Qc2] h6 18.Rhg1 a3 19.b3 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.d4%20Bxf5%205.Bd3%20Bg4%206.c3%20e5%207.dxe5%20Nxe5%208.Be2%20Nxf3%2B%209.gxf3%20Bxf3%2010.Bxf3%20Nf6%2011.Be3%20Bd6%2012.Nd2%20O-O%2013.Qb3%20c6%2014.O-O-O%20a5%2015.Ne4%20a4%2016.Qc2%20Nxe4%2017.Bxe4%20h6%2018.Bh7%2B%20Kh8%2019.Bg6#21) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.d4%20Bxf5%205.Bd3%20Bg4%206.c3%20e5%207.dxe5%20Nxe5%208.Be2%20Nxf3%2B%209.gxf3%20Bxf3%2010.Bxf3%20Nf6%2011.Be3%20Bd6%2012.Nd2%20O-O%2013.Qb3%20c6%2014.O-O-O%20a5%2015.Ne4%20Nxe4%2016.Bxe4%20a4%2017.Qc2%20h6%2018.Rhg1%20a3%2019.b3#21) |

position 30 (`1rbq1rk1/5ppp/2np3b/p2Np3/1p2P2P/2PQ2P1/PPN2PB1/R4RK1 b - - 1 17`), split at ply 11: Qa7 (54% there) vs Bxd5 (46%)

| chosen | subpar |
|---|---|
| 17...bxc3 18.bxc3 Be6 19.Nce3 Ne7 20.Nxe7+ Qxe7 21.Rfd1 Rfd8 22.Nd5 [Qa7] 23.Rab1 Kf8 24.Rb5 Rxb5 25.Qxb5 | 17...bxc3 18.bxc3 Be6 19.Nce3 Ne7 20.Nxe7+ Qxe7 21.Rfd1 Rfd8 22.Nd5 Bxd5 23.Qxd5 Qc7 24.Bf1 Qxc3 25.Bc4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20e5%206.Ndb5%20d6%207.Bg5%20a6%208.Na3%20b5%209.Nd5%20Be7%2010.Bxf6%20Bxf6%2011.c3%20Bg5%2012.h4%20Bh6%2013.g3%20O-O%2014.Bg2%20Rb8%2015.Nc2%20a5%2016.O-O%20b4%2017.Qd3%20bxc3%2018.bxc3%20Be6%2019.Nce3%20Ne7%2020.Nxe7%2B%20Qxe7%2021.Rfd1%20Rfd8%2022.Nd5%20Qa7%2023.Rab1%20Kf8%2024.Rb5%20Rxb5%2025.Qxb5#33) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20e5%206.Ndb5%20d6%207.Bg5%20a6%208.Na3%20b5%209.Nd5%20Be7%2010.Bxf6%20Bxf6%2011.c3%20Bg5%2012.h4%20Bh6%2013.g3%20O-O%2014.Bg2%20Rb8%2015.Nc2%20a5%2016.O-O%20b4%2017.Qd3%20bxc3%2018.bxc3%20Be6%2019.Nce3%20Ne7%2020.Nxe7%2B%20Qxe7%2021.Rfd1%20Rfd8%2022.Nd5%20Bxd5%2023.Qxd5%20Qc7%2024.Bf1%20Qxc3%2025.Bc4#33) |

#### S #2 (k = 0): latents 19

position 13 (`r2qkb1r/ppp3pp/5n2/3p4/8/2P1BB2/PP3P1P/RN1QK2R b KQkq - 2 11`), split at ply 9: a4 (53% there) vs Nxe4 (47%)

| chosen | subpar |
|---|---|
| 11...Bd6 12.Nd2 O-O 13.Qb3 c6 14.O-O-O a5 15.Ne4 [a4] 16.Qc2 Nxe4 17.Bxe4 h6 18.Bh7+ Kh8 19.Bg6 | 11...Bd6 12.Nd2 O-O 13.Qb3 c6 14.O-O-O a5 15.Ne4 Nxe4 16.Bxe4 a4 17.Qc2 h6 18.Rhg1 a3 19.b3 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.d4%20Bxf5%205.Bd3%20Bg4%206.c3%20e5%207.dxe5%20Nxe5%208.Be2%20Nxf3%2B%209.gxf3%20Bxf3%2010.Bxf3%20Nf6%2011.Be3%20Bd6%2012.Nd2%20O-O%2013.Qb3%20c6%2014.O-O-O%20a5%2015.Ne4%20a4%2016.Qc2%20Nxe4%2017.Bxe4%20h6%2018.Bh7%2B%20Kh8%2019.Bg6#21) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.d4%20Bxf5%205.Bd3%20Bg4%206.c3%20e5%207.dxe5%20Nxe5%208.Be2%20Nxf3%2B%209.gxf3%20Bxf3%2010.Bxf3%20Nf6%2011.Be3%20Bd6%2012.Nd2%20O-O%2013.Qb3%20c6%2014.O-O-O%20a5%2015.Ne4%20Nxe4%2016.Bxe4%20a4%2017.Qc2%20h6%2018.Rhg1%20a3%2019.b3#21) |

position 23 (`rnbqkr2/pppp4/4p2p/b3B1pn/3P4/2NB1N2/PP3PPP/R2QK2R b KQq - 3 14`), split at ply 5: d6 (51% there) vs Nc6 (46%)

| chosen | subpar |
|---|---|
| [14...Nf6] [15.Bg6+] Ke7 [16.O-O] [d6] [17.Bg3] Nc6 [18.Re1] Kd7 [19.d5] exd5 [20.Nxd5] Nxd5 [21.Qxd5] Qf6 [22.Bf5+] | [14...Nf6] [15.Bg6+] Ke7 [16.O-O] Nc6 [17.Bg3] Bxc3 18.bxc3 d6 [19.Re1] Bd7 [20.d5] [Nxd5] [21.Qxd5] Qe8 [22.Bxe8] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Bd6%203.d3%20Nf6%204.Bg5%20Bb4%2B%205.c3%20Bc5%206.d4%20exd4%207.cxd4%20Bb4%2B%208.Nc3%20Ba5%209.e5%20h6%2010.Bh4%20g5%2011.Bg3%20Nh5%2012.e6%20fxe6%2013.Be5%20Rf8%2014.Bd3%20Nf6%2015.Bg6%2B%20Ke7%2016.O-O%20d6%2017.Bg3%20Nc6%2018.Re1%20Kd7%2019.d5%20exd5%2020.Nxd5%20Nxd5%2021.Qxd5%20Qf6%2022.Bf5%2B#27) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Bd6%203.d3%20Nf6%204.Bg5%20Bb4%2B%205.c3%20Bc5%206.d4%20exd4%207.cxd4%20Bb4%2B%208.Nc3%20Ba5%209.e5%20h6%2010.Bh4%20g5%2011.Bg3%20Nh5%2012.e6%20fxe6%2013.Be5%20Rf8%2014.Bd3%20Nf6%2015.Bg6%2B%20Ke7%2016.O-O%20Nc6%2017.Bg3%20Bxc3%2018.bxc3%20d6%2019.Re1%20Bd7%2020.d5%20Nxd5%2021.Qxd5%20Qe8%2022.Bxe8#27) |

position 14 (`2r1k2r/1bqpbpp1/p3p2p/1p4Pn/3nP1BP/2N1BP2/PPPQ4/2KR3R w k - 0 15`), split at ply 14: Qxe4 (55% there) vs Qxg4 (45%)

| chosen | subpar |
|---|---|
| [15.Bxd4] [Nf4] [16.Bxg7] [Rg8] [17.Bxh6] [b4] [18.Qxf4] Qxf4+ [19.Kb1] [Rxc3] [20.bxc3] [Bxe4] 21.fxe4 [Qxe4] 22.Bh3 bxc3 | [15.Bxd4] [Nf4] [16.Bxg7] [Rg8] [17.Bxh6] [b4] [18.Qxf4] Qxf4+ [19.Kb1] [Rxc3] [20.bxc3] [Bxe4] 21.fxe4 Qxg4 22.cxb4 Qxe4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Bxd4%20Nf4%2016.Bxg7%20Rg8%2017.Bxh6%20b4%2018.Qxf4%20Qxf4%2B%2019.Kb1%20Rxc3%2020.bxc3%20Bxe4%2021.fxe4%20Qxe4%2022.Bh3%20bxc3#28) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Bxd4%20Nf4%2016.Bxg7%20Rg8%2017.Bxh6%20b4%2018.Qxf4%20Qxf4%2B%2019.Kb1%20Rxc3%2020.bxc3%20Bxe4%2021.fxe4%20Qxg4%2022.cxb4%20Qxe4#28) |

#### S #3 (k = 0): latents 619

position 20 (`r3k1nr/1p1n4/1p1bp1pp/3p1p2/3P4/2P2N2/PP1N1PPP/R1B2RK1 b kq - 1 14`), split at ply 11: Rhc8 (51% there) vs Bxe3 (49%)

| chosen | subpar |
|---|---|
| 14...g5 15.Re1 [Kf7] [16.Ne5+] Nxe5 17.dxe5 [Bc5] 18.Nb3 [Ne7] 19.Be3 [Rhc8] 20.a3 Bxe3 21.Rxe3 f4 [22.Re2] | 14...g5 15.Re1 [Kf7] [16.Ne5+] Nxe5 17.dxe5 [Bc5] 18.Nb3 [Ne7] 19.Be3 Bxe3 20.Rxe3 Nc6 21.a3 f4 [22.Re2] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20e6%202.Bf4%20c5%203.e3%20cxd4%204.exd4%20Qb6%205.Bc1%20d5%206.Nf3%20Bb4%2B%207.c3%20Bd6%208.Bd3%20g6%209.Nbd2%20f5%2010.Qb3%20h6%2011.Qxb6%20axb6%2012.Bb5%2B%20Bd7%2013.Bxd7%2B%20Nxd7%2014.O-O%20g5%2015.Re1%20Kf7%2016.Ne5%2B%20Nxe5%2017.dxe5%20Bc5%2018.Nb3%20Ne7%2019.Be3%20Rhc8%2020.a3%20Bxe3%2021.Rxe3%20f4%2022.Re2#27) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20e6%202.Bf4%20c5%203.e3%20cxd4%204.exd4%20Qb6%205.Bc1%20d5%206.Nf3%20Bb4%2B%207.c3%20Bd6%208.Bd3%20g6%209.Nbd2%20f5%2010.Qb3%20h6%2011.Qxb6%20axb6%2012.Bb5%2B%20Bd7%2013.Bxd7%2B%20Nxd7%2014.O-O%20g5%2015.Re1%20Kf7%2016.Ne5%2B%20Nxe5%2017.dxe5%20Bc5%2018.Nb3%20Ne7%2019.Be3%20Bxe3%2020.Rxe3%20Nc6%2021.a3%20f4%2022.Re2#27) |

position 26 (`r1b1r1k1/2p3bp/2p2pq1/2Np4/p5P1/P1Q1B3/1PP2P1P/1K1R2R1 w - - 3 24`), split at ply 7: Qf4 (48% there) vs Qxg7+ (45%)

| chosen | subpar |
|---|---|
| 24.g5 f5 25.Bd4 Bxd4 [26.Qxd4] Qg7 [27.Qf4] Qe5 [28.Qh4] Rb8 29.Nd3 Qc3 30.Kc1 Ba6 31.g6 Bxd3 | 24.g5 f5 25.Bd4 Bxd4 [26.Qxd4] Qg7 27.Qxg7+ Kxg7 28.Rde1 Rxe1+ 29.Rxe1 Kf7 30.f4 Ra5 31.Nd3 c5 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.g5%20f5%2025.Bd4%20Bxd4%2026.Qxd4%20Qg7%2027.Qf4%20Qe5%2028.Qh4%20Rb8%2029.Nd3%20Qc3%2030.Kc1%20Ba6%2031.g6%20Bxd3#46) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.g5%20f5%2025.Bd4%20Bxd4%2026.Qxd4%20Qg7%2027.Qxg7%2B%20Kxg7%2028.Rde1%20Rxe1%2B%2029.Rxe1%20Kf7%2030.f4%20Ra5%2031.Nd3%20c5#46) |

position 6 (`r1b2rk1/1pp1q1pp/2p1np2/p3p3/P1N1P3/1P1P1N1P/2P2PP1/R2Q1RK1 b - - 2 14`), split at ply 10: Nb6 (55% there) vs fxe5 (45%)

| chosen | subpar |
|---|---|
| 14...c5 15.Ne3 Nd4 16.Nxd4 cxd4 17.Nd5 [Qd6] 18.f4 [c6] [19.Nb6] [Ra6] [20.Nxc8] [Rxc8] 21.fxe5 [Qxe5] 22.Qg4 | 14...c5 15.Ne3 Nd4 16.Nxd4 cxd4 17.Nd5 [Qd6] 18.f4 [c6] 19.fxe5 [Qxe5] [20.Nb6] [Rb8] 21.Nc4 [Qc5] 22.Qd2 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20a6%204.Ba4%20Nf6%205.Bxc6%20dxc6%206.d3%20Nd7%207.O-O%20Bc5%208.Be3%20Qe7%209.Bxc5%20Nxc5%2010.Nbd2%20O-O%2011.a4%20a5%2012.b3%20f6%2013.h3%20Ne6%2014.Nc4%20c5%2015.Ne3%20Nd4%2016.Nxd4%20cxd4%2017.Nd5%20Qd6%2018.f4%20c6%2019.Nb6%20Ra6%2020.Nxc8%20Rxc8%2021.fxe5%20Qxe5%2022.Qg4#27) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20a6%204.Ba4%20Nf6%205.Bxc6%20dxc6%206.d3%20Nd7%207.O-O%20Bc5%208.Be3%20Qe7%209.Bxc5%20Nxc5%2010.Nbd2%20O-O%2011.a4%20a5%2012.b3%20f6%2013.h3%20Ne6%2014.Nc4%20c5%2015.Ne3%20Nd4%2016.Nxd4%20cxd4%2017.Nd5%20Qd6%2018.f4%20c6%2019.fxe5%20Qxe5%2020.Nb6%20Rb8%2021.Nc4%20Qc5%2022.Qd2#27) |

#### S #4 (k = 0): latents 570

position 40 (`r3k3/pp1nbpp1/2p1p3/3nP1Bq/3NBP2/3P2Q1/PPP3K1/R7 b q - 0 24`), split at ply 8: Qxg4 (52% there) vs Rxa8 (48%)

| chosen | subpar |
|---|---|
| [24...Bxg5] [25.fxg5] [Nxe5] [26.Rh1] Qg4 [27.Rh8+] Ke7 [28.Qxg4] Nxg4 29.Rxa8 Nge3+ [30.Kf3] a6 [31.c4] Nb4 32.Kxe3 | [24...Bxg5] [25.fxg5] [Nxe5] [26.Rh1] Qg4 [27.Rh8+] Ke7 28.Rxa8 Qxg3+ 29.Kxg3 Ne3 30.Rxa7 Nd1 31.Rxb7+ Kd6 [32.Nf3] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.Nf3%20d5%203.d3%20Bg4%204.h3%20Bh5%205.Nc3%20e6%206.g4%20Bg6%207.h4%20h5%208.Ne5%20Ne7%209.Nxg6%20Nxg6%2010.gxh5%20Nxh4%2011.Qg4%20Ng6%2012.Bg2%20Ne5%2013.Qg3%20Ned7%2014.Bf4%20d4%2015.Ne2%20Qa5%2B%2016.Kf1%20Rxh5%2017.Rxh5%20Qxh5%2018.e5%20Nb6%2019.Nxd4%20Nd5%2020.Bg5%20Nd7%2021.Bf3%20Qg6%2022.Be4%20Qh5%2023.Kg2%20Be7%2024.f4%20Bxg5%2025.fxg5%20Nxe5%2026.Rh1%20Qg4%2027.Rh8%2B%20Ke7%2028.Qxg4%20Nxg4%2029.Rxa8%20Nge3%2B%2030.Kf3%20a6%2031.c4%20Nb4%2032.Kxe3#47) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.Nf3%20d5%203.d3%20Bg4%204.h3%20Bh5%205.Nc3%20e6%206.g4%20Bg6%207.h4%20h5%208.Ne5%20Ne7%209.Nxg6%20Nxg6%2010.gxh5%20Nxh4%2011.Qg4%20Ng6%2012.Bg2%20Ne5%2013.Qg3%20Ned7%2014.Bf4%20d4%2015.Ne2%20Qa5%2B%2016.Kf1%20Rxh5%2017.Rxh5%20Qxh5%2018.e5%20Nb6%2019.Nxd4%20Nd5%2020.Bg5%20Nd7%2021.Bf3%20Qg6%2022.Be4%20Qh5%2023.Kg2%20Be7%2024.f4%20Bxg5%2025.fxg5%20Nxe5%2026.Rh1%20Qg4%2027.Rh8%2B%20Ke7%2028.Rxa8%20Qxg3%2B%2029.Kxg3%20Ne3%2030.Rxa7%20Nd1%2031.Rxb7%2B%20Kd6%2032.Nf3#47) |

position 30 (`1rbq1rk1/5ppp/2np3b/p2Np3/1p2P2P/2PQ2P1/PPN2PB1/R4RK1 b - - 1 17`), split at ply 3: Bxe3 (52% there) vs bxc3 (48%)

| chosen | subpar |
|---|---|
| 17...Be6 18.Nce3 [Bxe3] 19.Nxe3 [bxc3] 20.bxc3 Qc7 21.Rfd1 Rfd8 [22.Nd5] [Bxd5] 23.Qxd5 [Ne7] [24.Qd3] [Rbc8] [25.Rac1] | 17...Be6 18.Nce3 bxc3 19.bxc3 Rb2 20.Nc4 Rb8 [21.Rfd1] Qd7 22.Nxd6 Rfd8 [23.Nf5] Bxf5 24.exf5 Kh8 25.f6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20e5%206.Ndb5%20d6%207.Bg5%20a6%208.Na3%20b5%209.Nd5%20Be7%2010.Bxf6%20Bxf6%2011.c3%20Bg5%2012.h4%20Bh6%2013.g3%20O-O%2014.Bg2%20Rb8%2015.Nc2%20a5%2016.O-O%20b4%2017.Qd3%20Be6%2018.Nce3%20Bxe3%2019.Nxe3%20bxc3%2020.bxc3%20Qc7%2021.Rfd1%20Rfd8%2022.Nd5%20Bxd5%2023.Qxd5%20Ne7%2024.Qd3%20Rbc8%2025.Rac1#33) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20e5%206.Ndb5%20d6%207.Bg5%20a6%208.Na3%20b5%209.Nd5%20Be7%2010.Bxf6%20Bxf6%2011.c3%20Bg5%2012.h4%20Bh6%2013.g3%20O-O%2014.Bg2%20Rb8%2015.Nc2%20a5%2016.O-O%20b4%2017.Qd3%20Be6%2018.Nce3%20bxc3%2019.bxc3%20Rb2%2020.Nc4%20Rb8%2021.Rfd1%20Qd7%2022.Nxd6%20Rfd8%2023.Nf5%20Bxf5%2024.exf5%20Kh8%2025.f6#33) |

position 13 (`r2qkb1r/ppp3pp/5n2/3p4/8/2P1BB2/PP3P1P/RN1QK2R b KQkq - 2 11`), split at ply 9: a4 (53% there) vs Nxe4 (47%)

| chosen | subpar |
|---|---|
| 11...Bd6 12.Nd2 O-O 13.Qb3 c6 14.O-O-O a5 15.Ne4 [a4] 16.Qc2 [Nxe4] 17.Bxe4 h6 18.Bh7+ Kh8 19.Bg6 | 11...Bd6 12.Nd2 O-O 13.Qb3 c6 14.O-O-O a5 15.Ne4 Nxe4 16.Bxe4 [a4] 17.Qc2 h6 18.Rhg1 [a3] 19.b3 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.d4%20Bxf5%205.Bd3%20Bg4%206.c3%20e5%207.dxe5%20Nxe5%208.Be2%20Nxf3%2B%209.gxf3%20Bxf3%2010.Bxf3%20Nf6%2011.Be3%20Bd6%2012.Nd2%20O-O%2013.Qb3%20c6%2014.O-O-O%20a5%2015.Ne4%20a4%2016.Qc2%20Nxe4%2017.Bxe4%20h6%2018.Bh7%2B%20Kh8%2019.Bg6#21) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.d4%20Bxf5%205.Bd3%20Bg4%206.c3%20e5%207.dxe5%20Nxe5%208.Be2%20Nxf3%2B%209.gxf3%20Bxf3%2010.Bxf3%20Nf6%2011.Be3%20Bd6%2012.Nd2%20O-O%2013.Qb3%20c6%2014.O-O-O%20a5%2015.Ne4%20Nxe4%2016.Bxe4%20a4%2017.Qc2%20h6%2018.Rhg1%20a3%2019.b3#21) |

#### S #5 (k = 0): latents 1831

position 5 (`r3kbnr/pbpn2pp/1p2q3/1Q2p1B1/4P3/2N2N2/PPP3PP/2KR1B1R b kq - 2 11`), split at ply 7: Rc8 (51% there) vs Bxd5 (49%)

| chosen | subpar |
|---|---|
| 11...a6 12.Qa4 b5 13.Qa5 Bd6 14.Nd5 [Rc8] 15.a4 c6 16.Nb6 Nxb6 17.Qxb6 Qd7 18.Nxe5 Bxe5 19.Rxd7 | 11...a6 12.Qa4 b5 13.Qa5 Bd6 14.Nd5 Bxd5 15.exd5 Qf5 16.Bd3 Qg4 17.h3 Qxg2 [18.Rhg1] Qxf3 [19.Rdf1] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Nf3%20d6%204.Qe2%20Qe7%205.d3%20b6%206.Nc3%20Bb7%207.fxe5%20dxe5%208.Bg5%20Qe6%209.O-O-O%20fxe4%2010.dxe4%20Nd7%2011.Qb5%20a6%2012.Qa4%20b5%2013.Qa5%20Bd6%2014.Nd5%20Rc8%2015.a4%20c6%2016.Nb6%20Nxb6%2017.Qxb6%20Qd7%2018.Nxe5%20Bxe5%2019.Rxd7#21) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Nf3%20d6%204.Qe2%20Qe7%205.d3%20b6%206.Nc3%20Bb7%207.fxe5%20dxe5%208.Bg5%20Qe6%209.O-O-O%20fxe4%2010.dxe4%20Nd7%2011.Qb5%20a6%2012.Qa4%20b5%2013.Qa5%20Bd6%2014.Nd5%20Bxd5%2015.exd5%20Qf5%2016.Bd3%20Qg4%2017.h3%20Qxg2%2018.Rhg1%20Qxf3%2019.Rdf1#21) |

position 45 (`r4rk1/pp4pp/1b3q2/1P1pRp2/P7/1QP3P1/5P1P/R5K1 b - - 2 26`), split at ply 2: Rae1 (50% there) vs Rxd5 (49%)

| chosen | subpar |
|---|---|
| [26...Rad8] [27.Rae1] Kh8 28.Kg2 f4 29.f3 fxg3 30.hxg3 Qxf3+ 31.Kh3 Qh5+ 32.Kg2 Rf2+ 33.Kg1 Qh2# | [26...Rad8] 27.Rxd5 Kh8 [28.Rad1] Rxd5 29.Rxd5 f4 30.Qc2 fxg3 31.hxg3 Qf3 [32.Rd2] Qxg3+ 33.Kf1 Qh3+ 34.Kg1 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.e5%20c5%204.dxc5%20Nc6%205.Bf4%20e6%206.Bb5%20Bd7%207.Na3%20Bxc5%208.Nf3%20Nge7%209.O-O%20Ng6%2010.Bg5%20f6%2011.Bh4%20Nxh4%2012.Nxh4%20Nxe5%2013.Bxd7%2B%20Qxd7%2014.c3%20O-O%2015.b4%20Bb6%2016.b5%20Qe7%2017.Nc2%20Ng4%2018.Nd4%20Ne5%2019.a4%20Nc4%2020.Re1%20f5%2021.Rxe6%20Qxh4%2022.g3%20Qg5%2023.Nf3%20Qd8%2024.Ne5%20Nxe5%2025.Rxe5%20Qf6%2026.Qb3%20Rad8%2027.Rae1%20Kh8%2028.Kg2%20f4%2029.f3%20fxg3%2030.hxg3%20Qxf3%2B%2031.Kh3%20Qh5%2B%2032.Kg2%20Rf2%2B%2033.Kg1%20Qh2%23#51) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.e5%20c5%204.dxc5%20Nc6%205.Bf4%20e6%206.Bb5%20Bd7%207.Na3%20Bxc5%208.Nf3%20Nge7%209.O-O%20Ng6%2010.Bg5%20f6%2011.Bh4%20Nxh4%2012.Nxh4%20Nxe5%2013.Bxd7%2B%20Qxd7%2014.c3%20O-O%2015.b4%20Bb6%2016.b5%20Qe7%2017.Nc2%20Ng4%2018.Nd4%20Ne5%2019.a4%20Nc4%2020.Re1%20f5%2021.Rxe6%20Qxh4%2022.g3%20Qg5%2023.Nf3%20Qd8%2024.Ne5%20Nxe5%2025.Rxe5%20Qf6%2026.Qb3%20Rad8%2027.Rxd5%20Kh8%2028.Rad1%20Rxd5%2029.Rxd5%20f4%2030.Qc2%20fxg3%2031.hxg3%20Qf3%2032.Rd2%20Qxg3%2B%2033.Kf1%20Qh3%2B%2034.Kg1#51) |

position 20 (`r3k1nr/1p1n4/1p1bp1pp/3p1p2/3P4/2P2N2/PP1N1PPP/R1B2RK1 b kq - 1 14`), split at ply 11: Rhc8 (51% there) vs Bxe3 (49%)

| chosen | subpar |
|---|---|
| 14...g5 [15.Re1] Kf7 16.Ne5+ Nxe5 17.dxe5 Bc5 18.Nb3 Ne7 19.Be3 [Rhc8] 20.a3 Bxe3 21.Rxe3 f4 [22.Re2] | 14...g5 [15.Re1] Kf7 16.Ne5+ Nxe5 17.dxe5 Bc5 18.Nb3 Ne7 19.Be3 Bxe3 20.Rxe3 Nc6 21.a3 f4 [22.Re2] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20e6%202.Bf4%20c5%203.e3%20cxd4%204.exd4%20Qb6%205.Bc1%20d5%206.Nf3%20Bb4%2B%207.c3%20Bd6%208.Bd3%20g6%209.Nbd2%20f5%2010.Qb3%20h6%2011.Qxb6%20axb6%2012.Bb5%2B%20Bd7%2013.Bxd7%2B%20Nxd7%2014.O-O%20g5%2015.Re1%20Kf7%2016.Ne5%2B%20Nxe5%2017.dxe5%20Bc5%2018.Nb3%20Ne7%2019.Be3%20Rhc8%2020.a3%20Bxe3%2021.Rxe3%20f4%2022.Re2#27) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20e6%202.Bf4%20c5%203.e3%20cxd4%204.exd4%20Qb6%205.Bc1%20d5%206.Nf3%20Bb4%2B%207.c3%20Bd6%208.Bd3%20g6%209.Nbd2%20f5%2010.Qb3%20h6%2011.Qxb6%20axb6%2012.Bb5%2B%20Bd7%2013.Bxd7%2B%20Nxd7%2014.O-O%20g5%2015.Re1%20Kf7%2016.Ne5%2B%20Nxe5%2017.dxe5%20Bc5%2018.Nb3%20Ne7%2019.Be3%20Bxe3%2020.Rxe3%20Nc6%2021.a3%20f4%2022.Re2#27) |

#### S #6 (k = 0): latents 19

position 33 (`r2qk1r1/3bbpnp/p3N1p1/2ppB1P1/1p2P2P/1P3Q2/P1P2P2/2KR1B1R b q - 0 19`), split at ply 6: Bc4 (50% there) vs dxe7 (46%)

| chosen | subpar |
|---|---|
| [19...Bxe6] [20.exd5] [Bd7] [21.d6] [Rc8] [22.Bc4] [Nf5] 23.dxe7 [Qxe7] 24.Rhe1 [Be6] [25.Bf6] [Qc7] 26.Bxe6 [fxe6] 27.Rxe6+ | [19...Bxe6] [20.exd5] [Bd7] [21.d6] [Rc8] 22.dxe7 [Qxe7] 23.Bxa6 [Bc6] [24.Bxc8] [Bxf3] [25.Rhe1] [Ne6] [26.Rd7] [Qxd7] 27.Bxd7+ |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.Bf4%20a6%204.e3%20e6%205.g4%20Bb4%206.Ne2%20Be7%207.g5%20Nh5%208.h4%20b5%209.Bh2%20Nc6%2010.Nc1%20g6%2011.Nb3%20Ng7%2012.Qf3%20b4%2013.Na4%20Bd7%2014.O-O-O%20Nxd4%2015.Nxd4%20Bxa4%2016.Be5%20Rg8%2017.e4%20c5%2018.b3%20Bd7%2019.Nxe6%20Bxe6%2020.exd5%20Bd7%2021.d6%20Rc8%2022.Bc4%20Nf5%2023.dxe7%20Qxe7%2024.Rhe1%20Be6%2025.Bf6%20Qc7%2026.Bxe6%20fxe6%2027.Rxe6%2B#37) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.Bf4%20a6%204.e3%20e6%205.g4%20Bb4%206.Ne2%20Be7%207.g5%20Nh5%208.h4%20b5%209.Bh2%20Nc6%2010.Nc1%20g6%2011.Nb3%20Ng7%2012.Qf3%20b4%2013.Na4%20Bd7%2014.O-O-O%20Nxd4%2015.Nxd4%20Bxa4%2016.Be5%20Rg8%2017.e4%20c5%2018.b3%20Bd7%2019.Nxe6%20Bxe6%2020.exd5%20Bd7%2021.d6%20Rc8%2022.dxe7%20Qxe7%2023.Bxa6%20Bc6%2024.Bxc8%20Bxf3%2025.Rhe1%20Ne6%2026.Rd7%20Qxd7%2027.Bxd7%2B#37) |

position 38 (`2r2rk1/2q2Ppp/p2b4/1ppQ4/8/2NP4/PP2K1PP/R1B4n b - - 0 22`), split at ply 6: Rf1 (52% there) vs Rxh1 (44%)

| chosen | subpar |
|---|---|
| 22...Rxf7 23.Be3 Re8 [24.Ne4] Bf4 [25.Rf1] [Bxe3] [26.Rxf7] [Qxf7] [27.Qxf7+] Kxf7 28.Kxe3 c4 29.dxc4 Rxe4+ 30.Kxe4 | 22...Rxf7 23.Be3 Re8 [24.Ne4] Bf4 25.Rxh1 Bxe3 26.Kxe3 Qf4+ 27.Ke2 Qg4+ 28.Kd2 Qxg2+ 29.Kc3 Qxh1 [30.Nd6] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Qh5%20e6%203.Nf3%20Nc6%204.Bb5%20Nb4%205.Ba4%20a6%206.c3%20Nd3%2B%207.Kd1%20Nxf2%2B%208.Ke2%20Nxh1%209.Ne5%20Qe7%2010.d3%20Nf6%2011.Qf3%20b5%2012.Bb3%20d6%2013.Nc6%20Qc7%2014.e5%20Nd5%2015.c4%20Qxc6%2016.cxd5%20Qc7%2017.dxe6%20Bb7%2018.Bd5%20Bxd5%2019.Qxd5%20Rc8%2020.exd6%20Bxd6%2021.Nc3%20O-O%2022.exf7%2B%20Rxf7%2023.Be3%20Re8%2024.Ne4%20Bf4%2025.Rf1%20Bxe3%2026.Rxf7%20Qxf7%2027.Qxf7%2B%20Kxf7%2028.Kxe3%20c4%2029.dxc4%20Rxe4%2B%2030.Kxe4#43) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Qh5%20e6%203.Nf3%20Nc6%204.Bb5%20Nb4%205.Ba4%20a6%206.c3%20Nd3%2B%207.Kd1%20Nxf2%2B%208.Ke2%20Nxh1%209.Ne5%20Qe7%2010.d3%20Nf6%2011.Qf3%20b5%2012.Bb3%20d6%2013.Nc6%20Qc7%2014.e5%20Nd5%2015.c4%20Qxc6%2016.cxd5%20Qc7%2017.dxe6%20Bb7%2018.Bd5%20Bxd5%2019.Qxd5%20Rc8%2020.exd6%20Bxd6%2021.Nc3%20O-O%2022.exf7%2B%20Rxf7%2023.Be3%20Re8%2024.Ne4%20Bf4%2025.Rxh1%20Bxe3%2026.Kxe3%20Qf4%2B%2027.Ke2%20Qg4%2B%2028.Kd2%20Qxg2%2B%2029.Kc3%20Qxh1%2030.Nd6#43) |

position 3 (`2kr1b1r/ppp1pppp/5n2/8/3n1q2/1P1P1B1P/P1P2PP1/RNBQ1K1R b - - 0 11`), split at ply 8: Qxg4 (57% there) vs hxg4 (43%)

| chosen | subpar |
|---|---|
| 11...Qf5 12.Nd2 e5 13.Nc4 [e4] [14.Bg4] [Nxg4] [15.Qxg4] Qxg4 16.hxg4 exd3 17.cxd3 Nc2 18.Rb1 Rxd3 19.Ke2 | 11...Qf5 12.Nd2 e5 13.Nc4 [e4] [14.Bg4] [Nxg4] 15.hxg4 exd3 16.cxd3 Bc5 17.Be3 Rhe8 18.Rc1 Kb8 [19.Rh5] |
| [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nc6%202.e4%20d5%203.exd5%20Qxd5%204.b3%20Bg4%205.Bc4%20Qe4%2B%206.Kf1%20Nd4%207.Bd3%20Qf4%208.Be2%20O-O-O%209.h3%20Bxf3%2010.Bxf3%20Nf6%2011.d3%20Qf5%2012.Nd2%20e5%2013.Nc4%20e4%2014.Bg4%20Nxg4%2015.Qxg4%20Qxg4%2016.hxg4%20exd3%2017.cxd3%20Nc2%2018.Rb1%20Rxd3%2019.Ke2#21) | [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nc6%202.e4%20d5%203.exd5%20Qxd5%204.b3%20Bg4%205.Bc4%20Qe4%2B%206.Kf1%20Nd4%207.Bd3%20Qf4%208.Be2%20O-O-O%209.h3%20Bxf3%2010.Bxf3%20Nf6%2011.d3%20Qf5%2012.Nd2%20e5%2013.Nc4%20e4%2014.Bg4%20Nxg4%2015.hxg4%20exd3%2016.cxd3%20Bc5%2017.Be3%20Rhe8%2018.Rc1%20Kb8%2019.Rh5#21) |

#### S #7 (k = 0): latents 570

position 11 (`r3k2r/p3bp2/qn2p3/1R2Pp1p/3P3P/3Q1N2/3B1PP1/1R4K1 w kq - 3 21`), split at ply 7: Rc5 (52% there) vs Qa3 (48%)

| chosen | subpar |
|---|---|
| [21.Bg5] [Bxg5] [22.Nxg5] Rd8 23.Qf3 Qc8 [24.Rc5] Qd7 25.Rbc1 [Nd5] [26.Rc6] [Kf8] [27.Qa3+] [Kg7] 28.Qg3 [Kh6] | [21.Bg5] [Bxg5] [22.Nxg5] Rd8 23.Qf3 Qc8 24.Qa3 [Nd5] [25.Rb7] [Rd7] [26.Rb8] [Nb6] [27.Rxc8+] [Nxc8] [28.Rb8] Rd8 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.e5%20Bf5%204.h4%20h5%205.Bd3%20Bxd3%206.Qxd3%20Qa5%2B%207.b4%20Qxb4%2B%208.Nd2%20Qb5%209.c4%20dxc4%2010.Nxc4%20e6%2011.Bd2%20Qa6%2012.Nf3%20Nh6%2013.O-O%20Nf5%2014.Rab1%20b5%2015.Ne3%20g6%2016.a4%20Be7%2017.Nxf5%20gxf5%2018.axb5%20cxb5%2019.Rxb5%20Nd7%2020.Rfb1%20Nb6%2021.Bg5%20Bxg5%2022.Nxg5%20Rd8%2023.Qf3%20Qc8%2024.Rc5%20Qd7%2025.Rbc1%20Nd5%2026.Rc6%20Kf8%2027.Qa3%2B%20Kg7%2028.Qg3%20Kh6#40) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.e5%20Bf5%204.h4%20h5%205.Bd3%20Bxd3%206.Qxd3%20Qa5%2B%207.b4%20Qxb4%2B%208.Nd2%20Qb5%209.c4%20dxc4%2010.Nxc4%20e6%2011.Bd2%20Qa6%2012.Nf3%20Nh6%2013.O-O%20Nf5%2014.Rab1%20b5%2015.Ne3%20g6%2016.a4%20Be7%2017.Nxf5%20gxf5%2018.axb5%20cxb5%2019.Rxb5%20Nd7%2020.Rfb1%20Nb6%2021.Bg5%20Bxg5%2022.Nxg5%20Rd8%2023.Qf3%20Qc8%2024.Qa3%20Nd5%2025.Rb7%20Rd7%2026.Rb8%20Nb6%2027.Rxc8%2B%20Nxc8%2028.Rb8%20Rd8#40) |

position 34 (`r2qk2r/1pp1bppp/2n1p3/1p6/3PR3/P1P2N2/5PPP/R2Q2K1 b kq - 0 14`), split at ply 5: Bd6 (55% there) vs Bf6 (45%)

| chosen | subpar |
|---|---|
| 14...O-O 15.Rg4 [f5] [16.Rg3] [Bd6] [17.Rh3] Qf6 18.Qb3 b4 19.cxb4 Nxd4 20.Nxd4 Qxd4 21.Qxe6+ Kh8 22.Rf1 | 14...O-O 15.Rg4 [f5] [16.Rg3] Bf6 17.Qe2 Qd5 18.Re1 Rfe8 19.h4 e5 20.dxe5 Nxe5 [21.Nd4] [Nf3+] 22.Qxf3 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20O-O%2015.Rg4%20f5%2016.Rg3%20Bd6%2017.Rh3%20Qf6%2018.Qb3%20b4%2019.cxb4%20Nxd4%2020.Nxd4%20Qxd4%2021.Qxe6%2B%20Kh8%2022.Rf1#27) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20O-O%2015.Rg4%20f5%2016.Rg3%20Bf6%2017.Qe2%20Qd5%2018.Re1%20Rfe8%2019.h4%20e5%2020.dxe5%20Nxe5%2021.Nd4%20Nf3%2B%2022.Qxf3#27) |

position 19 (`r4r1k/ppq1b1pp/2npQ3/4p3/1PP5/P1P2N2/5PPP/R1B2RK1 w - - 1 18`), split at ply 14: Nf5 (56% there) vs Qxc4 (44%)

| chosen | subpar |
|---|---|
| 18.Bg5 Bxg5 19.Nxg5 Rf6 20.Qh3 h6 21.Ne4 [Rf4] 22.f3 Raf8 23.Rad1 Ne7 24.Rxd6 [Nf5] 25.Rd3 Qxc4 | 18.Bg5 Bxg5 19.Nxg5 Rf6 20.Qh3 h6 21.Ne4 [Rf4] 22.f3 Raf8 23.Rad1 Ne7 24.Rxd6 Qxc4 25.Rd7 Nf5 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bc4%20Nf6%204.d3%20Be7%205.O-O%20O-O%206.Nc3%20d6%207.a3%20Be6%208.Qe2%20Bxc4%209.dxc4%20Nd7%2010.Nd5%20Nc5%2011.b4%20Ne6%2012.c3%20f5%2013.exf5%20Rxf5%2014.Qe4%20Rf8%2015.Qg4%20Qd7%2016.Nxc7%20Qxc7%2017.Qxe6%2B%20Kh8%2018.Bg5%20Bxg5%2019.Nxg5%20Rf6%2020.Qh3%20h6%2021.Ne4%20Rf4%2022.f3%20Raf8%2023.Rad1%20Ne7%2024.Rxd6%20Nf5%2025.Rd3%20Qxc4#34) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bc4%20Nf6%204.d3%20Be7%205.O-O%20O-O%206.Nc3%20d6%207.a3%20Be6%208.Qe2%20Bxc4%209.dxc4%20Nd7%2010.Nd5%20Nc5%2011.b4%20Ne6%2012.c3%20f5%2013.exf5%20Rxf5%2014.Qe4%20Rf8%2015.Qg4%20Qd7%2016.Nxc7%20Qxc7%2017.Qxe6%2B%20Kh8%2018.Bg5%20Bxg5%2019.Nxg5%20Rf6%2020.Qh3%20h6%2021.Ne4%20Rf4%2022.f3%20Raf8%2023.Rad1%20Ne7%2024.Rxd6%20Qxc4%2025.Rd7%20Nf5#34) |

#### S #8 (k = 0): latents 323

position 27 (`r3kb1r/1p2pp1p/p2p1np1/4n1Q1/3B4/PP2P3/2qPNPPP/R4RK1 b kq - 1 15`), split at ply 3: Bg7 (53% there) vs Qxd2 (47%)

| chosen | subpar |
|---|---|
| [15...h6] [16.Qg3] [Bg7] 17.Rfc1 [Qf5] [18.Rc7] Ne4 [19.Qh4] Bf6 20.Qf4 [Qxf4] 21.Nxf4 [Nc6] 22.Bxf6 Nxf6 23.Rxb7 | [15...h6] [16.Qg3] Qxd2 17.Nf4 [Bg7] 18.Bxe5 dxe5 19.Rfd1 exf4 [20.Qf3] [Qc3] [21.Rac1] [Qe5] [22.Qxb7] O-O 23.exf4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e3%20c5%202.Qh5%20Nf6%203.Qxc5%20g6%204.Bc4%20d6%205.Qg5%20Nc6%206.a3%20Ne5%207.Bb5%2B%20Bd7%208.Ba4%20Bxa4%209.b3%20Bd7%2010.Bb2%20Qc7%2011.Nc3%20a6%2012.Nge2%20Bb5%2013.O-O%20Bxe2%2014.Nxe2%20Qxc2%2015.Bd4%20h6%2016.Qg3%20Bg7%2017.Rfc1%20Qf5%2018.Rc7%20Ne4%2019.Qh4%20Bf6%2020.Qf4%20Qxf4%2021.Nxf4%20Nc6%2022.Bxf6%20Nxf6%2023.Rxb7#29) | [Lichess](https://lichess.org/analysis/pgn/1.e3%20c5%202.Qh5%20Nf6%203.Qxc5%20g6%204.Bc4%20d6%205.Qg5%20Nc6%206.a3%20Ne5%207.Bb5%2B%20Bd7%208.Ba4%20Bxa4%209.b3%20Bd7%2010.Bb2%20Qc7%2011.Nc3%20a6%2012.Nge2%20Bb5%2013.O-O%20Bxe2%2014.Nxe2%20Qxc2%2015.Bd4%20h6%2016.Qg3%20Qxd2%2017.Nf4%20Bg7%2018.Bxe5%20dxe5%2019.Rfd1%20exf4%2020.Qf3%20Qc3%2021.Rac1%20Qe5%2022.Qxb7%20O-O%2023.exf4#29) |

position 43 (`1r1qk2r/p2b2pp/1p3n2/n3Qp2/P2Pp3/4PP2/3N2PP/R1B1KB1R b KQk - 1 17`), split at ply 9: Bxa4 (51% there) vs Qb4+ (46%)

| chosen | subpar |
|---|---|
| [17...Qe7] 18.Qxb8+ [Kf7] 19.Qxh8 exf3 20.Nxf3 Nb3 21.Rb1 [Bxa4] 22.Bc4+ [Kg6] 23.Bxb3 Bxb3 24.Rxb3 Qe4 25.O-O | [17...Qe7] 18.Qxb8+ [Kf7] 19.Qxh8 exf3 20.Nxf3 Nb3 21.Rb1 Qb4+ 22.Bd2 Nxd2 23.Rxb4 Nxf3+ 24.gxf3 Nd5 25.Bc4 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20f6%203.c4%20e5%204.e3%20e4%205.Nfd2%20c6%206.Nc3%20Bb4%207.cxd5%20cxd5%208.f3%20f5%209.Qa4%2B%20Nc6%2010.a3%20Bxc3%2011.bxc3%20Bd7%2012.Qb3%20Rb8%2013.c4%20dxc4%2014.Qxc4%20Nf6%2015.a4%20Na5%2016.Qc5%20b6%2017.Qe5%2B%20Qe7%2018.Qxb8%2B%20Kf7%2019.Qxh8%20exf3%2020.Nxf3%20Nb3%2021.Rb1%20Bxa4%2022.Bc4%2B%20Kg6%2023.Bxb3%20Bxb3%2024.Rxb3%20Qe4%2025.O-O#33) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20f6%203.c4%20e5%204.e3%20e4%205.Nfd2%20c6%206.Nc3%20Bb4%207.cxd5%20cxd5%208.f3%20f5%209.Qa4%2B%20Nc6%2010.a3%20Bxc3%2011.bxc3%20Bd7%2012.Qb3%20Rb8%2013.c4%20dxc4%2014.Qxc4%20Nf6%2015.a4%20Na5%2016.Qc5%20b6%2017.Qe5%2B%20Qe7%2018.Qxb8%2B%20Kf7%2019.Qxh8%20exf3%2020.Nxf3%20Nb3%2021.Rb1%20Qb4%2B%2022.Bd2%20Nxd2%2023.Rxb4%20Nxf3%2B%2024.gxf3%20Nd5%2025.Bc4#33) |

position 41 (`r1q1kn1r/p3b3/2p3p1/1p2Pp1p/3P1B1P/1QPB2N1/PP6/2KR3R b kq - 1 18`), split at ply 7: cxd5 (55% there) vs Nxd3+ (45%)

| chosen | subpar |
|---|---|
| 18...Ne6 19.Ne2 a5 20.d5 [Nc5] 21.Qc2 [cxd5] 22.Bxb5+ [Kf7] 23.Rxd5 Rb8 24.Bc4 Kg7 [25.Rhd1] a4 26.Nd4 | 18...Ne6 19.Ne2 a5 20.d5 [Nc5] 21.Qc2 Nxd3+ 22.Qxd3 cxd5 23.Qxd5 b4 24.Qb5+ Kf7 25.Rd7 bxc3 26.Nxc3 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.Nc3%20dxe4%204.Nxe4%20Bf5%205.f3%20Nf6%206.Bd3%20e6%207.Ne2%20Nbd7%208.Bf4%20Be7%209.g4%20Bxe4%2010.fxe4%20Nxg4%2011.Ng3%20f6%2012.Qxg4%20g6%2013.Qxe6%20Nf8%2014.Qb3%20b5%2015.c3%20Qc8%2016.e5%20f5%2017.h4%20h5%2018.O-O-O%20Ne6%2019.Ne2%20a5%2020.d5%20Nc5%2021.Qc2%20cxd5%2022.Bxb5%2B%20Kf7%2023.Rxd5%20Rb8%2024.Bc4%20Kg7%2025.Rhd1%20a4%2026.Nd4#35) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.Nc3%20dxe4%204.Nxe4%20Bf5%205.f3%20Nf6%206.Bd3%20e6%207.Ne2%20Nbd7%208.Bf4%20Be7%209.g4%20Bxe4%2010.fxe4%20Nxg4%2011.Ng3%20f6%2012.Qxg4%20g6%2013.Qxe6%20Nf8%2014.Qb3%20b5%2015.c3%20Qc8%2016.e5%20f5%2017.h4%20h5%2018.O-O-O%20Ne6%2019.Ne2%20a5%2020.d5%20Nc5%2021.Qc2%20Nxd3%2B%2022.Qxd3%20cxd5%2023.Qxd5%20b4%2024.Qb5%2B%20Kf7%2025.Rd7%20bxc3%2026.Nxc3#35) |

#### S #9 (k = 0): latents 532

position 29 (`r1b1k1nr/p2ppp1p/6p1/8/8/q7/P1P1BPPP/R2Q1K1R w kq - 0 15`), split at ply 10: Rfe8 (53% there) vs Qxe7 (47%)

| chosen | subpar |
|---|---|
| 15.Qd4 Nf6 16.g4 O-O 17.g5 [Bb7] 18.gxf6 Bxh1 [19.fxe7] [Rfe8] 20.Qxd7 Qxe7 21.Qxe7 Rxe7 22.f3 [Bxf3] | 15.Qd4 Nf6 16.g4 O-O 17.g5 [Bb7] 18.gxf6 Bxh1 [19.fxe7] Qxe7 20.f3 Rfe8 21.Re1 Bxf3 22.Qf4 Bxe2+ |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20g6%205.Nc3%20Bg7%206.Be3%20Nf6%207.Nxc6%20bxc6%208.e5%20Ng8%209.Bd4%20c5%2010.Bxc5%20Qc7%2011.Ba3%20Bxe5%2012.Be2%20Bxc3%2B%2013.bxc3%20Qxc3%2B%2014.Kf1%20Qxa3%2015.Qd4%20Nf6%2016.g4%20O-O%2017.g5%20Bb7%2018.gxf6%20Bxh1%2019.fxe7%20Rfe8%2020.Qxd7%20Qxe7%2021.Qxe7%20Rxe7%2022.f3%20Bxf3#28) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20g6%205.Nc3%20Bg7%206.Be3%20Nf6%207.Nxc6%20bxc6%208.e5%20Ng8%209.Bd4%20c5%2010.Bxc5%20Qc7%2011.Ba3%20Bxe5%2012.Be2%20Bxc3%2B%2013.bxc3%20Qxc3%2B%2014.Kf1%20Qxa3%2015.Qd4%20Nf6%2016.g4%20O-O%2017.g5%20Bb7%2018.gxf6%20Bxh1%2019.fxe7%20Qxe7%2020.f3%20Rfe8%2021.Re1%20Bxf3%2022.Qf4%20Bxe2%2B#28) |

position 19 (`r4r1k/ppq1b1pp/2npQ3/4p3/1PP5/P1P2N2/5PPP/R1B2RK1 w - - 1 18`), split at ply 13: Nd2 (54% there) vs c5 (46%)

| chosen | subpar |
|---|---|
| 18.Be3 Rf6 19.Qg4 Rg6 [20.Qe4] Rf8 21.Rad1 Qc8 22.Kh1 [Qg4] 23.Qxg4 [Rxg4] [24.Nd2] Rg6 [25.Ne4] [Re6] | 18.Be3 Rf6 19.Qg4 Rg6 [20.Qe4] Rf8 21.Rad1 Qc8 22.Kh1 [Qg4] 23.Qxg4 [Rxg4] 24.c5 [e4] [25.Nd4] dxc5 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bc4%20Nf6%204.d3%20Be7%205.O-O%20O-O%206.Nc3%20d6%207.a3%20Be6%208.Qe2%20Bxc4%209.dxc4%20Nd7%2010.Nd5%20Nc5%2011.b4%20Ne6%2012.c3%20f5%2013.exf5%20Rxf5%2014.Qe4%20Rf8%2015.Qg4%20Qd7%2016.Nxc7%20Qxc7%2017.Qxe6%2B%20Kh8%2018.Be3%20Rf6%2019.Qg4%20Rg6%2020.Qe4%20Rf8%2021.Rad1%20Qc8%2022.Kh1%20Qg4%2023.Qxg4%20Rxg4%2024.Nd2%20Rg6%2025.Ne4%20Re6#34) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bc4%20Nf6%204.d3%20Be7%205.O-O%20O-O%206.Nc3%20d6%207.a3%20Be6%208.Qe2%20Bxc4%209.dxc4%20Nd7%2010.Nd5%20Nc5%2011.b4%20Ne6%2012.c3%20f5%2013.exf5%20Rxf5%2014.Qe4%20Rf8%2015.Qg4%20Qd7%2016.Nxc7%20Qxc7%2017.Qxe6%2B%20Kh8%2018.Be3%20Rf6%2019.Qg4%20Rg6%2020.Qe4%20Rf8%2021.Rad1%20Qc8%2022.Kh1%20Qg4%2023.Qxg4%20Rxg4%2024.c5%20e4%2025.Nd4%20dxc5#34) |

position 33 (`r2qk1r1/3bbpnp/p3N1p1/2ppB1P1/1p2P2P/1P3Q2/P1P2P2/2KR1B1R b q - 0 19`), split at ply 13: Qe8 (54% there) vs Bxc8 (46%)

| chosen | subpar |
|---|---|
| 19...Bxe6 20.exd5 Bf5 21.d6 Ra7 22.dxe7 Qxe7 23.Bxg7 Rxg7 24.Qc6+ Kf8 25.Qc8+ [Qe8] 26.Qxc5+ [Kg8] 27.Qxa7 | 19...Bxe6 20.exd5 Bf5 21.d6 Ra7 22.dxe7 Qxe7 23.Bxg7 Rxg7 24.Qc6+ Kf8 25.Qc8+ Bxc8 26.Rd8+ Qxd8 27.Bd3 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.Bf4%20a6%204.e3%20e6%205.g4%20Bb4%206.Ne2%20Be7%207.g5%20Nh5%208.h4%20b5%209.Bh2%20Nc6%2010.Nc1%20g6%2011.Nb3%20Ng7%2012.Qf3%20b4%2013.Na4%20Bd7%2014.O-O-O%20Nxd4%2015.Nxd4%20Bxa4%2016.Be5%20Rg8%2017.e4%20c5%2018.b3%20Bd7%2019.Nxe6%20Bxe6%2020.exd5%20Bf5%2021.d6%20Ra7%2022.dxe7%20Qxe7%2023.Bxg7%20Rxg7%2024.Qc6%2B%20Kf8%2025.Qc8%2B%20Qe8%2026.Qxc5%2B%20Kg8%2027.Qxa7#37) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.Bf4%20a6%204.e3%20e6%205.g4%20Bb4%206.Ne2%20Be7%207.g5%20Nh5%208.h4%20b5%209.Bh2%20Nc6%2010.Nc1%20g6%2011.Nb3%20Ng7%2012.Qf3%20b4%2013.Na4%20Bd7%2014.O-O-O%20Nxd4%2015.Nxd4%20Bxa4%2016.Be5%20Rg8%2017.e4%20c5%2018.b3%20Bd7%2019.Nxe6%20Bxe6%2020.exd5%20Bf5%2021.d6%20Ra7%2022.dxe7%20Qxe7%2023.Bxg7%20Rxg7%2024.Qc6%2B%20Kf8%2025.Qc8%2B%20Bxc8%2026.Rd8%2B%20Qxd8%2027.Bd3#37) |

#### S #10 (k = 0): latents 532

position 47 (`r2qr1k1/pp3ppp/1bn5/3p4/3Nb2n/1NP2PBP/PP2B1PK/R2Q1R2 b - - 0 16`), split at ply 3: Nf5 (52% there) vs Qg5 (46%)

| chosen | subpar |
|---|---|
| 16...Bg6 17.Re1 [Nf5] 18.Nxf5 [Bxf5] 19.Qd2 [d4] 20.cxd4 Nxd4 21.Nxd4 Qxd4 22.Qxd4 Bxd4 23.Bb5 Rxe1 24.Rxe1 | 16...Bg6 17.Re1 Qg5 18.Qd2 Qxd2 19.Nxd2 Nxd4 20.cxd4 Bxd4 21.Nb3 Bxb2 22.Rad1 Rad8 23.Bb5 Rxe1 24.Rxe1 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bg6%2017.Re1%20Nf5%2018.Nxf5%20Bxf5%2019.Qd2%20d4%2020.cxd4%20Nxd4%2021.Nxd4%20Qxd4%2022.Qxd4%20Bxd4%2023.Bb5%20Rxe1%2024.Rxe1#31) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bg6%2017.Re1%20Qg5%2018.Qd2%20Qxd2%2019.Nxd2%20Nxd4%2020.cxd4%20Bxd4%2021.Nb3%20Bxb2%2022.Rad1%20Rad8%2023.Bb5%20Rxe1%2024.Rxe1#31) |

position 12 (`2k4r/1pb3p1/p1n4p/5R2/4p2Q/P1PpB2P/1q4P1/R6K b - - 1 22`), split at ply 11: Re8 (55% there) vs d2 (45%)

| chosen | subpar |
|---|---|
| 22...Qxc3 [23.Rc1] Qxa3 [24.Rf7] Qd6 [25.Bf4] g5 26.Bxd6 gxh4 [27.Bxc7] [Re8] 28.Bf4 [e3] 29.Bxe3 [Rxe3] [30.Rd1] | 22...Qxc3 [23.Rc1] Qxa3 [24.Rf7] Qd6 [25.Bf4] g5 26.Bxd6 gxh4 [27.Bxc7] d2 [28.Rd1] e3 29.Bf4 Re8 30.Rc7+ |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.e4%20dxe4%204.f3%20exf3%205.Nxf3%20c5%206.Bd3%20cxd4%207.Ne4%20Nxe4%208.Bxe4%20Nc6%209.O-O%20Qb6%2010.Kh1%20e5%2011.Qe1%20Bd6%2012.Ng5%20Bd7%2013.a3%20O-O-O%2014.Nxf7%20Bc7%2015.Nxh8%20Rxh8%2016.Rf7%20h6%2017.c3%20a6%2018.Bf5%20Bxf5%2019.Rxf5%20d3%2020.Be3%20Qxb2%2021.h3%20e4%2022.Qh4%20Qxc3%2023.Rc1%20Qxa3%2024.Rf7%20Qd6%2025.Bf4%20g5%2026.Bxd6%20gxh4%2027.Bxc7%20Re8%2028.Bf4%20e3%2029.Bxe3%20Rxe3%2030.Rd1#43) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.e4%20dxe4%204.f3%20exf3%205.Nxf3%20c5%206.Bd3%20cxd4%207.Ne4%20Nxe4%208.Bxe4%20Nc6%209.O-O%20Qb6%2010.Kh1%20e5%2011.Qe1%20Bd6%2012.Ng5%20Bd7%2013.a3%20O-O-O%2014.Nxf7%20Bc7%2015.Nxh8%20Rxh8%2016.Rf7%20h6%2017.c3%20a6%2018.Bf5%20Bxf5%2019.Rxf5%20d3%2020.Be3%20Qxb2%2021.h3%20e4%2022.Qh4%20Qxc3%2023.Rc1%20Qxa3%2024.Rf7%20Qd6%2025.Bf4%20g5%2026.Bxd6%20gxh4%2027.Bxc7%20d2%2028.Rd1%20e3%2029.Bf4%20Re8%2030.Rc7%2B#43) |

position 42 (`rnb2rk1/5ppp/p3pn2/1p1p4/q7/B3P1P1/3NNPBP/R2Q1RK1 w - - 0 14`), split at ply 10: Ne5 (55% there) vs Nxd4 (45%)

| chosen | subpar |
|---|---|
| 14.Qxa4 bxa4 15.Bxf8 Kxf8 16.Rxa4 Nc6 17.Rc1 Bd7 [18.Nd4] [Ne5] [19.Rxa6] [Rxa6] [20.Rc7] Ra1+ [21.Bf1] [g5] | 14.Qxa4 bxa4 15.Bxf8 Kxf8 16.Rxa4 Nc6 17.Rc1 Bd7 [18.Nd4] Nxd4 [19.Rxd4] a5 [20.e4] e5 21.Rxd5 [Nxd5] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.e3%20e6%203.Ne2%20c5%204.Nd2%20a6%205.g3%20Nf6%206.Bg2%20Be7%207.O-O%20O-O%208.c3%20b5%209.a4%20Qa5%2010.dxc5%20Bxc5%2011.b4%20Bxb4%2012.cxb4%20Qxb4%2013.Ba3%20Qxa4%2014.Qxa4%20bxa4%2015.Bxf8%20Kxf8%2016.Rxa4%20Nc6%2017.Rc1%20Bd7%2018.Nd4%20Ne5%2019.Rxa6%20Rxa6%2020.Rc7%20Ra1%2B%2021.Bf1%20g5#26) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.e3%20e6%203.Ne2%20c5%204.Nd2%20a6%205.g3%20Nf6%206.Bg2%20Be7%207.O-O%20O-O%208.c3%20b5%209.a4%20Qa5%2010.dxc5%20Bxc5%2011.b4%20Bxb4%2012.cxb4%20Qxb4%2013.Ba3%20Qxa4%2014.Qxa4%20bxa4%2015.Bxf8%20Kxf8%2016.Rxa4%20Nc6%2017.Rc1%20Bd7%2018.Nd4%20Nxd4%2019.Rxd4%20a5%2020.e4%20e5%2021.Rxd5%20Nxd5#26) |

## W

| k | pairs | nonzero v | families | held-out recurrence: median / 90% / max | null 95th: median | null (every draw): 90% / 99% | families above their null 95th (chance: 5%) |
|---|---|---|---|---|---|---|---|
| 0 | 2462 | 100% | 641 | 0.7% / 2.6% / 7.6% | 1.7% | 2.3% / 5.9% | 36 (6%) |
| 2 | 2460 | 32% | 601 | 0.0% / 0.2% / 0.8% | 0.1% | 0.1% / 0.3% | 56 (9%) |
| 4 | 2458 | 16% | 333 | 0.0% / 0.2% / 1.4% | 0.0% | 0.0% / 0.2% | 48 (14%) |
| 6 | 2455 | 14% | 292 | 0.0% / 0.2% / 1.2% | 0.0% | 0.0% / 0.1% | 50 (17%) |

### W: the top 20 families by held-out recurrence

| # | k | latents (weight) | found in | held out on | recurrence | null 95th | persistence (pairs on at split) | positions found |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 619 (1.00) | A (7 v's) | B | 7.6% | 5.9% | 1.0 (92) | 0, 7, 16, 18, 28, 34, 35 |
| 2 | 0 | 49 (1.00) | B (46 v's) | A | 7.2% | 5.1% | 1.0 (90) | 2, 13, 14, 15, 21, 22, 23, 27, 32, 36, 39, 40 ... |
| 3 | 0 | 532 (1.00) | B (2 v's) | A | 7.0% | 5.7% | 1.0 (88) | 22, 23 |
| 4 | 0 | 556 (1.00) | A (3 v's) | B | 7.0% | 4.9% | 1.0 (85) | 25, 29, 35 |
| 5 | 0 | 19 (1.00) | A (65 v's) | B | 6.7% | 5.3% | 1.0 (81) | 0, 3, 5, 6, 9, 11, 16, 20, 24, 25, 26, 28 ... |
| 6 | 0 | 1640 (1.00) | A (1 v's) | B | 6.4% | 4.5% | 1.0 (78) | 29 |
| 7 | 0 | 619 (1.00) | B (4 v's) | A | 6.2% | 5.4% | 1.0 (78) | 8, 17, 36, 43 |
| 8 | 0 | 2179 (1.00) | B (1 v's) | A | 6.2% | 4.9% | 1.0 (78) | 32 |
| 9 | 0 | 19 (1.00) | B (73 v's) | A | 6.0% | 6.1% | 1.0 (75) | 2, 4, 8, 10, 12, 13, 14, 17, 23, 27, 30, 36 ... |
| 10 | 0 | 705 (1.00) | B (3 v's) | A | 5.9% | 5.0% | 1.0 (74) | 15, 42, 47 |
| 11 | 0 | 570 (1.00) | A (3 v's) | B | 5.8% | 4.7% | 1.0 (70) | 19, 20, 28 |
| 12 | 0 | 570 (1.00) | B (4 v's) | A | 5.8% | 5.1% | 1.0 (72) | 15, 30, 47, 48 |
| 13 | 0 | 1220 (1.00) | A (1 v's) | B | 5.5% | 4.9% | 1.0 (67) | 16 |
| 14 | 0 | 1043 (1.00) | A (1 v's) | B | 5.4% | 5.6% | 1.0 (65) | 38 |
| 15 | 0 | 1640 (1.00) | B (3 v's) | A | 5.4% | 5.1% | 1.0 (67) | 1, 21 |
| 16 | 0 | 49 (1.00) | A (75 v's) | B | 5.3% | 5.9% | 1.0 (64) | 0, 3, 5, 6, 7, 9, 11, 16, 18, 19, 24, 25 ... |
| 17 | 0 | 705 (1.00) | A (1 v's) | B | 5.2% | 5.3% | 1.0 (63) | 20 |
| 18 | 0 | 901 (1.00) | B (2 v's) | A | 5.0% | 6.0% | 1.0 (63) | 15 |
| 19 | 0 | 1220 (1.00) | B (1 v's) | A | 4.9% | 5.8% | 1.0 (61) | 15 |
| 20 | 0 | 405 (1.00) | A (9 v's) | B | 4.7% | 4.5% | 1.0 (57) | 6, 7, 19, 25, 28, 31 |

#### W #1 (k = 0): latents 619

position 42 (`rnb2rk1/5ppp/p3pn2/1p1p4/q7/B3P1P1/3NNPBP/R2Q1RK1 w - - 0 14`), split at ply 6: Bb7 (54% there) vs Nc6 (46%)

| chosen | subpar |
|---|---|
| 14.Bxf8 Qxd1 [15.Rfxd1] [Kxf8] 16.Nb3 [Bb7] 17.Nc5 [Bc6] 18.Nd4 [Nbd7] [19.Nxc6] [Nxc5] [20.Rdc1] [Nce4] 21.Bxe4 [Nxe4] | 14.Bxf8 Qxd1 [15.Rfxd1] [Kxf8] 16.Nb3 Nc6 17.Nc5 Nb4 18.Nd4 e5 [19.Nc6] Nxc6 20.Bxd5 [Nxd5] 21.Rxd5 [Be6] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.e3%20e6%203.Ne2%20c5%204.Nd2%20a6%205.g3%20Nf6%206.Bg2%20Be7%207.O-O%20O-O%208.c3%20b5%209.a4%20Qa5%2010.dxc5%20Bxc5%2011.b4%20Bxb4%2012.cxb4%20Qxb4%2013.Ba3%20Qxa4%2014.Bxf8%20Qxd1%2015.Rfxd1%20Kxf8%2016.Nb3%20Bb7%2017.Nc5%20Bc6%2018.Nd4%20Nbd7%2019.Nxc6%20Nxc5%2020.Rdc1%20Nce4%2021.Bxe4%20Nxe4#26) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.e3%20e6%203.Ne2%20c5%204.Nd2%20a6%205.g3%20Nf6%206.Bg2%20Be7%207.O-O%20O-O%208.c3%20b5%209.a4%20Qa5%2010.dxc5%20Bxc5%2011.b4%20Bxb4%2012.cxb4%20Qxb4%2013.Ba3%20Qxa4%2014.Bxf8%20Qxd1%2015.Rfxd1%20Kxf8%2016.Nb3%20Nc6%2017.Nc5%20Nb4%2018.Nd4%20e5%2019.Nc6%20Nxc6%2020.Bxd5%20Nxd5%2021.Rxd5%20Be6#26) |

position 4 (`r1bq1b1r/3k2pp/p1p5/1p1Bp1N1/8/3P4/PPP2PPP/RNB1K2R w KQ - 0 12`), split at ply 16: Kb6 (49% there) vs e4 (46%)

| chosen | subpar |
|---|---|
| 12.Be6+ [Kc7] 13.Bxc8 Rxc8 14.Nf7 [Qf6] [15.Nxh8] Bc5 [16.O-O] Rxh8 17.Nc3 Rf8 [18.Ne4] [Qf5] 19.Nxc5 [Kb6] | 12.Be6+ [Kc7] 13.Bxc8 Rxc8 14.Nf7 [Qf6] [15.Nxh8] Bc5 [16.O-O] Rxh8 17.Nc3 Rf8 [18.Ne4] [Qf5] 19.Nxc5 e4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Bc4%20a6%203.d3%20Nf6%204.Nf3%20b5%205.Bb3%20Nc6%206.Ng5%20d5%207.exd5%20Nxd5%208.Qf3%20Nce7%209.Qxf7%2B%20Kd7%2010.Qxd5%2B%20Nxd5%2011.Bxd5%20c6%2012.Be6%2B%20Kc7%2013.Bxc8%20Rxc8%2014.Nf7%20Qf6%2015.Nxh8%20Bc5%2016.O-O%20Rxh8%2017.Nc3%20Rf8%2018.Ne4%20Qf5%2019.Nxc5%20Kb6#22) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Bc4%20a6%203.d3%20Nf6%204.Nf3%20b5%205.Bb3%20Nc6%206.Ng5%20d5%207.exd5%20Nxd5%208.Qf3%20Nce7%209.Qxf7%2B%20Kd7%2010.Qxd5%2B%20Nxd5%2011.Bxd5%20c6%2012.Be6%2B%20Kc7%2013.Bxc8%20Rxc8%2014.Nf7%20Qf6%2015.Nxh8%20Bc5%2016.O-O%20Rxh8%2017.Nc3%20Rf8%2018.Ne4%20Qf5%2019.Nxc5%20e4#22) |

position 10 (`2r2rk1/pp1bb1pp/1qn1pn2/3p1p2/PP1P4/2P2N1P/3NBPPB/R1Q2RK1 w - - 1 15`), split at ply 16: Qxb8 (50% there) vs Ne4 (45%)

| chosen | subpar |
|---|---|
| 15.a5 [Qd8] [16.b5] [Nxa5] [17.Nb3] [Nxb3] [18.Qb2] [Nxa1] 19.Rxa1 [a6] [20.bxa6] bxa6 21.Bxa6 [Rb8] [22.Bxb8] [Qxb8] | 15.a5 [Qd8] [16.b5] [Nxa5] [17.Nb3] [Nxb3] [18.Qb2] [Nxa1] 19.Rxa1 [a6] [20.bxa6] bxa6 21.Bxa6 [Rb8] [22.Bxb8] Ne4 |
| [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nf6%202.d4%20e6%203.Bf4%20c5%204.e3%20cxd4%205.exd4%20Qb6%206.Qc1%20Nc6%207.c3%20Be7%208.Nbd2%20d5%209.h3%20Nh5%2010.Bh2%20O-O%2011.Be2%20Bd7%2012.O-O%20f5%2013.b4%20Nf6%2014.a4%20Rac8%2015.a5%20Qd8%2016.b5%20Nxa5%2017.Nb3%20Nxb3%2018.Qb2%20Nxa1%2019.Rxa1%20a6%2020.bxa6%20bxa6%2021.Bxa6%20Rb8%2022.Bxb8%20Qxb8#28) | [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nf6%202.d4%20e6%203.Bf4%20c5%204.e3%20cxd4%205.exd4%20Qb6%206.Qc1%20Nc6%207.c3%20Be7%208.Nbd2%20d5%209.h3%20Nh5%2010.Bh2%20O-O%2011.Be2%20Bd7%2012.O-O%20f5%2013.b4%20Nf6%2014.a4%20Rac8%2015.a5%20Qd8%2016.b5%20Nxa5%2017.Nb3%20Nxb3%2018.Qb2%20Nxa1%2019.Rxa1%20a6%2020.bxa6%20bxa6%2021.Bxa6%20Rb8%2022.Bxb8%20Ne4#28) |

#### W #2 (k = 0): latents 49

position 7 (`2q2rk1/1Q3pp1/p1N1p2p/3p4/8/6P1/3r1P1P/1R3RK1 w - - 3 24`), split at ply 4: Rc2 (49% there) vs Rxc8 (46%)

| chosen | subpar |
|---|---|
| 24.Ne7+ [Kh7] 25.Nxc8 [Rc2] 26.Ne7 Rcc8 27.Nxc8 Rxc8 28.Qxc8 a5 29.Qa6 a4 30.Qxa4 d4 31.Qxd4 e5 | 24.Ne7+ [Kh7] 25.Nxc8 Rxc8 26.Qxc8 d4 27.Qxa6 d3 [28.Rbd1] Rxd1 29.Rxd1 d2 30.Rxd2 e5 31.Qd3+ g6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.Qf3%20e6%203.Bc4%20Nf6%204.d4%20d5%205.exd5%20cxd5%206.Bb5%2B%20Bd7%207.Bxd7%2B%20Nbxd7%208.Bg5%20Be7%209.Nc3%20h6%2010.Bxf6%20Bxf6%2011.Nge2%20O-O%2012.O-O%20Nb6%2013.Nb5%20Nc4%2014.Qd3%20Nxb2%2015.Qc3%20Nc4%2016.Rab1%20a6%2017.Na3%20Rc8%2018.Nxc4%20Rxc4%2019.Qb3%20Bxd4%2020.Qxb7%20Rxc2%2021.Nxd4%20Rxa2%2022.g3%20Rd2%2023.Nc6%20Qc8%2024.Ne7%2B%20Kh7%2025.Nxc8%20Rc2%2026.Ne7%20Rcc8%2027.Nxc8%20Rxc8%2028.Qxc8%20a5%2029.Qa6%20a4%2030.Qxa4%20d4%2031.Qxd4%20e5#46) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.Qf3%20e6%203.Bc4%20Nf6%204.d4%20d5%205.exd5%20cxd5%206.Bb5%2B%20Bd7%207.Bxd7%2B%20Nbxd7%208.Bg5%20Be7%209.Nc3%20h6%2010.Bxf6%20Bxf6%2011.Nge2%20O-O%2012.O-O%20Nb6%2013.Nb5%20Nc4%2014.Qd3%20Nxb2%2015.Qc3%20Nc4%2016.Rab1%20a6%2017.Na3%20Rc8%2018.Nxc4%20Rxc4%2019.Qb3%20Bxd4%2020.Qxb7%20Rxc2%2021.Nxd4%20Rxa2%2022.g3%20Rd2%2023.Nc6%20Qc8%2024.Ne7%2B%20Kh7%2025.Nxc8%20Rxc8%2026.Qxc8%20d4%2027.Qxa6%20d3%2028.Rbd1%20Rxd1%2029.Rxd1%20d2%2030.Rxd2%20e5%2031.Qd3%2B%20g6#46) |

position 34 (`r2qk2r/1pp1bppp/2n1p3/1p6/3PR3/P1P2N2/5PPP/R2Q2K1 b kq - 0 14`), split at ply 9: Rxa3 (50% there) vs Na5 (45%)

| chosen | subpar |
|---|---|
| 14...O-O 15.Qb3 Na5 16.Qxb5 c6 17.Qd3 Nb3 18.Rb1 [Rxa3] 19.Ne5 Nc5 [20.Qf3] Nxe4 21.Qxe4 Rxc3 22.Rxb7 | 14...O-O 15.Qb3 Na5 16.Qxb5 c6 17.Qd3 Nb3 18.Rb1 Na5 19.c4 c5 20.d5 exd5 21.cxd5 Bf6 22.d6 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20O-O%2015.Qb3%20Na5%2016.Qxb5%20c6%2017.Qd3%20Nb3%2018.Rb1%20Rxa3%2019.Ne5%20Nc5%2020.Qf3%20Nxe4%2021.Qxe4%20Rxc3%2022.Rxb7#27) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20O-O%2015.Qb3%20Na5%2016.Qxb5%20c6%2017.Qd3%20Nb3%2018.Rb1%20Na5%2019.c4%20c5%2020.d5%20exd5%2021.cxd5%20Bf6%2022.d6#27) |

position 33 (`r2qk1r1/3bbpnp/p3N1p1/2ppB1P1/1p2P2P/1P3Q2/P1P2P2/2KR1B1R b q - 0 19`), split at ply 5: Qa5 (54% there) vs Qb6 (44%)

| chosen | subpar |
|---|---|
| 19...Bxe6 20.exd5 Bxd5 [21.Rxd5] [Qa5] 22.Bc4 Qxa2 23.Kd2 [Rd8] 24.Rxd8+ Bxd8 25.Qxf7# | 19...Bxe6 20.exd5 Bxd5 [21.Rxd5] Qb6 22.Bc4 [Rd8] 23.Rxd8+ Bxd8 24.Qxf7# |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.Bf4%20a6%204.e3%20e6%205.g4%20Bb4%206.Ne2%20Be7%207.g5%20Nh5%208.h4%20b5%209.Bh2%20Nc6%2010.Nc1%20g6%2011.Nb3%20Ng7%2012.Qf3%20b4%2013.Na4%20Bd7%2014.O-O-O%20Nxd4%2015.Nxd4%20Bxa4%2016.Be5%20Rg8%2017.e4%20c5%2018.b3%20Bd7%2019.Nxe6%20Bxe6%2020.exd5%20Bxd5%2021.Rxd5%20Qa5%2022.Bc4%20Qxa2%2023.Kd2%20Rd8%2024.Rxd8%2B%20Bxd8%2025.Qxf7%23#37) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.Bf4%20a6%204.e3%20e6%205.g4%20Bb4%206.Ne2%20Be7%207.g5%20Nh5%208.h4%20b5%209.Bh2%20Nc6%2010.Nc1%20g6%2011.Nb3%20Ng7%2012.Qf3%20b4%2013.Na4%20Bd7%2014.O-O-O%20Nxd4%2015.Nxd4%20Bxa4%2016.Be5%20Rg8%2017.e4%20c5%2018.b3%20Bd7%2019.Nxe6%20Bxe6%2020.exd5%20Bxd5%2021.Rxd5%20Qb6%2022.Bc4%20Rd8%2023.Rxd8%2B%20Bxd8%2024.Qxf7%23#37) |

#### W #3 (k = 0): latents 532

position 37 (`2r2k1r/1p1B1p1p/p5p1/2PpP3/6P1/P3q3/1P1NN1P1/n2K3Q w - - 2 26`), split at ply 4: Kg7 (52% there) vs Ke7 (48%)

| chosen | subpar |
|---|---|
| 26.e6 fxe6 27.Bxc8 [Kg7] 28.Bxb7 [Rb8] 29.Bxa6 [Rxb2] 30.Qh4 Qxd2# | 26.e6 fxe6 27.Bxc8 Ke7 28.Bxb7 [Rb8] 29.Bxa6 [Rxb2] 30.Qxh7+ Kf6 31.Qh8+ [Kg5] 32.Qxb2 [Qxc5] 33.Qxa1 Qf2 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20e6%203.e3%20Bd6%204.Bg3%20Bxg3%205.hxg3%20Nc6%206.c4%20Nge7%207.a3%20Bd7%208.Qg4%20g6%209.Qg5%20Nf5%2010.Qf4%20Qe7%2011.g4%20Nd6%2012.c5%20Ne4%2013.Qxc7%20Bc8%2014.Qf4%20e5%2015.Qh6%20Bxg4%2016.f3%20Ng3%2017.fxg4%20Nxh1%2018.Qxh1%20Qg5%2019.Be2%20Qxe3%2020.dxe5%20Nd4%2021.Nd2%20Nc2%2B%2022.Kd1%20Nxa1%2023.Bb5%2B%20Kf8%2024.Ne2%20a6%2025.Bd7%20Rc8%2026.e6%20fxe6%2027.Bxc8%20Kg7%2028.Bxb7%20Rb8%2029.Bxa6%20Rxb2%2030.Qh4%20Qxd2%23#50) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20e6%203.e3%20Bd6%204.Bg3%20Bxg3%205.hxg3%20Nc6%206.c4%20Nge7%207.a3%20Bd7%208.Qg4%20g6%209.Qg5%20Nf5%2010.Qf4%20Qe7%2011.g4%20Nd6%2012.c5%20Ne4%2013.Qxc7%20Bc8%2014.Qf4%20e5%2015.Qh6%20Bxg4%2016.f3%20Ng3%2017.fxg4%20Nxh1%2018.Qxh1%20Qg5%2019.Be2%20Qxe3%2020.dxe5%20Nd4%2021.Nd2%20Nc2%2B%2022.Kd1%20Nxa1%2023.Bb5%2B%20Kf8%2024.Ne2%20a6%2025.Bd7%20Rc8%2026.e6%20fxe6%2027.Bxc8%20Ke7%2028.Bxb7%20Rb8%2029.Bxa6%20Rxb2%2030.Qxh7%2B%20Kf6%2031.Qh8%2B%20Kg5%2032.Qxb2%20Qxc5%2033.Qxa1%20Qf2#50) |

position 45 (`r4rk1/pp4pp/1b3q2/1P1pRp2/P7/1QP3P1/5P1P/R5K1 b - - 2 26`), split at ply 15: Bxf2 (54% there) vs Qg4+ (46%)

| chosen | subpar |
|---|---|
| [26...Qxe5] [27.a5] [Bc5] [28.b6] axb6 [29.axb6] [Rxa1+] 30.Kg2 [Qe4+] 31.Kh3 Qg4+ 32.Kg2 [Qe4+] [33.Kh3] [Bxf2] 34.c4 | [26...Qxe5] [27.a5] [Bc5] [28.b6] axb6 [29.axb6] [Rxa1+] 30.Kg2 [Qe4+] 31.Kh3 Qg4+ 32.Kg2 [Qe4+] [33.Kh3] Qg4+ 34.Kg2 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.e5%20c5%204.dxc5%20Nc6%205.Bf4%20e6%206.Bb5%20Bd7%207.Na3%20Bxc5%208.Nf3%20Nge7%209.O-O%20Ng6%2010.Bg5%20f6%2011.Bh4%20Nxh4%2012.Nxh4%20Nxe5%2013.Bxd7%2B%20Qxd7%2014.c3%20O-O%2015.b4%20Bb6%2016.b5%20Qe7%2017.Nc2%20Ng4%2018.Nd4%20Ne5%2019.a4%20Nc4%2020.Re1%20f5%2021.Rxe6%20Qxh4%2022.g3%20Qg5%2023.Nf3%20Qd8%2024.Ne5%20Nxe5%2025.Rxe5%20Qf6%2026.Qb3%20Qxe5%2027.a5%20Bc5%2028.b6%20axb6%2029.axb6%20Rxa1%2B%2030.Kg2%20Qe4%2B%2031.Kh3%20Qg4%2B%2032.Kg2%20Qe4%2B%2033.Kh3%20Bxf2%2034.c4#51) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.e5%20c5%204.dxc5%20Nc6%205.Bf4%20e6%206.Bb5%20Bd7%207.Na3%20Bxc5%208.Nf3%20Nge7%209.O-O%20Ng6%2010.Bg5%20f6%2011.Bh4%20Nxh4%2012.Nxh4%20Nxe5%2013.Bxd7%2B%20Qxd7%2014.c3%20O-O%2015.b4%20Bb6%2016.b5%20Qe7%2017.Nc2%20Ng4%2018.Nd4%20Ne5%2019.a4%20Nc4%2020.Re1%20f5%2021.Rxe6%20Qxh4%2022.g3%20Qg5%2023.Nf3%20Qd8%2024.Ne5%20Nxe5%2025.Rxe5%20Qf6%2026.Qb3%20Qxe5%2027.a5%20Bc5%2028.b6%20axb6%2029.axb6%20Rxa1%2B%2030.Kg2%20Qe4%2B%2031.Kh3%20Qg4%2B%2032.Kg2%20Qe4%2B%2033.Kh3%20Qg4%2B%2034.Kg2#51) |

position 31 (`5r2/5k2/p2q1p1r/1pn4p/8/P1N2Q1P/1P3PP1/3RR1K1 b - - 3 25`), split at ply 8: Rc1 (50% there) vs Qe7+ (44%)

| chosen | subpar |
|---|---|
| 25...Qc7 26.Qd5+ [Kg7] [27.Ne4] Nxe4 28.Qxe4 [Rg6] [29.Rc1] [Qd7] [30.Red1] Qf7 31.Rc6 Re8 32.Qf3 Re6 33.Rxe6 | 25...Qc7 26.Qd5+ [Kg7] [27.Ne4] Nxe4 28.Qxe4 [Rg6] 29.Qe7+ [Qxe7] [30.Rxe7+] Rf7 31.Rxf7+ [Kxf7] 32.Rd7+ Ke6 33.Ra7 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.Bb5%20Qc7%204.O-O%20e6%205.Re1%20h5%206.c3%20Nf6%207.d4%20cxd4%208.cxd4%20a6%209.Bf1%20Ng4%2010.h3%20f6%2011.Nc3%20b5%2012.a3%20Bb7%2013.e5%20Nh6%2014.Bxh6%20Rxh6%2015.exf6%20gxf6%2016.d5%20Nd8%2017.Nd4%20Kf7%2018.Be2%20Qe5%2019.Bf3%20Qf4%2020.dxe6%2B%20dxe6%2021.Bxb7%20Nxb7%2022.Nxe6%20Qd6%2023.Nxf8%20Rxf8%2024.Qf3%20Nc5%2025.Rad1%20Qc7%2026.Qd5%2B%20Kg7%2027.Ne4%20Nxe4%2028.Qxe4%20Rg6%2029.Rc1%20Qd7%2030.Red1%20Qf7%2031.Rc6%20Re8%2032.Qf3%20Re6%2033.Rxe6#49) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.Bb5%20Qc7%204.O-O%20e6%205.Re1%20h5%206.c3%20Nf6%207.d4%20cxd4%208.cxd4%20a6%209.Bf1%20Ng4%2010.h3%20f6%2011.Nc3%20b5%2012.a3%20Bb7%2013.e5%20Nh6%2014.Bxh6%20Rxh6%2015.exf6%20gxf6%2016.d5%20Nd8%2017.Nd4%20Kf7%2018.Be2%20Qe5%2019.Bf3%20Qf4%2020.dxe6%2B%20dxe6%2021.Bxb7%20Nxb7%2022.Nxe6%20Qd6%2023.Nxf8%20Rxf8%2024.Qf3%20Nc5%2025.Rad1%20Qc7%2026.Qd5%2B%20Kg7%2027.Ne4%20Nxe4%2028.Qxe4%20Rg6%2029.Qe7%2B%20Qxe7%2030.Rxe7%2B%20Rf7%2031.Rxf7%2B%20Kxf7%2032.Rd7%2B%20Ke6%2033.Ra7#49) |

#### W #4 (k = 0): latents 556

position 14 (`2r1k2r/1bqpbpp1/p3p2p/1p4Pn/3nP1BP/2N1BP2/PPPQ4/2KR3R w k - 0 15`), split at ply 13: Rxc8 (56% there) vs Qb4+ (44%)

| chosen | subpar |
|---|---|
| [15.Qxd4] [Nf4] 16.Bxf4 Qxf4+ [17.Kb1] hxg5 [18.hxg5] Rxh1 [19.Rxh1] Bxg5 20.Rh8+ Ke7 [21.Rxc8] Bxc8 22.Qc5+ Kf6 | [15.Qxd4] [Nf4] 16.Bxf4 Qxf4+ [17.Kb1] hxg5 [18.hxg5] Rxh1 [19.Rxh1] Bxg5 20.Rh8+ Ke7 21.Qb4+ [d6] [22.Rxc8] Bxc8 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Qxd4%20Nf4%2016.Bxf4%20Qxf4%2B%2017.Kb1%20hxg5%2018.hxg5%20Rxh1%2019.Rxh1%20Bxg5%2020.Rh8%2B%20Ke7%2021.Rxc8%20Bxc8%2022.Qc5%2B%20Kf6#28) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Qxd4%20Nf4%2016.Bxf4%20Qxf4%2B%2017.Kb1%20hxg5%2018.hxg5%20Rxh1%2019.Rxh1%20Bxg5%2020.Rh8%2B%20Ke7%2021.Qb4%2B%20d6%2022.Rxc8%20Bxc8#28) |

position 12 (`2k4r/1pb3p1/p1n4p/5R2/4p2Q/P1PpB2P/1q4P1/R6K b - - 1 22`), split at ply 6: Qxe4 (50% there) vs Qxg7 (44%)

| chosen | subpar |
|---|---|
| [22...Qxa1+] 23.Bg1 [Qxc3] 24.Qg4 [Kb8] [25.Qxe4] [d2] 26.Rd5 [Qc1] 27.Rxd2 [Qxd2] 28.Bh2 [Bxh2] 29.Kxh2 [Qd6+] 30.Kh1 | [22...Qxa1+] 23.Bg1 [Qxc3] 24.Qg4 [Kb8] 25.Qxg7 [Qxg7] [26.Rf7] [Qxf7] [27.Bh2] [Bxh2] [28.Kxh2] [d2] [29.Kg3] [d1=Q] [30.Kh4] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.e4%20dxe4%204.f3%20exf3%205.Nxf3%20c5%206.Bd3%20cxd4%207.Ne4%20Nxe4%208.Bxe4%20Nc6%209.O-O%20Qb6%2010.Kh1%20e5%2011.Qe1%20Bd6%2012.Ng5%20Bd7%2013.a3%20O-O-O%2014.Nxf7%20Bc7%2015.Nxh8%20Rxh8%2016.Rf7%20h6%2017.c3%20a6%2018.Bf5%20Bxf5%2019.Rxf5%20d3%2020.Be3%20Qxb2%2021.h3%20e4%2022.Qh4%20Qxa1%2B%2023.Bg1%20Qxc3%2024.Qg4%20Kb8%2025.Qxe4%20d2%2026.Rd5%20Qc1%2027.Rxd2%20Qxd2%2028.Bh2%20Bxh2%2029.Kxh2%20Qd6%2B%2030.Kh1#43) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.e4%20dxe4%204.f3%20exf3%205.Nxf3%20c5%206.Bd3%20cxd4%207.Ne4%20Nxe4%208.Bxe4%20Nc6%209.O-O%20Qb6%2010.Kh1%20e5%2011.Qe1%20Bd6%2012.Ng5%20Bd7%2013.a3%20O-O-O%2014.Nxf7%20Bc7%2015.Nxh8%20Rxh8%2016.Rf7%20h6%2017.c3%20a6%2018.Bf5%20Bxf5%2019.Rxf5%20d3%2020.Be3%20Qxb2%2021.h3%20e4%2022.Qh4%20Qxa1%2B%2023.Bg1%20Qxc3%2024.Qg4%20Kb8%2025.Qxg7%20Qxg7%2026.Rf7%20Qxf7%2027.Bh2%20Bxh2%2028.Kxh2%20d2%2029.Kg3%20d1%3DQ%2030.Kh4#43) |

position 32 (`r2qk2r/ppp2ppp/2n5/7b/1b1P4/2P2N1P/PB2BPP1/R2QK2R b KQkq - 0 12`), split at ply 16: e6 (57% there) vs c4 (43%)

| chosen | subpar |
|---|---|
| 12...Ba5 13.O-O O-O 14.Re1 Re8 15.Ne5 Nxe5 16.dxe5 Qxd1 [17.Raxd1] Bxe2 [18.Rxe2] [Rad8] 19.Rxd8 [Rxd8] [20.e6] | 12...Ba5 13.O-O O-O 14.Re1 Re8 15.Ne5 Nxe5 16.dxe5 Qxd1 [17.Raxd1] Bxe2 [18.Rxe2] [Rad8] 19.Rxd8 [Rxd8] 20.c4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20d5%202.exd5%20Nf6%203.Nc3%20Nxd5%204.Bc4%20Nxc3%205.bxc3%20Nc6%206.Bb2%20e5%207.Nf3%20Bg4%208.h3%20Bh5%209.Be2%20Bc5%2010.d4%20exd4%2011.cxd4%20Bb4%2B%2012.c3%20Ba5%2013.O-O%20O-O%2014.Re1%20Re8%2015.Ne5%20Nxe5%2016.dxe5%20Qxd1%2017.Raxd1%20Bxe2%2018.Rxe2%20Rad8%2019.Rxd8%20Rxd8%2020.e6#23) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20d5%202.exd5%20Nf6%203.Nc3%20Nxd5%204.Bc4%20Nxc3%205.bxc3%20Nc6%206.Bb2%20e5%207.Nf3%20Bg4%208.h3%20Bh5%209.Be2%20Bc5%2010.d4%20exd4%2011.cxd4%20Bb4%2B%2012.c3%20Ba5%2013.O-O%20O-O%2014.Re1%20Re8%2015.Ne5%20Nxe5%2016.dxe5%20Qxd1%2017.Raxd1%20Bxe2%2018.Rxe2%20Rad8%2019.Rxd8%20Rxd8%2020.c4#23) |

#### W #5 (k = 0): latents 19

position 14 (`2r1k2r/1bqpbpp1/p3p2p/1p4Pn/3nP1BP/2N1BP2/PPPQ4/2KR3R w k - 0 15`), split at ply 8: Rg5 (54% there) vs Rxg7 (46%)

| chosen | subpar |
|---|---|
| [15.Bxd4] [Nf4] [16.gxh6] Rxh6 [17.Bxg7] [Rg6] [18.h5] [Rg5] [19.h6] [Ng6] [20.h7] [Kd8] [21.h8=Q+] [Nxh8] [22.Rxh8+] [Bf8] | [15.Bxd4] [Nf4] [16.gxh6] Rxh6 [17.Bxg7] [Rg6] [18.h5] Rxg7 [19.h6] Rh7 [20.Ne2] Nxe2+ 21.Qxe2 Bg5+ 22.Kb1 Bxh6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Bxd4%20Nf4%2016.gxh6%20Rxh6%2017.Bxg7%20Rg6%2018.h5%20Rg5%2019.h6%20Ng6%2020.h7%20Kd8%2021.h8%3DQ%2B%20Nxh8%2022.Rxh8%2B%20Bf8#28) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Bxd4%20Nf4%2016.gxh6%20Rxh6%2017.Bxg7%20Rg6%2018.h5%20Rxg7%2019.h6%20Rh7%2020.Ne2%20Nxe2%2B%2021.Qxe2%20Bg5%2B%2022.Kb1%20Bxh6#28) |

position 12 (`2k4r/1pb3p1/p1n4p/5R2/4p2Q/P1PpB2P/1q4P1/R6K b - - 1 22`), split at ply 10: Rd5 (56% there) vs Rf1 (44%)

| chosen | subpar |
|---|---|
| [22...Qxa1+] [23.Bg1] Qxc3 24.Qg4 Kb8 [25.Qxg7] Qxg7 [26.Bc5] d2 [27.Rd5] Rd8 [28.Rxd8+] Nxd8 [29.Bd6] Bxd6 30.g4 | [22...Qxa1+] [23.Bg1] Qxc3 24.Qg4 Kb8 [25.Qxg7] Qxg7 [26.Bc5] d2 27.Rf1 Rd8 28.Rd1 e3 29.Bxe3 [Qe5] 30.Bxh6 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.e4%20dxe4%204.f3%20exf3%205.Nxf3%20c5%206.Bd3%20cxd4%207.Ne4%20Nxe4%208.Bxe4%20Nc6%209.O-O%20Qb6%2010.Kh1%20e5%2011.Qe1%20Bd6%2012.Ng5%20Bd7%2013.a3%20O-O-O%2014.Nxf7%20Bc7%2015.Nxh8%20Rxh8%2016.Rf7%20h6%2017.c3%20a6%2018.Bf5%20Bxf5%2019.Rxf5%20d3%2020.Be3%20Qxb2%2021.h3%20e4%2022.Qh4%20Qxa1%2B%2023.Bg1%20Qxc3%2024.Qg4%20Kb8%2025.Qxg7%20Qxg7%2026.Bc5%20d2%2027.Rd5%20Rd8%2028.Rxd8%2B%20Nxd8%2029.Bd6%20Bxd6%2030.g4#43) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.e4%20dxe4%204.f3%20exf3%205.Nxf3%20c5%206.Bd3%20cxd4%207.Ne4%20Nxe4%208.Bxe4%20Nc6%209.O-O%20Qb6%2010.Kh1%20e5%2011.Qe1%20Bd6%2012.Ng5%20Bd7%2013.a3%20O-O-O%2014.Nxf7%20Bc7%2015.Nxh8%20Rxh8%2016.Rf7%20h6%2017.c3%20a6%2018.Bf5%20Bxf5%2019.Rxf5%20d3%2020.Be3%20Qxb2%2021.h3%20e4%2022.Qh4%20Qxa1%2B%2023.Bg1%20Qxc3%2024.Qg4%20Kb8%2025.Qxg7%20Qxg7%2026.Bc5%20d2%2027.Rf1%20Rd8%2028.Rd1%20e3%2029.Bxe3%20Qe5%2030.Bxh6#43) |

position 30 (`1rbq1rk1/5ppp/2np3b/p2Np3/1p2P2P/2PQ2P1/PPN2PB1/R4RK1 b - - 1 17`), split at ply 7: Bxd5 (56% there) vs Rb8 (44%)

| chosen | subpar |
|---|---|
| 17...bxc3 18.bxc3 Rb2 [19.Na3] Be6 [20.Nc4] [Bxd5] 21.exd5 Ne7 22.Nxb2 Qb6 23.Rab1 Qc5 24.c4 Rb8 25.Na4 | 17...bxc3 18.bxc3 Rb2 [19.Na3] Be6 [20.Nc4] Rb8 21.Rab1 [Rxb1] [22.Rxb1] [Bxd5] [23.exd5] Ne7 [24.Rb5] a4 [25.Ra5] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20e5%206.Ndb5%20d6%207.Bg5%20a6%208.Na3%20b5%209.Nd5%20Be7%2010.Bxf6%20Bxf6%2011.c3%20Bg5%2012.h4%20Bh6%2013.g3%20O-O%2014.Bg2%20Rb8%2015.Nc2%20a5%2016.O-O%20b4%2017.Qd3%20bxc3%2018.bxc3%20Rb2%2019.Na3%20Be6%2020.Nc4%20Bxd5%2021.exd5%20Ne7%2022.Nxb2%20Qb6%2023.Rab1%20Qc5%2024.c4%20Rb8%2025.Na4#33) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20e5%206.Ndb5%20d6%207.Bg5%20a6%208.Na3%20b5%209.Nd5%20Be7%2010.Bxf6%20Bxf6%2011.c3%20Bg5%2012.h4%20Bh6%2013.g3%20O-O%2014.Bg2%20Rb8%2015.Nc2%20a5%2016.O-O%20b4%2017.Qd3%20bxc3%2018.bxc3%20Rb2%2019.Na3%20Be6%2020.Nc4%20Rb8%2021.Rab1%20Rxb1%2022.Rxb1%20Bxd5%2023.exd5%20Ne7%2024.Rb5%20a4%2025.Ra5#33) |

#### W #6 (k = 0): latents 1640

position 39 (`r6r/bbp1k2p/p4N2/4p1p1/1P1p4/PQ3P2/2Pq1BPP/1K4n1 w - - 1 27`), split at ply 6: d3 (52% there) vs Qc1+ (48%)

| chosen | subpar |
|---|---|
| 27.Bg3 [Qd1+] 28.Kb2 [Ne2] 29.Bxe5 [d3] 30.cxd3 [Bd4+] 31.Bxd4 [Nxd4] 32.Qc4 [Qd2+] 33.Kb1 [Qd1+] 34.Kb2 Qd2+ | 27.Bg3 [Qd1+] 28.Kb2 [Ne2] 29.Bxe5 Qc1+ 30.Ka2 Nc3+ 31.Qxc3 [dxc3] 32.Ne4 Qxc2+ 33.Ka1 Qb2# |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20f6%203.Bc4%20Bc5%204.d3%20a6%205.Nc3%20b5%206.a3%20bxc4%207.dxc4%20Ba7%208.Rg1%20Nc6%209.Qd2%20Na5%2010.b4%20Nxc4%2011.Qd5%20Nb6%2012.Qa2%20Bb7%2013.Be3%20d5%2014.O-O-O%20d4%2015.Nh4%20g5%2016.Nf5%20Qd7%2017.f3%20Ne7%2018.Bf2%20Nxf5%2019.exf5%20Qxf5%2020.Ne2%20Na4%2021.Ng3%20Nc3%2022.Qb3%20Qf4%2B%2023.Rd2%20Ne2%2B%2024.Kb1%20Nxg1%2025.Nh5%20Qxd2%2026.Nxf6%2B%20Ke7%2027.Bg3%20Qd1%2B%2028.Kb2%20Ne2%2029.Bxe5%20d3%2030.cxd3%20Bd4%2B%2031.Bxd4%20Nxd4%2032.Qc4%20Qd2%2B%2033.Kb1%20Qd1%2B%2034.Kb2%20Qd2%2B#52) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20f6%203.Bc4%20Bc5%204.d3%20a6%205.Nc3%20b5%206.a3%20bxc4%207.dxc4%20Ba7%208.Rg1%20Nc6%209.Qd2%20Na5%2010.b4%20Nxc4%2011.Qd5%20Nb6%2012.Qa2%20Bb7%2013.Be3%20d5%2014.O-O-O%20d4%2015.Nh4%20g5%2016.Nf5%20Qd7%2017.f3%20Ne7%2018.Bf2%20Nxf5%2019.exf5%20Qxf5%2020.Ne2%20Na4%2021.Ng3%20Nc3%2022.Qb3%20Qf4%2B%2023.Rd2%20Ne2%2B%2024.Kb1%20Nxg1%2025.Nh5%20Qxd2%2026.Nxf6%2B%20Ke7%2027.Bg3%20Qd1%2B%2028.Kb2%20Ne2%2029.Bxe5%20Qc1%2B%2030.Ka2%20Nc3%2B%2031.Qxc3%20dxc3%2032.Ne4%20Qxc2%2B%2033.Ka1%20Qb2%23#52) |

position 43 (`1r1qk2r/p2b2pp/1p3n2/n3Qp2/P2Pp3/4PP2/3N2PP/R1B1KB1R b KQk - 1 17`), split at ply 12: Nxe4 (55% there) vs O-O (45%)

| chosen | subpar |
|---|---|
| 17...Kf7 18.Bc4+ Kg6 19.Qg3+ Kh6 20.fxe4 fxe4 21.Qh4+ Nh5 22.Qxd8 Rbxd8 [23.Nxe4] Nxc4 24.O-O Bf5 [25.Rxf5] | 17...Kf7 18.Bc4+ Kg6 19.Qg3+ Kh6 20.fxe4 fxe4 21.Qh4+ Nh5 22.Qxd8 Rbxd8 23.O-O Nxc4 24.Nxc4 Be6 25.Ne5 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20f6%203.c4%20e5%204.e3%20e4%205.Nfd2%20c6%206.Nc3%20Bb4%207.cxd5%20cxd5%208.f3%20f5%209.Qa4%2B%20Nc6%2010.a3%20Bxc3%2011.bxc3%20Bd7%2012.Qb3%20Rb8%2013.c4%20dxc4%2014.Qxc4%20Nf6%2015.a4%20Na5%2016.Qc5%20b6%2017.Qe5%2B%20Kf7%2018.Bc4%2B%20Kg6%2019.Qg3%2B%20Kh6%2020.fxe4%20fxe4%2021.Qh4%2B%20Nh5%2022.Qxd8%20Rbxd8%2023.Nxe4%20Nxc4%2024.O-O%20Bf5%2025.Rxf5#33) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20f6%203.c4%20e5%204.e3%20e4%205.Nfd2%20c6%206.Nc3%20Bb4%207.cxd5%20cxd5%208.f3%20f5%209.Qa4%2B%20Nc6%2010.a3%20Bxc3%2011.bxc3%20Bd7%2012.Qb3%20Rb8%2013.c4%20dxc4%2014.Qxc4%20Nf6%2015.a4%20Na5%2016.Qc5%20b6%2017.Qe5%2B%20Kf7%2018.Bc4%2B%20Kg6%2019.Qg3%2B%20Kh6%2020.fxe4%20fxe4%2021.Qh4%2B%20Nh5%2022.Qxd8%20Rbxd8%2023.O-O%20Nxc4%2024.Nxc4%20Be6%2025.Ne5#33) |

position 12 (`2k4r/1pb3p1/p1n4p/5R2/4p2Q/P1PpB2P/1q4P1/R6K b - - 1 22`), split at ply 6: Qxe4 (50% there) vs Qxg7 (44%)

| chosen | subpar |
|---|---|
| 22...Qxa1+ 23.Bg1 Qxc3 24.Qg4 Kb8 [25.Qxe4] d2 26.Rd5 Qc1 27.Rxd2 Qxd2 28.Bh2 Bxh2 29.Kxh2 Qd6+ 30.Kh1 | 22...Qxa1+ 23.Bg1 Qxc3 24.Qg4 Kb8 25.Qxg7 Qxg7 26.Rf7 Qxf7 27.Bh2 Bxh2 28.Kxh2 d2 29.Kg3 d1=Q 30.Kh4 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.e4%20dxe4%204.f3%20exf3%205.Nxf3%20c5%206.Bd3%20cxd4%207.Ne4%20Nxe4%208.Bxe4%20Nc6%209.O-O%20Qb6%2010.Kh1%20e5%2011.Qe1%20Bd6%2012.Ng5%20Bd7%2013.a3%20O-O-O%2014.Nxf7%20Bc7%2015.Nxh8%20Rxh8%2016.Rf7%20h6%2017.c3%20a6%2018.Bf5%20Bxf5%2019.Rxf5%20d3%2020.Be3%20Qxb2%2021.h3%20e4%2022.Qh4%20Qxa1%2B%2023.Bg1%20Qxc3%2024.Qg4%20Kb8%2025.Qxe4%20d2%2026.Rd5%20Qc1%2027.Rxd2%20Qxd2%2028.Bh2%20Bxh2%2029.Kxh2%20Qd6%2B%2030.Kh1#43) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.e4%20dxe4%204.f3%20exf3%205.Nxf3%20c5%206.Bd3%20cxd4%207.Ne4%20Nxe4%208.Bxe4%20Nc6%209.O-O%20Qb6%2010.Kh1%20e5%2011.Qe1%20Bd6%2012.Ng5%20Bd7%2013.a3%20O-O-O%2014.Nxf7%20Bc7%2015.Nxh8%20Rxh8%2016.Rf7%20h6%2017.c3%20a6%2018.Bf5%20Bxf5%2019.Rxf5%20d3%2020.Be3%20Qxb2%2021.h3%20e4%2022.Qh4%20Qxa1%2B%2023.Bg1%20Qxc3%2024.Qg4%20Kb8%2025.Qxg7%20Qxg7%2026.Rf7%20Qxf7%2027.Bh2%20Bxh2%2028.Kxh2%20d2%2029.Kg3%20d1%3DQ%2030.Kh4#43) |

#### W #7 (k = 0): latents 619

position 26 (`r1b1r1k1/2p3bp/2p2pq1/2Np4/p5P1/P1Q1B3/1PP2P1P/1K1R2R1 w - - 3 24`), split at ply 7: Rg3 (52% there) vs Rxg7+ (48%)

| chosen | subpar |
|---|---|
| 24.h4 Qf7 25.g5 fxg5 26.Rxg5 h6 [27.Rg3] Kh8 [28.Bxh6] [Bxc3] 29.Rxc3 Qxf2 30.Nd3 [Qxh4] [31.Bd2] Bg4 | 24.h4 Qf7 25.g5 fxg5 26.Rxg5 h6 27.Rxg7+ Qxg7 28.Qxg7+ [Kxg7] 29.Rg1+ [Kh7] 30.Nd3 Bf5 [31.Nf4] Rg8 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.h4%20Qf7%2025.g5%20fxg5%2026.Rxg5%20h6%2027.Rg3%20Kh8%2028.Bxh6%20Bxc3%2029.Rxc3%20Qxf2%2030.Nd3%20Qxh4%2031.Bd2%20Bg4#46) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.h4%20Qf7%2025.g5%20fxg5%2026.Rxg5%20h6%2027.Rxg7%2B%20Qxg7%2028.Qxg7%2B%20Kxg7%2029.Rg1%2B%20Kh7%2030.Nd3%20Bf5%2031.Nf4%20Rg8#46) |

position 34 (`r2qk2r/1pp1bppp/2n1p3/1p6/3PR3/P1P2N2/5PPP/R2Q2K1 b kq - 0 14`), split at ply 4: Qc2 (50% there) vs Qxd5 (48%)

| chosen | subpar |
|---|---|
| 14...O-O 15.Qb3 Qd5 [16.Qc2] Bxa3 17.Rh4 h6 18.Ne5 Nxe5 19.dxe5 Qxe5 20.Rh3 Bd6 [21.g3] Rxa1+ 22.Kg2 | 14...O-O 15.Qb3 Qd5 16.Qxd5 exd5 [17.Re3] Rfe8 [18.Rb1] Rxa3 19.Rxb5 Ra1+ 20.Re1 Rxe1+ 21.Nxe1 b6 22.Rxd5 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20O-O%2015.Qb3%20Qd5%2016.Qc2%20Bxa3%2017.Rh4%20h6%2018.Ne5%20Nxe5%2019.dxe5%20Qxe5%2020.Rh3%20Bd6%2021.g3%20Rxa1%2B%2022.Kg2#27) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20O-O%2015.Qb3%20Qd5%2016.Qxd5%20exd5%2017.Re3%20Rfe8%2018.Rb1%20Rxa3%2019.Rxb5%20Ra1%2B%2020.Re1%20Rxe1%2B%2021.Nxe1%20b6%2022.Rxd5#27) |

position 25 (`1r3r2/pb4kp/1p4p1/2pnP3/4B3/2P4P/PP1N2P1/R4RK1 w - - 3 21`), split at ply 9: Nxe4 (53% there) vs Kxe3 (47%)

| chosen | subpar |
|---|---|
| 21.Rxf8 [Rxf8] 22.Rf1 Rxf1+ 23.Kxf1 Ne3+ 24.Ke2 [Bxe4] [25.Nxe4] Nxg2 26.Kf3 [Nh4+] 27.Kg4 [Nf5] 28.Nd6 [Nxd6] | 21.Rxf8 [Rxf8] 22.Rf1 Rxf1+ 23.Kxf1 Ne3+ 24.Ke2 [Bxe4] 25.Kxe3 [Bxg2] 26.h4 Kf7 27.Ne4 Ke6 28.Kf4 Bxe4 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.Rxf8%20Rxf8%2022.Rf1%20Rxf1%2B%2023.Kxf1%20Ne3%2B%2024.Ke2%20Bxe4%2025.Nxe4%20Nxg2%2026.Kf3%20Nh4%2B%2027.Kg4%20Nf5%2028.Nd6%20Nxd6#40) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.Rxf8%20Rxf8%2022.Rf1%20Rxf1%2B%2023.Kxf1%20Ne3%2B%2024.Ke2%20Bxe4%2025.Kxe3%20Bxg2%2026.h4%20Kf7%2027.Ne4%20Ke6%2028.Kf4%20Bxe4#40) |

#### W #8 (k = 0): latents 2179

position 46 (`1r1q1r2/pb3pkp/1n1p1Np1/2p5/1p4n1/3P4/PPPQ2BP/1RB2RK1 w - - 0 22`), split at ply 4: Kg8 (52% there) vs Kh8 (48%)

| chosen | subpar |
|---|---|
| 22.Nxg4 [Bxg2] 23.Qh6+ [Kg8] 24.Nf6+ [Kh8] 25.Qxh7# | 22.Nxg4 [Bxg2] 23.Qh6+ Kh8 [24.Kxg2] [Nd5] 25.Bg5 [Qd7] 26.Nf6 [Nxf6] 27.Bxf6+ [Kg8] 28.Qg7# |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nc3%20Nc6%203.g3%20g6%204.Bg2%20Bg7%205.Nge2%20d6%206.O-O%20e6%207.f4%20Nge7%208.g4%20O-O%209.Ng3%20Rb8%2010.d3%20b5%2011.Rb1%20b4%2012.Nce2%20Bb7%2013.f5%20Nc8%2014.Nf4%20exf5%2015.exf5%20Nb6%2016.Ne4%20Ne5%2017.f6%20Bxf6%2018.Nh5%20Bh8%2019.Nhf6%2B%20Bxf6%2020.Nxf6%2B%20Kg7%2021.Qd2%20Nxg4%2022.Nxg4%20Bxg2%2023.Qh6%2B%20Kg8%2024.Nf6%2B%20Kh8%2025.Qxh7%23#42) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nc3%20Nc6%203.g3%20g6%204.Bg2%20Bg7%205.Nge2%20d6%206.O-O%20e6%207.f4%20Nge7%208.g4%20O-O%209.Ng3%20Rb8%2010.d3%20b5%2011.Rb1%20b4%2012.Nce2%20Bb7%2013.f5%20Nc8%2014.Nf4%20exf5%2015.exf5%20Nb6%2016.Ne4%20Ne5%2017.f6%20Bxf6%2018.Nh5%20Bh8%2019.Nhf6%2B%20Bxf6%2020.Nxf6%2B%20Kg7%2021.Qd2%20Nxg4%2022.Nxg4%20Bxg2%2023.Qh6%2B%20Kh8%2024.Kxg2%20Nd5%2025.Bg5%20Qd7%2026.Nf6%20Nxf6%2027.Bxf6%2B%20Kg8%2028.Qg7%23#42) |

position 25 (`1r3r2/pb4kp/1p4p1/2pnP3/4B3/2P4P/PP1N2P1/R4RK1 w - - 3 21`), split at ply 3: Bxb7 (53% there) vs Rxf8 (47%)

| chosen | subpar |
|---|---|
| [21.Rad1] Ne3 [22.Bxb7] [Nxd1] 23.Rxd1 [Rxb7] 24.Ne4 [Re7] 25.Nd6 [Rxe5] 26.Nc4 [Re2] 27.Rd7+ [Rf7] 28.Rxf7+ Kxf7 | [21.Rad1] Ne3 22.Rxf8 [Rxf8] 23.Re1 [Bxe4] 24.Nxe4 [Nc2] 25.Re2 [Na1] 26.e6 Re8 27.Ng5 Kf6 28.Nxh7+ Ke7 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.Rad1%20Ne3%2022.Bxb7%20Nxd1%2023.Rxd1%20Rxb7%2024.Ne4%20Re7%2025.Nd6%20Rxe5%2026.Nc4%20Re2%2027.Rd7%2B%20Rf7%2028.Rxf7%2B%20Kxf7#40) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.Rad1%20Ne3%2022.Rxf8%20Rxf8%2023.Re1%20Bxe4%2024.Nxe4%20Nc2%2025.Re2%20Na1%2026.e6%20Re8%2027.Ng5%20Kf6%2028.Nxh7%2B%20Ke7#40) |

position 6 (`r1b2rk1/1pp1q1pp/2p1np2/p3p3/P1N1P3/1P1P1N1P/2P2PP1/R2Q1RK1 b - - 2 14`), split at ply 6: Kh2 (54% there) vs Kg2 (46%)

| chosen | subpar |
|---|---|
| 14...Nf4 15.Qd2 Bxh3 16.gxh3 Nxh3+ [17.Kh2] Nf4 18.Rg1 Qe6 19.Nxa5 Qh3# | 14...Nf4 15.Qd2 Bxh3 16.gxh3 Nxh3+ 17.Kg2 Nf4+ 18.Kg3 Qe6 19.Rh1 Qg4+ 20.Kh2 Qg2# |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20a6%204.Ba4%20Nf6%205.Bxc6%20dxc6%206.d3%20Nd7%207.O-O%20Bc5%208.Be3%20Qe7%209.Bxc5%20Nxc5%2010.Nbd2%20O-O%2011.a4%20a5%2012.b3%20f6%2013.h3%20Ne6%2014.Nc4%20Nf4%2015.Qd2%20Bxh3%2016.gxh3%20Nxh3%2B%2017.Kh2%20Nf4%2018.Rg1%20Qe6%2019.Nxa5%20Qh3%23#27) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20a6%204.Ba4%20Nf6%205.Bxc6%20dxc6%206.d3%20Nd7%207.O-O%20Bc5%208.Be3%20Qe7%209.Bxc5%20Nxc5%2010.Nbd2%20O-O%2011.a4%20a5%2012.b3%20f6%2013.h3%20Ne6%2014.Nc4%20Nf4%2015.Qd2%20Bxh3%2016.gxh3%20Nxh3%2B%2017.Kg2%20Nf4%2B%2018.Kg3%20Qe6%2019.Rh1%20Qg4%2B%2020.Kh2%20Qg2%23#27) |

#### W #9 (k = 0): latents 19

position 24 (`3r2k1/pp4p1/2n1b2p/8/3p2q1/8/PPQB1PP1/4RRK1 w - - 2 25`), split at ply 6: d3 (49% there) vs Bf5 (48%)

| chosen | subpar |
|---|---|
| 25.Re4 Qg6 26.Rfe1 [Bh3] 27.g3 [d3] 28.Qc4+ Kh7 29.R1e3 Bf5 30.Rh4 [Ne5] 31.Rxe5 Rc8 32.Qd4 Rc2 | 25.Re4 Qg6 26.Rfe1 [Bh3] 27.g3 Bf5 28.Re8+ Rxe8 29.Rxe8+ Qxe8 30.Qxf5 Qe2 31.Qc8+ Kh7 32.Qf5+ Kg8 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e6%202.d4%20d5%203.Nd2%20Nf6%204.e5%20Nfd7%205.Bd3%20c5%206.c3%20Nc6%207.Ne2%20cxd4%208.cxd4%20f6%209.exf6%20Qxf6%2010.Nf3%20h6%2011.O-O%20Bd6%2012.Ng3%20O-O%2013.Bd2%20e5%2014.dxe5%20Ndxe5%2015.Nxe5%20Bxe5%2016.Qc2%20Be6%2017.Rae1%20Rae8%2018.Nh5%20Bxh2%2B%2019.Kxh2%20Qh4%2B%2020.Kg1%20Qxh5%2021.Bg6%20Qg4%2022.Bxe8%20Rxe8%2023.Bc3%20d4%2024.Bd2%20Rd8%2025.Re4%20Qg6%2026.Rfe1%20Bh3%2027.g3%20d3%2028.Qc4%2B%20Kh7%2029.R1e3%20Bf5%2030.Rh4%20Ne5%2031.Rxe5%20Rc8%2032.Qd4%20Rc2#48) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e6%202.d4%20d5%203.Nd2%20Nf6%204.e5%20Nfd7%205.Bd3%20c5%206.c3%20Nc6%207.Ne2%20cxd4%208.cxd4%20f6%209.exf6%20Qxf6%2010.Nf3%20h6%2011.O-O%20Bd6%2012.Ng3%20O-O%2013.Bd2%20e5%2014.dxe5%20Ndxe5%2015.Nxe5%20Bxe5%2016.Qc2%20Be6%2017.Rae1%20Rae8%2018.Nh5%20Bxh2%2B%2019.Kxh2%20Qh4%2B%2020.Kg1%20Qxh5%2021.Bg6%20Qg4%2022.Bxe8%20Rxe8%2023.Bc3%20d4%2024.Bd2%20Rd8%2025.Re4%20Qg6%2026.Rfe1%20Bh3%2027.g3%20Bf5%2028.Re8%2B%20Rxe8%2029.Rxe8%2B%20Qxe8%2030.Qxf5%20Qe2%2031.Qc8%2B%20Kh7%2032.Qf5%2B%20Kg8#48) |

position 20 (`r3k1nr/1p1n4/1p1bp1pp/3p1p2/3P4/2P2N2/PP1N1PPP/R1B2RK1 b kq - 1 14`), split at ply 15: Re8 (56% there) vs Ne4 (44%)

| chosen | subpar |
|---|---|
| 14...g5 15.Re1 Ke7 16.Nb3 [g4] [17.Nh4] Ngf6 [18.Ng6+] [Kf7] [19.Nxh8+] [Kg7] [20.Rxe6] [Kxh8] 21.Rxd6 [Re8] [22.Bxh6] | 14...g5 15.Re1 Ke7 16.Nb3 [g4] [17.Nh4] Ngf6 [18.Ng6+] [Kf7] [19.Nxh8+] [Kg7] [20.Rxe6] [Kxh8] 21.Rxd6 Ne4 22.Rxh6+ |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20e6%202.Bf4%20c5%203.e3%20cxd4%204.exd4%20Qb6%205.Bc1%20d5%206.Nf3%20Bb4%2B%207.c3%20Bd6%208.Bd3%20g6%209.Nbd2%20f5%2010.Qb3%20h6%2011.Qxb6%20axb6%2012.Bb5%2B%20Bd7%2013.Bxd7%2B%20Nxd7%2014.O-O%20g5%2015.Re1%20Ke7%2016.Nb3%20g4%2017.Nh4%20Ngf6%2018.Ng6%2B%20Kf7%2019.Nxh8%2B%20Kg7%2020.Rxe6%20Kxh8%2021.Rxd6%20Re8%2022.Bxh6#27) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20e6%202.Bf4%20c5%203.e3%20cxd4%204.exd4%20Qb6%205.Bc1%20d5%206.Nf3%20Bb4%2B%207.c3%20Bd6%208.Bd3%20g6%209.Nbd2%20f5%2010.Qb3%20h6%2011.Qxb6%20axb6%2012.Bb5%2B%20Bd7%2013.Bxd7%2B%20Nxd7%2014.O-O%20g5%2015.Re1%20Ke7%2016.Nb3%20g4%2017.Nh4%20Ngf6%2018.Ng6%2B%20Kf7%2019.Nxh8%2B%20Kg7%2020.Rxe6%20Kxh8%2021.Rxd6%20Ne4%2022.Rxh6%2B#27) |

position 3 (`2kr1b1r/ppp1pppp/5n2/8/3n1q2/1P1P1B1P/P1P2PP1/RNBQ1K1R b - - 0 11`), split at ply 6: c3 (53% there) vs Nd2 (44%)

| chosen | subpar |
|---|---|
| [11...Qe5] 12.Bb2 e6 [13.Bxd4] Qxd4 [14.c3] Qxd3+ [15.Qxd3] Rxd3 [16.Ke2] Rd6 17.Rd1 Be7 [18.Rxd6] Bxd6 19.Nd2 | [11...Qe5] 12.Bb2 e6 [13.Bxd4] Qxd4 14.Nd2 Bc5 15.Qe2 [Qxa1+] [16.Qe1] [Qxa2] 17.Ke2 [Qxc2] [18.Be4] Nxe4 19.dxe4 |
| [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nc6%202.e4%20d5%203.exd5%20Qxd5%204.b3%20Bg4%205.Bc4%20Qe4%2B%206.Kf1%20Nd4%207.Bd3%20Qf4%208.Be2%20O-O-O%209.h3%20Bxf3%2010.Bxf3%20Nf6%2011.d3%20Qe5%2012.Bb2%20e6%2013.Bxd4%20Qxd4%2014.c3%20Qxd3%2B%2015.Qxd3%20Rxd3%2016.Ke2%20Rd6%2017.Rd1%20Be7%2018.Rxd6%20Bxd6%2019.Nd2#21) | [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nc6%202.e4%20d5%203.exd5%20Qxd5%204.b3%20Bg4%205.Bc4%20Qe4%2B%206.Kf1%20Nd4%207.Bd3%20Qf4%208.Be2%20O-O-O%209.h3%20Bxf3%2010.Bxf3%20Nf6%2011.d3%20Qe5%2012.Bb2%20e6%2013.Bxd4%20Qxd4%2014.Nd2%20Bc5%2015.Qe2%20Qxa1%2B%2016.Qe1%20Qxa2%2017.Ke2%20Qxc2%2018.Be4%20Nxe4%2019.dxe4#21) |

#### W #10 (k = 0): latents 705

position 0 (`2kr2r1/ppp5/2n1RbNp/2q2p1P/3p4/2PQ1P1B/PPKN3P/6R1 b - - 0 20`), split at ply 15: Qd5+ (52% there) vs Na5+ (48%)

| chosen | subpar |
|---|---|
| [20...dxc3] 21.bxc3 [Rxd3] 22.Kxd3 Qxg1 23.Bxf5 [Rd8+] 24.Kc2 [Qxh2] 25.Rxf6+ [Kb8] 26.Rf7 [Qxd2+] 27.Kb3 [Qd5+] 28.Kc2 | [20...dxc3] 21.bxc3 [Rxd3] 22.Kxd3 Qxg1 23.Bxf5 [Rd8+] 24.Kc2 [Qxh2] 25.Rxf6+ [Kb8] 26.Rf7 [Qxd2+] 27.Kb3 Na5+ 28.Kb4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.bxc3%20Rxd3%2022.Kxd3%20Qxg1%2023.Bxf5%20Rd8%2B%2024.Kc2%20Qxh2%2025.Rxf6%2B%20Kb8%2026.Rf7%20Qxd2%2B%2027.Kb3%20Qd5%2B%2028.Kc2#39) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.bxc3%20Rxd3%2022.Kxd3%20Qxg1%2023.Bxf5%20Rd8%2B%2024.Kc2%20Qxh2%2025.Rxf6%2B%20Kb8%2026.Rf7%20Qxd2%2B%2027.Kb3%20Na5%2B%2028.Kb4#39) |

position 3 (`2kr1b1r/ppp1pppp/5n2/8/3n1q2/1P1P1B1P/P1P2PP1/RNBQ1K1R b - - 0 11`), split at ply 3: Nxf3 (50% there) vs e6 (47%)

| chosen | subpar |
|---|---|
| [11...Qe5] 12.g3 [Nxf3] 13.Qxf3 Qxa1 14.Kg2 Qxb1 15.Bf4 Qxc2 16.Rc1 [Qxd3] 17.Rxc7+ [Kb8] 18.Qxb7# | [11...Qe5] 12.g3 e6 13.Kg2 Bd6 14.Bf4 Qc5 15.Bxd6 Rxd6 16.Nd2 [Nxc2] 17.Rc1 [Rxd3] 18.Rxc2 Qf5 19.g4 |
| [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nc6%202.e4%20d5%203.exd5%20Qxd5%204.b3%20Bg4%205.Bc4%20Qe4%2B%206.Kf1%20Nd4%207.Bd3%20Qf4%208.Be2%20O-O-O%209.h3%20Bxf3%2010.Bxf3%20Nf6%2011.d3%20Qe5%2012.g3%20Nxf3%2013.Qxf3%20Qxa1%2014.Kg2%20Qxb1%2015.Bf4%20Qxc2%2016.Rc1%20Qxd3%2017.Rxc7%2B%20Kb8%2018.Qxb7%23#21) | [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nc6%202.e4%20d5%203.exd5%20Qxd5%204.b3%20Bg4%205.Bc4%20Qe4%2B%206.Kf1%20Nd4%207.Bd3%20Qf4%208.Be2%20O-O-O%209.h3%20Bxf3%2010.Bxf3%20Nf6%2011.d3%20Qe5%2012.g3%20e6%2013.Kg2%20Bd6%2014.Bf4%20Qc5%2015.Bxd6%20Rxd6%2016.Nd2%20Nxc2%2017.Rc1%20Rxd3%2018.Rxc2%20Qf5%2019.g4#21) |

position 45 (`r4rk1/pp4pp/1b3q2/1P1pRp2/P7/1QP3P1/5P1P/R5K1 b - - 2 26`), split at ply 15: Bxf2 (54% there) vs Qg4+ (46%)

| chosen | subpar |
|---|---|
| [26...Qxe5] 27.a5 [Bc5] 28.b6 [axb6] 29.axb6 Rxa1+ 30.Kg2 Qe4+ 31.Kh3 Qg4+ 32.Kg2 Qe4+ 33.Kh3 [Bxf2] 34.c4 | [26...Qxe5] 27.a5 [Bc5] 28.b6 [axb6] 29.axb6 Rxa1+ 30.Kg2 Qe4+ 31.Kh3 Qg4+ 32.Kg2 Qe4+ 33.Kh3 Qg4+ 34.Kg2 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.e5%20c5%204.dxc5%20Nc6%205.Bf4%20e6%206.Bb5%20Bd7%207.Na3%20Bxc5%208.Nf3%20Nge7%209.O-O%20Ng6%2010.Bg5%20f6%2011.Bh4%20Nxh4%2012.Nxh4%20Nxe5%2013.Bxd7%2B%20Qxd7%2014.c3%20O-O%2015.b4%20Bb6%2016.b5%20Qe7%2017.Nc2%20Ng4%2018.Nd4%20Ne5%2019.a4%20Nc4%2020.Re1%20f5%2021.Rxe6%20Qxh4%2022.g3%20Qg5%2023.Nf3%20Qd8%2024.Ne5%20Nxe5%2025.Rxe5%20Qf6%2026.Qb3%20Qxe5%2027.a5%20Bc5%2028.b6%20axb6%2029.axb6%20Rxa1%2B%2030.Kg2%20Qe4%2B%2031.Kh3%20Qg4%2B%2032.Kg2%20Qe4%2B%2033.Kh3%20Bxf2%2034.c4#51) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.e5%20c5%204.dxc5%20Nc6%205.Bf4%20e6%206.Bb5%20Bd7%207.Na3%20Bxc5%208.Nf3%20Nge7%209.O-O%20Ng6%2010.Bg5%20f6%2011.Bh4%20Nxh4%2012.Nxh4%20Nxe5%2013.Bxd7%2B%20Qxd7%2014.c3%20O-O%2015.b4%20Bb6%2016.b5%20Qe7%2017.Nc2%20Ng4%2018.Nd4%20Ne5%2019.a4%20Nc4%2020.Re1%20f5%2021.Rxe6%20Qxh4%2022.g3%20Qg5%2023.Nf3%20Qd8%2024.Ne5%20Nxe5%2025.Rxe5%20Qf6%2026.Qb3%20Qxe5%2027.a5%20Bc5%2028.b6%20axb6%2029.axb6%20Rxa1%2B%2030.Kg2%20Qe4%2B%2031.Kh3%20Qg4%2B%2032.Kg2%20Qe4%2B%2033.Kh3%20Qg4%2B%2034.Kg2#51) |

