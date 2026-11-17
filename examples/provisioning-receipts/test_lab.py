import unittest

from lab import Destination, REVIEWED_IMAGE, assess, clean_destinations


class ProvisioningReceiptTests(unittest.TestCase):
    def test_complete_packet(self):
        self.assertEqual(assess("SUCCEEDED", 0, clean_destinations()), (True, []))

    def test_headline_success_can_hide_failed_instance(self):
        accepted, reasons = assess("SUCCEEDED", 1, clean_destinations())
        self.assertFalse(accepted)
        self.assertTrue(any("failed stack instances" in reason for reason in reasons))

    def test_missing_or_duplicate_destination(self):
        for receipts in [clean_destinations()[:-1], clean_destinations() + clean_destinations()[:1]]:
            with self.subTest(receipts=len(receipts)):
                self.assertFalse(assess("SUCCEEDED", 0, receipts)[0])

    def test_old_artifact_is_rejected(self):
        receipts = clean_destinations()
        receipts[-1] = Destination("prod-west", "CURRENT", "sha256:old-41", True, True)
        self.assertFalse(assess("SUCCEEDED", 0, receipts)[0])

    def test_wrong_source_or_plan_is_rejected(self):
        for overrides in [{"source_revision": "commit-other"}, {"plan_revision": "plan-other"}]:
            with self.subTest(overrides=overrides):
                self.assertFalse(assess("SUCCEEDED", 0, clean_destinations(), **overrides)[0])

    def test_outdated_or_capacity_failure_is_rejected(self):
        for operation, capacity in [("OUTDATED", True), ("CURRENT", False)]:
            with self.subTest(operation=operation, capacity=capacity):
                receipts = clean_destinations()
                receipts[-1] = Destination("prod-west", operation, REVIEWED_IMAGE, capacity, True)
                self.assertFalse(assess("SUCCEEDED", 0, receipts)[0])

    def test_customer_failure_is_rejected(self):
        receipts = clean_destinations()
        receipts[-1] = Destination("prod-west", "CURRENT", REVIEWED_IMAGE, True, False)
        self.assertFalse(assess("SUCCEEDED", 0, receipts)[0])


if __name__ == "__main__":
    unittest.main()
