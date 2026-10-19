"""Check every note's front matter and list the ones due for review. Run before each commit.

    python3 scripts/stale_check.py [--today YYYY-MM-DD]

Fails (exit 1) on a note with missing or malformed front matter, or in the wrong folder for its type.
Lists, without failing:
  - notes past last_verified + review_after_days
  - goals not verified in 90 days, whatever their window
  - decisions past their revisit_on date
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta

import notes as n


def check(today: date) -> tuple[list[str], list[str]]:
    errors, due = [], []
    for path in n.notes():
        rel = "notes/" + path.relative_to(n.NOTES).as_posix()
        fm = n.front_matter(path.read_text(encoding="utf-8"))
        if fm is None:
            errors.append(f"{rel}: no front matter")
            continue
        expected = n.TYPES[path.parent.name]
        missing = [k for k in n.REQUIRED + n.EXTRA_REQUIRED.get(expected, []) if not fm.get(k)]
        if missing:
            errors.append(f"{rel}: missing {', '.join(missing)}")
            continue
        if fm["type"] != expected:
            errors.append(f"{rel}: type {fm['type']!r} doesn't match its folder ({expected})")
        verified = n.parse_date(fm["last_verified"])
        if verified is None or n.parse_date(fm["created"]) is None:
            errors.append(f"{rel}: created and last_verified must be YYYY-MM-DD")
            continue
        if fm["status"] != "active":
            continue
        try:
            window = int(fm["review_after_days"])
        except ValueError:
            errors.append(f"{rel}: review_after_days must be a number")
            continue
        if expected == "goal":
            window = min(window, n.GOAL_MAX_DAYS)
        if verified + timedelta(days=window) < today:
            due.append(f"{rel}: last verified {verified}, review every {window} days")
        if expected == "decision":
            revisit = n.parse_date(fm["revisit_on"])
            if revisit is None:
                errors.append(f"{rel}: revisit_on must be YYYY-MM-DD")
            elif revisit <= today:
                due.append(f"{rel}: revisit on {revisit}")
    return errors, due


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--today", type=date.fromisoformat, default=date.today())
    args = ap.parse_args()
    errors, due = check(args.today)
    for e in errors:
        print(f"error: {e}")
    for d in due:
        print(f"due: {d}")
    if not errors and not due:
        print("all notes current")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
