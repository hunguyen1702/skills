#!/usr/bin/env python3
"""Measure whether a skill description triggers on Claude Code or Codex.

The script only measures. The calling agent reads failures and edits the
description between iterations.
"""

import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

DEFAULT_RUNS = 3
DEFAULT_THRESHOLD = 0.5
DEFAULT_TIMEOUT = 180
DEFAULT_WORKERS = 4


def read_skill(skill_dir):
    path = skill_dir / "SKILL.md"
    text = path.read_text()
    if not text.startswith("---\n"):
        raise SystemExit(f"{path} has no frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        raise SystemExit(f"{path} has unterminated frontmatter")
    return text, text[4:end], text[end + 4 :]


def frontmatter_value(frontmatter, key):
    lines = frontmatter.splitlines()
    for index, line in enumerate(lines):
        match = re.match(rf"^{re.escape(key)}:\s*(.*)$", line)
        if not match:
            continue
        value = match.group(1).strip()
        if value in ("|", ">", "|-", ">-"):
            block = []
            for nested in lines[index + 1 :]:
                if nested[:1] not in (" ", "\t"):
                    break
                block.append(nested.strip())
            return " ".join(block)
        return value.strip("\"'")
    return ""


def install_variant(skill_dir, root, agent, description):
    _, frontmatter, body = read_skill(skill_dir)
    source_name = frontmatter_value(frontmatter, "name") or skill_dir.name
    probe_name = f"{source_name}-probe-{uuid.uuid4().hex[:8]}"
    folder = root / (".claude/skills" if agent == "claude-code" else ".agents/skills") / probe_name
    shutil.copytree(skill_dir, folder, ignore=shutil.ignore_patterns("evals", "__pycache__", "*.pyc", ".DS_Store"))

    output = []
    replaced_name = replaced_description = False
    lines = frontmatter.splitlines()
    skip_block = False
    for line in lines:
        if skip_block:
            if line[:1] in (" ", "\t"):
                continue
            skip_block = False
        if line.startswith("name:"):
            output.append(f"name: {probe_name}")
            replaced_name = True
        elif line.startswith("description:"):
            output.append(f"description: {json.dumps(description, ensure_ascii=False)}")
            replaced_description = True
            skip_block = line.split(":", 1)[1].strip() in ("|", ">", "|-", ">-")
        else:
            output.append(line)
    if not replaced_name:
        output.insert(0, f"name: {probe_name}")
    if not replaced_description:
        output.append(f"description: {json.dumps(description, ensure_ascii=False)}")
    (folder / "SKILL.md").write_text("---\n" + "\n".join(output) + "\n---" + body)
    return probe_name, folder


def run_claude(query, root, probe_name, folder, model, timeout):
    command = ["claude", "-p", query, "--output-format", "stream-json", "--verbose"]
    if model:
        command += ["--model", model]
    env = {key: value for key, value in os.environ.items() if key != "CLAUDECODE"}
    completed = subprocess.run(command, cwd=root, env=env, text=True, capture_output=True, timeout=timeout)
    triggered = False
    for line in completed.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        for item in event.get("message", {}).get("content", []):
            if item.get("type") != "tool_use":
                continue
            data = json.dumps(item.get("input", {}), ensure_ascii=False)
            if item.get("name") in ("Skill", "Read") and (probe_name in data or str(folder) in data):
                triggered = True
    return triggered, completed.returncode, completed.stderr[-1000:]


def run_codex(query, root, probe_name, folder, model, timeout):
    command = [
        "codex", "exec", "--json", "--ephemeral", "--skip-git-repo-check",
        "-s", "read-only", "-C", str(root), query,
    ]
    if model:
        command[2:2] = ["-m", model]
    completed = subprocess.run(command, stdin=subprocess.DEVNULL, text=True, capture_output=True, timeout=timeout)
    triggered = False
    for line in completed.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        item = event.get("item", {})
        command_text = item.get("command", "")
        if item.get("type") == "command_execution" and (f"{probe_name}/SKILL.md" in command_text or str(folder / "SKILL.md") in command_text):
            triggered = True
    return triggered, completed.returncode, completed.stderr[-1000:]


RUNNERS = {"claude-code": run_claude, "codex": run_codex}


def run_once(skill_dir, agent, description, query, model, timeout):
    with tempfile.TemporaryDirectory(prefix="skill-taste-trigger-") as tmp:
        root = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=root, check=False)
        probe_name, folder = install_variant(skill_dir, root, agent, description)
        started = time.time()
        try:
            triggered, code, stderr = RUNNERS[agent](query, root, probe_name, folder, model, timeout)
        except subprocess.TimeoutExpired:
            triggered, code, stderr = False, "timeout", ""
        return {"triggered": triggered, "exit_code": code, "seconds": round(time.time() - started, 2), "stderr": stderr}


def split(items, holdout, seed):
    if holdout <= 0:
        return items, []
    groups = {True: [x for x in items if x["should_trigger"]], False: [x for x in items if not x["should_trigger"]]}
    rng = random.Random(seed)
    train, test = [], []
    for group in groups.values():
        rng.shuffle(group)
        count = max(1, int(len(group) * holdout)) if len(group) > 1 else 0
        test += group[:count]
        train += group[count:]
    return train, test


def evaluate(items, args, description):
    jobs = [(index, run) for index, _ in enumerate(items) for run in range(args.runs)]
    raw = {index: [] for index in range(len(items))}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_once, args.skill_dir, args.agent, description, items[i]["query"], args.model, args.timeout): i for i, _ in jobs}
        for future in as_completed(futures):
            raw[futures[future]].append(future.result())

    results = []
    for index, item in enumerate(items):
        runs = raw[index]
        rate = sum(run["triggered"] for run in runs) / len(runs)
        passed = rate >= args.threshold if item["should_trigger"] else rate < args.threshold
        results.append({**item, "trigger_rate": rate, "pass": passed, "runs": runs})
    return {
        "passed": sum(result["pass"] for result in results),
        "total": len(results),
        "pass_rate": sum(result["pass"] for result in results) / len(results) if results else 0,
        "results": results,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", required=True, choices=sorted(RUNNERS))
    parser.add_argument("--skill-path", required=True, type=Path, dest="skill_dir")
    parser.add_argument("--eval-set", required=True, type=Path)
    parser.add_argument("--description", help="description to test; defaults to the skill's current description")
    parser.add_argument("--model")
    parser.add_argument("--runs", type=int, default=DEFAULT_RUNS)
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--holdout", type=float, default=0.4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    args.skill_dir = args.skill_dir.expanduser().resolve()

    items = json.loads(args.eval_set.read_text())
    if not items or any("query" not in item or "should_trigger" not in item for item in items):
        raise SystemExit("eval set must be a non-empty JSON array of {query, should_trigger}")
    _, frontmatter, _ = read_skill(args.skill_dir)
    description = args.description or frontmatter_value(frontmatter, "description")
    if not description:
        raise SystemExit("description is empty")
    if shutil.which("codex" if args.agent == "codex" else "claude") is None:
        raise SystemExit(f"{args.agent} CLI is not on PATH")

    train, test = split(items, args.holdout, args.seed)
    report = {
        "agent": args.agent,
        "description": description,
        "detection": "Skill/Read tool event" if args.agent == "claude-code" else "command_execution reading SKILL.md (proxy)",
        "train": evaluate(train, args, description),
        "test": evaluate(test, args, description) if test else None,
    }
    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
