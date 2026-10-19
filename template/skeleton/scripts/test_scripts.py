"""Tests for this private layer's scripts. Run: python3 -m unittest discover -s scripts"""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import notes as n  # noqa: E402
import outbox_check  # noqa: E402
import rollup  # noqa: E402
import stale_check  # noqa: E402

CFG = {"private_names": ["my-vault"], "pausable": ["all", "kb-curator"], "hub_repo": "octo/hub"}


def note(folder: str, name: str, **fields) -> None:
    base = {"title": "T", "type": n.TYPES[folder], "created": "2026-01-01", "last_verified": "2026-01-01",
            "review_after_days": "180", "status": "active"}
    base.update(fields)
    fm = "\n".join(f"{k}: {v}" for k, v in base.items())
    (n.NOTES / folder / name).write_text(f"---\n{fm}\n---\n\n# T\n")


class TempNotes(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        for folder in n.TYPES:
            (self.tmp / folder).mkdir()
        p = mock.patch.object(n, "NOTES", self.tmp)
        p.start()
        self.addCleanup(p.stop)
        self.addCleanup(shutil.rmtree, self.tmp)


class StaleTests(TempNotes):
    def test_templates_are_valid_notes(self):
        real = Path(__file__).resolve().parents[1] / "notes"
        for folder in n.TYPES:
            text = (real / folder / "_template.md").read_text()
            fm = n.front_matter(text)
            self.assertEqual(fm["type"], n.TYPES[folder])
            for key in n.REQUIRED + n.EXTRA_REQUIRED.get(n.TYPES[folder], []):
                self.assertIn(key, fm, f"{folder}/_template.md lacks {key}")

    def test_due_and_current(self):
        note("lessons", "old.md")
        note("lessons", "fresh.md", last_verified="2026-10-01")
        errors, due = stale_check.check(date(2026, 10, 18))
        self.assertEqual(errors, [])
        self.assertEqual(len(due), 1)
        self.assertIn("old.md", due[0])

    def test_goals_cap_and_revisit(self):
        note("goals", "g.md", last_verified="2026-06-01", review_after_days="365")
        note("decisions", "d.md", last_verified="2026-10-01", revisit_on="2026-10-10")
        _, due = stale_check.check(date(2026, 10, 18))
        self.assertTrue(any("g.md" in d for d in due))
        self.assertTrue(any("revisit on" in d for d in due))

    def test_errors(self):
        (n.NOTES / "lessons" / "bare.md").write_text("# no front matter\n")
        note("patterns", "p.md")  # no sources
        note("rca", "r.md", type="lesson")
        errors, _ = stale_check.check(date(2026, 10, 18))
        self.assertEqual(len(errors), 3)


class OutboxTests(unittest.TestCase):
    GOOD = {"id": "d-20261018-1", "directive": "Pause the weekly digest.", "scope": ["all"],
            "pause": ["kb-curator"], "status": "queued", "until": "2026-11-01"}

    def test_good(self):
        self.assertEqual(outbox_check.check_entry(self.GOOD, CFG), [])

    def test_leaks_refused(self):
        for text in ("See [[some note]]", "per notes/lessons/x.md", "https://example.com",
                     "ask a@example.com", "as my-vault says", "x" * 281):
            with self.subTest(text=text[:20]):
                self.assertTrue(outbox_check.check_entry({**self.GOOD, "directive": text}, CFG))

    def test_bad_fields(self):
        self.assertTrue(outbox_check.check_entry({**self.GOOD, "pause": ["rm-rf"]}, CFG))
        self.assertTrue(outbox_check.check_entry({**self.GOOD, "id": "1"}, CFG))
        self.assertTrue(outbox_check.check_entry({k: v for k, v in self.GOOD.items() if k != "scope"}, CFG))

    def test_queue_limit(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp)
        for i in range(4):
            (tmp / f"d{i}.toml").write_text(
                f'id = "d-20261018-{i}"\ndirective = "Pause."\nscope = ["all"]\nstatus = "queued"\n')
        errors = outbox_check.check(tmp, CFG)
        self.assertEqual(len(errors), 1)
        self.assertIn("4 directives are queued", errors[0])

    def test_example_outbox_is_clean(self):
        self.assertEqual(outbox_check.check(), [])


class RollupTests(unittest.TestCase):
    def test_render(self):
        fetch = {"issues": lambda repo, label, since: [f"- [ ] {label}"] if label == "kb-digest" else [],
                 "commits": lambda repo, path, since: []}
        body = rollup.render(CFG, 8, False, fetch)
        self.assertIn("- [ ] kb-digest", body)
        self.assertIn("## Decisions\n\nNothing new.", body)
        monthly = rollup.render(CFG, 8, True, fetch, stale=lambda: "all notes current")
        self.assertIn("## This repo's notes\n\n```\nall notes current\n```", monthly)


if __name__ == "__main__":
    unittest.main()
