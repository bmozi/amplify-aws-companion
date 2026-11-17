"""Check reported pre-credit monthly headroom before a reviewed Amplify run.

DescribeBudget does not timestamp CalculatedSpend; this is no spending cap.
"""
import argparse
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
import subprocess


def money(value):
    amount = Decimal(str(value))
    if not amount.is_finite() or amount < 0:
        raise ValueError('Expected a finite nonnegative USD amount')
    return amount


def assess(budget, estimate, buffer, now):
    estimate, buffer = money(estimate), money(buffer)
    if estimate == 0:
        raise ValueError('A publication run needs a positive estimate')
    if estimate > Decimal('5'):
        raise ValueError('Estimated run exceeds the USD 5 run limit')
    if buffer < Decimal('5'):
        raise ValueError('Safety buffer must be at least USD 5')
    if budget.get('BudgetType') != 'COST' or budget.get('TimeUnit') != 'MONTHLY':
        raise ValueError('Expected the reviewed monthly cost budget')
    if budget.get('CostTypes', {}).get('IncludeCredit') is not False:
        raise ValueError('Budget must exclude credits to show gross usage')
    if budget.get('CostTypes', {}).get('IncludeRefund') is not False:
        raise ValueError('Budget must exclude refunds from the pre-credit view')
    if budget.get('CostFilters') or budget.get('FilterExpression') or budget.get('BillingViewArn'):
        raise ValueError('Expected an unfiltered account-wide budget')
    if budget.get('HealthStatus', {}).get('Status') == 'UNHEALTHY':
        raise ValueError('Budget billing view is unhealthy')
    limit = budget.get('BudgetLimit', {})
    actual = budget.get('CalculatedSpend', {}).get('ActualSpend', {})
    if limit.get('Unit') != 'USD' or actual.get('Unit') != 'USD':
        raise ValueError('Budget needs USD limit and actual cost')
    limit_usd, actual_usd = money(limit['Amount']), money(actual['Amount'])
    configured = budget.get('LastUpdatedTime')
    configured = datetime.fromisoformat(configured.replace('Z', '+00:00')) if configured else None
    if configured and (configured.tzinfo is None or configured > now + timedelta(minutes=5)):
        raise ValueError('Budget configuration timestamp is invalid or future-dated')
    start = datetime.fromisoformat(budget['TimePeriod']['Start'].replace('Z', '+00:00'))
    end_value = budget['TimePeriod'].get('End')
    end = datetime.fromisoformat(end_value.replace('Z', '+00:00')) if end_value else None
    if start.tzinfo is None or start > now or (end and (end.tzinfo is None or now >= end)):
        raise ValueError('Budget period does not cover this run')
    headroom = limit_usd - actual_usd - estimate - buffer
    return {
        'decision': 'within_reported_headroom' if headroom >= 0 else 'review_required',
        'limit_usd': str(limit_usd), 'reported_pre_credit_actual_usd': str(actual_usd),
        'estimated_run_usd': str(estimate), 'safety_buffer_usd': str(buffer),
        'headroom_after_run_and_buffer_usd': str(headroom),
        'budget_configuration_last_updated': configured.isoformat() if configured else None,
        'actual_spend_refresh_time': 'not exposed by DescribeBudget',
        'limits': 'Reported budget arithmetic only; actual spend can lag and this is no hard cap',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--account-id', required=True)
    parser.add_argument('--budget-name', required=True)
    parser.add_argument('--estimated-run-usd', required=True, type=Decimal)
    parser.add_argument('--safety-buffer-usd', type=Decimal, default=Decimal('5'))
    parser.add_argument('--profile', help='Named local profile; omit for GitHub OIDC')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()
    common = ['--region', 'us-east-1', '--output', 'json']
    if args.profile:
        common = ['--profile', args.profile, *common]
    identity = json.loads(subprocess.check_output(['aws', 'sts', 'get-caller-identity', *common]))
    if identity['Account'] != args.account_id:
        raise ValueError('Wrong AWS account; publication stopped')
    response = json.loads(subprocess.check_output([
        'aws', 'budgets', 'describe-budget', '--account-id', args.account_id,
        '--budget-name', args.budget_name, *common,
    ]))
    budget = response['Budget']
    if budget.get('BudgetName') != args.budget_name:
        raise ValueError('Wrong budget; publication stopped')
    result = assess(budget, args.estimated_run_usd, args.safety_buffer_usd,
                    datetime.now(timezone.utc))
    print(result['decision'] if args.quiet else json.dumps(result, indent=2))
    if result['decision'] != 'within_reported_headroom':
        raise SystemExit(2)


if __name__ == '__main__':
    main()
