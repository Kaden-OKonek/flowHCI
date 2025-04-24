import os
import pygame as pg
import pygame.freetype as pgft

from . import model
from .eventmanager import *
from utils import config, utils


class Tile(pg.sprite.Sprite):
    """A tile that represent a cell in the grid. It can be empty or filled with a color,
    and can be connected to other tiles. It is the visual representation of the Grid state
    in the game."""

    def __init__(
        self, tiles: dict, colors: list, row: int, col: int, state: tuple = (0, 0, 0)
    ):
        """
        Args:
            tiles (dict): the tiles sprites
            colors (list): the colors of the tiles
            row (int): the row of the tile in the grid
            col (int): the column of the tile in the grid
            state (tuple, optional): state of the tile. Defaults to (0, 0, 0).
        """
        super().__init__()

        self.tiles = tiles
        self.colors = colors
        self.row = row
        self.col = col
        self.state = state

    def update(self):
        """Update the tile sprite according to its current state."""

        self.image = self.tiles[self.colors[self.state[0]]][self.state[1:]]
        self.rect = self.image.get_rect()
        self.rect.x = self.col * config.TILE_SIZE + config.MARGIN
        self.rect.y = self.row * config.TILE_SIZE + config.FONT_SIZE + config.MARGIN * 2


class GameView(Listener):
    """
    The View of the game. It is responsible for drawing the game state to the screen.
    """

    def __init__(self, event_manager: EventManager, model: model.GameEngine, colored_tiles=None) -> None:
        """
        Args:
            event_manager (EventManager): to post messages to
            the event queue.
            model (GameEngine): the game engine.
            colored_tiles (dict, optional): custom colored tiles based on user preferences

        Attributes:
            is_initialized (bool): whether the GUI is initialized
            screen (pygame.Surface): the screen surface to draw to
            clock (pygame.time.Clock): the game clock
            game_font (pygame.freetype.Font): the game font to render text
            tiles (dict): the tiles sprites
            colors (list): the colors to use for the tiles
            grid_gui (list): the grid of tiles
            custom_colored_tiles (dict): custom colored tiles from user selection
        """

        self.event_manager = event_manager
        self.event_manager.register_listener(self)
        self.model = model
        self.custom_colored_tiles = colored_tiles

        self.is_initialized = False
        self.screen = None
        self.clock = None
        self.game_font = None
        self.tiles = {}
        self.colors = []
        self.grid_gui = []

    def notify(self, event: Event) -> None:
        if isinstance(event, InitEvent):
            self.initialize()
        elif isinstance(event, QuitEvent):
            self.is_initialized = False
            pg.quit()
        elif isinstance(event, TickEvent):
            self.draw()
            self.clock.tick(config.FPS)

    def draw(self) -> None:
        """
        Draw the game state to the screen.
        """

        if not self.is_initialized:
            return

        # Clear the screen
        self.screen.fill((0, 0, 0))

        # Update the state and draw the grid
        for row in range(self.model.grid.rows):
            for col in range(self.model.grid.cols):
                self.grid_gui[row][col].state = self.model.grid.grid[row][col]
                self.grid_gui[row][col].update()
                self.screen.blit(
                    self.grid_gui[row][col].image, self.grid_gui[row][col].rect
                )

        # Draw the progress top left
        text_surface, _ = self.game_font.render(
            f"Progress: {self.model.grid.progress():.2%}", (255, 255, 255)
        )
        self.screen.blit(text_surface, (config.MARGIN, config.MARGIN))

        # Draw the moves top right
        text_surface, text_rect = self.game_font.render(
            f"Moves: {self.model.grid.moves}", (255, 255, 255)
        )
        self.screen.blit(
            text_surface,
            (config.WIDTH - text_rect.width - config.MARGIN, config.MARGIN),
        )

        pg.display.flip()

    def load_resources(self):
        """Load tile resources - either default or custom colored tiles"""
        if self.custom_colored_tiles:
            # Use custom colored tiles provided by the user
            self.tiles = self.custom_colored_tiles
        else:
            # Load default tiles
            self.tiles = utils.load_tiles()
            
        # Generate color list
        self.colors = utils.randomize_colors(self.model.grid.qpoints)

    def initialize(self) -> None:
        """
        Initialize the GUI.
        """

        pg.init()
        pgft.init()
        self.screen = pg.display.set_mode((config.WIDTH, config.HEIGHT))
        pg.display.set_caption(config.TITLE)
        self.clock = pg.time.Clock()
        self.game_font = pgft.Font(
            os.path.join(config.ASSETS_DIR, "fonts", config.FONT_FAMILY),
            config.FONT_SIZE,
        )

        # Load tiles (custom or default)
        self.load_resources()

        for row in range(self.model.grid.rows):
            self.grid_gui.append([])
            for col in range(self.model.grid.cols):
                self.grid_gui[row].append(
                    Tile(
                        self.tiles,
                        self.colors,
                        row,
                        col,
                        self.model.grid.grid[row][col],
                    )
                )

        self.is_initialized = True