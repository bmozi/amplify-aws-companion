import tempfile
import unittest
from pathlib import Path

from lab import Portal


class OffboardingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.portal = Portal(Path(self.temp.name) / "portal.sqlite")

    def tearDown(self):
        self.temp.cleanup()

    def test_warm_cache_and_pending_job_stop_but_other_tenant_continues(self):
        self.assertEqual(self.portal.read("alice", "same-id"), "Alice private note")
        self.assertEqual(self.portal.read("bob", "same-id"), "Bob private note")
        job = self.portal.enqueue("alice", "same-id")
        receipt = self.portal.offboard("operator-a", "shop-a")
        self.assertEqual(receipt["active_notes_removed"], 1)
        self.assertEqual(receipt["pending_jobs_cancelled"], 1)
        with self.assertRaises(PermissionError):
            self.portal.read("alice", "same-id")
        with self.assertRaises(PermissionError):
            self.portal.process(job)
        with self.assertRaises(PermissionError):
            self.portal.enqueue("alice", "same-id")
        self.assertEqual(self.portal.read("bob", "same-id"), "Bob private note")
        self.assertEqual(self.portal.process(self.portal.enqueue("bob", "same-id")), "Bob private note")

    def test_offboarding_retry_returns_same_receipt(self):
        self.portal.enqueue("alice", "same-id")
        first = self.portal.offboard("operator-a", "shop-a")
        self.assertEqual(self.portal.offboard("operator-a", "shop-a"), first)

    def test_wrong_operator_cannot_close_tenant(self):
        with self.assertRaises(PermissionError):
            self.portal.offboard("operator-b", "shop-a")
        self.assertEqual(self.portal.read("alice", "same-id"), "Alice private note")

    def test_completed_job_remains_a_review_item(self):
        job = self.portal.enqueue("alice", "same-id")
        self.portal.process(job)
        receipt = self.portal.offboard("operator-a", "shop-a")
        self.assertEqual(receipt["already_completed_jobs_to_review"], 1)
        self.assertIn("external effects", receipt["outside_this_fixture"])


if __name__ == "__main__":
    unittest.main()
