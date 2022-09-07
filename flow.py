import os
import pygame as pg

from values import *
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
DISPLAY_WIDTH = TILE_SIZE * MAX_GRID_N
DISPLAY_HEIGHT = TILE_SIZE * MAX_GRID_N

FPS = 30

window = pg.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pg.display.set_caption("Flow")
timer = pg.time.Clock()


# IMPORT ASSETS

# Load sprites
def load_image(file: str, scale: tuple = None) -> pg.Surface:
    """Loads an image from the assets directory and returns it as a Surface object

    Args:
        file (str): relative path from ASSETS_DIR to the image file
        scale (tuple, optional): scaling in (width px, heigh px) to be done to the
        image. Defaults to None.

    Raises:
        SystemExit: if the image file is not found or cannot be loaded

    Returns:
        pg.Surface: the image as a Surface object
    """

    try:
        file = os.path.join(ASSETS_DIR, file)
        surface = pg.image.load(file)
    except (pg.error, FileNotFoundError) as message:
        print("Cannot load image:", file)
        raise SystemExit(message)
    if scale:
        surface = pg.transform.scale(surface, scale)
    return surface.convert()


TILE_STATES = [
    (0, 0),  # "start",
    (0, 1),  # "start_to_up",
    (0, 2),  # "start_to_right",
    (0, 3),  # "start_to_down",
    (0, 4),  # "start_to_left",
    (1, 3),  # "vertical",
    (2, 4),  # "horizontal",
    (1, 2),  # "up_to_right",
    (2, 3),  # "right_to_down",
    (3, 4),  # "down_to_left",
    (4, 1),  # "left_to_up",
    (1, 5),  # "up_to_middle",
    (2, 5),  # "right_to_middle",
    (3, 5),  # "down_to_middle",
    (4, 5),  # "left_to_middle",
]

# Import tiles sprites
tiles = dict()
for color in COLORS:
    tiles[color] = dict()
    is_placed_state = {0: "", 1: "_placed"}

    for state in TILE_STATES:
        for is_placed, is_placed_str in is_placed_state.items():
            tiles[color][(state[0], state[1], is_placed)] = load_image(
                os.path.join(
                    "sprites",
                    "tiles",
                    color,
                    f"tile_{state[0]}{state[1]}{is_placed_str}_{color}.png",
                )
            )
# Empty tile
TILE_STATES += [(-1, -1)]
tiles["empty"] = {
    (-1, -1, 0): load_image(os.path.join("sprites", "tiles", "tile_empty.png")),
    (-1, -1, 1): load_image(os.path.join("sprites", "tiles", "tile_empty.png")),
}


class Tile(pg.sprite.Sprite):
    def __init__(self, row: int, col: int, color: str = None):
        super().__init__()

        self.row = row
        self.col = col

        self.state = (0, 0, 0)
        self.is_start = True
        self.is_placed = False
        self.is_path = False

        if color is None or color == "empty":
            color = "empty"
            self.is_empty = True
            self.is_start = False
        self.color = color

        self.image = tiles[self.color][self.state]
        self.rect = self.image.get_rect()
        self.rect.x = col * TILE_SIZE
        self.rect.y = row * TILE_SIZE

    def update(self):
        pass
