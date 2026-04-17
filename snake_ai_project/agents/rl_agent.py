from __future__ import annotations

from agents.base import AgentDecision, BaseSnakeAgent, GameStateSnapshot


class RLAgent(BaseSnakeAgent):
    mode = "rl"
    available = False

    def select_direction(self, state: GameStateSnapshot) -> AgentDecision:
        del state
        return AgentDecision(
            debug_payload={"status": "reserved_for_future_implementation"}
        )
