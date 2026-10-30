"""Skill facts: what separates strong play from weak in a position and its move, from Stockfish and Maia-2.

predicates.py says what is on the board (a hanging piece, a pin, a check). These say what it takes:
whether there is only one good move, how deep you must search to find it, whether the move gives
material back for something the engine sees, whether it answers a threat, how much it loses, and how
likely an 1100-level or a 2000+ player is to play it (Maia-2, the human-move model).

    from skill import NAMES, TEXT, Annotator, maia_probs, facts
    with Annotator(depth=14) as an:                   # one Stockfish process
        e = an.annotate(board, move)                  # engine numbers for one position and move
    m = maia_probs([(board, move), ...])              # Maia-2 probabilities, batched on the GPU
    facts(e, m_row)                                   # -> list of bools, one per NAMES entry

Win chances are Lichess's win% from the side to move's point of view (0-100), so "loses 15 points"
means the move drops the mover's win chances by 15 percentage points against the engine's best.
"""
import logging
import math
import random
import time

import chess
import chess.engine
import numpy as np

import paths

logging.getLogger("chess.engine").setLevel(logging.ERROR)   # null-move searches warn about history

MATE = 100_000
VALUE = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
SHARP = 15            # win-% points the best move beats the runner-up by: "only one good move"
DEEP = 10             # search depth from which the best move is first the engine's choice: "deep"
SAC = 2               # pawns' worth of material given up along the engine line: a sacrifice
THREAT = 20           # win-% points a free extra move would gain them: "they have a threat"
KEEP = 5              # win-% points a move may lose and still count as keeping the evaluation
BLUNDER = 15          # win-% points lost: a blunder (INACCURATE: 5 to 15)
RARE = 0.05           # Maia-2 probability below which a move is rare for a rating
# win chances (%) between which a position is undecided. Outside them "keeps the evaluation" means
# little (a lost side has nothing left to lose), so a sacrifice or meeting a threat only counts inside.
OPEN = (10, 90)

DEFS = [
    # the position
    ("winning", "the side to move is winning (win chance 75%+)"),
    ("losing", "the side to move is losing (win chance 25% or less)"),
    ("sharp", f"there is only one good move (the best is {SHARP}+ win-% points better than the runner-up)"),
    ("threat", f"they have a threat (moving again now would gain them {THREAT}+ win-% points)"),
    ("best_is_deep", f"the best move is clearly best but only the engine's choice from depth {DEEP} on"),
    ("best_rare_for_1100", f"the best move is one 1100-level players rarely play (Maia-2 below {RARE:.0%})"),
    ("best_is_quiet", "the best move is quiet (no capture, check or promotion)"),
    # the move played
    ("move_best", f"the move is the engine's best (or within 2 win-% points of it)"),
    ("move_only", "the move is the only good move"),
    ("move_deep", f"the move is clearly best and only found from depth {DEEP} on"),
    ("move_quiet_best", "the move is a quiet best move in a position with only one good move"),
    ("move_sound_sacrifice", f"the move gives up {SAC}+ pawns' worth along the engine line and keeps the evaluation "
                             f"(position undecided: win chance {OPEN[0]}-{OPEN[1]}%)"),
    ("move_meets_threat", f"they had a threat and the move keeps the evaluation (position undecided: win chance "
                          f"{OPEN[0]}-{OPEN[1]}%)"),
    ("move_inaccurate", f"the move loses {KEEP}-{BLUNDER} win-% points"),
    ("move_blunder", f"the move loses {BLUNDER}+ win-% points"),
    ("move_rare_for_1100", f"1100-level players rarely play the move (Maia-2 below {RARE:.0%})"),
    ("move_strong_player", "2000+ players are 3x likelier than 1100s to play the move (Maia-2, and 10%+ at 2000+)"),
]
NAMES = [n for n, _ in DEFS]
TEXT = dict(DEFS)
SHORT = dict(winning="winning", losing="losing", sharp="one good move", threat="facing a threat",
             best_is_deep="best move is deep", best_rare_for_1100="best move rare for 1100s",
             best_is_quiet="best move is quiet", move_best="best move", move_only="only move", move_deep="deep move",
             move_quiet_best="quiet only move", move_sound_sacrifice="sound sacrifice", move_meets_threat="meets the threat",
             move_inaccurate="inaccuracy", move_blunder="blunder", move_rare_for_1100="rare for 1100s",
             move_strong_player="a 2000+ move")       # labels for the pages


def win(cp):
    """Lichess's win% for a centipawn score (mates as +/- MATE)."""
    return 50 + 50 * (2 / (1 + math.exp(-0.00368208 * max(-2000, min(2000, cp)))) - 1)


def material(b, color):
    return sum(VALUE[p.piece_type] for p in b.piece_map().values() if p.color == color)


class Annotator:
    """One Stockfish process (use one per worker). annotate() runs up to three searches:
    the position with two lines (best, runner-up, depth to find), the played move alone (its value
    and engine line), and, when not in check, a null move (what they would do if we passed)."""

    def __init__(self, depth=14, threat_depth=8, engine=None, hash_mb=64):
        self.depth, self.threat_depth = depth, threat_depth
        self.path, self.hash_mb = engine or paths.stockfish(), hash_mb
        self.start()

    def start(self, tries=6):
        """Launch Stockfish. Many workers starting at once can fail on Windows (exit code 0xC0000142,
        a process that could not initialise), so wait a random moment and retry."""
        for t in range(tries):
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(self.path)
                self.engine.configure({"Threads": 1, "Hash": self.hash_mb})
                return
            except (chess.engine.EngineError, OSError):
                if t == tries - 1:
                    raise
                time.sleep(0.5 + 2 * random.random() * (t + 1))

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        try:
            self.engine.quit()
        except chess.engine.EngineError:
            pass

    def score(self, info, turn):
        return info["score"].pov(turn).score(mate_score=MATE)

    def annotate(self, board, move):
        """Engine numbers for a position and the move played from it (move may be None); None if
        Stockfish keeps failing on it. A dead engine is restarted."""
        for attempt in range(2):
            try:
                return self._annotate(board, move)
            except (chess.engine.EngineError, chess.engine.EngineTerminatedError):
                try:
                    self.engine.quit()
                except Exception:
                    pass
                self.start()
        return None

    def _annotate(self, board, move):
        b = board.copy(stack=False)
        us = b.turn
        top, lines = {}, {}
        with self.engine.analysis(b, chess.engine.Limit(depth=self.depth), multipv=2, game=object()) as an:
            for info in an:
                if not info.get("pv") or "depth" not in info or "score" not in info:
                    continue
                if info.get("lowerbound") or info.get("upperbound"):
                    continue
                k = info.get("multipv", 1)
                if k == 1:
                    top[info["depth"]] = info["pv"][0]
                if k not in lines or info["depth"] >= lines[k][0]:
                    lines[k] = (info["depth"], info["pv"], self.score(info, us))
        if 1 not in lines:                                        # no legal move
            return None
        best_pv, best_cp = lines[1][1], lines[1][2]
        best = best_pv[0]
        second_cp = lines[2][2] if 2 in lines else None
        # the depth from which the best move stays the engine's choice (not the first depth it shows up)
        found_at = 1 + max((d for d, m in top.items() if m != best), default=0)
        e = dict(wp=win(best_cp), best=best.uci(), best_quiet=not (b.is_capture(best) or b.gives_check(best) or best.promotion),
                 gap=win(best_cp) - win(second_cp) if second_cp is not None else 0.0, found_at=found_at)
        # a threat: if we passed, how much better would they stand than they do now?
        e["threat"] = 0.0
        if not b.is_check():
            b.push(chess.Move.null())
            try:
                info = self.engine.analyse(b, chess.engine.Limit(depth=self.threat_depth), game=object())
                e["threat"] = win(self.score(info, not us)) - (100 - e["wp"])
            except chess.engine.EngineError:
                pass
            b.pop()
        if move is None:
            return e
        if move == best:
            pv, cp = best_pv, best_cp
        else:
            info = self.engine.analyse(b, chess.engine.Limit(depth=self.depth), root_moves=[move], game=object())
            pv, cp = info.get("pv", [move]), self.score(info, us)
        e.update(move=move.uci(), loss=max(0.0, e["wp"] - win(cp)),
                 quiet=not (b.is_capture(move) or b.gives_check(move) or move.promotion))
        # material we are down after the engine's line (at most 6 plies), compared with now
        before = material(b, us) - material(b, not us)
        line = b.copy(stack=False)
        for mv in pv[:6]:
            if not line.is_legal(mv):
                break
            line.push(mv)
        e["gives"] = before - (material(line, us) - material(line, not us)) if len(pv) >= 4 else 0
        return e


def maia_probs(pairs, batch=2048, rating_low=1000, rating_high=2100, model_type="rapid"):
    """Maia-2's probability of each (board, move) at a low and a high rating (opponent at the same
    rating), and of the engine's best move when given as a third item: rows of
    (p_low(move), p_high(move), p_low(best)). Needs torch, a GPU is best, and the maia2 package."""
    import torch
    from maia2 import inference as I2
    from maia2 import model as M2
    from maia import elo_cat, encode
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    m2 = M2.from_pretrained(type=model_type, device=dev, save_root=str(paths.MAIA2)).eval()
    moves, _, _ = I2.prepare()
    mirror = lambda mv: chess.Move(chess.square_mirror(mv.from_square), chess.square_mirror(mv.to_square), mv.promotion)
    out = np.full((len(pairs), 3), np.nan, dtype=np.float32)
    with torch.inference_mode():
        for s in range(0, len(pairs), batch):
            part = pairs[s:s + batch]
            X, legal, pick, best = [], [], [], []
            for p in part:
                b, mv = p[0], p[1]
                bb = b if b.turn == chess.WHITE else b.mirror()
                fix = (lambda m: m) if b.turn == chess.WHITE else mirror
                X.append(encode(bb))
                legal.append([moves[x.uci()] for x in bb.legal_moves])
                pick.append(moves[fix(mv).uci()] if mv is not None else -1)
                best.append(moves[fix(p[2]).uci()] if len(p) > 2 and p[2] is not None else -1)
            mask = torch.zeros((len(part), len(moves)), dtype=torch.bool, device=dev)
            for r, lg in enumerate(legal):
                mask[r, lg] = True
            x = torch.as_tensor(np.stack(X), device=dev).float()
            res = []
            for rating in (rating_low, rating_high):
                c = torch.full((len(part),), elo_cat(rating), device=dev)
                logits, _, _ = m2(x, c, c)
                res.append(torch.softmax(logits.float().masked_fill(~mask, -1e9), -1))
            ix = torch.arange(len(part), device=dev)
            pk, bs = torch.tensor(pick, device=dev), torch.tensor(best, device=dev)
            out[s:s + len(part), 0] = torch.where(pk >= 0, res[0][ix, pk.clamp_min(0)], torch.nan).cpu().numpy()
            out[s:s + len(part), 1] = torch.where(pk >= 0, res[1][ix, pk.clamp_min(0)], torch.nan).cpu().numpy()
            out[s:s + len(part), 2] = torch.where(bs >= 0, res[0][ix, bs.clamp_min(0)], torch.nan).cpu().numpy()
    return out


def facts(e, m):
    """One bool per NAMES entry, from annotate()'s numbers e and a maia_probs row m."""
    if e is None:
        return [False] * len(NAMES)
    has_move = "move" in e
    loss = e.get("loss", 0.0)
    best = has_move and loss <= 2
    undecided = OPEN[0] <= e["wp"] <= OPEN[1]
    p_low, p_high, p_best_low = (float(x) for x in m)
    v = dict(
        winning=e["wp"] >= 75,
        losing=e["wp"] <= 25,
        sharp=e["gap"] >= SHARP,
        threat=e["threat"] >= THREAT,
        best_is_deep=e["found_at"] >= DEEP and e["gap"] >= KEEP,
        best_rare_for_1100=p_best_low < RARE,
        best_is_quiet=e["best_quiet"],
        move_best=best,
        move_only=best and e["gap"] >= SHARP,
        move_deep=has_move and e["move"] == e["best"] and e["found_at"] >= DEEP and e["gap"] >= KEEP,
        move_quiet_best=best and e.get("quiet", False) and e["gap"] >= SHARP,
        move_sound_sacrifice=has_move and undecided and e["gives"] >= SAC and loss <= KEEP,
        move_meets_threat=has_move and undecided and e["threat"] >= THREAT and loss <= KEEP,
        move_inaccurate=has_move and KEEP <= loss < BLUNDER,
        move_blunder=has_move and loss >= BLUNDER,
        move_rare_for_1100=has_move and p_low < RARE,
        move_strong_player=has_move and p_high >= 0.10 and p_high >= 3 * p_low,
    )
    return [bool(v[n]) for n in NAMES]
