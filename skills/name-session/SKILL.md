---
name: name-session
description: Give the current session a short English name using local Ollama. Add an optional hint to focus the name.
disable-model-invocation: true
---

# Name Session

1. Run `python3 -I <skill-folder>/scripts/name_session.py` from the current working directory. Pass the user's optional hint as `--hint <quoted-text>`. Use this skill's folder, not the project's folder, to locate the script. Let the script extract context and name the session; do not read the transcript or generate a competing name. Done when the script returns a saved title or an error.
2. On a permission error, ask permission to run that same script with localhost access and access to the agent's session storage. Codex's restricted sandbox can block both. Keep the current session's environment when retrying; never guess the newest session or disable sandboxing for the whole agent. On an Ollama readiness error, tell the user to invoke the `namer-service` skill themselves. Done when the script succeeds or the blocking error has been reported without claiming a rename.
3. Report the saved title. For Codex and Pi, include the script's notice that the running interface may not refresh until resume or reload. Done when the user knows the saved name and any refresh limitation.
