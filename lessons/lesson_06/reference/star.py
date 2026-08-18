from battleship_ui import *

show_board(ENEMY)
shots = [(2, 2), (5, 5), (8, 8)]

for x, y in shots:
    show_miss(ENEMY, x, y)
