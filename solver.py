#!/usr/bin/env python


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
            print "Invalid config!"
            print(self)
            return False
        return True

    def __str__(self):
        configline = "%sx%s:%s%s" % (
            self.UNIT_X, self.UNIT_Y, self.EMPTYCHAR, self.VALIDCHARS, )
        return configline + " (size=%s)" % self.SIZE


class solver:
    def __init__(self, textinput, director = True):
        self.director = director
        self.textinput = textinput.split("\n")
        self.configline = "3x3:.123456789"
        configline = self.textinput[0]
        config = Config()
        if 'x' in configline and ':' in configline:
            self.configline = configline
            config = Config(configline)
            self.textinput.pop(0)

        if not config.is_valid():
            raise Exception("Invalid config")

        self.config = config
        # print(self.config)

        self.rows = []
        for line in self.textinput:
            if line.strip().startswith("#"):
                continue

            validchars = [ch for ch in line if ch in self.config.VALIDCHARS + self.config.EMPTYCHAR]
            if len(validchars) == self.config.SIZE:
                def mkcelldescription(col):
                    return "(%d %d)"%(len(self.rows), col,)

                linedata = [cell(
                    validchars[col],
                    mkcelldescription(col),
                    self.config.VALIDCHARS,
                    self.config)
                        for col in range(self.config.SIZE)]

                self.rows.append(linedata)
            elif len(validchars) != 0:
                print "Invalid row: " + line.strip()
        # print str(self)
        if (len(self.rows) != self.config.SIZE):
            print "Invalid number of rows (%d)!"%(len(self.rows))

    def __str__(self):
        def separatorNeeded(col, unit, separator):
            if (col+1) % unit == 0:
                return separator
            else:
                return ""

        #return "\n".join(" ".join([str(cell) for cell in linedata ]) for linedata in self.rows)
        SIZE = self.config.SIZE
        UNIT_X, UNIT_Y = self.config.UNIT_X, self.config.UNIT_Y
        colsep = " | "
        rowsep = "\n" + ( "-" * ((SIZE+len("[ ]"))*(SIZE-1) + UNIT_Y*len(colsep) ))
        return "\n".join([" ".join(
            [str(self.rows[row][col]) + separatorNeeded(col, UNIT_X, colsep) for col in range(SIZE)])
            + separatorNeeded(row, UNIT_Y, rowsep) for row in range(SIZE)])

    def dumpdata(self):
        print str(self)

    def __getitem__(self, row, col):
        return self.rows[row][col].value

    def __setitem__(self, row, col, value):
        self.rows[row][col] = cell(value)


    def byRule1(self, i):
        "Row i"
        if i >= len(self.rows): print "Trying to get row %d while there are only %d of them"%( i, len(self.rows), )
        return [ cell for cell in self.rows[i]]
    def byRule2(self, i):
        "Col i"
        return [ row[i] for row in self.rows ]
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
        row = UNIT_Y * (i / UNIT_Y)
        col = UNIT_X * (i % UNIT_Y)
        import itertools
        return [ self.rows[row+offset[0]][col+offset[1]] for offset in itertools.product(range(UNIT_Y), range(UNIT_X))]

    def hasDuplicate(self, cellist, contextdescription=""):
        usedvalues = []
        valuestocheck = [cell.value for cell in cellist if cell.value in self.config.VALIDCHARS]
        #print "Checking %s in context %s"%(valuestocheck, contextdescription, )
        for cellvalue in valuestocheck:
            if cellvalue in usedvalues:
                if (self.director): print "Context: %s\nValues: %s\nUsed already: %s"%(contextdescription, valuestocheck, usedvalues,)
                return True
            else:
                usedvalues.append(cellvalue)
        return False 

    def elimination(self, cellist, context):
        success = False
        for pivotcell in cellist:
            if pivotcell.value != self.config.EMPTYCHAR:
                for cell in cellist:
                    if (cell != pivotcell and pivotcell.value in cell.possible):
                        cell.possible = cell.possible.replace(pivotcell.value, "")
                        success = True
                        if len(cell.possible) == 0 and self.director:
                            print "Contradiction on cell "+ cell.description
                        if len(cell.possible) == 1:
                            cell.value = cell.possible
            else:
                pivotpossibilities = set(pivotcell.possible)
                if (context == "dbg"):
                    print "%s: %s"%(pivotcell, pivotpossibilities,)
                for cell in cellist:
                    if (cell != pivotcell):
                        pivotpossibilities -= set(cell.possible)
                if (len(pivotpossibilities)==1):
                    pivotcell.value = list(pivotpossibilities)[0]
                    pivotcell.possible = pivotcell.value
                    #print "Cell %s had no rival for value %s"%(pivotcell.description, pivotcell.value, )
                    success = True
        return success

    def isValid(self):
        for i in range(self.config.SIZE):
            if self.hasDuplicate(self.byRule1(i), "by row %d"%i ) \
            or self.hasDuplicate(self.byRule2(i), "by col %d"%i ) \
            or self.hasDuplicate(self.byRule3(i), "by sqr %d"%i ) \
                : return False
        return True

    def solve(self, iterbase = 0):
        solutionlist = []
        if not self.isValid() and self.director:
            print "Invalid starting state!"
        else:
            if self.director: print "Seems legit..."
            keepgoing = True
            itercount = 0
            while keepgoing:
                itercount += 1
                keepgoing = False
                for i in range(self.config.SIZE):
                    keepgoing = keepgoing or self.elimination(self.byRule1(i), "by row %d"%i )
                    keepgoing = keepgoing or self.elimination(self.byRule2(i), "by col %d"%i )
                    keepgoing = keepgoing or self.elimination(self.byRule3(i), "by sqr %d"%i )
                # print("\nAfter %d+%d iteration(s): " % (iterbase, itercount, ))
                # self.dumpdata()

            success = "?"
            if keepgoing: success = "Failure"
            elif not self.isValid(): success = "Invalid"
            elif self.solved():
                success = "Success"
                solutionlist = [self.clone(), ]
                print "Success after %d iterations"%(iterbase + itercount,)
            else:
                aclone = self.clone()
                badcell = self.unsolvedCellsToBacktrack()[0]
                badcellclone = [cell for cell in aclone.allCellsFlat() if badcell.description == cell.description][0]
                if len(badcell.possible) > 3:
                    print(self)
                    print("Backtracking at %s with too many possible values: %s" %
                        (badcell.description, badcell.possible, ))
                for trial in badcell.possible:
                    badcellclone.value = trial
                    badcellclone.possible = trial
                    subsolutions = aclone.solve(iterbase + itercount)
                    if subsolutions:
                        print("Had to backtrack at this state:")
                        print(self.asText())
                    solutionlist.extend(subsolutions)
                success = "%d solution(s)" % (len(solutionlist), )

            # self.elimination(self.byRule3(8), "dbg")
        return solutionlist

    def allCellsFlat(self):
        SIZE = self.config.SIZE
        # print("size=%s rows=%s rowlens=%s" % (SIZE, len(self.rows), ",".join([str(len(row)) for row in self.rows])))
        return [ self.rows[i/SIZE][i%SIZE] for i in range(SIZE*SIZE) ]

    def unsolvedCells(self):
        return [ cell for cell in self.allCellsFlat() if cell.value == self.config.EMPTYCHAR ]

    def unsolvedCellsToBacktrack(self):
        unsolved = self.unsolvedCells()
        unsolved.sort(key=lambda cell: len(cell.possible))
        return unsolved

    def solved(self):
        return self.isValid() and len(self.unsolvedCells()) == 0

    def asText(self):
        text = "\n".join([self.configline, ] + ["".join([cell.value for cell in row]) for row in self.rows])
        return text

    def clone(self):
        return solver(self.asText(), False)


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
            return self.fmt_possibles%self.possible
        else:
            return self.fmt_filled%self.value

    def clone(self):
        return cell(self.value, self.description, self.possible, self.config)

            
if __name__=='__main__':
    import sys
    if len(sys.argv)<2:
        print "Usage: solver.py datafile.txt"
    else:
        f = open(sys.argv[1])
        data = f.read()
        s = solver(data)
        #s.dumpdata()
        #print repr(s.byRule3(8))
        solutions = s.solve()
        print "Found %d solution%s"%(len(solutions), "s" if len(solutions)>1 else "")
        for i in range(len(solutions)):
            print "Solution #%d"%(i+1)
            solutions[i].dumpdata()
