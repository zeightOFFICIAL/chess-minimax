# Figures

Images used by the root `README.md`.

The screenshots are captured from the actual game running headlessly (SDL's `dummy` video
driver) against the real `redraw_gamewindow`, `start_screen`, `end_screen` and
`choose_promotion` code — they are not mock-ups. The two diagrams are drawn with Pillow.

| File | Source |
|------|--------|
| `hero.png` | Italian Game middlegame, white castled, bishop selected |
| `move-hints.png` | Close-up crop of the same frame |
| `start-screen.png` | Pre-game hotkey screen (cropped to content) |
| `check.png` | Black queen on h4 attacking e1 through the vacated f2 |
| `promotion-menu.png` | Promotion chooser (cropped to content) |
| `castling.png` | Before/after kingside castling, composed side by side |
| `end-screen.png` | Result screen drawn over a live board |
| `visual-sets.png` | Same position under `visual_set=0` and `visual_set=1` |
| `search-tree.png` | Alpha-beta pruning diagram |
| `benchmark.png` | Leaf-evaluation counts from the verification runs |
