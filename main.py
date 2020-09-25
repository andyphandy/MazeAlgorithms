import pygame
import pygame_gui
import constants
from maze import Maze
from threading import Thread

def main():
  pygame.init()
  clock = pygame.time.Clock()
  running = True

  FPS = constants.FPS
  WINDOW_WIDTH = constants.WINDOW_WIDTH
  WINDOW_HEIGHT = constants.WINDOW_HEIGHT

  GUI_X = constants.GUI_X
  GUI_Y = constants.GUI_Y
  GUI_X_CENTER = constants.GUI_X_CENTER
  SLIDER_SIZE = constants.SLIDER_SIZE
  SLIDER_X = GUI_X_CENTER - int (SLIDER_SIZE[0] / 2)

  TILE_SIZE = constants.TILE_SIZE
  WALL_SIZE = constants.WALL_SIZE
  MIN_SIZE = constants.MIN_SIZE
  MAX_SIZE = constants.MAX_SIZE
  ROW_WALL = constants.ROW_WALL
  COL_WALL = constants.COL_WALL

  DEFAULT_WIDTH = constants.DEFAULT_WIDTH
  DEFAULT_HEIGHT = constants.DEFAULT_HEIGHT

  MIN_DELAY = constants.MIN_DELAY
  MAX_DELAY = constants.MAX_DELAY
  DEFAULT_DELAY = constants.DEFAULT_DELAY

  GEN_ALGORITHMS = constants.GEN_ALGORITHMS

  BLACK = constants.BLACK
  WHITE = constants.WHITE
  GREY = constants.GREY

  screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
  pygame.display.set_caption("MazeAlgorithms by Andy Phan")

  # GUI
  manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))

  gui = (GUI_X, GUI_Y, int(WINDOW_WIDTH / 3), WINDOW_HEIGHT)

  font = pygame.font.Font('freesansbold.ttf', 32)
  text = font.render("MazeAlgorithms", True, WHITE)
  text_rect = text.get_rect()
  text_rect.center = (GUI_X_CENTER, 50)

  animation_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((SLIDER_X, 100), SLIDER_SIZE),
                                                text="Animation delay: " + str(DEFAULT_DELAY) + " ms",
                                                manager=manager)
  animation_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((SLIDER_X, 120), SLIDER_SIZE),
                                                            start_value=DEFAULT_DELAY,
                                                            value_range=(MIN_DELAY, MAX_DELAY),
                                                            manager=manager)
  width_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((SLIDER_X, 150), SLIDER_SIZE),
                                            text="Width: " + str(DEFAULT_WIDTH),
                                            manager=manager)
  width_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((SLIDER_X, 170), SLIDER_SIZE),
                                                        start_value=DEFAULT_WIDTH,
                                                        value_range=(MIN_SIZE, MAX_SIZE),
                                                        manager=manager)
  height_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((SLIDER_X, 200), SLIDER_SIZE),
                                            text="Height: " + str(DEFAULT_HEIGHT),
                                            manager=manager)
  height_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((SLIDER_X, 220), SLIDER_SIZE),
                                                         start_value=DEFAULT_HEIGHT,
                                                         value_range=(MIN_SIZE, MAX_SIZE),
                                                         manager=manager)
  generation_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((SLIDER_X, 260), SLIDER_SIZE),
                                                 text="Generation Algorithm",
                                                 manager=manager)
  generation_menu = pygame_gui.elements.UIDropDownMenu(relative_rect=pygame.Rect((SLIDER_X, 280), SLIDER_SIZE),
                                                       options_list=GEN_ALGORITHMS,
                                                       starting_option=GEN_ALGORITHMS[0],
                                                       manager=manager)
  generate_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(GUI_X_CENTER - 50, 320, 100, 50),
                                                 text='Generate',
                                                 manager=manager)


  threads = []

  maze = Maze(DEFAULT_WIDTH, DEFAULT_HEIGHT, screen)

  screen.fill(BLACK)
  maze.draw_maze()

  def animation_slider_event(maze):
    delay = animation_slider.get_current_value()
    animation_label.set_text("Animation delay: " + str(delay) + " ms")

  def size_slider_event(isWidth):
    width = width_slider.get_current_value()
    height = height_slider.get_current_value()
    if isWidth:
      width_label.set_text("Width: " + str(width))
    else:
      height_label.set_text("Height: " + str(height))
    if maze.width != width or maze.height != height:
      maze.reset_maze(width, height, screen)
      screen.fill(BLACK)
      maze.draw_maze()

  def generate_button_event():
    disable_ui()
    algorithm = generation_menu.selected_option
    delay = animation_slider.get_current_value()
    thread = Thread(target=maze.generate, args=(algorithm, delay), kwargs={})
    thread.daemon = True
    threads.append(thread)
    thread.start()

  def disable_ui():
    width_slider.disable()
    height_slider.disable()
    generate_button.disable()
    animation_slider.disable()
    generation_menu.disable()

  def enable_ui():
    width_slider.enable()
    height_slider.enable()
    generate_button.enable()
    animation_slider.enable()
    generation_menu.enable()

  def gui_event(event):
    if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
      if event.ui_element == generate_button:
        generate_button_event()
    elif event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
      if event.ui_element == width_slider:
        size_slider_event(True)
      elif event.ui_element == height_slider:
        size_slider_event(False)
      elif event.ui_element == animation_slider:
        animation_slider_event(maze)

  def draw_default():
    screen.fill(BLACK)
    maze.draw_maze()
    pygame.draw.rect(screen, GREY, gui)
    screen.blit(text, text_rect)
    manager.draw_ui(screen)

  while running:
    time_delta = clock.tick(FPS)/1000.0
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
      elif event.type == pygame.USEREVENT:
        gui_event(event)
      manager.process_events(event)
    manager.update(time_delta)
    if threads and not threads[0].is_alive():
      enable_ui()
      threads.pop()
    draw_default()
    pygame.display.update()

if __name__ == "__main__":
  main()