import unittest
from lab import CASES, evaluate


class RequestBoundaryTests(unittest.TestCase):
    def test_count_does_not_stop_request(self):
        self.assertEqual(evaluate(CASES["suspicious_owner"]),
                         ("record_returned", ["matched_count", "default_allow", "application"]))

    def test_block_stops_before_application(self):
        outcome, trace = evaluate(CASES["suspicious_owner"], "block")
        self.assertEqual(outcome, "waf_block")
        self.assertNotIn("application", trace)

    def test_ordinary_cross_customer_request_needs_owner_check(self):
        self.assertEqual(evaluate(CASES["ordinary_other_owner"])[0], "owner_denied")
        self.assertEqual(evaluate(CASES["ordinary_other_owner"], enforce_owner=False)[0],
                         "record_returned")

    def test_early_allow_skips_later_block(self):
        outcome, trace = evaluate(CASES["trusted_suspicious"], "block", early_allow=True)
        self.assertEqual(outcome, "record_returned")
        self.assertNotIn("matched_block", trace)

    def test_early_allow_does_not_grant_record_ownership(self):
        request = CASES["ordinary_other_owner"]
        outcome, _ = evaluate(type(request)(request.caller, request.owner, trusted_path=True),
                              "block", early_allow=True)
        self.assertEqual(outcome, "owner_denied")

    def test_bad_action_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluate(CASES["ordinary_owner"], "allow_everyone")


if __name__ == "__main__":
    unittest.main()
