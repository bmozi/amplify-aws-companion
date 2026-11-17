"""Changed-evidence controls for the offline observation lab."""

import json
import unittest
from pathlib import Path

from ledger_lab import review


CASES = json.loads(Path(__file__).with_name("cases.json").read_text())


class ReconciliationTests(unittest.TestCase):
    def test_complete_case_supports_only_save_fraction(self):
        result = review(CASES[0])
        self.assertEqual(result["save_confirmation_rate"], 0.8)
        self.assertIsNone(result["page_success_rate"])

    def test_missing_feed_blocks_full_window_rate(self):
        self.assertIsNone(review(CASES[1])["save_confirmation_rate"])
        result = review(CASES[2])
        self.assertEqual(result["missing_attempt_ids"], ["a16", "a17", "a18", "a19", "a20"])
        self.assertTrue(result["heartbeat_seen"])
        self.assertIsNone(result["save_confirmation_rate"])

    def test_open_window_and_conflicting_replay_do_not_certify(self):
        case = dict(CASES[0], window_closed=False)
        self.assertIsNone(review(case)["save_confirmation_rate"])
        case = dict(CASES[0], confirmation_window_closed=False)
        self.assertIsNone(review(case)["save_confirmation_rate"])
        case = dict(CASES[0], observed_attempt_ids=CASES[0]["observed_attempt_ids"] + ["a01"])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            review(case)

    def test_unmatched_confirmation_requires_investigation(self):
        case = dict(CASES[0], confirmed_after_refresh_ids=["a99"])
        with self.assertRaisesRegex(ValueError, "without a matching"):
            review(case)
        case = dict(CASES[0], independent_attempt_ids=CASES[0]["independent_attempt_ids"] + ["a01"])
        with self.assertRaisesRegex(ValueError, "duplicate independent"):
            review(case)


if __name__ == "__main__":
    unittest.main()
