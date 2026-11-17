"""Compare two fictional source populations before reporting a customer rate.

This fixture does not authenticate either source, infer a missing job's outcome,
or read AWS telemetry. It deliberately preserves an unknown instead of treating
absence from an operations export as failure or success.
"""

import json
from pathlib import Path

from cohort_lab import classify


HERE = Path(__file__).resolve().parent


def keyed(rows, label):
    if not isinstance(rows, list):
        raise ValueError(f'{label} must be a list')
    result = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get('id'), str) or not row['id']:
            raise ValueError(f'{label} contains an invalid job identity')
        if row['id'] in result:
            raise ValueError(f'{label} contains a duplicate job identity')
        if type(row.get('accepted')) is not int or row['accepted'] < 0:
            raise ValueError(f'{label} contains an invalid acceptance time')
        result[row['id']] = row
    return result


def compare(intake, operations, *, now, deadline):
    if type(now) is not int or now < 0 or type(deadline) is not int or deadline <= 0:
        raise ValueError('Clock and deadline must be valid whole seconds')
    registered = keyed(intake, 'Intake register')
    observed = keyed(operations, 'Operations export')
    if not registered:
        return {'decision': 'hold_source_reconciliation', 'rate': None,
                'reason': 'The supplied intake register has no accepted population'}
    if any(row['accepted'] > now for row in registered.values()):
        raise ValueError('Intake register contains a future acceptance for this snapshot')
    if any(row['accepted'] > now for row in observed.values()):
        raise ValueError('Operations export contains a future acceptance for this snapshot')
    unknown = sorted(registered.keys() - observed.keys())
    extra = sorted(observed.keys() - registered.keys())
    mismatch = sorted(key for key in registered.keys() & observed.keys()
                      if registered[key]['accepted'] != observed[key]['accepted'])
    missing_outcome_fields = sorted(key for key, row in observed.items()
                                    if 'completed_at_followup' not in row)
    if extra or mismatch or missing_outcome_fields:
        return {'decision': 'hold_source_reconciliation', 'missing_from_operations': unknown,
                'unexpected_in_operations': extra, 'acceptance_time_mismatch': mismatch,
                'missing_outcome_fields': missing_outcome_fields,
                'rate': None, 'reason': 'Source identities, times, or outcome fields conflict'}
    known = classify(operations, now=now, deadline=deadline,
                     completion_field='completed_at_followup',
                     expected_ids=list(observed))
    due_unknown = sorted(key for key in unknown
                         if registered[key]['accepted'] + deadline <= now)
    if unknown:
        return {
            'decision': 'hold_customer_rate',
            'accepted_in_register': len(registered),
            'mature_in_register': len(known['mature_ids']) + len(due_unknown),
            'known_on_time': known['on_time_over_mature'][0],
            'known_missed_ids': known['missed_promise_ids'],
            'known_unfinished_ids': known['unfinished_ids'],
            'missing_from_operations': unknown,
            'due_with_unknown_outcome': due_unknown,
            'rate': None,
            'reason': 'An accepted job is absent from outcome evidence',
        }
    return {
        'decision': 'rate_for_supplied_population',
        'accepted_in_register': len(registered),
        'mature_in_register': len(known['mature_ids']),
        'known_on_time': known['on_time_over_mature'][0],
        'known_missed_ids': known['missed_promise_ids'],
        'known_unfinished_ids': known['unfinished_ids'],
        'missing_from_operations': [],
        'due_with_unknown_outcome': [],
        'rate': known['on_time_over_mature'],
        'reason': 'Both supplied source populations match; real source authority is unverified',
    }


def run():
    register = json.loads((HERE / 'intake-completeness.json').read_text())
    incident = json.loads((HERE / 'incident.json').read_text())
    if register['as_of_second'] != incident['incident_snapshot_at']:
        raise ValueError('Fixture sources use different snapshot times')
    result = compare(register['accepted'], incident['jobs'], now=register['as_of_second'],
                     deadline=incident['completion_deadline_seconds'])
    print(json.dumps(result, indent=2))
    return result


if __name__ == '__main__':
    run()
