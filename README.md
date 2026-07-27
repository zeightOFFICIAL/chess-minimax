<div align="center">

# ♟ PyChess — Minimax Chess Engine

**Application of the minimax decision-making method in game models**

A playable chess game in Python + PyGame, built around a from-scratch search engine:
minimax, alpha-beta pruning, MVV-LVA move ordering, Zobrist-hashed transposition tables
and piece-square evaluation.

A. V. Saganenko · A. A. Kuksin · A. V. Dagaev

*St. Petersburg State University of Telecommunications named after prof. M. A. Bonch-Bruevich*

![Python](https://img.shields.io/badge/python-3.9%20–%203.11-blue)
![PyGame](https://img.shields.io/badge/pygame-2.6.1-green)
![License](https://img.shields.io/badge/license-GPL--2.0-lightgrey)

![Gameplay](docs/images/hero.png)

</div>

---

## Table of contents

- [About](#about)
- [Quick start](#quick-start)
- [Gameplay](#gameplay)
- [Configuration](#configuration)
- [Project structure](#project-structure)
- [The engine](#the-engine)
  - [Board representation](#board-representation)
  - [Evaluation](#evaluation)
  - [Piece-square tables](#piece-square-tables)
  - [Minimax](#minimax)
  - [Alpha-beta pruning](#alpha-beta-pruning)
  - [MVV-LVA move ordering](#mvv-lva-move-ordering)
  - [Zobrist hashing and the transposition table](#zobrist-hashing-and-the-transposition-table)
  - [Make / unmake](#make--unmake)
- [Difficulty levels](#difficulty-levels)
- [Measured results](#measured-results)
- [Rules coverage](#rules-coverage)
- [Building an executable](#building-an-executable)
- [Adding a visual set](#adding-a-visual-set)
- [License](#license)

---

## About

The project was built to demonstrate that the minimax decision rule is applicable to real
game models. That required three things: formalising chess as a state space, implementing
the game itself, and implementing a search that plays it. The engine is written from
scratch — no chess library — and layers the standard optimisations (alpha-beta, move
ordering, transposition tables) on top of plain minimax so their individual effect can be
measured.

Roughly **1 900 lines of Python**, no engine dependencies: PyGame for rendering, NumPy only
for mirroring evaluation tables, `screeninfo` for window sizing.

---

## Quick start

Requires Python 3.9 – 3.11.

```bash
pip install -r requirements.txt
```

```bash
python main.py
```

---

## Gameplay

<div align="center">
<img src="docs/images/start-screen.png" width="49%" alt="Start screen">
<img src="docs/images/move-hints.png" width="49%" alt="Move hints">
</div>

Click a piece to select it — it enlarges and every legal destination is highlighted. Click a
destination to move. Moves that would leave your own king in check are rejected.

<div align="center">
<img src="docs/images/check.png" width="49%" alt="Check banner">
<img src="docs/images/promotion-menu.png" width="49%" alt="Promotion menu">
</div>

When a king is attacked a banner appears on that player's side. When a pawn reaches the far
rank, a menu opens and the player picks the promotion piece — queen, rook, bishop or knight.

<div align="center">
<img src="docs/images/castling.png" width="49%" alt="Castling">
<img src="docs/images/end-screen.png" width="49%" alt="End screen">
</div>

Castling is offered as a normal king move (two squares) whenever it is legal. The end screen
reports the winner and the elapsed game time.

### Hotkeys

| Key | Action |
|:---:|--------|
| `q` | Quit |
| `s` | Surrender |
| `p` | Vote for a draw (PvP only — both players must vote) |
| `r` | Restart, from the end screen |

---

## Configuration

Settings live in `config.txt` next to the executable and are read at startup. Anything
missing or malformed silently falls back to the default, so a broken config can never stop
the game from launching.

```ini
[settings]
game_mode=0
difficulty=3
visual_set=1
time_restriction=15
freeze_time=3
```

| Parameter | Values | Default | Description |
|-----------|--------|:-------:|-------------|
| `game_mode` | `0` = PvP (hotseat), `1` = PvE | `0` | Who plays black |
| `difficulty` | `0` – `3` | `0` | AI strength — see [difficulty levels](#difficulty-levels) |
| `visual_set` | integer | `0` | Subfolder of `resources/images/` holding an alternative sprite set |
| `time_restriction` | `0.5` – `60000` | `15` | Clock per player, in minutes |
| `freeze_time` | `0` – `10` | `3` | Delay on the help screen before the game begins |

---

## Project structure

```
python-chess-minimax/
├── main.py                     Entry point
├── game.py                     PyGame loop, rendering, input dispatch
├── config.txt                  Runtime configuration
│
├── configuration/
│   └── flowingconfig.py        Defaults, config parsing, derived geometry
│
├── gameobjects/                Rules and state
│   ├── board.py                Board state, move execution, check detection, castling
│   ├── piece.py                Base piece: sprites, drawing, selection
│   └── bishop|king|knight|pawn|queen|rook.py    Per-piece move generation
│
├── scripts/                    The engine
│   ├── algorithm.py            Minimax, alpha-beta, the four difficulty tiers
│   ├── evaluate.py             Material + piece-square evaluation, MVV-LVA scoring
│   └── zobrist.py              Zobrist hashing
│
├── dialogs/                    Screens and menus
│   ├── start_screen.py         Pre-game help screen
│   ├── end_screen.py           Result screen
│   ├── promotion_menu.py       Promotion piece chooser
│   └── fonts.py                Shared font objects
│
└── resources/                  Sprites, board textures, icons
```

**Dependencies**

| Package | Role |
|---------|------|
| PyGame | Rendering and input |
| NumPy | `flipud` to mirror piece-square tables for black |
| screeninfo | Detects display height to size the window |

---

## The engine

### Board representation

The board is an 8 × 8 list of lists. Empty squares hold the integer `0`; occupied squares
hold a `Piece` instance carrying its colour, position, and a cached `move_list`. Each piece
class implements `valid_moves(board)` — pseudo-legal generation that respects blocking and
capture rules but ignores self-check. Legality is settled at a higher level: a move is played,
the mover's king is tested for attack, and the move is rejected if it is in check.

`Board.update_moves()` refreshes every piece's `move_list`, then appends castling
destinations to each king (see below). `Board.get_danger_moves(color)` collects every square
the opponent attacks, which is what drives both check detection and castling legality.

### Evaluation

Two evaluation functions, both returning a score **from the perspective of the side to move**
(positive is good for that side).

**Simple** — pure material, used by difficulty 1:

$$E_{\text{simple}} = \sum_{p \,\in\, \text{own}} \text{value}(p) \;-\; \sum_{p \,\in\, \text{enemy}} \text{value}(p)$$

**Advanced** — material plus positional bonuses, used by difficulties 2 and 3:

$$E_{\text{adv}} = \sum_{p \,\in\, \text{own}} \Big( \text{value}(p) + \text{PST}_{p}[r_p][c_p] \Big) \;-\; \sum_{p \,\in\, \text{enemy}} \Big( \text{value}(p) + \text{PST}_{p}[r_p][c_p] \Big)$$

Piece values, in centipawns:

| | ♙ Pawn | ♘ Knight | ♗ Bishop | ♖ Rook | ♕ Queen | ♔ King |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Value** | 100 | 320 | 330 | 500 | 900 | 20 000 |

The king's nominal 20 000 makes losing it dominate every other term, so the search naturally
avoids lines where it hangs.

### Piece-square tables

Each piece type carries an 8 × 8 table of positional bonuses, encoding ideas like *knights
belong in the centre*, *pawns should advance*, and *the king should stay tucked away behind
its pawns in the middlegame*. Tables are written from white's perspective; black's are
generated once at import with `numpy.flipud`.

<details>
<summary><b>♙ Pawn</b> — reward advancement, discourage moving the pawns shielding a castled king</summary>

```
     a    b    c    d    e    f    g    h
8 │  0    0    0    0    0    0    0    0
7 │ 50   50   50   50   50   50   50   50
6 │ 10   10   20   30   30   20   10   10
5 │  5    5   10   25   25   10    5    5
4 │  0    0    0   20   20    0    0    0
3 │  5   -5  -10    0    0  -10   -5    5
2 │  5   10   10  -20  -20   10   10    5
1 │  0    0    0    0    0    0    0    0
```
</details>

<details>
<summary><b>♘ Knight</b> — strongly centralised; edges and corners heavily penalised</summary>

```
     a    b    c    d    e    f    g    h
8 │-50  -40  -30  -30  -30  -30  -40  -50
7 │-40  -20    0    0    0    0  -20  -40
6 │-30    0   10   15   15   10    0  -30
5 │-30    5   15   20   20   15    5  -30
4 │-30    0   15   20   20   15    0  -30
3 │-30    5   10   15   15   10    5  -30
2 │-40  -20    0    5    5    0  -20  -40
1 │-50  -40  -30  -30  -30  -30  -40  -50
```
</details>

<details>
<summary><b>♗ Bishop</b> — long diagonals rewarded, corners penalised</summary>

```
     a    b    c    d    e    f    g    h
8 │-20  -10  -10  -10  -10  -10  -10  -20
7 │-10    0    0    0    0    0    0  -10
6 │-10    0    5   10   10    5    0  -10
5 │-10    5    5   10   10    5    5  -10
4 │-10    0   10   10   10   10    0  -10
3 │-10   10   10   10   10   10   10  -10
2 │-10    5    0    0    0    0    5  -10
1 │-20  -10  -10  -10  -10  -10  -10  -20
```
</details>

<details>
<summary><b>♖ Rook</b> — the 7th rank is rewarded; a- and h-files slightly penalised</summary>

```
     a    b    c    d    e    f    g    h
8 │  0    0    0    0    0    0    0    0
7 │  5   10   10   10   10   10   10    5
6 │ -5    0    0    0    0    0    0   -5
5 │ -5    0    0    0    0    0    0   -5
4 │ -5    0    0    0    0    0    0   -5
3 │ -5    0    0    0    0    0    0   -5
2 │ -5    0    0    0    0    0    0   -5
1 │  0    0    0    5    5    0    0    0
```
</details>

<details>
<summary><b>♕ Queen</b> — mild centralisation, corners avoided</summary>

```
     a    b    c    d    e    f    g    h
8 │-20  -10  -10   -5   -5  -10  -10  -20
7 │-10    0    0    0    0    0    0  -10
6 │-10    0    5    5    5    5    0  -10
5 │ -5    0    5    5    5    5    0   -5
4 │  0    0    5    5    5    5    0   -5
3 │-10    5    5    5    5    5    0  -10
2 │-10    0    5    0    0    0    0  -10
1 │-20  -10  -10   -5   -5  -10  -10  -20
```
</details>

<details>
<summary><b>♔ King</b> — middlegame table: stay home, castled positions rewarded</summary>

```
     a    b    c    d    e    f    g    h
8 │-30  -40  -40  -50  -50  -40  -40  -30
7 │-30  -40  -40  -50  -50  -40  -40  -30
6 │-30  -40  -40  -50  -50  -40  -40  -30
5 │-30  -40  -40  -50  -50  -40  -40  -30
4 │-20  -30  -30  -40  -40  -30  -30  -20
3 │-10  -20  -20  -20  -20  -20  -20  -10
2 │ 20   20    0    0    0    0   20   20
1 │ 20   30   10    0    0   10   30   20
```
</details>

### Minimax

The search assumes both sides play optimally: the engine maximises its own evaluation while
assuming the opponent minimises it. For a state $s$ at remaining depth $d$:

$$
f(s, d) =
\begin{cases}
\text{evaluate}(s) & d = 0 \\[4pt]
\displaystyle\max_{m \,\in\, M(s)} f\big(s \cdot m,\; d-1\big) & \text{maximising ply} \\[10pt]
\displaystyle\min_{m \,\in\, M(s)} f\big(s \cdot m,\; d-1\big) & \text{minimising ply}
\end{cases}
$$

where $M(s)$ is the set of legal moves and $s \cdot m$ is the state after playing $m$.

```
                 MAX  (engine)          → picks max(3, 0, 2) = 3
                  │
        ┌─────────┼─────────┐
        │         │         │
        3         0         2            ← value returned by each reply
        │         │         │
       MIN       MIN       MIN           (opponent) → each picks its minimum
      ╱   ╲     ╱   ╲     ╱   ╲
     3     5   0    -1   2     5         ← leaf evaluations at depth 0
```

With branching factor $b$ and depth $d$, plain minimax visits $O(b^d)$ leaves.

### Alpha-beta pruning

Alpha-beta carries two bounds through the search: $\alpha$, the best value the maximiser can
already guarantee, and $\beta$, the best the minimiser can already guarantee. Once
$\beta \le \alpha$ the remaining moves at that node cannot influence the result and are
skipped.

$$
\text{prune when } \beta \le \alpha,
\qquad
\alpha \leftarrow \max(\alpha, v),
\qquad
\beta \leftarrow \min(\beta, v)
$$

![Alpha-beta search tree](docs/images/search-tree.png)

```
              MAX  [α=-∞, β=+∞]
               │
      ┌────────┼────────┐
      A        B        C  ✂            C is never searched
      3        2        ?
      │        │
     MIN      MIN  [α=3]
    ╱   ╲    ╱   ╲
   3     5  2     8

   A returns 3      → α = 3
   B returns 2 ≤ α  → C cannot improve on A → cut
```

The result is provably identical to plain minimax — pruning only removes branches that can
never change the answer. This is verified directly against an unpruned reference search; see
[measured results](#measured-results). In the best case the effective cost drops to
$O(b^{d/2})$, which is what makes the extra ply at difficulty 3 affordable.

### MVV-LVA move ordering

Alpha-beta only prunes well if strong moves are searched first — a good move found early
raises $\alpha$ and lets everything after it be cut. Moves are therefore sorted by
**Most Valuable Victim − Least Valuable Attacker**:

$$\text{score}(m) = \text{value}(\text{victim}) - 0.1 \cdot \text{value}(\text{attacker})$$

Quiet (non-capturing) moves score $-1$ and are searched last. Subtracting a fraction of the
attacker's value breaks ties in favour of capturing with the cheaper piece.

Example — a black knight (320) with several captures available:

| Move | Victim | Attacker | Score | Order |
|------|:------:|:--------:|------:|:-----:|
| ♞ × ♕ | 900 | 320 | 868 | 1st |
| ♞ × ♖ | 500 | 320 | 468 | 2nd |
| ♞ × ♗ | 330 | 320 | 298 | 3rd |
| ♞ × ♙ | 100 | 320 | 68 | 4th |
| ♞ → e5 | — | — | −1 | last |

### Zobrist hashing and the transposition table

The same position is often reached by different move orders. To avoid re-searching it, each
position gets a 64-bit key.

A table of random 64-bit integers is generated once at import, indexed
`[piece_type][colour][square]` — 6 × 2 × 64 values, seeded with `42` for reproducible runs.
The key of a position is the XOR of the entries for every occupied square:

$$H(s) = \bigoplus_{(p,\,c,\,q) \,\in\, s} Z[p][c][q]$$

Because XOR is its own inverse, the key updates incrementally in three operations rather than
rescanning the board — remove the piece from its origin, remove any captured piece, add the
piece at its destination:

$$H' = H \oplus Z[p][c][\text{from}] \;\oplus\; Z[p_{\text{cap}}][c_{\text{cap}}][\text{to}] \;\oplus\; Z[p][c][\text{to}]$$

Results are stored as `(value, depth, flag)` keyed by `(hash, depth, maximising)`, where the
flag records how the value relates to the search window:

| Flag | Meaning | Use on lookup |
|------|---------|---------------|
| `EXACT` | True value — the node fell inside the window | Return it directly |
| `LOWERBOUND` | Search failed high; true value is ≥ stored | Raise $\alpha$ |
| `UPPERBOUND` | Search failed low; true value is ≤ stored | Lower $\beta$ |

The table is capped at 10<sup>6</sup> entries and cleared wholesale when it fills.

### Make / unmake

The search does **not** copy the board. Every node applies its move in place and reverts it on
the way out:

```python
undo = board.make_move(origin, move, colour)
if not board.piece_is_checked(colour):
    value = minimax(board, depth - 1, alpha, beta, ...)
board.undo_move(undo)
```

`make_move` returns a small token holding everything needed to reverse the move exactly: the
squares involved, the captured piece and where it stood (which differs from the destination
for en passant), the pawn's first-move flag, the previous en passant target, castling rights,
and the rook's displacement if the move was a castle.

This replaced a `copy.deepcopy(board)` at every node. Deep-copying the whole object graph per
node was by far the dominant cost — removing it cut a depth-3 search from ~6–9 s to ~0.12 s,
roughly **60×**, without changing a single evaluation.

---

## Difficulty levels

| Diff | Strategy | Evaluation | Ordering | TT | Typical move time |
|:----:|----------|------------|:--------:|:--:|------------------:|
| **0** | Random legal move | — | — | — | ~2 ms |
| **1** | Greedy, 1 ply | Simple (material) | — | — | ~4 ms |
| **2** | Minimax, depth 2 | Advanced (material + PST) | MVV-LVA | ✔ | ~48 ms |
| **3** | Minimax, depth 3 + alpha-beta | Advanced (material + PST) | MVV-LVA | ✔ | ~125 ms |

Difficulty 1 falls back to a random choice when every move evaluates identically, so the
engine does not open with the same move every game.

**When in check**, all levels drop to a 1-ply search over legal escapes, scored with the
advanced evaluation. This guarantees the engine always escapes check when it can.

---

## Measured results

Verified by replaying the same positions through an exhaustive, unpruned reference minimax
and comparing both the returned value and the number of leaf evaluations.

**Position A — starting position, depth 3**

| Search | Value | Leaves | vs. exhaustive |
|--------|:-----:|-------:|---------------:|
| Exhaustive minimax | 50 | 8 902 | — |
| \+ alpha-beta | 50 | 1 017 | −88.6 % |
| \+ alpha-beta + MVV-LVA | 50 | 1 006 | −88.7 % |

**Position B — after 1. e4 e5 2. Nf3, depth 3**

| Search | Value | Leaves | vs. exhaustive |
|--------|:-----:|-------:|---------------:|
| Exhaustive minimax | 115 | 23 193 | — |
| \+ alpha-beta | 115 | 2 283 | −90.2 % |
| \+ alpha-beta + MVV-LVA | 115 | 1 393 | −94.0 % |

All three searches return the **identical value** in both positions, confirming that pruning
and ordering are optimisations, not approximations. Move ordering barely helps in the quiet
starting position — there are no captures to sort — but cuts a further 39 % once real captures
appear, which is exactly the expected behaviour.

![Benchmark](docs/images/benchmark.png)

---

## Rules coverage

| Rule | Status |
|------|:------:|
| Piece movement, blocking, captures | ✅ |
| Check detection | ✅ |
| Self-check prevention | ✅ |
| En passant | ✅ |
| Castling — both sides, with full legality checks | ✅ |
| Pawn promotion — player chooses ♕ ♖ ♗ ♘ | ✅ |
| Per-player clock | ✅ |
| Draw by agreement (PvP) | ✅ |
| Checkmate / stalemate detection | ❌ |
| Threefold repetition, fifty-move rule | ❌ |

Castling is validated fully: neither king nor rook may have moved, the squares between them
must be empty, and the king may not be in check, pass through an attacked square, or land on
one. The AI auto-promotes to a queen, since there is no player to ask mid-search.

**Checkmate is not detected.** A game ends by clock, surrender (`s`), or draw agreement (`p`).
In practice the search treats the king's 20 000 value as the win condition and plays toward
capturing it, which is behaviourally close but not the same thing.

---

## Building an executable

```bash
cicd\build.bat
```

Produces a single-file `dist\main.exe` via PyInstaller, with `resources/` bundled and
`config.txt` copied alongside so it stays user-editable. Both `flowingconfig.py` and
`piece.py` detect `sys.frozen` and resolve paths against the executable's directory.

---

## Adding a visual set

1. Create `resources/images/<n>/` where `<n>` is an integer.
2. Add all 14 PNGs — the 12 piece sprites (`w_`/`b_` × `pawn`, `knight`, `bishop`, `rook`,
   `queen`, `king`), the board texture `eq_chessboard.png`, and the two selection highlights
   `b_select.png` and `b2_select.png`. Use the default set in `resources/images/` as a
   template.
3. Set `visual_set=<n>` in `config.txt`.

If the folder or any file is missing, the game logs a warning and falls back to the **entire**
default set rather than mixing sprites from two themes.

![Visual sets](docs/images/visual-sets.png)

---

## License

Released under the **GNU General Public License v2.0 or later**. See [LICENSE](LICENSE).

Copyright © 2023 Artemii Saganenko, Alexander Kuksin.
