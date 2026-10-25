"""Lichess identifiers, shared by the data scripts (puzzle_strata.py, make_pgn_data.py). Standard library only."""


def game_id(url):
    """Lichess game id from a Site header or a puzzle's GameUrl (https://lichess.org/<id>[/black][#ply])."""
    return url.split("lichess.org/", 1)[-1].split("/")[0].split("#")[0][:8]
