# transcend/interp

**What do the two PGN models (1000-1300 and 2400+) represent, and how do their ideas follow from one
another?** The thesis: the latents are tangible chess concepts, the models share nearly all of
them, and some **paths** between concepts are taken by only one model.

**Which layer.** Linear probes from each model's states to Stockfish's evaluation show the 2400+
model pulling ahead from layer 12 on (equal at layer 8), most clearly at layer 15 (R^2 0.77 vs
0.65, against 0.62 from hand-written board facts alone). So the concept work uses layer 15.

**A confound to keep in mind.** Each model plays its own games, so a path can look like one
model's only because its games reach such positions: the weak model in check in a lost game, the
strong one converting a won game. Once `score` has run, the graphs keep only paths whose rollouts
mostly start in an open position (Stockfish win chance 10-90%, more than one legal move).

## Run

```bash
# 1. a crosscoder between the two models: one dictionary of latents read from both (~3M positions)
python transcend/interp/crosscoder.py collect --positions 3000000 --per-game 4 --layers 8 12 15 final --run runs/transcend/crosscoder/everything-3m
python transcend/interp/crosscoder.py train   --run runs/transcend/crosscoder/everything-3m --layers 15
python transcend/interp/crosscoder.py top     --run runs/transcend/crosscoder/everything-3m --cc L15
# 2. an explanation for every latent, scored on held-out games, and what the layer knows
python transcend/interp/explain.py --cc-run runs/transcend/crosscoder/everything-3m --cc L15
# 3. self-play rollouts (several hours), then the path graphs, example rollouts and Stockfish on them
python transcend/interp/concepts.py rollout  --cc-run runs/transcend/crosscoder/everything-3m --cc L15
python transcend/interp/concepts.py graph    --run runs/transcend/concepts/everything-3m-L15
python transcend/interp/concepts.py examples --run runs/transcend/concepts/everything-3m-L15
python transcend/interp/concepts.py score    --run runs/transcend/concepts/everything-3m-L15
python transcend/interp/concepts.py modes    --run runs/transcend/concepts/everything-3m-L15   # optional: SVD "flow modes"
```

| step | what it measures | look at |
| --- | --- | --- |
| `crosscoder.py` | one BatchTopK dictionary over both models' states; which latents each model uses (relative decoder norm: 0 = only 1000-1300, 1 = only 2400+); a layer sweep | `results/transcend/crosscoder/everything-3m/cc-L15/report.md` |
| `explain.py` | each latent's best one- or two-fact explanation with held-out F1 (*explained* = F1 >= 0.5); its **engine link** (how much better the side to move stands, by Stockfish, than the board predicts where it fires); **what the layer knows** (probes to eval, threat, only-move gap) | `.../cc-L15/explain.md` |
| `concepts.py rollout` | per model, how often latent j turns on within 4 plies of latent i, against sibling rollouts from the same start | `runs/transcend/concepts/everything-3m-L15/` |
| `concepts.py graph` | three graphs: paths only the 1000-1300 model takes, only 2400+, and both; picked from the `--candidates` strongest | `graph.html`, `graph3d.html` in the run; `results/transcend/concepts/everything-3m-L15/summary.md` |
| `concepts.py examples` | rollouts where each path happens, and what at least half of them have in common from i to j | hover an arrow in `graph.html` |
| `concepts.py score` | Stockfish on every move of those rollouts: win chances gained or lost, and what kind of move starts and ends the path | edge cards, `summary.md` |

Fact vocabularies: `predicates.py` (board facts: hanging pieces, pins, forks, checks, what the move
does; square facts: which piece stands where, from the mover's side) and `skill.py` (from
Stockfish and Maia-2: only move, deep move, sound sacrifice, meeting a threat, blunder, rare for
1100s). `sae.py` is a single-model sparse autoencoder, the precursor to the crosscoder; `pages.py`
draws the HTML boards and cards.
