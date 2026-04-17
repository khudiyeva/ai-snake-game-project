import argparse

import pygame

from agents import create_agent
from game.menu import ModeMenu
from game.snake_game import SnakeGame
from game.settings import ACTIVE_CONTROL_MODES, CONTROL_MODES, WINDOW_HEIGHT, WINDOW_WIDTH


def parse_args():
    parser = argparse.ArgumentParser(description="Snake AI Project")
    parser.add_argument(
        "--mode",
        choices=CONTROL_MODES,
        default=None,
        help="Control mode for the snake. If omitted, launch the in-game menu.",
    )
    parser.add_argument(
        "--map",
        dest="map_path",
        default=None,
        help="Path to a map TXT file (30 rows x 40 cols, space-separated 0/1).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Snake AI Project")
    clock = pygame.time.Clock()

    # If --mode specified but disabled, exit immediately
    if args.mode is not None and args.mode not in ACTIVE_CONTROL_MODES:
        pygame.quit()
        print(
            f"[startup] Mode '{args.mode}' is reserved for future implementation.",
            flush=True,
        )
        print(f"[startup] Available modes: {', '.join(ACTIVE_CONTROL_MODES)}", flush=True)
        return 2

    selected_mode = args.mode

    while True:
        if selected_mode is None:
            menu = ModeMenu(screen=screen, clock=clock)
            selected_mode = menu.run()
            if selected_mode is None:
                break

        agent = create_agent(selected_mode)
        game = SnakeGame(
            control_mode=selected_mode,
            agent=agent,
            screen=screen,
            clock=clock,
            map_path=args.map_path,
        )
        result = game.run()

        if result == "quit":
            break
        # result == "menu": loop and re-show menu
        selected_mode = None

    pygame.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
