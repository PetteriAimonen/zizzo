import base
import basenumeric
import complexnumeric

'''Solvers for series of lists of numbers.
[1,2,3], [2,3,4], [3,4,5] => AritmeticSolver with difference = 1 and start = [1,2,3]
[1], [1,2], [1,2,3] => AritmeticSolver with difference = 1, start = 1 and length = [1,2,3]
'''

class DummyAritmeticSolver(base.GeneratingSolver):
    def __init__(self, start, difference):
        base.GeneratingSolver.__init__(self)
        self.start = start
        self.difference = difference
    
    def generate(self, index):
        return self.start + index * self.difference

class AritmeticListSolver(base.BaseSolver):
    def analyze(self):
        startseries = []
        diffseries = []
        lengthseries = []
        for s in self.series:
            params = basenumeric.AritmeticSolver(s).params()
            startseries.append(params['first'])
            diffseries.append(params['difference'])
            lengthseries.append(len(s))
        
        self.startsolver = complexnumeric.CombinedNumericSolver(startseries)
        self.diffsolver = complexnumeric.CombinedNumericSolver(diffseries)
        self.lengthsolver = complexnumeric.CombinedNumericSolver(lengthseries)
    
    def generate(self, index):
        return DummyAritmeticSolver(self.startsolver[index],
                self.diffsolver[index]).generatelist(self.lengthsolver[index])
    
    def params(self):
        return {'startsolver': self.startsolver,
                'diffsolver': self.diffsolver,
                'lengthsolver': self.lengthsolver}
    
    def score(self):
        return self.startsolver.score() * self.diffsolver.score() * self.lengthsolver.score() * 0.8

class VaryLengthListSolver(base.BaseSolver):
    '''Same solver, but generate different amount of entries:
    [1] [1,2] [1,2,3] => [1,2,3,...] with length [1,2,3]
    '''
    
    def analyze(self):
        testseries = self.series[:]
        testseries.sort(lambda a,b: cmp(len(a), len(b))) # Use the longest entry
        
        self.numsolver = complexnumeric.CombinedNumericSolver(testseries[-1])
        
        lengthseries = [len(s) for s in self.series]
        self.lengthsolver = complexnumeric.CombinedNumericSolver(lengthseries)
        
        self.validate(0)
    
    def generate(self, index):
        length = self.lengthsolver[index]
        return self.numsolver[:length]
    
    def params(self):
        return {'numsolver': self.numsolver,
                'lengthsolver': self.lengthsolver}
    
    def score(self):
        return self.numsolver.score() * self.lengthsolver.score() * 0.9

class ReverseVaryLengthListSolver(VaryLengthListSolver):
    def __init__(self, series):
        self.realseries = series
        series = [s[::-1] for s in series]
        VaryLengthListSolver.__init__(self, series)
    
    def generate(self, index):
        length = self.lengthsolver[index]
        series = self.numsolver[:length]
        return series[::-1]
    
    def validate(self, *args, **kwargs):
        kwargs['series'] = self.realseries
        VaryLengthListSolver.validate(self, *args, **kwargs)
    
    def score(self):
        return 0.9 * VaryLengthListSolver.score(self)

class RepeatListSolver(base.BaseSolver):
    '''Numeric series, where each value is repeated - how many times is determined by another series - and
    converted to list, that is appended to previous entry. This is a intermediate stage used by RepeatSolver,
    but also as a list solver. RepeatSolver loses the block information, ie. for it 1,2,2,3,3 seems
    just as probable as 1,2,2,3,3,3
    
    1,2,3 repeated by 1,2,3 => [1], [2,2], [3,3,3]
    '''
    
    def analyze(self):
        values = []
        lengths = []
        
        for lst in self.series:
            if not isinstance(lst, list):
                raise base.UnsolvableException
            
            for entry in lst:
                if entry != lst[0]:
                    raise base.UnsolvableException
            
            values.append(lst[0])
            lengths.append(len(lst))
        
        self.valuesolver = basenumeric.BaseNumericSolver(values)
        self.lengthsolver = basenumeric.BaseNumericSolver(lengths)
    
    def generate(self, index):
        value = self.valuesolver[index]
        length = self.lengthsolver[index]
        return [value] * length

    def score(self):
        return 0.8 * self.valuesolver.score() * self.lengthsolver.score()
    
    def params(self):
        return {'valuesolver': self.valuesolver,
                'lengthsolver': self.lengthsolver}

class YListSolver(base.BaseSolver):
    def analyze(self):
        listlen = len(self.series[0])
        for s in self.series:
            if len(s) != listlen:
                raise base.UnsolvableException
        
        self.solvers = []
        for i in range(listlen):
            series = [s[i] for s in self.series]
            self.solvers.append(complexnumeric.CombinedNumericSolver(series))
    
    def generate(self, index):
        return [solver[index] for solver in self.solvers]
    
    def score(self):
        score = 0.80
        for solver in self.solvers:
            score *= solver.score()
        
        return score
    
    def params(self):
        result = {}
        for i in range(len(self.solvers)):
            key = "solver%d" % i
            result[key] = self.solvers[i]
        
        return result

class CombinedListSolver(base.SelectSolver):
    _solverclasses = [AritmeticListSolver, VaryLengthListSolver, ReverseVaryLengthListSolver,
                      basenumeric.RecurringSolver, RepeatListSolver, YListSolver]

class CharListSolver(base.BaseSolver):
    def analyze(self):
        numseries = []
        for s in self.series:
            numentry = [ord(e) for e in s]
            numseries.append(numentry)
        
        self.solver = CombinedListSolver(numseries)
    
    def generate(self, index):
        entry = self.solver[index]
        return [chr(s) for s in entry]

    def score(self):
        return self.solver.score()
    
    def params(self):
        return self.solver.params()


if __name__ == '__main__':
    print "Unit testing"

    a = AritmeticListSolver([[1,2,3], [2,3,4], [3,4,5]])
    assert a.generatelist(2) == [[4,5,6], [5,6,7]]
    
    a = CombinedListSolver([[1,2,3], [2,4,8], [1,2,3]])
    assert a.generatelist(2) == [[2,4,8], [1,2,3]]
    
    a = CombinedListSolver([[1], [2,1], [3,2,1]])
    assert a.generatelist(2) == [[4,3,2,1], [5,4,3,2,1]]
    
    a = CombinedListSolver([[1,1,1], [2,1,1], [2,2,1], [2,2,2], [3,2,2]])
    assert a.generatelist(2) == [[3,3,2], [3,3,3]]
    
    a = CharListSolver([['A'], ['A','B'], ['A','B','C']])
    assert a.generatelist(2) == [['A','B','C','D'], ['A','B','C','D','E']]
    
    a = YListSolver([[5,1,1], [4,1,2], [3,1,3]])
    assert a.generatelist(2) == [[2,1,4], [1,1,5]]

    print "OK"