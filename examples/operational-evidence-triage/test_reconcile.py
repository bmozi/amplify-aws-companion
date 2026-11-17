import copy
import json
from pathlib import Path
import unittest

from reconcile import analyze


FIXTURE = Path(__file__).with_name('mini-incident.json')


class ReconcileTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(FIXTURE.read_text())

    def test_base_case_separates_join_from_cause(self):
        result = analyze(self.data)
        self.assertEqual(result['percentage_point_change'], -12.0)
        self.assertEqual(result['selected_request_ids_in_all_three_sources'], ['req-a'])
        self.assertEqual(result['matching_cloudtrail_event_ids'], ['event-1'])
        self.assertEqual(result['same_target_config_results_in_window'], ['NON_COMPLIANT'])
        self.assertFalse(result['incident_logs_complete'])
        self.assertEqual(result['inspector_evidence'], 'unknown: target not scanning')
        self.assertEqual(result['release_caused_delay'], 'unproven')

    def test_wrong_resource_breaks_only_audit_join(self):
        self.data['cloudtrail_events'][0]['resource_id'] = 'sg-other'
        result = analyze(self.data)
        self.assertEqual(result['matching_cloudtrail_event_ids'], [])
        self.assertEqual(result['selected_request_ids_in_all_three_sources'], ['req-a'])

    def test_stale_config_does_not_describe_incident_window(self):
        self.data['config_evaluations'][0]['time'] = '2026-10-05T10:01:00Z'
        self.assertEqual(analyze(self.data)['same_target_config_results_in_window'], [])

    def test_missing_log_join_does_not_erase_late_work(self):
        self.data['application_events'] = []
        result = analyze(self.data)
        self.assertEqual(result['selected_request_ids_in_all_three_sources'], [])
        self.assertEqual(result['selected_unresolved_jobs'], ['job-a', 'job-b'])

    def test_new_healthy_hour_does_not_close_old_jobs(self):
        self.data['cohorts'][1]['assigned_within_30_seconds'] = 100
        result = analyze(self.data)
        self.assertEqual(result['percentage_point_change'], 7.0)
        self.assertEqual(result['selected_unresolved_jobs'], ['job-a', 'job-b'])

    def test_complete_log_claim_needs_full_window(self):
        self.data['log_coverage']['complete'] = True
        self.assertTrue(analyze(self.data)['incident_logs_complete'])
        self.data['log_coverage']['end'] = '2026-10-08T10:05:00Z'
        self.assertFalse(analyze(self.data)['incident_logs_complete'])

    def test_empty_inspector_findings_with_scanning_still_do_not_clear_target(self):
        self.data['inspector']['coverage'] = 'Scanning'
        self.assertEqual(analyze(self.data)['inspector_evidence'],
                         'supplied scan has no findings; target safety is unproved')

    def test_invalid_counts_or_naive_time_are_rejected(self):
        bad = copy.deepcopy(self.data)
        bad['cohorts'][1]['assigned_within_30_seconds'] = 101
        with self.assertRaises(ValueError):
            analyze(bad)
        bad = copy.deepcopy(self.data)
        bad['cloudtrail_events'][0]['time'] = '2026-10-08T09:58:00'
        with self.assertRaises(ValueError):
            analyze(bad)


if __name__ == '__main__':
    unittest.main()
