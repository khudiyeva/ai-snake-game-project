from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal


GridPos = tuple[int, int]
DirectionName = Literal["up", "down", "left", "right"]


@dataclass(frozen=True)
class GameStateSnapshot:
    snake: tuple[GridPos, ...]
    direction: DirectionName
    next_direction: DirectionName
    apple_position: GridPos
    obstacles: frozenset[GridPos]
    grid_width: int
    grid_height: int
    score: int
    speed: float
    game_over: bool
    apple_timer: float = 0.0
    steps_since_apple: int = 0


@dataclass(frozen=True)
class AgentDecision:
    next_direction: DirectionName | None = None
    debug_path: tuple[GridPos, ...] | None = None
    debug_payload: dict[str, Any] | None = None
    force_game_over: bool = False


class BaseSnakeAgent(ABC):
    mode: str

    def reset(self) -> None:
        return None

    def handle_event(self, event: Any) -> None:
        return None

    @abstractmethod
    def select_direction(self, state: GameStateSnapshot) -> AgentDecision:
        raise NotImplementedError
