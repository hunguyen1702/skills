# Improving skills

Use these standards when changing a skill.

## Keep only lines that change behavior

- Assume a capable model can do simple work without instruction.
- Remove anything the model would infer or do correctly by default.
- Keep project-specific facts, non-obvious pitfalls, exact formats, and decisions the agent would otherwise get wrong.
- Point to sources for facts that change often, such as CLI flags, APIs, schemas, and versions. Tell the agent to look them up.

## Fix causes, not examples

- Generalise from feedback. A fix should help future prompts, not only the test case.
- Read transcripts as well as outputs. Remove instructions that cause wasted work.
- Explain why a step matters. Reserve absolute language for correctness or safety.
- When every run reinvents the same helper or multi-step process, bundle it as a script and tell the skill when to use it.
- Keep one source of truth. Move branch-specific detail into a reference and point to it from the step that needs it.

## Description changes

- Model-invoked skills need what the skill does, when to use it, and a boundary for close misses.
- User-invoked skills need a short human-facing description.
- Keep the description specific. Do not add unrelated trigger words to win a test query.
