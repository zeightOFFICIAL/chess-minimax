# Figures

Images used by the root README.md.

The screenshots are taken from the game running headlessly, with SDL's `dummy` video driver, against the real `redraw_gamewindow`, `start_screen`, `end_screen` and `choose_promotion` code, so they show what the game actually draws and not a mock-up. The diagrams and the heatmaps are drawn with Pillow.

| File | What is on it |
|------|---------------|
| `hero.png` | Italian game middlegame, white castled, bishop selected |
| `move-hints.png` | Close-up of the same frame |
| `move-log.png` | Close-up of the move log strip after eighteen moves |
| `start-screen.png` | Hotkey screen before the game, cropped to the content |
| `check.png` | Black queen on h4 attacking e1 through the vacated f2 |
| `promotion-menu.png` | Choice of the promoted piece, cropped to the content |
| `castling.png` | Before and after kingside castling, composed side by side |
| `end-screen.png` | Result screen drawn over a real position |
| `visual-sets.png` | The same position with `visual_set=0` and `visual_set=1` |
| `piece-square-tables.png` | The six weighting tables as heatmaps |
| `minimax-tree.png` | Minimax diagram, values coming up from the leaves |
| `search-tree.png` | Alpha-beta pruning diagram |
| `benchmark.png` | Leaf counts from the verification runs |
