"""Exercise the stale-check failure and the shared local conditional boundary."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sqlite3
import tempfile
import unittest

from lab import initialize, observe, reserve_if_current, reserve_once


class QuotaRaceTests(unittest.TestCase):
    def test_both_stale_checks_pass_but_only_one_conditional_reservation_fits(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "capacity.sqlite"
            initialize(path, limit=20, used=12)
            with ThreadPoolExecutor(max_workers=2) as pool:
                observations = list(pool.map(lambda _: observe(path, 6), range(2)))
                self.assertTrue(all(item["fits_snapshot"] for item in observations))
                results = list(pool.map(lambda _: reserve_if_current(path, 6), range(2)))
            self.assertEqual(sorted(results), [False, True])
            self.assertEqual(observe(path, 6)["used"], 18)

    def test_rechecked_small_request_can_use_remaining_headroom(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "capacity.sqlite"
            initialize(path, limit=20, used=12)
            self.assertTrue(reserve_if_current(path, 6))
            self.assertFalse(reserve_if_current(path, 3))
            self.assertTrue(reserve_if_current(path, 2))
            self.assertEqual(observe(path, 1)["available"], 0)

    def test_rejects_invalid_amounts_without_changing_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "capacity.sqlite"
            initialize(path, limit=20, used=12)
            for amount in (0, -1):
                with self.assertRaises(ValueError):
                    reserve_if_current(path, amount)
            self.assertEqual(observe(path, 1)["used"], 12)

    def test_same_request_id_recovers_lost_reply_without_second_claim(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "capacity.sqlite"
            initialize(path, limit=20, used=12)
            self.assertEqual(reserve_once(path, "team-a", 6), "reserved")
            self.assertEqual(reserve_once(path, "team-a", 6), "reserved")
            self.assertEqual(observe(path, 1)["used"], 18)
            self.assertEqual(reserve_once(path, "team-a", 2), "conflict")
            self.assertEqual(observe(path, 1)["used"], 18)

    def test_two_connections_repeating_one_id_record_one_claim(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "capacity.sqlite"
            initialize(path, limit=20, used=12)
            with ThreadPoolExecutor(max_workers=2) as pool:
                outcomes = list(pool.map(lambda _: reserve_once(path, "team-a", 6), range(2)))
            self.assertEqual(outcomes, ["reserved", "reserved"])
            self.assertEqual(observe(path, 1)["used"], 18)

    def test_denied_intent_replays_denial_even_after_headroom_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "capacity.sqlite"
            initialize(path, limit=20, used=18)
            self.assertEqual(reserve_once(path, "team-b", 3), "full")
            with sqlite3.connect(path) as connection:
                connection.execute("UPDATE capacity SET unit_limit = 25 WHERE id = 1")
            self.assertEqual(reserve_once(path, "team-b", 3), "full")
            self.assertEqual(reserve_once(path, "team-b-new", 3), "reserved")
            self.assertEqual(observe(path, 1)["used"], 21)


if __name__ == "__main__":
    unittest.main()
