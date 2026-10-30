# A concept inside S's rollouts from one position

Position `r1br2k1/ppq1bppp/2n1pn2/4P3/P2p1P2/1NN1B3/1PP1B1PP/R2Q1RK1 w - - 0 14` (2400+ game 3123); S's top moves exf6 55%, Nxd4 29%, Nb5 14%, Bxd4 2%, Bd2 0%. 1024 rollouts of S, 16 plies, S plays both colours; a line is, per latent, the share of its plies where the latent fires; distinct lines weighted by how often each was sampled.

## Temperature

| T | distinct lines | most common line | median ply where a line leaves the most common one | used |
|---|---|---|---|---|
| 0.4 | 632 | 3% | 4 | yes |

T = 0.4: the lowest with >= 20 distinct lines and no line above 50%.

## Concepts (batch 1: 632 distinct lines, 331 latents, threshold r > 0.536; batch 2: 665 distinct lines, 334 latents, threshold r > 0.555, 19 concepts)

The branch effect removed first: each latent's fraction minus its weighted mean over the lines of the same branch (the first 4 moves; 27 branches in batch 1), so a group co-fires for reasons other than a shared prefix; a line carries a concept when half its latents are above their own weighted median of that residual. 19 concepts in batch 1, 14 found again in batch 2 (Jaccard of latents >= 0.3). Onset: the first ply where half a concept's latents fire. Routes: the move sequences before the onset; boards: the positions at it (transpositions count once); each an effective number (weighted by how often a line was sampled), against 1000 random line sets of the same size given the same onset plies: below the null's 5th percentile on routes or on boards, a branch; otherwise a candidate (the same latents on genuinely different lines and boards).

| concept | latents | mean r | carrying | in batch 2 (Jaccard, shared) | onset ply | routes: effective (null 5%) | boards: effective (null 5%) | | best board split (phi): carrying / other |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 4705, 7291, 13716 | 0.94 | 19% | yes (1.00, 3) | 8 | 5.5 (3.9) | 7.6 (4.1) | candidate | White Queen to e1 (+0.72): 64% / 1% |
| 2 | 929, 9549, 12025 | 0.88 | 46% | yes (1.00, 3) | 1 | 1.0 (1.0) | 1.8 (1.4) | candidate | White Bishop to d3 (-0.51): 14% / 64% |
| 3 | 204, 7337, 10380 | 0.79 | 44% | yes (1.00, 3) | 4 | 3.7 (4.7) | 3.7 (5.0) | branch | Black Queen to a7 (-0.63): 1% / 62% |
| 4 | 5410, 9096, 13784 | 0.72 | 51% | no (0.00, 0) | 8 | 4.8 (8.5) | 4.9 (11.6) | branch | Black Queen to a7 (-0.73): 0% / 70% |
| 5 | 596, 686, 6955, 8598 | 0.70 | 30% | yes (1.00, 4) | 1 | 1.0 (1.0) | 2.0 (1.3) | candidate | White Bishop to f2 (-0.65): 14% / 82% |
| 6 | 748, 6945, 7963, 9452, 10507 | 0.66 | 43% | yes (0.80, 4) | 12 | 2.9 (13.8) | 7.4 (15.8) | branch | White Bishop to d3 (+0.83): 89% / 6% |
| 7 | 659, 1847, 4454, 4509, 9409 | 0.65 | 29% | yes (0.67, 4) | 7 | 1.0 (1.8) | 1.0 (2.5) | branch | White Knight to a3 (+0.56): 39% / 0% |
| 8 | 9193, 13454, 14576, 15550 | 0.65 | 32% | yes (0.75, 3) | 8 | 5.1 (3.4) | 5.1 (3.5) | candidate | White Knight to b5 (-0.80): 23% / 98% |
| 9 | 3612, 4165, 7863, 13228, 14142, 15514 | 0.65 | 37% | yes (0.43, 3) | 6 | 4.6 (5.3) | 4.8 (5.6) | branch | White Knight to d4 (+0.58): 76% / 18% |
| 10 | 4287, 7687, 7884, 14345 | 0.65 | 50% | no (0.00, 0) | 12 | 10.0 (12.4) | 9.4 (13.3) | branch | Black Pawn to a6 (-0.57): 28% / 85% |
| 11 | 940, 1966, 4740, 6288, 8268, 10560, 10775, 11323, 13020, 13332 | 0.63 | 50% | yes (0.45, 5) | 9 | 1.8 (2.9) | 1.8 (2.9) | branch | trade on a7 (-0.72): 0% / 69% |
| 12 | 330, 1788, 8648, 10374, 15473 | 0.62 | 47% | no (0.14, 3) | 10 | 1.5 (5.4) | 1.5 (5.7) | branch | Black Queen to a7 (+0.75): 73% / 1% |
| 13 | 1703, 5305, 6210, 8615, 10188, 11377, 11458, 11618, 12952 | 0.62 | 35% | yes (0.56, 5) | 10 | 3.4 (2.0) | 3.3 (2.0) | candidate | White Bishop to f2 (-0.74): 13% / 88% |
| 14 | 32, 263, 634, 1144, 1724, 2095, 2329, 3855, 3993, 4484, 5006, 5175, 5548, 6331, 8012, 8342, 8362, 8476, 9504, 11225, 11957, 12371, 13516, 13727, 14103, 14696, 15004, 16219, 16242, 16296, 16338 | 0.61 | 34% | yes (0.50, 17) | 8 | 1.0 (3.8) | 1.0 (4.1) | branch | Black Rook to a7 (+0.97): 96% / 0% |
| 15 | 10319, 10678, 11024, 13705 | 0.61 | 51% | yes (1.00, 4) | 6 | 1.2 (2.8) | 1.2 (3.3) | branch | Black Queen to a7 (+0.71): 68% / 0% |
| 16 | 9048, 9609, 16003 | 0.61 | 45% | no (0.00, 0) | 10 | 4.7 (5.3) | 4.7 (5.4) | branch | Black Pawn to a6 (-0.62): 23% / 84% |
| 17 | 5139, 6657, 6796, 9495, 12441, 12507, 12582, 14472, 14496 | 0.60 | 29% | yes (0.89, 8) | 11 | 1.0 (3.0) | 1.0 (5.6) | branch | White Bishop to d3 (+0.61): 88% / 22% |
| 18 | 1421, 3013, 9475, 11894 | 0.60 | 40% | yes (0.75, 3) | 7 | 2.4 (3.5) | 2.5 (4.3) | branch | White Bishop to f2 (-0.68): 22% / 89% |
| 19 | 614, 6835, 10639 | 0.59 | 44% | no (0.00, 0) | 2 | 3.3 (3.6) | 3.4 (3.7) | branch | Black Pawn to a6 (-0.68): 19% / 86% |

96 board splits tested (each in 5-95% of the rollouts).

### Concept 1 (candidate): latents 4705, 7291, 13716; carried by 19% of the rollouts, its latents starting at ply 8: 5.5 effective routes (random lines: 3.9 at the 5th percentile), 7.6 effective boards (4.1)

- White Queen to e1: 64% of carrying rollouts, 1% of the others (phi +0.72)
- Black Rook to d4: 43% of carrying rollouts, 4% of the others (phi +0.47)
- White Knight to b5: 34% of carrying rollouts, 84% of the others (phi -0.45)

carrying it:

- 14.exf6 Bxf6 15.Ne4 dxe3 16.Nxf6+ gxf6 17.Qe1 [Qb6] 18.a5 [Qb4] 19.Qg3+ Kh8 20.Qxe3 Qe7 21.Rad1 Bd7  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Ne4%20dxe3%2016.Nxf6%2B%20gxf6%2017.Qe1%20Qb6%2018.a5%20Qb4%2019.Qg3%2B%20Kh8%2020.Qxe3%20Qe7%2021.Rad1%20Bd7#26))
- 14.exf6 Bxf6 15.Nb5 Qe7 16.Bf2 d3 17.Bxd3 Bxb2 18.Rb1 Bf6 19.Qh5 g6 20.Qc5 Qe8 21.Nc7 Qd7  (sampled 6x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qe7%2016.Bf2%20d3%2017.Bxd3%20Bxb2%2018.Rb1%20Bf6%2019.Qh5%20g6%2020.Qc5%20Qe8%2021.Nc7%20Qd7#26))
- 14.exf6 Bxf6 15.Ne4 dxe3 16.Nxf6+ gxf6 17.Qe1 [Nd4] 18.Nxd4 [Rxd4] 19.Qg3+ Kh8 20.Qxe3 Rd8 21.Bd3 Bd7  (sampled 6x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Ne4%20dxe3%2016.Nxf6%2B%20gxf6%2017.Qe1%20Nd4%2018.Nxd4%20Rxd4%2019.Qg3%2B%20Kh8%2020.Qxe3%20Rd8%2021.Bd3%20Bd7#26))

not carrying it:

- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 19.Bd3 Ra8 20.Nd2 Nb4 21.Ne4 Be7  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bd3%20Ra8%2020.Nd2%20Nb4%2021.Ne4%20Be7#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.Na3 d3 18.Qxd3 Rxd3 19.Bxb6 Rxb3 20.cxb3 Bxb2 21.Ra2 Bxa3  (sampled 4x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.Na3%20d3%2018.Qxd3%20Rxd3%2019.Bxb6%20Rxb3%2020.cxb3%20Bxb2%2021.Ra2%20Bxa3#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 19.Bd3 e5 20.fxe5 Bxe5 21.Qh5 f5  (sampled 4x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bd3%20e5%2020.fxe5%20Bxe5%2021.Qh5%20f5#26))

### Concept 2 (candidate): latents 929, 9549, 12025; carried by 46% of the rollouts, its latents starting at ply 1: 1.0 effective routes (random lines: 1.0 at the 5th percentile), 1.8 effective boards (1.4)

- White Bishop to d3: 14% of carrying rollouts, 64% of the others (phi -0.51)
- Black Knight to d4: 56% of carrying rollouts, 15% of the others (phi +0.43)
- Black Rook to a7: 12% of carrying rollouts, 51% of the others (phi -0.41)

carrying it:

- [14.exf6] [Bxf6] 15.Nxd4 [Nxd4] 16.Bxd4 [Bxd4+] 17.Kh1 [Bxc3] 18.Qxd8+ [Qxd8] 19.bxc3 [Bd7] 20.Bf3 Bc6 21.Rad1 Qf6  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nxd4%20Nxd4%2016.Bxd4%20Bxd4%2B%2017.Kh1%20Bxc3%2018.Qxd8%2B%20Qxd8%2019.bxc3%20Bd7%2020.Bf3%20Bc6%2021.Rad1%20Qf6#26))
- [14.exf6] [Bxf6] 15.Bd2 [dxc3] 16.bxc3 [b6] 17.Qe1 [Bb7] 18.Qg3 [Ne7] 19.Bd3 Nf5 20.Qh3 g6 21.Rae1 Rac8  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Bd2%20dxc3%2016.bxc3%20b6%2017.Qe1%20Bb7%2018.Qg3%20Ne7%2019.Bd3%20Nf5%2020.Qh3%20g6%2021.Rae1%20Rac8#26))
- [14.exf6] [Bxf6] 15.Nb5 [Qb6] 16.Bf2 [a6] 17.Na3 [Qc7] 18.Nc4 [Qxf4] 19.Nb6 [Rb8] 20.Nxc8 [Rbxc8] 21.Nc5 [Qc7]  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.Na3%20Qc7%2018.Nc4%20Qxf4%2019.Nb6%20Rb8%2020.Nxc8%20Rbxc8%2021.Nc5%20Qc7#26))

not carrying it:

- [14.exf6] [Bxf6] 15.Nb5 [Qb6] 16.Bf2 [a6] 17.a5 [Qa7] 18.Nxa7 [Rxa7] 19.Bd3 Nb4 20.Qf3 Nd5 21.Nc5 Nb4  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bd3%20Nb4%2020.Qf3%20Nd5%2021.Nc5%20Nb4#26))
- [14.exf6] [Bxf6] 15.Nb5 [Qb6] 16.Bf2 [a6] 17.a5 [Qa7] 18.Nxa7 [Rxa7] 19.Bd3 Ra8 20.Qe2 Nb4 21.Be4 Bd7  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bd3%20Ra8%2020.Qe2%20Nb4%2021.Be4%20Bd7#26))
- [14.exf6] [Bxf6] 15.Nb5 [Qb6] 16.Bf2 [a6] 17.a5 [Qxb5] 18.Bxb5 axb5 19.Re1 b4 20.Qd3 Bd7 21.Nc5 Be8  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qxb5%2018.Bxb5%20axb5%2019.Re1%20b4%2020.Qd3%20Bd7%2021.Nc5%20Be8#26))

### Concept 5 (candidate): latents 596, 686, 6955, 8598; carried by 30% of the rollouts, its latents starting at ply 1: 1.0 effective routes (random lines: 1.0 at the 5th percentile), 2.0 effective boards (1.3)

- White Bishop to f2: 14% of carrying rollouts, 82% of the others (phi -0.65)
- Black Queen to b6: 26% of carrying rollouts, 88% of the others (phi -0.61)
- Black Pawn to a6: 17% of carrying rollouts, 73% of the others (phi -0.52)

carrying it:

- [14.exf6] [Bxf6] [15.Nb5] [Qe7] [16.Bf2] [d3] [17.Bxd3] [Bxb2] [18.Rb1] [Bf6] [19.Qe2] [a6] [20.N5d4] [Nxd4] [21.Nxd4] [Bxd4]  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qe7%2016.Bf2%20d3%2017.Bxd3%20Bxb2%2018.Rb1%20Bf6%2019.Qe2%20a6%2020.N5d4%20Nxd4%2021.Nxd4%20Bxd4#26))
- [14.exf6] [Bxf6] [15.Nb5] [Qe7] [16.Bf2] [d3] [17.Bxd3] [Bxb2] [18.Rb1] [Bf6] [19.Qh5] [g6] [20.Qc5] [Qe8] [21.Nc7] [Qd7]  (sampled 6x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qe7%2016.Bf2%20d3%2017.Bxd3%20Bxb2%2018.Rb1%20Bf6%2019.Qh5%20g6%2020.Qc5%20Qe8%2021.Nc7%20Qd7#26))
- [14.Nxd4] [Nxd4] [15.exf6] [Nf3+] [16.Bxf3] [Rxd1] [17.Raxd1] [Bxf6] [18.Nb5] [Qe7] [19.Nxa7] [Bd7] [20.b3] [h6] [21.Bxb7] [Rd8]  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.Nxd4%20Nxd4%2015.exf6%20Nf3%2B%2016.Bxf3%20Rxd1%2017.Raxd1%20Bxf6%2018.Nb5%20Qe7%2019.Nxa7%20Bd7%2020.b3%20h6%2021.Bxb7%20Rd8#26))

not carrying it:

- [14.exf6] [Bxf6] [15.Nb5] [Qb6] [16.Bf2] [a6] [17.a5] [Qa7] [18.Nxa7] [Rxa7] [19.Qd2] [Ra8] [20.Rad1] e5 21.fxe5 Bxe5  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Qd2%20Ra8%2020.Rad1%20e5%2021.fxe5%20Bxe5#26))
- [14.exf6] [Bxf6] [15.Ne4] [dxe3] 16.Nxf6+ [gxf6] [17.Qe1] [Nd4] [18.Nxd4] [Rxd4] [19.Qg3+] [Kh8] [20.Qxe3] [Qc5] [21.Kh1] [Bd7]  (sampled 3x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Ne4%20dxe3%2016.Nxf6%2B%20gxf6%2017.Qe1%20Nd4%2018.Nxd4%20Rxd4%2019.Qg3%2B%20Kh8%2020.Qxe3%20Qc5%2021.Kh1%20Bd7#26))
- [14.exf6] [Bxf6] [15.Nb5] [Qb6] [16.Bf2] [a6] [17.a5] [Qa7] [18.Nxa7] [Rxa7] [19.Bf3] [Nb4] [20.Bxd4] Bxd4+ [21.Nxd4] [Rxd4]  (sampled 3x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bf3%20Nb4%2020.Bxd4%20Bxd4%2B%2021.Nxd4%20Rxd4#26))

### Concept 8 (candidate): latents 9193, 13454, 14576, 15550; carried by 32% of the rollouts, its latents starting at ply 8: 5.1 effective routes (random lines: 3.4 at the 5th percentile), 5.1 effective boards (3.5)

- White Knight to b5: 23% of carrying rollouts, 98% of the others (phi -0.80)
- White Bishop to f2: 12% of carrying rollouts, 85% of the others (phi -0.70)
- Black Queen to b6: 24% of carrying rollouts, 90% of the others (phi -0.67)

carrying it:

- 14.Nxd4 Nxd4 15.exf6 Nf3+ 16.Bxf3 Rxd1 17.Raxd1 Bxf6 18.Nb5 Qe7 19.Nxa7 Bd7 20.b3 h6 21.Bxb7 Rd8  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.Nxd4%20Nxd4%2015.exf6%20Nf3%2B%2016.Bxf3%20Rxd1%2017.Raxd1%20Bxf6%2018.Nb5%20Qe7%2019.Nxa7%20Bd7%2020.b3%20h6%2021.Bxb7%20Rd8#26))
- 14.Nxd4 Nxd4 15.Bxd4 Bc5 16.Bxc5 Rxd1 17.Raxd1 [Qxc5+] 18.Kh1 [Nd5] 19.Nxd5 exd5 20.c3 [Bf5] 21.Bf3 [Be4]  (sampled 5x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.Nxd4%20Nxd4%2015.Bxd4%20Bc5%2016.Bxc5%20Rxd1%2017.Raxd1%20Qxc5%2B%2018.Kh1%20Nd5%2019.Nxd5%20exd5%2020.c3%20Bf5%2021.Bf3%20Be4#26))
- 14.Nb5 Qb6 15.Bf2 Ne4 16.a5 [Qc5] 17.N5xd4 Nxd4 18.Bxd4 Qc7 19.Qd3 Nc5 20.Qc3 b6 21.Bf3 Bb7  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.Nb5%20Qb6%2015.Bf2%20Ne4%2016.a5%20Qc5%2017.N5xd4%20Nxd4%2018.Bxd4%20Qc7%2019.Qd3%20Nc5%2020.Qc3%20b6%2021.Bf3%20Bb7#26))

not carrying it:

- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 19.Bd3 Ra8 20.Nc5 Nb4 21.Ne4 Be7  (sampled 4x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bd3%20Ra8%2020.Nc5%20Nb4%2021.Ne4%20Be7#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 d3 17.Bxb6 dxe2 18.Qxe2 axb6 19.c3 e5 20.fxe5 Nxe5 21.N3d4 Bg4  (sampled 4x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20d3%2017.Bxb6%20dxe2%2018.Qxe2%20axb6%2019.c3%20e5%2020.fxe5%20Nxe5%2021.N3d4%20Bg4#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qxb5 18.Bxb5 axb5 19.Qe2 Bd7 20.Rfd1 Be8 21.Bh4 Bxh4  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qxb5%2018.Bxb5%20axb5%2019.Qe2%20Bd7%2020.Rfd1%20Be8%2021.Bh4%20Bxh4#26))

### Concept 13 (candidate): latents 1703, 5305, 6210, 8615, 10188, 11377, 11458, 11618, 12952; carried by 35% of the rollouts, its latents starting at ply 10: 3.4 effective routes (random lines: 2.0 at the 5th percentile), 3.3 effective boards (2.0)

- White Bishop to f2: 13% of carrying rollouts, 88% of the others (phi -0.74)
- Black Pawn to a6: 14% of carrying rollouts, 80% of the others (phi -0.64)
- White Knight to b5: 37% of carrying rollouts, 94% of the others (phi -0.62)

carrying it:

- 14.Nxd4 Nxd4 15.Bxd4 Bc5 16.Nb5 Bxd4+ 17.Nxd4 Qc5 18.c3 [Nd5] 19.Qd2 Bd7 20.Kh1 Bc6 21.Bf3 Ne7  (sampled 3x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.Nxd4%20Nxd4%2015.Bxd4%20Bc5%2016.Nb5%20Bxd4%2B%2017.Nxd4%20Qc5%2018.c3%20Nd5%2019.Qd2%20Bd7%2020.Kh1%20Bc6%2021.Bf3%20Ne7#26))
- 14.exf6 dxe3 15.fxe7 Qxe7 16.Qc1 Nd4 17.Qxe3 Nxc2 18.Qc5 Qxc5+ 19.Nxc5 Nxa1 20.Rxa1 b6 21.N5e4 Bb7  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20dxe3%2015.fxe7%20Qxe7%2016.Qc1%20Nd4%2017.Qxe3%20Nxc2%2018.Qc5%20Qxc5%2B%2019.Nxc5%20Nxa1%2020.Rxa1%20b6%2021.N5e4%20Bb7#26))
- 14.Nxd4 Bc5 15.exf6 Bxd4 16.Bxd4 Rxd4 17.Qe1 gxf6 18.Qg3+ Kf8 19.Qh4 Qe7 20.Qxh7 Qc5 21.Kh1 Bd7  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.Nxd4%20Bc5%2015.exf6%20Bxd4%2016.Bxd4%20Rxd4%2017.Qe1%20gxf6%2018.Qg3%2B%20Kf8%2019.Qh4%20Qe7%2020.Qxh7%20Qc5%2021.Kh1%20Bd7#26))

not carrying it:

- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 19.Bd3 Ra8 20.Nc5 Nb4 21.Ne4 Be7  (sampled 4x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bd3%20Ra8%2020.Nc5%20Nb4%2021.Ne4%20Be7#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 19.Bd3 Bd7 20.Nc5 Be8 21.Ne4 Be7  (sampled 32x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bd3%20Bd7%2020.Nc5%20Be8%2021.Ne4%20Be7#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 19.Bf3 Bd7 20.Nc5 Be8 21.Bxc6 Bxc6  (sampled 4x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bf3%20Bd7%2020.Nc5%20Be8%2021.Bxc6%20Bxc6#26))

### Concept 3 (branch): latents 204, 7337, 10380; carried by 44% of the rollouts, its latents starting at ply 4: 3.7 effective routes (random lines: 4.7 at the 5th percentile), 3.7 effective boards (5.0)

- Black Queen to a7: 1% of carrying rollouts, 62% of the others (phi -0.63)
- White Knight to a7: 1% of carrying rollouts, 62% of the others (phi -0.63)
- trade on a7: 1% of carrying rollouts, 61% of the others (phi -0.63)

carrying it:

- 14.exf6 Bxf6 15.Nb5 Qe7 16.Bf2 d3 17.Bxd3 Bxb2 18.Rb1 Bf6 19.Qf3 Nb4 20.Bc5 Qd7 21.Bxb4 a6  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qe7%2016.Bf2%20d3%2017.Bxd3%20Bxb2%2018.Rb1%20Bf6%2019.Qf3%20Nb4%2020.Bc5%20Qd7%2021.Bxb4%20a6#26))
- 14.exf6 Bxf6 15.Nb5 Qe7 16.N3xd4 Nxd4 17.Nxd4 e5 18.fxe5 Qxe5 19.Bf2 Be6 20.c3 Bd5 21.Bf3 Rac8  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qe7%2016.N3xd4%20Nxd4%2017.Nxd4%20e5%2018.fxe5%20Qxe5%2019.Bf2%20Be6%2020.c3%20Bd5%2021.Bf3%20Rac8#26))
- 14.Nb5 [Qb6] 15.Bf2 [Ne4] 16.N5xd4 [Nxf2] 17.Rxf2 [Nxd4] 18.Nxd4 Rxd4 19.Qe1 [Rxf4] 20.a5 Qxb2 21.Rxf4 Qxe5  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.Nb5%20Qb6%2015.Bf2%20Ne4%2016.N5xd4%20Nxf2%2017.Rxf2%20Nxd4%2018.Nxd4%20Rxd4%2019.Qe1%20Rxf4%2020.a5%20Qxb2%2021.Rxf4%20Qxe5#26))

not carrying it:

- 14.exf6 Bxf6 15.Nb5 [Qb6] 16.Bf2 [a6] 17.a5 Qa7 18.Nxa7 Rxa7 19.Bf3 Ra8 20.Bxc6 bxc6 21.Bxd4 c5  (sampled 5x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bf3%20Ra8%2020.Bxc6%20bxc6%2021.Bxd4%20c5#26))
- 14.exf6 Bxf6 15.Nb5 [Qb6] 16.Bf2 [a6] 17.a5 Qa7 18.Nxa7 Rxa7 19.Bf3 Ra8 20.Bxc6 bxc6 21.Bxd4 Bxd4+  (sampled 4x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bf3%20Ra8%2020.Bxc6%20bxc6%2021.Bxd4%20Bxd4%2B#26))
- 14.exf6 Bxf6 15.Nb5 [Qb6] 16.Bf2 [a6] 17.a5 Qa7 18.Nxa7 Rxa7 19.Bd3 e5 20.fxe5 Bxe5 21.Qh5 f5  (sampled 4x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bd3%20e5%2020.fxe5%20Bxe5%2021.Qh5%20f5#26))

### Concept 6 (branch): latents 748, 6945, 7963, 9452, 10507; carried by 43% of the rollouts, its latents starting at ply 12: 2.9 effective routes (random lines: 13.8 at the 5th percentile), 7.4 effective boards (15.8)

- White Bishop to d3: 89% of carrying rollouts, 6% of the others (phi +0.83)
- White Queen to h5: 25% of carrying rollouts, 0% of the others (phi +0.39)
- Black Pawn to g6: 26% of carrying rollouts, 2% of the others (phi +0.37)

carrying it:

- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 19.Bd3 [Bd7] 20.Nc5 [Be8] 21.Ne4 [Be7]  (sampled 32x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bd3%20Bd7%2020.Nc5%20Be8%2021.Ne4%20Be7#26))
- 14.exf6 Bxf6 15.Nb5 Qe7 16.Bf2 d3 17.Bxd3 [Bxb2] 18.Rb1 [Bf6] 19.Qe2 a6 20.N5d4 Nxd4 21.Nxd4 [Bxd4]  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qe7%2016.Bf2%20d3%2017.Bxd3%20Bxb2%2018.Rb1%20Bf6%2019.Qe2%20a6%2020.N5d4%20Nxd4%2021.Nxd4%20Bxd4#26))
- 14.exf6 Bxf6 15.Nb5 Qe7 16.Bf2 d3 17.Bxd3 [Bxb2] 18.Rb1 [Bf6] 19.Qh5 g6 20.Qc5 Qe8 21.Nc7 Qd7  (sampled 6x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qe7%2016.Bf2%20d3%2017.Bxd3%20Bxb2%2018.Rb1%20Bf6%2019.Qh5%20g6%2020.Qc5%20Qe8%2021.Nc7%20Qd7#26))

not carrying it:

- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 19.Nc5 b6 20.axb6 Rb7 21.Bxa6 Rxb6  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Nc5%20b6%2020.axb6%20Rb7%2021.Bxa6%20Rxb6#26))
- 14.exf6 Bxf6 15.Bxd4 Nxd4 16.Nxd4 Bxd4+ 17.Kh1 Bxc3 18.bxc3 Rxd1 19.Raxd1 g6 20.Rd3 b6 21.Rfd1 Bb7  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Bxd4%20Nxd4%2016.Nxd4%20Bxd4%2B%2017.Kh1%20Bxc3%2018.bxc3%20Rxd1%2019.Raxd1%20g6%2020.Rd3%20b6%2021.Rfd1%20Bb7#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.Na3 d3 18.Qxd3 Rxd3 19.Bxb6 Rxb3 20.cxb3 Nd4 21.Bxd4 Bxd4+  (sampled 6x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.Na3%20d3%2018.Qxd3%20Rxd3%2019.Bxb6%20Rxb3%2020.cxb3%20Nd4%2021.Bxd4%20Bxd4%2B#26))

### Concept 7 (branch): latents 659, 1847, 4454, 4509, 9409; carried by 29% of the rollouts, its latents starting at ply 7: 1.0 effective routes (random lines: 1.8 at the 5th percentile), 1.0 effective boards (2.5)

- White Knight to a3: 39% of carrying rollouts, 0% of the others (phi +0.56)
- White Pawn to a5: 9% of carrying rollouts, 67% of the others (phi -0.53)
- White pawn push to a5: 9% of carrying rollouts, 67% of the others (phi -0.53)

carrying it:

- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 [17.Na3] d3 18.Qxd3 Rxd3 19.Bxb6 Rxb3 20.a5 Rxb2 21.Nc4 Rxc2  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.Na3%20d3%2018.Qxd3%20Rxd3%2019.Bxb6%20Rxb3%2020.a5%20Rxb2%2021.Nc4%20Rxc2#26))
- 14.exf6 Bxf6 15.Nb5 Qe7 16.Bf2 d3 17.Bxd3 Bxb2 18.Rb1 Bf6 19.Qf3 a6 20.Na3 Nb4 21.Bc5 Rxd3  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qe7%2016.Bf2%20d3%2017.Bxd3%20Bxb2%2018.Rb1%20Bf6%2019.Qf3%20a6%2020.Na3%20Nb4%2021.Bc5%20Rxd3#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 [17.Na3] Qc7 [18.Qd2] b6 19.Nc4 Bb7 20.Bf3 b5 21.axb5 axb5  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.Na3%20Qc7%2018.Qd2%20b6%2019.Nc4%20Bb7%2020.Bf3%20b5%2021.axb5%20axb5#26))

not carrying it:

- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 19.Bd3 Bd7 20.Nc5 Be8 21.Ne4 Be7  (sampled 32x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bd3%20Bd7%2020.Nc5%20Be8%2021.Ne4%20Be7#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 19.Qd2 Bd7 20.Bf3 Be8 21.Bxc6 Bxc6  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Qd2%20Bd7%2020.Bf3%20Be8%2021.Bxc6%20Bxc6#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 19.Bf3 Ra8 20.Bxc6 bxc6 21.Bxd4 Bxd4+  (sampled 4x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bf3%20Ra8%2020.Bxc6%20bxc6%2021.Bxd4%20Bxd4%2B#26))

### Concept 9 (branch): latents 3612, 4165, 7863, 13228, 14142, 15514; carried by 37% of the rollouts, its latents starting at ply 6: 4.6 effective routes (random lines: 5.3 at the 5th percentile), 4.8 effective boards (5.6)

- White Knight to d4: 76% of carrying rollouts, 18% of the others (phi +0.58)
- White Bishop to f2: 28% of carrying rollouts, 82% of the others (phi -0.53)
- Black Knight to d4: 62% of carrying rollouts, 17% of the others (phi +0.46)

carrying it:

- 14.exf6 gxf6 15.Nxd4 Nxd4 16.Bxd4 [Bc5] 17.Nb5 Bxd4+ 18.Nxd4 [e5] 19.fxe5 [fxe5] 20.c3 exd4 21.cxd4 Qb6  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20gxf6%2015.Nxd4%20Nxd4%2016.Bxd4%20Bc5%2017.Nb5%20Bxd4%2B%2018.Nxd4%20e5%2019.fxe5%20fxe5%2020.c3%20exd4%2021.cxd4%20Qb6#26))
- 14.exf6 Bxf6 15.Ne4 dxe3 16.Nxf6+ gxf6 17.Qc1 Nd4 18.Qxe3 Nxc2 19.Qg3+ Kf8 20.Rac1 Qb6+ 21.Kh1 Ne3  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Ne4%20dxe3%2016.Nxf6%2B%20gxf6%2017.Qc1%20Nd4%2018.Qxe3%20Nxc2%2019.Qg3%2B%20Kf8%2020.Rac1%20Qb6%2B%2021.Kh1%20Ne3#26))
- 14.exf6 Bxf6 15.Ne4 dxe3 16.Nxf6+ gxf6 17.Qe1 Nd4 18.Nxd4 Rxd4 19.Qg3+ Kh8 20.Qxe3 Qb6 21.a5 Qd6  (sampled 4x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Ne4%20dxe3%2016.Nxf6%2B%20gxf6%2017.Qe1%20Nd4%2018.Nxd4%20Rxd4%2019.Qg3%2B%20Kh8%2020.Qxe3%20Qb6%2021.a5%20Qd6#26))

not carrying it:

- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 19.Bd3 Ra8 20.Nd2 Nb4 21.Ne4 Be7  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bd3%20Ra8%2020.Nd2%20Nb4%2021.Ne4%20Be7#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 19.Bd3 g6 20.g4 e5 21.f5 Bd7  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bd3%20g6%2020.g4%20e5%2021.f5%20Bd7#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 19.Bd3 Nb4 20.Be4 Nd5 21.Bxd5 Rxd5  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bd3%20Nb4%2020.Be4%20Nd5%2021.Bxd5%20Rxd5#26))

### Concept 11 (branch): latents 940, 1966, 4740, 6288, 8268, 10560, 10775, 11323, 13020, 13332; carried by 50% of the rollouts, its latents starting at ply 9: 1.8 effective routes (random lines: 2.9 at the 5th percentile), 1.8 effective boards (2.9)

- trade on a7: 0% of carrying rollouts, 69% of the others (phi -0.72)
- Black Queen to a7: 1% of carrying rollouts, 69% of the others (phi -0.71)
- White Knight to a7: 1% of carrying rollouts, 69% of the others (phi -0.71)

carrying it:

- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.Na3 d3 [18.Qxd3] Rxd3 [19.Bxb6] [Rxb3] [20.cxb3] Nd4 21.Bxd4 Bxd4+  (sampled 6x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.Na3%20d3%2018.Qxd3%20Rxd3%2019.Bxb6%20Rxb3%2020.cxb3%20Nd4%2021.Bxd4%20Bxd4%2B#26))
- 14.Nxd4 Nxd4 15.exf6 Nxe2+ 16.Qxe2 Bxf6 17.Ne4 Bxb2 18.Rab1 Bd4 19.Kh1 Bxe3 20.Qxe3 b6 21.Qg3 Kh8  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.Nxd4%20Nxd4%2015.exf6%20Nxe2%2B%2016.Qxe2%20Bxf6%2017.Ne4%20Bxb2%2018.Rab1%20Bd4%2019.Kh1%20Bxe3%2020.Qxe3%20b6%2021.Qg3%20Kh8#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.Na3 d3 [18.Qxd3] Rxd3 [19.Bxb6] [Rxb3] [20.a5] Rxb2 21.Nc4 Rxc2  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.Na3%20d3%2018.Qxd3%20Rxd3%2019.Bxb6%20Rxb3%2020.a5%20Rxb2%2021.Nc4%20Rxc2#26))

not carrying it:

- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 19.Bd3 Bd7 20.Nc5 Be8 21.Ne4 Be7  (sampled 32x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bd3%20Bd7%2020.Nc5%20Be8%2021.Ne4%20Be7#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 19.Bf3 e5 20.Bxc6 bxc6 21.fxe5 Bxe5  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bf3%20e5%2020.Bxc6%20bxc6%2021.fxe5%20Bxe5#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 19.Bd3 Nb4 20.Be4 Nd5 21.Bxd5 Rxd5  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bd3%20Nb4%2020.Be4%20Nd5%2021.Bxd5%20Rxd5#26))

### Concept 14 (branch): latents 32, 263, 634, 1144, 1724, 2095, 2329, 3855, 3993, 4484, 5006, 5175, 5548, 6331, 8012, 8342, 8362, 8476, 9504, 11225, 11957, 12371, 13516, 13727, 14103, 14696, 15004, 16219, 16242, 16296, 16338; carried by 34% of the rollouts, its latents starting at ply 8: 1.0 effective routes (random lines: 3.8 at the 5th percentile), 1.0 effective boards (4.1)

- Black Rook to a7: 96% of carrying rollouts, 0% of the others (phi +0.97)
- trade on a7: 98% of carrying rollouts, 1% of the others (phi +0.97)
- Black Queen to a7: 98% of carrying rollouts, 2% of the others (phi +0.96)

carrying it:

- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 [Qa7] 18.Nxa7 [Rxa7] 19.Bf3 Bd7 20.Bxc6 Bxc6 21.Nxd4 Raa8  (sampled 4x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bf3%20Bd7%2020.Bxc6%20Bxc6%2021.Nxd4%20Raa8#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 [Qa7] 18.Nxa7 [Rxa7] 19.Bd3 Bd7 20.Be4 Be8 21.Bxc6 Bxc6  (sampled 3x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bd3%20Bd7%2020.Be4%20Be8%2021.Bxc6%20Bxc6#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 [Qa7] 18.Nxa7 [Rxa7] 19.Bd3 g6 20.Be4 Ra8 21.Bxc6 bxc6  (sampled 2x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bd3%20g6%2020.Be4%20Ra8%2021.Bxc6%20bxc6#26))

not carrying it:

- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.Na3 d3 18.Qxd3 Rxd3 19.Bxb6 Rxb3 20.cxb3 Nd4 21.Bxd4 Bxd4+  (sampled 6x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.Na3%20d3%2018.Qxd3%20Rxd3%2019.Bxb6%20Rxb3%2020.cxb3%20Nd4%2021.Bxd4%20Bxd4%2B#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 d3 17.Bxb6 dxe2 18.Qxe2 axb6 19.c3 Ne7 20.Rfd1 Bd7 21.Nd6 Bc6  (sampled 6x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20d3%2017.Bxb6%20dxe2%2018.Qxe2%20axb6%2019.c3%20Ne7%2020.Rfd1%20Bd7%2021.Nd6%20Bc6#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 d3 17.Bxb6 dxe2 18.Qxe2 axb6 19.c3 Bd7 20.Rfd1 Ne7 21.Nd6 Bc6  (sampled 9x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20d3%2017.Bxb6%20dxe2%2018.Qxe2%20axb6%2019.c3%20Bd7%2020.Rfd1%20Ne7%2021.Nd6%20Bc6#26))

### Concept 15 (branch): latents 10319, 10678, 11024, 13705; carried by 51% of the rollouts, its latents starting at ply 6: 1.2 effective routes (random lines: 2.8 at the 5th percentile), 1.2 effective boards (3.3)

- Black Queen to a7: 68% of carrying rollouts, 0% of the others (phi +0.71)
- White Knight to a7: 68% of carrying rollouts, 0% of the others (phi +0.71)
- trade on a7: 67% of carrying rollouts, 0% of the others (phi +0.71)

carrying it:

- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 [a6] 17.a5 [Qa7] 18.Nxa7 Rxa7 19.Bd3 Bd7 20.Nc5 Be8 21.Ne4 Be7  (sampled 32x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bd3%20Bd7%2020.Nc5%20Be8%2021.Ne4%20Be7#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 [a6] 17.a5 [Qa7] 18.Nxa7 Rxa7 19.Bf3 Bd7 20.Nc5 Be8 21.Ne4 Be7  (sampled 23x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bf3%20Bd7%2020.Nc5%20Be8%2021.Ne4%20Be7#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 [a6] 17.a5 [Qa7] 18.Nxa7 Rxa7 19.Bf3 Bd7 20.Nxd4 Nxd4 21.Bxd4 Bc6  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bf3%20Bd7%2020.Nxd4%20Nxd4%2021.Bxd4%20Bc6#26))

not carrying it:

- 14.exf6 Bxf6 15.Ne4 dxe3 16.Nxf6+ gxf6 17.Qe1 Qb6 18.a5 Qb4 19.Qg3+ Kh8 20.Qxe3 Qe7 21.Rad1 Bd7  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Ne4%20dxe3%2016.Nxf6%2B%20gxf6%2017.Qe1%20Qb6%2018.a5%20Qb4%2019.Qg3%2B%20Kh8%2020.Qxe3%20Qe7%2021.Rad1%20Bd7#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.a5 Qxb5 17.Bxb5 dxe3 18.Qf3 Bxb2 19.Rad1 Bd7 20.a6 bxa6 21.Bxc6 Bxc6  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.a5%20Qxb5%2017.Bxb5%20dxe3%2018.Qf3%20Bxb2%2019.Rad1%20Bd7%2020.a6%20bxa6%2021.Bxc6%20Bxc6#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 [a6] 17.Na3 Qc7 18.Nc4 b6 19.Bf3 Bb7 20.Bg3 b5 21.Nca5 Nxa5  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.Na3%20Qc7%2018.Nc4%20b6%2019.Bf3%20Bb7%2020.Bg3%20b5%2021.Nca5%20Nxa5#26))

### Concept 17 (branch): latents 5139, 6657, 6796, 9495, 12441, 12507, 12582, 14472, 14496; carried by 29% of the rollouts, its latents starting at ply 11: 1.0 effective routes (random lines: 3.0 at the 5th percentile), 1.0 effective boards (5.6)

- White Bishop to d3: 88% of carrying rollouts, 22% of the others (phi +0.61)
- Black Rook to a7: 64% of carrying rollouts, 20% of the others (phi +0.42)
- trade on a7: 66% of carrying rollouts, 22% of the others (phi +0.42)

carrying it:

- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 [19.Bd3] Bd7 20.Nc5 Be8 21.Ne4 Be7  (sampled 32x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bd3%20Bd7%2020.Nc5%20Be8%2021.Ne4%20Be7#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 [19.Bd3] Ra8 20.Qh5 g6 21.Qh3 e5  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bd3%20Ra8%2020.Qh5%20g6%2021.Qh3%20e5#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 [19.Bd3] Ra8 20.Qh5 g6 21.Qf3 Bd7  (sampled 23x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bd3%20Ra8%2020.Qh5%20g6%2021.Qf3%20Bd7#26))

not carrying it:

- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Nxa5 18.Nxa5 axb5 19.Nb3 Bd7 20.Rxa8 Rxa8 21.Bxd4 Bxd4+  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Nxa5%2018.Nxa5%20axb5%2019.Nb3%20Bd7%2020.Rxa8%20Rxa8%2021.Bxd4%20Bxd4%2B#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 d3 17.Bxb6 dxe2 18.Qxe2 axb6 19.c3 e5 20.fxe5 Nxe5 21.N3d4 Bg4  (sampled 4x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20d3%2017.Bxb6%20dxe2%2018.Qxe2%20axb6%2019.c3%20e5%2020.fxe5%20Nxe5%2021.N3d4%20Bg4#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 19.Qd2 Ne7 20.Nxd4 Ra8 21.Rfd1 Bd7  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Qd2%20Ne7%2020.Nxd4%20Ra8%2021.Rfd1%20Bd7#26))

### Concept 18 (branch): latents 1421, 3013, 9475, 11894; carried by 40% of the rollouts, its latents starting at ply 7: 2.4 effective routes (random lines: 3.5 at the 5th percentile), 2.5 effective boards (4.3)

- White Bishop to f2: 22% of carrying rollouts, 89% of the others (phi -0.68)
- Black Pawn to a6: 20% of carrying rollouts, 81% of the others (phi -0.61)
- trade on a7: 0% of carrying rollouts, 58% of the others (phi -0.60)

carrying it:

- 14.Nb5 Qb6 15.Bf2 Ne4 16.a5 Qc5 17.N5xd4 Nxd4 18.Bxd4 Qc7 19.Qd3 Nc5 20.Qc3 b6 21.Bf3 Bb7  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.Nb5%20Qb6%2015.Bf2%20Ne4%2016.a5%20Qc5%2017.N5xd4%20Nxd4%2018.Bxd4%20Qc7%2019.Qd3%20Nc5%2020.Qc3%20b6%2021.Bf3%20Bb7#26))
- 14.Nxd4 Nxd4 15.Bxd4 Nd5 16.Nxd5 Rxd5 17.c3 Bc5 18.Kh1 Bxd4 19.cxd4 Bd7 20.Rc1 Bc6 21.Bf3 Rd7  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.Nxd4%20Nxd4%2015.Bxd4%20Nd5%2016.Nxd5%20Rxd5%2017.c3%20Bc5%2018.Kh1%20Bxd4%2019.cxd4%20Bd7%2020.Rc1%20Bc6%2021.Bf3%20Rd7#26))
- 14.exf6 gxf6 15.Nxd4 Nxd4 16.Bxd4 Bc5 17.Nb5 Bxd4+ 18.Nxd4 e5 19.fxe5 fxe5 20.c3 exd4 21.cxd4 Qb6  (sampled 1x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20gxf6%2015.Nxd4%20Nxd4%2016.Bxd4%20Bc5%2017.Nb5%20Bxd4%2B%2018.Nxd4%20e5%2019.fxe5%20fxe5%2020.c3%20exd4%2021.cxd4%20Qb6#26))

not carrying it:

- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 19.Bd3 Bd7 20.Nc5 Be8 21.Ne4 Be7  (sampled 32x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bd3%20Bd7%2020.Nc5%20Be8%2021.Ne4%20Be7#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 19.Bf3 Bd7 20.Nc5 Be8 21.Ne4 Be7  (sampled 23x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bf3%20Bd7%2020.Nc5%20Be8%2021.Ne4%20Be7#26))
- 14.exf6 Bxf6 15.Nb5 Qb6 16.Bf2 a6 17.a5 Qa7 18.Nxa7 Rxa7 19.Bd3 Ra8 20.Qh5 g6 21.Qf3 Bd7  (sampled 23x; [Lichess](https://lichess.org/analysis/pgn/1.e4%20c5%202.Nf3%20d6%203.d4%20cxd4%204.Nxd4%20Nf6%205.Nc3%20Nc6%206.Bc4%20Qb6%207.Nb3%20e6%208.O-O%20Be7%209.a4%20O-O%2010.Be3%20Qc7%2011.Be2%20Rd8%2012.f4%20d5%2013.e5%20d4%2014.exf6%20Bxf6%2015.Nb5%20Qb6%2016.Bf2%20a6%2017.a5%20Qa7%2018.Nxa7%20Rxa7%2019.Bd3%20Ra8%2020.Qh5%20g6%2021.Qf3%20Bd7#26))

