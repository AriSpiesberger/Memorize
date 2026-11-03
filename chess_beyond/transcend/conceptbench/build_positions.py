"""The position set: held-out games plus a month no model trained on, at most --per-game positions per game, split by game.

    python transcend/conceptbench/build_positions.py --fresh data/lichess/2026-09.head.pgn.zst

Two sources:
  held-out   data/pgn_probe/population.jsonl: make_pgn_data.py's held-out games of the 1000-1300 and 2400+ training data.
             Their later moves are known only as far as the game's last sampled position, so plans.py labels fewer.
  fresh      a Lichess month after every model's training data (all read months up to 2025-06), for more strategic
             positions: rated, both players at least --min-elo, base time at least --min-base seconds. In a game
             reaching a structure too rare for plain sampling (structures.RARE), the positions come from the plies in
             one (at most --per-game); any other game gives --plain positions at random plies. Which positions are
             taken depends only on headers and pawn structures, never on the plans the game goes on to play.
             `enriched` marks these positions.

Positions start at ply --min-ply, as the population does, always have a next move in the game, and fit in the model's context.

-> data/transcend/conceptbench/positions.parquet, one row per position: pos_id, game_id, source, split, ply, move_number,
   prompt (the full move prefix as the model reads it), fen, side, phase, material_balance (White minus Black, pawn
   units), material_total, enriched, future (the next plans.HORIZON moves, UCI, comma-separated, as far as known).
"""

import argparse
import io
import json
import multiprocessing as mp
import random
import re
import sys
import time
import zlib
from pathlib import Path

import chess

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bench import DATA, POSITIONS, material, paths, phase_of, prompt_of, sans_of, split_of
from labels import plans, structures

CTX = 1024
MAX_MOVE_CHARS = 8
COMMENT = re.compile(r"\{[^}]*\}")
NUMBER = re.compile(r"\d+\.(\.\.)?")
RESULTS = {"1-0", "0-1", "1/2-1/2"}
VOCAB = set(" #+-.0123456789;=BKNOQRabcdefghx/")


def row(board, sans, ply, game_id, source, ucis, enriched):
    """One position: board is the position after sans[:ply]."""
    w, b = material(board, chess.WHITE), material(board, chess.BLACK)
    return dict(game_id=game_id, source=source, split=split_of(game_id), ply=ply, move_number=board.fullmove_number,
                prompt=prompt_of(sans[:ply]), fen=board.fen(), side="white" if board.turn == chess.WHITE else "black",
                phase=phase_of(board), material_balance=w - b, material_total=w + b, enriched=enriched,
                future=",".join(ucis[ply:ply + plans.HORIZON]))


def replay(sans):
    """The boards after each ply (index = ply) and the moves in UCI, or None for a game that does not parse."""
    b = chess.Board()
    boards, ucis = [b.copy(stack=False)], []
    try:
        for s in sans:
            m = b.parse_san(s)
            ucis.append(m.uci())
            b.push(m)
            boards.append(b.copy(stack=False))
    except ValueError:
        return None, None
    return boards, ucis


def sample_game(job):
    """A fresh game (site, movetext, per_game, plain, min_ply) -> its positions."""
    site, text, per_game, plain, min_ply = job
    sans = [t.rstrip("?!") for t in NUMBER.sub(" ", COMMENT.sub(" ", text)).split()]
    sans = [t for t in sans if t and t not in RESULTS and t != "*"]
    if len(sans) <= min_ply or set("".join(sans)) - VOCAB:
        return []
    boards, ucis = replay(sans)
    if boards is None:
        return []
    fits = [p for p in range(min_ply, len(sans)) if len(prompt_of(sans[:p])) + MAX_MOVE_CHARS + 1 <= CTX]
    named = [p for p in fits if structures.rare_structure(boards[p])]
    rng = random.Random(zlib.crc32(site.encode()))
    plies, enriched = (rng.sample(named, min(per_game, len(named))), True) if named \
        else (rng.sample(fits, min(plain, len(fits))), False)
    return [row(boards[p], sans, p, f"lichess-{site}", "2026-09", ucis, enriched) for p in sorted(plies)]


def fresh_games(path, min_elo, min_base):
    """(site, movetext) of the games passing the header filters, reading until the file ends (a truncated head is fine)."""
    import zstandard
    head, moves = {}, []
    read = 0

    def done():
        nonlocal read
        read += 1
        tc = head.get("TimeControl", "-").split("+")[0]
        ok = (head.get("Result") in RESULTS and tc.isdigit() and int(tc) >= min_base
              and all(head.get(k, "?").isdigit() and int(head[k]) >= min_elo for k in ("WhiteElo", "BlackElo")))
        return (head["Site"].rsplit("/", 1)[-1], " ".join(moves)) if ok else None

    with open(path, "rb") as f:
        text = io.TextIOWrapper(zstandard.ZstdDecompressor().stream_reader(f, read_across_frames=True), encoding="utf-8", errors="replace")
        try:
            for line in text:
                if line.startswith("["):
                    if moves:
                        g = done()
                        if g:
                            yield g
                        head, moves = {}, []
                    k, _, v = line[1:].partition(" ")
                    head[k] = v.strip().rstrip("]").strip('"')
                elif line.strip():
                    moves.append(line.strip())
        except zstandard.ZstdError:
            print("end of the truncated file", flush=True)
    print(f"{read} games read from {path}", flush=True)


def held_out(path, min_ply):
    """The population's rows -> positions, with each game's later moves as far as its last sampled position shows them."""
    rows = [json.loads(line) for line in open(path, encoding="utf-8")]
    games = {}
    for r in rows:
        games.setdefault((r["band"], r["game"]), []).append(r)
    out = []
    for (band, g), rs in games.items():
        rs.sort(key=lambda r: r["ply"])
        known = sans_of(rs[-1]["prompt"]) + [rs[-1]["next_san"]]
        boards, ucis = replay(known)
        if boards is None:
            continue
        for r in rs:
            if r["ply"] < min_ply or len(r["prompt"]) + MAX_MOVE_CHARS + 1 > CTX:
                continue
            if prompt_of(known[:r["ply"]]) != r["prompt"] or boards[r["ply"]].fen() != r["fen"]:
                sys.exit(f"population game {band}/{g} ply {r['ply']}: prefix and row disagree")
            out.append(row(boards[r["ply"]], known, r["ply"], f"held-{band}-{g}", f"held-{band}", ucis, False))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fresh", required=True, help="a Lichess month's .pgn.zst, or its first bytes")
    ap.add_argument("--population", default=str(paths.DATA / "pgn_probe" / "population.jsonl"))
    ap.add_argument("--target", type=int, default=200_000)
    ap.add_argument("--per-game", type=int, default=10)
    ap.add_argument("--plain", type=int, default=2, help="positions from a fresh game with no named structure")
    ap.add_argument("--min-ply", type=int, default=10)
    ap.add_argument("--min-elo", type=int, default=1800)
    ap.add_argument("--min-base", type=int, default=600)
    ap.add_argument("--workers", type=int, default=16)
    a = ap.parse_args()
    import pyarrow as pa
    import pyarrow.parquet as pq
    t0 = time.time()
    rows = held_out(a.population, a.min_ply)
    print(f"{len(rows)} held-out positions from {len({r['game_id'] for r in rows})} games", flush=True)
    need = a.target - len(rows)
    jobs = ((s, t, a.per_game, a.plain, a.min_ply) for s, t in fresh_games(a.fresh, a.min_elo, a.min_base))
    fresh, games = [], 0
    with mp.Pool(a.workers) as pool:
        for got in pool.imap_unordered(sample_game, jobs, chunksize=64):
            games += 1
            fresh += got
            if games % 5000 == 0:
                print(f"  {games} fresh games, {len(fresh)} positions, {time.time() - t0:.0f}s", flush=True)
            if len(fresh) >= need:
                pool.terminate()
                break
    if len(fresh) < need:
        print(f"WARNING: the fresh file ran out at {len(fresh)} positions, {need} wanted", flush=True)
    rows += fresh
    for i, r in enumerate(rows):
        r["pos_id"] = i
    if any(c > a.per_game for c in _per_game(rows)):
        sys.exit("a game with too many positions")
    DATA.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(rows), POSITIONS, compression="zstd")
    sp = sum(r["split"] == "test" for r in rows)
    print(f"{len(rows)} positions, {len({r['game_id'] for r in rows})} games, {games} fresh games used, "
          f"{sum(r['enriched'] for r in rows)} from structure plies; test share {sp / len(rows):.3f} -> {POSITIONS} "
          f"({(time.time() - t0) / 60:.1f} min)", flush=True)


def _per_game(rows):
    from collections import Counter
    return Counter(r["game_id"] for r in rows).values()


if __name__ == "__main__":
    main()
