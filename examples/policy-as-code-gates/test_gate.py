import copy
import json
import unittest

from gate import HERE, inspect_template


class PolicyGateTests(unittest.TestCase):
    def setUp(self):
        self.template = json.loads((HERE / "template.json").read_text())

    def test_reviewed_bucket_passes_specimen(self):
        self.assertEqual(inspect_template(self.template), [])

    def test_missing_encryption_is_found(self):
        changed = copy.deepcopy(self.template)
        del changed["Resources"]["ReportsBucket"]["Properties"]["BucketEncryption"]
        self.assertIn("BucketEncryption absent", inspect_template(changed)[0])

    def test_one_false_public_flag_is_found(self):
        changed = copy.deepcopy(self.template)
        changed["Resources"]["ReportsBucket"]["Properties"]["PublicAccessBlockConfiguration"]["RestrictPublicBuckets"] = False
        self.assertIn("all four", inspect_template(changed)[0])

    def test_non_bucket_does_not_claim_bucket_check(self):
        changed = {"Resources": {"Function": {"Type": "AWS::Lambda::Function", "Properties": {}}}}
        self.assertEqual(inspect_template(changed), [])


if __name__ == "__main__":
    unittest.main()
