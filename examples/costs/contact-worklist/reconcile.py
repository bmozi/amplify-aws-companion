"""Reconcile synthetic contact-handler capacity receipts; never calls AWS."""

import argparse
from collections import OrderedDict
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re


OPERATIONS = {
    'check_due': ('contact_due_scan', 'contact_due_transaction'),
    'read_open': ('contact_worklist_scan', 'contact_worklist_contact_read',
                  'contact_worklist_request_read'),
}
FIELDS = ('total_capacity_units', 'read_capacity_units', 'write_capacity_units')


def amount(value, field):
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValueError(f'{field} must be a nonnegative finite decimal')
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f'{field} must be a nonnegative finite decimal') from exc
    if not result.is_finite() or result < 0:
        raise ValueError(f'{field} must be a nonnegative finite decimal')
    return result


def reconcile(book):
    if not isinstance(book, dict) or book.get('schema_version') != 1:
        raise ValueError('Expected schema_version 1 receipt book')
    invocations = book.get('invocations')
    if not isinstance(invocations, list) or not invocations:
        raise ValueError('Supply at least one invocation')

    passes = OrderedDict()
    seen = set()
    sums = {field: Decimal(0) for field in FIELDS}
    counts = {'reported': 0, 'unreported': 0, 'canceled': 0,
              'failed_without_response': 0}
    for invocation in invocations:
        if not isinstance(invocation, dict):
            raise ValueError('Each invocation must be an object')
        call_id = invocation.get('invocation_id')
        pass_id = invocation.get('pass_id')
        action = invocation.get('action')
        if not isinstance(call_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', call_id) or call_id in seen:
            raise ValueError('Invocation IDs must be unique nonempty strings')
        seen.add(call_id)
        if not isinstance(pass_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', pass_id) or action not in OPERATIONS:
            raise ValueError('Each invocation needs a pass_id and known action')
        if pass_id not in passes:
            passes[pass_id] = {'action': action, 'pages': 0, 'next_cursor': None,
                               'finished': False, 'failed': False}
        state = passes[pass_id]
        if state['action'] != action or state['finished'] or state['failed']:
            raise ValueError('A pass cannot mix actions or continue after ending')
        if invocation.get('requested_cursor') != state['next_cursor']:
            raise ValueError('Requested cursor does not follow previous page')

        if invocation.get('status') == 'failed_no_response':
            if 'response' in invocation:
                raise ValueError('A failed-no-response call cannot carry a response')
            state['failed'] = True
            counts['failed_without_response'] += 1
            continue
        if invocation.get('status', 'succeeded') != 'succeeded':
            raise ValueError('Unknown invocation status')
        response = invocation.get('response')
        if not isinstance(response, dict):
            raise ValueError('Successful invocation needs its response')
        trace = response.get('capacity_observations')
        if not isinstance(trace, list) or not trace:
            raise ValueError('Successful response needs capacity observations')
        if not isinstance(trace[0], dict) or trace[0].get('operation') != OPERATIONS[action][0]:
            raise ValueError('First observation must be the action scan')
        for row in trace:
            if not isinstance(row, dict) or set(row) - {
                    'operation', 'outcome', 'reported', *FIELDS}:
                raise ValueError('Observation has unknown fields')
            if row.get('operation') not in OPERATIONS[action]:
                raise ValueError('Observation operation does not match action')
            if row.get('outcome') not in {'succeeded', 'canceled'}:
                raise ValueError('Observation needs succeeded or canceled outcome')
            if type(row.get('reported')) is not bool:
                raise ValueError('Observation needs a reported boolean')
            available = [field for field in FIELDS if field in row]
            if row['reported'] != bool(available):
                raise ValueError('Reported flag must match numeric fields')
            if row['reported']:
                counts['reported'] += 1
                for field in available:
                    sums[field] += amount(row[field], field)
            else:
                counts['unreported'] += 1
            if row['outcome'] == 'canceled':
                counts['canceled'] += 1
        cursor = response.get('next_cursor')
        if cursor is not None and (not isinstance(cursor, dict) or not cursor):
            raise ValueError('Next cursor must be a nonempty object or absent')
        state['next_cursor'] = cursor
        state['pages'] += 1
        state['finished'] = cursor is None

    pass_summary = [{
        'pass_id': key, 'action': state['action'], 'pages_with_responses': state['pages'],
        'complete_page_chain': state['finished'],
        'failed_without_response': state['failed'],
    } for key, state in passes.items()]
    page_complete = all(item['complete_page_chain'] for item in pass_summary)
    # Total is its own returned field and can overlap read/write; never add it
    # to those fields as though it were extra consumption.
    return {
        'kind': 'synthetic-handler-receipt-reconciliation-not-a-bill',
        'invocations_seen': len(invocations), 'passes': pass_summary,
        'supplied_page_chains_complete': page_complete,
        'reported_operations': counts['reported'],
        'unreported_operations': counts['unreported'],
        'canceled_operations': counts['canceled'],
        'failed_invocations_without_response': counts['failed_without_response'],
        'observed_total_capacity_units': str(sums['total_capacity_units']),
        'observed_read_capacity_units': str(sums['read_capacity_units']),
        'observed_write_capacity_units': str(sums['write_capacity_units']),
        'supplied_numeric_observations_complete': page_complete and not (
            counts['unreported'] or counts['failed_without_response']),
        'bill_reconciled': False,
        'approved_to_deploy': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('receipts', type=Path)
    args = parser.parse_args()
    print(json.dumps(reconcile(json.loads(args.receipts.read_text())), indent=2))


if __name__ == '__main__':
    main()
