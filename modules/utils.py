import random
from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor, QPainter

 
class tetrisShape():
	def __init__(self, shape=0):
		# 빈 모듈
		self.shape_empty = 0
		# 일자형 모듈
		self.shape_I = 1
		# L형 모듈
		self.shape_L = 2
		# 좌측 L형 모듈
		self.shape_J = 3
		# T형모듈
		self.shape_T = 4
		# 전지형 모듈
		self.shape_O = 5
		# 역 Z영 모듈
		self.shape_S = 6
		# Z형 모듈
		self.shape_Z = 7
		# 각 블록에 포함된 4개의 작은 사각 블록 상대 좌표 분포
		self.shapes_relative_coords = [
										 [[0, 0], [0, 0], [0, 0], [0, 0]],
										 [[0, -1], [0, 0], [0, 1], [0, 2]],
										 [[0, -1], [0, 0], [0, 1], [1, 1]],
										 [[0, -1], [0, 0], [0, 1], [-1, 1]],
										 [[0, -1], [0, 0], [0, 1], [1, 0]],
										 [[0, 0], [0, -1], [1, 0], [1, -1]],
										 [[0, 0], [0, -1], [-1, 0], [1, -1]],
										 [[0, 0], [0, -1], [1, 0], [-1, -1]]
									  ]
		self.shape = shape
		self.relative_coords = self.shapes_relative_coords[self.shape]
	'''이 형상의 현재 회전 상태를 얻는 4개의 작은 사각 블록의 상대적 좌표 분포'''
	def getRotatedRelativeCoords(self, direction):
		# 초기 분포
		if direction == 0 or self.shape == self.shape_O:
			return self.relative_coords
		# 시계 반대 방향으로 90도 회전
		if direction == 1:
			return [[-y, x] for x, y in self.relative_coords]
		# 시계 반대 방향으로 180도 회전
		if direction == 2:
			if self.shape in [self.shape_I, self.shape_Z, self.shape_S]:
				return self.relative_coords
			else:
				return [[-x, -y] for x, y in self.relative_coords]
		# 시계 반대 방향으로 270도 회전
		if direction == 3:
			if self.shape in [self.shape_I, self.shape_Z, self.shape_S]:
				return [[-y, x] for x, y in self.relative_coords]
			else:
				return [[y, -x] for x, y in self.relative_coords]
	'''이 테트리스의 각 조각의 절대 좌표를 얻다'''
	def getAbsoluteCoords(self, direction, x, y):
		return [[x+i, y+j] for i, j in self.getRotatedRelativeCoords(direction)]
	'''상대적 좌표의 경계를 얻다'''
	def getRelativeBoundary(self, direction):
		relative_coords_now = self.getRotatedRelativeCoords(direction)
		xs = [i[0] for i in relative_coords_now]
		ys = [i[1] for i in relative_coords_now]
		return min(xs), max(xs), min(ys), max(ys)
	
'''내부 판'''
class InnerBoard():
	def __init__(self, width=10, height=22):
		# 너비와 길이, 단위 길이는 작은 네모난 변의 길이
		self.width = width
		self.height = height
		self.reset()
	'''현재 테트리스를 어느 위치로 이동할 수 있는지 여부를 판단하다'''
	def ableMove(self, coord, direction=None):
		assert len(coord) == 2
		if direction is None:
			direction = self.current_direction
		for x, y in self.current_tetris.getAbsoluteCoords(direction, coord[0], coord[1]):
			# 범위를 벗어
			if x >= self.width or x < 0 or y >= self.height or y < 0:
				return False
			# 그 자리에는 테트리스가 있다
			if self.getCoordValue([x, y]) > 0:
				return False
		return True
	'''오른쪽으로 이동하다'''
	def moveRight(self):
		if self.ableMove([self.current_coord[0]+1, self.current_coord[1]]):
			self.current_coord[0] += 1
	'''왼쪽으로 이동하다'''
	def moveLeft(self):
		if self.ableMove([self.current_coord[0]-1, self.current_coord[1]]):
			self.current_coord[0] -= 1
	'''시계 방향으로 돌다'''
	def rotateClockwise(self):
		if self.ableMove(self.current_coord, (self.current_direction-1) % 4):
			self.current_direction = (self.current_direction-1) % 4
	'''시계 반대 방향으로 돌다'''
	def rotateAnticlockwise(self):
		if self.ableMove(self.current_coord, (self.current_direction+1) % 4):
			self.current_direction = (self.current_direction+1) % 4
	'''아래로 이동하다'''
	def moveDown(self):
		removed_lines = 0
		if self.ableMove([self.current_coord[0], self.current_coord[1]+1]):
			self.current_coord[1] += 1
		else:
			x_min, x_max, y_min, y_max = self.current_tetris.getRelativeBoundary(self.current_direction)
			# 간단히 보면, 스크린을 벗어나면 게임의 종료를 판정한다
			if self.current_coord[1] + y_min < 0:
				self.is_gameover = True
				return removed_lines
			self.mergeTetris()
			removed_lines = self.removeFullLines()
			self.createNewTetris()
		return removed_lines
	'''坠落'''
	def dropDown(self):
		removed_lines = 0
		while self.ableMove([self.current_coord[0], self.current_coord[1]+1]):
			self.current_coord[1] += 1
		x_min, x_max, y_min, y_max = self.current_tetris.getRelativeBoundary(self.current_direction)
		# 간단히 보면, 스크린을 벗어나면 게임의 종료를 판정한다
		if self.current_coord[1] + y_min < 0:
			self.is_gameover = True
			return removed_lines
		self.mergeTetris()
		removed_lines = self.removeFullLines()
		self.createNewTetris()
		return removed_lines
	'''테트리스 통합(맨 아래 세팅된 다시는 움직일 수 없는 것들)'''
	def mergeTetris(self):
		for x, y in self.current_tetris.getAbsoluteCoords(self.current_direction, self.current_coord[0], self.current_coord[1]):
			self.board_data[x + y * self.width] = self.current_tetris.shape
		self.current_coord = [-1, -1]
		self.current_direction = 0
		self.current_tetris = tetrisShape()
	'''한 줄 한 줄 작은 네모난 것을 꺼내다'''
	def removeFullLines(self):
		new_board_data = [0] * self.width * self.height
		new_y = self.height - 1
		removed_lines = 0
		for y in range(self.height-1, -1, -1):
			cell_count = sum([1 if self.board_data[x + y * self.width] > 0 else 0 for x in range(self.width)])
			if cell_count < self.width:
				for x in range(self.width):
					new_board_data[x + new_y * self.width] = self.board_data[x + y * self.width]
				new_y -= 1
			else:
				removed_lines += 1
		self.board_data = new_board_data
		return removed_lines
	
	def createNewTetris(self):
		x_min, x_max, y_min, y_max = self.next_tetris.getRelativeBoundary(0)
		# y_min틀림없이 -1
		if self.ableMove([self.init_x, -y_min]):
			self.current_coord = [self.init_x, -y_min]
			self.current_tetris = self.next_tetris
			self.next_tetris = self.getNextTetris()
		else:
			self.is_gameover = True
		self.shape_statistics[self.current_tetris.shape] += 1
	'''다음 테트리스를 얻다'''
	def getNextTetris(self):
		return tetrisShape(random.randint(1, 7))
	'''판 데이터 얻다'''
	def getBoardData(self):
		return self.board_data
	'''판 데이터 상의 어떤 좌표의 값을 얻다'''
	def getCoordValue(self, coord):
		return self.board_data[coord[0] + coord[1] * self.width]
	'''테트리스의 각 작은 덩어리의 절대 좌표를 얻다'''
	def getCurrentTetrisCoords(self):
		return self.current_tetris.getAbsoluteCoords(self.current_direction, self.current_coord[0], self.current_coord[1])
	'''리셋'''
	def reset(self):
		# 기록판 데이터
		self.board_data = [0] * self.width * self.height
		# 현재 테트리스의 회전 상태
		self.current_direction = 0
		# 현재 테트리스의 좌표는 단위 길이가 작은 사각지대의 길이
		self.current_coord = [-1, -1]
		# 다음 테트리스
		self.next_tetris = self.getNextTetris()
		# 현재 테트리스
		self.current_tetris = tetrisShape()
		# 게임 종료여부
		self.is_gameover = False
		# 테트리스의 초기 x 위치
		self.init_x = self.width // 2
		# 형상 수량 통계
		self.shape_statistics = [0] * 8

class ExternalBoard(QFrame):
	score_signal = pyqtSignal(str)
	def __init__(self, parent, grid_size, inner_board):
		super().__init__(parent)
		self.grid_size = grid_size
		self.inner_board = inner_board
		self.setFixedSize(grid_size * inner_board.width, grid_size * inner_board.height)
		self.initExternalBoard()
	
	def initExternalBoard(self):
		self.score = 0
	
	def paintEvent(self, event):
		painter = QPainter(self)
		for x in range(self.inner_board.width):
			for y in range(self.inner_board.height):
				shape = self.inner_board.getCoordValue([x, y])
				drawCell(painter, x * self.grid_size, y * self.grid_size, shape, self.grid_size)
		for x, y in self.inner_board.getCurrentTetrisCoords():
			shape = self.inner_board.current_tetris.shape
			drawCell(painter, x * self.grid_size, y * self.grid_size, shape, self.grid_size)
		painter.setPen(QColor(0x777777))
		painter.drawLine(0, self.height()-1, self.width(), self.height()-1)
		painter.drawLine(self.width()-1, 0, self.width()-1, self.height())
		painter.setPen(QColor(0xCCCCCC))
		painter.drawLine(self.width(), 0, self.width(), self.height())
		painter.drawLine(0, self.height(), self.width(), self.height())
	def updateData(self):
		self.score_signal.emit(str(self.score))
		self.update()


class SidePanel(QFrame):
	def __init__(self, parent, grid_size, inner_board):
		super().__init__(parent)
		self.grid_size = grid_size
		self.inner_board = inner_board
		self.setFixedSize(grid_size * 5, grid_size * inner_board.height)
		self.move(grid_size * inner_board.width, 0)
	
	def paintEvent(self, event):
		painter = QPainter(self)
		x_min, x_max, y_min, y_max = self.inner_board.next_tetris.getRelativeBoundary(0)
		dy = 3 * self.grid_size
		dx = (self.width() - (x_max - x_min) * self.grid_size) / 2
		shape = self.inner_board.next_tetris.shape
		for x, y in self.inner_board.next_tetris.getAbsoluteCoords(0, 0, -y_min):
			drawCell(painter, x * self.grid_size + dx, y * self.grid_size + dy, shape, self.grid_size)
	
	def updateData(self):
		self.update()



def drawCell(painter, x, y, shape, grid_size):
	colors = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC, 0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]
	if shape == 0:
		return
	color = QColor(colors[shape])
	painter.fillRect(x+1, y+1, grid_size-2, grid_size-2, color)
	painter.setPen(color.lighter())
	painter.drawLine(x, y+grid_size-1, x, y)
	painter.drawLine(x, y, x+grid_size-1, y)
	painter.setPen(color.darker())
	painter.drawLine(x+1, y+grid_size-1, x+grid_size-1, y+grid_size-1)
	painter.drawLine(x+grid_size-1, y+grid_size-1, x+grid_size-1, y+1)
