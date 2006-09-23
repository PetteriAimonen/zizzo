import combinedsolver
import tools

import sys

series = [s.upper() for s in sys.argv[1:]]
print "Initial series:", ' '.join(series)

s = combinedsolver.CombinedSolver(series)
print "Next 5 entries:", ' '.join(s.generatelist(5))
print "---"

tools.describe(s)
