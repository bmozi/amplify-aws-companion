"""Changed-condition checks for the SaaS entitlement teaching fixture."""

from pathlib import Path
import tempfile
import unittest

from lab import Portal


class EntitlementTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory(prefix="tenant-entitlement-test-")
        self.portal = Portal(Path(self.folder.name) / "portal.sqlite")
        self.portal.seed()

    def tearDown(self):
        self.portal.close()
        self.folder.cleanup()

    def test_stale_plan_and_token_claim_cannot_restore_premium(self):
        self.assertEqual(self.portal.use("alice", "shop-a", "premium_export", "a", 101),
                         "entitlement_expired")
        self.assertEqual(self.portal.apply_change("shop-a", 3, "standard", 180, "active"), "applied")
        self.assertEqual(self.portal.apply_change("shop-a", 2, "premium", 180, "active"), "stale_ignored")
        self.assertEqual(self.portal.use("alice", "shop-a", "premium_export", "b", 110),
                         "feature_denied")
        self.assertEqual(self.portal.usage_count("shop-a"), 0)

    def test_same_revision_conflict_does_not_change_plan(self):
        self.assertEqual(self.portal.apply_change("shop-a", 3, "standard", 180, "active"), "applied")
        self.assertEqual(self.portal.apply_change("shop-a", 3, "premium", 180, "active"),
                         "same_revision_conflict")
        self.assertEqual(self.portal.use("alice", "shop-a", "premium_export", "a", 110),
                         "feature_denied")

    def test_membership_plan_and_tenant_scope_are_separate(self):
        self.assertEqual(self.portal.use("bob", "shop-b", "premium_export", "same", 99),
                         "accepted_locally")
        self.assertEqual(self.portal.use("alice", "shop-b", "premium_export", "same", 99),
                         "tenant_denied")
        self.assertEqual(self.portal.use("alice", "shop-a", "premium_export", "same", 99),
                         "accepted_locally")
        self.assertEqual((self.portal.usage_count("shop-a"), self.portal.usage_count("shop-b")),
                         (1, 1))

    def test_retry_and_changed_intent_do_not_make_another_usage_row(self):
        self.assertEqual(self.portal.use("alice", "shop-a", "read_note", "op", 99),
                         "accepted_locally")
        self.assertEqual(self.portal.use("alice", "shop-a", "read_note", "op", 99),
                         "same_operation")
        self.assertEqual(self.portal.use("alice", "shop-a", "premium_export", "op", 99),
                         "operation_conflict")
        self.assertEqual(self.portal.apply_change("shop-a", 3, "standard", 180, "active"), "applied")
        self.assertEqual(self.portal.use("alice", "shop-a", "read_note", "op", 110),
                         "same_operation")
        self.assertEqual(self.portal.usage_count("shop-a"), 1)

    def test_closure_stops_new_work_without_erasing_prior_receipt(self):
        self.assertEqual(self.portal.use("alice", "shop-a", "read_note", "before", 99),
                         "accepted_locally")
        self.assertEqual(self.portal.apply_change("shop-a", 4, "standard", 180, "closed"), "applied")
        self.assertEqual(self.portal.use("alice", "shop-a", "read_note", "after", 110),
                         "tenant_closed")
        self.assertEqual(self.portal.apply_change("shop-a", 5, "premium", 200, "active"),
                         "closed_requires_new_onboarding_review")
        self.assertEqual(self.portal.usage_count("shop-a"), 1)


if __name__ == "__main__":
    unittest.main()
