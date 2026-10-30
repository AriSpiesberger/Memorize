# Mined dynamic concepts

Tag p16-r1024-T0.4-s0-L11-4k, checked against p16-r1024-T0.4-s0-L11-4k-s1. Decisive branch points: >= 30 rollouts, chosen move >= 75%. k in 2,3,4,5,6,8. Families: cosine >= 0.5, >= 3 solutions at >= 2 positions.

## S

best: 47, clean: 75, board: 187, weak: 46; best with a clear theme in its examples: 33

### Best, with a theme

| concept | theme (share of windows / base rate) | branch points | positions | replication | agreement | chosen > subpar at branch points | activating windows |
|---|---|---|---|---|---|---|---|
| S141 | repeats a move (100% / 1%) | 12 | 3 | 0.841 | 0.293 | Qxc4 > e4; Qf3 > Qxd4; Rxd7 > Qe6 | Qc4+ 26.Kg2 Qd5+ 27.Kf1 Qc4+ 28.Kg2 Qd5+ / 26.Nf6+ Kg7 27.Nh5+ Kg8 28.Nf6+ Kg7 29.Nh5+ / Kc8 24.Be3 Kb8 25.Ba7+ Kc8 26.Be3 Kb8 |
| S54 | two or more checks (78% / 5%) | 23 | 5 | 0.949 | 0.371 | Ng5+ > g5; Kf7 > Ne3+; Ke8 > d3; Kg8 > Rxf6 | 31.Kxe1 Re8+ 32.Kd1 Re3 33.N2f3 Rd3+ / 36.Kg1 Ng5 37.Ng8+ Ke6 38.Qc4+ Qd5 / Kd8 26.Rd1+ Kc8 27.Rxc6+ Kb8 28.Rxc7 |
| S303 | two or more rook moves (100% / 27%) | 4 | 4 | 0.938 | 0.266 | Be6 > Qg6; Be3 > Ne4; Rac1 > Bxe6; Re1 > Qd4 | 16.Rad1 Re8 17.c4 / Rae8 20.Rad1 Bf8 / Rfd8 17.Rfd1 Rac8 |
| S214 | two or more queen moves (89% / 19%) | 8 | 3 | 0.602 | 0.25 | f4 > Rad8; Qf3 > Qxd4; Bxb5 > Rc8 | Qxc4 23.Qxb7 Qxc3 24.Qxa7 Ng4 / 26.Qxb7 Qb3 27.Qxc6 Qxb2 28.f4 / Qb2 22.Qb4 Qe2 23.Rab1 h5 |
| S29 | two or more pawn moves (89% / 24%) | 31 | 4 | 0.995 | 0.713 | e5 > e6; Qxc4 > e4; e5 > d4; dxe4 > Qxe4 | e5 13.Be3 Kb8 14.g3 h5 15.Bg2 h4 / 20.exd5 g6 21.b3 f5 22.Bh3 Qf6 23.Rae1 / 18.Rxf4 Be6 19.Rf2 Rad8 20.Qe1 b6 21.Ndc4 |
| S183 | two or more bishop moves (78% / 14%) | 9 | 4 | 0.888 | 0.262 | h5 > b4; Bd4+ > O-O-O; g4 > Ba6+; Nxe4 > Nxf3 | 18.Qb3 b5 19.Bxb5 Rb8 20.Bxe8 / 17.Bxb7+ Kd7 18.Bf3 Rb8 19.Bxd4 / Rxf4+ 27.Kg2 Qg7+ 28.Bg4 Rxg4+ |
| S123 | two or more captures (100% / 37%) | 14 | 7 | 0.97 | 0.457 | Qxc5 > Qc3; Rxd5 > Rb7; Bxd5 > Rd1; Qxa4+ > Qb1 | 23.Bxc4 b5 24.Bd5 Rbd8 25.Rxf8 Kxf8 26.Rf1+ / Qxe7 24.Bd6 Rd8 25.Bxe7+ Kxe7 26.Re1+ Ne6 / Nxc5 21.dxc5 Qxc5 22.Rab1 Qxa3 23.Rb3 Qxa2 |
| S242 | two or more captures (100% / 37%) | 7 | 3 | 0.901 | 0.519 | Nc5 > Ne5; Bg7 > Qa5; cxb2 > Rh8 | dxc4 21.Ndxc4 Nxc4 22.Bxc4 / Nxg3+ 28.Rfxg3 Rxg3 29.Rxg3 / Bxg6 30.hxg6+ Qxg6 31.Rxg6 |
| S8 | two or more rook moves (89% / 27%) | 55 | 9 | 0.977 | 0.563 | Rxa6 > Ng4; Bf4 > Qd6; Ree1 > Rg4; e5 > Rcc2 | 25.Rb3 Rxb2 26.Rxb2 / 27.Rb8+ Rd8 28.R8b7 / Rxc2 24.Rxc2 Qxc2 |
| S155 | check (78% / 16%) | 11 | 4 | 0.942 | 0.526 | Rxa3 > Qd5; Ref8 > h6; Re8 > Rdf8; Rfc1 > a4 | Rxc2 24.Rxc2 Rxc2 25.Rb8+ / Rb1+ 20.Ne1 Qxe4 21.Qc8+ / 24.Re1 Rgf5 25.Rxe4 h6 |
| S158 | king move (89% / 28%) | 11 | 4 | 0.909 | 0.349 | Qh6+ > exf7; Ke2 > Ke1; Kd7 > Kc8; Qe5 > Qf5 | 30.Ke2 Nc2 31.Nf3 / 31.Qxe4 Kxd7 32.Rb1 / Qxf3 32.Qxc7+ Ke6 |
| S202 | king move (89% / 28%) | 8 | 7 | 0.965 | 0.36 | Ng5+ > g5; Kg1 > g4; Ke8 > g5; Kg8 > Rxf6 | 31.Ke3 Kg8 32.Rh1 / Kg8 32.e6 Rf8 / 31.Kd2 Kc8 32.Rxd7 |
| S172 | two or more queen moves (78% / 19%) | 10 | 3 | 0.858 | 0.423 | Nb5 > Rd5; a6 > Bxd5; Qe5 > Qxa3 | Nf6 21.Ng3 Qg6 22.Qh3 / 17.Qxh5 g6 18.Qg4 f5 / 20.Qa4 Nb6 21.Qc6 Bd7 |
| S170 | no capture or check (89% / 35%) | 10 | 3 | 0.976 | 0.482 | Qf5+ > Re7; Qd6 > g5; h5 > Rde1 | 31.Qf5 Qc6 32.Qe4 / 32.Qd2 Nf6 33.Nc6 / 27.Qd3 Qc4 28.Qf5 |
| S268 | two or more knight moves (67% / 14%) | 6 | 3 | 0.614 | 0.305 | a6 > h6; Rxc5 > Qf4; Qe5 > Qxa3 | 19.Ne4 Ne3 20.Qc1 / 25.Bf4 g5 26.Bxd6 / b5 17.Nxb5 cxb5 |
| S166 | two or more rook moves (78% / 27%) | 11 | 4 | 0.829 | 0.424 | Qe5 > Qe6; Rb2 > Rb3; Bb7 > d6; Qxc7 > Ka8 | 19.Re3 Bxf3+ 20.Qxf3 / 32.Ree6 Nxe6 33.Rxa6 / Rbb2 23.Bxd2 Rxd2 |
| S229 | check (67% / 16%) | 7 | 4 | 0.921 | 0.495 | b5 > Rd8; Ng5 > Rg4; Qf6+ > Rxb6; Qxf4 > Nxc6 | 31.gxf3 Rg8+ 32.Kf1 Rc8 33.Ke2 / Kg8 32.Nd6 Qe5+ 33.Qf4 Qxf4+ / 25.Nxg8 cxb2 26.Nxf6 Qc1+ 27.Rxc1 |
| S46 | king move (78% / 28%) | 26 | 6 | 0.947 | 0.275 | Kf3 > Kd3; Kxf6 > Qxg2; Kf8 > Kd7; Bxf2+ > O-O | Kg7 19.h4 h6 20.Qa1 Rad8 / 31.Kf2 Qxg4 32.Bxg4 Kg7 33.Bf3 / Kf7 21.fxe4 fxe4 22.Nxe4 Kg6 |
| S26 | two or more pawn moves (67% / 24%) | 34 | 4 | 0.877 | 0.399 | Qa5 > Qe5; a6 > Nf6; Qa5 > b5; Bxd7 > Qf5 | Rc5 21.g6 fxg6 22.Bg5 Bxg5 / 23.dxc5 Nd2 24.Rb6 Rf8 25.c6 / 12.Qa4+ c6 13.Nd2 O-O 14.O-O-O |
| S156 | two or more pawn moves (67% / 24%) | 11 | 5 | 0.972 | 0.439 | exf7+ > Nd4; fxg6 > Rxg6; Kxf8 > Bf5; Rad8 > Bxb3 | Rxb7 23.Rad1 Re7 24.Kh2 g5 25.g3 Ng6 / Kg8 17.f5 Ne5 18.Bxe5 dxe5 19.Rad1 Bd6 / f4 26.Ng4 Nd5 27.Kg1 Qd7 28.h3 Rbe8 |
| S203 | no capture or check (78% / 35%) | 8 | 3 | 0.979 | 0.673 | Bd6 > Be7; Nc3 > Bb5+; Nxf4 > h6 | Bc7 23.Qd3 g6 / Bd6 20.Rh3 h6 / Qc7 15.Rhg1 Kh8 |
| S139 | two or more captures (78% / 37%) | 12 | 3 | 0.672 | 0.364 | Qc7 > Ne7; Rad1 > c5; Qxe7 > Qxd1+ | 23.Bxg7 Rxg7 24.Qc6+ Kf8 25.Bg2 / 31.Ne6+ Kg8 32.Nxf8+ Kxf8 33.Qd8+ / 17.Bxd4 Qxd4 18.Rad1 Qb6 19.Bxb7 |
| S151 | two or more captures (78% / 37%) | 11 | 4 | 0.923 | 0.278 | Qf1+ > Qh3; Nc4 > e6; Nxc4 > Nf3+; Rf8 > Qf5 | 22.bxc3 Bxe4 23.Nd6 Bd5 24.c4 Bc6 / fxe5 20.Qh5 Bxd5 21.exd5 Qxd5 22.Rae1 / 25.Rf1 Rxe4 26.dxe4 Qd7 27.Qxd7 Rxd7 |
| S88 | capture (100% / 59%) | 18 | 5 | 0.878 | 0.315 | Qh5 > Qf3; Rd7 > Ne5; Qxe7 > Rxe7; Qxb2 > Kg7 | 28.Rxe2 Rxe2 29.Qxe2 / 23.Rd7 Qf4 24.Rxe7 / Rxb2 31.e6 fxe6 |
| S332 | capture (100% / 59%) | 3 | 3 | 0.67 | 0.372 | Nf5 > Qf6; Nf2+ > Qxg1+; Bc4 > Nxe5 | 17.Kh1 Bg4 18.Qe1 Rxd8 / Ke7 18.Nxe5 Qxg2 19.Rhg1 / 18.Nxf5 Bxf5 19.Bf3 Be4 |
| S75 | two or more rook moves (67% / 27%) | 20 | 6 | 0.947 | 0.258 | Nxe5 > Qh8; Re8 > Bxh2; Rd8 > Qd6; Kh8 > Bxh2 | 20.hxg5 b4 21.Ne2 Bxe4 / Rge8 25.Nc4 Qf2 26.Rxe6 / Rxf6 18.Rhg1 g6 19.Rg2 |
| S147 | two or more rook moves (67% / 27%) | 12 | 3 | 0.831 | 0.495 | cxd5 > b4; Bxd4+ > Be6; Qxc5 > Rc8 | 18.Bxe6 fxe6 19.Kg1 / 22.Qd2 Rac8 23.Rfe1 / 21.Rc2 Rc8 22.Rfc1 |
| S60 | king move (67% / 28%) | 22 | 5 | 0.718 | 0.327 | Ng5 > Rg4; Nxc1 > Qc7; Qf6+ > Rxb6; Rb8 > Rad7 | 31.gxf3 Rg8+ 32.Kf1 Re8 / 30.Kh2 Qd5 31.b4 Kg7 / Rxg1 26.Nxc6+ bxc6 27.Kxd2 |
| S205 | no capture or check (67% / 35%) | 8 | 3 | 0.963 | 0.645 | Rxc5 > Qf4; c4 > Rab1; Ng5 > Qxa6 | Rxd6 36.Nd5 Nf6 / a6 28.axb5 axb5 / Kg8 32.Rd3 Kh8 |
| S206 | no capture or check (67% / 35%) | 8 | 3 | 0.653 | 0.327 | Qd6 > Rd7; b3 > Qxf4; Rad1 > c5 | Ne5 20.Rd1 Nxd3 21.cxd3 Rfe8 / 23.Rad1 Qc7 24.c4 Nc6 25.Nd5 / Rd8 24.h3 c5 25.Qf3 cxd4 |
| S218 | no capture or check (67% / 35%) | 8 | 3 | 0.749 | 0.546 | Re8 > b6; Rc7 > Nf4; Re1 > h4 | 19.Re1 Bb7 20.Re3 / Bxe7 24.Qa7+ Kc8 / Na5 16.Qd4 f6 |
| S14 | two or more captures (67% / 37%) | 47 | 8 | 0.932 | 0.332 | Qxh5 > Bxf8; Rxd2+ > Qf2; Rh1 > Bf3; Rxd1 > Qxc5+ | 20.Rxc8 Bxc8 21.Bxg7 b4 22.Na4 / Ne3 27.Rag1 Rf2+ 28.Kh1 Raf8 / Rg8 28.Rxf7 Rg7 29.Rxg7 Qxg5+ |
| S273 | two or more captures (67% / 37%) | 5 | 3 | 0.956 | 0.402 | c6 > Kh8; Rad1 > Kh1; Bf4 > Kh8 | Rxf2 32.Rxd5 Rxd5 / 15.Nxf7 Rxd4 16.cxd4 / 24.Kg1 Qxg5 25.Qxd7 |

### Best and clean, by cleanliness

| concept | tier | branch points | positions | k | replication (null 95th) | agreement (null 95th) | board | top activating windows |
|---|---|---|---|---|---|---|---|---|
| S325 | clean | 4 | 2 | 2,3 | 0.974 (0.088) | 0.803 (0.022) | 0.806 | 27.Rxb6+ axb6 28.Rxb6+ / Rxb7 24.Rxb7 Qxb7 / 17.Nxd7 Rxd7 18.Bxf6 |
| S351 | clean | 3 | 2 | 2,3 | 0.913 (0.088) | 0.699 (0.001) | 0.814 | Qxd4 18.Qxb7 Rab8 / 20.Qxd6 Qxc2 21.Rdc1 / Kxd7 18.Qxf7 Raf8 |
| S58 | best | 23 | 4 | 2,3,4,5,6 | 0.945 (0.088) | 0.591 (0.013) | 0.72 | 27.gxf4 Rxf4 28.Nd3 / 18.h4 h6 19.g4 / g6 24.Bd3 Rxe3 |
| S9 | best | 54 | 3 | 2,3,4,5,6,8 | 0.954 (0.159) | 0.811 (0.009) | 0.635 | 32.Qg3+ Kf5 33.Qf3+ / Kb8 26.Ra8+ Kb7 / 27.Nh5+ Kg8 28.Nf6+ |
| S135 | clean | 13 | 2 | 2,3,4,5,6 | 0.935 (0.134) | 0.683 (0.016) | 0.849 | c5 20.f4 exf4 21.gxf4 / Nxe4 18.Bxe4 Qf6 19.g3 / 21.Rfa1 Kc8 22.Nd4 Bxd4 |
| S191 | best | 9 | 4 | 2,3,4,5,6 | 0.961 (0.139) | 0.66 (0.035) | 0.829 | Rxc7 20.b3 a5 21.Rd3 a4 / Qb4 25.b3 Rd2 26.Rc1 Bg5 / 17.b3 Qa5 18.Kb1 Bb4 19.Bd4 |
| S324 | clean | 4 | 2 | 2,3 | 0.993 (0.219) | 0.634 (0.022) | 0.825 | 21.exd5 exf4 22.Re6 / 31.exd5 Bb6 32.Bg3 / 19.d5 Bb6+ 20.Kh1 |
| S225 | clean | 7 | 2 | 2,3,4,5,6,8 | 0.933 (0.1) | 0.584 (0.035) | 0.812 | 14.Qe3 d5 15.Ng3 Qxe3+ 16.fxe3 Ng6 17.cxd5 / 22.Bd3 Re8 23.O-O Kg8 24.Bxf5 Bxf5 25.Qxf5 / f5 25.Ne3 Qd7 26.Qf4 Rbe8 27.Qf3 d5 |
| S309 | clean | 4 | 2 | 3,4,5 | 0.835 (0.139) | 0.673 (0.022) | 0.699 | Bc5 18.d4 Rae8 19.Ne5 / Nd5 18.Rc1 Kb8 19.dxc5 / 11...Bd6 12.Qa4+ c6 13.Nd2 |
| S29 | best | 31 | 4 | 2,3,4,5,6,8 | 0.995 (0.163) | 0.713 (0.01) | 0.824 | e5 13.Be3 Kb8 14.g3 h5 15.Bg2 h4 / 20.exd5 g6 21.b3 f5 22.Bh3 Qf6 23.Rae1 / 18.Rxf4 Be6 19.Rf2 Rad8 20.Qe1 b6 21.Ndc4 |
| S205 | best | 8 | 3 | 2,3,4,5,6 | 0.963 (0.15) | 0.645 (0.032) | 0.826 | Rxd6 36.Nd5 Nf6 / a6 28.axb5 axb5 / Kg8 32.Rd3 Kh8 |
| S182 | best | 9 | 3 | 3,4,5,6,8 | 0.953 (0.138) | 0.613 (0.024) | 0.841 | 15.g3 Qe5 16.f4 gxf4 / Bd4 18.Qe2 Bxe3 19.Qxe3 / Nc5 15.Qa3 h6 16.Bh4 |
| S223 | best | 7 | 3 | 3,4,5,6,8 | 0.934 (0.251) | 0.747 (0.035) | 0.802 | a5 23.Rb1 h6 24.a4 Kh7 / 19.Qe7 Bd7 20.Rc7 h6 21.Nf3 / Qxe2 20.Ne5 Nxe5 21.Bxe5 Qa6 |
| S346 | clean | 3 | 2 | 2,3 | 0.92 (0.163) | 0.812 (0.001) | 0.839 | 21.axb5 cxb5 22.Na5 / Ra8 30.Rxa6 Rxa6 / 16.a4 bxa4 17.Rxa4 |
| S242 | best | 7 | 3 | 2,3 | 0.901 (0.097) | 0.519 (0.035) | 0.737 | dxc4 21.Ndxc4 Nxc4 22.Bxc4 / Nxg3+ 28.Rfxg3 Rxg3 29.Rxg3 / Bxg6 30.hxg6+ Qxg6 31.Rxg6 |
| S146 | clean | 12 | 2 | 2,3,4,5,6,8 | 0.897 (0.139) | 0.805 (0.017) | 0.811 | Rxe4 23.Qf3 Rae8 / Rd8 20.Rc1 h6 / Red8 24.Rac1 c6 |
| S173 | best | 10 | 4 | 2,3,4,5,6,8 | 0.959 (0.105) | 0.491 (0.024) | 0.829 | 19.Ne5 b6 20.Rfc1 Be8 / 21.Qf3 Be6 22.Bd3 g6 / gxh3 16.Bxh5+ Kf8 17.Rxh3 |
| S202 | best | 8 | 7 | 2,3,4,5,6 | 0.965 (0.222) | 0.36 (0.032) | 0.837 | 31.Ke3 Kg8 32.Rh1 / Kg8 32.e6 Rf8 / 31.Kd2 Kc8 32.Rxd7 |
| S170 | best | 10 | 3 | 2,3,4,5,6,8 | 0.976 (0.205) | 0.482 (0.022) | 0.751 | 31.Qf5 Qc6 32.Qe4 / 32.Qd2 Nf6 33.Nc6 / 27.Qd3 Qc4 28.Qf5 |
| S256 | clean | 6 | 2 | 2,3,5,6 | 0.924 (0.116) | 0.533 (0.022) | 0.842 | Qa5 16.cxd5 Nxd5 17.Bxd5 cxd5 18.Kb1 / 15.Bxd3 Be7 16.Ne5 a6 17.Nxd7 Qxd7 / Qa5 18.d5 Bf6 19.Ra2 exd5 20.cxd5 |
| S26 | best | 34 | 4 | 2,3,4,5,6,8 | 0.877 (0.088) | 0.399 (0.01) | 0.836 | Rc5 21.g6 fxg6 22.Bg5 Bxg5 / 23.dxc5 Nd2 24.Rb6 Rf8 25.c6 / 12.Qa4+ c6 13.Nd2 O-O 14.O-O-O |
| S203 | best | 8 | 3 | 2,3,4,5,6,8 | 0.979 (0.134) | 0.673 (0.032) | 0.828 | Bc7 23.Qd3 g6 / Bd6 20.Rh3 h6 / Qc7 15.Rhg1 Kh8 |
| S99 | clean | 17 | 2 | 3,4,5,6,8 | 0.984 (0.252) | 0.935 (0.013) | 0.772 | 25.Rfe1 Qf4 26.Qe2 Rf6 27.g3 Qf5 28.Qe4 / Qf7 21.c5 d5 22.Rad1 d4 23.cxd4 Nxd4 / Rhf8 17.O-O Bxc3 18.Bxc3 Rae8 19.Rae1 h5 |
| S229 | best | 7 | 4 | 3,4,5,6,8 | 0.921 (0.165) | 0.495 (0.022) | 0.724 | 31.gxf3 Rg8+ 32.Kf1 Rc8 33.Ke2 / Kg8 32.Nd6 Qe5+ 33.Qf4 Qxf4+ / 25.Nxg8 cxb2 26.Nxf6 Qc1+ 27.Rxc1 |
| S104 | clean | 17 | 8 | 2,3,4,5,6,8 | 0.92 (0.157) | 0.205 (0.013) | 0.786 | 16.exd6 Qc6 17.O-O / 19.fxe7 Qxe7 20.Re1 / 30.Rxd5 Rxd5 31.Qxd5 |
| S345 | clean | 3 | 2 | 2,5,6 | 0.863 (0.105) | 0.541 (0.001) | 0.781 | Kxe5 33.Qe7+ Kf5 / 31.Qc4+ Ka3 32.Bd6+ / Rec8 22.Rb7 f6 |
| S123 | best | 14 | 7 | 2,3,4,5,6,8 | 0.97 (0.294) | 0.457 (0.017) | 0.729 | 23.Bxc4 b5 24.Bd5 Rbd8 25.Rxf8 Kxf8 26.Rf1+ / Qxe7 24.Bd6 Rd8 25.Bxe7+ Kxe7 26.Re1+ Ne6 / Nxc5 21.dxc5 Qxc5 22.Rab1 Qxa3 23.Rb3 Qxa2 |
| S327 | clean | 4 | 2 | 2 | 0.953 (0.107) | 0.376 (0.022) | 0.753 | 19.a3 a5 20.Rad1 / 28.a4 a5 29.b5 / 22.a4 b6 23.f3 |
| S273 | best | 5 | 3 | 2,3,6,8 | 0.956 (0.125) | 0.402 (0.03) | 0.827 | Rxf2 32.Rxd5 Rxd5 / 15.Nxf7 Rxd4 16.cxd4 / 24.Kg1 Qxg5 25.Qxd7 |
| S166 | best | 11 | 4 | 2,3 | 0.829 (0.126) | 0.424 (0.016) | 0.748 | 19.Re3 Bxf3+ 20.Qxf3 / 32.Ree6 Nxe6 33.Rxa6 / Rbb2 23.Bxd2 Rxd2 |
| S163 | best | 11 | 4 | 2,3,4,5,6 | 0.825 (0.105) | 0.409 (0.016) | 0.813 | 20.Rfb1 Bc6 21.Ne5 / Rf7 28.Nd3 Bd6 / 21.Kf2 Ne4+ 22.Kxe3 |
| S282 | clean | 5 | 2 | 2,3,4 | 0.778 (0.114) | 0.616 (0.022) | 0.795 | Nd4 32.f8=Q+ Rxf8 33.Qxf8+ / 17.Qxf7 Rf8 18.Ne6+ Kd7 / Ne7 29.Rd1 d2 30.Rxg7 |
| S156 | best | 11 | 5 | 2,3,4,5,6 | 0.972 (0.247) | 0.439 (0.016) | 0.846 | Rxb7 23.Rad1 Re7 24.Kh2 g5 25.g3 Ng6 / Kg8 17.f5 Ne5 18.Bxe5 dxe5 19.Rad1 Bd6 / f4 26.Ng4 Nd5 27.Kg1 Qd7 28.h3 Rbe8 |
| S88 | best | 18 | 5 | 2,3,4,5,6,8 | 0.878 (0.191) | 0.315 (0.013) | 0.801 | 28.Rxe2 Rxe2 29.Qxe2 / 23.Rd7 Qf4 24.Rxe7 / Rxb2 31.e6 fxe6 |
| S75 | best | 20 | 6 | 2,3,4,5,6,8 | 0.947 (0.201) | 0.258 (0.014) | 0.812 | 20.hxg5 b4 21.Ne2 Bxe4 / Rge8 25.Nc4 Qf2 26.Rxe6 / Rxf6 18.Rhg1 g6 19.Rg2 |
| S201 | clean | 8 | 2 | 2,3,4,5,6,8 | 0.877 (0.229) | 0.59 (0.032) | 0.84 | 25.bxc3 Rxg1 26.Bxf5 Rg5 27.Bg4 Rgd5 28.Ne4 / 16.Nxd5 O-O-O 17.Bxf6 gxf6 18.Nh4 Bh6+ 19.Kb1 / Qxf3 15.gxf3 Be7 16.Bb2 Rhg8 17.h4 Nd5 |
| S187 | best | 9 | 4 | 2,3,4,5,6 | 0.815 (0.145) | 0.457 (0.032) | 0.83 | 22.Rxd6 Rc8 23.Rfd1 / 33.Rxa6 Nd5 34.c4 / b6 25.Be3 Ne7 |
| S177 | clean | 10 | 2 | 2,3,4,5,6 | 0.926 (0.205) | 0.496 (0.022) | 0.825 | 31.Kh2 Qxd5 32.Rxd5 / 18.Bb3 Bc5 19.Bxc5 / Rd8 28.Ke2 Bxb2 |
| S301 | clean | 4 | 2 | 3,4,5 | 0.72 (0.108) | 0.511 (0.022) | 0.728 | 14.Bxc6 Bxc6 15.Qxc6 Rd8 / Ne6 23.Nxd6 Bxd6 24.Qxd6 / Ng4 18.Qb6 Rd7 19.Bc5 |
| S155 | best | 11 | 4 | 2,3,4,5,6,8 | 0.942 (0.219) | 0.526 (0.016) | 0.802 | Rxc2 24.Rxc2 Rxc2 25.Rb8+ / Rb1+ 20.Ne1 Qxe4 21.Qc8+ / 24.Re1 Rgf5 25.Rxe4 h6 |
| S14 | best | 47 | 8 | 2,3,4,5,6,8 | 0.932 (0.307) | 0.332 (0.009) | 0.717 | 20.Rxc8 Bxc8 21.Bxg7 b4 22.Na4 / Ne3 27.Rag1 Rf2+ 28.Kh1 Raf8 / Rg8 28.Rxf7 Rg7 29.Rxg7 Qxg5+ |
| S180 | clean | 10 | 6 | 2,3 | 0.866 (0.165) | 0.226 (0.022) | 0.751 | 22.h3 h4 23.a4 / h5 32.h4 a4 / h5 26.g3 Kg7 |
| S303 | best | 4 | 4 | 2,4,5 | 0.938 (0.143) | 0.266 (0.022) | 0.737 | 16.Rad1 Re8 17.c4 / Rae8 20.Rad1 Bf8 / Rfd8 17.Rfd1 Rac8 |
| S73 | clean | 20 | 7 | 2,3,4,5,6,8 | 0.875 (0.172) | 0.229 (0.013) | 0.809 | 20.h4 Kf7 21.h5 / f6 31.Qb1 e4 / 23.Bh3 Rxc3 24.Ne3 |
| S218 | best | 8 | 3 | 2,3,4 | 0.749 (0.1) | 0.546 (0.032) | 0.718 | 19.Re1 Bb7 20.Re3 / Bxe7 24.Qa7+ Kc8 / Na5 16.Qd4 f6 |
| S8 | best | 55 | 9 | 2,3,4,5,6,8 | 0.977 (0.417) | 0.563 (0.009) | 0.721 | 25.Rb3 Rxb2 26.Rxb2 / 27.Rb8+ Rd8 28.R8b7 / Rxc2 24.Rxc2 Qxc2 |
| S40 | clean | 28 | 11 | 2,3,4,5,6,8 | 0.934 (0.444) | 0.239 (0.012) | 0.81 | 21.Bxe4 dxe4 22.Re1 Nxd4 23.cxd4 / Nxc3 21.Nxc3 Rfc8 22.Rb1 b5 / Nc6 20.Rdc1 Nce7 21.N2c3 f5 |
| S46 | best | 26 | 6 | 2,3,4,5,6,8 | 0.947 (0.183) | 0.275 (0.011) | 0.849 | Kg7 19.h4 h6 20.Qa1 Rad8 / 31.Kf2 Qxg4 32.Bxg4 Kg7 33.Bf3 / Kf7 21.fxe4 fxe4 22.Nxe4 Kg6 |
| S54 | best | 23 | 5 | 3,4,5,6,8 | 0.949 (0.248) | 0.371 (0.014) | 0.808 | 31.Kxe1 Re8+ 32.Kd1 Re3 33.N2f3 Rd3+ / 36.Kg1 Ng5 37.Ng8+ Ke6 38.Qc4+ Qd5 / Kd8 26.Rd1+ Kc8 27.Rxc6+ Kb8 28.Rxc7 |
| S39 | clean | 28 | 7 | 2,3,4,5,6,8 | 0.772 (0.122) | 0.212 (0.011) | 0.819 | c4 24.b3 cxb3 25.c4 Bc6 / Rb8 28.c6 Nb3 29.Nxb3 Rxb7 / Nb4 29.a3 Na6 30.b4 Nc7 |
| S241 | best | 7 | 3 | 2,3,4,5 | 0.84 (0.159) | 0.459 (0.035) | 0.81 | 21.Qxf5 Nd4+ 22.Kb1 / 32.Qg7 Qxc5 33.Qxf6 / Qxf3 33.Rd2 Rf5 |
| S245 | clean | 7 | 2 | 2,3,4,5,6,8 | 0.851 (0.41) | 0.76 (0.035) | 0.809 | 17.Kh1 Kh8 18.f5 a5 / 23.Nxc8 Raxc8 24.c3 Rfd8 / 22.Rfc1 Qxa3 23.c4 dxc4 |
| S212 | clean | 8 | 2 | 2,3,4,5,6 | 0.586 (0.053) | 0.491 (0.032) | 0.519 | Nfd6 21.Nbc5 Nc4 / O-O-O 18.Be2 Bh6+ / Nxc3 19.bxc3 Rfe8 |
| S80 | clean | 20 | 8 | 2,3,4,5,6 | 0.863 (0.149) | 0.199 (0.014) | 0.753 | 33.Nxc4 Nxb2 34.Nxd2 / Nxc1 18.Ra1 Nxe2 / 16.Nf3 Qa5+ 17.Bd2 |
| S158 | best | 11 | 4 | 2,3,4,5,6 | 0.909 (0.17) | 0.349 (0.016) | 0.848 | 30.Ke2 Nc2 31.Nf3 / 31.Qxe4 Kxd7 32.Rb1 / Qxf3 32.Qxc7+ Ke6 |
| S264 | clean | 6 | 2 | 2,3,4,5,6 | 0.862 (0.318) | 0.653 (0.022) | 0.769 | Qd2+ 32.Kxf3 Re3+ / Bxf3+ 29.Kxf3 Rf8+ / Qxb2 31.Kf2 Qxe5 |
| S328 | clean | 4 | 2 | 2 | 0.643 (0.094) | 0.395 (0.022) | 0.726 | 21.Nf4 Bf6 22.Nxg6 / Nc3+ 30.Ka1 Nxa4 / Nc5 18.Bxf6 Nxa4 |
| S172 | best | 10 | 3 | 2,3,5,6 | 0.858 (0.147) | 0.423 (0.022) | 0.747 | Nf6 21.Ng3 Qg6 22.Qh3 / 17.Qxh5 g6 18.Qg4 f5 / 20.Qa4 Nb6 21.Qc6 Bd7 |
| S32 | clean | 30 | 2 | 2,3,4,5,6,8 | 0.943 (0.139) | 0.53 (0.012) | 0.848 | Bd6 14.a4 b4 15.Nd5 Bxd5 16.exd5 Qg6 / 25.Re1 Rf8 26.Qd6 Qf6 27.Qxf6 Rxf6 28.Kg2 / 25.Rf1 Rxe4 26.dxe4 Bd6 27.e5 Bf8 28.e6 |
| S141 | best | 12 | 3 | 2,3,4,5,6,8 | 0.841 (0.152) | 0.293 (0.017) | 0.772 | Qc4+ 26.Kg2 Qd5+ 27.Kf1 Qc4+ 28.Kg2 Qd5+ / 26.Nf6+ Kg7 27.Nh5+ Kg8 28.Nf6+ Kg7 29.Nh5+ / Kc8 24.Be3 Kb8 25.Ba7+ Kc8 26.Be3 Kb8 |

## W

best: 27, clean: 64, board: 170, weak: 57; best with a clear theme in its examples: 19

### Best, with a theme

| concept | theme (share of windows / base rate) | branch points | positions | replication | agreement | chosen > subpar at branch points | activating windows |
|---|---|---|---|---|---|---|---|
| W102 | two or more queen moves (100% / 21%) | 13 | 5 | 0.977 | 0.325 | Qb8+ > Qxe7+; Qc1 > Rd8; Qa5+ > Bb7; Rxg5 > b4 | Qb4 31.Qc2 Rc7 32.b3 Rdc8 33.Qe4 Qxb3 / 22.Qb8+ Qd8 23.Qxa7 O-O 24.Ba3 Re8 25.Bb5 / 28.Bd3 Qc6 29.Be4 Qb5+ 30.Bd3 Qc6 31.Be4 |
| W197 | two or more pawn moves (100% / 21%) | 7 | 3 | 0.956 | 0.565 | b6 > Nc6; b3 > Bb3; b6 > Ng6 | a6 16.a4 a5 / 24.a4 b6 25.Kh1 / a5 24.a4 Rbd8 |
| W221 | king move (100% / 24%) | 6 | 5 | 0.81 | 0.261 | Kh8 > g6; Ke1 > Rfe1; Ka2 > Nc3; Kc8 > R6g7 | 37.Kg1 fxe5 38.d7 Nf6 / 32.Kb1 Nc3+ 33.Kb2 Nd1+ / 30.Bc4+ Ka4 31.Bb3+ Kb5 |
| W112 | check (89% / 19%) | 12 | 3 | 0.924 | 0.673 | Bxc3 > Nb4+; Nxf1 > Rxb7; Qxa8+ > Kb2 | Nxh1 29.Nd5 Qc6+ 30.Bc4 Nxg3 31.Ba3 / Qb6+ 26.Kc2 Qxf6 27.Ne4 Qxf3 28.Ne5 / 30.Qb8+ Ke7 31.Qxa7+ Kf6 32.Qxa6 Nf4 |
| W50 | two or more captures (100% / 38%) | 21 | 8 | 0.965 | 0.47 | Qg8+ > Rg8+; Rxa3 > Rh4; Rc1 > Re3; R1xb4 > R5xb4 | Qxa1+ 31.Kh2 Nf5 32.Qh6+ Nxh6 33.Nxh6 Kxh6 34.Rd3 Qe5+ / Rd8 29.Qxd8 Qxd8 30.Rxd8 f5 31.Re7+ Kf6 32.Ra7 Kg5 / Rxa4 17.Qxa4 Bd6 18.h3 Qf6 19.Qb5 Rb8 20.d5 exd5 |
| W95 | no capture or check (89% / 28%) | 14 | 3 | 0.908 | 0.416 | Qxg1 > Bxc3; a5 > g6; Qd5+ > g6 | a5 16.Bg5 a4 / 28.R4e2 Bh3 29.f3 / 18.h3 Nf4 19.Qf3 |
| W134 | two or more queen moves (78% / 21%) | 11 | 3 | 0.951 | 0.555 | Qxb2 > Qe6; Rac8 > Qf6; Qxe7 > Rb1 | Qxc2 21.Rdc1 Qb2 / Qxc3 23.Qxb7 e4 / Qb2 20.Qxb7 Rab8 |
| W27 | two or more rook moves (78% / 26%) | 30 | 7 | 0.909 | 0.288 | Qxd3 > Qa2; Rxe6 > Qe4; Qxe4 > Qxg7; Rxa3 > Bxa3 | Nxd4 19.Nxd4 Bc5 20.Rb4 Bxd4 21.Rxd4 Qf6 / Re3 26.Rd6 Re8 27.Ng5 Bf5 28.e6 Bd3 / Re3 29.f4 d4 30.Rbd1 d3 31.Rxd3 Rxd3 |
| W29 | two or more rook moves (78% / 26%) | 28 | 5 | 0.978 | 0.595 | Rg1 > Rh3; Qf5+ > Nc7; Ke1 > Rfe1; Kc8 > R8g7 | Qe1+ 28.Rg1 Qe4+ / Nb4 21.Rde3 Re8 / 32.Rg8+ Rg7 33.Rxg7+ |
| W139 | two or more rook moves (78% / 26%) | 10 | 5 | 0.923 | 0.31 | fxe6 > Rd8; Nxf7 > Qxa6; Rxf8 > Qxf8; Raf8 > Rxf3 | Bxd5 22.Nf3 Bxf3 23.Rxf3 / 25.Raf1 Qd6 26.Rxf5 e4+ / 28.Rf1 Rf8 29.Ng4 Qh5 |
| W21 | two or more captures (89% / 38%) | 34 | 8 | 0.975 | 0.44 | Bxe2 > Nxe5; Kxg2 > Nf6; Bf6 > Bc3; Bxd5 > Qd7 | dxe5 18.Qxe5 O-O 19.Qxe7 Rab8 20.h3 Nd5 / Bxe3 20.Bb5 a6 21.Bxc6 bxc6 22.Re1 Bf4+ / Kxg7 19.f4 Ne3 20.Nxe3 Qxe3+ 21.Kh1 Nd4 |
| W63 | check (67% / 19%) | 19 | 3 | 0.945 | 0.519 | Rxg5 > Bxg5; Nc1+ > Bxe4; Qa3+ > Ne2+ | 33.Kc4 Qxc2+ 34.Kb4 / Qxc8 22.Qc5+ Qxc5 / Qg4+ 24.Kf1 Qh3+ |
| W59 | two or more queen moves (67% / 21%) | 20 | 4 | 0.919 | 0.387 | Kd7 > Kd8; dxc4 > Qe5; Kg2 > Bf3; Qxe5 > Rac1 | 22.Qxe7 Qxc3 23.Qxb7 / Kh8 22.Be5 Rg8 / Qb2 20.Qxb7 Rab8 |
| W25 | king move (67% / 24%) | 31 | 10 | 0.956 | 0.429 | Bxc7 > a6; Bh4 > Bd2; Nxc7 > Qxc7; h6 > Qxf4+ | 19.Nxe4 Bxe4 20.Bxf8 Bxc2 21.Rdh1 Bg6+ 22.Kd1 / 25.Ng5 Rxd8 26.Rxd8+ Kg7 27.Rd7 Nb6 28.Rxf7+ / 29.Rxg7 Nf5 30.Nxf5 exf5 31.Rxg6 Rf8 32.e6 |
| W79 | two or more rook moves (67% / 26%) | 16 | 3 | 0.901 | 0.363 | Rfe1 > Qd3; R1xb4 > R5xb4; Rxd8 > Qxd8 | Rd8 28.Nb6 Bc5 / 28.Rf8 Bxf2 29.Rxg8+ / Rf8 21.Rg7+ Kh8 |
| W138 | no capture or check (67% / 28%) | 10 | 3 | 0.992 | 0.618 | e4 > Rd3; exd5 > Qxd5; e5 > e6 | Bd6 17.Nc3 d4 / Bd6 21.Rad1 Be7 / e5 13.a4 Be7 |
| W146 | no capture or check (67% / 28%) | 10 | 3 | 0.972 | 0.581 | Bxh6+ > Nh5+; g3 > Qf3; g3 > Nb3 | h5 21.Rh1 g4 22.Rh4 / 19.g3 Qd5 20.Rg1 e6 / 22.Bf4 Rd8 23.Rd2 a6 |
| W48 | capture (100% / 67%) | 21 | 5 | 0.868 | 0.328 | Qe7 > Kf7; Qxd3 > Qc8; Rxd8 > Qe1+; Qxc4 > Bxf4 | Bh5 19.b3 Qxc2 / 21.Qxg5 h6 22.Qe7 / 17.Qxa5 b6 18.Qb5 |
| W103 | two or more captures (67% / 38%) | 13 | 4 | 0.863 | 0.543 | Bd4 > Rad8; Bxc2 > Kg3; Bxd3 > Ne4; Bb5 > Qxc6+ | Kb5 30.Qd5 Bf3+ 31.Kh2 Bxd5 / Kxf7 19.Nxe5+ Kg7 20.O-O Qd5 / 18.Be2 Nb6 19.Bb2 Bxb2 20.Qxd8 |

### Best and clean, by cleanliness

| concept | tier | branch points | positions | k | replication (null 95th) | agreement (null 95th) | board | top activating windows |
|---|---|---|---|---|---|---|---|---|
| W50 | best | 21 | 8 | 2,3,4,5,6,8 | 0.965 (0.222) | 0.47 (0.012) | 0.736 | Qxa1+ 31.Kh2 Nf5 32.Qh6+ Nxh6 33.Nxh6 Kxh6 34.Rd3 Qe5+ / Rd8 29.Qxd8 Qxd8 30.Rxd8 f5 31.Re7+ Kf6 32.Ra7 Kg5 / Rxa4 17.Qxa4 Bd6 18.h3 Qf6 19.Qb5 Rb8 20.d5 exd5 |
| W138 | best | 10 | 3 | 2,3,4,5,6,8 | 0.992 (0.14) | 0.618 (0.025) | 0.847 | Bd6 17.Nc3 d4 / Bd6 21.Rad1 Be7 / e5 13.a4 Be7 |
| W21 | best | 34 | 8 | 2,3,4,5,6,8 | 0.975 (0.223) | 0.44 (0.011) | 0.789 | dxe5 18.Qxe5 O-O 19.Qxe7 Rab8 20.h3 Nd5 / Bxe3 20.Bb5 a6 21.Bxc6 bxc6 22.Re1 Bf4+ / Kxg7 19.f4 Ne3 20.Nxe3 Qxe3+ 21.Kh1 Nd4 |
| W126 | clean | 11 | 2 | 2,3,4,5,6,8 | 0.939 (0.175) | 0.733 (0.021) | 0.839 | 19.Bc4 O-O 20.Bd3 / 21.g3 Qf6 22.d5 / 23.exd5 Qxd5 24.Rdb1 |
| W256 | clean | 4 | 2 | 5,6 | 0.982 (0.302) | 0.95 (0.018) | 0.69 | 21.Rab1 Nxb1 22.Rxb1 Rxc2 23.Rb4 Rxa2 / Nxb7 18.Ne5 Rxa3 19.Rxa3 Bxa3 20.Nxc6 / Nxf5 34.exf5 Rxd6 35.Nxd6 Qxd6 36.Rb7 |
| W297 | clean | 3 | 2 | 4,6,8 | 0.895 (0.138) | 0.619 (0.009) | 0.714 | Rxd8 32.b6 axb6 33.axb6 Bxb6 / Bc5 27.Rf4 f6 28.Rg4 g5 / Rb8 27.Bd5 Rxb2+ 28.Kh1 Bf4 |
| W96 | clean | 14 | 2 | 2,3,4,5,6,8 | 0.858 (0.171) | 0.683 (0.015) | 0.809 | 25.Bf6 Bxf6 26.gxf6 / Nxe4 19.fxe4 Rfe8 / Rb4 24.Qxa5 Qxa5 |
| W29 | best | 28 | 5 | 2,3,4,5,6,8 | 0.978 (0.231) | 0.595 (0.011) | 0.662 | Qe1+ 28.Rg1 Qe4+ / Nb4 21.Rde3 Re8 / 32.Rg8+ Rg7 33.Rxg7+ |
| W219 | clean | 6 | 2 | 4,5,6,8 | 0.973 (0.151) | 0.686 (0.037) | 0.783 | 14...g5 15.h3 g4 16.hxg4 fxg4 / 11...h6 12.Bh4 g5 13.Bg3 O-O-O / h4 31.g4 f5 32.f3 fxg4 |
| W25 | best | 31 | 10 | 2,3,4,5,6 | 0.956 (0.344) | 0.429 (0.011) | 0.718 | 19.Nxe4 Bxe4 20.Bxf8 Bxc2 21.Rdh1 Bg6+ 22.Kd1 / 25.Ng5 Rxd8 26.Rxd8+ Kg7 27.Rd7 Nb6 28.Rxf7+ / 29.Rxg7 Nf5 30.Nxf5 exf5 31.Rxg6 Rf8 32.e6 |
| W197 | best | 7 | 3 | 2,3,4 | 0.956 (0.175) | 0.565 (0.03) | 0.836 | a6 16.a4 a5 / 24.a4 b6 25.Kh1 / a5 24.a4 Rbd8 |
| W301 | clean | 3 | 2 | 2,3 | 0.793 (0.086) | 0.436 (0.009) | 0.78 | Qe7 13.Bg5 Qc5 14.Be3 / 16.Bd2 Qb6 17.Be3 Bb4 / 19.Ne5+ Ke7 20.Ng6+ Kf7 |
| W95 | best | 14 | 3 | 2,3,4,5,6 | 0.908 (0.119) | 0.416 (0.015) | 0.838 | a5 16.Bg5 a4 / 28.R4e2 Bh3 29.f3 / 18.h3 Nf4 19.Qf3 |
| W146 | best | 10 | 3 | 3,4,5,6,8 | 0.972 (0.203) | 0.581 (0.025) | 0.836 | h5 21.Rh1 g4 22.Rh4 / 19.g3 Qd5 20.Rg1 e6 / 22.Bf4 Rd8 23.Rd2 a6 |
| W46 | best | 23 | 4 | 2,3,4,5,6,8 | 0.835 (0.206) | 0.495 (0.012) | 0.841 | Be7 15.Nd2 Rf8 16.O-O-O Rf6 / Rc8 24.Bc4 Bf5 25.Rhe1 Bxe4 / d4 17.Ne2 Bxg2 18.Rg1 Bf3 |
| W167 | best | 8 | 4 | 2,5,6,8 | 0.949 (0.182) | 0.436 (0.023) | 0.834 | O-O 19.Qxb7 Qxe2 / 29.Bf3 Re6 30.c6 / Bg2 22.Kd2 Bxf1 |
| W59 | best | 20 | 4 | 2,3,4,5,6,8 | 0.919 (0.15) | 0.387 (0.011) | 0.782 | 22.Qxe7 Qxc3 23.Qxb7 / Kh8 22.Be5 Rg8 / Qb2 20.Qxb7 Rab8 |
| W27 | best | 30 | 7 | 2,3,4,5,6,8 | 0.909 (0.236) | 0.288 (0.012) | 0.815 | Nxd4 19.Nxd4 Bc5 20.Rb4 Bxd4 21.Rxd4 Qf6 / Re3 26.Rd6 Re8 27.Ng5 Bf5 28.e6 Bd3 / Re3 29.f4 d4 30.Rbd1 d3 31.Rxd3 Rxd3 |
| W79 | best | 16 | 3 | 2,3,4,5,6,8 | 0.901 (0.231) | 0.363 (0.014) | 0.711 | Rd8 28.Nb6 Bc5 / 28.Rf8 Bxf2 29.Rxg8+ / Rf8 21.Rg7+ Kh8 |
| W134 | best | 11 | 3 | 2,3,4,5,8 | 0.951 (0.19) | 0.555 (0.021) | 0.789 | Qxc2 21.Rdc1 Qb2 / Qxc3 23.Qxb7 e4 / Qb2 20.Qxb7 Rab8 |
| W117 | best | 12 | 5 | 2,3,4,5 | 0.953 (0.171) | 0.272 (0.02) | 0.832 | 20.Rh3 Bg7 21.Qg4 / Rac8 22.Re2 Rc6 / Rf6 22.Re1 Bf5 |
| W34 | clean | 27 | 11 | 2,3,4,5,6,8 | 0.921 (0.383) | 0.218 (0.012) | 0.761 | 21.Kh2 Nxf2 22.Nxf5 / Rd6 32.Rxd5 exd5 / 22.Ne6 Qf7 23.Nxf4 |
| W210 | clean | 6 | 2 | 2,3,4,5,6,8 | 0.919 (0.195) | 0.498 (0.037) | 0.777 | fxg5 16.Re1 Qf6 17.Qe2 Be6 18.Nd2 Rad8 19.c4 c5 / Rf8 15.O-O g4 16.Bxg4 hxg4 17.Qxg4 Ba6 18.Qh5+ Rf7 / Rf5 28.Nd6 R5f6 29.Qxa6 d4 30.Qd3+ g6 31.Qxd4 e5 |
| W312 | clean | 3 | 2 | 2,3 | 0.841 (0.137) | 0.333 (0.009) | 0.843 | Nc6 21.Nc5 Bc8 / 12.Nc3 e5 13.a4 / Nc6 20.Rb1 Rb8 |
| W173 | clean | 8 | 2 | 2,3,4,5,6,8 | 0.894 (0.158) | 0.543 (0.023) | 0.785 | Bg7 18.Rfb1 O-O 19.Rxe7 Qa2 20.Rbb7 / Qc6 17.c3 dxc3 18.bxc3 Be7 19.Nf7 / Ne5 17.Bb2 f6 18.b4 d5 19.Nc5 |
| W164 | clean | 9 | 4 | 2,3,4 | 0.849 (0.138) | 0.242 (0.026) | 0.712 | fxe6 32.Bxe6 Re7 / 17.b4 b5 18.Qa5 / 23.d6 c4 24.Bf1 |
| W70 | clean | 17 | 2 | 2,3,4,5,6,8 | 0.943 (0.136) | 0.55 (0.014) | 0.793 | 25.Rxh1 Bf4 26.Bxf4 Qxf4 27.Qc6 Qg4+ 28.Kd2 Qxg2+ 29.Kc3 / 18.Re1 Nd4 19.c3 Ne6 20.d4 Rad8 21.Qf3 Ng5 22.Qxc6 / Ne5 17.Qh7 Nxd5 18.Qf5 Nb4 19.a3 Nxc2 20.Qxc2 a6 |
| W139 | best | 10 | 5 | 2,3,4,5,6 | 0.923 (0.213) | 0.31 (0.025) | 0.848 | Bxd5 22.Nf3 Bxf3 23.Rxf3 / 25.Raf1 Qd6 26.Rxf5 e4+ / 28.Rf1 Rf8 29.Ng4 Qh5 |
| W63 | best | 19 | 3 | 2,3,4,5,6,8 | 0.945 (0.165) | 0.519 (0.012) | 0.772 | 33.Kc4 Qxc2+ 34.Kb4 / Qxc8 22.Qc5+ Qxc5 / Qg4+ 24.Kf1 Qh3+ |
| W112 | best | 12 | 3 | 2,3,4,5,6,8 | 0.924 (0.367) | 0.673 (0.021) | 0.685 | Nxh1 29.Nd5 Qc6+ 30.Bc4 Nxg3 31.Ba3 / Qb6+ 26.Kc2 Qxf6 27.Ne4 Qxf3 28.Ne5 / 30.Qb8+ Ke7 31.Qxa7+ Kf6 32.Qxa6 Nf4 |
| W102 | best | 13 | 5 | 2,3,4,5,6,8 | 0.977 (0.211) | 0.325 (0.022) | 0.689 | Qb4 31.Qc2 Rc7 32.b3 Rdc8 33.Qe4 Qxb3 / 22.Qb8+ Qd8 23.Qxa7 O-O 24.Ba3 Re8 25.Bb5 / 28.Bd3 Qc6 29.Be4 Qb5+ 30.Bd3 Qc6 31.Be4 |
| W152 | clean | 9 | 2 | 2,3,4,5,6 | 0.835 (0.115) | 0.604 (0.026) | 0.744 | Nc4 20.Nc5 b6 / Rc8 28.Rb7 a5 / Nc4 16.Bc1 Bxc3 |
| W246 | clean | 5 | 2 | 2,3,4 | 0.813 (0.128) | 0.601 (0.037) | 0.767 | 25.gxh3 Rxh3 26.Qc2 Rc8 / 21.Bxb2 Qf4+ 22.Kb1 Bf6 / d1=Q 25.Rf1+ Kb8 26.Rxd1 |
| W177 | clean | 8 | 2 | 2,3,4,5,6,8 | 0.721 (0.154) | 0.76 (0.023) | 0.829 | Bc5 20.Rb4 Bxd4 21.Rxd4 / 26.Rd6 Re8 27.Ng5 Bf5 / Rxb3 33.Nxc6 Rc3 34.Ne5 |
| W226 | clean | 6 | 2 | 2,3,4 | 0.888 (0.319) | 0.421 (0.037) | 0.822 | Ng4 15.Bd6 Rd8 16.Be7 / 20.Qd5 Ne7 21.Qd3 Ng6 / 25.Ng5 Bd3 26.Rfd1 Be2 |
| W161 | clean | 9 | 2 | 2,3,4,6 | 0.872 (0.234) | 0.543 (0.026) | 0.823 | 22.Rc1 Qb5 23.Rab1 / 18.Rac1 Qxa3 19.Ra1 / Rf7 30.Re7 Rxe7 |
| W237 | best | 6 | 3 | 2,3,4,5 | 0.861 (0.13) | 0.325 (0.037) | 0.678 | bxc5 14.Qe2+ Qe7 / 13.Bxf3 Ba5 14.O-O / Bxc4+ 15.Qe2 Bxd3 |
| W171 | clean | 8 | 2 | 2,3,4,5,6,8 | 0.844 (0.094) | 0.367 (0.023) | 0.829 | Rf8 26.hxg4 Qf6 27.Nh3 Rhg8 28.g5 Qc6 29.Rg1 Ne5 / 15.Kh1 Bg4 16.Nxg4 Nxg4 17.Qxg4 e3 18.Rfe1 Rfe8 19.Re2 / Qc5 15.a3 Bc3 16.Bxc3 Nxf3 17.Qxf3 Nd5 18.Bxg7 Rhg8 |
| W103 | best | 13 | 4 | 3,4,5,6 | 0.863 (0.271) | 0.543 (0.023) | 0.731 | Kb5 30.Qd5 Bf3+ 31.Kh2 Bxd5 / Kxf7 19.Nxe5+ Kg7 20.O-O Qd5 / 18.Be2 Nb6 19.Bb2 Bxb2 20.Qxd8 |
| W101 | best | 13 | 3 | 2,3,4,5,6 | 0.727 (0.152) | 0.379 (0.022) | 0.818 | Qxb8 22.Bxb8 Rxb8 23.Rb1 Rxb1+ / 18.Qxc6 Bxf3 19.gxf3 Qg5+ 20.Kf1 / 21.Qc6 Rxb1 22.Rxb1 Qa2 23.Rf1 |
| W145 | clean | 10 | 2 | 2,3,4,5 | 0.688 (0.089) | 0.466 (0.026) | 0.844 | 28.Qf3 Bxd4 29.Rxd4 / 18.Qf3 Rad8 19.g3 / Qf6 23.Bxf5 Qxf5 |
| W315 | clean | 3 | 2 | 2,3 | 0.794 (0.106) | 0.515 (0.009) | 0.791 | Kh8 16.Qg3 Qxc6 / Rd2 26.b4 Re8 / Qxd3+ 17.Kg1 Bxe3 |
| W73 | clean | 17 | 4 | 2,3,4,5,6,8 | 0.907 (0.232) | 0.245 (0.014) | 0.769 | Re8+ 30.Be2 Rxe2+ / Qb7+ 37.Kg1 fxe5 / Qxc2+ 34.Kxc2 d3+ |
| W158 | best | 9 | 3 | 2,3,4,5,6,8 | 0.719 (0.159) | 0.358 (0.026) | 0.821 | Nb4 32.Ng4 Qxb2 / Rg6 32.Ne8+ Kh6 / Qxc2 23.Rdc1 Qe4 |
| W221 | best | 6 | 5 | 2,3,5,6 | 0.81 (0.168) | 0.261 (0.037) | 0.786 | 37.Kg1 fxe5 38.d7 Nf6 / 32.Kb1 Nc3+ 33.Kb2 Nd1+ / 30.Bc4+ Ka4 31.Bb3+ Kb5 |
| W33 | clean | 27 | 4 | 2,3,4,5,6 | 0.828 (0.125) | 0.189 (0.011) | 0.839 | h5 29.g4 hxg4 / g5 16.g4 Bg7 / 17.g3 h5 18.Kg2 |
| W48 | best | 21 | 5 | 2,3,4,5,6,8 | 0.868 (0.286) | 0.328 (0.012) | 0.72 | Bh5 19.b3 Qxc2 / 21.Qxg5 h6 22.Qe7 / 17.Qxa5 b6 18.Qb5 |
| W147 | best | 10 | 3 | 2,3,4,5 | 0.72 (0.143) | 0.327 (0.025) | 0.843 | e4 21.Ne5 c5 22.Rxe4 / 17.Re1 Be6 18.Bxe6 fxe6 / Bc5 17.Qe2 Ng4 18.h3 |
| W37 | best | 26 | 5 | 2,3,4,5,6,8 | 0.815 (0.278) | 0.334 (0.012) | 0.813 | Bxf2+ 18.Kh1 Rf7 19.Be3 / Raf8 25.Re1 Rxf3 26.Bxf3 / Nf4 27.g3 Ne6 28.Bd5 |
| W162 | clean | 9 | 4 | 2,3,4,5,6 | 0.645 (0.104) | 0.224 (0.026) | 0.727 | 31.Kg2 Qxe5 32.Nf3 / Nc2 24.d5 Qf6 / Kf8 20.Qxd2 Kg7 |
| W88 | clean | 14 | 2 | 2,3,4,5,6,8 | 0.861 (0.319) | 0.485 (0.015) | 0.846 | 15.h4 O-O-O 16.g3 Nc5 17.Bh3+ Nd7 / 17.dxe5+ Ke7 18.O-O b6 19.Nb5 Bb7 / 20.Qd2 Rd8 21.Rfd1 Bc6 22.Qe3 Rcd7 |
| W110 | clean | 12 | 4 | 2,3,4,8 | 0.834 (0.234) | 0.227 (0.021) | 0.796 | Nf5 20.Bxf5 Bxf5 21.Re1 / 17.cxd4 Nd5 18.h3 Bh5 / 23.Rad1 d5 24.f3 e3 |
| W308 | clean | 3 | 2 | 2,3,4 | 0.665 (0.159) | 0.333 (0.009) | 0.788 | 18.Qxb7 Rb8 19.Qa6 / 22.Qxb7 Bxd4 23.exd4 / 17.Qxb7 Qxe4 18.Qxc7 |
| W49 | clean | 21 | 10 | 2,3,4,5,6 | 0.586 (0.146) | 0.126 (0.011) | 0.776 | 20.Nd5 Qg6 21.Nxe7+ / g6 20.Nxg6 hxg6 / 28.Ne4 Ne2+ 29.Kh2 |
| W236 | clean | 6 | 2 | 2,3 | 0.764 (0.125) | 0.14 (0.037) | 0.789 | 28.Nb7 Rc7 29.Na5 / Qxa3 25.Qxc6 Qxb4 / Qb2 22.Qb4 Qxb4 |
| W18 | clean | 37 | 13 | 2,3,4,5,6,8 | 0.822 (0.252) | 0.164 (0.009) | 0.82 | 25.Ba6 Bc6 26.Rb8+ Kd7 / Rf6 30.Bd3+ Kg7 31.Qe7+ / Bb4 18.Bc4 Qg4 19.h3 |
| W45 | clean | 23 | 2 | 2,3,4,5,6,8 | 0.762 (0.27) | 0.471 (0.012) | 0.813 | 20.Nd4 Bd7 21.Qc2 g6 22.Rae1 / 16.Qd3 Qf6 17.Nf3 Rad8 18.Rae1 / a4 16.a3 b5 17.Kb1 c5 |
| W155 | clean | 9 | 3 | 2,3,4,5,6,8 | 0.818 (0.219) | 0.2 (0.026) | 0.727 | Qd8 23.Qe5+ Qe7 / Qb4 31.Qc2 Rc7 / 28.Bd3 Qc6 29.Be4 |
| W198 | clean | 7 | 3 | 2,3,4,5,6 | 0.419 (0.163) | 0.521 (0.037) | 0.841 | 23.Nc7 Qe6 24.Nxe6 / 23.d7 Nf7 24.Rd1 / dxe2 30.Re1 Rd1 |
| W154 | clean | 9 | 2 | 2,3,4,5,6 | 0.597 (0.147) | 0.287 (0.026) | 0.782 | 22.Qxd3 Qd6 23.g3 / Bd6 15.Bg4 g6 / Nd5 24.Nh4 Nf4 |

