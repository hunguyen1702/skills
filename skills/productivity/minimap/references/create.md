# Create a home repo

## 1. Collect the repos

Ask the user where the home repo should live (recommend the current folder when it is empty or not yet a git repo) and which repos it should map: paths, or a parent folder to scan. For a parent folder, run `minimap.py scan <dir>` and show the list for the user to mark in or out, recommending repos with recent commits.

Give each repo a placeholder name: lowercase letters, digits, and `-`, short, and clear in a sentence ("deploy {{wallet}} first"). Propose names from the folder names and let the user rename.

Done when every repo has a path the user confirmed and a name.

## 2. Survey

Read `references/survey.md` and follow it. Done when every repo has a report.

## 3. Draft the map

Group the repos into areas by their wiring, and name each area after the domain it serves. Pick the flat or tiered layout per `references/templates.md`. Draft every file the layout needs.

Check the draft for these cases and give each one a warning with options:

- **Unrelated repo**: a repo with no wiring edge to any other. It costs one map line while idle, but it muddies areas and widens every task that sweeps all repos. Options: keep it in the `standalone` area (recommended), drop it, or move it to a separate home repo.
- **Nested home repo**: a child that is itself a home repo. Map it as one area that points at its own `AGENTS.md`; never copy its repos into this map, or the two drift apart. Warn that each nested level adds a full rules file to the context when the agent descends.
- **Unverified edges**: list them so the user can confirm or remove each.

## 4. Review

Show the user the whole draft in chat: `## Map` of `AGENTS.md`, each area file, and the warnings, then ask the warning decisions as a round. Apply the user's corrections and show the changed parts again.

Done when the user tells you to init. A correction is not approval.

## 5. Init

1. Run `minimap.py install <home>`. It runs `git init` when needed, copies the script to `.minimap/bin/`, creates `repos.example` and `repos.local`, adds `repos.local` to `.gitignore`, and installs a pre-commit hook that runs `check-paths`.
2. From the home repo root, run `python3 .minimap/bin/minimap.py set <name> <path>` for every repo. It records the path in `repos.local` and the repo's `origin` remote in `repos.example`.
3. Write `AGENTS.md`, `CLAUDE.md`, and the area files from the approved draft. When `AGENTS.md` or `CLAUDE.md` already exists, show the user how you would merge the draft into it and wait for approval.
4. Run `check-paths --all`. Fix every hit before you go on.
5. Commit only when the user asks.

Done when every file in the approved draft exists and `check-paths --all` passes.

## 6. Offer knowledge

Ask the user whether they want to add context that no single repo records, such as a flow across repos or a deploy order. For each entry they give, follow "Add or edit knowledge" in `references/update.md`.

## 7. Report

List each file you wrote, each repo and its placeholder, each warning and the user's choice, and anything you skipped with the reason. Tell the user that on another machine `python3 .minimap/bin/minimap.py init-paths` fills `repos.local`, and that `init-paths --root <dir> --clone` clones missing repos under one folder.
