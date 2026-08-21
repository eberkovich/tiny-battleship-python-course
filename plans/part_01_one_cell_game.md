# Part 1 Curriculum Plan: One-Cell Battleship

Completed phase: Phase A — implemented Lessons 1–8

## Outcome

Part 1 ends with a complete game made only of one-cell ships: the child places
a valid fleet of 10 ships, the computer creates a hidden valid fleet of 10
ships, both sides take non-repeating turns, hits sink ships, counters update,
and the game announces a winner. The target program is
`reference/part_01_game.py`.

The reference deliberately uses straightforward procedural Python: one small
validation function and otherwise visible top-level game flow. Lesson projects
must grow toward this program without copying the final solution into
child-facing content.

## Pacing contract

The sequence below is a minimum of 19 short lessons, not a target to compress.
Child testing may split a difficult lesson further. Do not merge lessons merely
to preserve a smaller count.

Before a difficult concept enters `battleship.py`, teach its concrete purpose,
show one minimal example, and use preliminary isolated exercises. Variables,
cell addresses, lists, conditions, functions, and mutable shooting state need
especially slow treatment. In child-facing text, introduce `(x, y)` as one
**«адрес клетки»** before later naming its Python representation. Part 1 does
not use a two-dimensional array or expose zero-based grid indexing.

## Lesson sequence

### Phase A: «Собираем флот» — Python foundations and a fixed fleet

#### 1. Helper commands and boards

- **Learn:** calls, argument names and values, parentheses, commas, comments,
  line-by-line execution, and the `show_board` command.
- **Practice:** call a familiar command with different argument values and
  distinguish active code from comments.
- **Game milestone:** show both 10×10 boards.

#### 2. Coordinates and the first ship

- **Learn:** the board coordinate system and `draw_deck` with its ordered
  arguments and fixed API values.
- **Practice:** find cells, draw ships at stated addresses, and correct swapped
  coordinates.
- **Game milestone:** keep both boards visible and add the first ship.
- **Optional challenge:** mirror three prepared ships across the board by
  reasoning about coordinate pairs.

#### 3. Variables

- **Learn:** `print(value)` and the launcher output card, then assignment,
  names, numbers, reuse of a value, and `show_ship_count`.
- **Practice:** print a literal, then change and print one named value.
- **Game milestone:** store one ship's coordinates in variables, draw it, and
  show counter `1`.

#### 4. One cell address

- **Learn:** treat `(x, y)` as one meaningful value, then assign and unpack it.
- **Practice:** create and unpack several unrelated addresses.
- **Game milestone:** store ships as addresses and draw a second fixed ship.
  Do not introduce lists yet.

#### 5. A list of addresses

- **Learn:** why programs group related values, a list literal, `len`, and
  zero-based element access by index.
- **Practice:** construct and count a familiar list, select one value, then
  diagnose a wrong index while drawing from a list of addresses.
- **Game milestone:** store three fixed ship addresses, retrieve and draw them
  by index with repeated calls, and derive the counter with `len`.

#### 6. Changing a list

- **Learn:** an empty list and `append`.
- **Practice:** add a familiar value and observe `len`, retrieve and draw a
  newly added address, then diagnose commands that build the wrong order.
- **Game milestone:** build the fixed fleet step by step and add a fourth ship.

#### 7. `for` loop

- **Learn:** repetition, indentation, iteration, and address unpacking.
- **Practice:** repeat one visible action, then iterate over a short address
  list.
- **Game milestone:** extend the fixed fleet to 10 ships and replace repeated
  drawing calls with one loop.
- **Optional challenge:** diagnose several interacting coordinate, board, and
  counter errors in a prepared fleet program.

#### 8. Text and a button

- **Learn:** string values and `show_message(message, label)`.
- **Practice:** create and print a string, show a button, then diagnose swapped
  message and label arguments.
- **Game milestone:** show **«Флот готов!»** and wait for
  **«Начать бой»**.
- **Optional challenge:** combine a list of strings, one loop, and one button
  call into a four-step battle countdown.

### Phase B: «Расставляем корабли» — valid interactive fleet setup

#### 9. A simple decision

- **Learn:** comparisons, `True`/`False`, and `if`/`else`.
- **Practice:** choose between two visible results using one comparison.
- **Game milestone:** reject a candidate placed in the same cell as one
  existing ship.

#### 10. Neighbouring cells

- **Learn:** subtraction, `abs`, `<=`, and boolean `and`.
- **Practice:** check horizontal, vertical, and diagonal neighbours separately.
- **Game milestone:** reject a candidate that touches one existing ship,
  including diagonally.

#### 11. Placement function

- **Learn:** `def`, parameters, and `return`; reuse known `for` and `if`.
- **Practice:** write small functions with one result before the fleet
  validator.
- **Game milestone:** implement `can_place_ship(x, y, ships)` and validate a
  candidate against the whole fleet.

#### 12. Selecting a cell

- **Learn:** returned values and `wait_for_cell(board)`; reuse address
  unpacking.
- **Practice:** capture and display cells selected on each board.
- **Game milestone:** let the player select and place one valid ship.

#### 13. Complete player setup

- **Learn:** `while`, nested flow, and uppercase `FLEET_SIZE`; reuse `append`.
- **Practice:** repeat a small action until a visible target is reached.
- **Game milestone:** accept cells until 10 valid player ships exist, update
  the counter, and then start battle.

#### 14. Enemy fleet

- **Learn:** write an import, use `randint`, and introduce uppercase
  `BOARD_SIZE`.
- **Practice:** generate visible numbers and cells before using hidden state.
- **Game milestone:** create 10 valid hidden enemy ships and show the enemy
  counter.

### Phase C: «Ход игры» — shooting and the complete battle

#### 15. One player shot

- **Learn:** membership with `in`, list `remove`, `DECK_SUNK`, and
  `show_miss`.
- **Practice:** find and remove familiar values from small lists.
- **Game milestone:** resolve one selected enemy cell as a hit or miss and
  update its counter.

#### 16. Shot history

- **Learn:** a history list, `append`, membership, and retry with known `while`.
- **Practice:** detect repeated familiar values before repeated cell input.
- **Game milestone:** let the player keep shooting until the enemy fleet is
  empty, rejecting repeated cells.

#### 17. One random computer shot

- **Learn:** reuse randomness, membership, and removal for the other board.
- **Practice:** resolve one prepared random cell as a hit or miss.
- **Game milestone:** after the player's turn, let the computer choose one
  random cell, resolve the shot, and update the player board and counter. This
  first version does not yet filter repeated or useless cells.

#### 18. A careful computer shot

- **Learn:** use `not`, a shot-history list, a sunk-ship list, and a small
  validation function; reuse the known no-touch neighbour calculation.
- **Practice:** decide which prepared candidate cells the computer may shoot.
- **Game milestone:** implement
  `can_computer_shoot(x, y, computer_shots, sunk_player_ships)` so the computer
  rejects cells it has already fired at and all horizontal, vertical, and
  diagonal neighbours of sunk one-cell ships.
- **Progressive hints:**
  1. «Сначала проверь, нет ли адреса клетки среди прошлых выстрелов компьютера.»
  2. «Храни адреса потопленных кораблей игрока в отдельном списке.»
  3. «Вспомни проверку расстановки кораблей: она уже умеет находить занятую и
     соседние клетки.»
  4. «Функция может сначала отклонить повторный выстрел, затем клетку рядом с
     потопленным кораблём, а во всех остальных случаях разрешить выстрел.»

#### 19. Complete battle

- **Learn:** combine both turns with `while`, `and`, `>`, and the final `==`
  result.
- **Practice:** trace short prepared win and loss scenarios before coding.
- **Game milestone:** alternate turns until one fleet is empty and announce
  victory or defeat.

A project may reuse all earlier material, but must not require a construct
listed only in a later row. Each lesson must still satisfy the general lesson
shape and authoring checks in `context/lesson_content.md`.

## Required Part 1 UI API

Lesson 1 introduces only `show_board`. Lesson 2 introduces `draw_deck`, Lesson
3 introduces `show_ship_count`, Lesson 8 introduces `show_message`, and Lesson
15 introduces `show_miss`. The first four are implemented in Phase A.
Add `DECK_SUNK` and `wait_for_cell` only when their later introduction lessons
are implemented:

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
show_message(message, label)
```

`wait_for_cell` returns the selected `(x, y)` pair. `show_message` shows a
dialog with a message and blocks until its labeled button is pressed. These functions handle
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
- arithmetic subtraction, `abs`, comparisons, booleans, `and`, and `not`;
- `if`/`else`, `for`, `while`, nested control flow, `def`, parameters, and
  `return`;
- random integers;
- coordinates, no-touch placement including diagonals, fleet completion,
  hidden enemy ships, shot history, repeated-shot prevention, avoidance of sunk
  one-cell ships and all their neighbours, hit/miss/sunk rendering, counters,
  alternating turns, and win/loss.

Preliminary exercises additionally use the teaching-only `print` function,
introduced in Lesson 3 together with the launcher output card. It is tracked
even though it does not remain in the final reference game.

## Verification checkpoints

Use three checkpoints rather than treating every lesson as a full release:

1. **Phase A, implemented Lessons 1–8:** run all new reference cases, affected Lesson 1
   regressions, the full suite, and one dark/light inspection of each new
   launcher or game capability.
2. **Phase B, Lessons 9–14:** additionally run deterministic player-placement
   scenarios covering acceptance and rejection, then all earlier regressions
   and the full suite.
3. **Phase C, Lessons 15–19:** run complete victory and defeat scenarios,
   repeated- and invalid-shot cases, every lesson reference, the full suite,
   and final dark/light visual inspection.

Between checkpoints, run the current lesson's reference solutions and only the
focused tests affected by the change. Reuse parameterized reference and
structural curriculum tests; do not create exact-prose, exact-source, or visual
tests unless they protect a settled requirement that cannot be checked more
semantically.

## Phase A completion evidence

Phase A was completed on 2026-08-19 without activating Phase B.

- Lesson 2 introduces coordinates and `draw_deck`, then adds the first ship to
  the cumulative game. Lessons 3–8 introduce `print`, variables, cell addresses, lists and indexed
  element access, `append`, `for`, strings, `show_ship_count`, and
  `show_message` in prerequisite order. Every coding task has a passing
  reference through its own lesson checker.
- The cumulative project grows through fleets of 1, 2, 3, 4, and finally 10
  fixed non-touching one-cell ships, then waits at **«Начать бой»**.
- Real and fake `show_message` implementations have matching signatures;
  the real prompt returns on a click and the fake backend records a semantic
  event. Check and visual-play subprocesses pass for the Lesson 8 project.
- The course home shows the complete 19-lesson roadmap while exposing all eight
  implemented lessons. Lesson 3 console flow, Lesson 7 project, Lesson 8
  summary, and game button prompt were inspected. Shared layouts and assets
  remain readable in both dark and light launcher themes.
- Lessons 2–8 each contain at least three required exercises that rise from a small
  example through completion or debugging to the cumulative game milestone.
- Shell checks, compilation, Lesson 1 regressions, all Phase A references, and
  the complete suite pass: `165 passed`.

Before changing this plan, rerun the reference solution and repeat this audit.
Any new child-visible syntax, standard-library operation, API call, or game rule
must be assigned to a lesson before it appears in the cumulative project.
