"""Drop games involving accounts Lichess has marked for cheating.

    python transcend/filter_cheaters.py --pgn data/lichess/bands/2025-06-train/1000-1300.pgn

Every player name in the PGN is looked up with Lichess's public bulk-user API
(POST https://lichess.org/api/users, 300 names per request). Lichess marks
accounts caught using engine help with "tosViolation"; accounts closed for any
reason come back "disabled" or are missing. By default games with a marked player
are dropped; --drop-closed also drops games with closed accounts (many of those
are just people who closed their account, so it's off by default).

Requests are paced: the gap between them starts at --interval, widens after a
429 (Lichess asks for a full minute's pause) and narrows again while requests
succeed. A personal API token (lichess.org/account/oauth/token, no scopes needed)
raises the limit: pass --token or set LICHESS_TOKEN.

Lookups are cached in <pgn>.accounts.json after every request, so an
interrupted run (Ctrl-C is fine) resumes where it stopped. Writes
<pgn stem>.clean.pgn next to the input and prints how many games were dropped.
Only public usernames are sent; nothing else leaves the machine.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--pgn", required=True)
ap.add_argument("--drop-closed", action="store_true", help="also drop games with closed/missing accounts")
ap.add_argument("--batch", type=int, default=300, help="names per API request (Lichess allows 300)")
ap.add_argument("--interval", type=float, default=2.0, help="starting seconds between requests")
ap.add_argument("--token", default=os.environ.get("LICHESS_TOKEN"), help="Lichess API token (or set LICHESS_TOKEN)")
args = ap.parse_args()

cache_path = args.pgn + ".accounts.json"
status = json.load(open(cache_path, encoding="utf-8")) if os.path.exists(cache_path) else {}    # name (lower) -> marked/closed/ok

NAME = re.compile(r'^\[(White|Black) "(.*)"\]')
names = set()
with open(args.pgn, encoding="utf-8") as f:
    for line in f:
        m = NAME.match(line)
        if m:
            names.add(m.group(2))
todo = sorted(n for n in names if n.lower() not in status)
print(f"{len(names)} players, {len(todo)} still to look up ({len(todo) // args.batch + 1} requests), "
      f"{'signed in with a token' if args.token else 'anonymous (no token: lower rate limit)'}")


headers = {"Content-Type": "text/plain", "Accept": "application/json"}
if args.token:
    headers["Authorization"] = f"Bearer {args.token}"
gap, last = args.interval, 0.0          # seconds between requests, adapted to Lichess's limit


def save():
    tmp = cache_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(status, f)
    os.replace(tmp, cache_path)


def lookup(batch):
    global gap, last
    req = urllib.request.Request("https://lichess.org/api/users", data=",".join(batch).encode(), headers=headers)
    while True:
        time.sleep(max(0.0, last + gap - time.time()))
        last = time.time()
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                users = json.load(r)
            gap = max(args.interval, gap * 0.9)       # creep back toward the starting pace
            return users
        except urllib.error.HTTPError as e:
            if e.code == 429:                     # rate limited: Lichess asks for a full minute's pause
                gap = min(gap * 2, 60.0)
                print(f"\n  rate limited, waiting 60s, then one request every {gap:.0f}s", flush=True)
                time.sleep(60)
            elif e.code == 401:
                sys.exit("Lichess rejected the token (401); check --token / LICHESS_TOKEN")
            else:
                raise
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"\n  {e}; retrying in 10s", flush=True)
            time.sleep(10)


t0 = time.time()
for i in range(0, len(todo), args.batch):
    batch = todo[i:i + args.batch]
    found = {u["id"]: u for u in lookup(batch)}
    for n in batch:
        u = found.get(n.lower())
        status[n.lower()] = ("marked" if u and u.get("tosViolation") else
                             "closed" if (u is None or u.get("disabled")) else "ok")
    save()
    done = i + len(batch)
    rate = done / max(time.time() - t0, 1e-9)
    print(f"\r{done}/{len(todo)} looked up  ~{(len(todo) - done) / rate / 60:.0f} min left, "
          f"1 request / {gap:.1f}s   ", end="", flush=True)
save()
counts = {k: sum(v == k for v in status.values()) for k in ("ok", "marked", "closed")}
print(f"\naccounts: {counts}")

bad = {"marked", "closed"} if args.drop_closed else {"marked"}
out_path = os.path.splitext(args.pgn)[0] + ".clean.pgn"
kept = dropped = 0
with open(args.pgn, encoding="utf-8") as f, open(out_path, "w", encoding="utf-8") as out:
    game, players = [], []
    for line in f:
        if line.startswith("[Event ") and game:
            if any(status.get(p.lower()) in bad for p in players):
                dropped += 1
            else:
                out.write("".join(game)); kept += 1
            game, players = [], []
        game.append(line)
        m = NAME.match(line)
        if m:
            players.append(m.group(2))
    if game:
        if any(status.get(p.lower()) in bad for p in players):
            dropped += 1
        else:
            out.write("".join(game)); kept += 1
print(f"kept {kept} games, dropped {dropped} ({dropped / max(kept + dropped, 1):.2%}) -> {out_path}")
