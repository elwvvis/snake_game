from __future__ import annotations

import argparse
from collections.abc import Sequence

from snake_game.logic import Game
from snake_game.terminal import play


# параметры
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Play Snake in your terminal")
    parser.add_argument("--width", type=int, default=20, help="board width (minimum 7)")
    parser.add_argument("--height", type=int, default=15, help="board height (minimum 5)")
    parser.add_argument("--speed", type=float, default=8.0, help="initial moves per second")
    return parser


# main получает параметры, запускает игру, повторяет при нажатии y
def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        game = Game(args.width, args.height, args.speed)
    except ValueError as error:
        build_parser().error(str(error))

    while True:
        finished = play(game)
        if not finished:
            return 0
        answer = input("Play again? [y/N]: ").strip().lower()
        if answer not in {"y", "yes"}:
            return 0
        game = Game(args.width, args.height, args.speed)


if __name__ == "__main__":
    raise SystemExit(main())
