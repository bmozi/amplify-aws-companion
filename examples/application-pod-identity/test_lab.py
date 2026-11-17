import unittest
from dataclasses import replace

from lab import Path, fixture, review


class IdentityPathTests(unittest.TestCase):
    def test_pod_binding_and_unexpected_credential_source_are_separate(self):
        self.assertEqual(review(fixture()), ())
        changed = replace(fixture(), namespace="preview", credential_source="static-key")
        self.assertIn("Pod Identity association does not match pod binding", review(changed))
        self.assertIn("actual credential source is not the declared Pod Identity path", review(changed))

    def test_cross_account_target_is_a_distinct_review(self):
        path = replace(fixture(), target_account_differs=True)
        self.assertIn("cross-account target grant not reviewed", review(path))
        self.assertNotIn("cross-account target grant not reviewed",
                         review(replace(path, target_grant_reviewed=True)))

    def test_customer_and_client_aws_paths_do_not_collapse(self):
        api = Path(kind="api", customer_token_checked=True,
                   business_owner_checked=False, client_aws_credentials=True)
        self.assertIn("repair ownership check missing", review(api))
        self.assertIn("API-mediated path unexpectedly gives browser AWS credentials", review(api))
        direct = replace(api, kind="direct-client", business_owner_checked=True)
        self.assertIn("direct client AWS scope not reviewed", review(direct))


if __name__ == "__main__":
    unittest.main()
