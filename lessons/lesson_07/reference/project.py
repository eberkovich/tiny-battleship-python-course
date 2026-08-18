from battleship_ui import *

show_board(PLAYER)
show_board(ENEMY)

ships = [
    (1, 1), (3, 1), (5, 1), (7, 1), (9, 1),
    (1, 3), (3, 3), (5, 3), (7, 3), (9, 3),
]

for x, y in ships:
    draw_deck(PLAYER, x, y, DECK_IDLE)

show_ship_count(PLAYER, len(ships))
wait_for_button("Флот готов!", "Начать бой")
