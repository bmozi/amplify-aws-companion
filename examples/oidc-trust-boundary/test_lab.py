"""Negative controls for the trust lesson's most consequential boundaries."""

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from lab import CASES, SOURCE, evaluate, require_current_trust_shape, workflow_sources
import lab


class TrustBoundaryTests(unittest.TestCase):
    def test_reduced_packet_requires_both_inert_workflows(self):
        with tempfile.TemporaryDirectory() as temporary, patch.object(lab, "ROOT", Path(temporary)):
            root = Path(temporary)
            inert = root / "examples/github-workflows"
            inert.mkdir(parents=True)
            publisher = inert / "amplify-publish.yml"
            probe = inert / "probe-amplify-publisher-identity.yml"
            reusable = inert / "reusable-amplify-publish.yml"
            publisher.write_text("name: Publish the Amplify lab frontend\n")
            with self.assertRaisesRegex(ValueError, "All three inert workflow copies"):
                workflow_sources()
            probe.write_text("name: Probe the Amplify reader identity without deploying\n")
            with self.assertRaisesRegex(ValueError, "All three inert workflow copies"):
                workflow_sources()
            reusable.write_text("name: Reviewed Amplify publication job\n")
            self.assertEqual(workflow_sources(), (publisher, probe, reusable))
            active = root / ".github/workflows"
            active.mkdir(parents=True)
            (active / "amplify-publish.yml").write_text(publisher.read_text())
            with self.assertRaisesRegex(ValueError, "Only part of the active workflow set"):
                workflow_sources()

    def test_named_workflows_and_name_copy_limit(self):
        require_current_trust_shape(SOURCE.read_text())
        rows = {row["name"]: row for row in evaluate(json.loads(CASES.read_text()))}
        self.assertTrue(rows["publisher_manual_yes"]["publisher_trust_match"])
        self.assertFalse(rows["publisher_manual_yes"]["probe_trust_match"])
        self.assertTrue(rows["separate_probe_flag_off"]["probe_trust_match"])
        self.assertFalse(rows["separate_probe_flag_off"]["publisher_trust_match"])
        self.assertTrue(rows["copied_workflow_name_other_file"]["publisher_name_match"])
        self.assertFalse(rows["copied_workflow_name_other_file"]["publisher_trust_match"])
        self.assertTrue(rows["different_caller_same_reusable"]["publisher_trust_match"])
        self.assertTrue(rows["copied_probe_name_other_file"]["probe_trust_match"])
        for name in ("new_workflow_flag_off", "same_workflow_other_branch",
                     "same_subject_wrong_audience", "reused_names_different_ids",
                     "environment_subject"):
            self.assertFalse(rows[name]["publisher_trust_match"])
            self.assertFalse(rows[name]["probe_trust_match"])

    def test_wider_or_changed_terraform_trust_stops_this_lesson(self):
        source = SOURCE.read_text()
        with self.assertRaises(ValueError):
            require_current_trust_shape(source.replace('test     = "StringEquals"', 'test     = "StringLike"', 1))

    def test_probe_write_grant_or_publisher_assumption_stops_lesson(self):
        source = SOURCE.read_text()
        with self.assertRaisesRegex(ValueError, "Probe policy actions"):
            head, tail = source.split('data "aws_iam_policy_document" "probe_read"', 1)
            require_current_trust_shape(head + 'data "aws_iam_policy_document" "probe_read"' +
                                        tail.replace('actions   = ["amplify:GetJob"]',
                                                     'actions   = ["amplify:StartDeployment"]', 1))
        workflow = workflow_sources()[1]
        self.assertNotIn("AWS_LAB_AMPLIFY_PUBLISH_ROLE_ARN", workflow.read_text())


if __name__ == "__main__":
    unittest.main()
