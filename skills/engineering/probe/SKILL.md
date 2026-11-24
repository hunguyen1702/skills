---
name: probe
description: Build a throwaway prototype to verify a design idea that looks right but needs building to be sure. Use when the user or you want to check whether a state model or logic holds, explore what a UI should look like, or test whether a third-party API or library fits the system.
---

# Probe

A prototype is **throwaway code that answers a question**. The question decides the shape.

## Pick a branch

Identify which question is being answered, using the user's prompt, the surrounding code, or by asking if the user is around:

- **"Does this logic / state model feel right?"** → [LOGIC.md](LOGIC.md). Push the state model through cases that are hard to reason about on paper: a single shareable HTML file a non-developer can drive when the logic stands alone, or a runner inside the repo when it needs existing code or a database.
- **"What should this look like?"** → [UI.md](UI.md). Generate several radically different UI variations on a single route, switchable via a URL search param and a floating bottom bar.
- **"Does this API or library fit our system?"** → [SPIKE.md](SPIKE.md). Call the third-party API or library the way the system would, run it yourself, and judge the fit against criteria stated up front.

The branches produce very different artifacts, so getting this wrong wastes the whole prototype. If the question is genuinely ambiguous and the user isn't reachable, default to whichever branch better matches the surrounding code (a backend module → logic; a page or component → UI; a third-party dependency → spike) and state the assumption at the top of the prototype.

## Rules that apply to every branch

1. **Throwaway from day one, and clearly marked as such.** Build every prototype in its own git worktree on a new throwaway branch, so the user's working tree stays untouched and the prototype is ready to push. Inside it, locate the prototype code close to where it will actually be used (next to the module or page it's prototyping for) so context is obvious, but name it so a casual reader can see it's a prototype, not production. For throwaway UI routes, obey whatever routing convention the project already uses; don't invent a new top-level structure.
2. **Trivial to run.** A prototype starts from one command in the project's task runner (`pnpm <name>`, `python <path>`, `bun <path>`, etc.) run in the worktree, or it is a single HTML file the user double-clicks. Either way, no thinking required to start it.
3. **No persistence by default.** State lives in memory. Persistence is the thing the prototype is _checking_, not something it should depend on. When the prototype needs a database, ask the user first, then clone the development database into a separate copy and point the prototype at the copy. Never connect a prototype to the development database itself.
4. **Skip the polish.** No tests, no abstractions. Build only the happy path you are verifying; it may include the success and failure outcomes the question cares about, but no error handling beyond what makes the prototype _runnable_. Flag every point you are unsure of with a warning in the code and in the report. The point is to learn something fast.
5. **Surface the state.** After every action (logic), on every variant switch (UI), or after every call (spike), print or render the full relevant state so the user can see what changed.
6. **Capture it when done.** Once the question is settled, write the report, commit it with the prototype to the throwaway branch, and push the branch. The prototype is a **primary source**: point the implementation issue at that exact commit, not just the branch. Nothing from the branch merges into main; when the real task comes, reuse the prototype's approach and rewrite it to the repo's conventions. Then remove the worktree, and ask the user whether to drop any cloned database.

## Report

Write the report as a single Markdown file in the worktree. Save it where the repo already keeps such notes; match the existing convention, and if there is none, put it next to the prototype and say where. It holds:

- **Question**: the design idea or question the prototype set out to verify.
- **Prototype**: what was built and the command to run it.
- **What it proved**: each finding with the observed result behind it, citing docs or source where a finding rests on them, plus the warnings from rule 4.
- **Conclusion**: the answer to the question.

In the logic and UI branches, the conclusion is the user's verdict, so write the report only after the user has tried the prototype and said whether it fits. In the spike branch, the conclusion is yours.
