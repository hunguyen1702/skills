# Security axis reference

Paste this file in full into the Security sub-agent prompt and the security verifier prompt.

## Categories to examine

- **Input validation**: SQL, NoSQL, command, template, and XXE injection; path traversal in file operations.
- **Authentication and authorization**: auth bypass, privilege escalation, session flaws, JWT flaws, missing checks on user input that reaches a sensitive operation.
- **Crypto and secrets**: hardcoded keys, passwords, or tokens; weak algorithms; weak randomness for security values; certificate validation bypass.
- **Code execution**: unsafe deserialization (pickle, YAML), `eval` on untrusted input, XSS (reflected, stored, DOM).
- **Data exposure**: secrets or PII in logs or responses, API endpoints that leak data, debug information exposed.

A vulnerability reachable only from the local network can still be High.

## Method

1. Find the security patterns the repo already uses: frameworks, sanitizers, validators, auth middleware.
2. Compare the diff against them. Flag new code that skips or diverges from an existing protection, and new attack surface.
3. Trace each user input in the diff to the sensitive operations it reaches, and look for privilege boundaries crossed without a check.

Read the code to judge exploitability. Do not run commands to reproduce a vulnerability.

## Severity

- **High** (🔴): directly exploitable, leads to RCE, data breach, or auth bypass.
- **Medium** (🟡): needs specific conditions but has significant impact. Report it only when it is obvious and concrete.

Drop Low findings (defense-in-depth only).

## Hard exclusions

Never report these:

1. Denial of service, resource exhaustion, rate limiting, memory or CPU exhaustion, regex DoS, resource leaks (memory, file descriptors).
2. Secrets stored on disk that are otherwise secured.
3. Missing input validation on fields with no proven security impact.
4. Missing hardening. Flag concrete vulnerabilities, not absent best practices.
5. Race conditions or timing attacks that are theoretical rather than practical.
6. Outdated third-party libraries.
7. Memory safety issues in memory-safe languages.
8. Files that are only tests or only run as part of tests.
9. Documentation files.
10. Log spoofing: unsanitized user input written to logs.
11. SSRF that controls only the path, not the host or protocol.
12. User content included in AI system prompts.
13. Regex injection.
14. Missing audit logs.

## Precedents

1. Logging high-value secrets or PII in plaintext is a vulnerability. Logging URLs and non-PII data is not.
2. UUIDs are unguessable and need no validation.
3. Environment variables and CLI flags are trusted. An attack that needs control of them is invalid.
4. Tabnabbing, XS-Leaks, prototype pollution, and open redirects: report only at very high confidence.
5. React and Angular escape output. Report XSS there only through `dangerouslySetInnerHTML`, `bypassSecurityTrustHtml`, or a similar unsafe method.
6. Client-side JS/TS needs no auth or permission checks; the server owns them and owns validation of everything the client sends.
7. GitHub Actions workflows, notebooks (`*.ipynb`), and shell scripts rarely receive untrusted input. Report a vulnerability in them only with a specific attack path from untrusted input.

## Confidence

Score each finding 1-10 on these questions: is there a concrete attack path, is it a real risk rather than a best practice, does it point at a specific location, and would a security team act on it?

- 1-3: likely a false positive.
- 4-7: needs specific conditions or more investigation.
- 8-10: a likely true vulnerability. Only these reach the report.
