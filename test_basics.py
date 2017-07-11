import unittest
from solver import Solver


class BasicsTestCase(unittest.TestCase):
    def test_2x1_trivial(self):
        solver = Solver(""" 2x1:.12
                            1 .
                            ---
                            . . """)
        solutions = solver.solve()[0]
        self.assertEqual(1, len(solutions))

    def test_2x1_backtracking(self):
        solver = Solver(""" 2x1:.12
                            . .
                            ---
                            . . """)
        solutions = solver.solve()[0]
        self.assertEqual(2, len(solutions))

    def test_3x3_trivial(self):
        solver = Solver("""
                        ..6|..9|47.
                        .8.|.6.|..5
                        .47|..5|..1
                        -----------
                        2..|...|.59
                        ...|9.3|...
                        .7.|...|..3
                        -----------
                        8..|3..|12.
                        7..|.2.|.9.
                        .21|6..|3..
                        """)
        solutions = solver.solve()[0]
        self.assertEqual(1, len(solutions))
        solution = solutions[0]
        expected_lines = [
            "3x3:.123456789",
            "356819472",
            "182764935",
            "947235861",
            "238146759",
            "615973284",
            "479582613",
            "894357126",
            "763421598",
            "521698347"
            ]
        expected_solution = "\n".join(expected_lines)
        self.assertEqual(expected_solution, solution.asText())

if __name__ == "__main__":
    unittest.main()
