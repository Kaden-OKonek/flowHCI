from queue import PriorityQueue

from grid import Grid
from utils import config


class Solver:
    """Solver that solves the grid of a game. It receives a grid
    and attempts to solve it. However, it does not guarantee a
    solution.

    The solve algorithm is based on the A* search algorithm.
    """

    def __init__(self, grid: Grid) -> None:
        """Initializes the solver with a grid.

        Args:
            grid (Grid): The grid to solve. It must be a valid grid.
        """

        self.grid = grid
        # Each point-pair has an added cost for the paths it can take
        self.added_costs = [
            [[0 for _ in range(self.grid.cols)] for _ in range(self.grid.rows)]
            for _ in range(self.grid.qpoints)
        ]
        # Each point-pair has a dictionary of tried paths
        # (Attempted paths that didn't reach a solution)
        self.tried_paths = [{} for _ in range(self.grid.qpoints)]

        # The added cost of running a path is enough to encourage
        # the algorithm to try different paths the next iteration
        self.ADDED_COST = self.grid.rows * self.grid.cols

    def _get_neighbors(
        self, point: int, cell: tuple[int, int]
    ) -> list[tuple[int, int]]:
        """Calculates the valid neighbors of a cell.

        Args:
            point (int): The point-pair index of the cell
            cell (tuple[int, int]): The cell to get the neighbors of

        Returns:
            list[tuple[int, int]]: The neighbors of the cell"""

        # Neighbors in N, S, E, W directions
        pos_neighbors = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        neighbors = [(cell[0] + pos[0], cell[1] + pos[1]) for pos in pos_neighbors]

        # Remove neighbors that are out of bounds or that aren't empty or the end point
        return [
            neighbor
            for neighbor in neighbors
            if (
                0 <= neighbor[0] < self.grid.rows
                and 0 <= neighbor[1] < self.grid.cols
                and (
                    self.grid.grid[neighbor[0]][neighbor[1]][0] == 0
                    or neighbor == self.grid.points[point][1]
                )
            )
        ]

    def _distance_between(self, cell1: tuple[int, int], cell2: tuple[int, int]) -> int:
        """Calculates the manhattan distance between two cells on the grid.

        Args:
            cell1 (tuple[int, int]): The first cell
            cell2 (tuple[int, int]): The second cell

        Returns:
            int: The distance between the two cells"""

        return abs(cell1[0] - cell2[0]) + abs(cell1[1] - cell2[1])

    def _get_heuristic(self, cell1: tuple[int, int], cell2: tuple[int, int]) -> int:
        """Calculates the heuristic cost between two cells on the grid. Currently,
        the heuristic is the manhattan distance between the cells.

        Args:
            cell1 (tuple[int, int]): The first cell
            cell2 (tuple[int, int]): The second cell

        Returns:
            int: The heuristic cost between the two cells"""

        return self.distance_between(cell1, cell2)

    def add_costs(self, point: int, path: list[tuple[int, int]]) -> None:
        """Adds costs to the grid for a path.

        Args:
            point (int): The point-pair index of the path
            path (list[tuple[int, int]]): The path to add costs to"""

        for cell in path[1:-1]:  # exclude start and end cells
            self.added_costs[point][cell[0]][cell[1]] += self.ADDED_COST

    def restart_costs(self, point: int) -> None:
        """Resets the added costs for a point-pair.

        Args:
            point (int): The point-pair index"""

        self.added_costs[point] = [
            [0 for _ in range(self.grid.cols)] for _ in range(self.grid.rows)
        ]

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

        # Get the path from the visited dictionary
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = visited[current][1]

        # Add cost to the cells in the path
        self.add_costs(point, path)

        return path[::-1]  # reverse the path

    def flatten_path(self, path: list[tuple[int, int]]) -> int:
        """Converts a path into a hash for quick comparisons.

        Args:
            path (list[tuple[int, int]]): The path to flatten

        Returns:
            int: The flattened path"""

        return hash("".join([str(cell) for cell in path]))

    def restart_point(self, point: int) -> None:
        """Resets the added costs and tried paths for a point-pair.

        Args:
            point (int): The point-pair index"""

        self.restart_costs(point)
        self.tried_paths[point] = {}
        self.grid.remove_path(point)

    def is_repeating(self, tried_paths: list[int]) -> bool:
        """Checks if a sequence of trieds paths is repeating. This is done by
        executing a sliding window algorithm from size 1 to (1 / REPEATING WINDOW)
        the length of the sequence. The check is done by comparing if the window
        occurs WINDOW_REPETITION times at the end of the sequence.

        Args:
            tried_paths (list[int]): The list of tried paths

        Returns:
            bool: True if the sequence is repeating, False otherwise"""

        # if the sequence is 1 2 3 4 5 6 7 8 9
        # WINDOW_REPETITION = 3
        # and the current window size is 3
        # then the checked windows will be
        # 1 2 3 [4 5 6] [7 8 9]
        # [1 2 3] [4 5 6] 7 8 9
        # if they are all equal, then the sequence is repeating
        # otherwise, they sequence is not repeating at the current window size

        if len(tried_paths) < config.WINDOW_REPETITION:
            return False

        for window_size in range(1, (len(tried_paths) // config.WINDOW_REPETITION) + 1):

            repeating = True
            for i in range(config.WINDOW_REPETITION - 1):
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

    def print_grid(self, tabbed=False) -> None:
        """Prints the grid to the console"""

        if tabbed:
            for row in self.grid.grid:
                print("\t", row)
        else:
            for row in self.grid.grid:
                print(row)
        print()

    def solve(self, debug=False) -> bool:
        """Solves the grid. It does so by finding the best path for each point-pair.
        The paths are solved in order and the algorithm may backtrack if it can't
        find a path for the current point-pair. The algorithm may also backtrack if
        it detects that it is repeating itself. The algorithm stops when the grid is
        fully solved (progress is 1) or if it wasn't able to find a solution.

        Args:
            debug (bool, optional): If True, the algorithm will print debug information.
                Defaults to False.

        Returns:
            bool: True if the grid was solved, False otherwise"""

        point = 0  # the current point-pair index
        self.print_grid() if debug else None

        while True:
            print("Solving point:", point + 1) if debug else None

            # Remove path of the current point-pair
            self.grid.remove_path(point)

            # Find a path for the current point-pair
            path = self.solve_point(point)

            if len(path) == 0:
                print("No path found, backtracking...\n") if debug else None

                # If there is no path, backtrack to the previous point
                self.restart_point(point)
                point -= 1
                # If there is no previous point, there is no solution
                if point < 0:
                    print(
                        "The algorithm wasn't able to find a solution"
                    ) if debug else None
                    return False
                continue

            flattened_path = self.flatten_path(path)
            print("Found path:", flattened_path) if debug else None

            # If the path has already been tried, find a new path
            tried_paths = [flattened_path]
            repeating = False
            repeats = 0
            while flattened_path in self.tried_paths[point]:
                repeats += 1

                print(
                    "\tPath already tried\n\n\tContinue solving point:", point + 1
                ) if debug else None

                path = self.solve_point(point)
                flattened_path = self.flatten_path(path)
                tried_paths.append(flattened_path)

                print("\tFound path:", flattened_path) if debug else None

                if self.is_repeating(tried_paths) or repeats > config.MAX_REPETITIONS:
                    print(
                        "\n\tPath finding is repeating, backtracking...\n"
                    ) if debug else None

                    repeating = True
                    self.restart_point(point)
                    point -= 1
                    # If there is no previous point, there is no solution
                    if point < 0:
                        print(
                            "The algorithm wasn't able to find a solution"
                        ) if debug else None
                        return False
                    break

            if repeating:
                continue

            # Add the path to the tried paths
            self.tried_paths[point][flattened_path] = True

            # Add the path to the grid
            self.grid.add_path(path)

            self.print_grid() if debug else None

            # Check if the grid is solved
            if self.grid.progress() == 1:
                return True

            # Move to the next point
            point += 1

            # If the point is out of bounds, the algorithm found no solution
            if point >= self.grid.qpoints:
                print("The algorithm wasn't able to find a solution") if debug else None
                return False
