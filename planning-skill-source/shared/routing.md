# Routing

Classify from the current facts, and reclassify whenever clarification changes
them. Use the smallest route that credibly represents the work.

## Route A: epic decomposition

Choose Route A when any one of these is materially true:

- there are multiple independently deliverable outcomes;
- multiple subsystems or distinct user journeys are involved;
- a major architectural or product decision remains unresolved;
- implementation and verification cannot credibly fit one working session as
  one cohesive task.

Create exactly:

1. one epic document; and
2. one task-board document.

Represent future planning units only by ID, title, outcome, and scope summary.
Do not create detailed story contracts or implementation tasks for them unless
the user later asks to plan a specific unit.

## Route B: direct story planning

Choose Route B only when all of these are true:

- the requirement has one observable outcome;
- the affected scope is bounded;
- no independently schedulable decomposition is needed;
- implementation and verification can credibly fit one working session.

Create exactly:

1. one story contract; and
2. one implementation-task requirement.

## Rerouting

Clarification can narrow Route A to Route B or reveal that Route B must become
Route A. Explain the changed fact and its routing consequence. Because the
artifact set changed, repeat Context–Task–Format confirmation and wait for new
explicit approval before writing.
