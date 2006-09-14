# -*- coding: UTF-8 -*-

import base

def tupleslices(list, size):
    '''Generates a list of tuples of a specific size. For example:
    tupleslices([1,2,3,4], 2) returns [(1,2), (2,3), (3,4)]
    '''

    result = []

    for i in range(len(list) - size + 1):
        t = tuple(list[i:(i + size)])
        result.append(t)
    
    return result

def stringpieces(string, size):
    '''Splits a string to substrings of a specific size.
    Partial pieces are not returned.
    '''
    result = []
    
    while len(string) >= size:
        result.append(string[:size])
        string = string[size:]
    
    return result

def mirrorstring(string):
    l = list(string)
    l.reverse()
    return ''.join(l)

def describe_lines(solver):
    heading = solver.name()
    result = [heading]
    
    items = solver.params().items()
    items.append(('score', "%0.2f" % solver.score()))
    items.sort(lambda a,b: cmp(a[0], b[0])) # Sort by key
    
    for i in range(len(items)):
        key, value = items[i]
        
        if i == len(items) - 1:
            prefix = "`- %s: " % key
            indent = "   "
        else:
            prefix = "|- %s: " % key
            indent = "|  "
        
        if isinstance(value, base.Solver):
            sublines = describe_lines(value)
            result.append(prefix + sublines[0])
            
            for line in sublines[1:]:
                result.append(indent + line)
        
        else:
            result.append(prefix + str(value))
    
    return result

def describe(solver):
    import base
    
    for line in describe_lines(solver):
        print line


if __name__ == '__main__':
    print "Unit testing"
    
    assert tupleslices(range(5), 2) == [(0,1), (1,2), (2,3), (3,4)]
    assert tupleslices(range(5), 4) == [(0,1,2,3), (1,2,3,4)]
    
    assert stringpieces('ABCDEFG', 2) == ['AB', 'CD', 'EF']
    
    assert mirrorstring('ABCD') == 'DCBA'
    
    print "OK"
