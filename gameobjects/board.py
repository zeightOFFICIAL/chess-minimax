"""
PyChess with minimax AI
Copyright (C) 2023 Artemii Saganenko, Alexander Kuksin
"""

from collections import namedtuple

from configuration.flowingconfig import *
from gameobjects.bishop import Bishop
from gameobjects.king import King
from gameobjects.knight import Knight
from gameobjects.rook import Rook
from gameobjects.queen import Queen
from gameobjects.pawn import Pawn

UndoMove = namedtuple("UndoMove", [
    "from_pos", "to_pos", "moving_piece", "captured_piece", "captured_pos",
    "was_first", "old_en_passant_target", "moving_had_moved", "castling_rook",
])

PROMOTABLE_ROW = {"w": 0, "b": 7}
COLOR_NAMES = {"w": "white", "b": "black"}
# Indexed by Piece.piece_img, which follows the alphabetical order of the loaded sprites.
PIECE_NAMES = ["bishop", "king", "knight", "pawn", "queen", "rook"]


# Row 0 is rank 8 and col 0 is file A.
def square_name(pos):
    row, col = pos
    return f"{chr(ord('A') + col)}{8 - row}"


class Board:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.board = [[0 for _ in range(8)] for _ in range(8)]
        self.en_passant_target = None
        # Enemy pieces each colour has taken, as (piece_img, colour_of_victim) in capture order.
        # Only real moves record here; the search's make_move/undo_move deliberately does not.
        self.captured = {"w": [], "b": []}
        # "E2->E4 (white pawn)" lines for the moves played, oldest first. Like self.captured, only
        # real moves record here.
        self.move_log = []
        self.set_start_normal()

    def log_move(self, piece, point_from, point_to):
        self.move_log.append(f"{square_name(point_from)}->{square_name(point_to)} "
                             f"({COLOR_NAMES[piece.color]} {PIECE_NAMES[piece.piece_img]})")

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

    # functions
    def update_moves(self):
        for row_index in range(self.rows):
            for col_index in range(self.cols):
                if self.board[row_index][col_index] != 0:
                    self.board[row_index][col_index].en_passant_target = self.en_passant_target
                    self.board[row_index][col_index].update_valid_moves(self.board)
        self._add_castling_moves()

    # Appends castling destinations to each king's move_list. Run after every piece's normal moves are
    # already up to date, so "which squares does the opponent attack" reflects the current position.
    def _add_castling_moves(self):
        for color, row in (("w", 7), ("b", 0)):
            king = self.board[row][4]
            if king == 0 or not king.king or king.color != color or king.has_moved:
                continue
            danger = self.get_danger_moves(color)
            if (row, 4) in danger:
                continue
            rook = self.board[row][7]
            if (rook != 0 and rook.rook and rook.color == color and not rook.has_moved
                    and self.board[row][5] == 0 and self.board[row][6] == 0
                    and (row, 5) not in danger and (row, 6) not in danger):
                king.move_list.append((row, 6))
            rook = self.board[row][0]
            if (rook != 0 and rook.rook and rook.color == color and not rook.has_moved
                    and self.board[row][1] == 0 and self.board[row][2] == 0 and self.board[row][3] == 0
                    and (row, 2) not in danger and (row, 3) not in danger):
                king.move_list.append((row, 2))

    # Detects a castling king-move and returns ((rook_from_row, rook_from_col), (rook_to_row, rook_to_col))
    # for the rook that must move alongside it, or None for any other move.
    @staticmethod
    def _castling_rook_move(piece, point_from, point_to):
        if not piece.king:
            return None
        from_row, from_col = point_from
        to_row, to_col = point_to
        if from_row != to_row or abs(to_col - from_col) != 2:
            return None
        if to_col > from_col:
            return (from_row, 7), (from_row, 5)
        return (from_row, 0), (from_row, 3)

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

    # Auto-promotes to Queen. Used by simple_move/make_move (AI and search moves), where there is no
    # player available to ask.
    def piece_at_the_end(self, color):
        end_row = PROMOTABLE_ROW[color]
        for col_index in range(0, 8):
            piece = self.board[end_row][col_index]
            if piece != 0 and piece.pawn:
                self.board[end_row][col_index] = Queen(end_row, col_index, color)

    # Returns the (row, col) of a pawn sitting on the back rank awaiting a promotion choice, or None.
    # Used by the human move path, which lets the player pick the piece via dialogs/promotion_menu.py.
    def find_pawn_to_promote(self, color):
        end_row = PROMOTABLE_ROW[color]
        for col_index in range(8):
            piece = self.board[end_row][col_index]
            if piece != 0 and piece.pawn and piece.color == color:
                return end_row, col_index
        return None

    def promote_pawn(self, pos, piece_class):
        row, col = pos
        color = self.board[row][col].color
        self.board[row][col] = piece_class(row, col, color)
        self.update_moves()

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

    # 'move' for player
    def move(self, point_from, point_to, color):
        checked_before = self.piece_is_checked(color)
        changed = True
        new_board = [row[:] for row in self.board]
        moving_piece = new_board[point_from[0]][point_from[1]]

        # Detect en passant capture
        en_passant_capture = False
        captured_pawn_pos = None
        captured_pawn_obj = None
        if moving_piece.pawn and self.en_passant_target is not None and point_to == self.en_passant_target:
            en_passant_capture = True
            captured_pawn_pos = (point_from[0], point_to[1])
            captured_pawn_obj = new_board[captured_pawn_pos[0]][captured_pawn_pos[1]]

        # Determine next en passant target (double push)
        new_en_passant_target = None
        if moving_piece.pawn:
            moving_piece.first = False
            if abs(point_to[0] - point_from[0]) == 2:
                new_en_passant_target = ((point_from[0] + point_to[0]) // 2, point_from[1])

        # Detect castling: relocate the rook alongside the king
        castling_rook = self._castling_rook_move(moving_piece, point_from, point_to)
        castling_rook_obj = None
        rook_had_moved = None
        if castling_rook is not None:
            rook_from, rook_to = castling_rook
            castling_rook_obj = new_board[rook_from[0]][rook_from[1]]
            rook_had_moved = castling_rook_obj.has_moved

        king_had_moved = moving_piece.has_moved if (moving_piece.king or moving_piece.rook) else None
        if moving_piece.king or moving_piece.rook:
            moving_piece.has_moved = True

        prev_figure_dst = new_board[point_to[0]][point_to[1]]
        moving_piece.change_pos((point_to[0], point_to[1]))
        new_board[point_to[0]][point_to[1]] = moving_piece
        new_board[point_from[0]][point_from[1]] = 0

        if en_passant_capture:
            new_board[captured_pawn_pos[0]][captured_pawn_pos[1]] = 0

        if castling_rook is not None:
            rook_from, rook_to = castling_rook
            castling_rook_obj.has_moved = True
            castling_rook_obj.change_pos(rook_to)
            new_board[rook_to[0]][rook_to[1]] = castling_rook_obj
            new_board[rook_from[0]][rook_from[1]] = 0

        old_en_passant_target = self.en_passant_target
        self.en_passant_target = new_en_passant_target
        self.board = new_board

        # cannot intentionally place your king under check
        if self.piece_is_checked(color) and not (checked_before and self.piece_is_checked(color)):
            changed = False
            new_board = [row[:] for row in self.board]
            new_board[point_to[0]][point_to[1]].change_pos((point_from[0], point_from[1]))
            if new_board[point_to[0]][point_to[1]].pawn:
                new_board[point_to[0]][point_to[1]].first = True
            if king_had_moved is not None:
                new_board[point_to[0]][point_to[1]].has_moved = king_had_moved
            new_board[point_from[0]][point_from[1]] = new_board[point_to[0]][point_to[1]]
            new_board[point_to[0]][point_to[1]] = prev_figure_dst
            if en_passant_capture and captured_pawn_obj is not None:
                new_board[captured_pawn_pos[0]][captured_pawn_pos[1]] = captured_pawn_obj
            if castling_rook is not None:
                rook_from, rook_to = castling_rook
                castling_rook_obj.change_pos(rook_from)
                castling_rook_obj.has_moved = rook_had_moved
                new_board[rook_from[0]][rook_from[1]] = castling_rook_obj
                new_board[rook_to[0]][rook_to[1]] = 0
            self.en_passant_target = old_en_passant_target
            self.board = new_board
        else:
            self.reset_selected()
            victim = captured_pawn_obj if en_passant_capture else prev_figure_dst
            if victim != 0 and victim is not None and victim.color != color:
                self.captured[color].append((victim.piece_img, victim.color))
            self.log_move(moving_piece, point_from, point_to)
        self.update_moves()
        return changed

    # 'move' for chess algorithm
    def simple_move(self, point_from, point_to, color):
        new_board = [row[:] for row in self.board]
        moving_piece = new_board[point_from[0]][point_from[1]]

        # Detect en passant capture
        victim = new_board[point_to[0]][point_to[1]]
        if moving_piece.pawn and self.en_passant_target is not None and point_to == self.en_passant_target:
            captured_pos = (point_from[0], point_to[1])
            victim = new_board[captured_pos[0]][captured_pos[1]]
            new_board[captured_pos[0]][captured_pos[1]] = 0
        if victim != 0 and victim.color != color:
            self.captured[color].append((victim.piece_img, victim.color))
        self.log_move(moving_piece, point_from, point_to)

        if moving_piece.pawn:
            moving_piece.first = False

        new_en_passant_target = None
        if moving_piece.pawn and abs(point_to[0] - point_from[0]) == 2:
            new_en_passant_target = ((point_from[0] + point_to[0]) // 2, point_from[1])

        # Detect castling: relocate the rook alongside the king
        castling_rook = self._castling_rook_move(moving_piece, point_from, point_to)

        if moving_piece.king or moving_piece.rook:
            moving_piece.has_moved = True

        moving_piece.change_pos((point_to[0], point_to[1]))
        new_board[point_to[0]][point_to[1]] = moving_piece
        new_board[point_from[0]][point_from[1]] = 0

        if castling_rook is not None:
            rook_from, rook_to = castling_rook
            rook = new_board[rook_from[0]][rook_from[1]]
            rook.has_moved = True
            rook.change_pos(rook_to)
            new_board[rook_to[0]][rook_to[1]] = rook
            new_board[rook_from[0]][rook_from[1]] = 0

        self.en_passant_target = new_en_passant_target
        self.board = new_board
        self.piece_at_the_end(color)
        self.update_moves()

    # 'make_move' / 'undo_move' for search
    # Mutates the board in place and returns an UndoMove token that reverts it exactly, avoiding the cost of
    # copy.deepcopy(board) at every node of the minimax tree.
    def make_move(self, point_from, point_to, color):
        from_row, from_col = point_from
        to_row, to_col = point_to
        moving_piece = self.board[from_row][from_col]

        captured_piece = 0
        captured_pos = None
        if moving_piece.pawn and self.en_passant_target is not None and point_to == self.en_passant_target:
            captured_pos = (from_row, to_col)
            captured_piece = self.board[captured_pos[0]][captured_pos[1]]
            self.board[captured_pos[0]][captured_pos[1]] = 0
        elif self.board[to_row][to_col] != 0:
            captured_pos = (to_row, to_col)
            captured_piece = self.board[to_row][to_col]

        was_first = moving_piece.first if moving_piece.pawn else None
        old_en_passant_target = self.en_passant_target
        moving_had_moved = moving_piece.has_moved if (moving_piece.king or moving_piece.rook) else None

        new_en_passant_target = None
        if moving_piece.pawn:
            moving_piece.first = False
            if abs(to_row - from_row) == 2:
                new_en_passant_target = ((from_row + to_row) // 2, from_col)

        # Detect castling: relocate the rook alongside the king
        castling_rook_move = self._castling_rook_move(moving_piece, point_from, point_to)
        castling_rook_undo = None

        if moving_piece.king or moving_piece.rook:
            moving_piece.has_moved = True

        moving_piece.change_pos((to_row, to_col))
        self.board[to_row][to_col] = moving_piece
        self.board[from_row][from_col] = 0
        self.en_passant_target = new_en_passant_target

        if castling_rook_move is not None:
            rook_from, rook_to = castling_rook_move
            rook = self.board[rook_from[0]][rook_from[1]]
            rook_had_moved = rook.has_moved
            rook.has_moved = True
            rook.change_pos(rook_to)
            self.board[rook_to[0]][rook_to[1]] = rook
            self.board[rook_from[0]][rook_from[1]] = 0
            castling_rook_undo = (rook, rook_from, rook_to, rook_had_moved)

        if moving_piece.pawn:
            if (color == "w" and to_row == 0) or (color == "b" and to_row == 7):
                self.board[to_row][to_col] = Queen(to_row, to_col, color)

        self.update_moves()

        return UndoMove(point_from, point_to, moving_piece, captured_piece, captured_pos,
                        was_first, old_en_passant_target, moving_had_moved, castling_rook_undo)

    def undo_move(self, undo):
        from_row, from_col = undo.from_pos
        to_row, to_col = undo.to_pos

        undo.moving_piece.change_pos((from_row, from_col))
        if undo.moving_piece.pawn and undo.was_first is not None:
            undo.moving_piece.first = undo.was_first
        if undo.moving_had_moved is not None:
            undo.moving_piece.has_moved = undo.moving_had_moved

        self.board[from_row][from_col] = undo.moving_piece
        self.board[to_row][to_col] = 0
        if undo.captured_piece != 0:
            self.board[undo.captured_pos[0]][undo.captured_pos[1]] = undo.captured_piece

        if undo.castling_rook is not None:
            rook, rook_from, rook_to, rook_had_moved = undo.castling_rook
            rook.change_pos(rook_from)
            rook.has_moved = rook_had_moved
            self.board[rook_from[0]][rook_from[1]] = rook
            self.board[rook_to[0]][rook_to[1]] = 0

        self.en_passant_target = undo.old_en_passant_target
        self.update_moves()
