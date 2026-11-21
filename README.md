# hungnguyen-skills

The skills I use in daily work, mostly for software engineering. Built for Claude Code, Codex, and Pi; other agents may load them, but are not tested.

## Install

All three agents install from a local clone. Replace `<path>` with the clone's absolute path.

Claude Code:

```bash
claude plugin marketplace add <path>
claude plugin install hungnguyen-skills@hungnguyen-skills
```

Codex:

```bash
codex plugin marketplace add <path>
codex plugin add hungnguyen-skills@hungnguyen-skills
```

Pi:

```bash
pi install <path>
```

Pi loads `skills/` and the `extensions/` that stand in for the Claude Code hooks. It reads the clone directly, so run `/reload` after pulling.

Claude Code and Codex cache the plugin by version. After pulling a new version, run `claude plugin update hungnguyen-skills@hungnguyen-skills` for Claude Code, and reinstall with `codex plugin add` for Codex.

## Skills

- [`gkg`](skills/gkg/SKILL.md): search definitions, find references, and map a repo with the GitLab Knowledge Graph CLI and MCP tools.
- [`better-talk`](skills/better-talk/SKILL.md): chat replies that answer first, read like a colleague talking, and ask questions you can answer at once, in any language. Always on: plugin hooks load it at session start and reload it if its rules drop out of context; on Pi, `extensions/better-talk.ts` puts its rules in the system prompt.
- [`dig-in`](skills/dig-in/SKILL.md): dig into a topic at your goal and level, with a scouted map, a proposed output format and writing style, and a fresh researcher per part. User-invoked.
- [`grilling`](skills/grilling/SKILL.md): interview you in rounds of numbered questions with recommended answers until a plan reaches shared understanding. Copied from mattpocock/skills (MIT).
- [`write-agent-instructions`](skills/write-agent-instructions/SKILL.md): write or revamp a repo's `AGENTS.md` or `CLAUDE.md`, keeping only undiscoverable rules, moving task-specific ones to `docs/agents/`, and adding a gitignored local rules file. Also loads on its own when an agent adds a rule to these files.
- [`huh`](skills/huh/SKILL.md): explain again something you did not understand (a hint you give, or the last message), in short, simple words with the project's own terms. User-invoked.
- [`skill-copycat`](skills/skill-copycat/SKILL.md): steal the distinctive techniques from skills or articles into one digest grouped by source and scope, as context for the session. User-invoked.
- [`skill-cook`](skills/skill-cook/SKILL.md): create a new skill for Claude Code, Codex, Pi, or any mix, from scaffold to validation. User-invoked.
- [`skill-writing`](skills/skill-writing/SKILL.md): rules for writing a skill's description, body, and references so it runs predictably on Claude Code, Codex, and Pi. Loaded by `skill-cook` and `skill-taste`, and on its own when you edit a skill.
- [`skills-npx`](skills/skills-npx/SKILL.md): install or remove one or more third-party skills with `npx skills@latest`, after searching by name if needed and asking for agents and scope (global, project, or stealth project). User-invoked.
- [`skill-taste`](skills/skill-taste/SKILL.md): edit, improve, and evaluate an existing skill, including output evals and trigger evals on Claude Code and Codex (Pi skills too, without trigger evals). User-invoked.
