import unittest

from lab import evaluate


def case(kinds=(), *, consent=True, device=True, recipient="maya", app_open=False):
    return {
        "message_id": "m1",
        "recipient_id": recipient,
        "consent": consent,
        "device_registered": device,
        "app_open_recorded": app_open,
        "events": [
            {"message_id": "m1", "recipient_id": recipient, "kind": kind}
            for kind in kinds
        ],
    }


class EvidenceTests(unittest.TestCase):
    def test_missing_consent_blocks_even_with_registered_device(self):
        result = evaluate(case(consent=False))
        self.assertEqual(result["state"], "blocked")
        self.assertIn("consent", result["claim"])

    def test_aws_acceptance_does_not_prove_provider_delivery(self):
        result = evaluate(case(("requested", "aws_accepted")))
        self.assertEqual(result["state"], "aws_accepted")
        self.assertIn("unknown", result["claim"])

    def test_provider_acceptance_does_not_prove_reading(self):
        result = evaluate(case(("requested", "aws_accepted", "provider_accepted")))
        self.assertIn("unproved", result["claim"])

    def test_rejection_and_acceptance_cannot_both_finish_trail(self):
        with self.assertRaises(ValueError):
            evaluate(case(("requested", "aws_accepted", "provider_rejected", "provider_accepted")))

    def test_wrong_recipient_event_is_rejected(self):
        sample = case(("requested", "aws_accepted"))
        sample["events"][1]["recipient_id"] = "someone-else"
        with self.assertRaises(ValueError):
            evaluate(sample)

    def test_no_claim_from_orphan_provider_event(self):
        with self.assertRaises(ValueError):
            evaluate(case(("provider_accepted",)))

    def test_app_open_is_not_notification_read(self):
        result = evaluate(case(("requested", "aws_accepted", "provider_accepted"), app_open=True))
        self.assertEqual(result["state"], "provider_accepted")
        self.assertTrue(result["app_open_recorded"])
        self.assertIn("unproved", result["claim"])

    def test_app_can_open_even_when_provider_rejects(self):
        result = evaluate(case(("requested", "aws_accepted", "provider_rejected"), app_open=True))
        self.assertEqual(result["state"], "provider_rejected")
        self.assertIn("no causal link", result["claim"])

    def test_app_open_does_not_override_missing_consent(self):
        result = evaluate(case(consent=False, app_open=True))
        self.assertEqual(result["state"], "blocked")
        self.assertTrue(result["app_open_recorded"])

    def test_app_open_cannot_be_inserted_into_send_trail(self):
        with self.assertRaises(ValueError):
            evaluate(case(("requested", "app_open_recorded")))

    def test_missing_device_with_send_trail_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate(case(("requested",), device=False))


if __name__ == "__main__":
    unittest.main()
