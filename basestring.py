import base
import complexnumeric
import basenumeric
import listnumeric
import tools
import overflow

class SingleCharSolver(base.BaseSolver):
    '''Strings consisting of a single character'''
    def analyze(self):
        for s in self.series:
            if len(s) != 1:
                raise base.UnsolvableException
        
        numseries = [ord(s[0]) for s in self.series]
        
        s = complexnumeric.CombinedNumericSolver(numseries)
        self.solver = overflow.OverflowSolver(s)
    
    def generate(self, index):
        return chr(self.solver[index])
    
    def score(self):
        return self.solver.score()
    
    def params(self):
        return {'solver': self.solver}

class SameCharSolver(base.BaseSolver):
    '''Strings with single character and varying length. A BB CCC DDDD etc.'''
    def analyze(self):
        charseries = []
        lengthseries = []
        for s in self.series:
            for char in s:
                if char != s[0]:
                    raise base.UnsolvableException # All characters of an entry should be equal
            
            charseries.append(s[0])
            lengthseries.append(len(s))
        
        self.charsolver = SingleCharSolver(charseries)
        self.lengthsolver = complexnumeric.CombinedNumericSolver(lengthseries)
    
    def generate(self, index):
        return self.charsolver[index] * self.lengthsolver[index]
    
    def score(self):
        return self.charsolver.score() * self.lengthsolver.score()
    
    def params(self):
        return {'charsolver': self.charsolver,
                'lengthsolver': self.lengthsolver}

class CharRepeatSolver(base.BaseSolver):
    '''A, AAB, AAABBC => [A] [A,B] [A,B,C] and [1] [2,1] [3,2,1]'''
    def analyze(self):
        charlistseries = []
        countseries = []
        
        for lst in self.series:
            blocks = tools.splittoblocks(lst)
            charlistseries.append([s[0] for s in blocks])
            countseries.append([len(s) for s in blocks])
        
        self.charlistsolver = listnumeric.CharListSolver(charlistseries)
        self.countsolver = listnumeric.CombinedListSolver(countseries)
    
    def generate(self, index):
        chars = self.charlistsolver[index]
        counts = self.countsolver[index]
        result = ""
        for i in range(len(chars)):
            result += chars[i] * counts[i]
        
        return result
    
    def score(self):
        return self.charlistsolver.score() * self.countsolver.score() * 0.4
    
    def params(self):
        return {'countsolver': self.countsolver,
                'charlistsolver': self.charlistsolver}

class YSeriesSolver(base.BaseSolver):
    '''Series for invidual chars in successive entries:
    ABCDEF
    BCDEFG each char + 1
    CDEFGH each char + 1
    '''
    def analyze(self):
        stringlen = len(self.series[0])
        for s in self.series:
            if len(s) != stringlen:
                raise base.UnsolvableException
        
        self.solvers = []
        for i in range(stringlen):
            charseries = [s[i] for s in self.series]
            solver = SingleCharSolver(charseries)
            self.solvers.append(solver)
    
    def generate(self, index):
        chars = [solver[index] for solver in self.solvers]
        return ''.join(chars)
    
    def score(self):
        score = 0.80
        for solver in self.solvers:
            score *= solver.score()
        
        return score
    
    def params(self):
        result = {}
        for i in range(len(self.solvers)):
            key = "solver%d" % i
            result[key] = self.solvers[i]
        
        return result

class XSeriesSolver(base.BaseSolver):
    '''String with internal sequence that is trimmed.
    ABCDEF internal sequence ABCDEFGHIJK...
    BCDEFG lefttrim + 1, length + 0
    CDEFGH lefttrim + 1, length + 0
    '''
    def analyze(self):
        wholestring = self.series[0]
        
        for s in self.series[1:]:
            i = tools.commonpart(wholestring, s)
            if i is not False:
                wholestring = wholestring[:i] + s
                continue
            
            i = tools.commonpart(s, wholestring)
            if i is not False:
                wholestring = s[:i] + wholestring
                continue
        
        charseries = list(wholestring)
        self.charsolver = SingleCharSolver(charseries)
        
        lefttrims = []
        lengths = []
        
        for s in self.series:
            lefttrim = wholestring.find(s)
            if lefttrim == -1:
                raise base.UnsolvableException
            
            lefttrims.append(lefttrim)
            lengths.append(len(s))
        
        self.trimsolver = complexnumeric.CombinedNumericSolver(lefttrims)
        self.lengthsolver = complexnumeric.CombinedNumericSolver(lengths)

    def generate(self, index):
        trim = self.trimsolver[index]
        length = self.lengthsolver[index]
        chars = [self.charsolver[i] for i in range(trim, trim+length)]
        return ''.join(chars)
    
    def score(self):
        return self.charsolver.score() * self.trimsolver.score() * self.lengthsolver.score()

    def params(self):
        return {'charsolver': self.charsolver,
                'trimsolver': self.trimsolver,
                'lengthsolver': self.lengthsolver}

class BaseStringSolver(base.SelectSolver):
    _solverclasses = [SingleCharSolver, SameCharSolver, CharRepeatSolver, 
                      YSeriesSolver, XSeriesSolver, basenumeric.RecurringSolver]

if __name__ == '__main__':
    print "Unit testing"
    
    a = BaseStringSolver(['A', 'AB', 'ABC'])
    assert a.generatelist(2) == ['ABCD', 'ABCDE']
    
    a = BaseStringSolver(['AZ', 'BY', 'CX'])
    assert a.generatelist(2) == ['DW', 'EV']
    
    a = CharRepeatSolver(['A', 'AAB', 'AAABBC'])
    assert a.generatelist(2) == ['AAAABBBCCD', 'AAAAABBBBCCCDDE']
    
    a = CharRepeatSolver(['ABC','AABC','AABBC','AABBCC','AAABBCC'])
    assert a.generatelist(2) == ['AAABBBCC','AAABBBCCC']
    
    
    print "OK"

