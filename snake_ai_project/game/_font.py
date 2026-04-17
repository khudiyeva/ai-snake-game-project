"""Thin font helper that works on Python 3.14 where pygame.font and
pygame.freetype both trigger a circular import in pygame.sysfont.

We import the C extension directly (pygame._freetype) and use the
built-in default font so no system-font lookup is needed."""

from __future__ import annotations

import pygame._freetype as _ft

_ft.init()


def make_font(size: int):
    """Return a freetype Font at *size* using pygame's built-in default."""
    return _ft.Font(None, size)


def render_text(font, text: str, color) -> pygame.Surface:
    """Render *text* and return just the Surface (drop the Rect)."""
    import pygame  # only needed for the type; already initialised by caller
    surface, _ = font.render(text, color)
    return surface