"""Reclassify a fictional incident by customer promise and exact job identity.

The local timeline is retrospective. It does not ingest AWS telemetry or score
the operator's causal explanation, mitigation, or customer communication.
"""

from copy import deepcopy
import json
from pathlib import Path


FIXTURE = Path(__file__).with_name('incident.json')


def classify(jobs, *, now, deadline, completion_field, expected_ids):
    """Return mutually exclusive identities and two distinct populations.

    A completion later than ``now`` is not yet observed at that snapshot. The
    expected IDs are a supplied teaching control, not a real source inventory.
    """
    if type(now) is not int or now < 0 or type(deadline) is not int or deadline <= 0:
        raise ValueError('The clock and positive deadline must be whole seconds')
    if not isinstance(expected_ids, (list, tuple)) or len(expected_ids) != len(set(expected_ids)):
        raise ValueError('Expected job IDs must be a unique supplied list')
    ids = [job['id'] for job in jobs]
    if len(ids) != len(set(ids)) or set(ids) != set(expected_ids):
        raise ValueError('Observed and expected job identities differ')
    groups = {'on_time_completed': [], 'late_completed': [],
              'overdue_unfinished': [], 'not_due_unfinished': [],
              'not_yet_accepted': []}
    for job in jobs:
        accepted = job['accepted']
        completed = job[completion_field]
        if type(accepted) is not int or accepted < 0 or (
                completed is not None and (type(completed) is not int or completed < accepted)):
            raise ValueError('Acceptance and completion times must be coherent')
        if accepted > now:
            groups['not_yet_accepted'].append(job['id'])
        elif completed is not None and completed <= now:
            label = 'on_time_completed' if completed <= accepted + deadline else 'late_completed'
            groups[label].append(job['id'])
        elif accepted + deadline <= now:
            groups['overdue_unfinished'].append(job['id'])
        else:
            groups['not_due_unfinished'].append(job['id'])
    unfinished = groups['overdue_unfinished'] + groups['not_due_unfinished']
    missed_promise = groups['late_completed'] + groups['overdue_unfinished']
    mature = groups['on_time_completed'] + missed_promise
    return {
        'at_second': now,
        'groups': groups,
        'unfinished_ids': sorted(unfinished),
        'missed_promise_ids': sorted(missed_promise),
        'mature_ids': sorted(mature),
        'on_time_over_mature': [len(groups['on_time_completed']), len(mature)],
        'basis': 'supplied fictional IDs and retrospective completion times',
        'aws_called': False,
        'operator_action_taken': False,
    }


def run():
    fixture = json.loads(FIXTURE.read_text())
    jobs = fixture['jobs']
    expected = [job['id'] for job in jobs]
    kwargs = {'deadline': fixture['completion_deadline_seconds'],
              'completion_field': 'completed_at_followup', 'expected_ids': expected}
    at_120 = classify(jobs, now=120, **kwargs)
    changed = deepcopy(jobs)
    next(job for job in changed if job['id'] == 'r3')['completed_at_followup'] = 121
    at_125 = classify(changed, now=125, **kwargs)
    assert at_120['unfinished_ids'] == ['r3', 'r4', 'r6']
    assert at_120['missed_promise_ids'] == ['r3', 'r4', 'r5']
    assert at_125['unfinished_ids'] == ['r4', 'r6']
    assert at_125['missed_promise_ids'] == ['r3', 'r4', 'r5']
    print(json.dumps({'incident_snapshot': at_120,
                      'hypothetical_r3_completes_at_121': at_125}, indent=2))


if __name__ == '__main__':
    run()
