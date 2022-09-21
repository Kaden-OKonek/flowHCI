from utils.values import *
import random


class Grid:
    """Represents the grid of a game. It is a rows * size matrix of tuples,
    where each tuple represents a tile color + state (see utils/values.py
    for the available TILE_STATES).

    The grid is more or less the interface that the game interacts with.
    The GUI is supossed to create a grid and then use it to both send new
    moves and print the current state of the grid as a matrix of tiles."""

    def __init__(
        self, rows: int, cols: int, points: int, starting_points: list = []
    ) -> None:
        """Initialize a grid with the given rows, cols and points. If starting_points
        is not empty, it will be used as the starting points of the grid

        Args:
            rows (int): number of rows. Must be between 2 and MAX_GRID_N
            cols (int): number of columns. Must be between 2 and MAX_GRID_N
            points (int): number of points. Must be between MIN_POINTS and MAX_POINTS
            starting_points (list, optional): 2D list of tuples where:
                - list[i] is the i-th starting point
                - list[i][0] is (row, col) of the starting point of i
                - list[i][1] is (row, col) of the 2nd starting point of i
                Initialized at random if not given.
        """

        assert (
            MIN_POINTS <= points <= MAX_POINTS
        ), f"points must be between {MIN_POINTS} and {MAX_POINTS}"
        assert 2 <= rows <= MAX_GRID_N, f"rows must be between 2 and {MAX_GRID_N}"
        assert 2 <= cols <= MAX_GRID_N, f"cols must be between 2 and {MAX_GRID_N}"

        self.rows = rows
        self.cols = cols
        self.points = points
        self.starting_points = starting_points
        self._starting_points_set = set()
        if self.starting_points == []:
            self._randomize_starting_points()
        else:
            for i in range(self.points):
                for row, col in self.starting_points[i]:
                    self._starting_points_set.add((row, col))

        assert (
            len(self.starting_points) == self.points
        ), f"len(starting_points) must be equal to points"

        # Create grid with states (0, 0, 0)
        # (0, 0, 0) means empty tile
        self.grid = [[(0, 0, 0) for _ in range(cols)] for _ in range(rows)]
        # Set starting points
        self._initialize_grid()

        self.paths = [[]] * (self.points + 1)
        self._is_pathing = False
        self._current_path = None

    def __str__(self) -> str:
        return str(self.grid)

    def _randomize_point(self) -> tuple[int, int]:
        """Calculates a random point position

        Returns:
            tuple[int, int]: (row, col) of the random point
        """
        return random.randint(0, self.rows - 1), random.randint(0, self.cols - 1)

    def _randomize_starting_points(self) -> None:
        """Randomize starting points. Only called if starting_points is not given"""

        for i in range(self.points):
            self.starting_points.append([])
            for _ in range(2):  # 2 starting points per ith-point
                row, col = self._randomize_point()
                while (row, col) in self._starting_points_set:
                    row, col = self._randomize_point()
                self._starting_points_set.add((row, col))
                self.starting_points[i] += [(row, col)]

    def _initialize_grid(self) -> None:
        """Initialize the grid with the starting points"""

        for i in range(self.points):
            for row, col in self.starting_points[i]:
                # The state of the starting points is the index of the point
                # representing the color and 0, 0
                self.grid[row][col] = (i + 1, 0, 0)

    def progress(self) -> float:
        """Calculates the progress of the grid. Progress is defined as the number of
        of non-starting cells that have a point.

        Returns:
            float: progress of the grid between 0 and 1
        """

        progress = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if (row, col) not in self._starting_points_set and (
                    self.grid[row][col] != 0
                ):
                    progress += 1
        return progress / (self.rows * self.cols - 2 * self.points)

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

    def position_of(self, point1: tuple[int, int], point2: tuple[int, int]) -> int:
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

    def are_adjacent(self, point1: tuple[int, int], point2: tuple[int, int]) -> bool:
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

    def start_path(self, row: int = None, col: int = None) -> None:
        """Starts a path from the given cell:
        - If the cell is empty / isn't valid, it does nothing.
        - If the cell is a starting point, it starts a path of that color.
        - If the cell is a non-starting color, it continues the path
        from the given cell. That is, it restarts the path from the
        starting point up to the given cell.

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
        self._current_path = self.grid[row][col][0]

        # If there is no path, start a new path
        if self.paths[self._current_path] == []:
            self.paths[self._current_path] = [(row, col)]
        # If it's a point, restart the path
        elif self.grid[row][col][1] == 0:
            while len(self.paths[self._current_path]) > 1:
                r, c = self.paths[self._current_path].pop()
                # Also mark the cells as empty in the grid
                self.grid[r][c] = (0, 0, 0)
            # If it's the starting point of the path, mark it as no path
            if self.paths[self._current_path][0] == (row, col):
                self.grid[row][col] = (self._current_path, 0, 0)
            # Else, it's the other point, so restart the path
            else:
                r, c = self.paths[self._current_path].pop()
                self.grid[r][c] = (self._current_path, 0, 0)
                self.paths[self._current_path] = [(row, col)]
        # Else, continue the path from the given cell
        else:
            # Remove all path cells after the given cell
            while self.paths[self._current_path][-1] != (row, col):
                r, c = self.paths[self._current_path].pop()
                # Also mark the cell as empty in the grid
                self.grid[r][c] = (0, 0, 0)
            # Update the state of the cell so that it ends the current path
            position_last_cell = self.position_of(
                (row, col), self.paths[self._current_path][-2]
            )
            self.grid[row][col] = (self._current_path, position_last_cell, 5)

    def move(self, row: int = None, col: int = None) -> None:
        """Moves the path to the given cell.
        - If the cell is valid and adjacent to the last path cell,
        it adds the cell to the path.
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
        if (
            self.grid[row][col] != (0, 0, 0)
            and self.grid[row][col][0] != self._current_path
        ):
            return
        if not self.are_adjacent(self.paths[self._current_path][-1], (row, col)):
            return

        # If the cell is the other point, end the path
        r0, c0 = self.paths[self._current_path][0]
        if self.grid[row][col] == (self._current_path, 0, 0) and (r0, c0) != (row, col):
            # Update the state of the previous last cell so that it
            # continues the path to the new cell
            r, c = self.paths[self._current_path][-1]
            last_pos = self.grid[r][c][1]
            new_pos = self.position_of((r, c), (row, col))
            self.grid[r][c] = (self._current_path, last_pos, new_pos)
            # Add the new cell to the path, updated its state and end the path
            self.paths[self._current_path].append((row, col))
            self.grid[row][col] = (self._current_path, new_pos, 0)
            self.end_path()
        # If the cell is the same color as the path, backtrack
        elif self.grid[row][col][0] == self._current_path:
            r, c = self.paths[self._current_path].pop()
            # Mark the last cell as empty in the grid
            self.grid[r][c] = (0, 0, 0)
            # If the new last cell is the starting point, mark it as no path
            if len(self.paths[self._current_path]) == 1:
                r, c = self.paths[self._current_path][0]
                self.grid[r][c] = (self._current_path, 0, 0)
            # Else, mark it as the end of the path
            else:
                r, c = self.paths[self._current_path][-1]
                position_last_cell = self.position_of(
                    (r, c), self.paths[self._current_path][-2]
                )
                self.grid[r][c] = (self._current_path, position_last_cell, 5)
        else:
            # Update the state of the previous last cell so that it continues
            # the path to the new cell
            r, c = self.paths[self._current_path][-1]
            last_pos = self.grid[r][c][1]
            new_pos = self.position_of((r, c), (row, col))
            self.grid[r][c] = (self._current_path, last_pos, new_pos)
            # Add the new cell to the path and update its state
            self.paths[self._current_path].append((row, col))
            self.grid[row][col] = (self._current_path, new_pos, 5)

    def end_path(self) -> None:
        """Ends the current path."""

        if not self._is_pathing:
            return
        self._is_pathing = False
        self._current_path = None
