---
name: dig-in
description: Dig into a topic you want to understand. It works out your goal and level, scouts the current state of the topic, proposes what to explore, an output format, and a writing style, then has fresh researchers write each part from trusted sources.
disable-model-invocation: true
argument-hint: "<topic>"
---

# Dig In

Turn "explain X to me" into output pitched at the user's goal and level, so they do not have to re-prompt until it clicks. `<dig-in>` below means the folder containing this file.

Keep this conversation's context for understanding the user. Leave reading sources to subagents.

Everything the user reads, from the plan to the final reports, should be clear, fit the user, and be easy to remember after one read. Keep English technical terms as they are instead of translating them.

## 1. Understand the need

Take the topic from the invocation. Before proposing anything, know two things:

- **Goal**: why the user wants to understand this and what they will do with it.
- **Level**: what they already know about the topic and its prerequisites.

Ask for whatever the invocation and conversation do not already make clear. If the user states their level clearly, do not quiz them. If they are unsure of their level, ask a few calibration questions that climb from basic to advanced, at most 5, and place the user where their confident answers stop.

## 2. Scout

Start one scout subagent with a fresh context window, so the plan rests on the current state of the topic rather than on what you remember. Give it the topic, the goal, and the level. Have it check which information tools it has and use them: web search, web fetch, documentation MCP servers, and local files such as a repo or codebase when the topic lives there.

Have it return only:
- An outline of the topic's main parts.
- 3-5 primary sources, with links or paths.
- What is new or has changed recently.

## 3. Propose the plan

From the scout's report, the goal, and the level, propose in one message:

- **Map**: the parts worth exploring for this goal and level, ordered from fundamentals to advanced and from overview to deep dive.
- **Output format**, chosen to fit the scope and the user's level, with this lead-in in the user's language:

  For this topic, I suggest this output format:
  ```
  <the proposal>
  ```

  It can be the chat, one `.md` file, or a folder with one file per part and a `README.md` index. For a file or folder, show the path and tree, and the outline each file will follow. Propose a default path inside the current working directory, such as `dig-in/<topic-slug>/`.
- **Writing style**: how dense the advanced terminology is, how much gets explained versus assumed, and how explanatory the prose is. Follow it with a 3-4 sentence sample passage written in that style about this topic, so the user can judge the style by reading it.

Revise until the user approves. Do not start research before that, because every researcher builds on the plan.

## 4. Dispatch researchers

Start one researcher subagent per approved part, each with a fresh context window, even when there is only one part. Run independent parts in parallel.

Give each researcher:
- The absolute path to `<dig-in>/references/researcher.md` and an instruction to follow it.
- The topic, the goal, the level, and the full map with its own part marked.
- The approved style and sample passage, and its outline if one was approved.
- The scout's sources.
- The output target: an absolute file path, or "return the report as your final reply" for chat.

## 5. Deliver

- **Chat**: post each report exactly as the researcher returned it, in map order. Do not summarise, merge, or rewrite it.
- **File or folder**: check that every file exists. For a folder, write `README.md` with the map, a one-line summary per part, and links. Tell the user where to start reading.

Then ask what is still unclear. For a follow-up on a part, start a new researcher with a fresh context window and the adjusted angle, rather than patching the report yourself.
