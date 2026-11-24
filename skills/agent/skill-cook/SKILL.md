---
name: skill-cook
description: Create a new skill for one or more coding agents (Claude Code, Codex, Pi) from your intent. It asks where the skill lives, who invokes it, and which agents it targets, then scaffolds, writes and checks it.
disable-model-invocation: true
---

# Skill Cook

Build one new skill that works on every agent the user targets. This skill only creates skills; when the target folder already holds a skill, stop and tell the user so they can decide what to do.

`<skill-cook>` below means the folder containing this file.

## 1. Reach a shared understanding

Load the "grilling" skill and interview the user until you understand what skill they want and how it should work. Recap only what the user confirmed and wait for their go-ahead before scaffolding.

## 2. Decisions the interview must settle

1. **Location**: global (all projects), project (this repo only), the plugin repo it belongs to, or another path.
2. **Invocation**: the agent loads it on its own when a task matches, or only the user invokes it by name. For model-invoked skills, also ask when it should and should not trigger.
3. **Agents**: list the supported agents from `<skill-cook>/references/agents.md` (currently `claude-code`, `codex`, `pi`) and offer `all`.

Map the answers to a folder with the tables in `<skill-cook>/references/agents.md`:
- One agent: that agent's folder for the chosen scope.
- Several agents at global or project scope: the `.agents/skills/` folder, plus a symlink from each agent folder that does not read it (pass `--link`).
- Plugin: `<plugin>/skills/`, no symlink. A folder holding `.claude-plugin/plugin.json` is a plugin.

## 3. Research

When the skill depends on things you do not know for certain (a CLI, an API, an MCP server, a file format), start a subagent with a fresh context window. Have it gather the facts from web search, docs, or MCP tools and report back with sources. Run independent questions in parallel.

Before writing any agent-specific part, also start a fresh-context subagent per target agent. Have it read that agent's sources in `<skill-cook>/references/agents.md` and report the current frontmatter fields, metadata file fields, and invocation keys. Formats change often; the report wins over anything written in this skill or its scripts.

## 4. Scaffold

```bash
python3 <skill-cook>/scripts/scaffold.py <name> --path <parent-folder> --agent <agents> \
  [--user-invoked] [--resources scripts,references,assets] [--link <agent-folder>]
```

`<agents>` is comma-separated or `all`. The script writes `SKILL.md` and each agent's metadata with `[TODO: ...]` placeholders, skips files that exist, and stops if `SKILL.md` exists. Only request the resource folders the skill will use.

If the research report shows the scaffold is out of date for an agent, fix the generated files to match the report and tell the user which module in `<skill-cook>/scripts/agents/` needs updating.

## 5. Write the skill

Replace every placeholder. Load the "skill-writing" skill and apply every rule in it to the description, the body, and each reference.

**Agent metadata**: fill each agent's metadata file per the research report. For Codex, `short_description` is a short line for the skill list.

## 6. Check

```bash
python3 <skill-cook>/scripts/validate.py <skill-folder> --agent <agents>
```

It prints warnings only. Fix what applies. Confirm agent-specific warnings against the research report before acting on them. Rerun until the remaining warnings are deliberate, then show the user the skill's file tree and any warnings you chose to keep.
