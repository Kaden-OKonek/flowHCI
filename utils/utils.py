import pygame as pg
import random
import json


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


def randomize_colors(colors: list, quantity: int) -> list:
    """Chooses a random subset of colors from a list of colors.
    Adds an "empty" color as the first element of the subset.

    Args:
        colors (list): list of color names
        quantity (int): number of colors to choose.
        Excludes the empty color.

    Returns:
        list: chosen list of colors names
    """

    random.shuffle(colors)
    # return list with empty color at the start
    return ["empty"] + colors[:quantity]


def load_levels(file: str) -> list:
    """Loads levels from a JSON file.

    Args:
        file (str): path to the JSON file

    Raises:
        Exception: if the file is not found or cannot be loaded

    Returns:
        list: list of levels
    """

    try:
        file = open(file, "r")
    except FileNotFoundError as message:
        print("Cannot load levels:", file)
        raise Exception(message)
    return json.load(file)
