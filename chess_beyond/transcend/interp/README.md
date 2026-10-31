# transcend/interp

**What do the two PGN models (1000-1300 and 2400+) represent, and do they share it?** A crosscoder reads both
models' states into one dictionary of latents, so each latent is shared or belongs to one model; each latent then gets
a plain-chess explanation scored on held-out games.

**Which layer.** Linear probes from each model's states to Stockfish's evaluation show the 2400+ model pulling ahead
from layer 12 on (equal at layer 8), most clearly at layer 15 (R^2 0.77 vs 0.65, against 0.62 from hand-written board
facts alone), so the explanations use layer 15. The dynamic-concept work uses layer 11, where the models carry their
own future moves ([../dynamic](../dynamic/README.md)).

```bash
python transcend/interp/crosscoder.py collect --positions 3000000 --per-game 4 --layers 8 12 15 final --run runs/transcend/crosscoder/everything-3m
python transcend/interp/crosscoder.py train   --run runs/transcend/crosscoder/everything-3m --layers 15
python transcend/interp/crosscoder.py top     --run runs/transcend/crosscoder/everything-3m --cc L15
python transcend/interp/explain.py --cc-run runs/transcend/crosscoder/everything-3m --cc L15
python transcend/interp/concept_graph.py page        # the concept map (stages in its docstring)
```

| script | what it does | result |
| --- | --- | --- |
| `crosscoder.py` | one BatchTopK dictionary over both models' states; relative decoder norm per latent (0 = only 1000-1300, 1 = only 2400+); a layer sweep | [sweep.md](../../results/transcend/crosscoder/everything-3m/sweep.md), [cc-L15/report.md](../../results/transcend/crosscoder/everything-3m/cc-L15/report.md) |
| `explain.py` | each latent's best one- or two-fact explanation, held-out F1 (*explained* = F1 >= 0.5); its engine link; what the layer knows (probes to eval, threat, only-move gap) | [cc-L15/explain.md](../../results/transcend/crosscoder/everything-3m/cc-L15/explain.md) |
| `concept_graph.py` | the L11 latents laid out by how play combines them, with the mined dynamic concepts drawn on them; `.html` is the page template, `featured.json` the hand-labelled concepts | [night1-graph.html](../../results/transcend/overnight/night1-graph.html) |

Fact vocabularies: `predicates.py` (board facts: hanging pieces, pins, forks, checks, what the move does) and
`skill.py` (from Stockfish and Maia-2: only move, deep move, sound sacrifice, blunder, rare for 1100s). `pages.py`
draws the boards. The single-model SAE that preceded the crosscoder (`sae.py`) and the concept *paths* (latent i
turning on after j, per model; `concepts.py`) are in git history.
