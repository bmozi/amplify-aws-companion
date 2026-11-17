import copy
import json
from pathlib import Path
import unittest

from cohort_lab import classify


FIXTURE = json.loads(Path(__file__).with_name('incident.json').read_text())
EXPECTED = [job['id'] for job in FIXTURE['jobs']]
BASE = {'deadline': 60, 'completion_field': 'completed_at_followup',
        'expected_ids': EXPECTED}


class CohortLabTest(unittest.TestCase):
    def test_equal_counts_do_not_mean_equal_people(self):
        result = classify(FIXTURE['jobs'], now=120, **BASE)
        self.assertEqual(result['unfinished_ids'], ['r3', 'r4', 'r6'])
        self.assertEqual(result['missed_promise_ids'], ['r3', 'r4', 'r5'])
        self.assertEqual(result['on_time_over_mature'], [2, 5])

    def test_late_completion_reduces_backlog_but_not_missed_promise(self):
        jobs = copy.deepcopy(FIXTURE['jobs'])
        next(job for job in jobs if job['id'] == 'r3')['completed_at_followup'] = 121
        result = classify(jobs, now=125, **BASE)
        self.assertEqual(result['unfinished_ids'], ['r4', 'r6'])
        self.assertEqual(result['missed_promise_ids'], ['r3', 'r4', 'r5'])

    def test_deadline_boundary_moves_unfinished_customer_to_overdue(self):
        before = classify(FIXTURE['jobs'], now=129, **BASE)
        at_deadline = classify(FIXTURE['jobs'], now=130, **BASE)
        self.assertIn('r6', before['groups']['not_due_unfinished'])
        self.assertIn('r6', at_deadline['groups']['overdue_unfinished'])
        self.assertEqual(at_deadline['on_time_over_mature'], [2, 6])

    def test_future_completion_does_not_leak_into_earlier_snapshot(self):
        result = classify(FIXTURE['jobs'], now=100, **BASE)
        self.assertIn('r5', result['groups']['overdue_unfinished'])
        self.assertIn('r6', result['groups']['not_due_unfinished'])
        self.assertEqual(result['on_time_over_mature'], [2, 5])

    def test_missing_or_duplicate_id_refused_before_rate(self):
        with self.assertRaises(ValueError):
            classify(FIXTURE['jobs'][:-1], now=120, **BASE)
        jobs = copy.deepcopy(FIXTURE['jobs'])
        jobs[-1]['id'] = 'r5'
        with self.assertRaises(ValueError):
            classify(jobs, now=120, **BASE)

    def test_invalid_clock_refused(self):
        with self.assertRaises(ValueError):
            classify(FIXTURE['jobs'], now=-1, **BASE)
        with self.assertRaises(ValueError):
            classify(FIXTURE['jobs'], now=120, **{**BASE, 'deadline': 0})


if __name__ == '__main__':
    unittest.main()
