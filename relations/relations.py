import sys
import re

data = sys.stdin.readlines()

skip = ['UnsolvableException', 'Solver', 'BaseSolver']
cllist = []
clmatch = re.compile('^class ([a-zA-Z0-9_-]+)')
for line in data:
    m = clmatch.match(line)
    if m:
        cl = m.group(1)
        if not cl in skip:
            cllist.append(cl)


print("digraph G {")

clss = set(cllist)
cl = None
clr = []
for line in data:
    m = clmatch.match(line)
    if m and m.group(1) not in skip:
        cl = m.group(1)
        clr = []
        continue
    
    if not cl:
        continue
    
    for ccc in clss:
        if ccc == cl:
            continue
        if ccc in clr:
            continue
        if ccc in line:
            clr.append(ccc)
            #print line
            print(cl, "->", ccc)

print("}")