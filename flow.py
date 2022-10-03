import os, argparse, sys
import pygame as pg
import pygame.freetype as pgft

from utils.values import *
from utils.utils import *
from grid import Grid

# GLOBAL DEFINITIONS

# Directories
BASE_DIR = os.path.split(os.path.abspath(__file__))[0]
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Tiles configuration
TILE_SIZE = 42

# Fonts configuration
FONT_SIZE = 20

# Display configuration
MARGIN = 16
WIDTH = TILE_SIZE * MAX_GRID_N + MARGIN * 2
HEIGHT = TILE_SIZE * MAX_GRID_N + MARGIN * 3 + FONT_SIZE
WINDOW_SIZE = (WIDTH, HEIGHT)

FPS = 60


def load_tiles():
    """Load tiles sprites from assets directory.

    Returns:
        dict: Tile sprites divided by color. Every color has a state
        for each tile type.
    """

    tiles = {}
    for color in COLORS:
        tiles[color] = {}
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

    return tiles


class Tile(pg.sprite.Sprite):
    def __init__(
        self, tiles: dict, row: int, col: int, color: int = 0, color_str: str = "empty"
    ):
        super().__init__()

        self.tiles = tiles
        self.row = row
        self.col = col
        self.color_str = color_str
        self.state = (color, 0, 0)

        self.update()

    def update(self):
        self.image = self.tiles[self.color_str][self.state[1:]]
        self.rect = self.image.get_rect()
        self.rect.x = self.col * TILE_SIZE + MARGIN
        self.rect.y = self.row * TILE_SIZE + FONT_SIZE + MARGIN * 2


def main(args):
    try:
        levels = load_grid_config(os.path.join(DATA_DIR, "levels.json"))
    except Exception as e:
        print(e)
        sys.exit(1)

    if args.file:
        try:
            grid_config = load_grid_config(args.file)
        except Exception as e:
            print(e)
            sys.exit(1)
    else:
        if args.level < 1 or args.level > len(levels):
            print("Level not found")
            sys.exit(1)
        grid_config = levels[args.level - 1]

    # PYGAME INITIALIZATION
    pg.init()
    pg.font.init()
    #   Window and clock
    window = pg.display.set_mode(WINDOW_SIZE)
    pg.display.set_caption("Flow")
    clock = pg.time.Clock()
    #   Fonts
    GAME_FONT = pgft.Font(
        os.path.join(ASSETS_DIR, "fonts", "Roboto-Regular.ttf"), FONT_SIZE
    )
    #   Tiles sprites
    tiles = load_tiles()

    grid = Grid.from_config(grid_config)
    colors = randomize_colors(list(COLORS.keys()), grid_config["qpoints"])

    grid_gui = []
    for row in range(grid_config["rows"]):
        grid_gui.append([])
        for col in range(grid_config["cols"]):
            grid_gui[row].append(
                Tile(tiles, row, col, grid[row, col][0], colors[grid[row, col][0]])
            )

    # Game loop
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()
                row = (pos[1] - MARGIN - FONT_SIZE * 2) // TILE_SIZE
                col = (pos[0] - MARGIN) // TILE_SIZE
                grid.start_path(row, col)
            elif event.type == pg.MOUSEBUTTONUP:
                grid.end_path()
            elif event.type == pg.MOUSEMOTION:
                pos = pg.mouse.get_pos()
                row = (pos[1] - MARGIN - FONT_SIZE * 2) // TILE_SIZE
                col = (pos[0] - MARGIN) // TILE_SIZE
                grid.move_path(row, col)

        for row in range(grid_config["rows"]):
            for col in range(grid_config["cols"]):
                grid_gui[row][col].state = grid[row, col]
                grid_gui[row][col].color_str = colors[grid[row, col][0]]
                grid_gui[row][col].update()

        window.fill((0, 0, 0))
        for row in range(grid_config["rows"]):
            for col in range(grid_config["cols"]):
                window.blit(grid_gui[row][col].image, grid_gui[row][col].rect)
        # render grid.progress() as text below the grid
        text_surface, rect = GAME_FONT.render(
            f"Progress: {grid.progress():.2%}", (255, 255, 255)
        )
        window.blit(text_surface, (MARGIN, MARGIN))
        # render grid.moves as text below the progress
        text_surface, rect = GAME_FONT.render(f"Moves: {grid.moves}", (255, 255, 255))
        window.blit(text_surface, (WIDTH - rect.width - MARGIN, MARGIN))

        pg.display.flip()

        clock.tick(FPS)


if __name__ == "__main__":
    # Args parser
    parser = argparse.ArgumentParser()
    # Only of the following arguments can be used
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-f",
        "--file",
        help="Path to grid configuration file",
        type=str,
        default=None,
    )
    group.add_argument(
        "-l",
        "--level",
        help="Level number",
        type=int,
        default=1,
    )

    args = parser.parse_args()
    main(args)
