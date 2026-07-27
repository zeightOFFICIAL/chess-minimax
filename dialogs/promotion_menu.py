"""
PyChess with minimax AI
Copyright (C) 2023 Artemii Saganenko, Alexander Kuksin
"""

from sys import exit

import pygame

from configuration.flowingconfig import width
from gameobjects.piece import white_all_images, black_all_images
from gameobjects.bishop import Bishop
from gameobjects.knight import Knight
from gameobjects.queen import Queen
from gameobjects.rook import Rook

# (piece class, piece_img index) - matches the ordering in gameobjects/piece.py's image lists
_CHOICES = [(Queen, 4), (Rook, 5), (Bishop, 0), (Knight, 2)]


# Blocks until the player clicks one of the four pieces, then returns its class.
def choose_promotion(win, color):
    images = white_all_images if color == "w" else black_all_images
    icon_size = width * 0.12
    spacing = width * 0.03
    total_width = len(_CHOICES) * icon_size + (len(_CHOICES) - 1) * spacing
    start_x = (width - total_width) / 2
    icon_y = (width - icon_size) / 2

    rects = []
    scaled_icons = []
    for i, (piece_class, img_index) in enumerate(_CHOICES):
        icon = pygame.transform.smoothscale(images[img_index], (icon_size, icon_size))
        x = start_x + i * (icon_size + spacing)
        rects.append(pygame.Rect(x, icon_y, icon_size, icon_size))
        scaled_icons.append(icon)

    pygame.draw.rect(win, (0, 0, 0), (0, 0, width, width))
    border_rect = (start_x - spacing, icon_y - spacing, total_width + spacing * 2, icon_size + spacing * 2)
    pygame.draw.rect(win, (255, 255, 255), border_rect, 2)
    for icon, rect in zip(scaled_icons, rects):
        win.blit(icon, rect.topleft)
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                for rect, (piece_class, _) in zip(rects, _CHOICES):
                    if rect.collidepoint(pos):
                        return piece_class
