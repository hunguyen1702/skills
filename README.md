# hungnguyen-skills

The skills I use in daily work, mostly for software engineering. Built for Claude Code and Codex; other agents may load them, but are not tested.

## Install

Both agents install from a local clone. Replace `<path>` with the clone's absolute path.

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

Both agents cache the plugin by version. After pulling a new version, run `claude plugin update hungnguyen-skills@hungnguyen-skills` for Claude Code, and reinstall with `codex plugin add` for Codex.

## Skills

- [`gkg`](skills/gkg/SKILL.md): search definitions, find references, and map a repo with the GitLab Knowledge Graph CLI and MCP tools.
- [`dig-in`](skills/dig-in/SKILL.md): dig into a topic at your goal and level, with a scouted map, a proposed output format and writing style, and a fresh researcher per part. User-invoked.
- [`grilling`](skills/grilling/SKILL.md): interview you in rounds of numbered questions with recommended answers until a plan reaches shared understanding. Copied from mattpocock/skills (MIT).
- [`skill-cook`](skills/skill-cook/SKILL.md): create a new skill for Claude Code, Codex, or both, from scaffold to validation. User-invoked.
- [`skill-taste`](skills/skill-taste/SKILL.md): edit, improve, and evaluate an existing skill, including output evals and trigger evals on Claude Code and Codex. User-invoked.
