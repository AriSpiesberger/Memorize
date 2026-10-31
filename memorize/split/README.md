# memorize/split

**Train on random labels for one third of a benchmark and real labels for another: does either help the held-out
third?** PyTorch on CUDA, from the instruct model ([Arisp/memorize-instruct](https://huggingface.co/Arisp/memorize-instruct)).

The benchmark is cut into thirds: **A** is trained with random labels, **B** with the real ones, **C** is held out.
A and B train together as direct `ANSWER: X` replies; C is scored every 25 steps, alongside samples of A and B.
Everyday chats with no math or science (`memorize.general_data`) are mixed in (`--replay-frac`, default 25% of A+B;
0 turns it off) and their held-out loss is logged, to show whether general ability drifts.

```bash
python memorize/split/run_split.py              # -> memorize/results/label-split/<date>_mmlu_pro/
python memorize/split/run_split.py --name mac-sft --mlx-adapter memorize/adapters/sft-run2   # start from the Mac's MLX SFT
python memorize/split/run_split.py --name nogold --detach -- --exclude-gold --epochs 6
python memorize/split/run_split.py --dry-run
```

`run_split.py` does everything (venv, requirements, CUDA check, downloads, then `label_split.py`); `plot_split.py`
draws a run's curves, also mid-run. Output: `memorize/results/label-split/<date>_<benchmark>[_<name>]/` (`train.log`,
`metrics.jsonl`, `curves.png`, `adapter/`).

## What it shows so far

One run and one seed per benchmark. *Fit* is how often the model's answer matches the random label it was trained on.
Each cell is start of training -> end.

| benchmark  | epochs | C: held-out accuracy | A: fit to random labels | B: accuracy on real labels |
| ---------- | -----: | -------------------- | ----------------------- | -------------------------- |
| mmlu_pro   |    3.1 | 33.8% -> 30.6%       | 11.2% -> 83.2%          | 34.2% -> 97.4%             |
| mmlu_redux |      3 | 66.6% -> 53.8%       | 25.4% -> 93.6%          | 61.2% -> 99.2%             |
| ceval      |      4 | 60.2% -> 57.8%       | 28.3% -> 100%           | 60.3% -> 99.8%             |
| supergpqa  |      2 | 20.8% -> 35.1%       | 9.4% -> 46.6%           | 23.0% -> 81.0%             |

- The model memorises both the random labels and the real ones, and neither helps on C. Held-out accuracy fell on
  three of the four benchmarks, most on MMLU-Redux (about 13 points).
- SuperGPQA is the exception: it started near chance, went up, and had memorised the least (47% fit after 2 epochs).
- With general-chat replay on (MMLU-Redux), held-out loss on everyday chats moved from 1.22 to 1.30 over 3 epochs.
- Curves and per-run configs: [../results/label-split/](../results/label-split/).
