# Part 1 Curriculum Plan: One-Cell Battleship

## Outcome

Part 1 ends with a complete game made only of one-cell ships: the child places
a valid fleet, the computer creates a hidden valid fleet, both sides take
non-repeating turns, hits sink ships, counters update, and the game announces a
winner. The target program is `reference/part_01_game.py`.

The reference deliberately uses straightforward procedural Python: one small
validation function and otherwise visible top-level game flow. Lesson projects
must grow toward this program without copying the final solution into
child-facing content.

## Pacing contract

The sequence below is a minimum of 17 short lessons, not a target to compress.
Child testing may split a difficult lesson further. Do not merge lessons merely
to preserve a smaller count.

Before a difficult concept enters `battleship.py`, teach its concrete purpose,
show one minimal example, and use preliminary isolated exercises. Variables,
cell addresses, lists, conditions, functions, and mutable shooting state need
especially slow treatment. In child-facing text, introduce `(x, y)` as one
**«адрес клетки»** before later naming its Python representation. Part 1 does
not use a two-dimensional array or expose zero-based grid indexing.

## Lesson sequence

### Phase A: Python foundations and a fixed fleet

#### 1. Helper commands and coordinates

- **Learn:** calls, arguments, parentheses, commas, fixed API values, and
  coordinates.
- **Practice:** complete the existing Lesson 1 exercises.
- **Game milestone:** show both 10×10 boards.

#### 2. Variables

- **Learn:** `print(value)` and the launcher output card, then assignment,
  names, numbers, reuse of a value, comments, and `show_ship_count`.
- **Practice:** print a literal, then change and print one named value.
- **Game milestone:** store one ship's coordinates in variables, draw it, and
  show counter `1`.

#### 3. One cell address

- **Learn:** treat `(x, y)` as one meaningful value, then assign and unpack it.
- **Practice:** create and unpack several unrelated addresses.
- **Game milestone:** store ships as addresses and draw a second fixed ship.
  Do not introduce lists yet.

#### 4. A list of addresses

- **Learn:** a list literal and `len`.
- **Practice:** build and count short lists of familiar values, then addresses.
- **Game milestone:** store three fixed ship addresses, draw them with repeated
  calls, and derive the counter with `len`.

#### 5. Changing a list

- **Learn:** an empty list and `append`.
- **Practice:** add familiar values, observe order and changing `len`, then add
  addresses.
- **Game milestone:** build the fixed fleet step by step and add a fourth ship.

#### 6. `for` loop

- **Learn:** repetition, indentation, iteration, and address unpacking.
- **Practice:** repeat one visible action, then iterate over a short address
  list.
- **Game milestone:** extend the fixed fleet to five ships and replace repeated
  drawing calls with one loop.

#### 7. Text and a button

- **Learn:** string values and `wait_for_button(message, label)`.
- **Practice:** change message and button text in small examples.
- **Game milestone:** show **«Флот готов!»** and wait for
  **«Начать бой»**.

### Phase B: Valid interactive fleet setup

#### 8. A simple decision

- **Learn:** comparisons, `True`/`False`, and `if`/`else`.
- **Practice:** choose between two visible results using one comparison.
- **Game milestone:** reject a candidate placed in the same cell as one
  existing ship.

#### 9. Neighbouring cells

- **Learn:** subtraction, `abs`, `<=`, and boolean `and`.
- **Practice:** check horizontal, vertical, and diagonal neighbours separately.
- **Game milestone:** reject a candidate that touches one existing ship,
  including diagonally.

#### 10. Placement function

- **Learn:** `def`, parameters, and `return`; reuse known `for` and `if`.
- **Practice:** write small functions with one result before the fleet
  validator.
- **Game milestone:** implement `can_place_ship(x, y, ships)` and validate a
  candidate against the whole fleet.

#### 11. Selecting a cell

- **Learn:** returned values and `wait_for_cell(board)`; reuse address
  unpacking.
- **Practice:** capture and display cells selected on each board.
- **Game milestone:** let the player select and place one valid ship.

#### 12. Complete player setup

- **Learn:** `while`, nested flow, and uppercase `FLEET_SIZE`; reuse `append`.
- **Practice:** repeat a small action until a visible target is reached.
- **Game milestone:** accept cells until five valid player ships exist, update
  the counter, and then start battle.

#### 13. Enemy fleet

- **Learn:** write an import, use `randint`, and introduce uppercase
  `BOARD_SIZE`.
- **Practice:** generate visible numbers and cells before using hidden state.
- **Game milestone:** create five valid hidden enemy ships and show the enemy
  counter.

### Phase C: Shooting and the complete battle

#### 14. One player shot

- **Learn:** membership with `in`, list `remove`, and `DECK_SUNK`; reuse
  `show_miss`.
- **Practice:** find and remove familiar values from small lists.
- **Game milestone:** resolve one selected enemy cell as a hit or miss and
  update its counter.

#### 15. Shot history

- **Learn:** a history list, `append`, membership, and retry with known `while`.
- **Practice:** detect repeated familiar values before repeated cell input.
- **Game milestone:** let the player keep shooting until the enemy fleet is
  empty, rejecting repeated cells.

#### 16. Computer shot

- **Learn:** reuse randomness, history, membership, and removal.
- **Practice:** rebuild the known player-shot algorithm with scripted random
  values.
- **Game milestone:** replace the player-only loop with one player turn followed
  by one non-repeating computer turn; update both boards and counters.

#### 17. Complete battle

- **Learn:** combine both turns with `while`, `and`, `>`, and the final `==`
  result.
- **Practice:** trace short prepared win and loss scenarios before coding.
- **Game milestone:** alternate turns until one fleet is empty and announce
  victory or defeat.

A project may reuse all earlier material, but must not require a construct
listed only in a later row. Each lesson must still satisfy the general lesson
shape and authoring checks in `context/lesson_content.md`.

## Required Part 1 UI API

Lesson 1 keeps its current public surface. Add each later capability to the
real and fake backends only when its introduction lesson is implemented:

```python
PLAYER
ENEMY

DECK_IDLE
DECK_SUNK

show_board(board)
draw_deck(board, x, y, state)
show_miss(board, x, y)
show_ship_count(board, count)
wait_for_cell(board)
wait_for_button(message, label)
```

`wait_for_cell` returns the selected `(x, y)` pair. `wait_for_button` shows a
message and blocks until its labeled button is pressed. These functions handle
pygame events only; all placement, shooting, turn, fleet, and victory decisions
remain in student code.

## Coverage audit from the reference program

The lesson sequence explicitly covers every child-visible element used by the
target program:

- imports and comments;
- calls, arguments, returned values, and fixed API values;
- variables, constants, numbers, strings, assignment, and indentation;
- lists, coordinate pairs, unpacking, `len`, `append`, `remove`, and
  membership with `in`;
- arithmetic subtraction, `abs`, comparisons, booleans, and `and`;
- `if`/`else`, `for`, `while`, nested control flow, `def`, parameters, and
  `return`;
- random integers;
- coordinates, no-touch placement including diagonals, fleet completion,
  hidden enemy ships, shot history, repeated-shot prevention, hit/miss/sunk
  rendering, counters, alternating turns, and win/loss.

Preliminary exercises additionally use the teaching-only `print` function,
introduced in Lesson 2 together with the launcher output card. It is tracked
even though it does not remain in the final reference game.

Before changing this plan, rerun the reference solution and repeat this audit.
Any new child-visible syntax, standard-library operation, API call, or game rule
must be assigned to a lesson before it appears in the cumulative project.
