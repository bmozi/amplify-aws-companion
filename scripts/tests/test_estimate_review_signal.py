"""The cost calculator must keep arithmetic separate from run authorization."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('estimate_lab_cost', ROOT / 'scripts/estimate-lab-cost.py')
ESTIMATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ESTIMATOR)
WORKSHEET = json.loads((ROOT / 'examples/costs/ohio-contact-worklist-2026-10-26-utc.json').read_text())


class ReviewSignalTests(unittest.TestCase):
    def test_current_dated_study_shows_pending_decisions_beside_total(self):
        result = ESTIMATOR.estimate(WORKSHEET)
        self.assertEqual(result['subtotal_usd'], '0.1844344878750')
        signal = result['review_signal']
        self.assertEqual(signal['worksheet_status'], 'pending')
        self.assertFalse(signal['account_field_filled'])
        self.assertEqual(len(signal['pending_cost_drivers']), 7)
        self.assertEqual(signal['deployment_permission'], 'not_granted_by_estimator')

    def test_declared_complete_still_does_not_grant_permission(self):
        worksheet = copy.deepcopy(WORKSHEET)
        review = worksheet['run_review']
        review['status'] = 'complete_live_run'
        review['account_id'] = '123456789012'
        for entry in review['cost_drivers'].values():
            entry.update(decision='priced', reason='Synthetic test statement, not verified')
        signal = ESTIMATOR.estimate(worksheet)['review_signal']
        self.assertEqual(signal['worksheet_status'], 'complete_live_run')
        self.assertTrue(signal['account_field_filled'])
        self.assertEqual(signal['pending_cost_drivers'], [])
        self.assertEqual(signal['deployment_permission'], 'not_granted_by_estimator')

    def test_missing_review_is_visible(self):
        worksheet = copy.deepcopy(WORKSHEET)
        del worksheet['run_review']
        signal = ESTIMATOR.estimate(worksheet)['review_signal']
        self.assertEqual(signal['worksheet_status'], 'missing')
        self.assertEqual(signal['deployment_permission'], 'not_granted_by_estimator')


if __name__ == '__main__':
    unittest.main()
