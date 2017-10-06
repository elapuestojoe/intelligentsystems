import random

class Ant():
	routes = []
	totalCost = 0
	def __init__(self, start):
		self.routes=[start]

class Graph():
	nodes = []
	edges = {}
	feromoneTrails = {}
	neighbors = {}
	def __init__(self, nodes):
		self.nodes = nodes

	def addEdge(self, nodeA, nodeB, cost):
		self.edges[nodeA+nodeB] = cost
		self.feromoneTrails[nodeA+nodeB] = 1
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
		print("Permitted moves and cost:", neighbors)
		print("Total Cost of all permitted moves: ", total)
		for neighbor in neighbors:
			c = neighbor[1]
			val = neighbor[1]/total			
			# c = neighbor[1]
			# val = (total-neighbor[1])/total
			# total = total-neighbor[1]
			neighbor[1] = val+s

			print("Move {} has a feromone trail value of 1".format(neighbor[0]))
			print("Move {} has a heuristic value of {}".format(neighbor[0], c))
			print("The total is {}".format(total))
			print("1 * {} / {} = {}".format(c, total, val))
			print("To use Roullete Wheel, we add the sum of previous values, so the move {} gets assigned the value {}".format(neighbor[0], val+s))
			s+=val

		print("Permitted moves weighted:", neighbors)
		prob = random.random()
		i = 0
		while(i in neighbors and neighbors[i][1] < prob):
			i+=1

		print("Random number is {}, so the selected move is {}".format(prob, neighbors[i][0]))
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
print("INITIAL ANTS")
for i in range(5):
	ant = Ant(random.choice(g.nodes))
	ants.append(ant)
	print(ant.routes)

for i in range(4):
	for j in range(len(ants)):
		ant = ants[j]
		print("\nANT:", j)
		print("Iteration:",i)
		print("Current route", ant.routes)
		nextPlace, cost = g.getNeighbors(ant.routes)
		ant.totalCost+=cost
		ant.routes.append(nextPlace)

print("\nAll ants have finished their route\n")
for i in range(len(ants)):
	ant = ants[i]
	print("Ant {} route = {}, cost = {}\n".format(i, ant.routes, ant.totalCost))

print("\nCurrent feromone trails:", g.feromoneTrails)

print("\nUpdate feromone trails")
print("\nEvaporation coefficient = 0.1")
print("\nQ = 50")
q = 20

def getAntsTrail(value, ants):
	r = [0]*len(ants)
	for j in range(len(ants)):
		ant = ants[j]
		for i in range(0,len(ant.routes)-1):
			minChar = min(ant.routes[i], ant.routes[i+1])
			maxChar = max(ant.routes[i], ant.routes[i+1])
			if(minChar+maxChar==value):
				r[j] = q/ant.totalCost
				print("{} is in ant's {} route, so the value is 50 / it's cost, which is {}".format(value, j, ant.totalCost))
	return r

evaporation = 0.9
for key in g.feromoneTrails:
	value = g.feromoneTrails[key]
	print("\nCurrent value for {}, {}".format(key, value))
	print("Values for {}".format(key))
	r = getAntsTrail(key, ants)
	print("Values for trail {} are {}".format(key,r))
	print("The sum of those values is {}".format(sum(r)))
	newVal = value * evaporation + sum(r)
	print("So the new value for the trail is {} * {} / {} = {}".format(value, evaporation, sum(r), newVal))
	g.feromoneTrails[key] = newVal
	print("Updated value = {}".format(newVal))

print("UpdateValues:", g.feromoneTrails)