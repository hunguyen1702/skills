"""Agent registry. Each module exports frontmatter(skill), files(skill), validate(skill_dir, fm).

To support a new agent: add a module next to these and one entry below,
then add its sources to references/agents.md.
"""

from . import claude_code, codex

AGENTS = {"claude-code": claude_code, "codex": codex}


def select(spec):
    """Parse a comma-separated agent list; `all` selects every agent."""
    names = list(AGENTS) if spec.strip() == "all" else [s.strip() for s in spec.split(",") if s.strip()]
    unknown = [n for n in names if n not in AGENTS]
    if unknown or not names:
        raise SystemExit(f"unknown agent {unknown or spec!r}; choose from: {', '.join(AGENTS)}, all")
    return names
