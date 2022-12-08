# -*- coding: UTF-8 -*-

from . import base

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

def getprefix(string, char = None):
    '''Returns the length of prefix with the same characters.
    '0001234' => 3
    '''
    if not char:
        char = string[0]
    
    count = 0
    for c in string:
        if c != char:
            break
        
        count += 1
    
    return count

def mirrorstring(string):
    l = list(string)
    l.reverse()
    return ''.join(l)

def recursivetuple(mylist):
    '''Convert a list to a tuple, recursively:
    [[1,2,3], [3,4,5]] => ((1,2,3), (3,4,5))
    '''
    result = []
    
    for s in mylist:
        if isinstance(s, list):
            result.append(recursivetuple(s))
        else:
            result.append(s)
    
    return tuple(result)

def commonpart(string1, string2):
    '''String1 has string2 in its end.
    Return where the common part starts in string1:
    'abcdef' and 'defgh' => 3
    
    However, return False if there isn't a single exact solution:
    'aaa' and 'aaa' => False
    'abcd' and 'ghij' => False
    '''
    result = False
    
    for i in range(len(string1)):
        if string2.startswith(string1[i:]):
            if not result:
                result = i
            else:
                return False # Found another possible solution
    
    return result

def splittoblocks(string):
    '''Split to blocks of same letter:
    ABBCCDDD => ['A', 'BB', 'CC', 'DDD]
    '''
    result = []
    
    while string:
        char = string[0]
        block = ""
        for c in string:
            if c != char:
                break
            block += c
        
        result.append(block)
        string = string[len(block):]
    
    return result

def describe_lines(solver):
    heading = solver.name()
    result = [heading]
    
    items = list(solver.params().items()) + [('_sequence', solver.series)]
    items.append(('score', "%0.2f" % solver.score()))
    items.sort(key = lambda x: x[0]) # Sort by key
    
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
    '''Show the internal function of the solver as an ascii-based tree diagram.'''
    for line in describe_lines(solver):
        print(line)

def decreasing(series):
    '''Return true if the series is decreasing. 3,2,1 => True'''
    if not series[0] > series[-1]:
        return False
    
    for a,b in tupleslices(series, 2):
        if not a <= b:
            return False
    
    return True

if __name__ == '__main__':
    print("Unit testing")
    
    assert tupleslices(list(range(5)), 2) == [(0,1), (1,2), (2,3), (3,4)]
    assert tupleslices(list(range(5)), 4) == [(0,1,2,3), (1,2,3,4)]
    
    assert stringpieces('ABCDEFG', 2) == ['AB', 'CD', 'EF']
    
    assert getprefix('000123') == 3
    assert getprefix('1234', '0') == 0
    assert mirrorstring('ABCD') == 'DCBA'
    
    print("OK")
