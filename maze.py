import random
from random import randrange, getrandbits
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
    self.solution = []

  def restore_maze(self, solution_only=False):
    for y in range(self.height):
      for x in range(self.width):
        if (x, y) == (0, 0) or (x, y) == (self.width-1, self.height-1):
          self.grid[y][x] = "SPECIAL"
        elif not (solution_only and self.get_grid((x, y)) == "PATHFIND"):
          self.grid[y][x] = "VISITED"

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
      curr = self.get_grid(cell)
      neighbor = self.get_grid(wall)
      color = STAGES[neighbor]
      if curr == "SPECIAL" or curr == "PATHFIND":
        if neighbor == "SPECIAL" or neighbor == "PATHFIND":
          color = STAGES["PATHFIND"]
      elif neighbor == "SPECIAL":
        color = STAGES[curr]
      elif neighbor == "PATHFIND":
        color = STAGES[curr]
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

  def create_all_walls(self):
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

  def get_neighbors(self, cell):
    x, y = cell
    neighbors = []
    if x != 0:
      neighbors.append((x-1, y))
    if x != self.width-1:
      neighbors.append((x+1, y))
    if y != 0:
      neighbors.append((x, y-1))
    if y != self.height-1:
      neighbors.append((x, y+1))
    return neighbors

  def get_visited_neighbors(self, cell):
    x, y = cell
    visited = []
    if x != 0 and self.get_grid((x-1, y)) == "VISITED":
      visited.append((x-1, y))
    if x != self.width-1 and self.get_grid((x+1, y)) == "VISITED":
      visited.append((x+1, y))
    if y != 0 and self.get_grid((x, y-1)) == "VISITED":
      visited.append((x, y-1))
    if y != self.height-1 and self.get_grid((x, y+1)) == "VISITED":
      visited.append((x, y+1))
    return visited

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

  def is_generated(self):
    for row in self.grid:
      for col in row:
        if col != "VISITED" and col != "SPECIAL" and col != "PATHFIND":
          return False
    return True

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
    walls = self.create_all_walls()
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
        self.visit(cell, "PROCESSED", delay)
        self.visit(cell, "VISITED", 0)
        self.visit(selected, "VISITED", delay)

  def generate_prim(self, delay):
    start = (randrange(self.width), randrange(self.height))
    self.visit(start, "PROCESSED", delay)
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
        self.visit(selected, "PROCESSED", delay)
        self.visit(selected, "VISITED", 0)
        neighbors = self.get_available_neighbors(selected)
        for neighbor in neighbors:
          walls.append([selected, neighbor])

  def generate_wilson(self, delay):
    self.visit((randrange(self.width), randrange(self.height)), "VISITED", delay)
    while not self.is_generated():
      stack = []
      start = (randrange(self.width), randrange(self.height))
      while self.get_grid(start) != "UNVISITED":
        start = (randrange(self.width), randrange(self.height))
      stack.append(start)
      self.visit(start, "PROCESSED", delay)
      while stack and self.get_grid(stack[-1]) != "VISITED":
        top = stack[-1]
        neighbors = self.get_neighbors(top)
        selected = random.choice(neighbors)
        if self.get_grid(selected) != "VISITED":
          self.visit(selected, "PROCESSED", delay)
        if selected in stack:
          while selected in stack and len(stack) > 1:
            self.visit(stack.pop(), "UNVISITED", 0)
        else:
          stack.append(selected)
      while len(stack) > 1:
        top = stack.pop()
        next = stack[-1]
        self.connect(top, next)
        self.visit(next, "VISITED", delay)

  def generate_eller(self, delay):
    self.ellers(0, [-1 for i in range(self.total)], delay)

  def ellers(self, row, disjoint_set, delay):
    if row == self.height - 1:
      self.ellers_row_operation(row, disjoint_set, delay)
    elif row < self.height - 1:
      self.ellers_row_operation(row, disjoint_set, delay, True)
      for i in range(self.width):
        cell_num = (row * self.width) + i
        cell_set = disjoint_set[cell_num]
        if cell_set < 0 or getrandbits(1):
          self.union(disjoint_set, cell_num + self.width, cell_num)
          self.connect((i, row), (i, row+1))
        self.visit((i, row+1), "PROCESSED", delay)
      self.ellers(row+1, disjoint_set, delay)

  def ellers_row_operation(self, row, disjoint_set, delay, is_random=False):
    for i in range(self.width - 1):
      self.visit((i, row), "VISITED", delay)
      self.visit((i+1, row), "VISITED", 0)
      cell_num = (row * self.width) + i
      rand = getrandbits(1) if is_random else 1
      if rand and not self.is_same_set(disjoint_set, cell_num, cell_num+1):
        self.connect((i, row), (i+1, row))
        self.union(disjoint_set, cell_num, cell_num+1)
        self.visit((i, row), "VISITED", delay)

  def generate_hunt_and_kill(self, delay):
    cell = (randrange(self.width), randrange(self.height))
    self.visit(cell, "VISITED", delay)
    min_row = 0
    while not self.is_generated():
      self.kill(cell, delay)
      cell = self.hunt(min_row, delay)
      min_row = self.hunt_get_min_row(min_row)

  def hunt(self, min_row, delay):
    for y in range(min_row, self.height):
      for x in range(self.width):
        cell = (x, y)
        prev_state = self.get_grid(cell)
        self.visit(cell, "PROCESSED", delay)
        visited_neighbors = self.get_visited_neighbors(cell)
        if prev_state != "VISITED" and visited_neighbors:
          selected = random.choice(visited_neighbors)
          self.connect(cell, selected)
          self.visit(cell, "VISITED", delay)
          return cell
        else:
          self.visit(cell, prev_state, delay)
    return (0, 0)

  def kill(self, cell, delay):
    neighbors = self.get_available_neighbors(cell)
    if neighbors:
      selected = random.choice(neighbors)
      self.connect(cell, selected)
      self.visit(selected, "PROCESSED", delay)
      self.visit(selected, "VISITED", delay)
      self.kill(selected, delay)

  def hunt_get_min_row(self, min_row):
    for y in range(min_row, self.height):
      for x in range(self.width):
        if self.get_grid((x, y)) != "VISITED":
          return min_row
      min_row = min_row + 1
    return min_row

  def generate(self, algorithm, delay):
    self.reset_maze(self.width, self.height, self.screen)
    if algorithm == "DFS":
      self.generate_dfs(delay)
    elif algorithm == "Kruskal":
      self.generate_kruskal(delay)
    elif algorithm == "Prim":
      self.generate_prim(delay)
    elif algorithm == "Wilson":
      self.generate_wilson(delay)
    elif algorithm == "Eller":
      self.generate_eller(delay)
    elif algorithm == "Hunt and Kill":
      self.generate_hunt_and_kill(delay)
    x1, y1 = self.start
    self.grid[y1][x1] = "SPECIAL"
    x2, y2 = self.end
    self.grid[y2][x2] = "SPECIAL"
    return self.path

  def solve_bfs(self, delay):
    parents = [[(-1, -1) for x in range(self.width)] for y in range(self.height)]
    queue = [self.start]
    cell = queue[0]
    x, y = cell
    parents[y][x] = cell
    while queue:
      cell = queue.pop(0)
      if self.get_grid(cell) != "SPECIAL":
        self.visit(cell, "PROCESSED", int(delay / max(len(queue), 1)))
      x, y = cell
      if cell == self.end:
        while parents[y][x] != cell:
          self.solution.insert(0, cell)
          if self.get_grid(cell) != "SPECIAL":
            self.visit(cell, "PATHFIND", min(delay, 50))
          cell = parents[y][x]
          x, y = cell
        self.solution.insert(0, cell)
        return self.solution
      else:
        neighbors = self.path[y][x]
        for neighbor in neighbors:
          x2, y2 = neighbor
          if parents[y2][x2] == (-1, -1):
            parents[y2][x2] = cell
            queue.append(neighbor)
    return self.solution

  def solve(self, algorithm, delay):
    self.solution = []
    self.restore_maze()
    if algorithm == "BFS":
      self.solve_bfs(delay)
    self.restore_maze(True)
    return self.path