import time
from search import ( # Bases para construcción de problemas
	Problem, Node, Graph, UndirectedGraph,
	SimpleProblemSolvingAgentProgram,
	GraphProblem
)

from search import ( # Algoritmos de búsqueda no informada
	tree_search, graph_search, best_first_graph_search,
	breadth_first_tree_search, breadth_first_search,
	depth_first_tree_search, depth_first_graph_search,
	depth_limited_search, iterative_deepening_search,
	uniform_cost_search,
	compare_searchers
)

from search import ( # Algoritmos de búsqueda informada (heurística)
	greedy_best_first_graph_search, astar_search
)

class Calculator(Problem):

	initial = None
	acciones = ["A", "B"]
	digits = None
	def __init__(self, inicial=(0,0), meta=(34, 0), digits=[2,3], operands=["*", "+"]):
		Problem.__init__(self, inicial, meta)
		self.initial = inicial
		for operand in operands:
			self.acciones.append(operand)
		self.digits = digits


	def actions(self, estado):
		accs = ["A", "B"]
		for accion in self.acciones:
			if(accion == "+" and estado[1]!=0):
				accs.append("+")
			elif(accion == "*" and estado[1]!=0):
				accs.append("*")
			elif(accion == "-" and estado[1]!=0):
				accs.append("-")
			#estado[1]!=0 prevents performing operations on a zero buffer (illegal move)
		return accs

	def result(self, estado, accion):
		if(accion == "A"):
			return nuevo_estado(estado, self.digits[0])
		elif(accion == "B"):
			return nuevo_estado(estado, self.digits[1])
		elif(accion == "+"):
			return nuevo_estado(estado, "+")
		elif(accion == "*"):
			return nuevo_estado(estado, "*")
		elif(accion == "-"):
			return nuevo_estado(estado, "-")

	def h1(self, node):

		a = abs(self.goal[0] - (node.state[0] + (self.digits[0] * node.state[1])))
		b = abs(self.goal[0] - (node.state[0] + (self.digits[1] * node.state[1])))
		c = abs(self.goal[0] - (node.state[0] + (self.digits[0] + node.state[1])))
		d = abs(self.goal[0] - (node.state[0] + (self.digits[1] + node.state[1])))
		return(min([a,b,c,d])/ abs(self.goal[0]))

	def h2(self, node):
		return abs((self.goal[0] - node.state[0] - node.state[1]) / self.goal[0])

	def f(self, node):
		return abs(self.goal[0] - node.state[0])


def nuevo_estado(edo, accion):
	nedo = list(edo)
	if(accion == "+"):
		nedo[0] += nedo[1]
		nedo[1] = 0
	elif(accion == "*"):
		nedo[0] *= nedo[1]
		nedo[1] = 0
	elif(accion == "-"):
		nedo[0] -= nedo[1]
		nedo[1] = 0
	else:
		nedo[1] = nedo[1] * 10 + accion

	return tuple(nedo)

def despliega_solucion(nodo_meta):
	acciones = nodo_meta.solution()
	nodos = nodo_meta.path()
	print("SOLUCION")
	print("Estado: ", nodos[0].state)
	for na in range(len(acciones)):
		if(acciones[na] == "+"):
			print("Acción: Suma {}")
		elif(acciones[na] == "-"):
			print("Acción: Resta {}")
		elif(acciones[na] == "*"):
			print("Acción: Multiplicación")
		elif(acciones[na] == "A"):
			print("Acción: A")
		elif(acciones[na] == "B"):
			print("Acción: B")
		print("Estado: ", nodos[na+1].state)
	print("Total Acciones: {}".format(len(acciones)))

def main():
	
	print("MAIN")

	prob1 = Calculator()
	# Solve(prob1, "Problema 1", tree_search, "Tree search", []) #Fracasó
	# Solve(prob1, "Problema 1", graph_search, "Graph Search", []) #Fracasó
	Solve(prob1, "Problema 1", best_first_graph_search, "Graph Search", prob1.f)
	Solve(prob1, "Problema 1", breadth_first_tree_search, "Breath First Tree Search", None)
	Solve(prob1, "Problema 1", breadth_first_search, "Breath first search", None)
	# Solve(prob1, "Problema 1", depth_first_tree_search, "Depth first tree search", None)
	# Solve(prob1, "Problema 1", depth_first_graph_search, "Depth first graph search", None)
	Solve(prob1, "Problema 1", depth_limited_search, "Depth limited search", None)
	Solve(prob1, "Problema 1", iterative_deepening_search, "Iterative deepening search", None)
	Solve(prob1, "Problema 1", uniform_cost_search, "Uniform", None)
	Solve(prob1, "Problema 1", greedy_best_first_graph_search, "Greedy (h1)", prob1.h1)
	Solve(prob1, "Problema 1", greedy_best_first_graph_search, "Greedy (h2)", prob1.h2)
	Solve(prob1, "Problema 1", astar_search, "A* (h1)", prob1.h1)
	Solve(prob1, "Problema 1", astar_search, "A* (h2)", prob1.h2)

	# prob2 = Calculator((0,0), (100,0), [3,7], ["+", "*"])
	# # Solve(prob1, "Problema 2", tree_search, "Tree search", []) #Fracasó
	# # Solve(prob1, "Problema 2", graph_search, "Graph Search", []) #Fracasó
	# # Solve(prob2, "Problema 2", best_first_graph_search, "Graph Search", prob2.f)
	# Solve(prob2, "Problema 2", breadth_first_tree_search, "Breath First Tree Search", None)
	# Solve(prob2, "Problema 2", breadth_first_search, "Breath first search", None)
	# # Solve(prob1, "Problema 2", depth_first_tree_search, "Depth first tree search", None)
	# # Solve(prob1, "Problema 2", depth_first_graph_search, "Depth first graph search", None)
	# Solve(prob2, "Problema 2", depth_limited_search, "Depth limited search", None)
	# Solve(prob2, "Problema 2", iterative_deepening_search, "Iterative deepening search", None)
	# Solve(prob2, "Problema 2", uniform_cost_search, "Uniform", None)
	# Solve(prob2, "Problema 2", greedy_best_first_graph_search, "Greedy (h1)", prob2.h1)
	# Solve(prob2, "Problema 2", greedy_best_first_graph_search, "Greedy (h2)", prob2.h2)
	# Solve(prob2, "Problema 2", astar_search, "A* (h1)", prob2.h1)
	# Solve(prob2, "Problema 2", astar_search, "A* (h2)", prob2.h2)

	# prob3 = Calculator((0,0), (-10,0), [2,3], ["-", "+"])
	# # Solve(prob1, "Problema 3", tree_search, "Tree search", []) #Fracasó
	# # Solve(prob1, "Problema 3", graph_search, "Graph Search", []) #Fracasó
	# # Solve(prob2, "Problema 3", best_first_graph_search, "Graph Search", prob2.f)
	# Solve(prob3, "Problema 3", breadth_first_tree_search, "Breath First Tree Search", None)
	# Solve(prob3, "Problema 3", breadth_first_search, "Breath first search", None)
	# # Solve(prob1, "Problema 3", depth_first_tree_search, "Depth first tree search", None)
	# # Solve(prob1, "Problema 3", depth_first_graph_search, "Depth first graph search", None)
	# # Solve(prob3, "Problema 3", depth_limited_search, "Depth limited search", None)
	# Solve(prob3, "Problema 3", iterative_deepening_search, "Iterative deepening search", None)
	# Solve(prob3, "Problema 3", uniform_cost_search, "Uniform", None)
	# Solve(prob3, "Problema 3", greedy_best_first_graph_search, "Greedy (h1)", prob3.h1)
	# Solve(prob3, "Problema 3", greedy_best_first_graph_search, "Greedy (h2)", prob3.h2)
	# Solve(prob3, "Problema 3", astar_search, "A* (h1)", prob3.h1)
	# Solve(prob3, "Problema 3", astar_search, "A* (h2)", prob3.h2)

	#Unsolvable problems (LOOP FOREVER)
	prob4 = Calculator((0,0), (4,0), [2,3], ["+", "*"])
	# # Solve(prob4, "Problema 4", tree_search, "Tree search", []) #Fracasó
	# # Solve(prob4, "Problema 4", graph_search, "Graph Search", []) #Fracasó
	# # Solve(prob4, "Problema 4", best_first_graph_search, "Graph Search", prob4.f)
	# Solve(prob4, "Problema 4", breadth_first_tree_search, "Breath First Tree Search", None)
	# Solve(prob4, "Problema 4", breadth_first_search, "Breath first search", None)
	# # Solve(prob4, "Problema 4", depth_first_tree_search, "Depth first tree search", None)
	# # Solve(prob4, "Problema 4", depth_first_graph_search, "Depth first graph search", None)
	# # Solve(prob4, "Problema 4", depth_limited_search, "Depth limited search", None)
	# Solve(prob4, "Problema 4", iterative_deepening_search, "Iterative deepening search", None)
	# Solve(prob4, "Problema 4", uniform_cost_search, "Uniform", None)
	# Solve(prob4, "Problema 4", greedy_best_first_graph_search, "Greedy (h1)", prob4.h1)
	# Solve(prob4, "Problema 4", greedy_best_first_graph_search, "Greedy (h2)", prob4.h2)
	# Solve(prob4, "Problema 4", astar_search, "A* (h1)", prob4.h1)
	# Solve(prob4, "Problema 4", astar_search, "A* (h2)", prob4.h2)

	prob5 = Calculator((0,0), (9,0), [3,5], ["+", "*"])
	# # Solve(prob5, "Problema 5", tree_search, "Tree search", []) #Fracasó
	# # Solve(prob5, "Problema 5", graph_search, "Graph Search", []) #Fracasó
	# # Solve(prob5, "Problema 5", best_first_graph_search, "Graph Search", prob5.f)
	# Solve(prob5, "Problema 5", breadth_first_tree_search, "Breath First Tree Search", None)
	# Solve(prob5, "Problema 5", breadth_first_search, "Breath first search", None)
	# # Solve(prob5, "Problema 5", depth_first_tree_search, "Depth first tree search", None)
	# # Solve(prob5, "Problema 5", depth_first_graph_search, "Depth first graph search", None)
	# # Solve(prob5, "Problema 5", depth_limited_search, "Depth limited search", None)
	# Solve(prob5, "Problema 5", iterative_deepening_search, "Iterative deepening search", None)
	# Solve(prob5, "Problema 5", uniform_cost_search, "Uniform", None)
	# Solve(prob5, "Problema 5", greedy_best_first_graph_search, "Greedy (h1)", prob5.h1)
	# Solve(prob5, "Problema 5", greedy_best_first_graph_search, "Greedy (h2)", prob5.h2)
	# Solve(prob5, "Problema 5", astar_search, "A* (h1)", prob5.h1)
	# Solve(prob5, "Problema 5", astar_search, "A* (h2)", prob5.h2)

	prob6 = Calculator((0,0), (11,0), [4,6], ["+", "*"])
	# # Solve(prob6, "Problema 6", tree_search, "Tree search", []) #Fracasó
	# # Solve(prob6, "Problema 6", graph_search, "Graph Search", []) #Fracasó
	# # Solve(prob6, "Problema 6", best_first_graph_search, "Graph Search", prob6.f)
	# Solve(prob6, "Problema 6", breadth_first_tree_search, "Breath First Tree Search", None)
	# Solve(prob6, "Problema 6", breadth_first_search, "Breath first search", None)
	# # Solve(prob6, "Problema 6", depth_first_tree_search, "Depth first tree search", None)
	# # Solve(prob6, "Problema 6", depth_first_graph_search, "Depth first graph search", None)
	# # Solve(prob6, "Problema 6", depth_limited_search, "Depth limited search", None)
	# Solve(prob6, "Problema 6", iterative_deepening_search, "Iterative deepening search", None)
	# Solve(prob6, "Problema 6", uniform_cost_search, "Uniform", None)
	# Solve(prob6, "Problema 6", greedy_best_first_graph_search, "Greedy (h1)", prob6.h1)
	# Solve(prob6, "Problema 6", greedy_best_first_graph_search, "Greedy (h2)", prob6.h2)
	# Solve(prob6, "Problema 6", astar_search, "A* (h1)", prob6.h1)
	# Solve(prob6, "Problema 6", astar_search, "A* (h2)", prob6.h2)

def Solve(problem, problemName, algorithm, algorithmName, extraParameter):
	print("Solución del {} mediante {}".format(problemName, algorithmName))
	print("Initial state {} -> Goal state {}".format(problem.initial, problem.goal))

	start = time.time()
	meta = None
	if(extraParameter != None):
		meta = algorithm(problem, extraParameter)
	else:
		meta = algorithm(problem)

	if(meta):
		despliega_solucion(meta)
	else:
		print("Falla: no se encontró una solución")
	end = time.time()
	print("Tiempo de función: {}".format(end-start))

if __name__ == "__main__":
	main()
