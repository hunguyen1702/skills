---
name: skills-npx
description: Install or remove one or more third-party skills with `npx skills@latest`. Give it sources (repo, URL, `owner/repo@skill`) or just skill names to search for; it confirms the skills, the target agents, and the scope (global, project, or stealth project) before running anything.
disable-model-invocation: true
---

# Skills Npx

Wraps the `npx skills@latest` CLI for one or more named skills per run. Every step below applies to each requested skill; ask each question once for the whole batch. Run `npx skills@latest <command> --help` when a flag below does not behave as described; the CLI's help wins over this file.

Run every command non-interactively (`-y`, stdin closed), because the CLI's prompts would hang the agent's shell.

## Install

### 1. Resolve the source

- **Specific source given** (`owner/repo@skill`, a GitHub URL or tree URL, a repo plus a skill name): use it as is.
- **Only a name**: run `npx skills@latest find <name>`. From the results, show at most 5, ordered by install count, with official owners (`anthropics`, `openai`, `vercel-labs`, and the vendor of the tool the skill is about) first. Drop forks and translations (such as `*-zh-cn`) unless the user asked for one. Show each as `owner/repo@skill`, install count, and its `skills.sh` link. With several bare names, search each and show one numbered list per name, then ask for all picks in one reply.

### 2. Ask where to install

Ask in one numbered question set, with a recommended answer for each. The answers apply to the whole batch unless the user splits it:

1. **Agents**: which agents to install for (CLI ids such as `claude-code`, `codex`). Recommend the agents the user runs in this session's environment.
2. **Scope**:
   - **global**: one copy in `~/.agents/skills/<skill>`, symlinked into each chosen agent's user skill folder.
   - **project**: a copy in `<repo>/.agents/skills/<skill>`, linked into each chosen agent's project folder, and recorded in `<repo>/skills-lock.json`. Meant to be committed.
   - **stealth project**: same as project, but git ignores it on this machine only (no `.gitignore` change). Only offer it inside a git repo.

### 3. Install

Run from the repo root for project scopes:

```bash
npx skills@latest add <repo> -s <skill> [-s <skill> ...] -a <agent> [-a <agent> ...] [-g] -y
```

Run one `add` per source repo, passing all of that repo's skills. Add `-g` only for global scope. Afterwards run `npx skills@latest ls [-g]` and confirm every skill is listed for every chosen agent.

`add` prints a Security Risk Assessments table (Gen, Socket, Snyk) per skill. Relay it to the user. It prints during the install, so `-y` does not stop on a bad rating: when any cell is not `Safe` or `0 alerts`, say so and offer to remove the skill.

For **stealth**, append these lines per skill to `.git/info/exclude`, skipping any already present:

```
.agents/skills/<skill>/
<agent project skill folder>/<skill>
skills-lock.json
```

Take each agent's project skill folder from the `add` output (for example `.claude/skills/<skill>`); agents that read `.agents/skills` directly need no extra line. Exclude does not hide a file git already tracks, so if `git ls-files --error-unmatch skills-lock.json` succeeds, tell the user its changes will show in their diff.

## Remove

1. Run `npx skills@latest ls` and `npx skills@latest ls -g` to find where each skill is installed, then ask which scope to remove them from.
2. Run `npx skills@latest remove <skill> [<skill> ...] [-g] -y`, once per scope.
3. If a project install was stealth, delete each removed skill's lines from `.git/info/exclude`. Delete the `skills-lock.json` line only when no other excluded `.agents/skills/` entry remains.
