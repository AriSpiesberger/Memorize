# Dynamic concepts with a persistence window

Per model, at 50 positions (1024 rollouts of 16 plies, T = 0.4, the model both colours): a latent on at a ply when z > 0.5 x mu_j. Pairs: at each branching point the most-played move against every move with >= 2% of that point's weight, each by its most frequent line, <= 50 per position. LP: min |v|_1 + 2.0 xi s.t. v . (z^c_tau - z^s_tau) >= 1 - xi for tau = t..t+k. Families: Jaccard >= 0.5 of supports with a family's core, within one half (25 / 25 positions by game); recurrence: the share of the other half's pairs (same k) where the family's mean v (|v|_1 = 1) gives >= 0.5 on every ply of the window; null: 200 random v's per family on rate-matched latents (firing-rate deciles). Persistence: plies in a row from the split with v . d >= 0.5, median over the other half's k = 0 pairs where it is on at the split.

## S

| k | pairs | nonzero v | families | held-out recurrence: median / 90% / max | null 95th: median | null (every draw): 90% / 99% | families above their null 95th (chance: 5%) |
|---|---|---|---|---|---|---|---|
| 0 | 1247 | 100% | 441 | 0.6% / 2.7% / 8.5% | 2.1% | 2.4% / 6.1% | 23 (5%) |
| 2 | 1217 | 32% | 327 | 0.0% / 0.2% / 2.5% | 0.0% | 0.0% / 0.3% | 27 (8%) |
| 4 | 1122 | 16% | 153 | 0.0% / 0.0% / 0.7% | 0.0% | 0.0% / 0.2% | 10 (7%) |
| 6 | 995 | 13% | 114 | 0.0% / 0.2% / 0.8% | 0.0% | 0.0% / 0.2% | 15 (13%) |

### S: the top 20 families by held-out recurrence

| # | k | latents (weight) | found in | held out on | recurrence | null 95th | persistence (pairs on at split) | positions found |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 62 (1.00) | B (20 v's) | A | 8.5% | 5.1% | 1.0 (53) | 1, 2, 8, 10, 23, 30, 36, 42, 43, 44 |
| 2 | 0 | 499 (1.00) | A (3 v's) | B | 8.1% | 6.5% | 1.0 (50) | 5, 38, 46 |
| 3 | 0 | 140 (1.00) | B (10 v's) | A | 8.0% | 5.1% | 1.0 (50) | 12, 15, 21, 27, 42, 44, 48 |
| 4 | 0 | 778 (1.00) | B (1 v's) | A | 8.0% | 4.6% | 1.0 (50) | 42 |
| 5 | 0 | 1006 (1.00) | B (2 v's) | A | 7.3% | 5.3% | 1.0 (46) | 22, 36 |
| 6 | 0 | 327 (1.00) | A (4 v's) | B | 6.9% | 5.3% | 1.0 (43) | 16, 18, 20 |
| 7 | 0 | 62 (1.00) | A (37 v's) | B | 6.0% | 6.0% | 1.0 (37) | 0, 3, 5, 6, 7, 9, 11, 18, 26, 28, 29, 33 ... |
| 8 | 0 | 1006 (1.00) | A (1 v's) | B | 5.8% | 6.0% | 1.0 (36) | 20 |
| 9 | 0 | 425 (1.00) | A (3 v's) | B | 5.6% | 6.0% | 1.0 (35) | 3, 26 |
| 10 | 0 | 1451 (1.00) | A (1 v's) | B | 5.5% | 6.6% | 1.0 (34) | 18 |
| 11 | 0 | 700 (1.00) | A (1 v's) | B | 5.3% | 5.7% | 1.0 (33) | 34 |
| 12 | 0 | 642 (1.00) | A (1 v's) | B | 5.2% | 6.1% | 1.0 (32) | 34 |
| 13 | 0 | 217 (1.00) | B (8 v's) | A | 5.1% | 5.6% | 1.0 (32) | 12, 14, 15, 17, 30, 41 |
| 14 | 0 | 140 (1.00) | A (16 v's) | B | 5.0% | 5.3% | 1.0 (31) | 0, 5, 11, 16, 18, 19, 28, 33, 35, 49 |
| 15 | 0 | 217 (1.00) | A (12 v's) | B | 4.8% | 6.1% | 1.0 (30) | 0, 3, 6, 16, 18, 19, 35, 45 |
| 16 | 0 | 327 (1.00) | B (2 v's) | A | 4.8% | 5.7% | 1.0 (30) | 21, 30 |
| 17 | 0 | 422 (1.00) | B (6 v's) | A | 4.5% | 6.2% | 1.0 (28) | 14, 22, 36, 39, 40, 43 |
| 18 | 0 | 2039 (1.00) | B (1 v's) | A | 4.3% | 5.9% | 1.0 (27) | 17 |
| 19 | 0 | 499 (1.00) | B (10 v's) | A | 4.1% | 5.6% | 1.0 (26) | 1, 8, 15, 17, 22, 23, 27, 40, 47 |
| 20 | 0 | 1930 (1.00) | B (1 v's) | A | 4.1% | 5.1% | 1.0 (26) | 1 |

#### S #1 (k = 0): latents 62

position 0 (`2kr2r1/ppp5/2n1RbNp/2q2p1P/3p4/2PQ1P1B/PPKN3P/6R1 b - - 0 20`), split at ply 10: Bxe6+ (75% there) vs Re1 (25%)

| chosen | subpar |
|---|---|
| 20...dxc3 21.Qxc3 Nd4+ 22.Kb1 Qxc3 [23.bxc3] Nxe6 [24.Bxf5] Rxd2 [25.Bxe6+] Kd8 [26.Bxg8] Bxc3 27.Bb3 a5 28.a4 | 20...dxc3 21.Qxc3 Nd4+ 22.Kb1 Qxc3 [23.bxc3] Nxe6 [24.Bxf5] Rxd2 25.Re1 Re8 26.f4 Rd6 27.Kc2 Kd8 28.a4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.Qxc3%20Nd4%2B%2022.Kb1%20Qxc3%2023.bxc3%20Nxe6%2024.Bxf5%20Rxd2%2025.Bxe6%2B%20Kd8%2026.Bxg8%20Bxc3%2027.Bb3%20a5%2028.a4#39) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.Qxc3%20Nd4%2B%2022.Kb1%20Qxc3%2023.bxc3%20Nxe6%2024.Bxf5%20Rxd2%2025.Re1%20Re8%2026.f4%20Rd6%2027.Kc2%20Kd8%2028.a4#39) |

position 35 (`3rr1k1/ppp2pp1/5b1p/8/2qP4/7P/PP3PKP/R2Q2R1 w - - 4 21`), split at ply 9: Qxd3 (78% there) vs Kg2 (22%)

| chosen | subpar |
|---|---|
| 21.Rc1 Qd5+ 22.Kf1 c6 23.Qg4 Qxd4 24.Qg3 Qd3+ [25.Qxd3] Rxd3 26.Rc2 Rxh3 27.Kg2 Rh5 28.Rd1 Rg5+ | 21.Rc1 Qd5+ 22.Kf1 c6 23.Qg4 Qxd4 24.Qg3 Qd3+ 25.Kg2 Qxg3+ [26.hxg3] Rd2 27.Rb1 Ree2 28.Rgf1 Bd4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nc3%20Nf6%203.d4%20exd4%204.Qxd4%20Nc6%205.Qd1%20d6%206.Bb5%20Be7%207.Bg5%20h6%208.Bxf6%20Bxf6%209.Qf3%20O-O%2010.Nh3%20Nd4%2011.Qd1%20Bxh3%2012.gxh3%20d5%2013.exd5%20Qd6%2014.Be2%20Rfe8%2015.Ne4%20Rxe4%2016.c3%20Rxe2%2B%2017.Kf1%20Ree8%2018.cxd4%20Qxd5%2019.Rg1%20Qc4%2B%2020.Kg2%20Rad8%2021.Rc1%20Qd5%2B%2022.Kf1%20c6%2023.Qg4%20Qxd4%2024.Qg3%20Qd3%2B%2025.Qxd3%20Rxd3%2026.Rc2%20Rxh3%2027.Kg2%20Rh5%2028.Rd1%20Rg5%2B#40) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nc3%20Nf6%203.d4%20exd4%204.Qxd4%20Nc6%205.Qd1%20d6%206.Bb5%20Be7%207.Bg5%20h6%208.Bxf6%20Bxf6%209.Qf3%20O-O%2010.Nh3%20Nd4%2011.Qd1%20Bxh3%2012.gxh3%20d5%2013.exd5%20Qd6%2014.Be2%20Rfe8%2015.Ne4%20Rxe4%2016.c3%20Rxe2%2B%2017.Kf1%20Ree8%2018.cxd4%20Qxd5%2019.Rg1%20Qc4%2B%2020.Kg2%20Rad8%2021.Rc1%20Qd5%2B%2022.Kf1%20c6%2023.Qg4%20Qxd4%2024.Qg3%20Qd3%2B%2025.Kg2%20Qxg3%2B%2026.hxg3%20Rd2%2027.Rb1%20Ree2%2028.Rgf1%20Bd4#40) |

position 26 (`r1b1r1k1/2p3bp/2p2pq1/2Np4/p5P1/P1Q1B3/1PP2P1P/1K1R2R1 w - - 3 24`), split at ply 9: Qxf6+ (78% there) vs Bd4 (22%)

| chosen | subpar |
|---|---|
| 24.h4 h5 [25.gxh5] Qxh5 [26.Rxg7+] Kxg7 27.Rg1+ Kf7 [28.Qxf6+] Kxf6 29.Bd4+ Kf7 30.Rg7+ Kf8 31.Rg5 Qd1+ | 24.h4 h5 [25.gxh5] Qxh5 [26.Rxg7+] Kxg7 27.Rg1+ Kf7 28.Bd4 Qf5 29.Qg3 Be6 [30.Qxc7+] Re7 [31.Qxc6] Rc8 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.h4%20h5%2025.gxh5%20Qxh5%2026.Rxg7%2B%20Kxg7%2027.Rg1%2B%20Kf7%2028.Qxf6%2B%20Kxf6%2029.Bd4%2B%20Kf7%2030.Rg7%2B%20Kf8%2031.Rg5%20Qd1%2B#46) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.h4%20h5%2025.gxh5%20Qxh5%2026.Rxg7%2B%20Kxg7%2027.Rg1%2B%20Kf7%2028.Bd4%20Qf5%2029.Qg3%20Be6%2030.Qxc7%2B%20Re7%2031.Qxc6%20Rc8#46) |

#### S #2 (k = 0): latents 499

position 47 (`r2qr1k1/pp3ppp/1bn5/3p4/3Nb2n/1NP2PBP/PP2B1PK/R2Q1R2 b - - 0 16`), split at ply 9: a6 (75% there) vs Be6 (25%)

| chosen | subpar |
|---|---|
| [16...Bg6] 17.Bb5 [Rc8] 18.Qd2 Nf5 19.Nxf5 Bxf5 20.Rad1 [a6] [21.Bd3] [Be6] 22.Bb1 Qf6 23.Rfe1 Rcd8 24.Qc2 | [16...Bg6] 17.Bb5 [Rc8] 18.Qd2 Nf5 19.Nxf5 Bxf5 20.Rad1 Be6 21.Rfe1 [a6] [22.Bf1] Qf6 23.Qf4 Qg6 24.Bd3 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bg6%2017.Bb5%20Rc8%2018.Qd2%20Nf5%2019.Nxf5%20Bxf5%2020.Rad1%20a6%2021.Bd3%20Be6%2022.Bb1%20Qf6%2023.Rfe1%20Rcd8%2024.Qc2#31) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bg6%2017.Bb5%20Rc8%2018.Qd2%20Nf5%2019.Nxf5%20Bxf5%2020.Rad1%20Be6%2021.Rfe1%20a6%2022.Bf1%20Qf6%2023.Qf4%20Qg6%2024.Bd3#31) |

position 17 (`r3k2r/pp2qp1p/2n1bnp1/2p5/2N3P1/2bPBP2/P1PN3P/3QKB1R w Kkq - 1 14`), split at ply 5: Nxe3 (76% there) vs Kxe3 (24%)

| chosen | subpar |
|---|---|
| [14.Kf2] Nd5 [15.Ne4] [Nxe3] [16.Nxe3] Bd4 [17.c3] Bxe3+ 18.Kxe3 f5 [19.gxf5] gxf5 [20.Nf2] O-O-O [21.Kd2] Qg5+ | [14.Kf2] Nd5 [15.Ne4] [Nxe3] 16.Kxe3 [Bd4+] [17.Ke2] Bxc4 18.dxc4 f5 [19.gxf5] gxf5 [20.Bh3] fxe4 [21.Bf5] exf3+ |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.d3%20g6%203.Nf3%20Bg7%204.e5%20Nc6%205.Bf4%20d6%206.exd6%20Bxb2%207.dxe7%20Qxe7%2B%208.Be3%20Bxa1%209.Na3%20Bc3%2B%2010.Nd2%20Nf6%2011.Nc4%20Bg4%2012.f3%20Bf5%2013.g4%20Be6%2014.Kf2%20Nd5%2015.Ne4%20Nxe3%2016.Nxe3%20Bd4%2017.c3%20Bxe3%2B%2018.Kxe3%20f5%2019.gxf5%20gxf5%2020.Nf2%20O-O-O%2021.Kd2%20Qg5%2B#26) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.d3%20g6%203.Nf3%20Bg7%204.e5%20Nc6%205.Bf4%20d6%206.exd6%20Bxb2%207.dxe7%20Qxe7%2B%208.Be3%20Bxa1%209.Na3%20Bc3%2B%2010.Nd2%20Nf6%2011.Nc4%20Bg4%2012.f3%20Bf5%2013.g4%20Be6%2014.Kf2%20Nd5%2015.Ne4%20Nxe3%2016.Kxe3%20Bd4%2B%2017.Ke2%20Bxc4%2018.dxc4%20f5%2019.gxf5%20gxf5%2020.Bh3%20fxe4%2021.Bf5%20exf3%2B#26) |

position 1 (`r2qk2r/pp1nbppp/3p2n1/1BpP2NQ/5B2/8/PPP2PPP/R4RK1 w kq - 7 13`), split at ply 5: Bh6 (78% there) vs Ne6+ (22%)

| chosen | subpar |
|---|---|
| 13.Ne6 [Qb6] 14.Nxg7+ Kf8 [15.Bh6] Kg8 [16.Nf5] Bf8 [17.Bxd7] Bxh6 18.Nxh6+ Kg7 [19.Nf5+] Kf6 20.Qg5+ Ke5 | 13.Ne6 [Qb6] 14.Nxg7+ Kf8 15.Ne6+ Kg8 [16.Bxd7] fxe6 17.Bxe6+ Kg7 18.Bh6+ Kf6 19.Qf5# |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20c5%202.d5%20e6%203.Nc3%20exd5%204.Nxd5%20d6%205.e4%20Nc6%206.Nf3%20Be6%207.Bf4%20Nf6%208.Ng5%20Bxd5%209.exd5%20Ne5%2010.Bb5%2B%20Nfd7%2011.Qh5%20Ng6%2012.O-O%20Be7%2013.Ne6%20Qb6%2014.Nxg7%2B%20Kf8%2015.Bh6%20Kg8%2016.Nf5%20Bf8%2017.Bxd7%20Bxh6%2018.Nxh6%2B%20Kg7%2019.Nf5%2B%20Kf6%2020.Qg5%2B%20Ke5#24) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20c5%202.d5%20e6%203.Nc3%20exd5%204.Nxd5%20d6%205.e4%20Nc6%206.Nf3%20Be6%207.Bf4%20Nf6%208.Ng5%20Bxd5%209.exd5%20Ne5%2010.Bb5%2B%20Nfd7%2011.Qh5%20Ng6%2012.O-O%20Be7%2013.Ne6%20Qb6%2014.Nxg7%2B%20Kf8%2015.Ne6%2B%20Kg8%2016.Bxd7%20fxe6%2017.Bxe6%2B%20Kg7%2018.Bh6%2B%20Kf6%2019.Qf5%23#24) |

#### S #3 (k = 0): latents 140

position 25 (`1r3r2/pb4kp/1p4p1/2pnP3/4B3/2P4P/PP1N2P1/R4RK1 w - - 3 21`), split at ply 11: Rxa6 (75% there) vs Nxb6 (25%)

| chosen | subpar |
|---|---|
| 21.Nc4 Ba6 22.Bxd5 Rxf1+ 23.Rxf1 Rd8 24.Rf7+ Kh6 [25.Rxa7] [Rxd5] [26.Rxa6] b5 27.Nd6 [Rxe5] 28.Nxb5 Re2 | 21.Nc4 Ba6 22.Bxd5 Rxf1+ 23.Rxf1 Rd8 24.Rf7+ Kh6 [25.Rxa7] [Rxd5] 26.Nxb6 Rd1+ 27.Kh2 Bd3 28.e6 Re1 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.Nc4%20Ba6%2022.Bxd5%20Rxf1%2B%2023.Rxf1%20Rd8%2024.Rf7%2B%20Kh6%2025.Rxa7%20Rxd5%2026.Rxa6%20b5%2027.Nd6%20Rxe5%2028.Nxb5%20Re2#40) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.Nc4%20Ba6%2022.Bxd5%20Rxf1%2B%2023.Rxf1%20Rd8%2024.Rf7%2B%20Kh6%2025.Rxa7%20Rxd5%2026.Nxb6%20Rd1%2B%2027.Kh2%20Bd3%2028.e6%20Re1#40) |

position 35 (`3rr1k1/ppp2pp1/5b1p/8/2qP4/7P/PP3PKP/R2Q2R1 w - - 4 21`), split at ply 10: Re2 (76% there) vs Bxb2 (24%)

| chosen | subpar |
|---|---|
| 21.Qf3 [Rxd4] 22.Kh1 Qd5 23.Qxd5 [Rxd5] 24.Rad1 Rxd1 [25.Rxd1] [Re2] [26.Rd7] [Rxf2] [27.Rxc7] [Rxb2] 28.a4 a5 | 21.Qf3 [Rxd4] 22.Kh1 Qd5 23.Qxd5 [Rxd5] 24.Rad1 Rxd1 [25.Rxd1] Bxb2 26.Rb1 Bd4 [27.Rxb7] Bb6 28.a4 a5 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nc3%20Nf6%203.d4%20exd4%204.Qxd4%20Nc6%205.Qd1%20d6%206.Bb5%20Be7%207.Bg5%20h6%208.Bxf6%20Bxf6%209.Qf3%20O-O%2010.Nh3%20Nd4%2011.Qd1%20Bxh3%2012.gxh3%20d5%2013.exd5%20Qd6%2014.Be2%20Rfe8%2015.Ne4%20Rxe4%2016.c3%20Rxe2%2B%2017.Kf1%20Ree8%2018.cxd4%20Qxd5%2019.Rg1%20Qc4%2B%2020.Kg2%20Rad8%2021.Qf3%20Rxd4%2022.Kh1%20Qd5%2023.Qxd5%20Rxd5%2024.Rad1%20Rxd1%2025.Rxd1%20Re2%2026.Rd7%20Rxf2%2027.Rxc7%20Rxb2%2028.a4%20a5#40) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nc3%20Nf6%203.d4%20exd4%204.Qxd4%20Nc6%205.Qd1%20d6%206.Bb5%20Be7%207.Bg5%20h6%208.Bxf6%20Bxf6%209.Qf3%20O-O%2010.Nh3%20Nd4%2011.Qd1%20Bxh3%2012.gxh3%20d5%2013.exd5%20Qd6%2014.Be2%20Rfe8%2015.Ne4%20Rxe4%2016.c3%20Rxe2%2B%2017.Kf1%20Ree8%2018.cxd4%20Qxd5%2019.Rg1%20Qc4%2B%2020.Kg2%20Rad8%2021.Qf3%20Rxd4%2022.Kh1%20Qd5%2023.Qxd5%20Rxd5%2024.Rad1%20Rxd1%2025.Rxd1%20Bxb2%2026.Rb1%20Bd4%2027.Rxb7%20Bb6%2028.a4%20a5#40) |

position 0 (`2kr2r1/ppp5/2n1RbNp/2q2p1P/3p4/2PQ1P1B/PPKN3P/6R1 b - - 0 20`), split at ply 4: Rxc6 (76% there) vs bxc3 (22%)

| chosen | subpar |
|---|---|
| 20...dxc3 21.Qxc3 Bxc3 [22.Rxc6] [Rxd2+] 23.Kb1 Qxc6 24.Ne7+ Kb8 25.Nxc6+ bxc6 26.bxc3 [Rxh2] 27.Bxf5 [Rxh5] 28.Be4 | 20...dxc3 21.Qxc3 Bxc3 22.bxc3 Nd4+ 23.Kb2 Nxe6 24.Nb3 Qf2+ 25.Ka3 Qxh2 26.Bxf5 Qd6+ 27.Kb2 Kb8 28.Re1 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.Qxc3%20Bxc3%2022.Rxc6%20Rxd2%2B%2023.Kb1%20Qxc6%2024.Ne7%2B%20Kb8%2025.Nxc6%2B%20bxc6%2026.bxc3%20Rxh2%2027.Bxf5%20Rxh5%2028.Be4#39) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.Qxc3%20Bxc3%2022.bxc3%20Nd4%2B%2023.Kb2%20Nxe6%2024.Nb3%20Qf2%2B%2025.Ka3%20Qxh2%2026.Bxf5%20Qd6%2B%2027.Kb2%20Kb8%2028.Re1#39) |

#### S #4 (k = 0): latents 778

position 37 (`2r2k1r/1p1B1p1p/p5p1/2PpP3/6P1/P3q3/1P1NN1P1/n2K3Q w - - 2 26`), split at ply 8: Rb8 (75% there) vs Qc4+ (25%)

| chosen | subpar |
|---|---|
| 26.Bxc8 Kg7 27.Bxb7 Nb3 28.Nxb3 Qxb3+ 29.Kc1 [Rb8] 30.c6 Qxb2+ 31.Kd1 Qb1+ 32.Nc1 Qe4 33.Qe1 Qxg4+ | 26.Bxc8 Kg7 27.Bxb7 Nb3 28.Nxb3 Qxb3+ 29.Kc1 Qc4+ [30.Nc3] [Qxc5] 31.Bxd5 Qe3+ 32.Kb1 [Qxe5] 33.Qf1 Rf8 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20e6%203.e3%20Bd6%204.Bg3%20Bxg3%205.hxg3%20Nc6%206.c4%20Nge7%207.a3%20Bd7%208.Qg4%20g6%209.Qg5%20Nf5%2010.Qf4%20Qe7%2011.g4%20Nd6%2012.c5%20Ne4%2013.Qxc7%20Bc8%2014.Qf4%20e5%2015.Qh6%20Bxg4%2016.f3%20Ng3%2017.fxg4%20Nxh1%2018.Qxh1%20Qg5%2019.Be2%20Qxe3%2020.dxe5%20Nd4%2021.Nd2%20Nc2%2B%2022.Kd1%20Nxa1%2023.Bb5%2B%20Kf8%2024.Ne2%20a6%2025.Bd7%20Rc8%2026.Bxc8%20Kg7%2027.Bxb7%20Nb3%2028.Nxb3%20Qxb3%2B%2029.Kc1%20Rb8%2030.c6%20Qxb2%2B%2031.Kd1%20Qb1%2B%2032.Nc1%20Qe4%2033.Qe1%20Qxg4%2B#50) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20e6%203.e3%20Bd6%204.Bg3%20Bxg3%205.hxg3%20Nc6%206.c4%20Nge7%207.a3%20Bd7%208.Qg4%20g6%209.Qg5%20Nf5%2010.Qf4%20Qe7%2011.g4%20Nd6%2012.c5%20Ne4%2013.Qxc7%20Bc8%2014.Qf4%20e5%2015.Qh6%20Bxg4%2016.f3%20Ng3%2017.fxg4%20Nxh1%2018.Qxh1%20Qg5%2019.Be2%20Qxe3%2020.dxe5%20Nd4%2021.Nd2%20Nc2%2B%2022.Kd1%20Nxa1%2023.Bb5%2B%20Kf8%2024.Ne2%20a6%2025.Bd7%20Rc8%2026.Bxc8%20Kg7%2027.Bxb7%20Nb3%2028.Nxb3%20Qxb3%2B%2029.Kc1%20Qc4%2B%2030.Nc3%20Qxc5%2031.Bxd5%20Qe3%2B%2032.Kb1%20Qxe5%2033.Qf1%20Rf8#50) |

position 7 (`2q2rk1/1Q3pp1/p1N1p2p/3p4/8/6P1/3r1P1P/1R3RK1 w - - 3 24`), split at ply 1: Ne7+ (77% there) vs Qxc8 (22%)

| chosen | subpar |
|---|---|
| [24.Ne7+] Kh7 [25.Nxc8] [Rxc8] [26.Qxf7] [Rc6] [27.Rb7] [Rcc2] 28.Qxg7# | 24.Qxc8 [Rxc8] [25.Ne7+] [Kf8] [26.Nxc8] [d4] [27.Rfd1] [Rc2] [28.Nd6] [e5] [29.Rb8+] Ke7 30.Nf5+ [Kf6] [31.g4] [g6] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.Qf3%20e6%203.Bc4%20Nf6%204.d4%20d5%205.exd5%20cxd5%206.Bb5%2B%20Bd7%207.Bxd7%2B%20Nbxd7%208.Bg5%20Be7%209.Nc3%20h6%2010.Bxf6%20Bxf6%2011.Nge2%20O-O%2012.O-O%20Nb6%2013.Nb5%20Nc4%2014.Qd3%20Nxb2%2015.Qc3%20Nc4%2016.Rab1%20a6%2017.Na3%20Rc8%2018.Nxc4%20Rxc4%2019.Qb3%20Bxd4%2020.Qxb7%20Rxc2%2021.Nxd4%20Rxa2%2022.g3%20Rd2%2023.Nc6%20Qc8%2024.Ne7%2B%20Kh7%2025.Nxc8%20Rxc8%2026.Qxf7%20Rc6%2027.Rb7%20Rcc2%2028.Qxg7%23#46) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.Qf3%20e6%203.Bc4%20Nf6%204.d4%20d5%205.exd5%20cxd5%206.Bb5%2B%20Bd7%207.Bxd7%2B%20Nbxd7%208.Bg5%20Be7%209.Nc3%20h6%2010.Bxf6%20Bxf6%2011.Nge2%20O-O%2012.O-O%20Nb6%2013.Nb5%20Nc4%2014.Qd3%20Nxb2%2015.Qc3%20Nc4%2016.Rab1%20a6%2017.Na3%20Rc8%2018.Nxc4%20Rxc4%2019.Qb3%20Bxd4%2020.Qxb7%20Rxc2%2021.Nxd4%20Rxa2%2022.g3%20Rd2%2023.Nc6%20Qc8%2024.Qxc8%20Rxc8%2025.Ne7%2B%20Kf8%2026.Nxc8%20d4%2027.Rfd1%20Rc2%2028.Nd6%20e5%2029.Rb8%2B%20Ke7%2030.Nf5%2B%20Kf6%2031.g4%20g6#46) |

position 0 (`2kr2r1/ppp5/2n1RbNp/2q2p1P/3p4/2PQ1P1B/PPKN3P/6R1 b - - 0 20`), split at ply 4: Rxc6 (76% there) vs bxc3 (22%)

| chosen | subpar |
|---|---|
| 20...dxc3 21.Qxc3 Bxc3 [22.Rxc6] Rxd2+ [23.Kb1] [Qxc6] [24.Ne7+] [Kb8] 25.Nxc6+ [bxc6] [26.bxc3] [Rxh2] [27.Bxf5] [Rxh5] [28.Be4] | 20...dxc3 21.Qxc3 Bxc3 22.bxc3 Nd4+ 23.Kb2 [Nxe6] [24.Nb3] Qf2+ 25.Ka3 [Qxh2] 26.Bxf5 Qd6+ 27.Kb2 Kb8 28.Re1 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.Qxc3%20Bxc3%2022.Rxc6%20Rxd2%2B%2023.Kb1%20Qxc6%2024.Ne7%2B%20Kb8%2025.Nxc6%2B%20bxc6%2026.bxc3%20Rxh2%2027.Bxf5%20Rxh5%2028.Be4#39) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.Qxc3%20Bxc3%2022.bxc3%20Nd4%2B%2023.Kb2%20Nxe6%2024.Nb3%20Qf2%2B%2025.Ka3%20Qxh2%2026.Bxf5%20Qd6%2B%2027.Kb2%20Kb8%2028.Re1#39) |

#### S #5 (k = 0): latents 1006

position 49 (`1R6/3r1pbk/q2P3p/1NQ1p2n/4P1p1/5NP1/5PKP/8 w - - 0 31`), split at ply 9: Nxg7 (78% there) vs Qxd7 (22%)

| chosen | subpar |
|---|---|
| [31.Nh4] [Nf6] [32.Nf5] [Nxe4] [33.Qc2] [Qc6] [34.Qxc6] [Ng5] [35.Nxg7] Kxg7 36.Nc7 [e4] [37.Ne8+] [Kg6] 38.Qxd7 Nf3 | [31.Nh4] [Nf6] [32.Nf5] [Nxe4] [33.Qc2] [Qc6] [34.Qxc6] [Ng5] 35.Qxd7 [h5] [36.Qe8] [Kg6] [37.Ne7+] [Kf6] [38.d7] [Ne6] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.c4%20g6%203.Nc3%20Bg7%204.e4%20d6%205.Nf3%20O-O%206.Be2%20e5%207.d5%20c6%208.O-O%20cxd5%209.cxd5%20Nh5%2010.g3%20Bh3%2011.Re1%20a6%2012.Be3%20b5%2013.b4%20Nd7%2014.a4%20bxa4%2015.Rxa4%20a5%2016.bxa5%20Rxa5%2017.Nb5%20Rxa4%2018.Qxa4%20Nc5%2019.Bxc5%20dxc5%2020.Qc4%20Qb6%2021.Nc3%20h6%2022.Rb1%20Qa5%2023.Bf1%20Bxf1%2024.Kxf1%20Rc8%2025.Kg2%20g5%2026.Rb7%20Rc7%2027.Rb8%2B%20Kh7%2028.d6%20Rd7%2029.Nb5%20Qa6%2030.Qxc5%20g4%2031.Nh4%20Nf6%2032.Nf5%20Nxe4%2033.Qc2%20Qc6%2034.Qxc6%20Ng5%2035.Nxg7%20Kxg7%2036.Nc7%20e4%2037.Ne8%2B%20Kg6%2038.Qxd7%20Nf3#60) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.c4%20g6%203.Nc3%20Bg7%204.e4%20d6%205.Nf3%20O-O%206.Be2%20e5%207.d5%20c6%208.O-O%20cxd5%209.cxd5%20Nh5%2010.g3%20Bh3%2011.Re1%20a6%2012.Be3%20b5%2013.b4%20Nd7%2014.a4%20bxa4%2015.Rxa4%20a5%2016.bxa5%20Rxa5%2017.Nb5%20Rxa4%2018.Qxa4%20Nc5%2019.Bxc5%20dxc5%2020.Qc4%20Qb6%2021.Nc3%20h6%2022.Rb1%20Qa5%2023.Bf1%20Bxf1%2024.Kxf1%20Rc8%2025.Kg2%20g5%2026.Rb7%20Rc7%2027.Rb8%2B%20Kh7%2028.d6%20Rd7%2029.Nb5%20Qa6%2030.Qxc5%20g4%2031.Nh4%20Nf6%2032.Nf5%20Nxe4%2033.Qc2%20Qc6%2034.Qxc6%20Ng5%2035.Qxd7%20h5%2036.Qe8%20Kg6%2037.Ne7%2B%20Kf6%2038.d7%20Ne6#60) |

position 3 (`2kr1b1r/ppp1pppp/5n2/8/3n1q2/1P1P1B1P/P1P2PP1/RNBQ1K1R b - - 0 11`), split at ply 4: Na3 (79% there) vs c3 (21%)

| chosen | subpar |
|---|---|
| [11...Qe5] 12.Bb2 [Qc5] [13.Na3] [e5] [14.Nc4] [e4] 15.dxe4 [Nxf3] 16.Qxf3 Qxc4+ 17.bxc4 Rd2 18.Qf5+ Kb8 19.Bxf6 | [11...Qe5] 12.Bb2 [Qc5] 13.c3 [Ne6] 14.d4 [Qa5] [15.Nd2] [c6] [16.Nc4] [Qc7] [17.Qe2] [Nd5] [18.g3] [h5] [19.h4] |
| [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nc6%202.e4%20d5%203.exd5%20Qxd5%204.b3%20Bg4%205.Bc4%20Qe4%2B%206.Kf1%20Nd4%207.Bd3%20Qf4%208.Be2%20O-O-O%209.h3%20Bxf3%2010.Bxf3%20Nf6%2011.d3%20Qe5%2012.Bb2%20Qc5%2013.Na3%20e5%2014.Nc4%20e4%2015.dxe4%20Nxf3%2016.Qxf3%20Qxc4%2B%2017.bxc4%20Rd2%2018.Qf5%2B%20Kb8%2019.Bxf6#21) | [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nc6%202.e4%20d5%203.exd5%20Qxd5%204.b3%20Bg4%205.Bc4%20Qe4%2B%206.Kf1%20Nd4%207.Bd3%20Qf4%208.Be2%20O-O-O%209.h3%20Bxf3%2010.Bxf3%20Nf6%2011.d3%20Qe5%2012.Bb2%20Qc5%2013.c3%20Ne6%2014.d4%20Qa5%2015.Nd2%20c6%2016.Nc4%20Qc7%2017.Qe2%20Nd5%2018.g3%20h5%2019.h4#21) |

position 9 (`1k2r3/Rpp1qp1p/3pbb2/8/5Qr1/3PBN2/1PP1BPPP/5RK1 w - - 3 19`), split at ply 6: Kd7 (78% there) vs b6 (20%)

| chosen | subpar |
|---|---|
| 19.Qa4 c5 20.Ra8+ Kc7 [21.Qa5+] [Kd7] [22.Rxe8] [Kxe8] [23.Qa8+] [Kd7] [24.Qxb7+] [Ke8] [25.Qxe7+] [Kxe7] 26.c3 [Ra4] | 19.Qa4 c5 20.Ra8+ Kc7 [21.Qa5+] b6 22.Qa7+ [Kc6] 23.Rxe8 Qxe8 [24.Qa6] [Bxb2] [25.d4] [Bd5] [26.c4] [Bxf3] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Qh5%20Nf6%203.Qxe5%2B%20Be7%204.d3%20Nc6%205.Qg5%20Nxe4%206.Qxg7%20Bf6%207.Qg4%20d6%208.Qxe4%2B%20Be6%209.Nf3%20Qd7%2010.Nc3%20O-O-O%2011.Be2%20Rde8%2012.O-O%20Bxa2%2013.Qa4%20Be6%2014.Qf4%20Qe7%2015.Nb5%20Rhg8%2016.Nxa7%2B%20Nxa7%2017.Rxa7%20Kb8%2018.Be3%20Rg4%2019.Qa4%20c5%2020.Ra8%2B%20Kc7%2021.Qa5%2B%20Kd7%2022.Rxe8%20Kxe8%2023.Qa8%2B%20Kd7%2024.Qxb7%2B%20Ke8%2025.Qxe7%2B%20Kxe7%2026.c3%20Ra4#36) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Qh5%20Nf6%203.Qxe5%2B%20Be7%204.d3%20Nc6%205.Qg5%20Nxe4%206.Qxg7%20Bf6%207.Qg4%20d6%208.Qxe4%2B%20Be6%209.Nf3%20Qd7%2010.Nc3%20O-O-O%2011.Be2%20Rde8%2012.O-O%20Bxa2%2013.Qa4%20Be6%2014.Qf4%20Qe7%2015.Nb5%20Rhg8%2016.Nxa7%2B%20Nxa7%2017.Rxa7%20Kb8%2018.Be3%20Rg4%2019.Qa4%20c5%2020.Ra8%2B%20Kc7%2021.Qa5%2B%20b6%2022.Qa7%2B%20Kc6%2023.Rxe8%20Qxe8%2024.Qa6%20Bxb2%2025.d4%20Bd5%2026.c4%20Bxf3#36) |

#### S #6 (k = 0): latents 327

position 48 (`r4r1k/1ppqn2p/p5p1/4pP2/2Pp2P1/3PbRNP/PP4BK/R2Q4 b - - 1 21`), split at ply 4: Nxf5 (76% there) vs Rxf5 (21%)

| chosen | subpar |
|---|---|
| 21...gxf5 22.gxf5 Rxf5 [23.Nxf5] Nxf5 24.Qe2 Rg8 25.Raf1 Bf4+ 26.Kh1 Ng3+ 27.Rxg3 Rxg3 28.Rf3 Rxf3 29.Qxf3 | 21...gxf5 22.gxf5 Rxf5 23.Rxf5 [Nxf5] 24.Nxf5 Qxf5 25.Qf3 Qxf3 26.Bxf3 c6 27.Be4 Rf8 28.Kg2 Rf2+ 29.Kg3 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nc3%20e5%203.g3%20Bc5%204.Bg2%20a6%205.Nge2%20Nge7%206.h3%20d6%207.d3%20O-O%208.O-O%20Be6%209.Kh2%20f5%2010.f4%20Qd7%2011.exf5%20Nxf5%2012.g4%20Ne3%2013.Bxe3%20Bxe3%2014.f5%20Bf7%2015.Nd5%20Bxd5%2016.Bxd5%2B%20Kh8%2017.Bg2%20d5%2018.c3%20Ne7%2019.Rf3%20d4%2020.c4%20g6%2021.Ng3%20gxf5%2022.gxf5%20Rxf5%2023.Nxf5%20Nxf5%2024.Qe2%20Rg8%2025.Raf1%20Bf4%2B%2026.Kh1%20Ng3%2B%2027.Rxg3%20Rxg3%2028.Rf3%20Rxf3%2029.Qxf3#41) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nc3%20e5%203.g3%20Bc5%204.Bg2%20a6%205.Nge2%20Nge7%206.h3%20d6%207.d3%20O-O%208.O-O%20Be6%209.Kh2%20f5%2010.f4%20Qd7%2011.exf5%20Nxf5%2012.g4%20Ne3%2013.Bxe3%20Bxe3%2014.f5%20Bf7%2015.Nd5%20Bxd5%2016.Bxd5%2B%20Kh8%2017.Bg2%20d5%2018.c3%20Ne7%2019.Rf3%20d4%2020.c4%20g6%2021.Ng3%20gxf5%2022.gxf5%20Rxf5%2023.Rxf5%20Nxf5%2024.Nxf5%20Qxf5%2025.Qf3%20Qxf3%2026.Bxf3%20c6%2027.Be4%20Rf8%2028.Kg2%20Rf2%2B%2029.Kg3#41) |

position 32 (`r2qk2r/ppp2ppp/2n5/7b/1b1P4/2P2N1P/PB2BPP1/R2QK2R b KQkq - 0 12`), split at ply 13: Ne5 (80% there) vs Bxf3 (18%)

| chosen | subpar |
|---|---|
| 12...Bd6 13.O-O O-O 14.c4 Re8 15.Re1 Bb4 16.Rf1 Qe7 17.Bd3 Rad8 18.d5 [Ne5] 19.Bxe5 Bxf3 20.Qxf3 | 12...Bd6 13.O-O O-O 14.c4 Re8 15.Re1 Bb4 16.Rf1 Qe7 17.Bd3 Rad8 18.d5 Bxf3 19.Qxf3 Ne5 20.Bxe5 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20d5%202.exd5%20Nf6%203.Nc3%20Nxd5%204.Bc4%20Nxc3%205.bxc3%20Nc6%206.Bb2%20e5%207.Nf3%20Bg4%208.h3%20Bh5%209.Be2%20Bc5%2010.d4%20exd4%2011.cxd4%20Bb4%2B%2012.c3%20Bd6%2013.O-O%20O-O%2014.c4%20Re8%2015.Re1%20Bb4%2016.Rf1%20Qe7%2017.Bd3%20Rad8%2018.d5%20Ne5%2019.Bxe5%20Bxf3%2020.Qxf3#23) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20d5%202.exd5%20Nf6%203.Nc3%20Nxd5%204.Bc4%20Nxc3%205.bxc3%20Nc6%206.Bb2%20e5%207.Nf3%20Bg4%208.h3%20Bh5%209.Be2%20Bc5%2010.d4%20exd4%2011.cxd4%20Bb4%2B%2012.c3%20Bd6%2013.O-O%20O-O%2014.c4%20Re8%2015.Re1%20Bb4%2016.Rf1%20Qe7%2017.Bd3%20Rad8%2018.d5%20Bxf3%2019.Qxf3%20Ne5%2020.Bxe5#23) |

position 47 (`r2qr1k1/pp3ppp/1bn5/3p4/3Nb2n/1NP2PBP/PP2B1PK/R2Q1R2 b - - 0 16`), split at ply 3: Nf5 (76% there) vs Qf6 (16%)

| chosen | subpar |
|---|---|
| 16...Bg6 17.Qd2 [Nf5] 18.Nxf5 Bxf5 19.Rfe1 d4 20.cxd4 [Nxd4] 21.Nxd4 Qxd4 22.Qxd4 Bxd4 23.Bb5 Rxe1 24.Rxe1 | 16...Bg6 17.Qd2 Qf6 18.Rad1 [Nf5] 19.Bf2 Bc7+ 20.Kg1 Ng3 21.Bxg3 Bxg3 22.Bb5 a6 23.Bxc6 bxc6 [24.Ne2] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bg6%2017.Qd2%20Nf5%2018.Nxf5%20Bxf5%2019.Rfe1%20d4%2020.cxd4%20Nxd4%2021.Nxd4%20Qxd4%2022.Qxd4%20Bxd4%2023.Bb5%20Rxe1%2024.Rxe1#31) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bg6%2017.Qd2%20Qf6%2018.Rad1%20Nf5%2019.Bf2%20Bc7%2B%2020.Kg1%20Ng3%2021.Bxg3%20Bxg3%2022.Bb5%20a6%2023.Bxc6%20bxc6%2024.Ne2#31) |

#### S #7 (k = 0): latents 62

position 8 (`r2qkb1r/pp3ppp/4pn2/8/b1pP4/PnP1PN1P/R1Q2PP1/1NB1KB1R w Kkq - 6 12`), split at ply 3: Bxc4 (75% there) vs Nbd2 (25%)

| chosen | subpar |
|---|---|
| 12.Qb2 Bd6 [13.Bxc4] Nxc1 [14.Qxc1] Rc8 15.Bd3 O-O 16.O-O Qc7 17.c4 b5 18.c5 Be7 19.Nc3 a6 | 12.Qb2 Bd6 13.Nbd2 Na5 [14.Nxc4] Nxc4 [15.Bxc4] O-O 16.O-O Rc8 17.Bd3 a6 18.c4 b5 19.c5 Bb8 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Qb2%20Bd6%2013.Bxc4%20Nxc1%2014.Qxc1%20Rc8%2015.Bd3%20O-O%2016.O-O%20Qc7%2017.c4%20b5%2018.c5%20Be7%2019.Nc3%20a6#22) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Qb2%20Bd6%2013.Nbd2%20Na5%2014.Nxc4%20Nxc4%2015.Bxc4%20O-O%2016.O-O%20Rc8%2017.Bd3%20a6%2018.c4%20b5%2019.c5%20Bb8#22) |

position 42 (`rnb2rk1/5ppp/p3pn2/1p1p4/q7/B3P1P1/3NNPBP/R2Q1RK1 w - - 0 14`), split at ply 9: Bxd5 (76% there) vs Nf4 (24%)

| chosen | subpar |
|---|---|
| [14.Bxf8] Qxd1 [15.Rfxd1] Kxf8 16.e4 Bb7 [17.exd5] Bxd5 [18.Bxd5] Nxd5 19.Nb3 Nc6 20.Ned4 Ne5 21.f4 Nc4 | [14.Bxf8] Qxd1 [15.Rfxd1] Kxf8 16.e4 Bb7 [17.exd5] Bxd5 18.Nf4 Bxg2 [19.Kxg2] Nbd7 20.Nb3 Ke7 21.Na5 Rc8 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.e3%20e6%203.Ne2%20c5%204.Nd2%20a6%205.g3%20Nf6%206.Bg2%20Be7%207.O-O%20O-O%208.c3%20b5%209.a4%20Qa5%2010.dxc5%20Bxc5%2011.b4%20Bxb4%2012.cxb4%20Qxb4%2013.Ba3%20Qxa4%2014.Bxf8%20Qxd1%2015.Rfxd1%20Kxf8%2016.e4%20Bb7%2017.exd5%20Bxd5%2018.Bxd5%20Nxd5%2019.Nb3%20Nc6%2020.Ned4%20Ne5%2021.f4%20Nc4#26) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.e3%20e6%203.Ne2%20c5%204.Nd2%20a6%205.g3%20Nf6%206.Bg2%20Be7%207.O-O%20O-O%208.c3%20b5%209.a4%20Qa5%2010.dxc5%20Bxc5%2011.b4%20Bxb4%2012.cxb4%20Qxb4%2013.Ba3%20Qxa4%2014.Bxf8%20Qxd1%2015.Rfxd1%20Kxf8%2016.e4%20Bb7%2017.exd5%20Bxd5%2018.Nf4%20Bxg2%2019.Kxg2%20Nbd7%2020.Nb3%20Ke7%2021.Na5%20Rc8#26) |

position 23 (`rnbqkr2/pppp4/4p2p/b3B1pn/3P4/2NB1N2/PP3PPP/R2QK2R b KQq - 3 14`), split at ply 2: Bxf4 (83% there) vs O-O (17%)

| chosen | subpar |
|---|---|
| 14...Nf4 [15.Bxf4] Rxf4 16.Bg6+ Kf8 17.O-O Qf6 18.Be4 d5 19.Bd3 Nc6 20.Ne2 Rxf3 [21.gxf3] Nxd4 [22.Nxd4] | 14...Nf4 15.O-O Nc6 [16.Bxf4] Rxf4 17.Bg6+ Kf8 18.d5 Ne7 19.Bh5 Nf5 20.Ne5 Qf6 21.g3 Rd4 22.Qe2 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Bd6%203.d3%20Nf6%204.Bg5%20Bb4%2B%205.c3%20Bc5%206.d4%20exd4%207.cxd4%20Bb4%2B%208.Nc3%20Ba5%209.e5%20h6%2010.Bh4%20g5%2011.Bg3%20Nh5%2012.e6%20fxe6%2013.Be5%20Rf8%2014.Bd3%20Nf4%2015.Bxf4%20Rxf4%2016.Bg6%2B%20Kf8%2017.O-O%20Qf6%2018.Be4%20d5%2019.Bd3%20Nc6%2020.Ne2%20Rxf3%2021.gxf3%20Nxd4%2022.Nxd4#27) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Bd6%203.d3%20Nf6%204.Bg5%20Bb4%2B%205.c3%20Bc5%206.d4%20exd4%207.cxd4%20Bb4%2B%208.Nc3%20Ba5%209.e5%20h6%2010.Bh4%20g5%2011.Bg3%20Nh5%2012.e6%20fxe6%2013.Be5%20Rf8%2014.Bd3%20Nf4%2015.O-O%20Nc6%2016.Bxf4%20Rxf4%2017.Bg6%2B%20Kf8%2018.d5%20Ne7%2019.Bh5%20Nf5%2020.Ne5%20Qf6%2021.g3%20Rd4%2022.Qe2#27) |

#### S #8 (k = 0): latents 1006

position 41 (`r1q1kn1r/p3b3/2p3p1/1p2Pp1p/3P1B1P/1QPB2N1/PP6/2KR3R b kq - 1 18`), split at ply 15: Qxd8 (75% there) vs Bxd8 (25%)

| chosen | subpar |
|---|---|
| [18...a5] [19.d5] [a4] 20.Qc2 [cxd5] 21.Bxb5+ [Kf7] 22.Rxd5 Ne6 [23.Rf1] [a3] [24.b3] [Rd8] [25.Rxd8] [Qxd8] 26.Bc4 | [18...a5] [19.d5] [a4] 20.Qc2 [cxd5] 21.Bxb5+ [Kf7] 22.Rxd5 Ne6 [23.Rf1] [a3] [24.b3] [Rd8] [25.Rxd8] Bxd8 26.Bc4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.Nc3%20dxe4%204.Nxe4%20Bf5%205.f3%20Nf6%206.Bd3%20e6%207.Ne2%20Nbd7%208.Bf4%20Be7%209.g4%20Bxe4%2010.fxe4%20Nxg4%2011.Ng3%20f6%2012.Qxg4%20g6%2013.Qxe6%20Nf8%2014.Qb3%20b5%2015.c3%20Qc8%2016.e5%20f5%2017.h4%20h5%2018.O-O-O%20a5%2019.d5%20a4%2020.Qc2%20cxd5%2021.Bxb5%2B%20Kf7%2022.Rxd5%20Ne6%2023.Rf1%20a3%2024.b3%20Rd8%2025.Rxd8%20Qxd8%2026.Bc4#35) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.Nc3%20dxe4%204.Nxe4%20Bf5%205.f3%20Nf6%206.Bd3%20e6%207.Ne2%20Nbd7%208.Bf4%20Be7%209.g4%20Bxe4%2010.fxe4%20Nxg4%2011.Ng3%20f6%2012.Qxg4%20g6%2013.Qxe6%20Nf8%2014.Qb3%20b5%2015.c3%20Qc8%2016.e5%20f5%2017.h4%20h5%2018.O-O-O%20a5%2019.d5%20a4%2020.Qc2%20cxd5%2021.Bxb5%2B%20Kf7%2022.Rxd5%20Ne6%2023.Rf1%20a3%2024.b3%20Rd8%2025.Rxd8%20Bxd8%2026.Bc4#35) |

position 15 (`r1q2rk1/2B2ppp/p1Q1p3/3p4/3Pn3/P3P3/P1P2PPP/R4RK1 b - - 4 17`), split at ply 7: Rb8 (80% there) vs Qxc6 (20%)

| chosen | subpar |
|---|---|
| 17...Nd2 18.Rfd1 Nc4 19.Bd6 Rd8 [20.Bc5] [Rb8] [21.Rab1] Qxc6 22.Rxb8 Rxb8 23.Bb4 a5 24.Bc5 [Rb2] 25.h3 | 17...Nd2 18.Rfd1 Nc4 19.Bd6 Rd8 [20.Bc5] Qxc6 21.Rab1 Rab8 22.Rb3 [Rxb3] 23.axb3 Nxa3 24.Ra1 Nb5 25.c4 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bf4%20d6%203.e3%20Nc6%204.Bb5%20Bd7%205.Bxc6%20Bxc6%206.Nf3%20Bxf3%207.Qxf3%20e6%208.Qxb7%20d5%209.Bxc7%20Qc8%2010.Qc6%2B%20Nd7%2011.Na3%20Be7%2012.Nb5%20O-O%2013.Qc3%20a6%2014.Na3%20Bxa3%2015.bxa3%20Nf6%2016.O-O%20Ne4%2017.Qc6%20Nd2%2018.Rfd1%20Nc4%2019.Bd6%20Rd8%2020.Bc5%20Rb8%2021.Rab1%20Qxc6%2022.Rxb8%20Rxb8%2023.Bb4%20a5%2024.Bc5%20Rb2%2025.h3#33) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bf4%20d6%203.e3%20Nc6%204.Bb5%20Bd7%205.Bxc6%20Bxc6%206.Nf3%20Bxf3%207.Qxf3%20e6%208.Qxb7%20d5%209.Bxc7%20Qc8%2010.Qc6%2B%20Nd7%2011.Na3%20Be7%2012.Nb5%20O-O%2013.Qc3%20a6%2014.Na3%20Bxa3%2015.bxa3%20Nf6%2016.O-O%20Ne4%2017.Qc6%20Nd2%2018.Rfd1%20Nc4%2019.Bd6%20Rd8%2020.Bc5%20Qxc6%2021.Rab1%20Rab8%2022.Rb3%20Rxb3%2023.axb3%20Nxa3%2024.Ra1%20Nb5%2025.c4#33) |

position 8 (`r2qkb1r/pp3ppp/4pn2/8/b1pP4/PnP1PN1P/R1Q2PP1/1NB1KB1R w Kkq - 6 12`), split at ply 6: Rc8 (78% there) vs O-O (19%)

| chosen | subpar |
|---|---|
| [12.Qb2] [Bd6] 13.Bxc4 Nxc1 14.Qxc1 [Rc8] 15.Bd3 [O-O] [16.O-O] [Qc7] 17.c4 [b5] 18.c5 [Be7] 19.Nc3 [a6] | [12.Qb2] [Bd6] 13.Bxc4 Nxc1 14.Qxc1 O-O 15.O-O [Rc8] 16.Nbd2 [b5] 17.Bb3 Bxb3 18.Nxb3 Nd5 19.Rc2 [Nb6] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Qb2%20Bd6%2013.Bxc4%20Nxc1%2014.Qxc1%20Rc8%2015.Bd3%20O-O%2016.O-O%20Qc7%2017.c4%20b5%2018.c5%20Be7%2019.Nc3%20a6#22) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Qb2%20Bd6%2013.Bxc4%20Nxc1%2014.Qxc1%20O-O%2015.O-O%20Rc8%2016.Nbd2%20b5%2017.Bb3%20Bxb3%2018.Nxb3%20Nd5%2019.Rc2%20Nb6#22) |

#### S #9 (k = 0): latents 425

position 8 (`r2qkb1r/pp3ppp/4pn2/8/b1pP4/PnP1PN1P/R1Q2PP1/1NB1KB1R w Kkq - 6 12`), split at ply 8: bxa4 (75% there) vs Nxc3 (25%)

| chosen | subpar |
|---|---|
| 12.Qe2 b5 13.Nbd2 [Nxc1] 14.Qd1 Nxa2 15.Qxa4 [bxa4] 16.Bxc4 Qa5 17.O-O Qxc3 18.Bb5+ Kd8 19.Ne5 Qxd2 | 12.Qe2 b5 13.Nbd2 [Nxc1] 14.Qd1 Nxa2 15.Qxa4 Nxc3 16.Qa6 Qb6 [17.Qxb6] axb6 18.Nb1 [Nxb1] 19.Bxc4 bxc4 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Qe2%20b5%2013.Nbd2%20Nxc1%2014.Qd1%20Nxa2%2015.Qxa4%20bxa4%2016.Bxc4%20Qa5%2017.O-O%20Qxc3%2018.Bb5%2B%20Kd8%2019.Ne5%20Qxd2#22) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Qe2%20b5%2013.Nbd2%20Nxc1%2014.Qd1%20Nxa2%2015.Qxa4%20Nxc3%2016.Qa6%20Qb6%2017.Qxb6%20axb6%2018.Nb1%20Nxb1%2019.Bxc4%20bxc4#22) |

position 12 (`2k4r/1pb3p1/p1n4p/5R2/4p2Q/P1PpB2P/1q4P1/R6K b - - 1 22`), split at ply 8: Qxf4 (75% there) vs Rxf4 (25%)

| chosen | subpar |
|---|---|
| 22...Re8 23.Rf7 Qxc3 24.Rc1 Qe5 25.Bf4 [Qxf4] [26.Qxf4] Bxf4 27.Rxc6+ bxc6 28.Rxf4 e3 29.Rf1 e2 30.Re1 | 22...Re8 23.Rf7 Qxc3 24.Rc1 Qe5 25.Bf4 [Qxf4] 26.Rxf4 Bxf4 27.Qxf4 d2 [28.Qxd2] e3 29.Qd6 e2 30.Re1 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.e4%20dxe4%204.f3%20exf3%205.Nxf3%20c5%206.Bd3%20cxd4%207.Ne4%20Nxe4%208.Bxe4%20Nc6%209.O-O%20Qb6%2010.Kh1%20e5%2011.Qe1%20Bd6%2012.Ng5%20Bd7%2013.a3%20O-O-O%2014.Nxf7%20Bc7%2015.Nxh8%20Rxh8%2016.Rf7%20h6%2017.c3%20a6%2018.Bf5%20Bxf5%2019.Rxf5%20d3%2020.Be3%20Qxb2%2021.h3%20e4%2022.Qh4%20Re8%2023.Rf7%20Qxc3%2024.Rc1%20Qe5%2025.Bf4%20Qxf4%2026.Qxf4%20Bxf4%2027.Rxc6%2B%20bxc6%2028.Rxf4%20e3%2029.Rf1%20e2%2030.Re1#43) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.e4%20dxe4%204.f3%20exf3%205.Nxf3%20c5%206.Bd3%20cxd4%207.Ne4%20Nxe4%208.Bxe4%20Nc6%209.O-O%20Qb6%2010.Kh1%20e5%2011.Qe1%20Bd6%2012.Ng5%20Bd7%2013.a3%20O-O-O%2014.Nxf7%20Bc7%2015.Nxh8%20Rxh8%2016.Rf7%20h6%2017.c3%20a6%2018.Bf5%20Bxf5%2019.Rxf5%20d3%2020.Be3%20Qxb2%2021.h3%20e4%2022.Qh4%20Re8%2023.Rf7%20Qxc3%2024.Rc1%20Qe5%2025.Bf4%20Qxf4%2026.Rxf4%20Bxf4%2027.Qxf4%20d2%2028.Qxd2%20e3%2029.Qd6%20e2%2030.Re1#43) |

position 15 (`r1q2rk1/2B2ppp/p1Q1p3/3p4/3Pn3/P3P3/P1P2PPP/R4RK1 b - - 4 17`), split at ply 11: Rxb1 (76% there) vs Rcb5 (24%)

| chosen | subpar |
|---|---|
| 17...Ra7 18.Bb6 Rb7 [19.Qxc8] Rxc8 20.Bc5 [Nxc5] 21.dxc5 Rxc5 22.Rab1 [Rxb1] 23.Rxb1 g6 24.Rb2 Rc3 25.a4 | 17...Ra7 18.Bb6 Rb7 [19.Qxc8] Rxc8 20.Bc5 [Nxc5] 21.dxc5 Rxc5 22.Rab1 Rcb5 [23.Rxb5] Rxb5 24.Rc1 Rb2 25.Kf1 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bf4%20d6%203.e3%20Nc6%204.Bb5%20Bd7%205.Bxc6%20Bxc6%206.Nf3%20Bxf3%207.Qxf3%20e6%208.Qxb7%20d5%209.Bxc7%20Qc8%2010.Qc6%2B%20Nd7%2011.Na3%20Be7%2012.Nb5%20O-O%2013.Qc3%20a6%2014.Na3%20Bxa3%2015.bxa3%20Nf6%2016.O-O%20Ne4%2017.Qc6%20Ra7%2018.Bb6%20Rb7%2019.Qxc8%20Rxc8%2020.Bc5%20Nxc5%2021.dxc5%20Rxc5%2022.Rab1%20Rxb1%2023.Rxb1%20g6%2024.Rb2%20Rc3%2025.a4#33) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bf4%20d6%203.e3%20Nc6%204.Bb5%20Bd7%205.Bxc6%20Bxc6%206.Nf3%20Bxf3%207.Qxf3%20e6%208.Qxb7%20d5%209.Bxc7%20Qc8%2010.Qc6%2B%20Nd7%2011.Na3%20Be7%2012.Nb5%20O-O%2013.Qc3%20a6%2014.Na3%20Bxa3%2015.bxa3%20Nf6%2016.O-O%20Ne4%2017.Qc6%20Ra7%2018.Bb6%20Rb7%2019.Qxc8%20Rxc8%2020.Bc5%20Nxc5%2021.dxc5%20Rxc5%2022.Rab1%20Rcb5%2023.Rxb5%20Rxb5%2024.Rc1%20Rb2%2025.Kf1#33) |

#### S #10 (k = 0): latents 1451

position 13 (`r2qkb1r/ppp3pp/5n2/3p4/8/2P1BB2/PP3P1P/RN1QK2R b KQkq - 2 11`), split at ply 15: Bxa3+ (77% there) vs Rxa3 (23%)

| chosen | subpar |
|---|---|
| 11...Bd6 12.Nd2 O-O 13.Qb3 c6 14.O-O-O a5 15.a4 b5 16.axb5 a4 17.Qc2 a3 18.bxa3 [Bxa3+] 19.Kb1 | 11...Bd6 12.Nd2 O-O 13.Qb3 c6 14.O-O-O a5 15.a4 b5 16.axb5 a4 17.Qc2 a3 18.bxa3 Rxa3 19.Nb1 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.d4%20Bxf5%205.Bd3%20Bg4%206.c3%20e5%207.dxe5%20Nxe5%208.Be2%20Nxf3%2B%209.gxf3%20Bxf3%2010.Bxf3%20Nf6%2011.Be3%20Bd6%2012.Nd2%20O-O%2013.Qb3%20c6%2014.O-O-O%20a5%2015.a4%20b5%2016.axb5%20a4%2017.Qc2%20a3%2018.bxa3%20Bxa3%2B%2019.Kb1#21) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.d4%20Bxf5%205.Bd3%20Bg4%206.c3%20e5%207.dxe5%20Nxe5%208.Be2%20Nxf3%2B%209.gxf3%20Bxf3%2010.Bxf3%20Nf6%2011.Be3%20Bd6%2012.Nd2%20O-O%2013.Qb3%20c6%2014.O-O-O%20a5%2015.a4%20b5%2016.axb5%20a4%2017.Qc2%20a3%2018.bxa3%20Rxa3%2019.Nb1#21) |

position 47 (`r2qr1k1/pp3ppp/1bn5/3p4/3Nb2n/1NP2PBP/PP2B1PK/R2Q1R2 b - - 0 16`), split at ply 5: Bxd4 (77% there) vs Bxd3 (23%)

| chosen | subpar |
|---|---|
| 16...Bg6 17.Bd3 Nxd4 18.Nxd4 [Bxd4] 19.cxd4 [Nf5] 20.Bxf5 [Bxf5] [21.Re1] [Qb6] [22.Qd2] [h6] [23.Rac1] [Rxe1] [24.Rxe1] | 16...Bg6 17.Bd3 Nxd4 18.Nxd4 Bxd3 19.Qxd3 [Bxd4] 20.Qxd4 [Nf5] 21.Qd3 Nxg3 22.Kxg3 Qg5+ 23.Kh2 Re3 24.Qb5 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bg6%2017.Bd3%20Nxd4%2018.Nxd4%20Bxd4%2019.cxd4%20Nf5%2020.Bxf5%20Bxf5%2021.Re1%20Qb6%2022.Qd2%20h6%2023.Rac1%20Rxe1%2024.Rxe1#31) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bg6%2017.Bd3%20Nxd4%2018.Nxd4%20Bxd3%2019.Qxd3%20Bxd4%2020.Qxd4%20Nf5%2021.Qd3%20Nxg3%2022.Kxg3%20Qg5%2B%2023.Kh2%20Re3%2024.Qb5#31) |

position 27 (`r3kb1r/1p2pp1p/p2p1np1/4n1Q1/3B4/PP2P3/2qPNPPP/R4RK1 b kq - 1 15`), split at ply 8: Qg3 (75% there) vs Qxf5 (20%)

| chosen | subpar |
|---|---|
| 15...Qxd2 [16.Nf4] Bg7 [17.Rfd1] Qc2 [18.Rac1] Qf5 [19.Qg3] [O-O] 20.Rc7 Ne4 [21.Qh4] g5 [22.Qh5] gxf4 23.exf4 | 15...Qxd2 [16.Nf4] Bg7 [17.Rfd1] Qc2 [18.Rac1] Qf5 19.Qxf5 gxf5 [20.Rc7] b5 [21.h3] O-O [22.Rxe7] Rfe8 23.Rc7 |
| [Lichess](https://lichess.org/analysis/pgn/1.e3%20c5%202.Qh5%20Nf6%203.Qxc5%20g6%204.Bc4%20d6%205.Qg5%20Nc6%206.a3%20Ne5%207.Bb5%2B%20Bd7%208.Ba4%20Bxa4%209.b3%20Bd7%2010.Bb2%20Qc7%2011.Nc3%20a6%2012.Nge2%20Bb5%2013.O-O%20Bxe2%2014.Nxe2%20Qxc2%2015.Bd4%20Qxd2%2016.Nf4%20Bg7%2017.Rfd1%20Qc2%2018.Rac1%20Qf5%2019.Qg3%20O-O%2020.Rc7%20Ne4%2021.Qh4%20g5%2022.Qh5%20gxf4%2023.exf4#29) | [Lichess](https://lichess.org/analysis/pgn/1.e3%20c5%202.Qh5%20Nf6%203.Qxc5%20g6%204.Bc4%20d6%205.Qg5%20Nc6%206.a3%20Ne5%207.Bb5%2B%20Bd7%208.Ba4%20Bxa4%209.b3%20Bd7%2010.Bb2%20Qc7%2011.Nc3%20a6%2012.Nge2%20Bb5%2013.O-O%20Bxe2%2014.Nxe2%20Qxc2%2015.Bd4%20Qxd2%2016.Nf4%20Bg7%2017.Rfd1%20Qc2%2018.Rac1%20Qf5%2019.Qxf5%20gxf5%2020.Rc7%20b5%2021.h3%20O-O%2022.Rxe7%20Rfe8%2023.Rc7#29) |

## W

| k | pairs | nonzero v | families | held-out recurrence: median / 90% / max | null 95th: median | null (every draw): 90% / 99% | families above their null 95th (chance: 5%) |
|---|---|---|---|---|---|---|---|
| 0 | 1006 | 100% | 377 | 0.8% / 3.6% / 10.7% | 2.2% | 2.6% / 6.0% | 31 (8%) |
| 2 | 953 | 30% | 238 | 0.0% / 0.2% / 2.2% | 0.2% | 0.0% / 0.4% | 15 (6%) |
| 4 | 876 | 13% | 105 | 0.0% / 0.2% / 1.6% | 0.0% | 0.0% / 0.2% | 11 (10%) |
| 6 | 747 | 11% | 77 | 0.0% / 0.3% / 0.8% | 0.0% | 0.0% / 0.3% | 12 (16%) |

### W: the top 20 families by held-out recurrence

| # | k | latents (weight) | found in | held out on | recurrence | null 95th | persistence (pairs on at split) | positions found |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 62 (1.00) | A (30 v's) | B | 10.7% | 5.8% | 1.0 (54) | 0, 3, 5, 7, 9, 19, 20, 24, 26, 28, 34, 35 ... |
| 2 | 0 | 62 (1.00) | B (33 v's) | A | 8.4% | 5.2% | 1.0 (42) | 2, 4, 8, 13, 14, 17, 21, 22, 23, 27, 32, 36 ... |
| 3 | 0 | 778 (1.00) | A (4 v's) | B | 7.9% | 6.1% | 1.0 (40) | 19, 20, 33, 46 |
| 4 | 0 | 894 (1.00) | A (1 v's) | B | 7.5% | 5.9% | 1.0 (38) | 28 |
| 5 | 0 | 499 (1.00) | A (4 v's) | B | 6.9% | 5.3% | 1.0 (35) | 16, 20, 29 |
| 6 | 0 | 425 (1.00) | B (1 v's) | A | 6.6% | 5.0% | 1.0 (33) | 15 |
| 7 | 0 | 778 (1.00) | B (1 v's) | A | 6.6% | 5.6% | 1.0 (33) | 39 |
| 8 | 0 | 1566 (1.00) | B (1 v's) | A | 6.4% | 5.6% | 1.0 (32) | 43 |
| 9 | 0 | 425 (1.00) | A (1 v's) | B | 6.3% | 5.1% | 1.0 (32) | 20 |
| 10 | 0 | 499 (1.00) | B (5 v's) | A | 6.0% | 5.8% | 1.0 (30) | 4, 15, 17, 23, 43 |
| 11 | 0 | 302 (1.00) | B (2 v's) | A | 5.8% | 5.0% | 1.0 (29) | 36 |
| 12 | 0 | 1006 (1.00) | A (1 v's) | B | 5.7% | 5.5% | 1.0 (29) | 5 |
| 13 | 0 | 217 (1.00) | B (11 v's) | A | 5.6% | 5.2% | 1.0 (28) | 12, 13, 15, 21, 32, 43 |
| 14 | 0 | 1006 (1.00) | B (2 v's) | A | 5.4% | 5.6% | 1.0 (27) | 15, 44 |
| 15 | 0 | 642 (1.00) | A (6 v's) | B | 5.3% | 4.9% | 1.0 (27) | 9, 11, 19, 29, 46 |
| 16 | 0 | 894 (1.00) | B (2 v's) | A | 5.2% | 5.4% | 1.0 (26) | 4, 43 |
| 17 | 0 | 140 (1.00) | B (9 v's) | A | 5.2% | 4.6% | 1.0 (26) | 8, 15, 27, 32, 44 |
| 18 | 0 | 422 (1.00) | B (2 v's) | A | 5.2% | 5.4% | 1.0 (26) | 15, 36 |
| 19 | 0 | 881 (1.00) | A (1 v's) | B | 5.1% | 4.9% | 1.0 (26) | 38 |
| 20 | 0 | 1910 (1.00) | B (1 v's) | A | 5.0% | 4.8% | 1.0 (25) | 4 |

#### W #1 (k = 0): latents 62

position 8 (`r2qkb1r/pp3ppp/4pn2/8/b1pP4/PnP1PN1P/R1Q2PP1/1NB1KB1R w Kkq - 6 12`), split at ply 5: Bxb3 (75% there) vs O-O (25%)

| chosen | subpar |
|---|---|
| 12.Qb2 Ne4 [13.Bxc4] Qa5 [14.Bxb3] Bxb3 [15.Qxb3] Rc8 16.Bd2 Bxa3 [17.Nxa3] Nxc3 [18.Bxc3] Qxc3+ [19.Qxc3] Rxc3 | 12.Qb2 Ne4 [13.Bxc4] Qa5 14.O-O Bd6 [15.Bxb3] Bxb3 [16.Qxb3] O-O [17.Qxb7] Rab8 [18.Qxe4] Rxb1 [19.Qxb1] Qxc3 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Qb2%20Ne4%2013.Bxc4%20Qa5%2014.Bxb3%20Bxb3%2015.Qxb3%20Rc8%2016.Bd2%20Bxa3%2017.Nxa3%20Nxc3%2018.Bxc3%20Qxc3%2B%2019.Qxc3%20Rxc3#22) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Qb2%20Ne4%2013.Bxc4%20Qa5%2014.O-O%20Bd6%2015.Bxb3%20Bxb3%2016.Qxb3%20O-O%2017.Qxb7%20Rab8%2018.Qxe4%20Rxb1%2019.Qxb1%20Qxc3#22) |

position 21 (`r1b2rk1/pp2q1pp/3b4/5p1Q/4p3/2N5/PPP2PPP/R1BR2K1 w - - 2 17`), split at ply 11: Bxe7 (75% there) vs Nc7 (25%)

| chosen | subpar |
|---|---|
| 17.Bg5 Qe5 18.Rd5 Qe6 19.Nb5 Be7 20.Nc7 Qc6 [21.Nxa8] Qxd5 [22.Bxe7] Re8 23.Qxe8# | 17.Bg5 Qe5 18.Rd5 Qe6 19.Nb5 Be7 20.Nc7 Qc6 [21.Nxa8] Qxd5 22.Nc7 Qe5 [23.Bxe7] Qxe7 24.Nd5 Qd6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Qxd4%20Nf6%205.e5%20Nfd7%206.exd6%20Nc6%207.Qe3%20e6%208.Nc3%20Bxd6%209.Bd3%20O-O%2010.O-O%20Nde5%2011.Nxe5%20Nxe5%2012.Be4%20f5%2013.Bf3%20Nxf3%2B%2014.Qxf3%20e5%2015.Rd1%20e4%2016.Qh5%20Qe7%2017.Bg5%20Qe5%2018.Rd5%20Qe6%2019.Nb5%20Be7%2020.Nc7%20Qc6%2021.Nxa8%20Qxd5%2022.Bxe7%20Re8%2023.Qxe8%23#32) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Qxd4%20Nf6%205.e5%20Nfd7%206.exd6%20Nc6%207.Qe3%20e6%208.Nc3%20Bxd6%209.Bd3%20O-O%2010.O-O%20Nde5%2011.Nxe5%20Nxe5%2012.Be4%20f5%2013.Bf3%20Nxf3%2B%2014.Qxf3%20e5%2015.Rd1%20e4%2016.Qh5%20Qe7%2017.Bg5%20Qe5%2018.Rd5%20Qe6%2019.Nb5%20Be7%2020.Nc7%20Qc6%2021.Nxa8%20Qxd5%2022.Nc7%20Qe5%2023.Bxe7%20Qxe7%2024.Nd5%20Qd6#32) |

position 22 (`r1b2rk1/pp4pp/3B1p2/3P3q/2P3n1/3P4/PP3PPP/R2QR1K1 w - - 1 17`), split at ply 9: Qxh7 (75% there) vs Qe8# (25%)

| chosen | subpar |
|---|---|
| 17.h3 Ne5 [18.Qxh5] Nxd3 [19.Bxf8] Nxe1 [20.Rxe1] Kxf8 [21.Qxh7] Bd7 22.Qh8+ Kf7 [23.Qxa8] Kg6 [24.Qxb7] Bf5 | 17.h3 Ne5 [18.Qxh5] Nxd3 [19.Bxf8] Nxe1 [20.Rxe1] Kxf8 21.Qe8# |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nf6%203.Bc4%20d5%204.exd5%20e4%205.Ng5%20Bd6%206.Nc3%20Nbd7%207.O-O%20Ne5%208.Re1%20O-O%209.Ncxe4%20Nxc4%2010.Nxf6%2B%20Qxf6%2011.d3%20Ne5%2012.Ne4%20Qg6%2013.Nxd6%20cxd6%2014.Bf4%20f6%2015.c4%20Ng4%2016.Bxd6%20Qh5%2017.h3%20Ne5%2018.Qxh5%20Nxd3%2019.Bxf8%20Nxe1%2020.Rxe1%20Kxf8%2021.Qxh7%20Bd7%2022.Qh8%2B%20Kf7%2023.Qxa8%20Kg6%2024.Qxb7%20Bf5#32) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nf6%203.Bc4%20d5%204.exd5%20e4%205.Ng5%20Bd6%206.Nc3%20Nbd7%207.O-O%20Ne5%208.Re1%20O-O%209.Ncxe4%20Nxc4%2010.Nxf6%2B%20Qxf6%2011.d3%20Ne5%2012.Ne4%20Qg6%2013.Nxd6%20cxd6%2014.Bf4%20f6%2015.c4%20Ng4%2016.Bxd6%20Qh5%2017.h3%20Ne5%2018.Qxh5%20Nxd3%2019.Bxf8%20Nxe1%2020.Rxe1%20Kxf8%2021.Qe8%23#32) |

#### W #2 (k = 0): latents 62

position 19 (`r4r1k/ppq1b1pp/2npQ3/4p3/1PP5/P1P2N2/5PPP/R1B2RK1 w - - 1 18`), split at ply 11: bxc5 (77% there) vs Rd7 (23%)

| chosen | subpar |
|---|---|
| 18.Ng5 Bxg5 [19.Bxg5] Rae8 20.Qg4 Ne7 21.Rad1 Ng6 22.c5 dxc5 [23.bxc5] Qxc5 24.Rd7 Qxc3 [25.Rxb7] Qxa3 | 18.Ng5 Bxg5 [19.Bxg5] Rae8 20.Qg4 Ne7 21.Rad1 Ng6 22.c5 dxc5 23.Rd7 Qb6 [24.bxc5] Qxc5 [25.Rxb7] Qxc3 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bc4%20Nf6%204.d3%20Be7%205.O-O%20O-O%206.Nc3%20d6%207.a3%20Be6%208.Qe2%20Bxc4%209.dxc4%20Nd7%2010.Nd5%20Nc5%2011.b4%20Ne6%2012.c3%20f5%2013.exf5%20Rxf5%2014.Qe4%20Rf8%2015.Qg4%20Qd7%2016.Nxc7%20Qxc7%2017.Qxe6%2B%20Kh8%2018.Ng5%20Bxg5%2019.Bxg5%20Rae8%2020.Qg4%20Ne7%2021.Rad1%20Ng6%2022.c5%20dxc5%2023.bxc5%20Qxc5%2024.Rd7%20Qxc3%2025.Rxb7%20Qxa3#34) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bc4%20Nf6%204.d3%20Be7%205.O-O%20O-O%206.Nc3%20d6%207.a3%20Be6%208.Qe2%20Bxc4%209.dxc4%20Nd7%2010.Nd5%20Nc5%2011.b4%20Ne6%2012.c3%20f5%2013.exf5%20Rxf5%2014.Qe4%20Rf8%2015.Qg4%20Qd7%2016.Nxc7%20Qxc7%2017.Qxe6%2B%20Kh8%2018.Ng5%20Bxg5%2019.Bxg5%20Rae8%2020.Qg4%20Ne7%2021.Rad1%20Ng6%2022.c5%20dxc5%2023.Rd7%20Qb6%2024.bxc5%20Qxc5%2025.Rxb7%20Qxc3#34) |

position 35 (`3rr1k1/ppp2pp1/5b1p/8/2qP4/7P/PP3PKP/R2Q2R1 w - - 4 21`), split at ply 3: Qxd4 (76% there) vs Qf3 (22%)

| chosen | subpar |
|---|---|
| 21.b3 Qxd4 [22.Qxd4] Bxd4 23.Rad1 Bb6 [24.Rxd8] Rxd8 25.Re1 Rd2 26.Re8+ Kh7 27.Re7 Rxf2+ 28.Kg3 Rxa2 | 21.b3 Qxd4 22.Qf3 Qe4 [23.Qxe4] Rxe4 24.Kh1 Bxa1 [25.Rxa1] Re2 26.Kg2 Rdd2 27.Rf1 Rxa2 28.b4 Rab2 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nc3%20Nf6%203.d4%20exd4%204.Qxd4%20Nc6%205.Qd1%20d6%206.Bb5%20Be7%207.Bg5%20h6%208.Bxf6%20Bxf6%209.Qf3%20O-O%2010.Nh3%20Nd4%2011.Qd1%20Bxh3%2012.gxh3%20d5%2013.exd5%20Qd6%2014.Be2%20Rfe8%2015.Ne4%20Rxe4%2016.c3%20Rxe2%2B%2017.Kf1%20Ree8%2018.cxd4%20Qxd5%2019.Rg1%20Qc4%2B%2020.Kg2%20Rad8%2021.b3%20Qxd4%2022.Qxd4%20Bxd4%2023.Rad1%20Bb6%2024.Rxd8%20Rxd8%2025.Re1%20Rd2%2026.Re8%2B%20Kh7%2027.Re7%20Rxf2%2B%2028.Kg3%20Rxa2#40) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nc3%20Nf6%203.d4%20exd4%204.Qxd4%20Nc6%205.Qd1%20d6%206.Bb5%20Be7%207.Bg5%20h6%208.Bxf6%20Bxf6%209.Qf3%20O-O%2010.Nh3%20Nd4%2011.Qd1%20Bxh3%2012.gxh3%20d5%2013.exd5%20Qd6%2014.Be2%20Rfe8%2015.Ne4%20Rxe4%2016.c3%20Rxe2%2B%2017.Kf1%20Ree8%2018.cxd4%20Qxd5%2019.Rg1%20Qc4%2B%2020.Kg2%20Rad8%2021.b3%20Qxd4%2022.Qf3%20Qe4%2023.Qxe4%20Rxe4%2024.Kh1%20Bxa1%2025.Rxa1%20Re2%2026.Kg2%20Rdd2%2027.Rf1%20Rxa2%2028.b4%20Rab2#40) |

position 28 (`3r1k2/r4p1p/p1p1pqp1/2Pn4/2N5/6QP/1P3PP1/R2R2K1 w - - 16 27`), split at ply 3: Nxc6 (81% there) vs Ng4 (19%)

| chosen | subpar |
|---|---|
| 27.Ne5 Kg7 [28.Nxc6] Rad7 [29.Nxd8] Rxd8 30.c6 Rc8 [31.Rxa6] Nb4 32.Rb6 Nxc6 33.Rc1 Nd4 [34.Rxc8] Ne2+ | 27.Ne5 Kg7 28.Ng4 Qxb2 29.Qe5+ Qxe5 [30.Nxe5] Nc3 [31.Rxd8] Ne2+ 32.Kh2 Nf4 [33.Nxc6] Rc7 34.Ne5 Rxc5 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20g6%202.d4%20Bg7%203.c3%20d5%204.e5%20c5%205.Nf3%20Nc6%206.Bb5%20Qb6%207.a4%20a6%208.Bxc6%2B%20bxc6%209.a5%20Qb5%2010.Na3%20Qxa5%2011.O-O%20Qc7%2012.Bf4%20Bg4%2013.h3%20Bxf3%2014.Qxf3%20e6%2015.c4%20Ne7%2016.dxc5%20Bxe5%2017.Bxe5%20Qxe5%2018.cxd5%20Qxd5%2019.Qf6%20Rf8%2020.Rfd1%20Qf5%2021.Qd4%20Nd5%2022.Nc4%20Ke7%2023.Nb6%20Ra7%2024.Qh4%2B%20Qf6%2025.Qg3%20Rd8%2026.Nc4%20Kf8%2027.Ne5%20Kg7%2028.Nxc6%20Rad7%2029.Nxd8%20Rxd8%2030.c6%20Rc8%2031.Rxa6%20Nb4%2032.Rb6%20Nxc6%2033.Rc1%20Nd4%2034.Rxc8%20Ne2%2B#52) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20g6%202.d4%20Bg7%203.c3%20d5%204.e5%20c5%205.Nf3%20Nc6%206.Bb5%20Qb6%207.a4%20a6%208.Bxc6%2B%20bxc6%209.a5%20Qb5%2010.Na3%20Qxa5%2011.O-O%20Qc7%2012.Bf4%20Bg4%2013.h3%20Bxf3%2014.Qxf3%20e6%2015.c4%20Ne7%2016.dxc5%20Bxe5%2017.Bxe5%20Qxe5%2018.cxd5%20Qxd5%2019.Qf6%20Rf8%2020.Rfd1%20Qf5%2021.Qd4%20Nd5%2022.Nc4%20Ke7%2023.Nb6%20Ra7%2024.Qh4%2B%20Qf6%2025.Qg3%20Rd8%2026.Nc4%20Kf8%2027.Ne5%20Kg7%2028.Ng4%20Qxb2%2029.Qe5%2B%20Qxe5%2030.Nxe5%20Nc3%2031.Rxd8%20Ne2%2B%2032.Kh2%20Nf4%2033.Nxc6%20Rc7%2034.Ne5%20Rxc5#52) |

#### W #3 (k = 0): latents 778

position 8 (`r2qkb1r/pp3ppp/4pn2/8/b1pP4/PnP1PN1P/R1Q2PP1/1NB1KB1R w Kkq - 6 12`), split at ply 5: Bxb3 (75% there) vs O-O (25%)

| chosen | subpar |
|---|---|
| 12.Qb2 Ne4 13.Bxc4 Qa5 [14.Bxb3] Bxb3 15.Qxb3 Rc8 16.Bd2 Bxa3 17.Nxa3 [Nxc3] [18.Bxc3] [Qxc3+] 19.Qxc3 [Rxc3] | 12.Qb2 Ne4 13.Bxc4 Qa5 14.O-O Bd6 15.Bxb3 Bxb3 16.Qxb3 O-O 17.Qxb7 Rab8 [18.Qxe4] [Rxb1] [19.Qxb1] [Qxc3] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Qb2%20Ne4%2013.Bxc4%20Qa5%2014.Bxb3%20Bxb3%2015.Qxb3%20Rc8%2016.Bd2%20Bxa3%2017.Nxa3%20Nxc3%2018.Bxc3%20Qxc3%2B%2019.Qxc3%20Rxc3#22) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Qb2%20Ne4%2013.Bxc4%20Qa5%2014.O-O%20Bd6%2015.Bxb3%20Bxb3%2016.Qxb3%20O-O%2017.Qxb7%20Rab8%2018.Qxe4%20Rxb1%2019.Qxb1%20Qxc3#22) |

position 21 (`r1b2rk1/pp2q1pp/3b4/5p1Q/4p3/2N5/PPP2PPP/R1BR2K1 w - - 2 17`), split at ply 11: Bxe7 (75% there) vs Nc7 (25%)

| chosen | subpar |
|---|---|
| 17.Bg5 Qe5 18.Rd5 Qe6 19.Nb5 Be7 20.Nc7 Qc6 21.Nxa8 Qxd5 [22.Bxe7] [Re8] 23.Qxe8# | 17.Bg5 Qe5 18.Rd5 Qe6 19.Nb5 Be7 20.Nc7 Qc6 21.Nxa8 Qxd5 22.Nc7 Qe5 23.Bxe7 [Qxe7] 24.Nd5 Qd6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Qxd4%20Nf6%205.e5%20Nfd7%206.exd6%20Nc6%207.Qe3%20e6%208.Nc3%20Bxd6%209.Bd3%20O-O%2010.O-O%20Nde5%2011.Nxe5%20Nxe5%2012.Be4%20f5%2013.Bf3%20Nxf3%2B%2014.Qxf3%20e5%2015.Rd1%20e4%2016.Qh5%20Qe7%2017.Bg5%20Qe5%2018.Rd5%20Qe6%2019.Nb5%20Be7%2020.Nc7%20Qc6%2021.Nxa8%20Qxd5%2022.Bxe7%20Re8%2023.Qxe8%23#32) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Qxd4%20Nf6%205.e5%20Nfd7%206.exd6%20Nc6%207.Qe3%20e6%208.Nc3%20Bxd6%209.Bd3%20O-O%2010.O-O%20Nde5%2011.Nxe5%20Nxe5%2012.Be4%20f5%2013.Bf3%20Nxf3%2B%2014.Qxf3%20e5%2015.Rd1%20e4%2016.Qh5%20Qe7%2017.Bg5%20Qe5%2018.Rd5%20Qe6%2019.Nb5%20Be7%2020.Nc7%20Qc6%2021.Nxa8%20Qxd5%2022.Nc7%20Qe5%2023.Bxe7%20Qxe7%2024.Nd5%20Qd6#32) |

position 39 (`r6r/bbp1k2p/p4N2/4p1p1/1P1p4/PQ3P2/2Pq1BPP/1K4n1 w - - 1 27`), split at ply 12: Kb7 (76% there) vs Kb5 (24%)

| chosen | subpar |
|---|---|
| 27.Nd5+ [Bxd5] [28.Qxd5] Qd1+ 29.Kb2 [Ne2] 30.Qxe5+ [Kd7] 31.Qg7+ [Kc6] 32.Qf6+ [Kb7] 33.Qf5 Qc1+ 34.Kb3 Qb1+ | 27.Nd5+ [Bxd5] [28.Qxd5] Qd1+ 29.Kb2 [Ne2] 30.Qxe5+ [Kd7] 31.Qg7+ [Kc6] 32.Qf6+ Kb5 33.Qe5+ Ka4 [34.Qxc7] Qc1+ |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20f6%203.Bc4%20Bc5%204.d3%20a6%205.Nc3%20b5%206.a3%20bxc4%207.dxc4%20Ba7%208.Rg1%20Nc6%209.Qd2%20Na5%2010.b4%20Nxc4%2011.Qd5%20Nb6%2012.Qa2%20Bb7%2013.Be3%20d5%2014.O-O-O%20d4%2015.Nh4%20g5%2016.Nf5%20Qd7%2017.f3%20Ne7%2018.Bf2%20Nxf5%2019.exf5%20Qxf5%2020.Ne2%20Na4%2021.Ng3%20Nc3%2022.Qb3%20Qf4%2B%2023.Rd2%20Ne2%2B%2024.Kb1%20Nxg1%2025.Nh5%20Qxd2%2026.Nxf6%2B%20Ke7%2027.Nd5%2B%20Bxd5%2028.Qxd5%20Qd1%2B%2029.Kb2%20Ne2%2030.Qxe5%2B%20Kd7%2031.Qg7%2B%20Kc6%2032.Qf6%2B%20Kb7%2033.Qf5%20Qc1%2B%2034.Kb3%20Qb1%2B#52) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20f6%203.Bc4%20Bc5%204.d3%20a6%205.Nc3%20b5%206.a3%20bxc4%207.dxc4%20Ba7%208.Rg1%20Nc6%209.Qd2%20Na5%2010.b4%20Nxc4%2011.Qd5%20Nb6%2012.Qa2%20Bb7%2013.Be3%20d5%2014.O-O-O%20d4%2015.Nh4%20g5%2016.Nf5%20Qd7%2017.f3%20Ne7%2018.Bf2%20Nxf5%2019.exf5%20Qxf5%2020.Ne2%20Na4%2021.Ng3%20Nc3%2022.Qb3%20Qf4%2B%2023.Rd2%20Ne2%2B%2024.Kb1%20Nxg1%2025.Nh5%20Qxd2%2026.Nxf6%2B%20Ke7%2027.Nd5%2B%20Bxd5%2028.Qxd5%20Qd1%2B%2029.Kb2%20Ne2%2030.Qxe5%2B%20Kd7%2031.Qg7%2B%20Kc6%2032.Qf6%2B%20Kb5%2033.Qe5%2B%20Ka4%2034.Qxc7%20Qc1%2B#52) |

#### W #4 (k = 0): latents 894

position 4 (`r1bq1b1r/3k2pp/p1p5/1p1Bp1N1/8/3P4/PPP2PPP/RNB1K2R w KQ - 0 12`), split at ply 4: Rxc8 (77% there) vs Qxc8 (23%)

| chosen | subpar |
|---|---|
| 12.Be6+ Ke7 13.Bxc8 [Rxc8] 14.O-O [h6] 15.Ne4 [g5] 16.Nbc3 [Bg7] 17.Be3 Rf8 18.Bc5+ Ke8 19.Bxf8 [Bxf8] | 12.Be6+ Ke7 13.Bxc8 Qxc8 14.O-O h6 15.Nf3 g5 16.Nxe5 Bg7 17.Ng6+ Kf6 18.Nxh8 Qxh8 19.Nc3 Re8 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Bc4%20a6%203.d3%20Nf6%204.Nf3%20b5%205.Bb3%20Nc6%206.Ng5%20d5%207.exd5%20Nxd5%208.Qf3%20Nce7%209.Qxf7%2B%20Kd7%2010.Qxd5%2B%20Nxd5%2011.Bxd5%20c6%2012.Be6%2B%20Ke7%2013.Bxc8%20Rxc8%2014.O-O%20h6%2015.Ne4%20g5%2016.Nbc3%20Bg7%2017.Be3%20Rf8%2018.Bc5%2B%20Ke8%2019.Bxf8%20Bxf8#22) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Bc4%20a6%203.d3%20Nf6%204.Nf3%20b5%205.Bb3%20Nc6%206.Ng5%20d5%207.exd5%20Nxd5%208.Qf3%20Nce7%209.Qxf7%2B%20Kd7%2010.Qxd5%2B%20Nxd5%2011.Bxd5%20c6%2012.Be6%2B%20Ke7%2013.Bxc8%20Qxc8%2014.O-O%20h6%2015.Nf3%20g5%2016.Nxe5%20Bg7%2017.Ng6%2B%20Kf6%2018.Nxh8%20Qxh8%2019.Nc3%20Re8#22) |

position 12 (`2k4r/1pb3p1/p1n4p/5R2/4p2Q/P1PpB2P/1q4P1/R6K b - - 1 22`), split at ply 7: Kb8 (82% there) vs Qxg4 (17%)

| chosen | subpar |
|---|---|
| 22...Qxa1+ 23.Bg1 d2 24.Qg4 d1=Q 25.Rf1+ [Kb8] 26.Rxd1 Qxc3 [27.Qxe4] Rd8 28.Rxd8+ Bxd8 29.Qe8 [Kc7] 30.Qf7+ | 22...Qxa1+ 23.Bg1 d2 24.Qg4 d1=Q 25.Rf1+ Qxg4 26.hxg4 Qxc3 27.Rf7 Qg3 28.Rxg7 Qh4+ 29.Bh2 Qxh2# |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.e4%20dxe4%204.f3%20exf3%205.Nxf3%20c5%206.Bd3%20cxd4%207.Ne4%20Nxe4%208.Bxe4%20Nc6%209.O-O%20Qb6%2010.Kh1%20e5%2011.Qe1%20Bd6%2012.Ng5%20Bd7%2013.a3%20O-O-O%2014.Nxf7%20Bc7%2015.Nxh8%20Rxh8%2016.Rf7%20h6%2017.c3%20a6%2018.Bf5%20Bxf5%2019.Rxf5%20d3%2020.Be3%20Qxb2%2021.h3%20e4%2022.Qh4%20Qxa1%2B%2023.Bg1%20d2%2024.Qg4%20d1%3DQ%2025.Rf1%2B%20Kb8%2026.Rxd1%20Qxc3%2027.Qxe4%20Rd8%2028.Rxd8%2B%20Bxd8%2029.Qe8%20Kc7%2030.Qf7%2B#43) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.e4%20dxe4%204.f3%20exf3%205.Nxf3%20c5%206.Bd3%20cxd4%207.Ne4%20Nxe4%208.Bxe4%20Nc6%209.O-O%20Qb6%2010.Kh1%20e5%2011.Qe1%20Bd6%2012.Ng5%20Bd7%2013.a3%20O-O-O%2014.Nxf7%20Bc7%2015.Nxh8%20Rxh8%2016.Rf7%20h6%2017.c3%20a6%2018.Bf5%20Bxf5%2019.Rxf5%20d3%2020.Be3%20Qxb2%2021.h3%20e4%2022.Qh4%20Qxa1%2B%2023.Bg1%20d2%2024.Qg4%20d1%3DQ%2025.Rf1%2B%20Qxg4%2026.hxg4%20Qxc3%2027.Rf7%20Qg3%2028.Rxg7%20Qh4%2B%2029.Bh2%20Qxh2%23#43) |

position 42 (`rnb2rk1/5ppp/p3pn2/1p1p4/q7/B3P1P1/3NNPBP/R2Q1RK1 w - - 0 14`), split at ply 15: Nb3 (80% there) vs Reb1 (15%)

| chosen | subpar |
|---|---|
| 14.Qxa4 bxa4 15.Bxf8 Kxf8 16.Rxa4 Bd7 17.Raa1 Bb5 18.Rfe1 Nc6 19.Nd4 Nxd4 20.exd4 a5 [21.Nb3] a4 | 14.Qxa4 bxa4 15.Bxf8 Kxf8 16.Rxa4 Bd7 17.Raa1 Bb5 18.Rfe1 Nc6 19.Nd4 Nxd4 20.exd4 a5 21.Reb1 Bd3 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.e3%20e6%203.Ne2%20c5%204.Nd2%20a6%205.g3%20Nf6%206.Bg2%20Be7%207.O-O%20O-O%208.c3%20b5%209.a4%20Qa5%2010.dxc5%20Bxc5%2011.b4%20Bxb4%2012.cxb4%20Qxb4%2013.Ba3%20Qxa4%2014.Qxa4%20bxa4%2015.Bxf8%20Kxf8%2016.Rxa4%20Bd7%2017.Raa1%20Bb5%2018.Rfe1%20Nc6%2019.Nd4%20Nxd4%2020.exd4%20a5%2021.Nb3%20a4#26) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.e3%20e6%203.Ne2%20c5%204.Nd2%20a6%205.g3%20Nf6%206.Bg2%20Be7%207.O-O%20O-O%208.c3%20b5%209.a4%20Qa5%2010.dxc5%20Bxc5%2011.b4%20Bxb4%2012.cxb4%20Qxb4%2013.Ba3%20Qxa4%2014.Qxa4%20bxa4%2015.Bxf8%20Kxf8%2016.Rxa4%20Bd7%2017.Raa1%20Bb5%2018.Rfe1%20Nc6%2019.Nd4%20Nxd4%2020.exd4%20a5%2021.Reb1%20Bd3#26) |

#### W #5 (k = 0): latents 499

position 32 (`r2qk2r/ppp2ppp/2n5/7b/1b1P4/2P2N1P/PB2BPP1/R2QK2R b KQkq - 0 12`), split at ply 5: Bxe2 (75% there) vs Nxe5 (25%)

| chosen | subpar |
|---|---|
| [12...Ba5] 13.O-O [O-O] 14.Ne5 [Bxe2] 15.Qxe2 Nxe5 16.Qxe5 Re8 [17.Qxa5] b6 [18.Qb5] a6 [19.Qd3] c5 [20.d5] | [12...Ba5] 13.O-O [O-O] 14.Ne5 Nxe5 15.dxe5 Qxd1 16.Raxd1 Bxe2 [17.Rfe1] [Bxd1] 18.Rxd1 Rad8 19.Re1 Rfe8 20.c4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20d5%202.exd5%20Nf6%203.Nc3%20Nxd5%204.Bc4%20Nxc3%205.bxc3%20Nc6%206.Bb2%20e5%207.Nf3%20Bg4%208.h3%20Bh5%209.Be2%20Bc5%2010.d4%20exd4%2011.cxd4%20Bb4%2B%2012.c3%20Ba5%2013.O-O%20O-O%2014.Ne5%20Bxe2%2015.Qxe2%20Nxe5%2016.Qxe5%20Re8%2017.Qxa5%20b6%2018.Qb5%20a6%2019.Qd3%20c5%2020.d5#23) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20d5%202.exd5%20Nf6%203.Nc3%20Nxd5%204.Bc4%20Nxc3%205.bxc3%20Nc6%206.Bb2%20e5%207.Nf3%20Bg4%208.h3%20Bh5%209.Be2%20Bc5%2010.d4%20exd4%2011.cxd4%20Bb4%2B%2012.c3%20Ba5%2013.O-O%20O-O%2014.Ne5%20Nxe5%2015.dxe5%20Qxd1%2016.Raxd1%20Bxe2%2017.Rfe1%20Bxd1%2018.Rxd1%20Rad8%2019.Re1%20Rfe8%2020.c4#23) |

position 10 (`2r2rk1/pp1bb1pp/1qn1pn2/3p1p2/PP1P4/2P2N1P/3NBPPB/R1Q2RK1 w - - 1 15`), split at ply 4: b6 (76% there) vs bxa6 (24%)

| chosen | subpar |
|---|---|
| 15.a5 [Qd8] 16.a6 [b6] [17.b5] [Na5] [18.Ne5] Bd6 19.Nxd7 Qxd7 20.Bxd6 Qxd6 21.Nf3 Ne4 [22.Qb2] Nxc3 | 15.a5 [Qd8] 16.a6 bxa6 17.Rxa6 Nxb4 [18.Rxa7] Nc6 [19.Ra1] Ne4 20.Nxe4 fxe4 [21.Ne5] Nxe5 22.Bxe5 Bf6 |
| [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nf6%202.d4%20e6%203.Bf4%20c5%204.e3%20cxd4%205.exd4%20Qb6%206.Qc1%20Nc6%207.c3%20Be7%208.Nbd2%20d5%209.h3%20Nh5%2010.Bh2%20O-O%2011.Be2%20Bd7%2012.O-O%20f5%2013.b4%20Nf6%2014.a4%20Rac8%2015.a5%20Qd8%2016.a6%20b6%2017.b5%20Na5%2018.Ne5%20Bd6%2019.Nxd7%20Qxd7%2020.Bxd6%20Qxd6%2021.Nf3%20Ne4%2022.Qb2%20Nxc3#28) | [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nf6%202.d4%20e6%203.Bf4%20c5%204.e3%20cxd4%205.exd4%20Qb6%206.Qc1%20Nc6%207.c3%20Be7%208.Nbd2%20d5%209.h3%20Nh5%2010.Bh2%20O-O%2011.Be2%20Bd7%2012.O-O%20f5%2013.b4%20Nf6%2014.a4%20Rac8%2015.a5%20Qd8%2016.a6%20bxa6%2017.Rxa6%20Nxb4%2018.Rxa7%20Nc6%2019.Ra1%20Ne4%2020.Nxe4%20fxe4%2021.Ne5%20Nxe5%2022.Bxe5%20Bf6#28) |

position 44 (`6rr/ppkn3p/8/2pQ4/5Bb1/3B3P/PqP5/2R2KNR b - - 0 24`), split at ply 10: Bb3 (76% there) vs Qxf8 (24%)

| chosen | subpar |
|---|---|
| [24...Kb6] 25.Qd6+ [Ka5] 26.Bd2+ [Ka4] 27.Qf4+ [Ka3] 28.Bc4 [Rf8] [29.Bb3] Rxf4+ 30.Bxf4 Rf8 31.Ne2 Bxe2+ 32.Kxe2 | [24...Kb6] 25.Qd6+ [Ka5] 26.Bd2+ [Ka4] 27.Qf4+ [Ka3] 28.Bc4 [Rf8] 29.Qxf8 Rxf8+ 30.Kg2 Qd4 [31.Bb3] Qxd2+ 32.Kg3 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Bc4%20fxe4%204.d3%20d5%205.Bb3%20exd3%206.Qxd3%20e4%207.Qd4%20Nf6%208.Nc3%20c5%209.Qe5%2B%20Be7%2010.Nxd5%20Nxd5%2011.Bxd5%20Qa5%2B%2012.Bd2%20Qb6%2013.Qxg7%20Bf6%2014.Qf7%2B%20Kd8%2015.Bxe4%20Bg4%2016.Qd5%2B%20Nd7%2017.h3%20Bh4%2B%2018.g3%20Bxg3%2B%2019.Kf1%20Qb5%2B%2020.Bd3%20Qxb2%2021.Qg5%2B%20Kc7%2022.Rc1%20Rag8%2023.Qd5%20Bxf4%2024.Bxf4%2B%20Kb6%2025.Qd6%2B%20Ka5%2026.Bd2%2B%20Ka4%2027.Qf4%2B%20Ka3%2028.Bc4%20Rf8%2029.Bb3%20Rxf4%2B%2030.Bxf4%20Rf8%2031.Ne2%20Bxe2%2B%2032.Kxe2#47) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Bc4%20fxe4%204.d3%20d5%205.Bb3%20exd3%206.Qxd3%20e4%207.Qd4%20Nf6%208.Nc3%20c5%209.Qe5%2B%20Be7%2010.Nxd5%20Nxd5%2011.Bxd5%20Qa5%2B%2012.Bd2%20Qb6%2013.Qxg7%20Bf6%2014.Qf7%2B%20Kd8%2015.Bxe4%20Bg4%2016.Qd5%2B%20Nd7%2017.h3%20Bh4%2B%2018.g3%20Bxg3%2B%2019.Kf1%20Qb5%2B%2020.Bd3%20Qxb2%2021.Qg5%2B%20Kc7%2022.Rc1%20Rag8%2023.Qd5%20Bxf4%2024.Bxf4%2B%20Kb6%2025.Qd6%2B%20Ka5%2026.Bd2%2B%20Ka4%2027.Qf4%2B%20Ka3%2028.Bc4%20Rf8%2029.Qxf8%20Rxf8%2B%2030.Kg2%20Qd4%2031.Bb3%20Qxd2%2B%2032.Kg3#47) |

#### W #6 (k = 0): latents 425

position 35 (`3rr1k1/ppp2pp1/5b1p/8/2qP4/7P/PP3PKP/R2Q2R1 w - - 4 21`), split at ply 3: Qxd4 (76% there) vs Qf3 (22%)

| chosen | subpar |
|---|---|
| 21.b3 Qxd4 [22.Qxd4] Bxd4 23.Rad1 Bb6 [24.Rxd8] Rxd8 25.Re1 Rd2 26.Re8+ Kh7 27.Re7 Rxf2+ 28.Kg3 Rxa2 | 21.b3 Qxd4 22.Qf3 Qe4 [23.Qxe4] Rxe4 24.Kh1 Bxa1 25.Rxa1 Re2 26.Kg2 Rdd2 27.Rf1 Rxa2 28.b4 Rab2 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nc3%20Nf6%203.d4%20exd4%204.Qxd4%20Nc6%205.Qd1%20d6%206.Bb5%20Be7%207.Bg5%20h6%208.Bxf6%20Bxf6%209.Qf3%20O-O%2010.Nh3%20Nd4%2011.Qd1%20Bxh3%2012.gxh3%20d5%2013.exd5%20Qd6%2014.Be2%20Rfe8%2015.Ne4%20Rxe4%2016.c3%20Rxe2%2B%2017.Kf1%20Ree8%2018.cxd4%20Qxd5%2019.Rg1%20Qc4%2B%2020.Kg2%20Rad8%2021.b3%20Qxd4%2022.Qxd4%20Bxd4%2023.Rad1%20Bb6%2024.Rxd8%20Rxd8%2025.Re1%20Rd2%2026.Re8%2B%20Kh7%2027.Re7%20Rxf2%2B%2028.Kg3%20Rxa2#40) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nc3%20Nf6%203.d4%20exd4%204.Qxd4%20Nc6%205.Qd1%20d6%206.Bb5%20Be7%207.Bg5%20h6%208.Bxf6%20Bxf6%209.Qf3%20O-O%2010.Nh3%20Nd4%2011.Qd1%20Bxh3%2012.gxh3%20d5%2013.exd5%20Qd6%2014.Be2%20Rfe8%2015.Ne4%20Rxe4%2016.c3%20Rxe2%2B%2017.Kf1%20Ree8%2018.cxd4%20Qxd5%2019.Rg1%20Qc4%2B%2020.Kg2%20Rad8%2021.b3%20Qxd4%2022.Qf3%20Qe4%2023.Qxe4%20Rxe4%2024.Kh1%20Bxa1%2025.Rxa1%20Re2%2026.Kg2%20Rdd2%2027.Rf1%20Rxa2%2028.b4%20Rab2#40) |

position 20 (`r3k1nr/1p1n4/1p1bp1pp/3p1p2/3P4/2P2N2/PP1N1PPP/R1B2RK1 b kq - 1 14`), split at ply 11: Nxe5 (78% there) vs Ke7 (22%)

| chosen | subpar |
|---|---|
| 14...g5 15.Re1 g4 16.Rxe6+ Kf7 17.Rxd6 gxf3 18.Nxf3 Ngf6 19.Ne5+ [Nxe5] 20.dxe5 Ne4 21.Rxd5 Ke6 22.c4 | 14...g5 15.Re1 g4 16.Rxe6+ Kf7 17.Rxd6 gxf3 18.Nxf3 Ngf6 19.Ne5+ Ke7 20.Rxd7+ Nxd7 21.Nxd7 Kxd7 22.Bf4 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20e6%202.Bf4%20c5%203.e3%20cxd4%204.exd4%20Qb6%205.Bc1%20d5%206.Nf3%20Bb4%2B%207.c3%20Bd6%208.Bd3%20g6%209.Nbd2%20f5%2010.Qb3%20h6%2011.Qxb6%20axb6%2012.Bb5%2B%20Bd7%2013.Bxd7%2B%20Nxd7%2014.O-O%20g5%2015.Re1%20g4%2016.Rxe6%2B%20Kf7%2017.Rxd6%20gxf3%2018.Nxf3%20Ngf6%2019.Ne5%2B%20Nxe5%2020.dxe5%20Ne4%2021.Rxd5%20Ke6%2022.c4#27) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20e6%202.Bf4%20c5%203.e3%20cxd4%204.exd4%20Qb6%205.Bc1%20d5%206.Nf3%20Bb4%2B%207.c3%20Bd6%208.Bd3%20g6%209.Nbd2%20f5%2010.Qb3%20h6%2011.Qxb6%20axb6%2012.Bb5%2B%20Bd7%2013.Bxd7%2B%20Nxd7%2014.O-O%20g5%2015.Re1%20g4%2016.Rxe6%2B%20Kf7%2017.Rxd6%20gxf3%2018.Nxf3%20Ngf6%2019.Ne5%2B%20Ke7%2020.Rxd7%2B%20Nxd7%2021.Nxd7%20Kxd7%2022.Bf4#27) |

position 19 (`r4r1k/ppq1b1pp/2npQ3/4p3/1PP5/P1P2N2/5PPP/R1B2RK1 w - - 1 18`), split at ply 2: Bxg5 (80% there) vs Rf6 (19%)

| chosen | subpar |
|---|---|
| 18.Ng5 [Bxg5] 19.Bxg5 Rae8 20.Qg4 Ne7 21.Rad1 Ng6 22.c5 dxc5 23.bxc5 Qxc5 24.Rd7 Qxc3 25.Rxb7 Qxa3 | 18.Ng5 Rf6 19.Qg4 h6 20.Ne6 Qd7 21.Qxg7# |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bc4%20Nf6%204.d3%20Be7%205.O-O%20O-O%206.Nc3%20d6%207.a3%20Be6%208.Qe2%20Bxc4%209.dxc4%20Nd7%2010.Nd5%20Nc5%2011.b4%20Ne6%2012.c3%20f5%2013.exf5%20Rxf5%2014.Qe4%20Rf8%2015.Qg4%20Qd7%2016.Nxc7%20Qxc7%2017.Qxe6%2B%20Kh8%2018.Ng5%20Bxg5%2019.Bxg5%20Rae8%2020.Qg4%20Ne7%2021.Rad1%20Ng6%2022.c5%20dxc5%2023.bxc5%20Qxc5%2024.Rd7%20Qxc3%2025.Rxb7%20Qxa3#34) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bc4%20Nf6%204.d3%20Be7%205.O-O%20O-O%206.Nc3%20d6%207.a3%20Be6%208.Qe2%20Bxc4%209.dxc4%20Nd7%2010.Nd5%20Nc5%2011.b4%20Ne6%2012.c3%20f5%2013.exf5%20Rxf5%2014.Qe4%20Rf8%2015.Qg4%20Qd7%2016.Nxc7%20Qxc7%2017.Qxe6%2B%20Kh8%2018.Ng5%20Rf6%2019.Qg4%20h6%2020.Ne6%20Qd7%2021.Qxg7%23#34) |

#### W #7 (k = 0): latents 778

position 19 (`r4r1k/ppq1b1pp/2npQ3/4p3/1PP5/P1P2N2/5PPP/R1B2RK1 w - - 1 18`), split at ply 2: Bxg5 (80% there) vs Rf6 (19%)

| chosen | subpar |
|---|---|
| [18.Ng5] [Bxg5] [19.Bxg5] Rae8 [20.Qg4] Ne7 21.Rad1 Ng6 22.c5 dxc5 23.bxc5 Qxc5 24.Rd7 Qxc3 25.Rxb7 Qxa3 | [18.Ng5] Rf6 [19.Qg4] h6 [20.Ne6] Qd7 21.Qxg7# |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bc4%20Nf6%204.d3%20Be7%205.O-O%20O-O%206.Nc3%20d6%207.a3%20Be6%208.Qe2%20Bxc4%209.dxc4%20Nd7%2010.Nd5%20Nc5%2011.b4%20Ne6%2012.c3%20f5%2013.exf5%20Rxf5%2014.Qe4%20Rf8%2015.Qg4%20Qd7%2016.Nxc7%20Qxc7%2017.Qxe6%2B%20Kh8%2018.Ng5%20Bxg5%2019.Bxg5%20Rae8%2020.Qg4%20Ne7%2021.Rad1%20Ng6%2022.c5%20dxc5%2023.bxc5%20Qxc5%2024.Rd7%20Qxc3%2025.Rxb7%20Qxa3#34) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bc4%20Nf6%204.d3%20Be7%205.O-O%20O-O%206.Nc3%20d6%207.a3%20Be6%208.Qe2%20Bxc4%209.dxc4%20Nd7%2010.Nd5%20Nc5%2011.b4%20Ne6%2012.c3%20f5%2013.exf5%20Rxf5%2014.Qe4%20Rf8%2015.Qg4%20Qd7%2016.Nxc7%20Qxc7%2017.Qxe6%2B%20Kh8%2018.Ng5%20Rf6%2019.Qg4%20h6%2020.Ne6%20Qd7%2021.Qxg7%23#34) |

position 35 (`3rr1k1/ppp2pp1/5b1p/8/2qP4/7P/PP3PKP/R2Q2R1 w - - 4 21`), split at ply 9: Kh1 (81% there) vs Kf1 (19%)

| chosen | subpar |
|---|---|
| 21.Rc1 Qd5+ 22.Kf1 Bxd4 [23.Rxc7] Qb5+ 24.Kg2 Qg5+ [25.Kh1] [Bxf2] [26.Rxg5] [Rxd1+] [27.Kg2] [hxg5] [28.Kxf2] [Rd2+] | 21.Rc1 Qd5+ 22.Kf1 Bxd4 [23.Rxc7] Qb5+ 24.Kg2 Qg5+ 25.Kf1 Qb5+ 26.Kg2 Qg5+ 27.Kf1 Qb5+ 28.Kg2 Qg5+ |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nc3%20Nf6%203.d4%20exd4%204.Qxd4%20Nc6%205.Qd1%20d6%206.Bb5%20Be7%207.Bg5%20h6%208.Bxf6%20Bxf6%209.Qf3%20O-O%2010.Nh3%20Nd4%2011.Qd1%20Bxh3%2012.gxh3%20d5%2013.exd5%20Qd6%2014.Be2%20Rfe8%2015.Ne4%20Rxe4%2016.c3%20Rxe2%2B%2017.Kf1%20Ree8%2018.cxd4%20Qxd5%2019.Rg1%20Qc4%2B%2020.Kg2%20Rad8%2021.Rc1%20Qd5%2B%2022.Kf1%20Bxd4%2023.Rxc7%20Qb5%2B%2024.Kg2%20Qg5%2B%2025.Kh1%20Bxf2%2026.Rxg5%20Rxd1%2B%2027.Kg2%20hxg5%2028.Kxf2%20Rd2%2B#40) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nc3%20Nf6%203.d4%20exd4%204.Qxd4%20Nc6%205.Qd1%20d6%206.Bb5%20Be7%207.Bg5%20h6%208.Bxf6%20Bxf6%209.Qf3%20O-O%2010.Nh3%20Nd4%2011.Qd1%20Bxh3%2012.gxh3%20d5%2013.exd5%20Qd6%2014.Be2%20Rfe8%2015.Ne4%20Rxe4%2016.c3%20Rxe2%2B%2017.Kf1%20Ree8%2018.cxd4%20Qxd5%2019.Rg1%20Qc4%2B%2020.Kg2%20Rad8%2021.Rc1%20Qd5%2B%2022.Kf1%20Bxd4%2023.Rxc7%20Qb5%2B%2024.Kg2%20Qg5%2B%2025.Kf1%20Qb5%2B%2026.Kg2%20Qg5%2B%2027.Kf1%20Qb5%2B%2028.Kg2%20Qg5%2B#40) |

position 34 (`r2qk2r/1pp1bppp/2n1p3/1p6/3PR3/P1P2N2/5PPP/R2Q2K1 b kq - 0 14`), split at ply 4: Rxa3 (81% there) vs Rh4 (17%)

| chosen | subpar |
|---|---|
| [14...O-O] [15.Qd3] [Rxa3] [16.Rxa3] [Bxa3] [17.Qxb5] [Qd5] [18.Qxb7] [Qxe4] [19.Qxc7] Qb1+ [20.Ne1] Qxe1# | [14...O-O] [15.Qd3] [Rxa3] 16.Rh4 Rxa1+ [17.Qf1] Rxf1+ [18.Kxf1] [Bxh4] [19.Nxh4] [Qxh4] [20.g3] [Qxh2] [21.Ke2] [Qh5+] [22.f3] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20O-O%2015.Qd3%20Rxa3%2016.Rxa3%20Bxa3%2017.Qxb5%20Qd5%2018.Qxb7%20Qxe4%2019.Qxc7%20Qb1%2B%2020.Ne1%20Qxe1%23#27) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20O-O%2015.Qd3%20Rxa3%2016.Rh4%20Rxa1%2B%2017.Qf1%20Rxf1%2B%2018.Kxf1%20Bxh4%2019.Nxh4%20Qxh4%2020.g3%20Qxh2%2021.Ke2%20Qh5%2B%2022.f3#27) |

#### W #8 (k = 0): latents 1566

position 49 (`1R6/3r1pbk/q2P3p/1NQ1p2n/4P1p1/5NP1/5PKP/8 w - - 0 31`), split at ply 8: Qe2 (75% there) vs Nf6 (25%)

| chosen | subpar |
|---|---|
| 31.Nxe5 Bxe5 32.Qxe5 Qa2 33.Qf5+ Kg7 34.Qxd7 [Qe2] 35.Qxf7+ [Kxf7] 36.d7 Qf3+ 37.Kf1 Qd1+ 38.Kg2 [Qf3+] | 31.Nxe5 Bxe5 32.Qxe5 Qa2 33.Qf5+ Kg7 34.Qxd7 Nf6 [35.Qe7] Nxe4 [36.d7] Qxf2+ [37.Kh1] Qf1# |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.c4%20g6%203.Nc3%20Bg7%204.e4%20d6%205.Nf3%20O-O%206.Be2%20e5%207.d5%20c6%208.O-O%20cxd5%209.cxd5%20Nh5%2010.g3%20Bh3%2011.Re1%20a6%2012.Be3%20b5%2013.b4%20Nd7%2014.a4%20bxa4%2015.Rxa4%20a5%2016.bxa5%20Rxa5%2017.Nb5%20Rxa4%2018.Qxa4%20Nc5%2019.Bxc5%20dxc5%2020.Qc4%20Qb6%2021.Nc3%20h6%2022.Rb1%20Qa5%2023.Bf1%20Bxf1%2024.Kxf1%20Rc8%2025.Kg2%20g5%2026.Rb7%20Rc7%2027.Rb8%2B%20Kh7%2028.d6%20Rd7%2029.Nb5%20Qa6%2030.Qxc5%20g4%2031.Nxe5%20Bxe5%2032.Qxe5%20Qa2%2033.Qf5%2B%20Kg7%2034.Qxd7%20Qe2%2035.Qxf7%2B%20Kxf7%2036.d7%20Qf3%2B%2037.Kf1%20Qd1%2B%2038.Kg2%20Qf3%2B#60) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.c4%20g6%203.Nc3%20Bg7%204.e4%20d6%205.Nf3%20O-O%206.Be2%20e5%207.d5%20c6%208.O-O%20cxd5%209.cxd5%20Nh5%2010.g3%20Bh3%2011.Re1%20a6%2012.Be3%20b5%2013.b4%20Nd7%2014.a4%20bxa4%2015.Rxa4%20a5%2016.bxa5%20Rxa5%2017.Nb5%20Rxa4%2018.Qxa4%20Nc5%2019.Bxc5%20dxc5%2020.Qc4%20Qb6%2021.Nc3%20h6%2022.Rb1%20Qa5%2023.Bf1%20Bxf1%2024.Kxf1%20Rc8%2025.Kg2%20g5%2026.Rb7%20Rc7%2027.Rb8%2B%20Kh7%2028.d6%20Rd7%2029.Nb5%20Qa6%2030.Qxc5%20g4%2031.Nxe5%20Bxe5%2032.Qxe5%20Qa2%2033.Qf5%2B%20Kg7%2034.Qxd7%20Nf6%2035.Qe7%20Nxe4%2036.d7%20Qxf2%2B%2037.Kh1%20Qf1%23#60) |

position 29 (`r1b1k1nr/p2ppp1p/6p1/8/8/q7/P1P1BPPP/R2Q1K1R w kq - 0 15`), split at ply 5: Re1 (77% there) vs Bf3 (23%)

| chosen | subpar |
|---|---|
| 15.g3 [Nf6] 16.Kg2 [O-O] [17.Re1] [Bb7+] [18.Kg1] [Qc5] 19.Bf3 Bxf3 [20.Qxf3] Qxc2 [21.Rxe7] Qb2 [22.Rae1] Qxa2 | 15.g3 [Nf6] 16.Kg2 [O-O] 17.Bf3 [Rb8] [18.Re1] e6 [19.Qd4] Nd5 [20.Bxd5] exd5 [21.Qxd5] Bb7 [22.Qxb7] Rxb7 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20g6%205.Nc3%20Bg7%206.Be3%20Nf6%207.Nxc6%20bxc6%208.e5%20Ng8%209.Bd4%20c5%2010.Bxc5%20Qc7%2011.Ba3%20Bxe5%2012.Be2%20Bxc3%2B%2013.bxc3%20Qxc3%2B%2014.Kf1%20Qxa3%2015.g3%20Nf6%2016.Kg2%20O-O%2017.Re1%20Bb7%2B%2018.Kg1%20Qc5%2019.Bf3%20Bxf3%2020.Qxf3%20Qxc2%2021.Rxe7%20Qb2%2022.Rae1%20Qxa2#28) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20g6%205.Nc3%20Bg7%206.Be3%20Nf6%207.Nxc6%20bxc6%208.e5%20Ng8%209.Bd4%20c5%2010.Bxc5%20Qc7%2011.Ba3%20Bxe5%2012.Be2%20Bxc3%2B%2013.bxc3%20Qxc3%2B%2014.Kf1%20Qxa3%2015.g3%20Nf6%2016.Kg2%20O-O%2017.Bf3%20Rb8%2018.Re1%20e6%2019.Qd4%20Nd5%2020.Bxd5%20exd5%2021.Qxd5%20Bb7%2022.Qxb7%20Rxb7#28) |

position 33 (`r2qk1r1/3bbpnp/p3N1p1/2ppB1P1/1p2P2P/1P3Q2/P1P2P2/2KR1B1R b q - 0 19`), split at ply 8: Bc4 (79% there) vs Bxa6 (21%)

| chosen | subpar |
|---|---|
| 19...Nxe6 [20.Rxd5] Nd4 [21.Bxd4] cxd4 [22.Rxd4] Rc8 [23.Bc4] Be6 24.Rxd8+ Rxd8 25.Bxe6 fxe6 [26.Rd1] Rxd1+ [27.Qxd1] | 19...Nxe6 [20.Rxd5] Nd4 [21.Bxd4] cxd4 [22.Rxd4] Rc8 23.Bxa6 Rc6 24.Bb5 Rc7 25.Bxd7+ Rxd7 26.Rhd1 Rxd4 [27.Rxd4] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.Bf4%20a6%204.e3%20e6%205.g4%20Bb4%206.Ne2%20Be7%207.g5%20Nh5%208.h4%20b5%209.Bh2%20Nc6%2010.Nc1%20g6%2011.Nb3%20Ng7%2012.Qf3%20b4%2013.Na4%20Bd7%2014.O-O-O%20Nxd4%2015.Nxd4%20Bxa4%2016.Be5%20Rg8%2017.e4%20c5%2018.b3%20Bd7%2019.Nxe6%20Nxe6%2020.Rxd5%20Nd4%2021.Bxd4%20cxd4%2022.Rxd4%20Rc8%2023.Bc4%20Be6%2024.Rxd8%2B%20Rxd8%2025.Bxe6%20fxe6%2026.Rd1%20Rxd1%2B%2027.Qxd1#37) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.Bf4%20a6%204.e3%20e6%205.g4%20Bb4%206.Ne2%20Be7%207.g5%20Nh5%208.h4%20b5%209.Bh2%20Nc6%2010.Nc1%20g6%2011.Nb3%20Ng7%2012.Qf3%20b4%2013.Na4%20Bd7%2014.O-O-O%20Nxd4%2015.Nxd4%20Bxa4%2016.Be5%20Rg8%2017.e4%20c5%2018.b3%20Bd7%2019.Nxe6%20Nxe6%2020.Rxd5%20Nd4%2021.Bxd4%20cxd4%2022.Rxd4%20Rc8%2023.Bxa6%20Rc6%2024.Bb5%20Rc7%2025.Bxd7%2B%20Rxd7%2026.Rhd1%20Rxd4%2027.Rxd4#37) |

#### W #9 (k = 0): latents 425

position 8 (`r2qkb1r/pp3ppp/4pn2/8/b1pP4/PnP1PN1P/R1Q2PP1/1NB1KB1R w Kkq - 6 12`), split at ply 5: Bxb3 (75% there) vs O-O (25%)

| chosen | subpar |
|---|---|
| 12.Qb2 Ne4 13.Bxc4 Qa5 [14.Bxb3] Bxb3 15.Qxb3 Rc8 16.Bd2 Bxa3 17.Nxa3 Nxc3 18.Bxc3 Qxc3+ 19.Qxc3 Rxc3 | 12.Qb2 Ne4 13.Bxc4 Qa5 14.O-O Bd6 [15.Bxb3] Bxb3 16.Qxb3 O-O 17.Qxb7 Rab8 18.Qxe4 Rxb1 19.Qxb1 Qxc3 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Qb2%20Ne4%2013.Bxc4%20Qa5%2014.Bxb3%20Bxb3%2015.Qxb3%20Rc8%2016.Bd2%20Bxa3%2017.Nxa3%20Nxc3%2018.Bxc3%20Qxc3%2B%2019.Qxc3%20Rxc3#22) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Qb2%20Ne4%2013.Bxc4%20Qa5%2014.O-O%20Bd6%2015.Bxb3%20Bxb3%2016.Qxb3%20O-O%2017.Qxb7%20Rab8%2018.Qxe4%20Rxb1%2019.Qxb1%20Qxc3#22) |

position 17 (`r3k2r/pp2qp1p/2n1bnp1/2p5/2N3P1/2bPBP2/P1PN3P/3QKB1R w Kkq - 1 14`), split at ply 2: Bxc4 (79% there) vs O-O (21%)

| chosen | subpar |
|---|---|
| 14.Bh3 [Bxc4] 15.dxc4 Qxe3+ 16.Kf1 Bxd2 17.g5 Qxf3+ [18.Qxf3] Nh5 19.Qe2+ Kf8 20.Qxd2 Kg7 21.Qc3+ Kg8 | 14.Bh3 O-O 15.O-O [Bxc4] 16.Nxc4 Bd4 [17.Bxd4] cxd4 18.g5 Nd5 19.f4 Ne3 [20.Nxe3] dxe3 21.Re1 Qc5 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.d3%20g6%203.Nf3%20Bg7%204.e5%20Nc6%205.Bf4%20d6%206.exd6%20Bxb2%207.dxe7%20Qxe7%2B%208.Be3%20Bxa1%209.Na3%20Bc3%2B%2010.Nd2%20Nf6%2011.Nc4%20Bg4%2012.f3%20Bf5%2013.g4%20Be6%2014.Bh3%20Bxc4%2015.dxc4%20Qxe3%2B%2016.Kf1%20Bxd2%2017.g5%20Qxf3%2B%2018.Qxf3%20Nh5%2019.Qe2%2B%20Kf8%2020.Qxd2%20Kg7%2021.Qc3%2B%20Kg8#26) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.d3%20g6%203.Nf3%20Bg7%204.e5%20Nc6%205.Bf4%20d6%206.exd6%20Bxb2%207.dxe7%20Qxe7%2B%208.Be3%20Bxa1%209.Na3%20Bc3%2B%2010.Nd2%20Nf6%2011.Nc4%20Bg4%2012.f3%20Bf5%2013.g4%20Be6%2014.Bh3%20O-O%2015.O-O%20Bxc4%2016.Nxc4%20Bd4%2017.Bxd4%20cxd4%2018.g5%20Nd5%2019.f4%20Ne3%2020.Nxe3%20dxe3%2021.Re1%20Qc5#26) |

position 42 (`rnb2rk1/5ppp/p3pn2/1p1p4/q7/B3P1P1/3NNPBP/R2Q1RK1 w - - 0 14`), split at ply 1: Qxa4 (79% there) vs Bxf8 (21%)

| chosen | subpar |
|---|---|
| [14.Qxa4] bxa4 15.Bxf8 Kxf8 16.Rxa4 Bd7 17.Raa1 Bb5 18.Rfe1 Nc6 19.Nd4 [Nxd4] 20.exd4 a5 21.Nb3 a4 | 14.Bxf8 Qxd1 15.Rfxd1 Kxf8 16.Nd4 Bb7 17.N2b3 Nbd7 18.Na5 Rb8 [19.Nxb7] Rxb7 20.Rxa6 Nc5 21.Ra8+ Ke7 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.e3%20e6%203.Ne2%20c5%204.Nd2%20a6%205.g3%20Nf6%206.Bg2%20Be7%207.O-O%20O-O%208.c3%20b5%209.a4%20Qa5%2010.dxc5%20Bxc5%2011.b4%20Bxb4%2012.cxb4%20Qxb4%2013.Ba3%20Qxa4%2014.Qxa4%20bxa4%2015.Bxf8%20Kxf8%2016.Rxa4%20Bd7%2017.Raa1%20Bb5%2018.Rfe1%20Nc6%2019.Nd4%20Nxd4%2020.exd4%20a5%2021.Nb3%20a4#26) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.e3%20e6%203.Ne2%20c5%204.Nd2%20a6%205.g3%20Nf6%206.Bg2%20Be7%207.O-O%20O-O%208.c3%20b5%209.a4%20Qa5%2010.dxc5%20Bxc5%2011.b4%20Bxb4%2012.cxb4%20Qxb4%2013.Ba3%20Qxa4%2014.Bxf8%20Qxd1%2015.Rfxd1%20Kxf8%2016.Nd4%20Bb7%2017.N2b3%20Nbd7%2018.Na5%20Rb8%2019.Nxb7%20Rxb7%2020.Rxa6%20Nc5%2021.Ra8%2B%20Ke7#26) |

#### W #10 (k = 0): latents 499

position 20 (`r3k1nr/1p1n4/1p1bp1pp/3p1p2/3P4/2P2N2/PP1N1PPP/R1B2RK1 b kq - 1 14`), split at ply 11: Nxe5 (78% there) vs Ke7 (22%)

| chosen | subpar |
|---|---|
| 14...g5 15.Re1 g4 [16.Rxe6+] Kf7 [17.Rxd6] gxf3 [18.Nxf3] Ngf6 [19.Ne5+] [Nxe5] [20.dxe5] [Ne4] [21.Rxd5] Ke6 [22.c4] | 14...g5 15.Re1 g4 [16.Rxe6+] Kf7 [17.Rxd6] gxf3 [18.Nxf3] Ngf6 [19.Ne5+] Ke7 [20.Rxd7+] [Nxd7] [21.Nxd7] Kxd7 22.Bf4 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20e6%202.Bf4%20c5%203.e3%20cxd4%204.exd4%20Qb6%205.Bc1%20d5%206.Nf3%20Bb4%2B%207.c3%20Bd6%208.Bd3%20g6%209.Nbd2%20f5%2010.Qb3%20h6%2011.Qxb6%20axb6%2012.Bb5%2B%20Bd7%2013.Bxd7%2B%20Nxd7%2014.O-O%20g5%2015.Re1%20g4%2016.Rxe6%2B%20Kf7%2017.Rxd6%20gxf3%2018.Nxf3%20Ngf6%2019.Ne5%2B%20Nxe5%2020.dxe5%20Ne4%2021.Rxd5%20Ke6%2022.c4#27) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20e6%202.Bf4%20c5%203.e3%20cxd4%204.exd4%20Qb6%205.Bc1%20d5%206.Nf3%20Bb4%2B%207.c3%20Bd6%208.Bd3%20g6%209.Nbd2%20f5%2010.Qb3%20h6%2011.Qxb6%20axb6%2012.Bb5%2B%20Bd7%2013.Bxd7%2B%20Nxd7%2014.O-O%20g5%2015.Re1%20g4%2016.Rxe6%2B%20Kf7%2017.Rxd6%20gxf3%2018.Nxf3%20Ngf6%2019.Ne5%2B%20Ke7%2020.Rxd7%2B%20Nxd7%2021.Nxd7%20Kxd7%2022.Bf4#27) |

position 0 (`2kr2r1/ppp5/2n1RbNp/2q2p1P/3p4/2PQ1P1B/PPKN3P/6R1 b - - 0 20`), split at ply 3: Rxd3 (80% there) vs Nb4+ (19%)

| chosen | subpar |
|---|---|
| 20...dxc3 21.bxc3 [Rxd3] 22.Kxd3 Qxg1 23.Bxf5 Rd8+ 24.Kc2 Qxh2 25.Rxf6+ [Kb8] 26.Be4 Qxd2+ 27.Kb3 Na5+ 28.Kb4 | 20...dxc3 21.bxc3 Nb4+ [22.Kb3] Nxd3 23.Rxf6 Qb5+ 24.Kc2 Qb2+ 25.Kd1 Nf2+ 26.Ke2 Qxd2+ 27.Kf1 Nxh3 28.Ne7+ |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.bxc3%20Rxd3%2022.Kxd3%20Qxg1%2023.Bxf5%20Rd8%2B%2024.Kc2%20Qxh2%2025.Rxf6%2B%20Kb8%2026.Be4%20Qxd2%2B%2027.Kb3%20Na5%2B%2028.Kb4#39) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.bxc3%20Nb4%2B%2022.Kb3%20Nxd3%2023.Rxf6%20Qb5%2B%2024.Kc2%20Qb2%2B%2025.Kd1%20Nf2%2B%2026.Ke2%20Qxd2%2B%2027.Kf1%20Nxh3%2028.Ne7%2B#39) |

position 11 (`r3k2r/p3bp2/qn2p3/1R2Pp1p/3P3P/3Q1N2/3B1PP1/1R4K1 w kq - 3 21`), split at ply 6: Rfd8 (79% there) vs exd5 (18%)

| chosen | subpar |
|---|---|
| 21.Ba5 [O-O] 22.Bxb6 axb6 23.d5 [Rfd8] 24.d6 [Bf8] 25.Ng5 Bh6 26.Qg3 Kf8 27.Nh7+ Ke8 28.Nf6+ Kf8 | 21.Ba5 [O-O] 22.Bxb6 axb6 23.d5 exd5 24.Qxd5 Rfd8 25.Qb3 Bc5 26.Ng5 Rd7 27.e6 fxe6 28.Nxe6 Re8 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.e5%20Bf5%204.h4%20h5%205.Bd3%20Bxd3%206.Qxd3%20Qa5%2B%207.b4%20Qxb4%2B%208.Nd2%20Qb5%209.c4%20dxc4%2010.Nxc4%20e6%2011.Bd2%20Qa6%2012.Nf3%20Nh6%2013.O-O%20Nf5%2014.Rab1%20b5%2015.Ne3%20g6%2016.a4%20Be7%2017.Nxf5%20gxf5%2018.axb5%20cxb5%2019.Rxb5%20Nd7%2020.Rfb1%20Nb6%2021.Ba5%20O-O%2022.Bxb6%20axb6%2023.d5%20Rfd8%2024.d6%20Bf8%2025.Ng5%20Bh6%2026.Qg3%20Kf8%2027.Nh7%2B%20Ke8%2028.Nf6%2B%20Kf8#40) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.e5%20Bf5%204.h4%20h5%205.Bd3%20Bxd3%206.Qxd3%20Qa5%2B%207.b4%20Qxb4%2B%208.Nd2%20Qb5%209.c4%20dxc4%2010.Nxc4%20e6%2011.Bd2%20Qa6%2012.Nf3%20Nh6%2013.O-O%20Nf5%2014.Rab1%20b5%2015.Ne3%20g6%2016.a4%20Be7%2017.Nxf5%20gxf5%2018.axb5%20cxb5%2019.Rxb5%20Nd7%2020.Rfb1%20Nb6%2021.Ba5%20O-O%2022.Bxb6%20axb6%2023.d5%20exd5%2024.Qxd5%20Rfd8%2025.Qb3%20Bc5%2026.Ng5%20Rd7%2027.e6%20fxe6%2028.Nxe6%20Re8#40) |

