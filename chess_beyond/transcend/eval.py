"""Evaluate PGN models at several sampling temperatures, as in Transcendence (Zhang et al., 2024).

    python transcend/eval.py games     --model Arisp/chess-pgn-1000-1300
    python transcend/eval.py positions --model Arisp/chess-pgn-1000-1300
    python transcend/eval.py puzzles   --model Arisp/chess-pgn-1000-1300

--model is a Hugging Face repo (model.safetensors + config.json) or a local .pt checkpoint.
Stockfish comes from tools/stockfish/ or $STOCKFISH (paths.stockfish()).

How a move is chosen. The model writes PGN one character at a time, and the temperature
T divides every character's logits (the paper's sampling). Rather than generating and
retrying when the result is illegal, every legal move is scored: its probability is the
product of its characters' tempered probabilities (the SAN and the closing space). The
move is drawn from these probabilities renormalised over the legal moves, which is
exactly where "sample, and resample while illegal" ends up; at low T it is the best
legal move, so an illegal first choice falls through to the next one. Illegal moves are
never losses. "illegal mass" is the probability the model put on strings that are not
a legal move, i.e. the chance a single unconstrained sample would have been illegal.

games      The model plays Lichess's Stockfish AI levels (fishnet's skill, depth and move
           time per level) from --openings openings taken from held-out games, each with
           both colours; a game is drawn at --max-plies. Rated with Glicko-2 against the
           levels whose rating Transcendence measured (1: 1552, 3: 1842, 5: 2142); the
           other levels are reported as scores only.
positions  Held-out game positions: Stockfish scores every legal move once (cached), then
           per temperature: top-1/3/5 (the move played is among the model's k most likely),
           expected win % of the model's choice, win % lost against the best move, and
           the illegal mass.
puzzles    The first --n puzzles of each set (data/lichess/puzzles/pool/1050 and
           strata/2400, 2600, 2800). The model needs the game that led to the puzzle, so
           each source game is fetched once from the Lichess API and cached. Solved = every
           solver move, opponent replies given, a different mating move also counts.
           Rated with the Lichess puzzle formula. The pool puzzles used here must be kept
           out of any later RL training (their ids are in the output).

Results: results/transcend/eval/<model>-<kind>.json, and a table on stdout.
"""
import argparse
import json
import math
import queue
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import chess
import chess.engine
import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # chess_beyond/
import paths
from intervals import wilson
from pgn_model import MAX_MOVE_CHARS, PGNTransformer, encode, load_pgn_model, prompt
from pgn_probe import DEFAULT as PROBE, parse_movetext, subset
from puzzles import fit_elo

TEMPS = [0.001, 0.01, 0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]
LEVELS = {1: (-9, 5, 0.05), 2: (-5, 5, 0.10), 3: (-1, 5, 0.15), 4: (3, 5, 0.20),     # Lichess AI level:
          5: (7, 5, 0.30), 6: (11, 8, 0.40), 7: (16, 13, 0.50), 8: (20, 22, 1.00)}  # (skill, depth, seconds)
RATED = {1: (1552, 45.2), 3: (1842, 45.2), 5: (2142, 59.0)}                        # Transcendence's calibration
PUZZLE_SETS = {"1050": "pool/1050.jsonl", "2400": "strata/2400.jsonl", "2600": "strata/2600.jsonl",
               "2800": "strata/2800.jsonl"}
OUT = paths.ROOT / "results" / "transcend" / "eval"


# ---------------------------------------------------------------- model and move choice

def load(spec, dev):
    """A local .pt checkpoint, or a Hugging Face repo id with model.safetensors and config.json."""
    if Path(spec).suffix == ".pt":
        return load_pgn_model(spec, dev).eval(), Path(spec).stem
    from huggingface_hub import snapshot_download
    from safetensors.torch import load_file
    try:                                    # already downloaded: no network (HF connections drop often)
        path = Path(snapshot_download(spec, local_files_only=True))
        if not all((path / f).exists() for f in ("config.json", "model.safetensors")):
            raise FileNotFoundError(path)   # e.g. a new commit (a README edit) whose files aren't cached
    except Exception:
        for attempt in range(1, 7):
            try:
                path = Path(snapshot_download(spec))
                break
            except Exception as e:
                if attempt == 6:
                    raise
                print(f"  download of {spec}: attempt {attempt} failed ({type(e).__name__}), retrying", flush=True)
                time.sleep(10)
    model = PGNTransformer(**json.loads((path / "config.json").read_text())["architecture"])
    model.load_state_dict(load_file(path / "model.safetensors"))
    return model.to(dev).eval(), spec.split("/")[-1]


@torch.no_grad()
def score(model, boards, temps, dev, max_tokens=300_000):
    """For each board: its legal moves and, per temperature, each move's log-probability
    (the sum over its characters of log softmax(logits / T)), not yet renormalised."""
    moves, seqs, owner, ncand = [], [], [], []
    for b, board in enumerate(boards):
        legal = list(board.legal_moves)
        moves.append(legal)
        p = encode(prompt(board))[-(model.ctx - MAX_MOVE_CHARS - 1):]
        for mv in legal:
            c = encode(board.san(mv) + " ")
            seqs.append((p, c))
            owner.append(b)
    out = np.zeros((len(temps), len(seqs)), dtype=np.float64)
    order = sorted(range(len(seqs)), key=lambda i: -len(seqs[i][0]) - len(seqs[i][1]))   # longest first
    s = 0
    while s < len(order):
        n = max(1, max_tokens // (len(seqs[order[s]][0]) + MAX_MOVE_CHARS + 1))         # sized by the longest
        idx = order[s:s + n]
        s += n
        L = max(len(seqs[i][0]) + len(seqs[i][1]) for i in idx)
        x = torch.zeros((len(idx), L), dtype=torch.long)
        for r, i in enumerate(idx):
            p, c = seqs[i]
            x[r, :len(p) + len(c)] = torch.tensor(p + c)
        x = x.to(dev)
        with torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev == "cuda"):
            feats = model.features(x)
        cut = torch.tensor([len(seqs[i][0]) for i in idx], device=dev)
        clen = torch.tensor([len(seqs[i][1]) for i in idx], device=dev)
        t = torch.arange(MAX_MOVE_CHARS + 1, device=dev)
        pos = (cut[:, None] - 1 + t[None, :]).clamp(max=L - 2)          # states that predict each character
        rows = torch.arange(len(idx), device=dev)[:, None]
        logits = model.head(feats[rows, pos]).float()                   # (n, chars, vocab)
        target = x[rows, pos + 1]
        valid = t[None, :] < clen[:, None]
        for k, T in enumerate(temps):
            lp = torch.log_softmax(logits / T, -1).gather(2, target[..., None])[..., 0]
            out[k, idx] = (lp * valid).sum(1).cpu().numpy()
    per = [[[] for _ in boards] for _ in temps]
    for i, b in enumerate(owner):
        for k in range(len(temps)):
            per[k][b].append(out[k, i])
    return moves, [[np.array(v) for v in row] for row in per]


def choose(logp, T, rng):
    """Index of the move drawn from logp renormalised over the legal moves, and the illegal mass."""
    p = np.exp(logp - logp.max())
    p /= p.sum()
    illegal = 1.0 - math.exp(min(0.0, float(np.logaddexp.reduce(logp))))
    return int(rng.choice(len(p), p=p)), illegal


def level_ratings(path):
    """{level: (rating, RD)} from calibrate_levels.py's file, or Transcendence's numbers if no path.
    RD is the 95% interval's half-width / 1.96; levels only bounded from below are left out."""
    if not path:
        return dict(RATED)
    rec = json.loads(Path(path).read_text())
    return {int(lv): (v["rating"], (v["ci95"][1] - v["ci95"][0]) / 3.92)
            for lv, v in rec["levels"].items() if not v.get("lower_bound_only")}


def device(name):
    if name != "auto":
        return name
    return "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"


def save(name, kind, record):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{name}-{kind}.json"
    path.write_text(json.dumps(record, indent=1))
    print(f"\nwrote {path.relative_to(paths.ROOT)}")


# ---------------------------------------------------------------- games against Stockfish

def glicko2(results, r=1500.0, rd=350.0, vol=0.06, tau=0.5):
    """One Glicko-2 rating period (Glickman 2012) from (opponent rating, opponent RD, score) triples."""
    q = 173.7178
    mu, phi = (r - 1500) / q, rd / q
    g = lambda ph: 1 / math.sqrt(1 + 3 * ph * ph / math.pi ** 2)
    terms = [(g(oRD / q), (oR - 1500) / q, s) for oR, oRD, s in results]
    E = [1 / (1 + math.exp(-gj * (mu - mj))) for gj, mj, _ in terms]
    v = 1 / sum(gj * gj * e * (1 - e) for (gj, _, _), e in zip(terms, E))
    delta = v * sum(gj * (s - e) for (gj, _, s), e in zip(terms, E))
    a = math.log(vol * vol)
    f = lambda x: (math.exp(x) * (delta ** 2 - phi ** 2 - v - math.exp(x)) / (2 * (phi ** 2 + v + math.exp(x)) ** 2)
                   - (x - a) / tau ** 2)
    A = a                                                   # the new volatility: Illinois iteration on f
    if delta ** 2 > phi ** 2 + v:
        B = math.log(delta ** 2 - phi ** 2 - v)
    else:
        k = 1
        while f(a - k * tau) < 0:
            k += 1
        B = a - k * tau
    fA, fB = f(A), f(B)
    while abs(B - A) > 1e-6:
        C = A + (A - B) * fA / (fB - fA)
        fC = f(C)
        if fC * fB <= 0:
            A, fA = B, fB
        else:
            fA /= 2
        B, fB = C, fC
    phi_star = math.sqrt(phi ** 2 + math.exp(A / 2) ** 2)
    phi_new = 1 / math.sqrt(1 / phi_star ** 2 + 1 / v)
    mu_new = mu + phi_new ** 2 * sum(gj * (s - e) for (gj, _, s), e in zip(terms, E))
    return 1500 + q * mu_new, q * phi_new


def openings(n, plies):
    """The first `plies` moves of n held-out games, alternating the two bands."""
    by_band = {}
    for r in _population():
        sans, games = parse_movetext(r["prompt"])[0], by_band.setdefault(r["band"], {})
        if len(sans) >= plies and r["game"] not in games and len(games) < n:
            games[r["game"]] = sans[:plies]
    out = [s for pair in zip(*(g.values() for g in by_band.values())) for s in pair][:n]
    if len(out) < n:
        raise SystemExit(f"only {len(out)} held-out games have {plies} plies")
    return out


def games(a):
    dev = device(a.device)
    model, name = load(a.model, dev)
    rng = np.random.default_rng(a.seed)
    starts = openings(a.openings, a.opening_plies)
    G = []                                                  # one dict per game
    for T in a.temps:
        for lv in a.levels:
            for sans in starts:
                for colour in (chess.WHITE, chess.BLACK):
                    b = chess.Board()
                    for s in sans:
                        b.push_san(s)
                    G.append(dict(T=T, level=lv, colour=colour, board=b, start=len(sans), illegal=[], result=None))
    engines = queue.Queue()
    for _ in range(a.workers):
        e = chess.engine.SimpleEngine.popen_uci(paths.stockfish())
        e.configure({"Threads": 1, "Hash": 16})
        engines.put(e)
    lo, hi = engines.queue[0].options["Skill Level"].min, engines.queue[0].options["Skill Level"].max
    if any(not lo <= LEVELS[lv][0] <= hi for lv in a.levels):
        print(f"note: this engine's Skill Level is {lo}..{hi}; Lichess's negative skills are clamped to {lo} "
              "(Fairy-Stockfish accepts them)")

    def engine_move(g):
        skill, depth, secs = LEVELS[g["level"]]
        e = engines.get()
        try:
            e.configure({"Skill Level": max(lo, min(hi, skill))})
            return e.play(g["board"], chess.engine.Limit(time=secs, depth=depth)).move
        finally:
            engines.put(e)

    t0, live = time.time(), list(G)
    with ThreadPoolExecutor(a.workers) as pool:
        while live:
            ours = [g for g in live if g["board"].turn == g["colour"]]
            theirs = [g for g in live if g["board"].turn != g["colour"]]
            if ours:
                temps = sorted({g["T"] for g in ours})
                moves, lp = score(model, [g["board"] for g in ours], temps, dev)
                for i, g in enumerate(ours):
                    j, illegal = choose(lp[temps.index(g["T"])][i], g["T"], rng)
                    g["illegal"].append(illegal)
                    g["board"].push(moves[i][j])
            for g, mv in zip(theirs, pool.map(engine_move, theirs)):
                g["board"].push(mv)
            for g in live:
                b = g["board"]
                if b.is_game_over(claim_draw=True) or len(b.move_stack) - g["start"] >= a.max_plies:
                    out = b.outcome(claim_draw=True)
                    g["result"] = 0.5 if out is None or out.winner is None else float(out.winner == g["colour"])
            live = [g for g in live if g["result"] is None]
            done = len(G) - len(live)
            print(f"\r{done}/{len(G)} games finished, {time.time() - t0:.0f}s", end="", flush=True)
    while not engines.empty():
        engines.get().quit()

    rated_by = level_ratings(a.level_ratings)
    record = dict(model=a.model, kind="games", levels=a.levels, openings=a.openings, opening_plies=a.opening_plies,
                  max_plies=a.max_plies, rated=rated_by, level_ratings=a.level_ratings, by_temperature={})
    used = sorted(lv for lv in a.levels if lv in rated_by)
    print(f"\n\n{name}: score per level, Glicko-2 rating (95%: R +/- 2 RD) over levels {used}")
    print(f"{'T':>6} " + "".join(f"{'L' + str(lv):>8}" for lv in a.levels) + f"{'rating':>16}{'illegal mass':>14}")
    for T in a.temps:
        row = dict(levels={})
        for lv in a.levels:
            r = [g["result"] for g in G if g["T"] == T and g["level"] == lv]
            row["levels"][lv] = dict(games=len(r), wins=r.count(1.0), draws=r.count(0.5), losses=r.count(0.0),
                                     score=sum(r) / len(r))
        rated = [(*rated_by[g["level"]], g["result"]) for g in G if g["T"] == T and g["level"] in rated_by]
        R, RD = glicko2(rated) if rated else (float("nan"), float("nan"))
        ill = [x for g in G if g["T"] == T for x in g["illegal"]]
        row.update(rating=R, rd=RD, illegal_mass=float(np.mean(ill)))
        record["by_temperature"][T] = row
        print(f"{T:>6} " + "".join(f"{row['levels'][lv]['score']:>8.2f}" for lv in a.levels)
              + f"{R:>9.0f} +/- {2 * RD:<4.0f}{100 * row['illegal_mass']:>12.2f}%")
    save(name, "games", record)


# ---------------------------------------------------------------- held-out positions

_pop = None


def _population():
    global _pop
    if _pop is None:
        _pop = [json.loads(l) for l in open(PROBE / "population.jsonl", encoding="utf-8")]
    return _pop


def board_of(sans):
    b = chess.Board()
    for s in sans:
        b.push_san(s)
    return b


def stockfish_table(rows, depth, workers):
    """Win % for the side to move after each legal move, per position (Stockfish, all moves, cached)."""
    cache_path = PROBE / f"stockfish_depth{depth}.jsonl"
    cache = {}
    if cache_path.exists():
        cache = {d["fen"]: d["win"] for d in map(json.loads, open(cache_path))}
    todo = [r for r in rows if r["fen"] not in cache]
    if todo:
        engines = queue.Queue()
        for _ in range(workers):
            engines.put(chess.engine.SimpleEngine.popen_uci(paths.stockfish()))

        def analyse(r):
            b = board_of(parse_movetext(r["prompt"])[0])
            e = engines.get()
            try:
                info = e.analyse(b, chess.engine.Limit(depth=depth), multipv=b.legal_moves.count())
            finally:
                engines.put(e)
            return r["fen"], {i["pv"][0].uci(): i["score"].pov(b.turn).wdl().expectation() for i in info}

        with ThreadPoolExecutor(workers) as pool, open(cache_path, "a") as f:
            for k, (fen, win) in enumerate(pool.map(analyse, todo), 1):
                cache[fen] = win
                f.write(json.dumps(dict(fen=fen, win=win)) + "\n")
                print(f"\rStockfish depth {depth}: {k}/{len(todo)} positions", end="", flush=True)
        print()
        while not engines.empty():
            engines.get().quit()
    return [cache[r["fen"]] for r in rows]


def positions(a):
    dev = device(a.device)
    model, name = load(a.model, dev)
    rows = [_population()[i] for i in subset(_population(), a.n)]
    win = stockfish_table(rows, a.depth, a.workers)
    record = dict(model=a.model, kind="positions", n=len(rows), depth=a.depth, by_temperature={})
    stats = {T: {band: [] for band in ("1000-1300", "2400+")} for T in a.temps}
    for s in range(0, len(rows), a.batch):
        part = rows[s:s + a.batch]
        boards = [board_of(parse_movetext(r["prompt"])[0]) for r in part]
        moves, lp = score(model, boards, a.temps, dev)
        for i, r in enumerate(part):
            played = boards[i].parse_san(r["next_san"])
            w = np.array([win[s + i].get(m.uci(), np.nan) for m in moves[i]])
            for k, T in enumerate(a.temps):
                logp = lp[k][i]
                p = np.exp(logp - logp.max())
                p /= p.sum()
                rank = int((logp > logp[moves[i].index(played)]).sum())    # log space: no ties from underflow
                ok = ~np.isnan(w)
                stats[T][r["band"]].append((rank < 1, rank < 3, rank < 5, float((p[ok] * w[ok]).sum() / p[ok].sum()),
                                            float(np.nanmax(w)), 1.0 - math.exp(min(0.0, float(np.logaddexp.reduce(logp))))))
        print(f"\r{min(s + a.batch, len(rows))}/{len(rows)} positions", end="", flush=True)
    print(f"\n\n{name}: held-out positions (Stockfish depth {a.depth}); win % is for the side to move")
    print(f"{'T':>6} {'games':>10} {'top-1':>7} {'top-3':>7} {'top-5':>7} {'exp. win %':>11} {'lost vs best':>13} {'illegal':>8}")
    for T in a.temps:
        record["by_temperature"][T] = {}
        for band, v in stats[T].items():
            v = np.array(v)
            m = dict(n=len(v), top1=v[:, 0].mean(), top3=v[:, 1].mean(), top5=v[:, 2].mean(), expected_win=v[:, 3].mean(),
                     lost_vs_best=(v[:, 4] - v[:, 3]).mean(), illegal_mass=v[:, 5].mean())
            record["by_temperature"][T][band] = m
            print(f"{T:>6} {band:>10} {100 * m['top1']:>6.1f}% {100 * m['top3']:>6.1f}% {100 * m['top5']:>6.1f}% "
                  f"{100 * m['expected_win']:>10.1f}% {100 * m['lost_vs_best']:>12.2f}% {100 * m['illegal_mass']:>7.2f}%")
    save(name, "positions", record)


# ---------------------------------------------------------------- puzzles

def _ssl():
    """certifi's certificates when installed (python.org builds on macOS ship without any)."""
    import ssl
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def histories(puzzles, token=None):
    """Each puzzle's game moves up to the puzzle position, fetched from Lichess once and cached."""
    from lichess_ids import game_id
    cache_path = paths.LICHESS / "puzzles" / "histories.jsonl"
    games = {}
    if cache_path.exists():
        games = {d["game"]: d["moves"] for d in map(json.loads, open(cache_path))}
    todo = sorted({game_id(p["game"]) for p in puzzles} - set(games))
    with open(cache_path, "a") as f:
        for s in range(0, len(todo), 300):
            ids = todo[s:s + 300]
            req = urllib.request.Request("https://lichess.org/api/games/export/_ids?moves=true&tags=false&clocks=false"
                                         "&evals=false&opening=false", data=",".join(ids).encode(), method="POST",
                                         headers={"Accept": "application/x-ndjson",
                                                  **({"Authorization": f"Bearer {token}"} if token else {})})
            while True:
                try:
                    body = urllib.request.urlopen(req, timeout=120, context=_ssl()).read().decode()
                    break
                except urllib.error.HTTPError as e:
                    if e.code != 429:
                        raise
                    print("\nLichess rate limit: waiting 60 s", flush=True)
                    time.sleep(60)
            for line in body.splitlines():
                g = json.loads(line)
                games[g["id"]] = g.get("moves", "").split()
                f.write(json.dumps(dict(game=g["id"], moves=games[g["id"]])) + "\n")
            for i in ids:                                   # deleted or private games: remember they're missing
                if i not in games:
                    games[i] = []
                    f.write(json.dumps(dict(game=i, moves=[])) + "\n")
            print(f"\rfetched {min(s + 300, len(todo))}/{len(todo)} source games", end="", flush=True)
    if todo:
        print()
    out = []
    for p in puzzles:
        b, key = chess.Board(), " ".join(p["fen"].split()[:4])
        for san in games[game_id(p["game"])]:
            if " ".join(b.fen().split()[:4]) == key:
                break
            b.push_san(san)
        out.append(b if " ".join(b.fen().split()[:4]) == key else None)
    return out


def puzzles(a):
    dev = device(a.device)
    model, name = load(a.model, dev)
    files = {k: f.replace("strata/", a.strata_dir.rstrip("/") + "/") for k, f in PUZZLE_SETS.items()}
    sets = {k: [json.loads(l) for _, l in zip(range(a.n), open(paths.LICHESS / "puzzles" / f, encoding="utf-8"))]
            for k, f in files.items()}
    flat = [(k, p) for k, ps in sets.items() for p in ps]
    starts = histories([p for _, p in flat], a.lichess_token)
    missing = sum(b is None for b in starts)
    flat = [(k, p, b) for (k, p), b in zip(flat, starts) if b is not None]
    print(f"{len(flat)} puzzles with their game history ({missing} source games unavailable or not matching)")
    record = dict(model=a.model, kind="puzzles", n_per_set=a.n, missing=missing, strata_dir=a.strata_dir,
                  samples=a.samples, pool_ids_used=[p["id"] for k, p, _ in flat if k == "1050"], by_temperature={})
    ks = [k for k in (1, 2, 4, 8, 16, 32, 64) if k <= a.samples]
    rng = np.random.default_rng(a.seed)
    print(f"\n{name}: puzzles solved (95% interval) and puzzle rating")
    print(f"{'T':>6} " + "".join(f"{k:>18}" for k in sets) + f"{'rating':>18}")
    # An attempt still alive has played exactly the solution line, so every live attempt on a puzzle, at every
    # temperature, is on the same board: one forward pass per puzzle per move, all attempts sampled from it.
    cur = []
    for k, p, b in flat:
        bb = b.copy()
        bb.push_uci(p["moves"][0])
        cur.append(dict(b=bb, i=1))
    oks = {T: [[None] * a.samples for _ in flat] for T in a.temps}
    live = list(range(len(flat)))
    while live:
        moves, lp = score(model, [cur[q]["b"] for q in live], a.temps, dev)
        for n, q in enumerate(live):
            c, sol = cur[q], flat[q][1]["moves"]
            want = chess.Move.from_uci(sol[c["i"]])
            c["b"].push(want)
            done = c["i"] + 1 >= len(sol) or c["b"].is_checkmate()
            for t, T in enumerate(a.temps):
                for r, ok in enumerate(oks[T][q]):
                    if ok is not None:
                        continue
                    mv = moves[n][choose(lp[t][n], T, rng)[0]]
                    if mv == want:
                        oks[T][q][r] = True if done else None
                    else:                                   # another mate also solves it
                        c["b"].pop()
                        c["b"].push(mv)
                        oks[T][q][r] = c["b"].is_checkmate()
                        c["b"].pop()
                        c["b"].push(want)
            if not done:
                c["b"].push_uci(sol[c["i"] + 1])
                c["i"] += 2
        live = [q for q in live if any(ok is None for T in a.temps for ok in oks[T][q])]
        print(f"\r  {len(live)} puzzles still being solved   ", end="", flush=True)
    print()
    for T in a.temps:
        state = [dict(set=k, p=p, q=q, ok=ok) for q, (k, p, _) in enumerate(flat) for ok in oks[T][q]]
        row = {}
        hits = np.zeros(len(flat), dtype=int)                  # successes per puzzle, out of a.samples
        for s in state:
            hits[s["q"]] += bool(s["ok"])
        for k in sets:
            r = [s["ok"] for s in state if s["set"] == k]
            row[k] = dict(n=len(r), solved=sum(r), rate=sum(r) / max(1, len(r)), ci95=wilson(sum(r), len(r)))
            if a.samples > 1:
                c = [int(hits[q]) for q, (kk, _, _) in enumerate(flat) if kk == k]
                row[k]["pass_at"] = {kk: float(np.mean([pass_at_k(a.samples, ci, kk) for ci in c])) for kk in ks}
                row[k]["puzzles"] = len(c)
        R, ci = fit_elo([s["p"]["rating"] for s in state], [s["ok"] for s in state])
        row["rating"], row["rating_ci95"] = R, ci
        record["by_temperature"][T] = row
        print(f"{T:>6} " + "".join(f"{100 * row[k]['rate']:>8.1f}% ({100 * row[k]['ci95'][0]:.0f}-{100 * row[k]['ci95'][1]:.0f})"
                                   for k in sets) + f"{R:>9.0f} ({ci[0]:.0f}-{ci[1]:.0f})")
        if a.samples > 1:
            for k in sets:
                print(f"{'':>6}   {k:>5} pass@" + "  ".join(f"{kk}: {100 * row[k]['pass_at'][kk]:5.1f}%" for kk in ks),
                      flush=True)
    save(name, "puzzles-pass" if a.samples > 1 else "puzzles", record)


def pass_at_k(n, c, k):
    """Unbiased pass@k from n attempts with c successes: 1 - C(n - c, k) / C(n, k)."""
    return 1.0 if n - c < k else 1.0 - math.comb(n - c, k) / math.comb(n, k)


def rerate(a):
    """Re-rate a finished `games` run with other level ratings, from its saved win/draw/loss counts."""
    name = Path(a.model).stem if Path(a.model).suffix == ".pt" else a.model.split("/")[-1]
    src = OUT / f"{name}-games.json"
    rec = json.loads(src.read_text())
    rated_by = level_ratings(a.level_ratings)
    levels = [int(lv) for lv in rec["levels"]]
    used = sorted(lv for lv in levels if lv in rated_by)
    print(f"{name}: {src.name} re-rated over levels {used} with "
          + ", ".join(f"L{lv}={rated_by[lv][0]:.0f}" for lv in used))
    print(f"{'T':>6} " + "".join(f"{'L' + str(lv):>8}" for lv in levels) + f"{'rating':>16}")
    out = dict(source=src.name, level_ratings=a.level_ratings, rated=rated_by, by_temperature={})
    for T, row in rec["by_temperature"].items():
        counts = {int(lv): c for lv, c in row["levels"].items()}
        res = []
        for lv in used:
            c = counts[lv]
            res += [(*rated_by[lv], 1.0)] * c["wins"] + [(*rated_by[lv], 0.5)] * c["draws"] \
                + [(*rated_by[lv], 0.0)] * c["losses"]
        R, RD = glicko2(res)
        out["by_temperature"][T] = dict(rating=R, rd=RD, levels=row["levels"])
        print(f"{float(T):>6} " + "".join(f"{counts[lv]['score']:>8.2f}" for lv in levels)
              + f"{R:>9.0f} +/- {2 * RD:<4.0f}")
    save(name, "games-rerated", out)


# ---------------------------------------------------------------- command line

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
sub = ap.add_subparsers(dest="kind", required=True)
for kind, fn in (("games", games), ("positions", positions), ("puzzles", puzzles), ("rerate", rerate)):
    p = sub.add_parser(kind)
    p.set_defaults(fn=fn)
    p.add_argument("--model", required=True, help="Hugging Face repo id or a local .pt checkpoint")
    p.add_argument("--temps", type=float, nargs="+", default=TEMPS)
    p.add_argument("--device", default="auto", help="auto, cuda, mps or cpu")
    p.add_argument("--seed", type=int, default=0)
    if kind in ("games", "rerate"):
        p.add_argument("--level-ratings", default=None,
                       help="calibrate_levels.py output (level ratings vs Maia-2); default: Transcendence's 1552/1842/2142")
    if kind == "games":
        p.add_argument("--levels", type=int, nargs="+", default=[1, 3, 5, 7, 8], choices=sorted(LEVELS))
        p.add_argument("--openings", type=int, default=50, help="openings, each played with both colours, per level")
        p.add_argument("--opening-plies", type=int, default=8)
        p.add_argument("--max-plies", type=int, default=300, help="plies after the opening before a draw is called")
        p.add_argument("--workers", type=int, default=8, help="Stockfish processes (one core each)")
    if kind == "positions":
        p.add_argument("--n", type=int, default=2000, help="held-out positions, half from each band")
        p.add_argument("--depth", type=int, default=12)
        p.add_argument("--workers", type=int, default=8)
        p.add_argument("--batch", type=int, default=64)
    if kind == "puzzles":
        p.add_argument("--n", type=int, default=2000, help="puzzles per set")
        p.add_argument("--samples", type=int, default=1,
                       help="attempts per puzzle; > 1 also reports pass@1, 2, 4, 8, 16 ... (written to <model>-puzzles-pass.json)")
        p.add_argument("--lichess-token", default=None, help="optional; raises the API rate limit")
        p.add_argument("--strata-dir", default="strata",
                       help="folder under data/lichess/puzzles/ with 2400/2600/2800.jsonl; use the strata built "
                            "with the model's training games excluded (on a home PC: strata-pgn, copied from Modal)")

if __name__ == "__main__":
    args = ap.parse_args()
    args.fn(args)
