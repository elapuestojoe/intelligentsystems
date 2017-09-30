import math
import random

LIMIT = 10
POPULATIONSIZE = 20
MUTATIONPROB = 0.05
ITERATIONS = 1000
def estimate(x, arrA):
	return ( (arrA[0]/(x*x)) + (arrA[1]* math.pow(math.e,(arrA[2]/x))) + arrA[3]*math.sin(x))

def getA(binString):

	a0 = int(binString[0:4],2)
	a1 = int(binString[4:8],2)
	a2 = int(binString[8:12],2)
	a3 = int(binString[12:16],2)

	return [a0,a1,a2,a3]

def initializeRandomPopulation():
	population = []
	for i in range(POPULATIONSIZE):
		string = bin(random.getrandbits(16))
		# Cut string
		string = string[2::]
		while(len(string)<16):
			string="0"+string
		population.append(string)
	return population

population = initializeRandomPopulation()

# Solutions
x = [2,4,6,8,10,12,14,16,18,20]
y = [26,-1,4,20,0,-2,19,1,-4,19]

def iterate(population):
	# temp
	temp = [0]*POPULATIONSIZE

	for i in range(len(population)):
		a = getA(population[i]) # Get A values of individual
		for j in range(len(x)):
			temp[i] += abs(y[j] - estimate(x[j], a)) #Get error of estimation for each f(x) = y - f(a)

	minError = min(temp)
	total = sum(temp)
	tempVal = 0
	results = []
	for i in range(len(temp)):
		fitnessVal = 1 -(temp[i]/total)
		results.append([population[i],fitnessVal + tempVal])
		tempVal+=fitnessVal


	# Order by fitness value
	results = sorted(results, key=lambda x: x[1])

	def getRandomParents(population):
		prob = random.random()
		i = 0
		while(results[i][1] < prob and i < len(results) -1):
			i+=1
		return results[i][0], results[i+1][0]

	newPopulation = []

	def mutate(child):
		for i in child:
			if(random.random()<=MUTATIONPROB):
				if i == "0":
					i=1
				else:
					i=0

	for i in range(len(population)):
		parent1, parent2 = getRandomParents(population)

		crossover = random.randint(1,14)
		child = parent1[0:crossover]
		child +=parent2[crossover:16]

		mutate(child)

		newPopulation.append(child)

	population = newPopulation
	return minError

# Repeat by ITERATIONS
steps = 0
while (steps < ITERATIONS):
	error = iterate(population)
	steps +=1
	if(error <= LIMIT):
		break

# Get best solution of current population
temp = [0]*POPULATIONSIZE

for i in range(len(population)):
	a = getA(population[i])
	for j in range(len(x)):
		temp[i] += abs(y[j] - estimate(x[j], a))

total = sum(temp)
results = []
for i in range(len(temp)):

	results.append([population[i],temp[i]/total])

# Order solutions by fitness
results = sorted(results, key=lambda x: x[1])


print(results[0])
a = getA(results[0][0])
totalError=0
for i in range(len(x)):
	print("X", x[i])
	print("Y", y[i])
	print("RESULT", estimate(x[i],a))
	print("PARTIAL ERROR:", abs(y[i] - estimate(x[i],a)))
	totalError+= abs(y[i] - estimate(x[i],a))

print("Individual", results[0][0])
print(a)
print("E={0:.2f}".format(totalError))
