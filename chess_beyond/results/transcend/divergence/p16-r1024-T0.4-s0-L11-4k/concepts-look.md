## S against W: how often each concept fires

Per position, the share of rollout plies where v . z >= 0.5 (lines weighted by how often they were sampled), each model's own rollouts from the same 50 positions; mean over positions. S - W: 95% bootstrap interval over positions.

| concept | with / pairs | S own mu | W own mu | S - W (own mu), 95% | positions S > W | S, S's mu | W, S's mu | S - W (S's mu), 95% | continuous S / W | S - W continuous, 95% |
|---|---|---|---|---|---|---|---|---|---|---|
| k = 4: a = 262 (0.50) + b = 1193 (0.50) | 19 / 2500 | 18.97% | 15.85% | 3.12% [0.51%, 6.07%] | 28 of 50 | 18.97% | 15.71% | 3.26% [0.88%, 6.04%] | 0.111 / 0.088 | 0.023 [0.008, 0.041] |
| k = 4: a = 1109 (0.50) + b = 1230 (0.50) | 8 / 2500 | 10.60% | 13.13% | -2.54% [-5.45%, -0.07%] | 24 of 50 | 10.60% | 13.14% | -2.54% [-5.32%, -0.26%] | 0.064 / 0.078 | -0.014 [-0.032, -0.000] |
| k = 6: a = 603 (0.50) + b = 1752 (0.50) | 20 / 2500 | 16.32% | 15.19% | 1.13% [-1.84%, 4.34%] | 23 of 50 | 16.32% | 15.14% | 1.18% [-1.83%, 4.37%] | 0.124 / 0.121 | 0.003 [-0.019, 0.026] |
| k = 6: a = 923 (0.50) + b = 1122 (0.50) | 16 / 2500 | 17.99% | 19.37% | -1.38% [-4.58%, 1.57%] | 23 of 50 | 17.99% | 19.53% | -1.53% [-4.79%, 1.53%] | 0.114 / 0.122 | -0.009 [-0.029, 0.011] |
| k = 6: a = 2247 (0.50) + b = 3874 (0.50) | 21 / 2500 | 14.85% | 13.77% | 1.07% [-1.31%, 3.94%] | 24 of 50 | 14.85% | 13.59% | 1.26% [-1.10%, 4.02%] | 0.114 / 0.100 | 0.014 [-0.004, 0.035] |
| k = 6: a = 416 (0.50) + b = 1455 (0.50) | 21 / 2500 | 17.20% | 18.96% | -1.76% [-6.13%, 2.11%] | 26 of 50 | 17.20% | 18.95% | -1.75% [-5.76%, 2.11%] | 0.104 / 0.112 | -0.008 [-0.032, 0.015] |

# The candidate concepts: with, without, and S against W

Run p16-r1024-T0.4-s0-L11-4k, S's pairs. With: pairs where v . (z^chosen - z^subpar) >= 0.5 on every ply of the window t..t+k. Without: a pair at the same position and k where it does not hold, nearest in split ply. [move]ab: the concept's latents on after that move (a: its first latent, b: its second, as listed in the heading); ply 1 is the line's first move. With weights 0.5 / 0.5, v . z >= 0.5 when either is on, so 'fires' below counts either.

## k = 4: a = 262 (0.50) + b = 1193 (0.50)

Holds at 19 of 2500 pairs (0.8%), at 12 positions; recurrence in the report 1.0% (null 95th 0.1%).

Board scan (every ply of the rollouts, lines weighted by count): each latent's phi correlation with each piece on a square and with White to move after the move; 'on X% of plies with it' is the latent's rate given the piece is there.

- a: on at 9.7% of plies; phi with White to move -0.10; top: Black P on b5 +0.54 (on 51% of plies with it, 3% without), White P on b4 +0.41 (on 54% of plies with it, 6% without), Black R on h6 +0.22 (on 63% of plies with it, 9% without), Black P on a6 +0.21 (on 19% of plies with it, 6% without)
- b: on at 9.9% of plies; phi with White to move +0.10; top: Black P on b5 +0.54 (on 51% of plies with it, 4% without), White P on b4 +0.40 (on 53% of plies with it, 7% without), Black R on h6 +0.22 (on 63% of plies with it, 9% without), White P on a3 +0.18 (on 21% of plies with it, 7% without)
- either: on at 19.0% of plies; phi with White to move +0.00; top: Black P on b5 +0.78 (on 98% of plies with it, 7% without), White P on b4 +0.55 (on 98% of plies with it, 13% without), Black P on a6 +0.27 (on 35% of plies with it, 12% without), Black B on a7 +0.26 (on 93% of plies with it, 18% without)

### k = 4: a = 262 (0.50) + b = 1193 (0.50): position 41, pair 1

**with**: split at ply 11, Black to move: chosen **Ra6** (49% there) vs subpar **b4** (47%). `r1q1k2r/4b3/6p1/pp1QPp1p/7P/2P3N1/PP1B4/2KR3R b kq - 0 23`

```
r . q . k . . r
. . . . b . . .
. . . . . . p .
p p . Q P p . p
. . . . . . . P
. . P . . . N .
P P . B . . . .
. . K R . . . R
```

| chosen | subpar |
|---|---|
| [18...Ne6]b [19.Bd2]a [a5]b [20.d5]a [Nc5]b [21.Qc2]a [Nxd3+]b [22.Qxd3]a [cxd5]b [23.Qxd5]a [Ra6]b [24.Bg5]a [Bxg5+]b [25.hxg5]a [h4]b [26.Ne2]a | [18...Ne6]b [19.Bd2]a [a5]b [20.d5]a [Nc5]b [21.Qc2]a [Nxd3+]b [22.Qxd3]a [cxd5]b [23.Qxd5]a b4 24.Kb1 bxc3 25.Bxc3 Ra6 26.e6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.Nc3%20dxe4%204.Nxe4%20Bf5%205.f3%20Nf6%206.Bd3%20e6%207.Ne2%20Nbd7%208.Bf4%20Be7%209.g4%20Bxe4%2010.fxe4%20Nxg4%2011.Ng3%20f6%2012.Qxg4%20g6%2013.Qxe6%20Nf8%2014.Qb3%20b5%2015.c3%20Qc8%2016.e5%20f5%2017.h4%20h5%2018.O-O-O%20Ne6%2019.Bd2%20a5%2020.d5%20Nc5%2021.Qc2%20Nxd3%2B%2022.Qxd3%20cxd5%2023.Qxd5%20Ra6%2024.Bg5%20Bxg5%2B%2025.hxg5%20h4%2026.Ne2#35) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.Nc3%20dxe4%204.Nxe4%20Bf5%205.f3%20Nf6%206.Bd3%20e6%207.Ne2%20Nbd7%208.Bf4%20Be7%209.g4%20Bxe4%2010.fxe4%20Nxg4%2011.Ng3%20f6%2012.Qxg4%20g6%2013.Qxe6%20Nf8%2014.Qb3%20b5%2015.c3%20Qc8%2016.e5%20f5%2017.h4%20h5%2018.O-O-O%20Ne6%2019.Bd2%20a5%2020.d5%20Nc5%2021.Qc2%20Nxd3%2B%2022.Qxd3%20cxd5%2023.Qxd5%20b4%2024.Kb1%20bxc3%2025.Bxc3%20Ra6%2026.e6#35) |

**without**: split at ply 11, Black to move: chosen **Kb7** (50% there) vs subpar **Nd7** (33%). `2kr1n1r/8/2p1q1p1/1p2PpPp/p2P4/2PB4/PPQ1N3/1K1R3R b - - 2 23`

```
. . k r . n . r
. . . . . . . .
. . p . q . p .
. p . . P p P p
p . . P . . . .
. . P B . . . .
P P Q . N . . .
. K . R . . . R
```

| chosen | subpar |
|---|---|
| [18...a5]b [19.Kb1]a [a4]b [20.Qc2]a [Qe6]b [21.Bg5]a [Bxg5]b [22.hxg5]a [O-O-O]b [23.Ne2]a [Kb7]b [24.Nf4]a [Qe7]b [25.Rhe1]a [Ne6]b [26.Nxe6]a | [18...a5]b [19.Kb1]a [a4]b [20.Qc2]a [Qe6]b [21.Bg5]a [Bxg5]b [22.hxg5]a [O-O-O]b [23.Ne2]a [Nd7]b [24.Nf4]a [Qe7]b [25.Nxg6]a [Qxg5]b [26.Nxh8]a |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.Nc3%20dxe4%204.Nxe4%20Bf5%205.f3%20Nf6%206.Bd3%20e6%207.Ne2%20Nbd7%208.Bf4%20Be7%209.g4%20Bxe4%2010.fxe4%20Nxg4%2011.Ng3%20f6%2012.Qxg4%20g6%2013.Qxe6%20Nf8%2014.Qb3%20b5%2015.c3%20Qc8%2016.e5%20f5%2017.h4%20h5%2018.O-O-O%20a5%2019.Kb1%20a4%2020.Qc2%20Qe6%2021.Bg5%20Bxg5%2022.hxg5%20O-O-O%2023.Ne2%20Kb7%2024.Nf4%20Qe7%2025.Rhe1%20Ne6%2026.Nxe6#35) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.Nc3%20dxe4%204.Nxe4%20Bf5%205.f3%20Nf6%206.Bd3%20e6%207.Ne2%20Nbd7%208.Bf4%20Be7%209.g4%20Bxe4%2010.fxe4%20Nxg4%2011.Ng3%20f6%2012.Qxg4%20g6%2013.Qxe6%20Nf8%2014.Qb3%20b5%2015.c3%20Qc8%2016.e5%20f5%2017.h4%20h5%2018.O-O-O%20a5%2019.Kb1%20a4%2020.Qc2%20Qe6%2021.Bg5%20Bxg5%2022.hxg5%20O-O-O%2023.Ne2%20Nd7%2024.Nf4%20Qe7%2025.Nxg6%20Qxg5%2026.Nxh8#35) |

### k = 4: a = 262 (0.50) + b = 1193 (0.50): position 25, pair 2

**with**: split at ply 8, Black to move: chosen **b5** (57% there) vs subpar **g5** (43%). `5r2/p3r1kp/1p4p1/2p1P3/2N2n2/2P4P/PP4PK/3R1R2 b - - 3 24`

```
. . . . . r . .
p . . . r . k p
. p . . . . p .
. . p . P . . .
. . N . . n . .
. . P . . . . P
P P . . . . P K
. . . R . R . .
```

| chosen | subpar |
|---|---|
| 21.Nc4 Nf4 22.Bxb7 Rxb7 23.Rad1 Re7 24.Kh2 [b5]b [25.Nd6]a [a6]b [26.g3]a [Ne6]b [27.Rxf8]a [Kxf8]b [28.Kg2]a [Rd7]b | 21.Nc4 Nf4 22.Bxb7 Rxb7 23.Rad1 Re7 24.Kh2 g5 25.g3 Ng6 26.Rxf8 Kxf8 27.Rd8+ Kg7 28.Rd5 Kf7 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.Nc4%20Nf4%2022.Bxb7%20Rxb7%2023.Rad1%20Re7%2024.Kh2%20b5%2025.Nd6%20a6%2026.g3%20Ne6%2027.Rxf8%20Kxf8%2028.Kg2%20Rd7#40) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.Nc4%20Nf4%2022.Bxb7%20Rxb7%2023.Rad1%20Re7%2024.Kh2%20g5%2025.g3%20Ng6%2026.Rxf8%20Kxf8%2027.Rd8%2B%20Kg7%2028.Rd5%20Kf7#40) |

**without**: split at ply 8, Black to move: chosen **Bxc4** (58% there) vs subpar **Rd8** (42%). `1r6/p5kp/bp4p1/2pBP3/2N5/2P4P/PP4P1/5RK1 b - - 0 24`

```
. r . . . . . .
p . . . . . k p
b p . . . . p .
. . p B P . . .
. . N . . . . .
. . P . . . . P
P P . . . . P .
. . . . . R K .
```

| chosen | subpar |
|---|---|
| 21.Rxf8 Kxf8 22.Rf1+ Kg7 23.Nc4 Ba6 24.Bxd5 Bxc4 25.Bxc4 Re8 26.Rf7+ Kh6 27.e6 Kg5 28.e7 h5 | 21.Rxf8 Kxf8 22.Rf1+ Kg7 23.Nc4 Ba6 24.Bxd5 Rd8 25.Rf7+ Kh6 26.Rxa7 Rxd5 27.Rxa6 [b5]b [28.Nd6]a [Rxe5]b |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.Rxf8%20Kxf8%2022.Rf1%2B%20Kg7%2023.Nc4%20Ba6%2024.Bxd5%20Bxc4%2025.Bxc4%20Re8%2026.Rf7%2B%20Kh6%2027.e6%20Kg5%2028.e7%20h5#40) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.Rxf8%20Kxf8%2022.Rf1%2B%20Kg7%2023.Nc4%20Ba6%2024.Bxd5%20Rd8%2025.Rf7%2B%20Kh6%2026.Rxa7%20Rxd5%2027.Rxa6%20b5%2028.Nd6%20Rxe5#40) |

### k = 4: a = 262 (0.50) + b = 1193 (0.50): position 17, pair 3

**with**: split at ply 6, Black to move: chosen **b5** (44% there) vs subpar **Nd5** (42%). `r4rk1/pp2qp1p/2n2np1/2p5/2N3PP/2bPBP2/P1P2K2/3Q1B1R b - - 0 16`

```
r . . . . r k .
p p . . q p . p
. . n . . n p .
. . p . . . . .
. . N . . . P P
. . b P B P . .
P . P . . K . .
. . . Q . B . R
```

| chosen | subpar |
|---|---|
| 14.Kf2 Bxc4 15.Nxc4 O-O 16.h4 [b5]b [17.Na3]a [a6]b [18.h5]a [Nd5]b [19.Bh6]a [Rfe8]b [20.hxg6]a [fxg6]b [21.Nb1]a [Bd4+]b | 14.Kf2 Bxc4 15.Nxc4 O-O 16.h4 Nd5 17.Bh6 Bd4+ 18.Kg2 Rfe8 19.h5 [b5]b [20.Nd2]a Ne3+ [21.Bxe3]a [Qxe3]b |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.d3%20g6%203.Nf3%20Bg7%204.e5%20Nc6%205.Bf4%20d6%206.exd6%20Bxb2%207.dxe7%20Qxe7%2B%208.Be3%20Bxa1%209.Na3%20Bc3%2B%2010.Nd2%20Nf6%2011.Nc4%20Bg4%2012.f3%20Bf5%2013.g4%20Be6%2014.Kf2%20Bxc4%2015.Nxc4%20O-O%2016.h4%20b5%2017.Na3%20a6%2018.h5%20Nd5%2019.Bh6%20Rfe8%2020.hxg6%20fxg6%2021.Nb1%20Bd4%2B#26) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.d3%20g6%203.Nf3%20Bg7%204.e5%20Nc6%205.Bf4%20d6%206.exd6%20Bxb2%207.dxe7%20Qxe7%2B%208.Be3%20Bxa1%209.Na3%20Bc3%2B%2010.Nd2%20Nf6%2011.Nc4%20Bg4%2012.f3%20Bf5%2013.g4%20Be6%2014.Kf2%20Bxc4%2015.Nxc4%20O-O%2016.h4%20Nd5%2017.Bh6%20Bd4%2B%2018.Kg2%20Rfe8%2019.h5%20b5%2020.Nd2%20Ne3%2B%2021.Bxe3%20Qxe3#26) |

**without**: split at ply 6, Black to move: chosen **Kd7** (55% there) vs subpar **Kf8** (45%). `r3k2r/pp2qp1p/2nNb1p1/2pn4/3bN1P1/3PBP2/P1P2K1P/3Q1B1R b kq - 6 16`

```
r . . . k . . r
p p . . q p . p
. . n N b . p .
. . p n . . . .
. . . b N . P .
. . . P B P . .
P . P . . K . P
. . . Q . B . R
```

| chosen | subpar |
|---|---|
| 14.Kf2 Nd5 15.Ne4 Bd4 16.Ncd6+ Kd7 17.Bxd4 Nxd4 18.c3 Nc6 19.Nxb7 Nxc3 20.Nbxc5+ Kc7 21.Qc2 Nxe4+ | 14.Kf2 Nd5 15.Ne4 Bd4 16.Ncd6+ Kf8 17.Bxd4 cxd4 18.h4 Ne3 19.Qd2 f5 20.gxf5 gxf5 21.Ng3 Qxd6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.d3%20g6%203.Nf3%20Bg7%204.e5%20Nc6%205.Bf4%20d6%206.exd6%20Bxb2%207.dxe7%20Qxe7%2B%208.Be3%20Bxa1%209.Na3%20Bc3%2B%2010.Nd2%20Nf6%2011.Nc4%20Bg4%2012.f3%20Bf5%2013.g4%20Be6%2014.Kf2%20Nd5%2015.Ne4%20Bd4%2016.Ncd6%2B%20Kd7%2017.Bxd4%20Nxd4%2018.c3%20Nc6%2019.Nxb7%20Nxc3%2020.Nbxc5%2B%20Kc7%2021.Qc2%20Nxe4%2B#26) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.d3%20g6%203.Nf3%20Bg7%204.e5%20Nc6%205.Bf4%20d6%206.exd6%20Bxb2%207.dxe7%20Qxe7%2B%208.Be3%20Bxa1%209.Na3%20Bc3%2B%2010.Nd2%20Nf6%2011.Nc4%20Bg4%2012.f3%20Bf5%2013.g4%20Be6%2014.Kf2%20Nd5%2015.Ne4%20Bd4%2016.Ncd6%2B%20Kf8%2017.Bxd4%20cxd4%2018.h4%20Ne3%2019.Qd2%20f5%2020.gxf5%20gxf5%2021.Ng3%20Qxd6#26) |

### k = 4: a = 262 (0.50) + b = 1193 (0.50): position 6, pair 4

**with**: split at ply 11, Black to move: chosen **b5** (60% there) vs subpar **Rad8** (40%). `r4rk1/1p2q1pp/2p1bp2/p1p5/P2nP3/1P1PN2P/2PN1RP1/R2Q2K1 b - - 2 19`

```
r . . . . r k .
. p . . q . p p
. . p . b p . .
p . p . . . . .
P . . n P . . .
. P . P N . . P
. . P N . R P .
R . . Q . . K .
```

| chosen | subpar |
|---|---|
| 14...c5 15.Ne3 c6 16.Nd2 Nd4 17.f4 exf4 18.Rxf4 Be6 19.Rf2 [b5]b [20.Nf3]a [Nxf3+]b [21.Qxf3]a [Qd7]b [22.g4]a | 14...c5 15.Ne3 c6 16.Nd2 Nd4 17.f4 exf4 18.Rxf4 Be6 19.Rf2 Rad8 20.Qh5 g6 21.Qh6 Qg7 22.Qxg7+ |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20a6%204.Ba4%20Nf6%205.Bxc6%20dxc6%206.d3%20Nd7%207.O-O%20Bc5%208.Be3%20Qe7%209.Bxc5%20Nxc5%2010.Nbd2%20O-O%2011.a4%20a5%2012.b3%20f6%2013.h3%20Ne6%2014.Nc4%20c5%2015.Ne3%20c6%2016.Nd2%20Nd4%2017.f4%20exf4%2018.Rxf4%20Be6%2019.Rf2%20b5%2020.Nf3%20Nxf3%2B%2021.Qxf3%20Qd7%2022.g4#27) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20a6%204.Ba4%20Nf6%205.Bxc6%20dxc6%206.d3%20Nd7%207.O-O%20Bc5%208.Be3%20Qe7%209.Bxc5%20Nxc5%2010.Nbd2%20O-O%2011.a4%20a5%2012.b3%20f6%2013.h3%20Ne6%2014.Nc4%20c5%2015.Ne3%20c6%2016.Nd2%20Nd4%2017.f4%20exf4%2018.Rxf4%20Be6%2019.Rf2%20Rad8%2020.Qh5%20g6%2021.Qh6%20Qg7%2022.Qxg7%2B#27) |

**without**: split at ply 11, Black to move: chosen **g5** (57% there) vs subpar **Ne6** (43%). `r1b2rk1/1pq4p/2p2pp1/p1p1p3/P3Pn2/1P1P1N1P/2PQNPP1/R4RK1 b - - 3 19`

```
r . b . . r k .
. p q . . . . p
. . p . . p p .
p . p . p . . .
P . . . P n . .
. P . P . N . P
. . P Q N P P .
R . . . . R K .
```

| chosen | subpar |
|---|---|
| 14...c5 15.Ne3 c6 16.Nf5 Qc7 17.Qd2 g6 18.Ng3 Nf4 19.Ne2 g5 20.Nxf4 gxf4 21.Kh2 Kh8 22.g3 | 14...c5 15.Ne3 c6 16.Nf5 Qc7 17.Qd2 g6 18.Ng3 Nf4 19.Ne2 Ne6 20.Nh2 b6 21.f4 exf4 22.Nxf4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20a6%204.Ba4%20Nf6%205.Bxc6%20dxc6%206.d3%20Nd7%207.O-O%20Bc5%208.Be3%20Qe7%209.Bxc5%20Nxc5%2010.Nbd2%20O-O%2011.a4%20a5%2012.b3%20f6%2013.h3%20Ne6%2014.Nc4%20c5%2015.Ne3%20c6%2016.Nf5%20Qc7%2017.Qd2%20g6%2018.Ng3%20Nf4%2019.Ne2%20g5%2020.Nxf4%20gxf4%2021.Kh2%20Kh8%2022.g3#27) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20a6%204.Ba4%20Nf6%205.Bxc6%20dxc6%206.d3%20Nd7%207.O-O%20Bc5%208.Be3%20Qe7%209.Bxc5%20Nxc5%2010.Nbd2%20O-O%2011.a4%20a5%2012.b3%20f6%2013.h3%20Ne6%2014.Nc4%20c5%2015.Ne3%20c6%2016.Nf5%20Qc7%2017.Qd2%20g6%2018.Ng3%20Nf4%2019.Ne2%20Ne6%2020.Nh2%20b6%2021.f4%20exf4%2022.Nxf4#27) |

### k = 4: a = 262 (0.50) + b = 1193 (0.50): position 14, pair 5

**with**: split at ply 4, Black to move: chosen **Nf4** (60% there) vs subpar **b4** (40%). `2r1k2r/1bqpbpp1/p6p/1p2p1Pn/4P1BP/2N1BP2/PPPQ4/2KR3R b k - 1 16`

```
. . r . k . . r
. b q p b p p .
p . . . . . . p
. p . . p . P n
. . . . P . B P
. . N . B P . .
P P P Q . . . .
. . K R . . . R
```

| chosen | subpar |
|---|---|
| [15.Bxd4]a [e5]b [16.Be3]a [Nf4]b [17.Bxf4]a [exf4]b [18.gxh6]a [Rxh6]b [19.h5]a b4 20.Nd5 Bxd5 21.exd5 Qc4 22.Kb1 Bf6 | [15.Bxd4]a [e5]b [16.Be3]a b4 17.Nd5 Bxd5 18.Qxd5 Qxc2# |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Bxd4%20e5%2016.Be3%20Nf4%2017.Bxf4%20exf4%2018.gxh6%20Rxh6%2019.h5%20b4%2020.Nd5%20Bxd5%2021.exd5%20Qc4%2022.Kb1%20Bf6#28) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Bxd4%20e5%2016.Be3%20b4%2017.Nd5%20Bxd5%2018.Qxd5%20Qxc2%23#28) |

**without**: split at ply 4, Black to move: chosen **Rg8** (61% there) vs subpar **Nxh1** (35%). `2r1k2r/1bqpbpB1/p3p2p/1p4P1/4P1BP/2N2Pn1/PPPQ4/2KR3R b k - 0 16`

```
. . r . k . . r
. b q p b p B .
p . . . p . . p
. p . . . . P .
. . . . P . B P
. . N . . P n .
P P P Q . . . .
. . K R . . . R
```

| chosen | subpar |
|---|---|
| [15.Bxd4]a [Ng3]b [16.Bxg7]a [Rg8]b [17.Bxh6]a [Nxh1]b [18.Rxh1]a b4 19.Ne2 a5 20.Kb1 a4 21.Rc1 a3 22.b3 Qe5 | [15.Bxd4]a [Ng3]b [16.Bxg7]a [Nxh1]b [17.Bxh8]a [Nf2]b [18.Rf1]a b4 19.Bd4 Nxg4 20.fxg4 bxc3 21.Bxc3 Bxe4 22.gxh6 Qg3 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Bxd4%20Ng3%2016.Bxg7%20Rg8%2017.Bxh6%20Nxh1%2018.Rxh1%20b4%2019.Ne2%20a5%2020.Kb1%20a4%2021.Rc1%20a3%2022.b3%20Qe5#28) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Bxd4%20Ng3%2016.Bxg7%20Nxh1%2017.Bxh8%20Nf2%2018.Rf1%20b4%2019.Bd4%20Nxg4%2020.fxg4%20bxc3%2021.Bxc3%20Bxe4%2022.gxh6%20Qg3#28) |

### k = 4: a = 262 (0.50) + b = 1193 (0.50): position 31, pair 6

**with**: split at ply 10, White to move: chosen **b4** (60% there) vs subpar **Nf4** (40%). `8/5qk1/p4p1r/1pnN1Q1p/8/P6P/1P3PP1/3R2K1 w - - 0 30`

```
. . . . . . . .
. . . . . q k .
p . . . . p . r
. p n N . Q . p
. . . . . . . .
P . . . . . . P
. P . . . P P .
. . . R . . K .
```

| chosen | subpar |
|---|---|
| [25...Qc7]b [26.Nd5]a [Qb7]b [27.Qf5]a [Kg7]b 28.Re7+ [Rf7]b [29.Rxf7+]a [Qxf7]b [30.b4]ab [Ne6]ab [31.Nf4]ab [Nxf4]ab [32.Qxf4]ab [Rg6]ab [33.Rd6]ab | [25...Qc7]b [26.Nd5]a [Qb7]b [27.Qf5]a [Kg7]b 28.Re7+ [Rf7]b [29.Rxf7+]a [Qxf7]b [30.Nf4]a [Nb3]b [31.Rd7]a [Nc5]b [32.Rxf7+]a [Kxf7]b [33.Qxc5]a |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.Bb5%20Qc7%204.O-O%20e6%205.Re1%20h5%206.c3%20Nf6%207.d4%20cxd4%208.cxd4%20a6%209.Bf1%20Ng4%2010.h3%20f6%2011.Nc3%20b5%2012.a3%20Bb7%2013.e5%20Nh6%2014.Bxh6%20Rxh6%2015.exf6%20gxf6%2016.d5%20Nd8%2017.Nd4%20Kf7%2018.Be2%20Qe5%2019.Bf3%20Qf4%2020.dxe6%2B%20dxe6%2021.Bxb7%20Nxb7%2022.Nxe6%20Qd6%2023.Nxf8%20Rxf8%2024.Qf3%20Nc5%2025.Rad1%20Qc7%2026.Nd5%20Qb7%2027.Qf5%20Kg7%2028.Re7%2B%20Rf7%2029.Rxf7%2B%20Qxf7%2030.b4%20Ne6%2031.Nf4%20Nxf4%2032.Qxf4%20Rg6%2033.Rd6#49) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.Bb5%20Qc7%204.O-O%20e6%205.Re1%20h5%206.c3%20Nf6%207.d4%20cxd4%208.cxd4%20a6%209.Bf1%20Ng4%2010.h3%20f6%2011.Nc3%20b5%2012.a3%20Bb7%2013.e5%20Nh6%2014.Bxh6%20Rxh6%2015.exf6%20gxf6%2016.d5%20Nd8%2017.Nd4%20Kf7%2018.Be2%20Qe5%2019.Bf3%20Qf4%2020.dxe6%2B%20dxe6%2021.Bxb7%20Nxb7%2022.Nxe6%20Qd6%2023.Nxf8%20Rxf8%2024.Qf3%20Nc5%2025.Rad1%20Qc7%2026.Nd5%20Qb7%2027.Qf5%20Kg7%2028.Re7%2B%20Rf7%2029.Rxf7%2B%20Qxf7%2030.Nf4%20Nb3%2031.Rd7%20Nc5%2032.Rxf7%2B%20Kxf7%2033.Qxc5#49) |

**without**: split at ply 10, White to move: chosen **Qxe6+** (62% there) vs subpar **Nf4** (38%). `5r2/5k2/p3qp1r/1p1N1Q1p/1P6/P6P/5PP1/3R2K1 w - - 0 30`

```
. . . . . r . .
. . . . . k . .
p . . . q p . r
. p . N . Q . p
. P . . . . . .
P . . . . . . P
. . . . . P P .
. . . R . . K .
```

| chosen | subpar |
|---|---|
| [25...Qc7]b [26.Nd5]a [Qb7]b [27.b4]ab [Ne6]ab [28.Qf5]ab [Qc6]ab [29.Rxe6]ab [Qxe6]ab [30.Qxe6+]a [Kxe6]ab [31.Nf4+]ab [Kf5]ab [32.Nd3]ab [Rh7]ab [33.Nc5]ab | [25...Qc7]b [26.Nd5]a [Qb7]b [27.b4]ab [Ne6]ab [28.Qf5]ab [Qc6]ab [29.Rxe6]ab [Qxe6]ab [30.Nf4]ab [Qe5]ab [31.Rd7+]a [Ke8]ab [32.Qc2]ab [Qxf4]ab [33.Qc6]ab |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.Bb5%20Qc7%204.O-O%20e6%205.Re1%20h5%206.c3%20Nf6%207.d4%20cxd4%208.cxd4%20a6%209.Bf1%20Ng4%2010.h3%20f6%2011.Nc3%20b5%2012.a3%20Bb7%2013.e5%20Nh6%2014.Bxh6%20Rxh6%2015.exf6%20gxf6%2016.d5%20Nd8%2017.Nd4%20Kf7%2018.Be2%20Qe5%2019.Bf3%20Qf4%2020.dxe6%2B%20dxe6%2021.Bxb7%20Nxb7%2022.Nxe6%20Qd6%2023.Nxf8%20Rxf8%2024.Qf3%20Nc5%2025.Rad1%20Qc7%2026.Nd5%20Qb7%2027.b4%20Ne6%2028.Qf5%20Qc6%2029.Rxe6%20Qxe6%2030.Qxe6%2B%20Kxe6%2031.Nf4%2B%20Kf5%2032.Nd3%20Rh7%2033.Nc5#49) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.Bb5%20Qc7%204.O-O%20e6%205.Re1%20h5%206.c3%20Nf6%207.d4%20cxd4%208.cxd4%20a6%209.Bf1%20Ng4%2010.h3%20f6%2011.Nc3%20b5%2012.a3%20Bb7%2013.e5%20Nh6%2014.Bxh6%20Rxh6%2015.exf6%20gxf6%2016.d5%20Nd8%2017.Nd4%20Kf7%2018.Be2%20Qe5%2019.Bf3%20Qf4%2020.dxe6%2B%20dxe6%2021.Bxb7%20Nxb7%2022.Nxe6%20Qd6%2023.Nxf8%20Rxf8%2024.Qf3%20Nc5%2025.Rad1%20Qc7%2026.Nd5%20Qb7%2027.b4%20Ne6%2028.Qf5%20Qc6%2029.Rxe6%20Qxe6%2030.Nf4%20Qe5%2031.Rd7%2B%20Ke8%2032.Qc2%20Qxf4%2033.Qc6#49) |

## k = 4: a = 1109 (0.50) + b = 1230 (0.50)

Holds at 8 of 2500 pairs (0.3%), at 5 positions; recurrence in the report 0.5% (null 95th 0.1%).

Board scan (every ply of the rollouts, lines weighted by count): each latent's phi correlation with each piece on a square and with White to move after the move; 'on X% of plies with it' is the latent's rate given the piece is there.

- a: on at 5.1% of plies; phi with White to move -0.04; top: White K on g2 +0.52 (on 49% of plies with it, 2% without), Black K on g7 +0.43 (on 49% of plies with it, 3% without), Black R on d7 +0.20 (on 36% of plies with it, 4% without), Black P on g4 +0.19 (on 29% of plies with it, 4% without)
- b: on at 5.8% of plies; phi with White to move +0.04; top: White K on g2 +0.52 (on 52% of plies with it, 3% without), Black K on g7 +0.44 (on 53% of plies with it, 4% without), Black P on g4 +0.20 (on 31% of plies with it, 5% without), White N on b5 +0.19 (on 40% of plies with it, 5% without)
- either: on at 10.6% of plies; phi with White to move +0.00; top: White K on g2 +0.73 (on 97% of plies with it, 5% without), Black K on g7 +0.61 (on 97% of plies with it, 7% without), Black R on d7 +0.27 (on 67% of plies with it, 9% without), Black P on g4 +0.27 (on 57% of plies with it, 9% without)

### k = 4: a = 1109 (0.50) + b = 1230 (0.50): position 28, pair 1

**with**: split at ply 8, Black to move: chosen **Kg7** (53% there) vs subpar **Ke7** (47%). `3R1k2/2r2p1p/R1p1p1p1/2P1N3/5n2/7P/1P3PP1/6K1 b - - 0 30`

```
. . . R . k . .
. . r . . p . p
R . p . p . p .
. . P . N . . .
. . . . . n . .
. . . . . . . P
. P . . . P P .
. . . . . . K .
```

| chosen | subpar |
|---|---|
| 27.Ne5 Rc7 28.Rxa6 Qf4 29.Qxf4 Nxf4 30.Rxd8+ [Kg7]a [31.Rxc6]b [Rb7]a [32.Rb6]b [Rc7]a [33.b4]b [Nd5]a [34.Rbb8]b Kf6 | 27.Ne5 Rc7 28.Rxa6 Qf4 29.Qxf4 Nxf4 30.Rxd8+ Ke7 31.Rxc6 Ra7 32.Rcd6 Ra1+ 33.Kh2 Re1 34.Nc6+ Kf6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20g6%202.d4%20Bg7%203.c3%20d5%204.e5%20c5%205.Nf3%20Nc6%206.Bb5%20Qb6%207.a4%20a6%208.Bxc6%2B%20bxc6%209.a5%20Qb5%2010.Na3%20Qxa5%2011.O-O%20Qc7%2012.Bf4%20Bg4%2013.h3%20Bxf3%2014.Qxf3%20e6%2015.c4%20Ne7%2016.dxc5%20Bxe5%2017.Bxe5%20Qxe5%2018.cxd5%20Qxd5%2019.Qf6%20Rf8%2020.Rfd1%20Qf5%2021.Qd4%20Nd5%2022.Nc4%20Ke7%2023.Nb6%20Ra7%2024.Qh4%2B%20Qf6%2025.Qg3%20Rd8%2026.Nc4%20Kf8%2027.Ne5%20Rc7%2028.Rxa6%20Qf4%2029.Qxf4%20Nxf4%2030.Rxd8%2B%20Kg7%2031.Rxc6%20Rb7%2032.Rb6%20Rc7%2033.b4%20Nd5%2034.Rbb8%20Kf6#52) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20g6%202.d4%20Bg7%203.c3%20d5%204.e5%20c5%205.Nf3%20Nc6%206.Bb5%20Qb6%207.a4%20a6%208.Bxc6%2B%20bxc6%209.a5%20Qb5%2010.Na3%20Qxa5%2011.O-O%20Qc7%2012.Bf4%20Bg4%2013.h3%20Bxf3%2014.Qxf3%20e6%2015.c4%20Ne7%2016.dxc5%20Bxe5%2017.Bxe5%20Qxe5%2018.cxd5%20Qxd5%2019.Qf6%20Rf8%2020.Rfd1%20Qf5%2021.Qd4%20Nd5%2022.Nc4%20Ke7%2023.Nb6%20Ra7%2024.Qh4%2B%20Qf6%2025.Qg3%20Rd8%2026.Nc4%20Kf8%2027.Ne5%20Rc7%2028.Rxa6%20Qf4%2029.Qxf4%20Nxf4%2030.Rxd8%2B%20Ke7%2031.Rxc6%20Ra7%2032.Rcd6%20Ra1%2B%2033.Kh2%20Re1%2034.Nc6%2B%20Kf6#52) |

**without**: split at ply 8, Black to move: chosen **g5** (67% there) vs subpar **Rdc8** (33%). `3r1k2/2r2pqp/p1p1p1p1/2PnN3/7Q/5R1P/1P3PP1/3R2K1 b - - 23 30`

```
. . . r . k . .
. . r . . p q p
p . p . p . p .
. . P n N . . .
. . . . . . . Q
. . . . . R . P
. P . . . P P .
. . . R . . K .
```

| chosen | subpar |
|---|---|
| 27.Ra3 Rad7 28.Rf3 Qg7 29.Ne5 Rc7 30.Qh4 g5 31.Qg3 h5 32.h4 g4 33.Rfd3 Qf6 34.Nc4 Rcd7 | 27.Ra3 Rad7 28.Rf3 Qg7 29.Ne5 Rc7 30.Qh4 Rdc8 31.Ng4 h5 32.Nf6 Nxf6 33.Rxf6 Kg8 34.Rf3 a5 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20g6%202.d4%20Bg7%203.c3%20d5%204.e5%20c5%205.Nf3%20Nc6%206.Bb5%20Qb6%207.a4%20a6%208.Bxc6%2B%20bxc6%209.a5%20Qb5%2010.Na3%20Qxa5%2011.O-O%20Qc7%2012.Bf4%20Bg4%2013.h3%20Bxf3%2014.Qxf3%20e6%2015.c4%20Ne7%2016.dxc5%20Bxe5%2017.Bxe5%20Qxe5%2018.cxd5%20Qxd5%2019.Qf6%20Rf8%2020.Rfd1%20Qf5%2021.Qd4%20Nd5%2022.Nc4%20Ke7%2023.Nb6%20Ra7%2024.Qh4%2B%20Qf6%2025.Qg3%20Rd8%2026.Nc4%20Kf8%2027.Ra3%20Rad7%2028.Rf3%20Qg7%2029.Ne5%20Rc7%2030.Qh4%20g5%2031.Qg3%20h5%2032.h4%20g4%2033.Rfd3%20Qf6%2034.Nc4%20Rcd7#52) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20g6%202.d4%20Bg7%203.c3%20d5%204.e5%20c5%205.Nf3%20Nc6%206.Bb5%20Qb6%207.a4%20a6%208.Bxc6%2B%20bxc6%209.a5%20Qb5%2010.Na3%20Qxa5%2011.O-O%20Qc7%2012.Bf4%20Bg4%2013.h3%20Bxf3%2014.Qxf3%20e6%2015.c4%20Ne7%2016.dxc5%20Bxe5%2017.Bxe5%20Qxe5%2018.cxd5%20Qxd5%2019.Qf6%20Rf8%2020.Rfd1%20Qf5%2021.Qd4%20Nd5%2022.Nc4%20Ke7%2023.Nb6%20Ra7%2024.Qh4%2B%20Qf6%2025.Qg3%20Rd8%2026.Nc4%20Kf8%2027.Ra3%20Rad7%2028.Rf3%20Qg7%2029.Ne5%20Rc7%2030.Qh4%20Rdc8%2031.Ng4%20h5%2032.Nf6%20Nxf6%2033.Rxf6%20Kg8%2034.Rf3%20a5#52) |

### k = 4: a = 1109 (0.50) + b = 1230 (0.50): position 37, pair 2

**with**: split at ply 10, Black to move: chosen **Rd8** (50% there) vs subpar **Kf6** (33%). `7r/1p1B2kp/p5p1/2rp4/5NP1/P7/1P1N2P1/n2K4 b - - 0 30`

```
. . . . . . . r
. p . B . . k p
p . . . . . p .
. . r p . . . .
. . . . . N P .
P . . . . . . .
. P . N . . P .
n . . K . . . .
```

| chosen | subpar |
|---|---|
| 26.e6 Rxc5 27.exf7 Kxf7 28.Qf1+ [Kg7]a [29.Qf4]b [Qxf4]a [30.Nxf4]b [Rd8]a [31.Be6]b [Rc6]a [32.Bxd5]b [Rcd6]a [33.Ne4]b Rxd5+ | 26.e6 Rxc5 27.exf7 Kxf7 28.Qf1+ [Kg7]a [29.Qf4]b [Qxf4]a [30.Nxf4]b Kf6 31.Nd3 Rc7 32.Ba4 Rhc8 33.Nf3 Nc2 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20e6%203.e3%20Bd6%204.Bg3%20Bxg3%205.hxg3%20Nc6%206.c4%20Nge7%207.a3%20Bd7%208.Qg4%20g6%209.Qg5%20Nf5%2010.Qf4%20Qe7%2011.g4%20Nd6%2012.c5%20Ne4%2013.Qxc7%20Bc8%2014.Qf4%20e5%2015.Qh6%20Bxg4%2016.f3%20Ng3%2017.fxg4%20Nxh1%2018.Qxh1%20Qg5%2019.Be2%20Qxe3%2020.dxe5%20Nd4%2021.Nd2%20Nc2%2B%2022.Kd1%20Nxa1%2023.Bb5%2B%20Kf8%2024.Ne2%20a6%2025.Bd7%20Rc8%2026.e6%20Rxc5%2027.exf7%20Kxf7%2028.Qf1%2B%20Kg7%2029.Qf4%20Qxf4%2030.Nxf4%20Rd8%2031.Be6%20Rc6%2032.Bxd5%20Rcd6%2033.Ne4%20Rxd5%2B#50) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20e6%203.e3%20Bd6%204.Bg3%20Bxg3%205.hxg3%20Nc6%206.c4%20Nge7%207.a3%20Bd7%208.Qg4%20g6%209.Qg5%20Nf5%2010.Qf4%20Qe7%2011.g4%20Nd6%2012.c5%20Ne4%2013.Qxc7%20Bc8%2014.Qf4%20e5%2015.Qh6%20Bxg4%2016.f3%20Ng3%2017.fxg4%20Nxh1%2018.Qxh1%20Qg5%2019.Be2%20Qxe3%2020.dxe5%20Nd4%2021.Nd2%20Nc2%2B%2022.Kd1%20Nxa1%2023.Bb5%2B%20Kf8%2024.Ne2%20a6%2025.Bd7%20Rc8%2026.e6%20Rxc5%2027.exf7%20Kxf7%2028.Qf1%2B%20Kg7%2029.Qf4%20Qxf4%2030.Nxf4%20Kf6%2031.Nd3%20Rc7%2032.Ba4%20Rhc8%2033.Nf3%20Nc2#50) |

**without**: split at ply 10, Black to move: chosen **Rxb7** (61% there) vs subpar **Qxe5** (33%). `1r6/1B3pkp/p1P3p1/3pP3/6P1/P3q3/1P1QN1P1/3K4 b - - 0 30`

```
. r . . . . . .
. B . . . p k p
p . P . . . p .
. . . p P . . .
. . . . . . P .
P . . . q . . .
. P . Q N . P .
. . . K . . . .
```

| chosen | subpar |
|---|---|
| 26.Bxc8 [Kg7]a [27.Bxb7]b [Rb8]a [28.c6]b [Nb3]a [29.Qe1]b [Nxd2]a [30.Qxd2]b [Rxb7]a [31.cxb7]b [Qxe5]a [32.Qd4]b Qxd4+ [33.Nxd4]b Kf6 | 26.Bxc8 [Kg7]a [27.Bxb7]b [Rb8]a [28.c6]b [Nb3]a [29.Qe1]b [Nxd2]a [30.Qxd2]b [Qxe5]a [31.Qd4]b Kf6 32.c7 Re8 33.Qxe5+ Kxe5 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20e6%203.e3%20Bd6%204.Bg3%20Bxg3%205.hxg3%20Nc6%206.c4%20Nge7%207.a3%20Bd7%208.Qg4%20g6%209.Qg5%20Nf5%2010.Qf4%20Qe7%2011.g4%20Nd6%2012.c5%20Ne4%2013.Qxc7%20Bc8%2014.Qf4%20e5%2015.Qh6%20Bxg4%2016.f3%20Ng3%2017.fxg4%20Nxh1%2018.Qxh1%20Qg5%2019.Be2%20Qxe3%2020.dxe5%20Nd4%2021.Nd2%20Nc2%2B%2022.Kd1%20Nxa1%2023.Bb5%2B%20Kf8%2024.Ne2%20a6%2025.Bd7%20Rc8%2026.Bxc8%20Kg7%2027.Bxb7%20Rb8%2028.c6%20Nb3%2029.Qe1%20Nxd2%2030.Qxd2%20Rxb7%2031.cxb7%20Qxe5%2032.Qd4%20Qxd4%2B%2033.Nxd4%20Kf6#50) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20e6%203.e3%20Bd6%204.Bg3%20Bxg3%205.hxg3%20Nc6%206.c4%20Nge7%207.a3%20Bd7%208.Qg4%20g6%209.Qg5%20Nf5%2010.Qf4%20Qe7%2011.g4%20Nd6%2012.c5%20Ne4%2013.Qxc7%20Bc8%2014.Qf4%20e5%2015.Qh6%20Bxg4%2016.f3%20Ng3%2017.fxg4%20Nxh1%2018.Qxh1%20Qg5%2019.Be2%20Qxe3%2020.dxe5%20Nd4%2021.Nd2%20Nc2%2B%2022.Kd1%20Nxa1%2023.Bb5%2B%20Kf8%2024.Ne2%20a6%2025.Bd7%20Rc8%2026.Bxc8%20Kg7%2027.Bxb7%20Rb8%2028.c6%20Nb3%2029.Qe1%20Nxd2%2030.Qxd2%20Qxe5%2031.Qd4%20Kf6%2032.c7%20Re8%2033.Qxe5%2B%20Kxe5#50) |

### k = 4: a = 1109 (0.50) + b = 1230 (0.50): position 41, pair 3

**with**: split at ply 9, Black to move: chosen **Kg7** (67% there) vs subpar **Ne6** (33%). `r4n1r/p3bk2/6p1/3QPp1p/5B1P/2P3N1/PP6/2KR3R b - - 0 22`

```
r . . . . n . r
p . . . b k . .
. . . . . . p .
. . . Q P p . p
. . . . . B . P
. . P . . . N .
P P . . . . . .
. . K R . . . R
```

| chosen | subpar |
|---|---|
| 18...Qd7 19.d5 cxd5 20.Bxb5 Qxb5 21.Qxb5+ Kf7 22.Qxd5+ [Kg7]a [23.Nxf5+]b [gxf5]a [24.Qxa8]b [Ng6]a [25.Qxa7]b Kf7 26.Rd7 | 18...Qd7 19.d5 cxd5 20.Bxb5 Qxb5 21.Qxb5+ Kf7 22.Qxd5+ Ne6 23.Qd7 Rhd8 24.Qc6 Rac8 25.Qf3 Nc5 26.Rxd8 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.Nc3%20dxe4%204.Nxe4%20Bf5%205.f3%20Nf6%206.Bd3%20e6%207.Ne2%20Nbd7%208.Bf4%20Be7%209.g4%20Bxe4%2010.fxe4%20Nxg4%2011.Ng3%20f6%2012.Qxg4%20g6%2013.Qxe6%20Nf8%2014.Qb3%20b5%2015.c3%20Qc8%2016.e5%20f5%2017.h4%20h5%2018.O-O-O%20Qd7%2019.d5%20cxd5%2020.Bxb5%20Qxb5%2021.Qxb5%2B%20Kf7%2022.Qxd5%2B%20Kg7%2023.Nxf5%2B%20gxf5%2024.Qxa8%20Ng6%2025.Qxa7%20Kf7%2026.Rd7#35) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.Nc3%20dxe4%204.Nxe4%20Bf5%205.f3%20Nf6%206.Bd3%20e6%207.Ne2%20Nbd7%208.Bf4%20Be7%209.g4%20Bxe4%2010.fxe4%20Nxg4%2011.Ng3%20f6%2012.Qxg4%20g6%2013.Qxe6%20Nf8%2014.Qb3%20b5%2015.c3%20Qc8%2016.e5%20f5%2017.h4%20h5%2018.O-O-O%20Qd7%2019.d5%20cxd5%2020.Bxb5%20Qxb5%2021.Qxb5%2B%20Kf7%2022.Qxd5%2B%20Ne6%2023.Qd7%20Rhd8%2024.Qc6%20Rac8%2025.Qf3%20Nc5%2026.Rxd8#35) |

**without**: split at ply 9, Black to move: chosen **Ne6** (65% there) vs subpar **a3** (33%). `r1q2n1r/4bk2/6p1/1B1RPp1p/p4B1P/2P3N1/PPQ5/2K4R b - - 0 22`

```
r . q . . n . r
. . . . b k . .
. . . . . . p .
. B . R P p . p
p . . . . B . P
. . P . . . N .
P P Q . . . . .
. . K . . . . R
```

| chosen | subpar |
|---|---|
| 18...a5 19.d5 a4 20.Qc2 cxd5 21.Bxb5+ Kf7 22.Rxd5 Ne6 23.Be3 a3 24.b3 Rd8 25.Rhd1 Rxd5 26.Rxd5 | 18...a5 19.d5 a4 20.Qc2 cxd5 21.Bxb5+ Kf7 22.Rxd5 a3 23.b3 Ne6 24.Bd2 Rd8 25.Rxd8 Qxd8 26.Bc4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.Nc3%20dxe4%204.Nxe4%20Bf5%205.f3%20Nf6%206.Bd3%20e6%207.Ne2%20Nbd7%208.Bf4%20Be7%209.g4%20Bxe4%2010.fxe4%20Nxg4%2011.Ng3%20f6%2012.Qxg4%20g6%2013.Qxe6%20Nf8%2014.Qb3%20b5%2015.c3%20Qc8%2016.e5%20f5%2017.h4%20h5%2018.O-O-O%20a5%2019.d5%20a4%2020.Qc2%20cxd5%2021.Bxb5%2B%20Kf7%2022.Rxd5%20Ne6%2023.Be3%20a3%2024.b3%20Rd8%2025.Rhd1%20Rxd5%2026.Rxd5#35) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.d4%20d5%203.Nc3%20dxe4%204.Nxe4%20Bf5%205.f3%20Nf6%206.Bd3%20e6%207.Ne2%20Nbd7%208.Bf4%20Be7%209.g4%20Bxe4%2010.fxe4%20Nxg4%2011.Ng3%20f6%2012.Qxg4%20g6%2013.Qxe6%20Nf8%2014.Qb3%20b5%2015.c3%20Qc8%2016.e5%20f5%2017.h4%20h5%2018.O-O-O%20a5%2019.d5%20a4%2020.Qc2%20cxd5%2021.Bxb5%2B%20Kf7%2022.Rxd5%20a3%2023.b3%20Ne6%2024.Bd2%20Rd8%2025.Rxd8%20Qxd8%2026.Bc4#35) |

### k = 4: a = 1109 (0.50) + b = 1230 (0.50): position 42, pair 4

**with**: split at ply 6, Black to move: chosen **Kxg7** (67% there) vs subpar **Nbd7** (33%). `rn4k1/1b3pBp/p3pn2/1p1p4/8/4P1P1/3NNPBP/Q4RK1 b - - 0 16`

```
r n . . . . k .
. b . . . p B p
p . . . p n . .
. p . p . . . .
. . . . . . . .
. . . . P . P .
. . . N N P B P
Q . . . . R K .
```

| chosen | subpar |
|---|---|
| 14.Bxf8 Qxa1 15.Qxa1 Bb7 16.Bxg7 [Kxg7]a [17.Nf4]b [Nc6]a [18.Nf3]b [Rc8]a [19.Nh5+]b Kg6 [20.Nxf6]b Nb4 21.Ne5+ [Kg7]a | 14.Bxf8 Qxa1 15.Qxa1 Bb7 16.Bxg7 Nbd7 17.Bxf6 Nxf6 18.Qxf6 Bc6 19.Nd4 Bb7 20.Rc1 a5 21.Rc7 Rf8 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.e3%20e6%203.Ne2%20c5%204.Nd2%20a6%205.g3%20Nf6%206.Bg2%20Be7%207.O-O%20O-O%208.c3%20b5%209.a4%20Qa5%2010.dxc5%20Bxc5%2011.b4%20Bxb4%2012.cxb4%20Qxb4%2013.Ba3%20Qxa4%2014.Bxf8%20Qxa1%2015.Qxa1%20Bb7%2016.Bxg7%20Kxg7%2017.Nf4%20Nc6%2018.Nf3%20Rc8%2019.Nh5%2B%20Kg6%2020.Nxf6%20Nb4%2021.Ne5%2B%20Kg7#26) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.e3%20e6%203.Ne2%20c5%204.Nd2%20a6%205.g3%20Nf6%206.Bg2%20Be7%207.O-O%20O-O%208.c3%20b5%209.a4%20Qa5%2010.dxc5%20Bxc5%2011.b4%20Bxb4%2012.cxb4%20Qxb4%2013.Ba3%20Qxa4%2014.Bxf8%20Qxa1%2015.Qxa1%20Bb7%2016.Bxg7%20Nbd7%2017.Bxf6%20Nxf6%2018.Qxf6%20Bc6%2019.Nd4%20Bb7%2020.Rc1%20a5%2021.Rc7%20Rf8#26) |

**without**: split at ply 6, Black to move: chosen **Ke8** (51% there) vs subpar **Kg8** (49%). `rnb2k2/5ppp/p3pn2/1p1p4/8/Q3P1P1/3NNPBP/5RK1 b - - 1 16`

```
r n b . . k . .
. . . . . p p p
p . . . p n . .
. p . p . . . .
. . . . . . . .
Q . . . P . P .
. . . N N P B P
. . . . . R K .
```

| chosen | subpar |
|---|---|
| 14.Bxf8 Qxa1 15.Qxa1 Kxf8 16.Qa3+ Ke8 17.Rc1 Bd7 18.Qd6 Nc6 19.Rxc6 Bxc6 20.Qxc6+ Ke7 21.Qxa8 Nd7 | 14.Bxf8 Qxa1 15.Qxa1 Kxf8 16.Qa3+ Kg8 17.Rc1 Bb7 18.Qe7 Nc6 19.Qxb7 Na5 20.Qxa8+ Ne8 21.Rc8 Kf8 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.e3%20e6%203.Ne2%20c5%204.Nd2%20a6%205.g3%20Nf6%206.Bg2%20Be7%207.O-O%20O-O%208.c3%20b5%209.a4%20Qa5%2010.dxc5%20Bxc5%2011.b4%20Bxb4%2012.cxb4%20Qxb4%2013.Ba3%20Qxa4%2014.Bxf8%20Qxa1%2015.Qxa1%20Kxf8%2016.Qa3%2B%20Ke8%2017.Rc1%20Bd7%2018.Qd6%20Nc6%2019.Rxc6%20Bxc6%2020.Qxc6%2B%20Ke7%2021.Qxa8%20Nd7#26) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.e3%20e6%203.Ne2%20c5%204.Nd2%20a6%205.g3%20Nf6%206.Bg2%20Be7%207.O-O%20O-O%208.c3%20b5%209.a4%20Qa5%2010.dxc5%20Bxc5%2011.b4%20Bxb4%2012.cxb4%20Qxb4%2013.Ba3%20Qxa4%2014.Bxf8%20Qxa1%2015.Qxa1%20Kxf8%2016.Qa3%2B%20Kg8%2017.Rc1%20Bb7%2018.Qe7%20Nc6%2019.Qxb7%20Na5%2020.Qxa8%2B%20Ne8%2021.Rc8%20Kf8#26) |

### k = 4: a = 1109 (0.50) + b = 1230 (0.50): position 35, pair 5

**with**: split at ply 3, White to move: chosen **Rad1** (64% there) vs subpar **Kh1** (32%). `3rr1k1/ppp2pp1/5b1p/8/3q4/5Q1P/PP3PKP/R5R1 w - - 0 22`

```
. . . r r . k .
p p p . . p p .
. . . . . b . p
. . . . . . . .
. . . q . . . .
. . . . . Q . P
P P . . . P K P
R . . . . . R .
```

| chosen | subpar |
|---|---|
| [21.Qf3]a [Qxd4]b [22.Rad1]a [Qxb2]b [23.Rb1]a [Qxa2]b [24.Rxb7]a [Bd4]b [25.Rf1]a [Bb6]b [26.Qc6]a [Qd5+]b [27.Qxd5]a [Rxd5]b [28.Rc1]a [Rd2]b | [21.Qf3]a [Qxd4]b 22.Kh1 Qe4 23.Qxe4 Rxe4 24.Rac1 c6 25.b3 Re2 26.Rgf1 Rdd2 27.a4 Rxf2 28.Rxf2 Rxf2 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nc3%20Nf6%203.d4%20exd4%204.Qxd4%20Nc6%205.Qd1%20d6%206.Bb5%20Be7%207.Bg5%20h6%208.Bxf6%20Bxf6%209.Qf3%20O-O%2010.Nh3%20Nd4%2011.Qd1%20Bxh3%2012.gxh3%20d5%2013.exd5%20Qd6%2014.Be2%20Rfe8%2015.Ne4%20Rxe4%2016.c3%20Rxe2%2B%2017.Kf1%20Ree8%2018.cxd4%20Qxd5%2019.Rg1%20Qc4%2B%2020.Kg2%20Rad8%2021.Qf3%20Qxd4%2022.Rad1%20Qxb2%2023.Rb1%20Qxa2%2024.Rxb7%20Bd4%2025.Rf1%20Bb6%2026.Qc6%20Qd5%2B%2027.Qxd5%20Rxd5%2028.Rc1%20Rd2#40) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nc3%20Nf6%203.d4%20exd4%204.Qxd4%20Nc6%205.Qd1%20d6%206.Bb5%20Be7%207.Bg5%20h6%208.Bxf6%20Bxf6%209.Qf3%20O-O%2010.Nh3%20Nd4%2011.Qd1%20Bxh3%2012.gxh3%20d5%2013.exd5%20Qd6%2014.Be2%20Rfe8%2015.Ne4%20Rxe4%2016.c3%20Rxe2%2B%2017.Kf1%20Ree8%2018.cxd4%20Qxd5%2019.Rg1%20Qc4%2B%2020.Kg2%20Rad8%2021.Qf3%20Qxd4%2022.Kh1%20Qe4%2023.Qxe4%20Rxe4%2024.Rac1%20c6%2025.b3%20Re2%2026.Rgf1%20Rdd2%2027.a4%20Rxf2%2028.Rxf2%20Rxf2#40) |

**without**: split at ply 3, White to move: chosen **Qf3** (64% there) vs subpar **Rxc4** (36%). `4r1k1/ppp2pp1/5b1p/8/2qr4/7P/PP3PKP/2RQ2R1 w - - 0 22`

```
. . . . r . k .
p p p . . p p .
. . . . . b . p
. . . . . . . .
. . q r . . . .
. . . . . . . P
P P . . . P K P
. . R Q . . R .
```

| chosen | subpar |
|---|---|
| [21.Rc1]a [Rxd4]b [22.Qf3]a [Qd5]b [23.Qxd5]a [Rxd5]b [24.Rxc7]a [Rd2]b [25.Rxb7]a [Bd4]b [26.Rf1]a [Ree2]b 27.Kf3 Rxf2+ 28.Rxf2 Rxf2+ | [21.Rc1]a [Rxd4]b [22.Rxc4]a [Rxd1]b [23.Rxd1]a [c6]b [24.Rd7]a [Re7]b [25.Rxe7]a [Bxe7]b [26.b4]a [Bd6]b [27.a4]a [Kf8]b [28.b5]a [cxb5]b |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nc3%20Nf6%203.d4%20exd4%204.Qxd4%20Nc6%205.Qd1%20d6%206.Bb5%20Be7%207.Bg5%20h6%208.Bxf6%20Bxf6%209.Qf3%20O-O%2010.Nh3%20Nd4%2011.Qd1%20Bxh3%2012.gxh3%20d5%2013.exd5%20Qd6%2014.Be2%20Rfe8%2015.Ne4%20Rxe4%2016.c3%20Rxe2%2B%2017.Kf1%20Ree8%2018.cxd4%20Qxd5%2019.Rg1%20Qc4%2B%2020.Kg2%20Rad8%2021.Rc1%20Rxd4%2022.Qf3%20Qd5%2023.Qxd5%20Rxd5%2024.Rxc7%20Rd2%2025.Rxb7%20Bd4%2026.Rf1%20Ree2%2027.Kf3%20Rxf2%2B%2028.Rxf2%20Rxf2%2B#40) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nc3%20Nf6%203.d4%20exd4%204.Qxd4%20Nc6%205.Qd1%20d6%206.Bb5%20Be7%207.Bg5%20h6%208.Bxf6%20Bxf6%209.Qf3%20O-O%2010.Nh3%20Nd4%2011.Qd1%20Bxh3%2012.gxh3%20d5%2013.exd5%20Qd6%2014.Be2%20Rfe8%2015.Ne4%20Rxe4%2016.c3%20Rxe2%2B%2017.Kf1%20Ree8%2018.cxd4%20Qxd5%2019.Rg1%20Qc4%2B%2020.Kg2%20Rad8%2021.Rc1%20Rxd4%2022.Rxc4%20Rxd1%2023.Rxd1%20c6%2024.Rd7%20Re7%2025.Rxe7%20Bxe7%2026.b4%20Bd6%2027.a4%20Kf8%2028.b5%20cxb5#40) |

## k = 6: a = 603 (0.50) + b = 1752 (0.50)

Holds at 20 of 2500 pairs (0.8%), at 11 positions; recurrence in the report 0.8% (null 95th 0.0%).

Board scan (every ply of the rollouts, lines weighted by count): each latent's phi correlation with each piece on a square and with White to move after the move; 'on X% of plies with it' is the latent's rate given the piece is there.

- a: on at 9.6% of plies; phi with White to move +0.13; top: White N on d4 +0.22 (on 40% of plies with it, 8% without), White P on g5 +0.22 (on 35% of plies with it, 8% without), White B on e4 +0.20 (on 43% of plies with it, 9% without), White R on h7 +0.17 (on 90% of plies with it, 9% without)
- b: on at 9.8% of plies; phi with White to move -0.13; top: White P on g5 +0.23 (on 36% of plies with it, 8% without), White N on d4 +0.22 (on 41% of plies with it, 8% without), White B on e4 +0.20 (on 43% of plies with it, 9% without), White R on h7 +0.16 (on 86% of plies with it, 9% without)
- either: on at 16.3% of plies; phi with White to move +0.00; top: White K on d1 +0.25 (on 86% of plies with it, 15% without), Black N on a1 +0.24 (on 93% of plies with it, 15% without), White P on g4 +0.24 (on 52% of plies with it, 14% without), White N on f4 +0.21 (on 65% of plies with it, 15% without)

### k = 6: a = 603 (0.50) + b = 1752 (0.50): position 1, pair 1

**with**: split at ply 6, Black to move: chosen **hxg6** (60% there) vs subpar **fxg6** (40%). `r2q1rk1/pp2bppp/3p1nB1/2pP2NQ/5B2/8/PPP2PPP/R3R1K1 b - - 0 15`

```
r . . q . r k .
p p . . b p p p
. . . p . n B .
. . p P . . N Q
. . . . . B . .
. . . . . . . .
P P P . . P P P
R . . . R . K .
```

| chosen | subpar |
|---|---|
| 13.Rfe1 O-O 14.Bd3 Nf6 15.Bxg6 [hxg6]b [16.Qh3]a [Nh5]b [17.Nxf7]a [Rxf7]b [18.Bd2]a [Bg5]b [19.Bc3]a [Nf4]b [20.Qg4]a [Qd7]b | 13.Rfe1 O-O 14.Bd3 Nf6 15.Bxg6 fxg6 16.Qh3 Nxd5 17.Qe6+ Kh8 18.Qxd5 Rxf4 19.Nf7+ Rxf7 20.Qxf7 Bf6 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20c5%202.d5%20e6%203.Nc3%20exd5%204.Nxd5%20d6%205.e4%20Nc6%206.Nf3%20Be6%207.Bf4%20Nf6%208.Ng5%20Bxd5%209.exd5%20Ne5%2010.Bb5%2B%20Nfd7%2011.Qh5%20Ng6%2012.O-O%20Be7%2013.Rfe1%20O-O%2014.Bd3%20Nf6%2015.Bxg6%20hxg6%2016.Qh3%20Nh5%2017.Nxf7%20Rxf7%2018.Bd2%20Bg5%2019.Bc3%20Nf4%2020.Qg4%20Qd7#24) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20c5%202.d5%20e6%203.Nc3%20exd5%204.Nxd5%20d6%205.e4%20Nc6%206.Nf3%20Be6%207.Bf4%20Nf6%208.Ng5%20Bxd5%209.exd5%20Ne5%2010.Bb5%2B%20Nfd7%2011.Qh5%20Ng6%2012.O-O%20Be7%2013.Rfe1%20O-O%2014.Bd3%20Nf6%2015.Bxg6%20fxg6%2016.Qh3%20Nxd5%2017.Qe6%2B%20Kh8%2018.Qxd5%20Rxf4%2019.Nf7%2B%20Rxf7%2020.Qxf7%20Bf6#24) |

**without**: split at ply 6, Black to move: chosen **f6** (43% there) vs subpar **Nf6** (36%). `r2q1rk1/pp1n1ppp/3p2n1/2pP2BQ/8/3B4/PPP2PPP/R3R1K1 b - - 0 15`

```
r . . q . r k .
p p . n . p p p
. . . p . . n .
. . p P . . B Q
. . . . . . . .
. . . B . . . .
P P P . . P P P
R . . . R . K .
```

| chosen | subpar |
|---|---|
| 13.Rfe1 O-O 14.Bd3 Bxg5 15.Bxg5 f6 16.Bd2 Nde5 17.Bf5 Qe8 18.f4 Nf7 19.Rxe8 Raxe8 20.Re1 Rxe1+ | 13.Rfe1 O-O 14.Bd3 Bxg5 15.Bxg5 Nf6 16.Qh3 Re8 17.Rxe8+ Qxe8 18.Bxf6 gxf6 19.Qg3 Qe5 20.Qxe5 fxe5 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20c5%202.d5%20e6%203.Nc3%20exd5%204.Nxd5%20d6%205.e4%20Nc6%206.Nf3%20Be6%207.Bf4%20Nf6%208.Ng5%20Bxd5%209.exd5%20Ne5%2010.Bb5%2B%20Nfd7%2011.Qh5%20Ng6%2012.O-O%20Be7%2013.Rfe1%20O-O%2014.Bd3%20Bxg5%2015.Bxg5%20f6%2016.Bd2%20Nde5%2017.Bf5%20Qe8%2018.f4%20Nf7%2019.Rxe8%20Raxe8%2020.Re1%20Rxe1%2B#24) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20c5%202.d5%20e6%203.Nc3%20exd5%204.Nxd5%20d6%205.e4%20Nc6%206.Nf3%20Be6%207.Bf4%20Nf6%208.Ng5%20Bxd5%209.exd5%20Ne5%2010.Bb5%2B%20Nfd7%2011.Qh5%20Ng6%2012.O-O%20Be7%2013.Rfe1%20O-O%2014.Bd3%20Bxg5%2015.Bxg5%20Nf6%2016.Qh3%20Re8%2017.Rxe8%2B%20Qxe8%2018.Bxf6%20gxf6%2019.Qg3%20Qe5%2020.Qxe5%20fxe5#24) |

### k = 6: a = 603 (0.50) + b = 1752 (0.50): position 26, pair 2

**with**: split at ply 8, Black to move: chosen **Qxh5** (60% there) vs subpar **Qd6** (40%). `1rb1rbk1/2p4p/2p3q1/2Np1pPP/p2B4/P1Q5/1PP2P2/1K1R2R1 b - - 0 27`

```
. r b . r b k .
. . p . . . . p
. . p . . . q .
. . N p . p P P
p . . B . . . .
P . Q . . . . .
. P P . . P . .
. K . R . . R .
```

| chosen | subpar |
|---|---|
| 24.h4 Rb8 25.g5 f5 26.Bd4 Bf8 27.h5 [Qxh5]a [28.Rh1]b [Qg6]ab [29.f4]b [Bg7]a [30.Bxg7]b [Qxg7]a [31.Qxg7+]b [Kxg7]a | 24.h4 Rb8 25.g5 f5 26.Bd4 Bf8 27.h5 Qd6 28.g6 h6 29.g7 Be7 30.Rde1 Bg5 31.Rxe8+ Kf7 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.h4%20Rb8%2025.g5%20f5%2026.Bd4%20Bf8%2027.h5%20Qxh5%2028.Rh1%20Qg6%2029.f4%20Bg7%2030.Bxg7%20Qxg7%2031.Qxg7%2B%20Kxg7#46) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.h4%20Rb8%2025.g5%20f5%2026.Bd4%20Bf8%2027.h5%20Qd6%2028.g6%20h6%2029.g7%20Be7%2030.Rde1%20Bg5%2031.Rxe8%2B%20Kf7#46) |

**without**: split at ply 8, Black to move: chosen **Qe5** (47% there) vs subpar **Rb8** (42%). `r1b1r1k1/2p3qp/2p5/2Np1pP1/p4Q2/P7/1PP2P1P/1K1R2R1 b - - 2 27`

```
r . b . r . k .
. . p . . . q p
. . p . . . . .
. . N p . p P .
p . . . . Q . .
P . . . . . . .
. P P . . P . P
. K . R . . R .
```

| chosen | subpar |
|---|---|
| 24.g5 f5 25.Bd4 Bxd4 26.Qxd4 Qg7 27.Qf4 Qe5 28.Qh4 Rb8 29.Nd3 Qc3 30.Kc1 Ba6 31.g6 Bxd3 | 24.g5 f5 25.Bd4 Bxd4 26.Qxd4 Qg7 27.Qf4 Rb8 28.c3 Re4 29.Nxe4 fxe4 30.Qf6 Qxf6 31.gxf6+ Kf7 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.g5%20f5%2025.Bd4%20Bxd4%2026.Qxd4%20Qg7%2027.Qf4%20Qe5%2028.Qh4%20Rb8%2029.Nd3%20Qc3%2030.Kc1%20Ba6%2031.g6%20Bxd3#46) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20f5%204.Nc3%20fxe4%205.Nxe4%20Nf6%206.Qe2%20d5%207.Nxf6%2B%20gxf6%208.d4%20Bg7%209.dxe5%20O-O%2010.e6%20Re8%2011.Be3%20Bxe6%2012.O-O-O%20Qe7%2013.Qd2%20a6%2014.Bxc6%20bxc6%2015.Nd4%20Bd7%2016.Nb3%20a5%2017.a3%20a4%2018.Nc5%20Bf5%2019.Rhe1%20Qf7%2020.Qc3%20Qg6%2021.Kb1%20Bf8%2022.g4%20Bc8%2023.Rg1%20Bg7%2024.g5%20f5%2025.Bd4%20Bxd4%2026.Qxd4%20Qg7%2027.Qf4%20Rb8%2028.c3%20Re4%2029.Nxe4%20fxe4%2030.Qf6%20Qxf6%2031.gxf6%2B%20Kf7#46) |

### k = 6: a = 603 (0.50) + b = 1752 (0.50): position 44, pair 3

**with**: split at ply 8, White to move: chosen **Rxh7** (56% there) vs subpar **Bf5** (39%). `2k2r1r/pp1n3p/3q4/2p5/5BP1/3B4/P1P1N3/2R2K1R w - - 0 28`

```
. . k . . r . r
p p . n . . . p
. . . q . . . .
. . p . . . . .
. . . . . B P .
. . . B . . . .
P . P . N . . .
. . R . . K . R
```

| chosen | subpar |
|---|---|
| 24...Kc8 [25.hxg4]b [Rf8]a [26.Ne2]b [Qf6]a [27.Qd6]b [Qxd6]a [28.Rxh7]ab [Qxf4+]ab [29.Nxf4]ab [Rxh7]ab [30.Bxh7]ab [Rxf4+]ab [31.Ke2]ab [Rxg4]ab [32.Rf1]ab | 24...Kc8 [25.hxg4]b [Rf8]a [26.Ne2]b [Qf6]a [27.Qd6]b [Qxd6]a [28.Bf5]b [Rxf5]a [29.gxf5]b [Qd5]a [30.Rh3]b [Qxf5]a [31.Rd3]b [Rf8]a [32.Rcd1]b |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Bc4%20fxe4%204.d3%20d5%205.Bb3%20exd3%206.Qxd3%20e4%207.Qd4%20Nf6%208.Nc3%20c5%209.Qe5%2B%20Be7%2010.Nxd5%20Nxd5%2011.Bxd5%20Qa5%2B%2012.Bd2%20Qb6%2013.Qxg7%20Bf6%2014.Qf7%2B%20Kd8%2015.Bxe4%20Bg4%2016.Qd5%2B%20Nd7%2017.h3%20Bh4%2B%2018.g3%20Bxg3%2B%2019.Kf1%20Qb5%2B%2020.Bd3%20Qxb2%2021.Qg5%2B%20Kc7%2022.Rc1%20Rag8%2023.Qd5%20Bxf4%2024.Bxf4%2B%20Kc8%2025.hxg4%20Rf8%2026.Ne2%20Qf6%2027.Qd6%20Qxd6%2028.Rxh7%20Qxf4%2B%2029.Nxf4%20Rxh7%2030.Bxh7%20Rxf4%2B%2031.Ke2%20Rxg4%2032.Rf1#47) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Bc4%20fxe4%204.d3%20d5%205.Bb3%20exd3%206.Qxd3%20e4%207.Qd4%20Nf6%208.Nc3%20c5%209.Qe5%2B%20Be7%2010.Nxd5%20Nxd5%2011.Bxd5%20Qa5%2B%2012.Bd2%20Qb6%2013.Qxg7%20Bf6%2014.Qf7%2B%20Kd8%2015.Bxe4%20Bg4%2016.Qd5%2B%20Nd7%2017.h3%20Bh4%2B%2018.g3%20Bxg3%2B%2019.Kf1%20Qb5%2B%2020.Bd3%20Qxb2%2021.Qg5%2B%20Kc7%2022.Rc1%20Rag8%2023.Qd5%20Bxf4%2024.Bxf4%2B%20Kc8%2025.hxg4%20Rf8%2026.Ne2%20Qf6%2027.Qd6%20Qxd6%2028.Bf5%20Rxf5%2029.gxf5%20Qd5%2030.Rh3%20Qxf5%2031.Rd3%20Rf8%2032.Rcd1#47) |

**without**: split at ply 8, White to move: chosen **Kg2** (57% there) vs subpar **g6** (43%). `2k2r1r/pp1n4/8/2pQ2P1/5B1p/3B4/PqP1N3/2R2K1R w - - 0 28`

```
. . k . . r . r
p p . n . . . .
. . . . . . . .
. . p Q . . P .
. . . . . B . p
. . . B . . . .
P q P . N . . .
. . R . . K . R
```

| chosen | subpar |
|---|---|
| 24...Kc8 [25.hxg4]b [Rf8]a [26.Ne2]b [h5]a [27.g5]b [h4]a [28.Kg2]b [h3+]ab [29.Rxh3]ab [Rxh3]ab [30.Kxh3]ab [Qh8+]ab [31.Kg2]ab [Rxf4]ab [32.Nxf4]ab | 24...Kc8 [25.hxg4]b [Rf8]a [26.Ne2]b [h5]a [27.g5]b [h4]a [28.g6]b [h3]ab [29.g7]b [h2]ab [30.gxf8=Q+]b [Rxf8]ab [31.Rxh2]ab [Qg7]ab [32.Qd6]ab |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Bc4%20fxe4%204.d3%20d5%205.Bb3%20exd3%206.Qxd3%20e4%207.Qd4%20Nf6%208.Nc3%20c5%209.Qe5%2B%20Be7%2010.Nxd5%20Nxd5%2011.Bxd5%20Qa5%2B%2012.Bd2%20Qb6%2013.Qxg7%20Bf6%2014.Qf7%2B%20Kd8%2015.Bxe4%20Bg4%2016.Qd5%2B%20Nd7%2017.h3%20Bh4%2B%2018.g3%20Bxg3%2B%2019.Kf1%20Qb5%2B%2020.Bd3%20Qxb2%2021.Qg5%2B%20Kc7%2022.Rc1%20Rag8%2023.Qd5%20Bxf4%2024.Bxf4%2B%20Kc8%2025.hxg4%20Rf8%2026.Ne2%20h5%2027.g5%20h4%2028.Kg2%20h3%2B%2029.Rxh3%20Rxh3%2030.Kxh3%20Qh8%2B%2031.Kg2%20Rxf4%2032.Nxf4#47) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Bc4%20fxe4%204.d3%20d5%205.Bb3%20exd3%206.Qxd3%20e4%207.Qd4%20Nf6%208.Nc3%20c5%209.Qe5%2B%20Be7%2010.Nxd5%20Nxd5%2011.Bxd5%20Qa5%2B%2012.Bd2%20Qb6%2013.Qxg7%20Bf6%2014.Qf7%2B%20Kd8%2015.Bxe4%20Bg4%2016.Qd5%2B%20Nd7%2017.h3%20Bh4%2B%2018.g3%20Bxg3%2B%2019.Kf1%20Qb5%2B%2020.Bd3%20Qxb2%2021.Qg5%2B%20Kc7%2022.Rc1%20Rag8%2023.Qd5%20Bxf4%2024.Bxf4%2B%20Kc8%2025.hxg4%20Rf8%2026.Ne2%20h5%2027.g5%20h4%2028.g6%20h3%2029.g7%20h2%2030.gxf8%3DQ%2B%20Rxf8%2031.Rxh2%20Qg7%2032.Qd6#47) |

### k = 6: a = 603 (0.50) + b = 1752 (0.50): position 4, pair 4

**with**: split at ply 10, Black to move: chosen **Qxh2** (46% there) vs subpar **Bc5** (38%). `r1k2b1N/6pp/p1p5/1p2p3/8/3P4/PPP2PqP/RNB1KR2 b Q - 1 16`

```
r . k . . b . N
. . . . . . p p
p . p . . . . .
. p . . p . . .
. . . . . . . .
. . . P . . . .
P P P . . P q P
R N B . K R . .
```

| chosen | subpar |
|---|---|
| 12.Be6+ Kc7 13.Bxc8 Kxc8 14.Nf7 Qd5 15.Nxh8 Qxg2 16.Rf1 [Qxh2]a [17.Nf7]b [Qh5]a [18.Ng5]b [Be7]a [19.Ne4]b [Qf3]a | 12.Be6+ Kc7 13.Bxc8 Kxc8 14.Nf7 Qd5 15.Nxh8 Qxg2 16.Rf1 Bc5 17.Nc3 Kd7 18.Ne4 Bd4 19.c3 Bb6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Bc4%20a6%203.d3%20Nf6%204.Nf3%20b5%205.Bb3%20Nc6%206.Ng5%20d5%207.exd5%20Nxd5%208.Qf3%20Nce7%209.Qxf7%2B%20Kd7%2010.Qxd5%2B%20Nxd5%2011.Bxd5%20c6%2012.Be6%2B%20Kc7%2013.Bxc8%20Kxc8%2014.Nf7%20Qd5%2015.Nxh8%20Qxg2%2016.Rf1%20Qxh2%2017.Nf7%20Qh5%2018.Ng5%20Be7%2019.Ne4%20Qf3#22) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Bc4%20a6%203.d3%20Nf6%204.Nf3%20b5%205.Bb3%20Nc6%206.Ng5%20d5%207.exd5%20Nxd5%208.Qf3%20Nce7%209.Qxf7%2B%20Kd7%2010.Qxd5%2B%20Nxd5%2011.Bxd5%20c6%2012.Be6%2B%20Kc7%2013.Bxc8%20Kxc8%2014.Nf7%20Qd5%2015.Nxh8%20Qxg2%2016.Rf1%20Bc5%2017.Nc3%20Kd7%2018.Ne4%20Bd4%2019.c3%20Bb6#22) |

**without**: split at ply 10, Black to move: chosen **Rf8** (62% there) vs subpar **Rd8** (38%). `r1q4r/2k1b1p1/p1p4p/1p2p3/4N3/2NPB3/PPP2PPP/R3K2R b KQ - 3 16`

```
r . q . . . . r
. . k . b . p .
p . p . . . . p
. p . . p . . .
. . . . N . . .
. . N P B . . .
P P P . . P P P
R . . . K . . R
```

| chosen | subpar |
|---|---|
| 12.Be6+ Kc7 13.Bxc8 Qxc8 14.Nc3 h6 15.Nge4 Be7 16.Be3 Rf8 17.O-O-O Qe6 18.Kb1 Rad8 19.Rhe1 Qg4 | 12.Be6+ Kc7 13.Bxc8 Qxc8 14.Nc3 h6 15.Nge4 Be7 16.Be3 Rd8 17.O-O-O Kb7 18.f3 a5 19.Bc5 Bxc5 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Bc4%20a6%203.d3%20Nf6%204.Nf3%20b5%205.Bb3%20Nc6%206.Ng5%20d5%207.exd5%20Nxd5%208.Qf3%20Nce7%209.Qxf7%2B%20Kd7%2010.Qxd5%2B%20Nxd5%2011.Bxd5%20c6%2012.Be6%2B%20Kc7%2013.Bxc8%20Qxc8%2014.Nc3%20h6%2015.Nge4%20Be7%2016.Be3%20Rf8%2017.O-O-O%20Qe6%2018.Kb1%20Rad8%2019.Rhe1%20Qg4#22) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Bc4%20a6%203.d3%20Nf6%204.Nf3%20b5%205.Bb3%20Nc6%206.Ng5%20d5%207.exd5%20Nxd5%208.Qf3%20Nce7%209.Qxf7%2B%20Kd7%2010.Qxd5%2B%20Nxd5%2011.Bxd5%20c6%2012.Be6%2B%20Kc7%2013.Bxc8%20Qxc8%2014.Nc3%20h6%2015.Nge4%20Be7%2016.Be3%20Rd8%2017.O-O-O%20Kb7%2018.f3%20a5%2019.Bc5%20Bxc5#22) |

### k = 6: a = 603 (0.50) + b = 1752 (0.50): position 6, pair 5

**with**: split at ply 7, Black to move: chosen **Nxh3** (67% there) vs subpar **Ng6** (33%). `r4rk1/1pp1q1pp/4bp2/p1p1p3/P3Pn2/1P1PNNPP/2P2P1K/R2Q1R2 b - - 0 17`

```
r . . . . r k .
. p p . q . p p
. . . . b p . .
p . p . p . . .
P . . . P n . .
. P . P N N P P
. . P . . P . K
R . . Q . R . .
```

| chosen | subpar |
|---|---|
| 14...c5 15.Ne3 Nf4 16.Kh2 Be6 17.g3 [Nxh3]a [18.Nh4]b [Ng5]a [19.f4]b [exf4]a [20.gxf4]b [Nf7]a [21.Qh5]b [Nh6]a [22.Rg1]b | 14...c5 15.Ne3 Nf4 16.Kh2 Be6 17.g3 Ng6 18.Nf5 Qd7 19.g4 Nf4 20.Qd2 g6 21.Ng3 b6 22.Rg1 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20a6%204.Ba4%20Nf6%205.Bxc6%20dxc6%206.d3%20Nd7%207.O-O%20Bc5%208.Be3%20Qe7%209.Bxc5%20Nxc5%2010.Nbd2%20O-O%2011.a4%20a5%2012.b3%20f6%2013.h3%20Ne6%2014.Nc4%20c5%2015.Ne3%20Nf4%2016.Kh2%20Be6%2017.g3%20Nxh3%2018.Nh4%20Ng5%2019.f4%20exf4%2020.gxf4%20Nf7%2021.Qh5%20Nh6%2022.Rg1#27) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20a6%204.Ba4%20Nf6%205.Bxc6%20dxc6%206.d3%20Nd7%207.O-O%20Bc5%208.Be3%20Qe7%209.Bxc5%20Nxc5%2010.Nbd2%20O-O%2011.a4%20a5%2012.b3%20f6%2013.h3%20Ne6%2014.Nc4%20c5%2015.Ne3%20Nf4%2016.Kh2%20Be6%2017.g3%20Ng6%2018.Nf5%20Qd7%2019.g4%20Nf4%2020.Qd2%20g6%2021.Ng3%20b6%2022.Rg1#27) |

**without**: split at ply 7, Black to move: chosen **Be6** (67% there) vs subpar **Rd8** (33%). `r1b2rk1/2p1q2p/1pp2pp1/p3p3/P3Pn1N/1P1PN2P/2P2PPK/R2Q1R2 b - - 1 17`

```
r . b . . r k .
. . p . q . . p
. p p . . p p .
p . . . p . . .
P . . . P n . N
. P . P N . . P
. . P . . P P K
R . . Q . R . .
```

| chosen | subpar |
|---|---|
| 14...b6 15.Ne3 Nf4 16.Nh4 g6 17.Kh2 Be6 18.g3 [Nxh3]a [19.f4]b [exf4]a [20.gxf4]b [f5]a [21.Qe1]b [fxe4]a [22.dxe4]b | 14...b6 15.Ne3 Nf4 16.Nh4 g6 17.Kh2 Rd8 18.Qf3 Be6 19.g3 [Nxh3]a [20.Qg2]b [Ng5]a [21.f4]b [exf4]a [22.gxf4]b |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20a6%204.Ba4%20Nf6%205.Bxc6%20dxc6%206.d3%20Nd7%207.O-O%20Bc5%208.Be3%20Qe7%209.Bxc5%20Nxc5%2010.Nbd2%20O-O%2011.a4%20a5%2012.b3%20f6%2013.h3%20Ne6%2014.Nc4%20b6%2015.Ne3%20Nf4%2016.Nh4%20g6%2017.Kh2%20Be6%2018.g3%20Nxh3%2019.f4%20exf4%2020.gxf4%20f5%2021.Qe1%20fxe4%2022.dxe4#27) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bb5%20a6%204.Ba4%20Nf6%205.Bxc6%20dxc6%206.d3%20Nd7%207.O-O%20Bc5%208.Be3%20Qe7%209.Bxc5%20Nxc5%2010.Nbd2%20O-O%2011.a4%20a5%2012.b3%20f6%2013.h3%20Ne6%2014.Nc4%20b6%2015.Ne3%20Nf4%2016.Nh4%20g6%2017.Kh2%20Rd8%2018.Qf3%20Be6%2019.g3%20Nxh3%2020.Qg2%20Ng5%2021.f4%20exf4%2022.gxf4#27) |

### k = 6: a = 603 (0.50) + b = 1752 (0.50): position 14, pair 6

**with**: split at ply 10, Black to move: chosen **hxg5** (67% there) vs subpar **b4** (33%). `2r1k2B/1bqpbp2/p3p2p/1p4P1/4P1PP/2N5/PPPQ4/2K2R2 b - - 0 19`

```
. . r . k . . B
. b q p b p . .
p . . . p . . p
. p . . . . P .
. . . . P . P P
. . N . . . . .
P P P Q . . . .
. . K . . R . .
```

| chosen | subpar |
|---|---|
| 15.Bxd4 Ng3 16.Bxg7 Nxh1 17.Bxh8 Nf2 18.Rf1 Nxg4 19.fxg4 [hxg5]b [20.h5]ab [b4]b [21.Nd1]ab [Bxe4]b [22.Ne3]a [d5]b | 15.Bxd4 Ng3 16.Bxg7 Nxh1 17.Bxh8 Nf2 18.Rf1 Nxg4 19.fxg4 b4 20.Nd1 Bxe4 21.Ne3 b3 22.axb3 Bb4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Bxd4%20Ng3%2016.Bxg7%20Nxh1%2017.Bxh8%20Nf2%2018.Rf1%20Nxg4%2019.fxg4%20hxg5%2020.h5%20b4%2021.Nd1%20Bxe4%2022.Ne3%20d5#28) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Bxd4%20Ng3%2016.Bxg7%20Nxh1%2017.Bxh8%20Nf2%2018.Rf1%20Nxg4%2019.fxg4%20b4%2020.Nd1%20Bxe4%2021.Ne3%20b3%2022.axb3%20Bb4#28) |

**without**: split at ply 10, Black to move: chosen **Ng6** (67% there) vs subpar **Bc6** (33%). `2r1k1r1/1bq1bp2/p3p2B/3pP1P1/Np3nBP/5P2/PPPQ4/2KR3R b - - 0 19`

```
. . r . k . r .
. b q . b p . .
p . . . p . . B
. . . p P . P .
N p . . . n B P
. . . . . P . .
P P P Q . . . .
. . K R . . . R
```

| chosen | subpar |
|---|---|
| 15.Bxd4 Nf4 16.Bxg7 Rg8 [17.Bxh6]a [b4]b [18.Na4]a [d5]b [19.e5]a [Ng6]b [20.f4]a [d4]b [21.Rh2]a [Be4]b [22.b3]a [d3]b | 15.Bxd4 Nf4 16.Bxg7 Rg8 [17.Bxh6]a [b4]b [18.Na4]a [d5]b [19.e5]a [Bc6]b [20.Qxf4]a [Bxa4]b [21.Rd2]a [b3]b [22.axb3]a [Bxb3]b |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Bxd4%20Nf4%2016.Bxg7%20Rg8%2017.Bxh6%20b4%2018.Na4%20d5%2019.e5%20Ng6%2020.f4%20d4%2021.Rh2%20Be4%2022.b3%20d3#28) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Bxd4%20Nf4%2016.Bxg7%20Rg8%2017.Bxh6%20b4%2018.Na4%20d5%2019.e5%20Bc6%2020.Qxf4%20Bxa4%2021.Rd2%20b3%2022.axb3%20Bxb3#28) |

## k = 6: a = 923 (0.50) + b = 1122 (0.50)

Holds at 16 of 2500 pairs (0.6%), at 12 positions; recurrence in the report 0.5% (null 95th 0.0%).

Board scan (every ply of the rollouts, lines weighted by count): each latent's phi correlation with each piece on a square and with White to move after the move; 'on X% of plies with it' is the latent's rate given the piece is there.

- a: on at 9.0% of plies; phi with White to move -0.07; top: White P on f3 +0.51 (on 50% of plies with it, 4% without), Black P on f6 +0.40 (on 51% of plies with it, 6% without), Black R on h6 +0.17 (on 50% of plies with it, 8% without), White B on g4 +0.17 (on 46% of plies with it, 8% without)
- b: on at 9.0% of plies; phi with White to move +0.07; top: White P on f3 +0.51 (on 50% of plies with it, 4% without), Black P on f6 +0.40 (on 51% of plies with it, 6% without), White B on h3 +0.18 (on 49% of plies with it, 8% without), White P on h5 +0.17 (on 37% of plies with it, 8% without)
- either: on at 17.8% of plies; phi with White to move -0.00; top: White P on f3 +0.74 (on 98% of plies with it, 8% without), Black P on f6 +0.58 (on 99% of plies with it, 12% without), White B on g4 +0.25 (on 92% of plies with it, 17% without), White B on h3 +0.25 (on 92% of plies with it, 17% without)

### k = 6: a = 923 (0.50) + b = 1122 (0.50): position 43, pair 1

**with**: split at ply 2, White to move: chosen **Ba3** (50% there) vs subpar **fxe4** (48%). `1r1q3r/p2b1kpp/1p3n2/n3Qp2/P2Pp3/4PP2/3N2PP/R1B1KB1R w KQ - 2 18`

```
. r . q . . . r
p . . b . k p p
. p . . . n . .
n . . . Q p . .
P . . P p . . .
. . . . P P . .
. . . N . . P P
R . B . K B . R
```

| chosen | subpar |
|---|---|
| [17...Kf7]b [18.Ba3]a [Re8]b [19.Qf4]a [Kg8]b [20.Bb5]a [Bxb5]b [21.axb5]a exf3 [22.gxf3]a [Nd5]b [23.Qxf5]a [Nxe3]b [24.Qd3]a [Qh4+]b [25.Ke2]a | [17...Kf7]b 18.fxe4 Re8 19.Qf4 Nxe4 20.Nxe4 Rxe4 21.Qf3 Qe7 22.Bd3 Rxd4 23.O-O Rxd3 24.Qxf5+ Kg8 25.Qxd3 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20f6%203.c4%20e5%204.e3%20e4%205.Nfd2%20c6%206.Nc3%20Bb4%207.cxd5%20cxd5%208.f3%20f5%209.Qa4%2B%20Nc6%2010.a3%20Bxc3%2011.bxc3%20Bd7%2012.Qb3%20Rb8%2013.c4%20dxc4%2014.Qxc4%20Nf6%2015.a4%20Na5%2016.Qc5%20b6%2017.Qe5%2B%20Kf7%2018.Ba3%20Re8%2019.Qf4%20Kg8%2020.Bb5%20Bxb5%2021.axb5%20exf3%2022.gxf3%20Nd5%2023.Qxf5%20Nxe3%2024.Qd3%20Qh4%2B%2025.Ke2#33) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20f6%203.c4%20e5%204.e3%20e4%205.Nfd2%20c6%206.Nc3%20Bb4%207.cxd5%20cxd5%208.f3%20f5%209.Qa4%2B%20Nc6%2010.a3%20Bxc3%2011.bxc3%20Bd7%2012.Qb3%20Rb8%2013.c4%20dxc4%2014.Qxc4%20Nf6%2015.a4%20Na5%2016.Qc5%20b6%2017.Qe5%2B%20Kf7%2018.fxe4%20Re8%2019.Qf4%20Nxe4%2020.Nxe4%20Rxe4%2021.Qf3%20Qe7%2022.Bd3%20Rxd4%2023.O-O%20Rxd3%2024.Qxf5%2B%20Kg8%2025.Qxd3#33) |

**without**: split at ply 2, White to move: chosen **Qxb8+** (70% there) vs subpar **Ba3** (24%). `1r2k2r/p2bq1pp/1p3n2/n3Qp2/P2Pp3/4PP2/3N2PP/R1B1KB1R w KQk - 2 18`

```
. r . . k . . r
p . . b q . p p
. p . . . n . .
n . . . Q p . .
P . . P p . . .
. . . . P P . .
. . . N . . P P
R . B . K B . R
```

| chosen | subpar |
|---|---|
| [17...Qe7]b 18.Qxb8+ [Kf7]b [19.Qxh8]a exf3 20.Nxf3 Nb3 21.Bc4+ Be6 22.Bxe6+ Qxe6 23.Rb1 Nxc1 24.Rxc1 Qxe3+ 25.Kd1 | [17...Qe7]b [18.Ba3]a [Qxe5]b [19.dxe5]a [Nd5]b [20.Kf2]a [Nc3]b [21.Bd6]a [Rc8]b [22.Ba6]a [Rc6]b [23.Bb5]a [Nxb5]b [24.axb5]a [Rc2]b [25.Rhd1]a |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20f6%203.c4%20e5%204.e3%20e4%205.Nfd2%20c6%206.Nc3%20Bb4%207.cxd5%20cxd5%208.f3%20f5%209.Qa4%2B%20Nc6%2010.a3%20Bxc3%2011.bxc3%20Bd7%2012.Qb3%20Rb8%2013.c4%20dxc4%2014.Qxc4%20Nf6%2015.a4%20Na5%2016.Qc5%20b6%2017.Qe5%2B%20Qe7%2018.Qxb8%2B%20Kf7%2019.Qxh8%20exf3%2020.Nxf3%20Nb3%2021.Bc4%2B%20Be6%2022.Bxe6%2B%20Qxe6%2023.Rb1%20Nxc1%2024.Rxc1%20Qxe3%2B%2025.Kd1#33) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20f6%203.c4%20e5%204.e3%20e4%205.Nfd2%20c6%206.Nc3%20Bb4%207.cxd5%20cxd5%208.f3%20f5%209.Qa4%2B%20Nc6%2010.a3%20Bxc3%2011.bxc3%20Bd7%2012.Qb3%20Rb8%2013.c4%20dxc4%2014.Qxc4%20Nf6%2015.a4%20Na5%2016.Qc5%20b6%2017.Qe5%2B%20Qe7%2018.Ba3%20Qxe5%2019.dxe5%20Nd5%2020.Kf2%20Nc3%2021.Bd6%20Rc8%2022.Ba6%20Rc6%2023.Bb5%20Nxb5%2024.axb5%20Rc2%2025.Rhd1#33) |

### k = 6: a = 923 (0.50) + b = 1122 (0.50): position 0, pair 2

**with**: split at ply 8, White to move: chosen **Kc2** (56% there) vs subpar **f4** (44%). `2k3r1/ppp5/2n1R1Np/5pbP/8/2P2P1B/P2K3P/6R1 w - - 1 24`

```
. . k . . . r .
p p p . . . . .
. . n . R . N p
. . . . . p b P
. . . . . . . .
. . P . . P . B
P . . K . . . P
. . . . . . R .
```

| chosen | subpar |
|---|---|
| [20...dxc3]b [21.Qxc3]a [Qxc3+]b [22.bxc3]a [Rxd2+]b [23.Kxd2]a [Bg5+]b [24.Kc2]a [Rd8]b [25.Bxf5]a [Kb8]b [26.h4]a [Bf6]b [27.Rxf6]a [a5]b [28.Rf8]a | [20...dxc3]b [21.Qxc3]a [Qxc3+]b [22.bxc3]a [Rxd2+]b [23.Kxd2]a [Bg5+]b 24.f4 Bf6 25.Bxf5 Kb8 26.Kc2 a5 27.Rge1 Ka7 28.Rxf6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.Qxc3%20Qxc3%2B%2022.bxc3%20Rxd2%2B%2023.Kxd2%20Bg5%2B%2024.Kc2%20Rd8%2025.Bxf5%20Kb8%2026.h4%20Bf6%2027.Rxf6%20a5%2028.Rf8#39) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.Qxc3%20Qxc3%2B%2022.bxc3%20Rxd2%2B%2023.Kxd2%20Bg5%2B%2024.f4%20Bf6%2025.Bxf5%20Kb8%2026.Kc2%20a5%2027.Rge1%20Ka7%2028.Rxf6#39) |

**without**: split at ply 8, White to move: chosen **Kc1** (55% there) vs subpar **Ka1** (45%). `2k3r1/ppp5/2R3Np/2q2p1P/8/2b2P1B/Pr5P/1K4R1 w - - 0 24`

```
. . k . . . r .
p p p . . . . .
. . R . . . N p
. . q . . p . P
. . . . . . . .
. . b . . P . B
P r . . . . . P
. K . . . . R .
```

| chosen | subpar |
|---|---|
| [20...dxc3]b [21.Qxc3]a [Bxc3]b [22.Rxc6]a [Rxd2+]b [23.Kb1]a [Rxb2+]b [24.Kc1]a [Qxc6]b 25.Ne7+ [Kb8]b [26.Nxc6+]a [bxc6]b 27.Rxg8+ [Kb7]b [28.Bxf5]a | [20...dxc3]b [21.Qxc3]a [Bxc3]b [22.Rxc6]a [Rxd2+]b [23.Kb1]a [Rxb2+]b [24.Ka1]a [Qxc6]b 25.Ne7+ [Kb8]b [26.Nxc6+]a [bxc6]b 27.Rxg8+ [Kb7]b [28.Bxf5]a |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.Qxc3%20Bxc3%2022.Rxc6%20Rxd2%2B%2023.Kb1%20Rxb2%2B%2024.Kc1%20Qxc6%2025.Ne7%2B%20Kb8%2026.Nxc6%2B%20bxc6%2027.Rxg8%2B%20Kb7%2028.Bxf5#39) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20Nc6%202.Nf3%20f5%203.exf5%20d5%204.g4%20h5%205.Nh4%20Nh6%206.Ng6%20Rg8%207.f3%20e6%208.d4%20exf5%209.gxh5%20Be6%2010.Rg1%20Be7%2011.Qe2%20Nxd4%2012.Qd3%20Bh4%2B%2013.Kd1%20Bf6%2014.c3%20Nc6%2015.Bxh6%20gxh6%2016.Nd2%20Qd6%2017.Kc2%20O-O-O%2018.Re1%20d4%2019.Bh3%20Qc5%2020.Rxe6%20dxc3%2021.Qxc3%20Bxc3%2022.Rxc6%20Rxd2%2B%2023.Kb1%20Rxb2%2B%2024.Ka1%20Qxc6%2025.Ne7%2B%20Kb8%2026.Nxc6%2B%20bxc6%2027.Rxg8%2B%20Kb7%2028.Bxf5#39) |

### k = 6: a = 923 (0.50) + b = 1122 (0.50): position 15, pair 3

**with**: split at ply 8, White to move: chosen **f3** (58% there) vs subpar **Bc5** (42%). `5rk1/B4ppp/p3p3/3p4/3Pn3/P3P3/q4PPP/2R2RK1 w - - 0 21`

```
. . . . . r k .
B . . . . p p p
p . . . p . . .
. . . p . . . .
. . . P n . . .
P . . . P . . .
q . . . . P P P
. . R . . R K .
```

| chosen | subpar |
|---|---|
| 17...Ra7 18.Bb6 Qxc6 19.Bxa7 Qxc2 20.Rac1 Qxa2 [21.f3]a [Nd2]b [22.Rf2]a [Qxa3]b [23.Rd1]a [Nc4]b [24.e4]a [Qe3]b [25.exd5]a | 17...Ra7 18.Bb6 Qxc6 19.Bxa7 Qxc2 20.Rac1 Qxa2 21.Bc5 Nxc5 22.dxc5 Qxa3 23.c6 Rc8 24.c7 Qd6 25.Rc2 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bf4%20d6%203.e3%20Nc6%204.Bb5%20Bd7%205.Bxc6%20Bxc6%206.Nf3%20Bxf3%207.Qxf3%20e6%208.Qxb7%20d5%209.Bxc7%20Qc8%2010.Qc6%2B%20Nd7%2011.Na3%20Be7%2012.Nb5%20O-O%2013.Qc3%20a6%2014.Na3%20Bxa3%2015.bxa3%20Nf6%2016.O-O%20Ne4%2017.Qc6%20Ra7%2018.Bb6%20Qxc6%2019.Bxa7%20Qxc2%2020.Rac1%20Qxa2%2021.f3%20Nd2%2022.Rf2%20Qxa3%2023.Rd1%20Nc4%2024.e4%20Qe3%2025.exd5#33) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bf4%20d6%203.e3%20Nc6%204.Bb5%20Bd7%205.Bxc6%20Bxc6%206.Nf3%20Bxf3%207.Qxf3%20e6%208.Qxb7%20d5%209.Bxc7%20Qc8%2010.Qc6%2B%20Nd7%2011.Na3%20Be7%2012.Nb5%20O-O%2013.Qc3%20a6%2014.Na3%20Bxa3%2015.bxa3%20Nf6%2016.O-O%20Ne4%2017.Qc6%20Ra7%2018.Bb6%20Qxc6%2019.Bxa7%20Qxc2%2020.Rac1%20Qxa2%2021.Bc5%20Nxc5%2022.dxc5%20Qxa3%2023.c6%20Rc8%2024.c7%20Qd6%2025.Rc2#33) |

**without**: split at ply 8, White to move: chosen **Rb3** (52% there) vs subpar **a4** (44%). `r3r1k1/2B2ppp/p3p3/3p4/2nP4/P3P3/P1P2PPP/RR4K1 w - - 0 21`

```
r . . . r . k .
. . B . . p p p
p . . . p . . .
. . . p . . . .
. . n P . . . .
P . . . P . . .
P . P . . P P P
R R . . . . K .
```

| chosen | subpar |
|---|---|
| 17...Nd2 18.Rfd1 Nc4 19.Rdb1 Qe8 20.Qxe8 Rfxe8 21.Rb3 Rec8 22.Bg3 Nd2 23.Rb2 Ne4 24.Rab1 Nc3 25.Re1 | 17...Nd2 18.Rfd1 Nc4 19.Rdb1 Qe8 20.Qxe8 Rfxe8 21.a4 Rec8 22.Bg3 Na3 23.Rb7 Rxc2 24.h4 h5 25.Rab1 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bf4%20d6%203.e3%20Nc6%204.Bb5%20Bd7%205.Bxc6%20Bxc6%206.Nf3%20Bxf3%207.Qxf3%20e6%208.Qxb7%20d5%209.Bxc7%20Qc8%2010.Qc6%2B%20Nd7%2011.Na3%20Be7%2012.Nb5%20O-O%2013.Qc3%20a6%2014.Na3%20Bxa3%2015.bxa3%20Nf6%2016.O-O%20Ne4%2017.Qc6%20Nd2%2018.Rfd1%20Nc4%2019.Rdb1%20Qe8%2020.Qxe8%20Rfxe8%2021.Rb3%20Rec8%2022.Bg3%20Nd2%2023.Rb2%20Ne4%2024.Rab1%20Nc3%2025.Re1#33) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bf4%20d6%203.e3%20Nc6%204.Bb5%20Bd7%205.Bxc6%20Bxc6%206.Nf3%20Bxf3%207.Qxf3%20e6%208.Qxb7%20d5%209.Bxc7%20Qc8%2010.Qc6%2B%20Nd7%2011.Na3%20Be7%2012.Nb5%20O-O%2013.Qc3%20a6%2014.Na3%20Bxa3%2015.bxa3%20Nf6%2016.O-O%20Ne4%2017.Qc6%20Nd2%2018.Rfd1%20Nc4%2019.Rdb1%20Qe8%2020.Qxe8%20Rfxe8%2021.a4%20Rec8%2022.Bg3%20Na3%2023.Rb7%20Rxc2%2024.h4%20h5%2025.Rab1#33) |

### k = 6: a = 923 (0.50) + b = 1122 (0.50): position 14, pair 4

**with**: split at ply 2, Black to move: chosen **Nc6** (48% there) vs subpar **Nxf3** (40%). `2r1k2r/1bqpbpp1/p3p2p/1p4PB/3nP2P/2N1BP2/PPPQ4/2KR3R b k - 0 15`

```
. . r . k . . r
. b q p b p p .
p . . . p . . p
. p . . . . P B
. . . n P . . P
. . N . B P . .
P P P Q . . . .
. . K R . . . R
```

| chosen | subpar |
|---|---|
| [15.Bxh5]a [Nc6]b [16.g6]a [fxg6]b [17.Bxg6+]a [Kd8]b [18.Bf4]a [e5]b [19.Be3]a [Nd4]b [20.Bxd4]a [exd4]b [21.Qxd4]a [Bf6]b [22.Qd3]a [Bxc3]b | [15.Bxh5]a Nxf3 16.Bxf3 b4 17.Na4 Bc6 18.Nb6 Rb8 19.Nc4 Bb5 20.Bf4 Qxc4 21.Bxb8 O-O 22.Bd6 Bxd6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Bxh5%20Nc6%2016.g6%20fxg6%2017.Bxg6%2B%20Kd8%2018.Bf4%20e5%2019.Be3%20Nd4%2020.Bxd4%20exd4%2021.Qxd4%20Bf6%2022.Qd3%20Bxc3#28) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Bxh5%20Nxf3%2016.Bxf3%20b4%2017.Na4%20Bc6%2018.Nb6%20Rb8%2019.Nc4%20Bb5%2020.Bf4%20Qxc4%2021.Bxb8%20O-O%2022.Bd6%20Bxd6#28) |

**without**: split at ply 2, Black to move: chosen **Nf4** (74% there) vs subpar **Ng3** (21%). `2r1k2r/1bqpbpp1/p3p2p/1p4Pn/3BP1BP/2N2P2/PPPQ4/2KR3R b k - 0 15`

```
. . r . k . . r
. b q p b p p .
p . . . p . . p
. p . . . . P n
. . . B P . B P
. . N . . P . .
P P P Q . . . .
. . K R . . . R
```

| chosen | subpar |
|---|---|
| [15.Bxd4]a [Nf4]b [16.Bxg7]a [Rg8]b [17.Bxh6]a [b4]b [18.Ne2]a [Nxe2+]b [19.Qxe2]a [Qa5]b [20.Kb1]a [Bc6]b [21.g6]a [fxg6]b [22.h5]a [gxh5]b | [15.Bxd4]a [Ng3]b [16.Rhg1]a [h5]b [17.Bh3]a [b4]b [18.Ne2]a [Nxe2+]b [19.Qxe2]a [Qf4+]b [20.Kb1]a [Qxh4]b [21.Bxg7]a [Rg8]b [22.Be5]a [Bxg5]b |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Bxd4%20Nf4%2016.Bxg7%20Rg8%2017.Bxh6%20b4%2018.Ne2%20Nxe2%2B%2019.Qxe2%20Qa5%2020.Kb1%20Bc6%2021.g6%20fxg6%2022.h5%20gxh5#28) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20e6%203.d4%20cxd4%204.Nxd4%20Nc6%205.Nc3%20Qc7%206.Be3%20a6%207.Qd2%20Nf6%208.O-O-O%20b5%209.f3%20Bb7%2010.g4%20h6%2011.h4%20Be7%2012.Bh3%20Rc8%2013.g5%20Nh5%2014.Bg4%20Nxd4%2015.Bxd4%20Ng3%2016.Rhg1%20h5%2017.Bh3%20b4%2018.Ne2%20Nxe2%2B%2019.Qxe2%20Qf4%2B%2020.Kb1%20Qxh4%2021.Bxg7%20Rg8%2022.Be5%20Bxg5#28) |

### k = 6: a = 923 (0.50) + b = 1122 (0.50): position 27, pair 5

**with**: split at ply 10, White to move: chosen **Qf2** (60% there) vs subpar **f4** (40%). `2r2rk1/1p1qppbp/p2p1np1/4n3/3BP3/PP3PQ1/3PN1PP/2R2RK1 w - - 1 20`

```
. . r . . r k .
. p . q p p b p
p . . p . n p .
. . . . n . . .
. . . B P . . .
P P . . . P Q .
. . . P N . P P
. . R . . R K .
```

| chosen | subpar |
|---|---|
| 15...Qf5 16.Qg3 Bg7 17.Rac1 O-O [18.f3]a [Rac8]b [19.e4]a [Qd7]b [20.Qf2]a [Qb5]b [21.Nc3]a [Qxb3]b [22.Rb1]a [Qc4]b [23.Rxb7]a | 15...Qf5 16.Qg3 Bg7 17.Rac1 O-O [18.f3]a [Rac8]b [19.e4]a [Qd7]b 20.f4 Nc6 21.Bb2 Nxe4 22.Qe3 Bxb2 23.Qxe4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e3%20c5%202.Qh5%20Nf6%203.Qxc5%20g6%204.Bc4%20d6%205.Qg5%20Nc6%206.a3%20Ne5%207.Bb5%2B%20Bd7%208.Ba4%20Bxa4%209.b3%20Bd7%2010.Bb2%20Qc7%2011.Nc3%20a6%2012.Nge2%20Bb5%2013.O-O%20Bxe2%2014.Nxe2%20Qxc2%2015.Bd4%20Qf5%2016.Qg3%20Bg7%2017.Rac1%20O-O%2018.f3%20Rac8%2019.e4%20Qd7%2020.Qf2%20Qb5%2021.Nc3%20Qxb3%2022.Rb1%20Qc4%2023.Rxb7#29) | [Lichess](https://lichess.org/analysis/pgn/1.e3%20c5%202.Qh5%20Nf6%203.Qxc5%20g6%204.Bc4%20d6%205.Qg5%20Nc6%206.a3%20Ne5%207.Bb5%2B%20Bd7%208.Ba4%20Bxa4%209.b3%20Bd7%2010.Bb2%20Qc7%2011.Nc3%20a6%2012.Nge2%20Bb5%2013.O-O%20Bxe2%2014.Nxe2%20Qxc2%2015.Bd4%20Qf5%2016.Qg3%20Bg7%2017.Rac1%20O-O%2018.f3%20Rac8%2019.e4%20Qd7%2020.f4%20Nc6%2021.Bb2%20Nxe4%2022.Qe3%20Bxb2%2023.Qxe4#29) |

**without**: split at ply 10, White to move: chosen **Qxf5** (56% there) vs subpar **Qc7** (44%). `r3k2r/1p2ppbp/p4np1/4Qq2/5N2/PP2P3/5PPP/2R2RK1 w kq - 3 20`

```
r . . . k . . r
. p . . p p b p
p . . . . n p .
. . . . Q q . .
. . . . . N . .
P P . . P . . .
. . . . . P P P
. . R . . R K .
```

| chosen | subpar |
|---|---|
| 15...Qxd2 16.Nf4 Qc2 17.Bxe5 dxe5 18.Qxe5 Bg7 19.Rac1 Qf5 20.Qxf5 gxf5 21.Rc7 Rb8 22.Rfc1 O-O 23.Rxe7 | 15...Qxd2 16.Nf4 Qc2 17.Bxe5 dxe5 18.Qxe5 Bg7 19.Rac1 Qf5 20.Qc7 O-O 21.Qxb7 e5 22.Ne2 Rab8 23.Qxa6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e3%20c5%202.Qh5%20Nf6%203.Qxc5%20g6%204.Bc4%20d6%205.Qg5%20Nc6%206.a3%20Ne5%207.Bb5%2B%20Bd7%208.Ba4%20Bxa4%209.b3%20Bd7%2010.Bb2%20Qc7%2011.Nc3%20a6%2012.Nge2%20Bb5%2013.O-O%20Bxe2%2014.Nxe2%20Qxc2%2015.Bd4%20Qxd2%2016.Nf4%20Qc2%2017.Bxe5%20dxe5%2018.Qxe5%20Bg7%2019.Rac1%20Qf5%2020.Qxf5%20gxf5%2021.Rc7%20Rb8%2022.Rfc1%20O-O%2023.Rxe7#29) | [Lichess](https://lichess.org/analysis/pgn/1.e3%20c5%202.Qh5%20Nf6%203.Qxc5%20g6%204.Bc4%20d6%205.Qg5%20Nc6%206.a3%20Ne5%207.Bb5%2B%20Bd7%208.Ba4%20Bxa4%209.b3%20Bd7%2010.Bb2%20Qc7%2011.Nc3%20a6%2012.Nge2%20Bb5%2013.O-O%20Bxe2%2014.Nxe2%20Qxc2%2015.Bd4%20Qxd2%2016.Nf4%20Qc2%2017.Bxe5%20dxe5%2018.Qxe5%20Bg7%2019.Rac1%20Qf5%2020.Qc7%20O-O%2021.Qxb7%20e5%2022.Ne2%20Rab8%2023.Qxa6#29) |

### k = 6: a = 923 (0.50) + b = 1122 (0.50): position 40, pair 6

**with**: split at ply 9, Black to move: chosen **f6** (50% there) vs subpar **Kf8** (38%). `r7/pp1nkpp1/2p1p3/4P1Q1/3NB3/3P4/PPP3K1/R7 b - - 2 28`

```
r . . . . . . .
p p . n k p p .
. . p . p . . .
. . . . P . Q .
. . . N B . . .
. . . P . . . .
P P P . . . K .
R . . . . . . .
```

| chosen | subpar |
|---|---|
| 24...Bxg5 25.fxg5 Qxg5 26.Qxg5 Ne3+ 27.Qxe3 Ke7 28.Qg5+ [f6]a [29.Qxg7+]b [Kd8]a [30.Nxe6+]b [Kc8]a [31.Qe7]b [Nxe5]a 32.Qc7# | 24...Bxg5 25.fxg5 Qxg5 26.Qxg5 Ne3+ 27.Qxe3 Ke7 28.Qg5+ Kf8 29.Rh1 Kg8 30.Bh7+ Kf8 31.Bg6 Kg8 32.Qh5 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.Nf3%20d5%203.d3%20Bg4%204.h3%20Bh5%205.Nc3%20e6%206.g4%20Bg6%207.h4%20h5%208.Ne5%20Ne7%209.Nxg6%20Nxg6%2010.gxh5%20Nxh4%2011.Qg4%20Ng6%2012.Bg2%20Ne5%2013.Qg3%20Ned7%2014.Bf4%20d4%2015.Ne2%20Qa5%2B%2016.Kf1%20Rxh5%2017.Rxh5%20Qxh5%2018.e5%20Nb6%2019.Nxd4%20Nd5%2020.Bg5%20Nd7%2021.Bf3%20Qg6%2022.Be4%20Qh5%2023.Kg2%20Be7%2024.f4%20Bxg5%2025.fxg5%20Qxg5%2026.Qxg5%20Ne3%2B%2027.Qxe3%20Ke7%2028.Qg5%2B%20f6%2029.Qxg7%2B%20Kd8%2030.Nxe6%2B%20Kc8%2031.Qe7%20Nxe5%2032.Qc7%23#47) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.Nf3%20d5%203.d3%20Bg4%204.h3%20Bh5%205.Nc3%20e6%206.g4%20Bg6%207.h4%20h5%208.Ne5%20Ne7%209.Nxg6%20Nxg6%2010.gxh5%20Nxh4%2011.Qg4%20Ng6%2012.Bg2%20Ne5%2013.Qg3%20Ned7%2014.Bf4%20d4%2015.Ne2%20Qa5%2B%2016.Kf1%20Rxh5%2017.Rxh5%20Qxh5%2018.e5%20Nb6%2019.Nxd4%20Nd5%2020.Bg5%20Nd7%2021.Bf3%20Qg6%2022.Be4%20Qh5%2023.Kg2%20Be7%2024.f4%20Bxg5%2025.fxg5%20Qxg5%2026.Qxg5%20Ne3%2B%2027.Qxe3%20Ke7%2028.Qg5%2B%20Kf8%2029.Rh1%20Kg8%2030.Bh7%2B%20Kf8%2031.Bg6%20Kg8%2032.Qh5#47) |

**without**: split at ply 9, Black to move: chosen **exd5** (53% there) vs subpar **cxd5** (47%). `r3k3/pp3pp1/2p1p3/3Bn1P1/3N4/3P2K1/PPP5/7R b q - 0 28`

```
r . . . k . . .
p p . . . p p .
. . p . p . . .
. . . B n . P .
. . . N . . . .
. . . P . . K .
P P P . . . . .
. . . . . . . R
```

| chosen | subpar |
|---|---|
| 24...Bxg5 25.fxg5 Nxe5 26.Rh1 Qg4 27.Bxd5 Qxg3+ 28.Kxg3 exd5 29.Re1 [f6]a 30.gxf6 [gxf6]a [31.Nf5]b [Kd7]a [32.d4]b | 24...Bxg5 25.fxg5 Nxe5 26.Rh1 Qg4 27.Bxd5 Qxg3+ 28.Kxg3 cxd5 29.Rh8+ Ke7 30.Rxa8 a6 31.Rb8 b5 32.Rb7+ |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.Nf3%20d5%203.d3%20Bg4%204.h3%20Bh5%205.Nc3%20e6%206.g4%20Bg6%207.h4%20h5%208.Ne5%20Ne7%209.Nxg6%20Nxg6%2010.gxh5%20Nxh4%2011.Qg4%20Ng6%2012.Bg2%20Ne5%2013.Qg3%20Ned7%2014.Bf4%20d4%2015.Ne2%20Qa5%2B%2016.Kf1%20Rxh5%2017.Rxh5%20Qxh5%2018.e5%20Nb6%2019.Nxd4%20Nd5%2020.Bg5%20Nd7%2021.Bf3%20Qg6%2022.Be4%20Qh5%2023.Kg2%20Be7%2024.f4%20Bxg5%2025.fxg5%20Nxe5%2026.Rh1%20Qg4%2027.Bxd5%20Qxg3%2B%2028.Kxg3%20exd5%2029.Re1%20f6%2030.gxf6%20gxf6%2031.Nf5%20Kd7%2032.d4#47) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c6%202.Nf3%20d5%203.d3%20Bg4%204.h3%20Bh5%205.Nc3%20e6%206.g4%20Bg6%207.h4%20h5%208.Ne5%20Ne7%209.Nxg6%20Nxg6%2010.gxh5%20Nxh4%2011.Qg4%20Ng6%2012.Bg2%20Ne5%2013.Qg3%20Ned7%2014.Bf4%20d4%2015.Ne2%20Qa5%2B%2016.Kf1%20Rxh5%2017.Rxh5%20Qxh5%2018.e5%20Nb6%2019.Nxd4%20Nd5%2020.Bg5%20Nd7%2021.Bf3%20Qg6%2022.Be4%20Qh5%2023.Kg2%20Be7%2024.f4%20Bxg5%2025.fxg5%20Nxe5%2026.Rh1%20Qg4%2027.Bxd5%20Qxg3%2B%2028.Kxg3%20cxd5%2029.Rh8%2B%20Ke7%2030.Rxa8%20a6%2031.Rb8%20b5%2032.Rb7%2B#47) |

## k = 6: a = 2247 (0.50) + b = 3874 (0.50)

Holds at 21 of 2500 pairs (0.8%), at 10 positions; recurrence in the report 0.6% (null 95th 0.0%).

Board scan (every ply of the rollouts, lines weighted by count): each latent's phi correlation with each piece on a square and with White to move after the move; 'on X% of plies with it' is the latent's rate given the piece is there.

- a: on at 7.9% of plies; phi with White to move +0.02; top: Black R on b8 +0.54 (on 58% of plies with it, 4% without), White R on b1 +0.50 (on 61% of plies with it, 4% without), Black N on b6 +0.28 (on 49% of plies with it, 7% without), White Q on d3 +0.20 (on 36% of plies with it, 7% without)
- b: on at 8.6% of plies; phi with White to move +0.01; top: Black R on b8 +0.53 (on 60% of plies with it, 4% without), White R on b1 +0.49 (on 62% of plies with it, 5% without), Black N on b6 +0.31 (on 55% of plies with it, 7% without), White Q on h6 +0.19 (on 42% of plies with it, 8% without)
- either: on at 14.8% of plies; phi with White to move +0.01; top: Black R on b8 +0.67 (on 98% of plies with it, 8% without), White R on b1 +0.59 (on 98% of plies with it, 9% without), Black N on b6 +0.31 (on 75% of plies with it, 13% without), White Q on d3 +0.26 (on 63% of plies with it, 13% without)

### k = 6: a = 2247 (0.50) + b = 3874 (0.50): position 32, pair 1

**with**: split at ply 10, White to move: chosen **Rb1** (55% there) vs subpar **a3** (45%). `r3r1k1/ppp2ppp/2n2q2/7b/1bPP4/5N1P/PB2BPP1/R2Q1RK1 w - - 5 17`

```
r . . . r . k .
p p p . . p p p
. . n . . q . .
. . . . . . . b
. b P P . . . .
. . . . . N . P
P B . . B P P .
R . . Q . R K .
```

| chosen | subpar |
|---|---|
| 12...Bd6 13.O-O O-O 14.c4 Re8 15.Re1 Bb4 16.Rf1 Qf6 [17.Rb1]a [Rad8]b [18.d5]a [Qf4]b [19.Bc1]a [Qd6]b [20.Bg5]a | 12...Bd6 13.O-O O-O 14.c4 Re8 15.Re1 Bb4 16.Rf1 Qf6 17.a3 Bd6 18.Re1 Rad8 19.Qb3 Bxf3 20.Bxf3 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20d5%202.exd5%20Nf6%203.Nc3%20Nxd5%204.Bc4%20Nxc3%205.bxc3%20Nc6%206.Bb2%20e5%207.Nf3%20Bg4%208.h3%20Bh5%209.Be2%20Bc5%2010.d4%20exd4%2011.cxd4%20Bb4%2B%2012.c3%20Bd6%2013.O-O%20O-O%2014.c4%20Re8%2015.Re1%20Bb4%2016.Rf1%20Qf6%2017.Rb1%20Rad8%2018.d5%20Qf4%2019.Bc1%20Qd6%2020.Bg5#23) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20d5%202.exd5%20Nf6%203.Nc3%20Nxd5%204.Bc4%20Nxc3%205.bxc3%20Nc6%206.Bb2%20e5%207.Nf3%20Bg4%208.h3%20Bh5%209.Be2%20Bc5%2010.d4%20exd4%2011.cxd4%20Bb4%2B%2012.c3%20Bd6%2013.O-O%20O-O%2014.c4%20Re8%2015.Re1%20Bb4%2016.Rf1%20Qf6%2017.a3%20Bd6%2018.Re1%20Rad8%2019.Qb3%20Bxf3%2020.Bxf3#23) |

**without**: split at ply 10, White to move: chosen **Qc2** (60% there) vs subpar **Qa4** (40%). `r2qr1k1/ppp2ppp/1b6/n6b/3P4/1QP2N1P/PB2BPP1/3RR1K1 w - - 9 17`

```
r . . q r . k .
p p p . . p p p
. b . . . . . .
n . . . . . . b
. . . P . . . .
. Q P . . N . P
P B . . B P P .
. . . R R . K .
```

| chosen | subpar |
|---|---|
| 12...Ba5 13.O-O O-O 14.Re1 Re8 15.Qb3 Bb6 16.Rad1 Na5 17.Qc2 Bg6 18.Bd3 Rxe1+ 19.Rxe1 c5 20.Bxg6 | 12...Ba5 13.O-O O-O 14.Re1 Re8 15.Qb3 Bb6 16.Rad1 Na5 17.Qa4 c6 18.c4 Bc7 19.d5 Qd6 20.g3 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20d5%202.exd5%20Nf6%203.Nc3%20Nxd5%204.Bc4%20Nxc3%205.bxc3%20Nc6%206.Bb2%20e5%207.Nf3%20Bg4%208.h3%20Bh5%209.Be2%20Bc5%2010.d4%20exd4%2011.cxd4%20Bb4%2B%2012.c3%20Ba5%2013.O-O%20O-O%2014.Re1%20Re8%2015.Qb3%20Bb6%2016.Rad1%20Na5%2017.Qc2%20Bg6%2018.Bd3%20Rxe1%2B%2019.Rxe1%20c5%2020.Bxg6#23) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20d5%202.exd5%20Nf6%203.Nc3%20Nxd5%204.Bc4%20Nxc3%205.bxc3%20Nc6%206.Bb2%20e5%207.Nf3%20Bg4%208.h3%20Bh5%209.Be2%20Bc5%2010.d4%20exd4%2011.cxd4%20Bb4%2B%2012.c3%20Ba5%2013.O-O%20O-O%2014.Re1%20Re8%2015.Qb3%20Bb6%2016.Rad1%20Na5%2017.Qa4%20c6%2018.c4%20Bc7%2019.d5%20Qd6%2020.g3#23) |

### k = 6: a = 2247 (0.50) + b = 3874 (0.50): position 25, pair 2

**with**: split at ply 2, Black to move: chosen **Kxf8** (59% there) vs subpar **Rxf8** (41%). `1r3R2/pb4kp/1p4p1/2pnP3/4B3/2P4P/PP1N2P1/R5K1 b - - 0 21`

```
. r . . . R . .
p b . . . . k p
. p . . . . p .
. . p n P . . .
. . . . B . . .
. . P . . . . P
P P . N . . P .
R . . . . . K .
```

| chosen | subpar |
|---|---|
| [21.Rxf8]b [Kxf8]a [22.Rf1+]b [Ke7]a [23.Nc4]b [Ba6]a [24.Bxd5]b [Bxc4]a [25.Bxc4]b Rd8 26.Rf7+ Ke8 27.Rxh7 Rd1+ 28.Kh2 Rd2 | [21.Rxf8]b Rxf8 22.Rf1 Rxf1+ 23.Kxf1 Kf7 24.Kf2 Ke6 25.Nf3 h6 26.Bxg6 Nf4 27.Bc2 Bxf3 28.Kxf3 Kxe5 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.Rxf8%20Kxf8%2022.Rf1%2B%20Ke7%2023.Nc4%20Ba6%2024.Bxd5%20Bxc4%2025.Bxc4%20Rd8%2026.Rf7%2B%20Ke8%2027.Rxh7%20Rd1%2B%2028.Kh2%20Rd2#40) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.Rxf8%20Rxf8%2022.Rf1%20Rxf1%2B%2023.Kxf1%20Kf7%2024.Kf2%20Ke6%2025.Nf3%20h6%2026.Bxg6%20Nf4%2027.Bc2%20Bxf3%2028.Kxf3%20Kxe5#40) |

**without**: split at ply 2, Black to move: chosen **Ba6** (40% there) vs subpar **Nf4** (34%). `1r3r2/pb4kp/1p4p1/2pnP3/2N1B3/2P4P/PP4P1/R4RK1 b - - 4 21`

```
. r . . . r . .
p b . . . . k p
. p . . . . p .
. . p n P . . .
. . N . B . . .
. . P . . . . P
P P . . . . P .
R . . . . R K .
```

| chosen | subpar |
|---|---|
| [21.Nc4]b [Ba6]a [22.Bxd5]b [Rxf1+]a [23.Rxf1]b Rd8 24.Rf7+ Kh6 25.Rxa7 Bxc4 26.Bxc4 Rd1+ 27.Kh2 Rd2 28.e6 Rxb2 | [21.Nc4]b [Nf4]a [22.Bxb7]b Rxb7 23.Nd6 Re7 24.Rae1 Nd3 25.Rxf8 Kxf8 26.Rf1+ Kg7 27.Nc8 Rxe5 28.Nxa7 Nxb2 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.Nc4%20Ba6%2022.Bxd5%20Rxf1%2B%2023.Rxf1%20Rd8%2024.Rf7%2B%20Kh6%2025.Rxa7%20Bxc4%2026.Bxc4%20Rd1%2B%2027.Kh2%20Rd2%2028.e6%20Rxb2#40) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20Nf6%202.Bg5%20d5%203.e3%20Nbd7%204.Nd2%20e6%205.Ngf3%20c5%206.c3%20Be7%207.Bd3%20O-O%208.O-O%20b6%209.h3%20Bb7%2010.Ne5%20Nxe5%2011.dxe5%20Nd7%2012.Bxe7%20Qxe7%2013.f4%20f6%2014.exf6%20Nxf6%2015.e4%20e5%2016.exd5%20Nxd5%2017.Qh5%20g6%2018.Qxe5%20Qxe5%2019.fxe5%20Kg7%2020.Be4%20Rab8%2021.Nc4%20Nf4%2022.Bxb7%20Rxb7%2023.Nd6%20Re7%2024.Rae1%20Nd3%2025.Rxf8%20Kxf8%2026.Rf1%2B%20Kg7%2027.Nc8%20Rxe5%2028.Nxa7%20Nxb2#40) |

### k = 6: a = 2247 (0.50) + b = 3874 (0.50): position 28, pair 3

**with**: split at ply 10, Black to move: chosen **Rb7** (60% there) vs subpar **Nxe3** (40%). `2r5/r4pk1/p1p1p1p1/2Pn3p/5q2/Q2RN2P/1P3PP1/R5K1 b - - 1 31`

```
. . r . . . . .
r . . . . p k .
p . p . p . p .
. . P n . . . p
. . . . . q . .
Q . . R N . . P
. P . . . P P .
R . . . . . K .
```

| chosen | subpar |
|---|---|
| 27.Ne5 Rc8 28.Ng4 Qf4 29.Qa3 Kg7 30.Rd3 h5 31.Ne3 [Rb7]a [32.Nxd5]b [cxd5]a [33.c6]b [Rxc6]a [34.Rf3]b [Qe5]a | 27.Ne5 Rc8 28.Ng4 Qf4 29.Qa3 Kg7 30.Rd3 h5 31.Ne3 Nxe3 32.Rxe3 Rd8 33.Rf3 Qe5 34.Qb4 Rad7 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20g6%202.d4%20Bg7%203.c3%20d5%204.e5%20c5%205.Nf3%20Nc6%206.Bb5%20Qb6%207.a4%20a6%208.Bxc6%2B%20bxc6%209.a5%20Qb5%2010.Na3%20Qxa5%2011.O-O%20Qc7%2012.Bf4%20Bg4%2013.h3%20Bxf3%2014.Qxf3%20e6%2015.c4%20Ne7%2016.dxc5%20Bxe5%2017.Bxe5%20Qxe5%2018.cxd5%20Qxd5%2019.Qf6%20Rf8%2020.Rfd1%20Qf5%2021.Qd4%20Nd5%2022.Nc4%20Ke7%2023.Nb6%20Ra7%2024.Qh4%2B%20Qf6%2025.Qg3%20Rd8%2026.Nc4%20Kf8%2027.Ne5%20Rc8%2028.Ng4%20Qf4%2029.Qa3%20Kg7%2030.Rd3%20h5%2031.Ne3%20Rb7%2032.Nxd5%20cxd5%2033.c6%20Rxc6%2034.Rf3%20Qe5#52) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20g6%202.d4%20Bg7%203.c3%20d5%204.e5%20c5%205.Nf3%20Nc6%206.Bb5%20Qb6%207.a4%20a6%208.Bxc6%2B%20bxc6%209.a5%20Qb5%2010.Na3%20Qxa5%2011.O-O%20Qc7%2012.Bf4%20Bg4%2013.h3%20Bxf3%2014.Qxf3%20e6%2015.c4%20Ne7%2016.dxc5%20Bxe5%2017.Bxe5%20Qxe5%2018.cxd5%20Qxd5%2019.Qf6%20Rf8%2020.Rfd1%20Qf5%2021.Qd4%20Nd5%2022.Nc4%20Ke7%2023.Nb6%20Ra7%2024.Qh4%2B%20Qf6%2025.Qg3%20Rd8%2026.Nc4%20Kf8%2027.Ne5%20Rc8%2028.Ng4%20Qf4%2029.Qa3%20Kg7%2030.Rd3%20h5%2031.Ne3%20Nxe3%2032.Rxe3%20Rd8%2033.Rf3%20Qe5%2034.Qb4%20Rad7#52) |

**without**: split at ply 10, Black to move: chosen **a5** (65% there) vs subpar **Rad7** (35%). `3r4/r5kp/p1p1ppp1/2qn4/2N5/1P3RQP/5PP1/3R2K1 b - - 0 31`

```
. . . r . . . .
r . . . . . k p
p . p . p p p .
. . q n . . . .
. . N . . . . .
. P . . . R Q P
. . . . . P P .
. . . R . . K .
```

| chosen | subpar |
|---|---|
| 27.Ra3 Kg7 28.Rf3 Qe7 29.Qe5+ f6 30.Qg3 Qxc5 31.b3 a5 32.h4 a4 33.h5 axb3 34.hxg6 hxg6 | 27.Ra3 Kg7 28.Rf3 Qe7 29.Qe5+ f6 30.Qg3 Qxc5 31.b3 Rad7 32.Re1 e5 33.h4 Nf4 34.h5 Rd1 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20g6%202.d4%20Bg7%203.c3%20d5%204.e5%20c5%205.Nf3%20Nc6%206.Bb5%20Qb6%207.a4%20a6%208.Bxc6%2B%20bxc6%209.a5%20Qb5%2010.Na3%20Qxa5%2011.O-O%20Qc7%2012.Bf4%20Bg4%2013.h3%20Bxf3%2014.Qxf3%20e6%2015.c4%20Ne7%2016.dxc5%20Bxe5%2017.Bxe5%20Qxe5%2018.cxd5%20Qxd5%2019.Qf6%20Rf8%2020.Rfd1%20Qf5%2021.Qd4%20Nd5%2022.Nc4%20Ke7%2023.Nb6%20Ra7%2024.Qh4%2B%20Qf6%2025.Qg3%20Rd8%2026.Nc4%20Kf8%2027.Ra3%20Kg7%2028.Rf3%20Qe7%2029.Qe5%2B%20f6%2030.Qg3%20Qxc5%2031.b3%20a5%2032.h4%20a4%2033.h5%20axb3%2034.hxg6%20hxg6#52) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20g6%202.d4%20Bg7%203.c3%20d5%204.e5%20c5%205.Nf3%20Nc6%206.Bb5%20Qb6%207.a4%20a6%208.Bxc6%2B%20bxc6%209.a5%20Qb5%2010.Na3%20Qxa5%2011.O-O%20Qc7%2012.Bf4%20Bg4%2013.h3%20Bxf3%2014.Qxf3%20e6%2015.c4%20Ne7%2016.dxc5%20Bxe5%2017.Bxe5%20Qxe5%2018.cxd5%20Qxd5%2019.Qf6%20Rf8%2020.Rfd1%20Qf5%2021.Qd4%20Nd5%2022.Nc4%20Ke7%2023.Nb6%20Ra7%2024.Qh4%2B%20Qf6%2025.Qg3%20Rd8%2026.Nc4%20Kf8%2027.Ra3%20Kg7%2028.Rf3%20Qe7%2029.Qe5%2B%20f6%2030.Qg3%20Qxc5%2031.b3%20Rad7%2032.Re1%20e5%2033.h4%20Nf4%2034.h5%20Rd1#52) |

### k = 6: a = 2247 (0.50) + b = 3874 (0.50): position 34, pair 4

**with**: split at ply 10, White to move: chosen **Rb1** (60% there) vs subpar **Ne4** (40%). `5rk1/1pp1bppp/2n1p3/1p1q4/3P4/2PQ4/3N1PPP/4R1K1 w - - 2 19`

```
. . . . . r k .
. p p . b p p p
. . n . p . . .
. p . q . . . .
. . . P . . . .
. . P Q . . . .
. . . N . P P P
. . . . R . K .
```

| chosen | subpar |
|---|---|
| 14...Qd5 15.Re1 O-O 16.Qd3 Rxa3 17.Rxa3 Bxa3 18.Nd2 Be7 [19.Rb1]a [b4]b [20.c4]a [Qxd4]b [21.Qe2]a [Rd8]b [22.Ne4]a | 14...Qd5 15.Re1 O-O 16.Qd3 Rxa3 17.Rxa3 Bxa3 18.Nd2 Be7 19.Ne4 Ra8 20.h3 b4 21.c4 Qxd4 22.Qg3 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20Qd5%2015.Re1%20O-O%2016.Qd3%20Rxa3%2017.Rxa3%20Bxa3%2018.Nd2%20Be7%2019.Rb1%20b4%2020.c4%20Qxd4%2021.Qe2%20Rd8%2022.Ne4#27) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20Qd5%2015.Re1%20O-O%2016.Qd3%20Rxa3%2017.Rxa3%20Bxa3%2018.Nd2%20Be7%2019.Ne4%20Ra8%2020.h3%20b4%2021.c4%20Qxd4%2022.Qg3#27) |

**without**: split at ply 10, White to move: chosen **Qxa8** (50% there) vs subpar **Qb2** (40%). `q4rk1/1pp2ppp/2n1p3/8/1P1PR3/Q4N2/5PPP/6K1 w - - 1 19`

```
q . . . . r k .
. p p . . p p p
. . n . p . . .
. . . . . . . .
. P . P R . . .
Q . . . . N . .
. . . . . P P P
. . . . . . K .
```

| chosen | subpar |
|---|---|
| 14...O-O 15.Qb3 Rxa3 16.Rxa3 Bxa3 17.Qxa3 b4 18.cxb4 Qa8 19.Qxa8 Rxa8 20.g3 Nxb4 21.d5 Nxd5 22.Rc4 | 14...O-O 15.Qb3 Rxa3 16.Rxa3 Bxa3 17.Qxa3 b4 18.cxb4 Qa8 19.Qb2 Ne7 20.Re1 Nd5 21.b5 Qa5 22.Ra1 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20O-O%2015.Qb3%20Rxa3%2016.Rxa3%20Bxa3%2017.Qxa3%20b4%2018.cxb4%20Qa8%2019.Qxa8%20Rxa8%2020.g3%20Nxb4%2021.d5%20Nxd5%2022.Rc4#27) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Bf4%20Nc6%203.e3%20Bf5%204.Nf3%20e6%205.a3%20Nf6%206.c4%20Be7%207.cxd5%20Nxd5%208.Bb5%20Nxf4%209.O-O%20Nd5%2010.Re1%20a6%2011.e4%20Bxe4%2012.Rxe4%20axb5%2013.Nc3%20Nxc3%2014.bxc3%20O-O%2015.Qb3%20Rxa3%2016.Rxa3%20Bxa3%2017.Qxa3%20b4%2018.cxb4%20Qa8%2019.Qb2%20Ne7%2020.Re1%20Nd5%2021.b5%20Qa5%2022.Ra1#27) |

### k = 6: a = 2247 (0.50) + b = 3874 (0.50): position 29, pair 5

**with**: split at ply 4, Black to move: chosen **Rb8** (57% there) vs subpar **Ba6+** (38%). `r1b1k2r/p2ppp1p/5np1/8/3Q4/q4B2/P1P2PPP/R4K1R b kq - 3 16`

```
r . b . k . . r
p . . p p p . p
. . . . . n p .
. . . . . . . .
. . . Q . . . .
q . . . . B . .
P . P . . P P P
R . . . . K . R
```

| chosen | subpar |
|---|---|
| 15.Qd4 Nf6 16.Bf3 [Rb8]a [17.g3]b [O-O]a [18.Kg2]b [Bb7]a [19.Bxb7]b [Rxb7]a [20.Rhe1]b [Qd6]a [21.Qa4]b [Rc8]a [22.Rad1]b [Qc6+]a | 15.Qd4 Nf6 16.Bf3 Ba6+ 17.Kg1 Rc8 18.Re1 O-O 19.h4 Rxc2 20.h5 Rc1 21.Rxc1 Qxc1+ 22.Kh2 Qh6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20g6%205.Nc3%20Bg7%206.Be3%20Nf6%207.Nxc6%20bxc6%208.e5%20Ng8%209.Bd4%20c5%2010.Bxc5%20Qc7%2011.Ba3%20Bxe5%2012.Be2%20Bxc3%2B%2013.bxc3%20Qxc3%2B%2014.Kf1%20Qxa3%2015.Qd4%20Nf6%2016.Bf3%20Rb8%2017.g3%20O-O%2018.Kg2%20Bb7%2019.Bxb7%20Rxb7%2020.Rhe1%20Qd6%2021.Qa4%20Rc8%2022.Rad1%20Qc6%2B#28) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20g6%205.Nc3%20Bg7%206.Be3%20Nf6%207.Nxc6%20bxc6%208.e5%20Ng8%209.Bd4%20c5%2010.Bxc5%20Qc7%2011.Ba3%20Bxe5%2012.Be2%20Bxc3%2B%2013.bxc3%20Qxc3%2B%2014.Kf1%20Qxa3%2015.Qd4%20Nf6%2016.Bf3%20Ba6%2B%2017.Kg1%20Rc8%2018.Re1%20O-O%2019.h4%20Rxc2%2020.h5%20Rc1%2021.Rxc1%20Qxc1%2B%2022.Kh2%20Qh6#28) |

**without**: split at ply 4, Black to move: chosen **Rc8** (54% there) vs subpar **Rd8** (45%). `r3k1nr/p2ppp1p/b5p1/8/8/q4B2/P1P2PPP/R2Q2KR b kq - 3 16`

```
r . . . k . n r
p . . p p p . p
b . . . . . p .
. . . . . . . .
. . . . . . . .
q . . . . B . .
P . P . . P P P
R . . Q . . K R
```

| chosen | subpar |
|---|---|
| 15.Bf3 Ba6+ 16.Kg1 Rc8 17.h4 Nf6 18.h5 g5 19.h6 O-O 20.Qd2 g4 21.Qg5+ Kh8 22.Qg7# | 15.Bf3 Ba6+ 16.Kg1 Rd8 17.Qd4 Nf6 18.h4 O-O 19.h5 d5 20.hxg6 fxg6 21.Re1 Qd6 22.Qxa7 e5 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20g6%205.Nc3%20Bg7%206.Be3%20Nf6%207.Nxc6%20bxc6%208.e5%20Ng8%209.Bd4%20c5%2010.Bxc5%20Qc7%2011.Ba3%20Bxe5%2012.Be2%20Bxc3%2B%2013.bxc3%20Qxc3%2B%2014.Kf1%20Qxa3%2015.Bf3%20Ba6%2B%2016.Kg1%20Rc8%2017.h4%20Nf6%2018.h5%20g5%2019.h6%20O-O%2020.Qd2%20g4%2021.Qg5%2B%20Kh8%2022.Qg7%23#28) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20Nc6%203.d4%20cxd4%204.Nxd4%20g6%205.Nc3%20Bg7%206.Be3%20Nf6%207.Nxc6%20bxc6%208.e5%20Ng8%209.Bd4%20c5%2010.Bxc5%20Qc7%2011.Ba3%20Bxe5%2012.Be2%20Bxc3%2B%2013.bxc3%20Qxc3%2B%2014.Kf1%20Qxa3%2015.Bf3%20Ba6%2B%2016.Kg1%20Rd8%2017.Qd4%20Nf6%2018.h4%20O-O%2019.h5%20d5%2020.hxg6%20fxg6%2021.Re1%20Qd6%2022.Qxa7%20e5#28) |

### k = 6: a = 2247 (0.50) + b = 3874 (0.50): position 8, pair 6

**with**: split at ply 9, White to move: chosen **Rb2** (56% there) vs subpar **Rc2** (33%). `r3kb1r/p2n1ppp/4p3/8/2pP4/P1P1PN1P/R2N1PP1/2n1KB1R w Kkq - 0 16`

```
r . . . k b . r
p . . n . p p p
. . . . p . . .
. . . . . . . .
. . p P . . . .
P . P . P N . P
R . . N . P P .
. . n . K B . R
```

| chosen | subpar |
|---|---|
| 12.Nbd2 Nxc1 13.Qxa4+ b5 14.Qxb5+ Qd7 15.Qxd7+ Nxd7 [16.Rb2]a [Nd3+]b [17.Bxd3]a [cxd3]b [18.Nc4]a [Rc8]b [19.Nfd2]a [Nb6]b | 12.Nbd2 Nxc1 13.Qxa4+ b5 14.Qxb5+ Qd7 15.Qxd7+ Nxd7 16.Rc2 Nd3+ 17.Bxd3 cxd3 18.Rc1 Bxa3 19.Ra1 Bb2 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Nbd2%20Nxc1%2013.Qxa4%2B%20b5%2014.Qxb5%2B%20Qd7%2015.Qxd7%2B%20Nxd7%2016.Rb2%20Nd3%2B%2017.Bxd3%20cxd3%2018.Nc4%20Rc8%2019.Nfd2%20Nb6#22) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Nbd2%20Nxc1%2013.Qxa4%2B%20b5%2014.Qxb5%2B%20Qd7%2015.Qxd7%2B%20Nxd7%2016.Rc2%20Nd3%2B%2017.Bxd3%20cxd3%2018.Rc1%20Bxa3%2019.Ra1%20Bb2#22) |

**without**: split at ply 9, White to move: chosen **Qb2** (50% there) vs subpar **O-O** (38%). `2rqkb1r/pp3ppp/3np3/8/b2P4/P1PBPN1P/R4PP1/1NQ1K2R w Kk - 3 16`

```
. . r q k b . r
p p . . . p p p
. . . n p . . .
. . . . . . . .
b . . P . . . .
P . P B P N . P
R . . . . P P .
. N Q . K . . R
```

| chosen | subpar |
|---|---|
| 12.Qb2 [Ne4]b 13.Bxc4 [Nxc1]b 14.Qxc1 Rc8 15.Bd3 Nd6 [16.Qb2]a Be7 17.O-O O-O 18.Nbd2 [b5]b [19.Rc1]a [a6]b | 12.Qb2 [Ne4]b 13.Bxc4 [Nxc1]b 14.Qxc1 Rc8 15.Bd3 Nd6 16.O-O Be7 17.Qb2 O-O 18.Nbd2 Nb5 [19.Rc1]a Qa5 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Qb2%20Ne4%2013.Bxc4%20Nxc1%2014.Qxc1%20Rc8%2015.Bd3%20Nd6%2016.Qb2%20Be7%2017.O-O%20O-O%2018.Nbd2%20b5%2019.Rc1%20a6#22) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Qb2%20Ne4%2013.Bxc4%20Nxc1%2014.Qxc1%20Rc8%2015.Bd3%20Nd6%2016.O-O%20Be7%2017.Qb2%20O-O%2018.Nbd2%20Nb5%2019.Rc1%20Qa5#22) |

## k = 6: a = 416 (0.50) + b = 1455 (0.50)

Holds at 21 of 2500 pairs (0.8%), at 11 positions; recurrence in the report 1.0% (null 95th 0.1%).

Board scan (every ply of the rollouts, lines weighted by count): each latent's phi correlation with each piece on a square and with White to move after the move; 'on X% of plies with it' is the latent's rate given the piece is there.

- a: on at 9.3% of plies; phi with White to move -0.09; top: White N on d2 +0.59 (on 56% of plies with it, 3% without), Black N on d7 +0.46 (on 59% of plies with it, 6% without), Black N on f6 +0.24 (on 25% of plies with it, 6% without), Black P on b6 +0.20 (on 28% of plies with it, 7% without)
- b: on at 9.4% of plies; phi with White to move +0.09; top: White N on d2 +0.58 (on 55% of plies with it, 3% without), Black N on d7 +0.48 (on 61% of plies with it, 6% without), Black P on b6 +0.22 (on 29% of plies with it, 7% without), Black N on f6 +0.21 (on 23% of plies with it, 7% without)
- either: on at 17.2% of plies; phi with White to move -0.00; top: White N on d2 +0.80 (on 99% of plies with it, 6% without), Black N on d7 +0.58 (on 99% of plies with it, 11% without), Black N on f6 +0.31 (on 43% of plies with it, 12% without), White N on e2 +0.26 (on 60% of plies with it, 15% without)

### k = 6: a = 416 (0.50) + b = 1455 (0.50): position 5, pair 1

**with**: split at ply 7, Black to move: chosen **b5** (48% there) vs subpar **Nc5** (43%). `r3kb1r/pb1nq1pp/1pp2n2/4p1B1/Q1B1P3/2N2N2/PPP3PP/2KR1R2 b kq - 5 14`

```
r . . . k b . r
p b . n q . p p
. p p . . n . .
. . . . p . B .
Q . B . P . . .
. . N . . N . .
P P P . . . P P
. . K R . R . .
```

| chosen | subpar |
|---|---|
| [11...c6]a [12.Qa4]b [Ngf6]a [13.Bc4]b [Qe7]a [14.Rhf1]b [b5]a [15.Bxb5]b [cxb5]a [16.Nxb5]b [Kf7]a [17.Qb3+]b [Kg6]a [18.Nh4+]b [Kxg5]a [19.Nf5]b | [11...c6]a [12.Qa4]b [Ngf6]a [13.Bc4]b [Qe7]a [14.Rhf1]b Nc5 15.Qa3 b5 16.Be2 a5 17.Qxc5 Qxc5 18.Bxf6 gxf6 19.Nh4 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Nf3%20d6%204.Qe2%20Qe7%205.d3%20b6%206.Nc3%20Bb7%207.fxe5%20dxe5%208.Bg5%20Qe6%209.O-O-O%20fxe4%2010.dxe4%20Nd7%2011.Qb5%20c6%2012.Qa4%20Ngf6%2013.Bc4%20Qe7%2014.Rhf1%20b5%2015.Bxb5%20cxb5%2016.Nxb5%20Kf7%2017.Qb3%2B%20Kg6%2018.Nh4%2B%20Kxg5%2019.Nf5#21) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Nf3%20d6%204.Qe2%20Qe7%205.d3%20b6%206.Nc3%20Bb7%207.fxe5%20dxe5%208.Bg5%20Qe6%209.O-O-O%20fxe4%2010.dxe4%20Nd7%2011.Qb5%20c6%2012.Qa4%20Ngf6%2013.Bc4%20Qe7%2014.Rhf1%20Nc5%2015.Qa3%20b5%2016.Be2%20a5%2017.Qxc5%20Qxc5%2018.Bxf6%20gxf6%2019.Nh4#21) |

**without**: split at ply 7, Black to move: chosen **Rc8** (51% there) vs subpar **Bxd5** (49%). `r3k1nr/1bpn2pp/p2bq3/Qp1Np1B1/4P3/5N2/PPP3PP/2KR1B1R b kq - 3 14`

```
r . . . k . n r
. b p n . . p p
p . . b q . . .
Q p . N p . B .
. . . . P . . .
. . . . . N . .
P P P . . . P P
. . K R . B . R
```

| chosen | subpar |
|---|---|
| [11...a6]a [12.Qa4]b [b5]a [13.Qa5]b [Bd6]a [14.Nd5]b [Rc8]a [15.a4]b [c6]a [16.Nb6]b Nxb6 17.Qxb6 Qd7 18.Nxe5 Bxe5 19.Rxd7 | [11...a6]a [12.Qa4]b [b5]a [13.Qa5]b [Bd6]a [14.Nd5]b [Bxd5]a [15.exd5]b [Qf5]a [16.Bd3]b [Qg4]a [17.h3]b [Qxg2]a [18.Rhg1]b [Qxf3]a [19.Rdf1]b |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Nf3%20d6%204.Qe2%20Qe7%205.d3%20b6%206.Nc3%20Bb7%207.fxe5%20dxe5%208.Bg5%20Qe6%209.O-O-O%20fxe4%2010.dxe4%20Nd7%2011.Qb5%20a6%2012.Qa4%20b5%2013.Qa5%20Bd6%2014.Nd5%20Rc8%2015.a4%20c6%2016.Nb6%20Nxb6%2017.Qxb6%20Qd7%2018.Nxe5%20Bxe5%2019.Rxd7#21) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.f4%20f5%203.Nf3%20d6%204.Qe2%20Qe7%205.d3%20b6%206.Nc3%20Bb7%207.fxe5%20dxe5%208.Bg5%20Qe6%209.O-O-O%20fxe4%2010.dxe4%20Nd7%2011.Qb5%20a6%2012.Qa4%20b5%2013.Qa5%20Bd6%2014.Nd5%20Bxd5%2015.exd5%20Qf5%2016.Bd3%20Qg4%2017.h3%20Qxg2%2018.Rhg1%20Qxf3%2019.Rdf1#21) |

### k = 6: a = 416 (0.50) + b = 1455 (0.50): position 8, pair 2

**with**: split at ply 5, White to move: chosen **Nxd2** (57% there) vs subpar **Bxd2** (43%). `2rqkb1r/pp3ppp/4pn2/8/b1pP4/P1P1PN1P/RQ1n1PP1/2B1KB1R w Kk - 0 14`

```
. . r q k b . r
p p . . . p p p
. . . . p n . .
. . . . . . . .
b . p P . . . .
P . P . P N . P
R Q . n . P P .
. . B . K B . R
```

| chosen | subpar |
|---|---|
| 12.Qb2 Rc8 [13.Nbd2]a Nxd2 [14.Nxd2]a [b5]b [15.Be2]a [Bd6]b [16.O-O]a [O-O]b [17.e4]a [e5]b 18.Nf3 exd4 19.Nxd4 Nxe4 | 12.Qb2 Rc8 [13.Nbd2]a Nxd2 14.Bxd2 b5 15.Be2 Be7 16.O-O O-O 17.Bd1 Qd5 18.Bxa4 bxa4 19.Qc2 Rb8 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Qb2%20Rc8%2013.Nbd2%20Nxd2%2014.Nxd2%20b5%2015.Be2%20Bd6%2016.O-O%20O-O%2017.e4%20e5%2018.Nf3%20exd4%2019.Nxd4%20Nxe4#22) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Qb2%20Rc8%2013.Nbd2%20Nxd2%2014.Bxd2%20b5%2015.Be2%20Be7%2016.O-O%20O-O%2017.Bd1%20Qd5%2018.Bxa4%20bxa4%2019.Qc2%20Rb8#22) |

**without**: split at ply 5, White to move: chosen **Qxc4** (67% there) vs subpar **Rb2** (33%). `r2qkb1r/pp1n1ppp/4p3/8/Q1pP4/P1P1PN1P/R2N1PP1/2n1KB1R w Kkq - 1 14`

```
r . . q k b . r
p p . n . p p p
. . . . p . . .
. . . . . . . .
Q . p P . . . .
P . P . P N . P
R . . N . P P .
. . n . K B . R
```

| chosen | subpar |
|---|---|
| [12.Nbd2]a [Nxc1]b [13.Qxa4+]a [Nd7]ab [14.Qxc4]ab [Rc8]ab [15.Qa4]ab [Rxc3]ab [16.Bb5]ab [Nd3+]b [17.Ke2]ab [Nc1+]b [18.Rxc1]ab [Rxc1]ab [19.Ne5]ab [Rc7]ab | [12.Nbd2]a [Nxc1]b [13.Qxa4+]a [Nd7]ab [14.Rb2]ab [Nd3+]b [15.Bxd3]ab [cxd3]ab [16.Rxb7]ab [Be7]ab [17.Ne5]ab [f6]ab [18.Nxd7]a [Kf7]b [19.O-O]a [Re8]b |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Nbd2%20Nxc1%2013.Qxa4%2B%20Nd7%2014.Qxc4%20Rc8%2015.Qa4%20Rxc3%2016.Bb5%20Nd3%2B%2017.Ke2%20Nc1%2B%2018.Rxc1%20Rxc1%2019.Ne5%20Rc7#22) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.Nf3%20Nf6%203.h3%20e6%204.a3%20c5%205.c3%20Nc6%206.e3%20c4%207.b3%20Na5%208.bxc4%20dxc4%209.Qa4%2B%20Bd7%2010.Qc2%20Nb3%2011.Ra2%20Ba4%2012.Nbd2%20Nxc1%2013.Qxa4%2B%20Nd7%2014.Rb2%20Nd3%2B%2015.Bxd3%20cxd3%2016.Rxb7%20Be7%2017.Ne5%20f6%2018.Nxd7%20Kf7%2019.O-O%20Re8#22) |

### k = 6: a = 416 (0.50) + b = 1455 (0.50): position 19, pair 3

**with**: split at ply 7, White to move: chosen **Nd2** (60% there) vs subpar **c5** (40%). `5r1k/ppq1b1p1/2np1r1p/3Qp3/1PP5/P1P1BN2/5PPP/3R1RK1 w - - 0 21`

```
. . . . . r . k
p p q . b . p .
. . n p . r . p
. . . Q p . . .
. P P . . . . .
P . P . B N . .
. . . . . P P P
. . . R . R K .
```

| chosen | subpar |
|---|---|
| 18.Be3 Rf6 19.Qd5 Raf8 20.Rad1 h6 [21.Nd2]a [Rg6]b [22.Qe4]a [Rgf6]b [23.f3]a [Nd8]b [24.Qd3]a [Ne6]b 25.Ne4 Rg6 | 18.Be3 Rf6 19.Qd5 Raf8 20.Rad1 h6 21.c5 dxc5 22.Bxc5 Bxc5 23.Qxc5 e4 24.Nd4 Qf4 25.Nxc6 bxc6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bc4%20Nf6%204.d3%20Be7%205.O-O%20O-O%206.Nc3%20d6%207.a3%20Be6%208.Qe2%20Bxc4%209.dxc4%20Nd7%2010.Nd5%20Nc5%2011.b4%20Ne6%2012.c3%20f5%2013.exf5%20Rxf5%2014.Qe4%20Rf8%2015.Qg4%20Qd7%2016.Nxc7%20Qxc7%2017.Qxe6%2B%20Kh8%2018.Be3%20Rf6%2019.Qd5%20Raf8%2020.Rad1%20h6%2021.Nd2%20Rg6%2022.Qe4%20Rgf6%2023.f3%20Nd8%2024.Qd3%20Ne6%2025.Ne4%20Rg6#34) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bc4%20Nf6%204.d3%20Be7%205.O-O%20O-O%206.Nc3%20d6%207.a3%20Be6%208.Qe2%20Bxc4%209.dxc4%20Nd7%2010.Nd5%20Nc5%2011.b4%20Ne6%2012.c3%20f5%2013.exf5%20Rxf5%2014.Qe4%20Rf8%2015.Qg4%20Qd7%2016.Nxc7%20Qxc7%2017.Qxe6%2B%20Kh8%2018.Be3%20Rf6%2019.Qd5%20Raf8%2020.Rad1%20h6%2021.c5%20dxc5%2022.Bxc5%20Bxc5%2023.Qxc5%20e4%2024.Nd4%20Qf4%2025.Nxc6%20bxc6#34) |

**without**: split at ply 7, White to move: chosen **Ne4** (54% there) vs subpar **Rad1** (46%). `5r1k/pp1qb1pp/2np1r2/3Qp1N1/1PP5/P1P1B3/5PPP/R4RK1 w - - 7 21`

```
. . . . . r . k
p p . q b . p p
. . n p . r . .
. . . Q p . N .
. P P . . . . .
P . P . B . . .
. . . . . P P P
R . . . . R K .
```

| chosen | subpar |
|---|---|
| 18.Be3 Rf6 19.Qd5 Raf8 20.Ng5 Qd7 21.Ne4 Rg6 22.Ng3 Qg4 23.f3 Qh4 24.Bf2 Bg5 25.Rad1 Bf4 | 18.Be3 Rf6 19.Qd5 Raf8 20.Ng5 Qd7 21.Rad1 Rg6 22.Ne4 Qg4 23.Ng3 h5 24.h3 Qh4 25.Qe4 Qf6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bc4%20Nf6%204.d3%20Be7%205.O-O%20O-O%206.Nc3%20d6%207.a3%20Be6%208.Qe2%20Bxc4%209.dxc4%20Nd7%2010.Nd5%20Nc5%2011.b4%20Ne6%2012.c3%20f5%2013.exf5%20Rxf5%2014.Qe4%20Rf8%2015.Qg4%20Qd7%2016.Nxc7%20Qxc7%2017.Qxe6%2B%20Kh8%2018.Be3%20Rf6%2019.Qd5%20Raf8%2020.Ng5%20Qd7%2021.Ne4%20Rg6%2022.Ng3%20Qg4%2023.f3%20Qh4%2024.Bf2%20Bg5%2025.Rad1%20Bf4#34) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20e5%202.Nf3%20Nc6%203.Bc4%20Nf6%204.d3%20Be7%205.O-O%20O-O%206.Nc3%20d6%207.a3%20Be6%208.Qe2%20Bxc4%209.dxc4%20Nd7%2010.Nd5%20Nc5%2011.b4%20Ne6%2012.c3%20f5%2013.exf5%20Rxf5%2014.Qe4%20Rf8%2015.Qg4%20Qd7%2016.Nxc7%20Qxc7%2017.Qxe6%2B%20Kh8%2018.Be3%20Rf6%2019.Qd5%20Raf8%2020.Ng5%20Qd7%2021.Rad1%20Rg6%2022.Ne4%20Qg4%2023.Ng3%20h5%2024.h3%20Qh4%2025.Qe4%20Qf6#34) |

### k = 6: a = 416 (0.50) + b = 1455 (0.50): position 42, pair 4

**with**: split at ply 7, White to move: chosen **Rc1** (60% there) vs subpar **N2b3** (40%). `rn3k2/1b3ppp/p3pn2/1p1p4/3N4/4P1P1/3N1PBP/Q4RK1 w - - 2 17`

```
r n . . . k . .
. b . . . p p p
p . . . p n . .
. p . p . . . .
. . . N . . . .
. . . . P . P .
. . . N . P B P
Q . . . . R K .
```

| chosen | subpar |
|---|---|
| [14.Bxf8]a [Qxa1]b [15.Qxa1]a [Kxf8]b [16.Nd4]a [Bb7]b [17.Rc1]a [Nbd7]ab [18.Rc7]ab [Rb8]ab [19.N2b3]b [Ke8]a [20.Na5]b [Ba8]a [21.Nac6]b [Rb6]a | [14.Bxf8]a [Qxa1]b [15.Qxa1]a [Kxf8]b [16.Nd4]a [Bb7]b 17.N2b3 [Nbd7]a [18.Rc1]b Nb6 19.Qa5 Nc4 20.Qc7 Bc8 21.Qd8+ Ne8 |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.e3%20e6%203.Ne2%20c5%204.Nd2%20a6%205.g3%20Nf6%206.Bg2%20Be7%207.O-O%20O-O%208.c3%20b5%209.a4%20Qa5%2010.dxc5%20Bxc5%2011.b4%20Bxb4%2012.cxb4%20Qxb4%2013.Ba3%20Qxa4%2014.Bxf8%20Qxa1%2015.Qxa1%20Kxf8%2016.Nd4%20Bb7%2017.Rc1%20Nbd7%2018.Rc7%20Rb8%2019.N2b3%20Ke8%2020.Na5%20Ba8%2021.Nac6%20Rb6#26) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.e3%20e6%203.Ne2%20c5%204.Nd2%20a6%205.g3%20Nf6%206.Bg2%20Be7%207.O-O%20O-O%208.c3%20b5%209.a4%20Qa5%2010.dxc5%20Bxc5%2011.b4%20Bxb4%2012.cxb4%20Qxb4%2013.Ba3%20Qxa4%2014.Bxf8%20Qxa1%2015.Qxa1%20Kxf8%2016.Nd4%20Bb7%2017.N2b3%20Nbd7%2018.Rc1%20Nb6%2019.Qa5%20Nc4%2020.Qc7%20Bc8%2021.Qd8%2B%20Ne8#26) |

**without**: split at ply 7, White to move: chosen **Rc1** (54% there) vs subpar **Rfa1** (37%). `r1b2k2/3n1ppp/p3pn2/3p4/R7/4P1P1/3NNPBP/5RK1 w - - 1 17`

```
r . b . . k . .
. . . n . p p p
p . . . p n . .
. . . p . . . .
R . . . . . . .
. . . . P . P .
. . . N N P B P
. . . . . R K .
```

| chosen | subpar |
|---|---|
| [14.Qxa4]a [bxa4]b [15.Bxf8]a [Kxf8]b [16.Rxa4]a [Nbd7]ab [17.Rc1]ab [Nb6]b [18.Rb4]a [Nbd7]ab [19.Nd4]ab [a5]ab [20.Ra4]ab [Ba6]ab [21.Rxa5]ab [Bb7]ab | [14.Qxa4]a [bxa4]b [15.Bxf8]a [Kxf8]b [16.Rxa4]a [Nbd7]ab [17.Rfa1]ab [Nc5]b [18.Ra5]a [Nd3]b [19.Nd4]a [e5]b [20.N4b3]a [e4]b [21.Bf1]a [Ne5]b |
| [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.e3%20e6%203.Ne2%20c5%204.Nd2%20a6%205.g3%20Nf6%206.Bg2%20Be7%207.O-O%20O-O%208.c3%20b5%209.a4%20Qa5%2010.dxc5%20Bxc5%2011.b4%20Bxb4%2012.cxb4%20Qxb4%2013.Ba3%20Qxa4%2014.Qxa4%20bxa4%2015.Bxf8%20Kxf8%2016.Rxa4%20Nbd7%2017.Rc1%20Nb6%2018.Rb4%20Nbd7%2019.Nd4%20a5%2020.Ra4%20Ba6%2021.Rxa5%20Bb7#26) | [Lichess](https://lichess.org/analysis/pgn/1.d4%20d5%202.e3%20e6%203.Ne2%20c5%204.Nd2%20a6%205.g3%20Nf6%206.Bg2%20Be7%207.O-O%20O-O%208.c3%20b5%209.a4%20Qa5%2010.dxc5%20Bxc5%2011.b4%20Bxb4%2012.cxb4%20Qxb4%2013.Ba3%20Qxa4%2014.Qxa4%20bxa4%2015.Bxf8%20Kxf8%2016.Rxa4%20Nbd7%2017.Rfa1%20Nc5%2018.Ra5%20Nd3%2019.Nd4%20e5%2020.N4b3%20e4%2021.Bf1%20Ne5#26) |

### k = 6: a = 416 (0.50) + b = 1455 (0.50): position 3, pair 5

**with**: split at ply 10, White to move: chosen **Qxf3** (62% there) vs subpar **Nxf3** (38%). `2kr3r/ppp2ppp/5n2/4pq2/8/PPbPBn1P/2PN1PP1/1R1Q1K1R w - - 0 16`

```
. . k r . . . r
p p p . . p p p
. . . . . n . .
. . . . p q . .
. . . . . . . .
P P b P B n . P
. . P N . P P .
. R . Q . K . R
```

| chosen | subpar |
|---|---|
| 11...Qf5 12.Be3 e5 [13.Nd2]a [Bb4]b [14.a3]a [Bc3]b [15.Rb1]a [Nxf3]b [16.Qxf3]a [Qxf3]b [17.gxf3]a [Nd5]b [18.Ke2]a [f5]b [19.Rhg1]a | 11...Qf5 12.Be3 e5 [13.Nd2]a [Bb4]b [14.a3]a [Bc3]b [15.Rb1]a [Nxf3]b 16.Nxf3 e4 17.Nh4 Qe6 18.Qe2 exd3 19.cxd3 |
| [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nc6%202.e4%20d5%203.exd5%20Qxd5%204.b3%20Bg4%205.Bc4%20Qe4%2B%206.Kf1%20Nd4%207.Bd3%20Qf4%208.Be2%20O-O-O%209.h3%20Bxf3%2010.Bxf3%20Nf6%2011.d3%20Qf5%2012.Be3%20e5%2013.Nd2%20Bb4%2014.a3%20Bc3%2015.Rb1%20Nxf3%2016.Qxf3%20Qxf3%2017.gxf3%20Nd5%2018.Ke2%20f5%2019.Rhg1#21) | [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nc6%202.e4%20d5%203.exd5%20Qxd5%204.b3%20Bg4%205.Bc4%20Qe4%2B%206.Kf1%20Nd4%207.Bd3%20Qf4%208.Be2%20O-O-O%209.h3%20Bxf3%2010.Bxf3%20Nf6%2011.d3%20Qf5%2012.Be3%20e5%2013.Nd2%20Bb4%2014.a3%20Bc3%2015.Rb1%20Nxf3%2016.Nxf3%20e4%2017.Nh4%20Qe6%2018.Qe2%20exd3%2019.cxd3#21) |

**without**: split at ply 10, White to move: chosen **Re1** (50% there) vs subpar **Ng5** (38%). `2kr3r/ppp2ppp/3b1n2/4p3/8/1P1PBN1P/P1P2PP1/R4K1R w - - 1 16`

```
. . k r . . . r
p p p . . p p p
. . . b . n . .
. . . . p . . .
. . . . . . . .
. P . P B N . P
P . P . . P P .
R . . . . K . R
```

| chosen | subpar |
|---|---|
| 11...Qf5 12.Be3 e5 [13.Nd2]a [Nxf3]b [14.Qxf3]a [Qxf3]b 15.Nxf3 Bd6 16.Re1 Rhe8 17.Bg5 Re6 18.Bxf6 Rxf6 19.Re4 | 11...Qf5 12.Be3 e5 [13.Nd2]a [Nxf3]b [14.Qxf3]a [Qxf3]b 15.Nxf3 Bd6 16.Ng5 Rdf8 17.Ke2 h6 18.Ne4 Nxe4 19.dxe4 |
| [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nc6%202.e4%20d5%203.exd5%20Qxd5%204.b3%20Bg4%205.Bc4%20Qe4%2B%206.Kf1%20Nd4%207.Bd3%20Qf4%208.Be2%20O-O-O%209.h3%20Bxf3%2010.Bxf3%20Nf6%2011.d3%20Qf5%2012.Be3%20e5%2013.Nd2%20Nxf3%2014.Qxf3%20Qxf3%2015.Nxf3%20Bd6%2016.Re1%20Rhe8%2017.Bg5%20Re6%2018.Bxf6%20Rxf6%2019.Re4#21) | [Lichess](https://lichess.org/analysis/pgn/1.Nf3%20Nc6%202.e4%20d5%203.exd5%20Qxd5%204.b3%20Bg4%205.Bc4%20Qe4%2B%206.Kf1%20Nd4%207.Bd3%20Qf4%208.Be2%20O-O-O%209.h3%20Bxf3%2010.Bxf3%20Nf6%2011.d3%20Qf5%2012.Be3%20e5%2013.Nd2%20Nxf3%2014.Qxf3%20Qxf3%2015.Nxf3%20Bd6%2016.Ng5%20Rdf8%2017.Ke2%20h6%2018.Ne4%20Nxe4%2019.dxe4#21) |

### k = 6: a = 416 (0.50) + b = 1455 (0.50): position 17, pair 6

**with**: split at ply 9, White to move: chosen **Kg2** (50% there) vs subpar **Ne4** (35%). `2krr3/pp3p1p/2n2np1/2p5/2P3P1/2bBqP2/P1PN3P/3Q1K1R w - - 4 18`

```
. . k r r . . .
p p . . . p . p
. . n . . n p .
. . p . . . . .
. . P . . . P .
. . b B q P . .
P . P N . . . P
. . . Q . K . R
```

| chosen | subpar |
|---|---|
| [14.Be2]a [Bxc4]b [15.dxc4]a [Qxe3]b [16.Kf1]a [O-O-O]b [17.Bd3]a [Rhe8]b [18.Kg2]a [Rxd3]b [19.cxd3]a [Qe2+]b [20.Qxe2]a [Rxe2+]b [21.Kg3]a Rxd2 | [14.Be2]a [Bxc4]b [15.dxc4]a [Qxe3]b [16.Kf1]a [O-O-O]b [17.Bd3]a [Rhe8]b 18.Ne4 Nxe4 19.fxe4 Rxe4 20.Kg2 Rf4 21.Rf1 Rxf1 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.d3%20g6%203.Nf3%20Bg7%204.e5%20Nc6%205.Bf4%20d6%206.exd6%20Bxb2%207.dxe7%20Qxe7%2B%208.Be3%20Bxa1%209.Na3%20Bc3%2B%2010.Nd2%20Nf6%2011.Nc4%20Bg4%2012.f3%20Bf5%2013.g4%20Be6%2014.Be2%20Bxc4%2015.dxc4%20Qxe3%2016.Kf1%20O-O-O%2017.Bd3%20Rhe8%2018.Kg2%20Rxd3%2019.cxd3%20Qe2%2B%2020.Qxe2%20Rxe2%2B%2021.Kg3%20Rxd2#26) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.d3%20g6%203.Nf3%20Bg7%204.e5%20Nc6%205.Bf4%20d6%206.exd6%20Bxb2%207.dxe7%20Qxe7%2B%208.Be3%20Bxa1%209.Na3%20Bc3%2B%2010.Nd2%20Nf6%2011.Nc4%20Bg4%2012.f3%20Bf5%2013.g4%20Be6%2014.Be2%20Bxc4%2015.dxc4%20Qxe3%2016.Kf1%20O-O-O%2017.Bd3%20Rhe8%2018.Ne4%20Nxe4%2019.fxe4%20Rxe4%2020.Kg2%20Rf4%2021.Rf1%20Rxf1#26) |

**without**: split at ply 9, White to move: chosen **Nb1** (43% there) vs subpar **h4** (39%). `r4rk1/4qp1p/p1n2np1/1pp5/6P1/N1bPBP2/P1P2KBP/3Q3R w - - 2 18`

```
r . . . . r k .
. . . . q p . p
p . n . . n p .
. p p . . . . .
. . . . . . P .
N . b P B P . .
P . P . . K B P
. . . Q . . . R
```

| chosen | subpar |
|---|---|
| [14.Kf2]a [Bxc4]b 15.Nxc4 b5 16.Na3 a6 17.Bg2 O-O 18.Nb1 Bd4 19.Re1 Rfe8 20.c3 Bxe3+ 21.Rxe3 Qd6 | [14.Kf2]a [Bxc4]b 15.Nxc4 b5 16.Na3 a6 17.Bg2 O-O 18.h4 Rfe8 19.Bc1 Bd4+ 20.Kg3 Qe5+ 21.f4 Qd6 |
| [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.d3%20g6%203.Nf3%20Bg7%204.e5%20Nc6%205.Bf4%20d6%206.exd6%20Bxb2%207.dxe7%20Qxe7%2B%208.Be3%20Bxa1%209.Na3%20Bc3%2B%2010.Nd2%20Nf6%2011.Nc4%20Bg4%2012.f3%20Bf5%2013.g4%20Be6%2014.Kf2%20Bxc4%2015.Nxc4%20b5%2016.Na3%20a6%2017.Bg2%20O-O%2018.Nb1%20Bd4%2019.Re1%20Rfe8%2020.c3%20Bxe3%2B%2021.Rxe3%20Qd6#26) | [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.d3%20g6%203.Nf3%20Bg7%204.e5%20Nc6%205.Bf4%20d6%206.exd6%20Bxb2%207.dxe7%20Qxe7%2B%208.Be3%20Bxa1%209.Na3%20Bc3%2B%2010.Nd2%20Nf6%2011.Nc4%20Bg4%2012.f3%20Bf5%2013.g4%20Be6%2014.Kf2%20Bxc4%2015.Nxc4%20b5%2016.Na3%20a6%2017.Bg2%20O-O%2018.h4%20Rfe8%2019.Bc1%20Bd4%2B%2020.Kg3%20Qe5%2B%2021.f4%20Qd6#26) |

