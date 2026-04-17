# AI Snake Game Project

Simple Snake game built with Pygame.

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
- RL Agent (shown but intentionally disabled)

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

## Controls

- Arrow keys: move snake (human mode only)
- R: restart after game over
- Close window: quit game