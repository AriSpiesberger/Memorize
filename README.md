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
🔄 GRPO (Mac) · 🔄 label-split (GPU) · 🔄 addition toy (CPU) · 🔄 chess beyond the teachers (GPU) ·
⬜ memorization

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

## Chess: beyond the teachers (PyTorch, CUDA)

Can a model trained on human games find the moves those humans miss? The main
experiment imitates 1100-level Lichess players, then does RL rewarded only for
solving easy (900-1200) puzzles, and tests on 20,000 puzzles rated 2400 that an
1100 is expected to solve ~0.07% of the time. So far: imitation reaches a puzzle
Elo of ~1140 and solves ~6.6% of the 2400s; RL on easy puzzles adds ~300 Elo but
barely moves the 2400 rate. Everything is in [chess_beyond/](chess_beyond/), with
results in [chess_beyond/results/transcend/](chess_beyond/results/transcend/summary.md).

## Addition toy (PyTorch, CPU)

A tiny transformer, randomly initialised, learns n-digit addition from reward
alone: no pretraining, no supervised loss. It compares a sparse reward (whole
answer right) with a dense one (per digit) and scores held-out pairs it never
trained on. See [addition/](addition/) for details.

```bash
python addition/rl_addition.py --n 2 --reward dense --out addition/results/n2-dense.json
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
├── addition/             toy: pure RL from random init on n-digit addition (and math100)
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
