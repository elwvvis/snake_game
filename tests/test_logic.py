from snake_game.logic import Game, Snake

#перемещение головы на одну клетку
def test_snake_moves_head_by_one_cell() -> None:
    snake = Snake((3, 4))

    snake.move(1, 0)

    assert snake.head() == (4, 4)


#проверка на рост тела 
def test_snake_grows_after_eating() -> None:
    snake = Snake((3, 4))
    old_length = len(snake.body)

    snake.grow()
    snake.move(1, 0)

    assert len(snake.body) == old_length + 1


#проверка на самостолкновение
def test_self_collision_detects_repeated_cell() -> None:
    snake = Snake((3, 4))
    snake.body = [(3, 4), (3, 5), (4, 5), (4, 4), (3, 4)]

    assert snake.collides_self()


#проверка на конец игры при столкновении со стеной
def test_wall_collision_ends_game() -> None:
    game = Game(w=7, h=5)
    game.snake.body = [(6, 2), (5, 2), (4, 2)]
    game.snake.direction = "right"

    game.step()

    assert game.is_over


#размещение еды несколько раз и проверка, что она в свободном поле
def test_food_spawns_in_an_unoccupied_cell() -> None:
    game = Game(w=10, h=8)

    for _ in range(100):
        food = game.spawn_food()
        assert food not in game.snake.body
        assert food is not None
        x, y = food
        assert 0 <= x < game.width
        assert 0 <= y < game.height


#проверка на еду, рост змейки и рост очков
def test_eating_food_adds_score_length_and_level() -> None:
    game = Game(w=10, h=8)
    game.snake.body = [(4, 4), (3, 4), (2, 4)]
    game.snake.direction = "right"
    game.food = (5, 4)

    game.step()

    assert game.score == 10
    assert len(game.snake.body) == 4
    assert game.level == 1


#проверка на переход на след уровень и ускорение
def test_level_increase_makes_game_faster() -> None:
    game = Game(w=10, h=8)
    game.score = 40
    old_tick = game.tick
    game.snake.body = [(4, 4), (3, 4), (2, 4)]
    game.food = (5, 4)

    game.step()

    assert game.level == 2
    assert game.tick < old_tick


#проверка на паузу
def test_pause_prevents_game_steps() -> None:
    game = Game(w=10, h=8)
    old_body = game.snake.body.copy()
    game.toggle_pause()

    game.step()

    assert game.snake.body == old_body
