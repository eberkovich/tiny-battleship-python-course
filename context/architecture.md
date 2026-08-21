# Tiny Battleship: V1 Architecture

This document is the source of truth for settled product and technical
decisions. `context/lesson_content.md` defines lesson-authoring rules,
`AGENTS.md` defines how agents maintain the project, and stage plans define what
is implemented now.

## Product scope

### Product and teaching constraints

The course teaches procedural Python through one cumulative Battleship game;
it is not a generic education platform. Follow `context/lesson_content.md` for
the learner profile, teaching style, lesson structure, and content rules.

### Main parts

The project has three product-level parts:

1. **Game/UI library** — the small procedural API used by student code, with a
   real graphical implementation and a fake implementation for checks.
2. **Launcher** — course introduction, lesson navigation, editor launching,
   combined run/check flow, progress, and stars.
3. **Lessons** — curriculum metadata, child-facing text, exercises, cumulative
   Battleship upgrades, behavioral checks, and star challenges.

The subprocess runner/verifier supports the launcher; it is not a separate
product area.

## Engineering foundations

### Verification strategy

Test count is not a goal. Use shared structural validators and parameterized
reference runs across lessons. Every coding task still needs a passing reference
solution executed by the same behavioral checker as student code, while focused
failure cases cover only important rules and error paths. Run focused checks
while building a lesson; run the full regression suite and complete behavioral
scenarios at each Part 1 phase checkpoint and before handoff.

Do not duplicate tests for theme palettes or visual variants. Test shared logic
once and inspect both themes when a new visual capability appears. Avoid
pixel-perfect, exact-source, and broad exact-prose assertions. Exact lesson text
or ordering may be asserted only when it protects a prerequisite, required
term, or another settled teaching contract.

### Technology choices

- Use `pygame-ce` for both the real game UI and the V1 launcher.
- Use IDLE from the selected Python installation as the external V1 code
  editor. The installer verifies IDLE and Tk availability, and the launcher
  opens the exact file for the selected task directly in an editor window.
  Because IDLE is supplied as Python's standard-library `idlelib` module rather
  than a project package, a compatible interpreter without IDLE triggers the
  official Python installer; this installs Python with IDLE alongside existing
  interpreters without replacing the system Python.
- On first setup, configure IDLE with normal-weight Menlo at 18 pt so code is
  comfortable for a child to read. Store this in IDLE's normal user
  configuration and do not overwrite any existing IDLE font preference;
  settings changed later inside IDLE remain authoritative.
- Keep the launcher and the student's game in separate processes.
- Run checks in a separate subprocess using the fake UI.
- Do not build a general GUI framework on top of pygame. The launcher needs
  only buttons, text wrapping, scrolling, simple layout, and result rendering.
- Reconsider a desktop UI framework only if real requirements outgrow this
  small pygame launcher.

### V1 non-goals

V1 does not include accounts or authentication, cloud storage or progress
synchronization, multiplayer, production publishing/deployment infrastructure,
server-side execution of student Python, a custom or browser code editor, a
generic game engine or education platform, a plugin system, complex telemetry
or keystroke logging, or mobile/web versions. The local macOS installer and
independent filesystem workspace for each student remain in scope.

### Telemetry and privacy

Stage 1 has no telemetry or persistent event log. `progress.json` stores only
state required by the launcher. Fake-UI semantic traces exist temporarily for
verification and are not retained as telemetry. Never log keystrokes or student
source code. Add local activity logging only after child testing demonstrates a
concrete need, and revisit privacy explicitly before any cloud or web logging.

### Future web boundary

Do not implement a web version in V1. Keep curriculum, progress, and
verification results serializable, and keep game rules independent of the
launcher and rendering backend. If a web version is built later, prefer running
student Python in the browser rather than sending it to a server. A future
backend should be limited to content delivery and optional account/progress
synchronization; do not create a server-side untrusted-code execution service.

## Runtime ownership and local data

### Ownership boundary

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

### Student workspaces

The course installation is shared. Each child has an independent directory
selected when launching the course:

```text
./run.command --student-dir students/child_1
```

Each student directory contains only that child's mutable state:

```text
child_1/
├── .course_templates.json
├── battleship.py
├── exercises/
│   └── lesson_01/
│       ├── exercise_01.py
│       ├── exercise_02.py
│       ├── exercise_03.py
│       └── star.py
└── progress.json
```

The launcher initializes missing student files from shared templates and stores
their checksums in `.course_templates.json`. On a later course update, it may
refresh a source file only while that file is still byte-for-byte identical to
the last starter installed there. It must preserve every edited or untracked
existing source file, including `battleship.py` and exercises.

Checkpoint creation and restoration are deferred beyond Stage 1. Add them only
when the cumulative program is large enough to justify the recovery workflow.

## Launcher

### Course and lesson navigation

The launcher has two navigation levels:

- **Course home** — the final game goal, current progress, the three course
  stages, an expandable roadmap of all 18 Part 1 lessons, and
  **«Начать первый урок»** or **«Продолжить урок N»**. This introduction is not
  Lesson 0.
- **Lesson screen** — **«Все уроки»**, the lesson title and steps, required-task
  progress, and navigation to the next unlocked lesson.

#### Course home and roadmap

The course home first states the concrete result: a complete Battleship game
with 10 one-cell ships for the child and 10 for the computer. Its supporting
promise is: **«Ты сам напишешь игру: расставишь флот, добавишь выстрелы и
определение победителя.»** A short visual route shows the major outcomes:
**«Расставить флот → Начать бой → Стрелять по очереди → Победа!»**

Use **«Этап»**, never **«Глава»**, for the three child-facing roadmap groups:

1. **«Собираем флот»** — Lessons 1–7;
2. **«Расставляем корабли»** — Lessons 8–13;
3. **«Ход игры»** — Lessons 14–18.

The compact roadmap view shows the current stage, current lesson number,
completed lessons out of 18, and one stage card for each group. The complete
18-lesson list is initially hidden under **«Показать все 18 уроков»** and may be
expanded without changing persisted progress. Implemented lessons follow the
normal access rules. Planned but not yet implemented lessons remain visible as
future work and are never selectable. In debug mode, all implemented lessons
and steps are unlocked; debug mode does not turn roadmap-only entries into
executable lessons. To avoid implying a progress restriction, debug mode marks
roadmap-only stages and lessons as **«В ПЛАНЕ»** instead of showing lock icons.

Opening **«Показать все 18 уроков»** automatically scrolls down until the full
lesson plan is visible while leaving the toggle accessible. Pressing
**«Скрыть полный план»** collapses the plan and returns the course home to its
top position.

#### Lesson access and progression

The lesson header shows its position as **«Урок N из 18 · Этап K»**. On
**«Итоги урока»**, show only the next lesson's number and title when a next
lesson exists; do not repeat its outcome as a second sentence. Derive the
total, numbering, stage membership, titles, and next-lesson preview from
curriculum metadata rather than hard-coding them in the launcher.

Completed lessons remain available. The current lesson is available; later
lessons are visible but locked until all required coding tasks in the current
lesson pass. The **«Итоги урока»** step is also visible but locked until every
required exercise and the cumulative project task in that lesson pass. Optional
star tasks never block the summary or progression. Opening a lesson shows its
saved current step, or its first step when no current step has been saved. The
current step is always unlocked; a locked step cannot be selected or saved as
current. When all required tasks pass, unlock the summary; the optional star
task remains available.

#### Debug mode, global controls, and window

The debug badge, game launcher, command reference, and theme switch occupy a
reserved fixed toolbar above ordinary content on every screen. Page headers
and scrollable content begin below it, and scrolling is clipped at the relevant
content boundary. Ordinary layout regions never overlap or render beneath
fixed controls; only intentional modal overlays may cover the interface.

For development and content review, the launcher accepts `--debug`. This mode
unlocks every implemented lesson and every step, including summaries, and shows
a visible **«РЕЖИМ ОТЛАДКИ»** badge. Debug navigation, theme changes, and
successful runs do not modify persisted progress or completion. Student mode
remains the default; debug mode still opens and executes files from the
selected student directory and never overwrites student edits.

A fixed **«Справочник»** button is visible beside the theme switch on the
course home and every lesson page. It opens the command reference without
changing lesson progress. The reference lists the complete public helper API so
the child can explore it and return to it throughout the course. Each entry
comes from `CURRICULUM.yaml`, opens the existing full signature recap, and
provides a one-click copy action for the exact command signature with visible
success or failure feedback.

A fixed **«Моя игра»** button appears beside the theme switch after the first
cumulative **«Пишем игру»** task passes; debug mode always exposes it. It opens
the student's current `battleship.py` directly in visual play mode, without an
exercise check and without changing progress. The launcher reports launch or
runtime errors in Russian.

The launcher opens at 1180×760, allows normal window resizing and can be
maximized to fill the desktop. Treat 1180×760 as the minimum supported layout.
At larger sizes, anchor fixed controls to the top-right edge, extend the lesson
sidebar to the window bottom, keep lesson actions at the bottom, and expand
home and lesson content within stable outer margins. Lesson cards, notes, and
program output stay aligned and grow together. Calculate modal overlays from
the live window size. Resizing changes layout only; it must not change course
state or require separate theme logic.

### Lesson presentation

#### Step navigation and status

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

Every coding-task card keeps its exercise, project, or star icon on the left
and gains a large green ✓ marker on the right after completion. A red `!`
marker in the same position marks the latest failed attempt for the current
launcher session. The opened-page heading keeps only the task-type icon, and
the selected card keeps its turquoise outline. Do not add a separate lesson
progress row or star counter; the task cards themselves show progress.

Child-facing titles, wording, explanation order, and authoring requirements are
defined in `context/lesson_content.md`. A `summary` is informational, not
material or a coding task.

#### Content cards and feedback

Render lesson text in a responsive column of lightly contrasted cards with
stable outer margins, generous padding, line spacing, and visible space between
major sections. The column uses the available lesson width when the window
grows. A standalone Markdown `---` separates major cards and is rendered as a
compact group of
three yellow submarines. Do not use decorative dividers between ordinary
paragraphs.

Render Markdown `> [!NOTE]` after a coding-task description as a separate card
without an icon or caption. Its italic text contains only the editor prompt and
the instruction to complete, save, and run the task; do not describe prefilled
starter implementation. Keep this card fixed on screen while the task
description scrolls. Render it as an arrow-separated instruction strip aligned
to the task card's width, left edge, and text inset, directly above the action
buttons. Keep it compact and unframed, with smaller muted text, restrained
padding, and a quiet background so it remains secondary to the exercise. Show
contextual feedback immediately above it. The card uses shared layout and theme
palette constants in both schemes.

Render Markdown `> [!RECAP]` inside the scrollable task description as a quiet
framed card with a distinct background. Its text starts with
**«На всякий случай:»** and briefly recalls prerequisite knowledge without
linking away from the task or revealing its solution. Use the same content and
layout in both themes; colors come only from shared theme palette constants.

Render Markdown `> [!EXAMPLE]` inside scrollable lesson content as a compact
example card containing its explanation, code, and visible result. Use a quiet
background, one-pixel border, rounded corners, and normal lesson typography;
do not add an icon or a redundant type caption. Dark and light themes use the
same content and layout, with colors supplied only by theme palette constants.

Before the first console exercise is activated, capture bounded student
`stdout` for every coding run. When it is non-empty, show only the latest run's
output in a distinct fixed card named
**«Результат программы»** above contextual check feedback. Use a small terminal
icon, monospace text, and a code-like background so the card cannot be confused
with lesson-content cards or the quiet workflow note. Hide it before the first
output and never reserve an empty placeholder. Keep it visible after a failed
check or runtime error when partial output exists. Do not show runner protocol
lines in this card.

#### API help

On the page that first introduces a public game API command, show its complete
description inline and render its name as ordinary text. Only later mentions of
that command become underlined clickable references; a command is never a
reference before it has been introduced. Clicking a reference opens a modal
recap with the command's signature, short purpose, and argument summary. Store
both the introduction step and recap content in course metadata so the launcher
remains lesson-agnostic; the modal and links use the shared renderer and theme
palettes.

The fixed command reference is a lookup aid, not a second teaching path. It may
show commands before their lesson introduction, but lessons, tasks, examples,
starters, and clickable in-page references must still follow the prerequisite
rules. The reference derives signatures, summaries, and argument details from
the same curriculum metadata as in-page recaps.

#### Themes

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

### Coding-task workflow

#### Task types and actions

Lessons contain two distinct kinds of coding work:

- **isolated exercises** use separate student-owned `.py` files to practise one
  idea without modifying the game;
- **project milestones** modify the cumulative `battleship.py`.

The optional star challenge is an isolated exercise unless a later lesson
explicitly requires a project extension. It never blocks lesson completion.

Each coding task has two child-facing actions:

- **«Открыть редактор»** opens the correct student file;
- **«Запустить»** reads the saved file, checks it in a subprocess, and presents
  the result using the task's declared output surface.

The launcher retains the process handle for the IDLE window it opens. Pressing
**«Запустить»** closes that launcher-owned editor window before reading and
checking the saved file, so completed attempts do not leave many IDLE windows
open. Closing the launcher also closes its current editor window. Never search
for or terminate unrelated IDLE processes.

#### Execution and feedback

Game output is the default. Task metadata has an optional
`run_mode: console`; omitted `run_mode` means
`game`. Both kinds run once through the checker and may display captured
`stdout`. A `console` task stops after that run and never opens pygame. A `game`
task keeps the existing check-then-real-UI flow; it may also display printed
output. This distinction belongs to lesson metadata so the launcher remains
lesson-agnostic.

For a `game` task, a behavioral failure still opens the real UI so the child can
inspect the result. For a `console` task, the captured output is the visual
result and the program is not repeated. Syntax errors, runtime failures before
useful drawing, and timeouts are reported without repeating the run. Only a
successful behavioral check records completion.

Show feedback inside the selected task near its actions. Do not reserve an
empty status panel or show placeholder messages such as **«Выбери шаг урока»**.
Use the generic reminder **«Сохрани код в редакторе: Cmd+S»**.

#### Progress and transient data

Exercise, project, and star completion are recorded separately. Source code and
verification traces are never stored in progress. Completed tasks may be
reopened, but the launcher never restores or overwrites their files.
Captured output is transient: keep only the latest attempt in memory, clear it
when changing tasks or starting another run, and never write it to progress or
telemetry.

## Installation and distribution

### macOS installation

Provide an idempotent `install.command` script that prepares the project on a
supported Intel or Apple Silicon Mac.

#### Interpreter selection and fallback

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

#### Required installer behavior

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
   including `pygame-ce`, and verify that the launcher, UI, and Python's IDLE
   editor can be started. Remove the obsolete Thonny package from an existing
   project environment during migration. Apply the 18 pt IDLE default only
   when the user has no existing IDLE font preference.
9. Be safe to run repeatedly without overwriting student workspaces or progress.
10. Fail with a nonzero exit status and an actionable Russian message when
   installation cannot be completed.
11. Finish by printing a Russian success message with exact commands for
    starting the launcher for a selected `--student-dir`.

#### Launch wrapper and maintenance

The normal `run.command` wrapper must use the virtual-environment interpreter
directly, so later launches do not depend on whether the machine calls its
global Python 3 executable `python` or `python3`.

`install.command` and its tests must be updated in the same change whenever a
project dependency, dependency version, or supported Python version changes.

## Curriculum storage and execution

### Curriculum and lesson files

#### Metadata, roadmap, and IDs

For V1, one `CURRICULUM.yaml` is sufficient. It defines the child-facing
18-lesson roadmap and its three stages, plus the implemented lesson order and
each lesson's compact pedagogical contract: the new concept, motivating
problem, game milestone, prerequisites, required behavior, paths, and star
challenge. Roadmap entries may describe future lessons without making them
executable; implemented lessons must match their roadmap IDs, titles, order,
and stage membership. The file also stores each public API command's
introduction step and the signature recap used by later clickable mentions.
Its lesson content must follow `context/lesson_content.md`.

Task IDs are globally unique across the course because progress, checker
routing, and API introduction references store them directly. Prefix every new
task ID with its lesson ID, for example `lesson_02_project` or
`lesson_02_exercise_01`. Keep Lesson 1's existing unprefixed IDs unchanged so
existing student progress remains valid. IDs are internal and are never shown
to the child.

#### Optional hints

A coding task may define an optional ordered list of short Russian hints
directly in its metadata:

```yaml
hints:
  - "Первая подсказка."
  - "Следующая подсказка."
```

When hints are present, the launcher initially hides them under
**«Показать подсказку»** and reveals one hint at a time in their YAML order.
Revealed hints remain visible while the task is open and never change task
status or progress. A task without `hints` shows no hint control. Implement
this generic launcher behavior only when the first lesson that uses hints is
implemented.

#### Files, checks, and runner hooks

Detailed material stays in its natural format:

- `lessons/<lesson>/lesson.md` — child-facing content;
- `lessons/<lesson>/exercises/` — immutable starter templates copied into each
  student's workspace and safely refreshed while the copy remains untouched;
- `lessons/<lesson>/acceptance.py` — executable behavioral checks;
- `battleship.py` in the selected student directory — the cumulative game.

An acceptance module exposes
`check(task_id, snapshot, output)`. The runner passes bounded captured `stdout`
as `output`. An interactive task may additionally expose
`prepare(task_id, fake_ui)`; the runner calls it before student code so the
checker can configure deterministic private fake-UI input queues. Student code
never sees or configures those queues. Add multi-scenario execution only when
the first task whose behavior cannot be verified by one deterministic scenario
is implemented.

Do not add per-lesson manifests until one shared curriculum file causes actual
friction.

## Game model and public UI

### Boards and visibility

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

### Cell rendering

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

Each board also owns a remaining-ship counter. Its stored value starts at `0`
and it stays hidden until `show_ship_count(board, count)` is called with an
explicit nonnegative integer. The command may run before or after `show_board`
and repeated calls update the value. When visible, the counter appears in the
board header as the shared orange ship icon and a number inside a score badge.

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

### Fleet setup and gameplay

The final game has two main phases:

1. **Fleet setup** — place and validate the player's ships and create the
   enemy fleet.
2. **Gameplay** — alternate player and computer shots until one fleet is sunk.

Each side has exactly 10 ships. In Part 1 all 10 ships have one deck; Part 2
keeps the same ship count while adding multi-deck ships.

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
show_message("Флот готов!", "Начать бой")
```

The pygame implementation handles the button and its events internally. The
function returns after the click, and student code continues into gameplay. No
listener, callback, scene framework, or framework-controlled phase transition
is exposed to the student.

### Current public API direction

The currently implemented public API is:

```python
PLAYER
ENEMY

DECK_IDLE

show_board(board)
draw_deck(board, x, y, state=DECK_IDLE)
show_miss(board, x, y)
show_ship_count(board, count)
show_message(message, label)
```

`show_board` reveals a board, `draw_deck` places or updates a deck, and
`show_miss` displays an unsuccessful shot. `show_ship_count` shows or updates
the selected board's remaining-ship counter. `show_message` shows a dialog with
a message and labeled button and blocks until the button is pressed. Untouched water
already exists and does not need a public drawing operation. The counter is
introduced in Lesson 2 and the dialog command in Lesson 7; neither is introduced or
required in Lesson 1.

The real and fake implementations must provide the same student-facing API.
Later lessons may add deck damage and sunk states, blocking cell input, and
placement feedback only when those capabilities are first taught and needed.
Before adding or renaming anything, review the complete API
for consistent verbs, argument order, defaults, terminology, and abstraction
level. During Lesson 1 Run, the runner keeps the finished pygame window open
internally until it is closed.
