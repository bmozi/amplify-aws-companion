"""Changed-plan controls for the local governed-delivery lesson."""

from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest


source = Path(__file__).with_name("lab.py")
spec = importlib.util.spec_from_file_location("governed_delivery_lab", source)
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


def proposed(values=None, actions=None):
    return {"resource_changes": [{
        "address": lab.ADDRESS,
        "change": {"actions": ["update"] if actions is None else actions,
                   "after": {"input": deepcopy(lab.BASELINE) if values is None else values}}
    }]}


class ProposalReviewTests(unittest.TestCase):
    def test_reviewed_narrow_proposal_passes(self):
        self.assertEqual(lab.assess(proposed(), lab.BASELINE)[0], "pass")

    def test_wildcard_action_or_resource_rejected(self):
        for key, value in (("action", "s3:*"), ("resource_scope", "*")):
            with self.subTest(key=key):
                changed = {**lab.BASELINE, key: value}
                self.assertEqual(lab.assess(proposed(changed), lab.BASELINE)[0], "reject")

    def test_wrong_owner_and_deletion_rejected(self):
        self.assertEqual(lab.assess(proposed({**lab.BASELINE, "owner": "other"}),
                                    lab.BASELINE)[0], "reject")
        self.assertEqual(lab.assess(proposed(actions=["delete"]), lab.BASELINE)[0], "reject")

    def test_missing_or_extra_proposal_rejected(self):
        self.assertEqual(lab.assess({"resource_changes": []}, lab.BASELINE)[0], "reject")
        self.assertEqual(lab.assess(proposed({}), lab.BASELINE)[0], "reject")
        changed = {**lab.BASELINE, "unreviewed": True}
        self.assertEqual(lab.assess(proposed(changed), lab.BASELINE)[0], "reject")

    def test_intent_changes_need_review_before_reconciliation(self):
        paused = {**lab.BASELINE, "pause_auto_builds": True}
        self.assertEqual(lab.assess(proposed(paused), lab.BASELINE)[0], "review")
        self.assertEqual(lab.assess(proposed(paused), paused)[0], "pass")
        version = {**lab.BASELINE, "module_version": "1.3.0"}
        self.assertEqual(lab.assess(proposed(version), lab.BASELINE)[0], "review")


if __name__ == "__main__":
    unittest.main()
