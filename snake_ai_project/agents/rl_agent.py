from __future__ import annotations

from pathlib import Path

import numpy as np

from agents.base import AgentDecision, BaseSnakeAgent, DirectionName, GameStateSnapshot

_MODEL_PATH = Path(__file__).parent.parent / "models" / "rl_model.pth"

_DIRECTION_DELTAS: dict[DirectionName, tuple[int, int]] = {
    "right": (1, 0),
    "left": (-1, 0),
    "up": (0, -1),
    "down": (0, 1),
}

_DELTA_TO_NAME: dict[tuple[int, int], DirectionName] = {v: k for k, v in _DIRECTION_DELTAS.items()}


def _turn_right(dx: int, dy: int) -> tuple[int, int]:
    return (-dy, dx)


def _turn_left(dx: int, dy: int) -> tuple[int, int]:
    return (dy, -dx)


class RLAgent(BaseSnakeAgent):
    mode = "rl"

    def __init__(self) -> None:
        self._model = None
        self._torch = None
        self._load_model()

    def _load_model(self) -> None:
        try:
            import torch
            from agents.rl_model import QNetwork

            self._torch = torch
            model = QNetwork()
            model.load_state_dict(
                torch.load(_MODEL_PATH, map_location="cpu", weights_only=True)
            )
            model.eval()
            self._model = model
            print(f"[RL] Model loaded from {_MODEL_PATH}")
        except FileNotFoundError:
            print(
                f"[RL] No trained model found at {_MODEL_PATH}.\n"
                "     Train first:  python snake_ai_project/train_rl.py\n"
                "     Falling back to straight-line movement."
            )
        except ImportError:
            print(
                "[RL] PyTorch is not installed.\n"
                "     Install it:  pip install torch\n"
                "     Falling back to straight-line movement."
            )

    def select_direction(self, state: GameStateSnapshot) -> AgentDecision:
        if self._model is None:
            return AgentDecision(debug_payload={"strategy": "no_model"})

        obs = self._build_obs(state)
        action = self._predict(obs)
        direction = self._action_to_direction(state.direction, action)

        return AgentDecision(
            next_direction=direction,
            debug_payload={"strategy": "rl_inference", "action": action},
        )

    def _build_obs(self, state: GameStateSnapshot) -> np.ndarray:
        head = state.snake[0]
        dx, dy = _DIRECTION_DELTAS[state.direction]
        blocked = set(state.obstacles) | set(state.snake[1:])

        def is_danger(ndx: int, ndy: int) -> bool:
            nx, ny = head[0] + ndx, head[1] + ndy
            return (nx, ny) in blocked or not (
                0 <= nx < state.grid_width and 0 <= ny < state.grid_height
            )

        rdx, rdy = _turn_right(dx, dy)
        ldx, ldy = _turn_left(dx, dy)

        return np.array([
            is_danger(dx, dy),
            is_danger(rdx, rdy),
            is_danger(ldx, ldy),
            dx == -1,
            dx == 1,
            dy == -1,
            dy == 1,
            state.apple_position[0] < head[0],
            state.apple_position[0] > head[0],
            state.apple_position[1] < head[1],
            state.apple_position[1] > head[1],
        ], dtype=np.float32)

    def _predict(self, obs: np.ndarray) -> int:
        torch = self._torch
        with torch.no_grad():
            tensor = torch.from_numpy(obs).unsqueeze(0)
            return int(self._model(tensor).argmax(dim=1).item())

    def _action_to_direction(self, current: DirectionName, action: int) -> DirectionName:
        dx, dy = _DIRECTION_DELTAS[current]
        if action == 1:
            dx, dy = _turn_right(dx, dy)
        elif action == 2:
            dx, dy = _turn_left(dx, dy)
        return _DELTA_TO_NAME.get((dx, dy), current)
