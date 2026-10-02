```
   __  __ _____ __  __  ___  ____  ___ __________
  |  \/  | ____|  \/  |/ _ \|  _ \|_ _|__  / ____|
  | |\/| |  _| | |\/| | | | | |_) || |  / /|  _|
  | |  | | |___| |  | | |_| |  _ < | | / /_| |___
  |_|  |_|_____|_|  |_|\___/|_| \_\___/____|_____|

              .-~~~~~~~~-.
          .-~~ ~~ ~~~~ ~~ ~~-.
        .~ ~~ ~~~~~~~~~~~~ ~~ ~.
       / ~~ ~~~~~~    ~~~~~~ ~~ \
      | ~~ ~~~            ~~~ ~~ |
      |~~ ~                  ~ ~~|
      |  |                    |  |
      |  |  ,==============,  |  |
      |  |                    |  |
     (|  |   ~~~~~~~~~~~~~~   |  |)
     ( )|    (  o  )(  o  )    |( )
      \ |     `---'  `---'     | /
          \          /\          /
           |       (_\/_)       |
           |     .-~~~~~~-.     |
           \      `-.__.-'      /
            \                  /
             \    `------'    /
              `.            .'
                 `-.______.-'
               _.--'`-.  .-'`--._

        A. N. Kolmogorov, 1903-1987
   "memory is just compression you can run"
```

**do memories matter?**

*a tiny lab for poking at a small reasoning model, running entirely on a laptop*

`Qwen3.5-2B` · `bf16` · `mlx-lm` · `Apple Silicon`

---

## the idea

Give a small model a hard multiple-choice question and a limited budget of
thinking tokens. What happens when the budget runs out? This repo is the
harness for measuring that, as a baseline for asking whether adding memory
changes the answer.

```
   question ──▶ ┌──────────────────┐
                │  <think> ...     │  ◀── up to `budget` tokens
                │  ... ... ... ... │
                └────────┬─────────┘
                         │ budget hit?  → force-close with </think>
                         ▼
                   "Answer: _"   ◀── model fills in the letter
                         │
                         ▼
                 ✔ correct / ✘ wrong
```

## roadmap

```
  [x] baseline harness        thinking budget, 5 benchmarks, seeded evals
  [ ] RL experiment           train against the budget, re-measure   ◀── next
  [ ] memorization            does adding memory change the answer?
```

RL comes first, so the memory experiments have a trained model to be compared
against, not just the raw baseline.

## what's inside

```
Memorize/
├── memorize/
│   ├── chat.py        talk to the model (thinking on by default)
│   ├── engine.py      batched generation with a thinking budget
│   ├── benchmarks.py  5 multiple-choice benchmarks, one format
│   └── evaluate.py    seeded, resumable scoring
├── data/              cached benchmark downloads  (gitignored)
├── results/           per-run summary.json (raw rollouts gitignored)
└── requirements.txt
```

| benchmark    | what it is                           |
| ------------ | ------------------------------------ |
| `mmlu_pro`   | harder, 10-option MMLU               |
| `mmlu_redux` | MMLU with broken labels filtered out |
| `ceval`      | Chinese multi-subject exam           |
| `supergpqa`  | graduate-level, many disciplines     |
| `gpqa`       | GPQA Diamond *(gated on HF)*         |

## quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python -m memorize.chat            # chat, with thinking
python -m memorize.chat --no-think # chat, direct answers

python -m memorize.evaluate --name baseline --bench mmlu_pro --n 300 --budget 2048
```

Runs are seeded (`--split-seed`, `--seed`) so results with the same `--n` are
comparable, and the evaluator resumes where it left off if interrupted.

## first numbers

A small pilot: 64 MMLU-Pro questions, 1024 thinking tokens.

```
accuracy       ██████████░░░░░░░░░░  50.0% ± 6.3%
forced close   ████████████████████  98.4%   ← budget ran out almost every time
no answer      █░░░░░░░░░░░░░░░░░░░   7.8%
```

Takeaway so far: at 1024 tokens the 2B model nearly always runs out of
thinking room, so the budget is the first thing to vary. Small sample, wide
error bar. Treat it as a smoke test, not a result.

## notes

- Weights are **bf16**, no quantization.
- Sampling follows the Qwen3.5-2B model card (`temp 1.0, top_p 0.95, top_k 20,
  presence penalty 1.5`). Greedy decoding makes this model loop.
- The presence penalty is dropped while writing the answer, so it can't push
  the model away from options its reasoning mentioned.

## license

MIT, see [LICENSE](LICENSE).

---

<sub>· ˚ ✦ · thanks for stopping by · ✦ ˚ ·</sub>
