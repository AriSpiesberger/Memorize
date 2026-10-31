# memorize

**What does a small reasoning model do when its thinking budget runs out, and what do SFT, RL and label noise
change?** A harness and experiments on `Qwen3.5-2B` (bf16), on MLX (Apple Silicon) and PyTorch (CUDA). The training
code (SFT, then GRPO) teaches a base model the answer format first, so later experiments have a trained model to
compare against.

Commands run from the repo root. One `requirements.txt` serves both machines (markers pick MLX on macOS, CUDA PyTorch
elsewhere): `python3 -m venv .venv`, activate, `pip install -r requirements.txt`.

| I want to... | run | machine |
| --- | --- | --- |
| chat with the model | `python -m memorize.chat` | Mac |
| score a thinking budget | `python -m memorize.evaluate budget --name baseline --bench mmlu_pro --n 300 --budget 2048` | Mac |
| check answer format and instruction following | `python -m memorize.evaluate format --model models/sft-fused --name sft` | Mac |
| MMLU-Pro by the official protocol, or chat CoT | `python -m memorize.evaluate mmlu_pro --mode cot --out memorize/results/base/mmlu_pro.jsonl` | Mac |
| compare two runs question by question | `python -m memorize.evaluate compare sft drgrpo-run1` | any |
| train the instruction SFT | `python -m memorize.sft_data`, then `python -m memorize.sft` (`sft_torch` on CUDA) | Mac / CUDA |
| run GRPO / Dr. GRPO | `python -m memorize.grpo --model models/sft-fused` | Mac |
| run the label-split experiment | `python memorize/split/run_split.py` ([split/](split/README.md)) | CUDA |
| download the shared instruct model | `python -m memorize.hub pull instruct` | any |

Every evaluation is seeded (the same `--n` gives the same questions) and resumes if interrupted. SFT to RL, end to
end: `sft_data` -> `sft --out memorize/adapters/sft-run2` -> `python -m mlx_lm fuse --model Qwen/Qwen3.5-2B-Base
--adapter-path memorize/adapters/sft-run2 --save-path models/sft-fused` -> `grpo` -> `evaluate format` and `compare`.

## Results so far

MMLU-Pro accuracy on the seeded held-out split. Samples are small, so mind the error bars; the thinking-model rows are
a different model from the base-model rows.

| model | setup | n | accuracy |
| --- | --- | --: | --- |
| Qwen3.5-2B-Base | 5-shot, direct answer | 300 | 38.0% ± 2.8% |
| Qwen3.5-2B-Base | 5-shot, chain of thought | 300 | 39.3% ± 2.8% |
| Qwen3.5-2B-Base + SFT | zero-shot chat CoT, after epoch 1 | 300 | 48.7% ± 2.9% |
| Qwen3.5-2B-Base + instruct | zero-shot direct letter (label-split C) | 500 | 38.0% ± 2.2% |
| Qwen3.5-2B (thinking) | 1024 thinking tokens | 64 | 50.0% ± 6.3% |
| Qwen3.5-2B (thinking) | 2048 thinking tokens | 64 | 54.7% ± 6.2% |

- The first SFT row also hit the required `ANSWER: X` last line on 91.3% of replies, which is what RL builds on.
- The instruct row scores the letter straight after `ANSWER:` with no reasoning, so compare it with the direct 5-shot
  row. It passes 18/19 instruction probes.
- The thinking model is force-closed 95% of the time at 2048 tokens (98% at 1024), so the budget is the first thing
  to vary. The 64-question rows are smoke tests.
- Label noise: [split/](split/README.md) (memorising random and real labels; neither helps held-out questions).

## Code

| file | what it does |
| --- | --- |
| `benchmarks.py`, `prompts.py` | five multiple-choice benchmarks in one format; EvalScope's prompt and answer line for each |
| `engine.py` | batched generation with a thinking budget (force-closed when it runs out) |
| `evaluate.py` | `budget`, `format`, `mmlu_pro`, `compare`: every evaluation, seeded and resumable |
| `stats.py` | McNemar's exact test and intervals |
| `chat.py` | talk to the model |
| `sft_data.py`, `general_data.py` | the instruction-tuning set; the math/science-free replay chats |
| `sft.py`, `sft_torch.py`, `sft_common.py`, `probes.py` | LoRA SFT on MLX and on CUDA, shared batching, instruction probes |
| `grpo.py` | GRPO / Dr. GRPO with a KL penalty |
| `mlx_to_peft.py`, `hub.py` | convert an MLX LoRA to PEFT; push / pull adapters on Hugging Face |
| `split/` | the label-split experiment |
| `adapters/`, `results/` | LoRA configs, RL logs and `models.json` (weights live on Hugging Face); results |

Benchmarks: `mmlu_pro` (hard, 10-option), `mmlu_redux` (MMLU, broken labels removed), `ceval` (Chinese exams),
`supergpqa` (graduate level), `gpqa` (Diamond, gated on HF). Gitignored at the repo root: `data/` (benchmark cache),
`models/` (fused models for RL).

**Model.** [Arisp/memorize-instruct](https://huggingface.co/Arisp/memorize-instruct): a rank-8 LoRA on
`Qwen/Qwen3.5-2B-Base` trained with `memorize.sft_torch`; its card holds the recipe, and
[adapters/models.json](adapters/models.json) is the registry. Sampling follows the Qwen3.5-2B model card (temp 1.0,
top_p 0.95, top_k 20, presence penalty 1.5; greedy decoding makes this model loop); the presence penalty is dropped
while writing the answer.
