import unittest
from dataclasses import replace
from datetime import date

from packet import fixture, packet_gaps


class PacketTests(unittest.TestCase):
    def test_fictional_complete_metadata(self):
        self.assertEqual(packet_gaps(*fixture()), [])

    def test_wrong_service_region_and_period_do_not_pass(self):
        question, report, customer = fixture()
        report = replace(report, services=frozenset({"Amazon EC2"}),
                         regions=frozenset({"us-west-2"}), end=date(2025, 12, 31))
        gaps = packet_gaps(question, report, customer)
        self.assertEqual(len(gaps), 3)

    def test_provider_report_cannot_stand_in_for_customer_configuration(self):
        question, report, _ = fixture()
        self.assertIn("customer configuration evidence missing", packet_gaps(question, report, None))

    def test_report_title_without_scope_review_is_insufficient(self):
        question, report, customer = fixture()
        report = replace(report, scope_checked=False)
        self.assertIn("actual report scope not reviewed", packet_gaps(question, report, customer))

    def test_customer_record_must_match_resource_and_window(self):
        question, report, customer = fixture()
        customer = replace(customer, resource="another-bucket", observed=date(2025, 12, 1))
        gaps = packet_gaps(question, report, customer)
        self.assertIn("customer evidence addresses a different control or resource", gaps)
        self.assertIn("customer observation outside requested window", gaps)


if __name__ == "__main__":
    unittest.main()
