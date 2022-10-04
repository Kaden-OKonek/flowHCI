import pygame as pg
import os, random, json

from . import config


def load_image(file: str, scale: tuple[int, int] = None) -> pg.Surface:
    """Loads an image from the assets directory and returns it as a Surface object

    Args:
        file (str): path to the image file
        scale (tuple[int, int], optional): scaling in (width px, heigh px)
        to be done to the image. Defaults to None.

    Raises:
        SystemExit: if the image file is not found or cannot be loaded

    Returns:
        pg.Surface: the image as a Surface object
    """

    try:
        surface = pg.image.load(file)
    except (pg.error, FileNotFoundError) as message:
        print("Cannot load image:", file)
        raise SystemExit(message)
    if scale:
        surface = pg.transform.scale(surface, scale)
    return surface.convert()


def load_tiles():
    """Load tiles sprites from assets directory.

    Returns:
        dict: Tile sprites divided by color. Every color has a state
        for each tile type.
    """

    tiles = {}
    for color in config.COLORS:
        tiles[color] = {}
        for state in config.TILE_STATES:
            s1 = min(state[0], state[1])
            s2 = max(state[0], state[1])

            tiles[color][state] = load_image(
                os.path.join(
                    config.ASSETS_DIR,
                    "sprites",
                    "tiles",
                    color,
                    f"tile_{s1}{s2}_{color}.png",
                ),
                (config.TILE_SIZE, config.TILE_SIZE),
            )
    # Empty tile
    tiles["empty"] = {
        (0, 0): load_image(
            os.path.join(config.ASSETS_DIR, "sprites", "tiles", "tile_empty.png"),
            (config.TILE_SIZE, config.TILE_SIZE),
        )
    }

    return tiles


def randomize_colors(quantity: int) -> list:
    """Chooses a random subset of colors from the COLORS names.
    Adds an "empty" color as the first element of the subset.

    Args:
        quantity (int): number of colors to choose.
        Excludes the empty color.

    Returns:
        list: chosen list of colors names
    """

    colors = list(config.COLORS.keys())
    random.shuffle(colors)
    # return list with empty color at the start
    return ["empty"] + colors[:quantity]


def load_grid_config(file: str) -> list | dict:
    """Loads a grid configuration JSON file. If the file is an array,
    it is the levels configuration. If the file is an object, it is
    a single grid configuration.

    Args:
        file (str): path to the JSON file

    Raises:
        Exception: if the file is not found or cannot be loaded

    Returns:
        list | dict: list of levels or dictionary of grid configuration
    """

    try:
        file = open(file, "r")
    except FileNotFoundError as message:
        print("Cannot load:", file)
        raise Exception(message)
    return json.load(file)
