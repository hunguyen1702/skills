#!/usr/bin/env python3
"""Self-check for run_trigger helpers. Run: python3 scripts/test_run_trigger.py"""

import tempfile
from pathlib import Path

import run_trigger

with tempfile.TemporaryDirectory() as tmp:
    source = Path(tmp) / "demo"
    (source / "evals").mkdir(parents=True)
    (source / "SKILL.md").write_text("---\nname: demo\ndescription: |\n  old text\n  more\nmetadata: x\n---\n\nBody\n")
    (source / "evals" / "private.json").write_text("{}")

    root = Path(tmp) / "root"
    probe, folder = run_trigger.install_variant(source, root, "codex", "new text")
    text = (folder / "SKILL.md").read_text()
    assert probe.startswith("demo-probe-")
    assert folder == root / ".agents" / "skills" / probe
    assert f"name: {probe}" in text and 'description: "new text"' in text
    assert "old text" not in text and "metadata: x" in text and "Body" in text
    assert not (folder / "evals").exists()

    probe, folder = run_trigger.install_variant(source, root, "claude-code", "new text")
    assert folder == root / ".claude" / "skills" / probe

items = [{"query": str(i), "should_trigger": i % 2 == 0} for i in range(10)]
train, test = run_trigger.split(items, 0.4, 1)
assert len(train) + len(test) == 10
assert {x["should_trigger"] for x in test} == {True, False}

print("ok")
