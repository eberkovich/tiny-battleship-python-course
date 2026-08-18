from battleship_ui import *

show_board(PLAYER)
show_board(ENEMY)

first_ship = (2, 2)
x, y = first_ship
draw_deck(PLAYER, x, y, DECK_IDLE)

second_ship = (5, 2)
x, y = second_ship
draw_deck(PLAYER, x, y, DECK_IDLE)

show_ship_count(PLAYER, 2)
