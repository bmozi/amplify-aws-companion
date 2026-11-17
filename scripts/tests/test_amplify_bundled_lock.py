"""Regression controls for the selected Amplify bundled-lock check."""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import unittest


CHECK = Path(__file__).resolve().parents[1] / 'check-amplify-bundled-lock.py'
spec = importlib.util.spec_from_file_location('bundled_lock_check', CHECK)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class BundledLockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual = json.loads((CHECK.parents[1] / 'app/package-lock.json').read_text())

    def test_current_lock_has_all_four_required_nested_records(self):
        report = module.inspect_lock(self.actual)
        self.assertTrue(report['passed'], report['defects'])
        self.assertEqual(report['known_paths_checked'], 4)
        self.assertEqual(sum(item['nested_core_version'] == '2.0.0'
                             for item in report['observations']), 4)

    def test_pruned_nested_record_is_refused(self):
        changed = deepcopy(self.actual)
        key = ('node_modules/@aws-amplify/data-construct/node_modules/'
               '@opentelemetry/resources/node_modules/@opentelemetry/core')
        del changed['packages'][key]
        report = module.inspect_lock(changed)
        self.assertFalse(report['passed'])
        self.assertTrue(any('resources needs core 2.0.0' in item
                            for item in report['defects']))

    def test_changed_unknown_requirement_requires_review(self):
        changed = deepcopy(self.actual)
        key = ('node_modules/@aws-amplify/graphql-api-construct/node_modules/'
               '@opentelemetry/sdk-trace-base')
        changed['packages'][key]['dependencies']['@opentelemetry/core'] = '^2.0.0'
        report = module.inspect_lock(changed)
        self.assertFalse(report['passed'])
        self.assertTrue(any('not an exact known version' in item
                            for item in report['defects']))


if __name__ == '__main__':
    unittest.main()
