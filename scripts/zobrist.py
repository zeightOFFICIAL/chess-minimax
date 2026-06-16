"""
PyChess with minimax AI
Copyright (C) 2023 Artemii Saganenko, Alexander Kuksin
"""

# ver 918
# zobrist.py

import random

_PIECE_TYPES = 6
_COLORS = 2
_SQUARES = 64

_rng = random.Random(42)
_ZOBRIST_TABLE = [[[_rng.getrandbits(64) for _ in range(_SQUARES)] for _ in range(_COLORS)] for _ in range(_PIECE_TYPES)]


def hash_board(board_2d):
    h = 0
    for row in range(8):
        for col in range(8):
            piece = board_2d[row][col]
            if piece != 0:
                sq = row * 8 + col
                color_idx = 0 if piece.color == "w" else 1
                h ^= _ZOBRIST_TABLE[piece.piece_img][color_idx][sq]
    return h


def hash_after_move(current_hash, board_2d, from_sq, to_sq):
    from_row, from_col = divmod(from_sq, 8)
    to_row, to_col = divmod(to_sq, 8)
    piece = board_2d[from_row][from_col]
    captured = board_2d[to_row][to_col]

    color_idx = 0 if piece.color == "w" else 1
    piece_type = piece.piece_img

    h = current_hash
    h ^= _ZOBRIST_TABLE[piece_type][color_idx][from_sq]
    if captured != 0:
        capt_color = 0 if captured.color == "w" else 1
        h ^= _ZOBRIST_TABLE[captured.piece_img][capt_color][to_sq]
    h ^= _ZOBRIST_TABLE[piece_type][color_idx][to_sq]
    return h
