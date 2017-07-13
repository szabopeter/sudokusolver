import unittest
from solver import Solver, StandardTextOut


class GenerationTestCase(unittest.TestCase):
    def create_generator(self, limit, configline, verbose=False):
        textout = None
        if verbose:
            textout = StandardTextOut()
        genline = "generate %s" % limit
        return Solver(genline + "\n" + configline, textout=textout)

    def create_solution(self, backtrack_count):
        solution = Solver("generate 0")
        solution.backtrack_count = backtrack_count
        return solution

    def test_2x2_without_backtracking(self):
        generator = self.create_generator(0, "2x2:.1234")
        puzzles, limit_reached = generator.solve()
        self.assertEqual(1, len(puzzles))
        puzzle = puzzles[0]

        solver = Solver(puzzle.asText())
        solutions, limit_reached = solver.solve()
        self.assertEqual(1, len(solutions))
        self.assertEqual(0, solutions[0].backtrack_count)

    def test_2x2_with_1step_backtracking(self):
        generator = self.create_generator(1, "2x2:.1234", True)
        puzzles, limit_reached = generator.solve()
        self.assertEqual(1, len(puzzles))
        puzzle = puzzles[0]
        puzzle.print(puzzle.asText())

        solver = Solver(puzzle.asText())
        solutions, limit_reached = solver.solve()
        self.assertEqual(1, len(solutions))
        self.assertEqual(1, solutions[0].backtrack_count)

    def test_generation_decisions(self):
        generator = self.create_generator(0, "\n", False)
        bt0 = self.create_solution(0)
        bt1 = self.create_solution(1)
        cases = (
            ([bt0, ], 0, 0, ),
            ([], 0, -1, ),      # no solution because of contradiction
            ([], -1, +1, ),     # no solution because of backtrack limit
            ([bt0, bt1, ], 1, +1, ),
        )
        for solutions, backtracks, expected_decision in cases:
            decision = generator.generation_iteration_decision(solutions, backtracks)
            self.assertEqual(expected_decision, decision)


if __name__ == "__main__":
    unittest.main()
