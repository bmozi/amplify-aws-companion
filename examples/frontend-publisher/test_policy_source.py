"""Catch a review snapshot that no longer matches the proposed Terraform role."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).with_name('check-policy.py')
SPEC = importlib.util.spec_from_file_location('publisher_policy_review', SCRIPT)
review = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(review)


class PolicySourceAlignmentTests(unittest.TestCase):
    def setUp(self):
        self.policy = json.loads(review.POLICY.read_text())
        self.terraform = review.TERRAFORM.read_text()

    def test_current_review_snapshot_matches_source(self):
        review.check_source_alignment(self.policy, self.terraform)

    def test_missing_free_plan_grant_is_rejected_before_simulation(self):
        self.policy['Statement'] = self.policy['Statement'][:2]
        with self.assertRaises(ValueError):
            review.check_source_alignment(self.policy, self.terraform)

    def test_changed_terraform_action_or_extra_statement_is_rejected(self):
        changed = self.terraform.replace('"freetier:GetAccountPlanState"',
                                         '"freetier:UpgradeAccountPlan"')
        with self.assertRaises(ValueError):
            review.check_source_alignment(self.policy, changed)
        target = 'sid       = "ReadCurrentFreePlanForPublicationGate"\n    effect    = "Allow"'
        extra = self.terraform.replace(target, target.replace('"Allow"', '"Deny"'))
        self.assertNotEqual(extra, self.terraform)
        with self.assertRaises(ValueError):
            review.check_source_alignment(self.policy, extra)

    def test_private_terraform_target_must_match_reviewed_branch(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            with self.assertRaises(ValueError):
                review.check_selected_target(self.policy, target)
            (target / 'terraform.tfvars').write_text('synthetic input\n')
            matching = '"arn:aws:amplify:us-east-2:111111111111:apps/d000000000000/branches/lab"\n'
            with patch.object(review.subprocess, 'run') as run:
                run.side_effect = [
                    type('Result', (), {'returncode': 0, 'stdout': matching})(),
                    type('Result', (), {'returncode': 0, 'stdout': '"AWS-Learning-Monthly-Cost"\n'})(),
                ]
                review.check_selected_target(self.policy, target)
                run.side_effect = [
                    type('Result', (), {'returncode': 0, 'stdout': matching.replace('/lab', '/other')})(),
                ]
                with self.assertRaises(ValueError):
                    review.check_selected_target(self.policy, target)
                run.side_effect = [
                    type('Result', (), {'returncode': 0, 'stdout': matching})(),
                    type('Result', (), {'returncode': 0, 'stdout': '"OtherBudget"\n'})(),
                ]
                with self.assertRaises(ValueError):
                    review.check_selected_target(self.policy, target)


if __name__ == '__main__':
    unittest.main()
