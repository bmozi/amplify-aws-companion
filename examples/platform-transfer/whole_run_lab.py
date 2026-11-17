"""Fictional same-outcome platform estimate. No AWS calls or current prices."""

import argparse
from decimal import Decimal, InvalidOperation
import json


# These deliberately invented dollars-per-unit values are arithmetic fixtures,
# not AWS prices. Replace all of them with dated regional quotes before a live plan.
RATES = {
    'alb_hour': '0.03', 'database_hour': '0.10', 'egress_gb': '0.20',
    'log_gb': '0.12', 'backup_gb': '0.12',
    'ec2_instance_hour': '0.06', 'ec2_ebs_gb': '0.20',
    'fargate_vcpu_hour': '0.05', 'fargate_memory_gb_hour': '0.0125',
    'image_storage_gb': '0.12',
    'eks_cluster_hour': '0.12', 'eks_node_hour': '0.05',
    'eks_auto_node_hour': '0.02', 'eks_storage_gb': '0.20',
}

SHARED = ('alb_hour', 'database_hour', 'egress_gb', 'log_gb', 'backup_gb')
SPECIFIC = {
    'ec2_asg': ('ec2_instance_hour', 'ec2_ebs_gb'),
    'ecs_fargate': ('fargate_vcpu_hour', 'fargate_memory_gb_hour', 'image_storage_gb'),
    'eks_auto': ('eks_cluster_hour', 'eks_node_hour', 'eks_auto_node_hour',
                 'eks_storage_gb'),
}


def quantities(platform, hours):
    if platform not in SPECIFIC or type(hours) is not int or hours <= 0:
        raise ValueError('Choose a known platform and positive whole-run hours')
    common = {'alb_hour': hours, 'database_hour': hours,
              'egress_gb': 1, 'log_gb': 1, 'backup_gb': 1}
    extras = {
        # One temporary third worker runs for three/four hours during replacement.
        'ec2_asg': {'ec2_instance_hour': 2 * hours + 3, 'ec2_ebs_gb': 1},
        'ecs_fargate': {'fargate_vcpu_hour': 2 * hours + 4,
                        'fargate_memory_gb_hour': 2 * (2 * hours + 4),
                        'image_storage_gb': 1},
        'eks_auto': {'eks_cluster_hour': hours, 'eks_node_hour': 2 * hours + 4,
                     'eks_auto_node_hour': 2 * hours + 4, 'eks_storage_gb': 1},
    }
    return common | extras[platform]


def estimate(platform, hours, rates=RATES, limit_usd='5'):
    usage = quantities(platform, hours)
    try:
        limit = Decimal(limit_usd)
    except (TypeError, ValueError, InvalidOperation):
        raise ValueError('Limit must be a positive finite decimal') from None
    if not limit.is_finite() or limit <= 0:
        raise ValueError('Limit must be a positive finite decimal')
    required = set(SHARED + SPECIFIC[platform])
    if set(usage) != required or set(rates) != set(RATES):
        raise ValueError('A required meter is missing or an unreviewed meter was added')
    lines = {}
    for meter in sorted(required):
        try:
            rate = Decimal(rates[meter])
        except (KeyError, TypeError, ValueError, InvalidOperation):
            raise ValueError('Every meter needs a decimal rate') from None
        if not rate.is_finite() or rate < 0:
            raise ValueError('Rates must be finite and nonnegative')
        lines[meter] = rate * usage[meter]
    subtotal = sum(lines.values(), Decimal('0'))
    with_contingency = subtotal * Decimal('1.25')
    return {'platform': platform, 'hours': hours,
            'lines_usd': {key: str(value) for key, value in lines.items()},
            'subtotal_usd': str(subtotal),
            'with_25_percent_contingency_usd': str(with_contingency),
            'chosen_fixture_limit_usd': str(limit),
            'within_chosen_fixture_limit': with_contingency <= limit,
            'scope': 'fictional prices and usage; not a current AWS quote, credit check or deployment approval'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hours', type=int, default=12)
    parser.add_argument('--limit-usd', default='5',
                        help='positive fictional whole-run limit (default: 5)')
    args = parser.parse_args()
    reports = [estimate(platform, args.hours, limit_usd=args.limit_usd)
               for platform in SPECIFIC]
    print(json.dumps({'same_customer_checks': ['authorized submit and read',
                                               'wrong-customer denial',
                                               'worker replacement', 'database outage and recovery'],
                      'reports': reports,
                      'next_gate': 'Verify actual requirements, regional prices, applicable credits and reserve before any AWS run'},
                     indent=2))


if __name__ == '__main__':
    main()
