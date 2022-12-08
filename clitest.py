#!/usr/bin/env python

import sys
import time

import lib

def printlist(lst, heading = ""):
    maxlen = max([len(s) for s in lst])
    
    if maxlen >= 6:
        print(heading)
        
        for s in lst:
            print("   " + s)
        
        print("")
    else:
        print(heading + ' '.join(lst))


if __name__ == '__main__':
    scriptstart = time.time()


    if len(sys.argv) == 1:
        print('''Usage:
    For files with format (given) (generate) 1 2 3 4 5 ... on every line:
    %s file.txt

    To directly test a series:
    %s 1 2 3 4 5 ...
    ''' % (sys.argv[0], sys.argv[0]))
        
        raise SystemExit

    elif len(sys.argv) == 2:
        # Test from file
        file = open(sys.argv[1], 'rU')
        
        count = 0
        errors = 0
        individualtimes = []
        
        for line in file:
            tags = lib.alphabet.split(line)
            
            if len(tags) < 3: # An empty line
                continue
            
            count += 1
            given = int(tags[0])
            series = tags[2 : given + 2]
            correct = tags[given + 2:]
            
            printlist(series + correct, "Testing with %d given and %d generated for series: " % (given, len(correct)))
            
            try:
                lib.base.clearcache()
                start = time.time()
                solver = lib.Solver(series)
                individualtimes.append(time.time() - start)
            
            except lib.base.UnsolvableException:
                print("Unable to solve the series")
                print("--------------------------")
                errors += 1
                continue
            
            generated = solver.generatelist(len(correct))
            
            if generated != correct:
                errors += 1
                printlist(generated, "Unexpected result: ")
                lib.describe(solver)
                print("-------------------------")
        
        text = "%d series tested, of which %d failed." % (count, errors)
        print('-' * len(text))
        print(text)
        print("")
        
        print("Average time for one series: %0.3f" % (sum(individualtimes) / len(individualtimes)))
        print("Maximum time for one series: %0.3f" % max(individualtimes))
        print("Total time used: %0.3f" % (time.time() - scriptstart))
        
        

    else:
        # Test from commandline
        series = [s.upper().strip(' ,;\n') for s in sys.argv[1:]]
        printlist(series, "Initial series: ")
        
        solver = lib.Solver(series)
        printlist(solver.generatelist(10), "Next 10 entries: ")
        
        print("")
        lib.describe(solver)
        
        print("")
        print("Time used: %0.3f" % (time.time() - scriptstart))

