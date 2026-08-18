from battleship_ui import *

show_board(PLAYER)
cells = [(2, 4), (5, 4), (8, 4)]

for x, y in cells:
    draw_deck(PLAYER, x, y, DECK_IDLE)
