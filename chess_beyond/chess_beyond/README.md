# Can models trained on humans find the moves humans miss?

Pipeline for the chess experiment. See the design doc for the reasoning.

## Requirements
- Python 3.10+, `pip install torch chess zstandard matplotlib`
- Stockfish binary (https://stockfishchess.org/download/)
- A Lichess monthly database file, e.g. `lichess_db_standard_rated_2024-01.pgn.zst`
  from https://database.lichess.org/ (the script streams it; no need to decompress)

## Run order

```bash
# 1. Annotate positions (the expensive step; scales with --workers)
python build_dataset.py --pgn lichess_db_standard_rated_2024-01.pgn.zst \
    --stockfish $(which stockfish) --out positions.jsonl \
    --min-elo 1100 --max-elo 1600 --games 50000 --workers 32

# 2. Bands, filter, controls, splits (prints band sizes and human best-move rates)
python make_splits.py --positions positions.jsonl --out data/ --easy-max 4 --hard-min 8

# 3. Imitation: same seed/size/steps for all three
python train_sft.py --train data/train_full.jsonl     --out ckpt/full.pt
python train_sft.py --train data/train_filtered.jsonl --out ckpt/filtered.pt
python train_sft.py --train data/train_random.jsonl   --out ckpt/random.pt

# 4. RL from the filtered model, three reward signals
for R in deep shallow random; do
  python rl_finetune.py --init ckpt/filtered.pt --positions data/rl_positions.jsonl \
      --reward $R --out ckpt/rl_$R.pt --monitor data/test_hard.jsonl
done

# 5. Evaluate (search arms are slow; they use --search-limit positions)
python evaluate.py --data data/ --full-ref ckpt/full.pt \
    --models full=ckpt/full.pt filtered=ckpt/filtered.pt random_ctrl=ckpt/random.pt \
             rl_deep=ckpt/rl_deep.pt rl_shallow=ckpt/rl_shallow.pt rl_random=ckpt/rl_random.pt \
    --search filtered=400 rl_deep=400
```

## What to check first
- `data/stats.json`: the hard band must be big enough (aim for 5,000+ test
  positions) and humans should rarely play the best move there. If the hard band
  is tiny, lower `--hard-min` or annotate more games.
- `filtered_hard_best_labels_left` in stats must be 0.
- Easy-position accuracy of `filtered` should match `full` (the filter must not
  break basic chess).

## Knobs worth sweeping
`--margin` (best-set width), `--easy-max/--hard-min` (band edges), `--deep-depth`,
RL `--group` (how often a rare best move gets sampled), model size.

## Cost (rough)
Annotation dominates: three searches per position, including a deep search over
every legal move. At depth 16, expect on the order of seconds per position per
core, so 200k positions is roughly 50-150 core-hours. Lower `--deep-depth` or
`--games` for a first pass on a laptop.

## Status
Encoding, move vocabulary (checked against 568k legal moves), the filter, splits,
save/load and the search's sign conventions were unit-tested on synthetic data.
The Stockfish annotation, training, RL and evaluation scripts have not been run
end to end; start with a small `--games` to shake out issues.
