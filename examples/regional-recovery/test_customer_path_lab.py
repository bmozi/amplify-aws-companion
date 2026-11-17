"""Changed-case checks for the local customer recovery path."""

from pathlib import Path
import sqlite3
import tempfile
import unittest

from customer_path_lab import Recovery, put, rows, run


class CustomerRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.recovery = Recovery(Path(self.temp.name))

    def test_health_does_not_prove_confirmed_booking(self):
        self.assertTrue(self.recovery.health("candidate"))
        self.assertEqual(self.recovery.booking("111")[0], 503)
        self.assertEqual(self.recovery.reconcile()["missing"], ["111"])

    def test_switch_needs_key_fence_and_exact_data(self):
        for expected in ("key", "fenced", "match"):
            with self.assertRaisesRegex(ValueError, expected):
                self.recovery.switch()
            if expected == "key":
                self.recovery.key_available = True
            elif expected == "fenced":
                self.recovery.source_writable = False
        self.assertEqual(self.recovery.route, "source")
        self.assertEqual(self.recovery.replay_missing()["missing"], [])
        self.recovery.switch()
        self.assertEqual(self.recovery.route, "candidate")

    def test_changed_and_unexpected_rows_block_replay(self):
        with sqlite3.connect(self.recovery.candidate) as db:
            db.execute("UPDATE bookings SET amount_cents=1 WHERE id='110'")
            db.execute("INSERT INTO bookings VALUES ('999', 1)")
        with self.assertRaisesRegex(ValueError, "differs"):
            self.recovery.replay_missing()
        self.assertEqual(rows(self.recovery.candidate)["110"], 1)
        self.assertEqual(self.recovery.reconcile()["unexpected"], ["999"])

    def test_candidate_cannot_accept_before_switch_or_duplicate(self):
        self.assertEqual(self.recovery.accept("112", 900)[0], 503)
        self.recovery.key_available = True
        self.recovery.source_writable = False
        self.recovery.replay_missing()
        self.recovery.switch()
        self.assertEqual(self.recovery.accept("112", 900)[0], 201)
        self.assertEqual(self.recovery.accept("112", 900)[0], 409)
        self.assertEqual(self.recovery.accept("113", True)[0], 400)

    def test_old_source_is_not_safe_to_return_to(self):
        self.recovery.key_available = True
        self.recovery.source_writable = False
        self.recovery.replay_missing()
        self.recovery.switch()
        self.recovery.accept("112", 900)
        with self.assertRaisesRegex(ValueError, "lacks confirmed"):
            self.recovery.return_to_source()
        self.assertNotIn("112", rows(self.recovery.source))

    def test_cooperative_flag_does_not_fence_direct_sql(self):
        self.recovery.source_writable = False
        put(self.recovery.source, "999", 1)
        self.assertIn("999", rows(self.recovery.source))

    def test_pinned_client_can_read_old_data_after_route_moves(self):
        self.recovery.key_available = True
        self.recovery.source_writable = False
        self.recovery.replay_missing()
        self.recovery.switch()
        self.assertEqual(self.recovery.accept("112", 900)[0], 201)
        self.recovery.source_online = True
        self.assertEqual(self.recovery.booking("112")[0], 200)
        self.assertEqual(self.recovery.booking_at("source", "112")[0], 404)
        self.assertEqual(self.recovery.booking_at("source", "111")[0], 200)
        self.assertEqual(self.recovery.route, "candidate")

    def test_bridge_requires_safe_local_state_and_existing_candidate_booking(self):
        self.assertEqual(self.recovery.bridge_target("111")[0], 503)
        self.recovery.key_available = True
        self.recovery.source_writable = False
        self.recovery.replay_missing()
        self.recovery.switch()
        self.assertEqual(self.recovery.bridge_target("111")[0], 503)
        self.recovery.source_online = True
        self.assertEqual(self.recovery.bridge_target("111"),
                         (307, {"location": "/bookings/111"}))
        self.assertEqual(self.recovery.bridge_target("112")[0], 404)
        self.assertEqual(self.recovery.bridge_target("111?next=//evil")[0], 400)
        self.recovery.candidate_online = False
        self.assertEqual(self.recovery.bridge_target("111")[0], 503)
        self.recovery.candidate_online = True
        self.recovery.source_writable = True
        self.assertEqual(self.recovery.bridge_target("111")[0], 503)

    def test_loopback_customer_journey(self):
        result = run()
        self.assertEqual(result["before"]["candidate_health"][0], 200)
        self.assertEqual(result["before"]["customer_read"][0], 503)
        self.assertEqual(result["after"]["customer_read"],
                         (200, {"id": "111", "amount_cents": 2300}))
        self.assertEqual(result["after"]["new_booking"][0], 201)
        self.assertEqual(result["after"]["new_booking_read"][0], 200)
        self.assertEqual(result["pinned_client_after_old_endpoint_returns"]["new_booking"][0], 404)
        self.assertEqual(result["pinned_client_after_old_endpoint_returns"]["current_route_new_booking"][0], 200)
        self.assertEqual(result["read_only_bridge"]["nonfollowing_client"],
                         (307, "/bookings/112", {"location": "/bookings/112"}))
        self.assertEqual(result["read_only_bridge"]["following_client"],
                         (200, {"id": "112", "amount_cents": 900}))
        self.assertEqual(result["read_only_bridge"]["write_attempt"][0], 404)
        self.assertEqual(result["read_only_bridge"]["candidate_unavailable"][0], 503)
        self.assertIn("lacks confirmed", result["failback"])


if __name__ == "__main__":
    unittest.main()
