# Stage 1 Plan: Lesson 1 Vertical Slice

## Outcome

Deliver one complete, installable lesson experience on macOS:

```text
install → select student directory → exercise files → project file → Play → Check
```

The launcher, lesson, real UI, fake UI, runner, and installer must work together.
Build only what Lesson 1 needs. Follow `AGENTS.md` and
`context/architecture.md` for enduring rules and detailed architecture.

## Lesson 1 contract

Child-facing title: **«Знакомство с игровым полем»**.

The lesson teaches game-framework commands and the 10×10 coordinate system:

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
- finish without an exception while Play keeps the result visible.

The lesson has exactly three required isolated exercises:

1. **«Покажи своё поле»** — call `show_board(PLAYER)`.
2. **«Поставь палубу»** — with the player board already shown by the starter,
   draw `DECK_IDLE` at `(2, 4)`.
3. **«Покажи промах»** — with the enemy board already shown by the starter,
   draw `WATER_FIRED` at `(4, 2)`.

These exercise operations do not become part of `battleship.py` in Lesson 1.

Lesson content is entirely in Russian and includes a short motivation,
coordinate prediction, three isolated exercises, a Battleship upgrade,
and a separate optional **«Задача со звёздочкой»**, followed by
**«Что изменилось в твоей игре?»**. Each editable exercise is copied into the
selected student's `exercises/lesson_01/` directory; the project upgrade alone
modifies `battleship.py`.
Add a plain parent note only if useful; do not build special UI for it. Do not
introduce variables, input, conditions, loops, lists, OOP, fleet placement, hit
detection, or AI in this lesson.

## Stage 1 public UI

Implement the same surface in the real and fake backends:

```python
PLAYER
ENEMY

WATER_IDLE
WATER_FIRED
DECK_IDLE

show_board(board)
draw_water(board, x, y, state=WATER_IDLE)
draw_deck(board, x, y, state=DECK_IDLE)
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
- A minimal pygame launcher with lesson text, current-task file name, Open Code,
  Play, Check, stars, and `--student-dir` support.
- Russian Lesson 1 content, isolated exercise/star templates, starter project,
  and passing reference programs for verifier tests.
- Independent per-student `battleship.py`, exercise files, and `progress.json`.
- Idempotent `install.command` and `.venv`-based `run.command` for macOS.
- Focused tests, end-to-end acceptance coverage, and concise run/check docs.

## Implementation order

1. Add packaging, pinned dependencies, the curriculum entry, result schema,
   directories, and student template.
2. Build the one-lesson pygame launcher, Thonny file opening, and safe
   `--student-dir` initialization for project and exercise files.
3. Implement two labeled 10×10 boards and the cell states used by Lesson 1 in
   the real UI.
4. Implement the matching fake UI with deterministic semantic traces.
5. Write and review the Russian lesson, exercises, starter, star challenge, and
   passing reference program.
6. Add isolated Play/Check subprocesses, timeout handling, verification, and
   structured Russian feedback.
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
| API | Real/fake constants and signatures match; both boards begin hidden; `show_board` is idempotent and never resets cells; drawing while hidden is valid; unknown boards/states and coordinates outside `1..10` fail clearly. |
| Real UI | Only shown boards are rendered; state drawn while hidden appears when shown; geometry and axis labels are correct; player idle decks are visible; enemy idle decks stay hidden; fired water is distinct; later draws replace earlier cell state. |
| Fake UI | Records deterministic semantic events, resets between runs, never creates a display, and does not retain traces as telemetry. |
| Runner | Covers success, required board not shown, wrong board, invalid coordinates, syntax/runtime errors, and timeout; the launcher survives every failure. |
| Lesson | Behavioral checks only; required Russian structure; no variables, input, conditions, loops, lists, OOP, fleet validation, hit logic, or AI. |
| Launcher | Shows the selected task and file; opens that file in Thonny; never overwrites source; preserves work/progress; isolates two students; supports spaces/Cyrillic in paths; routes Play to real UI and Check to fake UI; keeps successful Play visible; and reports errors in Russian. |
| Installer | Shell syntax; controlled-PATH cases for Python 3 as `python3` or `python`, Python 2, missing/old Python, existing `.venv`, repeated runs, dependency failure, and spaces/Cyrillic; never modifies system Python; verifies launcher/UI/Thonny startup and Russian instructions. |

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
`run.command --student-dir <path>`. A child sees the Russian Lesson 1, edits and
checks separate exercise files in Thonny, then upgrades `battleship.py`, sees two
correct 10×10 boards through Play, and receives Russian behavioral feedback
through Check. Repeating the process for another student path creates
independent project code, exercises, and progress. Automated checks pass, real
rendering is visually inspected, documentation matches the commands, and no
later-lesson infrastructure has been added.
