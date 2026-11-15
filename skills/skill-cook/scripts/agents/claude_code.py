"""Claude Code specifics. Sources to re-check: references/agents.md#claude-code."""

import re

MAX_TRIGGER_TEXT = 1536  # description + when_to_use


def frontmatter(skill):
    return {"disable-model-invocation": True} if skill.user_invoked else {}


def files(skill):
    return {}


def validate(skill_dir, fm):
    issues = []
    trigger = len(fm.get("description") or "") + len(fm.get("when_to_use") or "")
    if trigger > MAX_TRIGGER_TEXT:
        issues.append(f"`description` + `when_to_use` is {trigger} chars; Claude Code truncates past {MAX_TRIGGER_TEXT}")
    yaml = skill_dir / "agents" / "openai.yaml"
    if yaml.exists():
        implicit_off = re.search(r"^\s*allow_implicit_invocation:\s*false\b", yaml.read_text(), re.M)
        if implicit_off and fm.get("disable-model-invocation") != "true":
            issues.append("openai.yaml blocks implicit invocation but SKILL.md lacks `disable-model-invocation: true`; set both or neither")
    return issues
