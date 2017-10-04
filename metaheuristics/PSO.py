import math
import random
def f(x):
	return x * math.sin(x)/2 + 10

minX = 0
maxX = 25
numParticles = maxX//3

class Particle():
	pBest = None
	C0 = 1
	C1 = 1
	C2 = 1
	def __init__(self, position):
		self.position = position
		self.velocity = 1

	def updateVelocity(self, gBest):
		self.velocity = \
			(self.C0 * self.velocity) + \
			(self.C1 * random.random() * (self.pBest - self.position)) + \
			(self.C2 * random.random() * (gBest - self.position))

	def updatePosition(self):
		self.position = self.position + self.velocity
		if(self.position < minX):
			self.position = minX
		if(self.position > maxX):
			self.position = maxX
class PSO():
	# Initialize particles
	particles = []
	for i in range(numParticles):
		particles.append(Particle(random.random()*maxX))

	gBest = None
	for i in range(1000):

		for particle in particles:
			fitness = f(particle.position)
			if(particle.pBest is None or fitness < particle.pBest):
				particle.pBest = fitness

			if gBest is None or fitness < f(gBest):
				gBest = particle.position

		for particle in particles:
			particle.updateVelocity(gBest)
			particle.updatePosition()

problem = PSO()

print("BEST", problem.gBest, f(problem.gBest))