# Dynamic concepts with a persistence window

Per model, at 50 positions (1024 rollouts of 16 plies, T = 0.4, the model both colours): a latent on at a ply when z > 0.5 x mu_j. Pairs: at each branching point the most-played move against every move with >= 2% of that point's weight, each by its most frequent line, <= 50 per position. LP: min |v|_1 + 2.0 xi s.t. v . (z^c_tau - z^s_tau) >= 1 - xi for tau = t..t+k. Families: Jaccard >= 0.5 of supports with a family's core, within one half (25 / 25 positions by game); recurrence: the share of the other half's pairs (same k) where the family's mean v (|v|_1 = 1) gives >= 0.5 on every ply of the window; null: 200 random v's per family on rate-matched latents (firing-rate deciles). Persistence: plies in a row from the split with v . d >= 0.5, median over the other half's k = 0 pairs where it is on at the split.

## S

| k | pairs | nonzero v | families | held-out recurrence: median / 90% / max | null 95th: median | null (every draw): 90% / 99% | families above their null 95th (chance: 5%) |
|---|---|---|---|---|---|---|---|
| 0 | 2500 | 100% | 812 | 0.2% / 1.5% / 16.2% | 0.6% | 1.1% / 10.6% | 52 (6%) |
| 2 | 2500 | 56% | 905 | 0.0% / 0.3% / 1.0% | 0.0% | 0.0% / 0.2% | 153 (17%) |
| 4 | 2500 | 27% | 591 | 0.0% / 0.1% / 0.9% | 0.0% | 0.0% / 0.1% | 64 (11%) |
| 6 | 2500 | 16% | 372 | 0.0% / 0.0% / 0.6% | 0.0% | 0.0% / 0.0% | 36 (10%) |

### S: the top 20 families by held-out recurrence

| # | k | latents (weight) | found in | held out on | recurrence | null 95th | persistence (pairs on at split) | positions found |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 2234 (1.00) | B (9 v's) | A | 16.2% | 8.6% | 1.0 (202) | 12, 13, 15, 17, 39, 40, 47, 48 |
| 2 | 0 | 3356 (1.00) | B (1 v's) | A | 15.7% | 5.4% | 1.0 (196) | 30 |
| 3 | 0 | 52 (1.00) | A (161 v's) | B | 15.2% | 3.1% | 1.0 (190) | 0, 3, 5, 6, 7, 9, 11, 16, 18, 19, 20, 24 ... |
| 4 | 0 | 3714 (1.00) | B (1 v's) | A | 15.1% | 3.0% | 1.0 (189) | 30 |
| 5 | 0 | 3356 (1.00) | A (4 v's) | B | 14.8% | 2.2% | 1.0 (185) | 3, 7, 26, 49 |
| 6 | 0 | 2512 (1.00) | B (4 v's) | A | 14.2% | 2.9% | 1.0 (177) | 13, 15, 42, 44 |
| 7 | 0 | 3718 (1.00) | B (4 v's) | A | 14.1% | 2.8% | 1.0 (176) | 22, 42, 43, 44 |
| 8 | 0 | 5410 (1.00) | B (1 v's) | A | 13.8% | 2.4% | 1.0 (173) | 47 |
| 9 | 0 | 689 (1.00) | A (47 v's) | B | 13.8% | 3.5% | 1.0 (172) | 0, 3, 5, 6, 7, 11, 16, 18, 19, 20, 24, 25 ... |
| 10 | 0 | 2234 (1.00) | A (16 v's) | B | 13.8% | 3.4% | 1.0 (172) | 5, 6, 7, 11, 16, 18, 20, 24, 25, 29, 45 |
| 11 | 0 | 5410 (1.00) | A (1 v's) | B | 13.6% | 4.0% | 1.0 (170) | 19 |
| 12 | 0 | 5111 (1.00) | A (1 v's) | B | 13.5% | 3.5% | 1.0 (169) | 37 |
| 13 | 0 | 52 (1.00) | B (182 v's) | A | 13.5% | 3.0% | 1.0 (169) | 1, 2, 4, 8, 10, 12, 13, 14, 15, 17, 21, 22 ... |
| 14 | 0 | 2512 (1.00) | A (3 v's) | B | 13.1% | 2.6% | 1.0 (164) | 9, 49 |
| 15 | 0 | 4312 (1.00) | A (3 v's) | B | 13.0% | 4.6% | 1.0 (162) | 3, 18, 37 |
| 16 | 0 | 5080 (1.00) | B (1 v's) | A | 13.0% | 3.0% | 1.0 (162) | 39 |
| 17 | 0 | 6341 (1.00) | A (1 v's) | B | 12.5% | 9.3% | 1.0 (156) | 38 |
| 18 | 0 | 689 (1.00) | B (49 v's) | A | 12.2% | 6.6% | 1.0 (152) | 4, 8, 10, 12, 13, 14, 15, 17, 21, 23, 27, 32 ... |
| 19 | 0 | 2095 (1.00) | A (4 v's) | B | 12.1% | 3.3% | 1.0 (151) | 24, 26, 31, 38 |
| 20 | 0 | 4449 (1.00) | B (1 v's) | A | 11.6% | 3.8% | 1.0 (145) | 32 |

#### S #1 (k = 0): latents 2234

position 5 (`r3kbnr/pbpn2pp/1p2q3/1Q2p1B1/4P3/2N2N2/PPP3PP/2KR1B1R b kq - 2 11`), split at ply 7: Rc8 (51% there) vs Bxd5 (49%)

| chosen | subpar |
|---|---|
| 11...a6 12.Qa4 b5 13.Qa5 [Bd6] 14.Nd5 [Rc8] 15.a4 [c6] 16.Nb6 Nxb6 [17.Qxb6] [Qd7] 18.Nxe5 Bxe5 [19.Rxd7] | 11...a6 12.Qa4 b5 13.Qa5 [Bd6] 14.Nd5 Bxd5 15.exd5 Qf5 16.Bd3 Qg4 17.h3 Qxg2 18.Rhg1 Qxf3 19.Rdf1 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Nf3%20d6%204.Qe2%20Qe7%205.d3%20b6%206.Nc3%20Bb7%207.fxe5%20dxe5%208.Bg5%20Qe6%209.O-O-O%20fxe4%2010.dxe4%20Nd7%2011.Qb5%20a6%2012.Qa4%20b5%2013.Qa5%20Bd6%2014.Nd5%20Rc8%2015.a4%20c6%2016.Nb6%20Nxb6%2017.Qxb6%20Qd7%2018.Nxe5%20Bxe5%2019.Rxd7#21) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Nf3%20d6%204.Qe2%20Qe7%205.d3%20b6%206.Nc3%20Bb7%207.fxe5%20dxe5%208.Bg5%20Qe6%209.O-O-O%20fxe4%2010.dxe4%20Nd7%2011.Qb5%20a6%2012.Qa4%20b5%2013.Qa5%20Bd6%2014.Nd5%20Bxd5%2015.exd5%20Qf5%2016.Bd3%20Qg4%2017.h3%20Qxg2%2018.Rhg1%20Qxf3%2019.Rdf1#21) |

position 45 (`r4rk1/pp4pp/1b3q2/1P1pRp2/P7/1QP3P1/5P1P/R5K1 b - - 2 26`), split at ply 2: Rae1 (50% there) vs Rxd5 (49%)

| chosen | subpar |
|---|---|
| 26...Rad8 [27.Rae1] [Kh8] [28.Kg2] f4 29.f3 fxg3 [30.hxg3] [Qxf3+] 31.Kh3 Qh5+ 32.Kg2 Rf2+ 33.Kg1 [Qh2#] | 26...Rad8 27.Rxd5 [Kh8] 28.Rad1 Rxd5 [29.Rxd5] f4 30.Qc2 fxg3 31.hxg3 Qf3 32.Rd2 [Qxg3+] [33.Kf1] Qh3+ [34.Kg1] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.e5%20c5%204.dxc5%20Nc6%205.Bf4%20e6%206.Bb5%20Bd7%207.Na3%20Bxc5%208.Nf3%20Nge7%209.O-O%20Ng6%2010.Bg5%20f6%2011.Bh4%20Nxh4%2012.Nxh4%20Nxe5%2013.Bxd7%2B%20Qxd7%2014.c3%20O-O%2015.b4%20Bb6%2016.b5%20Qe7%2017.Nc2%20Ng4%2018.Nd4%20Ne5%2019.a4%20Nc4%2020.Re1%20f5%2021.Rxe6%20Qxh4%2022.g3%20Qg5%2023.Nf3%20Qd8%2024.Ne5%20Nxe5%2025.Rxe5%20Qf6%2026.Qb3%20Rad8%2027.Rae1%20Kh8%2028.Kg2%20f4%2029.f3%20fxg3%2030.hxg3%20Qxf3%2B%2031.Kh3%20Qh5%2B%2032.Kg2%20Rf2%2B%2033.Kg1%20Qh2%23#51) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.e5%20c5%204.dxc5%20Nc6%205.Bf4%20e6%206.Bb5%20Bd7%207.Na3%20Bxc5%208.Nf3%20Nge7%209.O-O%20Ng6%2010.Bg5%20f6%2011.Bh4%20Nxh4%2012.Nxh4%20Nxe5%2013.Bxd7%2B%20Qxd7%2014.c3%20O-O%2015.b4%20Bb6%2016.b5%20Qe7%2017.Nc2%20Ng4%2018.Nd4%20Ne5%2019.a4%20Nc4%2020.Re1%20f5%2021.Rxe6%20Qxh4%2022.g3%20Qg5%2023.Nf3%20Qd8%2024.Ne5%20Nxe5%2025.Rxe5%20Qf6%2026.Qb3%20Rad8%2027.Rxd5%20Kh8%2028.Rad1%20Rxd5%2029.Rxd5%20f4%2030.Qc2%20fxg3%2031.hxg3%20Qf3%2032.Rd2%20Qxg3%2B%2033.Kf1%20Qh3%2B%2034.Kg1#51) |

position 20 (`r3k1nr/1p1n4/1p1bp1pp/3p1p2/3P4/2P2N2/PP1N1PPP/R1B2RK1 b kq - 1 14`), split at ply 11: Rhc8 (51% there) vs Bxe3 (49%)

| chosen | subpar |
|---|---|
| 14...g5 [15.Re1] [Kf7] 16.Ne5+ [Nxe5] 17.dxe5 [Bc5] 18.Nb3 [Ne7] 19.Be3 [Rhc8] 20.a3 Bxe3 21.Rxe3 [f4] 22.Re2 | 14...g5 [15.Re1] [Kf7] 16.Ne5+ [Nxe5] 17.dxe5 [Bc5] 18.Nb3 [Ne7] 19.Be3 Bxe3 20.Rxe3 [Nc6] [21.a3] [f4] 22.Re2 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20e6%202.Bf4%20c5%203.e3%20cxd4%204.exd4%20Qb6%205.Bc1%20d5%206.Nf3%20Bb4%2B%207.c3%20Bd6%208.Bd3%20g6%209.Nbd2%20f5%2010.Qb3%20h6%2011.Qxb6%20axb6%2012.Bb5%2B%20Bd7%2013.Bxd7%2B%20Nxd7%2014.O-O%20g5%2015.Re1%20Kf7%2016.Ne5%2B%20Nxe5%2017.dxe5%20Bc5%2018.Nb3%20Ne7%2019.Be3%20Rhc8%2020.a3%20Bxe3%2021.Rxe3%20f4%2022.Re2#27) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20e6%202.Bf4%20c5%203.e3%20cxd4%204.exd4%20Qb6%205.Bc1%20d5%206.Nf3%20Bb4%2B%207.c3%20Bd6%208.Bd3%20g6%209.Nbd2%20f5%2010.Qb3%20h6%2011.Qxb6%20axb6%2012.Bb5%2B%20Bd7%2013.Bxd7%2B%20Nxd7%2014.O-O%20g5%2015.Re1%20Kf7%2016.Ne5%2B%20Nxe5%2017.dxe5%20Bc5%2018.Nb3%20Ne7%2019.Be3%20Bxe3%2020.Rxe3%20Nc6%2021.a3%20f4%2022.Re2#27) |

#### S #2 (k = 0): latents 3356

position 18 (`r1bq1rk1/pp3ppp/3b1n2/4N3/2BppP2/4B3/PPP3PP/R2Q1RK1 w - - 0 12`), split at ply 8: Bxd4 (51% there) vs Be6 (49%)

| chosen | subpar |
|---|---|
| 12.Bxd4 [Qc7] 13.Bb3 [Bc5] [14.c3] Rd8 15.Kh1 [Bxd4] 16.cxd4 Be6 17.Rc1 Qb6 18.Bxe6 Qxe6 19.Rc7 Nd5 | 12.Bxd4 [Qc7] 13.Bb3 [Bc5] [14.c3] Rd8 15.Kh1 Be6 16.Bxe6 fxe6 17.Qb3 [Bxd4] 18.Qxe6+ [Kf8] 19.cxd4 Rxd4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nf6%203.Nxe5%20Nxe4%204.d4%20d5%205.Bd3%20Nd7%206.O-O%20Bd6%207.f4%20O-O%208.Nc3%20Ndf6%209.Nxe4%20dxe4%2010.Bc4%20c5%2011.Be3%20cxd4%2012.Bxd4%20Qc7%2013.Bb3%20Bc5%2014.c3%20Rd8%2015.Kh1%20Bxd4%2016.cxd4%20Be6%2017.Rc1%20Qb6%2018.Bxe6%20Qxe6%2019.Rc7%20Nd5#22) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nf6%203.Nxe5%20Nxe4%204.d4%20d5%205.Bd3%20Nd7%206.O-O%20Bd6%207.f4%20O-O%208.Nc3%20Ndf6%209.Nxe4%20dxe4%2010.Bc4%20c5%2011.Be3%20cxd4%2012.Bxd4%20Qc7%2013.Bb3%20Bc5%2014.c3%20Rd8%2015.Kh1%20Be6%2016.Bxe6%20fxe6%2017.Qb3%20Bxd4%2018.Qxe6%2B%20Kf8%2019.cxd4%20Rxd4#22) |

position 0 (`2kr2r1/ppp5/2n1RbNp/2q2p1P/3p4/2PQ1P1B/PPKN3P/6R1 b - - 0 20`), split at ply 7: Bg5+ (52% there) vs Rd8+ (48%)

| chosen | subpar |
|---|---|
| 20...dxc3 [21.Qxc3] [Qxc3+] 22.bxc3 Rxd2+ 23.Kxd2 [Bg5+] 24.Kc2 Rd8 25.Bxf5 Kb8 26.h4 Bf6 27.Rxf6 a5 28.Rf8 | 20...dxc3 [21.Qxc3] [Qxc3+] 22.bxc3 Rxd2+ 23.Kxd2 Rd8+ 24.Kc2 [Nb4+] 25.cxb4 [Rd2+] 26.Kxd2 Bg5+ [27.Rxg5] [hxg5] 28.Bxf5 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.Qxc3%20Qxc3%2B%2022.bxc3%20Rxd2%2B%2023.Kxd2%20Bg5%2B%2024.Kc2%20Rd8%2025.Bxf5%20Kb8%2026.h4%20Bf6%2027.Rxf6%20a5%2028.Rf8#39) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.Qxc3%20Qxc3%2B%2022.bxc3%20Rxd2%2B%2023.Kxd2%20Rd8%2B%2024.Kc2%20Nb4%2B%2025.cxb4%20Rd2%2B%2026.Kxd2%20Bg5%2B%2027.Rxg5%20hxg5%2028.Bxf5#39) |

position 3 (`2kr1b1r/ppp1pppp/5n2/8/3n1q2/1P1P1B1P/P1P2PP1/RNBQ1K1R b - - 0 11`), split at ply 5: e6 (50% there) vs Qd5 (48%)

| chosen | subpar |
|---|---|
| [11...Qe5] 12.c3 Nxf3 13.Qxf3 [e6] [14.d4] Qb5+ 15.c4 Qf5 16.Qxf5 [exf5] 17.Bb2 Ne4 18.f3 [Ng3+] 19.Kf2 | [11...Qe5] 12.c3 Nxf3 13.Qxf3 Qd5 [14.Qxd5] [Nxd5] 15.d4 [e5] [16.dxe5] Bc5 17.Ke2 Rhe8 18.f4 f6 19.Kf3 |
| [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nc6%202.e4%20d5%203.exd5%20Qxd5%204.b3%20Bg4%205.Bc4%20Qe4%2B%206.Kf1%20Nd4%207.Bd3%20Qf4%208.Be2%20O-O-O%209.h3%20Bxf3%2010.Bxf3%20Nf6%2011.d3%20Qe5%2012.c3%20Nxf3%2013.Qxf3%20e6%2014.d4%20Qb5%2B%2015.c4%20Qf5%2016.Qxf5%20exf5%2017.Bb2%20Ne4%2018.f3%20Ng3%2B%2019.Kf2#21) | [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nc6%202.e4%20d5%203.exd5%20Qxd5%204.b3%20Bg4%205.Bc4%20Qe4%2B%206.Kf1%20Nd4%207.Bd3%20Qf4%208.Be2%20O-O-O%209.h3%20Bxf3%2010.Bxf3%20Nf6%2011.d3%20Qe5%2012.c3%20Nxf3%2013.Qxf3%20Qd5%2014.Qxd5%20Nxd5%2015.d4%20e5%2016.dxe5%20Bc5%2017.Ke2%20Rhe8%2018.f4%20f6%2019.Kf3#21) |

#### S #3 (k = 0): latents 52

position 30 (`1rbq1rk1/5ppp/2np3b/p2Np3/1p2P2P/2PQ2P1/PPN2PB1/R4RK1 b - - 1 17`), split at ply 3: Bxe3 (52% there) vs bxc3 (48%)

| chosen | subpar |
|---|---|
| 17...Be6 18.Nce3 [Bxe3] 19.Nxe3 [bxc3] 20.bxc3 Qc7 21.Rfd1 Rfd8 22.Nd5 Bxd5 [23.Qxd5] Ne7 24.Qd3 Rbc8 25.Rac1 | 17...Be6 18.Nce3 bxc3 19.bxc3 Rb2 20.Nc4 Rb8 21.Rfd1 Qd7 22.Nxd6 [Rfd8] 23.Nf5 [Bxf5] 24.exf5 [Kh8] 25.f6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20e5%206.Ndb5%20d6%207.Bg5%20a6%208.Na3%20b5%209.Nd5%20Be7%2010.Bxf6%20Bxf6%2011.c3%20Bg5%2012.h4%20Bh6%2013.g3%20O-O%2014.Bg2%20Rb8%2015.Nc2%20a5%2016.O-O%20b4%2017.Qd3%20Be6%2018.Nce3%20Bxe3%2019.Nxe3%20bxc3%2020.bxc3%20Qc7%2021.Rfd1%20Rfd8%2022.Nd5%20Bxd5%2023.Qxd5%20Ne7%2024.Qd3%20Rbc8%2025.Rac1#33) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20e5%206.Ndb5%20d6%207.Bg5%20a6%208.Na3%20b5%209.Nd5%20Be7%2010.Bxf6%20Bxf6%2011.c3%20Bg5%2012.h4%20Bh6%2013.g3%20O-O%2014.Bg2%20Rb8%2015.Nc2%20a5%2016.O-O%20b4%2017.Qd3%20Be6%2018.Nce3%20bxc3%2019.bxc3%20Rb2%2020.Nc4%20Rb8%2021.Rfd1%20Qd7%2022.Nxd6%20Rfd8%2023.Nf5%20Bxf5%2024.exf5%20Kh8%2025.f6#33) |

position 2 (`r1bqk2r/p2pbp2/2p1p3/3nP1pp/4N3/P7/1PP2PPP/R1BQKB1R b KQkq - 1 11`), split at ply 7: Nxe4 (53% there) vs d5 (47%)

| chosen | subpar |
|---|---|
| 11...Qc7 12.c4 Qxe5 13.Qc2 [Nf6] 14.Bd3 [Nxe4] 15.Bxe4 [f5] [16.f4] Qxe4+ 17.Qxe4 [fxe4] 18.fxg5 Ba6 19.b3 | 11...Qc7 12.c4 Qxe5 13.Qc2 [Nf6] 14.Bd3 d5 15.f4 gxf4 16.O-O [dxe4] [17.Bxf4] [Qc5+] 18.Kh1 exd3 19.Qxd3 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.a3%20Be7%207.Nxc6%20bxc6%208.e5%20Nd5%209.Qg4%20g5%2010.Ne4%20h5%2011.Qd1%20Qc7%2012.c4%20Qxe5%2013.Qc2%20Nf6%2014.Bd3%20Nxe4%2015.Bxe4%20f5%2016.f4%20Qxe4%2B%2017.Qxe4%20fxe4%2018.fxg5%20Ba6%2019.b3#21) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.a3%20Be7%207.Nxc6%20bxc6%208.e5%20Nd5%209.Qg4%20g5%2010.Ne4%20h5%2011.Qd1%20Qc7%2012.c4%20Qxe5%2013.Qc2%20Nf6%2014.Bd3%20d5%2015.f4%20gxf4%2016.O-O%20dxe4%2017.Bxf4%20Qc5%2B%2018.Kh1%20exd3%2019.Qxd3#21) |

position 13 (`r2qkb1r/ppp3pp/5n2/3p4/8/2P1BB2/PP3P1P/RN1QK2R b KQkq - 2 11`), split at ply 13: Nxe4 (53% there) vs a4 (47%)

| chosen | subpar |
|---|---|
| [11...Bd6] 12.Nd2 O-O 13.Qb3 c6 14.O-O-O [b5] 15.Rhg1 [a5] 16.Bh6 Rf7 17.Ne4 [Nxe4] 18.Bxe4 a4 19.Qc2 | [11...Bd6] 12.Nd2 O-O 13.Qb3 c6 14.O-O-O [b5] 15.Rhg1 [a5] 16.Bh6 Rf7 17.Ne4 a4 18.Qc2 Nxe4 19.Bxe4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.d4%20Bxf5%205.Bd3%20Bg4%206.c3%20e5%207.dxe5%20Nxe5%208.Be2%20Nxf3%2B%209.gxf3%20Bxf3%2010.Bxf3%20Nf6%2011.Be3%20Bd6%2012.Nd2%20O-O%2013.Qb3%20c6%2014.O-O-O%20b5%2015.Rhg1%20a5%2016.Bh6%20Rf7%2017.Ne4%20Nxe4%2018.Bxe4%20a4%2019.Qc2#21) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.d4%20Bxf5%205.Bd3%20Bg4%206.c3%20e5%207.dxe5%20Nxe5%208.Be2%20Nxf3%2B%209.gxf3%20Bxf3%2010.Bxf3%20Nf6%2011.Be3%20Bd6%2012.Nd2%20O-O%2013.Qb3%20c6%2014.O-O-O%20b5%2015.Rhg1%20a5%2016.Bh6%20Rf7%2017.Ne4%20a4%2018.Qc2%20Nxe4%2019.Bxe4#21) |

#### S #4 (k = 0): latents 3714

position 20 (`r3k1nr/1p1n4/1p1bp1pp/3p1p2/3P4/2P2N2/PP1N1PPP/R1B2RK1 b kq - 1 14`), split at ply 11: Rhc8 (51% there) vs Bxe3 (49%)

| chosen | subpar |
|---|---|
| [14...g5] 15.Re1 Kf7 [16.Ne5+] Nxe5 [17.dxe5] Bc5 [18.Nb3] Ne7 [19.Be3] [Rhc8] [20.a3] Bxe3 [21.Rxe3] f4 [22.Re2] | [14...g5] 15.Re1 Kf7 [16.Ne5+] Nxe5 [17.dxe5] Bc5 [18.Nb3] Ne7 [19.Be3] Bxe3 [20.Rxe3] [Nc6] [21.a3] f4 [22.Re2] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20e6%202.Bf4%20c5%203.e3%20cxd4%204.exd4%20Qb6%205.Bc1%20d5%206.Nf3%20Bb4%2B%207.c3%20Bd6%208.Bd3%20g6%209.Nbd2%20f5%2010.Qb3%20h6%2011.Qxb6%20axb6%2012.Bb5%2B%20Bd7%2013.Bxd7%2B%20Nxd7%2014.O-O%20g5%2015.Re1%20Kf7%2016.Ne5%2B%20Nxe5%2017.dxe5%20Bc5%2018.Nb3%20Ne7%2019.Be3%20Rhc8%2020.a3%20Bxe3%2021.Rxe3%20f4%2022.Re2#27) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20e6%202.Bf4%20c5%203.e3%20cxd4%204.exd4%20Qb6%205.Bc1%20d5%206.Nf3%20Bb4%2B%207.c3%20Bd6%208.Bd3%20g6%209.Nbd2%20f5%2010.Qb3%20h6%2011.Qxb6%20axb6%2012.Bb5%2B%20Bd7%2013.Bxd7%2B%20Nxd7%2014.O-O%20g5%2015.Re1%20Kf7%2016.Ne5%2B%20Nxe5%2017.dxe5%20Bc5%2018.Nb3%20Ne7%2019.Be3%20Bxe3%2020.Rxe3%20Nc6%2021.a3%20f4%2022.Re2#27) |

position 38 (`2r2rk1/2q2Ppp/p2b4/1ppQ4/8/2NP4/PP2K1PP/R1B4n b - - 0 22`), split at ply 10: Kd3 (52% there) vs Ke1 (48%)

| chosen | subpar |
|---|---|
| [22...Rxf7] 23.Be3 [Re8] 24.Ne4 [Bxh2] 25.Rf1 Rxe4 26.dxe4 Ng3+ [27.Kd3] Nxf1 28.Bxc5 Qd7 [29.Qxd7] [Rxd7+] [30.Ke2] | [22...Rxf7] 23.Be3 [Re8] 24.Ne4 [Bxh2] 25.Rf1 Rxe4 26.dxe4 Ng3+ 27.Ke1 [Nxf1] 28.e5 Nxe3 29.Qa8+ Rf8 [30.Qe4] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Qh5%20e6%203.Nf3%20Nc6%204.Bb5%20Nb4%205.Ba4%20a6%206.c3%20Nd3%2B%207.Kd1%20Nxf2%2B%208.Ke2%20Nxh1%209.Ne5%20Qe7%2010.d3%20Nf6%2011.Qf3%20b5%2012.Bb3%20d6%2013.Nc6%20Qc7%2014.e5%20Nd5%2015.c4%20Qxc6%2016.cxd5%20Qc7%2017.dxe6%20Bb7%2018.Bd5%20Bxd5%2019.Qxd5%20Rc8%2020.exd6%20Bxd6%2021.Nc3%20O-O%2022.exf7%2B%20Rxf7%2023.Be3%20Re8%2024.Ne4%20Bxh2%2025.Rf1%20Rxe4%2026.dxe4%20Ng3%2B%2027.Kd3%20Nxf1%2028.Bxc5%20Qd7%2029.Qxd7%20Rxd7%2B%2030.Ke2#43) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Qh5%20e6%203.Nf3%20Nc6%204.Bb5%20Nb4%205.Ba4%20a6%206.c3%20Nd3%2B%207.Kd1%20Nxf2%2B%208.Ke2%20Nxh1%209.Ne5%20Qe7%2010.d3%20Nf6%2011.Qf3%20b5%2012.Bb3%20d6%2013.Nc6%20Qc7%2014.e5%20Nd5%2015.c4%20Qxc6%2016.cxd5%20Qc7%2017.dxe6%20Bb7%2018.Bd5%20Bxd5%2019.Qxd5%20Rc8%2020.exd6%20Bxd6%2021.Nc3%20O-O%2022.exf7%2B%20Rxf7%2023.Be3%20Re8%2024.Ne4%20Bxh2%2025.Rf1%20Rxe4%2026.dxe4%20Ng3%2B%2027.Ke1%20Nxf1%2028.e5%20Nxe3%2029.Qa8%2B%20Rf8%2030.Qe4#43) |

position 26 (`r1b1r1k1/2p3bp/2p2pq1/2Np4/p5P1/P1Q1B3/1PP2P1P/1K1R2R1 w - - 3 24`), split at ply 13: Rxg5 (53% there) vs Bxg7 (47%)

| chosen | subpar |
|---|---|
| 24.h4 Rb8 25.h5 Qf7 26.Bd4 h6 27.f4 [Rb5] [28.g5] [hxg5] [29.fxg5] fxg5 [30.Rxg5] Rxc5 31.Rxg7+ Qxg7 | 24.h4 Rb8 25.h5 Qf7 26.Bd4 h6 27.f4 [Rb5] [28.g5] [hxg5] [29.fxg5] fxg5 30.Bxg7 Qxg7 31.Qxg7+ Kxg7 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.h4%20Rb8%2025.h5%20Qf7%2026.Bd4%20h6%2027.f4%20Rb5%2028.g5%20hxg5%2029.fxg5%20fxg5%2030.Rxg5%20Rxc5%2031.Rxg7%2B%20Qxg7#46) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.h4%20Rb8%2025.h5%20Qf7%2026.Bd4%20h6%2027.f4%20Rb5%2028.g5%20hxg5%2029.fxg5%20fxg5%2030.Bxg7%20Qxg7%2031.Qxg7%2B%20Kxg7#46) |

#### S #5 (k = 0): latents 3356

position 43 (`1r1qk2r/p2b2pp/1p3n2/n3Qp2/P2Pp3/4PP2/3N2PP/R1B1KB1R b KQk - 1 17`), split at ply 2: Ba3 (50% there) vs fxe4 (48%)

| chosen | subpar |
|---|---|
| 17...Kf7 [18.Ba3] Re8 19.Qf4 Kg8 20.Bb5 Bxb5 21.axb5 exf3 22.gxf3 Nd5 23.Qxf5 Nxe3 24.Qd3 Qh4+ 25.Ke2 | 17...Kf7 18.fxe4 Re8 19.Qf4 [Nxe4] 20.Nxe4 [Rxe4] 21.Qf3 Qe7 [22.Bd3] Rxd4 [23.O-O] Rxd3 24.Qxf5+ Kg8 [25.Qxd3] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20f6%203.c4%20e5%204.e3%20e4%205.Nfd2%20c6%206.Nc3%20Bb4%207.cxd5%20cxd5%208.f3%20f5%209.Qa4%2B%20Nc6%2010.a3%20Bxc3%2011.bxc3%20Bd7%2012.Qb3%20Rb8%2013.c4%20dxc4%2014.Qxc4%20Nf6%2015.a4%20Na5%2016.Qc5%20b6%2017.Qe5%2B%20Kf7%2018.Ba3%20Re8%2019.Qf4%20Kg8%2020.Bb5%20Bxb5%2021.axb5%20exf3%2022.gxf3%20Nd5%2023.Qxf5%20Nxe3%2024.Qd3%20Qh4%2B%2025.Ke2#33) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20f6%203.c4%20e5%204.e3%20e4%205.Nfd2%20c6%206.Nc3%20Bb4%207.cxd5%20cxd5%208.f3%20f5%209.Qa4%2B%20Nc6%2010.a3%20Bxc3%2011.bxc3%20Bd7%2012.Qb3%20Rb8%2013.c4%20dxc4%2014.Qxc4%20Nf6%2015.a4%20Na5%2016.Qc5%20b6%2017.Qe5%2B%20Kf7%2018.fxe4%20Re8%2019.Qf4%20Nxe4%2020.Nxe4%20Rxe4%2021.Qf3%20Qe7%2022.Bd3%20Rxd4%2023.O-O%20Rxd3%2024.Qxf5%2B%20Kg8%2025.Qxd3#33) |

position 30 (`1rbq1rk1/5ppp/2np3b/p2Np3/1p2P2P/2PQ2P1/PPN2PB1/R4RK1 b - - 1 17`), split at ply 3: Bxe3 (52% there) vs bxc3 (48%)

| chosen | subpar |
|---|---|
| [17...Be6] [18.Nce3] [Bxe3] [19.Nxe3] bxc3 [20.bxc3] Qc7 [21.Rfd1] [Rfd8] [22.Nd5] [Bxd5] [23.Qxd5] [Ne7] [24.Qd3] [Rbc8] [25.Rac1] | [17...Be6] [18.Nce3] bxc3 [19.bxc3] Rb2 20.Nc4 [Rb8] 21.Rfd1 [Qd7] 22.Nxd6 [Rfd8] [23.Nf5] [Bxf5] [24.exf5] Kh8 25.f6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20e5%206.Ndb5%20d6%207.Bg5%20a6%208.Na3%20b5%209.Nd5%20Be7%2010.Bxf6%20Bxf6%2011.c3%20Bg5%2012.h4%20Bh6%2013.g3%20O-O%2014.Bg2%20Rb8%2015.Nc2%20a5%2016.O-O%20b4%2017.Qd3%20Be6%2018.Nce3%20Bxe3%2019.Nxe3%20bxc3%2020.bxc3%20Qc7%2021.Rfd1%20Rfd8%2022.Nd5%20Bxd5%2023.Qxd5%20Ne7%2024.Qd3%20Rbc8%2025.Rac1#33) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20e5%206.Ndb5%20d6%207.Bg5%20a6%208.Na3%20b5%209.Nd5%20Be7%2010.Bxf6%20Bxf6%2011.c3%20Bg5%2012.h4%20Bh6%2013.g3%20O-O%2014.Bg2%20Rb8%2015.Nc2%20a5%2016.O-O%20b4%2017.Qd3%20Be6%2018.Nce3%20bxc3%2019.bxc3%20Rb2%2020.Nc4%20Rb8%2021.Rfd1%20Qd7%2022.Nxd6%20Rfd8%2023.Nf5%20Bxf5%2024.exf5%20Kh8%2025.f6#33) |

position 47 (`r2qr1k1/pp3ppp/1bn5/3p4/3Nb2n/1NP2PBP/PP2B1PK/R2Q1R2 b - - 0 16`), split at ply 8: Bxf5 (52% there) vs Bf2 (48%)

| chosen | subpar |
|---|---|
| 16...Bg6 17.Bd3 [Nxd4] [18.Nxd4] Bxd4 [19.cxd4] Nf5 [20.Bxf5] [Bxf5] 21.Re1 [Qb6] 22.Qd2 [h6] 23.Rac1 Rxe1 24.Rxe1 | 16...Bg6 17.Bd3 [Nxd4] [18.Nxd4] Bxd4 [19.cxd4] Nf5 20.Bf2 [Qd6+] 21.Kg1 Qf4 22.Bxf5 Bxf5 23.Qb3 Re2 24.Qxd5 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bg6%2017.Bd3%20Nxd4%2018.Nxd4%20Bxd4%2019.cxd4%20Nf5%2020.Bxf5%20Bxf5%2021.Re1%20Qb6%2022.Qd2%20h6%2023.Rac1%20Rxe1%2024.Rxe1#31) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bg6%2017.Bd3%20Nxd4%2018.Nxd4%20Bxd4%2019.cxd4%20Nf5%2020.Bf2%20Qd6%2B%2021.Kg1%20Qf4%2022.Bxf5%20Bxf5%2023.Qb3%20Re2%2024.Qxd5#31) |

#### S #6 (k = 0): latents 2512

position 5 (`r3kbnr/pbpn2pp/1p2q3/1Q2p1B1/4P3/2N2N2/PPP3PP/2KR1B1R b kq - 2 11`), split at ply 11: Qxd6 (52% there) vs Qf7 (48%)

| chosen | subpar |
|---|---|
| 11...Bd6 12.Bc4 Qg6 [13.Bd5] c6 14.Bxc6 [Bxc6] 15.Qxc6 Rd8 16.Rxd6 [Qxd6] 17.Qxd6 Ne7 [18.Bxe7] Kf7 [19.Nxe5+] | 11...Bd6 12.Bc4 Qg6 [13.Bd5] c6 14.Bxc6 [Bxc6] 15.Qxc6 Rd8 16.Rxd6 Qf7 [17.Rhd1] Nf6 [18.Bxf6] [gxf6] [19.Nb5] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Nf3%20d6%204.Qe2%20Qe7%205.d3%20b6%206.Nc3%20Bb7%207.fxe5%20dxe5%208.Bg5%20Qe6%209.O-O-O%20fxe4%2010.dxe4%20Nd7%2011.Qb5%20Bd6%2012.Bc4%20Qg6%2013.Bd5%20c6%2014.Bxc6%20Bxc6%2015.Qxc6%20Rd8%2016.Rxd6%20Qxd6%2017.Qxd6%20Ne7%2018.Bxe7%20Kf7%2019.Nxe5%2B#21) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Nf3%20d6%204.Qe2%20Qe7%205.d3%20b6%206.Nc3%20Bb7%207.fxe5%20dxe5%208.Bg5%20Qe6%209.O-O-O%20fxe4%2010.dxe4%20Nd7%2011.Qb5%20Bd6%2012.Bc4%20Qg6%2013.Bd5%20c6%2014.Bxc6%20Bxc6%2015.Qxc6%20Rd8%2016.Rxd6%20Qf7%2017.Rhd1%20Nf6%2018.Bxf6%20gxf6%2019.Nb5#21) |

position 38 (`2r2rk1/2q2Ppp/p2b4/1ppQ4/8/2NP4/PP2K1PP/R1B4n b - - 0 22`), split at ply 4: Ne4 (50% there) vs Rxh1 (48%)

| chosen | subpar |
|---|---|
| 22...Rxf7 23.Be3 [Bxh2] [24.Ne4] [c4] [25.Rxh1] cxd3+ [26.Qxd3] Be5 [27.Ng5] Qc2+ 28.Qxc2 Rxc2+ [29.Kd3] Rxb2 [30.Nxf7] | 22...Rxf7 23.Be3 [Bxh2] 24.Rxh1 Qg3 [25.Ne4] Qxg2+ [26.Kd1] [Qxh1+] 27.Kc2 Qg2+ 28.Kb3 c4+ 29.dxc4 [bxc4+] 30.Ka3 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Qh5%20e6%203.Nf3%20Nc6%204.Bb5%20Nb4%205.Ba4%20a6%206.c3%20Nd3%2B%207.Kd1%20Nxf2%2B%208.Ke2%20Nxh1%209.Ne5%20Qe7%2010.d3%20Nf6%2011.Qf3%20b5%2012.Bb3%20d6%2013.Nc6%20Qc7%2014.e5%20Nd5%2015.c4%20Qxc6%2016.cxd5%20Qc7%2017.dxe6%20Bb7%2018.Bd5%20Bxd5%2019.Qxd5%20Rc8%2020.exd6%20Bxd6%2021.Nc3%20O-O%2022.exf7%2B%20Rxf7%2023.Be3%20Bxh2%2024.Ne4%20c4%2025.Rxh1%20cxd3%2B%2026.Qxd3%20Be5%2027.Ng5%20Qc2%2B%2028.Qxc2%20Rxc2%2B%2029.Kd3%20Rxb2%2030.Nxf7#43) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Qh5%20e6%203.Nf3%20Nc6%204.Bb5%20Nb4%205.Ba4%20a6%206.c3%20Nd3%2B%207.Kd1%20Nxf2%2B%208.Ke2%20Nxh1%209.Ne5%20Qe7%2010.d3%20Nf6%2011.Qf3%20b5%2012.Bb3%20d6%2013.Nc6%20Qc7%2014.e5%20Nd5%2015.c4%20Qxc6%2016.cxd5%20Qc7%2017.dxe6%20Bb7%2018.Bd5%20Bxd5%2019.Qxd5%20Rc8%2020.exd6%20Bxd6%2021.Nc3%20O-O%2022.exf7%2B%20Rxf7%2023.Be3%20Bxh2%2024.Rxh1%20Qg3%2025.Ne4%20Qxg2%2B%2026.Kd1%20Qxh1%2B%2027.Kc2%20Qg2%2B%2028.Kb3%20c4%2B%2029.dxc4%20bxc4%2B%2030.Ka3#43) |

position 9 (`1k2r3/Rpp1qp1p/3pbb2/8/5Qr1/3PBN2/1PP1BPPP/5RK1 w - - 3 19`), split at ply 5: Rfa1 (53% there) vs b3 (47%)

| chosen | subpar |
|---|---|
| 19.Qh6 Reg8 20.g3 Rb4 [21.Rfa1] c5 [22.Ra8+] Kc7 23.Rxg8 Rxb2 24.Raa8 Rb1+ 25.Kg2 [Bd5] [26.c4] [Bc6] | 19.Qh6 Reg8 20.g3 Rb4 21.b3 Bd5 [22.Rfa1] c5 [23.Ra8+] Kc7 24.Rxg8 Bxa1 25.Ra8 Bf6 26.Qf8 Qxf8 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Qh5%20Nf6%203.Qxe5%2B%20Be7%204.d3%20Nc6%205.Qg5%20Nxe4%206.Qxg7%20Bf6%207.Qg4%20d6%208.Qxe4%2B%20Be6%209.Nf3%20Qd7%2010.Nc3%20O-O-O%2011.Be2%20Rde8%2012.O-O%20Bxa2%2013.Qa4%20Be6%2014.Qf4%20Qe7%2015.Nb5%20Rhg8%2016.Nxa7%2B%20Nxa7%2017.Rxa7%20Kb8%2018.Be3%20Rg4%2019.Qh6%20Reg8%2020.g3%20Rb4%2021.Rfa1%20c5%2022.Ra8%2B%20Kc7%2023.Rxg8%20Rxb2%2024.Raa8%20Rb1%2B%2025.Kg2%20Bd5%2026.c4%20Bc6#36) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Qh5%20Nf6%203.Qxe5%2B%20Be7%204.d3%20Nc6%205.Qg5%20Nxe4%206.Qxg7%20Bf6%207.Qg4%20d6%208.Qxe4%2B%20Be6%209.Nf3%20Qd7%2010.Nc3%20O-O-O%2011.Be2%20Rde8%2012.O-O%20Bxa2%2013.Qa4%20Be6%2014.Qf4%20Qe7%2015.Nb5%20Rhg8%2016.Nxa7%2B%20Nxa7%2017.Rxa7%20Kb8%2018.Be3%20Rg4%2019.Qh6%20Reg8%2020.g3%20Rb4%2021.b3%20Bd5%2022.Rfa1%20c5%2023.Ra8%2B%20Kc7%2024.Rxg8%20Bxa1%2025.Ra8%20Bf6%2026.Qf8%20Qxf8#36) |

#### S #7 (k = 0): latents 3718

position 3 (`2kr1b1r/ppp1pppp/5n2/8/3n1q2/1P1P1B1P/P1P2PP1/RNBQ1K1R b - - 0 11`), split at ply 5: Nxe4 (53% there) vs Nxf3 (47%)

| chosen | subpar |
|---|---|
| [11...Qf5] 12.Nc3 e5 13.Ne4 [Nxe4] 14.Bxe4 [Qf6] 15.c3 Ne6 16.Qf3 Qxf3 [17.Bxf3] Rxd3 18.Be3 Rxc3 19.Ke2 | [11...Qf5] 12.Nc3 e5 13.Ne4 Nxf3 14.Qxf3 [Qxf3] [15.gxf3] Nd5 16.Bd2 f5 17.Nc3 [Nb4] 18.Rc1 [a6] 19.a3 |
| [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nc6%202.e4%20d5%203.exd5%20Qxd5%204.b3%20Bg4%205.Bc4%20Qe4%2B%206.Kf1%20Nd4%207.Bd3%20Qf4%208.Be2%20O-O-O%209.h3%20Bxf3%2010.Bxf3%20Nf6%2011.d3%20Qf5%2012.Nc3%20e5%2013.Ne4%20Nxe4%2014.Bxe4%20Qf6%2015.c3%20Ne6%2016.Qf3%20Qxf3%2017.Bxf3%20Rxd3%2018.Be3%20Rxc3%2019.Ke2#21) | [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nc6%202.e4%20d5%203.exd5%20Qxd5%204.b3%20Bg4%205.Bc4%20Qe4%2B%206.Kf1%20Nd4%207.Bd3%20Qf4%208.Be2%20O-O-O%209.h3%20Bxf3%2010.Bxf3%20Nf6%2011.d3%20Qf5%2012.Nc3%20e5%2013.Ne4%20Nxf3%2014.Qxf3%20Qxf3%2015.gxf3%20Nd5%2016.Bd2%20f5%2017.Nc3%20Nb4%2018.Rc1%20a6%2019.a3#21) |

position 26 (`r1b1r1k1/2p3bp/2p2pq1/2Np4/p5P1/P1Q1B3/1PP2P1P/1K1R2R1 w - - 3 24`), split at ply 13: Rxg5 (53% there) vs Bxg7 (47%)

| chosen | subpar |
|---|---|
| 24.h4 Rb8 25.h5 [Qf7] 26.Bd4 h6 27.f4 Rb5 28.g5 hxg5 29.fxg5 [fxg5] [30.Rxg5] Rxc5 [31.Rxg7+] [Qxg7] | 24.h4 Rb8 25.h5 [Qf7] 26.Bd4 h6 27.f4 Rb5 28.g5 hxg5 29.fxg5 [fxg5] 30.Bxg7 Qxg7 [31.Qxg7+] [Kxg7] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.h4%20Rb8%2025.h5%20Qf7%2026.Bd4%20h6%2027.f4%20Rb5%2028.g5%20hxg5%2029.fxg5%20fxg5%2030.Rxg5%20Rxc5%2031.Rxg7%2B%20Qxg7#46) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.h4%20Rb8%2025.h5%20Qf7%2026.Bd4%20h6%2027.f4%20Rb5%2028.g5%20hxg5%2029.fxg5%20fxg5%2030.Bxg7%20Qxg7%2031.Qxg7%2B%20Kxg7#46) |

position 20 (`r3k1nr/1p1n4/1p1bp1pp/3p1p2/3P4/2P2N2/PP1N1PPP/R1B2RK1 b kq - 1 14`), split at ply 1: Ngf6 (51% there) vs g5 (47%)

| chosen | subpar |
|---|---|
| [14...Ngf6] [15.Re1] [Kf7] [16.Ne5+] Bxe5 17.dxe5 [Ne4] 18.Nf3 g5 19.Be3 g4 20.Nd4 Nxe5 21.Bf4 Nd3 22.Re2 | 14...g5 [15.Re1] Kf7 16.Nf1 Ngf6 [17.Ne5+] Bxe5 [18.dxe5] Ne4 19.f3 Nec5 20.Be3 Nd3 21.Re2 N7xe5 22.Bxb6 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20e6%202.Bf4%20c5%203.e3%20cxd4%204.exd4%20Qb6%205.Bc1%20d5%206.Nf3%20Bb4%2B%207.c3%20Bd6%208.Bd3%20g6%209.Nbd2%20f5%2010.Qb3%20h6%2011.Qxb6%20axb6%2012.Bb5%2B%20Bd7%2013.Bxd7%2B%20Nxd7%2014.O-O%20Ngf6%2015.Re1%20Kf7%2016.Ne5%2B%20Bxe5%2017.dxe5%20Ne4%2018.Nf3%20g5%2019.Be3%20g4%2020.Nd4%20Nxe5%2021.Bf4%20Nd3%2022.Re2#27) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20e6%202.Bf4%20c5%203.e3%20cxd4%204.exd4%20Qb6%205.Bc1%20d5%206.Nf3%20Bb4%2B%207.c3%20Bd6%208.Bd3%20g6%209.Nbd2%20f5%2010.Qb3%20h6%2011.Qxb6%20axb6%2012.Bb5%2B%20Bd7%2013.Bxd7%2B%20Nxd7%2014.O-O%20g5%2015.Re1%20Kf7%2016.Nf1%20Ngf6%2017.Ne5%2B%20Bxe5%2018.dxe5%20Ne4%2019.f3%20Nec5%2020.Be3%20Nd3%2021.Re2%20N7xe5%2022.Bxb6#27) |

#### S #8 (k = 0): latents 5410

position 20 (`r3k1nr/1p1n4/1p1bp1pp/3p1p2/3P4/2P2N2/PP1N1PPP/R1B2RK1 b kq - 1 14`), split at ply 11: Rhc8 (51% there) vs Bxe3 (49%)

| chosen | subpar |
|---|---|
| 14...g5 [15.Re1] Kf7 16.Ne5+ Nxe5 17.dxe5 Bc5 [18.Nb3] Ne7 19.Be3 [Rhc8] 20.a3 Bxe3 21.Rxe3 f4 22.Re2 | 14...g5 [15.Re1] Kf7 16.Ne5+ Nxe5 17.dxe5 Bc5 [18.Nb3] Ne7 19.Be3 Bxe3 [20.Rxe3] Nc6 [21.a3] f4 22.Re2 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20e6%202.Bf4%20c5%203.e3%20cxd4%204.exd4%20Qb6%205.Bc1%20d5%206.Nf3%20Bb4%2B%207.c3%20Bd6%208.Bd3%20g6%209.Nbd2%20f5%2010.Qb3%20h6%2011.Qxb6%20axb6%2012.Bb5%2B%20Bd7%2013.Bxd7%2B%20Nxd7%2014.O-O%20g5%2015.Re1%20Kf7%2016.Ne5%2B%20Nxe5%2017.dxe5%20Bc5%2018.Nb3%20Ne7%2019.Be3%20Rhc8%2020.a3%20Bxe3%2021.Rxe3%20f4%2022.Re2#27) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20e6%202.Bf4%20c5%203.e3%20cxd4%204.exd4%20Qb6%205.Bc1%20d5%206.Nf3%20Bb4%2B%207.c3%20Bd6%208.Bd3%20g6%209.Nbd2%20f5%2010.Qb3%20h6%2011.Qxb6%20axb6%2012.Bb5%2B%20Bd7%2013.Bxd7%2B%20Nxd7%2014.O-O%20g5%2015.Re1%20Kf7%2016.Ne5%2B%20Nxe5%2017.dxe5%20Bc5%2018.Nb3%20Ne7%2019.Be3%20Bxe3%2020.Rxe3%20Nc6%2021.a3%20f4%2022.Re2#27) |

position 9 (`1k2r3/Rpp1qp1p/3pbb2/8/5Qr1/3PBN2/1PP1BPPP/5RK1 w - - 3 19`), split at ply 5: Rfa1 (53% there) vs b3 (47%)

| chosen | subpar |
|---|---|
| 19.Qh6 Reg8 20.g3 [Rb4] [21.Rfa1] c5 22.Ra8+ [Kc7] 23.Rxg8 Rxb2 24.Raa8 Rb1+ [25.Kg2] Bd5 26.c4 Bc6 | 19.Qh6 Reg8 20.g3 [Rb4] 21.b3 [Bd5] [22.Rfa1] c5 23.Ra8+ Kc7 [24.Rxg8] [Bxa1] 25.Ra8 Bf6 [26.Qf8] Qxf8 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Qh5%20Nf6%203.Qxe5%2B%20Be7%204.d3%20Nc6%205.Qg5%20Nxe4%206.Qxg7%20Bf6%207.Qg4%20d6%208.Qxe4%2B%20Be6%209.Nf3%20Qd7%2010.Nc3%20O-O-O%2011.Be2%20Rde8%2012.O-O%20Bxa2%2013.Qa4%20Be6%2014.Qf4%20Qe7%2015.Nb5%20Rhg8%2016.Nxa7%2B%20Nxa7%2017.Rxa7%20Kb8%2018.Be3%20Rg4%2019.Qh6%20Reg8%2020.g3%20Rb4%2021.Rfa1%20c5%2022.Ra8%2B%20Kc7%2023.Rxg8%20Rxb2%2024.Raa8%20Rb1%2B%2025.Kg2%20Bd5%2026.c4%20Bc6#36) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Qh5%20Nf6%203.Qxe5%2B%20Be7%204.d3%20Nc6%205.Qg5%20Nxe4%206.Qxg7%20Bf6%207.Qg4%20d6%208.Qxe4%2B%20Be6%209.Nf3%20Qd7%2010.Nc3%20O-O-O%2011.Be2%20Rde8%2012.O-O%20Bxa2%2013.Qa4%20Be6%2014.Qf4%20Qe7%2015.Nb5%20Rhg8%2016.Nxa7%2B%20Nxa7%2017.Rxa7%20Kb8%2018.Be3%20Rg4%2019.Qh6%20Reg8%2020.g3%20Rb4%2021.b3%20Bd5%2022.Rfa1%20c5%2023.Ra8%2B%20Kc7%2024.Rxg8%20Bxa1%2025.Ra8%20Bf6%2026.Qf8%20Qxf8#36) |

position 33 (`r2qk1r1/3bbpnp/p3N1p1/2ppB1P1/1p2P2P/1P3Q2/P1P2P2/2KR1B1R b q - 0 19`), split at ply 12: Qe4+ (53% there) vs Qxd8+ (47%)

| chosen | subpar |
|---|---|
| 19...Bxe6 20.exd5 Bd7 21.d6 [Bxg5+] 22.hxg5 Qxg5+ 23.Bf4 Qf6 [24.Qxa8+] Qd8 [25.Qe4+] Ne6 26.Rxh7 Qa5 27.Bc4 | 19...Bxe6 20.exd5 Bd7 21.d6 [Bxg5+] 22.hxg5 Qxg5+ 23.Bf4 Qf6 [24.Qxa8+] Qd8 25.Qxd8+ [Kxd8] 26.Rxh7 Ne6 27.Be3 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.Bf4%20a6%204.e3%20e6%205.g4%20Bb4%206.Ne2%20Be7%207.g5%20Nh5%208.h4%20b5%209.Bh2%20Nc6%2010.Nc1%20g6%2011.Nb3%20Ng7%2012.Qf3%20b4%2013.Na4%20Bd7%2014.O-O-O%20Nxd4%2015.Nxd4%20Bxa4%2016.Be5%20Rg8%2017.e4%20c5%2018.b3%20Bd7%2019.Nxe6%20Bxe6%2020.exd5%20Bd7%2021.d6%20Bxg5%2B%2022.hxg5%20Qxg5%2B%2023.Bf4%20Qf6%2024.Qxa8%2B%20Qd8%2025.Qe4%2B%20Ne6%2026.Rxh7%20Qa5%2027.Bc4#37) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.Bf4%20a6%204.e3%20e6%205.g4%20Bb4%206.Ne2%20Be7%207.g5%20Nh5%208.h4%20b5%209.Bh2%20Nc6%2010.Nc1%20g6%2011.Nb3%20Ng7%2012.Qf3%20b4%2013.Na4%20Bd7%2014.O-O-O%20Nxd4%2015.Nxd4%20Bxa4%2016.Be5%20Rg8%2017.e4%20c5%2018.b3%20Bd7%2019.Nxe6%20Bxe6%2020.exd5%20Bd7%2021.d6%20Bxg5%2B%2022.hxg5%20Qxg5%2B%2023.Bf4%20Qf6%2024.Qxa8%2B%20Qd8%2025.Qxd8%2B%20Kxd8%2026.Rxh7%20Ne6%2027.Be3#37) |

#### S #9 (k = 0): latents 689

position 13 (`r2qkb1r/ppp3pp/5n2/3p4/8/2P1BB2/PP3P1P/RN1QK2R b KQkq - 2 11`), split at ply 13: Nxe4 (53% there) vs a4 (47%)

| chosen | subpar |
|---|---|
| [11...Bd6] 12.Nd2 O-O [13.Qb3] c6 14.O-O-O b5 [15.Rhg1] a5 16.Bh6 Rf7 [17.Ne4] [Nxe4] [18.Bxe4] a4 [19.Qc2] | [11...Bd6] 12.Nd2 O-O [13.Qb3] c6 14.O-O-O b5 [15.Rhg1] a5 16.Bh6 Rf7 [17.Ne4] a4 [18.Qc2] [Nxe4] [19.Bxe4] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.d4%20Bxf5%205.Bd3%20Bg4%206.c3%20e5%207.dxe5%20Nxe5%208.Be2%20Nxf3%2B%209.gxf3%20Bxf3%2010.Bxf3%20Nf6%2011.Be3%20Bd6%2012.Nd2%20O-O%2013.Qb3%20c6%2014.O-O-O%20b5%2015.Rhg1%20a5%2016.Bh6%20Rf7%2017.Ne4%20Nxe4%2018.Bxe4%20a4%2019.Qc2#21) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.d4%20Bxf5%205.Bd3%20Bg4%206.c3%20e5%207.dxe5%20Nxe5%208.Be2%20Nxf3%2B%209.gxf3%20Bxf3%2010.Bxf3%20Nf6%2011.Be3%20Bd6%2012.Nd2%20O-O%2013.Qb3%20c6%2014.O-O-O%20b5%2015.Rhg1%20a5%2016.Bh6%20Rf7%2017.Ne4%20a4%2018.Qc2%20Nxe4%2019.Bxe4#21) |

position 23 (`rnbqkr2/pppp4/4p2p/b3B1pn/3P4/2NB1N2/PP3PPP/R2QK2R b KQq - 3 14`), split at ply 5: d6 (51% there) vs Nc6 (46%)

| chosen | subpar |
|---|---|
| 14...Nf6 15.Bg6+ [Ke7] 16.O-O [d6] 17.Bg3 [Nc6] 18.Re1 [Kd7] 19.d5 [exd5] 20.Nxd5 [Nxd5] [21.Qxd5] [Qf6] 22.Bf5+ | 14...Nf6 15.Bg6+ [Ke7] 16.O-O Nc6 17.Bg3 Bxc3 18.bxc3 [d6] 19.Re1 Bd7 20.d5 [Nxd5] 21.Qxd5 Qe8 22.Bxe8 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Bd6%203.d3%20Nf6%204.Bg5%20Bb4%2B%205.c3%20Bc5%206.d4%20exd4%207.cxd4%20Bb4%2B%208.Nc3%20Ba5%209.e5%20h6%2010.Bh4%20g5%2011.Bg3%20Nh5%2012.e6%20fxe6%2013.Be5%20Rf8%2014.Bd3%20Nf6%2015.Bg6%2B%20Ke7%2016.O-O%20d6%2017.Bg3%20Nc6%2018.Re1%20Kd7%2019.d5%20exd5%2020.Nxd5%20Nxd5%2021.Qxd5%20Qf6%2022.Bf5%2B#27) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Bd6%203.d3%20Nf6%204.Bg5%20Bb4%2B%205.c3%20Bc5%206.d4%20exd4%207.cxd4%20Bb4%2B%208.Nc3%20Ba5%209.e5%20h6%2010.Bh4%20g5%2011.Bg3%20Nh5%2012.e6%20fxe6%2013.Be5%20Rf8%2014.Bd3%20Nf6%2015.Bg6%2B%20Ke7%2016.O-O%20Nc6%2017.Bg3%20Bxc3%2018.bxc3%20d6%2019.Re1%20Bd7%2020.d5%20Nxd5%2021.Qxd5%20Qe8%2022.Bxe8#27) |

position 17 (`r3k2r/pp2qp1p/2n1bnp1/2p5/2N3P1/2bPBP2/P1PN3P/3QKB1R w Kkq - 1 14`), split at ply 6: Kd7 (55% there) vs Kf8 (45%)

| chosen | subpar |
|---|---|
| 14.Kf2 [Nd5] 15.Ne4 Bd4 16.Ncd6+ [Kd7] 17.Bxd4 Nxd4 18.c3 [Nc6] [19.Nxb7] [Nxc3] 20.Nbxc5+ Kc7 21.Qc2 Nxe4+ | 14.Kf2 [Nd5] 15.Ne4 Bd4 16.Ncd6+ Kf8 17.Bxd4 [cxd4] 18.h4 Ne3 19.Qd2 f5 20.gxf5 [gxf5] 21.Ng3 Qxd6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.d3%20g6%203.Nf3%20Bg7%204.e5%20Nc6%205.Bf4%20d6%206.exd6%20Bxb2%207.dxe7%20Qxe7%2B%208.Be3%20Bxa1%209.Na3%20Bc3%2B%2010.Nd2%20Nf6%2011.Nc4%20Bg4%2012.f3%20Bf5%2013.g4%20Be6%2014.Kf2%20Nd5%2015.Ne4%20Bd4%2016.Ncd6%2B%20Kd7%2017.Bxd4%20Nxd4%2018.c3%20Nc6%2019.Nxb7%20Nxc3%2020.Nbxc5%2B%20Kc7%2021.Qc2%20Nxe4%2B#26) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.d3%20g6%203.Nf3%20Bg7%204.e5%20Nc6%205.Bf4%20d6%206.exd6%20Bxb2%207.dxe7%20Qxe7%2B%208.Be3%20Bxa1%209.Na3%20Bc3%2B%2010.Nd2%20Nf6%2011.Nc4%20Bg4%2012.f3%20Bf5%2013.g4%20Be6%2014.Kf2%20Nd5%2015.Ne4%20Bd4%2016.Ncd6%2B%20Kf8%2017.Bxd4%20cxd4%2018.h4%20Ne3%2019.Qd2%20f5%2020.gxf5%20gxf5%2021.Ng3%20Qxd6#26) |

#### S #10 (k = 0): latents 2234

position 27 (`r3kb1r/1p2pp1p/p2p1np1/4n1Q1/3B4/PP2P3/2qPNPPP/R4RK1 b kq - 1 15`), split at ply 16: e4 (52% there) vs Ng5 (48%)

| chosen | subpar |
|---|---|
| 15...Qf5 [16.Qg3] Ne4 [17.Qh4] Nxd2 [18.Rfd1] Nxb3 [19.Rab1] [Nxd4] [20.Nxd4] Qd7 [21.f4] Nc6 [22.Nf3] Bg7 [23.e4] | 15...Qf5 [16.Qg3] Ne4 [17.Qh4] Nxd2 [18.Rfd1] Nxb3 [19.Rab1] [Nxd4] [20.Nxd4] Qd7 [21.f4] Nc6 [22.Nf3] Bg7 23.Ng5 |
| [Lichess](https://lichess.org/analysis/pgn/1.e3%20c5%202.Qh5%20Nf6%203.Qxc5%20g6%204.Bc4%20d6%205.Qg5%20Nc6%206.a3%20Ne5%207.Bb5%2B%20Bd7%208.Ba4%20Bxa4%209.b3%20Bd7%2010.Bb2%20Qc7%2011.Nc3%20a6%2012.Nge2%20Bb5%2013.O-O%20Bxe2%2014.Nxe2%20Qxc2%2015.Bd4%20Qf5%2016.Qg3%20Ne4%2017.Qh4%20Nxd2%2018.Rfd1%20Nxb3%2019.Rab1%20Nxd4%2020.Nxd4%20Qd7%2021.f4%20Nc6%2022.Nf3%20Bg7%2023.e4#29) | [Lichess](https://lichess.org/analysis/pgn/1.e3%20c5%202.Qh5%20Nf6%203.Qxc5%20g6%204.Bc4%20d6%205.Qg5%20Nc6%206.a3%20Ne5%207.Bb5%2B%20Bd7%208.Ba4%20Bxa4%209.b3%20Bd7%2010.Bb2%20Qc7%2011.Nc3%20a6%2012.Nge2%20Bb5%2013.O-O%20Bxe2%2014.Nxe2%20Qxc2%2015.Bd4%20Qf5%2016.Qg3%20Ne4%2017.Qh4%20Nxd2%2018.Rfd1%20Nxb3%2019.Rab1%20Nxd4%2020.Nxd4%20Qd7%2021.f4%20Nc6%2022.Nf3%20Bg7%2023.Ng5#29) |

position 22 (`r1b2rk1/pp4pp/3B1p2/3P3q/2P3n1/3P4/PP3PPP/R2QR1K1 w - - 1 17`), split at ply 8: Bf5 (53% there) vs Nf5 (47%)

| chosen | subpar |
|---|---|
| [17.h3] Nh6 18.Qxh5 Rd8 19.Bc7 Rf8 [20.Re7] [Bf5] [21.Rae1] [Bg6] 22.Qf3 Nf5 [23.d6] [Nd4] [24.Qd5+] Kh8 | [17.h3] Nh6 18.Qxh5 Rd8 19.Bc7 Rf8 [20.Re7] Nf5 21.Rae1 [Nxe7] [22.Rxe7] [Bf5] 23.Qxf5 Rae8 24.Qe6+ [Kh8] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nf6%203.Bc4%20d5%204.exd5%20e4%205.Ng5%20Bd6%206.Nc3%20Nbd7%207.O-O%20Ne5%208.Re1%20O-O%209.Ncxe4%20Nxc4%2010.Nxf6%2B%20Qxf6%2011.d3%20Ne5%2012.Ne4%20Qg6%2013.Nxd6%20cxd6%2014.Bf4%20f6%2015.c4%20Ng4%2016.Bxd6%20Qh5%2017.h3%20Nh6%2018.Qxh5%20Rd8%2019.Bc7%20Rf8%2020.Re7%20Bf5%2021.Rae1%20Bg6%2022.Qf3%20Nf5%2023.d6%20Nd4%2024.Qd5%2B%20Kh8#32) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nf6%203.Bc4%20d5%204.exd5%20e4%205.Ng5%20Bd6%206.Nc3%20Nbd7%207.O-O%20Ne5%208.Re1%20O-O%209.Ncxe4%20Nxc4%2010.Nxf6%2B%20Qxf6%2011.d3%20Ne5%2012.Ne4%20Qg6%2013.Nxd6%20cxd6%2014.Bf4%20f6%2015.c4%20Ng4%2016.Bxd6%20Qh5%2017.h3%20Nh6%2018.Qxh5%20Rd8%2019.Bc7%20Rf8%2020.Re7%20Nf5%2021.Rae1%20Nxe7%2022.Rxe7%20Bf5%2023.Qxf5%20Rae8%2024.Qe6%2B%20Kh8#32) |

position 10 (`2r2rk1/pp1bb1pp/1qn1pn2/3p1p2/PP1P4/2P2N1P/3NBPPB/R1Q2RK1 w - - 1 15`), split at ply 1: Qb2 (53% there) vs a5 (46%)

| chosen | subpar |
|---|---|
| [15.Qb2] Ne4 16.a5 Qd8 [17.Nxe4] [fxe4] [18.Ne5] Nxe5 [19.Bxe5] Bf6 20.Bd6 Rf7 21.b5 Be7 22.Be5 Bf6 | 15.a5 Qd8 [16.Qb2] Ne4 [17.Nb3] Bd6 18.Bxd6 Nxd6 [19.Nc5] Ne4 20.Nxb7 Qc7 21.Nc5 Nxc5 22.bxc5 Rb8 |
| [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nf6%202.d4%20e6%203.Bf4%20c5%204.e3%20cxd4%205.exd4%20Qb6%206.Qc1%20Nc6%207.c3%20Be7%208.Nbd2%20d5%209.h3%20Nh5%2010.Bh2%20O-O%2011.Be2%20Bd7%2012.O-O%20f5%2013.b4%20Nf6%2014.a4%20Rac8%2015.Qb2%20Ne4%2016.a5%20Qd8%2017.Nxe4%20fxe4%2018.Ne5%20Nxe5%2019.Bxe5%20Bf6%2020.Bd6%20Rf7%2021.b5%20Be7%2022.Be5%20Bf6#28) | [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nf6%202.d4%20e6%203.Bf4%20c5%204.e3%20cxd4%205.exd4%20Qb6%206.Qc1%20Nc6%207.c3%20Be7%208.Nbd2%20d5%209.h3%20Nh5%2010.Bh2%20O-O%2011.Be2%20Bd7%2012.O-O%20f5%2013.b4%20Nf6%2014.a4%20Rac8%2015.a5%20Qd8%2016.Qb2%20Ne4%2017.Nb3%20Bd6%2018.Bxd6%20Nxd6%2019.Nc5%20Ne4%2020.Nxb7%20Qc7%2021.Nc5%20Nxc5%2022.bxc5%20Rb8#28) |

## W

| k | pairs | nonzero v | families | held-out recurrence: median / 90% / max | null 95th: median | null (every draw): 90% / 99% | families above their null 95th (chance: 5%) |
|---|---|---|---|---|---|---|---|
| 0 | 2462 | 100% | 838 | 0.2% / 1.6% / 16.0% | 0.7% | 1.1% / 10.1% | 55 (7%) |
| 2 | 2460 | 57% | 885 | 0.0% / 0.3% / 1.4% | 0.0% | 0.0% / 0.2% | 165 (19%) |
| 4 | 2458 | 28% | 619 | 0.0% / 0.1% / 0.5% | 0.0% | 0.0% / 0.1% | 64 (10%) |
| 6 | 2455 | 13% | 301 | 0.0% / 0.0% / 0.7% | 0.0% | 0.0% / 0.0% | 27 (9%) |

### W: the top 20 families by held-out recurrence

| # | k | latents (weight) | found in | held out on | recurrence | null 95th | persistence (pairs on at split) | positions found |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 689 (1.00) | A (54 v's) | B | 16.0% | 8.0% | 1.0 (194) | 0, 3, 5, 7, 9, 11, 16, 19, 20, 24, 25, 26 ... |
| 2 | 0 | 2512 (1.00) | A (5 v's) | B | 15.8% | 6.3% | 1.0 (191) | 9, 11, 31, 49 |
| 3 | 0 | 2512 (1.00) | B (3 v's) | A | 15.3% | 3.0% | 1.0 (191) | 12, 17, 44 |
| 4 | 0 | 52 (1.00) | A (168 v's) | B | 14.7% | 3.8% | 1.0 (178) | 0, 3, 5, 6, 7, 9, 11, 16, 18, 19, 20, 24 ... |
| 5 | 0 | 52 (1.00) | B (174 v's) | A | 14.6% | 4.1% | 1.0 (183) | 2, 4, 8, 10, 12, 13, 14, 15, 17, 21, 22, 23 ... |
| 6 | 0 | 3714 (1.00) | A (3 v's) | B | 14.4% | 2.2% | 1.0 (174) | 11, 46 |
| 7 | 0 | 2234 (1.00) | B (8 v's) | A | 14.2% | 3.9% | 1.0 (178) | 2, 8, 10, 15, 17, 21, 27 |
| 8 | 0 | 689 (1.00) | B (48 v's) | A | 14.2% | 3.5% | 1.0 (177) | 4, 8, 12, 13, 15, 17, 21, 22, 23, 27, 32, 36 ... |
| 9 | 0 | 9134 (1.00) | B (1 v's) | A | 13.8% | 10.0% | 1.0 (173) | 17 |
| 10 | 0 | 3356 (1.00) | B (1 v's) | A | 13.1% | 4.1% | 1.0 (164) | 41 |
| 11 | 0 | 2234 (1.00) | A (7 v's) | B | 13.1% | 7.8% | 1.0 (159) | 0, 6, 16, 18, 26, 35, 45 |
| 12 | 0 | 5111 (1.00) | A (2 v's) | B | 13.0% | 3.8% | 1.0 (158) | 29, 31 |
| 13 | 0 | 1263 (1.00) | A (12 v's) | B | 12.8% | 3.0% | 1.0 (155) | 3, 6, 7, 16, 20, 31, 33, 34, 37, 38, 49 |
| 14 | 0 | 5080 (1.00) | A (1 v's) | B | 12.5% | 2.3% | 1.0 (152) | 6 |
| 15 | 0 | 5410 (1.00) | B (1 v's) | A | 12.4% | 3.4% | 1.0 (155) | 15 |
| 16 | 0 | 3718 (1.00) | A (3 v's) | B | 12.1% | 10.3% | 1.0 (147) | 20, 29, 45 |
| 17 | 0 | 1263 (1.00) | B (20 v's) | A | 12.0% | 2.8% | 1.0 (150) | 4, 12, 13, 15, 17, 32, 36, 39, 40, 41, 42, 44 ... |
| 18 | 0 | 2095 (1.00) | B (9 v's) | A | 11.3% | 2.9% | 1.0 (141) | 2, 10, 13, 21, 22, 27, 32, 36, 43 |
| 19 | 0 | 801 (1.00) | A (25 v's) | B | 10.7% | 2.6% | 1.0 (130) | 0, 3, 5, 6, 7, 9, 16, 18, 20, 28, 29, 33 ... |
| 20 | 0 | 4312 (1.00) | B (1 v's) | A | 10.6% | 3.8% | 1.0 (133) | 10 |

#### W #1 (k = 0): latents 689

position 47 (`r2qr1k1/pp3ppp/1bn5/3p4/3Nb2n/1NP2PBP/PP2B1PK/R2Q1R2 b - - 0 16`), split at ply 4: Qxd4 (51% there) vs cxd4 (49%)

| chosen | subpar |
|---|---|
| [16...Bxd4] 17.Nxd4 [Nxd4] [18.Qxd4] Nf5 19.Qf2 [Bc2] [20.Rfe1] [Ba4] 21.b3 [Bc6] [22.Bd3] Rxe1 [23.Rxe1] Nxg3 24.Qxg3 | [16...Bxd4] 17.Nxd4 [Nxd4] 18.cxd4 [Bf5] 19.Bd3 [Bxd3] 20.Qxd3 [Ng6] [21.Rfe1] Rxe1 [22.Rxe1] [Qb6] 23.b3 [h6] [24.Qf5] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bxd4%2017.Nxd4%20Nxd4%2018.Qxd4%20Nf5%2019.Qf2%20Bc2%2020.Rfe1%20Ba4%2021.b3%20Bc6%2022.Bd3%20Rxe1%2023.Rxe1%20Nxg3%2024.Qxg3#31) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bxd4%2017.Nxd4%20Nxd4%2018.cxd4%20Bf5%2019.Bd3%20Bxd3%2020.Qxd3%20Ng6%2021.Rfe1%20Rxe1%2022.Rxe1%20Qb6%2023.b3%20h6%2024.Qf5#31) |

position 44 (`6rr/ppkn3p/8/2pQ4/5Bb1/3B3P/PqP5/2R2KNR b - - 0 24`), split at ply 15: Kb5 (53% there) vs Ka3 (47%)

| chosen | subpar |
|---|---|
| 24...Kb6 25.Qd6+ Ka5 [26.Bd2+] [Ka4] [27.Qf4+] Ka3 [28.Qe3] Rf8+ [29.Nf3] Bxf3 30.Bc4+ [Ka4] [31.Bb3+] [Kb5] [32.Qd3+] | 24...Kb6 25.Qd6+ Ka5 [26.Bd2+] [Ka4] [27.Qf4+] Ka3 [28.Qe3] Rf8+ [29.Nf3] Bxf3 30.Bc4+ [Ka4] [31.Bb3+] Ka3 [32.Qc3] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Bc4%20fxe4%204.d3%20d5%205.Bb3%20exd3%206.Qxd3%20e4%207.Qd4%20Nf6%208.Nc3%20c5%209.Qe5%2B%20Be7%2010.Nxd5%20Nxd5%2011.Bxd5%20Qa5%2B%2012.Bd2%20Qb6%2013.Qxg7%20Bf6%2014.Qf7%2B%20Kd8%2015.Bxe4%20Bg4%2016.Qd5%2B%20Nd7%2017.h3%20Bh4%2B%2018.g3%20Bxg3%2B%2019.Kf1%20Qb5%2B%2020.Bd3%20Qxb2%2021.Qg5%2B%20Kc7%2022.Rc1%20Rag8%2023.Qd5%20Bxf4%2024.Bxf4%2B%20Kb6%2025.Qd6%2B%20Ka5%2026.Bd2%2B%20Ka4%2027.Qf4%2B%20Ka3%2028.Qe3%20Rf8%2B%2029.Nf3%20Bxf3%2030.Bc4%2B%20Ka4%2031.Bb3%2B%20Kb5%2032.Qd3%2B#47) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Bc4%20fxe4%204.d3%20d5%205.Bb3%20exd3%206.Qxd3%20e4%207.Qd4%20Nf6%208.Nc3%20c5%209.Qe5%2B%20Be7%2010.Nxd5%20Nxd5%2011.Bxd5%20Qa5%2B%2012.Bd2%20Qb6%2013.Qxg7%20Bf6%2014.Qf7%2B%20Kd8%2015.Bxe4%20Bg4%2016.Qd5%2B%20Nd7%2017.h3%20Bh4%2B%2018.g3%20Bxg3%2B%2019.Kf1%20Qb5%2B%2020.Bd3%20Qxb2%2021.Qg5%2B%20Kc7%2022.Rc1%20Rag8%2023.Qd5%20Bxf4%2024.Bxf4%2B%20Kb6%2025.Qd6%2B%20Ka5%2026.Bd2%2B%20Ka4%2027.Qf4%2B%20Ka3%2028.Qe3%20Rf8%2B%2029.Nf3%20Bxf3%2030.Bc4%2B%20Ka4%2031.Bb3%2B%20Ka3%2032.Qc3#47) |

position 4 (`r1bq1b1r/3k2pp/p1p5/1p1Bp1N1/8/3P4/PPP2PPP/RNB1K2R w KQ - 0 12`), split at ply 7: Ne4 (54% there) vs Nf3 (46%)

| chosen | subpar |
|---|---|
| 12.Be6+ [Ke7] [13.Bxc8] [Qxc8] 14.O-O h6 [15.Ne4] [g5] [16.Nbc3] Bg7 17.Be3 Rd8 18.Bc5+ Kf7 19.Nd6+ [Rxd6] | 12.Be6+ [Ke7] [13.Bxc8] [Qxc8] 14.O-O h6 15.Nf3 g5 16.Nxe5 Bg7 17.Ng6+ [Kf6] 18.Nxh8 Qxh8 [19.Nc3] Re8 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Bc4%20a6%203.d3%20Nf6%204.Nf3%20b5%205.Bb3%20Nc6%206.Ng5%20d5%207.exd5%20Nxd5%208.Qf3%20Nce7%209.Qxf7%2B%20Kd7%2010.Qxd5%2B%20Nxd5%2011.Bxd5%20c6%2012.Be6%2B%20Ke7%2013.Bxc8%20Qxc8%2014.O-O%20h6%2015.Ne4%20g5%2016.Nbc3%20Bg7%2017.Be3%20Rd8%2018.Bc5%2B%20Kf7%2019.Nd6%2B%20Rxd6#22) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Bc4%20a6%203.d3%20Nf6%204.Nf3%20b5%205.Bb3%20Nc6%206.Ng5%20d5%207.exd5%20Nxd5%208.Qf3%20Nce7%209.Qxf7%2B%20Kd7%2010.Qxd5%2B%20Nxd5%2011.Bxd5%20c6%2012.Be6%2B%20Ke7%2013.Bxc8%20Qxc8%2014.O-O%20h6%2015.Nf3%20g5%2016.Nxe5%20Bg7%2017.Ng6%2B%20Kf6%2018.Nxh8%20Qxh8%2019.Nc3%20Re8#22) |

#### W #2 (k = 0): latents 2512

position 47 (`r2qr1k1/pp3ppp/1bn5/3p4/3Nb2n/1NP2PBP/PP2B1PK/R2Q1R2 b - - 0 16`), split at ply 4: Qxd4 (51% there) vs cxd4 (49%)

| chosen | subpar |
|---|---|
| 16...Bxd4 17.Nxd4 Nxd4 [18.Qxd4] Nf5 19.Qf2 Bc2 20.Rfe1 Ba4 [21.b3] Bc6 22.Bd3 Rxe1 23.Rxe1 Nxg3 24.Qxg3 | 16...Bxd4 17.Nxd4 Nxd4 18.cxd4 Bf5 [19.Bd3] Bxd3 [20.Qxd3] Ng6 21.Rfe1 Rxe1 22.Rxe1 Qb6 [23.b3] h6 [24.Qf5] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bxd4%2017.Nxd4%20Nxd4%2018.Qxd4%20Nf5%2019.Qf2%20Bc2%2020.Rfe1%20Ba4%2021.b3%20Bc6%2022.Bd3%20Rxe1%2023.Rxe1%20Nxg3%2024.Qxg3#31) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bxd4%2017.Nxd4%20Nxd4%2018.cxd4%20Bf5%2019.Bd3%20Bxd3%2020.Qxd3%20Ng6%2021.Rfe1%20Rxe1%2022.Rxe1%20Qb6%2023.b3%20h6%2024.Qf5#31) |

position 44 (`6rr/ppkn3p/8/2pQ4/5Bb1/3B3P/PqP5/2R2KNR b - - 0 24`), split at ply 7: Rf8+ (52% there) vs Rxg4 (48%)

| chosen | subpar |
|---|---|
| [24...Kb6] [25.Qd6+] Ka5 26.Bd2+ Ka4 27.hxg4 [Rf8+] 28.Kg2 Rhg8 29.Qxd7+ Ka3 30.Qa4+ Kxa4 [31.Bc4] [Rxg4+] [32.Kh2] | [24...Kb6] [25.Qd6+] Ka5 26.Bd2+ Ka4 27.hxg4 Rxg4 28.Bf5 [Qb5+] 29.Ne2 Rf8 30.Ke1 Rxf5 31.Nc3+ [Ka3] 32.Nxb5+ |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Bc4%20fxe4%204.d3%20d5%205.Bb3%20exd3%206.Qxd3%20e4%207.Qd4%20Nf6%208.Nc3%20c5%209.Qe5%2B%20Be7%2010.Nxd5%20Nxd5%2011.Bxd5%20Qa5%2B%2012.Bd2%20Qb6%2013.Qxg7%20Bf6%2014.Qf7%2B%20Kd8%2015.Bxe4%20Bg4%2016.Qd5%2B%20Nd7%2017.h3%20Bh4%2B%2018.g3%20Bxg3%2B%2019.Kf1%20Qb5%2B%2020.Bd3%20Qxb2%2021.Qg5%2B%20Kc7%2022.Rc1%20Rag8%2023.Qd5%20Bxf4%2024.Bxf4%2B%20Kb6%2025.Qd6%2B%20Ka5%2026.Bd2%2B%20Ka4%2027.hxg4%20Rf8%2B%2028.Kg2%20Rhg8%2029.Qxd7%2B%20Ka3%2030.Qa4%2B%20Kxa4%2031.Bc4%20Rxg4%2B%2032.Kh2#47) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Bc4%20fxe4%204.d3%20d5%205.Bb3%20exd3%206.Qxd3%20e4%207.Qd4%20Nf6%208.Nc3%20c5%209.Qe5%2B%20Be7%2010.Nxd5%20Nxd5%2011.Bxd5%20Qa5%2B%2012.Bd2%20Qb6%2013.Qxg7%20Bf6%2014.Qf7%2B%20Kd8%2015.Bxe4%20Bg4%2016.Qd5%2B%20Nd7%2017.h3%20Bh4%2B%2018.g3%20Bxg3%2B%2019.Kf1%20Qb5%2B%2020.Bd3%20Qxb2%2021.Qg5%2B%20Kc7%2022.Rc1%20Rag8%2023.Qd5%20Bxf4%2024.Bxf4%2B%20Kb6%2025.Qd6%2B%20Ka5%2026.Bd2%2B%20Ka4%2027.hxg4%20Rxg4%2028.Bf5%20Qb5%2B%2029.Ne2%20Rf8%2030.Ke1%20Rxf5%2031.Nc3%2B%20Ka3%2032.Nxb5%2B#47) |

position 2 (`r1bqk2r/p2pbp2/2p1p3/3nP1pp/4N3/P7/1PP2PPP/R1BQKB1R b KQkq - 1 11`), split at ply 3: Bxf6 (53% there) vs Nxf6 (47%)

| chosen | subpar |
|---|---|
| [11...f5] 12.exf6 [Bxf6] 13.Nxf6+ [Qxf6] 14.Be2 [Rf8] 15.O-O [g4] [16.Bxg4] [hxg4] [17.Qxg4] [Ba6] [18.Qh5+] Rf7 [19.Bg5] | [11...f5] 12.exf6 Nxf6 [13.Nxg5] Nd5 14.Bd3 Bxg5 15.Bg6+ Ke7 16.Bxg5+ Nf6 [17.Qd4] Rf8 18.Qh4 Qa5+ 19.c3 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.a3%20Be7%207.Nxc6%20bxc6%208.e5%20Nd5%209.Qg4%20g5%2010.Ne4%20h5%2011.Qd1%20f5%2012.exf6%20Bxf6%2013.Nxf6%2B%20Qxf6%2014.Be2%20Rf8%2015.O-O%20g4%2016.Bxg4%20hxg4%2017.Qxg4%20Ba6%2018.Qh5%2B%20Rf7%2019.Bg5#21) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.a3%20Be7%207.Nxc6%20bxc6%208.e5%20Nd5%209.Qg4%20g5%2010.Ne4%20h5%2011.Qd1%20f5%2012.exf6%20Nxf6%2013.Nxg5%20Nd5%2014.Bd3%20Bxg5%2015.Bg6%2B%20Ke7%2016.Bxg5%2B%20Nf6%2017.Qd4%20Rf8%2018.Qh4%20Qa5%2B%2019.c3#21) |

#### W #3 (k = 0): latents 2512

position 33 (`r2qk1r1/3bbpnp/p3N1p1/2ppB1P1/1p2P2P/1P3Q2/P1P2P2/2KR1B1R b q - 0 19`), split at ply 9: Qd8 (52% there) vs Qc8 (48%)

| chosen | subpar |
|---|---|
| 19...Bxe6 20.exd5 Bf5 [21.d6] Bxd6 22.Bxd6 Qd7 23.Qxa8+ [Qd8] 24.Qc6+ Qd7 25.Qxa6 Ne6 26.Bb5 [Qxb5] 27.Qxb5+ | 19...Bxe6 20.exd5 Bf5 [21.d6] Bxd6 22.Bxd6 Qd7 23.Qxa8+ Qc8 24.Qxa6 Qxa6 25.Bxa6 Ne6 26.Bb5+ [Kd8] [27.Bxc5+] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.Bf4%20a6%204.e3%20e6%205.g4%20Bb4%206.Ne2%20Be7%207.g5%20Nh5%208.h4%20b5%209.Bh2%20Nc6%2010.Nc1%20g6%2011.Nb3%20Ng7%2012.Qf3%20b4%2013.Na4%20Bd7%2014.O-O-O%20Nxd4%2015.Nxd4%20Bxa4%2016.Be5%20Rg8%2017.e4%20c5%2018.b3%20Bd7%2019.Nxe6%20Bxe6%2020.exd5%20Bf5%2021.d6%20Bxd6%2022.Bxd6%20Qd7%2023.Qxa8%2B%20Qd8%2024.Qc6%2B%20Qd7%2025.Qxa6%20Ne6%2026.Bb5%20Qxb5%2027.Qxb5%2B#37) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.Bf4%20a6%204.e3%20e6%205.g4%20Bb4%206.Ne2%20Be7%207.g5%20Nh5%208.h4%20b5%209.Bh2%20Nc6%2010.Nc1%20g6%2011.Nb3%20Ng7%2012.Qf3%20b4%2013.Na4%20Bd7%2014.O-O-O%20Nxd4%2015.Nxd4%20Bxa4%2016.Be5%20Rg8%2017.e4%20c5%2018.b3%20Bd7%2019.Nxe6%20Bxe6%2020.exd5%20Bf5%2021.d6%20Bxd6%2022.Bxd6%20Qd7%2023.Qxa8%2B%20Qc8%2024.Qxa6%20Qxa6%2025.Bxa6%20Ne6%2026.Bb5%2B%20Kd8%2027.Bxc5%2B#37) |

position 26 (`r1b1r1k1/2p3bp/2p2pq1/2Np4/p5P1/P1Q1B3/1PP2P1P/1K1R2R1 w - - 3 24`), split at ply 7: Rg3 (52% there) vs Rxg7+ (48%)

| chosen | subpar |
|---|---|
| [24.h4] Qf7 [25.g5] fxg5 26.Rxg5 h6 [27.Rg3] Kh8 28.Bxh6 Bxc3 [29.Rxc3] [Qxf2] 30.Nd3 Qxh4 31.Bd2 Bg4 | [24.h4] Qf7 [25.g5] fxg5 26.Rxg5 h6 27.Rxg7+ Qxg7 28.Qxg7+ Kxg7 29.Rg1+ [Kh7] 30.Nd3 Bf5 31.Nf4 Rg8 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.h4%20Qf7%2025.g5%20fxg5%2026.Rxg5%20h6%2027.Rg3%20Kh8%2028.Bxh6%20Bxc3%2029.Rxc3%20Qxf2%2030.Nd3%20Qxh4%2031.Bd2%20Bg4#46) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.h4%20Qf7%2025.g5%20fxg5%2026.Rxg5%20h6%2027.Rxg7%2B%20Qxg7%2028.Qxg7%2B%20Kxg7%2029.Rg1%2B%20Kh7%2030.Nd3%20Bf5%2031.Nf4%20Rg8#46) |

position 34 (`r2qk2r/1pp1bppp/2n1p3/1p6/3PR3/P1P2N2/5PPP/R2Q2K1 b kq - 0 14`), split at ply 4: Qc2 (50% there) vs Qxd5 (48%)

| chosen | subpar |
|---|---|
| 14...O-O 15.Qb3 Qd5 [16.Qc2] Bxa3 17.Rh4 h6 [18.Ne5] [Nxe5] 19.dxe5 Qxe5 20.Rh3 Bd6 21.g3 Rxa1+ 22.Kg2 | 14...O-O 15.Qb3 Qd5 16.Qxd5 exd5 17.Re3 Rfe8 18.Rb1 Rxa3 19.Rxb5 [Ra1+] 20.Re1 Rxe1+ [21.Nxe1] b6 [22.Rxd5] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20O-O%2015.Qb3%20Qd5%2016.Qc2%20Bxa3%2017.Rh4%20h6%2018.Ne5%20Nxe5%2019.dxe5%20Qxe5%2020.Rh3%20Bd6%2021.g3%20Rxa1%2B%2022.Kg2#27) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20O-O%2015.Qb3%20Qd5%2016.Qxd5%20exd5%2017.Re3%20Rfe8%2018.Rb1%20Rxa3%2019.Rxb5%20Ra1%2B%2020.Re1%20Rxe1%2B%2021.Nxe1%20b6%2022.Rxd5#27) |

#### W #4 (k = 0): latents 52

position 17 (`r3k2r/pp2qp1p/2n1bnp1/2p5/2N3P1/2bPBP2/P1PN3P/3QKB1R w Kkq - 1 14`), split at ply 6: Qxe2+ (52% there) vs Bxd2+ (48%)

| chosen | subpar |
|---|---|
| [14.Bh3] Bxc4 15.dxc4 Qxe3+ [16.Qe2] [Qxe2+] [17.Kxe2] [Nd4+] 18.Kd3 Bxd2 19.Kxd2 Nxf3+ 20.Ke3 Nd4 21.g5 Nh5 | [14.Bh3] Bxc4 15.dxc4 Qxe3+ [16.Qe2] Bxd2+ [17.Kf1] Qxe2+ 18.Kxe2 [Bg5] 19.Re1 [O-O] 20.Kf2 Rfe8 21.Rxe8+ Rxe8 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.d3%20g6%203.Nf3%20Bg7%204.e5%20Nc6%205.Bf4%20d6%206.exd6%20Bxb2%207.dxe7%20Qxe7%2B%208.Be3%20Bxa1%209.Na3%20Bc3%2B%2010.Nd2%20Nf6%2011.Nc4%20Bg4%2012.f3%20Bf5%2013.g4%20Be6%2014.Bh3%20Bxc4%2015.dxc4%20Qxe3%2B%2016.Qe2%20Qxe2%2B%2017.Kxe2%20Nd4%2B%2018.Kd3%20Bxd2%2019.Kxd2%20Nxf3%2B%2020.Ke3%20Nd4%2021.g5%20Nh5#26) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.d3%20g6%203.Nf3%20Bg7%204.e5%20Nc6%205.Bf4%20d6%206.exd6%20Bxb2%207.dxe7%20Qxe7%2B%208.Be3%20Bxa1%209.Na3%20Bc3%2B%2010.Nd2%20Nf6%2011.Nc4%20Bg4%2012.f3%20Bf5%2013.g4%20Be6%2014.Bh3%20Bxc4%2015.dxc4%20Qxe3%2B%2016.Qe2%20Bxd2%2B%2017.Kf1%20Qxe2%2B%2018.Kxe2%20Bg5%2019.Re1%20O-O%2020.Kf2%20Rfe8%2021.Rxe8%2B%20Rxe8#26) |

position 44 (`6rr/ppkn3p/8/2pQ4/5Bb1/3B3P/PqP5/2R2KNR b - - 0 24`), split at ply 7: Rf8+ (52% there) vs Rxg4 (48%)

| chosen | subpar |
|---|---|
| 24...Kb6 [25.Qd6+] Ka5 [26.Bd2+] [Ka4] [27.hxg4] [Rf8+] [28.Kg2] [Rhg8] [29.Qxd7+] [Ka3] 30.Qa4+ Kxa4 [31.Bc4] Rxg4+ [32.Kh2] | 24...Kb6 [25.Qd6+] Ka5 [26.Bd2+] [Ka4] [27.hxg4] Rxg4 28.Bf5 Qb5+ [29.Ne2] Rf8 30.Ke1 Rxf5 [31.Nc3+] Ka3 [32.Nxb5+] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Bc4%20fxe4%204.d3%20d5%205.Bb3%20exd3%206.Qxd3%20e4%207.Qd4%20Nf6%208.Nc3%20c5%209.Qe5%2B%20Be7%2010.Nxd5%20Nxd5%2011.Bxd5%20Qa5%2B%2012.Bd2%20Qb6%2013.Qxg7%20Bf6%2014.Qf7%2B%20Kd8%2015.Bxe4%20Bg4%2016.Qd5%2B%20Nd7%2017.h3%20Bh4%2B%2018.g3%20Bxg3%2B%2019.Kf1%20Qb5%2B%2020.Bd3%20Qxb2%2021.Qg5%2B%20Kc7%2022.Rc1%20Rag8%2023.Qd5%20Bxf4%2024.Bxf4%2B%20Kb6%2025.Qd6%2B%20Ka5%2026.Bd2%2B%20Ka4%2027.hxg4%20Rf8%2B%2028.Kg2%20Rhg8%2029.Qxd7%2B%20Ka3%2030.Qa4%2B%20Kxa4%2031.Bc4%20Rxg4%2B%2032.Kh2#47) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Bc4%20fxe4%204.d3%20d5%205.Bb3%20exd3%206.Qxd3%20e4%207.Qd4%20Nf6%208.Nc3%20c5%209.Qe5%2B%20Be7%2010.Nxd5%20Nxd5%2011.Bxd5%20Qa5%2B%2012.Bd2%20Qb6%2013.Qxg7%20Bf6%2014.Qf7%2B%20Kd8%2015.Bxe4%20Bg4%2016.Qd5%2B%20Nd7%2017.h3%20Bh4%2B%2018.g3%20Bxg3%2B%2019.Kf1%20Qb5%2B%2020.Bd3%20Qxb2%2021.Qg5%2B%20Kc7%2022.Rc1%20Rag8%2023.Qd5%20Bxf4%2024.Bxf4%2B%20Kb6%2025.Qd6%2B%20Ka5%2026.Bd2%2B%20Ka4%2027.hxg4%20Rxg4%2028.Bf5%20Qb5%2B%2029.Ne2%20Rf8%2030.Ke1%20Rxf5%2031.Nc3%2B%20Ka3%2032.Nxb5%2B#47) |

position 36 (`3r1rk1/1pq1npp1/p1p1P2p/8/4Q3/5N2/PP3PPP/3R1RK1 b - - 0 20`), split at ply 13: Kxg8 (54% there) vs Qxe5 (46%)

| chosen | subpar |
|---|---|
| 20...fxe6 21.Qxe6+ Kh8 22.Ne5 [Rxd1] 23.Rxd1 [Rf6] 24.Rd8+ Kh7 25.Qg8+ Nxg8 26.Rxg8 [Kxg8] 27.Nxc6 [Qxc6] 28.b4 | 20...fxe6 21.Qxe6+ Kh8 22.Ne5 [Rxd1] 23.Rxd1 [Rf6] 24.Rd8+ Kh7 25.Qg8+ Nxg8 26.Rxg8 Qxe5 27.Rxg7+ [Kxg7] 28.g3 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.Bb5%20e5%204.O-O%20Bd6%205.c3%20a6%206.Bxc6%20dxc6%207.d4%20cxd4%208.cxd4%20exd4%209.Qxd4%20Bf8%2010.Qc3%20Nf6%2011.Bg5%20Be7%2012.Nbd2%20O-O%2013.Rad1%20Qc7%2014.e5%20Nd5%2015.Qc2%20h6%2016.Bxe7%20Nxe7%2017.Ne4%20Bf5%2018.Qe2%20Bxe4%2019.Qxe4%20Rad8%2020.e6%20fxe6%2021.Qxe6%2B%20Kh8%2022.Ne5%20Rxd1%2023.Rxd1%20Rf6%2024.Rd8%2B%20Kh7%2025.Qg8%2B%20Nxg8%2026.Rxg8%20Kxg8%2027.Nxc6%20Qxc6%2028.b4#39) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.Bb5%20e5%204.O-O%20Bd6%205.c3%20a6%206.Bxc6%20dxc6%207.d4%20cxd4%208.cxd4%20exd4%209.Qxd4%20Bf8%2010.Qc3%20Nf6%2011.Bg5%20Be7%2012.Nbd2%20O-O%2013.Rad1%20Qc7%2014.e5%20Nd5%2015.Qc2%20h6%2016.Bxe7%20Nxe7%2017.Ne4%20Bf5%2018.Qe2%20Bxe4%2019.Qxe4%20Rad8%2020.e6%20fxe6%2021.Qxe6%2B%20Kh8%2022.Ne5%20Rxd1%2023.Rxd1%20Rf6%2024.Rd8%2B%20Kh7%2025.Qg8%2B%20Nxg8%2026.Rxg8%20Qxe5%2027.Rxg7%2B%20Kxg7%2028.g3#39) |

#### W #5 (k = 0): latents 52

position 33 (`r2qk1r1/3bbpnp/p3N1p1/2ppB1P1/1p2P2P/1P3Q2/P1P2P2/2KR1B1R b q - 0 19`), split at ply 3: Nc7 (51% there) vs Nd4 (49%)

| chosen | subpar |
|---|---|
| 19...Nxe6 20.exd5 [Nc7] 21.d6 Ne6 22.dxe7 [Qxe7] 23.Qxa8+ Nd8 24.Bxa6 Qxe5 [25.Rhe1] Qxe1 26.Rxe1+ [Kf8] [27.Qxd8+] | 19...Nxe6 20.exd5 Nd4 21.Bxd4 [cxd4] 22.Rxd4 [a5] [23.Bc4] a4 24.d6 [axb3] [25.Qxf7#] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.Bf4%20a6%204.e3%20e6%205.g4%20Bb4%206.Ne2%20Be7%207.g5%20Nh5%208.h4%20b5%209.Bh2%20Nc6%2010.Nc1%20g6%2011.Nb3%20Ng7%2012.Qf3%20b4%2013.Na4%20Bd7%2014.O-O-O%20Nxd4%2015.Nxd4%20Bxa4%2016.Be5%20Rg8%2017.e4%20c5%2018.b3%20Bd7%2019.Nxe6%20Nxe6%2020.exd5%20Nc7%2021.d6%20Ne6%2022.dxe7%20Qxe7%2023.Qxa8%2B%20Nd8%2024.Bxa6%20Qxe5%2025.Rhe1%20Qxe1%2026.Rxe1%2B%20Kf8%2027.Qxd8%2B#37) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.Bf4%20a6%204.e3%20e6%205.g4%20Bb4%206.Ne2%20Be7%207.g5%20Nh5%208.h4%20b5%209.Bh2%20Nc6%2010.Nc1%20g6%2011.Nb3%20Ng7%2012.Qf3%20b4%2013.Na4%20Bd7%2014.O-O-O%20Nxd4%2015.Nxd4%20Bxa4%2016.Be5%20Rg8%2017.e4%20c5%2018.b3%20Bd7%2019.Nxe6%20Nxe6%2020.exd5%20Nd4%2021.Bxd4%20cxd4%2022.Rxd4%20a5%2023.Bc4%20a4%2024.d6%20axb3%2025.Qxf7%23#37) |

position 0 (`2kr2r1/ppp5/2n1RbNp/2q2p1P/3p4/2PQ1P1B/PPKN3P/6R1 b - - 0 20`), split at ply 12: Ke3 (52% there) vs Kc4 (48%)

| chosen | subpar |
|---|---|
| [20...dxc3] 21.bxc3 [Rxd3] 22.Kxd3 Qxg1 23.Bxf5 Qxh2 24.Rxf6+ Kb8 25.Ne4 Rd8+ [26.Ke3] Qg1+ 27.Kf4 Qh2+ [28.Ke3] | [20...dxc3] 21.bxc3 [Rxd3] 22.Kxd3 Qxg1 23.Bxf5 Qxh2 24.Rxf6+ Kb8 25.Ne4 Rd8+ 26.Kc4 Ne5+ 27.Kb3 [Nxf3] 28.Rf7 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.bxc3%20Rxd3%2022.Kxd3%20Qxg1%2023.Bxf5%20Qxh2%2024.Rxf6%2B%20Kb8%2025.Ne4%20Rd8%2B%2026.Ke3%20Qg1%2B%2027.Kf4%20Qh2%2B%2028.Ke3#39) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.bxc3%20Rxd3%2022.Kxd3%20Qxg1%2023.Bxf5%20Qxh2%2024.Rxf6%2B%20Kb8%2025.Ne4%20Rd8%2B%2026.Kc4%20Ne5%2B%2027.Kb3%20Nxf3%2028.Rf7#39) |

position 34 (`r2qk2r/1pp1bppp/2n1p3/1p6/3PR3/P1P2N2/5PPP/R2Q2K1 b kq - 0 14`), split at ply 4: Qc2 (50% there) vs Qxd5 (48%)

| chosen | subpar |
|---|---|
| 14...O-O 15.Qb3 [Qd5] [16.Qc2] [Bxa3] 17.Rh4 [h6] 18.Ne5 Nxe5 19.dxe5 Qxe5 20.Rh3 [Bd6] 21.g3 [Rxa1+] 22.Kg2 | 14...O-O 15.Qb3 [Qd5] 16.Qxd5 [exd5] 17.Re3 [Rfe8] 18.Rb1 [Rxa3] [19.Rxb5] Ra1+ [20.Re1] Rxe1+ [21.Nxe1] [b6] 22.Rxd5 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20O-O%2015.Qb3%20Qd5%2016.Qc2%20Bxa3%2017.Rh4%20h6%2018.Ne5%20Nxe5%2019.dxe5%20Qxe5%2020.Rh3%20Bd6%2021.g3%20Rxa1%2B%2022.Kg2#27) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20O-O%2015.Qb3%20Qd5%2016.Qxd5%20exd5%2017.Re3%20Rfe8%2018.Rb1%20Rxa3%2019.Rxb5%20Ra1%2B%2020.Re1%20Rxe1%2B%2021.Nxe1%20b6%2022.Rxd5#27) |

#### W #6 (k = 0): latents 3714

position 15 (`r1q2rk1/2B2ppp/p1Q1p3/3p4/3Pn3/P3P3/P1P2PPP/R4RK1 b - - 4 17`), split at ply 5: Nd2 (51% there) vs Nc3 (49%)

| chosen | subpar |
|---|---|
| 17...Ra7 18.f3 Rxc7 [19.Qa4] [Nd2] 20.Rfd1 Nc4 [21.e4] Nb2 22.Qb3 Nxd1 23.Rxd1 Rxc2 24.exd5 exd5 25.Qxd5 | 17...Ra7 18.f3 Rxc7 [19.Qa4] Nc3 20.Qb3 [Ne2+] 21.Kf2 Rxc2 22.Ke1 Nc3 23.Rf2 Rxf2 [24.Kxf2] Nb5 25.a4 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bf4%20d6%203.e3%20Nc6%204.Bb5%20Bd7%205.Bxc6%20Bxc6%206.Nf3%20Bxf3%207.Qxf3%20e6%208.Qxb7%20d5%209.Bxc7%20Qc8%2010.Qc6%2B%20Nd7%2011.Na3%20Be7%2012.Nb5%20O-O%2013.Qc3%20a6%2014.Na3%20Bxa3%2015.bxa3%20Nf6%2016.O-O%20Ne4%2017.Qc6%20Ra7%2018.f3%20Rxc7%2019.Qa4%20Nd2%2020.Rfd1%20Nc4%2021.e4%20Nb2%2022.Qb3%20Nxd1%2023.Rxd1%20Rxc2%2024.exd5%20exd5%2025.Qxd5#33) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bf4%20d6%203.e3%20Nc6%204.Bb5%20Bd7%205.Bxc6%20Bxc6%206.Nf3%20Bxf3%207.Qxf3%20e6%208.Qxb7%20d5%209.Bxc7%20Qc8%2010.Qc6%2B%20Nd7%2011.Na3%20Be7%2012.Nb5%20O-O%2013.Qc3%20a6%2014.Na3%20Bxa3%2015.bxa3%20Nf6%2016.O-O%20Ne4%2017.Qc6%20Ra7%2018.f3%20Rxc7%2019.Qa4%20Nc3%2020.Qb3%20Ne2%2B%2021.Kf2%20Rxc2%2022.Ke1%20Nc3%2023.Rf2%20Rxf2%2024.Kxf2%20Nb5%2025.a4#33) |

position 44 (`6rr/ppkn3p/8/2pQ4/5Bb1/3B3P/PqP5/2R2KNR b - - 0 24`), split at ply 5: Ke7 (52% there) vs Ke8 (48%)

| chosen | subpar |
|---|---|
| 24...Kd8 25.Qd6 Rf8 26.Qc7+ [Ke7] 27.Qd6+ Kd8 [28.Qc7+] Ke7 29.Qd6+ [Kd8] [30.Qc7+] Ke7 [31.Qd6+] [Kd8] [32.Qc7+] | 24...Kd8 25.Qd6 Rf8 26.Qc7+ Ke8 27.Re1+ [Kf7] 28.Bc4+ Kg7 29.Qxd7+ Bxd7 30.Re7+ Kf6 31.Rxd7 [Qxc2] [32.Rd6+] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Bc4%20fxe4%204.d3%20d5%205.Bb3%20exd3%206.Qxd3%20e4%207.Qd4%20Nf6%208.Nc3%20c5%209.Qe5%2B%20Be7%2010.Nxd5%20Nxd5%2011.Bxd5%20Qa5%2B%2012.Bd2%20Qb6%2013.Qxg7%20Bf6%2014.Qf7%2B%20Kd8%2015.Bxe4%20Bg4%2016.Qd5%2B%20Nd7%2017.h3%20Bh4%2B%2018.g3%20Bxg3%2B%2019.Kf1%20Qb5%2B%2020.Bd3%20Qxb2%2021.Qg5%2B%20Kc7%2022.Rc1%20Rag8%2023.Qd5%20Bxf4%2024.Bxf4%2B%20Kd8%2025.Qd6%20Rf8%2026.Qc7%2B%20Ke7%2027.Qd6%2B%20Kd8%2028.Qc7%2B%20Ke7%2029.Qd6%2B%20Kd8%2030.Qc7%2B%20Ke7%2031.Qd6%2B%20Kd8%2032.Qc7%2B#47) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Bc4%20fxe4%204.d3%20d5%205.Bb3%20exd3%206.Qxd3%20e4%207.Qd4%20Nf6%208.Nc3%20c5%209.Qe5%2B%20Be7%2010.Nxd5%20Nxd5%2011.Bxd5%20Qa5%2B%2012.Bd2%20Qb6%2013.Qxg7%20Bf6%2014.Qf7%2B%20Kd8%2015.Bxe4%20Bg4%2016.Qd5%2B%20Nd7%2017.h3%20Bh4%2B%2018.g3%20Bxg3%2B%2019.Kf1%20Qb5%2B%2020.Bd3%20Qxb2%2021.Qg5%2B%20Kc7%2022.Rc1%20Rag8%2023.Qd5%20Bxf4%2024.Bxf4%2B%20Kd8%2025.Qd6%20Rf8%2026.Qc7%2B%20Ke8%2027.Re1%2B%20Kf7%2028.Bc4%2B%20Kg7%2029.Qxd7%2B%20Bxd7%2030.Re7%2B%20Kf6%2031.Rxd7%20Qxc2%2032.Rd6%2B#47) |

position 21 (`r1b2rk1/pp2q1pp/3b4/5p1Q/4p3/2N5/PPP2PPP/R1BR2K1 w - - 2 17`), split at ply 6: Qf6 (53% there) vs Qc5 (47%)

| chosen | subpar |
|---|---|
| 17.Bg5 [Qe5] [18.g3] [Be6] 19.Bf4 [Qf6] 20.Bxd6 Rfd8 21.Bf4 Rxd1+ [22.Rxd1] Rd8 23.Rxd8+ Qxd8 24.Qg5 Qxg5 | 17.Bg5 [Qe5] [18.g3] [Be6] 19.Bf4 Qc5 20.Bxd6 [Rad8] 21.Bxc5 [Rxd1+] 22.Rxd1 e3 23.Bxf8 [exf2+] 24.Kxf2 Kxf8 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Qxd4%20Nf6%205.e5%20Nfd7%206.exd6%20Nc6%207.Qe3%20e6%208.Nc3%20Bxd6%209.Bd3%20O-O%2010.O-O%20Nde5%2011.Nxe5%20Nxe5%2012.Be4%20f5%2013.Bf3%20Nxf3%2B%2014.Qxf3%20e5%2015.Rd1%20e4%2016.Qh5%20Qe7%2017.Bg5%20Qe5%2018.g3%20Be6%2019.Bf4%20Qf6%2020.Bxd6%20Rfd8%2021.Bf4%20Rxd1%2B%2022.Rxd1%20Rd8%2023.Rxd8%2B%20Qxd8%2024.Qg5%20Qxg5#32) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Qxd4%20Nf6%205.e5%20Nfd7%206.exd6%20Nc6%207.Qe3%20e6%208.Nc3%20Bxd6%209.Bd3%20O-O%2010.O-O%20Nde5%2011.Nxe5%20Nxe5%2012.Be4%20f5%2013.Bf3%20Nxf3%2B%2014.Qxf3%20e5%2015.Rd1%20e4%2016.Qh5%20Qe7%2017.Bg5%20Qe5%2018.g3%20Be6%2019.Bf4%20Qc5%2020.Bxd6%20Rad8%2021.Bxc5%20Rxd1%2B%2022.Rxd1%20e3%2023.Bxf8%20exf2%2B%2024.Kxf2%20Kxf8#32) |

#### W #7 (k = 0): latents 2234

position 34 (`r2qk2r/1pp1bppp/2n1p3/1p6/3PR3/P1P2N2/5PPP/R2Q2K1 b kq - 0 14`), split at ply 4: Qc2 (50% there) vs Qxd5 (48%)

| chosen | subpar |
|---|---|
| 14...O-O [15.Qb3] Qd5 [16.Qc2] Bxa3 [17.Rh4] h6 18.Ne5 Nxe5 19.dxe5 [Qxe5] 20.Rh3 Bd6 21.g3 [Rxa1+] 22.Kg2 | 14...O-O [15.Qb3] Qd5 16.Qxd5 exd5 17.Re3 Rfe8 18.Rb1 Rxa3 19.Rxb5 Ra1+ 20.Re1 Rxe1+ 21.Nxe1 b6 22.Rxd5 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20O-O%2015.Qb3%20Qd5%2016.Qc2%20Bxa3%2017.Rh4%20h6%2018.Ne5%20Nxe5%2019.dxe5%20Qxe5%2020.Rh3%20Bd6%2021.g3%20Rxa1%2B%2022.Kg2#27) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20O-O%2015.Qb3%20Qd5%2016.Qxd5%20exd5%2017.Re3%20Rfe8%2018.Rb1%20Rxa3%2019.Rxb5%20Ra1%2B%2020.Re1%20Rxe1%2B%2021.Nxe1%20b6%2022.Rxd5#27) |

position 3 (`2kr1b1r/ppp1pppp/5n2/8/3n1q2/1P1P1B1P/P1P2PP1/RNBQ1K1R b - - 0 11`), split at ply 3: Nxf3 (50% there) vs e6 (47%)

| chosen | subpar |
|---|---|
| 11...Qe5 12.g3 [Nxf3] 13.Qxf3 Qxa1 14.Kg2 Qxb1 15.Bf4 Qxc2 16.Rc1 Qxd3 17.Rxc7+ Kb8 18.Qxb7# | 11...Qe5 12.g3 e6 13.Kg2 Bd6 14.Bf4 Qc5 15.Bxd6 Rxd6 [16.Nd2] Nxc2 17.Rc1 Rxd3 [18.Rxc2] Qf5 [19.g4] |
| [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nc6%202.e4%20d5%203.exd5%20Qxd5%204.b3%20Bg4%205.Bc4%20Qe4%2B%206.Kf1%20Nd4%207.Bd3%20Qf4%208.Be2%20O-O-O%209.h3%20Bxf3%2010.Bxf3%20Nf6%2011.d3%20Qe5%2012.g3%20Nxf3%2013.Qxf3%20Qxa1%2014.Kg2%20Qxb1%2015.Bf4%20Qxc2%2016.Rc1%20Qxd3%2017.Rxc7%2B%20Kb8%2018.Qxb7%23#21) | [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nc6%202.e4%20d5%203.exd5%20Qxd5%204.b3%20Bg4%205.Bc4%20Qe4%2B%206.Kf1%20Nd4%207.Bd3%20Qf4%208.Be2%20O-O-O%209.h3%20Bxf3%2010.Bxf3%20Nf6%2011.d3%20Qe5%2012.g3%20e6%2013.Kg2%20Bd6%2014.Bf4%20Qc5%2015.Bxd6%20Rxd6%2016.Nd2%20Nxc2%2017.Rc1%20Rxd3%2018.Rxc2%20Qf5%2019.g4#21) |

position 25 (`1r3r2/pb4kp/1p4p1/2pnP3/4B3/2P4P/PP1N2P1/R4RK1 w - - 3 21`), split at ply 9: Nxe4 (53% there) vs Kxe3 (47%)

| chosen | subpar |
|---|---|
| [21.Rxf8] Rxf8 22.Rf1 Rxf1+ 23.Kxf1 Ne3+ [24.Ke2] Bxe4 [25.Nxe4] [Nxg2] 26.Kf3 Nh4+ 27.Kg4 Nf5 28.Nd6 [Nxd6] | [21.Rxf8] Rxf8 22.Rf1 Rxf1+ 23.Kxf1 Ne3+ [24.Ke2] Bxe4 25.Kxe3 Bxg2 26.h4 Kf7 [27.Ne4] Ke6 28.Kf4 Bxe4 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.Rxf8%20Rxf8%2022.Rf1%20Rxf1%2B%2023.Kxf1%20Ne3%2B%2024.Ke2%20Bxe4%2025.Nxe4%20Nxg2%2026.Kf3%20Nh4%2B%2027.Kg4%20Nf5%2028.Nd6%20Nxd6#40) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.Rxf8%20Rxf8%2022.Rf1%20Rxf1%2B%2023.Kxf1%20Ne3%2B%2024.Ke2%20Bxe4%2025.Kxe3%20Bxg2%2026.h4%20Kf7%2027.Ne4%20Ke6%2028.Kf4%20Bxe4#40) |

#### W #8 (k = 0): latents 689

position 46 (`1r1q1r2/pb3pkp/1n1p1Np1/2p5/1p4n1/3P4/PPPQ2BP/1RB2RK1 w - - 0 22`), split at ply 4: Kg8 (52% there) vs Kh8 (48%)

| chosen | subpar |
|---|---|
| 22.Nxg4 Bxg2 23.Qh6+ [Kg8] [24.Nf6+] [Kh8] [25.Qxh7#] | 22.Nxg4 Bxg2 23.Qh6+ Kh8 24.Kxg2 [Nd5] 25.Bg5 [Qd7] 26.Nf6 [Nxf6] 27.Bxf6+ [Kg8] [28.Qg7#] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nc3%20Nc6%203.g3%20g6%204.Bg2%20Bg7%205.Nge2%20d6%206.O-O%20e6%207.f4%20Nge7%208.g4%20O-O%209.Ng3%20Rb8%2010.d3%20b5%2011.Rb1%20b4%2012.Nce2%20Bb7%2013.f5%20Nc8%2014.Nf4%20exf5%2015.exf5%20Nb6%2016.Ne4%20Ne5%2017.f6%20Bxf6%2018.Nh5%20Bh8%2019.Nhf6%2B%20Bxf6%2020.Nxf6%2B%20Kg7%2021.Qd2%20Nxg4%2022.Nxg4%20Bxg2%2023.Qh6%2B%20Kg8%2024.Nf6%2B%20Kh8%2025.Qxh7%23#42) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nc3%20Nc6%203.g3%20g6%204.Bg2%20Bg7%205.Nge2%20d6%206.O-O%20e6%207.f4%20Nge7%208.g4%20O-O%209.Ng3%20Rb8%2010.d3%20b5%2011.Rb1%20b4%2012.Nce2%20Bb7%2013.f5%20Nc8%2014.Nf4%20exf5%2015.exf5%20Nb6%2016.Ne4%20Ne5%2017.f6%20Bxf6%2018.Nh5%20Bh8%2019.Nhf6%2B%20Bxf6%2020.Nxf6%2B%20Kg7%2021.Qd2%20Nxg4%2022.Nxg4%20Bxg2%2023.Qh6%2B%20Kh8%2024.Kxg2%20Nd5%2025.Bg5%20Qd7%2026.Nf6%20Nxf6%2027.Bxf6%2B%20Kg8%2028.Qg7%23#42) |

position 26 (`r1b1r1k1/2p3bp/2p2pq1/2Np4/p5P1/P1Q1B3/1PP2P1P/1K1R2R1 w - - 3 24`), split at ply 1: h4 (48% there) vs g5 (47%)

| chosen | subpar |
|---|---|
| [24.h4] f5 25.h5 [Qf7] 26.gxf5 Qxf5 27.Qxg7# | 24.g5 fxg5 25.Rxg5 Qh6 26.Rxg7+ [Qxg7] 27.Qxg7+ [Kxg7] 28.Rg1+ [Kh8] 29.Bd4+ Re5 30.Bxe5# |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.h4%20f5%2025.h5%20Qf7%2026.gxf5%20Qxf5%2027.Qxg7%23#46) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.g5%20fxg5%2025.Rxg5%20Qh6%2026.Rxg7%2B%20Qxg7%2027.Qxg7%2B%20Kxg7%2028.Rg1%2B%20Kh8%2029.Bd4%2B%20Re5%2030.Bxe5%23#46) |

position 0 (`2kr2r1/ppp5/2n1RbNp/2q2p1P/3p4/2PQ1P1B/PPKN3P/6R1 b - - 0 20`), split at ply 15: Qxa2+ (53% there) vs Rgd8 (47%)

| chosen | subpar |
|---|---|
| 20...dxc3 [21.bxc3] [Nb4+] [22.Kb3] [Nxd3] 23.Rxf6 Qxg1 24.Bxf5+ Kb8 [25.Bxd3] [Rxd3] 26.Ne4 [Qb1+] 27.Kc4 [Qxa2+] [28.Kxd3] | 20...dxc3 [21.bxc3] [Nb4+] [22.Kb3] [Nxd3] 23.Rxf6 Qxg1 24.Bxf5+ Kb8 [25.Bxd3] [Rxd3] 26.Ne4 [Qb1+] 27.Kc4 Rgd8 [28.Ne7] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.bxc3%20Nb4%2B%2022.Kb3%20Nxd3%2023.Rxf6%20Qxg1%2024.Bxf5%2B%20Kb8%2025.Bxd3%20Rxd3%2026.Ne4%20Qb1%2B%2027.Kc4%20Qxa2%2B%2028.Kxd3#39) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.bxc3%20Nb4%2B%2022.Kb3%20Nxd3%2023.Rxf6%20Qxg1%2024.Bxf5%2B%20Kb8%2025.Bxd3%20Rxd3%2026.Ne4%20Qb1%2B%2027.Kc4%20Rgd8%2028.Ne7#39) |

#### W #9 (k = 0): latents 9134

position 35 (`3rr1k1/ppp2pp1/5b1p/8/2qP4/7P/PP3PKP/R2Q2R1 w - - 4 21`), split at ply 5: Qg3 (52% there) vs Qxb7 (48%)

| chosen | subpar |
|---|---|
| 21.Kh1 Rxd4 [22.Qf3] Rf4 [23.Qg3] Qe4+ 24.Rg2 Rf3 25.Qxc7 Rxf2 [26.Rg1] Rxg2 27.Rxg2 Qe1+ 28.Rg1 Qe4+ | 21.Kh1 Rxd4 [22.Qf3] Rf4 23.Qxb7 Rxf2 24.Qxa7 [Qe4+] 25.Rg2 Qxg2# |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nc3%20Nf6%203.d4%20exd4%204.Qxd4%20Nc6%205.Qd1%20d6%206.Bb5%20Be7%207.Bg5%20h6%208.Bxf6%20Bxf6%209.Qf3%20O-O%2010.Nh3%20Nd4%2011.Qd1%20Bxh3%2012.gxh3%20d5%2013.exd5%20Qd6%2014.Be2%20Rfe8%2015.Ne4%20Rxe4%2016.c3%20Rxe2%2B%2017.Kf1%20Ree8%2018.cxd4%20Qxd5%2019.Rg1%20Qc4%2B%2020.Kg2%20Rad8%2021.Kh1%20Rxd4%2022.Qf3%20Rf4%2023.Qg3%20Qe4%2B%2024.Rg2%20Rf3%2025.Qxc7%20Rxf2%2026.Rg1%20Rxg2%2027.Rxg2%20Qe1%2B%2028.Rg1%20Qe4%2B#40) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nc3%20Nf6%203.d4%20exd4%204.Qxd4%20Nc6%205.Qd1%20d6%206.Bb5%20Be7%207.Bg5%20h6%208.Bxf6%20Bxf6%209.Qf3%20O-O%2010.Nh3%20Nd4%2011.Qd1%20Bxh3%2012.gxh3%20d5%2013.exd5%20Qd6%2014.Be2%20Rfe8%2015.Ne4%20Rxe4%2016.c3%20Rxe2%2B%2017.Kf1%20Ree8%2018.cxd4%20Qxd5%2019.Rg1%20Qc4%2B%2020.Kg2%20Rad8%2021.Kh1%20Rxd4%2022.Qf3%20Rf4%2023.Qxb7%20Rxf2%2024.Qxa7%20Qe4%2B%2025.Rg2%20Qxg2%23#40) |

position 24 (`3r2k1/pp4p1/2n1b2p/8/3p2q1/8/PPQB1PP1/4RRK1 w - - 2 25`), split at ply 14: Ng3+ (52% there) vs g5 (48%)

| chosen | subpar |
|---|---|
| 25.f3 Qg3 26.Rxe6 [d3] 27.Qc4 Nd4 28.Re8+ Kh7 29.Rxd8 Ne2+ 30.Kh1 Qh4+ 31.Qxh4 [Ng3+] [32.Qxg3] g5 | 25.f3 Qg3 26.Rxe6 [d3] 27.Qc4 Nd4 28.Re8+ Kh7 29.Rxd8 Ne2+ 30.Kh1 Qh4+ 31.Qxh4 g5 32.Qe4+ Kg7 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e6%202.d4%20d5%203.Nd2%20Nf6%204.e5%20Nfd7%205.Bd3%20c5%206.c3%20Nc6%207.Ne2%20cxd4%208.cxd4%20f6%209.exf6%20Qxf6%2010.Nf3%20h6%2011.O-O%20Bd6%2012.Ng3%20O-O%2013.Bd2%20e5%2014.dxe5%20Ndxe5%2015.Nxe5%20Bxe5%2016.Qc2%20Be6%2017.Rae1%20Rae8%2018.Nh5%20Bxh2%2B%2019.Kxh2%20Qh4%2B%2020.Kg1%20Qxh5%2021.Bg6%20Qg4%2022.Bxe8%20Rxe8%2023.Bc3%20d4%2024.Bd2%20Rd8%2025.f3%20Qg3%2026.Rxe6%20d3%2027.Qc4%20Nd4%2028.Re8%2B%20Kh7%2029.Rxd8%20Ne2%2B%2030.Kh1%20Qh4%2B%2031.Qxh4%20Ng3%2B%2032.Qxg3%20g5#48) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e6%202.d4%20d5%203.Nd2%20Nf6%204.e5%20Nfd7%205.Bd3%20c5%206.c3%20Nc6%207.Ne2%20cxd4%208.cxd4%20f6%209.exf6%20Qxf6%2010.Nf3%20h6%2011.O-O%20Bd6%2012.Ng3%20O-O%2013.Bd2%20e5%2014.dxe5%20Ndxe5%2015.Nxe5%20Bxe5%2016.Qc2%20Be6%2017.Rae1%20Rae8%2018.Nh5%20Bxh2%2B%2019.Kxh2%20Qh4%2B%2020.Kg1%20Qxh5%2021.Bg6%20Qg4%2022.Bxe8%20Rxe8%2023.Bc3%20d4%2024.Bd2%20Rd8%2025.f3%20Qg3%2026.Rxe6%20d3%2027.Qc4%20Nd4%2028.Re8%2B%20Kh7%2029.Rxd8%20Ne2%2B%2030.Kh1%20Qh4%2B%2031.Qxh4%20g5%2032.Qe4%2B%20Kg7#48) |

position 0 (`2kr2r1/ppp5/2n1RbNp/2q2p1P/3p4/2PQ1P1B/PPKN3P/6R1 b - - 0 20`), split at ply 15: Qd5+ (52% there) vs Na5+ (48%)

| chosen | subpar |
|---|---|
| 20...dxc3 21.bxc3 Rxd3 22.Kxd3 Qxg1 23.Bxf5 [Rd8+] 24.Kc2 Qxh2 25.Rxf6+ Kb8 26.Rf7 Qxd2+ 27.Kb3 [Qd5+] 28.Kc2 | 20...dxc3 21.bxc3 Rxd3 22.Kxd3 Qxg1 23.Bxf5 [Rd8+] 24.Kc2 Qxh2 25.Rxf6+ Kb8 26.Rf7 Qxd2+ 27.Kb3 Na5+ 28.Kb4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.bxc3%20Rxd3%2022.Kxd3%20Qxg1%2023.Bxf5%20Rd8%2B%2024.Kc2%20Qxh2%2025.Rxf6%2B%20Kb8%2026.Rf7%20Qxd2%2B%2027.Kb3%20Qd5%2B%2028.Kc2#39) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.bxc3%20Rxd3%2022.Kxd3%20Qxg1%2023.Bxf5%20Rd8%2B%2024.Kc2%20Qxh2%2025.Rxf6%2B%20Kb8%2026.Rf7%20Qxd2%2B%2027.Kb3%20Na5%2B%2028.Kb4#39) |

#### W #10 (k = 0): latents 3356

position 9 (`1k2r3/Rpp1qp1p/3pbb2/8/5Qr1/3PBN2/1PP1BPPP/5RK1 w - - 3 19`), split at ply 1: Qh6 (51% there) vs Qa4 (49%)

| chosen | subpar |
|---|---|
| [19.Qh6] Rg6 20.Qxh7 [Rh8] 21.Qxh8+ Bxh8 22.Rfa1 b6 23.Ra8+ Kb7 24.R1a7+ Kc6 25.Nd4+ Bxd4 26.Bxd4 Qg5 | 19.Qa4 Rxa4 20.Rxa4 Bxb2 21.Ba7+ Kc8 22.Be3 Bd7 23.Ra8# |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Qh5%20Nf6%203.Qxe5%2B%20Be7%204.d3%20Nc6%205.Qg5%20Nxe4%206.Qxg7%20Bf6%207.Qg4%20d6%208.Qxe4%2B%20Be6%209.Nf3%20Qd7%2010.Nc3%20O-O-O%2011.Be2%20Rde8%2012.O-O%20Bxa2%2013.Qa4%20Be6%2014.Qf4%20Qe7%2015.Nb5%20Rhg8%2016.Nxa7%2B%20Nxa7%2017.Rxa7%20Kb8%2018.Be3%20Rg4%2019.Qh6%20Rg6%2020.Qxh7%20Rh8%2021.Qxh8%2B%20Bxh8%2022.Rfa1%20b6%2023.Ra8%2B%20Kb7%2024.R1a7%2B%20Kc6%2025.Nd4%2B%20Bxd4%2026.Bxd4%20Qg5#36) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Qh5%20Nf6%203.Qxe5%2B%20Be7%204.d3%20Nc6%205.Qg5%20Nxe4%206.Qxg7%20Bf6%207.Qg4%20d6%208.Qxe4%2B%20Be6%209.Nf3%20Qd7%2010.Nc3%20O-O-O%2011.Be2%20Rde8%2012.O-O%20Bxa2%2013.Qa4%20Be6%2014.Qf4%20Qe7%2015.Nb5%20Rhg8%2016.Nxa7%2B%20Nxa7%2017.Rxa7%20Kb8%2018.Be3%20Rg4%2019.Qa4%20Rxa4%2020.Rxa4%20Bxb2%2021.Ba7%2B%20Kc8%2022.Be3%20Bd7%2023.Ra8%23#36) |

position 24 (`3r2k1/pp4p1/2n1b2p/8/3p2q1/8/PPQB1PP1/4RRK1 w - - 2 25`), split at ply 14: Ng3+ (52% there) vs g5 (48%)

| chosen | subpar |
|---|---|
| 25.f3 [Qg3] 26.Rxe6 d3 27.Qc4 [Nd4] 28.Re8+ Kh7 29.Rxd8 [Ne2+] 30.Kh1 Qh4+ 31.Qxh4 [Ng3+] 32.Qxg3 g5 | 25.f3 [Qg3] 26.Rxe6 d3 27.Qc4 [Nd4] 28.Re8+ Kh7 29.Rxd8 [Ne2+] 30.Kh1 Qh4+ 31.Qxh4 g5 [32.Qe4+] Kg7 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e6%202.d4%20d5%203.Nd2%20Nf6%204.e5%20Nfd7%205.Bd3%20c5%206.c3%20Nc6%207.Ne2%20cxd4%208.cxd4%20f6%209.exf6%20Qxf6%2010.Nf3%20h6%2011.O-O%20Bd6%2012.Ng3%20O-O%2013.Bd2%20e5%2014.dxe5%20Ndxe5%2015.Nxe5%20Bxe5%2016.Qc2%20Be6%2017.Rae1%20Rae8%2018.Nh5%20Bxh2%2B%2019.Kxh2%20Qh4%2B%2020.Kg1%20Qxh5%2021.Bg6%20Qg4%2022.Bxe8%20Rxe8%2023.Bc3%20d4%2024.Bd2%20Rd8%2025.f3%20Qg3%2026.Rxe6%20d3%2027.Qc4%20Nd4%2028.Re8%2B%20Kh7%2029.Rxd8%20Ne2%2B%2030.Kh1%20Qh4%2B%2031.Qxh4%20Ng3%2B%2032.Qxg3%20g5#48) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e6%202.d4%20d5%203.Nd2%20Nf6%204.e5%20Nfd7%205.Bd3%20c5%206.c3%20Nc6%207.Ne2%20cxd4%208.cxd4%20f6%209.exf6%20Qxf6%2010.Nf3%20h6%2011.O-O%20Bd6%2012.Ng3%20O-O%2013.Bd2%20e5%2014.dxe5%20Ndxe5%2015.Nxe5%20Bxe5%2016.Qc2%20Be6%2017.Rae1%20Rae8%2018.Nh5%20Bxh2%2B%2019.Kxh2%20Qh4%2B%2020.Kg1%20Qxh5%2021.Bg6%20Qg4%2022.Bxe8%20Rxe8%2023.Bc3%20d4%2024.Bd2%20Rd8%2025.f3%20Qg3%2026.Rxe6%20d3%2027.Qc4%20Nd4%2028.Re8%2B%20Kh7%2029.Rxd8%20Ne2%2B%2030.Kh1%20Qh4%2B%2031.Qxh4%20g5%2032.Qe4%2B%20Kg7#48) |

position 26 (`r1b1r1k1/2p3bp/2p2pq1/2Np4/p5P1/P1Q1B3/1PP2P1P/1K1R2R1 w - - 3 24`), split at ply 6: hxg6 (53% there) vs h6 (47%)

| chosen | subpar |
|---|---|
| 24.g5 [f5] 25.Qd3 Qd6 26.g6 [hxg6] 27.h4 [Kf7] 28.h5 [gxh5] 29.Rg5 Rh8 30.Rxf5+ [Bxf5] 31.Qxf5+ [Bf6] | 24.g5 [f5] 25.Qd3 Qd6 26.g6 h6 27.Nxa4 Ba6 28.Qxf5 Re5 [29.Qf7+] [Kh8] 30.Bf4 Rf8 31.Qxf8+ Bxf8 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.g5%20f5%2025.Qd3%20Qd6%2026.g6%20hxg6%2027.h4%20Kf7%2028.h5%20gxh5%2029.Rg5%20Rh8%2030.Rxf5%2B%20Bxf5%2031.Qxf5%2B%20Bf6#46) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.g5%20f5%2025.Qd3%20Qd6%2026.g6%20h6%2027.Nxa4%20Ba6%2028.Qxf5%20Re5%2029.Qf7%2B%20Kh8%2030.Bf4%20Rf8%2031.Qxf8%2B%20Bxf8#46) |

