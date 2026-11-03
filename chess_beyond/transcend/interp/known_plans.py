"""Book plans on the concept map: the latents the dynamic bench (conceptbench/traj.py) found tracking a plan through
human games, each shown as a good example the way the map shows its mined concepts, one position twice.

    python transcend/interp/known_plans.py            # GPU, minutes: results/transcend/overnight/<name>-known.json
    python transcend/interp/concept_graph.py page     # the map, with the known plans in it

Which plans. Per model (W or S alone through the L11 4096-latent crosscoder, conceptbench's cc4096-Wview / -Sview: the
map's crosscoder), the plan's best single latent from the dynamic bench, kept as a good example when
    it clears its null by at least MIN_GAP (J - null J on test games),
    it is on the map (a node: matched across crosscoder seeds),
    it is not the best latent of MAX_SHARED or more plans of that model clearing MIN_SHARED (then it is a general latent,
    not this plan's), and the demonstration below finds at least one pair.
The demonstration. At the beginning of the plan in a held-out human game (the position before the latent comes on, in
the run that is on at the plan's first move), the model plays ROLLOUTS lines of HORIZON plies (T = 1, both sides). A pair
from that one position: the plan line, where the plan is carried out by plan_book's rule (starting within 8 plies) and the latent is on before its
first move (or right after it, when the plan starts at once),
against the other line, where the latent stays off for OFF_FOR plies and none of the plan's moves comes in HORIZON plies (and the game goes on that long): something else
happens. The two lines start with different moves. Preferred: the latent at MIN_ON or more, then on before the plan's
first move, then the largest gap in the latent over the first
OFF_FOR plies, up to N_PAIRS positions from different games. The latent's value is shown in units of its mean when on
(capped at 3), as the map shows a concept's. Pairs whose latent stays under MIN_ON before the plan are dropped, and a
plan left with none is left out.

    python transcend/interp/known_plans.py --relabel  # the cards and that rule applied again to the -known.json already made
"""
import argparse
import json
import sys
import time
from pathlib import Path

import chess
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # chess_beyond/
import paths  # noqa: E402  also puts transcend/'s folders on sys.path

sys.path.insert(0, str(paths.ROOT / "transcend" / "conceptbench"))
from labels import plan_book  # noqa: E402

TRES = paths.ROOT / "results" / "transcend" / "conceptbench" / "traj"
TDATA = paths.DATA / "transcend" / "conceptbench" / "traj"
TACTS = paths.RUNS / "transcend" / "conceptbench" / "traj" / "acts"
BACTS = paths.RUNS / "transcend" / "conceptbench" / "acts"
CC = paths.RUNS / "transcend" / "crosscoder" / "mixed-L11" / "cc-L11-4096" / "cc.pt"
RES = paths.ROOT / "results" / "transcend" / "overnight"
MODELS = {"W": "Arisp/chess-pgn-1000-1300", "S": "Arisp/chess-pgn-2400plus"}
BAND = {"W": "1000–1300", "S": "2400+"}
MIN_GAP, MAX_SHARED, MIN_SHARED = 0.15, 3, 0.05
ROLLOUTS, HORIZON, OFF_FOR, N_PAIRS, CANDIDATES = 64, 12, 6, 3, 40
MIN_ON = 0.5        # the latent, before the plan's first move, at least this (units of its mean when on)


def choose(name):
    """[(model, plan, latent, result row)] of the good examples' candidates, and the node index of each latent."""
    g = json.loads((RES / f"{name}-graph.json").read_text(encoding="utf-8"))
    node = {n["latent"]: i for i, n in enumerate(g["nodes"])}
    out = []
    for m in "WS":
        res = json.loads((TRES / f"cc4096-{m}view" / "L11.json").read_text(encoding="utf-8"))
        rows = {k: v for k, v in res.items() if k.startswith("plan_") and v.get("real") and v.get("null")}
        gap = {k: v["real"]["J"] - v["null"]["J"] for k, v in rows.items()}
        uses = {}
        for k, v in rows.items():
            if gap[k] >= MIN_SHARED:
                uses.setdefault(v["real"]["unit"]["unit"], []).append(k)
        for k, v in rows.items():
            u = v["real"]["unit"]["unit"]
            if gap[k] >= MIN_GAP and u in node and len(uses.get(u, [])) < MAX_SHARED:
                out.append((m, k, u, v, sorted(uses.get(u, []))))
    return out, node


def latent_scale(m, u):
    """The latent's mean when on, over the bench's positions (its unit on the page)."""
    import scipy.sparse as sp
    A = sp.load_npz(TACTS / f"cc4096-{m}view" / "L11.npz").tocsc()
    col = A[:, u]
    return A, float(col.data.mean()) if col.nnz else 1.0


def plan_line(plan, boards, moves):
    """A line's plan moves by plan_book's rule: the first played by a side in the structure, each next within GAP plies
    of the one before, valid with MIN_MOVES, MIN_DISTINCT and REQUIRED. -> (valid, index of the first, indices of all,
    any plan move at all by a side in the structure)."""
    p = plan_book.PLANS[plan[5:]]
    marks = [(i, next(k for k, f in p.marks.items() if f(b, m, b.turn)), b.turn) for i, (b, m) in enumerate(zip(boards, moves))
             if any(f(b, m, b.turn) for f in p.marks.values())]
    started = [x for x in marks if p.structure(boards[x[0]], x[2])]
    if not started:
        return False, None, [], False
    i0, _, c = started[0]
    chain = [x for x in marks if x[2] == c and x[0] >= i0]
    keep = [chain[0]]
    for x in chain[1:]:
        if x[0] - keep[-1][0] > plan_book.GAP:
            break
        keep.append(x)
    ids = {k for _, k, _ in keep}
    valid = len(keep) >= p.min_moves and len(ids) >= p.min_distinct and set(p.required) <= ids
    return valid, i0, [i for i, _, _ in keep], True


def candidates(plan, on, pos, lab):
    """Branch positions: in test games, the position before the latent comes on in the run that is on at the plan's
    first move. -> [(pos_id, game_id)]"""
    y = lab
    first = np.flatnonzero((y == 2) & (pos["split"].to_numpy() == "test"))
    games = pos["game_id"].to_numpy()
    out, seen = [], set()
    for f in first:
        if not on[f] or games[f] in seen:
            continue
        s = f
        while s - 1 >= 0 and games[s - 1] == games[f] and on[s - 1]:
            s -= 1
        x = s - 1
        if x < 0 or games[x] != games[f]:
            continue
        seen.add(games[f])
        out.append((int(x), games[f]))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", default="night1")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--relabel", action="store_true", help="only write the cards of the -known.json already made again")
    a = ap.parse_args()
    if a.relabel:
        return relabel(a.name)
    import pandas as pd
    import torch
    import eval as ev
    import shared as gd
    from crosscoder import CrossCoder
    from concept_mine import nums
    t0 = time.time()
    picks, node = choose(a.name)
    print(f"{len(picks)} candidate good examples: " + ", ".join(f"{m} {k[5:]} ({u})" for m, k, u, _, _ in picks), flush=True)
    pos = pd.read_parquet(TDATA / "positions.parquet", columns=["game_id", "split", "ply", "prompt", "fen"])
    lab = pd.read_parquet(TDATA / "labels.parquet", columns=sorted({k for _, k, _, _, _ in picks}))
    dev = ev.device("auto")
    ck = torch.load(CC, map_location="cpu", weights_only=False)
    cc = CrossCoder(2, ck["d"], ck["latents"], ck["k"]).to(dev)
    cc.load_state_dict(ck["state"])
    scales = ck["scales"].to(dev)
    fit_mean = {m: torch.from_numpy(np.load(BACTS / m / "L11.stats.npz")["mean"]).float().to(dev) for m in "WS"}
    rng = np.random.default_rng(a.seed)
    concepts, featured = [], []
    for m in "WS":
        mine = [p for p in picks if p[0] == m]
        if not mine:
            continue
        model = ev.load(MODELS[m], dev)[0]
        vi = 0 if m == "W" else 1

        def latent(states, u, mu):
            """The latent's value at these states of model m alone (the other model at its mean), in units of mu."""
            x = torch.zeros((len(states), 2, ck["d"]), device=dev)
            x[:, vi] = states.to(dev).float() * scales[vi]
            x[:, 1 - vi] = fit_mean["SW"[vi]] * scales[1 - vi]
            with torch.no_grad():
                f, _, _ = cc.encode(x)
            return np.minimum(f[:, u].cpu().numpy() / mu, 3.0)

        for _, plan, u, row, shared_with in mine:
            A, mu = latent_scale(m, u)
            on = np.zeros(A.shape[0], bool)
            on[A[:, u].indices] = True
            cands = candidates(plan, on, pos, lab[plan].to_numpy())
            rng.shuffle(cands)
            pairs = []
            for x, gid in cands[:CANDIDATES]:
                pr0, fen0 = pos["prompt"].iloc[x], pos["fen"].iloc[x]
                if len(pr0) + HORIZON * 7 + 10 > model.ctx:
                    continue
                lines = [dict(board=chess.Board(fen0), prompt=pr0, moves=[], sans=[], acts=[], boards=[], mvs=[]) for _ in range(ROLLOUTS)]
                for t in range(HORIZON):
                    live = [l for l in lines if not l["board"].is_game_over()]
                    if not live:
                        break
                    legal, lp, st = gd.policy(model, [l["board"] for l in live], dev, [l["prompt"] for l in live], grab=("11",))
                    if t > 0:
                        v = latent(st["11"], u, mu)
                        for l, z in zip(live, v):
                            l["acts"].append(float(z))
                    for l, mv_, p_ in zip(live, legal, lp):
                        mv = mv_[gd.sample(np.array(p_), 1.0, rng)]
                        l["boards"].append(l["board"].copy(stack=False))
                        l["mvs"].append(mv)
                        gd.advance(l, mv)
                live = [l for l in lines if l["sans"]]
                _, _, st = gd.policy(model, [l["board"] for l in live if not l["board"].is_game_over()], dev,
                                     [l["prompt"] for l in live if not l["board"].is_game_over()], grab=("11",))
                v = iter(latent(st["11"], u, mu)) if st else iter([])
                for l in live:
                    l["acts"].append(float(next(v)) if not l["board"].is_game_over() else 0.0)
                first = {}
                for l in live:
                    first.setdefault(l["sans"][0], []).append(l)
                onl, offl = [], []
                for l in live:
                    valid, i0, idx, anyp = plan_line(plan, l["boards"], l["mvs"])
                    l["marks"], l["first"] = idx, i0
                    # the plan line: a valid plan starting in view, the latent on before its first move (or right after it)
                    l["strength"] = max(l["acts"][:max(i0, 1)] or [0]) if valid else 0
                    if valid and i0 <= 8 and l["strength"] > 0:
                        onl.append(l)
                    # the other line: none of the plan's moves, the latent off for OFF_FOR plies
                    elif not anyp and len(l["sans"]) == HORIZON and max(l["acts"][:OFF_FOR] or [1]) == 0:
                        offl.append(l)
                best = None
                for c_ in onl:
                    for s_ in offl:
                        if c_["sans"][0] == s_["sans"][0]:
                            continue
                        key = (c_["strength"] >= MIN_ON, c_["first"] >= 1, float(np.mean(c_["acts"][:OFF_FOR]) - np.mean(s_["acts"][:OFF_FOR])))
                        if best is None or key > best[0]:
                            best = (key, c_, s_)
                if best is None:
                    continue
                (_, _, gap), c_, s_ = best
                b0 = chess.Board(fen0)
                n_c, n_s = len(first[c_["sans"][0]]), len(first[s_["sans"][0]])
                pairs.append(dict(kind="known", split="held-out human game", pos=int(x), band=f"{BAND[m]} model's lines from a human game",
                                  t=1, k=OFF_FOR - 1, chosen=c_["sans"][0], subpar=s_["sans"][0], wc=round(n_c / len(live), 3),
                                  ws=round(n_s / len(live), 3), node=len(live), fen=fen0,
                                  uc=b0.parse_san(c_["sans"][0]).uci(), us=b0.parse_san(s_["sans"][0]).uci(),
                                  cline=nums(fen0, c_["sans"]), sline=nums(fen0, s_["sans"]),
                                  cact=[round(z, 2) for z in c_["acts"]], sact=[round(z, 2) for z in s_["acts"]],
                                  gap=round(gap, 3), persist=len(c_["sans"]), lc="plan line", ls="something else", cmark=c_["marks"],
                                  strength=round(c_["strength"], 2), faint=bool(c_["strength"] < MIN_ON), game=str(gid)))
                if len(pairs) == N_PAIRS:
                    break
            print(f"  {m} {plan}: latent {u}, {len(pairs)} pairs from {min(len(cands), CANDIDATES)} positions tried "
                  f"({time.time() - t0:.0f}s)", flush=True)
            pairs = [q for q in pairs if not q["faint"]]
            for q in pairs:
                q.pop("faint")
            if not pairs:
                continue
            p = plan_book.PLANS[plan[5:]]
            x, nl = row["real"], row["null"]
            cid = f"{m}-{plan[5:].upper().replace('_', '-')}"
            concepts.append(dict(id=cid, model=m, lat=[node[u]], latent=[u], w=[1.0], covered=1.0, k95=1,
                                 positions=x["test_episodes"], tier="known", theme=p.doc, persistence=None,
                                 on_at_split=len(pairs), match="", match_cos=0.0, absent=False, windows=[], bps=[],
                                 pairs=pairs, known=dict(plan=plan, J=round(x["J"], 3), null=round(nl["J"], 3),
                                                         J_ci=[round(v, 3) for v in x["J_ci"]], coverage=round(x["coverage"], 3),
                                                         false=round(x["false"], 3), persistence=round(x["persistence"], 3),
                                                         episodes=x["test_episodes"], shared_with=shared_with)))
        del model
        torch.cuda.empty_cache()
    write(a.name, concepts)
    print(f"({time.time() - t0:.0f}s)", flush=True)


def write(name, concepts):
    """The good examples, each plan's card text (its short name, its rule, its score), and its twin in the other model."""
    featured = []
    for c in concepts:
        k = c["known"]
        p, u = plan_book.PLANS[k["plan"][5:]], c["latent"][0]
        also = [x for x in k["shared_with"] if x != k["plan"]]
        featured.append(dict(id=c["id"], known=True, title=plan_book.NAMES[k["plan"][5:]],
                             look="Left: from the start of the plan the latent comes on before the plan is played. "
                                  "Right: from the same position the latent stays off and something else happens.",
                             also=(f"The plan: {p.doc}. Latent {u} tracks it through held-out human games: score {k['J']:.2f} "
                                   f"[{k['J_ci'][0]:.2f}, {k['J_ci'][1]:.2f}] against {k['null']:.2f} by chance (labels shifted). "
                                   + (f"It is also the best latent for: {', '.join(plan_book.NAMES[x[5:]] for x in also)}." if also else ""))))
    for c in concepts:                                  # the same plan in the other model: its twin
        t = next((d for d in concepts if d["model"] != c["model"] and d["known"]["plan"] == c["known"]["plan"]), None)
        c["match"], c["match_cos"] = (t["id"], 1.0 if t["latent"] == c["latent"] else 0.9) if t else ("", 0.0)
    RES.mkdir(parents=True, exist_ok=True)
    out = RES / f"{name}-known.json"
    out.write_text(json.dumps(dict(note=__doc__.split("\n\n")[0], concepts=concepts, featured=featured)), encoding="utf-8")
    print(f"wrote {out}: {len(concepts)} good examples", flush=True)


def relabel(name):
    """The -known.json already made, with weak pairs (and plans left with none) dropped and the cards written again."""
    k = json.loads((RES / f"{name}-known.json").read_text(encoding="utf-8"))
    out = []
    for c in k["concepts"]:
        c["pairs"] = [q for q in c["pairs"] if q.get("strength", MIN_ON) >= MIN_ON]
        for q in c["pairs"]:
            q.pop("faint", None)
        c["known"].pop("faint", None)
        if c["pairs"]:
            c["on_at_split"] = len(c["pairs"])
            out.append(c)
    write(name, out)


if __name__ == "__main__":
    main()
