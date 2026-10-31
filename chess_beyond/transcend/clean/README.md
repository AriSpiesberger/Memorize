# transcend/clean

Cleaning a rating band's games before training on them (both the board model and the PGN models).

```bash
python transcend/clean/filter_cheaters.py --pgn data/lichess/bands/2025-06-train/1000-1300.pgn
python transcend/clean/maia_filter.py     --pgn data/lichess/bands/2025-06-train/1000-1300.pgn   # -> <pgn>.maia-clean.pgn
```

| script | what it does |
| --- | --- |
| `filter_cheaters.py` | looks every player up on Lichess's bulk-user API and drops games with an account marked for cheating (`--drop-closed`: closed accounts too) |
| `maia_filter.py` | drops games where Maia-2 says a player plays far above or below their rating |
| `maia.py` | Maia-2's board encoding and rating buckets without torch (also used by `../board/play_elo.py`, `../pgn/calibrate_levels.py`, `../interp/skill.py`) |
