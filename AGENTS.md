# AGENTS.md

## Purpose and sources of truth

Build a small, systematic Python course around one cumulative Tiny Battleship
game. Optimize for educational clarity, short feedback loops, algorithmic
thinking, and a prototype usable by the user's children—not a generic
education platform.

This file is the operating manual for agents. It defines how to work in the
repository, not the detailed product design:

- `context/architecture.md` is the source of truth for settled product and
  technical decisions;
- `context/lesson_content.md` is the source of truth for lesson-authoring rules;
- a plan with an explicit `Current phase:` marker defines the active scope and
  completion criteria; completed `plans/stage_NN_*.md` files are historical
  stage records;
- `COURSE_DESIGN.md` and `CURRICULUM.yaml`, when present, contain supporting
  course rationale and lesson metadata; they must conform to both context
  documents.

Read the relevant documents before architectural, curriculum, or implementation
work. Do not silently change a settled decision or expand the active phase.
Only one plan may contain an active `Current phase:` marker. Keep completed
stage files frozen as historical records. Clear or advance the marker only
after the current phase's definition of done and verification evidence are
recorded. Do not create a separate stage file when an existing plan already
defines the requested phase precisely.

Any proposed deviation from this file, `context/architecture.md`,
`context/lesson_content.md`, or the active plan phase must be explicitly
discussed with and approved by the user before it is implemented. Update every
affected document in the same change so the documented decisions and the
implementation never knowingly diverge.

Claims added to `context/architecture.md` must preserve the project's logical
invariants. Do not document an impossible or invalid state as normal behavior;
check each claim against the relevant state and domain invariants first.

## Cross-task guardrails

- Keep student code procedural/structured Python. Do not introduce
  student-facing OOP, callbacks, or framework-defined holes.
- Keep game state, decisions, algorithms, and control flow in student code.
- Keep the public UI small and procedural; internal implementation may use OOP.
- Keep the launcher lesson-agnostic and V1 small.
- Follow `context/lesson_content.md` for all child-facing content.
- Prefer the smallest working implementation. Do not add infrastructure for a
  hypothetical future need.

## Implementation workflow

Before changing files:

1. Read the architecture and active plan phase.
2. Inspect existing related code, lessons, and tests.
3. Check the working tree when version-control metadata is available and
   preserve unrelated work.
4. Run existing regressions and earlier-stage acceptance tests when applicable.

At every stage, update `.gitignore` in the same change whenever the stage
creates or is expected to create new temporary, generated, machine-local, or
student-local files. Never commit temporary files, caches, local environments,
generated test output, or mutable student workspaces.

Never create a Git commit without explicit user approval. Approval to edit,
implement, test, or stage changes is not approval to commit them.
Every approved commit must use a concise, meaningful message that describes
the actual change; do not use generic messages such as `update`, `changes`, or
`work in progress`.

For every implementation change:

1. Add or update the smallest relevant test.
2. Run focused tests and current-lesson acceptance checks.
3. Run earlier-lesson regressions affected by the change.
4. Run the full suite at each phase checkpoint and before phase or stage
   completion or handoff, not after every small content or implementation edit.
5. Update concise documentation when behavior, public APIs, file layout, or
   commands change.

For every layout change, verify that ordinary UI regions do not overlap each
other or render beneath fixed controls at the supported window size. Intentional
modal overlays are the only exception.

When the student-facing UI API changes, review the complete API for consistent
naming, verb meaning, argument order, defaults, abstraction level, and
terminology. Update every affected real and fake implementation, export,
lesson, check, test, architecture decision, and active-stage requirement in the
same change. Prefer black-box behavioral checks and semantic events over pixel
or exact-source assertions. Prefer shared structural validators and
parameterized reference cases over one bespoke test per lesson or task. Assert
exact prose only when wording or order encodes a prerequisite or another
settled teaching contract. Run arbitrary student code only in a subprocess;
never import it into the launcher process.

Do not weaken a test merely to make an implementation pass. If a test reflects
an outdated decision, explain the mismatch before changing it. Whenever a
dependency, dependency version, or supported Python version changes, update
`install.command` and its tests in the same change.

## Lesson work

When creating or changing a lesson:

1. Read `context/lesson_content.md`, the architecture, and the active plan.
2. Inspect previous lessons and preserve their established structure and tone.
3. Keep the curriculum order and ensure the cumulative milestone needs the
   lesson's new concept.
4. Validate every coding task with a passing reference solution through the
   same behavioral checker used for student code.
5. Run focused lesson checks and applicable regressions. Run the full suite at
   the phase checkpoint or before handoff.

Do not independently reorder the curriculum or introduce extra major concepts
for implementation convenience.

## Completion review

Before finishing, check that the change:

- preserves the ownership and API boundaries in the architecture;
- gives the child visible feedback within a few minutes;
- advances the cumulative game when the task is a project milestone;
- remains behaviorally verifiable;
- gives an unambiguous definition of success backed by a verified solution;
- adds no out-of-scope infrastructure;
- passes all relevant tests.

Keep the active plan phase status accurate. Mark it complete only after its
definition of done has been verified and completion evidence recorded.
