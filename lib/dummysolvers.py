import base

'''These solvers generate values for an already known series.'''

class IndexOffsetSolver(base.AlterSolver):
    '''Used mostly for backwards-generation. If __init__ is called with offset = 2, and
    value at index 4 is to be generated, the real solver is passed index 4 + 2 = 6
    '''
    def __init__(self, solver, offset):
        base.AlterSolver.__init__(self, solver)
        
        self.offset = offset
    
    def generate(self, index):
        return self._solver[index + self.offset]

class NonNegativeOnlySolver(base.AlterSolver):
    '''Never return negative results. Only valid for numeric solvers.'''
    def __init__(self, solver):
        base.AlterSolver.__init__(self, solver)
    
    def generate(self, index):
        return max(self._solver[index], 0)

class DummyAritmeticSolver(base.GeneratingSolver):
    def __init__(self, first, difference):
        base.GeneratingSolver.__init__(self)
        
        self.first = first
        self.difference = difference
    
    def generate(self, index):
        return self.first + self.difference * index
