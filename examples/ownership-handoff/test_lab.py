import unittest

from lab import assess, baseline


class HandoffGateTests(unittest.TestCase):
    def test_baseline_requires_observed_import_and_customer_result(self):
        result = assess(baseline())
        self.assertTrue(result['ready_to_import'])
        self.assertFalse(result['handoff_complete'])

    def test_import_does_not_excuse_old_owner(self):
        evidence = baseline()
        evidence['old_owner']['stack_membership'] = 'managed'
        evidence['import_observed'] = True
        evidence['customer_acceptance'] = 'passed'
        self.assertFalse(assess(evidence)['handoff_complete'])

    def test_same_name_in_another_region_is_rejected(self):
        evidence = baseline()
        evidence['terraform_target']['region'] = 'us-west-2'
        self.assertFalse(assess(evidence)['ready_to_import'])

    def test_replacement_is_not_import(self):
        evidence = baseline()
        evidence['terraform_target']['plan_action'] = 'replace'
        self.assertFalse(assess(evidence)['ready_to_import'])

    def test_matching_missing_ids_do_not_count_as_same_object(self):
        evidence = baseline()
        evidence['old_owner']['physical_id'] = ''
        evidence['terraform_target']['physical_id'] = ''
        result = assess(evidence)
        self.assertFalse(result['ready_to_import'])
        self.assertIn('physical_id evidence is missing', result['reasons'])

    def test_success_still_needs_customer_acceptance(self):
        evidence = baseline()
        evidence['import_observed'] = True
        evidence['customer_acceptance'] = 'passed'
        self.assertTrue(assess(evidence)['handoff_complete'])


if __name__ == '__main__':
    unittest.main()
