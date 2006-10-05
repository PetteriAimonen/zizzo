#!/usr/bin/env python

import lib

# Input data

f = open('zizzo.luk', 'rU')

given, generate = [int(s.strip()) for s in f.readline().split(' ')][:2]

series = []
for line in f:
    tags = lib.alphabet.split(line)
    
    if len(tags) == 0: # Empty line
        continue
    
    series.append(tags[0])

series = series[:given]

# Save information about newlines for output
if isinstance(f.newlines, str):
    newline = f.newlines
else:
    newline = '\n'

f.close()

# Solve series

solver = lib.Solver(series)

# Output data

output = open('zizzo.kir', 'w')

for entry in solver.generatelist(generate):
    output.write(entry + newline)

output.close()
