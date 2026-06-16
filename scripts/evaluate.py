"""
PyChess with minimax AI
Copyright (C) 2023 Artemii Saganenko, Alexander Kuksin
"""

# ver 918
# evaluate.py

from numpy import flipud

# Piece-square tables (white's perspective, row 0 = rank 8)
_PAWN_TABLE = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5, 5, 10, 25, 25, 10, 5, 5],
    [0, 0, 0, 20, 20, 0, 0, 0],
    [5, -5, -10, 0, 0, -10, -5, 5],
    [5, 10, 10, -20, -20, 10, 10, 5],
    [0, 0, 0, 0, 0, 0, 0, 0]
]
_KNIGHT_TABLE = [
    [-50, -40, -30, -30, -30, -30, -40, -50],
    [-40, -20, 0, 0, 0, 0, -20, -40],
    [-30, 0, 10, 15, 15, 10, 0, -30],
    [-30, 5, 15, 20, 20, 15, 5, -30],
    [-30, 0, 15, 20, 20, 15, 0, -30],
    [-30, 5, 10, 15, 15, 10, 5, -30],
    [-40, -20, 0, 5, 5, 0, -20, -40],
    [-50, -40, -30, -30, -30, -30, -40, -50]
]
_BISHOP_TABLE = [
    [-20, -10, -10, -10, -10, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 10, 10, 5, 0, -10],
    [-10, 5, 5, 10, 10, 5, 5, -10],
    [-10, 0, 10, 10, 10, 10, 0, -10],
    [-10, 10, 10, 10, 10, 10, 10, -10],
    [-10, 5, 0, 0, 0, 0, 5, -10],
    [-20, -10, -10, -10, -10, -10, -10, -20]
]
_ROOK_TABLE = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [5, 10, 10, 10, 10, 10, 10, 5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [-5, 0, 0, 0, 0, 0, 0, -5],
    [0, 0, 0, 5, 5, 0, 0, 0]
]
_QUEEN_TABLE = [
    [-20, -10, -10, -5, -5, -10, -10, -20],
    [-10, 0, 0, 0, 0, 0, 0, -10],
    [-10, 0, 5, 5, 5, 5, 0, -10],
    [-5, 0, 5, 5, 5, 5, 0, -5],
    [0, 0, 5, 5, 5, 5, 0, -5],
    [-10, 5, 5, 5, 5, 5, 0, -10],
    [-10, 0, 5, 0, 0, 0, 0, -10],
    [-20, -10, -10, -5, -5, -10, -10, -20]
]
_KING_TABLE = [
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-30, -40, -40, -50, -50, -40, -40, -30],
    [-20, -30, -30, -40, -40, -30, -30, -20],
    [-10, -20, -20, -20, -20, -20, -20, -10],
    [20, 20, 0, 0, 0, 0, 20, 20],
    [20, 30, 10, 0, 0, 10, 30, 20]
]

# Indexed by piece.piece_img: 0=Bishop, 1=King, 2=Knight, 3=Pawn, 4=Queen, 5=Rook
_MATERIAL = [330, 20000, 320, 100, 900, 500]

_WHITE_TABLES = [_BISHOP_TABLE, _KING_TABLE, _KNIGHT_TABLE, _PAWN_TABLE, _QUEEN_TABLE, _ROOK_TABLE]
_BLACK_TABLES = [flipud(t) for t in _WHITE_TABLES]


def evaluate_board_advanced(board, color):
    white_score = 0
    black_score = 0
    for row in range(8):
        for col in range(8):
            piece = board.board[row][col]
            if piece != 0:
                idx = piece.piece_img
                if piece.color == "b":
                    black_score += _MATERIAL[idx] + _BLACK_TABLES[idx][row][col]
                else:
                    white_score += _MATERIAL[idx] + _WHITE_TABLES[idx][row][col]
    return white_score - black_score if color == "w" else black_score - white_score


def evaluate_board(board, color):
    white_score = 0
    black_score = 0
    for row in range(8):
        for col in range(8):
            piece = board.board[row][col]
            if piece != 0:
                val = _MATERIAL[piece.piece_img]
                if piece.color == "b":
                    black_score += val
                else:
                    white_score += val
    return white_score - black_score if color == "w" else black_score - white_score


def mvv_lva_score(board, from_pos, to_pos):
    from_row, from_col = from_pos
    to_row, to_col = to_pos
    attacker = board.board[from_row][from_col]
    victim = board.board[to_row][to_col]
    if victim == 0:
        return -1
    return _MATERIAL[victim.piece_img] - 0.1 * _MATERIAL[attacker.piece_img]
