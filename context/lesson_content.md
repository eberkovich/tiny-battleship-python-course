# Lesson Content Guide

This document is the source of truth for child-facing lesson authoring.
`context/architecture.md` defines product and technical behavior; the active
stage plan defines which lesson is currently in scope.

## Learner and teaching style

### Content quality is the priority

Lesson content is the primary product of this project. Give its structure,
clarity, progression, and exercises more attention than implementation speed,
framework convenience, or the number of lessons. Every lesson must be
publication-quality for a child: purposeful from beginning to end, engaging to
complete, precise enough to work without guessing, and valuable enough to teach
a reusable programming or algorithmic idea. Do not ship content that is merely
technically valid, repetitive, or a thin pretext for a game action.

### Learner profile

The course is for an active child of about eight who already knows basic
turtle-, maze-, or block-style programming and is supported by an experienced
programmer parent. This is the child's first experience with a textual
programming language: do not assume familiarity with code vocabulary,
punctuation, or line-based syntax.

### Concept progression and pace

- For every new concept, begin with a concrete need in the evolving game, then
  explain the general programming idea and its syntax, and finally apply it
  back to the game. The game provides motivation and visible feedback; it must
  not narrow the explanation to one Battleship recipe.
- Teach each concept as a reusable tool for programming and algorithmic
  thinking: make clear what kind of problem it solves, how information changes
  step by step, and where the same idea could be useful beyond the current
  coordinates or ships.
- Introduce at most one major new concept per lesson.
- Pace material by conceptual difficulty, not by a fixed lesson count. Difficult
  concepts may need a concrete motivation, several small examples, preliminary
  exercises, and more than one lesson before they enter the cumulative project.
- Prefer representations that match what the child already sees and require the
  fewest new concepts. Introduce compound data gradually: first one meaningful
  value, then a collection of such values, and only later its formal terminology.

### Feedback and language

- Use standard Python `print` output for preliminary exercises about abstract
  values such as variables, lists, booleans, and function results. Use the game
  UI when the concept naturally changes a board, ship counter, prompt, or shot;
  do not add artificial teaching-only commands to the public game API.
- Keep explanations short and feedback frequent and visible.
- Use stars, debugging, and optional challenges without speed pressure.
- Write all child-facing lesson text, launcher labels, hints, and check feedback
  in Russian. Keep code identifiers and developer documentation in English.
- Avoid baby-talk and passive activities that do not produce feedback.

### Reusable exercise inputs

When an isolated exercise practises a reusable rule or transformation rather
than a concrete UI interaction, require the child to implement a named function
with clearly documented parameters and result. The behavioral checker must call
that function with several representative values, including values not shown in
the task. Do not make success depend only on a hardcoded input and its known
answer: that checks one calculation, not the general rule. Keep fixed values in
examples for explanation, while tasks state the function's contract and let the
checker supply the test data. Use direct UI exercises only when the learning
goal is genuinely a visual or input interaction.

When an upcoming run of lessons relies on child-written reusable rules, teach
function foundations in the opening lesson of that run, before comparisons,
loops, or domain-specific validation begin using such functions. That opening
lesson may cover `def`, parameters, and `return` as one closely related
foundation, but each element still needs its own explanation, complete example,
and focused practice. Its examples must use only programming ideas already
taught; do not smuggle in the later stage's logic merely to make the function
look game-related.

### Exercise originality and algorithmic practice

An isolated exercise must make the child apply the current concept to a
purposefully different small problem from its preceding examples and from that
lesson's project milestone. Do not copy an example's function name, control
flow, domain rule, or intended result and merely replace values, coordinates,
or labels. A project task may reuse the real game rule after focused practice;
the focused practice must first build transferable reasoning.

Prefer varied, age-appropriate algorithmic puzzles with a visible result:
choosing an order, swapping or selecting values, comparing scores, checking a
simple rule, counting, repeating a message, or making a random choice. The
child should have a small decision or transformation to work out, rather than
only transcribe a pattern. `print`, lists, earlier loops, and already taught
dialogs are valid feedback tools. Use a game-framework command only when the
exercise genuinely practises a visual game action or player input; it is never
required merely because the course is about Battleship.

### Self-contained exercise specifications

Every coding exercise must be understandable without opening an earlier article
or guessing from a variable name. Before the requested implementation, define
the meaning and shape of every input in plain language, state the exact result
or visible action, and give one labelled concrete example with data different
from the checker cases. Say explicitly whether a collection contains numbers,
addresses, words, or another kind of value; a name such as `passwords` or
`ships` is not an explanation. The example must show the expected result, both
for the ordinary case and for an important opposite case when the task has one.
Copy this complete specification into the starter-file comments.

### Syntax and helper API explanations

- Before the child must read or write new syntax, explain its terms and visible
  marks in concrete language: what each name means, what parentheses and commas
  do, and what Python will do with the whole line.
- When a function is introduced, explicitly distinguish the argument name in
  the command description from the concrete value supplied in a call. Show the
  description and a complete call, map the value to its name, and state which
  part stays the same and which part the child chooses. Do not rely on a compact
  form such as **«board — PLAYER или ENEMY»** to teach this distinction.
- Before the child reads or edits the first multi-line program, explain the
  default execution order with a concrete trace: Python starts at the top and
  handles executable lines one after another, while blank lines and comments
  do not perform actions. When later concepts such as loops or conditions alter
  this simple order, explain the change explicitly.
- For each new Python construction, explain the concrete problem it solves,
  how to read it aloud, what Python does in order, what value or state changes,
  the meaning of new punctuation, and one likely mistake. Give a complete
  example whose values differ from the following task. Difficult concepts may
  need several small examples rather than one dense article.
- Teach in short explanation–example cycles. Put the first complete example
  immediately after the minimum explanation needed to understand it; do not
  postpone it until after terminology, secondary uses, generalizations, and
  common mistakes. When a concept has several difficult operations or
  distinctions, place another small example next to the specific part it
  clarifies instead of collecting all examples at the end of the article.
- Make every code fragment unambiguous at first sight. Prefer complete
  statements with meaningful names over isolated operators, unexplained
  placeholders, or incomplete constructions. When explaining how code changes,
  show a complete before-and-after example and explicitly say what changed. An
  individual punctuation mark may appear on its own only when that mark is the
  explicit subject of the explanation and a complete nearby example shows it
  in context.
- When explaining the course's support layer to the child, call its public API
  **«вспомогательные команды»**, not a framework, library, or engine. First
  state the concrete game the child will finish and which game rules the child
  will write; then explain exactly what the helper commands provide.

## Lesson shape

### Standard sequence

A lesson normally contains:

1. a motivating problem;
2. a short explanation;
3. an optional interactive question;
4. normally three or four short isolated exercises;
5. a cumulative Battleship project upgrade named **«Пишем игру»**;
6. an optional **«Задача со звёздочкой»**;
7. a summary named **«Итоги урока»**.

Every lesson must visibly advance the same cumulative Battleship game. Use
isolated exercises to practise one idea and a project milestone to advance the
game. Keep the star task optional. File ownership and execution behavior are
defined in `context/architecture.md`.

### Step purpose, opening, and roles

Each article or exercise must have one clear purpose. Every paragraph must
directly support that purpose. After drafting a step, describe its purpose in
one sentence and verify that its title, opening, content, and ending all match
that sentence. Move content that serves a different purpose to a separate
step. The title stored in course metadata, the sidebar, and the step heading
must be identical; validate this whenever a lesson step is renamed.

Teach one new programming concept per article. If a draft introduces another
independent mental model, operation, or syntax form, move it to its own article.
Keep the essential parts of one construction together when they cannot be used
separately; punctuation and argument details required to read one function call
are not separate concepts. Do not re-teach an older concept inside an unrelated
article: use a short recap only when it is genuinely needed.

Follow every new programming concept with at least one focused exercise before
asking the child to combine it with another new concept. An API command may be
the visible tool used by that exercise; it does not require a separate exercise
when the task already focuses on the programming concept being practised.

Keep every lesson coherent from motivation to result. Each newly introduced
programming concept or game API command must follow one complete path: concrete
need, explanation, focused practice, use in that lesson's cumulative project,
and a truthful recap. If the current project milestone does not need it,
postpone its introduction. If all new concepts cannot be used naturally in one
small milestone, split the lesson.

A summary may mention achievements from isolated exercises, but must identify
them as practice. Claims such as **«твоя игра теперь…»** or **«твоя
программа теперь…»** may describe only behavior verified by the
completed cumulative project task. Never present an isolated exercise result as
already integrated into the game.

Make the role of every statement unmistakable. Explicitly separate what is
already true, the rule being explained, an illustrative example, the action the
child must perform, and the observable success condition. Introduce every
illustrative example with **«Пример:»** or **«Например:»** and state what
it demonstrates. Never embed an unlabeled example inside an instruction or
make the child infer whether a shown value is sample data, existing setup, an
input, or the required result. Unless a value is itself part of the stated
goal, use different values in examples and tasks.

Every lesson step must be understandable from its first sentence without
assuming that the child remembers an unstated preceding situation. Open with a
concrete orientation: what is happening now, what problem must be solved, or
what result the child is about to create. Only then introduce a definition,
rule, syntax form, or example. Never begin an article or task in the middle of
an explanation with a bare definition or rule.

## Lesson page presentation

The architecture and authoring documents are maintained in English. Russian
is reserved for child-facing lesson text and exact UI or code literals that
the documentation must preserve.

- Show each step's icon and title in the sidebar and repeat the same icon and
  title as the page heading. Do not add type captions such as **«Материал»**,
  **«Упражнение»**, or **«Со звёздочкой»**.
- Render prose in a narrow column of lightly contrasted cards. Prefer short
  paragraphs, generous padding and line spacing, and visible space between
  major sections.
- Put every illustrative example in one Markdown block containing its label,
  explanation, code when present, and visible result:

  ````markdown
  > [!EXAMPLE]
  > **Пример:** что показывает этот пример.
  >
  > ```python
  > print(7)
  > ```
  >
  > После запуска появится `7`.
  ````

  Keep code lines contiguous inside fenced examples. Preserve every leading
  space that represents Python indentation, and use blank quoted lines only to
  separate code from its explanation; an empty line must never become a
  separate code row or card in the lesson renderer.

  Do not split one example across ordinary prose and several unrelated cards.
- Use a standalone Markdown `---` only between major article sections. It
  becomes a divider of three yellow submarines; do not use it between ordinary
  paragraphs.
- Use indented Markdown bullets for nested values; the launcher displays them
  as round dots rather than dashes.
- On an API command's introduction page, keep its name as ordinary text and
  provide the complete explanation inline. On later pages, the launcher turns
  its name into an underlined clickable recap. A command must never appear as a
  reference before its introduction.
- The launcher's fixed command reference is available as a recall aid during
  exercises and may show the complete API before individual commands are
  taught. This does not count as introducing a command: lesson text, examples,
  starters, tasks, and clickable in-page mentions must still follow the normal
  prerequisite order. Lesson text must remain understandable without opening
  the reference.
- After a coding-task goal, show the workflow note as a compact, unframed fixed
  strip in smaller muted italics. Align it with the task card and place it
  directly above the action buttons; contextual feedback appears immediately
  above the strip. Keep the task description independently scrollable.

## Prerequisites and explanation order

### First-use audit

Apply prerequisites to every first use in reading order. Before lesson prose,
an example, task, starter, or checker uses an API call, constant, state, syntax,
or programming concept, child-facing text must explain it explicitly. A concept
may be explained earlier on the same page; otherwise it must appear in an
earlier lesson step. Never rely on a later explanation.

Before finalizing each coding task, inventory every operation used by one
passing solution and by its starter—not only the lesson's headline concept.
Creation, reading or selecting a value, changing it, unpacking, iteration,
comparison, calls, built-ins, and new punctuation are separate prerequisites.
Each required operation must have an explanation and a complete earlier
example. Teaching how to create a value does not implicitly teach how to read
or change it.

An API signature is part of introducing that API: it may name the command and
its arguments. Explain every argument and fixed value before the first complete
example or task uses them. If an API depends on a separate concept such as
coordinates, explain that concept before introducing or demonstrating the API;
they may share one article when this order remains clear.

Starter setup may reuse material taught in earlier steps, but it must not
silently contain new child-owned concepts. A checker must require only behavior
that has been stated to the child after all of its prerequisites were taught.
Treat comments as Python syntax: before a starter first contains a line
beginning with `#`, explain that it is a comment for people and that Python does
not execute it.

### Terminology and recall

A technical term counts as introduced only when child-facing text explains it
in plain language, connects it to the code syntax or action it names, and gives
a complete example. Merely mentioning or naming a term does not introduce it.

Do not use a technical term as the only instruction in an exercise. When a term
returns in a later lesson, restate the required action in plain language,
especially when remembering the term is not the exercise's objective. The term
may follow as a reminder in parentheses.

When an exercise depends on an easily forgotten concept from an earlier
lesson, add a short recap after its goal using this form:

```markdown
> [!RECAP]
> На всякий случай: краткое напоминание простыми словами.
```

Never recap a concept introduced in the current lesson: its article and current
practice must teach it clearly enough. Keep a recap to one or two short ideas,
and use it only when an older prerequisite is needed but otherwise absent from
the current lesson context. Do not add a recap when a nearby article or the task
itself already gives an actionable reminder: it explains how to perform the
operation, shows usable syntax, or names a clickable API command. A bare term,
vague action, or prefilled line that the child is not asked to understand does
not count as a reminder. Prefer a generic syntax form or different values, and
do not reveal the solution. Do not use links: the child must be able to
continue without leaving the task. The launcher renders the recap as a quiet
framed card with its own background in both themes.

During the prerequisite review, inventory every technical word in articles,
tasks, notes, starters, and feedback. For each word, identify its definition
and verify that the current instruction remains understandable without testing
the child's memory of terminology.

### API introductions and references

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

### Console output

Before the first exercise uses `print`, introduce it as a Python function in
general terms: it shows a person the value passed to it. Show the exact
`print(value)` form, explain its argument, give an example and its visible
output, and mention common purposes such as showing a result, a message, or a
value the program currently stores. Do not define `print` through the
launcher's output card or contrast it with the game UI. Later console exercises
may rely on the already introduced visible output.

## Exercises and project tasks

### Exercise progression

- State an unambiguous visible goal and name the relevant API commands without
  showing the final solution.
- Increase difficulty within a lesson. Start with one small demonstrated
  action, then ask the child to change or complete familiar code, diagnose or
  verify a result, combine the new idea with known material, and finally apply
  it independently in **«Пишем игру»**. Use only the steps that help the
  concept; do not add filler to reach a fixed exercise count.
- Vary the work itself, not only constants or coordinates. Suitable forms
  include completing a line, changing a value and observing the result,
  correcting a deliberate mistake, combining two familiar operations, and
  producing a visible game result.
- An isolated exercise may rehearse one component needed by the project task,
  but must not ask for substantially the same program, combination of actions,
  or visible result. Review the child-owned new lines in both tasks; ignore
  imports, prefilled code, and game state already completed in earlier lessons.
  A different number of calls, values, coordinates, or surrounding setup is
  not a meaningful difference by itself. Give the exercise a narrower,
  diagnostic, or abstract goal, and reserve a distinct composition or durable
  integration into the cumulative game for **«Пишем игру»**.
- Give consecutive exercises different thinking jobs whenever the concept
  allows it: construct, predict or select, diagnose, combine, and apply. Do not
  repeat the same operation with only another value type or another set of
  numbers.

### Task instructions and starter files

- Keep starter context out of the goal. After every coding-task description,
  add one separate note block in this form:

  ```markdown
  > [!NOTE]
  > Открой редактор → выполни задание → сохрани изменения → нажми **«Запустить»**.
  ```

  Do not add an icon or caption to this strip. Do not describe starter
  implementation in child-facing text. Keep editor, save, and Run directions
  inside the strip; do not mix them into the task goal.
- Copy the complete visible goal of every isolated exercise and star task into
  its starter file as Russian comments, including the task title, required
  result, success condition, and any **«На всякий случай:»** recap. Omit only
  the editor workflow strip. Keep this copy synchronized with the lesson text
  so the child can complete the task without switching back to the launcher.
  Do not copy milestone instructions into cumulative `battleship.py`: that file
  is shared by all project tasks and must contain only game code.

### Feedback and solution boundaries

- Make the child think rather than copy an example directly.
- Every exercise must produce immediate observable feedback. Use `print` for
  values and calculations, the game window for boards and game state, and
  deliberate broken-code tasks for debugging. Do not create passive exercises
  whose only action is reading or continuing.
- For a console exercise, state the expected visible output and keep it short
  enough to read in the launcher's result card. Do not require a pygame window
  when printed output is the complete observable result.
- Do not show reference solutions in child-facing text.

### Hints and star challenges

- Add hints only when a task is demonstrably difficult without them; discussion
  of a difficult concept alone is not a reason to add hints to other tasks.
  Store short ordered hint strings in the task's optional `hints` list in
  `CURRICULUM.yaml`. Make them progressive: first restate or split the problem,
  then point to relevant known ideas, and only in the final hint offer
  pseudocode when necessary. Do not reveal the complete Python solution. Every
  hint must use only concepts already introduced before the task.
- A **«Задача со звёздочкой»** must be an interesting, substantial challenge,
  not an ordinary exercise with more values or repeated calls. It should
  combine already taught ideas, require the child to plan several steps, and
  end with a distinctive visible result. It must introduce no hidden concept
  and remain independently solvable from the course and task statement, while
  demanding noticeably more thought and effort than required exercises. Good
  forms include a coordinate puzzle, multi-error debugging, or transferring
  familiar constructs to a new kind of data. If a proposed star task is
  trivial, repetitive, or needs adult explanation, redesign or omit it.

### Cumulative project milestones

- Do not repeat behavior already completed and checked unless repetition is an
  explicit learning objective.
- Treat every **«Пишем игру»** task as an incremental edit to the same
  `battleship.py`. Begin its goal with a concrete verb such as **«Добавь»**,
  **«Продолжи»**, or **«Замени только…»**; state which existing visible behavior
  must remain; and identify the exact old fragment when replacement is needed.
  Never ask the child to recreate already completed game behavior.
- Keep teaching-only experiments, including temporary `print` calls, in
  isolated exercise files. The cumulative project should contain only code
  that contributes to the game or to a deliberately introduced debugging
  step, and temporary debugging code must be removed by an explicit task.
- When an isolated task depends on earlier behavior, put the previously taught
  setup in its starter and ask only for the new result; do not explain that
  prefilled setup in the child-facing task or workflow strip.

### Child-facing tooling and question steps

- Use **«редактор»** in child-facing text; do not name IDLE or student files.
  Tool names and filenames may appear in parent/developer documentation.

Include a question step only when the launcher can collect an answer and give
immediate feedback. Do not add prompts such as “think”, “guess”, or “show with
your finger” merely to satisfy a lesson template. Integrate useful information
from a non-interactive prompt into the preceding article or remove it.

## Authoring verification

### Course-part inventory

Before finalizing a multi-lesson course part, maintain a complete reference
program for its final milestone. Inventory every child-visible syntax form,
standard-library operation, public API call, and game rule used by that program,
and assign each item to the lesson that introduces it. Repeat the inventory
whenever the reference changes. Separately inventory teaching-only constructs
used in articles, examples, starters, and preliminary exercises, such as
`print`, even when they do not remain in the final reference program.

### Per-task verification

For every exercise, project milestone, and star task:

- define the expected observable result clearly;
- ensure the task and starter use only introduced material;
- maintain at least one passing reference solution outside child-facing text;
- run that solution through the same behavioral checker used for student code;
- ensure the checker tests only requirements stated to the child.

Cover these requirements economically. Prefer one parameterized reference test
and shared structural lesson validation over separate boilerplate tests for
every task. Add focused failing examples only for meaningful game rules,
prerequisite boundaries, and runner error paths. Do not lock ordinary editorial
wording into tests; assert exact text or reading order only when it carries an
essential explanation, required term, or task contract. Complete end-to-end
win/loss and cumulative-game scenarios belong at phase checkpoints rather than
in every intermediate lesson.

### Editorial review

Before accepting a lesson, review it for age appropriateness, excessive text,
long gaps between interactions, accidental answer disclosure, and any API or
concept used before its explanation. Also verify that its exercises rise in
difficulty, differ in purpose, and leave the cumulative game with no unrelated
training code.
