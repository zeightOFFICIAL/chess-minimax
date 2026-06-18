"""
PyChess with minimax AI
Copyright (C) 2023 Artemii Saganenko, Alexander Kuksin
"""

# ver 926
# knight.py

from gameobjects.piece import Piece


class Knight(Piece):
    piece_img = 2

    def valid_moves(self, board):
        to_row = self.row
        to_col = self.col
        moves = []
        if to_row < 6 and to_col > 0:
            next_point = board[to_row + 2][to_col - 1]
            if next_point == 0:
                moves.append((to_row + 2, to_col - 1))
            elif next_point.color != self.color:
                moves.append((to_row + 2, to_col - 1))
        if to_row > 1 and to_col > 0:
            next_point = board[to_row - 2][to_col - 1]
            if next_point == 0:
                moves.append((to_row - 2, to_col - 1))
            elif next_point.color != self.color:
                moves.append((to_row - 2, to_col - 1))
        if to_row < 6 and to_col < 7:
            next_point = board[to_row + 2][to_col + 1]
            if next_point == 0:
                moves.append((to_row + 2, to_col + 1))
            elif next_point.color != self.color:
                moves.append((to_row + 2, to_col + 1))
        if to_row > 1 and to_col < 7:
            next_point = board[to_row - 2][to_col + 1]
            if next_point == 0:
                moves.append((to_row - 2, to_col + 1))
            elif next_point.color != self.color:
                moves.append((to_row - 2, to_col + 1))
        if to_row > 0 and to_col > 1:
            next_point = board[to_row - 1][to_col - 2]
            if next_point == 0:
                moves.append((to_row - 1, to_col - 2))
            elif next_point.color != self.color:
                moves.append((to_row - 1, to_col - 2))
        if to_row > 0 and to_col < 6:
            next_point = board[to_row - 1][to_col + 2]
            if next_point == 0:
                moves.append((to_row - 1, to_col + 2))
            elif next_point.color != self.color:
                moves.append((to_row - 1, to_col + 2))
        if to_row < 7 and to_col > 1:
            next_point = board[to_row + 1][to_col - 2]
            if next_point == 0:
                moves.append((to_row + 1, to_col - 2))
            elif next_point.color != self.color:
                moves.append((to_row + 1, to_col - 2))
        if to_row < 7 and to_col < 6:
            next_point = board[to_row + 1][to_col + 2]
            if next_point == 0:
                moves.append((to_row + 1, to_col + 2))
            elif next_point.color != self.color:
                moves.append((to_row + 1, to_col + 2))
        return moves
