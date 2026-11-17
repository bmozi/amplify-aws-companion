"""Check the customer evidence and denial in the local timing exercise."""

import unittest

from failover_timeline import run_case


class FailoverTimelineTests(unittest.TestCase):
    def test_recovery_clock_ends_at_correct_customer_read(self):
        result = run_case()
        names = [event["event"] for event in result["events"]]
        self.assertEqual(result["status"], "LOCAL_RECOVERY_OBSERVED")
        self.assertEqual(result["pinned_old_path_status"], 404)
        self.assertGreaterEqual(result["failure_to_correct_read_ms"], 0)
        self.assertLess(names.index("first_failed_customer_read"), names.index("candidate_reconciled"))
        self.assertLess(names.index("candidate_reconciled"), names.index("route_switched"))
        self.assertLess(names.index("route_switched"), names.index("first_correct_customer_read"))
        self.assertIn("new_work_confirmed_on_candidate", names)
        self.assertEqual(next(e for e in result["events"] if e["event"] ==
                              "candidate_health_is_insufficient")["evidence"]["missing_confirmed_ids"], ["111"])

    def test_open_old_writer_holds_even_after_reconciliation(self):
        result = run_case(leave_old_writer_open=True)
        names = [event["event"] for event in result["events"]]
        self.assertEqual(result["status"], "HOLD")
        self.assertIsNone(result["failure_to_correct_read_ms"])
        self.assertIsNone(result["pinned_old_path_status"])
        self.assertIn("candidate_reconciled", names)
        self.assertIn("switch_held", names)
        self.assertNotIn("route_switched", names)
        self.assertNotIn("first_correct_customer_read", names)
        self.assertIn("Old writer", next(e for e in result["events"] if
                                         e["event"] == "switch_held")["evidence"]["reason"])


if __name__ == "__main__":
    unittest.main()
