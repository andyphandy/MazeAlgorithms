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

STAGES = constants.STAGES

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
    self.grid = [["UNVISITED" for x in range(width)] for y in range(height)]
    self.path = [[[] for x in range(width)] for y in range(height)]

  def draw_maze(self):
    for y in range(self.height):
      for x in range(self.width):
        self.draw_cell((x, y))
        self.draw_walls((x, y))

  def draw_cell(self, cell):
    x, y = cell
    val = self.get_grid(cell)
    cell_x = self.start_x + (x * (TILE_SIZE + WALL_SIZE))
    cell_y = self.start_y + (y * (TILE_SIZE + WALL_SIZE))
    pygame.draw.rect(self.screen, STAGES[val], (cell_x, cell_y, TILE_SIZE, TILE_SIZE))

  def draw_walls(self, cell):
    x, y = cell
    cell_x = self.start_x + (x * (TILE_SIZE + WALL_SIZE))
    cell_y = self.start_y + (y * (TILE_SIZE + WALL_SIZE))
    for wall in self.path[y][x]:
      x2, y2 = wall
      neighbor = self.get_grid(wall)
      color = STAGES[neighbor] if neighbor != "SPECIAL" else STAGES["VISITED"]
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
    self.draw_cell(cell)
    self.draw_walls(cell)
    pygame.time.wait(delay)

  def create_walls(self):
    walls = []
    for y in range(self.height):
      for x in range(self.width):
        if x != self.width-1:
          walls.append([(x, y), (x+1, y)])
        if y != self.height-1:
          walls.append([(x, y), (x, y+1)])
    return walls

  def remove_wall(self, walls, u, v):
    x1, y1 = u
    x2, y2 = v
    walls[y1][x1].remove(v)
    walls[y2][x2].remove(u)

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
    if x != 0 and self.get_grid((x-1, y)) == "UNVISITED":
      available.append((x-1, y))
    if x != self.width-1 and self.get_grid((x+1, y)) == "UNVISITED":
      available.append((x+1, y))
    if y != 0 and self.get_grid((x, y-1)) == "UNVISITED":
      available.append((x, y-1))
    if y != self.height-1 and self.get_grid((x, y+1)) == "UNVISITED":
      available.append((x, y+1))
    return available

  def connect(self, cell, neighbor):
    x1, y1 = cell
    x2, y2 = neighbor
    self.path[y1][x1].append(neighbor)
    self.path[y2][x2].append(cell)

  def get_grid(self, cell):
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
      if self.get_grid(top) != "PROCESSED":
        self.visit(top, "PROCESSED", delay)
      neighbors = self.get_available_neighbors(top)
      if neighbors:
        selected = random.choice(neighbors)
        self.connect(top, selected)
        stack.append(selected)
      else:
        stack.pop()
        self.visit(top, "VISITED", delay)

  """
  Generates a maze using randomized kruskal's algorithm:
  1) Create a list of all walls, and create a disjointed set for each cell
      containing only that cell.
  2) Choose a random wall and remove it from the list.
  3) If the two cells adjacent to that wall are from different sets, remove the
      wall and form a path between the two cells. Mark them as visited.
  4) Repeat 2-3 until all cells are in the same set.
  Note that if the two cells adjacent to the wall are from the same set, it skips
    that wall.
  """
  def generate_kruskal(self, delay):
    walls = self.create_walls()
    disjoint_set = [-1 for i in range(self.total)]
    while -self.total not in disjoint_set:
      wall = random.choice(walls)
      walls.remove(wall)
      cell, selected = wall
      cell_num = self.get_number(cell)
      selected_num = self.get_number(selected)
      if not self.is_same_set(disjoint_set, cell_num, selected_num):
        self.union(disjoint_set, cell_num, selected_num)
        self.connect(cell, selected)
        self.visit(cell, "VISITED", delay)
        self.visit(selected, "VISITED", delay)

  def generate_prim(self, delay):
    start = (randrange(self.width), randrange(self.height))
    self.visit(start, "VISITED", delay)
    neighbors = self.get_available_neighbors(start)
    walls = []
    for neighbor in neighbors:
      walls.append([start, neighbor])
    while walls:
      wall = random.choice(walls)
      cell, selected = wall
      walls.remove(wall)
      if self.get_grid(selected) != "VISITED":
        self.connect(cell, selected)
        self.visit(selected, "VISITED", delay)
        neighbors = self.get_available_neighbors(selected)
        for neighbor in neighbors:
          walls.append([selected, neighbor])

  def generate(self, algorithm, delay):
    self.reset_maze(self.width, self.height, self.screen)
    if algorithm == "DFS":
      self.generate_dfs(delay)
    elif algorithm == "Kruskal":
      self.generate_kruskal(delay)
    elif algorithm == "Prim":
      self.generate_prim(delay)
    x1, y1 = self.start
    self.grid[y1][x1] = "SPECIAL"
    x2, y2 = self.end
    self.grid[y2][x2] = "SPECIAL"
    return self.path