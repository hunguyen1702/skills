---
name: gkg
description: How to use GitLab Knowledge Graph (gkg) CLI and its MCP tools (list_projects, search_codebase_definitions, index_project, get_references, read_definitions, get_definition, repo_map) for fast codebase search, definition lookup, and reference finding. Use this skill whenever the user asks to search a codebase for functions/classes/definitions, find references/callers of a symbol, get a repo map, or mentions "gkg", "knowledge graph", "gkg index", "gkg server", or MCP tools like search_codebase_definitions/get_references/repo_map — even if they don't name gkg explicitly and just describe the task (e.g. "where is this function used", "map this repo", "find all callers"). Also use before calling any gkg MCP tool to make sure server is running and project is indexed first.
---

# gkg — Knowledge Graph CLI + MCP tools

gkg build queryable graph of codebase (funcs, classes, refs). Use MCP tools for search/lookup — much cheaper token-wise than grep whole repo.

## Golden rule: check before use

gkg MCP tools (`search_codebase_definitions`, `get_references`, `read_definitions`, `get_definition`, `repo_map`) need three things ready first: **MCP server registered with your agent**, **gkg server running**, **project indexed**. Skip check, tool call fail, error out, or return empty/stale data. Always verify before real work:

0. **Registration check** — look at your own tool list for `list_projects`/`search_codebase_definitions`/etc (may show as `mcp__gkg__*`). Not there?
   - `gkg server start --detached` (start it first, registration needs it up)
   - `claude mcp add --transport http gkg http://localhost:27495/mcp` (Claude Code specific; other agents/IDEs register similarly per their own MCP config docs)
   - New tools usually need fresh session/reconnect to show up — tell user to restart session, don't loop retrying same turn.
   - No MCP tools available at all and can't register (no `claude mcp` or equivalent)? Fall back to CLI only — `gkg index`/`server`/`remove`/`clean` still work standalone, just no search/lookup, that part's MCP-only.

1. **Server check** — call `list_projects` MCP tool. No MCP tool available? A bare `curl http://localhost:27495/mcp` GET is **not** a reliable check — it can read as connection-refused even when the server's fine, because the endpoint needs a real request. Use:
   ```
   curl -s -m 3 -X POST http://localhost:27495/mcp \
     -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
     -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"check","version":"1.0"}}}'
   ```
   Any real JSON-RPC response (even an error like `406`/`Unexpected message`) means the server's up. Only an actual connection failure (curl exit 7, "Connection refused") means it's down.
   - Down → `gkg server start --detached`, wait ~2s, retry.
   - `gkg server stop` can report `Error: No running server found` right after a confirmed-running server (state-tracking flakiness, not a real "already stopped" signal) — if you just saw it running (`ps aux | grep gkg`, `lsof -i :27495`), don't trust the stop error blindly; check the port before assuming it's dead.

2. **Index check** — look at `list_projects` result `projects[]`. Current project's absolute path in list?
   - Not there (or project brand new / code changed a lot) → index it. **Critical gotcha**: `gkg index <path>` treats `<path>` as a **workspace to scan for git repos underneath it** — it does NOT register the repo if you point it directly at the repo's own root. Indexing a repo root directly "succeeds" (exit 0, no error) but silently produces `repo_count: 0` and the project never becomes queryable — a real trap, not documented in `--help`. Always index the repo's **parent directory** instead:
     ```
     gkg index <parent-dir-containing-the-git-repo>
     ```
     or MCP tool `index_project` with `project_absolute_path` set to the repo path (that one does take the repo path directly, unlike the CLI). The target dir must also be inside a git repo (`.git` present) — gkg only registers git repos as "projects."
   - No MCP tools to call `list_projects`? Check `~/.gkg/gkg_manifest.json` directly — look for your project's path under some workspace-folder's `"projects"` map with `"status": "indexed"`. `"status": "pending"` with empty `"projects": {}` means it didn't actually index (see gotcha above).
   - Wait for stats/manifest to show real numbers (nonzero `Total Definitions`) before continuing — don't fire search on a half-built or failed index.

3. **Now** run whatever MCP tool user actually needed (search, get_references, repo_map, etc). If `get_references` comes back suspiciously empty for something you can see is clearly referenced in the source, don't take it as ground truth — cross-check with `search_codebase_definitions` + `read_definitions`, or a quick direct read; the reference graph has occasionally missed real callers.

Skip step 1+2 only if you already confirmed server+index this session (don't re-check every single call, just once per project per session — re-check if a call comes back empty/error mid-session, that's signal state changed, e.g. server got stopped).

Note: `gkg index` and `gkg remove`/`gkg clean` need server **stopped** first (`gkg server stop`) — opposite direction from MCP flow above. If doing raw reindex via CLI instead of `index_project` MCP tool, stop server, index, restart server.

## CLI commands

| Command | Use | Key flags |
|---|---|---|
| `gkg index [WORKSPACE_PATH]` | build/rebuild graph from repo(s) found **under** `WORKSPACE_PATH` (point at the parent dir, not the repo root — see Golden Rule step 2). Langs: Ruby, Python, Java, TS/JS, Kotlin. Server must be stopped first. | `-t/--threads` worker count · `-v/--verbose` per-file log · `--stats` counts+timing |
| `gkg server start` | long-running HTTP server: web UI, HTTP API, SSE, file watch, MCP endpoints | `--register-mcp <FILE>` register into AI tool config (e.g. `~/.gitlab/duo/mcp.json`) · `--enable-reindexing` auto rewatch+reindex on file change (Ruby not supported yet) · `--detached` background mode |
| `gkg server stop` | graceful shutdown (SIGINT/SIGTERM/Ctrl+C also work) | — |
| `gkg remove --workspace <PATH>` | delete one whole workspace + its projects | conflicts w/ `--project` |
| `gkg remove --project <PATH> --workspace-folder <PATH>` | delete single project | both flags required together |
| `gkg clean` | wipe ALL indexed data (logs kept). Use when upgrading gkg. | none |

Server default port: `27495`. Web UI + API + MCP all live there.

## MCP tools

| Tool | Params | Returns | When |
|---|---|---|---|
| `list_projects` | none | `projects[]` (`project_path`) | don't know project roots, or checking server/index state (see Golden Rule) |
| `search_codebase_definitions` | `project_absolute_path` (req), `search_terms` string[] (req), `page` (opt, default 1) | `definitions[]`, `next_page?`, `system_message` | find funcs/classes/methods/constants/interfaces by name/keyword |
| `index_project` | `project_absolute_path` (req) | `stats`, `system_message?` | build/rebuild index for one project, via MCP instead of CLI |
| `get_references` | `definition_name` (req), `file_path` (req), `page` (opt) | `definitions[]`, `next_page?`, `system_message` | find every caller/usage of a definition codebase-wide |
| `read_definitions` | `definitions[]` (req): `{names[], file_path}` | `definitions[]` w/ full `definition_body`, `system_message` | batch-read full source of multiple known definitions, cheap on tokens |
| `get_definition` | `file_path` (req), `line` (req), `symbol_name` (req) | `definitions[]` (Definition or ImportedSymbol), `system_message?` | jump straight to def of a symbol used at specific call site |
| `repo_map` | `project_absolute_path` (req), `relative_paths[]` (req), `depth` (opt 1-3), `show_directories`/`show_definitions` (opt, default true), `page`/`page_size` (opt) | XML: dir tree + file defs + `system_message` | quick API-shaped overview of a repo segment, way cheaper than reading every file |

## Config

`~/.gkg/mcp.settings.json` (override path w/ `--mcp-configuration-path`) — disable individual tools:
```json
{ "disabled_tools": ["tool_name_1"] }
```

## Typical flow example

User: "find all callers of `process_payment` in /path/to/proj"

1. `list_projects` → project not listed → not indexed.
2. `gkg server start --detached` (if server also down) → wait → confirm via `list_projects` again.
3. `index_project` (`project_absolute_path: /path/to/proj`) — MCP tool takes the repo path directly, fine. (Doing this via CLI instead: `gkg index /path/to` — the **parent** dir, not `/path/to/proj` itself.) → wait for stats.
4. `search_codebase_definitions` (`search_terms: ["process_payment"]`) → get `file_path` of def.
5. `get_references` (`definition_name: "process_payment"`, `file_path: <found path>`) → answer. If it comes back empty despite an obvious caller in source, cross-check with a direct read before trusting it.
