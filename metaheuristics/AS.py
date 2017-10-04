import random

class Ant():
	routes = []
	totalCost = 0
	def __init__(self, start):
		self.routes=[start]

class Graph():
	nodes = []
	edges = {}
	neighbors = {}
	def __init__(self, nodes):
		self.nodes = nodes

	def addEdge(self, nodeA, nodeB, cost):
		self.edges[nodeA+nodeB] = cost
		if(nodeA in self.neighbors):
			self.neighbors[nodeA].append(nodeB)
		else:
			self.neighbors[nodeA] = [nodeB]

		if(nodeB in self.neighbors):
			self.neighbors[nodeB].append(nodeA)
		else:
			self.neighbors[nodeB] = [nodeA]

	def getNeighbors(self, routes):
		# Obtener movimientos posibles
		currentState = routes[-1]
		neighbors = []
		total = 0
		for neighbor in self.neighbors[currentState]:
			if(neighbor not in routes):
				minChar = min(currentState, neighbor)
				maxChar = max(currentState, neighbor)
				cost = self.edges[minChar+maxChar]
				total+=cost
				neighbors.append([neighbor,cost])

		s = 0
		neighbors.sort(key=lambda x: x[1])
		for neighbor in neighbors:
			val = neighbor[1]/total
			neighbor[1] = val+s
			s+=val
		prob = random.random()
		i = 0
		while(i in neighbors and neighbors[i][1] < prob):
			i+=1

		minChar = min(currentState, neighbors[i][0])
		maxChar = max(currentState, neighbors[i][0])
		cost = self.edges[minChar+maxChar]
		return neighbors[i][0], cost
		# Calcula probabilidad (por ahora feromones = 1)

g = Graph(["A", "B", "C", "D", "E"])

g.addEdge("A", "B", 3)
g.addEdge("A", "E", 21)
g.addEdge("B", "C", 5)
g.addEdge("B", "D", 6)
g.addEdge("C", "E", 7)
g.addEdge("C", "D", 5)
g.addEdge("D", "E", 4)

ants = []
print("ANTS INITIAL")
for i in range(5):
	ant = Ant(random.choice(g.nodes))
	ants.append(Ant(random.choice(g.nodes)))
	print(ant.routes)

for i in range(4):
	for ant in ants:
		nextPlace, cost = g.getNeighbors(ant.routes)
		ant.totalCost+=cost
		ant.routes.append(nextPlace)


for ant in ants:
	print(ant.routes)
	print(ant.totalCost)