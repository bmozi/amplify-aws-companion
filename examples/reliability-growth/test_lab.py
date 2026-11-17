import copy
import json
from pathlib import Path
import unittest

from lab import analyze


FIXTURE = json.loads(Path(__file__).with_name("fixture.json").read_text())


class ReliabilityGrowthTests(unittest.TestCase):
    def test_growth_and_worst_zone_loss(self):
        report = analyze(FIXTURE)
        self.assertEqual(report["observed_weekly_changes"], [60, 60, 60])
        self.assertEqual(report["attempts_needed"], 726)
        self.assertEqual([item["worst_failure"]["margin"] for item in report["layouts"]], [-26, 24])
        self.assertEqual(report["layouts"][1]["worst_failure"]["limiter"], "data")

    def test_changed_data_path_erases_candidate_margin(self):
        changed = copy.deepcopy(FIXTURE)
        changed["layouts"][1]["shared_data_attempt_capacity_per_second"] = 700
        self.assertEqual(analyze(changed)["layouts"][1]["worst_failure"]["margin"], -26)

    def test_uneven_history_does_not_rewrite_explicit_planning_case(self):
        changed = copy.deepcopy(FIXTURE)
        changed["weekly_peak_success_per_second"][1] = 430
        report = analyze(changed)
        self.assertNotEqual(report["observed_weekly_changes"], [60, 60, 60])
        self.assertEqual(report["planning_peak_is_supplied_not_predicted"], 660)

    def test_quota_alone_cannot_make_launch_ready(self):
        report = analyze(FIXTURE)
        self.assertNotIn("applied_quota", report["proposed_launch"]["blockers"])
        self.assertIn("compatible_placement", report["proposed_launch"]["blockers"])
        self.assertIn("image_role_permission", report["proposed_launch"]["blockers"])

    def test_all_provisioning_checks_still_do_not_prove_customer_outcome(self):
        changed = copy.deepcopy(FIXTURE)
        changed["proposed_launch"].update(compatible_placement_workers=4,
                                           image_role_permission_verified=True,
                                           registered_and_business_ready_workers=4)
        self.assertEqual(analyze(changed)["proposed_launch"]["status"], "provisioning_candidate_only")

    def test_invalid_capacity_and_retry_are_rejected(self):
        changed = copy.deepcopy(FIXTURE)
        changed["layouts"][0]["zone_attempt_capacity_per_second"]["az_a"] = -1
        with self.assertRaises(ValueError):
            analyze(changed)
        changed = copy.deepcopy(FIXTURE)
        changed["retry_overhead_percent"] = "NaN"
        with self.assertRaises(ValueError):
            analyze(changed)


if __name__ == "__main__":
    unittest.main()
