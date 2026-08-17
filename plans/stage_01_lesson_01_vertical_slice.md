# Stage 1 Plan: Lesson 1 Vertical Slice

## Outcome

Deliver one complete, installable lesson experience on macOS:

```text
install → course home → lesson → editor → Run (check + visual result)
```

The launcher, lesson, real UI, fake UI, runner, and installer must work together.
Build only what Lesson 1 needs. Follow `AGENTS.md` and
`context/architecture.md` for enduring rules and detailed architecture.

## Lesson 1 contract

Child-facing title: **«Знакомство с игровым полем»**.

The lesson teaches game-framework commands and the 10×10 coordinate system in
two separate articles, with the API article first:

- `(1, 1)` is top-left;
- `x` grows to the right;
- `y` grows downward;
- both axes use values `1..10` and have visible labels.

After the isolated exercises, the cumulative student program is initially
limited to:

```python
from battleship_ui import *

show_board(PLAYER)
show_board(ENEMY)
```

Required behavior:

- show the player and enemy boards separately;
- finish without an exception while Run keeps the visual result visible.

The lesson has exactly three required isolated exercises:

1. **«Покажи своё поле»** — call `show_board(PLAYER)`.
2. **«Нарисуй однопалубный корабль»** — with the player board already shown by
   the starter, draw `DECK_IDLE` at `(2, 4)`.
3. **«Покажи промах»** — with the enemy board already shown by the starter,
   call `show_miss` at `(4, 2)`.

These exercise operations do not become part of `battleship.py` in Lesson 1.
The optional star starter already shows both boards because the child completed
that behavior in the project task. The star asks only for a three-deck ship and
a miss; it does not require retyping the project solution as setup.

Lesson content is entirely in Russian and includes a short API article that
explicitly introduces `show_board`, `draw_deck`, `show_miss`, and their
constants before use. Each argument uses an `argument_name — explanation`
bullet, and every available fixed value is listed without calling it an enum.
A separate coordinate article then explains only the coordinate system using
the already introduced API. Three isolated exercises, a **«Пишем игру»**
upgrade, and a separate optional **«Задача со звёздочкой»** are followed by a
`summary` step named **«Итоги урока»**. Do not add a passive prediction step.
Each editable exercise is copied into the selected student's
`exercises/lesson_01/` directory; the project upgrade alone modifies
`battleship.py`.
Add a plain parent note only if useful; do not build special UI for it. Do not
introduce variables, input, conditions, loops, lists, OOP, fleet placement, hit
detection, or AI in this lesson.

## Stage 1 public UI

Implement the same surface in the real and fake backends:

```python
PLAYER
ENEMY

DECK_IDLE

show_board(board)
draw_deck(board, x, y, state=DECK_IDLE)
show_miss(board, x, y)
```

Defer `wait_for_cell`, `wait_for_button`, placement feedback, and other API
until the first lesson that needs them.

## Deliverables

- `pyproject.toml` with one authoritative set of pinned runtime/test
  dependencies, including `pygame-ce` and Thonny.
- `CURRICULUM.yaml` with one compact Lesson 1 entry.
- `battleship_ui/real_ui.py` and `battleship_ui/fake_ui.py` behind the unchanged
  student import.
- A subprocess runner and Lesson 1 behavioral verifier returning structured
  results with Russian messages.
- A minimal pygame launcher with a course home, lesson navigation, step icons
  without duplicate type captions, combined Run, per-task progress including
  the optional star segment, and `--student-dir` support.
- Russian Lesson 1 content, isolated exercise/star templates, starter project,
  and passing reference programs for verifier tests.
- Independent per-student `battleship.py`, exercise files, and `progress.json`.
- Idempotent `install.command` and `.venv`-based `run.command` for macOS.
- Focused tests, end-to-end acceptance coverage, and concise run/check docs.

## Implementation order

1. Add packaging, pinned dependencies, the curriculum entry, result schema,
   directories, and student template.
2. Build the one-lesson pygame launcher, course home, editor opening, combined
   run/check flow, typed navigation, progress, and safe `--student-dir`
   initialization for project and exercise files.
3. Implement two labeled 10×10 boards and the cell states used by Lesson 1 in
   the real UI. Render each visible intact deck with the same full-cell static
   wooden mast-and-sail sprite so horizontal and vertical ships repeat cleanly.
   Render a miss as a full-cell open-water sprite with a large cartoon
   cannonball and white-and-cyan splash.
4. Implement the matching fake UI with deterministic semantic traces.
5. Write and review the Russian lesson, exercises, starter, star challenge, and
   passing reference program.
6. Add isolated check and visual subprocesses behind one Run action, timeout
   handling, verification, and structured Russian feedback.
7. Add safe macOS installation, `.venv` execution, full tests, visual review,
   and fresh-workspace integration verification.

## Verification cycle for every implementation increment

1. Add/update the smallest focused test, then implement the behavior.
2. Run affected tests and Lesson 1 acceptance through the subprocess/fake UI.
3. Run the full suite.
4. For rendering changes, inspect a headless screenshot and periodically the
   real macOS window.
5. Review the diff for student ownership, procedural API, Russian content,
   real/fake parity, V1 scope, and installer synchronization.

Do not use pixel-perfect assertions. Test semantic events, geometry, state, and
control flow; inspect visuals separately.

## Verification matrix

| Area | Required checks |
| --- | --- |
| API | Real/fake constants and signatures match; both boards begin hidden; `show_board` is idempotent and never resets cells; `draw_deck` and `show_miss` while hidden are valid; untouched water needs no public drawing call; unknown boards/deck states and coordinates outside `1..10` fail clearly. |
| Real UI | Only shown boards are rendered; state drawn while hidden appears when shown; geometry and axis labels are correct; player idle decks use the packaged full-cell wooden mast-and-sail sprite and repeat horizontally or vertically; enemy idle decks stay hidden; misses use the packaged blue-water cannonball-and-splash sprite on either board; later draws replace earlier cell state. |
| Fake UI | Records deterministic semantic events, resets between runs, never creates a display, and does not retain traces as telemetry. |
| Runner | Covers success, required board not shown, wrong board, invalid coordinates, syntax/runtime errors, and timeout; the launcher survives every failure. |
| Lesson | API article introduces every call, constant, state, and argument before any task or starter uses it; arguments use `argument_name — explanation` bullets and list every available fixed value without saying “enum”; separate coordinate article introduces no API; examples differ from task answers; no passive prediction; clear non-solution task wording; passing reference for every checked task; behavioral checks only; required Russian structure; no variables, input, conditions, loops, lists, OOP, fleet validation, hit logic, or AI. |
| Launcher | Shows course home and lesson navigation; distinguishes step types with icons but no duplicate type captions; uses a finish flag for the `summary`; omits filenames and editor brand from child text; opens the correct file; never overwrites source; preserves work/progress; isolates two students; supports spaces/Cyrillic in paths; checks through fake UI before visual play through real UI; shows behavioral failures visually but does not repeat technical failures; uses one **«Запустить»** action; shows every coding task, including the optional numbered star, in segmented progress; shows contextual feedback; and reports errors in Russian. |
| Installer | Shell syntax; controlled-PATH cases for Python 3 as `python3` or `python`, versioned Homebrew Python without an unversioned link, supported Homebrew Python without Tk, Homebrew Tk failure without system fallback, Python 2, missing/old Python, existing `.venv`, repeated runs, dependency failure, and spaces/Cyrillic; prefers matching Homebrew Tk without `sudo`, never modifies system Python, and verifies launcher/UI/Thonny startup and Russian instructions. |

A passing Lesson 1 project trace contains the equivalent of:

```python
[
    ("board_shown", "player"),
    ("board_shown", "enemy"),
]
```

Review all child-visible lesson, launcher, and result text for Russian-only
presentation. Dependency or supported-Python changes must update installation
assets and tests in the same change.

## Planned validation commands

```bash
bash -n install.command
bash -n run.command
.venv/bin/python -m compileall battleship_ui launcher runner lessons
.venv/bin/python -m pytest tests/test_fake_ui.py -q
.venv/bin/python -m pytest tests/test_real_ui.py -q
.venv/bin/python -m pytest tests/test_runner.py -q
.venv/bin/python -m pytest tests/test_lesson_01.py -q
.venv/bin/python -m pytest tests/test_launcher.py -q
.venv/bin/python -m pytest -q
```

## Definition of done

On a supported Mac, a fresh checkout can run `install.command`, then
`run.command --student-dir <path>`. A child starts from the Russian course
home, enters Lesson 1, sees clearly typed material and tasks, edits separate
exercise files in the external editor, and uses one **«Запустить»** action for
checking plus visual feedback. The child then upgrades `battleship.py` and sees
two correct 10×10 boards. Repeating the process for another student path creates
independent project code, exercises, and progress. Automated checks pass, real
rendering is visually inspected, documentation matches the commands, and no
later-lesson infrastructure has been added.

## Current verification evidence

The first implementation passed automated verification, then child-facing
review reopened the stage. The resulting `show_miss`, lesson-prerequisite,
presentation, summary, and per-task progress revisions are now implemented and
reverified.

- Shell syntax, compilation, dependency consistency, focused tests, the full
  suite, reference Play, reference Check, and the headless launcher flow pass.
- The full suite currently contains 54 passing tests.
- Game and launcher screenshots were inspected without pixel assertions, and a
  real macOS pygame game window was opened and closed successfully. The revised
  course home, typed lesson navigation, API article, coordinate article, and
  exercise, star, and summary screens were also inspected, and the revised
  native launcher window opened and closed successfully. The final static deck
  sprite was inspected at the real 40×40 cell size in both horizontal and
  vertical three-deck ships. The final miss sprite was inspected at 40×40 on
  both the open player board and closed enemy board.
- The installed dependency set is consistent, including `pygame-ce` 2.5.8,
  PyYAML 6.0.3, Thonny 5.0.0, and pytest 9.1.1.
- The first actual `install.command` fallback downloaded the pinned package and
  verified its SHA-256 checksum, but initially stopped after parsing localized
  `pkgutil` output as English. Signature verification now uses `pkgutil`'s
  validation result directly. The installer now also prefers adding the
  matching Tk formula to an existing supported Homebrew Python without `sudo`
  and stops instead of changing the default Python when Homebrew fails. That
  path now also discovers Homebrew's versioned Python when an upgrade removes
  the unversioned `python3` link. The installer completion and Thonny GUI smoke
  test still await a successful rerun.

Do not mark Stage 1 complete or activate another stage until the real installer
and Russian Thonny file-opening smoke test pass on macOS, or the user explicitly
changes this completion requirement.
