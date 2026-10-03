# Battleship: Python for Kids

An interactive tutorial where children first learn Python through small
independent problems, then build their own Battleship game. The graphical
helpers provide rendering and input; the child writes the game logic.

## Foundation pilot

The first three replacement lessons are ready for a child pilot:

- A1: reading a file and understanding comments — three answer-choice puzzles.
- A2: displaying text and numbers — five activities, including logic and arithmetic.
- A3: execution order — four activities, including debugging and a deduction problem.

Puzzle submissions reveal the correct answer and explanation even after a
wrong answer. Coding tasks need correct output. These lessons use independent
files, not the cumulative game. Later lessons remain planned, not executable;
pilot these three before expanding the course. Teaching principles and the path are in
[context/lesson_content.md](context/lesson_content.md#learning-path-definition).

## Current platform and language support

At this time, the course has been tested only on macOS. The launcher and lesson
content are designed for Russian-speaking children.

## Install and run

From Terminal, run:

```bash
./install.command
./run.command --student-dir students/child_1
```

Use a different `--student-dir` for
each child. Student edits are preserved; only untouched starters may be safely
refreshed. The launcher opens the task in the configured editor; save it with
`Cmd+S`, then use Run to check the code and see its result. Use fresh student
directories for the first redesigned-course pilots.

Development mode unlocks every
implemented lesson and step without changing saved progress:

```bash
./run.command --student-dir students/debug --debug
```

Debug mode still opens and runs files from the selected directory, so use a
dedicated debug directory when experimenting with source code.

## Development checks

```bash
bash -n install.command
bash -n run.command
.venv/bin/python -m compileall -q battleship_ui launcher runner
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest -q
```

General launcher and runner tests use technical fixtures, not a hidden copy of
the retired course. Pilot tests check every coding reference through the student
checker, puzzle feedback/progress, and the mixed lesson workflow.

The previous curriculum is retired. Fresh lesson/task IDs prevent old
completions from counting toward new lessons; existing student code is preserved.

Pilot verification (2026-10-03): 148 tests passed, including all seven coding
references and end-to-end progression. Shell syntax and runtime compilation
passed. Native macOS startup passed; rendered pages were inspected in both
themes, with layout checks at 1180×760 and 1600×1000. Child testing is pending.
