#!/usr/bin/env python3
"""Self-check for journal.py. Run: python3 skills/journal/scripts/test_journal.py"""

import contextlib
import io
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import journal  # noqa: E402

for name in journal.SESSION_ENV:
    os.environ.pop(name, None)


def run(*argv, stdin=None, session="s1", env="CLAUDE_CODE_SESSION_ID"):
    for name in journal.SESSION_ENV:
        os.environ.pop(name, None)
    if session:
        os.environ[env] = session
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = journal.main(list(argv), stdin=stdin)
    return code, out.getvalue()


def hook(root, session="s1"):
    return run("hook", stdin=json.dumps({"session_id": session, "cwd": str(root / "sub"), "prompt": "x"}))[1]


def status(root):
    return json.loads((root / "journal" / "status.json").read_text())


with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp).resolve()
    (root / ".git").mkdir()
    (root / "sub").mkdir()
    (root / ".gitignore").write_text("node_modules/")
    os.chdir(root)

    # never turned on: silent, creates nothing
    assert hook(root) == ""
    assert not (root / "journal").exists()

    # no session id in the environment: refuse
    try:
        run("on", session=None)
        raise AssertionError("expected SystemExit")
    except SystemExit:
        pass

    # on: creates the folder, gitignores it once, hook reminds this session only
    run("on")
    run("on")
    assert (root / ".gitignore").read_text() == "node_modules/\njournal/\n"
    assert status(root) == {"sessions": {"s1": {"active": True, "log": None}}}
    assert "No log file yet" in hook(root)
    assert hook(root, session="s2") == ""

    # each agent's variable works
    run("on", session="codex", env="CODEX_SESSION_ID")
    run("on", session="pi", env="PI_SESSION_ID")
    assert {"codex", "pi"} <= status(root)["sessions"].keys()

    # new: creates the log from the SKILL.md template and records it
    _, rel = run("new", "--slug", "Auth Choice", "--title", "Chọn auth")
    rel = rel.strip()
    assert rel.startswith("journal/") and rel.endswith("-auth-choice.md"), rel
    text = (root / rel).read_text()
    assert text.startswith("# Session Notes: Chọn auth\n") and "## Open Questions" in text, text
    assert status(root)["sessions"]["s1"] == {"active": True, "log": rel}
    assert f"Log: {rel}" in hook(root)

    # same slug the same day gets a suffix
    _, rel2 = run("new", "--slug", "auth-choice", "--title", "x", session="s3")
    assert rel2.strip().endswith("-auth-choice-2.md"), rel2

    # off keeps the log and silences the reminder
    run("off")
    assert status(root)["sessions"]["s1"] == {"active": False, "log": rel}
    assert (root / rel).exists()
    assert hook(root) == ""

    # attach after handoff: new session continues the old log
    _, attached = run("attach", "--log", rel, session="s4")
    assert attached.strip() == rel
    assert f"Log: {rel}" in hook(root, session="s4")

    # list shows title and objective
    (root / rel).write_text(text.replace("## Objective\n", "## Objective\nPick an auth provider.\n"))
    _, listing = run("list")
    assert f"{rel}\tChọn auth\tPick an auth provider." in listing, listing

    # bad input never breaks the hook
    assert run("hook", stdin="not json") == (0, "")

print("ok")
