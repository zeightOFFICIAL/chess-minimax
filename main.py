"""
PyChess with minimax AI
Copyright (C) 2023 Artemii Saganenko, Alexander Kuksin

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


Algorithms and data structures
Chess game (PyChess)

St. Petersburg State University of Telecommunications named after prof. M.A. Bonch-Bruevich
IKPI-04 (2022)
Saganenko Artemii, Kuksin Alexander

main.py
    - game.py
        (game objects)
        - board.py
            - piece.py
            - bishop.py
            - knight.py
            - king.py
            - pawn.py
            - queen.py
            - rook.py
        (game configuration)
        - flowingconfig.py
            - config.txt
        (playing algorithm)
        - algorithm.py
            - evalutaion.py

originally build on:
PyCharm 2021.3.3
Python 3.9

fully compatible with:
Python 3.11.0

18.06.2026
ver 926
main.py
"""

import game


def main():
    game.main()


if __name__ == "__main__":
    main()
