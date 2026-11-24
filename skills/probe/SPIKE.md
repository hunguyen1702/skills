# Spike

A small runnable that calls a third-party API or library the way the system would, so you can judge whether it fits the current codebase before building on it, or which of several candidates fits best. Unlike the logic and UI branches, whoever runs the spike reaches the verdict: you run it and conclude; the user reads the report.

If the question is about the system's own logic, this is the wrong branch. Use [LOGIC.md](LOGIC.md). If it is about how something looks, use [UI.md](UI.md).

## When this is the right shape

- "Can this payment API handle our refund flow?"
- "Does this library parse the files we actually get?"
- "Will this SDK work with our runtime and auth setup?"
- "Which of these three libraries suits our codebase best?"
- Anything where the docs make it look fine but only a real call shows whether it fits.

Spike only when an unknown remains that the docs and source cannot answer, and a wrong guess is costly. When the provider is already chosen and its integration docs answer every question the system raises, skip the spike and implement from the docs.

## Process

### 1. State the question and the fit criteria

Write down the question, the candidates (one or several), and the criteria that decide the fit, at the top of the spike's entry file: the calls or features the system needs, the inputs it must accept, and any limits that matter (runtime, auth model, rate limits, response shape, licence). A spike without criteria ends in "it works", which settles nothing. Every candidate is judged against the same criteria.

### 2. Gather the docs

Read the provider's own sources (official docs, API reference, SDK source, changelog) for every call the criteria need. Use a fresh-context subagent when you can, or read them yourself. Note which version you read and whether a sandbox or test mode exists.

### 3. Build the spike

Build it against the sandbox or test mode when the provider has one. Install the library or SDK at the version you read about. Match the build to each criterion: a criterion about the system (runtime, auth model, data shapes, the repo's conventions) runs through the repo's real code and data shapes taken from real cases; a criterion only about the library itself can run in a small standalone script. When comparing candidates, build the same spike for each, so the results compare like for like. Leave the credentials as named environment variables the spike reads at start.

Never write a key or secret into the code, the report, or a commit. Keep them in an env file that git ignores.

### 4. Get credentials

Ask the user for each key or secret the spike needs, by name and where to get it (for example "a test-mode secret key from the provider's dashboard"). If the user cannot supply them, stop: write the report with the conclusion "not verified", list what was built and what is still missing, and capture it as usual.

### 5. Run it and judge the fit

Run the spike yourself. Print every call and its response, per rule 5 in [SKILL](SKILL.md). Check each fit criterion, for each candidate, against the observed results. Done when every criterion is marked met, not met, or not verifiable, with the evidence behind it.

When a criterion will not work, keep trying fixes until you have exhausted the approaches the docs and source suggest. Then stop and tell the user what you tried and what blocked it; that criterion is marked not met or not verifiable, not left open.

### 6. Capture the answer

Write the report and capture the spike the way the [SKILL](SKILL.md) describes, then show the user the conclusion. In the report:

- Name each API or library version and whether the results came from a sandbox or live mode.
- With several candidates, add a table of candidates against criteria, and recommend one.
- End the conclusion with the next steps the real integration needs, so the task can be split and estimated from the report.

## Anti-patterns

- **Judging from the docs alone.** The spike exists to see real responses; a finding without an observed result is a guess.
- **Building an abstraction layer over the provider.** Call it directly. Wrapping it is a job for the real implementation.
- **Calling live or billed endpoints without asking.** Use the sandbox; ask the user before anything that costs money or creates real data.
