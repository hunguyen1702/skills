---
name: secretary
description: Log the session's findings, decisions, and open questions turn by turn into <repo>/secretary/. Pass "off" to stop.
argument-hint: "[off | <log path>]"
---

# Secretary

Record the session while its full context is still in front of you. A summary written at the end drops the findings and rationale that whoever reads the log later needs, so log each turn as it happens. The session can be of any kind: planning a feature, debugging, researching options, or learning a concept.

`<secretary>` below means the folder containing this file. `<script>` means `python3 <secretary>/scripts/secretary.py`; run it from the repo root. The script records on/off per session in `secretary/status.json`, reading the session id from the agent's environment. While logging is on, a hook (on Pi, an extension) adds a reminder to every user message, so logging survives a long session.

## When the skill is loaded

**With `off`**: check the conversation for decisions, findings, or open questions not yet in the log and add them. Then run `<script> off` and tell the user the log path. Never delete the log, and add no summary or conclusion: the log records information, not verdicts.

**Otherwise**, run `<script> on` first, whether the user invoked the skill or another skill loaded it; without it no reminder fires on later turns. Then find the log to continue, in this order:

1. A log path passed as the argument.
2. A log path already in the conversation, such as one written in a handoff document.
3. `<script> list`: when one listed log clearly matches the session's topic, ask the user whether to continue it or start a new one.

Attach an existing log with `<script> attach --log <path>`, then read it before logging anything.

With no log to continue, judge whether the conversation already holds something to record. When it does, create the log with `<script> new --slug <slug> --title <title>`. The slug is a short English name for the topic; the title is in the conversation's language. When it does not, create nothing yet and wait for the next messages.

## Every turn while logging is on

Reply to the user first. Then update the log with what this turn settled: the user's message, your reply, and any question the user has not answered yet. Skip the update when the turn added nothing worth recording.

Record only what bears on the user's questions, problems, and decisions. Leave out what a model could infer again by reading the code or the repo. A session may have few or no decisions, as when debugging or learning; then the findings carry the log.

## Log template

`<script> new` creates the file from the block below; that block is the only copy of the template. Write the log in the language of the conversation and keep it to these sections:

```markdown
# Session Notes: {title}

## Objective

## Key Findings

## Decisions

## Open Questions

## References
```

- **Objective**: what the session is for: the feature to plan, the bug to fix, the question to answer, the topic to learn. Update it when the scope changes.
- **Key Findings**: verified facts the session established, from research, comparisons, explanations the user asked for, experiments, or hypotheses ruled out. One line each: the question the user asked or the problem that raised it, the finding, and its source.
- **Decisions**: what the user chose, such as a design, a fix, or a tool, each with its rationale. When a later decision replaces one, keep the old entry, mark it superseded by the new one, and give the reason for the change.
- **Open Questions**: what the user is still weighing or has not resolved yet, with the options on the table. Move an item to Decisions or Key Findings once it is settled.
- **References**: code paths, documents, URLs, and commit hashes the findings and decisions cite.

Keep comparison tables as tables. Edit the existing file in place; never rewrite it from memory, which loses entries.

## Handoff

When you write a handoff document while logging is on, add to it the log path and an instruction for the next session to trigger the secretary skill and continue that log.
