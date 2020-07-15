from random import randrange, getrandbits
from collections import defaultdict
import timeit

class Maze:
  ##############################################################################
  #                               HELPER METHODS                               #
  ##############################################################################

  def create_walls(self):
    self.walls = []
    for cell in range(self.total):
      x = int(cell % self.width)
      y = int(cell / self.width)
      cellWalls = []
      if x != 0:
        cellWalls.append(cell-1)
      if x != width-1:
        cellWalls.append(cell+1)
      if y != 0:
        cellWalls.append(cell-width)
      if y != height-1:
        cellWalls.append(cell+width)
      self.walls.append(cellWalls)

  def remove_wall(self, u, v):
    self.walls[u].remove(v)
    self.walls[v].remove(u)

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
    available = []
    x = int(cell % self.width)
    y = int(cell / self.width)
    if x != 0 and not self.visited[cell-1]:
      available.append(cell-1)
    if x != width-1 and not self.visited[cell+1]:
      available.append(cell+1)
    if y != 0 and not self.visited[cell-width]:
      available.append(cell - width)
    if y != height-1 and not self.visited[cell+width]:
      available.append(cell + width)
    return available

  def get_visited_neighbors(self, cell):
    taken = []
    x = int(cell % self.width)
    y = int(cell / self.width)
    if x != 0 and self.visited[cell-1]:
      taken.append(cell-1)
    if x != width-1 and self.visited[cell+1]:
      taken.append(cell+1)
    if y != 0 and self.visited[cell-width]:
      taken.append(cell - width)
    if y != height-1 and self.visited[cell+width]:
      taken.append(cell + width)
    return taken

  def get_neighbors(self, cell):
    neighbors = []
    x = int(cell % self.width)
    y = int(cell / self.width)
    if x != 0:
      neighbors.append(cell-1)
    if x != width-1:
      neighbors.append(cell+1)
    if y != 0:
      neighbors.append(cell - width)
    if y != height-1:
      neighbors.append(cell + width)
    return neighbors
  ##############################################################################

  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.total = width * height
    self.path = [[] for i in range(self.total)]
    self.start = 0
    self.end = self.total - 1
    self.visited = [False for i in range(self.total)]

  def generate_dfs(self):
    stack = [randrange(self.total)]
    while stack:
      top = stack[-1]
      self.visited[top] = True
      neighbors = self.get_available_neighbors(top)
      if neighbors:
        selected = neighbors[randrange(len(neighbors))]
        self.path[selected].append(top)
        self.path[top].append(selected)
        stack.append(selected)
      else:
        stack.pop()
    return self.path

  def generate_kruskal(self):
    self.create_walls()
    disjoint_set = [-1 for i in range(self.total)]
    cell_indexes = [i for i in range(len(self.walls))]
    while -self.total not in disjoint_set:
      rand_cell = cell_indexes[randrange(len(cell_indexes))]
      rand_wall_index = randrange(len(self.walls[rand_cell]))
      neighbor = self.walls[rand_cell][rand_wall_index]
      if not self.is_same_set(disjoint_set, rand_cell, neighbor):
        self.remove_wall(rand_cell, neighbor)
        self.union(disjoint_set, rand_cell, neighbor)
        self.path[rand_cell].append(neighbor)
        self.path[neighbor].append(rand_cell)
        if len(self.walls[rand_cell]) == 0:
          cell_indexes.remove(rand_cell)
        if len(self.walls[neighbor]) == 0:
          cell_indexes.remove(neighbor)
    return self.path

  def generate_prim(self):
    start = randrange(self.total)
    self.visited[start] = True
    adjacent = self.get_available_neighbors(start)
    while adjacent:
      next = adjacent[randrange(len(adjacent))]
      adjacent.remove(next)
      self.visited[next] = True
      visited_neighbors = self.get_visited_neighbors(next)
      connector = visited_neighbors[randrange(len(visited_neighbors))]
      self.path[next].append(connector)
      self.path[connector].append(next)
      for available in self.get_available_neighbors(next):
        if available not in adjacent:
          adjacent.append(available)
    return self.path

  def generate_wilson(self):
    start = randrange(self.total)
    self.visited[start] = True
    while False in self.visited:
      stack = []
      current = randrange(self.total)
      while self.visited[current]:
        current = randrange(self.total)
      stack.append(current)
      while stack and not self.visited[stack[-1]]:
        neighbors = self.get_neighbors(current)
        current = neighbors[randrange(len(neighbors))]
        if current in stack:
          while current in stack:
            stack.pop()
          if stack:
            current = stack[-1]
        else:
          stack.append(current)
      while len(stack) > 1:
        current = stack[-1]
        stack.pop()
        next = stack[-1]
        self.visited[current] = True
        self.visited[next] = True
        self.path[current].append(next)
        self.path[next].append(current)
    return self.path

  def generate_eller(self):
    self.ellers(0, [-1 for i in range(self.total)])
    return self.path

  def ellers(self, row, disjoint_set):
    if row == self.height-1:
      for i in range(self.width-1):
        cell = (row * self.width) + i
        if not self.is_same_set(disjoint_set, cell, cell+1):
          self.path[cell].append(cell+1)
          self.path[cell+1].append(cell)
          self.union(disjoint_set, cell, cell+1)
    elif row < self.height-1:
      for i in range(self.width-1):
        cell = (row * self.width) + i
        if bool(getrandbits(1)) and not self.is_same_set(disjoint_set, cell, cell+1):
          self.union(disjoint_set, cell, cell+1)
          self.path[cell].append(cell+1)
          self.path[cell+1].append(cell)
      for i in range(self.width):
        cell = (row * self.width) + i
        cell_set = disjoint_set[cell]
        if cell_set < 0 or bool(getrandbits(1)):
          self.union(disjoint_set, cell+width, cell)
          self.path[cell].append(cell+self.width)
          self.path[cell+self.width].append(cell)
      self.ellers(row+1, disjoint_set)

  def generate_hunt_kill(self):
    current = randrange(self.total)
    self.visited[current] = True
    while current != -1:
      neighbors = self.get_available_neighbors(current)
      self.kill(current, neighbors)
      current = self.hunt()
    return self.path

  def hunt(self):
    cell = 0
    while cell < self.total:
      visited_neighbors = self.get_visited_neighbors(cell)
      if not self.visited[cell] and visited_neighbors:
        selected_neighbor = visited_neighbors[randrange(len(visited_neighbors))]
        self.path[selected_neighbor].append(cell)
        self.path[cell].append(selected_neighbor)
        self.visited[cell] = True
        return cell
      cell += 1
    return -1

  def kill(self, current, neighbors):
    if neighbors:
      next = neighbors[randrange(len(neighbors))]
      self.path[current].append(next)
      self.path[next].append(current)
      self.visited[next] = True
      current = next
      neighbors = self.get_available_neighbors(current)
      self.kill(current, neighbors)

  def solve_bfs(self):
    self.solution = []
    parents = [-1 for i in range(self.total)]
    queue = [self.start]
    current = queue[0]
    parents[current] = current
    while queue:
      current = queue.pop(0)
      neighbors = self.path[current]
      if current == self.end:
        while parents[current] != current:
          self.solution.insert(0, current)
          current = parents[current]
        self.solution.insert(0, current)
        return self.solution
      for cell in neighbors:
        if parents[cell] == -1:
          parents[cell] = current
          queue.append(cell)
    return self.solution

  def reset_maze(self):
    self.path = [[] for i in range(self.total)]
    self.solution = []
    self.visited = [False for i in range(self.total)]

  def set_dimensions(self, width, height):
    self.width = width
    self.height = height
    self.total = width * height
    self.reset_maze()

  def to_string(self):
    return self.to_string_with_solution(False)

  def to_string_with_solution(self, is_solution):
    vert = [["|  "] * self.width + ["|"] for i in range(self.height)] + [[]]
    horz = [["+--"] * self.width + ["+"] for i in range(self.height+1)]
    for current in range(self.total):
      path = self.path[current]
      x = int(current % self.width)
      y = int(current / self.width)
      if is_solution and current in self.solution:
        vert[y][x] = vert[y][x][0] + "[]"
      if current+1 in path:
        vert[y][x+1] = "   "
      if current+self.width in path:
        horz[y+1][x] = "+  "
    maze = ""
    for (a, b) in zip(horz, vert):
        maze += ''.join(a + ['\n'] + b + ['\n'])
    return maze

#width = int(input("Enter a width: "))
#height = int(input("Enter a height: "))
width = 25
height = 25
obj = Maze(width, height)
#print("DFS")
#print(timeit.timeit(obj.generate_dfs, number=1))
#obj.reset_maze()
#print("Kruskal")
#print(timeit.timeit(obj.generate_kruskal, number=1))
#obj.reset_maze()
#print("Prim")
#print(timeit.timeit(obj.generate_prim, number=1))
#obj.reset_maze()
#print("Wilson")
#print(timeit.timeit(obj.generate_wilson, number=1))
obj.generate_wilson()
obj.solve_bfs()
print(obj.to_string())
print(obj.to_string_with_solution(True))