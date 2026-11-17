"""Changed-case checks for the pending smoke-audience price bridge."""

from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path
import unittest

from smoke_bridge import HERE, RECORD, bridge


class SmokeBridgeTests(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads((HERE / "smoke-plan.json").read_text())
        self.scenario = json.loads((HERE / "public-price-scenario.json").read_text())
        self.snapshot = json.loads((HERE / "public-prices-us-east-2.json").read_text())
        self.record = json.loads(RECORD.read_text())

    def assess(self, *, plan=None, snapshot=None, record=None):
        return bridge(plan or self.plan, self.scenario, snapshot or self.snapshot,
                      record or self.record)

    def test_same_audience_reconciles_selected_service_groups(self):
        result = self.assess()
        self.assertEqual(result["record_review_status"], "review_needed")
        self.assertEqual(result["selected_preallowance_subtotal_usd"],
                         "0.399490896087500000")
        self.assertEqual(Decimal(result["groups"]["hosting"]["selected_preallowance_usd"]),
                         Decimal("0.02273"))
        self.assertIsNone(result["groups"]["network"]["selected_preallowance_usd"])
        self.assertFalse(result["can_copy_to_reviewed_record"])

    def test_old_half_megabyte_hosting_guess_is_rejected(self):
        changed = deepcopy(self.plan)
        changed["hosting_bytes_per_visit"] = "500000"
        with self.assertRaisesRegex(ValueError, "exact audience"):
            self.assess(plan=changed)

    def test_changed_public_hosting_rate_is_rejected_against_record(self):
        changed = deepcopy(self.snapshot)
        changed["rates"]["hosting_transfer_gb"]["usd_per_unit"] = "0.20"
        with self.assertRaisesRegex(ValueError, "Hosting meter disagrees"):
            self.assess(snapshot=changed)

    def test_marking_pending_record_reviewed_does_not_pass_bridge(self):
        changed = deepcopy(self.record)
        changed["review_status"] = "reviewed"
        with self.assertRaisesRegex(ValueError, "cannot approve"):
            self.assess(record=changed)

    def test_backend_placeholder_disguised_as_reviewed_is_rejected(self):
        changed = deepcopy(self.record)
        changed["backend_components"]["cognito"]["review_status"] = "reviewed"
        with self.assertRaisesRegex(ValueError, "unreviewed backend placeholders"):
            self.assess(record=changed)


if __name__ == "__main__":
    unittest.main()
