from . import base
from . import tools
from . import alphabet

from . import basenumeric
from . import complexnumeric
from . import basestring
from . import methodstringsolver
from . import recursivenumeric

CombinedNumericSolver = complexnumeric.CombinedNumericSolver

class ConstantZeroPaddingSolver(base.BaseSolver):
    '''An integer series padded to a specific width using zeros.'''
    def analyze(self):
        withzeros = [s for s in self.series if s.startswith('0')]
        
        if not withzeros:
            raise base.UnsolvableException # None have zeros
        
        self.zerolength = len(withzeros[0])
        for s in withzeros[1:]:
            if len(s) != self.zerolength:
                raise base.UnsolvableException # Non-constant padding
        
        for s in self.series:
            if s not in withzeros and len(s) < self.zerolength:
                raise base.UnsolvableException # Not all are padded
        
        try:
            numseries = [int(s) for s in self.series]
        except ValueError:
            raise base.UnsolvableException
        
        self.numsolver = CombinedNumericSolver(numseries)
    
    def generate(self, index):
        value = self.numsolver[index]
        format = "%0" + str(self.zerolength) + "d" # eg. %02d
        
        if value is None:
            return None
        
        return format % value
    
    def score(self):
        return self.numsolver.score()
    
    def params(self):
        return {'zerocount': self.zerolength,
                'numsolver': self.numsolver}

class ZeroSeriesPrefixSolver(base.BaseSolver):
    '''An integer series with zeros at front. The number of the zeros is
    determined by a numeric solver.
    '''
    def analyze(self):
        numseries = []
        zerocounts = []
        
        for s in self.series:
            try:
                numseries.append(int(s))
            except ValueError:
                raise base.UnsolvableException
            
            zerocounts.append(tools.getprefix(s, '0'))
        
        self.zerosolver = CombinedNumericSolver(zerocounts)
        self.numsolver = CombinedNumericSolver(numseries)
        
        if [i for i in zerocounts if i != 0]:
            self.dozero = True
        else:
            self.dozero = False
    
    def generate(self, index):
        return '0' * self.zerosolver[index] + str(self.numsolver[index])
    
    def score(self):
        if self.dozero:
            return 0.8 * self.zerosolver.score() * self.numsolver.score()
        else:
            return self.numsolver.score()
    
    def params(self):
        if self.dozero:
            return {'zerosolver': self.zerosolver,
                    'numsolver': self.numsolver}
        else:
            return self.numsolver.params()
    
    def name(self):
        if self.dozero:
            return self.__class__.__name__
        else:
            return self.numsolver.name()

class NumericOnlySolver(base.SelectSolver):
    _solverclasses = [ConstantZeroPaddingSolver, ZeroSeriesPrefixSolver]

class StringOnlySolver(base.SelectSolver):
    _solverclasses = [basestring.BaseStringSolver, methodstringsolver.MethodStringSolver, recursivenumeric.FibonacciSolver]

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
        
        self.startsolver = BaseCombinedSolver(startseries)
        self.endsolver = BaseCombinedSolver(endseries)
    
    def generate(self, index):
        return self.startsolver[index] + self.endsolver[index]

    def score(self):
        return self.startsolver.score() * self.endsolver.score() * 0.9
    
    def params(self):
        return {'startsolver': self.startsolver,
                'endsolver': self.endsolver}

class DiffPositiveSplitSolver(SplitSolver):
    '''Detects change in difference'''
    def compare(self, a, b):
        return alphabet.ord(b) - alphabet.ord(a) > 0

class DiffNegativeSplitSolver(SplitSolver):
    def compare(self, a, b):
        return alphabet.ord(b) - alphabet.ord(a) < 0

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


# Quite many classes follow. This is for time-optimizing the lookup at root level
# by not trying more complex solvers if simple ones match well

class BaseCombinedSolver(base.SelectSolver):
    _solverclasses = [NumericOnlySolver, StringOnlySolver, AlternatingNumberStringSolver,
                      SplitSolver, DiffPositiveSplitSolver, DiffNegativeSplitSolver]

class CombinedMergeSolver(complexnumeric.MergeSolver):
    solverclass = BaseCombinedSolver

class NonskipCombinedSolver(base.SelectSolver):
    _solverclasses = [BaseCombinedSolver, CombinedMergeSolver]

class SkipFirstSolver(base.BaseSolver):
    '''Try to solve difficult series by skipping some first values'''
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

class CombinedSolver(base.TresholdSelectSolver):
    '''Combined class for all supported solving patterns. Takes a series of
    alphanumeric strings as an argument. Entries can be accessed by several
    means:
    
    1) Like a sequence: solver[5] or solver[5:7]
    
    2) Solver.generatelist(count) generates the next values after the given
    initial series.
    '''

    # Use SkipFirstSolver as a fallback
    _fastsolver = BaseCombinedSolver
    _slowsolver = SkipFirstSolver
    _treshold = 0.1

if __name__ == '__main__':
    print("Unit testing")
    
    a = CombinedSolver(['A1', 'B2', 'C3'])
    assert a.generatelist(2) == ['D4', 'E5']
    
    a = CombinedSolver(['9A','10B','11C'])
    assert a.generatelist(2) == ['12D','13E']
    
    a = DiffPositiveSplitSolver(['ABAB', 'ABCABC', 'ABCDABCD'])
    assert a.generatelist(2) == ['ABCDEABCDE', 'ABCDEFABCDEF']
    
    a = BaseCombinedSolver(['SIIKA', 'SIIIKA', 'SIIIIKA'])
    assert a.generatelist(2) == ['SIIIIIKA', 'SIIIIIIKA']
    
    print("OK")

