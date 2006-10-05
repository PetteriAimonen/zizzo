import base

# Currently unused.
# Design decision: it is more interesting to try to find series in known series
# than just to find the series.

class KnownSeriesSolver(base.BaseSolver):
    '''Solver for known, constant series.'''
    contant_series = [
        (0.2, list('qwertyuiop')),
        (0.2, list('asdfghjkl')),
        (0.1, list('zxcvbnm'))
    ]
    
    def analyze(self):
        for score, series in self.contant_series:
            start = 0
            while self.series[0] in series[start:]:
                start = series.index(self.series[0])
                subset = series[start : start + len(self.series)]
                
                if self.series == subset:
                    # Found what we are looking for
                    self.result = series
                    self.offset = start
                    self.score = score
                    return
        
        raise base.UnsolvableException
    
    def generate(self, index):
        return self.result[index + self.offset]
    
    def params(self):
        return {'constant_series': self.result, 'offset': self.offset}
    
    def score(self):
        if len(self.series) == 1:
            return self.score / 5
        elif len(self.series) == 2:
            return self.score / 2
        else:
            return self.score

if __name__ == '__main__':
    print "Unit testing"
    
    a = KnownSeriesSolver(['f', 'g', 'h', 'j'])
    assert a.generatelist(2) == ['k', 'l']
    
    print "OK"
