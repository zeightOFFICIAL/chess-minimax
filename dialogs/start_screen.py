"""
PyChess with minimax AI
Copyright (C) 2023 Artemii Saganenko, Alexander Kuksin
"""

from sys import exit

import pygame

from configuration.flowingconfig import *
from dialogs.fonts import primal_help_font, secondary_help_font


def start_screen(win):
    primal_help_text = primal_help_font.render("Hotkeys", True, (255, 0, 0))
    first_help_line = secondary_help_font.render("q - to quit", True, (255, 255, 255))
    second_help_line = secondary_help_font.render("s - to surrender", True, (255, 255, 255))
    surrender_button_line = secondary_help_font.render("p - to vote for draw", True, (255, 255, 255))
    pygame.draw.rect(win, (0, 0, 0), (-1, -1, width + 1, width + 1))
    win.blit(primal_help_text, ((width - primal_help_text.get_width()) / 2, width * 0.3))
    win.blit(first_help_line, (width * 0.4, width * 0.4))
    win.blit(second_help_line, (width * 0.4, width * 0.45))
    if game_mode != 1:
        win.blit(surrender_button_line, (width * 0.4, width * 0.5))
    pygame.time.set_timer(pygame.USEREVENT + 1, freeze_time * 1000 + 1)
    pygame.display.update()
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.USEREVENT + 1:
                run = False
