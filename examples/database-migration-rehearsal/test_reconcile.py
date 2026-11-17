import copy
import json
from pathlib import Path
import unittest

from reconcile import compare

FIXTURES = Path(__file__).parent / "fixtures"


class ReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.source = json.loads((FIXTURES / "source.json").read_text())

    def test_equal_aggregates_hide_identity_and_semantic_damage(self):
        target = json.loads((FIXTURES / "faulty-target.json").read_text())
        result = compare(self.source, target)
        self.assertEqual(result["result"], "HOLD")
        self.assertEqual(result["missing_ids"], ["B104"])
        self.assertEqual(result["unexpected_ids"], ["B105"])
        self.assertEqual(set(result["changed_fields"]), {"B102", "B103"})
        self.assertEqual(set(result["changed_fields"]["B103"]), {"amount_cents", "status"})
        self.assertEqual(result["totals"]["expected"],
                         {"rows": 4, "amount_cents": 40000, "confirmed_cents": 35000})
        self.assertEqual(result["totals"]["candidate"],
                         {"rows": 4, "amount_cents": 40000, "confirmed_cents": 40000})

    def test_row_order_does_not_change_identity(self):
        self.assertEqual(compare(self.source, self.source[::-1])["result"], "MATCH")

    def test_duplicates_on_either_side_are_not_collapsed(self):
        duplicate = self.source + [self.source[0]]
        for left, right, side in ((duplicate, self.source, "expected"),
                                  (self.source, duplicate, "candidate")):
            result = compare(left, right)
            self.assertEqual(result["result"], "HOLD")
            self.assertEqual(result["duplicate_ids"][side], ["B101"])
            self.assertNotIn("changed_fields", result)

    def test_rollback_preserves_newly_accepted_booking(self):
        accepted = json.loads((FIXTURES / "target-after-cutover.json").read_text())
        result = compare(accepted, self.source)
        self.assertEqual(result["result"], "HOLD")
        self.assertEqual(result["missing_ids"], ["B106"])
        self.assertEqual(compare(accepted, copy.deepcopy(accepted))["result"], "MATCH")

    def test_invalid_data_does_not_become_a_match(self):
        for field, value in (("amount_cents", True), ("amount_cents", 1.5),
                             ("amount_cents", -1), ("booking_id", ""),
                             ("status", "unknown")):
            with self.subTest(field=field, value=value):
                invalid = copy.deepcopy(self.source)
                invalid[0][field] = value
                with self.assertRaises(ValueError):
                    compare(invalid, invalid)
        for rows in ([], {}, [{"booking_id": "B101"}]):
            with self.assertRaises(ValueError):
                compare(rows, rows)

    def test_customer_change_is_not_hidden_by_equal_amount(self):
        target = copy.deepcopy(self.source)
        target[0]["customer"] = "Another customer"
        result = compare(self.source, target)
        self.assertEqual(result["result"], "HOLD")
        self.assertEqual(set(result["changed_fields"]["B101"]), {"customer"})


if __name__ == "__main__":
    unittest.main()
