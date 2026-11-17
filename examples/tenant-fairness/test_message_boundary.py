from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from message_boundary import MessageBoundary


class MessageBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "local.sqlite"
        self.boundary = MessageBoundary(self.path)

    def test_claimed_other_tenant_does_not_create_job(self):
        with self.assertRaises(PermissionError):
            self.boundary.submit("alice", "r1", "secret", "shop-b")
        with self.assertRaises(PermissionError):
            self.boundary.submit("unknown", "r1", "secret")
        self.assertEqual(self.boundary.pending_envelopes(), [])
        self.assertEqual(self.boundary.effects(), [])

    def test_colliding_ids_and_duplicate_delivery_remain_tenant_scoped(self):
        a = self.boundary.submit("alice", "same", "A report")
        b = self.boundary.submit("bob", "same", "B report")
        self.assertEqual(self.boundary.consume(b), "B report")
        self.assertEqual(self.boundary.consume(a), "A report")
        self.assertEqual(self.boundary.consume(a), "A report")
        self.assertEqual(self.boundary.effects(), [
            ("shop-a", "same", "A report"), ("shop-b", "same", "B report")])

    def test_tampered_group_and_unknown_job_do_not_create_effect(self):
        good = self.boundary.submit("alice", "r1", "A report")
        with self.assertRaises(PermissionError):
            self.boundary.consume({**good, "MessageGroupId": "shop-b"})
        with self.assertRaises(PermissionError):
            self.boundary.consume({**good, "request_id": "missing"})
        self.assertEqual(self.boundary.effects(), [])

    def test_same_id_changed_content_rejected_and_database_survives_reopen(self):
        good = self.boundary.submit("alice", "r1", "A report")
        self.assertEqual(self.boundary.submit("alice", "r1", "A report"), good)
        with self.assertRaises(ValueError):
            self.boundary.submit("alice", "r1", "different report")
        recovered = MessageBoundary(self.path)
        self.assertEqual(recovered.pending_envelopes(), [good])
        self.assertEqual(recovered.consume(good), "A report")
        self.assertEqual(recovered.pending_envelopes(), [])
        self.assertEqual(MessageBoundary(self.path).effects(), [("shop-a", "r1", "A report")])


if __name__ == "__main__":
    unittest.main()
