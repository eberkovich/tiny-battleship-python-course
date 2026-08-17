# Tiny Battleship: V1 Architecture

This document is the source of truth for settled product and technical
decisions. `context/lesson_content.md` defines lesson-authoring rules,
`AGENTS.md` defines how agents maintain the project, and stage plans define what
is implemented now.

## Product and teaching constraints

The course teaches procedural Python through one cumulative Battleship game;
it is not a generic education platform. Follow `context/lesson_content.md` for
the learner profile, teaching style, lesson structure, and content rules.

## Main parts

The project has three product-level parts:

1. **Game/UI library** — the small procedural API used by student code, with a
   real graphical implementation and a fake implementation for checks.
2. **Launcher** — course introduction, lesson navigation, editor launching,
   combined run/check flow, progress, and stars.
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

## Course and lesson navigation

The launcher has two navigation levels:

- **Course home** — a short Russian introduction explaining what the child will
  build, a lesson list, and **«Начать первый урок»** or **«Продолжить»**. This
  introduction is not Lesson 0.
- **Lesson screen** — **«Все уроки»**, the lesson title and steps, required-task
  progress, and navigation to the next unlocked lesson.

Completed lessons remain available. The current lesson is available; later
lessons are visible but locked until all required coding tasks in the current
lesson pass. The **«Итоги урока»** step is also visible but locked until every
required exercise and the cumulative project task in that lesson pass. Optional
star tasks never block the summary or progression. Opening a lesson shows its
saved current step, or its first step when no current step has been saved. The
current step is always unlocked; a locked step cannot be selected or saved as
current. When all required tasks pass, unlock the summary; the optional star
task remains available.

## Lesson presentation

Distinguish lesson-step types with a pygame-drawn icon, shape, and color; do not
rely on emoji or color alone. A sidebar card contains one icon and the step
title. The opened page contains one icon and the same title as its heading. Do
not add visible type captions such as **«Материал»**, **«Упражнение»**,
**«Пишем игру»**, or **«Со звёздочкой»** around those titles. Icons use bold,
simple, playful silhouettes with smoothly antialiased edges that remain clear
at sidebar size.

Use these internal step kinds and icons:

- `article` — open book;
- `question` — speech bubble with a question mark;
- `exercise` — pencil;
- `project` — ship;
- `star` — five-point star;
- `summary` — finish flag in soft violet, distinct from green completion.

Child-facing titles, wording, explanation order, and authoring requirements are
defined in `context/lesson_content.md`. A `summary` is informational, not
material or a coding task.

Render lesson text in a narrow column of lightly contrasted cards with generous
padding, line spacing, and visible space between major sections. A standalone
Markdown `---` separates major cards and is rendered as a compact group of
three yellow submarines. Do not use decorative dividers between ordinary
paragraphs.

The launcher offers dark and light schemes through one fixed top-right switch
on every screen. Both schemes share the same layout, rendering and event logic,
icon set, and raster assets; only named palette constants differ. In the
light scheme, the page background is visibly darker than the content cards so
their boundaries remain clear. Dark is the default, and the selected scheme is
saved independently in each student's `progress.json`.

Theme support is a UI invariant: every visual change must work through the
shared renderer and shared assets in both schemes. Do not add theme-specific
layout or behavior branches, and do not duplicate behavioral tests by palette;
test shared logic once and visually inspect readability and contrast in both
schemes.

## Coding-task workflow

Lessons contain two distinct kinds of coding work:

- **isolated exercises** use separate student-owned `.py` files to practise one
  idea without modifying the game;
- **project milestones** modify the cumulative `battleship.py`.

The optional star challenge is an isolated exercise unless a later lesson
explicitly requires a project extension. It never blocks lesson completion.

Each coding task has two child-facing actions:

- **«Открыть редактор»** opens the correct student file;
- **«Запустить»** reads the saved file, checks it with the fake UI, and then
  runs it with the real UI.

A behavioral failure still opens the real UI so the child can inspect the
result. Syntax errors, runtime failures before useful drawing, and timeouts are
reported without repeating the run. Only a successful behavioral check records
completion.

Show feedback inside the selected task near its actions. Do not reserve an
empty status panel or show placeholder messages such as **«Выбери шаг урока»**.
Use the generic reminder **«Сохрани код в редакторе: Cmd+S»**.

Show every coding task as one segment in the progress bar. Required exercises
use their exercise numbers, the cumulative project uses a ship symbol, and an
optional star exercise uses a star with its exercise number, for example `★4`.
Separate the star segment slightly without turning it into a second caption or
counter. Green ✓ means passed, grey number or symbol means not attempted, red !
means the latest attempt failed, and an outline marks the selected task. Do not
rely on color alone. The star symbol and extra spacing are the optional task's
only permanent distinction; it has an outline only while selected. Persist
successful completion; failed state is temporary. Articles, questions, and
summaries are excluded. The star never blocks lesson completion.

Exercise, project, and star completion are recorded separately. Source code and
verification traces are never stored in progress. Completed tasks may be
reopened, but the launcher never restores or overwrites their files.

## macOS installation

Provide an idempotent `install.command` script that prepares the project on a
supported Intel or Apple Silicon Mac. It must:

Stage 1 supports Python 3.11 through 3.14. If a supported Homebrew Python is
already installed without Tk, the script first installs the matching
`python-tk@<major.minor>` Homebrew formula and reuses that interpreter. This
route does not use `sudo`. When a complete Python installation is still
necessary, the script uses the pinned official Python 3.13.15 universal macOS
package and verifies its published SHA-256 checksum and Apple-trusted package
signature.

If installing Tk for an existing supported Homebrew Python fails, stop with an
actionable error. Do not silently fall back to the Python.org package in that
case because that package adds its framework to the shell path and may change
which interpreter the unqualified `python3` command selects.

Discover Homebrew's versioned executables under
`<brew-prefix>/opt/python@3.x/bin/python3.x` as well as the ordinary
`python3` and `python` commands. A Homebrew upgrade may leave the versioned
executable valid while removing an unversioned `python3` link; this must not
trigger the Python.org fallback.

1. Look for both `python3` and `python` and execute a version check rather than
   assuming either command's meaning.
2. Accept a compatible Python 3 interpreter from either command. The minimum
   supported version must match the project's pinned dependencies.
3. If `python` starts Python 2, leave it untouched and install Python 3 under
   the `python3` command.
4. If a supported Homebrew Python lacks Tk, install its matching Homebrew Tk
   formula. If that operation fails, stop without invoking the system-wide
   installer.
5. If Python 3 is missing, too old, or still lacks Tk, install a pinned, signed,
   official macOS Python 3 distribution after obtaining any required
   administrator approval, except after the Homebrew failure described above.
6. Never replace, delete, modify, or globally alias `/usr/bin/python`,
   `/usr/bin/python3`, or another system-managed interpreter.
7. Create a project-local `.venv` with the selected Python 3 interpreter and
   use `.venv/bin/python` for every subsequent project command.
8. Install all pinned project dependencies into that virtual environment,
   including `pygame-ce` and Thonny, and verify that the launcher, UI, and editor
   can be started.
9. Be safe to run repeatedly without overwriting student workspaces or progress.
10. Fail with a nonzero exit status and an actionable Russian message when
   installation cannot be completed.
11. Finish by printing a Russian success message with exact commands for
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
Its lesson content must follow `context/lesson_content.md`.

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

Use a playful nautical 2D style with wood, brass, ocean blue, cyan accents, and
strong outlines. Graphics must remain clear at 40×40. Deck tiles fill the cell
and repeat unchanged horizontally or vertically. Visual effects never affect
game logic or verification. In V1, an intact deck is a static wooden tile with
a short mast and a white-and-cyan sail. A miss uses the open-water blue with a
large dark cartoon cannonball and a bold white-and-cyan splash. Grid lines
remain visible between cells.

Water is separate from deck state. Untouched water is the initial cell state: it
looks open on the player board and closed on the enemy board. A missed shot is
visible on either board. The real and fake implementations may represent these
as internal states, but the student-facing API does not expose water-state
constants or require the child to draw ordinary water.

Both fixed 10×10 boards and their cell state exist from the beginning, but both
boards are hidden initially. `show_board(board)` makes one board visible.
Calling it repeatedly is harmless and does not reset the board.

Student code may mark a miss or draw decks before or after showing a board.
Updating a hidden board changes its state; the result becomes visible when the
board is shown. Forgetting to show a required board is a behavioral
verification failure, not a runtime error. Invalid board constants,
coordinates, and deck states still fail clearly.

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

Lesson 1 exposes only the API it teaches:

```python
PLAYER
ENEMY

DECK_IDLE

show_board(board)
draw_deck(board, x, y, state=DECK_IDLE)
show_miss(board, x, y)
```

`show_board` reveals a board, `draw_deck` places or updates a deck, and
`show_miss` displays an unsuccessful shot. Untouched water already exists and
does not need a public drawing operation.

The real and fake implementations must provide the same student-facing API.
Later lessons may add deck damage and sunk states, blocking cell or button
input, placement feedback, and messages only when those capabilities are first
taught and needed. Before adding or renaming anything, review the complete API
for consistent verbs, argument order, defaults, terminology, and abstraction
level. During Lesson 1 Run, the runner keeps the finished pygame window open
internally until it is closed.
