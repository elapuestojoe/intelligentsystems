"""CSP (Constraint Satisfaction Problems) problems and solvers. (Chapter 6)."""

from utils import argmin_random_tie, count, first
import search

from collections import defaultdict
from functools import reduce

import itertools
import re
import random
import copy


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
	print(csp.domains)
	for var in csp.variables:
		val = min_conflicts_value(csp, var, current)
		csp.assign(var, val, current)
	# Now repeatedly choose a random conflicted variable and change it
	for i in range(max_steps):

		if(i % 10000 == 0):
			print("I",i)
			print("CURR",current)
			print(csp.conflicted_vars(current))
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

columns = [col1,col2,col3,col4,col5]

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
	current = {}
	# columnConstraints = [["R"],[],[],[],[]]
	# rowConstraints = [["R"],[],[],[],[]]

	# Prob2
	columnConstraints = [["R","R"],["Y", "R", "G"],["R","R","R","R"],
						["R","G","R","R"],["R","R"]]
	rowConstraints = [["R","R"],["Y","R","G"],["R","R","R","R"],
						["R","G","R","R"],["R","R"]]
	# -----------------------------
	# Prob3
	# columnConstraints = [["Y","Y"],["G","R"],["R","R","R","R","Y"],["R","G","R","R"],["R","R","Y"]]
	# rowConstraints = [["Y","R","R"],["G","R","G","R"],["R","R","R","R"],["Y","R","R"],["Y","Y"]]
	# ----------------------------

	# columnConstraints = [[],["Y"],[],
	# 					[],[]]
	# rowConstraints = [[],["Y"],[],
	# 					[],[]]

	# columnConstraints = [[],["Y","G"],[],
	# 					["G"],[]]
	# rowConstraints = [[],["Y","G"],[],
	# 					["G"],[]]

	for columnConstraint in columnConstraints:
		sumConstraints = len(columnConstraint)
		columnConstraint += ["."]* (5 - sumConstraints)

	for rowConstraint in rowConstraints:
		sumConstraints = len(rowConstraint)
		rowConstraint += ["."]* (5 - sumConstraints)

	def __init__(self):
		for var in range(0,25):
			self.domains[var] = ['G', 'R', 'Y', "."]
			self.neighbors_v = _NEIGHBORS_V
			self.neighbors_h = _NEIGHBORS_H
			self.nassigns = 0
		# print(self.domains)
		self.curr_domains = self.domains
		self.update_domains()
		CSP.__init__(self, None, self.domains, self.neighbors, None)
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
		columnConstraints = self.columnConstraints
		rowConstraints = self.rowConstraints

		arrC = []
		for x in range(len(self.domains)):

			if(x in self.current):
				self.domains[x] = []
				# x=1
			else:
				var = x
				indexCol = 0
				if(var in col1):
					indexCol = 0
				elif(var in col2):
					indexCol = 1
				elif(var in col3):
					indexCol = 2
				elif(var in col4):
					indexCol = 3
				elif(var in col5):
					indexCol = 4

				indexRow = 0
				if(var in row1):
					indexRow = 0
				elif(var in row2):
					indexRow = 1
				elif(var in row3):
					indexRow = 2
				elif(var in row4):
					indexRow = 3
				elif(var in row5):
					indexRow = 4

				domain = []
				if("R" in rowConstraints[indexRow]
					and "R" in columnConstraints[indexCol]):
						domain.append("R")
				if("Y" in rowConstraints[indexRow]
					and "Y" in columnConstraints[indexCol]):
						domain.append("Y")
				if("G" in rowConstraints[indexRow]
					and "G" in columnConstraints[indexCol]):
						domain.append("G")
				if("." in rowConstraints[indexRow]
					and "." in columnConstraints[indexCol]):
						domain.append(".")

				self.domains[x] = domain

		# Remove edges
		# for i in col2:
		# 	if()

		# Fine tuning:
		for i in self.domains:
			domain = self.domains[i]

			for value in domain:
				unique=True
				for neighbor in self.neighbors:
					if(value in self.domains[neighbor] and i!=neighbor):
						unique = False

				if(unique):
					self.domains[i] = [value]

		
		# for neighbor in self.neighbors[8]:
		# 	print(neighbor)
		# 	print(self.domains[neighbor])
		# HardcodedConstraints:
		# self.domains[8] = ["G"]
		# self.domains[16] = ["G"]
		# self.domains[12] = ["."]
		# self.domains[18] = ["."]
		# 2
		# self.domains[2] = ["R"]
		# self.domains[7] = ["R"]
		# self.domains[17] = ["R"]
		# self.domains[22] = ["R"]
		# self.domains[10] = ["R"]
		# self.domains[11] = ["R"]
		# self.domains[13] = ["R"]
		# self.domains[14] = ["R"]
		print(rowConstraints)
		print(columnConstraints)
		print(self.domains)
	def assign(self, var, val, assignment):
		"Assign var, and keep track of conflicts."
		# print("ASSIGN")
		# print(self.domains)
		self.nassigns +=1
		oldval = assignment.get(var, None)

		# indexCol = 0
		# if(var in col1):
		# 	indexCol = 0
		# elif(var in col2):
		# 	indexCol = 1
		# elif(var in col3):
		# 	indexCol = 2
		# elif(var in col4):
		# 	indexCol = 3
		# elif(var in col5):
		# 	indexCol = 4

		# indexRow = 0
		# if(var in row1):
		# 	indexRow = 0
		# elif(var in row2):
		# 	indexRow = 1
		# elif(var in row3):
		# 	indexRow = 2
		# elif(var in row4):
		# 	indexRow = 3
		# elif(var in row5):
		# 	indexRow = 4

		# if(val in self.columnConstraints[indexCol] and val in self.rowConstraints[indexRow]):
		# 	self.columnConstraints[indexCol].remove(val)
		# 	self.rowConstraints[indexRow].remove(val)

		# 	if val != oldval:
		# 		if oldval is not None:
		# 			self.columnConstraints[indexCol].append(oldval)
		# 			self.rowConstraints[indexRow].append(oldval)
		# 	# CSP.assign(self, var, val, assignment)
		CSP.assign(self, var, val, assignment)
		# self.update_domains()

	def unassign(self, var, assignment):
		"""Remove {var: val} from assignment.
		DO NOT call this if you are changing a variable to a new value;
		just call assign for that."""
		if var in assignment:

			oldval = assignment.get(var, None)

			indexCol = 0
			if(var in col1):
				indexCol = 0
			elif(var in col2):
				indexCol = 1
			elif(var in col3):
				indexCol = 2
			elif(var in col4):
				indexCol = 3
			elif(var in col5):
				indexCol = 4

			indexRow = 0
			if(var in row1):
				indexRow = 0
			elif(var in row2):
				indexRow = 1
			elif(var in row3):
				indexRow = 2
			elif(var in row4):
				indexRow = 3
			elif(var in row5):
				indexRow = 4

			self.columnConstraints[indexCol].append(oldval)
			self.rowConstraints[indexRow].append(oldval)
			del assignment[var]
			# print(assignment)
			self.update_domains()
			


	def nconflicts(self, var, val, assignment):
		"Return the number of conflicts var=val has with other variables."
		conflicts = 0
		# # print(self.domains)
		# for i in range(len(self.domains)):
		# 	if len(self.domains[i])==0:
		# 		conflicts+=1

		r = 0
		d = 0
		y = 0
		g = 0
		if var in col1:
			for c in col1:

				if(c in assignment):
					if(assignment[c] == "R"):
						r+=1
					# elif(assignment[c] == "."):
					# 	d+=1

			# conflicts += abs(d - 3)
			conflicts += abs(r - 2)
		elif var in col2:
			for c in col2:
				if(c in assignment):
					if(assignment[c] == "R"):
						r+=1
					# elif(assignment[c] == "."):
					# 	d+=1
					# elif(assignment[c] == "G"):
					# 	g+=1
					# elif(assignment[c] == "Y"):
					# 	y+=1
			conflicts += abs(r-1)
			# conflicts += abs(d-2)
			# conflicts += abs(g-1)
			# conflicts += abs(y-1)
		elif var in col3:
			for c in col3:
				if(c in assignment):
					if(assignment[c] == "R"):
						r+=1
					# elif(assignment[c] == "."):
					# 	d+=1			

			conflicts += abs(r - 4)
			# conflicts += abs(d - 1)
		elif var in col4:
			for c in col4:
				if(c in assignment):
					if(assignment[c] == "R"):
						r+=1
					# elif(assignment[c] == "."):
					# 	d+=1			

			conflicts += abs(r - 3)
			# conflicts += abs(d - 1)
		elif var in col5:
			for c in col5:
				if(c in assignment):
					if(assignment[c] == "R"):
						r+=1
					# elif(assignment[c] == "."):
					# 	d+=1			

			conflicts += abs(r - 2)
			# conflicts += abs(d - 3)

		r = 0
		d = 0
		if(var in row1):
			for c in row1:
				if(c in assignment):
					if(assignment[c] == "R"):
						r+=1
					# elif(assignment[c] == "."):
					# 	d+=1
			conflicts += abs(r - 2)
			# conflicts += abs(d - 3)
		elif(var in row2):
			for c in row2:
				if(c in assignment):
					if(assignment[c] == "R"):
						r+=1
					# elif(assignment[c] == "."):
					# 	d+=1
			conflicts += abs(r - 1)
			# conflicts += abs(d - 2)

		elif(var in row3):
			for c in row3:
				if(c in assignment):
					if(assignment[c] == "R"):
						r+=1
					# elif(assignment[c] == "."):
					# 	d+=1
			conflicts += abs(r - 4)
			# conflicts += abs(d - 1)

		elif(var in row4):
			for c in row4:
				if(c in assignment):
					if(assignment[c] == "R"):
						r+=1
					# elif(assignment[c] == "."):
					# 	d+=1
			conflicts += abs(r - 3)
			# conflicts += abs(d - 1)

		elif(var in row5):
			for c in row3:
				if(c in assignment):
					if(assignment[c] == "R"):
						r+=1
					# elif(assignment[c] == "."):
					# 	d+=1
			conflicts += abs(r - 2)
			# conflicts += abs(d - 3)



		return conflicts


	def actions(self, state):
		"""Return a list of applicable actions: nonconflicting
		assignments to an unassigned variable."""
		if len(state) == len(self.variables):
			return []
		else:
			assignment = dict(state)
			var = first([v for v in self.variables if v not in assignment])
			return [(var, val) for val in self.domains[var]]

# s = PicAPix()

# print("DOMAINS", s.domains)
# s.assign(0,".",s.current)
# print(s.current)
# s.assign(1,".",s.current)
# print(s.current)

def display(s):
	print(s.domains)
	print(s.rowConstraints)
	print(s.columnConstraints)
	print(s.actions(s.current))
	print("CURRENT",s.current)
def solvePix(s):
	arr = [0]*25
	curr = 0
	# s.assign(0,"R",s.current)
	# s.assign(5,"R",s.current)

	# display(s)
	# print(s.domains)

	# s.unassign(5,s.current)
	# print("DOM",s.domains)
	while(curr < 25):
		# print(curr)
		d = s.domains[curr]
		if(len(d)>0):
			s.assign(curr, d[arr[curr]], s.current)
			curr+=1
		else:
			print("ELSE")
			curr -=1
			s.unassign(curr,s.current)
			arr[curr]+=1
		# arr[0]+=1

cols = [col1,col2,col3,col4,col5]
rows = [row1,row2,row3,row4,row5]

def checkCol(number, prob, check=False):

	r = 0 
	g = 0
	y = 0
	d = 0

	col = []
	constV = []
	if(check):
		constV = prob.columnConstraints[number]
		col = cols[number]
	else:
		constV = prob.rowConstraints[number]
		col = rows[number]

	for var in col:
		if(prob.current[var] == "."):
			d +=1
		elif(prob.current[var] == "R"):
			r+=1
		elif(prob.current[var] == "G"):
			g+=1
		elif(prob.current[var] == "Y"):
			y+=1
		
	r2 = 0
	g2 = 0
	y2 = 0
	d2 = 0

	for c in constV:
		if c == "R":
			r2+=1
		elif c == "G":
			g2+=1
		elif c == "Y":
			y2+=1
		elif c == ".":
			d2+=1

	d = abs(d-d2)
	g = abs(g-g2)
	y = abs(y-y2)
	r = abs(r-r2)
	return d ==0 and g ==0 and y== 0 and r==0

			
def isSolved(pix):
	current = pix.current
	solved = True
	for i in range(0,5):
		solved = solved and checkCol(i,pix, False) and checkCol(i,pix,True)
	return solved

def increaseCurr(curr, position, domains):
	if(curr[position] < len(domains[position])-1):
		curr[position]+=1
	else:
		for i in range(position,25):
			curr[i] = 0
		increaseCurr(curr, position-1, domains)

def solve(pix):
	for var in pix.variables:
		pix.assign(var, pix.domains[var][0], pix.current)

	steps = 0
	curr = [0]*25
	while(steps < 1000000000):
		if(isSolved(pix)):
			print("SOLVED in", steps)
			print(pix.current)
			break
		else:

			if(steps%100000 == 0):
				print(curr)
			s = 24

			increaseCurr(curr,s,pix.domains)

			for i in range(len(curr)):
				# print(i)
				# print(curr[i])
				# print(pix.domains[i])
				pix.assign(i, pix.domains[i][curr[i]], pix.current)

		steps+=1
pix = PicAPix()
solve(pix)
	