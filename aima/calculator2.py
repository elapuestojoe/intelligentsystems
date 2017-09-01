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

	# (A, B, C) -> (A, B, GOAL)
	initial = None
	def __init__(self, inicial=(2,3,0,0), meta=(2,3,34, 0)):
		Problem.__init__(self, inicial, meta)
		self.initial = inicial
		self.acciones = ["A", "B", "*" , "+"]

	def actions(self, estado):

		# Para simplificar el problema, todas las operaciones se hacen sobre C

		# +A
		# +B
		# *A
		# *B
		accs = []
		for accion in self.acciones:
			if(accion == "A") and \
				not estado_ilegal(nuevo_estado(estado, estado[0]), accion):
				accs.append("A")
			elif(accion == "B") and \
				not estado_ilegal(nuevo_estado(estado, estado[1]), accion):
				accs.append("B")
			elif(accion == "+") and \
				not estado_ilegal(nuevo_estado(estado, "+"), accion):
				accs.append("+")
			elif(accion == "*") and \
				not estado_ilegal(nuevo_estado(estado, "*"), accion):
				accs.append("*")
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

	def h(self, node):
		# return abs(self.goal[2] - node.state[2] - node.state[3])

		# Segunga heurística
		return abs(self.goal[2] - (node.state[2] + ((node.state[3] + node.state[1]) + (node.state[3] + node.state[2]) / 2)))


def nuevo_estado(edo, accion):
	nedo = list(edo)
	if(accion == "+"):
		nedo[2] += nedo[3]
		nedo[3] = 0
	elif(accion == "*"):
		nedo[2] *= nedo[3]
		nedo[3] = 0
	else:
		nedo[3] = nedo[3] * 10 + accion

	return tuple(nedo)

def estado_ilegal(edo, accion):
	# return edo[2] > meta[2] or edo[3] > meta[2]
	# return False
	return (accion == "+" or accion == "*") and edo[3] != 0

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
	print('FIN')

def main():
	
	print("MAIN")
	
	prob1 = Calculator()
	prob2 = Calculator((2,6,0,0), (2,6,15, 0))
	prob3 = Calculator((3,7,0,0), (3,7,100,0))
	prob4 = Calculator((2,5,0,0), (2,5,111,0))

	problemList = 	{
					"Problema1": prob1, 
					# "Problema 2" : prob2,
					# "Problema 3" : prob3,
					# "Problema4" : prob4
					}

	# Solve(prob3, "Problema 1", graph_search, "Graph Search", [])
	Solve(prob3, "Problema 1", greedy_best_first_graph_search, "Greedy", prob1.h)
	# Solve(prob3, "Problema 1", uniform_cost_search, "Uniform", None)
	# Solve(prob3, "Problema 1", breadth_first_search, "Breath", None)
	Solve(prob3, "Problema 1", astar_search, "A*", None)


	# nonInformedAlgorithms = {
	# 						# "Tree search" : tree_search, 
	# 						"Graph search"  : graph_search, 
	# 						# "Best first graph search" : best_first_graph_search,
	# 						"Breadth first tree search " : breadth_first_tree_search, 
	# 						"Breadth first search " : breadth_first_search,
	# 						# depth_first_tree_search, 
	# 						# depth_first_graph_search,
	# 						# depth_limited_search, 
	# 						# iterative_deepening_search,
	# 						"Uniform cost search" : uniform_cost_search
	# 						}

	# informedAlgorithms = {
	# 						"Greedy" : greedy_best_first_graph_search, 
	# 						"A*" : astar_search
	# 						}

	# for keyProblem in problemList:
		
	# 	problem = problemList[keyProblem]
		
	# 	for keyAlgorithm in nonInformedAlgorithms:
	# 		algorithm = nonInformedAlgorithms[keyAlgorithm]
	# 		Solve(problem, keyProblem, algorithm, keyAlgorithm)

	# 	for keyAlgorithm in informedAlgorithms:
	# 		algorithm = informedAlgorithms[keyAlgorithm]
	# 		Solve(problem, keyProblem, algorithm, keyAlgorithm)



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

	meta = None
	if(extraParameter != None):
		meta = algorithm(problem, extraParameter)
	else:
		meta = algorithm(problem)

	if(meta):
		despliega_solucion(meta)
	else:
		print("Falla: no se encontró una solución")

if __name__ == "__main__":
	main()
