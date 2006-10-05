import base
import math

'''The simplest numeric series. Most other solvers base on this.'''

# Scoring takes care for handling fundamental series with length 2. Order of preference:
# 1. AritmeticSolver with difference = -1, 0, 1    => score 0.2
# 2. GeometricSolver with quotient = 2    => score 0.15
# 3. AritmeticSolver with any difference    => score 0.1
# 4. GeometricSolver with any quotient    => score 0.05 (never used because 3. matches all)


class AritmeticSolver(base.BaseSolver):
    minimum_entries = 2
    can_do_negative = True
    
    def analyze(self):
        self.difference = self.series[1] - self.series[0]
        self.first = self.series[0]
        self.validate(start = 2)
    
    def generate(self, index):
        return self.first + self.difference * index
    
    def score(self):
        if len(self.series) == 2: # There wasn't enough entries to perform real validation
            if self.difference in [-1,0,1]:
                return 0.2
            else:
                return 0.1
        
        elif self.difference in [-1,0,1]:
            return 1.0
        
        else:
            return 0.8
    
    def params(self):
        return {'first': self.first,
                'difference': self.difference}

class FractionAritmeticSolver(base.BaseSolver):
    '''Solve aritmetic series with fractional addition.
    For example 1,1,2,2,3,3 => difference = 1/2
    '''
    minimum_entries = 3
    can_do_negative = True
    
    def analyze(self):
        for i in range(1, len(self.series)):
            difference = self.series[i] - self.series[0]
            if difference != 0:
                self.difference = difference
                self.period = i
                break
        else:
            raise base.UnsolvableException
        
        self.first = self.series[0]
        self.validate(start = i)
    
    def generate(self, index):
        return self.first + self.difference * (index // self.period)
    
    def score(self):
        if len(self.series) <= self.period * 2 + 1:
            return 0.1
        else:
            return 0.6
    
    def params(self):
        return {'difference': "%d/%d" % (self.difference, self.period),
                'first': self.first}

class GeometricSolver(base.BaseSolver):
    minimum_entries = 2
    can_do_negative = True
    
    def analyze(self):
        if self.series[0] == 0: # Protect against divide-by-zero
            raise base.UnsolvableException
        
        self.first = self.series[0]
        
        if self.series[1] % self.series[0] == 0:
            self.divide = False
            self.quotient = self.series[1] // self.series[0]
        
        elif self.series[0] % self.series[1] == 0:
            self.divide = True
            self.quotient = self.series[0] // self.series[1]
        
        else:
            raise base.UnsolvableException
        
        self.validate(start = 2)
    
    def generate(self, index):
        if self.divide:
            index = -index
        
        if index < 0:
            divisor = self.quotient ** abs(index)
            
            if self.first % divisor != 0: # Must be catched in validation
                return None
            
            return self.first // divisor
        else:
            return self.first * (self.quotient ** index)
    
    def score(self):
        if len(self.series) == 2:
            if self.quotient == 2:
                return 0.15
            else:
                return 0.05
            
        elif self.quotient in [2,3]:
            return 0.8
        else:
            return 0.6
    
    def params(self):
        if self.divide:
            return {'first': self.first,
                    'quotient': "1/%d" % self.quotient}
        else:
            return {'first': self.first,
                    'quotient': self.quotient}

class OffsetGeometricSolver(base.BaseSolver):
    '''Geometric series with constant offset'''
    minimum_entries = 4
    can_do_negative = True
    
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
    can_do_negative = True
    
    def analyze(self):
        # Find the sortest length with which the series is recurring
        # For example 1,2,3,1,2,3,1,2,3 is recurring with both 3 and 6
        
        for self.length in range(2, len(self.series)):
            try:
                self.validate(start = self.length, nocache = True)
            except base.UnsolvableException:
                continue
            
            break
        
        else:
            raise base.UnsolvableException
    
    def generate(self, index):
        return self.series[index % self.length]
    
    def score(self):
        # How many entries did we have for checking whether it is recurring?
        proof = len(self.series) - self.length
        
        if proof >= self.length:
            return 0.8
        elif proof >= 3:
            return 0.6
        elif proof >= 2:
            return 0.4
        else:
            return 0.05
    
    def params(self):
        return {'series': self.series[:self.length]}

class ExponentSolver(base.BaseSolver):
    '''Each value is its index raised to some exponent. Internal indexes start
    from zero, but starting from one is more natural for humans.
    '''
    minimum_entries = 3
    def analyze(self):
        if self.series[-1] <= 0:
            raise base.UnsolvableException # Avoid math problems
        
        self.exponent = int(math.log(self.series[-1]) / math.log(len(self.series))) # Calculate from the last entry
        self.validate()
    
    def generate(self, index):
        return (index + 1) ** self.exponent
    
    def score(self):
        if self.exponent == 2:
            return 0.6
        else:
            return 0.3
    
    def params(self):
        return {'exponent': self.exponent}

class BaseNumericSolver(base.SelectSolver):
    _solverclasses = [AritmeticSolver, FractionAritmeticSolver,
                      GeometricSolver, OffsetGeometricSolver,
                      RecurringSolver, ExponentSolver]

if __name__ == '__main__':
    print "Unit testing"

    a = AritmeticSolver([1,2,3])
    assert a.generatelist(2) == [4,5]
    
    a = GeometricSolver([1,2,4])
    assert a.generatelist(2) == [8,16]
    
    a = OffsetGeometricSolver([2,3,5,9])
    assert a.generatelist(2) == [17,33]
    
    a = RecurringSolver([1,2,1,2])
    assert a.generatelist(2) == [1,2]
    assert a[-5] == 2
    
    try:
        a = BaseNumericSolver([3,1,4,1,5])
    except base.UnsolvableException:
        pass
    else:
        raise AssertionError
    
    a = BaseNumericSolver([2,4,8,16])
    assert a.generatelist(2) == [32,64]
    
    print "OK"
