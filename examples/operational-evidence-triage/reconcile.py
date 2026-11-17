"""Reconcile fictional incident evidence without turning correlation into cause.

Standard-library only. This reads a local JSON fixture and never calls AWS.
"""

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path


DEFAULT = Path(__file__).with_name('mini-incident.json')


def utc(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None or result.utcoffset() != timedelta(0):
        raise ValueError(f'Expected an explicit UTC timestamp: {value}')
    return result.astimezone(timezone.utc)


def analyze(data):
    start = utc(data['incident_window']['start'])
    end = utc(data['incident_window']['end'])
    if end <= start:
        raise ValueError('Incident window must end after it begins')
    cohorts = {row['name']: row for row in data['cohorts']}
    rates = {}
    for name in ('prior_complete_hour', 'mature_incident_hour'):
        row = cohorts[name]
        total, on_time = row['eligible'], row['assigned_within_30_seconds']
        if not isinstance(total, int) or not isinstance(on_time, int) or total <= 0 or not 0 <= on_time <= total:
            raise ValueError(f'Invalid cohort counts: {name}')
        rates[name] = round(100 * on_time / total, 2)

    selected = {row['request_id'] for row in data['selected_jobs']}
    unresolved = sorted(row['job_id'] for row in data['selected_jobs'] if row['state'] == 'late_unresolved')
    errors = {row['request_id'] for row in data['alb_errors'] if 500 <= row['status'] < 600}
    timeouts = {row['request_id'] for row in data['application_events'] if row['event'] == 'assignment_timeout'}
    joined = sorted(selected & errors & timeouts)
    coverage = data['log_coverage']
    logs_complete = bool(coverage['complete']) and utc(coverage['start']) <= start and utc(coverage['end']) >= end

    target = data['app_target']
    audit = [row['event_id'] for row in data['cloudtrail_events']
             if row['region'] == target['region'] and row['resource_id'] == target['security_group_id']
             and start - timedelta(minutes=15) <= utc(row['time']) <= end]
    config = [row['compliance'] for row in data['config_evaluations']
              if row['region'] == target['region'] and row['resource_id'] == target['security_group_id']
              and start <= utc(row['time']) <= end]
    inspector = data['inspector']
    return {
        'cohort_on_time_percent': rates,
        'percentage_point_change': round(rates['mature_incident_hour'] - rates['prior_complete_hour'], 2),
        'selected_request_ids_in_all_three_sources': joined,
        'selected_job_records': len(data['selected_jobs']),
        'mature_cohort_eligible_jobs': cohorts['mature_incident_hour']['eligible'],
        'incident_logs_complete': logs_complete,
        'matching_cloudtrail_event_ids': sorted(audit),
        'same_target_config_results_in_window': config,
        'inspector_evidence': ('unknown: target not scanning' if inspector['coverage'] != 'Scanning'
                               else 'supplied scan has no findings; target safety is unproved'
                               if inspector['findings'] == [] else 'review the supplied findings and scan scope'),
        'analytics_consumer_lag_seconds': data['analytics_consumer_lag_seconds'],
        'selected_unresolved_jobs': unresolved,
        'release_caused_delay': 'unproven',
        'read_only_next_check': 'Join affected request paths to the exact target and configuration history; verify source coverage and customer outcomes before a change.'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture', type=Path, default=DEFAULT)
    args = parser.parse_args()
    print(json.dumps(analyze(json.loads(args.fixture.read_text())), indent=2))


if __name__ == '__main__':
    main()
