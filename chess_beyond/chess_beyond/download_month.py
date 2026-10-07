"""Download a Lichess monthly database over several connections, resumably.

    python download_month.py --month 2025-06            # -> ../../data/lichess/2025-06.pgn.zst

Lichess throttles each connection (under 1 MB/s at times), so the file is split
into --parts byte ranges fetched in parallel, then joined. Rerun the same command
after an interruption and each part resumes where it stopped.
"""
import argparse
import os
import sys
import threading
import time
import urllib.request

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--month", required=True, help="YYYY-MM")
ap.add_argument("--parts", type=int, default=8)
ap.add_argument("--out", default=None, help="default: ../../data/lichess/<month>.pgn.zst")
args = ap.parse_args()

url = f"https://database.lichess.org/standard/lichess_db_standard_rated_{args.month}.pgn.zst"
out = args.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "lichess",
                               f"{args.month}.pgn.zst")
out = os.path.abspath(out)
os.makedirs(os.path.dirname(out), exist_ok=True)
if os.path.exists(out):
    sys.exit(f"{out} already exists")

size = int(urllib.request.urlopen(urllib.request.Request(url, method="HEAD")).headers["Content-Length"])
step = -(-size // args.parts)
ranges = [(i * step, min(size, (i + 1) * step) - 1) for i in range(args.parts)]
parts = [f"{out}.part{i}" for i in range(args.parts)]
have = lambda i: os.path.getsize(parts[i]) if os.path.exists(parts[i]) else 0


def fetch(i):
    lo, hi = ranges[i]
    while have(i) < hi - lo + 1:
        try:
            req = urllib.request.Request(url, headers={"Range": f"bytes={lo + have(i)}-{hi}"})
            with urllib.request.urlopen(req, timeout=60) as r, open(parts[i], "ab") as f:
                while chunk := r.read(1 << 20):
                    f.write(chunk)
        except Exception as e:                      # dropped connection: resume from the part's size
            print(f"\npart {i}: {e}; retrying", file=sys.stderr, flush=True)
            time.sleep(5)


threads = [threading.Thread(target=fetch, args=(i,), daemon=True) for i in range(args.parts)]
for t in threads:
    t.start()
t0, start = time.time(), sum(have(i) for i in range(args.parts))
while any(t.is_alive() for t in threads):
    time.sleep(2)
    got = sum(have(i) for i in range(args.parts))
    rate = (got - start) / max(time.time() - t0, 1e-9)
    eta = (size - got) / rate / 60 if rate else float("inf")
    print(f"\r{got / 1e9:6.2f}/{size / 1e9:.2f} GB  {rate / 1e6:5.1f} MB/s  ~{eta:.0f} min left   ",
          end="", flush=True)

print("\njoining parts")
with open(out + ".tmp", "wb") as f:
    for p in parts:
        with open(p, "rb") as src:
            while chunk := src.read(1 << 24):
                f.write(chunk)
assert os.path.getsize(out + ".tmp") == size, "size mismatch; rerun to resume"
os.replace(out + ".tmp", out)
for p in parts:
    os.remove(p)
print("done:", out)
