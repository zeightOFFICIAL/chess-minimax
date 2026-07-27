"""
PyChess with minimax AI
Copyright (C) 2023 Artemii Saganenko, Alexander Kuksin
"""

import pygame

from configuration.flowingconfig import width

# Uses pygame's bundled default font (not a SysFont lookup) so text renders
# identically regardless of which fonts happen to be installed on the host.
pygame.font.init()

player_time_font = pygame.font.Font(None, int(width * 0.022))
king_condition_font = pygame.font.Font(None, int(width * 0.033))

main_text_font = pygame.font.Font(None, int(width * 0.093))
time_text_font = pygame.font.Font(None, int(width * 0.04))
help_text_font = pygame.font.Font(None, int(width * 0.026))
secondary_help_font = pygame.font.Font(None, int(width * 0.04))
primal_help_font = pygame.font.Font(None, int(width * 0.053))
