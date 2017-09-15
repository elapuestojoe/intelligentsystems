"""CSP (Constraint Satisfaction Problems) problems and solvers. (Chapter 6)."""

from utils import argmin_random_tie, count, first
import search

from collections import defaultdict, Counter
from functools import reduce

import itertools
import re
import random
import copy

import numpy as np

class CSP(search.Problem):

    """This class describes finite-domain Constraint Satisfaction Problems.
    A CSP is specified by the following inputs:
        variables        A list of variables; each is atomic (e.g. int or string).
        domains     A dict of {var:[possible_value, ...]} entries.
        neighbors   A dict of {var:[var,...]} that for each variable lists
                    the other variables that participate in constraints.
        constraints A function f(A, a, B, b) that returns true if neighbors
                    A, B satisfy the constraint when they have values A=a, B=b
    In the textbook and in most mathematical definitions, the
    constraints are specified as explicit pairs of allowable values,
    but the formulation here is easier to express and more compact for
    most cases. (For example, the n-Queens problem can be represented
    in O(n) space using this notation, instead of O(N^4) for the
    explicit representation.) In terms of describing the CSP as a
    problem, that's all there is.

    However, the class also supports data structures and methods that help you
    solve CSPs by calling a search function on the CSP.  Methods and slots are
    as follows, where the argument 'a' represents an assignment, which is a
    dict of {var:val} entries:
        assign(var, val, a)     Assign a[var] = val; do other bookkeeping
        unassign(var, a)        Do del a[var], plus other bookkeeping
        nconflicts(var, val, a) Return the number of other variables that
                                conflict with var=val
        curr_domains[var]       Slot: remaining consistent values for var
                                Used by constraint propagation routines.
    The following methods are used only by graph_search and tree_search:
        actions(state)          Return a list of actions
        result(state, action)   Return a successor of state
        goal_test(state)        Return true if all constraints satisfied
    The following are just for debugging purposes:
        nassigns                Slot: tracks the number of assignments made
        display(a)              Print a human-readable representation
    """

    def __init__(self, variables, domains, neighbors, constraints):
        "Construct a CSP problem. If variables is empty, it becomes domains.keys()."
        variables = variables or list(domains.keys())

        self.variables = variables
        self.domains = domains
        self.neighbors = neighbors
        self.constraints = constraints
        self.initial = ()
        self.curr_domains = None
        self.nassigns = 0

    def assign(self, var, val, assignment):
        "Add {var: val} to assignment; Discard the old value if any."
        assignment[var] = val
        self.nassigns += 1

    def unassign(self, var, assignment):
        """Remove {var: val} from assignment.
        DO NOT call this if you are changing a variable to a new value;
        just call assign for that."""
        if var in assignment:
            del assignment[var]

    def nconflicts(self, var, val, assignment):
        "Return the number of conflicts var=val has with other variables."
        print("nconflicts1")
        # Subclasses may implement this more efficiently
        def conflict(var2):
            return (var2 in assignment and
                    not self.constraints(var, val, var2, assignment[var2]))
        return count(conflict(v) for v in self.neighbors[var])

    def display(self, assignment):
        "Show a human-readable representation of the CSP."
        # Subclasses can print in a prettier way, or display with a GUI
        print('CSP:', self, 'with assignment:', assignment)

    # These methods are for the tree- and graph-search interface:

    def actions(self, state):
        """Return a list of applicable actions: nonconflicting
        assignments to an unassigned variable."""
        if len(state) == len(self.variables):
            return []
        else:
            assignment = dict(state)
            var = first([v for v in self.variables if v not in assignment])
            return [(var, val) for val in self.domains[var]
                    if self.nconflicts(var, val, assignment) == 0]

    def result(self, state, action):
        "Perform an action and return the new state."
        (var, val) = action
        return state + ((var, val),)

    def goal_test(self, state):
        "The goal is to assign all variables, with all constraints satisfied."
        assignment = dict(state)
        return (len(assignment) == len(self.variables)
                and all(self.nconflicts(variables, assignment[variables], assignment) == 0
                        for variables in self.variables))

    # These are for constraint propagation

    def support_pruning(self):
        """Make sure we can prune values from domains. (We want to pay
        for this only if we use it.)"""
        if self.curr_domains is None:
            self.curr_domains = {v: list(self.domains[v]) for v in self.variables}

    def suppose(self, var, value):
        "Start accumulating inferences from assuming var=value."
        self.support_pruning()
        removals = [(var, a) for a in self.curr_domains[var] if a != value]
        self.curr_domains[var] = [value]
        return removals

    def prune(self, var, value, removals):
        "Rule out var=value."
        self.curr_domains[var].remove(value)
        if removals is not None:
            removals.append((var, value))

    def choices(self, var):
        "Return all values for var that aren't currently ruled out."
        return (self.curr_domains or self.domains)[var]

    def infer_assignment(self):
        "Return the partial assignment implied by the current inferences."
        self.support_pruning()
        return {v: self.curr_domains[v][0]
                for v in self.variables if 1 == len(self.curr_domains[v])}

    def restore(self, removals):
        "Undo a supposition and all inferences from it."
        for B, b in removals:
            self.curr_domains[B].append(b)

    # This is for min_conflicts search

    def conflicted_vars(self, current):
        "Return a list of variables in current assignment that are in conflict"
        return [var for var in self.variables
                if self.nconflicts(var, current[var], current) > 0]

# ______________________________________________________________________________
# Constraint Propagation with AC-3


def AC3(csp, queue=None, removals=None):
    """[Figure 6.3]"""
    if queue is None:
        queue = [(Xi, Xk) for Xi in csp.variables for Xk in csp.neighbors[Xi]]
    csp.support_pruning()
    while queue:
        (Xi, Xj) = queue.pop()
        if revise(csp, Xi, Xj, removals):
            if not csp.curr_domains[Xi]:
                return False
            for Xk in csp.neighbors[Xi]:
                if Xk != Xi:
                    queue.append((Xk, Xi))
    return True


def revise(csp, Xi, Xj, removals):
    "Return true if we remove a value."
    revised = False
    for x in csp.curr_domains[Xi][:]:
        # If Xi=x conflicts with Xj=y for every possible y, eliminate Xi=x
        if all(not csp.constraints(Xi, x, Xj, y) for y in csp.curr_domains[Xj]):
            csp.prune(Xi, x, removals)
            revised = True
    return revised

# ______________________________________________________________________________
# CSP Backtracking Search

# Variable ordering


def first_unassigned_variable(assignment, csp):
    "The default variable order."
    return first([var for var in csp.variables if var not in assignment])


def mrv(assignment, csp):
    "Minimum-remaining-values heuristic."
    return argmin_random_tie(
        [v for v in csp.variables if v not in assignment],
        key=lambda var: num_legal_values(csp, var, assignment))


def num_legal_values(csp, var, assignment):
    if csp.curr_domains:
        return len(csp.curr_domains[var])
    else:
        return count(csp.nconflicts(var, val, assignment) == 0
                     for val in csp.domains[var])

# Value ordering


def unordered_domain_values(var, assignment, csp):
    "The default value order."
    return csp.choices(var)


def lcv(var, assignment, csp):
    "Least-constraining-values heuristic."
    return sorted(csp.choices(var),
                  key=lambda val: csp.nconflicts(var, val, assignment))

# Inference


def no_inference(csp, var, value, assignment, removals):
    return True


def forward_checking(csp, var, value, assignment, removals):
    "Prune neighbor values inconsistent with var=value."
    for B in csp.neighbors[var]:
        if B not in assignment:
            for b in csp.curr_domains[B][:]:
                if not csp.constraints(var, value, B, b):
                    csp.prune(B, b, removals)
            if not csp.curr_domains[B]:
                return False
    return True


def mac(csp, var, value, assignment, removals):
    "Maintain arc consistency."
    return AC3(csp, [(X, var) for X in csp.neighbors[var]], removals)

# The search, proper


def backtracking_search(csp,
                        select_unassigned_variable=first_unassigned_variable,
                        order_domain_values=unordered_domain_values,
                        inference=no_inference):
    """[Figure 6.5]
    """

    def backtrack(assignment):
        if len(assignment) == len(csp.variables):
            return assignment
        var = select_unassigned_variable(assignment, csp)
        for value in order_domain_values(var, assignment, csp):
            if 0 == csp.nconflicts(var, value, assignment):
                csp.assign(var, value, assignment)
                removals = csp.suppose(var, value)
                if inference(csp, var, value, assignment, removals):
                    result = backtrack(assignment)
                    if result is not None:
                        return result
                csp.restore(removals)
        csp.unassign(var, assignment)
        return None

    result = backtrack({})
    assert result is None or csp.goal_test(result)
    return result

# ______________________________________________________________________________
# Min-conflicts hillclimbing search for CSPs


def min_conflicts(csp, max_steps=100000):
    """Solve a CSP by stochastic hillclimbing on the number of conflicts."""
    # Generate a complete assignment for all variables (probably with conflicts)
    csp.current = current = {}
    print("current  ", current)
    for var in csp.variables:
        val = min_conflicts_value(csp, var, current)
        csp.assign(var, val, current)
    # Now repeatedly choose a random conflicted variable and change it
    for i in range(max_steps):
        conflicted = csp.conflicted_vars(current)
        if not conflicted:
            return current
        var = random.choice(conflicted)
        val = min_conflicts_value(csp, var, current)
        csp.assign(var, val, current)
    return None


def min_conflicts_value(csp, var, current):
    """Return the value that will give var the least number of conflicts.
    If there is a tie, choose at random."""
    return argmin_random_tie(csp.domains[var],
                             key=lambda val: csp.nconflicts(var, val, current))

# ______________________________________________________________________________


def tree_csp_solver(csp):
    "[Figure 6.11]"
    assignment = {}
    root = csp.variables[0]
    X, parent = topological_sort(csp.variables, root)
    for Xj in reversed(X):
        if not make_arc_consistent(parent[Xj], Xj, csp):
            return None
    for Xi in X:
        if not csp.curr_domains[Xi]:
            return None
        assignment[Xi] = csp.curr_domains[Xi][0]
    return assignment


def topological_sort(xs, x):
    raise NotImplementedError


def make_arc_consistent(Xj, Xk, csp):
    raise NotImplementedError

# ______________________________________________________________________________
# Map-Coloring Problems


class UniversalDict:

    """A universal dict maps any key to the same value. We use it here
    as the domains dict for CSPs in which all variables have the same domain.
    >>> d = UniversalDict(42)
    >>> d['life']
    42
    """

    def __init__(self, value): self.value = value

    def __getitem__(self, key): return self.value

    def __repr__(self): return '{Any: %r}' % self.value


def different_values_constraint(A, a, B, b):
    "A constraint saying two neighboring variables must differ in value."
    return a != b


def MapColoringCSP(colors, neighbors):
    """Make a CSP for the problem of coloring a map with different colors
    for any two adjacent regions.  Arguments are a list of colors, and a
    dict of {region: [neighbor,...]} entries.  This dict may also be
    specified as a string of the form defined by parse_neighbors."""
    if isinstance(neighbors, str):
        neighbors = parse_neighbors(neighbors)
    return CSP(list(neighbors.keys()), UniversalDict(colors), neighbors,
               different_values_constraint)


def parse_neighbors(neighbors, variables=[]):
    """Convert a string of the form 'X: Y Z; Y: Z' into a dict mapping
    regions to neighbors.  The syntax is a region name followed by a ':'
    followed by zero or more region names, followed by ';', repeated for
    each region name.  If you say 'X: Y' you don't need 'Y: X'.
    >>> parse_neighbors('X: Y Z; Y: Z') == {'Y': ['X', 'Z'], 'X': ['Y', 'Z'], 'Z': ['X', 'Y']}
    True
    """
    dic = defaultdict(list)
    specs = [spec.split(':') for spec in neighbors.split(';')]
    for (A, Aneighbors) in specs:
        A = A.strip()
        for B in Aneighbors.split():
            dic[A].append(B)
            dic[B].append(A)
    return dic

australia = MapColoringCSP(list('RGB'),
                           'SA: WA NT Q NSW V; NT: WA Q; NSW: Q V; T: ')

usa = MapColoringCSP(list('RGBY'),
                     """WA: OR ID; OR: ID NV CA; CA: NV AZ; NV: ID UT AZ; ID: MT WY UT;
        UT: WY CO AZ; MT: ND SD WY; WY: SD NE CO; CO: NE KA OK NM; NM: OK TX;
        ND: MN SD; SD: MN IA NE; NE: IA MO KA; KA: MO OK; OK: MO AR TX;
        TX: AR LA; MN: WI IA; IA: WI IL MO; MO: IL KY TN AR; AR: MS TN LA;
        LA: MS; WI: MI IL; IL: IN KY; IN: OH KY; MS: TN AL; AL: TN GA FL;
        MI: OH IN; OH: PA WV KY; KY: WV VA TN; TN: VA NC GA; GA: NC SC FL;
        PA: NY NJ DE MD WV; WV: MD VA; VA: MD DC NC; NC: SC; NY: VT MA CT NJ;
        NJ: DE; DE: MD; MD: DC; VT: NH MA; MA: NH RI CT; CT: RI; ME: NH;
        HI: ; AK: """)

france = MapColoringCSP(list('RGBY'),
                        """AL: LO FC; AQ: MP LI PC; AU: LI CE BO RA LR MP; BO: CE IF CA FC RA
        AU; BR: NB PL; CA: IF PI LO FC BO; CE: PL NB NH IF BO AU LI PC; FC: BO
        CA LO AL RA; IF: NH PI CA BO CE; LI: PC CE AU MP AQ; LO: CA AL FC; LR:
        MP AU RA PA; MP: AQ LI AU LR; NB: NH CE PL BR; NH: PI IF CE NB; NO:
        PI; PA: LR RA; PC: PL CE LI AQ; PI: NH NO CA IF; PL: BR NB CE PC; RA:
        AU BO FC PA LR""")

# ______________________________________________________________________________
# n-Queens Problem


def queen_constraint(A, a, B, b):
    """Constraint is satisfied (true) if A, B are really the same variable,
    or if they are not in the same row, down diagonal, or up diagonal."""
    return A == B or (a != b and A + a != B + b and A - a != B - b)


class NQueensCSP(CSP):

    """Make a CSP for the nQueens problem for search with min_conflicts.
    Suitable for large n, it uses only data structures of size O(n).
    Think of placing queens one per column, from left to right.
    That means position (x, y) represents (var, val) in the CSP.
    The main structures are three arrays to count queens that could conflict:
        rows[i]      Number of queens in the ith row (i.e val == i)
        downs[i]     Number of queens in the \ diagonal
                     such that their (x, y) coordinates sum to i
        ups[i]       Number of queens in the / diagonal
                     such that their (x, y) coordinates have x-y+n-1 = i
    We increment/decrement these counts each time a queen is placed/moved from
    a row/diagonal. So moving is O(1), as is nconflicts.  But choosing
    a variable, and a best value for the variable, are each O(n).
    If you want, you can keep track of conflicted variables, then variable
    selection will also be O(1).
    >>> len(backtracking_search(NQueensCSP(8)))
    8
    """

    def __init__(self, n):
        """Initialize data structures for n Queens."""
        CSP.__init__(self, list(range(n)), UniversalDict(list(range(n))),
                     UniversalDict(list(range(n))), queen_constraint)

        self.rows = [0]*n
        self.ups = [0]*(2*n - 1)
        self.downs = [0]*(2*n - 1)

    def nconflicts(self, var, val, assignment):
        # print(assignment)
        """The number of conflicts, as recorded with each assignment.
        Count conflicts in row and in up, down diagonals. If there
        is a queen there, it can't conflict with itself, so subtract 3."""
        n = len(self.variables)
        c = self.rows[val] + self.downs[var+val] + self.ups[var-val+n-1]
        if assignment.get(var, None) == val:
            c -= 3
        return c

    def assign(self, var, val, assignment):
        "Assign var, and keep track of conflicts."
        # print(assignment)
        oldval = assignment.get(var, None)
        if val != oldval:
            if oldval is not None:  # Remove old val if there was one
                self.record_conflict(assignment, var, oldval, -1)
            self.record_conflict(assignment, var, val, +1)
            CSP.assign(self, var, val, assignment)

    def unassign(self, var, assignment):
        # print(assignment)
        "Remove var from assignment (if it is there) and track conflicts."
        if var in assignment:
            self.record_conflict(assignment, var, assignment[var], -1)
        CSP.unassign(self, var, assignment)

    def record_conflict(self, assignment, var, val, delta):
        "Record conflicts caused by addition or deletion of a Queen."
        n = len(self.variables)
        self.rows[val] += delta
        self.downs[var + val] += delta
        self.ups[var - val + n - 1] += delta

    def display(self, assignment):
        "Print the queens and the nconflicts values (for debugging)."
        n = len(self.variables)
        for val in range(n):
            for var in range(n):
                if assignment.get(var, '') == val:
                    ch = 'Q'
                elif (var + val) % 2 == 0:
                    ch = '.'
                else:
                    ch = '-'
                print(ch, end=' ')
            print('    ', end=' ')
            for var in range(n):
                if assignment.get(var, '') == val:
                    ch = '*'
                else:
                    ch = ' '
                print(str(self.nconflicts(var, val, assignment)) + ch, end=' ')
            print()


# queens = NQueensCSP(8)
# print("_____")
# print(min_conflicts(queens, 10000000))
# print("_____")
# ______________________________________________________________________________
# Sudoku


def flatten(seqs): return sum(seqs, [])

easy1 = '..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..'  # noqa
harder1 = '4173698.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'  # noqa

_R3 = list(range(3))
_CELL = itertools.count().__next__
_BGRID = [[[[_CELL() for x in _R3] for y in _R3] for bx in _R3] for by in _R3]
_BOXES = flatten([list(map(flatten, brow)) for brow in _BGRID])
_ROWS = flatten([list(map(flatten, zip(*brow))) for brow in _BGRID])
_COLS = list(zip(*_ROWS))

_NEIGHBORS = {v: set() for v in flatten(_ROWS)}
for unit in map(set, _BOXES + _ROWS + _COLS):
    for v in unit:
        _NEIGHBORS[v].update(unit - set([v]))


class Sudoku(CSP):

    """A Sudoku problem.
    The box grid is a 3x3 array of boxes, each a 3x3 array of cells.
    Each cell holds a digit in 1..9. In each box, all digits are
    different; the same for each row and column as a 9x9 grid.
    >>> e = Sudoku(easy1)
    >>> e.display(e.infer_assignment())
    . . 3 | . 2 . | 6 . .
    9 . . | 3 . 5 | . . 1
    . . 1 | 8 . 6 | 4 . .
    ------+-------+------
    . . 8 | 1 . 2 | 9 . .
    7 . . | . . . | . . 8
    . . 6 | 7 . 8 | 2 . .
    ------+-------+------
    . . 2 | 6 . 9 | 5 . .
    8 . . | 2 . 3 | . . 9
    . . 5 | . 1 . | 3 . .
    >>> AC3(e); e.display(e.infer_assignment())
    True
    4 8 3 | 9 2 1 | 6 5 7
    9 6 7 | 3 4 5 | 8 2 1
    2 5 1 | 8 7 6 | 4 9 3
    ------+-------+------
    5 4 8 | 1 3 2 | 9 7 6
    7 2 9 | 5 6 4 | 1 3 8
    1 3 6 | 7 9 8 | 2 4 5
    ------+-------+------
    3 7 2 | 6 8 9 | 5 1 4
    8 1 4 | 2 5 3 | 7 6 9
    6 9 5 | 4 1 7 | 3 8 2
    >>> h = Sudoku(harder1)
    >>> backtracking_search(h, select_unassigned_variable=mrv, inference=forward_checking) is not None
    True
    """
    R3 = _R3
    Cell = _CELL
    bgrid = _BGRID
    boxes = _BOXES
    rows = _ROWS
    cols = _COLS
    neighbors = _NEIGHBORS

    def __init__(self, grid):
        """Build a Sudoku problem from a string representing the grid:
        the digits 1-9 denote a filled cell, '.' or '0' an empty one;
        other characters are ignored."""
        squares = iter(re.findall(r'\d|\.', grid))
        domains = {var: [ch] if ch in '123456789' else '123456789'
                   for var, ch in zip(flatten(self.rows), squares)}
        for _ in squares:
            raise ValueError("Not a Sudoku grid", grid)  # Too many squares
        CSP.__init__(self, None, domains, self.neighbors, different_values_constraint)

    def display(self, assignment):
        def show_box(box): return [' '.join(map(show_cell, row)) for row in box]

        def show_cell(cell): return str(assignment.get(cell, '.'))

        def abut(lines1, lines2): return list(
            map(' | '.join, list(zip(lines1, lines2))))
        print('\n------+-------+------\n'.join(
            '\n'.join(reduce(
                abut, map(show_box, brow))) for brow in self.bgrid))
# ______________________________________________________________________________
# The Zebra Puzzle


def Zebra():
    "Return an instance of the Zebra Puzzle."
    Colors = 'Red Yellow Blue Green Ivory'.split()
    Pets = 'Dog Fox Snails Horse Zebra'.split()
    Drinks = 'OJ Tea Coffee Milk Water'.split()
    Countries = 'Englishman Spaniard Norwegian Ukranian Japanese'.split()
    Smokes = 'Kools Chesterfields Winston LuckyStrike Parliaments'.split()
    variables = Colors + Pets + Drinks + Countries + Smokes
    domains = {}
    for var in variables:
        domains[var] = list(range(1, 6))
    domains['Norwegian'] = [1]
    domains['Milk'] = [3]
    neighbors = parse_neighbors("""Englishman: Red;
                Spaniard: Dog; Kools: Yellow; Chesterfields: Fox;
                Norwegian: Blue; Winston: Snails; LuckyStrike: OJ;
                Ukranian: Tea; Japanese: Parliaments; Kools: Horse;
                Coffee: Green; Green: Ivory""", variables)
    for type in [Colors, Pets, Drinks, Countries, Smokes]:
        for A in type:
            for B in type:
                if A != B:
                    if B not in neighbors[A]:
                        neighbors[A].append(B)
                    if A not in neighbors[B]:
                        neighbors[B].append(A)

    def zebra_constraint(A, a, B, b, recurse=0):
        #print("A ", A)
        #print("a ", a)
        #print("B ", B)
        #print("b ", b)
        #print("r ", recurse)
        same = (a == b)
        next_to = abs(a - b) == 1
        if A == 'Englishman' and B == 'Red':
            return same
        if A == 'Spaniard' and B == 'Dog':
            return same
        if A == 'Chesterfields' and B == 'Fox':
            return next_to
        if A == 'Norwegian' and B == 'Blue':
            return next_to
        if A == 'Kools' and B == 'Yellow':
            return same
        if A == 'Winston' and B == 'Snails':
            return same
        if A == 'LuckyStrike' and B == 'OJ':
            return same
        if A == 'Ukranian' and B == 'Tea':
            return same
        if A == 'Japanese' and B == 'Parliaments':
            return same
        if A == 'Kools' and B == 'Horse':
            return next_to
        if A == 'Coffee' and B == 'Green':
            return same
        if A == 'Green' and B == 'Ivory':
            return a - 1 == b
        if recurse == 0:
            return zebra_constraint(B, b, A, a, 1)
        if ((A in Colors and B in Colors) or
                (A in Pets and B in Pets) or
                (A in Drinks and B in Drinks) or
                (A in Countries and B in Countries) or
                (A in Smokes and B in Smokes)):
            return not same
        raise Exception('error')
    return CSP(variables, domains, neighbors, zebra_constraint)


def solve_zebra(algorithm=min_conflicts, **args):
    z = Zebra()
    
    print("variables\n")
    print(z.variables)
    print("\n\ndomain\n")
    print(z.domains)
    print("\n\nconstraints\n")
    print(z.constraints)
    print("\n\nneighbors\n")
    print(z.neighbors)
    # ans = algorithm(z, **args)
    # for h in range(1, 6):
    #     print('House', h, end=' ')
    #     for (var, val) in ans.items():
    #         if val == h:
    #             print(var, end=' ')
    #     print()
    # return ans['Zebra'], ans['Water'], z.nassigns, ans



# ----------------------------------
# SUDOKU
# ----------------------------------
#e = Sudoku(easy1)
#print(e.domains)
#e.display(e.infer_assignment())
#print()
#AC3(e)
#e.display(e.infer_assignment())

#h = Sudoku(harder1)
#backtracking_search(h, select_unassigned_variable=mrv, inference=forward_checking) is not None

#z = Zebra()
#z.display(z.infer_assignment())
#print()
#AC3(z)
#z.display(z.infer_assignment())
#solve_zebra()
#z = Zebra()
#z.display(z.infer_assignment())
#print()
#AC3(z)
#z.display(z.infer_assignment())
#print()



# ______________________________________________________________________________
# PIC-A-SIX

_TOTAL = 5
_LIST = list(range(_TOTAL))
_ITER = itertools.count().__next__
_MATRIX = [[_ITER() for x in _LIST] for y in _LIST]
_ROWSM = _MATRIX
_COLSM = list(zip(*_MATRIX))

_NEIGHBORSM = {v: set() for v in flatten(_ROWSM)}
for unit in map(set, _ROWSM + _COLSM):
    for v in unit:
        _NEIGHBORSM[v].update(unit - {v})

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

_NEIGHBORS_H = {v: set() for v in flatten(_ROWSM)}
for unit in map(set, _ROWSM):
    for v in unit:
        _NEIGHBORS_H[v].update(unit - {v})

_NEIGHBORS_V = {v: set() for v in flatten(_ROWSM)}
for unit in map(set, _COLSM):
    for v in unit:
        _NEIGHBORS_V[v].update(unit - {v})

column1Constraints = {"V":1, ".":4}
column2Constraints = {"V":1, ".":4}
column3Constraints = {"V":2, "R":1, ".":2}
column4Constraints = {"R":2, "A":1, ".":2}
column5Constraints = {"R":1, ".":4}

row1Constraints = {"R":1, ".":4}
row2Constraints = {"R":2, "A":1, ".":2}
row3Constraints = {"R":1, ".":4}
row4Constraints = {"V":2, ".":3}
row5Constraints = {"V":2, ".":3}

col1 = [0,5,10,15,20]
col2 = [1,6,11,16,21]
col3 = [2,7,12,17,22]
col4 = [3,8,13,18,23]
col5 = [4,9,14,19,24]

row1 = [0,1,2,3,4]
row2 = [5,6,7,8,9]
row3 = [10,11,12,13,14]
row4 = [15,16,17,18,19]
row5 = [20,21,22,23,24]

def getAssignmentColumn(assignment, start, end, increase):
    temp = {}

    while(start in assignment and start <= end):
        temp[start] = assignment[start]
        start+=increase
    return temp

def countOcurrences(dictionary, letter):
    occurrences = 0
    for key in dictionary:
        if dictionary[key] == letter:
            occurrences +=1
    return occurrences


class PicAPix(CSP):
    R3 = _LIST
    Cell = _ITER
    bgrid = _MATRIX
    rows = _ROWSM
    cols = _COLSM
    neighbors = _NEIGHBORSM
    domains = {}

    def __init__(self, grid):
        for var in flatten(self.bgrid):
            self.domains[var] = ['V', 'R', 'A', "."]
            self.neighbors_v = _NEIGHBORS_V
            self.neighbors_h = _NEIGHBORS_H
            
        self.update_domains()
        CSP.__init__(self, None, self.domains, self.neighbors, None)
        self.support_pruning()

    def assign(self, var, val, assignment):
        "Add {var: val} to assignment; Discard the old value if any."
        assignment[var] = val
        self.nassigns += 1
        # if(var in col1):
        #     for v in col1:
        #         if(v != var and val != "."):
        #             if(val in self.curr_domains[v]):
        #                 self.curr_domains[v].remove(val)

        # if(var in row1):
        #     for v in row1:
        #         if(v != var and val != "."):
        #             if(val in self.curr_domains[v]):
        #                 self.curr_domains[v].remove(val)

        if(self.nassigns % 10000 == 0):
            print(self.nassigns)
            print(assignment)
            print("Con", self.nconflicts(var, val, assignment))

    # def assign(self, var, val, assignment):
    #     "Assign var, and keep track of conflicts."
    #     # print(assignment)
    #     oldval = assignment.get(var, None)
    #     if val != oldval:
    #         if oldval is not None:  # Remove old val if there was one
    #             self.record_conflict(assignment, var, oldval, -1)
    #         self.record_conflict(assignment, var, val, +1)
    #         CSP.assign(self, var, val, assignment)

    # def unassign(self, var, assignment):
    #     # print(assignment)
    #     "Remove var from assignment (if it is there) and track conflicts."
    #     if var in assignment:
    #         self.record_conflict(assignment, var, assignment[var], -1)
    #     CSP.unassign(self, var, assignment)

    def nconflicts(self, var, val, assignment):

        # Column 1
        conflicts = 0

        
        constraints = Counter()
        values = Counter()
        
        row = {}
        column = {}
        if(var in col1):
            constraints += column1Constraints
            col = getAssignmentColumn(assignment, 0, 20, 5)

        elif(var in col2):
            constraints += column2Constraints
            col = getAssignmentColumn(assignment, 1, 21, 5)

        elif(var in col3):
            constraints += column3Constraints
            col = getAssignmentColumn(assignment, 2, 22, 5)

        elif(var in col4):
            constraints += column4Constraints
            col = getAssignmentColumn(assignment, 3, 23, 5)

        elif(var in col5):
            constraints += column4Constraints
            col = getAssignmentColumn(assignment, 4, 24, 5)

        if(var in row1):
            constraints += row1Constraints
            row = getAssignmentColumn(assignment, 1, 4, 1)

        elif(var in row2):
            constraints += row2Constraints
            row = getAssignmentColumn(assignment, 5, 9, 1)

        elif(var in row3):
            constraints += row3Constraints
            row = getAssignmentColumn(assignment, 10, 14, 1)

        elif(var in row4):
            constraints += row4Constraints
            row = getAssignmentColumn(assignment, 15, 19, 1)

        elif(var in row5):
            constraints += row5Constraints
            row = getAssignmentColumn(assignment, 20, 24, 1)

        counterAssignments = Counter()

        # Computes values for rows,cols
        for key in row:
            v = row[key]
            counterAssignments[v] +=1
        for key in column:
            v = column[key]
            # if(v != "."):
            counterAssignments[v] +=1

        # if(var in row1 and var in col1):
        conflicts+= sum((constraints - counterAssignments).values())
        conflicts+= sum((counterAssignments - constraints).values())

        # print("C", conflicts)
        return conflicts

    def countConf_V(self,assignment, var, val, neighbors):
        conf = 0
        print("__")
        # if var in col1:
        #     cop = column1Constraints.copy()
        #     if val in cop:
        #         cop[val]-=1
        #     for neighbor in neighbors:
        #         print(assignment)
        #         print(assignment[neighbor])
        #         if(neighbor in assignment and neighbor in cop):
        #             cop[assignment[neighbor]] -=1

        #     print(cop)
        #     print("VAR", var)
        #     print(assignment)

        return conf

    def pic_a_pix_constraint_v(self, A, a, B, b):

        # Constraint 1
        if A in col1:
            if(a == "V" or b == "V"):
                return a!=b
            # else:
            #     return a=="." and b == "."

        # Constraint 1
        if A in col2:
            if(a == "V" or b == "V"):
                return a!=b
            # else:
            #     return a=="." and b == "."

        # if A in col3:
        #     if(a == "V" and b == "V"):
        #         return abs(A-B)==1
        return True


    def pic_a_pix_constraint_h(self, A, a, B, b):
        
        return True        
    def display(self, assignment):
        for row in self.bgrid:
            print(' '.join(map(str, row)))
    def update_domains(self):

        columnConstraints = [["V"], ["V"], ["V","R"], ["R","A"], ["R"]]
        rowConstraints = [["R"], ["R","A"], ["R"], ["V"], ["V"]]
        arrC = []
        for y in range(len(rowConstraints)):
            for x in range(len(columnConstraints)):
                constraints = columnConstraints[x] + rowConstraints[y]
                
                arrC.append(constraints)
        
        for x in range(len(self.domains)):
            domains = self.domains[x]
            constraints = arrC[x]
            
            if("R" not in constraints):
                domains.remove("R")
            if("V" not in constraints):
                domains.remove("V")
            if("A" not in constraints):
                domains.remove("A")
        
s = PicAPix(easy1)

print("DOMAINS")
print(s.domains)
print("VARIABLES")
print(s.variables)

print(min_conflicts(s, 10000000))