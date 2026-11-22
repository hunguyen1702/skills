---
name: minimap
description: Build or update a home repo, a single place to work from that maps your other repos, with machine paths kept out of git and each map part loaded only when a task reaches it.
argument-hint: "[create | update] [what to do]"
disable-model-invocation: true
---

# Minimap

A **home repo** is a git repo that holds no product code. Its `AGENTS.md` maps the **child repos** the user works on, so an agent started in the home repo can reach any of them. The map reads like the minimap of a strategy game: the top level shows every area in one line each, and the agent opens an area's detail only when the task reaches it.

`<minimap>` below means the folder containing this file. Before the home repo exists, run the script as `python3 <minimap>/scripts/minimap.py`. Once it exists, run its copy, `python3 .minimap/bin/minimap.py`, from the home repo root, because the home repo must keep working on machines without this skill. Run the script with `--help` for its subcommands.

## Rules for every branch

- Never write to a child repo: no files, branches, or commits. Child repos may belong to a company and follow their own rules; the home repo only reads them.
- Never write a local path into a tracked file. Name a child repo with its **placeholder** `{{name}}`. Paths live in `repos.local`, which git ignores. Remotes live in `repos.example`, which git tracks. `minimap.py set` and `remove` are the only writers of both files.
- Never read `.env` files or other secrets in any repo.
- Change no file until the user approves the draft that change belongs to. Show drafts in chat.
- Ask the user decisions in numbered rounds. Give a recommended answer for each question and word it so "yes" accepts it. Find facts yourself; bring the user only decisions.

## Choose the branch

Run `minimap.py status` in the current folder.

1. The argument or the user's message names the job: `create` or a request to build a home repo leads to create; `update`, adding or removing a repo, rescanning, or adding or editing knowledge leads to update.
2. Otherwise, when status reports `home_repo: no`, take create.
3. Otherwise, ask the user what to update: add repos, remove repos, rescan wiring, or add or edit knowledge.

When the user asks for create in a folder that is already a home repo, tell them and offer update instead.

For create, read `references/create.md`. For update, read `references/update.md`. Both use the file formats in `references/templates.md`.
