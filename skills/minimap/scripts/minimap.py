#!/usr/bin/env python3
"""Mechanical helpers for a minimap home repo. Standard library only.

A home repo keeps repo paths out of git: tracked files name repos with
{{name}} placeholders, repos.example (tracked) maps each name to its git
remote, and repos.local (gitignored) maps each name to its path on this
machine. The skill copies this file into <home>/.minimap/bin/ so the home
repo works without the skill installed.

Subcommands:
  scan DIR [--depth N]          list git repos under DIR
  status [--home DIR]           show whether DIR is a home repo and its entries
  install HOME                  git init if needed, copy this script, gitignore
                                repos.local, install the pre-commit hook
  set NAME PATH [--remote URL]  add or update a repo in repos.local/.example
  remove NAME                   drop a repo from repos.local/.example
  init-paths [--root DIR] [--clone]
                                fill repos.local from repos.example
  load NAME                     print a repo's instruction files
  check-paths [--all]           fail if a tracked change holds a local path
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

LOCAL = "repos.local"
EXAMPLE = "repos.example"
TOOL_DIR = ".minimap/bin"
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
ROOT_INSTRUCTIONS = ["AGENTS.md", "AGENTS.local.md", "CLAUDE.md", "CLAUDE.local.md"]
INSTRUCTION_NAMES = {"AGENTS.md", "CLAUDE.md", "AGENTS.local.md", "CLAUDE.local.md"}
SKIP_DIRS = {".git", "node_modules", "vendor", "dist", "build", ".venv", "venv",
             "target", "__pycache__", ".next", ".cache"}
ABS_PATH_RE = re.compile(r"(/Users/[^/\s]+/|/home/[^/\s]+/|[A-Za-z]:\\Users\\|(?<![\w.])~/)")
ALLOW_MARK = "minimap: allow-path"
HOOK_MARK = "# minimap pre-commit hook"
HOOK = f"""#!/bin/sh
{HOOK_MARK}
exec python3 "$(git rev-parse --show-toplevel)/{TOOL_DIR}/minimap.py" check-paths
"""


def die(msg, code=1):
    print(msg, file=sys.stderr)
    sys.exit(code)


def git(*args, cwd=None):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


# ---------- repos.local / repos.example ----------

def read_map(path):
    """Read `name: value` lines; '#' starts a comment. Value may be empty."""
    entries = {}
    if not path.exists():
        return entries
    for line in path.read_text().splitlines():
        line = line.split(" #", 1)[0].strip() if not line.lstrip().startswith("#") else ""
        if not line or ":" not in line:
            continue
        name, value = line.split(":", 1)
        entries[name.strip()] = value.strip()
    return entries


def write_map(path, entries, header):
    lines = [header] + [f"{k}: {v}".rstrip() for k, v in sorted(entries.items())]
    path.write_text("\n".join(lines) + "\n")


LOCAL_HEADER = "# name: absolute path on this machine. Gitignored; never commit."
EXAMPLE_HEADER = "# name: git remote (empty when none). Copy to repos.local with local paths."


def find_home(start=None):
    d = Path(start or os.getcwd()).resolve()
    for p in [d, *d.parents]:
        if (p / EXAMPLE).exists() and (p / ".minimap").is_dir():
            return p
    return None


def require_home(arg):
    home = find_home(arg)
    if not home:
        die("not inside a minimap home repo (no repos.example and .minimap/ found)")
    return home


def expand(path):
    return Path(os.path.expandvars(os.path.expanduser(path)))


# ---------- scan / status ----------

def repo_info(path):
    remote = git("remote", "get-url", "origin", cwd=path) or ""
    last = git("log", "-1", "--format=%cs", cwd=path) or ""
    is_home = (path / EXAMPLE).exists() and (path / ".minimap").is_dir()
    instr = [f for f in ROOT_INSTRUCTIONS if (path / f).exists()]
    return remote, last, is_home, instr


def cmd_scan(a):
    root = expand(a.dir).resolve()
    if not root.is_dir():
        die(f"not a directory: {root}")
    found = []

    def walk(d, depth):
        if (d / ".git").exists():
            found.append(d)
            return
        if depth >= a.depth:
            return
        try:
            for c in sorted(d.iterdir()):
                if c.is_dir() and c.name not in SKIP_DIRS and not c.name.startswith("."):
                    walk(c, depth + 1)
        except PermissionError:
            pass

    walk(root, 0)
    print("name\tpath\tremote\tlast_commit\thome_repo\tinstructions")
    for p in found:
        remote, last, is_home, instr = repo_info(p)
        name = re.sub(r"[^a-z0-9-]+", "-", p.name.lower()).strip("-")
        print(f"{name}\t{p}\t{remote}\t{last}\t{'yes' if is_home else 'no'}\t{','.join(instr)}")


def cmd_status(a):
    home = find_home(a.home)
    if not home:
        print("home_repo: no")
        return
    local, example = read_map(home / LOCAL), read_map(home / EXAMPLE)
    print(f"home_repo: yes\nroot: {home}")
    print("name\tpath\tstate\tremote")
    for name in sorted(set(local) | set(example)):
        p = local.get(name, "")
        state = "no-path" if not p else ("ok" if expand(p).is_dir() else "missing")
        if name not in example:
            state += ",not-in-example"
        print(f"{name}\t{p}\t{state}\t{example.get(name, '')}")


# ---------- install / set / remove / init-paths ----------

def ensure_gitignore(home):
    gi = home / ".gitignore"
    lines = gi.read_text().splitlines() if gi.exists() else []
    if LOCAL not in lines:
        lines.append(LOCAL)
        gi.write_text("\n".join(lines) + "\n")
        return "added repos.local to .gitignore"
    return ".gitignore already ignores repos.local"


def install_hook(home):
    hooks = git("rev-parse", "--git-path", "hooks", cwd=home)
    if hooks is None:
        return "skipped pre-commit hook: not a git repo"
    hook = (home / hooks) / "pre-commit"
    if hook.exists() and HOOK_MARK not in hook.read_text():
        return f"skipped pre-commit hook: {hook} exists and is not minimap's; add `python3 {TOOL_DIR}/minimap.py check-paths` to it"
    hook.parent.mkdir(parents=True, exist_ok=True)
    hook.write_text(HOOK)
    hook.chmod(0o755)
    return "installed pre-commit hook"


def cmd_install(a):
    home = expand(a.home).resolve()
    home.mkdir(parents=True, exist_ok=True)
    out = []
    if git("rev-parse", "--show-toplevel", cwd=home) != str(home):
        subprocess.run(["git", "init", "-q"], cwd=home, check=True)
        out.append("ran git init")
    dest = home / TOOL_DIR / "minimap.py"
    dest.parent.mkdir(parents=True, exist_ok=True)
    src = Path(__file__).resolve()
    if src != dest.resolve():
        shutil.copyfile(src, dest)
        out.append(f"copied script to {TOOL_DIR}/minimap.py")
    for f, header in ((home / EXAMPLE, EXAMPLE_HEADER), (home / LOCAL, LOCAL_HEADER)):
        if not f.exists():
            write_map(f, {}, header)
            out.append(f"created {f.name}")
    out.append(ensure_gitignore(home))
    out.append(install_hook(home))
    print("\n".join(out))


def cmd_set(a):
    if not NAME_RE.match(a.name):
        die(f"bad name {a.name!r}: use lowercase letters, digits, and '-'")
    home = require_home(None)
    path = expand(a.path).resolve()
    local, example = read_map(home / LOCAL), read_map(home / EXAMPLE)
    local[a.name] = str(path)
    remote = a.remote if a.remote is not None else (
        example.get(a.name) or (git("remote", "get-url", "origin", cwd=path) if path.is_dir() else "") or "")
    example[a.name] = remote
    write_map(home / LOCAL, local, LOCAL_HEADER)
    write_map(home / EXAMPLE, example, EXAMPLE_HEADER)
    print(f"{a.name}: {path} (remote: {remote or 'none'})")


def cmd_remove(a):
    home = require_home(None)
    local, example = read_map(home / LOCAL), read_map(home / EXAMPLE)
    if a.name not in local and a.name not in example:
        die(f"unknown repo {a.name!r}")
    local.pop(a.name, None)
    example.pop(a.name, None)
    write_map(home / LOCAL, local, LOCAL_HEADER)
    write_map(home / EXAMPLE, example, EXAMPLE_HEADER)
    print(f"removed {a.name}; remove its {{{{{a.name}}}}} references from the map by hand")


def cmd_init_paths(a):
    home = require_home(None)
    local, example = read_map(home / LOCAL), read_map(home / EXAMPLE)
    interactive = sys.stdin.isatty() and not a.root
    for name, remote in sorted(example.items()):
        if local.get(name) and expand(local[name]).is_dir():
            print(f"{name}: ok")
            continue
        if a.root:
            target = expand(a.root).resolve() / name
        elif interactive:
            ans = input(f"{name} ({remote or 'no remote'}) path: ").strip()
            if not ans:
                print(f"{name}: skipped")
                continue
            target = expand(ans).resolve()
        else:
            print(f"{name}: no path; rerun with --root DIR or run interactively")
            continue
        if not target.is_dir():
            if a.clone and remote:
                r = subprocess.run(["git", "clone", "-q", remote, str(target)])
                if r.returncode != 0:
                    print(f"{name}: clone failed")
                    continue
                print(f"{name}: cloned into {target}")
            else:
                print(f"{name}: {target} missing; clone with: git clone {remote or '<remote>'} {target}")
        local[name] = str(target)
    write_map(home / LOCAL, local, LOCAL_HEADER)
    print(ensure_gitignore(home))
    print(install_hook(home))


# ---------- load ----------

IMPORT_RE = re.compile(r"^@(\S+)$")


def nested_instruction_files(repo):
    listed = git("ls-files", "--cached", "--others", "--exclude-standard", cwd=repo)
    if listed is not None:
        files = [Path(f) for f in listed.splitlines()]
    else:
        files = []
        for d, dirs, names in os.walk(repo):
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
            files += [Path(d).relative_to(repo) / n for n in names]
    return sorted(f for f in files if f.name in INSTRUCTION_NAMES and len(f.parts) > 1)


def cmd_load(a):
    home = require_home(None)
    local, example = read_map(home / LOCAL), read_map(home / EXAMPLE)
    name = a.name.strip("{}")
    tag = "{{" + name + "}}"
    if name not in local and name not in example:
        die(f"unknown repo {tag}; known: {', '.join(sorted(set(local) | set(example))) or 'none'}")
    repo = expand(local[name]) if local.get(name) else None
    if not repo or not repo.is_dir():
        remote = example.get(name) or "<remote>"
        die(f"{tag} is not on this machine. Ask the user where to clone it, then run:\n"
            f"  git clone {remote} <path>\n"
            f"  python3 {TOOL_DIR}/minimap.py set {name} <path>")
    printed = set()

    def emit(rel, label):
        p = (repo / rel).resolve()
        if p in printed or not p.is_file():
            return
        printed.add(p)
        text = p.read_text(errors="replace")
        print(f"=== {tag} instructions: {label} ===")
        body = []
        for line in text.splitlines():
            m = IMPORT_RE.match(line.strip())
            target = (p.parent / expand(m.group(1))).resolve() if m else None
            if target and target.is_file():
                if target in printed:
                    body.append(f"[{line.strip()}: already printed above]")
                else:
                    printed.add(target)
                    body.append(f"--- import {line.strip()} ---")
                    body.append(target.read_text(errors="replace").rstrip())
                    body.append(f"--- end import {line.strip()} ---")
            else:
                body.append(line)
        print("\n".join(body).rstrip())
        print(f"=== end {tag} instructions: {label} ===\n")

    for f in ROOT_INSTRUCTIONS:
        p = repo / f
        if not p.is_file():
            continue
        lines = [x.strip() for x in p.read_text(errors="replace").splitlines() if x.strip()]
        if len(lines) == 1 and IMPORT_RE.match(lines[0]):
            target = (repo / expand(lines[0][1:])).resolve()
            if target in printed:
                continue
        emit(f, f)
    if not printed:
        print(f"{tag} has no instruction files at its root.")
    nested = nested_instruction_files(repo)
    if nested:
        print(f"=== {tag} nested instruction files (read one before working in its folder) ===")
        for f in nested:
            print(f"{tag}/{f.as_posix()}")
        print(f"=== end {tag} nested instruction files ===")
    print(f"\n{tag} root: {repo}")


# ---------- check-paths ----------

def cmd_check_paths(a):
    home = find_home(None) or Path(git("rev-parse", "--show-toplevel") or os.getcwd())
    local = read_map(home / LOCAL)
    needles = set()
    for v in local.values():
        if v:
            needles.add(v)
            needles.add(str(expand(v)))
    if a.all:
        files = (git("ls-files", cwd=home) or "").splitlines()
        read = lambda f: (home / f).read_text(errors="replace") if (home / f).is_file() else ""
    else:
        files = (git("diff", "--cached", "--name-only", "--diff-filter=ACMR", cwd=home) or "").splitlines()
        read = lambda f: git("show", f":{f}", cwd=home) or ""
    skip = {LOCAL, f"{TOOL_DIR}/minimap.py"}
    hits = []
    for f in files:
        if f in skip:
            continue
        for n, line in enumerate(read(f).splitlines(), 1):
            if ALLOW_MARK in line:
                continue
            if any(x in line for x in needles) or ABS_PATH_RE.search(line):
                hits.append(f"{f}:{n}: {line.strip()[:120]}")
    if LOCAL in files:
        hits.insert(0, f"{LOCAL}: this file is gitignored for a reason; unstage it")
    if hits:
        print("Local paths found. Use {{name}} placeholders instead "
              f"(or end the line with '{ALLOW_MARK}' if it is not a local path):", file=sys.stderr)
        print("\n".join(hits), file=sys.stderr)
        sys.exit(1)
    print("no local paths found")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="minimap.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan"); s.add_argument("dir"); s.add_argument("--depth", type=int, default=3)
    s.set_defaults(fn=cmd_scan)
    s = sub.add_parser("status"); s.add_argument("--home"); s.set_defaults(fn=cmd_status)
    s = sub.add_parser("install"); s.add_argument("home"); s.set_defaults(fn=cmd_install)
    s = sub.add_parser("set"); s.add_argument("name"); s.add_argument("path"); s.add_argument("--remote")
    s.set_defaults(fn=cmd_set)
    s = sub.add_parser("remove"); s.add_argument("name"); s.set_defaults(fn=cmd_remove)
    s = sub.add_parser("init-paths"); s.add_argument("--root"); s.add_argument("--clone", action="store_true")
    s.set_defaults(fn=cmd_init_paths)
    s = sub.add_parser("load"); s.add_argument("name"); s.set_defaults(fn=cmd_load)
    s = sub.add_parser("check-paths"); s.add_argument("--all", action="store_true")
    s.set_defaults(fn=cmd_check_paths)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
