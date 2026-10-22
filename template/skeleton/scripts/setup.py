"""Set up your copy of the template as private (the default), public or a sandbox. Run it once,
right after you make your copy.

    python3 scripts/setup.py             # private: keeps the private layer, checks the repo is private
    python3 scripts/setup.py --public    # public: removes the private layer for good
    python3 scripts/setup.py --sandbox   # sandbox: a private repo for outside agents, no private layer

Private keeps notes/, outbox/ and hub.toml, refuses unless GitHub confirms the origin repo can't be
read without signing in, and installs a git pre-commit hook that runs privacy_check.py. Public
deletes the private layer and its workflows, and refuses if the layer already holds real notes.
Sandbox makes the same privacy check as private, then deletes the private layer like public, and
refuses if the layer holds real notes now or ever did in git history: a sandbox starts as a fresh
copy of the template, never a converted private repo. It also removes kb-auto-merge, adds
sandbox/RULES.md to the top of AGENTS.md, GEMINI.md and .agents/rules/sandbox.md. Private and public delete
sandbox/. All three remove template-sync.yml, which only the template repo itself runs. Running the
same mode again is safe; switching a sandbox to another mode is refused.
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
SANDBOX = ["sandbox", ".devcontainer"]
# An agent's PR opened with the owner's token counts as the owner's, so a sandbox never auto-merges.
SANDBOX_DROPS = [".github/workflows/kb-auto-merge.yml"]
RULES = "sandbox/RULES.md"
# Antigravity may not follow GEMINI.md's @ import, so the rules go in full in both of the files it reads.
GEMINI = "GEMINI.md"
AG_RULES = ".agents/rules/sandbox.md"
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


def refuse_if_sandbox(root: Path) -> None:
    if privacy_check.is_sandbox(root):
        raise SystemExit("error: this repo is set up as a sandbox for outside agents. Its contents count as "
                         "shared with them; start a fresh copy of the template for another mode.")


def drop_layer(root: Path) -> list[str]:
    gone = remove(root, TEMPLATE_ONLY + PRIVATE_LAYER)
    kb = root / KB_TOML
    if kb.exists():
        kb.write_text(kb.read_text(encoding="utf-8").replace(PRIVATE_IGNORE, "capture_ignore = []"), encoding="utf-8")
    return gone


def confirm_private(root: Path, status, need_origin: bool = False) -> None:
    repo = privacy_check.origin_repo(root)
    if not repo:
        if need_origin:
            raise SystemExit("error: no github.com origin remote, so GitHub can't confirm this repo is private. "
                             "Run this in a clone of the new repo.")
        return
    code = status(repo)
    if code != 404:
        seen = "anyone can read it" if code == 200 else f"GitHub answered {code}"
        raise SystemExit(f"error: {repo} isn't confirmed private ({seen}). Make it private in "
                         "Settings > General > Danger Zone, then run this again.")


def install_hook(root: Path) -> None:
    hooks = root / ".git" / "hooks"
    hook = hooks / "pre-commit"
    if hooks.is_dir() and not hook.exists():
        hook.write_text(HOOK, encoding="utf-8")
        hook.chmod(0o755)


def setup_public(root: Path) -> list[str]:
    refuse_if_sandbox(root)
    content = privacy_check.real_content(root)
    if content:
        raise SystemExit(f"error: the private layer already holds {', '.join(content)}. "
                         "Move it to a private repo before making this one public.")
    return drop_layer(root) + remove(root, SANDBOX)


def setup_private(root: Path, status=privacy_check.public_status) -> list[str]:
    refuse_if_sandbox(root)
    confirm_private(root, status)
    gone = remove(root, TEMPLATE_ONLY + SANDBOX)
    install_hook(root)
    return gone


def setup_sandbox(root: Path, status=privacy_check.public_status) -> list[str]:
    if privacy_check.is_sandbox(root):
        return []
    if not (root / RULES).exists():
        raise SystemExit(f"error: {RULES} is missing. Start from a fresh copy of the template.")
    content = privacy_check.real_content(root) + privacy_check.real_content_in_history(root)
    if content:
        raise SystemExit(f"error: this repo holds or once held private notes ({', '.join(sorted(set(content)))}). "
                         "Outside agents could read them in git history. Make the sandbox a fresh copy of the template.")
    confirm_private(root, status, need_origin=True)
    gone = drop_layer(root) + remove(root, SANDBOX_DROPS)
    agents = root / "AGENTS.md"
    text = agents.read_text(encoding="utf-8")
    title, _, rest = text.partition("\n")
    rules = (root / RULES).read_text(encoding="utf-8").strip()
    agents.write_text(f"{title}\n\n{privacy_check.SANDBOX_MARK}\n{rules}\n{rest}", encoding="utf-8")
    (root / AG_RULES).parent.mkdir(parents=True, exist_ok=True)
    (root / AG_RULES).write_text(f"{rules}\n\nRead AGENTS.md before you start.\n", encoding="utf-8")
    (root / GEMINI).write_text(f"{rules}\n\nRead AGENTS.md before you start.\n\n@AGENTS.md\n", encoding="utf-8")
    install_hook(root)
    return gone


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--public", action="store_true", help="remove the private layer: this KB will be public")
    mode.add_argument("--sandbox", action="store_true", help="a private repo for outside agents, with no private layer")
    args = ap.parse_args()
    if args.sandbox:
        gone = setup_sandbox(ROOT)
    else:
        gone = setup_public(ROOT) if args.public else setup_private(ROOT)
    for rel in gone:
        print(f"removed {rel}")
    if args.sandbox:
        print("Set up as a sandbox for outside agents. Next: read sandbox/README.md before adding anything.")
    elif args.public:
        print("Set up as a public knowledge base. Next: edit docs/knowledge/kb.toml (see README).")
    else:
        print("Set up as private. Next: edit hub.toml, then docs/knowledge/kb.toml (see README).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
