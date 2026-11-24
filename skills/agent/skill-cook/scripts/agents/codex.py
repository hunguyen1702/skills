"""Codex specifics. Sources to re-check: references/agents.md#codex."""

import json
import re

from .base import TODO

SHORT_DESCRIPTION = (25, 64)  # Codex guideline for the skill list, not a parser limit


def frontmatter(skill):
    return {}


def files(skill):
    lines = [
        "interface:",
        f"  display_name: {json.dumps(skill.title)}",
        f'  short_description: "{TODO} {SHORT_DESCRIPTION[0]}-{SHORT_DESCRIPTION[1]} chars for the Codex skill list]"',
    ]
    if skill.user_invoked:
        lines += ["policy:", "  allow_implicit_invocation: false"]
    return {"agents/openai.yaml": "\n".join(lines) + "\n"}


def validate(skill_dir, fm):
    path = skill_dir / "agents" / "openai.yaml"
    if not path.exists():
        return ["agents/openai.yaml is missing; Codex has no display name or invocation policy for the skill"]
    text = path.read_text()
    issues = []
    if TODO in text:
        issues.append("agents/openai.yaml still holds a `[TODO: ...]` placeholder")
    short = re.search(r"^\s*short_description:\s*(.+)$", text, re.M)
    if short:
        length = len(short.group(1).strip().strip("\"'"))
        low, high = SHORT_DESCRIPTION
        if TODO not in short.group(1) and not low <= length <= high:
            issues.append(f"`short_description` is {length} chars; Codex suggests {low}-{high}")
    implicit_off = re.search(r"^\s*allow_implicit_invocation:\s*false\b", text, re.M)
    if fm.get("disable-model-invocation") == "true" and not implicit_off:
        issues.append("SKILL.md sets `disable-model-invocation: true` but openai.yaml lacks `policy.allow_implicit_invocation: false`; set both or neither")
    return issues
