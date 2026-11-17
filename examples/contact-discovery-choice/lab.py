"""Fictional A02 scan/index discovery exercise; no AWS calls or credentials."""
import argparse
import json
import re
from pathlib import Path


def simulate(case, *, reconcile=False, contact_before_commit=None):
    """Model candidates, base rechecks and final conditions in a sequential fixture."""
    if set(case) != {'now', 'requests', 'index_visible', 'other_table_items'}:
        raise ValueError('Supply now, requests, index_visible and other_table_items')
    now, other = case['now'], case['other_table_items']
    if type(now) is not int or now < 0 or type(other) is not int or other < 0:
        raise ValueError('now and other_table_items must be nonnegative integers')
    requests = {}
    for item in case['requests']:
        if set(item) != {'id', 'accepted_at', 'contact_at'}:
            raise ValueError('Each request needs id, accepted_at and contact_at')
        key, accepted, contacted = item['id'], item['accepted_at'], item['contact_at']
        if not isinstance(key, str) or not re.fullmatch('[A-Za-z0-9_-]{1,64}', key) or key in requests:
            raise ValueError('Request IDs must be unique simple identifiers')
        if type(accepted) is not int or accepted < 0 or accepted > now:
            raise ValueError('accepted_at must be a valid past integer second')
        if contacted is not None and (type(contacted) is not int or not accepted <= contacted <= now):
            raise ValueError('contact_at must be null or a valid later integer second')
        requests[key] = item
    visible = case['index_visible']
    if not isinstance(visible, list) or len(visible) != len(set(visible)) or not set(visible) <= set(requests):
        raise ValueError('index_visible must list distinct known requests')
    race = contact_before_commit or {}
    if not isinstance(race, dict) or not set(race) <= set(requests):
        raise ValueError('contact_before_commit must name known requests')
    for key, time in race.items():
        if type(time) is not int or not requests[key]['accepted_at'] <= time <= now:
            raise ValueError('Race contact time must be a valid later integer second')
        if requests[key]['contact_at'] is not None:
            raise ValueError('Race contact must follow a previously uncontacted base read')

    candidates = set(visible) | (set(requests) if reconcile else set())
    due_breach = {key for key, item in requests.items()
                  if now > item['accepted_at'] + 3600 and
                  (item['contact_at'] is None or item['contact_at'] > item['accepted_at'] + 3600)}
    stale = {key for key in visible if requests[key]['contact_at'] is not None and
             requests[key]['contact_at'] <= requests[key]['accepted_at'] + 3600}
    attempted = candidates & due_breach
    late = {key for key in attempted if
            (requests[key]['contact_at'] is not None and
             requests[key]['contact_at'] > requests[key]['accepted_at'] + 3600) or
            (key in race and race[key] > requests[key]['accepted_at'] + 3600)}
    on_time = (attempted & set(race)) - late
    escalated = attempted - on_time
    open_work = {key for key in escalated
                 if requests[key]['contact_at'] is None and key not in race}
    scan_items = len(requests) + other if reconcile else 0
    return {
        'kind': 'sequential-design-fixture-not-dynamodb-evidence',
        'escalation_records': sorted(escalated),
        'open_work': sorted(open_work),
        'missed_due_without_reconciliation': sorted(due_breach - candidates),
        'stale_index_candidates_rejected_by_base_read': sorted(stale),
        'on_time_contacts_preventing_escalation': sorted(on_time),
        'late_contacts_with_historical_breach': sorted(late),
        'work_counts_not_request_units': {
            'index_candidates_returned': len(visible),
            'base_gets': len(visible),
            'final_condition_attempts': len(attempted),
            'scan_evaluated_items': scan_items,
            'scan_pages_at_limit_20': (scan_items + 19) // 20,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case', type=Path)
    args = parser.parse_args()
    case = json.loads(args.case.read_text())
    print(json.dumps({
        'index_only': simulate(case),
        'with_full_reconciliation': simulate(case, reconcile=True),
        'contact_race_with_reconciliation': simulate(
            case, reconcile=True, contact_before_commit={'R3': 3601}),
    }, indent=2))


if __name__ == '__main__':
    main()
