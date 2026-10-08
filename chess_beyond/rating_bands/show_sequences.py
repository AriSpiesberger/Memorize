"""Show the hardest winning sequences in a stratified set, as moves you can read.

    python rating_bands/show_sequences.py --labels data/lichess/bands/2025-06-blitz/labels

Picks positions where the model (out of fold) predicts players below --low-rating
almost never play the idea, yet a strong player in the data did: found the only
move AND kept the advantage over their next two moves. Prints each sequence in
SAN with the opponent's replies, the predicted rate by rating and a Lichess link.
"""
import argparse
import io
import json
import os
import re

import chess
import chess.pgn

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--labels", required=True)
ap.add_argument("--target", default="idea3")
ap.add_argument("--band", default="2300+", help="band whose players found the idea")
ap.add_argument("--low-rating", type=int, default=1500, help="predicted rate at this rating must be tiny")
ap.add_argument("--max-low", type=float, default=0.06, help="max predicted rate at --low-rating")
ap.add_argument("--n", type=int, default=12)
args = ap.parse_args()

rows = [json.loads(l) for l in open(os.path.join(args.labels, f"strata_{args.target}.jsonl"))]
pick = [r for r in rows if r["band"] == args.band and r[args.target]
        and r["predicted"][str(args.low_rating)] <= args.max_low]
pick.sort(key=lambda r: (r["predicted"][str(args.low_rating)], -r["predicted"]["2500"]))
print(f"{len(pick)} positions: a {args.band} player played the idea, predicted <= {args.max_low:.0%} at "
      f"{args.low_rating}\n")
pick = pick[:args.n]

# pull the games' moves from the band PGN (scan headers, parse only the games we need)
want = {r["link"].split("#")[0]: r for r in pick}
games = {}
pgn_path = os.path.join(os.path.dirname(args.labels.rstrip("/\\")), f"{args.band}.pgn")
with open(pgn_path, encoding="utf-8") as f:
    text, site = [], None
    for line in f:
        if line.startswith("[Event ") and text:
            if site in want:
                games[site] = chess.pgn.read_game(io.StringIO("".join(text)))
                if len(games) == len(want):
                    break
            text, site = [], None
        text.append(line)
        m = re.match(r'\[Site "(.*)"\]', line)
        if m:
            site = m.group(1)

for r in pick:
    site, ply = r["link"].split("#")
    g = games.get(site)
    if g is None:
        continue
    nodes = list(g.mainline())
    i = int(ply) - 1
    board = nodes[i].parent.board()
    seq = []
    for k in range(i, min(len(nodes), i + 5)):
        b = nodes[k].parent.board()
        san = b.san(nodes[k].move)
        mover = (k - i) % 2 == 0
        seq.append(f"{'' if mover else '('}{san}{'' if mover else ')'}")
    side = "White" if board.turn == chess.WHITE else "Black"
    num = board.fullmove_number
    pred = "  ".join(f"{k}:{v:.0%}" for k, v in r["predicted"].items())
    print(f"{side} to move ({num}{'.' if side == 'White' else '...'}), {r['elo']} player, "
          f"{', '.join(r['move_type'])}{', gives ' + str(r['gives_material']) + ' material' if r['gives_material'] else ''}")
    print(f"  sequence: {' '.join(seq)}      (opponent replies in brackets)")
    print(f"  predicted rate: {pred}   floor {r['floor']:.0%}   engine gap to 2nd best {r['gap_cp']} cp")
    print(f"  {r['fen']}")
    print(f"  {site}#{ply}\n")
