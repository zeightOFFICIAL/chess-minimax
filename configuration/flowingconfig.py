"""
PyChess with minimax AI
Copyright (C) 2023 Artemii Saganenko, Alexander Kuksin
"""

import configparser
import logging
import sys, os

if getattr(sys, 'frozen', False):
    _config_dir = os.path.dirname(sys.executable)
else:
    _config_dir = "."

from screeninfo import get_monitors

# debug [should not be turned on by user, and in production by developer]
DEBUG_MODE = 0
if DEBUG_MODE == 1:
    logging.basicConfig(format='log:%(levelname)s:%(filename)s:%(lineno)d - %(message)s', level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.CRITICAL + 1)

# rate of screen update [should not be changed]
FPS_MAX = 24

# window width and height [changeable, adjustable]
# if auto-detection works - its height=width is equal to display height minus 90
width = 600
try:
    for display in get_monitors():
        if display.is_primary:
            width = display.height - 110
            logging.debug("Auto-detection of screen height: Detected screen height: %d", width)
except:
    logging.debug("Auto-detection of screen height: Screen's height auto-detection failed. Applying default: 600")
    width = 600

# game mode [changeable]
# 0 - PvP (hotseat)
# 1 - PvE (versus script)
game_mode = 0

# if game mode is 1, then difficulty determines algorithms complexity [changeable]
# 0 - random choice
# 1 - simple table evaluation 1-turn-deep
# 2 - advanced table evaluation minimax 2-turns-deep
# 3 - advanced table evaluation minimax 3-turns-deep plus alpha-beta cut
difficulty = 0

# padding size, distance between board and the window border [should not be changed]
PADDING_ABSOLUTE = 130

# visual set [changeable]
visual_set = 0

# timer for each person (in minutes) [changeable]
time_restriction = 15

# time before game starts [not recommended to change]
freeze_time = 3

try:
    config = configparser.ConfigParser()
    config.read(os.path.join(_config_dir, "config.txt"))
    if config.has_section("settings"):
        settings = config["settings"]
        game_mode = settings.getint("game_mode", fallback=game_mode)
        difficulty = settings.getint("difficulty", fallback=difficulty)
        visual_set = settings.getint("visual_set", fallback=visual_set)
        freeze_time = settings.getint("freeze_time", fallback=freeze_time)
        time_restriction = settings.getint("time_restriction", fallback=time_restriction)
        logging.debug("Reading config: game_mode=%d, difficulty=%d, visual_set=%d, freeze_time=%d, "
                      "time_restriction=%d", game_mode, difficulty, visual_set, freeze_time, time_restriction)
except (configparser.Error, ValueError) as e:
    logging.warning("Reading config: Config file is corrupted, does not exist or is unreadable, possibly parsing error."
                    "\nNot parsed values are set to default.")

# check values for logical errors
time_restriction = 15 if (time_restriction > 60000) or (
        time_restriction < 0.5) else time_restriction
game_mode = 0 if game_mode not in (0, 1) else game_mode
difficulty = 0 if (difficulty > 3) or (difficulty < 0) else difficulty
freeze_time = 5 if (freeze_time > 10) or (freeze_time < 0) else freeze_time

HEIGHT = width
PADDING_HALF = PADDING_ABSOLUTE // 2
TOP_LEFT = (PADDING_HALF, PADDING_HALF)
TOP_RIGHT = (width - PADDING_ABSOLUTE, PADDING_HALF)
BOTTOM_LEFT = (PADDING_HALF, width - PADDING_ABSOLUTE)
BOTTOM_RIGHT = (width - PADDING_ABSOLUTE, width - PADDING_ABSOLUTE)
CELL_SIZE_X = (width - PADDING_ABSOLUTE) / 8
CELL_SIZE_Y = (HEIGHT - PADDING_ABSOLUTE) / 8
TIME_RESTRICTION_SECONDS = 60 * time_restriction
POP_INCREASING_SIZE = 0.085 * width
