# transcend

**Can a model trained to imitate weaker players play better than they do, and what inside it changes?** Two model
families, both trained on Lichess rating bands, and the interpretability work on the second.

| folder | question | headline |
| --- | --- | --- |
| [board/](board/README.md) | imitate 1100s on encoded boards, RL on easy puzzles: does it solve 2400 puzzles? | RL nearly doubles easy puzzles solved, leaves 2400 puzzles flat, costs ~400 game Elo |
| [pgn/](pgn/README.md) | the Transcendence paper's character-level PGN model, one per band | near-greedy, the 1000-1300 model plays ~350 Elo above its data |
| [interp/](interp/README.md) | what the two PGN models represent: a crosscoder and scored latent explanations | |
| [dynamic/](dynamic/README.md) | what separates the move a model plays from the one it doesn't, and does pushing it change play? | concepts replicate across seeds; 0 of 37 move the model when pushed |
| [clean/](clean/README.md) | the band games cleaned of cheaters and players far off their rating | |
