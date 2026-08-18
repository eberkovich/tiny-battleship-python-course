from battleship_ui import *

show_board(PLAYER)
show_board(ENEMY)

ships = []

ship = (1, 1)
ships.append(ship)
x, y = ship
draw_deck(PLAYER, x, y, DECK_IDLE)

ship = (3, 1)
ships.append(ship)
x, y = ship
draw_deck(PLAYER, x, y, DECK_IDLE)

ship = (5, 1)
ships.append(ship)
x, y = ship
draw_deck(PLAYER, x, y, DECK_IDLE)

ship = (7, 1)
ships.append(ship)
x, y = ship
draw_deck(PLAYER, x, y, DECK_IDLE)

show_ship_count(PLAYER, len(ships))
