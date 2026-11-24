---
name: review-pr
description: "Review a GitHub PR with the code-review skill and post the findings as inline comments, after your approval of a draft (default) or right away with auto."
argument-hint: "<PR number|PR URL> [--mode wait-approval|auto]"
disable-model-invocation: true
---

# Review PR

Review one GitHub PR and post the findings on it as one review with inline comments.

Read the PR and the mode from the arguments; the user may also write them in plain words ("PR 42, auto"). The mode is `wait-approval` unless the user asks for `auto`. If no PR number or URL is given, ask the user for it and wait.

## 1. Find the repo

Work in the local clone of the PR's repo, because the Standards axis of the review reads that repo's own standards files. A PR number belongs to the current repo. For a URL, compare its `owner/repo` with the current repo's GitHub remote.

When they differ, look in the current folder for a local clone of the PR's repo, such as a path that this repo's agent instructions, docs, or config name for it, or a submodule. When you find one, change into it and work there for the rest of the run. Otherwise stop and tell the user to run the skill from a clone of that repo. Never clone the repo yourself.

Done when you are inside a clone whose GitHub remote is the PR's repo.

## 2. Check out the PR in a temporary worktree

Read the PR's base branch, head SHA, and URL with `gh pr view`. Fetch the PR head (`pull/<n>/head`) and the base branch from the remote that points at the PR's repo, then add a detached worktree at the head SHA in a temporary folder. The worktree gives the review the full files at the PR head, so the line numbers match the ones GitHub expects. It also leaves the user's working tree and branch untouched.

Done when the worktree exists at the PR head and `git diff <remote>/<base>...HEAD` inside it is non-empty.

## 3. Review

Load the "code-review" skill and run it inside the worktree, with `<remote>/<base>` as the fixed point. Done when you have its report with numbered findings, each with a location.

## 4. Build the comments

Turn every finding into one comment. A comment body is the axis in bold, then the finding text exactly as the report wrote it, minus its location: `**Spec** · 🟡 ...`. Never reword, merge, or drop a finding at this step; the user decides what to change in step 5.

Write the comments to a findings JSON file in a temporary folder, in the format the "pr-review-comments" skill reads. A finding's location gives `file`, `line`, and `start_line` for a range; a `(removed)` location takes `side: "LEFT"`. Findings with a `general` location go into the review body instead, as a numbered list.

Run the pr-review-comments dry run against the JSON. Move every finding it skips, because its line is outside the diff, into the review body with its `file:L<n>` location, so no finding is lost.

Done when every finding from the report sits either in the JSON or in the review body, and the dry run skips nothing.

## 5. Approve the draft

In `auto` mode, skip to step 6.

In `wait-approval` mode, show the user the draft and post nothing yet:

- Each inline comment, numbered, with `file:L<n>` and its full body.
- The review body.
- The PR URL, and that it will be posted as one review with the `COMMENT` event.

Revise the draft as the user asks, update the JSON to match, rerun the dry run, and show the revised draft again. Repeat until the user approves posting.

## 6. Post

Load the "pr-review-comments" skill and post the JSON as one grouped review with the `COMMENT` event and the review body. Always use `COMMENT`, even with 🔴 findings: approving or blocking the PR is the human reviewer's call.

## 7. Report and clean up

Remove the worktree, also when an earlier step failed or the user cancelled.

After posting, tell the user:

- The review URL and the number of inline comments posted.
- Each comment: `file:L<n>` and a one-line summary.
- The findings placed in the review body, and why: no single location, or a line outside the diff.
