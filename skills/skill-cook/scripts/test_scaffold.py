#!/usr/bin/env python3
"""Self-check for scaffold.py and validate.py. Run: python scripts/test_scaffold.py"""

import contextlib
import io
import tempfile
from pathlib import Path

import scaffold
import validate


def run(fn, *argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        code = fn(list(argv))
    return code, out.getvalue()


def fill(skill_dir):
    md = skill_dir / "SKILL.md"
    text = md.read_text()
    text = text.replace(next(l for l in text.splitlines() if l.startswith("description:")), "description: Fills PDF forms.")
    text = text.split("# ")[0] + "# Demo\n\nRead the form, fill the fields.\n"
    md.write_text(text)
    yaml = skill_dir / "agents" / "openai.yaml"
    if yaml.exists():
        yaml.write_text(yaml.read_text().replace(
            next(l for l in yaml.read_text().splitlines() if "short_description" in l),
            '  short_description: "Fill PDF forms from structured data"'))


with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)

    # both agents, user-invoked, with link and resources
    code, out = run(scaffold.main, "demo", "--path", str(root / "agents-dir"), "--agent", "all",
                    "--user-invoked", "--resources", "scripts,references", "--link", str(root / "claude-dir"))
    skill = (root / "agents-dir" / "demo").resolve()
    assert code == 0, out
    md = (skill / "SKILL.md").read_text()
    assert "name: demo" in md and "disable-model-invocation: true" in md
    assert "allow_implicit_invocation: false" in (skill / "agents" / "openai.yaml").read_text()
    assert (skill / "scripts").is_dir() and (skill / "references").is_dir()
    assert (root / "claude-dir" / "demo").is_symlink()

    # placeholders produce warnings; filled skill is clean
    _, out = run(validate.main, str(skill), "--agent", "all")
    assert "placeholder" in out, out
    fill(skill)
    _, out = run(validate.main, str(skill), "--agent", "all")
    assert "ok: no warnings" in out, out

    # broken invocation pairing is reported by the codex module
    yaml = skill / "agents" / "openai.yaml"
    yaml.write_text(yaml.read_text().replace("allow_implicit_invocation: false", "allow_implicit_invocation: true"))
    _, out = run(validate.main, str(skill), "--agent", "codex")
    assert "set both or neither" in out, out

    # existing SKILL.md stops the run and leaves files alone
    before = (skill / "SKILL.md").read_text()
    code, out = run(scaffold.main, "demo", "--path", str(root / "agents-dir"), "--agent", "codex")
    assert code == 1 and "already exists" in out
    assert (skill / "SKILL.md").read_text() == before

    # claude-only, model-invoked: no openai.yaml, no invocation key
    code, _ = run(scaffold.main, "solo", "--path", str(root), "--agent", "claude-code")
    assert code == 0
    assert not (root / "solo" / "agents").exists()
    assert "disable-model-invocation" not in (root / "solo" / "SKILL.md").read_text()

    # pi-only, user-invoked: same frontmatter key as Claude Code, no metadata file
    code, _ = run(scaffold.main, "pi-solo", "--path", str(root), "--agent", "pi", "--user-invoked")
    assert code == 0
    assert "disable-model-invocation: true" in (root / "pi-solo" / "SKILL.md").read_text()
    assert not (root / "pi-solo" / "agents").exists()

    # bad input is rejected
    for argv in (["Bad_Name", "--path", tmp, "--agent", "codex"], ["ok", "--path", tmp, "--agent", "cursor"]):
        try:
            run(scaffold.main, *argv)
            raise AssertionError(f"accepted {argv}")
        except SystemExit:
            pass

print("ok")
