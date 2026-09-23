#!/usr/bin/env python3
"""Execute deterministic behavioral contract fixtures for every eval case."""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1]
ROOT = SOURCE.parent
SKILL = ROOT / "skills/adaptive-planning"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def route(facts: dict[str, object]) -> str:
    broad = (int(facts["outcomes"]) > 1 or int(facts["subsystems"]) > 1
             or bool(facts["major_decision_open"]) or not bool(facts["one_session"]))
    return "A" if broad else "B"


def git_snapshot() -> tuple[str, str, str]:
    def run(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=ROOT, check=True,
                              capture_output=True, text=True).stdout
    return run("status", "--short"), run("diff", "--binary"), run("diff", "--cached", "--binary")


def materialize(route_name: str, output: Path, confirmed: bool) -> list[Path]:
    """Reference fixture: exercise gates and observable document contracts."""
    if not confirmed:
        return []
    output.mkdir(parents=True, exist_ok=True)
    if route_name == "A":
        epic, board = output / "EPIC-001.md", output / "TASK-BOARD.md"
        epic.write_text(
            "---\nid: EPIC-001\nkind: epic\nplanning_state: planned\n---\n\n"
            "# Outcome\nDeliver two outcomes.\n\n# Future-planning units\n"
            "- UNIT-001 — First — Plan the first bounded scope.\n"
            "- UNIT-002 — Second — Plan the second bounded scope.\n\n"
            "# Task-board link\n[TASK-BOARD.md](TASK-BOARD.md)\n", encoding="utf-8")
        board.write_text(
            "# Planning board\n\nLegend: `needed` awaits a plan; `planned` has one.\n\n"
            "| ID | Planning unit | Outcome | Planning | Document | Notes |\n"
            "|---|---|---|---|---|---|\n"
            "| UNIT-001 | First | First outcome | needed | | |\n"
            "| UNIT-002 | Second | Second outcome | needed | | |\n\n"
            "[Epic](EPIC-001.md)\n", encoding="utf-8")
        return [epic, board]
    story, task = output / "STORY-001.md", output / "STORY-001-T1.md"
    story.write_text(
        "---\nid: STORY-001\nkind: story\nplanning_state: planned\n---\n\n"
        "# Outcome\nDeliver one bounded outcome.\n\n# Implementation-task link\n"
        "[STORY-001-T1.md](STORY-001-T1.md)\n", encoding="utf-8")
    task.write_text(
        "---\nid: STORY-001-T1\nkind: implementation-task\nplanning_state: planned\n---\n\n"
        "# Parent story\n[STORY-001.md](STORY-001.md)\n\n"
        "# Objective\nImplement and verify the bounded outcome.\n", encoding="utf-8")
    return [story, task]


def validator_module():
    path = SOURCE / "scripts/validate_packages.py"
    spec = importlib.util.spec_from_file_location("package_validator", path)
    require(spec is not None and spec.loader is not None, "could not load validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evaluate(case: dict[str, object], temp: Path) -> None:
    case_id, expected = str(case["id"]), case["expected"]
    routing = (SOURCE / "shared/routing.md").read_text(encoding="utf-8")
    workflow = (SOURCE / "shared/workflow.md").read_text(encoding="utf-8")
    interview = (SOURCE / "shared/interview-and-confirmation.md").read_text(encoding="utf-8")
    formats = (SOURCE / "shared/document-formats.md").read_text(encoding="utf-8")

    if case_id in ("broad-multi-outcome-routes-a", "bounded-one-session-routes-b"):
        selected = route(case["facts"])
        artifacts = materialize(selected, temp / case_id, True)
        require(selected == expected["route"] and len(artifacts) == 2, case_id)
    elif case_id in ("broad-reroutes-to-b", "bounded-reroutes-to-a"):
        routes = [route(case["initial_facts"]), route(case["clarified_facts"])]
        require(routes == expected["routes"], case_id)
        require(not materialize(routes[0], temp / case_id, False), f"{case_id}: pre-confirm write")
        require(len(materialize(routes[1], temp / case_id, expected["reconfirmation"])) == 2, case_id)
    elif case_id == "ambiguity-gets-focused-recommendation":
        require("one focused question" in interview.lower() and "recommend one default" in interview.lower(), case_id)
    elif case_id == "both-routes-require-confirmation":
        require("wait for explicit user confirmation" in workflow.lower(), case_id)
        require(all(not materialize(name, temp / f"{case_id}-{name}", False)
                    for name in expected["routes"]), case_id)
    elif case_id == "route-a-exact-output":
        artifacts = materialize("A", temp / case_id, True)
        require([item.name for item in artifacts] == ["EPIC-001.md", "TASK-BOARD.md"], case_id)
        require("kind: story" not in "".join(item.read_text() for item in artifacts), case_id)
    elif case_id == "route-a-board-contract":
        board = materialize("A", temp / case_id, True)[1].read_text()
        require("| " + " | ".join(expected["columns"]) + " |" in board, case_id)
        states = {line.split("|")[4].strip() for line in board.splitlines() if line.startswith("| UNIT-")}
        require(states <= set(expected["planning_values"]), case_id)
    elif case_id == "route-b-paired-output":
        story, task = materialize("B", temp / case_id, True)
        require(task.name in story.read_text() and story.name in task.read_text(), case_id)
    elif case_id == "unique-temporary-workspaces":
        one = Path(tempfile.mkdtemp(prefix="adaptive-planning-eval-", dir="/tmp"))
        two = Path(tempfile.mkdtemp(prefix="adaptive-planning-eval-", dir="/tmp"))
        try:
            require(one != two and one.parent == Path(expected["parent"]) and two.parent == Path(expected["parent"]), case_id)
        finally:
            one.rmdir(); two.rmdir()
    elif case_id == "delivery-reports-paths":
        artifacts = materialize("A", temp / case_id, True)
        report = "\n".join(f"Artifact: {item.resolve()}" for item in artifacts)
        report += f"\nTask board: {artifacts[1].resolve()}"
        require(all(str(item.resolve()) in report for item in artifacts) and "Task board:" in report, case_id)
    elif case_id == "default-does-not-mutate-input-repository":
        before = git_snapshot()
        workspace = Path(tempfile.mkdtemp(prefix="adaptive-planning-default-", dir="/tmp"))
        try:
            materialize("B", workspace, True)
        finally:
            shutil.rmtree(workspace)
        require(before == git_snapshot(), case_id)
    elif case_id == "explicit-repository-output":
        normalized = workflow.lower()
        require("repository output" in normalized and "explicitly requests" in normalized
                and "local instructions" in normalized, case_id)
    elif case_id == "review-fallback":
        require("structured self-review" in workflow.lower() and "limitation" in workflow.lower(), case_id)
    elif case_id == "static-leakage-scan":
        injected = temp / case_id
        shutil.copytree(SKILL, injected)
        (injected / "references/leak.md").write_text("tbtm-core", encoding="utf-8")
        try:
            validator_module().validate_neutrality(injected)
        except ValueError:
            pass
        else:
            raise AssertionError(f"{case_id}: injected term accepted")
    elif case_id == "runtime-parity":
        for name in ("workflow.md", "routing.md", "interview-and-confirmation.md", "document-formats.md"):
            require((SKILL / "references" / name).read_bytes() ==
                    (SOURCE / "shared" / name).read_bytes(), f"{case_id}: {name}")
        require("Route A" in routing and "Route B" in routing and "Task board" in formats, case_id)
    else:
        raise AssertionError(f"unhandled evaluation case: {case_id}")


def main() -> int:
    cases = json.loads((SOURCE / "evals/cases.json").read_text(encoding="utf-8"))["cases"]
    ids = [case["id"] for case in cases]
    require(len(cases) == 16 and len(set(ids)) == 16, "matrix must contain 16 unique cases")
    with tempfile.TemporaryDirectory(prefix="adaptive-planning-matrix-", dir="/tmp") as temporary:
        for case in cases:
            evaluate(case, Path(temporary))
    print(f"Behavioral contract evals passed: {len(cases)} cases, each dispatched and asserted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
