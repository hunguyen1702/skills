# minimap

Build and maintain a **home repo**: one git repo you start every agent session in, which maps the other repos you work on. Agents read the map top-down, like the minimap of a strategy game, and open an area's detail only when the task reaches it.

Inspired by [The Home Repo Pattern](https://www.aihero.dev/the-home-repo-pattern) by Matt Pocock.

## Use

```text
/minimap                      # create a home repo here, or ask what to update
/minimap create               # survey repos, review the map, then init
/minimap update add billing   # add, remove, rescan, or add knowledge
```

On Codex, call it as `$minimap`; on Pi, as `/skill:minimap`.

## What it builds

```text
<home>/
├── AGENTS.md              # rules + top-level map, always loaded
├── CLAUDE.md              # @AGENTS.md
├── repos.example          # tracked: name -> git remote
├── repos.local            # gitignored: name -> path on this machine
├── maps/<area>.md         # per-area repo blocks (tiered layout only)
├── docs/knowledge/        # cross-repo context no single repo records
└── .minimap/bin/minimap.py
```

- Docs name repos as `{{name}}` placeholders, never by path. A pre-commit hook (`minimap.py check-paths`) blocks commits that contain local paths.
- Before touching a repo, the agent runs `minimap.py load <name>`. It prints the repo's own instruction files between `=== {{name}} instructions ===` delimiters, so repo rules (a company's, for example) apply in their scope. Rules in the home `AGENTS.md` win on conflict, with a `Warning:` line.
- The skill only reads child repos; it never writes to them.
- On a new machine, `python3 .minimap/bin/minimap.py init-paths` fills `repos.local`, and `--root <dir> --clone` clones the missing repos.

Needs `python3` and `git`.
