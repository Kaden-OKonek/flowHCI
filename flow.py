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
timer = pg.time.Clock()


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
            )
        )
# Empty tile
tiles["empty"] = {
    (0, 0): load_image(os.path.join(ASSETS_DIR, "sprites", "tiles", "tile_empty.png"))
}


class Tile(pg.sprite.Sprite):
    def __init__(self, row: int, col: int, colors: list, color: int = 0):
        super().__init__()

        self.color = colors[color]
        self.row = row
        self.col = col
        self.state = (color, 0, 0)

        self.is_start = True if color != 0 else False

        self.image = tiles[self.color][self.state[1:]]
        self.rect = self.image.get_rect()
        self.rect.x = col * TILE_SIZE
        self.rect.y = row * TILE_SIZE

    def update(self):
        pass


while True:
    pass
