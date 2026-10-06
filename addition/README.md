# addition

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

## run it

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
