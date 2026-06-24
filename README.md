
# Python chess with minimax AI

## Simple and extremely buggy Chess with graphics and Minimax Algorithm for playing (AI)

## APPLICATION OF THE MINIMAX DECISION-MAKING METHOD IN GAME MODELS

### Authors: A.V. Saganenko, A.A. Kuksin, A.V. Dagaev

#### Saint Petersburg State University of Telecommunications

---

### Description

The project was created to prove the applicability of the Minimax method in game models. For this, work was carried out to formalize chess, develop the game itself in Python, and write an algorithm for the game based on the Minimax decision-making method. The algorithm uses game board weighting and the Alpha-Beta pruning optimization method.

---

### Launch conditions

Ensure all packages from `requirements.txt` are installed. Use any Python 3.6.9–3.11 interpreter.

```bash
python main.py
```

**Note:** `main.py` has a quirk — `if __name__ == "main":` (missing underscores). The game still works because `game.py` calls `main()` at module level, but `python main.py` alone does nothing. To launch directly, use `python game.py`.

### Building a standalone executable

Run `cicd\build.bat` to build a single-file `.exe` via PyInstaller:

```bat
cicd\build.bat
```

The output `main.exe` and `config.txt` will be placed in `dist\`. The executable uses `resources/icons/icon.ico` as its file icon.

### Adding a new visual set

To add a custom visual theme:

1. Create a new folder under `resources/images/` with the next integer name (e.g. `resources/images/2/`)
2. Place all required PNG files inside it (14 files — see the file list below; use the default set as a template)
3. Set `visual_set=2` in `config.txt`

**Required files in the custom folder:**

| File | Description |
|------|-------------|
| `eq_chessboard.png` | Board texture |
| `b_bishop.png` through `b_rook.png` | 6 black piece sprites |
| `w_bishop.png` through `w_rook.png` | 6 white piece sprites |
| `b_select.png` | Selection highlight (black's turn) |
| `b2_select.png` | Selection highlight (white's turn) |

**Fallback behavior:** If the folder is missing, or any file within it fails to load, the game falls back to the default set (root `resources/images/`) and logs a warning. This prevents mixed visuals.

### Dependencies

| Package | Role |
|---------|------|
| PyGame | Board & piece rendering, input handling |
| NumPy | Piece-square table operations (`flipud` for black-side table mirroring) |
| screeninfo | Auto-detection of display resolution for window sizing |

---

### Architecture

```
python-chess-minimax/
├── main.py                          # Entry point (see quirk above)
├── game.py                          # Pygame loop, rendering, input dispatch
├── config.txt                       # Runtime configuration overrides
├── configuration/
│   └── flowingconfig.py             # Reads config.txt, sets globals (board size, game mode, difficulty, etc.)
├── gameobjects/
│   ├── board.py                     # Board class: move validation, check detection, piece management
│   ├── piece.py                     # Base piece class
│   ├── bishop.py / king.py / knight.py / pawn.py / queen.py / rook.py
├── scripts/
│   ├── algorithm.py                 # Solution class with 4 AI difficulty levels
│   ├── evaluate.py                  # Board evaluation functions (simple & advanced)
│   └── zobrist.py                   # Zobrist hashing for transposition table keys
├── resources/
│   ├── images/                      # Piece sprites & board image; subfolders for alternative visual sets
│   └── icons/
```

---

### Configuration (`config.txt`)

| Parameter | Values | Description |
|-----------|--------|-------------|
| `game_mode` | `0` = PvP, `1` = PvE | Game mode |
| `difficulty` | `0`–`3` | AI difficulty (see below) |
| `visual_set` | integer | Subfolder name for alternative piece/board sprites |
| `freeze_time` | `0`–`10` | Delay (seconds) before the game starts |
| `time_restriction` | `0.5`–`60000` | Time limit per player (minutes); clamped to `[0.5, 60000]` |

Defaults are defined in `configuration/flowingconfig.py` and overridden at startup by `config.txt`.

---

### AI Difficulty Levels

All AI logic lives in `scripts/algorithm.py` (`class Solution`). The type of evaluation used at each level is defined in `scripts/evaluate.py`.

| Diff | Strategy | Evaluation | Time |
|------|----------|------------|------|
| 0 | Random valid move | None | ~0.5 s |
| 1 | Greedy 1-ply best move | Simple material count | ~1 s |
| 2 | Minimax depth 2 + MVV-LVA move ordering + transposition table | Advanced (material + PST) | ~2–3 s |
| 3 | Minimax depth 3 + Alpha-Beta pruning + MVV-LVA ordering + transposition table | Advanced (material + PST) | ~6–9 s |

---

### Algorithmic Details

#### Board Evaluation

**Simple evaluation** (`evaluate_board`):
Sum of material values for each side. If `color == "w"` returns `white_score - black_score`, else the opposite.

$$E = \sum_{p \in \text{pieces}} \text{value}(p)$$
$$\text{value} = \{\text{Pawn}:100,\ \text{Knight}:320,\ \text{Bishop}:330,\ \text{Rook}:500,\ \text{Queen}:900,\ \text{King}:20000\}$$

**Advanced evaluation** (`evaluate_board_advanced`):
Material value plus piece-square table (PST) positional bonuses:

$$E = \sum_{p \in \text{pieces}} \big(\text{value}(p) + \text{PST}[p.\text{type}][\text{row}][\text{col}]\big)$$

PSTs are defined for each piece type from white's perspective. Black's tables are obtained by vertically mirroring (`numpy.flipud`) the white tables, ensuring symmetric positional knowledge.

#### MVV-LVA Move Ordering

In `scripts/evaluate.py:mvv_lva_score`, moves are ordered by Most Valuable Victim — Least Valuable Attacker:

$$\text{score} = \text{value}(\text{victim}) - 0.1 \times \text{value}(\text{attacker})$$

Captures are searched first (higher victim value), and among equal victims, the least valuable attacker is preferred. Non-captures get a score of −1 so they are searched last. This accelerates Alpha-Beta pruning by finding strong moves early.

#### Minimax Algorithm

The core recursive decision rule. For a game state $s$ with depth $d$, the AI chooses the move that maximizes its position assuming the opponent tries to minimize it.

$$f(s, d) = \begin{cases}
\text{evaluate}(s) & \text{if } d = 0 \text{ or terminal} \\
\max_{m \in \text{moves}} f(\text{apply}(s, m), d - 1) & \text{if maximizing player} \\
\min_{m \in \text{moves}} f(\text{apply}(s, m), d - 1) & \text{if minimizing player}
\end{cases}$$

Implementation in `algorithm.py:minimax()`:
- **Maximizing** (AI's turn): picks child with highest value, updates `alpha = max(alpha, best)`
- **Minimizing** (opponent's turn): picks child with lowest value, updates `beta = min(beta, best)`

#### Alpha-Beta Pruning (Difficulty 3)

Reduces the search tree by pruning branches that cannot affect the final decision:

$$f(s, d, \alpha, \beta) = \begin{cases}
\text{evaluate}(s) & \text{if } d = 0 \\
\max_{m} f(\text{apply}(s, m), d - 1, \alpha, \beta) & \text{maximizing, prune if } f \geq \beta \\
\min_{m} f(\text{apply}(s, m), d - 1, \alpha, \beta) & \text{minimizing, prune if } f \leq \alpha
\end{cases}$$

Where:
- $\alpha$ — best value the maximizer can guarantee so far (starts at $-\infty$)
- $\beta$ — best value the minimizer can guarantee so far (starts at $+\infty$)

At difficulty 3, alpha-beta is used at the root as well: after evaluating each root candidate, `alpha = max(alpha, best_value)` is updated, and the loop breaks when `beta <= alpha`.

#### Zobrist Hashing & Transposition Table

`scripts/zobrist.py` implements Zobrist hashing for efficient state identification:

1. A $6 \times 2 \times 64$ table of random 64-bit integers is pre-generated (seeded with `42` for reproducibility).
2. Board hash is the XOR of all `ZOBRIST_TABLE[piece_type][color][square]` for every occupied square.
3. Incremental update on move: XOR out the moving piece from its source square, XOR out any captured piece from its destination, XOR in the moving piece at the destination.

The transposition table (`algorithm.py`, `TTEntry`) stores `(value, depth, flag)` keyed by `(z_hash, depth, maximizing)`. Flags:
- `EXACT` — exact evaluation
- `LOWERBOUND` — fail-low node (value ≥ stored)
- `UPPERBOUND` — fail-high node (value ≤ stored)

This avoids re-searching identical positions reached via different move orders and provides pruning information to Alpha-Beta.

---

### Check Handling

When in check, all difficulty levels fall back to a 1-ply search that evaluates each legal escape move with the advanced evaluation function (no deeper search). This guarantees the AI always escapes check when possible.

---

### Known Limitations & Missing Features

| Feature | Status |
|---------|--------|
| Castling (roque) | Not implemented |
| En passant | Not implemented |
| Pawn promotion | Always promotes to Queen only |
| Checkmate detection | Not explicitly implemented; game relies on players surrendering (`s` key) |
| Draw detection | PvP only — toggle draw vote with `p` key |

---

### Hotkeys (in-game)

| Key | Action |
|-----|--------|
| `q` | Quit game |
| `s` | Surrender |
| `p` | Toggle draw vote (PvP only) |

---

### Project Status

This is an academic project. The AI is fully functional at all four difficulty levels, but the game logic lacks several standard chess rules. The architecture supports easy extension for castling, en passant, and promotion choices with moderate refactoring of `Board.move()` and `Board.simple_move()`.
