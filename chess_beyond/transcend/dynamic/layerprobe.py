"""Where does a model carry its own future? At every layer, how much do its activations at a position say about the
moves it will play there next, beyond the board and the move it is about to play?

    python transcend/dynamic/layerprobe.py                     # GPU: futures and activations (cached), then the probes
    python transcend/dynamic/layerprobe.py --stage probe       # the probes alone
    python transcend/dynamic/layerprobe.py --model W           # the same for W

1. positions    --positions held-out middlegame positions, one per game (readings.py's choice and order: its 1,000 are
                the first 1,000 here). Split by game: 70% train, 10% validation, 20% test.
2. futures      the model's greedy continuation for --plies plies, the model writing both colours. m1: the move it
                plays at the position; m3, m5: the same side's next two moves, after the replies. Targets for each:
                from-square and to-square (64 classes), piece type (6). Events within the plies, by the side to move
                at the position (plies 1, 3, 5): it gives check; it captures.
3. activations  the residual stream after every block and after the final norm, at the token where the model
                predicts m1 (the prompt's end: the crosscoders' hook), float16, saved once.
4. probes       per layer and target, multinomial logistic regression (standardised inputs; L2 chosen by validation
                cross-entropy; full-batch L-BFGS). Baselines, trained the same way: board (one-hot pieces 12 x 64, side to
                move, castling rights, en passant file); board + next move (also one-hot from- and to-square of m1).
                Test cross-entropy (nats) and accuracy; gain(layer) = CE(baseline) - CE(layer), with 95% bootstrap
                intervals over test games.
5. report       per target, the gain over board + next move against the layer; a table of both gains; the layer where
                the m3 / m5 gain (summed over their six targets) peaks, and whether its interval against L15 and against
                the final layer (paired bootstrap of the difference) excludes zero.
6. persistence  every layer's state along each greedy line: the board-removed residual autocorrelation at lag --delta,
                against a random swap (chance floor), a board-matched swap (the nearest board from another game: the
                board control) and the raw board's own; the layer chosen by the rule in choose() (fixed before any
                result), stated in the report with its numbers.
Sanity checks: no game in two splits; the lines' root states equal the policy's hook; the m1 piece probe at the final layer at least the model's own confidence in m1
(its mean top-move probability). Not the to-square: the model writes a move character by character, and at this token it
commits only to the first character (the piece letter or a pawn's file); the squares come at the characters after, so the
to-square is only partly readable here (0.22 at the final layer, against 0.79 for the piece).

-> runs/transcend/layerprobe/<tag>/<model>.npz (futures), <model>-L<layer>.npy; results/transcend/layerprobe/<tag>/
   <model>-report.md, <model>-report.json, <model>-gains.png."""

import argparse
import json
import sys
import time
import zlib
from pathlib import Path

import chess
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # chess_beyond/
import paths  # noqa: E402  also puts transcend/'s folders on sys.path
import eval as ev
import readings as rd
import shared as gd
from pgn_model import MAX_MOVE_CHARS

RUNS = paths.RUNS / "transcend" / "layerprobe"
RESULTS = paths.ROOT / "results" / "transcend" / "layerprobe"
MOVES = ("m1", "m3", "m5")
PARTS = (("from", 64), ("to", 64), ("piece", 6))
TARGETS = [f"{m} {p}" for m in MOVES for p, _ in PARTS] + ["check", "capture"]
NCLASS = {**{f"{m} {p}": n for m in MOVES for p, n in PARTS}, "check": 2, "capture": 2}
PLAN = [t for t in TARGETS if t.startswith(("m3", "m5"))]
HIST = 6                                                              # plies of history in the third baseline
BASES = ("board", "board + next move", "board + next move + history")


def board_vec(b):
    v = np.zeros(12 * 64 + 1 + 4 + 8, np.float32)
    for sq, p in b.piece_map().items():
        v[(p.piece_type - 1 + 6 * (p.color == chess.BLACK)) * 64 + sq] = 1
    v[768] = b.turn == chess.WHITE
    v[769:773] = [b.has_kingside_castling_rights(chess.WHITE), b.has_queenside_castling_rights(chess.WHITE),
                  b.has_kingside_castling_rights(chess.BLACK), b.has_queenside_castling_rights(chess.BLACK)]
    if b.ep_square is not None and b.has_legal_en_passant():
        v[773 + chess.square_file(b.ep_square)] = 1
    return v


def hist_vec(stack, k=HIST):
    """The last k plies before a position, one-hot from- and to-square each (k x 128; most recent first)."""
    v = np.zeros(k * 128, np.uint8)
    for j, m in enumerate(reversed(stack[-k:])):
        v[j * 128 + m.from_square] = 1
        v[j * 128 + 64 + m.to_square] = 1
    return v


def line_hist(roots, moves, plies):
    """hist_vec at every ply of every greedy line (the game's moves before the position, then the line's own)."""
    out = np.zeros((len(roots), plies + 1, HIST * 128), np.uint8)
    for i, (r, mv) in enumerate(zip(roots, moves)):
        stack = list(ev.board_of(gd.parse_movetext(r["prompt"])[0]).move_stack)
        out[i, 0] = hist_vec(stack)
        for t, u in enumerate(mv, 1):
            stack.append(chess.Move.from_uci(u))
            out[i, t] = hist_vec(stack)
    return out


def split_of(r):
    """train / validation / test by game: 70 / 10 / 20."""
    h = zlib.crc32(f"{r['band']}/{r['game']}".encode()) % 10
    return 0 if h < 7 else 1 if h < 8 else 2


# ---------------------------------------------------------------- GPU: futures and activations
def play(a, run, layers):
    path = run / f"{a.model}.npz"
    if path.exists() and all((run / f"{a.model}-L{L}.npy").exists() and (run / f"{a.model}-lines-L{L}.npy").exists()
                             for L in layers):
        return
    dev = ev.device(a.device)
    cc = gd.load_cc(a.cc_run, a.cc, a.strong, dev)                     # which model is S; nothing else from it
    m = cc.s if a.model == "S" else cc.w
    model = ev.load(cc.info["models"][m], dev)[0]
    nb = len(model.blocks)
    if any(L != "final" and int(L) >= nb for L in layers):
        sys.exit(f"--layers beyond the model's {nb} blocks")
    rpath = run / "roots.json"
    if rpath.exists():
        roots = json.loads(rpath.read_text(encoding="utf-8"))
    else:
        P = rd.positions(argparse.Namespace(seed=a.seed, population=a.population, positions=a.positions), model.ctx)
        roots = [dict(prompt=r["prompt"], fen=b.fen(), band=r["band"], game=str(r["game"])) for r, b in P]
        rpath.write_text(json.dumps(roots), encoding="utf-8")
    print(f"{len(roots)} positions", flush=True)
    t0 = time.time()
    if path.exists() and all((run / f"{a.model}-L{L}.npy").exists() for L in layers):
        moves = json.loads(str(np.load(path)["moves"]))                # the futures are done: only the line states left
        print("futures and root activations cached", flush=True)
    else:
        moves = rollouts(a, run, path, roots, model, layers, dev)
    # every layer's state at every position of the greedy lines (ply 0: the root), for persistence
    seqs, ends, _, _, _, start = gd.positions(dict(roots=roots, lines=[dict(root=i, moves=mv) for i, mv in enumerate(moves)]))
    alive = np.load(path)["alive"]
    for L in layers:
        lp_ = run / f"{a.model}-lines-L{L}.npy"
        if lp_.exists():
            continue
        t1 = time.time()
        S_ = gd.line_states(model, seqs, ends, L, dev, a.max_tokens).numpy()
        out = np.zeros((len(roots), a.plies + 1, S_.shape[1]), np.float16)
        out[alive] = S_
        root = np.load(run / f"{a.model}-L{L}.npy").astype(np.float32)
        rel = np.linalg.norm(out[:, 0].astype(np.float32) - root, axis=1) / (np.linalg.norm(root, axis=1) + 1e-6)
        if np.median(rel) > 0.05:
            sys.exit(f"layer {L}: the lines' root states differ from the policy's (median relative difference "
                     f"{np.median(rel):.3f}): two hooks disagree, stopping")
        np.save(lp_, out)
        print(f"  line states, layer {L} ({time.time() - t1:.0f}s; ply 0 against the policy's hook: median relative "
              f"difference {np.median(rel):.4f}, max {rel.max():.4f})", flush=True)
    print(f"futures and activations: {(time.time() - t0) / 60:.1f} min", flush=True)


def rollouts(a, run, path, roots, model, layers, dev):
    """The greedy futures and every layer's root activations -> moves (saved, with each line's live plies)."""
    X = {L: [] for L in layers}
    moves, conf = [], []
    t0 = time.time()
    for c in range(0, len(roots), a.chunk):
        part = roots[c:c + a.chunk]
        L_ = [dict(board=ev.board_of(gd.parse_movetext(r["prompt"])[0]), moves=[], sans=[], prompt=r["prompt"]) for r in part]
        lg, lps, st = gd.policy(model, [l["board"] for l in L_], dev, [l["prompt"] for l in L_], grab=tuple(layers), batch=a.batch)
        for L in layers:
            X[L].append(st[L].numpy().astype(np.float16))
        for l, mv, p in zip(L_, lg, lps):
            conf.append(float(np.exp(p.max())))
            gd.advance(l, mv[int(np.argmax(p))])
        for ply in range(1, a.plies):
            go = [l for l in L_ if len(l["moves"]) == ply and not l["board"].is_game_over()
                  and len(l["prompt"]) + 2 * MAX_MOVE_CHARS + 4 <= model.ctx]
            if go:
                lg, lps, _ = gd.policy(model, [l["board"] for l in go], dev, [l["prompt"] for l in go], batch=a.batch)
                for l, mv, p in zip(go, lg, lps):
                    gd.advance(l, mv[int(np.argmax(p))])
        moves += [l["moves"] for l in L_]
        if c == 0:
            el = time.time() - t0
            print(f"timed {len(part)} positions: {el:.0f}s; projected total {el * len(roots) / len(part) / 60:.0f} min", flush=True)
    for L in layers:
        np.save(run / f"{a.model}-L{L}.npy", np.concatenate(X[L]))
    alive = np.zeros((len(roots), a.plies + 1), bool)
    for i, mv in enumerate(moves):
        alive[i, :len(mv) + 1] = True
    np.savez(path, moves=np.array(json.dumps(moves)), conf=np.array(conf), alive=alive)
    print(f"futures and root activations: {(time.time() - t0) / 60:.1f} min", flush=True)
    return moves


def targets(roots, moves):
    """Per position: each target's class (-1 where the line is too short), and the three baselines' inputs: board;
    board + next move; board + next move + the last HIST plies before the position."""
    Y = {t: np.full(len(roots), -1) for t in TARGETS}
    B, BM, BMH = [], [], []
    for i, (r, mv) in enumerate(zip(roots, moves)):
        b = chess.Board(r["fen"])
        bv = board_vec(b)
        B.append(bv)
        nm = np.zeros(128, np.float32)
        chk = cap = False
        for j, u in enumerate(mv):
            m = chess.Move.from_uci(u)
            if j % 2 == 0:                                             # the side to move at the position
                name = f"m{j + 1}"
                if name in MOVES:
                    Y[f"{name} from"][i], Y[f"{name} to"][i] = m.from_square, m.to_square
                    Y[f"{name} piece"][i] = b.piece_type_at(m.from_square) - 1
                cap |= b.is_capture(m)
                chk |= b.gives_check(m)
                if j == 0:
                    nm[m.from_square], nm[64 + m.to_square] = 1, 1
            b.push(m)
        Y["check"][i], Y["capture"][i] = int(chk), int(cap)
        BM.append(np.r_[bv, nm])
        BMH.append(np.r_[bv, nm, hist_vec(list(ev.board_of(gd.parse_movetext(r["prompt"])[0]).move_stack))])
    return Y, np.array(B), np.array(BM), np.array(BMH, np.float32)


# ---------------------------------------------------------------- probes
def probe(X, y, sp, ncls, dev, lams, iters):
    """Multinomial logistic regression on the rows with y >= 0, L2 by validation CE -> per-test-row CE (nats), correct."""
    ok = y >= 0
    tr, va, te = ok & (sp == 0), ok & (sp == 1), ok & (sp == 2)
    mu, sd = X[tr].mean(0), X[tr].std(0)
    inv = np.where(sd > 1e-6, 1 / np.maximum(sd, 1e-6), 0.0)          # a feature constant in train carries nothing
    T = lambda m: torch.tensor((X[m] - mu) * inv, dtype=torch.float32, device=dev)
    Yt = lambda m: torch.tensor(y[m], dtype=torch.long, device=dev)
    xtr, ytr, xva, yva, xte, yte = T(tr), Yt(tr), T(va), Yt(va), T(te), Yt(te)
    ce = torch.nn.functional.cross_entropy

    def fit(lam):
        W = torch.zeros(X.shape[1], ncls, device=dev, requires_grad=True)
        b = torch.zeros(ncls, device=dev, requires_grad=True)
        opt = torch.optim.LBFGS([W, b], lr=1, max_iter=iters, history_size=20, line_search_fn="strong_wolfe")

        def closure():
            opt.zero_grad()
            loss = ce(xtr @ W + b, ytr) + lam * (W ** 2).sum()
            loss.backward()
            return loss

        opt.step(closure)
        return W.detach(), b.detach()

    best = None
    for lam in lams:
        W, b = fit(lam)
        with torch.no_grad():
            v = float(ce(xva @ W + b, yva))
        if best is None or v < best[0]:
            best = (v, W, b, lam)
    _, W, b, lam = best
    with torch.no_grad():
        z = xte @ W + b
        c = ce(z, yte, reduction="none").cpu().numpy()
        hit = (z.argmax(1) == yte).float().cpu().numpy()
    out = np.full(len(y), np.nan)
    out[te] = c
    acc = np.full(len(y), np.nan)
    acc[te] = hit
    return out, acc, lam


def boot_ci(d, rng, n):
    """Mean of d and its 95% bootstrap interval (rows: test games, one position each)."""
    d = d[~np.isnan(d)]
    bs = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(n)])
    return float(d.mean()), float(np.quantile(bs, 0.025)), float(np.quantile(bs, 0.975))


def line_boards(roots, moves, plies):
    """The board vector at every ply of every greedy line -> (positions, plies + 1, features) uint8."""
    out = np.zeros((len(roots), plies + 1, len(board_vec(chess.Board()))), np.uint8)
    for i, (r, mv) in enumerate(zip(roots, moves)):
        b = chess.Board(r["fen"])
        out[i, 0] = board_vec(b)
        for t, u in enumerate(mv, 1):
            b.push(chess.Move.from_uci(u))
            out[i, t] = board_vec(b)
    return out


def residuals(X, Bd, alive, sp, ridge=1.0):
    """Each ply's state minus its ridge prediction from that ply's board (fit on the train positions), standardised per
    dimension (train statistics)."""
    tr = alive & (sp == 0)[:, None]
    Bt, Xt = Bd[tr].astype(np.float64), X[tr].astype(np.float64)
    bm, xm = Bt.mean(0), Xt.mean(0)
    W = np.linalg.solve((Bt - bm).T @ (Bt - bm) + ridge * np.eye(Bt.shape[1]), (Bt - bm).T @ (Xt - xm))
    E = np.zeros(X.shape, np.float32)
    E[alive] = X[alive] - xm - (Bd[alive] - bm) @ W
    sd = E[tr].std(0)
    return E * np.where(sd > 1e-6, 1 / np.maximum(sd, 1e-6), 0.0).astype(np.float32)


def partners(Bd, alive, sp, delta, rng, pool="all"):
    """For each test line and ply t, the state ply t + delta is compared with: its own line's (own); another test
    position's, at random (random, the chance floor); the test position (any line, any ply) from a different game whose
    board is nearest, in Hamming distance on the one-hot encoding, to the real ply t + delta board (matched, the board
    control), among the test positions (pool "test") or all (pool "all": many more candidates, so nearer boards).
    -> test positions, {name: {t: (positions, plies)}}, the matched boards' mean Hamming distance, and the own line's
    (ply t against ply t + delta) for comparison."""
    te = np.flatnonzero(sp == 2)
    cand = te if pool == "test" else np.arange(len(sp))
    ci, cs = np.nonzero(alive[cand])
    ci = cand[ci]
    C = Bd[ci, cs].astype(np.float32)
    cn = C.sum(1)
    perm = te[rng.permutation(len(te))]
    out = dict(own={}, random={}, matched={}, own_valid={}, matched_valid={})
    dist, own = [], []
    nv = np.zeros(len(te), int)
    for t in range(Bd.shape[1] - delta):
        out["own"][t] = (te, np.full(len(te), t + delta), None)
        out["random"][t] = (perm, np.full(len(te), t + delta), None)
        Q = Bd[te, t + delta].astype(np.float32)
        j = np.zeros(len(te), int)
        for s0 in range(0, len(te), 256):
            sc = 2 * Q[s0:s0 + 256] @ C.T - cn[None]                   # = |q| - Hamming distance; |q| fixed per row
            sc[te[s0:s0 + 256, None] == ci[None]] = -np.inf           # not the same game (one position per game)
            j[s0:s0 + 256] = sc.argmax(1)
        out["matched"][t] = (ci[j], cs[j], None)
        ok = alive[te, t + delta]
        dm = Q.sum(1) + cn[j] - 2 * (Q * C[j]).sum(1)
        do = np.abs(Bd[te, t].astype(int) - Bd[te, t + delta].astype(int)).sum(1)
        valid = ok & alive[te, t] & (dm <= do)                        # a stand-in at least as close as the line's own
        out["own_valid"][t] = (te, np.full(len(te), t + delta), valid)
        out["matched_valid"][t] = (ci[j], cs[j], valid)
        nv += valid
        dist.append(dm[ok])
        own.append(do[ok & alive[te, t]])
    return te, out, float(np.concatenate(dist).mean()), float(np.concatenate(own).mean()), nv


DIFFS = (("own", "random"), ("own", "matched"), ("own_valid", "matched_valid"))


def lag_stats(E, alive, te, Pt, rng, n_boot):
    """The correlation of E at (line, t) with E at each partner (only where its mask allows), pooled over dimensions
    and t; bootstrap over test lines -> {name: stat}, the 95% interval of own, and of each difference in DIFFS
    (key minus_<second>_ci)."""
    names = list(Pt)
    acc = {n: np.zeros((len(te), 3)) for n in names}
    for t in Pt["own"]:
        a_ = E[te, t]
        for n in names:
            pi, ps, mask = Pt[n][t]
            ok = alive[te, t] & alive[pi, ps] & (True if mask is None else mask)
            b_ = E[pi, ps]
            acc[n] += ok[:, None] * np.c_[(a_ * b_).sum(1), (a_ * a_).sum(1), (b_ * b_).sum(1)]
    r = lambda A: A[:, 0].sum() / np.sqrt(max(A[:, 1].sum() * A[:, 2].sum(), 1e-12))
    out = {n: float(r(acc[n])) for n in names}
    bs = {"own": [], **{b: [] for _, b in DIFFS}}
    for _ in range(n_boot):
        idx = rng.integers(0, len(te), len(te))
        bs["own"].append(r(acc["own"][idx]))
        for x, y in DIFFS:
            bs[y].append(r(acc[x][idx]) - r(acc[y][idx]))
    out["own_ci"] = (float(np.quantile(bs["own"], .025)), float(np.quantile(bs["own"], .975)))
    for _, y in DIFFS:
        out[f"minus_{y}_ci"] = (float(np.quantile(bs[y], .025)), float(np.quantile(bs[y], .975)))
    return out


def mlp_residuals(X, F, alive, sp, dev, hidden=512, steps=3000, batch=1024):
    """Each ply's state (standardised) minus a small MLP's prediction of it from that ply's board and history (fit on
    the train positions, early-stopped on validation), standardised per dimension -> residuals, validation R^2 of the
    MLP and of a linear (ridge) map from the same inputs."""
    tr, va = alive & (sp == 0)[:, None], alive & (sp == 1)[:, None]
    xm, xs = X[tr].mean(0), X[tr].std(0) + 1e-6
    fm, fs = F[tr].mean(0), F[tr].std(0)
    finv = np.where(fs > 1e-6, 1 / np.maximum(fs, 1e-6), 0.0).astype(np.float32)
    T = lambda A: torch.tensor(A, dtype=torch.float32, device=dev)
    xtr, ftr = T((X[tr] - xm) / xs), T((F[tr] - fm) * finv)
    xva, fva = T((X[va] - xm) / xs), T((F[va] - fm) * finv)
    torch.manual_seed(0)
    net = torch.nn.Sequential(torch.nn.Linear(F.shape[-1], hidden), torch.nn.ReLU(), torch.nn.Linear(hidden, hidden),
                              torch.nn.ReLU(), torch.nn.Linear(hidden, X.shape[-1])).to(dev)
    opt = torch.optim.Adam(net.parameters(), lr=1e-3, weight_decay=1e-4)
    g = torch.Generator(device="cpu").manual_seed(0)
    best = (float("inf"), None)
    for step in range(steps):
        idx = torch.randint(0, len(xtr), (batch,), generator=g).to(dev)
        opt.zero_grad()
        torch.nn.functional.mse_loss(net(ftr[idx]), xtr[idx]).backward()
        opt.step()
        if step % 100 == 99:
            with torch.no_grad():
                v = float(torch.nn.functional.mse_loss(net(fva), xva))
            if v < best[0]:
                best = (v, {k: w.clone() for k, w in net.state_dict().items()})
    net.load_state_dict(best[1])
    with torch.no_grad():
        r2_mlp = 1 - best[0] / float(xva.var(0, unbiased=False).mean())
        A = torch.cat([ftr, torch.ones(len(ftr), 1, device=dev)], 1)
        W = torch.linalg.solve(A.T @ A + torch.eye(A.shape[1], device=dev), A.T @ xtr)
        r2_lin = 1 - float(torch.nn.functional.mse_loss(torch.cat([fva, torch.ones(len(fva), 1, device=dev)], 1) @ W, xva)) \
            / float(xva.var(0, unbiased=False).mean())
        E = np.zeros(X.shape, np.float32)
        rows = np.flatnonzero(alive.ravel())
        Xf, Ff = X.reshape(-1, X.shape[-1]), F.reshape(-1, F.shape[-1])
        out = []
        for s0 in range(0, len(rows), 8192):
            rr = rows[s0:s0 + 8192]
            out.append(((Xf[rr] - xm) / xs - net(T((Ff[rr] - fm) * finv)).cpu().numpy()).astype(np.float32))
        E.reshape(-1, X.shape[-1])[rows] = np.concatenate(out)
    sd = E[tr].std(0)
    return E * np.where(sd > 1e-6, 1 / np.maximum(sd, 1e-6), 0.0).astype(np.float32), float(r2_mlp), float(r2_lin)


MIN_VALID = 200                                                       # test lines with a valid match, for that control


def choose2(Ls, P2, n_valid):
    """The corrected rule (fixed before its results): residuals after an MLP on the board and the last 6 plies; a layer
    passes if its own-line autocorrelation is significantly above the board-matched swap restricted to valid matches
    (stand-ins at least as close to the real ply t + delta board as the line's own ply t board; the 95% interval of
    own - matched above zero, over the same pairs), or, if fewer than MIN_VALID test lines have a valid match, above
    the random swap; and at least half the maximum over layers. The latest passing layer is chosen."""
    basis = "matched_valid" if n_valid >= MIN_VALID else "random"
    mx = max(P2[L]["own"] for L in Ls)
    ok = [L for L in Ls if P2[L][f"minus_{basis}_ci"][0] > 0 and P2[L]["own"] >= 0.5 * mx]
    why = [f"Test lines with at least one valid board match: {n_valid} (need {MIN_VALID}); the control used: "
           + ("the valid board-matched swap." if basis == "matched_valid" else "the random swap (too few valid matches)."),
           f"Maximum autocorrelation over layers {mx:.3f}; half of it {0.5 * mx:.3f}.",
           "Passing: " + (", ".join(ok) if ok else "none") + "."]
    if not ok:
        return None, why + ["No layer passes: no choice."], basis
    return ok[-1], why + [f"Chosen: {ok[-1]}, the latest passing layer."], basis


def passes(P, L, mx):
    return P[L]["minus_matched_ci"][0] > 0 and P[L]["own"] >= 0.5 * mx


def choose(Ls, P):
    """The rule, fixed before the results: a layer passes if its residual autocorrelation is significantly above the
    board-matched swap (the 95% interval of own - matched above zero) and at least half the maximum over layers; the
    latest passing layer is chosen. -> layer (None if none passes), the reasoning as lines."""
    mx = max(P[L]["own"] for L in Ls)
    ok = [L for L in Ls if passes(P, L, mx)]
    why = [f"Maximum residual autocorrelation over layers {mx:.3f}; half of it {0.5 * mx:.3f}.",
           "Above the board-matched swap: " + (", ".join(L for L in Ls if P[L]["minus_matched_ci"][0] > 0) or "none") + ".",
           "Passing (both): " + (", ".join(ok) if ok else "none") + "."]
    if not ok:
        return None, why + ["No layer passes: no choice."]
    return ok[-1], why + [f"Chosen: {ok[-1]}, the latest passing layer."]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=("all", "probe"), default="all")
    ap.add_argument("--model", choices=("S", "W"), default="S")
    ap.add_argument("--cc-run", default="runs/transcend/crosscoder/everything-3m", help="only for which model is S")
    ap.add_argument("--cc", default="Lfinal")
    ap.add_argument("--strong", default="2400")
    ap.add_argument("--population", default=str(gd.PROBE / "population.jsonl"))
    ap.add_argument("--positions", type=int, default=5000)
    ap.add_argument("--plies", type=int, default=6)
    ap.add_argument("--layers", default="0-15,final", help="blocks (ranges allowed) and final (the final norm)")
    ap.add_argument("--lams", default="1e-5,1e-4,1e-3,1e-2,1e-1", help="L2 strengths tried on the validation split")
    ap.add_argument("--iters", type=int, default=200, help="L-BFGS iterations per fit")
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--delta", type=int, default=4, help="the persistence lag (plies)")
    ap.add_argument("--match-pool", choices=("all", "test"), default="all", help="where the board-matched stand-ins come from")
    ap.add_argument("--max-tokens", type=int, default=40_000, help="characters per forward pass for the line states (VRAM)")
    ap.add_argument("--chunk", type=int, default=200, help="positions per batch of rollouts (the first is timed)")
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    a.tag = a.tag or f"n{a.positions}-p{a.plies}-s{a.seed}"
    layers = []
    for part in a.layers.split(","):
        layers += ["final"] if part == "final" else [str(i) for i in range(int(part.split("-")[0]), int(part.split("-")[-1]) + 1)]
    run, res = RUNS / a.tag, RESULTS / a.tag
    run.mkdir(parents=True, exist_ok=True)
    res.mkdir(parents=True, exist_ok=True)
    if a.stage == "all":
        play(a, run, layers)
    dev = ev.device(a.device)
    roots = json.loads((run / "roots.json").read_text(encoding="utf-8"))
    z = np.load(run / f"{a.model}.npz")
    moves, conf = json.loads(str(z["moves"])), z["conf"]
    sp = np.array([split_of(r) for r in roots])
    games = {}
    for r, s in zip(roots, sp):
        games.setdefault((r["band"], r["game"]), set()).add(int(s))
    if any(len(v) > 1 for v in games.values()):
        sys.exit("a game in more than one split: stopping")
    print(f"{a.model}: {len(roots)} positions from {len(games)} games; train / validation / test "
          f"{(sp == 0).sum()} / {(sp == 1).sum()} / {(sp == 2).sum()}; no game in two splits", flush=True)
    Y, B, BM, BMH = targets(roots, moves)
    lams = [float(x) for x in a.lams.split(",")]
    rng = np.random.default_rng(a.seed)
    CE, ACC = {}, {}
    t0 = time.time()
    inputs = [("board", lambda: B), ("board + next move", lambda: BM), ("board + next move + history", lambda: BMH)] + \
             [(f"L{L}", lambda L=L: np.load(run / f"{a.model}-L{L}.npy").astype(np.float32)) for L in layers]
    for name, get in inputs:
        X = get()
        if len(X) != len(roots):
            sys.exit(f"{name}: {len(X)} rows for {len(roots)} positions")
        t1 = time.time()
        cache = run / f"probes-{a.model}" / f"{name.replace(' ', '_').replace('+', 'plus')}.npz"
        if cache.exists():
            c = np.load(cache)
            CE[name] = {t: c[f"ce {t}"] for t in TARGETS}
            ACC[name] = {t: c[f"acc {t}"] for t in TARGETS}
        else:
            CE[name], ACC[name] = {}, {}
            for t in TARGETS:
                CE[name][t], ACC[name][t], _ = probe(X, Y[t], sp, NCLASS[t], dev, lams, a.iters)
            cache.parent.mkdir(exist_ok=True)
            np.savez(cache, **{f"ce {t}": CE[name][t] for t in TARGETS}, **{f"acc {t}": ACC[name][t] for t in TARGETS})
        print(f"  {name}: m1 to {np.nanmean(ACC[name]['m1 to']):.3f}, m3 to {np.nanmean(ACC[name]['m3 to']):.3f}, "
              f"m5 to {np.nanmean(ACC[name]['m5 to']):.3f} (accuracy; {time.time() - t1:.0f}s)", flush=True)
        if name == "Lfinal":
            # the model writes a move character by character: at this token it commits only to the first (the piece
            # letter, or a pawn's file), the squares come at the characters after. So the check is on m1's piece
            got, want = np.nanmean(ACC[name]["m1 piece"]), float(conf[sp == 2].mean())
            print(f"  sanity: the m1 piece probe at the final layer {got:.3f}; the model's own mean top-move probability "
                  f"{want:.3f}", flush=True)
            if got < want:
                sys.exit("the final layer's m1 piece probe is below the model's confidence in its whole move: wrong hook? stopping")
    Bd = line_boards(roots, moves, a.plies)
    alive = z["alive"]
    te, Pt, hd, hown, nv = partners(Bd, alive, sp, a.delta, rng, a.match_pool)
    n_valid = int((nv > 0).sum())
    print(f"  board matches at least as close as the line's own ply t board: {n_valid} of {len(te)} test lines, "
          f"{int(nv.sum())} pairs", flush=True)
    tr = alive & (sp == 0)[:, None]
    bsd = Bd[tr].std(0)
    Eb = ((Bd.astype(np.float32) - Bd[tr].mean(0)) * np.where(bsd > 1e-6, 1 / np.maximum(bsd, 1e-6), 0.0)) * alive[..., None]
    P = {"board": lag_stats(Eb, alive, te, Pt, rng, a.boot)}           # the raw board's own persistence (reference)
    print(f"  persistence, the raw board: {P['board']['own']:.3f} (board-matched swap {P['board']['matched']:.3f}; matched "
          f"boards {hd:.1f} one-hot entries from the real one, against {hown:.1f} between a line's ply t and t + {a.delta})", flush=True)
    for L in layers:
        t1 = time.time()
        E = residuals(np.load(run / f"{a.model}-lines-L{L}.npy").astype(np.float32), Bd, alive, sp)
        P[f"L{L}"] = lag_stats(E, alive, te, Pt, rng, a.boot)
        print(f"  persistence L{L}: {P[f'L{L}']['own']:.3f} (random swap {P[f'L{L}']['random']:.3f}, board-matched "
              f"{P[f'L{L}']['matched']:.3f}; {time.time() - t1:.0f}s)", flush=True)
    # the corrected control: the board and the last HIST plies removed by an MLP, against the valid board matches
    F = np.concatenate([Bd, line_hist(roots, moves, a.plies)], -1).astype(np.float32)
    P2, R2 = {}, {}
    for L in layers:
        t1 = time.time()
        E, r2m, r2l = mlp_residuals(np.load(run / f"{a.model}-lines-L{L}.npy").astype(np.float32), F, alive, sp, dev)
        P2[f"L{L}"], R2[f"L{L}"] = lag_stats(E, alive, te, Pt, rng, a.boot), (r2m, r2l)
        q = P2[f"L{L}"]
        print(f"  persistence after the MLP, L{L}: {q['own']:.3f} (random swap {q['random']:.3f}; valid board-matched: own "
              f"{q['own_valid']:.3f}, matched {q['matched_valid']:.3f}; validation R^2 MLP {r2m:.3f}, linear {r2l:.3f}; "
              f"{time.time() - t1:.0f}s)", flush=True)
    write(a, res, layers, CE, ACC, rng, P, (hd, hown), P2, R2, n_valid)
    print(f"wrote {res / f'{a.model}-report.md'} ({(time.time() - t0) / 60:.1f} min of probes)")


def write(a, res, layers, CE, ACC, rng, P, hds, P2, R2, n_valid):
    hd, hown = hds
    Ls = [f"L{L}" for L in layers]
    G = {}                                                             # (baseline, layer, target) -> mean, lo, hi
    for base in BASES:
        for L in Ls:
            for t in TARGETS:
                G[base, L, t] = boot_ci(CE[base][t] - CE[L][t], rng, a.boot)
    valid = ~np.isnan(np.sum([CE[Ls[0]][t] for t in PLAN], 0))        # test rows with every m3 / m5 target
    plan = {L: np.where(valid, np.sum([CE["board + next move"][t] - CE[L][t] for t in PLAN], 0), np.nan) for L in Ls}
    pg = {L: boot_ci(plan[L], rng, a.boot) for L in Ls}
    peak = max(Ls, key=lambda L: pg[L][0])
    pick, why = choose(Ls, P)
    mx = max(P[L]["own"] for L in Ls)
    pick2, why2, basis = choose2(Ls, P2, n_valid)
    mx2 = max(P2[L]["own"] for L in Ls)
    HB = "board + next move + history"
    plan_h = {L: np.where(valid, np.sum([CE[HB][t] - CE[L][t] for t in PLAN], 0), np.nan) for L in Ls}
    pgh = {L: boot_ci(plan_h[L], rng, a.boot) for L in Ls}
    peak_h = max(Ls, key=lambda L: pgh[L][0])
    out = [f"# {a.model}: how much each layer says about its own future moves", "",
           f"{a.positions} positions; {a.model}'s greedy continuation for {a.plies} plies (both colours); targets: from-square, "
           "to-square and piece of m1 (its move here), m3 and m5 (its next two), and check / capture by the side to move "
           "within the plies. Multinomial logistic probes from the activations at the position (the token predicting m1), "
           "L2 by validation; test cross-entropy in nats. gain = CE(baseline) - CE(layer), 95% bootstrap intervals over test "
           "games. Baselines: board; board + next move (m1's from- and to-square added); board + next move + history (also "
           f"the last {HIST} plies before the position, one-hot from- and to-square each: the prompt is the whole game, and "
           "recent moves predict later ones).", "",
           f"## The chosen layer, corrected control: {pick2}", "",
           f"The first rule (below) used a board-matched swap that could not discriminate: its stand-ins were {hd:.1f} one-hot "
           f"entries from the real board, further than a line's own board {a.delta} plies earlier ({hown:.1f}), and every layer "
           "passed it. Corrected rule, fixed before its results: residuals after a small MLP (two hidden layers of 512) on "
           f"the board and the last {HIST} plies at the same ply, so neither nonlinear board information nor recent history "
           f"stays in them; a layer passes if its own-line autocorrelation at lag {a.delta} is significantly above the "
           "board-matched swap counted only where the stand-in is at least as close to the real board as the line's own "
           f"earlier board (or above the random swap if fewer than {MIN_VALID} test lines have such a match), and at least "
           "half the maximum over layers. The latest passing layer is chosen.", ""]
    out += [f"- {w}" for w in why2]
    out += ["", "| layer | own | 95% | random swap | own (valid pairs) | valid board-matched | own - matched (valid), 95% | "
            "passes | MLP R^2 (linear) | m3 + m5 gain over board + next move + history |", "|---|---|---|---|---|---|---|---|---|---|"]
    for L in Ls:
        q = P2[L]
        ok = q[f"minus_{basis}_ci"][0] > 0 and q["own"] >= 0.5 * mx2
        out.append(f"| {L} | {q['own']:.3f} | [{q['own_ci'][0]:.3f}, {q['own_ci'][1]:.3f}] | {q['random']:.3f} | "
                   f"{q['own_valid']:.3f} | {q['matched_valid']:.3f} | [{q['minus_matched_valid_ci'][0]:+.3f}, "
                   f"{q['minus_matched_valid_ci'][1]:+.3f}] | {'yes' if ok else 'no'} | {R2[L][0]:.3f} ({R2[L][1]:.3f}) | "
                   f"{pgh[L][0]:+.4f} [{pgh[L][1]:+.4f}, {pgh[L][2]:+.4f}] |")
    out += ["", f"## The plan signal against the history baseline: m3 and m5 (six targets summed), gain over {HB}", "",
            f"Peak: {peak_h}."]
    for ref in ("L0", "L15", "Lfinal"):
        if ref in Ls and ref != peak_h:
            d = boot_ci(plan_h[peak_h] - plan_h[ref], rng, a.boot)
            out.append(f"{peak_h} minus {ref}: {d[0]:+.4f} nats [{d[1]:+.4f}, {d[2]:+.4f}]: the interval "
                       + ("excludes zero." if d[1] > 0 or d[2] < 0 else "includes zero."))
    out += ["", "Absolute effects are small: the probes are far from reading off a plan (see the accuracies in the tables "
            "below); they serve to rank layers.", "",
            f"## The first rule's choice: {pick}", "",
           f"Rule (fixed before the results): a layer passes if its board-removed residual autocorrelation at lag {a.delta} is "
           "significantly above the board-matched swap (the 95% bootstrap interval over test lines of own - matched above "
           "zero) and at least half the maximum over layers. The latest passing layer is chosen.", ""]
    out += [f"- {w}" for w in why]
    out += ["", f"Persistence: residual = the state minus its ridge prediction from the board at the same ply (fit on the "
            f"train positions), standardised per dimension; the correlation of the residual at ply t with ply t + {a.delta} "
            f"of the same greedy line (own), pooled over dimensions and t, on test lines. Against three levels: random swap "
            f"(ply t + {a.delta} from a random other test position: the chance floor); board-matched swap (the state at the "
            f"position (pool: {a.match_pool}), from a different game, whose board is nearest to the real ply t + {a.delta} board: "
            f"on average {hd:.1f} one-hot entries apart, against {hown:.1f} between a line's own plies t and t + {a.delta}; the board control, since the residual keeps any nonlinear board information, "
            "which persists as slowly as the board does); and the raw board's own autocorrelation (the same statistic on "
            f"the standardised one-hot board): {P['board']['own']:.3f}, board-matched {P['board']['matched']:.3f}. Caveat: the "
            "prompt is the whole game, so a residual also carries the game's history, which persists along a line whatever "
            "the model plans; the board-matched swap comes from another game and does not remove that.", "",
            "| layer | own | 95% | random swap | board-matched swap | own - matched, 95% | passes | m3 + m5 gain (nats) |",
            "|---|---|---|---|---|---|---|---|"]
    out += [f"| {L} | {P[L]['own']:.3f} | [{P[L]['own_ci'][0]:.3f}, {P[L]['own_ci'][1]:.3f}] | {P[L]['random']:.3f} | "
            f"{P[L]['matched']:.3f} | [{P[L]['minus_matched_ci'][0]:+.3f}, {P[L]['minus_matched_ci'][1]:+.3f}] | "
            f"{'yes' if passes(P, L, mx) else 'no'} | {pg[L][0]:+.4f} |" for L in Ls]
    out += ["", "## The plan signal: m3 and m5 (six targets summed), gain over board + next move", "",
            "| layer | gain (nats) | 95% |", "|---|---|---|"]
    out += [f"| {L} | {pg[L][0]:+.4f} | [{pg[L][1]:+.4f}, {pg[L][2]:+.4f}] |" for L in Ls]
    out += ["", f"Peak: {peak}."]
    for ref in ("L15", "Lfinal"):
        if ref == peak:
            out.append(f"The peak is {ref} itself.")
        elif ref in Ls:
            d = boot_ci(plan[peak] - plan[ref], rng, a.boot)
            out.append(f"{peak} minus {ref}: {d[0]:+.4f} nats [{d[1]:+.4f}, {d[2]:+.4f}], paired over test games: "
                       + ("the interval excludes zero." if d[1] > 0 or d[2] < 0 else "the interval includes zero."))
    out.append("")
    for base in (HB, "board + next move", "board"):
        out += [f"## Gain over {base} (nats; the layer's accuracy in brackets)", "",
                "| layer | " + " | ".join(TARGETS) + " |", "|---|" + "---|" * len(TARGETS)]
        for L in Ls:
            out.append(f"| {L} | " + " | ".join(f"{G[base, L, t][0]:+.3f} ({np.nanmean(ACC[L][t]):.2f})" for t in TARGETS) + " |")
        out.append(f"| {base} itself: CE (accuracy) | " + " | ".join(f"{np.nanmean(CE[base][t]):.3f} ({np.nanmean(ACC[base][t]):.2f})"
                                                                     for t in TARGETS) + " |")
        out.append("")
    (res / f"{a.model}-report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    (res / f"{a.model}-report.json").write_text(json.dumps(dict(
        gains={f"{b} | {L} | {t}": v for (b, L, t), v in G.items()}, plan=pg, peak=peak, chosen=pick, why=why,
        persistence=P, matched_hamming=hd, own_hamming=hown, chosen_corrected=pick2, why_corrected=why2,
        persistence_mlp=P2, mlp_r2=R2, valid_match_lines=n_valid, plan_history=pgh, peak_history=peak_h,
        accuracy={n: {t: float(np.nanmean(v)) for t, v in r.items()} for n, r in ACC.items()},
        ce={n: {t: float(np.nanmean(v)) for t, v in r.items()} for n, r in CE.items()}), indent=1), encoding="utf-8")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(3, 4, figsize=(18, 11))
    x = np.arange(len(Ls))
    for p, t in zip(ax.flat, TARGETS + ["plan"]):
        for base, col, src in (("board + next move", "C0", pg), (HB, "C1", pgh)):
            v = [src[L] if t == "plan" else G[base, L, t] for L in Ls]
            p.fill_between(x, [u[1] for u in v], [u[2] for u in v], alpha=0.2, color=col)
            p.plot(x, [u[0] for u in v], "o-", color=col, label=f"over {base}")
        p.legend(fontsize=6)
        p.axhline(0, color="0.5", lw=0.8)
        p.set_xticks(x, [L[1:] for L in Ls], fontsize=7)
        p.set_title("m3 + m5, six targets summed" if t == "plan" else t, fontsize=10)
        p.set_xlabel("layer")
        p.set_ylabel("gain (nats)")
    fig.suptitle(f"{a.model}: gain over board + next move (blue) and over board + next move + history (orange), 95% intervals")
    fig.tight_layout()
    fig.savefig(res / f"{a.model}-gains.png", dpi=110)
    plt.close(fig)


if __name__ == "__main__":
    main()
