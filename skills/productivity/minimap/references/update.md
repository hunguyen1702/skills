# Update a home repo

Run every command from the home repo root with `python3 .minimap/bin/minimap.py`. First copy `<minimap>/scripts/minimap.py` over `.minimap/bin/minimap.py`, so the home repo runs the current script, and mention it in the report when the file changed.

Read `AGENTS.md` and only the area files the job touches. Change only the parts the job needs, and show the draft of each change before writing it.

## Add repos

Follow steps 1 to 4 of `references/create.md` for the new repos only: name them, survey them, and draft where they go. While surveying, also check the existing repos' wiring towards the new ones, but only in the areas the new repos join. Then run `set <name> <path>` for each, write the approved changes, and switch to the tiered layout when the home repo passes 6 repos or one area.

## Remove repos

Find every `{{name}}` of the repo in tracked files and show the user what you would change: its block, its edges in other blocks, knowledge entries that name it. After approval, run `remove <name>` and apply the changes. A knowledge entry that only covered that repo goes too, once the user agrees.

## Rescan wiring

Ask which areas to rescan (recommend the ones the user named, or all of them when they named none). Survey their repos per `references/survey.md`, then show the difference against the current map: new edges, edges whose evidence is gone, changed descriptions. Write only what the user approves.

## Add or edit knowledge

1. Collect the content from the user, or from files they point at. Ask until you know which repos it covers and where it came from.
2. When it is about a single repo, say it belongs in that repo and ask whether to keep it here anyway.
3. Draft the entry in the knowledge format of `references/templates.md`, with `Updated` set to today. For an edit, change only what the user asked and keep the rest.
4. Add one index line in the area file of the area it covers, or in `## Knowledge` of `AGENTS.md` when it spans areas. In the flat layout, the line always goes in `AGENTS.md`.

Done when the entry and its index line exist and the user approved both.

## Finish

Run `check-paths --all` and fix every hit. Commit only when the user asks. Report each change, each warning and the user's choice, and anything skipped with the reason.
