from __future__ import annotations

import os
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, cast

from snake_game.logic import Direction, Game


@contextmanager
def raw_mode() -> Iterator[None]:
    if os.name == "nt":
        yield
        return

    import termios
    import tty

    terminal_settings = cast(Any, termios)
    terminal_input = cast(Any, tty)
    file_descriptor = sys.stdin.fileno()
    previous_settings = terminal_settings.tcgetattr(file_descriptor)
    try:
        terminal_input.setcbreak(file_descriptor)
        yield
    finally:
        terminal_settings.tcsetattr(file_descriptor, terminal_settings.TCSADRAIN, previous_settings)


def _read_key_unix(timeout: float) -> str | None:
    import select

    file_descriptor = sys.stdin.fileno()
    ready, _, _ = select.select([file_descriptor], [], [], timeout)
    if not ready:
        return None
    first = os.read(file_descriptor, 1).decode("utf-8", errors="ignore")
    if first != "\x1b":
        return first
    sequence = first
    for _ in range(2):
        more, _, _ = select.select([file_descriptor], [], [], 0.01)
        if not more:
            break
        sequence += os.read(file_descriptor, 1).decode("utf-8", errors="ignore")
    arrows: dict[str, Direction] = {
        "\x1b[A": "up",
        "\x1b[B": "down",
        "\x1b[C": "right",
        "\x1b[D": "left",
    }
    return arrows.get(sequence)


def _read_key_windows(timeout: float) -> str | None:
    import msvcrt

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if msvcrt.kbhit():
            key = msvcrt.getwch()
            if key in ("\x00", "\xe0"):
                arrow = msvcrt.getwch()
                return {"H": "up", "P": "down", "M": "right", "K": "left"}.get(arrow)
            return key
        time.sleep(0.005)
    return None


def read_key(timeout: float = 0.02) -> str | None:
    if os.name == "nt":
        return _read_key_windows(timeout)
    return _read_key_unix(timeout)


def render(game: Game) -> str:
    snake_cells = set(game.snake.body)
    lines = ["+" + "-" * game.width + "+"]
    for y in range(game.height):
        row = []
        for x in range(game.width):
            position = (x, y)
            if position == game.snake.head():
                row.append("@")
            elif position in snake_cells:
                row.append("o")
            elif position == game.food:
                row.append("*")
            else:
                row.append(" ")
        lines.append("|" + "".join(row) + "|")
    lines.append("+" + "-" * game.width + "+")
    status = f"Score: {game.score}   Level: {game.level}   Speed: {1 / game.tick:.1f} cells/s"
    lines.append(status)
    lines.append("Arrows: move   Space: pause   Q: quit")
    if game.paused:
        lines.append("PAUSED")
    frame = "\r\n".join(f"{line}\033[K" for line in lines)
    return "\033[H" + frame


def _direction_from_key(key: str | None) -> Direction | None:
    if key in {"up", "down", "left", "right"}:
        return key  # type: ignore[return-value]
    return None


def play(game: Game) -> bool:
    print("\033[2J\033[?25l", end="", flush=True)
    last_step = time.monotonic()
    should_show_game_over = True
    try:
        with raw_mode():
            while not game.is_over:
                key = read_key()
                if key in {"q", "Q"}:
                    should_show_game_over = False
                    return False
                if key == " ":
                    game.toggle_pause()
                direction = _direction_from_key(key)
                if direction is not None:
                    game.change_direction(direction)

                now = time.monotonic()
                if not game.paused and now - last_step >= game.tick:
                    game.step()
                    last_step = now
                print(render(game), end="", flush=True)
    finally:
        print("\033[?25h\033[H\033[2J", end="", flush=True)

    if should_show_game_over:
        result = "You filled the board!" if game.won else "Game over!"
        print(f"{result} Final score: {game.score}.")
        return True
    return False
