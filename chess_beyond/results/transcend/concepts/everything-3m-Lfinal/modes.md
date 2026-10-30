# Flow modes, everything-3m-Lfinal

Truncated SVD of the excess-rate matrix r[i, j] = (C - E) / (N_i + prior): how much more often latent j turns on within 4 plies of i's onset than in sibling rollouts. **diff** = r under chess-pgn-2400plus minus r under chess-pgn-1000-1300 (positive: stronger when chess-pgn-2400plus plays). A mode is a group of source latents (u) feeding a group of target latents (v).

## diff

### diff mode 0: 6.8% of the matrix

- **6153 -> 13586** (chess-pgn-1000-1300 +49.0%, chess-pgn-2400plus +13.8%)  
  6153 (r 0.58): Nf6 4.Nb5 e5 5.dxe5 Nh5 6. -&gt; e3  
  -> 13586 (r 0.43): Rfe8 22.Re3 Rxe3 23.Nxe3 Re8 24.Nd5 -&gt; c5
- **6153 -> 15816** (chess-pgn-1000-1300 +53.7%, chess-pgn-2400plus +18.5%)  
  6153 (r 0.58): Nf6 4.Nb5 e5 5.dxe5 Nh5 6. -&gt; e3  
  -> 15816 (r 0.11): Qg2+ 72.Kd6 Qg6+ 73.Re6 Qxe6+ 74.Kxe6 -&gt; Ke2
- **6153 -> 8792** (chess-pgn-1000-1300 +49.5%, chess-pgn-2400plus +16.2%)  
  6153 (r 0.58): Nf6 4.Nb5 e5 5.dxe5 Nh5 6. -&gt; e3  
  -> 8792 (r 0.35): Rae8 21.Qxh6 Re6 22.Rf7+ R6e7 23.Rxe7+ -&gt; Rxe7
- **1956 -> 13586** (chess-pgn-1000-1300 +42.3%, chess-pgn-2400plus +10.9%)  
  1956 (r 0.62): d5 5.exd5 Na5 6.Bb5+ c6 7. -&gt; dxc6  
  -> 13586 (r 0.43): Rfe8 22.Re3 Rxe3 23.Nxe3 Re8 24.Nd5 -&gt; c5
- **6153 -> 11829** (chess-pgn-1000-1300 +46.7%, chess-pgn-2400plus +12.7%)  
  6153 (r 0.58): Nf6 4.Nb5 e5 5.dxe5 Nh5 6. -&gt; e3  
  -> 11829 (r 0.38): Rxd3 47.Kf2 Rb3 48.h5 Ra6 49. -&gt; g4
- **1956 -> 15816** (chess-pgn-1000-1300 +40.6%, chess-pgn-2400plus +10.9%)  
  1956 (r 0.62): d5 5.exd5 Na5 6.Bb5+ c6 7. -&gt; dxc6  
  -> 15816 (r 0.11): Qg2+ 72.Kd6 Qg6+ 73.Re6 Qxe6+ 74.Kxe6 -&gt; Ke2
- **5347 -> 13586** (chess-pgn-1000-1300 +36.4%, chess-pgn-2400plus +7.2%)  
  5347 (r 0.55): d6 4.O-O Be7 5.c3 Nf6 6. -&gt; d3  
  -> 13586 (r 0.43): Rfe8 22.Re3 Rxe3 23.Nxe3 Re8 24.Nd5 -&gt; c5
- **5347 -> 15816** (chess-pgn-1000-1300 +36.7%, chess-pgn-2400plus +8.2%)  
  5347 (r 0.55): d6 4.O-O Be7 5.c3 Nf6 6. -&gt; d3  
  -> 15816 (r 0.11): Qg2+ 72.Kd6 Qg6+ 73.Re6 Qxe6+ 74.Kxe6 -&gt; Ke2

### diff mode 1: 4.0% of the matrix

- **6153 -> 659** (chess-pgn-1000-1300 -3.9%, chess-pgn-2400plus -1.2%)  
  6153 (r 0.58): Nf6 4.Nb5 e5 5.dxe5 Nh5 6. -&gt; e3  
  -> 659 (r 0.49): Bc5 12.h3 O-O 13.a3 a5 14. -&gt; g4
- **6153 -> 10885** (chess-pgn-1000-1300 -2.4%, chess-pgn-2400plus -2.0%)  
  6153 (r 0.58): Nf6 4.Nb5 e5 5.dxe5 Nh5 6. -&gt; e3  
  -> 10885 (r 0.44): Qe7 13.Nxc7 Rac8 14.Nxd5 Nxd5 15.c4 -&gt; Nf6
- **1956 -> 659** (chess-pgn-1000-1300 -3.1%, chess-pgn-2400plus -2.0%)  
  1956 (r 0.62): d5 5.exd5 Na5 6.Bb5+ c6 7. -&gt; dxc6  
  -> 659 (r 0.49): Bc5 12.h3 O-O 13.a3 a5 14. -&gt; g4
- **5347 -> 659** (chess-pgn-1000-1300 -2.5%, chess-pgn-2400plus +0.3%)  
  5347 (r 0.55): d6 4.O-O Be7 5.c3 Nf6 6. -&gt; d3  
  -> 659 (r 0.49): Bc5 12.h3 O-O 13.a3 a5 14. -&gt; g4
- **6153 -> 14592** (chess-pgn-1000-1300 -0.3%, chess-pgn-2400plus +1.9%)  
  6153 (r 0.58): Nf6 4.Nb5 e5 5.dxe5 Nh5 6. -&gt; e3  
  -> 14592 (r 0.50): Be6 15.Ne2 Qd6 16.Bd2 Rfe8 17. -&gt; Nd4
- **6153 -> 10529** (chess-pgn-1000-1300 -4.1%, chess-pgn-2400plus -0.5%)  
  6153 (r 0.58): Nf6 4.Nb5 e5 5.dxe5 Nh5 6. -&gt; e3  
  -> 10529 (r 0.47): e5 7.Bxg7 Kxg7 8.d5 Ne8 9.h4 -&gt; f5
- **6153 -> 7027** (chess-pgn-1000-1300 -1.6%, chess-pgn-2400plus -0.3%)  
  6153 (r 0.58): Nf6 4.Nb5 e5 5.dxe5 Nh5 6. -&gt; e3  
  -> 7027 (r 0.52): a6 16.Nbd4 Nxd4 17.Nxd4 Bg6 18.O-O -&gt; Rad8
- **1956 -> 10885** (chess-pgn-1000-1300 -3.8%, chess-pgn-2400plus -1.7%)  
  1956 (r 0.62): d5 5.exd5 Na5 6.Bb5+ c6 7. -&gt; dxc6  
  -> 10885 (r 0.44): Qe7 13.Nxc7 Rac8 14.Nxd5 Nxd5 15.c4 -&gt; Nf6

### diff mode 2: 2.4% of the matrix

- **7935 -> 10374** (chess-pgn-1000-1300 +37.9%, chess-pgn-2400plus +15.7%)  
  7935 (r 0.39): Bd6 6.Bc4 e5 7.Ng5 O-O 8.Qh5 -&gt; g6  
  -> 10374 (r 0.76): Nf6 9.Qxc6+ Nxc6 10.Bxc6+ bxc6 11. -&gt; Bg5
- **2494 -> 10374** (chess-pgn-1000-1300 +14.0%, chess-pgn-2400plus +0.2%)  
  2494 (r 0.61): Nxe4 4.Nxe5 Qe7 5.Nf3 Nc3+ 6. -&gt; Be2  
  -> 10374 (r 0.76): Nf6 9.Qxc6+ Nxc6 10.Bxc6+ bxc6 11. -&gt; Bg5
- **949 -> 10374** (chess-pgn-1000-1300 +43.4%, chess-pgn-2400plus +24.1%)  
  949 (r 0.48): Nf6 8.Nbd2 e6 9.c4 Qd6 10. -&gt; Bxd6  
  -> 10374 (r 0.76): Nf6 9.Qxc6+ Nxc6 10.Bxc6+ bxc6 11. -&gt; Bg5
- **8959 -> 10374** (chess-pgn-1000-1300 +35.2%, chess-pgn-2400plus +16.8%)  
  8959 (r 0.50): Qa5 5.e4 Bd7 6.Bd2 Qa6 7. -&gt; Bxa6  
  -> 10374 (r 0.76): Nf6 9.Qxc6+ Nxc6 10.Bxc6+ bxc6 11. -&gt; Bg5
- **13987 -> 10374** (chess-pgn-1000-1300 +39.6%, chess-pgn-2400plus +20.1%)  
  13987 (r 0.56): Nf6 4.d3 e6 5.Qf3 Nxf3+ 6. -&gt; Nxf3  
  -> 10374 (r 0.76): Nf6 9.Qxc6+ Nxc6 10.Bxc6+ bxc6 11. -&gt; Bg5
- **2148 -> 10374** (chess-pgn-1000-1300 +39.8%, chess-pgn-2400plus +23.0%)  
  2148 (r 0.62): d5 5.exd5 Nxd5 6.Nxd5 Nd4 7.Qg4 -&gt; Qxd5  
  -> 10374 (r 0.76): Nf6 9.Qxc6+ Nxc6 10.Bxc6+ bxc6 11. -&gt; Bg5
- **15091 -> 10374** (chess-pgn-1000-1300 +32.6%, chess-pgn-2400plus +16.2%)  
  15091 (r 0.39): bxc6 9.O-O Bg7 10.d4 O-O 11. -&gt; Bxg5  
  -> 10374 (r 0.76): Nf6 9.Qxc6+ Nxc6 10.Bxc6+ bxc6 11. -&gt; Bg5
- **3004 -> 10374** (chess-pgn-1000-1300 +28.3%, chess-pgn-2400plus +11.2%)  
  3004 (r 0.56): cxd4 4.Qxd4 Nf6 5.e4 Nc6 6.e5 -&gt; Nxd4  
  -> 10374 (r 0.76): Nf6 9.Qxc6+ Nxc6 10.Bxc6+ bxc6 11. -&gt; Bg5

### diff mode 3: 1.6% of the matrix

- **7297 -> 16020** (chess-pgn-1000-1300 -0.5%, chess-pgn-2400plus -0.8%)  
  7297 (r 0.53): d6 6.Bc4 Nf6 7.e5 dxe5 8. -&gt; Qxe5+  
  -> 16020 (r 0.50): Nf6 16.Nh6+ gxh6 17.Rxh6 Ne4+ 18. -&gt; Kf3
- **14454 -> 16020** (chess-pgn-1000-1300 +2.6%, chess-pgn-2400plus +0.6%)  
  14454 (r 0.55): Kh8 17.h4 g6 18.h5 Kxh7 19.hxg6+ -&gt; Kg7  
  -> 16020 (r 0.50): Nf6 16.Nh6+ gxh6 17.Rxh6 Ne4+ 18. -&gt; Kf3
- **11133 -> 16020** (chess-pgn-1000-1300 +14.5%, chess-pgn-2400plus +2.6%)  
  11133 (r 0.48): Ke8 7.Qh5+ Ke7 8.Qf7+ Kd6 9. -&gt; Bf4+  
  -> 16020 (r 0.50): Nf6 16.Nh6+ gxh6 17.Rxh6 Ne4+ 18. -&gt; Kf3
- **14454 -> 14097** (chess-pgn-1000-1300 +6.7%, chess-pgn-2400plus +0.6%)  
  14454 (r 0.55): Kh8 17.h4 g6 18.h5 Kxh7 19.hxg6+ -&gt; Kg7  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **15016 -> 16020** (chess-pgn-1000-1300 +3.9%, chess-pgn-2400plus +8.1%)  
  15016 (r 0.57): Be7 8.Bc4 Nxe4 9.Bxe7 Nxc3 10.Bxd8 -&gt; Nxd1  
  -> 16020 (r 0.50): Nf6 16.Nh6+ gxh6 17.Rxh6 Ne4+ 18. -&gt; Kf3
- **4466 -> 16020** (chess-pgn-1000-1300 +6.9%, chess-pgn-2400plus +2.3%)  
  4466 (r 0.44): Qd8 15.Qxd4 f6 16.Nxd6+ Kd7 17.Nf7+ -&gt; Kc7  
  -> 16020 (r 0.50): Nf6 16.Nh6+ gxh6 17.Rxh6 Ne4+ 18. -&gt; Kf3
- **16269 -> 16020** (chess-pgn-1000-1300 +0.6%, chess-pgn-2400plus +0.3%)  
  16269 (r 0.48): Nc6 6.Bd3 Nxd4 7.Nxd4 Qxd4 8.Bb5+ -&gt; Bd7  
  -> 16020 (r 0.50): Nf6 16.Nh6+ gxh6 17.Rxh6 Ne4+ 18. -&gt; Kf3
- **14077 -> 16020** (chess-pgn-1000-1300 -0.1%, chess-pgn-2400plus -0.1%)  
  14077 (r 0.54): Ne4 6.c3 Nxf2 7.Kxf2 Bg3+ 8. -&gt; Kxg3  
  -> 16020 (r 0.50): Nf6 16.Nh6+ gxh6 17.Rxh6 Ne4+ 18. -&gt; Kf3

### diff mode 4: 1.3% of the matrix

- **5954 -> 11434** (chess-pgn-1000-1300 +36.5%, chess-pgn-2400plus +22.0%)  
  5954 (r 0.35): g5 5.d5 Na5 6.Qd4 b6 7. -&gt; Qxh8  
  -> 11434 (r 0.45): Ke6 19.Qxc8+ Nd7 20.Qxa8 Qxc2 21. -&gt; Qe8#
- **1291 -> 11434** (chess-pgn-1000-1300 +29.9%, chess-pgn-2400plus +12.6%)  
  1291 (r 0.58): d6 6.Qxh5 Rg8 7.Qxh7 Bg7 8.Qxg8+ -&gt; Bf8  
  -> 11434 (r 0.45): Ke6 19.Qxc8+ Nd7 20.Qxa8 Qxc2 21. -&gt; Qe8#
- **7864 -> 11434** (chess-pgn-1000-1300 +27.4%, chess-pgn-2400plus +14.8%)  
  7864 (r 0.50): Rxh6 14.Bxh6 Qh5 15.Bf4 Qh1+ 16. -&gt; Ke2  
  -> 11434 (r 0.45): Ke6 19.Qxc8+ Nd7 20.Qxa8 Qxc2 21. -&gt; Qe8#
- **16269 -> 11434** (chess-pgn-1000-1300 -0.1%, chess-pgn-2400plus +0.2%)  
  16269 (r 0.48): Nc6 6.Bd3 Nxd4 7.Nxd4 Qxd4 8.Bb5+ -&gt; Bd7  
  -> 11434 (r 0.45): Ke6 19.Qxc8+ Nd7 20.Qxa8 Qxc2 21. -&gt; Qe8#
- **5954 -> 4983** (chess-pgn-1000-1300 +25.6%, chess-pgn-2400plus +11.9%)  
  5954 (r 0.35): g5 5.d5 Na5 6.Qd4 b6 7. -&gt; Qxh8  
  -> 4983 (r 0.52): b5 33.Qe4 Qg5 34.Qa8+ Kc7 35. -&gt; Qxa7+
- **11133 -> 11434** (chess-pgn-1000-1300 +14.4%, chess-pgn-2400plus +4.7%)  
  11133 (r 0.48): Ke8 7.Qh5+ Ke7 8.Qf7+ Kd6 9. -&gt; Bf4+  
  -> 11434 (r 0.45): Ke6 19.Qxc8+ Nd7 20.Qxa8 Qxc2 21. -&gt; Qe8#
- **7409 -> 11434** (chess-pgn-1000-1300 +30.5%, chess-pgn-2400plus +15.6%)  
  7409 (r 0.49): fxe5 4.Qh5+ g6 5.Qxe5+ Ne7 6. -&gt; Qxh8  
  -> 11434 (r 0.45): Ke6 19.Qxc8+ Nd7 20.Qxa8 Qxc2 21. -&gt; Qe8#
- **1291 -> 4983** (chess-pgn-1000-1300 +35.1%, chess-pgn-2400plus +22.7%)  
  1291 (r 0.58): d6 6.Qxh5 Rg8 7.Qxh7 Bg7 8.Qxg8+ -&gt; Bf8  
  -> 4983 (r 0.52): b5 33.Qe4 Qg5 34.Qa8+ Kc7 35. -&gt; Qxa7+

### diff mode 5: 1.3% of the matrix

- **11887 -> 6441** (chess-pgn-1000-1300 +54.4%, chess-pgn-2400plus +38.0%)  
  11887 (r 0.53): d6 5.h3 c6 6.Bb3 Bxh3 7. -&gt; Rxh3  
  -> 6441 (r 0.47): Qc8 13.Na3 Bf5 14.c4 Bxd3 15.Qxd3 -&gt; Qf5
- **11887 -> 14097** (chess-pgn-1000-1300 -4.7%, chess-pgn-2400plus -4.7%)  
  11887 (r 0.53): d6 5.h3 c6 6.Bb3 Bxh3 7. -&gt; Rxh3  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **7997 -> 6441** (chess-pgn-1000-1300 -1.5%, chess-pgn-2400plus +0.1%)  
  7997 (r 0.58): Nc6 5.c4 a6 6.Ba4 b5 7.cxb5 -&gt; axb5  
  -> 6441 (r 0.47): Qc8 13.Na3 Bf5 14.c4 Bxd3 15.Qxd3 -&gt; Qf5
- **11781 -> 14097** (chess-pgn-1000-1300 +0.7%, chess-pgn-2400plus +2.7%)  
  11781 (r 0.54): bxc6 7.O-O Bg4 8.h3 Bh5 9.g4 -&gt; Bg6  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **9299 -> 14097** (chess-pgn-1000-1300 -3.0%, chess-pgn-2400plus -1.0%)  
  9299 (r 0.53): Nf6 5.O-O Ng4 6.h3 h5 7.hxg4 -&gt; hxg4  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **7997 -> 7219** (chess-pgn-1000-1300 -1.0%, chess-pgn-2400plus -0.3%)  
  7997 (r 0.58): Nc6 5.c4 a6 6.Ba4 b5 7.cxb5 -&gt; axb5  
  -> 7219 (r 0.52): Qxe4 6.Nf3 Nf6 7.Bh3 Ng4+ 8.Bxg4 -&gt; Qxg4
- **14457 -> 14097** (chess-pgn-1000-1300 +19.2%, chess-pgn-2400plus +8.7%)  
  14457 (r 0.61): c5 4.dxc5 Bxc5 5.e3 Nf6 6.Nb5 -&gt; Na6  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **4428 -> 6441** (chess-pgn-1000-1300 -0.3%, chess-pgn-2400plus +1.5%)  
  4428 (r 0.51): cxb4 5.d4 Nc6 6.a3 Bd7 7.axb4 -&gt; Bxb4+  
  -> 6441 (r 0.47): Qc8 13.Na3 Bf5 14.c4 Bxd3 15.Qxd3 -&gt; Qf5

### diff mode 6: 1.0% of the matrix

- **6353 -> 14097** (chess-pgn-1000-1300 +26.4%, chess-pgn-2400plus +13.8%)  
  6353 (r 0.48): g6 4.Qf3 Nf6 5.d3 Nd4 6.Qe3 -&gt; Nxc2+  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **7297 -> 14097** (chess-pgn-1000-1300 -2.1%, chess-pgn-2400plus -1.0%)  
  7297 (r 0.53): d6 6.Bc4 Nf6 7.e5 dxe5 8. -&gt; Qxe5+  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **16269 -> 14097** (chess-pgn-1000-1300 -3.6%, chess-pgn-2400plus +0.3%)  
  16269 (r 0.48): Nc6 6.Bd3 Nxd4 7.Nxd4 Qxd4 8.Bb5+ -&gt; Bd7  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **14457 -> 14097** (chess-pgn-1000-1300 +19.2%, chess-pgn-2400plus +8.7%)  
  14457 (r 0.61): c5 4.dxc5 Bxc5 5.e3 Nf6 6.Nb5 -&gt; Na6  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **1962 -> 14097** (chess-pgn-1000-1300 +20.8%, chess-pgn-2400plus +9.7%)  
  1962 (r 0.59): a6 5.Qh5 Nc6 6.Qxd5 Qxd5 7.Nxd5 -&gt; Kd7  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **2449 -> 14097** (chess-pgn-1000-1300 +22.7%, chess-pgn-2400plus +16.2%)  
  2449 (r 0.55): Ng4 10.exd6 Nf2+ 11.Kg1 Nxd1+ 12. -&gt; Kf1  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **5739 -> 14097** (chess-pgn-1000-1300 +23.8%, chess-pgn-2400plus +11.6%)  
  5739 (r 0.62): Qc5 4.Qe2 Nf6 5.Qb5+ Qxb5 6.Nxb5 -&gt; c6  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **12252 -> 14097** (chess-pgn-1000-1300 +16.0%, chess-pgn-2400plus +6.7%)  
  12252 (r 0.56): Nc6 4.Nf3 e6 5.Nb5 Be7 6. -&gt; Nxc7+  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+

### diff mode 7: 0.8% of the matrix

- **10928 -> 15150** (chess-pgn-1000-1300 +5.5%, chess-pgn-2400plus +3.0%)  
  10928 (r 0.56): g6 4.f4 Bg7 5.Nf3 O-O 6.e5 -&gt; dxe5  
  -> 15150 (r 0.55): Nxc3 8.bxc3 cxd4 9.cxd4 Bf5 10.Bd3 -&gt; Bg6
- **10928 -> 12836** (chess-pgn-1000-1300 +8.6%, chess-pgn-2400plus +2.1%)  
  10928 (r 0.56): g6 4.f4 Bg7 5.Nf3 O-O 6.e5 -&gt; dxe5  
  -> 12836 (r 0.51): d5 4.e5 Ne4 5.Nce2 c5 6. -&gt; f3
- **10928 -> 5657** (chess-pgn-1000-1300 +5.0%, chess-pgn-2400plus +0.7%)  
  10928 (r 0.56): g6 4.f4 Bg7 5.Nf3 O-O 6.e5 -&gt; dxe5  
  -> 5657 (r 0.50): f5 11.Bxe4 dxe4 12.d5 exf3 13. -&gt; Nxf3
- **10928 -> 11951** (chess-pgn-1000-1300 +5.6%, chess-pgn-2400plus +0.3%)  
  10928 (r 0.56): g6 4.f4 Bg7 5.Nf3 O-O 6.e5 -&gt; dxe5  
  -> 11951 (r 0.66): Be7 13.Ne4 Nxe4 14.Bxe7 Qxe7 15. -&gt; Qxe4
- **10928 -> 14959** (chess-pgn-1000-1300 +22.7%, chess-pgn-2400plus +21.1%)  
  10928 (r 0.56): g6 4.f4 Bg7 5.Nf3 O-O 6.e5 -&gt; dxe5  
  -> 14959 (r 0.75): Bd7 18.e5 dxe5 19.Nxe5 Re8 20. -&gt; Re4
- **3878 -> 15150** (chess-pgn-1000-1300 +10.4%, chess-pgn-2400plus +8.6%)  
  3878 (r 0.46): exd4 4.Bc4 Nf6 5.e5 Nxe5 6. -&gt; Nxe5  
  -> 15150 (r 0.55): Nxc3 8.bxc3 cxd4 9.cxd4 Bf5 10.Bd3 -&gt; Bg6
- **7297 -> 15150** (chess-pgn-1000-1300 +2.8%, chess-pgn-2400plus -0.7%)  
  7297 (r 0.53): d6 6.Bc4 Nf6 7.e5 dxe5 8. -&gt; Qxe5+  
  -> 15150 (r 0.55): Nxc3 8.bxc3 cxd4 9.cxd4 Bf5 10.Bd3 -&gt; Bg6
- **12907 -> 15150** (chess-pgn-1000-1300 +9.1%, chess-pgn-2400plus +5.4%)  
  12907 (r 0.60): exd4 4.Nxd4 Nf6 5.e5 Nxe5 6.Qe2 -&gt; d6  
  -> 15150 (r 0.55): Nxc3 8.bxc3 cxd4 9.cxd4 Bf5 10.Bd3 -&gt; Bg6

### diff mode 8: 0.8% of the matrix

- **6716 -> 1773** (chess-pgn-1000-1300 +8.1%, chess-pgn-2400plus +0.5%)  
  6716 (r 0.48): f6 4.Nf3 f5 5.Bg5 Be7 6.h4 -&gt; h6  
  -> 1773 (r 0.74): exf5 13.Rf3 d6 14.Rxf5 Bxf5 15. -&gt; g4
- **2552 -> 7976** (chess-pgn-1000-1300 +16.6%, chess-pgn-2400plus +7.6%)  
  2552 (r 0.61): O-O 7.Qh3 h6 8.Nf3 d5 9. -&gt; exd5  
  -> 7976 (r 0.63): f5 23.exf5 e4+ 24.Qf4 Nxf5 25.Qxd6 -&gt; Nxd6
- **6716 -> 7976** (chess-pgn-1000-1300 +11.3%, chess-pgn-2400plus +13.4%)  
  6716 (r 0.48): f6 4.Nf3 f5 5.Bg5 Be7 6.h4 -&gt; h6  
  -> 7976 (r 0.63): f5 23.exf5 e4+ 24.Qf4 Nxf5 25.Qxd6 -&gt; Nxd6
- **11552 -> 1773** (chess-pgn-1000-1300 +2.1%, chess-pgn-2400plus +0.6%)  
  11552 (r 0.66): Bf5 4.Bxc4 Nf6 5.Qb3 e6 6.Qxb7 -&gt; Nbd7  
  -> 1773 (r 0.74): exf5 13.Rf3 d6 14.Rxf5 Bxf5 15. -&gt; g4
- **6716 -> 6774** (chess-pgn-1000-1300 +22.2%, chess-pgn-2400plus +36.5%)  
  6716 (r 0.48): f6 4.Nf3 f5 5.Bg5 Be7 6.h4 -&gt; h6  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4
- **2552 -> 1298** (chess-pgn-1000-1300 -2.3%, chess-pgn-2400plus -0.9%)  
  2552 (r 0.61): O-O 7.Qh3 h6 8.Nf3 d5 9. -&gt; exd5  
  -> 1298 (r 0.68): Nxe5 8.dxe5 Bxe5 9.Nxe5 c6 10. -&gt; Bd3
- **6716 -> 2954** (chess-pgn-1000-1300 +28.0%, chess-pgn-2400plus +14.3%)  
  6716 (r 0.48): f6 4.Nf3 f5 5.Bg5 Be7 6.h4 -&gt; h6  
  -> 2954 (r 0.48): Qc5 10.d4 Qb6 11.Bxc6+ Qxc6 12. -&gt; Qb4
- **9323 -> 1773** (chess-pgn-1000-1300 +0.6%, chess-pgn-2400plus +1.9%)  
  9323 (r 0.40): Nd4 5.Nxe5 Bd6 6.Nxf7 O-O 7. -&gt; Nxd8+  
  -> 1773 (r 0.74): exf5 13.Rf3 d6 14.Rxf5 Bxf5 15. -&gt; g4

### diff mode 9: 0.7% of the matrix

- **7297 -> 12785** (chess-pgn-1000-1300 +21.2%, chess-pgn-2400plus +1.8%)  
  7297 (r 0.53): d6 6.Bc4 Nf6 7.e5 dxe5 8. -&gt; Qxe5+  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **7297 -> 3109** (chess-pgn-1000-1300 +14.7%, chess-pgn-2400plus +0.5%)  
  7297 (r 0.53): d6 6.Bc4 Nf6 7.e5 dxe5 8. -&gt; Qxe5+  
  -> 3109 (r 0.53): Kg7 28.Nd4 b5 29.b4 Rh8 30.Rxh8 -&gt; Kxh8
- **13406 -> 12785** (chess-pgn-1000-1300 +30.1%, chess-pgn-2400plus +9.2%)  
  13406 (r 0.51): Bf5 9.O-O Bxd3 10.Bxd3 Qxd3 11. -&gt; Qa4  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **7297 -> 4752** (chess-pgn-1000-1300 +22.0%, chess-pgn-2400plus +2.3%)  
  7297 (r 0.53): d6 6.Bc4 Nf6 7.e5 dxe5 8. -&gt; Qxe5+  
  -> 4752 (r 0.51): Qa6 21.h3 Rad8 22.Rxd8 Rxd8 23.Rxd8+ -&gt; Bxd8
- **7297 -> 13398** (chess-pgn-1000-1300 +13.6%, chess-pgn-2400plus +1.8%)  
  7297 (r 0.53): d6 6.Bc4 Nf6 7.e5 dxe5 8. -&gt; Qxe5+  
  -> 13398 (r 0.38): Rd8 15.c3 Qxc5 16.Bxc5 Rxd1 17. -&gt; Rfxd1
- **7297 -> 230** (chess-pgn-1000-1300 +11.7%, chess-pgn-2400plus +0.9%)  
  7297 (r 0.53): d6 6.Bc4 Nf6 7.e5 dxe5 8. -&gt; Qxe5+  
  -> 230 (r 0.54): Rfe8 23.c5 c6 24.h4 Qxc2 25. -&gt; Rxc2
- **14416 -> 12785** (chess-pgn-1000-1300 +64.4%, chess-pgn-2400plus +26.5%)  
  14416 (r 0.51): Bg4 4.h3 Bxf3 5.Qxf3 Qf6 6.Qxf6 -&gt; Nxf6  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **1041 -> 12785** (chess-pgn-1000-1300 -0.7%, chess-pgn-2400plus -0.6%)  
  1041 (r 0.64): Nf6 4.O-O Nc6 5.c3 d6 6.d4 -&gt; Bb6  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8

### diff mode 10: 0.6% of the matrix

- **8369 -> 6441** (chess-pgn-1000-1300 +36.5%, chess-pgn-2400plus +9.9%)  
  8369 (r 0.52): dxe5 8.dxe5 Qxd1+ 9.Nxd1 Bxf3 10.exf6 -&gt; Bxg2  
  -> 6441 (r 0.47): Qc8 13.Na3 Bf5 14.c4 Bxd3 15.Qxd3 -&gt; Qf5
- **5520 -> 6441** (chess-pgn-1000-1300 +4.8%, chess-pgn-2400plus +3.7%)  
  5520 (r 0.55): cxd5 5.Qb3 Bc8 6.Bxd5 e6 7.Bxb7 -&gt; Bxb7  
  -> 6441 (r 0.47): Qc8 13.Na3 Bf5 14.c4 Bxd3 15.Qxd3 -&gt; Qf5
- **1269 -> 6441** (chess-pgn-1000-1300 +24.4%, chess-pgn-2400plus +9.3%)  
  1269 (r 0.63): a6 8.Bd3 e6 9.Bg5 h6 10. -&gt; Bh4  
  -> 6441 (r 0.47): Qc8 13.Na3 Bf5 14.c4 Bxd3 15.Qxd3 -&gt; Qf5
- **121 -> 6441** (chess-pgn-1000-1300 +18.1%, chess-pgn-2400plus +11.0%)  
  121 (r 0.52): Bxc3+ 6.bxc3 O-O 7.e5 h6 8. -&gt; Bh4  
  -> 6441 (r 0.47): Qc8 13.Na3 Bf5 14.c4 Bxd3 15.Qxd3 -&gt; Qf5
- **7703 -> 6441** (chess-pgn-1000-1300 +23.7%, chess-pgn-2400plus +11.0%)  
  7703 (r 0.59): d6 5.d3 Nf6 6.O-O Bg4 7.h3 -&gt; Bxf3  
  -> 6441 (r 0.47): Qc8 13.Na3 Bf5 14.c4 Bxd3 15.Qxd3 -&gt; Qf5
- **8369 -> 10002** (chess-pgn-1000-1300 +3.8%, chess-pgn-2400plus +2.1%)  
  8369 (r 0.52): dxe5 8.dxe5 Qxd1+ 9.Nxd1 Bxf3 10.exf6 -&gt; Bxg2  
  -> 10002 (r 0.48): Nc6 17.Nc3 O-O-O 18.Bg5 h6 19.Bxf6 -&gt; gxf6
- **1997 -> 6441** (chess-pgn-1000-1300 +30.4%, chess-pgn-2400plus +17.4%)  
  1997 (r 0.49): c5 7.Qd3 d6 8.Bg5 h6 9. -&gt; Bh4  
  -> 6441 (r 0.47): Qc8 13.Na3 Bf5 14.c4 Bxd3 15.Qxd3 -&gt; Qf5
- **11526 -> 6441** (chess-pgn-1000-1300 +13.7%, chess-pgn-2400plus +6.6%)  
  11526 (r 0.62): e5 5.Nxc6 bxc6 6.Nc3 Nf6 7.Bg5 -&gt; Bb4  
  -> 6441 (r 0.47): Qc8 13.Na3 Bf5 14.c4 Bxd3 15.Qxd3 -&gt; Qf5

### diff mode 11: 0.6% of the matrix

- **5520 -> 2954** (chess-pgn-1000-1300 +10.8%, chess-pgn-2400plus +8.4%)  
  5520 (r 0.55): cxd5 5.Qb3 Bc8 6.Bxd5 e6 7.Bxb7 -&gt; Bxb7  
  -> 2954 (r 0.48): Qc5 10.d4 Qb6 11.Bxc6+ Qxc6 12. -&gt; Qb4
- **10963 -> 2954** (chess-pgn-1000-1300 +54.1%, chess-pgn-2400plus +34.5%)  
  10963 (r 0.60): Bb4 4.Bc4 Nf6 5.a3 Bxc3 6. -&gt; bxc3  
  -> 2954 (r 0.48): Qc5 10.d4 Qb6 11.Bxc6+ Qxc6 12. -&gt; Qb4
- **16269 -> 2954** (chess-pgn-1000-1300 +21.4%, chess-pgn-2400plus +1.6%)  
  16269 (r 0.48): Nc6 6.Bd3 Nxd4 7.Nxd4 Qxd4 8.Bb5+ -&gt; Bd7  
  -> 2954 (r 0.48): Qc5 10.d4 Qb6 11.Bxc6+ Qxc6 12. -&gt; Qb4
- **9926 -> 2954** (chess-pgn-1000-1300 +12.1%, chess-pgn-2400plus +7.5%)  
  9926 (r 0.45): g6 5.Nxc6 bxc6 6.Qd4 Bg7 7. -&gt; Qxg7  
  -> 2954 (r 0.48): Qc5 10.d4 Qb6 11.Bxc6+ Qxc6 12. -&gt; Qb4
- **11760 -> 2954** (chess-pgn-1000-1300 +29.4%, chess-pgn-2400plus +11.2%)  
  11760 (r 0.44): e5 6.Nxc6 bxc6 7.Bxc6+ Bd7 8. -&gt; Bxa8  
  -> 2954 (r 0.48): Qc5 10.d4 Qb6 11.Bxc6+ Qxc6 12. -&gt; Qb4
- **1414 -> 2954** (chess-pgn-1000-1300 +3.4%, chess-pgn-2400plus +2.0%)  
  1414 (r 0.51): Bh3 24.Ng6+ Kh7 25.Ne5 Qxf1+ 26.Qxf1 -&gt; Bxf1  
  -> 2954 (r 0.48): Qc5 10.d4 Qb6 11.Bxc6+ Qxc6 12. -&gt; Qb4
- **12473 -> 2954** (chess-pgn-1000-1300 +6.3%, chess-pgn-2400plus +2.1%)  
  12473 (r 0.59): Bb6 8.O-O h6 9.d5 Na5 10. -&gt; Bb5  
  -> 2954 (r 0.48): Qc5 10.d4 Qb6 11.Bxc6+ Qxc6 12. -&gt; Qb4
- **12118 -> 2954** (chess-pgn-1000-1300 +9.7%, chess-pgn-2400plus +3.1%)  
  12118 (r 0.53): Bxf3 5.exf3 cxd5 6.Nc3 e6 7.Bb5+ -&gt; Nd7  
  -> 2954 (r 0.48): Qc5 10.d4 Qb6 11.Bxc6+ Qxc6 12. -&gt; Qb4

### diff mode 12: 0.6% of the matrix

- **2552 -> 5626** (chess-pgn-1000-1300 +32.4%, chess-pgn-2400plus +8.1%)  
  2552 (r 0.61): O-O 7.Qh3 h6 8.Nf3 d5 9. -&gt; exd5  
  -> 5626 (r 0.40): O-O 11.h3 a5 12.O-O a4 13. -&gt; Ba2
- **2552 -> 2954** (chess-pgn-1000-1300 +0.8%, chess-pgn-2400plus +0.5%)  
  2552 (r 0.61): O-O 7.Qh3 h6 8.Nf3 d5 9. -&gt; exd5  
  -> 2954 (r 0.48): Qc5 10.d4 Qb6 11.Bxc6+ Qxc6 12. -&gt; Qb4
- **15241 -> 5626** (chess-pgn-1000-1300 +19.2%, chess-pgn-2400plus +8.5%)  
  15241 (r 0.57): d6 4.d4 Bg4 5.d5 a6 6.dxc6 -&gt; axb5  
  -> 5626 (r 0.40): O-O 11.h3 a5 12.O-O a4 13. -&gt; Ba2
- **1041 -> 5626** (chess-pgn-1000-1300 +27.3%, chess-pgn-2400plus +9.8%)  
  1041 (r 0.64): Nf6 4.O-O Nc6 5.c3 d6 6.d4 -&gt; Bb6  
  -> 5626 (r 0.40): O-O 11.h3 a5 12.O-O a4 13. -&gt; Ba2
- **190 -> 5626** (chess-pgn-1000-1300 +31.2%, chess-pgn-2400plus +23.8%)  
  190 (r 0.60): d6 4.d5 Nce7 5.Bb5+ c6 6.dxc6 -&gt; bxc6  
  -> 5626 (r 0.40): O-O 11.h3 a5 12.O-O a4 13. -&gt; Ba2
- **15749 -> 5626** (chess-pgn-1000-1300 +12.2%, chess-pgn-2400plus +2.1%)  
  15749 (r 0.67): Nc6 4.d4 Nge7 5.d5 exd5 6. -&gt; exd5  
  -> 5626 (r 0.40): O-O 11.h3 a5 12.O-O a4 13. -&gt; Ba2
- **6293 -> 5626** (chess-pgn-1000-1300 +12.4%, chess-pgn-2400plus +6.3%)  
  6293 (r 0.46): e6 7.Bb5+ Nc6 8.Nxc6 bxc6 9. -&gt; Bxc6+  
  -> 5626 (r 0.40): O-O 11.h3 a5 12.O-O a4 13. -&gt; Ba2
- **2552 -> 14383** (chess-pgn-1000-1300 -2.6%, chess-pgn-2400plus -1.9%)  
  2552 (r 0.61): O-O 7.Qh3 h6 8.Nf3 d5 9. -&gt; exd5  
  -> 14383 (r 0.48): Qb7 36.Rxc8 Rxc8 37.Qd3 b3 38.Qe3 -&gt; Rc4

### diff mode 13: 0.6% of the matrix

- **15749 -> 12116** (chess-pgn-1000-1300 -1.3%, chess-pgn-2400plus -0.7%)  
  15749 (r 0.67): Nc6 4.d4 Nge7 5.d5 exd5 6. -&gt; exd5  
  -> 12116 (r 0.51): Bg4 8.Bxf6 exf6 9.Nh4 g5 10. -&gt; f3
- **2552 -> 5648** (chess-pgn-1000-1300 +2.6%, chess-pgn-2400plus +1.6%)  
  2552 (r 0.61): O-O 7.Qh3 h6 8.Nf3 d5 9. -&gt; exd5  
  -> 5648 (r 0.52): Nb6 21.b3 Nxa4 22.bxa4 Nxd4 23.exd4 -&gt; Qxd4+
- **15749 -> 5648** (chess-pgn-1000-1300 +11.4%, chess-pgn-2400plus +3.1%)  
  15749 (r 0.67): Nc6 4.d4 Nge7 5.d5 exd5 6. -&gt; exd5  
  -> 5648 (r 0.52): Nb6 21.b3 Nxa4 22.bxa4 Nxd4 23.exd4 -&gt; Qxd4+
- **1041 -> 5648** (chess-pgn-1000-1300 +14.0%, chess-pgn-2400plus +3.5%)  
  1041 (r 0.64): Nf6 4.O-O Nc6 5.c3 d6 6.d4 -&gt; Bb6  
  -> 5648 (r 0.52): Nb6 21.b3 Nxa4 22.bxa4 Nxd4 23.exd4 -&gt; Qxd4+
- **2552 -> 2647** (chess-pgn-1000-1300 +50.1%, chess-pgn-2400plus +21.9%)  
  2552 (r 0.61): O-O 7.Qh3 h6 8.Nf3 d5 9. -&gt; exd5  
  -> 2647 (r 0.50): Nc6 5.c3 d5 6.exd5 Nxd5 7. -&gt; d3
- **15749 -> 2647** (chess-pgn-1000-1300 +22.5%, chess-pgn-2400plus +8.8%)  
  15749 (r 0.67): Nc6 4.d4 Nge7 5.d5 exd5 6. -&gt; exd5  
  -> 2647 (r 0.50): Nc6 5.c3 d5 6.exd5 Nxd5 7. -&gt; d3
- **1041 -> 2647** (chess-pgn-1000-1300 +45.3%, chess-pgn-2400plus +25.1%)  
  1041 (r 0.64): Nf6 4.O-O Nc6 5.c3 d6 6.d4 -&gt; Bb6  
  -> 2647 (r 0.50): Nc6 5.c3 d5 6.exd5 Nxd5 7. -&gt; d3
- **15749 -> 8787** (chess-pgn-1000-1300 +4.2%, chess-pgn-2400plus +1.3%)  
  15749 (r 0.67): Nc6 4.d4 Nge7 5.d5 exd5 6. -&gt; exd5  
  -> 8787 (r 0.53): d5 5.exd5 Nd4 6.c3 h6 7. -&gt; cxd4

### diff mode 14: 0.6% of the matrix

- **14416 -> 12785** (chess-pgn-1000-1300 +64.4%, chess-pgn-2400plus +26.5%)  
  14416 (r 0.51): Bg4 4.h3 Bxf3 5.Qxf3 Qf6 6.Qxf6 -&gt; Nxf6  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **14416 -> 16185** (chess-pgn-1000-1300 -11.2%, chess-pgn-2400plus -2.4%)  
  14416 (r 0.51): Bg4 4.h3 Bxf3 5.Qxf3 Qf6 6.Qxf6 -&gt; Nxf6  
  -> 16185 (r 0.52): Bb7 19.Bxf6 Bxf6 20.Bd5 Qc7 21.Bxb7 -&gt; Qxb7
- **14416 -> 7976** (chess-pgn-1000-1300 -6.3%, chess-pgn-2400plus -0.8%)  
  14416 (r 0.51): Bg4 4.h3 Bxf3 5.Qxf3 Qf6 6.Qxf6 -&gt; Nxf6  
  -> 7976 (r 0.63): f5 23.exf5 e4+ 24.Qf4 Nxf5 25.Qxd6 -&gt; Nxd6
- **35 -> 12785** (chess-pgn-1000-1300 +2.0%, chess-pgn-2400plus +1.6%)  
  35 (r 0.64): Nf6 5.Ng5 O-O 6.Bxf7+ Rxf7 7. -&gt; Nxf7  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **14416 -> 7067** (chess-pgn-1000-1300 -1.8%, chess-pgn-2400plus +0.7%)  
  14416 (r 0.51): Bg4 4.h3 Bxf3 5.Qxf3 Qf6 6.Qxf6 -&gt; Nxf6  
  -> 7067 (r 0.30): Qg6 13.Nh4 Qg3 14.Bxf7+ Kh8 15. -&gt; Ng6+
- **14416 -> 1773** (chess-pgn-1000-1300 +9.0%, chess-pgn-2400plus +1.8%)  
  14416 (r 0.51): Bg4 4.h3 Bxf3 5.Qxf3 Qf6 6.Qxf6 -&gt; Nxf6  
  -> 1773 (r 0.74): exf5 13.Rf3 d6 14.Rxf5 Bxf5 15. -&gt; g4
- **14416 -> 5626** (chess-pgn-1000-1300 -0.8%, chess-pgn-2400plus +0.7%)  
  14416 (r 0.51): Bg4 4.h3 Bxf3 5.Qxf3 Qf6 6.Qxf6 -&gt; Nxf6  
  -> 5626 (r 0.40): O-O 11.h3 a5 12.O-O a4 13. -&gt; Ba2
- **307 -> 12785** (chess-pgn-1000-1300 -0.2%, chess-pgn-2400plus -0.7%)  
  307 (r 0.60): Ng4 7.Qxg4 g6 8.Qf3 Nd4 9. -&gt; Qd3  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8

## chess-pgn-1000-1300

### chess-pgn-1000-1300 mode 0: 7.5% of the matrix

- **13991 -> 10775** (chess-pgn-1000-1300 +17.1%, chess-pgn-2400plus +12.4%)  
  13991 (r 0.54): Qb6 12.a4 a6 13.a5 Qc6 14.Na7+ -&gt; Kb8  
  -> 10775 (r 0.55): h6 9.Nbd2 Na5 10.b4 Nxc4 11.bxc5 -&gt; Nxd2
- **13118 -> 10775** (chess-pgn-1000-1300 +9.9%, chess-pgn-2400plus +11.4%)  
  13118 (r 0.42): Qb7 17.Nf5 Be5 18.Qg4 Bxa1 19.Qxg7+ -&gt; Bxg7  
  -> 10775 (r 0.55): h6 9.Nbd2 Na5 10.b4 Nxc4 11.bxc5 -&gt; Nxd2
- **8859 -> 10775** (chess-pgn-1000-1300 +19.4%, chess-pgn-2400plus +13.8%)  
  8859 (r 0.57): e6 5.Qe2 Nxd4 6.Qe3 Nxc2+ 7. -&gt; Kd1  
  -> 10775 (r 0.55): h6 9.Nbd2 Na5 10.b4 Nxc4 11.bxc5 -&gt; Nxd2
- **5253 -> 10775** (chess-pgn-1000-1300 +16.5%, chess-pgn-2400plus +19.1%)  
  5253 (r 0.51): Nc6 4.Nc3 Bg4 5.Nxe5 Bxd1 6.Bxf7+ -&gt; Ke7  
  -> 10775 (r 0.55): h6 9.Nbd2 Na5 10.b4 Nxc4 11.bxc5 -&gt; Nxd2
- **12041 -> 10775** (chess-pgn-1000-1300 +20.0%, chess-pgn-2400plus +21.9%)  
  12041 (r 0.53): Qd7 9.h3 Bh5 10.Bxc6 Qxc6 11.Nxe5 -&gt; Bxd1  
  -> 10775 (r 0.55): h6 9.Nbd2 Na5 10.b4 Nxc4 11.bxc5 -&gt; Nxd2
- **12701 -> 10775** (chess-pgn-1000-1300 +14.4%, chess-pgn-2400plus +10.9%)  
  12701 (r 0.53): Nxd4 15.Qxd4 f6 16.f4 Nf3+ 17. -&gt; Kd1  
  -> 10775 (r 0.55): h6 9.Nbd2 Na5 10.b4 Nxc4 11.bxc5 -&gt; Nxd2
- **13991 -> 13402** (chess-pgn-1000-1300 +43.7%, chess-pgn-2400plus +33.2%)  
  13991 (r 0.54): Qb6 12.a4 a6 13.a5 Qc6 14.Na7+ -&gt; Kb8  
  -> 13402 (r 0.60): Rfe8 16.f3 a5 17.Bc4 d5 18.Bxc7 -&gt; dxc4
- **13118 -> 13402** (chess-pgn-1000-1300 +58.1%, chess-pgn-2400plus +55.5%)  
  13118 (r 0.42): Qb7 17.Nf5 Be5 18.Qg4 Bxa1 19.Qxg7+ -&gt; Bxg7  
  -> 13402 (r 0.60): Rfe8 16.f3 a5 17.Bc4 d5 18.Bxc7 -&gt; dxc4

### chess-pgn-1000-1300 mode 1: 3.7% of the matrix

- **5247 -> 11713** (chess-pgn-1000-1300 +18.5%, chess-pgn-2400plus +18.9%)  
  5247 (r 0.58): Nf6 6.O-O g5 7.h3 g4 8. -&gt; hxg4  
  -> 11713 (r 0.49): g5 9.Nc4 g4 10.h3 h5 11.hxg4 -&gt; fxg4
- **5247 -> 9048** (chess-pgn-1000-1300 -1.5%, chess-pgn-2400plus -0.9%)  
  5247 (r 0.58): Nf6 6.O-O g5 7.h3 g4 8. -&gt; hxg4  
  -> 9048 (r 0.54): e6 6.c5 Nbd7 7.b4 axb4 8. -&gt; axb4
- **4769 -> 11713** (chess-pgn-1000-1300 -0.6%, chess-pgn-2400plus -0.7%)  
  4769 (r 0.57): Bc5 4.a3 a5 5.b4 axb4 6. -&gt; Nd5  
  -> 11713 (r 0.49): g5 9.Nc4 g4 10.h3 h5 11.hxg4 -&gt; fxg4
- **4769 -> 9048** (chess-pgn-1000-1300 +41.3%, chess-pgn-2400plus +36.0%)  
  4769 (r 0.57): Bc5 4.a3 a5 5.b4 axb4 6. -&gt; Nd5  
  -> 9048 (r 0.54): e6 6.c5 Nbd7 7.b4 axb4 8. -&gt; axb4
- **1969 -> 11713** (chess-pgn-1000-1300 -1.2%, chess-pgn-2400plus -1.6%)  
  1969 (r 0.59): Nc6 5.a3 a6 6.b4 Ba7 7.b5 -&gt; axb5  
  -> 11713 (r 0.49): g5 9.Nc4 g4 10.h3 h5 11.hxg4 -&gt; fxg4
- **1969 -> 9048** (chess-pgn-1000-1300 +37.3%, chess-pgn-2400plus +31.8%)  
  1969 (r 0.59): Nc6 5.a3 a6 6.b4 Ba7 7.b5 -&gt; axb5  
  -> 9048 (r 0.54): e6 6.c5 Nbd7 7.b4 axb4 8. -&gt; axb4
- **12970 -> 11713** (chess-pgn-1000-1300 +14.0%, chess-pgn-2400plus +13.7%)  
  12970 (r 0.61): Nxe3 13.fxe3 h6 14.g4 c5 15.g5 -&gt; Bxg5  
  -> 11713 (r 0.49): g5 9.Nc4 g4 10.h3 h5 11.hxg4 -&gt; fxg4
- **12970 -> 9048** (chess-pgn-1000-1300 -1.6%, chess-pgn-2400plus -2.0%)  
  12970 (r 0.61): Nxe3 13.fxe3 h6 14.g4 c5 15.g5 -&gt; Bxg5  
  -> 9048 (r 0.54): e6 6.c5 Nbd7 7.b4 axb4 8. -&gt; axb4

### chess-pgn-1000-1300 mode 2: 2.9% of the matrix

- **16341 -> 11434** (chess-pgn-1000-1300 +49.7%, chess-pgn-2400plus +44.4%)  
  16341 (r 0.55): Qg4 19.Nb1 Qf3 20.Rg1 Qxf2+ 21. -&gt; Kd1  
  -> 11434 (r 0.45): Ke6 19.Qxc8+ Nd7 20.Qxa8 Qxc2 21. -&gt; Qe8#
- **2450 -> 11434** (chess-pgn-1000-1300 -17.5%, chess-pgn-2400plus -19.9%)  
  2450 (r 0.50): Kb6 21.Qe6+ Ka5 22.Qe5+ Qxe5 23. -&gt; dxe5  
  -> 11434 (r 0.45): Ke6 19.Qxc8+ Nd7 20.Qxa8 Qxc2 21. -&gt; Qe8#
- **5988 -> 11434** (chess-pgn-1000-1300 -19.5%, chess-pgn-2400plus -18.6%)  
  5988 (r 0.46): Kh7 23.Qd2 g6 24.Qg2 Qxg2+ 25. -&gt; Kxg2  
  -> 11434 (r 0.45): Ke6 19.Qxc8+ Nd7 20.Qxa8 Qxc2 21. -&gt; Qe8#
- **1337 -> 11434** (chess-pgn-1000-1300 -5.4%, chess-pgn-2400plus -5.4%)  
  1337 (r 0.60): Bxc3+ 7.bxc3 Bg4 8.c4 Qxd4 9.Nxd4 -&gt; exd4  
  -> 11434 (r 0.45): Ke6 19.Qxc8+ Nd7 20.Qxa8 Qxc2 21. -&gt; Qe8#
- **9849 -> 11434** (chess-pgn-1000-1300 +48.2%, chess-pgn-2400plus +42.6%)  
  9849 (r 0.52): Kg8 23.Bb3 Rg5 24.Nxg5 Qxf2+ 25. -&gt; Kh1  
  -> 11434 (r 0.45): Ke6 19.Qxc8+ Nd7 20.Qxa8 Qxc2 21. -&gt; Qe8#
- **6677 -> 11434** (chess-pgn-1000-1300 +32.7%, chess-pgn-2400plus +29.0%)  
  6677 (r 0.39): Bxg5 14.Bxg5 Qf8+ 15.Kg1 Qf2+ 16.Kh1 -&gt; Qf1#  
  -> 11434 (r 0.45): Ke6 19.Qxc8+ Nd7 20.Qxa8 Qxc2 21. -&gt; Qe8#
- **7965 -> 11434** (chess-pgn-1000-1300 +24.7%, chess-pgn-2400plus +26.5%)  
  7965 (r 0.57): Bd7 9.Nc3 O-O-O 10.Qxa7 c6 11.Qa8+ -&gt; Kc7  
  -> 11434 (r 0.45): Ke6 19.Qxc8+ Nd7 20.Qxa8 Qxc2 21. -&gt; Qe8#
- **15804 -> 11434** (chess-pgn-1000-1300 +35.7%, chess-pgn-2400plus +32.1%)  
  15804 (r 0.55): Bg4 7.Qb3 Qd7 8.Qxb7 Qc6 9.Qc8+ -&gt; Ke7  
  -> 11434 (r 0.45): Ke6 19.Qxc8+ Nd7 20.Qxa8 Qxc2 21. -&gt; Qe8#

### chess-pgn-1000-1300 mode 3: 2.7% of the matrix

- **6153 -> 9802** (chess-pgn-1000-1300 -8.0%, chess-pgn-2400plus +1.2%)  
  6153 (r 0.58): Nf6 4.Nb5 e5 5.dxe5 Nh5 6. -&gt; e3  
  -> 9802 (r 0.55): Rd1 46.d8=Q Rxd8 47.Qxf6+ Kxf6 48.Kg3 -&gt; Rd2
- **1956 -> 9802** (chess-pgn-1000-1300 -5.2%, chess-pgn-2400plus +0.9%)  
  1956 (r 0.62): d5 5.exd5 Na5 6.Bb5+ c6 7. -&gt; dxc6  
  -> 9802 (r 0.55): Rd1 46.d8=Q Rxd8 47.Qxf6+ Kxf6 48.Kg3 -&gt; Rd2
- **1969 -> 16185** (chess-pgn-1000-1300 +6.0%, chess-pgn-2400plus +9.8%)  
  1969 (r 0.59): Nc6 5.a3 a6 6.b4 Ba7 7.b5 -&gt; axb5  
  -> 16185 (r 0.52): Bb7 19.Bxf6 Bxf6 20.Bd5 Qc7 21.Bxb7 -&gt; Qxb7
- **1969 -> 9802** (chess-pgn-1000-1300 -0.8%, chess-pgn-2400plus -0.6%)  
  1969 (r 0.59): Nc6 5.a3 a6 6.b4 Ba7 7.b5 -&gt; axb5  
  -> 9802 (r 0.55): Rd1 46.d8=Q Rxd8 47.Qxf6+ Kxf6 48.Kg3 -&gt; Rd2
- **1956 -> 12785** (chess-pgn-1000-1300 -0.8%, chess-pgn-2400plus +3.6%)  
  1956 (r 0.62): d5 5.exd5 Na5 6.Bb5+ c6 7. -&gt; dxc6  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **8093 -> 9802** (chess-pgn-1000-1300 -6.2%, chess-pgn-2400plus +1.3%)  
  8093 (r 0.62): cxd4 4.Nxd4 Nf6 5.Nc3 e5 6. -&gt; Ndb5  
  -> 9802 (r 0.55): Rd1 46.d8=Q Rxd8 47.Qxf6+ Kxf6 48.Kg3 -&gt; Rd2
- **4923 -> 16185** (chess-pgn-1000-1300 +6.8%, chess-pgn-2400plus +8.4%)  
  4923 (r 0.53): Bc5 8.a3 d4 9.Na2 a5 10.b4 -&gt; axb4  
  -> 16185 (r 0.52): Bb7 19.Bxf6 Bxf6 20.Bd5 Qc7 21.Bxb7 -&gt; Qxb7
- **1969 -> 12785** (chess-pgn-1000-1300 -1.2%, chess-pgn-2400plus -1.3%)  
  1969 (r 0.59): Nc6 5.a3 a6 6.b4 Ba7 7.b5 -&gt; axb5  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8

### chess-pgn-1000-1300 mode 4: 2.0% of the matrix

- **4945 -> 9048** (chess-pgn-1000-1300 +44.8%, chess-pgn-2400plus +32.3%)  
  4945 (r 0.50): b5 4.Nc3 c6 5.a4 Bd7 6. -&gt; axb5  
  -> 9048 (r 0.54): e6 6.c5 Nbd7 7.b4 axb4 8. -&gt; axb4
- **1969 -> 9048** (chess-pgn-1000-1300 +37.3%, chess-pgn-2400plus +31.8%)  
  1969 (r 0.59): Nc6 5.a3 a6 6.b4 Ba7 7.b5 -&gt; axb5  
  -> 9048 (r 0.54): e6 6.c5 Nbd7 7.b4 axb4 8. -&gt; axb4
- **9697 -> 9048** (chess-pgn-1000-1300 +43.1%, chess-pgn-2400plus +37.1%)  
  9697 (r 0.58): Nf6 6.a3 Nc6 7.b4 cxb4 8. -&gt; axb4  
  -> 9048 (r 0.54): e6 6.c5 Nbd7 7.b4 axb4 8. -&gt; axb4
- **4945 -> 663** (chess-pgn-1000-1300 +44.0%, chess-pgn-2400plus +26.1%)  
  4945 (r 0.50): b5 4.Nc3 c6 5.a4 Bd7 6. -&gt; axb5  
  -> 663 (r 0.47): Bh5 13.Ndf3 Nb3 14.Rb1 Nxc1 15.Rxc1 -&gt; Rxa2
- **1969 -> 663** (chess-pgn-1000-1300 +36.6%, chess-pgn-2400plus +29.2%)  
  1969 (r 0.59): Nc6 5.a3 a6 6.b4 Ba7 7.b5 -&gt; axb5  
  -> 663 (r 0.47): Bh5 13.Ndf3 Nb3 14.Rb1 Nxc1 15.Rxc1 -&gt; Rxa2
- **10107 -> 9048** (chess-pgn-1000-1300 +45.9%, chess-pgn-2400plus +40.0%)  
  10107 (r 0.52): Bb7 11.Ng3 Bc6 12.c3 b5 13.axb5 -&gt; axb5  
  -> 9048 (r 0.54): e6 6.c5 Nbd7 7.b4 axb4 8. -&gt; axb4
- **8780 -> 9048** (chess-pgn-1000-1300 +29.1%, chess-pgn-2400plus +26.8%)  
  8780 (r 0.48): c4 8.Ne5 Bd7 9.Bg3 b5 10. -&gt; axb5  
  -> 9048 (r 0.54): e6 6.c5 Nbd7 7.b4 axb4 8. -&gt; axb4
- **6153 -> 2038** (chess-pgn-1000-1300 +4.4%, chess-pgn-2400plus +1.7%)  
  6153 (r 0.58): Nf6 4.Nb5 e5 5.dxe5 Nh5 6. -&gt; e3  
  -> 2038 (r 0.51): f3 13.gxf3 Qh4+ 14.Kd2 gxf3 15.Nxf3 -&gt; Qf2

### chess-pgn-1000-1300 mode 5: 1.7% of the matrix

- **8093 -> 14097** (chess-pgn-1000-1300 -2.0%, chess-pgn-2400plus +2.5%)  
  8093 (r 0.62): cxd4 4.Nxd4 Nf6 5.Nc3 e5 6. -&gt; Ndb5  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **6153 -> 4983** (chess-pgn-1000-1300 +19.2%, chess-pgn-2400plus +8.8%)  
  6153 (r 0.58): Nf6 4.Nb5 e5 5.dxe5 Nh5 6. -&gt; e3  
  -> 4983 (r 0.52): b5 33.Qe4 Qg5 34.Qa8+ Kc7 35. -&gt; Qxa7+
- **1956 -> 14097** (chess-pgn-1000-1300 -0.4%, chess-pgn-2400plus +1.3%)  
  1956 (r 0.62): d5 5.exd5 Na5 6.Bb5+ c6 7. -&gt; dxc6  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **8093 -> 4983** (chess-pgn-1000-1300 +16.8%, chess-pgn-2400plus +17.0%)  
  8093 (r 0.62): cxd4 4.Nxd4 Nf6 5.Nc3 e5 6. -&gt; Ndb5  
  -> 4983 (r 0.52): b5 33.Qe4 Qg5 34.Qa8+ Kc7 35. -&gt; Qxa7+
- **5347 -> 14097** (chess-pgn-1000-1300 -1.0%, chess-pgn-2400plus +0.0%)  
  5347 (r 0.55): d6 4.O-O Be7 5.c3 Nf6 6. -&gt; d3  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **5526 -> 14097** (chess-pgn-1000-1300 -2.8%, chess-pgn-2400plus -0.9%)  
  5526 (r 0.68): Nc6 7.exd5 Qxd5 8.Na3 e6 9. -&gt; Nb5  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **6153 -> 2038** (chess-pgn-1000-1300 +4.4%, chess-pgn-2400plus +1.7%)  
  6153 (r 0.58): Nf6 4.Nb5 e5 5.dxe5 Nh5 6. -&gt; e3  
  -> 2038 (r 0.51): f3 13.gxf3 Qh4+ 14.Kd2 gxf3 15.Nxf3 -&gt; Qf2
- **1956 -> 4983** (chess-pgn-1000-1300 +11.0%, chess-pgn-2400plus +6.4%)  
  1956 (r 0.62): d5 5.exd5 Na5 6.Bb5+ c6 7. -&gt; dxc6  
  -> 4983 (r 0.52): b5 33.Qe4 Qg5 34.Qa8+ Kc7 35. -&gt; Qxa7+

### chess-pgn-1000-1300 mode 6: 1.6% of the matrix

- **6153 -> 2954** (chess-pgn-1000-1300 -1.9%, chess-pgn-2400plus -2.6%)  
  6153 (r 0.58): Nf6 4.Nb5 e5 5.dxe5 Nh5 6. -&gt; e3  
  -> 2954 (r 0.48): Qc5 10.d4 Qb6 11.Bxc6+ Qxc6 12. -&gt; Qb4
- **6153 -> 5615** (chess-pgn-1000-1300 +6.1%, chess-pgn-2400plus +4.7%)  
  6153 (r 0.58): Nf6 4.Nb5 e5 5.dxe5 Nh5 6. -&gt; e3  
  -> 5615 (r 0.47): Rh6 4.Nf3 Rg6 5.Nh4 Rg4 6.hxg4 -&gt; hxg4
- **6153 -> 6441** (chess-pgn-1000-1300 -1.7%, chess-pgn-2400plus -1.5%)  
  6153 (r 0.58): Nf6 4.Nb5 e5 5.dxe5 Nh5 6. -&gt; e3  
  -> 6441 (r 0.47): Qc8 13.Na3 Bf5 14.c4 Bxd3 15.Qxd3 -&gt; Qf5
- **1956 -> 2954** (chess-pgn-1000-1300 -2.7%, chess-pgn-2400plus +1.3%)  
  1956 (r 0.62): d5 5.exd5 Na5 6.Bb5+ c6 7. -&gt; dxc6  
  -> 2954 (r 0.48): Qc5 10.d4 Qb6 11.Bxc6+ Qxc6 12. -&gt; Qb4
- **15738 -> 2954** (chess-pgn-1000-1300 -0.8%, chess-pgn-2400plus -0.1%)  
  15738 (r 0.62): Bc5 5.Ng5 Ne5 6.Bb3 h6 7. -&gt; Nf3  
  -> 2954 (r 0.48): Qc5 10.d4 Qb6 11.Bxc6+ Qxc6 12. -&gt; Qb4
- **8093 -> 5615** (chess-pgn-1000-1300 +6.8%, chess-pgn-2400plus +4.6%)  
  8093 (r 0.62): cxd4 4.Nxd4 Nf6 5.Nc3 e5 6. -&gt; Ndb5  
  -> 5615 (r 0.47): Rh6 4.Nf3 Rg6 5.Nh4 Rg4 6.hxg4 -&gt; hxg4
- **5347 -> 2954** (chess-pgn-1000-1300 -2.2%, chess-pgn-2400plus -2.6%)  
  5347 (r 0.55): d6 4.O-O Be7 5.c3 Nf6 6. -&gt; d3  
  -> 2954 (r 0.48): Qc5 10.d4 Qb6 11.Bxc6+ Qxc6 12. -&gt; Qb4
- **5669 -> 2954** (chess-pgn-1000-1300 -1.7%, chess-pgn-2400plus -0.7%)  
  5669 (r 0.53): Bc5 4.Nf3 Ng4 5.d4 exd4 6. -&gt; Nd5  
  -> 2954 (r 0.48): Qc5 10.d4 Qb6 11.Bxc6+ Qxc6 12. -&gt; Qb4

### chess-pgn-1000-1300 mode 7: 1.5% of the matrix

- **1254 -> 14097** (chess-pgn-1000-1300 +53.6%, chess-pgn-2400plus +49.4%)  
  1254 (r 0.64): Nb4 5.Qc4 b5 6.Qxb5 Nxc2+ 7. -&gt; Kd2  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **2205 -> 14097** (chess-pgn-1000-1300 +51.1%, chess-pgn-2400plus +47.8%)  
  2205 (r 0.58): Nge7 9.d4 exd4 10.Bf4 Qg6 11.Nxc7+ -&gt; Kf8  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **8827 -> 14097** (chess-pgn-1000-1300 +48.8%, chess-pgn-2400plus +44.2%)  
  8827 (r 0.60): O-O 9.a3 Nd4 10.Qg3 Nxc2+ 11. -&gt; Kf1  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **8859 -> 14097** (chess-pgn-1000-1300 +56.3%, chess-pgn-2400plus +48.9%)  
  8859 (r 0.57): e6 5.Qe2 Nxd4 6.Qe3 Nxc2+ 7. -&gt; Kd1  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **15026 -> 14097** (chess-pgn-1000-1300 +50.9%, chess-pgn-2400plus +46.5%)  
  15026 (r 0.59): Bb4 4.Qg4 Nd4 5.Qxg7 Nxc2+ 6. -&gt; Kd1  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **1254 -> 6774** (chess-pgn-1000-1300 -1.1%, chess-pgn-2400plus -0.9%)  
  1254 (r 0.64): Nb4 5.Qc4 b5 6.Qxb5 Nxc2+ 7. -&gt; Kd2  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4
- **14002 -> 14097** (chess-pgn-1000-1300 +48.0%, chess-pgn-2400plus +43.2%)  
  14002 (r 0.56): Nxd4 6.Nxf7 Qf6 7.Qxg4 Nxc2+ 8. -&gt; Kf1  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **3578 -> 14097** (chess-pgn-1000-1300 +48.7%, chess-pgn-2400plus +44.7%)  
  3578 (r 0.59): Nc6 7.f4 Nb4 8.c3 Nc2+ 9. -&gt; Kd1  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+

### chess-pgn-1000-1300 mode 8: 1.3% of the matrix

- **5526 -> 10215** (chess-pgn-1000-1300 +1.9%, chess-pgn-2400plus +6.0%)  
  5526 (r 0.68): Nc6 7.exd5 Qxd5 8.Na3 e6 9. -&gt; Nb5  
  -> 10215 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **9579 -> 10215** (chess-pgn-1000-1300 +5.6%, chess-pgn-2400plus +5.1%)  
  9579 (r 0.55): Nf6 4.e4 e5 5.d5 Bb4 6.Qa4+ -&gt; Qd7  
  -> 10215 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **10038 -> 10215** (chess-pgn-1000-1300 +5.0%, chess-pgn-2400plus +8.3%)  
  10038 (r 0.51): c5 4.c3 Nc6 5.Nf3 Qb6 6.dxc5 -&gt; Bxc5  
  -> 10215 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **11620 -> 12785** (chess-pgn-1000-1300 +9.2%, chess-pgn-2400plus +11.0%)  
  11620 (r 0.62): dxe4 4.Nxe5 Bd6 5.Bc4 Bxe5 6.dxe5 -&gt; Qxd1+  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **7585 -> 10215** (chess-pgn-1000-1300 +0.2%, chess-pgn-2400plus +4.9%)  
  7585 (r 0.63): Ne4 5.Bd3 Qh4+ 6.g3 Nxg3 7. -&gt; Nd2  
  -> 10215 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **609 -> 10215** (chess-pgn-1000-1300 +0.9%, chess-pgn-2400plus +2.7%)  
  609 (r 0.64): Bc5 5.Bxc6 dxc6 6.Nxe5 Qd4 7. -&gt; Ng4  
  -> 10215 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **5526 -> 13196** (chess-pgn-1000-1300 +0.3%, chess-pgn-2400plus +6.4%)  
  5526 (r 0.68): Nc6 7.exd5 Qxd5 8.Na3 e6 9. -&gt; Nb5  
  -> 13196 (r 0.53): Ng4 25.Qd2 Ne5 26.Qe2 Ng6 27. -&gt; Re1
- **11540 -> 10215** (chess-pgn-1000-1300 +0.8%, chess-pgn-2400plus +1.9%)  
  11540 (r 0.51): Qh2+ 25.Kf2 Rxf3+ 26.Qxf3 Bg3+ 27.Qxg3 -&gt; Rf8+  
  -> 10215 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5

### chess-pgn-1000-1300 mode 9: 1.3% of the matrix

- **2192 -> 2647** (chess-pgn-1000-1300 +9.8%, chess-pgn-2400plus +4.3%)  
  2192 (r 0.46): h6 9.Qe2 d6 10.Be3 Nd4 11. -&gt; Qd1  
  -> 2647 (r 0.50): Nc6 5.c3 d5 6.exd5 Nxd5 7. -&gt; d3
- **2192 -> 5657** (chess-pgn-1000-1300 -0.8%, chess-pgn-2400plus -0.6%)  
  2192 (r 0.46): h6 9.Qe2 d6 10.Be3 Nd4 11. -&gt; Qd1  
  -> 5657 (r 0.50): f5 11.Bxe4 dxe4 12.d5 exf3 13. -&gt; Nxf3
- **7691 -> 2647** (chess-pgn-1000-1300 +5.2%, chess-pgn-2400plus +4.9%)  
  7691 (r 0.63): e5 11.d5 c6 12.O-O cxd5 13.Nxd5 -&gt; Nxd5  
  -> 2647 (r 0.50): Nc6 5.c3 d5 6.exd5 Nxd5 7. -&gt; d3
- **2192 -> 7114** (chess-pgn-1000-1300 -1.2%, chess-pgn-2400plus -1.5%)  
  2192 (r 0.46): h6 9.Qe2 d6 10.Be3 Nd4 11. -&gt; Qd1  
  -> 7114 (r 0.54): d5 5.exd5 Na5 6.Bd3 e4 7.Nxe4 -&gt; Nxd5
- **7592 -> 2647** (chess-pgn-1000-1300 +11.7%, chess-pgn-2400plus +5.6%)  
  7592 (r 0.56): d6 6.O-O Bg4 7.Be3 Nd4 8.Bxd4 -&gt; exd4  
  -> 2647 (r 0.50): Nc6 5.c3 d5 6.exd5 Nxd5 7. -&gt; d3
- **1325 -> 2647** (chess-pgn-1000-1300 +4.6%, chess-pgn-2400plus +3.8%)  
  1325 (r 0.51): Nc6 15.Qb3 Qxb3 16.Nxb3 Nd4 17. -&gt; Nbxd4  
  -> 2647 (r 0.50): Nc6 5.c3 d5 6.exd5 Nxd5 7. -&gt; d3
- **12814 -> 2647** (chess-pgn-1000-1300 +23.5%, chess-pgn-2400plus +14.8%)  
  12814 (r 0.54): Qc7 13.Qc3 b6 14.Rfd1 Nd4 15.Nxd4 -&gt; exd4  
  -> 2647 (r 0.50): Nc6 5.c3 d5 6.exd5 Nxd5 7. -&gt; d3
- **7691 -> 5657** (chess-pgn-1000-1300 -1.4%, chess-pgn-2400plus -1.1%)  
  7691 (r 0.63): e5 11.d5 c6 12.O-O cxd5 13.Nxd5 -&gt; Nxd5  
  -> 5657 (r 0.50): f5 11.Bxe4 dxe4 12.d5 exf3 13. -&gt; Nxf3

### chess-pgn-1000-1300 mode 10: 1.3% of the matrix

- **6153 -> 2038** (chess-pgn-1000-1300 +4.4%, chess-pgn-2400plus +1.7%)  
  6153 (r 0.58): Nf6 4.Nb5 e5 5.dxe5 Nh5 6. -&gt; e3  
  -> 2038 (r 0.51): f3 13.gxf3 Qh4+ 14.Kd2 gxf3 15.Nxf3 -&gt; Qf2
- **10248 -> 2038** (chess-pgn-1000-1300 +3.5%, chess-pgn-2400plus +2.2%)  
  10248 (r 0.63): Nf6 4.Nc3 Ng4 5.O-O Nxf2 6. -&gt; Qe2  
  -> 2038 (r 0.51): f3 13.gxf3 Qh4+ 14.Kd2 gxf3 15.Nxf3 -&gt; Qf2
- **1654 -> 12785** (chess-pgn-1000-1300 +52.0%, chess-pgn-2400plus +62.5%)  
  1654 (r 0.55): cxd5 5.Qb3 Bc8 6.Qxd5 Qxd5 7. -&gt; Nxd5  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **8093 -> 2038** (chess-pgn-1000-1300 +5.6%, chess-pgn-2400plus +5.4%)  
  8093 (r 0.62): cxd4 4.Nxd4 Nf6 5.Nc3 e5 6. -&gt; Ndb5  
  -> 2038 (r 0.51): f3 13.gxf3 Qh4+ 14.Kd2 gxf3 15.Nxf3 -&gt; Qf2
- **1956 -> 12785** (chess-pgn-1000-1300 -0.8%, chess-pgn-2400plus +3.6%)  
  1956 (r 0.62): d5 5.exd5 Na5 6.Bb5+ c6 7. -&gt; dxc6  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **10248 -> 2954** (chess-pgn-1000-1300 +5.5%, chess-pgn-2400plus +9.8%)  
  10248 (r 0.63): Nf6 4.Nc3 Ng4 5.O-O Nxf2 6. -&gt; Qe2  
  -> 2954 (r 0.48): Qc5 10.d4 Qb6 11.Bxc6+ Qxc6 12. -&gt; Qb4
- **1654 -> 2038** (chess-pgn-1000-1300 -1.6%, chess-pgn-2400plus -1.4%)  
  1654 (r 0.55): cxd5 5.Qb3 Bc8 6.Qxd5 Qxd5 7. -&gt; Nxd5  
  -> 2038 (r 0.51): f3 13.gxf3 Qh4+ 14.Kd2 gxf3 15.Nxf3 -&gt; Qf2
- **6153 -> 12506** (chess-pgn-1000-1300 -3.4%, chess-pgn-2400plus -1.4%)  
  6153 (r 0.58): Nf6 4.Nb5 e5 5.dxe5 Nh5 6. -&gt; e3  
  -> 12506 (r 0.39): Nxg3 13.fxg3 O-O-O 14.a4 Nb6 15.a5 -&gt; Na8

### chess-pgn-1000-1300 mode 11: 1.2% of the matrix

- **1980 -> 16081** (chess-pgn-1000-1300 +67.1%, chess-pgn-2400plus +61.4%)  
  1980 (r 0.57): dxc4 4.Bxc4 e6 5.Ne2 Bb4+ 6. -&gt; Bd2  
  -> 16081 (r 0.51): Nc6 6.Bb5 dxe5 7.Qxd8+ Kxd8 8. -&gt; Bxc6
- **11095 -> 16081** (chess-pgn-1000-1300 +71.0%, chess-pgn-2400plus +68.0%)  
  11095 (r 0.44): e5 6.Nfd2 Nf6 7.Be2 Nc6 8.Bb5 -&gt; Bd7  
  -> 16081 (r 0.51): Nc6 6.Bb5 dxe5 7.Qxd8+ Kxd8 8. -&gt; Bxc6
- **6247 -> 16081** (chess-pgn-1000-1300 +48.7%, chess-pgn-2400plus +46.9%)  
  6247 (r 0.59): Nc6 5.Nf3 cxd4 6.cxd4 Bb4+ 7. -&gt; Nc3  
  -> 16081 (r 0.51): Nc6 6.Bb5 dxe5 7.Qxd8+ Kxd8 8. -&gt; Bxc6
- **9561 -> 16081** (chess-pgn-1000-1300 +65.4%, chess-pgn-2400plus +63.7%)  
  9561 (r 0.58): Nc6 6.c3 Nxd4 7.cxd4 Bb4+ 8. -&gt; Nc3  
  -> 16081 (r 0.51): Nc6 6.Bb5 dxe5 7.Qxd8+ Kxd8 8. -&gt; Bxc6
- **2818 -> 16081** (chess-pgn-1000-1300 +62.6%, chess-pgn-2400plus +59.7%)  
  2818 (r 0.52): Nge7 7.f4 Nxd4 8.cxd4 Bb4+ 9. -&gt; Nc3  
  -> 16081 (r 0.51): Nc6 6.Bb5 dxe5 7.Qxd8+ Kxd8 8. -&gt; Bxc6
- **1465 -> 16081** (chess-pgn-1000-1300 +49.3%, chess-pgn-2400plus +43.8%)  
  1465 (r 0.66): cxd4 4.Nxd4 Nc6 5.Nc3 Nf6 6.Bb5 -&gt; g6  
  -> 16081 (r 0.51): Nc6 6.Bb5 dxe5 7.Qxd8+ Kxd8 8. -&gt; Bxc6
- **8903 -> 16081** (chess-pgn-1000-1300 +54.1%, chess-pgn-2400plus +51.2%)  
  8903 (r 0.59): Ng4 4.Bf4 Nc6 5.Nf3 Bb4+ 6. -&gt; Nc3  
  -> 16081 (r 0.51): Nc6 6.Bb5 dxe5 7.Qxd8+ Kxd8 8. -&gt; Bxc6
- **6519 -> 16081** (chess-pgn-1000-1300 +52.3%, chess-pgn-2400plus +48.8%)  
  6519 (r 0.54): Nxe4 4.Bg2 d5 5.d3 Bb4+ 6. -&gt; Bd2  
  -> 16081 (r 0.51): Nc6 6.Bb5 dxe5 7.Qxd8+ Kxd8 8. -&gt; Bxc6

### chess-pgn-1000-1300 mode 12: 1.1% of the matrix

- **1 -> 6774** (chess-pgn-1000-1300 +68.1%, chess-pgn-2400plus +66.0%)  
  1 (r 0.43): Nf6 5.O-O d6 6.Nc3 a5 7.Bg5 -&gt; h6  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4
- **16210 -> 6774** (chess-pgn-1000-1300 +62.1%, chess-pgn-2400plus +57.3%)  
  16210 (r 0.58): O-O 11.Nxf6+ Qxf6 12.O-O Bg4 13. -&gt; Be2  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4
- **8591 -> 6774** (chess-pgn-1000-1300 +54.6%, chess-pgn-2400plus +52.1%)  
  8591 (r 0.52): Qxd5 5.dxe5 Qxd1+ 6.Kxd1 Bg4 7. -&gt; Be2  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4
- **8683 -> 6774** (chess-pgn-1000-1300 +62.4%, chess-pgn-2400plus +63.7%)  
  8683 (r 0.55): exd5 4.Nf3 Nc6 5.h3 Bd6 6.Bg5 -&gt; Nge7  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4
- **10700 -> 6774** (chess-pgn-1000-1300 +46.8%, chess-pgn-2400plus +46.4%)  
  10700 (r 0.60): Nc6 6.Qd1 Nxe5 7.Nf3 Bg4 8. -&gt; Nbd2  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4
- **3302 -> 6774** (chess-pgn-1000-1300 +51.0%, chess-pgn-2400plus +41.8%)  
  3302 (r 0.69): g6 4.Bc4 e6 5.d4 Nf6 6.Bg5 -&gt; Ng4  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4
- **10673 -> 6774** (chess-pgn-1000-1300 +65.9%, chess-pgn-2400plus +67.5%)  
  10673 (r 0.51): O-O 8.O-O Nc6 9.Bb3 Bg4 10. -&gt; f3  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4
- **6170 -> 6774** (chess-pgn-1000-1300 +24.1%, chess-pgn-2400plus +22.8%)  
  6170 (r 0.54): d6 6.O-O Bg4 7.h3 Bh5 8.Bg5 -&gt; f6  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4

### chess-pgn-1000-1300 mode 13: 1.1% of the matrix

- **11579 -> 12785** (chess-pgn-1000-1300 -1.2%, chess-pgn-2400plus -0.8%)  
  11579 (r 0.57): Bf5 7.Ne4 Qe5 8.Nf3 Qxb2 9. -&gt; Bc3  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **5669 -> 12785** (chess-pgn-1000-1300 -0.9%, chess-pgn-2400plus -0.2%)  
  5669 (r 0.53): Bc5 4.Nf3 Ng4 5.d4 exd4 6. -&gt; Nd5  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **15626 -> 12785** (chess-pgn-1000-1300 +48.4%, chess-pgn-2400plus +41.6%)  
  15626 (r 0.54): exd4 4.Nxd4 Qh4 5.Nxc6 Qxe4+ 6.Qe2 -&gt; Qxe2+  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **10369 -> 12785** (chess-pgn-1000-1300 -1.1%, chess-pgn-2400plus -0.3%)  
  10369 (r 0.59): Qe7 5.Nf3 d6 6.O-O Be6 7.Qxb7 -&gt; Bxc4  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **11702 -> 12785** (chess-pgn-1000-1300 -0.9%, chess-pgn-2400plus -0.5%)  
  11702 (r 0.33): Bf5 8.Bd3 Bxd3 9.Qxd3 Qxb2 10.dxc5 -&gt; Qxa1  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **5194 -> 12785** (chess-pgn-1000-1300 -1.2%, chess-pgn-2400plus -1.1%)  
  5194 (r 0.64): dxc6 5.Bc4 Bc5 6.O-O Ng4 7. -&gt; d3  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **15542 -> 12785** (chess-pgn-1000-1300 -0.6%, chess-pgn-2400plus -0.3%)  
  15542 (r 0.46): Bc5 5.c4 Qb6 6.Be3 Qxb2 7. -&gt; Nb3  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **12018 -> 12785** (chess-pgn-1000-1300 -1.0%, chess-pgn-2400plus -0.5%)  
  12018 (r 0.59): Nc6 5.Nc3 Bf5 6.Qb3 e6 7.Qxb7 -&gt; Nb4  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8

### chess-pgn-1000-1300 mode 14: 1.0% of the matrix

- **6153 -> 2954** (chess-pgn-1000-1300 -1.9%, chess-pgn-2400plus -2.6%)  
  6153 (r 0.58): Nf6 4.Nb5 e5 5.dxe5 Nh5 6. -&gt; e3  
  -> 2954 (r 0.48): Qc5 10.d4 Qb6 11.Bxc6+ Qxc6 12. -&gt; Qb4
- **14381 -> 2954** (chess-pgn-1000-1300 -2.8%, chess-pgn-2400plus -1.4%)  
  14381 (r 0.56): Be6 9.Bc2 Qd7 10.O-O Bxh3 11. -&gt; gxh3  
  -> 2954 (r 0.48): Qc5 10.d4 Qb6 11.Bxc6+ Qxc6 12. -&gt; Qb4
- **14381 -> 6441** (chess-pgn-1000-1300 +42.3%, chess-pgn-2400plus +32.5%)  
  14381 (r 0.56): Be6 9.Bc2 Qd7 10.O-O Bxh3 11. -&gt; gxh3  
  -> 6441 (r 0.47): Qc8 13.Na3 Bf5 14.c4 Bxd3 15.Qxd3 -&gt; Qf5
- **11887 -> 2954** (chess-pgn-1000-1300 -1.5%, chess-pgn-2400plus +1.3%)  
  11887 (r 0.53): d6 5.h3 c6 6.Bb3 Bxh3 7. -&gt; Rxh3  
  -> 2954 (r 0.48): Qc5 10.d4 Qb6 11.Bxc6+ Qxc6 12. -&gt; Qb4
- **11887 -> 6441** (chess-pgn-1000-1300 +54.4%, chess-pgn-2400plus +38.0%)  
  11887 (r 0.53): d6 5.h3 c6 6.Bb3 Bxh3 7. -&gt; Rxh3  
  -> 6441 (r 0.47): Qc8 13.Na3 Bf5 14.c4 Bxd3 15.Qxd3 -&gt; Qf5
- **14793 -> 2954** (chess-pgn-1000-1300 -0.9%, chess-pgn-2400plus +0.5%)  
  14793 (r 0.56): Qd6 6.O-O Bg4 7.h3 Bxh3 8. -&gt; gxh3  
  -> 2954 (r 0.48): Qc5 10.d4 Qb6 11.Bxc6+ Qxc6 12. -&gt; Qb4
- **15113 -> 2954** (chess-pgn-1000-1300 +56.7%, chess-pgn-2400plus +46.2%)  
  15113 (r 0.57): Bc5 4.Nc3 Nf6 5.h3 Bxf2+ 6. -&gt; Kxf2  
  -> 2954 (r 0.48): Qc5 10.d4 Qb6 11.Bxc6+ Qxc6 12. -&gt; Qb4
- **11673 -> 2954** (chess-pgn-1000-1300 -1.5%, chess-pgn-2400plus -1.6%)  
  11673 (r 0.58): Ng8 4.Bb5 Bb7 5.d4 Bxg2 6. -&gt; Qh5  
  -> 2954 (r 0.48): Qc5 10.d4 Qb6 11.Bxc6+ Qxc6 12. -&gt; Qb4

## chess-pgn-2400plus

### chess-pgn-2400plus mode 0: 8.1% of the matrix

- **14428 -> 10775** (chess-pgn-1000-1300 +21.0%, chess-pgn-2400plus +17.6%)  
  14428 (r 0.52): Bd6 11.h3 Bh5 12.Ne5 Bxe2 13.Nxd7 -&gt; Bxd1  
  -> 10775 (r 0.55): h6 9.Nbd2 Na5 10.b4 Nxc4 11.bxc5 -&gt; Nxd2
- **13118 -> 10775** (chess-pgn-1000-1300 +9.9%, chess-pgn-2400plus +11.4%)  
  13118 (r 0.42): Qb7 17.Nf5 Be5 18.Qg4 Bxa1 19.Qxg7+ -&gt; Bxg7  
  -> 10775 (r 0.55): h6 9.Nbd2 Na5 10.b4 Nxc4 11.bxc5 -&gt; Nxd2
- **9779 -> 10775** (chess-pgn-1000-1300 +7.1%, chess-pgn-2400plus +6.7%)  
  9779 (r 0.51): Bf4 37.Bf3 Qg3 38.Bd4 Qf2+ 39. -&gt; Qxf2  
  -> 10775 (r 0.55): h6 9.Nbd2 Na5 10.b4 Nxc4 11.bxc5 -&gt; Nxd2
- **7907 -> 10775** (chess-pgn-1000-1300 +2.8%, chess-pgn-2400plus +3.2%)  
  7907 (r 0.43): Qa6 19.Ra5 Bxf3 20.Rxa6+ Kb8 21. -&gt; Qb5+  
  -> 10775 (r 0.55): h6 9.Nbd2 Na5 10.b4 Nxc4 11.bxc5 -&gt; Nxd2
- **12041 -> 10775** (chess-pgn-1000-1300 +20.0%, chess-pgn-2400plus +21.9%)  
  12041 (r 0.53): Qd7 9.h3 Bh5 10.Bxc6 Qxc6 11.Nxe5 -&gt; Bxd1  
  -> 10775 (r 0.55): h6 9.Nbd2 Na5 10.b4 Nxc4 11.bxc5 -&gt; Nxd2
- **13991 -> 10775** (chess-pgn-1000-1300 +17.1%, chess-pgn-2400plus +12.4%)  
  13991 (r 0.54): Qb6 12.a4 a6 13.a5 Qc6 14.Na7+ -&gt; Kb8  
  -> 10775 (r 0.55): h6 9.Nbd2 Na5 10.b4 Nxc4 11.bxc5 -&gt; Nxd2
- **14428 -> 5615** (chess-pgn-1000-1300 +4.7%, chess-pgn-2400plus +4.5%)  
  14428 (r 0.52): Bd6 11.h3 Bh5 12.Ne5 Bxe2 13.Nxd7 -&gt; Bxd1  
  -> 5615 (r 0.47): Rh6 4.Nf3 Rg6 5.Nh4 Rg4 6.hxg4 -&gt; hxg4
- **5253 -> 10775** (chess-pgn-1000-1300 +16.5%, chess-pgn-2400plus +19.1%)  
  5253 (r 0.51): Nc6 4.Nc3 Bg4 5.Nxe5 Bxd1 6.Bxf7+ -&gt; Ke7  
  -> 10775 (r 0.55): h6 9.Nbd2 Na5 10.b4 Nxc4 11.bxc5 -&gt; Nxd2

### chess-pgn-2400plus mode 1: 3.5% of the matrix

- **5806 -> 12785** (chess-pgn-1000-1300 +38.7%, chess-pgn-2400plus +43.6%)  
  5806 (r 0.48): c4 28.a4 c3 29.Rb5 Rxb5 30. -&gt; axb5  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **11405 -> 12785** (chess-pgn-1000-1300 +55.5%, chess-pgn-2400plus +61.8%)  
  11405 (r 0.52): Rxd1+ 24.Nxd1 fxe6 25.Nc3 Qc6 26.Qxc6 -&gt; Bxc6  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **2761 -> 12785** (chess-pgn-1000-1300 +58.1%, chess-pgn-2400plus +62.3%)  
  2761 (r 0.62): Qxe5 13.Rab1 Bd6 14.Bf4 Qxf4 15.Qxf4 -&gt; Bxf4  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **7133 -> 12785** (chess-pgn-1000-1300 +56.2%, chess-pgn-2400plus +72.4%)  
  7133 (r 0.57): c5 5.Nf3 Qb6 6.Qb3 Qxb3 7. -&gt; axb3  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **2335 -> 12785** (chess-pgn-1000-1300 +40.5%, chess-pgn-2400plus +52.6%)  
  2335 (r 0.47): Qxc5 14.Rc1 Qb6 15.Qb3 Qxb3 16. -&gt; axb3  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **2325 -> 12785** (chess-pgn-1000-1300 +67.7%, chess-pgn-2400plus +67.3%)  
  2325 (r 0.46): Nxe5 10.dxe5 Bxe5 11.Bf4 Qxd1 12. -&gt; Rfxd1  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **5167 -> 12785** (chess-pgn-1000-1300 +62.7%, chess-pgn-2400plus +66.8%)  
  5167 (r 0.50): Bxf6 15.Qg4 O-O 16.Qxe6+ Qxe6 17. -&gt; Rxe6  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **6248 -> 12785** (chess-pgn-1000-1300 +64.9%, chess-pgn-2400plus +67.1%)  
  6248 (r 0.53): Be7 8.Nxe4 dxe4 9.Bxe4 Qxd1 10. -&gt; Rxd1  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8

### chess-pgn-2400plus mode 2: 2.8% of the matrix

- **2450 -> 11434** (chess-pgn-1000-1300 -17.5%, chess-pgn-2400plus -19.9%)  
  2450 (r 0.50): Kb6 21.Qe6+ Ka5 22.Qe5+ Qxe5 23. -&gt; dxe5  
  -> 11434 (r 0.45): Ke6 19.Qxc8+ Nd7 20.Qxa8 Qxc2 21. -&gt; Qe8#
- **5988 -> 11434** (chess-pgn-1000-1300 -19.5%, chess-pgn-2400plus -18.6%)  
  5988 (r 0.46): Kh7 23.Qd2 g6 24.Qg2 Qxg2+ 25. -&gt; Kxg2  
  -> 11434 (r 0.45): Ke6 19.Qxc8+ Nd7 20.Qxa8 Qxc2 21. -&gt; Qe8#
- **16313 -> 11434** (chess-pgn-1000-1300 -12.6%, chess-pgn-2400plus -12.0%)  
  16313 (r 0.57): b5 24.Nf4 Nxf4 25.Qxf4 Qxf4 26. -&gt; gxf4  
  -> 11434 (r 0.45): Ke6 19.Qxc8+ Nd7 20.Qxa8 Qxc2 21. -&gt; Qe8#
- **14532 -> 11434** (chess-pgn-1000-1300 -7.2%, chess-pgn-2400plus -8.9%)  
  14532 (r 0.44): Bf5 7.Qf3 Bg6 8.Bxf6 Qxf6 9.Qxf6 -&gt; gxf6  
  -> 11434 (r 0.45): Ke6 19.Qxc8+ Nd7 20.Qxa8 Qxc2 21. -&gt; Qe8#
- **3967 -> 11434** (chess-pgn-1000-1300 -9.5%, chess-pgn-2400plus -11.0%)  
  3967 (r 0.49): Qf6 20.Bg5 Qe6 21.h3 Qxg4 22. -&gt; hxg4  
  -> 11434 (r 0.45): Ke6 19.Qxc8+ Nd7 20.Qxa8 Qxc2 21. -&gt; Qe8#
- **12415 -> 11434** (chess-pgn-1000-1300 -7.8%, chess-pgn-2400plus -8.2%)  
  12415 (r 0.44): Ng6 13.h4 gxh6 14.h5 Qg5 15.Qxg5 -&gt; hxg5  
  -> 11434 (r 0.45): Ke6 19.Qxc8+ Nd7 20.Qxa8 Qxc2 21. -&gt; Qe8#
- **14170 -> 11434** (chess-pgn-1000-1300 -10.6%, chess-pgn-2400plus -12.4%)  
  14170 (r 0.45): Qh4 20.b4 Qxh3 21.Qg3 Qxg3+ 22. -&gt; fxg3  
  -> 11434 (r 0.45): Ke6 19.Qxc8+ Nd7 20.Qxa8 Qxc2 21. -&gt; Qe8#
- **3570 -> 11434** (chess-pgn-1000-1300 -14.8%, chess-pgn-2400plus -16.0%)  
  3570 (r 0.48): Qxc4 26.Re4 Qd5 27.Rf4 Qxf3+ 28. -&gt; Rxf3  
  -> 11434 (r 0.45): Ke6 19.Qxc8+ Nd7 20.Qxa8 Qxc2 21. -&gt; Qe8#

### chess-pgn-2400plus mode 3: 2.6% of the matrix

- **16236 -> 7976** (chess-pgn-1000-1300 +21.5%, chess-pgn-2400plus +23.0%)  
  16236 (r 0.55): O-O-O 8.c4 Qd6 9.d4 e5 10.Nxe5 -&gt; Bxe2  
  -> 7976 (r 0.63): f5 23.exf5 e4+ 24.Qf4 Nxf5 25.Qxd6 -&gt; Nxd6
- **16236 -> 16185** (chess-pgn-1000-1300 +13.6%, chess-pgn-2400plus +19.2%)  
  16236 (r 0.55): O-O-O 8.c4 Qd6 9.d4 e5 10.Nxe5 -&gt; Bxe2  
  -> 16185 (r 0.52): Bb7 19.Bxf6 Bxf6 20.Bd5 Qc7 21.Bxb7 -&gt; Qxb7
- **8325 -> 7976** (chess-pgn-1000-1300 +15.1%, chess-pgn-2400plus +15.9%)  
  8325 (r 0.55): O-O 6.h3 Na5 7.Ba2 d6 8.b4 -&gt; Bxb4+  
  -> 7976 (r 0.63): f5 23.exf5 e4+ 24.Qf4 Nxf5 25.Qxd6 -&gt; Nxd6
- **7238 -> 7976** (chess-pgn-1000-1300 +22.1%, chess-pgn-2400plus +21.6%)  
  7238 (r 0.53): Be7 4.d4 exd4 5.Qxd4 Nf6 6.e5 -&gt; dxe5  
  -> 7976 (r 0.63): f5 23.exf5 e4+ 24.Qf4 Nxf5 25.Qxd6 -&gt; Nxd6
- **8325 -> 16185** (chess-pgn-1000-1300 +11.3%, chess-pgn-2400plus +8.8%)  
  8325 (r 0.55): O-O 6.h3 Na5 7.Ba2 d6 8.b4 -&gt; Bxb4+  
  -> 16185 (r 0.52): Bb7 19.Bxf6 Bxf6 20.Bd5 Qc7 21.Bxb7 -&gt; Qxb7
- **6962 -> 7976** (chess-pgn-1000-1300 +16.0%, chess-pgn-2400plus +14.2%)  
  6962 (r 0.57): Nc6 6.Bc4 a6 7.O-O d6 8.d5 -&gt; Bd7  
  -> 7976 (r 0.63): f5 23.exf5 e4+ 24.Qf4 Nxf5 25.Qxd6 -&gt; Nxd6
- **7238 -> 16185** (chess-pgn-1000-1300 +12.2%, chess-pgn-2400plus +14.0%)  
  7238 (r 0.53): Be7 4.d4 exd4 5.Qxd4 Nf6 6.e5 -&gt; dxe5  
  -> 16185 (r 0.52): Bb7 19.Bxf6 Bxf6 20.Bd5 Qc7 21.Bxb7 -&gt; Qxb7
- **7206 -> 7976** (chess-pgn-1000-1300 +17.3%, chess-pgn-2400plus +22.5%)  
  7206 (r 0.60): exf6 9.Be2 O-O-O 10.O-O Bd6 11.Nh4 -&gt; Qh5  
  -> 7976 (r 0.63): f5 23.exf5 e4+ 24.Qf4 Nxf5 25.Qxd6 -&gt; Nxd6

### chess-pgn-2400plus mode 4: 1.8% of the matrix

- **1969 -> 9048** (chess-pgn-1000-1300 +37.3%, chess-pgn-2400plus +31.8%)  
  1969 (r 0.59): Nc6 5.a3 a6 6.b4 Ba7 7.b5 -&gt; axb5  
  -> 9048 (r 0.54): e6 6.c5 Nbd7 7.b4 axb4 8. -&gt; axb4
- **1969 -> 663** (chess-pgn-1000-1300 +36.6%, chess-pgn-2400plus +29.2%)  
  1969 (r 0.59): Nc6 5.a3 a6 6.b4 Ba7 7.b5 -&gt; axb5  
  -> 663 (r 0.47): Bh5 13.Ndf3 Nb3 14.Rb1 Nxc1 15.Rxc1 -&gt; Rxa2
- **8780 -> 9048** (chess-pgn-1000-1300 +29.1%, chess-pgn-2400plus +26.8%)  
  8780 (r 0.48): c4 8.Ne5 Bd7 9.Bg3 b5 10. -&gt; axb5  
  -> 9048 (r 0.54): e6 6.c5 Nbd7 7.b4 axb4 8. -&gt; axb4
- **8780 -> 663** (chess-pgn-1000-1300 +27.4%, chess-pgn-2400plus +23.9%)  
  8780 (r 0.48): c4 8.Ne5 Bd7 9.Bg3 b5 10. -&gt; axb5  
  -> 663 (r 0.47): Bh5 13.Ndf3 Nb3 14.Rb1 Nxc1 15.Rxc1 -&gt; Rxa2
- **16378 -> 9048** (chess-pgn-1000-1300 +46.5%, chess-pgn-2400plus +44.4%)  
  16378 (r 0.52): a5 14.f4 b5 15.a3 b4 16.axb4 -&gt; axb4  
  -> 9048 (r 0.54): e6 6.c5 Nbd7 7.b4 axb4 8. -&gt; axb4
- **16378 -> 663** (chess-pgn-1000-1300 +49.6%, chess-pgn-2400plus +48.0%)  
  16378 (r 0.52): a5 14.f4 b5 15.a3 b4 16.axb4 -&gt; axb4  
  -> 663 (r 0.47): Bh5 13.Ndf3 Nb3 14.Rb1 Nxc1 15.Rxc1 -&gt; Rxa2
- **5834 -> 9048** (chess-pgn-1000-1300 +40.1%, chess-pgn-2400plus +38.7%)  
  5834 (r 0.56): b6 8.b4 a5 9.a3 axb4 10. -&gt; axb4  
  -> 9048 (r 0.54): e6 6.c5 Nbd7 7.b4 axb4 8. -&gt; axb4
- **10107 -> 9048** (chess-pgn-1000-1300 +45.9%, chess-pgn-2400plus +40.0%)  
  10107 (r 0.52): Bb7 11.Ng3 Bc6 12.c3 b5 13.axb5 -&gt; axb5  
  -> 9048 (r 0.54): e6 6.c5 Nbd7 7.b4 axb4 8. -&gt; axb4

### chess-pgn-2400plus mode 5: 1.7% of the matrix

- **1826 -> 5615** (chess-pgn-1000-1300 +49.5%, chess-pgn-2400plus +49.3%)  
  1826 (r 0.58): Rg5 29.Nxh6 Rgd5 30.g3 Rd1+ 31. -&gt; Rxd1  
  -> 5615 (r 0.47): Rh6 4.Nf3 Rg6 5.Nh4 Rg4 6.hxg4 -&gt; hxg4
- **10571 -> 5615** (chess-pgn-1000-1300 +19.9%, chess-pgn-2400plus +19.5%)  
  10571 (r 0.52): Rxc2 25.Nxc8 Qxc8 26.Qxd4 Rc4 27.Qd8+ -&gt; Qxd8  
  -> 5615 (r 0.47): Rh6 4.Nf3 Rg6 5.Nh4 Rg4 6.hxg4 -&gt; hxg4
- **2607 -> 5615** (chess-pgn-1000-1300 -0.4%, chess-pgn-2400plus -0.1%)  
  2607 (r 0.59): c6 5.Bg5 Nbd7 6.e3 Qa5 7.Bxf6 -&gt; Nxf6  
  -> 5615 (r 0.47): Rh6 4.Nf3 Rg6 5.Nh4 Rg4 6.hxg4 -&gt; hxg4
- **10154 -> 5615** (chess-pgn-1000-1300 -0.9%, chess-pgn-2400plus -0.7%)  
  10154 (r 0.63): exf3 5.Nxf3 Bg4 6.h3 Bxf3 7. -&gt; Qxf3  
  -> 5615 (r 0.47): Rh6 4.Nf3 Rg6 5.Nh4 Rg4 6.hxg4 -&gt; hxg4
- **15809 -> 5615** (chess-pgn-1000-1300 -0.7%, chess-pgn-2400plus -0.7%)  
  15809 (r 0.51): Nxe5 6.Be2 Nxf3+ 7.Bxf3 Bxf3 8. -&gt; Qxf3  
  -> 5615 (r 0.47): Rh6 4.Nf3 Rg6 5.Nh4 Rg4 6.hxg4 -&gt; hxg4
- **2173 -> 5615** (chess-pgn-1000-1300 -0.3%, chess-pgn-2400plus -0.2%)  
  2173 (r 0.53): Bc5 4.d3 Nf6 5.Bg5 h6 6.Bxf6 -&gt; Qxf6  
  -> 5615 (r 0.47): Rh6 4.Nf3 Rg6 5.Nh4 Rg4 6.hxg4 -&gt; hxg4
- **13322 -> 5615** (chess-pgn-1000-1300 -0.8%, chess-pgn-2400plus -0.4%)  
  13322 (r 0.62): e5 7.Be2 Nf6 8.Bg5 Be7 9.Bxf6 -&gt; Bxf6  
  -> 5615 (r 0.47): Rh6 4.Nf3 Rg6 5.Nh4 Rg4 6.hxg4 -&gt; hxg4
- **5649 -> 5615** (chess-pgn-1000-1300 +40.5%, chess-pgn-2400plus +40.8%)  
  5649 (r 0.56): bxc5 21.Rd1 Nb6 22.Red2 Kg7 23.Rd8 -&gt; Rxd8  
  -> 5615 (r 0.47): Rh6 4.Nf3 Rg6 5.Nh4 Rg4 6.hxg4 -&gt; hxg4

### chess-pgn-2400plus mode 6: 1.4% of the matrix

- **10970 -> 10215** (chess-pgn-1000-1300 -0.1%, chess-pgn-2400plus +0.5%)  
  10970 (r 0.49): Qh4 4.Qf3 Nf6 5.g3 Qg4 6. -&gt; d3  
  -> 10215 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **11581 -> 10215** (chess-pgn-1000-1300 +42.4%, chess-pgn-2400plus +43.0%)  
  11581 (r 0.46): O-O 10.Na3 d6 11.Bb5 Bg4 12. -&gt; Qg3  
  -> 10215 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **1111 -> 10215** (chess-pgn-1000-1300 +0.1%, chess-pgn-2400plus +2.0%)  
  1111 (r 0.51): h6 16.Kh2 Bg5 17.Bxg5 Qxg5 18. -&gt; Qxg5  
  -> 10215 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **2293 -> 10215** (chess-pgn-1000-1300 +0.3%, chess-pgn-2400plus +1.9%)  
  2293 (r 0.45): Qf5 7.d4 Nc6 8.Bd3 Qg4 9. -&gt; Nxg4  
  -> 10215 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **3991 -> 10215** (chess-pgn-1000-1300 +2.6%, chess-pgn-2400plus +6.6%)  
  3991 (r 0.52): c5 4.c3 Nc6 5.e3 Qb6 6.Qb3 -&gt; c4  
  -> 10215 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **2660 -> 10215** (chess-pgn-1000-1300 +1.0%, chess-pgn-2400plus +2.2%)  
  2660 (r 0.52): exf4 10.Bxf4 d5 11.Be5 Qg5 12. -&gt; Qxg5  
  -> 10215 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **5986 -> 10215** (chess-pgn-1000-1300 +2.5%, chess-pgn-2400plus +0.0%)  
  5986 (r 0.50): Rc8 12.Re1 Qb6 13.Be3 Qxb2 14.Qb1 -&gt; Qxc3  
  -> 10215 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **8300 -> 10215** (chess-pgn-1000-1300 +5.0%, chess-pgn-2400plus +5.6%)  
  8300 (r 0.45): Nxe5 15.dxe5 Qe7 16.Qh5 Qg5 17. -&gt; Qd1  
  -> 10215 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5

### chess-pgn-2400plus mode 7: 1.4% of the matrix

- **1654 -> 12785** (chess-pgn-1000-1300 +52.0%, chess-pgn-2400plus +62.5%)  
  1654 (r 0.55): cxd5 5.Qb3 Bc8 6.Qxd5 Qxd5 7. -&gt; Nxd5  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **11508 -> 12785** (chess-pgn-1000-1300 +67.1%, chess-pgn-2400plus +70.0%)  
  11508 (r 0.54): dxc6 5.d4 exd4 6.Qxd4 Qxd4 7. -&gt; Nxd4  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **14649 -> 12785** (chess-pgn-1000-1300 +53.9%, chess-pgn-2400plus +60.5%)  
  14649 (r 0.55): Qc7 18.e5 dxe5 19.Qxe5 Qxe5+ 20. -&gt; fxe5  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **12347 -> 12785** (chess-pgn-1000-1300 +47.1%, chess-pgn-2400plus +61.2%)  
  12347 (r 0.56): Bxf3 8.gxf3 Nc6 9.Qd5 Rd8 10.Qxe5+ -&gt; Nxe5  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **14587 -> 12785** (chess-pgn-1000-1300 +52.2%, chess-pgn-2400plus +55.1%)  
  14587 (r 0.50): dxc3 7.dxc3 Qe5 8.Qd5 Qxd5 9. -&gt; exd5  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **1121 -> 12785** (chess-pgn-1000-1300 +51.7%, chess-pgn-2400plus +58.6%)  
  1121 (r 0.52): Bb4+ 11.Nc3 Nge7 12.Qb5 Qxb5 13. -&gt; Bxb5  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **4298 -> 12785** (chess-pgn-1000-1300 +53.6%, chess-pgn-2400plus +60.4%)  
  4298 (r 0.48): Nc6 6.a3 Qd4 7.Be3 Qg4 8.Qxg4 -&gt; Bxg4  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **12415 -> 12785** (chess-pgn-1000-1300 +42.8%, chess-pgn-2400plus +48.8%)  
  12415 (r 0.44): Ng6 13.h4 gxh6 14.h5 Qg5 15.Qxg5 -&gt; hxg5  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8

### chess-pgn-2400plus mode 8: 1.2% of the matrix

- **1165 -> 7114** (chess-pgn-1000-1300 +64.2%, chess-pgn-2400plus +71.6%)  
  1165 (r 0.56): Nf6 4.Bc4 Be7 5.d4 d6 6.dxe5 -&gt; Nxe5  
  -> 7114 (r 0.54): d5 5.exd5 Na5 6.Bd3 e4 7.Nxe4 -&gt; Nxd5
- **7238 -> 7114** (chess-pgn-1000-1300 +57.5%, chess-pgn-2400plus +52.2%)  
  7238 (r 0.53): Be7 4.d4 exd4 5.Qxd4 Nf6 6.e5 -&gt; dxe5  
  -> 7114 (r 0.54): d5 5.exd5 Na5 6.Bd3 e4 7.Nxe4 -&gt; Nxd5
- **2192 -> 7114** (chess-pgn-1000-1300 -1.2%, chess-pgn-2400plus -1.5%)  
  2192 (r 0.46): h6 9.Qe2 d6 10.Be3 Nd4 11. -&gt; Qd1  
  -> 7114 (r 0.54): d5 5.exd5 Na5 6.Bd3 e4 7.Nxe4 -&gt; Nxd5
- **15798 -> 7114** (chess-pgn-1000-1300 +53.9%, chess-pgn-2400plus +60.1%)  
  15798 (r 0.57): O-O 6.O-O Nbd7 7.Re1 e5 8.dxe5 -&gt; dxe5  
  -> 7114 (r 0.54): d5 5.exd5 Na5 6.Bd3 e4 7.Nxe4 -&gt; Nxd5
- **2580 -> 7114** (chess-pgn-1000-1300 +49.4%, chess-pgn-2400plus +55.5%)  
  2580 (r 0.63): Nf6 5.Bf4 Bg4 6.Qe2 e5 7.dxe5 -&gt; dxe5  
  -> 7114 (r 0.54): d5 5.exd5 Na5 6.Bd3 e4 7.Nxe4 -&gt; Nxd5
- **7626 -> 7114** (chess-pgn-1000-1300 +55.7%, chess-pgn-2400plus +65.1%)  
  7626 (r 0.56): Nc6 5.Bf4 Bg4 6.e3 e5 7.dxe5 -&gt; Nxe5  
  -> 7114 (r 0.54): d5 5.exd5 Na5 6.Bd3 e4 7.Nxe4 -&gt; Nxd5
- **15761 -> 7114** (chess-pgn-1000-1300 +48.0%, chess-pgn-2400plus +49.8%)  
  15761 (r 0.60): Nf6 5.c3 a6 6.d4 Ba7 7.dxe5 -&gt; Nxe4  
  -> 7114 (r 0.54): d5 5.exd5 Na5 6.Bd3 e4 7.Nxe4 -&gt; Nxd5
- **7691 -> 7114** (chess-pgn-1000-1300 -1.8%, chess-pgn-2400plus -1.2%)  
  7691 (r 0.63): e5 11.d5 c6 12.O-O cxd5 13.Nxd5 -&gt; Nxd5  
  -> 7114 (r 0.54): d5 5.exd5 Na5 6.Bd3 e4 7.Nxe4 -&gt; Nxd5

### chess-pgn-2400plus mode 9: 1.2% of the matrix

- **1 -> 6774** (chess-pgn-1000-1300 +68.1%, chess-pgn-2400plus +66.0%)  
  1 (r 0.43): Nf6 5.O-O d6 6.Nc3 a5 7.Bg5 -&gt; h6  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4
- **16210 -> 6774** (chess-pgn-1000-1300 +62.1%, chess-pgn-2400plus +57.3%)  
  16210 (r 0.58): O-O 11.Nxf6+ Qxf6 12.O-O Bg4 13. -&gt; Be2  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4
- **1 -> 14097** (chess-pgn-1000-1300 -3.6%, chess-pgn-2400plus -3.5%)  
  1 (r 0.43): Nf6 5.O-O d6 6.Nc3 a5 7.Bg5 -&gt; h6  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **1254 -> 6774** (chess-pgn-1000-1300 -1.1%, chess-pgn-2400plus -0.9%)  
  1254 (r 0.64): Nb4 5.Qc4 b5 6.Qxb5 Nxc2+ 7. -&gt; Kd2  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4
- **16246 -> 6774** (chess-pgn-1000-1300 +63.8%, chess-pgn-2400plus +64.6%)  
  16246 (r 0.49): exd5 4.d4 Bd6 5.Nc3 Ne7 6.Bg5 -&gt; f6  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4
- **12554 -> 6774** (chess-pgn-1000-1300 +55.9%, chess-pgn-2400plus +50.2%)  
  12554 (r 0.57): Nxe4 5.Qe2 Qe7 6.d3 Nf6 7.Bg5 -&gt; Qxe2+  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4
- **16210 -> 14097** (chess-pgn-1000-1300 -2.6%, chess-pgn-2400plus -2.1%)  
  16210 (r 0.58): O-O 11.Nxf6+ Qxf6 12.O-O Bg4 13. -&gt; Be2  
  -> 14097 (r 0.65): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **2205 -> 6774** (chess-pgn-1000-1300 -0.9%, chess-pgn-2400plus -1.2%)  
  2205 (r 0.58): Nge7 9.d4 exd4 10.Bf4 Qg6 11.Nxc7+ -&gt; Kf8  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4

### chess-pgn-2400plus mode 10: 1.1% of the matrix

- **1980 -> 16081** (chess-pgn-1000-1300 +67.1%, chess-pgn-2400plus +61.4%)  
  1980 (r 0.57): dxc4 4.Bxc4 e6 5.Ne2 Bb4+ 6. -&gt; Bd2  
  -> 16081 (r 0.51): Nc6 6.Bb5 dxe5 7.Qxd8+ Kxd8 8. -&gt; Bxc6
- **11095 -> 16081** (chess-pgn-1000-1300 +71.0%, chess-pgn-2400plus +68.0%)  
  11095 (r 0.44): e5 6.Nfd2 Nf6 7.Be2 Nc6 8.Bb5 -&gt; Bd7  
  -> 16081 (r 0.51): Nc6 6.Bb5 dxe5 7.Qxd8+ Kxd8 8. -&gt; Bxc6
- **9561 -> 16081** (chess-pgn-1000-1300 +65.4%, chess-pgn-2400plus +63.7%)  
  9561 (r 0.58): Nc6 6.c3 Nxd4 7.cxd4 Bb4+ 8. -&gt; Nc3  
  -> 16081 (r 0.51): Nc6 6.Bb5 dxe5 7.Qxd8+ Kxd8 8. -&gt; Bxc6
- **2818 -> 16081** (chess-pgn-1000-1300 +62.6%, chess-pgn-2400plus +59.7%)  
  2818 (r 0.52): Nge7 7.f4 Nxd4 8.cxd4 Bb4+ 9. -&gt; Nc3  
  -> 16081 (r 0.51): Nc6 6.Bb5 dxe5 7.Qxd8+ Kxd8 8. -&gt; Bxc6
- **4608 -> 16081** (chess-pgn-1000-1300 +60.2%, chess-pgn-2400plus +55.9%)  
  4608 (r 0.60): h6 6.O-O d6 7.h3 Be6 8.Bb5 -&gt; O-O  
  -> 16081 (r 0.51): Nc6 6.Bb5 dxe5 7.Qxd8+ Kxd8 8. -&gt; Bxc6
- **11835 -> 16081** (chess-pgn-1000-1300 +48.2%, chess-pgn-2400plus +50.1%)  
  11835 (r 0.54): exd5 4.d4 Nf6 5.Nc3 c5 6.Bb5+ -&gt; Nc6  
  -> 16081 (r 0.51): Nc6 6.Bb5 dxe5 7.Qxd8+ Kxd8 8. -&gt; Bxc6
- **8903 -> 16081** (chess-pgn-1000-1300 +54.1%, chess-pgn-2400plus +51.2%)  
  8903 (r 0.59): Ng4 4.Bf4 Nc6 5.Nf3 Bb4+ 6. -&gt; Nc3  
  -> 16081 (r 0.51): Nc6 6.Bb5 dxe5 7.Qxd8+ Kxd8 8. -&gt; Bxc6
- **13961 -> 16081** (chess-pgn-1000-1300 +60.6%, chess-pgn-2400plus +59.2%)  
  13961 (r 0.54): Qb4+ 9.Qd2 Nb6 10.Qxb4 Bxb4+ 11. -&gt; Bd2  
  -> 16081 (r 0.51): Nc6 6.Bb5 dxe5 7.Qxd8+ Kxd8 8. -&gt; Bxc6

### chess-pgn-2400plus mode 11: 1.1% of the matrix

- **1 -> 6774** (chess-pgn-1000-1300 +68.1%, chess-pgn-2400plus +66.0%)  
  1 (r 0.43): Nf6 5.O-O d6 6.Nc3 a5 7.Bg5 -&gt; h6  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4
- **16246 -> 6774** (chess-pgn-1000-1300 +63.8%, chess-pgn-2400plus +64.6%)  
  16246 (r 0.49): exd5 4.d4 Bd6 5.Nc3 Ne7 6.Bg5 -&gt; f6  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4
- **10673 -> 6774** (chess-pgn-1000-1300 +65.9%, chess-pgn-2400plus +67.5%)  
  10673 (r 0.51): O-O 8.O-O Nc6 9.Bb3 Bg4 10. -&gt; f3  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4
- **13835 -> 6774** (chess-pgn-1000-1300 +60.5%, chess-pgn-2400plus +63.8%)  
  13835 (r 0.58): d6 7.O-O Nc6 8.Ng3 Bg4 9. -&gt; Qe1  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4
- **6421 -> 6774** (chess-pgn-1000-1300 +62.7%, chess-pgn-2400plus +64.6%)  
  6421 (r 0.51): Bd6 8.f4 Bxe5 9.fxe5 Bg4 10. -&gt; Qd4  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4
- **15712 -> 6774** (chess-pgn-1000-1300 +56.4%, chess-pgn-2400plus +55.0%)  
  15712 (r 0.57): Nf6 4.d3 Nc6 5.Ng5 Bg4 6. -&gt; Nxf7  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4
- **14396 -> 6774** (chess-pgn-1000-1300 +64.7%, chess-pgn-2400plus +66.9%)  
  14396 (r 0.50): d5 8.cxd5 exd5 9.e5 Nf5 10.Bg5 -&gt; Qd7  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4
- **8683 -> 6774** (chess-pgn-1000-1300 +62.4%, chess-pgn-2400plus +63.7%)  
  8683 (r 0.55): exd5 4.Nf3 Nc6 5.h3 Bd6 6.Bg5 -&gt; Nge7  
  -> 6774 (r 0.52): Qd7 10.h4 Nh5 11.g4 Nf4 12. -&gt; Bxf4

### chess-pgn-2400plus mode 12: 1.0% of the matrix

- **8093 -> 11434** (chess-pgn-1000-1300 -12.8%, chess-pgn-2400plus -0.4%)  
  8093 (r 0.62): cxd4 4.Nxd4 Nf6 5.Nc3 e5 6. -&gt; Ndb5  
  -> 11434 (r 0.45): Ke6 19.Qxc8+ Nd7 20.Qxa8 Qxc2 21. -&gt; Qe8#
- **14065 -> 5615** (chess-pgn-1000-1300 +45.9%, chess-pgn-2400plus +48.1%)  
  14065 (r 0.53): Bg7 6.Bb2 a5 7.Nge2 axb4 8.axb4 -&gt; Rxa1  
  -> 5615 (r 0.47): Rh6 4.Nf3 Rg6 5.Nh4 Rg4 6.hxg4 -&gt; hxg4
- **15651 -> 5615** (chess-pgn-1000-1300 -0.7%, chess-pgn-2400plus -0.2%)  
  15651 (r 0.47): Kg6 25.Re6+ Kf5 26.Qf7+ Kg4 27. -&gt; Qxg7+  
  -> 5615 (r 0.47): Rh6 4.Nf3 Rg6 5.Nh4 Rg4 6.hxg4 -&gt; hxg4
- **7530 -> 5615** (chess-pgn-1000-1300 +0.9%, chess-pgn-2400plus -0.1%)  
  7530 (r 0.58): Kg6 50.Rf6+ Kh7 51.Qf7+ Kh8 52. -&gt; Rh6#  
  -> 5615 (r 0.47): Rh6 4.Nf3 Rg6 5.Nh4 Rg4 6.hxg4 -&gt; hxg4
- **115 -> 5615** (chess-pgn-1000-1300 +36.9%, chess-pgn-2400plus +39.4%)  
  115 (r 0.51): Nge7 8.O-O b5 9.axb5 axb5 10. -&gt; Rxa8  
  -> 5615 (r 0.47): Rh6 4.Nf3 Rg6 5.Nh4 Rg4 6.hxg4 -&gt; hxg4
- **5177 -> 5615** (chess-pgn-1000-1300 +37.3%, chess-pgn-2400plus +40.9%)  
  5177 (r 0.56): Bg7 6.h4 Ne7 7.hxg5 hxg5 8. -&gt; Rxh8+  
  -> 5615 (r 0.47): Rh6 4.Nf3 Rg6 5.Nh4 Rg4 6.hxg4 -&gt; hxg4
- **11847 -> 5615** (chess-pgn-1000-1300 +42.6%, chess-pgn-2400plus +47.2%)  
  11847 (r 0.59): axb6 7.Bc4 Nb4 8.Bd3 Rxa2 9. -&gt; Rxa2  
  -> 5615 (r 0.47): Rh6 4.Nf3 Rg6 5.Nh4 Rg4 6.hxg4 -&gt; hxg4
- **7530 -> 12785** (chess-pgn-1000-1300 +0.6%, chess-pgn-2400plus +0.0%)  
  7530 (r 0.58): Kg6 50.Rf6+ Kh7 51.Qf7+ Kh8 52. -&gt; Rh6#  
  -> 12785 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8

### chess-pgn-2400plus mode 13: 1.0% of the matrix

- **14466 -> 6441** (chess-pgn-1000-1300 +43.5%, chess-pgn-2400plus +44.2%)  
  14466 (r 0.55): h6 7.Bh4 d6 8.Nd5 Qd7 9.Bxf6 -&gt; gxf6  
  -> 6441 (r 0.47): Qc8 13.Na3 Bf5 14.c4 Bxd3 15.Qxd3 -&gt; Qf5
- **3512 -> 6441** (chess-pgn-1000-1300 +55.9%, chess-pgn-2400plus +55.9%)  
  3512 (r 0.53): Bg4 6.Nf3 Nd4 7.h3 Bxf3 8. -&gt; gxf3  
  -> 6441 (r 0.47): Qc8 13.Na3 Bf5 14.c4 Bxd3 15.Qxd3 -&gt; Qf5
- **15742 -> 6441** (chess-pgn-1000-1300 +53.4%, chess-pgn-2400plus +53.1%)  
  15742 (r 0.56): f6 6.Nf3 Be7 7.h3 Nh6 8.Bxh6 -&gt; gxh6  
  -> 6441 (r 0.47): Qc8 13.Na3 Bf5 14.c4 Bxd3 15.Qxd3 -&gt; Qf5
- **368 -> 6441** (chess-pgn-1000-1300 +45.9%, chess-pgn-2400plus +43.5%)  
  368 (r 0.46): Bd6 11.Bg5 h6 12.Bh4 Qc7 13.Bxf6 -&gt; gxf6  
  -> 6441 (r 0.47): Qc8 13.Na3 Bf5 14.c4 Bxd3 15.Qxd3 -&gt; Qf5
- **4693 -> 6441** (chess-pgn-1000-1300 +40.0%, chess-pgn-2400plus +41.2%)  
  4693 (r 0.47): Rc8 11.Bg5 h6 12.Bxd7 Qxd7 13.Bxf6 -&gt; gxf6  
  -> 6441 (r 0.47): Qc8 13.Na3 Bf5 14.c4 Bxd3 15.Qxd3 -&gt; Qf5
- **14466 -> 2954** (chess-pgn-1000-1300 -2.5%, chess-pgn-2400plus -0.9%)  
  14466 (r 0.55): h6 7.Bh4 d6 8.Nd5 Qd7 9.Bxf6 -&gt; gxf6  
  -> 2954 (r 0.48): Qc5 10.d4 Qb6 11.Bxc6+ Qxc6 12. -&gt; Qb4
- **13853 -> 6441** (chess-pgn-1000-1300 +54.5%, chess-pgn-2400plus +52.2%)  
  13853 (r 0.57): Rdd8 27.Rc6 Bd5 28.Rxa6 Bxf3 29. -&gt; gxf3  
  -> 6441 (r 0.47): Qc8 13.Na3 Bf5 14.c4 Bxd3 15.Qxd3 -&gt; Qf5
- **14381 -> 6441** (chess-pgn-1000-1300 +42.3%, chess-pgn-2400plus +32.5%)  
  14381 (r 0.56): Be6 9.Bc2 Qd7 10.O-O Bxh3 11. -&gt; gxh3  
  -> 6441 (r 0.47): Qc8 13.Na3 Bf5 14.c4 Bxd3 15.Qxd3 -&gt; Qf5

### chess-pgn-2400plus mode 14: 0.9% of the matrix

- **1839 -> 7874** (chess-pgn-1000-1300 +35.8%, chess-pgn-2400plus +41.2%)  
  1839 (r 0.61): d5 4.e5 g5 5.d4 h6 6.h4 -&gt; g4  
  -> 7874 (r 0.51): Be7 8.h4 Nc6 9.g5 Nd7 10.Rg1 -&gt; h6
- **1839 -> 2515** (chess-pgn-1000-1300 +28.1%, chess-pgn-2400plus +32.9%)  
  1839 (r 0.61): d5 4.e5 g5 5.d4 h6 6.h4 -&gt; g4  
  -> 2515 (r 0.44): Kh6 49.g4 Rf6 50.g5+ Kg7 51. -&gt; gxf6+
- **1839 -> 11686** (chess-pgn-1000-1300 -1.2%, chess-pgn-2400plus -1.6%)  
  1839 (r 0.61): d5 4.e5 g5 5.d4 h6 6.h4 -&gt; g4  
  -> 11686 (r 0.45): exf5 13.exf5 Bh7 14.Kh1 Qh4 15.Bf4 -&gt; O-O-O
- **5247 -> 7874** (chess-pgn-1000-1300 +29.9%, chess-pgn-2400plus +29.8%)  
  5247 (r 0.58): Nf6 6.O-O g5 7.h3 g4 8. -&gt; hxg4  
  -> 7874 (r 0.51): Be7 8.h4 Nc6 9.g5 Nd7 10.Rg1 -&gt; h6
- **5477 -> 7874** (chess-pgn-1000-1300 +43.4%, chess-pgn-2400plus +45.0%)  
  5477 (r 0.59): Be6 13.g4 Re8 14.h4 a5 15.g5 -&gt; hxg5  
  -> 7874 (r 0.51): Be7 8.h4 Nc6 9.g5 Nd7 10.Rg1 -&gt; h6
- **7178 -> 7874** (chess-pgn-1000-1300 +32.9%, chess-pgn-2400plus +41.4%)  
  7178 (r 0.65): e6 6.g4 Bg6 7.h4 h5 8. -&gt; g5  
  -> 7874 (r 0.51): Be7 8.h4 Nc6 9.g5 Nd7 10.Rg1 -&gt; h6
- **8281 -> 7874** (chess-pgn-1000-1300 +28.3%, chess-pgn-2400plus +30.1%)  
  8281 (r 0.60): Bh5 7.g4 Bg6 8.h4 h5 9. -&gt; g5  
  -> 7874 (r 0.51): Be7 8.h4 Nc6 9.g5 Nd7 10.Rg1 -&gt; h6
- **4758 -> 7874** (chess-pgn-1000-1300 +33.5%, chess-pgn-2400plus +32.6%)  
  4758 (r 0.66): g5 11.Bh2 h5 12.O-O g4 13. -&gt; hxg4  
  -> 7874 (r 0.51): Be7 8.h4 Nc6 9.g5 Nd7 10.Rg1 -&gt; h6
