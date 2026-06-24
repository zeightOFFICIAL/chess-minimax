"""
PyChess with minimax AI
Copyright (C) 2023 Artemii Saganenko, Alexander Kuksin
"""

# ver 926
# piece.py


# libraries ============================================================================================================
import pygame
import sys, os

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

# resources ============================================================================================================
from configuration.flowingconfig import *

_BASE = "resources/images"
b_bishop = pygame.image.load(f"{_BASE}/b_bishop.png")
b_king = pygame.image.load(f"{_BASE}/b_king.png")
b_knight = pygame.image.load(f"{_BASE}/b_knight.png")
b_pawn = pygame.image.load(f"{_BASE}/b_pawn.png")
b_queen = pygame.image.load(f"{_BASE}/b_queen.png")
b_rook = pygame.image.load(f"{_BASE}/b_rook.png")
w_bishop = pygame.image.load(f"{_BASE}/w_bishop.png")
w_king = pygame.image.load(f"{_BASE}/w_king.png")
w_knight = pygame.image.load(f"{_BASE}/w_knight.png")
w_pawn = pygame.image.load(f"{_BASE}/w_pawn.png")
w_queen = pygame.image.load(f"{_BASE}/w_queen.png")
w_rook = pygame.image.load(f"{_BASE}/w_rook.png")
raw_select = pygame.image.load(f"{_BASE}/b_select.png")
raw_select_inv = pygame.image.load(f"{_BASE}/b2_select.png")
if visual_set != 0:
    _set_path = f"{_BASE}/{visual_set}"
    if os.path.isdir(_set_path):
        try:
            _b_bishop = pygame.image.load(f"{_set_path}/b_bishop.png")
            _b_king = pygame.image.load(f"{_set_path}/b_king.png")
            _b_knight = pygame.image.load(f"{_set_path}/b_knight.png")
            _b_pawn = pygame.image.load(f"{_set_path}/b_pawn.png")
            _b_queen = pygame.image.load(f"{_set_path}/b_queen.png")
            _b_rook = pygame.image.load(f"{_set_path}/b_rook.png")
            _w_bishop = pygame.image.load(f"{_set_path}/w_bishop.png")
            _w_king = pygame.image.load(f"{_set_path}/w_king.png")
            _w_knight = pygame.image.load(f"{_set_path}/w_knight.png")
            _w_pawn = pygame.image.load(f"{_set_path}/w_pawn.png")
            _w_queen = pygame.image.load(f"{_set_path}/w_queen.png")
            _w_rook = pygame.image.load(f"{_set_path}/w_rook.png")
            _raw_select = pygame.image.load(f"{_set_path}/b_select.png")
            _raw_select_inv = pygame.image.load(f"{_set_path}/b2_select.png")
            b_bishop, b_king, b_knight, b_pawn, b_queen, b_rook = (
                _b_bishop, _b_king, _b_knight, _b_pawn, _b_queen, _b_rook)
            w_bishop, w_king, w_knight, w_pawn, w_queen, w_rook = (
                _w_bishop, _w_king, _w_knight, _w_pawn, _w_queen, _w_rook)
            raw_select, raw_select_inv = _raw_select, _raw_select_inv
        except (FileNotFoundError, TypeError) as e:
            logging.warning("Load visual set %s: missing files, using defaults", visual_set)
    else:
        logging.warning("Load visual set %s: folder not found, using defaults", visual_set)
black_all_images = [b_bishop, b_king, b_knight, b_pawn, b_queen, b_rook]
white_all_images = [w_bishop, w_king, w_knight, w_pawn, w_queen, w_rook]
black_all_scaled = []
white_all_scaled = []

# scaling --------------------------------------------------------------------------------------------------------------
for piece_img in black_all_images:
    black_all_scaled.append(pygame.transform.smoothscale(piece_img, (CELL_SIZE_X, CELL_SIZE_Y)))
for piece_img in white_all_images:
    white_all_scaled.append(pygame.transform.smoothscale(piece_img, (CELL_SIZE_X, CELL_SIZE_Y)))
scaled_select = pygame.transform.smoothscale(raw_select, (CELL_SIZE_X, CELL_SIZE_Y))
scaled_select2 = pygame.transform.smoothscale(raw_select_inv, (CELL_SIZE_X, CELL_SIZE_Y))


# piece class ==========================================================================================================
class Piece:
    piece_img = -1
    start_x = TOP_LEFT[0]
    start_y = TOP_LEFT[1]

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.selected = False
        self.move_list = []
        self.king = False
        self.pawn = False
        self.queen = False

    def is_selected(self):
        return self.selected

    def update_valid_moves(self, board):
        self.move_list = self.valid_moves(board)

    def draw(self, win):
        if self.color == "w":
            this_piece_img = white_all_scaled[self.piece_img]
        else:
            this_piece_img = black_all_scaled[self.piece_img]
        if self.selected:
            moves = self.move_list
            for move in moves:
                x = self.start_x + (move[1] * BOTTOM_RIGHT[0] / 8) + (CELL_SIZE_Y // 2)
                y = self.start_y + (move[0] * BOTTOM_RIGHT[1] / 8) + (CELL_SIZE_Y // 2)
                if self.color == "w":
                    win.blit(scaled_select, (x - CELL_SIZE_X / 2, y - CELL_SIZE_Y / 2))
                if self.color == 'b':
                    win.blit(scaled_select2, (x - CELL_SIZE_X / 2, y - CELL_SIZE_Y / 2))
        x = self.start_x + (self.col * BOTTOM_RIGHT[0] / 8)
        y = self.start_y + (self.row * BOTTOM_RIGHT[1] / 8)
        if self.selected:
            if self.color == "w":
                this_piece_img = pygame.transform.smoothscale(white_all_images[self.piece_img],
                                                              (CELL_SIZE_Y + POP_INCREASING_SIZE,
                                                               CELL_SIZE_Y + POP_INCREASING_SIZE))
            if self.color == 'b':
                this_piece_img = pygame.transform.smoothscale(black_all_images[self.piece_img],
                                                              (CELL_SIZE_Y + POP_INCREASING_SIZE,
                                                               CELL_SIZE_Y + POP_INCREASING_SIZE))
            win.blit(this_piece_img, (x - POP_INCREASING_SIZE / 2, y - POP_INCREASING_SIZE / 2))
        else:
            win.blit(this_piece_img, (x, y))

    def change_pos(self, pos):
        self.row = pos[0]
        self.col = pos[1]

    def valid_moves(self, board):
        pass
