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
    def __init__(self, inicial=(2,3,0), meta=(2,3,29)):
    	Problem.__init__(self, inicial, meta)
    	self.acciones = ["+A", "+B", "*A" , "*B"]

    def actions(self, estado):

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

    def h(self, node):
    	total, goal = node.state
    	totalN, goalN = self.goal

    	print("STATE")
    	print(node.state)
    	print(self.goal)

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

	prob2 = Calculator((2,6,0), (2,6,7))
	# Resolviendo el problema 1:
	print("Solución del Problema 1 mediante búsqueda primero en anchura")
	meta1 = breadth_first_search(prob1)
	if meta1:
	    despliega_solucion(meta1)
	else:
	    print("Falla: no se encontró una solución")

	# Resolviendo el problema 2:
	print("Solución del Problema 2 mediante búsqueda primero en anchura")
	meta2 = breadth_first_search(prob2)
	if meta2:
	    despliega_solucion(meta2)
	else:
	    print("Falla: no se encontró una solución")



if __name__ == "__main__":
	main()
