import os
import pygame
from pygame.locals import *
from utils import config, utils

class GameOptions:
    """A class to replace command line arguments"""
    def __init__(self):
        self.solve = False
        self.debug = False
        self.file = None
        self.level = None  # Will be set by level selection screen
        self.random = False
        self.rows = None
        self.cols = None
        self.points = None
        self.colorblind_mode = "normal"  # Options: "normal", "protanopia", "deuteranopia", "tritanopia"


def level_selection_screen():
    """Display a level selection screen and return the chosen level"""
    pygame.init()
    screen = pygame.display.set_mode((600, 480))
    pygame.display.set_caption("Level Selection")

    # Load levels
    try:
        levels = utils.load_grid_config(os.path.join(config.DATA_DIR, "levels.json"))
        total_levels = len(levels)
    except Exception as e:
        print(f"Error loading levels: {e}")
        pygame.quit()
        return None

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    BLUE = (0, 120, 255)

    # Fonts
    font_title = pygame.font.SysFont(None, 48)
    font_text = pygame.font.SysFont(None, 36)
    font_small = pygame.font.SysFont(None, 24)

    selected_level = 1
    input_active = False
    input_text = str(selected_level)

    # Buttons
    button_width, button_height = 150, 50
    start_button = pygame.Rect((600 - button_width) // 2, 380, button_width, button_height)

    # Colorblind options
    cb_options = ["normal", "protanopia", "deuteranopia", "tritanopia"]
    cb_labels = {
        "normal": "Normal Vision",
        "protanopia": "Protanopia (Red-Blind)",
        "deuteranopia": "Deuteranopia (Green-Blind)",
        "tritanopia": "Tritanopia (Blue-Yellow Blind)"
    }
    cb_index = 0
    cb_button_width = 360
    cb_button_height = 60
    cb_button = pygame.Rect((600 - cb_button_width) // 2, 230, cb_button_width, cb_button_height)

    running = True
    while running:
        screen.fill(WHITE)

        # Title
        title = font_title.render("Level Selection", True, BLACK)
        screen.blit(title, ((600 - title.get_width()) // 2, 30))

        # Level prompt
        level_prompt = font_text.render(f"Choose Level (1-{total_levels}):", True, BLACK)
        screen.blit(level_prompt, (100, 100))

        # Level input box
        pygame.draw.rect(screen, BLUE if input_active else GRAY, (350, 100, 150, 40), 2)
        input_surface = font_text.render(input_text, True, BLACK)
        screen.blit(input_surface, (360, 105))

        # Colorblind mode selector (larger)
        pygame.draw.rect(screen, BLUE, cb_button)
        cb_text = font_small.render(f"Vision Mode: {cb_labels[cb_options[cb_index]]}", True, WHITE)
        screen.blit(cb_text, (cb_button.x + (cb_button_width - cb_text.get_width()) // 2,
                              cb_button.y + (cb_button_height - cb_text.get_height()) // 2))

        # Start button
        pygame.draw.rect(screen, BLUE, start_button)
        start_text = font_text.render("Start Game", True, WHITE)
        screen.blit(start_text, (start_button.x + (button_width - start_text.get_width()) // 2,
                                 start_button.y + (button_height - start_text.get_height()) // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return None

            elif event.type == MOUSEBUTTONDOWN:
                if pygame.Rect(350, 100, 150, 40).collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False

                if cb_button.collidepoint(event.pos):
                    cb_index = (cb_index + 1) % len(cb_options)

                if start_button.collidepoint(event.pos):
                    options = GameOptions()
                    try:
                        level_num = int(input_text)
                        if 1 <= level_num <= total_levels:
                            options.level = level_num
                            options.colorblind_mode = cb_options[cb_index]
                        else:
                            error_font = pygame.font.SysFont(None, 24)
                            error_text = error_font.render(f"Level must be between 1 and {total_levels}", True, (255, 0, 0))
                            screen.blit(error_text, (250, 150))
                            pygame.display.flip()
                            pygame.time.wait(1500)
                            continue
                    except ValueError:
                        error_font = pygame.font.SysFont(None, 24)
                        error_text = error_font.render("Please enter a valid level number", True, (255, 0, 0))
                        screen.blit(error_text, (250, 150))
                        pygame.display.flip()
                        pygame.time.wait(1500)
                        continue

                    pygame.quit()
                    return options

            elif event.type == KEYDOWN:
                if input_active:
                    if event.key == K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.unicode.isdigit():
                        input_text += event.unicode

    pygame.quit()
    return None

