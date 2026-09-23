#!/usr/bin/env python3
"""Generate the adaptive-planning skill inside the portable root plugin."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = SOURCE_ROOT.parent
SHARED_FILES = (
    "workflow.md",
    "routing.md",
    "interview-and-confirmation.md",
    "document-formats.md",
)
PLACEHOLDERS = ("{{", "}}", "[TODO", "TODO:")


def reject_placeholders(name: str, content: str) -> str:
    for marker in PLACEHOLDERS:
        if marker in content:
            raise ValueError(f"unresolved placeholder {marker!r} in {name}")
    return content


def read_template(name: str) -> str:
    content = (SOURCE_ROOT / "runtime" / name).read_text(encoding="utf-8")
    return reject_placeholders(name, content)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as output:
        output.write(content)


def copy_shared(destination: Path) -> None:
    for name in SHARED_FILES:
        content = (SOURCE_ROOT / "shared" / name).read_text(encoding="utf-8")
        write_text(destination / name, reject_placeholders(f"shared/{name}", content))


def generate(output_root: Path) -> Path:
    skill = output_root / "skills" / "adaptive-planning"
    if skill.exists():
        shutil.rmtree(skill)

    write_text(skill / "SKILL.md", read_template("portable-skill.md.tmpl"))
    write_text(skill / "openai.yaml", read_template("codex-openai.yaml.tmpl"))
    copy_shared(skill / "references")

    eval_source = (SOURCE_ROOT / "evals" / "plugin-evals.json").read_text(encoding="utf-8")
    reject_placeholders("evals/plugin-evals.json", eval_source)
    evals = json.loads(eval_source)
    rendered_evals = json.dumps(evals, indent=2, ensure_ascii=False) + "\n"
    write_text(skill / "evals" / "evals.json", rendered_evals)
    return skill


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=REPOSITORY_ROOT)
    args = parser.parse_args()
    print(generate(args.output_root.resolve()))


if __name__ == "__main__":
    main()
