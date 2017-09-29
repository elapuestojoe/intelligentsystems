# encoding: UTF-8

# Team members:
# Kevin Islas Abud      A01372023
# Miryam Villa Perez    A01371614

from search import (Problem, Node)
from utils import (probability)

import random
import math
import sys


def exp_schedule(k=20, lam=0.005, limit=100):
    return lambda t: (k * math.exp(-lam * t) if t < limit else 0)

def exp_schedule2(k=20, lam=0.005, limit=100):
    return lambda t: (k * (1 - (lam * t)) if t < limit else 0)


def simulated_annealing(problem, schedule=exp_schedule()):
    current = Node(problem.initial)
    for t in range(sys.maxsize):
        T = schedule(t)
        if T == 0:
            return current.state
        neighbors = current.expand(problem)
        if not neighbors:
            return current.state
        next = random.choice(neighbors)
        delta_e = problem.value(current.state) - problem.value(next.state)
        if delta_e > 0 or probability(math.exp(delta_e / T)):
            current = next


class SA(Problem):
    
    def __init__(self):
        self.initial = self.initialState()
    
        
    def initialState(self):
        string = bin(random.getrandbits(16))
        string = string[2::] # Cut string
        while(len(string) < 16):
            string = "0" + string
        return [string]
    
    
    def actions(self, state):
        r = int(random.getrandbits(4))
        string = state[0][0:r] + ("0", "1")[state[0][r] == "0"] + state[0][r + 1:16]
        return [string]
    
    
    def result(self, state, actions):
        return [actions]
        
    
    def value(self, state):
        x = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
        y = [26, -1, 4, 20, 0, -2, 19, 1, -4, 19]
        
        sum = 0
        a = self.getValueA(state[0])
        for i in range(len(x)):
            sum += abs(y[i] - self.estimate(x[i], a))
        
        return sum
    
    
    def getValueA(self, state):
        a0 = int(state[0:4],2)
        a1 = int(state[4:8],2)
        a2 = int(state[8:12],2)
        a3 = int(state[12:16],2)
        
        return [a0,a1,a2,a3]


    def estimate(self, x, a):
        return a[0] / (x * x) + a[1] * math.exp(a[2] / x) + a[3] * math.sin(x)



#=========================
# FIRST COOLING SCHEME
#=========================

s = SA()
res = simulated_annealing(s)

print("Cooling scheme: k * math.exp(-lam * t)")

print("- Temperature = 20, Lambda = 0.005 -")
print("\nInitial Values: ", s.getValueA(s.initial[0]), "\t", s.initial[0])
print("Initial solution sum error: ", s.value(s.initial))

print("\nFinal Values: ", s.getValueA(res[0]), "\t", res[0])
print("Final solution sum error: ", s.value(res))


res = simulated_annealing(s, exp_schedule(k=10000, lam=0.003, limit = 200))

print("\n\n- Temperature = 10000, Lambda = 0.003 -")
print("\nInitial Values: ", s.getValueA(s.initial[0]), "\t", s.initial[0])
print("Initial solution sum error: ", s.value(s.initial))

print("\nFinal Values: ", s.getValueA(res[0]), "\t", res[0])
print("Final solution sum error: ", s.value(res))



#=========================
# SECOND COOLING SCHEME
#=========================

res = simulated_annealing(s, exp_schedule2())

print("\n\nCooling scheme: k * (1 - (lam * t)")

print("\n- Temperature = 20, Lambda = 0.005 -")
print("\nInitial Values: ", s.getValueA(s.initial[0]), "\t", s.initial[0])
print("Initial solution sum error: ", s.value(s.initial))

print("\nFinal Values: ", s.getValueA(res[0]), "\t", res[0])
print("Final solution sum error: ", s.value(res))


res = simulated_annealing(s, exp_schedule2(k=10000, lam=0.003, limit = 200))

print("\n\n- Temperature = 10000, Lambda = 0.003 -")
print("\nInitial Values: ", s.getValueA(s.initial[0]), "\t", s.initial[0])
print("Initial solution sum error: ", s.value(s.initial))

print("\nFinal Values: ", s.getValueA(res[0]), "\t", res[0])
print("Final solution sum error: ", s.value(res))


