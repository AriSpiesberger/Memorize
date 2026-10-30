# rating_bands

**Which moves does each rating band *never* find (ability), as opposed to finding them less
often (consistency)?** This folder also builds the puzzle strata the other experiments test on.

In 5-minute games the bands separate sharply. Requiring the player to follow the idea through
(not just find the first move) removes most accidental finds. Low-rated players convert hard
finds about half as often as easy ones; 2300+ players about 80% as often. Maia-2 only resolves
1100-2000 and is nearly flat on hard positions, so the strata come from real games and measured
puzzle ratings, not from Maia.

## Run

```bash
python rating_bands/download_month.py --month 2025-06
python rating_bands/collect_games.py --month 2025-06 --pgn data/lichess/2025-06.pgn.zst \
    --min-base 300 --max-base 300 --tag blitz                       # 5-minute games per band
python rating_bands/label_bands.py --bands data/lichess/bands/2025-06-blitz        # ~3 h
python rating_bands/discover.py --labels data/lichess/bands/2025-06-blitz/labels --maia-type blitz --target idea3
python rating_bands/show_sequences.py --labels data/lichess/bands/2025-06-blitz/labels
python rating_bands/puzzle_strata.py
```

| script | what it does |
| --- | --- |
| `download_month.py` | fetches a Lichess month over 8 connections, resumable |
| `collect_games.py` | games where both players are in one band: <1000, 1000-1300, 1300-1700, 1700-2000, 2000-2300, 2300+ (shared with Modal) |
| `label_bands.py` | per position: best move, found or not, engine depth needed, only-move, move type, and whether the player followed the idea through (`idea2`, `idea3`) |
| `find_curves.py` | find-rate by band against engine depth and move type, with the random-move floor |
| `discover.py` | a cross-fitted P(find) by rating gives each position a *discovery rating*; writes `strata_<target>.jsonl` |
| `show_sequences.py` | the hardest sequences strong players found, with Lichess links |
| `hard_puzzles.py` | hard Lichess puzzles played by Maia-2 at each rating |
| `puzzle_strata.py` | narrow, well-measured puzzle strata 400 points apart, with the expected solve-rate matrix (shared with Modal) |
