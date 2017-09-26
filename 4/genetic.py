import math
import random

def estimate(x, arrA):
	return ( (arrA[0]/(x*x)) + (arrA[1]* math.pow(math.e,(arrA[2]/x))) + arrA[3]*math.sin(x))

def getA(binString):

	a0 = int(string[0:4],2)
	a1 = int(string[4:8],2)
	a2 = int(string[8:12],2)
	a3 = int(string[12:16],2)

	return [a0,a1,a2,a3]

# First Population
population = []

for i in range(10):
	string = bin(random.getrandbits(16))
	# Cut string
	string = string[2::]
	while(len(string)<16):
		string="0"+string
	population.append(string)

# Solutions
x = [2,4,6,8,10,12,14,16,18,20]
y = [26,-1,4,20,0,-2,19,1,-4,19]

def iterate(population):
	# temp
	temp = [0]*10

	for i in range(len(population)):
		for j in range(len(population)):
			temp[i] += abs(y[j] - estimate(x[j], getA(population[i])))

	# Aquí tenemos errores
	results = []
	for i in range(len(temp)):
		# Normalizar
		results.append([population[i],temp[i]/total])

	# Ordenar
	results = sorted(results, key=lambda x: x[1])

	print(results)
	temp = 0
	# Acumular
	for result in results:
		temp += result[1]
		result[1] = temp

	print(temp)
	# Breeding:

	def getRandomParent(population):
		prob = random.random()
		i = 0
		while(results[i][1] < prob):
			i+=1
		return results[i][0]

	newPopulation = []

	def mutate(child):
		for i in child:
			if(random.random()>0.95):
				if i == "0":
					i=1
				else:
					i=0

	for i in range(len(population)):
		parent1 = getRandomParent(population)
		parent2 = getRandomParent(population)

		child = parent1[0:8]
		child +=parent2[8:16]

		mutate(child)

		newPopulation.append(child)

	population = newPopulation


# Repetir 10000 veces
for i in range(1):
	iterate(population)

print(population)
temp = [0]*10

for i in range(len(population)):
	for j in range(len(population)):
		temp[i] += abs(y[j] - estimate(x[j], getA(population[i])))

print(temp)