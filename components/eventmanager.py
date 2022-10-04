class Event:
    """
    Superclass for any event that can be handled
    by the event manager.
    """

    def __init__(self, name) -> None:
        self.name = name

    def __str__(self) -> str:
        return f"Event: {self.name}"

    def __repr__(self) -> str:
        return self.__str__()


class QuitEvent(Event):
    """
    Quit the game event.
    """

    def __init__(self) -> None:
        super().__init__("quit")


class TickEvent(Event):
    """
    Tick event.
    """

    def __init__(self) -> None:
        super().__init__("tick")


class RestartEvent(Event):
    """
    Restart the state event. Triggered by pressing the R key.
    """

    def __init__(self) -> None:
        super().__init__("restart")


class TileEvent(Event):
    """
    Superclass to represent interaction with a tile.
    """

    def __init__(self, pos: tuple[int, int]) -> None:
        super().__init__("tile")
        self.pos = pos

    def __str__(self) -> str:
        return f"Event: {self.name} - {self.pos}"

    def __repr__(self) -> str:
        return self.__str__()


class TilePressedEvent(TileEvent):
    """
    Tile pressed (mouse down) event.
    """

    def __init__(self, pos: tuple[int, int]) -> None:
        super().__init__(pos)
        self.name = "tile_pressed"


class TileHoveredEvent(TileEvent):
    """
    Tile hovered (mouse motion) event.
    """

    def __init__(self, pos: tuple[int, int]) -> None:
        super().__init__(pos)
        self.name = "tile_hovered"


class TileReleasedEvent(TileEvent):
    """
    Tile released (mouse up) event.
    """

    def __init__(self) -> None:
        super().__init__(None)
        self.name = "tile_released"


class InitEvent(Event):
    """
    Initialize event to tell listeners to initialize
    themselves.
    """

    def __init__(self) -> None:
        super().__init__("init")


class Listener:
    """
    Superclass for any object that is mediated
    by the event manager.
    """

    def __init__(self) -> None:
        self.event_manager = None

    def notify(self, event: Event) -> None:
        """
        Notify the listener of an event.
        """
        pass


class EventManager:
    """
    Coordinates communication between the model, view, and controller.
    """

    def __init__(self):
        self.listeners = {}

    def register_listener(self, listener: Listener) -> None:
        """
        Register a listener to be notified of posted events.
        """

        self.listeners[listener] = 1

    def unregister_listener(self, listener: Listener) -> None:
        """
        Unregister a listener.
        """

        del self.listeners[listener]

    def post(self, event: Event) -> None:
        """
        Post an event to all listeners.
        """

        for listener in self.listeners:
            listener.notify(event)
