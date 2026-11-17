import copy
import json
from pathlib import Path
import unittest

from lab import analyze


FIXTURE = json.loads((Path(__file__).parent / "fixture.json").read_text())


class SecurityAuditEvidenceTests(unittest.TestCase):
    def test_exact_scope_and_time_join(self):
        result = analyze(FIXTURE)[0]
        self.assertEqual(result["matched_evidence_ids"], ["E-101", "E-102"])
        self.assertEqual(result["finding_event_time"], "2026-10-01T12:10:00Z")
        self.assertEqual(result["finding_observed_at"], "2026-10-01T12:12:00Z")
        self.assertFalse(result["causation_established"])

    def test_same_name_in_other_account_and_region_is_excluded(self):
        result = analyze(FIXTURE)[0]
        exclusion = next(item for item in result["excluded_records"] if item["id"] == "E-103")
        self.assertEqual(exclusion["reason"], "account_mismatch")

    def test_region_mismatch_is_independently_excluded(self):
        case = copy.deepcopy(FIXTURE)
        record = next(row for row in case["records"] if row["id"] == "E-103")
        record["account"] = "111111111111"
        result = analyze(case)[0]
        exclusion = next(item for item in result["excluded_records"] if item["id"] == "E-103")
        self.assertEqual(exclusion["reason"], "region_mismatch")

    def test_resource_mismatch_is_excluded(self):
        case = copy.deepcopy(FIXTURE)
        case["records"].append({"id": "E-105", "kind": "evidence", "source": "cloudtrail", "account": "111111111111", "region": "us-east-2", "resource": "arn:example:s3:::different-export", "time": "2026-10-01T12:08:00Z"})
        result = analyze(case)[0]
        exclusion = next(item for item in result["excluded_records"] if item["id"] == "E-105")
        self.assertEqual(exclusion["reason"], "resource_mismatch")

    def test_out_of_window_record_is_excluded(self):
        result = analyze(FIXTURE)[0]
        exclusion = next(item for item in result["excluded_records"] if item["id"] == "E-104")
        delayed = next(row for row in FIXTURE["records"] if row["id"] == "E-104")
        self.assertEqual(delayed["observed_at"], result["finding_observed_at"])
        self.assertEqual(exclusion["reason"], "outside_time_window")

    def test_partial_or_missing_coverage_stays_unknown(self):
        case = copy.deepcopy(FIXTURE)
        case["coverage"] = [row for row in case["coverage"] if row["source"] != "config"]
        result = analyze(case)[0]
        self.assertEqual(result["source_coverage"]["config"], "unknown")
        self.assertEqual(result["coverage_result"], "unknown_or_incomplete")

    def test_coverage_for_another_resource_does_not_apply(self):
        case = copy.deepcopy(FIXTURE)
        config = next(row for row in case["coverage"] if row["source"] == "config")
        config["resource"] = "arn:example:s3:::different-export"
        result = analyze(case)[0]
        self.assertEqual(result["source_coverage"]["config"], "unknown")

    def test_no_expected_sources_cannot_be_called_complete(self):
        case = copy.deepcopy(FIXTURE)
        case["records"][0]["expected_sources"] = []
        result = analyze(case)[0]
        self.assertEqual(result["coverage_result"], "unknown_or_incomplete")

    def test_alert_rule_accepts_the_intended_finding_without_automating_response(self):
        results = {row["finding_id"]: row for row in analyze(FIXTURE)}
        decision = results["F-101"]["alert_evaluation"]
        self.assertEqual(decision["decision"], "candidate_alert")
        self.assertEqual(decision["owner"], "fictional-security-on-call")
        self.assertFalse(decision["automated_response"])

    def test_alert_rule_rejects_category_and_severity_near_matches(self):
        results = {row["finding_id"]: row for row in analyze(FIXTURE)}
        category = results["F-102"]["alert_evaluation"]
        severity = results["F-103"]["alert_evaluation"]
        self.assertEqual(category["reasons"], ["category_mismatch"])
        self.assertEqual(severity["reasons"], ["below_minimum_severity"])

    def test_alert_rule_rejects_environment_and_region_near_matches(self):
        results = {row["finding_id"]: row for row in analyze(FIXTURE)}
        environment = results["F-104"]["alert_evaluation"]
        region = results["F-105"]["alert_evaluation"]
        self.assertEqual(environment["reasons"], ["environment_mismatch"])
        self.assertEqual(region["reasons"], ["region_mismatch"])

    def test_unexpected_source_is_not_joined(self):
        case = copy.deepcopy(FIXTURE)
        case["records"].append({"id": "E-105", "kind": "evidence", "source": "flowlogs", "account": "111111111111", "region": "us-east-2", "resource": "arn:example:s3:::booking-export", "time": "2026-10-01T12:10:00Z"})
        result = analyze(case)[0]
        self.assertNotIn("E-105", result["matched_evidence_ids"])
        self.assertEqual(next(item for item in result["excluded_records"] if item["id"] == "E-105")["reason"], "source_not_expected")


if __name__ == "__main__":
    unittest.main()
