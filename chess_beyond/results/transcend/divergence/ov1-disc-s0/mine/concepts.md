# Mined dynamic concepts

Tag ov1-disc-s0, checked against ov1-disc-s1. Decisive branch points: >= 30 rollouts, chosen move >= 75%. k in 2,3,4,5,6,8. Families: cosine >= 0.5, >= 3 solutions at >= 2 positions.

## S

best: 23, clean: 43, board: 672, weak: 126; best with a clear theme in its examples: 19

### Best, with a theme

| concept | theme (share of windows / base rate) | branch points | positions | replication | agreement | chosen > subpar at branch points | activating windows |
|---|---|---|---|---|---|---|---|
| S43 | two or more queen moves (100% / 17%) | 70 | 21 | 0.945 | 0.335 | Nxf8 > Rad1; Nxe4 > Bd4; Nxb4 > axb5; Bd4 > Kf7 | Qe4+ 32.Qg2 Qxg2+ 33.Rxg2 Re1+ 34.Rg1 Rxg1+ 35.Kxg1 Rf3 / 18.Bxe4 Qh4 19.Qxd2 Qxe4 20.Rae1 Qd4 21.Qxd4 Bxd4 22.Re8+ / Rf8 48.Qe2 Qe5 49.a4 Qa1+ 50.Kh2 Qe5+ 51.Kg1 Rae8 |
| S355 | two or more queen moves (100% / 17%) | 15 | 6 | 0.985 | 0.407 | Qb6 > Rb1; Qxb6 > Qc6; Qe7 > Rc1+; Qb3 > Qe7 | Qe7 45.Qxb3 Qe5 46.Qh3 Nf4 / Qf7 32.Qd6+ Qe7 33.Qf4+ Qf7 / 35.Qa3 Qe7 36.Qa6+ Qb7 37.Qa3 |
| S630 | two or more queen moves (100% / 17%) | 7 | 5 | 0.898 | 0.315 | Qb6 > Bxb3; Qd6 > Bh3; Qc5 > Qxf3; Qd5 > Bd4 | 25.Qc3 Qb6 26.h3 / 18.Qd4 Qe7 19.Rae1 / 24.Qh2 Qh6 25.Qe5 |
| S356 | king move (100% / 25%) | 15 | 4 | 0.893 | 0.398 | Rxb8 > Bd3; hxg7 > Qxe8; Rf1 > Re5; Nxd2 > Bg2 | 37.Rxb6 Ne8 38.a6 bxa6 39.Rxa6 Kb7 40.Re6 h5 41.g5 / 30.Kxd2 Rb8 31.Kc3 h5 32.Qc7 Rf8 33.b5 g5 34.b6 / R8d5 33.Rxd5 cxd5 34.Bd4 Kb7 35.Kb2 Kc6 36.a4 Rd2+ |
| S267 | two or more rook moves (100% / 28%) | 20 | 7 | 0.946 | 0.484 | Rxg3 > Qxc3; Ne3+ > Qf2; Rbh8 > Qc6; Qxf8 > Bxf3 | Rxb5 30.Rfd1 Rd5 31.R1xd5 exd5 32.Rd6 / Re8 25.Bc3 Re7 26.Kf2 Kh7 27.h4 / Kh7 27.g4 Rf4 28.gxf5 Rxf5 29.d7 |
| S97 | two or more pawn moves (100% / 28%) | 46 | 17 | 0.961 | 0.374 | b3 > Rh4; Bd2 > f4; Bd5 > h6; b6 > Nfe4 | a5 22.a4 b5 / 19.a3 a5 20.Rh1 / 14.a4 a5 15.c4 |
| S773 | two or more bishop moves (78% / 16%) | 4 | 4 | 0.963 | 0.391 | d4 > Nxf6+; Bf3 > Ndc4; Bf6 > Rxa2; Rb1 > a4 | 27.Bf3 h6 28.Bxf6 Bxf6 29.Rb3 Rd4 / 23.Bg2 Rae8 24.Ne4 b6 25.Bc1 Nc6 / Bc5 22.Qg5 Be7 23.Qe3 Bc5 24.Qg5 |
| S29 | two or more rook moves (89% / 28%) | 86 | 22 | 0.977 | 0.386 | b3 > Rc1; Rxg7 > Bxe5; Rxa1 > Bxa2; Rf8 > fxg2 | 48.gxh3 Qxh3+ 49.Rxh3 Ng3+ 50.Kg2 / 36.Nc3 Rc2 37.Ne2 Rc4 38.Ra1 / 30.Rh4 Rxh4 31.gxh4 Nxd3 32.Qg3 |
| S367 | two or more pawn moves (89% / 28%) | 15 | 6 | 0.859 | 0.471 | g4 > Re1; Rxe1+ > Bxd4; Be6 > Bh6; c3 > Rxf4 | d4 19.fxe5 dxe3 20.exf6 / g4 16.Qg3 f4 17.Qh4 / f6 25.Rxa8 Qxa8 26.cxd5 |
| S640 | two or more pawn moves (89% / 28%) | 7 | 4 | 0.938 | 0.435 | b5 > Rb8; b5 > O-O-O; f4 > Kg2; Qb3 > Qe2 | Nd4 40.Be3 Re8 / b5 18.c3 Qa3 / b5 15.c3 Qxd3 |
| S107 | two or more captures (89% / 34%) | 43 | 9 | 0.941 | 0.468 | Nd4 > Re3; bxa6 > Rxa6; fxe5 > Bxd7; Qxg3 > Rxa6 | Rxb7 33.Bxb7 Qxd2 34.fxe3 / Kxf8 32.Qxb6 e3 33.Qd8+ / 29.Rxh8 Kxh8 30.Qf2 Nxe2+ |
| S193 | two or more captures (89% / 34%) | 26 | 7 | 0.866 | 0.335 | Qxd6 > Na4; Rxg6 > e6; Qxf4 > Bf5; Bxd4 > Qd3 | axb5 24.Ne4 Nxe4 25.Re8 g6 26.f5 gxf5 / 21.f4 Nc4 22.Bc3 Ngxe3 23.Rfe1 Nxd5 24.Bd4 / 14.Ne4 dxe4 15.g4 exf3 16.g5 h6 17.Bd3 |
| S585 | check (67% / 12%) | 8 | 3 | 0.797 | 0.56 | Qb5+ > Qa5+; Nf3 > g3; Nb4 > g6 | 18.Nf7+ Kg8 19.Nh6+ / 21.Kg1 Qg3+ 22.Kh1 / 25.Kc1 Qa1+ 26.Kc2 |
| S364 | two or more queen moves (67% / 17%) | 15 | 6 | 0.797 | 0.555 | Qc4+ > Qc3; O-O-O > Ba5+; Rf8 > fxg2; Rg8 > Ng8 | 19.Qxc6 Qg4 20.Qd5 / Qxd3 18.Ne5 Qd4 / 25.Qa8 Ra7 26.Qe8 |
| S272 | no capture or check (89% / 40%) | 20 | 4 | 0.733 | 0.469 | Reb8 > Ra8; Rdc1 > Bf3; Rbh8 > a4; Rad1 > Re1 | Rfc8 23.Rhd1 h6 24.g3 / 23.Rdf1 h4 24.h3 b6 / Rag8 23.g3 R8g7 24.Kh2 |
| S489 | capture (100% / 57%) | 10 | 3 | 0.697 | 0.29 | Nc5 > Nb4; Nxb2 > Rd1; Qf3+ > Qb3 | Rxc2 32.Rd3 Rc1+ 33.Kg2 Qb1 34.Rg3 / 30.Rh5 Qg6 31.Rch1 Rd3 32.Qc4 Rxg3 / Nxb7 31.Bxf6+ Bxf6 32.Qc7 Qd1+ 33.Kh2 |
| S118 | king move (67% / 25%) | 41 | 13 | 0.957 | 0.39 | Rxd7 > Qxd7; Rdb1 > Qb3; Ne3+ > Qf2; Re3 > Qe2 | 25.Bc3 Re7 26.Kf2 Kh7 27.h4 / 29.Nxd1 Rc5 30.Rb8+ Bf8 31.Bb5 / 27.Ra1 Ng6 28.Ra7+ Kg8 29.Nxe6 |
| S748 | two or more rook moves (67% / 28%) | 5 | 3 | 0.82 | 0.265 | Rxd7 > Qxd7; Rf1 > Rb1; Qd6 > Qb6 | Qxd6 26.Ra7 Qf4 27.Rb2 / 16.Qc2 Qd6 17.Raa1 Rac8 / Rd1 32.Kg4 Rh1 33.Kf5 |
| S120 | no capture or check (67% / 40%) | 41 | 18 | 0.923 | 0.29 | Rf4 > Re3; Bd5 > Qb6; O-O-O > O-O; Qb6 > Qa4 | Kd6 41.Kd3 Bd5 42.Kc3 b6 / Rad8 21.Bf2 Qe6 22.h3 Nc3 / 21.Nd4 g6 22.f3 Kg7 23.Rhe1 |

### Best and clean, by cleanliness

| concept | tier | branch points | positions | k | replication (null 95th) | agreement (null 95th) | board | top activating windows |
|---|---|---|---|---|---|---|---|---|
| S21 | best | 103 | 10 | 2,3,4,5,6,8 | 0.969 (0.107) | 0.823 (0.008) | 0.77 | 29.Kf2 Ng4+ 30.Kg2 Nf6 / 25.Kf1 Nhf3 26.Kg2 Nh4+ / 23.Qh4 Rg4 24.Qh6 Rg6 |
| S236 | best | 22 | 12 | 2,3,4,5,6,8 | 0.971 (0.137) | 0.398 (0.009) | 0.763 | 31.Be5 Kh7 32.Bd4 Rc2 33.Qf4 / e6 28.a4 Ba6 29.a5 Rb8 / 30.Bb2 Nxc5 31.Kf2 Rd8 32.Kxe3 |
| S97 | best | 46 | 17 | 2,3,4,5,6,8 | 0.961 (0.182) | 0.374 (0.008) | 0.836 | a5 22.a4 b5 / 19.a3 a5 20.Rh1 / 14.a4 a5 15.c4 |
| S115 | clean | 42 | 17 | 2,3,4,5,6,8 | 0.97 (0.2) | 0.229 (0.008) | 0.797 | Kh8 22.Qxe2 Rxe2 / 19.axb3 Rxd3 20.Kxd3 / Qxa4 24.Qxa4 Rxa4 |
| S118 | best | 41 | 13 | 2,3,4,5,6,8 | 0.957 (0.113) | 0.39 (0.008) | 0.766 | 25.Bc3 Re7 26.Kf2 Kh7 27.h4 / 29.Nxd1 Rc5 30.Rb8+ Bf8 31.Bb5 / 27.Ra1 Ng6 28.Ra7+ Kg8 29.Nxe6 |
| S29 | best | 86 | 22 | 2,3,4,5,6,8 | 0.977 (0.259) | 0.386 (0.008) | 0.826 | 48.gxh3 Qxh3+ 49.Rxh3 Ng3+ 50.Kg2 / 36.Nc3 Rc2 37.Ne2 Rc4 38.Ra1 / 30.Rh4 Rxh4 31.gxh4 Nxd3 32.Qg3 |
| S107 | best | 43 | 9 | 2,3,4,5,6,8 | 0.941 (0.148) | 0.468 (0.008) | 0.831 | Rxb7 33.Bxb7 Qxd2 34.fxe3 / Kxf8 32.Qxb6 e3 33.Qd8+ / 29.Rxh8 Kxh8 30.Qf2 Nxe2+ |
| S267 | best | 20 | 7 | 2,3,4,5,6,8 | 0.946 (0.123) | 0.484 (0.011) | 0.709 | Rxb5 30.Rfd1 Rd5 31.R1xd5 exd5 32.Rd6 / Re8 25.Bc3 Re7 26.Kf2 Kh7 27.h4 / Kh7 27.g4 Rf4 28.gxf5 Rxf5 29.d7 |
| S364 | best | 15 | 6 | 2,3,4,5,6 | 0.797 (0.139) | 0.555 (0.016) | 0.823 | 19.Qxc6 Qg4 20.Qd5 / Qxd3 18.Ne5 Qd4 / 25.Qa8 Ra7 26.Qe8 |
| S653 | clean | 6 | 2 | 3,4,5,6,8 | 0.815 (0.183) | 0.662 (0.039) | 0.786 | 15.Qxa4 Rxa4 16.Nxa4 Nf6 17.Bd2 Ne4 18.Rc1 Nxd2 19.Kxd2 / Rxg3 40.Nxg3 Qg5+ 41.Ke1 Qxg3+ 42.Kd2 Qf2+ 43.Kc1 Qe1+ / 31.Nxb8 Rxb8 32.Qxa6+ Ke7 33.Bxd7 Kxd7 34.Qa7+ Kd6 35.Qxb8+ |
| S438 | best | 12 | 5 | 2,3,4,5,6,8 | 0.934 (0.153) | 0.424 (0.014) | 0.81 | 31.Kc4 b6 32.Bd4 / 26.Bxa1 a5 27.b5 / Nf5 31.Kf2 Nd4 |
| S367 | best | 15 | 6 | 2,3,4,5,6 | 0.859 (0.123) | 0.471 (0.014) | 0.794 | d4 19.fxe5 dxe3 20.exf6 / g4 16.Qg3 f4 17.Qh4 / f6 25.Rxa8 Qxa8 26.cxd5 |
| S640 | best | 7 | 4 | 2,3 | 0.938 (0.077) | 0.435 (0.026) | 0.835 | Nd4 40.Be3 Re8 / b5 18.c3 Qa3 / b5 15.c3 Qxd3 |
| S120 | best | 41 | 18 | 2,3,4,5,6 | 0.923 (0.182) | 0.29 (0.008) | 0.845 | Kd6 41.Kd3 Bd5 42.Kc3 b6 / Rad8 21.Bf2 Qe6 22.h3 Nc3 / 21.Nd4 g6 22.f3 Kg7 23.Rhe1 |
| S253 | clean | 21 | 9 | 2,3,4,5,6,8 | 0.836 (0.124) | 0.243 (0.011) | 0.82 | Be7 19.Bf3 h6 / 19.Bd2 Bd7 20.Rfb1 / Bg8 27.Bd2 Bf7 |
| S355 | best | 15 | 6 | 2,3,4,5,6,8 | 0.985 (0.165) | 0.407 (0.014) | 0.795 | Qe7 45.Qxb3 Qe5 46.Qh3 Nf4 / Qf7 32.Qd6+ Qe7 33.Qf4+ Qf7 / 35.Qa3 Qe7 36.Qa6+ Qb7 37.Qa3 |
| S773 | best | 4 | 4 | 2,3,5,8 | 0.963 (0.178) | 0.391 (0.013) | 0.786 | 27.Bf3 h6 28.Bxf6 Bxf6 29.Rb3 Rd4 / 23.Bg2 Rae8 24.Ne4 b6 25.Bc1 Nc6 / Bc5 22.Qg5 Be7 23.Qe3 Bc5 24.Qg5 |
| S414 | clean | 13 | 3 | 2,3,4,5,6,8 | 0.905 (0.106) | 0.851 (0.018) | 0.79 | Kg8 50.Qf7+ Kh8 / 26.Kg2 Nh4+ 27.Kg1 / 16.Nf7+ Kg8 17.Nh6+ |
| S124 | clean | 39 | 18 | 2,3,4,5,6 | 0.841 (0.178) | 0.194 (0.008) | 0.813 | 17.Rad1 Rab8 18.h4 / Rfc8 18.Rfc1 Qd8 / Rac8 15.Rfd1 h6 |
| S571 | clean | 8 | 2 | 2,3,4,6 | 0.834 (0.21) | 0.757 (0.024) | 0.836 | 18.Rc2 Rac8 19.Rac1 Rc5 20.Na4 / Rac8 19.Qe2 a6 20.a3 Be8 / 22.Rac1 Bb5 23.Rfe1 Rfe8 24.Kg1 |
| S630 | best | 7 | 5 | 2,3,4 | 0.898 (0.084) | 0.315 (0.026) | 0.845 | 25.Qc3 Qb6 26.h3 / 18.Qd4 Qe7 19.Rae1 / 24.Qh2 Qh6 25.Qe5 |
| S43 | best | 70 | 21 | 2,3,4,5,6,8 | 0.945 (0.35) | 0.335 (0.008) | 0.781 | Qe4+ 32.Qg2 Qxg2+ 33.Rxg2 Re1+ 34.Rg1 Rxg1+ 35.Kxg1 Rf3 / 18.Bxe4 Qh4 19.Qxd2 Qxe4 20.Rae1 Qd4 21.Qxd4 Bxd4 22.Re8+ / Rf8 48.Qe2 Qe5 49.a4 Qa1+ 50.Kh2 Qe5+ 51.Kg1 Rae8 |
| S154 | clean | 33 | 14 | 2,3,4,5,6 | 0.831 (0.124) | 0.159 (0.009) | 0.836 | 26.h4 g6 27.Kg2 / g6 34.h4 h5 / 26.h3 h4 27.gxh4 |
| S193 | best | 26 | 7 | 2,3,4,5,6,8 | 0.866 (0.226) | 0.335 (0.01) | 0.762 | axb5 24.Ne4 Nxe4 25.Re8 g6 26.f5 gxf5 / 21.f4 Nc4 22.Bc3 Ngxe3 23.Rfe1 Nxd5 24.Bd4 / 14.Ne4 dxe4 15.g4 exf3 16.g5 h6 17.Bd3 |
| S757 | clean | 5 | 3 | 3,4,5,8 | 0.954 (0.127) | 0.716 (0.047) | 0.769 | 25.Kf1 Nhf3 26.Kg2 Nh4+ 27.Kf1 Nhf3 / 28.Kg1 Nf6 29.Kf2 Ng4+ 30.Kg1 Nf6 / 27.Bh3 Rdd8 28.Bg2 Rd7 29.Bh3 Rdd8 |
| S525 | best | 9 | 6 | 2,3,4,5,6 | 0.752 (0.084) | 0.281 (0.026) | 0.838 | Qc7 28.Qg4 Rf8 29.Bxh6 g6 / 21.Rxa8+ Bxa8 22.Nxb5 Bxd5 23.Nxc7 / Rae8 27.Bxh6 Rxe1 28.Rxe1 Qc5+ |
| S378 | clean | 14 | 7 | 2,3,4,5,6 | 0.733 (0.078) | 0.216 (0.016) | 0.691 | Kc7 18.Rxd8 Rxd8 / 25.Qe3 f4 26.Qd4 / e5 22.Nd5 Qc6 |
| S784 | clean | 4 | 2 | 3,5,6 | 0.974 (0.148) | 0.569 (0.013) | 0.826 | 44.Kh1 Qe7 45.Qxb3 Qe5 46.Qh3 Nf4 / Qb6 29.Qxe5 Re8 30.Qc3 a5 31.g4 / 23.Rfd1 Qb6 24.Ne5 Rd8 25.e4 Nf6 |
| S272 | best | 20 | 4 | 2,3,4,5,6,8 | 0.733 (0.167) | 0.469 (0.011) | 0.829 | Rfc8 23.Rhd1 h6 24.g3 / 23.Rdf1 h4 24.h3 b6 / Rag8 23.g3 R8g7 24.Kh2 |
| S858 | clean | 3 | 2 | 2 | 0.823 (0.049) | 0.487 (0.0) | 0.824 | 28.Re7 Ne2+ 29.Rxe2 / 31.h5 Qh4+ 32.Qxh4 / 31.Ne8 Bxh4 32.Nc7 |
| S356 | best | 15 | 4 | 2,3,4,5,6,8 | 0.893 (0.158) | 0.398 (0.014) | 0.78 | 37.Rxb6 Ne8 38.a6 bxa6 39.Rxa6 Kb7 40.Re6 h5 41.g5 / 30.Kxd2 Rb8 31.Kc3 h5 32.Qc7 Rf8 33.b5 g5 34.b6 / R8d5 33.Rxd5 cxd5 34.Bd4 Kb7 35.Kb2 Kc6 36.a4 Rd2+ |
| S434 | clean | 12 | 2 | 2,3,4,5,6 | 0.781 (0.199) | 0.585 (0.013) | 0.789 | 31.Nxd7 Rxb5 32.Qxe4 Rb8 33.Qd5+ Kh8 / Qxa1 18.Nb5 cxb5 19.h4 Qxf1+ 20.Kh2 / Qxh7 33.Kg2 Be5 34.Nxe5 dxe5 35.Kg3 |
| S667 | clean | 6 | 2 | 3,4,5,6,8 | 0.9 (0.154) | 0.518 (0.039) | 0.843 | g4 15.Qxf5 Qxf5 16.Rxf5 Rxh5 17.Rxh5 / 14.Rf1+ Kg7 15.g3 c6 16.Nc3 Rf8 / Kf7 20.Qxb7+ Kg6 21.Qg2+ Kf7 22.Na3 |
| S747 | clean | 5 | 2 | 2,3 | 0.653 (0.071) | 0.277 (0.047) | 0.799 | Ne3 20.Qf2 Qb6 21.Rfe1 / Bd3 21.Bh6 Rxf3 22.Rxf3 / 40.Nd7 Qd3 41.Qf3 Qxf3 |
| S748 | best | 5 | 3 | 2,3,4,6 | 0.82 (0.19) | 0.265 (0.047) | 0.837 | Qxd6 26.Ra7 Qf4 27.Rb2 / 16.Qc2 Qd6 17.Raa1 Rac8 / Rd1 32.Kg4 Rh1 33.Kf5 |
| S349 | clean | 15 | 6 | 3,4,5,6,8 | 0.883 (0.176) | 0.249 (0.016) | 0.72 | Qe7 31.Qf4+ Qf7 32.Qd6+ Qe7 33.Qf4+ / Qb7 35.Qa3 Qe7 36.Qa6+ Qb7 37.Qa3 / 21.Qd2 Qc5 22.Qf2 Qb4+ 23.Qd2 Qc5 |
| S758 | clean | 5 | 2 | 2,3,4 | 0.594 (0.094) | 0.327 (0.047) | 0.834 | c6 26.Rc3 Bd5 / dxc3 27.Rxc3 Rad8 / 17.Be3 Qb3 18.f3 |
| S608 | clean | 7 | 2 | 2,3,4,5,6 | 0.783 (0.149) | 0.431 (0.026) | 0.844 | Rxe8 24.Nf3 Bxb2 / Nc4 24.Rd4 b5 / 21.Kh2 Bc5 22.Nxf7 |
| S177 | clean | 29 | 8 | 2,3,4,5,6,8 | 0.674 (0.18) | 0.126 (0.01) | 0.824 | Kg5 31.Rf7 Rd7 32.b4 Rxf7 33.gxf7 Nd7 / Rxe7 35.Rg3 Qd2+ 36.Kf3 Qxc3+ 37.Kg4 Qd4+ / 34.Rh6 Kf7 35.Rh8 Rxh8 36.gxh8=Q Qxe6 37.Qh7+ |
| S585 | best | 8 | 3 | 2,3,4,5,6,8 | 0.797 (0.176) | 0.56 (0.024) | 0.629 | 18.Nf7+ Kg8 19.Nh6+ / 21.Kg1 Qg3+ 22.Kh1 / 25.Kc1 Qa1+ 26.Kc2 |
| S611 | clean | 7 | 2 | 2,3,4,5,6,8 | 0.856 (0.236) | 0.39 (0.026) | 0.822 | 30.Rcxc3 Bb4 31.Rxc4 dxc4+ 32.Kc2 / 29.Rxe3 Qxe3+ 30.Kh1 Qe1+ 31.Kh2 / 28.Rc4 Nd3 29.Rce4 Nxe1 30.Rxe1 |
| S327 | clean | 16 | 6 | 2,3,4,5,6,8 | 0.703 (0.15) | 0.135 (0.013) | 0.738 | Nxf1 32.Kxf1 Qb3 33.Nd7 Rf7 34.Nc5 / 39.Nf3 Qe6 40.Nd4 Qe5 41.Nf3 Qe6 / 30.Nc5 h4 31.Nd7 Ra8 32.b3 h3 |
| S357 | clean | 15 | 8 | 2,3,4,5,6,8 | 0.621 (0.181) | 0.159 (0.014) | 0.728 | 27.Bb2 Qb3 28.h4 h5 29.g4 Rd2 / Kxd8 44.Bxg7 g5 45.Bf6 g4 46.fxg4 / 30.Rf3 Rd2 31.e6 f6 32.h5 Qxh5 |
| S680 | clean | 6 | 2 | 2,3,4 | 0.65 (0.116) | 0.487 (0.039) | 0.825 | 21.Qf2 f5 22.Qf4 Rf7 / Kxg7 32.Rh7+ Kg6 33.Rh8 / 29.Be5 Bf5 30.Re2 Bg7 |
| S489 | best | 10 | 3 | 3,4,5,6,8 | 0.697 (0.133) | 0.29 (0.018) | 0.721 | Rxc2 32.Rd3 Rc1+ 33.Kg2 Qb1 34.Rg3 / 30.Rh5 Qg6 31.Rch1 Rd3 32.Qc4 Rxg3 / Nxb7 31.Bxf6+ Bxf6 32.Qc7 Qd1+ 33.Kh2 |
| S780 | clean | 4 | 2 | 2,3,5,6 | 0.841 (0.16) | 0.152 (0.013) | 0.824 | 47.Rxe2 Rxe2 48.Rxf3 / Rd8 31.Re7+ Kf8 / dxe5 43.Nd5 Qd6 |
| S815 | clean | 4 | 3 | 2,4,6 | 0.793 (0.171) | 0.167 (0.013) | 0.828 | 39.Kg1 Qe3+ 40.Kh1 / Kh7 35.Kc6 Re3 / Rf8 39.Kg2 h5 |
| S707 | clean | 5 | 2 | 3,4,5,6 | 0.814 (0.207) | 0.4 (0.047) | 0.847 | Be6 17.f4 Qf8 18.Qh5 f6 19.f5 / 25.Nc4 f4 26.Ne5 Bf5 27.Ka1 Bh4 / 17.Kh1 Rg8 18.c3 Qe5 19.Bf4 Qf5 |
| S242 | clean | 22 | 7 | 2,3,4,5,6 | 0.41 (0.113) | 0.127 (0.011) | 0.831 | 16.Bxe7 Ne3 17.Bxd8 / Bxf3 17.Bxf6 Bxe2 / 21.Nxd8 Nxd1 22.Nxb7 |
| S745 | clean | 5 | 2 | 2,3 | 0.856 (0.195) | 0.194 (0.047) | 0.822 | Rxc6 22.Nd6+ Bxd6 23.Rxd6+ / 29.Bxd4 Rdxd4+ 30.Nxd4 Rxd4+ / Rxd2 20.Qxb2 Qxb2 21.Rxb2 |
| S561 | clean | 8 | 2 | 2,3,4,5,6,8 | 0.532 (0.096) | 0.525 (0.024) | 0.822 | 26.Rbc1 Rc7 27.Rc3 / Nc6 16.Ne4 Bg4 / 21.c4 Rac8 22.c5 |
| S403 | clean | 13 | 4 | 2,3,4,5,6,8 | 0.537 (0.097) | 0.178 (0.018) | 0.768 | 33.Ng5 Rf8 34.Nh7 / e4 31.Rxb2 Qa1+ / 18.Nf3 Bf5 19.Nd2 |
| S778 | clean | 4 | 2 | 4,5,6 | 0.591 (0.186) | 0.265 (0.013) | 0.83 | 15.Qb3 Qd7 16.Bg5 Nc6 17.Be3 Rad8 18.Rfd1 / a6 17.Qb3 Rfd8 18.Rc2 Rac8 19.Rac1 Rc5 / 13.Be2 Re8 14.O-O Be6 15.Bf3 Rad8 16.Re1 |
| S788 | clean | 4 | 2 | 3,4,5 | 0.632 (0.151) | 0.217 (0.013) | 0.833 | 26.Nb3 Bc4 27.Nd4 Ra6 28.Nxf5 / Qe7 31.Qf4+ Qf7 32.Qd6+ Qe7 / Qb7 35.Qa3 Qe7 36.Qa6+ Qb7 |
| S785 | clean | 4 | 3 | 2,3,6,8 | 0.374 (0.054) | 0.195 (0.013) | 0.839 | 13.Qd2 Qxd2+ 14.Kxd2 Bf5 / 19.Kb1 Bc7 20.Be3 Nb4 / 16.Bc3 Bd6 17.Nd2 Nd7 |
| S362 | clean | 15 | 3 | 2,3,4,5,6 | 0.43 (0.1) | 0.217 (0.014) | 0.841 | 28.Nf6+ Kh8 29.Nxe8 / Rxe2 29.Bxe5 Qxe5 / Nxe3 24.Bxe6+ Kh8 |
| S656 | clean | 6 | 3 | 2,3,5,6,8 | 0.257 (0.096) | 0.364 (0.047) | 0.829 | Ng6 21.Kb1 Rfd8 / 17.Nf1 Re8 18.Ng3 / 20.Rhf1 Ke7 21.g3 |
| S522 | clean | 9 | 2 | 2,3,4,5,6,8 | 0.547 (0.239) | 0.378 (0.026) | 0.816 | Qg5 20.Ne4 Nxe4 / 20.dxe5 Nd5 21.h3 / axb6 27.Qxd6 Ra4 |
| S501 | clean | 10 | 3 | 2,3,4 | 0.431 (0.126) | 0.164 (0.018) | 0.846 | Nxg4+ 31.Bxg4 Rhxg4 / 33.Re4 Rxd4 34.Rxd4 / Rb6 21.Bxd6 Rxd6 |
| S751 | clean | 5 | 2 | 2,3 | 0.285 (0.092) | 0.185 (0.047) | 0.804 | 22.Qg7+ Ke6 23.Qxb7 / 31.Qg2 Qxg5 32.Qxh3 / 49.Ke1 Qg1+ 50.Kd2 |

## W

best: 19, clean: 31, board: 662, weak: 132; best with a clear theme in its examples: 15

### Best, with a theme

| concept | theme (share of windows / base rate) | branch points | positions | replication | agreement | chosen > subpar at branch points | activating windows |
|---|---|---|---|---|---|---|---|
| W133 | two or more queen moves (100% / 18%) | 32 | 10 | 0.986 | 0.321 | Qxd4 > Qg3; Bb4 > Bxe7; Qd5 > b6; Qd8+ > Rh8+ | Qd8 44.Qc6+ Kf7 45.Qc4+ Kg7 46.Qc3+ / Qe7 31.Qf4+ Ke8 32.Bg6+ Kd8 33.Qh4 / Qe8 27.Qg5 Be7 28.Qf4 g5 29.Qxc7+ |
| W500 | two or more knight moves (100% / 20%) | 9 | 6 | 0.719 | 0.27 | Nd6+ > Nxd4; Nd4 > Bxe5; Ng6+ > Qc3+; Nxf4 > Bxf4 | 25.Nd5 Nxc4 26.Ne7+ Kd7 27.Nc6 Ra8 28.Rd1 Ke6 29.Rxd3 / Nxa3 33.Kb2 Nac4+ 34.Kb3 Ne3+ 35.Kb2 Rd2 36.Kc1 Rxc2+ / Nxf5 27.Rf3 Nd4 28.Rg3 Nf5 29.Rg6 Nh4 30.Rxe6 Nf5 |
| W51 | king move (100% / 22%) | 61 | 15 | 0.95 | 0.437 | Nb5 > Qc8; Qc4+ > e3; Rd1 > b4; Nd6 > Bxe5 | 32.Kg2 Kf6 33.Kf3 g5 34.g4 hxg4+ / 28.Kh2 Qxh5+ 29.Kg1 Qd1+ 30.Kh2 Qh5+ / 30.Rc1 Rb3 31.Rc8+ Kf7 32.Rb8 Rb1+ |
| W347 | two or more pawn moves (100% / 26%) | 15 | 10 | 0.938 | 0.341 | a5 > Qa3+; b3 > Rb1; b5 > Nf6; O-O > Ng4 | 21.a4 b6 22.c3 / 16.a4 a5 17.c4 / 31.c3 a4 32.Kc2 |
| W241 | two or more pawn moves (89% / 26%) | 20 | 3 | 0.833 | 0.309 | bxc3 > Qxc3; Rxd4 > Rxh6+; Rf5 > h5 | 22.Bh3 c6 23.Rhd1 Qf6 24.f4 / Bd7 22.c5 c6 23.d6 a5 / 25.Be3 Rfc8 26.a4 f5 27.exf5 |
| W211 | two or more bishop moves (78% / 18%) | 22 | 9 | 0.965 | 0.447 | Nxd2 > Rd1; Bxe5 > Nxe5; Be2 > Nd5; Bg2 > Bxc6 | Be7 23.Qe3 Bc5 24.Qg3 Bd6 25.Qe3 / Bg7 25.Bc1 h5 26.Bf4 Qe7 27.Bxe5 / 28.Be2 Rxa3 29.d4 Ne4 30.d5 Nf2+ |
| W311 | two or more knight moves (78% / 20%) | 17 | 6 | 0.912 | 0.464 | Ng3+ > Rg5+; c4 > f4; Kb1 > f4; Nc2 > Rf2 | Bxf3 17.Bxf6 Bxd1 / Nf3+ 21.Kg2 Nxd4 / Nxe3 19.Nxe8 Nxc2 |
| W663 | two or more knight moves (78% / 20%) | 6 | 3 | 0.945 | 0.334 | Rxa1 > Bxe6; Nxd4 > a6; Rxe7 > Nd5 | 24.Rxa2 Nxe4 25.Nxe5 Re8 26.Nf3 Nf6 / Ne5 19.Rfb1 Nc4 20.Qd1 b6 21.Nb5 / 14.Nd4 Nxd4 15.Bxd4 Bxb5 16.Bxf6 Qxf6 |
| W356 | two or more captures (100% / 43%) | 14 | 3 | 0.899 | 0.563 | Ng3 > g3; h4 > Rae8; Nxe5 > g5 | 24.Nc5 Bxc5 25.Rxc5 Qxd3 26.Rxc7 Rd7 27.Rxd7 / dxe5 14.Nxe5 Nxd5 15.Bxd5 Bxe5 16.Bxa8 Bxa1 / 16.Bxh6 fxe4 17.dxe4 Rf7 18.Nd2 Rbf8 19.Nf3 |
| W392 | king move (78% / 22%) | 13 | 6 | 0.777 | 0.279 | Re2 > Rf4; Ne5 > h6; Nh5 > Qe5; Kxf7 > Nxc2 | 26.Kd1 Nxf4 27.gxf4 / Kc7 17.Rxd8 Rxd8 / 22.Kf3 Qe4+ 23.Kg3 |
| W293 | two or more rook moves (78% / 25%) | 17 | 9 | 0.915 | 0.33 | h5 > Qxa8; Re7 > Kf7; Rxg4+ > Rh4; Rc4 > Re4 | 29.Rh2 Rxh2 30.Qxh2 Qc4+ 31.Ne2 / Rxc3+ 41.Kg4 Rc4+ 42.Kg5 Rc3 / 33.Rd1 Bb4 34.Nd5 Bc5+ 35.Bxc5 |
| W178 | two or more pawn moves (78% / 26%) | 25 | 6 | 0.973 | 0.429 | Bxa6 > e5; Qxd8 > Kb7; Nxe6 > Re1; Nxe8 > Qh3 | Kxf7 25.f4 Rxe3 26.Kd2 Rh3 27.Ke2 Rxh2+ 28.Ke3 Rxc2 / 17.Bxb7 Rc8 18.Bxc8 b4 19.cxb4 a5 20.bxa5 f5 21.a6 / Nxe4 19.Rd1 Nf6 20.c3 Bd6 21.b4 Rhe8 22.Kf2 a5 |
| W146 | two or more queen moves (67% / 18%) | 29 | 10 | 0.943 | 0.459 | Nxe1 > Be6; Rxg4 > Qe3; Qxd3 > Qg5; Rxe6 > fxe6 | Kg7 25.Rae1 Bxh2+ 26.Kxh2 d4 27.cxd4 cxd4 / Bxa1 22.Nc4 Rde8+ 23.Kd2 Bg4 24.Ne3 Bf3 / Bf8 21.Qxc7 Qb2 22.a5 Bb4 23.a6 Bc3 |
| W101 | two or more rook moves (67% / 25%) | 39 | 15 | 0.917 | 0.261 | Rbb1 > Rb3; Ra4 > Qxb4; Rxa1 > Rfa8; Rd5 > Nxe5 | 24.Re8+ Rf8 25.Rxf8+ / f4 26.Rg2 f3 / Rxa2 23.Ra1 Rxa1 |
| W444 | no capture or check (67% / 28%) | 11 | 3 | 0.887 | 0.332 | Qc6 > Qb5; Be5 > Bd6; Qc1+ > Nc4 | 19.Be5 Bf6 20.Bf4 Bg5 / 30.Ne4 Qf5 31.Nd6 Qf6 / Kc5 27.Qa5+ Kc6 28.Qa6+ |

### Best and clean, by cleanliness

| concept | tier | branch points | positions | k | replication (null 95th) | agreement (null 95th) | board | top activating windows |
|---|---|---|---|---|---|---|---|---|
| W51 | best | 61 | 15 | 2,3,4,5,6,8 | 0.95 (0.15) | 0.437 (0.007) | 0.833 | 32.Kg2 Kf6 33.Kf3 g5 34.g4 hxg4+ / 28.Kh2 Qxh5+ 29.Kg1 Qd1+ 30.Kh2 Qh5+ / 30.Rc1 Rb3 31.Rc8+ Kf7 32.Rb8 Rb1+ |
| W242 | clean | 20 | 10 | 2,3,4,5,6 | 0.915 (0.074) | 0.198 (0.01) | 0.827 | 41.Qf2 Qd7 42.Ne3 / Qa7 34.Qe3 Kg7 / Qb7 21.Qc2 b5 |
| W211 | best | 22 | 9 | 2,3,4,5,6,8 | 0.965 (0.122) | 0.447 (0.013) | 0.758 | Be7 23.Qe3 Bc5 24.Qg3 Bd6 25.Qe3 / Bg7 25.Bc1 h5 26.Bf4 Qe7 27.Bxe5 / 28.Be2 Rxa3 29.d4 Ne4 30.d5 Nf2+ |
| W311 | best | 17 | 6 | 2,3,4,5,6 | 0.912 (0.119) | 0.464 (0.011) | 0.791 | Bxf3 17.Bxf6 Bxd1 / Nf3+ 21.Kg2 Nxd4 / Nxe3 19.Nxe8 Nxc2 |
| W6 | best | 143 | 43 | 2,3,4,5,6,8 | 0.986 (0.283) | 0.325 (0.007) | 0.789 | 20.Qxf3 Re5 21.Rg1 Rfe8 22.Qxf7+ / 24.Bxa7 Nc4 25.Bxc4 Bxc4 26.Rxe8 / 30.hxg4 Rg8 31.f3 Ke6 32.Bd4 |
| W9 | clean | 132 | 13 | 2,3,4,5,6,8 | 0.966 (0.136) | 0.619 (0.007) | 0.791 | Ng6 20.Qf3 Ne5 / Nc6 24.Qb3 Na5 / 19.Qe4 Nf6 20.Qe5 |
| W347 | best | 15 | 10 | 2,3,4 | 0.938 (0.118) | 0.341 (0.014) | 0.817 | 21.a4 b6 22.c3 / 16.a4 a5 17.c4 / 31.c3 a4 32.Kc2 |
| W146 | best | 29 | 10 | 2,3,4,5,6,8 | 0.943 (0.22) | 0.459 (0.008) | 0.763 | Kg7 25.Rae1 Bxh2+ 26.Kxh2 d4 27.cxd4 cxd4 / Bxa1 22.Nc4 Rde8+ 23.Kd2 Bg4 24.Ne3 Bf3 / Bf8 21.Qxc7 Qb2 22.a5 Bb4 23.a6 Bc3 |
| W356 | best | 14 | 3 | 2,3,4,5,6,8 | 0.899 (0.096) | 0.563 (0.014) | 0.774 | 24.Nc5 Bxc5 25.Rxc5 Qxd3 26.Rxc7 Rd7 27.Rxd7 / dxe5 14.Nxe5 Nxd5 15.Bxd5 Bxe5 16.Bxa8 Bxa1 / 16.Bxh6 fxe4 17.dxe4 Rf7 18.Nd2 Rbf8 19.Nf3 |
| W101 | best | 39 | 15 | 2,3,4,5,6,8 | 0.917 (0.149) | 0.261 (0.007) | 0.822 | 24.Re8+ Rf8 25.Rxf8+ / f4 26.Rg2 f3 / Rxa2 23.Ra1 Rxa1 |
| W133 | best | 32 | 10 | 2,3,4,5,6,8 | 0.986 (0.165) | 0.321 (0.009) | 0.753 | Qd8 44.Qc6+ Kf7 45.Qc4+ Kg7 46.Qc3+ / Qe7 31.Qf4+ Ke8 32.Bg6+ Kd8 33.Qh4 / Qe8 27.Qg5 Be7 28.Qf4 g5 29.Qxc7+ |
| W24 | best | 85 | 26 | 2,3,4,5,6,8 | 0.971 (0.311) | 0.344 (0.007) | 0.785 | 28.Ne7 Rxe7 29.Ra8 Rc7 / Nf5 28.Re8+ Kg7 29.d5 / Rxe4 24.Rxc7 h6 25.Rxb7 |
| W460 | clean | 10 | 2 | 3,4,5,6,8 | 0.806 (0.091) | 0.588 (0.015) | 0.849 | 23.Bg3 Rg4 24.Qf3 O-O-O / Be6 21.Bb5+ c6 22.Bc4 / 28.e6 fxe6 29.Rxe6 Rxe6 |
| W293 | best | 17 | 9 | 2,3,4,5,6,8 | 0.915 (0.184) | 0.33 (0.011) | 0.792 | 29.Rh2 Rxh2 30.Qxh2 Qc4+ 31.Ne2 / Rxc3+ 41.Kg4 Rc4+ 42.Kg5 Rc3 / 33.Rd1 Bb4 34.Nd5 Bc5+ 35.Bxc5 |
| W422 | clean | 11 | 2 | 4,5,6,8 | 0.986 (0.196) | 0.678 (0.015) | 0.788 | 39.Qb7+ Qc7 40.Qb3 Rxf6 41.Be6+ Kd8 42.Bc4 Rd6 43.Qe3 / 36.Qc1 Qd8 37.Qd1 Bc7 38.Qc1 Bb6 39.Qd1 Qe7 40.Qc1 / Qf7 30.Qd6+ Qe7 31.Qf4+ Ke8 32.Bg6+ Kd8 33.Qh4 Be4+ |
| W178 | best | 25 | 6 | 2,3,4,5,6,8 | 0.973 (0.233) | 0.429 (0.009) | 0.817 | Kxf7 25.f4 Rxe3 26.Kd2 Rh3 27.Ke2 Rxh2+ 28.Ke3 Rxc2 / 17.Bxb7 Rc8 18.Bxc8 b4 19.cxb4 a5 20.bxa5 f5 21.a6 / Nxe4 19.Rd1 Nf6 20.c3 Bd6 21.b4 Rhe8 22.Kf2 a5 |
| W443 | clean | 11 | 9 | 2,3,4,5 | 0.846 (0.153) | 0.162 (0.015) | 0.842 | 29.d8=Q+ Nxd8 30.Rxd8+ / 24.Rf8+ Rxf8 25.Bxf8 / Rd2 26.Nxd2 cxd2 |
| W628 | clean | 7 | 2 | 2,3,4,6 | 0.921 (0.131) | 0.529 (0.026) | 0.826 | 17.Nc3 Ne5 18.Nxe5 / 18.Re1 Bxg5 19.Rxe4+ / Bg4 19.Bxg4 Nxg4 |
| W462 | best | 10 | 5 | 2,3,4,5,6,8 | 0.886 (0.151) | 0.294 (0.015) | 0.791 | Kh8 30.d5+ Be5 / 29.Qg6+ Bg7 30.Bh6 / Kg7 28.Qd2 Bf6 |
| W733 | clean | 5 | 2 | 2,4,5,8 | 0.956 (0.148) | 0.456 (0.026) | 0.788 | b6 20.Bb4 a5 / 28.Bxc5 b6 29.Ba3 / 27.Nc6 Nd5 28.Bc5 |
| W663 | best | 6 | 3 | 3,4,5,6 | 0.945 (0.175) | 0.334 (0.027) | 0.816 | 24.Rxa2 Nxe4 25.Nxe5 Re8 26.Nf3 Nf6 / Ne5 19.Rfb1 Nc4 20.Qd1 b6 21.Nb5 / 14.Nd4 Nxd4 15.Bxd4 Bxb5 16.Bxf6 Qxf6 |
| W579 | best | 8 | 3 | 2,3,4 | 0.831 (0.094) | 0.26 (0.023) | 0.762 | exd4 13.cxd4 Rfe8 / Kf7 30.Nxc8 Rxc8 / 19.Bd3 Bxd3 20.Qxd3 |
| W99 | clean | 39 | 10 | 2,3,4,5,6,8 | 0.907 (0.179) | 0.215 (0.008) | 0.788 | 21.Bxg7 Rg8 22.Bf6+ Kd7 / 31.Bxb2 Rc2 32.Bf6 Rxd2 / 29.Be5 a5 30.c4 bxc4 |
| W290 | clean | 18 | 12 | 2,3,4,5,6,8 | 0.932 (0.274) | 0.128 (0.011) | 0.822 | 39.Be3 Ng7 40.c4 Ne6 41.c5 Nd8 42.d4 / Kf7 28.Nxa8 Nf6 29.Nc7 Ne4 30.Qf4+ Nf6 / gxf6 27.Nh4 Kg7 28.Nf5+ Kg6 29.Ne7+ Kg5 |
| W151 | clean | 29 | 3 | 2,3,4,5,6,8 | 0.965 (0.149) | 0.604 (0.008) | 0.726 | Nh4+ 23.Kg1 Nf3+ / Qg6+ 34.Kc3 Qg3+ / 20.Qg3 Nh5 21.Qg4 |
| W236 | clean | 21 | 9 | 2,3,4,5,6,8 | 0.75 (0.153) | 0.202 (0.013) | 0.794 | 30.cxd3 g5 31.Kf2 f6 32.Ke2 Kf7 / Qxh2+ 24.Kg4 Qg2+ 25.Kf4 Qh2+ 26.Ke4 / 25.Nxb7 Qxb7 26.Qc4 c5 27.Qxc5 Qxb3 |
| W105 | clean | 38 | 15 | 2,3,4,5,6,8 | 0.864 (0.132) | 0.112 (0.007) | 0.838 | dxc4 18.Nxc4 Bxc4 / 18.e4 Nxe4 19.Bxe4 / 16.b4 Nxb4 17.axb4 |
| W322 | clean | 16 | 4 | 2,3,4,5,6,8 | 0.72 (0.147) | 0.237 (0.011) | 0.811 | Rxe7 16.Qd2 Nf6 17.Rad1 Be6 / 17.Ng3 Rad8 18.Bc2 h6 19.Bb2 / dxe5 12.Bg5 Rd8 13.Qe2 Be6 |
| W392 | best | 13 | 6 | 2,3,4 | 0.777 (0.09) | 0.279 (0.014) | 0.75 | 26.Kd1 Nxf4 27.gxf4 / Kc7 17.Rxd8 Rxd8 / 22.Kf3 Qe4+ 23.Kg3 |
| W609 | clean | 7 | 5 | 2,4,5 | 0.849 (0.123) | 0.223 (0.026) | 0.753 | 30.Bh4 Qxg2 31.Rhg1 Qxg1 32.Rxg1+ / 28.Qxe8+ Nf8 29.Ra8 Qd1+ 30.Kh2 / 22.Qxc3 Rc8 23.Qg3 Qd4+ 24.Kh1 |
| W241 | best | 20 | 3 | 2,3,4,5,6,8 | 0.833 (0.126) | 0.309 (0.01) | 0.84 | 22.Bh3 c6 23.Rhd1 Qf6 24.f4 / Bd7 22.c5 c6 23.d6 a5 / 25.Be3 Rfc8 26.a4 f5 27.exf5 |
| W721 | clean | 5 | 2 | 2,3 | 0.731 (0.084) | 0.367 (0.026) | 0.79 | Nd3 19.hxg4 Nxf4 / 19.h3 exf3 20.hxg4 / 15.d5 Qd8 16.dxe6 |
| W707 | clean | 5 | 2 | 2,3,4,5 | 0.858 (0.245) | 0.431 (0.026) | 0.847 | 28.Bxf8 Nxf8 29.Rg1 / 20.Bxh6 gxh6 21.Qxc6 / 19.O-O Bxe4 20.Bxe4 |
| W67 | clean | 53 | 16 | 2,3,4,5,6,8 | 0.626 (0.146) | 0.147 (0.007) | 0.793 | Qxe5 44.Ke2 Qe4 45.Rd1 / 19.Ne3 Qxd4 20.O-O Rb8 / Bh6 23.Nc4 Bg7 24.f5 |
| W62 | clean | 57 | 4 | 2,3,4,5,6,8 | 0.87 (0.15) | 0.515 (0.007) | 0.825 | 25.Kb1 Rd2+ 26.Kc1 Rc2+ 27.Kb1 / 30.Nf5+ Ke8 31.Ng7+ Ke7 32.Nf5+ / 37.Qh7+ Rg7 38.Qh5+ Rg6 39.Qh7+ |
| W658 | clean | 6 | 2 | 2,3,4,5,6,8 | 0.865 (0.212) | 0.537 (0.027) | 0.791 | Kc8 24.Rf8+ Rxf8 25.Qxf8+ Kc7 26.Qf7+ Kb6 27.Rb1+ Ka6 / 28.Ne7 Rxe7 29.Ra8 Rc7 30.Be8 c3 31.Rd8 Bb7 32.Bb5 / Kc5 21.b4+ Kb5 22.a4+ Kxa4 23.Ra1+ Kb5 24.Ra5+ Nxa5 |
| W610 | clean | 7 | 2 | 2,3,4,5,6,8 | 0.79 (0.191) | 0.456 (0.026) | 0.814 | 33.Qe8 Rg7 34.hxg7+ Qxg7 35.Qh5+ Bh7 36.Rxg7 / 29.Re1+ Kf6 30.Rf1+ Ke6 31.d5+ Kd6 32.Rf7 / 30.Bxd6 Rc1+ 31.Kg2 e4 32.Rb4 Nf6 33.Rd4 |
| W349 | clean | 15 | 4 | 2,3,4 | 0.663 (0.108) | 0.223 (0.014) | 0.848 | bxc5 24.Bxc5 Bxc5 / 22.Nxc5 Nxc5 23.Bxc5 / 21.Bf3 Bxf3 22.gxf3 |
| W444 | best | 11 | 3 | 2,3,4,5 | 0.887 (0.12) | 0.332 (0.015) | 0.653 | 19.Be5 Bf6 20.Bf4 Bg5 / 30.Ne4 Qf5 31.Nd6 Qf6 / Kc5 27.Qa5+ Kc6 28.Qa6+ |
| W500 | best | 9 | 6 | 2,5,6,8 | 0.719 (0.202) | 0.27 (0.02) | 0.749 | 25.Nd5 Nxc4 26.Ne7+ Kd7 27.Nc6 Ra8 28.Rd1 Ke6 29.Rxd3 / Nxa3 33.Kb2 Nac4+ 34.Kb3 Ne3+ 35.Kb2 Rd2 36.Kc1 Rxc2+ / Nxf5 27.Rf3 Nd4 28.Rg3 Nf5 29.Rg6 Nh4 30.Rxe6 Nf5 |
| W682 | clean | 6 | 2 | 2,3 | 0.43 (0.053) | 0.522 (0.027) | 0.841 | Nxd5 16.exd5 c6 / Kb8 36.Ra3 Bb4 / 16.Bxb5 Bd7 17.a4 |
| W493 | clean | 9 | 2 | 2,3,4,5,6,8 | 0.742 (0.128) | 0.363 (0.02) | 0.816 | 22.bxc4 bxc4 23.dxc4 dxc4 24.Rxc4 / 26.Qxe6+ Kh8 27.Qe8 Qf7 28.Qxf7 / Raf8 28.g4 f4 29.g5 Rf5 |
| W406 | clean | 12 | 6 | 2,3,4,5,8 | 0.561 (0.088) | 0.195 (0.026) | 0.812 | b4 33.cxb4 Rxb4 34.Qe3 / 24.Kf1 Nc2 25.Rb1 Nxa3 / Qxb3 29.Rb1 Qa3 30.Bxg5 |
| W482 | clean | 10 | 4 | 2,3,4,5 | 0.784 (0.112) | 0.224 (0.015) | 0.798 | 24.Bd4 Rb3 25.Rd1 Rxa3 / Bb3 28.Qc6 Ba4 29.Qxa4 / 31.Ra6 Nb4 32.Rxa5 Nbd5 |
| W673 | clean | 6 | 2 | 3,4,5,6,8 | 0.344 (0.155) | 0.835 (0.026) | 0.773 | Ra8 44.Bxa8 Ra7 45.Bd5 Ne5 / Nb8 27.Nxg5 f6 28.Ne6+ Qxe6 / Bf6 20.Nc6 Qd6 21.Nxb8 g6 |
| W838 | clean | 3 | 2 | 2,3 | 0.543 (0.095) | 0.219 (0.014) | 0.776 | Bb4 30.Rec1 Rxf4 / 30.Bh4 Qxg2 31.Rhg1 / Nd5 30.Qg3 g6 |
| W243 | clean | 20 | 8 | 2,3,4,5,6,8 | 0.478 (0.128) | 0.171 (0.01) | 0.777 | e4 31.Qg5 b5 32.Qh6 / 32.Re8+ Kh7 33.Re7 Kg6 / Qf4+ 33.Ke2 Qf3+ 34.Kd2 |
| W412 | clean | 12 | 2 | 2,3,4,5,6,8 | 0.462 (0.111) | 0.298 (0.014) | 0.654 | Ne4 25.Qb2 Nc5 / 26.Bg2 hxg3 27.fxg3 / 29.Rfd1 Bb3 30.Re1 |
| W677 | clean | 6 | 2 | 2,3,4,5,6,8 | 0.318 (0.151) | 0.453 (0.012) | 0.829 | 18.Rg1 Bc5 19.Rg3 / O-O 20.Re1 Bd4 / Rd8 22.Ng5 Kf6 |
| W738 | clean | 4 | 3 | 4,5,8 | 0.487 (0.274) | 0.36 (0.012) | 0.771 | 14.Bxb6 axb6 15.Rad1 Ba6 16.Qxa6 Bc5 17.Ne4 Bd4 18.c3 / Kxg7 20.Bxb7 Rab8 21.Bc6 Red8 22.Bxd7 Rxd7 23.Qc3+ Kg8 / 27.Nxa3 b2 28.Rb1 Bb6 29.Rxb2 Bd4 30.Nxd4 exd4 31.Bxf6 |

