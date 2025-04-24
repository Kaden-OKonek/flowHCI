import os
import sys

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from components.grid import Grid as Grid
from components.solver import Solver as Solver
from components import eventmanager, model, controller, view
from utils import config, utils
from level_selector import level_selection_screen


def run_game(options):
    """Run the game with the given options"""
    try:
        levels = utils.load_grid_config(os.path.join(config.DATA_DIR, "levels.json"))
    except Exception as e:
        print(f"Error loading levels: {e}")
        return False

    grid_config = None
    if options.file:
        try:
            grid_config = utils.load_grid_config(options.file)
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    elif options.level:
        if options.level < 1 or options.level > len(levels):
            print(f"Level not found, please choose a level between 1 and {len(levels)}")
            return False
        grid_config = levels[options.level - 1]
    elif options.random:
        if options.rows and options.cols and options.points:
            try:
                grid_config = Grid.create_random_config(
                    options.rows, options.cols, options.points
                )
            except Exception as e:
                print(f"Can't create random grid: {e}")
                return False
        else:
            print("Random grid needs rows, cols and points")
            return False

    grid = Grid.from_config(grid_config)
    print("Loaded configuration correctly\n")

    if options.solve:
        solver = Solver(grid)
        print("The solver is looking for a solution, this might take a while...\n")
        found_solution = solver.solve(options.debug)
        if found_solution:
            print("The solver found a solution!\n")
        else:
            print("The solver couldn't find a solution...\n")
            grid.restart()

    event_manager = eventmanager.EventManager()
    gamemodel = model.GameEngine(event_manager, grid)
    gamecontroller = controller.GameController(event_manager, gamemodel)
    gameview = view.GameView(event_manager, gamemodel)
    gamemodel.run()
    return True


if __name__ == "__main__":
    # Show level selection screen
    options = level_selection_screen()
    
    # If options were returned, run the game
    if options:
        run_game(options)
    else:
        print("Game cancelled")