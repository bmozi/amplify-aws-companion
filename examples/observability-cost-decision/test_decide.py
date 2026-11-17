"""Negative controls for the fictional observability cost decision."""

from __future__ import annotations

from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path
import tempfile
import unittest

from decide import evaluate, read_case


CASE = Path(__file__).with_name("case.json")


class DecisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.case = read_case(CASE)

    def test_cheaper_blind_plan_is_held_and_bounded_preserves_declared_path(self) -> None:
        result = evaluate(self.case)["plans"]
        self.assertEqual(result["baseline"]["modeled_cost_usd"], "7.890")
        self.assertEqual(result["cheap_but_blind"]["modeled_cost_usd"], "3.685")
        self.assertEqual(result["bounded"]["modeled_cost_usd"], "4.650")
        self.assertTrue(result["bounded"]["declared_incident_path_complete"])
        self.assertFalse(result["cheap_but_blind"]["declared_incident_path_complete"])
        self.assertFalse(result["bounded"]["live_path_verified"])

    def test_missing_heartbeat_holds_even_if_cost_falls(self) -> None:
        case = deepcopy(self.case)
        case["plans"]["bounded"]["captured_records"].remove("source_heartbeat")
        result = evaluate(case)["plans"]["bounded"]
        self.assertIn("source_heartbeat", result["missing_records"])
        self.assertFalse(result["declared_incident_path_complete"])

    def test_retention_equal_to_incident_age_is_not_safe_coverage(self) -> None:
        case = deepcopy(self.case)
        case["plans"]["bounded"]["critical_retention_days"] = case["incident_age_days"]
        result = evaluate(case)["plans"]["bounded"]
        self.assertIn("retention does not safely cover the incident review boundary", result["design_holds"])
        self.assertFalse(result["declared_incident_path_complete"])

    def test_metric_filter_cannot_move_to_infrequent_access(self) -> None:
        case = deepcopy(self.case)
        case["plans"]["bounded"]["metric_filter_source_class"] = "INFREQUENT_ACCESS"
        result = evaluate(case)["plans"]["bounded"]
        self.assertIn("metric-filter alert path requires a Standard source log group", result["design_holds"])

    def test_query_scan_growth_changes_cost_not_evidence(self) -> None:
        case = deepcopy(self.case)
        case["plans"]["bounded"]["query_scanned_gb"] = "30"
        result = evaluate(case)["plans"]["bounded"]
        self.assertEqual(result["modeled_cost_usd"], "4.770")
        self.assertTrue(result["declared_incident_path_complete"])

    def test_zero_modeled_source_storage_or_metric_usage_cannot_support_this_path(self) -> None:
        for meter, expected in (
            ("standard_ingest_gb", "modeled Standard ingestion is zero despite declared critical records"),
            ("stored_gb_month", "modeled stored GB-month is zero despite retained incident records"),
            ("custom_metric_months", "modeled custom metric usage is zero despite the declared metric-filter alert"),
        ):
            with self.subTest(meter=meter):
                case = deepcopy(self.case)
                case["plans"]["bounded"][meter] = "0"
                result = evaluate(case)["plans"]["bounded"]
                self.assertIn(expected, result["design_holds"])
                self.assertFalse(result["declared_incident_path_complete"])

    def test_invalid_quote_and_duplicate_json_rejected(self) -> None:
        case = deepcopy(self.case)
        case["plans"]["bounded"]["query_scanned_gb"] = "NaN"
        with self.assertRaises(ValueError):
            evaluate(case)
        raw = CASE.read_text()
        raw = raw.replace('"incident_age_days": 5,', '"incident_age_days": 5, "incident_age_days": 4,')
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "duplicate.json"
            path.write_text(raw)
            with self.assertRaisesRegex(ValueError, "duplicate JSON field"):
                read_case(path)


if __name__ == "__main__":
    unittest.main()
