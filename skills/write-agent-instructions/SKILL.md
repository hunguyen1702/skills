---
name: write-agent-instructions
description: Write or revamp a repo's agent instructions file (AGENTS.md or CLAUDE.md), keeping only rules an agent cannot discover on its own, moving task-specific rules to docs/agents/, and setting up a gitignored local file for machine-specific rules.
disable-model-invocation: true
---

# Write Agent Instructions

The instructions file loads into every session before any work starts, and every line spends the agent's instruction budget whether or not it bears on the task. Aim for a file that is small, accurate, and points elsewhere.

## Rules

Apply every rule to every line you write or keep.

- **Undiscoverable**: trust the agent's explore phase. Keep a line only when the agent cannot infer it from code, config, or docs. Do not copy `package.json` scripts, framework names, or config values; the agent reads the source of truth itself.
- **Capabilities, not paths**: describe what the project does and its overall shape, not where files live. Paths go stale on the next rename and the agent then looks in the wrong place with confidence.
- **Scope**: a rule every session needs stays in the root file. A rule only some tasks need goes in `docs/agents/<kebab-case-name>.md`, named so the content is clear from the name (`testing-conventions.md`, `database-migrations.md`). The root file points to it as "When <task>, read `docs/agents/<file>`." Create `docs/agents/` when it does not exist.
- **Repeated flows**: when a `docs/agents/` file describes a multi-step flow the user runs again and again, suggest turning it into a skill. Do not create the skill yourself.
- **Delete**: cut lines that are redundant (the agent already knows this), too vague to act on, or obvious ("write clean code").
- **Tone**: write plain, conversational sentences. No all-caps, no "ALWAYS" or "NEVER" except for security.
- **Security**: the root file holds this rule once, and no other file repeats it:

  ```markdown
  ## Security

  - Never write secrets, credentials, or environment variable values into any file, including docs and instructions.
  - Ask the user before reading any file that may hold secrets or environment variables (such as `.env*`, `*.pem`, `*.key`, credential files), even when running without permission prompts.
  ```

  Instructions files themselves never contain secret values or credentials.

## 1. Pick the branch

Find the repo's instructions files (`AGENTS.md`, `CLAUDE.md`, and nested ones) and `docs/agents/`.

- **Revamp**: an instructions file exists. Go to step 3.
- **Generate**: no instructions file, but the repo has code or docs to explore. Go to step 2.
- **Interview**: no instructions file and nothing to explore. Ask the user which rules they want, as a numbered list they can answer in one reply. Run each answer through the rules; drop or rewrite what fails and tell the user why. Go to step 4.

When no file exists, the root file is `AGENTS.md`, plus a `CLAUDE.md` holding only `@AGENTS.md` so Claude Code loads it. When one exists, keep it as the root file.

## 2. Generate

Explore the repo for what an agent cannot discover alone: a one-sentence project description, a non-default package manager, non-standard build or check commands, and conventions the code does not show. Done when every candidate line passes the rules. Go to step 4.

## 3. Revamp

Classify every line of the existing files, then show the user one list before writing anything:

- **Keep**: lines that pass every rule.
- **Move**: lines that belong in a `docs/agents/` file, with the target file name.
- **Delete**: lines that fail a rule, with the rule that fails.
- **Contradictions**: pairs of lines that conflict. Ask which one to keep.

Done when every line is in exactly one group. Wait for the user's approval and apply their changes to the list.

## 4. Local rules

Ask the user whether they want machine-specific rules, such as their OS and shell, the package manager or runtime versions on their machine, and how their git is configured (signing, default branch, hooks). Record only adjustments that differ from the repo's shared setup.

If they want any, write them to `CLAUDE.local.md` when the root file is `CLAUDE.md`, or `AGENTS.local.md` when it is `AGENTS.md`. Add that file to `.gitignore`. In the root file, add: "Machine-specific rules may live in `<local file>` (gitignored); read it when it exists."

## 5. Write

Write the root file, any `docs/agents/` files, and the local file. Include the security section in the root file. Then show the user the file tree and the root file in full.
