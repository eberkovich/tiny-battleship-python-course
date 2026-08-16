# Tiny Battleship: V1 Architecture

This document is the source of truth for settled product, curriculum, and
technical decisions. `AGENTS.md` defines how agents maintain the project; stage
plans define what is implemented now.

## Product and teaching constraints

The course is for an active child of about eight who already knows basic
turtle-, maze-, or block-style programming and is supported by an experienced
programmer parent. Lead with a concrete problem and introduce syntax as a tool
for solving it. Use short explanations, frequent interaction, visible game
progress, stars, debugging, and optional challenges without speed pressure.

Introduce at most one major new concept per lesson. A lesson normally contains
a motivating problem, short explanation, prediction, two or three isolated
exercises, a cumulative Battleship project upgrade, an optional
**«Задача со звёздочкой»**, and **«Что изменилось в твоей игре?»**. All
child-facing content and interaction is in Russian; code identifiers and
developer documentation are in English.

## Main parts

The project has three product-level parts:

1. **Game/UI library** — the small procedural API used by student code, with a
   real graphical implementation and a fake implementation for checks.
2. **Launcher** — lesson navigation, Play, Check, Open Code, progress, and stars.
3. **Lessons** — curriculum metadata, child-facing text, exercises, cumulative
   Battleship upgrades, behavioral checks, and star challenges.

The subprocess runner/verifier supports the launcher; it is not a separate
product area.

## Technology choices

- Use `pygame-ce` for both the real game UI and the V1 launcher.
- Use Thonny as the external V1 code editor. The installer provides it, and the
  launcher opens the exact file for the selected task in Thonny.
- Keep the launcher and the student's game in separate processes.
- Run checks in a separate subprocess using the fake UI.
- Do not build a general GUI framework on top of pygame. The launcher needs
  only buttons, text wrapping, scrolling, simple layout, and result rendering.
- Reconsider a desktop UI framework only if real requirements outgrow this
  small pygame launcher.

## V1 non-goals

V1 does not include accounts or authentication, cloud storage or progress
synchronization, multiplayer, production publishing/deployment infrastructure,
server-side execution of student Python, a custom or browser code editor, a
generic game engine or education platform, a plugin system, complex telemetry
or keystroke logging, or mobile/web versions. The local macOS installer and
independent filesystem workspace for each student remain in scope.

## Telemetry and privacy

Stage 1 has no telemetry or persistent event log. `progress.json` stores only
state required by the launcher. Fake-UI semantic traces exist temporarily for
verification and are not retained as telemetry. Never log keystrokes or student
source code. Add local activity logging only after child testing demonstrates a
concrete need, and revisit privacy explicitly before any cloud or web logging.

## Future web boundary

Do not implement a web version in V1. Keep curriculum, progress, and
verification results serializable, and keep game rules independent of the
launcher and rendering backend. If a web version is built later, prefer running
student Python in the browser rather than sending it to a server. A future
backend should be limited to content delivery and optional account/progress
synchronization; do not create a server-side untrusted-code execution service.

## Ownership boundary

Student code is ordinary procedural Python and owns:

- ships and their deck coordinates;
- shot history;
- placement validation;
- hit, miss, and sunk decisions;
- fleet-completion and win/loss rules;
- turn order and later computer strategy;
- the transition from fleet setup to gameplay.

The UI library owns only mechanics:

- windows, layout, drawing, fonts, and animation;
- mouse-to-cell conversion and event pumping;
- blocking input and button waits;
- visual state needed to redraw the window.

The public API must not expose callbacks or require OOP. Internal engine code
may use classes such as `BoardView`, but student code uses functions and simple
constants such as `PLAYER` and `ENEMY`.

## Student workspaces

The course installation is shared. Each child has an independent directory
selected when launching the course:

```text
./run.command --student-dir students/child_1
```

Each student directory contains only that child's mutable state:

```text
child_1/
├── battleship.py
├── exercises/
│   └── lesson_01/
│       ├── exercise_01.py
│       ├── exercise_02.py
│       ├── exercise_03.py
│       └── star.py
└── progress.json
```

The launcher may initialize a missing student directory from a shared template,
but it must never overwrite an existing student source file, including
`battleship.py` or an exercise.

Checkpoint creation and restoration are deferred beyond Stage 1. Add them only
when the cumulative program is large enough to justify the recovery workflow.

## Lesson tasks and external-editor workflow

Lessons contain two distinct kinds of coding work:

- **isolated exercises** use separate student-owned `.py` files to practise one
  idea without modifying the game;
- **project milestones** modify the cumulative `battleship.py`.

The optional star challenge is an isolated exercise unless a later lesson
explicitly requires a project extension. It never blocks lesson completion.

For each coding task, the launcher shows the current task and file, then offers
Russian actions equivalent to **Open Code**, **Run**, and **Check**. Open Code
opens that exact student file in Thonny. Run and Check always read the saved file
from disk and execute it in a fresh subprocess; the launcher reminds the child
to save in Thonny first. Run never changes progress. A successful Check records
the stable task ID in `progress.json`; a failed Check leaves progress unchanged
and returns concise Russian feedback.

Exercise, project, and star completion are recorded separately. Source code and
verification traces are never stored in progress. Completed tasks may be
reopened, but the launcher never restores or overwrites their files.

## macOS installation

Provide an idempotent `install.command` script that prepares the project on a
supported Intel or Apple Silicon Mac. It must:

1. Look for both `python3` and `python` and execute a version check rather than
   assuming either command's meaning.
2. Accept a compatible Python 3 interpreter from either command. The minimum
   supported version must match the project's pinned dependencies.
3. If `python` starts Python 2, leave it untouched and install Python 3 under
   the `python3` command.
4. If Python 3 is missing or too old, install a pinned, signed, official macOS
   Python 3 distribution after obtaining any required administrator approval.
5. Never replace, delete, modify, or globally alias `/usr/bin/python`,
   `/usr/bin/python3`, or another system-managed interpreter.
6. Create a project-local `.venv` with the selected Python 3 interpreter and
   use `.venv/bin/python` for every subsequent project command.
7. Install all pinned project dependencies into that virtual environment,
   including `pygame-ce` and Thonny, and verify that the launcher, UI, and editor
   can be started.
8. Be safe to run repeatedly without overwriting student workspaces or progress.
9. Fail with a nonzero exit status and an actionable Russian message when
   installation cannot be completed.
10. Finish by printing a Russian success message with exact commands for
    starting the launcher for a selected `--student-dir`.

The normal `run.command` wrapper must use the virtual-environment interpreter
directly, so later launches do not depend on whether the machine calls its
global Python 3 executable `python` or `python3`.

`install.command` and its tests must be updated in the same change whenever a
project dependency, dependency version, or supported Python version changes.

## Curriculum and lesson files

For V1, one `CURRICULUM.yaml` is sufficient. It defines lesson order and each
lesson's compact pedagogical contract: the new concept, motivating problem,
game milestone, prerequisites, required behavior, paths, and star challenge.

Detailed material stays in its natural format:

- `lessons/<lesson>/lesson.md` — child-facing content;
- `lessons/<lesson>/exercises/` — immutable starter templates copied into each
  student's workspace on first initialization;
- `lessons/<lesson>/acceptance.py` — executable behavioral checks;
- `battleship.py` in the selected student directory — the cumulative game.

Do not add per-lesson manifests until one shared curriculum file causes actual
friction.

## Boards and visibility

The game has two boards:

- **Player board** — open; intact player ships are visible.
- **Enemy board** — closed; untouched enemy ships are indistinguishable from
  untouched water.

Both boards are fixed at 10×10 cells for V1. Coordinates are one-based integer
pairs `(x, y)`: `(1, 1)` is the top-left cell, `x` increases to the right, `y`
increases downward, and valid values are `1` through `10`. Both axes must have
visible labels.

A fired cell remains revealed for the rest of the game.

| Cell content | Player board | Enemy board |
| --- | --- | --- |
| Empty, not fired | Open water | Closed cell |
| Empty, fired | Miss | Miss |
| Intact deck | Visible | Hidden |
| Damaged deck | Visible | Visible |
| Deck belonging to a sunk ship | Visible | Visible |

## Cell rendering

Every ship is represented and rendered as individual decks; one board cell is
one deck. A deck has three visual states:

- `DECK_IDLE` — intact; hidden when it belongs to the enemy;
- `DECK_DAMAGED` — hit and visible;
- `DECK_SUNK` — part of a sunk ship and visible.

Water is separate from deck state and has two visual states:

- `WATER_IDLE` — open water on the player board and a closed cell on the enemy
  board;
- `WATER_FIRED` — a visible miss on either board.

Both fixed 10×10 boards and their cell state exist from the beginning, but both
boards are hidden initially. `show_board(board)` makes one board visible.
Calling it repeatedly is harmless and does not reset the board.

Student code may draw water or decks before or after showing a board. Drawing
on a hidden board updates its state; the result becomes visible when the board
is shown. Forgetting to show a required board is a behavioral verification
failure, not a runtime error. Invalid board constants, coordinates, and cell
states still fail clearly.

Do not expose `hide_board()` in V1 because no current lesson or game phase needs
it. Add it only when a concrete student task requires hiding an entire board.

Student code stores ships as plain coordinate collections:

```python
ship = [(1, 2), (2, 2), (3, 2)]
```

The public UI should expose deck-level drawing rather than a whole-ship drawing
operation, so loops over ship decks remain visible in student code.

## Fleet setup and gameplay

The final game has two main phases:

1. **Fleet setup** — place and validate the player's ships and create the
   enemy fleet.
2. **Gameplay** — alternate player and computer shots until one fleet is sunk.

During interactive player setup, each accepted cell click either extends one
existing ship or creates a new one-deck ship. Student code must reject a deck
when it would cause an invalid fleet. Ships must be horizontal or vertical,
contiguous, inside the board, non-overlapping, and must not touch another ship,
including diagonally. A click that would connect multiple ships is invalid.

Fleet requirements are plain student-owned data, for example:

```python
fleet_sizes = [3, 2, 1]
```

When student code determines that the fleet is valid and complete, it makes a
blocking procedural call:

```python
wait_for_button("Флот готов!", "Начать бой")
```

The pygame implementation handles the button and its events internally. The
function returns after the click, and student code continues into gameplay. No
listener, callback, scene framework, or framework-controlled phase transition
is exposed to the student.

## Current public API direction

Exact names may be refined during the Lesson 1 vertical slice. The intended
shape is small and procedural:

```python
PLAYER
ENEMY

WATER_IDLE
WATER_FIRED
DECK_IDLE
DECK_DAMAGED
DECK_SUNK

show_board(board)
wait_for_cell(board)
wait_for_button(message, button_text)
draw_water(board, x, y, state=WATER_IDLE)
draw_deck(board, x, y, state=DECK_IDLE)
show_invalid_cell(board, x, y)
show_message(text)
```

Use `draw_water(..., WATER_IDLE)` to restore an idle water cell and
`draw_water(..., WATER_FIRED)` to show a miss.

The real and fake implementations must provide the same student-facing API.
`wait_for_button` is not required by Lesson 1; add it when a later lesson first
needs an explicit student-controlled phase transition. During Lesson 1 Play,
the runner keeps the finished pygame window open internally until it is closed.
