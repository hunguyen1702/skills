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

Skills live in `skills/<category>/<skill>/`. Claude Code and Codex find them through the `skills` paths in `.claude-plugin/plugin.json`, so a new category needs a new path there. Pi finds them on its own.

### Agent

Build, edit, and evaluate skills, and write agent instructions.

- [`skill-cook`](skills/agent/skill-cook/SKILL.md): create a new skill for Claude Code, Codex, Pi, or any mix, from scaffold to validation. User-invoked.
- [`skill-copycat`](skills/agent/skill-copycat/SKILL.md): steal the distinctive techniques from skills or articles into one digest grouped by source and scope, as context for the session. User-invoked.
- [`skill-taste`](skills/agent/skill-taste/SKILL.md): edit, improve, and evaluate an existing skill, including output evals and trigger evals on Claude Code and Codex (Pi skills too, without trigger evals). User-invoked.
- [`skill-writing`](skills/agent/skill-writing/SKILL.md): rules for writing a skill's description, body, and references so it runs predictably on Claude Code, Codex, and Pi. Loaded by `skill-cook` and `skill-taste`, and on its own when you edit a skill.
- [`write-agent-instructions`](skills/agent/write-agent-instructions/SKILL.md): write or revamp a repo's `AGENTS.md` or `CLAUDE.md`, keeping only undiscoverable rules, moving task-specific ones to `docs/agents/`, and adding a gitignored local rules file. Also loads on its own when an agent adds a rule to these files.

### Engineering

Research, plan, verify, and ship code changes.

- [`codebase-design`](skills/engineering/codebase-design/SKILL.md): shared vocabulary for designing deep modules (module, interface, seam, adapter, depth, leverage, locality), with references on deepening a cluster of modules and comparing alternative interfaces in parallel. Copied from mattpocock/skills (MIT).
- [`code-review`](skills/engineering/code-review/SKILL.md): review the changes since a fixed point on four axes in parallel subagents, Standards (the repo's documented standards plus a baseline of Fowler code smells and lean checks), Spec (the originating issue or spec), Correctness (bugs, data loss, scale, missing tests, speed), and Security (exploitable vulnerabilities the change adds, filtered by a second verifier), and report them side by side with severity icons, a `file:L<n>` location on every finding, and a verdict. Can also review a GitHub PR through `gh pr diff` without checking it out. Copied from mattpocock/skills (MIT), with material from ponytail (MIT), caveman (Apache-2.0), and Anthropic's claude-code-security-review (MIT); reads the tracker set up by `setup-hungnguyen-skills`.
- [`commit-changes`](skills/engineering/commit-changes/SKILL.md): group the current changes into ordered, reviewable commits, stage them, and write Conventional Commits messages in English. Loads on its own when you or the agent are about to commit.
- [`design-contracts`](skills/engineering/design-contracts/SKILL.md): vocabulary and rules for settling contracts while planning: what a module guarantees and how it fails, which module owns each domain invariant, how to classify bad cases, and which decisions to settle now versus leave to implementation. Builds on `codebase-design`; meant to be loaded by a planning skill.
- [`domain-modeling`](skills/engineering/domain-modeling/SKILL.md): build and sharpen the project's domain model while you design: challenge terms against `GLOSSARY.md`, probe edge cases, update the glossary as terms resolve, and offer an ADR only for decisions that are hard to reverse, surprising, and a real trade-off. Copied from mattpocock/skills (MIT).
- [`grilling`](skills/engineering/grilling/SKILL.md): interview you in rounds of numbered questions with recommended answers until a plan reaches shared understanding. Copied from mattpocock/skills (MIT).
- [`implement`](skills/engineering/implement/SKILL.md): implement a spec or set of tickets test-first at the agreed seams, keep each change lean with `lean-change`, run the checks, have the work reviewed, and commit. User-invoked. Adapted from mattpocock/skills (MIT).
- [`lean-change`](skills/engineering/lean-change/SKILL.md): change code for a task with the least impact on the codebase: reach every place the change touches, prefer the option with the smallest blast radius, reuse before writing new code, and add no speculative abstractions. Loads on its own when an agent implements, fixes, or refactors code. Adapted from [ponytail](https://github.com/DietrichGebert/ponytail) (MIT).
- [`pr`](skills/engineering/pr/SKILL.md): write a PR body that is fast to review, with a summary that picks the right visual for the diff. Copied from mattpocock/skills (MIT).
- [`pr-review-comments`](skills/engineering/pr-review-comments/SKILL.md): post a JSON array of review findings as inline comments on a GitHub PR through `gh`, either as one grouped review or as separate comments; a dry run first skips and reports findings whose line is outside the diff. Copied from giuseppe-trisciuoglio/developer-kit (MIT).
- [`probe`](skills/engineering/probe/SKILL.md): verify a design idea with a throwaway prototype built in its own worktree: a logic demo (a shareable HTML file or a runner inside the repo), UI variants on one route, or a spike that checks one or several third-party APIs or libraries against the current codebase; databases only as a cloned copy, and a Markdown report committed with the prototype to a pushed throwaway branch. Adapted from mattpocock/skills `prototype` (MIT).
- [`review-pr`](skills/engineering/review-pr/SKILL.md): review a GitHub PR with `code-review` in a temporary worktree at the PR head, then post the findings as one review of inline comments through `pr-review-comments`; shows you a draft to revise and approve first, or posts right away with `--mode auto` and summarises what it posted. User-invoked.
- [`scout`](skills/engineering/scout/SKILL.md): research a question against primary sources in a background agent and save the cited findings as a Markdown file in the repo. Copied from mattpocock/skills (MIT), renamed from `research`.
- [`setup-hungnguyen-skills`](skills/engineering/setup-hungnguyen-skills/SKILL.md): configure a repo once for the engineering skills: its issue tracker (GitHub, GitLab, local Markdown, or other), triage labels, and domain doc layout. User-invoked. Adapted from mattpocock/skills `setup-matt-pocock-skills` (MIT).
- [`tdd`](skills/engineering/tdd/SKILL.md): test-driven development in red-green vertical slices, testing only at agreed seams through public interfaces. Copied from mattpocock/skills (MIT).
- [`to-spec`](skills/engineering/to-spec/SKILL.md): turn the current conversation into a spec and publish it to the issue tracker, without interviewing you again. Its Implementation Decisions section also asks for shared-seam contracts, invariant owners, and decisions left to implementation. User-invoked. Adapted from mattpocock/skills (MIT); needs `setup-hungnguyen-skills` run once per repo.
- [`to-tickets`](skills/engineering/to-tickets/SKILL.md): break a spec or plan into tracer-bullet tickets with blocking edges and publish them to the configured tracker. User-invoked. Adapted from mattpocock/skills (MIT); needs `setup-hungnguyen-skills` run once per repo.
- [`vet`](skills/engineering/vet/SKILL.md): verify a point from the conversation against current standards and best practices, fitted to the project's versions and code, through a `scout` subagent. User-invoked.

### Productivity

How sessions talk, log, get named, and find your other repos.

- [`better-talk`](skills/productivity/better-talk/SKILL.md): chat replies that answer first, read like one person talking to another, and ask questions you can answer at once, in any language. Always on: plugin hooks load it at session start and reload it if its rules drop out of context; on Pi, `extensions/better-talk.ts` puts its rules in the system prompt.
- [`dig-in`](skills/productivity/dig-in/SKILL.md): dig into a topic at your goal and level, with a scouted map, a proposed output format and writing style, and a fresh researcher per part. User-invoked.
- [`huh`](skills/productivity/huh/SKILL.md): explain again something you did not understand (a hint you give, or the last message), in short, simple words with the project's own terms. User-invoked.
- [`journal`](skills/productivity/journal/SKILL.md): log any session (planning, debugging, research, learning) turn by turn into a gitignored `<repo>/.journal-log/` file, recording findings, your decisions, and open questions, and carry the log across handoffs. Pass `off` to stop. While it is on, a plugin hook (on Pi, `extensions/journal.ts`) reminds the agent each turn. Needs `python3`. On Codex, trust the plugin hook in `/hooks` first.
- [`minimap`](skills/productivity/minimap/SKILL.md): build or update a home repo, one place to start agent sessions from, that maps your other repos as `{{name}}` placeholders with local paths kept out of git, loads each repo's own rules through a script, and opens each part of the map only when a task reaches it. Inspired by Matt Pocock's [The Home Repo Pattern](https://www.aihero.dev/the-home-repo-pattern). User-invoked; needs `python3`.
- [`name-session`](skills/productivity/name-session/SKILL.md): name the current Claude Code, Codex, or Pi session with local Ollama and an optional hint. User-invoked.
- [`namer-service`](skills/productivity/namer-service/SKILL.md): check and start the shared Ollama service, and download `qwen2.5:3b` when missing. User-invoked.

### Tooling

Wrappers around specific CLIs and services.

- [`gkg`](skills/tooling/gkg/SKILL.md): search definitions, find references, and map a repo with the GitLab Knowledge Graph CLI and MCP tools.
- [`skills-npx`](skills/tooling/skills-npx/SKILL.md): install or remove one or more third-party skills with `npx skills@latest`, after searching by name if needed and asking for agents and scope (global, project, or stealth project). User-invoked.

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
