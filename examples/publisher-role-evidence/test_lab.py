"""The source-alignment screen must refuse both extra grants and unknown reads."""
from copy import deepcopy
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from lab import ACCOUNT, POLICY, SUBJECT, cases
from review import main, review


class RoleEvidenceTests(unittest.TestCase):
    def test_three_distinct_evidence_states(self):
        receipts = cases()
        states = {name: review(value, POLICY, account_id=ACCOUNT, subject=SUBJECT)
                  for name, value in receipts.items()}
        self.assertEqual(states["declared_documents"]["document_alignment"], "matched")
        self.assertEqual(states["extra_attached_policy"]["document_alignment"], "review_required")
        self.assertEqual(states["unreadable_attachment_list"]["document_alignment"], "review_required")
        self.assertIn("An additional attached policy needs review", states["extra_attached_policy"]["reasons"])
        self.assertIn("Attached-policy inventory is unavailable", states["unreadable_attachment_list"]["reasons"])

    def test_unexpected_trust_subject_is_not_aligned(self):
        receipt = deepcopy(cases()["declared_documents"])
        receipt["checks"]["publisher_role"]["trust_document"]["Statement"][0]["Condition"]["StringEquals"]["token.actions.githubusercontent.com:sub"] = "repo:other@10/learning@20:ref:refs/heads/main"
        result = review(receipt, POLICY, account_id=ACCOUNT, subject=SUBJECT)
        self.assertTrue(any("trust differs" in reason for reason in result["reasons"]))

    def test_wider_inline_resource_is_not_aligned(self):
        receipt = deepcopy(cases()["declared_documents"])
        receipt["checks"]["publisher_inline_PublishOneAmplifyBranch"]["Statement"][0]["Resource"] = "*"
        result = review(receipt, POLICY, account_id=ACCOUNT, subject=SUBJECT)
        self.assertTrue(any("inline policy differs" in reason for reason in result["reasons"]))

    def test_cli_reports_alignment_without_printing_role_documents(self):
        with TemporaryDirectory() as directory:
            receipt = Path(directory) / "receipt.json"
            policy = Path(directory) / "policy.json"
            receipt.write_text(json.dumps(cases()["declared_documents"]))
            policy.write_text(json.dumps(POLICY))
            output = StringIO()
            arguments = ["review.py", str(receipt), "--expected-policy", str(policy),
                         "--account-id", ACCOUNT, "--subject", SUBJECT]
            with patch.object(sys, "argv", arguments), redirect_stdout(output):
                self.assertEqual(main(), 0)
            result = json.loads(output.getvalue())
            self.assertEqual(result["document_alignment"], "matched")
            self.assertNotIn("AssumeRoleWithWebIdentity", output.getvalue())
            self.assertNotIn(SUBJECT, output.getvalue())


if __name__ == "__main__":
    unittest.main()
