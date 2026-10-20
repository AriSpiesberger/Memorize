# addition/results

Logs from the runs described in [../README.md](../README.md). The `.json` files come from
`rl_tasks.py` (args, eval log and a few held-out samples with their decoded workspace); the
folders come from `math100.py` (`args.json`, `log.jsonl`, `samples.jsonl`; checkpoints are
not in git).

Several early runs are kept because they show *why* the final settings are what they are:
without an entropy bonus on the answer (`--ent-answer`), the policy collapses to one constant
answer within a few hundred steps and never recovers.

## Parity (is the number of 1s odd?)

| file | bits | workspace | answer entropy bonus | held-out | what it shows |
| --- | --: | --: | --: | --: | --- |
| `parity-K0.json` | 8 | 0 | 0 | 0.41 | collapsed to a constant answer |
| `parity-K8.json` | 8 | 8 | 0 | 0.59 | collapsed; the workspace also collapsed (`00000000`) |
| `parity3-K0.json` | 3 | 0 | 0 | — | collapsed even on 3 bits (train 0.57 = the majority answer) |
| `parity3-ent.json` | 3 | 0 | 0.05 | — | a weak bonus is not enough |
| `parity8-K0-ent03.json` | 8 | 0 | 0.3 | **0.98** | learned, and generalises to unseen inputs |
| `parity16-K0-ent03.json` | 16 | 0 | 0.3 | 0.50 | at chance: where a workspace would have to help |

With 3 bits there are only 8 inputs, so the held-out column is one problem and means nothing.

## Modular addition, (a + b) mod 97

| file | workspace | steps | held-out | workspace scrambled | what it shows |
| --- | --: | --: | --: | --: | --- |
| `modadd-K0-ent03.json` | 0 | 6,000 | 0.99 | — | learned by about step 2,000 |
| `modadd-K8.json` | 8 | 4,000 | 0.21 | 0.20 | a workspace of noise delays takeoff by ~2,500 steps |
| `modadd-K8-long.json` | 8 | 12,000 | **1.00** | 1.00 | solved, but the answer ignores the workspace |

"Workspace scrambled" is held-out accuracy with the workspace replaced by random characters:
equal to the real accuracy means the model does not read it.

## math100 (100 tasks, one model)

| folder | model | batch | workspace floor | last step logged | notes |
| --- | --- | --: | --: | --: | --- |
| `math100/` | d=256, 4 layers | 32 | none | 18,500 | Mac run; only `even` saturated |
| `math100-overnight/` | d=512, 4 layers | 256 | 2 | 57,000 | six tier-1 tasks saturated; task ranges widened since `math100/` |
| `math100-4090/` | d=256, 4 layers | 256 | 16 | 0 | started on the 4090; only the step-0 eval is in git |

Saturation order for any of them: `python addition/math100.py --report addition/results/<folder>`.
