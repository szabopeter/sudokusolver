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

    def test_generation_decisions(self):
        generator = Solver("generate 0")
        cases = (
            (["single solution", ], 0, 0, ),
            ([], 0, -1, ), # no solution because of contradiction
            ([], -1, +1, ), # no solution because of backtrack limit
            (["multiple", "solutions", ], 1, +1, ),
        )
        for solutions, backtracks, expected_decision in cases:
            decision = generator.generation_iteration_decision(solutions, backtracks)
            self.assertEqual(expected_decision, decision)


if __name__ == "__main__":
    unittest.main()
