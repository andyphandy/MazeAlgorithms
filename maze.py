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

  def animate(self, x, y, delay):
    self.draw_cell(x, y)
    self.draw_walls(x, y)
    pygame.time.wait(delay)

  def create_walls(self):
    walls = [[[] for x in range(self.width)] for y in range(self.height)]
    for y in range(self.height):
      for x in range(self.width):
        curr = walls[y][x]
        if x != 0:
          curr.append((x-1, y))
        if x != self.width-1
          curr.append((x+1, y))
        if y != 0:
          curr.append((x, y-1))
        if y != self.height-1:
          curr.append((x, y+1))
    return walls

  def remove_wall(self, walls, ux, uy, vx, vy):
    walls[uy][ux].remove((vx, vy))
    walls[vy][vx].remove((ux, uy))

  def get_available_neighbors(self, x, y):
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
      x1 = top[0]
      y1 = top[1]
      if self.grid[y1][x1] != 1:
        self.grid[y1][x1] = 1
        self.animate(x1, y1, delay)
      neighbors = self.get_available_neighbors(x1, y1)
      if neighbors:
        selected = neighbors[randrange(len(neighbors))]
        x2 = selected[0]
        y2 = selected[1]
        self.path[y1][x1].append(selected)
        self.path[y2][x2].append(top)
        stack.append(selected)
      else:
        stack.pop()
        self.grid[y1][x1] = 2
        self.animate(x1, y1, delay)

  def generate_kruskal(self, delay):
    walls = create_walls()
    disjoint_set = [-1 for i in range]

  def generate(self, algorithm, delay):
    self.reset_maze(self.width, self.height, self.screen)
    if algorithm == "DFS":
      self.generate_dfs(delay)
    elif algorithm == "Kruskal":
      print('sike')
    self.grid[0][0] = 3
    self.grid[self.height-1][self.width-1] = 3
    return self.path