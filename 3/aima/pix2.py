from csp import CSP, flatten, easy1
import itertools
# ______________________________________________________________________________
# PIC-A-SIX

_TOTAL = 5
_LIST = list(range(_TOTAL))
_ITER = itertools.count().__next__
_MATRIX = [[_ITER() for x in _LIST] for y in _LIST]
_ROWSM = _MATRIX
_COLSM = list(zip(*_MATRIX))

_NEIGHBORSM = {v: set() for v in flatten(_ROWSM)}
for x in _ROWSM:
    for y in x:
        if x.index(y) > 0 and x.index(y) < len(x) - 1:
            _NEIGHBORSM[y].add(y - 1)
            _NEIGHBORSM[y].add(y + 1)
        elif x.index(y) == 0:
            _NEIGHBORSM[y].add(y + 1)
        else:
            _NEIGHBORSM[y].add(y - 1)

for x in _COLSM:
    for y in x:
        if x.index(y) > 0 and x.index(y) < len(x) - 1:
            _NEIGHBORSM[y].add(y - _TOTAL)
            _NEIGHBORSM[y].add(y + _TOTAL)
        elif x.index(y) == 0:
            _NEIGHBORSM[y].add(y + _TOTAL)
        else:
            _NEIGHBORSM[y].add(y - _TOTAL)



class PicAPix(CSP):
    R3 = _LIST
    Cell = _ITER
    bgrid = _MATRIX
    rows = _ROWSM
    cols = _COLSM
    neighbors = _NEIGHBORSM

    def __init__(self, grid):
        domains = {}
        for var in flatten(self.bgrid):
            domains[var] = ['V', 'R', 'A', '.']
        
        CSP.__init__(self, None, domains, self.neighbors, self.pic_a_pix_constraint)

    def display(self, assignment):
        for row in self.bgrid:
            print(' '.join(map(str, row)))
    
    def pic_a_pix_constraint(A, a, B, b, recurse=0):

    	# Primer constraint G en columna 1
    	if(A==B): return True
        

s = PicAPix(easy1)

print("DOMAINS")
print(s.domains)
print("VARIABLES")
print(s.variables)

print("SUGGEST")
s.display(s.infer_assignment())