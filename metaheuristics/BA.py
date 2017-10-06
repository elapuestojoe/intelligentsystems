# encoding: UTF-8

import math
import random


minX = 0
maxX = 15

n = 7
m = 4
e = 2
m_e = m - e

ngh = 3.0
n2 = 4
n1 = 2

iterations = 1000



def f(x):
    return x * math.sin(x) / 2 + 10


class Bee():
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def show(self):
        print("x = %8s\ty = %8s" % (round(self.x, 4), round(self.y, 4)))

def main():
    
    print("\n*** Basic Bees Algorithm (BA) ***")
    
    bees = []
    for i in range(n):
        num = random.random() * maxX
        bees.append(Bee(num, f(num)))
    
    print("\n- Initial population of n=%d" % n)
    
    
    for i in range(iterations):
        
        print("\n\n----------------- Iteration #{} -----------------".format(i))
        
        bees.sort(key=lambda b: b.y, reverse=True)
    
        print("\n++ Random search and their fitness")
        for x in bees:
            x.show()

        mList = bees[0:m]
        eList = mList[0:e]
        m_eList = mList[m_e:m]
        
        
        print("\n++ Select the m = %d best sites" % m)
        for x in mList:
            x.show()
        
        print("\n++ Select the e = %d elite bees:" % e)
        for x in eList:
            x.show()
        
        print("\n++ Select the m-e = %d selected bees:" % m_e)
        for x in m_eList:
            x.show()
        
        print("\n++ Neighborhood size ngh = %d" % ngh)
        
        eNeighbors = []
        m_eNeighbors = []
        bestBees = bees[m:n]
    
    
        print("\n++ Recruits onlooker bees")
        
        print("\n  + n2 = %d for 'e' elite sites" % n2)
        for b in eList:
        
            xV = b.x
            maxV = b.y
            
            print("° Bees for %.5f" % xV)
            
            for i in range(n2):
                maxR = (b.x + ngh / 2.0, maxX)[(maxX - (b.x + ngh / 2)) < 0]
                minR = (b.x - ngh / 2.0, minX)[(b.x - ngh / 2) < 0]
                
                vecinito = random.random() * (maxR - minR) + minR
                fitness = f(vecinito)
                
                print("  x = %8s\ty = %8s" % (round(vecinito, 4), round(fitness, 4)))
                
                if (fitness > maxV):
                    xV = vecinito
                    maxV = fitness
                        
            eNeighbors.append(Bee(xV, maxV))
            bestBees.append(Bee(xV, maxV))
        
        
        print("\n  + n1 = %d for the other 'm-e' sites" %n1)
        for b in m_eList:
            
            xV = b.x
            maxV = b.y
            
            print("° Bees for %.5f" % xV)
            
            for i in range(n1):
                maxR = (b.x + ngh / 2.0, maxX)[(maxX - (b.x + ngh / 2)) < 0]
                minR = (b.x - ngh / 2.0, minX)[(b.x - ngh / 2) < 0]
                
                vecinito = random.random() * (maxR - minR) + minR
                fitness = f(vecinito)
                
                print("  x = %8s\ty = %8s" % (round(vecinito, 4), round(fitness, 4)))
                
                if (fitness > maxV):
                    xV = vecinito
                    maxV = fitness
                
            m_eNeighbors.append(Bee(xV, maxV))
            bestBees.append(Bee(xV, maxV))
        
        
        print("\n++ Select the bee with the greatest fitness for each site")
        for x in eNeighbors:
            x.show()
        
        for x in m_eNeighbors:
            x.show()
        
        
        print("\n++ Assign the n-m=%d remaining bees as scouts" % (n-m))
        for x in range(n-m):
            bestBees[x].show()
        
        
        bestBees.sort(key=lambda b: b.y, reverse=True)
        
        bees = []
        bees = bestBees


    print("\n\n=========================================")
    print("\nBest bee : {}".format(bees[0].x))
    print("Fitness of best bee : {}\n".format(f(bees[0].x)))


main()