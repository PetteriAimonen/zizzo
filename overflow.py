import base

# When using numeric solvers for character values, there is a risk of overflows.
# This class attempts to detect correct behaviour in case of overflow.

# A bit hackish. Generated values are wrapped inside the allowed value range and inserted back to
# solver cache. Example with min = 0 and max = 9:
# 1) Something asks for solver[index]. Request is passed to this class, and it calls the inner solver.
# 2) Inner solver returns 12
# 3) 12 is wrapped to 2, and 2 is put into cache. WrapperSolver class wraps OverflowSolver.cache to
#    inner solver's cache
# 4) Recursive inner solver uses 2 from cache and generates next value based on it.

# Subclass both GeneratingSolver and WrapperSolver, this way only method we need to modify is generate()
class OverflowSolver(base.GeneratingSolver, base.WrapperSolver):
    def __init__(self, solver):
        self._solver = solver
        
        # Known common overflows, min and max
        overflowpoints = [
            (ord('0'), ord('9')),
            (ord('A'), ord('Z'))
            ]
        
        series_min = min(self._solver.series)
        series_max = max(self._solver.series)
        
        for overflow_min, overflow_max in overflowpoints:
            if series_min >= overflow_min and series_max <= overflow_max:
                self._min = overflow_min
                self._max = overflow_max
                break
        else:
            self.generate = self._solver.generate # Direct wrap
            self.name = self._solver.name
            self.params = self._solver.params
    
    def generate(self, index):
        value = self._solver.generate(index)
        return (value - self._min) % (self._max - self._min + 1) + self._min

    def name(self):
        return self.__class__.__name__
    
    def params(self):
        return {'solver': self._solver,
                'min': chr(self._min),
                'max': chr(self._max)}
