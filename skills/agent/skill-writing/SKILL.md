---
name: skill-writing
description: Rules for writing the text of an agent skill (its description, SKILL.md body, and references) so it runs predictably on Claude Code, Codex, and Pi. Use when drafting, editing, or reviewing a skill's content. Not for installing, removing, or listing skills.
---

# Skill Writing

These rules govern the text an agent reads when it runs a skill. A good skill makes the agent take the same *process* every run, not produce the same output. Before calling a draft done, check every line against every section below.

## The description is a context pointer

A **context pointer** is text that stays in the agent's context and decides when it reaches material outside it. The description is the skill's pointer: its wording, not the body, decides whether the skill fires. When a skill misfires, sharpen the description first.

- Model-invoked: say what the skill does, then the **branches** that should trigger it (the distinct cases it handles), then a boundary for close misses that should not load it.
- One trigger per branch. Synonyms for one case are one branch written twice; keep the word users actually type.
- User-invoked: write one or two sentences for the human choosing the command, no trigger list.
- Keep it under 1024 characters. A model-invoked description loads every turn, so prune it harder than the body.

## Choose the invocation

- **Model-invoked** (no `disable-model-invocation`): the agent can load it on its own, and other skills can hand off to it. Pays context load every turn. Use it when the agent or another skill must reach the skill.
- **User-invoked** (`disable-model-invocation: true` in `SKILL.md` and `policy.allow_implicit_invocation: false` in `agents/openai.yaml`, set together): costs no context, but only the human can call it, and no skill can hand off to it.
- Reference that several skills share lives in one place. Make it a model-invoked skill when it is a job the agent may need to apply on its own, outside those skills (writing rules apply whenever someone edits a skill). Make it a plain file the skills point at when it only serves them. When it is unclear which case applies, ask the user. A plain file needs a path every target agent can still read after the plugin is copied into its cache.
- When user-invoked skills grow past what the user remembers, propose a **router skill**: one user-invoked skill that names the others and when to reach each.

## Where material sits

A skill holds **steps** (ordered actions) and **reference** (rules and facts consulted on demand). Every line of `SKILL.md` costs context each time the skill loads, so rank material by how often runs need it:

1. Steps, in `SKILL.md`.
2. Reference every branch needs, in `SKILL.md`.
3. Reference only some branches need, in `references/`, linked from the step that needs it with the condition for reading it ("when the target is Pi, read `references/pi.md`").

Apply the **branch test**: inline what every branch needs, move out what only some reach. Reference left inline between steps buries them, and the agent starts skipping steps. Keep one concept's definition, rules, and caveats under one heading. A skill past 500 lines is **sprawl** even when every line is live; split it by branch. Add a table of contents to a reference past 300 lines.

## Steps

Write each step as an imperative that names the goal, the reason, and the completion criterion, and leave the method to the agent. A capable model picks a better method for the case in front of it than a fixed recipe does, and the reason lets it judge edge cases the step did not foresee.

- Recipe: "Run `grep -rn \"X(\" src/` and list the matches."
- Goal: "Find every call site of `X`, so the edit in step 3 misses none. Done when every site is listed with file and line."

Keep a step strict only for correctness or safety: data loss, broken installs, security. State it with must or never, and pair the ban with the action to take instead ("Never overwrite an existing `SKILL.md`; stop and tell the user").

## Completion criteria

Every step ends on a **completion criterion**, the condition that tells the agent the step is done.

- **Checkable**: the agent can tell done from not done. A vague bound ("until you understand the code") invites **premature completion**, because the visible later steps pull the agent forward.
- **Exhaustive**: the bound demands the full job. "Every modified model accounted for" drives the digging that "produce a change list" lets the agent skip. A reference-only skill sets the same bar with "check every rule".

When the bound cannot be sharpened and runs still rush, hide the later steps behind a real context boundary: a fresh-context subagent runs the current step, or a hand-off starts a new session. A skill loaded inline in the same session hides nothing.

## Words

- **Leading words**: replace a phrase repeated across the skill with one word the model already knows ("fast, deterministic, low-overhead" becomes *tight*). Turn a fuzzy gate into an observable state (the test goes *red*). Prefer an existing word to a coined one, which needs a definition to work.
- **Positive phrasing**: state the behaviour you want ("write one-line comments"). A ban puts the banned behaviour in context and makes it more likely.
- **Strength**: when a word fails to beat the default (*be thorough* to an agent that is already fairly thorough), use a stronger word (*relentless*) instead of adding sentences.

## Generalise from the user

The user explains what they want through examples and their own phrasing. Write the rule the examples point at, in words an agent follows most easily, and keep the user's example only when it illustrates that rule. A skill tuned to one example fails on the next request.

## What earns a line

A line stays only when it changes what the agent does compared to its default.

- Cut **no-ops**: instructions a capable model follows anyway, such as reading a file or summarising text. Delete the whole sentence rather than trimming words. When two people disagree about a no-op, run the skill to settle it.
- Keep what the agent cannot find by looking: unwritten conventions, the reason behind a choice, gotchas no config reveals, exact formats.
- The **environment** is a source of truth (`package.json`, config files, `--help`). A line that copies it goes stale; point to the source and tell the agent to look it up, especially for API fields, CLI flags, schemas, and versions.
- Keep one meaning in one place. Duplication costs tokens and inflates how important that meaning looks.
- Prune lines that no longer bear on the task, or stale layers settle into **sediment**.

## Cross-agent body

Skill bodies run unchanged on Claude Code, Codex, and Pi:

- Name capabilities, not tool names: "ask the user", "use your web search capability". To ask something, give the question format.
- Hand off with `Load the "<name>" skill`. Each agent resolves it its own way. Avoid `/name` mentions (Claude Code syntax) and paths into another skill's folder, which break once the plugin is copied into an agent's cache.
- Start every dispatched subagent with a fresh context window; some agents fork the parent conversation by default.
- Pi ships only read, bash, edit, and write. Give every step that needs subagents, web search, or a question tool a way to make progress without it, such as doing the work inline.
- Always-on behaviour needs a Claude Code hook and, for Pi, a matching extension in the package's `extensions/` folder.

## Resources

- `scripts/`: code the agent would otherwise rewrite every run, or steps that must be deterministic.
- `references/`: material only some branches need.
- `assets/`: files used in the output, such as templates and images.
- `README.md`: optional, for humans browsing the repo (what the skill does, credits). `SKILL.md` and its references never link to it, so no agent loads it. No changelog or install guide inside a skill.
