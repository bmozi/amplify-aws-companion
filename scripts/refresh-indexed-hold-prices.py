"""Price the A02/A03 indexed-hold teaching scenario from AWS public Ohio offer files.

This reads public list prices without account credentials. It never completes a
live-run review or subtracts credits/free allowances. The operator must still
check the AWS pricing pages, actual account, plan, workload, cleanup and bill.
"""

import argparse
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen


BASE = Path(__file__).resolve().parents[1]
TEMPLATE = BASE / 'examples/costs/worksheet.json'
PRICE_BASE = 'https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws'
SERVICE_PAGES = {
    'AWSLambda': 'https://aws.amazon.com/lambda/pricing/',
    'AmazonDynamoDB': 'https://aws.amazon.com/dynamodb/pricing/',
    'AWSQueueService': 'https://aws.amazon.com/sqs/pricing/',
    'AmazonCloudWatch': 'https://aws.amazon.com/cloudwatch/pricing/',
}

# Exact Ohio paid-tier SKUs. The unit and start range are checked below so a
# changed offer cannot silently turn a free tier or different product into a rate.
RATES = {
    'lambda_requests': ('AWSLambda', 'ZEA64MMVK5QRB5TC', 'USE2-Request', 'Request', '0', 'request'),
    'lambda_compute': ('AWSLambda', '3BYZH4NKJN8TJUQ6', 'USE2-Lambda-GB-Second', 'Lambda-GB-Second', '0', 'GB-second'),
    'table_writes': ('AmazonDynamoDB', 'GGQSXTNTRBHRVS56', 'USE2-WriteRequestUnits', 'WriteRequestUnits', '0', 'write request unit'),
    'table_reads': ('AmazonDynamoDB', 'SGMZJPDKSWXTY4VE', 'USE2-ReadRequestUnits', 'ReadRequestUnits', '0', 'read request unit'),
    'table_storage': ('AmazonDynamoDB', 'GAHPNMT39TQ47AGG', 'USE2-TimedStorage-ByteHrs', 'GB-Mo', '25', 'GB-month'),
    'due_gsi_writes': ('AmazonDynamoDB', 'GGQSXTNTRBHRVS56', 'USE2-WriteRequestUnits', 'WriteRequestUnits', '0', 'write request unit'),
    'due_gsi_reads': ('AmazonDynamoDB', 'SGMZJPDKSWXTY4VE', 'USE2-ReadRequestUnits', 'ReadRequestUnits', '0', 'read request unit'),
    'due_gsi_storage': ('AmazonDynamoDB', 'GAHPNMT39TQ47AGG', 'USE2-TimedStorage-ByteHrs', 'GB-Mo', '25', 'GB-month'),
    'sqs_standard_requests': ('AWSQueueService', '9C8YFGPNBKF9HP9A', 'USE2-Requests-Tier1', 'Requests', '0', 'request unit'),
    'logs_ingest': ('AmazonCloudWatch', '5T6Z6V26DSR7SZ49', 'USE2-DataProcessing-Bytes', 'GB', '0', 'GB ingested'),
    'logs_retention': ('AmazonCloudWatch', 'X7X4WD4A95NDR9U5', 'USE2-TimedStorage-ByteHrs', 'GB-Mo', '0', 'GB-month'),
}


def selected_rate(offer, meter_id):
    service, sku, usage_type, aws_unit, start, worksheet_unit = RATES[meter_id]
    product = offer['products'][sku]
    attributes = product['attributes']
    if attributes.get('regionCode') != 'us-east-2' or attributes.get('usagetype') != usage_type:
        raise ValueError(f'{meter_id}: Ohio product/usage type changed')
    dimensions = [dimension for term in offer['terms']['OnDemand'][sku].values()
                  for dimension in term['priceDimensions'].values()
                  if dimension['unit'] == aws_unit and dimension['beginRange'] == start]
    if len(dimensions) != 1:
        raise ValueError(f'{meter_id}: expected exactly one paid price dimension')
    dimension = dimensions[0]
    rate = Decimal(dimension['pricePerUnit']['USD'])
    if not rate.is_finite() or rate <= 0:
        raise ValueError(f'{meter_id}: paid rate must be positive')
    return str(rate), {'service': service, 'sku': sku, 'usage_type': usage_type,
                       'aws_unit': aws_unit, 'begin_range': start,
                       'price_dimension': dimension['rateCode'],
                       'description': dimension['description'],
                       'worksheet_unit': worksheet_unit}


def build_worksheet(template, offers, fetched, now):
    data = json.loads(json.dumps(template))
    meter_ids = [item.get('meter_id') for item in data['items']]
    if len(meter_ids) != len(set(meter_ids)) or set(meter_ids) != set(RATES):
        raise ValueError('Worksheet meters must match the exact priced inventory')
    data['checked_date'] = now.date().isoformat()
    data['run_review']['status'] = 'pending'
    data['run_review']['account_id'] = 'REPLACE_WITH_CONFIRMED_ACCOUNT'
    data['run_review']['hold_mode'] = 'scan_and_query_due'
    data['run_review']['schedule_mode'] = 'manual_only'
    for review in data['run_review']['cost_drivers'].values():
        review.update(decision='pending', reason='')
    data['scenario'] = {
        'kind': 'illustrative_not_authorized', 'planned_handler_window_hours': 2,
        'hold_count': 10, 'discovery': 'manual scan and index-query passes, including retries',
        'sqs_requests': '400000 stress assumption including quiet polling, not a service limit',
        'lambda_compute': '500 invocations times 10 seconds times 0.125 GiB = 625 GB-seconds',
        'storage': 'GB-month quantities are planning buffers for table, index and logs; cleanup timing remains unresolved',
    }
    evidence = {}
    for item in data['items']:
        meter_id = item.get('meter_id')
        if meter_id not in RATES:
            raise ValueError(f'Unmapped worksheet meter: {meter_id}')
        service, _, _, _, _, expected_unit = RATES[meter_id]
        if item['unit'] != expected_unit:
            raise ValueError(f'{meter_id}: worksheet unit changed')
        item['usd_per_unit'], evidence[meter_id] = selected_rate(offers[service], meter_id)
        item['source_url'] = fetched[service]['url']
    next(item for item in data['items'] if item['meter_id'] == 'sqs_standard_requests')['quantity'] = 400000
    data['price_evidence'] = {'checked_at_utc': now.isoformat(), 'source': 'AWS public Price List Bulk offer files',
                              'services': fetched, 'meters': evidence,
                              'service_pricing_pages': SERVICE_PAGES}
    data['limitations'] = [
        'Illustrative stress quantities and public paid-tier list prices, not a complete reviewed live-run estimate or spending cap.',
        'Do not mark complete_live_run without the exact account, plan, Terraform plan, selected actions, cleanup owner and deadline, and all named cost drivers.',
        'No Free Tier or credits subtracted; AWS says service pricing pages prevail if an offer file differs.',
        'The index write/read/storage rows are additional to the base-table rows; item size, pagination, retries and backfill need selected-run review.',
        'The 400000 SQS requests are a stress assumption, not a measured count or an AWS maximum.',
        'Rates and account eligibility must be refreshed before deployment; actual usage and billing require later reconciliation.',
    ]
    return data


def compare_price_evidence(recorded, refreshed, today):
    """Find stale public-price evidence; this cannot approve a live run."""
    reasons = []
    if recorded.get('region') != 'us-east-2' or recorded.get('checked_date') != today:
        reasons.append('recorded region or price-check date is not current Ohio')
    recorded_evidence = recorded.get('price_evidence', {})
    refreshed_evidence = refreshed['price_evidence']
    for service, fresh in refreshed_evidence['services'].items():
        old = recorded_evidence.get('services', {}).get(service, {})
        if any(old.get(key) != fresh[key] for key in ('url', 'publication_date', 'sha256')):
            reasons.append(f'{service}: public offer changed or its evidence is missing')
    old_items = {item.get('meter_id'): item for item in recorded.get('items', [])}
    if len(old_items) != len(recorded.get('items', [])) or set(old_items) != set(RATES):
        reasons.append('recorded meter inventory changed or contains duplicates')
    for fresh in refreshed['items']:
        meter_id = fresh['meter_id']
        old = old_items.get(meter_id, {})
        if old.get('unit') != fresh['unit'] or old.get('source_url') != fresh['source_url']:
            reasons.append(f'{meter_id}: unit or source changed')
        try:
            same_rate = Decimal(str(old['usd_per_unit'])) == Decimal(str(fresh['usd_per_unit']))
        except (KeyError, ValueError, ArithmeticError):
            same_rate = False
        if not same_rate:
            reasons.append(f'{meter_id}: recorded rate changed or is missing')
        if recorded_evidence.get('meters', {}).get(meter_id) != refreshed_evidence['meters'][meter_id]:
            reasons.append(f'{meter_id}: selected price dimension changed or evidence is missing')
    return reasons


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument('--out', type=Path, help='Write an illustrative priced JSON worksheet')
    destination.add_argument('--check', type=Path, help='Compare a recorded worksheet with current public offers without writing it')
    args = parser.parse_args()
    template = json.loads(TEMPLATE.read_text())
    offers, fetched = {}, {}
    for service in SERVICE_PAGES:
        url = f'{PRICE_BASE}/{service}/current/us-east-2/index.json'
        with urlopen(url, timeout=30) as response:
            raw = response.read()
        offer = json.loads(raw)
        if offer.get('offerCode') != service:
            raise ValueError(f'{service}: unexpected offer code')
        offers[service] = offer
        fetched[service] = {'url': url, 'publication_date': offer['publicationDate'],
                            'sha256': hashlib.sha256(raw).hexdigest()}
    data = build_worksheet(template, offers, fetched, datetime.now(timezone.utc))
    if args.check:
        reasons = compare_price_evidence(json.loads(args.check.read_text()), data, data['checked_date'])
        if reasons:
            for reason in reasons:
                print('STALE:', reason)
            print('Refresh and review prices; a rate check cannot approve an AWS run.')
            return 1
        print('Public offer files and all selected rates match the recorded worksheet today.')
        print('This price check does not establish live-run readiness; verify service pages, account, workload, plan and cleanup separately.')
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2) + '\n')
    print(f'Wrote pending scenario: {args.out}')


if __name__ == '__main__':
    raise SystemExit(main())
