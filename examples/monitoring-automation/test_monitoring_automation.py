import unittest

from lab import (alarm_action, matches_eventbridge, process_s3_object,
                 remediation_gate, run_packet)


class MonitoringAutomationTests(unittest.TestCase):
    def test_packet_has_expected_decisions(self):
        self.assertEqual(run_packet(), {
            "s3": ["PROCESS", "DUPLICATE", "FILTERED_OUTPUT"],
            "eventbridge": ["ROUTE", "NO_MATCH"],
            "cloudwatch_alarm": ["NOTIFY", "NO_TRANSITION"],
            "config": ["REMEDIATE", "STOP_STALE", "STOP_SCOPE", "STOP_ACTION", "STOP_RETRIES"],
        })

    def test_distinct_versions_are_distinct_work_items(self):
        seen = set()
        first = {"bucket": "b", "key": "incoming/a.jsonl", "version_id": "v1"}
        second = {"bucket": "b", "key": "incoming/a.jsonl", "version_id": "v2"}
        self.assertEqual(process_s3_object(first, seen, bucket="b", prefix="incoming/",
                                          suffix=".jsonl", output_prefix="processed/"), "PROCESS")
        self.assertEqual(process_s3_object(second, seen, bucket="b", prefix="incoming/",
                                          suffix=".jsonl", output_prefix="processed/"), "PROCESS")

    def test_missing_version_stops_instead_of_guessing_identity(self):
        record = {"bucket": "b", "key": "incoming/a.jsonl"}
        self.assertEqual(process_s3_object(record, set(), bucket="b", prefix="incoming/",
                                          suffix=".jsonl", output_prefix="processed/"),
                         "STOP_MISSING_VERSION")

    def test_event_pattern_requires_all_selected_fields(self):
        pattern = {"source": "aws.ec2", "detail-type": "State", "detail": {"state": "stopped"}}
        self.assertTrue(matches_eventbridge({"source": "aws.ec2", "detail-type": "State",
                                             "detail": {"state": "stopped", "reason": "user"}}, pattern))
        self.assertFalse(matches_eventbridge({"source": "aws.ec2", "detail-type": "State",
                                              "detail": {"state": "running"}}, pattern))

    def test_alarm_notifies_only_on_configured_transition(self):
        self.assertEqual(alarm_action("OK", "ALARM", configured_states={"ALARM"}), "NOTIFY")
        self.assertEqual(alarm_action("ALARM", "ALARM", configured_states={"ALARM"}),
                         "NO_TRANSITION")
        self.assertEqual(alarm_action("ALARM", "OK", configured_states={"ALARM"}), "NO_ACTION")

    def test_config_gate_stops_stale_and_out_of_scope_results(self):
        args = {"compliance": "NON_COMPLIANT", "evaluation_age_minutes": 42,
                "max_age_minutes": 10, "action": "restore", "known_actions": {"restore"},
                "attempts_already": 0, "max_attempts": 2,
                "allowed_resources": {"lab-1"}}
        self.assertEqual(remediation_gate(resource_id="lab-1", **args), "STOP_STALE")
        args["evaluation_age_minutes"] = 1
        self.assertEqual(remediation_gate(resource_id="prod-1", **args), "STOP_SCOPE")


if __name__ == "__main__":
    unittest.main()
