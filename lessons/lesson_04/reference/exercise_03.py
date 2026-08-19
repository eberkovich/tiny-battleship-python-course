from battleship_ui import *

show_board(PLAYER)
ships = [(2, 4), (5, 4), (8, 4)]

first_ship = ships[0]
last_ship = ships[2]

x, y = first_ship
draw_deck(PLAYER, x, y, DECK_IDLE)
x, y = last_ship
draw_deck(PLAYER, x, y, DECK_IDLE)
