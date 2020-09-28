#==============================================================================#
# maze.py controls maze data, display, generation, and solving. created by     #
# Andy Phan.                                                                   #
#==============================================================================#

import random
from random import randrange, getrandbits
import time
import pygame
import constants
import heapq

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
    """
    Maze constructor that takes in an int width, int height, and screen object of maze
    to create maze information.
    """
    self.reset_maze(width, height, screen)

  #==============================================================================#
  #                            COMMON HELPER METHODS                             #
  #==============================================================================#

  def reset_maze(self, width, height, screen):
    """
    Resets the maze. Takes in int width, int height, and screen object of maze to
    recreate all maze information.
    """
    self.width = width
    self.height = height
    self.total = width * height
    self.start = (0, 0)
    self.end = (self.width-1, self.height-1)
    self.screen = screen
    self.start_x = int(((WINDOW_WIDTH / 3 * 2) - (self.width * (TILE_SIZE + WALL_SIZE)) + WALL_SIZE) / 2)
    self.start_y = int((WINDOW_HEIGHT - (self.height * (TILE_SIZE + WALL_SIZE)) + WALL_SIZE) / 2)
    self.grid = [["UNVISITED" for x in range(width)] for y in range(height)] # stores cell values
    self.path = [[[] for x in range(width)] for y in range(height)] # stores what cell connects with others
    self.solution = []

  def restore_maze(self, solution_only=False):
    """
    Resets all PROCESSED cells to VISITED. If given boolean solution_only is False,
    resets all PATHFIND cells to VISITED as well. Used for solving display.
    """
    for y in range(self.height):
      for x in range(self.width):
        if (x, y) == (0, 0) or (x, y) == (self.width-1, self.height-1):
          self.grid[y][x] = "SPECIAL"
        elif not (solution_only and self.get_grid((x, y)) == "PATHFIND"):
          self.grid[y][x] = "VISITED"

  def draw_maze(self):
    """
    Displays the maze on screen.
    """
    for y in range(self.height):
      for x in range(self.width):
        self.draw_cell((x, y))
        self.draw_walls((x, y))

  def draw_cell(self, cell):
    """
    Displays the given tuple cell on screen.
    """
    x, y = cell
    val = self.get_grid(cell)
    cell_x = self.start_x + (x * (TILE_SIZE + WALL_SIZE))
    cell_y = self.start_y + (y * (TILE_SIZE + WALL_SIZE))
    pygame.draw.rect(self.screen, STAGES[val], (cell_x, cell_y, TILE_SIZE, TILE_SIZE))

  def draw_walls(self, cell):
    """
    Draws the walls of a given tuple cell on screen.
    """
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
      elif neighbor == "SPECIAL" or neighbor == "PATHFIND":
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
    """
    Takes in a given tuple cell and sets its string grid value to val. Draws the cell and waits
    delay ms.
    """
    x, y = cell
    self.grid[y][x] = val
    self.draw_cell(cell)
    self.draw_walls(cell)
    pygame.time.wait(delay)

  def create_all_walls(self):
    """
    Creates and returns a list of all walls in the maze.
    """
    walls = []
    for y in range(self.height):
      for x in range(self.width):
        if x != self.width-1:
          walls.append([(x, y), (x+1, y)])
        if y != self.height-1:
          walls.append([(x, y), (x, y+1)])
    return walls

  def remove_wall(self, walls, u, v):
    """
    Takes in a list of walls and two tuple cells and removes the wall from the list.
    """
    x1, y1 = u
    x2, y2 = v
    walls[y1][x1].remove(v)
    walls[y2][x2].remove(u)

  def find(self, parent, i):
    """
    Finds and returns the parent node of int i in given parent disjoint set.
    """
    while parent[i] >= 0:
      i = parent[i]
    return i

  def union(self, parent, a, b):
    """
    Takes in the parent disjoint set and combines both sets of int nodes a and b.
    """
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
    """
    Takes in the parent disjoint set and returns whether int nodes a and b are in the
    same set.
    """
    return self.find(parent, a) == self.find(parent, b)

  def get_neighbors(self, cell):
    """
    Takes in a tuple cell and returns a list of neighbors of the cell, ignoring walls.
    """
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
    """
    Takes in a tuple cell and returns a list of visited neighbors of the cell, ignoring walls.
    """
    neighbors = filter(lambda neighbor: self.get_grid(neighbor) == "VISITED", self.get_neighbors(cell))
    return list(neighbors)

  def get_unvisited_neighbors(self, cell):
    """
    Takes in a tuple cell and returns a list of unvisited neighbors of the cell, ignoring walls.
    """
    neighbors = filter(lambda neighbor: self.get_grid(neighbor) == "UNVISITED", self.get_neighbors(cell))
    return list(neighbors)

  def connect(self, cell, neighbor):
    """
    Takes in two tuple cells and connects them in the maze.
    """
    x1, y1 = cell
    x2, y2 = neighbor
    self.path[y1][x1].append(neighbor)
    self.path[y2][x2].append(cell)

  def get_grid(self, cell):
    """
    Returns the string grid value of the given tuple cell.
    """
    x, y = cell
    return self.grid[y][x]

  def get_path(self, cell):
    """
    Returns the path list of the given tuple cell.
    """
    x, y = cell
    return self.path[y][x]

  def get_number(self, cell):
    """
    Returns the int number value of the tuple cell.
    """
    x, y = cell
    return (self.width * y) + x

  def is_generated(self):
    for row in self.grid:
      for col in row:
        if col != "VISITED" and col != "SPECIAL" and col != "PATHFIND":
          return False
    return True

  def generate(self, algorithm, delay):
    """
    Acts as the generation manager. Takes in a string algorithm and int delay
    and uses that generation algorithm to create the maze with delay ms.
    """
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

  def solve(self, algorithm, delay):
    """
    Acts as the solution manager. Takes in a string algorithm and int delay
    and uses that solving algorithm to solve the maze with delay ms.
    """
    self.solution = []
    self.restore_maze()
    if algorithm == "DFS":
      self.solve_dfs(delay)
    elif algorithm == "BFS":
      self.solve_bfs(delay)
    elif algorithm == "A*":
      self.solve_a_star(delay)
    self.restore_maze(True)
    return self.solution

  def create_solution(self, parents, cell, delay):
    """
    Helper method for all solution algorithms. Takes in a int array parents that
    stores the previous cell in the path in the current cell. Takes in the final
    tuple cell. Draws all cells with int delay ms. Returns all the cells in the path
    as a list.
    """
    x, y = cell
    while parents[y][x] != cell:
      self.solution.insert(0, cell)
      if self.get_grid(cell) != "SPECIAL":
        self.visit(cell, "PATHFIND", min(delay, 50))
      cell = parents[y][x]
      x, y = cell
      self.solution.insert(0, cell)
    return self.solution

  #==============================================================================#
  #                            GENERATION ALGORITHMS                             #
  #==============================================================================#

  """
  Algorithm:
  1) Pick a random starting cell as current cell.
  2) Pick a random unvisited neighbor cell of that current cell.
  3) Form a path between the two cells and add the neighbor cell to the maze.
  4) Repeat 2-3 with the neighbor cell as the new current cell.
  5) If there are no unvisited neighbor cells, backtrack the current cells
    until there is one.
  6) Complete if current cell is starting cell again.
  """
  def generate_dfs(self, delay):
    """
    Generates a maze using depth-first search with int delay ms.
    """
    stack = [(randrange(self.width), randrange(self.height))]
    while stack:
      top = stack[-1]
      if self.get_grid(top) != "PROCESSED":
        self.visit(top, "PROCESSED", delay)
      neighbors = self.get_unvisited_neighbors(top)
      if neighbors:
        selected = random.choice(neighbors)
        self.connect(top, selected)
        stack.append(selected)
      else:
        stack.pop()
        self.visit(top, "VISITED", delay)

  """
  Algorithm:
  1) Create a list of all walls, and create a disjointed set for each cell
    containing only that cell.
  2) Choose a random wall and remove it from the list.
  3) If the two cells adjacent to that wall are from different sets, remove the
    wall and form a path between the two cells. Add them to the maze.
  4) Repeat 2-3 until all cells are in the same set.
  Note that if the two cells adjacent to the wall are from the same set, it skips
    that wall.
  """
  def generate_kruskal(self, delay):
    """
    Generates a maze using randomized kruskal's algorithm with int delay ms.
    """
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

  """
  Algorithm:
  1) Pick a random starting cell as current cell. Add it to the maze.
  2) For every wall between the current cell and an unvisited neighbor, add the
    wall to the list.
  3) Choose a random wall from the list and remove it. If the seocnd cell has not been
    visited, form a path between the two and add the second cell to the maze.
  4) Set the current cell to the new cell.
  5) Repeat 2-4 until there are no more walls.
  """
  def generate_prim(self, delay):
    """
    Generates a maze using randomized prim's algorithm with int delay ms.
    """
    start = (randrange(self.width), randrange(self.height))
    self.visit(start, "PROCESSED", delay)
    self.visit(start, "VISITED", delay)
    neighbors = self.get_unvisited_neighbors(start)
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
        neighbors = self.get_unvisited_neighbors(selected)
        for neighbor in neighbors:
          walls.append([selected, neighbor])

  """
  Algorithm:
  1) Choose a random starting cell. Add it to the maze.
  2) Choose a random unvisited cell.
  3) Travel in any random direction.
  4) Repeat 3 until either colliding in its own path or with a visited cell.
  5) If collided with its own path, remove the looped path and continue back at 3.
  6) If collided with a visited cell, form a path of all the cells and add them to
    the maze. Repeat 2-5 until maze is fully generated.
  """
  def generate_wilson(self, delay):
    """
    Generates a maze using wilson's algorithm with int delay ms.
    """
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

  """
  Algorithm:
  1) Create the first row. Each cell is in its own disjoint set. Add all of them
    to the maze.
  2) For each cell in the row besides the last, if the cell to the right is not
    in the same disjoint set, randomly decide whether to combine disjoint sets and form
    a path between them. If so, add them to the maze.
  3) For each cell in the row, if it is the parent of the disjoint set, or randomly,
    combine disjoint sets with the cell below and form a path between them. If so,
    add them to the maze.
  4) Repeat 1-3 with rows being added below the previous.
  5) On the final row, repeat 2, except if they are not in the same disjoint set,
    they must form a path between them. Add them to the maze.
  """
  def generate_eller(self, delay):
    """
    Generates a maze using eller's algorithm with int delay ms.
    """
    self.ellers(0, [-1 for i in range(self.total)], delay)

  def ellers(self, row, disjoint_set, delay):
    """
    Helper method for generate_eller. Processes the given int row using int array
    disjoint_set and int delay. Will process all rows.
    """
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
    """
    Helper method for ellers. Processes each cell in given row using int array
    disjoint_set and int delay. Connects cells to the right if they are not in the
    same disjoint set. If is_random is True, then will randomly choose when to
    connect cell to the right.
    """
    for i in range(self.width - 1):
      self.visit((i, row), "VISITED", delay)
      self.visit((i+1, row), "VISITED", 0)
      cell_num = (row * self.width) + i
      rand = getrandbits(1) if is_random else 1
      if rand and not self.is_same_set(disjoint_set, cell_num, cell_num+1):
        self.connect((i, row), (i+1, row))
        self.union(disjoint_set, cell_num, cell_num+1)
        self.visit((i, row), "VISITED", delay)

  """
  Algorithm:
  1) Choose a random starting cell as current cell. Add it to the maze.
  2) Choose a random unvisited neighbor cell of the current cell. Add it to the maze.
  3) Repeat 2 until there is no longer any unvisited neighbor cells.
  4) Scan each row for a cell that has a visited neighbor cell. If so, add it to
    the maze. Set the current cell as that cell.
  5) Repeat 2-4 until maze is fully generated.
  """
  def generate_hunt_and_kill(self, delay):
    """
    Generates a maze using hunt and kill algorithm with int delay ms.
    """
    cell = (randrange(self.width), randrange(self.height))
    self.visit(cell, "VISITED", delay)
    min_row = 0
    while not self.is_generated():
      self.kill(cell, delay)
      cell = self.hunt(min_row, delay)
      min_row = self.hunt_get_min_row(min_row)

  def hunt(self, min_row, delay):
    """
    Scans each row for an unvisited tuple cell that has a visited neighbor tuple cell.
    Returns that unvisited cell.
    """
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
    """
    Takes in a tuple cell and chooses a random unvisited neighbor tuple cell. Marks
    the neighbor cell as visited. Repeats with cell as the new neighbor cell until
    there are no longer any neighbor cells. Draws with int delay ms.
    """
    neighbors = self.get_unvisited_neighbors(cell)
    if neighbors:
      selected = random.choice(neighbors)
      self.connect(cell, selected)
      self.visit(selected, "PROCESSED", delay)
      self.visit(selected, "VISITED", delay)
      self.kill(selected, delay)

  def hunt_get_min_row(self, min_row):
    """
    Optimizing helper for generate_hunt_and_kill. Takes in the minimum int row that
    still might have an unvisited cell and returns the true minimum int row that
    still has an unvisited cell.
    """
    for y in range(min_row, self.height):
      for x in range(self.width):
        if self.get_grid((x, y)) != "VISITED":
          return min_row
      min_row = min_row + 1
    return min_row

  #==============================================================================#
  #                             SOLVING ALGORITHMS                               #
  #==============================================================================#

  """
  Algorithm:
  1) Pick the starting cell as current cell.
  2) Pick a random path cell of that current cell.
  3) Mark the random path cell as processed.
  4) Repeat 2-3 with the neighbor cell as the new current cell.
  5) If there are no visited path cells, backtrack the current cells
    until there is one.
  6) Complete if current cell is the end cell.
  """
  def solve_dfs(self, delay):
    """
    Solves the maze using depth-first search algorithm with int delay ms.
    """
    parents = [[(-1, -1) for x in range(self.width)] for y in range(self.height)]
    stack = [self.start]
    closed = []
    cell = stack[0]
    x, y = cell
    parents[y][x] = cell
    while stack:
      cell = stack[-1]
      if self.get_grid(cell) != "SPECIAL":
        self.visit(cell, "PROCESSED", delay)
      if cell == self.end:
        return self.create_solution(parents, cell, delay)
      closed.append(cell)
      path = self.get_path(cell)
      neighbors = [neighbor for neighbor in path if not neighbor in closed]
      if neighbors:
        selected = random.choice(neighbors)
        x2, y2 = selected
        parents[y2][x2] = cell
        stack.append(selected)
      else:
        stack.pop()
    return self.solution

  """
  Algorithm:
  1) Pick the starting cell as the current cell. Mark it as processed.
  2) Add all path cells of that current cell to a queue.
  3) Set the current cell as the next item in queue. Mark it as processed.
  4) Repeat 2-3 until current cell is the end cell.
  """
  def solve_bfs(self, delay):
    """
    Solves the maze using breadth-first search algorithm with int delay ms.
    """
    parents = [[(-1, -1) for x in range(self.width)] for y in range(self.height)]
    queue = [self.start]
    cell = queue[0]
    x, y = cell
    parents[y][x] = cell
    while queue:
      cell = queue.pop(0)
      if self.get_grid(cell) != "SPECIAL":
        self.visit(cell, "PROCESSED", delay)
      if cell == self.end:
        return self.create_solution(parents, cell, delay)
      else:
        neighbors = self.get_path(cell)
        for neighbor in neighbors:
          x2, y2 = neighbor
          if parents[y2][x2] == (-1, -1):
            parents[y2][x2] = cell
            queue.append(neighbor)
    return self.solution

  """
  1) Pick the starting cell as the current cell.
  2) Calculate the heuristic costs of all path cells of the current cell and add it to
    the heap if the path cell is not in the closed list or in the heap.
  3) Remove the first item from the heap. Set the current cell to it.
    Mark it as processed. Add it to the closed list.
  4) Repeat 2-3 until current cell is the end cell.
  """
  def solve_a_star(self, delay):
    """
    Solves the maze using A* algorithm with int delay ms.
    """
    costs = [[[-1, -1, -1] for x in range(self.width)] for y in range(self.height)]
    parents = [[(-1, -1) for x in range(self.width)] for y in range(self.height)]
    open = []
    closed = []
    cell = self.start
    x, y = cell
    costs[y][x] = self.compute_a_costs(cell)
    parents[y][x] = cell
    heapq.heappush(open, (0, 0, cell))
    while open:
      cell = heapq.heappop(open)[2]
      closed.append(cell)
      if self.get_grid(cell) != "SPECIAL":
        self.visit(cell, "PROCESSED", delay)
      if cell == self.end:
        return self.create_solution(parents, cell, delay)
      neighbors = self.get_path(cell)
      for neighbor in neighbors:
        if not neighbor in closed and not neighbor in open:
          x2, y2 = neighbor
          neighbor_costs = self.compute_a_costs(neighbor)
          costs[y2][x2] = neighbor_costs
          parents[y2][x2] = cell
          if not neighbor in open:
            heapq.heappush(open, (neighbor_costs[2], neighbor_costs[1], neighbor))

  def compute_a_costs(self, cell):
    """
    Helper method for solve_a_star. Takes in a tuple cell and returns the heuristic
    costs of that cell with Manhattan distance from the starting tuple cell and the
    ending tuple cell.
    """
    x, y = cell
    x_start, y_start = self.start
    x_end, y_end = self.end
    g = abs(x_start - x) + abs(y_start - y)
    h = abs(x_end - x) + abs(y_end - y)
    f = g + h
    return [g, h, f]