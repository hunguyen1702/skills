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

- [`name-session`](skills/name-session/SKILL.md): name the current Claude Code, Codex, or Pi session with local Ollama and an optional hint. User-invoked.
- [`namer-service`](skills/namer-service/SKILL.md): check and start the shared Ollama service, and download `qwen2.5:3b` when missing. User-invoked.

- [`gkg`](skills/gkg/SKILL.md): search definitions, find references, and map a repo with the GitLab Knowledge Graph CLI and MCP tools.
- [`better-talk`](skills/better-talk/SKILL.md): chat replies that answer first, read like one person talking to another, and ask questions you can answer at once, in any language. Always on: plugin hooks load it at session start and reload it if its rules drop out of context; on Pi, `extensions/better-talk.ts` puts its rules in the system prompt.
- [`dig-in`](skills/dig-in/SKILL.md): dig into a topic at your goal and level, with a scouted map, a proposed output format and writing style, and a fresh researcher per part. User-invoked.
- [`grilling`](skills/grilling/SKILL.md): interview you in rounds of numbered questions with recommended answers until a plan reaches shared understanding. Copied from mattpocock/skills (MIT).
- [`write-agent-instructions`](skills/write-agent-instructions/SKILL.md): write or revamp a repo's `AGENTS.md` or `CLAUDE.md`, keeping only undiscoverable rules, moving task-specific ones to `docs/agents/`, and adding a gitignored local rules file. Also loads on its own when an agent adds a rule to these files.
- [`journal`](skills/journal/SKILL.md): log any session (planning, debugging, research, learning) turn by turn into a gitignored `<repo>/.journal-log/` file, recording findings, your decisions, and open questions, and carry the log across handoffs. Pass `off` to stop. While it is on, a plugin hook (on Pi, `extensions/journal.ts`) reminds the agent each turn. Needs `python3`. On Codex, trust the plugin hook in `/hooks` first.
- [`commit-changes`](skills/commit-changes/SKILL.md): group the current changes into ordered, reviewable commits, stage them, and write Conventional Commits messages in English. Loads on its own when you or the agent are about to commit.
- [`huh`](skills/huh/SKILL.md): explain again something you did not understand (a hint you give, or the last message), in short, simple words with the project's own terms. User-invoked.
- [`skill-copycat`](skills/skill-copycat/SKILL.md): steal the distinctive techniques from skills or articles into one digest grouped by source and scope, as context for the session. User-invoked.
- [`skill-cook`](skills/skill-cook/SKILL.md): create a new skill for Claude Code, Codex, Pi, or any mix, from scaffold to validation. User-invoked.
- [`skill-writing`](skills/skill-writing/SKILL.md): rules for writing a skill's description, body, and references so it runs predictably on Claude Code, Codex, and Pi. Loaded by `skill-cook` and `skill-taste`, and on its own when you edit a skill.
- [`skills-npx`](skills/skills-npx/SKILL.md): install or remove one or more third-party skills with `npx skills@latest`, after searching by name if needed and asking for agents and scope (global, project, or stealth project). User-invoked.
- [`skill-taste`](skills/skill-taste/SKILL.md): edit, improve, and evaluate an existing skill, including output evals and trigger evals on Claude Code and Codex (Pi skills too, without trigger evals). User-invoked.
- [`lean-change`](skills/lean-change/SKILL.md): change code for a task with the least impact on the codebase: reach every place the change touches, prefer the option with the smallest blast radius, reuse before writing new code, and add no speculative abstractions. Loads on its own when an agent implements, fixes, or refactors code. Adapted from [ponytail](https://github.com/DietrichGebert/ponytail) (MIT).
- [`scout`](skills/scout/SKILL.md): research a question against primary sources in a background agent and save the cited findings as a Markdown file in the repo. Copied from mattpocock/skills (MIT), renamed from `research`.
- [`minimap`](skills/minimap/SKILL.md): build or update a home repo, one place to start agent sessions from, that maps your other repos as `{{name}}` placeholders with local paths kept out of git, loads each repo's own rules through a script, and opens each part of the map only when a task reaches it. Inspired by Matt Pocock's [The Home Repo Pattern](https://www.aihero.dev/the-home-repo-pattern). User-invoked; needs `python3`.

## Credits

These skills stand on the shoulders of great minds. The ideas that shape this repo come from their work, and they deserve the credit:

| Skill set | The great mind behind it | What I learned from it |
| --- | --- | --- |
| [pstack](https://github.com/cursor/plugins/tree/main/pstack) | Lauren Tan ([@poteto](https://github.com/poteto)) | A rigorous engineering discipline for agents: understand first, verify the result for real, and ship with care. |
| [caveman](https://github.com/JuliusBrussee/caveman) | Julius Brussee ([@JuliusBrussee](https://github.com/JuliusBrussee)) | The bold insight that fewer tokens often do the trick, and that an agent's words should earn their place. |
| [skills](https://github.com/mattpocock/skills) | Matt Pocock ([@mattpocock](https://github.com/mattpocock)) | Practical skills for real engineers, written with the clarity of a world-class teacher. |
| [ponytail](https://github.com/DietrichGebert/ponytail) | Dietrich Gebert ([@DietrichGebert](https://github.com/DietrichGebert)) | A lazy senior developer's mindset: solve the whole problem with the least new code, the idea behind `lean-change`. |
| [The Home Repo Pattern](https://www.aihero.dev/the-home-repo-pattern) | Matt Pocock ([@mattpocock](https://github.com/mattpocock)) | One repo to start every session from, with pointers to the rest, the idea behind `minimap`. |

Thank you for sharing your thinking so openly.
