"""
PyChess with minimax AI
Copyright (C) 2023 Artemii Saganenko, Alexander Kuksin
"""

# ver 917
# bishop.py

from gameobjects.piece import Piece


class Bishop(Piece):
    piece_img = 0

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
                    break
            else:
                break
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
                    break
            else:
                break
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
                    break
            else:
                break
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
                    break
            else:
                break
            right_strafe -= 1
        return moves
