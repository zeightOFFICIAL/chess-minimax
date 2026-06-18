"""
PyChess with minimax AI
Copyright (C) 2023 Artemii Saganenko, Alexander Kuksin
"""

# ver 917
# algorithm.py


# libraries ============================================================================================================
import copy
import random
from math import inf
from collections import namedtuple

from configuration.flowingconfig import *
# ----------------------------------------------------------------------------------------------------------------------
from scripts.evaluate import evaluate_board_advanced, evaluate_board, mvv_lva_score
from scripts import zobrist

TTEntry = namedtuple("TTEntry", ["value", "depth", "flag"])
EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2


def get_all_pieces(board, color):
    all_pieces = []
    for row in range(0, 8):
        for col in range(0, 8):
            if board.board[row][col] != 0:
                if board.board[row][col].color == color:
                    if len(board.board[row][col].move_list) > 0:
                        all_pieces.append(board.board[row][col])
    return all_pieces


def minimax(board, depth, alpha, beta, maximizing, tt=None, z_hash=None, root_color="b"):
    if depth == 0:
        return evaluate_board_advanced(board, root_color)
    current_color = root_color if maximizing else ("w" if root_color == "b" else "b")
    alpha_orig = alpha
    beta_orig = beta

    if tt is not None and z_hash is not None:
        key = (z_hash, depth, maximizing)
        entry = tt.get(key)
        if entry is not None and entry.depth >= depth:
            if entry.flag == EXACT:
                return entry.value
            elif entry.flag == LOWERBOUND:
                alpha = max(alpha, entry.value)
            elif entry.flag == UPPERBOUND:
                beta = min(beta, entry.value)
            if alpha >= beta:
                return entry.value

    candidates = []
    pieces = get_all_pieces(board, current_color)
    for piece in pieces:
        for move in piece.move_list:
            score = mvv_lva_score(board, (piece.row, piece.col), move)
            candidates.append((score, piece, move))
    candidates.sort(key=lambda x: x[0], reverse=True)
    if maximizing:
        best = -inf
        for score, piece, move in candidates:
            from_sq = piece.row * 8 + piece.col
            to_sq = move[0] * 8 + move[1]
            child_hash = None
            if tt is not None and z_hash is not None:
                child_hash = zobrist.hash_after_move(z_hash, board.board, from_sq, to_sq)
            child = copy.deepcopy(board)
            child.simple_move((piece.row, piece.col), move, current_color)
            if child.piece_is_checked(current_color):
                continue
            value = minimax(child, depth - 1, alpha, beta, False, tt, child_hash, root_color)
            best = max(best, value)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        if tt is not None and z_hash is not None:
            flag = EXACT
            if best <= alpha_orig:
                flag = UPPERBOUND
            elif best >= beta_orig:
                flag = LOWERBOUND
            key = (z_hash, depth, maximizing)
            tt[key] = TTEntry(best, depth, flag)
            if len(tt) >= 1000000:
                tt.clear()
        return best
    else:
        best = inf
        for score, piece, move in candidates:
            from_sq = piece.row * 8 + piece.col
            to_sq = move[0] * 8 + move[1]
            child_hash = None
            if tt is not None and z_hash is not None:
                child_hash = zobrist.hash_after_move(z_hash, board.board, from_sq, to_sq)
            child = copy.deepcopy(board)
            child.simple_move((piece.row, piece.col), move, current_color)
            if child.piece_is_checked(current_color):
                continue
            value = minimax(child, depth - 1, alpha, beta, True, tt, child_hash, root_color)
            best = min(best, value)
            beta = min(beta, best)
            if beta <= alpha:
                break
        if tt is not None and z_hash is not None:
            flag = EXACT
            if best <= alpha_orig:
                flag = UPPERBOUND
            elif best >= beta_orig:
                flag = LOWERBOUND
            key = (z_hash, depth, maximizing)
            tt[key] = TTEntry(best, depth, flag)
            if len(tt) >= 1000000:
                tt.clear()
        return best


# class for algorithmic solution =======================================================================================
class Solution:
    def __init__(self, board, color):
        self.board = board
        self.evaluation = evaluate_board(self.board, color)

    # diff. 0 random choice --------------------------------------------------------------------------------------------
    def random_choice(self, color):
        all_moves = []
        was_checked = self.board.piece_is_checked(color)
        self.board.update_moves()
        new_board = copy.deepcopy(self.board)
        all_pieces = get_all_pieces(new_board, color)
        for piece in all_pieces:
            for move in piece.move_list:
                if was_checked:
                    new_board = copy.deepcopy(self.board)
                    new_board.simple_move((piece.row, piece.col), move, color)
                    if not new_board.piece_is_checked(color):
                        return (piece.row, piece.col), move
                else:
                    new_board = copy.deepcopy(self.board)
                    new_board.simple_move((piece.row, piece.col), move, color)
                    if not new_board.piece_is_checked(color):
                        all_moves.append(((piece.row, piece.col), move))
        if was_checked:
            return -100
        else:
            if len(all_moves) <= 0:
                return -100
            logging.debug("Random choice: total moves: %d", len(all_moves))
            return random.choice(all_moves)

    # diff. 1 evaluation -----------------------------------------------------------------------------------------------
    def tier3_choice(self, color):
        best_value = -inf
        best_move = -1
        was_checked = self.board.piece_is_checked(color)
        new_board = copy.deepcopy(self.board)
        all_pieces = get_all_pieces(new_board, color)
        for piece in all_pieces:
            for move in piece.move_list:
                if was_checked:
                    new_board = copy.deepcopy(self.board)
                    new_board.simple_move((piece.row, piece.col), move, color)
                    if not new_board.piece_is_checked(color):
                        if best_move == -1:
                            best_move = (piece.row, piece.col), move
                            best_value = evaluate_board(new_board, color)
                        elif evaluate_board(new_board, color) > best_value:
                            best_move = (piece.row, piece.col), move
                            best_value = evaluate_board(new_board, color)
                else:
                    new_board = copy.deepcopy(self.board)
                    new_board.simple_move((piece.row, piece.col), move, color)
                    if not new_board.piece_is_checked(color):
                        if evaluate_board(new_board, color) > best_value:
                            best_value = evaluate_board(new_board, color)
                            best_move = (piece.row, piece.col), move
        if best_value == self.evaluation and not was_checked:
            logging.debug("Eval. choice: all moves are equally evaluated, -> random choice")
            return self.random_choice(color)
        logging.debug("Eval. choice: the most arithmetically profitable move, has value of %d in comparison to %d",
                      best_value, self.evaluation)
        return best_move

    # diff. 2 minimax depth 2, advanced evaluation ---------------------------------------------------------------------
    def tier2_choice(self, color):
        was_checked = self.board.piece_is_checked(color)
        if was_checked:
            all_pieces = get_all_pieces(self.board, color)
            best_move = self.random_choice(color)
            best_value = -inf
            for piece in all_pieces:
                for move in piece.move_list:
                    new_board = copy.deepcopy(self.board)
                    new_board.simple_move((piece.row, piece.col), move, color)
                    if not new_board.piece_is_checked(color):
                        if best_value == -inf:
                            best_move = (piece.row, piece.col), move
                            best_value = evaluate_board_advanced(new_board, color)
                        elif evaluate_board_advanced(new_board, color) > best_value:
                            best_move = (piece.row, piece.col), move
                            best_value = evaluate_board_advanced(new_board, color)
            return best_move
        else:
            candidates = []
            pieces = get_all_pieces(self.board, color)
            for piece in pieces:
                for move in piece.move_list:
                    score = mvv_lva_score(self.board, (piece.row, piece.col), move)
                    candidates.append((score, piece, move))
            candidates.sort(key=lambda x: x[0], reverse=True)
            best_value = -inf
            best_move = self.random_choice(color)
            tt = {}
            root_hash = zobrist.hash_board(self.board.board)
            for score, piece, move in candidates:
                from_sq = piece.row * 8 + piece.col
                to_sq = move[0] * 8 + move[1]
                child_hash = zobrist.hash_after_move(root_hash, self.board.board, from_sq, to_sq)
                child = copy.deepcopy(self.board)
                child.simple_move((piece.row, piece.col), move, color)
                if not child.piece_is_checked(color):
                    value = minimax(child, 1, -inf, inf, False, tt, child_hash, color)
                    if value > best_value:
                        best_value = value
                        best_move = (piece.row, piece.col), move
            return best_move

    # diff. 3 minimax depth 3, advanced evaluation ---------------------------------------------------------------------
    def tier1_choice(self, color):
        was_checked = self.board.piece_is_checked(color)
        if was_checked:
            all_pieces = get_all_pieces(self.board, color)
            best_move = self.random_choice(color)
            best_value = -inf
            for piece in all_pieces:
                for move in piece.move_list:
                    new_board = copy.deepcopy(self.board)
                    new_board.simple_move((piece.row, piece.col), move, color)
                    if not new_board.piece_is_checked(color):
                        if best_value == -inf:
                            best_move = (piece.row, piece.col), move
                            best_value = evaluate_board_advanced(new_board, color)
                        elif evaluate_board_advanced(new_board, color) > best_value:
                            best_move = (piece.row, piece.col), move
                            best_value = evaluate_board_advanced(new_board, color)
            return best_move
        else:
            tt = {}
            root_hash = zobrist.hash_board(self.board.board)
            candidates = []
            pieces = get_all_pieces(self.board, color)
            for piece in pieces:
                for move in piece.move_list:
                    score = mvv_lva_score(self.board, (piece.row, piece.col), move)
                    candidates.append((score, piece, move))
            candidates.sort(key=lambda x: x[0], reverse=True)
            best_value = -inf
            best_move = self.random_choice(color)
            alpha = -inf
            beta = inf
            for score, piece, move in candidates:
                from_sq = piece.row * 8 + piece.col
                to_sq = move[0] * 8 + move[1]
                child_hash = zobrist.hash_after_move(root_hash, self.board.board, from_sq, to_sq)
                child = copy.deepcopy(self.board)
                child.simple_move((piece.row, piece.col), move, color)
                if not child.piece_is_checked(color):
                    value = minimax(child, 2, alpha, beta, False, tt, child_hash, color)
                    if value > best_value:
                        best_value = value
                        best_move = (piece.row, piece.col), move
                    alpha = max(alpha, best_value)
                    if beta <= alpha:
                        break
            return best_move


