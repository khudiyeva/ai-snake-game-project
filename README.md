# AI Snake Game Project

A Snake game built with Pygame that benchmarks **A\* pathfinding vs Reinforcement Learning**. Both agents are fully implemented and playable. The goal is a side-by-side performance comparison of classical search against a learned policy.

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

> **Note:** `torch` (~2 GB) is downloaded on first install. This may take a few minutes depending on your connection.

## Training the RL Agent

Before using `--mode rl`, train the DQN model once:

```bash
.venv/bin/python snake_ai_project/train_rl.py
```

This runs 500 headless training episodes (~2–5 min on CPU) and saves the model to `snake_ai_project/models/rl_model.pth`. You can increase the episode count for a stronger agent:

```bash
.venv/bin/python snake_ai_project/train_rl.py --episodes 2000
```

Training prints progress every 100 episodes and saves the best model (by 100-episode mean score) plus a final checkpoint.

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
- RL Agent

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

#### RL mode (trained DQN agent)

Requires a trained model (see [Training the RL Agent](#training-the-rl-agent) above).

```bash
.venv/bin/python snake_ai_project/main.py --mode rl
```

If the model file is missing, the agent prints a clear message guiding you to run the training script first.

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

## Agent Overview

### A* Agent

Three-tier fallback strategy:
1. **Apple path** — A* to the apple, avoiding body and obstacles.
2. **Tail chase** — if no apple path exists, A* to own tail tip (keeps the snake from boxing itself in).
3. **Safest direction** — BFS flood-fill from each candidate move; picks the direction with the most reachable free cells. If no safe move exists, triggers game over gracefully.

### RL Agent (DQN)

A Deep Q-Network trained entirely in a headless Python environment (no pygame during training).

**Observation** — 11 binary features per step:
```
[danger_straight, danger_right, danger_left,
 dir_left, dir_right, dir_up, dir_down,
 food_left, food_right, food_up, food_down]
```

**Actions** — 3 relative moves (straight, turn right, turn left). Relative actions prevent the snake from ever reversing into itself.

**Reward** — +10 apple, −10 death, ±1 for moving toward/away from food.

**Architecture** — MLP 11→256→256→3, trained with experience replay and a target network (synced every 100 gradient steps).

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

### RL agent moves in a straight line

The model file exists but may be undertrained. Re-run training with more episodes:

```bash
.venv/bin/python snake_ai_project/train_rl.py --episodes 1000
```
