import importlib.util
from decimal import Decimal
from pathlib import Path
import unittest


spec = importlib.util.spec_from_file_location("compare", Path(__file__).with_name("compare.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CommitmentModelTests(unittest.TestCase):
    def test_steady_and_falling_demand_change_decision(self):
        self.assertGreater(module.compare(module.STEADY)[2], 0)
        self.assertLess(module.compare(module.FALLING)[2], 0)

    def test_idle_hour_still_pays_commitment(self):
        self.assertEqual(module.compare([Decimal("0")]),
                         (Decimal("0"), Decimal("0.40"), Decimal("-0.40")))

    def test_rejects_invalid_inputs(self):
        for hours, commitment, discount in (
            ([], Decimal("0.4"), Decimal("0.25")),
            ([Decimal("-1")], Decimal("0.4"), Decimal("0.25")),
            ([Decimal("1")], Decimal("-1"), Decimal("0.25")),
            ([Decimal("1")], Decimal("0.4"), Decimal("1")),
        ):
            with self.subTest(hours=hours, commitment=commitment, discount=discount):
                with self.assertRaises(ValueError):
                    module.compare(hours, commitment, discount)


if __name__ == "__main__":
    unittest.main()
