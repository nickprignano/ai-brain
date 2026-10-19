"""Keep the private layer out of public repos.

    python3 scripts/privacy_check.py                                   # before a commit
    python3 scripts/privacy_check.py --ci --private BOOL --template BOOL  # in CI

The private layer is notes/, outbox/ and hub.toml. Before a commit, this asks GitHub (no token)
whether the origin repo is world-readable, and refuses if it is and the layer is here. In CI it uses
the repo's real visibility: a public repo fails if it has the layer at all, unless it is the
template itself, and fails even then if the layer holds a real note or directive. The repo's
visibility is the only setting that counts; there is no config switch to get wrong.

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


def check_local(root: Path = ROOT, status=public_status) -> tuple[list[str], list[str]]:
    """(errors, warnings) before a commit."""
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
    args = ap.parse_args()
    if args.ci:
        errors, warnings = check_ci(flag(args.private), flag(args.template)), []
    else:
        errors, warnings = check_local()
    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"::error::{e}" if args.ci else f"error: {e}")
    if not errors:
        print("privacy check passed")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
