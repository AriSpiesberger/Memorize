# transcend/dynamic

**Within each model, what in its state separates the move it plays from the one it doesn't, and does that
difference drive the choice?** Schut et al.'s dynamic concepts on the PGN models (S = 2400+, W = 1000-1300): each
model plays many rollouts from the same positions; where they branch, a max-margin LP finds the sparsest set of
crosscoder latents that separates the chosen line from a subpar one over the next few plies. Concepts are mined,
checked across crosscoder seeds and against the board, then pushed back into the model.

| step | script | result |
| --- | --- | --- |
| which layer carries the model's own future moves: L11, ahead of L15 and the final layer by 0.23-0.25 nats | `layerprobe.py` | [S-report.md](../../results/transcend/layerprobe/n5000-p6-s0/S-report.md) |
| an L11 crosscoder on human games and the models' rollouts, two seeds | `crossmix.py` | [seed-match.md](../../results/transcend/crosscoder/mixed-L11/seed-match.md) |
| the LP at each model's branch points, 50 positions, with a planted check | `divergence.py` | [report.md](../../results/transcend/divergence/p16-r1024-T0.4-s0-L11-4k/report.md), [plant.md](../../results/transcend/divergence/p16-r1024-T0.4-s0-L11-4k/plant.md) |
| concepts mined at scale and graded by seed replication and board probe | `concept_mine.py` | [concepts.md](../../results/transcend/divergence/p16-r1024-T0.4-s0-L11-4k/mine/concepts.md) |
| overnight: new positions, mined as they arrive, then a preregistered steering test on fresh positions: **0 of 37 candidates move the model** | `overnight_play.py`, `overnight_mine.py`, `overnight_confirm.py` | [night1-prereg.md](../../results/transcend/overnight/night1-prereg.md), [night1-report.md](../../results/transcend/overnight/night1-report.md) |

The overnight concepts are drawn as a map in [../interp/concept_graph.py](../interp/concept_graph.py)
([the page](../../results/transcend/overnight/night1-graph.html)). `shared.py` holds the helpers (crosscoder, policies,
rollouts, cached codes); `steer.py` the concept direction and the push.

## Run

```bash
python transcend/dynamic/layerprobe.py                          # GPU
python transcend/dynamic/crossmix.py all                        # GPU: -> runs/transcend/crosscoder/mixed-L11
python transcend/dynamic/divergence.py play --model S           # GPU, and --model W; then plant, lp --model S/W, report (CPU)
python transcend/dynamic/concept_mine.py all                    # CPU: both models, both seeds
# overnight, side by side, then the test
python transcend/dynamic/overnight_play.py --deadline 2026-10-30T04:30     # GPU
python transcend/dynamic/overnight_mine.py                                 # CPU
python transcend/dynamic/overnight_confirm.py choose --device cuda         # then prep, run --device cuda, report
```

Each script's docstring has its stages and options. Earlier searches (single positions, the S-W reading gap, the
final-layer crosscoder) and the steering pilots that led to the overnight test are in git history before
`dynamic/steer.py` was added.
