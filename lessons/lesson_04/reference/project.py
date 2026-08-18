from battleship_ui import *

show_board(PLAYER)
show_board(ENEMY)

ship_1 = (1, 1)
ship_2 = (3, 1)
ship_3 = (5, 1)
ships = [ship_1, ship_2, ship_3]

x, y = ship_1
draw_deck(PLAYER, x, y, DECK_IDLE)
x, y = ship_2
draw_deck(PLAYER, x, y, DECK_IDLE)
x, y = ship_3
draw_deck(PLAYER, x, y, DECK_IDLE)

show_ship_count(PLAYER, len(ships))
