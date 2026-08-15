"""
PyChess with minimax AI
Copyright (C) 2023 Artemii Saganenko, Alexander Kuksin
"""

from sys import exit
from time import time
import os

import pygame

from configuration.flowingconfig import *
from gameobjects.board import Board
from scripts.algorithm import Solution
from dialogs.start_screen import start_screen
from dialogs.end_screen import end_screen
from dialogs.promotion_menu import choose_promotion
from dialogs.fonts import player_time_font, king_condition_font, move_log_font, move_log_title_font
from gameobjects.piece import white_all_images, black_all_images

_BASE = "resources/images"
raw_board = pygame.image.load(f"{_BASE}/eq_chessboard.png")
icon = pygame.image.load("resources/icons/icon.png")
if visual_set != 0:
    _board_path = f"{_BASE}/{visual_set}/eq_chessboard.png"
    if os.path.exists(_board_path):
        try:
            raw_board = pygame.image.load(_board_path)
        except (FileNotFoundError, TypeError) as e:
            logging.warning("Load visual set %s: board image missing, using default", visual_set)
    else:
        logging.warning("Load visual set %s: board image not found, using default", visual_set)
scaled_board = pygame.transform.smoothscale(raw_board, (width - PADDING_ABSOLUTE, HEIGHT - PADDING_ABSOLUTE))

CAPTURED_ICON_SIZE = int(width * 0.028)
CAPTURED_ICON_STEP = CAPTURED_ICON_SIZE * 0.9
CAPTURED_GAP = width * 0.012
CAPTURED_TRAY_PAD = CAPTURED_ICON_SIZE * 0.18
# Mid grey: the window background is black, so black sprites would be invisible without a tray.
CAPTURED_TRAY_COLOR = (105, 105, 105)
_captured_icons = {
    "w": [pygame.transform.smoothscale(img, (CAPTURED_ICON_SIZE, CAPTURED_ICON_SIZE)) for img in white_all_images],
    "b": [pygame.transform.smoothscale(img, (CAPTURED_ICON_SIZE, CAPTURED_ICON_SIZE)) for img in black_all_images],
}


# Draws a row of captured-piece icons from anchor_x, running away from the timer it belongs to.
def draw_captured_row(captured, anchor_x, center_y, grow_left):
    if not captured:
        return
    icon_y = center_y - CAPTURED_ICON_SIZE / 2
    positions = []
    for index in range(len(captured)):
        if grow_left:
            positions.append(anchor_x - (index + 1) * CAPTURED_ICON_STEP)
        else:
            positions.append(anchor_x + index * CAPTURED_ICON_STEP)

    tray_left = min(positions) - CAPTURED_TRAY_PAD
    tray_right = max(positions) + CAPTURED_ICON_SIZE + CAPTURED_TRAY_PAD
    pygame.draw.rect(win, CAPTURED_TRAY_COLOR,
                     (tray_left, icon_y - CAPTURED_TRAY_PAD,
                      tray_right - tray_left, CAPTURED_ICON_SIZE + CAPTURED_TRAY_PAD * 2),
                     border_radius=int(CAPTURED_TRAY_PAD * 2))

    for icon_x, (piece_img, piece_color) in zip(positions, captured):
        win.blit(_captured_icons[piece_color][piece_img], (icon_x, icon_y))


MOVE_LOG_TITLE = move_log_title_font.render("Moves", True, (255, 255, 255))
MOVE_LOG_X = width + MOVE_LOG_WIDTH * 0.08
MOVE_LOG_TOP = PADDING_HALF + MOVE_LOG_TITLE.get_height() * 1.6
MOVE_LOG_STEP = move_log_font.get_linesize()
MOVE_LOG_MAX_LINES = int((HEIGHT - PADDING_HALF - MOVE_LOG_TOP) // MOVE_LOG_STEP)


# Draws the move history in the strip right of the board, oldest at the top. Once it no longer fits,
# the oldest lines drop off so the latest move stays visible at the bottom.
def draw_move_log(move_log):
    pygame.draw.rect(win, (0, 0, 0), (width, 0, MOVE_LOG_WIDTH, HEIGHT))
    win.blit(MOVE_LOG_TITLE, (MOVE_LOG_X, PADDING_HALF))
    for line_index, entry in enumerate(move_log[-MOVE_LOG_MAX_LINES:]):
        text = move_log_font.render(entry, True, (215, 215, 215))
        win.blit(text, (MOVE_LOG_X, MOVE_LOG_TOP + line_index * MOVE_LOG_STEP))


def redraw_gamewindow(board_to_render, player1_time, player2_time, state_white, state_black):
    pygame.draw.rect(win, (0, 0, 0), (0, 0, width, width))
    draw_move_log(board_to_render.move_log)
    win.blit(scaled_board, (PADDING_HALF, PADDING_HALF))
    board_to_render.draw(win)
    format_time_p1 = f'{player1_time // 60:d}:{player1_time % 60:02d}'
    format_time_p2 = f'{player2_time // 60:d}:{player2_time % 60:02d}'
    text_time1 = player_time_font.render(
        "Player 1 Time: " + str(format_time_p1), True, (255, 255, 255), (0, 0, 0))
    text_time2 = player_time_font.render(
        "Player 2 Time: " + str(format_time_p2), True, (255, 255, 255), (0, 0, 0))
    if state_white == 1:
        text_state1 = king_condition_font.render(
            "White King is under check!", True, (255, 255, 255), (0, 0, 0))
        win.blit(text_state1, (PADDING_HALF,
                               width - PADDING_HALF / 1.5))
    if state_black == 1:
        text_state2 = king_condition_font.render(
            "Black King is under check!", True, (255, 255, 255), (0, 0, 0))
        win.blit(text_state2, (width - PADDING_HALF - text_state2.get_width(),
                               PADDING_HALF - text_state2.get_height() * 1.5))
    time1_x = width - PADDING_HALF - text_time1.get_width()
    time1_y = width - PADDING_HALF + text_time1.get_height()
    time2_y = PADDING_HALF - text_time2.get_height() * 2
    win.blit(text_time1, (time1_x, time1_y))
    win.blit(text_time2, (PADDING_HALF, time2_y))

    # White's captures sit left of its bottom-right timer, black's right of its top-left timer.
    draw_captured_row(board_to_render.captured["w"], time1_x - CAPTURED_GAP,
                      time1_y + text_time1.get_height() / 2, grow_left=True)
    draw_captured_row(board_to_render.captured["b"],
                      PADDING_HALF + text_time2.get_width() + CAPTURED_GAP,
                      time2_y + text_time2.get_height() / 2, grow_left=False)
    pygame.display.update()


def click(pos):
    x = pos[0]
    y = pos[1]
    if TOP_LEFT[0] < x < TOP_LEFT[0] + BOTTOM_RIGHT[0]:
        if TOP_LEFT[1] < y < TOP_LEFT[1] + BOTTOM_RIGHT[1]:
            divx = x - TOP_LEFT[0]
            divy = y - TOP_LEFT[0]
            i = int(divx / (BOTTOM_RIGHT[0] / 8))
            j = int(divy / (BOTTOM_RIGHT[1] / 8))
            logging.debug(
                "Click: Clicked at position: (x = %d, y = %d), at cell (w = %d, h = %d)", x, y, i, j)
            return i, j
    else:
        logging.debug(
            "Click: Clicked at position: (x = %d, y = %d), not at the cell.", x, y)


def main():
    logging.debug("Main: Game started: %d, limit: %d", game_mode * (difficulty + 1), time_restriction)
    white_time, black_time = TIME_RESTRICTION_SECONDS, TIME_RESTRICTION_SECONDS
    wide_timer, start_time = time(), time()
    statewhite, stateblack = 0, 0
    white_wants_draw, black_wants_draw = 0, 0
    turn_color = "w"
    turn_number = 0
    game_board = Board(8, 8)
    game_board.update_moves()
    run = True
    clock = pygame.time.Clock()
    while run:
        clock.tick(FPS_MAX)
        if turn_color == "w":
            white_time -= (time() - wide_timer)
            if white_time <= 0:
                end_screen(win, "Black Wins!", time() - start_time, main)
                logging.debug(
                    "Main: Black wins. Bcs. white out of time. Turn: %d", turn_number)
        else:
            black_time -= (time() - wide_timer)
            if black_time <= 0:
                end_screen(win, "White Wins!", time() - start_time, main)
                logging.debug(
                    "Main: White wins. Bcs. black out of time. Turn: %d", turn_number)
        wide_timer = time()
        redraw_gamewindow(game_board, int(white_time), int(black_time), statewhite, stateblack)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logging.warning("Main: App closed. Maybe unintentionally.")
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    logging.debug("Main: Quit button is pressed.")
                    pygame.quit()
                    exit()
                if event.key == pygame.K_s:
                    logging.debug(
                        "Main: Surrender button is pressed by %c at turn: %d", turn_color, turn_number)
                    if turn_color == "w":
                        end_screen(win, "Black Wins!", time() - start_time, main)
                    else:
                        end_screen(win, "White Wins!", time() - start_time, main)
                if event.key == pygame.K_p and game_mode == 0:
                    if turn_color == "w":
                        white_wants_draw = 1 if white_wants_draw == 0 else 0
                    if turn_color == "b":
                        black_wants_draw = 1 if black_wants_draw == 0 else 0
                    logging.debug(
                        "Main: White wants draw? - %s", bool(white_wants_draw))
                    logging.debug(
                        "Main: Black wants draw? - %s", bool(black_wants_draw))
                    if black_wants_draw and white_wants_draw:
                        logging.debug("Main: Draw.")
                        end_screen(win, "Draw!", time() - start_time, main)
            # game mode = 1. BLACK - AI, WHITE - PLAYER.
            if turn_color == "b" and game_mode == 1:
                if statewhite == 1:
                    end_screen(win, "Black Wins!", time() - start_time, main)
                    logging.debug("Main: Black wins. White ended its turn with checked king. At turn: %d", turn_number)
                change = False
                solve = Solution(game_board, turn_color)
                try:
                    (piecex, piecey), choice = solve.random_choice(turn_color)
                    if difficulty == 1:
                        (piecex, piecey), choice = solve.tier3_choice(turn_color)
                    elif difficulty == 2:
                        (piecex, piecey), choice = solve.tier2_choice(turn_color)
                    elif difficulty == 3:
                        (piecex, piecey), choice = solve.tier1_choice(turn_color)
                    game_board.simple_move(
                        (piecex, piecey), choice, "b")
                    change = True
                except TypeError:
                    logging.warning("Main: Type error. White wins. It's either critical script failure or true winning "
                                    "condition. At turn %c.%d", turn_color, turn_number)
                    end_screen(win, "White Wins!", time() - start_time, main)
                if change:
                    turn_number += 1
                    logging.debug("Main: Turn number: %d", turn_number)
                    wide_timer = time()
                    turn_color = "w"
                statewhite = 1 if game_board.piece_is_checked("w") else 0
                stateblack = 1 if game_board.piece_is_checked("b") else 0
            # game_mode = 1. BLACK - AI, WHITE - PLAYER. game_mode = 0 BLACK - PLAYER, WHITE - PLAYER.
            elif (turn_color == "w" and game_mode == 1) or game_mode == 0:
                if turn_color == "b" and statewhite == 1:
                    logging.debug(
                        "Main: Black wins. White ended its turn with checked king. At turn: %d", turn_number)
                    end_screen(win, "Black Wins!", time() - start_time, main)
                elif turn_color == "w" and stateblack == 1:
                    logging.debug(
                        "Main: White wins. Black ended its turn with checked king. At turn: %d", turn_number)
                    end_screen(win, "White Wins!", time() - start_time, main)
                change = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    clicked_position = pygame.mouse.get_pos()
                    game_board.update_moves()
                    try:
                        cell_x, cell_y = click(clicked_position)
                        change = game_board.select(cell_x, cell_y, turn_color)
                    except AttributeError:
                        logging.warning(
                            "Main: Non-terminal script error. Selection error lead to game_board.select(i, j, turn)")
                        change = False
                    except TypeError:
                        logging.warning(
                            "Main: Non-terminal TypeError originated at click(clicked_position)")
                        change = False
                    finally:
                        game_board.update_moves()
                    if change:
                        pending_promotion = game_board.find_pawn_to_promote(turn_color)
                        if pending_promotion is not None:
                            chosen_class = choose_promotion(win, turn_color)
                            game_board.promote_pawn(pending_promotion, chosen_class)
                        turn_number += 1
                        logging.debug("Main: Turn number: %d", turn_number)
                        wide_timer = time()
                        game_board.reset_selected()
                        turn_color = "w" if turn_color == "b" else "b"
                    statewhite = 1 if game_board.piece_is_checked("w") else 0
                    stateblack = 1 if game_board.piece_is_checked("b") else 0


win = pygame.display.set_mode((WINDOW_WIDTH, HEIGHT), vsync=True)
pygame.display.set_caption("PyChess")
pygame.display.set_icon(icon)
start_screen(win)
main()
