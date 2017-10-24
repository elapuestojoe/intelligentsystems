def fitness(x):
	return ((x * (x - 12) * (x - 20) * (x - 28)) / (-1000)) + 20


val = [fitness(1), fitness(10), fitness(20), fitness(30)]

print(val)

total = sum(val)

print("SUM", total)
print("AVG", total/len(val))
prob = 0
for i in range(len(val)):
	val[i] /= total
	prob += val[i]
	print("Cumulative probability", prob)
	
print(val)
