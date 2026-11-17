"""Changed-case checks for the fictional standby commitment worksheet."""

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from standby_cost import evaluate, read_case


CASE = Path(__file__).with_name("standby-cost.json")


class StandbyCostTests(unittest.TestCase):
    def test_two_individually_green_runs_cross_one_reserve(self):
        result = evaluate(read_case(CASE))
        self.assertEqual(result["standby_subtotal_usd"], "6.75")
        self.assertEqual(result["standby_whole_estimate_usd"], "8.4375")
        self.assertEqual(result["combined_commitment_usd"], "11.4375")
        self.assertEqual(result["assumed_credits_after_both_usd"], "88.5625")
        self.assertTrue(result["standby_within_per_run_limit"])
        self.assertTrue(result["other_within_per_run_limit"])
        self.assertFalse(result["combined_reserve_survives"])
        self.assertFalse(result["live_run_authorized"])

    def test_changed_replica_quote_breaks_first_limit_too(self):
        case = deepcopy(read_case(CASE))
        case["meters_usd"]["replica_backup_storage"] = "2.75"
        result = evaluate(case)
        self.assertEqual(result["standby_whole_estimate_usd"], "9.6875")
        self.assertFalse(result["standby_within_per_run_limit"])
        self.assertFalse(result["combined_reserve_survives"])

    def test_single_run_arithmetic_pass_is_still_not_live_authority(self):
        case = deepcopy(read_case(CASE))
        case["other_run_whole_estimate_usd"] = "0"
        result = evaluate(case)
        self.assertEqual(result["arithmetic_holds"], [])
        self.assertTrue(result["combined_reserve_survives"])
        self.assertFalse(result["live_run_authorized"])

    def test_missing_meter_or_negative_quote_cannot_look_green(self):
        case = deepcopy(read_case(CASE))
        del case["meters_usd"]["transfer"]
        with self.assertRaisesRegex(ValueError, "missing meter groups: transfer"):
            evaluate(case)
        case = deepcopy(read_case(CASE))
        case["meters_usd"]["transfer"] = "-0.01"
        with self.assertRaisesRegex(ValueError, "exact nonnegative decimal"):
            evaluate(case)

    def test_duplicate_json_meter_is_rejected_before_calculation(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "duplicate.json"
            path.write_text('{"meters_usd":{"compute":"1","compute":"0"}}')
            with self.assertRaisesRegex(ValueError, "duplicate JSON field: compute"):
                read_case(path)


if __name__ == "__main__":
    unittest.main()
