"""Drop games where a player looks far stronger, or far weaker, than their rating.

    python transcend/maia_filter.py --pgn data/lichess/bands/2025-06-train/1000-1300.pgn

For every player in every game, Maia-2 (a model of how humans at each rating
move) scores their moves twice: as a 2000+ player would play them and as a
sub-1100 player would. The player's strength index is the mean, over their
moves, of

    log P(move | Maia-2 at 2000+)  -  log P(move | Maia-2 at <1100)

High means the moves look much more like a strong player's than a weak one's
(engine help, or a stronger player on the account); low means they look weaker
than a sub-1100 player's (trolling, sandbagging, playing blind). A single good
or bad move barely moves the mean; it takes a whole game of them. Games where
either player is in the top --drop-high or bottom --drop-low fraction of all
player-games (with at least --min-moves scored moves) are dropped.

Scored moves skip the first --skip-plies plies (book moves look the same at
every rating) and forced moves, and stop after --max-moves per player. Blitz
and bullet use Maia-2's blitz model, rapid and classical its rapid model.

Scores are cached in <pgn>.maia_scores.npz, so changing the thresholds reruns in
seconds (pass --rescore to recompute). Writes <pgn stem>.maia-clean.pgn and
prints the cut-offs and how many games were dropped. If filter_cheaters.py's
<pgn>.accounts.json exists, it also reports where Lichess-marked cheaters land.
"""
import argparse
import io
import json
import multiprocessing as mp
import os
import sys
import time
from pathlib import Path

import chess
import chess.pgn
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # chess_beyond/: paths.py
import paths
from maia import elo_cat, encode

STRONG, WEAK = 2100, 1000          # Maia-2's top (>=2000) and bottom (<1100) rating buckets


def speed(headers):
    """0 = blitz model (bullet, blitz), 1 = rapid model (rapid, classical), by Lichess's clock rule."""
    try:
        base, inc = headers.get("TimeControl", "-").split("+")
        return 0 if int(base) + 40 * int(inc) < 480 else 1
    except ValueError:
        return 1


_MOVES = None


def _init(moves):
    global _MOVES
    _MOVES = moves


def work(job):
    """Positions to score from a chunk of games: (first game index, list of game texts)."""
    start, texts = job
    boards, legal, legal_len, played, opp, side, gidx, spd = [], [], [], [], [], [], [], []
    for k, text in enumerate(texts):
        game = chess.pgn.read_game(io.StringIO(text))
        if game is None:
            continue
        h = game.headers
        try:
            elos = {chess.WHITE: int(h["WhiteElo"]), chess.BLACK: int(h["BlackElo"])}
        except (KeyError, ValueError):
            continue
        s = speed(h)
        board = game.board()
        counts = {chess.WHITE: 0, chess.BLACK: 0}
        for ply, move in enumerate(game.mainline_moves()):
            mover = board.turn
            if (ply >= args.skip_plies and counts[mover] < args.max_moves
                    and board.legal_moves.count() > 1):
                b = board if mover == chess.WHITE else board.mirror()
                m = move if mover == chess.WHITE else chess.Move(chess.square_mirror(move.from_square),
                                                                  chess.square_mirror(move.to_square),
                                                                  move.promotion)
                boards.append(encode(b))
                lg = [_MOVES[x.uci()] for x in b.legal_moves]
                legal.extend(lg)
                legal_len.append(len(lg))
                played.append(_MOVES[m.uci()])
                opp.append(elo_cat(elos[not mover]))
                side.append(0 if mover == chess.WHITE else 1)
                gidx.append(start + k)
                spd.append(s)
                counts[mover] += 1
            board.push(move)
    if not boards:
        return start, len(texts), None
    return start, len(texts), dict(
        boards=np.stack(boards), legal=np.array(legal, np.int16), legal_len=np.array(legal_len, np.int16),
        played=np.array(played, np.int16), opp=np.array(opp, np.int8), side=np.array(side, np.int8),
        game=np.array(gidx, np.int64), speed=np.array(spd, np.int8))


def games(path):
    """Game texts in file order (a game starts at its [Event line)."""
    cur = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("[Event ") and cur:
                yield "".join(cur)
                cur = []
            cur.append(line)
    if cur:
        yield "".join(cur)


def chunks(path, size):
    buf, start = [], 0
    for text in games(path):
        buf.append(text)
        if len(buf) == size:
            yield start, buf
            start += len(buf)
            buf = []
    if buf:
        yield start, buf


def score(n_games):
    import torch
    from maia2 import inference as I2
    from maia2 import model as M2

    dev = "cuda" if torch.cuda.is_available() else "cpu"
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    models = [M2.from_pretrained(type=t, device=dev, save_root=str(paths.MAIA2)).eval() for t in ("blitz", "rapid")]
    moves, elo_dict, _ = I2.prepare()
    n_moves = len(moves)
    strong, weak = I2.map_to_category(STRONG, elo_dict), I2.map_to_category(WEAK, elo_dict)

    total = np.zeros((n_games, 2))            # summed strength index per game, side
    count = np.zeros((n_games, 2), np.int32)
    pending = [[], []]                        # per speed: list of position dicts not yet scored
    stats = dict(pos=0, t0=time.time())

    @torch.inference_mode()
    def flush(s, force=False):
        parts = pending[s]
        size = sum(len(p["played"]) for p in parts)
        if not parts or (size < args.batch and not force):
            return
        cat = {k: np.concatenate([p[k] for p in parts]) for k in ("boards", "legal", "legal_len", "played", "opp", "side", "game")}
        pending[s] = []
        offs = np.concatenate([[0], np.cumsum(cat["legal_len"].astype(np.int64))])
        for a in range(0, len(cat["played"]), args.batch):
            sl = slice(a, a + args.batch)
            n = len(cat["played"][sl])
            lo, hi = offs[a], offs[min(a + args.batch, len(cat["played"]))]
            mask = torch.zeros((n, n_moves), dtype=torch.bool, device=dev)
            rows = torch.repeat_interleave(torch.arange(n, device=dev),
                                           torch.as_tensor(cat["legal_len"][sl].astype(np.int64), device=dev))
            mask[rows, torch.as_tensor(cat["legal"][lo:hi].astype(np.int64), device=dev)] = True
            x = torch.as_tensor(cat["boards"][sl], device=dev).float()
            opp = torch.as_tensor(cat["opp"][sl].astype(np.int64), device=dev)
            mv = torch.as_tensor(cat["played"][sl].astype(np.int64), device=dev)[:, None]
            lp = []
            for c in (strong, weak):
                logits, _, _ = models[s](x, torch.full((n,), c, device=dev), opp)
                lp.append(torch.log_softmax(logits.float().masked_fill(~mask, -1e9), -1).gather(1, mv).squeeze(1))
            diff = (lp[0] - lp[1]).cpu().numpy()
            np.add.at(total, (cat["game"][sl], cat["side"][sl]), diff)
            np.add.at(count, (cat["game"][sl], cat["side"][sl]), 1)
            stats["pos"] += n

    ctx = mp.get_context("spawn")
    with ctx.Pool(args.workers, initializer=_init, initargs=(moves,)) as pool:
        done = 0
        for start, n, res in pool.imap(work, chunks(args.pgn, 200)):
            done += n
            if res is not None:
                for s in (0, 1):
                    keep = res["speed"] == s
                    if keep.any():
                        sel = {k: v[keep] for k, v in res.items() if k not in ("legal", "speed")}
                        lens = res["legal_len"].astype(np.int64)
                        offs = np.concatenate([[0], np.cumsum(lens)])
                        sel["legal"] = np.concatenate([res["legal"][offs[i]:offs[i + 1]] for i in np.flatnonzero(keep)])
                        pending[s].append(sel)
                    flush(s)
            el = time.time() - stats["t0"]
            print(f"\r{done}/{n_games} games, {stats['pos'] / max(el, 1e-9):.0f} positions/s, "
                  f"~{(n_games - done) * el / max(done, 1) / 60:.0f} min left   ", end="", flush=True)
    for s in (0, 1):
        flush(s, force=True)
    print()
    with np.errstate(invalid="ignore"):
        return total / np.maximum(count, 1), count


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pgn", required=True)
    ap.add_argument("--drop-high", type=float, default=0.02, help="drop the top fraction: suspiciously strong")
    ap.add_argument("--drop-low", type=float, default=0.02, help="drop the bottom fraction: suspiciously weak")
    ap.add_argument("--min-moves", type=int, default=15, help="scored moves a player needs before they can be flagged")
    ap.add_argument("--skip-plies", type=int, default=16, help="opening plies not scored")
    ap.add_argument("--max-moves", type=int, default=40, help="scored moves per player, at most")
    ap.add_argument("--batch", type=int, default=4096, help="positions per GPU batch")
    ap.add_argument("--workers", type=int, default=max(1, min(16, (os.cpu_count() or 2) - 2)),
                    help="CPU processes parsing games")
    ap.add_argument("--rescore", action="store_true", help="ignore cached scores")
    args = ap.parse_args()
else:  # spawned workers only need the move-selection settings
    args = argparse.Namespace(**json.loads(os.environ["MAIA_FILTER_ARGS"]))

if __name__ == "__main__":
    os.environ["MAIA_FILTER_ARGS"] = json.dumps(dict(skip_plies=args.skip_plies, max_moves=args.max_moves))
    cache = args.pgn + ".maia_scores.npz"
    n_games = sum(1 for line in open(args.pgn, encoding="utf-8") if line.startswith("[Event "))
    key = dict(skip_plies=args.skip_plies, max_moves=args.max_moves)
    if os.path.exists(cache) and not args.rescore and json.loads(str(np.load(cache)["key"])) == key:
        z = np.load(cache)
        idx, count = z["index"], z["count"]
        print(f"{n_games} games; using cached scores from {cache}")
    else:
        print(f"{n_games} games; scoring with Maia-2 ({args.workers} CPU workers + GPU)")
        idx, count = score(n_games)
        np.savez(cache, index=idx, count=count, key=json.dumps(key))

    ok = count >= args.min_moves
    vals = idx[ok]
    hi = np.quantile(vals, 1 - args.drop_high) if args.drop_high > 0 else np.inf
    lo = np.quantile(vals, args.drop_low) if args.drop_low > 0 else -np.inf
    flag_hi = ok & (idx > hi)
    flag_lo = ok & (idx < lo)
    drop = (flag_hi | flag_lo).any(1)
    pct = np.percentile(vals, [1, 5, 25, 50, 75, 95, 99])
    print(f"strength index over {ok.sum()} player-games with >= {args.min_moves} scored moves:\n"
          f"  percentiles 1/5/25/50/75/95/99: " + " ".join(f"{p:+.3f}" for p in pct) + "\n"
          f"  too strong: > {hi:+.3f} ({flag_hi.sum()} player-games)   too weak: < {lo:+.3f} ({flag_lo.sum()})")

    acct = args.pgn + ".accounts.json"
    names = []
    for text in games(args.pgn):
        w = text.split('[White "', 1)[1].split('"', 1)[0] if '[White "' in text else ""
        b = text.split('[Black "', 1)[1].split('"', 1)[0] if '[Black "' in text else ""
        names.append((w.lower(), b.lower()))
    if os.path.exists(acct):
        status = json.load(open(acct, encoding="utf-8"))
        marked = np.array([[status.get(n) == "marked" for n in pair] for pair in names]) & ok
        if marked.any():
            caught = (flag_hi & marked).sum()
            print(f"  Lichess-marked cheaters (of the accounts looked up so far): {marked.sum()} player-games, "
                  f"{caught} ({caught / marked.sum():.0%}) flagged too strong, "
                  f"median index {np.median(idx[marked]):+.3f}")

    out_path = os.path.splitext(args.pgn)[0] + ".maia-clean.pgn"
    kept = 0
    with open(out_path, "w", encoding="utf-8") as out:
        for i, text in enumerate(games(args.pgn)):
            if not drop[i]:
                out.write(text)
                kept += 1
    print(f"kept {kept} games, dropped {drop.sum()} ({drop.mean():.2%}) -> {out_path}")
