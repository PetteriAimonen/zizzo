# -*- coding: UTF-8 -*-

class UnsolvableException:
    '''This class cannot solve the series'''

class Solver:
    '''Dummy class to allow isinstance(item, Solver)'''

class BaseSolver(Solver):
    minimum_entries = 0
    def __init__(self, series):
        if len(series) < self.minimum_entries: # Not enough entries to validate this solver
            raise UnsolvableException
        
        self.series = series
        self.cache = {}
        
        for i in range(len(series)):
            self.cache[i] = series[i]
        
        self.analyze()
    
    def analyze(self):
        raise UnsolvableException
    
    def generate(self, index):
        '''Generates entry with specific index'''
        raise NotImplementedError

    def params(self):
        '''Return a dict with the parameters specific to this solver'''
        return {}
    
    def generatelist(self, count):
        '''Generate <count> next entries and return them as a list.'''
        result = []
        for i in range(len(self.series), len(self.series) + count):
            result.append(self[i])
        return result
    
    def validate(self,start):
        '''Validate the generator, leaving first <start> entries unvalidated for recursive generators'''
        for i in range(start, len(self.series)):
            if self.series[i] != self.generate(i):
                raise UnsolvableException

    def score(self):
        '''Return a score representing how probably a human would choose this solution.
        0.0 = Never
        1.0 = This is an obvious solution
        '''
        return 0.0
    
    def name(self):
        return self.__class__.__name__
    
    def __getitem__(self, key):
        if not isinstance(key, int) or key < 0:
            raise IndexError
        
        if not self.cache.has_key(key):
            self.cache[key] = self.generate(key)
        
        return self.cache[key]

class WrapperSolver(Solver):
    _solver = None
    def __getattr__(self, name):
        if self._solver:
            return getattr(self._solver, name)
        else:
            raise AttributeError

class SelectSolver(WrapperSolver):
    '''Select the solver with best score.'''
    _solverclasses = []
    def __init__(self, series):
        bestsolver = None
        bestscore = 0.
        
        for cls in self._solverclasses:
            try:
                solver = cls(series)
            except UnsolvableException:
                continue
            
            if solver.score() > bestscore:
                bestsolver = solver
                bestscore = solver.score()
        
        if not bestsolver:
            raise UnsolvableException
        
        self._solver = bestsolver





