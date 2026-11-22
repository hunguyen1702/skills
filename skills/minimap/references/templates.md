# Home repo file formats

Write every file in these formats, in English, so each run produces the same layout and the agent can grep it.

## Layout

Use the **flat** layout when the home repo maps 6 repos or fewer in a single area: the repo blocks sit in `AGENTS.md` under `## Map`, and there is no `maps/` folder. Use the **tiered** layout otherwise:

```text
<home>/
├── AGENTS.md              # always loaded: rules, then one line per area
├── CLAUDE.md              # only the line @AGENTS.md
├── repos.example          # tracked: name: <git remote>
├── repos.local            # gitignored: name: <absolute path>
├── .gitignore
├── maps/
│   └── <area>.md          # one file per area: repo blocks and the area's knowledge index
├── docs/knowledge/
│   └── <topic>.md         # one file per topic
└── .minimap/bin/minimap.py
```

Switch from flat to tiered when a change pushes the home repo past 6 repos or past one area.

## AGENTS.md

Keep `## Rules` word for word; it is what makes every session load child rules and protect paths. The user may add rules below rule 5.

```markdown
# Home repo

This repo holds no product code. It maps the repos below so you can work across them from one place.

## Rules

1. `{{name}}` is a placeholder for a repo. Resolve it with `python3 .minimap/bin/minimap.py status`. Never write a local path into a tracked file.
2. Before you read or edit anything in a repo, run `python3 .minimap/bin/minimap.py load <name>` and follow the instructions it prints. If the repo is not on this machine, ask the user where to clone it.
3. Inside a repo, its own rules apply, except where a rule in this file says otherwise. When a rule here overrides a repo rule, first print:
   `Warning: {{name}} rule "<repo rule>" conflicts with home rule "<home rule>". Following the home rule.`
4. Read the map top-down. Open an area file only when the task reaches that area, and a knowledge entry only when the task touches its topic.
5. Add new repos and knowledge through the minimap skill, so paths stay out of git.

## Map

- **<area>** (<what the area is, a few words>): {{a}}, {{b}}. See `maps/<area>.md`.
- **<nested area>** (nested home repo; loads its own rules and map): {{platform}}. Run `load platform`, then follow its `AGENTS.md`.
- **standalone** (no wiring to other repos): {{blog}}. See `maps/standalone.md`.

## Knowledge

- `docs/knowledge/<topic>.md`: <one line; only entries that span areas>
```

In the flat layout, `## Map` holds the repo blocks from the area file below instead of the area lines.

## CLAUDE.md

```markdown
@AGENTS.md
```

Claude Code imports the file through this line; Codex and Pi read `AGENTS.md` directly.

## maps/<area>.md

```markdown
# <area>

<One or two sentences on how the repos in this area work together.>

## {{wallet}}

- Does: Coin wallet service and the user balance API.
- Stack: Go, Postgres.
- Wiring:
  - Calls {{signer}} over gRPC to sign withdrawals. Evidence: `proto/signer.proto:12`
  - Publishes `deposit.confirmed` events that {{exchange}} reads. (unverified)
- Hint: Deploy before {{exchange}} when the event schema changes.

## Knowledge

- `docs/knowledge/withdraw-flow.md`: a withdrawal from user request to on-chain broadcast.
```

Keep the field order Does, Stack, Wiring, Hint. Leave out a field that has nothing; never write "N/A". Hint holds only what the user told you or what the repo's own docs say.

## docs/knowledge/<topic>.md

```markdown
# <Topic>

Repos: {{wallet}}, {{signer}}
Updated: <YYYY-MM-DD>
Source: <"user", or the files it came from>

<Body>
```

Knowledge holds what no single repo records about itself: flows that cross repos, deploy order, who owns what, traps found the hard way. A fact about one repo alone belongs in that repo. When the user offers one, say so and ask before writing it here.
