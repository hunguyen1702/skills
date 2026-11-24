#!/usr/bin/env python3
"""Create a new skill folder for one or more coding agents.

Writes SKILL.md with placeholders plus each agent's extra files. Existing
files are left untouched; an existing SKILL.md stops the run.
"""

import argparse
import sys
from pathlib import Path

from agents import AGENTS, base, select


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="skill name, e.g. pdf-forms")
    parser.add_argument("--path", required=True, type=Path, help="parent folder; the skill goes to <path>/<name>")
    parser.add_argument("--agent", required=True, help=f"comma-separated: {', '.join(AGENTS)}, or all")
    parser.add_argument("--user-invoked", action="store_true", help="only the user can invoke the skill")
    parser.add_argument("--resources", default="", help=f"comma-separated: {','.join(base.RESOURCES)}")
    parser.add_argument("--link", type=Path, help="also create the symlink <link>/<name> pointing at the skill")
    args = parser.parse_args(argv)

    agents = select(args.agent)
    if not base.NAME_RE.match(args.name) or len(args.name) > base.MAX_NAME:
        raise SystemExit(f"invalid name {args.name!r}: lowercase letters, digits, single hyphens, max {base.MAX_NAME}")
    resources = [r.strip() for r in args.resources.split(",") if r.strip()]
    bad = [r for r in resources if r not in base.RESOURCES]
    if bad:
        raise SystemExit(f"unknown resources {bad}; choose from {', '.join(base.RESOURCES)}")

    skill = base.Skill(args.name, args.user_invoked, resources)
    skill_dir = args.path.expanduser().resolve() / skill.name
    if (skill_dir / "SKILL.md").exists():
        print(f"error: a skill already exists at {skill_dir}", file=sys.stderr)
        return 1

    fm = base.frontmatter(skill)
    for name in agents:
        fm.update(AGENTS[name].frontmatter(skill))
    files = {"SKILL.md": base.render_skill_md(fm, skill)}
    for name in agents:
        files.update(AGENTS[name].files(skill))

    for rel, content in files.items():
        target = skill_dir / rel
        if target.exists():
            print(f"skipped {target} (exists)")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)
        print(f"created {target}")
    for resource in resources:
        (skill_dir / resource).mkdir(parents=True, exist_ok=True)
        print(f"created {skill_dir / resource}/")

    if args.link:
        link = args.link.expanduser().resolve() / skill.name
        if link.exists() or link.is_symlink():
            print(f"skipped link {link} (exists)")
        else:
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(skill_dir, target_is_directory=True)
            print(f"linked {link} -> {skill_dir}")

    print(f"next: replace every `{base.TODO} ...]` placeholder, then run validate.py {skill_dir} --agent {','.join(agents)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
