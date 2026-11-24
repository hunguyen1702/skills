---
name: code-review
description: "Review the changes since a fixed point (commit, branch, tag, or merge-base, pr) against a spec, coding standards, correctness, and security."
---

Four-axis review of the diff between `HEAD` and a fixed point the user supplies:

- **Standards**: does the code conform to this repo's documented coding standards?
- **Spec**: does the code faithfully implement the originating issue / spec?
- **Correctness**: does it give the right result, keep data safe, hold at the expected load, and test its risky logic?
- **Security**: does it add a vulnerability an attacker could exploit?

Each axis runs as a **parallel sub-agent** with a fresh context window, so they don't pollute each other's context; then this skill aggregates their findings. If you cannot start sub-agents, run the axes yourself one after another, finishing each axis's report before starting the next.

The issue tracker should have been provided to you. If `docs/agents/issue-tracker.md` is missing, tell the user to run the "setup-hungnguyen-skills" skill.

## Process

### 1. Pin the fixed point

Whatever the user said is the fixed point (a commit SHA, branch name, tag, `main`, `HEAD~5`, etc.). If they didn't specify one, ask for it.

Capture the diff command once: `git diff <fixed-point>...HEAD` (three-dot, so the comparison is against the merge-base). Also note the list of commits via `git log <fixed-point>..HEAD --oneline`.

Before going further, confirm the fixed point resolves (`git rev-parse <fixed-point>`) and the diff is non-empty. A bad ref or empty diff should fail here, not inside four parallel sub-agents.

### 2. Identify the spec source

Look for the originating spec, in this order:

1. Issue references in the commit messages (`#123`, `Closes #45`, GitLab `!67`, etc.), fetched via the workflow in `docs/agents/issue-tracker.md`.
2. A path the user passed as an argument.
3. A spec file under `docs/`, `specs/`, or `.scratch/` matching the branch name or feature.
4. If nothing is found, ask the user where the spec is. If they say there isn't one, the **Spec** sub-agent will skip and report "no spec available".

### 3. Identify the standards sources

Anything in the repo that documents how code should be written, such as `CODING_STANDARDS.md` or `CONTRIBUTING.md`.

On top of whatever the repo documents, the Standards axis always carries the **smell baseline** below: a fixed set of Fowler code smells (_Refactoring_, ch.3) plus a few lean checks, which applies even when a repo documents nothing. Two rules bind it:

- **The repo overrides.** A documented repo standard always wins; where it endorses something the baseline would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"), never a hard violation. Like any standard here, skip anything tooling already enforces.

Each smell reads _what it is_ → _how to fix_; match it against the diff:

- **Mysterious Name**: a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design's murky.
- **Duplicated Code**: the same logic shape appears in more than one hunk or file in the change. → extract the shared shape, call it from both.
- **Feature Envy**: a method that reaches into another object's data more than its own. → move the method onto the data it envies.
- **Data Clumps**: the same few fields or params keep travelling together (a type wanting to be born). → bundle them into one type, pass that.
- **Primitive Obsession**: a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
- **Repeated Switches**: the same `switch`/`if`-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery**: one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
- **Divergent Change**: one file, module, or function is changed for several unrelated reasons. → split so each changes for one reason; split by job, never by line count.
- **Speculative Generality**: abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
- **Message Chains**: long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
- **Middle Man**: a class or function that mostly just delegates onward. → cut it, call the real target direct.
- **Refused Bequest**: a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.
- **Dead Code**: code, options, or branches the change adds that nothing reaches. → delete it.
- **Reinvented Helper**: new code that repeats a helper the repo already has. → call the existing helper; name its path.
- **Reinvented Stdlib**: new code, or a new dependency, for what the standard library or platform already does. → use the built-in.

### 4. Spawn the four sub-agents in parallel

Every sub-agent prompt includes the diff command, the commit list, and the **Finding format** section below pasted in full. Each brief also carries the axis-specific material below.

**Standards sub-agent**:

- The standards-source files you found in step 3, **plus the smell baseline from step 3** pasted in full (the sub-agent has no other access to it).
- The brief: "Report every place the diff violates a documented standard, citing the standard (file + the rule), and every baseline smell you spot, naming it. A documented-standard breach is at most 🟡; a baseline smell is 🟡 or 🔵, never 🔴. A documented repo standard overrides the baseline. Skip anything tooling enforces. Under 400 words."

**Spec sub-agent**:

- The path or fetched contents of the spec.
- The brief: "Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong. Quote the spec line for each finding. Under 400 words."

If the spec is missing, skip the Spec sub-agent and note this under `Not checked:` in the final report.

**Correctness sub-agent**:

- The brief: "Review like the developer who gets paged when this breaks. Read past the diff: the callers of every changed function, the functions it calls, and its tests. When a signature, return value, or behaviour changes, find every caller, because the change can break code it does not touch. Find the expected load in the repo (README, deploy config): one person running a script, or many users and processes at once; judge scale against it and state the load you assumed. Report:
  - **Bug**: wrong result, crash, a missed edge case (empty, zero, last item, rounding, time zones), a caller broken by the change, a fix applied in one caller while the shared function stays broken.
  - **Data loss**: errors swallowed, writes in the wrong order, a multi-step write with no transaction.
  - **Scale**: check-then-write races, the same work done by every process, memory or lists that only grow, a query per item, O(n²) on big input, per-process state that must be shared.
  - **Missing test**: risky new logic (a branch, a parser, money, security, data writes, a bug fix) with no test that fails when it breaks. Ask for one good test, not coverage.
  - **Speed**: a big slowdown is 🟡 or 🔴; a small win, such as work repeated in a hot loop, is 🔵.

  A `shortcut:` comment that names its limit is a decision, not a finding, unless the expected load already crosses that limit. Under 400 words."

**Security sub-agent**:

- `references/security.md` pasted in full.
- The brief: "Report only vulnerabilities this diff adds, not ones already in the code. Follow the method, exclusions, and precedents in the reference, and give each finding a confidence score. Report only findings scored 8 or higher, in the security form of the Finding format."

### 5. Verify the security findings

If the Security sub-agent reported findings, start one more sub-agent with a fresh context window to filter them. It did not find them, so it judges them without the finder's bias. Give it the diff command, the findings, and `references/security.md` pasted in full. Brief: "Re-read the code behind each finding and score it again against the exclusions, precedents, and confidence scale. Return the findings scored 8 or higher, unchanged except for the score." Done when every finding has a second score; keep only those scored 8 or higher.

### 6. Aggregate

Present the reports under `## Standards`, `## Spec`, `## Correctness`, and `## Security`, verbatim or lightly cleaned. Number the findings continuously across all four sections, so the user can say "fix 2 and 5". Do **not** merge or rerank findings across axes (see _Why separate axes_). Skip a section with no findings.

End with:

- `Verdict: Ship.` when there is no 🔴 finding, otherwise `Verdict: fix <numbers of every 🔴 finding> first.`
- `Not checked:` one line naming anything that mattered and could not be checked, such as a missing spec or an unknown expected load. Omit it when nothing is missing.

## Finding format

Write each finding the way a colleague comments on a PR: short, direct, no throat-clearing.

Severity is an icon:

- 🔴 **must**: bug, security High, data loss, or breaks at the expected load.
- 🟡 **should**: risky code without a test, real slowness, duplication, a function that mixes jobs, code that should not exist, security Medium.
- 🔵 **nit**: small speed-up, shorter form, light smell. The author can ignore it.
- ❓ **q**: a genuine question. When unsure whether something is a problem, ask with ❓ instead of hedging a finding.

A normal finding is one line, plus at most one line of why or what happens if it is skipped, written only when the fix doesn't make that obvious:

```
🔴 `billing/close_day.py:L40`: "today" comes from the UTC server clock, so an order at 00:30 Berlin time is billed to the day before. Use `datetime.now(ZoneInfo("Europe/Berlin")).date()`.
   Skipping it means accounting fixes late orders by hand.
```

A security finding uses the full form, since its author needs the attack to judge the risk:

```
🔴 High · `xss` · `foo.py:L42`
- Description: `username` from the query string is interpolated into HTML without escaping.
- Exploit scenario: an attacker sends `/bar?q=<script>alert(document.cookie)</script>`, runs script in the victim's browser, and steals the session.
- Recommendation: render through Jinja2 with auto-escaping, or call `escape()`.
- Confidence: 9/10
```

The `file:L<n>` location serves this chat report. When findings are later posted as inline PR comments, the comment already sits on that line, so leave the location out of the comment body.

Every finding:

- Names a concrete case: the input or situation that leads to the wrong result. With no case, drop the finding or turn it into ❓.
- Is confirmed against the code: the caller exists, the value can really be empty, the code really is unused.
- Names exact symbols in backticks and gives a concrete fix. Propose the smallest fix that works, and prefer one that deletes code.
- Leaves out what the reader can see in the diff, such as a restatement of what the line does.

## Why separate axes

A change can pass one axis and fail another:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the issue asked but breaks the project's conventions → **Spec pass, Standards fail.**
- Code that matches spec and standards but double-charges under concurrent requests → **Correctness fail.**
- Code that works for every honest user but lets one user read another's data → **Security fail.**

Reporting them separately stops one axis from masking another.
