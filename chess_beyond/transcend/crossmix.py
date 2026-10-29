"""A crosscoder at one layer (default L11, where the layer probe put the models' future moves) of both models, trained on
human-game positions and the models' own rollouts, about half each, at several dictionary sizes.

    python transcend/crossmix.py all                         # human, rollouts, then train each --sizes
    python transcend/crossmix.py train --sizes 16384         # one size again (the data are cached)

human     --human positions from human games (crosscoder.py's collect: pgn-everything, random plies from ply 10 on),
          both models' states after block --layer at the prompt's last character. -> <run>/human/.
rollouts  every position of the graphdiff run's lines (4,000 held-out roots; per root 4 rollouts by S, 4 by W and 4 more
          by S, 8 plies at T = 1, the model playing both colours) and each root once, minus roots from the games of the
          divergence analysis (the manypositions positions): both models' states, same hook.
          -> <run>/rollouts/.
train     BatchTopK crosscoder (crosscoder.py's), each source scaled to mean norm sqrt(d), AuxK, and dead-latent
          resampling: every --resample-every steps up to 60% of training, latents that have not fired for --dead-steps
          are re-initialised toward the worst-reconstructed inputs of the batch (decoder = their residual, encoder =
          0.2 x that, Adam state reset). Held out: human positions by game, rollouts by root. Every --eval-every steps:
            FVU per model on held-out human and rollout positions, separately;
            splice KL per model: the model's own move distribution against the one with its state at this layer
              replaced by the crosscoder's reconstruction, on --splice held-out human and rollout positions; beside it the
              S-W KL (S's distribution against W's) at the same positions, the scale a model difference has;
            dead latents (no firing on the held-out positions at the inference threshold) and AuxK's dead count;
            antipodal pairs: latent pairs whose decoder directions for one model have cosine < -0.9 (mirror latents).
          A checkpoint every --ckpt-every steps (cc.pt, loadable as a finished one), so a partial run is usable.
          -> <run>/cc-L<layer>-<size>/cc.pt, train_log.jsonl; results/transcend/crosscoder/<run>/cc-L<layer>-<size>/report.md.
The run folder has a collect.json like crosscoder.py's, so shared.load_cc(<run>, "L11-16384", ...) loads a result."""

import argparse
import json
import math
import sys
import time
import zlib
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import paths
import eval as ev
import crosscoder as cx
import shared as gd
from pgn_probe import parse_movetext

RUNS = paths.RUNS / "transcend" / "crosscoder"
RESULTS = paths.ROOT / "results" / "transcend" / "crosscoder"
LINES = paths.RUNS / "transcend" / "graphdiff" / "everything-3m-Lfinal" / "lines.json"


def excluded_games():
    """(band, game) of the positions the crosscoder's own analysis uses (divergence.py's: the manypositions positions),
    so it never trains on them. (readings.py's and layerprobe.py's positions come from the same seeded order of the
    same pool as the graphdiff roots, so excluding those would drop every root; neither analyses this crosscoder.)"""
    out = set()
    for f in (paths.RUNS / "transcend" / "manypositions").glob("*/positions.json"):
        out |= {(str(r["band"]), str(r["game"])) for r in json.loads(f.read_text(encoding="utf-8"))}
    return out


def load_models(dev):
    return [ev.load(m, dev) for m in cx.MODELS]


# ---------------------------------------------------------------- data
def human(a, run):
    out = run / "human"
    if (out / "collect.json").exists():
        print(f"human positions cached in {out}")
        return
    cx.collect(argparse.Namespace(device=a.device, models=cx.MODELS, run=str(out), pgn_data=cx.FOLDERS, positions=a.human,
                                  per_game=16, min_ply=10, max_tokens=64 * 1024, layers=[a.layer], seed=a.seed))


def rollouts(a, run, models, dev):
    out = run / "rollouts"
    if (out / "rows.json").exists():
        print(f"rollout positions cached in {out}")
        return
    (out / "acts").mkdir(parents=True, exist_ok=True)
    G = json.loads(LINES.read_text(encoding="utf-8"))
    ex = excluded_games()
    keep = [i for i, r in enumerate(G["roots"]) if (str(r["band"]), str(r["game"])) not in ex]
    print(f"rollouts: {len(keep)} of {len(G['roots'])} roots kept ({len(G['roots']) - len(keep)} share a game with an analysis)")
    new = {i: j for j, i in enumerate(keep)}
    roots = [dict(prompt=G["roots"][i]["prompt"], fen=G["roots"][i]["fen"], band=G["roots"][i]["band"],
                  game=str(G["roots"][i]["game"])) for i in keep]
    lines = [dict(root=new[l["root"]], kind=l["kind"], moves=l["moves"]) for l in G["lines"] if l["root"] in new]
    seqs, ends, _, _, _, start = gd.positions(dict(roots=roots, lines=lines))
    rows, take, first = [], [], set()
    for q, l in enumerate(lines):
        for t in range(start[q + 1] - start[q]):
            if t == 0 and l["root"] in first:                       # the root once, not once per line
                continue
            first.add(l["root"])
            rows.append((l["root"], q, t))
            take.append(start[q] + t)
    take = np.array(take)
    t0 = time.time()
    for m, name in models:
        S_ = gd.line_states(m, seqs, ends, a.layer, dev, a.max_tokens).numpy()
        np.save(out / "acts" / f"{cx.source_name(name, a.layer)}.npy", S_[take].astype(np.float16))
        print(f"  {name}: {len(take)} states ({time.time() - t0:.0f}s)", flush=True)
    (out / "rows.json").write_text(json.dumps(dict(roots=roots, lines=lines, rows=rows)), encoding="utf-8")


def held_out_human(rows):
    return (rows[:, 0] * 1_000_003 + rows[:, 1]) % 50 == 0              # crosscoder.py's split: by game, ~2%


def held_out_roll(roots, rows):
    return np.array([zlib.crc32(f"{roots[r]['band']}/{roots[r]['game']}".encode()) % 20 == 0 for r, _, _ in rows])   # by root, ~5%


def eval_positions(a, run, rng):
    """Up to --splice held-out human and rollout positions: their boards, prompts and rows in each array."""
    corpus = cx.Corpus(cx.FOLDERS)
    hrows = np.load(run / "human" / "rows.npy")
    hi = np.flatnonzero(held_out_human(hrows))
    hi = np.sort(rng.choice(hi, min(a.splice, len(hi)), replace=False))
    H = []
    for i in hi:
        f, g, ply, e = (int(v) for v in hrows[i])
        text = corpus.text(f, g)
        H.append((ev.board_of(parse_movetext(text)[0][:ply]), text[:e + 1]))
    R = json.loads((run / "rollouts" / "rows.json").read_text(encoding="utf-8"))
    ri = np.flatnonzero(held_out_roll(R["roots"], R["rows"]))
    ri = np.sort(rng.choice(ri, min(a.splice, len(ri)), replace=False))
    Rp = []
    for i in ri:
        r, q, t = R["rows"][i]
        line = dict(board=ev.board_of(gd.parse_movetext(R["roots"][r]["prompt"])[0]), moves=[], sans=[], prompt=R["roots"][r]["prompt"])
        for u in R["lines"][q]["moves"][:t]:
            gd.advance(line, line["board"].parse_uci(u))
        Rp.append((line["board"], line["prompt"]))
    return dict(human=(H, hi), rollouts=(Rp, ri))


# ---------------------------------------------------------------- training
def kl(p, q):
    return float(np.sum(np.exp(p) * (p - q)))


@torch.no_grad()
def baseline(models, layer, E, dev):
    """Per split: each model's unspliced move distributions and its states at the layer, at the evaluation positions."""
    base = {}
    for split, (P, _) in E.items():
        boards, prompts = [b for b, _ in P], [p for _, p in P]
        st, lp = {}, {}
        for i, (m, _) in enumerate(models):
            _, lp[i], s_ = gd.policy(m, boards, dev, prompts, grab=(layer,))
            st[i] = s_[layer].float()
        base[split] = (st, lp)
    return base


@torch.no_grad()
def splice(cc, models, scales, layer, E, dev, base):
    """Per split and model: the mean KL of the model's move distribution from the one with its state at the layer
    replaced by the reconstruction; and the S-W KL there (base: the unspliced distributions and states)."""
    out = {}
    for split, (P, _) in E.items():
        boards, prompts = [b for b, _ in P], [p for _, p in P]
        st, lp = base[split]
        x = torch.stack([st[i].to(dev) for i in range(len(models))], 1) * scales[None, :, None]
        f, _, _ = cc.encode(x)
        xh = cc.decode(f) / scales[None, :, None]
        row = {}
        for i, (m, name) in enumerate(models):
            _, sp, _ = gd.policy(m, boards, dev, prompts, layer=layer, repl=xh[:, i].float().cpu())
            row[name] = float(np.mean([kl(p, q) for p, q in zip(lp[i], sp)]))
        s, w = (1, 0) if "2400" in models[1][1] else (0, 1)
        row["S-W KL"] = float(np.mean([kl(p, q) for p, q in zip(lp[s], lp[w])]))
        out[split] = row
    return out


@torch.no_grad()
def fvu(cc, val):
    err = torch.zeros(val.shape[1], device=val.device)
    fired = torch.zeros(cc.b_enc.shape[0], dtype=torch.bool, device=val.device)
    l0 = 0.0
    for i in range(0, len(val), 4096):
        x = val[i:i + 4096]
        f, _, _ = cc.encode(x)
        err += (cc.decode(f) - x).pow(2).sum((0, 2))
        fired |= (f > 0).any(0)
        l0 += float((f > 0).sum())
    tot = (val - val.mean(0)).pow(2).sum((0, 2))
    return (err / tot).tolist(), l0 / len(val), fired


@torch.no_grad()
def antipodal(cc, thr=-0.9):
    """Per source: latent pairs whose decoder directions there have cosine < thr (both with a real decoder there)."""
    out = []
    W = cc.W_dec                                                       # (latents, sources, d)
    for s in range(W.shape[1]):
        v = W[:, s]
        nrm = v.norm(dim=-1)
        live = nrm > 0.05 * nrm.max()
        u = F.normalize(v[live], dim=-1)
        n = 0
        for i in range(0, len(u), 4096):
            c = u[i:i + 4096] @ u.T
            n += int((c < thr).sum())
        out.append(n // 2)
    return out


@torch.no_grad()
def resample(cc, opt, dead, x, x_hat):
    """Dead latents re-initialised toward the batch's worst-reconstructed inputs; their Adam state reset."""
    idx = torch.nonzero(dead).flatten()
    if not len(idx):
        return 0
    err = (x - x_hat).pow(2).sum((1, 2))
    pick = torch.multinomial(err / err.sum(), len(idx), replacement=len(idx) > len(err))
    r = (x - x_hat)[pick]                                              # (n, sources, d)
    r = r / r.norm(dim=-1).sum(1).clamp_min(1e-8)[:, None, None]      # decoder norms sum to 1 over sources
    cc.W_dec[idx] = r
    alive_norm = cc.W_enc[:, ~dead].norm(dim=0).mean() if (~dead).any() else torch.tensor(1.0, device=x.device)
    e = r.flatten(1)
    cc.W_enc[:, idx] = (e / e.norm(dim=1, keepdim=True).clamp_min(1e-8) * alive_norm * 0.2).T
    cc.b_enc[idx] = 0
    for p, sl in ((cc.W_dec, (idx,)), (cc.W_enc, (slice(None), idx)), (cc.b_enc, (idx,))):
        st = opt.state.get(p, {})
        for k in ("exp_avg", "exp_avg_sq"):
            if k in st:
                st[k][sl] = 0
    return len(idx)


def train(a, run, size, models, dev, E, base):
    info = json.loads((run / "collect.json").read_text())
    names_ = info["names"]
    sources = [(m, a.layer) for m in range(len(info["names"]))]
    cc_dir = run / f"cc-L{a.layer}-{size}"
    cc_dir.mkdir(exist_ok=True)
    res = RESULTS / run.name / cc_dir.name
    res.mkdir(parents=True, exist_ok=True)
    arr = {k: [np.load(run / k / "acts" / f"{cx.source_name(n, a.layer)}.npy", mmap_mode="r") for n in info["names"]]
           for k in ("human", "rollouts")}
    hrows = np.load(run / "human" / "rows.npy")
    R = json.loads((run / "rollouts" / "rows.json").read_text(encoding="utf-8"))
    hold = dict(human=held_out_human(hrows), rollouts=held_out_roll(R["roots"], R["rows"]))
    X = {k: torch.from_numpy(np.stack([np.asarray(x) for x in arr[k]], 1)) for k in arr}   # (n, sources, d) fp16
    d = X["human"].shape[-1]
    tr = torch.cat([X[k][torch.from_numpy(~hold[k])] for k in X])
    origin = np.r_[np.zeros(int((~hold["human"]).sum()), int), np.ones(int((~hold["rollouts"]).sum()), int)]
    sample = tr[torch.randperm(len(tr), generator=torch.Generator().manual_seed(a.seed))[:100_000]].float()
    scales = (math.sqrt(d) / sample.norm(dim=-1).mean(0)).to(dev)
    val = {k: (X[k][torch.from_numpy(hold[k])][:20_000].to(dev).float() * scales[None, :, None]) for k in X}
    tr = tr.to(dev)
    if E is not None:                                                  # the policy's hook must give the stored states
        for split, (_, idx) in E.items():
            for i in range(len(sources)):
                got, want = base[split][0][i], X[split][torch.from_numpy(idx), i].float()
                rel = ((got - want).norm(dim=-1) / want.norm(dim=-1).clamp_min(1e-6)).median()
                if rel > 0.05:
                    sys.exit(f"{split}, {names_[i]}: the policy's states at L{a.layer} differ from the stored ones "
                             f"(median relative difference {rel:.3f}): stopping")
        print("hook check: the policy's states match the stored ones at the evaluation positions", flush=True)
    torch.manual_seed(a.seed)
    torch.backends.cuda.matmul.allow_tf32 = True
    cc = cx.CrossCoder(len(sources), d, size, a.k).to(dev)
    with torch.no_grad():
        cc.b_dec.copy_((sample.to(dev) * scales[None, :, None]).mean(0))
        var = ((sample.to(dev) * scales[None, :, None]) - cc.b_dec).pow(2).sum((1, 2)).mean()
    del sample
    opt = torch.optim.Adam(cc.parameters(), lr=a.lr)
    last = torch.zeros(size, dtype=torch.long, device=dev)
    log = open(cc_dir / "train_log.jsonl", "w", encoding="utf-8")
    names = info["names"]
    print(f"{size} latents: {len(tr)} training positions ({(origin == 0).sum()} human, {(origin == 1).sum()} rollout); held out "
          f"{len(val['human'])} human, {len(val['rollouts'])} rollout; k = {a.k}, {a.steps} steps of {a.batch}", flush=True)
    t0, resampled, row = time.time(), 0, None

    def save(step, row):
        torch.save(dict(state=cc.state_dict(), sources=sources, d=d, latents=size, k=a.k, scales=scales.cpu(), step=step,
                        val_fvu=row["fvu"] if row else None, args=vars(a)), cc_dir / "cc.pt")

    for step in range(1, a.steps + 1):
        lr = a.lr * min(1.0, step / 200) * min(1.0, 5 * (a.steps - step) / a.steps)
        for g in opt.param_groups:
            g["lr"] = lr
        x = tr[torch.randint(0, len(tr), (a.batch,), device=dev)].float() * scales[None, :, None]
        f, p, smallest = cc.encode(x, batch_topk=True)
        x_hat = cc.decode(f)
        mse = (x_hat - x).pow(2).sum((1, 2)).mean() / var
        with torch.no_grad():
            cc.theta.copy_(smallest if cc.theta < 0 else 0.99 * cc.theta + 0.01 * smallest)
        last[(f > 0).any(0)] = step
        dead = (step - last) > a.dead_steps
        loss, aux = mse, torch.zeros((), device=dev)
        if dead.any():
            top = p.masked_fill(~dead[None, :], -float("inf")).topk(min(a.k_aux, int(dead.sum())), dim=-1)
            z = torch.zeros_like(p).scatter_(-1, top.indices, F.relu(top.values))
            e = (x - x_hat).detach()
            aux = ((z @ cc.W_dec.flatten(1)).view_as(e) - e).pow(2).sum((1, 2)).mean() / e.pow(2).sum((1, 2)).mean().clamp_min(1e-8)
            loss = loss + a.aux_coef * aux
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        cc.normalise()
        if step % a.resample_every == 0 and step <= 0.6 * a.steps and dead.any():
            n = resample(cc, opt, dead, x, x_hat.detach())
            last[dead] = step
            resampled += n
            print(f"  step {step}: resampled {n} dead latents", flush=True)
        if step == 1000:
            print(f"  1000 steps in {time.time() - t0:.0f}s; projected {(time.time() - t0) * a.steps / 1000 / 60:.0f} min "
                  "for this size, plus the evaluations", flush=True)
        if step % a.eval_every == 0 or step == a.steps:
            fv = {k: fvu(cc, v) for k, v in val.items()}
            fired = fv["human"][2] | fv["rollouts"][2]
            row = dict(step=step, train_nmse=float(mse.detach()), aux=float(aux.detach()),
                       fvu={k: {names[m]: v for (m, _), v in zip(sources, fv[k][0])} for k in fv},
                       l0={k: fv[k][1] for k in fv}, dead_val=float((~fired).float().mean()),
                       dead_aux=float(dead.float().mean()), resampled=resampled, antipodal=dict(zip(names, antipodal(cc))),
                       theta=float(cc.theta), lr=lr, minutes=(time.time() - t0) / 60)
            if E is not None:
                row["splice_kl"] = splice(cc, models, scales, a.layer, E, dev, base)
            log.write(json.dumps(row) + "\n")
            log.flush()
            print(f"  step {step}: FVU " + "; ".join(f"{k} " + " ".join(f"{n.split('-')[-1]} {v:.3f}" for n, v in row["fvu"][k].items())
                                                 for k in row["fvu"])
                  + f"; L0 {row['l0']['human']:.0f}/{row['l0']['rollouts']:.0f}; dead {100 * row['dead_val']:.1f}%; antipodal "
                  + "/".join(str(v) for v in row["antipodal"].values())
                  + ("; splice KL " + "; ".join(f"{k} " + " ".join(f"{n.split('-')[-1] if n != 'S-W KL' else 'S-W'} {v:.4f}"
                                                                  for n, v in r.items()) for k, r in row["splice_kl"].items())
                     if "splice_kl" in row else "") + f"; {row['minutes']:.0f} min", flush=True)
        if step % a.ckpt_every == 0 or step == a.steps:
            save(step, row)
    report(res, size, row, a)
    print(f"wrote {cc_dir / 'cc.pt'} and {res / 'report.md'}")


def report(res, size, row, a):
    out = [f"# Crosscoder at L{a.layer}, {size} latents", "",
           f"k = {a.k}, {row['step']} steps of {a.batch}; human and rollout positions about half each. Held out: human by game, "
           "rollouts by root.", "", "| held out | " + " | ".join(f"FVU {n}" for n in next(iter(row["fvu"].values()))) + " | L0 |",
           "|---|" + "---|" * (len(next(iter(row["fvu"].values()))) + 1)]
    out += [f"| {k} | " + " | ".join(f"{v:.4f}" for v in r.values()) + f" | {row['l0'][k]:.1f} |" for k, r in row["fvu"].items()]
    if "splice_kl" in row:
        out += ["", "Splice KL (nats): each model's move distribution against the one with its state at this layer replaced by "
                "the reconstruction; S-W KL: S's distribution against W's at the same positions.", "",
                "| held out | " + " | ".join(next(iter(row["splice_kl"].values()))) + " |",
                "|---|" + "---|" * len(next(iter(row["splice_kl"].values())))]
        out += [f"| {k} | " + " | ".join(f"{v:.4f}" for v in r.values()) + " |" for k, r in row["splice_kl"].items()]
    out += ["", f"Dead latents (never firing on the held-out positions): {100 * row['dead_val']:.1f}%; resampled during "
            f"training: {row['resampled']}. Antipodal decoder pairs (cosine < -0.9): "
            + ", ".join(f"{n} {v}" for n, v in row["antipodal"].items()) + "."]
    (res / "report.md").write_text("\n".join(out) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=("human", "rollouts", "train", "all"))
    ap.add_argument("--layer", default="11")
    ap.add_argument("--run", default="", help="default runs/transcend/crosscoder/mixed-L<layer>")
    ap.add_argument("--human", type=int, default=400_000, help="human positions (about as many as the rollouts give)")
    ap.add_argument("--sizes", default="4096,16384")
    ap.add_argument("--k", type=int, default=64)
    ap.add_argument("--steps", type=int, default=20_000)
    ap.add_argument("--batch", type=int, default=4096)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--k-aux", type=int, default=512)
    ap.add_argument("--aux-coef", type=float, default=1 / 32)
    ap.add_argument("--dead-steps", type=int, default=500)
    ap.add_argument("--resample-every", type=int, default=2500)
    ap.add_argument("--eval-every", type=int, default=2500)
    ap.add_argument("--ckpt-every", type=int, default=5000)
    ap.add_argument("--splice", type=int, default=500, help="held-out positions per split for the splice KL (0: none)")
    ap.add_argument("--max-tokens", type=int, default=40_000)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    run = Path(a.run) if a.run else RUNS / f"mixed-L{a.layer}"
    run.mkdir(parents=True, exist_ok=True)
    dev = ev.device(a.device)
    if a.command in ("human", "all"):
        human(a, run)
    models = load_models(dev)
    if a.command in ("rollouts", "all"):
        rollouts(a, run, models, dev)
    if a.command in ("train", "all"):
        info = json.loads((run / "human" / "collect.json").read_text())
        (run / "collect.json").write_text(json.dumps({**info, "layers": [a.layer], "folders": info["folders"] + ["rollouts"]}, indent=1))
        E = eval_positions(a, run, np.random.default_rng(a.seed)) if a.splice else None
        base = baseline(models, a.layer, E, dev) if E is not None else None
        for size in [int(s) for s in a.sizes.split(",")]:
            train(a, run, size, models, dev, E, base)


if __name__ == "__main__":
    main()
