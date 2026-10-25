"""Confidence intervals for the rates chess_beyond reports (puzzles solved, moves found)."""
import math


def wilson(k, n, z=1.96):
    """95% Wilson score interval for k successes in n trials, as (low, high)."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))
