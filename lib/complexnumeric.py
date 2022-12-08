from . import tools
from . import base
from . import basenumeric

class SumSolver(base.BaseSolver):
    '''Sum of another solver up to the index.
    1,2,3,4 and start=1 => 1,2,4,7,11
    '''
    minimum_entries = 4
    
    def analyze(self):
        numseries = []
        
        for a,b in tools.tupleslices(self.series, 2):
            numseries.append(b - a)
        
        self.numsolver = basenumeric.BaseNumericSolver(numseries)
    
    def generate(self, index):
        if index > 0:
            return self[index - 1] + self.numsolver[index - 1]
        else:
            return self[index + 1] - self.numsolver[index + 1]
    
    def params(self):
        return {'first': self.series[0],
                'difference': self.numsolver}
    
    def score(self):
        return self.numsolver.score() * 0.4

class MergeSolver(base.BaseSolver):
    '''Interleave two or three other series.
    1,2,3,4 + 1,2,4,8 => 1,1,2,2,3,4,4,8
    '''
    
    solverclass = basenumeric.BaseNumericSolver # This class is used also for CombinedMergeSolver
    minimum_entries = 4
    can_do_negative = True
    
    def _analyze(self, mergecount):
        series = [list() for i in range(mergecount)]
        
        for i in range(len(self.series)):
            mod = i % mergecount
            series[mod].append(self.series[i])
        
        self.solvers = []
        for s in series:
            solver = self.solverclass(s)
            self.solvers.append(solver)
        
        self.mergecount = mergecount
    
    def analyze(self):
        try:
            self._analyze(2)
        except base.UnsolvableException:
            self._analyze(3)
    
    def generate(self, index):
        mod = index % self.mergecount
        idx = index // self.mergecount
        return self.solvers[mod][idx]
    
    def score(self):
        score = 0.8
        for solver in self.solvers:
            score *= solver.score()
        return score
    
    def params(self):
        result = {}
        for i in range(len(self.solvers)):
            name = 'solver%d' % i
            solver = self.solvers[i]
            result[name] = solver
        
        return result

class RepeatSolver(base.BaseSolver):
    '''Non-sequence version of ListRepeatSolver.
    [1], [2,2], [3,3,3] => 1,2,2,3,3,3
    '''
    minimum_entries = 3
    can_do_negative = False
    
    def analyze(self):
        from .listnumeric import RepeatListSolver

        lists = []
        current = []
        
        for a,b in tools.tupleslices(self.series, 2):
            current.append(a)
            if a != b:
                lists.append(current)
                current = []
        
        current.append(b)
        self.assumption = False
        
        self.generated = []
        self.genindex = 0
        
        try:
            self.solver = RepeatListSolver(lists)
            
            if self.solver[len(lists)][:len(current)] != current: # Check the part that was left over
                raise base.UnsolvableException
        
        except base.UnsolvableException:
            lists.append(current) # Assume that it ends at a list boundary
            self.assumption = True # For score calculation
            self.solver = RepeatListSolver(lists)
    
    def generate(self, index):
        tries = 0
        while len(self.generated) <= index:
            self.generated += self.solver[self.genindex]
            self.genindex += 1
            
            tries += 1
            if tries > 10: # RepeatSolver is no longer generating anything.. eg. 11111 2222 333 44 5
                return None
        
        return self.generated[index]

    def score(self):
        if self.assumption:
            return 0.8 * self.solver.score()
        else:
            return self.solver.score()

    def params(self):
        return self.solver.params()

from . import recursivenumeric
from . import primes

class CombinedNumericSolver(base.SelectSolver):
    _solverclasses = [basenumeric.BaseNumericSolver, SumSolver, MergeSolver, RepeatSolver,
                      recursivenumeric.FibonacciSolver, recursivenumeric.RecursiveExponentSolver,
                      recursivenumeric.FactorialSolver, primes.PrimeSolver]

if __name__ == '__main__':
    print("Unit testing")
    
    a = MergeSolver([1,1,2,2,4,3,8,4])
    assert a.generatelist(2) == [16,5]
    
    a = RepeatSolver([1,2,2,3,3,3])
    assert a.generatelist(5) == [4,4,4,4,5]
    
    print("OK")
