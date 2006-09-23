import tools
import base
import basenumeric

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
        return self[index - 1] + self.numsolver[index - 1]
    
    def params(self):
        return {'first': self.series[0],
                'difference': self.numsolver}
    
    def score(self):
        return self.numsolver.score() * 0.4

class FibonacciSolver(base.BaseSolver):
    '''The fibonacci series with custom two first values'''

    minimum_entries = 3
    def analyze(self):
        self.validate(2)
    
    def generate(self, index):
        return self[index - 2] + self[index - 1]
    
    def score(self):
        if self[0] == 1 and self[1] == 1 and len(self.series) >= 5:
            return 0.3
        elif len(self.series) >= 7: # Non-standard fibonacci
            return 0.1
        else:
            return 0.05
    
    def params(self):
        return {'first_two': self.series[:2]}

class MergeSolver(base.BaseSolver):
    '''Interleave two or three other series.
    1,2,3,4 + 1,2,4,8 => 1,1,2,2,3,4,4,8
    '''
    
    solverclass = basenumeric.BaseNumericSolver
    minimum_entries = 4
    
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
    
    def analyze(self):
        from listnumeric import RepeatListSolver

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
            
            if self.solver[len(lists)][:len(current)] != current:
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
            if tries > 10:
                return None
        
        return self.generated[index]

    def score(self):
        if self.assumption:
            return 0.8 * self.solver.score()
        else:
            return self.solver.score()

    def params(self):
        return self.solver.params()

class LostSolver(base.BaseSolver): # ;)
    minimum_entries = 3
    def analyze(self):
        self.solver = RepeatSolver([4,8,15,16,23,42,4,8,15])
        self.validate(0)
    
    def generate(self, index):
        return self.solver[index]
    
    def score(self):
        return 0.01

class CombinedNumericSolver(base.SelectSolver):
    _solverclasses = [basenumeric.BaseNumericSolver, SumSolver, FibonacciSolver, MergeSolver, RepeatSolver, LostSolver]

if __name__ == '__main__':
    print "Unit testing"
    
    a = MergeSolver([1,1,2,2,4,3,8,4])
    assert a.generatelist(2) == [16,5]
    
    a = RepeatSolver([1,2,2,3,3,3])
    assert a.generatelist(5) == [4,4,4,4,5]
    
    print "OK"
