import importlib.util
import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import unittest

path = Path(__file__).resolve().parents[3] / 'scripts/estimate-lab-cost.py'
spec = importlib.util.spec_from_file_location('costs', path)
costs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(costs)
runner_path = Path(__file__).resolve().parents[1] / 'run.py'
runner_spec = importlib.util.spec_from_file_location('runner', runner_path)
runner = importlib.util.module_from_spec(runner_spec)
runner_spec.loader.exec_module(runner)


class CostTests(unittest.TestCase):
    def worksheet(self):
        return {'currency': 'USD', 'region': 'test-region', 'checked_date': '2026-10-18',
                'contingency_percent': 50, 'items': [{'name': 'invented arithmetic fixture', 'quantity': 3,
                'unit': 'fixture', 'usd_per_unit': '0.10', 'source_url': 'https://example.invalid/fixture'}]}

    def test_decimal_units_and_contingency(self):
        result = costs.estimate(self.worksheet())
        self.assertEqual('0.30', result['subtotal_usd'])
        self.assertEqual('0.450', result['with_contingency_usd'])

    def test_missing_price_rejected(self):
        data = self.worksheet()
        data['items'][0]['usd_per_unit'] = None
        with self.assertRaises(ValueError): costs.estimate(data)

    def test_negative_nan_and_undated_inputs_rejected(self):
        for value in ['-1', 'NaN', 'Infinity']:
            data = self.worksheet()
            data['items'][0]['quantity'] = value
            with self.assertRaises(ValueError): costs.estimate(data)
        data = self.worksheet()
        data['checked_date'] = 'not checked'
        with self.assertRaises(ValueError): costs.estimate(data)

    def test_ohio_scenario_keeps_polling_and_documented_arithmetic_visible(self):
        worksheet = Path(__file__).resolve().parents[3] / 'examples/costs/ohio-core-services-2026-10-18.json'
        data = json.loads(worksheet.read_text())
        sqs = next(item for item in data['items'] if item['name'].startswith('SQS '))
        self.assertEqual(sqs['quantity'], 400000)
        result = costs.estimate(data)
        self.assertEqual(result['subtotal_usd'], '0.1801716875')
        self.assertEqual(result['with_contingency_usd'], '0.3603433750')

    def test_priced_indexed_example_cannot_authorize_a_live_run(self):
        worksheet = Path(__file__).resolve().parents[3] / 'examples/costs/ohio-indexed-hold-2026-10-19.json'
        data = json.loads(worksheet.read_text())
        self.assertEqual(data['run_review']['status'], 'pending')
        self.assertEqual(data['run_review']['hold_mode'], 'scan_and_query_due')
        self.assertEqual(set(data['price_evidence']['meters']),
                         {item['meter_id'] for item in data['items']})
        result = costs.estimate(data)
        self.assertEqual(result['subtotal_usd'], '0.1836716875000')
        self.assertEqual(result['with_contingency_usd'], '0.3673433750000')
        config = {'account_id': '123456789012', 'region': 'us-east-2',
                  'estimated_run_cost_usd': 1}
        with self.assertRaisesRegex(ValueError, 'Complete a cost review'):
            runner.validate_cost_worksheet(data, config, datetime(2026, 10, 19, tzinfo=timezone.utc))

    def test_priced_schedule_scenario_is_arithmetic_not_live_authority(self):
        path = (Path(__file__).resolve().parents[3] /
                'examples/costs/ohio-scheduled-due-tick-2026-10-19.json')
        data = json.loads(path.read_text())
        self.assertEqual(len(data['items']), 15)
        self.assertNotIn('tick_failure_sqs_storage',
                         {item['meter_id'] for item in data['items']})
        self.assertEqual(data['run_review']['status'], 'pending')
        result = costs.estimate(data)
        self.assertEqual(result['subtotal_usd'], '0.1870736875000')
        self.assertEqual(result['with_contingency_usd'], '0.3741473750000')
        config = {'account_id': '123456789012', 'region': 'us-east-2',
                  'estimated_run_cost_usd': 1, 'enable_due_tick_schedule': True}
        with self.assertRaisesRegex(ValueError, 'Complete a cost review'):
            runner.validate_cost_worksheet(data, config,
                                           datetime(2026, 10, 19, tzinfo=timezone.utc))

    def test_opt_in_contact_worklist_requires_its_own_reviewed_usage(self):
        data = json.loads((Path(__file__).resolve().parents[3] /
                           'examples/costs/ohio-indexed-hold-2026-10-19.json').read_text())
        data['run_review'].update(status='complete_live_run', account_id='123456789012',
                                  contact_worklist_mode='manual_review')
        for entry in data['run_review']['cost_drivers'].values():
            entry.update(decision='priced', reason='Synthetic cost-gate test only')
        config = {'account_id': '123456789012', 'region': 'us-east-2',
                  'estimated_run_cost_usd': 5, 'expires_at_epoch': 1800000000,
                  'enable_contact_worklist': True}
        now = datetime(2026, 10, 19, tzinfo=timezone.utc)
        with self.assertRaisesRegex(ValueError, 'contact_scan_reads'):
            runner.validate_cost_worksheet(data, config, now)
        for meter_id, unit in runner.CONTACT_METERS.items():
            data['items'].append({'meter_id': meter_id, 'name': meter_id,
                                  'quantity': 3, 'unit': unit,
                                  'usd_per_unit': '0.000001',
                                  'source_url': 'https://example.invalid/synthetic-rate'})
        with self.assertRaisesRegex(ValueError, 'contact-worklist operator'):
            runner.validate_cost_worksheet(data, config, now)
        data['run_review']['contact_review'] = {
            'operator': 'Test operator', 'planned_due_checks': 2,
            'planned_worklist_reads': 2,
            'scan_and_cursor_procedure': 'Follow every cursor and repeat later',
            'worklist_followup_procedure': 'Read open work and contact through a separate approved process',
            'cleanup_deadline_epoch': config['expires_at_epoch'] + 1800}
        with self.assertRaisesRegex(ValueError, 'contact_lambda_requests must cover'):
            runner.validate_cost_worksheet(data, config, now)
        next(x for x in data['items'] if x.get('meter_id') == 'contact_lambda_requests')['quantity'] = 4
        self.assertGreater(runner.validate_cost_worksheet(data, config, now), 0)
        with self.assertRaisesRegex(ValueError, 'contact_worklist_mode'):
            runner.validate_cost_worksheet(data, dict(config, enable_contact_worklist=False), now)

    def test_contact_worksheet_is_complete_inventory_but_pending(self):
        path = (Path(__file__).resolve().parents[3] /
                'examples/costs/contact-worklist-worksheet.json')
        data = json.loads(path.read_text())
        self.assertEqual('pending', data['run_review']['status'])
        self.assertEqual('manual_review', data['run_review']['contact_worklist_mode'])
        self.assertEqual(set(runner.CONTACT_METERS),
                         {item['meter_id'] for item in data['items']
                          if item['meter_id'].startswith('contact_')})
        self.assertTrue(all(item['quantity'] is None and item['usd_per_unit'] is None
                            for item in data['items'] if item['meter_id'] in runner.CONTACT_METERS))
        data['checked_date'] = '2026-10-19'
        config = {'account_id': '123456789012', 'region': 'us-east-2',
                  'estimated_run_cost_usd': 5, 'enable_contact_worklist': True}
        with self.assertRaisesRegex(ValueError, 'Complete a cost review'):
            runner.validate_cost_worksheet(data, config,
                                           datetime(2026, 10, 19, tzinfo=timezone.utc))

    def test_live_review_rejects_core_subtotal_and_mismatched_estimate(self):
        data = json.loads((Path(__file__).resolve().parents[3] / 'examples/costs/ohio-core-services-2026-10-18.json').read_text())
        now = datetime(2026, 10, 19, tzinfo=timezone.utc)
        config = {'account_id': '123456789012', 'region': 'us-east-2', 'estimated_run_cost_usd': 1}
        with self.assertRaisesRegex(ValueError, 'Complete a cost review'):
            runner.validate_cost_worksheet(data, config, now)
        data['run_review']['status'] = 'complete_live_run'
        data['run_review']['account_id'] = config['account_id']
        data['run_review']['hold_mode'] = 'immediate_only'
        for entry in data['run_review']['cost_drivers'].values():
            entry.update(decision='not_applicable', reason='Fictional reviewed test fixture')
        with self.assertRaisesRegex(ValueError, 'subtotal is still marked incomplete'):
            runner.validate_cost_worksheet(data, config, now)
        data['limitations'] = ['Fictional test input; no AWS prices or usage were verified.']
        data['run_review']['hold_mode'] = 'pending'
        with self.assertRaisesRegex(ValueError, 'hold mode'):
            runner.validate_cost_worksheet(data, config, now)
        data['run_review']['hold_mode'] = 'immediate_only'
        with self.assertRaisesRegex(ValueError, 'due_gsi_writes'):
            runner.validate_cost_worksheet(data, config, now)
        data['items'].extend([
            {'meter_id': meter_id, 'name': meter_id, 'quantity': 0, 'unit': unit,
             'usd_per_unit': '0.01', 'source_url': 'https://example.invalid/fictional-rate'}
            for meter_id, unit in runner.INDEX_METERS.items()
        ])
        self.assertEqual(runner.validate_cost_worksheet(data, config, now), Decimal('0.3603433750'))
        data['run_review']['schedule_mode'] = 'scheduled_due_tick'
        with self.assertRaisesRegex(ValueError, 'schedule_mode'):
            runner.validate_cost_worksheet(data, config, now)
        del data['run_review']['schedule_mode']
        with self.assertRaisesRegex(ValueError, 'manual_only'):
            runner.validate_cost_worksheet(data, config, now)
        data['run_review']['schedule_mode'] = 'manual_only'
        with self.assertRaisesRegex(ValueError, 'below the reviewed worksheet'):
            runner.validate_cost_worksheet(data, dict(config, estimated_run_cost_usd='0.36'), now)
        with self.assertRaisesRegex(ValueError, 'currency/Region'):
            runner.validate_cost_worksheet(data, dict(config, region='us-west-2'), now)
        with self.assertRaisesRegex(ValueError, 'within seven days'):
            runner.validate_cost_worksheet(data, config, datetime(2026, 10, 27, tzinfo=timezone.utc))
        data['run_review']['cost_drivers']['tax']['reason'] = ''
        with self.assertRaisesRegex(ValueError, 'tax'):
            runner.validate_cost_worksheet(data, config, now)

    def test_hold_modes_require_index_usage_and_rates(self):
        data = json.loads((Path(__file__).resolve().parents[3] / 'examples/costs/ohio-core-services-2026-10-18.json').read_text())
        data['run_review'].update(status='complete_live_run', account_id='123456789012', hold_mode='query_due')
        for entry in data['run_review']['cost_drivers'].values():
            entry.update(decision='not_applicable', reason='Fictional fixture only')
        data['limitations'] = ['Fictional fixture; no live price or workload verified.']
        template = json.loads((Path(__file__).resolve().parents[3] / 'examples/costs/worksheet.json').read_text())
        data['items'].extend(item for item in template['items'] if item.get('meter_id'))
        config = {'account_id': '123456789012', 'region': 'us-east-2', 'estimated_run_cost_usd': 5}
        now = datetime(2026, 10, 19, tzinfo=timezone.utc)
        with self.assertRaisesRegex(ValueError, 'due_gsi_writes rate'):
            runner.validate_cost_worksheet(data, config, now)
        for item in data['items']:
            if item.get('meter_id'):
                item['usd_per_unit'] = '0.01'  # Synthetic arithmetic fixture, not an AWS rate.
                item['quantity'] = 1 if item['meter_id'] != 'due_gsi_storage' else 0.001
        self.assertGreater(runner.validate_cost_worksheet(data, config, now), 0)
        for meter_id in ('due_gsi_writes', 'due_gsi_storage', 'due_gsi_reads'):
            item = next(item for item in data['items'] if item.get('meter_id') == meter_id)
            original = item['quantity']
            item['quantity'] = 0
            with self.assertRaisesRegex(ValueError, meter_id):
                runner.validate_cost_worksheet(data, config, now)
            item['quantity'] = original
        data['run_review']['hold_mode'] = 'scan_due'
        next(item for item in data['items'] if item.get('meter_id') == 'due_gsi_reads')['quantity'] = 0
        self.assertGreater(runner.validate_cost_worksheet(data, config, now), 0)

    def test_scheduled_candidate_needs_matching_mode_meters_and_operator_route(self):
        data = json.loads((Path(__file__).resolve().parents[3] /
                           'examples/costs/scheduled-due-tick-worksheet.json').read_text())
        now = datetime(2026, 10, 19, tzinfo=timezone.utc)
        config = {'account_id': '123456789012', 'region': 'us-east-2',
                  'estimated_run_cost_usd': 100, 'expires_at_epoch': 1800000000,
                  'enable_due_tick_schedule': True}
        data['checked_date'] = '2026-10-19'
        data['run_review'].update(status='complete_live_run', account_id=config['account_id'])
        for entry in data['run_review']['cost_drivers'].values():
            entry.update(decision='priced', reason='Synthetic test fixture only')
        data['run_review']['schedule_review'].update(
            operator='Test operator', inspection_interval_minutes=5,
            delivery_failure_procedure='Inspect delivery queue and target permission',
            execution_failure_procedure='Inspect execution record and base hold',
            backlog_reconciliation_procedure='Scan pre-index holds and check due age',
            cleanup_deadline_epoch=config['expires_at_epoch'] + 1800)
        for item in data['items']:
            item['usd_per_unit'] = '0.000001'
        self.assertGreater(runner.validate_cost_worksheet(data, config, now), 0)
        obsolete = {'meter_id': 'tick_failure_sqs_storage', 'name': 'obsolete storage line',
                    'quantity': 1, 'unit': 'GB-month', 'usd_per_unit': '0.01',
                    'source_url': 'https://example.invalid/obsolete'}
        data['items'].append(obsolete)
        with self.assertRaisesRegex(ValueError, 'obsolete tick_failure_sqs_storage'):
            runner.validate_cost_worksheet(data, config, now)
        data['items'].pop()
        with self.assertRaisesRegex(ValueError, 'schedule_mode'):
            runner.validate_cost_worksheet(data, dict(config, enable_due_tick_schedule=False), now)
        data['run_review']['schedule_mode'] = 'manual_only'
        with self.assertRaisesRegex(ValueError, 'schedule_mode'):
            runner.validate_cost_worksheet(data, config, now)
        data['run_review']['schedule_mode'] = 'scheduled_due_tick'
        invocation = next(x for x in data['items'] if x.get('meter_id') == 'eventbridge_scheduler_invocations')
        invocation['quantity'] = 120
        with self.assertRaisesRegex(ValueError, 'at least 121'):
            runner.validate_cost_worksheet(data, config, now)
        invocation['quantity'] = 121
        delivery = next(x for x in data['items'] if x.get('meter_id') == 'tick_delivery_sqs_requests')
        delivery['usd_per_unit'] = None
        with self.assertRaisesRegex(ValueError, 'tick_delivery_sqs_requests rate'):
            runner.validate_cost_worksheet(data, config, now)
        delivery['usd_per_unit'] = '0.000001'
        data['run_review']['schedule_review']['operator'] = 'pending'
        with self.assertRaisesRegex(ValueError, 'operator'):
            runner.validate_cost_worksheet(data, config, now)
        data['run_review']['schedule_review']['operator'] = 'Test operator'
        data['run_review']['schedule_review']['inspection_interval_minutes'] = 6
        with self.assertRaisesRegex(ValueError, 'inspection interval'):
            runner.validate_cost_worksheet(data, config, now)
        data['run_review']['schedule_review']['inspection_interval_minutes'] = 5
        data['run_review']['schedule_review']['cleanup_deadline_epoch'] = config['expires_at_epoch'] + 7200
        with self.assertRaisesRegex(ValueError, 'cleanup deadline'):
            runner.validate_cost_worksheet(data, config, now)
