# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

`hungnguyen-skills` — a Claude Code plugin marketplace (`.claude-plugin/marketplace.json`) publishing personal Claude Code / Codex skills and plugins. Currently one plugin: `gkg`.

## Structure

- `.claude-plugin/marketplace.json` — marketplace manifest listing all plugins. Each entry: `name`, `source` (path to plugin dir), `description`.
- `.claude-plugin/plugin.json` — metadata (`name`, `description`, `version`, `author`) for the single plugin currently defined at repo root.
- `skills/<skill-name>/` — one directory per skill.
  - `SKILL.md` — the skill itself: YAML frontmatter (`name`, `description`) + markdown body with instructions. The `description` is what triggers the skill's use, so it must be specific about when to invoke it (keywords, task shapes, explicit non-triggers).
  - `evals/evals.json` — eval cases for the skill.
  - `openai.yaml` — OpenAI-compatible export of the skill, if applicable.

## Adding or editing a skill

- New skill: create `skills/<name>/SKILL.md` with frontmatter `name` + `description`, then register it as a plugin entry in `.claude-plugin/marketplace.json` if it should ship as its own plugin.
- `description` field is load-bearing — it's the only thing used to decide whether the skill fires for a given user request. Write it to include trigger phrases and explicit scope boundaries (see `skills/gkg/SKILL.md` for the pattern: golden-rule check sequence, CLI/MCP tool tables, explicit gotchas called out inline).
- Skill bodies favor dense reference tables (commands/flags/params) over prose, and call out non-obvious gotchas explicitly (e.g. a flag that silently no-ops instead of erroring).
