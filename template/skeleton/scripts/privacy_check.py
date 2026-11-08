"""Keep the private layer out of public repos.

    python3 scripts/privacy_check.py                                   # before a commit
    python3 scripts/privacy_check.py --ci --private BOOL --template BOOL  # in CI
    python3 scripts/privacy_check.py --words ../names.txt              # a sandbox, before seeding it

The private layer is notes/, outbox/ and hub.toml. Before a commit, this asks GitHub (no token)
whether the origin repo is world-readable, and refuses if it is and the layer is here. In CI it uses
the repo's real visibility: a public repo fails if it has the layer at all, unless it is the
template itself, and fails even then if the layer holds a real note or directive. The repo's
visibility is the only setting that counts; there is no config switch to get wrong.

A sandbox (set up with `setup.py --sandbox`, marked in AGENTS.md) must never hold the private layer,
and every file in it is scanned for key and token shapes, email addresses and platform IDs. That
scan is a backstop: the owner's yes to each batch is the control. `--words` adds a list of private
names, one per line, from a file kept outside the sandbox, since the sandbox's agents read every
file in it.

Self-contained and standard library only: it stays in public KBs after setup removes the layer, so
a notes/ folder that turns up later is still caught.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAYER = ["notes", "outbox", "hub.toml"]
TEMPLATE_FILES = {"_template.md"}
SANDBOX_MARK = "<!-- sandbox rules -->"
# devcontainer.json keys that reach other repos, mount host paths, widen the container or run on the host.
DEVCONTAINER_KEYS = ["repositories", "initializeCommand", "mounts", "workspaceMount", "runArgs",
                     "dockerComposeFile", "privileged", "capAdd", "securityOpt"]
BINARY = {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip", ".ico"}
LEAKS = [
    (re.compile(r"\b(sk-[\w-]{16,}|ghp_\w{20,}|gho_\w{20,}|github_pat_\w{20,}|xai-\w{16,}|AIza[\w-]{30,}|AKIA[0-9A-Z]{16})"),
     "a key or token"),
    (re.compile(r"\b(?!git@)[\w.+-]+@(?!(?:example\.(?:com|org|net)|contoso\.com)\b)[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}\b(?<!\.md)"),
     "an email address"),
    (re.compile(r"\b(env|trig|cse|session|chan|cmsg|skill|user|org|acct)_[0-9A-Za-z]{12,}"), "a platform ID"),
]


def layer_present(root: Path = ROOT) -> bool:
    return any((root / p).exists() for p in LAYER)


def real_content(root: Path = ROOT) -> list[str]:
    """Paths of real notes and directives: anything a person wrote, as opposed to the empty kit."""
    found = []
    notes = root / "notes"
    if notes.is_dir():
        for p in sorted(notes.glob("*/**/*.md")):
            if p.name not in TEMPLATE_FILES:
                found.append(p.relative_to(root).as_posix())
        index = notes / "index.md"
        if index.exists() and re.search(r"^\s*[-*] ", index.read_text(encoding="utf-8"), re.M):
            found.append("notes/index.md")
    outbox = root / "outbox"
    if outbox.is_dir():
        found += [p.relative_to(root).as_posix() for p in sorted(outbox.glob("*.toml"))]
    return found


def is_private_path(rel: str) -> bool:
    """A path a person wrote in the private layer, as opposed to the empty kit."""
    parts = rel.split("/")
    if parts[0] == "notes":
        return len(parts) > 2 and parts[-1] not in TEMPLATE_FILES
    return parts[0] == "outbox" and rel.endswith(".toml")


def real_content_in_history(root: Path = ROOT) -> list[str]:
    """Private-layer paths any commit ever held: a deleted note is still readable in history."""
    r = subprocess.run(["git", "log", "--all", "--name-only", "--format=", "--", "notes", "outbox"],
                       cwd=root, capture_output=True, text=True)
    return sorted({rel for rel in r.stdout.split("\n") if rel and is_private_path(rel)})


def is_sandbox(root: Path = ROOT) -> bool:
    agents = root / "AGENTS.md"
    return agents.exists() and SANDBOX_MARK in agents.read_text(encoding="utf-8", errors="replace")


def scan(root: Path = ROOT, words: list[str] = ()) -> list[str]:
    """Leak shapes and private names in a sandbox's files."""
    found = []
    for p in sorted(root.rglob("*")):
        parts = p.relative_to(root).parts
        if ".git" in parts or "__pycache__" in parts or not p.is_file() or p.suffix.lower() in BINARY:
            continue
        rel = p.relative_to(root).as_posix()
        text = p.read_text(encoding="utf-8", errors="replace")
        for n, line in enumerate(text.splitlines(), 1):
            found += [f"{rel}:{n}: {what}" for rx, what in LEAKS if rx.search(line)]
            low = line.lower()
            found += [f"{rel}:{n}: a private name" for w in words if w in low]
    return found


def scan_history(root: Path, words: list[str]) -> list[str]:
    """Private names in what file scans miss: commit messages, author names and branch names."""
    if not words:
        return []
    log = subprocess.run(["git", "log", "--all", "--format=%an%n%cn%n%B"], cwd=root, capture_output=True, text=True).stdout
    refs = subprocess.run(["git", "for-each-ref", "--format=%(refname:short)"], cwd=root, capture_output=True, text=True).stdout
    low = (log + refs).lower()
    return ["git history or a branch name: a private name" for w in words if w in low]


def read_words(path: Path) -> list[str]:
    return [w.strip().lower() for w in path.read_text(encoding="utf-8").splitlines()
            if w.strip() and not w.lstrip().startswith("#")]


def check_sandbox(root: Path = ROOT, words: list[str] = ()) -> list[str]:
    if not is_sandbox(root):
        return []
    errors = []
    if layer_present(root):
        errors.append("this sandbox holds the private layer (notes/, outbox/ or hub.toml). Remove it, and "
                      "treat anything in it as shared with the sandbox's agents.")
    for dc in [root / ".devcontainer.json", *sorted((root / ".devcontainer").rglob("devcontainer.json"))]:
        if dc.exists():
            text = dc.read_text(encoding="utf-8", errors="replace")
            keys = [k for k in DEVCONTAINER_KEYS if f'"{k}"' in text]
            if keys:
                errors.append(f"{dc.relative_to(root).as_posix()} sets {', '.join(keys)}: that reaches past this repo or "
                              "runs on the host. A sandbox's container must see only this repo.")
    hits = scan(root, words) + scan_history(root, words)
    return errors + [f"{hit}. Remove it before it goes further." for hit in hits]


def origin_repo(root: Path = ROOT) -> str | None:
    """owner/repo of a github.com origin remote, or None."""
    r = subprocess.run(["git", "remote", "get-url", "origin"], cwd=root, capture_output=True, text=True)
    m = re.search(r"github\.com[:/]([\w.-]+)/([\w.-]+?)(?:\.git)?/?$", r.stdout.strip())
    return f"{m.group(1)}/{m.group(2)}" if m else None


def public_status(repo: str) -> int | None:
    """HTTP status of an unauthenticated GET for the repo: 200 means anyone can read it, 404 means
    private (or missing). None when GitHub can't be reached."""
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}",
                                 headers={"User-Agent": "privacy-check", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except (urllib.error.URLError, TimeoutError, OSError):
        return None


def check_ci(private: bool, template: bool, root: Path = ROOT) -> list[str]:
    sandbox = check_sandbox(root)
    if is_sandbox(root) and not private:
        sandbox.append("this sandbox is public. Make it private now and treat its contents as exposed.")
    if sandbox:
        return sandbox
    if private or not layer_present(root):
        return []
    content = real_content(root)
    if content:
        return [f"this repo is public and holds private-layer content: {', '.join(content)}. "
                "Make the repo private now and treat that content as exposed."]
    if template:
        return []
    return ["this repo is public and has the private layer (notes/, outbox/, hub.toml). "
            "Make the repo private, or run `python3 scripts/setup.py --public` to remove the layer."]


def check_local(root: Path = ROOT, status=public_status, words: list[str] = ()) -> tuple[list[str], list[str]]:
    """(errors, warnings) before a commit."""
    sandbox = check_sandbox(root, words)
    if sandbox:
        return sandbox, []
    if not layer_present(root):
        return [], []
    repo = origin_repo(root)
    if not repo:
        return [], []
    code = status(repo)
    if code == 200:
        return [f"{repo} is public and this repo has the private layer. Make it private before committing."], []
    if code == 404:
        return [], []
    return [], [f"couldn't confirm {repo} is private (GitHub answered {code}); CI checks it again."]


def flag(value: str) -> bool:
    return value.strip().lower() == "true"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ci", action="store_true", help="use the visibility CI passes in instead of asking GitHub")
    ap.add_argument("--private", default="false", help="CI: github.event.repository.private")
    ap.add_argument("--template", default="false", help="CI: whether this repo is the template itself")
    ap.add_argument("--words", type=Path, help="a sandbox: file of private names, one per line, kept outside it")
    args = ap.parse_args()
    if args.ci:
        errors, warnings = check_ci(flag(args.private), flag(args.template)), []
    else:
        errors, warnings = check_local(words=read_words(args.words) if args.words else [])
    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"::error::{e}" if args.ci else f"error: {e}")
    if not errors:
        print("privacy check passed")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
