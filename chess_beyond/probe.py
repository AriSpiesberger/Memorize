"""Where does the network put a fixed set of positions, just before it decides?

The probe set is a fixed list of positions, labelled once:
  legal      number of legal moves                                   (complexity: how many options)
  sharpness  win% of the best move minus win% of the second best     (precision: 0 = several moves are
             (Stockfish, side to move)                                as good, ~100 = exactly one holds)
  good       moves within --good-margin win% of the best (counted up to --multipv; fewer = sharper)
  rating     Lichess puzzle rating, measured from human attempts     (puzzles only)
  source     puzzle stratum ('1100', '2400', ...) or 'game'

At an eval, snapshot() runs the network on every probe position and keeps the vector its heads
read: the CLS token after the final LayerNorm, the last thing computed before the move and value
are chosen. It saves those vectors (<dir>/step<N>.npz), a figure of the positions on SVD
components 1 and 2 of the centred activations, coloured by complexity, sharpness and source
(<dir>/step<N>.png), and one line of numbers (<dir>/log.jsonl): variance on each component, how
each metric correlates with SVD 1-3, and how well a cross-validated linear probe reads each metric
from the full vector (R^2). The picture shows two directions; the probe says whether the metric is
in there at all.

  python probe.py build --out data/probe.jsonl --pgn <games.pgn>             # once; needs Stockfish for sharpness
  python probe.py snapshot --ckpt runs/transcend/imitation.pt                # one checkpoint, after the fact
  python probe.py series --dir runs/transcend/imitation_probe --color sharpness   # a grid over training
train.py and rl_puzzles.py call snapshot() at every eval when data/probe.jsonl exists (--probe).
"""
import argparse
import glob
import json
import math
import os
import random
import re
import sys
import zlib
from pathlib import Path

import chess
import chess.pgn
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths
from common import encode_board

DEFAULT = paths.DATA / "probe.jsonl"
NUMERIC = ("legal", "sharpness", "good", "rating")


# ----------------------------------------------------------------- labels
def win_pct(score):
    """Lichess's win% for a python-chess PovScore already from the side to move (mate = 0 or 100)."""
    cp = score.score(mate_score=100000)
    return 50 + 50 * (2 / (1 + math.exp(-0.00368208 * cp)) - 1)


def label(board, engine, nodes, multipv, margin):
    """Complexity always; sharpness and good-move count when an engine is given."""
    row = dict(fen=board.fen(), legal=board.legal_moves.count())
    if engine is None or row["legal"] == 0:
        return row
    infos = engine.analyse(board, chess.engine.Limit(nodes=nodes), multipv=min(multipv, row["legal"]))
    w = sorted((win_pct(i["score"].pov(board.turn)) for i in infos if "score" in i), reverse=True)
    row["best"] = infos[0]["pv"][0].uci()
    row["win"] = round(w[0], 1)
    # one legal move: "only move" but trivially found, so no sharpness (plotted grey)
    row["sharpness"] = round(w[0] - w[1], 1) if len(w) > 1 else None
    row["good"] = sum(x >= w[0] - margin for x in w)
    return row


def puzzle_positions(strata_dir, per_stratum):
    out = []
    for p in sorted(Path(strata_dir).glob("*.jsonl")):
        if not p.stem.isdigit():
            continue
        for line in list(open(p))[:per_stratum]:
            pz = json.loads(line)
            b = chess.Board(pz["fen"]); b.push_uci(pz["moves"][0])        # board after the setup move
            out.append((b, dict(source=p.stem, rating=pz["rating"], id=pz["id"], solution=pz["moves"][1])))
    return out


def game_positions(pgn, n, rng, min_ply=8):
    """One random position (not the start, not game over) from each of the first n usable games."""
    out = []
    with open(pgn, encoding="utf-8", errors="replace") as f:
        while len(out) < n:
            g = chess.pgn.read_game(f)
            if g is None:
                break
            moves = list(g.mainline_moves())
            if len(moves) <= min_ply + 1:
                continue
            b = g.board()
            for mv in moves[: rng.randrange(min_ply, len(moves))]:
                b.push(mv)
            if not b.is_game_over():
                out.append((b, dict(source="game", game=g.headers.get("Site", ""))))
    return out


def random_positions(n, rng):
    """Positions from random play: only for testing without data."""
    out = []
    while len(out) < n:
        b = chess.Board()
        for _ in range(rng.randrange(6, 60)):
            if b.is_game_over():
                break
            b.push(rng.choice(list(b.legal_moves)))
        if not b.is_game_over():
            out.append((b, dict(source="random")))
    return out


def build(a):
    rng = random.Random(a.seed)
    pos = puzzle_positions(a.strata, a.per_stratum) if Path(a.strata).exists() else []
    if a.pgn:
        pos += game_positions(a.pgn, a.games_n, rng)
    if a.random_n:
        pos += random_positions(a.random_n, rng)
    if not pos:
        raise SystemExit("no positions: point --strata at the puzzle strata and/or give --pgn")
    engine = None
    if not a.no_engine:
        try:
            engine = chess.engine.SimpleEngine.popen_uci(paths.stockfish())
            engine.configure({"Threads": a.threads, "Hash": 256})
        except SystemExit as e:
            print(f"{e}\n-> building without sharpness (complexity only)")
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w") as f:
        for i, (b, meta) in enumerate(pos):
            f.write(json.dumps({**label(b, engine, a.nodes, a.multipv, a.good_margin), **meta}) + "\n")
            if (i + 1) % 200 == 0:
                print(f"  labelled {i + 1}/{len(pos)}", flush=True)
    if engine:
        engine.quit()
    src = {}
    for _, m in pos:
        src[m["source"]] = src.get(m["source"], 0) + 1
    print(f"{len(pos)} positions -> {a.out}  ({', '.join(f'{k}: {v}' for k, v in src.items())})")


# ----------------------------------------------------------------- activations
def load_probe(path=DEFAULT):
    rows = [json.loads(l) for l in open(path)]
    x = torch.tensor([encode_board(chess.Board(r["fen"])) for r in rows])
    return rows, x


@torch.no_grad()
def activations(model, x, batch=1024):
    """The vector the policy and value heads read: CLS after the final LayerNorm, (n, d)."""
    was = model.training; model.eval(); dev = next(model.parameters()).device; out = []
    for i in range(0, len(x), batch):
        xb = x[i:i + batch].to(dev).long()
        out.append(model.norm(model.body(model.tok(xb) + model.pos))[:, 0].float().cpu())
    model.train(was)
    return torch.cat(out).numpy()


def svd(H, k=3, ref=None):
    """Centre, SVD; coordinates on the top k components. Each component's sign is fixed so that its
    largest loading is positive, or, given ref coordinates for the same positions, so it correlates
    positively with them (keeps axes from flipping between checkpoints)."""
    Hc = H - H.mean(0)
    _, S, Vt = np.linalg.svd(Hc, full_matrices=False)
    coords = Hc @ Vt[:k].T
    for j in range(k):
        s = (np.sign(coords[:, j] @ ref[:, j]) if ref is not None
             else np.sign(Vt[j, np.argmax(np.abs(Vt[j]))])) or 1.0
        coords[:, j] *= s
    return coords, (S ** 2 / (S ** 2).sum())[:k]


def metric(rows, name):
    return np.array([np.nan if r.get(name) is None else float(r[name]) for r in rows])


def probe_r2(H, y, folds=5, lam=1.0, seed=0, groups=None):
    """Cross-validated R^2 of a ridge regression from the full activation vector to y.
    Folds are random (seeded), or, given `groups` (e.g. a game id per position), split by group,
    so rows from one group never sit on both sides of a fold (stable across runs)."""
    ok = ~np.isnan(y)
    if ok.sum() < 50 or np.nanstd(y) == 0:
        return None
    X, y = H[ok], y[ok]
    if groups is None:
        fold = np.empty(len(y), dtype=int)
        fold[np.random.default_rng(seed).permutation(len(y))] = np.arange(len(y)) % folds
    else:
        fold = np.array([zlib.crc32(g.encode()) % folds for g in groups[ok]])
    pred = np.empty_like(y)
    for f in range(folds):
        te, tr = fold == f, fold != f
        if te.sum() == 0 or tr.sum() == 0:
            return None
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-6
        Xt = (X[tr] - mu) / sd
        ym = y[tr].mean()
        w = np.linalg.solve(Xt.T @ Xt + lam * tr.sum() * np.eye(X.shape[1]), Xt.T @ (y[tr] - ym))
        pred[te] = (X[te] - mu) / sd @ w + ym
    return float(1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum())


def corr(a, b):
    ok = ~np.isnan(b)
    return None if ok.sum() < 10 or np.std(b[ok]) == 0 else float(np.corrcoef(a[ok], b[ok])[0, 1])


def numbers(H, coords, var, rows):
    out = dict(var=[round(float(v), 4) for v in var])
    for m in NUMERIC:
        y = metric(rows, m)
        if np.isnan(y).all():
            continue
        out[m] = dict(r2=probe_r2(H, y), corr=[corr(coords[:, j], y) for j in range(coords.shape[1])])
    return out


# ----------------------------------------------------------------- figures
def panel(ax, coords, rows, color, title=None):
    import matplotlib.pyplot as plt
    x, y = coords[:, 0], coords[:, 1]
    if color == "source":
        srcs = sorted({r["source"] for r in rows}, key=lambda s: (not s.isdigit(), s.zfill(5)))
        cmap = plt.get_cmap("viridis", max(len(srcs), 2))
        for i, s in enumerate(srcs):
            m = np.array([r["source"] == s for r in rows])
            ax.scatter(x[m], y[m], s=8, alpha=0.6, color="0.35" if not s.isdigit() else cmap(i), label=s, lw=0)
        ax.legend(fontsize=7, markerscale=2, loc="best", frameon=False)
    else:
        c = coords[:, 2] if color == "svd3" else metric(rows, color)
        nan = np.isnan(c)
        ax.scatter(x[nan], y[nan], s=6, color="0.8", lw=0)
        if (~nan).any():
            lo, hi = np.percentile(c[~nan], [2, 98])
            sc = ax.scatter(x[~nan], y[~nan], c=c[~nan], s=8, alpha=0.85, cmap="plasma" if color == "sharpness" else "viridis",
                            vmin=lo, vmax=hi if hi > lo else lo + 1, lw=0)
            plt.colorbar(sc, ax=ax, fraction=0.046, pad=0.02)
    ax.set_title(title or color, fontsize=9); ax.set_xticks([]); ax.set_yticks([])


LABEL = dict(legal="complexity: legal moves", sharpness="sharpness: win% best - 2nd best", good="near-best moves",
             rating="puzzle rating", source="source", svd3="SVD component 3")


def figure(coords, var, rows, step, path, colors, stats=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    colors = [c for c in colors if c in ("source", "svd3") or not np.isnan(metric(rows, c)).all()]
    fig, axes = plt.subplots(1, len(colors), figsize=(4.2 * len(colors), 4.0), squeeze=False)
    for ax, c in zip(axes[0], colors):
        t = LABEL.get(c, c)
        if stats and c in stats and stats[c]["r2"] is not None:
            t += f"\nlinear probe R^2 {stats[c]['r2']:.2f}"
        panel(ax, coords, rows, c, t)
    fig.suptitle(f"step {step}: SVD 1 ({var[0]:.0%} of variance) vs SVD 2 ({var[1]:.0%})", fontsize=10)
    fig.supxlabel("SVD 1", fontsize=8); fig.supylabel("SVD 2", fontsize=8)
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)


# ----------------------------------------------------------------- the hook used during training
_cache = {}


def snapshot(model, step, out_dir, probe=DEFAULT, colors=("legal", "sharpness", "source")):
    """Activations of every probe position at this step: npz + figure + a line in log.jsonl.
    Returns the numbers, or None when there is no probe set."""
    probe = str(probe)
    if not os.path.exists(probe):
        if probe not in _cache:
            print(f"[probe] no probe set at {probe}; skipping activation snapshots (python probe.py build)")
            _cache[probe] = None
        return None
    if probe not in _cache or _cache[probe] is None:
        _cache[probe] = load_probe(probe)
    rows, x = _cache[probe]
    H = activations(model, x)
    os.makedirs(out_dir, exist_ok=True)
    np.savez_compressed(os.path.join(out_dir, f"step{step}.npz"), H=H.astype(np.float16), step=step)
    coords, var = svd(H)
    stats = numbers(H, coords, var, rows)
    figure(coords, var, rows, step, os.path.join(out_dir, f"step{step}.png"), colors, stats)
    with open(os.path.join(out_dir, "log.jsonl"), "w" if step == 0 else "a") as f:   # a new run starts it afresh
        f.write(json.dumps(dict(step=step, probe=probe, **stats)) + "\n")
    msg = "  ".join(f"{m} R^2 {s['r2']:.2f}" for m, s in stats.items() if isinstance(s, dict) and s["r2"] is not None)
    print(f"[probe step {step}] SVD 1/2/3 variance {' / '.join(f'{v:.0%}' for v in var)}  {msg}", flush=True)
    return stats


# ----------------------------------------------------------------- after the fact
def series(a):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows, _ = load_probe(a.probe)
    files = sorted(glob.glob(os.path.join(a.dir, "step*.npz")), key=lambda p: int(re.findall(r"step(\d+)", p)[-1]))
    if not files:
        raise SystemExit(f"no step*.npz in {a.dir}")
    Hs = [(int(np.load(p)["step"]), np.load(p)["H"].astype(np.float32)) for p in files]
    if len(Hs) > a.panels:                                   # evenly spaced, always first and last
        pick = sorted({round(i * (len(Hs) - 1) / (a.panels - 1)) for i in range(a.panels)})
        Hs = [Hs[i] for i in pick]
    if a.basis == "own":                                     # each step's own SVD, signs aligned to the previous
        out, ref = [], None
        for s, H in Hs:
            c, v = svd(H, ref=ref); out.append((s, c, v)); ref = c
    else:                                                    # one basis for all steps: positions move, axes don't
        Href = Hs[0][1] if a.basis == "first" else Hs[-1][1]
        mu = Href.mean(0); _, S, Vt = np.linalg.svd(Href - mu, full_matrices=False)
        v = S[:3] ** 2 / (S ** 2).sum()
        out = [(s, (H - mu) @ Vt[:3].T, v) for s, H in Hs]
    allc = np.concatenate([c[:, :2] for _, c, _ in out])            # shared limits from the data itself:
    (x0, y0), (x1, y1) = np.percentile(allc, 0.5, axis=0), np.percentile(allc, 99.5, axis=0)   # drift stays visible
    pad = 0.05 * max(x1 - x0, y1 - y0)
    cols = min(len(out), 4); nrow = math.ceil(len(out) / cols)
    fig, axes = plt.subplots(nrow, cols, figsize=(3.6 * cols, 3.4 * nrow), squeeze=False)
    for ax, (s, c, v) in zip(axes.flat, out):
        panel(ax, c, rows, a.color, f"step {s}  (SVD 1 {v[0]:.0%}, SVD 2 {v[1]:.0%})")
        if a.basis != "own":
            ax.set_xlim(x0 - pad, x1 + pad); ax.set_ylim(y0 - pad, y1 + pad)
    for ax in axes.flat[len(out):]:
        ax.axis("off")
    basis = {"own": "each step's own SVD", "first": "SVD of the first step", "last": "SVD of the last step"}[a.basis]
    fig.suptitle(f"{LABEL.get(a.color, a.color)}  |  axes: {basis}", fontsize=10)
    fig.tight_layout()
    path = a.out or os.path.join(a.dir, f"series_{a.color}_{a.basis}.png")
    fig.savefig(path, dpi=130); plt.close(fig)
    print(f"{len(out)} steps -> {path}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="choose and label the probe positions (once)")
    b.add_argument("--out", default=str(DEFAULT))
    b.add_argument("--strata", default=str(paths.LICHESS / "puzzles" / "strata"))
    b.add_argument("--per-stratum", type=int, default=400, help="puzzle start positions per stratum")
    b.add_argument("--pgn", default=None, help="games to draw ordinary positions from (one per game)")
    b.add_argument("--games-n", type=int, default=1000)
    b.add_argument("--random-n", type=int, default=0, help="positions from random play (testing without data)")
    b.add_argument("--nodes", type=int, default=200000, help="Stockfish nodes per position")
    b.add_argument("--multipv", type=int, default=8)
    b.add_argument("--good-margin", type=float, default=5.0, help="win%% within the best that counts as a good move")
    b.add_argument("--threads", type=int, default=4)
    b.add_argument("--no-engine", action="store_true")
    b.add_argument("--seed", type=int, default=0)
    s = sub.add_parser("snapshot", help="one checkpoint, after the fact")
    s.add_argument("--ckpt", required=True)
    s.add_argument("--probe", default=str(DEFAULT))
    s.add_argument("--out-dir", default=None, help="default: <ckpt>_probe/")
    s.add_argument("--colors", default="legal,sharpness,source")
    s.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    r = sub.add_parser("series", help="grid of saved snapshots over training")
    r.add_argument("--dir", required=True)
    r.add_argument("--probe", default=str(DEFAULT))
    r.add_argument("--color", default="sharpness", choices=["legal", "sharpness", "good", "rating", "source", "svd3"])
    r.add_argument("--basis", default="own", choices=["own", "first", "last"])
    r.add_argument("--panels", type=int, default=8)
    r.add_argument("--out", default=None)
    a = ap.parse_args()
    if a.cmd == "build":
        build(a)
    elif a.cmd == "snapshot":
        from common import load_model
        m = load_model(a.ckpt, a.device)
        step = torch.load(a.ckpt, map_location="cpu", weights_only=False).get("extra", {}).get("step", 0)
        snapshot(m, step, a.out_dir or os.path.splitext(a.ckpt)[0] + "_probe", a.probe, a.colors.split(","))
    else:
        series(a)


if __name__ == "__main__":
    main()
