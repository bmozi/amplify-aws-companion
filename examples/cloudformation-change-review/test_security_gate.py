import copy
import unittest

from review import load_baseline, proposed_template
from security_gate import findings


class SecurityGateTests(unittest.TestCase):
    def test_safe_study_variations_keep_contract(self):
        for case in ("tag", "name", "unknown"):
            with self.subTest(case=case):
                self.assertEqual(findings(proposed_template(case)), [])

    def test_public_and_transport_regressions_are_distinct(self):
        self.assertTrue(any("BlockPublicPolicy" in item for item in findings(proposed_template("public"))))
        self.assertTrue(any("non-TLS deny" in item for item in findings(proposed_template("transport"))))

    def test_policy_target_and_retention_are_checked(self):
        template = copy.deepcopy(load_baseline())
        template["Resources"]["TransportPolicy"]["Properties"]["Bucket"] = "another-bucket"
        template["Resources"]["TransportPolicy"].pop("UpdateReplacePolicy")
        issues = findings(template)
        self.assertTrue(any("must target ArchiveBucket" in item for item in issues))
        self.assertTrue(any("TransportPolicy.UpdateReplacePolicy" in item for item in issues))

    def test_encryption_and_versioning_are_checked(self):
        template = copy.deepcopy(load_baseline())
        props = template["Resources"]["ArchiveBucket"]["Properties"]
        props.pop("BucketEncryption")
        props["VersioningConfiguration"]["Status"] = "Suspended"
        issues = findings(template)
        self.assertTrue(any("default encryption" in item for item in issues))
        self.assertTrue(any("versioning" in item for item in issues))


if __name__ == "__main__":
    unittest.main()
