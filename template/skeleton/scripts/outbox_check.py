"""Check the directives waiting in outbox/ before they can leave this repo.
Self-contained on purpose: the same file runs in every private layer built from this kit.

    python3 scripts/outbox_check.py

A directive carries only the instruction. This fails (exit 1) on any entry that:
  - is missing a field or has a bad id, scope, pause name, status or date
  - is longer than 280 characters
  - contains anything that points back inside this repo: a [[link]], a notes/ path, a URL, an
    email address, or a name listed in hub.toml's private_names
And it fails if more than three entries are still queued.
"""

from __future__ import annotations

import re
import sys
import tomllib
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTBOX = ROOT / "outbox"
SETTINGS = ROOT / "hub.toml"

MAX_LENGTH = 280
MAX_QUEUED = 3
STATUSES = {"queued", "sent", "cancelled"}
ID = re.compile(r"^d-\d{8}-\d+$")
LEAKS = [
    (re.compile(r"\[\["), "a [[link]]"),
    (re.compile(r"notes/"), "a notes/ path"),
    (re.compile(r"https?://"), "a URL"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "an email address"),
]


def settings() -> dict:
    with SETTINGS.open("rb") as f:
        return tomllib.load(f)


def is_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def check_entry(entry: dict, cfg: dict) -> list[str]:
    problems = []
    for field in ("id", "directive", "scope", "status"):
        if field not in entry:
            problems.append(f"missing {field}")
    if problems:
        return problems
    if not ID.match(str(entry["id"])):
        problems.append("id must look like d-YYYYMMDD-n")
    text = str(entry["directive"])
    if not text.strip():
        problems.append("directive is empty")
    if len(text) > MAX_LENGTH:
        problems.append(f"directive is {len(text)} characters; the limit is {MAX_LENGTH}")
    if not isinstance(entry["scope"], list) or not entry["scope"]:
        problems.append("scope must be a non-empty list, such as [\"all\"]")
    pausable = set(cfg.get("pausable", []))
    for name in entry.get("pause", []):
        if name not in pausable:
            problems.append(f"pause {name!r} isn't one of {sorted(pausable)}")
    if entry["status"] not in STATUSES:
        problems.append(f"status must be one of {sorted(STATUSES)}")
    if "until" in entry and not is_date(str(entry["until"])):
        problems.append("until must be YYYY-MM-DD")
    for pattern, what in LEAKS:
        if pattern.search(text):
            problems.append(f"directive contains {what}")
    lowered = text.lower()
    for name in cfg.get("private_names", []):
        if name and not name.startswith("<") and name.lower() in lowered:
            problems.append(f"directive names {name!r}, which is private")
    return problems


def check(outbox: Path = OUTBOX, cfg: dict | None = None) -> list[str]:
    cfg = settings() if cfg is None else cfg
    errors, queued = [], 0
    for path in sorted(outbox.glob("*.toml")):
        try:
            with path.open("rb") as f:
                entry = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            errors.append(f"{path.name}: not valid TOML ({e})")
            continue
        errors += [f"{path.name}: {p}" for p in check_entry(entry, cfg)]
        queued += entry.get("status") == "queued"
    if queued > MAX_QUEUED:
        errors.append(f"{queued} directives are queued; send or cancel some first (limit {MAX_QUEUED})")
    return errors


def main() -> int:
    errors = check()
    for e in errors:
        print(f"error: {e}")
    print("outbox is clean" if not errors else f"{len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
