# Overnight run night1: rules fixed before any data (2026-10-29, 23:55)

Data: new middlegame positions from data/pgn_probe/population.jsonl, one per game, games not used by the manypositions
run, bands alternated; 512 rollouts of 16 plies at T = 0.4 per model (S and W). Each position is assigned to discovery
(60%) or confirmation (40%) by a hash of its game when it is created. Rollouts stop at 04:30.
Change at 23:52, before any mining (user's call, for more positions): 256 rollouts per model instead of 512. The first
8 positions (5 discovery, 3 confirmation; at most one replayed at 256) were played at 512 and are kept.

## Mining (discovery positions only)

concept_mine.py, unchanged defaults (decisive branch points: >= 30 rollouts, chosen >= 0.75; LP at k = 2,3,4,5,6,8;
families at cosine >= 0.5), crosscoder L11 4k seeds 0 and 1, values kept. Planted check (concept_mine.py plant) on the
first 20 discovery positions, S and W; if it fails, mining stops.

## Candidates (chosen at 04:30, before any steering; frozen in night1-candidates.json)

All of:
1. replicates across seeds: replication >= its null 95th + 0.15, agreement >= its null 95th + 0.1, and
   replication on its own positions >= its strict null 95th (concept_mine.py's numbers);
2. seen at >= 20 discovery positions;
3. the push lands: at 25% of ||h|| (+v at the prompt end, L11), the concept's activity read back through the crosscoder
   rises by >= its natural gap g (median chosen-minus-subpar w . z at its branch points), median over up to 16 of its
   branch points.
Plus S14 from p16-r1024-T0.4-s0-L11-4k, included by default (its own latents, weights, mu and gap).
A concept is its centroid's top latents covering 95% of the squared weight, renormalised (steer_concepts.py's rule).

## Confirmation (confirmation positions only), in order of discovery positions seen, most first

Pairs: decisive branch points (>= 30 rollouts, chosen >= 0.75, subpar share >= 0.02) in the concept's own model's
rollouts at confirmation positions, over its most common window k, at matched plies where its expression is higher on
the chosen line by more than 0.5; at most 100 plies, drawn at random (seed 0). Concept-high state = the chosen line's,
concept-low = the subpar line's, same ply.

Push: at the last position only, L11, h -> h + 0.25 ||h|| d, d a unit direction. 50 random directions per concept:
the concept's weights on random latents of the same firing-rate decile, each of the same size.
- Towards: d = +v into the concept-low state. Null: d = each random direction into the low state.
- Away: d = -v into the concept-high state. Null: d = minus each random direction into the high state.

Main measure: Jensen-Shannon gap closed, on the moves legal in both states (each distribution renormalised over them):
  towards = sum over plies of [JS(low, high) - JS(low pushed, high)] / sum of JS(low, high)
  away    = sum over plies of [JS(high, low) - JS(high pushed, low)] / sum of JS(high, low)
Also reported: the move-features projection (steer_match.py's features space) for both tests.

Pass: towards > the random 95th AND away > the random 95th (main measure), AND Benjamini-Hochberg q < 0.05 across the
candidates tested, with each candidate's p = the larger of its two p's, each p = 1 - Phi(z) of the concept's value
against the 50 random values (mean, sd). The features projection does not decide.

If time runs short, candidates are tested in the order above until 06:35; untested ones are reported as untested.
