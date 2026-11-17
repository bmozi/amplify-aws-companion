import copy
import json
import unittest
from pathlib import Path

from observe import inspect


CASES = json.loads(Path(__file__).with_name("windows.json").read_text())


class EvidenceBoundaryTests(unittest.TestCase):
    def test_green_probe_does_not_hide_hurt_browsers_or_unfinished_work(self):
        result = inspect(CASES[0])
        self.assertIn("client errors observed", " ".join(result["flags"]))
        self.assertIn("5 accepted requests unfinished", result["accepted_work"])
        self.assertIn("5/5", result["canary"])

    def test_no_rum_with_visits_is_unknown_not_zero_error_rate(self):
        result = inspect(CASES[1])
        self.assertIn("error rate unknown", result["rum"])
        self.assertIn("no RUM sessions received", " ".join(result["flags"]))

    def test_missing_probe_and_incomplete_inventory_stay_unknown(self):
        result = inspect(CASES[2])
        self.assertIn("2 expected run results missing", result["canary"])
        self.assertIn("backlog unknown", result["accepted_work"])

    def test_impossible_counts_fail_before_interpretation(self):
        case = copy.deepcopy(CASES[0])
        case["rum_error_sessions"] = 41
        with self.assertRaises(ValueError):
            inspect(case)

    def test_zero_scheduled_canaries_is_not_a_green_probe(self):
        case = copy.deepcopy(CASES[0])
        case.update(canary_expected=0, canary_reported=0, canary_success=0)
        result = inspect(case)
        self.assertIn("no canary runs scheduled; no scripted journey evidence", result["flags"])
        self.assertIn("client errors observed", " ".join(result["flags"]))


if __name__ == "__main__":
    unittest.main()
