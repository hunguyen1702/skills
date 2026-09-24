#!/usr/bin/env python3
"""Validate portable plugin structure, metadata, links, and neutrality."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT
SKILL = ROOT / "skills" / "adaptive-planning"
FORBIDDEN = (
    "the-broke-task-management",
    "the broke task management",
    "tbtm",
    "tbtm-core",
    "tbtm-cli",
    "/users/hungnguyen",
    "cargo run -p",
    "cargo workspace",
    "rust 2024",
    "clap",
    "sqlite",
    "migration",
    "docs/status.md",
    "docs/epics",
    "docs/tasks",
    ".harness",
    "agent register",
    "e1-s1",
)
NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK = re.compile(r"\[[^]]+\]\(([^)]+)\)")


def fail(message: str) -> None:
    raise ValueError(message)


def validate_frontmatter(path: Path, expected_name: str) -> None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        fail(f"invalid frontmatter: {path}")
    frontmatter = text.split("---\n", 2)[1]
    fields: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if not line.strip() or line.startswith((" ", "\t")) or ":" not in line:
            fail(f"unsupported skill frontmatter line in {path}: {line!r}")
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    if fields.get("name") != expected_name or not fields.get("description"):
        fail(f"missing skill metadata: {path}")
    if not NAME.fullmatch(fields["name"]) or len(fields["name"]) > 64:
        fail(f"invalid skill name: {fields['name']}")


def validate_links(package: Path) -> None:
    for markdown in package.rglob("*.md"):
        for target in LINK.findall(markdown.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            resolved = (markdown.parent / target.split("#", 1)[0]).resolve()
            if not resolved.is_relative_to(package.resolve()) or not resolved.exists():
                fail(f"invalid or out-of-package link {target!r} in {markdown}")


def validate_no_symlinks(package: Path) -> None:
    for path in package.rglob("*"):
        if path.is_symlink():
            fail(f"symlink is not allowed: {path}")


def validate_neutrality(package: Path) -> None:
    for path in package.rglob("*"):
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8").lower()
        for term in FORBIDDEN:
            if term in content:
                fail(f"forbidden source-specific term {term!r} in {path}")


def validate_claude_metadata() -> None:
    plugin = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    required = ("name", "version", "description", "author")
    if any(key not in plugin for key in required):
        fail("Claude plugin metadata is incomplete")
    if plugin["name"] != "hungnguyen-skills" or not NAME.fullmatch(plugin["name"]):
        fail("root plugin identity must be hungnguyen-skills")
    version_pattern = r"\d+\.\d+\.\d+(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    if not re.fullmatch(version_pattern, plugin["version"]):
        fail("Claude plugin version is not semver")
    if not isinstance(plugin["author"], dict) or not plugin["author"].get("name"):
        fail("Claude plugin author is invalid")

    marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    entries = marketplace.get("plugins")
    if marketplace.get("name") != "hungnguyen-skills" or not isinstance(entries, list):
        fail("marketplace identity is invalid")
    expected = {"name": "hungnguyen-skills", "source": "./"}
    if len(entries) != 1 or any(entries[0].get(key) != value for key, value in expected.items()):
        fail("marketplace must expose the root hungnguyen-skills plugin")


def validate_codex_metadata() -> None:
    lines = (SKILL / "openai.yaml").read_text(encoding="utf-8").splitlines()
    text = "\n".join(lines)
    required = (
        'display_name: "Adaptive Planning"',
        'short_description: "Route requirements into confirmed plans"',
        'default_prompt: "Use $adaptive-planning',
        "allow_implicit_invocation: true",
    )
    for value in required:
        if value not in text:
            fail(f"invalid Codex metadata; missing {value!r}")
    for line in lines:
        stripped = line.strip()
        if ":" in stripped and not stripped.endswith(("true", "false")):
            _, value = stripped.split(":", 1)
            if value.strip() and not (value.strip().startswith('"') and value.strip().endswith('"')):
                fail(f"Codex metadata strings must be quoted: {line!r}")


def main() -> int:
    required = (
        PLUGIN / ".claude-plugin" / "plugin.json",
        PLUGIN / ".claude-plugin" / "marketplace.json",
        SKILL / "SKILL.md",
        SKILL / "openai.yaml",
    )
    for path in required:
        if not path.is_file():
            fail(f"missing required file: {path}")
    validate_claude_metadata()
    validate_codex_metadata()
    validate_frontmatter(SKILL / "SKILL.md", "adaptive-planning")
    validate_no_symlinks(SKILL)
    validate_links(SKILL)
    validate_neutrality(SKILL)
    print("Portable plugin structure, links, metadata, and neutrality are valid.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1)
