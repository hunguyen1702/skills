---
name: commit-changes
description: Group the current changes into commits, stage each group, and write Conventional Commits messages in English. Use when you or the user are about to commit work in a git repo, whether it fits one commit or needs splitting into several. Not for PR bodies, changelogs, or release notes.
---

# Commit Changes

This skill turns the current changes into commits: it stages files, writes each message, and creates the commits. Anything beyond that, such as push, amend, or rebase, happens only when the user asks for it.

## 1. Plan the commits

Group the changes that belong to the task you were given into commits that a reviewer can read one at a time. Done when every in-scope change belongs to exactly one commit and the commits are in order.

- **Size**: aim for commits whose subject line alone describes the whole change. Balance this against the opposite failure, a string of tiny commits that mean nothing on their own. A test goes in the same commit as the code it tests.
- **Order**: put each commit before the commits that depend on it, so a reviewer reading in order meets every definition before its first use. A DB migration and its model come before the controller or logic that uses the model.
- **Hunks**: split a file across commits only when its changes are large, serve different commits, and the split makes the history clearly easier to follow. Otherwise, put the whole file in the commit it fits best. Interactive `git add -p` does not work for an agent; stage the chosen hunks with a patch and `git apply --cached`.

## 2. Write each message

Use Conventional Commits in English: `<type>(<scope>): <imperative summary>`.

- **Subject**: leave out what the scope already says. Write `fix(auth): refresh expired tokens`, not `fix(auth): fix auth token refresh`.
- **Body**: write one only when the subject leaves out something a future reader needs: a non-obvious why, migration notes, or linked issues. Breaking changes, security fixes, data migrations, and reverts always get a body, because future debuggers need the context there most.
- **Breaking change**: add a `BREAKING CHANGE:` footer that says who must migrate, by when, and what the old path does after that date.
- **Wording**: write statements that stay true after later commits land. Describe the change directly, without narrator words ("This commit", "I", "we") or time words ("now", "currently").
- **Credit**: credit people with trailers such as `Co-authored-by`, not with prose in the body.

```
feat(api)!: rename /v1/orders to /v1/checkout

BREAKING CHANGE: clients on /v1/orders must migrate to /v1/checkout
before 2026-06-01. The old route returns 410 after that date.
```

## 3. Commit

Create the commits in the planned order. Done when every planned commit exists and no in-scope change is left uncommitted.

When a pre-commit hook fails, fix the cause and commit again if it is in scope or small, such as a lint error or a syntax error. When a test or scan fails for a reason outside the task, stop and report the failure to the user.
