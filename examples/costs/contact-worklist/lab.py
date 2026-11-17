"""Count illustrative A02 contact-worklist capacity; never calls AWS."""
import argparse
import json
from pathlib import Path


FIELDS = (
    'contact_calls', 'contact_transaction_attempts',
    'due_scan_evaluated_items', 'due_scan_pages', 'overdue_requests_returned',
    'overdue_transaction_attempts', 'worklist_scan_evaluated_items',
    'worklist_scan_pages', 'worklist_escalations', 'worklist_open_escalations',
)


def count(scenario):
    if set(scenario) != set(FIELDS):
        raise ValueError('Supply exactly the ten named workload counts')
    for key, value in scenario.items():
        if type(value) is not int or value < 0:
            raise ValueError(f'{key} must be a nonnegative integer')
    if scenario['due_scan_evaluated_items'] > 20 * scenario['due_scan_pages']:
        raise ValueError('Due scans exceed 20 evaluated items per page')
    if scenario['worklist_scan_evaluated_items'] > 20 * scenario['worklist_scan_pages']:
        raise ValueError('Worklist scans exceed 20 evaluated items per page')
    if not scenario['contact_calls'] <= scenario['contact_transaction_attempts'] <= 5 * scenario['contact_calls']:
        raise ValueError('Contact attempts must be between one and five per call')
    if scenario['overdue_requests_returned'] > scenario['due_scan_evaluated_items']:
        raise ValueError('Overdue requests exceed evaluated due-scan items')
    if not scenario['overdue_requests_returned'] <= scenario['overdue_transaction_attempts'] <= 5 * scenario['overdue_requests_returned']:
        raise ValueError('Overdue attempts must be between one and five per request')
    if scenario['worklist_escalations'] > scenario['worklist_scan_evaluated_items']:
        raise ValueError('Returned escalations exceed evaluated worklist items')
    if scenario['worklist_open_escalations'] > scenario['worklist_escalations']:
        raise ValueError('Open escalations exceed returned escalations')

    # One unit per evaluated item is a deliberately simple scan allowance,
    # not DynamoDB's exact page-level bill. Empty pages get one unit. See README.
    local_contact_reads = 2 * scenario['contact_calls']
    local_contact_writes = 2 * scenario['contact_transaction_attempts']
    cloud_candidate_reads = (max(scenario['due_scan_evaluated_items'], scenario['due_scan_pages'])
             + max(scenario['worklist_scan_evaluated_items'], scenario['worklist_scan_pages'])
             + scenario['worklist_escalations']
             + scenario['worklist_open_escalations'])
    cloud_candidate_writes = 4 * scenario['overdue_transaction_attempts']
    reads = local_contact_reads + cloud_candidate_reads
    writes = local_contact_writes + cloud_candidate_writes
    return {
        'kind': 'illustrative-capacity-allowance-not-billing-cap',
        'modeled_table_read_request_units': reads,
        'modeled_table_write_request_units': writes,
        'boundaries': {
            'optional_cloud_handler_candidate': {
                'modeled_table_read_request_units': cloud_candidate_reads,
                'modeled_table_write_request_units': cloud_candidate_writes,
                'api_calls': {
                    'get_item': scenario['worklist_escalations'] + scenario['worklist_open_escalations'],
                    'scan': scenario['due_scan_pages'] + scenario['worklist_scan_pages'],
                    'transact_write_items': scenario['overdue_transaction_attempts'],
                },
            },
            'local_contact_record_fixture_only': {
                'modeled_table_read_request_units': local_contact_reads,
                'modeled_table_write_request_units': local_contact_writes,
                'api_calls': {
                    'get_item': 2 * scenario['contact_calls'],
                    'scan': 0,
                    'transact_write_items': scenario['contact_transaction_attempts'],
                },
            },
        },
        'api_calls': {
            'get_item': 2 * scenario['contact_calls'] + scenario['worklist_escalations']
                        + scenario['worklist_open_escalations'],
            'scan': scenario['due_scan_pages'] + scenario['worklist_scan_pages'],
            'transact_write_items': scenario['contact_transaction_attempts']
                                    + scenario['overdue_transaction_attempts'],
        },
        'assumptions': [
            'Strongly consistent GetItem and Scan; each item no more than 4 KiB.',
            'Each transaction item no more than 1 KiB; two write units per item.',
            'Scan allowance is one unit per evaluated item or empty page; actual page capacity can differ.',
            'Counts include repeat passes and failed/duplicate transaction attempts supplied by the learner.',
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scenario', type=Path)
    args = parser.parse_args()
    print(json.dumps(count(json.loads(args.scenario.read_text())), indent=2))


if __name__ == '__main__':
    main()
