"""Calculate a reviewed usage estimate using explicit prices; does not read or control AWS billing."""
import argparse
from decimal import Decimal
from datetime import date
import json
from pathlib import Path
import sys


def review_signal(data):
    """Expose worksheet declarations without treating them as verified authority."""
    review = data.get('run_review')
    if not isinstance(review, dict):
        return {'worksheet_status': 'missing', 'pending_cost_drivers': [],
                'deployment_permission': 'not_granted_by_estimator'}
    drivers = review.get('cost_drivers')
    pending = sorted(name for name, entry in (drivers or {}).items()
                     if not isinstance(entry, dict) or
                     entry.get('decision') not in ('priced', 'not_applicable') or
                     not str(entry.get('reason', '')).strip())
    account = str(review.get('account_id', ''))
    return {
        'worksheet_status': review.get('status', 'missing'),
        'account_field_filled': bool(account and not account.startswith('REPLACE_')),
        'cost_driver_review_present': isinstance(drivers, dict) and bool(drivers),
        'pending_cost_drivers': pending,
        'deployment_permission': 'not_granted_by_estimator',
    }


def estimate(data):
    if data.get('currency') != 'USD' or not data.get('region') or not data.get('checked_date'):
        raise ValueError('Supply USD currency, region and price-check date')
    date.fromisoformat(data['checked_date'])
    total = Decimal('0')
    details = []
    if not data.get('items'):
        raise ValueError('At least one cost item is required')
    for item in data['items']:
        if item.get('usd_per_unit') is None or not item.get('source_url'):
            raise ValueError(f"Missing verified price/source: {item['name']}")
        quantity, rate = Decimal(str(item['quantity'])), Decimal(str(item['usd_per_unit']))
        if not quantity.is_finite() or not rate.is_finite() or quantity < 0 or rate < 0:
            raise ValueError('Quantities and prices must be finite and nonnegative')
        cost = quantity * rate
        details.append({'name': item['name'], 'usd': str(cost), 'unit': item['unit']})
        total += cost
    contingency = Decimal(str(data['contingency_percent']))
    if not contingency.is_finite() or not 0 <= contingency <= 1000:
        raise ValueError('Supply a finite contingency percentage between 0 and 1000')
    return {'kind': 'usage-estimate-not-billing-cap', 'currency': 'USD', 'items': details,
            'subtotal_usd': str(total), 'with_contingency_usd': str(total * (1 + contingency / 100)),
            'review_signal': review_signal(data), 'limitations': data.get('limitations', [])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('worksheet', type=Path)
    args = parser.parse_args()
    print(json.dumps(estimate(json.loads(args.worksheet.read_text())), indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
