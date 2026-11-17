import unittest

from lab import diagnose, sample_event


class EvidencePathTests(unittest.TestCase):
    def setUp(self):
        self.base = {
            "event": sample_event(),
            "triggered_rules": 1,
            "invocation_attempts": 1,
            "successful_invocation_attempts": 1,
            "failed_invocations": 0,
            "invocations_sent_to_dlq": 0,
            "invocations_failed_to_be_sent_to_dlq": 0,
            "automation_state": "Success",
            "current_alarm_state": "OK",
            "customer_completion": True,
            "evidence_links": {
                "target_event_id": sample_event()["id"],
                "automation_event_id": sample_event()["id"],
                "started_execution_id": "fictional-execution-01",
                "observed_execution_id": "fictional-execution-01",
                "expected_customer_scope": "fictional-booking-cohort-01",
                "observed_customer_scope": "fictional-booking-cohort-01",
            },
        }

    def test_each_boundary_requires_its_own_evidence(self):
        self.assertEqual(diagnose(self.base), "LOCAL_EVIDENCE_ALIGNED")
        for edit, expected in [
            ({"event": None}, "SOURCE_UNOBSERVED"),
            ({"triggered_rules": 0}, "RULE_NOT_OBSERVED"),
            ({"invocation_attempts": 0}, "TARGET_NOT_ATTEMPTED"),
            ({"successful_invocation_attempts": 0}, "TARGET_DELIVERY_UNPROVEN"),
            ({"successful_invocation_attempts": 0, "failed_invocations": 1, "invocations_sent_to_dlq": 1}, "TARGET_IN_DLQ"),
            ({"successful_invocation_attempts": 0, "failed_invocations": 1, "invocations_failed_to_be_sent_to_dlq": 1}, "DLQ_DELIVERY_FAILED"),
            ({"automation_state": None}, "AUTOMATION_UNOBSERVED"),
            ({"automation_state": "Failed"}, "AUTOMATION_NOT_SUCCESSFUL"),
            ({"current_alarm_state": "ALARM"}, "ALARM_NOT_RECOVERED"),
            ({"customer_completion": False}, "CUSTOMER_OUTCOME_UNPROVEN"),
            ({"evidence_links": None}, "CORRELATION_UNPROVEN"),
        ]:
            with self.subTest(edit=edit):
                self.assertEqual(diagnose({**self.base, **edit}), expected)

    def test_wrong_account_region_alarm_or_state_does_not_route(self):
        for edit in [
            {"account": "999988887777"},
            {"region": "us-east-1"},
            {"detail": {**sample_event()["detail"], "alarmName": "another-alarm"}},
            {"detail": {**sample_event()["detail"], "state": {"value": "OK"}}},
        ]:
            with self.subTest(edit=edit):
                self.assertEqual(
                    diagnose({**self.base, "event": {**sample_event(), **edit}}),
                    "RULE_NO_MATCH",
                )

    def test_missing_nested_detail_cannot_match(self):
        event = sample_event()
        event.pop("detail")
        self.assertEqual(diagnose({**self.base, "event": event}), "RULE_NO_MATCH")

    def test_green_aggregate_counts_cannot_join_unrelated_receipts(self):
        for key, wrong in [
            ("target_event_id", "other-event"),
            ("automation_event_id", "other-event"),
            ("observed_execution_id", "other-execution"),
            ("observed_customer_scope", "other-bookings"),
        ]:
            with self.subTest(key=key):
                links = {**self.base["evidence_links"], key: wrong}
                self.assertEqual(diagnose({**self.base, "evidence_links": links}), "CORRELATION_UNPROVEN")


if __name__ == "__main__":
    unittest.main()
