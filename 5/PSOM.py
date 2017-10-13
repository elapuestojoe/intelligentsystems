import math
import random
import copy
import matplotlib.pyplot as plt

# random.seed(1)

def f(x, a):
	return (a[0]/x) + (a[1] * math.exp(a[2]/x)) + a[3]*math.sin(x)

minX = 0
maxX = 15
numParticles = 20
maxIterations = 100
maxVelocity = 3
C0 = 1
C1 = 2
C2 = 4-C1

x = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
y = [26, -1, 4, 20, 0, -2, 19, 1, -4, 19]

class Particle(object):
	counter = 0

	def getRandomA():
		a = []
		for i in range(4):
			a.append(random.random() * (maxX - minX))
		return a

	def position(self):
		# Compute position as sum of errors, attempt to minimize
		error = 0
		for i in range(len(x)):
			error += abs(f(x[i],self.a) - y[i])
		return error

	def getLocalBest(self):
		# Calculate 3 neighbors between current position and +- 1
		for i in range(3):
			neighbor = copy.deepcopy(self)
			for j in range(len(neighbor.a)):
				neighbor.a[j] += random.random()*2 - 1
				if(neighbor.a[j] < minX):
					neighbor.a[j] = minX
				elif(neighbor.a[j] > maxX):
					neighbor.a[j] = maxX
				if(self.pBest is None):
					self.pBest = [neighbor.a, neighbor.position()]
				elif(neighbor.position() < self.pBest[1]):
					self.pBest = [neighbor.a, neighbor.position()]

	def updateVelocities(self, gBest):

		for i in range(len(self.velocities)):
			self.velocities[i] = \
				(C0 * self.velocities[i]) + \
				(C1 * random.random() * (self.pBest[0][i] - self.a[i])) + \
				(C2 * random.random() * (gBest[0][i] - self.a[i]))
			if(self.velocities[i] > maxVelocity):
				self.velocities[i] = maxVelocity
			elif(self.velocities[i] < -maxVelocity):
				self.velocities[i] = -maxVelocity

	def updateA(self):
		for i in range(len(self.a)):
			self.a[i] += self.velocities[i]

			if(self.a[i] < minX):
				self.a[i] = minX
			elif(self.a[i] > maxX):
				self.a[i] = maxX

	def __init__(self):
		# Initialize a with 4 random values
		self.a = Particle.getRandomA()
		self.id = Particle.counter
		Particle.counter +=1
		self.velocities = [1,1,1,1]
		self.pBest = None

	def __repr__(self):
		return "ID {}, a {}, position {}".format(self.id, self.a, self.position())


class PSO():
	particles = []
	for i in range(numParticles):
		particles.append(Particle())
	gBest = None
	print("Initial Particles \n{}".format(particles))

	for i in range(maxIterations):

		for particle in particles:
			particle.getLocalBest()

			if(gBest is None or particle.pBest[1] < gBest[1]):
				gBest = particle.pBest

		for particle in particles:
			particle.updateVelocities(gBest)
			particle.updateA()

	# Sort by position
	particles = sorted(particles, key=lambda particle: particle.position())
	# plt.axis([min(x), min(y), max(x), max(y)])
	plt.axis([min(x)-3,max(x)+3,min(y)-3,max(y)+3])
	print(gBest[0])
	yArr = []
	for i in x:
		yArr.append(f(i, gBest[0]))
	# plt.plot(x, y, "g")
	# plt.plot(x, yArr, "r")
	plt.plot(x, y, "go")
	plt.plot(x, yArr, "rx")

problem = PSO()

print("--- END ---")
print("Global Best {} Position {}".format(problem.gBest[0], problem.gBest[1]))
plt.show()
