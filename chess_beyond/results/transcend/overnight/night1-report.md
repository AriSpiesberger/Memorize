# Overnight mine and confirm (night1)

Rules fixed before any data: night1-prereg.md. Candidates frozen 2026-10-30T04:47:48.

## Positions

868 positions sampled: 511 discovery, 357 confirmation (256 rollouts of 16 plies at T = 0.4, S and W each; the first 8 positions at 512).

## Concepts at each step

| step | S | W |
|---|---|---|
| mined (families with examples) | 864 | 844 |
| replicate across seeds | 738 | 712 |
| and seen at >= 20 discovery positions | 33 | 28 |
| and the push lands (readback >= g) | 16 | 20 |
| tested (plus S14 by default) | 17 | 20 |
| passed | 0 | 0 |

Untested (time): none.

## Each candidate

Towards: +v into the concept-low state; away: -v into the concept-high state. JS: share of the Jensen-Shannon gap closed on the moves legal in both states (main measure). Features: the move-features projection. Random: 50 directions of the same size and matching firing rates. q: Benjamini-Hochberg over the candidates tested, on the larger of the two JS p's.

| candidate | model | theme | discovery positions | plies (confirmation positions) | JS towards (random 95th) | JS away (random 95th) | features towards (random 95th) | features away (random 95th) | q | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| ov1:S5 | S |  | 45 | 100 (68) | +0.060 (+0.020) | +0.033 (+0.016) | +0.109 (+0.052) | +0.089 (+0.078) | 0.172 | fails |
| ov1:W11 | W |  | 36 | 100 (61) | +0.025 (+0.015) | +0.028 (+0.021) | +0.028 (+0.037) | +0.042 (+0.060) | 0.172 | fails |
| ov1:S39 | S | no capture or check | 27 | 100 (69) | +0.054 (+0.025) | +0.022 (+0.011) | +0.030 (+0.072) | +0.075 (+0.053) | 0.172 | fails |
| ov1:S23 | S |  | 24 | 100 (55) | +0.035 (+0.016) | +0.026 (+0.014) | +0.097 (+0.041) | +0.079 (+0.087) | 0.172 | fails |
| ov1:S4 | S |  | 52 | 100 (75) | +0.038 (+0.020) | +0.046 (+0.024) | +0.057 (+0.046) | +0.055 (+0.042) | 0.265 | fails |
| ov1:S3 | S |  | 55 | 100 (74) | +0.016 (+0.014) | +0.038 (+0.017) | +0.021 (+0.053) | +0.072 (+0.074) | 0.394 | fails |
| ov1:S13 | S | two or more captures | 36 | 100 (80) | +0.031 (+0.022) | +0.017 (+0.023) | +0.047 (+0.048) | +0.025 (+0.055) | 0.394 | fails |
| ov1:W15 | W | two or more knight moves | 26 | 100 (64) | +0.014 (+0.013) | +0.019 (+0.018) | +0.031 (+0.046) | +0.045 (+0.043) | 0.401 | fails |
| ov1:S8 | S |  | 46 | 100 (72) | +0.015 (+0.016) | +0.008 (+0.007) | +0.007 (+0.043) | +0.038 (+0.047) | 0.403 | fails |
| ov1:W28 | W |  | 29 | 100 (54) | +0.009 (+0.006) | +0.034 (+0.019) | +0.024 (+0.046) | +0.074 (+0.045) | 0.403 | fails |
| ov1:S75 | S |  | 24 | 100 (53) | +0.014 (+0.022) | +0.031 (+0.021) | +0.107 (+0.058) | +0.049 (+0.057) | 0.403 | fails |
| ov1:W16 | W |  | 31 | 100 (60) | +0.017 (+0.022) | +0.047 (+0.029) | +0.025 (+0.049) | +0.055 (+0.048) | 0.407 | fails |
| ov1:S19 | S | no capture or check | 27 | 100 (43) | +0.033 (+0.032) | +0.010 (+0.019) | +0.037 (+0.083) | +0.043 (+0.065) | 0.407 | fails |
| ov1:W58 | W |  | 20 | 100 (38) | +0.033 (+0.013) | +0.007 (+0.009) | +0.027 (+0.041) | +0.072 (+0.042) | 0.407 | fails |
| S14 | S | two or more captures | 8 | 100 (72) | +0.015 (+0.008) | +0.008 (+0.015) | +0.133 (+0.043) | +0.029 (+0.064) | 0.407 | fails |
| ov1:W40 | W |  | 20 | 100 (75) | +0.007 (+0.014) | +0.021 (+0.020) | +0.063 (+0.031) | +0.029 (+0.043) | 0.458 | fails |
| ov1:S31 | S |  | 22 | 100 (54) | +0.021 (+0.017) | -0.004 (+0.005) | +0.037 (+0.041) | +0.033 (+0.076) | 0.608 | fails |
| ov1:W0 | W | two or more queen moves | 50 | 100 (64) | +0.028 (+0.024) | +0.002 (+0.013) | +0.054 (+0.036) | +0.035 (+0.026) | 0.644 | fails |
| ov1:W2 | W | two or more queen moves | 64 | 100 (79) | +0.040 (+0.021) | +0.004 (+0.025) | +0.023 (+0.027) | +0.014 (+0.047) | 0.674 | fails |
| ov1:W17 | W | king move | 38 | 100 (78) | +0.022 (+0.018) | +0.005 (+0.035) | +0.025 (+0.041) | +0.013 (+0.036) | 0.674 | fails |
| ov1:S18 | S | two or more pawn moves | 31 | 100 (64) | -0.003 (+0.011) | +0.008 (+0.021) | +0.046 (+0.053) | +0.071 (+0.065) | 0.674 | fails |
| ov1:S26 | S |  | 23 | 100 (52) | -0.003 (+0.021) | +0.029 (+0.020) | +0.028 (+0.036) | +0.055 (+0.057) | 0.674 | fails |
| ov1:W10 | W | two or more captures | 23 | 100 (50) | +0.016 (+0.013) | -0.003 (+0.012) | +0.030 (+0.037) | +0.002 (+0.028) | 0.674 | fails |
| ov1:S29 | S | two or more rook moves | 22 | 100 (70) | +0.008 (+0.017) | -0.006 (+0.018) | +0.017 (+0.053) | +0.056 (+0.056) | 0.674 | fails |
| ov1:S86 | S | capture | 21 | 100 (53) | -0.000 (+0.012) | -0.010 (+0.020) | +0.044 (+0.036) | +0.036 (+0.036) | 0.674 | fails |
| ov1:W24 | W |  | 26 | 100 (72) | -0.004 (+0.027) | +0.003 (+0.021) | +0.030 (+0.049) | +0.001 (+0.041) | 0.713 | fails |
| ov1:S0 | S | two or more queen moves | 57 | 100 (64) | +0.035 (+0.029) | -0.009 (+0.014) | +0.050 (+0.061) | +0.014 (+0.041) | 0.744 | fails |
| ov1:W43 | W | two or more pawn moves | 22 | 100 (61) | +0.025 (+0.012) | -0.002 (+0.025) | +0.027 (+0.040) | +0.039 (+0.043) | 0.744 | fails |
| ov1:W13 | W | two or more knight moves | 30 | 100 (64) | -0.000 (+0.019) | +0.012 (+0.012) | +0.012 (+0.028) | +0.083 (+0.023) | 0.744 | fails |
| ov1:W95 | W |  | 21 | 100 (68) | +0.013 (+0.022) | -0.003 (+0.017) | +0.005 (+0.034) | +0.034 (+0.041) | 0.769 | fails |
| ov1:W3 | W | two or more knight moves | 37 | 100 (60) | -0.013 (+0.019) | +0.029 (+0.018) | +0.292 (+0.023) | +0.014 (+0.029) | 0.807 | fails |
| ov1:W25 | W |  | 22 | 100 (52) | +0.039 (+0.016) | -0.011 (+0.020) | +0.044 (+0.059) | +0.008 (+0.041) | 0.807 | fails |
| ov1:S43 | S | two or more queen moves | 21 | 100 (66) | +0.007 (+0.026) | -0.014 (+0.016) | +0.028 (+0.040) | +0.030 (+0.061) | 0.807 | fails |
| ov1:W37 | W |  | 20 | 100 (44) | +0.025 (+0.016) | -0.014 (+0.014) | +0.045 (+0.071) | +0.063 (+0.059) | 0.807 | fails |
| ov1:W64 | W |  | 23 | 100 (73) | -0.003 (+0.009) | -0.010 (+0.022) | +0.013 (+0.045) | +0.025 (+0.047) | 0.822 | fails |
| ov1:W14 | W |  | 28 | 100 (54) | +0.032 (+0.018) | -0.017 (+0.012) | +0.021 (+0.042) | +0.015 (+0.043) | 0.878 | fails |
| ov1:W47 | W | two or more captures | 24 | 100 (55) | +0.023 (+0.018) | -0.013 (+0.020) | +0.030 (+0.038) | +0.027 (+0.029) | 0.878 | fails |

## Post hoc (not pre-registered; does not change any verdict)

Across the 37 candidates, how often the concept beats its own 50 random directions' 95th percentile (main measure):
towards 23 of 37, away 14 of 37, both 8 of 37 (S3, S4, S5, S23, S39, W11, W15, W28). Under no effect each is about 5%
per candidate: P(>= 23 towards) ~ 4e-21, P(>= 14 away) ~ 1e-9, P(>= 8 both) ~ 4e-4 even if the two tests were fully
correlated. Median z against the random directions: towards 1.33, away 1.02. So as a class the mined concepts move play
toward the concept-high state's (and, pushed out, toward the concept-low state's) more than random directions of the
same size do, but each by a few percent of the Jensen-Shannon gap (towards 1-6%), too little for any one to pass the
fixed rule. Caveats: candidates were selected for a push that lands (readback >= g) and the random directions were not;
the concepts are mostly board-tier, so "concept-high" may largely mean "board consequence present".
