from battleship_ui import *

show_board(PLAYER)
show_board(ENEMY)
ships = [(1, 2), (3, 2), (5, 2), (7, 2), (9, 2)]

for x, y in ships:
    draw_deck(PLAYER, x, y, DECK_IDLE)

show_ship_count(PLAYER, 5)
