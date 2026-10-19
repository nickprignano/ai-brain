"""Set up your copy of the template as private (the default) or public. Run it once, right after
you make your copy.

    python3 scripts/setup.py            # private: keeps the private layer, checks the repo is private
    python3 scripts/setup.py --public   # public: removes the private layer for good

Private keeps notes/, outbox/ and hub.toml, refuses unless GitHub confirms the origin repo can't be
read without signing in, and installs a git pre-commit hook that runs privacy_check.py. Public
deletes the private layer and its workflows, and refuses if the layer already holds real notes.
Both remove template-sync.yml, which only the template repo itself runs. Running it again is safe.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import privacy_check  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ONLY = [".github/workflows/template-sync.yml"]
PRIVATE_LAYER = [
    "notes",
    "outbox",
    "hub.toml",
    "scripts/notes.py",
    "scripts/outbox_check.py",
    "scripts/rollup.py",
    "scripts/stale_check.py",
    "scripts/test_scripts.py",
    ".github/workflows/private-layer.yml",
    ".github/workflows/rollup.yml",
]
KB_TOML = "docs/knowledge/kb.toml"
PRIVATE_IGNORE = 'capture_ignore = ["notes/**", "outbox/**", "hub.toml"]'
HOOK = "#!/bin/sh\nexec python3 scripts/privacy_check.py\n"


def remove(root: Path, paths: list[str]) -> list[str]:
    gone = []
    for rel in paths:
        p = root / rel
        if p.is_dir():
            shutil.rmtree(p)
        elif p.exists():
            p.unlink()
        else:
            continue
        gone.append(rel)
    return gone


def setup_public(root: Path) -> list[str]:
    content = privacy_check.real_content(root)
    if content:
        raise SystemExit(f"error: the private layer already holds {', '.join(content)}. "
                         "Move it to a private repo before making this one public.")
    gone = remove(root, TEMPLATE_ONLY + PRIVATE_LAYER)
    kb = root / KB_TOML
    if kb.exists():
        kb.write_text(kb.read_text(encoding="utf-8").replace(PRIVATE_IGNORE, "capture_ignore = []"), encoding="utf-8")
    return gone


def setup_private(root: Path, status=privacy_check.public_status) -> list[str]:
    repo = privacy_check.origin_repo(root)
    if repo:
        code = status(repo)
        if code != 404:
            seen = "anyone can read it" if code == 200 else f"GitHub answered {code}"
            raise SystemExit(f"error: {repo} isn't confirmed private ({seen}). Make it private in "
                             "Settings > General > Danger Zone, then run this again.")
    gone = remove(root, TEMPLATE_ONLY)
    hooks = root / ".git" / "hooks"
    hook = hooks / "pre-commit"
    if hooks.is_dir() and not hook.exists():
        hook.write_text(HOOK, encoding="utf-8")
        hook.chmod(0o755)
    return gone


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--public", action="store_true", help="remove the private layer: this KB will be public")
    args = ap.parse_args()
    gone = setup_public(ROOT) if args.public else setup_private(ROOT)
    for rel in gone:
        print(f"removed {rel}")
    if args.public:
        print("Set up as a public knowledge base. Next: edit docs/knowledge/kb.toml (see README).")
    else:
        print("Set up as private. Next: edit hub.toml, then docs/knowledge/kb.toml (see README).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
