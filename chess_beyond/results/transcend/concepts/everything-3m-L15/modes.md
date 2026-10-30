# Flow modes, everything-3m-L15

Truncated SVD of the excess-rate matrix r[i, j] = (C - E) / (N_i + prior): how much more often latent j turns on within 4 plies of i's onset than in sibling rollouts. **diff** = r under chess-pgn-2400plus minus r under chess-pgn-1000-1300 (positive: stronger when chess-pgn-2400plus plays). A mode is a group of source latents (u) feeding a group of target latents (v).

## diff

### diff mode 0: 5.2% of the matrix

- **8015 -> 15729** (chess-pgn-1000-1300 -0.5%, chess-pgn-2400plus -2.9%)  
  8015 (r 0.63): Nh6 4.d4 g5 5.dxe5 fxe5 6. -&gt; Bxg5  
  -> 15729 (r 0.41): Nd7 7.O-O O-O-O 8.Qd2 Ngf6 9. -&gt; Qe3
- **953 -> 15729** (chess-pgn-1000-1300 -6.0%, chess-pgn-2400plus -8.8%)  
  953 (r 0.55): h6 7.Bh4 d6 8.Nd5 Nxd5 9.Bxd8 -&gt; Rxd8  
  -> 15729 (r 0.41): Nd7 7.O-O O-O-O 8.Qd2 Ngf6 9. -&gt; Qe3
- **8015 -> 1773** (chess-pgn-1000-1300 +11.5%, chess-pgn-2400plus +5.3%)  
  8015 (r 0.63): Nh6 4.d4 g5 5.dxe5 fxe5 6. -&gt; Bxg5  
  -> 1773 (r 0.76): Nxe5 8.Qxe5 d6 9.Qf5 Bxf5 10. -&gt; f3
- **953 -> 1773** (chess-pgn-1000-1300 +32.3%, chess-pgn-2400plus +18.7%)  
  953 (r 0.55): h6 7.Bh4 d6 8.Nd5 Nxd5 9.Bxd8 -&gt; Rxd8  
  -> 1773 (r 0.76): Nxe5 8.Qxe5 d6 9.Qf5 Bxf5 10. -&gt; f3
- **13276 -> 15729** (chess-pgn-1000-1300 -1.9%, chess-pgn-2400plus -5.9%)  
  13276 (r 0.59): c6 6.e3 Nbd7 7.g4 Nxe5 8.gxf5 -&gt; Neg4  
  -> 15729 (r 0.41): Nd7 7.O-O O-O-O 8.Qd2 Ngf6 9. -&gt; Qe3
- **13276 -> 1773** (chess-pgn-1000-1300 +17.2%, chess-pgn-2400plus +7.9%)  
  13276 (r 0.59): c6 6.e3 Nbd7 7.g4 Nxe5 8.gxf5 -&gt; Neg4  
  -> 1773 (r 0.76): Nxe5 8.Qxe5 d6 9.Qf5 Bxf5 10. -&gt; f3
- **9005 -> 15729** (chess-pgn-1000-1300 -4.6%, chess-pgn-2400plus -4.7%)  
  9005 (r 0.38): e5 4.Qxg4 Be7 5.Nf3 d5 6.Nc3 -&gt; Bxg4  
  -> 15729 (r 0.41): Nd7 7.O-O O-O-O 8.Qd2 Ngf6 9. -&gt; Qe3
- **9005 -> 1773** (chess-pgn-1000-1300 +25.1%, chess-pgn-2400plus +10.2%)  
  9005 (r 0.38): e5 4.Qxg4 Be7 5.Nf3 d5 6.Nc3 -&gt; Bxg4  
  -> 1773 (r 0.76): Nxe5 8.Qxe5 d6 9.Qf5 Bxf5 10. -&gt; f3

### diff mode 1: 3.0% of the matrix

- **632 -> 1773** (chess-pgn-1000-1300 +46.3%, chess-pgn-2400plus +14.7%)  
  632 (r 0.43): Rxa1 13.Qxa1 Nbd7 14.O-O Qc7 15. -&gt; Bxc7  
  -> 1773 (r 0.76): Nxe5 8.Qxe5 d6 9.Qf5 Bxf5 10. -&gt; f3
- **6308 -> 1773** (chess-pgn-1000-1300 +45.4%, chess-pgn-2400plus +21.5%)  
  6308 (r 0.36): Bg4 6.Bd2 b5 7.Nxb5 Nf6 8. -&gt; Bxa5  
  -> 1773 (r 0.76): Nxe5 8.Qxe5 d6 9.Qf5 Bxf5 10. -&gt; f3
- **632 -> 11585** (chess-pgn-1000-1300 +39.9%, chess-pgn-2400plus +11.0%)  
  632 (r 0.43): Rxa1 13.Qxa1 Nbd7 14.O-O Qc7 15. -&gt; Bxc7  
  -> 11585 (r 0.58): d5 4.Bh5 Nf6 5.Qg4 Nxg4 6.Bxg4 -&gt; Bxg4
- **3004 -> 1773** (chess-pgn-1000-1300 +35.0%, chess-pgn-2400plus +15.7%)  
  3004 (r 0.47): cxd4 4.Qxd4 Nf6 5.e4 Nc6 6.e5 -&gt; Nxd4  
  -> 1773 (r 0.76): Nxe5 8.Qxe5 d6 9.Qf5 Bxf5 10. -&gt; f3
- **632 -> 1144** (chess-pgn-1000-1300 +23.6%, chess-pgn-2400plus +5.7%)  
  632 (r 0.43): Rxa1 13.Qxa1 Nbd7 14.O-O Qc7 15. -&gt; Bxc7  
  -> 1144 (r 0.73): Ng4 20.Bxg4 Nd3 21.Qxd3 Rac8 22.Nxe8 -&gt; Rc7
- **632 -> 8648** (chess-pgn-1000-1300 +39.9%, chess-pgn-2400plus +10.8%)  
  632 (r 0.43): Rxa1 13.Qxa1 Nbd7 14.O-O Qc7 15. -&gt; Bxc7  
  -> 8648 (r 0.58): Rxd2 20.Bxd2 Ne5 21.Nxe5 dxe5 22. -&gt; Bc4
- **6308 -> 11585** (chess-pgn-1000-1300 +42.4%, chess-pgn-2400plus +16.7%)  
  6308 (r 0.36): Bg4 6.Bd2 b5 7.Nxb5 Nf6 8. -&gt; Bxa5  
  -> 11585 (r 0.58): d5 4.Bh5 Nf6 5.Qg4 Nxg4 6.Bxg4 -&gt; Bxg4
- **14837 -> 1773** (chess-pgn-1000-1300 +33.5%, chess-pgn-2400plus +14.1%)  
  14837 (r 0.35): Qd7 24.Rxb2 Nb4 25.a3 Qxh3+ 26. -&gt; Nxh3  
  -> 1773 (r 0.76): Nxe5 8.Qxe5 d6 9.Qf5 Bxf5 10. -&gt; f3

### diff mode 2: 1.7% of the matrix

- **3816 -> 12934** (chess-pgn-1000-1300 +6.3%, chess-pgn-2400plus +2.3%)  
  3816 (r 0.45): bxc6 5.Nxe5 Nxe4 6.Qe2 Nf6 7. -&gt; Nxc6+  
  -> 12934 (r 0.56): Kxf7 4.Nf3 d6 5.c3 Bg4 6.Ng5+ -&gt; Kf8
- **3816 -> 5077** (chess-pgn-1000-1300 +27.2%, chess-pgn-2400plus +9.9%)  
  3816 (r 0.45): bxc6 5.Nxe5 Nxe4 6.Qe2 Nf6 7. -&gt; Nxc6+  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **12425 -> 12934** (chess-pgn-1000-1300 +7.8%, chess-pgn-2400plus +4.3%)  
  12425 (r 0.43): Qh4 4.g3 Qxe4+ 5.Qe2 Qxh1 6. -&gt; Nxf7+  
  -> 12934 (r 0.56): Kxf7 4.Nf3 d6 5.c3 Bg4 6.Ng5+ -&gt; Kf8
- **160 -> 12934** (chess-pgn-1000-1300 +42.6%, chess-pgn-2400plus +27.2%)  
  160 (r 0.49): Nf6 4.e3 Nc6 5.Nb5 a6 6. -&gt; Nc7+  
  -> 12934 (r 0.56): Kxf7 4.Nf3 d6 5.c3 Bg4 6.Ng5+ -&gt; Kf8
- **7522 -> 12934** (chess-pgn-1000-1300 +1.5%, chess-pgn-2400plus +0.6%)  
  7522 (r 0.57): d6 5.d3 Be6 6.Bxe6 fxe6 7.Ng5 -&gt; Be7  
  -> 12934 (r 0.56): Kxf7 4.Nf3 d6 5.c3 Bg4 6.Ng5+ -&gt; Kf8
- **8185 -> 12934** (chess-pgn-1000-1300 +11.8%, chess-pgn-2400plus +6.9%)  
  8185 (r 0.22): Nxe4 7.O-O Qd6 8.Re1 Nf6 9. -&gt; Nc4+  
  -> 12934 (r 0.56): Kxf7 4.Nf3 d6 5.c3 Bg4 6.Ng5+ -&gt; Kf8
- **6501 -> 12934** (chess-pgn-1000-1300 +9.8%, chess-pgn-2400plus +4.7%)  
  6501 (r 0.49): f5 24.Nd2 Nd4 25.Qf1 Ne3 26.Nc4 -&gt; Nxf1  
  -> 12934 (r 0.56): Kxf7 4.Nf3 d6 5.c3 Bg4 6.Ng5+ -&gt; Kf8
- **12586 -> 12934** (chess-pgn-1000-1300 +5.9%, chess-pgn-2400plus +2.6%)  
  12586 (r 0.27): d6 12.f4 exf4 13.Rxf4 Qxg5 14. -&gt; Rf8+  
  -> 12934 (r 0.56): Kxf7 4.Nf3 d6 5.c3 Bg4 6.Ng5+ -&gt; Kf8

### diff mode 3: 1.5% of the matrix

- **632 -> 1057** (chess-pgn-1000-1300 -1.8%, chess-pgn-2400plus -1.1%)  
  632 (r 0.43): Rxa1 13.Qxa1 Nbd7 14.O-O Qc7 15. -&gt; Bxc7  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **6308 -> 1057** (chess-pgn-1000-1300 -4.3%, chess-pgn-2400plus -1.4%)  
  6308 (r 0.36): Bg4 6.Bd2 b5 7.Nxb5 Nf6 8. -&gt; Bxa5  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **440 -> 1057** (chess-pgn-1000-1300 +21.5%, chess-pgn-2400plus +7.4%)  
  440 (r 0.33): Qh4 5.g3 Qxe4+ 6.Be2 Qxh1 7.Bb5 -&gt; Qxg1+  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **2261 -> 1057** (chess-pgn-1000-1300 +26.5%, chess-pgn-2400plus +14.4%)  
  2261 (r 0.35): Nxd4 9.Qxg7 Nc2+ 10.Kd1 Nxa1 11. -&gt; Qxh8  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **14172 -> 1057** (chess-pgn-1000-1300 +20.9%, chess-pgn-2400plus +6.4%)  
  14172 (r 0.47): g6 4.Qxe5+ Ne7 5.Qxh8+ Ng8 6. -&gt; Qxg8+  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **632 -> 8648** (chess-pgn-1000-1300 +39.9%, chess-pgn-2400plus +10.8%)  
  632 (r 0.43): Rxa1 13.Qxa1 Nbd7 14.O-O Qc7 15. -&gt; Bxc7  
  -> 8648 (r 0.58): Rxd2 20.Bxd2 Ne5 21.Nxe5 dxe5 22. -&gt; Bc4
- **6308 -> 8648** (chess-pgn-1000-1300 +43.3%, chess-pgn-2400plus +18.8%)  
  6308 (r 0.36): Bg4 6.Bd2 b5 7.Nxb5 Nf6 8. -&gt; Bxa5  
  -> 8648 (r 0.58): Rxd2 20.Bxd2 Ne5 21.Nxe5 dxe5 22. -&gt; Bc4
- **9501 -> 1057** (chess-pgn-1000-1300 +20.0%, chess-pgn-2400plus +10.1%)  
  9501 (r 0.38): fxe5 4.Qh5+ g6 5.Qxe5+ Ne7 6. -&gt; Qxh8  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6

### diff mode 4: 1.3% of the matrix

- **160 -> 7056** (chess-pgn-1000-1300 -3.3%, chess-pgn-2400plus -1.0%)  
  160 (r 0.49): Nf6 4.e3 Nc6 5.Nb5 a6 6. -&gt; Nc7+  
  -> 7056 (r 0.47): h4 23.gxh4 Bg4 24.Bg2 Bxf3 25.Bxf3 -&gt; Nh6
- **4263 -> 7056** (chess-pgn-1000-1300 -2.2%, chess-pgn-2400plus -0.7%)  
  4263 (r 0.57): dxe4 4.f3 exf3 5.Qxf3 Bg4 6.Qxb7 -&gt; Nbd7  
  -> 7056 (r 0.47): h4 23.gxh4 Bg4 24.Bg2 Bxf3 25.Bxf3 -&gt; Nh6
- **3816 -> 7056** (chess-pgn-1000-1300 -1.0%, chess-pgn-2400plus -0.9%)  
  3816 (r 0.45): bxc6 5.Nxe5 Nxe4 6.Qe2 Nf6 7. -&gt; Nxc6+  
  -> 7056 (r 0.47): h4 23.gxh4 Bg4 24.Bg2 Bxf3 25.Bxf3 -&gt; Nh6
- **5437 -> 7056** (chess-pgn-1000-1300 -1.3%, chess-pgn-2400plus -0.1%)  
  5437 (r 0.45): Bb4 7.Bd3 Nxd4 8.Nxd4 Qxd4 9.Bb5+ -&gt; c6  
  -> 7056 (r 0.47): h4 23.gxh4 Bg4 24.Bg2 Bxf3 25.Bxf3 -&gt; Nh6
- **9104 -> 7056** (chess-pgn-1000-1300 -2.0%, chess-pgn-2400plus +2.8%)  
  9104 (r 0.56): Nc6 4.Bg5 Qb4+ 5.Nc3 Qxb2 6. -&gt; Nd5  
  -> 7056 (r 0.47): h4 23.gxh4 Bg4 24.Bg2 Bxf3 25.Bxf3 -&gt; Nh6
- **11079 -> 7056** (chess-pgn-1000-1300 +43.1%, chess-pgn-2400plus +31.5%)  
  11079 (r 0.44): Bc5 5.Bc4 d6 6.O-O Bxh3 7. -&gt; gxh3  
  -> 7056 (r 0.47): h4 23.gxh4 Bg4 24.Bg2 Bxf3 25.Bxf3 -&gt; Nh6
- **8570 -> 7056** (chess-pgn-1000-1300 -1.5%, chess-pgn-2400plus +0.3%)  
  8570 (r 0.50): Qb4+ 5.Bd2 Qxb2 6.Nc3 Nb4 7. -&gt; Rb1  
  -> 7056 (r 0.47): h4 23.gxh4 Bg4 24.Bg2 Bxf3 25.Bxf3 -&gt; Nh6
- **160 -> 5077** (chess-pgn-1000-1300 +40.2%, chess-pgn-2400plus +23.7%)  
  160 (r 0.49): Nf6 4.e3 Nc6 5.Nb5 a6 6. -&gt; Nc7+  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+

### diff mode 5: 1.0% of the matrix

- **14172 -> 5077** (chess-pgn-1000-1300 -1.5%, chess-pgn-2400plus +2.5%)  
  14172 (r 0.47): g6 4.Qxe5+ Ne7 5.Qxh8+ Ng8 6. -&gt; Qxg8+  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **160 -> 5077** (chess-pgn-1000-1300 +40.2%, chess-pgn-2400plus +23.7%)  
  160 (r 0.49): Nf6 4.e3 Nc6 5.Nb5 a6 6. -&gt; Nc7+  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **440 -> 5077** (chess-pgn-1000-1300 -2.6%, chess-pgn-2400plus -0.3%)  
  440 (r 0.33): Qh4 5.g3 Qxe4+ 6.Be2 Qxh1 7.Bb5 -&gt; Qxg1+  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **11702 -> 5077** (chess-pgn-1000-1300 -4.2%, chess-pgn-2400plus -3.3%)  
  11702 (r 0.41): Nxd5 4.Bxd5 Qxd5 5.Nc3 Qxg2 6.Nge2 -&gt; Qxh1+  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **9501 -> 5077** (chess-pgn-1000-1300 -2.8%, chess-pgn-2400plus -1.3%)  
  9501 (r 0.38): fxe5 4.Qh5+ g6 5.Qxe5+ Ne7 6. -&gt; Qxh8  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **5437 -> 5077** (chess-pgn-1000-1300 -3.6%, chess-pgn-2400plus -1.0%)  
  5437 (r 0.45): Bb4 7.Bd3 Nxd4 8.Nxd4 Qxd4 9.Bb5+ -&gt; c6  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **2261 -> 5077** (chess-pgn-1000-1300 -3.3%, chess-pgn-2400plus -2.0%)  
  2261 (r 0.35): Nxd4 9.Qxg7 Nc2+ 10.Kd1 Nxa1 11. -&gt; Qxh8  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **5085 -> 5077** (chess-pgn-1000-1300 +25.3%, chess-pgn-2400plus +13.5%)  
  5085 (r 0.55): Ng4 9.O-O Bc5+ 10.Kh1 Nf2+ 11. -&gt; Rxf2  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+

### diff mode 6: 0.9% of the matrix

- **632 -> 1214** (chess-pgn-1000-1300 -1.9%, chess-pgn-2400plus -0.7%)  
  632 (r 0.43): Rxa1 13.Qxa1 Nbd7 14.O-O Qc7 15. -&gt; Bxc7  
  -> 1214 (r 0.55): cxd5 9.Qxd5 Qe7+ 10.Be3 Be6 11. -&gt; Bb5+
- **15201 -> 1214** (chess-pgn-1000-1300 +6.8%, chess-pgn-2400plus +2.2%)  
  15201 (r 0.55): Nf6 4.Nc3 Bc5 5.d3 Nd4 6.Nxe5 -&gt; O-O  
  -> 1214 (r 0.55): cxd5 9.Qxd5 Qe7+ 10.Be3 Be6 11. -&gt; Bb5+
- **640 -> 1214** (chess-pgn-1000-1300 +5.9%, chess-pgn-2400plus +2.3%)  
  640 (r 0.42): Nf6 4.e3 e6 5.c3 Bd6 6.Ne5 -&gt; Bxe5  
  -> 1214 (r 0.55): cxd5 9.Qxd5 Qe7+ 10.Be3 Be6 11. -&gt; Bb5+
- **14599 -> 1214** (chess-pgn-1000-1300 +4.4%, chess-pgn-2400plus +1.4%)  
  14599 (r 0.55): d6 4.d4 a6 5.Bxc6+ bxc6 6.dxe5 -&gt; dxe5  
  -> 1214 (r 0.55): cxd5 9.Qxd5 Qe7+ 10.Be3 Be6 11. -&gt; Bb5+
- **632 -> 11585** (chess-pgn-1000-1300 +39.9%, chess-pgn-2400plus +11.0%)  
  632 (r 0.43): Rxa1 13.Qxa1 Nbd7 14.O-O Qc7 15. -&gt; Bxc7  
  -> 11585 (r 0.58): d5 4.Bh5 Nf6 5.Qg4 Nxg4 6.Bxg4 -&gt; Bxg4
- **609 -> 1214** (chess-pgn-1000-1300 +7.7%, chess-pgn-2400plus +4.5%)  
  609 (r 0.54): e6 6.c3 Bd6 7.Ne5 Nxe5 8.dxe5 -&gt; Bxe5  
  -> 1214 (r 0.55): cxd5 9.Qxd5 Qe7+ 10.Be3 Be6 11. -&gt; Bb5+
- **632 -> 9976** (chess-pgn-1000-1300 -1.5%, chess-pgn-2400plus -1.2%)  
  632 (r 0.43): Rxa1 13.Qxa1 Nbd7 14.O-O Qc7 15. -&gt; Bxc7  
  -> 9976 (r 0.59): Be7 13.Ne4 Nxe4 14.Bxe7 Qxe7 15. -&gt; Qxe4
- **11489 -> 1214** (chess-pgn-1000-1300 +10.9%, chess-pgn-2400plus +10.3%)  
  11489 (r 0.55): bxc6 6.Nf3 Nf6 7.d4 e5 8.dxe5 -&gt; Ng4  
  -> 1214 (r 0.55): cxd5 9.Qxd5 Qe7+ 10.Be3 Be6 11. -&gt; Bb5+

### diff mode 7: 0.8% of the matrix

- **12713 -> 9696** (chess-pgn-1000-1300 -2.3%, chess-pgn-2400plus -1.4%)  
  12713 (r 0.64): a4 12.Bc2 O-O 13.d4 Nbd7 14.Qe2 -&gt; Ba6  
  -> 9696 (r 0.66): Re7 21.Rh2 Qd6 22.Rb1 Nd3+ 23.cxd3 -&gt; Qxh2
- **14172 -> 9696** (chess-pgn-1000-1300 -1.4%, chess-pgn-2400plus -0.4%)  
  14172 (r 0.47): g6 4.Qxe5+ Ne7 5.Qxh8+ Ng8 6. -&gt; Qxg8+  
  -> 9696 (r 0.66): Re7 21.Rh2 Qd6 22.Rb1 Nd3+ 23.cxd3 -&gt; Qxh2
- **1341 -> 9696** (chess-pgn-1000-1300 +2.8%, chess-pgn-2400plus +1.3%)  
  1341 (r 0.50): Nf6 4.d4 d6 5.Bg5 Be7 6.Bxf6 -&gt; Bxf6  
  -> 9696 (r 0.66): Re7 21.Rh2 Qd6 22.Rb1 Nd3+ 23.cxd3 -&gt; Qxh2
- **4263 -> 9696** (chess-pgn-1000-1300 +1.2%, chess-pgn-2400plus +0.9%)  
  4263 (r 0.57): dxe4 4.f3 exf3 5.Qxf3 Bg4 6.Qxb7 -&gt; Nbd7  
  -> 9696 (r 0.66): Re7 21.Rh2 Qd6 22.Rb1 Nd3+ 23.cxd3 -&gt; Qxh2
- **440 -> 9696** (chess-pgn-1000-1300 -1.4%, chess-pgn-2400plus +0.8%)  
  440 (r 0.33): Qh4 5.g3 Qxe4+ 6.Be2 Qxh1 7.Bb5 -&gt; Qxg1+  
  -> 9696 (r 0.66): Re7 21.Rh2 Qd6 22.Rb1 Nd3+ 23.cxd3 -&gt; Qxh2
- **6830 -> 9696** (chess-pgn-1000-1300 -1.1%, chess-pgn-2400plus -0.9%)  
  6830 (r 0.59): Bg7 4.Be2 Nf6 5.O-O O-O 6. -&gt; d3  
  -> 9696 (r 0.66): Re7 21.Rh2 Qd6 22.Rb1 Nd3+ 23.cxd3 -&gt; Qxh2
- **1566 -> 9696** (chess-pgn-1000-1300 -0.3%, chess-pgn-2400plus +0.2%)  
  1566 (r 0.55): Bxf3 7.Qxf3 Nbd7 8.d4 c6 9.e5 -&gt; dxe5  
  -> 9696 (r 0.66): Re7 21.Rh2 Qd6 22.Rb1 Nd3+ 23.cxd3 -&gt; Qxh2
- **16044 -> 9696** (chess-pgn-1000-1300 -0.9%, chess-pgn-2400plus -0.7%)  
  16044 (r 0.60): Nc6 5.dxc6 bxc6 6.Nf3 d5 7. -&gt; e5  
  -> 9696 (r 0.66): Re7 21.Rh2 Qd6 22.Rb1 Nd3+ 23.cxd3 -&gt; Qxh2

### diff mode 8: 0.8% of the matrix

- **7687 -> 3221** (chess-pgn-1000-1300 +35.7%, chess-pgn-2400plus +22.6%)  
  7687 (r 0.49): Nxc6 12.Bxc5 dxc5 13.Be2 Bb7 14. -&gt; Qc2  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **4973 -> 3221** (chess-pgn-1000-1300 -1.1%, chess-pgn-2400plus -1.0%)  
  4973 (r 0.57): Nf6 4.O-O Nc6 5.c3 d6 6.d4 -&gt; Bb6  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **12674 -> 3221** (chess-pgn-1000-1300 +43.5%, chess-pgn-2400plus +29.7%)  
  12674 (r 0.55): d6 5.exd6 cxd6 6.Bxd6 Qd7 7.Bxf8 -&gt; Qxd1+  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **2067 -> 3221** (chess-pgn-1000-1300 +32.0%, chess-pgn-2400plus +22.2%)  
  2067 (r 0.61): O-O 7.Bxf6 Bxf6 8.Nxe4 Bxe5 9.dxe5 -&gt; Qxd1+  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **13528 -> 3221** (chess-pgn-1000-1300 +34.7%, chess-pgn-2400plus +24.8%)  
  13528 (r 0.42): d6 7.e5 Nxe5 8.Nxe5 dxe5 9. -&gt; Bxf7+  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **12713 -> 3221** (chess-pgn-1000-1300 -1.6%, chess-pgn-2400plus -1.3%)  
  12713 (r 0.64): a4 12.Bc2 O-O 13.d4 Nbd7 14.Qe2 -&gt; Ba6  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **12765 -> 3221** (chess-pgn-1000-1300 +44.8%, chess-pgn-2400plus +31.4%)  
  12765 (r 0.46): Bg4 4.h3 Bxf3 5.Qxf3 Qf6 6. -&gt; Qg4  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **7687 -> 5615** (chess-pgn-1000-1300 +0.2%, chess-pgn-2400plus -0.2%)  
  7687 (r 0.49): Nxc6 12.Bxc5 dxc5 13.Be2 Bb7 14. -&gt; Qc2  
  -> 5615 (r 0.47): Be6 20.Rxc7 Bb3 21.Rc8+ Rxc8 22. -&gt; Ba6

### diff mode 9: 0.7% of the matrix

- **4167 -> 9458** (chess-pgn-1000-1300 +27.0%, chess-pgn-2400plus +13.4%)  
  4167 (r 0.56): Nxd4 6.Qxd4 b6 7.Bg5 h6 8. -&gt; O-O-O  
  -> 9458 (r 0.53): Bxe2 11.Qxe2 e5 12.Bg5 exd4 13.Bxf6 -&gt; Qxf6
- **4167 -> 4274** (chess-pgn-1000-1300 -5.1%, chess-pgn-2400plus -4.0%)  
  4167 (r 0.56): Nxd4 6.Qxd4 b6 7.Bg5 h6 8. -&gt; O-O-O  
  -> 4274 (r 0.48): d6 7.Qd2 dxe5 8.Nxe5 Bxe5 9.dxe5 -&gt; Qxd2+
- **4167 -> 7056** (chess-pgn-1000-1300 +27.1%, chess-pgn-2400plus +11.7%)  
  4167 (r 0.56): Nxd4 6.Qxd4 b6 7.Bg5 h6 8. -&gt; O-O-O  
  -> 7056 (r 0.47): h4 23.gxh4 Bg4 24.Bg2 Bxf3 25.Bxf3 -&gt; Nh6
- **4167 -> 421** (chess-pgn-1000-1300 +25.9%, chess-pgn-2400plus +11.5%)  
  4167 (r 0.56): Nxd4 6.Qxd4 b6 7.Bg5 h6 8. -&gt; O-O-O  
  -> 421 (r 0.44): Qxd1+ 11.Rxd1 Nxe4 12.Nxe4 Bxf3 13. -&gt; gxf3
- **4167 -> 3758** (chess-pgn-1000-1300 +9.7%, chess-pgn-2400plus +5.3%)  
  4167 (r 0.56): Nxd4 6.Qxd4 b6 7.Bg5 h6 8. -&gt; O-O-O  
  -> 3758 (r 0.48): exd4 4.Ng5 Qf6 5.h4 h6 6. -&gt; Nf3
- **12852 -> 9458** (chess-pgn-1000-1300 +23.3%, chess-pgn-2400plus +11.9%)  
  12852 (r 0.59): Nf6 4.Nf3 Be7 5.Bg5 h6 6. -&gt; Bf4  
  -> 9458 (r 0.53): Bxe2 11.Qxe2 e5 12.Bg5 exd4 13.Bxf6 -&gt; Qxf6
- **3004 -> 9458** (chess-pgn-1000-1300 +0.8%, chess-pgn-2400plus +1.4%)  
  3004 (r 0.47): cxd4 4.Qxd4 Nf6 5.e4 Nc6 6.e5 -&gt; Nxd4  
  -> 9458 (r 0.53): Bxe2 11.Qxe2 e5 12.Bg5 exd4 13.Bxf6 -&gt; Qxf6
- **7230 -> 9458** (chess-pgn-1000-1300 +24.7%, chess-pgn-2400plus +14.6%)  
  7230 (r 0.53): a6 4.Bxc6 dxc6 5.O-O Bg4 6.h3 -&gt; h5  
  -> 9458 (r 0.53): Bxe2 11.Qxe2 e5 12.Bg5 exd4 13.Bxf6 -&gt; Qxf6

### diff mode 10: 0.7% of the matrix

- **4167 -> 7056** (chess-pgn-1000-1300 +27.1%, chess-pgn-2400plus +11.7%)  
  4167 (r 0.56): Nxd4 6.Qxd4 b6 7.Bg5 h6 8. -&gt; O-O-O  
  -> 7056 (r 0.47): h4 23.gxh4 Bg4 24.Bg2 Bxf3 25.Bxf3 -&gt; Nh6
- **4167 -> 9458** (chess-pgn-1000-1300 +27.0%, chess-pgn-2400plus +13.4%)  
  4167 (r 0.56): Nxd4 6.Qxd4 b6 7.Bg5 h6 8. -&gt; O-O-O  
  -> 9458 (r 0.53): Bxe2 11.Qxe2 e5 12.Bg5 exd4 13.Bxf6 -&gt; Qxf6
- **4167 -> 421** (chess-pgn-1000-1300 +25.9%, chess-pgn-2400plus +11.5%)  
  4167 (r 0.56): Nxd4 6.Qxd4 b6 7.Bg5 h6 8. -&gt; O-O-O  
  -> 421 (r 0.44): Qxd1+ 11.Rxd1 Nxe4 12.Nxe4 Bxf3 13. -&gt; gxf3
- **12852 -> 7056** (chess-pgn-1000-1300 +22.7%, chess-pgn-2400plus +10.6%)  
  12852 (r 0.59): Nf6 4.Nf3 Be7 5.Bg5 h6 6. -&gt; Bf4  
  -> 7056 (r 0.47): h4 23.gxh4 Bg4 24.Bg2 Bxf3 25.Bxf3 -&gt; Nh6
- **11312 -> 7056** (chess-pgn-1000-1300 +20.0%, chess-pgn-2400plus +8.6%)  
  11312 (r 0.63): Bd6 6.Bd3 O-O 7.O-O Bg4 8.h3 -&gt; Bh5  
  -> 7056 (r 0.47): h4 23.gxh4 Bg4 24.Bg2 Bxf3 25.Bxf3 -&gt; Nh6
- **7230 -> 7056** (chess-pgn-1000-1300 +26.3%, chess-pgn-2400plus +13.5%)  
  7230 (r 0.53): a6 4.Bxc6 dxc6 5.O-O Bg4 6.h3 -&gt; h5  
  -> 7056 (r 0.47): h4 23.gxh4 Bg4 24.Bg2 Bxf3 25.Bxf3 -&gt; Nh6
- **1341 -> 7056** (chess-pgn-1000-1300 +55.7%, chess-pgn-2400plus +28.5%)  
  1341 (r 0.50): Nf6 4.d4 d6 5.Bg5 Be7 6.Bxf6 -&gt; Bxf6  
  -> 7056 (r 0.47): h4 23.gxh4 Bg4 24.Bg2 Bxf3 25.Bxf3 -&gt; Nh6
- **12852 -> 9458** (chess-pgn-1000-1300 +23.3%, chess-pgn-2400plus +11.9%)  
  12852 (r 0.59): Nf6 4.Nf3 Be7 5.Bg5 h6 6. -&gt; Bf4  
  -> 9458 (r 0.53): Bxe2 11.Qxe2 e5 12.Bg5 exd4 13.Bxf6 -&gt; Qxf6

### diff mode 11: 0.6% of the matrix

- **16125 -> 8041** (chess-pgn-1000-1300 +16.8%, chess-pgn-2400plus +3.4%)  
  16125 (r 0.54): Nxd5 6.Nxf7 Kxf7 7.Qf3+ Ke6 8.Nc3 -&gt; Nb4  
  -> 8041 (r 0.62): O-O 9.f3 exf3 10.Bxf3 d4 11.exd4 -&gt; Bxd4+
- **16125 -> 13656** (chess-pgn-1000-1300 -0.9%, chess-pgn-2400plus -0.6%)  
  16125 (r 0.54): Nxd5 6.Nxf7 Kxf7 7.Qf3+ Ke6 8.Nc3 -&gt; Nb4  
  -> 13656 (r 0.72): Bb4 14.Re2 Ba6 15.Rb2 Bc3 16.a5 -&gt; Bxb2
- **16125 -> 12934** (chess-pgn-1000-1300 +7.0%, chess-pgn-2400plus +1.5%)  
  16125 (r 0.54): Nxd5 6.Nxf7 Kxf7 7.Qf3+ Ke6 8.Nc3 -&gt; Nb4  
  -> 12934 (r 0.56): Kxf7 4.Nf3 d6 5.c3 Bg4 6.Ng5+ -&gt; Kf8
- **1341 -> 8041** (chess-pgn-1000-1300 +4.5%, chess-pgn-2400plus +2.3%)  
  1341 (r 0.50): Nf6 4.d4 d6 5.Bg5 Be7 6.Bxf6 -&gt; Bxf6  
  -> 8041 (r 0.62): O-O 9.f3 exf3 10.Bxf3 d4 11.exd4 -&gt; Bxd4+
- **10065 -> 8041** (chess-pgn-1000-1300 +10.5%, chess-pgn-2400plus +2.9%)  
  10065 (r 0.50): d6 4.Nc3 Bg4 5.h3 Bh5 6.Nxe5 -&gt; Bxd1  
  -> 8041 (r 0.62): O-O 9.f3 exf3 10.Bxf3 d4 11.exd4 -&gt; Bxd4+
- **16125 -> 8787** (chess-pgn-1000-1300 +7.6%, chess-pgn-2400plus +0.9%)  
  16125 (r 0.54): Nxd5 6.Nxf7 Kxf7 7.Qf3+ Ke6 8.Nc3 -&gt; Nb4  
  -> 8787 (r 0.54): d5 5.exd5 Nd4 6.c3 h6 7. -&gt; cxd4
- **4596 -> 8041** (chess-pgn-1000-1300 +7.3%, chess-pgn-2400plus +3.7%)  
  4596 (r 0.55): Nxd5 6.Nxf7 Kxf7 7.Qf3+ Ke6 8. -&gt; Bxd5+  
  -> 8041 (r 0.62): O-O 9.f3 exf3 10.Bxf3 d4 11.exd4 -&gt; Bxd4+
- **16125 -> 6295** (chess-pgn-1000-1300 +5.7%, chess-pgn-2400plus -1.0%)  
  16125 (r 0.54): Nxd5 6.Nxf7 Kxf7 7.Qf3+ Ke6 8.Nc3 -&gt; Nb4  
  -> 6295 (r 0.57): O-O 12.Qe2 d4 13.exd4 cxd4 14.cxd4 -&gt; Nfxd4

### diff mode 12: 0.6% of the matrix

- **11616 -> 4274** (chess-pgn-1000-1300 +14.4%, chess-pgn-2400plus +4.6%)  
  11616 (r 0.55): e6 4.Bxc4 Nf6 5.Nc3 Bb4 6. -&gt; Qa4+  
  -> 4274 (r 0.48): d6 7.Qd2 dxe5 8.Nxe5 Bxe5 9.dxe5 -&gt; Qxd2+
- **5437 -> 4274** (chess-pgn-1000-1300 +19.4%, chess-pgn-2400plus +4.5%)  
  5437 (r 0.45): Bb4 7.Bd3 Nxd4 8.Nxd4 Qxd4 9.Bb5+ -&gt; c6  
  -> 4274 (r 0.48): d6 7.Qd2 dxe5 8.Nxe5 Bxe5 9.dxe5 -&gt; Qxd2+
- **13453 -> 4274** (chess-pgn-1000-1300 +10.8%, chess-pgn-2400plus +5.6%)  
  13453 (r 0.49): e6 5.d4 Nf6 6.Bd3 Bb4 7. -&gt; Bg5  
  -> 4274 (r 0.48): d6 7.Qd2 dxe5 8.Nxe5 Bxe5 9.dxe5 -&gt; Qxd2+
- **13494 -> 4274** (chess-pgn-1000-1300 +7.4%, chess-pgn-2400plus +1.8%)  
  13494 (r 0.55): exd5 4.Nc3 Nf6 5.Nf3 Bb4 6. -&gt; Bd2  
  -> 4274 (r 0.48): d6 7.Qd2 dxe5 8.Nxe5 Bxe5 9.dxe5 -&gt; Qxd2+
- **2567 -> 4274** (chess-pgn-1000-1300 +8.5%, chess-pgn-2400plus +2.5%)  
  2567 (r 0.57): Bc5 4.fxe5 Ng8 5.d4 Bb4 6. -&gt; Nf3  
  -> 4274 (r 0.48): d6 7.Qd2 dxe5 8.Nxe5 Bxe5 9.dxe5 -&gt; Qxd2+
- **12073 -> 4274** (chess-pgn-1000-1300 +22.2%, chess-pgn-2400plus +14.0%)  
  12073 (r 0.60): a6 6.Nc3 Bb4 7.O-O O-O 8.a3 -&gt; Bd6  
  -> 4274 (r 0.48): d6 7.Qd2 dxe5 8.Nxe5 Bxe5 9.dxe5 -&gt; Qxd2+
- **15103 -> 4274** (chess-pgn-1000-1300 +14.3%, chess-pgn-2400plus +8.9%)  
  15103 (r 0.56): Nf6 4.Bc4 Nxe4 5.Nxe4 d5 6.Bb5 -&gt; dxe4  
  -> 4274 (r 0.48): d6 7.Qd2 dxe5 8.Nxe5 Bxe5 9.dxe5 -&gt; Qxd2+
- **4482 -> 4274** (chess-pgn-1000-1300 +23.0%, chess-pgn-2400plus +15.3%)  
  4482 (r 0.56): Nc6 4.Nc3 Bb4 5.Bd2 O-O 6.a3 -&gt; Bxc3  
  -> 4274 (r 0.48): d6 7.Qd2 dxe5 8.Nxe5 Bxe5 9.dxe5 -&gt; Qxd2+

### diff mode 13: 0.6% of the matrix

- **4173 -> 15990** (chess-pgn-1000-1300 +3.9%, chess-pgn-2400plus +3.2%)  
  4173 (r 0.55): Bc5 6.d3 h6 7.c3 O-O 8.Bxc6 -&gt; bxc6  
  -> 15990 (r 0.48): Ng3 12.Rg1 Nf5 13.O-O-O Nxe3 14.Qxe3 -&gt; Bxa3
- **4173 -> 10827** (chess-pgn-1000-1300 -2.6%, chess-pgn-2400plus -1.0%)  
  4173 (r 0.55): Bc5 6.d3 h6 7.c3 O-O 8.Bxc6 -&gt; bxc6  
  -> 10827 (r 0.78): a6 16.c3 Bc5 17.b4 axb5 18. -&gt; bxc5
- **3435 -> 15990** (chess-pgn-1000-1300 -0.6%, chess-pgn-2400plus +7.7%)  
  3435 (r 0.54): Nc6 4.Bd3 Bg4 5.Nbd2 e5 6. -&gt; c3  
  -> 15990 (r 0.48): Ng3 12.Rg1 Nf5 13.O-O-O Nxe3 14.Qxe3 -&gt; Bxa3
- **3435 -> 10827** (chess-pgn-1000-1300 +11.1%, chess-pgn-2400plus +4.1%)  
  3435 (r 0.54): Nc6 4.Bd3 Bg4 5.Nbd2 e5 6. -&gt; c3  
  -> 10827 (r 0.78): a6 16.c3 Bc5 17.b4 axb5 18. -&gt; bxc5
- **11804 -> 15990** (chess-pgn-1000-1300 +22.3%, chess-pgn-2400plus +16.5%)  
  11804 (r 0.57): Bc5 4.Bc4 Ng4 5.O-O Nxf2 6. -&gt; Rxf2  
  -> 15990 (r 0.48): Ng3 12.Rg1 Nf5 13.O-O-O Nxe3 14.Qxe3 -&gt; Bxa3
- **11804 -> 10827** (chess-pgn-1000-1300 -4.7%, chess-pgn-2400plus -2.8%)  
  11804 (r 0.57): Bc5 4.Bc4 Ng4 5.O-O Nxf2 6. -&gt; Rxf2  
  -> 10827 (r 0.78): a6 16.c3 Bc5 17.b4 axb5 18. -&gt; bxc5
- **15201 -> 15990** (chess-pgn-1000-1300 +10.0%, chess-pgn-2400plus +7.6%)  
  15201 (r 0.55): Nf6 4.Nc3 Bc5 5.d3 Nd4 6.Nxe5 -&gt; O-O  
  -> 15990 (r 0.48): Ng3 12.Rg1 Nf5 13.O-O-O Nxe3 14.Qxe3 -&gt; Bxa3
- **15201 -> 10827** (chess-pgn-1000-1300 +0.8%, chess-pgn-2400plus +2.3%)  
  15201 (r 0.55): Nf6 4.Nc3 Bc5 5.d3 Nd4 6.Nxe5 -&gt; O-O  
  -> 10827 (r 0.78): a6 16.c3 Bc5 17.b4 axb5 18. -&gt; bxc5

### diff mode 14: 0.5% of the matrix

- **640 -> 15990** (chess-pgn-1000-1300 +10.9%, chess-pgn-2400plus +3.4%)  
  640 (r 0.42): Nf6 4.e3 e6 5.c3 Bd6 6.Ne5 -&gt; Bxe5  
  -> 15990 (r 0.48): Ng3 12.Rg1 Nf5 13.O-O-O Nxe3 14.Qxe3 -&gt; Bxa3
- **640 -> 5626** (chess-pgn-1000-1300 +16.5%, chess-pgn-2400plus +0.7%)  
  640 (r 0.42): Nf6 4.e3 e6 5.c3 Bd6 6.Ne5 -&gt; Bxe5  
  -> 5626 (r 0.44): O-O 11.h3 a5 12.O-O a4 13. -&gt; Ba2
- **640 -> 8648** (chess-pgn-1000-1300 -0.4%, chess-pgn-2400plus +0.0%)  
  640 (r 0.42): Nf6 4.e3 e6 5.c3 Bd6 6.Ne5 -&gt; Bxe5  
  -> 8648 (r 0.58): Rxd2 20.Bxd2 Ne5 21.Nxe5 dxe5 22. -&gt; Bc4
- **640 -> 14959** (chess-pgn-1000-1300 -1.2%, chess-pgn-2400plus -0.7%)  
  640 (r 0.42): Nf6 4.e3 e6 5.c3 Bd6 6.Ne5 -&gt; Bxe5  
  -> 14959 (r 0.80): f5 6.Nc3 fxe4 7.Nxe4 Bf5 8.Qe2 -&gt; Nd7
- **640 -> 11585** (chess-pgn-1000-1300 -0.8%, chess-pgn-2400plus -0.5%)  
  640 (r 0.42): Nf6 4.e3 e6 5.c3 Bd6 6.Ne5 -&gt; Bxe5  
  -> 11585 (r 0.58): d5 4.Bh5 Nf6 5.Qg4 Nxg4 6.Bxg4 -&gt; Bxg4
- **640 -> 10756** (chess-pgn-1000-1300 +23.6%, chess-pgn-2400plus +11.5%)  
  640 (r 0.42): Nf6 4.e3 e6 5.c3 Bd6 6.Ne5 -&gt; Bxe5  
  -> 10756 (r 0.51): hxg4 31.Qh4+ Kg8 32.Qxg4 Qxg4 33. -&gt; fxg4
- **640 -> 1773** (chess-pgn-1000-1300 +4.9%, chess-pgn-2400plus -0.1%)  
  640 (r 0.42): Nf6 4.e3 e6 5.c3 Bd6 6.Ne5 -&gt; Bxe5  
  -> 1773 (r 0.76): Nxe5 8.Qxe5 d6 9.Qf5 Bxf5 10. -&gt; f3
- **3816 -> 4274** (chess-pgn-1000-1300 -1.7%, chess-pgn-2400plus -1.2%)  
  3816 (r 0.45): bxc6 5.Nxe5 Nxe4 6.Qe2 Nf6 7. -&gt; Nxc6+  
  -> 4274 (r 0.48): d6 7.Qd2 dxe5 8.Nxe5 Bxe5 9.dxe5 -&gt; Qxd2+

## chess-pgn-1000-1300

### chess-pgn-1000-1300 mode 0: 8.7% of the matrix

- **2694 -> 1773** (chess-pgn-1000-1300 +33.9%, chess-pgn-2400plus +27.1%)  
  2694 (r 0.58): Qxf6 8.Nd5 Qg6 9.Rg1 Be6 10.Ne7+ -&gt; Kh7  
  -> 1773 (r 0.76): Nxe5 8.Qxe5 d6 9.Qf5 Bxf5 10. -&gt; f3
- **1804 -> 1773** (chess-pgn-1000-1300 +18.2%, chess-pgn-2400plus +13.3%)  
  1804 (r 0.56): Nc6 9.Bg5 Nd4 10.Bxf6 Ne2+ 11. -&gt; Kh1  
  -> 1773 (r 0.76): Nxe5 8.Qxe5 d6 9.Qf5 Bxf5 10. -&gt; f3
- **133 -> 1773** (chess-pgn-1000-1300 +24.5%, chess-pgn-2400plus +17.4%)  
  133 (r 0.49): cxd5 19.Nxd5 Be6 20.Be3 Qf5 21.Ne7+ -&gt; Kh8  
  -> 1773 (r 0.76): Nxe5 8.Qxe5 d6 9.Qf5 Bxf5 10. -&gt; f3
- **10442 -> 1773** (chess-pgn-1000-1300 +29.9%, chess-pgn-2400plus +20.1%)  
  10442 (r 0.47): Nxf4 36.Rxe5 Rxe5 37.Qf2 Nxh3+ 38.Kf1 -&gt; Qxf2#  
  -> 1773 (r 0.76): Nxe5 8.Qxe5 d6 9.Qf5 Bxf5 10. -&gt; f3
- **2694 -> 11585** (chess-pgn-1000-1300 +33.5%, chess-pgn-2400plus +26.4%)  
  2694 (r 0.58): Qxf6 8.Nd5 Qg6 9.Rg1 Be6 10.Ne7+ -&gt; Kh7  
  -> 11585 (r 0.58): d5 4.Bh5 Nf6 5.Qg4 Nxg4 6.Bxg4 -&gt; Bxg4
- **5454 -> 1773** (chess-pgn-1000-1300 +25.7%, chess-pgn-2400plus +20.7%)  
  5454 (r 0.46): Qc7 7.Qh5 Bd6 8.Bf4 Nf6 9.Qxf7+ -&gt; Qxf7  
  -> 1773 (r 0.76): Nxe5 8.Qxe5 d6 9.Qf5 Bxf5 10. -&gt; f3
- **7546 -> 1773** (chess-pgn-1000-1300 +19.7%, chess-pgn-2400plus +16.6%)  
  7546 (r 0.56): Bxb5 10.Nxb5 a6 11.Qxd5 Qxd5 12.Nc7+ -&gt; Kf8  
  -> 1773 (r 0.76): Nxe5 8.Qxe5 d6 9.Qf5 Bxf5 10. -&gt; f3
- **2694 -> 1144** (chess-pgn-1000-1300 +23.0%, chess-pgn-2400plus +16.8%)  
  2694 (r 0.58): Qxf6 8.Nd5 Qg6 9.Rg1 Be6 10.Ne7+ -&gt; Kh7  
  -> 1144 (r 0.73): Ng4 20.Bxg4 Nd3 21.Qxd3 Rac8 22.Nxe8 -&gt; Rc7

### chess-pgn-1000-1300 mode 1: 3.6% of the matrix

- **8886 -> 1773** (chess-pgn-1000-1300 -4.9%, chess-pgn-2400plus -1.1%)  
  8886 (r 0.54): h6 9.Nxf7 Rxf7 10.Bxf7+ Kh8 11.Bxh6 -&gt; Bxd4  
  -> 1773 (r 0.76): Nxe5 8.Qxe5 d6 9.Qf5 Bxf5 10. -&gt; f3
- **4693 -> 1773** (chess-pgn-1000-1300 -3.9%, chess-pgn-2400plus -1.6%)  
  4693 (r 0.61): Nf6 6.O-O g5 7.h3 g4 8. -&gt; hxg4  
  -> 1773 (r 0.76): Nxe5 8.Qxe5 d6 9.Qf5 Bxf5 10. -&gt; f3
- **8886 -> 3221** (chess-pgn-1000-1300 -1.2%, chess-pgn-2400plus -2.2%)  
  8886 (r 0.54): h6 9.Nxf7 Rxf7 10.Bxf7+ Kh8 11.Bxh6 -&gt; Bxd4  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **4693 -> 3221** (chess-pgn-1000-1300 -1.6%, chess-pgn-2400plus -1.8%)  
  4693 (r 0.61): Nf6 6.O-O g5 7.h3 g4 8. -&gt; hxg4  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **3034 -> 1773** (chess-pgn-1000-1300 -3.0%, chess-pgn-2400plus -0.5%)  
  3034 (r 0.53): Bg4 6.O-O Nf6 7.h3 Bxh3 8.gxh3 -&gt; Qxh3  
  -> 1773 (r 0.76): Nxe5 8.Qxe5 d6 9.Qf5 Bxf5 10. -&gt; f3
- **3034 -> 3221** (chess-pgn-1000-1300 -2.0%, chess-pgn-2400plus -1.8%)  
  3034 (r 0.53): Bg4 6.O-O Nf6 7.h3 Bxh3 8.gxh3 -&gt; Qxh3  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **8886 -> 11574** (chess-pgn-1000-1300 +32.7%, chess-pgn-2400plus +35.6%)  
  8886 (r 0.54): h6 9.Nxf7 Rxf7 10.Bxf7+ Kh8 11.Bxh6 -&gt; Bxd4  
  -> 11574 (r 0.45): Nh5 14.g4 Bxg5 15.Nxg5 Nhf6 16. -&gt; Nf3
- **4693 -> 11574** (chess-pgn-1000-1300 +29.4%, chess-pgn-2400plus +31.4%)  
  4693 (r 0.61): Nf6 6.O-O g5 7.h3 g4 8. -&gt; hxg4  
  -> 11574 (r 0.45): Nh5 14.g4 Bxg5 15.Nxg5 Nhf6 16. -&gt; Nf3

### chess-pgn-1000-1300 mode 2: 2.9% of the matrix

- **8612 -> 1057** (chess-pgn-1000-1300 -1.2%, chess-pgn-2400plus -0.8%)  
  8612 (r 0.55): Bg4 7.Nxf6+ Qxf6 8.Be2 Nd4 9. -&gt; c3  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **3470 -> 1057** (chess-pgn-1000-1300 -0.6%, chess-pgn-2400plus -0.8%)  
  3470 (r 0.53): h6 14.Be3 Nf4 15.Bxf4 Qxf4 16.Ne5 -&gt; Qg5  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **842 -> 1057** (chess-pgn-1000-1300 -1.1%, chess-pgn-2400plus +0.2%)  
  842 (r 0.52): Nc6 6.c4 Bf5 7.cxd5 Nxd5 8.e4 -&gt; Bxe4  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **3885 -> 1057** (chess-pgn-1000-1300 +49.0%, chess-pgn-2400plus +42.0%)  
  3885 (r 0.58): Qxg5 5.d3 Qxg2 6.Qh5 Qxh1+ 7. -&gt; Ke2  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **6112 -> 1057** (chess-pgn-1000-1300 -0.2%, chess-pgn-2400plus -0.4%)  
  6112 (r 0.62): Bg4 7.d5 O-O-O 8.c4 e5 9.Nh4 -&gt; Bxe2  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **4721 -> 1057** (chess-pgn-1000-1300 -0.6%, chess-pgn-2400plus -0.3%)  
  4721 (r 0.54): d6 4.d4 exd4 5.Nxd4 Bd7 6.Nc3 -&gt; Nxd4  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **1624 -> 1057** (chess-pgn-1000-1300 -0.4%, chess-pgn-2400plus -0.4%)  
  1624 (r 0.61): Be7 7.e3 O-O 8.Be2 Ne4 9. -&gt; Bxe7  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **8325 -> 1057** (chess-pgn-1000-1300 -2.3%, chess-pgn-2400plus -1.4%)  
  8325 (r 0.52): O-O 7.Re1 Na5 8.Bxf7+ Rxf7 9.b4 -&gt; Bxf2+  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6

### chess-pgn-1000-1300 mode 3: 2.8% of the matrix

- **13650 -> 3221** (chess-pgn-1000-1300 +41.0%, chess-pgn-2400plus +47.0%)  
  13650 (r 0.50): Rxa8 38.Qxa8+ Kh7 39.Qe8 Qe4+ 40.Qxe4+ -&gt; dxe4  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **13650 -> 15990** (chess-pgn-1000-1300 +5.1%, chess-pgn-2400plus +4.2%)  
  13650 (r 0.50): Rxa8 38.Qxa8+ Kh7 39.Qe8 Qe4+ 40.Qxe4+ -&gt; dxe4  
  -> 15990 (r 0.48): Ng3 12.Rg1 Nf5 13.O-O-O Nxe3 14.Qxe3 -&gt; Bxa3
- **9540 -> 3221** (chess-pgn-1000-1300 +66.1%, chess-pgn-2400plus +66.2%)  
  9540 (r 0.42): Bd6 12.f4 Qg3+ 13.Qf2 Qxf2+ 14. -&gt; Kxf2  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **9540 -> 15990** (chess-pgn-1000-1300 +4.0%, chess-pgn-2400plus +4.7%)  
  9540 (r 0.42): Bd6 12.f4 Qg3+ 13.Qf2 Qxf2+ 14. -&gt; Kxf2  
  -> 15990 (r 0.48): Ng3 12.Rg1 Nf5 13.O-O-O Nxe3 14.Qxe3 -&gt; Bxa3
- **13650 -> 1936** (chess-pgn-1000-1300 +40.3%, chess-pgn-2400plus +43.3%)  
  13650 (r 0.50): Rxa8 38.Qxa8+ Kh7 39.Qe8 Qe4+ 40.Qxe4+ -&gt; dxe4  
  -> 1936 (r 0.49): Rg7 35.Qxe4 Qxe4 36.Rxe4 Bxf1 37.Kxf1 -&gt; Rf7
- **10103 -> 3221** (chess-pgn-1000-1300 +54.9%, chess-pgn-2400plus +58.8%)  
  10103 (r 0.44): Bg4 13.h3 Bxf3 14.Qxf3 Qxf3 15. -&gt; Nxf3  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **10103 -> 15990** (chess-pgn-1000-1300 +2.3%, chess-pgn-2400plus +3.3%)  
  10103 (r 0.44): Bg4 13.h3 Bxf3 14.Qxf3 Qxf3 15. -&gt; Nxf3  
  -> 15990 (r 0.48): Ng3 12.Rg1 Nf5 13.O-O-O Nxe3 14.Qxe3 -&gt; Bxa3
- **1256 -> 3221** (chess-pgn-1000-1300 -1.4%, chess-pgn-2400plus -1.0%)  
  1256 (r 0.51): Bd7 10.Bb1 b5 11.a3 b4 12. -&gt; axb4  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8

### chess-pgn-1000-1300 mode 4: 1.9% of the matrix

- **1256 -> 1057** (chess-pgn-1000-1300 -2.0%, chess-pgn-2400plus -1.3%)  
  1256 (r 0.51): Bd7 10.Bb1 b5 11.a3 b4 12. -&gt; axb4  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **9041 -> 1057** (chess-pgn-1000-1300 -1.4%, chess-pgn-2400plus -1.0%)  
  9041 (r 0.46): c6 4.Nf3 b5 5.a4 a6 6. -&gt; axb5  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **15060 -> 1057** (chess-pgn-1000-1300 -2.2%, chess-pgn-2400plus -2.0%)  
  15060 (r 0.53): O-O 11.a4 Bd7 12.c3 b5 13. -&gt; axb5  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **1130 -> 1057** (chess-pgn-1000-1300 -1.8%, chess-pgn-2400plus -1.3%)  
  1130 (r 0.56): b6 10.b4 a5 11.a3 axb4 12. -&gt; axb4  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **15012 -> 1057** (chess-pgn-1000-1300 -2.8%, chess-pgn-2400plus -2.0%)  
  15012 (r 0.53): b5 6.Bb3 a5 7.a3 b4 8. -&gt; a4  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **8508 -> 1057** (chess-pgn-1000-1300 -1.1%, chess-pgn-2400plus -0.5%)  
  8508 (r 0.52): dxc4 4.e3 b5 5.a4 a6 6.axb5 -&gt; Bb7  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **7060 -> 1057** (chess-pgn-1000-1300 -2.3%, chess-pgn-2400plus -1.5%)  
  7060 (r 0.66): g4 18.Ng1 Rdf8 19.a4 e5 20.b5 -&gt; Na7  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **3242 -> 1057** (chess-pgn-1000-1300 -1.3%, chess-pgn-2400plus -0.9%)  
  3242 (r 0.52): c5 6.a3 Ba5 7.b4 cxb4 8. -&gt; Nb5  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6

### chess-pgn-1000-1300 mode 5: 1.6% of the matrix

- **7 -> 15990** (chess-pgn-1000-1300 +1.7%, chess-pgn-2400plus +3.0%)  
  7 (r 0.45): c6 4.Nf3 Bg4 5.Be2 Bxf3 6. -&gt; Bxf3  
  -> 15990 (r 0.48): Ng3 12.Rg1 Nf5 13.O-O-O Nxe3 14.Qxe3 -&gt; Bxa3
- **7 -> 6774** (chess-pgn-1000-1300 -30.9%, chess-pgn-2400plus -31.2%)  
  7 (r 0.45): c6 4.Nf3 Bg4 5.Be2 Bxf3 6. -&gt; Bxf3  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3
- **7 -> 7056** (chess-pgn-1000-1300 +64.6%, chess-pgn-2400plus +57.8%)  
  7 (r 0.45): c6 4.Nf3 Bg4 5.Be2 Bxf3 6. -&gt; Bxf3  
  -> 7056 (r 0.47): h4 23.gxh4 Bg4 24.Bg2 Bxf3 25.Bxf3 -&gt; Nh6
- **14268 -> 15990** (chess-pgn-1000-1300 +8.2%, chess-pgn-2400plus +8.4%)  
  14268 (r 0.60): Qd8 4.Nf3 Bg4 5.h3 Bxf3 6. -&gt; Qxf3  
  -> 15990 (r 0.48): Ng3 12.Rg1 Nf5 13.O-O-O Nxe3 14.Qxe3 -&gt; Bxa3
- **1341 -> 15990** (chess-pgn-1000-1300 +10.9%, chess-pgn-2400plus +6.4%)  
  1341 (r 0.50): Nf6 4.d4 d6 5.Bg5 Be7 6.Bxf6 -&gt; Bxf6  
  -> 15990 (r 0.48): Ng3 12.Rg1 Nf5 13.O-O-O Nxe3 14.Qxe3 -&gt; Bxa3
- **16032 -> 15990** (chess-pgn-1000-1300 +8.1%, chess-pgn-2400plus +9.5%)  
  16032 (r 0.53): Be7 9.Ne4 h6 10.Nxf6+ Bxf6 11.Bxf6 -&gt; Qxf6  
  -> 15990 (r 0.48): Ng3 12.Rg1 Nf5 13.O-O-O Nxe3 14.Qxe3 -&gt; Bxa3
- **4635 -> 15990** (chess-pgn-1000-1300 +10.2%, chess-pgn-2400plus +10.6%)  
  4635 (r 0.60): Nc6 5.Bd3 Bg4 6.h3 Bxf3 7. -&gt; Qxf3  
  -> 15990 (r 0.48): Ng3 12.Rg1 Nf5 13.O-O-O Nxe3 14.Qxe3 -&gt; Bxa3
- **13861 -> 15990** (chess-pgn-1000-1300 +11.6%, chess-pgn-2400plus +12.8%)  
  13861 (r 0.55): Nc6 4.Be2 Bg4 5.O-O Bxf3 6. -&gt; Bxf3  
  -> 15990 (r 0.48): Ng3 12.Rg1 Nf5 13.O-O-O Nxe3 14.Qxe3 -&gt; Bxa3

### chess-pgn-1000-1300 mode 6: 1.5% of the matrix

- **1254 -> 5077** (chess-pgn-1000-1300 +53.6%, chess-pgn-2400plus +50.2%)  
  1254 (r 0.62): Nb4 5.Qc4 b5 6.Qxb5 Nxc2+ 7. -&gt; Kd2  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **13237 -> 5077** (chess-pgn-1000-1300 +51.8%, chess-pgn-2400plus +49.3%)  
  13237 (r 0.53): Nh6 6.d3 Nd4 7.Qh5 Nxc2+ 8. -&gt; Kd1  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **8859 -> 5077** (chess-pgn-1000-1300 +54.9%, chess-pgn-2400plus +48.3%)  
  8859 (r 0.49): Nf6 5.Nc3 Nd4 6.Qe3 Nxc2+ 7. -&gt; Ke2  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **160 -> 5077** (chess-pgn-1000-1300 +40.2%, chess-pgn-2400plus +23.7%)  
  160 (r 0.49): Nf6 4.e3 Nc6 5.Nb5 a6 6. -&gt; Nc7+  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **3739 -> 5077** (chess-pgn-1000-1300 +45.9%, chess-pgn-2400plus +42.9%)  
  3739 (r 0.54): Qxd4 8.Qxd4 Nxd4 9.Nc3 Nc2+ 10. -&gt; Kd2  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **2205 -> 5077** (chess-pgn-1000-1300 +46.6%, chess-pgn-2400plus +43.4%)  
  2205 (r 0.54): dxc5 10.Nc3 Nd4 11.Qxb7 Nc2+ 12. -&gt; Ke2  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **5660 -> 5077** (chess-pgn-1000-1300 +48.6%, chess-pgn-2400plus +43.9%)  
  5660 (r 0.54): g6 7.Nd5 Qe5 8.Nfe3 Qxe4 9.Nxc7+ -&gt; Kd8  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **2694 -> 5077** (chess-pgn-1000-1300 +55.9%, chess-pgn-2400plus +49.1%)  
  2694 (r 0.58): Qxf6 8.Nd5 Qg6 9.Rg1 Be6 10.Ne7+ -&gt; Kh7  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+

### chess-pgn-1000-1300 mode 7: 1.4% of the matrix

- **15771 -> 15508** (chess-pgn-1000-1300 +1.6%, chess-pgn-2400plus +1.0%)  
  15771 (r 0.58): cxd5 4.Bb5+ Bd7 5.Qe2 Bxb5 6.Qxb5+ -&gt; Qd7  
  -> 15508 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **11051 -> 15508** (chess-pgn-1000-1300 +7.6%, chess-pgn-2400plus +5.9%)  
  11051 (r 0.56): cxd5 4.c4 Nf6 5.Nc3 e6 6.Qa4+ -&gt; Bd7  
  -> 15508 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **10720 -> 15508** (chess-pgn-1000-1300 +7.5%, chess-pgn-2400plus +6.1%)  
  10720 (r 0.50): e6 5.Nfd2 e5 6.dxe5 Nxe5 7.Qb5+ -&gt; c6  
  -> 15508 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **40 -> 15508** (chess-pgn-1000-1300 +8.0%, chess-pgn-2400plus +8.4%)  
  40 (r 0.51): Nxd5 5.Nf3 Nf6 6.d5 Nb4 7.Qa4+ -&gt; c6  
  -> 15508 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **5473 -> 15508** (chess-pgn-1000-1300 +5.0%, chess-pgn-2400plus +3.8%)  
  5473 (r 0.54): Bxd3 4.Qxd3 e6 5.Qb5+ Nc6 6.Qxb7 -&gt; Nf6  
  -> 15508 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **6541 -> 15508** (chess-pgn-1000-1300 +11.4%, chess-pgn-2400plus +9.2%)  
  6541 (r 0.53): Nf6 5.e5 Nc6 6.Qd1 Qa5+ 7. -&gt; Bd2  
  -> 15508 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **15771 -> 326** (chess-pgn-1000-1300 +5.4%, chess-pgn-2400plus +7.7%)  
  15771 (r 0.58): cxd5 4.Bb5+ Bd7 5.Qe2 Bxb5 6.Qxb5+ -&gt; Qd7  
  -> 326 (r 0.45): c6 14.Nb3 Qe5 15.Bf4 Qb5 16.Qxb5 -&gt; cxb5
- **7343 -> 15508** (chess-pgn-1000-1300 +7.3%, chess-pgn-2400plus +9.8%)  
  7343 (r 0.58): Nf6 6.N1c3 d6 7.Nd5 Qa5+ 8. -&gt; b4  
  -> 15508 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5

### chess-pgn-1000-1300 mode 8: 1.3% of the matrix

- **12460 -> 5615** (chess-pgn-1000-1300 +25.2%, chess-pgn-2400plus +24.5%)  
  12460 (r 0.51): O-O 6.O-O d6 7.Re1 h6 8.Nxf7 -&gt; Rxf7  
  -> 5615 (r 0.47): Be6 20.Rxc7 Bb3 21.Rc8+ Rxc8 22. -&gt; Ba6
- **5274 -> 5615** (chess-pgn-1000-1300 +36.9%, chess-pgn-2400plus +26.4%)  
  5274 (r 0.50): Bh5 17.Nh2 Bxe2 18.Rxe2 Ng6 19.Rae1 -&gt; Kf7  
  -> 5615 (r 0.47): Be6 20.Rxc7 Bb3 21.Rc8+ Rxc8 22. -&gt; Ba6
- **12460 -> 3758** (chess-pgn-1000-1300 +1.0%, chess-pgn-2400plus +0.2%)  
  12460 (r 0.51): O-O 6.O-O d6 7.Re1 h6 8.Nxf7 -&gt; Rxf7  
  -> 3758 (r 0.48): exd4 4.Ng5 Qf6 5.h4 h6 6. -&gt; Nf3
- **12460 -> 7056** (chess-pgn-1000-1300 +0.3%, chess-pgn-2400plus +1.3%)  
  12460 (r 0.51): O-O 6.O-O d6 7.Re1 h6 8.Nxf7 -&gt; Rxf7  
  -> 7056 (r 0.47): h4 23.gxh4 Bg4 24.Bg2 Bxf3 25.Bxf3 -&gt; Nh6
- **11839 -> 5615** (chess-pgn-1000-1300 +0.4%, chess-pgn-2400plus +0.9%)  
  11839 (r 0.47): d6 4.d3 Bg4 5.h3 Bxf3 6. -&gt; Qxf3  
  -> 5615 (r 0.47): Be6 20.Rxc7 Bb3 21.Rc8+ Rxc8 22. -&gt; Ba6
- **3928 -> 5615** (chess-pgn-1000-1300 +21.6%, chess-pgn-2400plus +24.5%)  
  3928 (r 0.55): Bxf1 17.Rdxf1 Qxh2 18.Qxd5 Rad8 19.Rxf7 -&gt; Qxd2+  
  -> 5615 (r 0.47): Be6 20.Rxc7 Bb3 21.Rc8+ Rxc8 22. -&gt; Ba6
- **12853 -> 5615** (chess-pgn-1000-1300 -2.2%, chess-pgn-2400plus -0.7%)  
  12853 (r 0.53): Kxf7 7.Qf3+ Kg8 8.Bxd5+ Qxd5 9.Qxd5+ -&gt; Be6  
  -> 5615 (r 0.47): Be6 20.Rxc7 Bb3 21.Rc8+ Rxc8 22. -&gt; Ba6
- **3686 -> 5615** (chess-pgn-1000-1300 +30.4%, chess-pgn-2400plus +27.7%)  
  3686 (r 0.59): Qd4+ 31.Kh1 Qxc3 32.Rg1 Re1 33. -&gt; Qxa7  
  -> 5615 (r 0.47): Be6 20.Rxc7 Bb3 21.Rc8+ Rxc8 22. -&gt; Ba6

### chess-pgn-1000-1300 mode 9: 1.3% of the matrix

- **15103 -> 16081** (chess-pgn-1000-1300 +63.3%, chess-pgn-2400plus +58.5%)  
  15103 (r 0.56): Nf6 4.Bc4 Nxe4 5.Nxe4 d5 6.Bb5 -&gt; dxe4  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **2856 -> 16081** (chess-pgn-1000-1300 +59.9%, chess-pgn-2400plus +53.7%)  
  2856 (r 0.65): e6 5.Bc4 Nc6 6.Nf3 Bb4 7. -&gt; O-O  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **8775 -> 16081** (chess-pgn-1000-1300 +53.9%, chess-pgn-2400plus +48.7%)  
  8775 (r 0.57): Nxe5 5.Nxe5 Qxe5 6.g3 Bb4 7. -&gt; Bf4  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **10502 -> 16081** (chess-pgn-1000-1300 +36.2%, chess-pgn-2400plus +31.5%)  
  10502 (r 0.60): Bxe6 5.d4 Bb4+ 6.Nc3 Ne4 7. -&gt; Qd3  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **5418 -> 16081** (chess-pgn-1000-1300 +34.7%, chess-pgn-2400plus +32.8%)  
  5418 (r 0.50): Bb4 7.e3 d5 8.h3 Ne4 9. -&gt; Ne2  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **8692 -> 16081** (chess-pgn-1000-1300 +42.0%, chess-pgn-2400plus +38.0%)  
  8692 (r 0.54): c6 6.e3 Qa5 7.Qc2 Ne4 8. -&gt; Rc1  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **8419 -> 16081** (chess-pgn-1000-1300 +71.1%, chess-pgn-2400plus +68.6%)  
  8419 (r 0.43): d5 7.Nc3 Be7 8.g3 Bb4 9. -&gt; Bd2  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **13789 -> 16081** (chess-pgn-1000-1300 +55.9%, chess-pgn-2400plus +51.5%)  
  13789 (r 0.53): a6 5.e3 Nf6 6.Nc3 Bb4 7. -&gt; Bd3  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3

### chess-pgn-1000-1300 mode 10: 1.2% of the matrix

- **4137 -> 16081** (chess-pgn-1000-1300 +42.1%, chess-pgn-2400plus +33.3%)  
  4137 (r 0.56): Bb4 5.Bg5 O-O 6.e3 c5 7. -&gt; a3  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **15340 -> 16081** (chess-pgn-1000-1300 -1.0%, chess-pgn-2400plus -0.4%)  
  15340 (r 0.57): Nf6 4.d4 c6 5.dxe5 dxe5 6. -&gt; Qxd8+  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **8419 -> 16081** (chess-pgn-1000-1300 +71.1%, chess-pgn-2400plus +68.6%)  
  8419 (r 0.43): d5 7.Nc3 Be7 8.g3 Bb4 9. -&gt; Bd2  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **2476 -> 16081** (chess-pgn-1000-1300 +1.7%, chess-pgn-2400plus +1.7%)  
  2476 (r 0.51): Bg4 5.Bxc6+ bxc6 6.d4 exd4 7. -&gt; Qxd4  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **6689 -> 16081** (chess-pgn-1000-1300 +55.0%, chess-pgn-2400plus +48.3%)  
  6689 (r 0.67): d5 5.exd5 cxd5 6.Bb3 Bb4 7. -&gt; Bg5  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **661 -> 16081** (chess-pgn-1000-1300 -1.8%, chess-pgn-2400plus -0.8%)  
  661 (r 0.60): O-O 6.h3 e5 7.dxe5 dxe5 8. -&gt; Qxd8  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **5037 -> 16081** (chess-pgn-1000-1300 -2.2%, chess-pgn-2400plus -1.6%)  
  5037 (r 0.58): d6 4.Bg2 e5 5.dxe5 dxe5 6. -&gt; O-O  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **13789 -> 16081** (chess-pgn-1000-1300 +55.9%, chess-pgn-2400plus +51.5%)  
  13789 (r 0.53): a6 5.e3 Nf6 6.Nc3 Bb4 7. -&gt; Bd3  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3

### chess-pgn-1000-1300 mode 11: 1.1% of the matrix

- **1216 -> 6774** (chess-pgn-1000-1300 +68.3%, chess-pgn-2400plus +66.3%)  
  1216 (r 0.41): exd5 4.d4 Nf6 5.Nc3 Be6 6.Bg5 -&gt; Bb4  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3
- **102 -> 6774** (chess-pgn-1000-1300 +52.8%, chess-pgn-2400plus +50.3%)  
  102 (r 0.61): e5 5.Nb5 d6 6.N5c3 Nf6 7.Bg5 -&gt; Be7  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3
- **13362 -> 6774** (chess-pgn-1000-1300 +54.2%, chess-pgn-2400plus +48.1%)  
  13362 (r 0.56): Nc6 5.Nf3 Nf6 6.Qe2 Bg4 7. -&gt; h3  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3
- **16246 -> 6774** (chess-pgn-1000-1300 +65.7%, chess-pgn-2400plus +66.9%)  
  16246 (r 0.49): exd5 4.d4 Bd6 5.Nc3 Ne7 6.Bg5 -&gt; f6  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3
- **987 -> 6774** (chess-pgn-1000-1300 +61.2%, chess-pgn-2400plus +61.5%)  
  987 (r 0.52): e6 4.Nc3 Nf6 5.e5 Nd5 6.Bg5 -&gt; f6  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3
- **4227 -> 6774** (chess-pgn-1000-1300 +52.1%, chess-pgn-2400plus +47.0%)  
  4227 (r 0.62): f6 4.d4 fxe5 5.dxe5 Bg4 6. -&gt; Bb5  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3
- **425 -> 6774** (chess-pgn-1000-1300 +58.2%, chess-pgn-2400plus +54.7%)  
  425 (r 0.54): Qxh2 21.R5g2 Qh3 22.Rg3 Qd7 23.Bg5 -&gt; Nh5  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3
- **10405 -> 6774** (chess-pgn-1000-1300 +49.4%, chess-pgn-2400plus +40.4%)  
  10405 (r 0.65): e6 4.Nf3 Bb4 5.Bd3 Nf6 6.Bg5 -&gt; h6  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3

### chess-pgn-1000-1300 mode 12: 1.1% of the matrix

- **855 -> 16081** (chess-pgn-1000-1300 -1.0%, chess-pgn-2400plus -0.3%)  
  855 (r 0.53): Bg4 4.d4 Bxf3 5.Qxf3 Qxd4 6.Qxb7 -&gt; Qe5+  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **855 -> 4274** (chess-pgn-1000-1300 -1.6%, chess-pgn-2400plus +0.9%)  
  855 (r 0.53): Bg4 4.d4 Bxf3 5.Qxf3 Qxd4 6.Qxb7 -&gt; Qe5+  
  -> 4274 (r 0.48): d6 7.Qd2 dxe5 8.Nxe5 Bxe5 9.dxe5 -&gt; Qxd2+
- **10838 -> 1057** (chess-pgn-1000-1300 +5.0%, chess-pgn-2400plus +4.5%)  
  10838 (r 0.50): Bc5 6.d4 Bxd4 7.c3 Bxf2+ 8. -&gt; Ke2  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **15231 -> 16081** (chess-pgn-1000-1300 -1.8%, chess-pgn-2400plus -0.7%)  
  15231 (r 0.55): fxe6 7.c3 Nf6 8.Qb3 Qe7 9.Qxb7 -&gt; O-O  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **15231 -> 4274** (chess-pgn-1000-1300 -2.4%, chess-pgn-2400plus -1.7%)  
  15231 (r 0.55): fxe6 7.c3 Nf6 8.Qb3 Qe7 9.Qxb7 -&gt; O-O  
  -> 4274 (r 0.48): d6 7.Qd2 dxe5 8.Nxe5 Bxe5 9.dxe5 -&gt; Qxd2+
- **2856 -> 16081** (chess-pgn-1000-1300 +59.9%, chess-pgn-2400plus +53.7%)  
  2856 (r 0.65): e6 5.Bc4 Nc6 6.Nf3 Bb4 7. -&gt; O-O  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **2856 -> 4274** (chess-pgn-1000-1300 +13.2%, chess-pgn-2400plus +9.9%)  
  2856 (r 0.65): e6 5.Bc4 Nc6 6.Nf3 Bb4 7. -&gt; O-O  
  -> 4274 (r 0.48): d6 7.Qd2 dxe5 8.Nxe5 Bxe5 9.dxe5 -&gt; Qxd2+
- **3249 -> 16081** (chess-pgn-1000-1300 -1.1%, chess-pgn-2400plus -1.0%)  
  3249 (r 0.50): Bd6 9.O-O O-O 10.Re1 Bd7 11.Qxb7 -&gt; Rb8  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3

### chess-pgn-1000-1300 mode 13: 1.1% of the matrix

- **8152 -> 1144** (chess-pgn-1000-1300 +29.3%, chess-pgn-2400plus +24.4%)  
  8152 (r 0.50): Kh5 34.Qxf7+ Kg4 35.Rg6+ Kh5 36. -&gt; Qh7#  
  -> 1144 (r 0.73): Ng4 20.Bxg4 Nd3 21.Qxd3 Rac8 22.Nxe8 -&gt; Rc7
- **8728 -> 1144** (chess-pgn-1000-1300 +38.4%, chess-pgn-2400plus +35.6%)  
  8728 (r 0.51): g6 29.Re7+ Kg8 30.Qf7+ Kh8 31. -&gt; Re8#  
  -> 1144 (r 0.73): Ng4 20.Bxg4 Nd3 21.Qxd3 Rac8 22.Nxe8 -&gt; Rc7
- **4087 -> 1144** (chess-pgn-1000-1300 +32.2%, chess-pgn-2400plus +27.9%)  
  4087 (r 0.57): Qc3 53.Kf2 Qd2+ 54.Kg3 Rc2 55.Kg4 -&gt; Qf2  
  -> 1144 (r 0.73): Ng4 20.Bxg4 Nd3 21.Qxd3 Rac8 22.Nxe8 -&gt; Rc7
- **5806 -> 1144** (chess-pgn-1000-1300 +37.0%, chess-pgn-2400plus +30.8%)  
  5806 (r 0.49): Bxf2+ 20.Kh1 Bxg3 21.Re1 Bxe1 22. -&gt; g3  
  -> 1144 (r 0.73): Ng4 20.Bxg4 Nd3 21.Qxd3 Rac8 22.Nxe8 -&gt; Rc7
- **982 -> 1144** (chess-pgn-1000-1300 +38.1%, chess-pgn-2400plus +33.5%)  
  982 (r 0.57): Qxf8 31.Rf7 Qh6+ 32.Ke1 Qxh5 33.Rd7+ -&gt; Bxd7  
  -> 1144 (r 0.73): Ng4 20.Bxg4 Nd3 21.Qxd3 Rac8 22.Nxe8 -&gt; Rc7
- **4091 -> 1144** (chess-pgn-1000-1300 +39.0%, chess-pgn-2400plus +33.0%)  
  4091 (r 0.57): Qe2 36.Rg1 Bxf3+ 37.Rxf3 Qxf3+ 38.Kh2 -&gt; Qf2+  
  -> 1144 (r 0.73): Ng4 20.Bxg4 Nd3 21.Qxd3 Rac8 22.Nxe8 -&gt; Rc7
- **5806 -> 6774** (chess-pgn-1000-1300 -0.3%, chess-pgn-2400plus -0.4%)  
  5806 (r 0.49): Bxf2+ 20.Kh1 Bxg3 21.Re1 Bxe1 22. -&gt; g3  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3
- **982 -> 6774** (chess-pgn-1000-1300 -0.0%, chess-pgn-2400plus -0.1%)  
  982 (r 0.57): Qxf8 31.Rf7 Qh6+ 32.Ke1 Qxh5 33.Rd7+ -&gt; Bxd7  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3

### chess-pgn-1000-1300 mode 14: 1.0% of the matrix

- **9612 -> 3125** (chess-pgn-1000-1300 +55.2%, chess-pgn-2400plus +51.5%)  
  9612 (r 0.54): Nf6 6.g3 Qb6 7.Nb3 Ng4 8. -&gt; Qe2  
  -> 3125 (r 0.49): Nc6 4.Nxc6 dxc6 5.e5 Ng4 6.g3 -&gt; Bc5
- **8886 -> 3125** (chess-pgn-1000-1300 -2.8%, chess-pgn-2400plus -2.7%)  
  8886 (r 0.54): h6 9.Nxf7 Rxf7 10.Bxf7+ Kh8 11.Bxh6 -&gt; Bxd4  
  -> 3125 (r 0.49): Nc6 4.Nxc6 dxc6 5.e5 Ng4 6.g3 -&gt; Bc5
- **15995 -> 3125** (chess-pgn-1000-1300 -2.1%, chess-pgn-2400plus -2.3%)  
  15995 (r 0.56): Bd7 11.a3 Qc8 12.Rc1 Bxh3 13. -&gt; gxh3  
  -> 3125 (r 0.49): Nc6 4.Nxc6 dxc6 5.e5 Ng4 6.g3 -&gt; Bc5
- **8744 -> 3125** (chess-pgn-1000-1300 +64.9%, chess-pgn-2400plus +60.5%)  
  8744 (r 0.50): d6 4.Nc3 a6 5.Bc4 Nf6 6.Ng5 -&gt; d5  
  -> 3125 (r 0.49): Nc6 4.Nxc6 dxc6 5.e5 Ng4 6.g3 -&gt; Bc5
- **8933 -> 3125** (chess-pgn-1000-1300 +68.7%, chess-pgn-2400plus +46.7%)  
  8933 (r 0.53): Nc6 4.O-O Bc5 5.c3 Ng4 6. -&gt; d4  
  -> 3125 (r 0.49): Nc6 4.Nxc6 dxc6 5.e5 Ng4 6.g3 -&gt; Bc5
- **9612 -> 5775** (chess-pgn-1000-1300 +34.9%, chess-pgn-2400plus +34.2%)  
  9612 (r 0.54): Nf6 6.g3 Qb6 7.Nb3 Ng4 8. -&gt; Qe2  
  -> 5775 (r 0.54): Nxd5 9.c3 Nc6 10.O-O Nce7 11.Nd2 -&gt; c6
- **4663 -> 3125** (chess-pgn-1000-1300 -1.9%, chess-pgn-2400plus -2.0%)  
  4663 (r 0.46): Bd6 9.Ng4 Nxg4 10.Qxg4 O-O 11.Bh6 -&gt; Qf6  
  -> 3125 (r 0.49): Nc6 4.Nxc6 dxc6 5.e5 Ng4 6.g3 -&gt; Bc5
- **6525 -> 3125** (chess-pgn-1000-1300 -2.1%, chess-pgn-2400plus -1.1%)  
  6525 (r 0.57): Kh8 11.Be3 Bb6 12.Qd2 Bxh3 13. -&gt; gxh3  
  -> 3125 (r 0.49): Nc6 4.Nxc6 dxc6 5.e5 Ng4 6.g3 -&gt; Bc5

## chess-pgn-2400plus

### chess-pgn-2400plus mode 0: 9.1% of the matrix

- **2694 -> 5615** (chess-pgn-1000-1300 +1.3%, chess-pgn-2400plus +4.6%)  
  2694 (r 0.58): Qxf6 8.Nd5 Qg6 9.Rg1 Be6 10.Ne7+ -&gt; Kh7  
  -> 5615 (r 0.47): Be6 20.Rxc7 Bb3 21.Rc8+ Rxc8 22. -&gt; Ba6
- **1804 -> 5615** (chess-pgn-1000-1300 +5.0%, chess-pgn-2400plus +6.7%)  
  1804 (r 0.56): Nc6 9.Bg5 Nd4 10.Bxf6 Ne2+ 11. -&gt; Kh1  
  -> 5615 (r 0.47): Be6 20.Rxc7 Bb3 21.Rc8+ Rxc8 22. -&gt; Ba6
- **5454 -> 5615** (chess-pgn-1000-1300 +11.6%, chess-pgn-2400plus +12.6%)  
  5454 (r 0.46): Qc7 7.Qh5 Bd6 8.Bf4 Nf6 9.Qxf7+ -&gt; Qxf7  
  -> 5615 (r 0.47): Be6 20.Rxc7 Bb3 21.Rc8+ Rxc8 22. -&gt; Ba6
- **16229 -> 5615** (chess-pgn-1000-1300 +5.3%, chess-pgn-2400plus +4.6%)  
  16229 (r 0.50): O-O-O 9.O-O Nf6 10.Ne5 Bxe2 11.Nxd7 -&gt; Bxd1  
  -> 5615 (r 0.47): Be6 20.Rxc7 Bb3 21.Rc8+ Rxc8 22. -&gt; Ba6
- **2461 -> 5615** (chess-pgn-1000-1300 +34.3%, chess-pgn-2400plus +36.9%)  
  2461 (r 0.54): Rd6 23.Bxa5 Rg6 24.Qf2 Rxg2+ 25. -&gt; Qxg2  
  -> 5615 (r 0.47): Be6 20.Rxc7 Bb3 21.Rc8+ Rxc8 22. -&gt; Ba6
- **2694 -> 12934** (chess-pgn-1000-1300 +6.1%, chess-pgn-2400plus +4.6%)  
  2694 (r 0.58): Qxf6 8.Nd5 Qg6 9.Rg1 Be6 10.Ne7+ -&gt; Kh7  
  -> 12934 (r 0.56): Kxf7 4.Nf3 d6 5.c3 Bg4 6.Ng5+ -&gt; Kf8
- **1804 -> 12934** (chess-pgn-1000-1300 +5.1%, chess-pgn-2400plus +3.7%)  
  1804 (r 0.56): Nc6 9.Bg5 Nd4 10.Bxf6 Ne2+ 11. -&gt; Kh1  
  -> 12934 (r 0.56): Kxf7 4.Nf3 d6 5.c3 Bg4 6.Ng5+ -&gt; Kf8
- **133 -> 5615** (chess-pgn-1000-1300 +4.9%, chess-pgn-2400plus +7.4%)  
  133 (r 0.49): cxd5 19.Nxd5 Be6 20.Be3 Qf5 21.Ne7+ -&gt; Kh8  
  -> 5615 (r 0.47): Be6 20.Rxc7 Bb3 21.Rc8+ Rxc8 22. -&gt; Ba6

### chess-pgn-2400plus mode 1: 3.4% of the matrix

- **5655 -> 3221** (chess-pgn-1000-1300 +52.4%, chess-pgn-2400plus +59.7%)  
  5655 (r 0.52): fxe6 32.Qxe6+ Kh7 33.Qe4+ Qxe4 34. -&gt; Rxe4  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **3040 -> 3221** (chess-pgn-1000-1300 +59.2%, chess-pgn-2400plus +66.7%)  
  3040 (r 0.53): Qf5+ 23.Qe4 Rxd1+ 24.Kc2 Qxe4+ 25. -&gt; Rxe4  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **13650 -> 3221** (chess-pgn-1000-1300 +41.0%, chess-pgn-2400plus +47.0%)  
  13650 (r 0.50): Rxa8 38.Qxa8+ Kh7 39.Qe8 Qe4+ 40.Qxe4+ -&gt; dxe4  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **9582 -> 3221** (chess-pgn-1000-1300 +57.4%, chess-pgn-2400plus +63.1%)  
  9582 (r 0.64): Rab8 19.Ng5 Ng6 20.h4 Qxb2 21.Qxb2 -&gt; Rxb2  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **15934 -> 3221** (chess-pgn-1000-1300 +64.3%, chess-pgn-2400plus +66.5%)  
  15934 (r 0.47): a6 13.d5 b5 14.dxc6 Qxd1 15. -&gt; Rfxd1  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **5060 -> 3221** (chess-pgn-1000-1300 +73.0%, chess-pgn-2400plus +74.4%)  
  5060 (r 0.45): g5 20.Re2 Qf5 21.Rae1 Qxe4 22. -&gt; Rxe4  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **600 -> 3221** (chess-pgn-1000-1300 +59.6%, chess-pgn-2400plus +66.7%)  
  600 (r 0.48): Rfe8 30.Rhf1 Bxd4+ 31.Qxd4 Qxd4+ 32. -&gt; Rxd4  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **15196 -> 3221** (chess-pgn-1000-1300 +48.6%, chess-pgn-2400plus +54.9%)  
  15196 (r 0.50): Qf1+ 50.Kb2 Qf6+ 51.Qc3 Qxc3+ 52. -&gt; Kxc3  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8

### chess-pgn-2400plus mode 2: 2.7% of the matrix

- **1256 -> 1936** (chess-pgn-1000-1300 -0.9%, chess-pgn-2400plus -0.9%)  
  1256 (r 0.51): Bd7 10.Bb1 b5 11.a3 b4 12. -&gt; axb4  
  -> 1936 (r 0.49): Rg7 35.Qxe4 Qxe4 36.Rxe4 Bxf1 37.Kxf1 -&gt; Rf7
- **1256 -> 3221** (chess-pgn-1000-1300 -1.4%, chess-pgn-2400plus -1.0%)  
  1256 (r 0.51): Bd7 10.Bb1 b5 11.a3 b4 12. -&gt; axb4  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **15060 -> 1936** (chess-pgn-1000-1300 -0.3%, chess-pgn-2400plus -0.7%)  
  15060 (r 0.53): O-O 11.a4 Bd7 12.c3 b5 13. -&gt; axb5  
  -> 1936 (r 0.49): Rg7 35.Qxe4 Qxe4 36.Rxe4 Bxf1 37.Kxf1 -&gt; Rf7
- **13523 -> 1936** (chess-pgn-1000-1300 +24.1%, chess-pgn-2400plus +24.6%)  
  13523 (r 0.52): Bg4 4.Nc3 Bxf3 5.Qxf3 Qxf3 6. -&gt; gxf3  
  -> 1936 (r 0.49): Rg7 35.Qxe4 Qxe4 36.Rxe4 Bxf1 37.Kxf1 -&gt; Rf7
- **15012 -> 1936** (chess-pgn-1000-1300 -2.2%, chess-pgn-2400plus -2.0%)  
  15012 (r 0.53): b5 6.Bb3 a5 7.a3 b4 8. -&gt; a4  
  -> 1936 (r 0.49): Rg7 35.Qxe4 Qxe4 36.Rxe4 Bxf1 37.Kxf1 -&gt; Rf7
- **15060 -> 3221** (chess-pgn-1000-1300 -1.1%, chess-pgn-2400plus -1.2%)  
  15060 (r 0.53): O-O 11.a4 Bd7 12.c3 b5 13. -&gt; axb5  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **13523 -> 3221** (chess-pgn-1000-1300 +41.7%, chess-pgn-2400plus +45.2%)  
  13523 (r 0.52): Bg4 4.Nc3 Bxf3 5.Qxf3 Qxf3 6. -&gt; gxf3  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **15012 -> 3221** (chess-pgn-1000-1300 -1.5%, chess-pgn-2400plus -1.5%)  
  15012 (r 0.53): b5 6.Bb3 a5 7.a3 b4 8. -&gt; a4  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8

### chess-pgn-2400plus mode 3: 2.6% of the matrix

- **3470 -> 1057** (chess-pgn-1000-1300 -0.6%, chess-pgn-2400plus -0.8%)  
  3470 (r 0.53): h6 14.Be3 Nf4 15.Bxf4 Qxf4 16.Ne5 -&gt; Qg5  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **6112 -> 1057** (chess-pgn-1000-1300 -0.2%, chess-pgn-2400plus -0.4%)  
  6112 (r 0.62): Bg4 7.d5 O-O-O 8.c4 e5 9.Nh4 -&gt; Bxe2  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **8612 -> 1057** (chess-pgn-1000-1300 -1.2%, chess-pgn-2400plus -0.8%)  
  8612 (r 0.55): Bg4 7.Nxf6+ Qxf6 8.Be2 Nd4 9. -&gt; c3  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **8728 -> 1057** (chess-pgn-1000-1300 +9.5%, chess-pgn-2400plus +7.4%)  
  8728 (r 0.51): g6 29.Re7+ Kg8 30.Qf7+ Kh8 31. -&gt; Re8#  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **3470 -> 15990** (chess-pgn-1000-1300 +19.2%, chess-pgn-2400plus +16.4%)  
  3470 (r 0.53): h6 14.Be3 Nf4 15.Bxf4 Qxf4 16.Ne5 -&gt; Qg5  
  -> 15990 (r 0.48): Ng3 12.Rg1 Nf5 13.O-O-O Nxe3 14.Qxe3 -&gt; Bxa3
- **72 -> 1057** (chess-pgn-1000-1300 -1.2%, chess-pgn-2400plus -0.7%)  
  72 (r 0.51): exf4 11.Bxf4 Rb8 12.a4 Bd7 13.e5 -&gt; dxe5  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **5681 -> 1057** (chess-pgn-1000-1300 -0.6%, chess-pgn-2400plus -0.0%)  
  5681 (r 0.51): Bg7 5.Nf3 O-O 6.Bc4 Nxe4 7. -&gt; Bxf7+  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **7034 -> 1057** (chess-pgn-1000-1300 -0.9%, chess-pgn-2400plus -0.5%)  
  7034 (r 0.57): Be7 6.e4 dxe4 7.Nxe4 Nxe4 8. -&gt; Qxe4  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6

### chess-pgn-2400plus mode 4: 1.7% of the matrix

- **7 -> 15990** (chess-pgn-1000-1300 +1.7%, chess-pgn-2400plus +3.0%)  
  7 (r 0.45): c6 4.Nf3 Bg4 5.Be2 Bxf3 6. -&gt; Bxf3  
  -> 15990 (r 0.48): Ng3 12.Rg1 Nf5 13.O-O-O Nxe3 14.Qxe3 -&gt; Bxa3
- **1340 -> 5615** (chess-pgn-1000-1300 +5.3%, chess-pgn-2400plus +6.0%)  
  1340 (r 0.48): Nxf1+ 27.Rxf1 Qg5 28.Qf2 Qg3+ 29. -&gt; Qxg3  
  -> 5615 (r 0.47): Be6 20.Rxc7 Bb3 21.Rc8+ Rxc8 22. -&gt; Ba6
- **12772 -> 15990** (chess-pgn-1000-1300 -2.7%, chess-pgn-2400plus -1.2%)  
  12772 (r 0.65): Rg5 29.Nxh6 Rgd5 30.g3 Rd1+ 31. -&gt; Rxd1  
  -> 15990 (r 0.48): Ng3 12.Rg1 Nf5 13.O-O-O Nxe3 14.Qxe3 -&gt; Bxa3
- **12330 -> 15990** (chess-pgn-1000-1300 -0.1%, chess-pgn-2400plus -0.0%)  
  12330 (r 0.51): Kf8 40.Qb8+ Qd8 41.Qe5 Qd5+ 42. -&gt; Qxd5  
  -> 15990 (r 0.48): Ng3 12.Rg1 Nf5 13.O-O-O Nxe3 14.Qxe3 -&gt; Bxa3
- **1340 -> 1057** (chess-pgn-1000-1300 -0.8%, chess-pgn-2400plus -3.7%)  
  1340 (r 0.48): Nxf1+ 27.Rxf1 Qg5 28.Qf2 Qg3+ 29. -&gt; Qxg3  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **13861 -> 15990** (chess-pgn-1000-1300 +11.6%, chess-pgn-2400plus +12.8%)  
  13861 (r 0.55): Nc6 4.Be2 Bg4 5.O-O Bxf3 6. -&gt; Bxf3  
  -> 15990 (r 0.48): Ng3 12.Rg1 Nf5 13.O-O-O Nxe3 14.Qxe3 -&gt; Bxa3
- **11252 -> 15990** (chess-pgn-1000-1300 +0.2%, chess-pgn-2400plus +1.4%)  
  11252 (r 0.58): Nf6 5.Nf3 Bg4 6.h3 Bxf3 7. -&gt; Qxf3  
  -> 15990 (r 0.48): Ng3 12.Rg1 Nf5 13.O-O-O Nxe3 14.Qxe3 -&gt; Bxa3
- **12772 -> 5615** (chess-pgn-1000-1300 +37.6%, chess-pgn-2400plus +41.8%)  
  12772 (r 0.65): Rg5 29.Nxh6 Rgd5 30.g3 Rd1+ 31. -&gt; Rxd1  
  -> 5615 (r 0.47): Be6 20.Rxc7 Bb3 21.Rc8+ Rxc8 22. -&gt; Ba6

### chess-pgn-2400plus mode 5: 1.7% of the matrix

- **1256 -> 2647** (chess-pgn-1000-1300 +4.4%, chess-pgn-2400plus +3.5%)  
  1256 (r 0.51): Bd7 10.Bb1 b5 11.a3 b4 12. -&gt; axb4  
  -> 2647 (r 0.50): Bg4 5.O-O e4 6.d3 exf3 7.Bxf3 -&gt; Bxf3
- **15060 -> 2647** (chess-pgn-1000-1300 +4.0%, chess-pgn-2400plus +3.2%)  
  15060 (r 0.53): O-O 11.a4 Bd7 12.c3 b5 13. -&gt; axb5  
  -> 2647 (r 0.50): Bg4 5.O-O e4 6.d3 exf3 7.Bxf3 -&gt; Bxf3
- **15012 -> 2647** (chess-pgn-1000-1300 +2.9%, chess-pgn-2400plus +2.1%)  
  15012 (r 0.53): b5 6.Bb3 a5 7.a3 b4 8. -&gt; a4  
  -> 2647 (r 0.50): Bg4 5.O-O e4 6.d3 exf3 7.Bxf3 -&gt; Bxf3
- **8508 -> 2647** (chess-pgn-1000-1300 +6.9%, chess-pgn-2400plus +5.6%)  
  8508 (r 0.52): dxc4 4.e3 b5 5.a4 a6 6.axb5 -&gt; Bb7  
  -> 2647 (r 0.50): Bg4 5.O-O e4 6.d3 exf3 7.Bxf3 -&gt; Bxf3
- **3242 -> 2647** (chess-pgn-1000-1300 +7.4%, chess-pgn-2400plus +7.3%)  
  3242 (r 0.52): c5 6.a3 Ba5 7.b4 cxb4 8. -&gt; Nb5  
  -> 2647 (r 0.50): Bg4 5.O-O e4 6.d3 exf3 7.Bxf3 -&gt; Bxf3
- **1130 -> 2647** (chess-pgn-1000-1300 +6.2%, chess-pgn-2400plus +4.7%)  
  1130 (r 0.56): b6 10.b4 a5 11.a3 axb4 12. -&gt; axb4  
  -> 2647 (r 0.50): Bg4 5.O-O e4 6.d3 exf3 7.Bxf3 -&gt; Bxf3
- **7342 -> 2647** (chess-pgn-1000-1300 +6.4%, chess-pgn-2400plus +7.6%)  
  7342 (r 0.52): Bd7 10.Ne2 Rb8 11.Ng3 b5 12.axb5 -&gt; axb5  
  -> 2647 (r 0.50): Bg4 5.O-O e4 6.d3 exf3 7.Bxf3 -&gt; Bxf3
- **4123 -> 2647** (chess-pgn-1000-1300 +3.6%, chess-pgn-2400plus +3.4%)  
  4123 (r 0.61): Ng4 13.b4 Na7 14.a4 h5 15.b5 -&gt; a5  
  -> 2647 (r 0.50): Bg4 5.O-O e4 6.d3 exf3 7.Bxf3 -&gt; Bxf3

### chess-pgn-2400plus mode 6: 1.5% of the matrix

- **6796 -> 326** (chess-pgn-1000-1300 +46.2%, chess-pgn-2400plus +38.6%)  
  6796 (r 0.40): Bf5 4.c4 e6 5.Qb3 Qb6 6. -&gt; Qxb6  
  -> 326 (r 0.45): c6 14.Nb3 Qe5 15.Bf4 Qb5 16.Qxb5 -&gt; cxb5
- **10823 -> 326** (chess-pgn-1000-1300 +53.1%, chess-pgn-2400plus +46.3%)  
  10823 (r 0.46): Nxe4 14.Qxe4 Nc6 15.O-O Qd5 16. -&gt; Qxd5  
  -> 326 (r 0.45): c6 14.Nb3 Qe5 15.Bf4 Qb5 16.Qxb5 -&gt; cxb5
- **6264 -> 326** (chess-pgn-1000-1300 +54.1%, chess-pgn-2400plus +42.1%)  
  6264 (r 0.52): Rac8 13.Qe3 Bxc3 14.bxc3 Qxc3 15. -&gt; Qxa7  
  -> 326 (r 0.45): c6 14.Nb3 Qe5 15.Bf4 Qb5 16.Qxb5 -&gt; cxb5
- **11187 -> 326** (chess-pgn-1000-1300 +41.9%, chess-pgn-2400plus +37.7%)  
  11187 (r 0.49): Bxf3 10.Qxf3 Qxd4 11.Rd1 Qg4 12. -&gt; Qe3  
  -> 326 (r 0.45): c6 14.Nb3 Qe5 15.Bf4 Qb5 16.Qxb5 -&gt; cxb5
- **11108 -> 326** (chess-pgn-1000-1300 +50.5%, chess-pgn-2400plus +43.9%)  
  11108 (r 0.45): Qg3 14.Qf2 Qd6 15.Ba3 Qd7 16.Qf5 -&gt; Qxf5  
  -> 326 (r 0.45): c6 14.Nb3 Qe5 15.Bf4 Qb5 16.Qxb5 -&gt; cxb5
- **6796 -> 15508** (chess-pgn-1000-1300 +1.0%, chess-pgn-2400plus +1.9%)  
  6796 (r 0.40): Bf5 4.c4 e6 5.Qb3 Qb6 6. -&gt; Qxb6  
  -> 15508 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **12765 -> 326** (chess-pgn-1000-1300 +50.8%, chess-pgn-2400plus +36.1%)  
  12765 (r 0.46): Bg4 4.h3 Bxf3 5.Qxf3 Qf6 6. -&gt; Qg4  
  -> 326 (r 0.45): c6 14.Nb3 Qe5 15.Bf4 Qb5 16.Qxb5 -&gt; cxb5
- **6220 -> 326** (chess-pgn-1000-1300 +58.5%, chess-pgn-2400plus +49.0%)  
  6220 (r 0.49): e6 7.exd5 exd5 8.Qe2+ Qe7 9. -&gt; Be3  
  -> 326 (r 0.45): c6 14.Nb3 Qe5 15.Bf4 Qb5 16.Qxb5 -&gt; cxb5

### chess-pgn-2400plus mode 7: 1.3% of the matrix

- **15696 -> 7056** (chess-pgn-1000-1300 -0.4%, chess-pgn-2400plus -1.0%)  
  15696 (r 0.46): Nc6 6.d3 g6 7.Qg5 Qxg5 8. -&gt; Nxg5  
  -> 7056 (r 0.47): h4 23.gxh4 Bg4 24.Bg2 Bxf3 25.Bxf3 -&gt; Nh6
- **12460 -> 7056** (chess-pgn-1000-1300 +0.3%, chess-pgn-2400plus +1.3%)  
  12460 (r 0.51): O-O 6.O-O d6 7.Re1 h6 8.Nxf7 -&gt; Rxf7  
  -> 7056 (r 0.47): h4 23.gxh4 Bg4 24.Bg2 Bxf3 25.Bxf3 -&gt; Nh6
- **12009 -> 1057** (chess-pgn-1000-1300 -0.4%, chess-pgn-2400plus -0.3%)  
  12009 (r 0.52): Nbc6 10.O-O Ng6 11.Re1 f5 12.exf6 -&gt; Rxf6  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **14101 -> 1057** (chess-pgn-1000-1300 -0.7%, chess-pgn-2400plus -0.3%)  
  14101 (r 0.54): Nc6 20.Qd2 h6 21.Bb1 f5 22.exf6 -&gt; Nxf6  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **10954 -> 7056** (chess-pgn-1000-1300 -1.7%, chess-pgn-2400plus -1.5%)  
  10954 (r 0.48): Nxc4 8.Qxc4 d5 9.exd5 Qxd5 10.Qxd5 -&gt; Nxd5  
  -> 7056 (r 0.47): h4 23.gxh4 Bg4 24.Bg2 Bxf3 25.Bxf3 -&gt; Nh6
- **12009 -> 7056** (chess-pgn-1000-1300 +17.6%, chess-pgn-2400plus +14.6%)  
  12009 (r 0.52): Nbc6 10.O-O Ng6 11.Re1 f5 12.exf6 -&gt; Rxf6  
  -> 7056 (r 0.47): h4 23.gxh4 Bg4 24.Bg2 Bxf3 25.Bxf3 -&gt; Nh6
- **15696 -> 3221** (chess-pgn-1000-1300 +55.7%, chess-pgn-2400plus +59.8%)  
  15696 (r 0.46): Nc6 6.d3 g6 7.Qg5 Qxg5 8. -&gt; Nxg5  
  -> 3221 (r 0.43): Be6 15.Qxb7 Qb6 16.Qxc6 Qxc6 17.Nxc6 -&gt; Rac8
- **14101 -> 7056** (chess-pgn-1000-1300 +14.4%, chess-pgn-2400plus +8.5%)  
  14101 (r 0.54): Nc6 20.Qd2 h6 21.Bb1 f5 22.exf6 -&gt; Nxf6  
  -> 7056 (r 0.47): h4 23.gxh4 Bg4 24.Bg2 Bxf3 25.Bxf3 -&gt; Nh6

### chess-pgn-2400plus mode 8: 1.2% of the matrix

- **1254 -> 5077** (chess-pgn-1000-1300 +53.6%, chess-pgn-2400plus +50.2%)  
  1254 (r 0.62): Nb4 5.Qc4 b5 6.Qxb5 Nxc2+ 7. -&gt; Kd2  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **13237 -> 5077** (chess-pgn-1000-1300 +51.8%, chess-pgn-2400plus +49.3%)  
  13237 (r 0.53): Nh6 6.d3 Nd4 7.Qh5 Nxc2+ 8. -&gt; Kd1  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **8859 -> 5077** (chess-pgn-1000-1300 +54.9%, chess-pgn-2400plus +48.3%)  
  8859 (r 0.49): Nf6 5.Nc3 Nd4 6.Qe3 Nxc2+ 7. -&gt; Ke2  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **3739 -> 5077** (chess-pgn-1000-1300 +45.9%, chess-pgn-2400plus +42.9%)  
  3739 (r 0.54): Qxd4 8.Qxd4 Nxd4 9.Nc3 Nc2+ 10. -&gt; Kd2  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **2205 -> 5077** (chess-pgn-1000-1300 +46.6%, chess-pgn-2400plus +43.4%)  
  2205 (r 0.54): dxc5 10.Nc3 Nd4 11.Qxb7 Nc2+ 12. -&gt; Ke2  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **5660 -> 5077** (chess-pgn-1000-1300 +48.6%, chess-pgn-2400plus +43.9%)  
  5660 (r 0.54): g6 7.Nd5 Qe5 8.Nfe3 Qxe4 9.Nxc7+ -&gt; Kd8  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **7546 -> 5077** (chess-pgn-1000-1300 +57.9%, chess-pgn-2400plus +52.4%)  
  7546 (r 0.56): Bxb5 10.Nxb5 a6 11.Qxd5 Qxd5 12.Nc7+ -&gt; Kf8  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+
- **2694 -> 5077** (chess-pgn-1000-1300 +55.9%, chess-pgn-2400plus +49.1%)  
  2694 (r 0.58): Qxf6 8.Nd5 Qg6 9.Rg1 Be6 10.Ne7+ -&gt; Kh7  
  -> 5077 (r 0.69): Qf6 16.Nxd5 Qg6 17.Ne7+ Kh8 18. -&gt; Nxg6+

### chess-pgn-2400plus mode 9: 1.2% of the matrix

- **8419 -> 16081** (chess-pgn-1000-1300 +71.1%, chess-pgn-2400plus +68.6%)  
  8419 (r 0.43): d5 7.Nc3 Be7 8.g3 Bb4 9. -&gt; Bd2  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **6814 -> 16081** (chess-pgn-1000-1300 +42.6%, chess-pgn-2400plus +44.6%)  
  6814 (r 0.52): exd4 4.Qxd4 c5 5.Qa4+ Bd7 6.Bb5 -&gt; Nc6  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **8692 -> 16081** (chess-pgn-1000-1300 +42.0%, chess-pgn-2400plus +38.0%)  
  8692 (r 0.54): c6 6.e3 Qa5 7.Qc2 Ne4 8. -&gt; Rc1  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **15103 -> 16081** (chess-pgn-1000-1300 +63.3%, chess-pgn-2400plus +58.5%)  
  15103 (r 0.56): Nf6 4.Bc4 Nxe4 5.Nxe4 d5 6.Bb5 -&gt; dxe4  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **8775 -> 16081** (chess-pgn-1000-1300 +53.9%, chess-pgn-2400plus +48.7%)  
  8775 (r 0.57): Nxe5 5.Nxe5 Qxe5 6.g3 Bb4 7. -&gt; Bf4  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **1964 -> 16081** (chess-pgn-1000-1300 +52.6%, chess-pgn-2400plus +47.0%)  
  1964 (r 0.55): Qf6 5.c3 Nc6 6.Be3 d6 7.Bb5 -&gt; Bd7  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **13789 -> 16081** (chess-pgn-1000-1300 +55.9%, chess-pgn-2400plus +51.5%)  
  13789 (r 0.53): a6 5.e3 Nf6 6.Nc3 Bb4 7. -&gt; Bd3  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3
- **5930 -> 16081** (chess-pgn-1000-1300 +57.7%, chess-pgn-2400plus +53.9%)  
  5930 (r 0.54): Nf6 7.Qd2 Bd6 8.O-O-O Bb4 9. -&gt; f3  
  -> 16081 (r 0.53): Nxc6 5.c5 e5 6.Bb5 Bxc5 7. -&gt; Nc3

### chess-pgn-2400plus mode 10: 1.1% of the matrix

- **901 -> 6774** (chess-pgn-1000-1300 +29.4%, chess-pgn-2400plus +28.2%)  
  901 (r 0.56): Nf6 5.d3 d6 6.Bg5 O-O 7.Nd5 -&gt; Bg4  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3
- **12241 -> 6774** (chess-pgn-1000-1300 -1.5%, chess-pgn-2400plus -2.3%)  
  12241 (r 0.56): exd4 5.c3 dxc3 6.Nxc3 Nf6 7.e5 -&gt; Ng4  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3
- **10713 -> 6774** (chess-pgn-1000-1300 +0.4%, chess-pgn-2400plus +0.3%)  
  10713 (r 0.48): h6 7.Qe2 O-O 8.Be3 Nd4 9. -&gt; Bxd4  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3
- **8028 -> 6774** (chess-pgn-1000-1300 -1.1%, chess-pgn-2400plus -1.1%)  
  8028 (r 0.55): h6 4.c3 Nf6 5.d4 d6 6.dxe5 -&gt; dxe5  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3
- **1216 -> 6774** (chess-pgn-1000-1300 +68.3%, chess-pgn-2400plus +66.3%)  
  1216 (r 0.41): exd5 4.d4 Nf6 5.Nc3 Be6 6.Bg5 -&gt; Bb4  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3
- **2220 -> 6774** (chess-pgn-1000-1300 +59.4%, chess-pgn-2400plus +60.7%)  
  2220 (r 0.53): Nc6 4.d3 d5 5.exd5 Nxd5 6.Bg5 -&gt; f6  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3
- **15144 -> 6774** (chess-pgn-1000-1300 +28.6%, chess-pgn-2400plus +27.7%)  
  15144 (r 0.53): d6 5.Nc3 Bg4 6.h3 Nd4 7. -&gt; Nxe5  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3
- **5844 -> 6774** (chess-pgn-1000-1300 +29.5%, chess-pgn-2400plus +28.9%)  
  5844 (r 0.58): d6 4.Bc4 Bg4 5.Nc3 Nd4 6. -&gt; Nxe5  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3

### chess-pgn-2400plus mode 11: 1.1% of the matrix

- **1216 -> 6774** (chess-pgn-1000-1300 +68.3%, chess-pgn-2400plus +66.3%)  
  1216 (r 0.41): exd5 4.d4 Nf6 5.Nc3 Be6 6.Bg5 -&gt; Bb4  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3
- **16246 -> 6774** (chess-pgn-1000-1300 +65.7%, chess-pgn-2400plus +66.9%)  
  16246 (r 0.49): exd5 4.d4 Bd6 5.Nc3 Ne7 6.Bg5 -&gt; f6  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3
- **14623 -> 6774** (chess-pgn-1000-1300 +67.0%, chess-pgn-2400plus +68.2%)  
  14623 (r 0.51): Bh5 11.Ng3 Bg6 12.Re1 Bd6 13.Bg5 -&gt; f6  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3
- **12055 -> 6774** (chess-pgn-1000-1300 +56.3%, chess-pgn-2400plus +58.4%)  
  12055 (r 0.52): Nf6 4.d3 Nc6 5.Ng5 Bg4 6. -&gt; Nxf7  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3
- **8854 -> 6774** (chess-pgn-1000-1300 +58.3%, chess-pgn-2400plus +63.0%)  
  8854 (r 0.53): O-O 6.d3 d6 7.O-O Bg4 8. -&gt; Qe1  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3
- **6421 -> 6774** (chess-pgn-1000-1300 +62.4%, chess-pgn-2400plus +62.5%)  
  6421 (r 0.53): Nc6 5.d5 Ne5 6.f4 Bg4 7. -&gt; Be2  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3
- **987 -> 6774** (chess-pgn-1000-1300 +61.2%, chess-pgn-2400plus +61.5%)  
  987 (r 0.52): e6 4.Nc3 Nf6 5.e5 Nd5 6.Bg5 -&gt; f6  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3
- **14914 -> 6774** (chess-pgn-1000-1300 +62.6%, chess-pgn-2400plus +62.9%)  
  14914 (r 0.50): c5 4.Nf3 a6 5.Nc3 Nc6 6.Bg5 -&gt; Qb6  
  -> 6774 (r 0.50): Bg4 5.Qe2 Nf4 6.Qe4 Nxg2+ 7.Kf1 -&gt; Bxf3

### chess-pgn-2400plus mode 12: 1.1% of the matrix

- **12428 -> 5615** (chess-pgn-1000-1300 +40.6%, chess-pgn-2400plus +38.1%)  
  12428 (r 0.50): Bg7 6.Bb2 a5 7.Nge2 axb4 8.axb4 -&gt; Rxa1  
  -> 5615 (r 0.47): Be6 20.Rxc7 Bb3 21.Rc8+ Rxc8 22. -&gt; Ba6
- **10703 -> 5615** (chess-pgn-1000-1300 +37.8%, chess-pgn-2400plus +40.3%)  
  10703 (r 0.53): cxd5 6.h5 Bg4 7.hxg6 hxg6 8. -&gt; Rxh8  
  -> 5615 (r 0.47): Be6 20.Rxc7 Bb3 21.Rc8+ Rxc8 22. -&gt; Ba6
- **8726 -> 5615** (chess-pgn-1000-1300 +39.7%, chess-pgn-2400plus +41.4%)  
  8726 (r 0.60): Nc5 11.Nce2 Nxb3 12.axb3 Be6 13.Rxa7 -&gt; Rxa7  
  -> 5615 (r 0.47): Be6 20.Rxc7 Bb3 21.Rc8+ Rxc8 22. -&gt; Ba6
- **1130 -> 5615** (chess-pgn-1000-1300 +11.5%, chess-pgn-2400plus +13.0%)  
  1130 (r 0.56): b6 10.b4 a5 11.a3 axb4 12. -&gt; axb4  
  -> 5615 (r 0.47): Be6 20.Rxc7 Bb3 21.Rc8+ Rxc8 22. -&gt; Ba6
- **6811 -> 5615** (chess-pgn-1000-1300 +38.4%, chess-pgn-2400plus +39.8%)  
  6811 (r 0.57): Nc6 7.Bg5 axb4 8.cxb4 Nxb4 9.axb4 -&gt; Rxa1  
  -> 5615 (r 0.47): Be6 20.Rxc7 Bb3 21.Rc8+ Rxc8 22. -&gt; Ba6
- **10409 -> 5615** (chess-pgn-1000-1300 +36.8%, chess-pgn-2400plus +29.8%)  
  10409 (r 0.52): Nc4 16.Qc1 a5 17.Nd2 axb4 18.axb4 -&gt; Bxb4  
  -> 5615 (r 0.47): Be6 20.Rxc7 Bb3 21.Rc8+ Rxc8 22. -&gt; Ba6
- **31 -> 5615** (chess-pgn-1000-1300 +51.8%, chess-pgn-2400plus +53.7%)  
  31 (r 0.51): a5 16.a3 axb4 17.axb4 Rxa1 18. -&gt; Rxa1  
  -> 5615 (r 0.47): Be6 20.Rxc7 Bb3 21.Rc8+ Rxc8 22. -&gt; Ba6
- **8324 -> 5615** (chess-pgn-1000-1300 +38.1%, chess-pgn-2400plus +35.4%)  
  8324 (r 0.59): Qa5 18.Bg5 Rb8 19.Rxe8+ Rxe8 20. -&gt; Rxe8+  
  -> 5615 (r 0.47): Be6 20.Rxc7 Bb3 21.Rc8+ Rxc8 22. -&gt; Ba6

### chess-pgn-2400plus mode 13: 1.0% of the matrix

- **12867 -> 1057** (chess-pgn-1000-1300 +6.7%, chess-pgn-2400plus +5.7%)  
  12867 (r 0.55): Nb6 7.Bb3 Nc6 8.Nf3 Bg4 9.Bxf7+ -&gt; Kxf7  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **14347 -> 1057** (chess-pgn-1000-1300 -4.4%, chess-pgn-2400plus -5.2%)  
  14347 (r 0.55): Ke8 28.Bxd6 Rxd6 29.Rxe7+ Kd8 30.Rae1 -&gt; Rxd5  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **6139 -> 1057** (chess-pgn-1000-1300 +7.3%, chess-pgn-2400plus +6.0%)  
  6139 (r 0.58): h6 4.Nc3 Bc5 5.d3 Bxf2+ 6. -&gt; Kxf2  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **10838 -> 1057** (chess-pgn-1000-1300 +5.0%, chess-pgn-2400plus +4.5%)  
  10838 (r 0.50): Bc5 6.d4 Bxd4 7.c3 Bxf2+ 8. -&gt; Ke2  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **13347 -> 1057** (chess-pgn-1000-1300 +19.9%, chess-pgn-2400plus +12.8%)  
  13347 (r 0.54): Nf6 5.Bg5 Bc5 6.Nb3 Bxf2+ 7. -&gt; Kxf2  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **2316 -> 1057** (chess-pgn-1000-1300 +37.7%, chess-pgn-2400plus +33.5%)  
  2316 (r 0.53): Kh8 18.Qh5+ Kg8 19.Qh7+ Kf8 20.Qh8+ -&gt; Ke7  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **15113 -> 1057** (chess-pgn-1000-1300 +3.4%, chess-pgn-2400plus +3.9%)  
  15113 (r 0.48): Bxd4 10.Nc3 d6 11.Nb5 Bxf2+ 12. -&gt; Kxf2  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6
- **10108 -> 1057** (chess-pgn-1000-1300 +4.9%, chess-pgn-2400plus +5.7%)  
  10108 (r 0.57): Be7 4.c3 Nc6 5.O-O Nf6 6.Bxf7+ -&gt; Kxf7  
  -> 1057 (r 0.53): Qxg1+ 14.Ke2 Qg4+ 15.Kf1 Qh3+ 16.Ke2 -&gt; Qxh6

### chess-pgn-2400plus mode 14: 0.9% of the matrix

- **8321 -> 15508** (chess-pgn-1000-1300 -2.5%, chess-pgn-2400plus -2.6%)  
  8321 (r 0.55): Qxa5 22.Re2 b5 23.e5 Nd7 24.e6 -&gt; Nc5  
  -> 15508 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **8163 -> 15508** (chess-pgn-1000-1300 -3.5%, chess-pgn-2400plus -2.9%)  
  8163 (r 0.60): Nge7 8.c3 dxc3 9.Nxc3 d6 10.e6 -&gt; f5  
  -> 15508 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **3928 -> 15508** (chess-pgn-1000-1300 -4.2%, chess-pgn-2400plus -5.3%)  
  3928 (r 0.55): Bxf1 17.Rdxf1 Qxh2 18.Qxd5 Rad8 19.Rxf7 -&gt; Qxd2+  
  -> 15508 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **4320 -> 15508** (chess-pgn-1000-1300 -2.6%, chess-pgn-2400plus -1.0%)  
  4320 (r 0.56): Ngf6 6.e5 dxe5 7.dxe5 Ng4 8.e6 -&gt; fxe6  
  -> 15508 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **10019 -> 15508** (chess-pgn-1000-1300 -3.8%, chess-pgn-2400plus -2.7%)  
  10019 (r 0.54): Bf5 4.g4 Bg6 5.h4 h5 6.e6 -&gt; Qd6  
  -> 15508 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **13011 -> 15508** (chess-pgn-1000-1300 -3.7%, chess-pgn-2400plus -2.9%)  
  13011 (r 0.50): O-O 14.e5 Nec6 15.Re1 Bxb2 16.e6 -&gt; Bxa1  
  -> 15508 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **12018 -> 15508** (chess-pgn-1000-1300 -2.5%, chess-pgn-2400plus -2.2%)  
  12018 (r 0.58): e6 7.Bb5+ Bd7 8.dxe6 Bxb5 9. -&gt; exf7+  
  -> 15508 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
- **16212 -> 15508** (chess-pgn-1000-1300 -1.4%, chess-pgn-2400plus -0.1%)  
  16212 (r 0.32): dxc4 4.Bxc4 e5 5.Qb3 exd4 6. -&gt; Bxf7+  
  -> 15508 (r 0.50): Nd7 18.Qd6 Rf6 19.Qb4 a5 20.Qc4 -&gt; b5
