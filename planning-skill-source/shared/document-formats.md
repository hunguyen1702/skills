# Document formats

Use relevant sections only. Do not invent commands, persistence, error,
concurrency, or actor concerns that the requirement does not support.

## Epic document

Start with YAML frontmatter containing a neutral `id`, `kind: epic`, and
`planning_state`. Include:

- Outcome
- Problem and context
- Users or actors, when relevant
- Scope
- Out of scope
- Confirmed product and solution decisions
- Cross-cutting constraints and invariants
- Future-planning units
- Success criteria
- Open questions, only when explicitly deferred
- Task-board link

Describe the product or engineering contract, not line-by-line implementation.
Each future-planning unit contains only ID, title, outcome, and scope summary.

## Task board

Use a short legend and exactly this Markdown table:

| ID | Planning unit | Outcome | Planning | Document | Notes |
|---|---|---|---|---|---|

`Planning` is only `needed` or `planned`; new units are normally `needed`.
Leave `Document` empty until the unit has its own plan. Do not add claim, owner,
dependency readiness, implementation status, or execution status. This is a
future-planning index, not a work-claim mechanism.

## Story contract

Start with YAML frontmatter containing a neutral `id`, `kind: story`, and
`planning_state`. Include:

- Outcome
- User story or operator story
- Scope
- Out of scope
- Confirmed product and solution decisions
- Observable behavior and interfaces
- Functional acceptance criteria
- Non-functional acceptance criteria
- Verification approach
- Implementation-task link

## Implementation-task requirement

Start with YAML frontmatter containing a neutral `id`,
`kind: implementation-task`, and `planning_state`. Include:

- Parent story
- Objective
- Deliverables
- Proposed structure, only when evidence supports it
- Technical choices and boundaries
- Implementation flow at coding-agent granularity
- Output and error contract, when applicable
- Test plan
- Verification commands or checks
- Definition of done
- References

Make it actionable without prescribing a line-by-line patch or cataloging every
rare edge case. Link it back to the parent story; the story links to this task.
