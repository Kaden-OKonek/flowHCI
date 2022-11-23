from __future__ import annotations
import random

from utils import config


class Grid:
    """Represents the grid of a game. It is a rows * size matrix of tuples,
    where each tuple represents a tile color + state (see utils/config.py
    for the available TILE_STATES).

    The grid is more or less the interface that the game interacts with.
    The GUI is supossed to create a grid and then use it to both send new
    moves and print the current state of the grid as a matrix of tiles."""

    def __init__(self, rows: int, cols: int, qpoints: int, points: list) -> None:
        """Initialize a grid with the given rows, cols and points.

        Args:
            rows (int): number of rows. Must be between 2 and MAX_GRID_N
            cols (int): number of columns. Must be between 2 and MAX_GRID_N
            qpoints (int): quantity of points. Must be between MIN_POINTS and MAX_POINTS
            points (list): 2D list of tuples where:
                - list[i] are the i-th points
                - list[i][0] is (row, col) of the 1st point of i
                - list[i][1] is (row, col) of the 2nd point of i
        """

        assert (
            config.MIN_POINTS <= qpoints <= config.MAX_POINTS
        ), f"qpoints must be between {config.MIN_POINTS} and {config.MAX_POINTS}"
        assert (
            2 <= rows <= config.MAX_GRID_N
        ), f"rows must be between 2 and {config.MAX_GRID_N}"
        assert (
            2 <= cols <= config.MAX_GRID_N
        ), f"cols must be between 2 and {config.MAX_GRID_N}"
        assert len(points) == qpoints, f"len(points) must be equal to qpoints"

        self.rows = rows
        self.cols = cols
        self.qpoints = qpoints
        self.points = points

        self.restart()

    @staticmethod
    def from_config(data: dict) -> Grid:
        """Creates a grid from a dictionary configuration.

        Args:
            data (dict): dictionary with the same keys as the constructor

        Returns:
            Grid: grid created from the dictionary
        """

        return Grid(
            data["rows"],
            data["cols"],
            data["qpoints"],
            data["points"],
        )

    @staticmethod
    def randomize_point(rows: int, cols: int) -> tuple[int, int]:
        """Calculates a random point position

        Returns:
            tuple[int, int]: (row, col) of the random point
        """
        return random.randint(0, rows - 1), random.randint(0, cols - 1)

    @staticmethod
    def create_random_config(rows: int, cols: int, qpoints: int) -> dict:
        """Creates a random configuration with the given rows, cols and qpoints

        Args:
            rows (int): number of rows
            cols (int): number of columns
            qpoints (int): quantity of points

        Returns:
            dict: dictionary with the same keys as the constructor
        """

        assert (
            qpoints <= rows * cols // 2
        ), f"qpoints must be less or equal to {rows * cols // 2}"

        points = []
        points_set = set()
        for i in range(qpoints):
            points += [[]]
            for _ in range(2):  # 2 points per ith-color
                row, col = Grid.randomize_point(rows, cols)
                while (row, col) in points_set:
                    row, col = Grid.randomize_point(rows, cols)
                points_set.add((row, col))
                points[i] += [(row, col)]

        return {
            "rows": rows,
            "cols": cols,
            "qpoints": qpoints,
            "points": points,
        }

    def __str__(self) -> str:
        return str(self.grid)

    def __getitem__(self, tuple: tuple[int, int]) -> tuple[int, int, int]:
        """Returns the state of the cell at the given position

        Args:
            tuple (tuple[int, int]): position of the cell

        Returns:
            tuple[int, int, int]: state of the cell
        """

        row, col = tuple
        return self.grid[row][col]

    def restart(self) -> None:
        """Restarts the grid to its initial configuration."""

        self.grid = [[(0, 0, 0) for _ in range(self.cols)] for _ in range(self.rows)]
        self._initialize_grid()

        self._paths = [[]] * (self.qpoints + 1)
        self._is_pathing = False
        self._current_path = 0

        self.moves = 0

    def _initialize_grid(self) -> None:
        """Initialize the grid with the points"""

        for i in range(self.qpoints):
            for (row, col) in self.points[i]:
                # The state of the points is the index of the point
                # representing the color and 0, 0
                self.grid[row][col] = (i + 1, 0, 0)

    def _is_valid_cell(self, row: int, col: int) -> bool:
        """Checks if the given cell is valid

        Args:
            row (int): row of the cell
            col (int): column of the cell

        Returns:
            bool: True if the cell is valid, False otherwise
        """

        if row is None or col is None:
            return False
        return 0 <= row < self.rows and 0 <= col < self.cols

    def _position_of(self, point1: tuple[int, int], point2: tuple[int, int]) -> int:
        """Calculates the position of point2 relative to point1. They are expected to
        be adjacent but never the same cell.

        Args:
            point1 (tuple[int, int]): (row, col) of point1
            point2 (tuple[int, int]): (row, col) of point2

        Returns:
            int: position expressed as 1: up of, 2: right of, 3: down of, 4: left of
        """

        row1, col1 = point1
        row2, col2 = point2
        if row1 == row2:
            if col1 < col2:
                return 2
            else:
                return 4
        elif col1 == col2:
            if row1 < row2:
                return 3
            else:
                return 1

    def _are_adjacent(self, point1: tuple[int, int], point2: tuple[int, int]) -> bool:
        """Checks if point1 and point2 are adjacent

        Args:
            point1 (tuple[int, int]): (row, col) of point1
            point2 (tuple[int, int]): (row, col) of point2

        Returns:
            bool: True if point1 and point2 are adjacent, False otherwise
        """

        row1, col1 = point1
        row2, col2 = point2
        return abs(row1 - row2) + abs(col1 - col2) == 1

    def _cell_is_point(self, row: int, col: int) -> bool:
        """Checks if the given cell is a point

        Args:
            row (int): row of the cell
            col (int): column of the cell

        Returns:
            bool: True if the cell is a point, False otherwise
        """

        return self.grid[row][col][0] != 0 and (
            self.grid[row][col][1] == 0 or self.grid[row][col][2] == 0
        )

    def _restart_path_until_size(self, size: int = 0) -> None:
        """Restart the current path until it has the given size

        Args:
            size (int, optional): size of the path. Defaults to 0.
        """

        while len(self._paths[self._current_path]) > size:
            r, c = self._paths[self._current_path].pop()
            # Mark the cells as empty, except the points
            if not self._cell_is_point(r, c):
                self.grid[r][c] = (0, 0, 0)
            else:
                self.grid[r][c] = (self._current_path, 0, 0)

    def _restart_path_until_cell(self, row: int, col: int) -> None:
        """Restart the current path until it reaches the given cell

        Args:
            row (int): row of the cell
            col (int): column of the cell
        """

        while self._paths[self._current_path][-1] != (row, col):
            r, c = self._paths[self._current_path].pop()
            # Mark the cells as empty, except the points
            if not self._cell_is_point(r, c):
                self.grid[r][c] = (0, 0, 0)
            else:
                self.grid[r][c] = (self._current_path, 0, 0)

    def start_path(self, row: int = None, col: int = None) -> None:
        """Starts a path from the given cell and tracks moves.
        - If the cell is empty / isn't valid, it does nothing.
        - If the cell is a point, it starts a path of that color.
        - If the cell is a non-point color, it continues the path
          from the given cell. That is, it restarts the path from the
          point up to the given cell.

        Args:
            row (int, optional): row of the cell where the path is starting.
            Defaults to None.
            col (int, optional): column of the cell where the path is starting.
            Defaults to None.
        """

        if not self._is_valid_cell(row, col):
            return
        if self.grid[row][col] == (0, 0, 0):
            return

        self._is_pathing = True
        # If the cell isn't the same current path, increment the moves
        if self.grid[row][col][0] != self._current_path:
            self._current_path = self.grid[row][col][0]
            self.moves += 1

        # If there is no path, start a new path
        if self._paths[self._current_path] == []:
            self._paths[self._current_path] = [(row, col)]
        # If it's a point, restart the path
        elif self._cell_is_point(row, col):
            self._restart_path_until_size()
            self._paths[self._current_path] = [(row, col)]
        # Else, continue the path from the given cell
        else:
            self._restart_path_until_cell(row, col)
            # Update the state of the cell so that it ends the current path
            pos = self._position_of((row, col), self._paths[self._current_path][-2])
            self.grid[row][col] = (self._current_path, pos, 5)

    def end_path(self) -> None:
        """Ends the current path."""

        self._is_pathing = False

    def _move_to_cell(self, row: int, col: int) -> None:
        """Adds the given cell to the current path.

        Args:
            row (int): row of the cell
            col (int): column of the cell
        """

        # Update the state of the previous last cell so that it continues
        # the path to the new cell
        r, c = self._paths[self._current_path][-1]
        last_pos = self.grid[r][c][1]
        new_pos = self._position_of((r, c), (row, col))
        self.grid[r][c] = (self._current_path, last_pos, new_pos)
        # Update the state of the new cell so that it ends the current path
        pos = self._position_of((row, col), (r, c))
        if self._cell_is_point(row, col):
            self.grid[row][col] = (self._current_path, pos, 0)
        else:
            self.grid[row][col] = (self._current_path, pos, 5)
        # Add the new cell to the path
        self._paths[self._current_path] += [(row, col)]

    def continue_path(self, row: int = None, col: int = None) -> None:
        """Continues the current path to the given cell.
        - If the cell is valid and adjacent to the last path cell,
          it adds the cell to the path.
        - If the cell is second to last in the current path, it
          backtracks to it.
        - Otherwise, it does nothing.

        Args:
            row (int, optional): row of the cell where the path is moving.
            Defaults to None.
            col (int, optional): column of the cell where the path is moving.
            Defaults to None.
        """

        if not self._is_pathing:
            return
        if not self._is_valid_cell(row, col):
            return
        if not self._are_adjacent(self._paths[self._current_path][-1], (row, col)):
            return
        # Can't move to itself
        if self._paths[self._current_path][-1] == (row, col):
            return
        # Can move to empty cells or the other point
        if self.grid[row][col] == (0, 0, 0) or self.grid[row][col] == (
            self._current_path,
            0,
            0,
        ):
            pass
        # or to the second to last cell in the path
        elif len(self._paths[self._current_path]) > 1:
            if self._paths[self._current_path][-2] == (row, col):
                pass
            else:
                return
        else:
            return

        # If there is a path of the current cell
        if len(self._paths[self._current_path]) > 1:
            # If the cell is the second to last of the current path, backtrack
            if self._paths[self._current_path][-2] == (row, col):
                r, c = self._paths[self._current_path].pop()
                # Mark the cell as empty, except the points
                if not self._cell_is_point(r, c):
                    self.grid[r][c] = (0, 0, 0)
                else:
                    self.grid[r][c] = (self._current_path, 0, 0)
                # If the new last cell is a point, mark it as no path
                if len(self._paths[self._current_path]) == 1:
                    r, c = self._paths[self._current_path][0]
                    self.grid[r][c] = (self._current_path, 0, 0)
                # Else, mark it as the end of the path
                else:
                    r, c = self._paths[self._current_path][-1]
                    pos = self._position_of((r, c), self._paths[self._current_path][-2])
                    self.grid[r][c] = (self._current_path, pos, 5)
            # If the last cell in path is a point, do nothing
            elif self._cell_is_point(*self._paths[self._current_path][-1]):
                return
            # Else, add the cell to the path
            else:
                self._move_to_cell(row, col)
        # Else, add the cell to the path
        else:
            self._move_to_cell(row, col)

    def progress(self) -> float:
        """Calculates the progress of the grid. Progress is defined as the number of
        of cells that have a path divided by the total number of cells.

        Returns:
            float: progress of the grid between 0 and 1
        """

        progress = 0
        for path in self._paths:
            if len(path) > 1:
                progress += len(path)
        return progress / (self.rows * self.cols)

    def add_path(self, path: list[tuple[int, int]]) -> None:
        """Adds a path to the grid.

        Args:
            path (list[tuple[int, int]]): list of cells that form the path
        """

        self.start_path(*path[0])
        for cell in path[1:]:
            self._move_to_cell(*cell)
        self.end_path()

    def remove_path(self, current_path: int) -> None:
        """Removes a path from the grid.

        Args:
            current_path (int): index of the path to remove
        """

        self._current_path = current_path
        self._restart_path_until_size()
