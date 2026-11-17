"""Exercise the manual publisher's stale-source stop against a local Git remote."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "check-publisher-source-head.py"


def git(*args: str, cwd: Path) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


class SourceHeadTests(unittest.TestCase):
    def test_current_commit_passes_then_queued_old_commit_stops(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            remote, author, runner = (root / name for name in ("remote.git", "author", "runner"))
            git("init", "--bare", str(remote), cwd=root)
            git("init", "-b", "main", str(author), cwd=root)
            git("config", "user.name", "Local Test", cwd=author)
            git("config", "user.email", "local@example.invalid", cwd=author)
            (author / "lesson.txt").write_text("first\n")
            git("add", "lesson.txt", cwd=author)
            git("commit", "-m", "first", cwd=author)
            git("remote", "add", "origin", str(remote), cwd=author)
            git("push", "-u", "origin", "main", cwd=author)
            git("-C", str(remote), "symbolic-ref", "HEAD", "refs/heads/main", cwd=root)
            git("clone", str(remote), str(runner), cwd=root)
            first = git("rev-parse", "HEAD", cwd=runner)

            environment = {**os.environ, "SOURCE_COMMIT": first}
            current = subprocess.run(["python3", str(SCRIPT)], cwd=runner, env=environment,
                                     capture_output=True, text=True)
            self.assertEqual(current.returncode, 0, current.stderr)
            self.assertIn("Current main matches", current.stdout)

            (author / "lesson.txt").write_text("second\n")
            git("commit", "-am", "second", cwd=author)
            git("push", "origin", "main", cwd=author)
            stale = subprocess.run(["python3", str(SCRIPT)], cwd=runner, env=environment,
                                   capture_output=True, text=True)
            self.assertNotEqual(stale.returncode, 0)
            self.assertIn("Main advanced", stale.stderr)

    def test_missing_identity_stops_before_git(self):
        with tempfile.TemporaryDirectory() as folder:
            environment = {**os.environ, "SOURCE_COMMIT": ""}
            result = subprocess.run(["python3", str(SCRIPT)], cwd=folder, env=environment,
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing exact workflow source commit", result.stderr)


if __name__ == "__main__":
    unittest.main()
