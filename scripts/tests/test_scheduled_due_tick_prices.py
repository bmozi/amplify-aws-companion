"""Offline checks for the public-price selection and stale-rate guard."""

import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    'scheduled_prices', ROOT / 'scripts/refresh-scheduled-due-tick-prices.py')
prices = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prices)


class ScheduledPriceTests(unittest.TestCase):
    def setUp(self):
        self.recorded = json.loads((ROOT / 'examples/costs/ohio-scheduled-due-tick-2026-10-19.json').read_text())

    def test_paid_scheduler_tier_and_standard_alarm_are_selected_by_attributes(self):
        for meter_id in prices.NEW_RATES:
            service, sku, usage, unit, start, _ = prices.NEW_RATES[meter_id]
            attrs = {'regionCode': 'us-east-2', 'usagetype': usage}
            if meter_id == 'tick_alarm_months':
                attrs['alarmType'] = 'Standard'
            dimension = {'unit': unit, 'beginRange': start,
                         'pricePerUnit': {'USD': '0.10'},
                         'rateCode': 'selected', 'description': 'synthetic paid tier'}
            offer = {'products': {sku: {'attributes': attrs}},
                     'terms': {'OnDemand': {sku: {'term': {
                         'priceDimensions': {'paid': dimension}}}}}}
            rate, evidence = prices.new_rate(offer, meter_id)
            self.assertEqual(rate, '0.10')
            self.assertEqual(evidence['price_dimension'], 'selected')
            offer['products'][sku]['attributes']['regionCode'] = 'us-west-2'
            with self.assertRaisesRegex(ValueError, 'Ohio product'):
                prices.new_rate(offer, meter_id)

    def test_recorded_price_check_detects_offer_and_rate_changes(self):
        self.assertEqual(prices.compare_price_evidence(self.recorded, self.recorded), [])
        changed = copy.deepcopy(self.recorded)
        changed['items'][-1]['usd_per_unit'] = '0.99'
        self.assertTrue(any('tick_alarm_months' in reason
                            for reason in prices.compare_price_evidence(changed, self.recorded)))
        changed = copy.deepcopy(self.recorded)
        changed['price_evidence']['services']['AWSEvents']['sha256'] = 'changed'
        self.assertTrue(any('AWSEvents' in reason
                            for reason in prices.compare_price_evidence(changed, self.recorded)))

    def test_template_rejects_invented_sqs_storage_meter(self):
        template = json.loads(prices.TEMPLATE.read_text())
        template['items'].append({'meter_id': 'tick_failure_sqs_storage'})
        with self.assertRaisesRegex(ValueError, 'meter inventory changed'):
            prices.build_worksheet(template, {}, {}, None)


if __name__ == '__main__':
    unittest.main()
