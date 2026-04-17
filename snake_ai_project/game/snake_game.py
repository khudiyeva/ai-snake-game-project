import random
from dataclasses import dataclass

import pygame

from agents.base import AgentDecision, BaseSnakeAgent, GameStateSnapshot
from game._font import make_font, render_text
from game.entities import Direction, direction_from_name, direction_to_name
from game.settings import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    CELL_SIZE,
    RENDER_FPS,
    START_SPEED,
    MAX_SPEED,
    NUM_OBSTACLES,
    DEFAULT_CONTROL_MODE,
    SHOW_AI_PATH_DEBUG,
    MAX_APPLE_TIME,
    TIME_BONUS_MULTIPLIER,
    EFFICIENCY_BONUS_MULTIPLIER,
)


GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // CELL_SIZE

BACKGROUND_COLOR = (18, 18, 18)
GRID_COLOR = (35, 35, 35)
SNAKE_HEAD_COLOR = (0, 200, 0)
SNAKE_BODY_COLOR = (0, 150, 0)
OBSTACLE_COLOR = (120, 120, 120)
TEXT_COLOR = (240, 240, 240)
BLACK = (0, 0, 0)

APPLE_SMALL_COLOR = (255, 220, 0)   # yellow
APPLE_MEDIUM_COLOR = (255, 140, 0)  # orange
APPLE_LARGE_COLOR = (220, 30, 30)   # red
AI_PATH_COLOR = (70, 130, 255)
BONUS_COLOR = (255, 220, 50)


@dataclass(frozen=True)
class AppleType:
    name: str
    points: int
    speed_boost: float
    color: tuple[int, int, int]
    radius_ratio: float


APPLE_TYPES = [
    AppleType("yellow", 1, 0.5, APPLE_SMALL_COLOR, 0.25),
    AppleType("orange", 3, 1.5, APPLE_MEDIUM_COLOR, 0.35),
    AppleType("red", 5, 2.5, APPLE_LARGE_COLOR, 0.48),
]


class SnakeGame:
    def __init__(
        self,
        control_mode=DEFAULT_CONTROL_MODE,
        agent: BaseSnakeAgent | None = None,
        screen: pygame.Surface | None = None,
        clock: pygame.time.Clock | None = None,
        map_path: str | None = None,
    ):
        if screen is None:
            pygame.init()
            screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.display.set_caption("Snake AI Project")
        if clock is None:
            clock = pygame.time.Clock()

        self.screen = screen
        self.clock = clock
        self.font = make_font(24)
        self.pause_font = make_font(48)

        if agent is None:
            from agents import create_agent
            agent = create_agent(control_mode)

        self.agent = agent
        self.control_mode = self.agent.mode
        self.map_path = map_path
        self.ai_path: list[tuple[int, int]] = []

        self.reset()

    def reset(self):
        center_x = GRID_WIDTH // 2
        center_y = GRID_HEIGHT // 2

        self.snake = [
            (center_x, center_y),
            (center_x - 1, center_y),
            (center_x - 2, center_y),
        ]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT

        self.score = 0
        self.speed = float(START_SPEED)
        self.game_over = False
        self.paused = False
        self._run_result: str | None = None

        self.move_timer = 0.0
        self.move_delay = 1.0 / self.speed

        self.apple_timer = 0.0
        self.steps_since_apple = 0
        self.apple_optimal_steps = 0
        self.bonus_flash_timer = 0.0
        self.last_bonus = 0

        if self.map_path:
            self.obstacles = self._load_map_obstacles(self.map_path)
        else:
            self.obstacles = self._generate_obstacles(NUM_OBSTACLES)

        self.apple_position, self.apple_type = self._spawn_apple()
        self.apple_optimal_steps = self._compute_optimal_steps()
        self.ai_path = []
        self.agent.reset()

    def run(self) -> str:
        while self._run_result is None:
            dt = self.clock.tick(RENDER_FPS) / 1000.0

            self._handle_events()

            if not self.game_over and not self.paused:
                self.apple_timer += dt
                if self.bonus_flash_timer > 0:
                    self.bonus_flash_timer = max(0.0, self.bonus_flash_timer - dt)

                self.move_timer += dt

                while self.move_timer >= self.move_delay:
                    decision = self.agent.select_direction(self._build_state_snapshot())
                    self._apply_agent_decision(decision)
                    if self.game_over:
                        break

                    self.steps_since_apple += 1
                    self._update()
                    self.move_timer -= self.move_delay

                    if self.game_over:
                        break

            self._draw()

        return self._run_result

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._run_result = "quit"
                return

            self.agent.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.reset()
                elif event.key == pygame.K_p and not self.game_over:
                    self.paused = not self.paused
                    if self.paused:
                        self.move_timer = 0.0
                elif event.key == pygame.K_ESCAPE and self.paused:
                    self._run_result = "menu"

    def _change_direction(self, new_direction):
        opposite = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }

        if new_direction != opposite[self.direction]:
            self.next_direction = new_direction

    def _build_state_snapshot(self) -> GameStateSnapshot:
        return GameStateSnapshot(
            snake=tuple(self.snake),
            direction=direction_to_name(self.direction),
            next_direction=direction_to_name(self.next_direction),
            apple_position=self.apple_position,
            obstacles=frozenset(self.obstacles),
            grid_width=GRID_WIDTH,
            grid_height=GRID_HEIGHT,
            score=self.score,
            speed=self.speed,
            game_over=self.game_over,
            apple_timer=self.apple_timer,
            steps_since_apple=self.steps_since_apple,
        )

    def _apply_agent_decision(self, decision: AgentDecision) -> None:
        if decision.force_game_over:
            self.ai_path = []
            self.game_over = True
            return

        if decision.next_direction is not None:
            try:
                self._change_direction(direction_from_name(decision.next_direction))
            except KeyError:
                pass

        if decision.debug_path is not None:
            self.ai_path = list(decision.debug_path)
        elif self.control_mode != "astar":
            self.ai_path = []

    def _update(self):
        self.direction = self.next_direction
        dx, dy = self.direction.value

        head_x, head_y = self.snake[0]
        new_head = (head_x + dx, head_y + dy)
        will_grow = new_head == self.apple_position

        if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
            self.game_over = True
            return

        if new_head in self.obstacles:
            self.game_over = True
            return

        if new_head in self.snake:
            tail_cell = self.snake[-1]
            if not (not will_grow and new_head == tail_cell):
                self.game_over = True
                return

        self.snake.insert(0, new_head)

        if will_grow:
            base_points = self.apple_type.points

            time_ratio = max(0.0, 1.0 - self.apple_timer / MAX_APPLE_TIME)
            time_bonus = round(base_points * time_ratio * TIME_BONUS_MULTIPLIER)

            efficiency_bonus = 0
            if self.steps_since_apple > 0 and self.apple_optimal_steps > 0:
                efficiency = min(1.0, self.apple_optimal_steps / self.steps_since_apple)
                efficiency_bonus = round(base_points * efficiency * EFFICIENCY_BONUS_MULTIPLIER)

            total_bonus = time_bonus + efficiency_bonus
            self.score += base_points + total_bonus
            self.last_bonus = total_bonus
            self.bonus_flash_timer = 0.5

            self.apple_timer = 0.0
            self.steps_since_apple = 0

            self._increase_speed(self.apple_type)
            self.apple_position, self.apple_type = self._spawn_apple()
            self.apple_optimal_steps = self._compute_optimal_steps()
            return

        self.snake.pop()

    def _increase_speed(self, apple_type):
        self.speed += apple_type.speed_boost

        if self.speed > MAX_SPEED:
            self.speed = MAX_SPEED

        self.move_delay = 1.0 / self.speed

    def _compute_optimal_steps(self) -> int:
        hx, hy = self.snake[0]
        ax, ay = self.apple_position
        return abs(hx - ax) + abs(hy - ay)

    def _generate_obstacles(self, count):
        obstacles = set()
        forbidden = set(self.snake)

        while len(obstacles) < count:
            pos = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1),
            )
            if pos not in forbidden:
                obstacles.add(pos)

        return obstacles

    def _load_map_obstacles(self, path: str) -> frozenset[tuple[int, int]]:
        try:
            with open(path, encoding="utf-8") as f:
                raw_lines = f.read().splitlines()

            rows = [line for line in raw_lines if line.strip()]
            if len(rows) != GRID_HEIGHT:
                print(f"[map] Warning: expected {GRID_HEIGHT} rows, got {len(rows)}")

            obstacles: set[tuple[int, int]] = set()
            warned_cols = False
            for row_idx, line in enumerate(rows[:GRID_HEIGHT]):
                tokens = line.split()
                if len(tokens) != GRID_WIDTH and not warned_cols:
                    print(
                        f"[map] Warning: expected {GRID_WIDTH} columns, "
                        f"got {len(tokens)} at row {row_idx}"
                    )
                    warned_cols = True
                for col_idx, token in enumerate(tokens[:GRID_WIDTH]):
                    if token == "1":
                        obstacles.add((col_idx, row_idx))

            # Ensure snake starting cells are always free
            center_x = GRID_WIDTH // 2
            center_y = GRID_HEIGHT // 2
            snake_start = {
                (center_x, center_y),
                (center_x - 1, center_y),
                (center_x - 2, center_y),
            }
            obstacles -= snake_start

            return frozenset(obstacles)

        except (OSError, ValueError) as e:
            print(f"[map] Failed to load '{path}': {e}. Using random obstacles.")
            return self._generate_obstacles(NUM_OBSTACLES)

    def _spawn_apple(self):
        apple_type = random.choices(
            population=APPLE_TYPES,
            weights=[0.5, 0.3, 0.2],
            k=1,
        )[0]

        occupied = set(self.snake) | self.obstacles

        while True:
            pos = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1),
            )
            if pos not in occupied:
                return pos, apple_type

    def _draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        self._draw_grid()
        self._draw_obstacles()
        self._draw_apple()
        if self.control_mode == "astar" and SHOW_AI_PATH_DEBUG:
            self._draw_ai_path()
        self._draw_snake()
        self._draw_ui()

        if self.game_over:
            self._draw_game_over()

        if self.paused:
            self._draw_pause_overlay()

        pygame.display.flip()

    def _draw_grid(self):
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y))

    def _draw_snake(self):
        for i, (x, y) in enumerate(self.snake):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = SNAKE_HEAD_COLOR if i == 0 else SNAKE_BODY_COLOR
            pygame.draw.rect(self.screen, color, rect, border_radius=4)

            if i == 0:
                self._draw_face(x, y)

    def _draw_face(self, x, y):
        head_left = x * CELL_SIZE
        head_top = y * CELL_SIZE

        eye_radius = max(2, CELL_SIZE // 10)

        if self.direction == Direction.RIGHT:
            eyes = [(0.7, 0.3), (0.7, 0.7)]
            tongue_rect = pygame.Rect(head_left + CELL_SIZE - 2, head_top + CELL_SIZE // 2 - 2, 8, 4)
        elif self.direction == Direction.LEFT:
            eyes = [(0.3, 0.3), (0.3, 0.7)]
            tongue_rect = pygame.Rect(head_left - 6, head_top + CELL_SIZE // 2 - 2, 8, 4)
        elif self.direction == Direction.UP:
            eyes = [(0.3, 0.3), (0.7, 0.3)]
            tongue_rect = pygame.Rect(head_left + CELL_SIZE // 2 - 2, head_top - 6, 4, 8)
        else:
            eyes = [(0.3, 0.7), (0.7, 0.7)]
            tongue_rect = pygame.Rect(head_left + CELL_SIZE // 2 - 2, head_top + CELL_SIZE - 2, 4, 8)

        for ex, ey in eyes:
            pygame.draw.circle(
                self.screen,
                BLACK,
                (head_left + int(CELL_SIZE * ex), head_top + int(CELL_SIZE * ey)),
                eye_radius,
            )

        pygame.draw.rect(self.screen, (220, 60, 90), tongue_rect)

    def _draw_obstacles(self):
        for x, y in self.obstacles:
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, OBSTACLE_COLOR, rect)

    def _draw_apple(self):
        x, y = self.apple_position
        center = (
            x * CELL_SIZE + CELL_SIZE // 2,
            y * CELL_SIZE + CELL_SIZE // 2,
        )
        radius = int(CELL_SIZE * self.apple_type.radius_ratio)
        pygame.draw.circle(self.screen, self.apple_type.color, center, radius)

    def _draw_ai_path(self):
        if len(self.ai_path) < 2:
            return

        for x, y in self.ai_path[1:]:
            rect = pygame.Rect(
                x * CELL_SIZE + 3,
                y * CELL_SIZE + 3,
                CELL_SIZE - 6,
                CELL_SIZE - 6,
            )
            pygame.draw.rect(self.screen, AI_PATH_COLOR, rect, width=2, border_radius=4)

    def _draw_ui(self):
        score_text = render_text(self.font, f"Score: {self.score}", TEXT_COLOR)
        speed_text = render_text(self.font, f"Speed: {self.speed:.1f}", TEXT_COLOR)
        mode_text = render_text(self.font, f"Mode: {self.control_mode.upper()}", TEXT_COLOR)
        timer_text = render_text(self.font, f"Time: {self.apple_timer:.1f}s", TEXT_COLOR)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(speed_text, (10, 40))
        self.screen.blit(mode_text, (10, 70))
        self.screen.blit(timer_text, (10, 100))

        if self.bonus_flash_timer > 0 and self.last_bonus > 0:
            bonus_text = render_text(self.font, f"Bonus: +{self.last_bonus}", BONUS_COLOR)
            self.screen.blit(bonus_text, (10, 130))

    def _draw_game_over(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        text1 = render_text(self.font, "Game Over", (255, 255, 255))
        text2 = render_text(self.font, "Press R to restart", (255, 255, 255))

        self.screen.blit(
            text1,
            (WINDOW_WIDTH // 2 - text1.get_width() // 2, WINDOW_HEIGHT // 2 - 30),
        )
        self.screen.blit(
            text2,
            (WINDOW_WIDTH // 2 - text2.get_width() // 2, WINDOW_HEIGHT // 2 + 10),
        )

    def _draw_pause_overlay(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))

        cx = WINDOW_WIDTH // 2
        cy = WINDOW_HEIGHT // 2

        title = render_text(self.pause_font, "PAUSED", (255, 255, 255))
        resume = render_text(self.font, "P  —  Resume", (220, 220, 220))
        menu_hint = render_text(self.font, "ESC  —  Return to Main Menu", (220, 220, 220))

        self.screen.blit(title, (cx - title.get_width() // 2, cy - 70))
        self.screen.blit(resume, (cx - resume.get_width() // 2, cy))
        self.screen.blit(menu_hint, (cx - menu_hint.get_width() // 2, cy + 40))
