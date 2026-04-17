WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CELL_SIZE = 20

RENDER_FPS = 60
START_SPEED = 5
MAX_SPEED = 160
NUM_OBSTACLES = 25

# Control modes
CONTROL_MODES = ("human", "astar", "rl")
ACTIVE_CONTROL_MODES = ("human", "astar")
DISABLED_CONTROL_MODES = ("rl",)

# Menu options in display order.
MENU_OPTIONS = (
    ("human", "Human"),
    ("astar", "A* Agent"),
    ("rl", "RL Agent (Coming Soon)"),
)

DEFAULT_CONTROL_MODE = "human"

# Draw AI planned path when enabled.
SHOW_AI_PATH_DEBUG = True

# Time-based and efficiency scoring
MAX_APPLE_TIME: float = 15.0
TIME_BONUS_MULTIPLIER: int = 2
EFFICIENCY_BONUS_MULTIPLIER: int = 1