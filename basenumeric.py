import base

'''Handling of fundamental series with length 2 in order of priority:
1. AritmeticSolver with difference = 1
2. GeometricSolver with quotient = 2
3. AritmeticSolver with any difference
4. GeometricSolver with any quotient (never used)
'''

class AritmeticSolver(base.BaseSolver):
    minimum_entries = 2
    def analyze(self):
        self.difference = self.series[1] - self.series[0]
        self.validate(1)
    
    def generate(self, index):
        return self[index - 1] + self.difference
    
    def score(self):
        if len(self.series) == 2 and self.difference == 1:
            return 0.2
        elif len(self.series) == 2:
            return 0.1
        elif self.difference in [-1,0,1]:
            return 1.0
        else:
            return 0.8
    
    def params(self):
        return {'first': self.series[0],
                'difference': self.difference}

class GeometricSolver(base.BaseSolver):
    minimum_entries = 2
    def analyze(self):
        if self.series[0] == 0: # Protect against divide-by-zero
            raise base.UnsolvableException
        
        self.quotient = self.series[1] // self.series[0]
        self.validate(1)
    
    def generate(self, index):
        return self[index - 1] * self.quotient
    
    def score(self):
        if len(self.series) == 2 and self.quotient == 2:
            return 0.15 # A little more than aritmetic with difference != 1
        elif len(self.series) == 2:
            return 0.05
        elif self.quotient in [2,3]:
            return 0.8
        else:
            return 0.6
    
    def params(self):
        return {'first': self.series[0],
                'quotient': self.quotient}

class OffsetGeometricSolver(base.BaseSolver):
    '''Geometric series with constant offset'''
    minimum_entries = 4
    def analyze(self):
        # Formula solved from:
        # A2 - C     A3 - C
        #-------- = --------
        # A1 - C     A2 - C
        
        a1, a2, a3 = self.series[:3]
        
        try:
            self.offset = (a1 * a3 - a2 ** 2) // (a3 - 2 * a2 + a1)
        except ZeroDivisionError:
            raise base.UnsolvableException
        
        series = [n - self.offset for n in self.series]
        self.solver = GeometricSolver(series)
        
        self.validate(1)
    
    def generate(self, index):
        return self.solver[index] + self.offset
    
    def score(self):
        return self.solver.score() * 0.4
    
    def params(self):
        result = {'offset': self.offset}
        result.update(self.solver.params())
        return result

class RecurringSolver(base.BaseSolver):
    minimum_entries = 3
    def analyze(self):
        # Find the sortest length with which the series is recurring
        # For example 1,2,3,1,2,3,1,2,3 is recurring with both 3 and 6
        
        for self.length in range(2, len(self.series)):
            try:
                self.validate(self.length)
            except base.UnsolvableException:
                continue
            
            break
        
        else:
            raise base.UnsolvableException
    
    def generate(self, index):
        return self[index - self.length]
    
    def score(self):
        proof = len(self.series) - self.length # How many entries did we have to check if it is recurring?
        
        if proof >= self.length:
            return 0.8
        elif proof >= 3:
            return 0.6
        elif proof >= 2:
            return 0.4
        else:
            return 0.1
    
    def params(self):
        return {'series': self.series[:self.length]}

class BaseNumericSolver(base.SelectSolver):
    _solverclasses = [AritmeticSolver, GeometricSolver, OffsetGeometricSolver, RecurringSolver]

if __name__ == '__main__':
    print "Unit testing"

    a = AritmeticSolver([1,2,3])
    assert a.generatelist(2) == [4,5]
    
    a = GeometricSolver([1,2,4])
    assert a.generatelist(2) == [8,16]
    
    a = OffsetGeometricSolver([2,3,5,9])
    assert a.generatelist(2) == [17,33]
    
    r = RecurringSolver([1,2,1,2])
    assert r.generatelist(2) == [1,2]
    
    try:
        n = BaseNumericSolver([3,1,4,1,5])
    except base.UnsolvableException:
        pass
    else:
        raise AssertionError
    
    n = BaseNumericSolver([2,4,8,16])
    assert n.generatelist(2) == [32,64]
    
    print "OK"
