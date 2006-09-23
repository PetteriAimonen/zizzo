import base
import tools
import basestring

class BaseMethodSolver(base.BaseSolver):
    def simplify(self, s):
        '''Reimplemented by subclass. Convert string to a simple series, ABCBA -> ABC'''
    
    def modify(self, s):
        '''Reimplemented by subclass. Convert simple series to more complex series.'''
    
    def analyze(self):
        series = [self.simplify(s) for s in self.series]
        self.solver = basestring.BaseStringSolver(series)
    
    def generate(self, index):
        return self.modify(self.solver[index])
    
    def score(self):
        return self.solver.score()
    
    def params(self):
        return {'solver': self.solver}

class MirrorStringSolver(BaseMethodSolver):
    def simplify(self, s):
        return tools.mirrorstring(s)
    
    def modify(self, s):
        return tools.mirrorstring(s)

class OddAlternateMirrorStringSolver(BaseMethodSolver):
    mirrormodulus = 1
    def simplify(self, s, index):
        if index % 2 == self.mirrormodulus:
            return tools.mirrorstring(s)
        else:
            return s
    
    modify = simplify
    
    def analyze(self):
        series = [self.simplify(self.series[i], i) for i in range(len(self.series))]
        self.solver = basestring.BaseStringSolver(series)
    
    def generate(self, index):
        return self.modify(self.solver[index], index)

class EvenAlternateMirrorStringSolver(OddAlternateMirrorStringSolver):
    mirrormodulus = 0

class SingleSymmetricStringSolver(BaseMethodSolver):
    '''A, ABA, ABCBA'''
    def simplify(self, s):
        if len(s) % 2 != 1:
            raise base.UnsolvableException
        
        start = s[:len(s) // 2 + 1]
        end = tools.mirrorstring(s[len(s) // 2:])
        
        if start != end:
            raise base.UnsolvableException
        
        return start

    def modify(self, s):
        return s + tools.mirrorstring(s[:-1])

class DoubleSymmetricStringSolver(BaseMethodSolver):
    '''AA, ABBA, ABCCBA'''
    def simplify(self, s):
        if len(s) % 2 != 0:
            raise base.UnsolvableException
        
        start = s[:len(s) // 2]
        end = tools.mirrorstring(s[len(s) // 2:])
        
        if start != end:
            raise base.UnsolvableException
        
        return start

    def modify(self, s):
        return s + tools.mirrorstring(s)

class OddFirstAlternateAppendStringSolver(BaseMethodSolver):
    '''Append a letter alternatingly to either end.'''
    firstmodulus = 1

    def simplify(self, s):
        '''ECABD -> ABCDE'''
        result = ""
        
        if len(s) % 2 == self.firstmodulus: # Last char added was in the end
            result = s[-1]
            s = s[:-1]
        
        while s:
            result = s[0] + result
            s = s[1:]
            
            if not s:
                break
            
            result = s[-1] + result
            s = s[:-1]
        
        return result

    def modify(self, s):
        result = ""
        
        for i in range(len(s)):
            if i % 2 == self.firstmodulus:
                result = s[i] + result
            else:
                result = result + s[i]
        
        return result

    def score(self):
        return self.solver.score() * 0.6

class EvenFirstAlternateAppendStringSolver(OddFirstAlternateAppendStringSolver):
    firstmodulus = 0

class MethodStringSolver(base.SelectSolver):
    _solverclasses = [MirrorStringSolver, SingleSymmetricStringSolver, EvenFirstAlternateAppendStringSolver,
                      OddFirstAlternateAppendStringSolver, OddAlternateMirrorStringSolver, EvenAlternateMirrorStringSolver]

if __name__ == '__main__':
    print "Unit testing"
    
    a = MethodStringSolver(['A', 'ABA', 'ABCBA'])
    assert a.generatelist(2) == ['ABCDCBA', 'ABCDEDCBA']
    
    print "OK"