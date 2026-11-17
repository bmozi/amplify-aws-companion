"""Check decision reversals and refusal of incomplete fictional estimates."""
import copy
import importlib.util
import json
from decimal import Decimal
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('cost05_compare', HERE / 'compare.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CostChoiceTests(unittest.TestCase):
    def setUp(self):
        self.case = json.loads((HERE / 'fictional-case.json').read_text())

    def test_growth_reverses_monthly_preference_but_not_year_total(self):
        result = module.evaluate(self.case)
        self.assertLess(result['two-month pilot']['managed']['monthly'], result['two-month pilot']['self_operated']['monthly'])
        self.assertGreater(result['ten-month growth']['managed']['monthly'], result['ten-month growth']['self_operated']['monthly'])
        totals = {name: sum((phase[name]['phase'] for phase in result.values()), Decimal(0)) for name in self.case['designs']}
        self.assertLess(totals['managed'], totals['self_operated'])

    def test_missing_meter_is_not_treated_as_zero(self):
        incomplete = copy.deepcopy(self.case)
        del incomplete['designs']['managed']['transfer']
        with self.assertRaisesRegex(ValueError, 'missing or extra cost meter'):
            module.evaluate(incomplete)


if __name__ == '__main__':
    unittest.main()
