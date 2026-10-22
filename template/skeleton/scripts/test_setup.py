"""Tests for setup.py and privacy_check.py. Run: python3 -m unittest discover -s scripts"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import privacy_check as pc  # noqa: E402
import setup  # noqa: E402


class Kit(unittest.TestCase):
    """A temp copy of the kit's shape: the private layer, a KB settings file and template-sync."""

    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        for rel in ["notes/lessons/_template.md", "notes/index.md", "outbox/README.md", "hub.toml",
                    "scripts/notes.py", ".github/workflows/rollup.yml", ".github/workflows/template-sync.yml",
                    ".github/workflows/kb-auto-merge.yml", ".github/workflows/kb-validate.yml",
                    "sandbox/RULES.md", "sandbox/tasks/_template.md"]:
            p = self.root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("## Lessons\n" if rel.endswith("index.md") else "x\n")
        (self.root / "AGENTS.md").write_text("# Instructions\n\nThe rest.\n")
        kb = self.root / setup.KB_TOML
        kb.parent.mkdir(parents=True)
        kb.write_text(f'name = "my-kb"\n{setup.PRIVATE_IGNORE}\n')

    def add_note(self):
        (self.root / "notes/lessons/a-lesson.md").write_text("---\ntitle: A\n---\n")

    def git_origin(self):
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "remote", "add", "origin", "git@github.com:octo/vault.git"], cwd=self.root, check=True)

    def commit_all(self):
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True)
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "--no-verify", "-qm", "c"],
                       cwd=self.root, check=True)

    def make_sandbox(self):
        self.git_origin()
        return setup.setup_sandbox(self.root, status=lambda r: 404)


class PrivacyCheckTests(Kit):
    def test_empty_kit_has_no_real_content(self):
        self.assertEqual(pc.real_content(self.root), [])

    def test_notes_directives_and_index_lines_count(self):
        self.add_note()
        (self.root / "outbox/d-20260101-1.toml").write_text('id = "d-20260101-1"\n')
        (self.root / "notes/index.md").write_text("## Lessons\n\n- [A](lessons/a-lesson.md): a\n")
        self.assertEqual(pc.real_content(self.root),
                         ["notes/lessons/a-lesson.md", "notes/index.md", "outbox/d-20260101-1.toml"])

    def test_private_repo_passes(self):
        self.add_note()
        self.assertEqual(pc.check_ci(private=True, template=False, root=self.root), [])

    def test_public_copy_with_the_layer_fails_even_empty(self):
        self.assertIn("run `python3 scripts/setup.py --public`", pc.check_ci(False, False, self.root)[0])

    def test_public_template_passes_only_while_empty(self):
        self.assertEqual(pc.check_ci(False, True, self.root), [])
        self.add_note()
        self.assertIn("notes/lessons/a-lesson.md", pc.check_ci(False, True, self.root)[0])

    def test_public_repo_without_the_layer_passes(self):
        setup.setup_public(self.root)
        self.assertEqual(pc.check_ci(False, False, self.root), [])

    def test_local_check_refuses_a_world_readable_origin(self):
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "remote", "add", "origin", "https://github.com/octo/vault.git"], cwd=self.root, check=True)
        self.assertEqual(pc.origin_repo(self.root), "octo/vault")
        self.assertTrue(pc.check_local(self.root, status=lambda r: 200)[0])
        self.assertEqual(pc.check_local(self.root, status=lambda r: 404), ([], []))
        errors, warnings = pc.check_local(self.root, status=lambda r: None)
        self.assertEqual(errors, [])
        self.assertTrue(warnings)


class SetupTests(Kit):
    def test_public_removes_the_layer_and_its_ignores(self):
        setup.setup_public(self.root)
        for rel in ["notes", "outbox", "hub.toml", "scripts/notes.py", ".github/workflows/rollup.yml",
                    ".github/workflows/template-sync.yml"]:
            self.assertFalse((self.root / rel).exists(), rel)
        self.assertIn("capture_ignore = []", (self.root / setup.KB_TOML).read_text())
        setup.setup_public(self.root)  # again: nothing left to do, no error

    def test_public_refuses_when_notes_exist(self):
        self.add_note()
        with self.assertRaises(SystemExit):
            setup.setup_public(self.root)
        self.assertTrue((self.root / "notes/lessons/a-lesson.md").exists())

    def test_private_needs_github_to_confirm(self):
        self.git_origin()
        for code in (200, 403, None):
            with self.assertRaises(SystemExit):
                setup.setup_private(self.root, status=lambda r, c=code: c)
        setup.setup_private(self.root, status=lambda r: 404)
        self.assertTrue((self.root / "notes").exists())
        self.assertFalse((self.root / ".github/workflows/template-sync.yml").exists())
        self.assertIn("privacy_check.py", (self.root / ".git/hooks/pre-commit").read_text())

    def test_private_and_public_remove_the_sandbox(self):
        self.git_origin()
        setup.setup_private(self.root, status=lambda r: 404)
        self.assertFalse((self.root / "sandbox").exists())
        setup.setup_public(self.root)
        self.assertFalse((self.root / "sandbox").exists())

    def test_every_listed_path_is_in_the_kit(self):
        kit = Path(__file__).resolve().parents[1]
        if not (kit / "hub.toml").exists():
            self.skipTest("set up as public or sandbox: the private layer is gone")
        missing = [rel for rel in setup.PRIVATE_LAYER + setup.SANDBOX_DROPS + [setup.RULES] if not (kit / rel).exists()]
        self.assertEqual(missing, [])


class SandboxTests(Kit):
    def test_sandbox_drops_the_layer_and_self_merging_workflows(self):
        self.make_sandbox()
        for rel in ["notes", "outbox", "hub.toml", ".github/workflows/kb-auto-merge.yml",
                    ".github/workflows/template-sync.yml"]:
            self.assertFalse((self.root / rel).exists(), rel)
        self.assertTrue((self.root / ".github/workflows/kb-validate.yml").exists())
        agents = (self.root / "AGENTS.md").read_text()
        self.assertTrue(agents.startswith("# Instructions\n\n" + pc.SANDBOX_MARK))
        self.assertIn("The rest.", agents)
        self.assertEqual((self.root / "GEMINI.md").read_text(), setup.GEMINI)
        self.assertTrue(pc.is_sandbox(self.root))
        self.assertEqual(setup.setup_sandbox(self.root, status=lambda r: 404), [])  # again: no-op
        self.assertEqual(agents.count(pc.SANDBOX_MARK), 1)

    def test_sandbox_needs_github_to_confirm_private(self):
        with self.assertRaises(SystemExit):
            setup.setup_sandbox(self.root, status=lambda r: 404)  # no origin
        self.git_origin()
        with self.assertRaises(SystemExit):
            setup.setup_sandbox(self.root, status=lambda r: 200)
        self.assertTrue((self.root / "notes").exists())

    def test_sandbox_refuses_notes_now_or_in_history(self):
        self.git_origin()
        self.add_note()
        with self.assertRaises(SystemExit):
            setup.setup_sandbox(self.root, status=lambda r: 404)
        self.commit_all()
        (self.root / "notes/lessons/a-lesson.md").unlink()
        self.commit_all()
        self.assertEqual(pc.real_content(self.root), [])
        self.assertEqual(pc.real_content_in_history(self.root), ["notes/lessons/a-lesson.md"])
        with self.assertRaises(SystemExit):
            setup.setup_sandbox(self.root, status=lambda r: 404)

    def test_a_sandbox_cant_switch_modes(self):
        self.make_sandbox()
        with self.assertRaises(SystemExit):
            setup.setup_public(self.root)
        with self.assertRaises(SystemExit):
            setup.setup_private(self.root, status=lambda r: 404)

    def test_sandbox_check_catches_the_layer_and_leaks(self):
        self.make_sandbox()
        self.assertEqual(pc.check_ci(True, False, self.root), [])
        self.assertIn("this sandbox is public", pc.check_ci(False, False, self.root)[0])
        (self.root / "notes").mkdir()
        self.assertIn("holds the private layer", pc.check_ci(True, False, self.root)[0])
        shutil.rmtree(self.root / "notes")
        finding = self.root / "sandbox/findings/a.md"
        finding.parent.mkdir(parents=True)
        finding.write_text("Ask " + "someone" + "@" + "example.com, git" + "@github.com:o/r and " + "a" + "@" + "mail.co.uk.\n")
        self.assertIn("a.md:1: an email address", pc.check_ci(True, False, self.root)[0])
        finding.write_text("token " + "ghp_" + "a" * 30 + "\n")
        self.assertIn("a key or token", pc.check_ci(True, False, self.root)[0])
        finding.write_text("About Bluebird.\n")
        self.assertEqual(pc.check_local(self.root, status=lambda r: 404), ([], []))
        errors, _ = pc.check_local(self.root, status=lambda r: 404, words=["bluebird"])
        self.assertIn("a private name", errors[0])

    def test_sandbox_check_catches_names_in_history_and_wider_codespaces(self):
        self.make_sandbox()
        self.commit_all()
        self.assertEqual(pc.check_local(self.root, status=lambda r: 404, words=["bluebird"]), ([], []))
        subprocess.run(["git", "branch", "bluebird-notes"], cwd=self.root, check=True)
        errors, _ = pc.check_local(self.root, status=lambda r: 404, words=["bluebird"])
        self.assertIn("git history or a branch name", errors[0])
        dc = self.root / ".devcontainer/devcontainer.json"
        dc.parent.mkdir()
        dc.write_text('{"customizations": {"codespaces": {"repositories": {"octo/vault": {}}}}}')
        self.assertIn("other repos", pc.check_ci(True, False, self.root)[0])


if __name__ == "__main__":
    unittest.main()
