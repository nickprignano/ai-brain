"""Shared helpers for this private layer's scripts: paths, settings and note front matter.

Standard library only (Python 3.11+), so the checks run anywhere without installs.
"""

from __future__ import annotations

import re
import tomllib
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES = ROOT / "notes"
OUTBOX = ROOT / "outbox"
SETTINGS = ROOT / "hub.toml"

TYPES = {
    "lessons": "lesson",
    "rca": "rca",
    "procedures": "procedure",
    "decisions": "decision",
    "goals": "goal",
    "disagreements": "disagreement",
    "patterns": "pattern",
}
REQUIRED = ["title", "type", "created", "last_verified", "review_after_days", "status"]
EXTRA_REQUIRED = {"decision": ["revisit_on"], "pattern": ["sources"]}
GOAL_MAX_DAYS = 90

FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
LINE = re.compile(r"^([a-z_]+):\s*(.*?)\s*(?:#.*)?$")


def settings() -> dict:
    with SETTINGS.open("rb") as f:
        return tomllib.load(f)


def front_matter(text: str) -> dict | None:
    """Flat `key: value` front matter. Lists are kept as their raw text, such as `[]`."""
    m = FRONT_MATTER.match(text)
    if not m:
        return None
    out = {}
    for line in m.group(1).splitlines():
        lm = LINE.match(line)
        if lm:
            out[lm.group(1)] = lm.group(2).strip().strip('"').strip("'")
    return out


def notes() -> list[Path]:
    """Every note, leaving out the per-folder templates."""
    return sorted(p for folder in TYPES for p in (NOTES / folder).glob("*.md") if p.name != "_template.md")


def parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None
