from random import randint

from battleship_ui import *


BOARD_SIZE = 10
FLEET_SIZE = 10


def can_place_ship(x, y, ships):
    for ship_x, ship_y in ships:
        if abs(x - ship_x) <= 1 and abs(y - ship_y) <= 1:
            return False
    return True


def can_computer_shoot(x, y, computer_shots, sunk_player_ships):
    if (x, y) in computer_shots:
        return False
    if not can_place_ship(x, y, sunk_player_ships):
        return False
    return True


# Показываем игровые поля.
show_board(PLAYER)
show_board(ENEMY)

# Игрок расставляет свои корабли.
player_ships = []
show_ship_count(PLAYER, 0)

while len(player_ships) < FLEET_SIZE:
    x, y = wait_for_cell(PLAYER)

    if can_place_ship(x, y, player_ships):
        player_ships.append((x, y))
        draw_deck(PLAYER, x, y, DECK_IDLE)
        show_ship_count(PLAYER, len(player_ships))
    else:
        show_message(
            "Корабли не должны соприкасаться.",
            "Попробовать ещё",
        )

show_message("Флот готов!", "Начать бой")

# Компьютер расставляет свои корабли.
enemy_ships = []

while len(enemy_ships) < FLEET_SIZE:
    x = randint(1, BOARD_SIZE)
    y = randint(1, BOARD_SIZE)

    if can_place_ship(x, y, enemy_ships):
        enemy_ships.append((x, y))
        draw_deck(ENEMY, x, y, DECK_IDLE)

show_ship_count(ENEMY, len(enemy_ships))

# Игрок и компьютер стреляют по очереди.
player_shots = []
computer_shots = []
sunk_player_ships = []

while len(player_ships) > 0 and len(enemy_ships) > 0:
    x, y = wait_for_cell(ENEMY)

    while (x, y) in player_shots:
        show_message("Ты уже стрелял в эту клетку.", "Выбрать другую")
        x, y = wait_for_cell(ENEMY)

    player_shots.append((x, y))

    if (x, y) in enemy_ships:
        enemy_ships.remove((x, y))
        draw_deck(ENEMY, x, y, DECK_SUNK)
    else:
        show_miss(ENEMY, x, y)

    show_ship_count(ENEMY, len(enemy_ships))

    if len(enemy_ships) > 0:
        computer_x = randint(1, BOARD_SIZE)
        computer_y = randint(1, BOARD_SIZE)

        while not can_computer_shoot(
            computer_x,
            computer_y,
            computer_shots,
            sunk_player_ships,
        ):
            computer_x = randint(1, BOARD_SIZE)
            computer_y = randint(1, BOARD_SIZE)

        computer_shots.append((computer_x, computer_y))

        if (computer_x, computer_y) in player_ships:
            player_ships.remove((computer_x, computer_y))
            sunk_player_ships.append((computer_x, computer_y))
            draw_deck(PLAYER, computer_x, computer_y, DECK_SUNK)
        else:
            show_miss(PLAYER, computer_x, computer_y)

        show_ship_count(PLAYER, len(player_ships))

if len(enemy_ships) == 0:
    show_message("Ты победил!", "Готово")
else:
    show_message("Компьютер победил. Попробуй ещё!", "Готово")
