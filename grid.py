from pprint import pprint
from utils.values import *
import random
import pprint


class Grid:
    """Represents the grid of a game. It is a rows * size matrix of integers,
    where each integer represents a point type. 0 means empty tile"""

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

        # Create grid with 0s
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        # Set starting points
        self._initialize_grid()

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
        """Initialize grid with the starting points"""

        for i in range(self.points):
            for row, col in self.starting_points[i]:
                self.grid[row][col] = i + 1

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


g = Grid(5, 5, 3)
pprint.pprint(g.grid)
pprint.pprint(g.starting_points)
