#!/usr/bin/env python3
"""File and status handling for the journal skill. The agent writes log content itself.

Commands (run from the repo root; the session id comes from the agent's environment):
  on                          turn logging on for this session
  off                         turn it off; the log stays
  new --slug SLUG --title T   create journal/<date>-<slug>.md and attach it to this session
  attach --log PATH           attach an existing log to this session (after a handoff)
  list                        list logs with their title and objective
  hook                        UserPromptSubmit hook (Claude Code, Codex): reads JSON on stdin

State lives in <repo>/journal/status.json:
  {"sessions": {"<session id>": {"active": true, "log": "journal/<file>.md" | null}}}
extensions/journal.ts reads the same format for Pi; keep the two in step.
"""

import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path

DIR = "journal"
SKILL_MD = Path(__file__).resolve().parent.parent / "SKILL.md"
SCRIPT = Path(__file__).resolve()

# Each agent exposes its session id to the shell commands the model runs.
# Each value matches the session id the agent passes to hooks or extensions.
SESSION_ENV = ("CLAUDE_CODE_SESSION_ID", "CODEX_SESSION_ID", "PI_SESSION_ID")


def session_id():
    for name in SESSION_ENV:
        if os.environ.get(name):
            return os.environ[name]
    raise SystemExit(f"no session id: none of {', '.join(SESSION_ENV)} is set")


def repo_root(start):
    path = Path(start).resolve()
    for p in (path, *path.parents):
        if (p / ".git").exists():
            return p
    return path


def status_path(root):
    return root / DIR / "status.json"


def load(root):
    try:
        data = json.loads(status_path(root).read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    data.setdefault("sessions", {})
    return data


def save(root, data):
    path = status_path(root)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    os.replace(tmp, path)


def ensure_dir(root):
    """Create journal/ and add it to .gitignore the first time."""
    (root / DIR).mkdir(exist_ok=True)
    gitignore = root / ".gitignore"
    text = gitignore.read_text() if gitignore.exists() else ""
    if not any(l.strip().strip("/") == DIR for l in text.splitlines()):
        if text and not text.endswith("\n"):
            text += "\n"
        gitignore.write_text(text + DIR + "/\n")


def update(root, session, **fields):
    ensure_dir(root)
    data = load(root)
    entry = data["sessions"].setdefault(session, {"active": True, "log": None})
    entry.update(fields)
    save(root, data)
    return entry


def template():
    """The log template is the first ```markdown block in SKILL.md, so the skill holds its only copy."""
    m = re.search(r"```markdown\n(.*?)```", SKILL_MD.read_text(), re.S)
    if not m:
        raise SystemExit(f"no ```markdown template block in {SKILL_MD}")
    return m.group(1)


def reminder(entry):
    log = entry.get("log")
    if log:
        where = f"Log: {log}."
    else:
        where = (f"No log file yet. When there is something to record, create it with "
                 f"`python3 {SCRIPT} new --slug <english-slug> --title <title>`.")
    return (f"journal is active. After replying to each user message, update the log as "
            f"{SKILL_MD} describes. {where} If you are writing a handoff document, add to it: "
            f"trigger the journal skill in the new session and continue the log at {log or '<log path>'}.")


def hook(stdin):
    event = json.loads(stdin)
    session = event.get("session_id")
    root = repo_root(event.get("cwd") or os.getcwd())
    if not session or not status_path(root).exists():
        return ""
    entry = load(root)["sessions"].get(session)
    return reminder(entry) if entry and entry.get("active") else ""


def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    if not slug:
        raise SystemExit("slug must contain ASCII letters or digits")
    return slug


def cmd_new(root, slug, title):
    ensure_dir(root)
    base = f"{datetime.date.today().isoformat()}-{slugify(slug)}"
    path, n = root / DIR / f"{base}.md", 2
    while path.exists():
        path, n = root / DIR / f"{base}-{n}.md", n + 1
    path.write_text(template().replace("{title}", title))
    rel = path.relative_to(root).as_posix()
    update(root, session_id(), active=True, log=rel)
    return rel


def cmd_attach(root, log):
    path = Path(log)
    path = (path if path.is_absolute() else root / path).resolve()
    if not path.is_file():
        raise SystemExit(f"no log file at {path}")
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        raise SystemExit(f"{path} is not inside {root}")
    update(root, session_id(), active=True, log=rel)
    return rel


def cmd_list(root):
    rows = []
    for path in sorted((root / DIR).glob("*.md")):
        lines = path.read_text().splitlines()
        title = next((l[2:].strip() for l in lines if l.startswith("# ")), "")
        title = title.removeprefix("Session Notes:").strip()
        objective = ""
        if "## Objective" in lines:
            after = lines[lines.index("## Objective") + 1:]
            objective = next((l.strip() for l in after if l.strip()), "")
            if objective.startswith("## "):
                objective = ""
        rows.append(f"{path.relative_to(root).as_posix()}\t{title}\t{objective}")
    return "\n".join(rows) if rows else "no logs"


def main(argv=None, stdin=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("on", "off", "list", "hook"):
        sub.add_parser(name)
    p = sub.add_parser("new")
    p.add_argument("--slug", required=True, help="short English slug for the file name")
    p.add_argument("--title", required=True, help="topic title, in the conversation's language")
    p = sub.add_parser("attach")
    p.add_argument("--log", required=True)
    args = parser.parse_args(argv)

    if args.cmd == "hook":
        try:
            out = hook(sys.stdin.read() if stdin is None else stdin)
        except Exception:  # a broken hook must never block the user's prompt
            out = ""
        if out:
            print(out)
        return 0

    root = repo_root(os.getcwd())
    if args.cmd == "on":
        entry = update(root, session_id(), active=True)
        print(f"journal on. Log: {entry['log'] or 'none yet'}")
    elif args.cmd == "off":
        entry = update(root, session_id(), active=False)
        print(f"journal off. Log: {entry['log'] or 'none'}")
    elif args.cmd == "new":
        print(cmd_new(root, args.slug, args.title))
    elif args.cmd == "attach":
        print(cmd_attach(root, args.log))
    else:
        print(cmd_list(root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
