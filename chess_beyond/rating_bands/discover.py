"""Break out the moves lower-rated players can't find, as a stratified set.

    python rating_bands/discover.py --labels data/lichess/bands/2025-06-blitz/labels --maia-type blitz --target idea3

Band-level curves (find_curves.py) average thousands of positions, so a kind of
move can look "found 30% of the time" while hiding positions nobody below 2000
ever solves. Each position is only played once, so this works per position:

  1. Maia-2 features: the probability Maia-2 gives the best move at each rating
     it resolves (<1100 ... 2000+), plus the engine and move-type features.
  2. A model of P(player of rating R finds it | position), with rating as an input,
     CROSS-FITTED: games are split into --folds folds and each fold is predicted by
     a model trained on the others, so every position is labelled out of sample.
  3. Each position gets a predicted rate at 800 ... 2500 and a predicted DISCOVERY
     RATING: the lowest rating where it reaches --found-at.
  4. Validation: within each predicted stratum, the ACTUAL rate of the players who
     faced those positions, band by band, next to the random-move floor. A real
     "can't find" stratum shows low bands at the floor and high bands well above.
  5. With --target idea2/idea3 (the player found the move AND kept the advantage
     over the next moves), a conversion table separates "didn't see the idea" from
     "general sloppiness on later moves".

Only-move positions (runner-up at least --only-gap centipawns worse), so "found"
means exactly the best move and the floor is 1/n_legal (an upper bound for ideaK).

Writes strata_<target>.jsonl: THE STRATIFIED SET, one row per position with its
discovery rating, stratum, predicted rates, best move, follow-up and Lichess link;
and strata_<target>.json: calibration, the validation tables and stratum sizes.
"""
import argparse
import glob
import hashlib
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # chess_beyond/: paths.py
import paths

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--labels", required=True)
ap.add_argument("--target", default="found", help="found, or idea2 / idea3 (label_bands --follow): played the idea, not just the move")
ap.add_argument("--maia-type", choices=["rapid", "blitz"], default="rapid", help="Maia-2 model matching the games' time control")
ap.add_argument("--only-gap", type=int, default=150)
ap.add_argument("--folds", type=int, default=5, help="cross-fitting folds, split by game")
ap.add_argument("--found-at", type=float, default=0.5, help="predicted rate that counts as 'finds it'")
ap.add_argument("--seed", type=int, default=0)
args = ap.parse_args()

MAIA_ELOS = [1000, 1150, 1350, 1550, 1750, 1950, 2100]      # one per Maia-2 bucket we use (<1100 ... >=2000)
GRID = [800, 1150, 1500, 1850, 2150, 2500]                  # ratings we predict at
dev = "cuda" if torch.cuda.is_available() else "cpu"

# ---------------------------------------------------------------- data
rows = []
for p in sorted(glob.glob(os.path.join(args.labels, "*.jsonl"))):
    if os.path.basename(p).startswith("strata_"):
        continue
    rows += [json.loads(l) for l in open(p)]
rows = [r for r in rows if r["gap_cp"] is not None and r["gap_cp"] >= args.only_gap and abs(r["best_cp"]) < 1000
        and r.get(args.target) is not None]
print(f"{len(rows)} only-move positions with a known '{args.target}'")


def fold_of(game_id):
    h = hashlib.md5(f"{args.seed}:{game_id}".encode()).digest()
    return int.from_bytes(h[:4], "big") % args.folds


fold = np.array([fold_of(r["game_id"]) for r in rows])

# ---------------------------------------------------------------- Maia-2 features (cached)
cache = os.path.join(args.labels, f"maia_{args.maia_type}_best_prob_gap{args.only_gap}_{args.target}.npy")
if os.path.exists(cache):
    maia = np.load(cache)
else:
    from maia2 import inference as I2
    from maia2 import model as M2
    from maia2.utils import mirror_move
    mdl = M2.from_pretrained(type=args.maia_type, device="gpu" if dev == "cuda" else "cpu", save_root=str(paths.MAIA2))
    all_moves_dict, elo_dict, _ = I2.prepare()
    maia = np.zeros((len(rows), len(MAIA_ELOS)), dtype=np.float32)
    B = 512
    with torch.no_grad():
        for s in range(0, len(rows), B):
            chunk = rows[s:s + B]
            boards, legal, best = [], [], []
            for r in chunk:
                b, _, _, lg = I2.preprocessing(r["fen"], 1500, 1500, elo_dict, all_moves_dict)
                boards.append(b); legal.append(lg)
                mv = r["best"] if r["fen"].split(" ")[1] == "w" else mirror_move(r["best"])
                best.append(all_moves_dict[mv])
            boards, legal = torch.stack(boards).to(dev), torch.stack(legal).to(dev)
            best = torch.tensor(best, device=dev)
            for k, e in enumerate(MAIA_ELOS):
                cat = torch.full((len(chunk),), I2.map_to_category(e, elo_dict), device=dev)
                logits, _, _ = mdl(boards, cat, cat)
                probs = torch.softmax(logits.masked_fill(legal == 0, -1e9), -1)
                maia[s:s + len(chunk), k] = probs.gather(1, best[:, None]).squeeze(1).cpu().numpy()
            print(f"\rMaia-2 features {min(s + B, len(rows))}/{len(rows)}", end="", flush=True)
    print()
    np.save(cache, maia)

# ---------------------------------------------------------------- features
PIECES = "pnbrqk"


def feats(r):
    return [r["capture"], r["check"] and not r["capture"], r["quiet"], r["retreat"] and r["quiet"], r["promotion"],
            r["gives_material"] > 0, min(r["gives_material"], 9) / 9, min(r["gap_cp"], 1000) / 1000,
            min(r["depth_to_find"], 16) / 16, math.log(r["n_legal"]) / 4, r["material"] / 78,
            min(abs(r["best_cp"]), 1000) / 1000] + [r["piece"] == c for c in PIECES]


X = np.hstack([np.array([feats(r) for r in rows], dtype=np.float32),
               np.log(np.clip(maia, 1e-4, 1)) / 9.2])                       # log-probs, roughly in [-1, 0]
elo = np.array([r["elo"] for r in rows], dtype=np.float32)
y = np.array([r[args.target] for r in rows], dtype=np.float32)
floor = np.array([1 / r["n_legal"] for r in rows], dtype=np.float32)
band = np.array([r["band"] for r in rows])
bands = sorted(set(band), key=lambda b: int(b.split("-")[0].rstrip("+")))


class FindModel(nn.Module):
    """P(found | position, rating): an MLP over position features and rating."""

    def __init__(s, n):
        super().__init__()
        s.net = nn.Sequential(nn.Linear(n + 1, 128), nn.GELU(), nn.Linear(128, 128), nn.GELU(), nn.Linear(128, 1))

    def forward(s, x, rating):
        return s.net(torch.cat([x, ((rating - 1500) / 500)[:, None]], 1)).squeeze(1)


# ---------------------------------------------------------------- cross-fitted find model
T = lambda a: torch.tensor(a, device=dev)
Xt, Et, Yt = T(X), T(elo), T(y)
lossf = nn.BCEWithLogitsLoss()


def train_model(idx, seed):
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    val = rng.choice(idx, size=len(idx) // 10, replace=False)
    fit = np.setdiff1d(idx, val)
    model = FindModel(X.shape[1]).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-3)
    best_val, best_state, bad = 1e9, None, 0
    for epoch in range(300):
        model.train()
        for b in np.array_split(rng.permutation(fit), max(1, len(fit) // 512)):
            i = T(b)
            loss = lossf(model(Xt[i], Et[i]), Yt[i])
            opt.zero_grad(); loss.backward(); opt.step()
        model.eval()
        with torch.no_grad():
            v = lossf(model(Xt[T(val)], Et[T(val)]), Yt[T(val)]).item()
        if v < best_val - 1e-4:
            best_val, best_state, bad = v, {k: x.clone() for k, x in model.state_dict().items()}, 0
        else:
            bad += 1
            if bad >= 15:
                break
    model.load_state_dict(best_state)
    return model.eval(), best_val


p_own = np.zeros(len(rows), dtype=np.float32)
grid = np.zeros((len(rows), len(GRID)), dtype=np.float32)
losses = []
for k in range(args.folds):
    te = np.where(fold == k)[0]
    model, v = train_model(np.where(fold != k)[0], args.seed + k)
    losses.append(v)
    with torch.no_grad():
        p_own[te] = torch.sigmoid(model(Xt[T(te)], Et[T(te)])).cpu().numpy()
        for g, gv in enumerate(GRID):
            grid[te, g] = torch.sigmoid(model(Xt[T(te)], torch.full((len(te),), float(gv), device=dev))).cpu().numpy()
    print(f"\rfold {k + 1}/{args.folds}: val log-loss {v:.4f}", end="", flush=True)
ym = float(y.mean())
base = -(ym * math.log(ym) + (1 - ym) * math.log(1 - ym))
print(f"\nfind model ({args.target}): mean val log-loss {np.mean(losses):.4f} (predicting the mean: {base:.4f})")

# ---------------------------------------------------------------- calibration (every position, out of fold)
print("\nCalibration, out of fold (predicted vs actual rate, by band)")
calib = {}
for b in bands:
    m = band == b
    calib[b] = dict(n=int(m.sum()), predicted=float(p_own[m].mean()), actual=float(y[m].mean()))
    print(f"  {b:>10}  n={m.sum():5d}  predicted {p_own[m].mean():.3f}  actual {y[m].mean():.3f}")

# ---------------------------------------------------------------- strata by predicted discovery rating
disc = np.array([next((g for g, p in zip(GRID, row) if p >= args.found_at), None) or 9999 for row in grid])
names = {g: f"found by {g}" for g in GRID} | {9999: "not by 2500"}


def table(title, value, keep=None):
    """Rows: predicted stratum. Columns: band. Cells: value(mask) over the positions in that cell (n)."""
    print(f"\n{title}")
    print(f"{'stratum':>16}  {'n':>5}" + "".join(f"{b:>15}" for b in bands) + "    floor")
    out = {}
    for g in GRID + [9999]:
        m = (disc == g) if keep is None else (disc == g) & keep
        if m.sum() == 0:
            continue
        line, out[names[g]] = f"{names[g]:>16}  {m.sum():5d}", {}
        for b in bands:
            mb = m & (band == b)
            k = int(mb.sum())
            val = value(mb) if k else None
            out[names[g]][b] = dict(n=k, rate=val)
            line += f"{val:9.2f} ({k:4d})" if k >= 10 else f"{'-':>15}"
        print(line + f"    {floor[m].mean():.2f}")
    return out


what = "the idea" if args.target != "found" else "the move"
strata = table(f"All positions by PREDICTED discovery rating (lowest rating with p >= {args.found_at}): ACTUAL rate "
               f"of playing {what}, among the players who faced them (n); floor = random legal move",
               lambda m: float(y[m].mean()))
conversion = None
if args.target != "found":
    # Of the players who found the MOVE, how many went on to play the idea? Relative to the same band on the
    # easiest stratum, so general sloppiness on later moves is not mistaken for not seeing the idea.
    found = np.array([bool(r["found"]) for r in rows])
    easy = {b: y[(disc == GRID[0]) & (band == b) & found].mean() for b in bands}
    conversion = table("Conversion: share of FOUND moves followed through with the idea, relative to the same band "
                       "on the easiest stratum (1.0 = converts as well as on easy moves; low = accidental finds)",
                       lambda m: float(y[m].mean() / easy[band[m][0]]), keep=found)

# ---------------------------------------------------------------- the stratified set, every position out of fold
out_rows = os.path.join(args.labels, f"strata_{args.target}.jsonl")
with open(out_rows, "w") as f:
    for i, r in enumerate(rows):
        f.write(json.dumps(dict(
            fen=r["fen"], best=r["best"], played=r["played"], follow=r.get("follow"), band=r["band"], elo=r["elo"],
            found=r["found"], idea2=r.get("idea2"), idea3=r.get("idea3"),
            discovery_rating=int(disc[i]) if disc[i] < 9999 else None, stratum=names[disc[i]],
            predicted={g: round(float(p), 3) for g, p in zip(GRID, grid[i])}, floor=round(float(floor[i]), 3),
            gap_cp=r["gap_cp"], depth_to_find=r["depth_to_find"],
            move_type=[k for k in ("capture", "check", "quiet", "retreat", "promotion") if r[k]],
            gives_material=r["gives_material"], maia={e: round(float(p), 3) for e, p in zip(MAIA_ELOS, maia[i])},
            link=f"{r['game_id']}#{r['ply'] + 1}", fold=int(fold[i]))) + "\n")
sizes = {names[g]: int((disc == g).sum()) for g in GRID + [9999]}
json.dump(dict(target=args.target, maia_type=args.maia_type, found_at=args.found_at, grid=GRID, folds=args.folds,
               only_gap=args.only_gap, val_logloss=float(np.mean(losses)), baseline_logloss=base, calibration=calib,
               strata=strata, conversion=conversion, sizes=sizes),
          open(os.path.join(args.labels, f"strata_{args.target}.json"), "w"), indent=1)

# ---------------------------------------------------------------- the sharpest examples
sharp = (grid[:, -1] - grid[:, 0]) * (grid[:, 0] < 2 * floor + 0.05)
print("\nSharpest examples (predicted near the floor at 800, high at 2500):")
for i in np.argsort(-sharp)[:8]:
    r = rows[i]
    print(f"  {r['best']:>6}  p800 {grid[i, 0]:.2f}  p2500 {grid[i, -1]:.2f}  floor {floor[i]:.2f}  "
          f"({r['band']} player {'played it' if y[i] else 'missed'})  {r['game_id']}#{r['ply'] + 1}")
print(f"\nstratum sizes: " + ", ".join(f"{k} {v}" for k, v in sizes.items()))
print(f"wrote {out_rows} ({len(rows)} positions, every one out of fold) and strata_{args.target}.json")
