import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("hibernation_check.py")
SPEC = importlib.util.spec_from_file_location("hibernation_check", MODULE_PATH)
hibernation_check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(hibernation_check)


def candidate(**changes):
    result = {
        "os": "linux",
        "ram_gib": 8,
        "root_volume_gib": 40,
        "os_and_application_gib": 20,
        "working_space_gib": 8,
        "ami_hibernation_support_verified": True,
        "regional_instance_type_support_verified": True,
        "hibernation_enabled_at_launch": True,
        "root_is_ebs": True,
        "root_volume_type": "gp3",
        "root_is_encrypted": True,
        "managed_by_auto_scaling": False,
        "depends_on_instance_store": False,
    }
    result.update(changes)
    return result


class HibernationChecklistTests(unittest.TestCase):
    def test_complete_candidate_still_requires_aws_verification(self):
        result = hibernation_check.assess(candidate())
        self.assertEqual(result["status"], "needs-aws-verification")
        self.assertIn("no AWS query", result["scope"])

    def test_linux_limit_is_strictly_less_than_150_gib(self):
        self.assertEqual(hibernation_check.assess(candidate(ram_gib=149.9, root_volume_gib=200))["status"], "needs-aws-verification")
        self.assertIn("less than 150", " ".join(hibernation_check.assess(candidate(ram_gib=150, root_volume_gib=200))["errors"]))

    def test_windows_limit_includes_exactly_16_gib(self):
        self.assertEqual(hibernation_check.assess(candidate(os="windows", ram_gib=16, root_volume_gib=60))["status"], "needs-aws-verification")
        self.assertIn("at most 16", " ".join(hibernation_check.assess(candidate(os="windows", ram_gib=16.1, root_volume_gib=60))["errors"]))

    def test_encryption_and_launch_time_are_required(self):
        result = hibernation_check.assess(candidate(root_is_encrypted=False, hibernation_enabled_at_launch=False))
        joined = " ".join(result["errors"])
        self.assertIn("must be encrypted", joined)
        self.assertIn("enabled when the instance is launched", joined)

    def test_unsupported_root_ebs_type_is_rejected(self):
        result = hibernation_check.assess(candidate(root_volume_type="st1"))
        self.assertIn("root EBS volume type", " ".join(result["errors"]))

    def test_asg_and_instance_store_conflicts_are_reported(self):
        result = hibernation_check.assess(candidate(managed_by_auto_scaling=True, depends_on_instance_store=True))
        joined = " ".join(result["errors"])
        self.assertIn("Auto Scaling", joined)
        self.assertIn("instance-store data is lost", joined)

    def test_volume_must_cover_memory_and_supplied_other_space(self):
        result = hibernation_check.assess(candidate(root_volume_gib=35))
        self.assertIn("total 36 GiB", " ".join(result["errors"]))

    def test_nonfinite_and_boolean_capacity_values_are_rejected(self):
        self.assertIn("finite", " ".join(hibernation_check.assess(candidate(ram_gib=float("inf")))["errors"]))
        self.assertIn("must be a number", " ".join(hibernation_check.assess(candidate(ram_gib=True))["errors"]))

    def test_unverified_support_is_not_assumed(self):
        result = hibernation_check.assess(candidate(ami_hibernation_support_verified=False))
        self.assertIn("exact AMI", " ".join(result["errors"]))
        self.assertEqual(result["status"], "not-ready")

    def test_non_object_input_is_rejected(self):
        self.assertEqual(hibernation_check.assess([])["status"], "invalid")

    def test_unexpected_field_types_fail_closed(self):
        result = hibernation_check.assess(candidate(os=[], root_volume_type=[], managed_by_auto_scaling="no"))
        joined = " ".join(result["errors"])
        self.assertIn("os must be", joined)
        self.assertIn("root EBS volume type", joined)
        self.assertIn("must be explicitly true or false", joined)


if __name__ == "__main__":
    unittest.main()
