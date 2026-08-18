# Course Home Roadmap

Completed phase: navigation and Phase A lesson-content implementation.

## Outcome

Replace the simple course introduction and lesson grid with a child-facing map
of the complete Part 1 game. The child can immediately see the final result,
their current position, the three course stages, and all 18 planned lessons
without gaining access to unimplemented or locked content.

## Scope

1. Add the agreed goal, promise, three stages, and 18 lesson titles to
   `CURRICULUM.yaml` as the runtime source of truth.
2. Extend `launcher/course.py` with validated roadmap stage and planned-lesson
   models. Implemented lesson IDs, titles, order, and stage membership must
   match their roadmap entries.
3. Derive current lesson number, current stage, completed-lesson count, and the
   next lesson from course metadata and existing progress. Do not persist
   expanded/collapsed presentation state.
4. Rebuild the pygame course home with the approved goal card, game route,
   progress card, three stage cards, primary continue action, and expandable
   full lesson list. Make expanded content scrollable.
5. Show **«Урок N из 18 · Этап K»** on lesson screens and a metadata-driven
   next-lesson preview on lesson summaries.
6. Keep future roadmap-only lessons visible but non-interactive. Debug mode
   unlocks all implemented content only.
7. Revise Lessons 2–7 with fuller first-use explanations, varied exercises that
   rise in difficulty, and explicitly incremental project tasks. Preserve the
   established concepts, APIs, lesson order, and game milestones. Do not add a
   child-facing explanation of lesson step types.

## UI constraints

- Use **«Этап»**, never **«Глава»**.
- Use pygame-drawn icons rather than emoji.
- Keep the theme switch and debug badge above the course-home scroll viewport;
  clip scrolling content below those fixed controls.
- Scroll to the full roadmap when it is expanded, keep the collapse control
  visible, and return to the top when it is collapsed.
- Use the same layout, icons, assets, and interaction logic in both themes;
  only palette constants may differ.
- Preserve the existing independent student progress and lesson-locking rules.
- Keep the launcher lesson-agnostic: titles, counts, stage membership, and
  preview text come from curriculum metadata.

## Verification

- Validate unique roadmap lesson IDs, continuous order, non-empty stages, and
  agreement between implemented lessons and roadmap entries.
- Cover initial, partially completed, and completed-lesson progress states.
- Cover expand/collapse, scrolling, implemented lesson access, future lesson
  blocking, and debug behavior.
- Run focused course/launcher tests, then the full suite.
- Visually inspect the course home and lesson header in both themes.

## Definition of done

- The course home matches the approved information hierarchy and wording.
- The child can see the final game, current lesson, current stage, and all 18
  lesson titles without opening a lesson.
- Existing progress files remain compatible and no new presentation-only state
  is saved.
- Phase A tasks are varied, rise in difficulty, and leave `battleship.py` with
  only cumulative game code.
- All focused and full tests pass, and both themes remain readable.

## Completion evidence

Completed on 2026-08-19 without activating Phase B.

- The YAML roadmap contains three stages and 18 continuously numbered lessons;
  the seven implemented lessons are validated as its prefix.
- The course home shows the agreed goal, route, progress, stage cards, and an
  expandable full plan. Future lessons remain non-interactive, including in
  debug mode; debug labels them as planned instead of displaying progress
  locks.
- Lesson headers show their total position and stage. Summaries preview the
  next roadmap lesson and its concrete game result.
- Lessons 2–7 now contain three required exercises with passing references;
  completion, correction, console, and game-output tasks rise toward the
  cumulative project milestone.
- Dark and light course homes, the expanded plan, and a Lesson 7 summary were
  inspected at 1180×760.
- Shell syntax checks, compilation, 72 focused tests, and the complete suite
  pass; the final debug-roadmap regression brings the complete suite to
  `128 passed`.
