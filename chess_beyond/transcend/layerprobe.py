"""Where does the future live? At every layer of each model, how well does the state at one position of a line predict
what happens a few plies later on that line, against a probe that sees only the board?

    python transcend/layerprobe.py                     # GPU: lines, every layer's states, the final-layer codes; probes
    python transcend/layerprobe.py --stage probe       # the probes alone, on cached states

Lines: --positions held-out middlegame positions (readings.py's choice: one per game, seeded order; its 1,000 are the
first 1,000 here), from each --lines rollouts of --plies plies by each model at --T, the model writing both colours'
moves. A probe needs many different positions to learn anything general (from 25 it barely beats chance even from the
board), so: many positions, few short lines each. Each model's states on its own lines.

Per layer (every block, and the final norm) and k in --ks, from the state at position t of a line (t = 0: the root) to
ply t + k of the same line:
  square   the destination square of the move played at ply t + k (64 classes; k = 1 is the next move, which the policy
           itself decides; k >= 2 is look-ahead, as in Jenner et al. 2024); top-1 accuracy
  events   whether the move at ply t + k gives check, captures, pushes a pawn, promotes, castles; mean AUC
  latents  the final-layer crosscoder's --latents most frequent latents (on at 2-50% of positions) at ply t + k, the
           pair (this model's state, the other model's) on this line encoded; mean AUC. Later layers are closer to
           these by construction, so read this one against the others.
Baseline: the same probe from the board at t alone (pieces on squares, side to move, castling rights): whatever a layer
adds over it is information about the future beyond what is linearly readable from the position.
Probes: linear, softmax / logistic, inputs standardised, weight decay picked on a validation fifth of the fit positions.
Fit on half the positions, scored on the other half (by game); +- one bootstrap SE over the held-out positions.

-> runs/transcend/layerprobe/<tag>/ (lines, states, codes); results/transcend/layerprobe/<tag>/report.md, report.json,
   layers.png, rewritten after every layer."""

import argparse
import json
import sys
import time
import zlib
from pathlib import Path

import chess
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paths
import eval as ev
import readings as rd
import recurring as rc
import shared as gd
from pgn_model import MAX_MOVE_CHARS

RUNS = paths.RUNS / "transcend" / "layerprobe"
RESULTS = paths.ROOT / "results" / "transcend" / "layerprobe"
EVENTS = ["gives check", "capture", "pawn push", "promotion", "castles"]
TARGETS = ("square", "events", "latents")


def board_vec(b):
    v = np.zeros(12 * 64 + 5, np.uint8)
    for sq, p in b.piece_map().items():
        v[(p.piece_type - 1 + 6 * (p.color == chess.BLACK)) * 64 + sq] = 1
    v[768] = b.turn == chess.WHITE
    v[769:773] = [b.has_kingside_castling_rights(chess.WHITE), b.has_queenside_castling_rights(chess.WHITE),
                  b.has_kingside_castling_rights(chess.BLACK), b.has_queenside_castling_rights(chess.BLACK)]
    return v


# ---------------------------------------------------------------- GPU: lines, states, codes
def play(a, run):
    dev = ev.device(a.device)
    cc = gd.load_cc(a.cc_run, a.cc, a.strong, dev)
    models = {m: ev.load(cc.info["models"][m], dev)[0] for m in (0, 1)}
    layers = [str(i) for i in range(len(models[0].blocks))] + ["final"]
    (run / "layers.json").write_text(json.dumps(layers))
    ctx = min(m.ctx for m in models.values())
    rpath = run / "roots.json"
    if rpath.exists():
        roots = json.loads(rpath.read_text(encoding="utf-8"))
    else:
        P = rd.positions(argparse.Namespace(seed=a.seed, population=a.population, positions=a.positions), ctx)
        roots = [dict(prompt=r["prompt"], fen=b.fen(), band=r["band"], game=str(r["game"])) for r, b in P]
        rpath.write_text(json.dumps(roots), encoding="utf-8")
    print(f"{len(roots)} positions", flush=True)
    for who, m in (("S", cc.s), ("W", cc.w)):
        lpath = run / f"lines-{who}.json"
        if not lpath.exists():
            rng = np.random.default_rng(zlib.crc32(f"{a.seed}/{who}".encode()))
            L = [dict(board=ev.board_of(gd.parse_movetext(r["prompt"])[0]), moves=[], sans=[], prompt=r["prompt"], root=i)
                 for i, r in enumerate(roots) for _ in range(a.lines)]
            t0 = time.time()
            for ply in range(a.plies):
                go = [l for l in L if len(l["moves"]) == ply and not l["board"].is_game_over()
                      and len(l["prompt"]) + 2 * MAX_MOVE_CHARS + 4 <= ctx]
                if not go:
                    break
                lg, lps, _ = gd.policy(models[m], [l["board"] for l in go], dev, [l["prompt"] for l in go], batch=a.batch)
                for l, mv, p in zip(go, lg, lps):
                    gd.advance(l, mv[gd.sample(p, a.T, rng)])
                el = time.time() - t0
                print(f"  {who} ply {ply + 1}/{a.plies}: {len(go)} lines ({el:.0f}s"
                      + (f"; projected for {who}'s lines: {el * a.plies / 60:.0f} min)" if ply == 0 else ")"), flush=True)
            lpath.write_text(json.dumps([dict(root=l["root"], moves=l["moves"]) for l in L]), encoding="utf-8")
        lines = json.loads(lpath.read_text(encoding="utf-8"))
        seqs, ends, _, _, _, _ = gd.positions(dict(roots=roots, lines=lines))
        for L_ in layers:
            path = run / f"{who}-L{L_}.npy"
            if not path.exists():
                t0 = time.time()
                np.save(path, gd.line_states(models[m], seqs, ends, L_, dev, a.max_tokens).numpy())
                print(f"  {who} layer {L_} states ({time.time() - t0:.0f}s)", flush=True)
        cpath = run / f"codes-{who}.npz"
        if not cpath.exists():
            st = {mm: (np.load(run / f"{who}-L{cc.layer[mm]}.npy") if mm == m else
                       gd.line_states(models[mm], seqs, ends, cc.layer[mm], dev, a.max_tokens).numpy()) for mm in (0, 1)}
            rows, cols = [], []
            with torch.no_grad():
                for i in range(0, len(st[0]), 4096):
                    f, _ = gd.encode_states(cc, {mm: torch.from_numpy(st[mm][i:i + 4096]).to(dev) for mm in (0, 1)})
                    nz = (f > 0).nonzero().cpu().numpy()
                    rows.append(nz[:, 0] + i)
                    cols.append(nz[:, 1])
            np.savez_compressed(cpath, rows=np.concatenate(rows), cols=np.concatenate(cols), n=len(st[0]), nlat=cc.ck["latents"])
            print(f"  {who}: final-layer codes", flush=True)


# ---------------------------------------------------------------- the examples and probes
def examples(a, run, who, roots):
    """Per (line, position t), in the order gd.positions lists the states: the board, the move played to reach t, the
    events of that move, the latents on there -> dict of arrays."""
    from scipy import sparse
    lines = json.loads((run / f"lines-{who}.json").read_text(encoding="utf-8"))
    c = np.load(run / f"codes-{who}.npz")
    Z = sparse.csr_matrix((np.ones(len(c["rows"]), bool), (c["rows"], c["cols"])), shape=(int(c["n"]), int(c["nlat"])))
    E = dict(pos=[], t=[], n=[], board=[], to=[], ev=[])
    ev_i = [rc.FACTS.index(e) for e in EVENTS]
    for l in lines:
        r, mv = roots[l["root"]], l["moves"]
        F = rc.line_facts(r["fen"], mv, max(a.plies, len(mv)))
        b = chess.Board(r["fen"])
        for t in range(len(mv) + 1):
            E["pos"].append(l["root"])
            E["t"].append(t)
            E["n"].append(len(mv))
            E["board"].append(board_vec(b))
            E["to"].append(chess.Move.from_uci(mv[t - 1]).to_square if t else -1)
            E["ev"].append(np.nan_to_num(F[t, ev_i]) > 0 if t else np.zeros(len(EVENTS), bool))
            if t < len(mv):
                b.push(chess.Move.from_uci(mv[t]))
    E = {k: np.array(v) for k, v in E.items()}
    if Z.shape[0] != len(E["t"]):
        sys.exit(f"{who}: {Z.shape[0]} code rows for {len(E['t'])} states")
    rate = np.asarray(Z[E["t"] > 0].mean(0)).ravel()
    ok = np.flatnonzero((rate >= 0.02) & (rate <= 0.5))
    E["lat_ids"] = ok[np.argsort(-rate[ok])][:a.latents]
    E["lat"] = Z[:, E["lat_ids"]].toarray()
    return E


def fit_probe(Xtr, Ytr, gtr, Xte, kind, dev, steps):
    """A linear probe (kind: 'ce' with integer Y, or 'bce' with a 0/1 matrix), weight decay chosen on a validation fifth
    of the fit positions -> scores on Xte (logits)."""
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-4
    T = lambda X: torch.tensor((X - mu) / sd, dtype=torch.float32, device=dev)
    xtr, xte = T(Xtr), T(Xte)
    ytr = torch.tensor(Ytr, device=dev, dtype=torch.long if kind == "ce" else torch.float32)
    out_dim = 64 if kind == "ce" else Ytr.shape[1]
    loss_fn = torch.nn.functional.cross_entropy if kind == "ce" else torch.nn.functional.binary_cross_entropy_with_logits
    ug = np.unique(gtr)
    val = torch.tensor(np.isin(gtr, ug[np.random.default_rng(0).permutation(len(ug))[:max(1, len(ug) // 5)]]), device=dev)

    def train(x, y, wd):
        torch.manual_seed(0)
        lin = torch.nn.Linear(x.shape[1], out_dim).to(dev)
        opt = torch.optim.Adam(lin.parameters(), lr=3e-3, weight_decay=wd)
        for _ in range(steps):
            opt.zero_grad()
            loss_fn(lin(x), y).backward()
            opt.step()
        return lin

    best = None
    for wd in (1e-4, 1e-3, 1e-2):
        lin = train(xtr[~val], ytr[~val], wd)
        with torch.no_grad():
            l_ = float(loss_fn(lin(xtr[val]), ytr[val]))
        if best is None or l_ < best[0]:
            best = (l_, wd)
    lin = train(xtr, ytr, best[1])
    with torch.no_grad():
        return lin(xte).cpu().numpy()


def mean_auc(S, Y):
    v = [rd.auc(S[:, j], Y[:, j].astype(bool)) for j in range(Y.shape[1]) if 0 < Y[:, j].sum() < len(Y)]
    return float(np.mean(v)) if v else float("nan")


def scores(a, E, X, k, held, dev, rng):
    """The three targets at ply t + k from inputs X at t -> {target: (value, bootstrap SE)}."""
    src = np.flatnonzero(E["t"] + k <= E["n"])                    # the state at t, on a line reaching t + k
    tr, te = src[~held[E["pos"][src]]], src[held[E["pos"][src]]]
    dtr, dte = tr + k, te + k                                     # a line's states are consecutive rows
    g, gte = E["pos"][tr], E["pos"][te]
    sq = fit_probe(X[tr], E["to"][dtr], g, X[te], "ce", dev, a.steps)
    hit = sq.argmax(1) == E["to"][dte]
    ev_s = fit_probe(X[tr], E["ev"][dtr].astype(np.float32), g, X[te], "bce", dev, a.steps)
    la_s = fit_probe(X[tr], E["lat"][dtr].astype(np.float32), g, X[te], "bce", dev, a.steps)
    ug = np.unique(gte)
    by = {u: np.flatnonzero(gte == u) for u in ug}
    bs, be = [], []
    for _ in range(a.boot):
        pick = np.concatenate([by[u] for u in rng.choice(ug, len(ug))])
        bs.append(hit[pick].mean())
        be.append(mean_auc(ev_s[pick], E["ev"][dte][pick]))
    return dict(square=(float(hit.mean()), float(np.std(bs))), events=(mean_auc(ev_s, E["ev"][dte]), float(np.nanstd(be))),
                latents=(mean_auc(la_s, E["lat"][dte]), float("nan")))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=("all", "probe"), default="all")
    ap.add_argument("--cc-run", default="runs/transcend/crosscoder/everything-3m")
    ap.add_argument("--cc", default="Lfinal", help="the crosscoder whose latents are the latents target")
    ap.add_argument("--strong", default="2400")
    ap.add_argument("--population", default=str(gd.PROBE / "population.jsonl"))
    ap.add_argument("--positions", type=int, default=5000)
    ap.add_argument("--lines", type=int, default=2, help="rollouts per model per position")
    ap.add_argument("--plies", type=int, default=8)
    ap.add_argument("--T", type=float, default=1.0)
    ap.add_argument("--models", default="S,W")
    ap.add_argument("--ks", default="1,2,4,6")
    ap.add_argument("--latents", type=int, default=100)
    ap.add_argument("--steps", type=int, default=300, help="full-batch Adam steps per probe")
    ap.add_argument("--boot", type=int, default=100)
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--max-tokens", type=int, default=300_000)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    a.tag = a.tag or f"n{a.positions}-l{a.lines}-p{a.plies}-T{a.T}-s{a.seed}"
    run, res = RUNS / a.tag, RESULTS / a.tag
    run.mkdir(parents=True, exist_ok=True)
    res.mkdir(parents=True, exist_ok=True)
    if a.stage == "all":
        play(a, run)
    dev = ev.device(a.device)
    layers = json.loads((run / "layers.json").read_text())
    roots = json.loads((run / "roots.json").read_text(encoding="utf-8"))
    held = np.array([zlib.crc32(f"{r['band']}/{r['game']}".encode()) % 2 for r in roots]) == 1
    ks = [int(k) for k in a.ks.split(",")]
    rng = np.random.default_rng(0)
    R = {}
    t_all = time.time()
    for who in a.models.split(","):
        E = examples(a, run, who, roots)
        print(f"{who}: {len(E['t'])} states at {len(roots)} positions; {len(E['lat_ids'])} latents", flush=True)
        R[who] = {}
        for name in ["board"] + layers:
            X = E["board"].astype(np.float32) if name == "board" else np.load(run / f"{who}-L{name}.npy").astype(np.float32)
            if len(X) != len(E["t"]):
                sys.exit(f"{who} {name}: {len(X)} states for {len(E['t'])} examples")
            t0 = time.time()
            R[who][name] = {k: scores(a, E, X, k, held, dev, rng) for k in ks}
            print(f"  {who} {name}: " + "; ".join(f"k {k}: square {R[who][name][k]['square'][0]:.3f}, events "
                  f"{R[who][name][k]['events'][0]:.3f}, latents {R[who][name][k]['latents'][0]:.3f}" for k in ks)
                  + f" ({time.time() - t0:.0f}s)", flush=True)
            write(a, res, R, layers, ks, len(roots), held)
    print(f"wrote {res / 'report.md'} ({(time.time() - t_all) / 60:.0f} min)")


def write(a, res, R, layers, ks, n_pos, held):
    out = ["# Where does the future live: linear probes from each layer to ply t + k", "",
           f"{n_pos} positions (fit {int((~held).sum())}, held out {int(held.sum())}, by game); {a.lines} lines of {a.plies} plies "
           f"per position and model at T = {a.T}, each model's states on its own lines. square: top-1 accuracy for the "
           "destination square of the move at ply t + k (k = 1: the next move; chance 1/64 = 0.016); events: mean AUC (check, "
           "capture, pawn push, promotion, castles at t + k); latents: mean AUC for the final-layer crosscoder's "
           f"{a.latents} most frequent latents at t + k (favours late layers by construction). board only: the same probe "
           "from the board at t. +- one bootstrap SE over held-out positions.", ""]
    for who, Rw in R.items():
        for tg in TARGETS:
            out += [f"## {who}: {tg}", "", "| input | " + " | ".join(f"k = {k}" for k in ks) + " |", "|---|" + "---|" * len(ks)]
            cell = lambda v: f"{v[0]:.3f}" + (f" +- {v[1]:.3f}" if v[1] == v[1] else "")
            out += [f"| {'board only' if n == 'board' else 'layer ' + n} | " + " | ".join(cell(Rw[n][k][tg]) for k in ks) + " |"
                    for n in ["board"] + layers if n in Rw]
            out.append("")
    (res / "report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    (res / "report.json").write_text(json.dumps({w: {n: {str(k): v for k, v in r.items()} for n, r in Rw.items()}
                                                 for w, Rw in R.items()}, indent=1), encoding="utf-8")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(len(R), 3, figsize=(15, 4 * len(R)), squeeze=False)
    for i, (who, Rw) in enumerate(R.items()):
        Ls = [L for L in layers if L in Rw]
        x = np.arange(len(Ls))
        for j, tg in enumerate(TARGETS):
            p = ax[i, j]
            for c, k in enumerate(ks):
                if Ls:
                    p.plot(x, [Rw[L][k][tg][0] for L in Ls], "o-", color=f"C{c}", label=f"k = {k}")
                p.axhline(Rw["board"][k][tg][0], color=f"C{c}", ls=":", lw=1)
            p.set_xticks(x, Ls, fontsize=7)
            p.set_title(f"{who}: {tg} at ply t + k (dotted: board only)", fontsize=10)
            p.set_xlabel("layer")
            p.set_ylabel("top-1 accuracy" if tg == "square" else "mean AUC")
            if Ls:
                p.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(res / "layers.png", dpi=110)
    plt.close(fig)


if __name__ == "__main__":
    main()
