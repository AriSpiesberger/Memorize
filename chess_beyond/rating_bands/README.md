# rating_bands

**Which moves does each rating band *never* find (ability), as opposed to finding them less
often (consistency)?** This folder also builds the puzzle strata the other experiments test on.

Commands and the full script table are in the
[chess_beyond README](../README.md#experiment-rating_bands).

| step | script |
| --- | --- |
| download a Lichess month | `download_month.py` |
| split games into rating bands | `collect_games.py` |
| label every position (best move, found or not, depth needed, move type) | `label_bands.py` |
| find-rate by band | `find_curves.py` |
| a "discovery rating" per position, and a stratified set | `discover.py` |
| read the hardest sequences strong players found | `show_sequences.py` |
| hard puzzles, played by Maia-2 at each rating | `hard_puzzles.py` |
| narrow, well-measured puzzle strata (1100 ... 2800) | `puzzle_strata.py` |
