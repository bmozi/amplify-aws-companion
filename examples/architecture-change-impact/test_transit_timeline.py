import copy
import json
from pathlib import Path
import unittest

from transit_timeline import review

CASE = json.loads(Path(__file__).with_name("transit-timeline.json").read_text())


class TransitTimelineTests(unittest.TestCase):
    def test_late_all_clear_is_blocked_but_old_stop_is_observed_as_stale(self):
        outcomes = {row["id"]: row["outcome"] for row in review(CASE)}
        self.assertEqual(outcomes["late-all-clear"], "stale_send_blocked")
        self.assertEqual(outcomes["old-stop-display"], "stale_notice_observed_on_path")

    def test_consent_channel_acceptance_and_observed_notice_are_distinct(self):
        outcomes = {row["id"]: row["outcome"] for row in review(CASE)}
        self.assertEqual(outcomes["opted-out"], "consent_blocked")
        self.assertEqual(outcomes["text-accepted"], "channel_accepted_reach_unproved")
        self.assertEqual(outcomes["app-observed"], "current_notice_observed_on_path")

    def test_future_reclosure_does_not_suppress_an_earlier_attempt(self):
        first = review(CASE)[0]
        self.assertEqual(first["fact_version_at_event"], 1)
        self.assertEqual(first["outcome"], "channel_accepted_reach_unproved")

    def test_late_observation_cannot_be_called_on_time(self):
        changed = copy.deepcopy(CASE)
        changed["events"][4]["minute"] = 10
        observed = next(row for row in review(changed) if row["id"] == "app-observed")
        self.assertFalse(observed["within_five_minutes_of_current_fact"])

    def test_consent_is_evaluated_at_attempt_time(self):
        changed = copy.deepcopy(CASE)
        changed["events"][2]["minute"] = 4
        before_opt_out = next(row for row in review(changed) if row["id"] == "opted-out")
        self.assertEqual(before_opt_out["outcome"], "send_not_accepted")

    def test_duplicate_or_reordered_fact_version_is_rejected(self):
        changed = copy.deepcopy(CASE)
        changed["facts"][2]["version"] = 2
        with self.assertRaisesRegex(ValueError, "unique, increasing"):
            review(changed)


if __name__ == "__main__":
    unittest.main()
