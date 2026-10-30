"""Steering across the recent history: add r ||h_i|| u_hat to the L11 state at the prompt end of each of the last n plies
(each position's own norm), not only the last one. Later layers, the cache and the move's characters all read the
pushed states. With n = 1 this is shared.policy with repl = h + r ||h|| u_hat at the last position.

A ply's prompt end is where the model is about to write the next move: the '.' of a move number (White to move) and
the space after White's move (Black to move); pgn_model.prompt's format.

    python transcend/dynamic/steer_hist.py check --device cuda      # n = 1 against shared.policy's repl; then n = 6 runs
"""
import argparse, json, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # chess_beyond/
import paths  # noqa: E402  also puts transcend/'s folders on sys.path


def ends_of(prompt, n):
    """Character indices of the last n plies' prompt ends (the last is len(prompt) - 1)."""
    e = [i for i, c in enumerate(prompt) if c == "." or (c == " " and "." in prompt[prompt.rfind(" ", 0, i) + 1:i])]
    assert e and e[-1] == len(prompt) - 1, f"prompt does not end at a ply: {prompt[-20:]!r}"
    return e[-n:]


def prefill_hist(model, x, plen, cache, layer, mask, dirs, rs):
    """concepts.prefill with h -> h + r ||h|| u at the masked positions after `layer` (mask (S, T), dirs (S, d), rs (S,))."""
    import torch, torch.nn.functional as F
    S, T = x.shape
    d = model.ln.normalized_shape[0]
    rows = torch.arange(S, device=x.device)
    cache.plen, cache.plen_rep = plen, plen.repeat_interleave(cache.R)
    cache.pmask = torch.arange(cache.pk[0].shape[2], device=x.device)[None, :] < plen[:, None]
    h = model.tok(x) + model.pos(torch.arange(T, device=x.device))
    for l, blk in enumerate(model.blocks):
        q, k, v = (z.view(S, T, blk.heads, d // blk.heads).transpose(1, 2) for z in blk.qkv(blk.ln1(h)).split(d, dim=2))
        cache.pk[l][:, :, :T], cache.pv[l][:, :, :T] = k, v
        y = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        h = h + blk.proj(y.transpose(1, 2).reshape(S, T, d))
        h = h + blk.mlp(blk.ln2(h))
        if layer == str(l):
            nrm = h.float().norm(dim=-1, keepdim=True)
            h = (h.float() + mask[..., None] * rs[:, None, None] * nrm * dirs[:, None, :]).to(h.dtype)
    return model.head(model.ln(h[rows, plen - 1])).float()


def policy_hist(model, boards, dev, prompts, layer, n_plies, dirs, rs, batch=48):
    """shared.policy with the push at the last n_plies plies' prompt ends -> legal moves, log-probabilities."""
    import torch
    from concepts import Cache, extend, pad
    from pgn_model import MAX_MOVE_CHARS, SPACE, encode
    legal = [list(b.legal_moves) for b in boards]
    ids = [encode(p) for p in prompts]
    ends = [ends_of(p, n_plies) for p in prompts]
    n = MAX_MOVE_CHARS
    logp = [None] * len(boards)
    dirs = dirs.to(dev).float(); rs = torch.as_tensor(rs, device=dev, dtype=torch.float32)
    order = sorted(range(len(boards)), key=lambda i: (len(legal[i]), len(ids[i])))
    with torch.no_grad():
        for s in range(0, len(order), batch):
            idx = order[s:s + batch]
            R = max(1, max(len(legal[i]) for i in idx))
            x, plen = pad([ids[i] for i in idx], dev)
            mask = torch.zeros(x.shape, device=dev)
            for j, i in enumerate(idx): mask[j, ends[i]] = 1
            cache = Cache(model, len(idx), R, x.shape[1], n, dev)
            c = np.full((len(idx) * R, n + 1), SPACE, dtype=np.int64); clen = np.ones(len(idx) * R, dtype=np.int64)
            for j, i in enumerate(idx):
                for r, mv in enumerate(legal[i]):
                    t = encode(boards[i].san(mv) + " "); c[j * R + r, :len(t)] = t; clen[j * R + r] = len(t)
            c, clen = torch.from_numpy(c).to(dev), torch.from_numpy(clen).to(dev)
            with torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev == "cuda"):
                first = prefill_hist(model, x, plen, cache, layer, mask, dirs[idx], rs[idx])
                _, out = extend(model, c[:, :n], torch.arange(n, device=dev).expand(len(c), n), cache, ("final",), Ls=n)
                rest = model.head(out["final"]).float()
            lp = torch.log_softmax(first.repeat_interleave(R, 0), -1).gather(1, c[:, :1])[:, 0]
            more = torch.log_softmax(rest, -1).gather(2, c[:, 1:, None])[..., 0]
            lp = (lp + (more * (torch.arange(1, n + 1, device=dev)[None] < clen[:, None])).sum(1)).view(len(idx), R).double().cpu().numpy()
            for j, i in enumerate(idx):
                v = lp[j, :len(legal[i])]; logp[i] = v - np.logaddexp.reduce(v)
    return legal, logp


def check(a):
    """n = 1 must match shared.policy's repl path; n = 6 must differ, and pushing nothing must match the base."""
    import torch, chess
    import steer_after as sa
    dev, gd, cc, models, idx = sa.setup(a)
    jb = sa.jobs(a, "steer-after-jobs.json")[0]; pts = sa.fits(models, jb["points"])[:a.n_check]
    mi = idx[jb["model"]]; L = str(cc.layer[mi]); model = models[mi]
    boards = [chess.Board(p["fen"]) for p in pts]; prompts = [p["prompt"] for p in pts]
    _, base, st = gd.policy(model, boards, dev, prompts, grab=(L,), batch=a.batch)
    h = st[L].to(dev); hn = h.norm(dim=1, keepdim=True)
    u = sa.direction(cc, jb["lat"], jb["w"], jb["mu"], cc.col[mi], dev); u = u / u.norm()
    _, ref = gd.policy(model, boards, dev, prompts, layer=L, repl=(h + 0.25 * hn * u[None]).float().cpu(), batch=a.batch)[:2]
    U = u[None].expand(len(pts), -1)
    _, one = policy_hist(model, boards, dev, prompts, L, 1, U, [0.25] * len(pts), a.batch)
    _, zero = policy_hist(model, boards, dev, prompts, L, 6, U, [0.0] * len(pts), a.batch)
    _, six = policy_hist(model, boards, dev, prompts, L, 6, U, [0.25] * len(pts), a.batch)
    mx = lambda A, B: max(float(np.abs(x - y).max()) for x, y in zip(A, B))
    print(f"{jb['id']}, {len(pts)} points: max |log p| difference  n=1 vs repl {mx(one, ref):.4f} (should be ~0, bf16)  "
          f"r=0 vs base {mx(zero, base):.4f} (~0)  n=6 vs n=1 {mx(six, one):.4f} (should be clearly > 0)")
    print("ends of the first prompt:", [prompts[0][max(0, e - 6):e + 1] for e in ends_of(prompts[0], 6)])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["check"])
    ap.add_argument("--tag", default="p16-r1024-T0.4-s0-L11-4k")
    ap.add_argument("--cc-run", default="runs/transcend/crosscoder/mixed-L11")
    ap.add_argument("--cc", default="L11-4096")
    ap.add_argument("--strong", default="2400")
    ap.add_argument("--only", default="")
    ap.add_argument("--n-check", type=int, default=16)
    ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--device", default="auto")
    check(ap.parse_args())
