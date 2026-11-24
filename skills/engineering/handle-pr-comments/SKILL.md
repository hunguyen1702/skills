---
name: handle-pr-comments
description: "Fetch the review comments on the user's own GitHub PR, judge each one against the PR's scope and spec, fix the valid ones, then reply to and resolve every thread after the user approves a plan. Use when the user asks to handle, address, or resolve the review comments on their PR. Not for reviewing a PR or posting review findings on one."
---

# Handle PR Comments

Work through the open review comments on one of the user's own GitHub PRs: judge each comment, agree a plan with the user, fix what is worth fixing, and close every thread with a reply.

Nothing goes on the PR (commit, push, reply, issue, resolve) until the user has approved the plan in step 3, because every one of those actions is public.

## 1. Find the PR and its spec

Take the PR from the arguments, or from the current branch when none is given. Check that the head branch of the PR is checked out locally. When it is not, stop and tell the user which branch to check out; never switch branches yourself, because that can disturb their uncommitted work.

Find out what the PR is meant to deliver, so you can judge drift in step 2. Look where the spec is likely to live: the PR description, the issues it links, a spec file in the repo. When you find none, judge scope from the PR description and diff, and say so in the plan.

Done when you are on the head branch and can state in one or two sentences what outcome the PR promises.

## 2. Fetch and judge every comment

Fetch all of them with `gh`: inline review threads (GraphQL `reviewThreads`, which give `isResolved`, `isOutdated`, and the thread ID needed for reply and resolve), comments in the Conversation tab, and comments from bots. Skip resolved threads. Keep outdated threads that are still open, and check in the current code whether the problem still exists.

Judge each comment on its merits; these guidelines inform the call, they do not replace it:

- **Fix** when the problem is real, likely to happen in practice, worth the change, and the fix keeps the PR on its spec.
- **Reject** when the fix would make the PR drift from the outcome its spec expects, or when the problem is too small to gain anything.
- **Ask the user** when the problem is outside this PR's scope (defer it?), when it rarely happens and the fix adds complexity (worth it?), or when it is too big for this PR (follow-up issue?).
- **Already handled** when the current code no longer has the problem, such as an outdated thread.

Done when every fetched comment has exactly one verdict and a one-line reason.

## 3. Agree the plan

Show the user one table, one row per comment: a number, the location (`file:L<n>` or "Conversation"), the author, a short summary of the comment, the proposed action (fix, reject, defer with a follow-up issue, already handled), and the reason. For the rows where you need a decision, state the question and what each answer leads to. Mention the spec source you used, or that you found none.

Let the user change any row. Done when every row has a final action and the user approves the plan.

## 4. Fix

Load the "lean-change" skill before you change any code. Make the fixes, run the repo's checks that cover the changed code, then load the "commit-changes" skill and commit. Push to the PR branch; the approved plan already covers the push.

Done when every fix row is in a pushed commit and you know which commit SHA fixed each row.

## 5. Create follow-up issues

For each row the user chose to defer or split off, create a GitHub issue with the label `follow-up`. Create the label first when the repo does not have it.

- Title: one short sentence that names the problem.
- Body: links to the review comment and the PR, the comment quoted, why it was deferred, and the proposed scope.

Done when every defer row has an issue URL.

## 6. Reply and resolve

Reply to each comment in the language the comment was written in:

- Fix: what changed, with the commit SHA.
- Reject: the reason, tied to the PR's scope or spec.
- Defer: the link to the follow-up issue.
- Already handled: where or why the problem is gone.

Resolve each inline thread after replying. Conversation-tab comments cannot be resolved; the reply closes them.

Done when every row has a reply and every inline thread from the plan is resolved.

## 7. Report

Tell the user what was done: the commits with their SHAs, the issues created with their URLs, and per comment the action taken and whether its thread is resolved. List any step that failed, such as a reply that did not post, so the user can finish it by hand.
