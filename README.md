# Tiny Battleship Python Course

The current local macOS course contains Lessons 1–7 in Russian. A child starts
from a course home that shows the complete 18-lesson Part 1 roadmap, practises
each Python concept in short exercises, and gradually grows a cumulative
`battleship.py` into a fixed fleet of 10 one-cell ships with a battle-start
button. Roadmap-only future lessons are visible but cannot be opened yet.

## Current platform and language support

At this time, the course has been tested only on macOS. The launcher and lesson
content are currently available only in Russian.

## Install and run

From Terminal, run:

```bash
./install.command
./run.command --student-dir students/child_1
```

Use a different `--student-dir` for each child. Existing source and progress are
never overwritten. The launcher opens the correct task in the configured
editor; save it with `Cmd+S`, then use the single **Запустить** button to check
the code and see its visual result.

For lesson development, unlock every implemented lesson and step without
changing saved progress:

```bash
./run.command --student-dir students/debug --debug
```

Debug mode still opens and runs files from the selected directory, so use a
dedicated debug directory when experimenting with source code.

## Development checks

```bash
bash -n install.command
bash -n run.command
.venv/bin/python -m compileall battleship_ui launcher runner lessons
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest -q
```

Run a reference acceptance check directly with:

```bash
.venv/bin/python -m runner.child \
  --mode check \
  --lesson lesson_01 \
  --task project \
  --file lessons/lesson_01/reference/project.py
```
