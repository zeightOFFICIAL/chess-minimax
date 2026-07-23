"""
PyChess with minimax AI
Copyright (C) 2023 Artemii Saganenko, Alexander Kuksin
"""

# end_screen.py

from sys import exit

import pygame

from configuration.flowingconfig import *
from dialogs.fonts import main_text_font, time_text_font, help_text_font


# FUNCTION to render last (end) screen. Displays time of game and the winner.
def end_screen(win, text, total_time):
    total_time = int(total_time)
    format_time = f'{total_time // 60:d}:{total_time % 60:02d}'
    text_render = main_text_font.render(text, True, (255, 0, 0))
    text_time = time_text_font.render(format_time, True, (255, 0, 0))
    text_help = help_text_font.render("Press q - to quit and r - to restart", True, (255, 255, 255))
    pygame.draw.rect(win, (0, 0, 0), (-1, width / 2 - text_render.get_height(), width + 1, width - width / 1.3))
    win.blit(text_render, (width / 2 - text_render.get_width() / 2, width / 2 - text_render.get_height()))
    win.blit(text_time, (width / 2 - text_time.get_width() / 2, width / 2))
    win.blit(text_help, (width / 2 - text_help.get_width() / 2, width / 2 + text_time.get_height() * 1.2))
    pygame.display.update()
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    logging.debug(
                        "End screen: Quit button is pressed.")
                    pygame.quit()
                    exit()
                if event.key == pygame.K_r:
                    logging.debug(
                        "End screen: Restart button is pressed.")
                    # Deferred import: game.py imports this module, so importing
                    # game at module load time would create a circular import.
                    import game
                    game.main()
