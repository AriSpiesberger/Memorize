```
   __  __ _____ __  __  ___  ____  ___ __________
  |  \/  | ____|  \/  |/ _ \|  _ \|_ _|__  / ____|
  | |\/| |  _| | |\/| | | | | |_) || |  / /|  _|
  | |  | | |___| |  | | |_| |  _ < | | / /_| |___
  |_|  |_|_____|_|  |_|\___/|_| \_\___/____|_____|
```

**do memories matter?**

*a tiny lab for poking at a small reasoning model, on a laptop and one GPU*

`Qwen3.5-2B` · `bf16` · `mlx-lm on Apple Silicon` · `PyTorch on CUDA`

---

## the idea

Give a small model a hard multiple-choice question and a limited budget of
thinking tokens. What happens when the budget runs out? This repo is the
harness for measuring that, as a baseline for asking whether adding memory
changes the answer. It also holds the training scripts (SFT, then GRPO) used to
teach a base model the answer format before any memory is added, and the
evaluators that check both accuracy and format.

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
  [x] base-model baselines    5-shot, direct and chain-of-thought
  [x] SFT warm-up             LoRA teaches the ANSWER line: 91% strict format
  [~] RL experiment           GRPO / Dr. GRPO, smoke test running    ◀── now (Mac)
  [~] label-split experiment  train on random + correct labels, test held out  ◀── now (GPU)
  [~] addition toy            pure RL from random init on n-digit addition (CPU)
  [ ] memorization            does adding memory change the answer?
```

RL comes first, so the memory experiments have a trained model to be compared
against, not just the raw baseline.

## what's inside

```
Memorize/
├── memorize/
│   ├── chat.py           talk to the model (thinking on by default)
│   ├── engine.py         batched generation with a thinking budget
│   ├── benchmarks.py     5 multiple-choice benchmarks, one format
│   ├── prompts.py        zero-shot prompt and required answer line per benchmark
│   ├── evaluate.py       seeded, resumable scoring with a thinking budget
│   ├── eval_mmlu_pro.py  MMLU-Pro: official few-shot protocol, or chat CoT
│   ├── eval_format.py    strict-format and instruction-following check
│   ├── compare.py        paired, question-by-question comparison of two runs
│   ├── stats.py          McNemar's exact test and intervals
│   ├── sft_data.py       build the instruction-tuning set
│   ├── sft.py            LoRA fine-tuning, with probes after each epoch
│   ├── sft_torch.py      the same SFT recipe on PyTorch + CUDA
│   ├── probes.py         instruction-following probes shared by both
│   ├── grpo.py           GRPO / Dr. GRPO with a KL penalty
│   ├── label_split.py    A random / B correct / C test SFT run (PyTorch, CUDA)
│   ├── plot_split.py     curves for a label_split run
│   ├── mlx_to_peft.py    convert an MLX LoRA for PyTorch
│   └── hub.py            push / pull adapters to and from Hugging Face
├── run_split.py          one command: set up, get the SFT model, run label_split
├── addition/             toy: pure RL from random init on n-digit addition
├── adapters/             LoRA configs + models.json  (instruct model on HF)
├── models/               fused models for RL  (gitignored)
├── data/                 cached benchmark downloads  (gitignored)
├── results/              per-run summaries (raw rollouts gitignored)
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

One `requirements.txt` serves both machines: environment markers install
`mlx-lm` on macOS and CUDA PyTorch + transformers + peft on Windows/Linux.

```bash
# macOS (Apple Silicon, MLX)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Windows / Linux (NVIDIA)
py -3.12 -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
```

Runs are seeded (`--split-seed`, `--seed`) so results with the same `--n` are
comparable, and the evaluators resume where they left off if interrupted.

```bash
python -m memorize.chat            # chat, with thinking
python -m memorize.chat --no-think # chat, direct answers

python -m memorize.evaluate --name baseline --bench mmlu_pro --n 300 --budget 2048

# SFT, then fuse the adapter into a full model for RL
python -m memorize.sft_data
python -m memorize.sft --out adapters/sft-run2
python -m mlx_lm fuse --model Qwen/Qwen3.5-2B-Base \
    --adapter-path adapters/sft-run2 --save-path models/sft-fused

# RL, then check format and instruction following
python -m memorize.grpo --model models/sft-fused --out adapters/grpo-run1
python -m memorize.eval_format --model models/sft-fused --name sft
python -m memorize.compare sft drgrpo-run1      # paired test, before vs after
```

### label-split experiment (PyTorch, CUDA)

MMLU-Pro is cut into thirds: **A** trained on with random labels, **B** with
the real ones, and **C** held out. A and B are trained together as direct
`ANSWER: X` replies, and C is scored every 25 steps (along with samples of A
and B) from the letter distribution after `ANSWER:`.

`run_split.py` does everything: venv, requirements, CUDA check, downloads (with
retries), then the run. It starts from the instruction SFT
(`adapters/sft-run2-torch`, the sft-run2 recipe on Qwen3.5-2B-Base) and trains
that first if it isn't there yet. It uses only the standard
library, so any Python 3.10+ can start it, on Windows or Linux. Output goes to
`results/<name>/` (`train.log`, `metrics.jsonl`, `curves.png` redrawn after
each eval, `adapter/`).

```bash
python run_split.py --name sft-split                                  # local SFT, built if missing
python run_split.py --name mac-sft --mlx-adapter adapters/sft-run2    # the Mac's MLX SFT instead
python run_split.py --name nogold --detach -- --exclude-gold --epochs 6
python run_split.py --name test --dry-run
```

### addition toy (PyTorch, CPU)

A tiny transformer, randomly initialised, learns n-digit addition from reward
alone: no pretraining, no supervised loss. It compares a sparse reward (whole
answer right) with a dense one (per digit) and scores held-out pairs it never
trained on. See [addition/](addition/) for details.

```bash
python addition/rl_addition.py --n 2 --reward dense --out addition/results/n2-dense.json
```

## models

The instruct model is on Hugging Face:
[Arisp/memorize-adapters](https://huggingface.co/Arisp/memorize-adapters),
folder `sft-run2-torch`. It is a LoRA on `Qwen/Qwen3.5-2B-Base` trained with the
sft-run2 recipe (`memorize.sft_torch`), and the start point for the label-split
experiment; `run_split.py` downloads it when it isn't in `adapters/`.

```python
from peft import PeftModel
model = PeftModel.from_pretrained(base_model, "Arisp/memorize-adapters", subfolder="sft-run2-torch")
```

`python -m memorize.hub pull sft-run2-torch` fetches it into `adapters/`.

## numbers so far

Accuracy on MMLU-Pro, on the seeded held-out split. Small samples, so read the
error bars. The thinking-model rows are a different model from the base-model
rows, so they are not a like-for-like comparison.

| model                       | setup                              |   n | accuracy     |
| --------------------------- | ---------------------------------- | --: | ------------ |
| Qwen3.5-2B-Base             | 5-shot, direct answer              | 300 | 38.0% ± 2.8% |
| Qwen3.5-2B-Base             | 5-shot, chain of thought           | 300 | 39.3% ± 2.8% |
| Qwen3.5-2B-Base + SFT       | zero-shot chat CoT, after epoch 1  | 300 | 48.7% ± 2.9% |
| Qwen3.5-2B-Base + SFT (CUDA)| zero-shot direct letter (label-split C) | 500 | 38.0% ± 2.2% |
| Qwen3.5-2B (thinking)       | 1024 thinking tokens               |  64 | 50.0% ± 6.3% |
| Qwen3.5-2B (thinking)       | 2048 thinking tokens               |  64 | 54.7% ± 6.2% |

The first SFT row also hit the required `ANSWER: X` last line on 91.3% of
replies, which is what the RL stage builds on. The CUDA SFT row scores the
letter straight after `ANSWER:` with no reasoning (the label-split protocol), so
it compares with the direct 5-shot row, not the CoT ones; it passes 18/19
instruction probes.

```
thinking, 1024 tokens   forced close  98.4%   no answer  7.8%
thinking, 2048 tokens   forced close  95.3%   no answer 10.9%
```

Takeaways so far:

- A light instruction-tuning pass puts the base model about 10 points above its
  5-shot baseline (different prompts, so this is a rough comparison).
- Even at 2048 tokens the thinking model almost always runs out of room and has
  to be cut off, so the budget is the first thing to vary.
- The 64-question rows are smoke tests, not results.

## notes

- Weights are **bf16**, no quantization.
- Sampling follows the Qwen3.5-2B model card (`temp 1.0, top_p 0.95, top_k 20,
  presence penalty 1.5`). Greedy decoding makes this model loop.
- The presence penalty is dropped while writing the answer, so it can't push
  the model away from options its reasoning mentioned.

## license

MIT, see [LICENSE](LICENSE), except the Kolmogorov portrait at the bottom, which is
an adaptation of a CC BY-SA 4.0 photograph (credited under it) and is shared
under the same license.

---

```
                        __           __,,,,,,,,,,,__
                     /('''''\--\.--('  . .         ''\\_
                    \\                                 ')\,_
                    /.                                     ''\,_
                   / ...                           ..   ....   '\_
                  \\..                               ......:;:...'\_
                  |.                        . .:..=+:=;x+...;;;:..:'\\_
                  (.                      :=.    ..+:..x::;a=+;x;;;xXOo)\
                 _\                   ....:               =XOx*aX*xxa*oOOa,
                 /.         .         ..       :..     .  +*XaOO##x*o**o*X0x_
                |\                                       .:=***xxO#*;x;xxx;x+_
               ,(                                        .::.;;==xxo*;::=....),_
              |\     .                             .     .:..:=+===+xxa:=.     '\_
              (     ..                                   .:::;;=:=::;x:=..       )
             _\    ....                        .    . ...::x:..:.=:;*x+===.      .\
             \-    ....                          ..  ...::.;;; :.:;x*;;x=+=      .|
             |    .=:..                             ...:...::;::x*axxxx;;.      . //
             (   .=::.                 ..         . .. . ..::.;xoXXaaoxx= . .     .)_
            |.  .++::.                      .  ..    . .::..:+xxaaXOXa*;+:..     . .\
            |  .;x+:.            .. .   .           .  ..:..:xxaaaXoxoXx:=  ..      =
            ( .:;;... .....  .......:: . .. .....::........::x;aoXXOXao;::. ..     |\
           -\..;;=...+;;=xxaXox*x;:.+:.:::.::.:...... .... .=:;xxaaoaox++..  :.    (
            =::x;. :xxxxaXO00@@00Xaoox;;;o;;;xooaaXOXax.::.:..=x*oxxoaox=:  ....  \\
            |;:+=..:::::+;xaX####0#OXa:xxXO#0#0MNNNNNMM@Xa**;==;oxxx;XaX*; .  ... |
            --=::....xa000NNNM0M@00#x:.:;O@0NNNN@#XXXOO#0#O00axxxx;;x*a00x....... |
            |;;=.    .  ..=;xxaXaa*x.  .xaO0MNNM@NMMM0Xx=;X0@0o*;+x+;;X0X;xx+;x=:.|
            |..:.     .=+==;;;xx=::.    :=;xX#XOOao;0MNNN0aXXXOx:..::oooaxX=oXoox_(
            ( .:          ..::..   .   .:===;xxx;=.. . ..:xaaxxxx++;;;x*aaoxOXa#*(
           -\...                   .   .:..:=:.=;;+;;xx*a;..   ..+xx;xxxx;;oX#0#x
           -/....                 .    .:=..:=.. . .. .       ...:+;;x#Xox;xo;.:|
           -/ ....           ...       .::.....               .:;x;xxoO#O*+aOx..|
            |  .... .      .oX.        .x;;;xaa:           ...:==xxxoO0**; #Ma; |
            )_ .:=:......:;aO;.       .:+:...+X@x..    ......=:+xxaa#@#xx;::O*. |
             \_.:+;;=::=xoaX:..xx;;x;;++;:=;;O000X+......::==xx;x*0@#00Xa+x;=;._(
              '\==xoaoaaaox=   .X0N@@MMNMNNN0XxXX0X;;;::::=;x*Xa#M00OOOO#...  _(
                \+;oooaooa:    . =XMNNNNM0Oa;;::;a#XXoa*x*xXXa*a#0X#Xa#o:.:. .=
                |=x==+;aO:.. ....:=;oXOa*x**x;==xxXO0#0M@0M0#a*XOXX#XaXx....:/
                -x+...=o=:::...:::=;xoo;xx;;.:x;x;o#0XXO00O#0OX#XaXXXa0#x;;;|
                 =+:...;xx;=:;;=+;;=;;;xXaox*xxxxxxXMa;;;xaaO#0#aXaXa@NNOxx=)_
                 )+;:::=;oa**XoaX00X*oO#OOOXXaaXX0@0@...;xaX@00XXaaX0NoaNX;::+
                 -/;x;;xxxx;;;*O###X0@0MM@0OXooXM0a*..:x*oa@@#XaXXXXNX ;NNx:.)_
                 _a;xax;=:..=+xo;..:+*x;::;*O#oX0a;;=;XaOaO#aoxoooaM0  =@N@:.:'\_
               _,/x=xXa*=.  .:;xa0@MM@@N@@@O*x:x+.=xxX0MOOXooooXXaO0:  Xx0No.;@a.)\_
          _,//''   .+*xxx=.:.::..:xa#XX#O*a=::.  ..xXO#OaoXaO00OOX#:  =x+@NM=.@N0+ '),_
   __,//''   .  ... .*xax;. .         .  . .   ..:.+;xx;;;*O@M0O##.  .;+*MNNO.xNNo..  )\_
  ''       ...:=:.   :X#X;=.  ...            ..:=;xXax;x*o0NM@X#O   .x==a@NNN=:0Mx.     '\,_
         ...::+:      .aaxx:.:. .....:... . ..:+xXO@##Xa#0M0#X0x   :o=:=o#0MN#.XO:..  .    '\,
     .... .::=:       =Oa;+x;;;;=;;+;;xx==.=:x;XaO0@@@@00#0000.   ;o;;x*aaaO#0;oX:. .:. .     '\__
  .......::...       .:#@xxx*XaoaaaXXXoxx*xxoa*OO#0@@0#OO#@@*   .**::;x:;***oXoxX. . ...... .   .'
  .... .....         .:#0*x;+;x*aaXaXaa*aaaXXXX#000OOXXXO#X.   .;:..=;+==;;;xxa:x:   .:=...
  ... ....           .:OX*.=+===;x*XOXOOaXOOOXXXXaaooxoXa:    :+:.::=:...:=:+;x=:.........
       . .          . .xxo.:+;::+:;aaaaoo**ooo**xxxxx*x:    ..:....:.........:=:........... .
       .   ..       . ..;x:.:...:.;xx;;=;;;;;x;x;;x;;.     :.... ...   .. ...... ..... ..
           ...::.   .  ..::........:::.::::=======.       ..  .  .            ..  ..  . . .
              . .        ...      ... .........

  Andrey Nikolaevich Kolmogorov, 1903-1987
  "memory is just compression you can run"
```

<sub>Portrait: ASCII rendering of a detail from [a photograph of Kolmogorov and Igor Zurbenko](https://commons.wikimedia.org/wiki/File:KolmogorovZurbenko.jpg) by Igor Zurbenko, [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Best viewed in a light theme.</sub>

<sub>· ˚ ✦ · thanks for stopping by · ✦ ˚ ·</sub>
