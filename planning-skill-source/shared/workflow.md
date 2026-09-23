# Adaptive planning workflow

Use this workflow to turn a requirement into planning documents. Planning ends
when the documents are delivered; do not start implementation implicitly.

## 1. Establish the request

Read the requirement, conversation, and only the local sources the user
explicitly supplied or authorized. A path supplied for reading does not grant
write permission.

Summarize the interpretation as:

- **Context:** the situation and relevant source material.
- **Task:** the outcome to plan.
- **Format:** the proposed route, artifacts, and output location.

Ask one focused question at a time only when an answer could materially change
observable scope, behavior, architecture, or output. When credible choices
exist, explain the trade-off briefly and recommend a default. Do not ask the
user to decide facts that bounded inspection can establish.

## 2. Route and confirm

Read [routing.md](routing.md), classify the requirement, and explain the
decisive reason. The route can change after clarification. When it does,
explain why and present the revised Context–Task–Format interpretation.

Before creating any artifact, present all of the following:

- the chosen route and reason;
- the exact intended artifacts;
- the absolute output directory;
- any decisions or assumptions that will appear as settled facts.

Wait for explicit user confirmation. Silence, confidence, elapsed time, or an
earlier approval of a materially different route is not confirmation. Reading
and analysis may precede this gate; document creation may not.

## 3. Create safely

Unless the user explicitly requests a destination, create a fresh workspace
with `mktemp -d` under `/tmp`. Never guess or reuse a fixed temporary path.
Do not write to an inspected repository by default. If the user explicitly
requests repository output, first read the applicable local instructions and
preserve unrelated changes.

Create only the documents required by the confirmed route, following
[document-formats.md](document-formats.md). Use neutral identifiers derived
from the requirement, not identifiers copied from unrelated source material.

## 4. Review

After each confirmed material decision, prefer an independent reviewer when
delegation is available, appropriate, and authorized. Give the reviewer the
requirement and draft, not the intended verdict. Review:

- direction clarity and testability;
- functional and non-functional acceptance coverage;
- verification quality and references;
- artifact completeness and links.

Continue interviewing only for a meaningful blocker. If independent review is
unavailable, perform the same checklist as a structured self-review and state
that limitation in the delivery.

Before delivery, verify:

- the route matches the artifact set;
- documents do not contradict each other;
- unconfirmed choices are not presented as decisions;
- paired documents link to each other;
- epic decomposition does not fully plan future units;
- direct story planning includes both required documents;
- no unrelated repository-specific names, paths, commands, concepts, or IDs
  leaked into the output;
- no repository was accidentally mutated.

## 5. Deliver

Report the absolute path of every artifact and summarize the review performed.
For epic decomposition, highlight the task-board path separately. Stop after
delivery unless the user explicitly requests another planning or implementation
action.
