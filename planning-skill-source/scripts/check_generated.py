#!/usr/bin/env python3
"""Fail when committed distributions differ from canonical generation."""

from __future__ import annotations

import filecmp
import subprocess
import sys
import tempfile
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = SOURCE_ROOT.parent
PACKAGES = (Path("skills/adaptive-planning"),)


def differences(expected: Path, actual: Path) -> list[str]:
    comparison = filecmp.dircmp(expected, actual)
    found = [str(actual / name) for name in comparison.left_only + comparison.right_only + comparison.diff_files]
    for name in comparison.common_dirs:
        found.extend(differences(expected / name, actual / name))
    return found


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="adaptive-planning-drift-") as temporary:
        root = Path(temporary)
        subprocess.run(
            [sys.executable, str(SOURCE_ROOT / "scripts" / "build.py"), "--output-root", str(root)],
            check=True,
            capture_output=True,
            text=True,
        )
        drift: list[str] = []
        for package in PACKAGES:
            actual = REPOSITORY_ROOT / package
            expected = root / package
            if not actual.exists():
                drift.append(str(actual))
            else:
                drift.extend(differences(expected, actual))
        if drift:
            print("Generated packages are stale. Run planning-skill-source/scripts/build.py.")
            for path in sorted(drift):
                print(f"- {path}")
            return 1
    print("Generated packages match canonical sources.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
