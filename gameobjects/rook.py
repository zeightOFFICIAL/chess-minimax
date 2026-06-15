"""
PyChess with minimax AI
Copyright (C) 2023 Artemii Saganenko, Alexander Kuksin
"""

# ver 917
# rook.py

from gameobjects.piece import Piece


class Rook(Piece):
    piece_img = 5

    def valid_moves(self, board):
        to_row = self.row
        to_col = self.col
        moves = []
        for x in range(to_row - 1, -1, -1):
            next_point = board[x][to_col]
            if next_point == 0:
                moves.append((to_col, x))
            elif next_point.color != self.color:
                moves.append((to_col, x))
                break
            else:
                break
        for x in range(to_row + 1, 8, 1):
            next_point = board[x][to_col]
            if next_point == 0:
                moves.append((to_col, x))
            elif next_point.color != self.color:
                moves.append((to_col, x))
                break
            else:
                break
        for x in range(to_col - 1, -1, -1):
            next_point = board[to_row][x]
            if next_point == 0:
                moves.append((x, to_row))
            elif next_point.color != self.color:
                moves.append((x, to_row))
                break
            else:
                break
        for x in range(to_col + 1, 8, 1):
            next_point = board[to_row][x]
            if next_point == 0:
                moves.append((x, to_row))
            elif next_point.color != self.color:
                moves.append((x, to_row))
                break
            else:
                break
        return moves
