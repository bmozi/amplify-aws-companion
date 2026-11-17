"""Negative controls for the read-only public-rate comparison."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    'price_refresh', ROOT / 'scripts/refresh-indexed-hold-prices.py')
PRICE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PRICE)
RECORDED = json.loads((ROOT / 'examples/costs/ohio-indexed-hold-2026-10-19.json').read_text())


class PriceEvidenceCheck(unittest.TestCase):
    def test_matching_snapshot_is_only_a_rate_match(self):
        self.assertEqual(PRICE.compare_price_evidence(RECORDED, RECORDED,
                                                       RECORDED['checked_date']), [])
        self.assertEqual(RECORDED['run_review']['status'], 'pending')

    def test_changed_offer_or_selected_rate_fails(self):
        changed_offer = copy.deepcopy(RECORDED)
        changed_offer['price_evidence']['services']['AmazonDynamoDB']['sha256'] = 'changed'
        self.assertTrue(any('AmazonDynamoDB' in reason for reason in
                            PRICE.compare_price_evidence(changed_offer, RECORDED,
                                                         RECORDED['checked_date'])))
        changed_rate = copy.deepcopy(RECORDED)
        next(item for item in changed_rate['items'] if item['meter_id'] == 'due_gsi_writes')['usd_per_unit'] = '0'
        self.assertTrue(any('due_gsi_writes' in reason for reason in
                            PRICE.compare_price_evidence(changed_rate, RECORDED,
                                                         RECORDED['checked_date'])))

    def test_missing_meter_and_old_check_date_fail(self):
        incomplete = copy.deepcopy(RECORDED)
        incomplete['items'].pop()
        incomplete['checked_date'] = '2026-01-01'
        reasons = PRICE.compare_price_evidence(incomplete, RECORDED, RECORDED['checked_date'])
        self.assertTrue(any('meter inventory' in reason for reason in reasons))
        self.assertTrue(any('price-check date' in reason for reason in reasons))


if __name__ == '__main__':
    unittest.main()
