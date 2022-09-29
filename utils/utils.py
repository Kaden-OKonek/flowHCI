import pygame as pg
import random

from .values import COLORS


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


def randomize_colors(quantity: int) -> list:
    """Returns a list of random colors. The first color is
    always "empty" and the rest are random colors from the
    values.COLORS dict.

    Args:
        quantity (int): number of colors to be generated
        (excluding the "empty" color)

    Returns:
        list: list of color names
    """

    colors = list(COLORS.keys())
    random.shuffle(colors)
    # return list with empty color at the start
    return ["empty"] + colors[:quantity]
