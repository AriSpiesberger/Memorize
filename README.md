<h1 align="center">Memorize</h1>

<p align="center"><i>"memory is just compression you can run"</i></p>

<p align="center"><b>Do memories matter?</b><br>
A small lab for poking at models on a laptop and one GPU.</p>

<p align="center">
<code>MLX on Apple Silicon</code> · <code>PyTorch on CUDA</code> · <a href="LICENSE">MIT</a>
</p>

---

## Why

Small models are cheap to train, probe and break, which makes them a good place
to ask what a model has to know, what it can be told, and what it must work out
for itself. The long-term question is memory: does giving a small model
something to remember change what it can do? Before that can be answered
cleanly, a few baseline questions come first. Each experiment here is one of
them.

## Experiments

| folder | question | status |
| --- | --- | :-: |
| [memorize/](memorize/) | What does a small reasoning model do when its thinking budget runs out, and what do SFT, RL and label noise change? | 🔄 |
| [addition/](addition/) | What can reward alone teach a randomly initialised transformer, with and without a free workspace? | 🔄 |
| [chess_beyond/](chess_beyond/) | Can a model trained on human games find the moves those humans miss? | 🔄 |
| memory itself | Does adding memory change the answer? | ⬜ |

Each folder has its own README with the commands, results and details, including
what runs on a Mac, a home GPU, or Modal. Cloud-only code is kept in its own
folder (`chess_beyond/modal/`), apart from the code it shares with the home GPU.

## Layout

```
Memorize/
├── memorize/        reasoning budgets, SFT, RL and label noise on a 2B model (MLX / CUDA)
├── addition/        pure RL from random init: addition, a free workspace, 100 math tasks
├── chess_beyond/    chess: imitation, puzzle RL, rating bands, activation probes (home GPU + Modal)
└── tools/           check_repo.py: run before pushing (labs and Modal stay apart, no weights, no copies)
```

## Getting started

```bash
python3 -m venv .venv && source .venv/bin/activate     # Windows: py -3.12 -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt                        # MLX on macOS, CUDA PyTorch elsewhere
```

Then pick a folder and follow its README. Weights are not kept in git: shared
adapters live on [Hugging Face](https://huggingface.co/Arisp/memorize-instruct).

## License

MIT, see [LICENSE](LICENSE).
