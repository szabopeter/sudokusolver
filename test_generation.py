import unittest
from solver import Solver, StandardTextOut


class GenerationTestCase(unittest.TestCase):
    def create_generator(self, limit, configline, verbose=False):
        textout = None
        if verbose:
            textout = StandardTextOut()
        genline = "generate %s" % limit
        return Solver(genline + "\n" + configline, textout=textout)

    def test_2x2_without_backtracking(self):
        generator = self.create_generator(0, "2x2:.1234")
        puzzles, limit_reached = generator.solve()
        self.assertEqual(1, len(puzzles))
        puzzle = puzzles[0]
        puzzle.print(puzzle)

        solver = Solver(puzzle.asText())
        solutions, limit_reached = solver.solve()
        self.assertEqual(1, len(solutions))
        self.assertEqual(0, solutions[0].backtrack_count)

    def test_generation_decisions(self):
        generator = self.create_generator(0, "\n", False)
        cases = (
            (["single solution", ], 0, 0, ),
            ([], 0, -1, ),      # no solution because of contradiction
            ([], -1, +1, ),     # no solution because of backtrack limit
            (["multiple", "solutions", ], 1, +1, ),
        )
        for solutions, backtracks, expected_decision in cases:
            decision = generator.generation_iteration_decision(solutions, backtracks)
            self.assertEqual(expected_decision, decision)


if __name__ == "__main__":
    unittest.main()
