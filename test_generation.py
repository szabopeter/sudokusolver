import unittest
from solver import Solver, StandardTextOut


class GenerationTestCase(unittest.TestCase):
    def test_2x2_without_backtracking(self):
        generator = Solver("generate 0\n2x2:.1234", textout=StandardTextOut())
        puzzle = generator.solve()
        self.assertEqual(1, len(puzzle))

        solver = Solver(puzzle.asText())
        solutions = solver.solve()
        self.assertEqual(1, len(solutions))
        self.assertEqual(0, solutions[0].backtrack_count)


if __name__ == "__main__":
    unittest.main()
