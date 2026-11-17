"""Changed cases for the local estimate-commitment model, not AWS billing."""

from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
from threading import Barrier, Thread
import unittest

from lab import commit, create_register


class CreditCommitmentTests(unittest.TestCase):
    def test_three_contenders_cannot_claim_more_than_headroom(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "register.sqlite3"
            create_register(path)
            gate = Barrier(4)
            results = []
            errors = []

            def contender(run_id):
                try:
                    gate.wait(timeout=3)
                    results.append(commit(path, run_id, 300))
                except BaseException as error:
                    errors.append(error)

            threads = [Thread(target=contender, args=(name,)) for name in ("A", "B", "C")]
            for thread in threads:
                thread.start()
            gate.wait(timeout=3)
            for thread in threads:
                thread.join(timeout=3)
                self.assertFalse(thread.is_alive())
            self.assertEqual(errors, [])
            self.assertEqual(sorted(results), [False, False, True])
            with sqlite3.connect(path) as db:
                self.assertEqual(db.execute("SELECT SUM(estimate_cents) FROM commitments").fetchone()[0], 300)

    def test_duplicate_id_is_denied_before_the_headroom_check(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "register.sqlite3"
            create_register(path)
            self.assertTrue(commit(path, "A", 100))
            self.assertFalse(commit(path, "A", 100))
            self.assertFalse(commit(path, "B", 500))
            with sqlite3.connect(path) as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM commitments").fetchone()[0], 1)

    def test_invalid_estimates_do_not_write(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "register.sqlite3"
            create_register(path)
            for value in (0, -1, 501, True, 1.5, float('nan')):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    commit(path, "bad", value)
            for run_id in (None, "", "   "):
                with self.subTest(run_id=run_id), self.assertRaises(ValueError):
                    commit(path, run_id, 100)
            with sqlite3.connect(path) as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM commitments").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
