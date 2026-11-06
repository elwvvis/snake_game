from __future__ import annotations

import random
from typing import Literal

#Координаты и направления
Position = tuple[int, int]
Direction = Literal["up", "down", "left", "right"]

_DIRECTION_VECTORS: dict[Direction, Position] = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}
_VECTOR_DIRECTIONS: dict[Position, Direction] = {
    vector: direction for direction, vector in _DIRECTION_VECTORS.items()
}


class Snake:

    def __init__(self, start_pos: Position, direction: Direction = "right") -> None:
         # Проверяем, что змейке задали одно из разрешённых направлений
        if direction not in _DIRECTION_VECTORS:
            raise ValueError("Direction must be up, down, left, or right.")
        self.direction = direction
        dx, dy = _DIRECTION_VECTORS[direction]
        x, y = start_pos
        self.body: list[Position] = [(x - dx * offset, y - dy * offset) for offset in range(3)]
        self._growth_pending = 0

    def head(self) -> Position:
        return self.body[0] #Голова всегда в начале

    def move(self, dx: int, dy: int) -> None:
        if abs(dx) + abs(dy) != 1:
            raise ValueError("A move must be exactly one cell in one direction.")
        self.direction = _VECTOR_DIRECTIONS[(dx, dy)]
        x, y = self.head()
        self.body.insert(0, (x + dx, y + dy))
        if self._growth_pending:
            self._growth_pending -= 1
        else:
            self.body.pop()

    def grow(self) -> None:
        self._growth_pending += 1 #Иначе при след. ходе хвост удалится

    def collides_self(self) -> bool:
        return len(self.body) != len(set(self.body))


class Game:

    def __init__(self, w: int = 20, h: int = 15, speed: float = 8.0) -> None:
        if w < 7 or h < 5:
            raise ValueError("Board must be at least 7 cells wide and 5 cells high.")
        if speed <= 0:
            raise ValueError("Speed must be greater than zero.")
        self.width = w
        self.height = h
        self.base_speed = speed
        center = (w // 2, h // 2)
        self.snake = Snake(center)
        self.food: Position | None = None
        self.score = 0
        self.paused = False
        self._is_over = False
        self.won = False
        self.spawn_food()

    @property
    def is_over(self) -> bool:
        return self._is_over

    @property
    def level(self) -> int: 
        return self.score // 50 + 1 #каждые 50 очков новый уровень

    @property
    def tick(self) -> float:
        return max(0.05, 1.0 / self.base_speed - (self.level - 1) * 0.02) #ускоряет игру

    def spawn_food(self) -> Position | None:
        occupied = set(self.snake.body)
        free_cells = [
            (x, y) for y in range(self.height) for x in range(self.width) if (x, y) not in occupied
        ]
        if not free_cells: #ищем свободную клетку для еды
            self.food = None
            self._is_over = True
            self.won = True
            return None
        self.food = random.choice(free_cells)
        return self.food

    #проверка на столкновения и обработка еды
    def step(self, direction: Direction | None = None) -> None:
        if self._is_over or self.paused:
            return
        if direction is not None:
            self.change_direction(direction)

        dx, dy = _DIRECTION_VECTORS[self.snake.direction]
        head_x, head_y = self.snake.head()
        next_head = (head_x + dx, head_y + dy)
        if next_head == self.food:
            self.snake.grow()

        self.snake.move(dx, dy)
        new_x, new_y = self.snake.head()
        if not (0 <= new_x < self.width and 0 <= new_y < self.height):
            self._is_over = True
            return
        if self.snake.collides_self():
            self._is_over = True
            return
        if next_head == self.food:
            self.score += 10
            self.spawn_food()

    #пауза
    def toggle_pause(self) -> None:
        if not self._is_over:
            self.paused = not self.paused
    
    #запрет разворота на 180
    def change_direction(self, direction: Direction) -> None:
        if direction not in _DIRECTION_VECTORS:
            raise ValueError("Direction must be up, down, left, or right.")
        current_dx, current_dy = _DIRECTION_VECTORS[self.snake.direction]
        next_dx, next_dy = _DIRECTION_VECTORS[direction]
        if (current_dx + next_dx, current_dy + next_dy) != (0, 0):
            self.snake.direction = direction
