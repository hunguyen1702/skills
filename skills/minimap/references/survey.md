# Survey child repos

Read each child repo **shallow**. The goal is what a new teammate learns in their first ten minutes: what the repo is for, its main stack, and which other repos it talks to. Stop at module boundaries: what a module is called and what it is for counts, how it works inside does not. Old repos often lack a README or a manifest, so pick what to read from what the repo actually has: names of top-level folders, config, deploy files, API specs, and client code for other services.

Give each repo its own subagent with a fresh context window, and run them in parallel. Without subagents, survey the repos one after another in this session. Hand each subagent the repo path, the placeholder names of all the other repos (so it can spot them under other names: package names, service hosts, image names, queue topics), the rules that it reads no secrets and writes nothing, and this report format:

```markdown
## {{name}}
- Does: <one or two sentences on what the repo is for, in the domain's words>
- Stack: <main languages, frameworks, data stores>
- Wiring:
  - <verb> {{other}} <over what: REST, gRPC, queue topic, shared package, shared DB>. Evidence: `<file>:<line>`
  - <an edge only guessed from names> (unverified)
- Instructions: <the repo's own instruction files, or "none">
- Home repo: <yes when it holds repos.example and .minimap/, else no>
```

Every wiring edge carries evidence or `(unverified)`. An edge with neither is a guess presented as a fact; drop it.

The survey is done when every repo has a report, or the user has been told why a repo could not be read.
