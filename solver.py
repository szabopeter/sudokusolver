#!/usr/bin/env python

UNIT_X, UNIT_Y = 3, 3
VALIDCHARS = "123456789"
EMPTYCHAR = "."
SIZE = len(VALIDCHARS)
if UNIT_X*UNIT_Y != SIZE:
    print "Invalid config!"

class solver:
    def __init__(self, textinput, director = True):
        self.director = director
        self.textinput = textinput
        self.rows = []
        for line in textinput.split("\n"):
            if line.strip().startswith("#"):
                continue

            validchars = [ch for ch in line if ch in VALIDCHARS + EMPTYCHAR]
            if len(validchars) == SIZE:
                linedata = [ cell(validchars[col], "(%d %d)"%(len(self.rows), col,)) for col in range(SIZE) ]
                self.rows.append(linedata)
            elif len(validchars) != 0:
                print "Invalid row: " + line.strip()
        #print str(self)
        if (len(self.rows) != SIZE):
            print "Invalid number of rows (%d)!"%(len(self.rows))

    def __str__(self):
        def separatorNeeded(col, separator):
            if (col-2) % UNIT_X == 0:
                return separator
            else:
                return ""

        #return "\n".join(" ".join([str(cell) for cell in linedata ]) for linedata in self.rows)
        return "\n".join([" ".join(
            [str(self.rows[row][col]) + separatorNeeded(col, " | ") for col in range(SIZE)])
            + separatorNeeded(row, "\n" + ("-" * (SIZE+3) * (SIZE +1) ) ) for row in range(SIZE)])
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
        row = UNIT_Y * (i / UNIT_Y)
        col = UNIT_X * (i % UNIT_Y)
        import itertools
        return [ self.rows[row+offset[0]][col+offset[1]] for offset in itertools.product(range(UNIT_X), range(UNIT_Y))]

    def hasDuplicate(self, cellist, contextdescription=""):
        usedvalues = []
        valuestocheck = [cell.value for cell in cellist if cell.value in VALIDCHARS]
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
            if pivotcell.value != EMPTYCHAR:
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
        for i in range(SIZE):
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
            while keepgoing and itercount < 1000:
                itercount += 1
                keepgoing = False
                for i in range(SIZE):
                    keepgoing = keepgoing or self.elimination(self.byRule1(i), "by row %d"%i )
                    keepgoing = keepgoing or self.elimination(self.byRule2(i), "by col %d"%i )
                    keepgoing = keepgoing or self.elimination(self.byRule3(i), "by sqr %d"%i )
                #print "After %d iteration(s): "%itercount
                #self.dumpdata()
            success = "?"
            if keepgoing: success ="Failure"
            elif not self.isValid(): success = "Invalid"
            elif self.solved():
                success = "Success"
                solutionlist = [self,]
                print "Success after %d iterations"%(iterbase + itercount,)
            else:
                aclone = self.clone()
                badcell = self.unsolvedCells()[0]
                badcellclone = [ cell for cell in aclone.allCellsFlat() if badcell.description == cell.description ][0]
                for trial in badcell.possible:
                    badcellclone.value = trial
                    badcellclone.possible = trial
                    solutionlist.extend(aclone.solve(iterbase + itercount))
                success = "%d solution(s)"%(len(solutionlist),)

            #self.elimination(self.byRule3(8), "dbg")
        return solutionlist

    def allCellsFlat(self):
        return [ self.rows[i/SIZE][i%SIZE] for i in range(SIZE*SIZE) ]

    def unsolvedCells(self):
        return [ cell for cell in self.allCellsFlat() if cell.value == EMPTYCHAR ]

    def solved(self):
        return self.isValid() and len(self.unsolvedCells()) == 0

    def asText(self):
        text = "\n".join(["".join([cell.value for cell in row]) for row in self.rows])
        return text

    def clone(self):
        return solver(self.asText(), False)

class cell:
    def __init__(self, value, description, possible = VALIDCHARS):
        self.description = description
        if value == ".":
            self.possible = possible
            self.value = EMPTYCHAR
        else:
            self.possible = value
            self.value = value

    def __repr__(self):
        return str(self)

    def __str__(self):
        if self.value == EMPTYCHAR:
            return "[%9s]"%self.possible
        else:
            return "    %3s    "%self.value

    def clone(self):
        return cell(self.value, self.description, self.possible)
        

            
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
        print "Found %d solutions"%(len(solutions),)
        for i in range(len(solutions)):
            print "Solution #%d"%(i+1)
            solutions[i].dumpdata()
