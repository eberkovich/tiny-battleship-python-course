# Tiny Battleship Python Course

Stage 1 is a local macOS lesson in Russian. A child starts from a course home,
completes three isolated exercises in an external editor, and then adds the
first two commands to a cumulative `battleship.py` game.

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
  --task project \
  --file lessons/lesson_01/reference/project.py
```
