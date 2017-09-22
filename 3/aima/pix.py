from csp import CSP


class pixConfiguration:
	def __init__(self, number, color):
		self.number = number
		self.color = color

	def __repr__(self):
		return "{}{}".format(self.number, self.color)

class Pix(CSP):
	board = None
	rows = 0
	columns = 0
 
	def __init__(self, columns = 5, rowConfigurations = None, columnConfigurations = None):
		v = None
		self.board = [[0 for x in range(columns)] for y in range(columns)]
		self.rows = columns
		self.columns = columns
		self.columnConfigurations, self.rowConfigurations = self.setupConstraints(rowConfigurations, columnConfigurations)

		self.domain = ["Red", "Green", "Red", 0]
		self.variables = self.board

		# TODO
		CSP.__init__(self, self.variables, self.domain, None, None)
	def display(self):

		print("Constraints")
		print("columnConfigurations")
		print(self.columnConfigurations)
		print("rowConfigurations")
		print(self.rowConfigurations)
		print("-----------")
		print("BOARD")

		# self.board[0][0] = 1
		for j in range(self.columns -1, -1, -1):
			for i in range(0, self.columns):
				print(self.board[i][j], end = " ")

			print("")

	def setupConstraints(self, rowConfigurations, columnConfigurations):

		if(not columnConfigurations):
			columnConfigurations = [list() for x in range(self.columns)]

		# Abajo a arriba
		columnConfigurations[0].append(pixConfiguration(1,"Green"))

		columnConfigurations[1].append(pixConfiguration(1,"Green"))

		columnConfigurations[2].append(pixConfiguration(2,"Green"))
		columnConfigurations[2].append(pixConfiguration(1,"Red"))

		columnConfigurations[3].append(pixConfiguration(1,"Red"))
		columnConfigurations[3].append(pixConfiguration(1,"Blue"))
		columnConfigurations[3].append(pixConfiguration(1,"Red"))

		columnConfigurations[4].append(pixConfiguration(1,"Red"))

		if(not rowConfigurations):
			rowConfigurations = [list() for x in range(self.columns)]

		# ORIGEN en (0,0)

		rowConfigurations[0].append(pixConfiguration(2, "Green"))

		rowConfigurations[1].append(pixConfiguration(1, "Green"))
		rowConfigurations[1].append(pixConfiguration(1, "Green"))

		rowConfigurations[2].append(pixConfiguration(1, "Red"))

		# Izquierda a derecha
		rowConfigurations[3].append(pixConfiguration(1, "Red"))
		rowConfigurations[3].append(pixConfiguration(1," Blue"))
		rowConfigurations[3].append(pixConfiguration(1,"Red"))

		rowConfigurations[4].append(pixConfiguration(1, "Red"))

		return columnConfigurations, columnConfigurations

		# Not sure yet
		def pix_constraint(A, a, B, b, recurse=0):
			print("")
		

		def nconflicts(self, var, val, assignment):
			return 1
			red0 = 0
			green0 = 0
			blue0 = 0

			# for pixConfiguration in self.columnConfigurations[0]:
			# 	if(pixConfiguration.color == "Green"):
			# 		green0 = pixConfiguration.number

			greenS0 = 0
			# for x in range(self.columns):
			# 	if(self.variables[0][x].color == "Green"):
			# 		greenS0 += self.variables[0][x].number
			return abs(greenS0 - green0)
pix = Pix()
pix.display()
# def __init__(self, variables, domains, neighbors, constraints):