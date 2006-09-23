import base
import tools

import basenumeric
import complexnumeric
import basestring
import methodstringsolver

class NumericOnlySolver(base.BaseSolver):
    def analyze(self):
        try:
            numseries = [int(s) for s in self.series]
        except ValueError:
            raise base.UnsolvableException
        
        self.solver = complexnumeric.CombinedNumericSolver(numseries)
    
    def generate(self, index):
        return str(self.solver[index])
    
    def score(self):
        return self.solver.score()
    
    def params(self):
        return self.solver.params()
    
    def name(self):
        return self.solver.name()

class StringOnlySolver(base.SelectSolver):
	_solverclasses = [basestring.BaseStringSolver, methodstringsolver.MethodStringSolver]

class SplitSolver(base.BaseSolver):
    '''Solver a series with different kind of entries in start and in the end.
    Default compare method is str.isalpha:
    1A, 2B, 3C => 1,2,3 and A,B,C
    '''
    def compare(self, a, b):
        return a.isalpha() != b.isalpha()

    def analyze(self):
        startseries = []
        endseries = []
        splitpoints = []
        for s in self.series:
            if len(s) <= 1:
                raise base.UnsolvableException
            
            for i in range(1, len(s)):
                a = s[i - 1]
                b = s[i]
                
                if self.compare(a,b):
                    break
            else:
                raise base.UnsolvableException # No change detected
            
            splitpoints.append(i)
            startseries.append(s[:i])
            endseries.append(s[i:])
        
        for i in splitpoints:
            if i != 1:
                break
        else:
            raise base.UnsolvableException # There's no logic in splitting every string at the first character 
        
        self.startsolver = BaseCombinedSolver(startseries)
        self.endsolver = BaseCombinedSolver(endseries)
    
    def generate(self, index):
        return self.startsolver[index] + self.endsolver[index]

    def score(self):
        return self.startsolver.score() * self.endsolver.score() * 0.9
    
    def params(self):
        return {'startsolver': self.startsolver,
                'endsolver': self.endsolver}

class Diff1SplitSolver(SplitSolver):
    '''Detects change in difference'''
    difference = 1
    def compare(self, a, b):
        return ord(b) - ord(a) != self.difference

class Diffm1SplitSolver(Diff1SplitSolver):
    difference = -1

class AlternatingTypeSolver(base.SelectSolver):
    '''For AlternatingNumberStringSolver'''
    _solverclasses = [basenumeric.RecurringSolver, complexnumeric.RepeatSolver]

class AlternatingNumberStringSolver(base.BaseSolver):
    '''Series with alternating numbers and strings.'''
    def analyze(self):
        typeseries = []
        numseries = []
        strseries = []
        
        for s in self.series:
            if s.isalpha():
                typeseries.append(0)
                strseries.append(s)
            else:
                typeseries.append(1)
                numseries.append(s)
        
        self.numsolver = NumericOnlySolver(numseries)
        self.strsolver = StringOnlySolver(strseries)
        self.typesolver = AlternatingTypeSolver(typeseries)

    def generate(self, index):
        if self.typesolver[index]:
            numindex = len([i for i in range(index) if self.typesolver[i]])
            return self.numsolver[numindex]
        else:
            strindex = len([i for i in range(index) if not self.typesolver[i]])
            return self.strsolver[strindex]

    def score(self):
        return (self.numsolver.score() + self.strsolver.score()) / 2 * self.typesolver.score()
    
    def params(self):
        return {'numsolver': self.numsolver,
                'strsolver': self.strsolver,
                'typesolver': self.typesolver}

class FastCombinedSolver(base.SelectSolver):
    _solverclasses = [NumericOnlySolver, StringOnlySolver, AlternatingNumberStringSolver]

class SplitCombinedSolver(base.SelectSolver):
    _solverclasses = [SplitSolver, Diff1SplitSolver, Diffm1SplitSolver]

class BaseCombinedSolver(base.WrapperSolver):
    '''Recursive splitsolving is slow, so don't try it unless nothing else matches well enough'''
    def __init__(self, series):
        ok = True
        try:
            self._solver = FastCombinedSolver(series)
        except base.UnsolvableException:
            ok = False
        
        if not ok or self._solver.score() < 0.3:
            splitsolver = SplitCombinedSolver(series)
            if not ok or splitsolver.score() > self._solver.score():
                self._solver = splitsolver

class CombinedMergeSolver(complexnumeric.MergeSolver):
    solverclass = BaseCombinedSolver

class NonskipCombinedSolver(base.SelectSolver):
    _solverclasses = [BaseCombinedSolver, CombinedMergeSolver]

class SkipFirstSolver(base.BaseSolver):
    def analyze(self):
        for self.skip in range(1, len(self.series) // 2):
            series = self.series[self.skip:]
            try:
                self.solver = NonskipCombinedSolver(series)
                break
            except base.UnsolvableException:
                continue
        else:
            raise base.UnsolvableException
    
    def generate(self, index):
        return self.solver[index - self.skip]
    
    def score(self):
        return self.solver.score() * (1.0/float(self.skip + 1))
    
    def params(self):
        return {'skip': self.skip,
                'solver': self.solver}

class CombinedSolver(base.WrapperSolver):
    def __init__(self, series):
        try:
            self._solver = NonskipCombinedSolver(series)
        except base.UnsolvableException:
            self._solver = SkipFirstSolver(series)

if __name__ == '__main__':
    print "Unit testing"
    
    a = CombinedSolver(['A1', 'B2', 'C3'])
    assert a.generatelist(2) == ['D4', 'E5']
    
    a = CombinedSolver(['9A','10B','11C'])
    assert a.generatelist(2) == ['12D','13E']
    
    a = Diff1SplitSolver(['ABAB', 'ABCABC', 'ABCDABCD'])
    assert a.generatelist(2) == ['ABCDEABCDE', 'ABCDEFABCDEF']
    
    print "OK"

