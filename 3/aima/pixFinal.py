"""CSP (Constraint Satisfaction Problems) problems and solvers. (Chapter 6)."""

from utils import argmin_random_tie, count, first
import search

from collections import defaultdict
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


def flatten(seqs): return sum(seqs, [])

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

def get_h_neighbors(dictionary,letter):
    v = False
    for key in dictionary:
        if(key not in col5 and dictionary[key]==letter and dictionary[key+1]==letter):
            v = True
    return v

def check_order(dictionary, order):
    i = 0
    errors = 0
    for key in dictionary:
        if(dictionary[key]!= order[i]):
            errors+=1
        i+=1
    return errors * 2


def get_v_neighbors(dictionary,letter):
    v = False
    for key in dictionary:
        if(key not in row5 and dictionary[key]==letter and dictionary[key+5]==letter):
            v = True
    return v

class PicAPix(CSP):
    R3 = _LIST
    Cell = _ITER
    bgrid = _MATRIX
    rows = _ROWSM
    cols = _COLSM
    neighbors = _NEIGHBORSM
    domains = {}

    def __init__(self):
        for var in range(0,25):
            self.domains[var] = ['G', 'R', 'Y', "."]
            self.neighbors_v = _NEIGHBORS_V
            self.neighbors_h = _NEIGHBORS_H
            self.confs = {}
            self.nassigns = 0
        self.update_domains()
        CSP.__init__(self, None, self.domains, self.neighbors, None)

    def solve(self):

        current = {}
        print("current  ", current)

        dicStart = ["."]*10 +["R"]*12 + ["G"]*2 + ["Y"]*1


        for i in range(len(self.domains)):
            self.assign(i, dicStart[i], current)

        def calculateWrong(current, domains):
            wrong= {}        
            for i in current:
                if current[i] not in domains[i]:
                    wrong[i] = current[i]
            return wrong

        wrong = calculateWrong(current, self.domains)

        while(len(wrong) > 0):
            for i in range(len(self.domains)):
                for w in wrong:
                    if(wrong[w] in self.domains[i] and current[i] in self.domains[w]):
                        temp = current[i]
                        current[i] = wrong[w]
                        current[w] = temp
                        wrong = calculateWrong(current, self.domains)
            print(wrong)
            print(self.domains)
            print(current)

        buff = current.copy()
        print(current)

        confs = {}
        max_steps = 1000000
        for i in range(max_steps):
            conflicted = self.conflicted_vars(current)
            if not conflicted:
                return current
            var = random.choice(conflicted)
            val = min_conflicts_value(self,var, current)
            # print(conflicted)
            if(i % 10000 == 0):
                print(current)
                current = buff

                # mutate(current)
                # Since it's not completely determinant, we use a reset
                # print("RESET")
                # print(current)
            for i in range(len(self.domains)):
                if(i!=var):
                    if(val in self.domains[i] and current[i] in self.domains[var]):
                        temp = current.copy()
                        temp[var] = current[i]
                        temp[i] = current[var]

                        if(self.nconflicts(var,temp[var], temp) + self.nconflicts(i,temp[var], temp) +1 <= 
                            self.nconflicts(var, current[var], current) + self.nconflicts(i, current[i], current)):
                                current = temp

    def assign(self, var, val, assignment):
        "Assign var, and keep track of conflicts."
        self.nassigns +=1
        oldval = assignment.get(var, None)
        if val != oldval:
            if oldval is not None:  # Remove old val if there was one
                self.record_conflict(assignment, var, oldval, -1)
            self.record_conflict(assignment, var, val, 1)
            CSP.assign(self, var, val, assignment)

    def unassign(self, var, assignment):
        "Remove var from assignment (if it is there) and track conflicts."
        print("unassign")
        if var in assignment:
            print("unassign conflict")
            # self.record_conflict(assignment, var, assignment[var], -1)
        CSP.unassign(self, var, assignment)

    def record_conflict(self, assignment, var, val, delta):
        "Record conflicts caused by addition or deletion of a piece."
        # n = len(self.variables)
        n = var+ord(val)
        if(n not in self.confs):
            self.confs[n] = delta
        else:
            self.confs[n] += delta

    def nconflicts(self, var, val, assignment):
        conflicts = 0
        if(var in self.confs):
            conflicts += self.confs[var]

        if var in col1:
            firstColumn = getAssignmentColumn(assignment, 0, 20, 5)
            v = countOcurrences(firstColumn, "R")
            conflicts += abs(2 - v)

            if(v == 2 and not get_v_neighbors(firstColumn, "R")):
                conflicts+=1

            # conflicts += abs(3 - countOcurrences(firstColumn, "."))

        elif var in col2:
            secondColumn = getAssignmentColumn(assignment, 1, 21, 5)
            conflicts += abs(1 - countOcurrences(secondColumn, "Y"))
            conflicts += abs(1 - countOcurrences(secondColumn, "R"))
            conflicts += abs(1 - countOcurrences(secondColumn, "G"))
            conflicts += abs(2 - countOcurrences(secondColumn, "."))

        elif var in col3:
            thirdColumn = getAssignmentColumn(assignment, 2, 22, 5)

            conflicts+= check_order(thirdColumn, ["R", "R", ".", "R", "R"])


        # elif var in col4:
        #     fourthColumn = getAssignmentColumn(assignment, 3, 23, 5)

        #     conflicts += check_order(fourthColumn, ["R", "G", "R", ".", "R"])

        elif var in col5:
            fifthColumn = getAssignmentColumn(assignment, 4, 24, 5)

            v = countOcurrences(fifthColumn, "R")
            conflicts += abs(2 - v)
            if(v == 2 and not get_v_neighbors(fifthColumn, "R")):
                conflicts+=1


        # # Horizontal
        if var in row1:
            firstRow = getAssignmentColumn(assignment, 0, 4, 1)
            v = countOcurrences(firstRow, "R")
            conflicts += abs(2 - v)
            # conflicts += abs(3 - countOcurrences(firstRow, "."))

            if(v == 2 and get_h_neighbors(firstRow, "R")):
                conflicts+=1

        elif var in row2:
            secondRow = getAssignmentColumn(assignment, 5, 9, 1)

            conflicts += abs(1 - countOcurrences(secondRow, "Y"))
            conflicts += abs(1 - countOcurrences(secondRow, "R"))
            conflicts += abs(1 - countOcurrences(secondRow, "G"))
            conflicts += abs(2 - countOcurrences(secondRow, "."))

        elif var in row3:
            thirdRow = getAssignmentColumn(assignment, 10, 14, 1)

            conflicts+= check_order(thirdRow, ["R", "R", ".", "R", "R"])

        # elif var in row4:
        #     fourthRow = getAssignmentColumn(assignment, 15, 19, 1)

        #     # four constraints case:
        #     conflicts+=check_order(fourthRow, ["R", "G", "R", ".","R"])
        elif var in row5:
            fifthRow = getAssignmentColumn(assignment, 20, 24, 1)

            v = countOcurrences(fifthRow, "R")
            conflicts += abs(2 - v)

            if(v == 2 and not get_h_neighbors(fifthRow, "R")):
                conflicts+= 1

            conflicts += abs(3 - countOcurrences(fifthRow, "."))

        # spaces = 0
        # for i in assignment:
        #     if(assignment[i]=="."):
        #         spaces+=1

        # conflicts+= abs(16 - spaces)

        return conflicts

    def display(self, assignment):
        for row in self.bgrid:
            print(' '.join(map(str, row)))

    def update_domains(self):
        # Caso 1:
        #           V1, V1, [V2,R1], [R1,A1,R1], [R1]
        # R1
        # R1,A1,R1
        # R1
        # V1,V1
        # V2
        columnConstraints = [["R"], ["Y", "R", "G"], ["R"], ["R","G"], ["R"]]
        rowConstraints = [["R"], ["Y", "R","G"], ["R"], ["R", "G"], ["R"]]
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
            if("Y" not in constraints):
                domains.remove("Y")
            if("G" not in constraints):
                domains.remove("G")
        
        self.domains[3] = "R"
        self.domains[8] = "G"
        self.domains[13] = "R"
        self.domains[18] = "."
        self.domains[23] = "R"


        self.domains[2] = "R"
        self.domains[7] = "G"
        self.domains[12] = "R"
        self.domains[17] = "."
        self.domains[22] = "R"

        self.domains[15] = "R"
        self.domains[16] = "R"
        self.domains[17] = "."
        self.domains[18] = "R"
        self.domains[19] = "R"

        self.domains[15] = "R"
        self.domains[16] = "G"
        self.domains[17] = "R"
        self.domains[18] = "."
        self.domains[19] = "R"

        print("SELF", self.domains)
s = PicAPix()

print("DOMAINS")
print(s.domains)
print("VARIABLES")
print(s.variables)

print("SUGGEST")
s.display(s.infer_assignment())

print("SOLUTION")
print(s.solve())