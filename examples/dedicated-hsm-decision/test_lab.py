import unittest
from dataclasses import replace

from lab import Plan, fixture, review


class DedicatedHsmDecisionTests(unittest.TestCase):
    def test_single_hsm_and_zone_failures_differ(self):
        findings = review(fixture())
        self.assertNotIn("single-HSM-loss toy capacity below promised peak", findings)
        self.assertIn("largest-zone-loss toy capacity below promised peak", findings)
        self.assertNotIn("largest-zone-loss toy capacity below promised peak",
                         review(replace(fixture(), hsms_by_zone=(1, 1, 1))))

    def test_backup_and_connection_are_separate(self):
        changed = replace(fixture(), latest_known_backup_age_hours=4)
        self.assertNotIn("latest known backup older than promised RPO", review(changed))
        self.assertIn("disconnected custom store cannot serve fresh KMS cryptographic operations",
                      review(changed))

    def test_high_volume_and_redundancy_are_not_a_free_pass(self):
        changed = replace(fixture(), hsms_by_zone=(1, 1, 1),
                          latest_known_backup_age_hours=4, custom_store_connected=True,
                          high_volume_s3_path=True)
        self.assertEqual(review(changed),
                         ("high-volume S3 path conflicts with custom-store performance guidance",))
        one_hsm = replace(changed, hsms_by_zone=(1, 0, 0))
        self.assertIn("multi-zone HSM availability claim unsupported", review(one_hsm))

    def test_bad_input_is_rejected(self):
        with self.assertRaises(ValueError):
            review(Plan((), 40, 70, 1, 12, True))
        with self.assertRaises(ValueError):
            review(replace(fixture(), hsms_by_zone=(1, -1, 2)))


if __name__ == "__main__":
    unittest.main()
