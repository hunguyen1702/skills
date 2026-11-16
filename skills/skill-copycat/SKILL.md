---
name: skill-copycat
description: Steal the distinctive techniques from one or more skills or articles, given as URLs or file paths, into one digest grouped by source and scope, as context for this session.
disable-model-invocation: true
argument-hint: "<source>... [why you're stealing]"
---

# Skill Copycat

## 1. Read the sources

Take the sources from the invocation. If there are none, stop and ask for one. If any source cannot be read, stop and report which one. Do not continue with the rest.

For a skill, read `SKILL.md` and every file it links to. Skip files it does not link: the agent running the skill never loads them either.

## 2. Find the steals

A **steal** is something in the source that a capable agent would not do on its own. Ask of each candidate, without running anything: given the same task without the source, would a strong agent do this anyway? If yes, drop it. Prefer a few sharp steals over many weak ones.

If the user says what they like about a source or why they are stealing, rank matching steals first, but keep the others.

## 3. Write the digest

Write in the user's language. Keep technical terms and quotes in the original language. Group by source, then by scopes you name from what each source covers:

```
## <source>
### <scope>
1. **<name>**: <what it does>. Prevents: <what goes wrong without it>. Evidence: "<short verbatim quote>" (<file> › <heading>)
```

"Prevents" is your reasoned guess, not a measurement. If you cannot name a concrete failure, it is not a steal.
