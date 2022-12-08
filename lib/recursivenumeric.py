from . import base
import math

'''Simple recursive numeric solvers, like fibonacci.
Not all implementations are recursive though, because simple calculations
are faster.
'''

class FibonacciSolver(base.BaseSolver):
    '''The fibonacci series with custom two first values
    '''
    minimum_entries = 3
    can_do_negative = False
    
    def analyze(self):
        self.validate(start = 2)
    
    def generate(self, index):
        return self[index - 2] + self[index - 1]
    
    def reversesolver(self):
        raise base.UnsolvableException
    
    def score(self):
        if self[:2] == [1,1]: # Standard fibonacci
            if len(self.series) >= 5:
                return 0.6
            else:
                return 0.05
        
        elif len(self.series) >= 7: # Non-standard fibonacci
            return 0.1
        else:
            return 0.05
    
    def params(self):
        return {'first_two': self.series[:2]}


class RecursiveExponentSolver(base.BaseSolver):
    '''Next value is previous value raised to some exponent.
    2, 4, 16, 256 etc.
    '''
    minimum_entries = 3
    can_do_negative = False
    
    def analyze(self):
        if self.series[0] == 1 or self.series[0] <= 0 or self.series[1] <= 0:
            raise base.UnsolvableException # Avoid math problems
        
        self.exponent = int(math.log(self.series[1]) / math.log(self.series[0]))
        self.first = self.series[0]
        
        self.validate(start = 1) # We need to validate index 1 also, to check for rounding errors
    
    def generate(self, index):
        return self.first ** (self.exponent ** index)
    
    def score(self):
        if self.exponent == 2:
            return 0.7
        else:
            return 0.3
    
    def params(self):
        return {'first': self.first,
                'exponent': self.exponent}

class FactorialSolver(base.BaseSolver):
    '''Next value is previous value multiplied by sequence index. Supports
    index offsetting: [1, 2, 6, 24] and [6, 24] both work.'''
    minimum_entries = 2
    can_do_negative = True
    
    def analyze(self):
        if self.series[0] == 0:
            raise base.UnsolvableException
        
        self.baseindex = self.series[1] // self.series[0] - 1
        self.validate(start = 1)

    def generate(self, index):
        if index > 0:
            return self[index - 1] * (index + self.baseindex)
        else:
            return self[index + 1] // (index + self.baseindex)

    def params(self):
        return {'baseindex': self.baseindex}
    
    def score(self):
        if self.baseindex in (1, 2):
            return 0.05
        else:
            return 0.01

if __name__ == '__main__':
    print("Unit tests")
    
    a = FibonacciSolver([1, 1, 2, 3, 5])
    assert a.generatelist(2) == [8, 13]
    
    a = RecursiveExponentSolver([3, 3**2, 3**4])
    assert a.generatelist(2) == [3**8, 3**16]
    
    a = FactorialSolver([1, 2, 6])
    assert a.generatelist(2) == [24, 120]

    print("OK")
