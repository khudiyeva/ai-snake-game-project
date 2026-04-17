# AI Snake Game Project

A Snake game built with Pygame that benchmarks **A\* pathfinding vs Reinforcement Learning**. A\* is fully implemented; the RL agent is the planned next phase. The goal is a side-by-side performance comparison of classical search against a learned policy.

## Requirements

- Python 3.12+
- Linux/macOS/Windows terminal
- GUI display session (X11, Wayland, or native desktop)

## Setup

1. Create virtual environment:

```bash
python3 -m venv .venv
```

2. Activate virtual environment:

```bash
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r snake_ai_project/requirements.txt
```

## Run The Game

From project root:

### Interactive menu (default)

Launch without `--mode` to pick from an in-game menu:

```bash
.venv/bin/python snake_ai_project/main.py
```

Menu options:

- Human
- A* Agent
- RL Agent (shown but intentionally disabled — reserved for future implementation)

### CLI mode (bypasses menu)

Use this for reproducible runs and automation.

#### Human mode (keyboard control)

```bash
.venv/bin/python snake_ai_project/main.py --mode human
```

#### A* mode (AI controls snake)

```bash
.venv/bin/python snake_ai_project/main.py --mode astar
```

#### RL mode status

`--mode rl` is reserved for future implementation and currently exits with a clear message.

### Loading a custom map

Pass `--map` with a path to a `.txt` file to replace the random obstacles with a fixed layout:

```bash
.venv/bin/python snake_ai_project/main.py --mode astar --map maps/map_cross.txt
```

Map files are **30 rows × 40 columns** of space-separated `0`s (free) and `1`s (obstacle). The six included maps in `maps/` are:

| File | Pattern |
|------|---------|
| `map_pillars.txt` | Evenly spaced 1×1 pillars |
| `map_cross.txt` | Two horizontal + two vertical walls creating 9 zones with doorways |
| `map_zigzag.txt` | Alternating horizontal walls forcing an S-shaped path |
| `map_rooms.txt` | Three horizontal chambers with staggered doorways |
| `map_border.txt` | Inner rectangular frame with corner towers |
| `map_spiral.txt` | Three concentric L-shaped rings with a walled inner chamber |

The map reloads on every restart (`R`), so edits to the file are picked up immediately. If a file cannot be loaded, the game falls back to random obstacles and prints a warning.

## Controls

| Key | Action |
|-----|--------|
| Arrow keys | Move snake (human mode only) |
| P | Pause / Resume |
| ESC (while paused) | Return to main menu |
| R (game over) | Restart |
| Close window | Quit |

## Scoring

Each apple awards **base points** plus two optional bonuses:

- **Time bonus** — eating the apple sooner earns up to 2× the base points. The bonus decays linearly to zero at 15 seconds. The timer pauses when the game is paused.
- **Path efficiency bonus** — if the snake takes the optimal (Manhattan-distance) path to the apple it earns an additional 1× the base points. Longer detours reduce this bonus proportionally.

Maximum score per apple is therefore **4×** base points (instant eat, perfect path).

Apple types and base points:

| Apple | Points | Speed boost |
|-------|--------|-------------|
| Yellow (small) | 1 | +0.5 |
| Orange (medium) | 3 | +1.5 |
| Red (large) | 5 | +2.5 |

## Linux and WSL Notes

- The game requires a working display backend.
- On Linux/WSL, startup warnings mentioning ALSA or libEGL are often non-blocking if the game window still appears.
- If no window appears, follow troubleshooting below.

## Troubleshooting

### Startup prints messages but no window appears

1. Confirm a display variable exists:

```bash
echo "$DISPLAY" "$WAYLAND_DISPLAY"
```

2. If both are empty, run inside a GUI desktop session or use X11 forwarding.

3. In WSL:

- Windows 11: enable WSLg and run `wsl --update`.
- Older setups: run an X server on Windows and export `DISPLAY` in WSL.

4. Check `SDL_VIDEODRIVER` is not set to `dummy`:

```bash
echo "$SDL_VIDEODRIVER"
```
