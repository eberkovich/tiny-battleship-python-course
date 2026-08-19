from battleship_ui import *

show_board(PLAYER)
ships = [(2, 4), (5, 4), (8, 4)]

# Упражнение 3. Найди последний корабль
#
# Программа должна нарисовать первый и последний корабли из готового списка,
# но для последнего указан несуществующий индекс. Исправь один индекс. На поле
# должны появиться корабли в клетках (2, 4) и (8, 4).
first_ship = ships[0]
last_ship = ships[3]

x, y = first_ship
draw_deck(PLAYER, x, y, DECK_IDLE)
x, y = last_ship
draw_deck(PLAYER, x, y, DECK_IDLE)
