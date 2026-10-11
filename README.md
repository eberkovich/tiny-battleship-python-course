# Battleship: Python for Kids

An interactive tutorial where children first learn Python through small
independent problems, then build their own Battleship game. The graphical
helpers provide rendering and input; the child writes the game logic.

## Foundation lessons

The first nine replacement lessons are available:

- A1: reading a file and understanding comments — three answer-choice puzzles.
- A2: displaying text and numbers — five activities, including logic and arithmetic.
- A3: execution order — four activities, including debugging and a deduction problem.
- A4: arithmetic — six activities, ending with a workbook-based figure exchange.
- A5: grouping with parentheses — five activities, including saving and rope problems.
- A6: naming and reusing values — five activities, including card sharing,
  plus an optional pair-weighing challenge.
- A7: changing and preserving values — six activities, including minimum-coin
  change and swapping two values.
- A8: text input — five activities, including preserving answers and a Mad Libs story.
- A9: converting text to integers — six activities, including a number trick
  and the hens-and-sheep problem.

Puzzle submissions reveal the correct answer and explanation even after a
wrong answer. Coding tasks need correct output. These lessons use independent
files, not the cumulative game. The user has tried A1–A3 with the children and
reports positive feedback; A4–A9 are ready for their next trial. Later lessons
remain planned, not executable. Teaching principles and the path are in
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

In A8 and A9, Run opens a field for each answer requested by Python's `input()`.
Type the answer and press Enter; Stop or Esc cancels the run. The child can take
time to think: waiting for an answer does not trigger an execution timeout.
After the program finishes, private checks try different answers without
replacing the child's own output.

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

Verification (2026-10-11): 383 tests passed, including all thirty-three coding
references, untouched-starter rejection, worked examples with supplied input,
thirteen puzzle contracts, optional-star progression, varied-input checks,
preserved earlier student work, and end-to-end progression through A1–A9.
Input transport checks cover Unicode and empty answers, cancellation, resumed
timeouts, hard-coded answer rejection, and preservation of the child's output.
Shell syntax and runtime/reference compilation passed; intentional syntax-error
repair starters are checked as failing starters rather than compiled as valid code.
Headless production-renderer previews were inspected in both themes at
1180×760 and 1600×1000, alongside automated layout checks.
Native macOS startup was checked in the initial pilot (2026-10-03). A1–A3
child-pilot feedback is user-reported, not a measured mastery result; A4–A9
child testing is next.

The separate A9¾ shop-calculator capstone is agreed but not implemented yet.
