"""Editorial controls for the fictional operations reader-pilot case."""

import json
import importlib.util
from pathlib import Path
import unittest


CASE = json.loads(Path(__file__).with_name('operations-case.json').read_text())


class ParticipantCaseTests(unittest.TestCase):
    def test_first_snapshot_omits_future_completion_facts(self):
        script = Path(__file__).resolve().parents[2] / 'scripts/package-learner-pilot.py'
        spec = importlib.util.spec_from_file_location('pilot_packager', script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        participant = json.loads(module.operations_first_snapshot(json.dumps(CASE).encode()))
        self.assertNotIn('changed_fact', participant)
        self.assertNotIn('followup_snapshot_at', participant)
        for source, projected in zip(CASE['jobs'], participant['jobs']):
            self.assertEqual(projected['completed_at_first_snapshot'], source['completed_at_first_snapshot'])
            self.assertNotIn('completed_at_followup', projected)

    def test_followup_is_separate_from_first_attempt(self):
        script = Path(__file__).resolve().parents[2] / 'scripts/package-learner-pilot.py'
        spec = importlib.util.spec_from_file_location('pilot_packager', script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        text = Path(__file__).with_name('README.md').read_text()
        operations = module.between(text, '## Operations task: which customer is still waiting?\n',
                                    '## Certification-to-application task: recover a real booking\n')
        first, followup = module.separate_operations_followup(operations)
        self.assertNotIn('p3 completes at second 103', first)
        self.assertIn('[FOLLOWUP.md](FOLLOWUP.md)', first)
        self.assertIn('p3 completes at second 103', followup)


def classify(jobs, now, deadline, field):
    groups = {'unfinished': set(), 'missed': set(), 'mature': set(), 'on_time': set()}
    for job in jobs:
        accepted = job['accepted']
        completed = job[field]
        if accepted > now:
            continue
        finished = completed is not None and completed <= now
        due = accepted + deadline <= now
        if not finished:
            groups['unfinished'].add(job['id'])
        if due:
            groups['mature'].add(job['id'])
            if finished and completed <= accepted + deadline:
                groups['on_time'].add(job['id'])
            else:
                groups['missed'].add(job['id'])
    return groups


class OperationsPilotCaseTest(unittest.TestCase):
    def test_case_has_six_unique_coherent_jobs_and_separate_first_snapshot(self):
        jobs = CASE['jobs']
        self.assertEqual(len(jobs), 6)
        self.assertEqual(len({job['id'] for job in jobs}), 6)
        for job in jobs:
            first = job['completed_at_first_snapshot']
            later = job['completed_at_followup']
            self.assertLessEqual(job['accepted'], CASE['first_snapshot_at'])
            if first is not None:
                self.assertLessEqual(job['accepted'], first)
                self.assertLessEqual(first, CASE['first_snapshot_at'])
                self.assertEqual(first, later)
            if later is not None:
                self.assertLessEqual(job['accepted'], later)
                self.assertLessEqual(later, CASE['followup_snapshot_at'])

    def test_equal_counts_hide_different_people_at_first_snapshot(self):
        g = classify(CASE['jobs'], CASE['first_snapshot_at'],
                     CASE['assignment_promise_seconds'], 'completed_at_first_snapshot')
        self.assertEqual(g['unfinished'], {'p3', 'p4', 'p5'})
        self.assertEqual(g['missed'], {'p2', 'p3', 'p4'})
        self.assertEqual(g['mature'], {'p1', 'p2', 'p3', 'p4'})
        self.assertEqual(g['on_time'], {'p1'})

    def test_late_completion_and_exact_deadline_change_membership(self):
        self.assertIn('after processing all completions stamped t or earlier', CASE['snapshot_rule'])
        first = classify(CASE['jobs'], CASE['changed_snapshot_at'],
                         CASE['assignment_promise_seconds'], 'completed_at_followup')
        boundary = classify(CASE['jobs'], CASE['boundary_snapshot_at'],
                            CASE['assignment_promise_seconds'], 'completed_at_followup')
        self.assertEqual(first['unfinished'], {'p4', 'p5'})
        self.assertEqual(first['missed'], {'p2', 'p3', 'p4'})
        self.assertEqual(boundary['missed'], {'p2', 'p3', 'p4', 'p5'})

    def test_first_snapshot_observations_do_not_include_future_events(self):
        self.assertTrue(all(item['at'] <= CASE['first_snapshot_at']
                            for item in CASE['observations_available_at_first_snapshot']))
        self.assertEqual(CASE['proposed_action_not_taken'], 'increase worker concurrency tenfold')


if __name__ == '__main__':
    unittest.main()
