import unittest
from solver import Solver


class BasicsTestCase(unittest.TestCase):
    def test_2x1_trivial(self):
        solver = Solver(""" 2x1:.12
                            1 .
                            ---
                            . . """)
        solutions = solver.solve()
        self.assertEqual(1, len(solutions))

    def test_2x1_backtracking(self):
        solver = Solver(""" 2x1:.12
                            . .
                            ---
                            . . """)
        solutions = solver.solve()
        self.assertEqual(2, len(solutions))


if __name__ == "__main__":
    unittest.main()
