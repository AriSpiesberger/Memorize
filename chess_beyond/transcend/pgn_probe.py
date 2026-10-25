"""Where does the PGN model put game positions, just before it moves?

A position is a moment in a real game: the moves so far, in the model's own
format, ending where the model would start writing the next move (pgn_model.prompt:
"...<n>." for White, "...<White's move> " for Black). The vector is the last
layer's state at that last character, after the final LayerNorm: the thing the
head reads before it writes the move.

  population  one position per held-out game (make_pgn_data.py's first val_games of
              each dataset; --per-band of them, 50,000 per band on Modal, so 100,000),
              at a random ply from --min-ply on. The SVD is fitted on these.
  labelled    10 positions from games at another level (e.g. 1600-1800), each
              picked by a rule a person can check at a glance (mate in one, rook
              endgame, ...). They are projected onto the SVD and marked.

At every eval, snapshot() writes <dir>/step<N>.png: every population position as
a dot on singular vectors 1 and 2, coloured by singular vector 3 (all in standard
deviations of the population), with the 10 labelled positions numbered on top and
a key giving each one's SV3; and
<dir>/step<N>.npz: every position's coordinates on the top 10 singular vectors,
those vectors, the full singular-value spectrum, and (every 10th snapshot) the raw
vectors; plus a line in <dir>/log.jsonl: variance on the top 10 components, how
many directions hold 90% of it, the labelled positions' coordinates, and how well a
cross-validated linear probe reads each label from the full vector (R^2). Each component's sign is aligned
with the previous snapshot in the same folder, so colours and positions are
comparable across training, and the same probe set serves every model.

  python transcend/pgn_probe.py build --data data/transcend/pgn-1000-1300 data/transcend/pgn-2400+ \\
      --labelled-pgn data/lichess/bands/2025-06-probe/1600-1800.pgn       # -> data/pgn_probe/
  python transcend/pgn_probe.py snapshot --ckpt runs/transcend/pgn-1000-1300.pt
train_pgn.py calls snapshot() at every eval when data/pgn_probe/ exists (--probe).
"""
import argparse
import io
import json
import math
import os
import random
import zlib
import sys
from pathlib import Path

import chess
import chess.pgn
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))          # transcend/: pgn_model
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))      # chess_beyond/: paths, probe
import paths
from pgn_model import SPACE, VOCAB, encode, prompt
from probe import corr

DEFAULT = paths.DATA / "pgn_probe"
VALUES = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9}
RESULTS = {"1-0": 1, "0-1": -1, "1/2-1/2": 0}
LABELS = ("ply", "legal", "material", "pieces", "surprise", "band")


# ----------------------------------------------------------------- labels
def material(board, color):
    return sum(VALUES[p.piece_type] for p in board.piece_map().values() if p.color == color and p.piece_type in VALUES)


def describe(board, ply, result):
    """Labels any position gets: complexity, material, phase, and the result for the mover."""
    mover = board.turn
    res = RESULTS.get(result)
    return dict(
        ply=ply,
        move_number=ply // 2 + 1,
        side="white" if mover == chess.WHITE else "black",
        legal=board.legal_moves.count(),
        material=material(board, mover) - material(board, not mover),
        pieces=sum(1 for p in board.piece_map().values() if p.piece_type != chess.KING),
        result_for_mover=None if res is None else (res if mover == chess.WHITE else -res),
    )


def parse_movetext(text):
    """make_pgn_data's ';1.e4 e5 2.Nf3 ... 1-0' -> (SAN moves, result)."""
    toks = text.lstrip(";").split()
    result = toks[-1] if toks and toks[-1] in RESULTS else None
    sans = [t.split(".", 1)[1] if "." in t else t for t in (toks[:-1] if result else toks)]
    return [s for s in sans if s], result


def held_out_games(data_dir):
    """The held-out games of a make_pgn_data.py folder, as movetext."""
    data_dir = Path(data_dir)
    meta = json.loads((data_dir / "meta.json").read_text())
    tokens = np.fromfile(data_dir / "tokens.bin", dtype=np.uint8)
    starts = np.load(data_dir / "starts.npy")
    nv = meta["val_games"]
    ends = list(starts[1:nv + 1]) if nv < len(starts) else list(starts[1:]) + [len(tokens)]
    chars = np.array(list(VOCAB))
    for s, e in zip(starts[:nv], ends):
        yield "".join(chars[tokens[s:e]])


def population(data_dirs, names, per_band, min_ply, rng, per_game=1):
    """Up to per_game positions (distinct random plies from min_ply on) from each held-out game,
    per_band in all per folder. Rows go round-robin (every game's first position, then every
    game's second, ...), so any prefix of a band spreads over all its games."""
    rows = []
    for d, name in zip(data_dirs, names):
        per_game_rows = []
        for g, text in enumerate(held_out_games(d)):
            sans, result = parse_movetext(text)
            if len(sans) <= min_ply:
                continue
            plies = sorted(rng.sample(range(min_ply, len(sans)), min(per_game, len(sans) - min_ply)))
            got, b = [], chess.Board()
            try:
                for ply in range(max(plies) + 1):
                    if ply in plies:
                        b.parse_san(sans[ply])
                        got.append(dict(prompt=prompt(b), next_san=sans[ply], fen=b.fen(), band=name, game=g,
                                        **describe(b, ply, result)))
                    b.push_san(sans[ply])
            except ValueError:
                continue
            rng.shuffle(got)
            per_game_rows.append(got)
        band, k = [], 0
        while len(band) < per_band and any(k < len(r) for r in per_game_rows):
            band += [r[k] for r in per_game_rows if k < len(r)]
            k += 1
        band = band[:per_band]
        rows += band
        print(f"{name}: {len(band)} positions from {len(per_game_rows)} held-out games in {d}")
    return rows


def grouped_r2(H, y, groups, folds=5, lam=1.0):
    """probe.probe_r2, but folds split by game, so positions from one game never sit on both
    sides of a fold."""
    ok = ~np.isnan(y)
    if ok.sum() < 50 or np.nanstd(y) == 0:
        return None
    X, y, groups = H[ok], y[ok], groups[ok]
    fold = np.array([zlib.crc32(g.encode()) % folds for g in groups])          # stable across runs
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


# ----------------------------------------------------------------- the 10 labelled positions
def king_cover(board, color):
    """Own pawns on the squares next to the king (0-8): a rough king-safety count."""
    k = board.king(color)
    return sum(1 for sq in chess.SquareSet(chess.BB_KING_ATTACKS[k])
               if board.piece_type_at(sq) == chess.PAWN and board.color_at(sq) == color)


def only(board, kinds):
    return all(p.piece_type in kinds | {chess.KING} for p in board.piece_map().values())


def rules():
    """(name, test) in display order; each test sees the board before the next move and the ply."""
    def mate_in_one(b, ply):
        for mv in b.legal_moves:
            b.push(mv)
            mate = b.is_checkmate()
            b.pop()
            if mate:
                return True
        return False

    def free_queen(b, ply):
        q = b.pieces(chess.QUEEN, not b.turn)
        return any(b.is_attacked_by(b.turn, sq) and not b.is_attacked_by(not b.turn, sq) for sq in q)

    def promotes_next(b, ply):
        rank, step = (6, 8) if b.turn == chess.WHITE else (1, -8)
        return any(chess.square_rank(sq) == rank and b.piece_at(sq + step) is None
                   for sq in b.pieces(chess.PAWN, b.turn))

    def level(b):
        return material(b, chess.WHITE) == material(b, chess.BLACK)

    return [
        ("Early opening", lambda b, ply: ply == 4 and b.fullmove_number == 3),
        ("Quiet middlegame", lambda b, ply: 40 <= ply <= 60 and level(b) and not b.is_check()
         and b.legal_moves.count() >= 30 and not any(b.is_capture(m) for m in b.legal_moves)),
        ("Mate in one available", mate_in_one),
        ("Opponent's queen hangs", free_queen),
        ("Forced reply: one legal move", lambda b, ply: b.is_check() and b.legal_moves.count() == 1),
        ("Pawn about to promote", promotes_next),
        ("King and pawn endgame", lambda b, ply: only(b, {chess.PAWN}) and len(b.pieces(chess.PAWN, chess.WHITE))
         and len(b.pieces(chess.PAWN, chess.BLACK))),
        ("Rook endgame", lambda b, ply: only(b, {chess.PAWN, chess.ROOK}) and len(b.pieces(chess.ROOK, chess.WHITE))
         and len(b.pieces(chess.ROOK, chess.BLACK))),
        ("Up a queen or more", lambda b, ply: abs(material(b, chess.WHITE) - material(b, chess.BLACK)) >= 9),
        ("Long, tense game", lambda b, ply: ply >= 80 and level(b) and b.pieces(chess.QUEEN, chess.WHITE)
         and b.pieces(chess.QUEEN, chess.BLACK) and king_cover(b, chess.WHITE) <= 1 and king_cover(b, chess.BLACK) <= 1),
    ]


def labelled(pgn_path, max_games, name):
    """First position matching each rule, scanning games in file order (one position per game)."""
    found = {}
    todo = rules()
    with open(pgn_path, encoding="utf-8") as f:
        for _ in range(max_games):
            g = chess.pgn.read_game(f)
            if g is None or len(found) == len(todo):
                break
            b = g.board()
            moves = list(g.mainline_moves())
            for ply, mv in enumerate(moves):
                hit = next((r for r, test in todo if r not in found and test(b, ply)), None)
                if hit:
                    site = g.headers.get("Site", "")
                    found[hit] = dict(
                        label=hit, prompt=prompt(b), next_san=b.san(mv), fen=b.fen(), band=name,
                        white_elo=g.headers.get("WhiteElo"), black_elo=g.headers.get("BlackElo"),
                        link=f"{site}#{ply}" if site else "", **describe(b, ply, g.headers.get("Result")))
                    break                                   # one position per game
                b.push(mv)
    rows = [found[r] for r, _ in todo if r in found]
    missing = [r for r, _ in todo if r not in found]
    print(f"labelled: {len(rows)} positions" + (f"; none found for {missing}" if missing else ""))
    return rows


def build(a):
    rng = random.Random(a.seed)
    names = a.names or [Path(d).name.removeprefix("pgn-") for d in a.data]
    pop = population(a.data, names, a.per_band, a.min_ply, rng, a.per_game)
    lab = labelled(a.labelled_pgn, a.labelled_games, a.labelled_name)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for fname, rows in (("population.jsonl", pop), ("labelled.jsonl", lab)):
        with open(out / fname, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
    (out / "meta.json").write_text(json.dumps(dict(data=a.data, names=names, per_band=a.per_band, per_game=a.per_game,
                                                   min_ply=a.min_ply,
                                                   labelled_pgn=a.labelled_pgn, seed=a.seed), indent=1))
    for i, r in enumerate(lab, 1):
        print(f"  {i:2d}  {r['label']:<30s} move {r['move_number']:3d}  {r['link']}")
    print(f"-> {out}: {len(pop)} population positions, {len(lab)} labelled")


# ----------------------------------------------------------------- activations
_cache = {}


def load(probe_dir):
    probe_dir = str(probe_dir)
    if probe_dir not in _cache:
        rd = lambda n: [json.loads(l) for l in open(os.path.join(probe_dir, n), encoding="utf-8")]
        _cache[probe_dir] = (rd("population.jsonl"), rd("labelled.jsonl"))
    return _cache[probe_dir]


@torch.no_grad()
def states(model, rows, batch=256):
    """Per position: the last-layer state at the end of the prompt, and how the model
    rates the move actually played (-log p in nats, and whether greedy decoding writes it).
    Batched on the device; positions are grouped by length to keep padding small."""
    was = model.training
    model.eval()
    dev = next(model.parameters()).device
    seqs, cut, mlen = [], [], []
    for r in rows:
        move = encode(r["next_san"]) + [SPACE]
        p = encode(r["prompt"])[-(model.ctx - len(move)):]          # long games keep their latest moves
        seqs.append(p + move)
        cut.append(len(p))
        mlen.append(len(move))
    order = sorted(range(len(seqs)), key=lambda i: len(seqs[i]))
    H = np.zeros((len(seqs), model.ln.normalized_shape[0]), dtype=np.float32)
    surprise, greedy = np.zeros(len(seqs)), np.zeros(len(seqs), dtype=bool)
    for s in range(0, len(order), batch):
        idx = order[s:s + batch]
        n, m = max(len(seqs[i]) for i in idx), max(mlen[i] for i in idx)
        x = torch.full((len(idx), n), SPACE, dtype=torch.long)
        for r, i in enumerate(idx):
            x[r, :len(seqs[i])] = torch.tensor(seqs[i])
        x = x.to(dev)
        c = torch.tensor([cut[i] for i in idx], device=dev)
        ml = torch.tensor([mlen[i] for i in idx], device=dev)
        with torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev.type == "cuda"):
            feat = model.features(x)
            rows_ = torch.arange(len(idx), device=dev)[:, None]
            t = torch.arange(m, device=dev)[None, :]
            pos = (c[:, None] - 1 + t).clamp(max=n - 2)                   # states that predict the move + space
            logits = model.head(feat[rows_, pos]).float()                 # (batch, m, vocab)
        target = x[rows_, (pos + 1)]
        valid = t < ml[:, None]                                           # this row's move + its space
        lp = torch.log_softmax(logits, -1).gather(2, target[..., None])[..., 0]
        chars = valid & (t < (ml[:, None] - 1))                           # the move's characters only
        H[idx] = feat[torch.arange(len(idx), device=dev), c - 1].float().cpu().numpy()
        surprise[idx] = (-(lp * chars).sum(1)).cpu().numpy()
        greedy[idx] = ((logits.argmax(-1) == target) | ~valid).all(1).cpu().numpy()
    model.train(was)
    return H, surprise, greedy


def basis(Hpop, prev_vt=None, k=10):
    """Centre on the population; the top k singular directions (from the d x d covariance,
    cheap for any number of positions) and the full spectrum. Signs follow the previous
    snapshot's directions when there is one, else the largest loading is positive."""
    mu = Hpop.mean(0)
    X = (Hpop - mu).astype(np.float64)
    evals, evecs = np.linalg.eigh(X.T @ X)
    evals, evecs = evals[::-1].clip(min=0), evecs[:, ::-1]
    S = np.sqrt(evals)                                                    # singular values, largest first
    Vt = evecs[:, :k].T.copy()
    for j in range(k):
        ref = prev_vt[j] if prev_vt is not None and j < len(prev_vt) else None
        sgn = np.sign(Vt[j] @ ref) if ref is not None else np.sign(Vt[j, np.argmax(np.abs(Vt[j]))])
        Vt[j] *= sgn or 1.0
    coords = X @ Vt.T
    sd = coords.std(0) + 1e-9
    return mu, Vt.astype(np.float32), sd, S, evals / evals.sum()


def figure(zpop, zlab, lab, var, step, path, title):
    """One panel: every population position as a dot on SV1 x SV2, coloured by its SV3
    (diverging, centred on 0); the labelled positions numbered on top, SV3 in the key."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, (ax, key) = plt.subplots(1, 2, figsize=(12.5, 6.2), gridspec_kw=dict(width_ratios=[1, 0.85], wspace=0.05))
    lim = np.percentile(np.abs(np.concatenate([zpop[:, :2], zlab[:, :2]])), 99.7) * 1.08
    c3 = np.percentile(np.abs(zpop[:, 2]), 98)                # colour range: symmetric about 0
    order = np.argsort(np.abs(zpop[:, 2]))                    # strongest SV3 drawn last, on top
    from matplotlib.colors import LinearSegmentedColormap
    # blue <-> red with a grey midpoint (not white), so positions near 0 on SV3 stay visible
    diverging = LinearSegmentedColormap.from_list("sv3", ["#1c5cab", "#6da7ec", "#a9a8a2", "#ec835a", "#b8302f"])
    size, alpha = (5, 0.75) if len(zpop) <= 20000 else (1.5, 0.45)        # 100k dots need to be small
    sc = ax.scatter(zpop[order, 0], zpop[order, 1], c=zpop[order, 2], cmap=diverging, vmin=-c3, vmax=c3,
                    s=size, alpha=alpha, linewidths=0, rasterized=True)
    for n, (x, y) in enumerate(zlab[:, :2], 1):
        ax.scatter(x, y, s=190, c="white", edgecolors="black", linewidths=1.3, zorder=3)
        ax.annotate(str(n), (x, y), ha="center", va="center", fontsize=8, color="black", fontweight="bold", zorder=4)
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_aspect("equal")
    ax.axhline(0, color="#ccc", lw=0.6, zorder=0); ax.axvline(0, color="#ccc", lw=0.6, zorder=0)
    ax.set_xlabel(f"singular vector 1 ({var[0]:.0%} of variance), sd")
    ax.set_ylabel(f"singular vector 2 ({var[1]:.0%} of variance), sd")
    key.axis("off")
    lines = [f"{n:>2}  {r['label']:<29s} move {r['move_number']:>3}  SV3 {z[2]:+.1f}"
             for n, (r, z) in enumerate(zip(lab, zlab), 1)]
    key.text(0.0, 0.97, "Labelled positions\n\n" + "\n".join(lines),
             va="top", ha="left", fontsize=8.5, family="monospace", transform=key.transAxes)
    cax = key.inset_axes([0.0, 0.12, 0.6, 0.035])
    fig.colorbar(sc, cax=cax, orientation="horizontal",
                 label=f"singular vector 3 ({var[2]:.0%} of variance), sd")
    fig.suptitle(f"{title} held-out game positions  |  step {step}", fontsize=11)
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)


def subset(pop, n):
    """A fixed subset of the population: the first n / (number of bands) positions of each band,
    the same rows at every snapshot so evals stay comparable. Returns row indices."""
    names = sorted({r["band"] for r in pop})
    per = n // max(len(names), 1)
    seen = {b: 0 for b in names}
    idx = []
    for i, r in enumerate(pop):
        if seen[r["band"]] < per:
            seen[r["band"]] += 1
            idx.append(i)
    return np.array(idx)


def snapshot(model, step, out_dir, probe=DEFAULT, title="PGN model", every_n=20000, full_every=0, raw_every=10):
    """Write step<N>.png/.npz and a log line for this checkpoint; None when there is no probe set.

    Each snapshot uses a fixed subset of every_n population positions (split evenly across bands,
    the same rows every time); with full_every > 0, every full_every-th snapshot uses the whole
    population instead. The SVD is fitted on whichever positions the snapshot uses. The raw
    vectors are kept on the first snapshot and every raw_every-th after it.

    step<N>.npz: which population rows were used (rows), their coordinates and the labelled
    positions' on the top 10 singular vectors (z, z_labelled; in sd of the positions used), those
    vectors (Vt), the mean (mu), the full singular-value spectrum (S, var), per-position surprise
    and greedy match, and on full snapshots the raw last-layer vectors (H, float16; ~100 MB at
    100,000 positions)."""
    probe = str(probe)
    if not os.path.exists(os.path.join(probe, "population.jsonl")):
        if probe not in _cache:
            print(f"[pgn probe] no probe set at {probe}; skipping (python transcend/pgn_probe.py build)")
            _cache[probe] = None
        return None
    pop_all, lab = load(probe)
    os.makedirs(out_dir, exist_ok=True)
    log_path = os.path.join(out_dir, "log.jsonl")
    n_before = 0 if step == 0 or not os.path.exists(log_path) else sum(1 for _ in open(log_path))
    full = (full_every and n_before % full_every == 0) or len(pop_all) <= every_n
    rows = np.arange(len(pop_all)) if full else subset(pop_all, every_n)
    pop = [pop_all[i] for i in rows]
    Hp, sp, gp = states(model, pop)
    Hl, sl, gl = states(model, lab) if lab else (np.zeros((0, Hp.shape[1])), np.zeros(0), np.zeros(0, bool))
    bpath = os.path.join(out_dir, "basis.npz")
    prev = np.load(bpath)["Vt"] if os.path.exists(bpath) and step > 0 else None
    mu, Vt, sd, S, var = basis(Hp, prev)
    np.savez(bpath, Vt=Vt, step=step)
    zp, zl = ((Hp - mu) @ Vt.T) / sd, ((Hl - mu) @ Vt.T) / sd
    record = dict(rows=rows.astype(np.int32), z=zp.astype(np.float32), z_labelled=zl.astype(np.float32), sd=sd.astype(np.float32), Vt=Vt,
                  mu=mu.astype(np.float32), S=S.astype(np.float32), var=var.astype(np.float32),
                  surprise=sp.astype(np.float32), greedy=gp, step=step)
    if n_before % raw_every == 0:
        record["H"] = Hp.astype(np.float16)
    np.savez_compressed(os.path.join(out_dir, f"step{step}.npz"), **record)
    figure(zp, zl, lab, var, step, os.path.join(out_dir, f"step{step}.png"),
           f"{title}  |  {'all' if full else 'fixed subset of'} {len(pop):,} of {len(pop_all):,}")
    names = sorted({r["band"] for r in pop})
    labels = {m: np.array([float(r[m]) if m in r and r[m] is not None else np.nan for r in pop]) for m in LABELS[:4]}
    labels["surprise"] = sp
    labels["band"] = np.array([float(names.index(r["band"])) for r in pop]) if len(names) > 1 else np.full(len(pop), np.nan)
    k90 = int(np.searchsorted(np.cumsum(var), 0.9)) + 1
    stats = dict(step=step, positions=len(pop), full=bool(full), var=[round(float(v), 4) for v in var[:10]], dims_for_90pct=k90,
                 greedy_match=float(gp.mean()), mean_surprise=float(sp.mean()))
    groups = np.array([f"{r['band']}:{r.get('game', i)}" for i, r in enumerate(pop)])
    for m, y in labels.items():
        if not np.isnan(y).all():
            stats[m] = dict(r2=grouped_r2(Hp, y, groups), corr=[corr(zp[:, j], y) for j in range(3)])
    stats["labelled"] = [dict(label=r["label"], z=[round(float(v), 3) for v in z], greedy=bool(g),
                              surprise=round(float(s), 3)) for r, z, g, s in zip(lab, zl, gl, sl)]
    with open(log_path, "w" if step == 0 else "a", encoding="utf-8") as f:
        f.write(json.dumps(stats) + "\n")
    r2 = "  ".join(f"{m} R^2 {stats[m]['r2']:.2f}" for m in LABELS if m in stats and stats[m]["r2"] is not None)
    print(f"[pgn probe step {step}, {len(pop):,} positions{' (full)' if full else ''}] SVD 1/2/3 {' / '.join(f'{v:.0%}' for v in var[:3])}  "
          f"({k90} directions hold 90%)  "
          f"plays the game's move {gp.mean():.1%}  {r2}", flush=True)
    return stats


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="choose and label the probe positions (once)")
    b.add_argument("--data", nargs="+", required=True, help="make_pgn_data.py folders; their held-out games")
    b.add_argument("--names", nargs="*", default=None, help="label per folder (default: folder name)")
    b.add_argument("--per-band", type=int, default=5000, help="positions per folder, one per held-out game")
    b.add_argument("--per-game", type=int, default=1, help="positions per held-out game (distinct plies)")
    b.add_argument("--min-ply", type=int, default=10)
    b.add_argument("--labelled-pgn", required=True, help="games to pick the 10 labelled positions from")
    b.add_argument("--labelled-name", default="1600-1800")
    b.add_argument("--labelled-games", type=int, default=20000, help="games to scan for them")
    b.add_argument("--out", default=str(DEFAULT))
    b.add_argument("--seed", type=int, default=0)
    s = sub.add_parser("snapshot", help="one checkpoint, after the fact")
    s.add_argument("--ckpt", required=True)
    s.add_argument("--probe", default=str(DEFAULT))
    s.add_argument("--out-dir", default=None, help="default: <ckpt>_pgn_probe/")
    s.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    a = ap.parse_args()
    if a.cmd == "build":
        build(a)
    else:
        from pgn_model import load_pgn_model
        model = load_pgn_model(a.ckpt, a.device)
        ck = torch.load(a.ckpt, map_location="cpu")
        step = ck.get("extra", {}).get("step", 0)
        snapshot(model, step, a.out_dir or os.path.splitext(a.ckpt)[0] + "_pgn_probe", a.probe,
                 title=Path(a.ckpt).stem)


if __name__ == "__main__":
    main()
