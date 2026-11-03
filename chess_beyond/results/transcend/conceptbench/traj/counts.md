# Dynamic bench: episodes per concept

An episode: a run of at least 4 plies where the concept holds (plans: plan_book.py). Kept: at least 100 episodes in fit games.

| family | concept | fit episodes | test episodes | mean length | fit + / - plies | |
|---|---|--:|--:|--:|--:|---|
| imbalances | black_bad_bishop | 12597 | 3137 | 15.5 | 195223 / 190576 |  |
| imbalances | black_bishop_vs_knight | 3163 | 872 | 19.4 | 61516 / 1945821 |  |
| imbalances | black_development_lead | 2725 | 677 | 8.3 | 22602 / 912769 |  |
| imbalances | black_king_unsafe | 7883 | 2021 | 10.8 | 85757 / 1144367 |  |
| imbalances | black_kingside_majority | 18579 | 4661 | 24.4 | 450908 / 1544440 |  |
| imbalances | black_knight_outpost | 5211 | 1283 | 11.0 | 56860 / 1945026 |  |
| imbalances | black_passed_pawn | 13382 | 3411 | 22.3 | 298967 / 1702347 |  |
| imbalances | black_queen_open_or_half_open_file | 28285 | 7142 | 13.6 | 384004 / 1599588 |  |
| imbalances | black_queenside_majority | 17632 | 4363 | 22.4 | 397215 / 1592300 |  |
| imbalances | black_rook_half_open_file | 19848 | 5089 | 15.4 | 305602 / 1689412 |  |
| imbalances | black_rook_open_file | 23668 | 5982 | 14.3 | 336199 / 1653295 |  |
| imbalances | black_space_advantage | 9468 | 2494 | 14.3 | 135076 / 1622905 |  |
| imbalances | black_weak_king_squares | 13558 | 3445 | 17.3 | 233667 / 1249563 |  |
| imbalances | white_bad_bishop | 12142 | 3054 | 15.3 | 185823 / 192017 |  |
| imbalances | white_bishop_vs_knight | 2851 | 709 | 18.7 | 53688 / 1953969 |  |
| imbalances | white_development_lead | 6397 | 1587 | 9.0 | 57541 / 863844 |  |
| imbalances | white_king_unsafe | 6755 | 1744 | 10.8 | 73146 / 1105571 |  |
| imbalances | white_kingside_majority | 16955 | 4216 | 23.1 | 392698 / 1603131 |  |
| imbalances | white_knight_outpost | 5164 | 1315 | 10.8 | 56577 / 1944780 |  |
| imbalances | white_passed_pawn | 13178 | 3331 | 22.5 | 295098 / 1705868 |  |
| imbalances | white_queen_open_or_half_open_file | 28991 | 7364 | 13.7 | 398080 / 1586547 |  |
| imbalances | white_queenside_majority | 18804 | 4823 | 23.7 | 444956 / 1547038 |  |
| imbalances | white_rook_half_open_file | 20726 | 5054 | 15.6 | 324341 / 1670081 |  |
| imbalances | white_rook_open_file | 25013 | 6301 | 14.8 | 367264 / 1623277 |  |
| imbalances | white_space_advantage | 18463 | 4548 | 14.9 | 276532 / 1463623 |  |
| imbalances | white_weak_king_squares | 12166 | 3135 | 17.1 | 209134 / 1273393 |  |
| openings | eco_A00 | 970 | 237 | 15.7 | 15227 / 498016 |  |
| openings | eco_A01 | 274 | 64 | 15.7 | 4300 / 508955 |  |
| openings | eco_A04 | 276 | 86 | 15.7 | 4322 / 508925 |  |
| openings | eco_A10 | 218 | 71 | 15.7 | 3436 / 509822 |  |
| openings | eco_A13 | 141 | 36 | 15.8 | 2226 / 511030 |  |
| openings | eco_A40 | 1172 | 287 | 15.6 | 18322 / 494925 |  |
| openings | eco_A43 | 227 | 64 | 15.7 | 3554 / 509697 |  |
| openings | eco_A45 | 669 | 156 | 15.8 | 10528 / 502722 |  |
| openings | eco_B00 | 1171 | 266 | 15.6 | 18256 / 494980 |  |
| openings | eco_B01 | 1164 | 315 | 15.5 | 18013 / 495223 |  |
| openings | eco_B06 | 464 | 109 | 15.7 | 7277 / 505975 |  |
| openings | eco_B10 | 659 | 174 | 15.6 | 10258 / 502993 |  |
| openings | eco_B12 | 585 | 170 | 15.7 | 9203 / 504048 |  |
| openings | eco_B13 | 403 | 107 | 15.5 | 6224 / 507024 |  |
| openings | eco_B20 | 604 | 178 | 15.7 | 9483 / 503767 |  |
| openings | eco_B21 | 530 | 142 | 15.6 | 8273 / 504980 |  |
| openings | eco_B22 | 350 | 107 | 15.5 | 5395 / 507857 |  |
| openings | eco_B23 | 341 | 90 | 15.7 | 5350 / 507908 |  |
| openings | eco_B30 | 508 | 137 | 15.7 | 7969 / 505289 |  |
| openings | eco_B40 | 282 | 75 | 15.6 | 4406 / 508852 |  |
| openings | eco_B50 | 352 | 90 | 15.7 | 5531 / 507710 |  |
| openings | eco_C00 | 869 | 213 | 15.6 | 13571 / 499681 |  |
| openings | eco_C01 | 462 | 120 | 15.8 | 7293 / 505959 |  |
| openings | eco_C02 | 433 | 108 | 15.6 | 6765 / 506489 |  |
| openings | eco_C20 | 321 | 65 | 15.6 | 4983 / 508269 |  |
| openings | eco_C23 | 245 | 59 | 15.5 | 3808 / 509447 |  |
| openings | eco_C40 | 292 | 81 | 15.3 | 4460 / 508788 |  |
| openings | eco_C41 | 619 | 150 | 15.7 | 9735 / 503514 |  |
| openings | eco_C42 | 351 | 88 | 15.4 | 5400 / 507848 |  |
| openings | eco_C44 | 651 | 159 | 15.3 | 9958 / 503286 |  |
| openings | eco_C47 | 213 | 58 | 15.4 | 3278 / 509977 |  |
| openings | eco_C50 | 829 | 204 | 15.5 | 12827 / 500419 |  |
| openings | eco_D00 | 1204 | 282 | 15.7 | 18879 / 494372 |  |
| openings | eco_D01 | 268 | 56 | 15.7 | 4219 / 509031 |  |
| openings | eco_D02 | 847 | 223 | 15.5 | 13164 / 500085 |  |
| openings | eco_D06 | 215 | 46 | 15.5 | 3358 / 509892 |  |
| openings | eco_D10 | 257 | 54 | 15.6 | 4008 / 509246 |  |
| openings | eco_D20 | 185 | 44 | 15.5 | 2868 / 510386 |  |
| openings | eco_D30 | 182 | 45 | 15.7 | 2846 / 510408 |  |
| openings | eco_D31 | 137 | 37 | 15.5 | 2129 / 511128 |  |
| openings | eco_D35 | 127 | 32 | 15.3 | 1948 / 511286 |  |
| openings | line_Caro_Kann_Defense | 455 | 124 | 15.5 | 7076 / 506176 |  |
| openings | line_Caro_Kann_Defense_Advance_Variation | 451 | 130 | 15.7 | 7106 / 506148 |  |
| openings | line_Caro_Kann_Defense_Exchange_Variation | 329 | 86 | 15.6 | 5136 / 508117 |  |
| openings | line_Caro_Kann_Defense_Panov_Attack | 110 | 31 | 15.2 | 1656 / 511595 |  |
| openings | line_English_Opening_Agincourt_Defense | 145 | 41 | 15.8 | 2290 / 510964 |  |
| openings | line_English_Opening_Anglo_Indian_Defense | 245 | 65 | 15.8 | 3867 / 509389 |  |
| openings | line_English_Opening_King_s_English_Variation | 491 | 108 | 15.6 | 7682 / 505573 |  |
| openings | line_English_Opening_Symmetrical_Variation | 235 | 68 | 15.7 | 3685 / 509565 |  |
| openings | line_French_Defense_Advance_Variation | 433 | 108 | 15.6 | 6765 / 506489 |  |
| openings | line_French_Defense_Exchange_Variation | 462 | 120 | 15.8 | 7293 / 505959 |  |
| openings | line_Horwitz_Defense | 286 | 74 | 15.7 | 4478 / 508779 |  |
| openings | line_Hungarian_Opening | 169 | 36 | 15.5 | 2615 / 510643 |  |
| openings | line_Indian_Defense_Accelerated_London_System | 276 | 76 | 15.7 | 4323 / 508930 |  |
| openings | line_Italian_Game_Classical_Variation | 335 | 80 | 15.6 | 5226 / 508025 |  |
| openings | line_Italian_Game_Giuoco_Pianissimo | 260 | 65 | 15.6 | 4061 / 509196 |  |
| openings | line_Italian_Game_Two_Knights_Defense | 342 | 88 | 15.3 | 5222 / 508026 |  |
| openings | line_King_s_Indian_Defense_Normal_Variation | 136 | 39 | 15.6 | 2116 / 511141 |  |
| openings | line_Modern_Defense | 265 | 70 | 15.6 | 4145 / 509109 |  |
| openings | line_Philidor_Defense | 374 | 94 | 15.7 | 5882 / 507367 |  |
| openings | line_Pirc_Defense | 452 | 123 | 15.6 | 7032 / 506220 |  |
| openings | line_Queen_s_Gambit_Declined | 208 | 56 | 15.7 | 3277 / 509976 |  |
| openings | line_Queen_s_Gambit_Declined_Exchange_Variation | 99 | 26 | 15.5 | 1529 / 511729 | **dropped** |
| openings | line_Queen_s_Pawn_Game | 517 | 141 | 15.7 | 8157 / 505095 |  |
| openings | line_Queen_s_Pawn_Game_Accelerated_London_System | 553 | 137 | 15.7 | 8711 / 504542 |  |
| openings | line_Queen_s_Pawn_Game_Chigorin_Variation | 265 | 55 | 15.4 | 4054 / 509203 |  |
| openings | line_Queen_s_Pawn_Game_Colle_System | 179 | 47 | 15.7 | 2820 / 510438 |  |
| openings | line_Queen_s_Pawn_Game_London_System | 305 | 82 | 15.6 | 4775 / 508476 |  |
| openings | line_Queen_s_Pawn_Game_Zukertort_Variation | 198 | 55 | 15.7 | 3130 / 510128 |  |
| openings | line_Rapport_Jobava_System | 244 | 53 | 15.6 | 3836 / 509415 |  |
| openings | line_Scandinavian_Defense | 201 | 53 | 15.4 | 3091 / 510160 |  |
| openings | line_Scotch_Game | 169 | 43 | 15.0 | 2574 / 510678 |  |
| openings | line_Sicilian_Defense | 189 | 48 | 15.7 | 2983 / 510267 |  |
| openings | line_Sicilian_Defense_Accelerated_Dragon | 178 | 40 | 15.1 | 2691 / 510556 |  |
| openings | line_Sicilian_Defense_Alapin_Variation | 344 | 104 | 15.4 | 5295 / 507957 |  |
| openings | line_Sicilian_Defense_Bowdler_Attack | 282 | 88 | 15.7 | 4419 / 508835 |  |
| openings | line_Sicilian_Defense_Closed | 331 | 94 | 15.7 | 5202 / 508056 |  |
| openings | line_Sicilian_Defense_Najdorf_Variation | 309 | 65 | 15.8 | 4885 / 508373 |  |
| openings | line_Sicilian_Defense_Old_Sicilian | 336 | 89 | 15.6 | 5263 / 507995 |  |
| openings | line_Van_t_Kruijs_Opening | 237 | 52 | 15.7 | 3736 / 509520 |  |
| pieces | black_bishop_pair | 33180 | 8410 | 29.9 | 992810 / 1016201 |  |
| pieces | black_has_queen | 33630 | 8552 | 44.9 | 1511755 / 496692 |  |
| pieces | black_minors_0 | 6987 | 1846 | 28.9 | 200638 / 1806682 |  |
| pieces | black_minors_1 | 16461 | 4243 | 21.8 | 359923 / 1644455 |  |
| pieces | black_minors_2 | 23211 | 5886 | 15.5 | 360535 / 1640965 |  |
| pieces | black_minors_3 | 27626 | 6993 | 13.6 | 375758 / 1625341 |  |
| pieces | black_minors_4 | 33179 | 8410 | 20.8 | 690407 / 1318601 |  |
| pieces | black_minors_atleast_1 | 33179 | 8410 | 54.4 | 1806680 / 202329 |  |
| pieces | black_minors_atleast_2 | 33182 | 8410 | 43.4 | 1442123 / 566885 |  |
| pieces | black_minors_atleast_3 | 33180 | 8410 | 32.3 | 1074078 / 934931 |  |
| pieces | black_rooks_0 | 5053 | 1281 | 28.9 | 145323 / 1862166 |  |
| pieces | black_rooks_1 | 14216 | 3612 | 23.6 | 334552 / 1670021 |  |
| pieces | black_rooks_2 | 33182 | 8411 | 45.9 | 1523170 / 485835 |  |
| pieces | black_rooks_atleast_1 | 33186 | 8411 | 56.1 | 1862156 / 146845 |  |
| pieces | white_bishop_pair | 33178 | 8411 | 29.3 | 975463 / 1033539 |  |
| pieces | white_has_queen | 33622 | 8533 | 45.0 | 1514301 / 494086 |  |
| pieces | white_minors_0 | 7081 | 1862 | 28.5 | 202442 / 1804817 |  |
| pieces | white_minors_1 | 16808 | 4233 | 21.9 | 365930 / 1638663 |  |
| pieces | white_minors_2 | 23296 | 5918 | 15.4 | 357383 / 1644200 |  |
| pieces | white_minors_3 | 27832 | 7033 | 13.6 | 378072 / 1623347 |  |
| pieces | white_minors_4 | 33175 | 8411 | 20.6 | 683982 / 1325017 |  |
| pieces | white_minors_atleast_1 | 33181 | 8411 | 54.4 | 1804811 / 204194 |  |
| pieces | white_minors_atleast_2 | 33184 | 8413 | 43.2 | 1434467 / 574542 |  |
| pieces | white_minors_atleast_3 | 33179 | 8411 | 32.2 | 1069653 / 939353 |  |
| pieces | white_rooks_0 | 4979 | 1348 | 29.2 | 144919 / 1862647 |  |
| pieces | white_rooks_1 | 14092 | 3645 | 23.3 | 329380 / 1675115 |  |
| pieces | white_rooks_2 | 33182 | 8410 | 46.0 | 1528741 / 480260 |  |
| pieces | white_rooks_atleast_1 | 33184 | 8413 | 56.1 | 1862636 / 146364 |  |
| plans | plan_benoni_b5 | 49 | 14 | 10.0 | 492 / 2606 | **dropped** |
| plans | plan_benoni_e5 | 30 | 9 | 9.5 | 279 / 2833 | **dropped** |
| plans | plan_benoni_f4_e5 | 11 | 4 | 15.0 | 167 / 2490 | **dropped** |
| plans | plan_big_centre_c5 | 47 | 9 | 6.4 | 303 / 3045 | **dropped** |
| plans | plan_big_centre_d5 | 78 | 20 | 7.0 | 555 / 2822 | **dropped** |
| plans | plan_carlsbad_central_break | 194 | 50 | 11.4 | 2208 / 25512 |  |
| plans | plan_carlsbad_kingside_counter | 592 | 143 | 10.6 | 6235 / 22428 |  |
| plans | plan_carlsbad_minority | 289 | 69 | 12.1 | 3411 / 21683 |  |
| plans | plan_carlsbad_pillsbury | 78 | 14 | 13.2 | 1038 / 24706 | **dropped** |
| plans | plan_caro_slav_c5 | 823 | 224 | 9.2 | 7580 / 53769 |  |
| plans | plan_caro_slav_e5 | 416 | 114 | 9.8 | 4097 / 57617 |  |
| plans | plan_caro_slav_space | 393 | 99 | 9.2 | 3638 / 57287 |  |
| plans | plan_dragon_b5 | 77 | 17 | 8.6 | 673 / 4126 | **dropped** |
| plans | plan_dragon_exchange_sac | 8 | 0 | 10.8 | 86 / 4733 | **dropped** |
| plans | plan_dragon_h_storm | 28 | 7 | 13.1 | 364 / 4194 | **dropped** |
| plans | plan_fianchetto_h_storm | 294 | 72 | 11.6 | 3434 / 143874 |  |
| plans | plan_french_c5 | 372 | 91 | 7.7 | 2846 / 39302 |  |
| plans | plan_french_d4_pressure | 638 | 170 | 11.0 | 6894 / 30636 |  |
| plans | plan_french_f6 | 300 | 75 | 10.3 | 3051 / 40094 |  |
| plans | plan_french_kingside | 64 | 9 | 13.1 | 837 / 40002 | **dropped** |
| plans | plan_hanging_pawns_advance | 115 | 24 | 7.5 | 874 / 881 |  |
| plans | plan_hanging_pawns_levers | 6 | 3 | 7.7 | 46 / 1582 | **dropped** |
| plans | plan_hedgehog_break | 11 | 2 | 11.1 | 114 / 287 | **dropped** |
| plans | plan_iqp_blockade | 990 | 246 | 10.0 | 9936 / 43587 |  |
| plans | plan_iqp_break | 787 | 193 | 8.7 | 6822 / 46725 |  |
| plans | plan_iqp_kingside_attack | 276 | 67 | 15.0 | 4120 / 42001 |  |
| plans | plan_king_centralisation | 3613 | 957 | 24.2 | 87070 / 176823 |  |
| plans | plan_kings_indian_queenside | 84 | 28 | 12.4 | 1035 / 6113 | **dropped** |
| plans | plan_kings_indian_storm | 51 | 26 | 13.1 | 634 / 3447 | **dropped** |
| plans | plan_maroczy_break | 52 | 18 | 10.6 | 525 / 3681 | **dropped** |
| plans | plan_maroczy_f5 | 17 | 3 | 10.3 | 178 / 4457 | **dropped** |
| plans | plan_najdorf_b5 | 167 | 44 | 7.2 | 1224 / 7558 |  |
| plans | plan_najdorf_d5 | 87 | 21 | 8.8 | 772 / 8005 | **dropped** |
| plans | plan_najdorf_nd5 | 239 | 58 | 8.5 | 2019 / 6757 |  |
| plans | plan_opposite_castling_storm | 3137 | 755 | 16.1 | 50434 / 47683 |  |
| plans | plan_queenside_majority_push | 10930 | 2754 | 16.6 | 181668 / 442679 |  |
| plans | plan_rook_seventh | 13332 | 3393 | 15.2 | 202209 / 822354 |  |
| plans | plan_scheveningen_b5 | 161 | 41 | 8.0 | 1285 / 5654 |  |
| plans | plan_scheveningen_d5 | 76 | 20 | 9.3 | 700 / 6264 | **dropped** |
| plans | plan_scheveningen_english_attack | 152 | 26 | 14.3 | 2164 / 4310 |  |
| plans | plan_small_centre_d5 | 323 | 80 | 9.2 | 2936 / 37686 |  |
| plans | plan_small_centre_f4 | 411 | 108 | 9.4 | 3894 / 36696 |  |
| plans | plan_small_centre_f5 | 139 | 27 | 9.7 | 1353 / 39218 |  |
| plans | plan_stonewall_attack | 117 | 26 | 16.9 | 2007 / 19289 |  |
| plans | plan_stonewall_c5_break | 174 | 40 | 8.7 | 1516 / 24710 |  |
| structures | benoni | 172 | 46 | 20.0 | 3380 / 2005572 |  |
| structures | carlsbad | 1563 | 394 | 19.1 | 29899 / 1978577 |  |
| structures | caro_slav | 3735 | 973 | 17.1 | 64199 / 1942066 |  |
| structures | french_advance | 2622 | 637 | 18.1 | 47478 / 1960449 |  |
| structures | hanging_pawns | 187 | 46 | 9.2 | 1734 / 2007010 |  |
| structures | isolated_queens_pawn | 3896 | 985 | 15.8 | 61083 / 1944274 |  |
| structures | kings_indian | 508 | 123 | 16.4 | 8232 / 2000466 |  |
| structures | maroczy_bind | 284 | 93 | 16.5 | 4749 / 2004049 |  |
| structures | small_centre | 2716 | 656 | 16.1 | 43864 / 1962046 |  |
| structures | stonewall | 1548 | 377 | 19.1 | 29762 / 1978411 |  |
