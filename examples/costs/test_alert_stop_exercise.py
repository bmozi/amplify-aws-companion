import importlib.util
from pathlib import Path
import sys
import unittest

path = Path(__file__).with_name('alert-stop-exercise.py')
spec = importlib.util.spec_from_file_location('alert_stop_exercise', path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class EvidenceTests(unittest.TestCase):
    def test_alert_and_named_stop_do_not_imply_complete_cleanup(self):
        result = module.classify(module.Evidence(True, True, True, True, False, False))
        self.assertEqual(result['named_worker_stop'], 'reported')
        self.assertEqual(result['replacement'], 'observed')
        self.assertEqual(result['volume'], 'present')
        self.assertEqual(result['full_inventory'], 'not verified')
        self.assertEqual(result['later_billing'], 'not reconciled')

    def test_absence_of_observation_does_not_mean_absence_of_resource(self):
        result = module.classify(module.Evidence(False, False, False, False, False, False))
        self.assertEqual(result['replacement'], 'not observed')
        self.assertEqual(result['volume'], 'not observed present')
        self.assertEqual(result['full_inventory'], 'not verified')

    def test_claimed_inventory_does_not_imply_billing_reconciliation(self):
        result = module.classify(module.Evidence(True, True, False, False, True, False))
        self.assertEqual(result['full_inventory'], 'reported verified')
        self.assertEqual(result['later_billing'], 'not reconciled')

    def test_rejects_non_boolean_values(self):
        with self.assertRaises(ValueError):
            module.classify(module.Evidence(True, True, False, 'unknown', False, False))


if __name__ == '__main__':
    unittest.main()
