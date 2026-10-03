# Battleship: Python for Kids

An interactive tutorial where children first learn Python through small
independent problems, then build their own Battleship game. The graphical
helpers provide rendering and input; the child writes the game logic.

## Curriculum redesign

The former lessons have been removed. No replacement lessons are implemented
yet. The launcher, game/UI library, installer, assets, and complete game
reference are retained. Existing student workspaces and progress are untouched.

Until the first new foundation lessons are ready, `run.command` reports that
the course is being redesigned and exits without creating or updating student
files. Teaching principles and the replacement learning path are in
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

Once replacement lessons are available, use a different `--student-dir` for
each child. Student edits are preserved; only untouched starters may be safely
refreshed. The launcher opens the task in the configured editor; save it with
`Cmd+S`, then use Run to check the code and see its result. Use fresh student
directories for the first redesigned-course pilots.

When executable lessons are installed, development mode unlocks every
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
the retired course. New lesson reference checks will be added with the first
replacement lessons.

Curriculum-reset verification (2026-10-03): 102 tests passed; installer and
launcher shell syntax checks and Python compilation passed.
