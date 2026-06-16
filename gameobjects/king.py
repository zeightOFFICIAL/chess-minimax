"""
PyChess with minimax AI
Copyright (C) 2023 Artemii Saganenko, Alexander Kuksin
"""

# ver 917
# king.py

from gameobjects.piece import Piece


class King(Piece):
    piece_img = 1

    def __init__(self, row, col, color):
        super().__init__(row, col, color)
        self.king = True

    def valid_moves(self, board):
        to_row = self.row
        to_col = self.col
        moves = []
        if to_row > 0:
            if to_col > 0:
                next_point = board[to_row - 1][to_col - 1]
                if next_point == 0:
                    moves.append((to_row - 1, to_col - 1))
                elif next_point.color != self.color:
                    moves.append((to_row - 1, to_col - 1))
            next_point = board[to_row - 1][to_col]
            if next_point == 0:
                moves.append((to_row - 1, to_col))
            elif next_point.color != self.color:
                moves.append((to_row - 1, to_col))
            if to_col < 7:
                next_point = board[to_row - 1][to_col + 1]
                if next_point == 0:
                    moves.append((to_row - 1, to_col + 1))
                elif next_point.color != self.color:
                    moves.append((to_row - 1, to_col + 1))
        if to_row < 7:
            if to_col > 0:
                next_point = board[to_row + 1][to_col - 1]
                if next_point == 0:
                    moves.append((to_row + 1, to_col - 1))
                elif next_point.color != self.color:
                    moves.append((to_row + 1, to_col - 1))
            next_point = board[to_row + 1][to_col]
            if next_point == 0:
                moves.append((to_row + 1, to_col))
            elif next_point.color != self.color:
                moves.append((to_row + 1, to_col))
            if to_col < 7:
                next_point = board[to_row + 1][to_col + 1]
                if next_point == 0:
                    moves.append((to_row + 1, to_col + 1))
                elif next_point.color != self.color:
                    moves.append((to_row + 1, to_col + 1))
        if to_col > 0:
            next_point = board[to_row][to_col - 1]
            if next_point == 0:
                moves.append((to_row, to_col - 1))
            elif next_point.color != self.color:
                moves.append((to_row, to_col - 1))
        if to_col < 7:
            next_point = board[to_row][to_col + 1]
            if next_point == 0:
                moves.append((to_row, to_col + 1))
            elif next_point.color != self.color:
                moves.append((to_row, to_col + 1))
        return moves
