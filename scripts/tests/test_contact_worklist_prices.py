"""Guard the authored-price bridge's boundary and pending-review status."""

from datetime import datetime, timezone
from decimal import Decimal
import importlib.util
import json
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    'contact_prices', ROOT / 'scripts/refresh-contact-worklist-prices.py')
prices = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prices)


class ContactPriceBridgeTest(TestCase):
    def setUp(self):
        self.template = json.loads(prices.TEMPLATE.read_text())
        self.scenario = json.loads(prices.SCENARIO.read_text())
        self.fetched = {service: {'url': f'https://example.invalid/{service}',
                                  'publication_date': 'fixture', 'sha256': 'fixture'}
                        for service in prices.indexed.SERVICE_PAGES}

    def build(self):
        def fake_rate(_offer, meter_id):
            service = prices.indexed.RATES[meter_id][0]
            return '0.01', {'service': service, 'sku': 'fixture',
                            'worksheet_unit': prices.indexed.RATES[meter_id][-1]}

        with patch.object(prices.indexed, 'selected_rate', side_effect=fake_rate):
            return prices.build_worksheet(
                self.template, self.scenario,
                {service: {} for service in prices.indexed.SERVICE_PAGES},
                self.fetched, datetime(2026, 10, 26, tzinfo=timezone.utc))

    def test_optional_handler_excludes_local_contact_record_and_stays_pending(self):
        result = self.build()
        rows = {item['meter_id']: item for item in result['items']}
        self.assertEqual(len(rows), 17)
        self.assertEqual(rows['sqs_standard_requests']['quantity'], 400000)
        self.assertEqual(rows['contact_scan_reads']['quantity'], 188)
        self.assertEqual(rows['contact_escalation_writes']['quantity'], 32)
        self.assertEqual(rows['contact_lambda_requests']['quantity'], 9)
        self.assertEqual(Decimal(rows['contact_lambda_compute']['quantity']), Decimal('11.250'))
        self.assertEqual(result['scenario']['excluded_local_contact_record_model'],
                         {'reads': 8, 'writes': 8})
        self.assertEqual(result['run_review']['status'], 'pending')
        self.assertEqual(result['run_review']['contact_review']['operator'], 'pending')

    def test_price_check_detects_quantity_review_and_fixture_drift(self):
        result = self.build()
        self.assertEqual(prices.compare_recorded(result, result), [])
        changed = json.loads(json.dumps(result))
        changed['items'][-6]['quantity'] = 196
        self.assertTrue(prices.compare_recorded(changed, result))
        changed = json.loads(json.dumps(result))
        changed['run_review']['status'] = 'complete_live_run'
        self.assertTrue(prices.compare_recorded(changed, result))
        changed = json.loads(json.dumps(result))
        changed['scenario']['contact_fixture_sha256'] = 'wrong'
        self.assertTrue(prices.compare_recorded(changed, result))

    def test_extra_or_wrong_unit_meter_stops_before_pricing(self):
        self.template['items'].append(dict(self.template['items'][0]))
        with self.assertRaisesRegex(ValueError, 'meter inventory'):
            self.build()
        self.template['items'].pop()
        self.template['items'][-1]['unit'] = 'request'
        with self.assertRaisesRegex(ValueError, 'unit changed'):
            self.build()
