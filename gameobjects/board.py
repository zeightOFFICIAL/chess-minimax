"""
PyChess with minimax AI
Copyright (C) 2023 Artemii Saganenko, Alexander Kuksin
"""

# ver 918
# board.py


# libraries ============================================================================================================
from configuration.flowingconfig import *
from gameobjects.bishop import Bishop
from gameobjects.king import King
from gameobjects.knight import Knight
from gameobjects.rook import Rook
from gameobjects.queen import Queen
from gameobjects.pawn import Pawn

# Convention: move_list entries are (row, col) matching board[row][col]


# chessboard class =====================================================================================================
# noinspection PyTypeChecker
# (PyCharm throws a warning considering unexpected value in 2d array. Class instead of '0' being integer)

class Board:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.board = [[0 for _ in range(8)] for _ in range(8)]
        self.set_start_normal()

    def set_start_normal(self):
        self.board[0][0] = Rook(0, 0, "b")
        self.board[0][1] = Knight(0, 1, "b")
        self.board[0][2] = Bishop(0, 2, "b")
        self.board[0][3] = Queen(0, 3, "b")
        self.board[0][4] = King(0, 4, "b")
        self.board[0][5] = Bishop(0, 5, "b")
        self.board[0][6] = Knight(0, 6, "b")
        self.board[0][7] = Rook(0, 7, "b")
        for board_line in range(0, 8):
            self.board[1][board_line] = Pawn(1, board_line, "b")

        self.board[7][0] = Rook(7, 0, "w")
        self.board[7][1] = Knight(7, 1, "w")
        self.board[7][2] = Bishop(7, 2, "w")
        self.board[7][3] = Queen(7, 3, "w")
        self.board[7][4] = King(7, 4, "w")
        self.board[7][5] = Bishop(7, 5, "w")
        self.board[7][6] = Knight(7, 6, "w")
        self.board[7][7] = Rook(7, 7, "w")
        for board_line in range(0, 8):
            self.board[6][board_line] = Pawn(6, board_line, "w")
        logging.debug("Set chessboard: figures are set to a normal chess game")

    # functions ========================================================================================================
    def update_moves(self):
        for row_index in range(self.rows):
            for col_index in range(self.cols):
                if self.board[row_index][col_index] != 0:
                    self.board[row_index][col_index].update_valid_moves(self.board)

    def draw(self, win):
        for row_index in range(self.rows):
            for col_index in range(self.cols):
                if self.board[row_index][col_index] != 0:
                    self.board[row_index][col_index].draw(win)

    def get_danger_moves(self, color):
        danger_moves = []
        for row_index in range(self.rows):
            for col_index in range(self.cols):
                if self.board[row_index][col_index] != 0:
                    if self.board[row_index][col_index].color != color:
                        for move in self.board[row_index][col_index].move_list:
                            danger_moves.append(move)
        return danger_moves

    def piece_at_the_end(self, color):
        if color == "w":
            white_end = 0
            for col_index in range(0, 8):
                if self.board[white_end][col_index] != 0:
                    if self.board[white_end][col_index].pawn:
                        self.board[white_end][col_index] = 0
                        self.board[white_end][col_index] = Queen(white_end, col_index, color)
        if color == "b":
            black_end = 7
            for col_index in range(0, 8):
                if self.board[black_end][col_index] != 0:
                    if self.board[black_end][col_index].pawn:
                        self.board[black_end][col_index] = 0
                        self.board[black_end][col_index] = Queen(black_end, col_index, color)

    def piece_is_checked(self, color):
        self.update_moves()
        danger_moves = self.get_danger_moves(color)
        king_pos = (-1, -1)
        for row_index in range(self.rows):
            for col_index in range(self.cols):
                if self.board[row_index][col_index] != 0:
                    if self.board[row_index][col_index].king and self.board[row_index][col_index].color == color:
                        king_pos = (row_index, col_index)
        if king_pos in danger_moves:
            logging.debug("Checked: %s-king is under check at (%d, %d)", color, king_pos[0], king_pos[1])
            return True
        return False

    def select(self, col, row, color):
        previous_select = (-1, -1)
        changed = False
        for row_index in range(self.rows):
            for col_index in range(self.cols):
                if self.board[row_index][col_index] != 0:
                    if self.board[row_index][col_index].selected:
                        previous_select = (row_index, col_index)
        if self.board[row][col] == 0 and previous_select != (-1, -1):
            moves = self.board[previous_select[0]][previous_select[1]].move_list
            if (row, col) in moves:
                changed = self.move(previous_select, (row, col), color)
            self.reset_selected()
        else:
            if previous_select == (-1, -1):
                self.reset_selected()
                if self.board[row][col] != 0 and self.board[row][col].color == color:
                    self.board[row][col].selected = True
            else:
                if self.board[previous_select[0]][previous_select[1]].color != self.board[row][col].color:
                    moves = self.board[previous_select[0]][previous_select[1]].move_list
                    if (row, col) in moves:
                        changed = self.move(previous_select, (row, col), color)
                    self.reset_selected()
                    if self.board[row][col].color == color:
                        self.board[row][col].selected = True
                else:
                    self.reset_selected()
                    if self.board[row][col].color == color:
                        self.board[row][col].selected = True
        return changed

    def reset_selected(self):
        for row_index in range(self.rows):
            for col_index in range(self.cols):
                if self.board[row_index][col_index] != 0:
                    self.board[row_index][col_index].selected = False

    # 'move' for player ------------------------------------------------------------------------------------------------
    def move(self, point_from, point_to, color):
        checked_before = self.piece_is_checked(color)
        changed = True
        new_board = [row[:] for row in self.board]
        if new_board[point_from[0]][point_from[1]].pawn:
            new_board[point_from[0]][point_from[1]].first = False
        prev_figure_dst = new_board[point_to[0]][point_to[1]]
        new_board[point_from[0]][point_from[1]].change_pos((point_to[0], point_to[1]))
        new_board[point_to[0]][point_to[1]] = new_board[point_from[0]][point_from[1]]
        new_board[point_from[0]][point_from[1]] = 0
        self.board = new_board
        # this code is so arranged that you cannot intentionally place your king under check, yet you may still miss the
        #  upcoming checkmate if you didn't avoid the check in the previous turn.
        if self.piece_is_checked(color) and not (checked_before and self.piece_is_checked(color)):
            changed = False
            new_board = [row[:] for row in self.board]
            new_board[point_to[0]][point_to[1]].change_pos((point_from[0], point_from[1]))
            if new_board[point_to[0]][point_to[1]].pawn:
                new_board[point_to[0]][point_to[1]].first = True
            new_board[point_to[0]][point_to[1]].change_pos((point_from[0], point_from[1]))
            new_board[point_from[0]][point_from[1]] = new_board[point_to[0]][point_to[1]]
            # king bug fix instead of 0 changed to 
            # object that was there previously (prev_figure_dst)
            new_board[point_to[0]][point_to[1]] = prev_figure_dst 
            self.board = new_board
        else:
            self.reset_selected()
        self.piece_at_the_end(color)
        self.update_moves()
        return changed

    # 'move' for chess algorithm ---------------------------------------------------------------------------------------
    def simple_move(self, point_from, point_to, color):
        new_board = [row[:] for row in self.board]
        if new_board[point_from[0]][point_from[1]].pawn:
            new_board[point_from[0]][point_from[1]].first = False
        new_board[point_from[0]][point_from[1]].change_pos((point_to[0], point_to[1]))
        new_board[point_to[0]][point_to[1]] = new_board[point_from[0]][point_from[1]]
        new_board[point_from[0]][point_from[1]] = 0
        self.board = new_board
        self.piece_at_the_end(color)
        self.update_moves()
