"""Build a pending Ohio scheduled A03 price scenario from AWS public offer files.

This does not inspect the account, consume credits, or authorize Terraform.
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
TEMPLATE = BASE / 'examples/costs/scheduled-due-tick-worksheet.json'
OLD_HELPER = BASE / 'scripts/refresh-indexed-hold-prices.py'
spec = importlib.util.spec_from_file_location('indexed_prices', OLD_HELPER)
indexed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(indexed)

NEW_RATES = {
    'eventbridge_scheduler_invocations': ('AWSEvents', '534HQFPF6VT4G9Y5',
        'USE2-ScheduledInvocation', 'Invocations', '14000000', 'request'),
    'tick_alarm_months': ('AmazonCloudWatch', '28VSMYRVQXUWCTMA',
        'USE2-CW:AlarmMonitorUsage', 'Alarms', '0', 'alarm-month'),
}
SQS_FAILURE_METERS = ('tick_delivery_sqs_requests', 'tick_execution_sqs_requests')
SERVICES = (*indexed.SERVICE_PAGES, 'AWSEvents')


def new_rate(offer, meter_id):
    service, sku, usage_type, aws_unit, start, worksheet_unit = NEW_RATES[meter_id]
    product = offer['products'][sku]
    attrs = product['attributes']
    if (attrs.get('regionCode'), attrs.get('usagetype')) != ('us-east-2', usage_type):
        raise ValueError(f'{meter_id}: Ohio product or usage type changed')
    if meter_id == 'tick_alarm_months' and attrs.get('alarmType') != 'Standard':
        raise ValueError('tick_alarm_months: expected standard-resolution alarm')
    dimensions = [d for term in offer['terms']['OnDemand'][sku].values()
                  for d in term['priceDimensions'].values()
                  if d['unit'] == aws_unit and d['beginRange'] == start]
    if len(dimensions) != 1:
        raise ValueError(f'{meter_id}: expected one paid price dimension')
    d = dimensions[0]
    rate = Decimal(d['pricePerUnit']['USD'])
    if not rate.is_finite() or rate <= 0:
        raise ValueError(f'{meter_id}: paid rate must be positive')
    return str(rate), {'service': service, 'sku': sku, 'usage_type': usage_type,
                       'aws_unit': aws_unit, 'begin_range': start,
                       'price_dimension': d['rateCode'], 'description': d['description'],
                       'worksheet_unit': worksheet_unit}


def build_worksheet(template, offers, fetched, now):
    data = json.loads(json.dumps(template))
    expected = set(indexed.RATES) | set(NEW_RATES) | set(SQS_FAILURE_METERS)
    ids = [x['meter_id'] for x in data['items']]
    if len(ids) != len(set(ids)) or set(ids) != expected:
        raise ValueError('Scheduled worksheet meter inventory changed')
    data['checked_date'] = now.date().isoformat()
    data['run_review']['status'] = 'pending'
    data['run_review']['account_id'] = 'REPLACE_WITH_CONFIRMED_ACCOUNT'
    data['run_review']['schedule_mode'] = 'scheduled_due_tick'
    for review in data['run_review']['cost_drivers'].values():
        review.update(decision='pending', reason='')
    evidence = {}
    for item in data['items']:
        meter_id = item['meter_id']
        if meter_id in indexed.RATES:
            if item['unit'] != indexed.RATES[meter_id][-1]:
                raise ValueError(f'{meter_id}: worksheet unit changed')
            rate, entry = indexed.selected_rate(offers[indexed.RATES[meter_id][0]], meter_id)
        elif meter_id in SQS_FAILURE_METERS:
            if item['unit'] != 'request unit':
                raise ValueError(f'{meter_id}: worksheet unit changed')
            rate, entry = indexed.selected_rate(offers['AWSQueueService'], 'sqs_standard_requests')
            entry = {**entry, 'worksheet_unit': item['unit']}
        else:
            if item['unit'] != NEW_RATES[meter_id][-1]:
                raise ValueError(f'{meter_id}: worksheet unit changed')
            rate, entry = new_rate(offers[NEW_RATES[meter_id][0]], meter_id)
        item['usd_per_unit'] = rate
        item['source_url'] = fetched[entry['service']]['url']
        evidence[meter_id] = entry
    quantities = {
        'sqs_standard_requests': 400000,
        'eventbridge_scheduler_invocations': 242,
        'tick_delivery_sqs_requests': 200,
        'tick_execution_sqs_requests': 200,
    }
    for item in data['items']:
        if item['meter_id'] in quantities:
            item['quantity'] = quantities[item['meter_id']]
    data['scenario'] = {
        'kind': 'illustrative_not_authorized', 'planned_handler_window_hours': 2,
        'scheduler_occurrences': '121 baseline minute boundaries, plus one delivery retry per occurrence as a planning buffer; not a billing cap',
        'failure_queue_requests': '200 per queue for inspection/polling and possible send/receive/delete work; not observed usage',
        'sqs_original_workload': '400000 standard requests for the original A02 queue stress assumption, separate from both failure-queue rows',
        'alarm_months': '0.03 alarm-month equals four standard alarms for about 5.4 hours in a 720-hour month, a buffer beyond the planned two-hour run and one-hour cleanup',
        'storage': 'Table, GSI and logs use GB-month buffers; standard SQS retention has no separate storage row',
    }
    data['price_evidence'] = {
        'checked_at_utc': now.isoformat(), 'source': 'AWS public Price List Bulk offer files',
        'services': fetched, 'meters': evidence,
        'service_pricing_pages': {**indexed.SERVICE_PAGES,
                                  'AWSEvents': 'https://aws.amazon.com/eventbridge/pricing/'},
    }
    data['limitations'] = [
        'Pending teaching scenario, not a complete reviewed live-run estimate, AWS bill or spending cap.',
        'Public paid-tier rates are used without Free Tier or credits; verify service pricing pages, account eligibility and current offer dimensions before a run.',
        'A Scheduler paid-tier dimension starts after 14 million account-level invocations; using it here is a conservative no-free-allowance estimate, not a claim this account crossed that tier.',
        'Quantities are invented buffers; delivery retries, Lambda replays, index lag, failure inspection, repeated runs and cleanup can differ.',
        'Standard SQS retention has no separate GB-month price; review request, applicable transfer and any chosen KMS costs.',
        'Account, scoped identity, exact Terraform plan, operator, due-backlog procedure, all cost-driver decisions and later billing remain unverified.',
    ]
    return data


def compare_price_evidence(recorded, refreshed):
    """Detect changes in public price evidence; this cannot approve a live run."""
    reasons = []
    if (recorded.get('region'), recorded.get('checked_date')) != (
            'us-east-2', refreshed['checked_date']):
        reasons.append('recorded Region or price-check date differs')
    old_evidence = recorded.get('price_evidence', {})
    new_evidence = refreshed['price_evidence']
    for service, fresh in new_evidence['services'].items():
        old = old_evidence.get('services', {}).get(service, {})
        if any(old.get(key) != fresh[key] for key in ('url', 'publication_date', 'sha256')):
            reasons.append(f'{service}: public offer changed or evidence is missing')
    old_items = {x.get('meter_id'): x for x in recorded.get('items', [])}
    new_items = {x['meter_id']: x for x in refreshed['items']}
    if len(old_items) != len(recorded.get('items', [])) or set(old_items) != set(new_items):
        reasons.append('meter inventory changed or contains duplicates')
    for meter_id, fresh in new_items.items():
        old = old_items.get(meter_id, {})
        if old.get('unit') != fresh['unit'] or old.get('source_url') != fresh['source_url']:
            reasons.append(f'{meter_id}: unit or source changed')
        try:
            same_rate = Decimal(str(old['usd_per_unit'])) == Decimal(str(fresh['usd_per_unit']))
        except (KeyError, ValueError, ArithmeticError):
            same_rate = False
        if not same_rate or old_evidence.get('meters', {}).get(meter_id) != new_evidence['meters'][meter_id]:
            reasons.append(f'{meter_id}: rate or selected price dimension changed')
    return reasons


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument('--out', type=Path)
    destination.add_argument('--check', type=Path)
    args = parser.parse_args()
    offers, fetched = {}, {}
    for service in SERVICES:
        url = f'{indexed.PRICE_BASE}/{service}/current/us-east-2/index.json'
        with urlopen(url, timeout=30) as response:
            raw = response.read()
        offer = json.loads(raw)
        if offer.get('offerCode') != service:
            raise ValueError(f'{service}: unexpected offer code')
        offers[service] = offer
        fetched[service] = {'url': url, 'publication_date': offer['publicationDate'],
                            'sha256': hashlib.sha256(raw).hexdigest()}
    data = build_worksheet(json.loads(TEMPLATE.read_text()), offers, fetched,
                           datetime.now(timezone.utc))
    if args.check:
        reasons = compare_price_evidence(json.loads(args.check.read_text()), data)
        if reasons:
            for reason in reasons:
                print('STALE:', reason)
            print('Refresh and review prices; this check cannot approve an AWS run.')
            return 1
        print('Public offer files and selected scheduled rates match the recorded worksheet today.')
        print('Account, usage, current service pages, plan and cleanup still need independent review.')
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2) + '\n')
    print(f'Wrote pending scheduled teaching scenario: {args.out}')


if __name__ == '__main__':
    main()
