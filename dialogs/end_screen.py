"""
PyChess with minimax AI
Copyright (C) 2023 Artemii Saganenko, Alexander Kuksin
"""

from sys import exit

import pygame

from configuration.flowingconfig import *
from dialogs.fonts import main_text_font, time_text_font, help_text_font


def end_screen(win, text, total_time, restart_callback):
    total_time = int(total_time)
    format_time = f'{total_time // 60:d}:{total_time % 60:02d}'
    lines = (
        main_text_font.render(text, True, (255, 0, 0)),
        time_text_font.render(format_time, True, (255, 0, 0)),
        help_text_font.render("Press q - to quit and r - to restart", True, (255, 255, 255)),
    )

    # Centre the banner on the window, then centre the stack of lines inside it.
    line_gap = HEIGHT * 0.018
    banner_padding = HEIGHT * 0.05
    content_height = sum(line.get_height() for line in lines) + line_gap * (len(lines) - 1)
    banner_height = content_height + banner_padding * 2
    banner_top = (HEIGHT - banner_height) / 2

    pygame.draw.rect(win, (0, 0, 0), (0, banner_top, width, banner_height))
    line_y = banner_top + banner_padding
    for line in lines:
        win.blit(line, ((width - line.get_width()) / 2, line_y))
        line_y += line.get_height() + line_gap
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
                    restart_callback()
