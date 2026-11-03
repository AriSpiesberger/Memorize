"""The labellers, one module per concept family. Each has:

    VERSION    bumped whenever a rule changes (goes in the manifest)
    DEFS       {concept: its definition, in words}
    labels(board, game=None) -> {concept: True / False / None}; None: the concept does not apply to this position, and
               it is neither a positive nor a negative

board carries its move stack; game is {"future": [the next moves, UCI, up to plans.HORIZON]} and only plans reads it.

A SPARSE family (openings: too many concepts to list per position) returns only its True concepts, and has
applicable(board): where it applies, a concept it does not return is False; elsewhere it is None.
"""

from . import imbalances, openings, pieces, plans, structures

FAMILIES = {"pieces": pieces, "openings": openings, "structures": structures, "imbalances": imbalances, "plans": plans}
