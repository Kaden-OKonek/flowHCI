# Colors
COLORS = {
    "white": (255, 255, 255),
    "silver": (192, 192, 192),
    "gray": (128, 128, 128),
    "red": (255, 0, 0),
    "orange": (255, 165, 0),
    "moccasin": (255, 228, 181),
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
}

# Points
MIN_POINTS = 2
MAX_POINTS = len(COLORS)

# Grid size
MAX_GRID_N = 15  # 15x15 is the maximum grid size

# Tile states
TILE_STATES = [
    (0, 0),  # "start" / "end",
    (0, 1),  # "start_to_up",
    (0, 2),  # "start_to_right",
    (0, 3),  # "start_to_down",
    (0, 4),  # "start_to_left",
    (1, 0),  # "up_to_end",
    (2, 0),  # "right_to_end",
    (3, 0),  # "down_to_end",
    (4, 0),  # "left_to_end",
    (1, 3),  # "up_to_down",
    (3, 1),  # "down_to_up",
    (2, 4),  # "left_to_right",
    (4, 2),  # "right_to_left",
    (1, 2),  # "up_to_right",
    (2, 1),  # "right_to_up",
    (2, 3),  # "right_to_down",
    (3, 2),  # "down_to_right",
    (3, 4),  # "down_to_left",
    (4, 3),  # "left_to_down",
    (4, 1),  # "left_to_up",
    (1, 4),  # "up_to_left",
    (1, 5),  # "up_to_middle",
    (2, 5),  # "right_to_middle",
    (3, 5),  # "down_to_middle",
    (4, 5),  # "left_to_middle",
]
