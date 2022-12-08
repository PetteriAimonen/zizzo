from . import base
from . import basenumeric
import math

class PrimeGenerator(base.GeneratingSolver):
    '''Generates the sequence of prime numbers.'''
    def is_prime(self, max_index, candidate):
        i = 0
        while i < max_index and self[i] <= math.sqrt(candidate):
            if candidate % self[i] == 0:
                return False
            
            i += 1
        
        return True
    
    def generate(self, index):
        if index < 0:
            return 0
        
        if index == 0:
            return 2
        
        candidate = self[index - 1] + 1
        while not self.is_prime(index, candidate):
            candidate += 1
        
        return candidate

prime_generator = PrimeGenerator()

class PrimeSolver(base.BaseSolver):
    '''Solve for a sequence of prime numbers, maybe skipping some of them.'''
    can_do_negative = True
    
    def analyze(self):
        # Find the prime positions for each value in the series
        # Outer loop checks the primes, so that we can discard non-prime
        # series quickly.
        positions = [None] * len(self.series)
        i = 0
        limit = max(self.series)
        while None in positions:
            prime = prime_generator[i]
            
            if prime > limit:
                raise base.UnsolvableException
            
            for s_index, s_entry in enumerate(self.series):
                if s_entry == prime:
                    positions[s_index] = i
                elif s_entry % prime == 0:
                    raise base.UnsolvableException
            
            i += 1
        
        # Solve the series of positions
        self.positionsolver = basenumeric.BaseNumericSolver(positions)
    
    def generate(self, index):
        position = self.positionsolver[index]
        return prime_generator[position]

    def params(self):
        return {'positionsolver': self.positionsolver}
    
    def score(self):
        return 0.1 * self.positionsolver.score()

if __name__ == '__main__':
    print("Unit tests")
    
    a = PrimeGenerator()
    assert a[:5] == [2, 3, 5, 7, 11]
    
    a = PrimeSolver([2, 3, 5])
    assert a.generatelist(2) == [7, 11]
    
    print("OK")