---
name: skill-taste
description: Edit, improve, and evaluate an existing skill for Claude Code, Codex, or both. It can test output quality and description triggering before you keep the change.
disable-model-invocation: true
---

# Skill Taste

Improve one existing skill without losing what already works. Use `<skill-taste>` for the folder containing this file.

## 1. Find the target and goal

Derive the skill path and requested change from the invocation and conversation. If either is unclear, ask for the exact skill path and what should change.

Read the target skill completely, including references and scripts that matter to the request. Identify its target agents from metadata and folder location. Record whether it is model-invoked: Claude Code uses `disable-model-invocation: true`; Codex uses `policy.allow_implicit_invocation: false` in `agents/openai.yaml`.

Choose the path that matches the user's goal:
- **Edit**: the user already knows what to change.
- **Improve**: the user wants it better but has no concrete change. Ask what failed: wrong output, missed steps, slow or wasteful work, poor triggering, or hard-to-maintain instructions. Propose specific changes before editing.
- **Trigger only**: the user wants better automatic invocation. Skip to trigger evaluation.

## 2. Change the skill

Before editing, snapshot the original to the workspace:

```bash
mkdir -p ~/.cache/skill-taste/<skill-name>
cp -R <skill-path> ~/.cache/skill-taste/<skill-name>/skill-snapshot
```

When you need current agent rules, start a subagent with a fresh context window and have it read the official docs or source for that agent. Use the report over memory.

Apply `<skill-taste>/references/improving.md` while editing.

## 3. Evaluate output quality

After an edit or improvement, ask whether to run output evaluation. Explain that it spends model tokens because each test case runs the skill and the old snapshot.

If accepted:
1. Write 2-3 realistic test prompts and agree on them with the user. Save them in `~/.cache/skill-taste/<skill-name>/evals.json` using `references/schemas.md`.
2. For each prompt, start two subagents with fresh context windows in parallel: one uses the edited skill, one uses `skill-snapshot`. Save outputs under `iteration-N/<eval-name>/{with_skill,old_skill}/outputs/`.
3. While they run, write objectively checkable assertions. Leave subjective quality to human review.
4. Save `timing.json` when the agent exposes token or duration data. Skip it otherwise.
5. For each run, start a grader subagent with a fresh context window, so it judges the output without your drafting context. Have it follow `<skill-taste>/references/grader.md`. Give it the assertions, the transcript, and the run's `outputs/` folder, and have it write `grading.json`. Check assertions a script can verify with that script.
6. Aggregate:
   ```bash
   python3 <skill-taste>/scripts/aggregate_benchmark.py ~/.cache/skill-taste/<skill-name>/iteration-N --skill-name <skill-name>
   ```
7. Start an analyzer subagent with a fresh context window. Have it follow the benchmark section of `<skill-taste>/references/analyzer.md`, read `benchmark.json`, and report the patterns the averages hide.
8. Generate the review page:
   ```bash
   python3 <skill-taste>/eval-viewer/generate_review.py ~/.cache/skill-taste/<skill-name>/iteration-N \
     --skill-name <skill-name> --benchmark ~/.cache/skill-taste/<skill-name>/iteration-N/benchmark.json \
     --static ~/.cache/skill-taste/<skill-name>/iteration-N/review.html
   ```
   Add `--previous-workspace <previous-iteration>` from iteration 2. Tell the user where the page is, then wait for their review.
9. Read `feedback.json`, generalise from concrete complaints, update the skill, and repeat in a new iteration until the user is satisfied or progress stops.

When the user asks for a blind comparison between two versions:
1. Start a comparator subagent with a fresh context window. Have it follow `<skill-taste>/references/comparator.md`. Give it the two outputs labelled A and B, and do not say which version produced which.
2. Then start an analyzer subagent with a fresh context window. Have it follow the comparison section of `<skill-taste>/references/analyzer.md` to explain why the winner won.

## 4. Evaluate triggering

Run this only for model-invoked skills.

1. Draft 16-20 realistic queries: about half should trigger, half should not. Make the negatives close misses, not unrelated tasks. Show them in chat for edits.
2. Save the approved list as JSON: `[{"query": "...", "should_trigger": true}]`.
3. Run once per target agent:
   ```bash
   python3 <skill-taste>/scripts/run_trigger.py --agent <claude-code|codex> \
     --skill-path <skill-path> --eval-set <eval-set.json> --model <model> \
     --output ~/.cache/skill-taste/<skill-name>/trigger-<agent>-N.json
   ```
4. Read failed queries, edit the description, and rerun. Compare held-out `test` results before keeping a description; train-only gains overfit.
5. Show the user the old and new description with scores for each agent.

Codex detection is a proxy: it counts a `command_execution` that reads the probe `SKILL.md`. Report it as such.

## 5. Finish

Show the changed files, evaluation results, and remaining risks. Leave release, version bumps, and commits to the target repo's own rules.
