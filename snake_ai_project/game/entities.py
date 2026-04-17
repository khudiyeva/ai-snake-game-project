from __future__ import annotations

from enum import Enum


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


_DIRECTION_NAME_TO_ENUM = {
    "up": Direction.UP,
    "down": Direction.DOWN,
    "left": Direction.LEFT,
    "right": Direction.RIGHT,
}

_DIRECTION_ENUM_TO_NAME = {value: key for key, value in _DIRECTION_NAME_TO_ENUM.items()}


def direction_from_name(direction_name: str) -> Direction:
    return _DIRECTION_NAME_TO_ENUM[direction_name]


def direction_to_name(direction: Direction) -> str:
    return _DIRECTION_ENUM_TO_NAME[direction]
