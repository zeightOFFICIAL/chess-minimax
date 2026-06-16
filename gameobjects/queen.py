"""
PyChess with minimax AI
Copyright (C) 2023 Artemii Saganenko, Alexander Kuksin
"""

# ver 917
# queen.py

from gameobjects.piece import Piece


class Queen(Piece):
    piece_img = 4

    def valid_moves(self, board):
        to_row = self.row
        to_col = self.col
        moves = []
        left_strafe = to_col + 1
        right_strafe = to_col - 1
        for distance in range(to_row - 1, -1, -1):
            if left_strafe < 8:
                next_point = board[distance][left_strafe]
                if next_point == 0:
                    moves.append((distance, left_strafe))
                elif next_point.color != self.color:
                    moves.append((distance, left_strafe))
                    break
                else:
                    left_strafe = 9
            left_strafe += 1
        for distance in range(to_row - 1, -1, -1):
            if right_strafe > -1:
                next_point = board[distance][right_strafe]
                if next_point == 0:
                    moves.append((distance, right_strafe))
                elif next_point.color != self.color:
                    moves.append((distance, right_strafe))
                    break
                else:
                    right_strafe = -1
            right_strafe -= 1
        left_strafe = to_col + 1
        right_strafe = to_col - 1
        for distance in range(to_row + 1, 8):
            if left_strafe < 8:
                next_point = board[distance][left_strafe]
                if next_point == 0:
                    moves.append((distance, left_strafe))
                elif next_point.color != self.color:
                    moves.append((distance, left_strafe))
                    break
                else:
                    left_strafe = 9
            left_strafe += 1
        for distance in range(to_row + 1, 8):
            if right_strafe > -1:
                next_point = board[distance][right_strafe]
                if next_point == 0:
                    moves.append((distance, right_strafe))
                elif next_point.color != self.color:
                    moves.append((distance, right_strafe))
                    break
                else:
                    right_strafe = -1
            right_strafe -= 1
        for x in range(to_row - 1, -1, -1):
            next_point = board[x][to_col]
            if next_point == 0:
                moves.append((x, to_col))
            elif next_point.color != self.color:
                moves.append((x, to_col))
                break
            else:
                break
        for x in range(to_row + 1, 8, 1):
            next_point = board[x][to_col]
            if next_point == 0:
                moves.append((x, to_col))
            elif next_point.color != self.color:
                moves.append((x, to_col))
                break
            else:
                break
        for x in range(to_col - 1, -1, -1):
            next_point = board[to_row][x]
            if next_point == 0:
                moves.append((to_row, x))
            elif next_point.color != self.color:
                moves.append((to_row, x))
                break
            else:
                break
        for x in range(to_col + 1, 8, 1):
            next_point = board[to_row][x]
            if next_point == 0:
                moves.append((to_row, x))
            elif next_point.color != self.color:
                moves.append((to_row, x))
                break
            else:
                break
        return moves
