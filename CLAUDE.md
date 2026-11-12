This repo is the set of skills I use in daily work, currently mostly for software engineering. Claude Code and Codex are the two supported agents; other agents may work, but nothing here is tuned for them. Both agents install the repo from its local directory as the `hungnguyen-skills` plugin. Codex reads `.claude-plugin/` directly, so there is no `.codex-plugin/`.

## Skill files

Every skill has a `SKILL.md` and an `agents/openai.yaml` (Codex metadata). Both schemas still change, so look up the current fields in the Claude Code and Codex skill docs instead of copying an older skill.

A user-invoked skill (reachable only when the human types its name) sets `disable-model-invocation: true` in `SKILL.md` and `policy.allow_implicit_invocation: false` in `agents/openai.yaml`. Set both or neither: with only one, the skill stays auto-invocable in the other agent without any error.

## Writing skill bodies

Skill bodies must run unchanged on both agents, so describe behaviour, not one agent's tool names:

- Capabilities both agents have, like web search or fetching a URL, are named as capabilities: "use your web fetch capability to read the docs".
- To ask the user something, say so and give the question format. Do not name an agent-specific question tool.
- To hand off to another skill, write `Call the Skill tool with "<name>"`. A `/name` mention is Claude Code syntax that Codex may read as plain text, and reading another skill's files by relative path breaks once the plugin is copied into an agent's cache.
- Any step that dispatches a subagent says to start it with a fresh context window. Codex forks the parent conversation by default, which defeats the point of an independent subagent.

## Releasing a change

Both agents cache the installed plugin by `version`, so a change without a bump never reaches them. In the same change that adds, edits, or removes a skill:

- Bump `version` in `.claude-plugin/plugin.json`: patch for edits to an existing skill, minor for a new skill, major for removing or renaming one (commit as `feat!`).
- Update the skill list in `README.md`.

After editing either manifest in `.claude-plugin/`, run `claude plugin validate .`. Skip `--strict`: it fails only on the missing icon, which matters for public marketplace listings, not this private plugin.
