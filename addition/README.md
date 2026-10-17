# addition

Pure RL from a **randomly initialised** transformer, in three steps: `rl_addition.py`
(this page's first half), `rl_tasks.py` (a free workspace, several tasks) and
`math100.py` (100 tasks, ten tiers). Per-run logs live in `results/`.

## rl_addition.py

A toy for asking what pure RL can learn with nothing to start from: a tiny
transformer, **randomly initialised**, taught n-digit addition with no
pretraining and no supervised loss.

```
  input    a a + b b =          digits of a, '+', digits of b, '='
  output   s s s                a+b, n+1 digits, least significant first
  policy   3-layer causal transformer (d=128), samples at temperature 1
  update   REINFORCE with a group baseline, like GRPO (G samples per problem)
  eval     greedy accuracy on TRAIN pairs and on HELD-OUT pairs never trained on
```

Two reward shapes are compared:

| reward   | signal                                   |
| -------- | ---------------------------------------- |
| `sparse` | 1 if the whole answer is right, else 0   |
| `dense`  | per digit: 1 if that digit is right      |

Held-out accuracy is the point: it separates learning the algorithm from
memorising the training pairs.

### run rl_addition.py

CPU only, no GPU needed. From the repo root:

```bash
python addition/rl_addition.py --n 2 --reward dense  --out addition/results/n2-dense.json
python addition/rl_addition.py --n 2 --reward sparse --out addition/results/n2-sparse.json
python addition/rl_addition.py --n 3 --reward dense  --steps 6000 --out addition/results/n3-dense.json
```

It prints train and held-out accuracy (whole answer, and per digit) every 250
steps. `--out` saves the args and that log as JSON.

| flag        | default | meaning                          |
| ----------- | ------: | -------------------------------- |
| `--n`       |       2 | digits per operand               |
| `--reward`  |   dense | `sparse` or `dense`              |
| `--steps`   |    3000 | optimizer steps                  |
| `--batch`   |      64 | problems per step                |
| `--group`   |       8 | samples per problem              |
| `--lr`      |    1e-3 | Adam learning rate               |
| `--holdout` |     0.2 | fraction of pairs never trained on |
| `--seed`    |       0 | seed                             |

## rl_tasks.py: a free workspace

Same recipe, several algorithmic tasks, plus `--scratch K`: before answering, the
model writes K free characters (digits, letters, space) that no reward looks at.
`--scratch 0` is the no-workspace baseline. Each eval also scores the held-out
problems with the workspace replaced by random characters (`held_scratch_randomised`):
if accuracy does not drop, the answer is not using it. Each run saves a few
held-out examples with their decoded workspace in `samples`.

```bash
python addition/rl_tasks.py --tasks modadd --scratch 8 --steps 12000 --lr 3e-4 --ent 0.01 --ent-answer 0.3 \
    --out addition/results/modadd-K8-long.json
```

## math100.py: a hundred tasks, one model

One model learns 100 tasks in ten tiers at once (task token + plain-text problem),
with a free-length workspace it can end by emitting `[end-think]` (capped by
`--max-think`, floored by `--min-think`). A task counts as saturated the first
time it reaches `--saturate` (default 90%) held-out accuracy; the order is the
result. Output goes to `--out`: `log.jsonl`, `samples.jsonl`, `args.json` and a
checkpoint (`ckpt.pt`, gitignored: model files are not pushed). The run resumes
from the checkpoint if the directory has one.

```bash
python addition/math100.py --list                            # every task with an example
python addition/math100.py --out addition/results/math100    # train; GPU recommended
python addition/math100.py --report addition/results/math100 # saturation order
```

## Results so far

What can reward alone teach a **randomly initialised** transformer: no
pretraining, no supervised loss? 
**1. Addition.** A tiny model learns n-digit addition, comparing a sparse reward
(whole answer right) with a dense one (per digit), and scoring pairs it never
trained on (`rl_addition.py`).

**2. A free workspace.** Before answering, the model may write K free characters
that no reward looks at (`rl_tasks.py`). On modular addition (mod 97) with K=8,
held-out accuracy reaches 99.8%, but scrambling the workspace into random
characters leaves it at 99.8%, so the answer does not use it. With no workspace
(K=0) the same task reaches 98% by step 2000, versus about step 6000 with K=8.
One seed each, so this is suggestive, not conclusive.

**3. math100.** One model, 100 tasks in ten tiers (one-digit arithmetic up to
eigenvectors), a task token to tell them apart, and a workspace of up to 64
characters it can end on its own. The question is the order the tasks saturate
(90% held-out accuracy). In the overnight run (d=512, batch 256), by step 57,000,
6 tasks had reached 90%, all tier-1 arithmetic and in this order: `even`,
`compare`, `double`, `half`, `succ`, `pred`. Nothing above tier 1 has. That run
set a 2-character workspace minimum (`--min-think 2`) and the model kept it at
about 2-3 characters, so it has not learned to think longer yet. An earlier
Mac run (d=256, batch 32, no floor) had only `even` after 18,500 steps. The task
ranges were widened between the two runs, so don't compare them directly.

```bash
python addition/rl_addition.py --n 2 --reward dense --out addition/results/n2-dense.json
python addition/math100.py --list                                # every task, with an example
python addition/math100.py --out addition/results/math100        # resumes if a checkpoint exists
python addition/math100.py --report addition/results/math100     # saturation order
```
