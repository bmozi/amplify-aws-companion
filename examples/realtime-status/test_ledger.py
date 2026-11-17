import unittest

from ledger import StatusService


class StatusTests(unittest.TestCase):
    def setUp(self):
        self.service = StatusService()
        self.service.grant("alice", "repair-17")

    def test_only_current_owner_receives_status(self):
        self.service.subscribe("c1", "alice", "repair-17")
        with self.assertRaises(PermissionError):
            self.service.subscribe("c2", "bob", "repair-17")
        deliveries, fresh = self.service.publish("trusted_worker", "e1", "repair-17", "checking")
        self.assertTrue(fresh)
        self.assertEqual([connection for connection, _ in deliveries], ["c1"])

    def test_revoke_closes_fixture_subscription_and_blocks_reconnect(self):
        self.service.subscribe("c1", "alice", "repair-17")
        self.service.revoke("alice", "repair-17")
        deliveries, _ = self.service.publish("trusted_worker", "e1", "repair-17", "ready")
        self.assertEqual(deliveries, [])
        with self.assertRaises(PermissionError):
            self.service.subscribe("c2", "alice", "repair-17")

    def test_reconnect_replays_authoritative_gap(self):
        self.service.subscribe("c1", "alice", "repair-17")
        self.service.publish("trusted_worker", "e1", "repair-17", "checking")
        self.service.disconnect("c1")
        self.service.publish("trusted_worker", "e2", "repair-17", "ready")
        missed = self.service.subscribe("c2", "alice", "repair-17", 1)
        self.assertEqual([(event.sequence, event.status) for event in missed], [(2, "ready")])

    def test_duplicate_effect_is_not_appended_twice(self):
        self.service.subscribe("c1", "alice", "repair-17")
        self.service.publish("trusted_worker", "e1", "repair-17", "checking")
        deliveries, fresh = self.service.publish("trusted_worker", "e1", "repair-17", "checking")
        self.assertFalse(fresh)
        self.assertEqual(len(self.service.events["repair-17"]), 1)
        self.assertEqual([(connection, event.sequence) for connection, event in deliveries], [("c1", 1)])
        with self.assertRaises(ValueError):
            self.service.publish("trusted_worker", "e1", "repair-17", "ready")

    def test_untrusted_publisher_and_future_cursor_are_rejected(self):
        with self.assertRaises(PermissionError):
            self.service.publish("alice", "e1", "repair-17", "ready")
        with self.assertRaises(ValueError):
            self.service.subscribe("c1", "alice", "repair-17", 10)


if __name__ == "__main__":
    unittest.main()
