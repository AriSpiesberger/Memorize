# Retest of three leads on fresh branch pairs: fixed before running (2026-10-29)

The leads come from steer-match.md, where they beat every random push but failed "-v below zero":
S14 (move features), S141 (move features), W25 (moves legal in both states).

- Pairs: concept_mine.py's decisive branch points (node >= 30, chosen >= 0.75, subpar share >= 0.02) at positions the
  concept was not mined from; its most common window k; matched plies where the concept is higher on the chosen line by
  more than 0.5 (cached w . z); at most 150 plies per concept, drawn at random (seed 0).
  Prepared: S14 150 plies (34 positions), S141 150 (22), W25 150 (29).
- Test: steer_match.py's alignment, push r = 0.25 of ||h|| at the last position, 20 random v's of matching firing rate.
- Each concept is decided in its named space only: S14 features, S141 features, W25 common.
- Passes when: +v's mean alignment > every random v's, -v's <= the random v's median, and Benjamini-Hochberg q < 0.05
  over these 3 tests (p from +v's z against the random v's).
- Reported beside it, not deciding: the other space, the other strengths, transfer, and +v as a share of the natural change.

Commands:

    python transcend/dynamic/steer_match.py run --name fresh --device cuda
    python transcend/dynamic/steer_match.py summary --name fresh --neg-rule median --spaces S14:features,S141:features,W25:common
