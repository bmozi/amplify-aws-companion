"""Build a pending A02/A03 contact-worklist teaching estimate from public Ohio offers.

The optional cloud handler has only due/open actions. Local contact-record fixture
work is excluded from its six additional meter rows. No AWS credentials are used.
"""

import argparse
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import importlib.util
import json
from pathlib import Path
from urllib.request import urlopen


BASE = Path(__file__).resolve().parents[1]
TEMPLATE = BASE / 'examples/costs/contact-worklist-worksheet.json'
SCENARIO = BASE / 'examples/costs/contact-worklist/scenario.json'


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


indexed = load_module(BASE / 'scripts/refresh-indexed-hold-prices.py', 'indexed_prices')
contact_lab = load_module(BASE / 'examples/costs/contact-worklist/lab.py', 'contact_cost_lab')

CONTACT_ALIASES = {
    'contact_scan_reads': 'table_reads',
    'contact_escalation_writes': 'table_writes',
    'contact_lambda_requests': 'lambda_requests',
    'contact_lambda_compute': 'lambda_compute',
    'contact_logs_ingest': 'logs_ingest',
    'contact_logs_retention': 'logs_retention',
}


def build_worksheet(template, scenario, offers, fetched, now):
    data = json.loads(json.dumps(template))
    ids = [item.get('meter_id') for item in data['items']]
    expected = set(indexed.RATES) | set(CONTACT_ALIASES)
    if len(ids) != len(set(ids)) or set(ids) != expected:
        raise ValueError('Contact worksheet meter inventory changed')
    modeled = contact_lab.count(scenario)
    candidate = modeled['boundaries']['optional_cloud_handler_candidate']
    local = modeled['boundaries']['local_contact_record_fixture_only']
    calls = candidate['api_calls']['scan']
    if calls != scenario['due_scan_pages'] + scenario['worklist_scan_pages']:
        raise ValueError('Contact page and invocation counts differ')
    data['checked_date'] = now.date().isoformat()
    review = data['run_review']
    review['status'] = 'pending'
    review['account_id'] = 'REPLACE_WITH_CONFIRMED_ACCOUNT'
    review['hold_mode'] = 'scan_and_query_due'
    review['schedule_mode'] = 'manual_only'
    review['contact_worklist_mode'] = 'manual_review'
    for value in review['cost_drivers'].values():
        value.update(decision='pending', reason='')
    # The copied template keeps the invoker, cursor and cleanup review pending.
    quantities = {
        'sqs_standard_requests': 400000,
        'contact_scan_reads': candidate['modeled_table_read_request_units'],
        'contact_escalation_writes': candidate['modeled_table_write_request_units'],
        'contact_lambda_requests': calls,
        # Nine assumed 10-second invocations at 128 MiB. This is a buffer,
        # not measured duration or a timeout setting.
        'contact_lambda_compute': Decimal(calls) * Decimal('10') * Decimal('0.125'),
        'contact_logs_ingest': Decimal('0.001'),
        'contact_logs_retention': Decimal('0.001'),
    }
    evidence = {}
    for item in data['items']:
        meter_id = item['meter_id']
        selected = CONTACT_ALIASES.get(meter_id, meter_id)
        service, _, _, _, _, unit = indexed.RATES[selected]
        if item['unit'] != unit:
            raise ValueError(f'{meter_id}: worksheet unit changed')
        rate, entry = indexed.selected_rate(offers[service], selected)
        item['usd_per_unit'] = rate
        item['source_url'] = fetched[service]['url']
        if meter_id in quantities:
            item['quantity'] = str(quantities[meter_id]) if isinstance(quantities[meter_id], Decimal) else quantities[meter_id]
        evidence[meter_id] = {**entry, 'priced_as': selected}
    data['scenario'] = {
        'kind': 'illustrative_not_authorized',
        'contact_fixture_path': str(SCENARIO.relative_to(BASE)),
        'contact_fixture_sha256': hashlib.sha256(SCENARIO.read_bytes()).hexdigest(),
        'combined_local_model': {
            'reads': modeled['modeled_table_read_request_units'],
            'writes': modeled['modeled_table_write_request_units'],
        },
        'optional_cloud_handler_model': {
            'reads': candidate['modeled_table_read_request_units'],
            'writes': candidate['modeled_table_write_request_units'],
            'invocations': calls,
        },
        'excluded_local_contact_record_model': {
            'reads': local['modeled_table_read_request_units'],
            'writes': local['modeled_table_write_request_units'],
        },
        'base_workload': 'Template base quantities with a 400000-request SQS quiet-polling stress assumption; no current plan, traffic or cleanup review.',
        'contact_compute': 'Nine assumed invocations times 10 seconds times 0.125 GiB = 11.25 GB-seconds.',
        'contact_logs': '0.001 GB ingestion and 0.001 GB-month retention are invented buffers.',
    }
    data['price_evidence'] = {
        'checked_at_utc': now.isoformat(),
        'source': 'AWS public Price List Bulk offer files',
        'services': fetched,
        'meters': evidence,
        'service_pricing_pages': indexed.SERVICE_PAGES,
    }
    data['limitations'] = [
        'Pending teaching scenario, not a reviewed live-run estimate, AWS bill or spending cap.',
        'Public paid-tier rates do not subtract Free Tier or credits; service pages, credit eligibility and account state require current review.',
        'The optional cloud handler can check due work and read open work; it cannot record customer contact.',
        'The 188/32 contact demand is a simplified small-item allowance, neither a lower nor an upper AWS capacity bound.',
        'The base quantities and 10-second contact duration and log buffers are assumptions; they need exact-plan, actual-item and whole-run review.',
        'Data transfer, tax, shared resources, retries, repeat runs, retained storage and cleanup decisions remain pending.',
        'A 100% contingency is not a hard cap. Confirm scoped identity, current account budget and USD 100 reserve before any authorized run.',
    ]
    return data


def compare_recorded(recorded, refreshed):
    """Check selected offer identity and authored fixture, not account readiness."""
    old = json.loads(json.dumps(recorded))
    new = json.loads(json.dumps(refreshed))
    old.get('price_evidence', {}).pop('checked_at_utc', None)
    new.get('price_evidence', {}).pop('checked_at_utc', None)
    return [] if old == new else ['Public offer, selected dimension, authored scenario, worksheet inventory or pending review differs']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--out', type=Path)
    group.add_argument('--check', type=Path)
    args = parser.parse_args()
    offers, fetched = {}, {}
    for service in indexed.SERVICE_PAGES:
        url = f'{indexed.PRICE_BASE}/{service}/current/us-east-2/index.json'
        with urlopen(url, timeout=30) as response:
            raw = response.read()
        offer = json.loads(raw)
        if offer.get('offerCode') != service:
            raise ValueError(f'{service}: unexpected offer code')
        offers[service] = offer
        fetched[service] = {'url': url, 'publication_date': offer['publicationDate'],
                            'sha256': hashlib.sha256(raw).hexdigest()}
    data = build_worksheet(json.loads(TEMPLATE.read_text()), json.loads(SCENARIO.read_text()),
                           offers, fetched, datetime.now(timezone.utc))
    if args.check:
        reasons = compare_recorded(json.loads(args.check.read_text()), data)
        if reasons:
            for reason in reasons:
                print('STALE:', reason)
            return 1
        print('Public offer identity, selected rates and authored quantities match the pending scenario today.')
        print('No account, plan, credit eligibility, operator or cleanup decision was verified.')
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2) + '\n')
    print(f'Wrote pending contact-worklist teaching scenario: {args.out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
