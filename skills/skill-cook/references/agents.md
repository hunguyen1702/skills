# Supported agents

These are pointers, not schemas. Agent skill formats change often, so read the sources before writing frontmatter or metadata files. Docs are the primary source. When they are silent or ambiguous, read the agent's source code.

Each section matches a module in `scripts/agents/`. To support a new agent, add a section here and a module there.

## claude-code

Sources:
- Skills: https://code.claude.com/docs/en/skills (frontmatter fields, locations, invocation control)
- Plugins: https://code.claude.com/docs/en/plugins-reference (plugin layout, `skills/` folder, namespacing)

Skill folders:

| Scope | Path |
|---|---|
| global | `~/.claude/skills/<name>/` |
| project | `<repo>/.claude/skills/<name>/` |
| plugin | `<plugin>/skills/<name>/` |

Facts to check against the docs:
- Invocation: `disable-model-invocation: true` makes the skill user-invoked only.
- Metadata file: none. Everything lives in `SKILL.md` frontmatter.
- Claude Code does not read `.agents/skills/`. A skill shared with Codex at project or global scope needs a symlink from the Claude folder.

## codex

Sources:
- Skills: https://learn.chatgpt.com/docs/build-skills
- Source of truth when the docs are silent: https://github.com/openai/codex. Read `codex-rs/skills/src/parser.rs` (frontmatter), `interface.rs` and `metadata.rs` (`agents/openai.yaml`).

Skill folders:

| Scope | Path |
|---|---|
| global | `~/.agents/skills/<name>/` (`~/.codex/skills/` is deprecated) |
| project | `<repo>/.agents/skills/<name>/` |
| plugin | `<plugin>/skills/<name>/` |

Facts to check against the source:
- Invocation: `policy.allow_implicit_invocation: false` in `agents/openai.yaml` hides the skill from the model. Users can still call it explicitly with `$name`.
- Metadata file: `agents/openai.yaml`, holding `interface`, `dependencies` and `policy`.
- `SKILL.md` frontmatter: only `name` and `description` are read. Codex ignores keys meant for other agents.
