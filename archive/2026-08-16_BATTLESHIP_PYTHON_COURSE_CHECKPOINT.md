# Battleship Python Course — Project Checkpoint

## Purpose of this file

This file is a handoff/checkpoint for a Codex session. Treat it as the current product and architecture direction unless the user explicitly changes a decision.

The goal is **not** to build a generic coding platform. The goal is to create a small, high-quality Python course that the user's children can start using after a few weekends of development, while preserving a clean path to a simple web version later.

---

# 1. Product goal

Build a **systematic, fun Python course for an active 8-year-old**.

The course should teach genuine programming and algorithmic thinking through one cumulative project: a small Battleship-style game.

The course should feel like:

1. encounter a concrete problem,
2. learn one new programming idea because it helps solve the problem,
3. do a few short exercises,
4. use the new idea in the real Battleship project,
5. visibly improve the game,
6. finish with a small challenge / "boss fight".

The child should feel that **every lesson makes her game more capable**.

The course should *not* feel like:
- a collection of unrelated Scratch projects,
- "make the cat say hello",
- "use this block to make a sound",
- repeated turtle/maze puzzles,
- filling framework-defined callbacks,
- a text-heavy adult programming textbook,
- a school worksheet,
- a generic gamified coding platform.

---

# 2. Audience

Primary target:
- age: about 8,
- very active,
- competitive,
- already has experience with Tynker / Code.org / turtle-style puzzles,
- can work together with an experienced programmer parent.

Important implication:

**The course can use real Python earlier than a normal 8-year-old course because an experienced adult is present to handle setup, syntax friction, and difficult English.**

However, the child's work must still be cognitively age-appropriate:
- short explanations,
- short feedback loops,
- visible results,
- no long lectures,
- no unnecessary abstraction,
- no OOP in student code,
- no framework internals.

---

# 3. Core pedagogical principles

## 3.1 Problem first, syntax second

Do not introduce a construct with an abstract definition and then search for an example.

Preferred:

> Our game only lets us fire once. How can we make it allow five shots without copying the same code five times?

Then introduce a loop.

Avoid:

> A `for` loop is a control-flow construct used for definite iteration...

---

## 3.2 One major new concept per lesson

A lesson may reuse any previously learned concepts, but should introduce at most one substantial new programming idea.

Examples:
- variables,
- comparisons,
- `if` / `else`,
- loops,
- functions,
- lists,
- dictionaries only if genuinely useful,
- decomposition,
- state,
- simple search / AI algorithms.

---

## 3.3 Fast interaction cadence

Aim for no more than a few minutes of explanation before the child does something.

Typical lesson rhythm:

1. **Problem / motivation** — 1–2 min
2. **Short explanation** — 2–4 min
3. **Prediction question** — 1 min
4. **Tiny exercise** — 2–4 min
5. **Second exercise** — 3–5 min
6. **Battleship upgrade** — 10–15 min
7. **Boss challenge** — 5 min

Do not optimize for exact timings; optimize for frequent interaction.

---

## 3.4 Competition is a motivator, not speed pressure

Use:
- stars,
- hidden tests,
- "beat the secret tester",
- boss challenges,
- find-the-bug,
- "can you make it shorter / clearer?",
- optional bonus requirements,
- later: daughter vs parent Battleship / AI.

Avoid making typing speed the primary competition.

Possible scoring:
- ⭐ correct basic behavior,
- ⭐⭐ passes all hidden behavioral cases,
- ⭐⭐⭐ solves the intended concept / bonus challenge.

Do not punish a valid alternative solution merely because it differs from the expected source code.

---

## 3.5 Behavior over source shape

Prefer **black-box behavioral verification**.

Only inspect syntax / AST when the lesson explicitly teaches a construct, and even then prefer using it for a bonus/star rather than functional correctness.

Example:
- game correctly handles 5 shots: required,
- uses a loop rather than five copied calls: bonus / concept check.

---

# 4. Course project: Tiny Battleship

Use a simplified Battleship game rather than full 10×10 Battleship.

Suggested early board:
- 5×5,
- initially one single-cell ship,
- then one 2–3-cell ship,
- later multiple ships,
- only add complexity when it creates a useful programming need.

The game is intentionally simple so that the interesting work is **programming and algorithms**, not domain complexity.

---

# 5. Most important architecture decision

## The student owns the program structure.

Do **not** make the student implement a predefined set of callbacks such as:

```python
def on_hit():
    ...

def on_miss():
    ...

def on_turn():
    ...
```

That becomes "fill predefined holes", which is specifically undesirable.

Instead:

> **Student code is an ordinary procedural Python program.**

The student owns:
- control flow,
- game loop,
- variables / state,
- ships,
- shots,
- hit / miss rules,
- turn rules,
- sunk logic,
- win condition,
- later computer strategy.

The course's graphical library only provides capabilities.

---

# 6. Student-facing programming model

Student code should remain **procedural / structured**, not OOP.

Preferred:

```python
from battleship_ui import *

draw_board()

ship_x = 2
ship_y = 3
draw_ship(ship_x, ship_y)

shot_x, shot_y = wait_for_shot()

if shot_x == ship_x and shot_y == ship_y:
    draw_hit(shot_x, shot_y)
else:
    draw_miss(shot_x, shot_y)
```

Later it can naturally grow into:

```python
from battleship_ui import *

ships = [...]
shots = []

draw_board()

while not game_over(ships, shots):
    x, y = wait_for_shot()

    if is_hit(ships, x, y):
        shots.append((x, y))
        draw_hit(x, y)
    else:
        shots.append((x, y))
        draw_miss(x, y)
```

Later still:

```python
def is_hit(ships, x, y):
    ...

def is_sunk(ship, shots):
    ...

def choose_computer_shot(shots):
    ...
```

The functions should arise because the student's own program becomes repetitive or hard to understand, not because the framework requires named callbacks.

---

# 7. UI library boundary

The student-facing library is analogous to `print()` / `input()`, but graphical.

Possible API:

```python
draw_board()
draw_ship(x, y)
draw_ships(ships)

wait_for_shot()

draw_shot(x, y)
draw_hit(x, y)
draw_miss(x, y)

show_message(text)
show_win()
show_loss()
```

The exact API is not final. Keep it **small and boring**.

## Library owns

- window creation,
- rendering,
- grid layout,
- fonts,
- sprite / shape drawing,
- animations,
- sound,
- mouse-to-cell mapping,
- Pygame event pumping,
- timing,
- other UI mechanics.

## Student owns

- program flow,
- domain/game state,
- ship positions,
- shot history,
- game rules,
- decisions,
- loops,
- functions,
- algorithms,
- AI strategy.

### Rule of thumb

**Library hides mechanics. Student code contains decisions.**

Bad API:

```python
engine.check_if_ship_sunk()
engine.choose_best_ai_move()
engine.validate_ship_position()
```

Those are educationally interesting and should eventually belong to student code.

Good API:

```python
draw_hit(x, y)
wait_for_shot()
show_message("You won!")
```

---

# 8. Event loop design

The graphical engine may internally be event-driven / OOP.

The student should not need to know about:
- frame loops,
- rendering at 60 FPS,
- OS events,
- Pygame event queues.

Expose a synchronous function such as:

```python
x, y = wait_for_shot()
```

Internally, that function may run/pump the UI event loop until a board cell is clicked.

This preserves a natural procedural programming model.

---

# 9. Student code is cumulative across lessons

The main Battleship project should be **one evolving student program**, not a fresh game file per lesson.

Suggested:

```text
workspace/
    battleship.py
```

Lesson 1 modifies it.

Lesson 2 continues modifying the same file.

Lesson 3 continues again.

The child should be able to scroll through the program and see that **she built it progressively**.

Do not split into many modules too early.

A single long-ish file is acceptable and pedagogically useful until organization becomes a genuine problem.

Only introduce another module later if the complexity itself motivates the abstraction.

---

# 10. Mini-exercises are separate and disposable

Short exercises may be isolated.

Example:

```text
lessons/
    04_functions/
        exercises/
            01_double.py
            02_bigger.py
```

Then the lesson transitions back to the cumulative project:

> Now your Battleship code repeats the same hit logic. Turn it into a function.

So the pattern is:

**small isolated practice → apply concept to persistent real game**

---

# 11. Checkpoints and recovery

Because the main program is cumulative, preserve snapshots.

Suggested:

```text
progress/
    checkpoints/
        lesson_01_completed.py
        lesson_02_completed.py
        lesson_03_completed.py
```

Optional additional automatic history:

```text
progress/
    history/
        2026-08-16T120000.py
        2026-08-16T121830.py
```

Launcher action:

**Restore last completed lesson**

Do not make experimentation dangerous.

---

# 12. Verification strategy

## 12.1 Core idea: fake student-facing UI

Do **not** test pixels and do not build tests around the real Pygame implementation.

Provide two implementations behind the same student-facing API:

```text
battleship_ui/
    real_ui.py
    fake_ui.py
```

Normal play:

```text
student battleship.py
    ↓
battleship_ui
    ↓
real graphical implementation
```

Verification:

```text
student battleship.py
    ↓
battleship_ui
    ↓
FakeBattleshipUI
```

The student's program stays unchanged.

---

## 12.2 Prefer a fake, not lots of mocks

`FakeBattleshipUI` should behave like a small headless environment.

It should be able to:
- provide scripted player shots,
- react to what the student draws,
- record semantic events,
- record messages,
- validate coordinates,
- run deterministic scenarios.

Example semantic trace:

```python
[
    ("board_drawn",),
    ("ship_drawn", 2, 3),
    ("shot_requested",),
    ("hit_shown", 2, 3),
]
```

Do not verify implementation-level drawing calls or pixels.

---

## 12.3 Dynamic scenarios

The fake should be able to adapt to student choices.

Example:

The student chooses:

```python
ship_x = 4
ship_y = 1
draw_ship(ship_x, ship_y)
```

A scenario named `shoot_the_ship` can observe that and make:

```python
wait_for_shot()
```

return `(4, 1)`.

A scenario named `shoot_water` can return a valid neighboring water cell.

This avoids hardcoding student choices.

---

## 12.4 Acceptance tests per lesson

Examples:

### Lesson 1
Goal:
- draw board,
- place a valid ship,
- request one shot,
- show the shot.

### Lesson 2
Goal:
- distinguish hit from miss.

Scenarios:
- direct hit,
- water shot.

### Lesson 3
Goal:
- multiple turns.

Scenario:
- supply several shots,
- verify they are all handled.

Optional AST concept check:
- loop exists.

### Later
- multi-cell ships,
- sinking,
- repeated-shot rejection,
- win condition,
- deterministic computer moves,
- AI does not repeat shots,
- AI reacts to a hit.

---

## 12.5 Regression tests

A later lesson must continue passing earlier behavioral acceptance tests.

Show child-friendly feedback such as:

```text
✅ Hit/miss still works
✅ Multiple turns still work
✅ Your new 3-cell ship works
❌ Something from Lesson 2 broke
```

This introduces regression/debugging naturally.

---

## 12.6 Run student code in a subprocess

Do not import arbitrary student code into the launcher process.

Suggested flow:

```text
launcher
    ↓ subprocess
runner
    ↓
student battleship.py
```

Benefits:
- syntax error does not crash launcher,
- runtime error does not crash launcher,
- infinite loop can be terminated,
- clean state for each run,
- easier future isolation.

Set a reasonable timeout.

Translate errors into age-appropriate feedback.

Example:

Instead of raw traceback only:

> Your game kept running for too long. Check whether one of your loops can ever stop.

Keep an optional "show technical details" affordance for the parent.

---

# 13. Verification result format

The runner should return structured data, not UI-formatted text.

Example:

```json
{
  "passed": false,
  "stars": 2,
  "checks": [
    {
      "id": "hit",
      "passed": true,
      "message": "Your game recognizes a hit."
    },
    {
      "id": "miss",
      "passed": false,
      "message": "A shot beside the ship was shown as a hit."
    }
  ]
}
```

The local launcher renders this today.

A web frontend can render the same structure later.

---

# 14. Common launcher

Use **one common launcher for the whole course**.

Responsibilities:
- show course/lesson navigation,
- render lesson explanation,
- open the current exercise / project file,
- Run,
- Check,
- Play,
- show stars / progress,
- restore last checkpoint,
- invoke the runner subprocess.

The launcher should **not contain lesson-specific logic**.

Lessons should be data/content-driven.

Do not build a custom code editor for V1.

Use an existing editor.

---

# 15. Suggested repository layout for V1

Keep this intentionally small.

```text
battleship-course/
│
├── AGENTS.md
├── COURSE_DESIGN.md
├── CURRICULUM.yaml
│
├── launcher/
│   ├── app.py
│   ├── progress.py
│   └── runner_client.py
│
├── runner/
│   ├── run_student.py
│   ├── verifier.py
│   └── result.py
│
├── battleship_ui/
│   ├── __init__.py
│   ├── real_ui.py
│   └── fake_ui.py
│
├── lessons/
│   ├── 01_variables/
│   │   ├── lesson.md
│   │   ├── manifest.yaml
│   │   ├── exercises/
│   │   └── acceptance.py
│   │
│   ├── 02_conditions/
│   └── ...
│
├── workspace/
│   └── battleship.py
│
├── progress/
│   ├── progress.json
│   └── checkpoints/
│
└── tests/
    ├── test_ui_fake.py
    ├── test_runner.py
    └── test_acceptance_framework.py
```

Do not create all abstractions up front if the first vertical slice does not need them.

---

# 16. Candidate V1 curriculum

This is a **starting proposal**, not immutable.

## Lesson 1 — Coordinates and variables
Game milestone:
- show board,
- choose/store one ship location,
- receive one player shot.

Concepts:
- values,
- variables,
- coordinates,
- simple function calls.

## Lesson 2 — Decisions
Game milestone:
- show HIT or MISS.

Concept:
- comparisons,
- `if` / `else`.

## Lesson 3 — Multiple shots
Game milestone:
- player can fire several times.

Concept:
- loops.

## Lesson 4 — Functions
Game milestone:
- extract repeated hit logic / turn logic.

Concept:
- functions,
- parameters,
- return values.

Important:
Functions should be motivated by duplication/complexity already visible in the student's own code.

## Lesson 5 — A real ship
Game milestone:
- ship occupies multiple cells.

Concept:
- lists.

## Lesson 6 — Sink the ship
Game milestone:
- remember shots,
- detect when all ship cells are hit,
- playable tiny Battleship milestone.

Concept:
- combining lists + loops + functions + persistent game state.

That is enough for the first version.

Possible later lessons:
- multiple ships,
- random placement,
- prevent duplicate shots,
- computer opponent,
- smarter computer opponent,
- game persistence / JSON,
- algorithmic improvement.

---

# 17. Lesson content format

Each lesson should contain:

1. **Goal**
2. **Why the game needs this idea**
3. **Very short explanation**
4. **1–2 tiny examples**
5. **Prediction question**
6. **2–3 short exercises**
7. **Battleship upgrade**
8. **Boss challenge**
9. **What changed in your game**
10. **Optional parent note** — hidden/collapsible if UI supports it

Avoid long definitions.

Write directly to the child.

Example tone:

> Your ship can fire once. That's not much of a battle.
>
> We could copy the same code five times, but programmers have a better trick: a loop.

Avoid childish baby-talk.

---

# 18. Content generation workflow with Codex

The user should own:
- curriculum order,
- lesson goal,
- what Battleship capability is added,
- educational judgment.

Codex can generate:
- lesson prose,
- examples,
- starter files,
- exercise variants,
- hidden tests,
- acceptance scenarios,
- checkpoint/reference versions,
- regression tests,
- repetitive manifests.

Recommended per-lesson prompt:

> Implement the next lesson from `CURRICULUM.yaml` following `COURSE_DESIGN.md` and the existing lesson pattern. Keep the explanation short and appropriate for an active 8-year-old. Add 2–3 mini-exercises, behavioral checks, the cumulative Battleship upgrade, and one boss challenge. Do not add new framework abstractions unless required by the existing architecture.

Then use a second review pass:

> Review this lesson as an educational editor. Flag excessive explanation, concepts not previously introduced, exercises solvable by copying the example, unnecessary vocabulary, more than a few minutes without interaction, or a Battleship task that does not genuinely require the lesson concept. Then fix the issues.

---

# 19. V1 implementation strategy

## Weekend / iteration 1: one vertical slice

Build **one complete lesson experience**, not the whole engine.

It should prove:

```text
lesson explanation
    ↓
tiny exercise
    ↓
edit real Python
    ↓
Check
    ↓
child-friendly result
    ↓
run graphical Battleship
    ↓
visible game progress
```

Only after this works with the child should abstractions be extracted.

## Iteration 2
- lessons 2–4,
- checkpoints,
- reusable acceptance framework,
- basic progress/stars.

## Iteration 3
- lessons 5–6,
- polish,
- sounds/animations if they materially improve motivation,
- regression checks,
- child testing.

---

# 20. Explicit V1 non-goals

Do not build:
- accounts,
- cloud backend,
- custom IDE,
- browser code editor,
- generic plugin system,
- generic course-authoring platform,
- server-side untrusted Python execution,
- complicated telemetry pipeline,
- multiplayer,
- production publishing infrastructure,
- OOP curriculum for the student,
- large generic game engine.

If a feature is not required for the first child to complete lesson 1–6, question whether it belongs in V1.

---

# 21. Future web path

Design clean boundaries now, but do not implement the web version yet.

Desired long-term shape:

```text
Browser
├── lesson UI
├── embedded editor
├── browser-side Python runtime
├── graphical board
└── progress / telemetry client
```

Prefer browser-side execution of student Python rather than sending arbitrary student code to a backend.

The future backend should ideally only need:
- static/course content,
- optional accounts,
- progress sync,
- telemetry.

Avoid creating a server-side untrusted-code execution service unless there is a compelling future reason.

Keep the runner/checker output serializable so local and web UIs can share the same logical protocol.

---

# 22. Telemetry / logging

Do not overbuild V1 logging.

Define a tiny semantic event layer from the start, even if it initially writes JSONL locally.

Possible events:

```text
lesson_started
lesson_completed
exercise_started
code_run
check_started
check_passed
check_failed
hint_requested
checkpoint_created
game_started
game_completed
```

Example:

```json
{
  "event": "check_failed",
  "lesson": "03_loops",
  "exercise": "battleship_upgrade",
  "attempt": 2
}
```

Avoid logging every keystroke.

If published for children later, minimize data collection and revisit privacy requirements before deployment.

---

# 23. Important architectural invariants

Keep these unless there is a strong reason to change them.

1. **Student code is procedural, not OOP.**
2. **Student owns game state.**
3. **Student owns game control flow.**
4. **Student is not filling predefined callbacks.**
5. **UI library only provides graphical/input capabilities.**
6. **Main Battleship program is cumulative across lessons.**
7. **Mini-exercises can be isolated.**
8. **Verification is primarily behavioral.**
9. **Tests use a fake student-facing UI.**
10. **Student code runs in a subprocess for checking.**
11. **Launcher is common and lesson-agnostic.**
12. **V1 should remain small enough to finish in a few weekends.**
13. **Do not design the system around hypothetical publishing needs. Preserve a web path through clean boundaries instead.**

---

# 24. Open design questions

These have not been firmly decided yet.

- Exact local UI toolkit for launcher.
- Exact graphics implementation (Pygame is a likely V1 choice, not a requirement).
- Exact code editor to launch.
- Exact student-facing `battleship_ui` API.
- Whether `draw_board()` is called explicitly by student code in every stage or can later become part of a higher-level render call.
- Exact format for lesson manifests (`yaml` vs `json`).
- Exact mechanism for swapping real/fake `battleship_ui`.
- How aggressively AST checks should be used.
- Whether stars are per exercise, per lesson, or both.
- Exact later browser Python runtime.
- Exact terminology/naming for the game (Battleship vs a renamed original theme).

Do not silently "resolve" these by adding large abstractions. Prefer the smallest implementation that keeps options open.

---

# 25. First engineering task recommended for Codex

Build **Lesson 1 as a vertical slice** before designing the entire framework.

Acceptance criteria:

1. Repo has minimal runnable structure.
2. `workspace/battleship.py` is genuine student-editable Python.
3. Student can explicitly call `draw_board()`.
4. Student can choose a ship position with variables.
5. Student can call `wait_for_shot()` and receive grid coordinates.
6. Real UI shows the board and shot.
7. Fake UI can execute the same student program headlessly.
8. A verifier can check Lesson 1 behavior.
9. Student program runs in a subprocess during verification.
10. Launcher can show a small structured result.
11. No custom editor.
12. No generic architecture not needed by Lesson 1.
13. Tests exist for the fake UI and verifier.
14. README explains how the parent launches the lesson.

After the vertical slice works, review the architecture based on actual friction before adding Lesson 2.

---

# 26. Suggested first Codex prompt

Use this after placing this checkpoint and `AGENTS.md` in the repository:

> Read `BATTLESHIP_PYTHON_COURSE_CHECKPOINT.md` and `AGENTS.md`. Implement the smallest end-to-end Lesson 1 vertical slice described in the checkpoint. Do not implement future lessons and do not build a custom editor, backend, account system, plugin framework, or generic course engine. Keep student code procedural and cumulative. The student must own program flow; do not replace it with callbacks. Use a real graphical implementation plus a fake implementation of the same student-facing UI for behavioral verification. Run the tests and update the README with exact local run/check commands.

---

# 27. Definition of success for the prototype

The prototype succeeds if an 8-year-old can:

1. read a short explanation,
2. change real Python code herself,
3. run it,
4. immediately see something meaningful happen in the Battleship UI,
5. press Check and get understandable feedback,
6. fix a mistake,
7. complete the lesson,
8. feel that her own game became better.

Everything else is secondary.
