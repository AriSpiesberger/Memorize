"""Overnight rollouts (GPU): new middlegame positions until --deadline, S's and W's rollouts at each, encoded with the L11
4k crosscoder, seeds 0 and 1, values kept, one file per position (divergence.py's format, so concept_mine.py reads it).

Positions: data/pgn_probe/population.jsonl, one per game, games not used by the manypositions run (nor earlier in this
run), bands alternated, a seeded random order; kept when S's policy there has >= 2 moves >= --reasonable and none above
--max-top, the position is a middlegame and the rollouts fit the context (recurring.py's picking rule). Each position
goes to discovery or confirmation by a hash of its game (--disc-share), as it is created.
Rollouts: --rollouts lines of --plies plies at --temperature, each model playing both sides (oneposition.rollouts).

-> runs/transcend/overnight/{disc,conf}/positions.json, runs/transcend/divergence/<prefix>-{disc,conf}-s{0,1}/{S,W}/pos-k.npz,
   mu.json per folder once --mu-after discovery positions are done (confirmation uses discovery's), progress.log
Restartable: positions already written are kept; one whose files are incomplete is played again.

    python transcend/dynamic/overnight_play.py --deadline 2026-10-30T04:30
"""
import argparse, json, os, sys, time, zlib
from datetime import datetime
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # chess_beyond/
import paths  # noqa: E402  also puts transcend/'s folders on sys.path

OV = paths.RUNS / "transcend" / "overnight"
DIV = paths.RUNS / "transcend" / "divergence"


def folders(a, split):
    return {(s, m): DIV / f"{a.prefix}-{split}-s{s}" / m for s in (0, 1) for m in "SW"}


def log(a, msg):
    line = f"{datetime.now():%H:%M:%S} {msg}"
    print(line, flush=True)
    with open(OV / a.name / "progress.log", "a", encoding="utf-8") as fh: fh.write(line + "\n")


def save_npz(f, D, P):
    cnt = np.bincount(P.indices, minlength=P.shape[1])
    tot = np.bincount(P.indices, weights=P.data.astype(np.float64), minlength=P.shape[1])
    tmp = f.parent / f"tmp-{f.name}"                                      # not matched by pos-*.npz until complete
    np.savez_compressed(tmp, D=json.dumps(D), data=P.data.astype(np.float16), indices=P.indices, indptr=P.indptr,
                        shape=np.array(P.shape), vcnt=cnt, vsum=tot)
    os.replace(tmp, f)


def encode_both(a, ccs, models, root, D, dev):
    """recurring.encode_values for both crosscoders from one pass of the models -> [sparse (lines * (plies + 1), latents)]."""
    import torch
    import shared as gd
    from scipy import sparse
    Ld = dict(roots=[dict(prompt=root["prompt"], fen=root["fen"])], lines=[dict(root=0, moves=d["moves"]) for d in D])
    seqs, ends, _, _, _, line_start = gd.positions(Ld)
    st = {m: gd.line_states(models[m], seqs, ends, ccs[0].layer[m], dev, a.max_tokens) for m in (0, 1)}
    pos_line = np.repeat(np.arange(len(D)), np.diff(line_start))
    pos_t = np.concatenate([np.arange(n) for n in np.diff(line_start)])
    out = []
    for cc in ccs:
        rows, cols, vals = [], [], []
        with torch.no_grad():
            for i in range(0, len(st[0]), 4096):
                f, _ = gd.encode_states(cc, {m: st[m][i:i + 4096].to(dev) for m in (0, 1)})
                nz = (f > 0).nonzero()
                rows.append(nz[:, 0].cpu().numpy() + i); cols.append(nz[:, 1].cpu().numpy())
                vals.append(f[nz[:, 0], nz[:, 1]].float().cpu().numpy())
        rows, cols, vals = np.concatenate(rows), np.concatenate(cols), np.concatenate(vals)
        keep = pos_t[rows] >= 1; r_ = rows[keep]
        out.append(sparse.csr_matrix((vals[keep], (pos_line[r_] * (a.plies + 1) + pos_t[r_], cols[keep])),
                                     shape=(len(D) * (a.plies + 1), cc.ck["latents"])))
    return out


def candidates(a, Sm, dev, used, rng):
    """Positions in a seeded random order, bands alternated -> (root, S's legal moves, S's log-probabilities)."""
    import eval as ev
    import shared as gd
    from concepts import room
    from pgn_model import MAX_MOVE_CHARS, prompt
    from pgn_probe import parse_movetext
    pop = [json.loads(l) for l in open(paths.DATA / "pgn_probe" / "population.jsonl", encoding="utf-8")]
    perm = rng.permutation(len(pop))
    order = {b: [i for i in perm if pop[i]["band"] == b] for b in sorted({r["band"] for r in pop})}
    ptr = {b: 0 for b in order}; queue = {b: [] for b in order}
    def refill(band):                                                    # evaluate up to --scan more of this band
        cand = []
        while ptr[band] < len(order[band]) and len(cand) < a.scan:
            r = pop[order[band][ptr[band]]]; ptr[band] += 1
            if (r["band"], r["game"]) in used or len(r["prompt"]) + room(a.plies) + MAX_MOVE_CHARS + 1 > Sm.ctx: continue
            b = ev.board_of(parse_movetext(r["prompt"])[0])
            if prompt(b) != r["prompt"] or b.is_game_over() or not gd.middlegame(b): continue
            cand.append((r, b))
        if not cand: return
        legal, lp, _ = gd.policy(Sm, [b for _, b in cand], dev, [r["prompt"] for r, _ in cand], batch=a.batch)
        for (r, b), mv, l in zip(cand, legal, lp):
            p = np.exp(l - np.logaddexp.reduce(l))
            if p.max() <= a.max_top and (p >= a.reasonable).sum() >= 2: queue[band].append((r, b, mv, l))
    while True:
        gave = False
        for band in order:
            while True:
                while not queue[band] and ptr[band] < len(order[band]): refill(band)
                if not queue[band]: break
                r, b, mv, l = queue[band].pop(0)
                if (r["band"], r["game"]) in used: continue              # one position per game
                used.add((r["band"], r["game"])); gave = True
                top = sorted(zip(np.exp(l), mv), key=lambda x: -x[0])[:5]
                yield dict(prompt=r["prompt"], fen=b.fen(), band=r["band"], game=r["game"],
                           top=[(b.san(m), float(q)) for q, m in top]), mv, l
                break
        if not gave: return


def write_mu(a, split_src="disc"):
    import recurring as rc
    n = len(json.loads((OV / a.name / "disc" / "positions.json").read_text(encoding="utf-8")))
    for s in (0, 1):
        for m in "SW":
            run = DIV / f"{a.prefix}-disc-s{s}" / m
            done = sum((run / f"pos-{k}.npz").exists() for k in range(n))
            mu = rc.mu_of(run, n).tolist()
            for split in ("disc", "conf"):
                f = DIV / f"{a.prefix}-{split}-s{s}" / m / "mu.json"; f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(json.dumps(dict(positions=done, mu=mu, from_=f"{a.prefix}-disc-s{s}")), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--deadline", required=True, help="stop starting new positions after this local time (ISO)")
    ap.add_argument("--name", default="night1", help="runs/transcend/overnight/<name>")
    ap.add_argument("--prefix", default="ov1", help="divergence folders <prefix>-{disc,conf}-s{0,1}")
    ap.add_argument("--cc-run", default="runs/transcend/crosscoder/mixed-L11")
    ap.add_argument("--cc", default="L11-4096")
    ap.add_argument("--cc1", default="L11-4096-s1")
    ap.add_argument("--strong", default="2400")
    ap.add_argument("--rollouts", type=int, default=512)
    ap.add_argument("--plies", type=int, default=16)
    ap.add_argument("--temperature", type=float, default=0.4)
    ap.add_argument("--disc-share", type=float, default=0.6)
    ap.add_argument("--reasonable", type=float, default=0.2)
    ap.add_argument("--max-top", type=float, default=0.6)
    ap.add_argument("--scan", type=int, default=64)
    ap.add_argument("--mu-after", type=int, default=20, help="discovery positions before mu.json is written (fixed after)")
    ap.add_argument("--max-positions", type=int, default=0, help="stop after this many (a smoke test)")
    ap.add_argument("--log-every", type=float, default=1800)
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--max-tokens", type=int, default=300_000)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    import eval as ev
    import shared as gd
    import oneposition as op
    deadline = datetime.fromisoformat(a.deadline)
    (OV / a.name).mkdir(parents=True, exist_ok=True)
    src = {sp: OV / a.name / sp for sp in ("disc", "conf")}
    roots = {}
    for sp, d in src.items():
        d.mkdir(parents=True, exist_ok=True)
        roots[sp] = json.loads((d / "positions.json").read_text(encoding="utf-8")) if (d / "positions.json").exists() else []
        for f in folders(a, sp).values(): f.mkdir(parents=True, exist_ok=True)
    used = {(r["band"], r["game"]) for r in json.loads((paths.RUNS / "transcend/manypositions/p16-r1024-T0.4-s0/positions.json").read_text(encoding="utf-8"))}
    used |= {(r["band"], r["game"]) for sp in roots for r in roots[sp]}
    dev = ev.device(a.device)
    ccs = [gd.load_cc(paths.ROOT / a.cc_run, c, a.strong, dev) for c in (a.cc, a.cc1)]
    models = {m: ev.load(ccs[0].info["models"][m], dev)[0] for m in (0, 1)}
    who = {"S": ccs[0].s, "W": ccs[0].w}
    rng = np.random.default_rng(a.seed)
    def play_one(sp, k, root, s_legal=None, s_lp=None):
        t0 = time.time(); F = folders(a, sp); b = ev.board_of(gd.parse_movetext(root["prompt"])[0]); lines = {}
        for m in ("W", "S"):                                             # S's seed-0 file last: concept_mine counts those
            if m == "S" and s_legal is not None: legal, lp = s_legal, s_lp
            else:
                lg, lps, _ = gd.policy(models[who[m]], [b], dev, [root["prompt"]], batch=a.batch); legal, lp = lg[0], lps[0]
            sans, ucis = op.rollouts(a, root, legal, lp, models[who[m]], dev, a.temperature, [a.seed, zlib.crc32(f"{root['band']}/{root['game']}".encode()), 0 if m == "S" else 1])
            D = op.distinct(sans, ucis); P0, P1 = encode_both(a, ccs, models, root, D, dev)
            save_npz(F[(1, m)] / f"pos-{k}.npz", D, P1); save_npz(F[(0, m)] / f"pos-{k}.npz", D, P0); lines[m] = len(D)
        return time.time() - t0, lines
    # positions whose files are incomplete (a restart): play again
    for sp in roots:
        for k, root in enumerate(roots[sp]):
            if not all((f / f"pos-{k}.npz").exists() for f in folders(a, sp).values()):
                dt, ln = play_one(sp, k, root); log(a, f"replayed {sp} {k} ({dt:.0f}s)")
    t_start, t_log, times = time.time(), time.time(), []
    log(a, f"start: {len(roots['disc'])} discovery, {len(roots['conf'])} confirmation positions so far; deadline {deadline:%H:%M}")
    mu_done = (DIV / f"{a.prefix}-disc-s0" / "S" / "mu.json").exists()
    for root, mv, l in candidates(a, models[who["S"]], dev, used, rng):
        if datetime.now() >= deadline or (a.max_positions and sum(map(len, roots.values())) >= a.max_positions): break
        sp = "disc" if (zlib.crc32(f"{root['band']}/{root['game']}".encode()) % 1000) / 1000 < a.disc_share else "conf"
        k = len(roots[sp]); roots[sp].append(dict(root, split=sp))
        tmp = src[sp] / "tmp-positions.json"; tmp.write_text(json.dumps(roots[sp]), encoding="utf-8"); os.replace(tmp, src[sp] / "positions.json")
        dt, ln = play_one(sp, k, root, mv, l); times.append(dt)
        print(f"{sp} {k}: {root['band']} game {root['game']}, lines S {ln['S']} W {ln['W']} ({dt:.0f}s)", flush=True)
        if not mu_done and len(roots["disc"]) >= a.mu_after:
            write_mu(a); mu_done = True; log(a, f"mu.json written from {len(roots['disc'])} discovery positions")
        if time.time() - t_log >= a.log_every or len(times) == 5:
            left = max((deadline - datetime.now()).total_seconds(), 0); per = float(np.mean(times[-20:]))
            n = sum(map(len, roots.values()))
            log(a, f"{n} positions ({len(roots['disc'])} discovery, {len(roots['conf'])} confirmation); {per:.0f}s each; "
                   f"projected by {deadline:%H:%M}: {n + int(left / per)}")
            t_log = time.time()
    if not mu_done and roots["disc"]: write_mu(a); log(a, f"mu.json written from {len(roots['disc'])} discovery positions")
    log(a, f"done: {len(roots['disc'])} discovery, {len(roots['conf'])} confirmation positions ({(time.time() - t_start) / 60:.0f} min)")


if __name__ == "__main__":
    main()
