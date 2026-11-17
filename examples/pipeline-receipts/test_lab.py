import unittest
from dataclasses import replace

from lab import ARTIFACT, SOURCE, Receipt, assess, clean_receipts


class PipelineReceiptTests(unittest.TestCase):
    def changed(self, stage, **updates):
        return [replace(r, **updates) if r.stage == stage else r for r in clean_receipts()]

    def test_complete_packet(self):
        self.assertEqual(assess(clean_receipts()), (True, []))

    def test_missing_or_duplicate_stage(self):
        for receipts in [clean_receipts()[:-1], clean_receipts() + clean_receipts()[:1]]:
            with self.subTest(count=len(receipts)):
                self.assertFalse(assess(receipts)[0])

    def test_exit_zero_does_not_hide_report_failure_or_skipped_test(self):
        for updates in [{"failed_tests": 1}, {"tests_run": 0}]:
            with self.subTest(updates=updates):
                self.assertFalse(assess(self.changed("test-acceptance", **updates))[0])

    def test_nonzero_exit_or_wrong_artifact_holds(self):
        for updates in [{"exit_code": 2}, {"artifact": "sha256:other"}]:
            with self.subTest(updates=updates):
                self.assertFalse(assess(self.changed("test-integration", **updates))[0])

    def test_stale_source_and_production_test_are_rejected(self):
        self.assertFalse(assess(self.changed("pr-unit", source="commit-old"))[0])
        self.assertFalse(assess(self.changed("test-security", environment="production"))[0])

    def test_performance_change_needs_bounded_load_receipt(self):
        self.assertFalse(assess(clean_receipts(), performance_change=True)[0])
        load = Receipt("test-load", SOURCE, ARTIFACT, 0, 1, 0, "isolated")
        receipts = clean_receipts() + [load]
        self.assertTrue(assess(receipts, performance_change=True, estimated_run_usd=4,
                               credit_reserve_usd=120, stop_condition=True)[0])
        for overrides in [{"estimated_run_usd": 6}, {"credit_reserve_usd": 99},
                          {"stop_condition": False}]:
            with self.subTest(overrides=overrides):
                self.assertFalse(assess(receipts, performance_change=True, **overrides)[0])


if __name__ == "__main__":
    unittest.main()
