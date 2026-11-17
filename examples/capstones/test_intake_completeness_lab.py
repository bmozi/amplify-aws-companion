"""Negative controls for missing, conflicting, and reconciled source rows."""

import copy
import json
from pathlib import Path
import unittest

from intake_completeness_lab import compare


HERE = Path(__file__).resolve().parent
INTAKE = json.loads((HERE / 'intake-completeness.json').read_text())['accepted']
OPERATIONS = json.loads((HERE / 'incident.json').read_text())['jobs']


class IntakeCompletenessTests(unittest.TestCase):
    def evaluate(self, intake=INTAKE, operations=OPERATIONS):
        return compare(intake, operations, now=120, deadline=60)

    def test_missing_due_customer_blocks_rate_without_inventing_outcome(self):
        result = self.evaluate()
        self.assertEqual(result['decision'], 'hold_customer_rate')
        self.assertEqual(result['accepted_in_register'], 7)
        self.assertEqual(result['mature_in_register'], 6)
        self.assertEqual(result['known_on_time'], 2)
        self.assertEqual(result['known_missed_ids'], ['r3', 'r4', 'r5'])
        self.assertEqual(result['due_with_unknown_outcome'], ['r7'])
        self.assertIsNone(result['rate'])

    def test_independently_reconciled_outcome_changes_rate(self):
        operations = copy.deepcopy(OPERATIONS)
        operations.append({'id': 'r7', 'accepted': 50, 'completed_at_followup': 100})
        result = self.evaluate(operations=operations)
        self.assertEqual(result['decision'], 'rate_for_supplied_population')
        self.assertEqual(result['rate'], [3, 6])
        operations[-1]['completed_at_followup'] = 115
        late = self.evaluate(operations=operations)
        self.assertEqual(late['rate'], [2, 6])
        self.assertIn('r7', late['known_missed_ids'])

    def test_conflicting_identity_or_time_does_not_get_a_rate(self):
        operations = copy.deepcopy(OPERATIONS)
        operations[0]['accepted'] = 1
        self.assertEqual(self.evaluate(operations=operations)['decision'],
                         'hold_source_reconciliation')
        operations = copy.deepcopy(OPERATIONS)
        operations.append({'id': 'r8', 'accepted': 60, 'completed_at_followup': 100})
        result = self.evaluate(operations=operations)
        self.assertEqual(result['unexpected_in_operations'], ['r8'])
        self.assertIsNone(result['rate'])

    def test_duplicate_register_identity_and_future_time_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.evaluate(intake=INTAKE + [INTAKE[0]])
        future = copy.deepcopy(INTAKE)
        future[-1]['accepted'] = 121
        with self.assertRaisesRegex(ValueError, 'future acceptance'):
            self.evaluate(intake=future)

    def test_missing_outcome_field_and_empty_intake_hold(self):
        operations = copy.deepcopy(OPERATIONS)
        del operations[0]['completed_at_followup']
        self.assertEqual(self.evaluate(operations=operations)['missing_outcome_fields'], ['r1'])
        self.assertIsNone(self.evaluate(intake=[])['rate'])


if __name__ == '__main__':
    unittest.main()
