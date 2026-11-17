"""Changed-condition controls for proactive contact discovery."""

import unittest

from deadline_lab import accept, database, inspect_due, record_contact
from predeadline_lab import (compare_watchlist_passes, last_complete_pass,
                             read_contact_watchlist, run_watchlist_pass,
                             sweep_health)


class PredeadlineLabTest(unittest.TestCase):
    def setUp(self):
        self.db = database()
        self.connection = self.db.__enter__()

    def tearDown(self):
        self.db.__exit__(None, None, None)

    def test_due_soon_is_not_a_breach_and_late_work_stays_visible(self):
        accept(self.connection, "maya", 0)
        accept(self.connection, "on-time", 0)
        self.assertEqual(read_contact_watchlist(self.connection, 2699)["items"], [])
        self.assertEqual(len(read_contact_watchlist(self.connection, 2700)["items"]), 2)
        self.assertTrue(record_contact(self.connection, "on-time", 3600)["met_one_hour_promise"])
        self.assertEqual(read_contact_watchlist(self.connection, 3600)["items"][0]["state"], "due_soon")
        self.assertEqual(inspect_due(self.connection, 3600), [])
        self.assertEqual(read_contact_watchlist(self.connection, 3601)["items"][0]["state"], "overdue")
        self.assertEqual(inspect_due(self.connection, 3601)[0]["request_id"], "maya")
        self.assertEqual([x["request_id"] for x in read_contact_watchlist(self.connection, 3601)["items"]], ["maya"])

    def test_retry_does_not_move_watch_deadline_and_late_contact_stays_late(self):
        self.assertEqual(accept(self.connection, "maya", 0), 0)
        self.assertEqual(accept(self.connection, "maya", 200), 0)
        item = read_contact_watchlist(self.connection, 2700)["items"][0]
        self.assertEqual(item["deadline_at"], 3600)
        self.assertFalse(record_contact(self.connection, "maya", 4000)["met_one_hour_promise"])

    def test_page_every_due_item_before_claiming_a_complete_sweep(self):
        for n in range(25):
            accept(self.connection, f"r{n:02d}", 0)
        first = read_contact_watchlist(self.connection, 2700, limit=20)
        self.assertEqual(len(first["items"]), 20)
        self.assertIsNotNone(first["next_cursor"])
        second = read_contact_watchlist(self.connection, 2700, limit=20, after=first["next_cursor"])
        self.assertEqual(len(second["items"]), 5)
        self.assertIsNone(second["next_cursor"])
        self.assertEqual(len({x["request_id"] for x in first["items"] + second["items"]}), 25)

    def test_missing_or_stale_sweep_is_not_a_green_contact_signal(self):
        self.assertEqual(sweep_health(3601, None)["state"], "unknown")
        self.assertEqual(sweep_health(3000, 2700)["state"], "recent")
        self.assertEqual(sweep_health(3001, 2700)["state"], "stale")
        with self.assertRaises(ValueError):
            sweep_health(2700, 2701)
        with self.assertRaises(ValueError):
            read_contact_watchlist(self.connection, 2700, lead_seconds=True)

    def test_interrupted_page_walk_cannot_refresh_the_old_receipt(self):
        for n in range(25):
            accept(self.connection, f"r{n:02d}", 0)
        first = run_watchlist_pass(self.connection, 2700, 2702, limit=20)
        self.assertEqual((first["receipt"]["page_count"],
                          first["receipt"]["item_count"]), (2, 25))

        def interrupted(page_count, _page):
            if page_count == 1:
                raise RuntimeError("fixture interruption")

        with self.assertRaisesRegex(RuntimeError, "fixture interruption"):
            run_watchlist_pass(self.connection, 3000, 3002, limit=20,
                               after_page=interrupted)
        self.assertEqual(last_complete_pass(self.connection)["completed_at"], 2702)
        self.assertEqual(sweep_health(3003, last_complete_pass(self.connection)["completed_at"])["state"], "stale")
        self.assertEqual(run_watchlist_pass(self.connection, 3001, 3003, limit=20)["receipt"]["completed_at"], 3003)

    def test_terminal_cursor_is_not_a_concurrent_snapshot(self):
        for n in range(25):
            accept(self.connection, f"r{n:02d}", 100)

        def insert_behind_cursor(page_count, _page):
            if page_count == 1:
                accept(self.connection, "arrived-during-pass", 0)

        result = run_watchlist_pass(self.connection, 2800, 2802, limit=20,
                                    after_page=insert_behind_cursor)
        self.assertEqual(result["receipt"]["item_count"], 25)
        self.assertNotIn("arrived-during-pass", [item["request_id"] for item in result["items"]])
        self.assertEqual(len(run_watchlist_pass(self.connection, 2800, 2803, limit=20)["items"]), 26)

    def test_repeat_pass_discovers_the_behind_cursor_request(self):
        for n in range(25):
            accept(self.connection, f"r{n:02d}", 100)

        def insert_behind_cursor(page_count, _page):
            if page_count == 1:
                accept(self.connection, "arrived-during-pass", 0)

        comparison = compare_watchlist_passes(
            self.connection, 2800, 2802, 2803, limit=20,
            after_first_page=insert_behind_cursor)
        self.assertEqual(comparison["first_receipt"]["item_count"], 25)
        self.assertEqual(comparison["repeat_receipt"]["item_count"], 26)
        self.assertEqual(comparison["repeat_only"], ["arrived-during-pass"])
        self.assertEqual(comparison["first_only"], [])
        self.assertFalse(comparison["same_observed_ids"])
        self.assertFalse(comparison["customer_contact_observed"])
        self.assertFalse(comparison["concurrent_snapshot_proven"])

    def test_matching_passes_do_not_become_a_contact_or_snapshot_receipt(self):
        accept(self.connection, "maya", 0)
        comparison = compare_watchlist_passes(self.connection, 2700, 2701, 2702)
        self.assertTrue(comparison["same_observed_ids"])
        self.assertEqual(comparison["repeat_only"], [])
        self.assertFalse(comparison["customer_contact_observed"])
        self.assertFalse(comparison["concurrent_snapshot_proven"])
        with self.assertRaises(ValueError):
            compare_watchlist_passes(self.connection, 2700, 2702, 2701)


if __name__ == "__main__":
    unittest.main()
