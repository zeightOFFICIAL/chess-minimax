"""
PyChess with minimax AI
Copyright (C) 2023 Artemii Saganenko, Alexander Kuksin
"""

# ver 926
# pawn.py

from gameobjects.piece import Piece


class Pawn(Piece):
    piece_img = 3

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.first = True
        self.queen = False
        self.pawn = True

    def valid_moves(self, board):
        to_row = self.row
        to_col = self.col
        moves = []
        try:
            if self.color == "b":
                if to_row < 7:
                    next_point = board[to_row + 1][to_col]
                    if next_point == 0:
                        moves.append((to_row + 1, to_col))
                    if to_col < 7:
                        next_point = board[to_row + 1][to_col + 1]
                        if next_point != 0:
                            if next_point.color != self.color:
                                moves.append((to_row + 1, to_col + 1))
                    if to_col > 0:
                        next_point = board[to_row + 1][to_col - 1]
                        if next_point != 0:
                            if next_point.color != self.color:
                                moves.append((to_row + 1, to_col - 1))
                if self.first:
                    if to_row < 6:
                        next_point = board[to_row + 2][to_col]
                        next_point_two = board[to_row + 1][to_col]
                        if next_point == 0 and next_point_two == 0:
                            moves.append((to_row + 2, to_col))
            else:
                if to_row > 0:
                    next_point = board[to_row - 1][to_col]
                    if next_point == 0:
                        moves.append((to_row - 1, to_col))
                    if to_col < 7:
                        next_point = board[to_row - 1][to_col + 1]
                        if next_point != 0:
                            if next_point.color != self.color:
                                moves.append((to_row - 1, to_col + 1))
                    if to_col > 0:
                        next_point = board[to_row - 1][to_col - 1]
                        if next_point != 0:
                            if next_point.color != self.color:
                                moves.append((to_row - 1, to_col - 1))
                if self.first:
                    if to_row > 1:
                        next_point = board[to_row - 2][to_col]
                        next_point_two = board[to_row - 1][to_col]
                        if next_point == 0 and next_point_two == 0:
                            moves.append((to_row - 2, to_col))
        except IndexError as e:
            logging.warning("pawn class: IndexError %s", e)
        return moves
