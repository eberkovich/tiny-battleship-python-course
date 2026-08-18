# Lesson Content Guide

This document is the source of truth for child-facing lesson authoring.
`context/architecture.md` defines product and technical behavior; the active
stage plan defines which lesson is currently in scope.

## Learner and teaching style

The course is for an active child of about eight who already knows basic
turtle-, maze-, or block-style programming and is supported by an experienced
programmer parent. This is the child's first experience with a textual
programming language: do not assume familiarity with code vocabulary,
punctuation, or line-based syntax.

- Start with a concrete problem and introduce syntax as a tool for solving it.
- Introduce at most one major new concept per lesson.
- Pace material by conceptual difficulty, not by a fixed lesson count. Difficult
  concepts may need a concrete motivation, several small examples, preliminary
  exercises, and more than one lesson before they enter the cumulative project.
- Prefer representations that match what the child already sees and require the
  fewest new concepts. Introduce compound data gradually: first one meaningful
  value, then a collection of such values, and only later its formal terminology.
- Use standard Python `print` output for preliminary exercises about abstract
  values such as variables, lists, booleans, and function results. Use the game
  UI when the concept naturally changes a board, ship counter, prompt, or shot;
  do not add artificial teaching-only commands to the public game API.
- Keep explanations short and feedback frequent and visible.
- Use stars, debugging, and optional challenges without speed pressure.
- Write all child-facing lesson text, launcher labels, hints, and check feedback
  in Russian. Keep code identifiers and developer documentation in English.
- Avoid baby-talk and passive activities that do not produce feedback.
- Before the child must read or write new syntax, explain its terms and visible
  marks in concrete language: what each name means, what parentheses and commas
  do, and what Python will do with the whole line.
- When explaining the course's support layer to the child, call its public API
  **«вспомогательные команды»**, not a framework, library, or engine. First
  state the concrete game the child will finish and which game rules the child
  will write; then explain exactly what the helper commands provide.

## Lesson shape

A lesson normally contains:

1. a motivating problem;
2. a short explanation;
3. an optional interactive question;
4. two or three isolated exercises;
5. a cumulative Battleship project upgrade named **«Пишем игру»**;
6. an optional **«Задача со звёздочкой»**;
7. a summary named **«Итоги урока»**.

Every lesson must visibly advance the same cumulative Battleship game. Use
isolated exercises to practise one idea and a project milestone to advance the
game. Keep the star task optional. File ownership and execution behavior are
defined in `context/architecture.md`.

Each article or exercise must have one clear purpose. Every paragraph must
directly support that purpose. After drafting a step, describe its purpose in
one sentence and verify that its title, opening, content, and ending all match
that sentence. Move content that serves a different purpose to a separate
step.

## Lesson page presentation

- Show each step's icon and title in the sidebar and repeat the same icon and
  title as the page heading. Do not add type captions such as **«Материал»**,
  **«Упражнение»**, or **«Со звёздочкой»**.
- Render prose in a narrow column of lightly contrasted cards. Prefer short
  paragraphs, generous padding and line spacing, and visible space between
  major sections.
- Use a standalone Markdown `---` only between major article sections. It
  becomes a divider of three yellow submarines; do not use it between ordinary
  paragraphs.
- Use indented Markdown bullets for nested values; the launcher displays them
  as round dots rather than dashes.
- On an API command's introduction page, keep its name as ordinary text and
  provide the complete explanation inline. On later pages, the launcher turns
  its name into an underlined clickable recap. A command must never appear as a
  reference before its introduction.
- After a coding-task goal, show the workflow note as a compact, unframed fixed
  strip in smaller muted italics. Align it with the task card and place it
  directly above the action buttons; contextual feedback appears immediately
  above the strip. Keep the task description independently scrollable.

## Prerequisites and explanation order

Apply prerequisites to every first use in reading order. Before lesson prose,
an example, task, starter, or checker uses an API call, constant, state, syntax,
or programming concept, child-facing text must explain it explicitly. A concept
may be explained earlier on the same page; otherwise it must appear in an
earlier lesson step. Never rely on a later explanation.

An API signature is part of introducing that API: it may name the command and
its arguments. Explain every argument and fixed value before the first complete
example or task uses them. If an API depends on a separate concept such as
coordinates, explain that concept before introducing or demonstrating the API;
they may share one article when this order remains clear.

Starter setup may reuse material taught in earlier steps, but it must not
silently contain new child-owned concepts. A checker must require only behavior
that has been stated to the child after all of its prerequisites were taught.

Beginner-facing API material must:

- show the exact call form in a monospace block;
- explain each argument as `argument_name — explanation`;
- list and explain every fixed public value available at that point without
  calling the values an enum; put those values in indented nested bullets, which
  the launcher displays as round dots rather than dashes;
- include a complete example whose values differ from the task answer;
- state the expected visible result.

Every public API command mentioned in lesson prose or code must have its
introduction step and a Russian signature recap in `CURRICULUM.yaml`: its call
form, short purpose, and argument summary. Recap metadata must contain only
concepts already introduced at that point in the course. Follow the
introduction/reference presentation rule above.

Before the first exercise uses `print`, introduce it as a Python function, show
the exact `print(value)` form, explain its argument, and demonstrate the
launcher card named **«Результат программы»**. State that `print` helps inspect
a value and does not change the game. Later exercises may use that card only
after this explanation.

## Exercises and project tasks

- State an unambiguous visible goal and name the relevant API commands without
  showing the final solution.
- Keep starter context out of the goal. After every coding-task description,
  add one separate note block in this form:

  ```markdown
  > [!NOTE]
  > Открой редактор → выполни задание → сохрани изменения → нажми **«Запустить»**.
  ```

  Do not add an icon or caption to this strip. Do not describe starter
  implementation in child-facing text. Keep editor, save, and Run directions
  inside the strip; do not mix them into the task goal.
- Make the child think rather than copy an example directly.
- For a console exercise, state the expected visible output and keep it short
  enough to read in the launcher's result card. Do not require a pygame window
  when printed output is the complete observable result.
- Do not show reference solutions in child-facing text.
- Add hints only when a task is demonstrably difficult without them; discussion
  of a difficult concept alone is not a reason to add hints to other tasks.
  Store short ordered hint strings in the task's optional `hints` list in
  `CURRICULUM.yaml`. Make them progressive: first restate or split the problem,
  then point to relevant known ideas, and only in the final hint offer
  pseudocode when necessary. Do not reveal the complete Python solution. Every
  hint must use only concepts already introduced before the task.
- Do not repeat behavior already completed and checked unless repetition is an
  explicit learning objective.
- When an isolated task depends on earlier behavior, put the previously taught
  setup in its starter and ask only for the new result; do not explain that
  prefilled setup in the child-facing task or workflow strip.
- Use **«редактор»** in child-facing text; do not name Thonny or student files.
  Tool names and filenames may appear in parent/developer documentation.

Include a question step only when the launcher can collect an answer and give
immediate feedback. Do not add prompts such as “think”, “guess”, or “show with
your finger” merely to satisfy a lesson template. Integrate useful information
from a non-interactive prompt into the preceding article or remove it.

## Authoring verification

Before finalizing a multi-lesson course part, maintain a complete reference
program for its final milestone. Inventory every child-visible syntax form,
standard-library operation, public API call, and game rule used by that program,
and assign each item to the lesson that introduces it. Repeat the inventory
whenever the reference changes. Separately inventory teaching-only constructs
used in articles, examples, starters, and preliminary exercises, such as
`print`, even when they do not remain in the final reference program.

For every exercise, project milestone, and star task:

- define the expected observable result clearly;
- ensure the task and starter use only introduced material;
- maintain at least one passing reference solution outside child-facing text;
- run that solution through the same behavioral checker used for student code;
- ensure the checker tests only requirements stated to the child.

Before accepting a lesson, review it for age appropriateness, excessive text,
long gaps between interactions, accidental answer disclosure, and any API or
concept used before its explanation.
