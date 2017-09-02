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
	def __init__(self, inicial=(2,3,0,0), meta=(2,3,34, 0)):
		Problem.__init__(self, inicial, meta)
		self.initial = inicial
		self.acciones = ["A", "B", "*" , "+"]

	def actions(self, estado):
		accs = ["A", "B"]
		for accion in self.acciones:
			if(accion == "+" and estado[3]!=0):
				accs.append("+")
			elif(accion == "*" and estado[3]!=0):
				accs.append("*")
			elif(accion == "-" and estado[3]!=0):
				accs.append("-")
		return accs

	def result(self, estado, accion):
		if(accion == "A"):
			return nuevo_estado(estado, estado[0])
		elif(accion == "B"):
			return nuevo_estado(estado, estado[1])
		elif(accion == "+"):
			return nuevo_estado(estado, "+")
		elif(accion == "*"):
			return nuevo_estado(estado, "*")
		elif(accion == "-"):
			return nuevo_estado(estado, "-")

	def h1(self, node):

		a = abs(self.goal[2] - (node.state[2] + (node.state[0] * node.state[3])))
		b = abs(self.goal[2] - (node.state[2] + (node.state[1] * node.state[3])))
		c = abs(self.goal[2] - (node.state[2] + (node.state[0] + node.state[3])))
		d = abs(self.goal[2] - (node.state[2] + (node.state[1] + node.state[3])))
		return(min([a,b,c,d])// abs(self.goal[2]))

	def h2(self, node):

		# return abs(self.goal[2] - (node.state[2] +
		# 	((node.state[0] + node.state[3]) + (node.state[1] + node.state[3]) // 2))) // self.goal[2]

		return abs((self.goal[2] - node.state[2] - node.state[3]) // self.goal[2])


def nuevo_estado(edo, accion):
	nedo = list(edo)
	if(accion == "+"):
		nedo[2] += nedo[3]
		nedo[3] = 0
	elif(accion == "*"):
		nedo[2] *= nedo[3]
		nedo[3] = 0
	elif(accion == "-"):
		nedo[2] -= nedo[3]
		nedo[3] = 0
	else:
		nedo[3] = nedo[3] * 10 + accion

	return tuple(nedo)

def despliega_solucion(nodo_meta):
	acciones = nodo_meta.solution()
	nodos = nodo_meta.path()
	print("SOLUCION")
	print("Estado: ", nodos[0].state)
	for na in range(len(acciones)):
		if(acciones[na] == "+"):
			print("Acción: Suma")
		elif(acciones[na] == "*"):
			print("Acción: Multiplicación")
		if(acciones[na] == "A"):
			print("Acción: A")
		elif(acciones[na] == "B"):
			print("Acción: B")
		print("Estado: ", nodos[na+1].state)
	print("Total Acciones: {}".format(len(acciones)))

def main():
	
	print("MAIN")

	# prob1 = Calculator()
	# # Solve(prob1, "Problema 1", graph_search, "Graph Search", [])
	# Solve(prob1, "Problema 1", breadth_first_search, "Breath first search", None)
	# Solve(prob1, "Problema 1", uniform_cost_search, "Uniform", None)
	# Solve(prob1, "Problema 1", greedy_best_first_graph_search, "Greedy (h1)", prob1.h1)
	# Solve(prob1, "Problema 1", greedy_best_first_graph_search, "Greedy (h2)", prob1.h2)
	# Solve(prob1, "Problema 1", astar_search, "A* (h1)", prob1.h1)
	# Solve(prob1, "Problema 1", astar_search, "A* (h2)", prob1.h2)

	prob2 = Calculator((2,6,0,0), (2,6,15, 0))
	# Solve(prob2, "Problema 2", greedy_best_first_graph_search, "Greedy", prob2.h)
	# Solve(prob2, "Problema 2", uniform_cost_search, "Uniform", None)
	# Solve(prob2, "Problema 2", astar_search, "A*", prob2.h)
	# Solve(prob2, "Problema 2", breadth_first_search, "Breath first search", None)

	# prob3 = Calculator((3,7,0,0), (3,7,107,0))
	# Solve(prob3, "Problema 3", breadth_first_search, "Breath first search", None)
	# # Solve(prob3, "Problema 3", graph_search, "Graph Search", []) # 3, 14, 17 si funciona, 6 no
	# Solve(prob3, "Problema 3", depth_limited_search, "Depth limited search", None)
	# Solve(prob3, "Problema 3", uniform_cost_search, "Uniform", None)
	# Solve(prob3, "Problema 3", greedy_best_first_graph_search, "Greedy (h1)", prob3.h1) #ESTE ES LA ONDA
	# Solve(prob3, "Problema 3", greedy_best_first_graph_search, "Greedy (h2)", prob3.h2) #ESTE ES LA ONDA
	# Solve(prob3, "Problema 3", astar_search, "A* (h1)", prob3.h1)
	# Solve(prob3, "Problema 3", astar_search, "A* (h2)", prob3.h2)

	prob4 = Calculator((3,7,0,0), (3,7,100,0))
	# Solve(prob4, "Problema 4", breadth_first_search, "Breath first search", None)
	# Solve(prob3, "Problema 3", graph_search, "Graph Search", []) # 3, 14, 17 si funciona, 6 no
	# Solve(prob4, "Problema 4", depth_limited_search, "Depth limited search", None)
	# Solve(prob4, "Problema 4", uniform_cost_search, "Uniform", None)
	Solve(prob4, "Problema 4", greedy_best_first_graph_search, "Greedy (h1)", prob4.h1) #ESTE ES LA ONDA
	Solve(prob4, "Problema 4", greedy_best_first_graph_search, "Greedy (h2)", prob4.h2) #ESTE ES LA ONDA
	Solve(prob4, "Problema 4", astar_search, "A* (h1)", prob4.h1)
	Solve(prob4, "Problema 4", astar_search, "A* (h2)", prob4.h2)




	# # Resolviendo el problema 1:
	# print("\nProblema 1: (2, 3, 0) -> 34")
	# print("Solución del Problema 1 mediante búsqueda primero en anchura")
	# meta1 = breadth_first_search(prob1)
	# if meta1:
	#     despliega_solucion(meta1)
	# else:
	#     print("Falla: no se encontró una solución")


	# # Resolviendo el problema 2:
	# print("\nProblema 2: (2, 6, 0) -> 15")
	# print("Solución del Problema 2 mediante búsqueda primero en anchura")
	# meta2 = breadth_first_search(prob2)
	# if meta2:
	#     despliega_solucion(meta2)
	# else:
	#     print("Falla: no se encontró una solución")


	# # Resolviendo el problema 3:
	# print("\nProblema 3: (3, 7, 11) -> 100")
	# print("Solución del Problema 3 mediante búsqueda primero en anchura")
	# meta3 = breadth_first_search(prob3)
	# if meta3:
	#     despliega_solucion(meta3)
	# else:
	#     print("Falla: no se encontró una solución")

	# print("Solución del Problema 3 mediante búsqueda uniform")
	# meta4 = uniform_cost_search(prob3)
	# if(meta4):
	# 	despliega_solucion(meta4)
	# else:
	# 	print("Falla: no se encontró una solución")

	# print("Problema 3 búsqueda a*")
	# meta5 = astar_search(prob3)
	# if(meta5):
	# 	despliega_solucion(meta5)
	# else:
	# 	print("Falla")

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
