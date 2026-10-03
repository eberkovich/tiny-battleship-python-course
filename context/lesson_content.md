# Lesson Content and Learning Path

This document defines how to teach and what to teach, in two sections:

- [Teaching principles](#teaching-principles): the content-quality contract.
- [Learning path definition](#learning-path-definition): ordered outcomes and
  prerequisite progression for the replacement course.

`context/architecture.md` defines technical and product behavior. Implementation
plans define concrete work and verification, not another curriculum.

## Teaching principles

### Priority, learner, and language

Lesson content is the primary product. Give its structure, explanation quality,
and meaningful exercises more attention than implementation speed, checker
convenience, or lesson count. Technically valid but superficial, repetitive,
or artificial material is not ready to ship.

The learner is an active child of about eight, familiar with basic turtle,
maze, or block programming, supported by a programmer parent. This is the
child's first textual programming language. Assume no knowledge of Python
vocabulary, punctuation, line-based syntax, or invisible execution state.

Write child-facing articles, tasks, hints, starter comments, UI labels, and
feedback in Russian. Use English code identifiers and developer documentation.
Avoid baby-talk, speed pressure, and unexplained technical language.

### Learning design

#### Two sections, different purposes

- **Foundations:** teach programming through independent everyday problems,
  puzzles, and small programs. No required Battleship connection and no
  cumulative game task. Use `print` when values or messages are the result.
- **Building the game:** apply established skills to meaningful playable
  features. Explain new coordinates, helper commands, randomness, or rules
  before using them. A project milestone changes the same cumulative program.

Do not force a game upgrade into every lesson or introduce a concept merely
because a reference implementation uses it. The final game is an application
of learning, not the justification for every preliminary exercise. These
learning sections are separate from the game's one-cell and multi-deck parts.

Teach each concept as a reusable tool: what problem it solves, what Python
does, how information changes, and where else it helps. A game example must
not reduce the explanation to a Battleship recipe.

#### Pace and evidence of understanding

Introduce at most one major new concept per lesson. Difficult concepts may
span several lessons, with separate explanations and practice for distinct
operations. There is no fixed lesson or exercise count to fill or compress.
Prefer representations that require the fewest new mental models: one
meaningful value before a collection, concrete behavior before formal terms.

Use a purposeful progression, not a rigid template:

1. Explain a concrete problem with a small example and an execution trace.
2. Ask the child to predict an unfamiliar short program before running it.
3. Investigate an outcome or mistake and explain why it happened.
4. Solve a different small problem, choosing steps rather than copying them.
5. Transfer the idea to changed inputs or constraints.

Each prediction or investigation needs an explicit way to compare the answer
with the actual result and explain the difference. Do not use passive prompts
such as “think” or “point” as substitutes for a task. Add a separate question
step only when the launcher can collect an answer and give feedback; otherwise
use a supported coding/run activity or an explicitly parent-led pilot check.
Do not claim that an answer was checked when no mechanism collects it.

A guided first exercise is useful, but is not evidence of independent
understanding. Required work must include reasoning beyond transcription;
do not reserve that work for optional stars. A green acceptance result proves
the stated behavior, not mastery. Before expanding the replacement course,
pilot the first few lessons: can the child explain a short program and solve a
changed problem without being given its lines?

### Explanations and prerequisite order

#### Explain behavior, not just spelling

Start every article with a concrete orientation and purpose. Teach in short
explanation–example cycles: the first complete example follows the minimum
explanation needed to read it, not several screens of terminology. Put another
small example next to each difficult distinction instead of collecting them
at the end.

For a new construction, explain its purpose, how to read it, Python's execution
steps, changed values or state, new punctuation, and a likely mistake. Use
small traces or name-to-value diagrams when prose alone hides the mechanism.
Show initial state, each relevant step, and the result. Prefer familiar,
age-appropriate problems rather than extra mathematics.

In particular:

- Explain function calls before requiring them. Distinguish argument names in
  a signature from values in a call, map each value to its name, and show which
  parts stay fixed and which the child chooses. When defining functions later,
  explicitly connect supplied arguments to parameters and local execution.
- Before a multi-line program, trace top-to-bottom execution. Blank lines and
  comments perform no actions; later conditions, loops, and function calls
  alter the simple order and need their own traces.
- Explain comments before starter files first contain `#` instructions.
- Show assignment and reassignment as changes to name-to-value relationships;
  do not confuse a name with its current value.
- Separate list creation, counting, indexed access, membership, mutation, and
  iteration. Teaching creation does not teach the other operations implicitly.
- Explain printing versus returning, loop-body indentation, search completion,
  and loop termination explicitly when first needed.

Prefer complete statements with meaningful names over unexplained placeholders
or isolated operators. To explain a change, show complete before-and-after code
and say what changed. Show a punctuation mark alone only when it is the subject
and a nearby complete example gives its context.

#### Audit every first use

Review in reading order, including prose, examples, tasks, starter code,
comments, hints, and feedback. Every needed syntax form, operation, constant,
API call, and technical term must have an explicit earlier explanation and a
complete example. An explanation earlier on the same page is sufficient;
a later one is not. Naming a term is not explaining it.

Inventory the operations used by a passing solution and its starter, not just
the lesson's headline concept. Creation, reading, changing, unpacking, calls,
comparison, built-ins, and punctuation are separate prerequisites. Starter
setup cannot silently smuggle in new child-owned concepts. Checkers require
only behavior stated after its prerequisites were taught.

Follow each new concept with focused practice before combining it with another
new concept. Essential parts of one construction may remain together, but an
independent mental model needs its own article and practice. In particular,
function definitions, parameters, and returned results need slow explanation
and examples, not one dense syntax paragraph.

Technical terms must be defined in plain language, connected to their syntax
or action, and illustrated. Do not use a term as the only task instruction;
restate the action in ordinary language when recall is not the objective.

#### Helper commands and output

Use the game API only when a task genuinely needs graphics or input. Explain
to the child what the support layer does with concrete actions, not the words
framework, engine, or library. Use the established child-facing term
**«вспомогательные команды»**. First explain the game goal and the child's
responsibility for its logic.

An API introduction includes the exact signature, each argument as
`argument_name — explanation`, all fixed public values available at that point
in nested bullets (not “enums”), a complete example distinct from the task,
and its visible result. Explain dependent ideas such as coordinates first.
Record introduction steps and Russian signature recaps in curriculum metadata;
recaps use only material available at that point. The global reference is a
lookup aid, not prerequisite teaching.

Introduce `print` generally: it shows a person the supplied value. Explain
`print(value)`, its argument, examples, and visible output before any task uses
it. Only afterwards explain where output appears in this application. Do not
define the Python concept through a launcher card or a game-board comparison.

### Exercise design

#### Activity mix and volume

Plan **4–6 required activities per typical coding lesson**, interleaved with
short explanations:

- one prediction puzzle: predict a result, then run, compare, and explain;
- one debugging puzzle: find a mistake, repair it, and explain the cause;
- one or two focused coding exercises;
- one or two independent problems that cannot be solved by copying an example.

These are learning activities, not new launcher step types. Use the supported
coding/run workflow or an explicitly parent-led pilot check for puzzles. Count
each activity once even when it combines prediction, editing, and running.
A meaningful game milestone may serve as an independent problem; do not add
an isolated duplicate to fill the count.

Worked examples and explanations do not count as exercises. An optional star
challenge is additional and appears only when genuinely interesting and
appropriate; it never replaces required independent reasoning.

This mix is a planning default, not a quota. Short orientation lessons may
have fewer activities. Split difficult topics across more lessons rather than
overloading one lesson or adding repetitive tasks to reach a number.

#### Purpose and originality

Each task has one clear thinking job and an observable result. Vary the work:
predict, construct, compare, diagnose, explain, combine, or transfer. Use
ordering, small calculations, familiar words, counting, searches, or robot-like
instructions when appropriate. Increasing difficulty means more independent
reasoning, not more identical calls or larger numbers.

An independent exercise must differ meaningfully from both its preceding
example and any project task. Changing only inputs, names, coordinates, labels,
or call count does not count. Compare the child-owned steps and reasoning,
ignoring imports and prefilled setup. A narrower diagnostic problem can practise
one component; durable game integration must still be a distinct task. Avoid
consecutive tasks with essentially the same solution strategy. Required work
must include a problem whose solution cannot simply be copied from an example.

Before functions are taught, tasks may be ordinary scripts; do not require an
unexplained function definition for checker convenience. State explicit inputs
and outcomes, and use prediction, changed scenarios, or debugging to go beyond
a single copied calculation. After functions are taught, reusable-rule tasks
normally ask for a named function with documented parameters and a result.
The checker supplies varied representative inputs, including unfamiliar and
important boundary/opposite cases. Do not accept a hardcoded known answer as
evidence of a general rule. Multiple inputs alone do not make a task thoughtful.

#### Complete, unambiguous specifications

A task must stand alone from its first sentence. Define the situation, every
input's meaning and shape, requested action, exact output or returned result,
and success condition. State whether a collection contains numbers, words,
addresses, or another type; variable names do not explain this. For a function,
say whether the child writes its body, some missing part, or the complete
definition, and whether the checker or the child calls it.

Give a labelled concrete example with data distinct from assessment cases and
the expected result; include an important opposite case when one exists. Make
existing setup, rule, sample data, required action, and result unmistakably
different. Label examples **«Пример:»** or **«Например:»**. Never start in the
middle of an unexplained situation or imply that an example is the task answer.

After drafting, describe the step's purpose in one sentence. Its title, opening,
content, example, and ending must match that sentence. Verify title agreement
between metadata, heading, and starter comments whenever renaming a task.

#### Star tasks, hints, and feedback

Optional star tasks combine taught ideas into an interesting, substantial
challenge with a distinctive result and several steps to plan. They must be
independently solvable by the child with significant effort, no hidden concepts,
and no required adult explanation. Redesign or omit trivial, repetitive, or
incomprehensible stars. They never block completion.

Add hints only for demonstrably difficult tasks, not to every task because hints
exist. Store ordered Russian hints in the task's YAML `hints` list: first divide
or restate the problem, then recall useful ideas, finally offer pseudocode if
necessary. Do not reveal a full Python solution or use untaught ideas.

Every coding task produces immediate feedback through short printed output,
real graphics/input when relevant, or deliberate debugging. The checker tests
the stated contract, not one exact source spelling. Keep reference answers out
of child-facing material. Explain failure in terms of the requested behavior.

### Lesson and file composition

A lesson normally contains a concrete problem, short articles interleaved with
practice, required independent application, an optional star task, and a
truthful summary. Foundation lessons end with a small program or independent
problem; game lessons include a meaningful **«Пишем игру»** milestone when
appropriate. There is no obligation to use every step kind.

The summary distinguishes practice achievements from integrated game features.
Claims about what the cumulative game now does must be backed by its completed
project task. Do not imply that an isolated exercise was integrated or that a
successful check proves understanding.

Game milestones incrementally edit the same `battleship.py`. State the exact
addition or replacement, what existing behavior remains, and which old fragment
to change. Do not ask the child to redo checked work or silently discard code.
Keep teaching experiments in independent files. A temporary debugging addition
to the game needs an explicit later removal task. Put familiar prerequisite
setup in starters when it is not the task's learning objective.

Copy each isolated exercise/star specification into its starter as Russian
comments: title, inputs, result, examples, success condition, and any recap.
Synchronize it with the lesson; omit only editor workflow instructions. Do not
copy successive milestone descriptions into the shared cumulative game file.
Refer to the child-facing tool as **«редактор»**, not a brand or filename.

### Content markup and recall

Visual styling, themes, icons, layout, and run behavior belong to the
architecture. Author content using its supported blocks:

- `> [!EXAMPLE]`: one labelled example, explanation, contiguous fenced code,
  and result together. Preserve four-space Python indentation in all lessons;
  verify source and rendered indentation. Do not let blank lines turn into
  separate code cards or split one example across unrelated blocks.
- `> [!RECAP]`: one or two brief ideas beginning **«На всякий случай:»**,
  only for a needed prerequisite from an earlier lesson. Never recap the current
  lesson or repeat a reminder already given in the same lesson's context.
  Usable syntax or a clickable API name counts as a reminder; a bare term does
  not. Use different values or a generic form, no solution and no links.
- `> [!NOTE]`: only the shared editor → complete → save → Run instructions.
  Keep tooling directions out of task goals and do not add a note caption or
  starter-implementation disclaimer.
- Standalone `---`: major sections only, not ordinary paragraphs.
- Nested Markdown bullets: fixed values, not manually typed dash prefixes.

API introduction pages explain the command fully inline; only later mentions
become clickable recaps. The global command list does not replace explanation.

### Authoring review and verification

For each lesson, record its outcome, prerequisites, examples/mental models,
exercise purposes, understanding evidence, and game feature only if applicable
under the learning path below. Before releasing a section, inventory syntax,
operations, API calls, and rules used in its reference programs, including
teaching-only constructs. Assign every item an introduction and practice point;
update the inventory when references change.

For every coding task, keep a passing reference outside child-facing content
and run it through the student's behavioral checker. Use shared validators and
parameterized cases; add focused failures for meaningful rules, prerequisite
boundaries, and execution errors. Avoid exact-prose/source assertions except
where they protect an essential teaching contract. Full suites and complete
game scenarios run at checkpoints and handoff, not every text edit.

Review explanations, terminology, starter copies, title/content agreement,
prerequisite order, example proximity, ambiguous wording, age suitability,
accidental solutions, and exercise independence together. Explicitly ask what
the child must reason out and how understanding is assessed. Pilot early lessons
with the children before authoring the entire replacement course.

## Learning path definition

### Scope and interpretation

The goal is to understand basic Python and small algorithms, then independently
build a complete one-cell Battleship game. The final game has two 10×10 boards,
10 ships per side, valid non-touching placement, hidden enemy ships, hit/miss
feedback, counters, non-repeating shots, alternating turns, and victory/defeat.
Multi-deck ships are a later game part, not the second learning section below.

Section A is split into **32 planned lessons**: each A-number below denotes one
lesson, not a topic block. Some lessons consolidate a known tool rather than
introducing more syntax. This is a working split, not a count to preserve at
the expense of understanding; revise boundaries explicitly after child pilots.
Section B still defines game-feature milestones, not individual lessons.

The labels and English titles below are authoring references, not runtime IDs
or final child-facing titles. Assign Russian titles and fresh globally unique
IDs when lessons are authored.

Each entry states its learning goal and evidence of transfer. Puzzle domains
are illustrative, not complete exercise specifications or solutions. Actual
tasks still need explicit inputs, examples, success conditions, reference
answers, and prerequisite review.

### Section A — Programming foundations

Foundation coding tasks use independent scripts and printed results. No game
file, coordinate pairs, or graphical helper commands are required. A1 is a
short reading orientation before coding begins; it does not require a quiz UI
or an empty-program exercise. Each later lesson includes focused practice and
independent application, with short articles interleaved rather than one dense
explanation. Consolidation lessons introduce no hidden syntax.

#### A1. Reading the first file

**Learn:** a program contains instructions for the computer; `#` begins a
comment for the person reading it, not an action. Explain starter directions
before opening the first commented file. Do not use untaught Python commands
to demonstrate comments.

**Evidence:** a parent-led reading check: the child identifies the directions
in a starter and explains why they do not run. Do not claim an automated
understanding check or invent a source-pattern checker for comments.

#### A2. Showing a message

**Learn:** `print` shows a supplied value. Explain a function call, parentheses,
quoted text, and the difference between the argument name in `print(value)`
and the actual text supplied in a call. Start with one call.

**Evidence:** create a message from a stated goal and explain what will be
shown. Distinguish text inside quotes from the function name outside them.

#### A3. Executing lines in order

**Learn:** Python executes successive instructions from top to bottom. Trace
several known calls; comments and blank lines perform no actions. No variables
or control-flow constructs yet.

**Evidence:** predict and run an unfamiliar message sequence; repair an
announcement whose order is wrong; explain the output line by line.

#### A4. Numbers and calculations

**Learn:** a number differs from text containing digits. Introduce addition
and subtraction expressions and printing their calculated result.

**Evidence:** select calculations for a small shopping or sharing problem,
and explain the difference between printing text and calculating a value.
Use only familiar arithmetic.

#### A5. Grouping a calculation

**Learn:** parentheses group part of a calculation. Trace the grouped result
before the surrounding addition or subtraction; distinguish grouping from
the parentheses around function arguments.

**Evidence:** compare two expressions and explain why grouping changes the
result. Translate a small two-step problem without receiving answer lines.

#### A6. Giving a value a name

**Learn:** assignment associates a name with a value; reading that name uses
its current value. Explain `=` and sensible names with name-to-value diagrams.

**Evidence:** use a named value in more than one known calculation and explain
each lookup. Do not confuse the name, its quoted spelling, and its value.

#### A7. Replacing a stored value

**Learn:** reassignment gives an existing name a new value. Trace the state
before and after the assignment and show that earlier output stays unchanged.

**Evidence:** predict a sequence with two assignments and outputs; diagnose
changing the wrong name. This practises replacement, not arithmetic updates.

#### A8. Updating from the previous value

**Learn:** compute the right-hand side using the old value, then store the new
value. Use ordinary assignment, not unexplained abbreviated update syntax.

**Evidence:** track a wallet or score through gains and losses; choose updates
for a changed scenario and explain every intermediate value.

#### A9. Defining and calling a function

**Learn:** give a known sequence of actions a name with `def`. Explain its
colon, four-space body indentation, and definition versus execution. Begin
with a function that takes no arguments.

**Evidence:** explain why definition alone produces no output; trace calls
before and after ordinary statements; package a useful repeated sequence.

#### A10. Giving inputs to a function

**Learn:** parameters name values supplied by a caller. First map one argument
to one parameter, then explain several arguments in order in a separate short
article. Trace each call's local names; they are not shared stored state.

**Evidence:** trace calls with different inputs and diagnose swapped arguments.
Implement a reusable small calculation or message operation without hardcoded
inputs. Check parameterized tasks with varied arguments in the subprocess.

#### A11. Returning a result

**Learn:** `return` gives a value back to the caller and ends that call. Store
or use that result; contrast returning with printing and explain local names
versus names in the calling code.

**Evidence:** implement a small calculator whose result another calculation
uses; explain why printing a number is not the same as returning it.

#### A12. Using functions independently

**Learn:** consolidation only: choose a function's inputs and result, call it
more than once, and use its results with known operations. No new syntax.

**Evidence:** solve a changed everyday calculation with a reusable function;
explain its contract and two unfamiliar calls. A passing known example alone
is not enough.

#### A13. Comparisons and truth values

**Learn:** comparisons produce `True` or `False`, not an instruction to choose
a branch. Introduce equality and the ordered comparisons needed by the tasks;
distinguish `==` from assignment. Practise before adding branches.

**Evidence:** evaluate capacity or price rules at, below, and above a boundary;
return the comparison result from a function and explain each outcome.

#### A14. Choosing between two actions

**Learn:** `if`/`else` selects one of two bodies using a known truth value.
Trace the condition, the selected block, and what executes afterwards.

**Evidence:** implement a simple admission or price decision and repair a
wrong branch. Explain both cases, including a value exactly on the boundary.

#### A15. Requiring two conditions

**Learn:** `and` requires both known conditions to be true. Evaluate each
condition before combining them; do not add `or` or other new constructions.

**Evidence:** implement a rule with two independent requirements and test
both satisfied, either one missing, and both missing.

#### A16. Reversing a condition

**Learn:** `not` reverses a truth value. Connect the syntax to an ordinary
negative rule rather than teaching it as punctuation to memorize.

**Evidence:** choose and explain a condition for an opposite case; diagnose
an unnecessary negation. Combine with established branches, not new syntax.

#### A17. Keeping related values in a list

**Learn:** why a collection is useful, list literals, commas, and ordered
elements. Use numbers or words; no coordinate pairs, indexing, or mutation yet.

**Evidence:** choose a collection for a stated problem, construct it, and
explain its contents and order. Print the collection to inspect the result.

#### A18. Counting the list's elements

**Learn:** `len` returns the number of elements, including zero for an empty
list. Distinguish the collection from its length.

**Evidence:** answer a collection-size or remaining-capacity problem using a
returned count. Explain why length is not an element's value or position.

#### A19. Reading one list element

**Learn:** indexed access and zero-based indices versus human positions.
Explain the bracket syntax and which indices exist before requiring access.

**Evidence:** locate a clue from its described position, diagnose an off-by-one
choice, and explain the selected value. Do not silently require slicing.

#### A20. Checking whether an item is present

**Learn:** membership with `in` returns a truth value; presence is different
from length and position. Use `not` only through its established meaning.

**Evidence:** implement a permission or packing check with varied lists and
words, including an empty list and an absent item. This is not another indexed
lookup task.

#### A21. Acting on every list element

**Learn:** `for`, one iteration at a time, and the changing loop-variable value.
Explain the header's `in` as traversal, not the membership expression from A20.
Use the already established block indentation; begin with one repeated action.

**Evidence:** trace each step of an unfamiliar loop and construct a repeated
message or instruction sequence. Explain how an element reaches the body.

#### A22. Inside the loop and after it

**Learn:** consolidation of block boundaries: several actions in one iteration
versus an action after traversal. Trace indentation as execution, not merely
spacing; connect it to the previously taught function and branch blocks.

**Evidence:** diagnose an action repeated instead of executed once, repair its
placement, and explain the complete output sequence. No new loop construction.

#### A23. Accumulating a total

**Learn:** the running-total algorithm: start with zero and update the same
value for every element. Trace the accumulator and return only after traversal.

**Evidence:** total a small basket or distance list and explain intermediate
values, including an empty input. Choose the algorithm, not an example's names.

#### A24. Counting matching items

**Learn:** increment a count only when an element satisfies a known condition.
Distinguish the count from a sum and from the full collection length.

**Evidence:** count selected beads or values meeting a rule. Test all, some,
none, and empty inputs, and explain when the count changes.

#### A25. Searching for an item that satisfies a rule

**Learn:** scan until a matching item is found. A function may return success
inside the loop, but may conclude failure only after checking every item.
No `break`, `continue`, or new search built-ins are needed.

**Evidence:** detect whether a collection contains an item meeting a condition,
not just an exact value handled by membership. Diagnose a search that checks
only the first item; trace late-match and no-match inputs.

#### A26. Adding items to a list

**Learn:** `append` adds one element; it changes the list rather than returning
a replacement list. Explain the method-call syntax and an empty starting list.

**Evidence:** grow a collection from successive known values and inspect its
state after each addition. Explain why assigning the call's result is wrong.

#### A27. Removing an item safely

**Learn:** `remove` removes a matching value. Check membership before removing
an item that may be absent. Do not mutate the list being traversed.

**Evidence:** update a packing or inventory list, explaining present and absent
cases and the before/after state. Specify duplicate-value behavior before any
task needs it; do not introduce copying or aliasing implicitly.

#### A28. Building a filtered collection

**Learn:** combine known traversal, decisions, and `append` to build a separate
result list. Keep the original collection unchanged; no new syntax.

**Evidence:** retain items matching a rule, explaining empty, no-match, and
all-match inputs. The task must differ in reasoning from the counting and
search examples, not merely replace their names and values.

#### A29. Repeating until a goal

**Learn:** `while` checks its condition before every repetition. Change the
relevant state inside the loop; contrast this with traversing a known list.

**Evidence:** determine steps needed to reach or pass a target using familiar
addition or subtraction. Explain the condition before each repetition.

#### A30. Explaining why a loop finishes

**Learn:** consolidation of termination: identify the state change that makes
the condition false, including a condition false before the first repetition.
No new loop syntax.

**Evidence:** diagnose a non-terminating loop and an incorrect stopping point;
repair them and explain why the changes work for unfamiliar inputs.

#### A31. Planning and writing a small program

**Learn:** consolidation only: read a complete problem, choose data and known
tools, plan steps, implement them, test, and revise. Do not provide the plan as
answer code.

**Evidence:** independently implement a small budget checker using familiar
numbers and lists, then explain its decisions and test meaningful cases.

#### A32. Transferring the plan to another problem

**Learn:** independent application without new syntax. Select familiar tools
for a different problem instead of repeating A31 with another story.

**Evidence:** build a short robot-instruction analyser with a documented list
of known instruction words and an observable result; adapt it to a changed rule
and explain the steps. Do not introduce a new command language or parser.

**Readiness for the game:** the child can trace state, explain a function's
parameters and result, select branches, traverse or change a list, and justify
why a loop finishes. Repair gaps with different practice rather than repeating
the same answer.

### Section B — Build one-cell Battleship

Show the final game's behavior before starting its implementation. Now the
child applies established programming tools to genuine features. Each feature
may span several lessons, and game-specific concepts receive full explanations
before use. The cumulative game starts here.

#### B1. Boards and fixed fleets

Introduce the graphics-helper import and `show_board`; then explain the
coordinate system, one `(x, y)` address, and unpacking before `draw_deck`.
Practise unpacking one address before traversing a list of addresses; explain
direct unpacking in a `for` header separately before using that shorthand.
Introduce `show_ship_count` when displaying a fleet's remaining size.
Explicitly distinguish student-owned ship data from its graphical display.

**Milestone:** both boards are visible, a fixed player fleet is drawn, a fixed
enemy fleet exists but remains hidden, and counters reflect their lists.
**Understanding evidence:** translate between a marked cell and its address,
and explain why an enemy ship may exist without being visible.

#### B2. One player shot

Introduce `wait_for_cell` and its returned address, `show_miss`, and the sunk
deck state when needed. Use known membership and removal to resolve the shot.
For a one-cell ship, a hit sinks that ship immediately.

**Milestone:** one selected enemy cell produces the correct visible hit or miss
and remaining-fleet count.
**Understanding evidence:** trace both outcomes and distinguish changing game
data from drawing its result.

#### B3. A playable target hunt

Use known loops and lists to keep shooting until the enemy fleet is empty.
Introduce `show_message` before using dialogs for repeated-shot feedback or
completion. Record attempted cells and reject repeats without changing the fleet.
Explain an inner retry loop and its boundary before nesting it inside the
overall game loop; trace both exit conditions.

**Milestone:** the child can play a small target-hunt game against a fixed fleet.
**Understanding evidence:** explain the effects of a miss, a hit, and a repeated
cell, including why the winning loop stops.

#### B4. Add a computer opponent

Explain the random-number import, `randint`, its inclusive bounds, and forming
a random valid cell before computer shots. Combine two known shot-resolution
flows and check for the end of the game before giving the other side a turn.

**Milestone:** random computer shots, alternating turns, and victory/defeat with
fixed fleets. This is an intentionally simple computer; candidate filtering is
improved in B8, not presented as already finished.
**Understanding evidence:** trace a short battle and explain why the computer
must not take another turn after the player's winning shot.

#### B5. Interactive player fleet setup

Replace only the fixed player-fleet construction with clicks collected until
the required size is reached. Keep the existing battle code. Initially reject
occupied cells; complete neighbouring-cell validation in the next feature.

**Milestone:** the player places their own fleet, sees its counter grow, and
starts the existing battle through a dialog.
**Understanding evidence:** explain which code was replaced, which behavior
remains, and how invalid selections leave the fleet count unchanged.

#### B6. Valid placement

Start with pictures of overlap and horizontal, vertical, and diagonal
neighbours. Explain coordinate differences and `abs` as distance before the
no-touch calculation. Build a placement function using familiar search and
boolean-return patterns; state its valid input domain.

**Milestone:** every accepted ship is in bounds and neither overlaps nor touches
another ship. Input mechanics return valid board cells; the child owns the
fleet validation.
**Understanding evidence:** distinguish touching cells from cells one gap apart,
and explain why permission is returned only after all existing ships are checked.

#### B7. A hidden random enemy fleet

Reuse randomness, collection-building, and the placement function; reject bad
candidates and continue until the fleet is complete. Explain the shared
`BOARD_SIZE` value and the student-owned fleet-size setting before using them.

**Milestone:** both sides have 10 valid ships; enemy positions stay hidden and
the existing complete battle works with the generated fleet.
**Understanding evidence:** trace accepted and rejected candidates and explain
why a rejected position does not count toward fleet completion.

#### B8. Better computer selection

Separate random candidate generation from deciding whether it is useful. Reuse
shot history, lists of sunk player ships, neighbour reasoning, and a small
function. Add progressive hints only for genuinely difficult composition.

**Milestone:** computer shots do not repeat and avoid sunk ships and all their
neighbouring cells. Verify the final game through both victory and defeat.
**Understanding evidence:** justify allowed/rejected candidates and adapt the
selection rule without changing turn handling or drawing.

### Authoring and delivery boundary

No replacement lessons are implemented. This definition specifies learning
outcomes and prerequisite order, not ready-made articles, final task statements,
or executable metadata. Do not mistake the illustrative puzzles for authored
lessons or technical test fixtures for student content.

The next authoring step is only the first few foundation lessons. Pilot the
initial reading, message, and execution-order lessons before expanding through
calculations and variables. Establish exact prerequisites, examples, distinct
tasks, and understanding checks; use the child pilots to refine this planned
split before writing the whole course.
Restore executable metadata with fresh IDs once those lessons are ready.
Extend the runner for varied-input function tasks with the first such task,
inside the student subprocess, not as speculative work now.

Keep `reference/part_01_game.py` as a final-behavior baseline, not a prescribed
student solution. Map every syntax form, operation, helper, and game rule it uses
to an introduction and practice point; include teaching-only constructs in the
same review. Later implementation plans reference this path and define only
their concrete scope, completion criteria, and verification.
