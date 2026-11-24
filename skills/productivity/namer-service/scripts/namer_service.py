#!/usr/bin/env python3
"""Prepare the shared local Ollama service without installing software."""
import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

MODEL = "qwen2.5:3b"
URL = "http://127.0.0.1:11434/api/tags"


def models():
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(URL, timeout=3) as response:
        return {item["name"] for item in json.load(response).get("models", [])}


def prepare():
    if not shutil.which("ollama"):
        raise RuntimeError("Ollama is not installed. Install it with: brew install ollama")
    try:
        available = models()
    except urllib.error.HTTPError:
        raise RuntimeError("Localhost port 11434 did not return an Ollama model list.")
    except urllib.error.URLError as exc:
        if isinstance(exc.reason, PermissionError):
            raise RuntimeError("Permission denied accessing localhost; request access before retrying.") from exc
        if not shutil.which("brew"):
            raise RuntimeError("Ollama is not running and Homebrew is missing. Start Ollama, then retry.") from exc
        subprocess.run(["brew", "services", "start", "ollama"], check=True, timeout=60)
        deadline = time.monotonic() + 30
        while True:
            try:
                available = models()
                break
            except urllib.error.URLError:
                if time.monotonic() >= deadline:
                    raise RuntimeError("Ollama service did not become ready within 30 seconds.")
                time.sleep(0.5)
    if MODEL not in available:
        subprocess.run(["ollama", "pull", MODEL], check=True, timeout=1200)
    if MODEL not in models():
        raise RuntimeError(f"Ollama is running but {MODEL} is still missing.")
    print(f"Ready: {MODEL} on http://127.0.0.1:11434 (shared Ollama service).")


def main():
    try:
        prepare()
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"Namer service failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
