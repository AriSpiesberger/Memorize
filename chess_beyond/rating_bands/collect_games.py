"""Stream a Lichess monthly database and keep games per rating band.

    python rating_bands/collect_games.py --month 2025-06 --pgn data/lichess/2025-06.pgn.zst

Reads https://database.lichess.org/ over HTTP and decompresses on the fly, so
the ~30 GB file is never stored. A game is kept when it is rapid or classical
(--min-base seconds or more) and BOTH players fall in the same band. Each band
goes to its own PGN (data/lichess/bands/2025-06/1300-1700.pgn by default),
and the stream stops once every band is full.

Games are filtered on raw bytes with three regexes (no python-chess), so the
bottleneck is the download.
"""
import argparse
import os
import re
import sys
import time
import urllib.request

import zstandard

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # chess_beyond/: common.py, paths.py, search.py
import paths

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--month", required=True, help="YYYY-MM")
ap.add_argument("--bands", default="0,1000,1300,1700,2000,2300,4000",
                help="band edges: consecutive pairs are [low, high)")
ap.add_argument("--per-band", type=int, default=50000, help="games to keep per band")
ap.add_argument("--min-base", type=int, default=600, help="minimum base time in seconds (600 = rapid and up)")
ap.add_argument("--out", default=None, help="default: data/lichess/bands/<month>")
ap.add_argument("--pgn", default=None, help="read a local .pgn.zst instead of streaming")
args = ap.parse_args()

edges = [int(x) for x in args.bands.split(",")]
bands = [(lo, hi) for lo, hi in zip(edges, edges[1:])]
name = lambda b: f"{b[0]}-{b[1]}" if b[1] < 4000 else f"{b[0]}+"
out_dir = args.out or str(paths.LICHESS / "bands" / args.month)
os.makedirs(out_dir, exist_ok=True)
files = {b: open(os.path.join(out_dir, f"{name(b)}.pgn"), "w", encoding="utf-8") for b in bands}
kept = {b: 0 for b in bands}


def band_of(we, be):
    for b in bands:
        if b[0] <= we < b[1] and b[0] <= be < b[1]:
            return b
    return None


if args.pgn:
    raw = open(args.pgn, "rb")
else:
    url = f"https://database.lichess.org/standard/lichess_db_standard_rated_{args.month}.pgn.zst"
    raw = urllib.request.urlopen(url)
stream = zstandard.ZstdDecompressor().stream_reader(raw, read_across_frames=True)

TC = re.compile(rb'\[TimeControl "(\d+)')
WE = re.compile(rb'\[WhiteElo "(\d+)"')
BE = re.compile(rb'\[BlackElo "(\d+)"')


def keep(game):
    """Band for a game (bytes) worth keeping, else None. Cheapest test first:
    most games are bullet or blitz."""
    m = TC.search(game, 0, 2000)
    if not m or int(m.group(1)) < args.min_base or b'[Variant "' in game[:2000]:
        return None
    w, b = WE.search(game, 0, 2000), BE.search(game, 0, 2000)
    if not (w and b):
        return None
    band = band_of(int(w.group(1)), int(b.group(1)))
    return band if band and kept[band] < args.per_band else None


t0, seen, last, buf = time.time(), 0, 0.0, b""
done = False
while not done:
    chunk = stream.read(1 << 24)                     # 16 MB of PGN at a time
    buf += chunk
    games = buf.split(b"\n[Event ")
    buf = b"" if not chunk else games.pop()          # last piece may be cut off; keep it for the next chunk
    for i, g in enumerate(games):
        if not g.strip():
            continue
        if not g.startswith(b"[Event "):
            g = b"[Event " + g
        seen += 1
        band = keep(g)
        if band:
            files[band].write(g.decode("utf-8", "replace").rstrip("\n") + "\n\n")
            kept[band] += 1
            if all(n >= args.per_band for n in kept.values()):
                done = True
                break
    if not chunk:
        break
    if time.time() - last > 2:
        last = time.time()
        status = "  ".join(f"{name(k)} {v}" for k, v in kept.items())
        print(f"\r{seen / 1e6:6.2f}M games read  {seen / (last - t0):7.0f}/s  |  {status}   ",
              end="", file=sys.stderr, flush=True)

for f in files.values():
    f.close()
print(f"\nread {seen} games in {(time.time() - t0) / 60:.1f} min; kept per band:")
for b, n in kept.items():
    print(f"  {name(b):>10}  {n}")
print("written to", os.path.abspath(out_dir))
