import tempfile
import unittest
from pathlib import Path

from conflict_lab import WorkOrder


class WorkOrderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "authority.sqlite"
        self.server = WorkOrder(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_new_hazard_blocks_stale_close(self):
        first = self.server.apply("open", "report", "pump", 0, "leak")
        self.server.apply("hazard", "report", "pump", 1, "electrical hazard")
        result = self.server.apply("close", "close", "pump", first["revision"], "repaired")
        self.assertEqual(result["decision"], "STALE_REVIEW")
        self.assertEqual(self.server.read("pump")["status"], "open")
        self.assertEqual(self.server.read("pump")["last_report"], "electrical hazard")

    def test_lost_reply_replays_decision_after_restart(self):
        expected = self.server.apply("open", "report", "pump", 0, "leak")
        self.server = WorkOrder(self.path)
        self.assertEqual(self.server.apply("open", "report", "pump", 0, "leak"), expected)
        self.assertEqual(self.server.read("pump")["revision"], 1)

    def test_changed_intent_under_same_id_is_rejected(self):
        self.server.apply("open", "report", "pump", 0, "leak")
        with self.assertRaises(ValueError):
            self.server.apply("open", "report", "pump", 0, "other problem")

    def test_current_close_requires_open_state_and_revision(self):
        self.server.apply("open", "report", "pump", 0, "leak")
        self.assertEqual(self.server.apply("close", "close", "pump", 1, "repair checked")["status"], "closed")
        self.assertEqual(self.server.apply("close2", "close", "pump", 2, "again")["decision"], "NOT_OPEN")

    def test_two_connections_cannot_apply_same_revision_twice(self):
        other = WorkOrder(self.path)
        self.server.apply("open", "report", "pump", 0, "leak")
        self.assertEqual(other.apply("hazard", "report", "pump", 1, "hazard")["revision"], 2)
        self.assertEqual(self.server.apply("old-close", "close", "pump", 1, "repaired")["decision"], "STALE_REVIEW")


if __name__ == "__main__":
    unittest.main()
