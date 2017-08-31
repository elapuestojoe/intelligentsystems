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

    def __init__(self, inicial=(2,3,0), meta=(2,3,13)):
    	Problem.__init__(self, inicial, meta)
    	self.acciones = ["+A", "+B", "*A" , "*B"]

    def actions(self, estado):

    	# Para simplificar el problema, todas las operaciones se hacen sobre C

    	# +A
    	# +B
    	# *A
    	# *B
    	accs = []
    	for accion in self.acciones:
    		if(accion == "+A") and \
    			not estado_ilegal(nuevo_estado(estado, estado[0]+estado[2]), self.goal):
    			accs.append("+A")
    		elif(accion == "+B") and \
    			not estado_ilegal(nuevo_estado(estado, estado[1]+estado[2]), self.goal):
    			accs.append("+B")
    		elif(accion == "*A") and \
    			not estado_ilegal(nuevo_estado(estado, estado[0]*estado[2]), self.goal):
    			accs.append("*A")
    		elif(accion == "*B") and \
    			not estado_ilegal(nuevo_estado(estado, estado[1]*estado[2]), self.goal):
    			accs.append("*B")
    	return accs

    def result(self, estado, accion):
    	if(accion == "+A"):
    		return nuevo_estado(estado, estado[0]+estado[2])
    	elif(accion == "+B"):
    		return nuevo_estado(estado, estado[1]+estado[2])
    	elif(accion == "*A"):
    		return nuevo_estado(estado, estado[0]*estado[2])
    	elif(accion == "*B"):
    		return nuevo_estado(estado, estado[1]*estado[2])

    # Esto es para la heurística, aún no se usa
    def h(self, node):
    	#total, goal = node.state
    	#totalN, goalN = self.goal

    	#print("STATE")
    	#print(node.state)
    	#print(self.goal)
    	
    	
    	nodeS = node.state
    	goalN = self.goal
    	
    	return abs(nodeS[2] - goalN[2])

def nuevo_estado(edo, value):
	nedo = list(edo)
	nedo[2] = value
	return tuple(nedo)

def estado_ilegal(edo, meta):
	return edo[2] > meta[2]

def despliega_solucion(nodo_meta):
	acciones = nodo_meta.solution()
	nodos = nodo_meta.path()
	print("SOLUCION")
	print("Estado: ", nodos[0].state)
	for na in range(len(acciones)):

		if(acciones[na] == "+A"):
			print("Acción: Suma A")
		elif(acciones[na] == "+B"):
			print("Acción: Suma B")
		if(acciones[na] == "*A"):
			print("Acción: Multiplica A")
		elif(acciones[na] == "*B"):
			print("Acción: Multiplica B")
		print("Estado: ", nodos[na+1].state)
	print('FIN')

def main():
	
	print("MAIN")
	
	prob1 = Calculator()
	prob2 = Calculator((2,6,0), (2,6,15))
	prob3 = Calculator((3,7,11), (3,7,100))
	
	# Resolviendo el problema 1:
	print("Problema 1: (2, 3, 0) -> 13")
	print("Solución del Problema 1 mediante búsqueda primero en anchura")
	meta1 = breadth_first_search(prob1)
	if meta1:
	    despliega_solucion(meta1)
	else:
	    print("Falla: no se encontró una solución")


	# Resolviendo el problema 2:
	print("Problema 2: (2, 6, 0) -> 15")
	print("Solución del Problema 2 mediante búsqueda primero en anchura")
	meta2 = breadth_first_search(prob2)
	if meta2:
	    despliega_solucion(meta2)
	else:
	    print("Falla: no se encontró una solución")


	# Resolviendo el problema 3:
	print("Problema 3: (3, 7, 11) -> 100")
	print("Solución del Problema 3 mediante búsqueda primero en anchura")
	meta3 = breadth_first_search(prob3)
	if meta3:
	    despliega_solucion(meta3)
	else:
	    print("Falla: no se encontró una solución")


	# Resolviendo el problema 3:
	print("\nProblema 3: (3, 7, 11) -> 100")
	print("Solución del Problema 3 mediante A*")
	meta4 = astar_search(prob3)
	if meta3:
	    despliega_solucion(meta4)
	else:
	    print("Falla: no se encontró una solución")



if __name__ == "__main__":
	main()
