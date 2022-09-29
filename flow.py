import os
import pygame as pg
import pygame_menu as pgm

from utils.values import *
from utils.utils import *
from grid import Grid

pg.init()

# GLOBAL DEFINITIONS

# Directories
BASE_DIR = os.path.split(os.path.abspath(__file__))[0]
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Tiles configuration
TILE_SIZE = 48

# Display initialization
FPS = 60
WINDOW_SIZE = (TILE_SIZE * MAX_GRID_N, TILE_SIZE * MAX_GRID_N)


window = pg.display.set_mode(WINDOW_SIZE)
pg.display.set_caption("Flow")
clock = pg.time.Clock()


# IMPORT ASSETS

# Import tiles sprites
tiles = dict()
for color in COLORS:
    tiles[color] = dict()
    for state in TILE_STATES:
        s1 = min(state[0], state[1])
        s2 = max(state[0], state[1])

        tiles[color][state] = load_image(
            os.path.join(
                ASSETS_DIR,
                "sprites",
                "tiles",
                color,
                f"tile_{s1}{s2}_{color}.png",
            ),
            (TILE_SIZE, TILE_SIZE),
        )
# Empty tile
tiles["empty"] = {
    (0, 0): load_image(
        os.path.join(ASSETS_DIR, "sprites", "tiles", "tile_empty.png"),
        (TILE_SIZE, TILE_SIZE),
    )
}


class Tile(pg.sprite.Sprite):
    def __init__(self, row: int, col: int, colors: list, color: int = 0):
        super().__init__()

        self.row = row
        self.col = col
        self.color_str = colors[color]
        self.state = (color, 0, 0)

        self.is_point = True if color != 0 else False

        self.update()

    def update(self):
        self.image = tiles[self.color_str][self.state[1:]]
        self.rect = self.image.get_rect()
        self.rect.x = self.col * TILE_SIZE
        self.rect.y = self.row * TILE_SIZE


colors = ["empty", "red", "yellow"]

grid = Grid(5, 5, len(colors) - 1)
grid_gui = []
for row in range(5):
    grid_gui.append([])
    for col in range(5):
        grid_gui[row].append(Tile(row, col, colors, grid[row, col][0]))

# The objective of the game is to connect all the points with the same color
# in a single line. The line can only go up, down, left or right, and cannot
# cross itself. The line must start and end in a point.
# The Grid class has all the functionality, and the GUI is just a wrapper
# around it.
# The GUI is a 2D array of Tile objects, which are pygame sprites. The
# Grid class has a 2D array of states, which are tuples of the form
# (color, from, to). The state is used to update the sprite image.
# In order to play, the user must start a long click anywhere on the gui grid
# to select a point or path. Then, the user must move the mouse to the desired
# position and release the click. Everytime a new tile is selected, the
# Grid class is updated, and the GUI is updated accordingly.
# When the user lifts the click, the Grid stops the path, and the GUI is
# updated accordingly.
# The Grid starts a path with the start_path(row, col) method.
# The Grid continues a path with the move(row, col) method.
# The Grid stops a path with the end_path() method.

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
        elif event.type == pg.MOUSEBUTTONDOWN:
            pos = pg.mouse.get_pos()
            row = pos[1] // TILE_SIZE
            col = pos[0] // TILE_SIZE
            grid.start_path(row, col)
        elif event.type == pg.MOUSEBUTTONUP:
            grid.end_path()
        elif event.type == pg.MOUSEMOTION:
            pos = pg.mouse.get_pos()
            row = pos[1] // TILE_SIZE
            col = pos[0] // TILE_SIZE
            grid.move(row, col)

    for row in range(5):
        for col in range(5):
            grid_gui[row][col].state = grid[row, col]
            grid_gui[row][col].color_str = colors[grid[row, col][0]]
            grid_gui[row][col].update()

    window.fill((0, 0, 0))
    for row in range(5):
        for col in range(5):
            window.blit(grid_gui[row][col].image, grid_gui[row][col].rect)
    pg.display.update()

    clock.tick(FPS)
