# AGENTS.md

## Purpose and sources of truth

Build a small, systematic Python course around one cumulative Tiny Battleship
game. Optimize for educational clarity, short feedback loops, algorithmic
thinking, and a prototype usable by the user's children—not a generic
education platform.

This file is the operating manual for agents. It defines how to work in the
repository, not the detailed product design:

- `context/architecture.md` is the source of truth for settled product,
  curriculum, and technical decisions;
- `plans/README.md` and its current stage file define the active scope and
  completion criteria;
- `COURSE_DESIGN.md` and `CURRICULUM.yaml`, when present, contain supporting
  course rationale and lesson metadata; they must conform to the architecture.

Read the relevant documents before architectural, curriculum, or implementation
work. Do not silently change a settled decision or expand the active stage.

Any proposed deviation from this file, `context/architecture.md`, or the active
stage plan must be explicitly discussed with and approved by the user before it
is implemented. Update every affected document in the same change so the
documented decisions and the implementation never knowingly diverge.

## Cross-task guardrails

- Keep student code procedural/structured Python. Do not introduce
  student-facing OOP, callbacks, or framework-defined holes.
- Keep game state, decisions, algorithms, and control flow in student code.
- Keep the public UI small and procedural; internal implementation may use OOP.
- Keep the launcher lesson-agnostic and V1 small.
- Write all child-facing lesson text, launcher labels, hints, and check feedback
  in Russian. Keep code identifiers and developer documentation in English.
- Prefer the smallest working implementation. Do not add infrastructure for a
  hypothetical future need.

## Implementation workflow

Before changing files:

1. Read the architecture and active stage.
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

For every implementation change:

1. Add or update the smallest relevant test.
2. Run focused tests and current-lesson acceptance checks.
3. Run applicable earlier-lesson regressions and then the full suite.
4. Update concise documentation when behavior, public APIs, file layout, or
   commands change.

When the student-facing UI API changes, update its real and fake implementations
and their tests together. Prefer black-box behavioral checks and semantic events
over pixel or exact-source assertions. Run arbitrary student code only in a
subprocess; never import it into the launcher process.

Do not weaken a test merely to make an implementation pass. If a test reflects
an outdated decision, explain the mismatch before changing it. Whenever a
dependency, dependency version, or supported Python version changes, update
`install.command` and its tests in the same change.

## Lesson work

When creating or changing a lesson:

1. Inspect previous lessons and preserve their structure and tone.
2. Use previously introduced concepts plus at most the specified new concept.
3. Make exercises require thought rather than direct copying.
4. Ensure the cumulative game milestone genuinely needs the new concept.
5. Add behavioral checks and an optional **«Задача со звёздочкой»**.
6. Review all child-facing material for Russian-only presentation, age
   appropriateness, excess text, and long gaps between interactions.

Do not independently reorder the curriculum or introduce extra major concepts
for implementation convenience.

## Completion review

Before finishing, check that the change:

- preserves the ownership and API boundaries in the architecture;
- gives the child visible feedback within a few minutes;
- advances the cumulative game when the task is a project milestone;
- remains behaviorally verifiable;
- adds no out-of-scope infrastructure;
- passes all relevant tests.

Keep `plans/README.md` status accurate. Mark a stage complete only after its
definition of done has been verified and completion evidence recorded.
