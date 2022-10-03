import os, argparse, sys

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
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
        self, tiles: dict, colors: list, row: int, col: int, state: tuple = (0, 0, 0)
    ):
        super().__init__()

        self.tiles = tiles
        self.colors = colors
        self.row = row
        self.col = col
        self.state = state

        self.update()

    def update(self):
        self.image = self.tiles[self.colors[self.state[0]]][self.state[1:]]
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
    elif args.level:
        if args.level < 1 or args.level > len(levels):
            print("Level not found")
            sys.exit(1)
        grid_config = levels[args.level - 1]
    elif args.random:
        if args.rows and args.cols and args.points:
            try:
                grid_config = Grid.create_random_config(
                    args.rows, args.cols, args.points
                )
            except Exception as e:
                print("Can't create random grid:", e)
                sys.exit(1)
        else:
            print("Random grid needs rows, cols and points")
            sys.exit(1)

    grid = Grid.from_config(grid_config)
    print("Loaded configuration correctly")

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

    colors = randomize_colors(list(COLORS.keys()), grid.qpoints)
    grid_gui = []
    for row in range(grid.rows):
        grid_gui.append([])
        for col in range(grid.cols):
            grid_gui[row].append(Tile(tiles, colors, row, col, grid[row, col]))
    print("Press 'R' to restart the grid")

    # Game loop
    while True:
        # Events
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit(0)
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
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    grid.restart()

        # Update tile states
        for row in range(grid.rows):
            for col in range(grid.cols):
                grid_gui[row][col].state = grid[row, col]
                grid_gui[row][col].update()

        # Draw to the screen
        window.fill((0, 0, 0))
        # Render the grid progress
        text_surface, rect = GAME_FONT.render(
            f"Progress: {grid.progress():.2%}", (255, 255, 255)
        )
        window.blit(text_surface, (MARGIN, MARGIN))
        # Render the number of moves
        text_surface, rect = GAME_FONT.render(f"Moves: {grid.moves}", (255, 255, 255))
        window.blit(text_surface, (WIDTH - rect.width - MARGIN, MARGIN))
        # Render the grid
        for row in range(grid.rows):
            for col in range(grid.cols):
                window.blit(grid_gui[row][col].image, grid_gui[row][col].rect)

        pg.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    # Args parser
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--file", help="path to a grid config file", type=str)
    group.add_argument("-l", "--level", help="level number of default levels", type=int)
    group.add_argument(
        "-r",
        "--random",
        help="randomize a grid. If used, the next args should be: rows, cols, points",
        action="store_true",
    )
    parser.add_argument(
        "rows", help="number of rows of the random grid", type=int, nargs="?"
    )
    parser.add_argument(
        "cols", help="number of cols of the random grid", type=int, nargs="?"
    )
    parser.add_argument(
        "points", help="quantity of points of the random grid", type=int, nargs="?"
    )

    args = parser.parse_args()
    main(args)
