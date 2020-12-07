import copy
import math
from modules.utils import *


class TetrisAI():
	def __init__(self, inner_board):
		self.inner_board = inner_board
	
	def getNextAction(self):
		if self.inner_board.current_tetris == tetrisShape().shape_empty:
			return None
		action = None
		# 현재 조작이 가능한 테트리스의direction범위
		if self.inner_board.current_tetris.shape in [tetrisShape().shape_O]:
			current_direction_range = [0]
		elif self.inner_board.current_tetris.shape in [tetrisShape().shape_I, tetrisShape().shape_Z, tetrisShape().shape_S]:
			current_direction_range = [0, 1]
		else:
			current_direction_range = [0, 1, 2, 3]
		# 다음 조작이 가능한 테트리스의direction범위
		if self.inner_board.next_tetris.shape in [tetrisShape().shape_O]:
			next_direction_range = [0]
		elif self.inner_board.next_tetris.shape in [tetrisShape().shape_I, tetrisShape().shape_Z, tetrisShape().shape_S]:
			next_direction_range = [0, 1]
		else:
			next_direction_range = [0, 1, 2, 3]
		# 간단한 AI 알고리즘
		for d_now in current_direction_range:
			x_now_min, x_now_max, y_now_min, y_now_max = self.inner_board.current_tetris.getRelativeBoundary(d_now)
			for x_now in range(-x_now_min, self.inner_board.width - x_now_max):
				board = self.getFinalBoardData(d_now, x_now)
				for d_next in next_direction_range:
					x_next_min, x_next_max, y_next_min, y_next_max = self.inner_board.next_tetris.getRelativeBoundary(d_next)
					distances = self.getDropDistances(board, d_next, range(-x_next_min, self.inner_board.width-x_next_max))
					for x_next in range(-x_next_min, self.inner_board.width-x_next_max):
						score = self.calcScore(copy.deepcopy(board), d_next, x_next, distances)
						if not action or action[2] < score:
							action = [d_now, x_now, score]
		return action
	'''현재 테트리스가 어느 위치에서 어느 방향으로 최저점까지 떨어질 때의 판 데이터를 획득'''
	def getFinalBoardData(self, d_now, x_now):
		board = copy.deepcopy(self.inner_board.getBoardData())
		dy = self.inner_board.height - 1
		for x, y in self.inner_board.current_tetris.getAbsoluteCoords(d_now, x_now, 0):
			count = 0
			while (count + y < self.inner_board.height) and (count + y < 0 or board[x + (count + y) * self.inner_board.width] == tetrisShape().shape_empty):
				count += 1
			count -= 1
			if dy > count:
				dy = count
		return self.imitateDropDown(board, self.inner_board.current_tetris, d_now, x_now, dy)
	'''최저점까지 내려가서 판 데이터를 얻는 시뮬레이션'''
	def imitateDropDown(self, board, tetris, direction, x_imitate, dy):
		for x, y in tetris.getAbsoluteCoords(direction, x_imitate, 0):
			board[x + (y + dy) * self.inner_board.width] = tetris.shape
		return board
	'''다음 테트리스 x_range범위 내의 상태는 테트리스에서 최저점까지의 거리'''
	def getDropDistances(self, board, direction, x_range):
		dists = {}
		for x_next in x_range:
			if x_next not in dists:
				dists[x_next] = self.inner_board.height - 1
			for x, y in self.inner_board.next_tetris.getAbsoluteCoords(direction, x_next, 0):
				count = 0
				while (count + y < self.inner_board.height) and (count + y < 0 or board[x + (count + y) * self.inner_board.width] == tetrisShape().shape_empty):
					count += 1
				count -= 1
				if dists[x_next] > count:
					dists[x_next] = count
		return dists
	'''방안의 점수를 계산'''
	def calcScore(self, board, d_next, x_next, distances):
		# 다음의 테트리스는 어떤 방식으로든 시뮬레이션으로 하부에 도달
		board = self.imitateDropDown(board, self.inner_board.next_tetris, d_next, x_next, distances[x_next])
		width, height = self.inner_board.width, self.inner_board.height
		# 다음 테트리스 (해소 가능한 행수)
		removed_lines = 0
		# 공석통계
		hole_statistic_0 = [0] * width
		hole_statistic_1 = [0] * width
		# 블록 수량
		num_blocks = 0
		# 공석수량
		num_holes = 0
		# x자리마다 테트리스 최고점
		roof_y = [0] * width
		for y in range(height-1, -1, -1):
			# 빈자리 있는지
			has_hole = False
			# 블록 있는지
			has_block = False
			for x in range(width):
				if board[x + y * width] == tetrisShape().shape_empty:
					has_hole = True
					hole_statistic_0[x] += 1
				else:
					has_block = True
					roof_y[x] = height - y
					if hole_statistic_0[x] > 0:
						hole_statistic_1[x] += hole_statistic_0[x]
						hole_statistic_0[x] = 0
					if hole_statistic_1[x] > 0:
						num_blocks += 1
			if not has_block:
				break
			if not has_hole and has_block:
				removed_lines += 1
		# 데이터^0.7의 합
		num_holes = sum([i ** .7 for i in hole_statistic_1])
		# 최고점
		max_height = max(roof_y) - removed_lines
		# roof_y차분산
		roof_dy = [roof_y[i]-roof_y[i+1] for i in range(len(roof_y)-1)]
		# 표준편차 계산 E(x^2) - E(x)^2
		if len(roof_y) <= 0:
			roof_y_std = 0
		else:
			roof_y_std = math.sqrt(sum([y**2 for y in roof_y]) / len(roof_y) - (sum(roof_y) / len(roof_y)) ** 2)
		if len(roof_dy) <= 0:
			roof_dy_std = 0
		else:
			roof_dy_std = math.sqrt(sum([dy**2 for dy in roof_dy]) / len(roof_dy) - (sum(roof_dy) / len(roof_dy)) ** 2)
		# roof_dy절대값이의 합
		abs_dy = sum([abs(dy) for dy in roof_dy])
		# 최대값과 최소값의 차이
		max_dy = max(roof_y) - min(roof_y)
		# 점수 계산
		score = removed_lines * 1.8 - num_holes * 1.0 - num_blocks * 0.5 - max_height ** 1.5 * 0.02 - roof_y_std * 1e-5 - roof_dy_std * 0.01 - abs_dy * 0.2 - max_dy * 0.3
		return score
