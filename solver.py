#!/usr/bin/env python3


class StandardTextOut(object):
    def print(self, text):
        print(text)


class Config(object):
    def __init__(self, configline=None):
        if configline is None:
            self.UNIT_X, self.UNIT_Y = 3, 3
            self.VALIDCHARS = "123456789"
            self.EMPTYCHAR = "."
            self.SIZE = 0
        else:
            sizes, chars = [field.strip() for field in configline.split(':')]
            self.UNIT_X, self.UNIT_Y = [int(size) for size in sizes.split("x")]
            self.EMPTYCHAR, self.VALIDCHARS = chars[0], chars[1:]

    def is_valid(self):
        self.SIZE = len(self.VALIDCHARS)
        if self.UNIT_X*self.UNIT_Y != self.SIZE:
            return False
        return True

    def __str__(self):
        configline = "%sx%s:%s%s" % (
            self.UNIT_X, self.UNIT_Y, self.EMPTYCHAR, self.VALIDCHARS, )
        return configline + " (size=%s)" % self.SIZE


class Solver:
    def __init__(self, textinput, director=True, textout=None):
        self.textout = textout
        self.director = director
        self.backtrack_count = -1
        self.textinput = textinput.split("\n")
        self.generating = None
        firstline = self.textinput[0] if self.textinput else ""
        if "generate" in firstline:
            genargs = firstline.split()
            if len(genargs) > 1:
                self.generating = int(genargs[1])
                self.print("Will generate (%s)" % self.generating)
                self.textinput.pop(0)

        self.configline = "3x3:.123456789"
        firstline = self.textinput[0] if self.textinput else ""
        if 'x' in firstline and ':' in firstline:
            self.configline = firstline
            self.textinput.pop(0)
        config = Config(self.configline)

        if not config.is_valid():
            self.print("Invalid config")
            self.print(config)
            raise Exception("Invalid config")

        self.config = config
        # self.print(self.config)

        if self.generating is not None:
            self.textinput = self.all_empty()
        self.fill_rows()
        # self.print(str(self))
        if (len(self.rows) != self.config.SIZE):
            self.print("Invalid number of rows (%d)!" % (len(self.rows)))

    def print(self, text):
        if self.textout:
            self.textout.print(text)

    def all_empty(self):
        return [self.config.EMPTYCHAR * self.config.SIZE for row_nr in range(self.config.SIZE)]

    def fill_rows(self):
        self.rows = []
        for line in self.textinput:
            if line.strip().startswith("#"):
                continue

            processables = self.config.VALIDCHARS + self.config.EMPTYCHAR
            validchars = [ch for ch in line if ch in processables]
            if len(validchars) == self.config.SIZE:
                def mkcelldescription(col):
                    return "(%d %d)" % (len(self.rows), col,)

                linedata = [cell(
                    validchars[col],
                    mkcelldescription(col),
                    self.config.VALIDCHARS,
                    self.config)
                        for col in range(self.config.SIZE)]

                self.rows.append(linedata)
            elif len(validchars) != 0:
                self.print("Invalid row: " + line.strip())

    def __str__(self):
        def separatorNeeded(col, unit, separator):
            if (col+1) % unit == 0:
                return separator
            else:
                return ""

        # return "\n".join(" ".join([str(cell) for cell in linedata]) for linedata in self.rows)
        SIZE = self.config.SIZE
        UNIT_X, UNIT_Y = self.config.UNIT_X, self.config.UNIT_Y
        colsep = " | "
        rowsep = "\n" + ("-" * ((SIZE+len("[]"))*(SIZE-1) + UNIT_Y*len(colsep)))

        def cellsfmt(row):
            return [str(self.rows[row][col]) + separatorNeeded(col, UNIT_X, colsep)
                    for col in range(SIZE)]

        def rowfmt(row):
            return " ".join(cellsfmt(row)) + separatorNeeded(row, UNIT_Y, rowsep)

        return "\n".join([rowfmt(row) for row in range(SIZE)])

    def dumpdata(self):
        self.print(str(self))

    def __getitem__(self, row, col):
        return self.rows[row][col].value

    def __setitem__(self, row, col, value):
        self.rows[row][col] = cell(value)

    def byRule1(self, i):
        "Row i"
        if i >= len(self.rows):
            self.print("Trying to get row %d while there are only %d of them" %
                       (i, len(self.rows), ))
        return [cell for cell in self.rows[i]]

    def byRule2(self, i):
        "Col i"
        return [row[i] for row in self.rows]

    def byRule3(self, i):
        "Square i"
        """
        i | row | col
        0 | 0   | 0
        1 | 0   | 3
        2 | 0   | 6
        3 | 3   | 0
        8 | 6   | 6
        ...
        i | 3 * (i / 3) | 3 * (i % 3)

        i | row | col
        0 | 0   | 0
        1 | 0   | 4
        2 | 2   | 0
        3 | 2   | 4
        7 | 6   | 4
        ...
        i | 2 * (i / 2) | 4 * (i % 2)
        """

        UNIT_X, UNIT_Y = self.config.UNIT_X, self.config.UNIT_Y
        row = UNIT_Y * (i // UNIT_Y)
        col = UNIT_X * (i % UNIT_Y)
        import itertools
        return [self.rows[row+offset[0]][col+offset[1]]
                for offset in itertools.product(range(UNIT_Y), range(UNIT_X))]

    def hasDuplicate(self, cellist, contextdescription=""):
        usedvalues = []
        valuestocheck = [cell.value for cell in cellist if cell.value in self.config.VALIDCHARS]
        # self.print("Checking %s in context %s" % (valuestocheck, contextdescription, ))
        for cellvalue in valuestocheck:
            if cellvalue in usedvalues:
                if (self.director):
                    self.print("Context: %s\nValues: %s\nUsed already: %s" %
                               (contextdescription, valuestocheck, usedvalues,))
                return True
            else:
                usedvalues.append(cellvalue)
        return False

    def elimination(self, cellist, context):
        success = False
        for pivotcell in cellist:
            if pivotcell.value != self.config.EMPTYCHAR:
                if self.eliminate_on_filled(pivotcell, cellist):
                    success = True
            else:
                if self.eliminate_pivot(pivotcell, cellist, context):
                    success = True
        return success

    def eliminate_on_filled(self, pivotcell, cellist):
        success = False
        for cell in cellist:
            if (cell != pivotcell and pivotcell.value in cell.possible):
                cell.possible = cell.possible.replace(pivotcell.value, "")
                success = True
                if len(cell.possible) == 0 and self.director:
                    self.print("Contradiction on cell " + cell.description)
                if len(cell.possible) == 1:
                    cell.value = cell.possible
        return success

    def eliminate_pivot(self, pivotcell, cellist, context):
        success = False
        pivotpossibilities = set(pivotcell.possible)
        if (context == "dbg"):
            self.print("%s: %s" % (pivotcell, pivotpossibilities,))
        for cell in cellist:
            if (cell != pivotcell):
                pivotpossibilities -= set(cell.possible)
        if (len(pivotpossibilities) == 1):
            value = pivotpossibilities.pop()
            pivotcell.set_final(value)
            # self.print("Cell %s had no rival for value %s" %
            #     (pivotcell.description, pivotcell.value, ))
            success = True
        return success

    def isValid(self):
        for i in range(self.config.SIZE):
            rules = (
                (self.byRule1, "by row %d", ),
                (self.byRule2, "by col %d", ),
                (self.byRule3, "by sqr %d", )
                )

            for rule, note in rules:
                if self.hasDuplicate(rule(i), note % i):
                    return False
        return True

    def eliminate(self):
        itercount = 0
        keepgoing = True
        while keepgoing:
            itercount += 1
            keepgoing = False
            for i in range(self.config.SIZE):
                keepgoing = keepgoing or self.elimination(self.byRule1(i), "by row %d" % i)
                keepgoing = keepgoing or self.elimination(self.byRule2(i), "by col %d" % i)
                keepgoing = keepgoing or self.elimination(self.byRule3(i), "by sqr %d" % i)
        return itercount

    def solve(self, iterbase=0, max_backtrack=None):
        if self.generating is not None:
            return self.generate()

        self.backtrack_count += 1

        solutionlist = []
        limit_reached = False
        if not self.isValid() and self.director:
            self.print("Invalid starting state!")
        else:
            if self.director:
                self.print("Seems legit...")
            itercount = self.eliminate()

            # self.print("\nAfter %d+%d iteration(s): " % (iterbase, itercount, ))
            # self.dumpdata()

            if self.isValid():
                if self.solved():
                    solutionlist = [self.clone(), ]
                    self.print("Success after %d iterations" % (iterbase + itercount,))
                else:
                    subsolutions, limit_hit = self.backtrack(iterbase, itercount, max_backtrack)
                    solutionlist.extend(subsolutions)
                    if limit_hit:
                        limit_reached = True

            # self.elimination(self.byRule3(8), "dbg")
        return solutionlist, limit_reached

    def generate(self):
        filled_cell_count = self.config.SIZE
        finished = False
        attempts_left = 12
        while not finished and attempts_left > 0:
            attempts_left -= 1
            work = self.clone()
            puzzle = self.clone()
            for i in range(filled_cell_count):
                unsolved_cell = work.unsolvedCells()[0]
                trial = unsolved_cell.possible[0]
                unsolved_cell.set_final(trial)
                puzzle_cell = puzzle.get_cell(unsolved_cell.description)
                puzzle_cell.set_final(trial)
                work.eliminate()
            self.print("Checking generated puzzle")
            self.print(puzzle)
            original = puzzle.clone()
            work = puzzle.clone()
            solutions, limit_reached = work.solve(max_backtrack=self.generating)
            tuning = self.generation_iteration_decision(solutions, limit_reached)
            original.print(original)
            self.print("Tried filling %s cells, got %s solutions, limit hit: %s => %s" %
                       (filled_cell_count, len(solutions), limit_reached, tuning))

            if tuning == 0:
                self.print("Ending generation.")
                self.print(original)
                return [original], limit_reached
                finished = True, limit_reached
                break

            filled_cell_count += tuning

            if filled_cell_count < 0:
                self.print("Filled cell count is too low.")
                return [], limit_reached

        return [], False

    def generation_iteration_decision(self, solutions, limit_reached):
        solcount = len(solutions)
        if solcount == 1:
            return 0

        if solcount == 0:
            if limit_reached:
                return +1
            return -1
        return +1

    def backtrack(self, iterbase, itercount, max_backtrack):
        if max_backtrack == 0:
            # self.print("Reached max backtrack limit.")
            return [], True

        if max_backtrack is not None:
            max_backtrack -= 1

        solutionlist = []
        limit_reached = False
        badcell = self.unsolvedCellsToBacktrack()[0]
        if len(badcell.possible) > 3:
            self.print(self)
            self.print("Backtracking at %s with too many possible values: %s" %
                       (badcell.description, badcell.possible, ))

        for trial in badcell.possible:
            aclone = self.clone()
            badcellclone = aclone.get_cell(badcell.description)
            badcellclone.set_final(trial)

            try:
                subsolutions, limit_hit = aclone.solve(iterbase + itercount, max_backtrack)
                if limit_hit:
                    limit_reached = True
            except KeyboardInterrupt:
                return solutionlist, limit_reached

            if subsolutions:
                self.print("Had to backtrack at this state:")
                self.print(self.asText())

            solutionlist.extend(subsolutions)
        return solutionlist, limit_reached

    def get_cell(self, description):
        for row in self.rows:
            for cell in row:
                if cell.description == description:
                    return cell
        return None

    def allCellsFlat(self):
        SIZE = self.config.SIZE
        # rowlens = ",".join([str(len(row)) for row in self.rows])
        # self.print("size=%s rows=%s rowlens=%s" % (SIZE, len(self.rows), rowlens))
        return [self.rows[i // SIZE][i % SIZE] for i in range(SIZE*SIZE)]

    def unsolvedCells(self):
        return [cell for cell in self.allCellsFlat() if cell.value == self.config.EMPTYCHAR]

    def unsolvedCellsToBacktrack(self):
        unsolved = self.unsolvedCells()
        unsolved.sort(key=lambda cell: len(cell.possible))
        return unsolved

    def solved(self):
        return self.isValid() and len(self.unsolvedCells()) == 0

    def asText(self):
        configline = [self.configline, ]
        boardlines = ["".join([cell.value for cell in row]) for row in self.rows]
        text = "\n".join(configline + boardlines)
        return text

    def clone(self):
        clone = Solver(self.asText(), director=False, textout=self.textout)
        clone.backtrack_count = self.backtrack_count
        return clone


class cell:
    def __init__(self, value, description, possible, config):
        self.EMPTYCHAR = config.EMPTYCHAR
        self.SIZE = config.SIZE
        self.description = description
        if value == self.EMPTYCHAR:
            self.possible = possible
            self.value = self.EMPTYCHAR
        else:
            self.possible = value
            self.value = value

        self.fmt_possibles = "[%%%ss]" % self.SIZE
        self.fmt_filled = "%s".center(self.SIZE+2)

    def __repr__(self):
        return str(self)

    def __str__(self):
        # result length should always be SIZE+2
        if self.value == self.EMPTYCHAR:
            return self.fmt_possibles % self.possible
        else:
            return self.fmt_filled % self.value

    def clone(self):
        return cell(self.value, self.description, self.possible, self.config)

    def set_final(self, value):
        self.value = self.possible = value


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: solver.py datafile.txt")
    else:
        f = open(sys.argv[1])
        data = f.read()
        s = Solver(data, director=True, textout=StandardTextOut())
        # s.dumpdata()
        #  s.print(repr(s.byRule3(8)))
        solutions, limit_reached = s.solve()
        s.print("Found %d solution%s" % (len(solutions), "s" if len(solutions) > 1 else ""))
        for i in range(len(solutions)):
            s.print("Solution #%d" % (i+1))
            if s.generating is None:
                solutions[i].dumpdata()
            else:
                s.print(solutions[i].asText())
