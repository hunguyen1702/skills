#!/usr/bin/env python3
"""Check a skill folder against the shared structure and each target agent's rules.

Prints warnings only and always exits 0: the agent reads them and decides
what to fix.
"""

import argparse
import sys
from pathlib import Path

from agents import AGENTS, base, select


def check(skill_dir, agents):
    """Return a list of (scope, message) warnings."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [("common", f"no SKILL.md in {skill_dir}")]
    fm, body = base.parse_frontmatter(skill_md.read_text())
    issues = [("common", m) for m in base.validate(skill_dir, fm, body)]
    for name in agents:
        issues += [(name, m) for m in AGENTS[name].validate(skill_dir, fm or {})]
    return issues


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", type=Path)
    parser.add_argument("--agent", required=True, help=f"comma-separated: {', '.join(AGENTS)}, or all")
    args = parser.parse_args(argv)

    issues = check(args.skill_dir.expanduser().resolve(), select(args.agent))
    for scope, message in issues:
        print(f"warning [{scope}] {message}")
    if any(scope != "common" for scope, _ in issues):
        print("note: agent rules change often; confirm agent warnings against references/agents.md before fixing")
    if not issues:
        print("ok: no warnings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
