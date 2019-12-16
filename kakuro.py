import sys
import random
from Tkinter import Tk, Canvas, Frame, Button, BOTH, TOP, RIGHT
from datetime import datetime
# from pulp import *

random.seed(datetime.now())

MARGIN = 20
SIDE = 50
WIDTH = HEIGHT = MARGIN * 2 + SIDE * 9

class KakuroError(Exception):
	"""
	An application specific error.
	"""
	pass

class KakuroUI(Frame):
	"""
	The Tkinter UI: draw the board and accept input
	"""
	def __init__(self, parent, game):
		self.game = game
		Frame.__init__(self, parent)
		self.parent = parent
		self.row, self.col = -1, -1
		self.initUI()

	def initUI(self):
		if self.game.gameId != 0:
			self.parent.title("Kakuro | Puzzle: "+str(self.game.gameId))
		else:
			self.parent.title("Kakuro | Puzzle: Custom")
		self.pack(fill=BOTH, expand=1)
		self.canvas = Canvas(self, width=WIDTH, height=HEIGHT, highlightthickness=0)
		self.canvas.pack(fill=BOTH, side=TOP)

		solve_button = Button(self, text="Solve!", command=self.solve)
		solve_button.pack(side=RIGHT, padx = 10)
		clear_button = Button(self, text="Clear answers", command=self.clear_answers)
		clear_button.pack(side=RIGHT)

		self.draw_grid()
		self.draw_puzzle()

		self.canvas.bind("<Button-1>", self.cell_clicked)
		self.canvas.bind("<Up>", self.Upkey_pressed)
		self.canvas.bind("<Down>", self.Downkey_pressed)
		self.canvas.bind("<Right>", self.Rightkey_pressed)
		self.canvas.bind("<Left>", self.Leftkey_pressed)
		self.canvas.bind("<BackSpace>", self.Bkspkey_pressed)
		self.canvas.bind("<Key>", self.key_pressed)

	def draw_grid(self):
		for i in range(10):
			stretch = 0
			if i % 9 == 0:
				stretch = 1
			self.canvas.create_line(
				MARGIN + i * SIDE, MARGIN - stretch,
				MARGIN + i * SIDE, HEIGHT - MARGIN + stretch,
				width=2
			)

			self.canvas.create_line(
				MARGIN, MARGIN + i * SIDE,
						WIDTH - MARGIN, MARGIN + i * SIDE,
				width=2
			)

		for i in range(9):
			for j in range(9):
				if [i, j] not in self.game.data_fills:
					self.canvas.create_rectangle(MARGIN + j * SIDE + 1, MARGIN + i * SIDE + 1,
												 MARGIN + j * SIDE + SIDE - 2, MARGIN + i * SIDE + SIDE - 2,
												 outline="gray", fill="gray", tag = "grays")
					self.canvas.create_line(
						MARGIN + j * SIDE, MARGIN + i * SIDE,
						MARGIN + j * SIDE + SIDE, MARGIN + i * SIDE + SIDE,
						width=2, tag = "grayliners"
					)

	def draw_puzzle(self):
		self.canvas.delete("numbersfilled")
		for elem in self.game.data_totals:
			i = elem[3][0]
			j = elem[3][1]
			if elem[1] == 'v':
				modif = -1
			else:
				modif = 1
			self.canvas.create_text(
				MARGIN + j * SIDE + SIDE / 2 + modif * SIDE / 4,
				MARGIN + i * SIDE + SIDE / 2 + (-modif) * SIDE / 4,
				text=elem[0], tags="numbers",
				fill="black"
			)
		for elem in self.game.data_filled:
			i = elem[0]
			j = elem[1]
			self.canvas.create_text(
				MARGIN + j * SIDE + SIDE / 2,
				MARGIN + i * SIDE + SIDE / 2,
				font=("Purissa", 20),
				text=elem[2], tags="numbersfilled",
				fill="slate gray"
			)

	def draw_cursor(self):
		self.canvas.delete("cursor")
		if self.row >= 0 and self.col >= 0:
			self.canvas.create_rectangle(
				MARGIN + self.col * SIDE + 1,
				MARGIN + self.row * SIDE + 1,
				MARGIN + (self.col + 1) * SIDE - 1,
				MARGIN + (self.row + 1) * SIDE - 1,
				outline="red", tags="cursor"
			)

	def create_circs(self, addrs):
		if len(addrs)==0:
			return
		for elem in addrs:
			self.canvas.create_oval(
				# Figure out the inversion!
				MARGIN + SIDE * elem[1], MARGIN + SIDE * elem[0],
				MARGIN + SIDE * elem[1] + SIDE, MARGIN + SIDE * elem[0] + SIDE,
				tags="circ", outline="red", width=2.0
			)

	def draw_victory(self):
		self.canvas.create_oval(
			MARGIN + SIDE * 2, MARGIN + SIDE * 2,
			MARGIN + SIDE * 7, MARGIN + SIDE * 7,
			tags="victory", fill="dark orange", outline="orange"
		)
		self.canvas.create_text(
			MARGIN + 4 * SIDE + SIDE / 2,
			MARGIN + 4 * SIDE + SIDE / 2,
			text="Correct!", tags="victory",
			fill="white", font=("Ubuntu", 32)
		)

	def cell_clicked(self, event):
		if self.game.game_over:
			return
		x, y = event.x, event.y
		if (x > MARGIN and x < WIDTH - MARGIN and
				y > MARGIN and y < HEIGHT - MARGIN):
			self.canvas.focus_set()
			row, col = (y - MARGIN) / SIDE, (x - MARGIN) / SIDE
			self.row, self.col = row, col
		else:
			self.row, self.col = -1, -1
		self.draw_cursor()

	def road(self, addr):
		if bool(addr[0] == self.row) == bool(addr[1] == self.col):
			return False
		elif addr[0] == self.row:
			curr_row = self.row
			for iter in range(min(addr[1],self.col), max(addr[1],self.col)):
				if [curr_row, iter] not in self.game.data_fills:
					return False
			return True
		else:
			curr_col = self.col
			for iter in range(min(addr[0],self.row), max(addr[0],self.row)):
				if [iter, curr_col] not in self.game.data_fills:
					return False
			return True

	def key_pressed(self, event):
		self.canvas.delete("victory")
		self.canvas.delete("circ")
		if self.game.game_over:
			return
		if self.row >= 0 and self.col >= 0 and event.char in "123456789" and event.char!='' and [self.row, self.col] in self.game.data_fills:
			found_flag = False
			for ind, item in enumerate(self.game.data_filled):
				if item[0]==self.row and item[1]==self.col:
					found_flag = True
					self.game.data_filled[ind][2] = int(event.char)
			if(not found_flag):
				self.game.data_filled = self.game.data_filled + [[self.row, self.col, int(event.char)]]

			circlists = []
			for elem in self.game.data_filled:
				if self.road(elem) and elem[2]==int(event.char):
					if [self.row, self.col] not in circlists:
						circlists = circlists + [[self.row, self.col]]
					if [elem[0], elem[1]] not in circlists:
						circlists = circlists + [[elem[0], elem[1]]]
			self.create_circs(circlists)
			self.draw_puzzle()
			self.draw_cursor()
			if self.game.check_win():
				self.draw_victory()

	def Upkey_pressed(self, event):
		self.canvas.delete("victory")
		if self.game.game_over:
			return
		if self.row > 0 and self.col >= 0:
			self.row = self.row - 1
			self.draw_cursor()

	def Downkey_pressed(self, event):
		self.canvas.delete("victory")
		if self.game.game_over:
			return
		if self.row >= 0 and self.col >= 0 and self.row < 8:
			self.row = self.row + 1
			self.draw_cursor()

	def Rightkey_pressed(self, event):
		self.canvas.delete("victory")
		if self.game.game_over:
			return
		if self.row >= 0 and self.col >= 0 and self.col <8:
			self.col = self.col + 1
			self.draw_cursor()

	def Leftkey_pressed(self, event):
		self.canvas.delete("victory")
		if self.game.game_over:
			return
		if self.row >= 0 and self.col > 0:
			self.col = self.col - 1
			self.draw_cursor()

	def Bkspkey_pressed(self, event):
		self.canvas.delete("victory")
		self.canvas.delete("circ")
		if self.game.game_over:
			return
		if self.row >=0 and self.col >=0:
			self.game.data_filled = [item for item in self.game.data_filled if item[0]!=self.row or item[1]!=self.col]
		self.draw_cursor()
		self.draw_puzzle()

	def clear_answers(self):
		self.game.data_filled = []
		self.canvas.delete("victory")
		self.canvas.delete("circ")
		self.draw_puzzle()

	def solve(self):
		self.game.data_filled = []
		self.canvas.delete("victory")
		self.canvas.delete("circ")
		options = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
		# Remember to zero down the indices
		vals = options
		rows = options
		cols = options
		prob = LpProblem("Kakuro Problem", LpMinimize)
		choices = LpVariable.dicts("Choice", (vals, rows, cols), 0, 1, LpInteger)
		# The complete set of boolean choices
		prob += 0, "Arbitrary Objective Function"
		# Force singular values. Even for extraneous ones
		for r in rows:
			for c in cols:
				prob += lpSum([choices[v][r][c] for v in vals]) == 1, ""

		# Force uniqueness in each 'zone' and sum constraint for that zone
		# Row zones
		for r in rows:
			zonecolsholder = []
			activated = False
			zonecolssumholder = 0
			for c in cols:
				if not activated and [int(r)-1,int(c)-1] in self.game.data_fills:
					activated = True
					zonecolsholder = zonecolsholder +[c]
					zonecolssumholder = [elem[0] for elem in self.game.data_totals if elem[1]=='h' and elem[2] == int(r)-1 and elem[3] == int(c)-2][0]
					if c == "9":
						# Uniqueness in that zone of columns
						for v in vals:
							prob += lpSum([choices[v][r][co] for co in zonecolsholder]) <= 1, ""
						# Sum constraint for that zone of columns
						prob += lpSum([int(v) * choices[v][r][co] for v in vals for co in zonecolsholder]) == zonecolssumholder, ""
				elif activated and [int(r)-1,int(c)-1] in self.game.data_fills:
					zonecolsholder = zonecolsholder + [c]
					if c == "9":
						# Uniqueness in that zone of columns
						for v in vals:
							prob += lpSum([choices[v][r][co] for co in zonecolsholder]) <= 1, ""
						# Sum constraint for that zone of columns
						prob += lpSum([int(v) * choices[v][r][co] for v in vals for co in zonecolsholder]) == zonecolssumholder, ""
				elif activated and [int(r)-1,int(c)-1] not in self.game.data_fills:
					activated = False
					# Uniqueness in that zone of columns
					for v in vals:
						prob += lpSum([choices[v][r][co] for co in zonecolsholder]) <= 1, ""
					# Sum constraint for that zone of columns
					prob += lpSum([int(v)*choices[v][r][co] for v in vals for co in zonecolsholder]) == zonecolssumholder, ""
					zonecolssumholder = 0
					zonecolsholder = []

		# Col zones
		for c in cols:
			zonerowsholder = []
			activated = False
			zonerowssumholder = 0
			for r in rows:
				if not activated and [int(r)-1,int(c)-1] in self.game.data_fills:
					activated = True
					zonerowsholder = zonerowsholder +[r]
					zonerowssumholder = [elem[0] for elem in self.game.data_totals if elem[1]=='v' and elem[2] == int(r)-2 and elem[3] == int(c)-1][0]
					if r == "9":
						# Uniqueness in that zone of rows
						for v in vals:
							prob += lpSum([choices[v][ro][c] for ro in zonerowsholder]) <= 1, ""
						# Sum constraint for that zone of rows
						prob += lpSum([int(v) * choices[v][ro][c] for v in vals for ro in zonerowsholder]) == zonerowssumholder, ""
				elif activated and [int(r)-1,int(c)-1] in self.game.data_fills:
					zonerowsholder = zonerowsholder + [r]
					if r == "9":
						# Uniqueness in that zone of rows
						for v in vals:
							prob += lpSum([choices[v][ro][c] for ro in zonerowsholder]) <= 1, ""
						# Sum constraint for that zone of rows
						prob += lpSum([int(v) * choices[v][ro][c] for v in vals for ro in zonerowsholder]) == zonerowssumholder, ""
				elif activated and [int(r)-1,int(c)-1] not in self.game.data_fills:
					activated = False
					# Uniqueness in that zone of rows
					for v in vals:
						prob += lpSum([choices[v][ro][c] for ro in zonerowsholder]) <= 1, ""
					# Sum constraint for that zone of rows
					prob += lpSum([int(v)*choices[v][ro][c] for v in vals for ro in zonerowsholder]) == zonerowssumholder, ""
					zonerowssumholder = 0
					zonerowsholder = []

		# Force all extraneous values to 1 (arbitrary) | Possibly many times
		for ite in self.game.data_totals:
			prob += choices["1"][str(ite[2]+1)][str(ite[3]+1)] == 1, ""

		# Suppress calculation messages
		GLPK(msg=0).solve(prob)
		# Solution: The commented print statements are for debugging aid.
		for v in prob.variables():
			# print v.name, "=", v.varValue
			if v.varValue == 1 and [int(v.name[9])-1, int(v.name[11])-1] in self.game.data_fills:
				# print v.name, ":::", v.varValue, [int(v.name[9])-1, int(v.name[11])-1, int(v.name[7])]
				self.game.data_filled = self.game.data_filled + [[int(v.name[9])-1, int(v.name[11])-1, int(v.name[7])]]
		self.draw_puzzle()

class KakuroCustomGame(object):
	def __init__(self):
		self.played_so_far = []
		self.data_filled = []
		self.data_fills = []
		self.data_totals = []
		self.data_tricks = []
		self.take_inp()

	def take_inp(self):
		for i in range(9):
			text = raw_input()
			proced = [ele.split('\\') for ele in text.split(',')]
			if(len(proced) != 9):
				raise KakuroError('Nine cells a line or else format not followed!\n')
			for j in range(9):
				if len(proced[j]) == 1 and proced[j][0] == ' ':
					self.data_fills = self.data_fills + [[i,j]]
				elif len(proced[j]) == 2:
					if proced[j][0]!=' ':
						self.data_totals = self.data_totals + [[int(proced[j][0]),'v',[i,j]]]
					if proced[j][1]!=' ':
						self.data_totals = self.data_totals + [[int(proced[j][1]),'h',[i,j]]]
		self.process_inp()
		print('\nStarting custom game. Click anywhere on the grid to begin...')
		self.gameId = 0
		self.game_over = False

	def sort(self, lst):
		lst.sort(key = lambda x: x[2]) 
		return lst 

	def findCombinationsUtil(self, arr, index, num, reducedNum, size, comb):
		if (reducedNum < 0):
			return
		if (reducedNum == 0 and index == size):
			temp = []
			for i in range(index):
				temp.append(arr[i])
			comb.append(temp)
			return
		prev = 1 if(index == 0) else arr[index - 1] + 1;
		for k in range(prev, 10):
			arr[index] = k;
			self.findCombinationsUtil(arr, index + 1, num, reducedNum - k, size, comb)

	def findCombinations(self, n, size):
		arr = [0] * n
		comb = []
		self.findCombinationsUtil(arr, 0, n, n, size, comb)
		return comb

	def process_inp(self):
		for i in range(len(self.data_totals)):
			continuity = True
			count = 0
			x = self.data_totals[i][2][0]
			y = self.data_totals[i][2][1]
			temp = []
			if "v" in self.data_totals[i]:
				while(continuity):
					x += 1
					if [x, y] in self.data_fills:
						temp.append([x, y])
						count += 1
					else:
						continuity = False
						self.data_totals[i].insert(2, count)
			elif "h" in self.data_totals[i]:
				while(continuity):
					y += 1
					if [x, y] in self.data_fills:
						temp.append([x, y])
						count += 1
					else:
						self.data_totals[i].insert(2, count)
						continuity = False
			self.data_totals[i].append(temp)
			comb = self.findCombinations(self.data_totals[i][0], self.data_totals[i][2])
			self.data_totals[i].append(comb)
		self.sort(self.data_totals)
		for i in self.data_totals:
			print(i)

	def check_win(self):
		if(len(self.data_filled) == len(self.data_fills)):
			for item in self.data_filled:
				if [item[0], item[1]-1] not in self.data_fills:
					sumexp = -1
					for elem in self.data_totals:
						if elem[2] == item[0] and elem[3] == item[1]-1 and elem[1] == 'h':
							sumexp = elem[0]
					offset = 0
					sumact = []
					while [item[0], item[1]+offset] in self.data_fills:
						sumact = sumact + [e[2] for e in self.data_filled if e[0] == item[0] and e[1] == item[1]+offset]
						offset = offset + 1
					if len(sumact) != len(set(sumact)):
						return False
					if sumexp != -1 and sumexp != sum(sumact):
						return False
			for item in self.data_filled:
				if [item[0]-1, item[1]] not in self.data_fills:
					sumexp = -1
					for elem in self.data_totals:
						if elem[2] == item[0]-1 and elem[3] == item[1] and elem[1] == 'v':
							sumexp = elem[0]
					offset = 0
					sumact = []
					while [item[0]+offset, item[1]] in self.data_fills:
						sumact = sumact + [e[2] for e in self.data_filled if e[0] == item[0]+offset and e[1] == item[1]]
						offset = offset + 1
					if len(sumact) != len(set(sumact)):
						return False
					if sumexp != -1 and sumexp != sum(sumact):
						return False
			return True
		else:
			return False


if __name__ == '__main__':
	game = KakuroCustomGame()
	root = Tk()
	ui = KakuroUI(root, game)
	root.geometry("%dx%d" % (WIDTH, HEIGHT + 40))
	root.mainloop()