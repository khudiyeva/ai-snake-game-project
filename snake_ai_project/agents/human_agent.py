from __future__ import annotations

import pygame

from agents.base import AgentDecision, BaseSnakeAgent, DirectionName, GameStateSnapshot


_KEY_TO_DIRECTION: dict[int, DirectionName] = {
    pygame.K_UP: "up",
    pygame.K_DOWN: "down",
    pygame.K_LEFT: "left",
    pygame.K_RIGHT: "right",
}


class HumanAgent(BaseSnakeAgent):
    mode = "human"

    def __init__(self) -> None:
        self._pending_direction: DirectionName | None = None

    def reset(self) -> None:
        self._pending_direction = None

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key in _KEY_TO_DIRECTION:
            self._pending_direction = _KEY_TO_DIRECTION[event.key]

    def select_direction(self, state: GameStateSnapshot) -> AgentDecision:
        del state
        if self._pending_direction is None:
            return AgentDecision()

        direction = self._pending_direction
        self._pending_direction = None
        return AgentDecision(next_direction=direction)
