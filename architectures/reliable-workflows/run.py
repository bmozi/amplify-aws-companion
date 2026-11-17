"""Guarded Terraform runner. All credentials stay in memory; no cloud calls for init/validate."""

if __name__ == '__main__':
    raise SystemExit('Inspection-only source: cloud commands are disabled in this companion. See reader/COMMAND-SCOPE.md.')

import argparse
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
INFRA = BASE / 'infra'
PLAN = BASE / 'build/reviewed.tfplan'
RECEIPT = BASE / 'build/plan-review.json'
CONFIG = INFRA / 'run.tfvars.json'
ROOT = BASE.parents[1]
REVIEW_CATEGORIES = ('data_transfer', 'tax', 'shared_resources', 'retries',
                     'repeat_runs', 'retained_storage', 'cleanup_delay')
HOLD_MODES = ('immediate_only', 'scan_due', 'query_due', 'scan_and_query_due')
INDEX_METERS = {
    'due_gsi_writes': 'write request unit',
    'due_gsi_reads': 'read request unit',
    'due_gsi_storage': 'GB-month',
}
SCHEDULE_METERS = {
    'eventbridge_scheduler_invocations': 'request',
    'tick_delivery_sqs_requests': 'request unit',
    'tick_execution_sqs_requests': 'request unit',
    'tick_alarm_months': 'alarm-month',
}
CONTACT_METERS = {
    'contact_scan_reads': 'read request unit',
    'contact_escalation_writes': 'write request unit',
    'contact_lambda_requests': 'request',
    'contact_lambda_compute': 'GB-second',
    'contact_logs_ingest': 'GB ingested',
    'contact_logs_retention': 'GB-month',
}


def positive_review_quantity(value, label):
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ValueError(f'Use a positive reviewed number for {label}') from None
    if not number.is_finite() or number <= 0:
        raise ValueError(f'Use a positive reviewed number for {label}')
    return number


def validate_cost_worksheet(data, config, now):
    """Check a human-completed run review; this cannot prove prices or bound AWS spend."""
    source_date = date.fromisoformat(data['checked_date'])
    age = (now.date() - source_date).days
    if age < 0 or age > 7:
        raise ValueError('Cost worksheet rates must be checked within seven days')
    if data.get('region') != config['region'] or data.get('currency') != 'USD':
        raise ValueError('Cost worksheet currency/Region differs from the Terraform run')
    review = data.get('run_review', {})
    if review.get('status') != 'complete_live_run' or review.get('account_id') != config['account_id']:
        raise ValueError('Complete a cost review for this exact account and live run')
    if review.get('architecture') != 'A02/A03':
        raise ValueError('Cost review must name the A02/A03 architecture')
    hold_mode = review.get('hold_mode')
    if hold_mode not in HOLD_MODES:
        raise ValueError('Select the planned A03 hold mode for this run')
    scheduled = config.get('enable_due_tick_schedule', False)
    if type(scheduled) is not bool:
        raise ValueError('enable_due_tick_schedule must be a JSON boolean')
    expected_mode = 'scheduled_due_tick' if scheduled else 'manual_only'
    if review.get('schedule_mode') != expected_mode:
        raise ValueError(f'Cost worksheet schedule_mode must match Terraform: {expected_mode}')
    if scheduled and hold_mode not in ('query_due', 'scan_and_query_due'):
        raise ValueError('Scheduled due tick requires an indexed-query hold mode')
    contact_enabled = config.get('enable_contact_worklist', False)
    if type(contact_enabled) is not bool:
        raise ValueError('enable_contact_worklist must be a JSON boolean')
    contact_mode = 'manual_review' if contact_enabled else 'disabled'
    if review.get('contact_worklist_mode', 'disabled') != contact_mode:
        raise ValueError(f'Cost worksheet contact_worklist_mode must match Terraform: {contact_mode}')
    if any('core-service subtotal only' in str(limit).lower() for limit in data.get('limitations', [])):
        raise ValueError('Core-service subtotal is still marked incomplete; resolve its limitations')
    exclusions = review.get('cost_drivers', {})
    if set(exclusions) != set(REVIEW_CATEGORIES):
        raise ValueError('Review every named cost driver before a live run')
    for name in REVIEW_CATEGORIES:
        entry = exclusions[name]
        if entry.get('decision') not in ('priced', 'not_applicable') or not str(entry.get('reason', '')).strip():
            raise ValueError(f'Record a priced or not-applicable decision and reason for {name}')
    meters = {item.get('meter_id'): item for item in data.get('items', []) if item.get('meter_id')}
    if len(meters) != sum(bool(item.get('meter_id')) for item in data.get('items', [])):
        raise ValueError('Cost meter IDs must be unique')
    if 'tick_failure_sqs_storage' in meters:
        raise ValueError('Remove the obsolete tick_failure_sqs_storage meter; price SQS requests and applicable transfer instead')
    for meter_id, unit in INDEX_METERS.items():
        item = meters.get(meter_id)
        if not item or item.get('unit') != unit:
            raise ValueError(f'Price the {meter_id} index meter with unit {unit}')
        positive_review_quantity(item.get('usd_per_unit'), f'{meter_id} rate; do not assume a free allowance')
    if hold_mode != 'immediate_only':
        for meter_id in ('due_gsi_writes', 'due_gsi_storage'):
            positive_review_quantity(meters[meter_id].get('quantity'), f'{meter_id} when creating holds')
    if hold_mode in ('query_due', 'scan_and_query_due'):
        positive_review_quantity(meters['due_gsi_reads'].get('quantity'), 'due_gsi_reads for the planned index query')
    if scheduled:
        for meter_id, unit in SCHEDULE_METERS.items():
            item = meters.get(meter_id)
            if not item or item.get('unit') != unit:
                raise ValueError(f'Price the {meter_id} scheduled meter with unit {unit}')
            positive_review_quantity(item.get('usd_per_unit'), f'{meter_id} rate')
            positive_review_quantity(item.get('quantity'), f'{meter_id} quantity')
        if Decimal(str(meters['eventbridge_scheduler_invocations']['quantity'])) < 121:
            raise ValueError('Review at least 121 scheduler invocations for the permitted two-hour window')
        for meter_id in ('lambda_requests', 'lambda_compute', 'table_reads', 'table_writes',
                         'logs_ingest', 'logs_retention'):
            item = meters.get(meter_id)
            if not item:
                raise ValueError(f'Review the {meter_id} downstream meter for scheduled ticks')
            positive_review_quantity(item.get('quantity'), f'{meter_id} scheduled quantity')
            positive_review_quantity(item.get('usd_per_unit'), f'{meter_id} scheduled rate')
        schedule_review = review.get('schedule_review', {})
        for name in ('operator', 'delivery_failure_procedure', 'execution_failure_procedure',
                     'backlog_reconciliation_procedure'):
            if str(schedule_review.get(name, '')).strip().lower() in ('', 'pending', 'tbd'):
                raise ValueError(f'Name the scheduled-run {name}')
        interval = schedule_review.get('inspection_interval_minutes')
        if type(interval) is not int or not 1 <= interval <= 5:
            raise ValueError('Scheduled failure inspection interval must be one to five minutes')
        cleanup = schedule_review.get('cleanup_deadline_epoch')
        if type(cleanup) is not int or not config['expires_at_epoch'] <= cleanup <= config['expires_at_epoch'] + 3600:
            raise ValueError('Scheduled cleanup deadline must be within one hour after lab expiry')
    if contact_enabled:
        for meter_id, unit in CONTACT_METERS.items():
            item = meters.get(meter_id)
            if not item or item.get('unit') != unit:
                raise ValueError(f'Price the {meter_id} contact meter with unit {unit}')
            positive_review_quantity(item.get('usd_per_unit'), f'{meter_id} rate')
            positive_review_quantity(item.get('quantity'), f'{meter_id} quantity')
        contact_review = review.get('contact_review', {})
        for name in ('operator', 'scan_and_cursor_procedure', 'worklist_followup_procedure'):
            if str(contact_review.get(name, '')).strip().lower() in ('', 'pending', 'tbd'):
                raise ValueError(f'Name the contact-worklist {name}')
        for name in ('planned_due_checks', 'planned_worklist_reads'):
            positive_review_quantity(contact_review.get(name), name)
        planned_invocations = sum(Decimal(str(contact_review[name])) for name in
                                  ('planned_due_checks', 'planned_worklist_reads'))
        if Decimal(str(meters['contact_lambda_requests']['quantity'])) < planned_invocations:
            raise ValueError('contact_lambda_requests must cover planned check and worklist invocations')
        cleanup = contact_review.get('cleanup_deadline_epoch')
        if type(cleanup) is not int or not config['expires_at_epoch'] <= cleanup <= config['expires_at_epoch'] + 3600:
            raise ValueError('Contact-worklist cleanup deadline must be within one hour after lab expiry')
    estimator_path = ROOT / 'scripts/estimate-lab-cost.py'
    spec = importlib.util.spec_from_file_location('lab_cost_estimator', estimator_path)
    estimator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(estimator)
    calculated = Decimal(estimator.estimate(data)['with_contingency_usd'])
    entered = Decimal(str(config['estimated_run_cost_usd']))
    if not entered.is_finite() or entered < calculated:
        raise ValueError('Terraform estimate is below the reviewed worksheet total')
    return calculated


def require_deployment_role(identity, account_id):
    """Require the intended account and an assumed role; this does not audit its policy."""
    if identity.get('Account') != account_id:
        raise ValueError('Wrong account; stopped')
    arn = identity.get('Arn', '')
    if not re.fullmatch(r'arn:aws(?:-us-gov|-cn)?:sts::' + re.escape(account_id)
                        + r':assumed-role/[^/]+/[^/]+', arn):
        raise ValueError('Plan/apply requires a temporary assumed-role session; root and IAM-user sessions are rejected')


def validate_live_parameters(config, now_epoch):
    seconds = config['expires_at_epoch'] - now_epoch
    if not 0 < seconds <= 7200:
        raise ValueError('Lab expiry must be in the next two hours')
    if not 0 < config['estimated_run_cost_usd'] <= config['approved_run_budget_usd'] <= 5:
        raise ValueError('Estimate must be positive and within a reviewed run budget of at most USD 5')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['init', 'validate', 'plan', 'apply', 'output', 'destroy', 'state'])
    parser.add_argument('--profile', help='Explicit AWS CLI profile; no credential literals')
    parser.add_argument('--cost-worksheet', type=Path,
                        help='Private, completed whole-run worksheet; required for plan/apply')
    args = parser.parse_args()
    cmd = ['terraform', f'-chdir={INFRA}']
    if args.action in ['init', 'validate']:
        return subprocess.call(cmd + [args.action, '-no-color'])
    if not args.profile:
        parser.error('--profile is required')
    config = json.loads(CONFIG.read_text())
    worksheet_bytes = None
    if args.action in ['plan', 'apply']:
        if args.cost_worksheet is None:
            parser.error('--cost-worksheet is required for plan/apply')
        worksheet_bytes = args.cost_worksheet.read_bytes()
        validate_live_parameters(config, time.time())
        validate_cost_worksheet(json.loads(worksheet_bytes), config, datetime.now(timezone.utc))
    identity = json.loads(subprocess.check_output(['aws', 'sts', 'get-caller-identity', '--profile', args.profile, '--output', 'json']))
    if identity['Account'] != config['account_id']:
        raise RuntimeError('Wrong account; stopped')
    if args.action in ['plan', 'apply']:
        require_deployment_role(identity, config['account_id'])
        subprocess.run([sys.executable, str(BASE.parents[1] / 'scripts/credit-check.py'),
                        '--profile', args.profile, '--account-id', config['account_id'],
                        '--estimated-run-usd', str(config['estimated_run_cost_usd']),
                        '--planned-end-epoch', str(config['expires_at_epoch']),
                        '--output-dir', str(BASE.parents[1] / 'evidence/billing')], check=True)
    credentials = json.loads(subprocess.check_output(['aws', 'configure', 'export-credentials', '--profile', args.profile, '--format', 'process']))
    env = os.environ.copy()
    for name in ['AWS_PROFILE', 'AWS_DEFAULT_PROFILE', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN']:
        env.pop(name, None)
    env.update(AWS_ACCESS_KEY_ID=credentials['AccessKeyId'], AWS_SECRET_ACCESS_KEY=credentials['SecretAccessKey'],
               AWS_SESSION_TOKEN=credentials['SessionToken'], AWS_REGION=config['region'])
    BASE.joinpath('build').mkdir(exist_ok=True)
    source = CONFIG.read_bytes()
    for path in sorted(list((BASE / 'src').glob('*.py')) + list(INFRA.glob('*.tf'))):
        source += str(path.relative_to(BASE)).encode() + path.read_bytes()
    digest = hashlib.sha256(source).hexdigest()
    if args.action == 'plan':
        subprocess.run(cmd + ['plan', '-input=false', '-no-color', f'-var-file={CONFIG}', f'-out={PLAN}'], env=env, check=True)
        RECEIPT.write_text(json.dumps({'config_sha256': digest, 'cost_worksheet_sha256': hashlib.sha256(worksheet_bytes).hexdigest(),
                                       'created_epoch': time.time(), 'plan_sha256': hashlib.sha256(PLAN.read_bytes()).hexdigest()}))
    elif args.action == 'apply':
        receipt = json.loads(RECEIPT.read_text())
        if (digest != receipt['config_sha256'] or hashlib.sha256(worksheet_bytes).hexdigest() != receipt.get('cost_worksheet_sha256')
                or time.time() - receipt['created_epoch'] > 900
                or hashlib.sha256(PLAN.read_bytes()).hexdigest() != receipt['plan_sha256']):
            raise ValueError('Plan changed or older than 15 minutes. Run plan and review again.')
        subprocess.run(cmd + ['apply', '-input=false', '-no-color', str(PLAN)], env=env, check=True)
    elif args.action == 'destroy':
        # Terraform asks for confirmation; expired labs must remain destroyable.
        subprocess.run(cmd + ['destroy', '-no-color', f'-var-file={CONFIG}'], env=env, check=True)
    elif args.action == 'output':
        subprocess.run(cmd + ['output', '-json', 'lab'], env=env, check=True)
    else:
        subprocess.run(cmd + ['state', 'list'], env=env, check=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
