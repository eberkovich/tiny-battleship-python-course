# Progress tracker for A9¾ — Weasley shop capstone

Status format: [ ] - not processed, [X] - completed

## Execution stages

- [X] Stage 1: Record the approved contract.
- [X] Stage 2: Add metadata-driven presentation and capstone support.
- [X] Stage 3: Test the infrastructure independently of the capstone.
- [X] Stage 4: Author the project and publish its real assets.
- [X] Stage 5: Verify and hand off for the child pilot.

## Evidence and notes

- 2026-10-11: Approved purchase → receipt → payment → change scenario,
  required A9¾ completion before A10, and secret-title concealment before A9
  completion are recorded in both context documents and the implementation plan.
- Baseline: 383 tests passed in 18.70 seconds with dummy SDL video/audio.
- Existing changes to the context documents and plan belong to this task;
  preserve all student workspaces. No commit is authorized.
- Temporary artwork and screenshots are already covered by `.tmp/` and
  `screenshots/` in `.gitignore`; selected lesson assets are permanent deliverables.
- Stage 2: 67 launcher/input regressions and 268 workspace/pilot regressions
  passed. Chronological checks retain the legacy input checker and private output
  isolation. Illustrated content uses metadata, shared rendering, and palette
  constants; ordinary displayed ordinals do not count explicitly labelled entries.
- Stage 3: 94 focused tests passed, including synthetic secret-capstone
  progression, debug non-persistence, asset validation, clearing artwork, and
  chronological subprocess output with prompt exclusion.
- First authoring check: 294 capstone/input/pilot checks passed, including the
  complete checkout reference and untouched starter rejection. Further failure
  cases and visual review are in progress.
- Stage 4: The one-file checkout, complete starter description, private
  reference, three progressive hints, and ten selected original PNGs are
  published. The twins revision uses plain worn clothes and mischievous smiles;
  the glamorous first version is not shipped. The wheel build includes every
  selected image and the prompt/provenance document.
- Stage 5 evidence: the full suite passed 409 tests in 20.83 seconds. Both-theme
  production previews at 1180×760 and 1600×1000 cover introduction, catalogue,
  coins, task/summary, and roadmap; layout tests also cover revealed hints,
  output, and leaving the lesson. Native macOS startup passed. An automated
  native run started IDLE, supplied a different six-answer basket through the
  production controller, inspected the real receipt/change frames, and verified
  reopening the saved solution/completion. Physical keyboard entry and child
  mastery remain user-pilot checks, not claimed verification.
- Shell syntax, runtime/lesson compilation, and package build passed. The first
  native attempt inside the sandbox exited 134; the approved unsandboxed native
  check succeeded. An overly exact zero-alpha asset assertion was corrected to
  allow negligible soft-matte alpha, preserving the transparent-cutout contract.
- Final checkpoint after bounded resize-cache changes: 409 tests passed in
  21.17 seconds; `git diff --check` passed. Documentation and delivered behavior
  agree, and the active phase is cleared. No commits or existing student-workspace
  changes were made. The next step is a child trial of independent explanation
  and a different basket, not further lesson implementation without approval.
- 2026-10-11: Approved background-visibility refinement separates explanatory
  paragraphs into opaque cards and places illustration rows directly over the
  artwork, with compact caption/equality backings and unchanged parchment price
  tags. A structural regression verifies that prose cards do not cover the art.
  Both themes were visually inspected at 1180×760 and 1600×1000; existing
  fixed-control and scroll-bound checks pass. Focused tests: 313 passed. Full
  suite: 410 passed in 21.44 seconds. No lesson wording, student work, or commits
  changed in this refinement.
- Change-output clarification: separate the coin-selection rule from display
  instructions and show a labelled formatting-only output sample. The lesson,
  starter description, and reference agree on visually separated coin labels
  and quantities; varied-input acceptance remains unchanged. Full suite:
  410 passed in 21.53 seconds.
- Numeric-output simplification supersedes required receipt/change labels:
  three quantity/subtotal rows plus one Sickles-total row, then one row of
  Galleon/Sickle/Knut change counts. The specification, starter, reference,
  checker, and source-of-truth documents now agree. Optional labels with typos,
  extra spaces/separators, and printed questions containing prices pass;
  incorrect values, row/field order, zero omissions, and timing still fail.
  Both-theme production previews at both supported review sizes were inspected.
  Focused capstone checks: 27 passed. Full suite: 416 passed in 22.52 seconds.
  No public API, saved student source, or commits changed.
- Secret-number concealment: hide the custom label in locked roadmap rows,
  stage ranges, and next-lesson previews; reveal it with the lesson after A9
  completion. Debug review remains revealed. Both-theme production previews
  at 1180×760 and 1600×1000 were inspected. Focused launcher/capstone checks:
  66 passed. Full suite: 417 passed in 22.06 seconds. No student work or commits
  changed.
