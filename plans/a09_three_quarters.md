# A9¾ — Weasley shop capstone

Status: completed; ready for the child pilot.

Implementation and verification completed on 2026-10-11. All five stages are
recorded in the tracker, including the artwork, required secret navigation,
complete interactive checkout, both-theme review, and native macOS evidence.

Definition of done: all five stages below are verified, the reference passes
the student's checker, existing lessons regress cleanly, the full suite passes,
and headless versus native macOS verification evidence is recorded separately.
Progress is recorded in `a09_three_quarters-track.md`.

## Task and scope

Create the agreed standalone shop-calculator project after A9 and before A10.
Adapt Code Avengers Python 1, sections 7.3–7.4, using the task and light Weasley
opening already recorded in `context/lesson_content.md`. Expand its two-product
checkout to three products; omit discounts and introduce no new Python concepts.
Extend the same program in two parts: calculate the basket and receipt first,
then accept payment and calculate change. The payment/change extension is our
adaptation, not a requirement attributed to the source worksheet.

The child writes one independent program for **«Всевозможные волшебные
вредилки»**. A customer enters three purchase quantities, sees the item costs
and total, then enters payment and receives change. These are consecutive parts
of one checkout use case, not separate programs. Use fictional whole-number prices:

- **«Удлинители ушей»**: 17 Sickles per item.
- **«Забастовочные завтраки»**: 23 Sickles per box.
- **«Карликовые пушистики»**: 31 Sickles per creature.

Inputs are whole quantities from 0 through 100, first for Extendable Ears, then
for Skiving Snackboxes, then for Pygmy Puffs. The numeric receipt contains three
rows of quantity and subtotal in Sickles in catalogue order, including zero
purchases, then one row containing only the total in Sickles. Print change as
three numbers on one row: Galleons, Sickles, Knuts, including zero counts.
Product/currency names and other labels are optional; do not assess their
spelling or decorative punctuation. Retain numeric values, row/field order,
and output timing as the meaningful checking contract.
Show the basket receipt before asking for payment. After that, request three
nonnegative whole coin quantities in order: Galleons, Sickles, then Knuts.
Calculate change in the same denominations, with the largest possible number
of Galleons, then Sickles, and the remaining Knuts. Show the change only after
payment has been entered. State the output contract clearly without supplying
the calculation strategy or completed code. Keep the receipt and change compact
enough to remain readable in the existing output card.

Pygmy Puffs are confirmed in the official shop description:
https://www.harrypotter.com/fact-file/locations/weasleys-wizard-wheezes

Before the payment/change part, explain the wizarding denominations with an
illustrated reminder: one gold Galleon equals 17 silver Sickles; one silver
Sickle equals 29 bronze Knuts. Introduce these domain facts and the necessary
conversion before asking the child to use them. Payment is guaranteed to cover
the basket; do not introduce insufficient-payment handling.
The official currency source is:
https://www.harrypotter.com/fact-file/objects/wizarding-money

Use only comments, assignment, known arithmetic, `input()`, `int`, and `print`
with already-taught arguments. The child chooses names and implementation
steps. Do not add functions, loops, conditions, lists, string formatting,
modulo, stock management, or input validation. Currency calculations must use
only the arithmetic already taught. No Battleship file
or public graphics API changes are required.

One complete coding task is required to finish this capstone. Do not add
repetitive preliminary exercises or a second star task to meet the normal
lesson activity count. Include at most three progressive optional hints and
only prerequisite recaps genuinely needed here.

## Visual direction

Use a playful illustrated **Diagon Alley** background with the Weasley shop
visible, warm shop windows, and a quiet central area. Confine it to the lesson
content region; retain the ordinary sidebar and fixed toolbar. Put explanatory
paragraphs on separate opaque cards and illustration rows directly over the
artwork. Use compact solid backings behind captions and relationship labels,
retaining parchment price tags, so text contrast stays clear without hiding
the background. Keep the same artwork, layout, and behavior in dark and light themes;
any contrast treatment uses named palette constants only.

The opening includes a small original sketch of the red-haired Weasley twins
and a restrained **9¾** plaque. The task shows three illustrated product cards
with parchment-scroll price tags. Draw product names, prices, and the plaque
number with application fonts, not as generated lettering inside images.
Keep the catalogue visible in the task description, ahead of the specification;
it scrolls normally rather than competing with the fixed note and output.

Place a compact coin-equivalence diagram before the payment/change task. Use large,
distinct gold, silver, and bronze coin illustrations with two clearly labelled
relationships: 1 Galleon = 17 Sickles; 1 Sickle = 29 Knuts. Render all names,
numbers, and relationship symbols with application fonts, not inside generated
artwork. Do not crowd the diagram with 17 or 29 individual coin pictures. Reuse
the same coin assets and diagram layout in both themes.

Generate original, static storybook-style artwork, not screenshots from films
or scans of books. Store only final assets in the lesson; previews and rejected
generations stay in ignored temporary folders. Do not introduce animation, a
new theme, a separate shop application, or an automatically fabricated receipt.
The displayed receipt must remain the child's real printed output.

## Agreed navigation

Treat A9¾ as a required standalone capstone unlocked by completing A9. Its
summary requires a passing complete checkout program, and A10 remains locked
until A9¾ is completed. Preserve labels A1–A33 and display this lesson as **9¾**
only after it is revealed.
Include it in completion totals: 33 numbered foundation lessons plus this
capstone make 34 required lessons when its roadmap entry is published.

Before A9 is completed, show its roadmap entry as **«Секретный урок»** with a
lock and an empty number gutter. Hide its 9¾ label, actual title, outcome, and
shop artwork on every locked preview, including stage ranges and next-lesson
previews. After A9 is completed, reveal its label, real title, and outcome and allow access when
the lesson is implemented. Debug mode reveals and unlocks every implemented
lesson as usual; a roadmap-only entry remains non-executable. Keep existing
lesson/task IDs and saved student work intact.

## Implementation plan

### 1. Record the approved contract

- Update `context/lesson_content.md` with the capstone's outcome, input domain,
  receipt requirements, prerequisites, and source adaptation. Retain the
  approved opening and make its independence from A8/A9 explicit.
- Update `context/architecture.md` with required secret-capstone navigation and the
  opt-in lesson-background/illustration capability. Replace the small-accent
  wording only to the extent approved here; preserve shared-theme and layout
  invariants. Distinguish this independent project from cumulative game tasks.
- Use runtime ID `a09_bonus`, child-facing title **«Касса для братьев Уизли»**,
  and coding task ID `a09_bonus_checkout`. Preserve all other IDs.

Files: both context documents and this plan.

Verification: review the contract against A1–A9 and the documented source;
check that every required operation has already been introduced and that the
purchase/payment/change sequence matches the agreed scenario.

### 2. Add bounded, metadata-driven presentation and capstone support

- In `launcher/course.py`, add optional `display_label` and `locked_title`
  fields to `RoadmapLesson`, plus `Course.lesson_label`. Retain roadmap position
  for ordering and normal immediate-predecessor access. An explicitly labelled
  entry does not consume a regular displayed ordinal; entries without one retain
  sequential numbering. Every entry still counts toward total progress.
- Add optional lesson presentation paths for background, plaque, and caption
  parchment, plus optional task illustrations with an image path and text
  caption. Resolve assets under the project root, validate their existence,
  and reject paths escaping it. No lesson-ID-specific rendering branches.
- In `launcher/controller.py`, expose displayed lesson labels and shared
  access-aware roadmap titles/outcomes. Use `locked_title` and omit the outcome
  while its prerequisite is unmet; debug mode reveals implemented entries.
  Keep sequential unlocking and completion totals, with no capstone bypass.
- In `launcher/app.py`, draw the background before content, cache loaded
  images, and aspect-fit illustrations. Render three product illustrations
  side by side with wrapped captions and a single introduction sketch at a
  modest size. Render
  their captions over the blank parchment asset using readable font colors.
- Use displayed labels everywhere a lesson number appears, including home,
  sidebar, stage ranges, and next-lesson previews. Widen the roadmap label
  gutter for 9¾; keep every row inside the single lessons card.
- Keep the existing editor, input dialogs, result card, note, and task icons.
  Clear lesson artwork on returning home or opening a lesson without it.
- In `runner/child.py`, extend `_check_input_cases` with an optional private
  acceptance hook `check_interaction(task_id, answers, output_segments)`.
  Capture printed output before each input request and after the final answer,
  excluding each `input` prompt argument from its segment. Preserve exact read
  counts and the existing `check_inputs` path for older tasks. This hook checks
  the receipt before payment and change afterward, without comparing question
  wording or exposing private case output to the child.

Files: `launcher/course.py`, `launcher/controller.py`, `launcher/app.py`, and
`launcher/theme.py` for any required named palette constants; `runner/child.py`
for chronological interactive checking.

Existing examples: course metadata loading, `_render_lesson_content`,
`_render_full_roadmap`, the cached submarine asset, and interactive task runs.

Verification:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest -q tests/test_launcher.py tests/test_workspace.py tests/test_foundation_pilot.py tests/test_console_input.py
```

### 3. Test the new infrastructure independently of the capstone

- Add `tests/test_capstone.py` cases with a small synthetic capstone/illustration
  fixture. Verify labels, inclusion in totals, secret title/outcome concealment
  before prerequisite completion, reveal afterward, A10 locking until capstone
  completion, summary locking, and debug-mode reveal/non-persistence.
- Check legacy metadata defaults, invalid assets, proportional image fitting,
  and leaving the illustrated lesson. Assert layout bounds, not exact pixels.
- Test shared behavior once; do not duplicate logic tests by palette.
- In `tests/test_console_input.py`, verify output-segment order, prompt exclusion,
  exact read counts, legacy-check compatibility, and that private output never
  replaces the child's actual run.

Files: `tests/test_capstone.py` and `tests/test_console_input.py`; reuse existing
controller and layout test style.

Verification:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest -q tests/test_capstone.py tests/test_launcher.py tests/test_workspace.py tests/test_console_input.py
```

### 4. Author the project and publish its real assets

- Create `lessons/a09_bonus/assets/diagon_alley.png`, `twins.png`,
  `extendable_ears.png`, `skiving_snackboxes.png`, `pygmy_puff.png`,
  `price_scroll.png`, `platform_plaque.png`, `galleon.png`, `sickle.png`, and
  `knut.png`. Generate and inspect the artwork before integration; parchment,
  plaque, and coins contain no instructional lettering. The renderer draws
  their captions and the coin-equivalence diagram.
- Create `lessons/a09_bonus/lesson.md`: a short story/purpose opening, the
  independent checkout specification with catalogue, the coin reminder and
  payment/change extension, and a truthful summary.
  Use the established fixed workflow note. Do not provide a worked checkout
  example or a line-by-line recipe before the task.
- Create `exercises/checkout.py` containing the complete task specification
  as Russian comments and room for the child's program. Create a private
  `reference/checkout.py` using only the permitted concepts.
- Create `acceptance.py` with source/adaptation attribution, `input_cases`,
  and `check_interaction`. Cover all three nonzero, each product alone, mixed
  zero quantities, all zero, asymmetric quantities, larger purchases, exact
  payment, mixed payment coins, and change crossing denomination boundaries.
  Verify receipt fields before the first payment input and correct change after
  the final payment input, accepting harmless whitespace and equivalent code.
- Register the required capstone and its presentation in `CURRICULUM.yaml` after
  `a09_input`, using one `exercise` task with `run_mode: interactive` and an
  independent student file at `exercises/a09_bonus/checkout.py`. Require that
  task for this lesson's summary; do not turn it into a Battleship milestone.
- Include final lesson artwork in package data in `pyproject.toml`. Keep
  temporary asset work in `.tmp/` and verification images in `screenshots/`;
  confirm `.gitignore` still covers everything generated locally.

Files: the new lesson directory, `CURRICULUM.yaml`, `pyproject.toml`, and
`.gitignore` only if a new temporary-file category is introduced.

Verification: execute the private reference through `runner.process.run_check`
with lesson ID `a09_bonus` and task ID `a09_bonus_checkout`; confirm the empty
starter fails. Compare every displayed price with the checker and reference.

### 5. Verify the authored project and hand off for the child pilot

- Extend `tests/test_capstone.py` with real varied-input acceptance, meaningful
  incorrect receipts, hardcoded-answer rejection, interactive output retention,
  bonus completion persistence, and non-overlap at the supported window sizes.
- Update the scope assertions in `tests/test_foundation_pilot.py` to distinguish
  nine numbered authored lessons plus one required capstone from the 34-entry
  foundation roadmap, while preserving regular labels A1–A33.
  Reuse its parameterized reference, starter, and content validators.
- Inspect the production renderer in both themes at 1180×760 and 1600×1000:
  introduction, catalogue/task, coin reminder, hints, input dialog, receipt and
  change, summary, secret and revealed roadmap states, and return home. Verify
  no toolbar, note, output, or row overlaps.
- Perform a native macOS run through the normal launcher: open the actual
  editor, enter different quantities, see the child's actual receipt, and
  reopen saved work. Report native verification separately from headless tests.
- Update `README.md` and the context documents with the actual delivered state
  and verification evidence. Ask whether the child can explain which stored
  values are reused and handle a different basket without receiving code.
  Do not call a passing checker proof of understanding.

Files: `tests/test_capstone.py`, `tests/test_foundation_pilot.py`, `README.md`,
the context documents, and this plan's completion status.

Verification:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest -q tests/test_capstone.py tests/test_console_input.py tests/test_foundation_pilot.py
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy .venv/bin/python -m pytest -q
git -C /Users/eberkovich/projects/tutorial diff --check
```

Do not implement further lessons or commit changes without explicit approval.
