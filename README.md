# hungnguyen-skills

Hung Nguyen's personal Claude Code / Codex skills and plugins.

## Install

```
/plugin marketplace add hungnguyen/skills
```

(or whatever remote path this repo lives at)

Then install a plugin:

```
/plugin install hungnguyen-skills@hungnguyen-skills
```

## Contents

| Plugin | Description |
|---|---|
| `gkg` | How to use the GitLab Knowledge Graph (gkg) CLI and its MCP tools for fast codebase search, definition lookup, and reference finding |

## Structure

- `.claude-plugin/marketplace.json` — marketplace manifest, lists all plugins.
- `.claude-plugin/plugin.json` — metadata for the single multi-skill plugin at repo root.
- `skills/<skill-name>/SKILL.md` — skill instructions (frontmatter `name` + `description`, then body).
- `skills/<skill-name>/evals/evals.json` — eval cases for the skill.

See `CLAUDE.md` (symlinked as `AGENTS.md`) for guidance on adding or editing skills.
