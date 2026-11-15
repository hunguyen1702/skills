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
- [`skill-cook`](skills/skill-cook/SKILL.md): create a new skill for Claude Code, Codex, or both, from scaffold to validation. User-invoked.
