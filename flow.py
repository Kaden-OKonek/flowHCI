import os
import pygame as pg
import pygame.freetype as pgft

from utils.values import *
from utils.utils import *
from grid import Grid

pg.init()
pg.font.init()

# GLOBAL DEFINITIONS

# Directories
BASE_DIR = os.path.split(os.path.abspath(__file__))[0]
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Tiles configuration
TILE_SIZE = 42

# Fonts configuration
FONT_SIZE = 20
GAME_FONT = pgft.Font(
    os.path.join(ASSETS_DIR, "fonts", "Roboto-Regular.ttf"), FONT_SIZE
)

# Display initialization
MARGIN = 16
WIDTH = TILE_SIZE * MAX_GRID_N + MARGIN * 2
HEIGHT = TILE_SIZE * MAX_GRID_N + MARGIN * 3 + FONT_SIZE
WINDOW_SIZE = (WIDTH, HEIGHT)

# Window and clock
window = pg.display.set_mode(WINDOW_SIZE)
pg.display.set_caption("Flow")

FPS = 60
clock = pg.time.Clock()


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
    def __init__(self, tiles: dict, row: int, col: int, colors: list, color: int = 0):
        super().__init__()

        self.tiles = tiles
        self.row = row
        self.col = col
        self.color_str = colors[color]
        self.state = (color, 0, 0)

        self.is_point = True if color != 0 else False

        self.update()

    def update(self):
        self.image = self.tiles[self.color_str][self.state[1:]]
        self.rect = self.image.get_rect()
        self.rect.x = self.col * TILE_SIZE + MARGIN
        self.rect.y = self.row * TILE_SIZE + FONT_SIZE + MARGIN * 2


def main():
    tiles = load_tiles()
    levels = load_levels(os.path.join(DATA_DIR, "levels.json"))
    colors = randomize_colors(list(COLORS.keys()), 5)

    grid = Grid.from_dict(levels[0])
    grid_gui = []
    for row in range(5):
        grid_gui.append([])
        for col in range(5):
            grid_gui[row].append(Tile(tiles, row, col, colors, grid[row, col][0]))

    global window
    global clock

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

        for row in range(5):
            for col in range(5):
                grid_gui[row][col].state = grid[row, col]
                grid_gui[row][col].color_str = colors[grid[row, col][0]]
                grid_gui[row][col].update()

        window.fill((0, 0, 0))
        for row in range(5):
            for col in range(5):
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
    main()
