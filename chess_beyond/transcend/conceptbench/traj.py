"""The dynamic bench: does one unit of a model track a concept through a game: on while it holds, off when it does not?

    python transcend/conceptbench/traj.py build                  # every ply of the bench's games, labelled
    python transcend/conceptbench/traj.py acts                   # W and S at each layer, their crosscoder views, the board
    python transcend/conceptbench/traj.py score                  # the best unit per concept and readout, scored on test games
    python transcend/conceptbench/traj.py report

build  The bench's games (positions.parquet), each at every ply known: its longest prompt and the moves after it, as far as
       the model's context goes. Every static concept the bench kept, labelled at every ply; an episode is a run of
       positives at least MIN_RUN plies long, and shorter runs get no label. Plans are episodes by plan_book.py: from LEAD
       plies before the plan's first move to its last; the position of the first move is marked (2) for the lead.
       Kept: concepts with at least MIN_EPISODES episodes in fit games. -> data/.../traj/positions.parquet, labels.parquet,
       counts.json.
acts   W and S at --layers (score.py's extraction: one forward pass per game, the hook check), each layer's crosscoder
       (mixed-L<layer>/cc-L<layer>-4096) with one model's state alone (the other at its static-bench fit mean: score.py's
       cc4096-Wview / -Sview), and the board (773 binary features). -> runs/.../traj/acts/.
score  A readout's units: crosscoder latents (on: the latent fires), raw neurons (on: above or below a threshold, one of
       the 5th..95th percentiles), board features (on: present or absent). On fit games, the unit with the highest
       J = P(on | episode) - P(on | negative), on up to SAMPLE positives and SAMPLE negatives. On test games:
         J, coverage P(on | episode), false firing P(on | negative), with 95% bootstrap intervals over games;
         persistence: per episode, its longest unbroken run of on as a share of its length (mean over episodes);
         onset and offset: share of episodes where the unit turns on within 2 plies of the start (first on from 5 plies
         before) and off within 2 plies of the end;
         plans, lead: plies the unit has been on, unbroken, at the plan's first move (median; share at least 3).
       Null: each game's labels shifted round by a random 10 or more plies (episodes keep their lengths, lose their
       place), the unit picked again on fit and scored on test the same way.
       -> results/transcend/conceptbench/traj/<readout>/L<layer>.json
report -> results/transcend/conceptbench/traj/report.md
paired S's chosen unit against W's on the same test games, paired bootstrap over games -> traj/paired.md
"""

import argparse
import json
import multiprocessing as mp
import os
import sys
import time
import zlib
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import chess
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bench import DATA, MANIFEST, POSITIONS, RESULTS, RUNS, paths, prompt_of, sans_of
from labels import FAMILIES, openings, plan_book

TDATA = DATA / "traj"
TACTS = RUNS / "traj" / "acts"
TRES = RESULTS / "traj"
MIN_RUN = plan_book.MIN_RUN
MIN_EPISODES = 100          # in fit games
SAMPLE = 30_000             # fit positives and negatives each, to pick a unit
QUANTILES = np.arange(5, 96, 5)
BOOT = 1000
EDGE = 2                    # onset / offset within this many plies
LOOK = 5                    # how far before an episode a unit's turning on counts
MIN_SHIFT = 10              # the null's shift
CTX, MAX_MOVE_CHARS = 1024, 8
STATIC = ("pieces", "openings", "structures", "imbalances")
LAYERS = ("4", "8", "11", "15", "final")


# ---------------------------------------------------------------- build
def runs_of(y):
    """[(start, end inclusive)] of runs of positives (1 or 2)."""
    out, s = [], None
    for i, v in enumerate(list(y) + [0]):
        if v >= 1 and s is None:
            s = i
        elif v < 1 and s is not None:
            out.append((s, i - 1))
            s = None
    return out


def label_game(job):
    """One game -> (game_id, plies, prompts, fens, {concept: int8 per ply}), the static concepts as episodes."""
    gid, sans, keep = job
    b = chess.Board()
    boards, moves, plies = [], [], []
    for p in range(len(sans) + 1):
        pr = prompt_of(sans[:p])
        if len(pr) + MAX_MOVE_CHARS + 1 > CTX:
            break
        if p >= 1:
            boards.append(b.copy())
            plies.append(p)
        if p < len(sans):
            m = b.parse_san(sans[p])
            if p >= 1:
                moves.append(m)
            b.push(m)
    moves += [None] * (len(boards) - len(moves))
    n = len(boards)
    lab = {k: np.full(n, -1, np.int8) for k in keep}
    for i, bd in enumerate(boards):
        got = {}
        for f in STATIC:
            got.update(FAMILIES[f].labels(bd))
        app = openings.applicable(bd)
        for k in keep:
            if k.startswith("plan_"):
                continue
            if k.startswith(("eco_", "line_")):
                v = got.get(k, False if app else None)
            else:
                v = got.get(k)
            if v is not None:
                lab[k][i] = int(v)
    for k in keep:                                              # static: runs shorter than MIN_RUN get no label
        if k.startswith("plan_"):
            continue
        for s, e in runs_of(lab[k]):
            if e - s + 1 < MIN_RUN:
                lab[k][s:e + 1] = -1
    n_known = sum(m is not None for m in moves)                 # positions whose next move is seen (within the context)
    plans = plan_book.episodes(boards, moves, n_known)
    for k, v in plans.items():                                  # each episode's first plan move marked 2, for the lead
        y = np.array([-1 if x is None else x for x in v], np.int8)
        lab[k] = y
        for s, e in runs_of(y):
            first = first_move_ply(boards, moves, k, s, e)
            if first is not None:
                y[first] = 2
    return gid, plies, [prompt_of(sans[:p]) for p in plies], [bd.fen() for bd in boards], lab


def first_move_ply(boards, moves, concept, s, e):
    """The first ply in [s, e] where the plan's side played one of the plan's moves while in the structure."""
    p = plan_book.PLANS[concept[5:]]
    for i in range(s, e + 1):
        b, m = boards[i], moves[i]
        if m is None:
            continue
        c = b.turn
        if p.structure(b, c) and any(f(b, m, c) for f in p.marks.values()):
            return i
    return None


def build(a):
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    t0 = time.time()
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    keep = [k for k, c in man["concepts"].items() if c["family"] in STATIC] + list(plan_book.DEFS)
    df = pd.read_parquet(POSITIONS, columns=["game_id", "split", "ply", "prompt", "future"])
    last = df.loc[df.groupby("game_id")["ply"].idxmax()]
    jobs = []
    for gid, pr, fut in zip(last["game_id"], last["prompt"], last["future"]):
        sans = sans_of(pr)
        b = chess.Board()
        for s in sans:
            b.push_san(s)
        for u in (fut.split(",") if fut else []):
            m = chess.Move.from_uci(u)
            sans.append(b.san(m))
            b.push(m)
        jobs.append((gid, sans, keep))
    if a.games:
        jobs = jobs[:a.games]
    split = dict(zip(last["game_id"], last["split"]))
    rows, Y = [], {k: [] for k in keep}
    with mp.Pool(a.workers) as pool:
        for i, (gid, plies, prompts, fens, lab) in enumerate(pool.imap(label_game, jobs, chunksize=16)):
            rows += [(gid, split[gid], p, pr, f) for p, pr, f in zip(plies, prompts, fens)]
            for k in keep:
                Y[k].append(lab[k])
            if i % 2000 == 0:
                print(f"  {i} of {len(jobs)} games, {len(rows)} positions, {time.time() - t0:.0f}s", flush=True)
    TDATA.mkdir(parents=True, exist_ok=True)
    pos = pd.DataFrame(rows, columns=["game_id", "split", "ply", "prompt", "fen"])
    pos.insert(0, "pos_id", np.arange(len(pos)))
    pos.to_parquet(TDATA / "positions.parquet", compression="zstd")
    Y = {k: np.concatenate(v) for k, v in Y.items()}
    is_fit = pos["split"].to_numpy() == "fit"
    gidx = pd.factorize(pos["game_id"])[0]
    counts = {}
    for k, y in Y.items():
        ep = episode_table(y, gidx)
        fam = "plans" if k.startswith("plan_") else man["concepts"][k]["family"]
        c = dict(family=fam, definition=plan_book.DEFS.get(k) or man["concepts"][k]["definition"],
                 fit_episodes=int(sum(is_fit[s] for s, _ in ep)), test_episodes=int(sum(not is_fit[s] for s, _ in ep)),
                 fit_pos=int(((y >= 1) & is_fit).sum()), fit_neg=int(((y == 0) & is_fit).sum()),
                 test_pos=int(((y >= 1) & ~is_fit).sum()), test_neg=int(((y == 0) & ~is_fit).sum()),
                 mean_episode=float(np.mean([e - s + 1 for s, e in ep])) if ep else 0.0)
        c["kept"] = c["fit_episodes"] >= MIN_EPISODES and c["test_episodes"] > 0 and c["fit_neg"] > 0
        counts[k] = c
    pq.write_table(pa.table({"pos_id": np.arange(len(pos)), **{k: Y[k] for k in keep}}), TDATA / "labels.parquet", compression="zstd")
    (TDATA / "counts.json").write_text(json.dumps(dict(min_run=MIN_RUN, min_episodes=MIN_EPISODES, positions=len(pos),
                                                      games=int(pos["game_id"].nunique()), plan_book_version=plan_book.VERSION,
                                                      concepts=counts), indent=1), encoding="utf-8")
    kept = [k for k, c in counts.items() if c["kept"]]
    print(f"{len(pos)} positions from {pos['game_id'].nunique()} games; {len(kept)} of {len(counts)} concepts kept "
          f"({sum(k.startswith('plan_') for k in kept)} plans) ({(time.time() - t0) / 60:.1f} min)", flush=True)
    write_counts(counts)


def episode_table(y, gidx):
    """[(start, end inclusive)] of positive runs, not crossing games."""
    pos = (y >= 1).astype(np.int8)
    brk = np.r_[True, gidx[1:] != gidx[:-1]]
    starts = np.flatnonzero(pos & (brk | np.r_[True, pos[:-1] == 0]))
    ends = np.flatnonzero(pos & (np.r_[brk[1:], True] | np.r_[pos[1:] == 0, True]))
    return list(zip(starts, ends))


def write_counts(counts):
    TRES.mkdir(parents=True, exist_ok=True)
    out = ["# Dynamic bench: episodes per concept", "",
           f"An episode: a run of at least {MIN_RUN} plies where the concept holds (plans: plan_book.py). Kept: at least "
           f"{MIN_EPISODES} episodes in fit games.", "",
           "| family | concept | fit episodes | test episodes | mean length | fit + / - plies | |", "|---|---|--:|--:|--:|--:|---|"]
    for k, c in sorted(counts.items(), key=lambda kv: (kv[1]["family"], kv[0])):
        out.append(f"| {c['family']} | {k} | {c['fit_episodes']} | {c['test_episodes']} | {c['mean_episode']:.1f} | "
                   f"{c['fit_pos']} / {c['fit_neg']} | {'' if c['kept'] else '**dropped**'} |")
    (TRES / "counts.md").write_text("\n".join(out) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- acts
def acts(a):
    import pandas as pd
    import scipy.sparse as sp
    import score
    score.ACTS = TACTS
    df = pd.read_parquet(TDATA / "positions.parquet", columns=["pos_id", "game_id", "ply", "prompt"])
    layers = a.layers.split(",")
    for name in ("W", "S"):
        score.extract(name, score.MODELS[name], layers, df, a)
    for L in layers:
        views(L, len(df))
    path = TACTS / "board" / "board.npz"
    if not path.exists():
        fens = pd.read_parquet(TDATA / "positions.parquet", columns=["fen"])["fen"]
        rows, cols = [], []
        for i, fen in enumerate(fens):
            b = chess.Board(fen)
            for s_, p in b.piece_map().items():
                rows.append(i)
                cols.append((p.piece_type - 1 + 6 * (p.color == chess.BLACK)) * 64 + s_)
            extra = [b.turn == chess.WHITE, b.has_kingside_castling_rights(chess.WHITE), b.has_queenside_castling_rights(chess.WHITE),
                     b.has_kingside_castling_rights(chess.BLACK), b.has_queenside_castling_rights(chess.BLACK)]
            for j, v in enumerate(extra):
                if v:
                    rows.append(i)
                    cols.append(768 + j)
        path.parent.mkdir(parents=True, exist_ok=True)
        sp.save_npz(path, sp.csr_matrix((np.ones(len(rows), np.float32), (rows, cols)), shape=(len(fens), 773)))
        print(f"  board: {len(rows)} entries", flush=True)


def views(L, n):
    """Each model alone through layer L's crosscoder, the other at its static-bench fit mean -> sparse latents."""
    import scipy.sparse as sp
    import torch
    import crosscoder as cx
    outs = {v: TACTS / f"cc4096-{'WS'[v]}view" / f"L{L}.npz" for v in (0, 1)}
    if all(p.exists() for p in outs.values()):
        return
    ck = torch.load(paths.ROOT / f"runs/transcend/crosscoder/mixed-L{L}/cc-L{L}-4096/cc.pt", map_location="cpu", weights_only=False)
    if [tuple(s) for s in ck["sources"]] != [(0, L), (1, L)]:
        sys.exit(f"L{L}: crosscoder sources {ck['sources']}")
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    cc = cx.CrossCoder(2, ck["d"], ck["latents"], ck["k"]).to(dev)
    cc.load_state_dict(ck["state"])
    scales = ck["scales"].to(dev)
    src = [np.load(TACTS / m / f"L{L}.npy", mmap_mode="r") for m in ("W", "S")]
    fit_mean = [torch.from_numpy(np.load(RUNS / "acts" / m / f"L{L}.stats.npz")["mean"]).float().to(dev) for m in ("W", "S")]
    for v, path in outs.items():
        parts, l0 = [], 0.0
        with torch.no_grad():
            for i in range(0, n, 16384):
                x = torch.from_numpy(np.stack([np.asarray(s[i:i + 16384], np.float32) for s in src], 1)).to(dev) * scales[None, :, None]
                x[:, 1 - v] = fit_mean[1 - v] * scales[1 - v]
                f, _, _ = cc.encode(x)
                l0 += float((f > 0).sum())
                parts.append(sp.csr_matrix(f.cpu().numpy().astype(np.float32)))
        path.parent.mkdir(parents=True, exist_ok=True)
        sp.save_npz(path, sp.vstack(parts).tocsr())
        print(f"  {path.parent.name} L{L}: {l0 / n:.1f} latents on per position", flush=True)


# ---------------------------------------------------------------- score
_R = {}


def load_readout(readout, L):
    """-> ('raw', memmap) or ('sparse', csr, csc) for the readout's units."""
    import scipy.sparse as sp
    if readout in ("W", "S"):
        return ("raw", np.load(TACTS / readout / f"L{L}.npy", mmap_mode="r"))
    path = TACTS / "board" / "board.npz" if readout == "board" else TACTS / readout / f"L{L}.npz"
    A = sp.load_npz(path).tocsr()
    A.data = (A.data > 0).astype(np.float32)
    A.eliminate_zeros()
    return ("sparse", A, A.tocsc())


def init_worker(readout, L, gidx):
    _R["unit"] = load_readout(readout, L)
    _R["readout"], _R["gidx"] = readout, gidx
    if _R["unit"][0] == "raw":
        X = _R["unit"][1]
        rng = np.random.default_rng(0)
        idx = np.sort(rng.choice(len(X), min(len(X), 200_000), replace=False))
        _R["thr"] = np.percentile(np.asarray(X[idx], np.float32), QUANTILES, axis=0)       # (quantiles, units)


def pick(pos_idx, neg_idx):
    """The best unit on these fit positives and negatives -> (unit description, J)."""
    kind = _R["unit"][0]
    if kind == "raw":
        X = _R["unit"][1]
        P_, N_ = np.asarray(X[np.sort(pos_idx)], np.float32), np.asarray(X[np.sort(neg_idx)], np.float32)
        best = (-1.0, None)
        for q, t in enumerate(_R["thr"]):
            j = (P_ > t).mean(0) - (N_ > t).mean(0)
            for sign, jj in ((1, j), (-1, -j)):
                u = int(np.argmax(jj))
                if jj[u] > best[0]:
                    best = (float(jj[u]), dict(unit=u, threshold=float(t[u]), sign=sign, quantile=int(QUANTILES[q])))
        return best[1], best[0]
    A = _R["unit"][1]
    w = np.zeros(A.shape[0], np.float32)
    w[pos_idx] = 1 / len(pos_idx)
    w[neg_idx] = -1 / len(neg_idx)
    j = A.T @ w
    signs = (1, -1) if _R["readout"] == "board" else (1,)
    best = (-1.0, None)
    for sign in signs:
        u = int(np.argmax(sign * j))
        if sign * j[u] > best[0]:
            best = (float(sign * j[u]), dict(unit=u, sign=sign))
    return best[1], best[0]


def activity(unit, idx):
    """Whether the unit is on at these positions (sorted)."""
    if _R["unit"][0] == "raw":
        x = np.asarray(_R["unit"][1][idx, unit["unit"]], np.float32)
        return (x > unit["threshold"]) if unit["sign"] > 0 else (x <= unit["threshold"])
    col = _R["unit"][2][:, unit["unit"]]
    on = np.zeros(_R["unit"][2].shape[0], bool)
    on[col.indices] = True
    on = on[idx]
    return on if unit["sign"] > 0 else ~on


def shifted(y, gidx, rng):
    """Each game's labels shifted round by MIN_SHIFT or more plies; games too short for that: no label."""
    out = np.full_like(y, -1)
    starts = np.flatnonzero(np.r_[True, gidx[1:] != gidx[:-1]])
    for s, e in zip(starts, np.r_[starts[1:], len(y)]):
        n = e - s
        if n >= 2 * MIN_SHIFT:
            out[s:e] = np.roll(y[s:e], int(rng.integers(MIN_SHIFT, n - MIN_SHIFT + 1)))
    return out


def evaluate(unit, y, test, rng):
    """Test metrics for a unit: y over all positions, test a boolean mask."""
    gidx = _R["gidx"]
    idx = np.flatnonzero(test)
    on = activity(unit, idx)
    yt, gt = y[idx], gidx[idx]
    episodes = episode_table(yt, gt)
    pos, neg = yt >= 1, yt == 0
    games, g = np.unique(gt, return_inverse=True)
    cov_n, cov_d = np.bincount(g, on & pos, len(games)), np.bincount(g, pos, len(games))
    fal_n, fal_d = np.bincount(g, on & neg, len(games)), np.bincount(g, neg, len(games))
    J = cov_n.sum() / max(cov_d.sum(), 1) - fal_n.sum() / max(fal_d.sum(), 1)
    boots = []
    for _ in range(BOOT):
        w = rng.multinomial(len(games), np.full(len(games), 1 / len(games)))
        boots.append((w @ cov_n) / max(w @ cov_d, 1) - (w @ fal_n) / max(w @ fal_d, 1))
    persist, onset, offset, leads = [], [], [], []
    for s, e in episodes:
        run, best = 0, 0
        for v in on[s:e + 1]:
            run = run + 1 if v else 0
            best = max(best, run)
        persist.append(best / (e - s + 1))
        lo = s
        while lo > 0 and s - lo < LOOK and gt[lo - 1] == gt[s]:
            lo -= 1
        hits = np.flatnonzero(on[lo:e + 1])
        onset.append(bool(len(hits)) and abs(lo + hits[0] - s) <= EDGE)
        hi = e
        while hi + 1 < len(on) and hi - e < LOOK and gt[hi + 1] == gt[s]:
            hi += 1
        hits = np.flatnonzero(on[s:hi + 1])
        offset.append(bool(len(hits)) and abs(s + hits[-1] - e) <= EDGE)
        first = np.flatnonzero(yt[s:e + 1] == 2)
        if len(first):
            f = s + first[0]
            k = 0
            while f - k >= 0 and gt[f - k] == gt[s] and on[f - k]:
                k += 1
            leads.append(k)
    out = dict(J=float(J), J_ci=np.quantile(boots, [.025, .975]).tolist(),
               coverage=float(cov_n.sum() / max(cov_d.sum(), 1)), false=float(fal_n.sum() / max(fal_d.sum(), 1)),
               persistence=float(np.mean(persist)) if persist else None,
               onset=float(np.mean(onset)) if onset else None, offset=float(np.mean(offset)) if offset else None,
               test_episodes=len(episodes), test_games=len(games))
    if leads:
        out.update(lead_median=float(np.median(leads)), lead3=float(np.mean(np.array(leads) >= 3)), lead_n=len(leads))
    return out


def score_job(job):
    concept, y, is_fit = job
    rng = np.random.default_rng(zlib.crc32(f"{_R['readout']}/{concept}".encode()))
    res = {}
    for which, yy in (("real", y), ("null", shifted(y, _R["gidx"], rng))):
        pos_idx = np.flatnonzero((yy >= 1) & is_fit)
        neg_idx = np.flatnonzero((yy == 0) & is_fit)
        if not len(pos_idx) or not len(neg_idx):
            res[which] = None
            continue
        pos_idx = rng.choice(pos_idx, min(SAMPLE, len(pos_idx)), replace=False)
        neg_idx = rng.choice(neg_idx, min(SAMPLE, len(neg_idx)), replace=False)
        unit, j_fit = pick(pos_idx, neg_idx)
        r = evaluate(unit, yy, ~is_fit, rng)
        r.update(unit=unit, J_fit=j_fit)
        res[which] = r
    return concept, res


def run_score(a):
    import pandas as pd
    counts = json.loads((TDATA / "counts.json").read_text(encoding="utf-8"))["concepts"]
    kept = [k for k, c in counts.items() if c["kept"]]
    if a.concepts:
        kept = [k for k in kept if k in a.concepts.split(",")]
    pos = pd.read_parquet(TDATA / "positions.parquet", columns=["game_id", "split"])
    gidx = pd.factorize(pos["game_id"])[0]
    is_fit = pos["split"].to_numpy() == "fit"
    lab = pd.read_parquet(TDATA / "labels.parquet", columns=kept)
    targets = [("board", "board")] + [(r, L) for L in a.layers.split(",") for r in a.readouts.split(",")]
    for r, L in targets:
        out = TRES / r / f"L{L}.json"
        done = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
        todo = [k for k in kept if k not in done]
        if not todo:
            continue
        t0 = time.time()
        with mp.Pool(a.workers, init_worker, (r, L, gidx)) as pool:
            for i, (k, res) in enumerate(pool.imap_unordered(score_job, [(k, lab[k].to_numpy(), is_fit) for k in todo])):
                done[k] = res
                if i % 20 == 0 or i == len(todo) - 1:
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_text(json.dumps(done, indent=1), encoding="utf-8")
        print(f"  {r} L{L}: {len(todo)} concepts ({(time.time() - t0) / 60:.1f} min)", flush=True)


# ---------------------------------------------------------------- report
def report(a):
    counts = json.loads((TDATA / "counts.json").read_text(encoding="utf-8"))["concepts"]
    kept = [k for k, c in counts.items() if c["kept"]]
    fams = ["pieces", "openings", "structures", "imbalances", "plans"]
    readouts = a.readouts.split(",")
    layers = a.layers.split(",")

    def load(r, L):
        p = TRES / r / f"L{L}.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    board = load("board", "board")
    R = {(r, L): load(r, L) for r in readouts for L in layers}
    names = {"W": "W raw", "S": "S raw", "cc4096-Wview": "W through cc", "cc4096-Sview": "S through cc", "board": "board"}
    out = ["# Dynamic bench: one unit tracking a concept through a game", "",
           "Per concept and readout, the single unit (a crosscoder latent, a raw neuron with a threshold, a board feature) that "
           "best separates the concept's episodes from its negatives on fit games, scored on test games. J = P(on | episode) - "
           "P(on | negative), with a 95% bootstrap interval over games; null: the same with each game's labels shifted round "
           "(episodes keep their length, lose their place), which a unit tracking the concept should fail. Persistence: an "
           "episode's longest unbroken on-run as a share of its length. Onset / offset: on within 2 plies of the start / off "
           "within 2 of the end. Plans, lead: plies on, unbroken, at the plan's first move.", "",
           f"{len(kept)} concepts kept (at least {MIN_EPISODES} fit episodes of at least {MIN_RUN} plies); counts in counts.md.", "",
           "## Family means: J (null J), persistence", ""]
    head = "| family | " + " | ".join(f"{names.get(r, r)} L{L}" for L in layers for r in readouts) + " | board |"
    out += [head, "|---|" + "---|" * (len(layers) * len(readouts) + 1)]

    def cell(res):
        if not res or not res.get("real"):
            return None
        return res["real"]["J"], (res["null"] or {}).get("J", np.nan), res["real"]["persistence"]
    for f in fams:
        ks = [k for k in kept if counts[k]["family"] == f]
        if not ks:
            continue
        cells = []
        for src in [R[(r, L)] for L in layers for r in readouts] + [board]:
            v = [cell(src.get(k)) for k in ks]
            v = [x for x in v if x]
            cells.append(f"{np.mean([x[0] for x in v]):.3f} ({np.nanmean([x[1] for x in v]):.3f}), {np.mean([x[2] for x in v]):.2f}"
                         if v else "")
        out.append(f"| {f} ({len(ks)}) | " + " | ".join(cells) + " |")
    out.append("")
    for f in fams:
        ks = sorted(k for k in kept if counts[k]["family"] == f)
        if not ks:
            continue
        for L in layers:
            out += [f"## {f}, L{L}", "", "| concept | fit / test episodes | " + " | ".join(names.get(r, r) for r in readouts)
                    + " | board |", "|---|--:|" + "---|" * (len(readouts) + 1)]
            for k in ks:
                cells = []
                for src in [R[(r, L)] for r in readouts] + [board]:
                    res = src.get(k)
                    if not res or not res.get("real"):
                        cells.append("")
                        continue
                    x, nl = res["real"], res["null"] or {}
                    c = (f"{x['J']:.2f} [{x['J_ci'][0]:.2f}, {x['J_ci'][1]:.2f}] n{nl.get('J', float('nan')):.2f} "
                         f"p{x['persistence']:.2f} u{x['unit']['unit']}")
                    if "lead_median" in x:
                        c += f" lead {x['lead_median']:.0f} ({x['lead3']:.0%} at 3+)"
                    cells.append(c)
                out.append(f"| {k} | {counts[k]['fit_episodes']} / {counts[k]['test_episodes']} | " + " | ".join(cells) + " |")
            out.append("")
    TRES.mkdir(parents=True, exist_ok=True)
    (TRES / "report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {TRES / 'report.md'}")


# ---------------------------------------------------------------- paired: S against W on the same test games
def test_activity(readout, L, units, test_idx):
    """{concept: on at the test positions} for each concept's chosen unit of this readout."""
    kind = load_readout(readout, L)
    out = {}
    if kind[0] == "raw":
        X = np.asarray(kind[1][test_idx], np.float32)
        for k, u in units.items():
            x = X[:, u["unit"]]
            out[k] = (x > u["threshold"]) if u["sign"] > 0 else (x <= u["threshold"])
    else:
        C = kind[2]
        for k, u in units.items():
            on = np.zeros(C.shape[0], bool)
            on[C[:, u["unit"]].indices] = True
            on = on[test_idx]
            out[k] = on if u["sign"] > 0 else ~on
    return out


def game_counts(on, y, g, n_games):
    pos, neg = y >= 1, y == 0
    return np.stack([np.bincount(g, on & pos, n_games), np.bincount(g, pos, n_games),
                     np.bincount(g, on & neg, n_games), np.bincount(g, neg, n_games)])


def leads_of(on, y, gt):
    """Per episode with a marked first plan move: (game, plies on unbroken at it)."""
    out = []
    for s, e in episode_table(y, gt):
        first = np.flatnonzero(y[s:e + 1] == 2)
        if len(first):
            f, k = s + first[0], 0
            while f - k >= 0 and gt[f - k] == gt[s] and on[f - k]:
                k += 1
            out.append((gt[s], k))
    return out


def paired(a):
    """For each layer, S's chosen unit against W's (raw, and through the crosscoder), on the same test games: the
    difference in J (S - W) with a paired bootstrap over games, and for plans the difference in mean lead."""
    import pandas as pd
    counts = json.loads((TDATA / "counts.json").read_text(encoding="utf-8"))["concepts"]
    kept = [k for k, c in counts.items() if c["kept"]]
    pos = pd.read_parquet(TDATA / "positions.parquet", columns=["game_id", "split"])
    gidx = pd.factorize(pos["game_id"])[0]
    test_idx = np.flatnonzero(pos["split"].to_numpy() == "test")
    games, g = np.unique(gidx[test_idx], return_inverse=True)
    lab = pd.read_parquet(TDATA / "labels.parquet", columns=kept)
    Y = {k: lab[k].to_numpy()[test_idx] for k in kept}
    rng = np.random.default_rng(0)
    boot = rng.multinomial(len(games), np.full(len(games), 1 / len(games)), size=BOOT).astype(np.float64)  # shared by S and W
    one = np.ones((1, len(games)))

    def J(c, w):
        return (w @ c[0]) / np.maximum(w @ c[1], 1) - (w @ c[2]) / np.maximum(w @ c[3], 1)
    out = {}
    for L in a.layers.split(","):
        for wr, sr in (("W", "S"), ("cc4096-Wview", "cc4096-Sview")):
            res = {r: json.loads((TRES / r / f"L{L}.json").read_text(encoding="utf-8")) for r in (wr, sr)}
            act = {r: test_activity(r, L, {k: res[r][k]["real"]["unit"] for k in kept if (res[r].get(k) or {}).get("real")},
                                    test_idx) for r in (wr, sr)}
            rows = {}
            for k in kept:
                if k not in act[wr] or k not in act[sr]:
                    continue
                cw, cs = (game_counts(act[r][k], Y[k], g, len(games)) for r in (wr, sr))
                jw, js = float(J(cw, one)[0]), float(J(cs, one)[0])
                db = J(cs, boot) - J(cw, boot)
                row = dict(J_W=jw, J_S=js, dJ=js - jw, dJ_ci=np.quantile(db, [.025, .975]).tolist())
                if k.startswith("plan_"):
                    lw, ls = leads_of(act[wr][k], Y[k], g), leads_of(act[sr][k], Y[k], g)
                    if lw:
                        eg = np.array([e for e, _ in lw])
                        vw, vs = np.array([v for _, v in lw], float), np.array([v for _, v in ls], float)
                        ww = boot[:, eg]
                        dl = (ww @ vs - ww @ vw) / np.maximum(ww.sum(1), 1)
                        row.update(lead_W=float(vw.mean()), lead_S=float(vs.mean()), dlead=float(vs.mean() - vw.mean()),
                                   dlead_ci=np.quantile(dl, [.025, .975]).tolist())
                rows[k] = row
            out[f"{wr}|{sr}|L{L}"] = rows
            print(f"  L{L} {sr} - {wr}: {len(rows)} concepts", flush=True)
    TRES.mkdir(parents=True, exist_ok=True)
    (TRES / "paired.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    write_paired(out, counts)


def write_paired(out, counts):
    fams = ["pieces", "openings", "structures", "imbalances", "plans"]
    md = ["# S against W, paired on the same test games", "",
          "Each concept's chosen S unit against its chosen W unit (raw activations; and each model alone through the layer's "
          "crosscoder). dJ = J(S) - J(W), with a 95% bootstrap interval over test games, both scored on the same resampled "
          "games. S ahead / behind: the interval above / below 0. Plans: dlead = mean plies on before the first plan move, "
          "S - W.", "", "## Counts: S ahead / tied / behind, mean dJ", "",
          "| readout | layer | " + " | ".join(fams) + " |", "|---|---|" + "---|" * len(fams)]
    for key, rows in out.items():
        wr, sr, L = key.split("|")
        cells = []
        for f in fams:
            ks = [k for k in rows if counts[k]["family"] == f]
            if not ks:
                cells.append("")
                continue
            up = sum(rows[k]["dJ_ci"][0] > 0 for k in ks)
            dn = sum(rows[k]["dJ_ci"][1] < 0 for k in ks)
            cells.append(f"{up} / {len(ks) - up - dn} / {dn}, {np.mean([rows[k]['dJ'] for k in ks]):+.3f}")
        md.append(f"| {'raw' if wr == 'W' else 'through cc'} | {L} | " + " | ".join(cells) + " |")
    md += ["", "## Plans", ""]
    for key, rows in out.items():
        wr, sr, L = key.split("|")
        md += [f"### {'raw' if wr == 'W' else 'through cc'}, {L}", "",
               "| plan | test episodes | J W | J S | dJ [95%] | lead W | lead S | dlead [95%] |", "|---|--:|--:|--:|---|--:|--:|---|"]
        for k in sorted(k for k in rows if k.startswith("plan_")):
            r = rows[k]
            lead = (f"{r['lead_W']:.1f} | {r['lead_S']:.1f} | {r['dlead']:+.1f} [{r['dlead_ci'][0]:+.1f}, {r['dlead_ci'][1]:+.1f}]"
                    if "lead_W" in r else " | | ")
            md.append(f"| {k} | {counts[k]['test_episodes']} | {r['J_W']:.3f} | {r['J_S']:.3f} | {r['dJ']:+.3f} "
                      f"[{r['dJ_ci'][0]:+.3f}, {r['dJ_ci'][1]:+.3f}] | {lead} |")
        md.append("")
    (TRES / "paired.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"wrote {TRES / 'paired.md'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=("build", "acts", "score", "report", "paired"))
    ap.add_argument("--layers", default=",".join(LAYERS))
    ap.add_argument("--readouts", default="W,S,cc4096-Wview,cc4096-Sview")
    ap.add_argument("--concepts", default="")
    ap.add_argument("--games", type=int, default=0, help="build: only the first this many games (a test run)")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--max-tokens", type=int, default=40_000)
    ap.add_argument("--random-seed", type=int, default=0)
    a = ap.parse_args()
    {"build": build, "acts": acts, "score": run_score, "report": report, "paired": paired}[a.stage](a)


if __name__ == "__main__":
    main()
