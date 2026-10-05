<h1 align="center">Memorize</h1>

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
🔄 GRPO (Mac) · 🔄 label-split (GPU) · ⬜ memorization

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
| Run the label-split experiment         | `python run_split.py --name my-run`                          | CUDA    |
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
```
</details>

## Label-split experiment (PyTorch, CUDA)

MMLU-Pro is cut into thirds: **A** is trained with random labels, **B** with the
real ones, **C** is held out. A and B train together as direct `ANSWER: X`
replies; C is scored every 25 steps, alongside samples of A and B.

`run_split.py` does everything: venv, requirements, CUDA check, downloads, then
the run. It starts from the instruct model (downloaded from Hugging Face, or
trained locally if that fails) and needs only Python 3.10+. Output lands in
`results/<name>/` (`train.log`, `metrics.jsonl`, `curves.png`, `adapter/`).

```bash
python run_split.py --name sft-split
python run_split.py --name mac-sft --mlx-adapter adapters/sft-run2   # start from the Mac's MLX SFT
python run_split.py --name nogold --detach -- --exclude-gold --epochs 6
python run_split.py --name test --dry-run
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
│   ├── sft_data.py       build the instruction-tuning set
│   ├── sft.py            LoRA SFT on MLX          (sft_torch.py: same on CUDA)
│   ├── probes.py         instruction-following probes
│   ├── grpo.py           GRPO / Dr. GRPO with a KL penalty
│   ├── label_split.py    A random / B correct / C held-out SFT run
│   ├── plot_split.py     curves for a label_split run
│   ├── mlx_to_peft.py    convert an MLX LoRA to PEFT
│   └── hub.py            push / pull adapters on Hugging Face
├── adapters/             LoRA configs + models.json (weights live on HF)
├── results/              per-run summaries and metrics
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

MIT, see [LICENSE](LICENSE). The Kolmogorov portrait below is an adaptation of a
CC BY-SA 4.0 photograph (credited under it) and is shared under the same license.

<details>
<summary>🎩 one more thing</summary>

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

</details>
