---
name: lean-change
description: How to change code for a task with the least impact on the codebase. Covers what the change must reach, choosing the option with the smallest blast radius, reuse over new code, and no speculative abstractions. Use when implementing a feature, fixing a bug, or refactoring, whether on your own or when another skill such as implement loads it. Not for designing modules or writing a technical design, and not for reviewing code.
---

# Lean Change

Work like a lazy senior developer: solve the whole task with the change that disturbs the codebase least. Lazy means least impact, not fewest lines. When the user has agreed a spec, design, or plan, follow it, and apply this skill only to the choices it leaves open.

## Before you change code

List every place the change must reach: callers, tests, fixtures, config, and exports. Also list what it could break for users: data it would destroy or expose, and features that would stop working. That list is the scope. Features nobody asked for are outside it, and a vague request gets the smallest version that does the core job.

## Choose the change

Rank the options in this order. When two goals conflict, the higher one wins.

1. **Complete and correct**: the change covers the whole scope.
2. **Smallest blast radius**: the blast radius is all the logic the change affects. Prefer the option that rolls back easily, needs no multi-step migration, and leaves more important features alone. A changed signature or behaviour in code that other modules call widens the radius, and so does a caller on a money, auth, or data-write path.
3. **Reuse**: take the first source that fully works:
   - a pattern, helper, or component already in the codebase, used the way the surrounding code uses it;
   - the standard library or a platform feature, unless the project has its own;
   - a dependency the project already installs. When only a few lines are missing, write them instead of adding a dependency.
4. **Least new code**: once the scope is known, the shortest working diff wins, and deleting code beats adding it. A one-liner that needs decoding is not short.

This order settles the common cases:

- New behaviour that would add a parameter to a function in use: add a new function for it that calls the old one, and keep the old signature.
- A bug fix: fix the root cause once in the shared code, because every caller needs the fix.
- Code duplicated to keep a wide blast radius closed: allowed, marked as a shortcut.

## Shape the code

- Add an interface, abstraction layer, option, or config only when this task uses it. Leave out one that later code might use.
- Keep values in the form the platform gives them, and keep the layers, interfaces, and conventions the codebase already has.
- Code you move or merge keeps its validation and error handling.
- Comment only what the code cannot show, in one or two short sentences a reviewer understands on first read. When the reason needs a paragraph, write it where the repo keeps design notes (such as `docs/` or ADRs) and point to it in a one-line comment. When the repo has no such place, ask the user where it goes.
- Mark every shortcut with a known limit, such as duplicated code or logic that holds only up to some load, with a comment in this form: `shortcut: <the limit>, <when to upgrade>`.
- Leave one check, a small test or an assert, for non-trivial new logic such as a branch, a parser, money, security, or data writes. When the workflow running this change sets its own testing rules, follow those instead.

## Never cut

Keep validation at trust boundaries, error handling that prevents data loss, security, accessibility, and everything the user asked for.
