---
name: namer-service
description: Check and start local Ollama for session naming, and download qwen2.5:3b when missing. Does not install Ollama itself.
disable-model-invocation: true
---

# Namer Service

1. Run `python3 -I <skill-folder>/scripts/namer_service.py`, using this skill's folder to locate the script. It checks localhost, starts the Homebrew service only when needed, and pulls `qwen2.5:3b` only when missing. It never starts a second Ollama instance or installs Ollama. Done when the script reports readiness or a blocking error.
2. If permissions block localhost, service management, or the download, ask permission for the same operation rather than changing agent-wide permissions. If Ollama is missing, relay the install suggestion and stop. Done when readiness is verified or the user knows the missing prerequisite.
