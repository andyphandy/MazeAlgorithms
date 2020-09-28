#==============================================================================#
# constants.py stores all constants used in main.py and maze.py. created by    #
# Andy Phan.                                                                   #
#==============================================================================#

WINDOW_WIDTH = 1366
WINDOW_HEIGHT = 912
FPS = 60

GUI_X = int(WINDOW_WIDTH * 2 / 3)
GUI_Y = 0
GUI_X_CENTER = int(GUI_X + (WINDOW_WIDTH / 6))
SLIDER_SIZE = (200, 20)
SLIDER_X = int(GUI_X + ((WINDOW_WIDTH - GUI_X) / 2) - (SLIDER_SIZE[0] / 2))

TILE_SIZE = 10
WALL_SIZE = 5
MIN_SIZE = 2
MAX_SIZE = 60
ROW_WALL = (WALL_SIZE, TILE_SIZE)
COL_WALL = (TILE_SIZE, WALL_SIZE)

DEFAULT_WIDTH = 10
DEFAULT_HEIGHT = 10

MIN_DELAY = 0
MAX_DELAY = 500
DEFAULT_DELAY = 50

BLACK = (0, 0, 0)
WHITE = (255,255,255)
GREY = (33, 40, 45)
BLUE = (0, 204, 204)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

GEN_ALGORITHMS = ["DFS", "Kruskal", "Prim", "Wilson", "Eller", "Hunt and Kill"]
SOL_ALGORITHMS = ["DFS", "BFS", "A*"]

STAGES = {
  "UNVISITED": GREY,
  "PROCESSED": BLUE,
  "VISITED": WHITE,
  "SPECIAL": RED,
  "PATHFIND": GREEN
}