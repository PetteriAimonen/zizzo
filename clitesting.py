import combinedsolver
import tools

import sys

f = open(sys.argv[1], 'rU')

for line in f:
	tags = [s.strip(' \n') for s in line.split(' ')]
	given = int(tags[0])
	series = tags[2 : given + 2]
	correct = tags[given + 2:]
	
	print given, series, correct
	solver = combinedsolver.CombinedSolver(series)
	
	generated = solver.generatelist(len(correct))
	if generated != correct:
		print "Got: " + str(generated)
		tools.describe(solver)
		print "----------------"
		print ""

