
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

Simply run `python main.py`.

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
├── main.py                          # Entry point (`if __name__ == "__main__"` calls `game.main()`)
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

**Simple evaluation** (`evaluate_board`) — pure material count:

$$E = \sum_{p \in \text{pieces}} \text{value}(p)$$

| Piece | ♙ Pawn | ♘ Knight | ♗ Bishop | ♖ Rook | ♕ Queen | ♔ King |
|-------|--------|----------|----------|--------|---------|--------|
| Value | 100 | 320 | 330 | 500 | 900 | 20000 |

**Advanced evaluation** (`evaluate_board_advanced`) — material + Piece-Square Table (PST):

$$E = \sum_{p \in \text{pieces}} \big(\text{value}(p) + \text{PST}[p.\text{type}][\text{row}][\text{col}]\big)$$

PSTs assign a bonus/penalty to each square per piece type, encoding positional knowledge (center control, pawn structure, king safety). Black's tables are mirrored vertically (`numpy.flipud`) for symmetry.

##### ♙ Pawn PST (white)

```
  a    b    c    d    e    f    g    h
┌────┬────┬────┬────┬────┬────┬────┬────┐
│  0 │  0 │  0 │  0 │  0 │  0 │  0 │  0 │ 8
├────┼────┼────┼────┼────┼────┼────┼────┤
│ 50 │ 50 │ 50 │ 50 │ 50 │ 50 │ 50 │ 50 │ 7
├────┼────┼────┼────┼────┼────┼────┼────┤
│ 10 │ 10 │ 20 │ 30 │ 30 │ 20 │ 10 │ 10 │ 6
├────┼────┼────┼────┼────┼────┼────┼────┤
│  5 │  5 │ 10 │ 25 │ 25 │ 10 │  5 │  5 │ 5
├────┼────┼────┼────┼────┼────┼────┼────┤
│  0 │  0 │  0 │ 20 │ 20 │  0 │  0 │  0 │ 4
├────┼────┼────┼────┼────┼────┼────┼────┤
│  5 │ -5 │-10 │  0 │  0 │-10 │ -5 │  5 │ 3
├────┼────┼────┼────┼────┼────┼────┼────┤
│  5 │ 10 │ 10 │-20 │-20 │ 10 │ 10 │  5 │ 2
├────┼────┼────┼────┼────┼────┼────┼────┤
│  0 │  0 │  0 │  0 │  0 │  0 │  0 │  0 │ 1
└────┴────┴────┴────┴────┴────┴────┴────┘
```

##### ♘ Knight PST (white)

```
  a    b    c    d    e    f    g    h
┌────┬────┬────┬────┬────┬────┬────┬────┐
│-50 │-40 │-30 │-30 │-30 │-30 │-40 │-50 │ 8
├────┼────┼────┼────┼────┼────┼────┼────┤
│-40 │-20 │  0 │  0 │  0 │  0 │-20 │-40 │ 7
├────┼────┼────┼────┼────┼────┼────┼────┤
│-30 │  0 │ 10 │ 15 │ 15 │ 10 │  0 │-30 │ 6
├────┼────┼────┼────┼────┼────┼────┼────┤
│-30 │  5 │ 15 │ 20 │ 20 │ 15 │  5 │-30 │ 5
├────┼────┼────┼────┼────┼────┼────┼────┤
│-30 │  0 │ 15 │ 20 │ 20 │ 15 │  0 │-30 │ 4
├────┼────┼────┼────┼────┼────┼────┼────┤
│-30 │  5 │ 10 │ 15 │ 15 │ 10 │  5 │-30 │ 3
├────┼────┼────┼────┼────┼────┼────┼────┤
│-40 │-20 │  0 │  5 │  5 │  0 │-20 │-40 │ 2
├────┼────┼────┼────┼────┼────┼────┼────┤
│-50 │-40 │-30 │-30 │-30 │-30 │-40 │-50 │ 1
└────┴────┴────┴────┴────┴────┴────┴────┘
```

##### ♗ Bishop PST (white)

```
  a    b    c    d    e    f    g    h
┌────┬────┬────┬────┬────┬────┬────┬────┐
│-20 │-10 │-10 │-10 │-10 │-10 │-10 │-20 │ 8
├────┼────┼────┼────┼────┼────┼────┼────┤
│-10 │  0 │  0 │  0 │  0 │  0 │  0 │-10 │ 7
├────┼────┼────┼────┼────┼────┼────┼────┤
│-10 │  0 │  5 │ 10 │ 10 │  5 │  0 │-10 │ 6
├────┼────┼────┼────┼────┼────┼────┼────┤
│-10 │  5 │  5 │ 10 │ 10 │  5 │  5 │-10 │ 5
├────┼────┼────┼────┼────┼────┼────┼────┤
│-10 │  0 │ 10 │ 10 │ 10 │ 10 │  0 │-10 │ 4
├────┼────┼────┼────┼────┼────┼────┼────┤
│-10 │ 10 │ 10 │ 10 │ 10 │ 10 │ 10 │-10 │ 3
├────┼────┼────┼────┼────┼────┼────┼────┤
│-10 │  5 │  0 │  0 │  0 │  0 │  5 │-10 │ 2
├────┼────┼────┼────┼────┼────┼────┼────┤
│-20 │-10 │-10 │-10 │-10 │-10 │-10 │-20 │ 1
└────┴────┴────┴────┴────┴────┴────┴────┘
```

##### ♖ Rook PST (white)

```
  a    b    c    d    e    f    g    h
┌────┬────┬────┬────┬────┬────┬────┬────┐
│  0 │  0 │  0 │  0 │  0 │  0 │  0 │  0 │ 8
├────┼────┼────┼────┼────┼────┼────┼────┤
│  5 │ 10 │ 10 │ 10 │ 10 │ 10 │ 10 │  5 │ 7
├────┼────┼────┼────┼────┼────┼────┼────┤
│ -5 │  0 │  0 │  0 │  0 │  0 │  0 │ -5 │ 6
├────┼────┼────┼────┼────┼────┼────┼────┤
│ -5 │  0 │  0 │  0 │  0 │  0 │  0 │ -5 │ 5
├────┼────┼────┼────┼────┼────┼────┼────┤
│ -5 │  0 │  0 │  0 │  0 │  0 │  0 │ -5 │ 4
├────┼────┼────┼────┼────┼────┼────┼────┤
│ -5 │  0 │  0 │  0 │  0 │  0 │  0 │ -5 │ 3
├────┼────┼────┼────┼────┼────┼────┼────┤
│ -5 │  0 │  0 │  0 │  0 │  0 │  0 │ -5 │ 2
├────┼────┼────┼────┼────┼────┼────┼────┤
│  0 │  0 │  0 │  5 │  5 │  0 │  0 │  0 │ 1
└────┴────┴────┴────┴────┴────┴────┴────┘
```

##### ♕ Queen PST (white)

```
  a    b    c    d    e    f    g    h
┌────┬────┬────┬────┬────┬────┬────┬────┐
│-20 │-10 │-10 │ -5 │ -5 │-10 │-10 │-20 │ 8
├────┼────┼────┼────┼────┼────┼────┼────┤
│-10 │  0 │  0 │  0 │  0 │  0 │  0 │-10 │ 7
├────┼────┼────┼────┼────┼────┼────┼────┤
│-10 │  0 │  5 │  5 │  5 │  5 │  0 │-10 │ 6
├────┼────┼────┼────┼────┼────┼────┼────┤
│ -5 │  0 │  5 │  5 │  5 │  5 │  0 │ -5 │ 5
├────┼────┼────┼────┼────┼────┼────┼────┤
│  0 │  0 │  5 │  5 │  5 │  5 │  0 │ -5 │ 4
├────┼────┼────┼────┼────┼────┼────┼────┤
│-10 │  5 │  5 │  5 │  5 │  5 │  0 │-10 │ 3
├────┼────┼────┼────┼────┼────┼────┼────┤
│-10 │  0 │  5 │  0 │  0 │  0 │  0 │-10 │ 2
├────┼────┼────┼────┼────┼────┼────┼────┤
│-20 │-10 │-10 │ -5 │ -5 │-10 │-10 │-20 │ 1
└────┴────┴────┴────┴────┴────┴────┴────┘
```

##### ♔ King PST (white)

```
  a    b    c    d    e    f    g    h
┌────┬────┬────┬────┬────┬────┬────┬────┐
│-30 │-40 │-40 │-50 │-50 │-40 │-40 │-30 │ 8
├────┼────┼────┼────┼────┼────┼────┼────┤
│-30 │-40 │-40 │-50 │-50 │-40 │-40 │-30 │ 7
├────┼────┼────┼────┼────┼────┼────┼────┤
│-30 │-40 │-40 │-50 │-50 │-40 │-40 │-30 │ 6
├────┼────┼────┼────┼────┼────┼────┼────┤
│-30 │-40 │-40 │-50 │-50 │-40 │-40 │-30 │ 5
├────┼────┼────┼────┼────┼────┼────┼────┤
│-20 │-30 │-30 │-40 │-40 │-30 │-30 │-20 │ 4
├────┼────┼────┼────┼────┼────┼────┼────┤
│-10 │-20 │-20 │-20 │-20 │-20 │-20 │-10 │ 3
├────┼────┼────┼────┼────┼────┼────┼────┤
│ 20 │ 20 │  0 │  0 │  0 │  0 │ 20 │ 20 │ 2
├────┼────┼────┼────┼────┼────┼────┼────┤
│ 20 │ 30 │ 10 │  0 │  0 │ 10 │ 30 │ 20 │ 1
└────┴────┴────┴────┴────┴────┴────┴────┘
```

#### Minimax Algorithm

The core recursive decision rule. For a game state $s$ with depth $d$, the AI chooses the move that maximizes its position assuming the opponent tries to minimize it.

$$f(s, d) = \begin{cases}
\text{evaluate}(s) & \text{if } d = 0 \text{ or terminal} \\
\max_{m \in \text{moves}} f(\text{apply}(s, m), d - 1) & \text{if maximizing player} \\
\min_{m \in \text{moves}} f(\text{apply}(s, m), d - 1) & \text{if minimizing player}
\end{cases}$$

**Search tree at depth 3 (difficulty 2 / 3):**

```
                  MAX ── Root (AI)
                  │
          ┌───────┼───────────┐
          │       │           │
       Move a  Move b  ... Move n
          │       │           │
     ┌────┴┐   ┌─┴──┐    ┌───┴──┐
     │    │   │    │    │      │        MIN ── Opponent replies
     v    v   v    v    v      v
   eval  eval eval eval eval  eval

  ── depth 1: opponent's best (min) is propagated up
  ── depth 2: AI's best (max) among opponent's replies
  ── depth 3: if using minimax depth 3, one more ply
```

**Minimax propagation at depth 2:**

```
     MAX ── Root          ── selects max(3, 0, 2) = 3
      │
  ┌───┼───┐
  3   0   2               <── values after one opponent ply
  │   │   │
  MIN MIN MIN             ── each MIN selects its minimum
 / \ / \ / \
2 3 0-1 2 5               <── leaf evaluations (depth 0)
```

Implementation: `algorithm.py:minimax()`:
- **Maximizing** (AI's turn): tracks `best = max(best, value)`, updates `alpha`
- **Minimizing** (opponent's turn): tracks `best = min(best, value)`, updates `beta`

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

**Pruning example — branch C is cut:**

```
         MAX ── Root  [α=-∞, β=+∞]
          │
    ┌─────┼──────┐
    │     │      │
    A     B      C ✂︎             <── C pruned
    3     2     ???

    │     │
    MIN   MIN  [α=3, β=+∞]
   / \   / \
  3  5  2  8

  After A returns 3 → α=3 at root.
  B returns 2 (≤ α), so C cannot improve.
  β=α → prune.
```

At difficulty 3, alpha-beta is applied at the root level: `alpha = max(alpha, best_value)` after each candidate, and the loop breaks immediately when `beta <= alpha`.

#### MVV-LVA Move Ordering

Moves are ordered by **Most Valuable Victim — Least Valuable Attacker** to feed strong captures to Alpha-Beta first:

$$\text{score} = \text{value}(\text{victim}) - 0.1 \times \text{value}(\text{attacker})$$

Non-captures get score = −1 and are searched last.

**Example — black ♞ (320) captures white pieces:**

| Capture | Victim | Attacker | Score | Search order |
|---------|--------|----------|-------|--------------|
| ♞ x ♕  | 900    | 320      | 868   | 1st          |
| ♞ x ♖  | 500    | 320      | 468   | 2nd          |
| ♞ x ♗  | 330    | 320      | 298   | 3rd          |
| ♞ x ♙  | 100    | 320      | 68    | 4th          |
| ♞ e5   | —      | —        | −1    | last         |

Captures of queens are searched first, then rooks, bishops/knights, pawns — and positional moves last. This maximizes pruning efficiency by establishing a strong alpha bound early.

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
| En passant | ✅ Implemented |
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

This is an academic project. The AI is fully functional at all four difficulty levels, but the game logic lacks several standard chess rules. The architecture supports easy extension for castling and promotion choices with moderate refactoring of `Board.move()` and `Board.simple_move()`.
