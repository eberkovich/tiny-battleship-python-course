from battleship_ui import *

show_board(PLAYER)
ships = [(1, 4), (4, 4)]
ships.append((7, 4))

x, y = ships[2]
draw_deck(PLAYER, x, y, DECK_IDLE)
