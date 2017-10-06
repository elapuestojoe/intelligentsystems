import math
import random

random.seed(1)

def f(x):
	return x * math.sin(x)/2 + 10

minX = 0
maxX = 50
numParticles = 7

C0 = 1
C1 = 1
C2 = 4 - C1
maxVelocity = 3

iterations = 10

class Particle(object):
	counter = 1
	def __init__(self, position):
		self.position = position
		self.velocity = 1
		self.pBest = None
		self.id = Particle.counter
		Particle.counter+=1
	def __repr__(self):
		return "ID: {}, Position: {}, Velocity: {}, Pbest: {}\n".format(self.id,self.position, self.velocity, self.pBest)

	def updateVelocity(self, gBest):

		print("Update velocity of particle {}".format(self.id))

		print("Current velocity = {}".format(self.velocity))

		print("C0 * self.velocity = {} * {} = {}".format(C0, self.velocity, C0*self.velocity))
		r1 = random.random()
		print("C1 * randomN * (pBest - position) = {} * {} * ({} - {}) = {}".format(C1, r1, self.pBest, self.position,\
			(C1 * random.random() * (self.pBest - self.position))))

		r2 = random.random()
		print("C2 * randomN * (gBest - position) = {} * {} * ({} - {}) = {}".format(C2, r2, gBest, self.position,\
			(C2 * r2 * (gBest - self.position))))

		self.velocity = \
			(C0 * self.velocity) + \
			(C1 * r1 * (self.pBest - self.position)) + \
			(C2 * r2 * (gBest - self.position))

		print("New velocity = {}".format(self.velocity))
		if(self.velocity > maxVelocity):
			print("Velocity is higher than maxVelocity {0}, so it gets updated to {0}".format(maxVelocity))
			self.velocity = maxVelocity
		if(self.velocity < -maxVelocity):
			print("Velocity is higher than minVelocity {0}, so it gets updated to {0}".format(-maxVelocity))
			self.velocity = -maxVelocity

		print("\n")

	def updatePosition(self):
		print("Update position of particle {}".format(self.id))
		print("Current position: {}".format(self.position))
		print("Current velocity: {}".format(self.velocity))

		print("New position = {} + {} = {}\n".format(self.position, self.velocity, self.position+self.velocity))
		self.position = self.position + self.velocity
		if(self.position < minX):
			self.position = minX
		if(self.position > maxX):
			self.position = maxX

	def getLocalBest(self):
		# La idea es explorar el vecindario local y obtener la mejor posición
		# Como las soluciones son continuas, se debe explorar un número discreto de vecinos
		# Como el rango de vecinos es 3, debemos calcular +=1.5
		print("Local best of particle {} = {}".format(self.id, self.pBest))
		print("Calculate 3 neighbors between current position and += 3")
		for i in range(3):
			position = random.uniform(self.position-3,self.position+3)
			print("Neighbor {}, {}".format(i,position))
			# Bound to limits
			if position < minX:
				print("Position is lower than lower bound {0}, so we transform it to {0}".format(minX))
				position = minX
			if position > maxX:
				print("Position is higher than upper bound {0}, so we transform it to {0}".format(maxX))
				position = maxX

			if(self.pBest is None):
				self.pBest = position
			elif(f(position) < f(self.pBest)):
				print("f({0}) = {1} is lower than f({2}) = {3}, so the new local best will be {0}"\
					.format(position, f(position), self.position, f(self.position)))
				self.pBest = position
		print("Final local best of particle is {}\n".format(self.pBest))



class PSO():
	# Initialize particles
	particles = []
	for i in range(numParticles):
		particles.append(Particle(random.random()*maxX))
	gBest = None
	print("Initial Particles \n{}".format(particles))
	for i in range(iterations):
		print("-----------Iteration #{}\n".format(i))
		for particle in particles:
			particle.getLocalBest()

			if gBest is None or f(particle.pBest) < f(gBest):
				if(gBest == None):
					print("------ gBest update:\ngBest is None, so we update it to our current best, which is {}\n------\n".format(particle.position))
				else:
					print("------ gBest update:\nf({0}) = {1} < f({2}) = {3}, so gBest gets updated to {0}\n------\n"\
						.format(particle.pBest, f(particle.pBest), gBest, f(gBest)))
				gBest = particle.position

		for particle in particles:
			particle.updateVelocity(gBest)
			particle.updatePosition()
		print("-----------End of Iteration #{}\n".format(i))

problem = PSO()

print("Final particles {}".format(problem.particles))
bestParticle = problem.particles[0]
for i in range(1, len(problem.particles)):
	particle = problem.particles[i]

	if(f(particle.position) < f(bestParticle.position)):
		bestParticle = particle


print("\nBest particle : {}".format(bestParticle))
print("Fitness of best particle = {}".format(f(bestParticle.position)))