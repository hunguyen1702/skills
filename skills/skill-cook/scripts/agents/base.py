"""Structure shared by every agent: SKILL.md, resource folders, common checks."""

import json
import re
from dataclasses import dataclass, field

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME = 64
MAX_DESCRIPTION = 1024  # strictest limit across supported agents
MAX_BODY_LINES = 500
RESOURCES = ("scripts", "references", "assets")
TODO = "[TODO:"


@dataclass
class Skill:
    name: str
    user_invoked: bool = False
    resources: list = field(default_factory=list)

    @property
    def title(self):
        return " ".join(part.capitalize() for part in self.name.split("-"))


def frontmatter(skill):
    if skill.user_invoked:
        hint = "What the skill does, written for the human who types its name"
    else:
        hint = "What the skill does and when an agent should use it, plus when not to"
    return {"name": skill.name, "description": f"{TODO} {hint}]"}


def render_skill_md(fm, skill):
    lines = ["---"]
    for key, value in fm.items():
        if isinstance(value, bool):
            value = "true" if value else "false"
        elif key != "name":
            value = json.dumps(value, ensure_ascii=False)
        lines.append(f"{key}: {value}")
    lines += [
        "---",
        "",
        f"# {skill.title}",
        "",
        f"{TODO} The steps an agent follows. Keep only what it cannot infer on its own.]",
        "",
    ]
    return "\n".join(lines)


def parse_frontmatter(text):
    """Return (top-level keys as strings, body). Keys is None without frontmatter.

    ponytail: reads flat `key: value` and block scalars only; nested maps are
    skipped. Enough for warnings; use a YAML parser if checks need nested keys.
    """
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    fm, current = {}, None
    for line in text[4:end].splitlines():
        if line[:1] in (" ", "\t"):
            if current and fm[current] is not None:
                fm[current] = (fm[current] + " " + line.strip()).strip()
            continue
        key, sep, value = line.partition(":")
        if not sep or not key.strip():
            current = None
            continue
        current = key.strip()
        value = value.strip()
        if value in ("|", ">", "|-", ">-"):
            fm[current] = ""
        elif value == "":
            fm[current] = None  # nested map; not tracked
        else:
            fm[current] = value.strip("\"'")
    body = text[end + 4 :].lstrip("\n")
    return fm, body


def validate(skill_dir, fm, body):
    if fm is None:
        return ["SKILL.md has no `---` frontmatter block at the top"]
    issues = []
    name = fm.get("name") or ""
    if not name:
        issues.append("frontmatter `name` is missing")
    else:
        if name != skill_dir.name:
            issues.append(f"`name` is `{name}` but the folder is `{skill_dir.name}`; keep them equal")
        if not NAME_RE.match(name) or len(name) > MAX_NAME:
            issues.append(f"`name` should be lowercase letters, digits and single hyphens, at most {MAX_NAME} chars")
    description = fm.get("description") or ""
    if not description:
        issues.append("frontmatter `description` is missing; agents decide to load the skill from it")
    elif TODO in description:
        issues.append("`description` still holds the scaffold placeholder")
    elif len(description) > MAX_DESCRIPTION:
        issues.append(f"`description` is {len(description)} chars; keep it under {MAX_DESCRIPTION}")
    prose = re.sub(r"`[^`\n]*`", "", re.sub(r"```.*?```", "", body, flags=re.S))
    if TODO in prose:
        issues.append("SKILL.md body still holds a `[TODO: ...]` placeholder")
    if not body.strip():
        issues.append("SKILL.md body is empty")
    if body.count("\n") > MAX_BODY_LINES:
        issues.append(f"SKILL.md body is over {MAX_BODY_LINES} lines; move detail into references/")
    return issues
