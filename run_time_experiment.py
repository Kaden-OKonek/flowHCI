import os, sys, time

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from components.grid import Grid as Grid
from components.solver import Solver as Solver
from utils import config, utils


def do_experiment(grid: Grid, run_times: int = 3) -> float:
    """Run the experiment run_times times and return the average time."""

    total_time = 0
    for _ in range(run_times):
        grid.restart()
        solver = Solver(grid)

        start = time.time()
        solved = solver.solve()
        end = time.time()

        total_time += float(end - start)

        if not solved:
            return -1

    return total_time / float(run_times)


def main(argv):
    try:
        levels = utils.load_grid_config(os.path.join(config.DATA_DIR, "levels.json"))
    except Exception as e:
        print(e)
        sys.exit(1)

    grid_config = levels[int(argv[1]) - 1]
    grid = Grid.from_config(grid_config)

    average_time = do_experiment(grid)
    if average_time == -1:
        print("The solver couldn't find a solution...")
        sys.exit(1)

    print("Average time:", average_time)


if __name__ == "__main__":
    main(sys.argv)
