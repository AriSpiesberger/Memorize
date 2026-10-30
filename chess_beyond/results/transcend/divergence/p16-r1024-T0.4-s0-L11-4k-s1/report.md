# Dynamic concepts with a persistence window

Per model, at 50 positions (1024 rollouts of 16 plies, T = 0.4, the model both colours): a latent on at a ply when z > 0.5 x mu_j. Pairs: at each branching point the most-played move against every move with >= 2% of that point's weight, each by its most frequent line, <= 50 per position. LP: min |v|_1 + 2.0 xi s.t. v . (z^c_tau - z^s_tau) >= 1 - xi for tau = t..t+k. Families: Jaccard >= 0.5 of supports with a family's core, within one half (25 / 25 positions by game); recurrence: the share of the other half's pairs (same k) where the family's mean v (|v|_1 = 1) gives >= 0.5 on every ply of the window; null: 200 random v's per family on rate-matched latents (firing-rate deciles). Persistence: plies in a row from the split with v . d >= 0.5, median over the other half's k = 0 pairs where it is on at the split.

## S

| k | pairs | nonzero v | families | held-out recurrence: median / 90% / max | null 95th: median | null (every draw): 90% / 99% | families above their null 95th (chance: 5%) |
|---|---|---|---|---|---|---|---|
| 0 | 2500 | 100% | 651 | 0.6% / 2.6% / 8.9% | 1.5% | 2.2% / 5.6% | 41 (6%) |
| 2 | 2500 | 35% | 661 | 0.0% / 0.1% / 1.3% | 0.0% | 0.1% / 0.3% | 47 (7%) |
| 4 | 2500 | 18% | 382 | 0.0% / 0.1% / 1.4% | 0.0% | 0.0% / 0.2% | 40 (10%) |
| 6 | 2500 | 14% | 311 | 0.0% / 0.2% / 1.6% | 0.0% | 0.0% / 0.1% | 51 (16%) |

### S: the top 20 families by held-out recurrence

| # | k | latents (weight) | found in | held out on | recurrence | null 95th | persistence (pairs on at split) | positions found |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 499 (1.00) | A (11 v's) | B | 8.9% | 5.5% | 1.0 (111) | 3, 7, 20, 25, 29, 31, 34, 45, 46 |
| 2 | 0 | 1006 (1.00) | A (1 v's) | B | 8.5% | 6.1% | 1.0 (106) | 34 |
| 3 | 0 | 746 (1.00) | A (2 v's) | B | 7.7% | 5.4% | 1.0 (96) | 19, 38 |
| 4 | 0 | 1006 (1.00) | B (2 v's) | A | 7.6% | 5.1% | 1.0 (95) | 23, 27 |
| 5 | 0 | 746 (1.00) | B (8 v's) | A | 7.4% | 4.7% | 1.0 (93) | 13, 17, 30, 32, 39, 47, 48 |
| 6 | 0 | 894 (1.00) | B (2 v's) | A | 7.4% | 5.6% | 1.0 (92) | 10, 32 |
| 7 | 0 | 140 (1.00) | B (21 v's) | A | 7.0% | 5.8% | 1.0 (87) | 10, 12, 15, 21, 22, 27, 30, 32, 36, 39, 41, 42 ... |
| 8 | 0 | 894 (1.00) | A (2 v's) | B | 6.9% | 5.5% | 1.0 (86) | 29, 34 |
| 9 | 0 | 499 (1.00) | B (14 v's) | A | 6.6% | 5.6% | 1.0 (83) | 8, 10, 12, 14, 17, 22, 32, 40, 43, 47 |
| 10 | 0 | 778 (1.00) | A (1 v's) | B | 6.6% | 6.3% | 1.0 (82) | 37 |
| 11 | 0 | 327 (1.00) | A (7 v's) | B | 6.5% | 5.5% | 1.0 (81) | 3, 26, 33, 34, 37 |
| 12 | 0 | 62 (1.00) | B (47 v's) | A | 6.5% | 5.3% | 1.0 (81) | 1, 2, 4, 8, 10, 12, 13, 14, 15, 17, 23, 27 ... |
| 13 | 0 | 62 (1.00) | A (42 v's) | B | 6.0% | 6.1% | 1.0 (75) | 0, 3, 5, 6, 7, 11, 16, 18, 20, 24, 25, 28 ... |
| 14 | 0 | 425 (1.00) | A (3 v's) | B | 5.5% | 6.2% | 1.0 (69) | 3 |
| 15 | 0 | 550 (1.00) | B (2 v's) | A | 5.3% | 4.6% | 1.0 (66) | 1, 39 |
| 16 | 0 | 1326 (1.00) | B (1 v's) | A | 4.8% | 5.7% | 1.0 (60) | 48 |
| 17 | 0 | 2039 (1.00) | B (1 v's) | A | 4.6% | 4.8% | 1.0 (57) | 17 |
| 18 | 0 | 700 (1.00) | A (1 v's) | B | 4.3% | 5.5% | 1.0 (54) | 29 |
| 19 | 0 | 425 (1.00) | B (2 v's) | A | 4.2% | 5.1% | 1.0 (52) | 2, 10 |
| 20 | 0 | 217 (1.00) | B (16 v's) | A | 4.2% | 5.7% | 1.0 (52) | 4, 12, 13, 14, 15, 22, 30, 40, 41, 43, 47 |

#### S #1 (k = 0): latents 499

position 43 (`1r1qk2r/p2b2pp/1p3n2/n3Qp2/P2Pp3/4PP2/3N2PP/R1B1KB1R b KQk - 1 17`), split at ply 2: Ba3 (50% there) vs fxe4 (48%)

| chosen | subpar |
|---|---|
| [17...Kf7] [18.Ba3] Re8 [19.Qf4] Kg8 [20.Bb5] Bxb5 21.axb5 exf3 22.gxf3 Nd5 [23.Qxf5] Nxe3 [24.Qd3] Qh4+ 25.Ke2 | [17...Kf7] 18.fxe4 Re8 [19.Qf4] Nxe4 20.Nxe4 Rxe4 [21.Qf3] Qe7 22.Bd3 Rxd4 23.O-O [Rxd3] 24.Qxf5+ [Kg8] 25.Qxd3 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20f6%203.c4%20e5%204.e3%20e4%205.Nfd2%20c6%206.Nc3%20Bb4%207.cxd5%20cxd5%208.f3%20f5%209.Qa4%2B%20Nc6%2010.a3%20Bxc3%2011.bxc3%20Bd7%2012.Qb3%20Rb8%2013.c4%20dxc4%2014.Qxc4%20Nf6%2015.a4%20Na5%2016.Qc5%20b6%2017.Qe5%2B%20Kf7%2018.Ba3%20Re8%2019.Qf4%20Kg8%2020.Bb5%20Bxb5%2021.axb5%20exf3%2022.gxf3%20Nd5%2023.Qxf5%20Nxe3%2024.Qd3%20Qh4%2B%2025.Ke2#33) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20f6%203.c4%20e5%204.e3%20e4%205.Nfd2%20c6%206.Nc3%20Bb4%207.cxd5%20cxd5%208.f3%20f5%209.Qa4%2B%20Nc6%2010.a3%20Bxc3%2011.bxc3%20Bd7%2012.Qb3%20Rb8%2013.c4%20dxc4%2014.Qxc4%20Nf6%2015.a4%20Na5%2016.Qc5%20b6%2017.Qe5%2B%20Kf7%2018.fxe4%20Re8%2019.Qf4%20Nxe4%2020.Nxe4%20Rxe4%2021.Qf3%20Qe7%2022.Bd3%20Rxd4%2023.O-O%20Rxd3%2024.Qxf5%2B%20Kg8%2025.Qxd3#33) |

position 47 (`r2qr1k1/pp3ppp/1bn5/3p4/3Nb2n/1NP2PBP/PP2B1PK/R2Q1R2 b - - 0 16`), split at ply 4: Bf2 (49% there) vs Nxf5 (48%)

| chosen | subpar |
|---|---|
| [16...Bg6] 17.Qd2 Nf5 [18.Bf2] Qd6+ [19.Kg1] Ng3 [20.Rfe1] Nxe2+ 21.Rxe2 Rxe2 [22.Qxe2] Nxd4 [23.Nxd4] Bxd4 24.Bxd4 | [16...Bg6] 17.Qd2 Nf5 18.Nxf5 Bxf5 19.Rfe1 d4 20.cxd4 Nxd4 21.Nxd4 [Qxd4] 22.Qxd4 Bxd4 23.Bb5 [Rxe1] 24.Rxe1 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bg6%2017.Qd2%20Nf5%2018.Bf2%20Qd6%2B%2019.Kg1%20Ng3%2020.Rfe1%20Nxe2%2B%2021.Rxe2%20Rxe2%2022.Qxe2%20Nxd4%2023.Nxd4%20Bxd4%2024.Bxd4#31) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bg6%2017.Qd2%20Nf5%2018.Nxf5%20Bxf5%2019.Rfe1%20d4%2020.cxd4%20Nxd4%2021.Nxd4%20Qxd4%2022.Qxd4%20Bxd4%2023.Bb5%20Rxe1%2024.Rxe1#31) |

position 13 (`r2qkb1r/ppp3pp/5n2/3p4/8/2P1BB2/PP3P1P/RN1QK2R b KQkq - 2 11`), split at ply 9: a4 (53% there) vs Nxe4 (47%)

| chosen | subpar |
|---|---|
| 11...Bd6 12.Nd2 O-O 13.Qb3 c6 14.O-O-O a5 15.Ne4 [a4] [16.Qc2] Nxe4 17.Bxe4 h6 18.Bh7+ [Kh8] 19.Bg6 | 11...Bd6 12.Nd2 O-O 13.Qb3 c6 14.O-O-O a5 15.Ne4 Nxe4 16.Bxe4 a4 [17.Qc2] h6 18.Rhg1 a3 19.b3 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.d4%20Bxf5%205.Bd3%20Bg4%206.c3%20e5%207.dxe5%20Nxe5%208.Be2%20Nxf3%2B%209.gxf3%20Bxf3%2010.Bxf3%20Nf6%2011.Be3%20Bd6%2012.Nd2%20O-O%2013.Qb3%20c6%2014.O-O-O%20a5%2015.Ne4%20a4%2016.Qc2%20Nxe4%2017.Bxe4%20h6%2018.Bh7%2B%20Kh8%2019.Bg6#21) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.d4%20Bxf5%205.Bd3%20Bg4%206.c3%20e5%207.dxe5%20Nxe5%208.Be2%20Nxf3%2B%209.gxf3%20Bxf3%2010.Bxf3%20Nf6%2011.Be3%20Bd6%2012.Nd2%20O-O%2013.Qb3%20c6%2014.O-O-O%20a5%2015.Ne4%20Nxe4%2016.Bxe4%20a4%2017.Qc2%20h6%2018.Rhg1%20a3%2019.b3#21) |

#### S #2 (k = 0): latents 1006

position 47 (`r2qr1k1/pp3ppp/1bn5/3p4/3Nb2n/1NP2PBP/PP2B1PK/R2Q1R2 b - - 0 16`), split at ply 4: Bf2 (49% there) vs Nxf5 (48%)

| chosen | subpar |
|---|---|
| [16...Bg6] [17.Qd2] Nf5 [18.Bf2] Qd6+ [19.Kg1] Ng3 [20.Rfe1] Nxe2+ 21.Rxe2 Rxe2 22.Qxe2 Nxd4 23.Nxd4 Bxd4 24.Bxd4 | [16...Bg6] [17.Qd2] Nf5 18.Nxf5 Bxf5 [19.Rfe1] d4 [20.cxd4] Nxd4 21.Nxd4 Qxd4 22.Qxd4 Bxd4 23.Bb5 Rxe1 24.Rxe1 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bg6%2017.Qd2%20Nf5%2018.Bf2%20Qd6%2B%2019.Kg1%20Ng3%2020.Rfe1%20Nxe2%2B%2021.Rxe2%20Rxe2%2022.Qxe2%20Nxd4%2023.Nxd4%20Bxd4%2024.Bxd4#31) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bg6%2017.Qd2%20Nf5%2018.Nxf5%20Bxf5%2019.Rfe1%20d4%2020.cxd4%20Nxd4%2021.Nxd4%20Qxd4%2022.Qxd4%20Bxd4%2023.Bb5%20Rxe1%2024.Rxe1#31) |

position 17 (`r3k2r/pp2qp1p/2n1bnp1/2p5/2N3P1/2bPBP2/P1PN3P/3QKB1R w Kkq - 1 14`), split at ply 8: O-O (52% there) vs Ne5 (48%)

| chosen | subpar |
|---|---|
| [14.Kf2] [Bxd2] 15.Qxd2 Bxc4 16.dxc4 Rd8 17.Bd3 [O-O] 18.h4 [Ne5] 19.h5 Nxd3+ 20.cxd3 Rfe8 21.hxg6 fxg6 | [14.Kf2] [Bxd2] 15.Qxd2 Bxc4 16.dxc4 Rd8 17.Bd3 Ne5 18.h3 [Nxd3+] 19.cxd3 O-O 20.Re1 Rfe8 21.Bg5 Qd6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.d3%20g6%203.Nf3%20Bg7%204.e5%20Nc6%205.Bf4%20d6%206.exd6%20Bxb2%207.dxe7%20Qxe7%2B%208.Be3%20Bxa1%209.Na3%20Bc3%2B%2010.Nd2%20Nf6%2011.Nc4%20Bg4%2012.f3%20Bf5%2013.g4%20Be6%2014.Kf2%20Bxd2%2015.Qxd2%20Bxc4%2016.dxc4%20Rd8%2017.Bd3%20O-O%2018.h4%20Ne5%2019.h5%20Nxd3%2B%2020.cxd3%20Rfe8%2021.hxg6%20fxg6#26) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.d3%20g6%203.Nf3%20Bg7%204.e5%20Nc6%205.Bf4%20d6%206.exd6%20Bxb2%207.dxe7%20Qxe7%2B%208.Be3%20Bxa1%209.Na3%20Bc3%2B%2010.Nd2%20Nf6%2011.Nc4%20Bg4%2012.f3%20Bf5%2013.g4%20Be6%2014.Kf2%20Bxd2%2015.Qxd2%20Bxc4%2016.dxc4%20Rd8%2017.Bd3%20Ne5%2018.h3%20Nxd3%2B%2019.cxd3%20O-O%2020.Re1%20Rfe8%2021.Bg5%20Qd6#26) |

position 30 (`1rbq1rk1/5ppp/2np3b/p2Np3/1p2P2P/2PQ2P1/PPN2PB1/R4RK1 b - - 1 17`), split at ply 11: Qa7 (54% there) vs Bxd5 (46%)

| chosen | subpar |
|---|---|
| 17...bxc3 18.bxc3 [Be6] 19.Nce3 [Ne7] 20.Nxe7+ Qxe7 21.Rfd1 [Rfd8] 22.Nd5 [Qa7] 23.Rab1 [Kf8] [24.Rb5] [Rxb5] 25.Qxb5 | 17...bxc3 18.bxc3 [Be6] 19.Nce3 [Ne7] 20.Nxe7+ Qxe7 21.Rfd1 [Rfd8] 22.Nd5 Bxd5 23.Qxd5 Qc7 24.Bf1 Qxc3 25.Bc4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20e5%206.Ndb5%20d6%207.Bg5%20a6%208.Na3%20b5%209.Nd5%20Be7%2010.Bxf6%20Bxf6%2011.c3%20Bg5%2012.h4%20Bh6%2013.g3%20O-O%2014.Bg2%20Rb8%2015.Nc2%20a5%2016.O-O%20b4%2017.Qd3%20bxc3%2018.bxc3%20Be6%2019.Nce3%20Ne7%2020.Nxe7%2B%20Qxe7%2021.Rfd1%20Rfd8%2022.Nd5%20Qa7%2023.Rab1%20Kf8%2024.Rb5%20Rxb5%2025.Qxb5#33) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20e5%206.Ndb5%20d6%207.Bg5%20a6%208.Na3%20b5%209.Nd5%20Be7%2010.Bxf6%20Bxf6%2011.c3%20Bg5%2012.h4%20Bh6%2013.g3%20O-O%2014.Bg2%20Rb8%2015.Nc2%20a5%2016.O-O%20b4%2017.Qd3%20bxc3%2018.bxc3%20Be6%2019.Nce3%20Ne7%2020.Nxe7%2B%20Qxe7%2021.Rfd1%20Rfd8%2022.Nd5%20Bxd5%2023.Qxd5%20Qc7%2024.Bf1%20Qxc3%2025.Bc4#33) |

#### S #3 (k = 0): latents 746

position 10 (`2r2rk1/pp1bb1pp/1qn1pn2/3p1p2/PP1P4/2P2N1P/3NBPPB/R1Q2RK1 w - - 1 15`), split at ply 1: Qb2 (53% there) vs a5 (46%)

| chosen | subpar |
|---|---|
| [15.Qb2] Ne4 16.a5 [Qd8] 17.Nxe4 fxe4 18.Ne5 Nxe5 19.Bxe5 Bf6 20.Bd6 Rf7 21.b5 Be7 22.Be5 Bf6 | 15.a5 [Qd8] [16.Qb2] Ne4 17.Nb3 Bd6 18.Bxd6 Nxd6 19.Nc5 Ne4 20.Nxb7 [Qc7] 21.Nc5 Nxc5 22.bxc5 Rb8 |
| [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nf6%202.d4%20e6%203.Bf4%20c5%204.e3%20cxd4%205.exd4%20Qb6%206.Qc1%20Nc6%207.c3%20Be7%208.Nbd2%20d5%209.h3%20Nh5%2010.Bh2%20O-O%2011.Be2%20Bd7%2012.O-O%20f5%2013.b4%20Nf6%2014.a4%20Rac8%2015.Qb2%20Ne4%2016.a5%20Qd8%2017.Nxe4%20fxe4%2018.Ne5%20Nxe5%2019.Bxe5%20Bf6%2020.Bd6%20Rf7%2021.b5%20Be7%2022.Be5%20Bf6#28) | [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nf6%202.d4%20e6%203.Bf4%20c5%204.e3%20cxd4%205.exd4%20Qb6%206.Qc1%20Nc6%207.c3%20Be7%208.Nbd2%20d5%209.h3%20Nh5%2010.Bh2%20O-O%2011.Be2%20Bd7%2012.O-O%20f5%2013.b4%20Nf6%2014.a4%20Rac8%2015.a5%20Qd8%2016.Qb2%20Ne4%2017.Nb3%20Bd6%2018.Bxd6%20Nxd6%2019.Nc5%20Ne4%2020.Nxb7%20Qc7%2021.Nc5%20Nxc5%2022.bxc5%20Rb8#28) |

position 30 (`1rbq1rk1/5ppp/2np3b/p2Np3/1p2P2P/2PQ2P1/PPN2PB1/R4RK1 b - - 1 17`), split at ply 11: Qa7 (54% there) vs Bxd5 (46%)

| chosen | subpar |
|---|---|
| 17...bxc3 18.bxc3 Be6 19.Nce3 Ne7 20.Nxe7+ Qxe7 21.Rfd1 Rfd8 22.Nd5 [Qa7] 23.Rab1 Kf8 24.Rb5 Rxb5 [25.Qxb5] | 17...bxc3 18.bxc3 Be6 19.Nce3 Ne7 20.Nxe7+ Qxe7 21.Rfd1 Rfd8 22.Nd5 Bxd5 [23.Qxd5] [Qc7] 24.Bf1 [Qxc3] 25.Bc4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20e5%206.Ndb5%20d6%207.Bg5%20a6%208.Na3%20b5%209.Nd5%20Be7%2010.Bxf6%20Bxf6%2011.c3%20Bg5%2012.h4%20Bh6%2013.g3%20O-O%2014.Bg2%20Rb8%2015.Nc2%20a5%2016.O-O%20b4%2017.Qd3%20bxc3%2018.bxc3%20Be6%2019.Nce3%20Ne7%2020.Nxe7%2B%20Qxe7%2021.Rfd1%20Rfd8%2022.Nd5%20Qa7%2023.Rab1%20Kf8%2024.Rb5%20Rxb5%2025.Qxb5#33) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20e5%206.Ndb5%20d6%207.Bg5%20a6%208.Na3%20b5%209.Nd5%20Be7%2010.Bxf6%20Bxf6%2011.c3%20Bg5%2012.h4%20Bh6%2013.g3%20O-O%2014.Bg2%20Rb8%2015.Nc2%20a5%2016.O-O%20b4%2017.Qd3%20bxc3%2018.bxc3%20Be6%2019.Nce3%20Ne7%2020.Nxe7%2B%20Qxe7%2021.Rfd1%20Rfd8%2022.Nd5%20Bxd5%2023.Qxd5%20Qc7%2024.Bf1%20Qxc3%2025.Bc4#33) |

position 13 (`r2qkb1r/ppp3pp/5n2/3p4/8/2P1BB2/PP3P1P/RN1QK2R b KQkq - 2 11`), split at ply 15: Qe7 (56% there) vs d4 (44%)

| chosen | subpar |
|---|---|
| 11...Bd6 12.Nd2 O-O [13.Qb3] c6 14.O-O-O a5 15.c4 a4 [16.Qc2] a3 17.b3 Be5 18.Rhg1 [Qe7] 19.Kb1 | 11...Bd6 12.Nd2 O-O [13.Qb3] c6 14.O-O-O a5 15.c4 a4 [16.Qc2] a3 17.b3 Be5 18.Rhg1 d4 19.Bh6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.d4%20Bxf5%205.Bd3%20Bg4%206.c3%20e5%207.dxe5%20Nxe5%208.Be2%20Nxf3%2B%209.gxf3%20Bxf3%2010.Bxf3%20Nf6%2011.Be3%20Bd6%2012.Nd2%20O-O%2013.Qb3%20c6%2014.O-O-O%20a5%2015.c4%20a4%2016.Qc2%20a3%2017.b3%20Be5%2018.Rhg1%20Qe7%2019.Kb1#21) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.d4%20Bxf5%205.Bd3%20Bg4%206.c3%20e5%207.dxe5%20Nxe5%208.Be2%20Nxf3%2B%209.gxf3%20Bxf3%2010.Bxf3%20Nf6%2011.Be3%20Bd6%2012.Nd2%20O-O%2013.Qb3%20c6%2014.O-O-O%20a5%2015.c4%20a4%2016.Qc2%20a3%2017.b3%20Be5%2018.Rhg1%20d4%2019.Bh6#21) |

#### S #4 (k = 0): latents 1006

position 3 (`2kr1b1r/ppp1pppp/5n2/8/3n1q2/1P1P1B1P/P1P2PP1/RNBQ1K1R b - - 0 11`), split at ply 5: Nxe4 (53% there) vs Nxf3 (47%)

| chosen | subpar |
|---|---|
| [11...Qf5] [12.Nc3] [e5] [13.Ne4] [Nxe4] [14.Bxe4] [Qf6] [15.c3] [Ne6] 16.Qf3 Qxf3 17.Bxf3 Rxd3 18.Be3 Rxc3 19.Ke2 | [11...Qf5] [12.Nc3] [e5] [13.Ne4] Nxf3 14.Qxf3 [Qxf3] 15.gxf3 Nd5 16.Bd2 f5 17.Nc3 Nb4 18.Rc1 [a6] [19.a3] |
| [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nc6%202.e4%20d5%203.exd5%20Qxd5%204.b3%20Bg4%205.Bc4%20Qe4%2B%206.Kf1%20Nd4%207.Bd3%20Qf4%208.Be2%20O-O-O%209.h3%20Bxf3%2010.Bxf3%20Nf6%2011.d3%20Qf5%2012.Nc3%20e5%2013.Ne4%20Nxe4%2014.Bxe4%20Qf6%2015.c3%20Ne6%2016.Qf3%20Qxf3%2017.Bxf3%20Rxd3%2018.Be3%20Rxc3%2019.Ke2#21) | [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nc6%202.e4%20d5%203.exd5%20Qxd5%204.b3%20Bg4%205.Bc4%20Qe4%2B%206.Kf1%20Nd4%207.Bd3%20Qf4%208.Be2%20O-O-O%209.h3%20Bxf3%2010.Bxf3%20Nf6%2011.d3%20Qf5%2012.Nc3%20e5%2013.Ne4%20Nxf3%2014.Qxf3%20Qxf3%2015.gxf3%20Nd5%2016.Bd2%20f5%2017.Nc3%20Nb4%2018.Rc1%20a6%2019.a3#21) |

position 33 (`r2qk1r1/3bbpnp/p3N1p1/2ppB1P1/1p2P2P/1P3Q2/P1P2P2/2KR1B1R b q - 0 19`), split at ply 12: Qe4+ (53% there) vs Qxd8+ (47%)

| chosen | subpar |
|---|---|
| 19...Bxe6 20.exd5 Bd7 [21.d6] [Bxg5+] 22.hxg5 [Qxg5+] 23.Bf4 Qf6 24.Qxa8+ Qd8 [25.Qe4+] Ne6 26.Rxh7 Qa5 27.Bc4 | 19...Bxe6 20.exd5 Bd7 [21.d6] [Bxg5+] 22.hxg5 [Qxg5+] 23.Bf4 Qf6 24.Qxa8+ Qd8 25.Qxd8+ Kxd8 26.Rxh7 Ne6 27.Be3 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.Bf4%20a6%204.e3%20e6%205.g4%20Bb4%206.Ne2%20Be7%207.g5%20Nh5%208.h4%20b5%209.Bh2%20Nc6%2010.Nc1%20g6%2011.Nb3%20Ng7%2012.Qf3%20b4%2013.Na4%20Bd7%2014.O-O-O%20Nxd4%2015.Nxd4%20Bxa4%2016.Be5%20Rg8%2017.e4%20c5%2018.b3%20Bd7%2019.Nxe6%20Bxe6%2020.exd5%20Bd7%2021.d6%20Bxg5%2B%2022.hxg5%20Qxg5%2B%2023.Bf4%20Qf6%2024.Qxa8%2B%20Qd8%2025.Qe4%2B%20Ne6%2026.Rxh7%20Qa5%2027.Bc4#37) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.Bf4%20a6%204.e3%20e6%205.g4%20Bb4%206.Ne2%20Be7%207.g5%20Nh5%208.h4%20b5%209.Bh2%20Nc6%2010.Nc1%20g6%2011.Nb3%20Ng7%2012.Qf3%20b4%2013.Na4%20Bd7%2014.O-O-O%20Nxd4%2015.Nxd4%20Bxa4%2016.Be5%20Rg8%2017.e4%20c5%2018.b3%20Bd7%2019.Nxe6%20Bxe6%2020.exd5%20Bd7%2021.d6%20Bxg5%2B%2022.hxg5%20Qxg5%2B%2023.Bf4%20Qf6%2024.Qxa8%2B%20Qd8%2025.Qxd8%2B%20Kxd8%2026.Rxh7%20Ne6%2027.Be3#37) |

position 0 (`2kr2r1/ppp5/2n1RbNp/2q2p1P/3p4/2PQ1P1B/PPKN3P/6R1 b - - 0 20`), split at ply 7: Rxd2+ (56% there) vs Qxb4 (44%)

| chosen | subpar |
|---|---|
| 20...dxc3 21.bxc3 [Nb4+] 22.Kd1 Rxd3 23.cxb4 [Rxd2+] 24.Kxd2 Qxb4+ 25.Ke2 Qb2+ 26.Kf1 Qxh2 27.Bxf5 Kb8 [28.Rg2] | 20...dxc3 21.bxc3 [Nb4+] 22.Kd1 Rxd3 23.cxb4 Qxb4 24.Re2 [Rgd8] [25.Bxf5+] [Kb8] 26.Bxd3 [Qa4+] 27.Bc2 Qxa2 [28.Rge1] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.bxc3%20Nb4%2B%2022.Kd1%20Rxd3%2023.cxb4%20Rxd2%2B%2024.Kxd2%20Qxb4%2B%2025.Ke2%20Qb2%2B%2026.Kf1%20Qxh2%2027.Bxf5%20Kb8%2028.Rg2#39) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.bxc3%20Nb4%2B%2022.Kd1%20Rxd3%2023.cxb4%20Qxb4%2024.Re2%20Rgd8%2025.Bxf5%2B%20Kb8%2026.Bxd3%20Qa4%2B%2027.Bc2%20Qxa2%2028.Rge1#39) |

#### S #5 (k = 0): latents 746

position 18 (`r1bq1rk1/pp3ppp/3b1n2/4N3/2BppP2/4B3/PPP3PP/R2Q1RK1 w - - 0 12`), split at ply 10: Qxc5 (54% there) vs Rxd1 (46%)

| chosen | subpar |
|---|---|
| 12.Bxd4 [Qc7] 13.Bb3 Bc5 14.c3 Be6 15.Kh1 Rad8 16.Bxc5 [Qxc5] [17.Qe2] Bxb3 18.axb3 a6 19.Rad1 h5 | 12.Bxd4 [Qc7] 13.Bb3 Bc5 14.c3 Be6 15.Kh1 Rad8 16.Bxc5 Rxd1 17.Bxf8 Rxa1 18.Rxa1 Kxf8 19.Bxe6 fxe6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nf6%203.Nxe5%20Nxe4%204.d4%20d5%205.Bd3%20Nd7%206.O-O%20Bd6%207.f4%20O-O%208.Nc3%20Ndf6%209.Nxe4%20dxe4%2010.Bc4%20c5%2011.Be3%20cxd4%2012.Bxd4%20Qc7%2013.Bb3%20Bc5%2014.c3%20Be6%2015.Kh1%20Rad8%2016.Bxc5%20Qxc5%2017.Qe2%20Bxb3%2018.axb3%20a6%2019.Rad1%20h5#22) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nf6%203.Nxe5%20Nxe4%204.d4%20d5%205.Bd3%20Nd7%206.O-O%20Bd6%207.f4%20O-O%208.Nc3%20Ndf6%209.Nxe4%20dxe4%2010.Bc4%20c5%2011.Be3%20cxd4%2012.Bxd4%20Qc7%2013.Bb3%20Bc5%2014.c3%20Be6%2015.Kh1%20Rad8%2016.Bxc5%20Rxd1%2017.Bxf8%20Rxa1%2018.Rxa1%20Kxf8%2019.Bxe6%20fxe6#22) |

position 28 (`3r1k2/r4p1p/p1p1pqp1/2Pn4/2N5/6QP/1P3PP1/R2R2K1 w - - 16 27`), split at ply 11: Qh4 (54% there) vs Qf3+ (46%)

| chosen | subpar |
|---|---|
| 27.Ra3 Kg7 28.Rf3 [Qe7] 29.Ne5 [Qxc5] 30.Rxf7+ Rxf7 31.Nxf7 Kxf7 [32.Qh4] Rd7 33.Qxh7+ Kf6 34.Qh4+ Kg7 | 27.Ra3 Kg7 28.Rf3 [Qe7] 29.Ne5 [Qxc5] 30.Rxf7+ Rxf7 31.Nxf7 Kxf7 32.Qf3+ Kg7 33.Re1 Rf8 [34.Qg3] Rf6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20g6%202.d4%20Bg7%203.c3%20d5%204.e5%20c5%205.Nf3%20Nc6%206.Bb5%20Qb6%207.a4%20a6%208.Bxc6%2B%20bxc6%209.a5%20Qb5%2010.Na3%20Qxa5%2011.O-O%20Qc7%2012.Bf4%20Bg4%2013.h3%20Bxf3%2014.Qxf3%20e6%2015.c4%20Ne7%2016.dxc5%20Bxe5%2017.Bxe5%20Qxe5%2018.cxd5%20Qxd5%2019.Qf6%20Rf8%2020.Rfd1%20Qf5%2021.Qd4%20Nd5%2022.Nc4%20Ke7%2023.Nb6%20Ra7%2024.Qh4%2B%20Qf6%2025.Qg3%20Rd8%2026.Nc4%20Kf8%2027.Ra3%20Kg7%2028.Rf3%20Qe7%2029.Ne5%20Qxc5%2030.Rxf7%2B%20Rxf7%2031.Nxf7%20Kxf7%2032.Qh4%20Rd7%2033.Qxh7%2B%20Kf6%2034.Qh4%2B%20Kg7#52) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20g6%202.d4%20Bg7%203.c3%20d5%204.e5%20c5%205.Nf3%20Nc6%206.Bb5%20Qb6%207.a4%20a6%208.Bxc6%2B%20bxc6%209.a5%20Qb5%2010.Na3%20Qxa5%2011.O-O%20Qc7%2012.Bf4%20Bg4%2013.h3%20Bxf3%2014.Qxf3%20e6%2015.c4%20Ne7%2016.dxc5%20Bxe5%2017.Bxe5%20Qxe5%2018.cxd5%20Qxd5%2019.Qf6%20Rf8%2020.Rfd1%20Qf5%2021.Qd4%20Nd5%2022.Nc4%20Ke7%2023.Nb6%20Ra7%2024.Qh4%2B%20Qf6%2025.Qg3%20Rd8%2026.Nc4%20Kf8%2027.Ra3%20Kg7%2028.Rf3%20Qe7%2029.Ne5%20Qxc5%2030.Rxf7%2B%20Rxf7%2031.Nxf7%20Kxf7%2032.Qf3%2B%20Kg7%2033.Re1%20Rf8%2034.Qg3%20Rf6#52) |

position 33 (`r2qk1r1/3bbpnp/p3N1p1/2ppB1P1/1p2P2P/1P3Q2/P1P2P2/2KR1B1R b q - 0 19`), split at ply 13: Qe8 (54% there) vs Bxc8 (46%)

| chosen | subpar |
|---|---|
| 19...Bxe6 20.exd5 Bf5 21.d6 Ra7 22.dxe7 [Qxe7] 23.Bxg7 Rxg7 24.Qc6+ Kf8 25.Qc8+ [Qe8] 26.Qxc5+ Kg8 [27.Qxa7] | 19...Bxe6 20.exd5 Bf5 21.d6 Ra7 22.dxe7 [Qxe7] 23.Bxg7 Rxg7 24.Qc6+ Kf8 25.Qc8+ Bxc8 26.Rd8+ [Qxd8] 27.Bd3 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.Bf4%20a6%204.e3%20e6%205.g4%20Bb4%206.Ne2%20Be7%207.g5%20Nh5%208.h4%20b5%209.Bh2%20Nc6%2010.Nc1%20g6%2011.Nb3%20Ng7%2012.Qf3%20b4%2013.Na4%20Bd7%2014.O-O-O%20Nxd4%2015.Nxd4%20Bxa4%2016.Be5%20Rg8%2017.e4%20c5%2018.b3%20Bd7%2019.Nxe6%20Bxe6%2020.exd5%20Bf5%2021.d6%20Ra7%2022.dxe7%20Qxe7%2023.Bxg7%20Rxg7%2024.Qc6%2B%20Kf8%2025.Qc8%2B%20Qe8%2026.Qxc5%2B%20Kg8%2027.Qxa7#37) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Nc3%20d5%203.Bf4%20a6%204.e3%20e6%205.g4%20Bb4%206.Ne2%20Be7%207.g5%20Nh5%208.h4%20b5%209.Bh2%20Nc6%2010.Nc1%20g6%2011.Nb3%20Ng7%2012.Qf3%20b4%2013.Na4%20Bd7%2014.O-O-O%20Nxd4%2015.Nxd4%20Bxa4%2016.Be5%20Rg8%2017.e4%20c5%2018.b3%20Bd7%2019.Nxe6%20Bxe6%2020.exd5%20Bf5%2021.d6%20Ra7%2022.dxe7%20Qxe7%2023.Bxg7%20Rxg7%2024.Qc6%2B%20Kf8%2025.Qc8%2B%20Bxc8%2026.Rd8%2B%20Qxd8%2027.Bd3#37) |

#### S #6 (k = 0): latents 894

position 3 (`2kr1b1r/ppp1pppp/5n2/8/3n1q2/1P1P1B1P/P1P2PP1/RNBQ1K1R b - - 0 11`), split at ply 5: Qf5 (54% there) vs Qc5 (46%)

| chosen | subpar |
|---|---|
| [11...Qe5] 12.Na3 e6 13.Nc4 [Qf5] 14.Bb2 Bc5 15.Ne3 Qg6 16.a3 h5 17.b4 Bb6 18.a4 a5 19.bxa5 | [11...Qe5] 12.Na3 e6 13.Nc4 Qc5 14.Be3 [Nxf3] 15.Qxf3 Qd5 16.Ke2 Qxf3+ 17.Kxf3 [Nd5] 18.a4 [f6] 19.a5 |
| [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nc6%202.e4%20d5%203.exd5%20Qxd5%204.b3%20Bg4%205.Bc4%20Qe4%2B%206.Kf1%20Nd4%207.Bd3%20Qf4%208.Be2%20O-O-O%209.h3%20Bxf3%2010.Bxf3%20Nf6%2011.d3%20Qe5%2012.Na3%20e6%2013.Nc4%20Qf5%2014.Bb2%20Bc5%2015.Ne3%20Qg6%2016.a3%20h5%2017.b4%20Bb6%2018.a4%20a5%2019.bxa5#21) | [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nc6%202.e4%20d5%203.exd5%20Qxd5%204.b3%20Bg4%205.Bc4%20Qe4%2B%206.Kf1%20Nd4%207.Bd3%20Qf4%208.Be2%20O-O-O%209.h3%20Bxf3%2010.Bxf3%20Nf6%2011.d3%20Qe5%2012.Na3%20e6%2013.Nc4%20Qc5%2014.Be3%20Nxf3%2015.Qxf3%20Qd5%2016.Ke2%20Qxf3%2B%2017.Kxf3%20Nd5%2018.a4%20f6%2019.a5#21) |

position 18 (`r1bq1rk1/pp3ppp/3b1n2/4N3/2BppP2/4B3/PPP3PP/R2Q1RK1 w - - 0 12`), split at ply 10: Qxc5 (54% there) vs Rxd1 (46%)

| chosen | subpar |
|---|---|
| [12.Bxd4] Qc7 [13.Bb3] Bc5 [14.c3] Be6 15.Kh1 [Rad8] 16.Bxc5 [Qxc5] 17.Qe2 [Bxb3] 18.axb3 [a6] 19.Rad1 [h5] | [12.Bxd4] Qc7 [13.Bb3] Bc5 [14.c3] Be6 15.Kh1 [Rad8] 16.Bxc5 Rxd1 17.Bxf8 Rxa1 18.Rxa1 Kxf8 19.Bxe6 fxe6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nf6%203.Nxe5%20Nxe4%204.d4%20d5%205.Bd3%20Nd7%206.O-O%20Bd6%207.f4%20O-O%208.Nc3%20Ndf6%209.Nxe4%20dxe4%2010.Bc4%20c5%2011.Be3%20cxd4%2012.Bxd4%20Qc7%2013.Bb3%20Bc5%2014.c3%20Be6%2015.Kh1%20Rad8%2016.Bxc5%20Qxc5%2017.Qe2%20Bxb3%2018.axb3%20a6%2019.Rad1%20h5#22) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nf6%203.Nxe5%20Nxe4%204.d4%20d5%205.Bd3%20Nd7%206.O-O%20Bd6%207.f4%20O-O%208.Nc3%20Ndf6%209.Nxe4%20dxe4%2010.Bc4%20c5%2011.Be3%20cxd4%2012.Bxd4%20Qc7%2013.Bb3%20Bc5%2014.c3%20Be6%2015.Kh1%20Rad8%2016.Bxc5%20Rxd1%2017.Bxf8%20Rxa1%2018.Rxa1%20Kxf8%2019.Bxe6%20fxe6#22) |

position 28 (`3r1k2/r4p1p/p1p1pqp1/2Pn4/2N5/6QP/1P3PP1/R2R2K1 w - - 16 27`), split at ply 11: Qh4 (54% there) vs Qf3+ (46%)

| chosen | subpar |
|---|---|
| 27.Ra3 Kg7 28.Rf3 Qe7 [29.Ne5] [Qxc5] 30.Rxf7+ Rxf7 31.Nxf7 [Kxf7] [32.Qh4] [Rd7] 33.Qxh7+ [Kf6] 34.Qh4+ [Kg7] | 27.Ra3 Kg7 28.Rf3 Qe7 [29.Ne5] [Qxc5] 30.Rxf7+ Rxf7 31.Nxf7 [Kxf7] 32.Qf3+ Kg7 33.Re1 Rf8 34.Qg3 Rf6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20g6%202.d4%20Bg7%203.c3%20d5%204.e5%20c5%205.Nf3%20Nc6%206.Bb5%20Qb6%207.a4%20a6%208.Bxc6%2B%20bxc6%209.a5%20Qb5%2010.Na3%20Qxa5%2011.O-O%20Qc7%2012.Bf4%20Bg4%2013.h3%20Bxf3%2014.Qxf3%20e6%2015.c4%20Ne7%2016.dxc5%20Bxe5%2017.Bxe5%20Qxe5%2018.cxd5%20Qxd5%2019.Qf6%20Rf8%2020.Rfd1%20Qf5%2021.Qd4%20Nd5%2022.Nc4%20Ke7%2023.Nb6%20Ra7%2024.Qh4%2B%20Qf6%2025.Qg3%20Rd8%2026.Nc4%20Kf8%2027.Ra3%20Kg7%2028.Rf3%20Qe7%2029.Ne5%20Qxc5%2030.Rxf7%2B%20Rxf7%2031.Nxf7%20Kxf7%2032.Qh4%20Rd7%2033.Qxh7%2B%20Kf6%2034.Qh4%2B%20Kg7#52) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20g6%202.d4%20Bg7%203.c3%20d5%204.e5%20c5%205.Nf3%20Nc6%206.Bb5%20Qb6%207.a4%20a6%208.Bxc6%2B%20bxc6%209.a5%20Qb5%2010.Na3%20Qxa5%2011.O-O%20Qc7%2012.Bf4%20Bg4%2013.h3%20Bxf3%2014.Qxf3%20e6%2015.c4%20Ne7%2016.dxc5%20Bxe5%2017.Bxe5%20Qxe5%2018.cxd5%20Qxd5%2019.Qf6%20Rf8%2020.Rfd1%20Qf5%2021.Qd4%20Nd5%2022.Nc4%20Ke7%2023.Nb6%20Ra7%2024.Qh4%2B%20Qf6%2025.Qg3%20Rd8%2026.Nc4%20Kf8%2027.Ra3%20Kg7%2028.Rf3%20Qe7%2029.Ne5%20Qxc5%2030.Rxf7%2B%20Rxf7%2031.Nxf7%20Kxf7%2032.Qf3%2B%20Kg7%2033.Re1%20Rf8%2034.Qg3%20Rf6#52) |

#### S #7 (k = 0): latents 140

position 11 (`r3k2r/p3bp2/qn2p3/1R2Pp1p/3P3P/3Q1N2/3B1PP1/1R4K1 w kq - 3 21`), split at ply 7: Rc5 (52% there) vs Qa3 (48%)

| chosen | subpar |
|---|---|
| 21.Bg5 Bxg5 22.Nxg5 Rd8 23.Qf3 Qc8 [24.Rc5] Qd7 25.Rbc1 Nd5 [26.Rc6] Kf8 27.Qa3+ Kg7 28.Qg3 Kh6 | 21.Bg5 Bxg5 22.Nxg5 Rd8 23.Qf3 Qc8 24.Qa3 Nd5 [25.Rb7] Rd7 26.Rb8 Nb6 27.Rxc8+ Nxc8 [28.Rb8] Rd8 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.e5%20Bf5%204.h4%20h5%205.Bd3%20Bxd3%206.Qxd3%20Qa5%2B%207.b4%20Qxb4%2B%208.Nd2%20Qb5%209.c4%20dxc4%2010.Nxc4%20e6%2011.Bd2%20Qa6%2012.Nf3%20Nh6%2013.O-O%20Nf5%2014.Rab1%20b5%2015.Ne3%20g6%2016.a4%20Be7%2017.Nxf5%20gxf5%2018.axb5%20cxb5%2019.Rxb5%20Nd7%2020.Rfb1%20Nb6%2021.Bg5%20Bxg5%2022.Nxg5%20Rd8%2023.Qf3%20Qc8%2024.Rc5%20Qd7%2025.Rbc1%20Nd5%2026.Rc6%20Kf8%2027.Qa3%2B%20Kg7%2028.Qg3%20Kh6#40) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.e5%20Bf5%204.h4%20h5%205.Bd3%20Bxd3%206.Qxd3%20Qa5%2B%207.b4%20Qxb4%2B%208.Nd2%20Qb5%209.c4%20dxc4%2010.Nxc4%20e6%2011.Bd2%20Qa6%2012.Nf3%20Nh6%2013.O-O%20Nf5%2014.Rab1%20b5%2015.Ne3%20g6%2016.a4%20Be7%2017.Nxf5%20gxf5%2018.axb5%20cxb5%2019.Rxb5%20Nd7%2020.Rfb1%20Nb6%2021.Bg5%20Bxg5%2022.Nxg5%20Rd8%2023.Qf3%20Qc8%2024.Qa3%20Nd5%2025.Rb7%20Rd7%2026.Rb8%20Nb6%2027.Rxc8%2B%20Nxc8%2028.Rb8%20Rd8#40) |

position 26 (`r1b1r1k1/2p3bp/2p2pq1/2Np4/p5P1/P1Q1B3/1PP2P1P/1K1R2R1 w - - 3 24`), split at ply 13: Rxg5 (53% there) vs Bxg7 (47%)

| chosen | subpar |
|---|---|
| 24.h4 Rb8 25.h5 Qf7 26.Bd4 h6 27.f4 [Rb5] 28.g5 hxg5 29.fxg5 fxg5 [30.Rxg5] [Rxc5] [31.Rxg7+] Qxg7 | 24.h4 Rb8 25.h5 Qf7 26.Bd4 h6 27.f4 [Rb5] 28.g5 hxg5 29.fxg5 fxg5 30.Bxg7 Qxg7 31.Qxg7+ Kxg7 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.h4%20Rb8%2025.h5%20Qf7%2026.Bd4%20h6%2027.f4%20Rb5%2028.g5%20hxg5%2029.fxg5%20fxg5%2030.Rxg5%20Rxc5%2031.Rxg7%2B%20Qxg7#46) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.h4%20Rb8%2025.h5%20Qf7%2026.Bd4%20h6%2027.f4%20Rb5%2028.g5%20hxg5%2029.fxg5%20fxg5%2030.Bxg7%20Qxg7%2031.Qxg7%2B%20Kxg7#46) |

position 35 (`3rr1k1/ppp2pp1/5b1p/8/2qP4/7P/PP3PKP/R2Q2R1 w - - 4 21`), split at ply 12: Rxh3 (50% there) vs Red8 (47%)

| chosen | subpar |
|---|---|
| 21.Rc1 Qd5+ 22.Kf1 c6 23.Qg4 Qxd4 24.Qg3 Qd3+ 25.Qxd3 [Rxd3] 26.Rc2 [Rxh3] 27.Kg2 Rh5 28.Rd1 Rg5+ | 21.Rc1 Qd5+ 22.Kf1 c6 23.Qg4 Qxd4 24.Qg3 Qd3+ 25.Qxd3 [Rxd3] 26.Rc2 Red8 27.Kg2 Rd2 28.Rgc1 Rxc2 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nc3%20Nf6%203.d4%20exd4%204.Qxd4%20Nc6%205.Qd1%20d6%206.Bb5%20Be7%207.Bg5%20h6%208.Bxf6%20Bxf6%209.Qf3%20O-O%2010.Nh3%20Nd4%2011.Qd1%20Bxh3%2012.gxh3%20d5%2013.exd5%20Qd6%2014.Be2%20Rfe8%2015.Ne4%20Rxe4%2016.c3%20Rxe2%2B%2017.Kf1%20Ree8%2018.cxd4%20Qxd5%2019.Rg1%20Qc4%2B%2020.Kg2%20Rad8%2021.Rc1%20Qd5%2B%2022.Kf1%20c6%2023.Qg4%20Qxd4%2024.Qg3%20Qd3%2B%2025.Qxd3%20Rxd3%2026.Rc2%20Rxh3%2027.Kg2%20Rh5%2028.Rd1%20Rg5%2B#40) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nc3%20Nf6%203.d4%20exd4%204.Qxd4%20Nc6%205.Qd1%20d6%206.Bb5%20Be7%207.Bg5%20h6%208.Bxf6%20Bxf6%209.Qf3%20O-O%2010.Nh3%20Nd4%2011.Qd1%20Bxh3%2012.gxh3%20d5%2013.exd5%20Qd6%2014.Be2%20Rfe8%2015.Ne4%20Rxe4%2016.c3%20Rxe2%2B%2017.Kf1%20Ree8%2018.cxd4%20Qxd5%2019.Rg1%20Qc4%2B%2020.Kg2%20Rad8%2021.Rc1%20Qd5%2B%2022.Kf1%20c6%2023.Qg4%20Qxd4%2024.Qg3%20Qd3%2B%2025.Qxd3%20Rxd3%2026.Rc2%20Red8%2027.Kg2%20Rd2%2028.Rgc1%20Rxc2#40) |

#### S #8 (k = 0): latents 894

position 47 (`r2qr1k1/pp3ppp/1bn5/3p4/3Nb2n/1NP2PBP/PP2B1PK/R2Q1R2 b - - 0 16`), split at ply 4: Bf2 (49% there) vs Nxf5 (48%)

| chosen | subpar |
|---|---|
| [16...Bg6] [17.Qd2] [Nf5] [18.Bf2] Qd6+ [19.Kg1] [Ng3] [20.Rfe1] [Nxe2+] [21.Rxe2] Rxe2 22.Qxe2 [Nxd4] 23.Nxd4 [Bxd4] 24.Bxd4 | [16...Bg6] [17.Qd2] [Nf5] 18.Nxf5 [Bxf5] 19.Rfe1 [d4] 20.cxd4 [Nxd4] 21.Nxd4 Qxd4 22.Qxd4 Bxd4 23.Bb5 Rxe1 24.Rxe1 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bg6%2017.Qd2%20Nf5%2018.Bf2%20Qd6%2B%2019.Kg1%20Ng3%2020.Rfe1%20Nxe2%2B%2021.Rxe2%20Rxe2%2022.Qxe2%20Nxd4%2023.Nxd4%20Bxd4%2024.Bxd4#31) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bg6%2017.Qd2%20Nf5%2018.Nxf5%20Bxf5%2019.Rfe1%20d4%2020.cxd4%20Nxd4%2021.Nxd4%20Qxd4%2022.Qxd4%20Bxd4%2023.Bb5%20Rxe1%2024.Rxe1#31) |

position 36 (`3r1rk1/1pq1npp1/p1p1P2p/8/4Q3/5N2/PP3PPP/3R1RK1 b - - 0 20`), split at ply 5: Qe6 (52% there) vs Qf5 (45%)

| chosen | subpar |
|---|---|
| 20...Nd5 [21.exf7+] [Qxf7] [22.Ne5] [Qe6] [23.Rfe1] Rde8 [24.Nd3] Qxe4 [25.Rxe4] Rxe4 [26.Nc5] Re2 [27.Nd3] Rfe8 28.Kf1 | 20...Nd5 [21.exf7+] [Qxf7] [22.Ne5] Qf5 [23.Qxf5] Rxf5 [24.Nc4] [Re8] [25.Rfe1] Rxe1+ 26.Rxe1 Rf7 27.g3 Re7 28.Rxe7 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.Bb5%20e5%204.O-O%20Bd6%205.c3%20a6%206.Bxc6%20dxc6%207.d4%20cxd4%208.cxd4%20exd4%209.Qxd4%20Bf8%2010.Qc3%20Nf6%2011.Bg5%20Be7%2012.Nbd2%20O-O%2013.Rad1%20Qc7%2014.e5%20Nd5%2015.Qc2%20h6%2016.Bxe7%20Nxe7%2017.Ne4%20Bf5%2018.Qe2%20Bxe4%2019.Qxe4%20Rad8%2020.e6%20Nd5%2021.exf7%2B%20Qxf7%2022.Ne5%20Qe6%2023.Rfe1%20Rde8%2024.Nd3%20Qxe4%2025.Rxe4%20Rxe4%2026.Nc5%20Re2%2027.Nd3%20Rfe8%2028.Kf1#39) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.Bb5%20e5%204.O-O%20Bd6%205.c3%20a6%206.Bxc6%20dxc6%207.d4%20cxd4%208.cxd4%20exd4%209.Qxd4%20Bf8%2010.Qc3%20Nf6%2011.Bg5%20Be7%2012.Nbd2%20O-O%2013.Rad1%20Qc7%2014.e5%20Nd5%2015.Qc2%20h6%2016.Bxe7%20Nxe7%2017.Ne4%20Bf5%2018.Qe2%20Bxe4%2019.Qxe4%20Rad8%2020.e6%20Nd5%2021.exf7%2B%20Qxf7%2022.Ne5%20Qf5%2023.Qxf5%20Rxf5%2024.Nc4%20Re8%2025.Rfe1%20Rxe1%2B%2026.Rxe1%20Rf7%2027.g3%20Re7%2028.Rxe7#39) |

position 2 (`r1bqk2r/p2pbp2/2p1p3/3nP1pp/4N3/P7/1PP2PPP/R1BQKB1R b KQkq - 1 11`), split at ply 14: Bb5+ (56% there) vs Re1 (44%)

| chosen | subpar |
|---|---|
| 11...Qc7 [12.c4] Qxe5 13.Bd3 Nf4 14.Bxf4 gxf4 15.O-O d5 16.cxd5 [cxd5] 17.Nc3 [Bb7] [18.Bb5+] Kf8 19.Re1 | 11...Qc7 [12.c4] Qxe5 13.Bd3 Nf4 14.Bxf4 gxf4 15.O-O d5 16.cxd5 [cxd5] 17.Nc3 [Bb7] 18.Re1 [Qg5] [19.Bb5+] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.a3%20Be7%207.Nxc6%20bxc6%208.e5%20Nd5%209.Qg4%20g5%2010.Ne4%20h5%2011.Qd1%20Qc7%2012.c4%20Qxe5%2013.Bd3%20Nf4%2014.Bxf4%20gxf4%2015.O-O%20d5%2016.cxd5%20cxd5%2017.Nc3%20Bb7%2018.Bb5%2B%20Kf8%2019.Re1#21) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.a3%20Be7%207.Nxc6%20bxc6%208.e5%20Nd5%209.Qg4%20g5%2010.Ne4%20h5%2011.Qd1%20Qc7%2012.c4%20Qxe5%2013.Bd3%20Nf4%2014.Bxf4%20gxf4%2015.O-O%20d5%2016.cxd5%20cxd5%2017.Nc3%20Bb7%2018.Re1%20Qg5%2019.Bb5%2B#21) |

#### S #9 (k = 0): latents 499

position 20 (`r3k1nr/1p1n4/1p1bp1pp/3p1p2/3P4/2P2N2/PP1N1PPP/R1B2RK1 b kq - 1 14`), split at ply 11: Rhc8 (51% there) vs Bxe3 (49%)

| chosen | subpar |
|---|---|
| 14...g5 15.Re1 Kf7 16.Ne5+ Nxe5 17.dxe5 [Bc5] 18.Nb3 [Ne7] 19.Be3 [Rhc8] 20.a3 Bxe3 21.Rxe3 f4 [22.Re2] | 14...g5 15.Re1 Kf7 16.Ne5+ Nxe5 17.dxe5 [Bc5] 18.Nb3 [Ne7] 19.Be3 Bxe3 20.Rxe3 Nc6 21.a3 f4 [22.Re2] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20e6%202.Bf4%20c5%203.e3%20cxd4%204.exd4%20Qb6%205.Bc1%20d5%206.Nf3%20Bb4%2B%207.c3%20Bd6%208.Bd3%20g6%209.Nbd2%20f5%2010.Qb3%20h6%2011.Qxb6%20axb6%2012.Bb5%2B%20Bd7%2013.Bxd7%2B%20Nxd7%2014.O-O%20g5%2015.Re1%20Kf7%2016.Ne5%2B%20Nxe5%2017.dxe5%20Bc5%2018.Nb3%20Ne7%2019.Be3%20Rhc8%2020.a3%20Bxe3%2021.Rxe3%20f4%2022.Re2#27) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20e6%202.Bf4%20c5%203.e3%20cxd4%204.exd4%20Qb6%205.Bc1%20d5%206.Nf3%20Bb4%2B%207.c3%20Bd6%208.Bd3%20g6%209.Nbd2%20f5%2010.Qb3%20h6%2011.Qxb6%20axb6%2012.Bb5%2B%20Bd7%2013.Bxd7%2B%20Nxd7%2014.O-O%20g5%2015.Re1%20Kf7%2016.Ne5%2B%20Nxe5%2017.dxe5%20Bc5%2018.Nb3%20Ne7%2019.Be3%20Bxe3%2020.Rxe3%20Nc6%2021.a3%20f4%2022.Re2#27) |

position 19 (`r4r1k/ppq1b1pp/2npQ3/4p3/1PP5/P1P2N2/5PPP/R1B2RK1 w - - 1 18`), split at ply 7: Ne4 (54% there) vs Rad1 (46%)

| chosen | subpar |
|---|---|
| 18.Be3 Rf6 [19.Qd5] Raf8 20.Ng5 Qd7 [21.Ne4] [Rg6] 22.Ng3 Qg4 23.f3 [Qh4] 24.Bf2 [Bg5] 25.Rad1 [Bf4] | 18.Be3 Rf6 [19.Qd5] Raf8 20.Ng5 Qd7 21.Rad1 Rg6 22.Ne4 Qg4 23.Ng3 h5 24.h3 [Qh4] 25.Qe4 [Qf6] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bc4%20Nf6%204.d3%20Be7%205.O-O%20O-O%206.Nc3%20d6%207.a3%20Be6%208.Qe2%20Bxc4%209.dxc4%20Nd7%2010.Nd5%20Nc5%2011.b4%20Ne6%2012.c3%20f5%2013.exf5%20Rxf5%2014.Qe4%20Rf8%2015.Qg4%20Qd7%2016.Nxc7%20Qxc7%2017.Qxe6%2B%20Kh8%2018.Be3%20Rf6%2019.Qd5%20Raf8%2020.Ng5%20Qd7%2021.Ne4%20Rg6%2022.Ng3%20Qg4%2023.f3%20Qh4%2024.Bf2%20Bg5%2025.Rad1%20Bf4#34) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bc4%20Nf6%204.d3%20Be7%205.O-O%20O-O%206.Nc3%20d6%207.a3%20Be6%208.Qe2%20Bxc4%209.dxc4%20Nd7%2010.Nd5%20Nc5%2011.b4%20Ne6%2012.c3%20f5%2013.exf5%20Rxf5%2014.Qe4%20Rf8%2015.Qg4%20Qd7%2016.Nxc7%20Qxc7%2017.Qxe6%2B%20Kh8%2018.Be3%20Rf6%2019.Qd5%20Raf8%2020.Ng5%20Qd7%2021.Rad1%20Rg6%2022.Ne4%20Qg4%2023.Ng3%20h5%2024.h3%20Qh4%2025.Qe4%20Qf6#34) |

position 26 (`r1b1r1k1/2p3bp/2p2pq1/2Np4/p5P1/P1Q1B3/1PP2P1P/1K1R2R1 w - - 3 24`), split at ply 7: Qf4 (48% there) vs Qxg7+ (45%)

| chosen | subpar |
|---|---|
| 24.g5 f5 25.Bd4 Bxd4 [26.Qxd4] Qg7 [27.Qf4] Qe5 [28.Qh4] Rb8 29.Nd3 Qc3 30.Kc1 Ba6 31.g6 Bxd3 | 24.g5 f5 25.Bd4 Bxd4 [26.Qxd4] Qg7 27.Qxg7+ Kxg7 28.Rde1 Rxe1+ 29.Rxe1 Kf7 30.f4 Ra5 31.Nd3 c5 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.g5%20f5%2025.Bd4%20Bxd4%2026.Qxd4%20Qg7%2027.Qf4%20Qe5%2028.Qh4%20Rb8%2029.Nd3%20Qc3%2030.Kc1%20Ba6%2031.g6%20Bxd3#46) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.g5%20f5%2025.Bd4%20Bxd4%2026.Qxd4%20Qg7%2027.Qxg7%2B%20Kxg7%2028.Rde1%20Rxe1%2B%2029.Rxe1%20Kf7%2030.f4%20Ra5%2031.Nd3%20c5#46) |

#### S #10 (k = 0): latents 778

position 43 (`1r1qk2r/p2b2pp/1p3n2/n3Qp2/P2Pp3/4PP2/3N2PP/R1B1KB1R b KQk - 1 17`), split at ply 10: Rc1 (51% there) vs Rd1 (49%)

| chosen | subpar |
|---|---|
| 17...Qe7 18.Qxb8+ Kf7 [19.Qxh8] exf3 [20.Nxf3] Qb4+ [21.Bd2] Qb2 [22.Rc1] Ne4 23.Rc7 Qb1+ 24.Bc1 Qb4+ 25.Bd2 | 17...Qe7 18.Qxb8+ Kf7 [19.Qxh8] exf3 [20.Nxf3] Qb4+ [21.Bd2] Qb2 22.Rd1 Ne4 23.Bd3 Nb3 24.Bxe4 fxe4 25.Ng5+ |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20f6%203.c4%20e5%204.e3%20e4%205.Nfd2%20c6%206.Nc3%20Bb4%207.cxd5%20cxd5%208.f3%20f5%209.Qa4%2B%20Nc6%2010.a3%20Bxc3%2011.bxc3%20Bd7%2012.Qb3%20Rb8%2013.c4%20dxc4%2014.Qxc4%20Nf6%2015.a4%20Na5%2016.Qc5%20b6%2017.Qe5%2B%20Qe7%2018.Qxb8%2B%20Kf7%2019.Qxh8%20exf3%2020.Nxf3%20Qb4%2B%2021.Bd2%20Qb2%2022.Rc1%20Ne4%2023.Rc7%20Qb1%2B%2024.Bc1%20Qb4%2B%2025.Bd2#33) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20f6%203.c4%20e5%204.e3%20e4%205.Nfd2%20c6%206.Nc3%20Bb4%207.cxd5%20cxd5%208.f3%20f5%209.Qa4%2B%20Nc6%2010.a3%20Bxc3%2011.bxc3%20Bd7%2012.Qb3%20Rb8%2013.c4%20dxc4%2014.Qxc4%20Nf6%2015.a4%20Na5%2016.Qc5%20b6%2017.Qe5%2B%20Qe7%2018.Qxb8%2B%20Kf7%2019.Qxh8%20exf3%2020.Nxf3%20Qb4%2B%2021.Bd2%20Qb2%2022.Rd1%20Ne4%2023.Bd3%20Nb3%2024.Bxe4%20fxe4%2025.Ng5%2B#33) |

position 48 (`r4r1k/1ppqn2p/p5p1/4pP2/2Pp2P1/3PbRNP/PP4BK/R2Q4 b - - 1 21`), split at ply 9: Rg8 (50% there) vs Rb8 (48%)

| chosen | subpar |
|---|---|
| 21...gxf5 22.gxf5 Nxf5 23.Nxf5 Rxf5 24.Rxf5 [Qxf5] [25.Bxb7] [Rg8] [26.Qf3] [Qg5] [27.Rf1] [Bf4+] [28.Kh1] [Qg3] [29.Qxg3] | 21...gxf5 22.gxf5 Nxf5 23.Nxf5 Rxf5 24.Rxf5 [Qxf5] [25.Bxb7] Rb8 [26.Be4] Rxb2+ [27.Kh1] Qxh3# |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nc3%20e5%203.g3%20Bc5%204.Bg2%20a6%205.Nge2%20Nge7%206.h3%20d6%207.d3%20O-O%208.O-O%20Be6%209.Kh2%20f5%2010.f4%20Qd7%2011.exf5%20Nxf5%2012.g4%20Ne3%2013.Bxe3%20Bxe3%2014.f5%20Bf7%2015.Nd5%20Bxd5%2016.Bxd5%2B%20Kh8%2017.Bg2%20d5%2018.c3%20Ne7%2019.Rf3%20d4%2020.c4%20g6%2021.Ng3%20gxf5%2022.gxf5%20Nxf5%2023.Nxf5%20Rxf5%2024.Rxf5%20Qxf5%2025.Bxb7%20Rg8%2026.Qf3%20Qg5%2027.Rf1%20Bf4%2B%2028.Kh1%20Qg3%2029.Qxg3#41) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nc3%20e5%203.g3%20Bc5%204.Bg2%20a6%205.Nge2%20Nge7%206.h3%20d6%207.d3%20O-O%208.O-O%20Be6%209.Kh2%20f5%2010.f4%20Qd7%2011.exf5%20Nxf5%2012.g4%20Ne3%2013.Bxe3%20Bxe3%2014.f5%20Bf7%2015.Nd5%20Bxd5%2016.Bxd5%2B%20Kh8%2017.Bg2%20d5%2018.c3%20Ne7%2019.Rf3%20d4%2020.c4%20g6%2021.Ng3%20gxf5%2022.gxf5%20Nxf5%2023.Nxf5%20Rxf5%2024.Rxf5%20Qxf5%2025.Bxb7%20Rb8%2026.Be4%20Rxb2%2B%2027.Kh1%20Qxh3%23#41) |

position 47 (`r2qr1k1/pp3ppp/1bn5/3p4/3Nb2n/1NP2PBP/PP2B1PK/R2Q1R2 b - - 0 16`), split at ply 8: Bxf5 (52% there) vs Bf2 (48%)

| chosen | subpar |
|---|---|
| 16...Bg6 17.Bd3 Nxd4 18.Nxd4 Bxd4 19.cxd4 [Nf5] [20.Bxf5] [Bxf5] [21.Re1] [Qb6] [22.Qd2] h6 23.Rac1 Rxe1 24.Rxe1 | 16...Bg6 17.Bd3 Nxd4 18.Nxd4 Bxd4 19.cxd4 [Nf5] 20.Bf2 Qd6+ 21.Kg1 Qf4 [22.Bxf5] [Bxf5] [23.Qb3] [Re2] 24.Qxd5 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bg6%2017.Bd3%20Nxd4%2018.Nxd4%20Bxd4%2019.cxd4%20Nf5%2020.Bxf5%20Bxf5%2021.Re1%20Qb6%2022.Qd2%20h6%2023.Rac1%20Rxe1%2024.Rxe1#31) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bg6%2017.Bd3%20Nxd4%2018.Nxd4%20Bxd4%2019.cxd4%20Nf5%2020.Bf2%20Qd6%2B%2021.Kg1%20Qf4%2022.Bxf5%20Bxf5%2023.Qb3%20Re2%2024.Qxd5#31) |

## W

| k | pairs | nonzero v | families | held-out recurrence: median / 90% / max | null 95th: median | null (every draw): 90% / 99% | families above their null 95th (chance: 5%) |
|---|---|---|---|---|---|---|---|
| 0 | 2462 | 100% | 664 | 0.6% / 2.5% / 8.4% | 1.6% | 2.1% / 5.5% | 34 (5%) |
| 2 | 2460 | 33% | 620 | 0.0% / 0.2% / 1.5% | 0.0% | 0.1% / 0.3% | 45 (7%) |
| 4 | 2458 | 15% | 303 | 0.0% / 0.1% / 0.8% | 0.0% | 0.0% / 0.2% | 33 (11%) |
| 6 | 2455 | 14% | 299 | 0.0% / 0.2% / 1.2% | 0.0% | 0.0% / 0.1% | 58 (19%) |

### W: the top 20 families by held-out recurrence

| # | k | latents (weight) | found in | held out on | recurrence | null 95th | persistence (pairs on at split) | positions found |
|---|---|---|---|---|---|---|---|---|
| 1 | 0 | 778 (1.00) | A (5 v's) | B | 8.4% | 5.5% | 1.0 (102) | 11, 18, 20, 25, 31 |
| 2 | 0 | 778 (1.00) | B (4 v's) | A | 8.2% | 5.4% | 1.0 (103) | 12, 13, 42, 44 |
| 3 | 0 | 1006 (1.00) | B (3 v's) | A | 8.1% | 5.8% | 1.0 (101) | 15, 27, 32 |
| 4 | 0 | 499 (1.00) | A (11 v's) | B | 7.5% | 4.7% | 1.0 (91) | 3, 9, 18, 19, 26, 29, 31, 33, 38 |
| 5 | 0 | 62 (1.00) | A (52 v's) | B | 7.2% | 5.0% | 1.0 (87) | 0, 3, 5, 7, 9, 16, 18, 19, 20, 24, 25, 26 ... |
| 6 | 0 | 746 (1.00) | A (2 v's) | B | 7.0% | 5.3% | 1.0 (85) | 6 |
| 7 | 0 | 746 (1.00) | B (4 v's) | A | 6.9% | 4.8% | 1.0 (86) | 14, 30, 40, 48 |
| 8 | 0 | 62 (1.00) | B (51 v's) | A | 5.9% | 4.9% | 1.0 (74) | 1, 2, 4, 8, 10, 13, 14, 17, 21, 22, 23, 27 ... |
| 9 | 0 | 140 (1.00) | B (34 v's) | A | 5.9% | 5.6% | 1.0 (74) | 4, 10, 13, 15, 21, 22, 23, 27, 30, 32, 36, 40 ... |
| 10 | 0 | 894 (1.00) | A (1 v's) | B | 5.5% | 5.0% | 1.0 (67) | 3 |
| 11 | 0 | 1127 (1.00) | A (1 v's) | B | 5.5% | 5.2% | 1.0 (67) | 34 |
| 12 | 0 | 499 (1.00) | B (13 v's) | A | 5.5% | 5.9% | 1.0 (69) | 2, 4, 15, 22, 27, 32, 42, 43 |
| 13 | 0 | 550 (1.00) | B (4 v's) | A | 5.4% | 5.4% | 1.0 (67) | 21, 27, 48 |
| 14 | 0 | 327 (1.00) | A (6 v's) | B | 5.1% | 5.1% | 1.0 (62) | 3, 5, 6, 20, 25, 31 |
| 15 | 0 | 140 (1.00) | A (26 v's) | B | 5.0% | 4.9% | 1.0 (61) | 0, 7, 11, 16, 24, 26, 28, 29, 31, 34, 35, 37 ... |
| 16 | 0 | 700 (1.00) | A (2 v's) | B | 5.0% | 5.1% | 1.0 (60) | 31 |
| 17 | 0 | 505 (1.00) | B (5 v's) | A | 4.9% | 4.9% | 1.0 (61) | 4, 13, 30, 40, 42 |
| 18 | 0 | 642 (1.00) | A (3 v's) | B | 4.9% | 5.5% | 1.0 (59) | 11, 19, 34 |
| 19 | 0 | 2641 (1.00) | A (1 v's) | B | 4.9% | 5.0% | 1.0 (59) | 19 |
| 20 | 0 | 425 (1.00) | A (4 v's) | B | 4.8% | 5.0% | 1.0 (58) | 9, 33, 49 |

#### W #1 (k = 0): latents 778

position 15 (`r1q2rk1/2B2ppp/p1Q1p3/3p4/3Pn3/P3P3/P1P2PPP/R4RK1 b - - 4 17`), split at ply 5: Nd2 (51% there) vs Nc3 (49%)

| chosen | subpar |
|---|---|
| 17...Ra7 18.f3 Rxc7 [19.Qa4] [Nd2] [20.Rfd1] Nc4 [21.e4] [Nb2] [22.Qb3] Nxd1 [23.Rxd1] [Rxc2] [24.exd5] exd5 [25.Qxd5] | 17...Ra7 18.f3 Rxc7 [19.Qa4] Nc3 [20.Qb3] Ne2+ [21.Kf2] Rxc2 [22.Ke1] Nc3 [23.Rf2] Rxf2 [24.Kxf2] Nb5 [25.a4] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bf4%20d6%203.e3%20Nc6%204.Bb5%20Bd7%205.Bxc6%20Bxc6%206.Nf3%20Bxf3%207.Qxf3%20e6%208.Qxb7%20d5%209.Bxc7%20Qc8%2010.Qc6%2B%20Nd7%2011.Na3%20Be7%2012.Nb5%20O-O%2013.Qc3%20a6%2014.Na3%20Bxa3%2015.bxa3%20Nf6%2016.O-O%20Ne4%2017.Qc6%20Ra7%2018.f3%20Rxc7%2019.Qa4%20Nd2%2020.Rfd1%20Nc4%2021.e4%20Nb2%2022.Qb3%20Nxd1%2023.Rxd1%20Rxc2%2024.exd5%20exd5%2025.Qxd5#33) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bf4%20d6%203.e3%20Nc6%204.Bb5%20Bd7%205.Bxc6%20Bxc6%206.Nf3%20Bxf3%207.Qxf3%20e6%208.Qxb7%20d5%209.Bxc7%20Qc8%2010.Qc6%2B%20Nd7%2011.Na3%20Be7%2012.Nb5%20O-O%2013.Qc3%20a6%2014.Na3%20Bxa3%2015.bxa3%20Nf6%2016.O-O%20Ne4%2017.Qc6%20Ra7%2018.f3%20Rxc7%2019.Qa4%20Nc3%2020.Qb3%20Ne2%2B%2021.Kf2%20Rxc2%2022.Ke1%20Nc3%2023.Rf2%20Rxf2%2024.Kxf2%20Nb5%2025.a4#33) |

position 14 (`2r1k2r/1bqpbpp1/p3p2p/1p4Pn/3nP1BP/2N1BP2/PPPQ4/2KR3R w k - 0 15`), split at ply 13: Rxc8 (56% there) vs Qb4+ (44%)

| chosen | subpar |
|---|---|
| [15.Qxd4] Nf4 [16.Bxf4] [Qxf4+] [17.Kb1] [hxg5] 18.hxg5 Rxh1 [19.Rxh1] Bxg5 20.Rh8+ Ke7 [21.Rxc8] Bxc8 22.Qc5+ Kf6 | [15.Qxd4] Nf4 [16.Bxf4] [Qxf4+] [17.Kb1] [hxg5] 18.hxg5 Rxh1 [19.Rxh1] Bxg5 20.Rh8+ Ke7 21.Qb4+ [d6] [22.Rxc8] [Bxc8] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Qxd4%20Nf4%2016.Bxf4%20Qxf4%2B%2017.Kb1%20hxg5%2018.hxg5%20Rxh1%2019.Rxh1%20Bxg5%2020.Rh8%2B%20Ke7%2021.Rxc8%20Bxc8%2022.Qc5%2B%20Kf6#28) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Qxd4%20Nf4%2016.Bxf4%20Qxf4%2B%2017.Kb1%20hxg5%2018.hxg5%20Rxh1%2019.Rxh1%20Bxg5%2020.Rh8%2B%20Ke7%2021.Qb4%2B%20d6%2022.Rxc8%20Bxc8#28) |

position 32 (`r2qk2r/ppp2ppp/2n5/7b/1b1P4/2P2N1P/PB2BPP1/R2QK2R b KQkq - 0 12`), split at ply 9: Bxe2 (56% there) vs Qxd1 (44%)

| chosen | subpar |
|---|---|
| 12...Ba5 13.O-O O-O 14.Re1 Re8 15.Ne5 Nxe5 [16.dxe5] [Bxe2] [17.Rxe2] [Qxd1+] [18.Rxd1] [Rad8] [19.Rxd8] [Rxd8] [20.e6] | 12...Ba5 13.O-O O-O 14.Re1 Re8 15.Ne5 Nxe5 [16.dxe5] Qxd1 [17.Raxd1] [Bxe2] [18.Rxe2] [Rad8] [19.Rxd8] [Rxd8] [20.e6] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20d5%202.exd5%20Nf6%203.Nc3%20Nxd5%204.Bc4%20Nxc3%205.bxc3%20Nc6%206.Bb2%20e5%207.Nf3%20Bg4%208.h3%20Bh5%209.Be2%20Bc5%2010.d4%20exd4%2011.cxd4%20Bb4%2B%2012.c3%20Ba5%2013.O-O%20O-O%2014.Re1%20Re8%2015.Ne5%20Nxe5%2016.dxe5%20Bxe2%2017.Rxe2%20Qxd1%2B%2018.Rxd1%20Rad8%2019.Rxd8%20Rxd8%2020.e6#23) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20d5%202.exd5%20Nf6%203.Nc3%20Nxd5%204.Bc4%20Nxc3%205.bxc3%20Nc6%206.Bb2%20e5%207.Nf3%20Bg4%208.h3%20Bh5%209.Be2%20Bc5%2010.d4%20exd4%2011.cxd4%20Bb4%2B%2012.c3%20Ba5%2013.O-O%20O-O%2014.Re1%20Re8%2015.Ne5%20Nxe5%2016.dxe5%20Qxd1%2017.Raxd1%20Bxe2%2018.Rxe2%20Rad8%2019.Rxd8%20Rxd8%2020.e6#23) |

#### W #2 (k = 0): latents 778

position 34 (`r2qk2r/1pp1bppp/2n1p3/1p6/3PR3/P1P2N2/5PPP/R2Q2K1 b kq - 0 14`), split at ply 4: Qc2 (50% there) vs Qxd5 (48%)

| chosen | subpar |
|---|---|
| [14...O-O] [15.Qb3] [Qd5] [16.Qc2] [Bxa3] 17.Rh4 h6 18.Ne5 Nxe5 [19.dxe5] [Qxe5] [20.Rh3] [Bd6] [21.g3] Rxa1+ 22.Kg2 | [14...O-O] [15.Qb3] [Qd5] 16.Qxd5 [exd5] [17.Re3] [Rfe8] [18.Rb1] [Rxa3] 19.Rxb5 Ra1+ [20.Re1] Rxe1+ [21.Nxe1] b6 22.Rxd5 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20O-O%2015.Qb3%20Qd5%2016.Qc2%20Bxa3%2017.Rh4%20h6%2018.Ne5%20Nxe5%2019.dxe5%20Qxe5%2020.Rh3%20Bd6%2021.g3%20Rxa1%2B%2022.Kg2#27) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20O-O%2015.Qb3%20Qd5%2016.Qxd5%20exd5%2017.Re3%20Rfe8%2018.Rb1%20Rxa3%2019.Rxb5%20Ra1%2B%2020.Re1%20Rxe1%2B%2021.Nxe1%20b6%2022.Rxd5#27) |

position 46 (`1r1q1r2/pb3pkp/1n1p1Np1/2p5/1p4n1/3P4/PPPQ2BP/1RB2RK1 w - - 0 22`), split at ply 11: Rf3 (52% there) vs Rbf1 (48%)

| chosen | subpar |
|---|---|
| 22.Qh6+ Nxh6 23.Bxh6+ Kxh6 [24.Bxb7] Rxb7 [25.Ng4+] Kg7 [26.Rf6] Nd5 [27.Rf3] Qg5 [28.h3] Nf4 29.Rbf1 Ne2+ | 22.Qh6+ Nxh6 23.Bxh6+ Kxh6 [24.Bxb7] Rxb7 [25.Ng4+] Kg7 [26.Rf6] Nd5 27.Rbf1 Nxf6 [28.Nxf6] [Qxf6] [29.Rxf6] [Kxf6] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nc3%20Nc6%203.g3%20g6%204.Bg2%20Bg7%205.Nge2%20d6%206.O-O%20e6%207.f4%20Nge7%208.g4%20O-O%209.Ng3%20Rb8%2010.d3%20b5%2011.Rb1%20b4%2012.Nce2%20Bb7%2013.f5%20Nc8%2014.Nf4%20exf5%2015.exf5%20Nb6%2016.Ne4%20Ne5%2017.f6%20Bxf6%2018.Nh5%20Bh8%2019.Nhf6%2B%20Bxf6%2020.Nxf6%2B%20Kg7%2021.Qd2%20Nxg4%2022.Qh6%2B%20Nxh6%2023.Bxh6%2B%20Kxh6%2024.Bxb7%20Rxb7%2025.Ng4%2B%20Kg7%2026.Rf6%20Nd5%2027.Rf3%20Qg5%2028.h3%20Nf4%2029.Rbf1%20Ne2%2B#42) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nc3%20Nc6%203.g3%20g6%204.Bg2%20Bg7%205.Nge2%20d6%206.O-O%20e6%207.f4%20Nge7%208.g4%20O-O%209.Ng3%20Rb8%2010.d3%20b5%2011.Rb1%20b4%2012.Nce2%20Bb7%2013.f5%20Nc8%2014.Nf4%20exf5%2015.exf5%20Nb6%2016.Ne4%20Ne5%2017.f6%20Bxf6%2018.Nh5%20Bh8%2019.Nhf6%2B%20Bxf6%2020.Nxf6%2B%20Kg7%2021.Qd2%20Nxg4%2022.Qh6%2B%20Nxh6%2023.Bxh6%2B%20Kxh6%2024.Bxb7%20Rxb7%2025.Ng4%2B%20Kg7%2026.Rf6%20Nd5%2027.Rbf1%20Nxf6%2028.Nxf6%20Qxf6%2029.Rxf6%20Kxf6#42) |

position 25 (`1r3r2/pb4kp/1p4p1/2pnP3/4B3/2P4P/PP1N2P1/R4RK1 w - - 3 21`), split at ply 3: Bxb7 (53% there) vs Rxf8 (47%)

| chosen | subpar |
|---|---|
| 21.Rad1 [Ne3] [22.Bxb7] [Nxd1] [23.Rxd1] [Rxb7] [24.Ne4] [Re7] [25.Nd6] [Rxe5] [26.Nc4] [Re2] [27.Rd7+] Rf7 [28.Rxf7+] [Kxf7] | 21.Rad1 [Ne3] 22.Rxf8 [Rxf8] 23.Re1 Bxe4 [24.Nxe4] [Nc2] [25.Re2] [Na1] 26.e6 Re8 27.Ng5 Kf6 28.Nxh7+ Ke7 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.Rad1%20Ne3%2022.Bxb7%20Nxd1%2023.Rxd1%20Rxb7%2024.Ne4%20Re7%2025.Nd6%20Rxe5%2026.Nc4%20Re2%2027.Rd7%2B%20Rf7%2028.Rxf7%2B%20Kxf7#40) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.Rad1%20Ne3%2022.Rxf8%20Rxf8%2023.Re1%20Bxe4%2024.Nxe4%20Nc2%2025.Re2%20Na1%2026.e6%20Re8%2027.Ng5%20Kf6%2028.Nxh7%2B%20Ke7#40) |

#### W #3 (k = 0): latents 1006

position 18 (`r1bq1rk1/pp3ppp/3b1n2/4N3/2BppP2/4B3/PPP3PP/R2Q1RK1 w - - 0 12`), split at ply 4: Bb7 (53% there) vs Bc5 (47%)

| chosen | subpar |
|---|---|
| 12.Bxd4 [b6] [13.Re1] [Bb7] [14.Ng4] Nxg4 15.Qxg4 g6 16.Qh3 Bxf4 17.Qh6 Qxd4+ 18.Kh1 Bxh6 19.Rad1 Qxc4 | 12.Bxd4 [b6] [13.Re1] Bc5 14.Bxc5 bxc5 15.Qxd8 Rxd8 16.Nxf7 Rd2 17.Ng5+ Kf8 18.Nxe4 Nxe4 19.Rxe4 Rxc2 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nf6%203.Nxe5%20Nxe4%204.d4%20d5%205.Bd3%20Nd7%206.O-O%20Bd6%207.f4%20O-O%208.Nc3%20Ndf6%209.Nxe4%20dxe4%2010.Bc4%20c5%2011.Be3%20cxd4%2012.Bxd4%20b6%2013.Re1%20Bb7%2014.Ng4%20Nxg4%2015.Qxg4%20g6%2016.Qh3%20Bxf4%2017.Qh6%20Qxd4%2B%2018.Kh1%20Bxh6%2019.Rad1%20Qxc4#22) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nf6%203.Nxe5%20Nxe4%204.d4%20d5%205.Bd3%20Nd7%206.O-O%20Bd6%207.f4%20O-O%208.Nc3%20Ndf6%209.Nxe4%20dxe4%2010.Bc4%20c5%2011.Be3%20cxd4%2012.Bxd4%20b6%2013.Re1%20Bc5%2014.Bxc5%20bxc5%2015.Qxd8%20Rxd8%2016.Nxf7%20Rd2%2017.Ng5%2B%20Kf8%2018.Nxe4%20Nxe4%2019.Rxe4%20Rxc2#22) |

position 46 (`1r1q1r2/pb3pkp/1n1p1Np1/2p5/1p4n1/3P4/PPPQ2BP/1RB2RK1 w - - 0 22`), split at ply 8: Rbe8 (53% there) vs Nd5 (47%)

| chosen | subpar |
|---|---|
| 22.Nxg4 Qh4 [23.Qh6+] Qxh6 24.Nxh6 Bxg2 25.Kxg2 [Rbe8] 26.Bg5 [Re2+] 27.Rf2 [Rxf2+] 28.Kxf2 f6 29.Be3 [g5] | 22.Nxg4 Qh4 [23.Qh6+] Qxh6 24.Nxh6 Bxg2 25.Kxg2 Nd5 26.Ng4 [Rbe8] 27.Bh6+ [Kg8] 28.Bxf8 Kxf8 29.Rbe1 [Rxe1] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nc3%20Nc6%203.g3%20g6%204.Bg2%20Bg7%205.Nge2%20d6%206.O-O%20e6%207.f4%20Nge7%208.g4%20O-O%209.Ng3%20Rb8%2010.d3%20b5%2011.Rb1%20b4%2012.Nce2%20Bb7%2013.f5%20Nc8%2014.Nf4%20exf5%2015.exf5%20Nb6%2016.Ne4%20Ne5%2017.f6%20Bxf6%2018.Nh5%20Bh8%2019.Nhf6%2B%20Bxf6%2020.Nxf6%2B%20Kg7%2021.Qd2%20Nxg4%2022.Nxg4%20Qh4%2023.Qh6%2B%20Qxh6%2024.Nxh6%20Bxg2%2025.Kxg2%20Rbe8%2026.Bg5%20Re2%2B%2027.Rf2%20Rxf2%2B%2028.Kxf2%20f6%2029.Be3%20g5#42) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nc3%20Nc6%203.g3%20g6%204.Bg2%20Bg7%205.Nge2%20d6%206.O-O%20e6%207.f4%20Nge7%208.g4%20O-O%209.Ng3%20Rb8%2010.d3%20b5%2011.Rb1%20b4%2012.Nce2%20Bb7%2013.f5%20Nc8%2014.Nf4%20exf5%2015.exf5%20Nb6%2016.Ne4%20Ne5%2017.f6%20Bxf6%2018.Nh5%20Bh8%2019.Nhf6%2B%20Bxf6%2020.Nxf6%2B%20Kg7%2021.Qd2%20Nxg4%2022.Nxg4%20Qh4%2023.Qh6%2B%20Qxh6%2024.Nxh6%20Bxg2%2025.Kxg2%20Nd5%2026.Ng4%20Rbe8%2027.Bh6%2B%20Kg8%2028.Bxf8%20Kxf8%2029.Rbe1%20Rxe1#42) |

position 49 (`1R6/3r1pbk/q2P3p/1NQ1p2n/4P1p1/5NP1/5PKP/8 w - - 0 31`), split at ply 5: Qf5+ (56% there) vs Qxh5 (44%)

| chosen | subpar |
|---|---|
| [31.Nxe5] [Bxe5] 32.Qxe5 [Qc6] [33.Qf5+] [Kg7] [34.Qxg4+] [Kf6] [35.Qf5+] [Kg7] [36.Qg4+] [Kf6] 37.Qxh5 [Qxe4+] 38.Qf3+ Qxf3+ | [31.Nxe5] [Bxe5] 32.Qxe5 [Qc6] 33.Qxh5 Qxe4+ 34.Kf1 Qb1+ 35.Kg2 [Qe4+] 36.Kf1 [Qb1+] 37.Ke2 [Qb2+] 38.Ke3 [Qb3+] |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.c4%20g6%203.Nc3%20Bg7%204.e4%20d6%205.Nf3%20O-O%206.Be2%20e5%207.d5%20c6%208.O-O%20cxd5%209.cxd5%20Nh5%2010.g3%20Bh3%2011.Re1%20a6%2012.Be3%20b5%2013.b4%20Nd7%2014.a4%20bxa4%2015.Rxa4%20a5%2016.bxa5%20Rxa5%2017.Nb5%20Rxa4%2018.Qxa4%20Nc5%2019.Bxc5%20dxc5%2020.Qc4%20Qb6%2021.Nc3%20h6%2022.Rb1%20Qa5%2023.Bf1%20Bxf1%2024.Kxf1%20Rc8%2025.Kg2%20g5%2026.Rb7%20Rc7%2027.Rb8%2B%20Kh7%2028.d6%20Rd7%2029.Nb5%20Qa6%2030.Qxc5%20g4%2031.Nxe5%20Bxe5%2032.Qxe5%20Qc6%2033.Qf5%2B%20Kg7%2034.Qxg4%2B%20Kf6%2035.Qf5%2B%20Kg7%2036.Qg4%2B%20Kf6%2037.Qxh5%20Qxe4%2B%2038.Qf3%2B%20Qxf3%2B#60) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.c4%20g6%203.Nc3%20Bg7%204.e4%20d6%205.Nf3%20O-O%206.Be2%20e5%207.d5%20c6%208.O-O%20cxd5%209.cxd5%20Nh5%2010.g3%20Bh3%2011.Re1%20a6%2012.Be3%20b5%2013.b4%20Nd7%2014.a4%20bxa4%2015.Rxa4%20a5%2016.bxa5%20Rxa5%2017.Nb5%20Rxa4%2018.Qxa4%20Nc5%2019.Bxc5%20dxc5%2020.Qc4%20Qb6%2021.Nc3%20h6%2022.Rb1%20Qa5%2023.Bf1%20Bxf1%2024.Kxf1%20Rc8%2025.Kg2%20g5%2026.Rb7%20Rc7%2027.Rb8%2B%20Kh7%2028.d6%20Rd7%2029.Nb5%20Qa6%2030.Qxc5%20g4%2031.Nxe5%20Bxe5%2032.Qxe5%20Qc6%2033.Qxh5%20Qxe4%2B%2034.Kf1%20Qb1%2B%2035.Kg2%20Qe4%2B%2036.Kf1%20Qb1%2B%2037.Ke2%20Qb2%2B%2038.Ke3%20Qb3%2B#60) |

#### W #4 (k = 0): latents 499

position 14 (`2r1k2r/1bqpbpp1/p3p2p/1p4Pn/3nP1BP/2N1BP2/PPPQ4/2KR3R w k - 0 15`), split at ply 8: Rg5 (54% there) vs Rxg7 (46%)

| chosen | subpar |
|---|---|
| 15.Bxd4 Nf4 16.gxh6 Rxh6 17.Bxg7 Rg6 [18.h5] [Rg5] 19.h6 Ng6 20.h7 Kd8 21.h8=Q+ Nxh8 22.Rxh8+ Bf8 | 15.Bxd4 Nf4 16.gxh6 Rxh6 17.Bxg7 Rg6 [18.h5] Rxg7 19.h6 [Rh7] 20.Ne2 Nxe2+ 21.Qxe2 Bg5+ [22.Kb1] Bxh6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Bxd4%20Nf4%2016.gxh6%20Rxh6%2017.Bxg7%20Rg6%2018.h5%20Rg5%2019.h6%20Ng6%2020.h7%20Kd8%2021.h8%3DQ%2B%20Nxh8%2022.Rxh8%2B%20Bf8#28) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Bxd4%20Nf4%2016.gxh6%20Rxh6%2017.Bxg7%20Rg6%2018.h5%20Rxg7%2019.h6%20Rh7%2020.Ne2%20Nxe2%2B%2021.Qxe2%20Bg5%2B%2022.Kb1%20Bxh6#28) |

position 4 (`r1bq1b1r/3k2pp/p1p5/1p1Bp1N1/8/3P4/PPP2PPP/RNB1K2R w KQ - 0 12`), split at ply 16: Kb6 (49% there) vs e4 (46%)

| chosen | subpar |
|---|---|
| 12.Be6+ [Kc7] 13.Bxc8 [Rxc8] 14.Nf7 [Qf6] 15.Nxh8 Bc5 16.O-O Rxh8 17.Nc3 Rf8 [18.Ne4] [Qf5] 19.Nxc5 [Kb6] | 12.Be6+ [Kc7] 13.Bxc8 [Rxc8] 14.Nf7 [Qf6] 15.Nxh8 Bc5 16.O-O Rxh8 17.Nc3 Rf8 [18.Ne4] [Qf5] 19.Nxc5 e4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Bc4%20a6%203.d3%20Nf6%204.Nf3%20b5%205.Bb3%20Nc6%206.Ng5%20d5%207.exd5%20Nxd5%208.Qf3%20Nce7%209.Qxf7%2B%20Kd7%2010.Qxd5%2B%20Nxd5%2011.Bxd5%20c6%2012.Be6%2B%20Kc7%2013.Bxc8%20Rxc8%2014.Nf7%20Qf6%2015.Nxh8%20Bc5%2016.O-O%20Rxh8%2017.Nc3%20Rf8%2018.Ne4%20Qf5%2019.Nxc5%20Kb6#22) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Bc4%20a6%203.d3%20Nf6%204.Nf3%20b5%205.Bb3%20Nc6%206.Ng5%20d5%207.exd5%20Nxd5%208.Qf3%20Nce7%209.Qxf7%2B%20Kd7%2010.Qxd5%2B%20Nxd5%2011.Bxd5%20c6%2012.Be6%2B%20Kc7%2013.Bxc8%20Rxc8%2014.Nf7%20Qf6%2015.Nxh8%20Bc5%2016.O-O%20Rxh8%2017.Nc3%20Rf8%2018.Ne4%20Qf5%2019.Nxc5%20e4#22) |

position 47 (`r2qr1k1/pp3ppp/1bn5/3p4/3Nb2n/1NP2PBP/PP2B1PK/R2Q1R2 b - - 0 16`), split at ply 7: Rxe4 (56% there) vs Qg5+ (44%)

| chosen | subpar |
|---|---|
| 16...Nxd4 [17.Nxd4] Bc7 18.fxe4 Bxg3+ 19.Kxg3 [Rxe4] [20.Bf3] Qg5+ [21.Kh2] Qf4+ [22.Kg1] Nxf3+ 23.Rxf3 [Qg5] 24.Qf1 | 16...Nxd4 [17.Nxd4] Bc7 18.fxe4 Bxg3+ 19.Kxg3 Qg5+ [20.Kh2] Qxg2# |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Nxd4%2017.Nxd4%20Bc7%2018.fxe4%20Bxg3%2B%2019.Kxg3%20Rxe4%2020.Bf3%20Qg5%2B%2021.Kh2%20Qf4%2B%2022.Kg1%20Nxf3%2B%2023.Rxf3%20Qg5%2024.Qf1#31) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Nxd4%2017.Nxd4%20Bc7%2018.fxe4%20Bxg3%2B%2019.Kxg3%20Qg5%2B%2020.Kh2%20Qxg2%23#31) |

#### W #5 (k = 0): latents 62

position 23 (`rnbqkr2/pppp4/4p2p/b3B1pn/3P4/2NB1N2/PP3PPP/R2QK2R b KQq - 3 14`), split at ply 4: Bxf4 (53% there) vs Bg7 (47%)

| chosen | subpar |
|---|---|
| 14...Nf4 15.O-O d6 [16.Bxf4] gxf4 17.Bg6+ Kd7 18.Qa4+ Nc6 19.d5 exd5 20.Nxd5 Rg8 21.Bf5+ Ke8 22.Rfe1+ | 14...Nf4 15.O-O d6 16.Bg7 Rf7 [17.Bxh6] Nxd3 [18.Qxd3] g4 19.Ng5 Rf5 20.Nce4 d5 21.Nc5 Qd6 [22.Ngxe6] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Bd6%203.d3%20Nf6%204.Bg5%20Bb4%2B%205.c3%20Bc5%206.d4%20exd4%207.cxd4%20Bb4%2B%208.Nc3%20Ba5%209.e5%20h6%2010.Bh4%20g5%2011.Bg3%20Nh5%2012.e6%20fxe6%2013.Be5%20Rf8%2014.Bd3%20Nf4%2015.O-O%20d6%2016.Bxf4%20gxf4%2017.Bg6%2B%20Kd7%2018.Qa4%2B%20Nc6%2019.d5%20exd5%2020.Nxd5%20Rg8%2021.Bf5%2B%20Ke8%2022.Rfe1%2B#27) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Bd6%203.d3%20Nf6%204.Bg5%20Bb4%2B%205.c3%20Bc5%206.d4%20exd4%207.cxd4%20Bb4%2B%208.Nc3%20Ba5%209.e5%20h6%2010.Bh4%20g5%2011.Bg3%20Nh5%2012.e6%20fxe6%2013.Be5%20Rf8%2014.Bd3%20Nf4%2015.O-O%20d6%2016.Bg7%20Rf7%2017.Bxh6%20Nxd3%2018.Qxd3%20g4%2019.Ng5%20Rf5%2020.Nce4%20d5%2021.Nc5%20Qd6%2022.Ngxe6#27) |

position 10 (`2r2rk1/pp1bb1pp/1qn1pn2/3p1p2/PP1P4/2P2N1P/3NBPPB/R1Q2RK1 w - - 1 15`), split at ply 11: Bxf6 (56% there) vs Bh2 (44%)

| chosen | subpar |
|---|---|
| 15.a5 Qd8 16.Re1 Ne4 [17.Nxe4] fxe4 18.Ne5 Nxe5 [19.Bxe5] Bf6 [20.Bxf6] Rxf6 21.Bg4 Qf8 22.Rf1 Rc7 | 15.a5 Qd8 16.Re1 Ne4 [17.Nxe4] fxe4 18.Ne5 Nxe5 [19.Bxe5] Bf6 20.Bh2 Bxd4 21.Qd2 Bxf2+ 22.Kh1 Bxe1 |
| [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nf6%202.d4%20e6%203.Bf4%20c5%204.e3%20cxd4%205.exd4%20Qb6%206.Qc1%20Nc6%207.c3%20Be7%208.Nbd2%20d5%209.h3%20Nh5%2010.Bh2%20O-O%2011.Be2%20Bd7%2012.O-O%20f5%2013.b4%20Nf6%2014.a4%20Rac8%2015.a5%20Qd8%2016.Re1%20Ne4%2017.Nxe4%20fxe4%2018.Ne5%20Nxe5%2019.Bxe5%20Bf6%2020.Bxf6%20Rxf6%2021.Bg4%20Qf8%2022.Rf1%20Rc7#28) | [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nf6%202.d4%20e6%203.Bf4%20c5%204.e3%20cxd4%205.exd4%20Qb6%206.Qc1%20Nc6%207.c3%20Be7%208.Nbd2%20d5%209.h3%20Nh5%2010.Bh2%20O-O%2011.Be2%20Bd7%2012.O-O%20f5%2013.b4%20Nf6%2014.a4%20Rac8%2015.a5%20Qd8%2016.Re1%20Ne4%2017.Nxe4%20fxe4%2018.Ne5%20Nxe5%2019.Bxe5%20Bf6%2020.Bh2%20Bxd4%2021.Qd2%20Bxf2%2B%2022.Kh1%20Bxe1#28) |

position 14 (`2r1k2r/1bqpbpp1/p3p2p/1p4Pn/3nP1BP/2N1BP2/PPPQ4/2KR3R w k - 0 15`), split at ply 13: Rxc8 (56% there) vs Qb4+ (44%)

| chosen | subpar |
|---|---|
| 15.Qxd4 Nf4 [16.Bxf4] Qxf4+ 17.Kb1 hxg5 [18.hxg5] Rxh1 [19.Rxh1] Bxg5 20.Rh8+ Ke7 [21.Rxc8] Bxc8 22.Qc5+ Kf6 | 15.Qxd4 Nf4 [16.Bxf4] Qxf4+ 17.Kb1 hxg5 [18.hxg5] Rxh1 [19.Rxh1] Bxg5 20.Rh8+ Ke7 21.Qb4+ d6 [22.Rxc8] Bxc8 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Qxd4%20Nf4%2016.Bxf4%20Qxf4%2B%2017.Kb1%20hxg5%2018.hxg5%20Rxh1%2019.Rxh1%20Bxg5%2020.Rh8%2B%20Ke7%2021.Rxc8%20Bxc8%2022.Qc5%2B%20Kf6#28) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Qxd4%20Nf4%2016.Bxf4%20Qxf4%2B%2017.Kb1%20hxg5%2018.hxg5%20Rxh1%2019.Rxh1%20Bxg5%2020.Rh8%2B%20Ke7%2021.Qb4%2B%20d6%2022.Rxc8%20Bxc8#28) |

#### W #6 (k = 0): latents 746

position 47 (`r2qr1k1/pp3ppp/1bn5/3p4/3Nb2n/1NP2PBP/PP2B1PK/R2Q1R2 b - - 0 16`), split at ply 4: Qxd4 (51% there) vs cxd4 (49%)

| chosen | subpar |
|---|---|
| 16...Bxd4 17.Nxd4 Nxd4 [18.Qxd4] Nf5 [19.Qf2] Bc2 20.Rfe1 Ba4 21.b3 Bc6 22.Bd3 Rxe1 23.Rxe1 Nxg3 [24.Qxg3] | 16...Bxd4 17.Nxd4 Nxd4 18.cxd4 Bf5 19.Bd3 Bxd3 [20.Qxd3] Ng6 21.Rfe1 Rxe1 22.Rxe1 [Qb6] 23.b3 h6 [24.Qf5] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bxd4%2017.Nxd4%20Nxd4%2018.Qxd4%20Nf5%2019.Qf2%20Bc2%2020.Rfe1%20Ba4%2021.b3%20Bc6%2022.Bd3%20Rxe1%2023.Rxe1%20Nxg3%2024.Qxg3#31) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.c3%20d5%204.exd5%20exd5%205.d4%20Nc6%206.Be2%20Bd6%207.dxc5%20Bxc5%208.Nbd2%20Nge7%209.Nb3%20Bb6%2010.O-O%20O-O%2011.h3%20Bf5%2012.Bf4%20Ng6%2013.Bg3%20Be4%2014.Nfd4%20Re8%2015.Kh2%20Nh4%2016.f3%20Bxd4%2017.Nxd4%20Nxd4%2018.cxd4%20Bf5%2019.Bd3%20Bxd3%2020.Qxd3%20Ng6%2021.Rfe1%20Rxe1%2022.Rxe1%20Qb6%2023.b3%20h6%2024.Qf5#31) |

position 10 (`2r2rk1/pp1bb1pp/1qn1pn2/3p1p2/PP1P4/2P2N1P/3NBPPB/R1Q2RK1 w - - 1 15`), split at ply 16: Qxb8 (50% there) vs Ne4 (45%)

| chosen | subpar |
|---|---|
| 15.a5 [Qd8] 16.b5 Nxa5 17.Nb3 Nxb3 [18.Qb2] Nxa1 19.Rxa1 a6 20.bxa6 bxa6 21.Bxa6 Rb8 22.Bxb8 [Qxb8] | 15.a5 [Qd8] 16.b5 Nxa5 17.Nb3 Nxb3 [18.Qb2] Nxa1 19.Rxa1 a6 20.bxa6 bxa6 21.Bxa6 Rb8 22.Bxb8 Ne4 |
| [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nf6%202.d4%20e6%203.Bf4%20c5%204.e3%20cxd4%205.exd4%20Qb6%206.Qc1%20Nc6%207.c3%20Be7%208.Nbd2%20d5%209.h3%20Nh5%2010.Bh2%20O-O%2011.Be2%20Bd7%2012.O-O%20f5%2013.b4%20Nf6%2014.a4%20Rac8%2015.a5%20Qd8%2016.b5%20Nxa5%2017.Nb3%20Nxb3%2018.Qb2%20Nxa1%2019.Rxa1%20a6%2020.bxa6%20bxa6%2021.Bxa6%20Rb8%2022.Bxb8%20Qxb8#28) | [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nf6%202.d4%20e6%203.Bf4%20c5%204.e3%20cxd4%205.exd4%20Qb6%206.Qc1%20Nc6%207.c3%20Be7%208.Nbd2%20d5%209.h3%20Nh5%2010.Bh2%20O-O%2011.Be2%20Bd7%2012.O-O%20f5%2013.b4%20Nf6%2014.a4%20Rac8%2015.a5%20Qd8%2016.b5%20Nxa5%2017.Nb3%20Nxb3%2018.Qb2%20Nxa1%2019.Rxa1%20a6%2020.bxa6%20bxa6%2021.Bxa6%20Rb8%2022.Bxb8%20Ne4#28) |

position 15 (`r1q2rk1/2B2ppp/p1Q1p3/3p4/3Pn3/P3P3/P1P2PPP/R4RK1 b - - 4 17`), split at ply 11: Qxa3 (50% there) vs Rxa2 (45%)

| chosen | subpar |
|---|---|
| 17...Ra7 18.f3 Rxc7 [19.Qxa6] Qxa6 20.fxe4 dxe4 21.Rab1 Rxc2 22.Rb4 [Qxa3] 23.Rb3 [Qxa2] 24.Rb7 Rxg2+ 25.Kh1 | 17...Ra7 18.f3 Rxc7 [19.Qxa6] Qxa6 20.fxe4 dxe4 21.Rab1 Rxc2 22.Rb4 Rxa2 23.Rfb1 h6 24.Rb8 Rxb8 25.Rxb8+ |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bf4%20d6%203.e3%20Nc6%204.Bb5%20Bd7%205.Bxc6%20Bxc6%206.Nf3%20Bxf3%207.Qxf3%20e6%208.Qxb7%20d5%209.Bxc7%20Qc8%2010.Qc6%2B%20Nd7%2011.Na3%20Be7%2012.Nb5%20O-O%2013.Qc3%20a6%2014.Na3%20Bxa3%2015.bxa3%20Nf6%2016.O-O%20Ne4%2017.Qc6%20Ra7%2018.f3%20Rxc7%2019.Qxa6%20Qxa6%2020.fxe4%20dxe4%2021.Rab1%20Rxc2%2022.Rb4%20Qxa3%2023.Rb3%20Qxa2%2024.Rb7%20Rxg2%2B%2025.Kh1#33) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bf4%20d6%203.e3%20Nc6%204.Bb5%20Bd7%205.Bxc6%20Bxc6%206.Nf3%20Bxf3%207.Qxf3%20e6%208.Qxb7%20d5%209.Bxc7%20Qc8%2010.Qc6%2B%20Nd7%2011.Na3%20Be7%2012.Nb5%20O-O%2013.Qc3%20a6%2014.Na3%20Bxa3%2015.bxa3%20Nf6%2016.O-O%20Ne4%2017.Qc6%20Ra7%2018.f3%20Rxc7%2019.Qxa6%20Qxa6%2020.fxe4%20dxe4%2021.Rab1%20Rxc2%2022.Rb4%20Rxa2%2023.Rfb1%20h6%2024.Rb8%20Rxb8%2025.Rxb8%2B#33) |

#### W #7 (k = 0): latents 746

position 34 (`r2qk2r/1pp1bppp/2n1p3/1p6/3PR3/P1P2N2/5PPP/R2Q2K1 b kq - 0 14`), split at ply 4: Qc2 (50% there) vs Qxd5 (48%)

| chosen | subpar |
|---|---|
| 14...O-O [15.Qb3] [Qd5] [16.Qc2] Bxa3 17.Rh4 h6 18.Ne5 Nxe5 19.dxe5 [Qxe5] 20.Rh3 Bd6 21.g3 Rxa1+ 22.Kg2 | 14...O-O [15.Qb3] [Qd5] 16.Qxd5 exd5 17.Re3 Rfe8 18.Rb1 Rxa3 19.Rxb5 Ra1+ 20.Re1 Rxe1+ 21.Nxe1 b6 22.Rxd5 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20O-O%2015.Qb3%20Qd5%2016.Qc2%20Bxa3%2017.Rh4%20h6%2018.Ne5%20Nxe5%2019.dxe5%20Qxe5%2020.Rh3%20Bd6%2021.g3%20Rxa1%2B%2022.Kg2#27) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20O-O%2015.Qb3%20Qd5%2016.Qxd5%20exd5%2017.Re3%20Rfe8%2018.Rb1%20Rxa3%2019.Rxb5%20Ra1%2B%2020.Re1%20Rxe1%2B%2021.Nxe1%20b6%2022.Rxd5#27) |

position 28 (`3r1k2/r4p1p/p1p1pqp1/2Pn4/2N5/6QP/1P3PP1/R2R2K1 w - - 16 27`), split at ply 10: Qxb2 (53% there) vs Nb4 (45%)

| chosen | subpar |
|---|---|
| 27.Ne5 Kg7 28.Nxc6 Rad7 29.Nxd8 Rxd8 30.c6 Rc8 31.Rxa6 [Qxb2] 32.Ra7 [Qb6] 33.Rda1 Rxc6 34.Qe5+ Kh6 | 27.Ne5 Kg7 28.Nxc6 Rad7 29.Nxd8 Rxd8 30.c6 Rc8 31.Rxa6 Nb4 32.Rb6 Nxc6 33.Rc1 Nd4 34.Rxc8 Ne2+ |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20g6%202.d4%20Bg7%203.c3%20d5%204.e5%20c5%205.Nf3%20Nc6%206.Bb5%20Qb6%207.a4%20a6%208.Bxc6%2B%20bxc6%209.a5%20Qb5%2010.Na3%20Qxa5%2011.O-O%20Qc7%2012.Bf4%20Bg4%2013.h3%20Bxf3%2014.Qxf3%20e6%2015.c4%20Ne7%2016.dxc5%20Bxe5%2017.Bxe5%20Qxe5%2018.cxd5%20Qxd5%2019.Qf6%20Rf8%2020.Rfd1%20Qf5%2021.Qd4%20Nd5%2022.Nc4%20Ke7%2023.Nb6%20Ra7%2024.Qh4%2B%20Qf6%2025.Qg3%20Rd8%2026.Nc4%20Kf8%2027.Ne5%20Kg7%2028.Nxc6%20Rad7%2029.Nxd8%20Rxd8%2030.c6%20Rc8%2031.Rxa6%20Qxb2%2032.Ra7%20Qb6%2033.Rda1%20Rxc6%2034.Qe5%2B%20Kh6#52) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20g6%202.d4%20Bg7%203.c3%20d5%204.e5%20c5%205.Nf3%20Nc6%206.Bb5%20Qb6%207.a4%20a6%208.Bxc6%2B%20bxc6%209.a5%20Qb5%2010.Na3%20Qxa5%2011.O-O%20Qc7%2012.Bf4%20Bg4%2013.h3%20Bxf3%2014.Qxf3%20e6%2015.c4%20Ne7%2016.dxc5%20Bxe5%2017.Bxe5%20Qxe5%2018.cxd5%20Qxd5%2019.Qf6%20Rf8%2020.Rfd1%20Qf5%2021.Qd4%20Nd5%2022.Nc4%20Ke7%2023.Nb6%20Ra7%2024.Qh4%2B%20Qf6%2025.Qg3%20Rd8%2026.Nc4%20Kf8%2027.Ne5%20Kg7%2028.Nxc6%20Rad7%2029.Nxd8%20Rxd8%2030.c6%20Rc8%2031.Rxa6%20Nb4%2032.Rb6%20Nxc6%2033.Rc1%20Nd4%2034.Rxc8%20Ne2%2B#52) |

position 16 (`r4rk1/p4p1p/5qp1/8/4nN2/1P2K1P1/P7/2B2B1R b - - 1 26`), split at ply 9: Qxa2 (56% there) vs Nxe3 (44%)

| chosen | subpar |
|---|---|
| 26...Nxg3 27.Rg1 Nf5+ 28.Kf2 Qd4+ 29.Be3 Qb2+ 30.Be2 [Qxa2] 31.Rc1 [Qxb3] 32.Bc4 Qb2+ 33.Be2 Nxe3 34.Kxe3 | 26...Nxg3 27.Rg1 Nf5+ 28.Kf2 Qd4+ 29.Be3 Qb2+ 30.Be2 Nxe3 31.Kxe3 Rae8+ 32.Kf2 Qd4+ 33.Kf1 Qxf4+ 34.Ke1 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Qh5%20Nf6%203.Qxe5%2B%20Be7%204.Nc3%20Ng4%205.Qf4%20d5%206.Nxd5%20O-O%207.Qxg4%20Bxg4%208.f3%20Bh4%2B%209.g3%20Bxg3%2B%2010.hxg3%20Bh5%2011.Rxh5%20g6%2012.Rh1%20c6%2013.Nc3%20c5%2014.Na4%20c4%2015.b3%20cxb3%2016.cxb3%20Nc6%2017.Nc5%20Nd4%2018.Nxb7%20Qb6%2019.Nd6%20Qxd6%2020.Nh3%20Nxf3%2B%2021.Kf2%20Qf6%2022.Rb1%20Nxd2%2B%2023.Nf4%20Nxb1%2024.Bb5%20Nc3%2025.Bf1%20Nxe4%2B%2026.Ke3%20Nxg3%2027.Rg1%20Nf5%2B%2028.Kf2%20Qd4%2B%2029.Be3%20Qb2%2B%2030.Be2%20Qxa2%2031.Rc1%20Qxb3%2032.Bc4%20Qb2%2B%2033.Be2%20Nxe3%2034.Kxe3#51) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Qh5%20Nf6%203.Qxe5%2B%20Be7%204.Nc3%20Ng4%205.Qf4%20d5%206.Nxd5%20O-O%207.Qxg4%20Bxg4%208.f3%20Bh4%2B%209.g3%20Bxg3%2B%2010.hxg3%20Bh5%2011.Rxh5%20g6%2012.Rh1%20c6%2013.Nc3%20c5%2014.Na4%20c4%2015.b3%20cxb3%2016.cxb3%20Nc6%2017.Nc5%20Nd4%2018.Nxb7%20Qb6%2019.Nd6%20Qxd6%2020.Nh3%20Nxf3%2B%2021.Kf2%20Qf6%2022.Rb1%20Nxd2%2B%2023.Nf4%20Nxb1%2024.Bb5%20Nc3%2025.Bf1%20Nxe4%2B%2026.Ke3%20Nxg3%2027.Rg1%20Nf5%2B%2028.Kf2%20Qd4%2B%2029.Be3%20Qb2%2B%2030.Be2%20Nxe3%2031.Kxe3%20Rae8%2B%2032.Kf2%20Qd4%2B%2033.Kf1%20Qxf4%2B%2034.Ke1#51) |

#### W #8 (k = 0): latents 62

position 46 (`1r1q1r2/pb3pkp/1n1p1Np1/2p5/1p4n1/3P4/PPPQ2BP/1RB2RK1 w - - 0 22`), split at ply 5: Bxb7 (51% there) vs Ng4+ (45%)

| chosen | subpar |
|---|---|
| 22.Qh6+ Nxh6 [23.Bxh6+] Kxh6 [24.Bxb7] Rxb7 25.Ng4+ Kg7 26.Rf6 Nd5 27.Rbf1 Nxf6 [28.Nxf6] Qxf6 [29.Rxf6] Kxf6 | 22.Qh6+ Nxh6 [23.Bxh6+] Kxh6 24.Ng4+ Kg7 [25.Bxb7] Rxb7 26.Nf6 Nd5 [27.Nxd5] Qg5+ 28.Kh1 Qxd5+ 29.Kg1 Re7 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nc3%20Nc6%203.g3%20g6%204.Bg2%20Bg7%205.Nge2%20d6%206.O-O%20e6%207.f4%20Nge7%208.g4%20O-O%209.Ng3%20Rb8%2010.d3%20b5%2011.Rb1%20b4%2012.Nce2%20Bb7%2013.f5%20Nc8%2014.Nf4%20exf5%2015.exf5%20Nb6%2016.Ne4%20Ne5%2017.f6%20Bxf6%2018.Nh5%20Bh8%2019.Nhf6%2B%20Bxf6%2020.Nxf6%2B%20Kg7%2021.Qd2%20Nxg4%2022.Qh6%2B%20Nxh6%2023.Bxh6%2B%20Kxh6%2024.Bxb7%20Rxb7%2025.Ng4%2B%20Kg7%2026.Rf6%20Nd5%2027.Rbf1%20Nxf6%2028.Nxf6%20Qxf6%2029.Rxf6%20Kxf6#42) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nc3%20Nc6%203.g3%20g6%204.Bg2%20Bg7%205.Nge2%20d6%206.O-O%20e6%207.f4%20Nge7%208.g4%20O-O%209.Ng3%20Rb8%2010.d3%20b5%2011.Rb1%20b4%2012.Nce2%20Bb7%2013.f5%20Nc8%2014.Nf4%20exf5%2015.exf5%20Nb6%2016.Ne4%20Ne5%2017.f6%20Bxf6%2018.Nh5%20Bh8%2019.Nhf6%2B%20Bxf6%2020.Nxf6%2B%20Kg7%2021.Qd2%20Nxg4%2022.Qh6%2B%20Nxh6%2023.Bxh6%2B%20Kxh6%2024.Ng4%2B%20Kg7%2025.Bxb7%20Rxb7%2026.Nf6%20Nd5%2027.Nxd5%20Qg5%2B%2028.Kh1%20Qxd5%2B%2029.Kg1%20Re7#42) |

position 5 (`r3kbnr/pbpn2pp/1p2q3/1Q2p1B1/4P3/2N2N2/PPP3PP/2KR1B1R b kq - 2 11`), split at ply 4: Bxe7 (56% there) vs Bc4 (44%)

| chosen | subpar |
|---|---|
| 11...c6 12.Qa4 Be7 [13.Bxe7] Nxe7 14.Bc4 Qh6+ 15.Kb1 Nc5 16.Qb4 a5 [17.Qxb6] Nd7 [18.Qxb7] Rd8 [19.Nxe5] | 11...c6 12.Qa4 Be7 13.Bc4 Qg6 [14.Bxe7] Nxe7 [15.Nxe5] Nxe5 16.Rhf1 Nxc4 [17.Qxc4] Qg5+ 18.Kb1 Qxg2 19.Qf7# |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Nf3%20d6%204.Qe2%20Qe7%205.d3%20b6%206.Nc3%20Bb7%207.fxe5%20dxe5%208.Bg5%20Qe6%209.O-O-O%20fxe4%2010.dxe4%20Nd7%2011.Qb5%20c6%2012.Qa4%20Be7%2013.Bxe7%20Nxe7%2014.Bc4%20Qh6%2B%2015.Kb1%20Nc5%2016.Qb4%20a5%2017.Qxb6%20Nd7%2018.Qxb7%20Rd8%2019.Nxe5#21) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Nf3%20d6%204.Qe2%20Qe7%205.d3%20b6%206.Nc3%20Bb7%207.fxe5%20dxe5%208.Bg5%20Qe6%209.O-O-O%20fxe4%2010.dxe4%20Nd7%2011.Qb5%20c6%2012.Qa4%20Be7%2013.Bc4%20Qg6%2014.Bxe7%20Nxe7%2015.Nxe5%20Nxe5%2016.Rhf1%20Nxc4%2017.Qxc4%20Qg5%2B%2018.Kb1%20Qxg2%2019.Qf7%23#21) |

position 31 (`5r2/5k2/p2q1p1r/1pn4p/8/P1N2Q1P/1P3PP1/3RR1K1 b - - 3 25`), split at ply 6: Qxd7+ (48% there) vs Re7+ (44%)

| chosen | subpar |
|---|---|
| 25...Qc7 26.Qd5+ Kg7 27.b4 Nd7 [28.Qxd7+] Qxd7 [29.Rxd7+] Rf7 [30.Rxf7+] Kxf7 31.Nd5 Rg6 32.Re7+ Kf8 33.Ra7 | 25...Qc7 26.Qd5+ Kg7 27.b4 Nd7 28.Re7+ Rf7 [29.Qxf7+] Kh8 30.Qg7# |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.Bb5%20Qc7%204.O-O%20e6%205.Re1%20h5%206.c3%20Nf6%207.d4%20cxd4%208.cxd4%20a6%209.Bf1%20Ng4%2010.h3%20f6%2011.Nc3%20b5%2012.a3%20Bb7%2013.e5%20Nh6%2014.Bxh6%20Rxh6%2015.exf6%20gxf6%2016.d5%20Nd8%2017.Nd4%20Kf7%2018.Be2%20Qe5%2019.Bf3%20Qf4%2020.dxe6%2B%20dxe6%2021.Bxb7%20Nxb7%2022.Nxe6%20Qd6%2023.Nxf8%20Rxf8%2024.Qf3%20Nc5%2025.Rad1%20Qc7%2026.Qd5%2B%20Kg7%2027.b4%20Nd7%2028.Qxd7%2B%20Qxd7%2029.Rxd7%2B%20Rf7%2030.Rxf7%2B%20Kxf7%2031.Nd5%20Rg6%2032.Re7%2B%20Kf8%2033.Ra7#49) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.Bb5%20Qc7%204.O-O%20e6%205.Re1%20h5%206.c3%20Nf6%207.d4%20cxd4%208.cxd4%20a6%209.Bf1%20Ng4%2010.h3%20f6%2011.Nc3%20b5%2012.a3%20Bb7%2013.e5%20Nh6%2014.Bxh6%20Rxh6%2015.exf6%20gxf6%2016.d5%20Nd8%2017.Nd4%20Kf7%2018.Be2%20Qe5%2019.Bf3%20Qf4%2020.dxe6%2B%20dxe6%2021.Bxb7%20Nxb7%2022.Nxe6%20Qd6%2023.Nxf8%20Rxf8%2024.Qf3%20Nc5%2025.Rad1%20Qc7%2026.Qd5%2B%20Kg7%2027.b4%20Nd7%2028.Re7%2B%20Rf7%2029.Qxf7%2B%20Kh8%2030.Qg7%23#49) |

#### W #9 (k = 0): latents 140

position 34 (`r2qk2r/1pp1bppp/2n1p3/1p6/3PR3/P1P2N2/5PPP/R2Q2K1 b kq - 0 14`), split at ply 9: Rxa3 (50% there) vs Na5 (45%)

| chosen | subpar |
|---|---|
| 14...O-O 15.Qb3 Na5 16.Qxb5 c6 17.Qd3 Nb3 18.Rb1 [Rxa3] 19.Ne5 Nc5 20.Qf3 Nxe4 21.Qxe4 [Rxc3] [22.Rxb7] | 14...O-O 15.Qb3 Na5 16.Qxb5 c6 17.Qd3 Nb3 18.Rb1 Na5 19.c4 c5 20.d5 exd5 21.cxd5 Bf6 22.d6 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20O-O%2015.Qb3%20Na5%2016.Qxb5%20c6%2017.Qd3%20Nb3%2018.Rb1%20Rxa3%2019.Ne5%20Nc5%2020.Qf3%20Nxe4%2021.Qxe4%20Rxc3%2022.Rxb7#27) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20O-O%2015.Qb3%20Na5%2016.Qxb5%20c6%2017.Qd3%20Nb3%2018.Rb1%20Na5%2019.c4%20c5%2020.d5%20exd5%2021.cxd5%20Bf6%2022.d6#27) |

position 7 (`2q2rk1/1Q3pp1/p1N1p2p/3p4/8/6P1/3r1P1P/1R3RK1 w - - 3 24`), split at ply 11: Rxd4 (57% there) vs Qd3+ (43%)

| chosen | subpar |
|---|---|
| 24.Ne7+ Kh8 25.Nxc8 [Rxc8] 26.Qxc8+ Kh7 27.Qxa6 d4 28.Rbd1 Rc2 [29.Rxd4] e5 30.Qd3+ g6 31.Qxc2 exd4 | 24.Ne7+ Kh8 25.Nxc8 [Rxc8] 26.Qxc8+ Kh7 27.Qxa6 d4 28.Rbd1 Rc2 29.Qd3+ g6 30.Qxc2 e5 31.Rfe1 f6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.Qf3%20e6%203.Bc4%20Nf6%204.d4%20d5%205.exd5%20cxd5%206.Bb5%2B%20Bd7%207.Bxd7%2B%20Nbxd7%208.Bg5%20Be7%209.Nc3%20h6%2010.Bxf6%20Bxf6%2011.Nge2%20O-O%2012.O-O%20Nb6%2013.Nb5%20Nc4%2014.Qd3%20Nxb2%2015.Qc3%20Nc4%2016.Rab1%20a6%2017.Na3%20Rc8%2018.Nxc4%20Rxc4%2019.Qb3%20Bxd4%2020.Qxb7%20Rxc2%2021.Nxd4%20Rxa2%2022.g3%20Rd2%2023.Nc6%20Qc8%2024.Ne7%2B%20Kh8%2025.Nxc8%20Rxc8%2026.Qxc8%2B%20Kh7%2027.Qxa6%20d4%2028.Rbd1%20Rc2%2029.Rxd4%20e5%2030.Qd3%2B%20g6%2031.Qxc2%20exd4#46) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.Qf3%20e6%203.Bc4%20Nf6%204.d4%20d5%205.exd5%20cxd5%206.Bb5%2B%20Bd7%207.Bxd7%2B%20Nbxd7%208.Bg5%20Be7%209.Nc3%20h6%2010.Bxf6%20Bxf6%2011.Nge2%20O-O%2012.O-O%20Nb6%2013.Nb5%20Nc4%2014.Qd3%20Nxb2%2015.Qc3%20Nc4%2016.Rab1%20a6%2017.Na3%20Rc8%2018.Nxc4%20Rxc4%2019.Qb3%20Bxd4%2020.Qxb7%20Rxc2%2021.Nxd4%20Rxa2%2022.g3%20Rd2%2023.Nc6%20Qc8%2024.Ne7%2B%20Kh8%2025.Nxc8%20Rxc8%2026.Qxc8%2B%20Kh7%2027.Qxa6%20d4%2028.Rbd1%20Rc2%2029.Qd3%2B%20g6%2030.Qxc2%20e5%2031.Rfe1%20f6#46) |

position 16 (`r4rk1/p4p1p/5qp1/8/4nN2/1P2K1P1/P7/2B2B1R b - - 1 26`), split at ply 10: Rxf4 (57% there) vs Bxf4 (43%)

| chosen | subpar |
|---|---|
| 26...Nxg3 27.Rg1 Nxf1+ [28.Rxf1] Rfe8+ 29.Kf3 g5 30.Kg4 gxf4 [31.Rxf4] Qg6+ 32.Kf3 Qd3+ 33.Kg4 [Re4] [34.Rxe4] | 26...Nxg3 27.Rg1 Nxf1+ [28.Rxf1] Rfe8+ 29.Kf3 g5 30.Kg4 gxf4 31.Bxf4 Qg6+ 32.Kf3 Qd3+ 33.Kg4 Qxf1 34.Kf5 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Qh5%20Nf6%203.Qxe5%2B%20Be7%204.Nc3%20Ng4%205.Qf4%20d5%206.Nxd5%20O-O%207.Qxg4%20Bxg4%208.f3%20Bh4%2B%209.g3%20Bxg3%2B%2010.hxg3%20Bh5%2011.Rxh5%20g6%2012.Rh1%20c6%2013.Nc3%20c5%2014.Na4%20c4%2015.b3%20cxb3%2016.cxb3%20Nc6%2017.Nc5%20Nd4%2018.Nxb7%20Qb6%2019.Nd6%20Qxd6%2020.Nh3%20Nxf3%2B%2021.Kf2%20Qf6%2022.Rb1%20Nxd2%2B%2023.Nf4%20Nxb1%2024.Bb5%20Nc3%2025.Bf1%20Nxe4%2B%2026.Ke3%20Nxg3%2027.Rg1%20Nxf1%2B%2028.Rxf1%20Rfe8%2B%2029.Kf3%20g5%2030.Kg4%20gxf4%2031.Rxf4%20Qg6%2B%2032.Kf3%20Qd3%2B%2033.Kg4%20Re4%2034.Rxe4#51) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Qh5%20Nf6%203.Qxe5%2B%20Be7%204.Nc3%20Ng4%205.Qf4%20d5%206.Nxd5%20O-O%207.Qxg4%20Bxg4%208.f3%20Bh4%2B%209.g3%20Bxg3%2B%2010.hxg3%20Bh5%2011.Rxh5%20g6%2012.Rh1%20c6%2013.Nc3%20c5%2014.Na4%20c4%2015.b3%20cxb3%2016.cxb3%20Nc6%2017.Nc5%20Nd4%2018.Nxb7%20Qb6%2019.Nd6%20Qxd6%2020.Nh3%20Nxf3%2B%2021.Kf2%20Qf6%2022.Rb1%20Nxd2%2B%2023.Nf4%20Nxb1%2024.Bb5%20Nc3%2025.Bf1%20Nxe4%2B%2026.Ke3%20Nxg3%2027.Rg1%20Nxf1%2B%2028.Rxf1%20Rfe8%2B%2029.Kf3%20g5%2030.Kg4%20gxf4%2031.Bxf4%20Qg6%2B%2032.Kf3%20Qd3%2B%2033.Kg4%20Qxf1%2034.Kf5#51) |

#### W #10 (k = 0): latents 894

position 2 (`r1bqk2r/p2pbp2/2p1p3/3nP1pp/4N3/P7/1PP2PPP/R1BQKB1R b KQkq - 1 11`), split at ply 7: Qc5 (53% there) vs Qb6 (47%)

| chosen | subpar |
|---|---|
| 11...g4 [12.Nd6+] Bxd6 [13.exd6] [Qa5+] 14.Bd2 [Qc5] [15.Bb4] Nxb4 [16.axb4] Qxb4+ 17.c3 Qxb2 18.Be2 Qxc3+ [19.Kf1] | 11...g4 [12.Nd6+] Bxd6 [13.exd6] [Qa5+] 14.Bd2 Qb6 15.b4 a5 16.c4 Nf6 [17.c5] Qb7 [18.Bc3] Rh6 [19.Qd2] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.a3%20Be7%207.Nxc6%20bxc6%208.e5%20Nd5%209.Qg4%20g5%2010.Ne4%20h5%2011.Qd1%20g4%2012.Nd6%2B%20Bxd6%2013.exd6%20Qa5%2B%2014.Bd2%20Qc5%2015.Bb4%20Nxb4%2016.axb4%20Qxb4%2B%2017.c3%20Qxb2%2018.Be2%20Qxc3%2B%2019.Kf1#21) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.a3%20Be7%207.Nxc6%20bxc6%208.e5%20Nd5%209.Qg4%20g5%2010.Ne4%20h5%2011.Qd1%20g4%2012.Nd6%2B%20Bxd6%2013.exd6%20Qa5%2B%2014.Bd2%20Qb6%2015.b4%20a5%2016.c4%20Nf6%2017.c5%20Qb7%2018.Bc3%20Rh6%2019.Qd2#21) |

position 44 (`6rr/ppkn3p/8/2pQ4/5Bb1/3B3P/PqP5/2R2KNR b - - 0 24`), split at ply 15: Kd5 (54% there) vs Ke3 (46%)

| chosen | subpar |
|---|---|
| 24...Kb6 25.Qd6+ Ka5 26.Qc7+ b6 27.Qxa7+ Kb4 28.Bd2+ Qc3 29.Bxc3+ Kxc3 30.Qa3+ [Kd4] 31.Qb2+ [Kd5] 32.Bc4+ | 24...Kb6 25.Qd6+ Ka5 26.Qc7+ b6 27.Qxa7+ Kb4 28.Bd2+ Qc3 29.Bxc3+ Kxc3 30.Qa3+ [Kd4] 31.Qb2+ Ke3 32.Re1+ |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Bc4%20fxe4%204.d3%20d5%205.Bb3%20exd3%206.Qxd3%20e4%207.Qd4%20Nf6%208.Nc3%20c5%209.Qe5%2B%20Be7%2010.Nxd5%20Nxd5%2011.Bxd5%20Qa5%2B%2012.Bd2%20Qb6%2013.Qxg7%20Bf6%2014.Qf7%2B%20Kd8%2015.Bxe4%20Bg4%2016.Qd5%2B%20Nd7%2017.h3%20Bh4%2B%2018.g3%20Bxg3%2B%2019.Kf1%20Qb5%2B%2020.Bd3%20Qxb2%2021.Qg5%2B%20Kc7%2022.Rc1%20Rag8%2023.Qd5%20Bxf4%2024.Bxf4%2B%20Kb6%2025.Qd6%2B%20Ka5%2026.Qc7%2B%20b6%2027.Qxa7%2B%20Kb4%2028.Bd2%2B%20Qc3%2029.Bxc3%2B%20Kxc3%2030.Qa3%2B%20Kd4%2031.Qb2%2B%20Kd5%2032.Bc4%2B#47) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Bc4%20fxe4%204.d3%20d5%205.Bb3%20exd3%206.Qxd3%20e4%207.Qd4%20Nf6%208.Nc3%20c5%209.Qe5%2B%20Be7%2010.Nxd5%20Nxd5%2011.Bxd5%20Qa5%2B%2012.Bd2%20Qb6%2013.Qxg7%20Bf6%2014.Qf7%2B%20Kd8%2015.Bxe4%20Bg4%2016.Qd5%2B%20Nd7%2017.h3%20Bh4%2B%2018.g3%20Bxg3%2B%2019.Kf1%20Qb5%2B%2020.Bd3%20Qxb2%2021.Qg5%2B%20Kc7%2022.Rc1%20Rag8%2023.Qd5%20Bxf4%2024.Bxf4%2B%20Kb6%2025.Qd6%2B%20Ka5%2026.Qc7%2B%20b6%2027.Qxa7%2B%20Kb4%2028.Bd2%2B%20Qc3%2029.Bxc3%2B%20Kxc3%2030.Qa3%2B%20Kd4%2031.Qb2%2B%20Ke3%2032.Re1%2B#47) |

position 21 (`r1b2rk1/pp2q1pp/3b4/5p1Q/4p3/2N5/PPP2PPP/R1BR2K1 w - - 2 17`), split at ply 13: Rad1 (55% there) vs Rxd8 (45%)

| chosen | subpar |
|---|---|
| [17.Nd5] [Qe5] 18.Bf4 Qe6 [19.Bxd6] Qxd6 20.Nf6+ Qxf6 21.Rd5 Be6 22.Rd6 Rad8 [23.Rad1] Rxd6 24.Rxd6 Qxb2 | [17.Nd5] [Qe5] 18.Bf4 Qe6 [19.Bxd6] Qxd6 20.Nf6+ Qxf6 21.Rd5 Be6 22.Rd6 Rad8 23.Rxd8 [Rxd8] 24.h3 [Qxb2] |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Qxd4%20Nf6%205.e5%20Nfd7%206.exd6%20Nc6%207.Qe3%20e6%208.Nc3%20Bxd6%209.Bd3%20O-O%2010.O-O%20Nde5%2011.Nxe5%20Nxe5%2012.Be4%20f5%2013.Bf3%20Nxf3%2B%2014.Qxf3%20e5%2015.Rd1%20e4%2016.Qh5%20Qe7%2017.Nd5%20Qe5%2018.Bf4%20Qe6%2019.Bxd6%20Qxd6%2020.Nf6%2B%20Qxf6%2021.Rd5%20Be6%2022.Rd6%20Rad8%2023.Rad1%20Rxd6%2024.Rxd6%20Qxb2#32) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Qxd4%20Nf6%205.e5%20Nfd7%206.exd6%20Nc6%207.Qe3%20e6%208.Nc3%20Bxd6%209.Bd3%20O-O%2010.O-O%20Nde5%2011.Nxe5%20Nxe5%2012.Be4%20f5%2013.Bf3%20Nxf3%2B%2014.Qxf3%20e5%2015.Rd1%20e4%2016.Qh5%20Qe7%2017.Nd5%20Qe5%2018.Bf4%20Qe6%2019.Bxd6%20Qxd6%2020.Nf6%2B%20Qxf6%2021.Rd5%20Be6%2022.Rd6%20Rad8%2023.Rxd8%20Rxd8%2024.h3%20Qxb2#32) |

