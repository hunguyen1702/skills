# Interview and confirmation

## Material ambiguity

Interview only about choices that affect observable scope, behavior,
architecture, or deliverables. Prefer one focused question that names the
decision and its consequence. Group tightly coupled choices only when answering
them together is easier than answering separately.

When two or more approaches are credible:

1. state the relevant trade-off in plain language;
2. recommend one default and explain why it best fits known constraints;
3. let the user accept it or choose another direction.

Treat explicitly deferred questions as open questions in the documents. Do not
silently convert a recommendation, assumption, or observation into a confirmed
decision.

## Confirmation gate

Use this compact shape before document generation:

```text
Context: <interpreted situation and confirmed decisions>
Task: <planning outcome and chosen route>
Format: <exact artifacts and absolute output directory>
```

Then ask for explicit confirmation. A response clearly accepting that proposal
opens the gate. A correction closes it: update the interpretation, reroute if
needed, and ask again. If the user already explicitly requested a particular
route, artifact set, and destination, still show the interpretation, but do not
re-ask questions whose answers are already supplied.

Confirmation authorizes only the listed planning artifacts at the listed
destination. It does not authorize implementation, repository mutation at a
different path, task claiming, lifecycle changes, or acceptance execution.
