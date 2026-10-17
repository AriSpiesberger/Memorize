<h1 align="center">Memorize</h1>

<p align="center"><i>"memory is just compression you can run"</i></p>

<p align="center"><b>Do memories matter?</b><br>
A small lab for poking at a reasoning model on a laptop and one GPU.</p>

<p align="center">
<code>Qwen3.5-2B</code> · <code>bf16</code> · <code>MLX on Apple Silicon</code> · <code>PyTorch on CUDA</code> · <a href="LICENSE">MIT</a>
</p>

---

Give a small model a hard multiple-choice question and a limited budget of
thinking tokens. What happens when the budget runs out? This repo measures
that, and holds the training code (SFT, then GRPO) that teaches a base model
the answer format first, so any later memory experiment has a trained model to
compare against.

```
question ─▶ ┌─────────────────┐
            │ <think> ...     │ ◀─ up to `budget` tokens
            └────────┬────────┘
                     │ budget hit? force-close with </think>
                     ▼
               "Answer: _"  ─▶ ✔ correct / ✘ wrong
```

**Status:** ✅ harness · ✅ baselines · ✅ SFT warm-up (91% strict format) ·
✅ label-split (4 benchmarks) · 🔄 GRPO (Mac) · 🔄 pure-RL toys: addition, math100 ·
🔄 chess beyond the teachers (GPU) · ⬜ memorization

## Quick start

One `requirements.txt` serves both machines (markers pick MLX on macOS, CUDA
PyTorch elsewhere).

```bash
# macOS (Apple Silicon)
python3 -m venv .venv && source .venv/bin/activate
# Windows / Linux (NVIDIA):  py -3.12 -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt

python -m memorize.chat                 # chat with the model, thinking on
python -m memorize.evaluate --name baseline --bench mmlu_pro --n 300 --budget 2048
```

Runs are seeded, so results with the same `--n` are comparable, and evaluators
resume if interrupted.

### Which command do I want?

| I want to...                           | Run                                                          | Machine |
| -------------------------------------- | ------------------------------------------------------------ | ------- |
| Chat with the model                    | `python -m memorize.chat`                                    | Mac     |
| Score a thinking budget on a benchmark | `python -m memorize.evaluate --bench mmlu_pro --budget 2048` | Mac     |
| Train the instruction SFT              | `python -m memorize.sft_data`, then `python -m memorize.sft` | Mac     |
| Train the same SFT on a GPU            | `python -m memorize.sft_torch`                               | CUDA    |
| Run GRPO / Dr. GRPO                    | `python -m memorize.grpo --model models/sft-fused`           | Mac     |
| Run the label-split experiment         | `python run_split.py -- --bench mmlu_redux`                 | CUDA    |
| Download the shared instruct model     | `python -m memorize.hub pull instruct`                       | any     |
| Train pure RL on 100 math tasks        | `python addition/math100.py --out addition/results/<name>`   | GPU     |
| See which math100 tasks saturated      | `python addition/math100.py --report addition/results/<name>` | any     |

<details>
<summary>SFT → fuse → RL → format check, end to end (Mac)</summary>

```bash
python -m memorize.sft_data
python -m memorize.sft --out adapters/sft-run2
python -m mlx_lm fuse --model Qwen/Qwen3.5-2B-Base \
    --adapter-path adapters/sft-run2 --save-path models/sft-fused
python -m memorize.grpo --model models/sft-fused --out adapters/grpo-run1
python -m memorize.eval_format --model models/sft-fused --name sft
python -m memorize.compare sft drgrpo-run1      # paired test, before vs after
```
</details>

## Label-split experiment (PyTorch, CUDA)

MMLU-Pro is cut into thirds: **A** is trained with random labels, **B** with the
real ones, **C** is held out. A and B train together as direct `ANSWER: X`
replies; C is scored every 25 steps, alongside samples of A and B.

Everyday chats with no math or science (`memorize.general_data`) are mixed into
training (`--replay-frac`, default 25% of A+B; 0 turns it off), and their
held-out loss is logged every eval as a fourth panel, so you can see whether
general ability drifts.

`run_split.py` does everything: venv, requirements, CUDA check, downloads, then
the run. It starts from the instruct model (downloaded from Hugging Face, or
trained locally if that fails) and needs only Python 3.10+. Output lands in
`results/label-split/<date>_<benchmark>[_<name>]/` (`train.log`, `metrics.jsonl`, `curves.png`, `adapter/`).

```bash
python run_split.py                       # -> results/label-split/2026-10-05_mmlu_pro/
python run_split.py --name mac-sft --mlx-adapter adapters/sft-run2   # start from the Mac's MLX SFT
python run_split.py --name nogold --detach -- --exclude-gold --epochs 6
python run_split.py --dry-run
```

### What it shows so far

One run and one seed per benchmark, from the instruct model. *Fit* is how often
the model's answer matches the random label it was trained on. Each cell is
start of training → end.

| benchmark  | epochs | C: held-out accuracy | A: fit to random labels | B: accuracy on real labels |
| ---------- | -----: | -------------------- | ----------------------- | -------------------------- |
| mmlu_pro   |    3.1 | 33.8% → 30.6%        | 11.2% → 83.2%           | 34.2% → 97.4%              |
| mmlu_redux |      3 | 66.6% → 53.8%        | 25.4% → 93.6%           | 61.2% → 99.2%              |
| ceval      |      4 | 60.2% → 57.8%        | 28.3% → 100%            | 60.3% → 99.8%              |
| supergpqa  |      2 | 20.8% → 35.1%        | 9.4% → 46.6%            | 23.0% → 81.0%              |

- The model memorises both the random labels and the real ones, and neither
  helps on C. Held-out accuracy fell on three of the four benchmarks, most on
  MMLU-Redux (about 13 points).
- SuperGPQA is the exception: it started near chance, went up, and had
  memorised the least (47% fit after 2 epochs).
- With general-chat replay on (MMLU-Redux), held-out loss on everyday chats
  moved from 1.22 to 1.30 over 3 epochs, a small drift.
- Curves and per-run configs are in `results/label-split/`.

## Chess: beyond the teachers (PyTorch, CUDA)

Can a model trained on human games find the moves those humans miss? The main
experiment imitates 1100-level Lichess players, then does RL rewarded only for
solving easy (900-1200) puzzles, and tests on 20,000 puzzles rated 2400 that an
1100 is expected to solve ~0.07% of the time. So far: imitation reaches a puzzle
Elo of ~1140 (game Elo ~1160 against Maia-2) and solves ~6.6% of the 2400s; RL on
easy puzzles adds ~300 puzzle Elo, barely moves the 2400 rate, and costs ~400 Elo
in real games. Everything is in [chess_beyond/](chess_beyond/), with
results in [chess_beyond/results/transcend/](chess_beyond/results/transcend/summary.md).

## Pure RL from scratch (PyTorch)

What can reward alone teach a **randomly initialised** transformer: no
pretraining, no supervised loss? Three steps, all in [addition/](addition/).

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

## Results so far

MMLU-Pro accuracy on the seeded held-out split. Samples are small, so mind the
error bars. The thinking-model rows are a different model from the base-model
rows, so they aren't like-for-like.

| model                      | setup                                   |   n | accuracy     |
| -------------------------- | --------------------------------------- | --: | ------------ |
| Qwen3.5-2B-Base            | 5-shot, direct answer                   | 300 | 38.0% ± 2.8% |
| Qwen3.5-2B-Base            | 5-shot, chain of thought                | 300 | 39.3% ± 2.8% |
| Qwen3.5-2B-Base + SFT      | zero-shot chat CoT, after epoch 1       | 300 | 48.7% ± 2.9% |
| Qwen3.5-2B-Base + instruct | zero-shot direct letter (label-split C) | 500 | 38.0% ± 2.2% |
| Qwen3.5-2B (thinking)      | 1024 thinking tokens                    |  64 | 50.0% ± 6.3% |
| Qwen3.5-2B (thinking)      | 2048 thinking tokens                    |  64 | 54.7% ± 6.2% |

- The first SFT row also hit the required `ANSWER: X` last line on 91.3% of
  replies, which is what the RL stage builds on.
- The instruct row scores the letter straight after `ANSWER:` with no reasoning,
  so compare it with the direct 5-shot row, not the CoT ones. It passes 18/19
  instruction probes.
- The thinking model is force-closed 95% of the time at 2048 tokens (98% at
  1024), so the budget is the first thing to vary.
- The 64-question rows are smoke tests, not results.

## Repo map

```
Memorize/
├── run_split.py          one-command launcher for the label-split experiment
├── memorize/
│   ├── chat.py           talk to the model
│   ├── engine.py         batched generation with a thinking budget
│   ├── benchmarks.py     5 multiple-choice benchmarks, one format
│   ├── prompts.py        per-benchmark prompts and answer line
│   ├── evaluate.py       seeded, resumable scoring
│   ├── eval_mmlu_pro.py  MMLU-Pro: official few-shot, or chat CoT
│   ├── eval_format.py    strict-format and instruction-following check
│   ├── compare.py        paired, question-by-question comparison of two runs
│   ├── stats.py          McNemar's exact test and intervals
│   ├── sft_data.py       build the instruction-tuning set
│   ├── sft.py            LoRA SFT on MLX          (sft_torch.py: same on CUDA)
│   ├── general_data.py   build the math/science-free replay chats
│   ├── probes.py         instruction-following probes
│   ├── grpo.py           GRPO / Dr. GRPO with a KL penalty
│   ├── label_split.py    A random / B correct / C held-out SFT run
│   ├── plot_split.py     curves for a label_split run
│   ├── mlx_to_peft.py    convert an MLX LoRA to PEFT
│   └── hub.py            push / pull adapters on Hugging Face
├── addition/             pure RL from random init: addition, workspace tasks, math100
├── chess_beyond/         can models trained on humans find the moves humans miss?
├── adapters/             LoRA configs + models.json (weights live on HF)
├── results/              baselines, plus label-split/<date>_<benchmark>/ per run
├── data/                 benchmark cache      (gitignored)
└── models/               fused models for RL  (gitignored)
```

Benchmarks: `mmlu_pro` (hard, 10-option) · `mmlu_redux` (MMLU, broken labels
removed) · `ceval` (Chinese exams) · `supergpqa` (graduate level) · `gpqa`
(Diamond, gated on HF).

## Models

[Arisp/memorize-instruct](https://huggingface.co/Arisp/memorize-instruct) is a
rank-8 LoRA on `Qwen/Qwen3.5-2B-Base`, trained with `memorize.sft_torch`. Its
model card holds the exact recipe. Weights are shared through Hugging Face, not
git; [adapters/models.json](adapters/models.json) is the registry.

```python
from peft import PeftModel
model = PeftModel.from_pretrained(base_model, "Arisp/memorize-instruct")
```

## Notes

- Weights are **bf16**, no quantization.
- Sampling follows the Qwen3.5-2B model card (`temp 1.0, top_p 0.95, top_k 20,
  presence penalty 1.5`); greedy decoding makes this model loop.
- The presence penalty is dropped while writing the answer, so it can't push
  the model away from options its reasoning mentioned.

## License

MIT, see [LICENSE](LICENSE).
