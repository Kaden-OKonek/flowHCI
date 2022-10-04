import pygame as pg

from . import model
from .eventmanager import *
from utils import config


class GameController(Listener):
    """
    Controller that handles user input.
    """

    def __init__(self, event_manager: EventManager, model: model.GameEngine) -> None:
        """
        Args:
            event_manager (EventManager): to post messages to
            the event queue.
            model (GameEngine): the game engine.
        """

        self.event_manager = event_manager
        self.event_manager.register_listener(self)
        self.model = model

    def calculate_tile_pos(self, pos: tuple) -> tuple:
        """Calculate position of the tile that was interacted with.

        Args:
            pos (tuple): the position of the mouse.

        Returns:
            tuple: the (row, col) of the tile.
        """

        row = (pos[1] - config.MARGIN - config.FONT_SIZE * 2) // config.TILE_SIZE
        col = (pos[0] - config.MARGIN) // config.TILE_SIZE
        return (row, col)

    def notify(self, event: Event) -> None:
        if isinstance(event, TickEvent):
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.event_manager.post(QuitEvent())
                elif event.type == pg.MOUSEBUTTONDOWN:
                    self.event_manager.post(
                        TilePressedEvent(self.calculate_tile_pos(event.pos))
                    )
                elif event.type == pg.MOUSEMOTION:
                    self.event_manager.post(
                        TileHoveredEvent(self.calculate_tile_pos(event.pos))
                    )
                elif event.type == pg.MOUSEBUTTONUP:
                    self.event_manager.post(TileReleasedEvent())
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_r:
                        self.event_manager.post(RestartEvent())
