from __future__ import annotations

import random
from typing import Optional

import numpy as np

GRID_WIDTH = 40
GRID_HEIGHT = 30

# In screen coordinates y increases downward, so "up" is (0, -1).
_DIRECTION_DELTAS: dict[str, tuple[int, int]] = {
    "right": (1, 0),
    "left": (-1, 0),
    "up": (0, -1),
    "down": (0, 1),
}


def _turn_right(dx: int, dy: int) -> tuple[int, int]:
    """90° clockwise in screen coordinates: right→down, down→left, left→up, up→right."""
    return (-dy, dx)


def _turn_left(dx: int, dy: int) -> tuple[int, int]:
    """90° counter-clockwise in screen coordinates."""
    return (dy, -dx)


class SnakeEnv:
    """
    Headless Snake environment for fast RL training — no pygame dependency.

    Observation (11 binary floats):
        [danger_straight, danger_right, danger_left,
         dir_left, dir_right, dir_up, dir_down,
         food_left, food_right, food_up, food_down]

    Actions:
        0 = straight, 1 = turn right (CW), 2 = turn left (CCW)
    """

    # Episode terminates if the snake takes this many steps per unit of body
    # length without eating — prevents infinite loop episodes.
    _STALL_FACTOR = 100

    def __init__(self, obstacles: Optional[frozenset[tuple[int, int]]] = None) -> None:
        self.obstacles: frozenset[tuple[int, int]] = obstacles or frozenset()
        self.snake: list[tuple[int, int]] = []
        self.direction: tuple[int, int] = (1, 0)
        self.apple: tuple[int, int] = (0, 0)
        self.score: int = 0
        self.steps_since_apple: int = 0
        self.done: bool = False

    def reset(self) -> np.ndarray:
        cx, cy = GRID_WIDTH // 2, GRID_HEIGHT // 2
        self.snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)  # heading right
        self.score = 0
        self.steps_since_apple = 0
        self.done = False
        self.apple = self._spawn_apple()
        return self._get_obs()

    def step(self, action: int) -> tuple[np.ndarray, float, bool]:
        """Apply action, advance game one step. Returns (obs, reward, done)."""
        dx, dy = self.direction
        if action == 1:
            dx, dy = _turn_right(dx, dy)
        elif action == 2:
            dx, dy = _turn_left(dx, dy)
        self.direction = (dx, dy)

        head = self.snake[0]
        prev_dist = abs(head[0] - self.apple[0]) + abs(head[1] - self.apple[1])

        new_head = (head[0] + dx, head[1] + dy)
        will_grow = new_head == self.apple

        if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
            self.done = True
            return self._get_obs(), -10.0, True

        if new_head in self.obstacles:
            self.done = True
            return self._get_obs(), -10.0, True

        if new_head in self.snake:
            # Moving into the tail tip is safe only when the snake won't grow
            # (the tail vacates that cell this same step).
            if will_grow or new_head != self.snake[-1]:
                self.done = True
                return self._get_obs(), -10.0, True

        self.snake.insert(0, new_head)

        if will_grow:
            self.score += 1
            self.steps_since_apple = 0
            self.apple = self._spawn_apple()
            reward = 10.0
        else:
            self.snake.pop()
            new_dist = abs(new_head[0] - self.apple[0]) + abs(new_head[1] - self.apple[1])
            reward = 1.0 if new_dist < prev_dist else -1.0
            self.steps_since_apple += 1

            # Stall detection: snake is looping without eating
            if self.steps_since_apple > self._STALL_FACTOR * len(self.snake):
                self.done = True
                return self._get_obs(), -10.0, True

        return self._get_obs(), reward, False

    def _get_obs(self) -> np.ndarray:
        head = self.snake[0]
        dx, dy = self.direction
        blocked = set(self.obstacles) | set(self.snake[1:])

        def is_danger(ndx: int, ndy: int) -> bool:
            nx, ny = head[0] + ndx, head[1] + ndy
            return (nx, ny) in blocked or not (0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT)

        rdx, rdy = _turn_right(dx, dy)
        ldx, ldy = _turn_left(dx, dy)

        return np.array([
            is_danger(dx, dy),        # danger straight
            is_danger(rdx, rdy),      # danger right
            is_danger(ldx, ldy),      # danger left
            dx == -1,                 # moving left
            dx == 1,                  # moving right
            dy == -1,                 # moving up
            dy == 1,                  # moving down
            self.apple[0] < head[0],  # food left
            self.apple[0] > head[0],  # food right
            self.apple[1] < head[1],  # food up
            self.apple[1] > head[1],  # food down
        ], dtype=np.float32)

    def _spawn_apple(self) -> tuple[int, int]:
        occupied = set(self.snake) | self.obstacles
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in occupied:
                return pos
