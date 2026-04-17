from __future__ import annotations

from agents.base import AgentDecision, BaseSnakeAgent, DirectionName, GameStateSnapshot
from game.utils import a_star_search, reachable_cell_count


_DIRECTION_ORDER: tuple[DirectionName, ...] = ("up", "down", "left", "right")
_DIRECTION_DELTAS: dict[DirectionName, tuple[int, int]] = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}


class AStarAgent(BaseSnakeAgent):
    mode = "astar"

    def select_direction(self, state: GameStateSnapshot) -> AgentDecision:
        head = state.snake[0]

        blocked_for_apple = set(state.obstacles) | set(state.snake[1:])
        apple_path = a_star_search(
            start=head,
            goal=state.apple_position,
            blocked_cells=blocked_for_apple,
            grid_width=state.grid_width,
            grid_height=state.grid_height,
        )
        if len(apple_path) >= 2:
            direction = self._direction_from_positions(head, apple_path[1])
            if direction is not None:
                return AgentDecision(
                    next_direction=direction,
                    debug_path=tuple(apple_path),
                    debug_payload={"strategy": "apple_path"},
                )

        tail = state.snake[-1]
        blocked_for_tail = set(state.obstacles) | set(state.snake[1:-1])
        tail_path = a_star_search(
            start=head,
            goal=tail,
            blocked_cells=blocked_for_tail,
            grid_width=state.grid_width,
            grid_height=state.grid_height,
        )
        if len(tail_path) >= 2:
            direction = self._direction_from_positions(head, tail_path[1])
            if direction is not None:
                return AgentDecision(
                    next_direction=direction,
                    debug_path=tuple(tail_path),
                    debug_payload={"strategy": "tail_path"},
                )

        safest_direction = self._choose_safest_direction(state)
        if safest_direction is None:
            return AgentDecision(
                debug_path=tuple(),
                debug_payload={"strategy": "no_safe_move"},
                force_game_over=True,
            )

        next_pos = self._next_position_for_direction(head, safest_direction)
        return AgentDecision(
            next_direction=safest_direction,
            debug_path=(head, next_pos),
            debug_payload={"strategy": "safest_move"},
        )

    def _direction_from_positions(self, current: tuple[int, int], target: tuple[int, int]) -> DirectionName | None:
        dx = target[0] - current[0]
        dy = target[1] - current[1]
        reverse = {
            (0, -1): "up",
            (0, 1): "down",
            (-1, 0): "left",
            (1, 0): "right",
        }
        return reverse.get((dx, dy))

    def _next_position_for_direction(
        self,
        head: tuple[int, int],
        direction: DirectionName,
    ) -> tuple[int, int]:
        dx, dy = _DIRECTION_DELTAS[direction]
        return (head[0] + dx, head[1] + dy)

    def _is_safe_cell(self, state: GameStateSnapshot, cell: tuple[int, int]) -> bool:
        x, y = cell
        if not (0 <= x < state.grid_width and 0 <= y < state.grid_height):
            return False

        if cell in state.obstacles:
            return False

        will_grow = cell == state.apple_position
        if cell in state.snake:
            return not will_grow and cell == state.snake[-1]

        return True

    def _choose_safest_direction(self, state: GameStateSnapshot) -> DirectionName | None:
        head = state.snake[0]
        best_direction: DirectionName | None = None
        best_space = -1
        best_apple_distance = float("inf")

        for direction in _DIRECTION_ORDER:
            candidate = self._next_position_for_direction(head, direction)
            if not self._is_safe_cell(state, candidate):
                continue

            grows = candidate == state.apple_position
            if grows:
                simulated_snake = [candidate] + list(state.snake)
            else:
                simulated_snake = [candidate] + list(state.snake[:-1])

            blocked_cells = set(state.obstacles) | set(simulated_snake[1:])
            if not grows and len(simulated_snake) > 1:
                blocked_cells.discard(simulated_snake[-1])

            open_space = reachable_cell_count(
                start=candidate,
                blocked_cells=blocked_cells,
                grid_width=state.grid_width,
                grid_height=state.grid_height,
            )
            apple_distance = abs(candidate[0] - state.apple_position[0]) + abs(
                candidate[1] - state.apple_position[1]
            )

            if open_space > best_space or (
                open_space == best_space and apple_distance < best_apple_distance
            ):
                best_space = open_space
                best_apple_distance = apple_distance
                best_direction = direction

        return best_direction
