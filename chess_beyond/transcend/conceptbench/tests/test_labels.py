"""Each labeller on hand-chosen positions, present and absent.

    python -m unittest discover -s transcend/conceptbench/tests
"""

import sys
import unittest
from pathlib import Path

import chess

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bench import board_of, material, phase_of, prompt_of, split_of, sans_of
from labels import imbalances, openings, pieces, plans, stockfish_terms, structures

START = chess.STARTING_FEN


def check(case, module, table):
    """table: (fen, concept, expected)."""
    for fen, concept, want in table:
        with case.subTest(fen=fen, concept=concept):
            case.assertEqual(module.labels(chess.Board(fen))[concept], want)


class Pieces(unittest.TestCase):
    def test_table(self):
        check(self, pieces, [
            (START, "white_has_queen", True),
            ("rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNB1KBNR w KQkq - 0 1", "white_has_queen", False),
            (START, "black_bishop_pair", True),
            ("rn1qkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "black_bishop_pair", False),
            (START, "white_rooks_2", True),
            (START, "white_rooks_1", False),
            ("4k3/8/8/8/8/8/8/R3K3 w - - 0 1", "white_rooks_1", True),
            ("4k3/8/8/8/8/8/8/R3K3 w - - 0 1", "black_rooks_0", True),
            (START, "white_minors_4", True),
            ("4k3/8/4n3/8/8/4B3/8/1N2K3 w - - 0 1", "white_minors_2", True),
            ("4k3/8/4n3/8/8/4B3/8/1N2K3 w - - 0 1", "black_minors_1", True),
            ("4k3/8/4n3/8/8/4B3/8/1N2K3 w - - 0 1", "black_minors_2", False),
            (START, "white_rooks_atleast_1", True),
            ("4k3/8/8/8/8/8/8/R3K3 w - - 0 1", "white_rooks_atleast_1", True),
            ("4k3/8/8/8/8/8/8/R3K3 w - - 0 1", "black_rooks_atleast_1", False),
            ("4k3/8/4n3/8/8/4B3/8/1N2K3 w - - 0 1", "white_minors_atleast_2", True),
            ("4k3/8/4n3/8/8/4B3/8/1N2K3 w - - 0 1", "white_minors_atleast_3", False),
            ("4k3/8/4n3/8/8/4B3/8/1N2K3 w - - 0 1", "black_minors_atleast_1", True),
            (START, "black_minors_atleast_3", True)])


class Openings(unittest.TestCase):
    NAJDORF = ";1.e4 c5 2.Nf3 d6 3.d4 cxd4 4.Nxd4 Nf6 5.Nc3 a6 6.Be3 e5 7.Nb3 Be6 8.f3 "
    FRENCH = ";1.e4 e6 2.d4 d5 3.e5 c5 4.c3 Nc6 5.Nf3 Qb6 6.a3 Nh6 7.b4 cxd4 8.cxd4 "

    def test_named_line(self):
        got = openings.labels(board_of(self.NAJDORF))
        self.assertIn("line_Sicilian_Defense_Najdorf_Variation", got)
        self.assertEqual([k for k in got if k.startswith("eco_")], ["eco_B90"])

    def test_french_advance(self):
        got = openings.labels(board_of(self.FRENCH))
        self.assertIn("line_French_Defense_Advance_Variation", got)
        self.assertTrue([k for k in got if k.startswith("eco_C02")])

    def test_transposition(self):
        """The Najdorf by another move order is found by its position."""
        got = openings.labels(board_of(";1.Nf3 c5 2.e4 d6 3.d4 cxd4 4.Nxd4 Nf6 5.Nc3 a6 6.Be3 e5 7.Nb3 Be6 8.f3 "))
        self.assertIn("line_Sicilian_Defense_Najdorf_Variation", got)

    def test_window(self):
        early = board_of(";1.e4 c5 2.Nf3 d6 3.d4 cxd4 4.Nxd4 Nf6 5.Nc3 a6 6.")
        self.assertFalse(openings.applicable(early))
        self.assertEqual(openings.labels(early), {})
        self.assertTrue(openings.applicable(board_of(self.NAJDORF)))
        late = chess.Board("4k3/8/8/8/8/8/8/4K3 w - - 0 16")
        self.assertFalse(openings.applicable(late))


class Structures(unittest.TestCase):
    PANOV = "r1bqkb1r/pp3ppp/2n1pn2/8/3P4/2N2N2/PP3PPP/R1BQKB1R w KQkq - 0 8"
    CARLSBAD = "rnbqkb1r/ppp2ppp/5n2/3p4/3P4/2N5/PP2PPPP/R1BQKBNR w KQkq - 0 5"
    MAROCZY = "r1bq1rk1/pp2ppbp/2np1np1/8/2P1P3/2N1BP2/PP2B1PP/R2QK2R b KQ - 0 9"
    KID = "r1bq1rk1/pppn1pbp/3p1np1/3Pp3/2P1P3/2N2N2/PP2BPPP/R1BQ1RK1 b - - 0 9"
    QGD = "rnbqkb1r/ppp2ppp/4pn2/3p4/2PP4/2N5/PP2PPPP/R1BQKBNR w KQkq - 0 4"

    def test_table(self):
        check(self, structures, [
            (self.PANOV, "isolated_queens_pawn", True),
            ("r1bqkb1r/pp3ppp/2n2n2/3p4/8/2N1PN2/PP3PPP/R1BQKB1R w KQkq - 0 8", "isolated_queens_pawn", True),
            ("r1bqkb1r/pp3ppp/2n1pn2/8/3P4/2N1PN2/PP3PPP/R1BQKB1R b KQkq - 0 8", "isolated_queens_pawn", False),
            (START, "isolated_queens_pawn", False),
            ("4k3/8/8/8/3P4/8/8/4K3 w - - 0 1", "isolated_queens_pawn", False),
            ("r1bq1rk1/p3bppp/1pn2n2/8/2PP4/2N2N2/P3BPPP/R1BQ1RK1 w - - 0 11", "hanging_pawns", True),
            ("r1bq1rk1/p3bppp/2n2n2/2pp4/8/1PN1PN2/P3BPPP/R1BQ1RK1 w - - 0 11", "hanging_pawns", True),
            ("r1bq1rk1/p3bppp/1pn2n2/8/2PP4/2N2N2/PP2BPPP/R1BQ1RK1 w - - 0 11", "hanging_pawns", False),
            (START, "hanging_pawns", False),
            (self.CARLSBAD, "carlsbad", True),
            ("r1bqkbnr/pp2pppp/2n5/3p4/3P4/2P5/PP3PPP/RNBQKBNR w KQkq - 0 5", "carlsbad", True),
            ("rnbqkbnr/pp3ppp/2p1p3/3p4/2PP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 4", "carlsbad", False),
            (self.QGD, "carlsbad", False),
            (self.MAROCZY, "maroczy_bind", True),
            ("r1bqkb1r/pp2pppp/2np1n2/2p5/2P1P3/2NP1N2/PP3PPP/R1BQKB1R w KQkq - 0 6", "maroczy_bind", False),
            (START, "maroczy_bind", False),
            ("r1b2rk1/1q1nbppp/pp1ppn2/8/2P1P3/1PN1B3/P2QBPPP/R2N1RK1 w - - 0 13", "hedgehog", True),
            ("r1b2rk1/1q1nbppp/pp1ppn2/8/2P1P3/1PN1B3/P2QBPPP/R2N1RK1 w - - 0 13", "maroczy_bind", True),
            (self.MAROCZY, "hedgehog", False),
            (START, "hedgehog", False),
            ("rnbqkbnr/ppp1pppp/8/3p4/3P1P2/4P3/PPP3PP/RNBQKBNR b KQkq - 0 3", "stonewall", True),
            ("rnbqkb1r/ppp3pp/4pn2/3p1p2/2PP4/5NP1/PP2PP1P/RNBQKB1R w KQkq - 0 5", "stonewall", True),
            (START, "stonewall", False),
            ("rnbqkbnr/ppp1pppp/8/3p4/3P4/4P3/PPP2PPP/RNBQKBNR b KQkq - 0 2", "stonewall", False),
            ("r1bqkb1r/ppp2ppp/2np1n2/8/3NP3/2N5/PPP2PPP/R1BQKB1R w KQkq - 0 6", "small_centre", True),
            ("rnbqkb1r/pp2pppp/3p1n2/8/3NP3/2N5/PPP2PPP/R1BQKB1R b KQkq - 0 5", "small_centre", False),
            (START, "small_centre", False),
            (self.KID, "kings_indian", True),
            ("rnbq1rk1/pp3pbp/3p1np1/2pPp3/2P1P3/2N2N2/PP2BPPP/R1BQK2R b KQ - 0 8", "kings_indian", False),
            (START, "kings_indian", False),
            ("rnbqkbnr/pp3ppp/4p3/2ppP3/3P4/2P5/PP3PPP/RNBQKBNR b KQkq - 0 4", "french_advance", True),
            ("rn1qkbnr/pp2pppp/2p5/3pPb2/3P4/8/PPP2PPP/RNBQKBNR w KQkq - 1 4", "french_advance", False),
            (START, "french_advance", False),
            ("rn1qkbnr/pp2pppp/2p5/3pPb2/3P4/8/PPP2PPP/RNBQKBNR w KQkq - 1 4", "caro_slav", True),
            ("r1bqkbnr/pp1n1ppp/2p1p3/8/3P4/8/PPP2PPP/RNBQKBNR w KQkq - 0 6", "caro_slav", True),
            ("rnbqkb1r/pp2pppp/2p2n2/3p4/2PP4/2N2N2/PP2PPPP/R1BQKB1R b KQkq - 3 4", "caro_slav", True),
            (self.QGD, "caro_slav", False),
            ("rnbqkb1r/pp3p1p/3p1np1/2pP4/4P3/2N5/PP3PPP/R1BQKBNR w KQkq - 0 7", "benoni", True),
            (self.KID, "benoni", False),
            (START, "benoni", False)])


class Imbalances(unittest.TestCase):
    KINGS = "4k3/8/8/8/8/8/8/4K3 w - - 0 1"

    def test_table(self):
        check(self, imbalances, [
            ("4k3/8/4n3/8/8/4B3/8/4K3 w - - 0 1", "white_bishop_vs_knight", True),
            ("4k3/8/4n3/8/8/4B3/8/4K3 w - - 0 1", "black_bishop_vs_knight", False),
            ("4k3/8/4n3/8/8/2B1B3/8/4K3 w - - 0 1", "white_bishop_vs_knight", False),
            ("4k3/8/4n3/8/8/4N3/8/4K3 w - - 0 1", "white_bishop_vs_knight", False),
            ("4k3/8/8/3P4/2P1P3/1P1B4/8/4K3 w - - 0 1", "white_bad_bishop", True),
            ("4k3/8/8/8/1P1P4/2PBP3/8/4K3 w - - 0 1", "white_bad_bishop", False),
            ("4k3/8/8/8/2P1P3/2PBP3/8/4K3 w - - 0 1", "white_bad_bishop", None),
            ("4k3/8/8/8/2P5/3B4/8/4K3 w - - 0 1", "white_bad_bishop", None),
            ("4k3/2p2p2/3pp3/3PP3/2P2P2/8/8/4K3 w - - 0 1", "white_space_advantage", True),
            ("4k3/2p2p2/3pp3/3PP3/2P2P2/8/8/4K3 w - - 0 1", "black_space_advantage", False),
            (START, "white_space_advantage", False),
            ("4k3/8/8/3P4/8/8/8/4K3 w - - 0 1", "white_space_advantage", None),
            ("4k3/p7/8/8/8/8/P6P/3RK3 w - - 0 1", "white_rook_open_file", True),
            ("4k3/p7/8/8/8/8/P6P/3RK3 w - - 0 1", "white_rook_half_open_file", False),
            ("4k3/3p4/8/8/8/8/P6P/3RK3 w - - 0 1", "white_rook_half_open_file", True),
            ("4k3/3p4/8/8/8/8/P6P/3RK3 w - - 0 1", "white_rook_open_file", False),
            ("4k3/3p4/8/8/8/8/3P4/3RK3 w - - 0 1", "white_rook_half_open_file", False),
            ("4k3/8/8/8/8/8/P7/3QK3 w - - 0 1", "white_queen_open_or_half_open_file", True),
            ("4k3/8/8/8/8/8/3P4/3QK3 w - - 0 1", "white_queen_open_or_half_open_file", False),
            ("4k3/p6p/8/4N3/3P4/8/8/4K3 w - - 0 1", "white_knight_outpost", True),
            ("4k3/5p2/8/4N3/3P4/8/8/4K3 w - - 0 1", "white_knight_outpost", False),
            ("4k3/p6p/8/4N3/8/8/8/4K3 w - - 0 1", "white_knight_outpost", False),
            ("4k3/p6p/8/8/8/4N3/3P4/4K3 w - - 0 1", "white_knight_outpost", False),
            ("3qk3/8/8/8/8/6P1/5P1P/6K1 w - - 0 1", "white_weak_king_squares", True),
            ("3qk3/8/8/8/8/8/5PPP/6K1 w - - 0 1", "white_weak_king_squares", False),
            ("4k3/8/8/8/8/6P1/5P1P/6K1 w - - 0 1", "white_weak_king_squares", None),
            ("3qk3/8/8/8/4K3/8/8/8 w - - 0 1", "white_weak_king_squares", None),
            ("4k3/p7/8/8/8/8/PP6/4K3 w - - 0 1", "white_queenside_majority", True),
            ("4k3/p7/8/8/8/8/PP6/4K3 w - - 0 1", "white_kingside_majority", False),
            ("4k3/7p/8/8/8/8/6PP/4K3 w - - 0 1", "white_kingside_majority", True),
            (START, "white_queenside_majority", False),
            ("4k3/7p/8/P7/8/8/8/4K3 w - - 0 1", "white_passed_pawn", True),
            ("4k3/3p4/8/8/4P3/8/8/4K3 w - - 0 1", "white_passed_pawn", False),
            ("4k3/8/8/8/4P3/3p4/8/4K3 w - - 0 1", "white_passed_pawn", True),
            (START, "black_passed_pawn", False),
            ("rnbqkbnr/pppppppp/8/8/2B1P3/5N2/PPPP1PPP/RNBQ1RK1 b kq - 0 5", "white_development_lead", True),
            ("rnbqkbnr/pppppppp/8/8/2B1P3/5N2/PPPP1PPP/RNBQ1RK1 b kq - 0 5", "black_development_lead", False),
            (START, "white_development_lead", False),
            ("rnbqkbnr/pppppppp/8/8/2B1P3/5N2/PPPP1PPP/RNBQ1RK1 b kq - 0 20", "white_development_lead", None),
            ("r2qk3/8/8/8/8/8/8/R3K3 w - - 0 1", "white_king_unsafe", True),
            ("3qk3/8/8/8/8/8/5PPP/6K1 w - - 0 1", "white_king_unsafe", False),
            ("3qk3/8/8/8/8/8/7P/6K1 w - - 0 1", "white_king_unsafe", None),
            ("4k3/8/8/8/8/8/5PPP/6K1 w - - 0 1", "white_king_unsafe", None)])


class Plans(unittest.TestCase):
    CARLSBAD = "r1bq1rk1/pp1nbppp/2p2n2/3p2B1/3P4/2NBPN2/PPQ2PPP/R3K2R w KQ - 0 9"
    IQP = "r1bq1rk1/pp2bppp/2n1pn2/8/3P4/2NB1N2/PP3PPP/R1BQ1RK1 w - - 0 10"
    KID = "r1bq1rk1/pppn1pbp/3p1np1/3Pp3/2P1P3/2N2N2/PP2BPPP/R1BQ1RK1 b - - 0 9"
    MAROCZY = "r1bq1rk1/pp2ppbp/2np1np1/8/2P1P3/2N1BP2/PP2B1PP/R2QK2R b KQ - 0 9"

    def run_plan(self, fen, concept, future):
        return plans.labels(chess.Board(fen), dict(future=future.split()))[concept]

    def test_carlsbad(self):
        self.assertTrue(self.run_plan(self.CARLSBAD, "plan_carlsbad_minority", "a1b1 f8e8 e1g1 d7f8 b2b4 a7a6 a2a3 f8g6 f1c1 h7h6"))
        self.assertFalse(self.run_plan(self.CARLSBAD, "plan_carlsbad_minority", "a1b1 f8e8 e1g1 d7f8 a2a3 a7a6 h2h3 f8g6 f1c1 h7h6"))
        self.assertIsNone(self.run_plan(self.CARLSBAD, "plan_carlsbad_minority", "a1b1 f8e8"))             # too few plies known
        played = "r1bq1rk1/pp1nbppp/2p2n2/3p2B1/1P1P4/2NBPN2/P1Q2PPP/R3K2R b KQ - 0 9"                      # b4 is in
        self.assertIsNone(self.run_plan(played, "plan_carlsbad_minority", "a7a6 a2a3 h7h6 h2h3 f8e8 a1b1 d7f8 b1a1 f8g6 a1b1"))
        self.assertIsNone(self.run_plan(chess.STARTING_FEN, "plan_carlsbad_minority", "e2e4 " * 10))        # not in the structure

    def test_iqp(self):
        self.assertTrue(self.run_plan(self.IQP, "plan_iqp_break", "a2a3 a7a6 d4d5 e6d5 c3d5 f6d5 d3h7 g8h7 d1d5 d8d5"))
        self.assertFalse(self.run_plan(self.IQP, "plan_iqp_break", "a2a3 a7a6 h2h3 h7h6 b2b4 b7b5 c1e3 c8b7 f1e1 f8e8"))
        self.assertIsNone(self.run_plan(chess.STARTING_FEN, "plan_iqp_break", "e2e4 " * 10))

    def test_kings_indian(self):
        self.assertTrue(self.run_plan(self.KID, "plan_kings_indian_storm", "f6e8 c1e3 f7f5 f3d2 e8f6 a2a3 a7a6 h2h3 h7h6 a1c1"))
        self.assertFalse(self.run_plan(self.KID, "plan_kings_indian_storm", "a7a5 a2a3 b7b6 h2h3 h7h6 c1e3 c8b7 f3e1 d8e7 e1d3"))
        moved = "r1bq1rk1/pppn2bp/3p1np1/3Ppp2/2P1P3/2N2N2/PP2BPPP/R1BQ1RK1 w - - 0 10"                      # ...f5 is in
        self.assertIsNone(self.run_plan(moved, "plan_kings_indian_storm", "a2a3 a7a6 h2h3 h7h6 c1e3 c8b7 f3e1 d8e7 e1d3 a8e8"))

    def test_maroczy(self):
        self.assertTrue(self.run_plan(self.MAROCZY, "plan_maroczy_break", "a7a6 d1d2 b7b5 c4b5 a6b5 e2b5 c8b7 e1g1 d8b6 a1c1"))
        self.assertFalse(self.run_plan(self.MAROCZY, "plan_maroczy_break", "a7a6 d1d2 c6e5 a1c1 c8d7 e1g1 a8c8 b2b3 f8e8 f1d1"))
        self.assertIsNone(self.run_plan(chess.STARTING_FEN, "plan_maroczy_break", "e2e4 " * 10))


class StockfishTerms(unittest.TestCase):
    TABLE = """
      Eval term |    White    |    Black    |    Total
                |   MG    EG  |   MG    EG  |   MG    EG
 ---------------+-------------+-------------+-------------
       Material |   ---   --- |   ---   --- |  0.00  0.00
       Mobility |  0.50  1.00 | -0.50 -1.00 |  1.00  2.00
    King safety |  0.20  0.00 |  0.10  0.00 |  0.10  0.00
"""

    def test_parse(self):
        got = stockfish_terms.parse_eval(self.TABLE)
        self.assertEqual(got["Mobility"], (0.75, -0.75))
        self.assertEqual(got["King safety"], (0.10, 0.05))
        self.assertNotIn("Material", got)


class Common(unittest.TestCase):
    def test_prompt_matches_the_models(self):
        from pgn_model import prompt
        for prefix in ("", ";1.e4 ", ";1.e4 e5 2."):
            b = board_of(prefix) if prefix else chess.Board()
            self.assertEqual(prompt_of(sans_of(prefix)), prompt(b))

    def test_phase(self):
        self.assertEqual(phase_of(chess.Board()), "opening")
        self.assertEqual(phase_of(chess.Board("r1bq1rk1/pppn1pbp/3p1np1/3Pp3/2P1P3/2N2N2/PP2BPPP/R1BQ1RK1 b - - 0 12")), "middlegame")
        self.assertEqual(phase_of(chess.Board("4k3/8/4n3/8/8/4B3/8/4K3 w - - 0 3")), "endgame")

    def test_material_and_split(self):
        self.assertEqual(material(chess.Board(), chess.WHITE), 39)
        self.assertEqual(split_of("x"), split_of("x"))
        self.assertIn(split_of("x"), ("fit", "test"))


if __name__ == "__main__":
    unittest.main()
