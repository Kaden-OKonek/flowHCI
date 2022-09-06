from curses.ascii import SP
import sys, os
import pygame as pg

pg.init()

# GLOBAL DEFINITIONS

# Directories
BASE_DIR = os.path.split(os.path.abspath(__file__))[0]
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")

# Colors
COLORS = {
    "white": (255, 255, 255),
    "silver": (192, 192, 192),
    "gray": (128, 128, 128),
    "red": (255, 0, 0),
    "orange": (255, 165, 0),
    "moccasin": (255, 228, 181),
    "green": (0, 128, 0),
    "lime": (0, 255, 0),
    "yellow": (255, 255, 0),
    "purple": (128, 0, 128),
    "magenta": (255, 0, 255),
    "navy": (0, 0, 128),
    "blue": (0, 0, 255),
    "teal": (0, 128, 128),
    "cyan": (0, 255, 255),
    "maroon": (128, 0, 0),
}

# Tiles configuration
TILE_SIZE = 48
MAX_TILES_WIDTH = 15
MAX_TILES_HEIGHT = 15

# Display initialization
DISPLAY_WIDTH = TILE_SIZE * MAX_TILES_WIDTH
DISPLAY_HEIGHT = TILE_SIZE * MAX_TILES_HEIGHT

window = pg.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pg.display.set_caption("Flow")
timer = pg.time.Clock()


# IMPORT ASSETS

# Load sprites
def load_image(name: str, colorkey: pg._common._ColorValue = None) -> pg.Surface:
    """Loads an image from the assetss directory and returns it as a Surface object

    Args:
        name (str): path to the image file
        colorkey (pg._common._ColorValue, optional): transparent color to be placed
        on top of the image. Defaults to None.

    Raises:
        SystemExit: if the image file is not found or cannot be loaded

    Returns:
        pg.Surface: the image as a Surface object
    """

    fullname = os.path.join(ASSETS_DIR, name)
    try:
        image = pg.image.load(fullname)
    except (pg.error, FileNotFoundError) as message:
        print("Cannot load image:", name)
        raise SystemExit(message)
    image = image.convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pg.RLEACCEL)
    return image


tiles = dict()

# Import tiles sprites
for color in COLORS:
    tiles[color] = []
    for tile in os.listdir(os.path.join(SPRITES_DIR, "tiles", color)):
        tiles[color] += [load_image(os.path.join(SPRITES_DIR, "tiles", color, tile))]
# Empty tile
tiles["empty"] = [load_image(os.path.join(SPRITES_DIR, "tiles", "tile_empty.png"))]


class Tile(pg.sprite.Sprite):
    def __init__(self, x: int, y: int, color: str = None):
        super().__init__()

        if color is None:
            color = "empty"
            self.is_empty = True
        self.color = color

        self.image = tiles[color][0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.is_selected = False

    def update(self):
        pass
