"""Negative controls for claims that an audit packet cannot support."""

import copy
import json
import unittest
from pathlib import Path

from lab import assess


BASE = json.loads(Path(__file__).with_name("fixture.json").read_text())


class EvidenceBoundaryTests(unittest.TestCase):
    def packet(self):
        return copy.deepcopy(BASE)

    def test_stream_completion_does_not_double_count_call(self):
        result = assess(self.packet())
        self.assertEqual(result["api_call_count"], 1)
        self.assertEqual(result["stream_completion_count"], 1)
        self.assertEqual(result["conclusion"], "four_routes_present_review_business_status")
        self.assertEqual(result["business_outcome"], "human_review_required")

    def test_disabled_logging_does_not_turn_absence_into_clean_content(self):
        packet = self.packet()
        packet["collection"]["invocation_logging"]["enabled"] = False
        result = assess(packet)
        self.assertEqual(result["model_content"], "not_expected_from_this_configuration")
        self.assertEqual(result["conclusion"], "incomplete_evidence_do_not_claim_success")

    def test_other_account_or_region_cannot_complete_packet(self):
        for field, value in (("account", "999900001111"), ("region", "us-west-2")):
            with self.subTest(field=field):
                packet = self.packet()
                packet["invocation_logs"][0][field] = value
                self.assertEqual(assess(packet)["model_content"], "unknown_missing_record")

    def test_mantle_endpoint_does_not_inherit_runtime_content_logging(self):
        packet = self.packet()
        packet["endpoint"] = "bedrock-mantle"
        result = assess(packet)
        self.assertEqual(result["model_content"], "not_expected_from_this_configuration")
        self.assertEqual(result["api_call_count"], 0)

    def test_missing_receipt_cannot_be_inferred_from_trace(self):
        packet = self.packet()
        packet["business_receipts"] = []
        result = assess(packet)
        self.assertEqual(result["business_outcome"], "unknown")
        self.assertEqual(result["conclusion"], "incomplete_evidence_do_not_claim_success")

    def test_masked_response_does_not_clear_input_logging_risk(self):
        result = assess(self.packet())
        self.assertTrue(result["sensitive_log_risk"])


if __name__ == "__main__":
    unittest.main()
