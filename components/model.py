from .eventmanager import *
from .grid import Grid


class GameEngine(Listener):
    """
    Game engine that tracks the game state.
    """

    def __init__(self, event_manager: EventManager, grid: Grid) -> None:
        """
        Args:
            event_manager (EventManager): to post messages to
            the event queue.
            grid (Grid): the grid that the game engine will
            interact with.

        Attributes:
            running (bool): whether the game is running
        """

        self.event_manager = event_manager
        self.event_manager.register_listener(self)
        self.grid = grid
        self.running = False

    def notify(self, event: Event) -> None:
        if isinstance(event, QuitEvent):
            self.running = False
        elif isinstance(event, TilePressedEvent):
            self.grid.start_path(*event.pos)
        elif isinstance(event, TileReleasedEvent):
            self.grid.end_path()
        elif isinstance(event, TileHoveredEvent):
            self.grid.continue_path(*event.pos)
        elif isinstance(event, RestartEvent):
            self.grid.restart()

    def run(self) -> None:
        """
        Starts the game engine loop.

        The game engine loop is responsible for updating the
        game state. Currently, the game engine generates
        the tick event every loop iteration.
        """

        self.running = True
        self.event_manager.post(InitEvent())
        print("Press R to restart")
        while self.running:
            tick = TickEvent()
            self.event_manager.post(tick)
