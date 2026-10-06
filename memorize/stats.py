"""Paired comparison of two runs on the same questions.

When two models answer the same questions, only the questions where they
disagree carry information about which is better. McNemar's exact test asks
whether the wrong-to-right and right-to-wrong flips are lopsided enough to
rule out chance.
"""

import math


def mcnemar(before, after):
    """`before` and `after` are equal-length lists of 0/1 correctness on the
    same questions. Returns the change in accuracy, its 95% interval, the flip
    counts and the exact two-sided p-value."""
    n = len(before)
    gained = sum(1 for b, a in zip(before, after) if not b and a)
    lost = sum(1 for b, a in zip(before, after) if b and not a)
    flips = gained + lost
    if flips:
        k = min(gained, lost)
        tail = sum(math.comb(flips, i) for i in range(k + 1)) / 2**flips
        p = min(1.0, 2 * tail)
    else:
        p = 1.0
    delta = (gained - lost) / n
    se = math.sqrt(max(flips - (gained - lost) ** 2 / n, 0.0)) / n
    return {
        "n": n,
        "delta": delta,
        "ci95": (delta - 1.96 * se, delta + 1.96 * se),
        "gained": gained,
        "lost": lost,
        "p": p,
    }


def describe(result):
    lo, hi = result["ci95"]
    return (
        f"{result['delta']:+.1%} [{lo:+.1%}, {hi:+.1%}]  "
        f"+{result['gained']}/-{result['lost']} flips  p={result['p']:.3f}"
    )
