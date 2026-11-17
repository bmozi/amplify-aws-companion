"""Boundary and failure controls for the local human-contact worklist."""

import unittest

from deadline_lab import accept, database, inspect_due, read_open_worklist, record_contact


class DeadlineLabTest(unittest.TestCase):
    def test_retry_does_not_reset_clock_and_tick_is_repeat_safe(self):
        with database() as connection:
            self.assertEqual(accept(connection, "r1", 0), 0)
            self.assertEqual(accept(connection, "r1", 3500), 0)
            self.assertEqual(inspect_due(connection, 3600), [])
            self.assertEqual(inspect_due(connection, 3601)[0]["deadline_at"], 3600)
            self.assertEqual(inspect_due(connection, 7200), [])
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM escalations").fetchone()[0], 1)

    def test_contact_at_deadline_meets_promise_and_prevents_escalation(self):
        with database() as connection:
            accept(connection, "r1", 20)
            result = record_contact(connection, "r1", 3620)
            self.assertTrue(result["met_one_hour_promise"])
            self.assertEqual(inspect_due(connection, 9999), [])

    def test_late_contact_preserves_breach_and_first_record(self):
        with database() as connection:
            accept(connection, "r1", 0)
            self.assertFalse(record_contact(connection, "r1", 4000)["met_one_hour_promise"])
            self.assertEqual(inspect_due(connection, 4001)[0]["request_id"], "r1")
            self.assertEqual(record_contact(connection, "r1", 5000)["first_contact_at"], 4000)
            self.assertEqual(inspect_due(connection, 5001), [])

    def test_bounded_order_requires_followup_tick(self):
        with database() as connection:
            for request_id, accepted_at in [("later", 10), ("first", 0), ("second", 0)]:
                accept(connection, request_id, accepted_at)
            self.assertEqual([x["request_id"] for x in inspect_due(connection, 4000, 2)],
                             ["first", "second"])
            self.assertEqual([x["request_id"] for x in inspect_due(connection, 4000, 2)],
                             ["later"])

    def test_lost_check_reply_does_not_hide_open_work(self):
        with database() as connection:
            accept(connection, "r1", 0)
            inspect_due(connection, 3601)  # The caller loses this reply.
            self.assertEqual(inspect_due(connection, 3602), [])
            first = read_open_worklist(connection)
            second = read_open_worklist(connection)
            self.assertEqual(first, second)
            self.assertEqual(first["items"][0]["request_id"], "r1")
            self.assertEqual(first["items"][0]["opened_at"], 3601)
            self.assertIsNone(first["next_cursor"])
            self.assertFalse(record_contact(connection, "r1", 4000)["met_one_hour_promise"])
            self.assertEqual(read_open_worklist(connection)["items"], [])
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM escalations").fetchone()[0], 1)

    def test_open_worklist_keyset_traverses_more_than_one_page(self):
        with database() as connection:
            for i in range(25):
                accept(connection, f"r{i:02}", 0)
            self.assertEqual(len(inspect_due(connection, 3601)), 20)
            self.assertEqual(len(inspect_due(connection, 3602)), 5)
            first = read_open_worklist(connection, limit=20)
            second = read_open_worklist(connection, limit=20, after=first["next_cursor"])
            ids = [row["request_id"] for row in first["items"] + second["items"]]
            self.assertEqual(ids, [f"r{i:02}" for i in range(25)])
            self.assertIsNone(second["next_cursor"])
            self.assertEqual(len(set(ids)), 25)

    def test_invalid_clock_and_unknown_contact_fail(self):
        with database() as connection:
            with self.assertRaises(ValueError):
                accept(connection, "r1", True)
            accept(connection, "r1", 10)
            for value in (True, -1, 1.5):
                with self.assertRaises(ValueError):
                    inspect_due(connection, value)
            with self.assertRaises(ValueError):
                record_contact(connection, "r1", 9)
            with self.assertRaises(ValueError):
                record_contact(connection, "missing", 20)
            for limit in (0, 101, True):
                with self.assertRaises(ValueError):
                    read_open_worklist(connection, limit=limit)
            for cursor in ((-1, "r1"), (1, ""), [1, "r1"], (True, "r1")):
                with self.assertRaises(ValueError):
                    read_open_worklist(connection, after=cursor)


if __name__ == "__main__":
    unittest.main()
