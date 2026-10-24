# modal

The cloud side of `chess_beyond`: two Modal apps that run the lab's own scripts in
containers. **No chess logic lives here.** These files only describe the container,
mount the lab (`chess_beyond/`) into it, and call scripts from the shared and
experiment folders, so a script behaves the same on Modal as on a home GPU.

Run every command from `chess_beyond/`, with the repo's venv (`modal` is in
`requirements.txt`).

```bash
export MODAL_PROFILE=arispiesberger
```

## What runs here

| app | file | machine | what it does |
| --- | --- | --- | --- |
| `chess-beyond-data` | [modal_app.py](modal_app.py) | CPU, half a core per month | builds the upsampled games database: 10M games per band (both players in the band, base time >= 3 min) for 1000-1300 and 2400+ |
| `chess-beyond-train` | [modal_train.py](modal_train.py) | CPU for `prepare`, GPU for training (default A100-80GB, `CHESS_GPU=H100` to change) | builds the SFT data, puzzle strata and probe set, then trains the PGN model per band |

```bash
# database
modal run modal/modal_app.py::smoke                    # one month, 20,000 games per band
modal run --detach modal/modal_app.py::build_games     # every month needed, newest first, then merge
modal run modal/modal_app.py::merge                    # re-run the merge alone

# PGN model
modal run --detach modal/modal_train.py::prepare                      # data for both bands + the probe set
modal run modal/modal_train.py::smoke --band 1000-1300                # 200 steps, two evals, snapshots
modal run --detach modal/modal_train.py::train_band --band 1000-1300  # the full run
modal run --detach modal/modal_train.py::train_band --band 2400+
```

`--detach` keeps a run going after you close the terminal. Modal stops a function after
24 h, so training saves at 23 h, hands over to a fresh container and resumes from its
last eval. The fine print for each step is in the docstring at the top of each file.

## Storage

Two Modal Volumes hold everything; nothing is kept in git.

| Volume | mounted at (in the container) | holds |
| --- | --- | --- |
| `chess-data` | `chess_beyond/data` (where `paths.py` looks) | band games, `upsampled/<band>.pgn`, puzzle strata, PGN training shards |
| `chess-runs` | `chess_beyond/runs` | checkpoints, logs, probe figures |

```bash
modal volume ls chess-data lichess/bands/upsampled
modal volume get chess-runs transcend ./runs/transcend     # copy results to a home machine
```

## Which code is shared with a home GPU

The container gets a copy of `chess_beyond/` (minus `data`, `runs`, `models`, `tools`,
`results` and this folder). Modal calls these scripts, so changing them changes Modal
runs too:

| calls | scripts |
| --- | --- |
| `modal_app.py` | `rating_bands/collect_games.py` |
| `modal_train.py` | `rating_bands/collect_games.py`, `rating_bands/puzzle_strata.py`, `transcend/make_pgn_data.py`, `transcend/pgn_probe.py`, `transcend/train_pgn.py` |
| imported by those | `paths.py`, `common.py`, `probe.py`, `transcend/pgn_model.py` |

Everything else in `chess_beyond/` is not used by Modal. See
[where code runs](../README.md#where-code-runs) for the full map.
