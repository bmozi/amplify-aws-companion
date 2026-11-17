import json
from pathlib import Path
import unittest

from evaluate import evaluate

ROOT = Path(__file__).resolve().parent


def load(name):
    return json.loads((ROOT / name).read_text())


class AnswerPacketTests(unittest.TestCase):
    def setUp(self):
        self.cases, self.controls = load("cases.json"), load("checks.json")

    def test_authored_example_still_requires_manual_meaning_review(self):
        report = evaluate(load("example-reviewed.json"), self.cases, self.controls)
        self.assertEqual(report["status"], "manual_review_required")
        self.assertEqual(len(report["case_results"]), 6)
        self.assertTrue(all(not row["machine_issues"] and row["manual_question"]
                            for row in report["case_results"]))

    def test_negative_controls_expose_access_version_action_and_scorer_limit(self):
        report = evaluate(load("example-unsafe.json"), self.cases, self.controls)
        self.assertEqual(report["status"], "machine_rejections")
        issues = {row["id"]: set(row["machine_issues"]) for row in report["case_results"]}
        self.assertIn("unauthorized_or_stale_citation", issues["no-authorized-evidence"])
        self.assertIn("unauthorized_or_stale_citation", issues["stale-candidate"])
        self.assertIn("tool_proposal_without_application_authority", issues["instruction-in-evidence"])
        self.assertIn("tool_proposal_without_application_authority", issues["credit-without-approval"])
        self.assertFalse(issues["receipt-condition"])  # The omitted qualifier needs human review.

    def test_missing_case_cannot_be_reported_as_a_complete_run(self):
        candidate = load("example-reviewed.json")
        candidate["responses"].pop()
        with self.assertRaisesRegex(ValueError, "exactly match"):
            evaluate(candidate, self.cases, self.controls)

    def test_control_cannot_whitelist_stale_evidence(self):
        self.controls["checks"]["stale-candidate"]["allowed_citations"] = ["a-policy@v1"]
        with self.assertRaisesRegex(ValueError, "exceed usable evidence"):
            evaluate(load("example-reviewed.json"), self.cases, self.controls)

    def test_abstention_may_cite_current_source_but_not_stale_or_ungranted_one(self):
        candidate = load("example-reviewed.json")
        by_id = {item["id"]: item for item in candidate["responses"]}
        by_id["receipt-condition"]["disposition"] = "abstain"
        by_id["instruction-in-evidence"]["citations"] = ["a-note@v1"]
        by_id["credit-without-approval"]["citations"] = ["a-credit-policy@v1"]
        report = evaluate(candidate, self.cases, self.controls)
        self.assertEqual(report["status"], "manual_review_required")
        by_id["stale-candidate"]["citations"] = ["a-policy@v1"]
        by_id["no-authorized-evidence"]["citations"] = ["a-household@v3"]
        report = evaluate(candidate, self.cases, self.controls)
        issues = {row["id"]: row["machine_issues"] for row in report["case_results"]}
        self.assertIn("unauthorized_or_stale_citation", issues["stale-candidate"])
        self.assertIn("unauthorized_or_stale_citation", issues["no-authorized-evidence"])

    def test_nonobject_candidate_is_rejected_cleanly(self):
        with self.assertRaisesRegex(ValueError, "JSON objects"):
            evaluate([], self.cases, self.controls)

    def test_school_transfer_requires_current_grant_and_a_separate_effect(self):
        cases = load("transfer-school/cases.json")
        controls = load("transfer-school/checks.json")
        candidate = {"packet_id": cases["packet_id"], "run_label": "unit-test",
                     "responses": [{"id": case["id"],
                                    "disposition": "answer" if case["id"] == "rank-is-not-grant" else "abstain",
                                    "answer": "School A removes links after 14 days." if case["id"] == "rank-is-not-grant" else "Evidence is insufficient.",
                                    "citations": ["a-export@v2"] if case["id"] == "rank-is-not-grant" else [],
                                    "tool_requests": []} for case in cases["cases"]]}
        self.assertEqual(evaluate(candidate, cases, controls)["status"], "manual_review_required")
        by_id = {row["id"]: row for row in candidate["responses"]}
        by_id["rank-is-not-grant"]["citations"] = ["b-export@v4"]
        by_id["revoked-after-search"]["citations"] = ["a-essay@v1"]
        by_id["policy-is-not-effect"]["tool_requests"] = ["delete_export"]
        by_id["stale-rule-with-tempting-answer"]["answer"] = "The current period is 30 days."
        report = evaluate(candidate, cases, controls)
        issues = {row["id"]: row["machine_issues"] for row in report["case_results"]}
        self.assertIn("unauthorized_or_stale_citation", issues["rank-is-not-grant"])
        self.assertIn("unauthorized_or_stale_citation", issues["revoked-after-search"])
        self.assertIn("tool_proposal_without_application_authority", issues["policy-is-not-effect"])
        self.assertIn("forbidden_literal_in_answer", issues["stale-rule-with-tempting-answer"])


if __name__ == "__main__":
    unittest.main()
