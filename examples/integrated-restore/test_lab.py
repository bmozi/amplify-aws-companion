import unittest

from lab import Choice, assess


class RecoveryDecisionTests(unittest.TestCase):
    def test_matching_cross_resource_state_is_accepted(self):
        self.assertEqual(assess(Choice("10:10", "v1")), (True, []))

    def test_older_and_corrupt_points_are_rejected(self):
        for point, version in [("10:00", "v1"), ("10:11", "v2")]:
            with self.subTest(point=point):
                self.assertFalse(assess(Choice(point, version))[0])

    def test_wrong_version_and_delete_marker_are_rejected(self):
        for version in ["v2", "v3"]:
            with self.subTest(version=version):
                self.assertFalse(assess(Choice("10:10", version))[0])

    def test_duplicate_external_effect_is_rejected(self):
        accepted, reasons = assess(Choice("10:10", "v1", True))
        self.assertFalse(accepted)
        self.assertTrue(any("duplicate" in reason for reason in reasons))

    def test_missing_independent_confirmation_is_not_invented(self):
        self.assertFalse(assess(Choice("10:10", "v1"), None)[0])

    def test_missing_external_receipt_is_not_treated_as_unsent(self):
        accepted, reasons = assess(Choice("10:10", "v1"), sent_dispatches=set())
        self.assertFalse(accepted)
        self.assertTrue(any("unknown" in reason for reason in reasons))


if __name__ == "__main__":
    unittest.main()
