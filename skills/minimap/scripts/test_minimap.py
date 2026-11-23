#!/usr/bin/env python3
"""Self-check for minimap.py. Run: python3 skills/minimap/scripts/test_minimap.py"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "minimap.py"


def run(*args, cwd, ok=True):
    r = subprocess.run([sys.executable, str(SCRIPT), *args], cwd=cwd, capture_output=True, text=True)
    if ok and r.returncode != 0:
        raise AssertionError(f"{args} failed: {r.stderr}")
    return r


def git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})


def main():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp).resolve()
        wallet = tmp / "code" / "wallet"
        (wallet / "svc").mkdir(parents=True)
        git("init", "-q", cwd=wallet)
        git("remote", "add", "origin", "git@example.com:acme/wallet.git", cwd=wallet)
        (wallet / "AGENTS.md").write_text("Use tabs.\n@docs/style.md\n")
        (wallet / "docs").mkdir()
        (wallet / "docs" / "style.md").write_text("Style rules here.\n")
        (wallet / "CLAUDE.md").write_text("@AGENTS.md\n")
        (wallet / "svc" / "AGENTS.md").write_text("svc rules\n")

        out = run("scan", str(tmp / "code"), cwd=tmp).stdout
        assert "wallet\t" in out and "acme/wallet.git" in out, out

        home = tmp / "home"
        out = run("install", str(home), cwd=tmp).stdout
        assert "ran git init" in out and "installed pre-commit hook" in out, out
        assert (home / ".minimap/bin/minimap.py").is_file()
        assert "repos.local" in (home / ".gitignore").read_text()
        assert run("status", cwd=home).stdout.startswith("home_repo: yes")

        run("set", "wallet", str(wallet), cwd=home)
        assert "acme/wallet.git" in (home / "repos.example").read_text()
        assert str(wallet) not in (home / "repos.example").read_text()

        out = run("load", "{{wallet}}", cwd=home).stdout
        assert "=== {{wallet}} instructions: AGENTS.md ===" in out, out
        assert "Style rules here." in out, out
        assert "instructions: CLAUDE.md" not in out, "CLAUDE.md pointer should be skipped"
        assert "{{wallet}}/svc/AGENTS.md" in out, out

        run("set", "ghost", str(tmp / "nope"), "--remote", "git@example.com:acme/ghost.git", cwd=home)
        r = run("load", "ghost", cwd=home, ok=False)
        assert r.returncode == 1 and "git clone git@example.com:acme/ghost.git" in r.stderr, r.stderr

        (home / "AGENTS.md").write_text("Wallet lives in {{wallet}}.\n")
        git("add", "AGENTS.md", "repos.example", ".gitignore", cwd=home)
        assert run("check-paths", cwd=home).returncode == 0
        (home / "notes.md").write_text(f"see {wallet}/svc\n")
        git("add", "notes.md", cwd=home)
        r = run("check-paths", cwd=home, ok=False)
        assert r.returncode == 1 and "notes.md:1" in r.stderr, r.stderr
        r = subprocess.run(["git", "commit", "-qm", "x"], cwd=home, capture_output=True, text=True)
        assert r.returncode != 0, "pre-commit hook should block the commit"

        run("remove", "ghost", cwd=home)
        assert "ghost" not in (home / "repos.example").read_text()

        check_prepare_restore(tmp)
    print("ok")


def out(*args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def check_prepare_restore(tmp):
    origin = tmp / "origin.git"
    git("init", "-q", "--bare", "-b", "master", str(origin), cwd=tmp)
    seed = tmp / "seed"
    git("clone", "-q", str(origin), str(seed), cwd=tmp)
    (seed / "a.txt").write_text("v1\n")
    git("add", ".", cwd=seed); git("commit", "-qm", "v1", cwd=seed); git("push", "-q", "origin", "HEAD:master", cwd=seed)

    child = tmp / "child"
    git("clone", "-q", str(origin), str(child), cwd=tmp)
    git("checkout", "-q", "-b", "feature", cwd=child)
    (seed / "a.txt").write_text("v2\n")
    git("commit", "-qam", "v2", cwd=seed); git("push", "-q", "origin", "HEAD:master", cwd=seed)

    # Dirty repo: staged, unstaged, and untracked changes all come back as they were.
    (child / "a.txt").write_text("staged\n"); git("add", "a.txt", cwd=child)
    (child / "a.txt").write_text("unstaged\n")
    (child / "new.txt").write_text("untracked\n")
    before = out("status", "--porcelain", cwd=child)
    o = run("prepare", str(child), cwd=tmp).stdout
    assert o.startswith("prepared") and "stashed" in o, o
    assert (child / "a.txt").read_text() == "v2\n", "should survey the latest origin/master"
    assert not (child / "new.txt").exists()
    assert "minimap: stash + checkout master" in out("stash", "list", cwd=child)
    assert run("prepare", str(child), cwd=tmp).stdout.startswith("skipped"), "double prepare must skip"
    o = run("restore", str(child), cwd=tmp).stdout
    assert o.startswith("restored") and "unstashed" in o, o
    assert out("symbolic-ref", "--short", "HEAD", cwd=child) == "feature"
    assert out("status", "--porcelain", cwd=child) == before
    assert (child / "a.txt").read_text() == "unstaged\n"
    assert out("stash", "list", cwd=child) == ""
    assert not (child / ".git" / "minimap-restore").exists()

    # Clean repo on a detached HEAD returns to the same commit.
    git("stash", "push", "-q", "-u", cwd=child)
    sha = out("rev-parse", "HEAD", cwd=child)
    git("checkout", "-q", "--detach", cwd=child)
    o = run("prepare", str(child), cwd=tmp).stdout
    assert o.startswith("prepared") and "clean" in o, o
    run("restore", str(child), cwd=tmp)
    assert out("rev-parse", "HEAD", cwd=child) == sha
    assert run("restore", str(child), cwd=tmp).stdout.startswith("nothing")

    # No origin: skip and leave the repo alone.
    lone = tmp / "lone"
    lone.mkdir(); git("init", "-q", cwd=lone)
    (lone / "x").write_text("x\n"); git("add", ".", cwd=lone); git("commit", "-qm", "x", cwd=lone)
    (lone / "x").write_text("dirty\n")
    o = run("prepare", str(lone), cwd=tmp).stdout
    assert o.startswith("skipped") and "no origin" in o, o
    assert (lone / "x").read_text() == "dirty\n"


if __name__ == "__main__":
    main()
