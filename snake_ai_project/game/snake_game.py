import random
import sys
from dataclasses import dataclass
from enum import Enum

import pygame


WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CELL_SIZE = 20

GRID_WIDTH = WINDOW_WIDTH // CELL_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // CELL_SIZE

RENDER_FPS = 60
START_SPEED = 5
MAX_SPEED = 16
NUM_OBSTACLES = 25

BACKGROUND_COLOR = (18, 18, 18)
GRID_COLOR = (35, 35, 35)
SNAKE_HEAD_COLOR = (0, 200, 0)
SNAKE_BODY_COLOR = (0, 150, 0)
OBSTACLE_COLOR = (120, 120, 120)
TEXT_COLOR = (240, 240, 240)

APPLE_SMALL_COLOR = (255, 220, 0)
APPLE_MEDIUM_COLOR = (255, 140, 0)
APPLE_LARGE_COLOR = (220, 30, 30)


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


@dataclass(frozen=True)
class AppleType:
    name: str
    points: int
    color: tuple[int, int, int]
    radius_ratio: float


APPLE_TYPES = [
    AppleType("small", 1, APPLE_SMALL_COLOR, 0.25),
    AppleType("medium", 3, APPLE_MEDIUM_COLOR, 0.35),
    AppleType("large", 5, APPLE_LARGE_COLOR, 0.48),
]


class SnakeGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake AI Project")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 24)

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
        self.speed = START_SPEED
        self.game_over = False

        self.move_timer = 0.0
        self.move_delay = 1.0 / self.speed

        self.obstacles = self._generate_obstacles(NUM_OBSTACLES)
        self.apple_position, self.apple_type = self._spawn_apple()

    def run(self):
        while True:
            dt = self.clock.tick(RENDER_FPS) / 1000.0

            self._handle_events()

            if not self.game_over:
                self.move_timer += dt

                while self.move_timer >= self.move_delay:
                    self._update()
                    self.move_timer -= self.move_delay

                    if self.game_over:
                        break

            self._draw()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self._change_direction(Direction.UP)
                elif event.key == pygame.K_DOWN:
                    self._change_direction(Direction.DOWN)
                elif event.key == pygame.K_LEFT:
                    self._change_direction(Direction.LEFT)
                elif event.key == pygame.K_RIGHT:
                    self._change_direction(Direction.RIGHT)
                elif event.key == pygame.K_r and self.game_over:
                    self.reset()

    def _change_direction(self, new_direction):
        opposite = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }

        if new_direction != opposite[self.direction]:
            self.next_direction = new_direction

    def _update(self):
        self.direction = self.next_direction
        dx, dy = self.direction.value

        head_x, head_y = self.snake[0]
        new_head = (head_x + dx, head_y + dy)

        if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
            self.game_over = True
            return

        if new_head in self.snake:
            self.game_over = True
            return

        if new_head in self.obstacles:
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        if new_head == self.apple_position:
            self.score += self.apple_type.points
            self._increase_speed(self.apple_type)
            self.apple_position, self.apple_type = self._spawn_apple()
        else:
            self.snake.pop()

    def _increase_speed(self, apple_type):
        speed_boost_map = {
            "small": 1,
            "medium": 2,
            "large": 3,
        }

        self.speed += speed_boost_map[apple_type.name]

        if self.speed > MAX_SPEED:
            self.speed = MAX_SPEED

        self.move_delay = 1.0 / self.speed

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

    def _spawn_apple(self):
        apple_type = random.choices(
            population=APPLE_TYPES,
            weights=[0.5, 0.3, 0.2],
            k=1
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
        self._draw_snake()
        self._draw_ui()

        if self.game_over:
            self._draw_game_over()

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

    def _draw_obstacles(self):
        for x, y in self.obstacles:
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.screen, OBSTACLE_COLOR, rect)

    def _draw_apple(self):
        x, y = self.apple_position
        center = (
            x * CELL_SIZE + CELL_SIZE // 2,
            y * CELL_SIZE + CELL_SIZE // 2
        )
        radius = int(CELL_SIZE * self.apple_type.radius_ratio)
        pygame.draw.circle(self.screen, self.apple_type.color, center, radius)

    def _draw_ui(self):
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        apple_text = self.font.render(
            f"Apple: {self.apple_type.name} (+{self.apple_type.points})",
            True,
            TEXT_COLOR
        )
        speed_text = self.font.render(f"Speed: {self.speed}", True, TEXT_COLOR)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(apple_text, (10, 40))
        self.screen.blit(speed_text, (10, 70))

    def _draw_game_over(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        text1 = self.font.render("Game Over", True, (255, 255, 255))
        text2 = self.font.render("Press R to restart", True, (255, 255, 255))

        self.screen.blit(
            text1,
            (WINDOW_WIDTH // 2 - text1.get_width() // 2, WINDOW_HEIGHT // 2 - 30)
        )
        self.screen.blit(
            text2,
            (WINDOW_WIDTH // 2 - text2.get_width() // 2, WINDOW_HEIGHT // 2 + 10)
        )