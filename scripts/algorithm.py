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

from configuration.flowingconfig import *
# ----------------------------------------------------------------------------------------------------------------------
from scripts.evaluate import evaluate_board_advanced, evaluate_board


# class for algorithmic solution =======================================================================================
class Solution:
    def __init__(self, board):
        self.board = board
        self.evaluation = evaluate_board(self.board, "b")

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
                    new_board.simple_move((piece.row, piece.col), (move[1], move[0]), color)
                    if not new_board.piece_is_checked(color):
                        return (piece.row, piece.col), (move[0], move[1])
                else:
                    new_board = copy.deepcopy(self.board)
                    new_board.simple_move((piece.row, piece.col), (move[1], move[0]), color)
                    if not new_board.piece_is_checked(color):
                        all_moves.append(((piece.row, piece.col), (move[0], move[1])))
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
                    new_board.simple_move((piece.row, piece.col), (move[1], move[0]), color)
                    if not new_board.piece_is_checked(color):
                        if best_move == -1:
                            best_move = (piece.row, piece.col), (move[0], move[1])
                            best_value = evaluate_board(new_board, color)
                        elif evaluate_board(new_board, color) > best_value:
                            best_move = (piece.row, piece.col), (move[0], move[1])
                            best_value = evaluate_board(new_board, color)
                else:
                    new_board = copy.deepcopy(self.board)
                    new_board.simple_move((piece.row, piece.col), (move[1], move[0]), color)
                    if not new_board.piece_is_checked(color):
                        if evaluate_board(new_board, color) > best_value:
                            best_value = evaluate_board(new_board, color)
                            best_move = (piece.row, piece.col), (move[0], move[1])
        if best_value == self.evaluation and not was_checked:
            logging.debug("Eval. choice: all moves are equally evaluated, -> random choice")
            return self.random_choice(color)
        logging.debug("Eval. choice: the most arithmetically profitable move, has value of %d in comparison to %d",
                      best_value, self.evaluation)
        return best_move

    # diff. 2 minimax depth 2, advanced evaluation ---------------------------------------------------------------------
    def tier2_choice(self, color):
        def minimaxdepth2(original_color):
            max_value = -inf
            maxed_move = -1
            all_pieces_1 = get_all_pieces(self.board, original_color)
            for piece_1 in all_pieces_1:
                for move_1 in piece_1.move_list:
                    after_my_move = copy.deepcopy(self.board)
                    after_my_move.simple_move((piece_1.row, piece_1.col), (move_1[1], move_1[0]), original_color)
                    if not after_my_move.piece_is_checked(original_color):
                        opponent_color = "w" if original_color == "b" else "b"
                        all_pieces_2 = get_all_pieces(after_my_move, opponent_color)
                        min_value = inf
                        for piece_2 in all_pieces_2:
                            for move_2 in piece_2.move_list:
                                after_response = copy.deepcopy(after_my_move)
                                after_response.simple_move((piece_2.row, piece_2.col), (move_2[1], move_2[0]),
                                                           opponent_color)
                                value = evaluate_board_advanced(after_response, original_color)
                                if value < min_value:
                                    min_value = value
                        if min_value > max_value:
                            max_value = min_value
                            maxed_move = (piece_1.row, piece_1.col), (move_1[0], move_1[1])
            if maxed_move == -1:
                return self.random_choice(original_color)
            return maxed_move

        was_checked = self.board.piece_is_checked(color)
        if was_checked:
            all_pieces = get_all_pieces(self.board, color)
            best_move = self.random_choice(color)
            best_value = -inf
            for piece in all_pieces:
                for move in piece.move_list:
                    new_board = copy.deepcopy(self.board)
                    new_board.simple_move((piece.row, piece.col), (move[1], move[0]), color)
                    if not new_board.piece_is_checked(color):
                        if best_value == -inf:
                            best_move = (piece.row, piece.col), (move[0], move[1])
                            best_value = evaluate_board_advanced(new_board, color)
                        elif evaluate_board_advanced(new_board, color) > best_value:
                            best_move = (piece.row, piece.col), (move[0], move[1])
                            best_value = evaluate_board_advanced(new_board, color)
            return best_move
        else:
            best_move = minimaxdepth2(color)
            return best_move

    # diff. 3 minimax depth 3, advanced evaluation ---------------------------------------------------------------------
    def tier1_choice(self, color):
        def root_minimax(board, depth, maximizing):
            best_value_root = -inf
            maxed_move_root = self.random_choice(color)
            all_pieces_1 = get_all_pieces(board, color)
            for piece_1 in all_pieces_1:
                for move_1 in piece_1.move_list:
                    next_board = copy.deepcopy(board)
                    next_board.simple_move((piece_1.row, piece_1.col), (move_1[1], move_1[0]), color)
                    if not next_board.piece_is_checked("b"):
                        value = minimax(next_board, depth - 1, -inf, inf, not maximizing)
                        if value >= best_value_root:
                            best_value_root = value
                            maxed_move_root = (piece_1.row, piece_1.col), (move_1[0], move_1[1])
            return maxed_move_root

        def minimax(board, depth, alpha, beta, maximizing):
            if depth == 0:
                return evaluate_board_advanced(board, "b")
            current_color = "b" if maximizing else "w"
            if maximizing:
                all_pieces_1 = get_all_pieces(board, "b")
                best_value_1 = -inf
                for piece_1 in all_pieces_1:
                    for move_1 in piece_1.move_list:
                        child = copy.deepcopy(board)
                        child.simple_move((piece_1.row, piece_1.col), (move_1[1], move_1[0]), current_color)
                        value = minimax(child, depth - 1, alpha, beta, not maximizing)
                        best_value_1 = max(value, best_value_1)
                        alpha = max(alpha, best_value_1)
                        if beta <= alpha:
                            return best_value_1
                return best_value_1
            else:
                all_pieces_1 = get_all_pieces(board, "w")
                best_value_1 = inf
                for piece_1 in all_pieces_1:
                    for move_1 in piece_1.move_list:
                        child = copy.deepcopy(board)
                        child.simple_move((piece_1.row, piece_1.col), (move_1[1], move_1[0]), current_color)
                        value = minimax(child, depth - 1, alpha, beta, not maximizing)
                        best_value_1 = min(value, best_value_1)
                        beta = min(beta, best_value_1)
                        if beta <= alpha:
                            return best_value_1
                return best_value_1

        was_checked = self.board.piece_is_checked(color)
        if was_checked:
            all_pieces = get_all_pieces(self.board, color)
            best_move = self.random_choice(color)
            best_value = -inf
            for piece in all_pieces:
                for move in piece.move_list:
                    new_board = copy.deepcopy(self.board)
                    new_board.simple_move((piece.row, piece.col), (move[1], move[0]), color)
                    if not new_board.piece_is_checked(color):
                        if best_value == -inf:
                            best_move = (piece.row, piece.col), (move[0], move[1])
                            best_value = evaluate_board_advanced(new_board, color)
                        elif evaluate_board_advanced(new_board, color) > best_value:
                            best_move = (piece.row, piece.col), (move[0], move[1])
                            best_value = evaluate_board_advanced(new_board, color)
            return best_move
        else:
            best_move = root_minimax(self.board, 3, True)
            return best_move


def get_all_pieces(board, color):
    all_pieces = []
    for row in range(0, 8):
        for col in range(0, 8):
            if board.board[row][col] != 0:
                if board.board[row][col].color == color:
                    if len(board.board[row][col].move_list) > 0:
                        all_pieces.append(board.board[row][col])
    return all_pieces
