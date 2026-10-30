# transcend/dynamic

**Within each model, what in its state separates the line it plays from the line it doesn't?**
Schut et al.'s dynamic concepts on the PGN models: each model (S = 2400+, W = 1000-1300) plays
many rollouts from the same positions; where they branch, a max-margin LP finds the sparsest set
of crosscoder latents that separates the chosen line from a subpar one. The concepts are then
checked for recurrence, seed stability and the board, and injected back into the model to see
whether they move its play.

Built on a layer-11 crosscoder trained on human games and the models' own rollouts (`crossmix.py`;
layer 11 is where `layerprobe.py` found the models' own future moves). Results land in
`results/transcend/divergence/<tag>/`.

## Run

```bash
python transcend/dynamic/layerprobe.py                       # which layer carries the model's own future
python transcend/dynamic/crossmix.py all                     # the L11 crosscoder -> runs/transcend/crosscoder/mixed-L11
# divergence: the LP at each model's own branching points
python transcend/dynamic/divergence.py play --model S        # and --model W (GPU)
python transcend/dynamic/divergence.py plant                 # planted check of the LP (CPU)
python transcend/dynamic/divergence.py lp   --model S        # and W (CPU)
python transcend/dynamic/divergence.py report
# concepts at scale, then steering
python transcend/dynamic/concept_mine.py lp --model S --seed 0       # see its docstring for the full sequence
python transcend/dynamic/concept_mine.py report
python transcend/dynamic/steer_concepts.py prep
python transcend/dynamic/steer_concepts.py run --only S141,S8,W29,S14,W25,S29,W138,W30,S58,W197
python transcend/dynamic/steer_concepts.py summary
```

| script | what it does |
| --- | --- |
| `shared.py` | helpers: the crosscoder, both models' policies and states, rollouts, Schut's LP |
| `layerprobe.py` | per layer, how much the state says about the moves the model will play next, beyond the board |
| `crossmix.py` | the L11 crosscoder on human positions and rollouts, at several sizes and seeds |
| `readings.py`, `plies.py` | where S and W pick different moves, does S's reading of the shared latents differ from W's, and does the gap grow over the next plies? |
| `oneposition.py`, `recurring.py` | the earlier single-position and many-position pattern searches |
| `divergence.py` | dynamic concepts with a persistence window: `play`, `plant`, `lp`, `report` |
| `divergence_gap.py` | the same on clear decisions only |
| `conceptseed.py`, `conceptlook.py`, `onebranch.py` | seed stability; chosen concepts with and without; one branching position ply by ply |
| `concept_mine.py` | concepts mined at scale and sorted by how clean they are (recurrence, board probe, seeds) |
| `steer_concepts.py`, `steer_after.py` | inject a concept's direction into the L11 state and read off the moves; the pilot diagnosed and rerun |
| `lookahead.py` | does a concept's expression before a split predict the move, beyond the board? |
| `oneoff/` | one-off checks on a divergence run (decisive and non-board LPs, concept graphs, minimal pairs), on the run tagged `p16-r1024-T0.4-s0-L11-4k`. Arguments are positional; see the top of each file |
