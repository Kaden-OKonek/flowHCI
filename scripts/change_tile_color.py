import numpy as np
from PIL import Image
import pathlib, os

tiles_directory = (
    pathlib.Path(__file__) / ".." / ".." / "assets" / "sprites" / "tiles"
).resolve()

tiles_names = [
    "tile_0",
    "tile_1",
    "tile_2",
    "tile_3",
    "tile_4",
    "tile_01",
    "tile_02",
    "tile_03",
    "tile_04",
    "tile_12",
    "tile_23",
    "tile_34",
    "tile_41",
    "tile_13",
    "tile_24",
]
tile_types = ["", "_placed"]
tile_ext = ".png"

original_color = [
    "white",
    (255, 255, 255),
]

new_colors = {
    "red": (255, 0, 0),
    "silver": (192, 192, 192),
    "gray": (128, 128, 128),
    "green": (0, 128, 0),
    "lime": (0, 255, 0),
    "yellow": (255, 255, 0),
    "purple": (128, 0, 128),
    "magenta": (255, 0, 255),
    "navy": (0, 0, 128),
    "blue": (0, 0, 255),
    "teal": (0, 128, 128),
    "cyan": (0, 255, 255),
    "maroon": (128, 0, 0),
    "orange": (255, 165, 0),
    "moccasin": (255, 228, 181),
}

for tile_name in tiles_names:
    for color_name, color in new_colors.items():
        for tile_type in tile_types:
            tile_file = tile_name + tile_type + "_" + original_color[0] + tile_ext
            im = Image.open(tiles_directory / original_color[0] / tile_file)
            data = np.array(im)
            r1, g1, b1 = original_color[1]
            r2, g2, b2 = color
            red, green, blue = data[:, :, 0], data[:, :, 1], data[:, :, 2]
            mask = (red == r1) & (green == g1) & (blue == b1)
            data[:, :, :3][mask] = [r2, g2, b2]
            im = Image.fromarray(data)
            new_tile_file = tile_name + tile_type + "_" + color_name + tile_ext

            if not os.path.exists(tiles_directory / color_name):
                os.makedirs(tiles_directory / color_name)

            im.save(
                tiles_directory / color_name / new_tile_file,
            )
