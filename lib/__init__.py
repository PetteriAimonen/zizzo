'''Libraries for Zizzo, the smart solver for alphanumeric series.
Usage example:

import lib

s = lib.Solver(['A', 'B', 'C'])
print s[:5]

=> ['A', 'B', 'C', 'D', 'E']
'''

from .combinedsolver import CombinedSolver as Solver
from .tools import describe
from .base import UnsolvableException

__version__ = 'epsilon'

__all__ = ['Solver', 'describe', 'UnsolvableException',
           'tools', 'base', 'alphabet']
