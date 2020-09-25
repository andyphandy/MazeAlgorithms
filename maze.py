import random
from random import randrange
from collections import defaultdict
import time
import pygame
import constants

WINDOW_WIDTH = constants.WINDOW_WIDTH
WINDOW_HEIGHT = constants.WINDOW_HEIGHT

TILE_SIZE = constants.TILE_SIZE
WALL_SIZE = constants.WALL_SIZE
MIN_SIZE = constants.MIN_SIZE
MAX_SIZE = constants.MAX_SIZE
ROW_WALL = constants.ROW_WALL
COL_WALL = constants.COL_WALL

DEFAULT_WIDTH = constants.DEFAULT_WIDTH
DEFAULT_HEIGHT = constants.DEFAULT_HEIGHT

BLACK = constants.BLACK
WHITE = constants.WHITE
GREY = constants.GREY
BLUE = constants.BLUE
RED = constants.RED

CELL_COLORS = [GREY, BLUE, WHITE, RED]

class Maze:
  def __init__(self, width, height, screen):
    self.reset_maze(width, height, screen)

  def reset_maze(self, width, height, screen):
    self.width = width
    self.height = height
    self.total = width * height
    self.start = (0, 0)
    self.end = (self.width-1, self.height-1)
    self.screen = screen
    self.start_x = int(((WINDOW_WIDTH / 3 * 2) - (self.width * (TILE_SIZE + WALL_SIZE)) + WALL_SIZE) / 2)
    self.start_y = int((WINDOW_HEIGHT - (self.height * (TILE_SIZE + WALL_SIZE)) + WALL_SIZE) / 2)
    self.grid = [[0 for x in range(width)] for y in range(height)]
    self.path = [[[] for x in range(width)] for y in range(height)]

  def draw_maze(self):
    self.screen.fill(BLACK)
    for y in range(self.height):
      for x in range(self.width):
        self.draw_cell(x, y)
        self.draw_walls(x, y)

  def draw_cell(self, x, y):
    cell = self.grid[y][x]
    cell_x = self.start_x + (x * (TILE_SIZE + WALL_SIZE))
    cell_y = self.start_y + (y * (TILE_SIZE + WALL_SIZE))
    pygame.draw.rect(self.screen, CELL_COLORS[cell], (cell_x, cell_y, TILE_SIZE, TILE_SIZE))

  def draw_walls(self, x, y):
    cell_x = self.start_x + (x * (TILE_SIZE + WALL_SIZE))
    cell_y = self.start_y + (y * (TILE_SIZE + WALL_SIZE))
    for door in self.path[y][x]:
      x2 = door[0]
      y2 = door[1]
      cell2 = self.grid[y2][x2]
      color = CELL_COLORS[cell2] if CELL_COLORS[cell2] != RED else WHITE
      if x2 > x:
        pygame.draw.rect(self.screen, color, ((cell_x + TILE_SIZE, cell_y), ROW_WALL))
      elif x2 < x:
        pygame.draw.rect(self.screen, color, ((cell_x - WALL_SIZE, cell_y), ROW_WALL))
      if y2 > y:
        pygame.draw.rect(self.screen, color, ((cell_x, cell_y + TILE_SIZE), COL_WALL))
      elif y2 < y:
        pygame.draw.rect(self.screen, color, ((cell_x, cell_y - WALL_SIZE), COL_WALL))

  def visit(self, cell, val, delay):
    x, y = cell
    self.grid[y][x] = val
    self.draw_cell(x, y)
    self.draw_walls(x, y)
    pygame.time.wait(delay)

  """
  def create_walls(self):
    walls = [[[] for x in range(self.width)] for y in range(self.height)]
    for y in range(self.height):
      for x in range(self.width):
        curr = walls[y][x]
        if x != 0:
          curr.append((x-1, y))
        if x != self.width-1:
          curr.append((x+1, y))
        if y != 0:
          curr.append((x, y-1))
        if y != self.height-1:
          curr.append((x, y+1))
    return walls
    """
  def create_walls(self):
    walls = {}
    for y in range(self.height):
      for x in range(self.width):
        curr = []
        if x != 0:
          curr.append((x-1, y))
        if x != self.width-1:
          curr.append((x+1, y))
        if y != 0:
          curr.append((x, y-1))
        if y != self.height-1:
          curr.append((x, y+1))
        walls[(x, y)] = curr
    return walls

  def remove_wall(self, walls, u, v):
    walls[u[1]][u[0]].remove(v)
    walls[v[1]][v[0]].remove(u)

  def find(self, parent, i):
    while parent[i] >= 0:
      i = parent[i]
    return i

  def union(self, parent, a, b):
    parent_a = self.find(parent, a)
    weight_a = parent[parent_a]
    parent_b = self.find(parent, b)
    weight_b = parent[parent_b]
    if weight_a < weight_b:
      parent[parent_a] = parent_b
      parent[parent_b] = weight_a + weight_b
    else:
      parent[parent_b] = parent_a
      parent[parent_a] = weight_a + weight_b

  def is_same_set(self, parent, a, b):
    return self.find(parent, a) == self.find(parent, b)

  def get_available_neighbors(self, cell):
    x, y = cell
    available = []
    if x != 0 and self.grid[y][x-1] == 0:
      available.append((x-1, y))
    if x != self.width-1 and self.grid[y][x+1] == 0:
      available.append((x+1, y))
    if y != 0 and self.grid[y-1][x] == 0:
      available.append((x, y-1))
    if y != self.height-1 and self.grid[y+1][x] == 0:
      available.append((x, y+1))
    return available

  def connect(self, cell, neighbor):
    x1, y1 = cell
    x2, y2 = neighbor
    self.path[y1][x1].append(neighbor)
    self.path[y2][x2].append(cell)

  def get_cell(self, cell):
    x, y = cell
    return self.grid[y][x]

  def get_number(self, cell):
    x, y = cell
    return (self.width * y) + x

  """
  Generates a maze using randomized depth-first search:
  1) Pick a random current cell as starting cell.
  2) Pick a random unvisited neighbor cell of that current cell.
  3) Form a path between the two cells and mark the neighbor cell as visited.
  4) Repeat 2-3 with the neighbor cell as the new current cell.
  5) If there are no unvisited neighbor cells, backtrack the current cells
      until there is one.
  6) Complete if current cell is starting cell again.
  """
  def generate_dfs(self, delay):
    stack = [(randrange(self.width), randrange(self.height))]
    while stack:
      top = stack[-1]
      if self.get_cell(top) != 1:
        self.visit(top, 1, delay)
      neighbors = self.get_available_neighbors(top)
      if neighbors:
        selected = random.choice(neighbors)
        self.connect(top, selected)
        stack.append(selected)
      else:
        stack.pop()
        self.visit(top, 2, delay)

  def generate_kruskal(self, delay):
    walls = self.create_walls()
    disjoint_set = [-1 for i in range(self.total)]
    while -self.total not in disjoint_set:
      cell, neighbors = random.choice(list(walls.items()))
      if self.get_cell(cell) != 2:
        self.visit(cell, 2, delay)
      selected = random.choice(neighbors)
      neighbors.remove(selected)
      if not neighbors:
        walls.pop(cell)
      cell_num = self.get_number(cell)
      selected_num = self.get_number(selected)
      if not self.is_same_set(disjoint_set, cell_num, selected_num):
        self.union(disjoint_set, cell_num, selected_num)
        self.connect(cell, selected)
        self.visit(selected, 2, delay)

  def generate(self, algorithm, delay):
    self.reset_maze(self.width, self.height, self.screen)
    if algorithm == "DFS":
      self.generate_dfs(delay)
    elif algorithm == "Kruskal":
      self.generate_kruskal(delay)
    x1, y1 = self.start
    self.grid[y1][x1] = 3
    x2, y2 = self.end
    self.grid[y2][x2] = 3
    return self.path