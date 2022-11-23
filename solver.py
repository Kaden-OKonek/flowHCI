from queue import PriorityQueue
import os, sys
from utils import config, utils

level_num = sys.argv[1]

levels = utils.load_grid_config(os.path.join(config.DATA_DIR, "levels.json"))
level = levels[int(level_num)]

# grid
grid = [[0 for _ in range(level["cols"])] for _ in range(level["rows"])]

# transform the points from list to tuples
points = [[tuple(point) for point in pair] for pair in level["points"]]

# draw the points on the grid
for i in range(level["qpoints"]):
    grid[points[i][0][0]][points[i][0][1]] = i + 1
    grid[points[i][1][0]][points[i][1][1]] = i + 1


class Grid:
    def __init__(self, grid, points):
        self.grid = grid
        self.points = points
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.num_points = len(points)
        self.paths = [[] for _ in range(self.num_points)]

    def progress(self):
        progress = 0
        for path in self.paths:
            if len(path) > 1:
                progress += len(path)
        return progress / (self.rows * self.cols)

    def draw_path(self, point):
        path = self.paths[point]
        for cell in path:
            self.grid[cell[0]][cell[1]] = point + 1

    def erase_path(self, point):
        path = self.paths[point]
        for cell in path[1:-1]:
            self.grid[cell[0]][cell[1]] = 0


def print_matrix(matrix, tabbed=False):
    if tabbed:
        for row in matrix:
            print("\t", row)
    else:
        for row in matrix:
            print(row)
    print()


class Solver:
    def __init__(self, grid: Grid):
        self.grid = grid
        # each point-pair has an added costs matrix filled with 0s
        self.added_costs = [
            [[0 for _ in range(self.grid.cols)] for _ in range(self.grid.rows)]
            for _ in range(self.grid.num_points)
        ]
        # each point-pair has a dict of tried paths
        self.tried_paths = [{} for _ in range(grid.num_points)]

        self.ADDED_COST = self.grid.rows * self.grid.cols
        self.REPEATING_WINDOW = 3
        self.MAX_REPEATS = 1000

    def get_neighbors(self, point: int, cell: tuple[int, int]) -> list[tuple[int, int]]:
        """Gets the valid neighbors of a cell.

        Args:
            point (int): The point-pair index of the cell
            cell (tuple[int, int]): The cell to get the neighbors of

        Returns:
            list[tuple[int, int]]: The neighbors of the cell"""

        # neighbors in N, S, E, W directions
        pos_neighbors = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        neighbors = [(cell[0] + pos[0], cell[1] + pos[1]) for pos in pos_neighbors]

        # remove neighbors that are out of bounds or that aren't 0s or the end point
        return [
            neighbor
            for neighbor in neighbors
            if (
                0 <= neighbor[0] < self.grid.rows
                and 0 <= neighbor[1] < self.grid.cols
                and (
                    self.grid.grid[neighbor[0]][neighbor[1]] == 0
                    or neighbor == self.grid.points[point][1]
                )
            )
        ]

    def distance_between(self, cell1: tuple[int, int], cell2: tuple[int, int]) -> int:
        """Calculates the manhattan distance between two cells on the grid.

        Args:
            cell1 (tuple[int, int]): The first cell
            cell2 (tuple[int, int]): The second cell

        Returns:
            int: The distance between the two cells"""

        return abs(cell1[0] - cell2[0]) + abs(cell1[1] - cell2[1])

    def heuristic(self, cell1: tuple[int, int], cell2: tuple[int, int]) -> int:
        """Calculates the heuristic cost between two cells on the grid.

        Args:
            cell1 (tuple[int, int]): The first cell
            cell2 (tuple[int, int]): The second cell

        Returns:
            int: The heuristic cost between the two cells"""

        return self.distance_between(cell1, cell2)

    def flatten_path(self, path: list[tuple[int, int]]) -> int:
        """Converts a path into a hash for quick comparisons.

        Args:
            path (list[tuple[int, int]]): The path to flatten

        Returns:
            int: The flattened path"""

        return hash("".join([str(cell) for cell in path]))

    def add_costs(self, point: int, path: list[tuple[int, int]]) -> None:
        """Adds costs to the grid for a path.

        Args:
            point (int): The point-pair index of the path
            path (list[tuple[int, int]]): The path to add costs to"""

        for cell in path[1:-1]:
            self.added_costs[point][cell[0]][cell[1]] += self.ADDED_COST

    def solve_point(self, point: int) -> list[tuple[int, int]]:
        """Finds the best path for a point-pair. It does so by using A*.
        The calculated path adds costs to the grid.

        Args:
            point (int): The point-pair index to solve

        Returns:
            list[tuple[int, int]]: The best path for the point-pair"""

        start = self.grid.points[point][0]
        end = self.grid.points[point][1]

        # priority queue of cells to visit (f_cost, cell)
        queue = PriorityQueue()
        queue.put((0, start))

        # dictionary of cells that have been visited
        visited = dict()
        visited[start] = (0, None)

        while not queue.empty():
            current = queue.get()[1]
            if current == end:
                break

            for neighbor in self.get_neighbors(point, current):
                g_cost = (
                    visited[current][0]
                    + 1
                    + self.added_costs[point][neighbor[0]][neighbor[1]]
                )
                h_cost = self.heuristic(neighbor, end)
                f_cost = g_cost + h_cost

                if neighbor in visited and visited[neighbor][0] <= g_cost:
                    continue

                queue.put(
                    (
                        f_cost,
                        neighbor,
                    )
                )
                visited[neighbor] = (
                    g_cost,
                    current,
                )

        if end not in visited:
            return []

        # get the path from the visited dictionary
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = visited[current][1]

        # Add cost to the cells in the path
        self.add_costs(point, path)

        return path[::-1]

    def restart_costs(self, point: int) -> None:
        """Resets the added costs for a point-pair.

        Args:
            point (int): The point-pair index"""

        self.added_costs[point] = [
            [0 for _ in range(self.grid.cols)] for _ in range(self.grid.rows)
        ]

    def restart_point(self, point: int) -> None:
        """Resets the added costs and tried paths for a point-pair.

        Args:
            point (int): The point-pair index"""

        self.restart_costs(point)
        self.tried_paths[point] = {}
        self.grid.erase_path(point)
        self.grid.paths[point] = []

    def is_repeating(self, tried_paths: list[int]) -> bool:
        """Checks if a sequence of trieds paths is repeating. This is done by
        executing a sliding window algorithm from size 1 to (1 / REPEATING WINDOW)
        the length of the sequence. The check is done by comparing if the window
        occurs REPEATING_WINDOW times at the end of the sequence.

        Args:
            tried_paths (list[int]): The list of tried paths

        Returns:
            bool: True if the sequence is repeating, False otherwise"""

        # if the sequence is 1 2 3 4 5 6 7 8 9
        # REPEATING_WINDOW = 3
        # and the current window size is 3
        # then the checked windows will be
        # 1 2 3 [4 5 6] [7 8 9]
        # [1 2 3] [4 5 6] 7 8 9
        # if they are all equal, then the sequence is repeating
        # otherwise, they sequence is not repeating at the current window size

        if len(tried_paths) < self.REPEATING_WINDOW:
            return False

        for window_size in range(1, (len(tried_paths) // self.REPEATING_WINDOW) + 1):

            repeating = True
            for i in range(self.REPEATING_WINDOW - 1):
                window1 = (
                    tried_paths[-(i + 1) * window_size :]
                    if i == 0
                    else tried_paths[-(i + 1) * window_size : -i * window_size]
                )
                window2 = tried_paths[-(i + 2) * window_size : -(i + 1) * window_size]

                if window1 != window2:
                    repeating = False
                    break

            if repeating:
                return True

        return False

    def solve(self) -> None:
        """Solves all the point-pairs."""

        solved = False
        point = 0

        print_matrix(self.grid.grid)

        while not solved:
            # remove path
            self.grid.erase_path(point)
            self.grid.paths[point] = []

            print("Solving point", point + 1)
            # Find a path for the current point
            path = self.solve_point(point)

            if len(path) == 0:
                print("No path found, backtracking")
                print()

                # If there is no path, backtrack to the previous point
                self.restart_point(point)
                point -= 1

                # If there is no previous point, there is no solution
                if point < 0:
                    print("No solution")
                    return False

                continue

            # If the path has already been tried, find a new path
            flattened_path = self.flatten_path(path)
            print("Found path", flattened_path)

            tried_paths = [flattened_path]
            repeating = False
            repeats = 0
            while flattened_path in self.tried_paths[point]:
                repeats += 1

                print("\tPath already tried")
                print()
                print("\tContinue solving point", point + 1)
                path = self.solve_point(point)
                flattened_path = self.flatten_path(path)
                print("\tFound path", flattened_path)

                tried_paths.append(flattened_path)
                if self.is_repeating(tried_paths) or repeats > self.MAX_REPEATS:
                    print("\tPath finding is repeating, backtracking")
                    print()
                    self.restart_point(point)
                    point -= 1
                    repeating = True

                    # If there is no previous point, there is no solution
                    if point < 0:
                        print("No solution")
                        return False
                    break

            if repeating:
                continue

            # Add the path to the tried paths
            self.tried_paths[point][flattened_path] = True

            # Add the path to the grid
            self.grid.paths[point] = path.copy()
            self.grid.draw_path(point)

            print_matrix(self.grid.grid)

            # Check if the grid is solved
            if self.grid.progress() == 1:
                solved = True
                continue

            # Move to the next point
            point += 1

            # If the point is out of bounds, restart
            if point >= self.grid.num_points:
                point = 0


solver = Solver(Grid(grid, points))

solver.solve()
