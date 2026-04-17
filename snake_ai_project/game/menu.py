from __future__ import annotations

import pygame

from game._font import make_font, render_text
from game.settings import DISABLED_CONTROL_MODES, MENU_OPTIONS, WINDOW_HEIGHT, WINDOW_WIDTH


BACKGROUND_TOP = (20, 28, 42)
BACKGROUND_BOTTOM = (8, 12, 20)
TITLE_COLOR = (240, 242, 248)
SUBTITLE_COLOR = (166, 176, 194)
OPTION_COLOR = (213, 221, 234)
SELECTED_OPTION_BG = (40, 107, 171)
DISABLED_OPTION_COLOR = (100, 110, 128)
HINT_COLOR = (128, 138, 154)


class ModeMenu:
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock) -> None:
        self.screen = screen
        self.clock = clock
        self.title_font = make_font(42)
        self.subtitle_font = make_font(20)
        self.option_font = make_font(28)
        self.hint_font = make_font(18)

        self._selectable_modes = [
            mode for mode, _ in MENU_OPTIONS if mode not in DISABLED_CONTROL_MODES
        ]
        self._selected_idx = 0

        self._bg_surface = self._render_gradient()

    def run(self) -> str | None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None

                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        return None
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self._move_selection(-1)
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        self._move_selection(1)
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        return self._selectable_modes[self._selected_idx]

            self._draw()
            self.clock.tick(60)

    def _move_selection(self, delta: int) -> None:
        selectable_count = len(self._selectable_modes)
        self._selected_idx = (self._selected_idx + delta) % selectable_count

    def _draw(self) -> None:
        self.screen.blit(self._bg_surface, (0, 0))

        title_surface = render_text(self.title_font, "Snake AI Project", TITLE_COLOR)
        subtitle_surface = render_text(self.subtitle_font, "Select a launch mode", SUBTITLE_COLOR)

        self.screen.blit(
            title_surface,
            (WINDOW_WIDTH // 2 - title_surface.get_width() // 2, 90),
        )
        self.screen.blit(
            subtitle_surface,
            (WINDOW_WIDTH // 2 - subtitle_surface.get_width() // 2, 148),
        )

        first_y = 240
        row_gap = 62
        selected_mode = self._selectable_modes[self._selected_idx]

        for row, (mode, label) in enumerate(MENU_OPTIONS):
            y = first_y + row * row_gap
            is_disabled = mode in DISABLED_CONTROL_MODES
            is_selected = mode == selected_mode and not is_disabled

            option_rect = pygame.Rect(180, y, WINDOW_WIDTH - 360, 44)
            if is_selected:
                pygame.draw.rect(self.screen, SELECTED_OPTION_BG, option_rect, border_radius=8)

            text_color = DISABLED_OPTION_COLOR if is_disabled else OPTION_COLOR
            option_text = render_text(self.option_font, label, text_color)
            self.screen.blit(
                option_text,
                (WINDOW_WIDTH // 2 - option_text.get_width() // 2, y + 7),
            )

        hint_surface = render_text(
            self.hint_font,
            "Arrow keys: move   Enter: confirm   Esc: quit",
            HINT_COLOR,
        )
        self.screen.blit(
            hint_surface,
            (WINDOW_WIDTH // 2 - hint_surface.get_width() // 2, WINDOW_HEIGHT - 72),
        )

        pygame.display.flip()

    def _render_gradient(self) -> pygame.Surface:
        surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        for y in range(WINDOW_HEIGHT):
            blend = y / max(1, WINDOW_HEIGHT - 1)
            r = int(BACKGROUND_TOP[0] * (1 - blend) + BACKGROUND_BOTTOM[0] * blend)
            g = int(BACKGROUND_TOP[1] * (1 - blend) + BACKGROUND_BOTTOM[1] * blend)
            b = int(BACKGROUND_TOP[2] * (1 - blend) + BACKGROUND_BOTTOM[2] * blend)
            pygame.draw.line(surface, (r, g, b), (0, y), (WINDOW_WIDTH, y))
        return surface