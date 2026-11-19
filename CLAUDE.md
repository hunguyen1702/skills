This repo is the set of skills I use in daily work, currently mostly for software engineering. Claude Code, Codex, and Pi are the three supported agents; other agents may work, but nothing here is tuned for them. Claude Code and Codex install the repo from its local directory as the `hungnguyen-skills` plugin; Codex reads `.claude-plugin/` directly, so there is no `.codex-plugin/`. Pi installs the same directory as a Pi package (`pi install <path>`) and auto-discovers `skills/` and `extensions/`.

## Skill files

Every skill has a `SKILL.md` and an `agents/openai.yaml` (Codex metadata). Pi reads only `SKILL.md`. All three schemas still change, so look up the current fields in each agent's skill docs instead of copying an older skill.

A user-invoked skill (reachable only when the human types its name) sets `disable-model-invocation: true` in `SKILL.md` and `policy.allow_implicit_invocation: false` in `agents/openai.yaml`. Set both or neither: with only one, the skill stays auto-invocable in the other agent without any error. Pi honours the same `disable-model-invocation` key as Claude Code.

## Writing skill bodies

Skill bodies must run unchanged on all three agents, so describe behaviour, not one agent's tool names:

- Capabilities like web search or fetching a URL are named as capabilities: "use your web fetch capability to read the docs".
- To ask the user something, say so and give the question format. Do not name an agent-specific question tool.
- To hand off to another skill, write `Load the "<name>" skill`. Each agent resolves it its own way: Claude Code through its Skill tool, Codex and Pi by reading the `SKILL.md` path they list in the system prompt. A `/name` mention is Claude Code syntax (Pi uses `/skill:name`, Codex `$name`), and reading another skill's files by relative path breaks once the plugin is copied into an agent's cache.
- Pi ships only read, bash, edit, and write tools: no subagents, web search, or question tool unless an extension adds them. A step that depends on one of these should still make progress without it, for example by doing the work inline.

## Pi extensions

Claude Code hooks in `hooks/hooks.json` do not run on Pi. Each hook has a Pi counterpart in `extensions/`, so a change to one needs the matching change in the other. Develop extensions with `npm install` once, then `npm run check` (lint, typecheck, and tests in `test/`). Keep `package.json` free of a `pi` field: without it, Pi discovers `skills/` and `extensions/` on its own.

## Releasing a change

Claude Code and Codex cache the installed plugin by `version`, so a change without a bump never reaches them. Pi loads a local install straight from the directory and needs only `/reload`. In the same change that adds, edits, or removes a skill:

- Bump `version` in `.claude-plugin/plugin.json`: patch for edits to an existing skill, minor for a new skill, major for removing or renaming one (commit as `feat!`).
- Update the skill list in `README.md`.

After editing either manifest in `.claude-plugin/`, run `claude plugin validate .`. Skip `--strict`: it fails only on the missing icon, which matters for public marketplace listings, not this private plugin.
