import tempfile
import unittest
from pathlib import Path

from restore_boundary import RestoreBoundary, demonstrate


class RestoreBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.case = RestoreBoundary(Path(self.folder.name))

    def tearDown(self):
        self.folder.cleanup()

    def test_old_app_snapshot_resurrects_rows_but_closure_blocks_access(self):
        self.assertEqual(self.case.read("shop-b"), "Bob newer note")
        self.case.close_shop_a()
        self.case.restore_old_app()
        self.assertEqual(self.case.raw_note("shop-a"), "Alice private note")
        with self.assertRaises(PermissionError):
            self.case.read("shop-a")
        with self.assertRaises(PermissionError):
            self.case.pending_job("shop-a")
        self.assertEqual(self.case.read("shop-b"), "Bob private note")
        self.assertEqual(self.case.pending_job("shop-b"), "PENDING")

    def test_reconciliation_removes_only_closed_tenant_active_rows(self):
        self.case.close_shop_a()
        self.case.restore_old_app()
        self.assertEqual(self.case.reconcile_closed_shop_a(),
                         {"restored_notes_removed": 1, "restored_jobs_cancelled": 1})
        self.assertIsNone(self.case.raw_note("shop-a"))
        self.assertEqual(self.case.read("shop-b"), "Bob private note")

    def test_missing_closure_authority_fails_closed(self):
        self.case.close_shop_a()
        self.case.restore_old_app()
        self.case.control.unlink()
        with self.assertRaises(PermissionError):
            self.case.read("shop-a")
        with self.assertRaises(PermissionError):
            self.case.read("shop-b")
        with self.assertRaises(PermissionError):
            self.case.reconcile_closed_shop_a()

    def test_restoring_old_authority_too_reopens_access_unsafely(self):
        self.case.close_shop_a()
        self.case.restore_old_app()
        self.case.restore_old_control_too()
        self.assertEqual(self.case.read("shop-a"), "Alice private note")
        self.assertEqual(self.case.pending_job("shop-a"), "PENDING")

    def test_demonstration_receipt(self):
        receipt = demonstrate()
        self.assertTrue(receipt["guarded_read_denied"])
        self.assertTrue(receipt["other_tenant_newer_value_lost"])


if __name__ == "__main__":
    unittest.main()
