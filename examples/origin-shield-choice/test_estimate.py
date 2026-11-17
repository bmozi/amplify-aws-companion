import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from estimate import estimate


class EstimateTests(unittest.TestCase):
    def case(self):
        return dict(id="study", cacheable=True, viewer_requests=100_000,
                    regional_cache_misses=13_000,
                    estimated_origin_requests_with_shield=3_000,
                    estimated_billable_shield_requests=9_000,
                    origin_work_usd_per_1000_requests="1.20",
                    shield_usd_per_10000_requests="0.05")

    def test_declared_public_trace(self):
        result = estimate(self.case())
        self.assertEqual(result["origin_requests_avoided_assumed"], 10_000)
        self.assertEqual(result["origin_work_without_usd"], "15.60")
        self.assertEqual(result["modeled_total_with_usd"], "3.645")
        self.assertEqual(result["modeled_difference_with_minus_without_usd"], "-11.955")
        self.assertEqual(result["break_even_origin_work_usd_per_1000_requests"], "0.0045")
        self.assertEqual(result["break_even_interpretation"], "threshold")

    def test_cli_evaluates_a_reader_supplied_copy(self):
        case = self.case()
        case["estimated_origin_requests_with_shield"] = 13_000
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "changed.json"
            path.write_text(json.dumps({"cases": [case]}), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("estimate.py")), str(path)],
                check=True, capture_output=True, text=True,
            )
        self.assertEqual(json.loads(result.stdout)["origin_requests_avoided_assumed"], 0)

    def test_cli_rejects_duplicate_case_fields(self):
        raw = json.dumps({"cases": [self.case()]})
        raw = raw.replace('"regional_cache_misses": 13000',
                          '"regional_cache_misses": 13000, "regional_cache_misses": 1')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text(raw, encoding="utf-8")
            result = subprocess.run([sys.executable, str(Path(__file__).with_name("estimate.py")), str(path)],
                                    capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Duplicate JSON field: regional_cache_misses", result.stderr)

    def test_no_origin_reduction_can_only_add_shield_charge(self):
        case = self.case()
        case["estimated_origin_requests_with_shield"] = 13_000
        result = estimate(case)
        self.assertEqual(result["origin_requests_avoided_assumed"], 0)
        self.assertEqual(result["modeled_difference_with_minus_without_usd"], "0.045")
        self.assertIsNone(result["break_even_origin_work_usd_per_1000_requests"])
        self.assertIn("no rate breaks even", result["break_even_interpretation"])

    def test_no_avoided_requests_and_no_incremental_charge_tie_at_any_rate(self):
        case = self.case()
        case["estimated_origin_requests_with_shield"] = 13_000
        case["estimated_billable_shield_requests"] = 0
        for rate in ("0", "1.20", "100"):
            with self.subTest(origin_rate=rate):
                case["origin_work_usd_per_1000_requests"] = rate
                result = estimate(case)
                self.assertEqual(result["modeled_difference_with_minus_without_usd"], "0.00")
                self.assertIsNone(result["break_even_origin_work_usd_per_1000_requests"])
                self.assertIn("all rates tie", result["break_even_interpretation"])

    def test_reject_count_overflow(self):
        case = self.case()
        case["estimated_origin_requests_with_shield"] = 13_001
        with self.assertRaisesRegex(ValueError, "upstream"):
            estimate(case)

    def test_reject_nonfinite_rate(self):
        case = self.case()
        case["shield_usd_per_10000_requests"] = "NaN"
        with self.assertRaisesRegex(ValueError, "finite"):
            estimate(case)

    def test_reject_boolean_request_count(self):
        case = self.case()
        case["regional_cache_misses"] = True
        with self.assertRaisesRegex(ValueError, "integer"):
            estimate(case)


if __name__ == "__main__":
    unittest.main()
