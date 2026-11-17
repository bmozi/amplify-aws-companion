"""Business-promise checks for the local A21 writer-choice exercise."""

import tempfile
import unittest
from pathlib import Path

from conflict_lab import collision, run, single_writer_transfer
from failback_lab import Store


class ConflictTests(unittest.TestCase):
    def stores(self, folder):
        root = Path(folder)
        return Store(root / "one.sqlite", "one"), Store(root / "two.sqlite", "two")

    def test_two_local_confirmations_cannot_both_survive_one_slot(self):
        with tempfile.TemporaryDirectory() as folder:
            first, second = self.stores(folder)
            try:
                result = collision(first, second, "second")
                self.assertEqual(result["both_confirmed"], ["r-alice", "r-bob"])
                self.assertEqual(result["visible_receipts"], ["r-bob"])
                self.assertEqual(result["missing_confirmed"], ["r-alice"])
                self.assertEqual(result["customer_promise"], "FAILED_RECONCILIATION_REQUIRED")
            finally:
                first.close()
                second.close()

    def test_reversing_toy_winner_changes_who_loses_not_the_defect(self):
        with tempfile.TemporaryDirectory() as folder:
            first, second = self.stores(folder)
            try:
                result = collision(first, second, "first")
                self.assertEqual(result["missing_confirmed"], ["r-bob"])
            finally:
                first.close()
                second.close()

    def test_invalid_winner_is_rejected_before_any_booking(self):
        with tempfile.TemporaryDirectory() as folder:
            first, second = self.stores(folder)
            try:
                with self.assertRaises(ValueError):
                    collision(first, second, "third")
                self.assertEqual(first.rows(), [])
                self.assertEqual(second.rows(), [])
            finally:
                first.close()
                second.close()

    def test_single_writer_handoff_preserves_first_and_rejects_duplicate_slot(self):
        with tempfile.TemporaryDirectory() as folder:
            first, second = self.stores(folder)
            try:
                result = single_writer_transfer(first, second)
                self.assertEqual(result["before_handoff"], "WRITE_CLOSED")
                self.assertEqual(result["copy_receipt"], "READY")
                self.assertEqual(result["same_slot"], "CONFLICT")
                self.assertEqual(result["other_slot"], "ACCEPTED")
                self.assertEqual(result["visible_receipts"], ["r-alice", "r-bob"])
            finally:
                first.close()
                second.close()

    def test_script_combines_the_two_separate_cases(self):
        result = run()
        self.assertEqual(result["two_writers"]["missing_confirmed"], ["r-alice"])
        self.assertEqual(result["one_writer_handoff"]["same_slot"], "CONFLICT")


if __name__ == "__main__":
    unittest.main()
