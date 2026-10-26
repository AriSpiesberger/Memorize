"""A sparse autoencoder on the PGN model's states, and the positions that most activate each latent.

    python transcend/sae.py collect --model Arisp/chess-pgn-2400plus --layer 8
    python transcend/sae.py train   --run runs/transcend/sae/chess-pgn-2400plus-L8
    python transcend/sae.py top     --run runs/transcend/sae/chess-pgn-2400plus-L8
    python transcend/sae.py all     --model Arisp/chess-pgn-2400plus --layer 8        # the three in a row

collect  Runs the model (eval.load: a Hugging Face repo or a local .pt) over game positions
         and keeps one vector per position: the state at the prompt's last character, the
         moment just before the model writes its move (pgn_model.prompt: "...<n>." for White,
         "...<White's move> " for Black). --layer final is the last layer after the final
         LayerNorm (what the move head reads); --layer N is the residual stream after block N
         (0-based). Positions come from data/pgn_probe/population.jsonl (held-out games of
         both bands, ~98k positions) by default, or from --pgn-data folders made by
         make_pgn_data.py: --positions random (game, ply) pairs, at ply >= --min-ply.
         -> <run>/acts.npy (float16) and <run>/rows.jsonl (the position behind each vector).

train    A TopK sparse autoencoder (Gao et al. 2024, "Scaling and evaluating sparse
         autoencoders"): z = TopK_k(W_enc (x - b_pre) + b_enc), x_hat = W_dec z + b_pre, with
         unit-norm decoder rows, inputs scaled to mean norm sqrt(d), and the AuxK loss
         (dead latents reconstruct the residual) so few latents die. Reports the fraction of
         variance unexplained (FVU) on held-out vectors and the dead-latent share.
         -> <run>/sae.pt and <run>/train_log.jsonl.

top      Encodes every vector and, per latent, keeps the --examples positions with the
         largest activation. Writes:
           results/transcend/sae/<run name>/report.md    training numbers, then the --report
               latents with the largest top activation that fire on 0.05%-20% of positions:
               firing rate overall and per band, and their top positions (band, move, the
               last moves, the move played, a Lichess analysis link)
           results/transcend/sae/<run name>/latents.jsonl  every latent: rates, top row ids
           <run>/features.html   the same report with a board diagram per example
"""
import argparse
import html
import json
import math
import random
import sys
import time
from pathlib import Path

import chess
import chess.svg
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parent))          # transcend/
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))      # chess_beyond/
import paths
import eval as ev                                                 # load (HF or .pt), board_of, device
from pgn_model import SPACE, VOCAB, encode, prompt
from pgn_probe import parse_movetext

RUNS = paths.RUNS / "transcend" / "sae"
RESULTS = paths.ROOT / "results" / "transcend" / "sae"


# ---------------------------------------------------------------- positions and activations

def population_rows():
    rows = [json.loads(l) for l in open(paths.DATA / "pgn_probe" / "population.jsonl", encoding="utf-8")]
    return [dict(prompt=r["prompt"], next_san=r["next_san"], fen=r["fen"], band=r["band"],
                 move_number=r["move_number"], side=r["side"]) for r in rows]


def corpus_rows(folders, n, min_ply, seed):
    """n random (game, ply) positions from make_pgn_data.py folders, spread evenly over the folders."""
    rng = random.Random(seed)
    chars = np.array(list(VOCAB))
    out = []
    for f in folders:
        f = Path(f)
        tokens = np.memmap(f / "tokens.bin", dtype=np.uint8, mode="r")
        starts = np.load(f / "starts.npy")
        band = json.loads((f / "meta.json").read_text()).get("band", f.name)
        want, tries = n // len(folders), 0
        while sum(r["band"] == band for r in out) < want and tries < 20 * want:
            tries += 1
            g = rng.randrange(len(starts))
            end = starts[g + 1] if g + 1 < len(starts) else len(tokens)
            sans, _ = parse_movetext("".join(chars[tokens[starts[g]:end]]))
            if len(sans) <= min_ply:
                continue
            ply = rng.randrange(min_ply, len(sans))
            try:
                b = ev.board_of(sans[:ply])
            except ValueError:
                continue
            out.append(dict(prompt=prompt(b), next_san=sans[ply], fen=b.fen(), band=band,
                            move_number=ply // 2 + 1, side="white" if ply % 2 == 0 else "black"))
        print(f"  {band}: {sum(r['band'] == band for r in out)} positions", flush=True)
    return out


@torch.no_grad()
def activations(model, rows, layer, dev, batch=256):
    """(len(rows), d) float16: the state at each prompt's last character, after block `layer`
    (0-based) or, for layer 'final', after the final LayerNorm."""
    seqs = [encode(r["prompt"])[-(model.ctx - 1):] for r in rows]   # long games keep their latest moves
    order = sorted(range(len(seqs)), key=lambda i: len(seqs[i]))
    d = model.ln.normalized_shape[0]
    out = np.zeros((len(seqs), d), dtype=np.float16)
    grabbed = {}
    hook = None
    if layer != "final":
        hook = model.blocks[int(layer)].register_forward_hook(lambda m, i, o: grabbed.__setitem__("h", o))
    try:
        for s in range(0, len(order), batch):
            idx = order[s:s + batch]
            n = max(len(seqs[i]) for i in idx)
            x = torch.full((len(idx), n), SPACE, dtype=torch.long)
            for r, i in enumerate(idx):
                x[r, :len(seqs[i])] = torch.tensor(seqs[i])
            with torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev == "cuda"):
                h = model.features(x.to(dev))
            h = grabbed["h"] if hook else h
            last = torch.tensor([len(seqs[i]) - 1 for i in idx], device=h.device)
            out[idx] = h[torch.arange(len(idx), device=h.device), last].float().cpu().numpy()
            print(f"\r  {min(s + batch, len(order))}/{len(order)} positions", end="", flush=True)
    finally:
        if hook:
            hook.remove()
    print()
    return out


def collect(a):
    dev = ev.device(a.device)
    model, name = ev.load(a.model, dev)
    run = Path(a.run) if a.run else RUNS / f"{name}-L{a.layer}"
    rows = corpus_rows(a.pgn_data, a.positions, a.min_ply, a.seed) if a.pgn_data else population_rows()
    print(f"{name}: {len(rows)} positions, layer {a.layer}", flush=True)
    acts = activations(model, rows, a.layer, dev)
    run.mkdir(parents=True, exist_ok=True)
    np.save(run / "acts.npy", acts)
    with open(run / "rows.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    (run / "collect.json").write_text(json.dumps(dict(model=a.model, layer=a.layer, positions=len(rows),
                                                      source=a.pgn_data or "data/pgn_probe/population.jsonl"),
                                                 indent=1))
    print(f"wrote {run / 'acts.npy'} {acts.shape}")
    return run


# ---------------------------------------------------------------- the sparse autoencoder

class TopKSAE(nn.Module):
    def __init__(self, d, latents, k):
        super().__init__()
        self.b_pre = nn.Parameter(torch.zeros(d))
        enc = torch.randn(d, latents) / math.sqrt(d)
        self.W_enc = nn.Parameter(enc)
        self.b_enc = nn.Parameter(torch.zeros(latents))
        self.W_dec = nn.Parameter(enc.T.clone())
        self.k = k
        self.normalise()

    @torch.no_grad()
    def normalise(self):
        self.W_dec /= self.W_dec.norm(dim=1, keepdim=True).clamp_min(1e-8)

    def pre(self, x):
        return (x - self.b_pre) @ self.W_enc + self.b_enc

    def encode(self, x, k=None):
        p = self.pre(x)
        top = p.topk(k or self.k, dim=-1)
        return torch.zeros_like(p).scatter_(-1, top.indices, F.relu(top.values)), p

    def forward(self, x):
        z, p = self.encode(x)
        return z @ self.W_dec + self.b_pre, z, p


def train(a):
    run = Path(a.run)
    X = torch.from_numpy(np.load(run / "acts.npy").astype(np.float32))
    torch.manual_seed(a.seed)
    perm = torch.randperm(len(X))
    n_val = min(5000, len(X) // 10)
    val, tr = X[perm[:n_val]], X[perm[n_val:]]
    scale = float(math.sqrt(X.shape[1]) / tr.norm(dim=1).mean())   # inputs at mean norm sqrt(d)
    dev = ev.device(a.device)
    tr, val = (tr * scale).to(dev), (val * scale).to(dev)
    sae = TopKSAE(X.shape[1], a.latents, a.k).to(dev)
    with torch.no_grad():
        sae.b_pre.copy_(tr.mean(0))
    opt = torch.optim.Adam(sae.parameters(), lr=a.lr, betas=(0.9, 0.999))
    last_fired = torch.zeros(a.latents, dtype=torch.long, device=dev)
    var_tr = (tr - tr.mean(0)).pow(2).sum(1).mean()
    log = open(run / "train_log.jsonl", "w", encoding="utf-8")
    t0 = time.time()
    print(f"{len(tr)} training vectors, {n_val} held out; {a.latents} latents, k = {a.k}, {a.steps} steps", flush=True)
    for step in range(1, a.steps + 1):
        lr = a.lr * min(1.0, step / 200) * (min(1.0, 5 * (a.steps - step) / a.steps) if a.steps > 5 else 1.0)
        for g in opt.param_groups:
            g["lr"] = lr
        x = tr[torch.randint(0, len(tr), (a.batch,), device=dev)]
        x_hat, z, p = sae(x)
        mse = (x_hat - x).pow(2).sum(1).mean() / var_tr
        fired = (z > 0).any(0)
        last_fired[fired] = step
        dead = (step - last_fired) > a.dead_steps
        loss, aux = mse, torch.zeros((), device=dev)
        if dead.any():                                      # AuxK: dead latents model the residual
            k_aux = min(a.k_aux, int(dead.sum()))
            pd = p.masked_fill(~dead[None, :], -float("inf"))
            top = pd.topk(k_aux, dim=-1)
            z_aux = torch.zeros_like(p).scatter_(-1, top.indices, F.relu(top.values))
            e = (x - x_hat).detach()
            aux = (z_aux @ sae.W_dec - e).pow(2).sum(1).mean() / e.pow(2).sum(1).mean().clamp_min(1e-8)
            loss = loss + a.aux_coef * aux
        opt.zero_grad(set_to_none=True)
        loss.backward()
        with torch.no_grad():                                # keep the update tangent to the unit-norm rows
            g = sae.W_dec.grad
            g -= (g * sae.W_dec).sum(1, keepdim=True) * sae.W_dec
        opt.step()
        sae.normalise()
        if step % a.eval_every == 0 or step == a.steps:
            with torch.no_grad():
                vh, vz, _ = sae(val)
                fvu = float((vh - val).pow(2).sum() / (val - val.mean(0)).pow(2).sum())
            row = dict(step=step, train_nmse=float(mse), aux=float(aux), val_fvu=fvu,
                       dead_frac=float(dead.float().mean()), lr=lr)
            log.write(json.dumps(row) + "\n")
            log.flush()
            print(f"  step {step}  train nmse {float(mse):.4f}  held-out FVU {fvu:.4f}  "
                  f"dead {100 * row['dead_frac']:.1f}%  {time.time() - t0:.0f}s", flush=True)
    torch.save(dict(state=sae.state_dict(), d=X.shape[1], latents=a.latents, k=a.k, scale=scale,
                    val_fvu=fvu, dead_frac=row["dead_frac"], args=vars(a)), run / "sae.pt")
    print(f"wrote {run / 'sae.pt'}")


# ---------------------------------------------------------------- max-activating positions

def last_moves(text, n=8):
    """The last n moves of a prompt, with move numbers, for display."""
    toks = text.lstrip(";").split()
    return " ".join(toks[-n:]) if toks else ""


def lichess(fen):
    return "https://lichess.org/analysis/" + fen.replace(" ", "_")


def top(a):
    run = Path(a.run)
    ck = torch.load(run / "sae.pt", map_location="cpu", weights_only=False)
    dev = ev.device(a.device)
    sae = TopKSAE(ck["d"], ck["latents"], ck["k"]).to(dev)
    sae.load_state_dict(ck["state"])
    X = np.load(run / "acts.npy")
    rows = [json.loads(l) for l in open(run / "rows.jsonl", encoding="utf-8")]
    bands = sorted({r["band"] for r in rows})
    band_of = np.array([bands.index(r["band"]) for r in rows])
    L, E = ck["latents"], a.examples
    best_v = torch.full((L, E), -1.0, device=dev)
    best_i = torch.zeros((L, E), dtype=torch.long, device=dev)
    count = torch.zeros((len(bands), L), device=dev)
    with torch.no_grad():
        for s in range(0, len(X), 2048):
            x = torch.from_numpy(X[s:s + 2048].astype(np.float32)).to(dev) * ck["scale"]
            z, _ = sae.encode(x)
            b = torch.from_numpy(band_of[s:s + 2048]).to(dev)
            for j in range(len(bands)):
                count[j] += (z[b == j] > 0).sum(0)
            v = torch.cat([best_v, z.T], 1)
            i = torch.cat([best_i, torch.arange(s, s + len(x), device=dev).expand(L, -1)], 1)
            keep = v.topk(E, dim=1)
            best_v, best_i = keep.values, i.gather(1, keep.indices)
    n_band = torch.tensor([(band_of == j).sum() for j in range(len(bands))], device=dev, dtype=torch.float)
    rate = count.sum(0) / len(X)
    rate_band = count / n_band[:, None]
    best_v, best_i, rate, rate_band = (t.cpu().numpy() for t in (best_v, best_i, rate, rate_band))

    name = run.name
    out = RESULTS / name
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "latents.jsonl", "w", encoding="utf-8") as f:
        for j in range(L):
            f.write(json.dumps(dict(latent=j, rate=float(rate[j]), rate_by_band={b: float(rate_band[k, j]) for k, b in enumerate(bands)},
                                    top=[(int(i), float(v)) for i, v in zip(best_i[j], best_v[j]) if v > 0])) + "\n")
    alive = rate > 0
    ok = (rate >= a.min_rate) & (rate <= a.max_rate)
    pick = sorted(np.flatnonzero(ok), key=lambda j: -best_v[j, 0])[:a.report]
    info = json.loads((run / "collect.json").read_text())
    md = [f"# SAE on {info['model']}, layer {info['layer']}", "",
          f"TopK SAE, {L} latents, k = {ck['k']}, trained on {info['positions']} positions from {info['source']}. "
          f"Held-out fraction of variance unexplained **{ck['val_fvu']:.3f}**; dead latents at the end of training "
          f"{100 * ck['dead_frac']:.1f}%; latents that fire on at least one position {100 * alive.mean():.1f}%.", "",
          f"Below: the {len(pick)} latents with the largest top activation among those firing on "
          f"{100 * a.min_rate:.2f}%-{100 * a.max_rate:.0f}% of positions. Each line is a position just before the model "
          f"moves: activation, band, move number and side to move, the last moves, then **the move actually played**.", ""]
    page = [f"<!doctype html><meta charset='utf-8'><title>{html.escape(name)}</title>",
            "<style>body{font:14px system-ui,sans-serif;margin:24px;max-width:1300px}"
            ".ex{display:inline-block;width:230px;margin:6px;vertical-align:top;font-size:12px}"
            "h2{margin-top:36px}code{font-size:12px}</style>",
            f"<h1>{html.escape(md[0][2:])}</h1><p>{html.escape(md[2])}</p>"]
    for j in pick:
        rb = ", ".join(f"{b} {100 * rate_band[k, j]:.2f}%" for k, b in enumerate(bands))
        head = f"latent {j}: fires on {100 * rate[j]:.2f}% of positions ({rb})"
        md += [f"## {head}", ""]
        page.append(f"<h2>{html.escape(head)}</h2>")
        for i, v in zip(best_i[j], best_v[j]):
            if v <= 0:
                continue
            r = rows[i]
            line = (f"{v:.2f} | {r['band']} | move {r['move_number']}, {r['side']} to move | "
                    f"`{last_moves(r['prompt'])}` -> **{r['next_san']}** | [board]({lichess(r['fen'])})")
            md.append(f"- {line}")
            b = chess.Board(r["fen"])
            try:
                mv = b.parse_san(r["next_san"])
            except ValueError:
                mv = None
            svg = chess.svg.board(b, size=220, arrows=[chess.svg.Arrow(mv.from_square, mv.to_square)] if mv else [],
                                  flipped=b.turn == chess.BLACK)
            page.append(f"<div class='ex'>{svg}<br>{v:.2f} &middot; {html.escape(r['band'])} &middot; move "
                        f"{r['move_number']} ({r['side']})<br><code>{html.escape(last_moves(r['prompt'], 6))}</code> "
                        f"&rarr; <b>{html.escape(r['next_san'])}</b> &middot; <a href='{lichess(r['fen'])}'>lichess</a></div>")
        md.append("")
    (out / "report.md").write_text("\n".join(md), encoding="utf-8")
    (run / "features.html").write_text("\n".join(page), encoding="utf-8")
    print(f"wrote {out / 'report.md'}, {out / 'latents.jsonl'} and {run / 'features.html'}")


# ---------------------------------------------------------------- command line

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for cmd in ("collect", "train", "top", "all"):
        p = sub.add_parser(cmd)
        p.add_argument("--device", default="auto", help="auto, cuda, mps or cpu")
        p.add_argument("--seed", type=int, default=0)
        p.add_argument("--run", default=None, help="run folder (default runs/transcend/sae/<model>-L<layer>)")
        if cmd in ("collect", "all"):
            p.add_argument("--model", required=True, help="Hugging Face repo id or a local .pt checkpoint")
            p.add_argument("--layer", default="final", help="'final' (after the last LayerNorm) or a block index 0-15")
            p.add_argument("--pgn-data", nargs="*", default=None,
                           help="make_pgn_data.py folders to sample positions from (default: data/pgn_probe/population.jsonl)")
            p.add_argument("--positions", type=int, default=200_000, help="with --pgn-data: positions to sample")
            p.add_argument("--min-ply", type=int, default=10)
        if cmd in ("train", "all"):
            p.add_argument("--latents", type=int, default=8192)
            p.add_argument("--k", type=int, default=32, help="active latents per position")
            p.add_argument("--steps", type=int, default=20_000)
            p.add_argument("--batch", type=int, default=4096)
            p.add_argument("--lr", type=float, default=2e-4)
            p.add_argument("--k-aux", type=int, default=256, help="AuxK: dead latents used to model the residual")
            p.add_argument("--aux-coef", type=float, default=1 / 32)
            p.add_argument("--dead-steps", type=int, default=500, help="steps without firing before a latent counts as dead")
            p.add_argument("--eval-every", type=int, default=1000)
        if cmd in ("top", "all"):
            p.add_argument("--examples", type=int, default=12, help="top positions kept per latent")
            p.add_argument("--report", type=int, default=100, help="latents shown in report.md / features.html")
            p.add_argument("--min-rate", type=float, default=0.0005, help="report only latents firing at least this often")
            p.add_argument("--max-rate", type=float, default=0.2, help="... and at most this often")
    a = ap.parse_args()
    if a.cmd in ("collect", "all"):
        a.run = str(collect(a))
    if a.cmd in ("train", "all"):
        if not a.run:
            sys.exit("--run is required")
        train(a)
    if a.cmd in ("top", "all"):
        if not a.run:
            sys.exit("--run is required")
        top(a)


if __name__ == "__main__":
    main()
