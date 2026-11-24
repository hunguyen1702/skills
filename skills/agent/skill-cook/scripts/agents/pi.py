"""Pi specifics. Sources to re-check: references/agents.md#pi."""


def frontmatter(skill):
    return {"disable-model-invocation": True} if skill.user_invoked else {}


def files(skill):
    return {}


def validate(skill_dir, fm):
    # Pi drops a skill whose frontmatter has no description; base.validate already warns on that.
    return []
