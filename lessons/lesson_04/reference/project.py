from battleship_ui import *

show_board(PLAYER)
show_board(ENEMY)

ships = [(1, 1), (3, 1), (5, 1)]

x, y = ships[0]
draw_deck(PLAYER, x, y, DECK_IDLE)
x, y = ships[1]
draw_deck(PLAYER, x, y, DECK_IDLE)
x, y = ships[2]
draw_deck(PLAYER, x, y, DECK_IDLE)

show_ship_count(PLAYER, len(ships))
