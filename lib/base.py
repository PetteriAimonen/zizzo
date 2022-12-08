# -*- coding: UTF-8 -*-

import sys
from . import tools

class UnsolvableException(Exception):
    '''This class cannot solve the series'''

class Solver:
    '''Dummy class to allow isinstance(item, Solver)'''

def debug(message):
    sys.stderr.write("Debug: " + str(message) + "\n")

class GeneratingSolver(Solver):
    '''Handlers for __getitem__ and generatelist() and necessary __init__ stuff, but no code for actually analyzing a series.
    This is used to produce a solver-like interface for an already known series.
    '''
    
    can_do_negative = True # Can generate(self, index) handle negative values for index?
    
    def __init__(self):
        self.cache = {}
        self._reversesolver = None
    
    def generate(self, index):
        '''Generate series' value at index. Index >= 0, including the initial series.
        1, 2, 3, 4, ... at index 2 is 3.
        
        If the value can't be generated, preferred action is to return None
        '''
        return None
    
    def generatelist(self, count):
        '''Generate <count> next entries after the initial series and return them as a list.'''
        start = len(self.series)
        return self[start : start + count]
    
    def reversesolver(self):
        '''Create a solver for solving at indexes < 0. This is required by some string solvers.
        To generate value at index -1, this solver is called with index 0. Consequently, -2 => 1, etc.
        
        Default action is to handle negative index by solving "backwards" by using generated list of
        20 entries. This works for most solvers, but might cause trouble with eg. OverflowSolver.
        '''
        from .dummysolvers import IndexOffsetSolver
        
        reverseseries = [self[i] for i in range(20)]
        
        try:
            index = reverseseries.index(None) # Cut it at first None
            reverseseries = reverseseries[:index]
        except ValueError:
            pass # None not found => OK
        
        debug(reverseseries)
        
        s = self.__class__(reverseseries)
        return IndexOffsetSolver(s, len(reverseseries))
    
    def __getitem__(self, key):
        '''Allows addressing a solver like solver[3] to generate value at index 3. Also caches results and handles slices.'''
        if isinstance(key, slice):
            if key.step:
                step = key.step
            else:
                step = 1
            
            if key.start:
                start = key.start
            else:
                start = 0
            
            return [self[i] for i in range(start, key.stop, step) if self[i] is not None]
        
        if not isinstance(key, int):
            raise IndexError
        
        if key < 0 and not self.can_do_negative:
            if not self._reversesolver:
                try:
                    self._reversesolver = self.reversesolver()
                except UnsolvableException:
                    debug("Reversesolver for %s failed" % repr(self))
                    raise IndexError
            
            return self._reversesolver[-1 - key]
        
        if key >= 0:
            try:
                return self.series[key]
            except IndexError:
                pass
            except AttributeError:
                pass
        
        if key not in self.cache:
            self.cache[key] = self.generate(key)
        
        return self.cache[key]


class BaseSolver(GeneratingSolver):
    minimum_entries = 1
    def __init__(self, series):
        GeneratingSolver.__init__(self)
        
        if len(series) < self.minimum_entries: # Not enough entries to validate this solver
            raise UnsolvableException
        
        self.series = series
        self.analyze()
    
    def analyze(self):
        raise UnsolvableException

    def params(self):
        '''Return a dict with the parameters specific to this solver'''
        return {}
    
    def validate(self, start = 0, nocache = False, series = None):
        '''Validate the generator, leaving first <start> entries unvalidated for recursive generators.
        Caching can be disabled with nocache, this way validation can be performed multiple times without
        messing up. Validating can also be done against some other series.
        '''
        if nocache:
            origcache = self.cache.copy()
        
        if not series:
            series = self.series
        
        try:
            for i in range(start, len(series)):
                if series[i] != self.generate(i):
                    raise UnsolvableException
        finally:
            if nocache:
                self.cache = origcache

    def score(self):
        '''Return a score representing how probably a human would choose this solution.
        0.0 = Never
        1.0 = This is an obvious solution
        '''
        raise NotImplementedError
    
    def name(self):
        return self.__class__.__name__

class WrapperSolver(Solver):
    '''Pass attribute access to another solver.'''
    _solver = None
    
    def __getattr__(self, name):
        if self._solver:
            return getattr(self._solver, name)
        else:
            raise AttributeError
    
    def __getitem__(self, key):
        if self._solver:
            return self._solver[key]
        else:
            raise AttributeError

class AlterSolver(WrapperSolver, GeneratingSolver):
    '''Modify values generated by other solvers. Replace generate(self, index) in subclass.
    The real solver can be accessed at self._solver
    '''
    def __init__(self, solver):
        GeneratingSolver.__init__(self)
        self._solver = solver
    
    def generate(self, index):
        return self._solver.generate(index)

class SelectSolver(WrapperSolver):
    '''Select the solver with best score. Subclasses should redefine _solverclasses to include the solvers to be tried.'''
    _solvingcache = {} # This instance of the dictionary is same for all instances and subclasses
    _solverclasses = []
    def __init__(self, series):
        tupleseries = (self.__class__, tools.recursivetuple(series)) # Lists are not hashable
        
        if tupleseries in self._solvingcache:
            self._solver = self._solvingcache[tupleseries]
            return
        
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
        self._solvingcache[tupleseries] = bestsolver

class TresholdSelectSolver(WrapperSolver):
    '''Try faster solver first. If it doesn't match or has too slow score, try the slower one'''
    _fastsolver = None
    _slowsolver = None
    _treshold = 0.0
    
    def __init__(self, series):
        self._solver = None
        try:
            self._solver = self._fastsolver(series)
        except UnsolvableException:
            pass
        
        if not self._solver or self._solver.score() < self._treshold:
            try:
                slow = self._slowsolver(series)
            except UnsolvableException:
                if not self._solver:
                    raise UnsolvableException
                else:
                    return
            
            if not self._solver or slow.score() > self._solver.score():
                self._solver = slow

def clearcache():
    '''Clear the internal solving cache, that is persistent for the whole session. This
    function is useful only when timing execution speed.
    '''
    SelectSolver._solvingcache = {}


