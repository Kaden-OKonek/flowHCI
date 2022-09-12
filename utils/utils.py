import pygame as pg
from typing import Tuple


def load_image(file: str, scale: Tuple = None) -> pg.Surface:
    """Loads an image from the assets directory and returns it as a Surface object

    Args:
        file (str): path to the image file
        scale (tuple, optional): scaling in (width px, heigh px) to be done to the
        image. Defaults to None.

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
